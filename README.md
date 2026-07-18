# Quranic Phonemizer

Quranic Phonemizer converts Quran references to ordered phoneme tokens. The
runtime has a riwayah-aware resource boundary; Hafs is implemented and Warsh
fails closed until its phonology is researched and implemented.

The current public projection is deliberately limited to phonemes. Source
script normalization, boundary realization, Tajweed behavior, and rendering
remain separate inside the package.

## Install

```bash
pip install quranic-phonemizer
```

Python 3.11 or newer is required.

## Usage

```python
from quranic_phonemizer import Phonemizer

phonemizer = Phonemizer()

continuous = phonemizer.phonemize("1:1")
verse_stops = phonemizer.phonemize("1:1", stop_signs=["verse"])
selected_stops = phonemizer.phonemize("1:1", stop_refs=["1:1:2"])

print(continuous.phonemes_list("word"))
print(verse_stops.phonemes_str())
```

Selected words are joined by default, except for the request's final edge.
`stop_signs` accepts the existing `verse`, `preferred_continue`,
`preferred_stop`, `optional_stop`, `compulsory_stop`, and `prohibited_stop`
names. `stop_refs` accepts exact word references.

References may select a surah, verse, word, or inclusive range:

```text
1
2:255
2:255:3
1:1-1:4
1-2:2
```

`phonemes_list()` groups tokens by word by default. It also accepts `"verse"`
or `"both"`. `phonemes_str()` accepts phoneme, word, and verse separators.

## Runtime organization

```text
quranic_phonemizer/
  api.py                 public entry point
  corpus.py              packed corpus loading and reference resolution
  parsing.py             source Unicode to canonical graphemes
  model/                 orthography, phonology, and realized recitation values
  rules/                 shared phonological algorithms
  rendering.py           semantic segments to phoneme inventory symbols
  data/shared/           finite shared facts and render inventory
  data/riwayat/hafs/     Hafs aliases, exceptions, and packed corpus
```

Complex pronunciation behavior is Python code. Runtime YAML contains only
finite reviewed facts such as glyph aliases, letter sets, pair tables, and
rendered tokens.

## Regression contract

The full Hafs corpus, surahs 1 through 114, is frozen at every source-word
boundary for continuous recitation, verse stopping, and stopping after every
word. Tests compare the UTF-8 bytes of all 77,433 word-level phoneme arrays.
Source tokenization is also required to reconstruct every corpus word exactly.

## License

MIT. See [LICENSE](LICENSE).
