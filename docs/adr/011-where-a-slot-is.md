# ADR-011: Where a slot is, and which draft an edge means

Status: **accepted**. Closes three of the four items in design question 05.
Audit: "Abstraction".

## Context

`canon.build` and `rules/` had no agreed vocabulary for where a slot is, so
each caller invented one. Three of the four consequences the design question
listed had a single correct answer once measured; the fourth is still a
judgement call and stays open.

**Three implementations of "the slot before this one."** `boundary._previous`,
`madd._before` and `tafkheem._before` were the same algorithm — rebuild the
flat slot list with `Score.slots()`, scan it for the id, take the index
before. `engine/neighbourhood.py` already held that list, an index into it,
and the forward question `after()`. The cost was measurable but is not the
argument: three copies of one question can disagree about a word boundary,
and one of them would be wrong for a whole class of verses with no test
noticing.

**A pass list arriving by default.** `build(reading, passes=None)` fell back
to `canon.passes.LEXEME_PASSES`, so a riwayah that forgot to supply its own
got a working pipeline that was not its own.

**`Scribe` keying on `id()`.** Grapheme-to-slot edges were recorded against
`id()` of a mutable draft. A pass that dropped a draft took the key out of
`ordinals` with it, `_slot` returned `None`, and the edge was discarded in
silence. Measured over the corpus, both scripts: **1,283,790 edge lookups,
188 misses, in 30 verses** — every one a muqattaat opening, where
`canon/spell.py` replaces a word's drafts with the spelled letter names.
They were harmless only because that pass re-evidences what it splices in, so
the loss and the replacement cancelled. A written character anchored to no
sound is invisible in output and invisible to the attestation gate, which by
construction reads the links that survived.

## Decision

**One question, one implementation, on the object that already has the
index.** `before`, `first_of_word` and `last_of_word` join `after` on
`Neighbourhood`. The design question asked whether adjacency belongs there or
on `Score`; `Neighbourhood` wins both halves because it holds the flat order
and the word map, and answering from one index is what makes the answers
agree by construction rather than by review.

**No pass list arrives by default.** `passes` is required. There is no
`BuildProfile`: it is still the only per-riwayah build knob, so there is
nothing for one to carry. `LEXEME_PASSES` stays what it is — the shared two
that `riwayat.hafs` composes its list from — rather than a default.

**A draft has an identity, and losing an edge raises.** `_Draft` carries a
`uid` minted at creation; `assemble` keys ordinals on it; a miss is
`OrphanedEdgeError` naming the verse, the offset and the draft. A pass that
drops a draft now has to say what becomes of its edges: `spell_muqattaat`
calls `Scribe.withdraw(span)` rather than orphaning them.

### Why `before` ignores junctions when `after` blocks at them

`Neighbourhood.after()` returns `None` across a stop, because recitation ends
there and a rule that cannot be heard across a pause must not fire across it.
`before()` does not, because the slot behind a stop *was* said. That is what
all three deleted copies did, so this ADR preserves behaviour rather than
choosing it.

It is recorded here because it was written down nowhere, and because **no
gate distinguishes the two readings**. Making `before` block at junctions
leaves all eight gates and every other test passing. One test in
`tests/test_neighbourhood.py` is the only thing holding it, which is the
whole reason that test exists.

### Why an identity rather than an ordinal

The obvious identity is the slot ordinal, and it is wrong: ordinals are
assigned in `assemble` from the surviving draft list, so they do not exist
while the passes that reorder, splice and drop drafts are running. A counter
minted at draft creation survives all three.

Two defects fall out of the same field. `list.remove` and `list.index`
compare `_Draft` by value, so `spell.py`'s splice could have landed at an
identical draft in an earlier word; and a freed `id()` can be reused by a
draft created later in the same build, which would point an edge at the wrong
slot rather than at none. Neither was firing — reuse measured zero across the
corpus — and a unique field closes both.

## What this does not decide

**The five-object pass signature** stays open in design question 05. A
`LexemePass` takes `(reading, drafts, lexicon, scribe, selection)` whether it
needs all five or not, and 27 `del` statements say "accepted and deliberately
ignored". `del` is honest — it makes the unused parameter visible where a
linter suppression would hide it — so this is a signature that grew by
addition, not a bug, and collapsing it into a context object trades the 27
lines for invisible dependencies. Genuinely two-sided, and nothing forces it.

**`cross_word_noon` returning a role name** rather than the slot it created
is listed under 05 but belongs to design question 08:
`build._split_tanween_words` greps the role name, so a script fact decides a
canonical question, and the fix is bound up with making `requires` a
description.

## Evidence

No output moves, and this time the stronger claim is available: the
`Inscription` is byte-identical across the whole corpus in both scripts —
**1,322,678 spellings, same digest** before and after. All eight gates read
as they did: cross 99.997/100.000, regression 99.928/97.674, roundtrip
100.000, attest 178/239, l1 18.

Two falsifiers were run by hand and each failed as it should. Removing
`Scribe.withdraw` from the muqattaat pass makes `2:1` raise
`OrphanedEdgeError` at offset 0 — the path that used to swallow 188 edges.
Making `before` block at junctions passes every gate, which is the finding
that put a test around it.
