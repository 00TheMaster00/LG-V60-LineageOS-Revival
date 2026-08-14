#!/usr/bin/env python3
"""Generate or verify the deterministic public SHA256SUMS.txt."""

from __future__ import annotations

import argparse
import difflib
import hashlib
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SHA256SUMS.txt"
FALLBACK_SKIP_PARTS = {".git", ".venv", "__pycache__"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    data = path.read_bytes()
    # .gitattributes fixes repository text at LF. Normalize the Windows
    # working tree to those canonical committed bytes so the manifest is
    # identical on Windows and Linux. The bsdiff artifact stays byte-exact.
    if path.suffix.lower() != ".bsdiff":
        data = data.replace(b"\r\n", b"\n")
    digest.update(data)
    return digest.hexdigest().upper()


def public_files(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        relative_names = [name for name in result.stdout.split(b"\0") if name]
        return [
            root / name.decode("utf-8", errors="surrogateescape")
            for name in relative_names
            if (root / name.decode("utf-8", errors="surrogateescape")).is_file()
        ]
    return [
        path for path in root.rglob("*")
        if path.is_file()
        and not (set(path.relative_to(root).parts) & FALLBACK_SKIP_PARTS)
    ]


def render() -> str:
    paths = sorted(
        (path for path in public_files() if path != MANIFEST),
        key=lambda path: path.relative_to(ROOT).as_posix().casefold(),
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
            print("".join(difflib.unified_diff(
                actual.splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile="committed/SHA256SUMS.txt",
                tofile="current-tree/SHA256SUMS.txt",
                n=1,
            )))
            return 1
        print("SHA256SUMS.txt: PASS")
        return 0
    MANIFEST.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Wrote {len(expected.splitlines())} entries to {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
