# Archived design documents

Superseded on 2026-07-26. Kept as decision history. **Nothing here describes
the current codebase or the accepted design.** Each file carries a header
explaining why it was archived.

Three groups:

**Merged design questions** — `design/01`, `design/04` and `design/07` each
stalled on the same question and were replaced by `docs/design/08`. What could
be settled without answering it is ADR-010. Each carries its own header saying
which half went where.

**Pre-refactor snapshots** — `architecture-today.md` and
`current-implementation-mapping.md` document the 35-module implementation that
`e0d9fb9` deleted.

**The unbuilt target model** — `adr/001-internal-model.md`, `adr/002`,
`adr/003`, `tajweed-model.md`, `internal-model-worked-examples.md`, and
`follow-up-decisions.md` specify a six-layer model of which layers 1, 2 and 4
reached the code. Alignment, recited writing, and Tajweed occurrences did not.
The specified package tree was collapsed during implementation without the
documents being updated.

`warsh-integration-plan.md` is archived for sequencing: a second Hafs script
(IndoPak) is now the next orthography phase, ahead of Warsh.

Still live and not archived: `docs/domain-facts.md` (riwayah-independent
domain inventory), `docs/archive/riwayah-agnostic-refactor-pr.md` (accurate record of
what `e0d9fb9` landed), `research/warsh/warsh-script-codepoint-audit.md` (source
evidence), and `docs/hafs/` (research and mapping references).
