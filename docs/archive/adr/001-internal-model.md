# ADR-001: Canonical internal model for multiple riwāyāt

> **Archived 2026-07-26.** Historical record only — do not read this as a
> description of the current codebase or of the accepted design. A new ADR
> set is being written to supersede it.
>
> Reason: only layers 1, 2 and 4 of its six-layer model reached the code at
> `e0d9fb9`. Alignment, recited writing, and Tajweed occurrences were never
> built, and the landed package tree differs from the one described here.

Status: **accepted for implementation** for the Hafs refactor and Warsh script
normalization. Warsh pronunciation remains gated by research identified in the
integration plan.

Companions:

- `docs/tajweed-model.md` is the concrete type and occurrence contract.
- `research/warsh/warsh-script-codepoint-audit.md` is the source-encoding evidence.
- ADR-002 defines invariants and migration gates.
- ADR-003 defines code, runtime-data, build, evidence, and research ownership.

## 1. Decision

Replace the mutable `LetterSymbol`/neighbour-mutation pipeline with one
utterance result containing six connected layers:

1. exact source `Grapheme`s;
2. source-normalized, source-only `LetterUnit`s;
3. provenance-bearing `RecitedWord`/`RecitedLetter`s after lexical/boundary
   realization;
4. realized sound `Segment`s;
5. explicit grapheme-to-segment `Alignment`s;
6. stored Tajwīd (including madd), realization, recited-writing, and
   rendered-token facts.

Each result belongs to one `Riwayah` enum value (`hafs` or `warsh`). Adding a
supported riwāyah extends the enum, resources, implementation, and tests. The
model has no qirāʾah or ṭarīq fields.

The new API may be clean rather than shape-compatible with every existing
mapping DTO. Existing outputs are evidence for behavior which must be mapped
or deliberately retired, not schemas which dictate the new internal model.

## 2. Why the layers are separate

### Exact source

The loaded corpus must remain byte-reconstructable. Normalization never edits
the source sequence. This preserves codepoint attribution, orthographic hints,
stop signs, and corpus provenance.

### Canonical spelling

Rules cannot operate directly on source scalars. PR #37 proves that:

- Hafs `ٱ` and several Warsh initial-alef sequences can represent hamzat
  al-waṣl;
- Warsh uses three nonstandard Unicode marks for the three tanween values;
- `۪`, `۟`, and `۬` are context-dependent and cannot have one global meaning;
- Warsh yeh barree frequently corresponds to Hafs alef maqṣūrah/yāʾ family.

Each source adapter tokenizes grapheme clusters and emits canonical
`LetterUnit`s composed with first-class `Harakah` (including sukūn), `Tanween`,
`SmallVowel`, shaddah, and orthographic-hint values. Dagger alef and mini wāw/yāʾ are
`SmallVowel`s, not a generic modifier category. Shared rule code starts at this
boundary and never inspects raw script glyphs.

Normalization is many-to-one: several tanween scalars and a reviewed
harakah+mini-mīm composition can all produce one canonical `Tanween`. It is
also sequence-sensitive: the same scalar may normalize differently in
different clusters. Exact `Grapheme`s always preserve which source convention
was written.

### Sound

Rules work on typed consonant/vowel segments, not token strings. A segment can
carry gemination, nasalization/hidden realization, emphasis, qalqalah, vowel
quality, and vowel length. Output strings exist only in the renderer.

### Recited writing

`LetterUnit` never represents a manually inserted/non-script letter: its base
source graphemes are non-empty. Ordinary realization copies its canonical
form into a `RecitedLetter`; lexical expansion and implicit sounds create
`RecitedLetter`s only through a typed `RealizationEvent`. Rules consume this
recited stream, which lets expanded muqaṭṭaʿāt use the ordinary rule pipeline
without falsifying source provenance. `RecitedWord` distinguishes each
expanded letter name and owns the join/stop/sakt boundaries used by rules.

### Alignment

Every source grapheme has one typed relationship to sound: realizes, carries,
assimilated, silent, orthographic hint, or structural. Many graphemes may
share one segment and one grapheme may contribute to multiple segments.

This relation is required, not optional metadata. It is what makes letter and
character mapping, silent-letter explanation, cross-word mergers, long-vowel
ownership, and Tajwīd highlighting simple projections rather than separate
detectors.

### Occurrences and derived writing

The builder records named Tajwīd occurrences (including specialized madd
occurrences) and
non-Tajwīd realization events while it knows why the sound changed. It also
records source-linked recited Arabic graphemes for waqf/ibtidāʾ and lexical
expansion. Rendered tokens point to segment ids.

## 3. Identity and configuration

```python
@dataclass(frozen=True, slots=True)
class RiwayahResources:
    riwayah: Riwayah
    corpus: CorpusSpec
    script: ScriptAdapter
    render: RenderConfig
```

`Riwayah` is a Python 3.11 `StrEnum`. This package is not a plugin registry;
supporting a riwāyah requires code, domain fixtures, and packaged resources,
so a closed enum is the simpler honest contract. Other closed linguistic
concepts—letters, harakāt, vowel qualities, small-vowel kinds, rule names,
alignment kinds, madd types—also use `StrEnum`.

Corpus, address metadata, searchable-text normalization, script adapter,
exceptions, pipeline construction, render configuration, and caches are instance-local
or keyed by immutable riwāyah/config identity. Hafs and Warsh must coexist in
one process without global overrides.

A reference such as `2:255:3` is interpreted in the active riwāyah corpus. No
assumption is made that two corpora have the same verse numbering or word
shape.

## 4. Tajwīd vocabulary and relationships

The canonical Tajwīd rule set is made of conventional named phenomena, not
implementation mutations:

- ghunnah mushaddadah;
- iẓhār ḥalqī, ikhfāʾ ḥaqīqī, iqlāb, idghām with/without ghunnah;
- iẓhār, ikhfāʾ, and idghām shafawī;
- idghām mutamāthilayn, mutaqāribayn, and mutajānisayn;
- lām shamsiyyah;
- qalqalah;
- tafkhīm and tarqīq.

Noon sākinah versus tanween is a trigger detail of the same named rule.
Kāmil/naqis and sughrā/kubrā are typed details. The following letter in ikhfāʾ
is stored as the `following` trigger, not an assimilation target. Iẓhār and tarqīq are explicit in
the new annotation model even when pronunciation stays plain, because an
exhaustive Tajwīd projection cannot represent only mutations.

`TajweedOccurrence` is a tagged union by rule family. A common core stores
subject and result; nūn/mīm records name the following letter; idghām records
the actual target; qalqalah records its degree/boundary; emphasis stores a
typed direct/look-back reason. There is no generic `condition`, `effect`,
`source/target` boolean, free-form detail dictionary, or executable condition
tree.

## 5. Madd and other realization

Madd is a specialized `TajweedOccurrence` linked to the affected sound
segment(s), written carrier graphemes, and typed cause. Plural segments are required because
leen is not simply a long-vowel segment. The initial set is exactly what
current implemented output needs:

- ṭabīʿī;
- wājib muttaṣil;
- jāʾiz munfaṣil;
- lāzim;
- ʿāriḍ li-s-sukūn;
- leen.

The phonemizer stores no minimum, maximum, count, or duration. `MaddContext`
records `ALLAH_DAGGER_ALEF`, `WAQF_IWAD`, pronoun/plural-mīm ṣilah, and
`MUQATTAAT` separately from the six current `MaddType`s. Thus ṣilah/ʿiwaḍ are
useful details without becoming speculative mutually exclusive types; a ṣilah
site followed by hamza can still classify as munfaṣil.

Hamzat al-waṣl, iltiqāʾ al-sākinayn, orthographic silence, waqf/ibtidāʾ,
tāʾ-marbūṭah at waqf, inserted sounds, and named contextual exceptions are
typed `RealizationEvent`s. They are not Tajwīd enum members.

## 6. Rule execution and riwāyah variation

Complex rules remain typed Python modules. Shared passes implement shared
behavior. The speculative `RulePolicies` domain object is removed. When a
second researched implementation genuinely differs, explicit riwāyah pipeline
construction binds that one typed classifier.

The pattern is:

```text
shared pass -> call the classifier bound by the active Python pipeline
            -> produce canonical segment -> record the same occurrence variant
```

Hafs supplies `classify_hafs_raa`; Warsh can later supply
`classify_warsh_raa` only after research. They return the same `Emphasis` type
and the shared builder records `TAFKHEEM` or `TARQIQ`. No profile subclasses, scattered
`if riwayah == ...`, or data-file function names are allowed.

Source representation variation is resolved before this point. A Warsh mark
which merely spells the same tanween differently cannot fork a Tajwīd rule.
A source hint such as small mīm validates a derived iqlāb decision but does not
drive it. A likely genuine difference such as plural-mīm ṣilah stays pending
until riwāyah research supplies its implementation and tests.

## 7. Muqaṭṭaʿāt

Store only the compact-letter-to-recited-spelling mapping, keyed by Arabic:

```yaml
names:
  "ص": "صَادْ"
  "م": "مِيمْ"
  "ع": "عَيْنْ"
```

The displayed form, consonants, vowels, length, leen, madd, qalqalah, and
cross-name Tajwīd are derived by feeding the recited spelling through the same
pipeline. Hand-written `segments`, `letter_mappings`, and `tajweed_mapping`
blocks are deleted. Madd lāzim is detected when a long-vowel/leen carrier is
followed by a permanent sākin consonant, whether that consonant realizes
plainly, through shaddah/gemination, or assimilates into the next name. The expansion remains joined to the
following Qurʾānic word, with typed Hafs exceptions for the audited `يسٓ`,
`نٓ`, and Āl ʿImrān connection cases. A separate display value exists only
when a demonstrated requirement differs from the recited spelling.

## 8. Final aggregate and projections

The immutable `Recitation` owns words/addresses, source graphemes, canonical
source letters, recited letters, segments, alignments, boundaries, Tajwīd
occurrences, realization events, recited graphemes, and rendered tokens.

New public projections should expose these facts directly:

- source/normalized/recited text;
- ordered semantic segments and rendered phoneme tokens;
- grapheme and letter mappings through the one alignment relation;
- silent/assimilated/structural graphemes with causes;
- conventional Tajwīd occurrences and their participants;
- madd classifications as a filtered Tajwīd-occurrence projection.

Token indices, view grouping, table cells, and JSON layout are presentation
choices. They are never stored as linguistic truth and never rediscovered by
phoneme-string inspection.

## 9. Rejected alternatives

- Preserve the current output DTOs as the internal object graph.
- One universal `codepoint -> meaning` registry.
- A generic YAML rule/effect engine.
- One subclass per letter or rule.
- A copied Hafs/Warsh rules tree.
- Extensible string riwāyah ids and a speculative all-family `RulePolicies`
  object before a second implementation exists.
- Profile identity split into qirāʾah/riwāyah/ṭarīq fields.
- Madd timing/count fields.
- Duplicate muqaṭṭaʿāt spelling plus segment/Tajwīd expansions.
- Inferring silence from an empty token list.
- Inferring rules from output-token spelling.
- Selecting contextual rules from renderer maps keyed by written states such
  as “bare nūn”.

## 10. Proof order

1. Exact source preservation and full Hafs/Warsh codepoint accountability.
2. Hafs and proved-Warsh sequence normalization fixtures.
3. One nūn/tanwīn vertical slice producing segments, alignments, Tajwīd, and
   new projections.
4. A waqf/ibtidāʾ slice and all audited muqaṭṭaʿāt forms proving recited
   writing, next-word context, and boundary-dependent occurrence changes.
5. Port every current Hafs behavior with semantic regression tests.
6. Make the new Hafs pipeline the default and remove old re-derivers.
7. Add only researched Warsh rule deltas.
