#!/usr/bin/env python3
"""Miracle deck — Phase 3 unfolding module.

Shipped by the miracle-anchor-addon skill. anchor-check's phase3_unfold.py imports
this module if present, so the 本体 script carries NO miracle-specific code or data.

Miracle cards unfold into the SAME 5 property layers as the 78-card deck. The posture
vocabulary (SEPHIRA/PLANET/SIGN postures) and the generic reversal note are owned by
the 本体 and passed in by the caller — this module never duplicates 本体 constants.

正逆位 is not a looked-up meaning: the reversed variant is derived in Phase 4 by
reasoning from the sephira/property layers, exactly as for the 78-card deck.

Data source: miracle.json (sibling file) — core meaning + 主锚 sephira/planet/zodiac.
"""

import json
from pathlib import Path
from typing import Any

MIRACLE_DATA_PATH = Path(__file__).resolve().parent / "miracle.json"


def load_miracle_index() -> dict[str, Any]:
    """Load miracle.json (deck element + per-card core meaning + 主锚)."""
    if not MIRACLE_DATA_PATH.exists():
        return {}
    with MIRACLE_DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def unfold_miracle(
    mcard: dict,
    position_label: str,
    reversed_flag: bool,
    postures: dict,
    reversal_note: str,
) -> dict:
    """Unfold a Miracle card into the same 5 property layers as the 78-card deck.

    postures: {"sephira": SEPHIRA_POSTURES, "planet": PLANET_POSTURES, "sign": SIGN_POSTURES}
              — the 本体's posture-vocabulary lookups, injected by the caller.
    reversal_note: the 本体's generic reversal-note string (same one the 78-card deck
                   appends to dignity_layer when a card is reversed).
    """
    sp = postures["sephira"]
    pp = postures["planet"]
    zp = postures["sign"]

    sephira = mcard.get("sephira") or []
    planet = mcard.get("planet") or []
    zodiac = mcard.get("zodiac") or []

    seph_phrase = " and ".join(sephira) if sephira else "no numbered sephira"
    seph_postures = "; ".join(sp.get(s, s) for s in sephira) or "—"
    planet_phrase = " and ".join(planet) if planet else "no planet"
    planet_postures = "; ".join(pp.get(p, "planetary pressure") for p in planet) or "—"
    zodiac_phrase = " and ".join(zodiac) if zodiac else "no sign"
    zodiac_postures = "; ".join(zp.get(z, z) for z in zodiac) or "—"

    dignity_layer = "No decanic dignity applies; modulation rests with the sephira, planet, and sign attributions."
    if reversed_flag:
        dignity_layer = dignity_layer + reversal_note

    return {
        "element_layer": (
            "The deck-level element is Aether, the fifth element: spirit or psyche itself, "
            "outside the four elemental qualities. It carries transformation of the personality "
            "structure rather than fire/water/air/earth pressure."
        ),
        "sephira_layer": f"The sephira attribution is {seph_phrase}, narrowing the posture through {seph_postures}.",
        "decan_layer": (
            f"No decan structure applies; the operative layer is the planet {planet_phrase} and "
            f"the sign {zodiac_phrase} — {planet_postures}, within {zodiac_postures}."
        ),
        "dignity_layer": dignity_layer,
        "position_layer": (
            f"Landing on '{position_label}', the sephira, planet, and sign attributions touch "
            "that spread position without deciding the later judgment."
        ),
    }


def compound_miracle(mcard: dict, position_label: str, postures: dict) -> str:
    """Build the compound_image for a Miracle card — posture-forward, parallel to compound_pip."""
    sp = postures["sephira"]
    pp = postures["planet"]
    zp = postures["sign"]

    sephira = mcard.get("sephira") or []
    planet = mcard.get("planet") or []
    zodiac = mcard.get("zodiac") or []

    seph_postures = "; ".join(sp.get(s, s) for s in sephira) or "no numbered sephira"
    planet_postures = "; ".join(pp.get(p, "planetary pressure") for p in planet) or "no planet"
    zodiac_postures = "; ".join(zp.get(z, z) for z in zodiac) or "no sign"
    return (
        f"The position '{position_label}' carries an Aether-level transformation: the posture is "
        f"narrowed through {seph_postures}, with {planet_postures} acting within {zodiac_postures}."
    )
