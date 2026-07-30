# 05 - The public contract, in plain words

Status: **proposed**, and the thing to argue with before any code is written.
Scope: Uthmani, Hafs.

This document is not a tajweed glossary. It is the contract explained for
someone who has never read `model/`, plus a name-by-name audit with the
alternatives that were rejected, so the naming can be reviewed rather than
inherited.

Everything marked **RENAME** is a proposal, not a decision. Each carries its
cost. Reject them individually.

---

## 1. Read this much and stop

`Mappings` is one document, and you almost never walk it yourself. It has
methods for the things consumers actually ask for, each returning a small
record with the joins already done. The graph underneath is what you reach for
when no method fits - not where you start.

### "Which tajweed rules apply to this verse?"

```python
m = mappings("2:255")

for hit in m.rules():
    print(hit.rule, hit.source.letter, hit.trigger.letter)
    # ikhfaa_haqiqi  noon  jeem
    # madd_lazim     ya    meem
    # tafkheem       sad   -
```

`hit.rule` is one of 40 names. `hit.source`, `hit.trigger`, `hit.target` are
the units involved, already resolved. `hit.tokens` is what it sounds like and
`hit.glyphs` is what to point at.

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
    print(s.glyph.char, s.rule)
    # ٱ  wasl_elision
    # ل  lam_shamsiyyah
    # ا  -            (written-only: the otiose alif, no rule took it)
```

`s.rule` is `None` for a glyph that never fed a sound in the first place -
the otiose alif, the carrier under a dagger - as opposed to one a rule
silenced. Legacy could not tell those apart.

### "Just the phonemes"

```python
m.tokens()            # ('ʔ', 'a', 'l', 'lˤ', 'a:', 'h', 'u', ...)
m.tokens_by_word()    # (('ʔ','a','l','lˤ','a:','h','u'), ...)
```

Or use the `phonemes` projection, which is these tokens and nothing else, and
does not change when the graph does.

### The rest of the surface

```text
m.rules_at(word=3)               the same hits, filtered
m.letters()                      the legacy letter-to-phoneme grouping
m.recited_text()                 the words respelled as recited
m.display_glyph(sound, policy)   which glyph to paint for one sound
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
      +--------- contributions ---> [ Occurrence ] <---- modifiers --------+
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

---

### 2.1 What this shape lets you build

The seven capabilities the contract is being bought for, each traced to the
edges that answer it and the model work it still needs. "Needs" means the
graph shape is right and the producer is not finished, not that the design is
in doubt.

| | Capability | Reads | Needs |
|---|---|---|---|
| 1 | rule -> phoneme | `attributions.by` and `modifiers.by` on the sound | **C2** (modifier edges are discarded today), **C5**, B1's law |
| 2 | rule -> recited letter, waqf and wasl applied | recited-writing serializer over `write` + contributions | **C3**, **C4**; gated on `write` totality (F6) |
| 3 | rule -> source glyph | participants -> units -> `spellings` | **C3** |
| 4 | recited text, silent glyphs greyed | source glyph order + `Presents(Silent)` vs `WrittenOnly` | **C3** |
| 5 | recited text, silent glyphs omitted | **not** 4 minus rows - see below | **C3**, **C4**, F6 |
| 6 | glyph <-> phoneme, N to M | `contributions` | **C3** |
| 7 | everything else | below | |

**On 3, "some rules have nowhere to point".** Fewer than expected, and the set
is *queryable* rather than guessed: a unit with no `supplies(fact=nucleus)`
edge has an unwritten vowel, and a sound with no `Presents` edge has no glyph
at all. Both named worries turn out to point somewhere:

- **The divine name's long `aa`.** In `ٱللَّهِ` (1:1:2) there is a dagger alef
  and it supplies the nucleus. In `لِلَّهِ` (1:2:2) there is **no dagger in the
  rasm at all** - and the fatha supplies the nucleus by itself, because the
  length is a lexical fact the build derives. Two spellings, both with a
  glyph to point at, and neither is the one a reader would guess.
- **Madd iwad.** At 2:5:3 stopped, the `iwad` occurrence lengthens the dal's
  vowel, and that vowel is supplied by the **tanween mark** `ً`. The alef
  maqsura seat `ى` only `decorates` - it is the otiose companion, not the
  source of the length.

What genuinely has no glyph is an **inserted** sound, and there is exactly one
kind: the helping kasra of iltiqa al-sakinayn. It is placed by
`Insertion(anchor, side)` between two glyphs rather than on one. See **04 B6** -
today the package emits none at all.

**On 5, the trap.** "Recited text with silent letters omitted" is *not*
"recited text with silent letters greyed, minus those rows", because **a glyph
is not atomically silent**. The single tanween mark `ً` at 2:5:3 supplies
three facts across two units: the dal's vowel, the noon's letter, and the
noon's silence. At waqf the noon half goes silent and the vowel half
lengthens into the iwad. Delete the glyph and you lose the vowel; keep it and
you keep a noon that is not said.

This is exactly where legacy needed split-extension rows and
`EXTENSION_FALLBACK_CHARS`. The contract handles it because `Presents` is
per-glyph-per-target - one glyph may present both a `hosts` and a `silent` -
but the honest answer to capability 5 is that it is **capability 2**, the
recited-writing serializer, not a filtered capability 4. Capability 4 is a
rendering of the *source* glyph sequence; capabilities 2 and 5 render a
*different* glyph sequence.

**On 6, one thing deliberately withheld.** The contract gives you every
glyph-sound link, including the many-to-many ones - a haraka and its carrier
both presenting one vowel, one muqattaat glyph presenting nine sounds, two
words' glyphs presenting one merged consonant. It does **not** tell you which
single glyph *owns* a sound for animation. That is `display_glyph(sound,
policy)`, a rendering policy, because when a haraka and its carrier supply the
same nucleus no stored owner can name which one to paint (ADR-013 §2).

**7. What else falls out, with no further work**

- **Teaching "why".** Every occurrence carries its participants, so "why is
  this raa heavy?" is answered by the `tafkheem` occurrence's `trigger`,
  rather than by re-running the rule in the UI.
- **Boundary rehearsal.** Two `Mappings` for one ref under different
  `boundaries`, diffed: exactly what changes if you stop here.
- **Khilaf diffing.** Same, varying `khilaf` instead - which is the only way
  to show a reader the two wajhs of a disputed raa side by side.
- **Cross-script proof.** Uthmani and IndoPak `Mappings` for one ref must
  agree on `units`, `sounds` and `occurrences` and differ only in `glyphs`
  and `spellings`. That is the claim the whole riwayah-agnostic design is
  named for, expressible as a document comparison.
- **Corpus search.** Every site of a rule, or of a rule on a given letter, or
  of a rule that crosses a word boundary.
- **Alignment targets.** Sounds with their word allocation and rule labels -
  what a tajweed-aware ASR or a forced aligner consumes, without the SDK
  re-slicing words or maintaining an "indexable unit" coordinate space to
  exclude render-only markers.
- **Custom notation.** The same graph with a different `token` serializer;
  nothing else in the document is notation-dependent.

## 3. The naming rules this document applies

So that the next name is decidable rather than argued.

**N1. The domain's own word wins, written in plain ASCII.** If Hafs teaching
has a term - `tanween`, `madd`, `idgham`, `qalqala`, `sakt`, `silah`, `waqf`,
`wasl`, `khilaf`, `riwayah`, `haraka`, `shadda` - use it. Not the English
linguistics calque for the same thing. Nobody reading a mushaf says
"nunation".

**N2. Plain English wins where the domain has no word.** There is no Arabic
term for "the row in the array that says which position produced this sound".
`hosts`, `sound`, `word`, `glyph`, `occurrence` are structure, not doctrine.

**N3. A structure is never named after a rule.** `Silah` is currently both a
rule and a nucleus kind, which means `unit.nucleus.kind == "silah"` and
`occurrence.rule == "silah"` are different claims spelled identically.

**N4. A field says what it holds, not how it was derived.** `spelled` holds
"is part of a spoken letter name" and reads as "is written".

**N5. Two names that are near-synonyms in English may not carry a load-bearing
distinction.** `Evidences` against `Attests` is the current example: both mean
"provides evidence for", and the contract needs them to mean two very
different things.

**N6. No abbreviations on the wire.** `cls` is Python; JSON has room for
`kind`.

---

## 4. The register

Columns: the name, what it holds in domain terms, why that word, and what was
considered and rejected. **RENAME** marks a proposal against the current
drafts.

### 4.1 The request envelope

| Name | Means | Why | Rejected |
|---|---|---|---|
| `Mappings` | the whole document for one request | carries the migration lineage: a consumer looking for `letter_phoneme_mappings` finds where their view went | `Reading` - `orthography/adapter.py` defines it and eight modules import it. `Recitation` - `api.py` defines it. Noted tension: a plural noun for one document reads like a bag, and this is the one name settled before the others |
| `ref` | the passage: `"2:255"`, `"2:255:3-2:256:1"` | legacy's word, short, and already what a caller types | `passage`, `range` - longer, no gain |
| `riwayah` | which transmission | N1 | `reading` - triple-booked |
| `script` | `uthmani` or `indopak` | plain and correct | `mushaf`, `orthography` |
| `notation` | which phoneme alphabet, e.g. `"ipa"` | it names the *choice*; `render/alphabet.py::Alphabet` is the table that choice selects | `alphabet` - that is the internal table, and publishing the same word for both is the collision this contract is trying to avoid |
| `khilaf` **RENAME** | the variant readings selected | N1. The model already has `KhilafId`; the wrapper being called `VariantSelection` is the only place the English is used | keep `selection: VariantSelection`. Cost of the rename: one field name and one type alias, no behaviour |
| `boundaries` | where the reciter starts, stops, joins, and takes a sakt | covers all four states; `waqf_plan` would name only one of them | `waqf`, `stops` |
| `canon_digest` **RENAME** | identifies the canonical data the indices were resolved against | `score_digest` exposes `Score`, an internal layer name with a musical metaphor a consumer has no way to decode | keep `score_digest`. Cost: one field name |

### 4.2 `Word`

| Name | Means | Why | Rejected |
|---|---|---|---|
| `location` | `surah:ayah:word` | the join key every downstream system already uses | |
| `text` | the source word as written | | |
| `started_on` **RENAME** | recitation begins at this word (ibtidaa) | `starts` reads as "this word starts something"; `started_on` says it is the reciter who started, and matches `BoundaryPlan.started_on` | keep `starts`; legacy's `is_starting` |
| `junction_after` | what happens after this word | it is the complete boundary fact, so a separate `stops` would be a second copy | `boundary_after`, `stop` |
| `Junction` values **RENAME** | `wasl \| sakt \| waqf \| edge` | N1. The domain's three states are literally wasl, waqf and ibtidaa (`domain-facts.md` §2); `join`/`stop` are the English calques of two of them, while `sakt` is already the domain word - so the current enum is half-translated | keep `join \| sakt \| stop \| edge`. Cost: this is a **model** enum, so its values are hashed into digests and every fixture regenerates. Land it with D1, which regenerates them anyway |
| `advice` | the mushaf's stop sign, if any | the sign advises; it does not decide | `stop_sign` - names the glyph, not the class |
| `lexeme` | lexical identity: currently only `divine_name` | D2: a lexical fact is not a recitation process | `divine_name: bool` - cannot grow; `word_class` - collides with grammatical class |

### 4.3 `Unit` - the one word to get right

A **unit** is one letter together with the vowel state that follows it. It is
the thing a rule fires on.

It is not the same as a written letter cluster. Some units are written by
several glyphs (a long vowel: haraka plus carrier). Some glyphs write several
units (a muqattaat letter: `ص` spells four). Some units are written by no
glyph of their own (the noon inside a tanween).

| Name | Means | Why | Rejected |
|---|---|---|---|
| `Unit` | one canonical position | deliberately content-free, because the thing it names is not any one of the words a reader would guess | `Letter` - readable, but a unit is letter *plus* vowel state, and `Letter.letter` is absurd. `Slot` - the internal name, equally content-free with no lineage. `Syllable` - wrong; a geminate spans two units. `Cluster` - `domain-facts.md` §1.1 already uses it for the *written* thing |
| `letter` | which of the 30 | `CanonLetter`: the 28 plus hamza and taa marbuta. Phonological identity, not glyphic - no alef maqsura, no alef wasla | |
| `onset` / `Onset` | the state of the consonant: `plain \| geminate \| wasl \| silah \| tashil` | phonologically exact, and the census (`03-vocabulary §4`) proved every impossible combination has a domain reason | `consonant: ConsonantState` - readable, but then `Sound`'s `Consonant` variant means something else and the two would be confused |
| `nucleus` / `Nucleus` | the vowel state | same | `vowel` - a `Silent` nucleus is not a vowel, and `Release` (qalqala) attaches here too |
| `Part` **RENAME** | `onset \| nucleus`, the two halves a rule can address separately | `Aspect` is the worst name in the surface: in linguistics "aspect" means something else entirely, and nothing about the word suggests "which half of a unit". `Part` needs no gloss | keep `Aspect`. Cost: a model enum name, no values change, no digest moves |
| `tanween` **RENAME** | this unit is the noon of a tanween | N1, and the reviewer's own example. `nunation` is the English linguistics calque; the corpus, the docs, and every teaching source say tanween | keep `nunation`. Cost: one public field plus `SlotOrigin.NUNATION` under D1, which is already being decomposed |
| `letter_name` **RENAME** | this unit is part of a letter's spoken name (`ص` -> `s`,`aa`,`d`) | N4. `spelled` reads as "is written", which is the opposite of useful next to `Glyph` and `spellings` | keep `spelled`; `muqattaat` - the mechanism is more general than the openings; `part_of_letter_name` - unambiguous but long, and offered as the fallback if `letter_name` reads as a string field |

### 4.4 `Nucleus` variants

| Name | Means | Why | Rejected |
|---|---|---|---|
| `Silent` | no vowel here | | `Sukun` - the sukun is a *mark*; a bare letter with no mark is equally silent |
| `Short(quality)` | fatha, damma, kasra | | |
| `Long(quality)` | a madd letter's vowel | | |
| `LongWhenJoined(quality)` **RENAME** | the pronoun haa's silah: long in wasl, absent at pause | N3 - `Silah` is currently both this and `Rule.SILAH`, so `kind == "silah"` and `rule == "silah"` are different claims spelled the same. The new name also *says* the condition instead of requiring the reader to know it | keep `Silah`. Cost: a model type name |
| `LongWhenStopped(quality)` **RENAME** | the seven alifs: short in wasl, long at pause | pairs with the above and states the condition. `PausalLong` is half-English half-jargon and does not say which way round it goes - which is exactly the confusion **04 M1** found live in the engine | keep `PausalLong` |

The pair is the point: these two are the *boundary-conditional* half of the
nucleus, and everything else is inherent. Naming them for their condition
makes `03-vocabulary §5`'s two axes visible in the values themselves rather
than in a docstring.

### 4.5 `Glyph`

| Name | Means | Why | Rejected |
|---|---|---|---|
| `Glyph` | one Unicode scalar the script wrote | | `Character` - friendliest, and legacy's `chars`, but ambiguous between scalar and cluster. `Grapheme` - the model's name and the least accurate of the three: in Unicode a grapheme is a *cluster*, and this is one scalar. `Scalar` - accurate, meaningless to a reader |
| `char` | the scalar itself | | |
| `kind` **RENAME** | `base \| haraka \| tanween \| shadda \| length_carrier \| small_vowel \| madd_sign \| silence_sign \| annotation \| advice \| structural` | N6: `cls` is a Python abbreviation, and JSON has room. The *values* are already domain words and stay | keep `cls`. Cost: one wire field name |
| `word_index` **RENAME/split** | the scalar's ordinal within its word | this is what `model/inscription.py:39` actually holds and what legacy's `source_letter_index` joins on. **04 M8**: the drafts currently call one field `source_index` and define it two incompatible ways | |
| `source_index` | the scalar's ordinal in the whole requested passage | what the concatenation law walks | |

### 4.6 `Sound`

| Name | Means | Why | Rejected |
|---|---|---|---|
| `Sound` | one segment that is heard | | `Phoneme` - these are not phonemes of a language, they are realized segments. `Phone` - accurate, jargon |
| `word` | which word it is credited to | for a merged sound this is the **host**'s word (04 B3 leg 1) | |
| `token` | the selected notation's spelling of it, e.g. `"m̃m̃"` | | `phoneme`, `ipa` - `ipa` is one notation among possible several |
| `kind` + variant fields **RENAME** | `consonant \| vowel \| nasal \| release`, flattened onto the node | the drafts nest the union under a field called `spec`, which says nothing. A tagged union inline is one fewer hop and is how the other four unions are already serialized | keep `spec: Consonant \| Vowel \| Nasal \| Release` |

The variants and their fields, unchanged: `consonant{letter, geminate,
emphatic, nasal}`, `vowel{quality, long, emphatic}`, `nasal{place, emphatic}`,
`release{kind}`. A flat record with every field optional would admit
impossible sounds, which is why this is a union at all.

### 4.7 `Occurrence`

| Name | Means | Why | Rejected |
|---|---|---|---|
| `Occurrence` | one firing of one rule at one place | not "rule": the same rule fires many times | `RuleInstance`, `Application`, `Tag` - legacy's word, and it is the flattening this design exists to undo |
| `rule` | one of the 40 | trigger-independent: one `ikhfaa_haqiqi` for noon and tanween alike. The trigger is read off the participant's `unit.tanween` | the legacy trigger-split names; see §5 |
| `participants` | who was involved, and how | | |
| `Participant{unit, part, role}` **RENAME** | flattened | the drafts nest `anchor: AspectRef{unit, aspect}`; nothing else references the inner type, so the nesting buys nothing | keep `anchor: AspectRef` |
| `role` | `trigger \| source \| target \| context` | see the table below | |

**Roles, stated once**, because 02-gate §3.3 and 01-design §3.5 currently
contradict each other on the idgham case (04 M6):

| Role | Means | In `min rabbihim` (idgham bila ghunnah) |
|---|---|---|
| `source` | the rule's canonical locus - the unit the rule is *about* | the sakin noon |
| `trigger` | the condition that made it applicable | the following raa |
| `target` | the affected anchor, where the outcome lands | the raa's onset, which is now doubled |
| `context` | a required participant with none of the above meanings | - |

`trigger` and `target` are the same unit here and are still two roles: one
says why the rule matched, the other says where it landed. The full
per-family assignment is settled in [06](06-examples.md), not here.

`RuleFamily` and `Phase` are **not** fields on an occurrence. They are total
functions of `rule`, published as versioned tables, so an occurrence never
carries a second classification that can drift from the first.

### 4.8 The four edge families

Subject matters. Three of the attribution edges state something a *unit*
does; one states something with no unit at all. That is the only irregularity
and it is worth knowing before reading them.

| Edge | Subject | Means |
|---|---|---|
| **spellings** | | |
| `Supplies(glyph, unit, fact)` **RENAME** | the glyph | supplies a canonical fact of the unit: this fatha *is* the unit's vowel |
| `Witnesses(glyph, family, unit)` **RENAME** | the glyph | witnesses that a rule of this family happens here, without supplying any canonical fact: a word-initial shadda witnesses an assimilation from the previous word |
| `Decorates(glyph, unit)` | the glyph | supplies nothing and asserts nothing, but is bound to the unit it marks: the maddah |
| `Structural(glyph)` | the glyph | belongs to no word at all: space, verse marker, tatweel, stop-sign scalar |
| **attributions** | | |
| `Hosts(units, part, sound, by?)` | the units | these units produce this sound. Several units means joint ownership, not a preferred owner |
| `MergedInto(units, part, sound, by?)` | the units | this unit disappeared into that sound. A merger **is** the `Hosts`/`MergedInto` pair sharing one sound and one occurrence; there is no `assimilated` flag |
| `Silent(units, part, by?)` | the units | this unit lost its sound, and `by` says which rule took it |
| `Insertion(anchor, side, part, sound, by?)` **RENAME** | nobody | a sound no unit owns, placed before or after an anchor unit: the 3:1 iltiqa kasra. Renamed from `Inserted` because it is the one edge whose subject is not a unit, and a noun says so |
| **modifiers** | | |
| `Recolours(sound, by, feature, value)` | the occurrence | tafkheem made this consonant heavy. The domain's own word (`domain-facts.md` §4) |
| `SetsLength(sound, by, length)` **RENAME** | the occurrence | iltiqa shortened this madd; ibdal lengthened that one. `Relengths` is a coined verb that exists nowhere else | keep `Relengths` |
| `Classifies(sound, by)` | the occurrence | this rule names this sound without changing it. Every madd, every izhar, tarqeeq, tashil |
| **contributions** | | |
| `Presents(glyph, target)` | the glyph | this is the mark you point at for that outcome. `target` is a tagged index: `{"to": "attribution", "index": 4}` |
| `WrittenOnly(glyph)` **RENAME** | the glyph | written, and contributes to nothing heard. Distinct from `Silent`: `Silent` is a *unit* whose sound a rule removed; this is a *glyph* that never fed one - the carrier waw under a dagger alef | keep `OrthographicOnly` |

**`Supplies` / `Witnesses` is the rename with the strongest case.** `Evidences`
and `Attests` are near-synonyms in English carrying the contract's sharpest
distinction: one is a claim about the *canonical text*, made by the script
adapter; the other is a claim about the *performance*, made with no knowledge
of which rule actually fired. A consumer cannot guess which is which from the
words, and 04's open question 5 existed precisely because the drafts' own
authors could not either. Cost: these are model type names with a lint gate
(`tools/attest.py`, `engine/laws.py::check_attestations`) built around the
second one, so the model may keep `Attests` while the public says `Witnesses`
- the namespaced module makes that legal.

### 4.9 `by`, and what its absence means

`by` is the index of the occurrence responsible. It is **optional**
(04 B4). No `by` means no rule claimed this outcome: it is what the script
writes, realized by default.

```json
{"kind": "hosts", "units": [0], "part": "onset", "sound": 0}
{"kind": "hosts", "units": [5], "part": "onset", "sound": 5, "by": 2}
```

The first is the `k` of `kitaab`. Nothing made it; it is just there. There is
no `plain` rule in the public vocabulary, because absence is the honest
encoding of absence, and because a `rules_by_sound()` that answers `["plain"]`
for most of the corpus is the exact complaint this redesign exists to fix.

---

## 5. The legacy vocabulary, and why it is not the public one

Legacy had 33 rule names; the branch has 40. Six legacy names are the same
rule with the trigger baked into the name:

| Legacy pair | Public | The trigger is read from |
|---|---|---|
| `ikhfaa_noon` / `ikhfaa_tanween` | `ikhfaa_haqiqi` | `unit.tanween` |
| `iqlab_noon` / `iqlab_tanween` | `iqlab` | `unit.tanween` |
| `idgham_ghunnah_noon` / `_tanween` | `idgham_bi_ghunnah` | `unit.tanween` |
| `idgham_bila_ghunnah_noon` / `_tanween` | `idgham_bila_ghunnah` | `unit.tanween` |
| `noon_ghunnah` / `meem_ghunnah` | `ghunnah_mushaddadah` | `unit.letter` |
| `hamza_wasl_fatha` / `_kasra` / `_damma` | `wasl_start` | `unit.nucleus.quality` |

A rule is a rule; what triggered it is data on a node. Baking the trigger into
the name means every new trigger is a new enum member and a breaking release,
and it is why legacy needed six hand-maintained classification tables to
answer questions the participant already answers.

The rest of the mapping is renames (`madd_arid_lissukun` ->
`madd_arid_lil_sukun`, `lam_shamsiyah` -> `lam_shamsiyyah`,
`hamza_wasl_silent` -> `wasl_elision`) and 15 additions the branch names that
legacy could not - every izhar, `tarqeeq`, `iwad`, `qalqala_akbar`,
`ibdal_hamza`, `imala`, `tashil`, `ishmam`, `silah`, `sakt`, `waqf_ending`.

Two legacy names have no successor and are retired by name:

- **`vowel_silent`** - the catch-all for "this letter produced nothing and we
  have no better reason". 4,568 attributions in the frozen baseline. In the
  new contract every `Silent` edge cites an occurrence with a real rule, so
  the catch-all has nothing to mean. Which real rules those 4,568 rows turn
  out to be is a measurement the gate reports (00-audit F9), not a name.
- **`mode="simple"`** - retired by owner decision in 03-review.

**One grouping axis, not two.** `RuleFamily` is published - `assimilation`,
`nasalization`, `insertion`, `lengthening`, `emphasis`, `release`, `elision` -
and it is an *effect* class: what a script adapter can see. It is deliberately
not a teaching taxonomy. `idgham_bi_ghunnah` is `assimilation` here even
though a tajweed textbook files it under "noon sakinah and tanween". A
consumer that wants the textbook grouping builds it from `rule`, which is a
closed 40-member enum; the contract does not ship a second classification it
would then have to version.

---

## 6. Every rename, collected

Accept or reject individually. "Public only" means the model keeps its current
name and the namespaced public module differs, which the 04 M11 decision makes
legal.

| # | From | To | Reach | Cost |
|---|---|---|---|---|
| R1 | `nunation` | `tanween` | public + `SlotOrigin` under D1 | none beyond D1, which already rewrites this field |
| R2 | `spelled` | `letter_name` | public + `Slot.spelled` under D1 | same |
| R3 | `Aspect` | `Part` | model + public | a type name; no values change, no digest moves |
| R4 | `cls` | `kind` | public only | one wire field |
| R5 | `spec` flattened into `Sound` | `kind` + variant fields | public only | wire shape only |
| R6 | `Inserted` | `Insertion` | public only | a type name |
| R7 | `Relengths` | `SetsLength` | public only | a type name |
| R8 | `OrthographicOnly` | `WrittenOnly` | public only | a type name |
| R9 | `Evidences` / `Attests` | `Supplies` / `Witnesses` | public only | two type names; the model keeps `Attests` for `tools/attest.py` |
| R10 | `Silah` / `PausalLong` nucleus kinds | `LongWhenJoined` / `LongWhenStopped` | model + public | two type names and two `NucleusKind` values, so digests move - land with D1 |
| R11 | `score_digest` | `canon_digest` | public only | one field |
| R12 | `selection: VariantSelection` | `khilaf: KhilafSelection` | public only | one field, one alias |
| R13 | `starts` | `started_on` | public only | one field |
| R14 | `source_index` | split into `word_index` + `source_index` | public only | one added field; fixes 04 M8 |
| R15 | `Junction` values `join`/`stop` | `wasl`/`waqf` | model + public | **the expensive one**: enum values are hashed into digests, so every ledger fixture regenerates. Only worth it if bundled with D1 |

R1, R2, R4, R14 fix things that are actively misleading. R3, R9, R10 fix
things that mislead more subtly and cost more. R15 is the only one that is
arguably not worth its price.

---

## 7. Open, for the owner

1. **`Unit`.** Is there a better word? `Letter` is what a consumer would
   reach for and is wrong for the tanween noon and for `Unit.letter`. Nothing
   else considered is better than content-free.
2. **Booleans.** `tanween`, `letter_name`, `started_on` are all
   noun-shaped booleans. The repo avoids `is_` prefixes (`Word.starts`, not
   `is_starting`), but `letter_name: bool` genuinely reads like a string
   field. Adopt `is_` for booleans whose name is a noun, or accept the
   ambiguity?
3. **R15.** Half-translated `Junction` values, or pay for the digest churn?
4. **`Mappings`.** Settled, and re-raised only because §4.1 names the
   tension: a plural noun for one document. `Reading` and `Recitation` are
   both taken, but nothing has been tried beyond those two.
