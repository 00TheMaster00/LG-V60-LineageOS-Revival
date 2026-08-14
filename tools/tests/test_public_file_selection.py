from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parents[1]


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load("audit_public_release", "audit_public_release.py")
MANIFEST = load("generate_release_manifest", "generate_release_manifest.py")


class PublicFileSelectionTests(unittest.TestCase):
    def test_third_party_actions_are_pinned_to_full_commits(self) -> None:
        root = TOOLS.parent
        workflow = root / ".github" / "workflows" / "ci.yml"
        actions = re.findall(r"^\s*-\s+uses:\s+([^\s#]+)", workflow.read_text(encoding="utf-8"), re.M)
        self.assertTrue(actions)
        for action in actions:
            if action.startswith("./"):
                continue
            self.assertRegex(action, r"^[^@]+@[0-9a-fA-F]{40}$")

    def test_force_added_ignored_file_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / ".gitignore").write_text("private/\n", encoding="utf-8")
            private = root / "private"
            private.mkdir()
            secret = private / "force-added.txt"
            secret.write_text("fixture only", encoding="utf-8")

            subprocess.run(
                ["git", "-C", str(root), "add", ".gitignore"], check=True
            )
            self.assertNotIn(secret, AUDIT.files(root))

            subprocess.run(
                ["git", "-C", str(root), "add", "-f", "private/force-added.txt"],
                check=True,
            )
            self.assertIn(secret, AUDIT.files(root))
            self.assertIn(secret, MANIFEST.public_files(root))


if __name__ == "__main__":
    unittest.main()
