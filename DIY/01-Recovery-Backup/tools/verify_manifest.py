#!/usr/bin/env python3
"""Verify every size/hash in a manifest created by hash_directory.py."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from hash_directory import sha256_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()

    manifest = args.manifest.resolve()
    root = manifest.parent
    failures: list[str] = []
    checked = 0

    with manifest.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"relative_path", "size_bytes", "sha256"}
        if set(reader.fieldnames or ()) != required:
            parser.error(f"manifest columns must be exactly {sorted(required)}")
        for row in reader:
            checked += 1
            candidate = (root / row["relative_path"]).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                failures.append(f"unsafe path: {row['relative_path']}")
                continue
            if not candidate.is_file():
                failures.append(f"missing: {row['relative_path']}")
                continue
            expected_size = int(row["size_bytes"])
            if candidate.stat().st_size != expected_size:
                failures.append(f"size mismatch: {row['relative_path']}")
                continue
            actual_hash = sha256_file(candidate)
            if actual_hash.upper() != row["sha256"].upper():
                failures.append(f"hash mismatch: {row['relative_path']}")

    if failures:
        print("FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"PASS: verified {checked} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

