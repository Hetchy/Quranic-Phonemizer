# Qurʾanic Phonemizer

<p align="center">
  <a href="https://pypi.org/project/quranic-phonemizer/"><img src="https://img.shields.io/pypi/v/quranic-phonemizer" alt="PyPI version"></a>
  <a href="https://pypi.org/project/quranic-phonemizer/"><img src="https://img.shields.io/pypi/pyversions/quranic-phonemizer" alt="Python versions"></a>
  <a href="https://quranicphonemizer.com/"><img src="https://img.shields.io/badge/Demo-quranicphonemizer.com-blue" alt="Website"></a>
  <a href="https://huggingface.co/datasets/hetchyy/everyayah-phonemes"><img src="https://img.shields.io/badge/%F0%9F%A4%97_Hugging_Face-EveryAyah_Phonemes_Dataset-yellow" alt="Dataset"></a>
  <a href="https://openreview.net/forum?id=hZt0JK28iV"><img src="https://img.shields.io/badge/Paper-OpenReview-red" alt="Paper"></a>
  <a href="https://github.com/Hetchy/Quranic-Phonemizer/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/quranic-phonemizer" alt="License"></a>
  <a href="https://pypi.org/project/quranic-phonemizer/"><img src="https://static.pepy.tech/badge/quranic-phonemizer/month" alt="Downloads"></a>
</p>

A Grapheme-to-Phoneme converter (G2P) for the Qurʾan (Hafs riwaya), converting text to phoneme sequences with comprehensive support for all tajweed rules and waqf phonetic effects.

Potential use cases:

- **Speech Recognition**: Phonetically transcribe recitations, create training data for machine learning systems
- **Text-to-Speech**: Develop accurate TTS systems for Qurʾanic Arabic
- **Linguistic & Tajweed Analysis**: Study phonological patterns and tajweed rule distributions across the Qurʾan, apply tajweed rule labels and coloring
- **Educational Tools**: Build interactive applications for assessing Qur'an and tajweed pronunciation
- **Timing Analysis**: Generate word-by-word timestamps for recitations, analyse madd/ghunnah durations

In addition to the Python API, the phonemizer can be used interactively: [quranicphonemizer.com](https://quranicphonemizer.com/).

## Table of Contents
- [Phoneme Inventory](#phoneme-inventory)
- [Usage](#usage)
- [Input References](#input-references)
- [Text Search](#text-search)
- [Outputs](#outputs)
- [Stops (Waqf)](#stops-waqf)
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
| `show_table(phoneme_sep, split)` | Pandas DataFrame view, grouped by `split` (requires `pandas`)  |
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

## Phonetic Text

`phonetic_text()` returns a recitation-accurate rendering of the Arabic text, applying the phonetic transforms that occur when starting or stopping on a word. This is useful for displaying text as it would actually be recited.

### Starting Transforms

| Transform | Original | Phonetic Text |
|---|---|---|
| Hamza wasl → fatha | `ٱلرَّحْمَٰنِ` | `أَلرَّحْمَٰنْ` |
| Hamza wasl → damma | `ٱدْعُ` | `أُدْعْ` |
| Hamza wasl → kasra | `ٱهْدِنَا` | `إِهْدِنَا` |
| Remove first-letter shaddah | `لِّلْمُتَّقِينَ` | `لِلْمُتَّقِينْ` |

### Stopping Transforms

| Transform | Original | Phonetic Text |
|---|---|---|
| Haraka → sukun | `ٱلرَّحِيمِ` | `ٱلرَّحِيمْ` |
| Taa marbuta → haa + sukun | `رَحْمَةِ` | `رَحْمَهْ` |
| Madd iwad (alef) | `كِتَٰبًا` | `كِتَٰبَا` |
| Madd iwad (hamza) | `دُعَآءً` | `دُعَآءَا` |
| Strip madd silah | `حَوْلَهُۥ` | `حَوْلَهْ` |

### Other Transforms

| Transform | Original | Phonetic Text |
|---|---|---|
| Allah dagger alef | `ٱللَّهِ` | `ٱللَّـٰهِ` |

### Huroof Muqattaʿat

Opening letters are returned as their spelled-out recitation forms:

| Text | Phonetic Text |
|---|---|
| الٓمٓ | أَلِفْ لَآم مِّيٓمْ |
| الٓر | أَلِفْ لَآمْ رَا |
| الٓمٓصٓ | أَلِفْ لَآم مِّيٓمْ صَآدْ |
| الٓمٓر | أَلِفْ لَآم مِّيٓمْ رَا |
| كٓهيعٓصٓ | كآفْ هَا يَا عَيْن صَآدْ |
| طه | طَا هَا |
| طسٓمٓ | طَا سِيٓن مِّيٓمْ |
| طسٓ | طَا سِيٓنْ |
| يسٓ | يَا سِيٓنْ |
| صٓ | صَآدْ |
| حمٓ | حَا مِيٓمْ |
| عٓسٓقٓ | عَيْن سِيٓن قَآفْ |
| قٓ | قَآفْ |
| نٓ | نُوٓنْ |

## Contributing

If you find any issues or have feature suggestions, please feel free to open an issue or submit a pull request. 

Future plans include detailed tajweed annotations and support for other turuq and riwayat.

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
