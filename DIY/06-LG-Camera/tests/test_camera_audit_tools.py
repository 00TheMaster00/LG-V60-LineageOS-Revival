from __future__ import annotations

import importlib.util
import csv
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parents[1] / "tools"


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SMALI = load("audit_smali_changes", "audit_smali_changes.py")


class CameraAuditToolTests(unittest.TestCase):
    def test_published_classes3_sources_match_candidate_manifest(self) -> None:
        camera_root = TOOLS.parent
        manifest = camera_root / "audit" / "expected-smali-changes.csv"
        expected: dict[str, str] = {}
        with manifest.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["status"] == "added" and row["path"].startswith("classes3/"):
                    expected[row["path"]] = row["candidate_sha256"]

        published = camera_root / "source"
        actual = {
            path.relative_to(published).as_posix(): hashlib.sha256(
                SMALI.normalized_bytes(path)
            ).hexdigest().upper()
            for path in (published / "classes3").rglob("*.smali")
        }
        self.assertEqual(len(expected), 10)
        self.assertEqual(actual, expected)

    def test_smali_audit_ignores_debug_but_detects_opcode_change(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stock = root / "stock" / "classes"
            candidate = root / "candidate" / "classes"
            stock.mkdir(parents=True)
            candidate.mkdir(parents=True)
            old = stock / "Example.smali"
            new = candidate / "Example.smali"
            old.write_text(
                ".class public LExample;\n.method public run()V\n.line 1\nreturn-void\n.end method\n",
                encoding="utf-8",
            )
            new.write_text(
                ".class public LExample;\n.method public run()V\n.line 99\nreturn-void\n.end method\n",
                encoding="utf-8",
            )
            self.assertEqual(SMALI.compare(SMALI.collect(stock.parent), SMALI.collect(candidate.parent)), [])

            new.write_text(
                ".class public LExample;\n.method public run()V\nconst/4 v0, 0x1\nreturn-void\n.end method\n",
                encoding="utf-8",
            )
            changes = SMALI.compare(SMALI.collect(stock.parent), SMALI.collect(candidate.parent))
            self.assertEqual(len(changes), 1)
            self.assertEqual(changes[0][0:2], ("changed", "classes/Example.smali"))


if __name__ == "__main__":
    unittest.main()
