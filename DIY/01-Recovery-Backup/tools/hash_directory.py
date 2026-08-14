#!/usr/bin/env python3
"""Create a deterministic SHA-256 CSV for a private partition-backup folder."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


CHUNK_SIZE = 8 * 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    directory = args.directory.resolve()
    output = args.output.resolve()
    if not directory.is_dir():
        parser.error(f"not a directory: {directory}")
    if output.parent != directory:
        parser.error("write the manifest inside the directory being hashed")

    files = sorted(
        path for path in directory.rglob("*")
        if path.is_file() and path.resolve() != output
    )
    if not files:
        parser.error("the directory contains no files")

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("relative_path", "size_bytes", "sha256"))
        for path in files:
            relative = path.relative_to(directory).as_posix()
            writer.writerow((relative, path.stat().st_size, sha256_file(path)))

    print(f"Wrote {len(files)} entries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

