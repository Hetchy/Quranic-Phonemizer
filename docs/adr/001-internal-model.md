# ADR-001: Canonical internal model for multiple riwāyāt

Status: **accepted for implementation** for the Hafs refactor and Warsh script
normalization. Warsh pronunciation remains gated by research identified in the
integration plan.

Companions:

- `docs/tajweed-model.md` is the concrete type and occurrence contract.
- `docs/warsh-script-codepoint-audit.md` is the source-encoding evidence.
- ADR-002 defines invariants and migration gates.
- ADR-003 defines code, runtime-data, build, evidence, and research ownership.

## 1. Decision

Replace the mutable `LetterSymbol`/neighbour-mutation pipeline with one
utterance result containing five connected layers:

1. exact source `Grapheme`s;
2. source-normalized `LetterUnit`s;
3. realized sound `Segment`s;
4. explicit grapheme-to-segment `Alignment`s;
5. stored Tajwīd, madd, realization, recited-writing, and rendered-token facts.

Each result belongs to one registered `RiwayahSpec`. The package identity is
only the riwāyah id (`hafs`, `warsh`, and future registered ids). The model has
no qirāʾah or ṭarīq fields.

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
`LetterUnit`s composed with first-class `ShortVowel`, `Tanween`, `SmallVowel`,
sukun, shaddah, and orthographic-hint values. Dagger alef and mini wāw/yāʾ are
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

### Alignment

Every source grapheme has one typed relationship to sound: realizes, carries,
assimilated, silent, orthographic hint, or structural. Many graphemes may
share one segment and one grapheme may contribute to multiple segments.

This relation is required, not optional metadata. It is what makes letter and
character mapping, silent-letter explanation, cross-word mergers, long-vowel
ownership, and Tajwīd highlighting simple projections rather than separate
detectors.

### Occurrences and derived writing

The builder records named Tajwīd occurrences, madd classifications, and
non-Tajwīd realization events while it knows why the sound changed. It also
records source-linked recited Arabic graphemes for waqf/ibtidāʾ and lexical
expansion. Rendered tokens point to segment ids.

## 3. Identity and configuration

```python
@dataclass(frozen=True, slots=True)
class RiwayahSpec:
    id: str
    corpus: CorpusSpec
    script: ScriptAdapter
    policies: RulePolicies
    render: RenderConfig
```

The id is a validated registry key rather than an enum because installed
riwāyāt are extensible identities. Closed linguistic concepts—letters, vowel
qualities, small-vowel kinds, rule names, alignment kinds, madd types—use
Python 3.11 `StrEnum`.

Corpus, address metadata, searchable-text normalization, script adapter,
exceptions, rule policies, render configuration, and caches are instance-local
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
is a condition, not an assimilation target. Iẓhār and tarqīq are explicit in
the new annotation model even when pronunciation stays plain, because an
exhaustive Tajwīd projection cannot represent only mutations.

`TajweedOccurrence` stores `subject`, `condition`, `target`, `result`, and an
optional validated detail union. There is no generic `effect`, `source/target`
boolean, free-form detail dictionary, or rule subclass tree.

## 5. Madd and other realization

Madd is a separate classification linked to the affected sound segment(s),
written carrier graphemes, and cause. Plural segments are required because
leen is not simply a long-vowel segment. The initial set is exactly what
current implemented output needs:

- ṭabīʿī;
- wājib muttaṣil;
- jāʾiz munfaṣil;
- lāzim;
- ʿāriḍ li-s-sukūn;
- leen.

The phonemizer stores no minimum, maximum, count, or duration. It does not add
badal or ṣilah sughrā/kubrā without a supported behavior and API requirement.
Ṣilah may be the context of a pronoun-hāʾ or plural-mīm realization; it is not
automatically a madd type. Waqf ʿiwaḍ is a realization event which yields a
long vowel, not a new stored madd classification.

Hamzat al-waṣl, iltiqāʾ al-sākinayn, orthographic silence, waqf/ibtidāʾ,
tāʾ-marbūṭah at waqf, inserted sounds, and named contextual exceptions are
typed `RealizationEvent`s. They are not Tajwīd enum members.

## 6. Rule execution and riwāyah variation

Complex rules remain typed Python modules. Shared passes implement shared
behavior. A `RulePolicies` composition object provides narrow strategies only
where conditions genuinely vary—for example rāʾ emphasis, marked-vowel
quality, or plural-mīm realization.

The pattern is:

```text
shared pass -> call active policy -> produce canonical segment
            -> record the same canonical occurrence relationship
```

Hafs can supply `classify_hafs_raa`; Warsh can later supply
`classify_warsh_raa`. They return the same `Emphasis` type and the shared pass
records `TAFKHEEM` or `TARQIQ`. No profile subclasses, scattered
`if riwayah == ...`, or data-file function names are allowed.

Source representation variation is resolved before this point. A Warsh mark
which merely spells the same tanween differently cannot fork a Tajwīd rule.
A source hint such as small mīm validates a derived iqlāb decision but does not
drive it. A likely genuine difference such as plural-mīm ṣilah stays pending
until riwāyah research supplies its policy and tests.

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
blocks are deleted. A separate display value exists only when a demonstrated
requirement differs from the recited spelling.

## 8. Final aggregate and projections

The immutable `Recitation` owns words/addresses, source graphemes, canonical
letters, segments, alignments, boundaries, Tajwīd occurrences, madd
occurrences, realization events, recited graphemes, and rendered tokens.

New public projections should expose these facts directly:

- source/normalized/recited text;
- ordered semantic segments and rendered phoneme tokens;
- grapheme and letter mappings through the one alignment relation;
- silent/assimilated/structural graphemes with causes;
- conventional Tajwīd occurrences and their participants;
- madd classifications.

Token indices, view grouping, table cells, and JSON layout are presentation
choices. They are never stored as linguistic truth and never rediscovered by
phoneme-string inspection.

## 9. Rejected alternatives

- Preserve the current output DTOs as the internal object graph.
- One universal `codepoint -> meaning` registry.
- A generic YAML rule/effect engine.
- One subclass per letter or rule.
- A copied Hafs/Warsh rules tree.
- Profile identity split into qirāʾah/riwāyah/ṭarīq fields.
- Madd timing/count fields.
- Duplicate muqaṭṭaʿāt spelling plus segment/Tajwīd expansions.
- Inferring silence from an empty token list.
- Inferring rules from output-token spelling.

## 10. Proof order

1. Exact source preservation and full Hafs/Warsh codepoint accountability.
2. Hafs and proved-Warsh sequence normalization fixtures.
3. One nūn/tanwīn vertical slice producing segments, alignments, Tajwīd, and
   new projections.
4. A waqf/ibtidāʾ slice and a muqaṭṭaʿāt expansion proving recited writing.
5. Port every current Hafs behavior with semantic regression tests.
6. Make the new Hafs pipeline the default and remove old re-derivers.
7. Add only researched Warsh rule deltas.
