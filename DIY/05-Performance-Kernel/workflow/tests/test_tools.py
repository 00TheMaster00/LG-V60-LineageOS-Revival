#!/usr/bin/env python3
"""Functional tests for the repository's host-side transformation tools."""
from __future__ import annotations

import hashlib
import importlib.util
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FDT_TOOL = ROOT / "tools" / "fdt-bundle.py"
CLONE_TOOL = ROOT / "tools" / "clone-vendor-gpu-bin.py"
BEFORE = ROOT / "patches" / "speed-bin0-before.dtsi.fragment"
AFTER = ROOT / "patches" / "speed-bin0-after.dtsi.fragment"
PROFILE = ROOT / "profiles" / "profile.sh"
WRAPPER = ROOT / "profiles" / "wrapper.sh"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_dtb(tag: int, size: int = 64) -> bytes:
    assert size >= 40
    payload = bytearray(size)
    struct.pack_into(">II", payload, 0, 0xD00DFEED, size)
    payload[8:12] = tag.to_bytes(4, "big")
    for i in range(12, size):
        payload[i] = (tag + i) & 0xFF
    return bytes(payload)


def test_fdt_bundle() -> None:
    fdt = load_module(FDT_TOOL, "fdt_bundle")
    entries = [fake_dtb(1, 64), fake_dtb(2, 72), fake_dtb(3, 80)]
    bundle = b"".join(entries)
    assert fdt.split_bundle(bundle) == entries

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        bundle_path = td / "bundle.dtb"
        replacement = td / "replacement.dtb"
        output = td / "output.dtb"
        bundle_path.write_bytes(bundle)
        replacement_bytes = fake_dtb(9, 88)
        replacement.write_bytes(replacement_bytes)
        fdt.cmd_replace(bundle_path, 2, replacement, output)
        result = fdt.split_bundle(output.read_bytes())
        assert result == [entries[0], replacement_bytes, entries[2]]
        assert hashlib.sha256(result[0]).digest() == hashlib.sha256(entries[0]).digest()
        assert hashlib.sha256(result[2]).digest() == hashlib.sha256(entries[2]).digest()


def test_clone_vendor_bin() -> None:
    before = BEFORE.read_text(encoding="utf-8")
    after = AFTER.read_text(encoding="utf-8")
    source = after.replace("qcom,gpu-pwrlevels-0", "qcom,gpu-pwrlevels-1", 1)
    source = source.replace("qcom,speed-bin = <0>;", "qcom,speed-bin = <1>;", 1)
    fixture = "qcom,gpu-pwrlevel-bins {\n" + before + "\n" + source + "\n};\n"

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "kona-v2-gpu.dtsi"
        out = td / "patched.dtsi"
        src.write_text(fixture, encoding="utf-8")
        subprocess.run(
            [sys.executable, str(CLONE_TOOL), str(src), "--output", str(out)],
            check=True,
            text=True,
            capture_output=True,
        )
        clone = load_module(CLONE_TOOL, "clone_vendor_gpu_bin")
        _, _, result = clone.find_block(out.read_text(encoding="utf-8"), 0)
        expected = after.strip()
        assert result.strip() == expected


def test_daily_profile_enforces_587_cap() -> None:
    profile = PROFILE.read_text(encoding="utf-8")
    wrapper = WRAPPER.read_text(encoding="utf-8")
    assert "set_gpu_daily()" in profile
    assert 'CAP="$(select_gpu_at_or_below 587000000)"' in profile
    mode_cases = profile.split('case "$MODE" in', 1)[1]
    daily_case = mode_cases.split("daily)", 1)[1].split(";;", 1)[0]
    cpu_case = mode_cases.split("cpu)", 1)[1].split(";;", 1)[0]
    assert "set_gpu_daily" in daily_case
    assert "set_gpu_daily" in cpu_case
    assert 'daily) "$PROFILE" daily; "$BUS" auto; echo daily > "$MODE_FILE" ;;' in wrapper
    assert 'cpu) "$PROFILE" cpu; "$BUS" auto; echo cpu-max > "$MODE_FILE" ;;' in wrapper
    assert "daily-pending-bandwidth" in daily_case
    assert "cpu-max-pending-bandwidth" in cpu_case


def main() -> int:
    test_fdt_bundle()
    test_clone_vendor_bin()
    test_daily_profile_enforces_587_cap()
    print("Functional tool tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
