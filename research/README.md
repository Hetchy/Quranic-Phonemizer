# Research

This tree contains evidence and exploratory outputs. Nothing here is imported
by the phonemizer or shipped in its wheel.

- `hafs/tajweed/notes/` contains source notes and examples.
- `hafs/tajweed/generated/` contains historical comparison output.
- `hafs/syntheses/` contains the per-rule syntheses those notes support.
- `hafs/unicode/` contains codepoint occurrence inventories.
- `warsh/` contains the Warsh source-encoding audit.
- `evidence/` contains spike results and completed phase reports.
- `reviews/` contains audits of the code as it stood on a date.
- `spines/` contains the three blind design drafts and their adjudication.
- `legacy-baselines/` contains the frozen pre-rebuild output.

A document here is dated by construction: it records what was found or decided
at a point in time. `docs/` is the opposite -- it describes the current release
and is wrong the moment the code moves past it.

Executable corpus building and regression tooling belongs in `tools/`, not in
this tree.
