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
| - | ى | `orthographic_silence` |
| held meem | ً + مّ | `idgham_bi_ghunnah`: the tanween's noon merges into word two's meem |
| i | ِ | |
| n | ن | |

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

No dagger alif anywhere in this word, so the fatha alone supplies the vowel
and there is no length carrier. The long vowel is written, by one glyph rather
than the usual two. The lam is light here, following a kasra, so no `tafkheem`
fires.

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
| the hamza wasl started on | a sound no source glyph presents: a gap row in source, an ordinary row in recited |
| iltiqa al-sakinayn | a gap row between two rows that neither owns |
| the badal | a source glyph changes kind as well as shape: a hamza becomes the madd letter of the vowel before it, so one recited cluster covers two source glyphs |
| the divine name's long vowel | one presenting glyph where a long vowel usually has two, and no length carrier to own it |
| taa marbuta at a stop | the glyph does not change and the sound does |
| a muqattaat opening | one glyph spelling several units, under both groupings |

## 4. Where the two texts differ

Two separate questions, and conflating them is easy.

**Sounds no source glyph presents.** These take a gap row under
`text="source"`. There are two. The hamza wasl's helping vowel is hosted on
that unit's own vowel; only the iltiqa vowel is attributed as an insertion,
and nothing constructs one yet.

| Sound | Rendered as |
|---|---|
| the hamza wasl's helping vowel, when started on | the haraka its grammar chooses |
| the iltiqa helping vowel | the haraka its position calls for, a kasra or a fatha |

**Recited spellings that differ from the source.** Here the sound has a source
glyph; what changes is what recitation writes for it.

| Case | The recited text |
|---|---|
| madd iwad, no seat written | adds an alif the rasm does not have |
| madd iwad, seat written | keeps the seat, which stops being silent |
| taa marbuta at a stop | keeps the glyph, changes the sound |
| the badal | writes the quiescent hamza as a madd letter, changing its kind |
| the hamza wasl started on | adds the helping haraka, and under the explicit policy respells the seat |

The divine name's long vowel belongs to neither list. Its fatha supplies the
vowel, so it is written; it simply has no length carrier, and the writer
does not abbreviate it to a dagger.

The qalqala echo is in neither list either. It is a release sound rather than
a letter, and the recited text does not write it.

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
marbuta at waqf; meeting a sakin, the inserted vowel.

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
