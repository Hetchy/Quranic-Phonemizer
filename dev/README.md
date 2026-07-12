# dev/

Sources and tooling that are **not** shipped in the wheel. The runtime
package only loads `quranic_phonemizer/resources/quran_db.bin` — this
folder contains the human-editable inputs that the binary is generated
from.

## Files

| file | purpose |
|---|---|
| `Quran.json`, `Quran_warsh.json` | Canonical word-by-word source. Edit this. |
| `unicode_validator.py` | Generates 2 files: `unicode_inventory.json` that contains all the authorized and allowed Unicode codepoints, and `flagged.json` that contains the unknown and non-allowed Unicode codepoints. |
| `strip_flagged_chars.py` | Removes the flagged Unicode codepoints listed in `flagged.json`. |
| `build_quran_db.py` | Regenerates `quranic_phonemizer/resources/{hafs-warsh}/quran_db.bin` from `Quran_{warsh}.json`. |
| `compare_coverage.py` | Tests font compatibility. |
| `split_script.py` | Split a script data into s:v:w format. |
| `Allah_references.txt`, `unicode_occurences/` | Reference data for tajweed-rule research. Not used at runtime. |

## Editing workflow

```bash
# 1. Edit dev/Quran.json (text changes only — see "Risk register" below)
$EDITOR dev/Quran.json

# 2. Regenerate the runtime binary
python dev/build_quran_db.py dev/Quran_{warsh}.json quranic_phonemizer/resources/{hafs-warsh}/quran_db.bin quranic_phonemizer/resources/{hafs-warsh}/surah_info_warsh.json 

# 3. Run tests / phonemize a sanity reference
python -c "from quranic_phonemizer import Phonemizer; \
           print(Phonemizer().phonemize('1:1').phonemes_str())"

# 4. Commit BOTH dev/Quran.json AND quranic_phonemizer/resources/quran_db.bin
git add dev/Quran_{warsh}.json quranic_phonemizer/resources/{hafs-warsh}/quran_db.bin
git commit
```

CI (`.github/workflows/sync-quran-db.yml`) re-runs the regen on every PR
that touches `dev/Quran.json`, `surah_info.json`, or the bin itself, and
fails if the committed `quran_db.bin` differs from a fresh regeneration.
A drifted bin can never reach `main`.

## Testing Font workflow

```bash
# 1. Generate the `unicode_inventory.json` and `flagged.json` files
python dev/unicode_validator.py quranic_phonemizer/resources/{hafs-warsh}/raw_data/quran.json text_field unicode_inventory.json flagged.json

# 2. Remove the flagged codepoints listed in `flagged.json`
python dev/strip_flagged_chars.py quranic_phonemizer/resources/{hafs-warsh}/raw_data/quran.json text_field flagged.json quranic_phonemizer/resources/{hafs-warsh}/processed_data/quran_cleaned.json

# 3. Extract the font's character-map table to see which Unicode characters the font claims to support
python -m fontTools.ttx -t cmap -o cmap.ttx quranic_phonemizer/resources/{hafs-warsh}/fonts/font.ttf-otf

# 4. Verify font compatibility
python dev/compare_coverage.py cmap.ttx unicode_inventory.json
```

## Split Script workflow

```bash
# Split script data into s:v:w format in case it's not already formatted that way
python dev/scripts/split_script.py quranic_phonemizer/resources/{hafs-warsh}/processed_data/quran_cleaned.json text_field dev/Quran_warsh.json
```


## Risk register — what kinds of edit are safe vs dangerous

The runtime DB is a **deduplicated word-text store** keyed implicitly by
position in canonical `(surah, ayah, word)` order. Word indices are
derived from `surah_info.json`'s per-verse `num_words`. The contract
between the three files is:

- `Quran.json` defines `text` for each `s:v:w` slot.
- `surah_info.json` defines how many words are in each verse and how
  many verses are in each surah — i.e., it defines the *shape* of the
  word slot array.
- `quran_db.bin` is a binary projection of `Quran.json`'s texts laid out
  in `surah_info`-derived order.

The build script enforces `sum(num_words) == len(Quran.json)`, so an
inconsistent shape cannot ship.

### ✅ Safe — text-only edits

These touch only the `text` field of an existing word and never affect
position or count. The binary regen reflects the new text exactly.

- Fix a typo, add a missing diacritic, correct a stop sign on an
  existing word.
- Replace one Quranic-symbol code-point with a canonical equivalent.
- Reformat the JSON (whitespace, key order) — has no runtime effect.

Effect on phoneme output: only at the location(s) you edited. Mappings
and tajweed annotations may shift accordingly, also only at those
locations.

### ⚠️ Risky — shape edits (require coordinated `surah_info.json` update)

Any change that alters the **count or position** of words in a verse
requires a matching edit to `surah_info.json` in the same commit. The
build script will refuse to regenerate the binary otherwise.

- Adding or removing a word in a verse (e.g. splitting one stored word
  into two).
- Renumbering keys (`2:5:6` → `2:5:7`) — disturbs ordering.
- Adding or removing a verse from a surah.

If you forget to update `surah_info.json`:
`python dev/build_quran_db.py` exits with `SystemExit("Mismatch:
Quran.json has N words but surah_info.json implies M.")`. CI fails at
the regen step.

If you update `surah_info.json` but not `Quran.json`: the regen script
still detects the mismatch, but if both somehow land out of sync, the
runtime will mis-index words — every phoneme call returns the **wrong
word** at every offset past the first divergent verse. **High risk of
silent corruption**; the CI verify step is your safety net.

### 🛑 Dangerous — schema or invariant changes

These break the loader and need code changes alongside the data edit:

- Removing the `text` field from `Quran.json` entries — current loader
  reads `raw[k]["text"]`. If you remove or rename it, regen crashes.
- Adding a 65,536th unique word text — exceeds the `uint16` per-word
  index. Regen exits with a clear error; widening to `uint32` is a
  one-line change in both `dev/build_quran_db.py` and
  `quranic_phonemizer/loader.py`.
- Adding a 115th surah, or swapping the `(surah, ayah, word)` semantics.
  These are below-the-package-API assumptions; touch the loader and the
  range-resolver in `loader.py`.

### Edits that don't go through this folder

Phoneme/rule changes (the `*.yaml` files in `quranic_phonemizer/resources`)
do **not** require a binary regen. Edit the YAML, run your tests, ship.

`base_phonemes.yaml` / `rule_phonemes.yaml` / `simple_phonemes.yaml` /
`special_words.yaml` are read directly at runtime.
