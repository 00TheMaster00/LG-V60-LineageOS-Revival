#!/usr/bin/env python3
"""Clone one complete Qualcomm GPU speed-bin block into another.

Default operation used by this project:
- source speed bin: 1 (vendor 670 MHz ladder)
- destination speed bin: 0 (documented device)
- retain destination speed-bin identifier 0

The parser balances braces rather than relying on fixed line numbers.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def find_block(text: str, speed_bin: int) -> tuple[int, int, str]:
    pattern = re.compile(
        r"(?P<indent>^[ \t]*)qcom,gpu-pwrlevels-(?P<node>\d+)\s*\{"
        r"(?P<body>.*?)^[ \t]*\};",
        re.MULTILINE | re.DOTALL,
    )
    # Regex alone cannot safely balance nested braces, so identify candidate
    # starts then scan character-by-character.
    start_re = re.compile(r"^[ \t]*qcom,gpu-pwrlevels-\d+\s*\{", re.MULTILINE)
    for match in start_re.finditer(text):
        start = match.start()
        brace = text.find("{", match.start(), match.end())
        depth = 0
        end = None
        for i in range(brace, len(text)):
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    semi = text.find(";", i)
                    if semi < 0:
                        raise ValueError("Block closes without semicolon")
                    end = semi + 1
                    break
        if end is None:
            raise ValueError("Unbalanced GPU power-level block")
        block = text[start:end]
        if re.search(rf"qcom,speed-bin\s*=\s*<{speed_bin}>\s*;", block):
            return start, end, block
    raise ValueError(f"Speed-bin block {speed_bin} not found")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=Path)
    ap.add_argument("--source-bin", type=int, default=1)
    ap.add_argument("--dest-bin", type=int, default=0)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    if args.in_place and args.output:
        ap.error("Choose --in-place or --output, not both")

    text = args.file.read_text(encoding="utf-8")
    dst_start, dst_end, dst = find_block(text, args.dest_bin)
    _, _, src = find_block(text, args.source_bin)

    dst_node = re.search(r"qcom,gpu-pwrlevels-(\d+)", dst)
    src_node = re.search(r"qcom,gpu-pwrlevels-(\d+)", src)
    if not dst_node or not src_node:
        raise ValueError("Could not identify node labels")

    replacement = src
    replacement = replacement.replace(
        f"qcom,gpu-pwrlevels-{src_node.group(1)}",
        f"qcom,gpu-pwrlevels-{dst_node.group(1)}",
        1,
    )
    replacement, count = re.subn(
        rf"qcom,speed-bin\s*=\s*<{args.source_bin}>\s*;",
        f"qcom,speed-bin = <{args.dest_bin}>;",
        replacement,
        count=1,
    )
    if count != 1:
        raise ValueError("Could not rewrite speed-bin identifier")

    patched = text[:dst_start] + replacement + text[dst_end:]

    # Safety assertions specific to the intended result.
    _, _, new_dst = find_block(patched, args.dest_bin)
    freqs = [int(x) for x in re.findall(r"qcom,gpu-freq\s*=\s*<(\d+)>;", new_dst)]
    expected = [670000000, 587000000, 525000000, 490000000, 441600000, 400000000, 305000000, 0]
    if args.source_bin == 1 and args.dest_bin == 0 and freqs != expected:
        raise ValueError(f"Unexpected destination ladder: {freqs}")
    if "qcom,initial-pwrlevel = <6>;" not in new_dst:
        raise ValueError("Expected initial-pwrlevel 6 is missing")
    if "qcom,throttle-pwrlevel = <1>;" not in new_dst:
        raise ValueError("Expected throttle-pwrlevel 1 is missing")

    out = args.file if args.in_place else (args.output or args.file.with_suffix(args.file.suffix + ".patched"))
    out.write_text(patched, encoding="utf-8")
    print(f"Patched: {out}")
    print("Destination frequencies:", " ".join(map(str, freqs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
