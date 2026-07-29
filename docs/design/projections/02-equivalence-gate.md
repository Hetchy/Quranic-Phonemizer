# 02 - The equivalence gate

Status: **proposed**. The acceptance criterion for [01-design](01-design.md).

## 1. The rule

Every fact the legacy projections published must either

- have a **1-1 mapping** into `Reading` proving equivalence, or
- have an **adapter** proving equivalence, where the adapter is a pure function
  of `Reading` alone (a rule rename, a trigger split, an edge-kind read).

Two exemptions, both stated up front:

- **Phoneme corrections from PR #39.** Where the branch deliberately produces a
  different sound than `main`, the difference is a fix and is out of scope. The
  gate compares *structure and labels*, not tokens, wherever a token changed;
  the token diff is already covered by `out/phonemized_v*` regression.
- **Additive facts.** Rules, relationships and fields that `Reading` exposes and
  legacy did not (`IZHAR_*`, `IWAD`, `advice`, `owner`, `merged_from`,
  `effect`, `phase`, `attests`) are not gated. Nothing has to consume them.

Anything else is a regression.

## 2. Mechanism

`tools/projection_parity.py`. For every verse of the corpus, at each of the
three waqf levels the manual regression corpus already uses
(`out/phonemized_v*`: `v`, `vqm`, `vqsjm`):

1. Build the legacy projections from `main` (a pinned checkout or an installed
   pre-refactor wheel).
2. Build `Reading` from the branch at the same ref and boundary policy.
3. Run the adapters below.
4. Assert field-by-field equality; write every mismatch to a residue report
   grouped by cause, not by verse.

The report is the deliverable, not a pass/fail. A gate that says "1,412
mismatches" is useless; one that says "1,398 of them are `vowel_silent` on a
taa marbuta at waqf" closes an item.

## 3. Adapters, one per legacy projection

### 3.1 `silent_flags()` -> `[(char, silent, mark)]`

The tightest of the four and the right one to do first: it is one tuple per
written grapheme in reading order, and `qua_shared` has proven it 1-1 against a
real shard.

```
for glyph in reading.glyphs where glyph.cls != structural:
    char   = glyph.char
    silent = all(reading.units[u].sounds == () for u in glyph.units)
    mark   = the char of an adjacent silence_sign glyph on the same units, or ""
```

Three known divergences to confirm rather than assume:

- **Tokenization.** Legacy splits only the dagger alef, mini-waw and mini-yaa
  into their own entries; every other combining mark merges onto the grapheme
  before it. `Reading.glyphs` is one entry per grapheme. The adapter must
  re-merge, and the merge rule must be shown to be the same one.
- **Carrier waw** (`صَلَوٰة`, `زَكَوٰة`). Legacy special-cases a waw that is a silent
  seat for a dagger-alef madd. In `Reading` this should fall out of
  `glyph.units` and `unit.sounds` with no special case. If it does not, that is
  a modelling finding, not an adapter one.
- **Silah at waqf.** Legacy marks the mini-waw/yaa silent when the word stops.
  In `Reading` the unit has `conditional = true` and `sounds = ()`. Should be
  exact.

### 3.2 `tajweed_mappings()` -> `{char, source_rules[], target_rules[]}`

```
for each legacy entry, find its glyph; for each unit of that glyph:
    for each RuleHit naming the unit:
        source_rules  += rule if hit.at is this unit
        target_rules  += rule if this unit is in hit.context
    then apply the vocabulary adapter (00-audit §5)
```

The `is_source` bit maps onto `at` vs `context`, which is why C1 (labelling
`Participants`) is a prerequisite and not a nicety. Expected residue, all of
which should be *extra* rules on the new side:

- `IZHAR_*` and `LAM_QAMARIYYAH` on letters legacy left bare.
- `TAFKHEEM` reaching sounds legacy reached only through
  `HEAVY_VOWEL_PHONEMES = {"aˤ:"}`, a phoneme-shape test.
- Madd rules on units where legacy's `MADD_TYPE_MAP` collapsed `iwad` into
  `MADD_TABII`.

### 3.3 `letter_phoneme_mappings()` -> `[(chars, phonemes)]`

The loosest, because legacy's entry boundaries are the *output* of five merge
tables. Reconstruct them from `Reading`:

```
start from units in order; a unit with sounds == () merges into
  - the next unit, when its silencing rule is one of
    {wasl_elision, lam_shamsiyyah, iltiqa_repair}
  - the unit hosting the sound it merged into, when the edge is a merge
  - otherwise the previous unit
chars    = concatenation of the merged units' glyphs
phonemes = the merged units' sounds, in order
```

The gate here is not row-for-row identity -- it is that the *derived* merge
direction agrees with legacy's table lookup on every letter. Where it does not,
one of the two is wrong about the domain and the disagreement is the finding.

Two known re-attributions legacy performs after the fact and `Reading` does not
need, because the unit already holds the answer: iltiqa demotion of a shortened
long vowel onto the preceding consonant, and waqf-tanween redistribution of the
long vowel onto the otiose alif. Both must be shown to land on the same glyph.

### 3.4 `character_phoneme_mappings()` -> cells

The largest, and the one where "1-1" is the wrong ambition -- the cell schema
carries presentation state that `Reading` deliberately does not. Per field:

| Cell field | From `Reading` | Kind |
|---|---|---|
| `chars` | `unit.glyphs`, or the glyph's `char` | 1-1 |
| `role` | `glyph.cls`, folded 11 -> 4 | 1-1, lossy in the safe direction |
| `status` | derived, 01-design §2 | adapter |
| `phonemes` | `unit.sounds` -> `phoneme.token` | 1-1 |
| `phoneme_indices` | `unit.sounds`, rebased word-local | 1-1 |
| `tag` | the highest-priority `RuleHit` on the unit | adapter, keeps legacy's priority order |
| `secondary_tags` | the rest of them | adapter |
| `phoneme_rule_tags` | `phoneme.rules` per sound | 1-1 |
| `share_group` | units sharing a `phoneme.id` | adapter |
| `source_letter_index` | `glyph.index` | 1-1 |
| `source_letter_indices` | `glyph.units` -> their glyphs | 1-1 |

The cases to check by name, because each is one of the seven synthesized tags or
two surgeries from 00-audit §2.1: the hamza-wasl helping vowel (all three
qualities), the 3:1 iltiqa fatha, the Allah dagger alef, the madd-iwad alif at
waqf, the dropped silah at waqf, taa marbuta at waqf, the iqlab noon and its
small meem, and every muqattaat opening.

## 4. Residue that closes a finding

Three of the audit's findings are answered by running the gate, not by
reasoning:

- **F9 -- `vowel_silent`.** Enumerate, over the whole corpus, which `Rule`
  appears on the `Silent` attribution of every unit legacy tagged
  `vowel_silent`. If the set is small and named, the catch-all is retired and
  the frontend tooltip splits. If any unit has no rule, the model has a silent
  hole and that is a correctness bug, not a projection one.
- **F10 -- the iqlab small meem.** Does any `Glyph` with `char == "ۢ"` have
  a non-empty `units`? One query.
- **F6 -- `write` totality.** ADR-005 §4's trigger set, asserted as
  `unit.glyphs != ""` over the whole corpus at all three waqf levels. This is
  the phase-2 gate that ADR-005 says must pass before "no fourth layer" is a
  decision rather than a hypothesis.

## 5. Order of work

1. Resolve [03](../03-canonical-vocabulary.md). It blocks the `Unit` shape.
2. **C1** -- label `Participants`. Mechanical, 21 sites, no behaviour change.
3. **C2** -- keep the modifier edge. Small, and F1/F3 do not close without it.
4. Build `Reading` over a single verse with a hand-written composition, and
   check it against `tests/test_anchored_projection.py`'s six verses.
5. **C3** -- the composition root and a real boundary policy.
6. `tools/projection_parity.py`, `silent_flags` adapter first.
7. The other three adapters, largest last.
8. Bump `out/phonemized_v{N+1}` and write the `changes.txt` entry.

Steps 1-4 are design closure. 5 onward is the gate.
