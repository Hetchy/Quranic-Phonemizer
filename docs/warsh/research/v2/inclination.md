# Warsh inclination

This document specifies fath, taqlil, and imala kubra for Warsh from Nafi via
al-Azraq. It owns domain classification, boundary masking, and the authored
registers needed by the classifier. Public selector names, values, and defaults
remain in [`docs/variants.md`](../../../variants.md).

The selected King Fahd script is evidence, not the rule source. Its U+06EA mark
is overloaded and must not select a vowel quality by itself. Projection details
remain in [`script-projection.md`](script-projection.md).

## Sound model

The transmitted quality order is:

```text
fath < taqlil < imala kubra
```

Taqlil is the intermediate quality between fath and full imala. The classical
sources describe relative articulation, not exact formant targets
([Al-Wafi](https://www.islamweb.net/ar/library/content/245/28/),
[Al-Nashr](https://www.islamweb.net/ar/library/content/70/158/)). The project
uses the following broad engineering representatives:

| Domain quality | Typed quality | Rule tag | Broad token |
| --- | --- | --- | --- |
| Fath | `A` | none | `a` or `a:` |
| Taqlil | `TAQLIL` | `taqlil` | `ɛ` or `ɛ:` |
| Imala kubra | `KUBRA` | `imala` | `e` or `e:` |

The `/ɛ, ɛ:/` and `/e, e:/` choices are project modeling choices. They are not a
claim that the sources attest those exact IPA values or that every reciter has
one invariant acoustic target.

`TAQLIL` and `KUBRA` are distinct typed qualities, and `taqlil` and `imala` are
distinct rule tags. Ordinary Warsh taqlil is never gated by an extra phoneme.
The `imala` extra phoneme affects rendering only:

| Typed quality | `imala` enabled | `imala` disabled for Warsh |
| --- | --- | --- |
| `TAQLIL` | `ɛ` or `ɛ:` | `ɛ` or `ɛ:` |
| `KUBRA` | `e` or `e:` | `ɛ` or `ɛ:` |

Disabling the extra phoneme does not change the `KUBRA` fact or remove the
`imala` rule. It only makes kubra render with the Warsh taqlil fallback. This is
how the fixed Haa of `طَه۪ۖ` remains one domain reading without a public
selector.

## Classification order

The classifier runs on canonical letters, nuclei, lexical facts, and resolved
boundaries. It must apply this ownership order before emitting a rule:

1. Resolve whether the target nucleus exists in the requested state. A deleted
   alif has no performed quality in that state.
2. Apply the fixed kubra register.
3. Apply a coupled lam-and-inclination owner. The coupled owner returns one
   compatible pair and prevents a second independent lam decision.
4. Apply named opening-letter, verse-head, raa-origin, alif-before-final-raa,
   and fixed lexical registers.
5. Apply a public lexical or systematic selector from `docs/variants.md`.
6. Apply the ordinary dhat-yaa predicate.
7. Otherwise retain fath.

An occurrence has one effective quality. A more specific owner masks a less
specific one; it does not stack a second inclination rule on the same nucleus.

## Domain predicates and fixed registers

### Fixed kubra

The only fixed kubra target in this scope is the Haa nucleus of `طَه۪ۖ`, source
20:1:1 and canonical 20:1. It always has typed quality `KUBRA` and the `imala`
rule. Rendering falls back to taqlil when the `imala` extra phoneme is disabled.
The stronger inclination of this Haa is transmitted in the opening-letter
chapter ([Al-Nashr](https://www.islamweb.net/ar/library/content/70/169/)).

### Fixed taqlil openings

The following are closed registers:

| Register | Exact canonical sites | Count |
| --- | --- | ---: |
| Haa of the Hawamim | 40:1, 41:1, 42:1, 43:1, 44:1, 45:1, 46:1 | 7 |
| Raa of the `الر` and `المر` openings | 10:1, 11:1, 12:1, 13:1, 14:1, 15:1 | 6 |

Al-Nashr gives the Haa and Raa opening-letter readings and includes `المر` in
the Raa set ([source](https://www.islamweb.net/ar/library/content/70/169/)).
The v1 classification counted only five Raa openings because it matched `الر`
and missed `المر` at 13:1.

The Haa and Yaa of `كَهْيَعْص` are owned together by `maryam_haa_yaa`; the Yaa
of `يس` is owned by `yaseen_yaa`. Their closed scopes are 19:1 and 36:1
respectively, so neither falls through to the ordinary dhat-yaa classifier.
The two Maryam nuclei are one coupled choice. The Yaseen Yaa is independent
from the final Seen-noon wasl behavior
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/169/)).

### Dhat al-raa

A word-final eligible alif whose immediately preceding letter is raa is fixed
taqlil, whether or not it is a verse head. `أَرَاكَهُمْ` at canonical 8:43 is
the one named choice and is removed from the fixed set. The selected-script
v1 extraction contains 157 fixed dhat-al-raa targets after that exclusion.
Under the single-script decision the reviewed inclination-mark family supplies
these targets; the canonical predicate and the 157 count remain the
conformance reconciliation of the supplied set
([Al-Wafi](https://www.islamweb.net/ar/library/content/245/28/)).

### Alif before a final kasra raa

An alif immediately before a word-final raa with an original kasra is fixed
taqlil. The selected-script register has 192 targets. The predicate includes
forms such as `اَ۬لنّ۪ارِ`, `اَ۬لْكُفّ۪ارِ`, and `حِم۪ارِكَ`, but excludes:

- a non-final raa, including `تُمَارِ` and the `اَ۬لْجَوَارِ` family whose yaa is
  omitted by morphology;
- a doubled raa such as `مُضَارّٖ`, where the first raa is not the target final
  raa;
- a raa whose kasra is only caused by a suffix, such as `أَنصَارِيَ`; and
- an alif separated from the raa by another letter.

These conditions and exclusions are explicit in Al-Wafi
([source](https://www.islamweb.net/ar/library/content/245/28/)). `اَ۬لْجَارِ`
at canonical 4:36 and `جَبَّارِينَ` at 5:22 and 26:130 are removed from the
fixed set and owned by their named public selectors.

### Fixed lexical families

The fixed lexical register is keyed by canonical lexical identity, not by
display spelling:

| Family | Exact scope | Selected-corpus count |
| --- | --- | ---: |
| `كافرين` with yaa, definite or indefinite | Every inflection preserving that plural yaa; exclude `كافر`, `كافرة`, and `كافرون` | 93 |
| `التوراة` | Every occurrence | 18 |
| `رأى` in Surat al-Najm | 53:11 and 53:18 | 2 |

Together these are the 113 fixed lexical targets in the reviewed v1 export.
The source categories are supported by the fixed Warsh inclination discussion
in Al-Wafi ([source](https://www.islamweb.net/ar/library/content/245/28/)). A
generated register must assert the three subtotals separately so that a corpus
or spelling change cannot preserve only the misleading total.

### Verse heads

Warsh has fixed taqlil at eligible alif verse heads in exactly these 11 surahs:

```text
20, 53, 70, 75, 79, 80, 87, 91, 92, 93, 96
```

This is an endpoint predicate over the canonical verse ending, not a copied
word table. A pausal alif created only from fathatan is not an inclination
target. Dhat-al-raa and coupled-lam owners retain priority even when the token
is also a verse head
([Al-Wafi](https://www.islamweb.net/ar/library/content/245/28/)).

The one closed optional subset is the 25 pronominal-haa endings owned by
`haa_verse_heads`: canonical 79:27-32, 79:42, 79:44-46, and 91:1-15.
`ذِكْرَاهَا` at canonical 79:43 is excluded and fixed taqlil because its alif
follows raa. Al-Nashr and Al-Wafi state both the pronominal-haa choice and the
raa exception
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/164/),
[Al-Wafi](https://www.islamweb.net/ar/library/content/245/28/)).

### Ordinary dhat al-yaa and fixed fath exclusions

After the named owners above, an eligible final alif is dhat al-yaa when its
lexical or morphological origin is yaa. This includes yaa-origin nouns and
verbs, the productive `فعلى` and `فعالى` families, and augmented triliteral
forms whose inflection exposes yaa. The public `dhat_yaa` selector owns the
result. Orthographic alif maqsura is evidence but is not sufficient: origin is
a lexical/morphological fact
([Al-Wafi](https://www.islamweb.net/ar/library/content/245/28/)).

The following closed exclusions remain fixed fath even though their spelling
can resemble an eligible target:

| Exclusion | Exact scope | Selected-corpus count |
| --- | --- | ---: |
| `حَتَّى` | Every occurrence of the particle | 142 |
| `إِلَى` | Every standalone or prefixed occurrence of the particle | 434 |
| `عَلَى` | Every standalone or prefixed occurrence of the particle | 712 |
| `لَدَى` | Canonical 40:18; the 12:25 form is written with alif and is not a candidate | 1 |
| `زَكَى` | The unaugmented verb at 24:21; augmented `زَكَّى` forms remain eligible | 1 |
| `مَرْضَات` | Every occurrence, including the suffixed form at 60:1 | 5 |
| `ٱلرِّبَوٰا` or `رِّباٗ` | Every occurrence of the lexical family | 8 |
| `كِلَاهُمَا` | 17:23 | 1 |
| `مِشْكَوٰة` | 24:35 | 1 |

The first five spelling exclusions and the four Warsh-specific lexical
exclusions are stated in Al-Wafi
([written-yaa exclusions](https://www.islamweb.net/ar/library/content/245/28/),
[Warsh exclusions](https://www.islamweb.net/ar/library/content/245/28/)).
The authored data should store lexical keys and exact exceptional references;
it must not infer the exception from a source mark being absent.

The named choices `arakahum`, `al_jar`, and `jabbarin` are also removed from the
ordinary predicate. Their exact sites are canonical 8:43, both `اَ۬لْجَارِ`
tokens at 4:36, and 5:22 plus 26:130. See `docs/variants.md` for their public
outcomes.

## Boundary behavior

Inclination classifies a sounded nucleus, not an abstract written alif.

- If an eligible alif is deleted in wasl before a following sakin, no fath,
  taqlil, or kubra sound exists in that state and no inclination rule is
  emitted. At waqf the alif returns with its owned quality. Al-Wafi states that
  none of the three qualities is realizable after this deletion
  ([source](https://www.islamweb.net/ar/library/content/245/28/)).
- The same masking applies to a final alif suppressed by nunation in wasl. At
  plain waqf, the restored alif receives the selected or fixed quality.
- At `مُصَلّىٗۖ` (source 2:124:11, canonical 2:125) and `يَصْلَى اَ۬لنَّارَ`
  (source 87:12:2, canonical 87:12), wasl suppresses the inclined alif and the
  coupled owner realizes fath plus lam tafkheem. At waqf the selected coupled
  face manifests again.
- A selector remains a stable request even when its target is masked in the
  current state. Masking is not validation failure and does not rewrite the
  requested variant.

## Coupled lam sites

Inclination and lam weight are incompatible in only one pairing: an inclined
alif requires a light lam, while an emphatic lam requires fath. The classifier
therefore returns `taqlil` plus lam tarqiq or fath plus `tafkheem` as one owned
decision. It must never produce taqlil plus tafkheem
([Al-Nashr](https://islamweb.net/ar/library/content/70/192/)).

The closed register has ten sites:

| Owner | Canonical sites | Count |
| --- | --- | ---: |
| `lam_dhat_yaa` | 2:125, 17:18, 84:12, 87:12, 88:4, 92:15, 111:3 | 7 |
| `lam_verse_heads` | 75:31, 87:15, 96:10 | 3 |

Exact selected-script source keys and spellings are listed in
[`lam-tafkheem.md`](lam-tafkheem.md), which owns the lam side and the two
boundary masks.

## Source fixtures and manual sound checks

These fixtures prove source alignment. They are not the complete classifier:

| Source ref | Canonical ref | Exact selected text | Expected fact |
| --- | --- | --- | --- |
| 20:1:1 | 20:1 | `طَه۪ۖ` | Haa nucleus is fixed `KUBRA`. |
| 13:1:1 | 13:1 | `أَلَٓمِّٓر۪ۖ` | Raa nucleus is fixed `TAQLIL`; this is the v1 missed opening. |
| 40:1:1 | 40:1 | `ح۪مِٓۖ` | Haa nucleus is fixed `TAQLIL`. |
| 19:1:1 | 19:1 | `كَٓه۪ي۪عَٓصَٓۖ` | Haa and Yaa are one named pair. |
| 79:42:4 | 79:43 | `ذِكْر۪يٰهَآۖ` | Fixed taqlil, excluded from `haa_verse_heads`. |
| 91:13:7 | 91:13 | `وَسُقْيَاهَا` | One of the 25 pronominal-haa targets. |

Manual sequences use the broad project tokens:

```text
هُدَى
fath:   h u d a:
taqlil: h u d ɛ:

طَه۪ۖ, target Haa nucleus
typed KUBRA, imala enabled:  e:
typed KUBRA, imala disabled: ɛ:

صَلّ۪ىٰۖ, source 75:30:4, canonical 75:31
taqlil plus tarqiq: sˤ aˤ ll ɛ:
fath plus tafkheem:  sˤ aˤ lˤlˤ aˤ:
```

The two Haa renderings above must have identical typed quality and identical
`imala` rule ownership.

## Rule and source reach

For `taqlil` or `imala`, the occurrence classifies the target vowel sound. The
core subject is the slot whose nucleus changed. Source placement follows the
unit that owns that sound; transformed cells place the occurrence on the
vowel/carrier columns presenting it. An inclination witness such as U+06EA
stays provenance inside its owning unit and does not become an extra rule
participant.

The witness only attests the independently classified result. A mark with no
matching domain target is an adapter validation error; a domain target without
that mark is not silently changed to fath.

## Normative machine data

Do not import the v1 `imalah-classification.md` table as runtime data. It treats
all 2,569 U+06EA occurrences as one phenomenon, including 692 initial-alif
hamzat-al-wasl sequences, and its 2,481 word total therefore contains false
positives. It also records source-local ayah numbers as if they were canonical,
misses one Raa opening, and freezes the selected script's default choices as if
they were fixed law.

The normative Warsh package should own:

1. mark-supplied default targets from the reviewed inclination sequence
   families, with the structural predicates for dhat al-yaa, dhat al-raa,
   original final-raa kasra, and the 11 verse-head surahs retained as
   conformance reconciliation rather than runtime derivations;
2. closed lexical keys and exact coordinate sets from this document and
   `docs/variants.md`, which override or own their sites regardless of marks;
3. source-to-canonical coordinate fixtures for every closed set; and
4. a generated audit export containing every classified target, its owner,
   effective state, typed quality, and source witness.

Acceptance tests must reject overlap between owners, assert the fixed register
subtotals above, and reconcile every reviewed source witness against the
predicates, so a corpus or importer defect cannot silently change a supplied
quality.
