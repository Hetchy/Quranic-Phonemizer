# Phase D - machinery and the public surface

Five units, serial. Two deviate from `02-gate` section 8's literal order and
both deviations are forced by the code: D1 runs before D2 and D3 because the
writer needs a boundary plan over a span, and D5 runs after D4 because a schema
cannot be written before the arrays it describes exist. Note both when the gate
document is next revised.

---

## D1 - Ref grammar, sub-verse guard, orchestration, continuous assembly

**Items 34, 35, 36, 37. Large.**

`corpus.py` `locations()` already parses `surah[:ayah[:word]]` and hyphen
ranges, but does not enforce the contract's "both endpoints at the same depth",
and nothing clips a Score to a sub-verse span: `Recitation.words` is
verse-granular and `canon.build` is verse-scoped throughout. A request clipping
a ledger-addressed word must raise rather than build.

Item 35's overlap is two words, not one: `engine/neighbourhood.py` `after`
reaches one slot, but `canon/juncture.py` `apply_cross_word_noon` reaches a
word ahead, which is why one word of overlap is not enough.

Item 36: resolve `(ref, boundaries, variant)`, build, perform, and assemble one
index space. Arbitrary stops, sakt and cross-verse joins use the same path, and
a started-on word is the word after a stop rather than a second input.

**Files:** new `phonemize/request.py`, `phonemize/boundaries.py`,
`phonemize/span.py`, `phonemize/session.py`; `corpus.py`; `api.py`;
`engine/boundary_plan.py` `plan_from_request` (it takes `StopAdvice` classes
today, not `stop_signs` and `stop_refs`); `canon/build.py` for the overlap.

**Depends on** A4, A5, C1. **Verified by** the fixture matrix of `02-gate`
section 2: a range beginning inside a verse, one clipping a ledger-addressed
word, an arbitrary internal stop, a sakt, a cross-word and a cross-verse join, a
multi-verse range in one index space. `tools/parity.py` refuses `continuous`
today because a verse-by-verse harness cannot plan for it; this unit is what
unblocks that mode.

## D2 - The recited writer and `rendered`

**Item 32. Large.**

`orthography/write.py` `write_verse(score, pen)` takes a Score, so it has no
boundary plan and no performance and cannot spell a pausal, merged or
started-on form. It **cannot be extended in place**: `orthography` may import
only `dataio` and `model`. That is not a preference, it is the import graph, and
it is why item 32 exists.

`rendered` needs glyph records carrying `from_glyphs`, their own pairings, and
the blocks `respelling` returns. The 31 transformations of `06-two-texts`
section 4 are the specification.

**Files:** new `phonemize/recited.py`; reuse `orthography/write.py` `pen_for`
and `Pen`; `canon/spell.py` `named_by` for the muqattaat expansion.

**Depends on** D1, B1, B2, C1 through C4. **Verified by** the laws of `02-gate`
section 4.7. `roundtrip` is unaffected, being a different closure.

Settles open question 9: stop signs are kept in `rendered`, given the
`Structural` edge so they take no pairing, and `r.text("recited")` serializes
the same array `rendered` holds.

## D3 - Glyph pairing, alignment, respelling

**Item 33. Large, the hardest unit in the program.**

`render/anchored.py` `by_grapheme` is the nearest thing today and it is a bare
glyph-to-sounds dict: it cannot distinguish a sounded dagger from its silent
carrier, nor a performance deletion from orthographic zero. The ownership order
of `01-contract` section 6.1 and the cell clauses of section 6.4 are both built
on B2's fact split.

**Read [decisions.md](decisions.md) section 3.** The cell law names the `letter`
fact and states tanween as its exception; reword `02-gate` section 4.6 here.

Open question 2, `Block` is not total, is settled by building this and seeing
which shape the writer needs. Three cases resist a non-empty source: a soundless
insertion, a structural deletion, and the divine name's carrier, where E4 and
E13 draw one phenomenon two ways. **E13's shape is the one the set believes.**
If the other two still resist, strike section 6.3's claim rather than bending
the data to it.

**Files:** new `phonemize/pairing.py`, `phonemize/respell.py`,
`phonemize/nodes.py`, `phonemize/edges.py`, `phonemize/assemble.py`; retire
`render/anchored.py`.

**Depends on** B2, D2. **Verified by** the laws of `02-gate` sections 4.5 and
4.6 over the corpus in all three modes.
`tests/laws/test_anchored_projection.py` is the seed for the new suite.

## D4 - The public package

**Items 1, 5, 38, 39, and `01-contract` sections 3 through 5 in full. Large.**

Item 5 needs no work: `SlotOrigin` already has exactly the three members and
`tests/laws/test_model_vocabulary.py` already pins them. Confirm and move on.

**The layer declaration.** A new `structure_lint.py` node `phonemize`, above
`api`:

```python
"phonemize": {"api", "canon", "corpus", "engine", "model",
              "orthography", "render"},
"":          {"model", "phonemize"},
```

`api.recitation()` is already the assembled bundle, so importing it beats
re-deriving it, and this is the position `02-gate` section 9 anticipates.
**Do not declare a `rules` edge**: rules arrive inside `Recitation.rules`, and
`_unused_permissions` fails on a declared edge nothing exercises. `PUBLIC_API`
must gain every exported name or the dead-export check fails.

**Three placements are forced, not chosen.** `recited.py` cannot live in
`orthography/`; `labels.py` cannot live in `rules/`, because item 40 says the
labels mint no instance and assembly is what enforces that; `schema.py` may hold
no phoneme string, because `PHONEME_MARKERS` is checked over the whole package
outside `render/`.

**Item 39, the optional phonemes.** All four gate **at the notation** and reach
no node and no edge. See [decisions.md](decisions.md) section 7 for the tokens.

**Files:** new `phonemize/{__init__,session,document,names}.py`; `api.py`;
`__init__.py`; `tools/structure_lint.py` `ALLOWED` and `PUBLIC_API`;
`render/alphabet.py` and `data/render/ipa.yaml` for the toggles. Retire
`render/anchored.py` and `render/recite.py`; keep `api.recitation()`.

**Depends on** D1, D2, D3, A6, A7, A8, A9, C2. **Verified by** `structure`,
which is the gate this unit can fail on the import graph, the dead-export check
and the 400-line cap; and `02-gate` sections 4.1 and 6.

Closes open question 7 as it chooses the literals. `Unit.letter` takes
`CanonLetter`'s spellings verbatim (`ba`, `ya`, `ha`, `heh`); the contract prose
is what is wrong, not the model. `word_index` on a structural glyph is absent,
matching section 4.3.

## D5 - Versioned schema and negative tests

**`02-gate` section 5. Medium.**

Tagged unions for vowel, sound, spelling, attribution and modifier values, and
the twelve named negative cases. Adding a union member requires a version change
plus a negative test showing older readers fail clearly.

Discriminators are needed because `Witnesses` and `Decorates` have identical
payloads, and so do `Recolours` and `Classifies`. Pick a `kind` field carrying
the edge name lowercased.

**Files:** new `phonemize/schema.py`, new tests under `tests/schema/`.

**Depends on** D4. **Verified by** the twelve negative cases and canonical-JSON
round-trip.

---

## D6 - deferred

The six legacy adapters and `tools/projection_parity.py`. Out of scope for this
program: legacy parity confirms and never gates, so the adapters are a later
effort. `docs/legacy/` holds the specification of what they must reproduce and
`research/legacy-baselines/manifest.json` pins the frozen data.
