from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import unittest


CAMERA = Path(__file__).resolve().parents[1]
NATIVE = CAMERA / "source" / "native"
SOURCE = NATIVE / "surface_usage_shim.cpp"
SCRIPT = NATIVE / "build_surface_usage_shim.sh"
APK_CHANGES = CAMERA / "audit" / "expected-apk-entry-changes.csv"

SOURCE_SHA256 = "3587D81948D2F47BBE95BDDAC7A62F7DFD0195F87EAF2EA3938CEA99F91E0D42"
LIBRARY_SHA256 = "6C10BF25D9CFE3C719851D0F2951F02F06B2A47BE90E0A498509E2B9826CA5D1"


class NativeRecipeTests(unittest.TestCase):
    def test_source_and_recipe_pin_expected_library(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest().upper(), SOURCE_SHA256)
        recipe = SCRIPT.read_text(encoding="utf-8").upper()
        self.assertIn(SOURCE_SHA256, recipe)
        self.assertIn(LIBRARY_SHA256, recipe)
        self.assertIn("AARCH64-LINUX-ANDROID35", recipe)
        self.assertIn("JAVA_COM_LGE_CAMERA_UTIL_SURFACEUSAGESHIM_NATIVESETCONSUMERUSAGE", recipe)

        with APK_CHANGES.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        library = [
            row for row in rows
            if row["path"] == "lib/arm64-v8a/liblgcamera_surface_usage.so"
        ]
        self.assertEqual(len(library), 1)
        self.assertEqual(library[0]["candidate_size"], "3872")
        self.assertEqual(library[0]["candidate_sha256"], LIBRARY_SHA256)


if __name__ == "__main__":
    unittest.main()
