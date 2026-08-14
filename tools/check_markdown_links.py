#!/usr/bin/env python3
"""Check local Markdown links without fetching the network."""

from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
SKIP_PARTS = {".git", ".venv", "__pycache__"}


def main() -> int:
    failures: list[str] = []
    checked = 0
    for markdown in sorted(ROOT.rglob("*.md")):
        if set(markdown.relative_to(ROOT).parts) & SKIP_PARTS:
            continue
        text = markdown.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            target = match.group(1).strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = unquote(target.split("#", 1)[0])
            resolved = (markdown.parent / target).resolve()
            checked += 1
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"link escapes repository: {markdown.relative_to(ROOT)} -> {target}")
                continue
            if not resolved.exists():
                failures.append(f"missing link: {markdown.relative_to(ROOT)} -> {target}")
    if failures:
        print("MARKDOWN LINKS: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"MARKDOWN LINKS: PASS ({checked} local links checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

