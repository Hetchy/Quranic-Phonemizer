# Hamzat al-wasl

This document owns the canonical WASL onset, its helping vowel, and its
boundary realization in Warsh through al-Azraq. It does not own naql, the
repair on the preceding word after wasl elision, or the general single-hamza
ibdal chapter.

Public choices at the six interrogative-article forms and at article starts
are defined in [`docs/variants.md`](../../../variants.md). This document uses
those values only where they change the boundary result.

## Domain contract

Ordinary hamzat al-wasl is a real prosthetic onset at ibtidaa and is absent in
joined speech. The article begins with fath; the Quranic conventional nouns begin
with kasr; and a verb begins with damm only when the relevant stem vowel is an
original damm, otherwise with kasr. A surface damm created for a suffix does
not license a damm start. These are grammatical decisions, not Unicode
decisions ([wasl positions and start vowels](https://www.islamweb.net/ar/library/content/231/77/)).

The Warsh `article_ibtidaa` choice is the closed start exception. Its `hamza`
face follows the ordinary article A-start. Its `lam` face begins directly on
the vowel-bearing lam and emits neither `wasl_start` nor `wasl_elision` for the
omitted prosthetic onset. At internal-naql articles, the deleted qata remains
deleted under both faces. The exact scope remains in `docs/variants.md` and
the naql ownership is specified in [`naql.md`](naql.md).

The selected Warsh corpus contains 13,480 projected WASL onsets. The reviewed
start-quality register is:

| Start quality | Count | Predicate |
| --- | ---: | --- |
| A | 11,982 | Definite article. |
| I | 1,097 | Conventional noun, or verb without an original U trigger. |
| U | 401 | Verb whose relevant stem vowel is originally U. |

The conventional-noun lexicon is the Quranic subset of `اسم`, `ابن`, `ابنة`,
`امرؤ`, `امرأة`, `اثنان`, `اثنتان`, and the attested inflections and clitic
forms. The defective imperative families from `يقضي`, `يبني`, `يمضي`,
`يمشي`, and `يأتي` stay I even where the written third consonant has a
suffix-conditioned damm. Their canonical test lemmas are `اقضوا`, `ابنوا`,
`امضوا`, `امشوا`, and `ائتوا`; the selected register includes
`وَامْضُواْ`, source 15:65:12, canonical 15:65:12. `اتقوا` is a separate I
counterexample: its surface qaf damm is not the stem vowel that decides the
start. These closed morphology facts belong in riwayah data, not in
source-mark branches.

The selected reading has a genuine lexical delta at `اَ۟سْتُحِقَّ`, source
5:109:12, canonical 5:107:12: its passive shape begins `ʔ u`, not the Hafs
active-reading `ʔ i`. The corpus word itself supplies the different
morphology; this is not a location patch.

## Projection trigger

The adapter emits `Onset.WASL` only after recognizing a reviewed initial-alif
sequence and its lexical shape. The current source has no U+0671 and uses
several overloaded combinations such as `اَ۬`, `اَ۟`, and `اَ۪`. Their visible
ordinary haraka is not the helping vowel. For example:

| Selected source | Source ref | Canonical ref | Derived start |
| --- | --- | --- | --- |
| `اِ۬لْحَمْدُ` | 1:1:1 | 1:2:1 | `ʔ a l ...` |
| `اَ۟دْخُلُواْ` | 2:57:3 | 2:58:3 | `ʔ u d Q x u l u:` |
| `اَ۪بْنَ` | 2:86:11 | 2:87:11 | `ʔ i b Q n a` |
| `اَ۟سْتُحِقَّ` | 5:109:12 | 5:107:12 | `ʔ u s t u ħ i qq aˤ` |

The first row is deliberately adversarial: its printed kasra-like sequence
still starts the article with A. Likewise, the five selected `ائتوني` forms use
different visible initial sequences even though all have the same I start.
The `/Q/` releases in `ادخلوا` and `ابن` are independently owned by
ordinary `qalqala_sughra`; they are not part of `wasl_start`.
The source convention may attest the result after derivation; it never drives
the rule. The sequence ownership and rejection policy are defined in
[`script-projection.md`](script-projection.md).

## Boundary matrix

The relevant tokens below show only the affected onset and enough neighboring
sound to make the boundary result unambiguous.

| State | Canonical action | Example result | Rules and attribution |
| --- | --- | --- | --- |
| Ibtidaa | Realize the prosthetic hamza with its derived A, I, or U nucleus. | Starting `اِ۬لْحَمْدُ`: `ʔ a l ...` | `wasl_start` classifies the onset and reaches the complete source sequence that spells the wasl unit. The helping nucleus is canonical content, not a second classified sound. |
| Wasl | Silence both the prosthetic onset and its helping nucleus. | Joining `... اِ۬لْحَمْدُ`: `... l ...` | `wasl_elision` reaches the silenced onset, nucleus, and source sequence. The exposed first sakin is then handled by `iltiqa_haraka` or `iltiqa_shortening` on the preceding word when required. |
| Stop before word | Finish the preceding word normally. If the requested range continues after the stop, start the following word by its ibtidaa result. | `... # ʔ a l ...` | No `wasl_elision` spans the stop. The included following word emits `wasl_start`; only a word outside the requested utterance is unperformed. |

An utterance request that starts at a mid-passage WASL word uses the ibtidaa
row even if the word is not the first word of its ayah. Array position and a
mushaf stop sign are not boundary state.

## A following silent qata hamza

At ibtidaa on `ائتوني`, `ائذن`, or `اؤتمن`, the realized wasl vowel meets a
silent qata hamza. The qata hamza is obligatorily replaced by a carrier of the
same quality, producing one long vowel: I gives yaa and U gives waw
([Al-Wafi, the general two-hamza rule and the three starts](https://www.islamweb.net/ar/library/content/245/17/),
[explicit ibtidaa explanation](https://www.islamweb.net/ar/fatwa/76455/)).

The closed selected-corpus register has 16 tokens: fourteen `ائت...` forms,
one `ائذن`, and one `اؤتمن`. Five of the fourteen are `ائتوني`.

| Selected source | Source ref | Canonical ref | Ibtidaa result |
| --- | --- | --- | --- |
| `اَ۪يتِنَاۖ` | 6:71:29 | 6:71:29 | `ʔ i: t i n a:` |
| `اُ۪يتِنَا` | 7:76:9 | 7:77:9 | `ʔ i: t i n a:` |
| `اِ۪يتِنَا` | 8:32:17 | 8:32:17 | `ʔ i: t i n a:` |
| `اُ۪يتِنَا` | 29:29:12 | 29:29:17 | `ʔ i: t i n a:` |
| `اَ۪يتِ` | 10:15:11 | 10:15:11 | `ʔ i: t i` |
| `اِ۪يتِ` | 26:9:6 | 26:10:6 | `ʔ i: t i` |
| `اُ۪يتُونِے` | 10:79:3 | 10:79:3 | `ʔ i: t u: n i:` |
| `اُ۪يتُونِے` | 12:50:3 | 12:50:3 | `ʔ i: t u: n i:` |
| `اُ۪يتُونِے` | 12:54:3 | 12:54:3 | `ʔ i: t u: n i:` |
| `اَ۪يتُونِے` | 12:59:5 | 12:59:5 | `ʔ i: t u: n i:` |
| `اِ۪يتُونِے` | 46:3:18 | 46:4:18 | `ʔ i: t u: n i:` |
| `اَ۪يتُواْ` | 20:63:4 | 20:64:4 | `ʔ i: t u:` |
| `اُ۪يتُواْ` | 45:24:12 | 45:25:12 | `ʔ i: t u:` |
| `اِ۪يتِيَا` | 41:10:10 | 41:11:10 | `ʔ i: t i j a:` |
| `اُ۪يذَن` | 9:49:4 | 9:49:4 | Waqf on the host: `ʔ i: ð a n`; continuing into `لِے`: `ʔ i: ð a ll i:` through ordinary noon-to-lam idgham. |
| `اِ۟وتُمِنَ` | 2:282:16 | 2:283:16 | `ʔ u: t u m i n a` |

The start produces one result vowel with three independent facts:

- `wasl_start` classifies the realized prosthetic onset;
- `ibdal_hamza` reaches the result sound and both source units responsible for
  the wasl-plus-qata transformation; and
- `madd_tabii` reaches the same result sound and responsible source
  characters because the result is structurally a long carrier. The same
  vowel also receives `madd_badal`: its semantic origin is the replaced qata
  hamza. These overlapping classifications encode different facts and neither
  carries a recitation count.

In joined speech the wasl onset still elides. Warsh then applies the connected
single-hamza outcome to the exposed qata using the preceding pronounced
vowel; it must not reuse the ibtidaa helping vowel. Thus `فِرْعَوْنُ ائتوني`
at source 10:79:2-3 continues through a U replacement
(`... n u: t u: n i:`),
`السَّمَٰوَٰتِ ائتوني` at source 46:3:17-18 uses an I replacement
(`... t i: t u: n i:`), and `اَ۬لذِے اؤتمن` at source 2:282:15-16 has the
documented joined I result (`... ð i: t u m i n a`). Those outcomes and their
source ownership are specified in
[`single-hamza.md`](single-hamza.md). They are not naql: no qata vowel is
transferred to a preceding sakin host.

## Interrogative hamza before the article

At the six shared `istifham_article` sites, an interrogative qata hamza
precedes the article's wasl hamza. The selected public face either replaces
the wasl hamza with alif or eases it; ordinary wasl elision does not erase the
selected second onset in any boundary state. The exact sites and values remain
in [`docs/variants.md`](../../../variants.md).

For `ءَآلذَّكَرَيْنِ`, 6:143, the relevant results are:

| Selection | Relevant sequence | Rule reach |
| --- | --- | --- |
| `ibdal` | `ʔ a: ðð a k a rˤ aˤ j n i` | `ibdal_hamza` and `madd_lazim` both reach the single replacement vowel and responsible source characters; ordinary article assimilation owns `/ðð/`, and ordinary raa tafkheem colors its following A. |
| `tashil` | `ʔ a ʔ̞ a ðð a k a rˤ aˤ j n i` | `tashil` reaches the eased onset and source hamza even when the extra token is rendered as plain `ʔ`; the same ordinary article and raa rules apply. |

The internal hamza choice is unchanged at wasl, waqf on the word, and ibtidaa;
the selector concerns an internal meeting, not a preceding word boundary. The
displayed `ءَآلذَّكَرَيْنِ` rows are continuing forms. At full-sukun waqf its
final I drops in the ordinary way, while the selected internal prefix and its
rule occurrences remain unchanged.

## Machine-owned register and tests

The 13,480-site register is generated from accepted source sequences plus the
canonical WASL predicate. Each record stores source ref, canonical ref,
source text, lexical skeleton, derived A/I/U quality, and the evidence role of
every source mark. Tests must assert:

1. the exact total and A/I/U partition above;
2. every conventional noun and temporary-damm exception;
3. the Warsh passive `اَ۟سْتُحِقَّ` delta;
4. all 16 silent-qata starts, including all five `ائتوني` tokens;
5. wasl, waqf-before, and ibtidaa for each quality; and
6. that changing source marks cannot turn qata into wasl or select a rule.

An unknown initial-alif sequence is a projection error with its source ref and
scalars. It is never guessed from the visible haraka.
