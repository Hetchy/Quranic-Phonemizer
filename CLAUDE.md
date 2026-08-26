# CLAUDE.md

## Project

Quranic Phonemizer converts Quran references into recitation-aware phonemes.
It currently ships the Hafs reading in Uthmani and IndoPak scripts, applies
tajweed across word boundaries, and supports connected reading, stopping, and
starting. Its result preserves the written text, canonical reading, performed
sounds, rule occurrences, and the alignments between them.

The central distinction is between what a script writes, what the riwayah
reads, and what is actually pronounced under a boundary plan.

## Repository map

- `orthography/` reads script-specific graphemes and marks without deciding
  the recitation.
- `canon/` and `model/` build the script-independent reading and preserve how
  it is spelled.
- `engine/`, `rules/`, and `riwayat/` apply boundary-sensitive tajweed and
  bind the data and classifiers for a reading.
- `render/` owns phoneme tokens; `phonemize/` assembles the public result.
- `data/riwayat/` holds reading-specific corpora and authored facts;
  `data/shared/` is only for facts demonstrated to be reading-independent.

## Documentation

- Start with `docs/architecture.md`; use `docs/public-api.md` for the result
  contract and `docs/conformance.md` for known corpus-gate residue.
- `docs/variants.md` is the cross-riwayah selector contract;
  `docs/hafs/research/` contains the Hafs domain notes.
- Use `docs/performance.md` for reproducible benchmarks, profiling findings,
  full-Quran resource measurements, and large-batch guidance.
- `docs/warsh/status.md` tracks the active Warsh implementation state;
  `docs/warsh/foundation-iteration-log.md` records adapter/test reconciliation;
  `docs/warsh/foundation-test-reconciliation.md` records every promoted or
  deferred Hafs-only semantic test row;
  `docs/warsh/test-audit.md` records the current-suite audit;
  `docs/warsh/test-refactor-plan.md` owns the target test tree and harness;
  `docs/warsh/warsh-test-placement.md` owns shared versus riwayah-specific
  test placement and the adapter-first Warsh coverage matrix;
  `docs/warsh/tests-task.md` is the concise execution handoff;
  `docs/warsh/codepoint-audit.md` audits the source encoding.
- `docs/warsh/research/v2/` is the Warsh implementation reference:
  `phoneme-rule-inventory.md` and `script-projection.md` define the foundation;
  the wasl, iltiqa, hamza, madd, mim, yaa, and seven-alif files own their
  individual phenomena; and `inclination.md`, `raa.md`, and
  `lam-tafkheem.md` own vowel and consonant coloring.
- `docs/warsh/research/v1/` preserves the imported research unchanged. It is
  historical evidence, not an implementation specification.
- `docs/new-riwayah.md` is tentative guidance, not a final design.
- `docs/legacy/` describes the pre-refactor API only.

## Working principles

- The runtime is riwayah-aware but only Hafs is implemented. Do not present
  the tentative new-riwayah notes as an established abstraction.
- Raw Unicode and script conventions stay in `orthography/`. Tajweed rules
  operate on canonical or performed structures, not script codepoints.
- For a riwayah with one supported script, a reviewed mark-sequence family may
  directly supply the canonical fact it writes; an unreviewed sequence fails
  projection rather than being guessed. Research-derived predicates and counts
  remain conformance reconciliation, not required runtime derivations. Hafs is
  the deliberate two-script exception: its facts stay script-independent.
  Genuine closed exceptions belong in authored data.
- Phoneme strings belong in `render/`; other layers use typed model values.
- Treat wasl, waqf, and ibtidaa as explicit boundary state. Never infer them
  from array position or mutate neighbouring words to simulate a join.

- Source comments explain only non-obvious constraints; docstrings state the
  contract not visible from the signature. Keep both short.
- Source must describe current behaviour only. Do not reference design docs,
  numbered sections, project phases, reviews, history, or corpus measurements.
- Use ASCII transliteration in prose. Arabic script is allowed when quoting a
  word or mark. Avoid typographic punctuation in source.
- Do not write essays in comments, keep them short and to the point and only complement the code; which should be self-explanatory anyways. You do not need to explain general domain knowledge in comments, a reader is already familiar with that, but you can bring up specific domain knowledge that is relevant to the code.
- Respect `tools/comment_lint.py` and `tools/structure_lint.py`; do not bypass
  their import, export, size, or phoneme-ownership checks.
- Frozen legacy output is a change detector, not a correctness oracle. Document
  intentional conformance changes in `docs/conformance.md`.

## Validation

Before writing or modifying tests, read `tests/README.md` and follow its
semantic-case, source-span, boundary, and file-ownership conventions.

Use `python tools/gates.py --fast` while working. Run `python tools/gates.py`
before handing off runtime or corpus changes.
