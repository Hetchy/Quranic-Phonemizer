# 05 - The public contract, in plain words

Status: **proposed**, and the thing to argue with before any code is written.
Scope: Uthmani, Hafs.

This document is not a tajweed glossary. It is the contract explained for
someone who has never read `model/`, plus a name-by-name audit with the
alternatives that were rejected, so the naming can be reviewed rather than
inherited.

Everything marked **RENAME** is a proposal, not a decision. Each carries its
cost. Reject them individually. Items marked **[owner]** are settled.

---

## 1. Read this much and stop

`Mappings` is one document, and you almost never walk it yourself. It has
methods for the things consumers actually ask for, each returning a small
record with the joins already done. The graph underneath is what you reach for
when no method fits - not where you start.

### "Which tajweed rules apply to this verse?"

```python
m = mappings("2:255")

for r in m.rules:
    print(r.rule, r.source.letter, r.target.letter)
    # ikhfaa_haqiqi  noon  jeem
    # madd_lazim     ya    meem
    # tafkheem       sad   -
```

`m.rules` is the array itself, not a method: every rule that fired, in reading
order. `r.rule` is one of 39 names, `r.source` and `r.target` are the units
involved, `r.sounds` is what it sounds like and `r.glyphs` is what to point at.

### "Colour the letters of the script by rule"

```python
for glyph, rules in m.rules_on_glyphs():
    paint(glyph.char, colour_for(rules))
```

One call, because the hard part - a rule fires on a *unit* while the script
writes *glyphs*, and the two are not one-to-one - is done for you. A long
vowel is one unit written by two glyphs; a muqattaat letter is one glyph
spelling four units.

### "Which letters are silent, and why?"

```python
for s in m.silences():
    print(s.glyph.char, s.reason)
    # ٱ  wasl_elision
    # ل  lam_shamsiyyah
    # ا  orthographic     (the otiose alif: never fed a sound, no rule took it)
```

`reason` is a rule name, or the literal `orthographic` for a glyph that never
fed a sound in the first place. One field, two kinds of answer, no null to
handle. Legacy could not tell the two apart at all and needed `vowel_silent`
as a catch-all for 4,568 rows.

### "Just the phonemes"

Use the `phonemes` projection, which takes its own split argument. It is not
duplicated here: two ways to get one fact is how the five legacy views drifted.

### The rest of the surface

```text
m.rules_at(word=3)                  the same rule rows, filtered
m.cells(grouping=..., owner=...)    glyph rows at a chosen granularity (2.2)
m.recited_text()                    the words respelled as recited
```

Everything past this section is for the fifth consumer: an aligner, a
recited-writing renderer, or anything that needs a join no method offers. That
consumer reads §2 onward. Nobody else has to.

**Why methods and not five smaller documents.** Measured in
[04 §5](04-resolutions.md): no array dominates the payload, a tajweed-only
subset is 25% of it, and this shape of JSON compresses 31:1 - so a whole
`Mappings` for 2:255 is about 4.5 KB on the wire. Splitting would buy 4x on
4.5 KB while giving every visual consumer two documents to re-join, which is
exactly how the five legacy views drifted apart. A method costs nothing, has
no schema version, and cannot disagree with the graph because it *is* the
graph.

---

## 2. The shape, once

Five kinds of node, four kinds of edge between them. Nothing else.

```
   Glyph  --------- spellings ---------->  Unit  ---- attributions ---->  Sound
 what the script                     the canonical                    what is heard
    wrote                             position                             |
      |                                    ^                               |
      |                                    |                               |
      +--------- contributions --->  [ RuleInstance ] <---- modifiers -----+
                                     which rule fired,
                                     and on which units
```

Read it as four sentences:

- **spellings** - this mark supplies, witnesses or decorates that position.
- **attributions** - this position produced, absorbed, or lost that sound.
- **modifiers** - this rule coloured, relengthened or merely named that sound,
  without owning it.
- **contributions** - this written mark is the thing you point at for that
  outcome.

Every reference is an integer index into one of the five node arrays. There
are no reverse links stored: `units_by_word` and friends are helpers you build
locally, never a second copy of the truth that can disagree with the first.

**Why edges instead of fields on the nodes.** Because the interesting facts in
recitation are all *relationships between two things*, and the moment you
flatten one onto a node you have to pick a winner. A long vowel is voiced by a
haraka and a carrier together - put `owner: Unit` on the sound and you have
picked one and lost the other. A cross-word idgham is one sound belonging to
two units in two different words. A final consonant at a stop sounds while its
own vowel is deleted. The old four projections each flattened a different way,
each lost a different set, and every consumer rebuilt the join by matching on
rule names. The full argument is [ADR-013](../../adr/013-public-projection-foundations.md);
it is not re-run here.

### 2.1 What this shape lets you build

The seven capabilities the contract is being bought for. "Needs" means the
graph shape is right and the producer is not finished, not that the design is
in doubt.

| | Capability | Reads | Needs |
|---|---|---|---|
| 1 | rule -> phoneme | `attributions.by` and `modifiers.by` on the sound | **C2** (modifier edges are discarded today), **C5**, B1's law |
| 2 | rule -> recited letter, waqf and wasl applied | recited-writing serializer over `write` + contributions | **C3**, **C4**; gated on `write` totality (F6) |
| 3 | rule -> source glyph | participants -> units -> `spellings` | **C3** |
| 4 | recited text, silent glyphs greyed | source glyph order + `silences()` | **C3** |
| 5 | recited text, silent glyphs omitted | **not** 4 minus rows - see below | **C3**, **C4**, F6 |
| 6 | glyph <-> phoneme, N to M | `contributions` | **C3** |
| 7 | everything else | end of this section | |

**On 3, "some rules have nowhere to point".** The set is *queryable* rather
than maintained by hand: a unit with no `supplies(fact=nucleus)` edge has an
unwritten vowel, and a rule instance with no `presents` edge has no glyph at
all. Both named cases resolve, and neither the way an earlier draft claimed:

- **The divine name's long `aa` is unwritten everywhere.** There is no dagger
  alif in `ٱللَّهِ`, `ٱللَّهُ` or `لِلَّهِ` - the corpus scalars are
  `U+0671 U+0644 U+0644 U+0651 U+064E U+0647 U+0650` and no `U+0670`. The
  length is lexical. So the fatha `supplies` the unit's nucleus, and **no
  glyph `presents` the madd**: rule-to-glyph correctly returns nothing, and
  the consumer can tell the madd is unwritten rather than being handed a
  plausible wrong glyph. That is why `spellings` and `contributions` are two
  relations rather than one.
- **Madd iwad currently points at the wrong glyph, and that is a defect.** A
  madd must link to a vowel grapheme or a vowel phoneme. At 2:5:3 stopped, the
  alif seat `ى` is the grapheme that carries the iwad - legacy tags it
  `{'chars': 'ى', 'role': 'madd', 'phonemes': ['a:'], 'tag': 'madd_iwad'}` -
  but the branch has `ى` decorating the tanween noon, the one unit that goes
  silent. See **04 B7**; the fix is C9 and the law is L-madd.

What genuinely has no glyph and never will is an **inserted** sound, and there
is exactly one kind: the helping kasra of iltiqa al-sakinayn, placed by
`Insertion(anchor, side)` between two glyphs rather than on one. See
**04 B6** - today the package emits none at all.

**On 2 and 5, the orthographic transformations QUA cells need.** The
seat-versus-no-seat difference is real, is not a rule difference, and is what
legacy's `status` field was carrying. Counted over the corpus:

```
iwad sites with a written seat (ا or ى):  3,156     legacy: status "replaced"
iwad sites with no seat (all `ءً`):           78     legacy: status "inserted"
```

```
2:5:3   هُدًى   {'chars': 'ى', 'status': 'replaced', 'tag': 'madd_iwad'}
2:22:11 مَآءً   {'chars': '',  'status': 'inserted', 'tag': 'madd_iwad'}
```

In the first the seat is already written, silent in wasl, and un-silenced at
the pause. In the second there is no seat, and the recited form has a glyph
the rasm does not.

**`chars: ''` is legacy's defect, not the target.** **[owner]** An empty string
tells a consumer that something was inserted and refuses to say what, so every
renderer has to know on its own that an iwad inserts an alif. The contract
emits the **rendered glyph**: a render glyph carrying `ا`, linked to the sound
it spells and to the anchor it sits after, with no source glyph behind it.
ADR-005 §5 already requires this - "a slotless insertion is represented by its
before/after anchor and its rendered sound; it is not forced into a fake unit
or an empty source glyph" - and `write.py::_nucleus` already knows the
spelling, since a `Long(a)` nucleus spells as haraka plus carrier plus madd
sign. What does not exist is the serializer that applies performance results
to `write`, which is 00-audit §4.4's unbuilt ADR-005 mechanism and F6's gate.
Until it lands, capability 5 has no output for these 78 words. **The contract distinguishes them with no rule-name
difference**: the `a:` is presented by *two* glyphs in the first case - the
fathatan and the seat, once B7 puts the seat on the right unit - and by *one*
in the second. `status` is then derived, exactly as 01-design §5 defines it:
`inserted` when the recited writing has a glyph the source does not,
`replaced` when a source glyph's rendering changes.

Taa marbuta is the same shape from the other direction: the glyph does not
change but its sound does, so `ة` at waqf is `replaced` with one presenting
glyph throughout. These, madd iwad, and the wasl-hamza helping vowels are the
cases the recited-writing serializer has to get right, and they are ADR-005
§4's totality trigger set (F6) for exactly this reason.

**On 5, the trap.** "Silent letters omitted" is *not* "silent letters greyed,
minus those rows", because **a glyph is not atomically silent**. The single
tanween mark `ً` at 2:5:3 supplies three facts across two units: the dal's
vowel, the noon's letter, and the noon's silence. At waqf the noon half goes
silent and the vowel half lengthens into the iwad. Delete the glyph and you
lose the vowel; keep it and you keep a noon that is not said. So capability 5
**is capability 2** - the recited-writing serializer - not a filtered
capability 4. Capability 4 renders the *source* glyph sequence; 2 and 5 render
a different one.

**7. What else falls out, with no further work**

- **Teaching "why".** Every rule instance carries its participants, so "why is
  this raa heavy?" is answered by the `tafkheem` row rather than by re-running
  the rule in the UI.
- **Boundary rehearsal.** Two `Mappings` for one ref stopped at different
  words, diffed: exactly what changes if you stop here.
- **Variant diffing.** The same, varying `variant` - the only way to show a
  reader both wajhs of a disputed raa side by side.
- **Cross-script proof.** Uthmani and IndoPak `Mappings` for one ref must
  agree on `units`, `sounds` and `rules` and differ only in `glyphs` and
  `spellings`. That is the claim the riwayah-agnostic design is named for,
  expressible as a document comparison.
- **Corpus search.** Every site of a rule, or of a rule on a given letter, or
  of a rule that crosses a word boundary.
- **Alignment targets.** Sounds with their word allocation and rule labels,
  without the SDK re-slicing words or maintaining an "indexable unit"
  coordinate space to exclude render-only markers.

### 2.2 Granularity: one faithful relation, one fold over it

An earlier draft called display ownership "deliberately withheld". That was
wrong. What ADR-013 §2 forbids is a **stored** owner on a sound - when a
haraka and its carrier both supply one nucleus, no single stored value serves
both a faithful renderer and a font renderer. It does not forbid *shipping*
the policies, and shipping them is what stops each consumer inventing one.
That has already happened twice: `ts-source.ts::lettersFromCells` and
`qua-sdk/cells.py` each wrote their own, with the tiebreak living in a comment.

**The wire carries `faithful` only.** Every glyph, every `presents` edge,
including `بَ` as two glyphs presenting two sounds. Two groupings ship:

| `grouping` | One row per | For |
|---|---|---|
| `faithful` | glyph | the primitive; MFA allocation, letter-to-sound animation |
| `font` | base letter plus the combining marks a font shapes with it | font-based animation and highlighting |

`font` is not always 1:1 or even 2:1. A tanween cell is three glyphs' worth of
fact in one mark; an iltiqa site puts a sound between two cells that no cell
owns. The rows carry whatever `presents` says, and the partition law below is
what keeps that honest.

Legacy's `letter_phoneme_mappings` grouping is **not** a third policy. It is
`font` plus legacy's silent-merge policy, and it lives in the legacy adapter
(02-gate §3.4) where the rest of the legacy presentation already lives.

**Ownership is a parameter of `cells`, not a second method.** Every grouping
must **partition the glyph array and cover every sound exactly once** - that
is a gate law, so a fold that drops or duplicates a sound fails rather than
producing a plausible misalignment. Satisfying it *is* resolving ownership, so
there is nothing left for a separate timeline call to do:

| `owner` | Picks | For |
|---|---|---|
| `carrier` | the length carrier over the consonant's haraka | what QUA and the legacy frontend do today; keeps a consonant's highlight from smearing across the whole vowel |
| `first` | the first presenting glyph in source order | faithful letter-by-letter animation |

Silent-glyph co-highlighting composes from the same two pieces: `silences()`
gives per-glyph silence with its reason and the grouping gives the cell it
sits in, so "grey it inside its cell" and "skip it" are both derivable.

---

## 3. The naming rules this document applies

So that the next name is decidable rather than argued.

**N1. The domain's own word wins, written in plain ASCII.** If Hafs teaching
has a term - `tanween`, `madd`, `idgham`, `qalqala`, `sakt`, `silah`, `waqf`,
`wasl`, `riwayah`, `haraka`, `shadda` - use it, not the English linguistics
calque. Nobody reading a mushaf says "nunation".

**N2. Plain English wins where the domain has no word.** There is no Arabic
term for "the row that says which position produced this sound". `hosts`,
`sound`, `word`, `glyph` are structure, not doctrine.

**N3. A structure is never named after a rule.** `Silah` was both a rule and a
nucleus kind, so `unit.nucleus.kind == "silah"` and `rule == "silah"` were
different claims spelled identically. Resolved by deleting the rule (§5), not
by renaming around it.

**N4. A field says what it holds, not how it was derived.** `spelled` holds
"is part of a spoken letter name" and reads as "is written".

**N5. Two near-synonyms may not carry a load-bearing distinction.**
`Evidences` against `Attests`: both mean "provides evidence for", and the
contract needs them to mean two very different things.

**N6. No abbreviations on the wire.** `cls` is Python; JSON has room for
`kind`.

**N7. Booleans take `is_`.** **[owner]** `is_tanween`, `is_letter_name`,
`is_started_on`, `is_stopped_on`. A noun-shaped boolean reads as a field
holding that noun.

**N8. Infrastructure does not sit beside domain facts.** A field only the
producer and the cache care about goes under `provenance`, so the document's
top level is words, glyphs, units, sounds, rules and their edges - and nothing
a reader has to skip past.

**N9. One concept, one representation.** If the same fact is reachable two
ways, one of them is deleted. This retires `m.tokens()` in favour of the
`phonemes` projection, and `Junction` in favour of the two booleans that were
already the only thing anyone read.

---

## 4. The register

### 4.1 The envelope

Split in two, by N8. What a reader needs is at the top; what a cache needs is
under `provenance`.

| Name | Where | Means | Notes |
|---|---|---|---|
| `ref` | top | the passage: `"2:255"`, `"2:255:3-2:256:1"` | addresses words, not only verses (04 open question 4) |
| `variant` | top | the variant readings selected | **[owner]** `variant: VariantSelection`. R12's `khilaf` is rejected |
| `words` ... `contributions` | top | the nine arrays | |
| `riwayah`, `script` | `provenance` | which transmission, which mushaf | |
| `notation` | `provenance` | which phoneme alphabet, e.g. `"ipa"` | **kept, and this is the justification**: `Sound.token` is a string whose meaning depends on it, so a document without this field cannot say what its own tokens mean. Not kept on the theory that someone will pick another |
| `schema_version` | `provenance` | | |
| `canon_digest` **RENAME** | `provenance` | identifies the canonical data the indices were resolved against | pure cache correctness: two documents are comparable only if it matches. `score_digest` exposes `Score`, an internal layer name a consumer cannot decode |

**Dropped: `boundaries` / `BoundaryPlan`.** It was a third copy of a fact the
words already carry. See 4.2.

### 4.2 `Word`

**[owner] `Junction` leaves the public surface.** A word is started on,
stopped on, both, or neither - that is the whole boundary fact, and it is what
the domain calls ibtidaa, waqf and wasl. Checked against the source: the only
readers of the four-member enum are `stopped_on`, `started_on`, and one
lookahead block in `neighbourhood.py` that treats a sakt like a stop for
cross-word rules. Three booleans cover all three.

| Name | Means |
|---|---|
| `location` | `surah:ayah:word` - the join key every downstream system already uses |
| `text` | the source word as written |
| `is_started_on` | recitation begins here (ibtidaa) |
| `is_stopped_on` | recitation pauses after this word (waqf). The last word of a request is stopped on |
| `sakt_after` | a breathless pause after this word: not a stop, but cross-word rules are blocked |
| `stop_sign` **RENAME** | the mushaf's sign, if any: `preferred_stop`, `compulsory_stop`, ... |

The invariant, which a consumer can check: **`is_started_on` for word N+1 is
true exactly when word N `is_stopped_on`** - with one exception, and it is the
reason `sakt_after` is its own field: after a sakt the next word is *not*
started on, because a sakt is mid-wasl.

`advice` becomes `stop_sign` because that is what it is on the page. The
values already carry the advisory meaning; the field name does not need to.

**`lexeme` is dropped.** **[owner]** One field for one word. The only lam that
is ever heavy is the divine name's, so a `tafkheem` instance on a lam is
already unambiguous, and a consumer that wants to name the word can read it.

### 4.3 `Unit`

A **unit** is one letter together with the vowel state that follows it: the
thing a rule fires on. Not the same as a written cluster - some units are
written by several glyphs, some glyphs write several units, and the noon
inside a tanween is written by no glyph of its own.

| Name | Means | Notes |
|---|---|---|
| `letter` | which of the 30 | the 28 plus hamza and taa marbuta; phonological, so no alef maqsura and no alef wasla |
| `onset` | the consonant's state: `plain \| geminate \| wasl \| silah \| tashil` | |
| `nucleus` | the vowel state | |
| `is_tanween` **RENAME** | this unit is the noon of a tanween | R1 + N7. `nunation` is the English calque; every teaching source says tanween |
| `is_letter_name` **RENAME** | part of a letter's spoken name (`ص` -> `s`,`aa`,`d`) | R2 + N7. `spelled` reads as "is written" |
| `Part` **RENAME** | `onset \| nucleus`, the two halves a rule addresses separately | `Aspect` means something else in linguistics and suggests nothing about halves of a unit |

**No annotation field.** **[owner]** Imala, ishmam and tashil reach the
consumer as *rules*, because that is what they are. The canonical fact stays
internal, where `write` needs it for the round-trip (04 B2), and the mark that
writes it is a `tajweed_mark` glyph. Nothing called "annotation" appears in
the public document.

### 4.4 `Nucleus` variants

| Name | Means |
|---|---|
| `Silent` | no vowel here |
| `Short(quality)` | fatha, damma, kasra |
| `Long(quality)` | a madd letter's vowel |
| `LongWhenJoined(quality)` **RENAME** | the pronoun haa's silah: long in wasl, absent at pause. States the condition, and `Rule.SILAH` is deleted (below) so nothing is spelled two ways |
| `LongWhenStopped(quality)` **RENAME** | the seven alifs: short in wasl, long at pause. `PausalLong` does not say which way round it goes - which is exactly the confusion 04 M1 found live in the engine |

### 4.5 `Glyph`

| Name | Means | Notes |
|---|---|---|
| `Glyph` | one Unicode scalar the script wrote | `Grapheme`, the model's word, is the least accurate: in Unicode a grapheme is a *cluster* |
| `char` | the scalar | |
| `kind` **RENAME** | what the mark is | `cls` is a Python abbreviation (N6) |
| `word_index` | ordinal within its word - the legacy join key | 04 M8 |
| `source_index` | ordinal in the whole requested passage | what the concatenation law walks |

`kind` values, with two renamed:

`base` · `haraka` · `tanween` · `shadda` · **`vowel_letter`** *(was
`length_carrier`)* · `small_vowel` · `madd_sign` · `silence_sign` ·
**`tajweed_mark`** *(was `annotation`)* · `stop_sign` *(was `advice`)* ·
`structural`

- **`vowel_letter`**, because the set was inconsistent: `small_vowel` names a
  mark by its size, `length_carrier` named its neighbour by its function. The
  domain (`domain-facts.md` §1.1) calls them vowel letters and small vowels,
  so both are now named for what they are.
- **`tajweed_mark`**, because `annotation` was the vague member of an
  otherwise specific set - `madd_sign` and `silence_sign` say what they mark
  and this one did not. It covers the imala, ishmam and tashil marks: marks
  that name a manner of recitation.

### 4.6 `Sound`

`Sound` is the node; `token` is one field of it. **They are not the same
thing, and the reason is measurable.** Legacy shipped only tokens, so every
consumer answered questions about sounds with *string tests over the token*:
`is_madd(ph)` was `":" in ph`, `is_geminate(ph)` split the string in half and
compared, `is_nasalised(ph)` matched against a set loaded from YAML
(`b3bc53a:phonemes.py`). Those exist because the structure was thrown away and
had to be guessed back out of the spelling.

| Name | Means |
|---|---|
| `word` | which word it is credited to - for a merged sound, the **host**'s word (04 B3) |
| `token` | the selected notation's spelling, e.g. `"m̃m̃"` |
| `kind` + variant fields **RENAME** | `consonant \| vowel \| ghunnah \| release`, flattened onto the node rather than nested under a field called `spec` |

`consonant{letter, geminate, emphatic, ghunnah}` · `vowel{quality, long,
emphatic}` · `ghunnah{place, emphatic}` · `release{kind}`.

**`nasal` becomes `ghunnah` everywhere.** **[owner]** On a noon or a meem
"nasal" reads as tautological, which is why it looked like it added nothing.
It is not saying the letter is a nasal - it is saying the letter is **held
with ghunnah**, which for a noon changes `nn` to `ñ`. The domain has a word
for that and it is the one to use (N1). The standalone `ghunnah` kind is the
hum of ikhfaa and iqlab, which belongs to no letter at all: `place` is
`bilabial` for iqlab, `assimilated` for ikhfaa.

`Ghunnah.emphatic` **stays**. **[owner]** An ikhfaa before an istilaa letter
is heavy - `domain-facts.md` §5.5 says the ghunnah is coloured by the letter
after it - and legacy had a `heavy_phoneme` for exactly this. What legacy then
did was set it to `ŋ`, the same string as `light_phoneme`, which retired the
distinction in the notation while keeping it in the model. The field is right;
see **04 B9** for what has to change so anything can set it.

When `ghunnah` is set the alphabet ignores `geminate`, because a held nasal is
already the sound of a doubled letter - a model redundancy worth recording
rather than publishing.

**Geminate is a feature, not a kind.** A doubled consonant is still a
consonant, and it can also be emphatic or nasal; making `geminate` a fifth
kind would make those combinations unsayable. Same reasoning as `long` on a
vowel. A flat record with every field optional would admit impossible sounds,
which is why this is a union at all.

### 4.7 `RuleInstance`

**RENAME, [owner].** `Occurrence` does not say occurrence *of what*. The array
is `rules`, so `m.rules` answers "which rules apply here" and
`m.rules[0].rule` is its name.

| Name | Means |
|---|---|
| `rule` | one of the 39 |
| `source` | the unit the rule is about |
| `target` | the other unit it names; absent when the rule names only one |

**There is no `participants` array, no `Participant` type and no role enum.**
**[owner]** The census over the whole corpus in both boundary modes:

```
participants per rule instance:   1 -> 155,039     2 -> 95,389     3 -> 0
```

Nothing anywhere has a third, so a variable-length list of role-labelled
references was three layers of structure over a pair. Two fields carry it, and
`source`/`target` are legacy's own two words, so that part of the adapter is
an identity map. In `min rabbihim`: `source` is the sakin noon, `target` the
following raa.

The earlier four-role proposal is withdrawn entirely. `context` had zero
producers - the same defect class as B6 - and `target` as a *role* restated
where the attribution edge already lands, which is a second copy that can
disagree.

This still fixes what C1 was for: `PausalGlide` passes its pair reversed
(00-audit F2), and two named fields correct that as well as four roles would.

One wrinkle: arity is per instance, not per rule. `waqf_ending` has one
participant 43,548 times and two 6,756 times, because `TanweenAtWaqf` also
mints it - so `target` is optional per row, not per rule.

`RuleFamily` and `Phase` are not fields here. They are total functions of
`rule`, published as versioned tables.

### 4.8 The four edge families

Subject matters. Three attribution edges state something a *unit* does; one
states something with no unit at all.

| Edge | Subject | Means |
|---|---|---|
| **spellings** | | |
| `Supplies(glyph, unit, fact)` **RENAME** | the glyph | supplies a canonical fact: this fatha *is* the unit's vowel |
| `Witnesses(glyph, family, unit)` **RENAME** | the glyph | witnesses that a rule of this family happens here without supplying any canonical fact: a word-initial shadda witnesses an assimilation from the previous word |
| `Decorates(glyph, unit)` | the glyph | supplies and asserts nothing, but is bound to the unit it marks: the maddah |
| `Structural(glyph)` | the glyph | belongs to no word: space, verse marker, tatweel |
| **attributions** | | |
| `Hosts(units, part, sound, by?)` | the units | these units produce this sound. Several units is joint ownership, not a preferred owner |
| `MergedInto(units, part, sound, by?)` | the units | this unit disappeared into that sound. A merger **is** the `Hosts`/`MergedInto` pair sharing a sound and a rule instance |
| `Silent(units, part, by?)` | the units | this unit lost its sound, and `by` says which rule took it |
| `Insertion(anchor, side, part, sound, by?)` **RENAME** | nobody | a sound no unit owns, placed before or after an anchor. Renamed from `Inserted` because it is the one edge whose subject is not a unit |
| **modifiers** | | |
| `Recolours(sound, by, feature, value)` | the rule | tafkheem made this consonant heavy. The domain's own word |
| `SetsLength(sound, by, length)` **RENAME** | the rule | iltiqa shortened this madd. `Relengths` is a coined verb |
| `Classifies(sound, by)` | the rule | names this sound without changing it: every madd, every izhar, tarqeeq, tashil |
| **contributions** | | |
| `presents` | the glyph | one row per non-structural glyph, listing the outcomes it is the mark for. **An empty list means the glyph contributes to nothing heard** |

**`WrittenOnly` / `OrthographicOnly` is dropped.** **[owner]** Two edge kinds
for one question was over-built. `contributions` becomes one row per
non-structural glyph with a possibly-empty `presents` list, which keeps the
totality the gate needs - a glyph *missing* from the array is a bug, a glyph
present with an empty list is a deliberate statement - without a second type.
The read API then reports one `reason` field that is either a rule name or the
literal `orthographic`.

**`Supplies` / `Witnesses` is the rename with the strongest case.**
`Evidences` and `Attests` are near-synonyms carrying the contract's sharpest
distinction: one is a claim about the *canonical text* made by the script
adapter, the other a claim about the *performance* made with no knowledge of
which rule fired. 04's open question 5 existed because the drafts' own authors
could not tell them apart. The model may keep `Attests` for
`tools/attest.py`; the namespaced module makes that legal.

### 4.9 `by`, and what its absence means

`by` is the index of the rule instance responsible, and it is **optional**
(04 B4). No `by` means no rule claimed this: what the script writes, realized
by default.

```json
{"kind": "hosts", "units": [0], "part": "onset", "sound": 0}
{"kind": "hosts", "units": [5], "part": "onset", "sound": 5, "by": 2}
```

The first is the `k` of `kitaab`. There is no `plain` rule in the public
vocabulary, because absence is the honest encoding of absence.

---

## 5. The legacy vocabulary, and why it is not the public one

Legacy had 33 rule names; the public set has **39**. Six legacy names are the
same rule with the trigger baked in:

| Legacy pair | Public | The trigger is read from |
|---|---|---|
| `ikhfaa_noon` / `ikhfaa_tanween` | `ikhfaa_haqiqi` | `unit.is_tanween` |
| `iqlab_noon` / `iqlab_tanween` | `iqlab` | `unit.is_tanween` |
| `idgham_ghunnah_noon` / `_tanween` | `idgham_bi_ghunnah` | `unit.is_tanween` |
| `idgham_bila_ghunnah_noon` / `_tanween` | `idgham_bila_ghunnah` | `unit.is_tanween` |
| `noon_ghunnah` / `meem_ghunnah` | `ghunnah_mushaddadah` | `unit.letter` |
| `hamza_wasl_fatha` / `_kasra` / `_damma` | `wasl_start` | `unit.nucleus.quality` |

A rule is a rule; what triggered it is data on a node. Baking the trigger into
the name makes every new trigger a new enum member and a breaking release, and
it is why legacy needed six hand-maintained classification tables to answer
questions a participant already answers.

The rest is renames (`madd_arid_lissukun` -> `madd_arid_lil_sukun`,
`lam_shamsiyah` -> `lam_shamsiyyah`, `hamza_wasl_silent` -> `wasl_elision`)
and 14 additions legacy could not name - every izhar, `tarqeeq`, `iwad`,
`qalqala_akbar`, `ibdal_hamza`, `imala`, `tashil`, `ishmam`, `sakt`,
`waqf_ending`.

**`waqf_ending` is deleted, and split into what it does.** **[owner]** It names
a *cause* - the reciter stopped - where every other rule names an effect, and
it is currently carrying six unrelated outcomes. The effects are already
enumerated in `domain-facts.md` §7:

| One of today's `waqf_ending` instances | What actually happens | Becomes |
|---|---|---|
| a final short nucleus is silenced | the diacritic is not pronounced | `pausal_sukun` |
| dammatan or kasratan | the same thing - a final diacritic not pronounced. `unit.is_tanween` already says which it was | `pausal_sukun` |
| a `LongWhenJoined` nucleus is silenced | the silah vowel is absent | `pausal_sukun` |
| a `LongWhenStopped` nucleus is realized long | the seven alifs sound | `madd_tabii` |
| taa marbuta realized as heh | `ة` sounds as `h` | `taa_marbuta_pausal` |
| the yaa ithbat's onset is silenced | at the pause this unit is not pronounced | `pausal_sukun`. **[owner]** One site, `ءَاتَىٰنِۦَ` 27:36, and it is already a khilaf point - `variant` carries `YAA_ITHBAT`, which says which wajh was taken. A rule of its own would name what the selection already names |
| fathatan lengthens the base | the substitute alif | `iwad`, unchanged |

39 becomes 40, and that is the right direction: a name that says what happened
beats one name covering six things because they share a cause. Two of the six
turn out to be `pausal_sukun` as well, so the split adds two names and removes
one.

**Where "long when paused" lives, since `madd_tabii` does not say it.** In the
nucleus kind. `LongWhenStopped` says *when* - short joined, long at pause -
and `madd_tabii` says *what kind of madd* it is once long, and owns the
`Hosts` edge. Two facts, two places, neither repeated. What has to move is the
realization: today `WaqfEnding` emits it in the BOUNDARY phase, and it belongs
in the madd classifier, which is in the LENGTH phase and already reads the
boundary plan. That move is tied to **04 M1** - once the plain path stops
making `LongWhenStopped` long unconditionally, something boundary-aware has to,
and the madd classifier is the only place that both reads boundaries and owns
madd.

**No `waqf` rule family is added.** The cause is already in the document -
`word.is_stopped_on` - so "everything the stop did to this word" is a filter,
not a taxonomy. It correctly also catches `madd_arid_lil_sukun`,
`qalqala_kubra` and `qalqala_akbar`, which are effects of stopping too and
would have to be duplicated into any waqf family.

**The two iwads are one iwad, and that is correct.** Verified at 2:22:11
`مَآءً` stopped: `m a: ʔ a:`, with one `iwad` instance whose participants are
the tanween noon and the hamza - structurally identical to `هُدًى` at 2:5:3,
where the base is a dal. The hamza is simply what the base happens to be. Both
are one fact: fathatan on a base at waqf lengthens the base's vowel.

**`Rule.SILAH` is deleted.** **[owner]** A silah *is* a madd on the pronoun
haa, and the two facts it was carrying are both already stated elsewhere: the
nucleus kind `LongWhenJoined` says it is long joined and absent at pause, and
`MaddClass` already picks the right madd for it - `madd_tabii` normally,
`madd_jaiz_munfasil` when a hamza follows, which is the silah kubra. A rule
whose entire content is "this is the nucleus kind you can already read" is a
second spelling of one fact. 40 becomes 39, and the `Silah`/`silah`
structure-versus-rule collision (N3) goes with it rather than being renamed
around.

Two legacy names are retired: **`vowel_silent`**, the catch-all for 4,568 rows
where legacy had no better reason, now replaced by a real rule name or the
literal `orthographic`; and **`mode="simple"`**, retired by owner decision.

**One grouping axis. [owner]** `RuleFamily` is published - `assimilation`,
`nasalization`, `insertion`, `lengthening`, `emphasis`, `release`, `elision` -
as an *effect* class, what a script adapter can see. It is deliberately not a
teaching taxonomy; a consumer wanting the textbook grouping builds it from the
closed 40-member `rule`.

---

## 6. Every rename, collected

Accept or reject individually. "Public only" means the model keeps its name
and the namespaced public module differs, which 04 M11 makes legal.

| # | From | To | Reach | Cost |
|---|---|---|---|---|
| R1 | `nunation` | `is_tanween` | public + `SlotOrigin` under D1 | none beyond D1 |
| R2 | `spelled` | `is_letter_name` | public + `Slot.spelled` under D1 | same |
| R3 | `Aspect` | `Part` | model + public | a type name; no values change |
| R4 | `cls` | `kind` | public only | one wire field |
| R5 | `spec` nested | `kind` + variant fields inline | public only | wire shape |
| R6 | `Inserted` | `Insertion` | public only | a type name |
| R7 | `Relengths` | `SetsLength` | public only | a type name |
| R8 | `Occurrence` | `RuleInstance`, array `rules` | public only | a type name |
| R9 | `Evidences` / `Attests` | `Supplies` / `Witnesses` | public only | two type names |
| R10 | `Silah` / `PausalLong` kinds | `LongWhenJoined` / `LongWhenStopped` | model + public | two `NucleusKind` values, so digests move - land with D1 |
| R11 | `score_digest` | `canon_digest`, under `provenance` | public only | one field |
| R12 | `advice` | `stop_sign` | public only | one field |
| R13 | `starts` | `is_started_on`, and `Junction` dropped | public only | removes two fields, adds one |
| R14 | `source_index` | split into `word_index` + `source_index` | public only | one added field; fixes 04 M8 |
| R15 | `length_carrier` | `vowel_letter` | public only | one enum value |
| R16 | `annotation` glyph kind | `tajweed_mark` | public only | one enum value |
| R17 | `nasal` on a consonant, `Nasal` kind, `NasalPlace` | `ghunnah`, `Ghunnah`, `GhunnahPlace` | model + public | three names; no values change |

**Withdrawn:** the earlier R12 (`selection` -> `khilaf`) is rejected by the
owner; `variant` stays. The earlier R15 (`Junction` values to `wasl`/`waqf`)
is moot - the enum leaves the public surface entirely.

**Deletions, which are not renames.** Each removes a way of saying something
the contract already says another way:

| Deleted | Because |
|---|---|
| `m.tokens()`, `m.tokens_by_word()` | the `phonemes` projection owns the token stream and its splitting |
| `m.timeline()` | the partition law already makes every grouping resolve ownership |
| the `letter` grouping | it is `font` plus legacy's silent-merge policy; it belongs in the legacy adapter |
| `boundaries` on the request, and `Junction` | three per-word booleans carry everything anything reads |
| `lexeme` | one field for one word, and a heavy lam is already unambiguous |
| `Rule.SILAH` | the nucleus kind plus the madd rule already say it |
| `participants`, `Participant`, `ParticipantRole` | nothing has three participants; two fields carry it |
| `OrthographicOnly` | an empty `presents` list says it with no second edge kind |

## 7. Open, for the owner

1. **`Unit`.** Still content-free. `Letter` is what a consumer reaches for and
   is wrong for the tanween noon and for `Unit.letter`. Nothing considered is
   better.
2. **`Mappings`.** Settled, re-raised only because a plural noun for one
   document reads like a bag. `Reading` and `Recitation` are both taken.
