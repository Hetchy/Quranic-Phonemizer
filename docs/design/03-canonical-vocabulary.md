# 03 - The canonical vocabulary, before projections fix it

Status: **open**, and time-boxed. Audit: "Modelling, before projections become
a contract".

## Why this one has a deadline

A `Slot` is what a projection projects. Once `anchored`, the mualem view and
the tajweed mapping are public, `Onset` and `SlotOrigin` are in a consumer's
`match` statement and changing them is a breaking release. Every other
document on this list can wait; this one gets more expensive on a schedule.

The audit rejected refactoring `SlotOrigin` on the grounds that no audited
Warsh case needs two of its axes at once. That rejection is about *urgency*,
not about correctness -- the enum is still answering three questions. What
follows is the decision that rejection deferred.

## The three

### `Onset`

`PLAIN`, `GEMINATE`, `TASHIL` describe how the consonant is articulated.
`WASL`, `SILAH` describe whether it is there and what connects it. Two
orthogonal axes in one field, so the model cannot state "geminate and wasl"
even though nothing in the domain forbids the combination.

Options: split into `manner` and `presence`; or keep one enum and document the
combinations as genuinely impossible. The second is defensible only if someone
establishes that they *are* impossible -- across riwayat, not just in Hafs.

### `SlotOrigin`

`WRITTEN`, `SPELLED`, `NUNATION`. Three questions: did the script write it,
is it part of a spelled letter name, did it come from tanween. `WRITTEN`
carries no information -- it means "none of the others". A slot cannot be both
spelled and nunation, and no domain fact says it may not be.

Both `rules/boundary.py` and `rules/noon_sakinah.py` branch on this, and the
round-trip digest hashes it, so it is load-bearing. That makes it a
decomposition, not a deletion: three booleans, or a small set, or two fields.

### `Annotation`

Documented as "changes no sound". `DIVINE_NAME` changes sound, through
`rules/tafkheem.py:136`. Either the documentation is wrong, or `DIVINE_NAME`
is not an annotation.

The cheap reading -- rewrite the docstring -- is the wrong one. The stated
invariant is what lets a projection ignore annotations when computing
phonemes. If it does not hold, the type name is doing no work, and the honest
rename is `SlotTag`: a tag a slot carries, with no promise about sound.

`IMALA` staying an `Annotation` after moving out of `Quality` was judged
correct: the named process persists whichever vowel the khilaf selects. That
judgement does not extend to `DIVINE_NAME`.

### `PausalLong` and `Silah`

Both are `Nucleus` kinds. Both are statements about a boundary -- what this
vowel becomes when the reciter stops, what a pronoun vowel does before a
consonant. Wearing a nucleus kind makes them look like inherent length.

Open: whether the boundary fact belongs on the slot at all, or whether the
nucleus should be plain and the boundary rule should produce the length. The
second is cleaner and much larger; `engine/run.py` `_plain_sound` already
reads a `Relength` override, so the machinery exists.

## What to audit before deciding

1. **Enumerate the impossible combinations.** For `Onset`, every
   manner-presence pair, marked possible or impossible with a domain reason.
   A pair that is impossible only in Hafs is possible.
2. **Count the branches.** Every `match` and `is` on `SlotOrigin` in `rules/`
   and `render/`, and which of its three questions each one is asking. If
   every branch asks one question, the decomposition is mechanical.
3. **Audit `Annotation` members against sound.** For each, does any rule read
   it and emit a different sound. `DIVINE_NAME` is known; establish whether it
   is alone.
4. **Check `PausalLong` against the boundary plan.** Whether a `PausalLong`
   nucleus is ever correct at a slot the plan does not stop at. If it never
   is, it is a boundary fact and the nucleus kind is a cache.

## Ordering

`Annotation` first: smallest, and the answer is forced once the census is
done. `Onset` second. `SlotOrigin` third. `PausalLong`/`Silah` last, and only
if 4 shows the redundancy is real.

## Acceptance

- Every `Slot` field answers one question.
- No enum member means "none of the others".
- Any type documented as sound-neutral is sound-neutral, checked by a test
  that renders with and without it.
