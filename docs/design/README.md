# Open design questions

Decisions that are still open, one document each. A document leaves this
directory in one of three ways: it becomes a numbered ADR under `docs/adr/`,
it is closed as "no change", or it is merged into another document because it
turned out to be asking that document's question. The first leaves a decision
behind; the other two move the file to `docs/archive/`.

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
| [03](03-canonical-vocabulary.md) | Do `Onset`, `SlotOrigin` and `Annotation` split? **Resolved** -- census done, `SlotOrigin` splits, the other two do not. | projections |
| [06](06-seen-sad-khilaf.md) | How is the seen/sad khilaf authored and selected? | correctness today |
| [08](08-what-a-second-riwayah-decides.md) | Does a script fact attach to a scalar or to a match? | Warsh |

Read 06 first if you only read one. It is the only item on this list that is
wrong today rather than merely awkward.

## Multi-document questions

[projections/](projections/) is the public projection API that ADR-005 put out
of scope: two projections over the layered model (`phonemes` and `Mappings`),
the equivalence and completeness gate that replacement has to pass, and the
worked examples.

## Closed

| Was | Became |
|---|---|
| 02 — the output alphabet | [ADR-009](../adr/009-the-output-alphabet.md) |
| 01 — mark semantics | [ADR-010](../adr/010-constants-that-restate-data.md) in part, then merged into 08 |
| 04 — data schemas | [ADR-010](../adr/010-constants-that-restate-data.md) in part, then merged into 08 |
| 07 — Warsh readiness | merged into 08 |
| 05 — build internals | [ADR-011](../adr/011-where-a-slot-is.md), then [ADR-012](../adr/012-what-a-signature-may-leave-unsaid.md) |

01, 04 and 07 each stalled at the same question, which is why 08 asks it once.
What could be settled without answering it landed as ADR-010; the archived
originals are in `docs/archive/design/`.

05 left in two pieces. Three of its four items had a single correct answer
once measured and are ADR-011; the fourth it described as having no
measurement that would settle it, and counting the `del`s was that
measurement -- ADR-012. Worth remembering when a document here claims an item
is pure preference: 05 held that position for the item it had not counted.
