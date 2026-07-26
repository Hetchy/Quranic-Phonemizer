# Architecture decision records

This set supersedes `docs/archive/adr/001-003`, which described a six-layer
model of which only three layers were ever built and whose package tree does
not exist. Nothing in the archive is a target.

Provenance: three design spines were written blind from
`research/evidence/internal-model-redesign.md`; spine B was adjudicated the
baseline (`research/spines/settled-design.md`), reviewed by the other two
authors (`convergence-a.md`, `convergence-c.md`), and ten binding rulings
R1–R10 were issued. The authored result was then reviewed for simplicity and
for domain conformance (`research/reviews/`), and amended. Where a decision
comes from a ruling, a graft or a review finding it is cited inline.

All decisions are settled. The last one open, A1 — whether the tanwīn nūn is
its own slot — was ruled in favour of option 3; ADR-004 §8 keeps the options and
the reasoning, because the principle generalises: a design rule catching a
modelling error is the healthy direction, and weakening an invariant to fit the
model is not.

Read in order. 001–006 are the design; 007 is how it is laid out in code;
008 is the gate the implementation must pass.

| ADR | Decision |
|---|---|
| [001](001-layers-and-the-slot.md) | Three layers, one-way reference, and what a `Slot` is |
| [002](002-attribution-and-occurrences.md) | One attribution relation with `Aspect`; occurrences as the only path to sound |
| [003](003-script-boundary.md) | Adapters, `Spelling`, the Ledger, and the three boundary laws |
| [004](004-rule-execution.md) | Phases, the Plan, effects, and the boundary plan |
| [005](005-recited-writing.md) | Recited writing as a projection over `write` |
| [006](006-variants-and-exceptions.md) | Khilāf resolution and what may be a Ledger entry |
| [007](007-package-and-conventions.md) | Package tree, module boundaries, data schemas, naming |
| [008](008-conformance-and-phases.md) | Invariants, fixtures, the L1 harness, the reversal trigger, phase order |

## What this is for

**Phonemes are the test, not the product.** Consumers take script text plus
projections — tajweed occurrences linked to graphemes, orthography↔sound
relationships, silent letters with reasons — with phonemes optional or absent.
Byte-identical phonemes across two orthographies is what *proves* the canonical
layer is real. See ADR-001 §1.1; the ordering decides at least one design
question in the set.

Two throwaway spikes have since run the phase-1 gate (**99.79%** L1 agreement)
and inverted the `Spelling` link against the frozen baseline (**99.11%** role
agreement). Reports in `research/evidence/`. Neither is the gate — ADR-008 §5
says why.

## Vocabulary used throughout

- **Score** — the canonical layer. Script-free, boundary-free, riwayah-scoped.
- **Slot** — the Score's unit: one canonical consonantal position plus its
  nucleus.
- **Inscription** — one script's graphemes for a word, plus the `Spelling`
  edges that point up into the Score.
- **Performance** — one traversal: sounds, attributions, occurrences.
- **Ledger** — the typed store of canonical facts no script derivation
  supplies.
- **`Decorates`** — a grapheme that supplies no canonical fact but names the
  slot it shows, so projections can point at it (ADR-003 §4.0).
- **Witness** — a script, considered as evidence for canonical facts.

## Open questions

Collected in [008 §7](008-conformance-and-phases.md#7-open-questions). Nothing
open is resolved by assertion elsewhere in this set.
