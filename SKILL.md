---
name: symbol-anchor-check-v4
description: "Divination Anchor Check v4.0 — Phase 3 deterministic property unfolding + Phase 4 via negativa convergence. Runs phase3_unfold.py to extract Book T property layers, then uses elimination to narrow the field. I Ching / astro dice / word cards integrated in Phase 4 cross-symbol verification. Inherits v3.4 R1/R2 prose rules as post-check."
tags: [divination, interpretation, quality-control, tarot, book-t, via-negativa, phase3, phase4]
---

# Divination Anchor Check v4.0

**Core change from v3.x**: v3.x was prose-style rules laid on loose ground. v4.0 runs a deterministic property layer (Phase 3) first, then constrains LLM interpretation to that property material via negativa convergence (Phase 4). Prose rules (R1/R2) are retained as post-checks after Phase 4 output.

## Trigger

Triggered when the user asks follow-up questions or requests interpretation of an already-output divination spread result.

## Pipeline Overview

```
Spread output (6 cards + supplement + astro dice + I Ching + word cards)
        │
        ▼
Phase 3 ── python3 phase3_unfold.py  ← deterministic, no LLM
        │  Each tarot card → 5-layer property unfolding + compound_image
        │  Miracle cards → core meaning + transformation mechanism
        │  spread_synthesis → quality axes + elemental balance + sephirothic pattern
        │
        ▼
Phase 4 ── LLM via negativa convergence
        │  1. Elimination: rule out unsupported candidates, citing Phase 3 text as evidence
        │  2. narrowed_field: pure property language (no card/planet/sephira/sign names)
        │  3. Cross-symbol verification: I Ching + dice + word cards
        │  4. answer: describe the scene, not the cards
        │  5. open_threads: honestly preserve uncovered items
        │
        ▼
Post-check ─── R1/R2 prose rules (inherited from v3.4)
```

---

## Phase 3 — Execution

### Command

```bash
python3 phase3_unfold.py <input.json>
```

### Input Format

Construct from the spread output. Place card names (RWS format) and positions:

```json
{
  "spread": [
    {"position": "Pos 1 [My State]", "card_name": "King of Miracles", "reversed": false},
    {"position": "Pos 2 [Their State]", "card_name": "King of Pentacles", "reversed": true},
    ...
    {"position": "Supp: Pos 1", "card_name": "Devil", "reversed": true, "supplement": true}
  ]
}
```

### Output Structure

Standard cards:
```json
{
  "card_name": "Death",
  "card_id": "atu_13_death",
  "card_class": "major_arcana",
  "position": "Pos 6 [What They Want to Say]",
  "reversed": true,
  "property_unfolding": {
    "element_layer": "The sign Scorpio supplies cold+moist as the primary posture...",
    "sephira_layer": "Path 24 links Tiphareth to Netzach...",
    "decan_layer": "No decan is assigned to this trump...",
    "dignity_layer": "...The card is reversed...",
    "position_layer": "Landing on 'Pos 6 [What They Want to Say]'..."
  },
  "compound_image": "The position 'Pos 6 [What They Want to Say]' is touched by the sign Scorpio..."
}
```

Miracle cards:
```json
{
  "card_name": "King of Miracles",
  "card_class": "miracle",
  "property_unfolding": {
    "miracle_core": "Empty-regeneration — the middle way cutting through eternalism and nihilism...",
    "miracle_mechanism": "Transcending the limits of self...",
    "miracle_direction": "Upright: release attachment to 'I'...",
    "position_layer": "..."
  },
  "compound_image": "..."
}
```

---

## Phase 4 — Via Negativa Convergence

### Methodology

**The event is the model; the cards are its projection.** Phase 3 has already unfolded the cards into property language (element / sephira / decan / dignity / position / compound image / cross-checks). Phase 4's job is to operate on this property material, not recall canned card meanings.

### Step 1: Elimination

For each unknown item (see fixed unknowns below), working from Phase 3 property material, **eliminate at least one candidate answer that the material does not support**.

**Candidates must be structural candidates** ("a smooth, low-friction reception" / "a passive, indifferent response"), not card-meaning negations ("not a conflict card" / "not a card representing love").

**Each elimination must carry evidence**, quoting **exact substrings** from Phase 3 output. Format:

```
Eliminate: [candidate description]
Evidence:
  - card: Death, layer: element_layer, quote: "cold+moist as the primary posture"
  - card: Death, layer: sephira_layer, quote: "links Tiphareth to Netzach"
```

### Reversed Card Elimination Ban (R0)

A reversed card does NOT negate its upright property. Phase 3's dignity_layer already states that a reversed card means "the same energy expressed through its negative form: repression, immaturity, or an out-of-control variant" — same energy, different expression, not energy vanishing.

In the elimination step, **it is forbidden to eliminate a structural candidate supported by the upright property solely because "the card is reversed."**

| Upright | Reversed Does NOT Mean |
|---------|----------------------|
| 9 of Wands: tense vigilance, steady force under tension | strength gone, no vigilance |
| Queen: outward care/nurturing | no care, nurturing vanished |
| Magician: skill/will/channel flowing | no skill, will absent |
| World: completion, cycle closed | nothing was completed |

Correct elimination for reversed cards: retain the upright property base (strength/care/flow/completion), **eliminate the candidate where "the property operates in a full, outward, frictionless manner."** A reversed card turns the same property inward, holds it back, or routes it through a less visible path — but the property itself did not evaporate.

### Fixed Unknowns

A 6-position spirit communication spread maps to the following unknowns:

1. **Their state** (Pos 2): what are they doing / what energy state
2. **Their attitude** (Pos 4): what posture toward the current context
3. **Reason for attitude** (Pos 5): why this attitude
4. **What they want to say** (Pos 6): what they wish to convey
5. **Current context** (Pos 3): what is happening between the two parties (supplement card can lock this)
6. **My state (from their view)** (Pos 1): how they see your current state

### Step 2: narrowed_field

After elimination, describe the narrowed field using **pure property language**. 1–3 sentences.

**Allowed vocabulary**: posture, pressure, direction, weight, motion, receptivity, constraint, openness, cohesion, contour, propulsion, stillness, contraction, expansion, transmission, holding, boundary.

**Forbidden**:
- Card names, suits, numbers, major/minor arcana labels
- Planet names, zodiac sign names, sephira names, path names, world names
- "means", "represents", "symbolizes", "traditionally", "Book T says"
- Any form of "this card is..."

### Step 3: Cross-Symbol Verification

Cross-validate the tarot narrowed_field against the other three symbol systems:

**I Ching** (base hexagram + changing line + resultant hexagram):
- Base hexagram core image → same direction / opposite / tension with narrowed_field?
- Changing line text's action → what does it supplement?
- Resultant hexagram direction → what state does it ultimately land on?

**Astro Dice** (planet + sign + house + flying stars):
- Planetary nature → what force lies beneath
- Sign quality → what mode
- House domain → what field
- Flying stars → flow between which two domains

**Word Cards** (three cards):
- Content of each word card + landing point (which position/subject/action in the scene)
- Must explicitly quote word card content and assign landing points

Cross-symbol verification results go into a short paragraph (2–4 sentences) after narrowed_field, noting **multi-source alignment / tension / supplementation**.

### Step 4: answer

2–6 sentences. Describe the scene, not the cards. Use natural language matching the question's language.

**Forbidden**: card names, suits, planets, signs, sephiroth, paths. Forbid "this card says" / "the tarot shows". Speak human.

### Step 5: open_threads

Honestly list unknown items that Phase 4 could not fully cover. Uncertainty is uncertainty — preserving gaps is better than fabricating.

---

## Post-Check: R1/R2 Prose Rules (inherited from v3.4)

Run on answer and narrowed_field after writing:

### R1: Referent Rule

- Forbid abstract property nouns as agentive subjects (e.g., "moisture brings", "stillness causes")
- Forbid element personification
- Every sentence must pass the **naive listener test** — someone who doesn't know the spread can understand who is doing what
- Use position-semantic roles for reference ("the one at her position", "the card beneath his attitude")

### R2: Implicit Cross-Position

- Extending from one position to a related position requires property-layer support from that related position

### Forbidden Patterns

- "not X but rather Y" construction
- "both X and Y" construction  
- 3+ consecutive purely parallel sentences without logical connectors
- "this means", "represents", "symbolizes"

---

## Output Template

```markdown
## Phase 3 — Property Layers

[per_card table: Position | Card | Element Layer | Sephira/Path Layer | Decan Layer | Dignity Layer]
[spread_synthesis: quality axes + elemental balance + sephirothic pattern]

## Phase 4 — Via Negativa

### Elimination
- Eliminate: [candidate] — Evidence: card X, layer Y, quote "..."

### narrowed_field
[pure property language, 1–3 sentences]

### Cross-Symbol Verification
[I Ching + dice + word cards cross-check]

### answer
[describe the scene, not the cards]

### open_threads
[uncovered unknown items]
```

---

## Phase 3 Data Sources

- Standard 78 cards: `data/tarot/{atu,pips,courts}.json` (read-only reference)
- Miracle 14 cards: hardcoded in `phase3_unfold.py` (source: miracle cards core meaning reference file)
- I Ching: `data/yijing/`
- Word cards: spread draw script output
- Astro dice: spread draw script output

## Forbidden

- Skip Phase 3 property layers and jump directly to interpretation
- Do card-meaning negation in elimination ("not a conflict card")
- Card names / planet / sign / sephira / path names in narrowed_field or answer
- Fabricate or invent properties not present in Phase 3
- Use bullet lists in place of prose paragraphs (answer must be prose)
- Use "not X but rather Y" construction in answer
