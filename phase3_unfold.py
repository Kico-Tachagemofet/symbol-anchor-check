#!/usr/bin/env python3
"""Deterministic Book T unfolding; optional Miracle add-on. No random draws.

Run: python phase3_unfold.py input.json
Accepts a card array or {"spread": [...], "supplements": [...]}.
"""

import json
import os
import re
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

# ── stdout/stderr UTF-8 guard ───────────────────────────────
# Use UTF-8 for redirected output as well as interactive Windows terminals.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Data defaults to this checkout; overrides are explicit.
DATA_DIR = Path(os.environ.get("SYMBOL_ANCHOR_DATA", str(Path(__file__).resolve().parent / "data/tarot"))).expanduser()
_here = Path(__file__).resolve().parent
_addon_override = os.environ.get("MIRACLE_ADDON_DIR")
_addon_candidates = ([Path(_addon_override).expanduser()] if _addon_override else [
    _here / "addons/miracle-anchor-addon",
    _here.parent / "miracle-anchor-addon",
])
sys.dont_write_bytecode = True
miracle_unfold = None
for _candidate in _addon_candidates:
    if (_candidate / "miracle_unfold.py").is_file():
        sys.path.insert(0, str(_candidate))
        import miracle_unfold
        break

# ── Book T name → card_id mapping ───────────────────────────
# Spirit draw output uses RWS names; Book T uses Golden Dawn IDs.
NAME_TO_ID = {
    # Major Arcana
    "The Fool": "atu_00_fool",
    "Fool": "atu_00_fool",
    "The Magician": "atu_01_magician",
    "Magician": "atu_01_magician",
    "The High Priestess": "atu_02_high_priestess",
    "High Priestess": "atu_02_high_priestess",
    "The Empress": "atu_03_empress",
    "Empress": "atu_03_empress",
    "The Emperor": "atu_04_emperor",
    "Emperor": "atu_04_emperor",
    "The Hierophant": "atu_05_hierophant",
    "Hierophant": "atu_05_hierophant",
    "The Lovers": "atu_06_lovers",
    "Lovers": "atu_06_lovers",
    "The Chariot": "atu_07_chariot",
    "Chariot": "atu_07_chariot",
    "Justice": "atu_08_justice",
    "Adjustment": "atu_08_justice",
    "The Hermit": "atu_09_hermit",
    "Hermit": "atu_09_hermit",
    "Wheel of Fortune": "atu_10_wheel_of_fate",
    "Fortitude": "atu_11_fortitude",
    "Strength": "atu_11_fortitude",
    "The Hanged Man": "atu_12_hanged_man",
    "Hanged Man": "atu_12_hanged_man",
    "Death": "atu_13_death",
    "Temperance": "atu_14_temperance",
    "Art": "atu_14_temperance",
    "The Devil": "atu_15_devil",
    "Devil": "atu_15_devil",
    "The Tower": "atu_16_blasted_tower",
    "Tower": "atu_16_blasted_tower",
    "The Star": "atu_17_star",
    "Star": "atu_17_star",
    "The Moon": "atu_18_moon",
    "Moon": "atu_18_moon",
    "The Sun": "atu_19_sun",
    "Sun": "atu_19_sun",
    "Judgment": "atu_20_judgment",
    "Judgement": "atu_20_judgment",
    "The Aeon": "atu_20_judgment",
    "The World": "atu_21_universe",
    "World": "atu_21_universe",
    "The Universe": "atu_21_universe",
    # Courts — Pentacles/Disks
    "King of Pentacles": "king_of_disks",
    "Queen of Pentacles": "queen_of_disks",
    "Knight of Pentacles": "prince_of_disks",
    "Page of Pentacles": "princess_of_disks",
    # Courts — Cups
    "King of Cups": "king_of_cups",
    "Queen of Cups": "queen_of_cups",
    "Knight of Cups": "prince_of_cups",
    "Page of Cups": "princess_of_cups",
    # Courts — Swords
    "King of Swords": "king_of_swords",
    "Queen of Swords": "queen_of_swords",
    "Knight of Swords": "prince_of_swords",
    "Page of Swords": "princess_of_swords",
    # Courts — Wands
    "King of Wands": "king_of_wands",
    "Queen of Wands": "queen_of_wands",
    "Knight of Wands": "prince_of_wands",
    "Page of Wands": "princess_of_wands",
}

RWS_PIP_RANK_TO_ID = {
    "Ace": "ace",
    "1": "ace",
    "2": "2",
    "Two": "2",
    "3": "3",
    "Three": "3",
    "4": "4",
    "Four": "4",
    "5": "5",
    "Five": "5",
    "6": "6",
    "Six": "6",
    "7": "7",
    "Seven": "7",
    "8": "8",
    "Eight": "8",
    "9": "9",
    "Nine": "9",
    "10": "10",
    "Ten": "10",
}

RWS_SUIT_TO_ID = {
    "Wands": "wands",
    "Cups": "cups",
    "Swords": "swords",
    "Pentacles": "disks",
    "Disks": "disks",
    "Coins": "disks",
}

for rank_name, rank_id in RWS_PIP_RANK_TO_ID.items():
    for suit_name, suit_id in RWS_SUIT_TO_ID.items():
        NAME_TO_ID[f"{rank_name} of {suit_name}"] = f"{rank_id}_{suit_id}"

# ── Posture tables ──────────────────────────────────────────
ELEMENT_POSTURES = {
    "Fire": "hot+dry outward pressure, will-led motion, and low yielding",
    "Water": "cold+moist inward cohesion, receptivity, and high adaptability",
    "Air": "hot+moist mobility, contact, and directional openness",
    "Earth": "cold+dry density, stillness, and firm contour",
}

PLANET_POSTURES = {
    "Saturn": "constraint, weight, and boundary",
    "Jupiter": "increase, breadth, and permission",
    "Mars": "cutting force, heat, and contest",
    "Sun": "centralizing radiance and visibility",
    "Venus": "joining, attraction, and smoothing",
    "Mercury": "exchange, adjustment, and quick passage",
    "Moon": "fluctuation, reception, and reflected motion",
}

SIGN_POSTURES = {
    "Aries": "initiating fire",
    "Taurus": "fixed earth",
    "Gemini": "dividing air",
    "Cancer": "protective water",
    "Leo": "expressive solar fire",
    "Virgo": "sorting earth",
    "Libra": "balancing air",
    "Scorpio": "fixed water",
    "Sagittarius": "ranging fire",
    "Capricorn": "structuring earth",
    "Aquarius": "fixed air",
    "Pisces": "dissolving water",
}

SEPHIRA_POSTURES = {
    "Kether": "root force before division",
    "Chokmah": "initial impulse and fecundating movement",
    "Binah": "form-giving pressure and realized commencement",
    "Chesed": "settling expansion and constructed order",
    "Geburah": "severity, restriction, and judgment",
    "Tiphareth": "central accomplishment and harmonizing pressure",
    "Netzach": "possible result held beyond immediate material grip",
    "Hod": "isolated success with limited continuation",
    "Yesod": "fundamental force and executive basis",
    "Malkuth": "culminated force fixed into manifestation",
}

WORLD_POSTURES = {
    "Atziluth": "the archetypal world of pure will",
    "Briah": "the creative world of formative water",
    "Yetzirah": "the formative world of air and image",
    "Assiah": "the material world of earth and action",
}

# Generic reversal note — appended to dignity_layer for any reversed card (78-card
# deck and, via miracle_unfold, the miracle deck). Single source of truth.
REVERSAL_NOTE = " The card is reversed, indicating the same energy expressed through its negative form: repression, immaturity, or an out-of-control variant."


# ── Helpers ─────────────────────────────────────────────────
def _qualities_phrase(qualities: list[str]) -> str:
    return "+".join(qualities)


def _capitalize_first(s: str) -> str:
    if not s:
        return s
    return s[0].upper() + s[1:]


def _attribution_phrase(attribution: dict, sentence_start: bool = False) -> str:
    atype = attribution.get("type", "")
    prefix_map = {
        "element": ("the elemental attribution", "The elemental attribution"),
        "zodiac_sign": ("the sign", "The sign"),
        "planet": ("the planet", "The planet"),
    }
    label = prefix_map.get(atype, (atype, atype.capitalize()))
    chosen = label[1] if sentence_start else label[0]
    return f"{chosen} {attribution['value']}"


def _append_reversal_note(s: str) -> str:
    return s + REVERSAL_NOTE


def _split_compound(compound: str) -> tuple[str, str]:
    parts = compound.split(" of ")
    if len(parts) == 2:
        return parts[0], parts[1]
    return compound, ""


# ── Card index ──────────────────────────────────────────────
def load_card_index() -> dict[str, Any]:
    cards: dict[str, Any] = {}
    for fname in ("atu.json", "pips.json", "courts.json"):
        path = DATA_DIR / fname
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                for entry in json.load(f):
                    cards[entry["id"]] = entry
    return cards


# ── Unfold: standard cards ──────────────────────────────────
def unfold_pip(book_t: dict, position_label: str, reversed_flag: bool) -> dict:
    element = book_t["element"]
    sephira = book_t["sephira"]
    world = book_t["world"]
    decan = book_t.get("decan")
    dignity = book_t.get("decan_dignity")

    if decan:
        decan_layer = (
            f"{decan['planet']} in {decan['sign']} places {PLANET_POSTURES.get(decan['planet'], 'planetary pressure')} "
            f"inside {SIGN_POSTURES.get(decan['sign'], decan['sign'])} across {decan.get('span_degrees', 'its decan')}."
        )
    else:
        decan_layer = "No decan is assigned here, so the root elemental force remains undivided at this layer."

    if dignity:
        dignity_layer = f"{dignity} modulates the decanic pressure before it reaches the spread position."
    else:
        dignity_layer = "No decanic dignity is present here, so modulation remains at the root elemental layer."
    if reversed_flag:
        dignity_layer = _append_reversal_note(dignity_layer)

    return {
        "element_layer": f"{element}'s {_qualities_phrase(book_t['primary_qualities'])} posture brings {ELEMENT_POSTURES[element]}.",
        "sephira_layer": f"{sephira} in {world} narrows the posture through {SEPHIRA_POSTURES.get(sephira, sephira)} in {WORLD_POSTURES.get(world, world)}.",
        "decan_layer": decan_layer,
        "dignity_layer": dignity_layer,
        "position_layer": f"Landing on '{position_label}', these layers describe how that position receives the pressure before any Phase 4 collapse.",
    }


def unfold_major(book_t: dict, position_label: str, reversed_flag: bool) -> dict:
    attribution = book_t["attribution"]
    path_between = " to ".join(book_t["path_between"])
    qualities = _qualities_phrase(book_t.get("primary_qualities") or [])
    element = book_t.get("element")
    posture = ELEMENT_POSTURES.get(element, f"{attribution['value']} as the active attribution")
    attribution_start = _attribution_phrase(attribution, sentence_start=True)
    dignity_layer = "No decanic dignity is assigned to this trump; modulation remains with the attribution and path."
    if reversed_flag:
        dignity_layer = _append_reversal_note(dignity_layer)
    return {
        "element_layer": f"{attribution_start} supplies {qualities} as the primary posture, carried as {posture}.",
        "sephira_layer": f"Path {book_t['path_on_tree']} links {path_between}, placing the posture along that Tree-of-Life passage.",
        "decan_layer": "No decan is assigned to this trump, so the zodiacal or planetary attribution remains the operative layer.",
        "dignity_layer": dignity_layer,
        "position_layer": f"Landing on '{position_label}', the path and attribution touch that spread position without deciding the later judgment.",
    }


def unfold_court(book_t: dict, position_label: str, reversed_flag: bool) -> dict:
    outer, inner = _split_compound(book_t["element_compound"])
    span = book_t.get("zodiacal_span")
    if span:
        decan_layer = f"Its celestial span runs from {span['start']} to {span['end']}, giving the figure a bounded zodiacal corridor."
    else:
        decan_layer = f"Its celestial quadrant is {book_t.get('celestial_quadrant', 'not specified')}, so the figure is placed around a pole rather than a decan."
    if book_t.get("rules_decans"):
        dignity_layer = f"It oversees {', '.join(book_t['rules_decans'])}; those ranges orient the figure without creating a decanic dignity."
    else:
        dignity_layer = "No ruled decans are listed for this figure, so its modulation remains with the outer and inner elements."
    if reversed_flag:
        dignity_layer = _append_reversal_note(dignity_layer)
    return {
        "element_layer": f"{book_t['element_compound']} sets {outer}'s outer posture through {inner}'s inner field, with {_qualities_phrase(book_t['primary_qualities'])} leading.",
        "sephira_layer": "Court figures do not occupy a numbered sephira here; rank element and suit element supply the structural pressure.",
        "decan_layer": decan_layer,
        "dignity_layer": dignity_layer,
        "position_layer": f"Landing on '{position_label}', the figure behaves as a posture or actor-field rather than a numbered pip force.",
    }


# ── Compound image ──────────────────────────────────────────
def compound_pip(book_t: dict, position_label: str) -> str:
    element = book_t["element"]
    sephira = book_t["sephira"]
    world = book_t["world"]
    decan = book_t.get("decan")
    if decan:
        planet = decan["planet"]
        sign = decan["sign"]
        return (
            f"The position '{position_label}' receives {element}'s {_qualities_phrase(book_t['primary_qualities'])} drive through {sephira} in {world}, "
            f"while {planet}-in-{sign} sets {PLANET_POSTURES.get(planet, 'planetary pressure')} inside {SIGN_POSTURES.get(sign, sign)}."
        )
    return (
        f"The position '{position_label}' receives the root of {element}'s {_qualities_phrase(book_t['primary_qualities'])} force through {sephira} in {world}, "
        "before decanic pressure divides it into a narrower scene."
    )


def compound_major(book_t: dict, position_label: str) -> str:
    attribution = book_t["attribution"]
    path = book_t["path_on_tree"]
    between = " to ".join(book_t["path_between"])
    attribution_mid = _attribution_phrase(attribution, sentence_start=False)
    return (
        f"The position '{position_label}' is touched by {attribution_mid} moving along path {path} from {between}, "
        f"so the scene holds {_qualities_phrase(book_t.get('primary_qualities') or [])} pressure on that axis."
    )


def compound_court(book_t: dict, position_label: str) -> str:
    outer, inner = _split_compound(book_t["element_compound"])
    span = book_t.get("zodiacal_span")
    location = f"from {span['start']} to {span['end']}" if span else book_t.get("celestial_quadrant", "its quadrant")
    return (
        f"The position '{position_label}' receives a figure of {outer} acting through {inner}, placed {location}; "
        "the scene is a moving posture carried by rank and suit rather than a numbered pip pressure."
    )


# ── Spread synthesis ────────────────────────────────────────
PILLARS = {
    "Kether": "Middle", "Tiphareth": "Middle", "Yesod": "Middle", "Malkuth": "Middle",
    "Chokmah": "Right", "Chesed": "Right", "Netzach": "Right",
    "Binah": "Left", "Geburah": "Left", "Hod": "Left",
}


def synthesize_spread(per_card: list[dict]) -> dict:
    quality_counts: Counter[str] = Counter()
    element_counts: Counter[str] = Counter()
    pillar_counts: Counter[str] = Counter()
    sephira_counts: Counter[str] = Counter()
    other_element_counts: Counter[str] = Counter()
    primary_cards = [card for card in per_card if not card.get("supplement", False)]
    supplements = [card for card in per_card if card.get("supplement", False)]

    # Main-spread working uses main draws. Supplements retain their full local
    # unfolding, but do not add cross-position elemental/sephirothic votes.
    for card in primary_cards:
        raw = card.get("raw_correspondences", {})
        if not raw:
            continue
        for q in raw.get("primary_qualities") or []:
            quality_counts[q] += 1
        elem = raw.get("element")
        # Court cards use element_compound; extract inner (suit) element
        if not elem and raw.get("element_compound"):
            compound = raw["element_compound"]
            if " of " in compound:
                elem = compound.split(" of ")[1]  # "Fire of Earth" → "Earth"
        # Only the four classical elements enter elemental balance; the Miracle deck's
        # Aether is intentionally excluded by this positive check.
        if elem and elem in {"Fire", "Water", "Air", "Earth"}:
            element_counts[elem] += 1
        elif elem:
            other_element_counts[elem] += 1
        seph = raw.get("sephira")
        if seph:
            # Miracle cards carry a sephira list (may be a 双主锚); standard cards a single string
            seph_list = seph if isinstance(seph, list) else [seph]
            for s in seph_list:
                sephira_counts[s] += 1
                if s in PILLARS:
                    pillar_counts[PILLARS[s]] += 1

    # Quality axes
    if not quality_counts:
        quality_axes = "No primary qualities are present."
    else:
        ordered = ", ".join(f"{q}({c})" for q, c in quality_counts.most_common())
        if len(quality_counts) >= 4:
            quality_axes = f"Quality field is mixed across {ordered}, so no single quality pair can close the spread by itself."
        else:
            dominant = ", ".join(q for q, _ in quality_counts.most_common(2))
            quality_axes = f"Dominant quality pressure is {dominant}, with the full count at {ordered}."

    # Elemental balance
    all_elems = {"Fire", "Water", "Air", "Earth"}
    if not element_counts:
        elemental_balance = "No elemental balance can be named."
    else:
        max_count = max(element_counts.values())
        dominant = sorted(e for e, c in element_counts.items() if c == max_count)
        missing = sorted(all_elems - set(element_counts))
        dom_text = " + ".join(dominant) if len(dominant) < 4 else "no single element"
        miss_text = " + ".join(missing) if missing else "none"
        elemental_balance = f"Main-card element counts — most represented: {dom_text}; not represented in this sample: {miss_text}."

    # Sephirothic pattern
    concentrated = [p for p, c in pillar_counts.items() if c >= 3]
    if concentrated:
        details = ", ".join(f"{s}({c})" for s, c in sephira_counts.most_common())
        sephirothic = f"{' and '.join(sorted(concentrated))} pillar concentration, with sephiroth touched as {details}."
    elif sephira_counts:
        details = ", ".join(f"{s}({c})" for s, c in sephira_counts.most_common())
        sephirothic = f"no concentration; sephiroth touched as {details}."
    else:
        sephirothic = "no concentration"

    return {
        "quality_axes": quality_axes,
        "elemental_balance": elemental_balance,
        "sephirothic_pattern": sephirothic,
        "counts": {
            "elements": dict(element_counts),
            "primary_qualities": dict(quality_counts),
            "sephiroth": dict(sephira_counts),
            "pillars": dict(pillar_counts),
            "other_elements": dict(other_element_counts),
            "primary_card_count": len(primary_cards),
            "supplement_card_count": len(supplements),
        },
        "participation": {
            "scope": "primary_cards_only",
            "working_positions": [card.get("position") for card in primary_cards],
            "supplement_positions": [card.get("position") for card in supplements],
            "element_count_basis": "One attributed classical element per main card; court inner/suit element. Aether is listed in other_elements.",
            "quality_count_basis": "Declared primary_qualities per main card; court outer/rank qualities. Supplements clarify their parent position locally.",
        },
        "explicit_unknowns": [
            "The concrete referent of each position remains outside Phase 3.",
            "Which pressure should govern the spread is not decided by the property layer alone.",
        ],
        "compound_scene": f"In the spread, {elemental_balance} {sephirothic} The image remains property-level material for Phase 4.",
    }


# ── Main ─────────────────────────────────────────────────────
def normalize_spread_input(data: Any) -> list[dict]:
    """Accept a card list or {spread, supplements}, without changing its draws.

    Supplements may be inline or in the documented top-level list. Resolve
    their parent explicitly so local clarification cannot become another
    main-card participant. Duplicate inputs are reported rather than dropped.
    """
    if isinstance(data, dict):
        cards = data.get("spread")
        extra = data.get("supplements", [])
    else:
        cards, extra = data, []
    if not isinstance(cards, list) or not isinstance(extra, list):
        raise ValueError("Expected a card list or an object with spread and optional supplements lists")

    entries = []
    for items, from_supplements in ((cards, False), (extra, True)):
        for original in items:
            if not isinstance(original, dict):
                raise ValueError("Each card entry must be an object")
            entry = deepcopy(original)
            if not isinstance(entry.get("card_name"), str) or not entry["card_name"].strip():
                raise ValueError("Each card entry needs a card_name")
            for flag in ("reversed", "supplement"):
                if flag in entry and not isinstance(entry[flag], bool):
                    raise ValueError(f"{flag} must be a JSON boolean for {entry['card_name']}")
            label = entry.get("position")
            if label is not None and not isinstance(label, str):
                raise ValueError("position must be a string")
            entry["supplement"] = bool(
                from_supplements or entry.get("supplement")
                or entry.get("for_position") is not None
                or entry.get("parent_position") is not None
                or (label and label.startswith("Supp:"))
            )
            entries.append(entry)

    main_positions: dict[str, dict] = {}
    numbered_positions: dict[str, list[str]] = {}

    def position_number(label: str) -> str | None:
        match = re.match(r"^Pos\s*(\d+)\b", label, re.IGNORECASE)
        return str(int(match.group(1))) if match else None

    for ordinal, entry in enumerate(entries, 1):
        if entry["supplement"]:
            continue
        position = entry.get("position") or f"position {entry.get('position_index', ordinal)}"
        if position in main_positions:
            raise ValueError(f"Duplicate primary position: {position}")
        entry["position"] = position
        entry["parent_position"] = None
        main_positions[position] = entry
        number = position_number(position)
        if number is not None:
            numbered_positions.setdefault(number, []).append(position)

    seen_supplements = set()
    for entry in entries:
        if not entry["supplement"]:
            continue
        parent = entry.get("parent_position") or entry.get("for_position")
        if parent is None and (entry.get("position") or "").startswith("Supp:"):
            parent = entry["position"][5:].strip()
        if not isinstance(parent, str) or not parent.strip():
            raise ValueError(f"Supplement {entry['card_name']} requires a parent_position or for_position")
        parent = parent.strip()
        if parent not in main_positions:
            matches = numbered_positions.get(position_number(parent), [])
            if len(matches) != 1:
                raise ValueError(f"Unknown or ambiguous supplement parent position: {parent}")
            parent = matches[0]
        identity = (parent, NAME_TO_ID.get(entry["card_name"], entry["card_name"]))
        if identity in seen_supplements:
            raise ValueError(f"Duplicate supplement for {parent}: {entry['card_name']}; reconcile with the original draw")
        seen_supplements.add(identity)
        entry["parent_position"] = parent
        entry["position"] = entry.get("position") or f"Supp: {parent}"
    return entries


def unfold_spread(spread_input: list[dict]) -> dict:
    """Unfold a full spread into Phase 3 property layers."""
    spread_input = normalize_spread_input(spread_input)
    card_index = load_card_index()
    miracle_postures = {"sephira": SEPHIRA_POSTURES, "planet": PLANET_POSTURES, "sign": SIGN_POSTURES}
    # Miracle deck data is loaded lazily — only when a miracle card is actually
    # encountered — so a corrupt/missing miracle.json never breaks a pure 78-card
    # spread. The "78 cards don't depend on the addon" boundary stays intact.
    miracle_data: dict | None = None
    per_card = []

    for entry in spread_input:
        card_name = entry.get("card_name", "")
        position = entry.get("position", f"position {entry.get('position_index', '?')}")
        reversed_flag = bool(entry.get("reversed", False))
        is_supplement = bool(entry.get("supplement", False))

        # Miracle card — unfolding is delegated to the miracle-anchor-addon skill
        if "Miracle" in card_name or "Miracles" in card_name:
            if miracle_unfold is None:
                raise ValueError(
                    f"Phase 3 cannot continue: miracle card {card_name!r} at {position}, "
                    f"but the miracle-anchor-addon skill (miracle_unfold.py) was not found"
                )
            if miracle_data is None:
                miracle_data = miracle_unfold.load_miracle_index()
            mcard = miracle_data.get("cards", {}).get(card_name)
            if not mcard:
                raise ValueError(
                    f"Phase 3 cannot continue: unknown miracle card {card_name!r} at {position} "
                    f"(not found in the addon's miracle.json)"
                )
            unfolding = miracle_unfold.unfold_miracle(
                mcard, position, reversed_flag, miracle_postures, REVERSAL_NOTE
            )
            compound = miracle_unfold.compound_miracle(mcard, position, miracle_postures)
            raw_corr = {
                "core_meaning": mcard.get("core_meaning", ""),
                "element": miracle_data.get("element", "Aether"),
                "sephira": mcard.get("sephira") or [],
                "planet": mcard.get("planet") or [],
                "zodiac": mcard.get("zodiac") or [],
                "source": "miracle-anchor-addon: project-authored core meanings and correspondences",
            }
            per_card.append({
                "card_name": card_name,
                "card_class": "miracle",
                "position": position,
                "reversed": reversed_flag,
                "supplement": is_supplement,
                "role": "supplement" if is_supplement else "primary",
                "parent_position": entry.get("parent_position"),
                "working_eligible": not is_supplement,
                "raw_correspondences": raw_corr,
                "property_unfolding": unfolding,
                "compound_image": compound,
            })
            continue

        # Standard card
        card_id = NAME_TO_ID.get(card_name)
        if not card_id:
            raise ValueError(f"Phase 3 cannot continue: unknown card {card_name!r} at {position}")

        entry_data = card_index.get(card_id)
        if not entry_data:
            raise ValueError(
                f"Phase 3 cannot continue: card ID {card_id!r} for {card_name!r} "
                f"was not found in {DATA_DIR} at {position}"
            )

        book_t = entry_data["book_t"]
        card_class = entry_data["card_class"]

        if card_class == "minor_pip":
            unfolding = unfold_pip(book_t, position, reversed_flag)
            compound = compound_pip(book_t, position)
        elif card_class == "major_arcana":
            unfolding = unfold_major(book_t, position, reversed_flag)
            compound = compound_major(book_t, position)
        elif card_class == "court":
            unfolding = unfold_court(book_t, position, reversed_flag)
            compound = compound_court(book_t, position)
        else:
            raise ValueError(
                f"Phase 3 cannot continue: unknown card_class {card_class!r} "
                f"for {card_name!r} at {position}"
            )

        per_card.append({
            "card_name": card_name,
            "card_id": card_id,
            "card_class": card_class,
            "position": position,
            "reversed": reversed_flag,
            "supplement": is_supplement,
            "role": "supplement" if is_supplement else "primary",
            "parent_position": entry.get("parent_position"),
            "working_eligible": not is_supplement,
            "raw_correspondences": deepcopy(book_t),
            "property_unfolding": unfolding,
            "compound_image": compound,
        })

    spread_synth = synthesize_spread(per_card)

    return {
        "per_card": per_card,
        "spread_synthesis": spread_synth,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in ("-", "--help", "-h"):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    try:
        spread = normalize_spread_input(data)
        result = unfold_spread(spread)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
    # 本脚本只产 Phase 3 属性【数据】，不是解读。把告示钉进输出 + stderr 横幅，
    _NOTICE = (
        "Phase 3 属性资料已展开。请调用 symbol-anchor-check skill，继续完成 "
        "Phase 3.5 元素关系与场域称重、Phase 4 via-negativa 收束及跨符号校验，"
        "随后生成 answer。"
    )
    print(json.dumps({"_notice": _NOTICE, **result}, ensure_ascii=False, indent=2))
    _bar = "=" * 72
    print(f"\n{_bar}", file=sys.stderr)
    print("  Phase 3 资料步骤完成；请 Skill-invoke symbol-anchor-check 继续解读流程。", file=sys.stderr)
    print("  下一步：元素关系与场域称重 → via negativa → 跨符号校验 → answer。", file=sys.stderr)
    print(_bar, file=sys.stderr)
