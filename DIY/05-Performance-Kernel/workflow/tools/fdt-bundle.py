#!/usr/bin/env python3
"""Split, inspect, replace, and concatenate raw concatenated FDT/DTB bundles.

A DTB begins with big-endian magic 0xd00dfeed and stores its total size in
bytes 4..7. The LG V60 boot image used in this project contained three DTBs
concatenated directly without extra alignment between entries.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

MAGIC = 0xD00DFEED


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_bundle(data: bytes) -> list[bytes]:
    entries: list[bytes] = []
    offset = 0
    while offset < len(data):
        if len(data) - offset < 8:
            raise ValueError(f"Trailing {len(data)-offset} bytes at offset {offset}")
        magic, total = struct.unpack_from(">II", data, offset)
        if magic != MAGIC:
            raise ValueError(f"Bad FDT magic 0x{magic:08x} at offset {offset}")
        if total < 40 or offset + total > len(data):
            raise ValueError(f"Invalid FDT size {total} at offset {offset}")
        entries.append(data[offset : offset + total])
        offset += total
    return entries


def cmd_list(path: Path) -> int:
    data = path.read_bytes()
    entries = split_bundle(data)
    print(f"bundle={path}")
    print(f"bytes={len(data)}")
    print(f"sha256={sha(data)}")
    print(f"entries={len(entries)}")
    offset = 0
    for i, entry in enumerate(entries, 1):
        print(f"entry={i} offset={offset} bytes={len(entry)} sha256={sha(entry)}")
        offset += len(entry)
    return 0


def cmd_split(path: Path, out: Path) -> int:
    entries = split_bundle(path.read_bytes())
    out.mkdir(parents=True, exist_ok=True)
    for i, entry in enumerate(entries, 1):
        p = out / f"entry-{i:02d}.dtb"
        p.write_bytes(entry)
        print(f"{p} bytes={len(entry)} sha256={sha(entry)}")
    return 0


def cmd_replace(path: Path, index: int, replacement: Path, out: Path) -> int:
    entries = split_bundle(path.read_bytes())
    if not 1 <= index <= len(entries):
        raise ValueError(f"Index {index} outside 1..{len(entries)}")
    new_entry = replacement.read_bytes()
    parsed = split_bundle(new_entry)
    if len(parsed) != 1:
        raise ValueError("Replacement must contain exactly one DTB")
    old = entries[index - 1]
    entries[index - 1] = new_entry
    combined = b"".join(entries)
    out.write_bytes(combined)
    print(f"replaced_index={index}")
    print(f"old_bytes={len(old)} old_sha256={sha(old)}")
    print(f"new_bytes={len(new_entry)} new_sha256={sha(new_entry)}")
    print(f"bundle_bytes={len(combined)} bundle_sha256={sha(combined)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("bundle", type=Path)
    p = sub.add_parser("split")
    p.add_argument("bundle", type=Path)
    p.add_argument("out_dir", type=Path)
    p = sub.add_parser("replace")
    p.add_argument("bundle", type=Path)
    p.add_argument("index", type=int)
    p.add_argument("replacement", type=Path)
    p.add_argument("output", type=Path)
    args = ap.parse_args()
    if args.cmd == "list":
        return cmd_list(args.bundle)
    if args.cmd == "split":
        return cmd_split(args.bundle, args.out_dir)
    return cmd_replace(args.bundle, args.index, args.replacement, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
