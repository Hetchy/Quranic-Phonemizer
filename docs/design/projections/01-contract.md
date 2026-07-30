# 01 - The public contract

Status: **proposed**. Scope: Uthmani, Hafs.

Two projections over the layered model, and no third.

| Name | Shape | For |
|---|---|---|
| `phonemes` | ordered notation tokens, with word boundaries | consumers that want only sound |
| `Mappings` | identified nodes plus typed relation arrays | every script, alignment, and tajweed consumer |

They are never joined; a consumer picks one. `phonemes` stays separate because
the token stream is stable across every schema evolution of the graph, so a
consumer who wants a list of strings does not inherit the request envelope or
break on graph changes that did not affect them.

---

## 1. Read this much and stop

`Mappings` is one document, and you almost never walk it yourself. Three
methods answer what consumers actually ask.

### "Which rules apply here?"

```python
m = mappings("2:255")

for r in m.rules:
    print(r.rule, r.source.letter, r.target.letter)
```

`m.rules` is the array itself: every rule instance that fired, in reading
order. `r.source` and `r.target` are the units involved; `target` is absent
when the rule names only one.

### "Line the script up with the sound"

```python
for row in m.alignment(text="source", grouping="cluster"):
    paint(row.glyphs, row.sounds, row.shares)
```

One call, at a chosen granularity, over a chosen text. Section 6 is the whole
of it.

### "Which letters are silent, and why?"

```python
for s in m.silences():
    print(s.glyph.char, s.reason)
```

`reason` is a rule name, or the literal `orthographic` for a glyph that never
fed a sound. One field, two kinds of answer, no null to handle.

### "Just the phonemes"

Use the `phonemes` projection, which takes its own split argument.

---

## 2. The shape

Six kinds of node, four kinds of edge.

```
   Glyph  --------- spellings --------->  Unit  ---- attributions ---->  Sound
 what the script                     the canonical                    what is heard
    wrote                             position                             |
      |                                    ^                               |
      |                                    |                               |
      +--------- contributions --->  [ RuleInstance ] <---- modifiers -----+

  RenderGlyph ----- contributions ------------^
 what recitation
     spells
```

Read it as four sentences:

- **spellings** - this mark supplies, witnesses or decorates that position.
- **attributions** - this position produced, absorbed, or lost that sound.
- **modifiers** - this rule coloured, relengthened or merely named that sound,
  without owning it.
- **contributions** - this written mark is the thing you point at for that
  outcome.

Every reference is an integer index into one of the node arrays. No reverse
links are stored: `units_by_word` and friends are helpers a consumer builds
locally, never a second copy of the truth.

Edges rather than fields on the nodes, because the interesting facts in
recitation are relationships between two things, and flattening one onto a
node forces a winner. A long vowel is voiced by a haraka and a carrier
together. A cross-word idgham is one sound belonging to two units in two
words. A final consonant at a stop sounds while its own vowel is deleted.

### 2.1 What the shape lets you build

| Capability | Reads |
|---|---|
| rule to phoneme | `attributions.by` and `modifiers.by` on the sound |
| rule to source glyph | `rules` to units to `spellings` |
| rule to recited letter | `rules` to `contributions` over `rendered` |
| glyph to phoneme, N to M | `alignment(grouping="glyph")` |
| recited text, silent glyphs greyed | `alignment(text="source")`, `row.silent` |
| recited text, silent glyphs omitted | `alignment(text="recited")` |
| co-highlighting | `row.shares` |
| teaching "why" | the rule instance's `source` and `target` |
| boundary rehearsal | two `Mappings` for one ref stopped at different words, diffed |
| variant diffing | the same, varying `variant` |
| cross-script proof | two scripts must agree on `units`, `sounds` and `rules` |
| corpus search | every site of a rule, or of a rule crossing a word boundary |
| alignment targets | sounds with their word and rule labels |

---

## 3. Identity

A `Mappings` is a snapshot of one fully identified request.

```python
@dataclass(frozen=True)
class Mappings:
    ref: str
    variant: VariantSelection
    provenance: Provenance

    words: tuple[Word, ...]
    glyphs: tuple[Glyph, ...]
    rendered: tuple[RenderGlyph, ...]
    units: tuple[Unit, ...]
    sounds: tuple[Sound, ...]
    rules: tuple[RuleInstance, ...]

    spellings: tuple[SpellingEdge, ...]
    attributions: tuple[AttributionEdge, ...]
    modifiers: tuple[ModifierEdge, ...]
    contributions: tuple[Contribution, ...]
```

| Field | Where | Means |
|---|---|---|
| `ref` | top | the passage: `"2:255"`, `"2:255:3-2:256:1"`. Addresses words, not only verses |
| `variant` | top | the variant readings selected |
| `riwayah`, `script` | `provenance` | which transmission, which mushaf |
| `notation` | `provenance` | which phoneme alphabet. `Sound.token` is a string whose meaning depends on it |
| `schema_version` | `provenance` | |
| `canon_digest` | `provenance` | identifies the canonical data the indices were resolved against |

Indices are local to one document. A slot label is not a durable external
identifier: riwayah, variant, corpus revision and schema edition all affect
what it means. Alignment rows are request-local for the same reason.

The whole graph is always emitted. Referential integrity forces a dependency
order, so per-array flags would not be independent, and every law in
[02-gate](02-gate.md) would become conditional on whether its target array was
requested. Bulk output is an offline build that lands in a shard writer, and
the shard writer selects for itself.

---

## 4. Nodes

### 4.1 `Word`

| Name | Means |
|---|---|
| `location` | `surah:ayah:word` |
| `text` | the source word as written |
| `is_started_on` | recitation begins here (ibtidaa) |
| `is_stopped_on` | recitation pauses after this word (waqf) |
| `sakt_after` | a breathless pause: not a stop, but cross-word rules are blocked |
| `stop_sign` | the mushaf's sign, if any: `preferred_stop`, `compulsory_stop`, ... |

**The last word of a request is stopped on.** A consumer who wants that word
performed as a wasl asks for a longer `ref`. `sakt_after` is its own field
because a sakt blocks cross-word lookahead while neither stopping nor
starting.

### 4.2 `Unit`

One letter together with the vowel state that follows it: the thing a rule
fires on. Not the same as a written cluster - some units are written by
several glyphs, some glyphs write several units, and the noon inside a tanween
is written by no glyph of its own.

| Name | Means |
|---|---|
| `word` | index into `words` |
| `letter` | which of the thirty: the twenty-eight plus hamza and taa marbuta |
| `onset` | the consonant's state: `plain \| geminate \| wasl \| silah \| tashil` |
| `nucleus` | the vowel state |
| `is_tanween` | this unit is the noon of a tanween |
| `is_letter_name` | part of a letter's spoken name |

`Nucleus` is a discriminated union, so an impossible combination cannot be
spelled:

| Variant | Means |
|---|---|
| `Silent` | no vowel here |
| `Short(quality)` | fatha, damma, kasra |
| `Long(quality)` | a madd letter's vowel |
| `LongWhenJoined(quality)` | the pronoun haa's silah: long in wasl, absent at pause |
| `LongWhenStopped(quality)` | the seven alifs: short in wasl, long at pause |

There are deliberately no glyph, sound, rule, silence-reason or rendered-text
fields on a unit; those are relations. Madd counts and durations are absent
too: a madd's length in harakat is a property of the tariq a reciter takes,
not of the canonical position. Imala, ishmam and tashil reach the consumer as
rules, because that is what they are.

`Part` is `onset | nucleus`, the two halves a rule addresses separately.

### 4.3 `Glyph`

One Unicode scalar the source script wrote.

| Name | Means |
|---|---|
| `word` | index into `words`, or absent for a structural glyph |
| `char` | the scalar |
| `kind` | what the mark is |
| `word_index` | ordinal within its word |
| `source_index` | ordinal in the whole requested passage |

`kind` is `base`, `haraka`, `tanween`, `shadda`, `vowel_letter`,
`small_vowel`, `madd_sign`, `silence_sign`, `tajweed_mark`, `stop_sign`, or
`structural`.

### 4.4 `RenderGlyph`

One scalar of the recited spelling.

| Name | Means |
|---|---|
| `word` | index into `words`, or absent |
| `char` | the scalar to draw |
| `kind` | as `Glyph` |
| `from_glyph` | the source glyph it renders, or absent when nothing in the source spells it |

`from_glyph` absent is an insertion, and `char` says what to draw. A rendered
glyph that differs from its source is a replacement. Both are read as fields,
not derived by diffing two strings.

The recited spelling takes a policy:

| `spelling` | The wasl hamza renders as |
|---|---|
| `faithful` | `ٱ` plus the helping haraka |
| `explicit` | `أ` or `إ` per the vowel |

### 4.5 `Sound`

| Name | Means |
|---|---|
| `token` | the selected notation's spelling |
| `kind` and its fields | `consonant \| vowel \| ghunnah \| release` |

`consonant{letter, geminate, emphatic, ghunnah}`, `vowel{quality, long,
emphatic}`, `ghunnah{place, emphatic}`, `release{kind}`.

`ghunnah` on a consonant says the letter is **held**, which for a noon changes
`nn` to a held nasal. The standalone `ghunnah` kind is the hum of ikhfaa and
iqlab, which belongs to no letter: `place` is `bilabial` for iqlab,
`assimilated` for ikhfaa. An ikhfaa before an istilaa letter is heavy, which
is what `Ghunnah.emphatic` carries.

Geminate is a feature rather than a kind, because a doubled consonant can also
be emphatic or held.

**A sound has no `word` field.** Its word is the word of its primary origin -
the `Hosts` edge, or the `Insertion` anchor. A stored copy is a second answer
that can disagree with the first, and cross-word mergers are where it would.

### 4.6 `RuleInstance`

| Name | Means |
|---|---|
| `rule` | the rule name |
| `source` | the unit the rule is about |
| `target` | the other unit it names; absent when the rule names only one |

Nothing in the corpus has a third participant, so two fields carry it. Arity
is per instance rather than per rule, so `target` is optional per row.

`source` is the unit the rule is about and `target` the unit it reaches, for
every rule without exception. For `min rabbihim`, `source` is the sakin noon
and `target` the following raa. A producer that assembles its pair in the
other order is corrected at the producer.

`RuleFamily` and `Phase` are total functions of `rule`, published as versioned
tables rather than repeated on every instance. Every public rule has an entry
in both.

---

## 5. Edges

Subject matters. Three attribution edges state something a unit does; one
states something with no unit at all.

| Edge | Subject | Means |
|---|---|---|
| **spellings** | | |
| `Supplies(glyph, unit, fact)` | the glyph | supplies a canonical fact: this fatha *is* the unit's vowel |
| `Witnesses(glyph, family, unit)` | the glyph | witnesses that a rule of this family happens here without supplying a canonical fact: a word-initial shadda witnesses an assimilation from the previous word |
| `Decorates(glyph, unit)` | the glyph | supplies and asserts nothing, but is bound to the unit it marks: the maddah |
| `Structural(glyph)` | the glyph | belongs to no word: space, verse marker, tatweel |
| **attributions** | | |
| `Hosts(units, part, sound, by?)` | the units | these units produce this sound. Several units is joint ownership, not a preferred owner |
| `MergedInto(units, part, sound, by?)` | the units | this unit disappeared into that sound |
| `Silent(units, part, by?)` | the units | this unit lost its sound, and `by` says which rule took it |
| `Insertion(anchor, side, part, sound, by?)` | nobody | a sound no unit owns, placed before or after an anchor |
| **modifiers** | | |
| `Recolours(sound, by, feature, value)` | the rule | tafkheem made this consonant heavy |
| `SetsLength(sound, by, length)` | the rule | iltiqa shortened this madd |
| `Classifies(sound, by)` | the rule | names this sound without changing it: every madd, every izhar, tarqeeq, tashil |
| **contributions** | | |
| `presents` | the glyph | one row per non-structural glyph and per rendered glyph, listing the outcomes it is the mark for |

A merger **is** the `Hosts` and `MergedInto` pair sharing a sound and a rule
instance. `Part` is mandatory on every attribution: a final consonant can host
an onset while a separate nucleus attribution is silent at pause, and that
cannot be recovered from sound kind.

`contributions` has one row per glyph, whose `presents` list may be empty. An
empty list means the glyph contributes to nothing heard; a glyph *missing*
from the array is a bug. The read API reports one `reason` that is either a
rule name or the literal `orthographic`.

`by` is optional. Its absence means no rule claimed this: what the script
writes, realized by default. There is no `plain` rule, because absence is the
honest encoding of absence.

---

## 6. Alignment

Two axes, four combinations, one method.

```python
m.alignment(text="source"|"recited", grouping="glyph"|"cluster")
```

| | `text="source"` | `text="recited"` |
|---|---|---|
| `grouping="glyph"` | one row per source scalar | one row per rendered scalar |
| `grouping="cluster"` | base letter plus the marks a font shapes with it | the same over the recited spelling |

A row:

```python
@dataclass(frozen=True)
class AlignmentRow:
    glyphs: tuple[int, ...]   # into glyphs, or into rendered
    sounds: tuple[int, ...]   # the sounds this row owns
    shares: tuple[int, ...]   # sounds it presents that another row owns
    silent: tuple[int, ...]   # its glyphs presenting a Silent attribution
    rules:  tuple[int, ...]
    after:  int | None        # set only on a gap row
```

`sounds` and `shares` are what make co-highlighting a field rather than a
policy. A sound is timed once and lights every row that names it in either
list, so an idgham lights both the merged-away letter and its host, a lam
shamsiyyah lights the silent lam and the letter that doubles, and a tanween
lights its whole cluster and then again with the letter it merges into. A row
with both lists empty gets no highlight. A consumer that wants silent glyphs
gone filters the rows.

### 6.1 Ownership

Several glyphs can present one sound, and exactly one row owns it. The
ordering is total and is a definition rather than a parameter:

1. the glyph that supplies the sound's **length**, if one is written;
2. otherwise the glyph that supplies its **quality**;
3. for a merged sound, the **host** unit's glyph;
4. otherwise the first presenting glyph in source order.

So in `قَالَ` the alif owns the long vowel and the qaf owns its own consonant,
and in a cross-word idgham the host word's cell owns the geminate while the
merged-away cell shares it.

### 6.2 Gap rows

An inserted sound has no glyph in the source text. Under `text="source"` it
takes a **gap row**: `glyphs` empty, `after` naming the row it follows.
Under `text="recited"` it is an ordinary row, because a rendered glyph exists
for it.

### 6.3 Word-by-word

Not a grouping. Every node carries its word, and a merged sound's word is its
host's, so a consumer animating whole words reads which words a sound touches
and applies its own taste about which to light. The contract states the fact;
the choice is the consumer's.

---

## 7. Rules

The public set:

`ikhfaa_haqiqi` · `iqlab` · `idgham_bi_ghunnah` · `idgham_bila_ghunnah` ·
`izhar_halqi` · `izhar_mutlaq` · `ghunnah_mushaddadah` · `izhar_shafawi` ·
`ikhfaa_shafawi` · `idgham_shafawi` · `idgham_mutamathilayn` ·
`idgham_mutaqaribayn` · `idgham_mutajanisayn_kamil` ·
`idgham_mutajanisayn_naqis` · `lam_shamsiyyah` · `lam_qamariyyah` ·
`madd_tabii` · `madd_wajib_muttasil` · `madd_jaiz_munfasil` · `madd_lazim` ·
`madd_arid_lil_sukun` · `madd_leen` · `iwad` · `ibdal_hamza` ·
`qalqala_sughra` · `qalqala_kubra` · `qalqala_akbar` · `tafkheem` ·
`tarqeeq` · `imala` · `tashil` · `ishmam` · `sakt` · `wasl_start` ·
`wasl_elision` · `iltiqa_repair` · `pausal_sukun` · `taa_marbuta_pausal`

Names are trigger-independent: noon and tanween ikhfaa are one rule, and the
trigger is read from `unit.is_tanween`. Degrees stay distinct rules.

`RuleFamily` is an effect class - `assimilation`, `nasalization`, `insertion`,
`lengthening`, `emphasis`, `release`, `elision` - not a teaching taxonomy. A
consumer wanting the textbook grouping builds it from `rule`.

There is no `waqf` family. `word.is_stopped_on` is already in the document, so
"everything the stop did to this word" is a filter. It correctly also catches
`madd_arid_lil_sukun` and the pausal qalqalas, which a waqf family would have
to duplicate.

`pausal_sukun` names what a stop silences: the final short nucleus, the
tanween that goes with it, the absent silah vowel, and the dropped pronoun
yaa. One instance may carry several silences, because losing a tanween is one
event across two units. `is_tanween` and the nucleus kind already say which
case it was, so the name does not repeat them.

The two things a stop does other than silence keep their own names: `iwad`,
where the base's vowel lengthens instead, and `taa_marbuta_pausal`, where the
letter's sound changes.

---

## 8. What the producer must build

1. **One meaning for `source`.** Correct the producer that assembles its pair
   in the other order, so `source` reads the same for every rule.
2. **Retained modifier provenance.** Keep the rule-to-sound edge and its value
   when the engine applies a recolour or a length change, and add `Classifies`
   for a classification-only rule that names a sound. A recolour aimed at a
   part that merges away currently produces neither a sound nor an edge; see
   [04-open-questions](04-open-questions.md).
3. **Total glyph contribution.** Build the join that says which outcomes each
   glyph presents. It must distinguish a sounded dagger from its silent
   carrier, a sounded maddah from an otiose seat, and a performance deletion
   from orthographic zero. Where the source model cannot determine a link it
   is fixed below the projection; a serializer may not detect the answer from
   tokens or rule names.
4. **The dagger and its carrier.** Where a dagger sits over a written carrier,
   the carrier currently takes the nucleus edge and the dagger takes none,
   which is the reverse of what the contract states. This is canonical-layer
   work, not a cross-layer join.
5. **Sub-verse requests.** The canonical build resolves ledger entries against
   the whole verse, so a request that clips a ledger-addressed word raises
   rather than building. Ledger application must ask whether an entry is
   inside the request, not only inside the verse. Until it does, no ranged
   request over those verses builds at all.
6. **Insertions.** The helping vowel of iltiqa al-sakinayn is specified and
   constructed nowhere, so the sites that need one emit nothing.
7. **Recited glyphs.** The writer returns strings. `rendered` needs glyph
   records carrying `from_glyph` and their own `presents` edges. Both recited
   quadrants of section 6 depend on this and on nothing else.
8. **Madd tabii for its ordinary case.** The rule is minted only on the pausal
   glide, so an ordinary madd tabii produces no rule instance.
9. **Continuous assembly.** Cross-word lookahead reaches past a one-slot word,
   so a chunked continuous build must overlap by two words, or the reach must
   be bounded to one. Chunking that overlaps by one invents occurrences on
   kept words while leaving every sound identical, so a law stated over sounds
   cannot see it.
10. **Request orchestration.** Resolve `(ref, boundary policy, variant)`
    through the corpus, build the Score and Inscription, run the Performance,
    and assemble one index space across the requested range. Internal starts,
    arbitrary stops, sakt and cross-verse joins use the same path.
