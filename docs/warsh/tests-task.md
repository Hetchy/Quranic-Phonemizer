# Test refactor and Warsh test task

Use this prompt in the dedicated tests task for `feat/warsh-phonemizer`.

## Mission

Continue from the completed Hafs test reorganization and compact semantic
harness. Add the Warsh script-adapter baseline, then add fixed Warsh behavior
one implementation vertical at a time. Public variants are the final phase.

## Required reading

Read completely before editing:

- `CLAUDE.md`;
- `tests/README.md` and every current file under `tests/`;
- [`test-audit.md`](test-audit.md), which accounts for the current suite;
- [`test-refactor-plan.md`](test-refactor-plan.md), which is the executable
  tree, style, harness, coverage, case-budget, PR, and acceptance contract;
- [`warsh-test-placement.md`](warsh-test-placement.md), which decides which
  files are shared, Hafs-only, or Warsh-only and owns the adapter-first
  extension matrix;
- [`status.md`](status.md);
- every file under [`research/v2/`](research/v2/), starting with
  `phoneme-rule-inventory.md` and `script-projection.md`; and
- `tools/gates.py`, snapshot/parity tools, package registry, corpus loaders,
  adapters, rule catalogue, variants, and extra-phoneme model.

V2 owns expected Warsh domain behavior. `test-refactor-plan.md` owns how that
behavior is tested. `warsh-test-placement.md` owns where it is tested. Do not
restate these contracts inside implementation PRs.

## Ordered work

1. Treat the existing semantic tree, `Case`/`StateCase`/`VariantCase`
   harness, selectors, and spaced-token convention as the starting
   foundation. Existing Hafs selector cases exercise the harness; adding
   Warsh selector behavior remains the final implementation phase.
2. Add canonical/source alignment and the selected Warsh script adapter.
3. Extend independently verified shared semantic cases to Warsh.
4. Add the shared model and riwayah RuleSet foundation.
5. Implement the fixed Warsh verticals in the exact PR order in the plan.
6. Prove complete default-profile conformance and only then add Warsh
   snapshots.
7. Implement selectors last: 72 semantic `VariantCase` rows plus the small
   generic API contract covering all 71 selectors. `tamanna_noon` has no new
   phonemization behavior case.

## Non-negotiable rules

- Expectations come from v2, the selected script, and authoritative sources,
  not current engine output or frozen snapshots.
- Semantic sites use canonical/public coordinates. Adapter fixtures preserve
  selected-source coordinates and text separately.
- Shared laws use shared cases, not duplicated Hafs and Warsh trees.
- Riwayah-only law files use `test_hafs_` or `test_warsh_`; a source-only
  coordinate difference does not justify a prefix.
- `pick()` is only for a small riwayah-specific detail under the same law.
- Different applicability, rule identity, state behavior, or explanation gets
  a separate case.
- Full phoneme spans use inventory tokens separated by exactly one ASCII
  space.
- Every named rule is asserted on its exact source and exact result where the
  public contract requires both.
- Closed registers are test-owned and independent of production authored
  data.
- No duration matrix, madd-count selector, tariq validator, or surah-transition
  material is added.
- No partially implemented Warsh output is frozen as an expectation or
  snapshot.
- Variants remain last.

## Starting checkpoint

The Hafs semantic refactor and RAR projection reconciliation are green. All
hand-authored phonemization cases live under `tests/phonemize/`; the old
`adjacent`, `boundary`, `nasal`, `waqf`, root madd/muqattaat/one-off, and giant
khilaf behavior suites are gone. `tests/api/test_variants.py` owns only the
generic catalogue and selection contract. Preserve byte-identical Hafs
snapshots and the reconciled source/sound ownership while adding Warsh.

Run while working:

```text
python -m pytest --collect-only -q
python tools/quick.py <targeted tests...>
```

Pull requests run the complete ordinary suite and required static checks.

## Done

The task is done only when every acceptance criterion in
[`test-refactor-plan.md`](test-refactor-plan.md#acceptance-criteria) passes.
