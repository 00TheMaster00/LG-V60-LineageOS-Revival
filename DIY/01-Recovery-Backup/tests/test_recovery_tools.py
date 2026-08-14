from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parents[1] / "tools"
HASHER = TOOLS / "hash_directory.py"
VERIFIER = TOOLS / "verify_manifest.py"


class RecoveryToolTests(unittest.TestCase):
    def test_manifest_passes_then_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "lun0_drm.img.test-fixture").write_bytes(b"fixture-drm")
            nested = root / "nested"
            nested.mkdir()
            (nested / "lun1_modem_a.img.test-fixture").write_bytes(b"fixture-modem")
            manifest = root / "SHA256SUMS.csv"

            created = subprocess.run(
                [sys.executable, str(HASHER), "--directory", str(root), "--output", str(manifest)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)

            verified = subprocess.run(
                [sys.executable, str(VERIFIER), "--manifest", str(manifest)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

            (nested / "lun1_modem_a.img.test-fixture").write_bytes(b"changed")
            changed = subprocess.run(
                [sys.executable, str(VERIFIER), "--manifest", str(manifest)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(changed.returncode, 0)
            self.assertIn("mismatch", changed.stdout)


if __name__ == "__main__":
    unittest.main()

