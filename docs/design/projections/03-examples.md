# 03 - Worked examples

Status: **proposed**. Scope: Uthmani, Hafs.

Twenty-one passages, each written out as the document
[01-contract](01-contract.md) says it must look. Every phoneme string is the
package's own output for that request and boundary plan, in the notation it
ships; the source words are taken from the corpus, and everything else - the
recited spelling, the unit rows, the pairings and the rule names - is authored,
because none of it exists yet. A reader checks three things with them: that the
laws of [02-gate](02-gate.md) hold on a real passage, that every row of
[06-two-texts](06-two-texts.md) and every rule of [07-rules](07-rules.md) has a
place where a consumer can see it, and that the six relationships of
[01-contract](01-contract.md) section 2 cost what that document says they cost.
Where they do not, the example says so and the closing list collects it.

---

## 1. The format

Three parts, and a header. The header names the request and its boundary plan,
then gives one row per word: what the mushaf wrote, what recitation spells, and
the sounds. Where an example carries two boundary plans, the second header
repeats only the words that change.

**Part 1, units and parts.** One row per part of a unit, in reading order.

| Column | Holds |
|---|---|
| unit | the word, and the unit's letter by name |
| part | `consonant` or `vowel` |
| realization | the attribution: hosts, merged into, silent, or `not applicable` |
| on the sound | the modifier: a colour, a length, a classification |

`not applicable` is a unit whose vowel is absent in both its joined and its
stopped form: there is nothing for a rule to take, so the part states no
realization. A modifier cell reads `named <state>, rule` where the rule only
classifies the sound, and `<state>, rule` where it changed it. So a heavy raa
is `heavy, tafkheem` and a light one is `named light, tarqeeq`, and the two
sit in different edge families.

**Part 2, pairings.** One row per pairing of the selected text, stated for
`text="source"` and `grouping="cluster"` unless the example exists to show
another quadrant.

| Column | Holds |
|---|---|
| source | the pairing's source glyphs, as characters |
| recited | the rendered glyphs, as characters. Empty where nothing is written |
| owns | the sounds this pairing owns |
| shares | sounds it presents that another pairing owns |
| silent | its own glyphs that are written and not said |
| rules | every rule a consumer would colour on these glyphs |

A gap pairing has an empty source cell and an `after` naming the pairing it
follows. `rules` is total: it holds every rule shown on these glyphs whichever
edge family it came through. A glyph is in `silent` when it shows no sound and
the pairing names the rule for that silence; a glyph a merger took shows its
host's sound in `shares` and is not there, and a haraka the stop replaced with
a sukun is there because `pausal_sukun` names it.

A bare combining mark is written with a dotted circle: `◌َ` is a fatha, `◌ً` a
fathatan, `◌ْ` a sukun, `◌ّ` a shadda, `◌ٰ` a dagger alif, `◌ٓ` a maddah. A
tatweel carries the `Structural` edge and takes no pairing, so it is absent
from the source cells a font would draw it in: `تَٰ` is the pairing of
`ٱلْكِتَـٰبُ`, and the tatweel between the fatha and the dagger is in neither.

**Part 3, the walk.** The six relationships of
[01-contract](01-contract.md) section 2, and only where one is interesting.

| Column | Holds |
|---|---|
| relationship | one of the six |
| what a consumer must do | the calls and the field reads |
| cost | what it costs, and what it cannot answer |

A relationship with no answer is a **FINDING** and is marked as one. Where
every relationship is one call and one field read, the example says so in a
line and moves on. A row named `identity` is not one of the six: it records
something a consumer needs about the request that no relationship reaches.

---

## 2. The examples

### E1. The ordinary word

`mappings("2:2")`, joined throughout, stopping after the last word. The tables
are word 2.

| word | source | recited | phonemes |
|---|---|---|---|
| 2 | ٱلْكِتَـٰبُ | لْكِتَابُ | `l k i t a: b u` |

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w2 hamza | consonant | silent, `hamza_wasl_elision` | |
| w2 hamza | vowel | silent, `hamza_wasl_elision` | |
| w2 lam | consonant | hosts `l` | named plain, `lam_qamariyyah` |
| w2 lam | vowel | not applicable | |
| w2 kaf | consonant | hosts `k` | |
| w2 kaf | vowel | hosts `i` | |
| w2 ta | consonant | hosts `t` | |
| w2 ta | vowel | hosts `a:` | long, `madd_tabii` |
| w2 ba | consonant | hosts `b` | |
| w2 ba | vowel | hosts `u` | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| ٱ | | | | ٱ | `hamza_wasl_elision` |
| لْ | لْ | `l` | | | `lam_qamariyyah` |
| كِ | كِ | `k` `i` | | | |
| تَٰ | تَا | `t` `a:` | | | `madd_tabii` |
| بُ | بُ | `b` `u` | | | |

The tatweel sits between the fatha and the dagger, carries the `Structural`
edge, takes no pairing and is dropped (row 11); the space before the word
carries the same edge and is kept (row 31). The elided seat produces no
rendered glyph rather than an empty one, and the dagger's expansion into a
written alif is row 26.

**Part 3, the walk.** Every relationship is one call and one field read.

Word 2 is the baseline the rest of the set is awkward against: one unit per
cluster, one realization per part, no sound shared, no gap, and every rule
reachable from the glyphs it is drawn on.

### E2. A dagger over a written carrier, and a seat that stops being silent

Plan A: `mappings("2:28:4-2:28:8")`, joined throughout, stopping after word 8.

| word | source | recited | phonemes |
|---|---|---|---|
| 4 | وَكُنتُمْ | وَكُنتُمْ | `w a k u ŋ t u m` |
| 5 | أَمْوَٰتًا | أَمْوَاتَن | `ʔ a m w a: t a ŋ` |
| 6 | فَأَحْيَـٰكُمْ ۖ | فَأَحْيَاكُمْ ۖ | `f a ʔ a ħ j a: k u m` |
| 7 | ثُمَّ | ثُمَّ | `θ u m̃ a` |
| 8 | يُمِيتُكُمْ | يُمِيتُكُمْ | `j u m i: t u k u m` |

Plan B: `mappings("2:28:4-2:28:5")`, joined, stopping after word 5.

| word | source | recited | phonemes |
|---|---|---|---|
| 5 | أَمْوَٰتًا | أَمْوَاتَا | `ʔ a m w a: t a:` |

Word 5's fathatan is 4.1a's ikhfaa line under plan A, the haraka then a bare
noon, and its seat goes by row 4; under plan B the fathatan becomes a fatha
(row 21) and the same seat stops being silent (row 28).

**Part 1, units and parts**, plan A.

| unit | part | realization | on the sound |
|---|---|---|---|
| w4 waw | consonant | hosts `w` | |
| w4 waw | vowel | hosts `a` | |
| w4 kaf | consonant | hosts `k` | |
| w4 kaf | vowel | hosts `u` | |
| w4 noon | consonant | hosts `ŋ`, by `ikhfaa_haqiqi` | a hum, not doubled |
| w4 noon | vowel | not applicable | |
| w4 ta | consonant | hosts `t` | |
| w4 ta | vowel | hosts `u` | |
| w4 meem | consonant | hosts `m` | named plain, `izhar_shafawi` |
| w4 meem | vowel | not applicable | |
| w5 hamza | consonant | hosts `ʔ` | |
| w5 hamza | vowel | hosts `a` | |
| w5 meem | consonant | hosts `m` | named plain, `izhar_shafawi` |
| w5 meem | vowel | not applicable | |
| w5 waw | consonant | hosts `w` | |
| w5 waw | vowel | hosts `a:` | long, `madd_tabii` |
| w5 ta | consonant | hosts `t` | |
| w5 ta | vowel | hosts `a` | |
| w5 noon (tanween) | consonant | hosts `ŋ`, by `ikhfaa_haqiqi` | a hum, not doubled |
| w5 noon (tanween) | vowel | not applicable | |
| w6 fa | consonant | hosts `f` | |
| w6 fa | vowel | hosts `a` | |
| w6 hamza | consonant | hosts `ʔ` | |
| w6 hamza | vowel | hosts `a` | |
| w6 ha | consonant | hosts `ħ` | |
| w6 ha | vowel | not applicable | |
| w6 ya | consonant | hosts `j` | |
| w6 ya | vowel | hosts `a:` | long, `madd_tabii` |
| w6 kaf | consonant | hosts `k` | |
| w6 kaf | vowel | hosts `u` | |
| w6 meem | consonant | hosts `m` | named plain, `izhar_shafawi` |
| w6 meem | vowel | not applicable | |
| w7 tha | consonant | hosts `θ` | |
| w7 tha | vowel | hosts `u` | |
| w7 meem | consonant | hosts `m̃` | doubled, with ghunnah; named, `ghunnah_mushaddadah` |
| w7 meem | vowel | hosts `a` | |
| w8 ya | consonant | hosts `j` | |
| w8 ya | vowel | hosts `u` | |
| w8 meem | consonant | hosts `m` | |
| w8 meem | vowel | hosts `i:` | long, `madd_tabii` |
| w8 ta | consonant | hosts `t` | |
| w8 ta | vowel | hosts `u` | |
| w8 kaf | consonant | hosts `k` | |
| w8 kaf | vowel | hosts `u` | |
| w8 meem | consonant | hosts `m` | |
| w8 meem | vowel | not applicable | |

Word 8 is stopped on and no `pausal_sukun` fires: its final vowel is absent in
both forms, so there is no part for the stop to take.

**Part 1**, plan B, the rows that differ. Word 4 is unchanged and words 6 to 8
are outside the request.

| unit | part | realization | on the sound |
|---|---|---|---|
| w5 ta | vowel | hosts `a:` | long, `madd_tabii`; labelled `madd_iwad` |
| w5 noon (tanween) | consonant | silent, `pausal_sukun` | |

**Part 2, pairings**, word 5, `text="source"`, `grouping="glyph"`. A token that
repeats in the word carries its position in that word's phoneme string.

Plan A:

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| أ | أ | `ʔ` | | | |
| ◌َ | ◌َ | `a` (2) | | | |
| م | م | `m` | | | `izhar_shafawi` |
| ◌ْ | ◌ْ | | | | `izhar_shafawi` |
| و | و | `w` | | | |
| ◌َ | ◌َ | | `a:` | | `madd_tabii` |
| ◌ٰ | ا | `a:` | | | `madd_tabii` |
| ت | ت | `t` | | | |
| ◌ً | ◌َ, ن | `a` (7) `ŋ` | | | `ikhfaa_haqiqi` |
| ا | | | | ا | `orthographic_silence` |

Plan B:

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| أ | أ | `ʔ` | | | |
| ◌َ | ◌َ | `a` | | | |
| م | م | `m` | | | `izhar_shafawi` |
| ◌ْ | ◌ْ | | | | `izhar_shafawi` |
| و | و | `w` | | | |
| ◌َ | ◌َ | | `a:` (5) | | `madd_tabii` |
| ◌ٰ | ا | `a:` (5) | | | `madd_tabii` |
| ت | ت | `t` | | | |
| ◌ً | ◌َ | | `a:` (7) | | `madd_tabii`, `pausal_sukun` |
| ا | ا | `a:` (7) | | | `madd_tabii` |

The waw under the dagger presents its own consonant and does not present the
vowel: the dagger supplies the length and owns the sound, the fatha supplies
the quality and shares it. The final seat is one character in one place under
both plans, `silent` under A and owning the length under B. Word 6 carries a
tatweel, a space and the stop sign ۖ; all three take no pairing, and the
recited text drops the first (row 11) and keeps the other two (rows 31 and 30).

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - sound | colour the fathatan for the hum under plan A | one field read, and it over-reaches: one scalar owns two units' sounds, so a consumer that wants the hum alone has no sub-glyph answer on this text |
| script - rules | reach the tanween noon's silence under plan B through the fathatan's `rules` | one field read, and the same glyph is audible, so a consumer colouring silence paints a sounded character |
| recited - sound | read the row | one call and one field read, and the only side that separates the two units: the fathatan is two rendered glyphs under plan A |
| script - recited | diff the two plans | pairing indices are request-local, so a consumer keys on `source_index` and never on a pairing |
| the other two | | one call and one field read |

The word settles what an alignment quadrant is for: the same ten scalars, one
plan apart, move a sound's owner from the dagger's neighbour to a seat that was
silent, with no character changed anywhere.

### E3. Letters the rasm writes and recitation never says

`mappings("2:5:1-2:5:3")`, joined, stopping after word 3.

| word | source | recited | phonemes |
|---|---|---|---|
| 1 | أُو۟لَـٰٓئِكَ | أُلَآئِكَ | `ʔ u l a: ʔ i k a` |
| 2 | عَلَىٰ | عَلَا | `ʕ a l a:` |
| 3 | هُدًى | هُدَا | `h u d a:` |

Word 1's waw and its round zero are rows 3 and 5; word 2's dagger is row 26;
word 3's fathatan becomes a fatha (row 21), its seat stops being silent (row
31) and is written as the carrier the long a takes (row 17).

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w1 hamza | consonant | hosts `ʔ` | |
| w1 hamza | vowel | hosts `u` | |
| w1 lam | consonant | hosts `l` | |
| w1 lam | vowel | hosts `a:` | long, `madd_wajib_muttasil` |
| w1 hamza | consonant | hosts `ʔ` | |
| w1 hamza | vowel | hosts `i` | |
| w1 kaf | consonant | hosts `k` | |
| w1 kaf | vowel | hosts `a` | |
| w2 ain | consonant | hosts `ʕ` | |
| w2 ain | vowel | hosts `a` | |
| w2 lam | consonant | hosts `l` | |
| w2 lam | vowel | hosts `a:` | long, `madd_tabii` |
| w3 heh | consonant | hosts `h` | |
| w3 heh | vowel | hosts `u` | |
| w3 dal | consonant | hosts `d` | |
| w3 dal | vowel | hosts `a:` | long, `madd_tabii`; labelled `madd_iwad` |
| w3 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w3 noon (tanween) | vowel | not applicable | |

The waw of word 1 has no row here at all, and that is the whole of what
`orthographic_silence` is.

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| أُ | أُ | `ʔ` `u` | | | |
| و۟ | | | | و, ◌۟ | `orthographic_silence` |
| لَٰٓ | لَآ | `l` `a:` | | | `madd_wajib_muttasil` |
| ئِ | ئِ | `ʔ` `i` | | | |
| كَ | كَ | `k` `a` | | | |
| عَ | عَ | `ʕ` `a` | | | |
| لَ | لَ | `l` | `a:` | | `madd_tabii` |
| ىٰ | ا | `a:` | | | `madd_tabii` |
| هُ | هُ | `h` `u` | | | |
| دً | دَ | `d` | `a:` | | `madd_tabii`, `pausal_sukun` |
| ى | ا | `a:` | | | `madd_tabii` |

Two glyphs answer to no unit and take opposite treatment: the tatweel of word 1
carries the `Structural` edge, takes no pairing and is dropped, and the waw
with its round zero takes a pairing, owns nothing, and both its scalars are
`silent` under one instance. The maddah is inside the third pairing; under
`grouping="glyph"` it presents `a:` and supplies no fact. The alif maqsura of
word 2 is written under a dagger and is replaced by the carrier the dagger
spells; the bare one of word 3 is rewritten as the carrier the stop makes it.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - rules | start at `m.rules` and ask where each silence falls | the instance is reachable from the glyphs and the glyphs are not reachable from the instance, so the consumer scans every pairing's `rules`. Nothing else in the document needs that scan |
| sound - rules | walk sounds to rules | no answer, and correctly none: the instance owns no attribution and no modifier, so the walk never meets it. This is the exemption the completeness law already names |
| recited - sound, recited - rules | | the silenced glyphs are absent from the recited text, so the rule has no relation there at all |
| the other two | | one call and one field read |

One word settles both silent-glyph kinds and keeps them apart: a letter with no
unit takes a pairing and names its rule, and a structural glyph takes neither.

### E4. Started on, and the release at a pause

`mappings("1:2:1-1:2:3")`, started on ٱلْحَمْدُ, which is where the request
begins, joined, stopping after word 3.

| word | source | recited | phonemes |
|---|---|---|---|
| 1 | ٱلْحَمْدُ | أَلْحَمْدُ | `ʔ a l ħ a m d u` |
| 2 | لِلَّهِ | لِلَّاهِ | `l i ll a: h i` |
| 3 | رَبِّ | رَبّْ | `rˤ aˤ bb Q` |

Word 1 is rows 24 and 13 on the wasl seat; word 2 is row 16, the one insertion
whose sound the source text does write; word 3 is row 19.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w1 hamza | consonant | hosts `ʔ`, by `hamza_wasl_start` | |
| w1 hamza | vowel | hosts `a`, by `hamza_wasl_start` | |
| w1 lam | consonant | hosts `l` | named plain, `lam_qamariyyah` |
| w1 lam | vowel | not applicable | |
| w1 ha | consonant | hosts `ħ` | |
| w1 ha | vowel | hosts `a` | |
| w1 meem | consonant | hosts `m` | named plain, `izhar_shafawi` |
| w1 meem | vowel | not applicable | |
| w1 dal | consonant | hosts `d` | |
| w1 dal | vowel | hosts `u` | |
| w2 lam | consonant | hosts `l` | |
| w2 lam | vowel | hosts `i` | |
| w2 lam | consonant | hosts `ll` | |
| w2 lam | vowel | hosts `a:` | long, `madd_tabii` |
| w2 heh | consonant | hosts `h` | |
| w2 heh | vowel | hosts `i` | |
| w3 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w3 ra | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w3 ba | consonant | hosts `bb`, and the release `Q` beside it | the release is akbar, `qalqala_akbar` |
| w3 ba | vowel | silent, `pausal_sukun` | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| ٱ | أ | `ʔ` | | | `hamza_wasl_start` |
| (gap, after ٱ) | ◌َ | `a` | | | `hamza_wasl_start` |
| لْ | لْ | `l` | | | `lam_qamariyyah` |
| حَ | حَ | `ħ` `a` | | | |
| مْ | مْ | `m` | | | `izhar_shafawi` |
| دُ | دُ | `d` `u` | | | |
| لِ | لِ | `l` `i` | | | |
| لَّ | لَّ | `ll` `a:` | | | `madd_tabii` |
| هِ | هِ | `h` `i` | | | |
| رَ | رَ | `rˤ` `aˤ` | | | `tafkheem` |
| بِّ | بّْ | `bb` `Q` | | ◌ِ | `qalqala_akbar`, `pausal_sukun` |

The helping vowel takes a gap pairing because the rasm writes no haraka over
the seat, not because of how it was attributed: it is a `Hosts` on the hamza
unit like any other vowel. The divine name's `a:` has no length carrier in the
rasm, so ownership falls through to the glyph supplying the quality, and the
carrier recitation says is written into the recited text and named by no source
row. The release is the one sound with no glyph on either text, and the last
pairing owns two sounds for one part while the kasra it renders as a sukun is
`silent`.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - sound | draw the source text in order | a gap pairing has no source index, so the consumer cannot sort the rows on one key: it walks the glyph rows and splices each gap row in at the pairing its `after` names |
| script - recited | read `rendered` down the source rows | **FINDING.** An inserted rendered glyph names no source glyph, and nothing says which source pairing carries it. The helping fatha has a gap pairing to sit on; the divine name's alif has none, so the concatenation is short of a character recitation says, and a teleprompter reading the two columns off one row loses it |
| recited - sound | read the row | one call and one field read. The release has no rendered glyph and takes no gap pairing there, because it rides on the pairing of the consonant that makes it |
| the other three | | one call and one field read |

The word settles that the gap criterion is the text and is read per part: the
release is shown by the glyph of the consonant that makes it, and the helping
vowel is shown by nothing, because the rasm writes no haraka over the seat.

### E5. The cross-word merger

`mappings("2:5:3-2:5:4")`, joined, stopping after word 4.

| word | source | recited | phonemes |
|---|---|---|---|
| 3 | هُدًى | هُدَ | `h u d a` |
| 4 | مِّن | مِّنْ | `m̃ i n` |

Word 3 is 4.1a's idgham line, the haraka alone, and its seat goes by row 4.
Word 4 takes row 12: the rasm left the noon bare because an assimilation was
coming, the stop cancels it, and the sukun has to be written back.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w3 heh | consonant | hosts `h` | |
| w3 heh | vowel | hosts `u` | |
| w3 dal | consonant | hosts `d` | |
| w3 dal | vowel | hosts `a` | |
| w3 noon (tanween) | consonant | merged into `m̃`, by `idgham_bi_ghunnah` | |
| w3 noon (tanween) | vowel | not applicable | |
| w4 meem | consonant | hosts `m̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w4 meem | vowel | hosts `i` | |
| w4 noon | consonant | hosts `n` | |
| w4 noon | vowel | not applicable | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| هُ | هُ | `h` `u` | | | |
| دً | دَ | `d` `a` | `m̃` | | `idgham_bi_ghunnah` |
| ى | | | | ى | `orthographic_silence` |
| مِّ | مِّ | `m̃` `i` | | | `idgham_bi_ghunnah` |
| ن | نْ | `n` | | | |

The sound the first word's tanween helps make is owned in the second word, and
`shares` is the only field that reaches across: nothing on the tanween's own
row names the meem, and nothing on the meem's row names the tanween. The seat
ى goes because the plan joins here; stop on هُدًى instead, as E3 does, and the
same seat carries a long a and is not silent at all.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - sound | ask what دً makes audible | two field reads and one lookup: it owns two sounds and shares a third, and the shared one is owned in another word, so the consumer follows the owning pairing to learn which word times it |
| script - rules | highlight `idgham_bi_ghunnah` | the instance sits in two pairings in two words, and a highlight driven off either one lights half the rule. The consumer unions every pairing naming the instance |
| script - recited | ask why ى is unwritten | an absent rendered index says only that something is unrepresented; the cause is on the source side, in `silent` and `rules` |
| recited - rules | attribute the sukun of نْ | **FINDING.** No rule instance owns it. The noon's vowel is absent in its joined form and its stopped form alike, so the pause takes nothing from it and mints nothing, and a consumer colouring the recited text has a glyph it cannot attribute. Row 14 names `pausal_sukun` as its owner and no such instance exists |
| the other two | | one call and one field read |

The fixed cross-word case: the sound lives in the second word, the source glyph
is silent, and `shares` is the only thing joining them.

### E6. Every outcome the noon and the meem have

`mappings("106:4")`, joined throughout, stopping after word 7.

| word | source | recited | phonemes |
|---|---|---|---|
| 1 | ٱلَّذِىٓ | أَلَّذِىٓ | `ʔ a ll a ð i:` |
| 2 | أَطْعَمَهُم | أَطْعَمَهُ | `ʔ a tˤ Q ʕ a m a h u` |
| 3 | مِّن | مِّن | `m̃ i ŋ` |
| 4 | جُوعٍ | جُوعِ | `ʒ u: ʕ i` |
| 5 | وَءَامَنَهُم | وَّءَامَنَهُ | `w̃ a ʔ a: m a n a h u` |
| 6 | مِّنْ | مِّنْ | `m̃ i n` |
| 7 | خَوْفٍ | خَوْفْ | `x aˤ w f` |

Word 1 is rows 24 and 13 on the wasl seat. The quiescent meems of words 2 and 5
go by row 7, and word 5 takes the shadda row 18 adds. Word 4's kasratan is
4.1a's idgham line and word 7's is row 20.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w1 hamza | consonant | hosts `ʔ`, by `hamza_wasl_start` | |
| w1 hamza | vowel | hosts `a`, by `hamza_wasl_start` | |
| w1 lam | consonant | hosts `ll` | |
| w1 lam | vowel | hosts `a` | |
| w1 thal | consonant | hosts `ð` | |
| w1 thal | vowel | hosts `i:` | long, `madd_jaiz_munfasil` |
| w2 hamza | consonant | hosts `ʔ` | |
| w2 hamza | vowel | hosts `a` | |
| w2 tah | consonant | hosts `tˤ`, and the release `Q` beside it | heavy, `tafkheem`; the release is sughra, `qalqala_sughra` |
| w2 tah | vowel | not applicable | |
| w2 ain | consonant | hosts `ʕ` | |
| w2 ain | vowel | hosts `a` | |
| w2 meem | consonant | hosts `m` | |
| w2 meem | vowel | hosts `a` | |
| w2 heh | consonant | hosts `h` | |
| w2 heh | vowel | hosts `u` | |
| w2 meem | consonant | merged into `m̃`, by `idgham_shafawi` | |
| w2 meem | vowel | not applicable | |
| w3 meem | consonant | hosts `m̃`, by `idgham_shafawi` | doubled, with ghunnah |
| w3 meem | vowel | hosts `i` | |
| w3 noon | consonant | hosts `ŋ`, by `ikhfaa_haqiqi` | a hum, not doubled |
| w3 noon | vowel | not applicable | |
| w4 jeem | consonant | hosts `ʒ` | |
| w4 jeem | vowel | hosts `u:` | long, `madd_tabii` |
| w4 ain | consonant | hosts `ʕ` | |
| w4 ain | vowel | hosts `i` | |
| w4 noon (tanween) | consonant | merged into `w̃`, by `idgham_bi_ghunnah` | |
| w4 noon (tanween) | vowel | not applicable | |
| w5 waw | consonant | hosts `w̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w5 waw | vowel | hosts `a` | |
| w5 hamza | consonant | hosts `ʔ` | |
| w5 hamza | vowel | hosts `a:` | long, `madd_tabii`; labelled `madd_badal` |
| w5 meem | consonant | hosts `m` | |
| w5 meem | vowel | hosts `a` | |
| w5 noon | consonant | hosts `n` | |
| w5 noon | vowel | hosts `a` | |
| w5 heh | consonant | hosts `h` | |
| w5 heh | vowel | hosts `u` | |
| w5 meem | consonant | merged into `m̃`, by `idgham_shafawi` | |
| w5 meem | vowel | not applicable | |
| w6 meem | consonant | hosts `m̃`, by `idgham_shafawi` | doubled, with ghunnah |
| w6 meem | vowel | hosts `i` | |
| w6 noon | consonant | hosts `n` | named plain, `izhar` |
| w6 noon | vowel | not applicable | |
| w7 kha | consonant | hosts `x` | heavy, `tafkheem` |
| w7 kha | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w7 waw | consonant | hosts `w` | named leen, `madd_leen` |
| w7 waw | vowel | not applicable | |
| w7 fa | consonant | hosts `f` | |
| w7 fa | vowel | silent, `pausal_sukun` | |
| w7 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w7 noon (tanween) | vowel | not applicable | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| ٱ | أ | `ʔ` | | | `hamza_wasl_start` |
| (gap, after ٱ) | ◌َ | `a` | | | `hamza_wasl_start` |
| لَّ | لَّ | `ll` `a` | | | |
| ذِ | ذِ | `ð` | `i:` | | `madd_jaiz_munfasil` |
| ىٓ | ىٓ | `i:` | | | `madd_jaiz_munfasil` |
| أَ | أَ | `ʔ` `a` | | | |
| طْ | طْ | `tˤ` `Q` | | | `tafkheem`, `qalqala_sughra` |
| عَ | عَ | `ʕ` `a` | | | |
| مَ | مَ | `m` `a` | | | |
| هُ | هُ | `h` `u` | | | |
| م | | | `m̃` | | `idgham_shafawi` |
| مِّ | مِّ | `m̃` `i` | | | `idgham_shafawi` |
| ن | ن | `ŋ` | | | `ikhfaa_haqiqi` |
| جُ | جُ | `ʒ` | `u:` | | `madd_tabii` |
| و | و | `u:` | | | `madd_tabii` |
| عٍ | عِ | `ʕ` `i` | `w̃` | | `idgham_bi_ghunnah` |
| وَ | وَّ | `w̃` `a` | | | `idgham_bi_ghunnah` |
| ءَ | ءَ | `ʔ` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| مَ | مَ | `m` `a` | | | |
| نَ | نَ | `n` `a` | | | |
| هُ | هُ | `h` `u` | | | |
| م | | | `m̃` | | `idgham_shafawi` |
| مِّ | مِّ | `m̃` `i` | | | `idgham_shafawi` |
| نْ | نْ | `n` | | | `izhar` |
| خَ | خَ | `x` `aˤ` | | | `tafkheem` |
| وْ | وْ | `w` | | | `madd_leen` |
| فٍ | فْ | `f` | | ◌ٍ | `pausal_sukun` |

Four noons under four outcomes and only `origin` separates them: two are
written and sakin, two are a tanween's. The rasm leaves a written noon bare
where an assimilation follows and writes its sukun where none does, which is
why مِّن and مِّنْ are two spellings of one word in one verse. The notation
writes the emphasis on the vowel the khaa governs and not on the khaa's own
token, although `tafkheem` names both sounds of that unit.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - sound | walk the source text forward | three sounds are owned in a later word than the glyph that helped make them, and the helping vowel of word 1 is owned by no source glyph at all, so it takes a gap pairing whose only link is `after`, pointing backwards. A consumer walking forward keeps its own index of gaps by anchor |
| script - rules | colour the noon of جُوعٍ | one field read that cannot be narrowed: the kasratan supplies the ain's vowel and the tanween's noon, so colouring the rule and colouring the vowel colour the same character. Under an ikhfaa the recited spelling would separate them by writing a bare noon beside the haraka; under this idgham it does not |
| recited - rules | highlight the merger on the recited line | the recited text writes the haraka alone, so the merged noon has no rendered glyph. The instance shows twice over the source glyphs and once over the recited ones, and the consumer loses the contributor |
| the other three | | one call and one field read |

One verse holds a written sakin noon and a tanween's noon under four different
outcomes, so `origin` is visibly the only thing telling them apart.

### E7. Close consonants, and the shadda a start drops

Plan A: `mappings("77:20")`, joined throughout, stopping after word 5.

| word | source | recited | phonemes |
|---|---|---|---|
| 1 | أَلَمْ | أَلَمْ | `ʔ a l a m` |
| 2 | نَخْلُقكُّم | نَخْلُكُّ | `n a x l u kk u` |
| 3 | مِّن | مِّ | `m̃ i` |
| 4 | مَّآءٍ | مَّآءِ | `m̃ a: ʔ i` |
| 5 | مَّهِينٍ | مَّهِينْ | `m̃ a h i: n` |

Plan B: `mappings("77:20:3-77:20:5")`, started on مِّن, joined, stopping after
word 5.

| word | source | recited | phonemes |
|---|---|---|---|
| 3 | مِّن | مِ | `m i` |

Word 2's qaf and its final meem go by row 7, and so does word 3's noon; the
hosts already carry their shadda, so row 18 adds nothing. Word 5 is row 20.
Under plan B word 3 loses its shadda to row 9.

**Part 1, units and parts**, plan A.

| unit | part | realization | on the sound |
|---|---|---|---|
| w1 hamza | consonant | hosts `ʔ` | |
| w1 hamza | vowel | hosts `a` | |
| w1 lam | consonant | hosts `l` | |
| w1 lam | vowel | hosts `a` | |
| w1 meem | consonant | hosts `m` | named plain, `izhar_shafawi` |
| w1 meem | vowel | not applicable | |
| w2 noon | consonant | hosts `n` | |
| w2 noon | vowel | hosts `a` | |
| w2 kha | consonant | hosts `x` | heavy, `tafkheem` |
| w2 kha | vowel | not applicable | |
| w2 lam | consonant | hosts `l` | |
| w2 lam | vowel | hosts `u` | |
| w2 qaf | consonant | merged into `kk`, by `idgham_mutaqaribayn` | |
| w2 qaf | vowel | not applicable | |
| w2 kaf | consonant | hosts `kk`, by `idgham_mutaqaribayn` | doubled |
| w2 kaf | vowel | hosts `u` | |
| w2 meem | consonant | merged into `m̃`, by `idgham_shafawi` | |
| w2 meem | vowel | not applicable | |
| w3 meem | consonant | hosts `m̃`, by `idgham_shafawi` | doubled, with ghunnah |
| w3 meem | vowel | hosts `i` | |
| w3 noon | consonant | merged into `m̃`, by `idgham_bi_ghunnah` | |
| w3 noon | vowel | not applicable | |
| w4 meem | consonant | hosts `m̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w4 meem | vowel | hosts `a:` | long, `madd_wajib_muttasil` |
| w4 hamza | consonant | hosts `ʔ` | |
| w4 hamza | vowel | hosts `i` | |
| w4 noon (tanween) | consonant | merged into `m̃`, by `idgham_bi_ghunnah` | |
| w4 noon (tanween) | vowel | not applicable | |
| w5 meem | consonant | hosts `m̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w5 meem | vowel | hosts `a` | |
| w5 heh | consonant | hosts `h` | |
| w5 heh | vowel | hosts `i:` | long, `madd_arid_lil_sukun` |
| w5 noon | consonant | hosts `n` | |
| w5 noon | vowel | silent, `pausal_sukun` | |
| w5 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w5 noon (tanween) | vowel | not applicable | |

The qaf loses its consonant to a complete merger, so no colour is stated for it
and the kaf that doubles is not heavy.

**Part 1**, plan B, the rows that differ.

| unit | part | realization | on the sound |
|---|---|---|---|
| w3 meem | consonant | hosts `m` | |
| w3 meem | vowel | hosts `i` | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`, plan A.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| أَ | أَ | `ʔ` `a` | | | |
| لَ | لَ | `l` `a` | | | |
| مْ | مْ | `m` | | | `izhar_shafawi` |
| نَ | نَ | `n` `a` | | | |
| خْ | خْ | `x` | | | `tafkheem` |
| لُ | لُ | `l` `u` | | | |
| ق | | | `kk` | | `idgham_mutaqaribayn` |
| كُّ | كُّ | `kk` `u` | | | `idgham_mutaqaribayn` |
| م | | | `m̃` | | `idgham_shafawi` |
| مِّ | مِّ | `m̃` `i` | | | `idgham_shafawi` |
| ن | | | `m̃` | | `idgham_bi_ghunnah` |
| مَّ | مَّ | `m̃` | `a:` | | `idgham_bi_ghunnah`, `madd_wajib_muttasil` |
| آ | آ | `a:` | | | `madd_wajib_muttasil` |
| ءٍ | ءِ | `ʔ` `i` | `m̃` | | `idgham_bi_ghunnah` |
| مَّ | مَّ | `m̃` `a` | | | `idgham_bi_ghunnah` |
| هِ | هِ | `h` | `i:` | | `madd_arid_lil_sukun` |
| ي | ي | `i:` | | | `madd_arid_lil_sukun` |
| نٍ | نْ | `n` | | ◌ٍ | `pausal_sukun` |

**Part 2**, plan B, the row that differs.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| مِّ | مِ | `m` `i` | | | |

Four mergers in five words and three of them cross a boundary. Three of the
table's `shares` point into the word after them; the others stay inside their
own word, one from the merger inside نَخْلُقكُّم and two from a long vowel whose
carrier owns what its haraka presents. أَلَمْ holds the quiescent meem that
keeps its own sound. Starting on the third word takes a glyph out of the
recited text that nothing accounts for.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - sound | ask what a cluster sounds like | six clusters present a sound another row owns, three of them a row in the next word, and ق owns nothing at all, so the pairing that answers is never the row the consumer is on |
| script - rules | colour نَخْلُقكُّم | three rules over six clusters, two glyphs dropped under two different rules, and the pairing says which rule without saying where the sound went. That is on the instance's `host` |
| script - recited | account for مِّ becoming مِ under plan B | **FINDING.** No rule instance owns the difference. An absent rendered index says only that the shadda is unrepresented, and the source side cannot name it either: a glyph in `silent` names its rule, and this one has none. Row 11 has no owner and no name in the vocabulary |
| recited - rules | colour the recited word مِّ under plan A | it shows one rule, minted for the meem of the word before it. The noon this word loses into the word after writes nothing on the recited line and colours nothing there, so one of the word's two mergers is invisible on the text a consumer is drawing |
| the other two | | one call and one field read |

Starting on the third word shows a shadda whose deletion no rule instance owns,
which is the shape E8 meets again on a different letter.

### E8. The taa marbuta at a pause

Plan A: `mappings("2:26:7-2:26:9")`, joined, stopping after word 9.

| word | source | recited | phonemes |
|---|---|---|---|
| 7 | مَثَلًا | مَثَلَ | `m a θ a l a` |
| 8 | مَّا | مَّا | `m̃ a:` |
| 9 | بَعُوضَةً | بَعُوضَهْ | `b a ʕ u: dˤ aˤ h` |

Plan B: `mappings("2:26:8-2:26:9")`, started on مَّا, joined, stopping after
word 9.

| word | source | recited | phonemes |
|---|---|---|---|
| 8 | مَّا | مَا | `m a:` |

Word 7 is 4.1a's idgham line and its seat goes by row 4. Word 9 is rows 1 and
24: the tanween goes and leaves no alif, and the taa marbuta is written as the
haa recitation says. Under plan B word 8 loses its shadda to row 9.

**Part 1, units and parts**, plan A.

| unit | part | realization | on the sound |
|---|---|---|---|
| w7 meem | consonant | hosts `m` | |
| w7 meem | vowel | hosts `a` | |
| w7 tha | consonant | hosts `θ` | |
| w7 tha | vowel | hosts `a` | |
| w7 lam | consonant | hosts `l` | |
| w7 lam | vowel | hosts `a` | |
| w7 noon (tanween) | consonant | merged into `m̃`, by `idgham_bi_ghunnah` | |
| w7 noon (tanween) | vowel | not applicable | |
| w8 meem | consonant | hosts `m̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w8 meem | vowel | hosts `a:` | long, `madd_tabii` |
| w9 ba | consonant | hosts `b` | |
| w9 ba | vowel | hosts `a` | |
| w9 ain | consonant | hosts `ʕ` | |
| w9 ain | vowel | hosts `u:` | long, `madd_tabii` |
| w9 dad | consonant | hosts `dˤ` | heavy, `tafkheem` |
| w9 dad | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w9 taa marbuta | consonant | hosts `h`, by `taa_marbuta_pausal` | |
| w9 taa marbuta | vowel | silent, `pausal_sukun` | |
| w9 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w9 noon (tanween) | vowel | not applicable | |

**Part 1**, plan B, the rows that differ.

| unit | part | realization | on the sound |
|---|---|---|---|
| w8 meem | consonant | hosts `m` | |
| w8 meem | vowel | hosts `a:` | long, `madd_tabii` |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`, plan A.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| مَ | مَ | `m` `a` | | | |
| ثَ | ثَ | `θ` `a` | | | |
| لً | لَ | `l` `a` | `m̃` | | `idgham_bi_ghunnah` |
| ا | | | | ا | `orthographic_silence` |
| مَّ | مَّ | `m̃` | `a:` | | `idgham_bi_ghunnah`, `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| بَ | بَ | `b` `a` | | | |
| عُ | عُ | `ʕ` | `u:` | | `madd_tabii` |
| و | و | `u:` | | | `madd_tabii` |
| ضَ | ضَ | `dˤ` `aˤ` | | | `tafkheem` |
| ةً | هْ | `h` | | ◌ً | `taa_marbuta_pausal`, `pausal_sukun` |

**Part 2**, plan B, the row that differs.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| مَّ | مَ | `m` | `a:` | | `madd_tabii` |

The recited هْ names the taa marbuta it replaces and carries a different
character, while ة stands unaltered in the source array beside it: neither text
is the other with edits applied. The fathatan of that cluster shows two units'
silences and the pairing lists it once, so which part each silence took is on
the attribution edges and nowhere else. No catalogue row inserts the sukun on
that haa: row 20 turns the tanween into a sukun, row 22 substitutes the letter, and rows 12,
22 and 23 each want a shape this word does not have.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - recited | compare ةً with هْ under plan A | one substituted glyph naming the taa marbuta, one inserted glyph naming nothing, and one source glyph named by neither. A consumer comparing characters sees a changed letter and has to read `silent` and `rules` to learn that a second glyph went and why |
| script - recited | account for مَّ becoming مَ under plan B | **FINDING.** No instance owns the missing shadda. This is the unowned deletion E7 shows under the same row, and the same dead end on both sides of it |
| script - rules | say which rule reached which part of ةً | two rules sit on one cluster and the letter level cannot separate them |
| script - sound | tell the two `shares` apart | لً shares a sound owned in the next word and عُ shares one owned by the carrier beside it, and the two read identically although one crosses a boundary and one does not |
| the other three | | one call and one field read |

A rendered glyph carries a different character from the single source glyph it
names, and the source array stands unchanged beside it.

### E9. A tanween said plainly, and the pronoun haa joined

`mappings("112:4")`, joined throughout, stopping after word 5.

| word | source | recited | phonemes |
|---|---|---|---|
| 1 | وَلَمْ | وَلَمْ | `w a l a m` |
| 2 | يَكُن | يَكُ | `j a k u` |
| 3 | لَّهُۥ | لَّهُو | `ll a h u:` |
| 4 | كُفُوًا | كُفُوَنْ | `k u f u w a n` |
| 5 | أَحَدٌ | أَحَدْ | `ʔ a ħ a d Q` |

Word 2's noon goes by row 7 and the host already carries its shadda. Word 3 is
row 27, the silah mark written out as a haraka and a carrier. Word 4 is 4.1a's
izhar line, the haraka then a noon bearing a sukun, and its seat goes by row 4.
Word 5 is row 20.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w1 waw | consonant | hosts `w` | |
| w1 waw | vowel | hosts `a` | |
| w1 lam | consonant | hosts `l` | |
| w1 lam | vowel | hosts `a` | |
| w1 meem | consonant | hosts `m` | named plain, `izhar_shafawi` |
| w1 meem | vowel | not applicable | |
| w2 ya | consonant | hosts `j` | |
| w2 ya | vowel | hosts `a` | |
| w2 kaf | consonant | hosts `k` | |
| w2 kaf | vowel | hosts `u` | |
| w2 noon | consonant | merged into `ll`, by `idgham_bila_ghunnah` | |
| w2 noon | vowel | not applicable | |
| w3 lam | consonant | hosts `ll`, by `idgham_bila_ghunnah` | doubled |
| w3 lam | vowel | hosts `a` | |
| w3 heh | consonant | hosts `h` | |
| w3 heh | vowel | hosts `u:` | long, `madd_tabii`; labelled `silah` |
| w4 kaf | consonant | hosts `k` | |
| w4 kaf | vowel | hosts `u` | |
| w4 fa | consonant | hosts `f` | |
| w4 fa | vowel | hosts `u` | |
| w4 waw | consonant | hosts `w` | |
| w4 waw | vowel | hosts `a` | |
| w4 noon (tanween) | consonant | hosts `n` | named plain, `izhar` |
| w4 noon (tanween) | vowel | not applicable | |
| w5 hamza | consonant | hosts `ʔ` | |
| w5 hamza | vowel | hosts `a` | |
| w5 ha | consonant | hosts `ħ` | |
| w5 ha | vowel | hosts `a` | |
| w5 dal | consonant | hosts `d`, and the release `Q` beside it | the release is kubra, `qalqala_kubra` |
| w5 dal | vowel | silent, `pausal_sukun` | |
| w5 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w5 noon (tanween) | vowel | not applicable | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| وَ | وَ | `w` `a` | | | |
| لَ | لَ | `l` `a` | | | |
| مْ | مْ | `m` | | | `izhar_shafawi` |
| يَ | يَ | `j` `a` | | | |
| كُ | كُ | `k` `u` | | | |
| ن | | | `ll` | | `idgham_bila_ghunnah` |
| لَّ | لَّ | `ll` `a` | | | `idgham_bila_ghunnah` |
| هُۥ | هُو | `h` `u:` | | | `madd_tabii` |
| كُ | كُ | `k` `u` | | | |
| فُ | فُ | `f` `u` | | | |
| وً | وَنْ | `w` `a` `n` | | | `izhar` |
| ا | | | | ا | `orthographic_silence` |
| أَ | أَ | `ʔ` `a` | | | |
| حَ | حَ | `ħ` `a` | | | |
| دٌ | دْ | `d` `Q` | | ◌ٌ | `qalqala_kubra`, `pausal_sukun` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - rules | colour a tanween mark | one field read, and the consumer chooses which of two units a highlight means: the fathatan of كُفُوًا shows the waw's vowel and the noon's `izhar`, and the dammatan of أَحَدٌ shows two units the stop takes together |
| script - recited | read the two irregular rows | one source cluster renders as three glyphs and one renders as nothing, both on the `rendered` column of their own row. One field read |
| the other four | | one call and one field read |

One mark is spelled two ways here: the fathatan becomes a fatha, a noon and a
sukun, because its noon is said plainly; the dammatan becomes a bare sukun,
because the stop takes both units it shows. The package grades this release
`qalqala_sughra` because its word-final test counts the tanween noon behind the
dal; the table carries the degree the converse law requires.

### E10. Two identical consonants, and the mark that instructs

`mappings("18:1:8-18:1:11")`, joined, stopping after word 11.

| word | source | recited | phonemes |
|---|---|---|---|
| 8 | وَلَمْ | وَلَمْ | `w a l a m` |
| 9 | يَجْعَل | يَجْعَ | `j a ʒ Q ʕ a` |
| 10 | لَّهُۥ | لَّهُو | `ll a h u:` |
| 11 | عِوَجَاۜ | عِوَجَاۜ | `ʕ i w a ʒ a:` |

The merger of word 9 is row 7 alone: the mushaf already doubles the host, so
row 18 has nothing to add. Word 10 is row 27. The sakt mark of word 11 is 4.7's
unchanged case, and so is the release.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w8 waw | consonant | hosts `w` | |
| w8 waw | vowel | hosts `a` | |
| w8 lam | consonant | hosts `l` | |
| w8 lam | vowel | hosts `a` | |
| w8 meem | consonant | hosts `m` | named plain, `izhar_shafawi` |
| w8 meem | vowel | not applicable | |
| w9 ya | consonant | hosts `j` | |
| w9 ya | vowel | hosts `a` | |
| w9 jeem | consonant | hosts `ʒ`, and the release `Q` beside it | the release is sughra, `qalqala_sughra` |
| w9 jeem | vowel | not applicable | |
| w9 ain | consonant | hosts `ʕ` | |
| w9 ain | vowel | hosts `a` | |
| w9 lam | consonant | merged into `ll`, by `idgham_mutamathilayn` | |
| w9 lam | vowel | not applicable | |
| w10 lam | consonant | hosts `ll`, by `idgham_mutamathilayn` | doubled |
| w10 lam | vowel | hosts `a` | |
| w10 heh | consonant | hosts `h` | |
| w10 heh | vowel | hosts `u:` | long, `madd_tabii`; labelled `silah` |
| w11 ain | consonant | hosts `ʕ` | |
| w11 ain | vowel | hosts `i` | |
| w11 waw | consonant | hosts `w` | |
| w11 waw | vowel | hosts `a` | |
| w11 jeem | consonant | hosts `ʒ` | |
| w11 jeem | vowel | hosts `a:` | long, `madd_tabii` |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| وَ | وَ | `w` `a` | | | |
| لَ | لَ | `l` `a` | | | |
| مْ | مْ | `m` | | | `izhar_shafawi` |
| يَ | يَ | `j` `a` | | | |
| جْ | جْ | `ʒ` `Q` | | | `qalqala_sughra` |
| عَ | عَ | `ʕ` `a` | | | |
| ل | | | `ll` | | `idgham_mutamathilayn` |
| لَّ | لَّ | `ll` `a` | | | `idgham_mutamathilayn` |
| هُۥ | هُو | `h` `u:` | | | `madd_tabii` |
| عِ | عِ | `ʕ` `i` | | | |
| وَ | وَ | `w` `a` | | | |
| جَ | جَ | `ʒ` | `a:` | | `madd_tabii` |
| اۜ | اۜ | `a:` | | | `madd_tabii` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - rules | account for the sakt mark | **FINDING.** It belongs to its word, so it is not structural and takes a pairing, and no spelling edge fits it: it supplies no fact, witnesses no unit and decorates none. Sakt is not a rule either, so a pairing naming nothing is the only reading left, and calling the mark silent instead would owe a rule it cannot name. `Word.sakt_after` is where the fact belongs |
| script - recited | read the merger's spelling | the merger costs one deletion and buys no insertion, so `rendered` is shorter by one glyph and the host's row is unchanged. One field read |
| the other four | | one call and one field read |

A merger's whole spelling is a deletion here, because the mushaf already wrote
the shadda the join would otherwise add. The mark that instructs the reciter
survives into the recited text and is the one glyph in the example that no
table says anything about.

### E11. The homorganic pair that does not merge

Plan A: `mappings("27:22:5-27:22:10")`, joined, stopping after word 10.

| word | source | recited | phonemes |
|---|---|---|---|
| 5 | أَحَطتُ | أَحَطتُ | `ʔ a ħ a tˤ t u` |
| 6 | بِمَا | بِمَا | `b i m a:` |
| 7 | لَمْ | لَمْ | `l a m` |
| 8 | تُحِطْ | تُحِطْ | `t u ħ i tˤ Q` |
| 9 | بِهِۦ | بِهِي | `b i h i:` |
| 10 | وَجِئْتُكَ | وَجِئْتُكْ | `w a ʒ i ʔ t u k` |

Plan B: `mappings("27:22:5-27:22:9")`, joined, stopping after word 9.

| word | source | recited | phonemes |
|---|---|---|---|
| 9 | بِهِۦ | بِهْ | `b i h` |

Word 5 is 4.7's unchanged case for the naqis, whose letters the recited text
writes exactly as the rasm does. Word 9 is row 27 under plan A; under plan B
row 1 takes the silah mark and the sukun that replaces its kasra is covered by
no row. Word 10 is row 19.

**Part 1, units and parts**, plan A.

| unit | part | realization | on the sound |
|---|---|---|---|
| w5 hamza | consonant | hosts `ʔ` | |
| w5 hamza | vowel | hosts `a` | |
| w5 ha | consonant | hosts `ħ` | |
| w5 ha | vowel | hosts `a` | |
| w5 tah | consonant | hosts `tˤ` | heavy, `tafkheem`; manner changed by `idgham_mutajanisayn_naqis` |
| w5 tah | vowel | not applicable | |
| w5 ta | consonant | hosts `t` | |
| w5 ta | vowel | hosts `u` | |
| w6 ba | consonant | hosts `b` | |
| w6 ba | vowel | hosts `i` | |
| w6 meem | consonant | hosts `m` | |
| w6 meem | vowel | hosts `a:` | long, `madd_tabii` |
| w7 lam | consonant | hosts `l` | |
| w7 lam | vowel | hosts `a` | |
| w7 meem | consonant | hosts `m` | named plain, `izhar_shafawi` |
| w7 meem | vowel | not applicable | |
| w8 ta | consonant | hosts `t` | |
| w8 ta | vowel | hosts `u` | |
| w8 ha | consonant | hosts `ħ` | |
| w8 ha | vowel | hosts `i` | |
| w8 tah | consonant | hosts `tˤ`, and the release `Q` beside it | heavy, `tafkheem`; the release is sughra, `qalqala_sughra` |
| w8 tah | vowel | not applicable | |
| w9 ba | consonant | hosts `b` | |
| w9 ba | vowel | hosts `i` | |
| w9 heh | consonant | hosts `h` | |
| w9 heh | vowel | hosts `i:` | long, `madd_tabii`; labelled `silah` |
| w10 waw | consonant | hosts `w` | |
| w10 waw | vowel | hosts `a` | |
| w10 jeem | consonant | hosts `ʒ` | |
| w10 jeem | vowel | hosts `i` | |
| w10 hamza | consonant | hosts `ʔ` | |
| w10 hamza | vowel | not applicable | |
| w10 ta | consonant | hosts `t` | |
| w10 ta | vowel | hosts `u` | |
| w10 kaf | consonant | hosts `k` | |
| w10 kaf | vowel | silent, `pausal_sukun` | |

**Part 1**, plan B, the rows that differ.

| unit | part | realization | on the sound |
|---|---|---|---|
| w9 heh | consonant | hosts `h` | |
| w9 heh | vowel | silent, `pausal_sukun` | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`, plan A.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| أَ | أَ | `ʔ` `a` | | | |
| حَ | حَ | `ħ` `a` | | | |
| ط | ط | `tˤ` | | | `idgham_mutajanisayn_naqis`, `tafkheem` |
| تُ | تُ | `t` `u` | | | |
| بِ | بِ | `b` `i` | | | |
| مَ | مَ | `m` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| لَ | لَ | `l` `a` | | | |
| مْ | مْ | `m` | | | `izhar_shafawi` |
| تُ | تُ | `t` `u` | | | |
| حِ | حِ | `ħ` `i` | | | |
| طْ | طْ | `tˤ` `Q` | | | `qalqala_sughra`, `tafkheem` |
| بِ | بِ | `b` `i` | | | |
| هِۦ | هِي | `h` `i:` | | | `madd_tabii` |
| وَ | وَ | `w` `a` | | | |
| جِ | جِ | `ʒ` `i` | | | |
| ئْ | ئْ | `ʔ` | | | |
| تُ | تُ | `t` `u` | | | |
| كَ | كْ | `k` | | ◌َ | `pausal_sukun` |

**Part 2**, plan B, the row that differs.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| هِۦ | هْ | `h` | | ◌ِ, ۦ | `pausal_sukun` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| sound - rules | reach what the naqis did | **FINDING.** It changes the tah's manner and nothing else, and no modifier says so: it does not recolour, it does not set a length, and naming the sound would assert that nothing changed. The instance reaches a sound it altered through no edge, and a consumer reading the sound sees an ordinary heavy tah |
| script - sound | ask which glyph of هِۦ owns the vowel | at `grouping="cluster"` they are one row and the question does not arise; at `grouping="glyph"` the ownership order gives `i:` to the small yeh, which supplies its length, and the kasra takes it in `shares`. One field read |
| script - recited | read هِۦ under each plan | one source cluster renders as هِي under A and as هْ under B, on the row of whichever document the consumer asked for. One field read, two documents |
| the other three | | one call and one field read |

An idgham with nothing shared and no host, beside a mark that owns a long vowel
under one request and is written and unsaid under the other. The package hosts
every release on the vowel part rather than the consonant, and it puts the
naqis rule's trigger in the tuple position a merger uses for its host.

### E12. A sound no unit owns, and a release a merger consumes

`mappings("11:42:7-11:42:15")`, joined, stopping after word 15.

| word | source | recited | phonemes |
|---|---|---|---|
| 7 | وَنَادَىٰ | وَنَادَا | `w a n a: d a:` |
| 8 | نُوحٌ | نُوحُنِ | `n u: ħ u n` |
| 9 | ٱبْنَهُۥ | بْنَهُو | `b Q n a h u:` |
| 10 | وَكَانَ | وَكَانَ | `w a k a: n a` |
| 11 | فِى | فِى | `f i:` |
| 12 | مَعْزِلٍ | مَعْزِلِ | `m a ʕ z i l i` |
| 13 | يَـٰبُنَىَّ | يَّابُنَىَّ | `j̃ a: b u n a jj a` |
| 14 | ٱرْكَب | رْكَ | `rˤ k a` |
| 15 | مَّعَنَا | مَّعَنَا | `mm a ʕ a n a:` |

Word 8 is 4.1a's `iltiqa_kasra` line, the haraka then a noon with a kasra, and
row 14 writes the kasra itself. Word 13 takes rows 11, 18 and 26 together, and
word 14 rows 6 and 7.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w7 waw | consonant | hosts `w` | |
| w7 waw | vowel | hosts `a` | |
| w7 noon | consonant | hosts `n` | |
| w7 noon | vowel | hosts `a:` | long, `madd_tabii` |
| w7 dal | consonant | hosts `d` | |
| w7 dal | vowel | hosts `a:` | long, `madd_tabii` |
| w8 noon | consonant | hosts `n` | |
| w8 noon | vowel | hosts `u:` | long, `madd_tabii` |
| w8 ha | consonant | hosts `ħ` | |
| w8 ha | vowel | hosts `u` | |
| w8 noon (tanween) | consonant | hosts `n` | |
| w8 noon (tanween) | vowel | not applicable | |
| w9 hamza | consonant | silent, `hamza_wasl_elision` | |
| w9 hamza | vowel | silent, `hamza_wasl_elision` | |
| w9 ba | consonant | hosts `b`, and the release `Q` beside it | the release is sughra, `qalqala_sughra` |
| w9 ba | vowel | not applicable | |
| w9 noon | consonant | hosts `n` | |
| w9 noon | vowel | hosts `a` | |
| w9 heh | consonant | hosts `h` | |
| w9 heh | vowel | hosts `u:` | long, `madd_tabii`; labelled `silah` |
| w10 waw | consonant | hosts `w` | |
| w10 waw | vowel | hosts `a` | |
| w10 kaf | consonant | hosts `k` | |
| w10 kaf | vowel | hosts `a:` | long, `madd_tabii` |
| w10 noon | consonant | hosts `n` | |
| w10 noon | vowel | hosts `a` | |
| w11 fa | consonant | hosts `f` | |
| w11 fa | vowel | hosts `i:` | long, `madd_tabii` |
| w12 meem | consonant | hosts `m` | |
| w12 meem | vowel | hosts `a` | |
| w12 ain | consonant | hosts `ʕ` | |
| w12 ain | vowel | not applicable | |
| w12 zay | consonant | hosts `z` | |
| w12 zay | vowel | hosts `i` | |
| w12 lam | consonant | hosts `l` | |
| w12 lam | vowel | hosts `i` | |
| w12 noon (tanween) | consonant | merged into `j̃`, by `idgham_bi_ghunnah` | |
| w12 noon (tanween) | vowel | not applicable | |
| w13 ya | consonant | hosts `j̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w13 ya | vowel | hosts `a:` | long, `madd_tabii` |
| w13 ba | consonant | hosts `b` | |
| w13 ba | vowel | hosts `u` | |
| w13 noon | consonant | hosts `n` | |
| w13 noon | vowel | hosts `a` | |
| w13 ya | consonant | hosts `jj` | doubled |
| w13 ya | vowel | hosts `a` | |
| w14 hamza | consonant | silent, `hamza_wasl_elision` | |
| w14 hamza | vowel | silent, `hamza_wasl_elision` | |
| w14 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w14 ra | vowel | not applicable | |
| w14 kaf | consonant | hosts `k` | |
| w14 kaf | vowel | hosts `a` | |
| w14 ba | consonant | merged into `mm`, by `idgham_mutajanisayn_kamil` | |
| w14 ba | vowel | not applicable | |
| w15 meem | consonant | hosts `mm`, by `idgham_mutajanisayn_kamil` | doubled |
| w15 meem | vowel | hosts `a` | |
| w15 ain | consonant | hosts `ʕ` | |
| w15 ain | vowel | hosts `a` | |
| w15 noon | consonant | hosts `n` | |
| w15 noon | vowel | hosts `a:` | long, `madd_tabii` |

The helping kasra belongs to no unit, so it has no row above: `iltiqa_kasra`
anchors it on the tanween's noon and it is the one sound in the design that no
unit owns. No nasal rule fires on that noon either, because the helping vowel
takes it and a voweled noon has nothing to hide or merge.

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| وَ | وَ | `w` `a` | | | |
| نَ | نَ | `n` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| دَ | دَ | `d` | `a:` | | `madd_tabii` |
| ىٰ | ا | `a:` | | | `madd_tabii` |
| نُ | نُ | `n` | `u:` | | `madd_tabii` |
| و | و | `u:` | | | `madd_tabii` |
| حٌ | حُن | `ħ` `u` `n` | | | `iltiqa_kasra` |
| (gap, after حٌ) | ◌ِ | the helping kasra | | | `iltiqa_kasra` |
| ٱ | | | | ٱ | `hamza_wasl_elision` |
| بْ | بْ | `b` `Q` | | | `qalqala_sughra` |
| نَ | نَ | `n` `a` | | | |
| هُۥ | هُو | `h` `u:` | | | `madd_tabii` |
| وَ | وَ | `w` `a` | | | |
| كَ | كَ | `k` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| نَ | نَ | `n` `a` | | | |
| فِ | فِ | `f` | `i:` | | `madd_tabii` |
| ى | ى | `i:` | | | `madd_tabii` |
| مَ | مَ | `m` `a` | | | |
| عْ | عْ | `ʕ` | | | |
| زِ | زِ | `z` `i` | | | |
| لٍ | لِ | `l` `i` | `j̃` | | `idgham_bi_ghunnah` |
| يَٰ | يَّا | `j̃` `a:` | | | `idgham_bi_ghunnah`, `madd_tabii` |
| بُ | بُ | `b` `u` | | | |
| نَ | نَ | `n` `a` | | | |
| ىَّ | ىَّ | `jj` `a` | | | |
| ٱ | | | | ٱ | `hamza_wasl_elision` |
| رْ | رْ | `rˤ` | | | `tafkheem` |
| كَ | كَ | `k` `a` | | | |
| ب | | | `mm` | | `idgham_mutajanisayn_kamil` |
| مَّ | مَّ | `mm` `a` | | | `idgham_mutajanisayn_kamil` |
| عَ | عَ | `ʕ` `a` | | | |
| نَ | نَ | `n` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |

The ninth row is the gap pairing, `after` naming the cluster حٌ. The tanween
mark writes the haraka and the noon, and the kasra beside them is the
insertion's own glyph, which is why row 14 writes a letter and not only a mark.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - sound | place the helping vowel | one sound, two row identities: under `text="source"` it is a gap pairing and the consumer reads `after` to place it, under `text="recited"` it is an ordinary row on the kasra, and a consumer holding both texts at once cannot key it on either |
| sound - rules | ask what the baa does | one letter and one rule twice over: the baa of ٱبْنَهُۥ carries a release and the baa of ٱرْكَب carries a merger that consumed the closure, so `rules` gives different answers for the same letter in one request |
| script - rules | colour the merger of مَعْزِلٍ | the kasratan shows the lam's vowel and the noon's merger on one scalar, so the merger colours a mark the merged letter does not have. One field read, two units |
| script - recited | say why ٱرْكَب lost two glyphs | only `silent` beside `rules` separates the elision from the merger. Comparing the arrays says one thing was lost and does not say which |
| the other two | | one call and one field read |

The one insertion in the design and the one release a merger eats sit in the
same passage, and the same letter fires and does not fire on one page. The
package builds no insertion, so its output puts the tanween noon straight
against the sakin baa and classifies it against a wasl hamza it then elides;
the dagger alif of وَنَادَىٰ reaches no unit while the alif maqsura under it
carries the vowel.

### E13. The hum at the lips, the heavy hum, and the heavy lam

Plan A: `mappings("2:27:2-2:27:8")`, joined throughout, stopping after word 8.

| word | source | recited | phonemes |
|---|---|---|---|
| 2 | يَنقُضُونَ | يَنقُضُونَ | `j a ŋ q u dˤ u: n a` |
| 3 | عَهْدَ | عَهْدَ | `ʕ a h d a` |
| 4 | ٱللَّهِ | لَّاهِ | `lˤlˤ aˤ: h i` |
| 5 | مِن | مِن | `m i ŋ` |
| 6 | بَعْدِ | بَعْدِ | `b a ʕ d i` |
| 7 | مِيثَـٰقِهِۦ | مِيثَاقِهِي | `m i: θ a: q i h i:` |
| 8 | وَيَقْطَعُونَ | وَيَقْطَعُونْ | `w a j a q Q tˤ aˤ ʕ u: n` |

Plan B: `mappings("2:27:2-2:27:7")`, joined throughout, stopping after word 7.

| word | source | recited | phonemes |
|---|---|---|---|
| 7 | مِيثَـٰقِهِۦ | مِيثَاقِهْ | `m i: θ a: q i h` |

Word 4 is rows 6, 8 and 16: the wasl seat goes, the article lam goes, and the
long a the rasm has no carrier for is written. Word 5 is 4.7's unchanged case
for a joined iqlab. Word 7 is row 26 on the dagger and row 27 on the silah mark
under plan A; under plan B row 1 takes the mark and the sukun that replaces its
kasra is covered by no row. Word 8 is row 19.

**Part 1, units and parts**, plan A.

| unit | part | realization | on the sound |
|---|---|---|---|
| w2 ya | consonant | hosts `j` | |
| w2 ya | vowel | hosts `a` | |
| w2 noon | consonant | hosts `ŋ`, by `ikhfaa_haqiqi` | a hum, not doubled; heavy, `ikhfaa_haqiqi` |
| w2 noon | vowel | not applicable | |
| w2 qaf | consonant | hosts `q` | heavy, `tafkheem` |
| w2 qaf | vowel | hosts `u` | |
| w2 dad | consonant | hosts `dˤ` | heavy, `tafkheem` |
| w2 dad | vowel | hosts `u:` | long, `madd_tabii` |
| w2 noon | consonant | hosts `n` | |
| w2 noon | vowel | hosts `a` | |
| w3 ain | consonant | hosts `ʕ` | |
| w3 ain | vowel | hosts `a` | |
| w3 heh | consonant | hosts `h` | |
| w3 heh | vowel | not applicable | |
| w3 dal | consonant | hosts `d` | |
| w3 dal | vowel | hosts `a` | |
| w4 hamza | consonant | silent, `hamza_wasl_elision` | |
| w4 hamza | vowel | silent, `hamza_wasl_elision` | |
| w4 lam | consonant | merged into `lˤlˤ`, by `lam_shamsiyyah` | |
| w4 lam | vowel | not applicable | |
| w4 lam | consonant | hosts `lˤlˤ`, by `lam_shamsiyyah` | doubled; heavy, `tafkheem` |
| w4 lam | vowel | hosts `aˤ:` | long, `madd_tabii`; heavy, `tafkheem` |
| w4 heh | consonant | hosts `h` | |
| w4 heh | vowel | hosts `i` | |
| w5 meem | consonant | hosts `m` | |
| w5 meem | vowel | hosts `i` | |
| w5 noon | consonant | hosts `ŋ`, by `iqlab` | a hum, not doubled |
| w5 noon | vowel | not applicable | |
| w6 ba | consonant | hosts `b` | |
| w6 ba | vowel | hosts `a` | |
| w6 ain | consonant | hosts `ʕ` | |
| w6 ain | vowel | not applicable | |
| w6 dal | consonant | hosts `d` | |
| w6 dal | vowel | hosts `i` | |
| w7 meem | consonant | hosts `m` | |
| w7 meem | vowel | hosts `i:` | long, `madd_tabii` |
| w7 tha | consonant | hosts `θ` | |
| w7 tha | vowel | hosts `a:` | long, `madd_tabii` |
| w7 qaf | consonant | hosts `q` | heavy, `tafkheem` |
| w7 qaf | vowel | hosts `i` | |
| w7 heh | consonant | hosts `h` | |
| w7 heh | vowel | hosts `i:` | long, `madd_tabii`; labelled `silah` |
| w8 waw | consonant | hosts `w` | |
| w8 waw | vowel | hosts `a` | |
| w8 ya | consonant | hosts `j` | |
| w8 ya | vowel | hosts `a` | |
| w8 qaf | consonant | hosts `q`, and the release `Q` beside it | heavy, `tafkheem`; the release is sughra, `qalqala_sughra` |
| w8 qaf | vowel | not applicable | |
| w8 tah | consonant | hosts `tˤ` | heavy, `tafkheem` |
| w8 tah | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w8 ain | consonant | hosts `ʕ` | |
| w8 ain | vowel | hosts `u:` | long, `madd_arid_lil_sukun` |
| w8 noon | consonant | hosts `n` | |
| w8 noon | vowel | silent, `pausal_sukun` | |

Only an `a` has a heavy form, so the qaf of يَنقُضُونَ is heavy and the damma
it carries is not; the lam of ٱللَّهِ and the tah of وَيَقْطَعُونَ are the two
units here whose vowel the colour reaches.

**Part 1**, plan B, the rows that differ.

| unit | part | realization | on the sound |
|---|---|---|---|
| w7 heh | vowel | silent, `pausal_sukun` | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`, plan A.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| يَ | يَ | `j` `a` | | | |
| ن | ن | `ŋ` | | | `ikhfaa_haqiqi` |
| قُ | قُ | `q` `u` | | | `tafkheem` |
| ضُ | ضُ | `dˤ` | `u:` | | `tafkheem`, `madd_tabii` |
| و | و | `u:` | | | `madd_tabii` |
| نَ | نَ | `n` `a` | | | |
| عَ | عَ | `ʕ` `a` | | | |
| هْ | هْ | `h` | | | |
| دَ | دَ | `d` `a` | | | |
| ٱ | | | | ٱ | `hamza_wasl_elision` |
| ل | | | `lˤlˤ` | | `lam_shamsiyyah` |
| لَّ | لَّ | `lˤlˤ` `aˤ:` | | | `lam_shamsiyyah`, `tafkheem`, `madd_tabii` |
| هِ | هِ | `h` `i` | | | |
| مِ | مِ | `m` `i` | | | |
| ن | ن | `ŋ` | | | `iqlab` |
| بَ | بَ | `b` `a` | | | |
| عْ | عْ | `ʕ` | | | |
| دِ | دِ | `d` `i` | | | |
| مِ | مِ | `m` | `i:` | | `madd_tabii` |
| ي | ي | `i:` | | | `madd_tabii` |
| ثَٰ | ثَا | `θ` `a:` | | | `madd_tabii` |
| قِ | قِ | `q` `i` | | | `tafkheem` |
| هِۦ | هِي | `h` `i:` | | | `madd_tabii` |
| وَ | وَ | `w` `a` | | | |
| يَ | يَ | `j` `a` | | | |
| قْ | قْ | `q` `Q` | | | `tafkheem`, `qalqala_sughra` |
| طَ | طَ | `tˤ` `aˤ` | | | `tafkheem` |
| عُ | عُ | `ʕ` | `u:` | | `madd_arid_lil_sukun` |
| و | و | `u:` | | | `madd_arid_lil_sukun` |
| نَ | نْ | `n` | | ◌َ | `pausal_sukun` |

**Part 2**, plan B, the row that differs.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| هِۦ | هْ | `h` | | ◌ِ, ۦ | `pausal_sukun` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - recited | list every glyph the recited text drops | **FINDING.** `rendered` is empty for ٱ and for ل, and only ٱ is in `silent`: a merged lam shows the geminate through `shares`, so it is neither a `Silent` attribution nor a glyph showing no sound. No one list holds both, and the catalogue's "dropped" row says otherwise |
| script - recited | draw the recited word لَّاهِ | **FINDING**, the one E4 records. The alif written for a length the rasm has no carrier for names no source glyph and sits in no source row's `rendered`, so the source rows concatenate to a text one character short of what recitation says |
| script - recited | draw مِيثَاقِهْ under plan B | **FINDING.** Row 2 removes ۦ, and the kasra becoming a sukun is covered by no row: row 19 wants a vowel short in its joined form, row 20 a nunation, row 21 a fathatan, row 12 a bare consonant |
| sound - rules | highlight the geminate | one call and two rows: `lˤlˤ` is owned in the second lam and the instance names the first as its `source`, so the highlight reads one row through `sounds` and one through `shares` |
| script - sound, script - rules | read any other row | one call and one field read, except that ٱ and ل both own nothing, and only `silent` read against `shares` separates an elision from a merger |
| the other two | | one call and one field read |

Two hums, one token. The tables carry the heavy ghunnah the converse law asks
of an ikhfaa before an istilaa letter, and the iqlab's hum is said at the lips
while the published sound has nowhere to say so, which leaves gemination and
weight as the whole of what tells one hum from another. The passage settles
that a rule looking like a merger and a rule that is one part on `host`, not on
the shape of the recited word.

### E14. A length the stop reverts, and a length the join shortens

Plan A: `mappings("2:27:12-2:27:17")`, joined throughout, stopping after word
17.

| word | source | recited | phonemes |
|---|---|---|---|
| 12 | بِهِۦٓ | بِهِيٓ | `b i h i:` |
| 13 | أَن | أَ | `ʔ a` |
| 14 | يُوصَلَ | يُّوصَلَ | `j̃ u: sˤ aˤ l a` |
| 15 | وَيُفْسِدُونَ | وَيُفْسِدُونَ | `w a j u f s i d u: n a` |
| 16 | فِى | فِ | `f i` |
| 17 | ٱلْأَرْضِ ۚ | لْأَرْضْ ۚ | `l ʔ a rˤ dˤ` |

Plan B: `mappings("2:27:12")`, one word, stopped.

| word | source | recited | phonemes |
|---|---|---|---|
| 12 | بِهِۦٓ | بِهْ | `b i h` |

Word 12 is row 27 under plan A; under plan B rows 1 and 2 take the mark and its
maddah together, and the sukun that replaces its kasra is covered by no row.
Word 13's noon goes by row 7 and
word 14 takes the shadda row 18 adds. Word 16 loses its carrier to row 10, word
17 its wasl seat to row 6, and the stop sign is row 30.

**Part 1, units and parts**, plan A.

| unit | part | realization | on the sound |
|---|---|---|---|
| w12 ba | consonant | hosts `b` | |
| w12 ba | vowel | hosts `i` | |
| w12 heh | consonant | hosts `h` | |
| w12 heh | vowel | hosts `i:` | long, `madd_jaiz_munfasil`; labelled `silah`, `silah_kubra` |
| w13 hamza | consonant | hosts `ʔ` | |
| w13 hamza | vowel | hosts `a` | |
| w13 noon | consonant | merged into `j̃`, by `idgham_bi_ghunnah` | |
| w13 noon | vowel | not applicable | |
| w14 ya | consonant | hosts `j̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w14 ya | vowel | hosts `u:` | long, `madd_tabii` |
| w14 sad | consonant | hosts `sˤ` | heavy, `tafkheem` |
| w14 sad | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w14 lam | consonant | hosts `l` | |
| w14 lam | vowel | hosts `a` | |
| w15 waw | consonant | hosts `w` | |
| w15 waw | vowel | hosts `a` | |
| w15 ya | consonant | hosts `j` | |
| w15 ya | vowel | hosts `u` | |
| w15 fa | consonant | hosts `f` | |
| w15 fa | vowel | not applicable | |
| w15 seen | consonant | hosts `s` | |
| w15 seen | vowel | hosts `i` | |
| w15 dal | consonant | hosts `d` | |
| w15 dal | vowel | hosts `u:` | long, `madd_tabii` |
| w15 noon | consonant | hosts `n` | |
| w15 noon | vowel | hosts `a` | |
| w16 fa | consonant | hosts `f` | |
| w16 fa | vowel | hosts `i` | short, `iltiqa_shortening` |
| w17 hamza | consonant | silent, `hamza_wasl_elision` | |
| w17 hamza | vowel | silent, `hamza_wasl_elision` | |
| w17 lam | consonant | hosts `l` | named plain, `lam_qamariyyah` |
| w17 lam | vowel | not applicable | |
| w17 hamza | consonant | hosts `ʔ` | |
| w17 hamza | vowel | hosts `a` | |
| w17 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w17 ra | vowel | not applicable | |
| w17 dad | consonant | hosts `dˤ` | heavy, `tafkheem` |
| w17 dad | vowel | silent, `pausal_sukun` | |

**Part 1**, plan B, the rows that differ.

| unit | part | realization | on the sound |
|---|---|---|---|
| w12 heh | vowel | silent, `pausal_sukun` | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`, plan A.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| بِ | بِ | `b` `i` | | | |
| هِۦٓ | هِيٓ | `h` `i:` | | | `madd_jaiz_munfasil` |
| أَ | أَ | `ʔ` `a` | | | |
| ن | | | `j̃` | | `idgham_bi_ghunnah` |
| يُ | يُّ | `j̃` | `u:` | | `idgham_bi_ghunnah`, `madd_tabii` |
| و | و | `u:` | | | `madd_tabii` |
| صَ | صَ | `sˤ` `aˤ` | | | `tafkheem` |
| لَ | لَ | `l` `a` | | | |
| وَ | وَ | `w` `a` | | | |
| يُ | يُ | `j` `u` | | | |
| فْ | فْ | `f` | | | |
| سِ | سِ | `s` `i` | | | |
| دُ | دُ | `d` | `u:` | | `madd_tabii` |
| و | و | `u:` | | | `madd_tabii` |
| نَ | نَ | `n` `a` | | | |
| فِ | فِ | `f` `i` | | | `iltiqa_shortening` |
| ى | | | | ى | `iltiqa_shortening` |
| ٱ | | | | ٱ | `hamza_wasl_elision` |
| لْ | لْ | `l` | | | `lam_qamariyyah` |
| أَ | أَ | `ʔ` `a` | | | |
| رْ | رْ | `rˤ` | | | `tafkheem` |
| ضِ | ضْ | `dˤ` | | ◌ِ | `tafkheem`, `pausal_sukun` |

The stop sign ۚ carries the `Structural` edge, takes no pairing, and is kept in
`rendered`.

**Part 2**, plan B.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| بِ | بِ | `b` `i` | | | |
| هِۦٓ | هْ | `h` | | ◌ِ, ۦ, ◌ٓ | `pausal_sukun` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| sound - rules | ask فِى for its madd rule | **FINDING.** The converse law asks a canonically long vowel for a madd rule instance, and the only Length rule naming this one is `iltiqa_shortening`, which took the length away |
| script - sound | ask why the fa's vowel is short | the ى owns nothing and is `silent`, and that the vowel is canonically long is on the length edge of the sound and nowhere on either glyph, so the question takes a row read and an edge read |
| script - recited | draw بِهِۦٓ stopped | rows 1 and 2 remove the mark and its maddah together, and the maddah is a glyph that presented a sound it supplied no fact for. One field read |
| the other three | | one call and one field read |

The maddah goes with the plan and the carrier goes with the join, and neither
change is a property of the glyph kind: the same `madd_sign` over a
`madd_wajib_muttasil` survives every plan. The package puts a
`madd_jaiz_munfasil` on فِى as well; its trigger is the hamza that begins
ٱلْأَرْضِ, which is a wasl hamza and elides, so no rule of that name is on the
tables.

### E15. An alif the rasm does not have

`mappings("2:22:10-2:22:11")`, started on ٱلسَّمَآءِ, which is where the
request begins, joined, stopping after word 11.

| word | source | recited | phonemes |
|---|---|---|---|
| 10 | ٱلسَّمَآءِ | أَسَّمَآءِ | `ʔ a ss a m a: ʔ i` |
| 11 | مَآءً | مَآءَا | `m a: ʔ a:` |

Word 10 is rows 24 and 13 on the wasl seat and row 8 on the article lam. Word
11's fathatan becomes a fatha and an alif is written where the rasm has no seat
for it to lengthen, which is row 15 beside row 21.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w10 hamza | consonant | hosts `ʔ`, by `hamza_wasl_start` | |
| w10 hamza | vowel | hosts `a`, by `hamza_wasl_start` | |
| w10 lam | consonant | merged into `ss`, by `lam_shamsiyyah` | |
| w10 lam | vowel | not applicable | |
| w10 seen | consonant | hosts `ss`, by `lam_shamsiyyah` | doubled |
| w10 seen | vowel | hosts `a` | |
| w10 meem | consonant | hosts `m` | |
| w10 meem | vowel | hosts `a:` | long, `madd_wajib_muttasil` |
| w10 hamza | consonant | hosts `ʔ` | |
| w10 hamza | vowel | hosts `i` | |
| w11 meem | consonant | hosts `m` | |
| w11 meem | vowel | hosts `a:` | long, `madd_wajib_muttasil` |
| w11 hamza | consonant | hosts `ʔ` | |
| w11 hamza | vowel | hosts `a:` | long, `madd_tabii`; labelled `madd_iwad` |
| w11 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w11 noon (tanween) | vowel | not applicable | |

**Part 2, pairings**, `text="recited"`, `grouping="glyph"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| ٱ | أ | `ʔ` | | | `hamza_wasl_start` |
| | ◌َ | `a` | | | `hamza_wasl_start` |
| س | س | `ss` | | | `lam_shamsiyyah` |
| ◌ّ | ◌ّ | | `ss` | | `lam_shamsiyyah` |
| ◌َ | ◌َ | `a` | | | |
| م | م | `m` | | | |
| ◌َ | ◌َ | | `a:` | | `madd_wajib_muttasil` |
| ا | ا | `a:` | | | `madd_wajib_muttasil` |
| ◌ٓ | ◌ٓ | | `a:` | | `madd_wajib_muttasil` |
| ء | ء | `ʔ` | | | |
| ◌ِ | ◌ِ | `i` | | | |
| م | م | `m` | | | |
| ◌َ | ◌َ | | `a:` | | `madd_wajib_muttasil` |
| ا | ا | `a:` | | | `madd_wajib_muttasil` |
| ◌ٓ | ◌ٓ | | `a:` | | `madd_wajib_muttasil` |
| ء | ء | `ʔ` | | | |
| ◌ً | ◌َ | | `a:` | | `pausal_sukun`, `madd_tabii` |
| | ا | `a:` | | | `madd_tabii` |

The space between the two words is kept and carries the `Structural` edge, so
it takes no pairing. The last alif and the helping fatha have an empty source
cell, which is what an insertion is; the lam of ٱلسَّمَآءِ has no row at all.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - sound | ask what the merged lam sounds like | not answerable from this quadrant. The lam is written and not recited, so it has no rendered glyph and no row here; the source quadrants are where it is |
| script - recited | read the fathatan's two rendered rows | the fatha it becomes and the alif that was never written. Row 23 names a written seat this word does not have and row 15 is the one that supplies the alif, so the substitution is stated by neither alone |
| the other four | | one call and one field read on every row. No sound takes a gap pairing, and the two insertions are ordinary rows with an empty source cell rather than a second array |

The quadrant settles which array a colouring consumer should be reading: on the
recited side every sound has a glyph and every glyph a row, and the price is
that the letter a rule removed has nothing left to colour.

### E16. The letter said only at a pause

Plan A: `mappings("76:15:8-76:16:1")`, joined across the verse boundary,
stopping after the second word.

| word | source | recited | phonemes |
|---|---|---|---|
| 76:15:8 | قَوَارِيرَا۠ | قَوَارِيرَ | `q aˤ w a: r i: rˤ aˤ:` |
| 76:16:1 | قَوَارِيرَا۟ | قَوَارِيرْ | `q aˤ w a: r i: r` |

Plan B: the same request with `stops=("76:15:8",)`, so the second word is
started on.

| word | source | recited | phonemes |
|---|---|---|---|
| 76:15:8 | قَوَارِيرَا۠ | قَوَارِيرَا | `q aˤ w a: r i: rˤ aˤ:` |

The two plans print one phoneme string. The recited spellings above and the
tables below state the vowel's two forms, which is where the plans part: the
first word's final vowel is short in its joined form and long in its stopped
form, so its seat is row 4; the second word's is short in both, so nothing but
the stop takes it and its seat is row 3. Both silence signs are row 5. This is
the one place where the tables and the phoneme line disagree: the package gives
the long form under both plans, and the tables state the reading the contract's
correction to the seven alifs requires.

**Part 1, units and parts**, 76:15:8 under plan A. Words are numbered within
their own verse.

| unit | part | realization | on the sound |
|---|---|---|---|
| w8 qaf | consonant | hosts `q` | heavy, `tafkheem` |
| w8 qaf | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w8 waw | consonant | hosts `w` | |
| w8 waw | vowel | hosts `a:` | long, `madd_tabii` |
| w8 ra | consonant | hosts `r` | named light, `tarqeeq` |
| w8 ra | vowel | hosts `i:` | long, `madd_tabii` |
| w8 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w8 ra | vowel | hosts `aˤ` | heavy, `tafkheem` |

Under plan B the last vowel hosts `aˤ:`, long by `madd_tabii` and heavy by
`tafkheem`.

**Part 1**, 76:16:1, the same under both plans.

| unit | part | realization | on the sound |
|---|---|---|---|
| w1 qaf | consonant | hosts `q` | heavy, `tafkheem` |
| w1 qaf | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w1 waw | consonant | hosts `w` | |
| w1 waw | vowel | hosts `a:` | long, `madd_tabii` |
| w1 ra | consonant | hosts `r` | named light, `tarqeeq` |
| w1 ra | vowel | hosts `i:` | long, `madd_arid_lil_sukun` |
| w1 ra | consonant | hosts `r` | named light, `tarqeeq` |
| w1 ra | vowel | silent, `pausal_sukun` | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`. The first three
clusters are the same word for word, plan for plan.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| قَ | قَ | `q` `aˤ` | | | `tafkheem` |
| وَ | وَ | `w` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |

**Part 2**, 76:15:8, the last four clusters under plan A.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| رِ | رِ | `r` | `i:` | | `tarqeeq`, `madd_tabii` |
| ي | ي | `i:` | | | `madd_tabii` |
| رَ | رَ | `rˤ` `aˤ` | | | `tafkheem` |
| ا۠ | | | | ا, ◌۠ | `orthographic_silence` |

The same word under plan B, where the last two clusters change.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| رَ | رَ | `rˤ` | `aˤ:` | | `tafkheem`, `madd_tabii` |
| ا۠ | ا | `aˤ:` | | ◌۠ | `madd_tabii` |

**Part 2**, 76:16:1, the last four clusters, the same under both plans. The
word is stopped on under both, so the long `i:` is a length the stop caused and
not the plain one the same five letters carry in the verse before.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| رِ | رِ | `r` | `i:` | | `tarqeeq`, `madd_arid_lil_sukun` |
| ي | ي | `i:` | | | `madd_arid_lil_sukun` |
| رَ | رْ | `r` | | ◌َ | `tarqeeq`, `pausal_sukun` |
| ا۟ | | | | ا, ◌۟ | `orthographic_silence` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - rules | attribute the silence signs | **FINDING.** Both are written and not said under every plan, and row 5 drops them with no owner. Where the seat beside the sign is silent too, the pairing names `orthographic_silence` and the law that every silence names a rule is met by the seat's instance; on the stopped 76:15:8 the alif sounds, the sign alone is silent, and the pairing's rules name only a madd |
| identity | tell the two requests apart | **FINDING.** They differ only in the junction after 76:15:8 and the package prints one phoneme string for both, so a consumer reading `phonemes` alone cannot separate them |
| script - sound | ask an alif what it sounds like | one call and one field read, and the answer is what the character cannot give: two alifs with the same neighbours and the same harakat, one owning a long vowel at a pause and one owning nothing under any plan |
| sound - rules | reach `orthographic_silence` | one call and one field read. It owns no attribution in either word, so it is reached only through the seat's pairing |
| the other three | | one call and one field read |

The two words settle that the boundary belongs on the unit's vowel and not on
the letter: same letters, same harakat, opposite behaviour, and only the sign
written above them separates the two, across a verse boundary in one index
space.

### E17. A glyph that spells a whole name

Plan A: `mappings("27:1")`, joined throughout, stopping after word 6.

| word | source | recited | phonemes |
|---|---|---|---|
| 1 | طسٓ ۚ | طَا سِيٓن ۚ | `tˤ aˤ: s i: ŋ` |
| 2 | تِلْكَ | تِلْكَ | `t i l k a` |
| 3 | ءَايَـٰتُ | ءَايَاتُ | `ʔ a: j a: t u` |
| 4 | ٱلْقُرْءَانِ | لْقُرْءَانِ | `l q u rˤ ʔ a: n i` |
| 5 | وَكِتَابٍ | وَكِتَابِ | `w a k i t a: b i` |
| 6 | مُّبِينٍ | مُّبِينْ | `m̃ u b i: n` |

Plan B: `mappings("27:1", stops=("27:1:3",))`, the same with a stop after word
3, so word 4 is started on.

| word | source | recited | phonemes |
|---|---|---|---|
| 3 | ءَايَـٰتُ | ءَايَاتْ | `ʔ a: j a: t` |
| 4 | ٱلْقُرْءَانِ | أَلْقُرْءَانِ | `ʔ a l q u rˤ ʔ a: n i` |

Word 1 is one glyph per letter name, so row 25 spells it as two names with a
space between them; the noon of `seen` is left bare because an assimilation
follows. Word 5's kasratan is 4.1a's idgham line and word 6 already carries the
shadda the host needs, so row 18 adds nothing; word 6 is row 20.

**Part 1, units and parts.** Plan A, with the plan B reading where it differs.

| unit | part | realization | on the sound |
|---|---|---|---|
| w1 tah (spelled) | consonant | hosts `tˤ` | heavy, `tafkheem` |
| w1 tah (spelled) | vowel | hosts `aˤ:` | heavy, `tafkheem`; long, `madd_tabii` |
| w1 seen (spelled) | consonant | hosts `s` | |
| w1 seen (spelled) | vowel | hosts `i:` | long, `madd_lazim` |
| w1 noon (spelled) | consonant | hosts `ŋ`, by `ikhfaa_haqiqi` | a hum, not doubled |
| w1 noon (spelled) | vowel | not applicable | |
| w2 ta | consonant | hosts `t` | |
| w2 ta | vowel | hosts `i` | |
| w2 lam | consonant | hosts `l` | |
| w2 lam | vowel | not applicable | |
| w2 kaf | consonant | hosts `k` | |
| w2 kaf | vowel | hosts `a` | |
| w3 hamza | consonant | hosts `ʔ` | |
| w3 hamza | vowel | hosts `a:` | long, `madd_tabii`; labelled `madd_badal` |
| w3 ya | consonant | hosts `j` | |
| w3 ya | vowel | hosts `a:` | long, `madd_tabii`; `madd_arid_lil_sukun` under B |
| w3 ta | consonant | hosts `t` | |
| w3 ta | vowel | hosts `u`; silent, `pausal_sukun`, under B | |
| w4 hamza | consonant | silent, `hamza_wasl_elision`; hosts `ʔ`, by `hamza_wasl_start`, under B | |
| w4 hamza | vowel | silent, `hamza_wasl_elision`; hosts `a`, by `hamza_wasl_start`, under B | |
| w4 lam | consonant | hosts `l` | named plain, `lam_qamariyyah` |
| w4 lam | vowel | not applicable | |
| w4 qaf | consonant | hosts `q` | heavy, `tafkheem` |
| w4 qaf | vowel | hosts `u` | |
| w4 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w4 ra | vowel | not applicable | |
| w4 hamza | consonant | hosts `ʔ` | |
| w4 hamza | vowel | hosts `a:` | long, `madd_tabii`; labelled `madd_badal` |
| w4 noon | consonant | hosts `n` | |
| w4 noon | vowel | hosts `i` | |
| w5 waw | consonant | hosts `w` | |
| w5 waw | vowel | hosts `a` | |
| w5 kaf | consonant | hosts `k` | |
| w5 kaf | vowel | hosts `i` | |
| w5 ta | consonant | hosts `t` | |
| w5 ta | vowel | hosts `a:` | long, `madd_tabii` |
| w5 ba | consonant | hosts `b` | |
| w5 ba | vowel | hosts `i` | |
| w5 noon (tanween) | consonant | merged into `m̃`, by `idgham_bi_ghunnah` | |
| w5 noon (tanween) | vowel | not applicable | |
| w6 meem | consonant | hosts `m̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w6 meem | vowel | hosts `u` | |
| w6 ba | consonant | hosts `b` | |
| w6 ba | vowel | hosts `i:` | long, `madd_tabii` |
| w6 noon | consonant | hosts `n` | |
| w6 noon | vowel | silent, `pausal_sukun` | |
| w6 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w6 noon (tanween) | vowel | not applicable | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`, plan A.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| ط | طَا | `tˤ` `aˤ:` | | | `tafkheem`, `madd_tabii` |
| سٓ | سِيٓن | `s` `i:` `ŋ` | | | `madd_lazim`, `ikhfaa_haqiqi` |
| تِ | تِ | `t` `i` | | | |
| لْ | لْ | `l` | | | |
| كَ | كَ | `k` `a` | | | |
| ءَ | ءَ | `ʔ` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| يَٰ | يَا | `j` `a:` | | | `madd_tabii` |
| تُ | تُ | `t` `u` | | | |
| ٱ | | | | ٱ | `hamza_wasl_elision` |
| لْ | لْ | `l` | | | `lam_qamariyyah` |
| قُ | قُ | `q` `u` | | | `tafkheem` |
| رْ | رْ | `rˤ` | | | `tafkheem` |
| ءَ | ءَ | `ʔ` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| نِ | نِ | `n` `i` | | | |
| وَ | وَ | `w` `a` | | | |
| كِ | كِ | `k` `i` | | | |
| تَ | تَ | `t` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| بٍ | بِ | `b` `i` | `m̃` | | `idgham_bi_ghunnah` |
| مُّ | مُّ | `m̃` `u` | | | `idgham_bi_ghunnah` |
| بِ | بِ | `b` | `i:` | | `madd_tabii` |
| ي | ي | `i:` | | | `madd_tabii` |
| نٍ | نْ | `n` | | ◌ٍ | `pausal_sukun` |

The stop sign of word 1 carries the `Structural` edge and takes no pairing, so
it has no row here and is present in both texts. Under plan B three rows change
and one is added: ٱ owns `ʔ` and names `hamza_wasl_start`, the helping fatha
takes a gap pairing after it and names the same rule, يَٰ names
`madd_arid_lil_sukun` where it named `madd_tabii`, and تُ owns `t` alone with
its damma `silent` and `pausal_sukun` in its rules.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - sound | ask the pairing of سٓ | it receives the sounds of a whole letter name at once. The glyph has no sub-range, so a consumer painting one letter of the name reads the recited text instead, where each name is spelled out |
| script - rules | light the ikhfaa's trigger | the rule is in the سٓ pairing and the letter that fired it is in the next word and names nothing, so a legend that wants the trigger locates it itself. One field read |
| script - recited | expand one source glyph | one call: it names several rendered glyphs, read through `from_glyphs` on each |
| identity | tell the two plans apart | **FINDING.** They are two documents whose `ref`, `riwayah`, `script`, `variant` and `canon_digest` are identical. Section 3 publishes no boundary field, so nothing in the identity separates them, and a consumer keyed on identity serves plan A's document for a plan B request |
| the other three | | one call and one field read |

One glyph is one pairing owning a whole name, and the noon inside that name
fires into the following word, so a spelled name is not closed. The stop before
word 4 moves the same wasl seat from silent to sounding while every source
glyph stands.

### E18. A hamza written as the vowel before it

Plan A: `mappings("2:283:12-2:283:17")`, joined throughout, stopping after word
17.

| word | source | recited | phonemes |
|---|---|---|---|
| 12 | بَعْضُكُم | بَعْضُكُم | `b a ʕ dˤ u k u ŋ` |
| 13 | بَعْضًا | بَعْضَن | `b a ʕ dˤ aˤ ŋ` |
| 14 | فَلْيُؤَدِّ | فَلْيُؤَدِّ | `f a l j u ʔ a dd i` |
| 15 | ٱلَّذِى | لَّذِ | `ll a ð i` |
| 16 | ٱؤْتُمِنَ | ؤْتُمِنَ | `ʔ t u m i n a` |
| 17 | أَمَـٰنَتَهُۥ | أَمَانَتَهْ | `ʔ a m a: n a t a h` |

Plan B: the same request with `stops=("2:283:15",)`, so word 16 is started on.

| word | source | recited | phonemes |
|---|---|---|---|
| 15 | ٱلَّذِى | لَّذِى | `ll a ð i:` |
| 16 | ٱؤْتُمِنَ | أُوتُمِنَ | `ʔ u: t u m i n a` |

Word 13 is 4.1a's ikhfaa line, the haraka then a bare noon, and its seat goes
by row 4. Word 15 loses its carrier to row 10 under plan A and keeps it under
plan B. Word 16 under plan B is row 24 on the seat, row 13 for the haraka and
row 23 for the quiescent hamza. Word 17 is rows 26 and 1, and the sukun that
replaces its damma is covered by no row.

**Part 1, units and parts.** Plan A, with the plan B reading where it differs.

| unit | part | realization | on the sound |
|---|---|---|---|
| w12 ba | consonant | hosts `b` | |
| w12 ba | vowel | hosts `a` | |
| w12 ain | consonant | hosts `ʕ` | |
| w12 ain | vowel | not applicable | |
| w12 dad | consonant | hosts `dˤ` | heavy, `tafkheem` |
| w12 dad | vowel | hosts `u` | |
| w12 kaf | consonant | hosts `k` | |
| w12 kaf | vowel | hosts `u` | |
| w12 meem | consonant | hosts `ŋ`, by `ikhfaa_shafawi` | a hum, not doubled |
| w12 meem | vowel | not applicable | |
| w13 ba | consonant | hosts `b` | |
| w13 ba | vowel | hosts `a` | |
| w13 ain | consonant | hosts `ʕ` | |
| w13 ain | vowel | not applicable | |
| w13 dad | consonant | hosts `dˤ` | heavy, `tafkheem` |
| w13 dad | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w13 noon (tanween) | consonant | hosts `ŋ`, by `ikhfaa_haqiqi` | a hum, not doubled |
| w13 noon (tanween) | vowel | not applicable | |
| w14 fa | consonant | hosts `f` | |
| w14 fa | vowel | hosts `a` | |
| w14 lam | consonant | hosts `l` | |
| w14 lam | vowel | not applicable | |
| w14 ya | consonant | hosts `j` | |
| w14 ya | vowel | hosts `u` | |
| w14 hamza | consonant | hosts `ʔ` | |
| w14 hamza | vowel | hosts `a` | |
| w14 dal | consonant | hosts `dd` | |
| w14 dal | vowel | hosts `i` | |
| w15 hamza | consonant | silent, `hamza_wasl_elision` | |
| w15 hamza | vowel | silent, `hamza_wasl_elision` | |
| w15 lam | consonant | hosts `ll` | |
| w15 lam | vowel | hosts `a` | |
| w15 thal | consonant | hosts `ð` | |
| w15 thal | vowel | hosts `i`; hosts `i:` under B | long by `madd_jaiz_munfasil`, then short by `iltiqa_shortening`; long by `madd_tabii` under B |
| w16 hamza (wasl) | consonant | silent, `hamza_wasl_elision`; hosts `ʔ`, by `hamza_wasl_start`, under B | |
| w16 hamza (wasl) | vowel | silent, `hamza_wasl_elision`; hosts `u:` under B | long, `madd_tabii`; labelled `madd_badal`, under B |
| w16 hamza | consonant | hosts `ʔ`; silent, `ibdal_hamza`, under B | |
| w16 hamza | vowel | not applicable | |
| w16 ta | consonant | hosts `t` | |
| w16 ta | vowel | hosts `u` | |
| w16 meem | consonant | hosts `m` | |
| w16 meem | vowel | hosts `i` | |
| w16 noon | consonant | hosts `n` | |
| w16 noon | vowel | hosts `a` | |
| w17 hamza | consonant | hosts `ʔ` | |
| w17 hamza | vowel | hosts `a` | |
| w17 meem | consonant | hosts `m` | |
| w17 meem | vowel | hosts `a:` | long, `madd_tabii` |
| w17 noon | consonant | hosts `n` | |
| w17 noon | vowel | hosts `a` | |
| w17 ta | consonant | hosts `t` | |
| w17 ta | vowel | hosts `a` | |
| w17 heh | consonant | hosts `h` | |
| w17 heh | vowel | silent, `pausal_sukun` | |

The meem hidden at the lips and the noon hidden behind the dad print one token,
because the published sound carries no place of articulation.

**Part 2, pairings**, `text="source"`, `grouping="cluster"`, plan A.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| بَ | بَ | `b` `a` | | | |
| عْ | عْ | `ʕ` | | | |
| ضُ | ضُ | `dˤ` `u` | | | `tafkheem` |
| كُ | كُ | `k` `u` | | | |
| م | م | `ŋ` | | | `ikhfaa_shafawi` |
| بَ | بَ | `b` `a` | | | |
| عْ | عْ | `ʕ` | | | |
| ضً | ضَن | `dˤ` `aˤ` `ŋ` | | | `tafkheem`, `ikhfaa_haqiqi` |
| ا | | | | ا | `orthographic_silence` |
| فَ | فَ | `f` `a` | | | |
| لْ | لْ | `l` | | | |
| يُ | يُ | `j` `u` | | | |
| ؤَ | ؤَ | `ʔ` `a` | | | |
| دِّ | دِّ | `dd` `i` | | | |
| ٱ | | | | ٱ | `hamza_wasl_elision` |
| لَّ | لَّ | `ll` `a` | | | |
| ذِ | ذِ | `ð` `i` | | | `madd_jaiz_munfasil`, `iltiqa_shortening` |
| ى | | | | ى | `iltiqa_shortening` |
| ٱ | | | | ٱ | `hamza_wasl_elision` |
| ؤْ | ؤْ | `ʔ` | | | |
| تُ | تُ | `t` `u` | | | |
| مِ | مِ | `m` `i` | | | |
| نَ | نَ | `n` `a` | | | |
| أَ | أَ | `ʔ` `a` | | | |
| مَٰ | مَا | `m` `a:` | | | `madd_tabii` |
| نَ | نَ | `n` `a` | | | |
| تَ | تَ | `t` `a` | | | |
| هُۥ | هْ | `h` | | ◌ُ, ۥ | `pausal_sukun` |

Under plan B four rows change: ذِ owns `ð` and shares `i:` with `madd_tabii`; ى
owns `i:` and names `madd_tabii`; ٱ of word 16 owns `ʔ` and names
`hamza_wasl_start`; ؤْ renders as و, owns `u:` and names `ibdal_hamza` and
`madd_tabii`. The damma the started-on seat takes is written in the recited
text and nowhere in the rasm, so ٱ presents no vowel and the substituted hamza
owns the one that sounds.

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| script - recited | read `from_glyphs` on the rendered waw at the ibdal | **FINDING.** Row 25 promises a glyph covering the vowel's source glyph and the hamza's; here the vowel is itself an insertion, so the tuple has one member |
| sound - rules | order the thal's lengthening against its shortening | no order between them is published. The sound's own `long` field is the answer; the two modifier edges are the account, and a consumer reading only the first is wrong |
| script - rules | account for word 15's yaa | one field read, and a consumer that reached for the reclass finds a deletion: the yaa is written in one plan and not in the other, and the rule that removes it is `iltiqa_shortening` rather than row 29's reclass |
| identity | tell the two plans apart | **FINDING**, the one E17 records, and here it separates two readings of the same six words |
| the other three | | one call and one field read |

The substitution happens only when the word is started on: joined, the
quiescent hamza is an ordinary consonant and its seat and its sukun render
unchanged. The wasl glyph before it moves either way, deleted when the plan
joins and respelled as a hamza with a damma when the plan starts there. Word 17
is stopped on under both plans, so its silah vowel is absent and no lengthening
in this request carries the `silah` label.

### E19. Colour, and the vowel that tilts

`mappings("11:41:6-11:41:11")`, joined throughout, stopping after word 11.

| word | source | recited | phonemes |
|---|---|---|---|
| 6 | مَجْر۪ىٰهَا | مَجْرِ۪ىهَا | `m a ʒ Q r i: h a:` |
| 7 | وَمُرْسَىٰهَآ ۚ | وَمُرْسَاهَآ ۚ | `w a m u rˤ s a: h a:` |
| 8 | إِنَّ | إِنَّ | `ʔ i ñ a` |
| 9 | رَبِّى | رَبِّى | `rˤ aˤ bb i:` |
| 10 | لَغَفُورٌ | لَغَفُورُ | `l a ɣ aˤ f u: rˤ u` |
| 11 | رَّحِيمٌ | رَّحِيمْ | `rˤrˤ aˤ ħ i: m` |

Word 6 is row 26 on a dagger whose vowel is not a long a: the expansion writes
the haraka the unit carries and the carrier that quality takes, and the imala
mark itself is kept. No row of the catalogue states that respelling, so it is
row 26 read together with the unit's own quality. The maddah of word 7 stands
because the plan joins, which is the contrast row 2 is stated against, and its
stop sign is row 30. Word 10 is 4.1a's idgham line and word 11 already carries
the shadda.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w6 meem | consonant | hosts `m` | |
| w6 meem | vowel | hosts `a` | |
| w6 jeem | consonant | hosts `ʒ`, and the release `Q` beside it | the release is sughra, `qalqala_sughra` |
| w6 jeem | vowel | not applicable | |
| w6 ra | consonant | hosts `r` | named light, `tarqeeq` |
| w6 ra | vowel | hosts `i:` | tilted, `imala`; long, `madd_tabii` |
| w6 heh | consonant | hosts `h` | |
| w6 heh | vowel | hosts `a:` | long, `madd_tabii` |
| w7 waw | consonant | hosts `w` | |
| w7 waw | vowel | hosts `a` | |
| w7 meem | consonant | hosts `m` | |
| w7 meem | vowel | hosts `u` | |
| w7 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w7 ra | vowel | not applicable | |
| w7 seen | consonant | hosts `s` | |
| w7 seen | vowel | hosts `a:` | long, `madd_tabii` |
| w7 heh | consonant | hosts `h` | |
| w7 heh | vowel | hosts `a:` | long, `madd_jaiz_munfasil` |
| w8 hamza | consonant | hosts `ʔ` | |
| w8 hamza | vowel | hosts `i` | |
| w8 noon | consonant | hosts `ñ` | doubled, with ghunnah; named, `ghunnah_mushaddadah` |
| w8 noon | vowel | hosts `a` | |
| w9 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w9 ra | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w9 ba | consonant | hosts `bb` | |
| w9 ba | vowel | hosts `i:` | long, `madd_tabii` |
| w10 lam | consonant | hosts `l` | |
| w10 lam | vowel | hosts `a` | |
| w10 ghain | consonant | hosts `ɣ` | heavy, `tafkheem` |
| w10 ghain | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w10 fa | consonant | hosts `f` | |
| w10 fa | vowel | hosts `u:` | long, `madd_tabii` |
| w10 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w10 ra | vowel | hosts `u` | |
| w10 noon (tanween) | consonant | merged into `rˤrˤ`, by `idgham_bila_ghunnah` | |
| w10 noon (tanween) | vowel | not applicable | |
| w11 ra | consonant | hosts `rˤrˤ`, by `idgham_bila_ghunnah` | doubled; heavy, `tafkheem` |
| w11 ra | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w11 ha | consonant | hosts `ħ` | |
| w11 ha | vowel | hosts `i:` | long, `madd_arid_lil_sukun` |
| w11 meem | consonant | hosts `m` | |
| w11 meem | vowel | silent, `pausal_sukun` | |
| w11 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w11 noon (tanween) | vowel | not applicable | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| مَ | مَ | `m` `a` | | | |
| جْ | جْ | `ʒ` `Q` | | | `qalqala_sughra` |
| ر۪ | رِ۪ | `r` | `i:` | | `tarqeeq`, `imala`, `madd_tabii` |
| ىٰ | ى | `i:` | | | `imala`, `madd_tabii` |
| هَ | هَ | `h` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| وَ | وَ | `w` `a` | | | |
| مُ | مُ | `m` `u` | | | |
| رْ | رْ | `rˤ` | | | `tafkheem` |
| سَ | سَ | `s` | `a:` | | `madd_tabii` |
| ىٰ | ا | `a:` | | | `madd_tabii` |
| هَ | هَ | `h` | `a:` | | `madd_jaiz_munfasil` |
| آ | آ | `a:` | | | `madd_jaiz_munfasil` |
| إِ | إِ | `ʔ` `i` | | | |
| نَّ | نَّ | `ñ` `a` | | | `ghunnah_mushaddadah` |
| رَ | رَ | `rˤ` `aˤ` | | | `tafkheem` |
| بِّ | بِّ | `bb` | `i:` | | `madd_tabii` |
| ى | ى | `i:` | | | `madd_tabii` |
| لَ | لَ | `l` `a` | | | |
| غَ | غَ | `ɣ` `aˤ` | | | `tafkheem` |
| فُ | فُ | `f` | `u:` | | `madd_tabii` |
| و | و | `u:` | | | `madd_tabii` |
| رٌ | رُ | `rˤ` `u` | `rˤrˤ` | | `tafkheem`, `idgham_bila_ghunnah` |
| رَّ | رَّ | `rˤrˤ` `aˤ` | | | `idgham_bila_ghunnah`, `tafkheem` |
| حِ | حِ | `ħ` | `i:` | | `madd_arid_lil_sukun` |
| ي | ي | `i:` | | | `madd_arid_lil_sukun` |
| مٌ | مْ | `m` | | ◌ٌ | `pausal_sukun` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| sound - rules | tell a colour from a classification | one field read each, and the sound's `emphatic` field alone gives the state of every raa here and the name of none: `tafkheem` recolours and `tarqeeq` only names |
| script - rules | colour the imala | the mark and the vowel it tilts fall in two clusters and both name the instance, so a consumer colouring the mark alone lights half of it. One field read |
| script - sound | derive a sound from a spelling | the source writes ىٰ, which spells a long a everywhere else in this request; the pairing answers and the glyph does not, so a consumer deriving sound from spelling is wrong at exactly this cluster |
| the other three | | one call and one field read |

The imala vowel prints as a long i under the shipped reading, so the quality
the contract reserves for the tilt never reaches a token. Beside it the same
letter carries the two colours in two edge families, which is the difference a
single `emphatic` field cannot show.

### E20. A rule that produces nothing

`mappings("12:11:5-12:11:8")`, joined throughout, stopping after word 8.

| word | source | recited | phonemes |
|---|---|---|---|
| 5 | لَا | لَا | `l a:` |
| 6 | تَأْمَ۫نَّا | تَأْمَ۫نَّا | `t a ʔ m a ñ a:` |
| 7 | عَلَىٰ | عَلَا | `ʕ a l a:` |
| 8 | يُوسُفَ | يُوسُفْ | `j u: s u f` |

The ishmam mark survives into the recited text under 4.7's unchanged case for
the tashil and ishmam marks: the mark is what the reciter reads, so the source
spelling is the recited spelling. Word 7 is row 26 and word 8 is row 19.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w5 lam | consonant | hosts `l` | |
| w5 lam | vowel | hosts `a:` | long, `madd_tabii` |
| w6 ta | consonant | hosts `t` | |
| w6 ta | vowel | hosts `a` | |
| w6 hamza | consonant | hosts `ʔ` | |
| w6 hamza | vowel | not applicable | |
| w6 meem | consonant | hosts `m` | |
| w6 meem | vowel | hosts `a` | |
| w6 noon | consonant | hosts `ñ` | doubled, with ghunnah; named, `ghunnah_mushaddadah` |
| w6 noon | vowel | hosts `a:` | long, `madd_tabii` |
| w7 ain | consonant | hosts `ʕ` | |
| w7 ain | vowel | hosts `a` | |
| w7 lam | consonant | hosts `l` | |
| w7 lam | vowel | hosts `a:` | long, `madd_tabii` |
| w8 ya | consonant | hosts `j` | |
| w8 ya | vowel | hosts `u:` | long, `madd_tabii` |
| w8 seen | consonant | hosts `s` | |
| w8 seen | vowel | hosts `u` | |
| w8 fa | consonant | hosts `f` | |
| w8 fa | vowel | silent, `pausal_sukun` | |

`ishmam` has no row above. It is the unit's rule and it reaches neither part.

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| لَ | لَ | `l` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| تَ | تَ | `t` `a` | | | |
| أْ | أْ | `ʔ` | | | |
| مَ۫ | مَ۫ | `m` `a` | | | `ishmam` |
| نَّ | نَّ | `ñ` | `a:` | | `ghunnah_mushaddadah`, `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| عَ | عَ | `ʕ` `a` | | | |
| لَ | لَ | `l` | `a:` | | `madd_tabii` |
| ىٰ | ا | `a:` | | | `madd_tabii` |
| يُ | يُ | `j` | `u:` | | `madd_tabii` |
| و | و | `u:` | | | `madd_tabii` |
| سُ | سُ | `s` `u` | | | |
| فَ | فْ | `f` | | ◌َ | `pausal_sukun` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| sound - rules | reach the ishmam from a sound | the instance names no sound, so no attribution and no modifier reaches it. It is in `m.rules` and in one pairing's `rules`, and a consumer animating by sound never meets it |
| script - rules | say what the instance on that row reached | under `grouping="cluster"` the mark folds into the meem's cluster, so the instance sits on a row that owns two real sounds and nothing on the row says the rule reaches neither. `grouping="glyph"` separates the mark and the row it gets owns nothing at all |
| script - sound | tell a soundless cluster from a soundless rule | **FINDING.** They are the same shape. `silent` distinguishes them, but only because it names glyphs recitation never says, and this mark is one the reciter performs |
| the other three | | one call and one field read |

**FINDING.** Learning that an instance produces nothing takes a scan of both
edge arrays that finds nothing. The exemption is a law of the gate and no field
of the document states it, so an empty result and a rule that owns nothing are
indistinguishable to a consumer that has not read the gate. This is the one
place a request's whole answer to sound - rules is an absence, and everything
else in the four words is ordinary, which is what makes the cost visible.

### E21. A hamza the reciter eases

`mappings("41:44:8-41:44:10")`, joined throughout, stopping after word 10.

| word | source | recited | phonemes |
|---|---|---|---|
| 8 | ءَايَـٰتُهُۥٓ ۖ | ءَايَاتُهُوٓ ۖ | `ʔ a: j a: t u h u:` |
| 9 | ءَا۬عْجَمِىٌّ | ءَا۬عْجَمِىُّ | `ʔ a ʔ a ʕ ʒ a m i jj u` |
| 10 | وَعَرَبِىٌّ ۗ | وَّعَرَبِىّْ ۗ | `w̃ a ʕ a rˤ aˤ b i jj` |

Word 8 is row 26 on the dagger and row 27 on the silah mark, which the joining
plan keeps, with the maddah standing on the carrier it expands into. The tashil
mark of word 9 is 4.7's unchanged case. Word 9's dammatan is 4.1a's idgham line
and word 10 takes the shadda row 18 adds; word 10 is row 20.

**Part 1, units and parts.**

| unit | part | realization | on the sound |
|---|---|---|---|
| w8 hamza | consonant | hosts `ʔ` | |
| w8 hamza | vowel | hosts `a:` | long, `madd_tabii`; labelled `madd_badal` |
| w8 ya | consonant | hosts `j` | |
| w8 ya | vowel | hosts `a:` | long, `madd_tabii` |
| w8 ta | consonant | hosts `t` | |
| w8 ta | vowel | hosts `u` | |
| w8 heh | consonant | hosts `h` | |
| w8 heh | vowel | hosts `u:` | long, `madd_jaiz_munfasil`; labelled `silah`, `silah_kubra` |
| w9 hamza | consonant | hosts `ʔ` | |
| w9 hamza | vowel | hosts `a` | |
| w9 hamza | consonant | hosts `ʔ` | named eased, `tashil` |
| w9 hamza | vowel | hosts `a` | |
| w9 ain | consonant | hosts `ʕ` | |
| w9 ain | vowel | not applicable | |
| w9 jeem | consonant | hosts `ʒ` | |
| w9 jeem | vowel | hosts `a` | |
| w9 meem | consonant | hosts `m` | |
| w9 meem | vowel | hosts `i` | |
| w9 ya | consonant | hosts `jj` | doubled |
| w9 ya | vowel | hosts `u` | |
| w9 noon (tanween) | consonant | merged into `w̃`, by `idgham_bi_ghunnah` | |
| w9 noon (tanween) | vowel | not applicable | |
| w10 waw | consonant | hosts `w̃`, by `idgham_bi_ghunnah` | doubled, with ghunnah |
| w10 waw | vowel | hosts `a` | |
| w10 ain | consonant | hosts `ʕ` | |
| w10 ain | vowel | hosts `a` | |
| w10 ra | consonant | hosts `rˤ` | heavy, `tafkheem` |
| w10 ra | vowel | hosts `aˤ` | heavy, `tafkheem` |
| w10 ba | consonant | hosts `b` | |
| w10 ba | vowel | hosts `i` | |
| w10 ya | consonant | hosts `jj` | doubled |
| w10 ya | vowel | silent, `pausal_sukun` | |
| w10 noon (tanween) | consonant | silent, `pausal_sukun` | |
| w10 noon (tanween) | vowel | not applicable | |

**Part 2, pairings**, `text="source"`, `grouping="cluster"`.

| source | recited | owns | shares | silent | rules |
|---|---|---|---|---|---|
| ءَ | ءَ | `ʔ` | `a:` | | `madd_tabii` |
| ا | ا | `a:` | | | `madd_tabii` |
| يَٰ | يَا | `j` `a:` | | | `madd_tabii` |
| تُ | تُ | `t` `u` | | | |
| هُۥٓ | هُوٓ | `h` `u:` | | | `madd_jaiz_munfasil` |
| ءَ | ءَ | `ʔ` `a` | | | |
| ا۬ | ا۬ | `ʔ` `a` | | | `tashil` |
| عْ | عْ | `ʕ` | | | |
| جَ | جَ | `ʒ` `a` | | | |
| مِ | مِ | `m` `i` | | | |
| ىٌّ | ىُّ | `jj` `u` | `w̃` | | `idgham_bi_ghunnah` |
| وَ | وَّ | `w̃` `a` | | | `idgham_bi_ghunnah` |
| عَ | عَ | `ʕ` `a` | | | |
| رَ | رَ | `rˤ` `aˤ` | | | `tafkheem` |
| بِ | بِ | `b` `i` | | | |
| ىٌّ | ىّْ | `jj` | | ◌ٌ | `pausal_sukun` |

**Part 3, the walk.**

| relationship | what a consumer must do | cost |
|---|---|---|
| sound - rules | tell the eased hamza from the plain one | one field read to reach the rule and none at all to reach the manner: the two are the same token, the ease is a `Classifies` edge and no field of the sound, which is what the contract intends and what a consumer reading tokens alone cannot recover |
| script - sound | ask an alif what it owns | one field read, and a consumer keyed on the base letter reads an alif twice and hears two different things: the ا۬ of word 9 owns a hamza and the vowel after it, where the plain ا of word 8 owns the long a of the letter before it |
| script - recited | expand the silah mark | one call: one source glyph names a haraka and a carrier |
| the other three | | one call and one field read |

Manner is a rule here and nothing else, so two hamzas a reciter says
differently are separated by their rule lists alone. The label on the
lengthening names a configuration the graph already states and mints no
instance, so the length it reports is the madd rule's, and `m.rules` carries no
entry called `silah_kubra`: a consumer looking that teaching name up scans
every instance's `labels`.

---

## 3. Coverage

Three tables, one per thing that has to be covered. A blank cell is the point
of the table: it says the set has no place where a consumer could see that
thing, and section 4 says why.

### 3.1 Every rule

| Rule | Exercised by |
|---|---|
| `ikhfaa_haqiqi` | E2, E6, E13, E17, E18 |
| `iqlab` | E13 |
| `idgham_bi_ghunnah` | E5, E6, E7, E8, E12, E14, E17, E21 |
| `idgham_bila_ghunnah` | E9, E19 |
| `izhar` | E6, E9 |
| `ghunnah_mushaddadah` | E2, E19, E20 |
| `izhar_shafawi` | E2, E4, E7, E9, E10, E11 |
| `ikhfaa_shafawi` | E18 |
| `idgham_shafawi` | E6, E7 |
| `idgham_mutamathilayn` | E10 |
| `idgham_mutaqaribayn` | E7 |
| `idgham_mutajanisayn_kamil` | E12 |
| `idgham_mutajanisayn_naqis` | E11 |
| `lam_shamsiyyah` | E13, E15 |
| `lam_qamariyyah` | E1, E4, E14, E17 |
| `madd_tabii` | E1 to E4, E6, E8 to E21 |
| `madd_wajib_muttasil` | E3, E7, E15 |
| `madd_jaiz_munfasil` | E6, E14, E18, E19, E21 |
| `madd_lazim` | E17 |
| `madd_arid_lil_sukun` | E7, E13, E16, E17, E19 |
| `madd_leen` | E6 |
| `iltiqa_shortening` | E14, E18 |
| `qalqala_sughra` | E6, E10, E11, E12, E13, E19 |
| `qalqala_kubra` | E9 |
| `qalqala_akbar` | E4 |
| `tafkheem` | E4, E6, E7, E8, E11 to E14, E16 to E19, E21 |
| `tarqeeq` | E16, E19 |
| `imala` | E19 |
| `tashil` | E21 |
| `ishmam` | E20 |
| `hamza_wasl_start` | E4, E6, E15, E17, E18 |
| `hamza_wasl_elision` | E1, E12, E13, E14, E17, E18 |
| `iltiqa_kasra` | E12 |
| `pausal_sukun` | E2, E3, E4, E6 to E9, E11, E13 to E21 |
| `taa_marbuta_pausal` | E8 |
| `ibdal_hamza` | E18 |
| `orthographic_silence` | E2, E3, E5, E8, E9, E16, E18 |
| `madd_iwad` (label) | E2, E3, E15 |
| `madd_badal` (label) | E6, E17, E18, E21 |
| `silah` (label) | E9, E10, E11, E12, E13, E14, E21 |
| `silah_kubra` (label) | E14, E21 |

### 3.2 Every catalogue row

Rows are [06-two-texts](06-two-texts.md) section 4, by number and by
subsection.

| Row | Shown in |
|---|---|
| 4.1 deleted | |
| 1 | E8 |
| 2 | E11, E13, E14, E18 |
| 3 | E14 |
| 4 | |
| 5 | E3, E16 |
| 6 | E2, E5, E8, E9, E16, E18 |
| 7 | E3, E16 |
| 8 | E1, E12, E13, E14, E17, E18 |
| 9 | E6, E7, E9, E10, E12, E14 |
| 10 | E13, E15 |
| 11 | E7, E8 |
| 12 | E14, E18 |
| 13 | E1, E3, E12 |
| 4.1a spelled apart | |
| `izhar` | E9 |
| `ikhfaa_haqiqi`, `iqlab` | E2, E18 |
| an idgham | E5, E6, E7, E8, E12, E17, E19, E21 |
| `iltiqa_kasra` | E12 |
| 4.2 inserted | |
| 14 | E5 |
| 15 | E4, E6, E15, E17, E18 |
| 16 | E12 |
| 17 | E15 |
| 18 | E4, E13 |
| 19 | E3 |
| 20 | E6, E12, E14, E21 |
| 4.3 substituted | |
| 21 | E4, E11, E13, E14, E16, E17, E20 |
| 22 | E6, E7, E9, E17, E19, E21 |
| 23 | E2, E3, E15 |
| 24 | E8 |
| 25 | E18 |
| 26 | E4, E6, E15, E17, E18 |
| 27 | |
| 4.4 spelled out | |
| 28 | E17 |
| 29 | E1, E2, E3, E12, E13, E17, E18, E19, E20, E21 |
| 30 | E9, E10, E11, E12, E13, E14, E21 |
| 4.5 reclassed | |
| 31 | E2, E3 |
| 32 | |
| 4.6 kept | |
| 33 | E2, E14, E17, E19, E21 |
| 34 | E1, E2, E15 |
| 4.7 unchanged | |
| a shadda marking root gemination | E4, E18, E19, E20 |
| the maddah over a `madd_wajib_muttasil` | E3, E7, E15 |
| an iqlab, when the plan joins | E13 |
| `idgham_mutajanisayn_naqis` | E11 |
| every ikhfaa and every izhar | E2, E6, E9, E13, E18 |
| `tafkheem` and `tarqeeq` | E16, E19 |
| the tashil and the ishmam mark | E20, E21 |
| the sakt mark | E10 |
| the qalqala echo | E4, E9, E10, E12, E13, E19 |

### 3.3 Every law

A law's cell names an example where a consumer could see the law fail. Where an
example does catch it failing, the cell says so.

| Law | Where it lives | Caught by |
|---|---|---|
| request identity is present | 4.1 | E1 |
| canonical serialization is byte-stable | 4.1 | |
| every index is in range and of the declared kind | 4.1 | |
| node order is reading order, one index space per request | 4.1 | E16 |
| changing the request changes the identity field | 4.1 | E16, E17, E18, all FINDING |
| every source scalar produces one glyph | 4.2 | E3 |
| concatenating `char` reproduces the source text | 4.2 | E2 |
| every glyph participates in a spelling edge | 4.2 | E2, E7, E19 |
| the `Structural` edge is exclusive | 4.2 | E2, E19 |
| every `Supplies` edge names the correct fact | 4.2 | E2, E15 |
| many-to-many edges are present rather than collapsed | 4.2 | E2, E17 |
| a dagger over a written carrier supplies the vowel | 4.2 | E2, FINDING |
| one realization per applicable part | 4.3 | E1 |
| every sound has one primary origin | 4.3 | E5 |
| every merger is a `Hosts` and `MergedInto` pair | 4.3 | E5 |
| every insertion has a valid anchor and lands after it | 4.3 | E12 |
| every silence names a rule | 4.3 | E1, E3, E16 FINDING |
| every release is hosted on a consonant | 4.3 | E4, E11 |
| every attribution names exactly one unit | 4.3 | E5 |
| a consonant hosts while the same unit's vowel is silent | 4.3 | E4 |
| `source` is the unit the rule is about | 4.4 | E5, E13 |
| only a merger carries a host | 4.4 | E6, E11, E13 |
| every recolour and length change keeps one modifier edge | 4.4 | E13, E14, E19 |
| every classification-only rule has a `Classifies` edge | 4.4 | E6, E14, E19, E11 FINDING |
| every instance owns an attribution or a modifier | 4.4 | E3, E20 |
| under `text="recited"` no sound takes a gap pairing | 4.5 | E4, E12, E15 |
| every sound and rule a pairing names resolves | 4.5 | E1 |
| structural glyphs take no pairing | 4.5 | E1, E14, E17 |
| a haraka and a carrier may both present one vowel | 4.5 | E15 |
| a carrier under a dagger presents nothing | 4.5 | E2, FINDING |
| a maddah may present a target it supplies no fact for | 4.5 | E3, E14 |
| a soundless mark may present its rule instance | 4.5 | E20, E21 |
| no audibility of a glyph is inferred from its unit | 4.5 | E2 |
| the pairings partition the selected text's glyphs | 4.6 | E2 |
| the pairings cover every sound exactly once in `sounds` | 4.6 | E2, E5 |
| a gap pairing has no glyphs, one sound and an `after` | 4.6 | E4 |
| a sound takes a gap exactly when no glyph presents it | 4.6 | E4, E12 |
| `shares` names only sounds another pairing owns | 4.6 | E5 |
| `silent` names glyphs written and not said | 4.6 | E5, E13 FINDING |
| both arrays are populated whichever text is selected | 4.6 | E2, E8 |
| ownership follows the published order, and it is total | 4.6 | E1, E4, E15 |
| the writer is total for every representation and insertion | 4.7 | E17 |
| every rendered glyph names a source glyph or is an insertion | 4.7 | E4 FINDING, E8, E15, E18 |
| source glyph order and values never change | 4.7 | E8 |
| no rendered glyph carries an empty character | 4.7 | E1 |
| a part is applicable unless the vowel is absent in both forms | contract 8 | E2, E5, E17 |
| a vowel canonically long requires a madd rule | 4.8 | E1, E14 FINDING |
| a vowel long in its stopped form, stopped | 4.8 | E2, E3 |
| a vowel long in its joined form, joined | 4.8 | E9, E13 |
| a silent waw or yaa after a short a requires `madd_leen` | 4.8 | E6 |
| a sakin noon or tanween joined requires a noon rule | 4.8 | E5, E6, E12 FINDING |
| a sakin meem joined requires a meem rule | 4.8 | E6, E7, E9, E18 |
| a geminate noon or meem requires `ghunnah_mushaddadah` | 4.8 | E2, E19 |
| identical, close or homorganic consonants joined require an idgham | 4.8 | E7, E10, E11, E12 |
| an article lam requires one of the two lam rules | 4.8 | E1, E13, E14 |
| a wasl consonant word-initial and started on requires `hamza_wasl_start` | 4.8 | E4 |
| a wasl consonant otherwise requires `hamza_wasl_elision` | 4.8 | E1 |
| two sakins meeting across a boundary, joined, require an iltiqa rule | 4.8 | E12, E14 |
| a qalqala letter with a silent vowel requires its degree | 4.8 | E4, E9, E10 |
| the same, merged away, requires none | 4.8 | E12 |
| an istilaa letter or a raa requires `tafkheem` or `tarqeeq` | 4.8 | E13, E19 |
| a taa marbuta at a stop requires `taa_marbuta_pausal` | 4.8 | E8 |
| a substituted quiescent hamza requires `ibdal_hamza` | 4.8 | E18 |
| a vowel, tanween or silah the stop takes requires `pausal_sukun` | 4.8 | E6, E11, E18, E20 |
| an imala, ishmam or tashil mark requires that rule | 4.8 | E19, E20, E21 |
| an ikhfaa before an istilaa letter requires a heavy ghunnah | 4.8 | E13 |
| a letter the canonical layer gives no sound requires `orthographic_silence` | 4.8 | E16 |
| a label mints no instance of its own | 4.8 | E3, E6, E14, E21 |

---

## 4. What the set cannot reach

What a reader should not go looking for, and why it is not here.

| | Why no example shows it |
|---|---|
| byte-stable serialization | a property of the harness, and no table can carry a canonical serialization, so nothing on a page could disagree with it |
| an index out of range or of the wrong kind | the tables print resolved letters, sounds and rules rather than indices, so a wrong index is invisible in this format |
| the iqlab mark | this script does not write one, so the catalogue has no row for it and no passage could show it. E13 shows what an iqlab does to the noon and to a tanween |
| the imala mark respelled | the mark is written and stays written, so the catalogue has no row for it. E19 writes the vowel's quality from the unit and the carrier from row 26 |
| row 29, the word-final role flip | no word in the set ends in a voweled yaa, waw or alif maqsura at a stop. E18 reaches for the row and finds a deletion instead |
| the verse marker | it is not a glyph in this corpus, so it cannot be shown taking no pairing, and the concatenation law's third constituent cannot appear. E2 concatenates a space and a stop sign back to the printed source string; the tatweel is in E1 and E3 and the stop sign in E2, E14, E17, E19 and E21 |
| a gap pairing with no `after` | every sound in the corpus with no source glyph is a helping vowel or an insertion following a seat that already presents a sound, so no gap can precede every pairing. E4 gives the other half of the law |

Where a rule or a row needed a transformation the catalogue does not carry,
the example states the transformation and marks it, rather than inventing a
row: the sukun on a
pausal taa marbuta in E8, the sukun on a stopped silah in E11, E13, E14 and
E18, the fathatan with no seat in E15, and the imala respelling in E19.
