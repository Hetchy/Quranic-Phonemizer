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
```

What is not said is on the row that does not say it. `pairing.silent` names the
glyphs, and each one names its rule twice over: a unit the reading silenced has
a `Silent` edge, and a letter the rasm carries and recitation never says has no
unit to silence, so its contribution names the rule instead.

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

`seen_sad` is published and has no sites in the shipped Hafs data, so nothing
selects it yet. The two nasal placement points are not here: see section 4.4.

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

**The divine name is not published.** It is a lexeme, not a recitation
process, and a word field naming it would let a consumer colour by lexical
identity, which is not what this document is for. Its heavy lam is on the
sounds, carrying a `tafkheem` and its modifier edge. Its light lam is not:
that case leaves no trace, because a light lam is the ordinary lam and no rule
fires to say so.

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

**Cardinality.** Six cells, four populated and two closed by a law: a
consonant that sounds only when started on is a word-initial elidable hamza,
and one that sounds only when joined is the yaa of 27:36, which a reader may
keep or drop at a pause. Neither is ever doubled, so `geminate` is true only
where `sounds` is `always`. `when_joined` has a single site in the corpus.

The vowel long only when joined is the pronoun haa's, and it is section
4.2.2's business. Nothing here is that.

The model keeps these two facts in one enum and the projection derives them.
That is `03-canonical-vocabulary` D3, and it holds: the enum can express every
combination that exists, and the coupling stops at the model's edge. What the
contract requires is that the consumer never sees it.

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

`quality`: `a` · `u` · `i` · `e`. The last is what imala tilts toward, and it
reaches a document only when the request selects it at `imala_quality`; under
the default reading no vowel in the corpus takes it.

### 4.3 `Glyph` and `RenderGlyph`

| Name | Means |
|---|---|
| `word` | index into `words`, or absent when structural |
| `char` | the Unicode scalar |
| `kind` | below |
| `word_index` | ordinal within its word |
| `source_index` | ordinal in the whole passage |

`RenderGlyph` adds `from_glyphs`: the source glyphs it renders, empty when the
source has none. It is a tuple because the mapping is many-to-many in both
directions, which is what section 2's last row is about, and a recited row
needs no second list of source glyphs: it reads them through here.

| `kind` | Is | In `rendered` |
|---|---|---|
| `base` | a letter of the rasm | may change letter: a quiescent hamza becomes a vowel letter |
| `haraka` | fatha, damma, kasra | added at a started-on hamza wasl, dropped at a stop |
| `tanween` | the doubled haraka | dropped at a stop, and may leave an alif |
| `shadda` | doubling | unchanged |
| `vowel_letter` | alif, waw or yaa carrying length | added where the rasm omits one; occurs in `rendered` only |
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
| `ghunnah` | `emphatic` |
| `release` | `kind` |

A ghunnah is the hum an ikhfaa or an iqlab leaves where the noon was. It
belongs to no letter, which is why it is its own kind; `ghunnah` on a
consonant means the letter is held instead. It has no place of articulation:
one value would be a place and the other would be "wherever the next letter
is", and which of the two a reciter produces is a khilaf the shipped data does
not yet site. `release.kind` is `qalqala`.

**The consonant's cardinality.** `ghunnah` is true only where `geminate` is,
because a held consonant is one a merger doubled, and it occurs on four
letters: noon, meem, waw, yaa. Every other combination of the three booleans
is attested, except `ghunnah` with `emphatic`, which is the heavy ghunnah of
[04-open-questions](04-open-questions.md) section 1.

A sound has no `word` field: its word is the word of its primary origin.

### 4.5 `RuleInstance`

| Name | Means |
|---|---|
| `rule` | section 7 |
| `source` | the unit the rule is about |
| `target` | the unit it reaches, or absent |
| `labels` | teaching names for this instance, section 7.3 |

`source` means the same for every rule, and a rule is read against its
`source`: a lam shamsiyyah belongs to the lam that disappears, not to the
letter that doubles. Nothing in the corpus has a third participant. There is no family and no phase: the grouping in section 7 is for
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
| `Hosts(unit, part, sound, by?)` | the unit | this unit produces this sound |
| `MergedInto(unit, part, sound, by?)` | the unit | this unit disappeared into that sound |
| `Silent(unit, part, by)` | the unit | this unit lost its sound |
| `Insertion(anchor, part, sound, by?)` | nobody | a sound no unit owns |
| **modifiers** | | |
| `Recolours(sound, by)` | the rule | tafkheem made this consonant heavy |
| `SetsLength(sound, by, length)` | the rule | iltiqa shortened this madd |
| `Classifies(sound, by)` | the rule | names this sound without changing it |
| **contributions** | | |
| `Contribution(glyph, text, sounds, rules)` | the glyph | what this glyph puts on the page |

One unit per attribution. Two units never own one sound jointly: a merger is
already a pair of edges over one sound, which is what carries the sharing, and
a long vowel is shared by *graphemes*, which the spelling and contribution
edges carry.

An insertion has no side. The one sound in the design that no unit owns is the
helping vowel of an iltiqa, and it lands after its anchor.

`Recolours` carries no value. Emphasis is the only feature a rule sets, only
one rule sets it, and the resulting state is `emphatic` on the sound; the edge
exists to say which rule put it there. A light letter is the ordinary letter
and no rule fires, so there is nothing for a second value to mean. `length` is
`short` or `long`.

`Supplies.fact`: `letter` · `consonant` · `vowel_quality` · `vowel_length` ·
`tajweed_mark`. Quality and length are separate facts, because otherwise a
haraka and its carrier make the identical claim about the identical unit and
section 6.1 cannot be evaluated. Sakt is not a unit-level fact: it is stated
on the word.

### 5.1 `Contribution`

Ownership in section 6.1 says which pairing *owns* a sound. This says which
glyphs *show* it, which is the join a colouring consumer needs and the only
place a glyph that shows nothing is distinguished from one nothing looked at.

```python
@dataclass(frozen=True)
class Contribution:
    glyph:  int                # index into glyphs, or into rendered
    text:   str                # "source" or "recited": which array glyph indexes
    sounds: tuple[int, ...]    # the sounds this glyph puts on the page
    rules:  tuple[int, ...]    # rule instances it shows that no sound carries
```

`sounds` is empty for a glyph the reading does not say, and `rules` then names
why: an `orthographic_silence`, a `pausal_sukun`, a merger. A glyph with both
lists empty is a defect, not a state.

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

### 6.3 What a cluster is, and what a pairing is not

A muqattaat glyph is one cluster row owning the sounds of a whole letter name.
That is the granularity a font shapes and the granularity this grouping is
named for; a consumer animating inside the name reads the units, which are
already there and already ordered.

Pairings are request-local and will never take a durable key. A consumer
persisting records against them keys on position and defends against drift
with a content snapshot, which is the right shape for content that changes.

### 6.4 Word-by-word

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

### 7.3 Teaching labels

Each is a true description of a configuration the graph already states. They
are not rules and never mint an instance of their own: each names the trigger
rather than the outcome, and a second instance over one lengthening would
leave `by` with two answers. They are a field on the instance that did happen.

`labels` is a subset of:

| Label | Holds when |
|---|---|
| `madd_iwad` | a madd on a unit whose tanween noon is silenced at a stop |
| `madd_badal` | a madd on a unit whose letter is hamza |
| `silah` | a madd on a unit whose vowel is long joined and absent stopped |
| `silah_kubra` | the same, where the rule is `madd_jaiz_munfasil` |

The length is always the rule's. A silah kubra is `madd_jaiz_munfasil` on a
silah vowel and takes that rule's length; a badal in this reading is the
length of a `madd_tabii`, which is why it is a name and not a rule.

`ibdal_hamza` is a rule and not on this list, because substituting a hamza for
a vowel is an outcome. Madd badal is the length that follows it.

### 7.4 Silence the script writes

`orthographic_silence` names a letter the rasm carries and recitation never
says: the alif of the plural waw, the alif no vowel can carry, the otiose waw,
the yaa and the alif maqsura. One rule, because `letter` says which.

The verdict is a canonical fact. Which evidence a script offered for it - a
written silence sign in Uthmani, position alone elsewhere - is the script
adapter's business, and a script that marks nothing owes its adapter the
derivation. Uthmani's is correct today.

The instance owns no attribution - there is no unit to silence - so it joins
`ishmam` and `sakt` as a rule that produces nothing. The seat's contribution
shows no sound and its `rules` names this one.

---

## 8. Laws a consumer can check

| |
|---|
| Every glyph appears in exactly one pairing of its text, unless it is structural |
| Every sound appears in exactly one pairing's `sounds`, and any number of `shares` |
| Every unit states one realization per applicable part: hosted, merged, or silent |
| Every sound has one primary origin: a `Hosts` or an `Insertion` |
| Every merger is a `Hosts` and `MergedInto` pair sharing sound and rule |
| Every silence names a rule |
| Concatenating `glyphs` in `source_index` order reproduces the source text |
| Under `text="recited"`, no sound takes a gap pairing |
| Every non-structural glyph, of either text, has exactly one contribution |

A part is applicable unless the unit's vowel is absent in both forms, which is
a unit the reading never vowels: it has nothing for a rule to take and states
no vowel realization. That covers the sukun, the bare consonant, the tanween's
noon and a letter of a spelled name alike. The consonant part is always
applicable.

---

## 9. What the producer must build

The contract states what is right; where the model disagrees, the model
changes.

**Model shape**

1. **The consonant's two facts are derived, not split.** The projection
   publishes `geminate` and `sounds`; the model keeps one enum, because it can
   express every combination that exists. Manner is not published at all: an
   eased hamza is a rule and already is one.
2. **The modifier edge survives into the document.** A recolour and a length
   change are engine effects today, applied to the sound and then dropped, so
   the rule that made them owns nothing. `tafkheem` is the largest instance
   class in the corpus and every one of its instances is currently empty.
   `Classifies` is the third modifier and it has never existed at all: it is
   the edge every classification-only rule needs, and those are the majority
   of the instances that own nothing, `tarqeeq` and `madd_arid_lil_sukun` and
   `lam_qamariyyah` among them.
3. **`silah` names two unrelated things** - a consonant present only when
   joined, and a vowel long only when joined - on two types.
4. **The vowel becomes a joined form and a stopped form.** Five named variants
   collapse to two fields over one small value set, and the base a fathatan
   lengthens becomes a data change rather than a new variant.
   The seven alifs must be sited **by word location**, not by vocalised
   skeleton: the tail of `جَآءَنَا` spells what `أَنَا۠` spells and its final
   alif is an ordinary pronoun, and 76:15 `قَوَارِيرَا۠` and 76:16
   `قَوَارِيرَا۟` are the same letters and harakat with opposite behaviour,
   told apart by a silence sign no skeleton keeps. Today the
   boundary-conditional
   vowel has no effect on any token, so this item is the first to change one:
   it corrects every `أَنَا۠` in the corpus, which is long when joined today
   and should be short, and `02-gate` section 1 requires those refs be
   allowlisted before the change lands.
5. **`origin` replaces two booleans**, which today admit an impossible state.
6. **`Supplies.fact` distinguishes quality from length.** Without it a haraka
   and its carrier make identical claims and ownership cannot be evaluated.
7. **The rule family and phase leave the model.** Three readers must be
   replaced first, and one changes recitation: qalqala asks the family whether
   a slot was assimilated from.
8. **Delete the plain rule and make `by` optional.**
9. **Rename the parts** to `consonant` and `vowel` throughout.
10. **`Participants` are labelled.** A rule's units are a source and a target,
    and today the pair is positional.

**Facts the model drops**

11. **Marks that reach no unit.** The largest group is the alif seating a
    fathatan, skipped although it sounds at a pause and every iwad case needs
    it. Then the superscript alif over a written carrier, the sakt mark, the
    combining hamza above, and the rectangular zero.
12. **The separator between words is a glyph.** A space inside a word's own
    text is emitted; the one between two words is not, so the concatenation
    law passes only on a single-word verse.
13. **One scalar, one glyph.** One verse emits a combining mark twice, and
    duplicate spelling edges exist for every alef wasla and every tatweel.
14. **One notion of structural, and it is the `Structural` edge.** The class
    and the edge disagree in both directions: a tatweel is classed structural
    and carries no edge, a stop sign carries the edge and is classed as
    advice. Both move to the edge, and section 4.3 follows: `stop_sign` keeps
    its own `kind` and takes no pairing, and a tatweel takes none either.
15. **The dagger and its carrier are reversed.**
16. **`length_carrier` is a class nothing assigns.** No scalar classifies as
    one, and the recited spelling is where a length carrier is added.
17. **Sakt is a word fact and is evidenced by nothing.** The unit-level fact
    exists in the model and no glyph supplies it.

**Rules with no producer**

18. **Madd rules for their ordinary cases.** `madd_tabii` is minted only on
    the pausal glide; an ordinary long vowel, a silah vowel and a stopped
    seven-alif produce none.
19. **`orthographic_silence`.** The seats are identified, but the field naming
    the unit each shows against is written and never read, and one seat class
    reaches no spelling edge at all.
20. **The iltiqa helping vowel** is constructed nowhere. It is one insertion,
    at a handful of sites, and it is the only sound in the design no unit owns.
21. **Split the boundary rules to match the names.** One code rule covers
    `pausal_sukun` and `taa_marbuta_pausal`; another mints an iwad name the
    contract does not have.
22. **Release attribution moves to the consonant** - and the fill step reads
    any realization as claiming the part, so moving only the effect deletes
    the consonant's own sound. Every release in the corpus sits on the vowel
    today, so this is not a repair at the margin.

**Machinery**

23. **A writer for the recited text.** The one that exists takes a Score, so
    it has no boundary plan and no performance and cannot spell a pausal,
    merged or started-on form. `rendered` needs glyph records carrying
    `from_glyph` and their own contribution rows.
24. **Total glyph contribution.** The join saying which outcomes each glyph
    presents, distinguishing a sounded dagger from its silent carrier and a
    performance deletion from orthographic zero.
25. **Sub-verse requests.** A request clipping a ledger-addressed word raises
    rather than building.
26. **Continuous assembly** overlaps by two words, because cross-word
    lookahead reaches past a one-slot word.
27. **Request orchestration.** Resolve `(ref, boundaries, variant)`, build,
    perform, and assemble one index space. Internal starts, arbitrary stops,
    sakt and cross-verse joins use the same path.
