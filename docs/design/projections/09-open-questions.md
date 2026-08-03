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

## 6. Laws that name a case they then exclude

Two, all one sentence each, both pointing at a real graph the law rejects.

**Stop effects** is closed: [decisions](units/decisions.md) settles it and unit
C1 reworded section 7.2 to say per part, not per unit.

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
