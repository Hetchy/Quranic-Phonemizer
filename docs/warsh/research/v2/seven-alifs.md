# Seven alifs

"The seven alifs" is a teaching label for seven word headings whose final
alif needs boundary-aware treatment. It is not one phonological rule. Warsh
through al-Azraq has four different canonical shapes across the set, and the
second `قَوَارِيراٗ` shares the same Warsh tanwin behavior as the first even
though it is not a separate heading in the traditional seven.

There is no `seven_alifs` rule ID. Canonical projection authors the appropriate
joined/stopped shape; existing madd, `madd_iwad`, noon, and boundary rules classify
the result.

## Exact Warsh matrix

| Traditional heading | Selected source and canonical ref | Warsh wasl | Warsh waqf |
| --- | --- | --- | --- |
| `أَنَا` | Recurring; closed qata subsets below | Normally final short `/a/`. Before qata A or U, retain `/a:/`; before qata I, delete the alif. | `/a:/` everywhere |
| `لَّٰكِنَّا` | Source `18:37:1`, canonical `18:38` | Final short `/a/` | Final `/a:/` |
| `اِ۬لظُّنُونَاۖ` | Source/canonical `33:10`, word 16 | Final `/a:/` | Final `/a:/` |
| `اَ۬لرَّسُولَاۖ` | Source/canonical `33:66`, word 11 | Final `/a:/` | Final `/a:/` |
| `اَ۬لسَّبِيلَاۖ` | Source/canonical `33:67`, word 8 | Final `/a:/` | Final `/a:/` |
| `سَلَٰسِلاٗ` | Source/canonical `76:4`, word 4 | Fathatan; the noon enters the ordinary next-onset rule | `/a:/` with `madd_iwad + madd_tabii` |
| first `قَوَارِيراٗۖ` | Source/canonical `76:15`, word 8 | Fathatan; the noon enters the ordinary next-onset rule | `/a:/` with `madd_iwad + madd_tabii` |
| related second `قَوَارِيراٗ` | Source/canonical `76:16`, word 1 | Fathatan; the noon enters the ordinary next-onset rule | `/a:/` with `madd_iwad + madd_tabii` |

The three Ahzab forms are retained by Nafi in both wasl and waqf
([qiraat source for all three](https://quranpedia.net/ayahs/33/10/1/349)).
Al-Wafi states that Nafi reads `سَلَٰسِلاٗ` and both `قَوَارِيراٗ` with
tanwin in wasl and replaces that tanwin with alif at waqf
([Al-Wafi, Insan forms](https://quranpedia.net/chapter/356412)).

## Ana

All readers retain the final alif at waqf. In wasl, Warsh retains it before a
qata onset with A or U, making munfasil, and deletes it before qata I or any
other onset. The Shatibiyya line and Warsh explanation state this division
directly ([Warsh through al-Azraq, Ana section](https://quranpedia.net/book-attachment/19884/77923)).

### Twelve retained qata boundaries

The selected King Fahd script marks exactly 12 retained sites:

| Selected source span | Canonical ref | Exact selected boundary |
| --- | --- | --- |
| `2:257:21-22` | `2:258` | `أَنَآ أُحْيِۦ` |
| `6:165:6-7` | `6:163` | `وَأَنَآ أَوَّلُ` |
| `7:143:39-40` | `7:143` | `وَأَنَآ أَوَّلُ` |
| `12:45:8-9` | `12:45` | `اَنَآ أُنَبِّئُكُم` |
| `12:69:10-11` | `12:69` | `أَنَآ أَخُوكَ` |
| `18:34:8-9` | `18:34` | `أَنَآ أَكْثَرُ` |
| `18:38:15-16` | `18:39` | `أَنَآ أَقَلَّ` |
| `27:40:5-6` | `27:39` | `أَنَآ ءَاتِيكَ` |
| `27:41:7-8` | `27:40` | `أَنَآ ءَاتِيكَ` |
| `40:42:11-12` | `40:42` | `وَأَنَآ أَدْعُوكُمُۥٓ` |
| `43:81:6-7` | `43:81` | `فَأَنَآ أَوَّلُ` |
| `60:1:36-37` | `60:1` | `وَأَنَآ أَعْلَمُ` |

The U and A boundary types have these concrete fixtures; every retained row
follows the matching pattern:

```text
اَنَآ أُنَبِّئُكُم بِتَاوِيلِهِۦ, source 12:45:8-10
wasl:                         ... ʔ a n a: ʔ u n a bb i ʔ u k u ŋ b i ...
ibtidaa at Ana and continue:  ʔ a n a: ʔ u n a bb i ʔ u k u ŋ b i ...

أَنَآ أَخُوكَ, source 12:69:10-11
wasl:                         ... ʔ a n a: ʔ a x u: k a
ibtidaa at Ana and continue:  ʔ a n a: ʔ a x u: k a

waqf on Ana in either case:   ʔ a n a:
rule on final long A          madd_munfasil in joined rows;
                               madd_tabii at waqf
```

The exact qata vowel is carried by its own `/a/` or `/u/` token.
The U fixture also includes the independent default-open ikhfaa shafawi at
`كُم بِـ`; selecting the shared closed nasal face changes `/ŋ/` to `/m̃/` only.

### Three qata-I deletions

Warsh has exactly three `أَنَا إِلَّا` boundaries in the corpus and deletes
the alif in wasl:

| Selected source span | Canonical ref | Exact selected boundary |
| --- | --- | --- |
| `7:188:23-24` | `7:188` | `اَنَا إِلَّا` |
| `26:115:2-3` | `26:115` | `اَنَا إِلَّا` |
| `46:8:21-22` | `46:9` | `أَنَا إِلَّا` |

```text
wasl:                         ... ʔ a n a ʔ i ll a: ...
ibtidaa at Ana and continue:  ʔ a n a ʔ i ll a: ...
waqf on Ana:                  ʔ a n a:
```

The joined short `/a/` and final alif source witness receive `pausal_alif`;
there is no munfasil madd. At waqf `/a:/` instead receives `madd_tabii`.
All other joined `أَنَا` sites follow this short/long pausal shape unless they
are in the 12-row retained table.

## Lakinna

The supported Warsh path deletes the alif in wasl and retains it in waqf.
Classical discussion identifies this as the ordinary joined/stopped analysis
of `لَّٰكِنَّا هُوَ اَ۬للَّهُ رَبِّے`
([al-Zajjaj, the boundary analysis](https://www.islamweb.net/ar/library/content/233/1570/%D9%82%D9%88%D9%84%D9%87-%D8%AA%D8%B9%D8%A7%D9%84%D9%89-%D9%84%D9%83%D9%86%D8%A7-%D9%87%D9%88-%D8%A7%D9%84%D9%84%D9%87-%D8%B1%D8%A8%D9%8A-%D9%88%D9%84%D8%A7-%D8%A3%D8%B4%D8%B1%D9%83-%D8%A8%D8%B1%D8%A8%D9%8A-%D8%A3%D8%AD%D8%AF%D8%A7)).

```text
wasl:                         l a: k i ñ a h u w a ...
ibtidaa at Lakinna and join:  l a: k i ñ a h u w a ...
waqf on Lakinna:              l a: k i ñ a:
```

Joined `/a/` receives `pausal_alif`; stopped `/a:/` receives `madd_tabii`.
The geminated nasal is the ordinary noon rule result, not part of the alif
decision.

## The three retained Ahzab alifs

Warsh retains these lexical alifs in both states. They are ordinary long
vowels with `madd_tabii`, not pausal alifs:

```text
اِ۬لظُّنُونَا   wasl/waqf relevant ending: ... n u: n a:
اَ۬لرَّسُولَا   wasl/waqf relevant ending: ... s u: l a:
اَ۬لسَّبِيلَا   wasl/waqf relevant ending: ... b i: l a:
```

Their full started shapes include the ordinary article and raa/emphasis rules;
those independent classifications must not be folded into a seven-alifs rule.
Ibtidaa at the host has the same lexical long as wasl. Stopping on the host
retains it as the same `madd_tabii` vowel.

## Salasila and both Qawarira

These are not pausal-alif shapes in Warsh. They have ordinary fathatan in
wasl and `madd_iwad + madd_tabii` in waqf. Nafi's two-Qawarira reading is explicitly
both-token tanwin, not only a decision on the verse-final first token
([classical qiraat summary](https://quranpedia.net/book/438/1/479)).

```text
boundary                                  canonical tanwin   performed wasl
سَلَٰسِلاٗ وَأَغْلَٰلاٗ                    ... l a n + w ...  ... l a w̃ ...
قَوَارِيراٗۖ قَوَارِيراٗ                  ... r a n + q ...  ... r a ŋˤ q ...
قَوَارِيراٗ مِّن فِضَّةٖ                  ... r a n + m ...  ... r a m̃ ...
```

The `+` marks the canonical word boundary; it is not a rendered token.

The first and third boundaries receive `idgham_bi_ghunnah`; the verse-crossing
qaf boundary receives `ikhfaa`. The sequences above use the default
light face of `raa_fathatan` for the final raa in both Qawarira words. A
different selected raa face does not change the tanwin shape or the identity
of `madd_iwad`, but it does color the raa-dependent A. Short A from fathatan in
wasl and long A created by `madd_iwad` at waqf are emphatic under a heavy raa and
plain under a light raa unless another cause supplies emphasis. See
[`../../../variants.md`](../../../variants.md). Waqf on any of the three words
produces final `/a:/` with `madd_iwad + madd_tabii`: the first rule names the
fathatan exchange and the second names the resulting ordinary long.

The tanwin source and affected nasal/next onset expose the relevant shared
noon rule. At waqf the core `madd_iwad` occurrence names the nunation as source
and the base vowel it lengthens as host. The transformed vowel/carrier cells
and `/a:/` sound carry both `madd_iwad` and `madd_tabii`; the composite tanwin
column does not receive raa coloring merely because that A is emphatic.

## Ownership and acceptance checks

- Canonical authored facts own the four shapes: pausal long, lexical long,
  ordinary fathatan, and Ana's qata-A/U retained long.
- Under the single-script decision the reviewed alif-mark families supply the
  shapes directly where the script distinguishes them: plain retained alif,
  alternate fathatan, madda-marked retained Ana, and the pausal-alif sign
  family. The closed registers above are the conformance reconciliation, and
  the joined/stopped alternation itself remains boundary behavior the written
  form cannot express.
- Existing `pausal_alif`, `madd_tabii`, `madd_munfasil`, `madd_iwad`,
  `idgham_bi_ghunnah`, and `ikhfaa` rules own the performed results.
- Tests cover all eight table rows, all 12 retained Ana boundaries, all three
  qata-I boundaries, ordinary Ana before a consonant and wasl onset, and all
  wasl/waqf/ibtidaa states.
- Sound and character assertions distinguish joined `pausal_alif`, stopped
  `madd_tabii`, retained `madd_munfasil`, and tanwin-created
  `madd_iwad + madd_tabii`.
- No seven-alifs rule, Warsh variant, duration option, or second-Qawarira
  omission is acceptable.
