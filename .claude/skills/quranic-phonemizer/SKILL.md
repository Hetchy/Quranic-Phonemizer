---
name: quranic-phonemizer
description: Domain expert in the Quranic Phonemizer package (quranic-phonemizer on PyPI) — a G2P converter for the Quran with tajweed rule annotation.
allowed-tools:
  - Glob
  - Grep
  - Read
  - Bash
  - Python
  - Python3
---

# Quranic Phonemizer — Domain Expert

Expert skill for the `quranic-phonemizer` PyPI package — a Grapheme-to-Phoneme (G2P) converter for the Quran (Hafs recitation) that produces IPA phoneme sequences with comprehensive tajweed rule annotation and waqf (stopping) support.

**Source:** https://github.com/Hetchy/Quranic-Phonemizer

## Documentation Map

Consult existing documentation before answering questions — avoid duplicating what's already well-documented.

| Topic | Location | Contents |
|-------|----------|----------|
| Full API & usage | `.claude/skills/quranic-phonemizer/references/README.md` | Installation, input refs, text search, outputs, stops, phonetic text, tajweed mappings, letter-phoneme mappings, phoneme inventory |
| Tajweed mapping spec | `.claude/skills/quranic-phonemizer/references/tajweed-mappings.md` | Output structure, source/target rules, all 33 rule definitions, multi-rule overlap, stopping effects, muqattaat, serialization |
| Letter-phoneme mapping spec | `.claude/skills/quranic-phonemizer/references/letter-phoneme-mappings.md` | Merge rules (PREV/NEXT/CROSS-WORD), extension splitting, stopping effects, validation rules, serialization |
| Tajweed linguistics | `.claude/skills/quranic-phonemizer/references/tajweed-linguistics.md` | What tajweed is, rule categories, how rules affect pronunciation — for those unfamiliar with Arabic phonetics |
| DB build / risk register | `dev/README.md` | How `dev/Quran.json` + `surah_info.json` produce `quran_db.bin`, safe vs dangerous edits, CI sync workflow |
| Phoneme config | `quranic_phonemizer/resources/base_phonemes.yaml` | Character-to-phoneme YAML definitions |
| Tajweed phoneme config | `quranic_phonemizer/resources/rule_phonemes.yaml` | Tajweed rule phoneme symbols (configurable at runtime) |
| Simple-mode collapse | `quranic_phonemizer/resources/simple_phonemes.yaml` | Reduced-vocabulary collapse rules used by `Phonemizer(mode="simple")` |

## Quick API Reference

### Installation & Import

```python
pip install quranic-phonemizer

from quranic_phonemizer import Phonemizer
pm = Phonemizer()                       # full IPA inventory (default)
pm = Phonemizer(mode="simple")          # reduced vocabulary (collapses gemination/allophones)
```

### Core Workflow

```python
# Phonemize by reference
result = pm.phonemize(ref="1:1")                          # verse
result = pm.phonemize(ref="2:255:1")                      # word
result = pm.phonemize(ref="1:1 - 1:4")                    # range

# Phonemize by text search (fuzzy match)
result = pm.phonemize(ref_text="بسم الله الرحمن الرحيم")
print(result.match_score)                                  # 0–1 confidence

# With stopping
result = pm.phonemize("112", stop_signs=["verse"])
result = pm.phonemize("1:1-1:3", stop_refs=["1:2:2"])
```

### Output Methods

```python
result.text()                                              # Arabic text
result.phonemes_str(phoneme_sep=" ", word_sep=" | ")       # Phoneme string
result.phonemes_list(split="word")                         # Nested lists
result.show_table()                                        # Pandas DataFrame
result.phonetic_text()                                     # Recitation-accurate text
result.save("out.json")                                    # JSON/CSV
```

### Tajweed Mappings

Per-letter tajweed rule annotations distinguishing source (triggers) and target (affected) rules.

```python
tajweed = result.tajweed_mappings()
print(tajweed.to_json(indent=2))
result.save("out.json", fmt="tajweed")
```

Returns `TajweedMapping` with `TajweedWordMapping` per word and `TajweedEntry` per grapheme. For the full rule list (33 rules), output structure, and examples, see `docs/tajweed-mappings.md`.

### Letter-Phoneme Mappings

Flat `[chars, phonemes]` pairs where silent letters are merged into adjacent entries and word boundaries are spaces.

```python
lpm = result.letter_phoneme_mappings()
for chars, phonemes in lpm.to_list():
    print(f"{chars!r} -> {phonemes}")
violations = lpm.validate()                                # empty = valid
result.save("out.json", fmt="letter_phoneme")
```

Returns `FlatMappingResult`. For merge rules, extension splitting, stopping effects, and validation, see `docs/letter-phoneme-mappings.md`.

### PhonemeRegistry (Runtime Customization)

Singleton that caches YAML phoneme definitions and supports runtime overrides:

```python
from quranic_phonemizer.phoneme_registry import PhonemeRegistry
registry = PhonemeRegistry()
registry.set_rule_phoneme("qalqala", "ʔ")                 # override qalqala phoneme
```

## Public API Exports

From `quranic_phonemizer`:

```
Phonemizer, Location, Word
Symbol, LetterSymbol, DiacriticSymbol, ExtensionSymbol, StopSymbol, OtherSymbol
PhonemizeResult
LetterMapping, WordMapping, AlignmentEntry, PhonemizationMapping
TajweedRule, TajweedRuleTag
TajweedMapping, TajweedWordMapping, TajweedEntry
FlatMappingResult
```

## Architecture Overview

```
Reference or Arabic text
  -> TextMatcher (fuzzy search if raw text)
  -> Parser.load_words() (Loader reads dedup'd binary `quran_db.bin` + `surah_info.json`, lazy + cached)
  -> Parser.parse_word() (Unicode chars -> Symbol subclass instances)
  -> Word.phonemize() (LetterSymbol.phonemize() per letter)
  -> PhonemizeResult (output interface; `mode="simple"` collapses via simple_mode.collapse_phonemes)
```

**DB pipeline:** `dev/Quran.json` is the canonical editable source. `python dev/build_quran_db.py` regenerates `quranic_phonemizer/resources/quran_db.bin` (uint16 dedup index + UTF-8 blob). CI workflow `sync-quran-db` fails if the committed bin drifts from a fresh regen. Edit details + risk register in `dev/README.md`.

- **Symbol hierarchy:** `Symbol` (ABC) -> `LetterSymbol` subclasses implement tajweed logic via template method. Key: `Noon`, `Meem`, `HamzaWasl`, `Lam`, `Raa`, `Qalqala`, `TaaMarbuta`, vowel letters (`Alef`, `Waw`, `Yaa`, `AlefMaksura`).
- **Cross-word mutations:** `Word` objects are doubly-linked (`prev_word`/`next_word`). Letters can mutate neighboring words' phonemes (e.g., noon idgham).
- **TajweedRule enum** (33 values) in `tajweed_rule.py` — single source of truth for rule tagging via `set_tajweed_rule()`.
- **All imports** within the package use relative imports.

## Unicode Inspection

To inspect Arabic text character by character:

```python
import unicodedata

def inspect(text):
    for i, ch in enumerate(text):
        name = unicodedata.name(ch, "UNKNOWN")
        print(f"[{i:2d}] {ch!r:6} U+{ord(ch):04X}  {name}")
```

Combine with the phonemizer for investigating specific words:

```python
result = pm.phonemize("1:1:1")
mapping = result.get_mapping()
for word in mapping.words:
    inspect(word.text)
    for lm in word.letter_mappings:
        print(f"  {lm.char} -> {lm.phonemes}")
```

## Phoneme Inventory Summary

69–71 phonemes total. Full tables in `README.md` § Phoneme Inventory.

- **Consonants:** 28 base + 24 geminated (shaddah = doubled phoneme, except m/n which use ghunnah)
- **Vowels:** short `a u i`, long `a: u: i:`, emphatic `aˤ aˤ:`
- **Tajweed:** `ŋ/ŋˤ` (ikhfaa), `ñ/m̃/j̃/w̃` (idgham), `Q/QQ` (qalqala), `lˤlˤ` (heavy lam), `rˤ/rˤrˤ` (heavy raa)

## Key Data Files

In `quranic_phonemizer/resources/` (shipped in wheel):

| File | Description |
|------|-------------|
| `quran_db.bin` | Deduplicated binary word-text store (Hafs); loaded lazily by `loader.py`. Generated from `dev/Quran.json`. |
| `surah_info.json` | Per-surah/per-verse word counts; defines slot-array shape and is the source for reconstructing `s:v:w` keys. |
| `base_phonemes.yaml` | Character-to-IPA phoneme mappings |
| `rule_phonemes.yaml` | Tajweed rule phoneme symbols |
| `simple_phonemes.yaml` | Collapse rules for `Phonemizer(mode="simple")` reduced vocabulary |
| `special_words.yaml` | Location-specific override phonemizations (muqattaat, etc.) |

Canonical editable source `dev/Quran.json` is **not** shipped in the wheel — runtime reads only the binary. See `dev/README.md` for the regen workflow and the safe/risky/dangerous edit register.
