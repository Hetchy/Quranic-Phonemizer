# 07 - The rules

Status: **proposed**. Scope: Uthmani, Hafs.

Every rule, one row each. [01-contract](01-contract.md) section 7 names them
and groups them for reading; this document states what each one is about, what
it reaches, what it does, and how the two levels a consumer can read it at
relate. Recited spellings are named by their row in
[06-two-texts](06-two-texts.md) section 4 rather than restated.

---

## 1. How to read the matrix

| Column | Holds |
|---|---|
| **source** | the unit the rule is about, and the unit it is read against |
| **trigger** | what the rule read in order to fire, or `-` |
| **crosses** | `never` · `may` · `always` |
| **on the sound** | what the rule does to the sounds the units produce |
| **recited** | what the recited text writes, by its catalogue row |

**The trigger is not a field.** It is stated here because a reader wants to
know what fired a rule, and it is not on the instance because it is not the
same kind of thing twice: sometimes a unit after, sometimes one before,
sometimes the unit's own vowel, sometimes the boundary plan. The one second
participant an instance carries is `host`, and only a merger has one.

`on the sound` is stated in domain words, and each maps onto one edge family
that [01-contract](01-contract.md) section 5 defines: silencing and merging and
hosting are attributions, colouring and setting a length and naming are
modifiers, and producing nothing is a rule that owns neither.

---

## 2. The matrix

### 2.1 The nasal letters

| Rule | Source | Trigger | Crosses | On the sound | Recited |
|---|---|---|---|---|---|
| `ikhfaa_haqiqi` | a sakin noon, or a tanween's noon | the ikhfaa letter | always for a tanween, may otherwise | the noon's consonant is a hum | unchanged |
| `iqlab` | a sakin noon, or a tanween's noon | the following baa | always for a tanween, may otherwise | the noon's consonant is a hum made at the lips | unchanged |
| `idgham_bi_ghunnah` | a sakin noon, or a tanween's noon | the following letter | always | the noon merges into the host, which is held | rows 7 and 18 |
| `idgham_bila_ghunnah` | a sakin noon, or a tanween's noon | the following lam or raa | always | the noon merges into the host | rows 7 and 18 |
| `izhar` | a sakin noon, or a tanween's noon | a throat letter, the waw or yaa of its own word, or the end of a spelled name | may | names the noon's own sound | unchanged |
| `ghunnah_mushaddadah` | a geminate noon or meem | - | never | names its own held sound | unchanged |
| `izhar_shafawi` | a sakin meem | the following letter, or the end of a spelled name | may | names the meem's own sound | unchanged |
| `ikhfaa_shafawi` | a sakin meem | the following baa | always | the meem is held | unchanged |
| `idgham_shafawi` | a sakin meem | the following meem | always | the meem merges into the host, which is held | rows 7 and 18 |

`iqlab` substitutes a unit and does not merge one: the baa is untouched and no
sound is shared. The recited text writes the rasm unchanged where the noon is
written, because the Uthmani rasm has no iqlab mark and a plain meem would
assert a consonant nobody says. Where the noon is a tanween's, the recited
text spells the two units apart and the noon is bare, which is
[06-two-texts](06-two-texts.md) section 4.1a for every noon rule at once.

`ikhfaa_shafawi` and `idgham_shafawi` never fire inside a word: a quiescent
meem meets a baa or a meem only across a boundary, and a meem doubled inside a
word is written with a shadda and is `ghunnah_mushaddadah`. `izhar_shafawi` has
no such limit and fires wherever a sakin meem meets any other letter, which is
inside a word as often as across one.

**A spelled name is closed.** A unit whose `origin` is `muqattaat` takes no
rule from outside the word it is in and gives none to the word after it. Its
letters are names being recited, not a word being read, so they are said the
same whether the plan joins or stops. The rules of the opening still fire
between its own names -- the seen of طسٓمٓ merges its noon into the following
meem, and the ain of عٓسٓقٓ hums its noon before the seen.

The last unit of the last name is said plainly, and the rule that names it is
the plain-articulation rule of its own letter: `izhar` where the name ends in a
noon, `izhar_shafawi` where it ends in a meem. That is the third trigger in
each of their rows, and it is what keeps the converse laws whole -- a sakin
meem joined to a following consonant still owns a rule at `الٓمٓ` and `طسٓمٓ`
and `حمٓ`.

Three sites are disputed and none is wired: the noon of `نٓ` and of `يسٓ`
before a following waw, and the meem of `الٓمٓ` before `ٱللَّهُ`. Each is a
khilaf point rather than an exception to this law, so the closed reading is
what the default document states and a selection is what changes it.

### 2.2 Adjacent consonants

| Rule | Source | Trigger | Crosses | On the sound | Recited |
|---|---|---|---|---|---|
| `idgham_mutamathilayn` | the first of two identical consonants | the second | may | merges into the host | rows 7 and 18 |
| `idgham_mutaqaribayn` | the first of two close consonants | the second | may | merges into the host | rows 7 and 18 |
| `idgham_mutajanisayn_kamil` | the first of two homorganic consonants | the second | may | merges into the host | rows 7 and 18 |
| `idgham_mutajanisayn_naqis` | the first of two homorganic consonants | the second | may | names the pair; the sound is unchanged | unchanged |
| `lam_shamsiyyah` | the article's lam | the following letter | never | merges into the host | row 8 |
| `lam_qamariyyah` | the article's lam | the following letter | never | names the lam's own sound | unchanged |

A `lam_shamsiyyah` and a cross-word idgham are the same edge shape and differ
in what the recited text writes: the rasm already doubles the sun letter, so
row 8 deletes and adds nothing, where row 18 has a shadda to add.

### 2.3 Length

The source is the unit whose vowel the rule lengthens. The trigger is what
caused it, and for two of them it is the boundary plan rather than a unit.

| Rule | Source | Trigger | Crosses | On the sound | Recited |
|---|---|---|---|---|---|
| `madd_tabii` | the unit whose vowel is long | - | never | hosts the merged vowel | rows 16, 17, 26, 27, 29 |
| `madd_wajib_muttasil` | the unit whose vowel is long | the hamza in the same word | never | names the length | as above |
| `madd_jaiz_munfasil` | the unit whose vowel is long | the hamza that begins the next word | always | names the length | as above, and row 2 when the plan stops |
| `madd_lazim` | the unit whose vowel is long | the unit whose permanent sukun or gemination follows | never | names the length | as above |
| `madd_arid_lil_sukun` | the unit whose vowel is long | the unit the stop silenced | never | names the length | as above |
| `madd_leen` | the unit whose waw or yaa has no vowel and follows a short a | the unit the stop silenced | never | names the sound | unchanged |
| `iltiqa_shortening` | the unit whose long vowel shortens | the sakin it met | always | sets the length to short | row 10 |

`madd_leen` names rather than lengthens, because a leen is not a long vowel:
its waw or yaa is silent and the vowel before it stays short.

Row 29's `madd_tabii` is a merger rather than a direct realization, so its
source is the glide that disappears -- a stopped word-final waw or yaa after
its matching short vowel -- and the host is the unit whose vowel it lengthens,
the same convention every merger uses.

### 2.4 Release

| Rule | Source | Trigger | Crosses | On the sound | Recited |
|---|---|---|---|---|---|
| `qalqala_sughra` | a qalqala letter whose vowel is absent | - | never | adds a release beside the consonant | unchanged |
| `qalqala_kubra` | the same, word-final at a stop | - | never | adds a release | unchanged |
| `qalqala_akbar` | the same, word-final and geminate at a stop | - | never | adds a release | unchanged |

The three are one phenomenon at three degrees and are three rules because the
degree is what a consumer names. A release is an addition, so the consonant
still states its own realization beside it.

### 2.5 Colour and manner

| Rule | Source | Trigger | Crosses | On the sound | Recited |
|---|---|---|---|---|---|
| `tafkheem` | the unit whose sound is heavy | - | never | makes the sound heavy, and the vowel of the same unit with it | unchanged |
| `tarqeeq` | the unit whose raa is light | - | never | names the sound | unchanged |
| `imala` | the unit whose vowel tilts | - | never | names the vowel's quality | unchanged |
| `tashil` | the unit whose hamza is eased | - | never | names the sound | unchanged |
| `ishmam` | the unit the reciter rounds his lips on | - | never | produces nothing | unchanged |

`tafkheem` is the only rule that names more than one sound of its own unit: the
consonant is heavy and the vowel it governs is heavy with it, and both are
sounds of the source. Its trigger is inside the unit, which is why the column
is empty.

### 2.6 Boundary

| Rule | Source | Trigger | Crosses | On the sound | Recited |
|---|---|---|---|---|---|
| `hamza_wasl_start` | the word-initial unit whose consonant sounds only when started on | - | never | hosts the consonant and its vowel | rows 13 and 24 |
| `hamza_wasl_elision` | the same unit, not started on or not word-initial | - | never | silences both parts | row 6 |
| `iltiqa_kasra` | the unit the reading vowels | - | always | hosts a vowel on a part the canon leaves absent | row 14 |
| `pausal_sukun` | the unit whose part the stop takes | - | never | silences the part | rows 1, 12, 19, 20 |
| `iwad` | a tanween's noon whose fathatan lengthens at a stop | - | never | silences the consonant | rows 15, 21, 28 |
| `taa_marbuta_pausal` | the taa marbuta unit | - | never | realizes the letter as a haa | row 22 |
| `fakk_idgham` | the word-initial unit a cross-word merger would have geminated | the letter before it, unjoined because the reading starts here | always | names the unit's own plain sound | row 9 |

`pausal_sukun` reaches the most catalogue rows of any rule, and the reason is
that it is one event with several spellings: the haraka it takes may be a
haraka, a tanween, a silah mark or nothing written at all, and the sukun it
writes is a replacement in the first three cases and an addition in the
fourth.

`iwad` is a separate rule and not a case of it, because nothing is lost. The
other three tanween at a stop lose their noon and write a sukun; a fathatan's
noon becomes the length in front of it, so the unit before gains a long vowel
where the others gain nothing. A rule named for what a stop takes may not be
the rule for the one stop that takes nothing.

`fakk_idgham` reads the same tables as the noon, meem and adjacent-consonant
merge families, from the other side: a word-initial letter the merge would
have geminated, checked against the letter before it regardless of whether
this reading joins into it. It fires only where that check holds and the
reading starts here instead, so it and the merger it mirrors never both fire
on the same pair.

`iltiqa_kasra` is the only rule that sounds a part the canon leaves absent, and
the only one whose letter-level relation exists on one text and not the other.
See section 6.

### 2.7 Substitution and orthography

| Rule | Source | Trigger | Crosses | On the sound | Recited |
|---|---|---|---|---|---|
| `ibdal_hamza` | the unit whose quiescent hamza the reading substitutes | - | never | the letter is realized as the vowel letter of the vowel before it | row 23 |
| `orthographic_silence` | see section 5 | - | never | produces nothing | rows 3 and 4 |

---

## 3. Every merger

A merger is the only place two units share one sound, so which unit hosts is
stated per rule rather than reasoned about.

| Rule | Host | Crosses a word |
|---|---|---|
| `idgham_mutamathilayn` | the second of the two | may |
| `idgham_mutaqaribayn` | the second of the two | may |
| `idgham_mutajanisayn_kamil` | the second of the two | may |
| `idgham_bi_ghunnah` | the following letter | always |
| `idgham_bila_ghunnah` | the following lam or raa | always |
| `idgham_shafawi` | the following meem | always |
| `lam_shamsiyyah` | the following letter | never |

The host owns the sound and the source has a `MergedInto` edge to it. Across a
boundary the host's word owns it, so a merged sound is never credited to the
word that lost it, and a consumer animating whole words reads a sound in the
second word that the first word's letter helped make.

Two rules look like mergers and are not. `idgham_mutajanisayn_naqis` keeps the
letter's own sound, so no sound is shared: the letter loses its own place of
articulation and keeps its heaviness, and this model has no manner axis to
record that on, so the instance owns a `Classifies` and changes nothing. A
notation that wanted to write a naqis letter differently has the instance
already sitting there. `iqlab` substitutes one unit and leaves the following
baa untouched.

---

## 4. Teaching labels

Each is a true description of a configuration the graph already states. They
are not rules and never mint an instance of their own: each names the trigger
rather than the outcome, and a second instance over one lengthening would leave
a sound with two rules claiming it. They are a field on the instance that did
happen.

| Label | Holds when |
|---|---|
| `madd_iwad` | a madd on the unit before a noon that `iwad` silenced |
| `madd_badal` | a madd on a unit whose letter is hamza, and whose length the canon states |
| `silah` | a madd on a unit whose vowel is long joined and absent stopped |
| `silah_kubra` | the same, where the rule is `madd_jaiz_munfasil` |

The length is always the rule's. A silah kubra is a `madd_jaiz_munfasil` on a
silah vowel and takes that rule's length; a badal in this reading is the length
of a `madd_tabii`, so it names a configuration rather than setting one.

`ibdal_hamza` is a rule and not on this list, because substituting a hamza for
a vowel is an outcome. Madd badal is the length that follows it.

`iwad` and `madd_iwad` are a rule and a label with nearly one name, and they
are two things: the rule is what happened to the noon, the label is what to
call the length beside it. The label is on the madd instance, the rule is on
the noon, and neither claims the other's unit.

---

## 5. Silence the script writes

`orthographic_silence` names a letter the rasm carries and recitation never
says: the alif of the plural waw, the alif no vowel can carry, the otiose waw,
the yaa and the alif maqsura. One rule, because `letter` says which.

The verdict is a canonical fact. Which evidence a script offered for it - a
written silence sign in Uthmani, position alone elsewhere - is the script
adapter's business, and a script that marks nothing owes its adapter the
derivation. Uthmani's is correct today.

The instance owns no attribution, because there is no unit to silence, so it
joins `ishmam` as a rule that produces nothing. The seat is in its
pairing's `silent` and the pairing's `rules` names this instance. That pairing
is the only place the instance is reachable from, which makes it the one rule
whose entire relation to the document is at the letter level.

Its two behaviours are catalogue rows 3 and 4, and `letter` does not tell them
apart: an alif the rasm never says and an alif the rasm says only at a pause
are the same letter in the same position, distinguished by the sign written
over them.

---

## 6. The letter level and the phoneme level

A rule can be read two ways. At the **phoneme level** it is `source` and
`host`, and the attribution and modifier edges that reach the sounds those
units produce. At the **letter level** it is a member of some pairing's
`rules`, reached from the glyphs.

**The two agree exactly when the rule's source unit has a glyph that supplies
one of its facts, and that glyph is in the source unit's own word.** Then the
pairing holding the glyph names the instance, the instance names the unit, and
reading up or down gives one answer. That is most of the corpus.

Six cases where they do not agree. Each is a real shape of the domain and none
is a defect to be repaired.

| | The divergence | Phoneme level | Letter level |
|---|---|---|---|
| 1 | **many units, one glyph** - a muqattaat opening | the rule's source is a unit whose `origin` is `muqattaat`, and a spelled name has several | one glyph spells one whole name, and the sounds under it are ordered, so a rule reaches the sounds it made and not a range of characters |
| 2 | **one unit, no glyph** - the tanween's noon | the noon is the `source` of every noon rule when `origin` is `tanween` | the instance is reached through the tanween mark, which also supplies the previous unit's vowel. One scalar shows two units' facts, so colouring the noon and colouring the vowel colour the same character |
| 3 | **one sound, two words** - a cross-word merger | `source` and host are units in different words, and the host's word owns the sound | the instance appears in two pairings: the source glyph's, where the glyph is `silent`, and the host's, where the sound is owned. `shares` is what joins them |
| 4 | **a sound with no letter** - a release | the release is a separate sound hosted on the consonant part, beside that part's own realization | it has no glyph, so the base letter's pairing owns two sounds for one part, and the recited text writes nothing for it |
| 5 | **a sound with no glyph** - `iltiqa_kasra` | the vowel of a unit the canon leaves vowelless, and the only rule that sounds one | no source glyph states it, so the sound takes a gap pairing under `text="source"` and an ordinary one under `text="recited"`. The only rule whose letter-level relation differs between the two texts |
| 6 | **a glyph with no unit** - `orthographic_silence` | nothing to reach: no unit, no sound, no attribution | the seat's pairing carries the instance and the glyph. The exact inverse of case 5, and the relation exists only on the source side |

Case 1 is where a consumer expects to be stuck and is not. One compact glyph
spells one letter name, so the pairing is per glyph and the sounds under it are
ordered: `alif` is five sounds under the first glyph of a three-glyph opening,
and the `madd_lazim` of `laam` reaches that name's vowel and nothing else. A
consumer colouring by sound has the relation already. Only one that insists on
painting a sub-range of the compact glyph has to invent offsets, and the
recited text is where that consumer should be reading, because there the name
is spelled out and every sound has a glyph of its own.

Case 3 is the one that surprises. The sound is in the second word and it is
owned there. The letter level sees the rule twice: once on the first word's
glyph, which is `silent`, and once on the second word's, which owns the sound.
A highlight that follows only one of them lights half the rule.

Cases 5 and 6 together are why the recited text has its own pairings rather
than a list of edits over the source text: one rule is invisible to the source
glyphs and another is invisible to the recited ones, and a single array of
edits would have to hold both and could hold neither.
