"""Exercise the shipped data and CLI in an isolated installation; no random draws."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_anchor_unfold import unfold


ROOT = Path(__file__).resolve().parents[1]


class PublicPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="anchor-public-test-")
        self.scratch = Path(self.temporary.name).resolve()
        self.assertTrue(self.scratch.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temporary.cleanup)
        self.package = self.scratch / "installed skill"
        self.package.mkdir()
        shutil.copy2(ROOT / "phase3_unfold.py", self.package)
        shutil.copytree(ROOT / "data/tarot", self.package / "data/tarot")
        self.env = os.environ.copy()
        for key in ("SYMBOL_ANCHOR_DATA", "MIRACLE_ADDON_DIR", "PYTHONPATH"):
            self.env.pop(key, None)
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def run_cli(self, payload, *, from_file=False):
        command = [sys.executable, "-X", "utf8", "-B", str(self.package / "phase3_unfold.py")]
        content = json.dumps(payload, ensure_ascii=False)
        if from_file:
            path = self.scratch / "input.json"
            path.write_text(content, encoding="utf-8")
            command.append(str(path))
            content = None
        else:
            command.append("-")
        return subprocess.run(command, input=content, text=True, encoding="utf-8",
                              cwd=self.scratch, env=self.env, capture_output=True, timeout=30)

    def add_miracle_module(self):
        shutil.copytree(ROOT / "addons/miracle-anchor-addon",
                        self.package / "addons/miracle-anchor-addon")

    def test_all_78_standard_cards_work_without_miracle_module_in_both_orientations(self):
        names = {}
        for name, card_id in unfold.NAME_TO_ID.items():
            names.setdefault(card_id, name)
        card_ids = sorted(unfold.load_card_index())
        self.assertEqual(len(card_ids), 78)
        for reversed_flag in (False, True):
            with self.subTest(reversed=reversed_flag):
                spread = [{"position": f"Card {i}", "card_name": names[card_id],
                           "reversed": reversed_flag} for i, card_id in enumerate(card_ids)]
                run = self.run_cli(spread)
                self.assertEqual(run.returncode, 0, run.stderr)
                result = json.loads(run.stdout)
                self.assertEqual(len(result["per_card"]), 78)
                self.assertEqual({c["card_id"] for c in result["per_card"]}, set(card_ids))
                self.assertEqual(result["spread_synthesis"]["counts"]["primary_card_count"], 78)
                self.assertTrue(all(c["reversed"] == reversed_flag for c in result["per_card"]))

    def test_all_14_miracle_cards_load_from_bundled_module_in_both_orientations(self):
        self.add_miracle_module()
        deck = json.loads((self.package / "addons/miracle-anchor-addon/miracle.json").read_text(encoding="utf-8"))
        self.assertEqual(len(deck["cards"]), 14)
        for reversed_flag in (False, True):
            with self.subTest(reversed=reversed_flag):
                spread = [{"position": f"Card {i}", "card_name": name, "reversed": reversed_flag}
                          for i, name in enumerate(deck["cards"])]
                run = self.run_cli({"spread": spread}, from_file=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                result = json.loads(run.stdout)
                self.assertEqual(len(result["per_card"]), 14)
                self.assertTrue(all(c["card_class"] == "miracle" for c in result["per_card"]))
                counts = result["spread_synthesis"]["counts"]
                self.assertEqual(counts["elements"], {})
                self.assertEqual(counts["other_elements"], {"Aether": 14})

    def test_mixed_packet_keeps_supplement_local_and_court_counting_separate(self):
        self.add_miracle_module()
        payload = {
            "spread": [
                {"position": "Pos 1 [Context]", "card_name": "Four of Wands", "reversed": False},
                {"position": "Pos 2 [Approach]", "card_name": "King of Pentacles", "reversed": False},
                {"position": "Pos 3 [Message]", "card_name": "Queen of Miracles", "reversed": True},
            ],
            "supplements": [{"for_position": "Pos 1", "card_name": "Two of Cups", "reversed": False}],
        }
        run = self.run_cli(payload)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        counts = result["spread_synthesis"]["counts"]
        self.assertEqual(counts["elements"], {"Fire": 1, "Earth": 1})
        self.assertEqual(counts["primary_qualities"], {"hot": 2, "dry": 2})
        self.assertEqual(counts["other_elements"], {"Aether": 1})
        self.assertEqual((counts["primary_card_count"], counts["supplement_card_count"]), (3, 1))
        supplement = next(c for c in result["per_card"] if c["supplement"])
        self.assertEqual(supplement["parent_position"], "Pos 1 [Context]")
        self.assertFalse(supplement["working_eligible"])
        self.assertEqual(supplement["raw_correspondences"]["element"], "Water")

    def test_miracle_input_without_module_reports_an_error_instead_of_partial_output(self):
        run = self.run_cli([{"position": "Context", "card_name": "Ace of Miracles", "reversed": False}])
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(run.stdout, "")
        self.assertIn("error", json.loads(run.stderr))


if __name__ == "__main__":
    unittest.main()
