# The work, batched

`01-contract.md` section 9 lists 40 items. They do not land one at a time:
several touch the same types, and a few cannot be split without leaving the
tree broken in between. This directory batches them into 22 **units**, in
dependency order, and records what each one is allowed to move.

Read [decisions.md](decisions.md) first. It holds the answers to the three
questions in `09-open-questions.md` that block a unit, and where an answer
contradicts the contract it says which unit corrects the contract.

| Phase | Units | Holds |
|---|---|---|
| [A](phase-a.md) | A1 - A9 | model surgery: the rule vocabulary, the vowel, the sound |
| [B](phase-b.md) | B1 - B2 | inscription: what a glyph shows, and which fact it supplies |
| [C](phase-c.md) | C1 - C4 | rules that exist in the vocabulary and produce nothing |
| [D](phase-d.md) | D1 - D5 | orchestration, the recited text, the projections, the package |
| [E](phase-e.md) | E1, E3 | the assertions the suite has been waiting for |

D6, the six legacy adapters, is **deferred** out of this program. Legacy parity
confirms and never gates, so the adapters are a later effort.

## What a unit must do

1. **Read its entry here and the section-9 items it names.** The item text is
   the specification. Where this ledger and the contract disagree, say so
   rather than choosing silently.
2. **Commit once per unit**, so a regression can be bisected to one.
3. **Run `python tools/gates.py` and account for every number that moved.**
   The entry says which gates this unit is allowed to move. A gate that moves
   and is not named in the entry is the failure this whole arrangement exists
   to catch.
4. **When output moves, say which words.** Regenerate
   `tests/snapshots/head/{word,verse}.jsonl.gz` in the same commit and put the
   corrected refs in `docs/conformance/corrections.md`. `02-gate` section 1
   requires the parity report name them rather than swallow them.
5. **Leave a test that fails when the change is reverted.** A test that passes
   either way has asserted nothing.
6. **Strike what you closed.** A unit that settles an entry in
   `09-open-questions.md` deletes that entry in the same commit, and corrects
   whatever contract prose the answer contradicts. The register says so itself.

## The lanes

Peak useful concurrency is two, and it is a property of the tree rather than a
budget: `model/canon.py` is touched by 9 of the 21 units and `rules/madd.py` by
3, so a third lane manufactures conflicts instead of throughput.

- **Lane 1** is the model spine, strictly serial: A1, A2, A3, A6, then A4, A5,
  then A7, A8, A9.
- **Lane 2** is inscription: B1 alongside A1 through A3, then B2 after A4.
- **Phase C** runs C1 with C4, then C2 with C3.
- **Phase D** is serial throughout.
