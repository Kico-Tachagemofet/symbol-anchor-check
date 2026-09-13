"""Deterministic Phase 3 contracts; no draws or live tarot data are used.

Set ANCHOR_UNFOLD_PATH to exercise a staged candidate before installation.
Otherwise the tests use the repository-local script.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
UNFOLD_PATH = Path(os.environ.get(
    "ANCHOR_UNFOLD_PATH",
    str(ROOT / "phase3_unfold.py"),
))


def load_unfold_module():
    spec = importlib.util.spec_from_file_location("anchor_unfold_under_test", UNFOLD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import the Phase 3 entry point: {UNFOLD_PATH}")
    module = importlib.util.module_from_spec(spec)
    # Importing a test candidate must not write bytecode into a live skill.
    with mock.patch.object(sys, "dont_write_bytecode", True):
        spec.loader.exec_module(module)
    return module


unfold = load_unfold_module()


def pip_record(element, qualities, sephira="Chesed", world="Atziluth"):
    return {
        "card_class": "minor_pip",
        "book_t": {
            "element": element,
            "primary_qualities": qualities,
            "sephira": sephira,
            "world": world,
            "decan": None,
            "decan_dignity": None,
        },
    }


CARD_INDEX = {
    "4_wands": pip_record("Fire", ["hot", "dry"]),
    "2_cups": pip_record("Water", ["cold", "moist"], "Chokmah", "Briah"),
    "8_disks": pip_record("Earth", ["cold", "dry"], "Hod", "Assiah"),
    "king_of_disks": {
        "card_class": "court",
        "book_t": {
            "element_compound": "Fire of Earth",
            "primary_qualities": ["hot", "dry"],
            "celestial_quadrant": "synthetic test quadrant",
        },
    },
}


def synthesis_card(position, raw, *, supplement=False, card_class="minor_pip"):
    return {
        "card_name": "Synthetic fixture",
        "position": position,
        "supplement": supplement,
        "card_class": card_class,
        "raw_correspondences": deepcopy(raw),
    }


class NormalizeSpreadInputTests(unittest.TestCase):
    def setUp(self):
        self.main = {"position": "Pos 1 [状态]", "card_name": "Four of Wands", "reversed": False}
        self.supplement = {
            "for_position": self.main["position"],
            "card_name": "Two of Cups",
            "reversed": True,
        }

    def test_plain_list_and_wrapped_spread_keep_the_same_main_cards(self):
        plain = unfold.normalize_spread_input([self.main])
        wrapped = unfold.normalize_spread_input({"spread": [self.main]})
        self.assertEqual(plain, wrapped)
        self.assertEqual(plain[0]["card_name"], "Four of Wands")
        self.assertFalse(plain[0].get("supplement", False))

    def test_top_level_supplements_are_not_silently_dropped(self):
        normalized = unfold.normalize_spread_input({
            "spread": [self.main], "supplements": [self.supplement],
        })
        self.assertEqual(len(normalized), 2)
        supplement = next(card for card in normalized if card.get("supplement"))
        self.assertEqual(supplement["card_name"], "Two of Cups")
        self.assertTrue(supplement["reversed"])
        self.assertEqual(supplement["parent_position"], self.main["position"])

    def test_embedded_and_top_level_supplements_have_equivalent_meaning(self):
        embedded_card = {
            **self.supplement,
            "position": "clarifier of Pos 1",
            "supplement": True,
        }
        embedded = unfold.normalize_spread_input([self.main, embedded_card])
        top_level = unfold.normalize_spread_input({
            "spread": [self.main], "supplements": [self.supplement],
        })
        # Display labels may be supplied or generated. Parentage, orientation,
        # identity, and participation must not depend on the input convention.
        keys = ("card_name", "reversed", "supplement", "parent_position")
        project = lambda cards: [tuple(card.get(key) for key in keys) for card in cards]
        self.assertEqual(project(embedded), project(top_level))

    def test_parent_position_is_preserved_for_embedded_supplements(self):
        embedded = {
            "position": "local clarification",
            "parent_position": self.main["position"],
            "card_name": "Two of Cups",
            "supplement": True,
        }
        normalized = unfold.normalize_spread_input([self.main, embedded])
        self.assertEqual(normalized[1]["parent_position"], self.main["position"])
        self.assertTrue(normalized[1]["supplement"])

    def test_unknown_parent_fails_instead_of_turning_into_a_main_card(self):
        invalid = {**self.supplement, "for_position": "Pos 99 [missing]"}
        with self.assertRaisesRegex(ValueError, "Pos 99"):
            unfold.normalize_spread_input({"spread": [self.main], "supplements": [invalid]})

    def test_same_supplement_in_both_input_channels_is_rejected(self):
        embedded = {
            **self.supplement,
            "position": "local clarification",
            "supplement": True,
        }
        with self.assertRaisesRegex(ValueError, "(?i)duplicate|重复"):
            unfold.normalize_spread_input({
                "spread": [self.main, embedded],
                "supplements": [deepcopy(self.supplement)],
            })

    def test_reversed_flag_cannot_disguise_a_duplicate_supplement(self):
        with self.assertRaisesRegex(ValueError, "(?i)duplicate|重复"):
            unfold.normalize_spread_input({
                "spread": [self.main],
                "supplements": [self.supplement, {**self.supplement, "reversed": False}],
            })

    def test_different_supplements_for_one_parent_are_not_deduplicated(self):
        normalized = unfold.normalize_spread_input({
            "spread": [self.main],
            "supplements": [self.supplement, {**self.supplement, "card_name": "Eight of Pentacles"}],
        })
        supplements = [card for card in normalized if card.get("supplement")]
        self.assertEqual(len(supplements), 2)
        self.assertEqual({card["parent_position"] for card in supplements}, {self.main["position"]})

    def test_short_parent_reference_resolves_to_the_full_primary_label(self):
        normalized = unfold.normalize_spread_input({
            "spread": [self.main],
            "supplements": [{**self.supplement, "for_position": "Pos 1"}],
        })
        self.assertEqual(normalized[1]["parent_position"], self.main["position"])

    def test_supplement_without_a_parent_fails_clearly(self):
        with self.assertRaisesRegex(ValueError, "(?i)parent|for_position|父"):
            unfold.normalize_spread_input({
                "spread": [self.main],
                "supplements": [{"card_name": "Two of Cups"}],
            })

    def test_duplicate_primary_positions_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "(?i)duplicate|重复"):
            unfold.normalize_spread_input([
                self.main, {**self.main, "card_name": "Eight of Pentacles"},
            ])

    def test_normalization_neither_mutates_nor_aliases_input(self):
        packet = {
            "spread": [{**self.main, "metadata": {"note": "keep"}}],
            "supplements": [{**self.supplement, "metadata": {"note": "local"}}],
        }
        before = deepcopy(packet)
        normalized = unfold.normalize_spread_input(packet)
        self.assertEqual(packet, before)
        normalized[0]["metadata"]["note"] = "changed"
        normalized[1]["metadata"]["note"] = "changed"
        self.assertEqual(packet, before)


class SpreadSynthesisTests(unittest.TestCase):
    def test_supplements_cannot_change_any_global_attribute_count(self):
        main = synthesis_card("Pos 1", CARD_INDEX["4_wands"]["book_t"])
        water = synthesis_card("Supp: Pos 1", CARD_INDEX["2_cups"]["book_t"], supplement=True)
        earth = synthesis_card("Supp: Pos 1", CARD_INDEX["8_disks"]["book_t"], supplement=True)
        baseline = unfold.synthesize_spread([main])
        result = unfold.synthesize_spread([main, water, earth])
        for key in ("elements", "primary_qualities", "sephiroth", "pillars", "other_elements"):
            with self.subTest(attribute=key):
                self.assertEqual(result["counts"][key], baseline["counts"][key])
        self.assertEqual(result["counts"]["elements"], {"Fire": 1})
        self.assertEqual(result["counts"]["primary_qualities"], {"hot": 1, "dry": 1})
        self.assertEqual(result["counts"]["sephiroth"], {"Chesed": 1})
        self.assertEqual(result["counts"]["pillars"], {"Right": 1})
        self.assertEqual(result["counts"]["primary_card_count"], 1)
        self.assertEqual(result["counts"]["supplement_card_count"], 2)
        self.assertEqual(result["participation"]["scope"], "primary_cards_only")
        self.assertEqual(result["participation"]["working_positions"], ["Pos 1"])
        self.assertEqual(result["participation"]["supplement_positions"], ["Supp: Pos 1", "Supp: Pos 1"])

    def test_court_counts_suit_once_and_keeps_rank_qualities(self):
        raw = CARD_INDEX["king_of_disks"]["book_t"]
        result = unfold.synthesize_spread([synthesis_card("Pos 1", raw, card_class="court")])
        self.assertEqual(result["counts"]["elements"], {"Earth": 1})
        self.assertEqual(sum(result["counts"]["elements"].values()), 1)
        self.assertEqual(result["counts"]["primary_qualities"], {"hot": 1, "dry": 1})
        self.assertNotIn("cold", result["counts"]["primary_qualities"])

    def test_aether_remains_separate_but_keeps_each_sephirothic_anchor(self):
        aether = synthesis_card("Pos 1", {
            "element": "Aether", "sephira": ["Hod", "Yesod"],
        }, card_class="miracle")
        water = synthesis_card("Pos 2", CARD_INDEX["2_cups"]["book_t"])
        result = unfold.synthesize_spread([aether, water])
        self.assertEqual(result["counts"]["elements"], {"Water": 1})
        self.assertEqual(result["counts"]["other_elements"], {"Aether": 1})
        self.assertEqual(result["counts"]["primary_qualities"], {"cold": 1, "moist": 1})
        self.assertEqual(result["counts"]["sephiroth"], {"Hod": 1, "Yesod": 1, "Chokmah": 1})
        self.assertEqual(result["counts"]["pillars"], {"Left": 1, "Middle": 1, "Right": 1})
        self.assertEqual(result["participation"]["working_positions"], ["Pos 1", "Pos 2"])

    def test_aether_supplement_does_not_enter_global_anchors_or_other_elements(self):
        aether = synthesis_card("Supp: Pos 1", {
            "element": "Aether", "sephira": ["Hod", "Yesod"],
        }, supplement=True, card_class="miracle")
        result = unfold.synthesize_spread([aether])
        for key in ("elements", "primary_qualities", "sephiroth", "pillars", "other_elements"):
            self.assertEqual(result["counts"][key], {})
        self.assertEqual(result["counts"]["primary_card_count"], 0)
        self.assertEqual(result["counts"]["supplement_card_count"], 1)
        self.assertEqual(result["participation"]["working_positions"], [])

    def test_empty_spread_has_zero_participants_and_no_invented_attributes(self):
        result = unfold.synthesize_spread([])
        self.assertEqual(result["counts"], {
            "elements": {}, "primary_qualities": {}, "sephiroth": {},
            "pillars": {}, "other_elements": {},
            "primary_card_count": 0, "supplement_card_count": 0,
        })
        self.assertEqual(result["participation"]["working_positions"], [])
        self.assertEqual(result["participation"]["supplement_positions"], [])

    def test_same_card_at_two_primary_positions_counts_as_two_occurrences(self):
        first = synthesis_card("Pos 1", CARD_INDEX["4_wands"]["book_t"])
        second = {**deepcopy(first), "position": "Pos 2"}
        result = unfold.synthesize_spread([first, second])
        self.assertEqual(result["counts"]["elements"], {"Fire": 2})
        self.assertEqual(result["counts"]["primary_qualities"], {"hot": 2, "dry": 2})
        self.assertEqual(result["counts"]["sephiroth"], {"Chesed": 2})
        self.assertEqual(result["counts"]["primary_card_count"], 2)
        self.assertEqual(result["participation"]["working_positions"], ["Pos 1", "Pos 2"])


class UnfoldSpreadIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.index = deepcopy(CARD_INDEX)
        self.loader = mock.patch.object(unfold, "load_card_index", return_value=self.index)
        self.loader.start()
        self.addCleanup(self.loader.stop)

    def test_supplement_keeps_its_local_unfolding_without_global_participation(self):
        packet = {
            "spread": [{"position": "Pos 1 [状态]", "card_name": "Four of Wands"}],
            "supplements": [{
                "for_position": "Pos 1", "card_name": "Two of Cups", "reversed": True,
            }],
        }
        result = unfold.unfold_spread(unfold.normalize_spread_input(packet))
        main, supplement = result["per_card"]
        self.assertEqual(main["role"], "primary")
        self.assertTrue(main["working_eligible"])
        self.assertIsNone(main["parent_position"])
        self.assertEqual(supplement["role"], "supplement")
        self.assertFalse(supplement["working_eligible"])
        self.assertEqual(supplement["parent_position"], main["position"])
        self.assertEqual(supplement["raw_correspondences"]["element"], "Water")
        self.assertTrue(supplement["reversed"])
        self.assertTrue(supplement["property_unfolding"])
        self.assertTrue(supplement["compound_image"])
        self.assertEqual(set(supplement["property_unfolding"]), {
            "element_layer", "sephira_layer", "decan_layer", "dignity_layer", "position_layer",
        })
        self.assertEqual(result["spread_synthesis"]["counts"]["elements"], {"Fire": 1})

    def test_direct_list_interface_also_normalizes_parentage(self):
        result = unfold.unfold_spread([
            {"position": "Pos 1 [状态]", "card_name": "Four of Wands"},
            {"position": "clarifier", "for_position": "Pos 1", "card_name": "Eight of Pentacles", "supplement": True},
        ])
        self.assertEqual(result["per_card"][1]["parent_position"], "Pos 1 [状态]")
        self.assertFalse(result["per_card"][1]["working_eligible"])
        self.assertEqual(result["spread_synthesis"]["counts"]["pillars"], {"Right": 1})

    def test_reversal_does_not_change_deterministic_element_and_quality_counts(self):
        upright = unfold.unfold_spread([{
            "position": "Pos 1", "card_name": "King of Pentacles", "reversed": False,
        }])
        reversed_result = unfold.unfold_spread([{
            "position": "Pos 1", "card_name": "King of Pentacles", "reversed": True,
        }])
        self.assertEqual(upright["spread_synthesis"]["counts"], reversed_result["spread_synthesis"]["counts"])
        self.assertFalse(upright["per_card"][0]["reversed"])
        self.assertTrue(reversed_result["per_card"][0]["reversed"])

    def test_unfolding_does_not_mutate_input_or_the_shared_card_index(self):
        cards = [{"position": "Pos 1", "card_name": "Four of Wands"}]
        original_cards, original_index = deepcopy(cards), deepcopy(self.index)
        result = unfold.unfold_spread(cards)
        self.assertEqual(cards, original_cards)
        self.assertEqual(self.index, original_index)
        result["per_card"][0]["raw_correspondences"]["primary_qualities"].append("changed")
        self.assertEqual(self.index, original_index)

    def test_miracle_primary_is_eligible_without_becoming_a_classical_element(self):
        addon = mock.Mock()
        addon.load_miracle_index.return_value = {
            "element": "Aether",
            "cards": {"King of Miracles": {"core_meaning": "fixture", "sephira": ["Kether", "Tiphareth"]}},
        }
        addon.unfold_miracle.return_value = {"element_layer": "fixture"}
        addon.compound_miracle.return_value = "fixture scene"
        with mock.patch.object(unfold, "miracle_unfold", addon):
            result = unfold.unfold_spread([{"position": "Pos 1", "card_name": "King of Miracles"}])
        card = result["per_card"][0]
        self.assertTrue(card["working_eligible"])
        self.assertEqual(card["role"], "primary")
        self.assertEqual(card["raw_correspondences"]["element"], "Aether")
        self.assertEqual(result["spread_synthesis"]["counts"]["elements"], {})
        self.assertEqual(result["spread_synthesis"]["counts"]["other_elements"], {"Aether": 1})
        self.assertEqual(result["spread_synthesis"]["counts"]["sephiroth"], {"Kether": 1, "Tiphareth": 1})
        addon.load_miracle_index.assert_called_once_with()

    def test_standard_cards_do_not_load_the_miracle_addon(self):
        addon = mock.Mock()
        addon.load_miracle_index.side_effect = AssertionError("Standard cards must not need miracle data")
        with mock.patch.object(unfold, "miracle_unfold", addon):
            result = unfold.unfold_spread([{"position": "Pos 1", "card_name": "Four of Wands"}])
        self.assertEqual(len(result["per_card"]), 1)
        addon.load_miracle_index.assert_not_called()


if __name__ == "__main__":
    unittest.main()
