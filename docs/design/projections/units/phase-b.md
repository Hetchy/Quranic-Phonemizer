# Phase B - inscription

Two units, lane 2. B1 runs alongside A1 through A3 and lands before A3, because
both rework `model/inscription.py`. B2 waits for A4 and B1.

---

## B1 - Inscription hygiene

**Items 16, 17, 18, 19, 20, 21, 22. Large.**

Seven defects, each located:

- **16, marks that reach no unit.** The largest group is the alif seating a
  fathatan, skipped by `canon/build.py` `_skip_iwad_carrier`, although it sounds
  at a pause and every iwad case needs it. Then the superscript alif over a
  written carrier, the sakt mark, the combining hamza above, the rectangular
  zero.
- **17, the separator between words is a glyph.** `orthography/cluster.py`
  `begin_word` advances the offset for the inter-word space and emits no
  `Grapheme`, while a space inside a word's own text is emitted. The
  concatenation law of `02-gate` section 4.2 therefore passes only on a
  single-word verse.
- **18, one scalar one glyph.** `ٱ` carries both a letter and an onset, so the
  cluster emits two evidences at one offset and `canon/build.py` then records
  the onset again. A tatweel gets a `Decorates` from the cluster and a second
  from the scribe.
- **19, one notion of structural, and it is the edge.** The class and the edge
  disagree in both directions: a tatweel is classed structural and carries a
  `Decorates` edge, a stop sign is classed as advice and carries the
  `Structural` edge. Both move to the edge. A `stop_sign` keeps its own kind and
  takes no pairing; a tatweel takes none either.
- **20, the dagger and its carrier are reversed.**
- **21, `length_carrier` is a class nothing assigns.** No scalar in either
  script yaml classifies as one. The recited spelling is where a length carrier
  is added.
- **22, sakt is a word fact evidenced by nothing.** `SlotFact.SAKT` is set on a
  draft and lifted onto the word, and no scalar declares it.

**Files:**

- `orthography/cluster.py` - **load-bearing**, 264 lines
- `orthography/inventory.py` - **load-bearing**, 351 lines, `_load_structural`,
  `_load_decorates`, `LetterEntry`
- `model/inscription.py` - `GraphemeClass`, `Structural`, `SlotFact`
- both script yamls - **load-bearing**
- `canon/scribe.py` (`finish`, `_decorations`), `canon/build.py` (`_not_a_slot`,
  `_slot_draft`, `_skip_iwad_carrier`; **369 lines, watch the 400-line cap**),
  `canon/draft.py`
- `canon/derive/tanween.py` `iwad_carrier`, `canon/derive/length.py` `dagger`
- `render/anchored.py` `_writers`, `tools/l1_harness.py`
- `tests/laws/test_anchored_projection.py`,
  `tests/schema/test_inventory_contract.py`,
  `tests/laws/test_build_contract.py`

**Depends on** nothing logically; land it before A3. **Moves** the `l1`
provenance split and the `Decorates` count, which `l1_harness` reports beside
the residue, so the `l1` ceiling may move and must be accounted for.
`attestation` and `roundtrip` must hold. Watch `structure` for the line caps.

## B2 - `Supplies.fact` distinguishes quality from length

**Item 6, and item 22's other half. Medium: 61 `SlotFact` references across 16
files, 22 of them `NUCLEUS`.**

Without the split a haraka and its carrier make identical claims and ownership
cannot be evaluated, which is what `01-contract` section 6.1's ownership order
rests on.

**Read [decisions.md](decisions.md) section 3 before starting.** This is the
unit that states the tanween mark's spelling edges once and for all: it supplies
`letter` and the vowel facts for the noon it writes, and no `consonant` fact.
`01-contract` section 4.2's "a unit no glyph writes" is corrected here.

**Files:**

- `model/inscription.py` `SlotFact` - **load-bearing.** `NUCLEUS` splits into
  `vowel_quality`, `vowel_length` and `vowel_absence`; `tajweed_mark` arrives;
  `SAKT` leaves with B1.
- `orthography/inventory.py` `_fact_value`, `_load_evidences` - **load-bearing**
- `canon/draft.py` `fact_of`, `set_fact` - **load-bearing**, 10 hits in 82 lines
- `canon/derive/length.py` (11 hits), `derive/silah.py`, `derive/tanween.py`,
  `derive/wasl.py`, `canon/build.py`, `canon/scribe.py`, `canon/ledger.py`,
  `canon/passes.py`, `canon/spell.py`
- `render/anchored.py` `_FACT_OF_ASPECT` - the ownership order is built directly
  on this split
- both script yamls (every `fact: NUCLEUS` row)
- `tests/schema/test_ledger.py` (16 rejection cases, the strictest loader test
  in the suite), `tests/laws/test_anchored_projection.py`,
  `tests/laws/test_build_contract.py`

**Depends on** A4 and B1. A length fact separate from a quality fact only means
something once the vowel has two axes. **Moves** nothing in the tokens.
`l1`, `roundtrip` and `attestation` must hold.

Closes open question 4.
