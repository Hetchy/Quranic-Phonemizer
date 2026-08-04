# The public API this package used to have

Everything in this directory describes the **pre-refactor** package: a flat
`quranic_phonemizer/` holding `phonemizer.py`, `word.py`, `symbols/`, and a
`Phonemizer().phonemize(...) -> PhonemizeResult` returning six independently
computed projections. None of those modules exist any more. They were deleted
when the pipeline became `Reading -> Score -> Performance`.

These files are kept for one reason: `docs/design/projections/02-gate.md`
section 3 defines a set of adapters that must reproduce the legacy views from
the new graph, and these are the specification of what those views were. The
frozen output itself is in `tests/snapshots/`, pinned by digest.

**Do not read these as documentation of the package.** For that, read
`CLAUDE.md` and then `docs/design/projections/`.

| File | Was |
|---|---|
| `api.md` | Installation, refs, text search, outputs, stops, phonetic text |
| `tajweed-mappings.md` | 33 rule definitions, source and target rows, overlap, stopping effects |
| `letter-phoneme-mappings.md` | Merge rules, extension splitting, validation |
| `character-phoneme-mappings.md` | The per-character cell schema the shard consumer reads |

`character-phoneme-mappings.md` is the one with a live downstream consumer, and
`docs/design/projections/08-legacy-parity.md` reads its schema column by column
against the contract.
