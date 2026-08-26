# Quranic Phonemizer

Quranic Phonemizer converts Quran references into recitation-aware phonemes.
It preserves the exact written text, resolved boundaries, performed sounds,
tajweed rule occurrences, and source-to-sound relationships.

The package ships Hafs in Uthmani and IndoPak scripts and Warsh in Uthmani
script. Python 3.11 or later is required.

## Install

```bash
pip install quranic-phonemizer
```

## Quick start

```python
from quranic_phonemizer import Phonemizer

reader = Phonemizer()
result = reader.analyse("2:255")

print(result.text())
print(" ".join(result.phonemes()))
print(result.phonemes(by="word"))
```

Use `stop_refs` for exact word-addressed stops or `stop_signs` for stop
classes available in the selected riwayah and script:

```python
reader.analyse("1:1-1:3", stop_refs=("1:2:2",))
reader.analyse("2:255", stop_signs=("preferred_stop", "optional_stop"))
```

Configuration is stated once on `Phonemizer`:

```python
reader = Phonemizer(
    riwayah="hafs",
    script="uthmani",
    variants={"iqlab_nasal": "bilabial"},
    extra_phonemes=("emphatic_fatha", "emphatic_ikhfaa"),
)
```

The configured catalogues show exactly what that reader accepts:

```python
reader.available_stop_signs
reader.available_variants
reader.tajweed_rules
```

## Selective projections

Core analysis is eager. Source tokenization, highlights, and cells are built
once on first use and cached on the result:

```python
result.words
result.boundaries
result.sounds
result.rule_occurrences
result.mergers

source = result.source()
groups = result.highlights()
source_cells = result.cells(spelling="source")
transformed_cells = result.cells(spelling="transformed")
```

The native schema-v2 documents are available without serializer imports:

```python
analysis = result.document("analysis_result")
source = result.document("source_view")
highlights = result.document("highlight_groups")
cells = result.document("cell_view", spelling="transformed")
```

See [docs/public-api.md](docs/public-api.md) for the complete contract,
[docs/architecture.md](docs/architecture.md) for internals, and
[docs/performance.md](docs/performance.md) for benchmarking guidance.

## Development

```bash
python tools/gates.py --fast
```

The project is licensed under the [MIT License](LICENSE).
