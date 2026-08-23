# Warsh lam taghliz

This document specifies lam taghliz for Warsh from Nafi via al-Azraq. It owns
the structural trigger, the inclination coupling, boundary behavior, and all
finite exception registers. Public selector values and defaults remain in
[`docs/variants.md`](../../../variants.md).

Use `taghliz` for lam, not generic `tafkheem`. Al-Nashr notes that the terms are
near-synonyms but reserves taghliz for lam and tafkheem for raa
([source](https://www.islamweb.net/ar/library/content/70/190/)).

## Sound and rule model

Lam has one light and one emphatic typed sound:

| Effective lam | Broad token | Rule |
| --- | --- | --- |
| Light | `l` | A selected or exceptional light face carries `tarqeeq`; an ordinary unowned light lam carries neither weight rule. |
| Emphatic | `lˤ` | `taghliz` |

Gemination is independent. The same emphatic lam type renders `lˤ` for a
single lam and `lˤlˤ` for a geminated lam. Do not add a separate
"Allah-only" or "single emphatic lam" phoneme.

A `taghliz` or lam-`tarqeeq` occurrence reaches the lam sound and source lam.
When the owned lam determines its A nucleus, the same occurrence also reaches
that vowel sound. This includes short A from fatha or fathatan, lexical long A
from a carrier, and stop-created long A from `madd_iwad`:

- light lam has plain `a` or `a:`;
- emphatic lam has `aˤ` or `aˤ:`; and
- tarqiq removes only the target lam's emphasis cause, so the A becomes plain
  only if sad, taa, zhaa, or another owner does not still require emphasis.

This propagation is directional. It does not recolor a vowel before the lam.
Al-Nashr describes taghliz as thickening the lam's own movement and treats the
following alif as dependent on the surrounding emphatic articulation
([lam terminology](https://www.islamweb.net/ar/library/content/70/190/),
[dependent alif](https://www.islamweb.net/amp/ar/library/content/70/44/)).

## Ordinary structural trigger

The ordinary Azraq trigger requires all of the following:

1. The target lam is open.
2. It is directly preceded in the same word by sad, taa, or zhaa.
3. That trigger consonant is open or sakin.

Al-Nashr states these three conditions and gives the Quranic forms
([source](https://www.islamweb.net/ar/library/content/70/190/)). The ordinary
ownership is:

- qualifying sad-lam is fixed taghliz unless a more specific owner below
  applies;
- qualifying taa-lam is owned by `lam_after_taa`;
- qualifying zhaa-lam is owned by `lam_after_zhaa`; and
- every other lam remains light unless another established shared rule, such
  as the divine-name lam, owns it.

The public taa and zhaa owners intentionally expose one consumer choice across
their ordinary qualifying scope. Narrow route subdivisions by exact spelling,
trigger haraka, or individual transmission are research provenance, not
separate runtime selectors.

## Ownership and precedence

Classify one lam in this order:

1. Resolve boundary state and whether its following vowel/alif survives.
2. Apply one coupled inclination-and-lam owner.
3. Apply `lam_salsal` to the first sakin lam in its four-token register.
4. Apply `lam_separated_by_alif` or `lam_final_waqf` in its exact state.
5. Apply the ordinary direct sad, taa, or zhaa trigger.
6. Apply a shared lam rule outside this Warsh chapter, or leave the lam light.

One lam has one weight owner. The more specific owner replaces the ordinary
trigger; it does not add a second, contradictory lam rule.

## Coupled inclination registers

An inclined alif and an emphatic lam are incompatible at these targets. The
only legal pairs are:

```text
fath plus taghliz
taqlil plus lam tarqiq
```

No independent lam selector or validator is needed. The named inclination
choice returns the compatible pair. Al-Nashr states that inclination and
taghliz do not combine
([source](https://islamweb.net/ar/library/content/70/192/)).

### Non-verse-head dhat-yaa sites

`lam_dhat_yaa` owns exactly seven sites:

| Source ref | Canonical ref | Exact selected text | State note |
| --- | --- | --- | --- |
| 2:124:11 | 2:125 | `مُصَلّىٗۖ` | Waqf manifests the selected pair; wasl masks it to fath plus taghliz. |
| 17:18:16 | 17:18 | `يَصْلَيٰهَا` | Selected pair in all sounded states. |
| 84:12:1 | 84:12 | `وَيُصَلَّىٰ` | Selected pair in all sounded states. |
| 87:12:2 | 87:12 | `يَصْلَى` | Waqf manifests the selected pair; wasl before `اَ۬لنَّارَ` masks it to fath plus taghliz. |
| 88:4:1 | 88:4 | `تَصْلَىٰ` | Selected pair in all sounded states. |
| 92:15:2 | 92:15 | `يَصْلَيٰهَآ` | Selected pair in all sounded states. |
| 111:3:1 | 111:3 | `سَيَصْلَىٰ` | Selected pair in all sounded states. |

The seven-site division and the special connected states are part of the
classical lam-and-inclination discussion
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/190/)). The selected
variant is still stored at the two masked sites; wasl merely makes its target
pair unavailable in that performance.

### Verse-head sites

`lam_verse_heads` owns exactly three sites:

| Source ref | Canonical ref | Exact selected text |
| --- | --- | --- |
| 75:30:4 | 75:31 | `صَلّ۪ىٰۖ` |
| 87:15:4 | 87:15 | `فَصَلّ۪ىٰۖ` |
| 96:10:3 | 96:10 | `صَلّ۪ىٰٓۖ` |

Al-Nashr identifies exactly these three verse-head positions
([source](https://www.islamweb.net/ar/library/content/70/190/)). They are
removed from the general verse-head inclination owner and the ordinary fixed
sad-lam trigger.

## Alif-separated register

The ordinary direct trigger does not cross an alif. The authenticated exception
is exposed as `lam_separated_by_alif` at exactly these five sites:

| Source ref | Canonical ref | Exact selected text |
| --- | --- | --- |
| 2:231:36 | 2:233 | `فِصَالاً` |
| 4:127:13 | 4:128 | `يَّصَّٰلَحَا` |
| 20:85:1 | 20:86 | `اَفَطَالَ` |
| 21:44:6 | 21:44 | `طَالَ` |
| 57:15:21 | 57:16 | `فَطَالَ` |

The source describes two sad-lam forms and the three occurrences of taa-alif-
lam, with both transmitted lam weights
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/190/)). The selected
Warsh spelling `يَّصَّٰلَحَا` is a fixed lexical reading difference; match its
canonical token identity, not a Hafs surface spelling.

`طَالَ` remains owned here even at word end. It is explicitly excluded from the
final-lam waqf register.

## Final-lam waqf register

`lam_final_waqf` owns the final lam only at full-sukun waqf. The register has
six lexical forms across nine occurrences:

| Source ref | Canonical ref | Exact selected text |
| --- | --- | --- |
| 2:26:14 | 2:27 | `يُّوصَلَ` |
| 2:247:2 | 2:249 | `فَصَلَ` |
| 6:120:11 | 6:119 | `فَصَّلَ` |
| 7:117:3 | 7:118 | `وَبَطَلَ` |
| 13:23:8 | 13:21 | `يُّوصَلَ` |
| 13:26:14 | 13:25 | `يُّوصَلَ` |
| 16:58:5 | 16:58 | `ظَلَّ` |
| 38:19:5 | 38:20 | `وَفَصْلَ` |
| 43:16:8 | 43:17 | `ظَلَّ` |

Al-Nashr names the six forms, the repeated occurrences, and both pausal faces
([source](https://www.islamweb.net/ar/library/content/70/190/)). In wasl or a
request that ends later, the ordinary sounded-lam owner applies. Full waqf
replaces that owner with `lam_final_waqf`; it does not leave two weight rules on
the same lam.

## Salsal register

`lam_salsal` owns the first, sakin lam between the two sads in all four
`صَلْصَٰلٖ` tokens:

| Source ref | Canonical ref | Exact selected text |
| --- | --- | --- |
| 15:26:5 | 15:26 | `صَلْصَٰلٖ` |
| 15:28:9 | 15:28 | `صَلْصَٰلٖ` |
| 15:33:8 | 15:33 | `صَلْصَٰلٖ` |
| 55:12:4 | 55:14 | `صَلْصَٰلٖ` |

Only the first lam belongs to this owner. The special case exists because that
lam is sakin; the ordinary structural trigger requires an open lam. Al-Nashr
records both transmitted treatments and identifies the between-two-sads
condition
([source](https://www.islamweb.net/ar/library/content/70/190/)).

## Boundary matrix

| Owner | Wasl | Full waqf | Ibtidaa |
| --- | --- | --- | --- |
| Ordinary direct trigger | Effective while lam and its fatha sound | If the target lam becomes final, `lam_final_waqf` may replace it | Recomputed from same-word structure |
| `lam_dhat_yaa`, ordinary five sites | Selected coupled pair | Selected coupled pair | Selected coupled pair |
| `lam_dhat_yaa`, 2:125 and 87:12 | Fath plus taghliz because the inclined alif is deleted | Selected coupled pair | Recomputed from the started token; no preceding-word dependency |
| `lam_verse_heads` | Selected coupled pair | Selected coupled pair | Selected coupled pair |
| `lam_separated_by_alif` | Selected lam result | Same result, including `طَالَ` | Same result |
| `lam_final_waqf` | Inactive | Selected final-lam result | Inactive |
| `lam_salsal` | Selected first-lam result | Same first-lam result | Same first-lam result |

## Manual sound checks

```text
مَطْلَعِ, source 97:5:4, canonical 97:5
tarqiq:  m a tˤ Q l a ʕ i
taghliz: m a tˤ Q lˤ aˤ ʕ i

فِصَالاً عَن, source 2:231:36-37, canonical 2:233
joined tarqiq:  f i sˤ aˤ: l a n ʕ
joined taghliz: f i sˤ aˤ: lˤ aˤ n ʕ
waqf tarqiq:    f i sˤ aˤ: l a:
waqf taghliz:   f i sˤ aˤ: lˤ aˤ:

صَلّ۪ىٰۖ, source 75:30:4, canonical 75:31
taqlil plus tarqiq: sˤ aˤ ll ɛ:
fath plus taghliz:  sˤ aˤ lˤlˤ aˤ:

صَلْصَٰلٖ مِّنْ حَمَإٖ, source 15:26:5-7, canonical 15:26, target first lam, joined
tarqiq first word:  sˤ aˤ l sˤ aˤ: l i
taghliz first word: sˤ aˤ lˤ sˤ aˤ: l i
following span:     m̃ i n ħ a ...
```

The alif after the first sad in `فِصَالاً` stays emphatic in both outcomes. It
is colored by sad, not by the later target lam. Conversely, the target lam's A
changes with the selected lam weight: it is short from fathatan in joined
speech and long from `madd_iwad` at waqf. The weight occurrence,
`madd_iwad`, and `madd_tabii` therefore overlap on the pausal sound without
changing each other's rule identity. In transformed cells the color occurrence
is placed on the rendered vowel/carrier column, not on the composite tanwin
column; that tanwin column retains only its own noon/boundary rules.
The sakin taa in `مَطْلَعِ` independently emits `qalqala_sughra` on `Q`.
`صَلْصَٰلٖ` has no A nucleus on the target first lam, so its `taghliz`
occurrence reaches only that lam sound and source lam. Its tanwin merges into
the following meem; the held `/m̃/` already represents the geminate and is not
doubled.

## Structural data versus authored data

Runtime logic should own:

- the direct same-word sad/taa/zhaa predicate;
- its haraka conditions;
- state resolution; and
- causal recoloring of the target lam's A nucleus in every boundary shape.

Warsh authored data should own:

- the 10 coupled inclination coordinates;
- the five alif-separated coordinates;
- the nine final-waqf coordinates;
- the four first-lam Salsal coordinates; and
- source-to-canonical alignment for every member.

Do not infer a register from U+06EA, an emphatic color mark, or the v1
classification. Those marks only attest selected-script spelling and default
performance.

## Test invariants

- The finite registers contain exactly 10, 5, 9, and 4 members respectively.
- No lam belongs to two owners in the same state.
- The coupled owner can produce only the two compatible pairs and preserves the
  caller's selected value while a boundary masks it.
- Both source and canonical refs are asserted for every finite member.
- Every light/heavy test checks the lam sound and the dependent short A,
  carrier A, or `madd_iwad` A sound. Cell assertions put coloring on the
  rendered vowel/carrier and never on a composite tanwin column.
- Removing the lam's coloring cause does not erase emphasis owned by the
  preceding sad, taa, zhaa, or another independent owner.
- `طَالَ` is never admitted to `lam_final_waqf`; Salsal owns only its first lam.
- An unknown source color or inclination witness cannot create taghliz.
