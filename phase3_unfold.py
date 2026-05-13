#!/usr/bin/env python3
"""
Phase 3 — Deterministic Property Layer Unfolding
Reimplements Claude Code's phase3_analyzer logic as a standalone Hermes module.
Reads Book T correspondence data (atu/pips/courts.json) and Miracle牌意.
Accepts a spread dict, outputs property_unfolding + compound_image + spread_synthesis.

Usage:
  python3 phase3_unfold.py < spread_input.json
  python3 phase3_unfold.py spread_input.json

Input format (matching spirit_draw_v2 output card names):
{
  "spread": [
    {"position": "Pos 1 [我的状态]", "card_name": "King of Miracles", "reversed": false},
    {"position": "Pos 2 [他的状态]", "card_name": "King of Pentacles", "reversed": true},
    ...
  ],
  "supplements": [
    {"for_position": "Pos 1 [我的状态]", "card_name": "Devil", "reversed": true},
    ...
  ]
}
"""

import json
import os
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

# ── Data paths ──────────────────────────────────────────────
DATA_DIR = Path(os.path.expanduser("~/.hermes/data/tarot"))
MIRACLE_REF = Path("/mnt/e/My Grimoire/My Grimoire/摘抄/占卜符号类/世界名画塔罗牌/f. 奇迹牌组 - 核心牌意提取.md")

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

# ── Miracle牌意（硬编码核心意，来源：奇迹牌组核心牌意提取.md） ──
MIRACLE_MEANINGS = {
    "King of Miracles": {
        "core": "空性再生 — 斩常见与断见的中道，在空性中持续生成新的存在形态",
        "upright": "放下对「我」的执着，空了但没有消失，持续再生",
        "reversed": "堕入常见（僵化自我设限）或断见（将空性误读为虚无）",
        "mechanism": "超越自我有限性，不再需要任何版本的边界",
    },
    "Queen of Miracles": {
        "core": "复活 — 经历了象征性死亡后以崭新形态重新存在",
        "upright": "阴性力量的复辟，温柔的、自上而下的感召",
        "reversed": "复活未能完成，仍困在旧形态中",
        "mechanism": "审判之后的状态——死亡天使不是在审判，是在温柔接引",
    },
    "Knight of Miracles": {
        "core": "阴影整合 — 阴影显现、叛逆、对权威的质疑",
        "upright": "路西法的坠落——痛苦但必要的分离，阴影已成为你的一部分后的重生",
        "reversed": "拒绝与阴影整合，方向迷失，与潜意识隔离",
        "mechanism": "承认光暗一体后的重生过程",
    },
    "Page of Miracles": {
        "core": "跨越边界 — 站在边界上，即将跨越",
        "upright": "痛苦但不可逆的转变正在发生，站在门槛上的恐惧",
        "reversed": "已经被推过去之后的剧变体验——旧自我毁灭，灵性指引，共时性的暗示",
        "mechanism": "跨越本身没有正负之分",
    },
    "Ace of Miracles": {
        "core": "重置 — 旧循环走到终点，归零后的重新开始",
        "upright": "一切推倒重来的起点，转化本身的种子",
        "reversed": "拒绝承认旧循环已结束，或归零后无法启动",
        "mechanism": "一切人格变化的前提：先承认旧的已经走到尽头",
    },
    "2 of Miracles": {
        "core": "着魔 — 被某种力量/观念/情感完全占据",
        "upright": "丧失对自身原有身份的觉知，不由自主",
        "reversed": "从着魔中醒来，个体意志回归",
        "mechanism": "人格结构被外力接管",
    },
    "3 of Miracles": {
        "core": "直面阴影 / 净化仪式",
        "upright": "被迫面对黑暗面 + 经由仪式性净化清除负面能量",
        "reversed": "拒绝直面，蒙住眼睛；压抑带来的不是安全而是更深焦虑",
        "mechanism": "心理层（你面对阴影）+ 仪式层（某种力量在对你施加净化）",
    },
    "4 of Miracles": {
        "core": "人格放大 — 承接超越自身的力量或认知",
        "upright": "人格向更大维度扩展，存在本身被撑大",
        "reversed": "放大失控，承接了超出自己容量的东西",
        "mechanism": "外来伟大内容进入人格并被吸收",
    },
    "5 of Miracles": {
        "core": "英雄认同 — 经由崇拜唤醒潜能",
        "upright": "被他者的伟大所感召而发生内在转变",
        "reversed": "认同变成盲从，过度控制、刻意模仿，反而压抑自身本能",
        "mechanism": "力量与勇气的来源不是自生的，而是经由崇拜被唤醒的",
    },
    "6 of Miracles": {
        "core": "团体认同 — 在集体场域中的人格变化",
        "upright": "从团体中获得支持、勇气和归属感",
        "reversed": "团体心理的退行——群体恐慌、盲从、个体意识被集体情绪淹没",
        "mechanism": "你在团体中变成了一个不同的人",
    },
    "7 of Miracles": {
        "core": "人格缩小 — 内在坍缩，行动力丧失",
        "upright": "被打击到缩成一团，一个本来强大的存在失去了行动的勇气",
        "reversed": "被压制的潜能仍在，坚定的守护仍在，只是尚未被看见",
        "mechanism": "「我」本身变小了",
    },
    "8 of Miracles": {
        "core": "技术超越 — 通过技艺精进实现层次跃升",
        "upright": "代达罗斯成功了——技术本身是有效的",
        "reversed": "伊卡洛斯坠落——技术力量在自我整合尚未完成时失控",
        "mechanism": "通过技术/技艺/学术的精进实现人格层次跃升",
    },
    "9 of Miracles": {
        "core": "神圣遭遇 — 遭遇超越日常认知框架的神秘体验",
        "upright": "认知结构被根本性地震动，存在本身被触碰了",
        "reversed": "被神圣感的恐惧吞没，无法整合体验；或偏执的迷信/全面拒斥",
        "mechanism": "遭遇了超越日常认知框架的神秘体验",
    },
    "10 of Miracles": {
        "core": "「我」的边界位移",
        "upright": "意识到「我」比「我以为的我」更大——不是发现了新东西，而是发现边界比以为的远",
        "reversed": "把门关上了——封闭、自我隔离、拒绝承认内在还有更大的存在",
        "mechanism": "不是高我，不是外部存在——全部都是你，只是边界移动了",
    },
}


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
    return s + " The card is reversed, indicating the same energy expressed through its negative form: repression, immaturity, or an out-of-control variant."


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


def unfold_miracle(card_name: str, position_label: str, reversed_flag: bool) -> dict:
    """Unfold a Miracle card using the hardcoded meanings."""
    info = MIRACLE_MEANINGS.get(card_name, {})
    if not info:
        return {"error": f"Unknown miracle card: {card_name}"}

    direction = "reversed" if reversed_flag else "upright"
    direction_text = info.get(direction, info.get("core", ""))

    return {
        "miracle_core": info.get("core", ""),
        "miracle_mechanism": info.get("mechanism", ""),
        "miracle_direction": f"{'逆位' if reversed_flag else '正位'}: {direction_text}",
        "position_layer": f"Landing on '{position_label}', this Miracle card marks a personality-structure transformation at play in this position.",
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


def compound_miracle(card_name: str, position_label: str, reversed_flag: bool) -> str:
    info = MIRACLE_MEANINGS.get(card_name, {})
    direction = "逆位" if reversed_flag else "正位"
    core = info.get("core", "")
    return f"The position '{position_label}' carries {card_name} {direction} — {core}."


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

    for card in per_card:
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
        if elem:
            element_counts[elem] += 1
        seph = raw.get("sephira")
        if seph:
            sephira_counts[seph] += 1
            if seph in PILLARS:
                pillar_counts[PILLARS[seph]] += 1

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
        elemental_balance = f"Dominant: {dom_text}; missing: {miss_text}."

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
        "explicit_unknowns": [
            "The concrete referent of each position remains outside Phase 3.",
            "Which pressure should govern the spread is not decided by the property layer alone.",
        ],
        "compound_scene": f"In the spread, {elemental_balance} {sephirothic} The image remains property-level material for Phase 4.",
    }


# ── Main ─────────────────────────────────────────────────────
def unfold_spread(spread_input: list[dict]) -> dict:
    """Unfold a full spread into Phase 3 property layers."""
    card_index = load_card_index()
    per_card = []

    for entry in spread_input:
        card_name = entry.get("card_name", "")
        position = entry.get("position", f"position {entry.get('position_index', '?')}")
        reversed_flag = bool(entry.get("reversed", False))
        is_supplement = bool(entry.get("supplement", False))

        # Check if Miracle card
        if "Miracle" in card_name or "Miracles" in card_name:
            unfolding = unfold_miracle(card_name, position, reversed_flag)
            if "error" in unfolding:
                raise ValueError(f"Phase 3 cannot continue: {unfolding['error']} at {position}")
            compound = compound_miracle(card_name, position, reversed_flag)
            per_card.append({
                "card_name": card_name,
                "card_class": "miracle",
                "position": position,
                "reversed": reversed_flag,
                "supplement": is_supplement,
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

    spread = data.get("spread", data)
    try:
        result = unfold_spread(spread)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))
