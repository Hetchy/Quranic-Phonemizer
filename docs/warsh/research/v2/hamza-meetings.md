# Warsh hamza meetings

This document owns adjacent qata hamzas inside one word and across a joined
word boundary. It defines the structural vowel matrix, the finite lexical
exceptions, boundary behavior, result sounds, and rule reach. A lone lexical
hamza is owned by [`single-hamza.md`](single-hamza.md); genuine wasl and naql
are owned by [`wasl-hamza.md`](wasl-hamza.md) and [`naql.md`](naql.md).

Public selector values, defaults, and full public scopes remain in
[`docs/variants.md`](../../../variants.md). The selectors are independent and
do not encode recitation counts or validate a historical route combination.

## Corpus register

The selected Warsh corpus contains 60 one-word adjacent-hamza sites:

| Shape | Count | Owner |
| --- | ---: | --- |
| Ordinary first A plus second A | 20 | `hamza_dhat_fath` |
| First A plus second I | 32 | Fixed tashil, except the five `أئمة` tokens |
| First A plus second U | 3 | Fixed tashil |
| `ءَأَعْجَمِيٌّ` | 1 | Fixed tashil |
| Triple-hamza forms | 4 | Fixed tashil on the second qata |

The selected corpus also contains 156 adjacent qata pairs across two words:

| First + second quality | Count | General outcome |
| --- | ---: | --- |
| A + A | 30 | `hamza_muttafiq`, except the two `jaa_aal` sites |
| I + I | 37 | `hamza_muttafiq`, except the two `hamza_kasr_yaa` sites |
| U + U | 1 | `hamza_muttafiq` |
| A + I | 19 | Fixed tashil |
| A + U | 1 | Fixed tashil |
| I + A | 29 | Fixed pure ibdal |
| U + A | 13 | Fixed pure ibdal |
| U + I | 26 | `hamza_damm_kasr` |

There is no I + U pair in the selected register. These counts are generated
from canonical qata identity and performed vowels, then checked against the
selected script. A source sign can attest a face but cannot create a meeting.

Exactly two pairs cross an ayah boundary within the same surah:

- source `14:29:18 -> 14:30:1`, canonical `14:27:18 -> 14:28:1`, is U+A; and
- source `19:1:6 -> 19:2:1`, canonical `19:2:5 -> 19:3:1`, is A+I.

They activate only under a direct joined-ayah boundary plan. No pair crosses a
surah boundary; corpus adjacency alone may not create one.

## One-word structural matrix

The first hamza is the open interrogative qata and always remains full. The
second qata supplies the branch. Al-Wafi defines vowel-conditioned tashil as
between the hamza and the carrier matching its own vowel
([source](https://www.islamweb.net/ar/library/content/245/14/)); Al-Nashr gives
the one-word Warsh faces and exceptions
([source](https://www.islamweb.net/ar/library/content/70/103/)).

### Ordinary second A

The 20 ordinary sites use `hamza_dhat_fath`, subject to the two pausal masks
below. For
`ءَآنذَرْتَهُمُۥٓ`, source 2:5:6, canonical 2:6:6:

| Effective face | Relevant result | Rules |
| --- | --- | --- |
| Ibdal | `ʔ a: ŋ ð a rˤ ...` | `ibdal_hamza` on the replacement A and `madd_lazim` because fixed noon sukun follows. |
| Tashil | `ʔ a ʔ̞ a ŋ ð a rˤ ...` | `tashil` on the eased second onset; the first qata stays full. |

At a site whose next segment is moving, the ibdal-created long receives
`madd_tabii` instead of `madd_lazim`. It is not `madd_badal`: this carrier is
an incidental result of the selected two-hamza face, not the lexical badal
origin classified in [`madd-badal.md`](madd-badal.md).

The following sakin noon is independently `ikhfaa` before dhal and
renders as `ŋ`; the sakin raa after fatha is independently `tafkheem` and
renders as `rˤ`. Neither ordinary rule belongs to the hamza face.

The two bare `أَأَنتَ` sites are the pausal exception: selected source
`5:118:7`, canonical `5:116:7`, and selected/canonical `21:62:2`. Both faces
apply in continuing reading and ibtidaa, but a complete full-sukun waqf forces
tashil because the ibdal face would create three consecutive sukuns. The
selector remains legal; its ibdal value is masked only in that boundary state.
Suffixed forms do not take this fallback
([Al-Nashr, pausal restriction](https://islamweb.net/ar/library/content/70/112/)).

### Second I and U

Ordinary second-I and second-U forms are fixed tashil:

| Quality | Selected source and refs | Canonical ref | Relevant result |
| --- | --- | --- | --- |
| I | `أَئِنَّكُمْ`, source 6:20:19 | 6:19:19 | `ʔ a ʔ̞ i ñ a k u m ...` |
| U | `اَوْ۟نَبِّئُكُم بِخَيْرٖ`, source 3:15:2-3 | 3:15:2-3 | `ʔ a ʔ̞ u n a bb i ʔ u k u ŋ b i ...` in its actual joined context |
| U | `اَ۟نزِلَ`, source 38:7:1 | 38:8:1 | `ʔ a ʔ̞ u ŋ z i l a ...` |
| U | `اَ۟لْقِيَ`, source and canonical 54:25:1 | 54:25:1 | `ʔ a ʔ̞ u l q i j a ...` |

Each emits `tashil` on the second hamza in wasl, waqf, and ibtidaa. Disabling
the extra token changes `ʔ̞` to rendered `ʔ`; it does not remove the eased
typed state or the rule.
The ellipses mark continuing spans; any word ending or plural-mim boundary
outside the hamza meeting follows its independent boundary rule.

The held noon in `أَئِنَّكُمْ` independently emits
`ghunnah_mushaddadah`. The hidden noon in `اَ۟نزِلَ` independently emits
`ikhfaa`. At `اَوْ۟نَبِّئُكُم بِخَيْرٖ`, ordinary `ikhfaa_shafawi`
owns the displayed default-open `/ŋ/`; the shared closed face renders `/m̃/`
instead. Those ordinary rules do not extend the reach of `tashil`.

### Aimma

Five tokens form the closed `hamza_aimma` exception within the 32 second-I
sites:

| Selected source ref | Canonical ref | Exact selected text |
| --- | --- | --- |
| 9:12:11 | 9:12:11 | `أَي۪مَّةَ` |
| 21:72:2 | 21:73:2 | `أَئِمَّةٗ` |
| 28:4:10 | 28:5:10 | `أَئِمَّةٗ` |
| 28:41:2 | 28:41:2 | `أَئِمَّةٗ` |
| 32:24:3 | 32:24:3 | `أَئِمَّةٗ` |

Al-Nashr authenticates both faces at these five forms
([source](https://www.islamweb.net/ar/library/content/70/105/)). Tashil gives
`ʔ a ʔ̞ i m̃ a ...`; ibdal gives moving yaa, `ʔ a j i m̃ a ...`. The moving
yaa is consonantal and emits `ibdal_hamza` without a madd rule.
The held meem independently emits `ghunnah_mushaddadah` in both faces.

### Fixed forms

`ءَآعْجَمِيّٞ`, source 41:43:9, canonical 41:44:9, is fixed tashil:
In its actual joined context before the following `وَعَرَبِيّٰ`, the relevant
span is `ʔ a ʔ̞ a ʕ ʒ a m i jj u w̃ a ʕ a rˤ aˤ ...`. Ordinary tanwin-to-waw
idgham owns `/w̃/`. The form is excluded from `hamza_dhat_fath`
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/103/)).

The four triple-hamza sites are:

| Family | Selected source ref | Canonical ref | Exact selected text |
| --- | --- | --- | --- |
| `أَءَامَنتُم` | 7:122:3 | 7:123:3 | `ءَاٰ۬مَنتُم` |
| `أَءَامَنتُم` | 20:70:2 | 20:71:2 | `ءَاٰ۬مَنتُم` |
| `أَءَامَنتُم` | 26:48:2 | 26:49:2 | `ءَاٰ۬مَنتُم` |
| `أَءَالِهَتُنَا` | 43:58:2 | 43:58:2 | `ءَاٰ۬لِهَتُنَا` |

They have fixed `ʔ a ʔ̞ a: ...`: the first interrogative qata remains full,
the second explicit qata emits `tashil`, and the existing following long A
keeps `madd_badal` without `madd_tabii`. Do not emit `ibdal_hamza` for that
already lexical badal carrier. Al-Wafi distinguishes these fixed forms from the
ordinary open-second-hamza choice
([source](https://www.islamweb.net/ar/library/content/245/14/)).

For a full ordinary-context check, `أَءَامَنتُم` continues as
`ʔ a ʔ̞ a: m a ŋ t u m ...`: the sakin noon independently emits
`ikhfaa` before taa. `أَءَالِهَتُنَا` continues as
`ʔ a ʔ̞ a: l i h a t u n a: ...`.

## Across-word structural matrix

Across-word meetings exist only when the two words are joined. The first word
must end in a moving qata and the next word must begin with a moving qata.
Al-Wafi defines that exact two-word boundary and the Warsh matrix
([source](https://www.islamweb.net/ar/library/content/245/16/)); Al-Nashr gives
the matching-vowel faces
([source](https://www.islamweb.net/ar/library/content/70/107/)).

For any pair:

| Boundary state | Result |
| --- | --- |
| Joined through the boundary | Apply the matrix below. A later stop on the second word does not undo the meeting. |
| Complete stop after the first word | End the first word normally. If the requested range continues, begin the second word with its full qata. |
| Ibtidaa at the second word | Realize the second word's full qata and vowel; emit no two-word hamza-meeting rule. |

### Matching vowels

The matching A+A, I+I, and U+U rows use `hamza_muttafiq`, except for the four
narrow sites below. Ibdal replaces the second qata with a pure carrier matching
the first vowel. Tashil retains a vowel-conditioned eased second onset.

| Pair | Selected source and refs | Canonical ref | Ibdal span | Tashil span |
| --- | --- | --- | --- | --- |
| A+A | `جَآءَ احَدٞ مِّنكُم`, 4:43:27-29 | 4:43:27-29 | `... ʔ a: ħ a d u m̃ ...` | `... ʔ a ʔ̞ a ħ a d u m̃ ...` |
| I+I | `اَ۬لنِّسَآءِ الَّا`, 4:22:7-8 | 4:22:7-8 | `... ʔ i: ll a:` | `... ʔ i ʔ̞ i ll a:` |
| U+U | `أَوْلِيَآءُۖ اوْلَٰٓئِكَ`, 46:31:14-15 | 46:32:14-15 | `... ʔ u: l a: ʔ i k a` | `... ʔ u ʔ̞ u: l a: ʔ i k a` |

A pure carrier created by the meeting emits `ibdal_hamza` and the effective
structural madd on the same result sound and responsible source characters. It
does not acquire `madd_badal` merely from the meeting. Independently existing
badal origin is preserved, however. At the unique U+U site, the second word's
lexical waw carrier remains `madd_badal`: under ibdal it fuses with the created
carrier and the resulting `/u:/` has `ibdal_hamza`, `madd_badal`, and
`madd_muttasil`; under tashil it remains the muttasil `/u:/` after the eased
onset.
Tashil emits `tashil` on that onset even when it renders as plain `ʔ`.
In the A+A row, the selected context continues as `احَدٞ مِّنكُم`; ordinary
tanwin-to-meem idgham owns `/m̃/`. The ellipsis crops the sequence after that
assimilating onset rather than inventing an isolated final consonant.

### Different vowels

The different-vowel matrix is structural:

| Pair | Count | Example | Required result |
| --- | ---: | --- | --- |
| A+I | 19 | `تَفِےٓءَ ا۪لَىٰٓ`, source and canonical 49:9:17-18 | Fixed tashil: `... ʔ a ʔ̞ i l a:`. The final nucleus has the fixed Warsh fath result. |
| A+U | 1 | `جَآءَ اُ۟مَّةٗ رَّسُولُهَا`, source and canonical 23:44:7-9 | Fixed tashil: `... ʔ a ʔ̞ u m̃ a t a rˤrˤ aˤ ...` in its actual joined context; ordinary tanwin-to-raa idgham owns `/rˤrˤ/`. |
| I+A | 29 | `اِ۬لنِّسَآءِ اَ۬وَ اَكْنَنتُمْ فِےٓ`, source 2:233:9-12, canonical 2:235:9-12 | Fixed moving ibdal to yaa + A, followed by ordinary naql at the next boundary: `... ʔ i j a w a k n a ŋ t u m f i:`. |
| U+A | 13 | `وَيَٰسَمَآءُ اَ۬قْلِعِےۖ`, source and canonical 11:44:5-6 | Fixed moving ibdal to waw + A: `... ʔ u w a q Q l ...`. |
| U+I | 26 | `يَٰزَكَرِيَّآءُ اِ۪نَّا`, source 19:6:1-2, canonical 19:7:1-2 | Public `hamza_damm_kasr`: ibdal `... ʔ u w i ñ a:`, tashil `... ʔ u ʔ̞ i ñ a:`. |

For I+A and U+A, the replacement is a moving consonant carrying the second
hamza's A nucleus. It emits `ibdal_hamza` and no replacement madd. U+I likewise
produces a moving kasra-bearing waw and emits `ibdal_hamza` without madd. Fixed
tashil and the selected U+I tashil face always emit `tashil`.

Ordinary tajwid remains independently visible in those examples: the held
meem and noon emit `ghunnah_mushaddadah`, while the sakin qaf emits
`qalqala_sughra`. These rules do not belong to the hamza-meeting occurrence.
Likewise, the subsequent `اَ۬وَ اَكْنَنتُمْ` boundary emits its own `naql`;
neither that transfer nor the following ikhfaa belongs to the I+A meeting.

## Narrow matching-vowel registers

### Jaa Aal

The two A+A boundaries `جَآءَ ا۟لَ لُوطٖ`, source and canonical 15:61:2-3,
and `جَآءَ ا۟لَ فِرْعَوْنَ`, source and canonical 54:41:2-3, are owned by
`jaa_aal`, not `hamza_muttafiq`. Al-Nashr identifies this two-site subcase
([source](https://www.islamweb.net/amp/ar/library/content/70/109/)).

Ibdal removes the second onset and canonicalizes the adjacent A carriers to
the sequence `... ʔ a: l ...`. That one long A result after the first qata has
`ibdal_hamza` and retains the lexical carrier's `madd_badal` without
`madd_tabii`.
Tashil keeps `... ʔ a ʔ̞ a: l ...`, with `tashil` on the eased onset and
`madd_badal` on the lexical long A. Count-dependent duration correlations do
not create additional phoneme outcomes or selectors.

### Kasr plus yaa

The two I+I boundaries are:

| Selected source span | Selected source refs | Canonical refs |
| --- | --- | --- |
| `هَٰٓؤُلَآءِ ان` | 2:30:12-13 | 2:31:12-13 |
| `اَ۬لْبِغَآءِ انَ` | 24:33:32-33 | 24:33:32-33 |

They are owned by `hamza_kasr_yaa`. Al-Wafi authenticates all three faces at
these two boundaries
([source](https://www.islamweb.net/ar/library/content/245/16/)):

| Effective face | Relevant result | Rules |
| --- | --- | --- |
| Ibdal | `... ʔ i: ...` | `ibdal_hamza` plus the effective structural madd. |
| Tashil | `... ʔ i ʔ̞ i ...` | `tashil` on the eased second onset. |
| Yaa | `... ʔ i j i ...` | `ibdal_hamza` on a moving kasra-bearing yaa; no madd. |

The `yaa` face is a consonantal replacement, not a duration choice.

## Rule reach and test ownership

For every meeting, the first qata remains independently aligned to its sound
and source. `tashil` reaches the eased second onset. `ibdal_hamza` names the
second, replaced hamza as its source and the replacement carrier or consonant
as its host. When ibdal creates a long carrier, the effective madd rule reaches
the same result sound. Visible unit and cell placements follow sound ownership
and silence; trigger-only neighboring letters are not tagged. A moving waw or
yaa receives no invented madd.

Machine data must own all 60 one-word and 156 across-word rows with source
ref, canonical ref, first and second qualities, boundary scope, structural
owner, and authored-exception owner. Tests assert the exact partitions above,
all five Aimma sites, the Aajami site, all four triple-hamza sites, both Jaa-Aal
sites, both kasr-plus-yaa sites, and every boundary state. They must also prove
that disabling the `tashil` extra token changes only rendering, never the
typed state, `tashil` occurrence, or source reach.
