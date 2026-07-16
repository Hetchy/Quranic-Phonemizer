# Tajwīd and realization model

Status: concrete target contract for ADR-001. It covers every rule family the
current Hafs code implements and adds explicit iẓhār/tarqīq occurrences where
the new annotation API needs an exhaustive decision. It does not add
unimplemented textbook madd types or performance counts.

## 1. What is first-class

"Tajwīd is first-class" means one rule decision is stored once with:

- its conventional rule name;
- the written subject governed by the rule;
- the context which selected the rule;
- an assimilation target only where assimilation actually occurs;
- the resulting sound segments;
- a small typed detail only when the named rule has a real subtype.

It does not mean every pronunciation mechanic is a Tajwīd rule. Hamzat
al-waṣl, iltiqāʾ al-sākinayn, an otiose alef, waqf vowel removal, and inserted
sounds are `RealizationEvent`s. Madd classification is a `MaddOccurrence`.
Source marks such as the Warsh small mīm are orthographic hints.

## 2. Canonical object graph

The model uses composition. There is no subclass per Arabic letter, no rule
object hierarchy, no free-form details dictionary, and no YAML effect engine.

```python
from dataclasses import dataclass
from enum import StrEnum
from typing import NewType, TypeAlias

GraphemeId = NewType("GraphemeId", int)
GraphemeClusterId = NewType("GraphemeClusterId", int)
LetterUnitId = NewType("LetterUnitId", int)
SegmentId = NewType("SegmentId", int)
TajweedOccurrenceId = NewType("TajweedOccurrenceId", int)
RealizationEventId = NewType("RealizationEventId", int)


class Letter(StrEnum):
    HAMZA = "ء"
    HAMZA_WASL = "ٱ"       # canonical identity; source need not contain this scalar
    BAA = "ب"
    NOON = "ن"
    MEEM = "م"
    RAA = "ر"
    LAM = "ل"
    # ...the remaining canonical Arabic letters


class VowelQuality(StrEnum):
    A = "a"
    I = "i"
    U = "u"
    IMALA = "imala"
    TAQLIL = "taqlil"


class TanweenQuality(StrEnum):
    FATH = "fath"
    DAMM = "damm"
    KASR = "kasr"


class SmallVowelKind(StrEnum):
    DAGGER_ALEF = "dagger_alef"
    MINI_WAW = "mini_waw"
    MINI_YAA = "mini_yaa"


class HintKind(StrEnum):
    IQLAB = "iqlab"
    MARKED_VOWEL = "marked_vowel"
    SILENT_IN_WASL = "silent_in_wasl"
    SAKT = "sakt"


@dataclass(frozen=True, slots=True)
class Grapheme:
    id: GraphemeId
    char: str                 # exactly one source Unicode scalar
    word_index: int
    source_offset: int


@dataclass(frozen=True, slots=True)
class GraphemeCluster:
    """Source Unicode grouping only; it assigns no phonological meaning."""

    id: GraphemeClusterId
    word_index: int
    graphemes: tuple[GraphemeId, ...]


@dataclass(frozen=True, slots=True)
class ShortVowel:
    quality: VowelQuality
    graphemes: tuple[GraphemeId, ...]


@dataclass(frozen=True, slots=True)
class Tanween:
    quality: TanweenQuality
    graphemes: tuple[GraphemeId, ...]


@dataclass(frozen=True, slots=True)
class SmallVowel:
    kind: SmallVowelKind
    quality: VowelQuality
    graphemes: tuple[GraphemeId, ...]


Vocalization: TypeAlias = ShortVowel | Tanween | SmallVowel


@dataclass(frozen=True, slots=True)
class OrthographicHint:
    kind: HintKind
    graphemes: tuple[GraphemeId, ...]


@dataclass(frozen=True, slots=True)
class LetterUnit:
    id: LetterUnitId
    letter: Letter
    base_graphemes: tuple[GraphemeId, ...]
    vocalizations: tuple[Vocalization, ...] = ()
    shaddah: tuple[GraphemeId, ...] = ()
    sukun: tuple[GraphemeId, ...] = ()
    hints: tuple[OrthographicHint, ...] = ()
```

`GraphemeCluster` records only how the source Unicode is grouped: a base scalar
and its combining scalars, or another source-defined cluster. It assigns no
pronunciation and does not collapse semantic values into a generic mark bucket.

`LetterUnit` is the canonical written letter plus first-class vocalization
values composed onto it. Dagger alef, mini wāw, and mini yāʾ are explicit
`SmallVowel` values with their own source grapheme ids. A letter may carry both
a `ShortVowel` and a `SmallVowel`, as the script requires.

Hafs `ٱ` and a reviewed Warsh `اَ۬` sequence can yield the same
hamzat-al-waṣl `LetterUnit` even though their source graphemes differ. Warsh
`ٖ`, Hafs `ٍ`, and a reviewed kasra+mini-mīm iqlāb spelling can all yield a
`Tanween(quality=KASR, ...)`. Source graphemes are never replaced or
discarded.

`ShortVowel`, `Tanween`, and `sukun` are mutually exclusive on one letter;
`SmallVowel` may accompany a short vowel. All three absent means
orthographically bare, which remains distinct from explicit sukun. A
multi-scalar initial-alef cluster may normalize to one hamzat-al-waṣl unit;
the semantic parts of that unit still retain the exact grapheme ids which
licensed them.

Normalization is deliberately many-to-one and context-sensitive in both
directions:

- Hafs/Warsh standard, alternate, and composite tanween spellings map to the
  same `TanweenQuality.FATH/DAMM/KASR`; the exact source scalars remain in
  `Grapheme` and an
  optional reviewed visual-rule hint may be retained for validation;
- `۪` can participate in a hamzat-al-waṣl sequence or a marked-vowel sequence,
  so the adapter maps the complete cluster/context rather than the scalar;
- the presence/shape of a tanween hint never drives iẓhār, ikhfāʾ, iqlāb, or
  idghām. Those are derived from the canonical tanween plus following
  canonical letter and boundary.

Thus semantic normalization loses no source provenance, while shared rules
are independent of whether a mushaf uses open/closed or other visual forms.

### Composite iqlāb spelling

The selected Warsh source makes the many-to-one requirement concrete. Its 575
small-mīm-above sites divide exactly into:

| Source composition | Count | Canonical subject |
|---|---:|---|
| bare nūn + `ۢ` | 270 | nūn sākinah plus `IQLAB` hint |
| fatha + `ۢ` | 91 | `Tanween(FATH)` plus `IQLAB` hint |
| damma + `ۢ` | 123 | `Tanween(DAMM)` plus `IQLAB` hint |
| kasra + `ۢ` | 91 | `Tanween(KASR)` plus `IQLAB` hint |

All 270 nūn cases and 292 of the 305 composite-tanween cases are followed by
`ب` within the audited ayah; the other 13 composite cases are at an ayah edge
which that audit deliberately treated as a boundary. The current Hafs corpus
contains neither small mīm above nor below; it derives iqlāb solely from nūn or
ordinary tanween plus context.

The mini mīm is not a `SmallVowel`. In a composite tanween spelling, its
grapheme and the harakah grapheme together license one `Tanween` value and an
orthographic iqlāb hint. On nūn it is only the hint. In both cases the shared
rule independently checks the following canonical `ب`; an inconsistent hint
is a source-validation error, not permission to force iqlāb.

The written-letter and sound inventories are deliberately separate. All hamza
seats can realize one glottal-stop consonant, while wāw/yāʾ may realize a
consonant or carry a vowel. Consonants and vowels are different segment
variants because their fields and rules differ; letter subclasses are not
needed.

```python
class VowelLength(StrEnum):
    SHORT = "short"
    LONG = "long"


class Emphasis(StrEnum):
    PLAIN = "plain"
    EMPHATIC = "emphatic"


class Consonant(StrEnum):
    GLOTTAL_STOP = "glottal_stop"
    B = "b"
    N = "n"
    M = "m"
    R = "r"
    L = "l"
    # ...the remaining consonant sounds


@dataclass(frozen=True, slots=True)
class ConsonantSegment:
    id: SegmentId
    consonant: Consonant | None    # None only for a placeless/hidden nasal
    word_index: int
    geminated: bool = False
    nasalized: bool = False
    hidden: bool = False
    emphasis: Emphasis = Emphasis.PLAIN
    qalqalah: bool = False


@dataclass(frozen=True, slots=True)
class VowelSegment:
    id: SegmentId
    quality: VowelQuality
    length: VowelLength
    word_index: int
    emphasis: Emphasis = Emphasis.PLAIN


Segment: TypeAlias = ConsonantSegment | VowelSegment
```

The segment stores meaning, not an IPA-like output token. A renderer may emit
`ŋ`, `m̃`, or another configured token for the same supported semantic segment
without changing rule detection or Tajwīd annotation.

## 3. Written-to-sound alignment and silence

Absence of a phoneme is not enough to explain a silent letter. Every source
grapheme gets one alignment record:

```python
class AlignmentKind(StrEnum):
    REALIZES = "realizes"          # directly contributes the sound
    CARRIES = "carries"            # long-vowel/hamza seat, shares a segment
    ASSIMILATED = "assimilated"    # no independent sound; shares target result
    SILENT = "silent"              # no result segment
    ORTHOGRAPHIC_HINT = "orthographic_hint"
    STRUCTURAL = "structural"


@dataclass(frozen=True, slots=True)
class OccurrenceCause:
    tajweed: TajweedOccurrenceId | None = None
    realization: RealizationEventId | None = None


@dataclass(frozen=True, slots=True)
class GraphemeAlignment:
    grapheme: GraphemeId
    segments: tuple[SegmentId, ...]
    kind: AlignmentKind
    cause: OccurrenceCause | None = None
```

Invariants reject both cause fields being set. `ASSIMILATED` and `SILENT`
require a cause. A long alef can `CARRY` the same vowel segment initiated by a
fatha. In cross-word idghām, the source nūn is `ASSIMILATED`, the target letter
`REALIZES`, and both align to the shared geminated/nasal result. An iqlāb small
mīm is `ORTHOGRAPHIC_HINT`; it does not itself create a segment.

This one relation projects:

- source-character-to-segment mapping;
- letter-to-phoneme mapping after rendering;
- silent letters with reasons;
- shared/cross-word ownership;
- character-cell status if that presentation is retained.

It replaces the independent silence, character, letter, and Tajwīd detectors
in today's output modules.

## 4. Small vowels, full carriers, and semivowels

Miniature writing is an orthographic distinction with provenance, not a new
phoneme class.

- Dagger alef, mini wāw, and mini yāʾ are `SmallVowel` values composed into a
  `LetterUnit`. Their own graphemes align to the vowel segment they realize or
  carry.
- A full alef, wāw, yāʾ, or alef maqṣūrah is a `LetterUnit`, because it is a
  written letter and its function is not always known from shape alone.
- `VowelSegment` has quality and realized length; it has no `mini=True` flag.
  A full and small spelling which sound alike therefore produce the same
  segment type while alignments preserve the different writing.

Examples of alignment:

```text
fatha + full alef       -> one long A VowelSegment
  fatha grapheme        -> REALIZES that segment
  alef grapheme         -> CARRIES that segment

damma + mini waw        -> one long U VowelSegment in the supported context
  damma grapheme        -> REALIZES that segment
  mini-waw grapheme     -> CARRIES that segment

dagger alef             -> long A VowelSegment
  dagger-alef grapheme  -> REALIZES/CARRIES that segment as the source dictates
```

Full wāw/yāʾ role is a realization decision over the immutable written unit:

1. after a compatible short vowel, it may carry the corresponding long vowel;
2. as a sākin semivowel or in an incompatible context, it may realize `w`/`j`;
3. in an otiose/redundant spelling, it may be silent with a realization cause;
4. at waqf, the final written harakah is removed first and the same unit is
   re-evaluated, so a final wāw/yāʾ can switch between consonant, carrier, and
   silent roles without mutating `LetterUnit`;
5. fatha + sākin wāw/yāʾ can remain a semivowel in wasl and become a leen madd
   site at waqf.

Small vowels are also realized contextually. The ordinary dagger alef carries
long `A`; a mini wāw/yāʾ used for ṣilah may carry `U/I` in wasl and align as
`SILENT` at waqf. These are rule/realization decisions, not separate subclasses
and not properties inferred from output strings.

This handles the existing `vowel.py` behavior with domain-specific written
values. The boundary-resolved builder produces one realization;
another wasl/waqf request reuses the same source/canonical writing and creates
different segments/alignments where required.

## 5. Tajwīd occurrences

```python
class TajweedRule(StrEnum):
    GHUNNAH_MUSHADDADAH = "ghunnah_mushaddadah"
    IZHAR_HALQI = "izhar_halqi"
    IKHFAA_HAQIQI = "ikhfaa_haqiqi"
    IQLAB = "iqlab"
    IDGHAM_BI_GHUNNAH = "idgham_bi_ghunnah"
    IDGHAM_BILA_GHUNNAH = "idgham_bila_ghunnah"
    IZHAR_SHAFAWI = "izhar_shafawi"
    IKHFAA_SHAFAWI = "ikhfaa_shafawi"
    IDGHAM_SHAFAWI = "idgham_shafawi"
    IDGHAM_MUTAMATHILAYN = "idgham_mutamathilayn"
    IDGHAM_MUTAQARIBAYN = "idgham_mutaqaribayn"
    IDGHAM_MUTAJANISAYN = "idgham_mutajanisayn"
    LAM_SHAMSIYYAH = "lam_shamsiyyah"
    QALQALAH = "qalqalah"
    TAFKHEEM = "tafkheem"
    TARQIQ = "tarqiq"


class NoonTrigger(StrEnum):
    NOON_SAKINAH = "noon_sakinah"
    TANWEEN = "tanween"


class IdghamCompleteness(StrEnum):
    KAMIL = "kamil"
    NAQIS = "naqis"


class QalqalahDegree(StrEnum):
    SUGHRA = "sughra"
    KUBRA = "kubra"


class EmphasisSubject(StrEnum):
    INHERENT_LETTER = "inherent_letter"
    RAA = "raa"
    LAM_ALLAH = "lam_allah"


@dataclass(frozen=True, slots=True)
class NoonDetail:
    trigger: NoonTrigger


@dataclass(frozen=True, slots=True)
class IdghamDetail:
    completeness: IdghamCompleteness


@dataclass(frozen=True, slots=True)
class QalqalahDetail:
    degree: QalqalahDegree


@dataclass(frozen=True, slots=True)
class EmphasisDetail:
    subject: EmphasisSubject


RuleDetail: TypeAlias = (
    NoonDetail | IdghamDetail | QalqalahDetail | EmphasisDetail
)


@dataclass(frozen=True, slots=True)
class TajweedOccurrence:
    id: TajweedOccurrenceId
    rule: TajweedRule
    subject: tuple[GraphemeId, ...]
    condition: tuple[GraphemeId, ...]
    target: tuple[GraphemeId, ...]
    result: tuple[SegmentId, ...]
    detail: RuleDetail | None = None
```

These are named relationships, not generic effects:

- `subject` is what the rule governs;
- `condition` selects/explains the decision but is not falsely called an
  assimilation target;
- `target` is populated only when the subject's sound assimilates into it;
- `result` is the sound produced by the occurrence.

Constructors validate the permitted detail for each rule. For example,
`QALQALAH` requires `QalqalahDetail`, and `IKHFAA_HAQIQI` may take
`NoonDetail` but can never take `IdghamDetail`. This is stricter and smaller
than either rule subclasses or a `dict[str, object]`.

## 6. Concrete rule-family mapping

The examples illustrate the canonical record; exact references are fixtures
selected from the audited corpus during implementation.

| Family | Example | Stored relationship and sound |
|---|---|---|
| ghunnah mushaddadah | `إِنَّ`, `ثُمَّ` | mushaddad nūn/mīm is `subject`; nasal geminate segment is `result`; no target |
| iẓhār ḥalqī | `مِنْ هَادٍ` | nūn is `subject`, `ه` is `condition`, clear nūn is `result`; no target |
| ikhfāʾ ḥaqīqī | `مِنْ شَرِّ` | nūn/tanween is `subject`, `ش` is `condition`, hidden nasal is `result`; `ش` is not a target |
| iqlāb | `مِنۢ بَعْدِ` | nūn/tanween is `subject`, `ب` is `condition`, hidden/placeless mīm-like nasal is `result`; small mīm is a hint |
| idghām bi-ghunnah | `مَن يَقُولُ` | nūn/tanween is `subject`, `ي` is `target`, merged nasalized target segment is `result` |
| idghām bilā-ghunnah | `مِن رَّبِّهِمْ` | nūn/tanween is `subject`, `ر` is `target`, merged non-nasal target segment is `result` |
| iẓhār shafawī | `هُمْ فِيهَا` | sākin mīm is `subject`, following letter is `condition`, clear mīm is `result` |
| ikhfāʾ shafawī | `تَرْمِيهِم بِحِجَارَةٍ` | sākin mīm is `subject`, `ب` is `condition`, hidden bilabial nasal is `result`; no target |
| idghām shafawī | `لَهُم مَّا` | first mīm is `subject`, next mīm is `target`, nasal geminate is `result` |
| idghām mutamāthilayn | sākin letter followed by the same letter | first is `subject`, second is `target`, merged segment is `result`, detail is normally `KAMIL` |
| idghām mutaqāribayn | implemented pairs such as `لْ` into `ر` | first is `subject`, second is `target`, merged result; pair membership is a reviewed finite table |
| idghām mutajānisayn | implemented same-articulation pairs | first is `subject`, second is `target`; detail records `KAMIL` or `NAQIS` instead of creating two rule ids |
| lām shamsiyyah | `ٱلشَّمْسِ` | article lām is `subject`, sun letter is `target`, doubled sun-letter segment is `result` |
| qalqalah | medial sākin `ق/ط/ب/ج/د`; stopped final `أَحَدْ` | qalqalah letter is `subject`; result links the consonant/release; detail is `SUGHRA` or `KUBRA` |
| tafkhīm | inherent istiʿlāʾ letter, heavy rāʾ, or heavy lām of Allah | affected grapheme is `subject`, deciding vowels/neighbours are `condition`, emphatic segment(s) are `result`, detail states subject family |
| tarqīq | light rāʾ or light lām of Allah | same shape as tafkhīm with a plain segment result; it is explicit so annotation is exhaustive |

The old enum splits nūn versus tanween and kamil versus naqis into different
rule names. The new model stores the conventional rule once and puts the real
distinction in `detail`. Conversely, it stores iẓhār and tarqīq even though the
old code often treats them as "nothing happened"; an annotation API cannot be
complete if only mutations are first-class.

## 7. Madd is classification, not duration

```python
class MaddType(StrEnum):
    TABII = "tabii"
    WAJIB_MUTTASIL = "wajib_muttasil"
    JAIZ_MUNFASIL = "jaiz_munfasil"
    LAZIM = "lazim"
    ARID_LISSUKUN = "arid_lissukun"
    LEEN = "leen"


@dataclass(frozen=True, slots=True)
class MaddOccurrence:
    madd_type: MaddType
    segments: tuple[SegmentId, ...]
    carrier: tuple[GraphemeId, ...]
    cause: tuple[GraphemeId, ...] = ()
```

There is no minimum, maximum, count, or duration. Waqf ʿiwaḍ is a realization
event which creates a long vowel; it is not a seventh stored madd type in the
current product. Ṣilah is context for realizing a pronoun-hāʾ or plural-mīm;
it is not automatically a madd classification. Badal and silah
sughrā/kubrā are not added until a supported riwāyah, behavior, and API need
them.

`segments` is plural deliberately: ordinary madd points to a long-vowel
segment, while leen may involve the fatha plus a semivowel/diphthong
realization. Calling the field `vowel` would misrepresent the existing leen
case.

## 8. Non-Tajwīd realization

```python
class RealizationReason(StrEnum):
    HAMZA_WASL_WASL = "hamza_wasl_wasl"
    HAMZA_WASL_IBTIDA = "hamza_wasl_ibtida"
    ILTIQAA_SAKINAYN = "iltiqaa_sakinayn"
    ORTHOGRAPHIC_SILENCE = "orthographic_silence"
    WAQF_VOWEL_DROP = "waqf_vowel_drop"
    WAQF_IWAD = "waqf_iwad"
    TAA_MARBUTA_WAQF = "taa_marbuta_waqf"
    LEXICAL_EXPANSION = "lexical_expansion"
    TYPED_EXCEPTION = "typed_exception"


@dataclass(frozen=True, slots=True)
class RealizationEvent:
    id: RealizationEventId
    reason: RealizationReason
    source: tuple[GraphemeId, ...]
    removed: tuple[SegmentId, ...]
    added: tuple[SegmentId, ...]
```

Inserted segments have an event origin. Removed/silent graphemes align back to
the event. This represents hamzat al-waṣl vowel choice, otiose letters,
waqf/ibtidāʾ changes, iltiqāʾ repairs, and true contextual exceptions without
calling them Tajwīd rules or encoding `effect: silence/replace` in YAML.

## 9. Same rule, different riwāyah logic

The stable model and rule name are shared. Only the classifier/realizer is a
strategy when research proves different conditions:

```python
RaaClassifier = Callable[[RuleContext, LetterUnitId], Emphasis]
MarkedVowelClassifier = Callable[[RuleContext, LetterUnitId], VowelQuality]
PluralMeemRealizer = Callable[[RuleContext, LetterUnitId], None]


@dataclass(frozen=True, slots=True)
class RulePolicies:
    raa: RaaClassifier
    marked_vowel: MarkedVowelClassifier
    plural_meem: PluralMeemRealizer


@dataclass(frozen=True, slots=True)
class RiwayahSpec:
    id: str
    corpus: CorpusSpec
    script: ScriptAdapter
    policies: RulePolicies
    render: RenderConfig
```

The registry id is a validated string (`"hafs"`, `"warsh"`) because supported
riwāyāt are registered identities, not a closed linguistic enum. There are no
qirāʾah or ṭarīq fields in this package model.

For rāʾ, the shared pass asks `riwayah.policies.raa(...)`, writes either
`TAFKHEEM` or `TARQIQ`, and aligns the same subject/condition/result shape.
Hafs supplies `classify_hafs_raa`; Warsh supplies a different function only
after its conditions are researched. No `if riwayah == ...` spreads through
the rule module, no subclass is required, and no YAML contains executable
branching.

The same pattern handles the marked `۪` vowel: the script adapter identifies
the source sequence; the Hafs policy can return `IMALA` for its one occurrence;
the Warsh policy can return `TAQLIL` or `IMALA` as evidence requires. The
renderer only maps the resulting `VowelQuality` to tokens.

## 10. Where letters, rule data, and phonemes live

- Complex decision logic lives in `rules/*.py`.
- Proven riwāyah strategy replacements live in `riwayat/<id>/rules.py`.
- Small finite shared sets/pairs may live in `data/shared/tajweed.yaml`, using
  Arabic glyph strings such as `"ءهعحغخ"` and
  `"تثجدذزسشصضطظفقك"`; the loader converts them to `Letter` enums.
- A riwāyah table contains only a proved replacement/delta, never a copied
  Hafs rule tree.
- All output tokens live in `data/shared/render.yaml` plus sparse riwāyah
  overrides. There is no separate file of "Tajwīd effects". Rules create
  semantic segments; the renderer chooses token strings.
- Source-specific single-scalar aliases may be data. Contextual Unicode
  sequence interpretation lives in the script adapter and fixtures.

A finite set is data; "if the rāʾ is sākin and the previous consonant is also
sākin, inspect the preceding vowel..." is code.

## 11. Muqaṭṭaʿāt are derived from spelling

The earlier proposed segment lists are redundant. The minimal resource is:

```yaml
names:
  "ص": "صَادْ"
  "م": "مِيمْ"
  "ع": "عَيْنْ"
```

The Arabic value is both the recited spelling and default display. The normal
tokenizer, vowel/carrier logic, Tajwīd passes, and madd classifier derive the
segments—including the leen in `عَيْنْ`. A separate display value is added
only if a real requirement differs. Location lists are unnecessary where the
compact corpus text already identifies the opening; any riwāyah exception is
a sparse override with a test.

## 12. Final result and projections

The two remaining derived records are also source-linked rather than bare
strings:

```python
@dataclass(frozen=True, slots=True)
class RecitedGrapheme:
    char: str
    word_index: int
    source: tuple[GraphemeId, ...]
    event: RealizationEventId | None = None


@dataclass(frozen=True, slots=True)
class RenderedToken:
    value: str
    word_index: int
    segments: tuple[SegmentId, ...]
```

Boundary state is resolved once per request. Sakt is separate from waqf: both
block a cross-boundary rule, but only waqf applies final-word transforms.

```python
class BoundaryCause(StrEnum):
    REQUEST_EDGE = "request_edge"
    VERSE_END = "verse_end"
    STOP_SIGN = "stop_sign"
    EXPLICIT_REF = "explicit_ref"
    SAKT_SIGN = "sakt_sign"


@dataclass(frozen=True, slots=True)
class SourceWord:
    index: int
    location: str
    graphemes: tuple[GraphemeId, ...]


@dataclass(frozen=True, slots=True)
class WordBoundaryState:
    word_index: int
    starts_here: bool
    stops_here: bool
    sakt_after: bool
    causes: tuple[BoundaryCause, ...]
    signs: tuple[GraphemeId, ...] = ()
```

Validation prevents `stops_here` and `sakt_after` from describing the same
after-word boundary. The next included word starts after a stop; a request's
first word starts. Rules consume this stored state rather than recomputing
verse edges or raw stop signs.

```python
@dataclass(frozen=True, slots=True)
class Recitation:
    riwayah: str
    ref: str
    words: tuple[SourceWord, ...]
    graphemes: tuple[Grapheme, ...]
    clusters: tuple[GraphemeCluster, ...]
    letters: tuple[LetterUnit, ...]
    segments: tuple[Segment, ...]
    boundaries: tuple[WordBoundaryState, ...]
    alignments: tuple[GraphemeAlignment, ...]
    tajweed: tuple[TajweedOccurrence, ...]
    madd: tuple[MaddOccurrence, ...]
    realizations: tuple[RealizationEvent, ...]
    recited_graphemes: tuple[RecitedGrapheme, ...]
    rendered_tokens: tuple[RenderedToken, ...]
```

`RecitedGrapheme` preserves the source-linked Arabic form after waqf/ibtidāʾ
or lexical expansion. `RenderedToken` points to its source `SegmentId`s.
Public APIs may be new and cleaner; they project this graph and never re-run a
phonological detector. Exact legacy JSON field compatibility is not a design
constraint.
