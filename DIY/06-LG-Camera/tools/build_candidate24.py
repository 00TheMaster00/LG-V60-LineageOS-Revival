#!/usr/bin/env python3
"""Reconstruct the tested LG Camera Candidate 24 from the exact EA40g APK."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import tempfile


INPUT_SIZE = 106_673_076
INPUT_SHA256 = "65D69A9E0DB652F43E232EC4AE86DCFC11AC688E324C5103CAAB1FECB27807E8"
PATCH_SIZE = 13_676_109
PATCH_SHA256 = "4FB8A5D55E8E048AF737851D19CF98ABF1E2FC55F5AC119415E24746B3DCF485"
OUTPUT_SIZE = 101_512_334
OUTPUT_SHA256 = "E428C92DA17247F0DC3316C7EE3C1725979A242522D6618B104F81DA983CAF71"
CHUNK_SIZE = 8 * 1024 * 1024


class VerificationError(RuntimeError):
    """Raised when an input or generated artifact is not byte-exact."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest().upper()


def verify_file(path: Path, expected_size: int, expected_hash: str, label: str) -> None:
    if not path.is_file():
        raise VerificationError(f"{label} does not exist or is not a file: {path}")
    actual_size = path.stat().st_size
    if actual_size != expected_size:
        raise VerificationError(
            f"{label} size mismatch: expected {expected_size}, got {actual_size}"
        )
    actual_hash = sha256_file(path)
    if actual_hash != expected_hash.upper():
        raise VerificationError(
            f"{label} SHA-256 mismatch: expected {expected_hash}, got {actual_hash}"
        )


def apply_verified_patch(stock: Path, patch: Path, output: Path, force: bool = False) -> None:
    verify_file(stock, INPUT_SIZE, INPUT_SHA256, "EA40g stock APK")
    verify_file(patch, PATCH_SIZE, PATCH_SHA256, "Candidate 24 delta")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not force:
        raise VerificationError(f"output already exists (use --force to replace it): {output}")

    try:
        import bsdiff4
    except ImportError as exc:
        raise VerificationError(
            "missing dependency bsdiff4; install requirements-camera.txt first"
        ) from exc

    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=".candidate24-", suffix=".apk.tmp", dir=output.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)

        bsdiff4.file_patch(str(stock), str(temporary), str(patch))
        verify_file(temporary, OUTPUT_SIZE, OUTPUT_SHA256, "generated Candidate 24 APK")
        os.replace(temporary, output)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build byte-exact LG Camera Candidate 24 from an owned EA40g APK."
    )
    parser.add_argument("--stock", required=True, type=Path, help="exact EA40g LGCameraApp.apk")
    parser.add_argument(
        "--patch",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "patches" / "EA40g-to-Candidate24.bsdiff",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        apply_verified_patch(
            args.stock.resolve(), args.patch.resolve(), args.output.resolve(), args.force
        )
    except VerificationError as exc:
        print(f"ERROR: {exc}")
        return 1

    print("PASS: Candidate 24 reconstructed and verified")
    print(f"Output: {args.output.resolve()}")
    print(f"Bytes:  {OUTPUT_SIZE}")
    print(f"SHA256: {OUTPUT_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

