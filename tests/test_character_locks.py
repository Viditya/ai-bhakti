import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_character_locks import MANIFEST_PATH, validate_manifest


class CharacterLockTests(unittest.TestCase):
    def test_current_registry_is_valid(self):
        self.assertEqual(validate_manifest(), [])

    def test_every_character_root_is_a_locked_stage(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for character in manifest["characters"].values():
            root = character["identity_root_stage"]
            self.assertEqual(character["stages"][root]["status"], "locked")

    def test_checksum_drift_is_rejected(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest["characters"]["indra"]["stages"]["ageless_adult"]["sha256"] = "0" * 64
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=False
        ) as output:
            json.dump(manifest, output)
            temporary_path = Path(output.name)
        try:
            errors = validate_manifest(temporary_path)
            self.assertTrue(any("checksum mismatch" in error for error in errors))
        finally:
            temporary_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
