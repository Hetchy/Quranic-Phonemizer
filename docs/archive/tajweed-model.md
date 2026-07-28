# Tajwīd and realization model

> **Archived 2026-07-26.** Historical record only — do not read this as a
> description of the current codebase or of the accepted design. A new ADR
> set is being written to supersede it.
>
> Reason: companion contract to ADR-001. No Tajweed occurrence type exists in
> the code. Retained as the most detailed statement of the intended model and
> as input to its replacement.

Status: concrete target contract for ADR-001. It covers every rule family the
current Hafs code implements and adds explicit iẓhār/tarqīq occurrences where
the new annotation API needs an exhaustive decision. It does not add
unimplemented textbook madd types or performance counts.

## 1. What is first-class

"Tajwīd is first-class" means one rule decision is stored once as a typed
occurrence variant with:

- its conventional rule name;
- the written subject governed by the rule;
- the rule-specific facts which selected the rule;
- an assimilation target only where assimilation actually occurs;
- the resulting sound segments;
- a small typed detail only when the named rule has a real subtype.

It does not mean every pronunciation mechanic is a Tajwīd rule. Hamzat
al-waṣl, iltiqāʾ al-sākinayn, an otiose alef, waqf vowel removal, and inserted
sounds are `RealizationEvent`s. Madd is Tajwīd and `MaddOccurrence` is one
variant of `TajweedOccurrence`, not a parallel annotation system. Source marks
such as the Warsh small mīm are orthographic hints.

## 2. Canonical object graph

The model uses composition and a small tagged union of occurrence records.
There is no subclass per Arabic letter, executable condition tree, free-form
details dictionary, or YAML effect engine.

```python
from dataclasses import dataclass
from enum import StrEnum
from typing import NewType, TypeAlias

GraphemeId = NewType("GraphemeId", int)
GraphemeClusterId = NewType("GraphemeClusterId", int)
LetterUnitId = NewType("LetterUnitId", int)
RecitedWordId = NewType("RecitedWordId", int)
RecitedLetterId = NewType("RecitedLetterId", int)
RecitedGraphemeId = NewType("RecitedGraphemeId", int)
SegmentId = NewType("SegmentId", int)
TajweedOccurrenceId = NewType("TajweedOccurrenceId", int)
RealizationEventId = NewType("RealizationEventId", int)
BoundaryId = NewType("BoundaryId", int)


class Letter(StrEnum):
    HAMZA = "ء"
    HAMZA_WASL = "ٱ"       # canonical identity; source need not contain this scalar
    BAA = "ب"
    NOON = "ن"
    MEEM = "م"
    RAA = "ر"
    LAM = "ل"
    # ...the remaining canonical Arabic letters


class Riwayah(StrEnum):
    HAFS = "hafs"
    WARSH = "warsh"


class VowelQuality(StrEnum):
    A = "a"
    I = "i"
    U = "u"
    IMALA = "imala"
    TAQLIL = "taqlil"


class HarakahKind(StrEnum):
    FATHA = "fatha"
    DAMMA = "damma"
    KASRA = "kasra"
    SUKUN = "sukun"


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
class Harakah:
    kind: HarakahKind
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


@dataclass(frozen=True, slots=True)
class OrthographicHint:
    kind: HintKind
    graphemes: tuple[GraphemeId, ...]


@dataclass(frozen=True, slots=True)
class LetterUnit:
    id: LetterUnitId
    letter: Letter
    base_graphemes: tuple[GraphemeId, ...]
    harakah: Harakah | None = None
    tanween: Tanween | None = None
    small_vowels: tuple[SmallVowel, ...] = ()
    shaddah: tuple[GraphemeId, ...] = ()
    hints: tuple[OrthographicHint, ...] = ()
```

`GraphemeCluster` records only how the source Unicode is grouped: a base scalar
and its combining scalars, or another source-defined cluster. It assigns no
pronunciation and does not collapse semantic values into a generic mark bucket.

`LetterUnit` is source-only. `base_graphemes` is non-empty and every referenced
grapheme must be in the same source cluster. Package code constructs it only
through the source adapter; a lexical expansion or rule may not manufacture a
`LetterUnit`. This closes the ambiguity where a manually added letter could
look as if it came from the mushaf.

It contains the canonical written letter plus first-class written values.
Dagger alef, mini wāw, and mini yāʾ are explicit `SmallVowel` values with their
own source grapheme ids. A letter may carry both a `Harakah` and a
`SmallVowel`, as the script requires. `Harakah` is the conventional written
category, so it honestly includes sukūn; calling the type `ShortVowel` would
incorrectly imply that sukūn is a vowel.

Hafs `ٱ` and a reviewed Warsh `اَ۬` sequence can yield the same
hamzat-al-waṣl `LetterUnit` even though their source graphemes differ. Warsh
`ٖ`, Hafs `ٍ`, and a reviewed kasra+mini-mīm iqlāb spelling can all yield a
`Tanween(quality=KASR, ...)`. Source graphemes are never replaced or
discarded.

`harakah` and `tanween` are mutually exclusive on one letter; `SmallVowel` may
accompany a fatha/damma/kasra. Both absent means orthographically bare, which
remains distinct from `Harakah(SUKUN)`. A
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

### Source units versus inserted/expanded writing

Rules operate on an explicit recited stream. Ordinary source letters are
copied into that stream; muqaṭṭaʿāt expansion and implicit rule output add
recited letters through a `RealizationEvent`:

```python
@dataclass(frozen=True, slots=True)
class LetterForm:
    letter: Letter
    harakah: HarakahKind | None = None
    tanween: TanweenQuality | None = None
    small_vowels: tuple[SmallVowelKind, ...] = ()
    shaddah: bool = False


@dataclass(frozen=True, slots=True)
class RecitedLetter:
    id: RecitedLetterId
    form: LetterForm
    word: RecitedWordId
    graphemes: tuple[RecitedGraphemeId, ...]
    source_letters: tuple[LetterUnitId, ...] = ()
    event: RealizationEventId | None = None


@dataclass(frozen=True, slots=True)
class RecitedWord:
    id: RecitedWordId
    source_word_indexes: tuple[int, ...]
    letters: tuple[RecitedLetterId, ...]
    expansion: RealizationEventId | None = None
```

Construction requires exactly one provenance route: one or more
`source_letters`, or one `event`. The normal source path derives `LetterForm`
from `LetterUnit`; it is not a second normalization table. A muqaṭṭaʿāt event
parses the trusted Arabic name into `LetterForm`s and links every generated
letter back to the compact source grapheme through that event. This is how
non-script/implicit writing is allowed explicitly without weakening source
reconstruction.

`RecitedWord` supplies the lexical boundary needed by the rules. An ordinary
source word creates one recited word. Compact `الم` creates three recited words
(`أَلِفْ`, `لَامْ`, `مِيمْ`) joined by recited boundaries; the final recited
word receives the source/request boundary before the following Qurʾānic word.
This lets madd distinguish “same letter name” from “across names” without
location hacks.

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
    word: RecitedWordId
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
    word: RecitedWordId
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
class OccurrenceCore:
    id: TajweedOccurrenceId
    rule: TajweedRule
    subject: tuple[RecitedLetterId, ...]
    result: tuple[SegmentId, ...]


@dataclass(frozen=True, slots=True)
class GhunnahOccurrence:
    core: OccurrenceCore


@dataclass(frozen=True, slots=True)
class NoonOccurrence:
    core: OccurrenceCore
    trigger: NoonTrigger
    following: RecitedLetterId
    target: RecitedLetterId | None = None


@dataclass(frozen=True, slots=True)
class MeemOccurrence:
    core: OccurrenceCore
    following: RecitedLetterId
    target: RecitedLetterId | None = None


@dataclass(frozen=True, slots=True)
class IdghamOccurrence:
    core: OccurrenceCore
    target: RecitedLetterId
    completeness: IdghamCompleteness


@dataclass(frozen=True, slots=True)
class QalqalahOccurrence:
    core: OccurrenceCore
    degree: QalqalahDegree
    boundary: BoundaryId | None


@dataclass(frozen=True, slots=True)
class DirectHarakahReason:
    harakah: HarakahKind


@dataclass(frozen=True, slots=True)
class SakinAfterHarakahReason:
    previous: RecitedLetterId
    harakah: HarakahKind


@dataclass(frozen=True, slots=True)
class SakinAfterSakinReason:
    intervening: RecitedLetterId
    vowel_bearer: RecitedLetterId
    harakah: HarakahKind


@dataclass(frozen=True, slots=True)
class KasrahBeforeIstilaaReason:
    previous: RecitedLetterId
    following: RecitedLetterId


@dataclass(frozen=True, slots=True)
class WaqfLookbackReason:
    boundary: BoundaryId
    vowel_bearer: RecitedLetterId
    harakah: HarakahKind


@dataclass(frozen=True, slots=True)
class InherentEmphasisReason:
    pass


@dataclass(frozen=True, slots=True)
class LamAllahReason:
    previous_vowel: SegmentId


EmphasisReason: TypeAlias = (
    DirectHarakahReason
    | SakinAfterHarakahReason
    | SakinAfterSakinReason
    | KasrahBeforeIstilaaReason
    | WaqfLookbackReason
    | InherentEmphasisReason
    | LamAllahReason
)


@dataclass(frozen=True, slots=True)
class EmphasisOccurrence:
    core: OccurrenceCore
    subject_kind: EmphasisSubject
    reason: EmphasisReason


NonMaddOccurrence: TypeAlias = (
    GhunnahOccurrence
    | NoonOccurrence
    | MeemOccurrence
    | IdghamOccurrence
    | QalqalahOccurrence
    | EmphasisOccurrence
)
```

There is deliberately no generic `condition` tuple. It was too vague to say
whether the referenced graphemes were a following trigger, a look-back vowel,
a boundary, or an assimilation target, and it could not represent the rāʾ
algorithm without an undocumented convention.

Each occurrence variant stores only the facts its rule family uses:

- `OccurrenceCore.subject` is what the rule governs and `result` is the sound;
- nūn/tanween and mīm records name the following recited letter directly;
- only an actual idghām record has a required assimilation `target`;
- ikhfāʾ/iqlāb records have `target=None` because the following letter is a
  trigger, not something the subject assimilates into;
- rāʾ/lām decisions carry one tagged `EmphasisReason`, including the actual
  look-back letters or boundary which selected the result.

These are explanatory snapshots produced by Python rule code, not executable
conditions and not a second rule language. Constructors validate rule/variant
pairings; for example `IKHFAA_HAQIQI` requires `NoonOccurrence(target=None)`,
while `IDGHAM_BI_GHUNNAH` requires a target. This is more explicit than a
free-form dictionary without creating one class per individual rule.

## 6. Concrete rule-family mapping

The examples illustrate the canonical record; exact references are fixtures
selected from the audited corpus during implementation.

| Family | Example | Stored relationship and sound |
|---|---|---|
| ghunnah mushaddadah | `إِنَّ`, `ثُمَّ` | mushaddad nūn/mīm is `subject`; nasal geminate segment is `result`; no target |
| iẓhār ḥalqī | `مِنْ هَادٍ` | `NoonOccurrence`: nūn is `subject`, `following=ه`, clear nūn is `result`, `target=None` |
| ikhfāʾ ḥaqīqī | `مِنْ شَرِّ` | `NoonOccurrence`: nūn/tanween is `subject`, `following=ش`, hidden nasal is `result`, `target=None` |
| iqlāb | `مِنۢ بَعْدِ` | `NoonOccurrence`: nūn/tanween is `subject`, `following=ب`, hidden/placeless mīm-like nasal is `result`, `target=None`; small mīm is a hint |
| idghām bi-ghunnah | `مَن يَقُولُ` | nūn/tanween is `subject`, `ي` is `target`, merged nasalized target segment is `result` |
| idghām bilā-ghunnah | `مِن رَّبِّهِمْ` | nūn/tanween is `subject`, `ر` is `target`, merged non-nasal target segment is `result` |
| iẓhār shafawī | `هُمْ فِيهَا` | `MeemOccurrence`: sākin mīm is `subject`, following letter is explicit, clear mīm is `result`, `target=None` |
| ikhfāʾ shafawī | `تَرْمِيهِم بِحِجَارَةٍ` | `MeemOccurrence`: sākin mīm is `subject`, `following=ب`, hidden bilabial nasal is `result`, `target=None` |
| idghām shafawī | `لَهُم مَّا` | first mīm is `subject`, next mīm is `target`, nasal geminate is `result` |
| idghām mutamāthilayn | sākin letter followed by the same letter | first is `subject`, second is `target`, merged segment is `result`, detail is normally `KAMIL` |
| idghām mutaqāribayn | implemented pairs such as `لْ` into `ر` | first is `subject`, second is `target`, merged result; pair membership is a reviewed finite table |
| idghām mutajānisayn | implemented same-articulation pairs | first is `subject`, second is `target`; detail records `KAMIL` or `NAQIS` instead of creating two rule ids |
| lām shamsiyyah | `ٱلشَّمْسِ` | article lām is `subject`, sun letter is `target`, doubled sun-letter segment is `result` |
| qalqalah | medial sākin `ق/ط/ب/ج/د`; stopped final `أَحَدْ` | qalqalah letter is `subject`; result links the consonant/release; detail is `SUGHRA` or `KUBRA` |
| tafkhīm | inherent istiʿlāʾ letter, heavy rāʾ, or heavy lām of Allah | `EmphasisOccurrence`: affected recited letter is `subject`, emphatic segment(s) are `result`, and one typed reason records the exact direct/look-back/Allah facts |
| tarqīq | light rāʾ or light lām of Allah | same typed emphasis shape with a plain segment result; it is explicit so annotation is exhaustive |

The old enum splits nūn versus tanween and kamil versus naqis into different
rule names. The new model stores the conventional rule once and puts the real
distinction in `detail`. Conversely, it stores iẓhār and tarqīq even though the
old code often treats them as "nothing happened"; an annotation API cannot be
complete if only mutations are first-class.

## 7. Madd is a Tajwīd occurrence, not duration

```python
class MaddType(StrEnum):
    TABII = "tabii"
    WAJIB_MUTTASIL = "wajib_muttasil"
    JAIZ_MUNFASIL = "jaiz_munfasil"
    LAZIM = "lazim"
    ARID_LISSUKUN = "arid_lissukun"
    LEEN = "leen"


class MaddContext(StrEnum):
    ORDINARY = "ordinary"
    ALLAH_DAGGER_ALEF = "allah_dagger_alef"
    WAQF_IWAD = "waqf_iwad"
    PRONOUN_HAA_SILAH = "pronoun_haa_silah"
    PLURAL_MEEM_SILAH = "plural_meem_silah"
    MUQATTAAT = "muqattaat"


class MaddCarrierForm(StrEnum):
    VOWEL = "vowel"
    LEEN = "leen"


class PermanentSukunRealization(StrEnum):
    PLAIN = "plain"
    GEMINATED = "geminated"
    ASSIMILATED = "assimilated"


@dataclass(frozen=True, slots=True)
class NoSpecialMaddCause:
    pass


@dataclass(frozen=True, slots=True)
class HamzaMaddCause:
    hamza: RecitedLetterId
    same_word: bool


@dataclass(frozen=True, slots=True)
class PermanentSukunCause:
    consonant: RecitedLetterId
    realization: PermanentSukunRealization
    carrier_form: MaddCarrierForm = MaddCarrierForm.VOWEL


@dataclass(frozen=True, slots=True)
class BoundarySukunCause:
    boundary: BoundaryId
    consonant: RecitedLetterId


@dataclass(frozen=True, slots=True)
class LeenMaddCause:
    boundary: BoundaryId
    semivowel: RecitedLetterId
    following_consonant: RecitedLetterId


MaddCause: TypeAlias = (
    NoSpecialMaddCause
    | HamzaMaddCause
    | PermanentSukunCause
    | BoundarySukunCause
    | LeenMaddCause
)


@dataclass(frozen=True, slots=True)
class MaddOccurrence:
    id: TajweedOccurrenceId
    madd_type: MaddType
    subject: tuple[RecitedLetterId, ...]
    segments: tuple[SegmentId, ...]
    carrier: tuple[RecitedGraphemeId, ...]
    cause: MaddCause
    context: MaddContext = MaddContext.ORDINARY


TajweedOccurrence: TypeAlias = NonMaddOccurrence | MaddOccurrence
```

There is no minimum, maximum, count, or duration. `MaddType` answers the
phonological classification; `MaddContext` explains how this site arose. The
axes are intentionally separate:

- the implicit dagger alef of the name of Allah is normally
  `TABII + ALLAH_DAGGER_ALEF`;
- stopping on fathatan can produce `TABII + WAQF_IWAD`, linked to the waqf
  realization event which inserted/replaced the long vowel;
- pronoun-hāʾ or plural-mīm ṣilah is context, while the surrounding hamza can
  still make the actual classification `JAIZ_MUNFASIL`;
- a three-letter muqaṭṭaʿ name is `LAZIM + MUQATTAAT`; `ʿAYN` records
  `carrier_form=LEEN` without pretending its yāʾ is an ordinary long vowel.

This gives ṣilah/ʿiwaḍ/Allah/muqaṭṭaʿāt useful detail without inventing
`silah_sughra`, `silah_kubra`, or `allah` as mutually exclusive madd types.
Badal is not added until a supported behavior and API need it.

`segments` is plural deliberately: ordinary madd points to a long-vowel
segment, while leen may involve the fatha plus a semivowel/diphthong
realization. Calling the field `vowel` would misrepresent the existing leen
case. `MaddOccurrence` is in the `TajweedOccurrence` union, so the aggregate
has one Tajwīd collection; `recitation.madd()` is only a filtered projection.

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
    removed_letters: tuple[RecitedLetterId, ...] = ()
    added_letters: tuple[RecitedLetterId, ...] = ()
```

Inserted segments have an event origin. Removed/silent graphemes align back to
the event. This represents hamzat al-waṣl vowel choice, otiose letters,
waqf/ibtidāʾ changes, iltiqāʾ repairs, and true contextual exceptions without
calling them Tajwīd rules or encoding `effect: silence/replace` in YAML.

Boundary realization is deliberately upstream of Tajwīd annotation. The
selected request follows this dependency order:

```text
source normalization
  -> lexical expansion (including muqaṭṭaʿāt)
  -> boundary projection onto the recited stream
  -> waqf/ibtidāʾ/hamzat-al-waṣl/carrier realization events
  -> baseline segments
  -> nūn/mīm/idghām and other context rules
  -> qalqalah, madd, and emphasis over the resolved result
  -> renderers/projections
```

Therefore waqf can remove a cross-word idghām, create qalqalah kubrā, change a
carrier into madd ʿiwaḍ, or create ʿāriḍ/leen. The aggregate stores only the
occurrences valid for that selected realization. It does not create an
occurrence and later mark it deleted. A separate debug trace can be added if a
real need appears; it is not part of the domain model.

## 9. Same rule, different riwāyah logic

`Riwayah` is a Python 3.11 `StrEnum`. The package intentionally supports a
closed set, currently `HAFS` and `WARSH`; adding another riwāyah is a code and
test change, so extending the enum is the clearest YAGNI choice. There are no
qirāʾah or ṭarīq fields.

The earlier `RulePolicies` object is removed. It named speculative seams
(`plural_meem`, generic marked vowels, and rāʾ) before a second implementation
existed and leaked implementation wiring into the domain model. Resources are
still grouped explicitly:

```python
@dataclass(frozen=True, slots=True)
class RiwayahResources:
    riwayah: Riwayah
    corpus: CorpusSpec
    script: ScriptAdapter
    render: RenderConfig
```

When research proves the same rule has different logic, ordinary Python
composition supplies the one varying classifier at pipeline construction. For
example:

```python
def apply_raa(context: RuleContext, classify: RaaClassifier) -> EmphasisOccurrence:
    decision = classify(context)
    return build_raa_occurrence(context, decision)


def build_hafs_pipeline() -> RulePipeline:
    return RulePipeline(raa=classify_hafs_raa, passes=SHARED_PASSES)


def build_warsh_pipeline() -> RulePipeline:
    # This constructor is not enabled until research proves whether the Hafs
    # classifier is shared or supplies classify_warsh_raa with fixtures.
    raise UnsupportedRiwayahRule("warsh", "raa")
```

This is not a generic policy framework: `RulePipeline` is internal execution
wiring, and a varying callable is introduced only with its first concrete
second implementation. Once supported, both classifiers return the same
`EmphasisDecision`, and the shared builder creates the same
`EmphasisOccurrence` shape. Unknown Warsh behavior does not silently inherit
Hafs.

Representation-only variation never reaches this seam. Hafs `ٱ` and a
reviewed Warsh alef sequence normalize to the same hamzat-al-waṣl form and use
the same rule. A marked `۪` sequence normalizes to a typed marked-vowel input;
Hafs binds its implemented imālah classifier, while Warsh pronunciation stays
rejected until its taqlīl/imālah behavior is researched. A token-only
difference belongs in `RenderConfig`.

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

### Render maps and Arabic text options

All **token selection** can be declarative once rules have produced semantic
segments. The map is keyed by semantic features, not by an Arabic glyph plus
an assumed context:

```yaml
consonants:
  "n": "n"
  "nasal:hidden": "ŋ"
  "w:geminated": "ww"
  "w:nasalized": "w̃"
  "j:geminated": "jj"
  "j:nasalized": "j̃"
releases:
  qalqalah: "Q"
```

Qalqalah does not require a rule-specific renderer branch: the rule produces
a consonant plus an attributed release feature/segment and the renderer maps
both. A map from written state such as “bare nūn means ikhfāʾ” is rejected.
Bare versus explicit sukūn is a source convention; nūn/tanween may interact
across a boundary; idghām of wāw/yāʾ depends on the preceding subject; rāʾ and
full wāw/yāʾ depend on look-back and waqf. Rule code must first produce
`hidden`, `nasalized`, `geminated`, `emphasis`, and `qalqalah` features.

Arabic rendering is a projection over stored source/recited writing:

```python
class TextLayer(StrEnum):
    SOURCE = "source"
    RECITED = "recited"


class SilentMode(StrEnum):
    KEEP = "keep"
    OMIT = "omit"


class ExpansionMode(StrEnum):
    COMPACT = "compact"
    EXPANDED = "expanded"


@dataclass(frozen=True, slots=True)
class ArabicRenderOptions:
    layer: TextLayer
    silent: SilentMode
    include_inserted: bool
    expansion: ExpansionMode
```

Named presets prevent callers from rediscovering today's workarounds:

| Preset | Options | Use |
|---|---|---|
| `SOURCE_EXACT` | source, keep silence, no inserted, compact | exact mushaf/source text |
| `RECITED_ARABIC` | recited, omit silence, include inserted, expanded | current “phonetic text”, including hamzat-al-waṣl vowels, ʿiwaḍ, Allah dagger alef, and muqaṭṭaʿāt names |
| `RECITED_WITH_SILENT` | recited, keep silence, include inserted, expanded | inspection/highlighting |

The renderer never decides what is silent or inserted; alignments and events
already do. Tokenizer round-trip is tested even earlier with a dedicated
source serializer:

```python
assert source_serializer(recitation.graphemes) == loaded_source_text
assert source_serializer(recitation.graphemes).encode("utf-8") == loaded_bytes
```

`SOURCE_EXACT` must produce the same result and is a useful integration test,
but byte reconstruction is fundamentally a source-tokenization invariant, not
proof that recitation rendering is correct.

## 11. Muqaṭṭaʿāt are derived from spelling

The earlier proposed segment lists are redundant. The minimal resource is:

```yaml
schema_version: 1
names:
  "ا": "أَلِفْ"
  "ح": "حَا"
  "ر": "رَا"
  "ص": "صَادْ"
  "م": "مِيمْ"
  "ع": "عَيْنْ"
  # plus ك ه ي ط س ق ن ل: all fourteen names, once
```

The Arabic value is both the recited spelling and default display. The normal
tokenizer, vowel/carrier logic, Tajwīd passes, and madd classifier derive the
segments—including the leen in `عَيْنْ`. A separate display value is added
only if a real requirement differs.

The madd-lāzim predicate is semantic and works for ordinary words and letter
names:

```text
long-vowel carrier followed by a permanent sākin consonant in the same
lexical unit -> LAZIM
```

The consonant may realize plainly, as part of a shaddah/geminate, or assimilate
into the next name. `PermanentSukunCause.realization` records which occurred;
geminated/assimilated causes provide the conventional muthaqqal detail, but
they are not the only way to recognize lāzim. `عَيْنْ` uses the same
permanent-sukūn test with `carrier_form=LEEN`, preserving its special carrier
shape while keeping the currently supported `LAZIM` classification.

The expansion creates joined recited-name units and retains the boundary
after the final name, so ordinary rules also see the following Qurʾānic word.
The complete current-Hafs audit is in
`docs/internal-model-worked-examples.md`; it includes:

- lām→mīm idghām shafawī and sīn→mīm idghām bi-ghunnah;
- ʿayn→ṣād, ʿayn→sīn, sīn→qāf, and continued ṭā-sīn→`تِلْكَ`
  ikhfāʾ;
- qalqalah on the stopped dāl of ṣād;
- the clear-nūn exceptions before wāw after `يسٓ` and `نٓ`;
- connected `الم`→`اللَّهُ` in 3:1–2, where the final mīm-name realization
  receives fatha before hamzat-al-waṣl.

The compact corpus text identifies ordinary openings, so the shared names
table has no copied phonemes, segments, or Tajwīd. Only demonstrated
location/boundary exceptions use a sparse typed Hafs exception record. Any
Warsh override waits for Warsh recitation research.

## 12. Final result and projections

The two remaining derived records are also source-linked rather than bare
strings:

```python
@dataclass(frozen=True, slots=True)
class RecitedGrapheme:
    id: RecitedGraphemeId
    char: str
    word: RecitedWordId
    segments: tuple[SegmentId, ...]
    source: tuple[GraphemeId, ...]
    event: RealizationEventId | None = None


@dataclass(frozen=True, slots=True)
class RenderedToken:
    value: str
    word: RecitedWordId
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


class BoundaryMode(StrEnum):
    JOIN = "join"
    STOP = "stop"
    SAKT = "sakt"
    EDGE = "edge"


@dataclass(frozen=True, slots=True)
class SourceWord:
    index: int
    location: str
    graphemes: tuple[GraphemeId, ...]


@dataclass(frozen=True, slots=True)
class RecitedBoundary:
    id: BoundaryId
    left: RecitedWordId | None
    right: RecitedWordId | None
    mode: BoundaryMode
    causes: tuple[BoundaryCause, ...]
    signs: tuple[GraphemeId, ...] = ()
```

There is one boundary before the first recited word, between every adjacent
pair, and after the last. `EDGE` is valid only when one side is `None`.
`SAKT` blocks cross-boundary rules without applying waqf transforms; `STOP`
blocks them and applies waqf/ibtidāʾ on its sides; `JOIN` allows interaction.
Muqaṭṭaʿāt name boundaries are `JOIN`; the boundary after the final name is the
projected source/request boundary. Rules consume this stored state rather than
recomputing verse edges or raw stop signs.

```python
@dataclass(frozen=True, slots=True)
class Recitation:
    riwayah: Riwayah
    ref: str
    words: tuple[SourceWord, ...]
    graphemes: tuple[Grapheme, ...]
    clusters: tuple[GraphemeCluster, ...]
    letters: tuple[LetterUnit, ...]
    recited_words: tuple[RecitedWord, ...]
    recited_letters: tuple[RecitedLetter, ...]
    segments: tuple[Segment, ...]
    boundaries: tuple[RecitedBoundary, ...]
    alignments: tuple[GraphemeAlignment, ...]
    tajweed: tuple[TajweedOccurrence, ...]
    realizations: tuple[RealizationEvent, ...]
    recited_graphemes: tuple[RecitedGrapheme, ...]
    rendered_tokens: tuple[RenderedToken, ...]
```

`RecitedGrapheme` preserves the source-linked Arabic form after waqf/ibtidāʾ
or lexical expansion. It must have either non-empty `source` or one `event`,
never neither/both. Its segment links let annotations address a generated
muqaṭṭaʿāt carrier or an inserted vowel without pretending it was a source
scalar. `RenderedToken` points to its source `SegmentId`s.
Public APIs may be new and cleaner; they project this graph and never re-run a
phonological detector. Exact legacy JSON field compatibility is not a design
constraint.
