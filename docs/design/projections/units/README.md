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
3. **Run the gates and account for every number that moved.** The entry says
   which gates this unit is allowed to move. A gate that moves and is not named
   in the entry is the failure this whole arrangement exists to catch.

   Three gates read no corpus and take seconds; the other five each walk 77,433
   words. So the cadence is `python tools/gates.py --fast` while working and
   after each unit, and the full `python tools/gates.py` once before handing the
   batch on. The full run is parallel across gates, which is why it is minutes
   rather than tens of minutes.
4. **When output moves, say which words.** Regenerate
   `tests/snapshots/head/{word,verse}.jsonl.gz` in the same commit and put the
   corrected refs in `docs/conformance/corrections.md`. `02-gate` section 1
   requires the parity report name them rather than swallow them.
5. **Leave a test that fails when the change is reverted.** A test that passes
   either way has asserted nothing.
6. **Strike what you closed.** A unit that settles an entry in
   `09-open-questions.md` deletes that entry in the same commit, and corrects
   whatever contract prose the answer contradicts. The register says so itself.

## The order

One order, and every unit lands on `feat/public-projection` in turn.

```
A1  A2  A3  A6  B1  A4  B2  A5  A7  A8  A9        phases A and B
C1  C4  C2  C3                                     phase C
D1  D2  D3  D4  D5                                 phase D
E1  E3                                             phase E
```

Concurrency was considered and is not worth having. `model/canon.py` is touched
by 9 of the 21 units and `rules/madd.py` by 3, so the most that can ever run at
once is two, and the one genuinely independent pairing (B1 beside A1 and A2)
overlaps on `render/anchored.py`. Two lanes would buy wall-clock, which nothing
here is short of, and pay for it in merge conflicts on the hottest files in the
tree.
