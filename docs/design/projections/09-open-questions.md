# 09 - What this set has not settled

Status: **proposed**. Scope: Uthmani, Hafs.

Four independent adversarial reviews were run against this set, two model
families, two rounds, each blind to the others. Their agreed findings were
applied. What is below is what survived: places where the set states two
incompatible things, or one thing the corpus or the package refutes, and where
choosing between them wants a producer rather than another reading.

**This register is the merge condition.** The set merges as a proposal with its
open questions written down, not as a document that claims to be consistent.
Every entry names what would settle it. An entry that implementation closes
should be struck from here in the same change.

The two rounds overlapped on a fifth of what they found, so the list below is a
sample of the remaining defects and not a floor under them. Read it as evidence
about where the set is soft, rather than as a complete inventory.

---

## 1. The set deletes two working variant points

[01-contract](01-contract.md) section 3.1 says "The two nasal placement points
are not here: see section 4.4", and section 4.4 says the hum "needs no place of
articulation" because "the shipped data does not site" the choice. Section 9
item 10 removes the standalone nasal type that carries the place.

The package answers otherwise. `KhilafId.IQLAB_NASAL` and
`KhilafId.IKHFAA_SHAFAWI_NASAL` are live, and a selection naming one changes the
token:

```
2:27:5  default   m i ŋ
2:27:5  bilabial  m i m̃
```

The point has no per-site rows in `khilaf.yaml`, which is what "does not site"
meant, but a whole-point selection needs none. Under this contract both
readings would leave `available_variants`, `variants`, `r.variant`, the graph
and `phonemes()` together, and the rule name cannot carry the difference
because it is `iqlab` either way.

**Settled by** deciding whether a hum has a published place. If it does, the
`Sound` for a nasal consonant needs the field and section 3.1 needs the two
points back.

## 2. `Block` is not total

[01-contract](01-contract.md) section 6.3 says "No block has an empty
`source`", on the grounds that a rendered glyph the source did not produce still
writes a sound and the closure over sounds places it beside the pairing that
owns it. Three cases resist:

- A soundless insertion. [06-two-texts](06-two-texts.md) row 12 writes a sukun
  that owns nothing, so no sound closure reaches it.
- A structural deletion. A tatweel and a verse marker take no pairing at all,
  so no block can state that recitation drops them.
- The divine name's carrier. E4 prints a block with an empty source and says so
  in prose, while E13 draws the same word as one block holding the carrier
  beside the cell whose length it carries. Two examples, one phenomenon, two
  partitions.

**Settled by** implementing `respelling` over the corpus and seeing which shape
the writer actually needs. E13's is the one this document believes.

## 3. `tashil` has no producer path

[01-contract](01-contract.md) section 3.2 offers `tashil` as an optional
phoneme, and section 9 item 39 says the optional phonemes "reach no node and no
edge, so the gate belongs beside the alphabet and nowhere in the producer". But
section 4.4's consonant `Sound` publishes `letter`, `geminate`, `emphatic` and
`ghunnah`, and section 9 item 1 says "Manner is not published at all". The
notation is handed a `Sound` and nothing else, so with the toggle on it cannot
tell an eased hamza from a plain one. E21 states the same thing from the other
side: the ease "is a `Classifies` edge and no field of the sound".

The other three toggles each have a field behind them. This one does not.

**Settled by** either publishing manner on the hamza's sound, which is what the
other three do, or dropping the toggle. The corpus has one site, `41:44:9`.

## 5. Rule effects disagree between 07 and 01

[07-rules](07-rules.md) section 1 maps "setting a length" onto the modifier
family, then gives `madd_tabii`, wajib, jaiz, lazim and arid the effect "sets
the length". [01-contract](01-contract.md) section 9 calls
`madd_arid_lil_sukun` classification-only and requires `Classifies`, and
reserves `SetsLength` for a real relength. The package agrees with the
contract: `rules/madd.py` classifies these and only the iltiqa repair emits a
relength.

The same split reaches `imala`, which section 2.5 says "sets the vowel's
quality" while section 5 publishes no modifier that can carry a quality change,
and `khilaf.yaml` resolves the quality at build time as an annotation.

**Settled by** one pass over section 2's effect column against the three
modifier edges, once the producer exists to say which rules own which.

## 6. Laws that name a case they then exclude

Three, all one sentence each, all pointing at a real graph the law rejects.

- **Stop effects.** [01-contract](01-contract.md) section 7.2 calls them
  "Mutually exclusive per unit and per part". E8 gives one taa marbuta unit
  `taa_marbuta_pausal` on its consonant and `pausal_sukun` on its vowel. They
  are exclusive per part and not per unit.
- **`tafkheem`'s trigger.** [07-rules](07-rules.md) gives it trigger `-` and
  crosses `never`, while the divine name's lam reads a vowel that can be in the
  previous word, which E13 prints.
- **`MergedInto.by`.** [01-contract](01-contract.md) section 5 publishes it
  optional and then defines a merger as a pair "sharing a sound and a rule".
  The model has it mandatory.

**Settled by** writing the completeness suite, which is where a law that cannot
hold announces itself.

## 7. The wire format is not specified

[01-contract](01-contract.md) opens by promising a consumer never reads
`model/`. Two things a consumer needs are not here.

- **Discriminators.** `Witnesses(glyph, unit)` and `Decorates(glyph, unit)` have
  identical payloads, and so do `Recolours(sound, by)` and
  `Classifies(sound, by)`. [02-gate](02-gate.md) requires tagged unions and
  canonical round trips; nothing names the tag or its literals.
- **Letter literals.** `Unit.letter` is "the twenty-eight, plus `hamza` and
  `taa_marbuta`". The prose says baa and yaa where the model says `ba` and
  `ya`, and `heh` for one letter and `ha` for another.

Also open: what `word_index` means on a structural glyph, which by section 4.3
has no word.

**Settled by** section 9 item 2's versioned schema, which is where these
literals get chosen.

## 8. `08`'s `shortened` derivation

[08-legacy-parity](08-legacy-parity.md) section 3 derives the shard's
`shortened` status from "the glyph is in `silent` under `iltiqa_shortening`".
E14 says the opposite for the one word that exercises it: the shortened carrier
"is in no `silent` list either, because the shortening took a length and
silenced no part".

**Settled by** deriving it from `respelling` instead, where the dropped carrier
is visible, and rewriting section 3's row.

## 9. `rendered` and the stop signs

[06-two-texts](06-two-texts.md) section 1 says a thing recitation does not say
is absent from the recited text. Row 30 keeps every stop sign and calls it
"advice and not recitation". E14 relies on the sign being kept.

**Settled by** saying which of the two `r.text("recited")` serializes, and
whether the answer is the same as what `rendered` holds.

---

## What was checked and holds

Recorded because a register of defects with no counterweight reads as a verdict
on the whole set.

Every phoneme line in E1 through E21 reproduces the package at head, including
the three the preamble declares and no undeclared one. `raa_tafkheem` has nine
sites with differing defaults, `seen_sad` and both nasal points have no sited
rows, and no vowel takes quality `e` under the default. `when_joined` has
exactly one site. Section 9's own claims check out where they are countable:
`tafkheem` is the largest instance class and every instance of it owns nothing,
the iltiqa repair owns nothing, and every release in the corpus sits on the
vowel. The rule vocabulary in [01-contract](01-contract.md) section 7 matches
[07-rules](07-rules.md) section 2 and [03-examples](03-examples.md) section 3.1
exactly. `comment_lint` and `structure_lint` report no problems and the suite
passes.
