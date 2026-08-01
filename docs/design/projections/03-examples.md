# 03 - Worked examples

Status: **format seed**. Scope: Uthmani, Hafs.

These are the specification, not a recording. Nothing here can be generated
today: the contract names rules no code mints, a recited text no writer
produces, and pairings no method returns. Each table says what the
output must look like when the work in [01-contract](01-contract.md) section 9
is done, which is what makes them the acceptance fixtures.

Source words are taken from the corpus, because hand-typing Arabic is how a
combining mark ends up in the wrong order. Everything else is authored.

Every phoneme below is the package's own output for that word and boundary
plan, in the notation it ships. The rule names, the recited spelling and the
alignment columns are the authored part, because none of them exists yet.

## 1. The format

One row per part of a unit, in reading order.

| Column | Holds |
|---|---|
| letter | the unit's letter. Blank means the row above's letter, its other half |
| on the letter | the rule that hosted, merged or silenced this part |
| sound | the token, or `-` for a part that is written and not said |
| on the sound | the rule that coloured, lengthened or named the sound |

**A rule appears on the row of its `source`, never its `target`.** So a lam
shamsiyyah is written against the lam that disappears, not against the letter
that doubles.

The two rule columns are the two edge families: what happened to the position,
and what happened to the sound it produced. They differ more often than they
agree - a stop silences a vowel while a madd lengthens one, and neither is the
other's business.

A **recited** line follows the table only where the recited text differs from
the rasm.

Rule names and recited spellings are authored; every token is the package's
output for that request.

## 2. Worked examples

### E1. Cross-word idgham bi ghunnah - 2:5:3-4, joined then stopped

`هُدًى مِّن` -> `h u d a m̃ i n`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ه | | h | |
| | | u | |
| د | | d | |
| | | a | |
| ن | `idgham_bi_ghunnah` | - | |
| م | | m̃ | |
| | | i | |
| ن | | n | |

The tanween's noon is written by no glyph of its own, and it is the rule's
`source`, so the row is there and not on the meem that receives it. The seat
`ى` spells nothing in this reading; joined, it is neither sounded nor
separately silenced.

### E2. The divine name - 1:2:2, joined

`لِلَّهِ` -> `l i ll a: h i`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ل | | l | |
| | | i | |
| ل | | ll | |
| | | a: | `madd_tabii` |
| ه | | h | |
| | | i | |

No dagger alif anywhere in this word, so the fatha alone supplies the vowel
and there is no length carrier. The lam is light here, following a kasra, so
no `tafkheem`.

### E3. Stopping on a word - 2:2:1

`ذَٰلِكَ` -> `ð a: l i k`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ذ | | ð | |
| | | a: | `madd_tabii` |
| ل | | l | |
| | | i | |
| ك | | k | |
| | `pausal_sukun` | - | |

The last two rows are why `Part` exists: the kaf's consonant sounds while the
kaf's vowel is silent.

### E4. The hamza wasl, started on - 1:2:1, stopped

`ٱلْحَمْدُ` -> `ʔ a l ħ a m d Q`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ء | `hamza_wasl_start` | ʔ | |
| | `hamza_wasl_start` | a | |
| ل | | l | `lam_qamariyyah` |
| ح | | ħ | |
| | | a | |
| م | | m | |
| د | | d | |
| | | Q | `qalqala_kubra` |
| | `pausal_sukun` | - | |

The helping vowel has no glyph in the source, which is the one case that takes
a gap pairing. The echo sits beside the consonant rather than replacing it, and
the vowel that is gone is a separate row.

Recited `أَلْحَمْدْ`.

### E5. Lam shamsiyyah - 1:3:1, stopped

`ٱلرَّحْمَـٰنِ` -> `ʔ a rˤrˤ aˤ ħ m a: n`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ء | `hamza_wasl_start` | ʔ | |
| | `hamza_wasl_start` | a | |
| ل | `lam_shamsiyyah` | - | |
| ر | | rˤrˤ | `tafkheem` |
| | | aˤ | `tafkheem` |
| ح | | ħ | |
| م | | m | |
| | | a: | `madd_tabii` |
| ن | | n | |
| | `pausal_sukun` | - | |

The lam is the rule's `source` and gets the row; the raa that doubles does
not. Emphasis is a colour on the sound and spreads to the vowel after it, so
it appears twice in the right-hand column and never in the left.

Recited `أَرَّحْمَانْ`.

### E6. Lam qamariyyah, and a dagger - 2:2:2, started on

`ٱلْكِتَـٰبُ` -> `ʔ a l k i t a: b u`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ء | `hamza_wasl_start` | ʔ | |
| | `hamza_wasl_start` | a | |
| ل | | l | `lam_qamariyyah` |
| ك | | k | |
| | | i | |
| ت | | t | |
| | | a: | `madd_tabii` |
| ب | | b | |
| | | u | |

The same written shape as E5 and the opposite outcome: here the lam sounds and
nothing assimilates. The difference is a fact about the following letter, not
about the lam.

Recited `أَلْكِتَابُ` - the dagger becomes a written alif.

### E7. The plural waw's alif - 2:6:3, joined

`كَفَرُوا۟` -> `k a f a rˤ u:`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ك | | k | |
| | | a | |
| ف | | f | |
| | | a | |
| ر | | rˤ | `tafkheem` |
| | | u: | `madd_tabii` |
| ا | `orthographic_silence` | - | |

The alif is written and never said. Its rule instance owns no attribution, so
the glyph's pairing shows no sound and names the rule in its `rules`.

Recited `كَفَرُو`.

### E8. Madd iwad, seat written - 2:5:3, stopped

`هُدًى` -> `h u d a:`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ه | | h | |
| | | u | |
| د | | d | |
| | | a: | `madd_tabii` |
| ن | `pausal_sukun` | - | |

One mark supplies two units: the dal's vowel, which lengthens, and the noon,
which goes. "Madd iwad" is those two rows read together, and no rule is named
for it. The seat stops being silent rather than being inserted.

Recited `هُدَا`.

### E9. Madd iwad, no seat - 2:22:11, stopped

`مَآءً` -> `m a: ʔ a:`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| م | | m | |
| | | a: | `madd_wajib_muttasil` |
| ء | | ʔ | |
| | | a: | `madd_tabii` |
| ن | `pausal_sukun` | - | |

The same event as E8 with no seat to un-silence. The sound has a source glyph,
so it is not a gap pairing; what differs is the recited text.

Recited `مَآءَا` - an alif the rasm does not have.

### E10. Taa marbuta carrying tanween - 2:26:9, stopped

`بَعُوضَةً` -> `b a ʕ u: dˤ aˤ h`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ب | | b | |
| | | a | |
| ع | | ʕ | |
| | | u: | `madd_tabii` |
| ض | | dˤ | `tafkheem` |
| | | aˤ | `tafkheem` |
| ة | `taa_marbuta_pausal` | h | |
| | `pausal_sukun` | - | |
| ن | `pausal_sukun` | - | |

Two rules doing two different things on one word: one changes a letter's
sound, the other takes two sounds away. Neither changes a glyph.

Recited `بَعُوضَهْ`.

### E11. Qalqala on a geminate - 113:1:3, stopped

`بِرَبِّ` -> `b i rˤ aˤ bb Q`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ب | | b | |
| | | i | |
| ر | | rˤ | `tafkheem` |
| | | aˤ | `tafkheem` |
| ب | | bb | |
| | | Q | `qalqala_akbar` |
| | `pausal_sukun` | - | |

A geminate at a stop takes the strongest degree. The echo and the doubled
consonant are two sounds on one part, which is legal because a release is an
addition and not the part's realization.

### E12. Muqattaat - 2:1:1

`الٓمٓ` -> `ʔ a l i f l a: m̃ i: m`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| ء | | ʔ | |
| | | a | |
| ل | | l | |
| | | i | |
| ف | | f | |
| ل | | l | |
| | | a: | `madd_lazim` |
| م | `idgham_shafawi` | - | |
| م | | m̃ | |
| | | i: | `madd_lazim` |
| م | | m | |

Three glyphs spell seven units, every one with `origin = letter_name`: `ا`
alone spells the three of `alif`. The rows are parts, which is why there are
eleven of them. The two meems at the seam are one held nasal, not two, and the
meem that disappears is the rule's `source`.

Recited `أَلِفْ لَآمّٓ مِيمْ`.

### E13. Silah - 2:27:7, joined

`مِيثَـٰقِهِۦ` -> `m i: θ a: q i h i:`

| letter | on the letter | sound | on the sound |
|---|---|---|---|
| م | | m | |
| | | i: | `madd_tabii` |
| ث | | θ | |
| | | a: | `madd_tabii` |
| ق | | q | |
| | | i | |
| ه | | h | |
| | | i: | `madd_tabii` |

The pronoun haa's vowel is long joined and absent at a pause. That is the
vowel kind, and no rule repeats it: "silah" is the kind plus whichever madd
rule fired. Stop on this word and the last row becomes a `pausal_sukun`.

## 3. The alignment quadrants

Each case below is written out in all four combinations of `text` and
`grouping`. The set is chosen because these are where the quadrants disagree;
a case that reads the same in all four proves nothing.

| Case | What it settles |
|---|---|
| a plain word with a long vowel (E6) | ownership: the carrier owns the vowel, the consonant owns itself |
| cross-word idgham (E1) | `shares` on both sides; the host word owns the sound |
| tanween before an idgham letter | one glyph reaching two units; a cluster that owns two sounds and shares a third |
| lam shamsiyyah (E5) | a silent glyph sharing the geminate: the same row shape as idgham, a different rule |
| madd iwad with a written seat (E8) | the seat un-silences at the pause; a rendered glyph replaces a source glyph |
| madd iwad with no seat (E9) | the recited text has a glyph the source does not; only the recited quadrants show it |
| the hamza wasl started on (E4) | a sound no source glyph presents: a gap pairing in source, an ordinary pairing in recited |
| iltiqa al-sakinayn | a gap pairing between two pairings that neither owns |
| the badal | a source glyph changes kind as well as shape: a hamza becomes the madd letter of the vowel before it, so one recited cluster covers two source glyphs |
| the divine name's long vowel | one presenting glyph where a long vowel usually has two, and no length carrier to own it |
| taa marbuta at a stop (E10) | the sound changes and so does the recited glyph, while the source glyph stands |
| a muqattaat opening (E12) | one glyph spelling several units, under both groupings |

## 4. Where the two texts differ

[06-two-texts](06-two-texts.md) is the whole of it, and every case below
appears there with its trigger and its owning rule.

## 5. The inventory still to produce

Ordered so each mechanism appears before the rules that depend on it. Every
row of [02-gate](02-gate.md) section 6 maps onto at least one.

**A. Script and vowels.** Plain word, no rule; long vowel as haraka plus
carrier; dagger alif; long vowel with no carrier glyph (E2); otiose alif after
the plural waw; alif maqsura; silent carrier under a dagger; shadda in the
rasm; muqattaat, one glyph and several units; structural glyphs and the
concatenation law.

**B. Tanween.** Joined izhar; fathatan at waqf with a seat; fathatan at waqf
with no seat and an alif rendered; dammatan and kasratan at waqf; on taa
marbuta at waqf; meeting a sakin, the inserted kasra.

**C. Boundary.** Waqf on a final short vowel (E3); taa marbuta to a heh;
ibtidaa with the hamza wasl sounding, all three vowels, both spelling
policies; wasl with the hamza silent; iltiqa shortening a long vowel; sakt;
silah joined and at waqf; the seven alifs joined and stopped; madd leen at
waqf; the stop that hands itself back at 27:36.

**D. Noon sakinah and tanween**, each in both its forms. Izhar halqi; izhar
mutlaq; ikhfaa haqiqi; iqlab; idgham bi ghunnah cross-word (E1); idgham bila
ghunnah; ghunnah mushaddadah on noon and on meem.

**E. Meem sakinah.** Izhar shafawi; ikhfaa shafawi; idgham shafawi.

**F. Idgham of adjacent consonants.** Mutamathilayn; mutaqaribayn;
mutajanisayn kamil; mutajanisayn naqis, which does not merge; lam shamsiyyah;
lam qamariyyah.

**G. Madd.** Tabii; wajib muttasil; jaiz munfasil and its reversion at waqf;
lazim; arid lil sukun; leen, whose edge lands on a consonant; iwad; the pausal
glide; the badal.

**H. Colour.** Tafkheem spreading to a fatha; raa heavy; raa light; the divine
lam heavy and light; imala; tashil; ishmam, the soundless instance; ikhfaa
before an istilaa letter, which nothing can currently produce.

**I. Release.** Qalqala sughra; kubra; akbar; suppressed by an idgham that
never releases.

**J. Muqattaat.** One name with its madd lazim; idgham across the seam between
two names; the seam to the following word.
