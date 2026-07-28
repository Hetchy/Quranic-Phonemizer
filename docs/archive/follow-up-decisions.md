# Follow-up decisions from the second adversarial review

> **Archived 2026-07-26.** Historical record only — do not read this as a
> description of the current codebase or of the accepted design. A new ADR
> set is being written to supersede it.
>
> Reason: records decisions folded into ADR-001-003, which are themselves
> archived.

Status: decisions incorporated into ADR-001–003, the integration plan, and
`docs/tajweed-model.md`.

## 1. Can `LetterUnit` silently contain a non-script/implicit letter?

No. `LetterUnit` is now source-only and requires non-empty base
`GraphemeId`s from one source cluster. Only the source adapter constructs it.

Inserted sounds, phonetic Arabic additions, and muqaṭṭaʿāt expansion use
`RecitedLetter`. A recited letter must point either to source `LetterUnit`s or
to exactly one `RealizationEvent`. This allows implicit writing, but never
implicitly and never by pretending it occurred in the mushaf.

`RecitedWord` is also first-class: ordinary words map one-to-one, while a
compact opening can expand into several joined recited words. This is required
to distinguish same-name madd causes from rules across names and from the
boundary to the following Qurʾānic word.

## 2. Rename `ShortVowel` to `Harakah` and include sukūn?

Yes. `HarakahKind` is `FATHA | DAMMA | KASRA | SUKUN`.

Sukūn is not a vowel, so `ShortVowel` was the wrong type name. `Harakah` is the
conventional orthographic category and preserves the important distinction
between an explicit sukūn and an orthographically bare letter. `Tanween` and
`SmallVowel` remain separate first-class values.

## 3. Can render options replace the current display workarounds?

Yes, provided rendering only selects already-derived facts.

- `SOURCE_EXACT`: exact source, compact muqaṭṭaʿāt, source silence retained,
  inserted writing omitted.
- `RECITED_ARABIC`: expanded muqaṭṭaʿāt, inserted writing included, silent
  source writing omitted, selected waqf/ibtidāʾ realization applied.
- `RECITED_WITH_SILENT`: the same recited view with silent writing retained for
  inspection/highlighting.

The old `phonetic_text.py` becomes the `RECITED_ARABIC` projection. The
renderer does not decide hamzat al-waṣl, silence, ʿiwaḍ, lexical expansion, or
waqf; `RealizationEvent`s and alignments already decided them.

A dedicated source serializer must reconstruct the loaded text and UTF-8 bytes
from ordered `Grapheme`s. `SOURCE_EXACT` must match it as an integration test,
but round-trip success proves tokenization/source preservation, not phonology.

## 4. Why is `Riwayah` not an enum?

It is now a Python 3.11 `StrEnum` with `HAFS` and `WARSH`. Supporting another
riwāyah requires code, resources, research, and tests, so extending the enum is
clearer than a speculative plugin identity registry. There are no qirāʾah or
ṭarīq fields.

## 5. What did `TajweedOccurrence.condition` mean?

It was under-specified and has been removed.

The model now uses a small tagged union:

- `NoonOccurrence`: trigger kind, following recited letter, optional target;
- `MeemOccurrence`: following recited letter, optional target;
- `IdghamOccurrence`: required target and completeness;
- `QalqalahOccurrence`: degree and boundary;
- `EmphasisOccurrence`: a typed direct/look-back/Allah reason;
- `MaddOccurrence`: type, carrier, typed cause, and context.

For ikhfāʾ and iqlāb, `following` explains the trigger and `target=None`. For
idghām, the assimilating target is required. Complex rāʾ cases store a tagged
reason such as `SakinAfterSakinReason` or `WaqfLookbackReason`, including the
actual letters/harakah/boundary inspected. These records explain a completed
decision; they are not executable condition trees or YAML logic.

## 6. Why was madd outside Tajwīd?

It should not have been outside. Madd has different fields, but that justifies
a specialized union variant, not a parallel top-level annotation collection.
`MaddOccurrence` is now one `TajweedOccurrence` variant. A madd-only API filters
the one occurrence collection.

Composition is preferable to inheritance here: a common occurrence identity
and result contract, plus family records with the fields they actually need.

## 7. How are Allah dagger alef, ʿiwaḍ, and ṣilah represented?

`MaddType` and `MaddContext` are separate axes.

| Example | Type | Context |
|---|---|---|
| ordinary long vowel | ṭabīʿī or another derived type | ordinary |
| implicit dagger alef in Allah | usually ṭabīʿī | Allah dagger alef |
| fathatan transformed at waqf | ṭabīʿī in the current six-type projection | waqf ʿiwaḍ |
| pronoun hāʾ before a non-hamza | derived from resulting vowel | pronoun-hāʾ ṣilah |
| pronoun hāʾ before hamza | jāʾiz munfaṣil where applicable | pronoun-hāʾ ṣilah |
| Warsh plural-mīm candidate | not enabled before research | plural-mīm ṣilah |
| three-letter opening name | lāzim | muqaṭṭaʿāt |

Thus ṣilah is not itself forced into the madd-type enum, and sughrā/kubrā are
not speculative types. The context still remains queryable.

## 8. Can waqf/ibtidāʾ add, remove, or change Tajwīd?

Yes. Boundary resolution and realization run before occurrence construction.
The selected realization can:

- cancel cross-boundary nūn/mīm/idghām rules;
- create qalqalah kubrā;
- create ʿāriḍ li-s-sukūn or leen;
- create the long vowel and madd context for ʿiwaḍ;
- change wāw/yāʾ between consonant, carrier, semivowel, and silence;
- pronounce or silence hamzat al-waṣl.

The result stores only rules valid for that selected request. It does not
derive a wasl rule and later mark it deleted.

## 9. Does madd lāzim derive for all muqaṭṭaʿāt?

The classifier is changed from today’s token check (“next token is a shaddah
or ghunnah token”) to the semantic rule:

```text
long-vowel/leen carrier + following permanent sākin consonant in the same
lexical name => madd lāzim
```

The following consonant can stay plain, be the sākin half of a shaddah, or
assimilate into the next name. `PermanentSukunRealization` records
`PLAIN/GEMINATED/ASSIMILATED`; the latter two supply the conventional
`muthaqqal` detail and plain supplies `mukhaffaf`. `عَيْنْ` keeps its leen carrier shape
while the supported classification remains lāzim.

The full fourteen-name/fourteen-form/30-location audit and the next-word cases
are in `docs/internal-model-worked-examples.md`.

## 10. What replaces the proposed `evidence/` tree?

There is no top-level `evidence/` tree.

- stable decisions and source-convention conclusions: `docs/` and
  `docs/script-conventions/`;
- small executable cases: `tests/fixtures/`;
- phonemizer-related source material, screenshots, bulk occurrence lists:
  `research/phonemizer/`;
- pure Qurʾānic research unrelated to package behavior:
  `research/quranic-studies/`;
- reproducible generated outputs/reports: ignored `build/`.

The generic `dev/` bucket is still removed, but material is moved by purpose.

## 11. What is the concrete role of `RulePolicies`?

There was no concrete second implementation to justify it, so it is removed
from the model and plan.

Shared rule code stays in `rules/`. Hafs binds its concrete classifiers in a
Hafs pipeline constructor. If research proves Warsh rāʾ differs, a concrete
`classify_warsh_raa` is added and bound by the Warsh constructor. Both return
the same decision type and the shared builder creates the same
`EmphasisOccurrence`. Unknown Warsh behavior raises unsupported rather than
silently inheriting Hafs.

This is ordinary typed Python composition, not a generic policy framework or
a YAML function-name registry.

## 12. Can all phoneme rendering be expressed with maps?

All **output token selection** can be mapped from semantic segment features.
For example, plain/geminated/nasalized wāw and yāʾ can map to `w`, `ww`, `w̃`
and `j`, `jj`, `j̃`. A qalqalah release can also map to `Q`; it does not need a
special renderer algorithm.

Rule selection cannot safely be mapped from written states such as “nūn with
no sukūn.” Today’s Hafs code relies on that script shortcut, but:

- explicit sukūn and a bare letter are distinct source facts that can both
  represent semantic sākin state in reviewed conventions;
- nūn/tanween and mīm depend on the following effective letter and boundary;
- nasalized `w/j` depends on a preceding assimilated subject;
- rāʾ needs multi-letter look-back and can change at waqf;
- wāw/yāʾ can switch role at waqf.

The recommended split is therefore:

```text
Arabic glyph map -> baseline consonant/vowel identity
typed Python rules -> semantic features and occurrences
semantic render map -> final token string(s)
```

## 13. Are Hafs and Warsh mostly the same Unicode?

Mostly for ordinary inventory, yes; merely “count deltas,” no.

The selected Warsh word corpus has 63 scalar values and 57 also occur in the
current Hafs corpus. Its six unique scalars are combining hamza below, three
alternate tanween marks, yeh barree, and mini mīm above. Many differences are
many-to-one normalization.

However, important frequent differences are sequence-level: Warsh has no Hafs
`U+0671` hamzat-al-waṣl scalar, `U+06EA/U+06EC/U+06DF` are context/source
dependent, harakah+mini-mīm composes tanween, shared small-wāw/maddah patterns
contain a likely plural-mīm delta, and structural/stop attachment affects
addresses and boundaries. The accurate conclusion is “mostly shared ordinary
scalars, small scalar delta, significant convention/sequence delta.”

## 14. Is the plan implementation-ready now?

The Hafs internal-model refactor and the accepted Warsh source-normalization
subset are implementation-ready after these changes. The worked examples now
exercise the object relationships rather than only naming them.

A complete Warsh phonemizer remains intentionally not ready until Warsh
pronunciation, marked vowels, plural mīm, stop conventions, hamza behavior,
and other rule deltas have reviewed sources and fixtures.
