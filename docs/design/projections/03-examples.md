# 03 - Worked examples

Status: **format seed**. Scope: Uthmani, Hafs.

Every literal here is generated from the corpus, including the source word.
Where the model cannot yet say something the contract promises, the row says
so.

## 1. The format

One table. Rows are sounds in reading order; a row with `-` heard is something
written that is not said.

| Column | Holds |
|---|---|
| heard | the token |
| written | the glyphs that produce it, in source order. `+` joins glyphs from different words |
| rule | the rule instance, and a note only when the row is not self-explanatory |

No indices. What is on a row belongs together.

## 2. Three sound examples

### E1. Cross-word idgham bi ghunnah, 2:5:3-4, joined

`هُدًى مِّن`

| heard | written | rule |
|---|---|---|
| h | ه | |
| u | ُ | |
| d | د | |
| a | ً | |
| held meem | ً + مّ | `idgham_bi_ghunnah`: the tanween's noon merges into word two's meem |
| i | ِ | |
| n | ن | |
| - | ى | otiose seat |

One mark, three facts: `ً` is the dal's vowel, the noon's letter, and the
noon's silence. One sound, two words. The word-initial shadda witnesses the
assimilation without asserting it: stop on word one and the meem sounds plain.

### E2. The divine name, 1:2:2, joined

`لِلَّهِ`

| heard | written | rule |
|---|---|---|
| l | ل | |
| i | ِ | |
| ll | لّ | |
| long a | َ | `madd_tabii`, which no code mints for this case today |
| h | ه | |
| i | ِ | |

No dagger alif anywhere in this word, so the fatha alone writes a long vowel.
Rule to glyph for the madd returns nothing; glyph to sound still links the
fatha. The lam is light here, following a kasra, so no `tafkheem` fires.

### E3. Stopping on a word, 2:2:1

`ذَٰلِكَ`

| heard | written | rule |
|---|---|---|
| dh | ذ | |
| long a | َ ٰ | two glyphs, one vowel |
| l | ل | |
| i | ِ | |
| k | ك | |
| - | َ | `pausal_sukun` |

The last two rows are why `Part` exists: the kaf's consonant sounds while the
kaf's vowel is silent.

## 3. The alignment quadrants

Each case below is generated in all four combinations of `text` and
`grouping`. The set is chosen because these are where the quadrants disagree;
a case that reads the same in all four proves nothing.

| Case | What it settles |
|---|---|
| a plain word with a long vowel | ownership: the carrier owns the vowel, the consonant owns itself |
| cross-word idgham (E1) | `shares` on both sides; the host word owns the sound |
| tanween before an idgham letter | one glyph reaching two units; a cluster that owns two sounds and shares a third |
| lam shamsiyyah | a silent glyph sharing the geminate: the same row shape as idgham, a different rule |
| madd iwad with a written seat | the seat un-silences at the pause; a rendered glyph replaces a source glyph |
| madd iwad with no seat | the recited text has a glyph the source does not; only the recited quadrants show it |
| the wasl hamza's helping vowel | a sound with no source glyph: a gap row in source, an ordinary row in recited |
| iltiqa al-sakinayn | a gap row between two rows that neither owns |
| the divine name's long vowel | unwritten in every quadrant: the negative case |
| taa marbuta at a stop | the glyph does not change and the sound does |
| a muqattaat opening | one glyph spelling several units, under both groupings |

## 4. Sounds with no source glyph

Every insertion names the character to draw.

| Sound | Rendered as |
|---|---|
| the wasl hamza's helping vowel, when started on | the haraka its grammar chooses |
| the divine name's long vowel | a dagger alif |
| madd iwad where no seat is written | an alif |
| the iltiqa helping kasra | a kasra |

Iwad sites that already have a seat need no insertion: the seat stops being
silent, which is a replacement rather than an insertion.

The qalqala echo is not here. It is a release sound rather than a letter, and
the recited text does not write it.

The counts for each of these are boundary-mode dependent, so they belong to a
measurement rather than to this document. A fixture set derived from performed
output covers what a count would only assert.

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
ibtidaa with the wasl hamza sounding, all three vowels, both spelling
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
glide; ibdal hamza.

**H. Colour.** Tafkheem spreading to a fatha; raa heavy; raa light; the divine
lam heavy and light; imala; tashil; ishmam, the soundless instance; ikhfaa
before an istilaa letter, which nothing can currently produce.

**I. Release.** Qalqala sughra; kubra; akbar; suppressed by an idgham that
never releases.

**J. Muqattaat.** One name with its madd lazim; idgham across the seam between
two names; the seam to the following word.
