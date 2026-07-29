# 05 - The five-object pass signature

Status: **open**, lowest urgency, and the last item of what was a four-part
document. Audit: "Abstraction". The other three parts are
[ADR-011](../adr/011-where-a-slot-is.md).

## What is left

A `LexemePass` takes `(reading, drafts, lexicon, scribe, selection)` whether
it needs all five or not. 27 `del` statements across the package exist to say
"accepted and deliberately ignored", concentrated in `rules/boundary.py` (6),
`rules/annotation.py` (3) and `rules/madd.py` (3).

`del` is honest -- it makes the unused parameter explicit rather than letting
a linter suppress it -- so this is not a bug. It is a signature that grew by
addition. A context object would collapse it, at the cost of making every
pass's true dependencies invisible, which is the thing the `del`s currently
make visible.

Open, and genuinely two-sided: is the explicitness worth 27 lines.

## What to audit before deciding

For each `del`, whether the parameter is unused by that pass or unused by
that pass *today*. The second is a signature that will need it back, and a
context object would hide the moment it does.

A second reading worth pricing: passes that need three of the five could
declare which, and the caller supply only those. That keeps dependencies
visible without the `del`s, but it needs a registration mechanism, and
`canon/derive/vocabulary.py` is the cautionary example -- ADR-010 records
that its `requires` tuples over-declare massively and are checked as a union
because a per-derivation check would be a lie.

## What went elsewhere

- **Slot adjacency, the pass-list default, and `Scribe`'s draft identity** --
  [ADR-011](../adr/011-where-a-slot-is.md). Adjacency moved onto
  `Neighbourhood`, `passes` became required, and a dropped edge now raises
  instead of vanishing.
- **`cross_word_noon` returning a role name** rather than the slot it created
  -- [08](08-what-a-second-riwayah-decides.md), under `requires` as a
  description. The builder greps the role name, so a script fact decides a
  canonical question; the fix is the derivation returning the slot, and it is
  bound up with what `requires` is allowed to mean.

## Why this is last

Nothing here blocks Warsh and nothing here is wrong in output. Unlike the
three items that left, this one has no measurement that would settle it --
only a preference about what a signature should show.

## Acceptance

- Either the signature is unchanged and this document is closed as "no
  change", or every pass's true dependencies are visible without `del`.
