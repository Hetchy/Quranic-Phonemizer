# Phase A - model surgery

Nine units on the model spine. Lane 1, strictly serial: A1, A2, A3, A6, then
A4, A5, then A7, A8, A9. Three of them move recitation output and are marked.

---

## A1 - Rename the parts to `consonant` and `vowel`

**Item 9. Small, wide: 84 `Aspect` occurrences across 16 files.**

- `model/performance.py` - **load-bearing.** `Aspect`, and the `aspect` field
  on `Hosts`, `Inserted`, `MergedInto`, `Silent`.
- `engine/plan.py`, `engine/run.py`, `engine/laws.py`
- `render/anchored.py` (`_FACT_OF_ASPECT`), `render/recite.py` (`_ASPECT_ORDER`)
- `rules/`: `boundary.py`, `meem_sakinah.py`, `madd.py`, `noon_sakinah.py`,
  `idgham.py`, `lam_shamsiyyah.py`, `qalqala.py`, `tafkheem.py`
- `tests/laws/test_model_vocabulary.py` (asserts `len(Aspect) == 2`),
  `tests/laws/test_noon_family.py`

**Depends on** nothing. **Moves** nothing: `regression` and `cross-script` must
come back byte-identical, and `tools/snapshot.py diff` must report zero. A
rename that moves a number is a bug in the rename.

## A2 - Trim the rule vocabulary

**Items 8, 11, 12. Small to medium.**

Delete `Rule.PLAIN` and `Rule.SAKT`; collapse `IZHAR_HALQI` and `IZHAR_MUTLAQ`
into one `IZHAR`, because one outcome with two triggers may not carry the
trigger in its name. Sakt becomes `Word.sakt_after` and stops being a rule.
`by` becomes optional on the attributions, since with no `plain` rule there is
nothing to cite when no rule claimed the sound.

- `model/canon.py` - **load-bearing.** `Rule`, `FAMILY_OF`,
  `CLASSIFICATION_ONLY`.
- `model/performance.py` - `by: OccurrenceId | None` on all four attributions.
- `engine/run.py` - the synthetic `plain` occurrence and the `_fill` that cites
  it; `engine/laws.py` `_every_occurrence_produced_or_declared` and
  `_every_attribution_resolves`.
- `engine/plan.py` `mint()` indexes on `list(Rule).index(rule)`, so removing a
  member reshuffles every `OccurrenceId`. Request-local and harmless, but no
  test may key on one.
- `rules/noon_sakinah.py` (the two izhar branches), `rules/annotation.py`
  (delete the `Sakt` classifier), `riwayat/hafs/rules.py`

**Depends on** A1. **Moves** nothing.

## A3 - The rule family and phase leave the model

**Item 7. Large: three readers to replace, and one changes recitation.**

- `model/canon.py` - **load-bearing.** Delete `RuleFamily`, `Phase`,
  `FAMILY_OF`.
- `model/inscription.py` `Attests` - **load-bearing.** `Attests.family` is the
  model's other consumer; the contract's `Witnesses(glyph, unit)` is this edge
  minus the family.
- `engine/plan.py` `assimilated_from` - **load-bearing and output-changing.**
  `rules/qalqala.py` calls it, and it asks whether the family is assimilation.
  `02-gate` section 4.8 forbids the replacement from reading a performance
  result, so the condition becomes the canonical merger table over letters plus
  the boundary plan.
- `engine/classifier.py` (`RuleSet.phases`), `engine/run.py` (`PHASE_ORDER`),
  `engine/laws.py` `check_attestations`
- `orthography/adapter.py` `Attestation`, `canon/scribe.py`,
  `canon/derive/vocabulary.py`, `canon/derive/gemination.py`
- `riwayat/hafs/rules.py` (the `Phase`-keyed dict)
- `tools/attest.py`, `tools/structure_lint.py` (`PROTOCOLS` keys on a literal
  parameter tuple)
- `tests/laws/test_model_vocabulary.py`, `tests/laws/test_attestation_law.py`,
  `tests/laws/test_build_contract.py`

**Depends on** A2. **Moves** `regression`, for qalqala only. `attestation` is
the only gate exercising `Attests` and must hold.
`tests/laws/test_minimal_pairs.py::test_an_assimilated_closure_has_no_qalqala`
(5:28 `بَسَطتَ`) is the sharpest local test.

## A4 - The two-form vowel

**Items 3, 4 (the type half). Large: the widest change in the set, roughly 272
occurrences across 41 files.**

Five `Nucleus` variants collapse to one record with a `joined` form and a
`stopped` form, each `absent | short(quality) | long(quality)`. Item 3's other
half: `Onset.SILAH` is renamed so the word stops naming two unrelated things,
a consonant present only when joined and a vowel long only when joined.

- `model/canon.py` - **load-bearing.** Delete `NucleusKind`, `Silent`, `Short`,
  `Long`, `Silah`, `PausalLong`, the `Nucleus` alias and `SILENT`.
- `canon/derive/length.py` - **load-bearing.** `dagger`, `carrier` and
  `pausal_length` are the three producers of the collapsed variants.
- `canon/derive/{silah,tanween,lexeme,wasl,gemination,vocabulary}.py`
- `canon/draft.py`, `canon/passes.py`, `canon/juncture.py`, `canon/khilaf.py` -
  **load-bearing:** `type(held)(quality)` reconstructs a nucleus from its class
  and means nothing after the collapse.
- `canon/spell.py`, `canon/ledger.py` (`_NUCLEUS_KINDS`), `canon/assemble.py` -
  **load-bearing:** the digest line embeds `nucleus.kind`, so **every
  `canon_digest` changes with this unit.**
- `orthography/inventory.py` (`_NUCLEUS_KINDS`, the second copy of that table)
  and `orthography/write.py` `_nucleus` - **load-bearing:** its `match` is the
  whole `roundtrip` gate.
- `engine/run.py` (`_plain_sound`, `has_content`), `engine/classifier.py`
- `rules/madd.py` (33 hits, **load-bearing**), `rules/boundary.py` (19,
  **load-bearing**), and `annotation`, `tafkheem`, `qalqala`, `idgham`,
  `lam_shamsiyyah`, `ownership`, `khilaf`
- `riwayat/khilaf.py`, `riwayat/hafs/rules.py`
- both script yamls (every `value: {kind: ...}` row), `ledger.yaml`
- `tools/roundtrip.py`, `tools/l1_harness.py`
- `tests/laws/test_model_vocabulary.py` (pins the five kinds),
  `tests/schema/test_ledger.py`, `tests/laws/test_minimal_pairs.py`,
  `tests/laws/test_noon_family.py`, `tests/test_khilaf.py`,
  `tests/laws/test_script_agreement.py`

**Depends on** A1, A2. **Moves** nothing. `roundtrip`, `l1`, `cross-script` and
`regression` must all be unchanged: this unit is deliberately output-neutral and
A5 is where the number moves.

## A5 - The seven alifs sited by word location  [moves output]

**Item 4 (the data half). Small in code, first unit to change a token.**

`engine/run.py`'s plain fill renders a `PausalLong` as long under every boundary
plan, so the boundary-conditional vowel affects no token today. `أَنَا۠` is long
when joined and should be short.

The seven alifs must be sited **by word location**, not by vocalised skeleton:
the tail of `جَآءَنَا` spells what `أَنَا۠` spells and its final alif is an ordinary
pronoun, and 76:15 `قَوَارِيرَا۠` and 76:16 `قَوَارِيرَا۟` are the same letters and
harakat with opposite behaviour, told apart by a silence sign no skeleton keeps.

- `canon/passes.py` `_apply_pausal_lexemes` - **load-bearing.** Keys on the
  vocalised span today.
- `data/riwayat/hafs/lexicon.yaml` - **load-bearing.** Its own comment concedes
  the skeleton cannot separate `لَّـٰكِنَّا۠` or the three `قَوَارِيرَا۠` sites, which
  is why those are already Ledger entries.
- `canon/lexicon.py`, or move the sites into `ledger.yaml`
- `tools/gates.py` - the `regression` floors drop. This is permitted: the oracle
  is the previous implementation with its defects frozen in.
- `docs/conformance/gate-residues.md`, and a new
  `docs/conformance/corrections.md` with one exact old and new case per ref
- `tests/schema/test_lexicon.py` (budgets), one regression test per corrected ref

**Depends on** A4. **Moves** `regression`, and `cross-script` must move with it
in both scripts, because the fact is lexical and not orthographic. Regenerate
both head snapshots.

## A6 - `Participants` are labelled

**Item 14. Small: 23 construction sites.**

`Participants.slots` becomes `source` and `host`. A rule's units are a source
and a host, and the pair is positional today.

- `model/performance.py` - **load-bearing.**
- Every `rules/` module, and `engine/run.py`
- The readers of `.parts.slots`: `engine/laws.py`, `engine/plan.py`,
  `tests/laws/test_minimal_pairs.py`, `tests/laws/test_noon_family.py`

**Depends on** A3, which deletes the one positional reader that is not a
projection. **Moves** nothing.

## A7 - Modifier edges survive into the document

**Items 2, 28. Medium to large.**

`engine/run.py` folds every `Recolour` into a feature dict, bakes it into the
`Sound`, and discards the edge; same for `Relength`. `tafkheem` is the largest
instance class in the corpus and every instance owns nothing. `Classifies` has
never existed: `CLASSIFICATION_ONLY` is an allowlist that exists purely so the
laws will not raise on rules that own nothing.

- `model/performance.py` - **load-bearing.** `Recolours(sound, by)`,
  `SetsLength(sound, by, length)`, `Classifies(sound, by)`; `Performance` gains
  a `modifiers` tuple.
- `engine/run.py` `_materialise`, `_colours`, `_apply_colours` -
  **load-bearing.**
- `engine/plan.py` `Recolour` and `Relength`; `engine/laws.py` gains a law that
  every applied recolour and relength retains exactly one edge
- `model/canon.py` `CLASSIFICATION_ONLY` becomes the `Classifies` list rather
  than an exemption list
- `rules/tafkheem.py` `Emphasis.look` - **item 28**: decline the colour where a
  complete merger consumed the consonant, because the letter has no sound of
  its own to be heavy. `_silenced` already declines it for the vowel; the
  consonant needs the same guard.
- `rules/annotation.py`, `rules/madd.py` `_classify`
- `tests/laws/test_model_vocabulary.py`, `tests/laws/test_noon_family.py`

**Depends on** A1. **Moves** nothing from the edges themselves: adding an edge
must not move a token. Item 28 is the exception and does move `regression`.

Settles open question 5 in passing. The package already agrees with the
contract: only the iltiqa repair emits a real relength, so `SetsLength` is for
that alone and the five madd rules take `Classifies`. `imala` takes
`Classifies` too, since its quality is resolved at build time. Correct
`07-rules` section 2's effect column in the same commit.

## A8 - The ghunnah is a consonant feature  [moves output]

**Items 10, 13, 15. Medium: 61 `Nasal` hits across 9 files, 44 `Release` hits
across 7.**

**Read [decisions.md](decisions.md) sections 1, 2 and 7 before starting.** They
settle what the nasal place does, what an eased hamza does, and the two new
tokens.

- `model/performance.py` - **load-bearing.** Delete `Nasal` and `NasalPlace`;
  `Consonant.nasal` becomes `ghunnah`; `Consonant` gains `eased`; `Release`
  gains `degree` and `ReleaseKind` collapses to its single kind.
- `render/alphabet.py` - **load-bearing.** The `nasals` and `releases` dicts,
  the `case Nasal()` branch, the nasal branch of `_consonant`.
- `data/render/ipa.yaml` - **load-bearing.** Delete the `nasals:` block. The
  four `nasal:` entries on meem, noon, waw and ya already spell what item 10
  needs, except `ŋ`: a non-geminate nasal noon is the hum, a geminate one is
  the held letter, which is the one key item 10 says the notation gains. Add
  `hamza.eased` (`ʔ̞`) and the heavy hum (`ŋˤ`).
- `engine/run.py` (`case Nasal()` in `_apply_colours`)
- `rules/noon_sakinah.py`, `rules/meem_sakinah.py`, `rules/lam_shamsiyyah.py`,
  `rules/khilaf.py` (`NASAL_PLACES`, `nasal_place`), `rules/qalqala.py`
- `model/address.py` - `KhilafId.IQLAB_NASAL` and
  `KhilafId.IKHFAA_SHAFAWI_NASAL` **stay**; the reading now rides on the letter
  the rule mints.
- `01-contract.md` sections 3.1 and 4.4, and section 9 item 1: all three are
  corrected here.
- `tests/schema/test_render_map.py` (the strictest file in the suite, total by
  coverage in both directions), `tests/nasal/test_nasal_place.py`,
  `tests/test_khilaf.py`, `tests/laws/test_minimal_pairs.py`,
  `tests/test_muqattaat.py`

**Depends on** A7: item 13's heavy hum is a `Recolours` edge the ikhfaa owns.
**Moves** `regression` only where item 13's heavy hum applies. Every other token
must stay as it is, and `tests/nasal/test_nasal_place.py` must keep passing
unchanged.

Closes open questions 1 and 3.

## A9 - Release attribution moves to the consonant  [moves output]

**Item 29. Small in lines, sharp in consequence: every release in the corpus
sits on the vowel today.**

- `rules/qalqala.py` - **load-bearing.** The single mint site.
- `engine/run.py` `_fill_plain` - **load-bearing, and the trap item 29 names.**
  The claim set is built from every realization, so the moment the release names
  the consonant part the plain fill treats that part as spoken for and **the
  consonant's own sound disappears.** The release must become an addition the
  claim set ignores.
- `engine/run.py` `_realize` and `_fill`; `engine/laws.py`
- `render/recite.py` `_ASPECT_ORDER` and `sounds_in_order` - **load-bearing.**
  Two sounds on one slot and part collide on the sort key, so order becomes
  insertion-order dependent. The same collision is in `phonemes_by_word`.
- `render/anchored.py` `_FACT_OF_ASPECT`: a release on the consonant part now
  pulls the letter's graphemes, which is what `07-rules` section 6 case 4
  describes.
- `tests/laws/test_minimal_pairs.py`

**Depends on** A1, A8. **Moves** token **order** if it goes wrong: `b Q` must
not become `Q b`. `tools/parity.py` compares exact token sequences per word, so
an ordering slip shows up immediately in `regression` and `cross-script`.
