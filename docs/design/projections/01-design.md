# 01 - Two projections

Status: **proposed**. Depends on [00-audit](00-audit.md) and on
[03-canonical-vocabulary](../03-canonical-vocabulary.md) being resolved.
Scope: Uthmani, Hafs.

## 1. The decision

Two public projections, and no third.

| | Name | Shape | For |
|---|---|---|---|
| **P1** | `phonemes` | `tuple[str, ...]`, plus a per-word split | everyone who wants only sound |
| **P2** | `Reading` | five parallel node arrays joined by integer index | everyone else |

`Reading` replaces `character_phoneme_mappings`, `letter_phoneme_mappings`,
`silent_flags` and `tajweed_mappings` -- all four -- with no loss. It is one
document because the four were one join computed four times (00-audit §1), and
because a set of "atomic" projections over a graph is a set of tables a consumer
must re-join, which is the thing that went wrong.

It does not couple, because the arrays are independently ignorable. A tajweed
colourer for a mushaf reads `words`, `glyphs`, `units`, `rules` and never
touches `phonemes`. An ASR labeller reads `phonemes` and `rules`. Ignoring an
array costs nothing; re-joining two documents costs correctness.

## 2. The key: a unit, not a character

This is the load-bearing choice, and it is what the legacy projections got
wrong.

Legacy keyed rows on **written characters**, so anything recited but not written
had no row. It grew `chars=""` implicit cells and a five-member `status` enum
(`present`/`inserted`/`dropped`/`replaced`/`shortened`) to describe the gap, and
downstream consumers still had to synthesize `madd_iwad`, `allah_dagger_alef`,
`iltiqaa_kasra` and an iqlab mini-meem for themselves.

`Reading` keys on the **`Slot`** -- published as `Unit`. A `Slot` is
boundary-free and script-free: it exists whether or not this script wrote it and
whether or not it sounds at this junction. Every legacy implicit cell is an
ordinary unit:

| Legacy implicit cell | Unit |
|---|---|
| hamza-wasl connecting vowel | a unit with `Onset.WASL` and a short nucleus |
| iltiqa kasra (3:1) | an `Inserted` sound anchored to a unit |
| Allah dagger alef | a unit with a `LONG` nucleus and the `divine_name` tag |
| madd-iwad alef | a unit with a `PAUSAL_LONG` nucleus |
| muqattaat name letters | units with `spelled = true` |

Nothing is invented, and `status` disappears -- not because consumers stop
wanting those five treatments, but because each is now *derived* from facts:

```
inserted  = unit.graphemes == () and unit.glyphs != ""
dropped   = unit.graphemes != () and unit.sounds == ()
replaced  = unit.glyphs differs from the text its graphemes spell
shortened = a rule with `iltiqa_repair` names the unit
present   = otherwise
```

The producer ships facts; the renderer keeps its vocabulary.

## 3. `Reading`

One request: a ref, a stop-sign policy (which advice classes are honoured), a
riwayah, a `VariantSelection`. One document.

```python
@dataclass(frozen=True)
class Reading:
    ref: str
    riwayah: Riwayah
    script: Script
    notation: str                      # the Alphabet that produced the tokens
    selection: VariantSelection
    words:    tuple[Word, ...]
    glyphs:   tuple[Glyph, ...]
    units:    tuple[Unit, ...]
    phonemes: tuple[Phoneme, ...]
    rules:    tuple[RuleHit, ...]
```

Every cross-reference is an integer index into one of the five arrays, in both
directions. Ids stay available as strings for stable external addressing.

### 3.1 `Word`

```python
location: Location          # 2:20:3
text: str                   # the script's own word, verbatim
spelled: str                # write() over this word's units
starts: bool                # recitation began here
stops: bool                 # recitation stopped after
junction: Junction          # join | sakt | stop | edge
advice: StopAdvice | None   # the mushaf's stop sign on this word
units: tuple[int, ...]
glyphs: tuple[int, ...]
```

`starts` / `stops` are the two facts every consumer re-derived from
`is_starting` / `is_stopping`; `junction` is the full four-way fact underneath
them. `advice` is new to a projection and comes free from `Inscription.advice`.

### 3.2 `Unit` -- the spine

```python
id: str                     # "2:20#7"
word: int
letter: CanonLetter
geminate: bool
prosthetic: bool            # Onset.WASL: present only when started on
conditional: bool           # this unit's presence or length depends on the junction
nucleus: Quality | None     # None when silent
length: NucleusKind         # silent | short | long | silah | pausal_long
nunation: bool              # the tanween noon
spelled: bool               # part of a muqattaat letter name
tags: tuple[SlotTag, ...]   # ishmam | divine_name | imala
graphemes: tuple[int, ...]  # what wrote it; () when unwritten
glyphs: str                 # what it looks like -- always non-empty
sounds: tuple[int, ...]     # what it produced here; () when silent
silenced_by: int | None     # index into `rules`
rules: tuple[int, ...]      # every rule naming this unit
```

`glyphs` is the answer to "the keys of pure script orthography are the wrong
choice". It is `write` applied to this one unit under this script's `Pen`, so it
is always non-empty and always spellable in the script the consumer is
rendering. When `graphemes` is empty, `glyphs` is the only thing to draw. When
`graphemes` is non-empty and `glyphs` differs from the text they spell, the
consumer has learned that the recited form and the written form diverge -- which
is exactly the `replaced` case, stated as two facts instead of one enum member.

`conditional` collapses `Onset.SILAH`, `NucleusKind.SILAH` and
`NucleusKind.PAUSAL_LONG` into the one thing a consumer must know: *do not read
this unit's length as inherent; the junction decided it*. The precise kind is
still in `length` for anyone who wants it.

### 3.3 `Glyph`

```python
id: str                     # "2:20@14"
word: int
char: str
cls: GraphemeClass          # base | haraka | tanween | shadda | length_carrier
                            # | small_vowel | madd_sign | silence_sign
                            # | annotation | advice | structural
index: int                  # ordinal within the word
units: tuple[int, ...]      # () for structural
fact: SlotFact | None       # letter | onset | nucleus | sakt | annotation
                            # None for Decorates / Attests
attests: RuleFamily | None  # from Attests
```

`cls` is `GraphemeClass` unchanged and replaces legacy `role` exactly:
`base`->`base`, `haraka`->`haraka`, `tanween`->`tanween`,
`madd`->`length_carrier | small_vowel | madd_sign`. It is a fact about the mark,
not a rendering slot, and it is finer than legacy's four.

A compact grapheme reaching many units (the `الٓمٓ` opening: three graphemes,
seven units) is `units` with length > 1. Legacy needed `source_letter_indices`
plus a parallel `phoneme_rule_tags` array for the same thing.

### 3.4 `Phoneme`

```python
id: int                     # == its index; the flat sequence position
word: int
token: str                  # the notation token
kind: str                   # consonant | vowel | nasal | release
letter: CanonLetter | None
quality: Quality | None
long: bool
geminate: bool
emphatic: bool
nasal: bool
units: tuple[int, ...]      # Hosts; () when Inserted
owner: int | None           # THE unit that displays it
merged_from: tuple[int, ...]# units whose own sound folded into this one
anchor: tuple[int, str] | None   # (unit, "before" | "after") when Inserted
rules: tuple[int, ...]      # every rule that produced, modified or classified it
```

Three fields earn their place:

- **`owner`.** Exactly one unit displays each sound. This is the fact
  `ts-source.ts::lettersFromCells` reimplements ("the carrier wins over the
  consonant's haraka") and gets to decide differently from the SDK. The rule is
  stated once here and tested: for a nucleus-aspect sound the owner is the last
  unit in `units`; for an onset-aspect sound, the first. `share_group`
  disappears -- co-highlighting is "every unit in `units`", and a disjoint
  animation is "the `owner` only".
- **`merged_from`.** The disappearing side of an idgham. Legacy needed
  `is_source` plus six rule-name tables to find it.
- **`rules` is a list.** `secondary_tags` and `phoneme_rule_tags` were two
  separate escape hatches for the fact that a sound carries more than one rule.
  Both go.

### 3.5 `RuleHit`

```python
id: int
rule: Rule
family: RuleFamily
phase: Phase
effect: str                 # hosts | insert | merge | silence | classify
at: int                     # the anchor unit
context: tuple[int, ...]    # the other participants
units: tuple[int, ...]      # at + context
phonemes: tuple[int, ...]   # every sound it produced, removed or coloured
```

`effect` replaces legacy's `source_rules` / `target_rules` partition, and is
strictly more informative. On a cross-word idgham, legacy put the rule in
`source_rules` on the disappearing noon and in `target_rules` on the receiving
letter -- one bit, recovered from a hand-maintained table. Here the same rule is
one `RuleHit` with `effect = merge`, `at` = the noon, `context` = the host, and
`phonemes` = the single shared sound. Both sides fall out.

`effect = classify` is the fix for finding F1: madd, tafkheem, izhar and the
other 15 classification-only rules get a hit with the sounds they name, so
`Phoneme.rules` is complete rather than "whatever attributed the sound".

## 4. Model changes this requires

Three, all small, all in `model/` and `engine/`. Nothing in `rules/` changes
behaviour.

**C1 -- label the participants** (fixes F2). `Participants` becomes

```python
@dataclass(frozen=True, slots=True)
class Participants:
    at: SlotId
    context: tuple[SlotId, ...] = ()
```

21 call sites, mechanical. `rules/madd.py:69` is the one that changes meaning:
its `(before.id, at)` becomes `at=at, context=(before.id,)`, matching every
other rule. Without this the `at` / `context` split in `RuleHit` is a guess.

**C2 -- keep the modifier edge** (fixes F3). `engine/run.py` consumes `Recolour`
and `Relength` and discards which occurrence emitted them. Record them:

```python
@dataclass(frozen=True, slots=True)
class Modifies:
    sound: SoundId
    by: OccurrenceId
```

added to the `Attribution` union or carried as a separate
`Performance.modifiers` tuple. Separate tuple is preferred: `Modifies` does not
own a sound, and the P1 law ("every sound is hosted exactly once") should not
have to special-case it.

**C3 -- a composition root** (fixes F4). Not a design question, but it is the
gate on shipping. It takes `(ref, stop policy, riwayah, selection)` and returns
`Reading`; the boundary plan is derived from the policy plus `Inscription.advice`
plus verse ends, which is what `engine/boundary_plan.py` should grow beyond
`all_join`.

Deliberately **not** changed:

- `CLASSIFICATION_ONLY` stays. It is the correct statement that a rule owns no
  sound; C2 gives it an edge without giving it ownership.
- `SlotOrigin` decomposition, `Annotation` naming: see
  [03](../03-canonical-vocabulary.md), which this design assumes resolved.
- `Onset` splitting: not required. `Reading` publishes `geminate` and
  `prosthetic` as separate booleans regardless of the internal enum shape,
  which is the whole point of a projection.

## 5. Rule vocabulary

**Keep the branch `Rule` set unchanged.** Three properties make it better than
legacy's and all three should survive:

1. **Trigger-independent naming.** One `IKHFAA_HAQIQI`, not `ikhfaa_noon` +
   `ikhfaa_tanween`. The trigger is `unit.nunation`, which the consumer has. A
   rule name that encodes its own trigger multiplies with every new trigger.
2. **`FAMILY_OF` is total.** Every rule declares a `RuleFamily`, so a consumer
   that does not want 40 colours gets 7 for free and a new rule lands in an
   existing bucket instead of falling off the legend.
3. **Degrees are separate members.** `QALQALA_SUGHRA` / `KUBRA` / `AKBAR`,
   `IDGHAM_MUTAJANISAYN_KAMIL` / `NAQIS`. A projection that cannot say which
   degree fired is not a tajweed projection.

One rename to consider and one to reject:

- `Rule.PLAIN` is the plain-fill sentinel, not a tajweed rule. In `RuleHit` it
  should either be omitted (a sound with no `rules` entry is plain) or kept with
  `family = ELISION`, which is wrong. **Omit it.** A `Phoneme` with empty `rules`
  is plain; that is one less vocabulary item a consumer must learn to ignore.
- Do **not** split `TAFKHEEM` by cause (istilaa vs raa vs divine name). The
  cause is recoverable from `at.letter` and `at.tags`, and splitting re-imports
  legacy's trigger-in-the-name mistake.

## 6. What each application gets

| Application | Reads | Was |
|---|---|---|
| Inspector cells | `glyphs`, `units`, `phonemes`, `rules` | `character_phoneme_mappings` + 2 FE surgeries + 7 synthesized tags |
| Silent co-highlight | `unit.sounds == ()`; the mark is the neighbouring `silence_sign` glyph | `silent_flags` |
| Aligner letter timing | `phoneme.owner` for disjoint spans, `phoneme.units` for co-light | `lettersFromCells` heuristic |
| Cross-word bridge | a `RuleHit` with `effect = merge` and units in two words | `detect_cross_word_mergers` + 2 re-exported rule sets |
| Flat char-to-phoneme runs | `units` with `graphemes` and `sounds` | `letter_phoneme_mappings` |
| Tajweed-coloured mushaf | `glyphs` -> `units` -> `rules` | `tajweed_mappings` |
| Tajweed ASR / error detection | `phonemes` + `phoneme.rules` + `selection`, with `khilaf().points()` for the alternatives | not possible |
| Custom notation | swap the `Alphabet`; `token` changes, nothing else does | not possible |

## 7. Open questions

1. **Multi-verse documents.** Finding F5. Ids are already `VerseRef`-qualified,
   so a `Reading` over a range is concatenation plus a decision about whether
   array indices restart. Proposal: they do not -- one `Reading`, one index
   space, `word.location` carries the verse.
2. **`Unit.glyphs` guarantee.** Blocked on ADR-005 §4's totality gate (F6). If
   `write` cannot spell a recited form, `glyphs` needs a nullable escape and the
   ADR-005 refusal of a fourth layer has failed its own trigger.
3. **Serialization.** Legacy shipped positional tuples and grew four
   append-only slots. `Reading` should ship named JSON; the positional shard row
   is the *consumer's* encoding, not the producer's, and the SDK already
   projects into a different field order. This wants stating so it does not
   recur.
4. **Does the Uthmani inventory read `ۢ`?** Finding F10. If not, `Glyph.units`
   will not attach the iqlab small meem and the frontend surgery survives.
