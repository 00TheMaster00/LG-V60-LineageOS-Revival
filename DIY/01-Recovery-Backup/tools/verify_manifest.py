#!/usr/bin/env python3
"""Verify every size/hash in a manifest created by hash_directory.py."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re

from hash_directory import sha256_file


SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()

    manifest = args.manifest.resolve()
    root = manifest.parent
    failures: list[str] = []
    expected_paths: set[str] = set()
    checked = 0

    with manifest.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"relative_path", "size_bytes", "sha256"}
        if set(reader.fieldnames or ()) != required:
            parser.error(f"manifest columns must be exactly {sorted(required)}")
        for row in reader:
            checked += 1
            relative_text = row["relative_path"]
            if relative_text in expected_paths:
                failures.append(f"duplicate manifest entry: {relative_text}")
                continue
            expected_paths.add(relative_text)

            candidate = (root / relative_text).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                failures.append(f"unsafe path: {relative_text}")
                continue
            if not candidate.is_file():
                failures.append(f"missing: {relative_text}")
                continue
            try:
                expected_size = int(row["size_bytes"])
            except ValueError:
                failures.append(f"invalid size: {relative_text}")
                continue
            if expected_size < 0:
                failures.append(f"invalid size: {relative_text}")
                continue
            if candidate.stat().st_size != expected_size:
                failures.append(f"size mismatch: {relative_text}")
                continue
            if not SHA256_RE.fullmatch(row["sha256"]):
                failures.append(f"invalid SHA-256: {relative_text}")
                continue
            actual_hash = sha256_file(candidate)
            if actual_hash.upper() != row["sha256"].upper():
                failures.append(f"hash mismatch: {relative_text}")

    actual_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.resolve() != manifest
    }
    for relative_text in sorted(actual_paths - expected_paths):
        failures.append(f"extra: {relative_text}")

    if failures:
        print("FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"PASS: verified {checked} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
