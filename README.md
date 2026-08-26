# Qurʾanic Phonemizer

<p align="center">
  <a href="https://pypi.org/project/quranic-phonemizer/"><img src="https://img.shields.io/pypi/v/quranic-phonemizer" alt="PyPI version"></a>
  <a href="https://quranicphonemizer.com/"><img src="https://img.shields.io/badge/Demo-quranicphonemizer.com-blue" alt="Website"></a>
  <a href="https://openreview.net/forum?id=hZt0JK28iV"><img src="https://img.shields.io/badge/Paper-OpenReview-red" alt="Paper"></a>
  <a href="https://github.com/Hetchy/Quranic-Phonemizer/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/quranic-phonemizer" alt="License"></a>
</p>

Qur'anic Grapheme-to-Phoneme (G2P) converter and tajweed annotator for the riwayat of Hafs 'An Asim and Warsh 'An Nafi', converting text to phoneme sequences with comprehensive support for waqf/intidaa transformations and tajweed breakdowns.

Use cases:

- **Speech Recognition**: Phonetically transcribe recitations, create training data for machine learning systems
- **Text-to-Speech**: Develop accurate TTS systems for Qurʾanic Arabic
- **Linguistic & Tajweed Analysis**: Study phonological patterns and tajweed rule distributions across the Qurʾan, apply tajweed rule labels and coloring
- **Educational Tools**: Build interactive applications for assessing Qur'an and tajweed pronunciation
- **Timing Analysis**: Generate word-by-word timestamps for recitations, analyse madd/ghunnah durations

## Table of Contents
- [Phoneme Inventory](#phoneme-inventory)
- [Quick start](#quick-start)
- [Waqf](#waqf)
- [Analysis](#analysis)
- [Tajweed rules](#tajweed-rules)
- [Contributing](#contributing)
- [Credits](#credits)
- [Citing](#citing)

## Phoneme Inventory

The phoneme inventory uses the standard International Phonetic Alphabet (IPA) [Arabic phonemes](https://en.wikipedia.org/wiki/Help%3AIPA/Arabic?utm_source=chatgpt.com) alongside custom phonemes for Tajweed rules. Hafs has 68 base phonemes plus 5 optional tokens; Warsh has 71 base phonemes plus 4 optional tokens.

### Foundational Phonemes

| **Letter**               | **Phoneme**              | **Letter** | **Phoneme**               | **Letter** | **Phoneme**              | **Letter** | **Phoneme**              |
|:------------------------:|:------------------------|:----------:|:-------------------------|:----------:|:------------------------|:----------:|:------------------------|
| أ , إ , ء , ؤ , ئ        | `ʔ`                      | د          | `d` / `dd`                | ض          | `dˤ` / `dˤdˤ`            | ك          | `k` / `kk`              |
| ب                        | `b` / `bb`               | ذ          | `ð` / `ðð`                | ط          | `tˤ` / `tˤtˤ`            | ل          | `l` / `lˤ` / `ll` /  `lˤlˤ` |
| ت                        | `t` / `tt`               | ر          | `r` / `rˤ` / `rr` / `rˤrˤ`| ظ          | `ðˤ` / `ðˤðˤ`            | م          | `m`                      |
| ث                        | `θ` / `θθ`               | ز          | `z` / `zz`                | ع          | `ʕ` / `ʕʕ`               | ن          | `n`                      |
| ج                        | `ʒ` / `ʒʒ`               | س          | `s` / `ss`                | غ          | `ɣ`                      | هـ         | `h` / `hh`               |
| ح                        | `ħ` / `ħħ`               | ش          | `ʃ` / `ʃʃ`                | ف          | `f` / `ff`               | و          | `w` / `ww`               |
| خ                        | `x` / `xx`               | ص          | `sˤ` / `sˤsˤ`             | ق          | `q` / `qq`               | ي , ى      | `j` / `jj`               |

`lˤ` is the single emphatic lam used in Warsh. Gemination (shaddah) is represented by repeating the phoneme to create new distinct phonemes. Note that there is no gemination for `m` / `n` (modelled as tajweed instead), and for `ʔ` / `ɣ` (do not exist in the Qurʾān).

### Vowel Phonemes

| **Vowel**                      | **Phoneme**            |
|:--------------------------------|:------------------------|
| َ                              | `a`                    |
| ُ                              | `u`                    |
| ِ                              | `i`                    |
| ا , ى                          | `aː` / `aˤː`           |
| و                              | `uː`                   |
| ي , ى                          | `iː`                   |
| ى۪ Warsh Taqlil (Imala Sughra) | `ɛː`                   |

### Tajweed Phonemes

| **Rule**       | **Phoneme**                   |
|----------------|:------------------------------|
| Ikhfaa         | `ŋ`                           |
| Ikhfaa shafawi | `ŋ` / `m̃`                    |
| Iqlab          | `ŋ` / `m̃`                    |
| Idgham         | `ñ` / `m̃` / `j̃` / `w̃`     |
| Qalqala        | `Q`                           |

Iqlab and ikhfaa shafawi use the open-lip nasal `ŋ` by default. Their nasal variants can instead select the closed-lip bilabial realization `m̃`, since both alternatives exist in recitations.

### Extra Phonemes

`extra_phonemes` selects toggleable output distinctions. Its default is empty to keep the default inventory compact; the underlying reading rule is unchanged.

| **API option**              | **Phoneme**        | **Default** | **Notes** |
|-----------------------------|:------------------|:-----------:|:---------|
| `emphatic_fatha`            | `aˤ`              | Off         | Allophone |
| `emphatic_ikhfaa`           | `ŋˤ`              | Off         | Heavy nasal allophone |
| `qalqala_degree`            | `QQ`              | Off         | Stronger Qalqala kubra/akbar degree |
| `tashil` (Hafs only)        | `ʔ̞`              | Off         | One case Hafs: `ءَا۬عْجَمِيٌّ` (41:44), off -> `ʔ` <br>Warsh always applies Tashil as `ʔ̞` since it is common |
| `imala` (kubra)             | `e:`              | Off         | Hafs: `مَجْر۪ىٰهَا` (11:41), off -> `i:` <br> Warsh: `طَه۪` (20:1), off -> `ɛ:` |

## Quick start

Install the package and create a reader for the riwayah you need:

```bash
pip install quranic-phonemizer
```

```python
from quranic_phonemizer import Phonemizer

hafs = Phonemizer()
warsh = Phonemizer(riwayah="warsh")

for name, reader, ref in (
    ("Hafs 1:4", hafs, "1:4"),
    ("Warsh 1:3", warsh, "1:3"),
):
    result = reader.analyse(ref)
    print(name)
    print(result.text())
    print(" ".join(result.phonemes()))
```

```text
Hafs 1:4
مَـٰلِكِ يَوْمِ ٱلدِّينِ
m a: l i k i j a w m i dd i: n

Warsh 1:3
مَلِكِ يَوْمِ اِ۬لدِّينِۖ
m a l i k i j a w m i dd i: n
```

The phoneme sequences differ at one token:

Hafs: m `a:` l i k i j a w m i dd i: n

Warsh: m `a` l i k i j a w m i dd i: n

### References

`analyse()` accepts words, verses, surahs, and ranges:

| Reference | Selection |
| :--- | :--- |
| `"1"` | Surah 1 |
| `"1:3"` | Ayah 3 of surah 1 |
| `"1:3:1"` | Word 1 of ayah 1:3 |
| `"1:3-1:4"` | Ayahs 1:3 through 1:4 |
| `"1:3-1:4:2"` | Ayah 1:3 through word 2 of 1:4 |
| `"1-2:2"` | Surah 1 through ayah 2:2 |

## Waqf

Use `stop_signs` to apply waqf at mushaf signs and `stop_refs` to stop after exact words:

```python
hafs.analyse("68:33", stop_signs=("optional_stop",))
hafs.analyse("2:255", stop_refs=("2:255:7",))
```

This applies waqf to `2:255:7` and ibtidaa to `2:55:8`, or any words with `ۚ ` in `68:33`, changing phonemes and tajweed rules accordingly.

Note the first and last word of a request always apply ibtidaa and waqf respectively.

`reader.available_stop_signs` gives the keys valid for that reader. Hafs uses:

| Stop key | Sign |
| :--- | :---: |
| `preferred_continue` | ۖ |
| `preferred_stop` | ۗ |
| `optional_stop` | ۚ |
| `compulsory_stop` | ۘ |
| `prohibited_stop` | ۙ |
| `either_stop` | ۛ |

Warsh exposes only `optional_stop`ۖ

## Analysis

The phonemizer exposes more detailed analysis, breakdowns, relationships and rules:

```python
result = hafs.analyse("107:4")

print(result.text())
print(" ".join(result.phonemes()))
print([occurrence.rule_id.value for occurrence in result.rule_occurrences])
```

```text
فَوَيْلٌ لِّلْمُصَلِّينَ
f a w a j l u ll i l m u sˤ a ll i: n
['waqf_diacritic_drop', 'idgham_bila_ghunnah', 'lam_qamariyyah',
 'izhar', 'madd_arid_lissukun', 'tafkheem']
```

The core records are available directly:

```python
result.words
result.boundaries
result.sounds
result.rule_occurrences
result.mergers
```

The same result provides its source units, highlight groups, and transformed cells:

```python
source = result.source()
highlights = result.highlights()
cells = result.cells(spelling="transformed")
```

The transformed view contains 19 columns. These are the columns carrying a rule, a spelling change, or shared sound presentation:

| Column | Text | Status | Rule occurrence | Owns | Presents |
| ---: | :---: | --- | --- | --- | --- |
| 7 | `ٌ` | `present` | `1 idgham_bila_ghunnah` | `6` | `7` |
| 8 | `لّ` | `present` | `1 idgham_bila_ghunnah` | `7` | |
| 10 | `لْ` | `present` | `2 lam_qamariyyah` | `9` | |
| 14 | `ص` | `present` | `5 tafkheem` | `12` | |
| 15 | `َ` | `present` | `5 tafkheem` | `13` | |
| 17 | `ِ` | `present` | | | `15` |
| 18 | `ي` | `present` | `4 madd_arid_lissukun` | `15` | |
| 19 | `نْ` | `replaced` | `3 izhar` | `16` | |
| 20 | `َ` | `dropped` | `0 waqf_diacritic_drop` | | |

The first boundary bridges columns 7 and 8 through sound 7 and rule occurrence 1. IDs remain valid across the core analysis, source view, highlights, and cells.

`document()` returns JSON-compatible schema 2 documents for the analysis and its projections. See the [public API reference](docs/public-api.md) for every record and field.

## Tajweed rules

The catalogue is scoped to the reader. Each definition provides an ID, English name, Arabic name, and summary:

```python
for rule in hafs.tajweed_rules:
    print(rule.id.value, rule.name, rule.arabic_name, rule.summary)

result.rule_definition("idgham_bila_ghunnah")
result.rule_occurrences
```

`rule_occurrences` contains the rules applied to that request. Hafs and Warsh share these published rule IDs:

- Noon and tanween: `izhar`, `ikhfaa`, `iqlab`, `idgham_bi_ghunnah`, `idgham_bila_ghunnah`, `ghunnah_mushaddadah`
- Meem sakinah: `izhar_shafawi`, `ikhfaa_shafawi`, `idgham_shafawi`
- Assimilation and the definite article: `idgham_mutamathilayn`, `idgham_mutaqaribayn`, `idgham_mutajanisayn_kamil`, `idgham_mutajanisayn_naqis`, `lam_shamsiyyah`, `lam_qamariyyah`
- Qalqala: `qalqala_sughra`, `qalqala_kubra`, `qalqala_akbar`
- Tafkheem and tarqeeq: `tafkheem`, `tarqeeq`
- Special readings: `imala`, `tashil`, `ishmam`
- Madd: `madd_tabii`, `madd_muttasil`, `madd_munfasil`, `madd_lazim`, `madd_arid_lissukun`, `madd_leen`, `madd_iwad`, `madd_badal`, `madd_silah`
- Hamza and adjacent sakin letters: `ibdal_hamza`, `hamza_wasl_silent`, `hamza_wasl_fatha`, `hamza_wasl_damma`, `hamza_wasl_kasra`, `iltiqa_haraka`, `iltiqa_shortening`
- Waqf and silence: `waqf_diacritic_drop`, `waqf_silah_drop`, `waqf_taa_marbuta`, `pausal_alif` (seven alifs), `orthographic_silence` (rasm)

Warsh adds five rule IDs:

- `taqlil`
- `madd_leen_mahmuz`
- `madd_mim_al_jam`
- `madd_yaa_zawaid`
- `naql`

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
