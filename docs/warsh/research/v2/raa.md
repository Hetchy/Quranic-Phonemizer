# Warsh raa weight

This document specifies raa tafkheem and tarqeeq for Warsh from Nafi via
al-Azraq. It owns the domain predicates, precedence, boundary behavior, and
closed occurrence registers. Public selector values and defaults remain in
[`docs/variants.md`](../../../variants.md).

`heavy` and `light` below mean the effective raa result. The rule occurrence is
`tafkheem` or `tarqeeq`. Lam uses the same public vocabulary; its distinct
classifier and occurrence ownership preserve the lam-specific contract.

## Structural law

For an open or dammed raa, Warsh has a systematic tarqeeq environment when the
same word contains either:

- a sakin yaa immediately before the raa; or
- an original kasra before the raa, directly or separated by one sakin
  consonant.

A same-word isti'la consonant following the raa blocks the trigger, even when
an alif intervenes. A same-word isti'la consonant between the kasra and raa
also blocks it; in Quranic data the relevant interveners are sad, taa, and
qaf. Khaa is the transmitted exception only in the intervening position and
does not block tarqeeq there. A temporary kasra, a hamzat-al-wasl start kasra,
or a kasra in a preceding word is not a trigger. Al-Wafi states the predicate,
the same-word requirement, the one-sakin extension, the blockers, and the khaa
exception
([source](https://www.islamweb.net/ar/library/content/245/30/)).

For a sakin raa, apply the ordinary shared raa law after boundary resolution:

- an original preceding kasra makes it light unless a following same-word
  isti'la consonant owns a fixed-heavy result;
- an incidental kasra does not lighten it;
- rawm retains the wasl vowel law; and
- full-sukun waqf re-evaluates the now-sakin raa from its surviving same-word
  context.

These pausal distinctions, including `مِصْر`, `اَ۬لْقِطْر`, and `فِرْق`, are
given in Al-Wafi
([source](https://www.islamweb.net/ar/library/content/245/30/)) and Al-Nashr
([pausal details](https://www.islamweb.net/ar/library/content/70/189/)).

## Ownership and precedence

Run the classifier in this order:

1. Resolve the request boundary and the performed raa state: sounded vowel,
   rawm, or full sukun.
2. Apply a fixed lexical or structural exception.
3. Apply one named public owner from the closed registers below.
4. Apply the systematic fathatan or damma owner to an otherwise eligible raa.
5. Apply the ordinary sakin or moving-raa law.
6. Default to the ordinary heavy result where no tarqeeq cause survives.

Exactly one owner chooses weight for one raa. A named lexical owner removes its
target from `raa_fathatan` and `raa_damma`; a pausal owner applies only in its
declared state and does not change the joined result.

Inclination can itself create a light-raa result because the raa follows the
inclined nucleus. That result is downstream from inclination and must not be
reclassified by the ordinary fath/damma predicate
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/184/)).

## Systematic consumer scopes

The two large scopes are generated from the structural predicate, not stored as
lists of Unicode spellings:

| Owner | Target | Selected-corpus acceptance count |
| --- | --- | ---: |
| `raa_fathatan` | Otherwise eligible raa carrying fathatan | 259 |
| `raa_damma` | Otherwise eligible raa carrying damma or dammatan | 851 |

The five-word register and `raa_sihra` are excluded from `raa_fathatan`. Named
lexical and pausal owners are excluded from both. At a word-final dammed raa,
the selected moving result applies while the ending sounds; full-sukun waqf
uses the pausal structural result. A medial raa keeps the selected weight.

The three `raa_fathatan` values encode the only state distinction needed by
this classifier: `light` stays light in joined and stopped performance,
`heavy_wasl` is heavy while fathatan sounds and light at full waqf, and
`heavy` stays heavy in both. `raa_damma` is binary; a final target still
reverts to its ordinary light pausal result when damma disappears. The public
defaults and option order remain in `docs/variants.md`.

`raa_ishruna_kibr` owns exactly `عِشْرُونَ` at source 8:66:10, canonical 8:65,
and `كِبْرٞ` at source 40:55:14, canonical 40:56. The first target is medial;
the second follows the ordinary pausal result when its damma disappears. See
Al-Nashr for this grouped exception
([source](https://www.islamweb.net/ar/library/content/70/185/)).

The counts are conformance assertions produced from the canonical score of the
pinned King Fahd artifact. They supersede the pre-adapter research estimates
of 255 and 837: the final adapter projects 276 fathatan candidates and 855
damma candidates before the following-isti'la check. That check removes one
damma target; named exclusions then leave 259 and 851 respectively. The
runtime predicate must not test alternate tanwin glyphs or a color mark.

## Shared closed scopes

The following owners are shared with Hafs but may have a different riwayah
default or a different closed subset. The public catalogue is authoritative
for those defaults.

| Owner | Exact Warsh scope | Active state |
| --- | --- | --- |
| `raa_firq` | `فِرْقٖ`, canonical 26:63 | All states; one consumer choice intentionally owns the whole occurrence. |
| `raa_misr_waqf` | Non-tanwin `مِصْرَ` or `بِمِصْرَ` at 10:87, 12:21, 12:99, 43:51 | Full-sukun waqf only. |
| `raa_alqitr_waqf` | `اَ۬لْقِطْرِ`, 34:12 | Full-sukun waqf only. |
| `raa_yasr_waqf` | `يَسْرِ`, 89:4 | Full-sukun waqf only; Warsh's joined yaa drops at stop. |
| `raa_asr_waqf` | Warsh `فَاسْرِ` at 11:81, 15:65, 44:23 | Full-sukun waqf only. |
| `raa_wanuthur_waqf` | Six `وَنُذُرِ` endings at 54:16, 54:18, 54:21, 54:30, 54:37, 54:39 | Full-sukun waqf only; the joined yaa drops at stop. |

Both faces for `فِرْق`, `مِصْر`, and `اَ۬لْقِطْر` are documented in Al-Wafi
([source](https://www.islamweb.net/ar/library/content/245/30/)). Al-Nashr gives
the `يَسْر`, `أَسْر`, and `وَنُذُر` pausal cases
([source](https://www.islamweb.net/ar/library/content/70/189/)).

Negative members are part of the register:

- `مِصْراٗ` at 2:61 and `قِطْراٗ` at 18:96 are fixed heavy and are not the
  pausal selectors.
- `أَنِ اِ۪سْرِ` at 20:77 and 26:52 is fixed light for Warsh and is not in
  `raa_asr_waqf`.
- The three `بِالنُّذُرِ` at 54:23, 54:33, and 54:36 are fixed heavy at full
  waqf and are not `raa_wanuthur_waqf`.

## Warsh lexical choice registers

Each row is one closed owner. Its values and default are intentionally not
repeated here.

| Owner | Exact canonical register | Count | State |
| --- | --- | ---: | --- |
| `raa_alishraq` | `وَالِاشْرَاقِ`, 38:18 | 1 | All states |
| `raa_hayran` | `حَيْرَانَ`, 6:71 | 1 | All states |
| `raa_bisharar` | `بِشَرَرٍ`, 77:32 | 1 | Joined: first raa only; full waqf: both raas |
| `raa_five_words` | The 16 sites in the register below | 16 | All states |
| `raa_sihra` | `صِهْراٗ`, 25:54 | 1 | All states |
| `raa_iram` | `إِرَمَ`, 89:7 | 1 | All states |
| `raa_alif_ayn` | `ذِرَاعَيْهِ` 18:18; `سِرَاعاٗ` 50:44 and 70:43; `ذِرَاعاٗ` 69:32 | 4 | All states |
| `raa_alif_hamza` | `اَ۪فْتِرَآءً` 6:138 and 6:140; `مِرَآءٗ` 18:22 | 3 | All states |
| `raa_dual_alif` | `طَهِّرَا` 2:125; `لَسَٰحِرَٰنِ` 20:63; `سَٰحِرَٰنِ` 28:48; `تَنتَصِرَٰنِ` 55:35 | 4 | All states |
| `raa_ashiratukum` | `وَعَشِيرَتُكُمْ`, 9:24 | 1 | All states |
| `raa_wizraka` | `وِزْرَكَ`, 94:2 | 1 | All states |
| `raa_dhikraka` | `ذِكْرَكَ`, 94:4 | 1 | All states |
| `raa_wizra_ukhra` | `وِزْرَ أُخْرَى` at 6:164, 17:15, 35:18, 39:7, 53:38 | 5 | Wasl across the boundary only |
| `raa_ijrami` | `إِجْرَامِے`, 11:35 | 1 | All states |
| `raa_hidhrakum` | `حِذْرَكُمْ`, 4:71 and 4:102 | 2 | All states |
| `raa_ibrah_kibrahu` | Six `عِبْرَة` sites plus `كِبْرَهُ`, listed below | 7 | All states |
| `raa_hasirat_suduruhum` | `حَصِرَتْ صُدُورُهُمْ`, 4:90 | 1 | Wasl across the boundary only |

These lexical choices and their route evidence are collected in the Warsh raa
chapter of Al-Nashr
([source](https://www.islamweb.net/ar/library/content/70/183/)); `بِشَرَرٍ` is
discussed separately
([source](https://www.islamweb.net/ar/library/content/70/184/)). Al-Wafi
supports the six-word group, `بِشَرَرٍ`, and `حَيْرَانَ`
([source](https://www.islamweb.net/ar/library/content/245/30/)).

The exact `raa_five_words` register is:

| Lexeme | Canonical sites | Count |
| --- | --- | ---: |
| `ذِكْراٗ` | 2:200, 18:70, 18:83, 20:99, 20:113, 21:48, 33:41, 37:3, 37:168, 65:10, 77:5 | 11 |
| `سِتْراٗ` | 18:90 | 1 |
| `إِمْراٗ` | 18:71 | 1 |
| `وِزْراٗ` | 20:100 | 1 |
| `حِجْراٗ` | 25:22, 25:53 | 2 |

`صِهْراٗ` is deliberately separate: an authenticated route can keep this site
light while keeping the five-word set heavy. The six lexical types and the
preference evidence are in Al-Wafi
([source](https://www.islamweb.net/ar/library/content/245/30/)).

The exact `raa_ibrah_kibrahu` register is `عِبْرَة` or `لَعِبْرَة` at 3:13,
12:111, 16:66, 23:21, 24:44, and 79:26, plus `كِبْرَهُ` at 24:11. This consumer
owner intentionally collapses narrower route subpatterns; its seven-member
coordinate set must remain explicit.

For `raa_wizra_ukhra`, stopping on `وِزْرَ` is fixed light and starting at
`أُخْرَى` has no target raa. The inclination choice in `أُخْرَى` is independent.
For `raa_hasirat_suduruhum`, stopping on `حَصِرَتْ` is fixed light and starting
at `صُدُورُهُمْ` has no target raa.

## Fixed lexical exclusions

The following closed sets must bypass the systematic and lexical-choice
owners:

| Fixed result | Exact register | Count |
| --- | --- | ---: |
| Heavy | Every `إِبْرَاهِيم` (69), `إِسْرَائِيل` (43), and `عِمْرَان` (3) | 115 |
| Heavy | `ضِرَاراٗ` 2:231 and 9:107; `فِرَاراٗ` 18:18, 33:13, 71:6; `اُ۬لْفِرَارُ` 33:16; `إِسْرَاراٗ` 71:9; `مِّدْرَاراٗ` 6:6, 11:52, 71:11 | 10 |
| Light | `حِذْرَهُمْ`, 4:102 | 1 |
| Light | Other `عشير` family sites: 22:13, 26:214, 58:22 | 3 |

Al-Wafi identifies the three foreign-name families, `إِرَم`, and the repeated-
raa forms as exceptions to the structural tarqeeq law
([source](https://www.islamweb.net/ar/library/content/245/30/)). `إِرَم` is
selector-owned and therefore is not in the fixed-heavy table.

Other fixed results should remain structural, not copied into a coordinate
list: a same-word isti'la blocker after the raa, a temporary or cross-word
kasra, and a start-only hamzat-al-wasl kasra all produce the ordinary heavy
result. This prevents route examples from becoming brittle Unicode exceptions.

## Boundary matrix

| Shape | Joined | Full-sukun waqf | Ibtidaa |
| --- | --- | --- | --- |
| Eligible medial moving raa | Selected/systematic result | Same result if the raa remains medial | Same result from word-internal facts |
| Eligible final dammed raa | Selected result | Recompute as sakin; ordinary result is light | Same as joined when started at the word |
| Eligible fathatan raa | Selected joined result | Owner may preserve or change weight; fathatan becomes pausal alif | Same word-internal choice, with no preceding-word dependency |
| `raa_*_waqf` target | Ordinary joined result | Named pausal owner | Ordinary start result |
| Cross-word `_wasl` target | Named owner only while both words join | Fixed first-word result | No target when starting at word two |

Rawm preserves enough of the joined vowel to follow the joined law. It is a
domain state even if the first implementation exposes only joined and full
waqf.

## Sound, rules, and coloring

The light raa sound is `r`; the emphatic raa sound is `rˤ`. The selected weight
adds `tarqeeq` or `tafkheem` to both the raa sound and its source character.

When that raa determines its A nucleus, the same rule occurrence reaches the
vowel sound. This includes A written with fatha or fathatan, lexical long A,
and stop-created long A from `madd_iwad`:

- light raa produces plain `a` or `a:`;
- heavy raa produces emphatic `aˤ` or `aˤ:`; and
- making the raa light removes only the raa's emphasis cause, so the A becomes
  plain only if an isti'la consonant or another owner does not still require
  emphasis.

This is directional causal coloring. It does not recolor an unrelated vowel
before the raa. Classical descriptions explicitly treat the neighboring alif
as following the heavy or light articulation
([Al-Nashr](https://www.islamweb.net/amp/ar/library/content/70/44/)).

Manual sequences:

```text
خَيْراٗ فَإِنَّ, source 2:157:20-21, canonical 2:158
joined light before f:  x aˤ j r a ŋ f
joined heavy before f:  x aˤ j rˤ aˤ ŋ f
waqf light:    x aˤ j r a:
waqf heavy:    x aˤ j rˤ aˤ:

ذِكْراٗ فَمِنَ, source 2:199:10-11, canonical 2:200
joined light before f:  ð i k r a ŋ f
joined heavy before f:  ð i k rˤ aˤ ŋ f

خَيْرٞ لَّكُمْ, source 2:53:17-18, canonical 2:54
joined light:  x aˤ j r u ll a k u m
joined heavy:  x aˤ j rˤ u ll a k u m
plain waqf:    x aˤ j r
```

The fatha after khaa remains emphatic in all three examples because khaa owns
that coloring independently. Only the raa-dependent following A vowel changes.
The first two joined examples use the project's plain ikhfaa hum `/ŋ/` before
fa. In the third, tanwin merges without ghunnah into the following lam, so no
`/n/` remains and the lam is geminated.

## Selected-script fixtures

| Source ref | Canonical ref | Exact selected text | Owner or result |
| --- | --- | --- | --- |
| 26:63:11 | 26:63 | `فِرْقٖ` | `raa_firq` |
| 11:80:9 | 11:81 | `فَاسْرِ` | Warsh member of `raa_asr_waqf` |
| 38:17:7 | 38:18 | `وَالِاشْرَاقِ` | `raa_alishraq` |
| 6:71:23 | 6:71 | `حَيْرَانَۖ` | `raa_hayran` |
| 77:32:3 | 77:32 | `بِشَرَرٖ` | `raa_bisharar` |
| 4:89:11 | 4:90 | `حَصِرَتْ` | First word of `raa_hasirat_suduruhum` |

The source coordinates prove alignment only. Variant ownership is derived from
canonical facts and authored registers, never from the source's visual marks.

## Implementation and test invariants

- Store structural predicates separately from finite authored registers.
- Store source and canonical coordinates separately for every finite fixture.
- Assert the 259 and 851 systematic counts after excluding every named owner.
- Assert every finite subtotal and reject duplicate ownership of one raa.
- Test both weight outcomes at the sound and source-character projections.
- Test dependent short A, carrier A, and `madd_iwad` A recoloring in both
  directions, and retain any independently emphatic neighboring vowel. In the
  transformed cell view, place coloring on the rendered vowel/carrier column,
  never on the composite tanwin column.
- For each pausal owner, test joined, full waqf, and ibtidaa. For each
  cross-word owner, also test stopping after word one and starting at word two.
- Test the negative members explicitly: `مِصْراٗ`, `قِطْراٗ`, both
  `أَنِ اِ۪سْرِ`, all three `بِالنُّذُرِ`, `حِذْرَهُمْ`, and the three other
  `عشير` sites.
- Do not import the v1 mega table or infer raa weight from a color codepoint.
