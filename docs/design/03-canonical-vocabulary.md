# 03 - Canonical vocabulary resolved before projections

Status: **resolved as a design decision**. Implementation is scheduled before
ADR-010 is accepted. Audit: “Modelling, before projections become a contract”.

## Why this had a deadline

A `Slot` is what a projection ultimately anchors. Once internal vocabulary
leaks into consumers' match statements, changing it becomes a breaking release.
The projection audit makes the boundary clear: the public trace exposes anchor
aspect, realization effect, lexical relationships and occurrences—not these
internal storage types.

## Decisions

### Split `Onset` into manner and presence

`PLAIN`, `GEMINATE` and `TASHIL` describe articulation. `WASL` and `SILAH`
describe boundary-conditional presence. They are independent questions, and
one enum forbids combinations without a cross-riwayah domain reason.

`Slot` will instead carry:

* `onset_manner`: plain, geminate or tashil; and
* `onset_presence`: always, when-started or when-connected.

Waṣl is `when-started`; the exceptional onset-silah site is
`when-connected`. Rules then inspect only the axis they mean. The public trace
does not expose either enum; it exposes the resulting anchor/realization.

### Replace `SlotOrigin` with provenance membership

`WRITTEN` means “neither of the other values” and says nothing: script
writtenness lives in `Inscription.Spelling`. Existing branches ask either “is
this nunation?” or “is this part of a spelled letter name?”.

Replace the enum with an independent provenance set whose closed members are
`SPELLED` and `NUNATION`; ordinary slots use the empty set. Membership permits a
future combination without claiming Hafs contains one. Update round-trip
digests and every call site from enum equality to the question it asks.

### Replace `Annotation` with lexical class and processes

The claim that `Annotation` changes no sound is false. `DIVINE_NAME` is read by
tafkheem, and `IMALA`/`ISHMAM` are read by the classifier to create named
realizations or occurrences.

Delete the container, not the facts:

* `DIVINE_NAME` becomes an optional lexical class on the slot/lexeme; and
* `IMALA` and `ISHMAM` become members of a recitation-process set.

Imala remains attached regardless of which vowel quality a khilaf selects. The
public trace exposes the lexical relationship and resulting occurrences, not a
misleading sound-neutral tag collection.

### Retain `Silah` and `PausalLong` nuclei

These are boundary-conditional canonical functions, not cached outcomes.
`Silah` is long when connected and absent at pause; `PausalLong` is short when
connected and long at pause. A boundary-free Score must state which function a
plan will resolve. Flattening to a plain nucleus would move lexical knowledge
into a detector and force recited writing to reconstruct it. `Relength`
performs the selected branch; it does not make the conditional fact redundant.

## Audit findings

1. Current `Onset` consumers ask either manner (`GEMINATE`, `TASHIL`) or
   presence (`WASL`, `SILAH`). No branch requires the mixed union.
2. `SlotOrigin` consumers ask either nunation (boundary/writing) or spelled
   expansion (muqattaat/noon). No consumer positively needs `WRITTEN`.
3. Every current `Annotation` member participates in classification or sound;
   the sound-neutral invariant cannot be repaired with a docstring tweak.
4. Conditional nuclei are correct before choosing a boundary plan: the plan
   selects a branch but does not create the lexical fact.

## Migration order

1. Split `Annotation`, updating digest and classifier fixtures.
2. Replace `SlotOrigin`, updating serialization, rules, writing and muqattaat
   fixtures.
3. Split onset manner/presence, updating triggers and conflict keys.
4. Keep conditional nuclei and test both outcomes under distinct plans.

This work precedes freezing `trace`, but replacement types remain internal.

## Acceptance

* Every `Slot` field answers one question.
* No enum member means “none of the others”.
* No type claims sound-neutrality while a sound/classification rule reads it.
* Wasl/silah and manner combinations are representable without enum growth.
* Both conditional nucleus outcomes are tested from the same Score under two
  plans.
* Projection fixtures preserve the same anchors, realizations, sounds and
  occurrences through the migration.
