# Internal model worked examples

> **Archived 2026-07-26.** Historical record only — do not read this as a
> description of the current codebase or of the accepted design. A new ADR
> set is being written to supersede it.
>
> Reason: companion to ADR-001. Its muqattaat and rule-family audits remain
> useful evidence, but two behaviours it specifies (27:1 ikhfaa into `تِلْكَ`,
> connected 3:1 `الم` into `اللَّهُ`) are not implemented.

Status: implementation companion to ADR-001 and `docs/tajweed-model.md`.

This document walks actual Hafs behavior through every target layer. It is not
a legacy JSON specification. Identifiers are illustrative and omitted fields
use their defaults.

## 1. Reading the examples

The pipeline is:

```text
source bytes
  -> Grapheme / GraphemeCluster
  -> source-only LetterUnit
  -> RecitedLetter / RecitedGrapheme after expansion and boundary realization
  -> semantic Segment
  -> GraphemeAlignment + typed TajweedOccurrence + RealizationEvent
  -> Arabic and phoneme renderers
```

Conventions used below:

- `g3` is a source `GraphemeId`; `l2` is a source `LetterUnitId`;
- `r4` is a `RecitedLetterId`; `rg5` is a `RecitedGraphemeId`;
- `s6` is a semantic `SegmentId`; `t7` is a Tajwīd occurrence id;
- a `LetterUnit` always has source graphemes;
- a generated `RecitedLetter` always has a `RealizationEvent`;
- `following` is a trigger/context letter; `target` means actual assimilation.

## 2. Source tokenization and exact reconstruction

### 2.1 Ordinary letter and harakah: `بِ`

```text
source UTF-8 / string: "بِ"

Grapheme(g0, "ب", word=0, offset=0)
Grapheme(g1, "ِ", word=0, offset=1)
GraphemeCluster(c0, graphemes=(g0, g1))

LetterUnit(
  id=l0,
  letter=Letter.BAA,
  base_graphemes=(g0,),
  harakah=Harakah(KASRA, graphemes=(g1,)),
)

RecitedLetter(r0, form=LetterForm(BAA, KASRA), source_letters=(l0,))
ConsonantSegment(s0, B)
VowelSegment(s1, I, SHORT)

g0 -> REALIZES (s0)
g1 -> REALIZES (s1)
```

The source serializer joins `g0.char + g1.char` and must reproduce the exact
source bytes. `SOURCE_EXACT` produces `بِ`; the phoneme renderer maps `s0,s1`
to `b,i`.

### 2.2 Explicit sukūn versus bare

`نْ` produces `Harakah(SUKUN)`; bare `ن` produces `harakah=None`. They are not
collapsed by normalization. A source convention may establish that a bare
nūn in a particular reviewed sequence is semantically sākin, but rules ask a
typed `is_sakin(recited_letter, convention)` predicate—they do not assume that
every missing mark means sukūn.

This fixes the current implementation shortcut where `Noon.phonemize_letter`
treats any diacritic, including explicit sukūn, as a plain nūn and only applies
nūn-sākinah rules to a bare nūn.

### 2.3 A manually inserted letter

This is invalid:

```python
LetterUnit(letter=Letter.ALEF, base_graphemes=())  # construction error
```

An inserted alef instead has an event and recited provenance:

```text
RealizationEvent(e0, reason=WAQF_IWAD, source=(g_fathatan, ...))
RecitedGrapheme(rg0, "ا", source=(), event=e0, segments=(s_long_a,))
RecitedLetter(r0, form=LetterForm(ALEF), source_letters=(), event=e0,
              graphemes=(rg0,))
```

## 3. Full carriers, small vowels, and semivowels

### 3.1 Fatha plus full alef

```text
...َا
fatha grapheme -> REALIZES long-A segment s0
alef grapheme  -> CARRIES s0
VowelSegment(s0, quality=A, length=LONG)
```

The alef is its own `LetterUnit`. The fatha and carrier share one sound; the
source serializer still preserves both scalars.

### 3.2 Dagger alef and mini wāw/yāʾ

```text
dagger alef -> SmallVowel(DAGGER_ALEF, A) -> long-A segment
mini wāw    -> SmallVowel(MINI_WAW, U)     -> long-U segment when realized
mini yāʾ    -> SmallVowel(MINI_YAA, I)     -> long-I segment when realized
```

They are first-class written values composed on a source `LetterUnit`, not a
generic “extension” list. Their source graphemes align directly to the vowel
segment. The segment has no `mini` flag because a full and small carrier can
be phonologically equivalent.

### 3.3 Full wāw/yāʾ role change

The same immutable source form can resolve differently:

| Context | Written unit | Recited result |
|---|---|---|
| matching preceding vowel | full wāw/yāʾ | long-vowel carrier |
| incompatible vowel / explicit consonantal use | full wāw/yāʾ | consonant `w/j` |
| fatha + sākin wāw/yāʾ in wasl | full wāw/yāʾ | semivowel/diphthong |
| same leen site at waqf | full wāw/yāʾ | `MaddOccurrence(LEEN)` |
| otiose/redundant spelling | full wāw/yāʾ | `SILENT` with realization cause |

Waqf removes/replaces the effective final harakah before this role is
resolved. No source `LetterUnit` is mutated.

## 4. Many-to-one script normalization

### 4.1 Tanween spellings

These may all produce the same canonical `Tanween(DAMM)` while retaining exact
source graphemes:

```text
Hafs/standard dammatan U+064C
Warsh alternate damm tanween U+065E
reviewed Warsh damma U+064F + mini mīm U+06E2 composite
```

The composite produces:

```text
LetterUnit(
  tanween=Tanween(DAMM, graphemes=(g_damma, g_mini_meem)),
  hints=(OrthographicHint(IQLAB, graphemes=(g_mini_meem,)),),
)
```

If the following recited letter is `ب`, shared rule code independently creates
`NoonOccurrence(rule=IQLAB, trigger=TANWEEN, following=ب, target=None)`. The
hint validates that result; it cannot force it.

### 4.2 Nūn plus mini mīm

Bare nūn + `U+06E2` normalizes to semantic nūn sākinah plus the same iqlāb
hint. The mini mīm is neither a `SmallVowel` nor a second pronounced mīm.

### 4.3 Hamzat al-waṣl

Hafs `ٱ` and a reviewed Warsh initial-alef sequence can produce the same
canonical hamzat-al-waṣl form. Their `Grapheme`s remain different. Starting or
joining is then decided by the shared boundary realization—not by a global
`codepoint -> sound` table.

## 5. Nūn sākinah and tanween: all five outcomes

| Outcome | Stored record | Result |
|---|---|---|
| iẓhār ḥalqī | `NoonOccurrence(trigger, following=throat letter, target=None)` | clear nūn segment |
| ikhfāʾ ḥaqīqī | `NoonOccurrence(trigger, following=ikhfāʾ letter, target=None)` | hidden/placeless nasal |
| iqlāb | `NoonOccurrence(trigger, following=ب, target=None)` | hidden mīm-like/placeless nasal |
| idghām bi-ghunnah | `NoonOccurrence(trigger, following=ي/ن/م/و, target=that letter)` | one shared nasalized target segment |
| idghām bilā-ghunnah | `NoonOccurrence(trigger, following=ل/ر, target=that letter)` | one shared non-nasal target segment |

For nūn idghām, the source nūn alignment is `ASSIMILATED` and the target
letter realizes the shared result. For tanween idghām, the tanween's nūn
component shares the target result while its short-vowel segment remains on
the carrying letter.

Stopping at the intervening word boundary prevents all five cross-boundary
decisions from inspecting the next word; the stopped nūn/tanween realization
is built first.

## 6. Mīm and ghunnah

| Case | Variant | Key fields |
|---|---|---|
| nūn/mīm with shaddah | `GhunnahOccurrence` | mushaddad letter subject, nasal geminate result |
| mīm sākinah + ب | `MeemOccurrence(IKHFAA_SHAFAWI)` | `following=ب`, `target=None` |
| mīm sākinah + م | `MeemOccurrence(IDGHAM_SHAFAWI)` | `following=target=م`, shared nasal geminate |
| mīm sākinah + other | `MeemOccurrence(IZHAR_SHAFAWI)` | following explicit, `target=None`, clear mīm |

The exhaustive iẓhār occurrence is useful even when the output token is the
plain baseline `m`; annotation is not limited to mutations.

## 7. Other idghām families and lām shamsiyyah

```text
IdghamOccurrence(
  core=(rule, subject recited letter(s), result segment(s)),
  target=<actual receiving recited letter>,
  completeness=KAMIL | NAQIS,
)
```

The shared finite Arabic pair tables select:

- mutamāthilayn: identical consonants;
- mutaqāribayn: current implemented pairs such as `ل -> ر`, `ق -> ك`;
- mutajānisayn: current same-articulation pairs, with kāmil/naqis in the
  occurrence field;
- lām shamsiyyah: article lām as subject and the sun letter as target.

The renderer sees only the resulting semantic consonant (plain, geminated,
nasalized, etc.). It does not contain separate idghām logic.

## 8. Tafkhīm, tarqīq, and complex reasons

### 8.1 Inherent istiʿlāʾ

```text
EmphasisOccurrence(
  subject_kind=INHERENT_LETTER,
  reason=InherentEmphasisReason(),
  result=(emphatic consonant/vowel segments),
)
```

### 8.2 Rāʾ

The Hafs classifier emits one of these explanatory snapshots:

| Decision shape | Example facts stored |
|---|---|
| direct harakah | rāʾ fatha/damma -> heavy; kasra -> light |
| sākin after harakah | previous letter id + previous fatha/damma/kasra |
| sākin after sākin | intervening consonant id + earlier vowel bearer/id |
| kasra before istiʿlāʾ | previous kasra letter + following same-word istiʿlāʾ letter |
| waqf look-back | boundary id + effective earlier vowel bearer |

For example, a stopped rāʾ whose immediately previous consonant is also sākin
uses `WaqfLookbackReason` or `SakinAfterSakinReason`; a generic tuple of
“condition graphemes” would not say which role each item played.

Warsh can later supply a different classifier, but it returns the same decision
and the same `EmphasisOccurrence` variants. Until researched, the Warsh rāʾ
pipeline is unsupported rather than assumed equal to Hafs.

### 8.3 Lām in the name of Allah

The lām occurrence has `subject_kind=LAM_ALLAH` and
`LamAllahReason(previous_vowel=sX)`. The implicit long `ā` is separately:

```text
MaddOccurrence(
  madd_type=TABII,
  context=ALLAH_DAGGER_ALEF,
  cause=NoSpecialMaddCause(),
)
```

Its inserted dagger alef/recited grapheme points to the Allah realization
event; no source grapheme is fabricated.

## 9. Qalqalah and render composition

At medial/permanent sukūn:

```text
QalqalahOccurrence(degree=SUGHRA, boundary=None)
```

At a selected stop on a qalqalah consonant:

```text
QalqalahOccurrence(degree=KUBRA, boundary=b7)
```

The semantic result can render as the consonant token plus a mapped release
token (`d`, `Q`). Qalqalah is not a reason to put rule logic in the renderer.

## 10. Boundary realization examples

### 10.1 Hamzat al-waṣl at ibtidāʾ

For started `ٱلْحَمْدُ`, the source hamzat-al-waṣl remains source-linked. A
`HAMZA_WASL_IBTIDA` event creates the effective hamza/vowel recited output and
segments. For connected recitation, `HAMZA_WASL_WASL` aligns the source sign as
silent and creates no hamza segment.

### 10.2 Iltiqāʾ al-sākinayn

For a long vowel before connected hamzat al-waṣl, a realization event shortens
the vowel and silences the carrier. For tanween before hamzat al-waṣl, an
inserted kasra has event provenance. Neither is a Tajwīd rule occurrence.

### 10.3 Tāʾ marbūṭah at waqf

The source `ة` remains exact. A `TAA_MARBUTA_WAQF` event replaces the recited
letter form/result with stopped hāʾ realization; source alignments explain the
replacement.

### 10.4 Waqf ʿiwaḍ

Stopping on supported fathatan:

```text
WAQF_IWAD event: remove tanween n component; add/replace long-A realization
MaddOccurrence(type=TABII, context=WAQF_IWAD, carrier=<recited alef>, ...)
```

The event describes the writing/sound transformation; the madd occurrence
classifies the resulting Tajwīd site.

### 10.5 ʿĀriḍ and leen

- long vowel before a consonant made sākin by the selected stop:
  `MaddOccurrence(ARID_LISSUKUN, cause=BoundarySukunCause(...))`;
- fatha + consonantal sākin wāw/yāʾ before the stopped final consonant:
  `MaddOccurrence(LEEN, cause=LeenMaddCause(...))`.

Both are absent in the joined realization when their stopping cause is absent.

## 11. All six current madd classifications and contexts

| Madd type | Semantic cause | Example shape |
|---|---|---|
| ṭabīʿī | long vowel with no stronger cause | compatible harakah + carrier |
| wājib muttaṣil | following hamza in same lexical word | `HamzaMaddCause(same_word=True)` |
| jāʾiz munfaṣil | following hamza across joined word boundary | `HamzaMaddCause(same_word=False)` |
| lāzim | following permanent sākin consonant | `PermanentSukunCause` |
| ʿāriḍ li-s-sukūn | boundary-created final sukūn | `BoundarySukunCause` |
| leen | fatha + sākin semivowel before boundary-created sukūn | `LeenMaddCause` |

`MaddContext` then records ordinary, Allah dagger alef, waqf ʿiwaḍ,
pronoun-hāʾ ṣilah, plural-mīm ṣilah, or muqaṭṭaʿāt. For example, a ṣilah vowel
followed by hamza can be `JAIZ_MUNFASIL + PRONOUN_HAA_SILAH`; the two axes do
not overwrite each other.

No record contains duration, minimum, maximum, or count.

## 12. Complete muqaṭṭaʿāt derivation audit

### 12.1 The fourteen stored names

The shared resource stores each Arabic name once:

| Compact | Recited spelling | Derived madd |
|---|---|---|
| `ا` | `أَلِفْ` | none |
| `ح` | `حَا` | ṭabīʿī |
| `ي` | `يَا` | ṭabīʿī |
| `ط` | `طَا` | ṭabīʿī + inherent tafkhīm |
| `ه` | `هَا` | ṭabīʿī |
| `ر` | `رَا` | ṭabīʿī + rāʾ tafkhīm |
| `ل` | `لَامْ` | lāzim; final permanent sākin mīm |
| `م` | `مِيمْ` | lāzim; final permanent sākin mīm |
| `س` | `سِينْ` | lāzim; final permanent sākin nūn |
| `ك` | `كَافْ` | lāzim; final permanent sākin fāʾ |
| `ص` | `صَادْ` | lāzim + tafkhīm; dāl has qalqalah by boundary |
| `ق` | `قَافْ` | lāzim + tafkhīm |
| `ن` | `نُونْ` | lāzim; final permanent sākin nūn |
| `ع` | `عَيْنْ` | lāzim in current output, `carrier_form=LEEN` |

The ordinary lāzim classifier must accept a permanent sākin **plain
consonant**, not only today's shaddah/ghunnah output tokens. If that consonant
is geminated or assimilates into the next name,
`PermanentSukunCause.realization` records `GEMINATED` or `ASSIMILATED` for the
muthaqqal detail; `PLAIN` records the mukhaffaf case.

`عَيْنْ` is a real special carrier shape: its yāʾ is leen rather than an
ordinary long-vowel carrier. Hafs performance traditions permit special
length choices, but this phonemizer intentionally stores classification and
context, not counts. A domain cross-check for this exception and the connected
Āl ʿImrān case is recorded in [this madd-lāzim reference](https://surahquran.com/Tajweed/mad-lazem-en.html).

### 12.2 Every compact resource form

The current YAML has fourteen forms, thirty source locations, and twenty-nine
surah openings (Ash-Shūrā has `حمٓ` and `عٓسٓقٓ` as two source words).

| Compact form | Locations | Derived internal interactions |
|---|---|---|
| `حمٓ` | 40,41,42,43,44,45,46:1 | ḥā ṭabīʿī; mīm lāzim; final mīm gets iẓhār shafawī before the following effective `ت/ع/و` when joined |
| `الٓمٓ` | 2,3,29,30,31,32:1 | lām final mīm → mīm initial mīm: idghām shafawī; lām lāzim muthaqqal; mīm lāzim mukhaffaf; following-word case below |
| `الٓر` | 10,11,12,14,15:1 | lām lāzim; lām-final mīm before rāʾ is iẓhār shafawī; rāʾ ṭabīʿī/tafkḥīm |
| `الٓمٓصٓ` | 7:1 | lām→mīm idghām shafawī; mīm-final mīm before ṣād iẓhār; ṣād lāzim/tafkḥīm; stopped dāl qalqalah kubrā, joined dāl sughrā |
| `الٓمٓر` | 13:1 | lām→mīm idghām shafawī; mīm-final mīm before rāʾ iẓhār; rāʾ ṭabīʿī/tafkḥīm |
| `كٓهيعٓصٓ` | 19:1 | kāf lāzim; hā/yā ṭabīʿī; ʿayn lāzim-leen; ʿayn-final nūn before ṣād ikhfāʾ; ṣād lāzim/tafkḥīm/qalqalah by boundary |
| `طسٓمٓ` | 26,28:1 | ṭā ṭabīʿī/tafkḥīm; sīn-final nūn assimilates into mīm with ghunnah; sīn lāzim muthaqqal; mīm lāzim; final mīm before `ت` is iẓhār when joined |
| `طسٓ` | 27:1 | ṭā ṭabīʿī/tafkḥīm; sīn lāzim; if continued into `تِلْكَ`, final nūn has ikhfāʾ; a selected stop cancels it |
| `طه` | 20:1 | ṭā and hā ṭabīʿī; ṭā/its vowel emphatic |
| `يسٓ` | 36:1 | yā ṭabīʿī; sīn lāzim; final nūn remains clear before following wāw by named Hafs exception |
| `عٓسٓقٓ` | 42:2 | ʿayn-final nūn before sīn ikhfāʾ; sīn-final nūn before qāf ikhfāʾ; all three long names get their derived madd details |
| `صٓ` | 38:1 | ṣād lāzim/tafkḥīm; final dāl qalqalah degree follows selected boundary |
| `قٓ` | 50:1 | qāf lāzim/tafkḥīm; final fāʾ clear before following wāw |
| `نٓ` | 68:1 | nūn lāzim; final nūn remains clear before following wāw by named Hafs exception |

### 12.3 Following-word audit

The lexical expansion must not stop at the compact opening unless the selected
boundary does. Important following contexts are:

| Opening | Following source word | Joined consequence |
|---|---|---|
| `حمٓ` 42:1 | `عٓسٓقٓ` 42:2 | final mīm before ʿayn: iẓhār shafawī; verse-stop selection cancels the cross-boundary occurrence |
| `الٓمٓ` 3:1 | `ٱللَّهُ` 3:2 | named connected realization gives the final mīm-name fatha before silent hamzat al-waṣl; do not apply mīm-sākinah iẓhār |
| `طسٓ` 27:1 | `تِلْكَ` | nūn before tāʾ: ikhfāʾ when joined |
| `يسٓ` 36:1 | `وَٱلْقُرْءَانِ` | named Hafs clear-nūn exception instead of normal nūn→wāw idghām |
| `نٓ` 68:1 | `وَٱلْقَلَمِ` | named Hafs clear-nūn exception instead of normal nūn→wāw idghām |
| `صٓ`, `قٓ` | following wāw words | no nūn/mīm boundary rule; ordinary consonant continuation |

Other forms still receive exhaustive plain outcomes (for example final mīm
iẓhār shafawī), even if the legacy special YAML omitted them because no token
mutated.

### 12.4 One fully expanded record: `الٓمٓ`

```text
source compact graphemes: ا ل ◌ٓ م ◌ٓ
LEXICAL_EXPANSION event e0 points to the compact source letters

recited names:
  أَلِفْ | لَامْ | مِيمْ

RecitedWord rw0 (ALIF), rw1 (LAM), rw2 (MEEM), all source_word_indexes=(0,)
boundaries: EDGE -> rw0 JOIN rw1 JOIN rw2 -> projected source boundary

derived source-linked RecitedLetters:
  name ALIF: hamza+a, lam+i, fa+sukun
  name LAM:  lam+a, alef carrier, meem+sukun
  name MEEM: meem+i, yaa carrier, meem+sukun

segments before cross-name rule:
  ... l, long-a, m | m, long-i, m

occurrences:
  MaddOccurrence(LAZIM, context=MUQATTAAT,
                 cause=PermanentSukunCause(meem-of-LAM,
                                            realization=ASSIMILATED))
  MeemOccurrence(IDGHAM_SHAFAWI,
                 subject=final-meem-of-LAM,
                 following=target=initial-meem-of-MEEM,
                 result=shared nasal geminate)
  MaddOccurrence(LAZIM, context=MUQATTAAT,
                 cause=PermanentSukunCause(final-meem-of-MEEM,
                                            realization=PLAIN))
```

The source renderer still returns compact `الٓمٓ`. `RECITED_ARABIC` returns the
derived spelling. The phoneme renderer maps the final semantic segments; no
muqaṭṭaʿāt phoneme array survives.

## 13. Render-map examples

After rules, these are ordinary map lookups:

| Semantic segment/features | Possible configured token |
|---|---|
| `Consonant(N)` | `n` |
| placeless hidden nasal | `ŋ` |
| `Consonant(W, geminated=True)` | `ww` |
| `Consonant(W, nasalized=True)` | `w̃` |
| `Consonant(J, geminated=True)` | `jj` |
| `Consonant(J, nasalized=True)` | `j̃` |
| emphatic rāʾ | `rˤ` |
| long emphatic A | `aˤ:` |
| qalqalah release | `Q` |

The written Arabic key `ن` can seed baseline consonant identity, but it cannot
select ikhfāʾ/idghām/iqlāb. That decision is already represented in semantic
features and an occurrence.

## 14. Projection examples from one graph

From the same aggregate:

- source text joins exact `Grapheme.char` values;
- recited Arabic joins selected `RecitedGrapheme`s with render options;
- phoneme output renders ordered `Segment`s;
- letter/character mapping follows alignments and recited grapheme segments;
- silence queries `AlignmentKind.SILENT` and its event cause;
- Tajwīd annotation walks `TajweedOccurrence` variants;
- madd annotation filters `MaddOccurrence` from that collection;
- highlighting follows source/recited grapheme → segment links.

No projection runs nūn, madd, silence, boundary, or muqaṭṭaʿāt detection again.

## 15. Every current `TajweedRule` tag has one target owner

| Current tag(s) | Target representation |
|---|---|
| `noon_ghunnah`, `meem_ghunnah` | `GhunnahOccurrence` |
| `ikhfaa_noon`, `ikhfaa_tanween` | one `IKHFAA_HAQIQI` `NoonOccurrence`, distinguished by trigger |
| `iqlab_noon`, `iqlab_tanween` | one `IQLAB` `NoonOccurrence`, distinguished by trigger |
| `idgham_ghunnah_noon`, `idgham_ghunnah_tanween` | one `IDGHAM_BI_GHUNNAH` `NoonOccurrence` with real target |
| `idgham_bila_ghunnah_noon`, `idgham_bila_ghunnah_tanween` | one `IDGHAM_BILA_GHUNNAH` `NoonOccurrence` with real target |
| `ikhfaa_shafawi`, `idgham_shafawi` | `MeemOccurrence`; target only for idghām |
| `lam_shamsiyah` | `IdghamOccurrence(LAM_SHAMSIYYAH)` |
| `idgham_mutamathilayn`, `idgham_mutaqaribayn` | `IdghamOccurrence` |
| `idgham_mutajanisayn_kamil`, `idgham_mutajanisayn_naqis` | one rule plus `completeness` field |
| `tafkheem` | `EmphasisOccurrence(TAFKHEEM)`; exhaustive tarqīq is newly explicit |
| `qalqala_sughra`, `qalqala_kubra` | one `QalqalahOccurrence` plus `degree` |
| `madd_tabii`, `madd_wajib_muttasil`, `madd_jaiz_munfasil`, `madd_lazim`, `madd_arid_lissukun`, `madd_leen` | six `MaddType` values in `MaddOccurrence` |
| `vowel_silent` | `GraphemeAlignment(SILENT)` + typed realization cause |
| `hamza_wasl_silent`, `hamza_wasl_fatha`, `hamza_wasl_kasra`, `hamza_wasl_damma` | hamzat-al-waṣl `RealizationEvent`, recited writing, and segments |
| `silent_iltiqaa_sakinayn`, `iltiqaa_sakinayn_tanween` | iltiqāʾ `RealizationEvent` |

The new exhaustive iẓhār, tarqīq, and mīm-iẓhār occurrences have no legacy
mutation tag; they are intentional additions required for a complete
annotation projection.

## 16. Implementation fixture checklist

The implementation is not accepted until fixtures cover:

- source byte round-trip for every Hafs accepted sequence family and every
  accepted Warsh subset family;
- explicit sukūn versus bare state;
- full/small carrier equivalence and attribution;
- all five nūn/tanween outcomes for nūn and tanween, within/across words;
- all three mīm-sākinah outcomes and ghunnah mushaddadah;
- every current general-idghām pair and kāmil/naqis result;
- direct, look-back, same-word istiʿlāʾ, and waqf rāʾ reasons;
- lām of Allah heavy/light plus implicit dagger alef;
- qalqalah sughrā/kubrā under different boundaries;
- hamzat al-waṣl, iltiqāʾ, tāʾ marbūṭah, ʿiwaḍ, ʿāriḍ, and leen;
- all six madd types and every supported `MaddContext`;
- all fourteen muqaṭṭaʿāt names, fourteen forms, thirty source locations, and
  following-word cases;
- `SOURCE_EXACT`, `RECITED_ARABIC`, `RECITED_WITH_SILENT`, full-token, and
  simple-token rendering from the same graph;
- two phonemizer instances (`HAFS`, accepted `WARSH` normalization) in either
  construction order with no shared mutable state.
