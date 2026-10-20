"""Set KICO_MEANINGS_PACK to test the optional separately installed DLC."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from test_anchor_unfold import unfold

PACK = os.environ.get("KICO_MEANINGS_PACK")


@unittest.skipUnless(PACK, "Optional DLC not installed; set KICO_MEANINGS_PACK")
class MeaningIntegrationTests(unittest.TestCase):
    def test_enabled_text_and_main_supplement_deduplication(self):
        spread = {"spread": [
            {"position": "Pos 1", "card_name": "Strength"},
            {"position": "Pos 2", "card_name": "Justice"},
            {"position": "Pos 3", "card_name": "Ace of Cups"}],
            "supplements": [{"for_position": "Pos 1", "card_name": "Strength"}]}
        original = deepcopy(spread)
        off = unfold.unfold_spread(spread, meanings_pack=False)
        on = unfold.unfold_spread(spread, meanings_pack=PACK)
        self.assertEqual(spread, original)
        self.assertFalse(off["meaning_pack"]["enabled"])
        self.assertEqual(on["spread_synthesis"], off["spread_synthesis"])
        self.assertEqual(len(on["author_meanings"]), 2)
        self.assertEqual(on["per_card"][0]["author_meaning_ref"], "atu_11_fortitude")
        self.assertEqual(on["per_card"][1]["author_meaning_ref"], "atu_08_justice")
        for before, after in zip(off["per_card"], on["per_card"]):
            after = dict(after)
            after.pop("author_meaning_ref", None)
            self.assertEqual(before, after)
        self.assertFalse(on["per_card"][-1]["working_eligible"])
        self.assertTrue(on["author_meanings"]["atu_11_fortitude"]["text"].startswith("# 力量"))

    def test_nonmajor_only_has_no_text(self):
        out = unfold.unfold_spread([{"card_name": "Ace of Cups", "position": "Pos 1"}],
                                   meanings_pack=PACK)
        self.assertTrue(out["meaning_pack"]["enabled"])
        self.assertEqual(out["author_meanings"], {})

    def test_explicit_missing_pack_fails_even_without_majors(self):
        with self.assertRaises(ValueError):
            unfold.unfold_spread([{"card_name": "Ace of Cups"}],
                                 meanings_pack=Path(PACK) / "missing")


if __name__ == "__main__":
    unittest.main()
