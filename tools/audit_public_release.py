#!/usr/bin/env python3
"""Fail when the public tree contains private/proprietary release hazards."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_BINARY = Path("DIY/06-LG-Camera/patches/EA40g-to-Candidate24.bsdiff")
ALLOWED_BINARY_SIZE = 13_676_109
ALLOWED_BINARY_HASH = "4FB8A5D55E8E048AF737851D19CF98ABF1E2FC55F5AC119415E24746B3DCF485"
FALLBACK_SKIP_PARTS = {".git", ".venv", "__pycache__"}
BLOCKED_SUFFIXES = {
    ".apk", ".apks", ".idsig", ".kdz", ".dz", ".tot", ".qcn", ".xqcn",
    ".img", ".bin", ".elf", ".mbn", ".key", ".jks", ".keystore",
}
TEXT_PATTERNS = {
    "Windows user profile": re.compile(r"[A-Za-z]:\\Users\\(?!USERNAME\\|REPLACE)", re.I),
    "private project drive path": re.compile(r"[A-Za-z]:\\LG-V60-Project", re.I),
    "Linux home username": re.compile(r"/home/(?!user/|USERNAME/|REPLACE)[A-Za-z0-9._-]+/"),
    "probable raw LG ADB serial": re.compile(r"\bLMV[0-9A-Fa-f]{8,}\b"),
    "probable IMEI": re.compile(r"(?<![0-9A-Fa-f])[0-9]{15}(?![0-9A-Fa-f])"),
}
# Both are the project owner's GitHub noreply identities. The former account
# remains only in historical patch headers; new public work uses 00TheMaster00.
ALLOWED_EMAILS = {
    "315181980+The1-Master@users.noreply.github.com",
    "153080814+00TheMaster00@users.noreply.github.com",
}
EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest().upper()


def files(root: Path = ROOT) -> list[Path]:
    """Return everything that Git would publish, including force-added files."""
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        relative_names = [name for name in result.stdout.split(b"\0") if name]
        return sorted(
            (root / name.decode("utf-8", errors="surrogateescape"))
            for name in relative_names
            if (root / name.decode("utf-8", errors="surrogateescape")).is_file()
        )

    # Source archives have no Git index. Scan all content there; do not exempt
    # directories merely because they are commonly named private/input/logs.
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and not (set(path.relative_to(root).parts) & FALLBACK_SKIP_PARTS)
    )


def main() -> int:
    failures: list[str] = []
    scanned = files()
    for path in scanned:
        relative = path.relative_to(ROOT)
        if path.is_symlink():
            failures.append(f"symlink not allowed in public release: {relative}")
            continue
        if path.stat().st_size > 50 * 1024 * 1024:
            failures.append(f"file over 50 MiB: {relative}")

        if relative == ALLOWED_BINARY:
            if path.stat().st_size != ALLOWED_BINARY_SIZE:
                failures.append(f"camera delta size mismatch: {relative}")
            elif sha256_file(path) != ALLOWED_BINARY_HASH:
                failures.append(f"camera delta hash mismatch: {relative}")
            continue

        if path.suffix.lower() in BLOCKED_SUFFIXES:
            failures.append(f"blocked artifact type: {relative}")
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"unexpected binary file: {relative}")
            continue

        for label, pattern in TEXT_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{label}: {relative}")
        for email in EMAIL_PATTERN.findall(text):
            if email not in ALLOWED_EMAILS:
                failures.append(f"unexpected email {email}: {relative}")

    if failures:
        print("PUBLIC RELEASE AUDIT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"PUBLIC RELEASE AUDIT: PASS ({len(scanned)} files scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
