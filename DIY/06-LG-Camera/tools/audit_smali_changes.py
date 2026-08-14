#!/usr/bin/env python3
"""Verify a local stock-to-Candidate24 Smali change inventory without publishing code."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import re


DEBUG_DIRECTIVE = re.compile(
    r"^\s*(?:\.line\b|\.local\b|\.end local\b|\.restart local\b|"
    r"\.prologue\b|\.source\b|#|$)"
)
SHA256_RE = re.compile(r"^[0-9A-F]{64}$")
MANIFEST_COLUMNS = ("status", "path", "stock_sha256", "candidate_sha256")


def normalized_bytes(path: Path) -> bytes:
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [line.rstrip() for line in lines if not DEBUG_DIRECTIVE.match(line)]
    return ("\n".join(kept) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def collect(root: Path) -> dict[str, bytes]:
    if not root.is_dir():
        raise ValueError(f"Smali root is not a directory: {root}")
    return {
        path.relative_to(root).as_posix(): normalized_bytes(path)
        for path in sorted(root.rglob("*.smali"))
        if path.is_file()
    }


def compare(
    stock: dict[str, bytes], candidate: dict[str, bytes]
) -> list[tuple[str, str, str, str]]:
    changes: list[tuple[str, str, str, str]] = []
    for relative in sorted(set(stock) | set(candidate)):
        old = stock.get(relative)
        new = candidate.get(relative)
        if old is None:
            changes.append(("added", relative, "", sha256(new or b"")))
        elif new is None:
            changes.append(("deleted", relative, sha256(old), ""))
        elif old != new:
            changes.append(("changed", relative, sha256(old), sha256(new)))
    return changes


def read_manifest(path: Path) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != MANIFEST_COLUMNS:
            raise ValueError(f"manifest columns must be exactly {MANIFEST_COLUMNS}")
        for row in reader:
            status = row["status"]
            relative = row["path"]
            stock_hash = row["stock_sha256"].upper()
            candidate_hash = row["candidate_sha256"].upper()
            if status not in {"added", "changed", "deleted"}:
                raise ValueError(f"invalid status for {relative}: {status}")
            if not relative or relative.startswith("/") or ".." in Path(relative).parts:
                raise ValueError(f"unsafe manifest path: {relative}")
            if stock_hash and not SHA256_RE.fullmatch(stock_hash):
                raise ValueError(f"invalid stock hash: {relative}")
            if candidate_hash and not SHA256_RE.fullmatch(candidate_hash):
                raise ValueError(f"invalid candidate hash: {relative}")
            rows.append((status, relative, stock_hash, candidate_hash))
    if len(rows) != len(set(rows)):
        raise ValueError("duplicate manifest row")
    return sorted(rows, key=lambda row: row[1])


def write_manifest(path: Path, changes: list[tuple[str, str, str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(MANIFEST_COLUMNS)
        writer.writerows(changes)


def method_blocks(data: bytes) -> dict[str, bytes]:
    lines = data.decode("utf-8").splitlines()
    methods: dict[str, bytes] = {}
    current: list[str] | None = None
    signature = ""
    for line in lines:
        if line.startswith(".method "):
            current = [line]
            signature = line[len(".method ") :]
        elif current is not None:
            current.append(line)
            if line == ".end method":
                methods[signature] = ("\n".join(current) + "\n").encode("utf-8")
                current = None
    return methods


def changed_methods(old: bytes | None, new: bytes | None) -> list[str]:
    old_methods = method_blocks(old or b"")
    new_methods = method_blocks(new or b"")
    return [
        signature
        for signature in sorted(set(old_methods) | set(new_methods))
        if old_methods.get(signature) != new_methods.get(signature)
    ]


def parse_args() -> argparse.Namespace:
    default_manifest = Path(__file__).resolve().parents[1] / "audit" / "expected-smali-changes.csv"
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=default_manifest)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--show-methods", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        stock = collect(args.stock.resolve())
        candidate = collect(args.candidate.resolve())
        changes = compare(stock, candidate)
        if args.write_manifest:
            write_manifest(args.manifest.resolve(), changes)
            print(f"Wrote {len(changes)} semantic changes to {args.manifest.resolve()}")
            return 0
        expected = read_manifest(args.manifest.resolve())
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2

    if changes != expected:
        print("SMALI SOURCE AUDIT: FAIL")
        actual_set = set(changes)
        expected_set = set(expected)
        for row in sorted(expected_set - actual_set):
            print(f"- missing expected row: {row[0]} {row[1]}")
        for row in sorted(actual_set - expected_set):
            print(f"- unexpected row/hash: {row[0]} {row[1]}")
        return 1

    counts = {status: sum(row[0] == status for row in changes) for status in ("added", "changed", "deleted")}
    print(
        "SMALI SOURCE AUDIT: PASS "
        f"({len(changes)} semantic files: {counts['added']} added, "
        f"{counts['changed']} changed, {counts['deleted']} deleted)"
    )
    if args.show_methods:
        for status, relative, _old_hash, _new_hash in changes:
            methods = changed_methods(stock.get(relative), candidate.get(relative))
            if methods:
                for method in methods:
                    print(f"{status}\t{relative}\t{method}")
            else:
                print(f"{status}\t{relative}\t<class-level change>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
