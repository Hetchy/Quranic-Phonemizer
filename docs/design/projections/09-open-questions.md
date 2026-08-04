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

## 8. `08`'s `shortened` derivation

[08-legacy-parity](08-legacy-parity.md) section 3 derives the shard's
`shortened` status from "the glyph is in `silent` under `iltiqa_shortening`".
E14 says the opposite for the one word that exercises it: the shortened carrier
"is in no `silent` list either, because the shortening took a length and
silenced no part".

**Settled by** deriving it from `respelling` instead, where the dropped carrier
is visible, and rewriting section 3's row.

---

## 10. A tatweel seating a dagger is structural by class and not by edge

Item 19 says there is one notion of structural and it is the `Structural` edge,
and B1 moved the stop sign and the bare tatweel onto it. One case did not move:
a tatweel that seats a dagger is `kind="structural"` and carries no `Structural`
edge, so it takes a pairing. `2:255` has four, which makes this visible on the
contract's own headline example:

```
glyph 17, 117, 345, 375   char U+0640   kind structural   Structural edge absent
```

`02-gate` section 4.5 says a non-structural glyph is in some pairing and a
structural one is in none. A glyph that answers "structural" to one question and
"not structural" to the other satisfies neither reading.

**Settled by** deciding what a seat is when the thing it seats is the sounding
glyph. The dagger sounds and the tatweel under it does not, so the seat is
structural and the edge is what is missing; but B1 deliberately gave a seat a
`Decorates` edge, and those two answers are not compatible.

## 11. `replace()` on a `PhonemizeResult` returns a broken object

`PhonemizeResult` holds its assembled graph in `_assembled`, set after
construction because the projections need more than the published arrays.
Section 3 names sixteen members and not that one, so it was taken off the
dataclass field list. The consequence is that `dataclasses.replace()` succeeds
and returns an object on which every method raises `AttributeError`.

Both available fixes trade one wrong behaviour for another: putting the field
back publishes a seventeenth member the contract does not name, and leaving it
off keeps a public frozen dataclass that fails the one operation frozen
dataclasses exist for.

**Settled by** deciding whether the projections derive from the published arrays
alone. If they can, `_assembled` goes and the question with it. If they cannot,
the contract should say that a result is built and not copied.

---

Entries 10 and 11 came from implementation contact rather than from the four
document reviews, which is what the register said would happen.

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
exactly, including `fakk_idgham` and `pausal_alif`, which phase D minted.
`comment_lint` and `structure_lint` report no problems and the suite passes.
