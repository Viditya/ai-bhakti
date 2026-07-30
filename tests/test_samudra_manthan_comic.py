import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
COMIC = REPO / "experiments" / "comicbook" / "samudra_manthan_001"
MANIFEST = REPO / "references" / "character_locks" / "manifest.json"


class SamudraManthanComicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = json.loads((COMIC / "content.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_story_has_nine_ordered_panels(self):
        panels = self.content["panels"]
        self.assertEqual(len(panels), 9)
        self.assertEqual(
            [panel["id"] for panel in panels],
            [f"panel-{number:02}" for number in range(1, 10)],
        )

    def test_every_panel_has_publishable_art_and_hindi_caption(self):
        for number, panel in enumerate(self.content["panels"], 1):
            art = COMIC / "art" / f"panel_{number:02}.png"
            self.assertTrue(art.is_file(), art)
            self.assertGreater(art.stat().st_size, 100_000)
            caption = panel["caption_hi"]
            self.assertGreater(len(caption), 20)
            self.assertTrue(any("\u0900" <= char <= "\u097f" for char in caption))

    def test_every_requested_character_lock_resolves(self):
        registry = self.manifest["characters"]
        for panel in self.content["panels"]:
            for request in panel["characters"]:
                character = registry[request["character_id"]]
                stage = character["stages"][request["age_stage"]]
                self.assertEqual(stage["status"], "locked")
                if "form_id" in request:
                    form = character["forms"][request["form_id"]]
                    self.assertEqual(form["status"], "locked")


if __name__ == "__main__":
    unittest.main()
