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
| the graph | identified nodes plus typed relation arrays | every script, alignment, and tajweed consumer |

One call answers both, and a consumer reads whichever it came for. `phonemes`
is a method rather than an array because the token stream is stable across
every schema evolution of the graph.

---

## 1. Read this much and stop

```python
r = Phonemizer().phonemize("2:255")

r.phonemes()                                  # every token, in reading order
r.rules                                       # every rule, in reading order
r.alignment(text="source", grouping="cell")   # writing lined up with sound
r.respelling(grouping="cell")                 # the two texts against each other
```

What is not said is on the row that does not say it. `pairing.silent` names the
glyphs, and each names its rule: a unit the reading silenced has a `Silent`
edge, and a letter the rasm carries and recitation never says has no unit to
silence, so its pairing names the rule instead.

Section 6 is the whole of `alignment` and `respelling`. Everything past
section 4 is for a consumer that needs a join no method offers.

### 1.1 The call

Configuration selects which data is loaded, so it is stated once, on the
instance. What varies per call is the passage and where the reader pauses.

```python
pm = Phonemizer(
    riwayah="hafs",
    script=None,              # defaults per riwayah; hafs is uthmani
    variants=None,            # section 3.1
    extra_phonemes=(),        # section 3.2
)

pm.phonemize(
    ref,                      # below
    stop_signs=(),            # stop at every word carrying one of these signs
    stop_refs=(),             # stop after these words
) -> PhonemizeResult
```

`Phonemizer()` bare is hafs uthmani under the default reading. No caller
constructs a model object: every argument is a string, a dict or a tuple of
them.

**The ref.** An endpoint is `surah[:ayah[:word]]`, and a ref is one endpoint or
two joined by a hyphen, both at the same depth.

```
"2"    "2:255"    "2:255-2:257"    "2:255:3"    "2:255:3-2:256:1"
```

There is no list of refs: two disjoint spans have no junction between them, so
a discontinuous request has no reading to describe.

**The boundaries.** A request always stops after its last word, so a passage
read alone is complete without naming any. Everything else about the reading
follows from where it pauses: which madd reverts, which noon merges, which
vowel the pause takes.

There is no `starts`. Where recitation begins is where it last stopped, so
`Word.is_started_on` is derived rather than asked for, and a passage started on
mid-ref is a stop before it. Sakt is not asked for either: it is a fact of the
word, and where it falls is data the riwayah carries rather than a request
field.

The two things that raise rather than guess: a `ref` outside the corpus, and a
`ref` that clips a word the riwayah's data addresses as a whole. A stop asked
for where the mushaf forbids one is not an error, because the reader is
allowed to be wrong and the document should say what that reading sounds like.

### 1.2 Names a person reads

Every rule has a display name in English and in Arabic, and they are part of
this contract rather than a consumer's table. `ikhfaa_haqiqi` is the
identifier and "Ikhfaa Haqiqi" with إخفاء حقيقي is what a legend prints.

```python
supported_riwayat()          -> ("hafs",)
available_variants("hafs")   -> section 3.1
tajweed_rules("hafs")        -> ((identifier, english, arabic), ...)
```

Three module functions and no more. `available_variants` has to answer before
an instance exists, because it is read to decide what to pass as `variants`.
Everything else a consumer might enumerate - which scripts a riwayah has, the
phoneme inventory, the glyphs of a script, a sentence explaining each rule - is
documentation, and a table in a document does not go stale the way a shipped
one does.

---

## 2. Three calls, and why they cover everything

A consumer wants four things and every question is a relationship between two
of them.

| | |
|---|---|
| **source** | what the mushaf wrote |
| **recited** | what recitation spells |
| **sound** | what is heard |
| **rules** | what happened, and why |

Four things make six pairings. This table is a coverage proof and not a menu:
four of the six are columns of one row of one table, and the other two have a
call each.

| Pairing | Answered by |
|---|---|
| source - sound | `alignment(text="source")`, `pairing.sounds` |
| source - rules | `alignment(text="source")`, `pairing.rules` |
| recited - sound | `alignment(text="recited")`, `pairing.sounds` |
| recited - rules | `alignment(text="recited")`, `pairing.rules` |
| source - recited | `r.respelling()` |
| sound - rules | `r.rules`, and `by` on every attribution and modifier |

**So there are three calls and not six**, and the reason is not economy. Four
of the pairings are columns of one row, because a pairing given its own call is
a second traversal of one join and a consumer wanting two of them has to
rejoin by index. Co-highlighting is the plain case: it reads `sounds` and
`shares` off one row, and no arrangement in which those arrive from two calls
can do it without the consumer rebuilding the row.

Source against recited is the one that cannot be a column. It is many-to-many
in both directions - a recited cell can cover two source glyphs and one
source glyph can render as two - and a column on a row that partitions one text
cannot hold a group that spans several rows of the other. `respelling` returns
those groups directly, which is what a diff view or a two-line teleprompter
reads.

`text` and `grouping` are axes of `alignment` and not two more calls: `text`
says which text the rows partition, and a pairing holds that text's glyphs
alone.

---

## 3. Identity

```python
@dataclass(frozen=True)
class PhonemizeResult:
    ref: str
    riwayah: str
    script: str
    variant: dict
    extra_phonemes: frozenset[str]
    schema_version: str
    canon_digest: str

    def phonemes(self, by=None): ...   # by="word" nests one tuple per word
    def text(self, which="source"): ...

    words:    tuple[Word, ...]
    glyphs:   tuple[Glyph, ...]
    rendered: tuple[RenderGlyph, ...]
    units:    tuple[Unit, ...]
    sounds:   tuple[Sound, ...]
    rules:    tuple[RuleInstance, ...]

    spellings:    tuple[SpellingEdge, ...]
    attributions: tuple[AttributionEdge, ...]
    modifiers:    tuple[ModifierEdge, ...]
```

| Field | Means |
|---|---|
| `ref` | the passage: `"2:255"`, `"2:255:3-2:256:1"`. Addresses words, not only verses |
| `riwayah`, `script` | which transmission, which mushaf |
| `variant` | which reading was taken at every disputed point, resolved |
| `extra_phonemes` | which optional tokens this notation spent, section 3.2 |
| `schema_version` | the shape of this document |
| `canon_digest` | identifies the canonical data the indices were resolved against |

Seven fields, all flat. No envelope groups them: a reader who must decide
whether a field is domain or infrastructure before reading it has been handed
a puzzle rather than a document.

The result restates the configuration the instance holds because the result is
what gets cached, serialized and compared. A document that says which reading
it is, at every site, resolved against which canon, is a complete record; one
that says only `"2:255"` is not.

**There is no notation field.** One notation ships, and a consumer supplying
its own tokens knows which it supplied.

### 3.1 Variants

A reading can differ at several points, and a reciter may take one wajh
throughout and another in a single word. So a selection is per point, and per
site within a point.

```python
variants={"raa_tafkheem": "heavy"}                  # every site of that point
variants={"raa_tafkheem": {"<site>": "heavy"}}      # one site
```

A string value broadcasts over the point's sites; a dict value names them. The
nesting is what `available_variants` returns, so a caller hands a site key back
rather than composing one.

| `khilaf` | Disputes |
|---|---|
| `seen_sad` | which letter is read where the rasm allows both |
| `raa_tafkheem` | whether a raa is heavy or light |
| `imala_quality` | the vowel imala tilts toward |
| `nucleus_vowel` | which vowel a position takes |
| `yaa_ithbat` | whether a pronoun yaa is pronounced at a pause |

`seen_sad` is published and has no sites in the shipped Hafs data, so nothing
selects it yet. The two nasal placement points are not here: see section 4.4.

**Every point in the shipped Hafs data is a set of sites, and one of them has
sites whose defaults differ from each other.** So a whole-point choice is a
broadcast that can move a site off its default rather than a name for a
reading, which `raa_tafkheem` and its nine sites already show. `r.variant`
publishes the resolved selection, every site with the value actually read, so a
caller who passed nothing can still see what was taken where.

**Rule identifiers are stable and site keys are not.** A site key is an opaque
token read from `available_variants` and handed back; a planned refactor names
a case per lexeme or pattern and rewrites them. A consumer that stores one
stores a version with it.

### 3.2 Optional phonemes

Three distinctions the model always carries and the notation does not always
spend a token on. All default off.

| Name | Off | On |
|---|---|---|
| `tashil` | the hamza token | a token of its own |
| `heavy_ikhfaa` | one ghunnah token | the emphatic form |
| `qalqala_degree` | one release token | sughra apart from kubra and akbar |

`qalqala_degree` is a two-way split: kubra and akbar share a token and akbar
takes no third.

**Switching one on changes no node and no edge.** `Sound.emphatic` on a ghunnah
is true whether or not the token shows it, and a qalqala's degree is on the
sound either way, so nothing is lost by leaving a toggle off and a consumer can
always read the distinction from the graph. That is what separates this from
`variants`, which changes what is read.

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
| `origin` | `written` · `muqattaat` · `tanween` |

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

| `kind` | Is |
|---|---|
| `base` | a letter of the rasm |
| `haraka` | fatha, damma, kasra |
| `tanween` | the doubled haraka |
| `shadda` | doubling |
| `vowel_letter` | alif, waw or yaa carrying length; occurs in `rendered` only |
| `small_vowel` | the dagger alif, the mini waw and yaa |
| `madd_sign` | the maddah |
| `sukun` | the mark stating a unit has no vowel |
| `silence_sign` | the round and rectangular zeros |
| `tajweed_mark` | the imala, ishmam and tashil marks |
| `stop_sign` | the mushaf's advice |
| `structural` | space, tatweel, the hizb and sajdah marks, the right-to-left mark |

What each becomes in `rendered` is not a property of its kind, and there is no
spelling policy to choose: the recited text is what recitation writes, once.
[06-two-texts](06-two-texts.md) is the whole of that relationship.

### 4.4 `Sound`

| Name | Means |
|---|---|
| `token` | how this sound is written in the chosen notation |
| `kind` | `consonant` · `vowel` · `qalqala` |

| `kind` | Fields |
|---|---|
| `consonant` | `letter`, `geminate`, `emphatic`, `ghunnah` |
| `vowel` | `quality`, `long`, `emphatic` |
| `qalqala` | `degree` |

**A ghunnah is not a kind.** It is a consonant said through the nose, and the
consonant is always a real letter: an ikhfaa hums the noon it fires on, so the
sound is that noon, and an idgham holds the letter its noon merged into, so
the sound is that letter. One field, one referent, and no sound that belongs
to no letter.

`geminate` tells the two apart. A hummed noon is not doubled and an idgham's
host is, which is also why the hum needs no place of articulation: it is the
noon, and where a reciter puts it is a khilaf the shipped data does not site.

`ghunnah` occurs on four letters, noon, meem, waw and yaa. With `emphatic` it
is the heavy ghunnah of an ikhfaa before an istilaa letter, which the ikhfaa
sets, because the ikhfaa is already the rule that read the following letter.

There is one kind of release and it is the qalqala, so the kind is named for
it; `degree` is `sughra`, `kubra` or `akbar`, and the rule of the same name is
where the degree was decided.

A sound has no `word` field: its word is the word of its primary origin.

### 4.5 `RuleInstance`

| Name | Means |
|---|---|
| `rule` | section 7 |
| `source` | the unit the rule is about, or absent |
| `host` | the unit that keeps the sound, where one is shared |
| `labels` | teaching names for this instance, [07-rules](07-rules.md) |

A rule is read against its `source`: a lam shamsiyyah belongs to the lam that
disappears, not to the letter that doubles. `source` is absent for one rule
only, `orthographic_silence`, which is about a letter no unit answers to.

**A trigger is not a participant.** What a rule read in order to fire is data
on a node, and where that data sits is not the same from rule to rule: the
letter after, for an ikhfaa; the letter before, for a raa's colour; the unit's
own vowel, for a qalqala; the boundary plan, for a madd arid or a hamza wasl.
A field naming it would have to mean a different thing in each family, which
is what `target` was doing.

So `host` is the only second participant, it is present only where two units
share one sound, and that is the mergers. Nothing has a third.

There is no family and no phase: the grouping in section 7 is for reading, and
a colouring scheme is a convention a consumer picks.

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
| **modifiers** | | |
| `Recolours(sound, by)` | the rule | tafkheem made this consonant heavy |
| `SetsLength(sound, by, length)` | the rule | iltiqa shortened this madd |
| `Classifies(sound, by)` | the rule | names this sound without changing it |

One unit per attribution. Two units never own one sound jointly: a merger is
already a pair of edges over one sound, which is what carries the sharing, and
a long vowel is shared by *graphemes*, which the spelling edges and the glyph
edges carry.

Every sound has a unit. The helping vowel of an iltiqa is the vowel of the
unit the reading vowels - a tanween's noon, or the meem of a spelled name -
hosted on a vowel part the canon leaves absent, which is the mirror of a stop
silencing a vowel the canon states.

`Recolours` carries no value. Emphasis is the only feature a rule sets, only
one rule sets it, and the resulting state is `emphatic` on the sound; the edge
exists to say which rule put it there. A light letter is the ordinary letter
and no rule fires, so there is nothing for a second value to mean. `length` is
`short` or `long`.

`Supplies.fact`: `letter` · `consonant` · `vowel_quality` · `vowel_length` ·
`vowel_absence` · `tajweed_mark`. Quality and length are separate facts, because otherwise a
haraka and its carrier make the identical claim about the identical unit and
section 6.1 cannot be evaluated. Sakt is not a unit-level fact: it is stated
on the word.

**Which glyphs show a sound is not an edge.** It is
`alignment(grouping="glyph")`, whose rows are one glyph each and already carry
what a colouring consumer needs: the sounds the glyph owns, the ones it only
presents, the ones it is written for and does not say, and its rules. A second
array over the same join would say less and have to be kept consistent with it.

`Part` is `consonant | vowel`. Silence is not a third value: it is what
happened to one of the two, and it happens to both.

A merger **is** a `Hosts` and `MergedInto` pair sharing a sound and a rule. A
release is hosted on the consonant that makes it, and is an **addition**: the
part still states one realization and carries the echo beside it.

`by` is absent when no rule claimed the sound. There is no `plain` rule.

---

## 6. Alignment and respelling

```python
r.alignment(text="source"|"recited", grouping="glyph"|"cell")
```

| | `text="source"` | `text="recited"` |
|---|---|---|
| `grouping="glyph"` | one pairing per source scalar | one per rendered scalar |
| `grouping="cell"` | section 6.4 | the same over the recited spelling |

```python
@dataclass(frozen=True)
class Pairing:
    glyphs:   tuple[int, ...]   # glyphs of the selected text
    sounds:   tuple[int, ...]   # the sounds this pairing owns
    shares:   tuple[int, ...]   # sounds it presents that another owns
    silent:   tuple[int, ...]   # its glyphs that are written and not said
    rules:    tuple[int, ...]   # every rule this pairing shows
    after:    int | None        # set only on a gap pairing
```

`rules` is total. Every rule a consumer would colour on these glyphs is in
it, whether the rule silenced the position or coloured the sound it made,
because a colouring consumer asks what happened here and not through which
edge family it happened. Which part or sound each one reached is on the
edges.

`text` selects which array is partitioned, and a pairing holds only that
text's glyphs. The two texts are related by `respelling`, not by a column: the
mapping between them is many-to-many in both directions and a column on one row
cannot carry that.

`silent` holds a glyph whose silence a rule names, and nothing else - a glyph
with a `Silent` attribution, or one carrying an `orthographic_silence`. A mark
that states a fact and makes no sound is not silent: a sukun, a shadda and a
carrier under a dagger stay out. Under `text="recited"` the list is always
empty, because no rule silences a glyph recitation itself wrote.

`sounds` and `shares` make co-highlighting a field. A sound is timed once and
lights every pairing naming it in either list, so an idgham lights the
merged-away letter and its host, and a tanween lights its own cell and again
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

### 6.3 Respelling

```python
r.respelling(grouping="glyph"|"cell")
```

```python
@dataclass(frozen=True)
class Block:
    source:  tuple[int, ...]   # pairings of alignment(text="source")
    recited: tuple[int, ...]   # pairings of alignment(text="recited")
```

A block is the smallest group of pairings on each side that corresponds as a
unit, closed under `from_glyphs` and under the sounds the pairings own. The
second closure is what places a sound the source does not write: its gap
pairing and the rendered glyph that writes it own one sound, so they fall in
one block, and neither is left for the reader to place. Where the two texts run one to one a block
holds one pairing on each side; where a source glyph renders as two, or a
recited cell covers two source glyphs, it holds what it has to. A source
glyph the recited text drops gives a block with an empty `recited`. No block
has an empty `source`: a rendered glyph the source did not produce still writes
a sound, and the closure over sounds puts it beside the pairing that owns it,
which is a gap pairing where no glyph states it.

It carries nothing the two alignments do not. The sounds, the rules and the
silences stay on the pairings a block points at, so there is one place each
fact is stated. This is a group-by with a name, published because every
consumer showing both texts writes the same one.

### 6.4 What a cell is, and what a pairing is not

A **cell** is a letter with the mark that vowels it, and a long vowel is a cell
of its own. Four clauses, applied to the glyphs of the selected text in order.
They group glyphs and never split one.

1. A glyph presenting a vowel the reading makes **long** opens a cell. Length
   here is what the reading realizes, never what the canon states: the spelling
   edges are boundary-free and a cell is a thing a reader sees at one boundary
   plan.
2. A glyph supplying that same vowel's quality joins it.
3. A glyph presenting that vowel and supplying no fact joins it: the seat
   under a dagger, and the maddah.
4. Every other glyph joins the cell of the glyph supplying its unit's
   consonant, and is a cell of its own where there is none: a letter the rasm
   carries that answers to no unit, and the sakt mark.

So `مَا` is `م` then `َا`, and `ءَايَـٰتُ` gives `ي` then `َٰ`: the mark that
carries the length takes the haraka with it and leaves the letter bare, which
is the one thing a consumer colouring letter by letter cannot do for itself
without knowing which vowel is long. A letter whose vowel is written only on
it stays whole, so `كَ` and `بٍ` are one cell each, and so is a bare letter
under a sukun.

A muqattaat glyph is one cell owning the sounds of a whole letter name,
because no clause can split a glyph; a consumer animating inside the name
reads the units, which are already there and already ordered.

**This is the grouping a renderer wants and `glyph` is not.** A haraka does not
highlight on its own and a maddah does not animate on its own, and a font
colours a letter, not a scalar. `glyph` is for a consumer asking what one
character does, which is a different question and the one the spelling edges
answer.

Pairings are request-local and will never take a durable key. A consumer
persisting records against them keys on position and defends against drift
with a content snapshot, which is the right shape for content that changes.

### 6.5 Word-by-word

Not a grouping. Every node carries its word and a merged sound's word is its
host's, so a consumer animating whole words reads which words a sound touches
and applies its own taste.

---

## 7. Rules

A rule name says what happened, never what triggered it: the trigger is data
on a node. Noon and tanween ikhfaa are one rule, and `origin` says which.

**The nasal letters.** `ikhfaa_haqiqi` · `iqlab` · `idgham_bi_ghunnah` ·
`idgham_bila_ghunnah` · `izhar` · `ghunnah_mushaddadah` · `izhar_shafawi` ·
`ikhfaa_shafawi` · `idgham_shafawi`

`izhar` is one rule. Saying the noon plainly before a throat letter, before
the waw or yaa of a word it shares, and at the end of a spelled name is one
outcome with three triggers, and a name may not carry a trigger. The meem's
three keep their own names because the meem's outcomes are its own, and
`izhar_shafawi` takes the same third trigger where a spelled name ends in a
meem.

**Adjacent consonants.** `idgham_mutamathilayn` · `idgham_mutaqaribayn` ·
`idgham_mutajanisayn_kamil` · `idgham_mutajanisayn_naqis` · `lam_shamsiyyah` ·
`lam_qamariyyah`

**Length.** `madd_tabii` · `madd_wajib_muttasil` · `madd_jaiz_munfasil` ·
`madd_lazim` · `madd_arid_lil_sukun` · `madd_leen` · `iltiqa_shortening`

**Release.** `qalqala_sughra` · `qalqala_kubra` · `qalqala_akbar`

**Colour and manner.** `tafkheem` · `tarqeeq` · `imala` · `tashil` · `ishmam`

**Boundary.** `hamza_wasl_start` · `hamza_wasl_elision` · `iltiqa_kasra` ·
`pausal_sukun` · `iwad` · `taa_marbuta_pausal`

Sakt is not here. It is a silence the reciter holds between two words, it
produces no sound and reaches no unit, and `Word.sakt_after` already says
where it falls. A rule for it would name a boundary twice.

**Substitution.** `ibdal_hamza`

**Orthographic.** `orthographic_silence`

That is the vocabulary. What each rule reaches, which unit hosts a merged
sound, the teaching labels, the silence the script writes, and where a rule
means one thing to a letter and another to a sound are all in
[07-rules](07-rules.md).

### 7.2 What a stop does

| | |
|---|---|
| a sound goes | `pausal_sukun`, or `iwad` on the noon of a lengthening fathatan |
| a vowel lengthens | a madd rule |
| a letter is realized differently | `taa_marbuta_pausal` |

Mutually exclusive per unit and per part.

---

## 8. Laws a consumer can check

| |
|---|
| Every glyph appears in exactly one pairing of its text, unless it is structural |
| Every sound appears in exactly one pairing's `sounds`, and any number of `shares` |
| Every unit states one realization per part: hosted, merged, silent, or absent |
| Every sound has one primary origin, a `Hosts` |
| Every merger is a `Hosts` and `MergedInto` pair sharing sound and rule |
| Every silence names a rule |
| Concatenating `glyphs` in `source_index` order reproduces the source text |
| Under `text="recited"`, no sound takes a gap pairing |
| No rule instance holds a `muqattaat` unit and a unit of another word |

**Absent is not silent.** A part is silent when it had a sound and the reading
took it, and absent when nothing put one there. The canon leaves a vowel
absent at the sukun, the bare consonant, the tanween's noon and a letter of a
spelled name, and at almost all of them nothing ever does: the exception is the
iltiqa, which sounds the noon's vowel and makes that part hosted like any
other. Silence names a rule and absence does not, which is why the two cannot
be one value.

Absence is stated by having no attribution rather than by an edge for it. The
producer emits nothing where nothing happened, which is what it would do
anyway, and [02-gate](02-gate.md) checks the converse over the corpus: a part
with no attribution has a canonically absent vowel and no rule sounding it.

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
   allowlisted so the parity report names them.
5. **`origin` stays one enum.** A letter name is spelled out and takes no
   grammatical ending, so a slot cannot be both spelled and nunated, and two
   booleans would publish a state that cannot exist.
6. **`Supplies.fact` distinguishes quality from length.** Without it a haraka
   and its carrier make identical claims and ownership cannot be evaluated.
7. **The rule family and phase leave the model.** Three readers must be
   replaced first, and one changes recitation: qalqala asks the family whether
   a slot was assimilated from.
8. **Delete the plain rule and make `by` optional.**
9. **Rename the parts** to `consonant` and `vowel` throughout.
10. **The ghunnah stops being a sound of its own.** A hummed noon is a
    consonant with `ghunnah`, so the standalone nasal type goes and the
   notation gains one key: a noon with `ghunnah` and no gemination is the hum
   it already writes, and the same noon geminate is the held letter it
    already writes. Every token stays as it is.
11. **`izhar` replaces `izhar_halqi` and `izhar_mutlaq`.** One outcome, two
    triggers, and a name may not carry a trigger.
12. **Sakt stops being a rule.** `Word.sakt_after` is where it lives.
13. **An ikhfaa sets its ghunnah's weight.** The rule reads the following
    letter already; before an istilaa letter the hum is heavy, and the
    `Recolours` edge is the rule's own. The notation has no emphatic form
    for a nasal and refuses one outright, so the token is a second half of
    this item and not a consequence of it.
14. **`Participants` are labelled.** A rule's units are a source and a host,
    and today the pair is positional.
15. **A qalqala's degree is on the sound.** Section 4.4 publishes `degree`;
    `Release` carries only `kind`, whose single value is the qalqala itself,
    and the degree lives in the rule names alone. A consumer reading a release
    has to walk to the rule to learn how hard it bounces.

**Facts the model drops**

16. **Marks that reach no unit.** The largest group is the alif seating a
    fathatan, skipped although it sounds at a pause and every iwad case needs
    it. Then the superscript alif over a written carrier, the sakt mark, the
    combining hamza above, and the rectangular zero.
17. **The separator between words is a glyph.** A space inside a word's own
    text is emitted; the one between two words is not, so the concatenation
    law passes only on a single-word verse.
18. **One scalar, one glyph.** One verse emits a combining mark twice, and
    duplicate spelling edges exist for every alef wasla and every tatweel.
19. **One notion of structural, and it is the `Structural` edge.** The class
    and the edge disagree in both directions: a tatweel is classed structural
    and carries no edge, a stop sign carries the edge and is classed as
    advice. Both move to the edge, and section 4.3 follows: `stop_sign` keeps
    its own `kind` and takes no pairing, and a tatweel takes none either.
20. **The dagger and its carrier are reversed.**
21. **`length_carrier` is a class nothing assigns.** No scalar classifies as
    one, and the recited spelling is where a length carrier is added.
22. **Sakt is a word fact and is evidenced by nothing.** The unit-level fact
    exists in the model and no glyph supplies it.

**Rules with no producer**

23. **Madd rules for their ordinary cases.** `madd_tabii` is minted only on
    the pausal glide; an ordinary long vowel, a silah vowel and a stopped
    seven-alif produce none.
24. **`orthographic_silence`.** The seats are identified, but the field
    naming the unit each shows against is written and never read, and one
    seat class reaches no spelling edge at all. It stays one rule: a letter
    never said and a seat silent only when joined are the same outcome, and
    the boundary tells them apart without a second name.
25. **The vocabulary is short two rules**, both mandatory and both corpus-wide:
    dropping a word-initial shadda when a word is started on, and the role a
    word-final yaa, waw or alif maqsura takes at a pause. Neither has a name,
    neither has a converse trigger, and [06-two-texts](06-two-texts.md) is
    where the transformation each performs is written down.
26. **The iltiqa helping vowel** is constructed nowhere. It is the vowel of
    the unit the reading vowels - a tanween's noon, or the meem of a spelled
    name - hosted on a vowel part the canon leaves absent.
27. **Split the boundary rules to match the names.** One code rule covers
    `pausal_sukun` and `taa_marbuta_pausal`. The iwad is already its own rule
    and keeps its name.
28. **A colour is not minted for a part a complete merger consumed.** The
    letter has no sound of its own to be heavy, which is the whole difference
    between a complete idgham and a partial one. The producer already declines
    this for the vowel and must decline it for the consonant too.
29. **Release attribution moves to the consonant** - and the fill step reads
    any realization as claiming the part, so moving only the effect deletes
    the consonant's own sound. Every release in the corpus sits on the vowel
    today, so this is not a repair at the margin.
30. **A merger host keeps its ghunnah.** The pair-table family builds its host
    consonant with no nasal fact, and the corpus has one merger of that family
    whose host is a nasal letter: the baa of `ٱرْكَب` into the meem of
    `مَّعَنَا`, which is held today without a hum.
31. **A spelled name is closed.** The noon that ends a disjoined-letter
    opening takes the nasal rules of the word after it, so `طسٓ` hums into
    `تِلْكَ` and `نٓ` merges into `وَٱلْقَلَمِ` and loses its own consonant.
    A unit whose `origin` is `muqattaat` neither takes a rule from another
    word nor gives one, and the last unit of the last name takes the
    plain-articulation rule of its own letter: `izhar` after a noon and
    `izhar_shafawi` after a meem, which nine of the openings need. The rules
    between the names of one opening are unaffected, and the three disputed
    sites are khilaf points rather than exceptions.

**Machinery**

32. **A writer for the recited text.** The one that exists takes a Score, so
    it has no boundary plan and no performance and cannot spell a pausal,
    merged or started-on form. `rendered` needs glyph records carrying
    `from_glyphs`, their own pairings, and the blocks `respelling` returns.
33. **Total glyph pairing.** The join saying which outcomes each glyph
    presents, distinguishing a sounded dagger from its silent carrier and a
    performance deletion from orthographic zero.
34. **Sub-verse requests.** A request clipping a ledger-addressed word raises
    rather than building.
35. **Continuous assembly** overlaps by two words, because cross-word
    lookahead reaches past a one-slot word.
36. **Request orchestration.** Resolve `(ref, boundaries, variant)`, build,
    perform, and assemble one index space. Arbitrary stops, sakt and
    cross-verse joins use the same path, and a started-on word is the word
    after a stop rather than a second input.
37. **The ref grammar.** An endpoint is `surah[:ayah[:word]]` and a ref is one
    or two of them at the same depth. Five forms, and a whole surah is the
    common one.
38. **The three module functions.** `supported_riwayat`, `available_variants`
    and `tajweed_rules`, answering without an instance, and
    `available_variants` returning the nesting `variants` accepts.
39. **The optional phonemes are gated at the notation.** Section 3.2's three
    names select tokens and reach no node and no edge, so the gate belongs
    beside the alphabet and nowhere in the producer.
40. **The teaching labels are derived.** Section 4.5 publishes `labels` and
    [07-rules](07-rules.md) section 4 defines four of them; nothing computes
    any. Each is a predicate over an instance and the unit it names, so they
    are derived where the instance is assembled and mint no instance of their
    own.
