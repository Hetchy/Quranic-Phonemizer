# 00 - What the legacy projections said, and what the model can say now

Status: **audit**, input to [01-design](01-design.md). Scope: Uthmani, Hafs.
IndoPak is deferred and nothing here depends on it.

This document is evidence, not decision. It answers three questions:

1. What did the five legacy projections actually publish, and which consumer
   read which field?
2. Where did a consumer have to invent a fact the projection did not give it?
   Those are the gaps, and they are the specification for the replacement.
3. What can the layered model on `riwayah-agnostic-refactor` state today, and
   what can it still not state?

Sources read: `main` at `quranic_phonemizer/{char_phoneme_mapping,
letter_phoneme_mapping,tajweed_mapping,silent,phonetic_text,tajweed_rule}.py`;
the branch
package; `quranic-universal-audio` (`qua_shared/schemas/bucket/ts_shard.py`,
`inspector/frontend/src/tabs/timestamps/utils/*`,
`inspector/frontend/src/lib/recitation-data/ts-source.ts`); `qua-sdk`
(`components/timing/lib/cells.py`, `domain/char_cells.py`).

---

## 1. The five legacy projections

| Projection | Row | Key | Payload |
|---|---|---|---|
| `letter_phoneme_mappings()` | one flat entry | a run of chars | `[chars, phonemes]`, every entry has >= 1 phoneme |
| `silent_flags()` | one written grapheme | position in reading order | `(char, silent, mark)` |
| `tajweed_mappings()` | one letter or split extension | `char` | `source_rules[]`, `target_rules[]` |
| `character_phoneme_mappings()` | one written or implicit character | `source_letter_index` + ordinal | `chars, role, status, phonemes, phoneme_indices, tag, share_group, source_letter_indices, phoneme_rule_tags, secondary_tags` |
| `phonetic_text()` | one string | none | the words re-spelled as recited, joined by separators |

`phonetic_text` is the odd one and the reason it is easy to overlook: it
publishes no rows, only text. `phonetic_text.py::_build_letter_segment`
rebuilds recited Arabic from `Word` and `LetterSymbol` by branching on
`TajweedRule` names, with `_is_allah_word` and `_get_allah_lam_index` as
lexical special cases. It is ADR-005's recited writing, implemented as a
string builder over rule names. The replacement is 01-design's recited-writing
serializer over `write` plus the contribution and attribution edges, and
because it is a serializer rather than a schema it changes none of the node or
relation design -- but it is a legacy promise, so 02-gate's manifest pins it.

The first four are four **traversals of the same join**, computed four times, over a model
(`PhonemizationMapping` -> `WordMapping` -> `LetterMapping`) that had no join to
traverse. `LetterMapping` held a letter, its diacritic, its extensions, its
phonemes and its rule tags in one flat record. Every relationship that crossed a
letter -- a merger, a shared long vowel, an inserted vowel, a redistributed madd
-- had to be *recomputed* by each projection from rule names.

That is the root cause of every smell below. It is not a naming problem.

### 1.1 Consequences that show in the code

**Rule-name-driven joins.** `letter_phoneme_mapping.py` classifies mergers by
intersecting a letter's source rules against six hand-maintained sets
(`NEXT_MERGE_TAJWEED_RULES`, `CROSS_WORD_MERGE_TAJWEED_RULES`,
`CROSS_WORD_BOTH_MERGE_TAJWEED_RULES`, `CROSS_WORD_NON_MERGE_TAJWEED_RULES`,
`WITHIN_WORD_NEXT_MERGE_TAJWEED_RULES`, `_SILENT_GAP_REASONS`). Adding a rule
means editing five tables in two modules or the merge silently misclassifies.

**Two coordinate spaces.** `char_phoneme_mapping` documents at length that
`phoneme_indices` come from "the raw per-letter walk, never a redistributed
view", because `letter_phoneme_mapping` separately performs iltiqa demotion and
waqf-tanween redistribution. A cell therefore points at a phoneme index that its
own `chars` may no longer own. The docstring is careful; the design is not.

**Presentation enums in the producer.** `CellRole` (`base`/`haraka`/`tanween`/
`madd`) and `CellStatus` (`present`/`inserted`/`dropped`/`replaced`/`shortened`)
are rendering vocabulary. `status` is not a fact about the text; it is a fact
about how a particular UI wants to draw it.

**Priority picks and spillover slots.** A cell carries one `tag`. When a
grapheme genuinely carries two rules the projection picks one by an ordered
tuple (`QALQALA_RULE_ORDER`) and spills the loser into `secondary_tags`. When a
single grapheme sounds several rules (muqattaat) it spills into a parallel
`phoneme_rule_tags` array. Two additive escape hatches for the same missing
fact: a rule applies to a *sound*, not to a *cell*, and there can be many.

**Grapheme-keyed rows cannot name what is not written.** Hence "implicit" cells
with `chars=""`, and hence `share_group` -- an integer invented so a consumer
could re-discover that two cells voice one sound.

---

## 2. Where consumers invent facts

This is the specification. Every item is a fact the producer knows and did not
publish, forcing a downstream reimplementation.

### 2.1 Frontend (`inspector/frontend/src/tabs/timestamps`)

`tajweed-rules.ts` declares seven `FeSynthesizedTag`s -- tags the renderer makes
up because no cell carries them:

| Synthesized tag | Why | Model has it? |
|---|---|---|
| `izhar_halqi` | legacy emits nothing for a sounding sakin noon | yes, `Rule.IZHAR_HALQI` |
| `izhar_shafawi` | same for meem | yes, `Rule.IZHAR_SHAFAWI` |
| `iqlab_silent_noon` | legacy tags iqlab only on tanween, never on noon | yes, `Rule.IQLAB` with the noon as participant |
| `iltiqaa`, `iltiqaa_kasra` | the SDK rewrites the raw tanween-iltiqa tag | yes, `Rule.ILTIQA_REPAIR` |
| `madd_iwad` | legacy maps `iwad` to `MADD_TABII` and loses it | yes, `Rule.IWAD` |
| `allah_dagger_alef` | no rule name for the lafdh al-jalalah dagger | yes, `Annotation.DIVINE_NAME` + a `LONG` nucleus |

`cell-special-cases.ts` performs two *cell surgeries*:

- **Iqlab noon.** Synthesizes a mini-meem cell above the noon and blanks the
  noon's phoneme indices, "the phonemizer stamps a mini-meem cell only for
  tanween iqlab". The Uthmani script writes `ۢ` in both cases; the producer
  simply did not attach it.
- **Silah maddah.** Moves the maddah glyph off the bearing `ه` onto the
  mini-waw/yaa carrier, because the producer merged it onto the wrong row.

`ts-source.ts::lettersFromCells` reimplements sound ownership: "Each phoneme is
therefore assigned to exactly ONE letter -- the carrier (`madd`) wins over the
consonant's `haraka`". This exists because `share_group` says two cells share a
sound but not which one *owns* it for animation. Letting both claim it smears
the consonant's highlight across the whole vowel. **The producer knows the
answer and does not ship it.**

### 2.2 SDK (`qua-sdk/src/qua_sdk/components/timing/lib/cells.py`, 641 lines)

- Re-slices the aligner's flat phones into words "by the phonemizer's natural
  per-word counts", because the shard's word allocation and the phonemizer's
  disagree at a cross-word idgham.
- Maintains an "indexable unit" coordinate space to exclude render-only markers
  (`Q`) from the index the cells count against.
- Re-exports `BRIDGE_RULE_VALUES` / `MERGER_ON_PREV_VALUES` from the phonemizer
  to decide which rules bridge words and which side of the bridge holds -- a
  classification that belongs to the merger edge itself.

### 2.3 Summary

Every invention above is a *relationship* the legacy row shape could not carry:
sound-to-letter ownership, rule-to-sound (many), rule-to-participant-role,
grapheme-to-unit when the grapheme is compact or the unit is unwritten.

---

## 3. What the branch model can say

Three layers, and the projection is a traversal of the graph between them.

```
Grapheme --Spelling--> Slot --Attribution--> Sound
                        ^          |
                        +-- Occurrence(Rule) --+
```

| Fact | Where it lives | Adequate? |
|---|---|---|
| what the script wrote | `Grapheme{id, char, cls, index}` | yes |
| what a mark is doing | `Spelling = Evidences \| Attests \| Decorates \| Structural` | yes |
| canonical position | `Slot{id, letter, onset, nucleus, origin, annotations}` | yes, see 4 |
| stop advice | `Inscription.advice`, one per word | yes |
| sakt | `ScoreWord.sakt_after` + `Rule.SAKT` | yes |
| what is heard | `Sound = Consonant \| Vowel \| Nasal \| Release` | yes |
| who produced it | `Attribution = Hosts \| Inserted \| MergedInto \| Silent` | yes |
| why | `Occurrence{id, rule, parts}`, `FAMILY_OF`, `Phase` | partly, see 4.1 |
| boundary state | `BoundaryPlan.junctions`, `Junction` | yes |
| variant reading | `VariantSelection`, `KhilafId`, `Option` | yes |
| a slot's own glyphs | `orthography/write.py::write_verse` via `Pen` | yes, see 4.5 |

Two structural wins over legacy, both free:

- **A merger is a pair of edges sharing a `SoundId`**, not an `assimilated`
  flag. `MergedInto` names the disappearing side, `Hosts` the surviving one.
  Legacy's `is_source` boolean and its six merge-classification tables collapse
  into reading the edge kind.
- **`Slot` is boundary-free and script-free.** Every legacy "implicit cell" --
  the hamza-wasl helping vowel, the iltiqa kasra, the Allah dagger alef, the
  madd-iwad alef -- is an ordinary `Slot` here. Nothing has to be invented to
  key them.

---

## 4. What the model still cannot say

Ordered by how much each blocks the projection.

### 4.1 Classification-only rules reach no sound (blocking)

`CLASSIFICATION_ONLY` in `model/canon.py` holds 18 rules that emit no
sound-producing effect: every `MADD_*`, `TAFKHEEM`, `TARQEEQ`, all three
`IZHAR_*`, `LAM_QAMARIYYAH`, `ILTIQA_REPAIR`, `IMALA`, `TASHIL`, `ISHMAM`,
`SILAH`, `SAKT`, `WASL_START`, `IDGHAM_MUTAJANISAYN_NAQIS`.

`render/anchored.py::_owners` only walks `Hosts` and `Inserted`, so
`AnchoredSound.rule` is the *attributing* rule -- which for all 18 is
`Rule.PLAIN`. A madd vowel's `rule` is `plain`. Tafkheem is invisible.

That is most of the tajweed a colourer wants. The information is not lost --
`Performance.occurrences` retains every `Occurrence` with its `Participants` --
but there is no edge from a sound to it, so today the join is guesswork.

**Two sub-gaps make the join unsafe:**

- **`Participants.slots` is an unlabelled tuple** whose order is convention.
  Twenty-one call sites pass `(at, other)` with `at` the anchor -- except
  `rules/madd.py:69` (`PausalGlide`), which passes `(before.id, at)`. A
  projection reading `parts.slots[0]` as the anchor is wrong exactly there.
- **`Recolour` and `Relength` are consumed and discarded.** `engine/run.py`
  folds them into the `Sound`'s `emphatic`/`nasal`/`long` fields and keeps no
  record of which occurrence set them. After materialisation you can see that a
  consonant is emphatic; you cannot see that `TAFKHEEM` made it so.

### 4.2 The composition root stops one level below a projection

`api.recitation(riwayah)` assembles a riwayah's adapters, data and rules, and
`engine/boundary_plan.py::plan_from_request` turns per-word `StopAdvice` plus a
requested stop set into a `BoundaryPlan`. Both of the pieces this document's
first draft called missing are there.

What is still absent is the level above them: a call that takes a *ref* -- a
range, not a verse -- resolves it against `PackedCorpus.locations`, loops
`read` -> `build` -> `perform` per verse, and returns one document. Today a
caller does that loop by hand, which is what every test does. That is
assembly, not design, but nothing ships until it exists.

### 4.3 The projection is verse-scoped; consumers are not

`SlotId.ordinal` counts slots across the verse and `GraphemeId.offset` is a
codepoint index within the verse. `Performance` is one verse. Legacy's `ref`
accepted ranges, and the teleprompter's wasl chains span verses. Ids are already
`VerseRef`-qualified, so a multi-verse document is assembly, not redesign -- but
it must be decided, not discovered.

### 4.4 `render/recite.py` is not ADR-005's `recite()`

ADR-005 specifies `recite(performance, inscription, *, faithfulness, silence,
insertions, depth) -> str` and calls the totality of `write` over recited forms
a phase-2 gate. `render/recite.py` on the branch is phoneme *ordering*
(`sounds_in_order`, `phonemes`, `phonemes_by_word`) under the same name. The
ADR-005 mechanism is unbuilt and the name is taken. The projection depends on
`write` totality (see 4.5), not on `recite`, but the collision should be fixed
before either is public.

### 4.5 `write` totality is unproven for the cases that matter

`orthography/write.py::write_verse` spells a `Score`. The recited-writing view
uses it for canonical units and separately renders slotless insertions at their
anchors. ADR-005 section 4 already names the trigger set: the 3:1 connected
meem fatha, hamzat al-wasl helping vowels in all three flavours, madd iwad, taa
marbuta at waqf, and every muqattaat expansion. Until that check passes, the
derived recited-writing view has no totality guarantee.

Two known asymmetries in `write` today, neither wrong but both visible in
output: `NucleusKind.LONG` always spells haraka + carrier + madd sign rather
than the dagger abbreviation, and `Annotation.DIVINE_NAME` has no role so it
spells nothing.

### 4.6 `write` reads `IMALA` off the slot, and D2 takes it away

`orthography/write.py` reads `Annotation.IMALA` from `slot.annotations` in two
places: `_SPELT_AS_A_NUCLEUS` at line 45, which suppresses writing the mark
twice, and `_nucleus` at lines 197-200, where `pen.role(IMALA)` writes the
whole vowel, carrier and all, as one mark.

[03](../03-canonical-vocabulary.md) D2, as ADR-013 §4 amends it, makes `IMALA`
a rule occurrence rather than a unit tag. Occurrences live in the
`Performance`, and `write` takes a `Score`. So D2 as stated breaks the
round-trip on every imala site unless one of these lands with it:

- `write` takes the selection and re-derives imala from the khilaf point, which
  is where the quality choice already lives (`KhilafId.IMALA_QUALITY`); or
- imala stays a canonical fact under a different name, and the occurrence is
  the classification over it -- the same shape `DIVINE_NAME` gets.

The second is the smaller change and matches the reasoning D2 uses for
`DIVINE_NAME`: a fact the script writes is canonical, and the occurrence is
what a projection names it by. The first is defensible but moves khilaf
resolution into the writer. Either way it is a decision D2 currently does not
make, and the round-trip gate catches it the moment D2 lands.

`ISHMAM` is unaffected: no script writes it and `write` never reads it.

### 4.7 Smaller items

- `Onset.SILAH` is set from one ledger row only (`27:36:8#3`, the yaa ithbat).
  It is live, not dead -- worth stating because grepping the package finds no
  producer.
- `SlotOrigin.WRITTEN` is read by zero branches. See [03](../03-canonical-vocabulary.md).
- `Annotation` is documented "changes no sound"; `DIVINE_NAME` gates tafkheem
  at `rules/tafkheem.py:135`. Also 03.
- `ScoreWord` has no text. The projection must carry the script's own word
  string, which comes from the corpus, not from any layer.
- Whether the Uthmani inventory reads the iqlab small meem `ۢ` (U+06E2) as an
  `Attests(NASALIZATION)` on the noon has not been checked. If it does not, the
  frontend's iqlab-noon surgery survives the rewrite.

---

## 5. Legacy rule vocabulary against the new one

Legacy `TajweedRule` has 30 members; branch `Rule` has 40. The mapping is total
in one direction and needs one recoverable bit in the other.

| Legacy | Branch | Adapter |
|---|---|---|
| `ikhfaa_noon` / `ikhfaa_tanween` | `IKHFAA_HAQIQI` | split on `unit.nunation` |
| `iqlab_noon` / `iqlab_tanween` | `IQLAB` | split on `unit.nunation` |
| `idgham_ghunnah_noon` / `_tanween` | `IDGHAM_BI_GHUNNAH` | split on `unit.nunation` |
| `idgham_bila_ghunnah_noon` / `_tanween` | `IDGHAM_BILA_GHUNNAH` | split on `unit.nunation` |
| `noon_ghunnah` / `meem_ghunnah` | `GHUNNAH_MUSHADDADAH` | split on `unit.letter` |
| `madd_arid_lissukun` | `MADD_ARID_LIL_SUKUN` | rename |
| `hamza_wasl_fatha` / `_kasra` / `_damma` | `WASL_START` | split on the unit's nucleus quality |
| `silent_iltiqaa_sakinayn`, `iltiqaa_sakinayn_tanween` | `ILTIQA_REPAIR`, `WASL_ELISION` | see gate |
| `lam_shamsiyah` | `LAM_SHAMSIYYAH` | spelling |
| `vowel_silent` | none | catch-all, see below |
| the rest | same name | identity |

Branch-only, no legacy counterpart (all additive, exempt from the gate):
`IZHAR_HALQI`, `IZHAR_MUTLAQ`, `IZHAR_SHAFAWI`, `LAM_QAMARIYYAH`,
`QALQALA_AKBAR`, `TARQEEQ`, `IMALA`, `TASHIL`, `ISHMAM`, `IWAD`, `IBDAL_HAMZA`,
`WAQF_ENDING`, `SILAH`, `SAKT`, `PLAIN`.

**`vowel_silent` is the one open item.** It is legacy's catch-all for a letter
that produced nothing with no better reason, and the frontend gives it a
tooltip. In the branch every `Silent` attribution cites an `Occurrence` with a
real `Rule`. Whether that is *always* true across the corpus, and which rules
appear, is an empirical question the gate must answer (02-gate §3).

---

## 6. Findings, ranked

| # | Finding | Blocks |
|---|---|---|
| F1 | Classification-only rules have no sound edge; `AnchoredSound.rule` is `plain` for every madd | the whole tajweed payload |
| F2 | `Participants.slots` is unlabelled; `PausalGlide` reverses the convention | any rule-to-unit join |
| F3 | `Recolour`/`Relength` lose their occurrence at materialisation | `tafkheem` on a sound, `iltiqa` shortening |
| F4 | `api.recitation` and `plan_from_request` exist; the ref-to-document loop above them does not | shipping anything |
| F5 | Verse-scoped ids vs multi-verse consumers | wasl chains, ranged refs |
| F6 | `write` totality unproven over ADR-005 section 4's trigger set | recited writing |
| F7 | *Withdrawn.* See below | -- |
| F8 | `render/recite.py` occupies ADR-005's `recite` name | naming only |
| F9 | `vowel_silent` residue unquantified | the equivalence gate |
| F10 | Iqlab small meem attachment unverified | one frontend surgery |
| F11 | `write` reads `IMALA` off the slot; 03's D2 removes it | the round-trip, once D2 lands |

**F7 is withdrawn, not fixed.** It read "sound ownership for display is
computed by the consumer", filed as an animation-correctness risk on the
grounds that `ts-source.ts::lettersFromCells` and the SDK could pick different
owners. ADR-013 §2 establishes that display ownership *is* a rendering policy
and must not be stored: a haraka and its length carrier evidence the same
unit, so no `owner: Unit` can name which glyph to paint. The divergence in
§2.1 is real, but its cause is the missing glyph-level relation, which is
F1/F3's contribution edge -- not a missing ownership field. `display_glyph`
being a consumer policy is the design, so it is not a finding.
