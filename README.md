# Qurʾanic Phonemizer

<p align="center">
  <a href="https://pypi.org/project/quranic-phonemizer/"><img src="https://img.shields.io/pypi/v/quranic-phonemizer" alt="PyPI version"></a>
  <a href="https://pypi.org/project/quranic-phonemizer/"><img src="https://img.shields.io/pypi/pyversions/quranic-phonemizer" alt="Python versions"></a>
  <a href="https://quranicphonemizer.com/"><img src="https://img.shields.io/badge/Demo-quranicphonemizer.com-blue" alt="Website"></a>
  <a href="https://huggingface.co/datasets/hetchyy/everyayah-phonemes"><img src="https://img.shields.io/badge/%F0%9F%A4%97_Hugging_Face-EveryAyah_Phonemes_Dataset-yellow" alt="Dataset"></a>
  <a href="https://openreview.net/forum?id=hZt0JK28iV"><img src="https://img.shields.io/badge/Paper-OpenReview-red" alt="Paper"></a>
  <a href="https://github.com/Hetchy/Quranic-Phonemizer/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/quranic-phonemizer" alt="License"></a>

A Grapheme-to-Phoneme converter (G2P) for the Qurʾan (Hafs riwaya), converting text to phoneme sequences with comprehensive support for waqf phonetic effects and tajweed mappings.

Potential use cases:

- **Speech Recognition**: Phonetically transcribe recitations, create training data for machine learning systems
- **Text-to-Speech**: Develop accurate TTS systems for Qurʾanic Arabic
- **Linguistic & Tajweed Analysis**: Study phonological patterns and tajweed rule distributions across the Qurʾan, apply tajweed rule labels and coloring
- **Educational Tools**: Build interactive applications for assessing Qur'an and tajweed pronunciation
- **Timing Analysis**: Generate word-by-word timestamps for recitations, analyse madd/ghunnah durations

## Table of Contents
- [Phoneme Inventory](#phoneme-inventory)
- [Usage](#usage)
- [Input References](#input-references)
- [Text Search](#text-search)
- [Outputs](#outputs)
- [Stops (Waqf)](#stops-waqf)
- [Tajweed Mappings](#tajweed-mappings)
- [Letter-Phoneme Mappings](#letter-phoneme-mappings)
- [Phonetic Text](#phonetic-text)
- [Contributing](#contributing)
- [Credits](#credits)
- [Citing](#citing)

## Phoneme Inventory

The phoneme inventory uses the standard International Phonetic Alphabet (IPA) [Arabic phonemes](https://en.wikipedia.org/wiki/Help%3AIPA/Arabic?utm_source=chatgpt.com) alongside custom phonemes for Tajweed rules, totalling 69-71 phonemes (depending on Tajweed configuration).

All phonemes are configurable in [resources/base_phonemes.yaml](quranic_phonemizer/resources/base_phonemes.yaml) and [resources/rule_phonemes.yaml](quranic_phonemizer/resources/rule_phonemes.yaml).

### Consonants
| **Letter**               | **Phoneme**              | **Letter** | **Phoneme**               | **Letter** | **Phoneme**              | **Letter** | **Phoneme**              |
|:------------------------:|:------------------------:|:----------:|:-------------------------:|:----------:|:------------------------:|:----------:|:------------------------:|
| أ , إ , ء , ؤ , ئ        | `ʔ`                      | د          | `d` / `dd`                | ض          | `dˤ` / `dˤdˤ`            | ك          | `k` / `kk`              |
| ب                        | `b` / `bb`               | ذ          | `ð` / `ðð`                | ط          | `tˤ` / `tˤtˤ`            | ل          | `l` / `ll` / `lˤlˤ`      |
| ت                        | `t` / `tt`               | ر          | `r` / `rˤ` / `rr` / `rˤrˤ`| ظ          | `ðˤ` / `ðˤðˤ`            | م          | `m`                      |
| ث                        | `θ` / `θθ`               | ز          | `z` / `zz`                | ع          | `ʕ` / `ʕʕ`               | ن          | `n`                      |
| ج                        | `ʒ` / `ʒʒ`               | س          | `s` / `ss`                | غ          | `ɣ`                      | هـ         | `h` / `hh`               |
| ح                        | `ħ` / `ħħ`               | ش          | `ʃ` / `ʃʃ`                | ف          | `f` / `ff`               | و          | `w` / `ww`               |
| خ                        | `x` / `xx`               | ص          | `sˤ` / `sˤsˤ`             | ق          | `q` / `qq`               | ي , ى      | `j` / `jj`               |

Gemination (shaddah) is represented by repeating the phoneme to create new distinct phonemes. Note that there is no gemination for `m` / `n` (modelled as tajweed instead), and for `ʔ` / `ɣ` (do not exist in the Qurʾān).

### Vowels


| **Vowel**     | **Phoneme**   |
|:-------------:|:-------------:|
| َ              | `a` / `aˤ`    |
| ُ              | `u`           |
| ِ              | `i`           |
| ا , ى         | `a:` / `aˤ:`  |
| و             | `u:`          |
| ي , ى         | `i:`          |


### Tajweed Rules

| **Rule**           | **Phoneme**                                              |
|:------------------:|:---------------------------------------------------------|
| Iqlab              | `ŋ`                                                       |
| Idgham             | `ñ` / `m̃` / `j̃` / `w̃`                                    |
| Ikhfaa             | `ŋ`  (Light)<br> `ŋˤ` (Heavy)<br> `ŋ` (Shafawi)          |
| Qalqala            | `Q`  (Sughra)<br> `QQ` (Kubra)                           |
| Tafkheem           | `lˤlˤ` (Lam in "Allah")<br> `rˤ` / `rˤrˤ` (Raa)          |

## Usage

### Installation

```bash
pip install quranic-phonemizer
```

### Quick Start

```python
from quranic_phonemizer import Phonemizer

pm = Phonemizer()
res = pm.phonemize("1:1")
print(res.text())
print(res.phonemes_str())
```

بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ  ١ 

bismi lla:hi rˤrˤaˤħma:ni rˤrˤaˤħi:m

## Input References
`phonemize()` accepts a variety of flexible formats to specify which part of the Qurʾān to phonemize:

| Format Example  | Meaning                                              |
| --------------- | -----------------------------------------------------|
| `"1"`           | Entire chapter 1                                     |
| `"1:1"`         | Verse 1 of chapter 1                                 |
| `"1:1:1"`       | Word 1 of verse 1 of chapter 1                       |
| `"1:1 - 1:4"`   | Verse range: 1:1 through 1:4                         |
| `"1:1 - 1:2:2"` | From 1:1 to word 2 of 1:2                            |
| `"1 - 2:2"`     | From entire chapter 1 through verse 2 of chapter 2   |


## Text Search

Instead of a reference, you can pass Arabic text directly using `ref_text` to fuzzy-match against the Uthmanic Hafs text of the Qur'an:

```python
res = pm.phonemize(ref_text="بسم الله الرحمن الرحيم")
print(res.ref)
print(res.match_score)
print(res.phonemes_str())
```

1:1:1-1:1:4

0.903

bismi lla:hi rˤrˤaˤħma:ni rˤrˤaˤħi:m

The `match_score` attribute (0–1) indicates how closely the input text matched the Qurʾānic text. You can also scope the search to a specific surah or range by combining `ref` and `ref_text`:

```python
res = pm.phonemize(ref="2", ref_text="الله لا إله إلا هو الحي القيوم")
print(res.ref)
print(res.match_score)
print(res.phonemes_str())
```

2:255:1-2:255:7

0.836

ʔalˤlˤaˤ:hu la: ʔila:ha ʔilla: huwa lħajju lqaˤjju:m

## Outputs
`phonemize()` returns a `PhonemizeResult` object, containing:

| Attribute           | Description                                                 |
| ------------------- | ----------------------------------------------------------- |
| `ref`               | The resolved reference string                               |
| `match_score`       | Fuzzy match confidence (0–1) when using `ref_text`; `None` otherwise |
| `text()`            | The Qurʾānic text  |
| `phonemes_list(split)` | Phoneme lists grouped by `split`: `"word"`, `"verse"`, or `"both"` |
| `phonemes_str(phoneme_sep, word_sep, verse_sep)` | Full phoneme string, configurable with separators           |
| `show_table(phoneme_sep, split)` | Tabular view grouped by `split`. Returns a `pandas.DataFrame` if `pandas` is installed; otherwise prints a plain-text table and returns the rows as a list of dicts |
| `save(path, *, fmt, split)` | Save results to JSON, CSV, or mapping format |
| `phonetic_text(word_sep, verse_sep)` | Recitation-accurate display text with stopping/starting transforms |

### Output Example (Phonemes String)

```python
res = pm.phonemize("112", stop_signs=["verse"])
print(res.text())
print(res.phonemes_str(phoneme_sep=" ", word_sep=" | ", verse_sep="\n"))
```
قُلْ هُوَ ٱللَّهُ أَحَدٌ  ١  ٱللَّهُ ٱلصَّمَدُ  ٢  لَمْ يَلِدْ وَلَمْ يُولَدْ  ٣  وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌ  ٤ 

q u l | h u w a | lˤlˤ aˤ: h u | ʔ a ħ a d Q |
ʔ a lˤlˤ aˤ: h u | sˤsˤ aˤ m a d Q |
l a m | j a l i d Q | w a l a m | j u: l a d Q |
w a l a m | j a k u | ll a h u: | k u f u w a n | ʔ a ħ a d Q

## Stops (Waqf)

Optionally, pass `stop_signs=[]` to apply stops at Quranic stop signs, and/or `stop_refs=[]` to stop at specific word locations:

| Stop key               | Symbol 
| ---------------------- | ------ 
| `"verse"`              | ۝
| `"preferred_continue"` | ۖ      
| `"preferred_stop"`     | ۗ      
| `"optional_stop"`      | ۚ      
| `"compulsory_stop"`    | ۘ      
| `"prohibited_stop"`    | ۙ      

```python
ref = "68:33"
res = pm.phonemize(ref)
print(res.text())
print(res.phonemes_str())

res = pm.phonemize(ref, stop_signs=["preferred_continue"])
print(res.phonemes_str())

res = pm.phonemize(ref, stop_signs=["optional_stop"])
print(res.phonemes_str())
```

كَذَٰلِكَ ٱلْعَذَابُ ۖ وَلَعَذَابُ ٱلْـَٔاخِرَةِ أَكْبَرُ ۚ لَوْ كَانُوا۟ يَعْلَمُونَ  ٣٣ 

kaða:lika lʕaða:`bu` walaʕaða:bu lʔa:xirˤaˤti ʔakba`rˤu` law ka:nu: jaʕlamu:n

kaða:lika lʕaða:`bQ` walaʕaða:bu lʔa:xirˤaˤti ʔakba`rˤu` law ka:nu: jaʕlamu:n

kaða:lika lʕaða:`bu` walaʕaða:bu lʔa:xirˤaˤti ʔakba`rˤ` law ka:nu: jaʕlamu:n

```python
# Stop at a specific word location
res = pm.phonemize("1:1-1:3", stop_refs=["1:2:2"])
```

## Tajweed Mappings

`tajweed_mappings()` returns per-letter tajweed rule annotations for any phonemized passage. Each Arabic letter is annotated with the rules it participates in, distinguishing between **source rules** (rules the letter triggers) and **target rules** (rules affecting this letter from another letter). Annotations account for starting and stopping effects — cross-word rules disappear when stopping, while rules like `qalqala_kubra` and `madd_arid_lissukun` only appear at stops.

```python
result = pm.phonemize("1:1", stop_signs=["verse"])
tajweed = result.tajweed_mappings()
print(tajweed.to_json(indent=2))
```

Example output for `ٱلرَّحْمَـٰنِ` (continuing):

```json
{"location": "1:1:3", "entries": [
  {"char": "ٱ", "source_rules": ["hamza_wasl_silent"]},
  {"char": "ل", "source_rules": ["lam_shamsiyah"]},
  {"char": "ر", "source_rules": ["tafkheem"], "target_rules": ["lam_shamsiyah"]},
  {"char": "ح"},
  {"char": "م"},
  {"char": "ٰ", "source_rules": ["madd_tabii"]},
  {"char": "ن"}
]}
```

Extension characters (dagger alef `ٰ`, mini waw `ۥ`, mini yaa `ۦ`) are split into their own entries so their madd rules are kept separate from the base letter. Huroof muqattaat are returned in their spelled-out recitation form (e.g. الٓمٓ → أَلِفْ · لَآم · مِّيٓمْ).

### Rules

**Source-only** — rules that annotate only the letter itself:

- `tafkheem`
- `noon_ghunnah`, `meem_ghunnah`
- `qalqala_sughra`, `qalqala_kubra`
- `vowel_silent`, `silent_iltiqaa_sakinayn`, `iltiqaa_sakinayn_tanween`
- `hamza_wasl_silent`, `hamza_wasl_fatha`, `hamza_wasl_kasra`, `hamza_wasl_damma`
- `madd_tabii`, `madd_wajib_muttasil`, `madd_jaiz_munfasil`, `madd_lazim`, `madd_arid_lissukun`, `madd_leen`

**Source + target** — the source letter triggers the rule and a second letter is annotated as the target:

- `iqlab_noon`, `iqlab_tanween`
- `ikhfaa_noon`, `ikhfaa_tanween`, `ikhfaa_shafawi`
- `idgham_ghunnah_noon`, `idgham_ghunnah_tanween`, `idgham_shafawi`
- `idgham_bila_ghunnah_noon`, `idgham_bila_ghunnah_tanween`
- `idgham_mutamathilayn`, `idgham_mutaqaribayn`, `idgham_mutajanisayn_kamil`, `idgham_mutajanisayn_naqis`, `lam_shamsiyah`

For full details, examples, and multi-rule overlap documentation, see [docs/tajweed-mappings.md](docs/tajweed-mappings.md).

## Letter-Phoneme Mappings

`letter_phoneme_mappings()` returns flat `[chars, phonemes]` pairs where every entry has at least one phoneme. Silent letters are merged into adjacent entries rather than appearing with empty phonemes, and word boundaries are encoded as spaces in the `chars` field.

```python
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

### Merge Rules

Silent letters merge in one of three directions:

| Direction | When | Example |
|-----------|------|---------|
| **PREV** | Silent vowel letter merges into previous entry | `"وا" -> ['w']` — silent alef appended to waw |
| **NEXT** | Silent letter at word start merges into next entry | `"ٱلر" -> ['rˤrˤ', 'aˤ']` — hamza wasl + lam into raa |
| **CROSS-WORD** | Silent letter at word end merges with next word's first | `"ن ر" -> ['rˤrˤ', 'aˤ']` — space inside chars |

When both sides of a word boundary have phonemes, they stay separate with a space suffix on the last entry: `"ن " -> ['ŋ']`.

Extension characters (dagger alef, mini waw, mini yaa) are split into their own entries. Mappings reflect stopping/starting context — entry count and merge patterns change depending on waqf.

For full details, merge rule reference, and validation rules, see [docs/letter-phoneme-mappings.md](docs/letter-phoneme-mappings.md).

## Contributing

If you find any issues or have feature suggestions, please feel free to open an issue or submit a pull request. 

Future plans include support for other turuq and riwayat.

## Credits

The project makes use of the [Quranic Universal Library's (QUL) Hafs script](https://qul.tarteel.ai/resources/quran-script/312).

## Citing

If you use this phonemizer in your work, please cite [the paper](https://openreview.net/pdf?id=hZt0JK28iV) as follows:

```bibtex
@inproceedings{
ibrahim2025quranic,
title={Qur{\textquoteright}anic Phonemizer: Bringing Tajweed-Aware Phonemes to Qur{\textquoteright}anic Machine Learning},
author={Ahmed Ibrahim},
booktitle={5th Muslims in ML Workshop co-located with NeurIPS 2025},
year={2025},
url={https://openreview.net/forum?id=hZt0JK28iV}
}
```
