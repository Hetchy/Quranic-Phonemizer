# CLAUDE.md

## Comments and docstrings

Enforced by `tools/comment_lint.py`, which runs in CI.

A comment explains **why the code is not the obvious thing**. A docstring says **what a thing is** and names any constraint a caller cannot see from the signature. Nothing else belongs in source.

Banned outright:

- **Design-document references.** No `ADR-nnn`, no section signs, no `R9`, no phase or report names. Rationale lives in `docs/adr/`; source links to nothing.
- **History and process.** Not what the old implementation did, not what a review found, not what changed, not what a law "caught". Source describes the code as it is. Changelog goes in the commit.
- **Narration.** No "which is why", "the whole argument for", "did its job". If a paragraph is needed to justify the code, the code is wrong. Fix the code.
- **Measurements and counts.** No corpus statistics, residue counts, or percentages. They rot. Put them in `docs/`.
- **Non-ASCII prose.** See `.claude/rules/transliteration.md`. ASCII transliteration, no diacritics; Arabic script allowed when quoting a word or mark; no section sign, em dash, curly quotes, or multiplication sign.

Budget: module docstring 1-3 lines, class/function docstring 1 line by default and 3 at most, inline comment 1 line. Exceeding it is a signal to simplify the code, not to keep writing.

## The pipeline

Four stages, each with its own type. Read them in this order; nothing later is intelligible without the one before it.

```
text  --read-->  Reading  --build-->  Score  --perform-->  Performance  --render-->  tokens
                (script)            (canonical,         (+ BoundaryPlan)
                                     boundary-free)
```

- **`Reading`** (`orthography/`) is what a script wrote: grapheme clusters with their marks, no interpretation.
- **`Score`** (`model/canon.py`) is the canonical reading: `Slot`s carrying a `CanonLetter`, an `Onset` and a `Nucleus`. Boundary-free and script-free, so both Uthmani and IndoPak build the same one. That claim is the `l1` gate.
- **`Performance`** (`model/performance.py`) is the Score plus a `BoundaryPlan`, run through the tajweed rules: `Sound`s and the `Attribution`s that produced them.
- **Tokens** come from `render/alphabet.py`, the only place in the package holding a phoneme string.

`Inscription` (`model/inscription.py`) is the sideways relation: `Spelling` edges pointing from a grapheme up into the Score, recorded by `canon/scribe.py` as the Score is decided. It is what every alignment view is built from.

## Layers

`tools/structure_lint.py` holds the allowed-imports map and **fails CI on any edge not declared there**, on any declared edge nothing exercises, and on any cycle.

```
dataio  model  corpus  orthography  canon  engine  rules  render  riwayat  api
```

Load-bearing consequences, all of them checked rather than remembered:

- `orthography/` and `render/` may import only `dataio` and `model`. Neither can see a `BoundaryPlan`, a `Performance`, or an `Occurrence`.
- `api.py` is the composition root. `Recitation` holds every loaded resource; `recitation(riwayah)` builds one.
- A file over 400 lines or a function over 50 fails `structure_lint`.
- A phoneme string outside `render/` fails `structure_lint`. Hold tokens by asking the alphabet.
- A name in `__all__` that nothing in the repo imports must be listed in `PUBLIC_API` or the dead-export check fails.

## The gates

Eight, all in `.github/workflows/gates.yml`. Floors may only rise; every row behind a floor short of 100% is named in `docs/conformance/gate-residues.md`.

| Gate | Asks |
|---|---|
| `suite` | `python -m pytest tests/ -q` |
| `comments` | `tools/comment_lint.py` |
| `structure` | `tools/structure_lint.py` |
| `cross-script` | Uthmani and IndoPak give the same phonemes |
| `regression` | Output against frozen legacy snapshots. **A change detector, not a correctness oracle** - the frozen output has known defects, so this floor may fall when the oracle is the one that is wrong. |
| `roundtrip` | Every Score spells back to itself |
| `attestation` | A shadda a script writes is produced by some occurrence |
| `l1` | The two scripts build the same Score |

`python tools/gates.py` runs them all, in parallel across gates. `--fast` runs only `suite`, `comments` and `structure`, which read no corpus and take seconds; the other five each walk 77,433 words. Work against `--fast`, and run the full set before handing anything on.

Never edit a floor without saying in the same commit which refs moved and why.

## Tests

`tests/README.md` is the authority. In short: a case is a `Site(hafs=("1:1", (1, 2)))`, boundary state is an argument (`isolated`, `ibtidaa`, `waqf`, `wasl`) and never junction arithmetic, and a test says what the reading **should** be. Where the engine disagrees the test fails and that failure is the record of the bug; mark it `@pytest.mark.engine_bug` and never change a correct expectation to match the engine.

`tests/laws/` holds invariants over the whole corpus. `tests/schema/` holds what the loaders must reject.

## Data

Everything the riwayah knows is data under `quranic_phonemizer/data/`, not code:

- `riwayat/hafs/ledger.yaml` - authored canonical facts and the witnesses that agree with them
- `riwayat/hafs/lexicon.yaml` - canonical skeletons, closed classes of Arabic
- `riwayat/hafs/khilaf.yaml` - the points where the riwayah legitimately disagrees with itself
- `riwayat/hafs/scripts/{uthmani,indopak}.yaml` - the scalar inventory per script
- `shared/{rules,muqattaat,morphology}.yaml` - rule letter tables, letter-name spellings, clitic sets
- `render/ipa.yaml` - the output alphabet

Adding a letter to the model is one entry per table. The four alphabet tables are total over their enums, checked at load.

## In flight

`docs/design/projections/` specifies a public API that does not exist yet: `Phonemizer(...).phonemize(ref) -> PhonemizeResult`. `01-contract.md` section 9 is the work list, `02-gate.md` is the acceptance criterion, and `docs/design/projections/units/` batches the work and records the decisions already taken. Read `units/decisions.md` before touching anything the contract names.
