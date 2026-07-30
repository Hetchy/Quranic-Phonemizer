# 06 - Worked examples: what the contract says, case by case

Status: **format seed**. Three examples, the format they are written in, and
the full inventory still to be produced. Scope: Uthmani, Hafs.

Every example here is **generated from the branch at this head**, not written
by hand. Where the current model cannot say something the contract promises,
the example says so rather than showing the intended output - those are the
rows that justify C1-C6.

Names follow [05-vocabulary](05-vocabulary.md)'s *proposals*, including the
renames. If a rename is rejected these examples change with it, which is the
point: they are the strongest argument for or against each one.

---

## 1. The format

Two tables and two lines of prose per case.

- **Header** - the case, the ref, and the boundary mode, because most of these
  facts are boundary-conditional.
- **One line** - the source, and the token stream it produces.
- **units** - the canonical positions in the example. Indices are local to the
  example, starting at `u0`.
- **reading** - one row per sound, in reading order, plus a row for anything
  written that is *not* heard. Indices local, starting at `s0`.
- **Notice** - one or two sentences naming what this case exists to show.

A row in **reading** with `-` in the token column is something the script
wrote that produced no sound. That keeps silence, orthographic-only glyphs and
soundless occurrences in the same scannable list as everything else, instead
of in three appendices.

Cross-word and merge cases show two words. Everything else shows one.

---

## 2. Three examples

### E1. Cross-word idgham bi ghunnah - 2:5:3-4, joined

`هُدًى مِّن` -> `h u d a m̃m̃ i n`

| unit | word | letter | onset | nucleus | flags |
|---|---|---|---|---|---|
| u0 | 3 | heh | plain | short `u` | |
| u1 | 3 | dal | plain | short `a` | |
| u2 | 3 | noon | plain | silent | **tanween** |
| u3 | 4 | meem | plain | short `i` | |
| u4 | 4 | noon | plain | silent | |

| | token | attribution | by | glyphs |
|---|---|---|---|---|
| s0 | `h` | hosts u0 onset | - | `ه` supplies letter |
| s1 | `u` | hosts u0 nucleus | - | `ُ` supplies nucleus |
| s2 | `d` | hosts u1 onset | - | `د` supplies letter |
| s3 | `a` | hosts u1 nucleus | - | `ً` supplies nucleus |
| s4 | `m̃m̃` | **hosts u3 onset** + **merged u2 onset** | `idgham_bi_ghunnah` | `م` supplies letter, `ّ` **witnesses** assimilation, `ً` supplies u2's letter and nucleus |
| s5 | `i` | hosts u3 nucleus | - | `ِ` supplies nucleus |
| s6 | `n` | hosts u4 onset | - | `ن` supplies letter |
| - | - | - | - | `ى` **decorates** u2 - the otiose seat, written-only |
| - | - | - | - | ` ` and `ۖ` structural |

**occurrence** `idgham_bi_ghunnah`: source `u2` (the tanween noon), trigger
`u3` (the following meem), target `u3` onset.

**Notice.** One sound, two units, two *words*: `s4` has a `hosts` edge in word
4 and a `merged` edge in word 3, sharing one sound index and one occurrence.
That pair **is** the merger; there is no `assimilated` flag anywhere. And one
glyph, three facts: the single tanween mark `ً` supplies u1's vowel, u2's
letter and u2's silence, which is why a grapheme-keyed row could never carry
this and legacy had to invent an implicit cell with `chars=""`.

The word-initial `ّ` is a **witness**, not a supplier: it asserts no canonical
fact about u3 (u3's onset is `plain`, not `geminate` - the doubling comes from
the idgham, not from the rasm), it only says a rule of the `assimilation`
family happens here. If the reciter stopped on word 3 instead, this shadda
would be dropped and u3 would sound a plain `m`.

`s4`'s word is **4**, the host's - the 04 B3 decision. Legacy credited it
differently, and the legacy adapter re-slices using the `merged` edge.

### E2. The divine name, joined - 1:2:2

`لِلَّهِ` -> `l i ll a: h i`

| unit | word | letter | onset | nucleus | flags |
|---|---|---|---|---|---|
| u0 | 2 | lam | plain | short `i` | |
| u1 | 2 | lam | **geminate** | **long `a`** | word lexeme `divine_name` |
| u2 | 2 | heh | plain | short `i` | |

| | token | attribution | by | glyphs |
|---|---|---|---|---|
| s0 | `l` | hosts u0 onset | - | `ل` supplies letter |
| s1 | `i` | hosts u0 nucleus | - | `ِ` supplies nucleus |
| s2 | `ll` | hosts u1 onset | - | `ل` supplies letter, `ّ` supplies onset |
| s3 | `a:` | hosts u1 nucleus | **nothing** - see below | `َ` supplies nucleus |
| s4 | `h` | hosts u2 onset | - | `ه` supplies letter |
| s5 | `i` | hosts u2 nucleus | - | `ِ` supplies nucleus |

**Notice.** `s3` is a long `aa` written by a single fatha and no carrier at
all. `لِلَّهِ` has no dagger alef in the rasm; the length is a lexical fact the
build derives from the word's identity. So a consumer asking "which glyph do I
paint for this madd?" gets the fatha, and any design that stored `owner: Unit`
on the sound could not have answered at all. Compare `ٱللَّهِ` at 1:1:2, which
*does* write the dagger - same unit, same sound, different glyph fan-in.

The lam here is **light**: it follows a kasra, so no `tafkheem` occurrence
fires. `Word.lexeme = divine_name` is published as lexical identity, and the
heaviness is a separate occurrence that is simply absent in this word.

**This example is currently wrong, and B5 is why.** `s3` is a madd tabii and
carries no occurrence at all - the whole word produces zero occurrences today.
The frozen legacy baseline tags `madd_tabii` here (`1:2:2`, on the same
vowel), and `madd_tabii` is 41,543 of its attributions corpus-wide. After
**C5** the row reads `classifies s3, by madd_tabii`. Until then the
`tajweed_mappings` adapter cannot reproduce the most common tag in the Quran.

### E3. Stopping on a word - 2:2:1, stopped

`ذَٰلِكَ` -> `ð a: l i k`

| unit | word | letter | onset | nucleus | flags |
|---|---|---|---|---|---|
| u0 | 1 | thal | plain | long `a` | |
| u1 | 1 | lam | plain | short `i` | |
| u2 | 1 | kaf | plain | short `a` | |

| | token | attribution | by | glyphs |
|---|---|---|---|---|
| s0 | `ð` | hosts u0 onset | - | `ذ` supplies letter |
| s1 | `a:` | hosts u0 nucleus | - | `َ` supplies nucleus **and** `ٰ` supplies nucleus |
| s2 | `l` | hosts u1 onset | - | `ل` supplies letter |
| s3 | `i` | hosts u1 nucleus | - | `ِ` supplies nucleus |
| s4 | `k` | hosts u2 onset | - | `ك` supplies letter |
| - | - | **silent u2 nucleus** | `waqf_ending` | `َ` supplies nucleus - written, not heard |
| - | - | - | - | `ۛ` `ۛ` structural (stop advice), two spaces structural |

Word: `junction_after = waqf`, `advice = either_stop`.

**Notice.** The last row is the whole reason `Part` exists. u2's **onset**
hosts a sound while u2's **nucleus** is silent - one unit, two outcomes, and
no way to recover that from the sound alone. A `sounds: [...]` list on the
unit could not say it.

`s1` shows the ordinary long vowel: two glyphs, the fatha and the dagger,
both supplying the same nucleus fact of the same unit. Neither is the owner.
Which one a UI paints is a rendering policy over these two edges, not a field
the producer stores.

The final fatha is still `supplies nucleus` even though the vowel is not
heard. Spelling says what the script asserts; the attribution says what
happened to it. Collapsing the two is what made legacy's `status` enum
necessary.

---

## 3. What this format does not show, and why

- **`source_index` and `word_index`** are omitted from the glyph column. They
  are mechanical, and printing two integers per glyph would double the width
  of the busiest column for no reading gain. One example in the final set
  (`A10`, structural glyphs) prints them, because that is the case where the
  concatenation law is the thing being demonstrated.
- **`Presents` edges** are folded into the glyph column's wording. "supplies
  letter" is the spelling edge; that the glyph also presents the attribution
  is implied. Two cases in the final set print contributions explicitly - the
  silent carrier under a dagger, and the maddah - because those are the two
  where `Presents` and the spelling edge disagree.
- **Notation** is IPA throughout. The token stream is a function of
  `notation`; nothing else in the contract is.

---

## 4. The inventory still to produce

Roughly 55 cases. Ordered so that a reader who works straight through meets
each mechanism before the rules that depend on it. Every row in 02-gate §6's
adequacy matrix maps onto at least one of these.

**A. Script and vowels - the machinery**

A1 plain word, no rule fires · A2 long vowel as haraka + carrier · A3 long
vowel as dagger alef · A4 long vowel with no carrier glyph (E2) · A5 otiose
alef after the plural waw · A6 alef maqsura · A7 silent carrier waw under a
dagger · A8 shadda in the rasm · A9 muqattaat: one glyph, four units ·
A10 structural glyphs and the concatenation law

**B. Tanween**

B1 tanween joined, izhar · B2 fathatan at waqf -> iwad · B3 dammatan and
kasratan at waqf, dropped · B4 tanween on taa marbuta at waqf · B5 tanween
meeting a sakin -> the inserted kasra

**C. Boundary**

C1 waqf on a final short vowel (E3) · C2 taa marbuta -> `h` at waqf ·
C3 ibtidaa: the wasl hamza sounds, all three qualities · C4 wasl: the wasl
hamza is silent · C5 iltiqa: a long vowel shortens · C6 sakt · C7 silah joined
and silah at waqf · C8 the seven alifs, joined and stopped - **the 04 M1
defect, shown as it is** · C9 madd leen at waqf · C10 the stop that hands
itself back (27:36)

**D. Noon sakinah and tanween** - each with its noon and its tanween form

D1 izhar halqi · D2 izhar mutlaq, within one word · D3 ikhfaa haqiqi ·
D4 iqlab · D5 idgham bi ghunnah, cross-word (E1) · D6 idgham bila ghunnah ·
D7 ghunnah mushaddadah, on noon and on meem

**E. Meem sakinah**

E1 izhar shafawi · E2 ikhfaa shafawi · E3 idgham shafawi

**F. Idgham of adjacent consonants**

F1 mutamathilayn · F2 mutaqaribayn · F3 mutajanisayn kamil ·
F4 mutajanisayn naqis - **the one that does not merge** · F5 lam shamsiyyah ·
F6 lam qamariyyah

**G. Madd**

G1 tabii · G2 wajib muttasil · G3 jaiz munfasil, and its reversion at waqf ·
G4 lazim · G5 arid lil sukun · G6 leen - **the `classifies` edge lands on a
consonant, 04 N3** · G7 iwad · G8 the pausal glide, `huwa` -> `huu` - **the
one madd occurrence that owns its sound** · G9 ibdal hamza

**H. Colour**

H1 tafkheem on an istilaa letter, spreading to its fatha · H2 raa heavy ·
H3 raa light · H4 the divine lam, heavy and light · H5 imala, 11:41 ·
H6 tashil, 41:44 · H7 ishmam, 12:11 - **the soundless occurrence, 04 B2**

**I. Release**

I1 qalqala sughra · I2 qalqala kubra · I3 qalqala akbar · I4 qalqala
suppressed by an idgham that never releases the closure

**J. Muqattaat**

J1 one name with its madd lazim · J2 idgham across the seam between two names
· J3 the seam from the last name to the following word

Each family's example set fixes its **participant role assignment**, which is
C1's specification and which no document currently states for any family
(04 M6).
