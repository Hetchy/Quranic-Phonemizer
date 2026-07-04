# ADR-002: Model invariants, code rules, and hygiene

Status: **proposed** — companion to ADR-001 (v2). ADR-001 defines the shapes;
this document defines the discipline that keeps them honest. Rules are
organized by *how they are enforced*: by construction (illegal states
unrepresentable), by validation (checked on every frozen `Recitation`), and
by CI/lint (code rules). §E ranks them by impact.

---

## A. By construction — illegal states unrepresentable

**A1. Every deviation is explained.** A segment may differ from its letter's
default realization *only* via a builder mutation, and every builder mutation
requires a `RuleApplication` argument — `Builder.set/delete/insert` have no
application-less form. The model becomes a self-documenting audit trail:
"why does this sound this way?" is always answerable, and silent drift from
the domain is structurally impossible.

**A2. Detectors can't cheat.** Signature-locked
`(Builder, RiwayaSpec) -> None`. Detectors receive the Builder, never the
`Recitation`; they never import each other; they never see render tables
(phonology must not condition on output tokens). The registry is frozen at
import time.

**A3. No module-level mutable state.** Today's `set_phoneme_override`
globals die; runtime overrides become fields on a derived `RiwayaSpec`.
`phonemize(spec, corpus, ref, stops)` is a pure function — which also makes
concurrent multi-riwaya use trivially safe.

**A4. Enum vs registry split** (the nuance in "enum everything"):
- `StrEnum` for **closed domain vocabularies**: `GraphemeKind`, `Boundary`,
  application `kind`s, `OverrideCondition`, `MaddType`, `LetterId` (the
  alphabet + hamza-wasl is closed).
- `NewType` + **load-time registry validation** for **open,
  riwaya-extensible vocabularies**: `RuleId`, `ConsonantId`, `VowelQuality`.
  Enum-ing these would require a Python release to add a Warsh rule,
  defeating the data seam.
- `NewType` all integer ids (`GraphemeId`, `SegmentId`, `WordIndex`) so an
  index mixup is a type error.

**A5. Pydantic posture:** `frozen=True` and `extra="forbid"` on every model;
no `Optional` field except the documented ones (`Consonant.ident=None` =
placeless nasal; `Grapheme.display`). No default value may encode a domain
fact — counts, lengths, and trigger outcomes always flow from data; Python
defaults are structural falsy only.

**A6. Shaddah accounting (decision).** The shaddah grapheme is included in
the geminate segment's `spelling`. This makes coverage (B1) total with no
carve-out, and gives the letter view its composed `بّ` for free.

**A7. Make defaults explicit (decision).** Emit `Annotation(rule="izhar")`
for every izhar and `Madd(tabii)` for every natural long vowel — never
"absence of a rule means X". Costs a few thousand cheap objects; buys the
exactly-one invariants (B6) and kills the pattern that caused today's
continuing-tanween-alef attribution gap. Both A6 and A7 change output
counts, so they must be decided **before** the characterization net locks.

---

## B. Recitation invariants — `validate()`

Run always in tests and property-based suites; opt-in in production.

Structural:

- **B1. Total coverage.** Every grapheme is (a) in some segment's spelling,
  **xor** (b) named by exactly one `Silence`, **xor** (c) of an inherently
  non-sounding kind (`STOP_SIGN`, `SILENCE_MARK`, `MARK`). No unexplained
  silence, no double-accounting. (The silent-letter audit's Check A,
  generalized to the whole model.)
- **B2. Id coherence.** `graphemes[i].id == i`, `segments[i].id == i`; every
  id in spellings and applications resolves; spelling tuples are in reading
  order with no duplicates.
- **B3. Stream order.** `segment.word` is non-decreasing; every spelling
  grapheme belongs to `segment.word` or an adjacent word (cross-word spans
  have width ≤ 1).
- **B4. Insertion coherence.** `spelling == ()` ⟺ an `Insertion` names the
  segment (both directions).
- **B5. Kind agreement.** `Madd.segment` is a Vowel or a w/j Consonant;
  `Assimilation.target` is geminate unless `complete=False`;
  `Substitution.grapheme` is in some spelling or named by a `Silence`.

Domain (each catches a real detector-bug class):

- **B6. Exactly-one-per-family.** Every bare noon/tanween trigger has
  exactly one noon-family application; every long Vowel exactly one `Madd`;
  every raa and isti'laa consonant exactly one tafkheem/tarqeeq annotation.
  Catches a detector skipping a site or double-firing.
- **B7. Feature justification.** `geminate=True` ⟹ shaddah in spelling or
  an `Assimilation` targets it. `ident=None` ⟹ `nasal=True` and a
  `Substitution` explains it. Emphatic vowel ⟹ emphatic adjacent consonant
  or an explaining annotation.
- **B8. Boundary discipline.** No application or spelling spans a stopping
  or sakt boundary. A stopping word's last sounding segment is not a short
  Vowel (golden rule 1). A starting word's first segment is a Consonant and
  not geminate (golden rule 2 + ibtidaa shaddah drop).
- **B9. Cross-traversal stability.** For the same ref, the wasl and waqf
  Recitations have identical `graphemes` arrays (same ids), so consumers can
  diff traversals by id. Tested explicitly.
- **B10. Render totality.** Every segment renders under both full and simple
  tables. Enforced stronger at *spec load*: the render table must cover the
  full producible feature lattice, so this can never fail per-recitation.

---

## C. Code rules — CI/lint enforced

- **C1. The literal gate.** A lint script failing on any Arabic-block
  codepoint (U+0600–06FF and friends), IPA-block character, or
  `\d+:\d+:\d+` location literal in `*.py` outside `tests/`. Resources are
  the only home for domain bytes. (Concretizes the Epic 3a acceptance gate.)
- **C2. No string surgery on model values.** Model fields are never
  sliced/concatenated/`in`-tested outside the render module (the
  `":" in ph` sin class). Greppable rule + review checklist.
- **C3. Layering, enforced by import-linter.** `model` imports nothing local
  ← `builder` ← `detectors`; `render` and `projections` import `model` +
  spec only; `riwaya` composes all. No cycles — and *projections cannot
  import detectors*: a projection needing a detector means the model is
  missing a fact.
- **C4. Exhaustiveness.** Every `match` over an enum or discriminated union
  ends in `assert_never`; pyright/mypy strict in CI. A new segment or
  application kind then breaks every switch that must handle it — that is
  the point.
- **C5. Data schema validation at load.** Every YAML parses into its
  Pydantic spec with `extra="forbid"`, failing with file+key on error. A
  typo'd trigger-set key must be a startup crash, never a silent no-op
  (today's exact failure mode for a second riwaya).
- **C6. Traceability matrix.** Every numbered fact in `domain-facts.md` maps
  to at least one test id; every detector's table-driven tests cite their §.
  CI fails on unmapped facts — the domain doc becomes a checklist, not prose.
- **C7. Oracles in CI.** The Hafs characterization net (byte-identical
  gate); `Recitation` JSON round-trip losslessness; property-based tests
  (random refs × stop selections) asserting the B-invariants; a perf
  benchmark (full-Quran phonemize, fail on >20% regression — we are
  replacing hand-optimized code).
- **C8. Deterministic serialization.** `rules` sorted by a canonical key at
  freeze; `schema_version` on `Recitation` from day one.
- **C9. Naming glossary.** One doc mapping Arabic terms → canonical rule-id
  spellings (Arabic terms for rule ids — idgham, not assimilation; English
  reserved for effect verbs / class names). Prevents `ikhfa`/`ikhfaa`
  drift across data files.
- **C10. Error and I/O policy.** Unknown codepoint at tokenize = hard error
  (ties into the Epic 1a validator). No detector or builder performs I/O;
  specs are loaded once and injected.

---

## D. Small decisions to record now

- **D1.** A6 (shaddah-in-spelling) and A7 (explicit izhar/tabii) — decide
  before the characterization net locks, since both change output counts.
- **D2.** Skeleton normalization is **one data-driven function**
  (`graphemes → tuple[LetterId]`) shared by the override matcher and any
  future search — never re-implemented per table.
- **D3.** The Builder may record an optional **pass-by-pass trace** (which
  detector did what) for debugging — nearly free given A1, painful to
  retrofit.
- **D4.** Khilaf (dual-valid readings) are `Annotation`s with explicit rule
  ids — never alternate outputs.

---

## E. Priority — what to adopt first

Not everything above is equal. Ranked by impact:

**Tier 1 — load-bearing; the redesign fails without them.**
- **A1** (no mutation without an application) and **B1** (total grapheme
  coverage). Together they guarantee the model can never silently drift
  from the domain — which is the failure mode this entire redesign exists
  to end. Everything else is defense in depth.
- **C7's characterization net + B10/render-totality-at-load** — ADR-001's
  ranked risk #1 is render-table fidelity; these are its only proof.

**Tier 2 — cheap now, expensive to retrofit; adopt at first commit.**
- **A3** (purity / no globals), **A5** (frozen + forbid + no domain
  defaults), **C3** (layering) — architectural properties that are one-line
  decisions on day one and rewrites later.
- **D1** (shaddah-in-spelling, explicit izhar/tabii) — must precede the net.
- **C1** (literal gate) — already an Epic 3a acceptance item; wire it early
  so violations never accumulate.

**Tier 3 — high value, adopt during build-out.**
- **B6–B8** (exactly-one, feature justification, boundary discipline) — the
  invariants that actually catch detector bugs; grow them alongside the
  detectors they check.
- **A4** (enum/registry split) and **C4** (exhaustiveness) — the typing
  discipline that makes extension safe.
- **C5** (spec validation at load), **C6** (traceability matrix).

**Tier 4 — worthwhile polish; schedule, don't block on.**
- B2–B5, B9 structural checks beyond coverage; C2, C8, C9, C10; D2–D4;
  property-based testing and the perf benchmark (add once the net is green).

Rule of thumb embedded in the ranking: prefer **unrepresentable** over
**validated** over **linted** — each tier down catches the same bug later
and more expensively.
