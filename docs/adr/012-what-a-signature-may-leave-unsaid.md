# ADR-012: What a signature may leave unsaid

Status: **accepted**. Closes the last item of design question 05.
Audit: "Abstraction".

## Context

Design question 05 asked whether the pass signature's 27 `del` statements
were worth their explicitness, or should collapse into a context object. It
sat open longest because it looked like the one item with no measurement that
would settle it -- only a preference about what a signature should show.

Counting them settles it. **The 27 were never one number.** They span three
unrelated callback signatures plus five parameters that belong to no
signature at all, and only four were the `LexemePass` the question named:

| | signature | count | where |
|---|---|---|---|
| A | `Classifier.look(near, plan, at, boundaries)` -- *four* | 16 | `rules/` ×7 modules |
| B | `LexemePass(reading, drafts, lexicon, scribe, selection)` | 4 | `canon/passes.py` ×2, `spell.py`, `khilaf.py` |
| C | `derivation(context)` | 2 | `derive/length.py`, `derive/wasl.py` |
| D | no protocol at all | 5 | `engine/run.py` ×2, `laws.py`, `derive/lexeme.py`, `rules/boundary.py` |

Group D was dead code rather than a trade-off. `perform` built
`index = {slot.id: slot for slot in slots}` for the sole purpose of handing it
to `_materialise`, which deleted it. `relengthened(nucleus)` ignored its only
argument and returned `Long(Quality.A)` unconditionally, so a call shaped like
a transform transformed nothing.

And the real defect was neither the count nor the collapse: the convention the
`del`s serve **was not being applied**. `_apply_allah_lexeme` ignored
`selection` and `_apply_pausal_lexemes` ignored `scribe` and `selection`,
none of them saying so. Two of the five lexeme passes, silently. So "no `del`"
meant either "reads all of them" or "the author forgot", with nothing to tell
them apart -- there is no ruff and no mypy in this repository, and neither
`comment_lint` nor `structure_lint` looked at a signature.

## Decision

**`del` stays, and becomes a checked claim rather than a convention.**
`structure_lint`'s `signature-honesty` reports any protocol parameter a body
neither reads nor deletes. 25 implementations are checked; a Protocol's own
`...` body is skipped, since it declares parameters and by construction reads
none.

**Group D is deleted.** Five parameters and one dict comprehension that fed
nothing. `relengthened` becomes the frozen value it always returned.

**The two protocols state what they are.** `LexemePass` was
`Callable[[Reading, list, object, object, object], None]` -- three `object`s
type-check nothing, which is most of why the signature read as arbitrary. It
is a `Protocol` with names and types. The `=None` defaults on three
implementations went with it: `build` supplies all five on every call, so a
default advertised an optionality no caller has.

The count settles at **23**: 16 classifier, 5 pass, 2 derivation. Every one of
them verified.

### Why not a context object

It would hide what a pass depends on, which is the thing the `del`s make
visible. The recount sharpens this rather than softening it: 16 of the 23 are
a *four*-parameter protocol where a context object buys one line per
implementation and costs the dependency list. The remaining 5 are a
five-parameter protocol whose fourth and fifth arguments -- the scribe and the
variant selection -- are exactly the ones a reader needs to see a pass decline.

### Why not `_plan` and `_boundaries`

The underscore prefix is the standard idiom and would remove all 23 lines. It
loses two things. `del` takes the name out of scope, so an edit that starts
reading the parameter fails loudly; `_plan` can simply be read under its new
name and nothing notices. And a `Protocol` declares parameter names, so an
implementation that renames one stops matching it -- inert today with no type
checker in CI, and a trap the moment one is added.

## What this does not decide

**Group C's two `del context`s** stay where they are. `hamzat_wasl` declares
13 `requires` and reads zero; `pausal_length` declares 9 and reads zero. That
is design question 08's question -- ADR-010 already records why `requires` is
a hand-kept proxy and why a per-derivation check would be a lie -- and the
`del` is a symptom of it, not the thing to fix.

## Evidence

No output moves. Every change either removes a parameter nothing read or adds
a `del` for one nothing read. All eight gates read as they did: cross
99.997/100.000, regression 99.928/97.674, roundtrip 100.000, attest 178/239,
l1 18.

Three falsifiers were run by hand and each failed as it should. Dropping
`scribe` from `connect_plural_meem`'s `del` line is named at
`passes.py:174`. Restoring the two defects this ADR's second commit fixed is
named three times, once per silently ignored parameter -- so the check catches
the exact defect that was live. And `_materialise` still raises
`MaterialisationError` on a half-merge with `index` gone, which is the only
behaviour the group D deletions came near.
