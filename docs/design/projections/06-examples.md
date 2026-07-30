# 06 - Worked examples: what the contract says, case by case

Status: **format seed**. Three examples, the format the remaining fifty-odd
will use, and the inventory to audit for coverage. Scope: Uthmani, Hafs.

Every example is **generated from the branch at this head**. Where the model
cannot yet say something the contract promises, the row says so.

Names follow [05-vocabulary](05-vocabulary.md), renames included.

---

## 1. The format

One table. Rows are sounds in reading order; a row with `-` heard is something
written that is not said.

| Column | Holds |
|---|---|
| heard | the token |
| written | the glyphs that produce it, in source order. `+` joins glyphs from different words |
| rule | the rule instance, and a short note only when the row is not self-explanatory |

No indices. Rows are the links: what is on a row belongs together. Cross-word
and merge cases show two words; everything else shows one.

---

## 2. Three examples

### E1. Cross-word idgham bi ghunnah - 2:5:3-4, joined

`هُدًى مِّن` -> `h u d a m̃ i n`

| heard | written | rule |
|---|---|---|
| h | ه | |
| u | ُ | |
| d | د | |
| a | ً | |
| m̃ | ً + مّ | `idgham_bi_ghunnah` - the tanween's noon merges into word 2's meem |
| i | ِ | |
| n | ن | |
| - | ى | otiose seat |

One mark, three facts: `ً` is the dal's vowel, the noon's letter, and the
noon's silence. One sound, two words. The token is `m̃`, not `m̃m̃` - a held
nasal is already a doubled letter's sound, so the alphabet does not double it.

The word-initial `ّ` witnesses the assimilation without asserting it: stop on
word 1 and the meem sounds plain.

### E2. The divine name, joined - 1:2:2

`لِلَّهِ` -> `l i ll a: h i`

| heard | written | rule |
|---|---|---|
| l | ل | |
| i | ِ | |
| ll | لّ | |
| a: | َ | `madd_tabii` - **B5: no rule instance exists today** |
| h | ه | |
| i | ِ | |

No dagger alif in the rasm anywhere in this word, so the fatha alone writes a
long vowel. Rule-to-glyph for the madd returns nothing; glyph-to-sound still
links `َ` to `a:`.

The lam is light here - it follows a kasra - so no `tafkheem` instance fires.

### E3. Stopping on a word - 2:2:1, stopped

`ذَٰلِكَ` -> `ð a: l i k`

| heard | written | rule |
|---|---|---|
| ð | ذ | |
| a: | َ ٰ | two glyphs, one vowel, neither the owner |
| l | ل | |
| i | ِ | |
| k | ك | |
| - | َ | `pausal_sukun` |

The last two rows are why `Part` exists: the kaf's consonant sounds while the
kaf's vowel is silent.

---

## 3. Sounds with no glyph, and what gets rendered for them

"No rendered glyph is empty" (04 B8) means every inserted sound names the
character to draw. The full set, counted:

| Sound with no source glyph | Sites | Rendered as |
|---|---|---|
| the wasl hamza's helping vowel, when started on | 13,483 | the haraka `َ` `ِ` `ُ` its grammar chooses |
| the divine name's long `aa` | 2,704 | a dagger alif `ٰ` |
| madd iwad where no seat is written (all `ءً`) | 78 | an alif `ا` |
| the iltiqa helping kasra | 46 | a kasra `ِ` |

The other 3,156 iwad sites need no insertion: the seat is already written and
stops being silent, which is a `replaced` rendering, not an `inserted` one.

The qalqala echo is not in this table. It is a `release` sound, not a letter,
and the recited text does not write it - which is also why the `Q` token has
to be filterable in the flat stream.

**Recited writing takes a policy, like `cells` does.**

| `spelling` | The wasl hamza renders as | For |
|---|---|---|
| `faithful` | `ٱ` plus the helping haraka | keeps every source glyph recognisable |
| `explicit` | `أ` or `إ` per the vowel | a display that wants the hamza's seat to show which vowel it takes |

---

## 4. The inventory still to produce

Roughly 55 cases, ordered so each mechanism appears before the rules that
depend on it. Every row of 02-gate §6's adequacy matrix maps onto at least one.

**A. Script and vowels** - A1 plain word, no rule · A2 long vowel as haraka
plus carrier · A3 dagger alif · A4 long vowel with no carrier glyph (E2) ·
A5 otiose alif after the plural waw · A6 alif maqsura · A7 silent carrier
under a dagger · A8 shadda in the rasm · A9 muqattaat: one glyph, four units ·
A10 structural glyphs and the concatenation law

**B. Tanween** - B1 joined, izhar · B2 fathatan at waqf, seat written ·
B3 fathatan at waqf, **no seat, alif rendered** · B4 dammatan and kasratan at
waqf · B5 on taa marbuta at waqf · B6 meeting a sakin: **the inserted kasra**

**C. Boundary** - C1 waqf on a final short vowel (E3) · C2 taa marbuta to `h`
· C3 ibtidaa: the wasl hamza sounds, all three vowels, both spelling policies
· C4 wasl: the hamza silent · C5 iltiqa: a long vowel shortens · C6 sakt ·
C7 silah joined and at waqf · C8 the seven alifs joined and stopped - **the
M1 defect as it is** · C9 madd leen at waqf · C10 the stop that hands itself
back, 27:36

**D. Noon sakinah and tanween**, each with its noon and its tanween form -
D1 izhar halqi · D2 izhar mutlaq · D3 ikhfaa haqiqi · D4 iqlab · D5 idgham bi
ghunnah cross-word (E1) · D6 idgham bila ghunnah · D7 ghunnah mushaddadah on
noon and on meem

**E. Meem sakinah** - E1 izhar shafawi · E2 ikhfaa shafawi · E3 idgham shafawi

**F. Idgham of adjacent consonants** - F1 mutamathilayn · F2 mutaqaribayn ·
F3 mutajanisayn kamil · F4 mutajanisayn naqis, **which does not merge** ·
F5 lam shamsiyyah · F6 lam qamariyyah

**G. Madd** - G1 tabii · G2 wajib muttasil · G3 jaiz munfasil and its
reversion at waqf · G4 lazim · G5 arid lil sukun · G6 leen, **whose edge lands
on a consonant** · G7 iwad · G8 the pausal glide, `huwa` to `huu` · G9 ibdal
hamza

**H. Colour** - H1 tafkheem spreading to a fatha · H2 raa heavy · H3 raa light
· H4 the divine lam heavy and light · H5 imala 11:41 · H6 tashil 41:44 ·
H7 ishmam 12:11, **the soundless instance** · H8 ikhfaa before an istilaa
letter - **B9, which nothing can currently produce**

**I. Release** - I1 qalqala sughra · I2 kubra · I3 akbar · I4 suppressed by an
idgham that never releases

**J. Muqattaat** - J1 one name with its madd lazim · J2 idgham across the seam
between two names · J3 the seam to the following word
