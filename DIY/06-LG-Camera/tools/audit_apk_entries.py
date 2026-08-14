#!/usr/bin/env python3
"""Verify exact stock/Candidate24 ZIP-entry differences without exposing entry data."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import re
import zipfile

from build_candidate24 import CANDIDATE24_SPEC, verify_file


SHA256_RE = re.compile(r"^[0-9A-F]{64}$")
MANIFEST_COLUMNS = (
    "status",
    "path",
    "stock_size",
    "stock_sha256",
    "candidate_size",
    "candidate_sha256",
)


def entries(path: Path) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            if info.filename in result:
                raise ValueError(f"duplicate ZIP entry: {info.filename}")
            digest = hashlib.sha256()
            with archive.open(info) as handle:
                while chunk := handle.read(8 * 1024 * 1024):
                    digest.update(chunk)
            result[info.filename] = (info.file_size, digest.hexdigest().upper())
    return result


def compare(
    stock: dict[str, tuple[int, str]], candidate: dict[str, tuple[int, str]]
) -> list[tuple[str, str, str, str, str, str]]:
    changes: list[tuple[str, str, str, str, str, str]] = []
    for name in sorted(set(stock) | set(candidate)):
        old = stock.get(name)
        new = candidate.get(name)
        if old is None:
            changes.append(("added", name, "", "", str(new[0]), new[1]))
        elif new is None:
            changes.append(("deleted", name, str(old[0]), old[1], "", ""))
        elif old != new:
            changes.append(("changed", name, str(old[0]), old[1], str(new[0]), new[1]))
    return changes


def read_manifest(path: Path) -> list[tuple[str, str, str, str, str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != MANIFEST_COLUMNS:
            raise ValueError(f"manifest columns must be exactly {MANIFEST_COLUMNS}")
        rows = [tuple(row[column] for column in MANIFEST_COLUMNS) for row in reader]
    for status, name, old_size, old_hash, new_size, new_hash in rows:
        if status not in {"added", "changed", "deleted"} or not name:
            raise ValueError(f"invalid manifest row: {status} {name}")
        for value in (old_size, new_size):
            if value and (not value.isdigit() or int(value) < 0):
                raise ValueError(f"invalid size for {name}: {value}")
        for value in (old_hash, new_hash):
            if value and not SHA256_RE.fullmatch(value.upper()):
                raise ValueError(f"invalid hash for {name}")
    if len(rows) != len(set(rows)):
        raise ValueError("duplicate manifest row")
    return sorted(rows, key=lambda row: row[1])


def write_manifest(path: Path, rows: list[tuple[str, str, str, str, str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(MANIFEST_COLUMNS)
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    default_manifest = Path(__file__).resolve().parents[1] / "audit" / "expected-apk-entry-changes.csv"
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=default_manifest)
    parser.add_argument("--write-manifest", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stock_path = args.stock.resolve()
    candidate_path = args.candidate.resolve()
    try:
        verify_file(
            stock_path,
            CANDIDATE24_SPEC.input_size,
            CANDIDATE24_SPEC.input_sha256,
            "EA40g stock APK",
        )
        verify_file(
            candidate_path,
            CANDIDATE24_SPEC.output_size,
            CANDIDATE24_SPEC.output_sha256,
            "Candidate 24 APK",
        )
        changes = compare(entries(stock_path), entries(candidate_path))
        if args.write_manifest:
            write_manifest(args.manifest.resolve(), changes)
            print(f"Wrote {len(changes)} APK-entry changes to {args.manifest.resolve()}")
            return 0
        expected = read_manifest(args.manifest.resolve())
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        return 2

    if changes != expected:
        print("APK ENTRY AUDIT: FAIL")
        return 1
    counts = {status: sum(row[0] == status for row in changes) for status in ("added", "changed", "deleted")}
    print(
        "APK ENTRY AUDIT: PASS "
        f"({len(changes)} entries: {counts['added']} added, "
        f"{counts['changed']} changed, {counts['deleted']} deleted)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
