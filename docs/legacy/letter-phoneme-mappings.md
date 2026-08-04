# Letter-Phoneme Mappings

Letter-phoneme mappings provide flat `[chars, phonemes]` entries for any phonemized passage. Every entry has at least one phoneme — silent letters are merged into adjacent entries. Word boundaries appear as spaces in the `chars` field.

```python
from quranic_phonemizer import Phonemizer

pm = Phonemizer()
result = pm.phonemize("1:1")
lpm = result.letter_phoneme_mappings()
for chars, phonemes in lpm.to_list():
    print(f"{chars!r} -> {phonemes}")
```

```
'ب' -> ['b', 'i']
'س' -> ['s']
'م ' -> ['m', 'i']
'ٱلل' -> ['ll', 'a:']
'ه ' -> ['h', 'i']
'ٱلر' -> ['rˤrˤ', 'aˤ']
'ح' -> ['ħ']
'م' -> ['m']
'ٰ' -> ['a:']
'ن ' -> ['n', 'i']
'ٱلر' -> ['rˤrˤ', 'aˤ']
'ح' -> ['ħ']
'ي' -> ['i:']
'م' -> ['m']
```

## Output Structure

```
FlatMappingResult
├── ref: str                                  # Resolved reference
├── entries: List[Tuple[str, List[str]]]      # Flat [chars, phonemes] pairs
└── mapping: PhonemizationMapping             # Full mapping for validation
```

Each entry is a `(chars, phonemes)` pair where:
- **chars** — one or more Arabic characters, possibly with a trailing space for word boundaries
- **phonemes** — one or more IPA phoneme strings (always non-empty)

## Core Principles

### No Empty Entries

Every entry has at least one phoneme. When a letter produces no sound (silent letters), it is merged into an adjacent entry rather than appearing alone with empty phonemes.

### Word Boundaries via Spaces

- **Space suffix** on the last entry of a word = normal word boundary: `"ب " -> ['b', 'i']`
- **Space inside** an entry = cross-word merge (silent letter at word end merged with next word's first letter): `"ن ر" -> ['rˤrˤ', 'aˤ']`
- The final word has no trailing space

### Merge Directions

| Direction | When | Result |
|-----------|------|--------|
| **PREV** | Silent letter merges into previous entry | `"وا" -> ['w']` — silent alef appended to waw |
| **NEXT** | Silent letter merges into next entry | `"ٱلر" -> ['rˤrˤ', 'aˤ']` — hamza wasl and lam prepended to raa |
| **CROSS-WORD** | Silent letter at word end merges with next word's first | `"ن م" -> ['m̃', 'i']` — space inside chars |

## Examples

### Silent vowel letters (PREV merge)

Silent alef, waw, or yaa merge into the preceding entry.

```
كَفَرُوا۟ (2:6:3)
["ك",  ["k", "a"]]
["ف",  ["f", "a"]]
["ر",  ["rˤ"]]
["وا ", ["u:"]]       ← silent alef merged into previous (waw)
```

### Lam shamsiyah + hamza wasl (NEXT merge)

Silent letters at word start merge into the next sounding letter.

```
ٱلرَّحْمَـٰنِ (1:1:3)
["ٱلر", ["rˤrˤ", "aˤ"]]   ← hamza wasl + lam merge into next (raa)
["ح",   ["ħ"]]
["م",   ["m"]]
["ٰ",   ["a:"]]             ← dagger alef split into own entry
["ن ",  ["n", "i"]]
```

### Cross-word idgham — noon merging (CROSS-WORD merge)

Silent noon at word end merges with the next word's first letter into a single entry with space inside.

```
مِن رَّبِّهِمْ (2:26:18-19)
["م",   ["m", "i"]]
["ن ر", ["rˤrˤ", "aˤ"]]    ← noon silent, merged with raa across word boundary
["ب",   ["bb", "i"]]
["ه",   ["h", "i"]]
["م ",  ["m"]]
```

### Cross-word non-merge — ikhfaa (space suffix)

When both sides of the word boundary have phonemes, they stay separate. The last entry of the first word gets a space suffix.

```
مِن قَبْلِكَ (2:4:8-9)
["م",  ["m", "i"]]
["ن ", ["ŋ"]]              ← noon nasalized, keeps phoneme, space suffix
["ق",  ["q", "aˤ"]]
["ب",  ["b", "Q"]]
["ل",  ["l", "i"]]
["ك ", ["k", "a"]]
```

### Tanween with silent alef (PREV merge + space suffix)

The alef after tanween is always silent and merges into the previous entry. If the tanween has a cross-word effect, the result gets a space suffix.

```
رِزْقًا لَّكُمْ (2:22:16-17)
["ر",   ["r", "i"]]
["ز",   ["z"]]
["قا ", ["q", "aˤ"]]       ← silent alef merged into previous, space suffix for word boundary
["ل",   ["ll", "a"]]
["ك",   ["k", "u"]]
["م ",  ["m"]]
```

### Extension splitting — dagger alef

When a consonant carries a dagger alef (or mini waw/yaa), the extension is split into its own entry so each long vowel phoneme has exactly one corresponding grapheme.

```
ٱلرَّحْمَـٰنِ (1:1:3)
["م",  ["m"]]      ← consonant keeps its phoneme
["ٰ",  ["a:"]]     ← dagger alef gets the madd phoneme
```

Extensions that split: dagger alef (`ٰ`), mini waw (`ۥ`), mini yaa end (`ۦ`).

Exceptions that do NOT split:
- Maddah (`ٓ`) — stays with its base letter
- Alef maksura + dagger alef (`ىٰ`) — reinforcing extension, stays together

### Iltiqaa — long vowel before hamza wasl (CROSS-WORD merge)

When a long vowel meets hamza wasl across a word boundary, the vowel is shortened. The demoted short vowel moves back to the preceding consonant, and the now-silent vowel letter chains cross-word into the next word.

```
فِى ٱلْأَرْضِ (2:11:6-7)
["ف",     ["f", "i"]]      ← consonant gets the demoted short vowel
["ى ٱل", ["l"]]            ← silent yaa chains cross-word into next word
["أ",     ["ʔ", "a"]]
["ر",     ["rˤ"]]
["ض ",    ["dˤ", "i"]]
```

### Stopping — tanween becomes long vowel

When stopping on a word with fathatan + alef, the tanween becomes a long vowel on the consonant. The alef carries the long vowel after redistribution.

```python
result = pm.phonemize("2:5:3", stop_refs=["2:5:3"])
```
```
هُدًى (2:5:3) — stopping
["ه",  ["h", "u"]]
["د",  ["d"]]
["ى",  ["a:"]]            ← alef maksura gets redistributed madd phoneme
```

### Muqattaat (special words)

Disconnected letters are spelled out with pre-computed phonemes. No extension splitting — phoneme order matches the letter name pronunciation.

```
الٓمٓ (2:1:1)
["ا",  ["ʔ", "a", "l", "i", "f"]]    ← "alif" spelled out
["لٓ", ["l", "a:"]]                    ← lam with maddah
["مٓ", ["m̃", "i:", "m"]]              ← meem with maddah
```

## Merge Rules Reference

### Group 1: PREV merges (silent vowel letters)

Silent letters that merge into the **previous** entry.

| Case | Example | Result |
|------|---------|--------|
| Silent alef (always) | `مَّشَوْا۟` | `["وا", ["w"]]` |
| Silent alef (continuation) | `أَنَا۠` continuing | `["نا", ["n", "a"]]` |
| Silent waw | `أُو۟لَـٰٓئِكَ` | `["أو", ["ʔ", "u"]]` |
| Silent yaa | `مَلَإِي۟هِمْ` | `["إي", ["ʔ", "i"]]` |
| Tanween alif | `رِزْقًا` | `["قا", ["q", "aˤ"]]` — alef after tanween |
| Special stop skip | `ءَاتَىٰنَِۧ` stopping | `["نۧ", ["n"]]` — mini yaa skipped |

### Group 2: Idgham (assimilation)

Merge direction depends on position — within-word merges into next entry, cross-word creates a merged entry with space, or stays separate with space suffix.

| Rule | Cross-Word | Example |
|------|-----------|---------|
| Idgham mutamathilayn | MERGE | `["ن ن", [...]]` — identical letters |
| Idgham mutaqaribayn | MERGE | Close articulation points |
| Idgham mutajanisayn kamil | MERGE | `["ذ ظ", ["ðˤðˤ", "aˤ"]]` |
| Idgham ghunnah noon | MERGE | `["ن م", ["m̃", "i"]]` — noon + ي/ن/م/و |
| Idgham bila ghunnah noon | MERGE | `["ن ر", ["rˤrˤ", "aˤ"]]` — noon + ل/ر |
| Idgham shafawi | BOTH MERGE | `["م م", ["m̃", "a"]]` — both meems have phonemes |
| Idgham ghunnah tanween | NON-MERGE | `["ب ", ["b", "i"]]` — space suffix |
| Idgham bila ghunnah tanween | NON-MERGE | `["قا ", ["q", "aˤ"]]` — space suffix |
| Ikhfaa noon | NON-MERGE | `["ن ", ["ŋ"]]` — noon nasalized |
| Iqlab noon | NON-MERGE | `["ن ", ["ŋ"]]` — noon before baa |
| Ikhfaa tanween | NON-MERGE | `["قا ", ["q", "aˤ", "ŋ"]]` — vowel + nasal |
| Iqlab tanween | NON-MERGE | `["م ", ["m", "u", "ŋ"]]` — vowel + nasal |
| Ikhfaa shafawi | NON-MERGE | `["م ", ["ŋ"]]` — meem before baa |

### Group 3: NEXT merges (word-start silent letters)

Silent letters at word start that merge into the **next** sounding letter.

| Case | Example | Result |
|------|---------|--------|
| Hamza wasl (silent) | `ٱلرَّحْمَـٰنِ` | `["ٱلر", ["rˤrˤ", "aˤ"]]` |
| Lam shamsiyah | `ٱلرَّحِيمِ` | Lam merges into next (sun letter) |
| Iltiqaa tanween | `جَمِيعًا ٱلَّذِى` | `["ٱل", ["ll", "a"]]` — hamza wasl after tanween |
| Iltiqaa vowel | `فِى ٱلْأَرْضِ` | `["ى ٱل", ["l"]]` — vowel silent, cross-word chain |

## Stopping and Starting Effects

The mapping changes depending on whether recitation stops or continues at a word.

**When stopping:**
- Last letter's vowel removed (sukun) — fewer phonemes but letter still has its consonant
- Tanween on last letter becomes long vowel (madd iwad)
- Qalqala letters at word end gain `"Q"` phoneme
- Cross-word effects disappear — each word is self-contained

**When starting:**
- Hamza wasl is pronounced (has phonemes) instead of silent
- First letter's shaddah removed

**Entry count may differ:** A letter that is silent when continuing (e.g., `أَنَا۠` — alef merges into previous) becomes pronounced when stopping (alef gets `["a:"]` — own entry). The flat mapping must be generated per-phonemization with specific stopping context.

## Validation Rules

Five rules are enforced programmatically and can be checked via `result.validate()`:

1. **No empty phonemes** — every entry has `len(phonemes) >= 1`
2. **Character coverage** — concatenating all `chars` (minus spaces) reproduces every letter and extension character from the source, in order
3. **Madd grapheme correspondence** — every long vowel phoneme (containing `:`) has a corresponding madd grapheme in the same entry's chars (with exceptions for Allah, hamza+fathatan, and muqattaat)
4. **Space placement** — total space count equals `word_count - 1`; each word boundary has exactly one space
5. **No orphaned phonemes** — every entry's phonemes come from at least one non-silent source letter

## Serialization

```python
lpm = result.letter_phoneme_mappings()

# List of (chars, phonemes) tuples
entries = lpm.to_list()

# JSON string
print(lpm.to_json(indent=2))

# Validate
violations = lpm.validate()  # empty list = valid

# Save to file
lpm.save("output.json")

# Or via result.save()
result.save("output.json", fmt="letter_phoneme")
```