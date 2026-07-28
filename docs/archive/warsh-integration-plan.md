# Riwāyah-agnostic refactor and Warsh integration plan

> **Archived 2026-07-26.** Historical record only — do not read this as a
> description of the current codebase or of the accepted design. A new ADR
> set is being written to supersede it.
>
> Reason: sequencing superseded. A second Hafs script (IndoPak) is now the
> next orthography phase, ahead of Warsh.

## Outcome

Build a clean canonical phonemizer for Hafs whose source-normalization and
explicit rule-construction seams are already proved against the available Warsh script. Then
add Warsh pronunciation only from reviewed Warsh recitation research.

The rework is not a legacy-schema preservation exercise. Today's code is the
behavior inventory and executable evidence; the target API and internal model
may be cleaner. The goal is to preserve correct capabilities—phonemes,
boundaries, Tajwīd, madd classification, letter/character attribution, silent
letters, recited Arabic, text matching—not every historical DTO field or
string enum.

Governing documents:

- ADR-001: canonical model and riwāyah pipeline composition;
- ADR-002: invariants and implementation gates;
- ADR-003: code/runtime-data/build/docs/research ownership;
- `docs/tajweed-model.md`: concrete models and every implemented Tajwīd family;
- `docs/warsh-script-codepoint-audit.md`: complete Hafs/Warsh source audit;
- `docs/current-implementation-mapping.md`: every current module/resource/tool
  mapped to a target owner.
- `docs/internal-model-worked-examples.md`: complete model walkthrough,
  including every muqaṭṭaʿāt form.
- `docs/follow-up-decisions.md`: point-by-point decisions from the second
  adversarial review.

## Readiness verdict

The **Hafs refactor is implementation-ready after the second-pass corrections
in these documents**. The model, relationship variants,
Tajwīd vocabulary, data/code split, repository layout, migration ownership,
and vertical proof slices are decided.

The **Warsh source adapter is implementation-ready only for the accepted
families in the codepoint audit**: ordinary shared letters/marks, alternate
tanween, yeh barree families, reviewed hamzat-al-waṣl sequences, structural
marks, and iqlāb hints.

The **complete Warsh phonemizer is not implementation-ready** because there is
no reviewed Warsh rule/delta research yet. The unresolved items are now narrow
and explicit rather than model gaps:

- marked `۪` vowels: which sites are imālah versus taqlīl and their exact
  sound values;
- plural-mīm/small-wāw realization;
- Warsh stop-sign convention and boundary policy;
- Warsh-specific hamza/naql/tashīl/ibdāl behavior;
- any Warsh-specific rāʾ, lām, madd, waqf, muqaṭṭaʿāt, or exception deltas;
- minority ambiguous Unicode sequences listed by the script audit.

Unknown Warsh behavior must fail closed or remain unimplemented; it must not
inherit Hafs merely because the model can express it.

## What the audit established

The audit covered all 35 production Python files (7,372 lines), all current
runtime resources, the five development scripts, workflows, tests/baselines,
and every codepoint in the current Hafs and PR #37 Warsh word corpora.

Key consequences:

- the current mutable `LetterSymbol` graph, string-token predicates, madd
  post-pass, global caches/overrides, and six independent output re-derivers
  all need replacement;
- one grapheme↔segment alignment relation can project letter mapping,
  character mapping, silence, shared ownership, and Tajwīd participants;
- rules must see canonical letters/marks, not source glyphs;
- `U+0656` is a Warsh kasratan convention, not imālah;
- `U+06EC`, `U+06DF`, and `U+06EA` are sequence/context dependent;
- the Hafs 11:41 imālah hardcode can be replaced by marked-vowel recognition,
  while the riwāyah classifier decides the quality;
- small mīm is an orthographic iqlāb hint, not the rule engine;
- 621 aligned plural-mīm cases are likely genuine riwāyah behavior, not a
  source alias;
- PR #37's raw cleaner removes 6,228 characters through a generic flagged
  list and needs a semantic transform manifest;
- Warsh has a separate address/word shape, including structural-token
  differences, so corpus selection must be riwāyah-scoped.

## Target flow

```text
request + riwayah id + boundary policy
  -> riwayah corpus/address resolution
  -> exact source Graphemes
  -> source adapter -> source-only canonical LetterUnits
  -> lexical expansion + boundary realization -> provenance-bearing RecitedWords/Letters
  -> baseline semantic Segments
  -> shared rule passes + explicit riwayah pipeline classifiers
  -> Alignments + TajweedOccurrences (including madd) + RealizationEvents
  -> recited Arabic graphemes + rendered tokens
  -> clean public projections
```

No projection runs a rule detector. No rule reads output-token strings. No
source adapter decides Tajwīd merely from an optional hint mark.

## Implementation sequence

Each slice lands running code and tests. Do not create every future data file
up front.

### PR 1 — repository and corpus-build foundations

**Changes**

- Raise Python floor/CI/package metadata to 3.11+.
- Create `corpora/`, `tools/corpus`, `tools/audit`, `research/`,
  `docs/script-conventions/`, and ignored `build/` according to ADR-003.
- Move current `dev/` and runtime research/material by purpose; do not mix moves with
  phonological changes.
- Add Hafs corpus manifest, canonical `words.json`, deterministic DB/index
  build, and hash comparison.
- Import PR #37 raw Warsh source and canonical word input under a Warsh corpus
  manifest. Replace generic stripping with an explicit transform manifest.
- Decide lexical versus structural word slots during build; prove rub-el-hizb
  cannot become an accidental phonemizer word.
- Configure recursive package data for `quranic_phonemizer/data/**`.
- Build/install wheel and sdist and run a Hafs corpus smoke test.

**Acceptance**

- Both runtime corpus pairs reproduce from committed canonical inputs.
- Raw-to-canonical Warsh counts/removals are explained and hashed.
- Runtime imports nothing from corpus inputs, docs, research, or build.

### PR 2 — canonical model and source adapters

**Changes**

- Add `model/` types from ADR-001 and `tajweed-model.md`.
- Add the closed `Riwayah` enum, `RiwayahResources`, explicit pipeline
  constructors, immutable render config, and riwāyah-keyed corpus/matcher
  caches. Do not add `RulePolicies`.
- Implement exact grapheme clustering and canonical `LetterUnit` construction.
- Enforce non-empty source provenance on every `LetterUnit`; add
  provenance-bearing `RecitedWord`/`RecitedLetter` for event-created/expanded
  writing and boundaries between recited words.
- Model `Harakah` (fatha/damma/kasra/sukūn), tanween, and
  dagger-alef/mini-wāw/mini-yāʾ
  `SmallVowel`s as first-class composed values; do not port the legacy generic
  mark category.
- Implement the complete Hafs source adapter with fixtures for every accepted
  codepoint/sequence family.
- Implement only the accepted Warsh adapter subset from the codepoint audit;
  reject unresolved sequences with location/codepoint diagnostics.
- Add glyph-first `data/shared/tajweed.yaml`, `render.yaml`, and source scalar
  aliases only where the code now consumes them.
- Fix the current `_DB.items()` matcher defect in the new corpus interface;
  do not preserve the exception.

**Acceptance**

- Exact source strings reconstruct byte-for-byte.
- The source serializer and `SOURCE_EXACT` render preset agree byte-for-byte;
  manually inserted writing cannot enter the `LetterUnit` collection.
- Every grapheme has a role and every sounding candidate belongs to one unit.
- Hafs `ٱ` and reviewed Warsh alef+mark sequences yield the same hamzat-waṣl
  unit.
- Hafs/Warsh tanween and yāʾ-family equivalence fixtures pass.
- Warsh harakah+mini-mīm and bare-nūn+mini-mīm normalize to canonical
  tanween/nūn subjects plus a non-driving iqlāb hint.
- Hafs and Warsh instances coexist in either construction order.

### PR 3 — baseline segments, alignment, and nūn/tanwīn vertical slice

**Changes**

- Build baseline consonant/vowel segments without per-letter subclasses.
- Add one `GraphemeAlignment` per source scalar.
- Implement boundary resolution before cross-word rules.
- Implement the exhaustive nūn/tanwīn family in shared Python using glyph-first
  finite sets:
  iẓhār ḥalqī, ikhfāʾ ḥaqīqī, iqlāb, idghām with and without ghunnah.
- Record `NoonOccurrence` with subject/result, trigger kind, following letter,
  and a target only for actual idghām.
- Render semantic segments and expose the first clean source/letter/segment,
  silence, and Tajwīd projections.
- Validate (but do not depend on) the Warsh small-mīm iqlāb hint.

**Acceptance**

- Within-word, cross-word, nūn, tanween, all five outcomes, and stopping
  cancellation pass.
- Ikhfāʾ has an explicit following trigger and no false target; idghām has a
  real target.
- Source/letter/phoneme/silence views are all projections of the same
  alignment and occurrence records.
- At least one different-script/same-shared-rule Warsh fixture passes without
  Warsh rule code.

### PR 4 — mīm, general idghām, and lām shamsiyyah

**Changes**

- Implement ghunnah mushaddadah.
- Implement the exhaustive mīm-sākinah family: iẓhār, ikhfāʾ, idghām shafawī.
- Port mutamāthilayn, mutaqāribayn, and mutajānisayn pair logic from the
  current executable behavior into shared modules and reviewed Arabic pair
  tables.
- Represent kāmil/nāqiṣ as `IdghamOccurrence.completeness`, not separate rule
  ids.
- Implement lām shamsiyyah as an assimilation relationship.
- Cover muqaṭṭaʿāt cross-name interactions later through the same rules, not
  special mappings.

**Acceptance**

- Every current pair in `letter.py` and targeted occurrence evidence has a
  test and one target owner.
- No duplicated cross-word detector remains in projections.

### PR 5 — vowel carriers, boundaries, and recited writing

**Changes**

- Port alef/wāw/yāʾ/maqṣūrah carrier versus consonant versus silent logic.
- Realize `SmallVowel` dagger alef/mini wāw/mini yāʾ through the same semantic
  vowel segments while preserving their own grapheme attribution.
- Re-evaluate full wāw/yāʾ after waqf vowel removal so the immutable written
  letter can switch among consonant, carrier, leen, and silent realizations.
- Implement typed orthographic silence and long-vowel shared alignment.
- Implement hamzat al-waṣl, iltiqāʾ al-sākinayn, waqf, ibtidāʾ, tāʾ marbūṭah,
  and sakt boundary behavior as realization events.
- Add source-linked recited Arabic graphemes.
- Add `SOURCE_EXACT`, `RECITED_ARABIC`, and `RECITED_WITH_SILENT` Arabic render
  presets over the same stored source/recited graph. Options control inserted
  writing, silence, and compact/expanded lexical display; they never run
  rules.
- Replace the current `phonetic_text.py`, `silent.py`, and relevant
  character/letter mapping re-derivations with projections.
- Implement typed handlers for current boundary exceptions as they are ported.

**Acceptance**

- Wasl, starting, and stopping fixtures cover every current transform family.
- Full and small spellings of the same vowel share a segment shape but retain
  distinct source alignment; mini ṣilah vowels drop at waqf without mutating
  the canonical writing.
- Inserted, removed, shortened, carried, assimilated, and silent cases have
  explicit provenance.
- No view independently reconstructs waqf or ibtidāʾ.
- Waqf/ibtidāʾ realization runs before Tajwīd occurrence construction, and
  tests prove it can cancel/add/change cross-word, qalqalah, and madd
  occurrences.

### PR 6 — emphasis, qalqalah, and marked vowels

**Changes**

- Implement inherent tafkhīm, exhaustive rāʾ tafkhīm/tarqīq, and lām of Allah.
- Implement the concrete Hafs `RaaClassifier`; bind it in the Hafs Python
  pipeline. Add a Warsh classifier only with researched differing behavior.
- Implement qalqalah with typed sughrā/kubrā detail and attributed rendering.
- Have the Hafs adapter recognize the 11:41 `۪` marked-vowel sequence; have
  the Hafs classifier return `IMALA`; delete the location-keyed phoneme patch.
- Preserve Warsh marked-vowel inputs but reject pronunciation until its classifier
  is researched.

**Acceptance**

- Rāʾ receives exactly one heavy/light occurrence in supported contexts.
- The same `EmphasisOccurrence` variants and typed look-back reasons work with
  a fixture replacement classifier.
- Hafs imālah is representation-driven plus riwāyah classifier, not location
  hardcoding.

### PR 7 — madd, exceptions, and muqaṭṭaʿāt

**Changes**

- Classify the six supported madd types from semantic segments and boundaries;
  delete token-string `madd.py` rediscovery.
- Store `MaddOccurrence` inside the Tajwīd occurrence union. Store no
  duration/count and add no speculative types.
- Add typed causes plus `MaddContext` for ordinary, Allah dagger alef, waqf
  ʿiwaḍ, pronoun/plural-mīm ṣilah, and muqaṭṭaʿāt.
- Replace generic contextual pronunciation patch operations with named typed
  handlers and location data only where still needed.
- Reduce muqaṭṭaʿāt data to Arabic compact-letter → recited-spelling and feed
  the spelling through the normal pipeline.
- Remove hand-authored muqaṭṭaʿāt phonemes, segments, letter mappings, and
  Tajwīd mappings.
- Derive lāzim when a long-vowel/leen carrier is followed by a permanent sākin
  consonant, whether that consonant stays plain, is geminated/shaddah, or
  assimilates.
- Audit and test all fourteen letter names, all fourteen compact resource
  forms (30 source locations), all cross-name interactions, and the following
  Qurʾānic word. Keep typed Hafs exceptions for `يسٓ`, `نٓ`, and connected
  Āl ʿImrān `الم`→`اللَّهُ`.

**Acceptance**

- All six current madd classifications have fixtures and source/segment
  ownership.
- Every audited opening in `docs/internal-model-worked-examples.md`, including
  continued `طسٓ`→`تِلْكَ`, derives without segment arrays.
- No generic resource patch/effect language remains.

### PR 8 — clean API, switch, and old-pipeline removal

**Changes**

- Finalize public `Recitation` projections for text, recited text, tokens,
  grapheme/letter mapping, silence, Tajwīd, and madd.
- Decide each current method/export in `current-implementation-mapping.md`:
  retain as a thin projection, replace with the new API, or retire.
- Port text matching to the active source adapter and corpus.
- Remove mutable `symbols/` realization, global phoneme overrides/caches,
  string predicates used as domain state, old mapping re-derivers, generic
  contextual patches, and obsolete resource schemas.
- Run full Hafs semantic regressions and installed-artifact tests.
- Update README and quranic-phonemizer skill documentation.

**Acceptance**

- Every current capability is represented, intentionally redesigned, or
  explicitly retired—none is lost accidentally.
- Projections contain no rule logic or token-string inference.
- The old pipeline can be deleted completely; there is one source of truth.

### PR 9 — Warsh linguistic matrix and implementation

This work starts with research, not YAML scaffolding.

For each candidate family record:

| Field | Requirement |
|---|---|
| canonical phenomenon | conventional name and whether it is Tajwīd, madd, realization, or script |
| Hafs behavior | current canonical input/output |
| Warsh behavior | same/different with reviewed source |
| source representation | exact Warsh sequences and whether they are hints |
| relationship | occurrence variant, subject/result, and its typed trigger/reason/target fields |
| implementation owner | shared code/table, Warsh source adapter, Warsh classifier, render override, or exception |
| tests | location, boundary state, expected segments/occurrences |

Research order:

1. `۪` marked vowels and imālah/taqlīl;
2. plural mīm/small wāw;
3. stop signs and boundary behavior;
4. hamza, naql, tashīl/ibdāl;
5. rāʾ/lām and madd deltas;
6. waqf/ibtidāʾ, muqaṭṭaʿāt, and closed exceptions;
7. minority unresolved script sequences.

Implement shared cases first. Add a Warsh classifier/table only for a proved
difference. The complete Warsh feature is done only when every accepted
runtime sequence and rule behavior has a fixture and source.

## PR #37 disposition

Keep as intake evidence/source material:

- selected King Fahd raw source and Warsh font provenance;
- canonical word corpus direction;
- parameterized DB-builder intent;
- Unicode/font comparison utilities.

Rework before integration:

- metadata meanings corrected by the codepoint audit;
- generic block validator becomes semantic inventory validation;
- generic flagged-character stripping becomes manifest transforms;
- raw/font/research artifacts move outside runtime package data;
- structural word/address policy becomes explicit;
- unrelated formatting changes to shared phoneme/muqattaʿāt YAML are dropped.

## Final architecture test

Every observed Hafs/Warsh difference must have exactly one owner:

1. corpus/address/build difference;
2. source-script normalization difference;
3. shared rule/table input;
4. genuine riwāyah classifier/table/render/exception delta.

If two owners both need to "fix" the same difference, the boundary is wrong.
If none owns it, implementation is not ready for that case.
