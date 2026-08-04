# Tajweed Mappings

Tajweed mappings provide structured, per-letter tajweed rule annotations for any phonemized passage. Each Arabic letter is annotated with the tajweed rules it participates in, making it straightforward to build colored tajweed displays, educational tools, or analytical pipelines.

```python
from quranic_phonemizer import Phonemizer

pm = Phonemizer()
result = pm.phonemize("1:1")
tajweed = result.tajweed_mappings()
print(tajweed.to_json())
```

## Output Structure

The output is organized by **word**, with each word containing a list of **entries** — one per grapheme unit in reading order.

```
TajweedMapping
├── ref: str                          # Resolved reference
└── words: List[TajweedWordMapping]
    ├── location: str                 # Word location (surah:ayah:word)
    ├── is_stopping: bool             # Whether recitation stops at this word
    └── entries: List[TajweedEntry]
        ├── char: str                 # Arabic character
        ├── source_rules: List[str]   # Rules this letter triggers
        └── target_rules: List[str]   # Rules affecting this letter from another letter
```

### Source vs Target Rules

Tajweed rules often involve two letters — one that **triggers** the rule (source) and one that is **affected** by it (target). For example, in noon idgham (نْ + ر), the noon is the source and the raa is the target:

```json
{"char": "ن", "source_rules": ["idgham_bila_ghunnah_noon"]},
{"char": "ر", "source_rules": ["tafkheem"], "target_rules": ["idgham_bila_ghunnah_noon"]}
```

Rules that involve only one letter (like ghunnah or qalqala) appear only in `source_rules`.

Entries with no rules have empty `source_rules` and `target_rules` (omitted in JSON output for brevity).

## Examples

### Basic — `بِسْمِ ٱللَّهِ` (1:1:1–1:1:2, continuing)

```json
{
  "ref": "1:1:1-1:1:2",
  "words": [
    {"location": "1:1:1", "entries": [
      {"char": "ب"},
      {"char": "س"},
      {"char": "م"}
    ], "is_stopping": false},
    {"location": "1:1:2", "entries": [
      {"char": "ٱ", "source_rules": ["hamza_wasl_silent"]},
      {"char": "ل", "source_rules": ["idgham_mutamathilayn"]},
      {"char": "ل", "target_rules": ["idgham_mutamathilayn"]},
      {"char": "ٰ", "source_rules": ["madd_tabii"]},
      {"char": "ه"}
    ], "is_stopping": false}
  ]
}
```

### Extension splitting — `ٱلرَّحْمَـٰنِ` (1:1:3)

Dagger alef (ٰ) and mini waw/yaa (ۥ/ۦ) are split into their own entries so their madd rules are separate from the parent letter:

```json
{"location": "1:1:3", "entries": [
  {"char": "ٱ", "source_rules": ["hamza_wasl_silent"]},
  {"char": "ل", "source_rules": ["lam_shamsiyah"]},
  {"char": "ر", "source_rules": ["tafkheem"], "target_rules": ["lam_shamsiyah"]},
  {"char": "ح"},
  {"char": "م"},
  {"char": "ٰ", "source_rules": ["madd_tabii"]},
  {"char": "ن"}
], "is_stopping": false}
```

### Cross-word idgham — `مِن رَّبِّهِمْ`

```json
{
  "words": [
    {"location": "2:5:1", "entries": [
      {"char": "م"},
      {"char": "ن", "source_rules": ["idgham_bila_ghunnah_noon"]}
    ], "is_stopping": false},
    {"location": "2:5:2", "entries": [
      {"char": "ر", "source_rules": ["tafkheem"], "target_rules": ["idgham_bila_ghunnah_noon"]},
      {"char": "ب"},
      {"char": "ه"},
      {"char": "م"}
    ], "is_stopping": false}
  ]
}
```

### Stopping — `دُعَآءً` (with waqf)

When stopping, fathatan on the final letter produces a long vowel (madd iwad), classified as `madd_tabii`:

```json
{"location": "40:50:2", "entries": [
  {"char": "د"},
  {"char": "ع"},
  {"char": "ا", "source_rules": ["madd_wajib_muttasil"]},
  {"char": "ء", "source_rules": ["madd_tabii"]}
], "is_stopping": true}
```

## Tajweed Rules

All annotated rules and when they appear.

### Nasalization (Ghunnah)

| Rule | Type | Description | Trigger |
|------|------|-------------|---------|
| `noon_ghunnah` | source | Noon with shaddah — prolonged nasalization | نّ |
| `meem_ghunnah` | source | Meem with shaddah — prolonged nasalization | مّ |
| `ikhfaa_noon` | source+target | Noon sakin before an ikhfaa letter — hidden nasalization | نْ + ikhfaa letter |
| `ikhfaa_tanween` | source+target | Tanween before an ikhfaa letter — hidden nasalization | tanween + ikhfaa letter |
| `ikhfaa_shafawi` | source+target | Meem sakin before baa — lip-based hidden nasalization | مْ + ب |
| `iqlab_noon` | source+target | Noon sakin before baa — noon converts to meem sound | نْ + ب |
| `iqlab_tanween` | source+target | Tanween before baa — converts to meem sound | tanween + ب |
| `idgham_ghunnah_noon` | source+target | Noon sakin merges into ي/ن/م/و with nasalization | نْ + ي/ن/م/و |
| `idgham_ghunnah_tanween` | source+target | Tanween merges into ي/ن/م/و with nasalization | tanween + ي/ن/م/و |
| `idgham_shafawi` | source+target | Meem sakin merges into meem with nasalization | مْ + م |

### Silent Letters

| Rule | Type | Description | Trigger |
|------|------|-------------|---------|
| `vowel_silent` | source | Vowel letter (alef/waw/yaa) produces no sound | Orthographic vowel with no phoneme |
| `hamza_wasl_silent` | source | Hamza wasl is silent when connecting to previous word | ٱ mid-verse |
| `lam_shamsiyah` | source+target | Lam of the definite article is silent before sun letters | ال + sun letter |
| `idgham_bila_ghunnah_noon` | source+target | Noon sakin fully merges into lam/raa (no nasalization) | نْ + ل/ر |
| `idgham_bila_ghunnah_tanween` | source+target | Tanween fully merges into lam/raa | tanween + ل/ر |
| `idgham_mutamathilayn` | source+target | Identical letters merge — first becomes silent | Same letter + shaddah |
| `idgham_mutaqaribayn` | source+target | Letters with close articulation points merge | e.g. ل + ر |
| `idgham_mutajanisayn_kamil` | source+target | Letters with same articulation point merge fully | e.g. ت + ط |
| `silent_iltiqaa_sakinayn` | source | Long vowel shortened when two sukuns meet at a word boundary | Long vowel + hamza wasl |

### Tafkheem (Heaviness)

| Rule | Type | Description | Trigger |
|------|------|-------------|---------|
| `tafkheem` | source | Heavy/emphatic pronunciation | Istilaa consonants (ص ض ط ظ خ غ ق), heavy raa, heavy lam (in Allah), and their vowels |

Tafkheem applies to:
- **Istilaa consonants** — always heavy by nature
- **Raa** — heavy in specific vowel contexts (fatha, damma, or sukun after fatha/damma)
- **Lam** — heavy only in the name Allah when preceded by fatha or damma
- **Vowel letters** — alef, dagger alef, or alef maksura carrying a heavy vowel (e.g. `خَا`, `طَا`, `ٱلْكُبْرَى`) gets both `tafkheem` and its madd rule

### Qalqala (Echoing)

| Rule | Type | Description | Trigger |
|------|------|-------------|---------|
| `qalqala_sughra` | source | Minor echoing bounce on qalqala letter with sukun | ق ط ب ج د with sukun (mid-word/verse) |
| `qalqala_kubra` | source | Major echoing bounce at a stop | ق ط ب ج د with sukun at waqf |

### Hamza Wasl (Starting Vowel)

| Rule | Type | Description | Trigger |
|------|------|-------------|---------|
| `hamza_wasl_fatha` | source | Hamza wasl pronounced with fatha when starting | Starting on ال (definite article) |
| `hamza_wasl_kasra` | source | Hamza wasl pronounced with kasra when starting | Starting on a verb/noun with kasra pattern |
| `hamza_wasl_damma` | source | Hamza wasl pronounced with damma when starting | Starting on a verb with damma pattern |

### Iltiqaa (Meeting of Two Sukuns)

| Rule | Type | Description | Trigger |
|------|------|-------------|---------|
| `iltiqaa_sakinayn_tanween` | source | Tanween gets kasra added when followed by hamza wasl | tanween + ٱ |
| `silent_iltiqaa_sakinayn` | source | Long vowel shortened before hamza wasl | Long vowel + ٱ |

### Idgham Mutajanisayn (Partial)

| Rule | Type | Description | Trigger |
|------|------|-------------|---------|
| `idgham_mutajanisayn_naqis` | source+target | Partial assimilation — source letter changes but is not fully silent | ط before ت (e.g. `بَسَطتَ`) |

### Madd (Vowel Lengthening)

| Rule | Type | Description | Duration |
|------|------|-------------|----------|
| `madd_tabii` | source | Natural lengthening — long vowel with no cause | 2 counts |
| `madd_wajib_muttasil` | source | Obligatory connected — long vowel followed by hamza in the same word | 4–5 counts |
| `madd_jaiz_munfasil` | source | Permissible separated — long vowel at word-end followed by hamza in next word | 2–4–5 counts |
| `madd_lazim` | source | Obligatory — long vowel followed by sukun (including shaddah) in same word | 6 counts |
| `madd_arid_lissukun` | source | Presented lengthening — long vowel before a letter that gets sukun from stopping | 2–4–6 counts |
| `madd_leen` | source | Soft lengthening — fatha + waw/yaa sakin before a stopping sukun | 2–4–6 counts |

Madd rules appear on the **vowel grapheme** that carries the lengthening:
- Vowel letters (alef, waw, yaa) — the madd rule is on the letter entry directly
- Dagger alef (ٰ) / mini waw (ۥ) / mini yaa (ۦ) — split into a separate entry with the madd rule
- Iwad (fathatan + hamza at stop) — `madd_tabii` is on the hamza entry

## Multi-Rule Overlap

A single letter can carry multiple rules from different categories simultaneously. The most common overlaps:

| Combination | Example |
|-------------|---------|
| tafkheem + madd | Alef after heavy consonant: `خَا` → alef has `[tafkheem, madd_tabii]` |
| tafkheem + qalqala | Qaf or taa with sukun: `قْ` → `[tafkheem, qalqala_sughra]` |
| idgham (target) + tafkheem | Raa as idgham target: نْ + ر → raa has `source: [tafkheem]`, `target: [idgham_bila_ghunnah_noon]` |

Rules that appear on **different entries** (no overlap):
- Muqattaat letters are spelled out as separate words, so ghunnah and madd land on different entries
- Iltiqaa tags the previous vowel letter, while `hamza_wasl_silent` tags the hamza — separate entries
- Extension splitting separates a letter's own rule from the dagger alef's madd rule

## Stopping and Starting Effects

Tajweed rules change depending on whether recitation stops (waqf) or starts (ibtidaa) at a word. The `is_stopping` flag on each word indicates the recitation context. The rules in the output already reflect this context:

**Rules that appear only when stopping:**
- `madd_arid_lissukun` — long vowel before a consonant that receives sukun from stopping
- `madd_leen` — soft vowel before stopping sukun
- `madd_tabii` (iwad) — fathatan becomes long vowel at stop
- `qalqala_kubra` — qalqala letter at word-end when stopping (may be `qalqala_sughra` or absent when continuing)

**Rules that appear only when starting:**
- `hamza_wasl_fatha` / `hamza_wasl_kasra` / `hamza_wasl_damma` — hamza wasl is pronounced only when starting; these rules replace `hamza_wasl_silent` (which applies mid-verse when the hamza is skipped over)

**Rules that disappear when stopping:**
- Cross-word noon/meem rules (ikhfaa, iqlab, idgham) — the last letter receives sukun, blocking cross-word interaction
- Cross-word idgham rules (`idgham_mutamathilayn`, `idgham_mutaqaribayn`, `idgham_mutajanisayn`) — same reason; stopping breaks the word boundary assimilation
- Both iltiqaa rules (`iltiqaa_sakinayn_tanween`, `silent_iltiqaa_sakinayn`) — only apply when continuing into a hamza wasl; disappear when stopping before that word
- `madd_jaiz_munfasil` — becomes `madd_tabii` when stopping; the cross-word hamza interaction does not occur, so the long vowel is treated as natural lengthening
- `tafkheem` on raa — may disappear when stopping if the word-final raa's sukun (from waqf) is preceded by a kasra or ya, switching to tarqeeq

**Rules that appear only due to stopping (context-dependent):**
- `tafkheem` on raa — may appear when stopping if the word-final raa receives sukun and the preceding vowel context favors heaviness (fatha or damma), whereas it was absent when continuing with a different vowel

## Huroof Muqattaat (Opening Letters)

The disconnected letters at the start of certain surahs (e.g. الٓمٓ, حمٓ, كٓهيعٓصٓ) are returned in their **spelled-out recitation form**, with each letter name as a separate word:

| Compact | Output words | Rule highlights |
|---------|-------------|-----------------|
| الٓمٓ | أَلِفْ · لَآم · مِّيٓمْ | `madd_lazim` on ا in لَآم, `idgham_shafawi` between م←م, `madd_lazim` on ي in مِّيٓمْ |
| صٓ | صَآدْ | `tafkheem` on ص, `madd_lazim` on ا, `qalqala_kubra` on د |
| كٓهيعٓصٓ | كآفْ · هَا · يَا · عَيْن · صَآدْ | Rules distributed across individual words |

This matches how muqattaat are actually recited and ensures each rule lands on the correct grapheme.

## Serialization

```python
tajweed = result.tajweed_mappings()

# JSON string
print(tajweed.to_json(indent=2))

# Python dict
data = tajweed.to_dict()

# Save to file
result.save("output.tajweed.json", fmt="tajweed")
```
