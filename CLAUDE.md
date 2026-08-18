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
- `docs/hafs/variants.md` and `docs/hafs/research/` cover the Hafs reading.
- `docs/warsh/codepoint-audit.md` contains the available Warsh script audit.
- `docs/new-riwayah.md` is tentative guidance, not a final design.
- `docs/legacy/` describes the pre-refactor API only.

## Working principles

- The runtime is riwayah-aware but only Hafs is implemented. Do not present
  the tentative new-riwayah notes as an established abstraction.
- Raw Unicode and script conventions stay in `orthography/`. Tajweed rules
  operate on canonical or performed structures, not script codepoints.
- Source marks may attest a derived reading; they must not silently become the
  rule that decides it. Genuine closed exceptions belong in authored data.
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

Use `python tools/gates.py --fast` while working. Run `python tools/gates.py`
before handing off runtime or corpus changes.
