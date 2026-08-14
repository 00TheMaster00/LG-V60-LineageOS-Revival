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
    def create_fixture(self, root: Path) -> Path:
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
        return manifest

    def verify(self, manifest: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VERIFIER), "--manifest", str(manifest)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_manifest_passes_then_detects_change(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self.create_fixture(root)
            verified = self.verify(manifest)
            self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)

            (root / "nested" / "lun1_modem_a.img.test-fixture").write_bytes(b"changed")
            changed = self.verify(manifest)
            self.assertNotEqual(changed.returncode, 0)
            self.assertIn("mismatch", changed.stdout)

    def test_manifest_detects_extra_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self.create_fixture(root)
            (root / "unexpected-partition.img.test-fixture").write_bytes(b"extra")

            verified = self.verify(manifest)
            self.assertNotEqual(verified.returncode, 0)
            self.assertIn("extra: unexpected-partition.img.test-fixture", verified.stdout)

    def test_generator_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "partition.img.test-fixture"
            target.write_bytes(b"fixture")
            link = root / "linked-partition.img.test-fixture"
            try:
                link.symlink_to(target)
            except OSError as error:
                self.skipTest(f"symlink creation unavailable: {error}")

            manifest = root / "SHA256SUMS.csv"
            created = subprocess.run(
                [sys.executable, str(HASHER), "--directory", str(root), "--output", str(manifest)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(created.returncode, 0)
            self.assertIn("symlink not allowed", created.stderr)
            self.assertFalse(manifest.exists())


if __name__ == "__main__":
    unittest.main()
