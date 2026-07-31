# 01 - The public contract

Status: **proposed**. Scope: Uthmani, Hafs.

This document is self-contained. Every value space it publishes is enumerated
here, so a consumer never reads `model/` and a reviewer sees a missing case
rather than arguing about one. Where an enumeration disagrees with the model
today, the contract is what is right and section 9 carries the change.

Two projections, and no third.

| Name | Shape | For |
|---|---|---|
| `phonemes` | ordered tokens, with word boundaries | consumers that want only sound |
| `Mappings` | identified nodes plus typed relation arrays | every script, alignment, and tajweed consumer |

They are never joined; a consumer picks one. `phonemes` stays separate because
the token stream is stable across every schema evolution of the graph.

---

## 1. Read this much and stop

```python
m = mappings("2:255")

m.rules                                          # every rule, in reading order
m.alignment(text="source", grouping="cluster")   # writing lined up with sound
m.silences()                                     # what is not said, and why
```

Section 6 is the whole of `alignment`. Everything past section 4 is for a
consumer that needs a join no method offers.

---

## 2. The four things a consumer wants, and their six pairings

| | |
|---|---|
| **script** | what the mushaf wrote |
| **recited** | what recitation spells |
| **sound** | what is heard |
| **rules** | what happened, and why |

Every question is a relationship between two of them.

| Pairing | Answered by |
|---|---|
| script - sound | `alignment(text="source")`, `pairing.sounds` |
| script - rules | `alignment(text="source")`, `pairing.rules` |
| recited - sound | `alignment(text="recited")`, `pairing.sounds` |
| recited - rules | `alignment(text="recited")`, `pairing.rules` |
| sound - rules | `m.rules`, and `by` on every attribution and modifier |
| **script - recited** | `pairing.rendered` beside `pairing.glyphs`, on one row |

The last is what a diff view or a two-line teleprompter needs, and the only
one many-to-many in both directions: a recited cluster can cover two source
glyphs, and one source glyph can render as two. It is a column on the same
row, not a fifth call.

---

## 3. Identity

```python
@dataclass(frozen=True)
class Mappings:
    ref: str
    riwayah: Riwayah
    script: Script
    variant: VariantSelection
    schema_version: str
    canon_digest: str

    words:    tuple[Word, ...]
    glyphs:   tuple[Glyph, ...]
    rendered: tuple[RenderGlyph, ...]
    units:    tuple[Unit, ...]
    sounds:   tuple[Sound, ...]
    rules:    tuple[RuleInstance, ...]

    spellings:     tuple[SpellingEdge, ...]
    attributions:  tuple[AttributionEdge, ...]
    modifiers:     tuple[ModifierEdge, ...]
    contributions: tuple[Contribution, ...]
```

| Field | Means |
|---|---|
| `ref` | the passage: `"2:255"`, `"2:255:3-2:256:1"`. Addresses words, not only verses |
| `riwayah`, `script` | which transmission, which mushaf |
| `variant` | which reading was taken at each disputed point |
| `schema_version` | the shape of this document |
| `canon_digest` | identifies the canonical data the indices were resolved against |

Six fields, all flat. No envelope groups them: a reader who must decide
whether a field is domain or infrastructure before reading it has been handed
a puzzle rather than a document.

**There is no notation field.** One notation ships, and a consumer supplying
its own tokens knows which it supplied.

### 3.1 Variants

A `VariantSelection` is a list of choices, because a reading can differ at
several points and a reciter may take one wajh throughout and another in a
single word.

```python
VariantSelection(options=(Option(khilaf, site, name), ...))
```

A choice naming a site outranks one naming the whole point.

| `khilaf` | Disputes |
|---|---|
| `seen_sad` | which letter is read where the rasm allows both |
| `raa_tafkheem` | whether a raa is heavy or light |
| `imala_quality` | the vowel imala tilts toward |
| `nucleus_vowel` | which vowel a position takes |
| `yaa_ithbat` | whether a pronoun yaa is pronounced at a pause |
| `iqlab_nasal` | where the iqlab hum is placed |
| `ikhfaa_shafawi_nasal` | where the ikhfaa shafawi hum is placed |

Indices are local to one document, and pairings are request-local.

---

## 4. Nodes

### 4.1 `Word`

| Name | Means |
|---|---|
| `location` | `surah:ayah:word` |
| `text` | the source word as written |
| `is_started_on` | recitation begins here |
| `is_stopped_on` | recitation pauses after this word. True for the last word of a request |
| `sakt_after` | neither starts nor stops, and blocks cross-word rules |
| `stop_sign` | one of the below, or absent |

`preferred_continue` · `preferred_stop` · `optional_stop` ·
`compulsory_stop` · `prohibited_stop` · `either_stop` · `permitted_stop`

### 4.2 `Unit`

One letter with the vowel state that follows it: the thing a rule fires on. A
unit is **not** a grapheme cluster - the tanween's noon is a unit no glyph
writes, and one muqattaat glyph makes several.

| Name | Values |
|---|---|
| `word` | index into `words` |
| `letter` | the twenty-eight, plus `hamza` and `taa_marbuta` |
| `consonant` | 4.2.1 |
| `vowel` | 4.2.2 |
| `origin` | `written` · `letter_name` · `tanween` |

`letter` is phonological, so there is no alif maqsura and no alef wasla -
those are spellings. `origin` is one field with three values rather than two
booleans, which would admit a fourth state that cannot exist.

**Cardinality.** Every unit has a consonant and a vowel. Neither is optional;
absence is a value of the vowel, not a missing field. A position that could
sound in no boundary state is not a unit.

#### 4.2.1 `consonant`

Two independent facts, because they combine.

| Field | Values | Means |
|---|---|---|
| `geminate` | true, false | the letter is doubled |
| `sounds` | `always` · `when_started_on` · `when_joined` | whether the consonant is there at all |

`when_started_on` is the hamza wasl, elided otherwise. `when_joined` is its
exact mirror. Manner is not here: an eased hamza is something a reciter does,
so it is a rule.

#### 4.2.2 `vowel`

A vowel has a **joined** form and a **stopped** form, each one of `absent`,
`short(quality)` or `long(quality)`. That is the whole of it.

| joined | stopped | Called |
|---|---|---|
| `absent` | `absent` | sukun |
| `short(q)` | `short(q)` | an ordinary haraka |
| `long(q)` | `long(q)` | an ordinary madd letter |
| `long(q)` | `absent` | the pronoun haa's silah |
| `short(q)` | `long(q)` | the seven alifs, and the base a fathatan lengthens |

Two fields instead of five named variants; the names become rows. A final
short vowel dropping at a pause is not here because it is a rule: the position
has a vowel and the stop takes it.

`quality`: `a` · `u` · `i` · `e`, the last being what imala tilts toward.

### 4.3 `Glyph` and `RenderGlyph`

| Name | Means |
|---|---|
| `word` | index into `words`, or absent when structural |
| `char` | the Unicode scalar |
| `kind` | below |
| `word_index` | ordinal within its word |
| `source_index` | ordinal in the whole passage |

`RenderGlyph` adds `from_glyph`: the source glyph it renders, absent when the
source has none.

| `kind` | Is | In `rendered` |
|---|---|---|
| `base` | a letter of the rasm | may change letter: a quiescent hamza becomes a vowel letter |
| `haraka` | fatha, damma, kasra | added at a started-on hamza wasl, dropped at a stop |
| `tanween` | the doubled haraka | dropped at a stop, and may leave an alif |
| `shadda` | doubling | unchanged |
| `vowel_letter` | alif, waw or yaa carrying length | added where the rasm omits one |
| `small_vowel` | the dagger alif, the mini waw and yaa | written full |
| `madd_sign` | the maddah | unchanged |
| `silence_sign` | the round and rectangular zeros | dropped: recitation does not write what it does not say |
| `tajweed_mark` | the imala, ishmam and tashil marks | unchanged |
| `stop_sign` | the mushaf's advice | dropped: advice is not recitation |
| `structural` | space, verse marker, tatweel | spaces kept, the rest dropped |

The recited spelling takes one policy, and it changes exactly one thing:

| `spelling` | A hamza wasl started on | Everything else |
|---|---|---|
| `faithful` | `ٱ` plus the helping haraka | identical |
| `explicit` | `أ` or `إ` per the vowel | identical |

### 4.4 `Sound`

| Name | Means |
|---|---|
| `token` | how this sound is written in the chosen notation |
| `kind` | `consonant` · `vowel` · `ghunnah` · `release` |

| `kind` | Fields |
|---|---|
| `consonant` | `letter`, `geminate`, `emphatic`, `ghunnah` |
| `vowel` | `quality`, `long`, `emphatic` |
| `ghunnah` | `place`, `emphatic` |
| `release` | `kind` |

`ghunnah.place` is `bilabial` for iqlab and `assimilated` for ikhfaa. That hum
belongs to no letter, which is why it is its own kind; `ghunnah` on a
consonant means the letter is held. `release.kind` is `qalqala`.

A sound has no `word` field: its word is the word of its primary origin.

### 4.5 `RuleInstance`

| Name | Means |
|---|---|
| `rule` | section 7 |
| `source` | the unit the rule is about |
| `target` | the unit it reaches, or absent |

`source` means the same for every rule. Nothing in the corpus has a third
participant. There is no family and no phase: the grouping in section 7 is for
reading, and a colouring scheme is a convention a consumer picks.

---

## 5. Edges

| Edge | Subject | Means |
|---|---|---|
| **spellings** | | |
| `Supplies(glyph, unit, fact)` | the glyph | supplies a canonical fact |
| `Witnesses(glyph, unit)` | the glyph | witnesses something without supplying a fact: a word-initial shadda |
| `Decorates(glyph, unit)` | the glyph | bound to the unit, supplying and asserting nothing: the maddah |
| `Structural(glyph)` | the glyph | belongs to no word |
| **attributions** | | |
| `Hosts(units, part, sound, by?)` | the units | these units produce this sound |
| `MergedInto(units, part, sound, by?)` | the units | this unit disappeared into that sound |
| `Silent(units, part, by)` | the units | this unit lost its sound |
| `Insertion(anchor, side, part, sound, by?)` | nobody | a sound no unit owns |
| **modifiers** | | |
| `Recolours(sound, by, feature, value)` | the rule | tafkheem made this consonant heavy |
| `SetsLength(sound, by, length)` | the rule | iltiqa shortened this madd |
| `Classifies(sound, by)` | the rule | names this sound without changing it |
| **contributions** | | |
| `presents` | the glyph | one row per non-structural glyph and per rendered glyph |

`Supplies.fact`: `letter` · `consonant` · `vowel_quality` · `vowel_length` ·
`sakt` · `tajweed_mark`. Quality and length are separate facts, because
otherwise a haraka and its carrier make the identical claim about the
identical unit and section 6.1 cannot be evaluated.

`Part` is `consonant | vowel`. Silence is not a third value: it is what
happened to one of the two, and it happens to both.

A merger **is** a `Hosts` and `MergedInto` pair sharing a sound and a rule. A
release is hosted on the consonant that makes it, and is an **addition**: the
part still states one realization and carries the echo beside it.

`by` is absent when no rule claimed the sound. There is no `plain` rule.

---

## 6. Alignment

```python
m.alignment(text="source"|"recited", grouping="glyph"|"cluster")
```

| | `text="source"` | `text="recited"` |
|---|---|---|
| `grouping="glyph"` | one pairing per source scalar | one per rendered scalar |
| `grouping="cluster"` | base letter plus the marks a font shapes with it | the same over the recited spelling |

```python
@dataclass(frozen=True)
class Pairing:
    glyphs:   tuple[int, ...]   # source glyphs
    rendered: tuple[int, ...]   # rendered glyphs
    sounds:   tuple[int, ...]   # the sounds this pairing owns
    shares:   tuple[int, ...]   # sounds it presents that another owns
    silent:   tuple[int, ...]   # its glyphs that are written and not said
    rules:    tuple[int, ...]
    after:    int | None        # set only on a gap pairing
```

`text` selects which array is partitioned; both are always populated, which is
what makes the script-recited pairing a column rather than a call.

`sounds` and `shares` make co-highlighting a field. A sound is timed once and
lights every pairing naming it in either list, so an idgham lights the
merged-away letter and its host, and a tanween lights its cluster and again
with the letter it merges into.

### 6.1 Ownership

Several glyphs can present one sound; exactly one pairing owns it.

1. the glyph supplying the sound's **length**;
2. otherwise the glyph supplying its **quality**;
3. for a merged sound, the first presenting glyph of the **host** unit;
4. otherwise the first presenting glyph in source order.

### 6.2 Gap pairings

A sound no glyph of the selected text presents takes a **gap pairing**:
`glyphs` empty, `after` naming the pairing it follows. The criterion is what
the text writes, not how the sound was attributed.

### 6.3 Word-by-word

Not a grouping. Every node carries its word and a merged sound's word is its
host's, so a consumer animating whole words reads which words a sound touches
and applies its own taste.

---

## 7. Rules

A rule name says what happened, never what triggered it: the trigger is data
on a node. Noon and tanween ikhfaa are one rule, and `origin` says which.

**The nasal letters.** `ikhfaa_haqiqi` · `iqlab` · `idgham_bi_ghunnah` ·
`idgham_bila_ghunnah` · `izhar_halqi` · `izhar_mutlaq` ·
`ghunnah_mushaddadah` · `izhar_shafawi` · `ikhfaa_shafawi` · `idgham_shafawi`

**Adjacent consonants.** `idgham_mutamathilayn` · `idgham_mutaqaribayn` ·
`idgham_mutajanisayn_kamil` · `idgham_mutajanisayn_naqis` · `lam_shamsiyyah` ·
`lam_qamariyyah`

**Length.** `madd_tabii` · `madd_wajib_muttasil` · `madd_jaiz_munfasil` ·
`madd_lazim` · `madd_arid_lil_sukun` · `madd_leen` · `iltiqa_shortening`

**Release.** `qalqala_sughra` · `qalqala_kubra` · `qalqala_akbar`

**Colour and manner.** `tafkheem` · `tarqeeq` · `imala` · `tashil` · `ishmam`

**Boundary.** `hamza_wasl_start` · `hamza_wasl_elision` · `iltiqa_kasra` ·
`pausal_sukun` · `taa_marbuta_pausal` · `sakt`

**Substitution.** `ibdal_hamza`

**Orthographic.** `orthographic_silence`

### 7.1 Every merger

A merger is the only place two units share one sound, so which unit hosts is
stated per rule rather than reasoned about.

| Rule | Source | Host | Crosses a word |
|---|---|---|---|
| `idgham_mutamathilayn` | the first of two identical consonants | the second | may |
| `idgham_mutaqaribayn` | the first of two close consonants | the second | may |
| `idgham_mutajanisayn_kamil` | the first of two homorganic consonants | the second | may |
| `idgham_bi_ghunnah` | a sakin noon or a tanween | the following letter | always |
| `idgham_bila_ghunnah` | a sakin noon or a tanween | the following lam or raa | always |
| `idgham_shafawi` | a sakin meem | the following meem | may |
| `lam_shamsiyyah` | the article's lam | the following letter | never |

The host owns the sound; the source has a `MergedInto` edge to it. Across a
boundary the host's word owns it, so a merged sound is never credited to the
word that lost it.

Two rules that look like mergers and are not. `idgham_mutajanisayn_naqis`
keeps the letter's own sound and changes only its manner.
`iqlab` turns a noon into a meem, which is one unit substituting, and leaves
the following baa untouched.

### 7.2 What a stop does

| | |
|---|---|
| a sound goes | `pausal_sukun` |
| a vowel lengthens | a madd rule |
| a letter is realized differently | `taa_marbuta_pausal` |

Mutually exclusive per unit and per part.

### 7.3 Teaching labels the contract does not mint

Each is a true description of a configuration the graph already states,
published as a predicate so a consumer does not rebuild it from prose.

| Label | Holds when |
|---|---|
| madd iwad | a madd on a unit whose tanween noon is silenced at a stop |
| madd badal | a madd on a unit whose letter is hamza |
| silah | a madd on a unit whose vowel is long joined and absent stopped |
| silah kubra | the same, where the rule is `madd_jaiz_munfasil` |

`ibdal_hamza` is a rule and not on this list, because substituting a hamza for
a vowel is an outcome. Madd badal is the length that follows it.

### 7.4 Silence the script writes

`orthographic_silence` names a letter the rasm carries and recitation never
says: the alif of the plural waw, the alif no vowel can carry, the otiose waw,
the yaa and the alif maqsura. One rule, because `letter` says which.

The instance owns no attribution - there is no unit to silence - so it joins
`ishmam` and `sakt` as a rule that produces nothing. The seat's `presents`
list is empty and its `reason` names this rule.

---

## 8. Laws a consumer can check

| |
|---|
| Every glyph appears in exactly one pairing of its text, unless it is structural |
| Every sound appears in exactly one pairing's `sounds`, and any number of `shares` |
| Every unit states one realization per part: hosted, merged, or silent |
| Every sound has one primary origin: a `Hosts` or an `Insertion` |
| Every merger is a `Hosts` and `MergedInto` pair sharing sound and rule |
| Every silence names a rule |
| Concatenating `glyphs` in `source_index` order reproduces the source text |
| Under `text="recited"`, no sound takes a gap pairing |

---

## 9. What the producer must build

The contract states what is right; where the model disagrees, the model
changes.

**Model shape**

1. **The consonant's two facts split.** Gemination and whether the consonant
   sounds are independent, and today they are five values of one enum in which
   two have a single site each.
2. **Manner leaves the consonant.** An eased hamza is a rule and already is
   one; it should not also be a state.
3. **`silah` names two unrelated things** - a consonant present only when
   joined, and a vowel long only when joined - on two types.
4. **The vowel becomes a joined form and a stopped form.** Five named variants
   collapse to two fields over one small value set, and the base a fathatan
   lengthens becomes a data change rather than a new variant.
5. **`origin` replaces two booleans**, which today admit an impossible state.
6. **`Supplies.fact` distinguishes quality from length.** Without it a haraka
   and its carrier make identical claims and ownership cannot be evaluated.
7. **The rule family and phase leave the model.** Three readers must be
   replaced first, and one changes recitation: qalqala asks the family whether
   a slot was assimilated from.
8. **Delete the plain rule and make `by` optional.**
9. **Rename the parts** to `consonant` and `vowel` throughout.

**Facts the model drops**

10. **Marks that reach no unit.** The largest group is the alif seating a
    fathatan, skipped although it sounds at a pause and every iwad case needs
    it. Then the superscript alif over a written carrier, the sakt mark, the
    combining hamza above, and the rectangular zero.
11. **Spaces are glyphs.** None are emitted, so the concatenation law cannot
    pass on any verse.
12. **One scalar, one glyph.** One verse emits a combining mark twice, and
    duplicate spelling edges exist for every alef wasla and every tatweel.
13. **One notion of structural.** A glyph class and a spelling edge disagree
    in both directions; the edge is the authority.
14. **The dagger and its carrier are reversed.**

**Rules with no producer**

15. **Madd rules for their ordinary cases.** `madd_tabii` is minted only on
    the pausal glide; an ordinary long vowel, a silah vowel and a stopped
    seven-alif produce none.
16. **`orthographic_silence`.** The seats are identified, but the field naming
    the unit each shows against is written and never read, and one seat class
    reaches no spelling edge at all.
17. **The iltiqa helping vowel** is constructed nowhere.
18. **Split the boundary rules to match the names.** One code rule covers
    `pausal_sukun` and `taa_marbuta_pausal`; another mints an iwad name the
    contract does not have.
19. **Release attribution moves to the consonant** - and the fill step reads
    any realization as claiming the part, so moving only the effect deletes
    the consonant's own sound.

**Machinery**

20. **A writer for the recited text.** The one that exists takes a Score, so
    it has no boundary plan and no performance and cannot spell a pausal,
    merged or started-on form. `rendered` needs glyph records carrying
    `from_glyph` and their own `presents` edges.
21. **Total glyph contribution.** The join saying which outcomes each glyph
    presents, distinguishing a sounded dagger from its silent carrier and a
    performance deletion from orthographic zero.
22. **Sub-verse requests.** A request clipping a ledger-addressed word raises
    rather than building.
23. **Continuous assembly** overlaps by two words, because cross-word
    lookahead reaches past a one-slot word.
24. **Request orchestration.** Resolve `(ref, boundaries, variant)`, build,
    perform, and assemble one index space. Internal starts, arbitrary stops,
    sakt and cross-verse joins use the same path.
