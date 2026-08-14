#!/usr/bin/env python3
"""Generate or verify the deterministic public SHA256SUMS.txt."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SHA256SUMS.txt"
SKIP_PARTS = {".git", ".venv", "__pycache__", "input", "output", "private", "logs"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest().upper()


def render() -> str:
    paths = sorted(
        path for path in ROOT.rglob("*")
        if path.is_file()
        and path != MANIFEST
        and not (set(path.relative_to(ROOT).parts) & SKIP_PARTS)
    )
    return "".join(
        f"{sha256_file(path)}  {path.relative_to(ROOT).as_posix()}\n" for path in paths
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        actual = MANIFEST.read_text(encoding="utf-8") if MANIFEST.is_file() else ""
        if actual != expected:
            print("SHA256SUMS.txt is missing or stale")
            return 1
        print("SHA256SUMS.txt: PASS")
        return 0
    MANIFEST.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Wrote {len(expected.splitlines())} entries to {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

