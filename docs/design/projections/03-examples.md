# 03 - Worked examples

Status: **format seed**. Scope: Uthmani, Hafs.

These are the specification, not a recording. Nothing here can be generated
today: the contract names rules no code mints, a recited text no writer
produces, and alignment rows no method returns. Each table says what the
output must look like when the work in [01-contract](01-contract.md) section 8
is done, which is what makes them the acceptance fixtures.

Source words are taken from the corpus, because hand-typing Arabic is how a
combining mark ends up in the wrong order. Everything else is authored.

Tokens are written descriptively rather than in one notation, since the
document carries a `notation` field and the choice is a consumer's.

## 1. The format

One table. Rows are sounds in reading order; a row with `-` heard is something
written that is not said.

| Column | Holds |
|---|---|
| heard | the token |
| written | the glyphs that produce it, in source order. `+` joins glyphs from different words |
| rule | the rule instance, and a note only when the row is not self-explanatory |

No indices. What is on a row belongs together.

## 2. Worked examples

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

### E4. The hamza wasl, both ways - 1:2:1

`ٱلْحَمْدُ`

Started on, the prosthetic hamza sounds and its helping vowel has no glyph at
all - the one case in the source text that needs a gap row.

| heard | written | rule |
|---|---|---|
| glottal stop | ٱ | `hamza_wasl_start` |
| a | *(gap row)* | `hamza_wasl_start`: nothing in the source writes it |
| l | ل | `lam_qamariyyah` |
| h | ح | |
| a | َ | |
| m | م | |
| d | د | |
| u | ُ | |

Joined, both halves of that unit go and the word begins on the lam.

| heard | written | rule |
|---|---|---|
| - | ٱ | `hamza_wasl_elision` |
| l | ل | `lam_qamariyyah` |
| ... | | as above |

### E5. Lam shamsiyyah - 1:3:1, joined

`ٱلرَّحْمَـٰنِ`

| heard | written | rule |
|---|---|---|
| - | ٱ | `hamza_wasl_elision` |
| - | ل | `lam_shamsiyyah` |
| rr | ل + ر ّ | `lam_shamsiyyah` |
| a | َ | |
| h | ح | |
| m | م | |
| long a | َ ٰ | `madd_tabii` |
| n | ن | |
| i | ِ | |

The silent lam and the doubled raa are one sound with two units. Under
`alignment` the lam's row has it in `shares` and the raa's row owns it, which
is what lights both when the sound is timed. The tatweel is structural and
takes no row.

### E6. A dagger alif - 2:2:2, joined

`ٱلْكِتَـٰبُ`

| heard | written | rule |
|---|---|---|
| - | ٱ | `hamza_wasl_elision` |
| l | ل | `lam_qamariyyah` |
| k | ك | |
| i | ِ | |
| t | ت | |
| long a | َ ٰ | `madd_tabii` |
| b | ب | |
| u | ُ | |

Contrast E5: there the lam is silent and the next letter doubles; here the lam
sounds and nothing assimilates. Two rules, one written shape.

### E7. The plural waw's alif - 2:6:3, joined

`كَفَرُوا۟`

| heard | written | rule |
|---|---|---|
| k | ك | |
| a | َ | |
| f | ف | |
| a | َ | |
| r | ر | |
| long u | ُ و | `madd_tabii` |
| - | ا ۟ | `orthographic_silence` |

The alif and its silence sign are written and never said. The rule instance
owns no attribution; the two glyphs carry an empty `presents` list and name it
as their reason.

### E8. Madd iwad, seat written - 2:5:3, stopped

`هُدًى`

| heard | written | rule |
|---|---|---|
| h | ه | |
| u | ُ | |
| d | د | |
| long a | ً ى | `madd_tabii` |
| - | ً | `pausal_sukun`: the tanween's noon |

One mark twice, because it supplies two units' facts: the base's vowel, which
lengthens, and the noon, which goes. The seat stops being silent rather than
being inserted, so the recited text replaces a glyph and adds none. "Madd
iwad" is the two rows read together.

### E9. Madd iwad, no seat - 2:22:11, stopped

`مَآءً`

| heard | written | rule |
|---|---|---|
| m | م | |
| long a | َ ا ٓ | `madd_wajib_muttasil` |
| glottal stop | ء | |
| long a | ً | `madd_tabii` |
| - | ً | `pausal_sukun` |

The same event as E8 with nothing to lengthen onto. The sound has a source
glyph, so it is not a gap row; what differs is the recited text, which writes
an alif the rasm does not have.

### E10. Taa marbuta with tanween - 2:26:9, stopped

`بَعُوضَةً`

| heard | written | rule |
|---|---|---|
| b | ب | |
| a | َ | |
| ayn | ع | |
| long u | ُ و | `madd_tabii` |
| emphatic d | ض | |
| a | َ | |
| h | ة | `taa_marbuta_pausal` |
| - | ً | `pausal_sukun` |

Two rules on one word doing two different things: one changes a letter's
sound, the other takes a sound away. The glyph does not change in either.

### E11. Qalqala at a stop - 113:1:3

`بِرَبِّ`

| heard | written | rule |
|---|---|---|
| b | ب | |
| i | ِ | |
| r | ر | |
| a | َ | |
| bb | ب ّ | |
| echo | ب ّ | `qalqala_kubra` |
| - | ِ | `pausal_sukun` |

The echo is hosted on the consonant and is an addition: the same part states
one realization, the doubled b, and carries the release beside it. Both rows
name the same glyphs, so under `alignment` they are one row owning two sounds.

### E12. Muqattaat - 2:1:1

`الٓمٓ`

| heard | written | rule |
|---|---|---|
| a | ا | |
| l | ا | |
| i | ا | |
| f | ا | |
| l | ل | |
| long a | ل ٓ | `madd_lazim` |
| m | ل | |
| m | م | |
| long i | م ٓ | `madd_lazim` |
| m | م | |

Three glyphs, ten sounds, and each letter's spoken name is several units with
`is_letter_name` set. Under `grouping="cluster"` this is three rows, each
owning a whole name.

### E13. Silah - 2:27:7, joined

`مِيثَـٰقِهِۦ`

| heard | written | rule |
|---|---|---|
| m | م | |
| long i | ِ ي | `madd_tabii` |
| th | ث | |
| long a | َ ٰ | `madd_tabii` |
| q | ق | |
| i | ِ | |
| h | ه | |
| long i | ِ ۦ | `madd_tabii` |

The pronoun haa's vowel is long joined and absent at a pause, which the vowel
kind says and no rule repeats. "Silah" is that kind plus the madd rule that
fired; stop on this word and the last row is a `pausal_sukun` instead.

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
that unit's own vowel; only the iltiqa kasra is attributed as an insertion,
and nothing constructs one yet.

| Sound | Rendered as |
|---|---|
| the hamza wasl's helping vowel, when started on | the haraka its grammar chooses |
| the iltiqa helping kasra | a kasra |

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
row of [02-gate](02-gate.md) section 6 maps onto at least one. Cases already
written in section 2 are marked with their example number.

**A. Script and vowels.** Plain word, no rule; long vowel as haraka plus
carrier; dagger alif (E6); long vowel with no carrier glyph (E2); otiose alif after
the plural waw (E7); alif maqsura; silent carrier under a dagger; shadda in the
rasm; muqattaat, one glyph and several units (E12); structural glyphs and the
concatenation law.

**B. Tanween.** Joined izhar; fathatan at waqf with a seat (E8); fathatan at waqf
with no seat and an alif rendered (E9); dammatan and kasratan at waqf; on taa
marbuta at waqf (E10); meeting a sakin, the inserted kasra.

**C. Boundary.** Waqf on a final short vowel (E3); taa marbuta to a heh;
ibtidaa with the hamza wasl sounding, all three vowels, both spelling
policies; wasl with the hamza silent (E4); iltiqa shortening a long vowel; sakt;
silah joined and at waqf (E13); the seven alifs joined and stopped; madd leen at
waqf; the stop that hands itself back at 27:36.

**D. Noon sakinah and tanween**, each in both its forms. Izhar halqi; izhar
mutlaq; ikhfaa haqiqi; iqlab; idgham bi ghunnah cross-word (E1); idgham bila
ghunnah; ghunnah mushaddadah on noon and on meem.

**E. Meem sakinah.** Izhar shafawi; ikhfaa shafawi; idgham shafawi.

**F. Idgham of adjacent consonants.** Mutamathilayn; mutaqaribayn;
mutajanisayn kamil; mutajanisayn naqis, which does not merge; lam shamsiyyah (E5);
lam qamariyyah (E4, E6).

**G. Madd.** Tabii; wajib muttasil; jaiz munfasil and its reversion at waqf;
lazim; arid lil sukun; leen, whose edge lands on a consonant; iwad; the pausal
glide; the badal.

**H. Colour.** Tafkheem spreading to a fatha; raa heavy; raa light; the divine
lam heavy and light; imala; tashil; ishmam, the soundless instance; ikhfaa
before an istilaa letter, which nothing can currently produce.

**I. Release.** Qalqala sughra; kubra (E11); akbar; suppressed by an idgham that
never releases.

**J. Muqattaat.** One name with its madd lazim (E12); idgham across the seam between
two names; the seam to the following word.
