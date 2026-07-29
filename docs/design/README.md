# Open design questions

Decisions that are still open, one document each. A document leaves this
directory in one of two ways: it becomes a numbered ADR under `docs/adr/`, or
it is closed as "no change" and moves to `docs/archive/`.

These are not a backlog of known fixes. Everything in the July 2026 audit that
had one correct answer and no design content has already landed. What is left
is here because the answer depends on a choice, and the choice depends on
evidence that has not been gathered yet.

`research/reviews/architecture-audit-2026-07.md` is the evidence: what four
independent reviewers found, what they measured, and what was rejected. These
documents do not restate it. Each names its section of the audit and then adds
what the audit did not have -- the options, what each one costs, what has to be
measured before choosing, and what would make the decision wrong.

| | Question | Blocks |
|---|---|---|
| [01](01-mark-semantics.md) | Does a script inventory hand downstream code a typed fact or a string? | Warsh |
| [02](02-render-map.md) | Is the output alphabet a table of feature tuples or a set of rules? | a second notation |
| [03](03-canonical-vocabulary.md) | Do `Onset`, `SlotOrigin` and `Annotation` split? **Resolved** -- census done, `SlotOrigin` splits, the other two do not. | projections |
| [04](04-data-schemas.md) | What does a data file have to say about itself before it is trusted? | Warsh |
| [05](05-build-internals.md) | Who owns slot adjacency, pass order, and slot identity? | nothing yet |
| [06](06-seen-sad-khilaf.md) | How is the seen/sad khilaf authored and selected? | correctness today |
| [07](07-warsh-readiness.md) | What must exist before a Warsh inventory can be written? | Warsh |

Read 06 first if you only read one. It is the only item on this list that is
wrong today rather than merely awkward.

## Multi-document questions

[projections/](projections/) is the public projection API that ADR-005 put out
of scope: an audit of the four legacy projections and their consumers, a
two-projection design over the layered model, and the equivalence gate that
replacement has to pass. It assumes 03 resolved.
