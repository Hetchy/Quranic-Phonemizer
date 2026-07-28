# ADR-002: Invariants, typing, and migration gates

> **Archived 2026-07-26.** Historical record only — do not read this as a
> description of the current codebase or of the accepted design. A new ADR
> set is being written to supersede it.
>
> Reason: companion to ADR-001; its migration gates were written against a
> target model that was only partially implemented.

Status: **accepted for implementation** — companion to ADR-001.

## 1. Typing conventions

The package targets Python 3.11 or newer. The first implementation change
raises `requires-python` and CI accordingly; the current `>=3.8` metadata is
already false because production code uses newer syntax.

Use `StrEnum` for closed domain vocabularies which code branches on or exposes:

- supported riwāyāt;
- canonical Arabic letters and marks;
- segment qualities/features;
- alignment kinds;
- Tajwīd rules and typed details;
- madd types, boundary kinds, and realization reasons.

Use validated strings for non-domain resource identities:

- corpus and source-script ids;
- renderer/preset ids.

Arabic-letter enum values are the glyphs themselves. YAML uses Arabic glyph
keys/strings, not redundant `ba`, `lam`, `raa` identifiers. Code may use
readable enum member names such as `Letter.BAA`; serialized script data stays
glyph-first.

Arbitrary strings never drive control flow. Values such as `effect: keep`,
`merge_plain`, `nasalize`, or a Python function name in YAML are rejected.

Use `NewType` only for ids whose accidental mixing is plausible: grapheme,
letter-unit, segment, Tajwīd occurrence, and realization-event ids. Frozen
slotted dataclasses are the final model; small mutable slotted builders are
allowed during realization. No free-form metadata dictionaries exist.

## 2. Construction invariants

### I1. Exact source preservation

Concatenating source graphemes in order reproduces the loaded source word text
exactly. Normalization never overwrites, NFC-normalizes, silently strips, or
reorders the source layer.

### I2. Source-script accountability

Every scalar in a runtime corpus is recognized as a base, combining mark,
formatting/attachment mark, stop/structural sign, or explicit source-build
artifact. Arabic-block membership and font coverage are not semantic
validation.

Every sequence whose canonical interpretation is source-specific has a
fixture containing riwāyah, location, raw string/codepoints, expected
`LetterUnit`, and review status. Contextual scalars such as `۪`, `۟`, and `۬`
cannot be registered with one global meaning.

### I3. Letter-unit coverage

Every sounding or potentially sounding grapheme belongs to exactly one
canonical `LetterUnit`. Structural signs do not become letters. A combining
mark does not become a letter because its Unicode name contains "ALEF" or
"HAMZA". A multi-scalar source sequence may form one unit. Every `LetterUnit`
has non-empty base source graphemes; inserted/expanded writing is represented
only by a provenance-bearing `RecitedLetter` created by a
`RealizationEvent`.

### I4. One alignment per source grapheme

Every grapheme has exactly one `GraphemeAlignment`. Audible segments are
linked through `REALIZES`, `CARRIES`, or `ASSIMILATED`; silence has a typed
cause; hints and structural marks are explicit. No projection guesses silence
from an empty phoneme list.

### I5. Every recited unit and sound has provenance

Every `RecitedLetter` is copied from source `LetterUnit`s or created by exactly
one `RealizationEvent`. Every segment either participates in at least one
alignment or was inserted by one event. Cross-word shared segments may align
to graphemes in both words. No relation crosses a stopping boundary.

Every `RecitedLetter` belongs to exactly one `RecitedWord`. An ordinary source
word produces one recited word; lexical expansion may produce several. There
are exactly `len(recited_words) + 1` `RecitedBoundary` records, including
request edges. Expanded-name boundaries are joined and the final name inherits
the source/request boundary.

### I6. References and order are valid

Ids equal array positions, all references resolve, word ownership is explicit,
and reading order is monotonic except for a documented shared/inserted
realization. The final aggregate is immutable.

### I7. One domain decision, many projections

Tajwīd relationships, madd classifications, alignments, silence causes,
boundary decisions, and recited-writing transforms are recorded once. A
public projection may group or serialize them but may not invoke a detector or
inspect token spelling to rediscover them.

### I8. Render attribution

Every rendered token points to its segment(s), and every audible segment
renders at least one full-mode token. Word/global token indices are projection
values, not model fields. Simple output is another renderer/presentation over
the same segments.

### I9. Recited-writing provenance

Every recited Arabic grapheme points to source graphemes or one realization
event. Muqaṭṭaʿāt expansion maps each recited name to its compact source
letter. The exact source remains independently reconstructable.

### I10. Riwāyah isolation

Corpus/address data, source adapter, searchable-text normalization,
exceptions, pipeline construction, render configuration, and caches are keyed by immutable
riwāyah/config identity. Hafs→Warsh and Warsh→Hafs construction order produces
the same isolated results.

## 3. Tajwīd invariants

### T1. Conventional names

Every non-madd `OccurrenceCore.rule` and every `MaddOccurrence.madd_type` is a
conventional Tajwīd phenomenon.
Orthographic silence, hamzat-al-waṣl vowel choice, `keep`, and `replace` are
not Tajwīd ids. Madd is represented by the specialized `MaddOccurrence`
variant of `TajweedOccurrence`.

### T2. Relationship semantics

- every occurrence has a typed variant and a subject;
- each variant names its rule-specific trigger/reason fields;
- target is present only for actual assimilation;
- result references the realized sound;
- no generic `condition` tuple or free-form detail dictionary exists.

Tests must cover ikhfāʾ (following trigger, no target), iqlāb, idghām with and without
ghunnah (real target), shafawī rules, general idghām, qalqalah, tafkhīm, and
tarqīq, including cross-word ownership.

### T3. Exhaustive family decisions

Nūn/tanwīn has exactly one of iẓhār ḥalqī, ikhfāʾ ḥaqīqī, iqlāb, idghām
bi-ghunnah, or idghām bilā-ghunnah when the required context is present.
Mīm sākinah has exactly one of iẓhār, ikhfāʾ, or idghām shafawī. Rāʾ receives
exactly one of tafkhīm or tarqīq. Stopping boundaries cancel cross-boundary
decisions before these families are evaluated.

### T4. Trigger/detail is not rule identity

Nūn sākinah versus tanween is `NoonOccurrence.trigger`; kāmil versus nāqiṣ is
`IdghamOccurrence.completeness`; sughrā versus kubrā is
`QalqalahOccurrence.degree`. Invalid rule/variant combinations fail at
occurrence construction.

### T5. Madd scope

Every supported long-vowel/leen site has at most one `MaddOccurrence` for the
current realization. The record stores type, segment(s), carrier, typed cause,
and orthogonal context such as Allah dagger alef, ʿiwaḍ, ṣilah, or
muqaṭṭaʿāt; never performance duration/count. New types require a real
riwāyah behavior, API need, and tests.

## 4. Dependency boundaries

```text
model
  <- source adapters
  <- lexical expansion + corpus/request/boundary resolver
  <- boundary/structural realization
  <- baseline segment builder
  <- shared rules + explicit riwāyah pipeline wiring
  <- renderer and public projections
```

- `rules/` sees canonical letters/marks, boundaries, and segments; it never
  sees raw source glyph conventions or output tokens.
- `script/` is the only package allowed to interpret source-specific Unicode
  sequences.
- `render/` is the only package allowed to assign output token strings.
- `riwayat/<id>/rules.py` contains only proven classifier replacements; shared
  modules do not import riwāyah modules.
- rules and projections perform no file I/O.
- runtime configuration is immutable and instance-local.

A targeted lint may prohibit raw Arabic source literals and IPA-like token
literals in shared `rules/`. A repository-wide ban is wrong: adapters,
glyph-first data, fixtures, docs, and tests legitimately contain Arabic.

## 5. Resource/build validation

At runtime-data load:

1. the riwāyah id and referenced corpus/script/render ids agree;
2. all files exist and declare a supported schema version;
3. every glyph key is exactly one intended scalar or an explicitly allowed
   sequence;
4. glyph keys convert to known canonical enums where required;
5. finite family sets are complete/disjoint when the domain says they are;
6. a riwāyah replacement table replaces one whole named family, never a deep
   merge of ambiguous fragments;
7. exception locations exist in that riwāyah corpus;
8. duplicate keys and unknown fields fail.

At corpus build:

1. raw input, licence/provenance, and hash are recorded;
2. every removal/replacement is in a transformation manifest with counts;
3. structural tokens are removed from lexical addressing deliberately;
4. the normalized editable corpus, packed database, and address index are
   reproducible;
5. the generated codepoint report has no unknown/unreviewed runtime scalar.

## 6. Migration gates

Exact legacy schema parity is not required. Semantic coverage is.

### Gate A — behavior inventory

Keep today's full-surah flat mappings, targeted Tajwīd suite, silent tests, and
audited module map as an executable behavior inventory. Add missing fixtures
for phoneme output, cross-word ownership, waqf/ibtidāʾ, character mapping,
phonetic Arabic, text matching, muqaṭṭaʿāt, contextual exceptions, and all six
madd classifications.

For each existing output field/method, decide explicitly: represented by the
new aggregate, retained as a thin projection, redesigned, or retired. Known
bugs are fixed rather than enshrined.

### Gate B — source normalization

Commit a Hafs fixture for every accepted source family and a Warsh fixture for
every family allowed by `warsh-script-codepoint-audit.md`. Unknown or
unreviewed Warsh sequences fail closed. Prove at least one different-byte,
same-canonical case end to end.

### Gate C — vertical Tajwīd slice

Implement nūn/tanwīn through source graphemes, units, baseline segments,
occurrences, alignments, rendering, silence, and the new mapping API. It must
exercise within-word, cross-word, stop cancellation, all five family outcomes,
and both nūn/tanween details.

### Gate D — representation slices

Before porting every rule, prove:

- source serializer and `SOURCE_EXACT` renderer reconstruct every Hafs source
  word byte-for-byte and the accepted Warsh normalization fixture bytes;
- one waqf/ibtidāʾ transform with recited-writing provenance;
- that the same boundary transform removes/adds the expected cross-word,
  qalqalah, and madd occurrences before rendering;
- one qalqalah result which renders multiple/configured tokens;
- one inserted sound;
- one long vowel with haraka+carrier sharing;
- every one of the fourteen muqaṭṭaʿāt names derived solely from Arabic
  recited spelling, plus all fourteen compact opening forms and their next-word
  boundary cases from the worked-example audit.

### Gate E — full Hafs semantic migration

Every implemented behavior in the audit map has a new owner and regression
test. Projections contain no rule detectors. Only then switch Hafs to the new
pipeline and remove the old mutable graph/re-derivers.

### Gate F — installed-artifact proof

Build wheel and sdist, install each in a clean environment, and run Hafs plus
Warsh-normalization smoke tests. Runtime code must not depend on `dev/`,
`research/`, `build/`, `docs/`, or repository-relative paths.

### Gate G — Warsh pronunciation

For every implemented Warsh delta, require a reviewed source, canonical input,
expected segment change, expected occurrence/realization, and test. Script
difference alone never authorizes a rule fork.

## 7. Implementation readiness

The Hafs refactor and the proved Warsh source-adapter subset are ready to
implement after these ADRs. A complete Warsh phonemizer is not: stop-sign
semantics, marked-vowel interpretation, plural-mīm realization, and other
riwāyah-specific rules still need research. The code must represent those
unknowns without guessing them.
