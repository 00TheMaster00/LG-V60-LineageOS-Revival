from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "build_candidate24.py"
SPEC = importlib.util.spec_from_file_location("build_candidate24", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CameraBuilderTests(unittest.TestCase):
    def test_pinned_release_constants(self) -> None:
        self.assertEqual(MODULE.INPUT_SIZE, 106_673_076)
        self.assertEqual(
            MODULE.INPUT_SHA256,
            "65D69A9E0DB652F43E232EC4AE86DCFC11AC688E324C5103CAAB1FECB27807E8",
        )
        self.assertEqual(MODULE.PATCH_SIZE, 13_676_109)
        self.assertEqual(
            MODULE.PATCH_SHA256,
            "4FB8A5D55E8E048AF737851D19CF98ABF1E2FC55F5AC119415E24746B3DCF485",
        )
        self.assertEqual(MODULE.OUTPUT_SIZE, 101_512_334)
        self.assertEqual(
            MODULE.OUTPUT_SHA256,
            "E428C92DA17247F0DC3316C7EE3C1725979A242522D6618B104F81DA983CAF71",
        )

    def test_wrong_stock_is_rejected_before_patching(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stock = root / "wrong.apk"
            patch = root / "patch.bsdiff"
            output = root / "output.apk"
            stock.write_bytes(b"not the EA40g APK")
            patch.write_bytes(b"not a patch")
            with self.assertRaises(MODULE.VerificationError):
                MODULE.apply_verified_patch(stock, patch, output)
            self.assertFalse(output.exists())

    def test_verified_patch_success_path_is_atomic(self) -> None:
        import bsdiff4

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stock = root / "stock.bin"
            patch = root / "delta.bsdiff"
            output = root / "output.bin"
            stock_bytes = b"synthetic stock camera fixture\n"
            output_bytes = b"synthetic candidate camera fixture\n"
            stock.write_bytes(stock_bytes)
            patch.write_bytes(bsdiff4.diff(stock_bytes, output_bytes))

            spec = MODULE.ArtifactSpec(
                input_size=len(stock_bytes),
                input_sha256=hashlib.sha256(stock_bytes).hexdigest().upper(),
                patch_size=patch.stat().st_size,
                patch_sha256=MODULE.sha256_file(patch),
                output_size=len(output_bytes),
                output_sha256=hashlib.sha256(output_bytes).hexdigest().upper(),
            )
            MODULE.apply_verified_patch(stock, patch, output, spec=spec)

            self.assertEqual(output.read_bytes(), output_bytes)
            self.assertFalse(list(root.glob(".candidate24-*.tmp")))

    def test_hash_helper(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / "sample"
            sample.write_bytes(b"LG V60\n")
            self.assertEqual(
                MODULE.sha256_file(sample),
                "4CBDE8951F3149527BEC24559446DC0C7DC69DC05D9CE780087D80F9E701811C",
            )


if __name__ == "__main__":
    unittest.main()
