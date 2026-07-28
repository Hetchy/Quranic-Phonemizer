# 05 - Adjacency, pass order, and slot identity

Status: **open**, lowest urgency. Audit: "Abstraction".

Four separate defects that share one cause: `canon.build` and `rules/` have no
agreed vocabulary for *where a slot is*, so each caller invents one.

## The four

### Slot adjacency is reimplemented per rule module

Named helpers today:

| module | helpers |
|---|---|
| `rules/boundary.py` | `_previous`, `_is_first_of_word`, `_is_last_of_word` |
| `rules/madd.py` | `_before` |
| `rules/tafkheem.py` | `_before` |

Three modules, three implementations of two questions. The audit measured
23,526 extra `Score.slots()` calls and about 1,686,196 extra slot items
inspected over a full corpus run, but the cost is not the argument -- three
copies of "the slot before this one" can disagree about a word boundary, and
one of them would be wrong for a whole class of verses without any test
noticing.

`engine/neighbourhood.py` already exists and already knows the boundary plan.
The question is whether adjacency belongs there (it has the plan, so it can
answer "previous, joined or not") or on `Score` (it has the words, so it can
answer "first of word" without a plan). They are different questions and may
have different homes.

### `build` falls back to `LEXEME_PASSES`

`build(reading, passes=None)` uses `canon/passes.py:LEXEME_PASSES`. So there
are two ways a pass list arrives and the default is the shared two. A riwayah
that forgets to supply its own list gets a working pipeline that is silently
not its own.

Options: make `passes` required; or introduce a `BuildProfile` carrying the
pass list with whatever else a riwayah configures about building, constructed
by the composition root and never defaulted. The second is better if there
turns out to be more than one such knob -- establish whether there is.

Related and smaller: `cross_word_noon` returns a role name, so `canon` matches
on an orthography string to find the slot it created. It should return the
slot.

### `Scribe` keys on `id()`

`canon/scribe.py` links graphemes to draft slots by `id()` of a mutable
object, valid only while `build`'s list is alive, and drops the link silently
when the lookup misses. A dropped link is a written character anchored to no
sound -- invisible in output, invisible in tests, and exactly the kind of
thing the attestation gate exists to catch but cannot, because the gate reads
the links that survived.

Two changes, both uncontroversial in direction: give a draft a stable
identity, and make a miss raise. The design content is only in what the
identity is -- an ordinal assigned at draft creation is the obvious answer and
survives the reordering that passes do, but that needs checking against
`_skip_iwad_carrier` and the tanween split, both of which consume drafts.

### The five-object pass signature

A `LexemePass` takes `(reading, drafts, lexicon, scribe, selection)` whether
it needs all five or not. 26 `del` statements across the package exist to say
"accepted and deliberately ignored", concentrated in `rules/boundary.py` (6),
`rules/madd.py` (3) and `rules/annotation.py` (3).

`del` is honest -- it makes the unused parameter explicit rather than letting
a linter suppress it -- so this is not a bug. It is a signature that grew by
addition. A context object would collapse it, at the cost of making every
pass's true dependencies invisible, which is the thing the `del`s currently
make visible.

Open, and genuinely two-sided: is the explicitness worth 26 lines.

## What to audit before deciding

1. **Diff the three adjacency implementations** against each other on a full
   corpus run: for every slot, does each implementation return the same
   answer. A disagreement is a live bug and promotes this document.
2. **Count the riwayah build knobs.** If `passes` is the only one,
   `BuildProfile` is premature and "make it required" is the answer.
3. **Trace draft identity through the passes** that create, split or drop
   drafts, and establish whether an ordinal assigned at creation stays stable.
4. **For each `del`, whether the parameter is unused by that pass or unused
   by that pass today.** The second is a signature that will need it back.

## Why this is last

Nothing here blocks Warsh, and nothing here is wrong in output. Item 1 could
change that -- if the three adjacency implementations disagree anywhere, this
document moves to the top of the list.

## Acceptance

- One implementation of "the slot before this one" and one of "first/last of
  word".
- No pass list arrives by default.
- A `Scribe` miss raises and names the address.
