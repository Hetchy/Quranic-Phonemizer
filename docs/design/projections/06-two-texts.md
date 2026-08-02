# 06 - The two texts

Status: **proposed**. Scope: Uthmani, Hafs.

What `rendered` holds, how a consumer reads it against `glyphs`, and every
transformation between the two. [01-contract](01-contract.md) defines the node
and edge types and names the glyph kinds; this document states what each
transformation does and nothing that document already says.

---

## 1. What `rendered` is

**`rendered` is what recitation writes.** A thing recitation does not say is
absent from it. There is no silenced flag, no tombstone glyph and no parallel
array of what was removed.

Two consequences a consumer relies on:

- concatenating `rendered` gives a string that can be drawn without filtering;
- `rendered` and `glyphs` are two texts, not one text and a set of edits, so
  neither is derived by replaying the other.

What is written and not said is a fact about the **source** text, and it is
answered there: `pairing.silent` names the glyphs, and each names its rule.
Putting the same fact into `rendered` would state it twice and would make the
recited text unconcatenable, which is the one thing it is for.

The consumer that motivated this document is a mushaf renderer that colours
tajweed on the page and shows the recited form of a clicked word beside it. It
draws the source text on the page, unmodified, with a distinct colour per kind
of silence, and it draws the recited text in a separate panel as one string.
The two texts appear in two places. It has no diff view, and the strikethrough
reading - a recited line with the dropped glyphs shown struck out - is a mark
on the writing rather than on the recitation, so it is drawn over the source
array and its `silent` list.

### 1.1 The recited spelling is not a policy

There is one recited spelling and no setting selects it. A hamza wasl started
on is written as the hamza its vowel calls for, with that vowel: `أ` with a
fatha or a damma, `إ` with a kasra. Writing the wasl seat and hanging a helping
haraka on it produces a spelling no mushaf carries and no reader recognises.

---

## 2. Reading the two arrays

`RenderGlyph.from_glyphs` is the link. It is a tuple, and its length is the
whole of what it says:

| Length | Means |
|---|---|
| 0 | an insertion: nothing in the source produced this |
| 1 | kept if the character matches, substituted if not |
| more than one | merged: this rendered glyph covers several source glyphs |

The inverse is not a field. A source glyph named by no rendered glyph is a
glyph the recited text does not write, and that is read from the source side.

| Relationship | Read it as |
|---|---|
| kept | one `from_glyphs` entry, same character |
| substituted | one entry, different character |
| inserted | `from_glyphs` empty |
| split | several rendered glyphs naming one source glyph |
| merged | one rendered glyph naming several source glyphs |
| dropped | no rendered glyph names the source glyph in its `from_glyphs`. Silence is a different question: a merged-away letter and a shortened carrier are dropped and not silent |

**Dropped is the one that is not read from `from_glyphs`, and it is the one
where the answer matters most.** Scanning `rendered` for an absent source index
says only that a glyph is unrepresented. It does not distinguish a stop taking
a vowel from a letter the rasm never says from a consonant a merger took, and a
consumer colouring silence needs all three apart. The pairing separates them: a
unit the reading silenced carries a `Silent` edge naming its rule, a merged
consonant carries `MergedInto` naming its host, and a letter with no unit at
all has the rule in its pairing's `rules`.

So the two arrays answer shape, and the pairings answer cause. A consumer that
diffs the arrays and stops there gets three cases wrong.

---

## 3. The axes

Every row of the catalogue states four things.

| Axis | Values | Means |
|---|---|---|
| **effect** | `delete` · `insert` · `substitute` · `spell out` · `reclass` · `kept` | what happens to the glyph sequence |
| **kind** | `orthographic` · `performance` · `advice` | whether the rasm could have written it otherwise, or the reciter could have read it otherwise |
| **boundary** | `none` · `joined` · `stopped` · `started` | the boundary state that triggers it |
| **owner** | a rule, or `-` | the instance a consumer reaches it through |

`orthographic` means the difference holds under every boundary plan: the rasm
wrote a letter compactly, or wrote one it never says. `performance` means the
difference is a property of this reading of this passage. The distinction
decides what a consumer may cache per word and what it must ask for per
request.

`owner = -` says a real difference between the two texts is reachable through
no rule instance. Those rows are why the catalogue exists: a consumer cannot
find them through `r.rules` and has nowhere else to look.

A glyph kind is not the unit of this decision. Eleven kinds do not decide
thirty-four transformations, and a kind that behaves one way under a rule and
another way under a different rule has no single cell: the maddah over a madd
whose trigger is inside the word survives every plan, and the maddah over one
whose trigger is the next word goes as soon as the plan stops. Both are
`madd_sign`. The rule decides, so the rule is the row.

---

## 4. The catalogue

### 4.1 Deleted: the script writes it, recitation does not say it

| | Transformation | Trigger | Kind | Boundary | Owner |
|---|---|---|---|---|---|
| 1 | the silah mark goes, and any maddah on it | a stopped word whose vowel is long joined and absent stopped | performance | stopped | `pausal_sukun` |
| 2 | the maddah over a madd the stop reverts goes | a stopped word whose final vowel carried a maddah for `madd_jaiz_munfasil` | performance | stopped | **-** |
| 3 | a letter the rasm carries and recitation never says goes | the canonical no-sound verdict | orthographic | none | `orthographic_silence` |
| 4 | the same letter goes when the plan joins, and stays when it stops | the verdict, on a unit whose vowel is short joined and long stopped | performance | joined | `orthographic_silence` |
| 5 | the silence sign goes | a round or a rectangular zero | orthographic | none | **-** |
| 6 | the hamza wasl seat goes | not started on, or not word-initial | performance | joined | `hamza_wasl_elision` |
| 7 | the merged-away consonant goes, with its sukun | joined, an idgham fires | performance | joined | the idgham rule |
| 8 | the article lam goes, with its sukun | the article before a sun letter | performance | none | `lam_shamsiyyah` |
| 9 | the word-initial shadda goes | started on a word whose first shadda is the previous word's idgham trace | performance | started | **-** |
| 10 | the carrier of a shortened long vowel goes | joined, two sakins meet | performance | joined | `iltiqa_shortening` |
| 11 | the verse marker and the tatweel go | a structural glyph | orthographic | none | **-** |

Rows 3 and 4 are one rule and two behaviours, and `letter` does not tell them
apart: the same alif is row 3 in one word and row 4 in another. What separates
them is the sign the rasm wrote over it, which
[07-rules](07-rules.md) section 5 places with the script adapter rather than
with the rule.

### 4.1a How a tanween is spelled out

The tanween is one mark over two units, so the recited text has to write them
apart. What it writes is not a choice: the noon is a unit like any other and
the rule that fired on it says how it is said, so the spelling follows the
rule.

| The noon's rule | The recited text writes |
|---|---|
| `izhar` | the haraka, then a noon with a sukun |
| `ikhfaa_haqiqi`, `iqlab` | the haraka, then a bare noon |
| an idgham | the haraka alone; the host carries the shadda |
| `iltiqa_kasra` | the haraka, then a noon with a kasra |

The bare noon is not an omission. A consonant the rasm leaves bare is
orthographically distinct from one bearing a sukun, and bareness is what
signals the assimilation coming, which is the same convention the source text
already uses on a written noon.

### 4.2 Inserted: recitation says it, the script does not write it

| | Transformation | Trigger | Kind | Boundary | Owner |
|---|---|---|---|---|---|
| 12 | a sukun is written on a letter the rasm left bare | a stopped word whose final consonant the rasm wrote bare | performance | stopped | **-** |
| 13 | the helping haraka is written | started on, a consonant that sounds only when started on | performance | started | `hamza_wasl_start` |
| 14 | the helping kasra is written, and the noon it follows | joined, two sakins meet after a tanween | performance | joined | `iltiqa_kasra` |
| 15 | an alif is written where the rasm has no seat for the fathatan to lengthen | a stopped word ending in a nunated hamza | performance | stopped | a madd rule |
| 16 | the long a of the divine name is written | that lam, which no carrier follows | orthographic | none | a madd rule |
| 17 | a carrier is written for a word-final long a the rasm writes bare | a stopped word ending in a bare alif maqsura that sounds as a long a | performance | stopped | a madd rule |
| 18 | a shadda is written on an idgham host the rasm does not double | joined, a cross-word idgham | performance | joined | the idgham rule |

Row 12 is the largest population in the catalogue and the one a per-kind
account cannot reach. Where the rasm wrote a haraka, the stop replaces it (row
19). Where the rasm left the consonant bare because a cross-word rule was going
to take it, there is no haraka to replace and the write is the whole
transformation. Bareness is not an absence of information in the rasm: it says
an assimilation follows. A stop cancels the assimilation, so the sukun the rasm
left out has to be written back.

Row 14 writes a letter and not only a mark. The tanween's noon is a unit no
glyph writes, so a recited text that wrote the kasra alone would leave that
noon's consonant presented by no rendered glyph, which
[02-gate](02-gate.md) section 4.5 forbids.

Row 16 is the one insertion whose sound the source text does write: the fatha
supplies the vowel and only its length carrier is missing. It is here rather
than under `spell out` because there is nothing in the rasm to spell out from.

### 4.3 Substituted: one thing written, another said

| | Transformation | Trigger | Kind | Boundary | Owner |
|---|---|---|---|---|---|
| 19 | the haraka of a vowel the stop silences becomes a sukun | a stopped word whose final vowel the stop takes, short or long | performance | stopped | `pausal_sukun` |
| 20 | a final tanween that leaves no lengthening becomes a sukun | a stopped word, nunated, where nothing lengthens: a dammatan, a kasratan, or a fathatan on a taa marbuta | performance | stopped | `pausal_sukun` |
| 21 | a fathatan becomes a fatha | a stopped word whose fathatan lengthens, whether the seat is written or row 15 invents it | performance | stopped | a madd rule |
| 22 | a taa marbuta becomes a haa | a stopped word ending in taa marbuta | performance | stopped | `taa_marbuta_pausal` |
| 23 | a quiescent hamza becomes a vowel letter | the reading substitutes it | orthographic | none | `ibdal_hamza` |
| 24 | the hamza wasl seat becomes the hamza its vowel calls for | started on | performance | started | `hamza_wasl_start` |

Row 22 changes the glyph. The pausal realization of a taa marbuta is a haa, and
the recited text writes what is said, so it writes a haa. The taa marbuta in
`glyphs` is untouched, which is a different statement about a different array.

Row 23 is the case that makes `from_glyphs` a tuple: the hamza is written as
the madd letter of the vowel before it, so one recited glyph covers the vowel's
source glyph and the hamza's.

### 4.4 Spelled out: the script writes it compactly

| | Transformation | Trigger | Kind | Boundary | Owner |
|---|---|---|---|---|---|
| 25 | a muqattaat glyph becomes its spelled letter names | a disjoined-letter opening | orthographic | none | **-** |
| 26 | a dagger alif becomes a haraka and a full carrier | any dagger alif | orthographic | none | **-** |
| 27 | a silah mark becomes a haraka and a full carrier | joined, a vowel long in its joined form | orthographic | joined | a madd rule |

Rows 26 and 27 are two instances of one policy: **a long vowel is written as
its haraka and then its carrier, whatever the rasm abbreviated it to.** A
maddah is kept where the rasm wrote one and never added, which is section 4.7.
The policy has no row of its own because it fires wherever a long vowel does,
and rows 16 and 17 are the two places it has to invent a carrier rather than
expand one.

Row 25 owns nothing and cannot. The expansion is not the outcome of a rule; the
rules that fire inside a spelled name own their own effects and nothing owns
the act of spelling out. It is the case where the letter-level and the
phoneme-level relation to a rule diverge furthest, which
[07-rules](07-rules.md) section 5 states.

### 4.5 Reclassed: no glyph changes, and the relation does

| | Transformation | Trigger | Kind | Boundary | Owner |
|---|---|---|---|---|---|
| 28 | the seat of a fathatan stops being silent | a stopped word whose written seat follows a fathatan | performance | stopped | a madd rule |
| 29 | a word-final yaa, waw or alif maqsura changes between consonant and vowel | a stopped word ending in one of them, voweled | performance | stopped | **-** |

Row 28 is why the catalogue cannot be a diff. Both arrays hold the same seat at
the same place with the same character, and the fact that changed is that the
seat now shows a sound. A consumer comparing characters sees nothing.

### 4.6 Kept, where a reader would expect otherwise

| | Transformation | Trigger | Kind | Boundary | Owner |
|---|---|---|---|---|---|
| 30 | the stop sign is kept, and takes no pairing | any stop sign | advice | none | **-** |
| 31 | the space between words is kept | a space | orthographic | none | **-** |

A stop sign is advice and not recitation, and dropping it from `rendered` on
that ground costs a consumer the one place it wants it: a recited line that
ends where the reader was told he may stop. Keeping it costs nothing, because
it carries the `Structural` edge and therefore takes no pairing and shows no
sound. It is present and it says nothing, which is exactly what it says on the
page.

### 4.7 Considered and unchanged

Nine cases where the recited text is the source text. They are listed because a
kind marked unchanged is not evidence that every case under it was examined.

| Case | Why |
|---|---|
| a shadda marking root gemination | the sound is doubled and the mark says so |
| the maddah over a `madd_wajib_muttasil` | the trigger hamza is inside the word, so no plan removes it. Contrast row 2 |
| an iqlab, when the plan joins | the sound is a hum, not a meem. The rasm writes the noon bare and this script has no mark for the hum, so writing a plain meem would assert a consonant nobody says |
| `idgham_mutajanisayn_naqis` | the letter keeps its own sound and only its manner changes |
| every ikhfaa and every izhar | the outcome is a state of the noon already written, and no mark records it |
| `tafkheem` and `tarqeeq` | a colour on a sound; no glyph carries it |
| the tashil and the ishmam mark | the mark is what the reciter reads, so the source spelling is the recited spelling |
| the sakt mark | it instructs the reciter rather than advising him, so it survives where row 30's sign would not have |
| the qalqala echo | a release rather than a letter, and the recited text does not write it |

### 4.8 What the table adds up to

| | |
|---|---|
| deleted | 11 |
| inserted | 7 |
| substituted | 6 |
| spelled out | 3 |
| reclassed | 2 |
| kept against expectation | 2 |
| **transformations** | **31** |
| cases examined and unchanged | 9 |
| transformations reachable through no rule instance | 10 |
| orthographic | 10 |
| performance | 20 |
| advice | 1 |
| boundary-dependent | 21 |

The ten with no owner are rows 2, 5, 9, 11, 12, 25, 26, 29, 30 and 31. Two of
them are missing rules rather than transformations no rule should own: dropping
the word-initial shadda at ibtidaa (row 9) and the word-final role flip at a
pause (row 29) are both mandatory and neither has a name in
[01-contract](01-contract.md) section 7 or a converse trigger in
[02-gate](02-gate.md) section 4.8. Row 12 has no owner for a different reason:
a consonant the rasm leaves bare has a vowel that is absent joined and stopped
alike, so no `pausal_sukun` instance exists to claim the sukun the recited text
writes there. Row 4 shares row 3's owner, which is the other half of one
problem: one rule, two behaviours, and nothing in the instance says which.

---

## 5. Digital Khatt

The motivating consumer reads the Digital Khatt script rather than the Uthmani
rasm. Seven of the transformations it performs are script repairs and have no
place in this catalogue, and a reader comparing the two should know which.

| Its transformation | The Uthmani position |
|---|---|
| an alif maqsura is respelled as a yaa where the letter sounds as a yaa | **no analogue.** Uthmani writes `ى` throughout, and the role is a fact of the unit. Row 29 is the general case |
| a dagger alif is inserted into the divine name | the same fact. The Uthmani rasm writes no dagger on this word either, so row 16 is an insertion in both scripts |
| an iqlab is written as a plain vowel plus a small meem | a script that marks the hum. Uthmani writes neither mark, so the noon stands bare and the rule is the only record |
| a tatweel seats a dagger alif | cosmetic; Uthmani seats its daggers on the letter |
| precomposed hamza seats are decomposed | encoding only |
| a stop sign attaches with no preceding space | cosmetic |
| a deletion is written as an invisible combining mark rather than removing the character | **not a domain fact at all.** It exists so that string length stays stable and colour offsets keep pointing at the right characters |

The last one is the shape of the problem this design removes. A consumer that
can only hand its renderer one string plus a list of offsets cannot delete a
character without invalidating every offset, so it substitutes an invisible
mark, then shifts the offsets by a running total, then discovers that a shifted
offset has no way of knowing that an inserted character belongs to a rule. Its
answer is to ship a second array of offsets computed against the modified text.
That second array is `rendered` and its pairings, invented by a consumer that
did not have them.

Everything else that consumer does appears in section 4. In particular, writing
a sukun onto a bare final noon or meem is **not** a Digital Khatt artefact: the
Uthmani rasm leaves those letters bare for the same reason, and row 12 is the
general case.

---

## 6. The control surface

**No request field switches a transformation on or off.** The recited text is a
total function of `(ref, riwayah, script, variant, boundary plan)`, and one of
it exists per request.

Each candidate switch, and why it is not one:

| Candidate | Why not |
|---|---|
| keep or drop the stop advice | the consumer wants it kept and wants it outside the rule relation, which is row 30 and needs no setting |
| compact or expanded muqattaat | the consumer wants both at once, and `glyphs` beside `rendered` is both at once |
| show or hide the silences | the silences are on the source text, where they are always shown. Section 1 |
| show or hide the insertions | hiding them produces a text no reciter reads |
| source glyphs or recited glyphs | that is `glyphs` against `rendered`, not a setting |
| the recited spelling of a started-on hamza wasl | one spelling, section 1.1 |
| which words stop and start | already a request field, and a fact about the recitation rather than about the rendering |

Six of these transformations have an off position that produces an incoherent
text rather than a different one: the pausal sukun, the hamza wasl start, the
hamza wasl elision, the merger re-spellings, the iltiqa repairs and the
muqattaat expansion. A word cannot be stopped on with a full vowel and cannot
be started on with a vowelless letter, so a setting that produced one would be
publishing an error under a name.

The cost of a switch is not only its own combinations. [02-gate](02-gate.md)
section 4.5 states that under `text="recited"` no sound takes a gap pairing,
and section 4.7 that the writer is total for every insertion. Both are false
the moment any insertion can be suppressed, so a design with a switch has no
completeness law over the recited text. Determinism and transparency are
properties of a published enumeration, and that is what this document is.
