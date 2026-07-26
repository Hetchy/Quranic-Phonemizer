# Archived design documents

Superseded on 2026-07-26. Kept as decision history. **Nothing here describes
the current codebase or the accepted design.** Each file carries a header
explaining why it was archived.

Two groups:

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
domain inventory), `docs/riwayah-agnostic-refactor-pr.md` (accurate record of
what `e0d9fb9` landed), `docs/warsh-script-codepoint-audit.md` (source
evidence), and `docs/hafs/` (research and mapping references).
