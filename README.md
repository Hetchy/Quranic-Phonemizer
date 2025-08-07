# Qurʾānic Phonemizer

A modular phonemizer (Grapheme to Phoneme converter) for the Qurʾān in the Hafs riwaya, converting text to phoneme sequences with support for Tajweed rules.

The system uses a hierarchical pipeline that tokenizes text, applies contextual phoneme mappings, and processes Tajweed rules. It is highly extensible and customizable.

## Table of Contents
- [Phoneme Inventory](#phoneme-inventory)
  - [Consonants](#consonants)
  - [Vowels](#vowels)
  - [Tajweed Rules](#tajweed-rules)
- [Usage](#usage)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
- [Input References](#input-references)
- [Outputs](#outputs)
- [Stops (Boundary Markers)](#stops-boundary-markers)
- [Contributing](#contributing)
- [Credits](#credits)
- [Citing](#citing)

## Phoneme Inventory

The phoneme inventory uses the standard International Phonetic Alphabet (IPA) [Arabic phonemes](https://en.wikipedia.org/wiki/Help%3AIPA/Arabic?utm_source=chatgpt.com) alongside custom phonemes for Tajweed rules. There is a total of 72 phonemes, corresponding to:

- 28 consonants
- 24 geminated consonants
- 8 vowels
- 12 Tajweed phonemes

All phonemes are configurable in [resources/base_phonemes.yaml](resources/base_phonemes.yaml) and [resources/rule_phonemes.yaml](resources/rule_phonemes.yaml).

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

Gemination (shaddah) is represented by repeating the phoneme to create new distinct phonemes. Note that there is no gemination for `m` / `n` (modelled as Tajweed instead), and for `ʔ` / `ɣ` (do not exist in the Qurʾān).

### Vowels


| **Vowel**     | **Phoneme**   |
|:-------------:|:-------------:|
| َ              | `a` / `aˤ`    |
| ُ              | `u`           |
| ِ              | `i`           |
| ا             | `a:` / `aˤ:`  |
| و             | `u:`          |
| ي , ى         | `i:`          |


### Tajweed Rules

| **Rule**           | **Phoneme**                                              |
|:------------------:|:---------------------------------------------------------|
| Idgham             | `ñ` / `m̃` / `j̃` / `w̃`                                    |
| Iqlab              | `m̃`                                                      |
| Ikhfaa             | `ŋ`  (Light)<br> `ŋˤ` (Heavy)<br> `ɱ`  (Shafawi)        |
| Qalqala            | `Q`  (Sughra)<br> `QQ` (Kubra)                          |
| Tafkheem           | `lˤlˤ` (Lam in "Allah")<br> `rˤ` / `rˤrˤ` (Raa)                    |

## Usage

### Installation


```bash
git clone https://github.com/Hetchy/Quranic-Phonemizer.git
cd phonemizer
pip install -r requirements.txt
```

### Quick Start

```python
from core.phonemizer import Phonemizer

pm = Phonemizer()
res = pm.phonemize("1:1")
print(res.text)
print(res.phonemes_str())
```

بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِيمِ ‏﴿١﴾‏

bismi llahi rraħma:ni rraħi:m

## Input References
`phonemize` accepts a variety of flexible formats to specify which part of the Qurʾān to phonemize:

| Format Example  | Meaning                                                |
| --------------- | ------------------------------------------------------ |
| `"1"`           | Entire chapter 1 (Al-Fātiħa)                       |
| `"1:1"`         | Verse 1 of chapter 1                               |
| `"1:1:1"`       | Word 1 of verse 1 of chapter 1                     |
| `"1:1 - 1:4"`   | Verse range: 1:1 through 1:4                       |
| `"1:1 - 1:2:2"` | From 1:1 to word 2 of 1:2                          |
| `"1 - 2:2"`     | From entire chapter 1 through verse 2 of chapter 2 |


## Outputs
The phonemizer returns a `PhonemizeResult` object, which contains:

| Attribute           | Description                                                 |
| ------------------- | ----------------------------------------------------------- |
| `ref`               | The original reference string                               |
| `text`              | The Qurʾānic text                                            |
| `phonemes_nested()` | List of phoneme lists, one per word                         |
| `phonemes_flat()`   | Flat list of all phonemes                                   |
| `phonemes_str()`    | Full phoneme string, configurable with separators           |
| `show_table()`      | Pandas DataFrame view: word locations, word text, phonemes  |
| `save(path, fmt)`   | Save results to JSON or CSV                                 |

### Output Example (Phonemes String)

```python
res = pm.phonemize("112", stops=["verse"])
print(res.text)
print(res.phonemes_str(phoneme_sep=" ", word_sep=" | ", verse_sep="\n"))
```
قُلۡ هُوَ ٱللَّهُ أَحَدٌ ‏﴿١﴾‏ ٱللَّهُ ٱلصَّمَدُ ‏﴿٢﴾‏ لَمۡ يَلِدۡ وَلَمۡ يُولَدۡ ‏﴿٣﴾‏ وَلَمۡ يَكُن لَّهُۥ كُفُوًا أَحَدُۢ ‏﴿٤﴾‏

q u l | h u w a | ll a h u | ʔ a ħ a d QQ

ʔ a ll a h u | sˤsˤ a m a d QQ

l a m | j a l i d Q | w a l a m | j u: l a d QQ

w a l a m | j a k u | ll a h u: | k u f u w a n | ʔ a ħ a d QQ

### Output Example (Table View)

```python
res = pm.phonemize("112", stops=["verse"])
df = res.show_table()
df
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>location</th>
      <th>word</th>
      <th>phonemes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>112:1:1</td>
      <td>قُلۡ</td>
      <td>qul</td>
    </tr>
    <tr>
      <th>1</th>
      <td>112:1:2</td>
      <td>هُوَ</td>
      <td>huwa</td>
    </tr>
    <tr>
      <th>2</th>
      <td>112:1:3</td>
      <td>ٱللَّهُ</td>
      <td>llahu</td>
    </tr>
    <tr>
      <th>3</th>
      <td>112:1:4</td>
      <td>أَحَدٌ</td>
      <td>ʔaħadQQ</td>
    </tr>
    <tr>
      <th>4</th>
      <td>112:2:1</td>
      <td>ٱللَّهُ</td>
      <td>ʔallahu</td>
    </tr>
    <tr>
      <th>5</th>
      <td>112:2:2</td>
      <td>ٱلصَّمَدُ</td>
      <td>sˤsˤamadQQ</td>
    </tr>
    <tr>
      <th>6</th>
      <td>112:3:1</td>
      <td>لَمۡ</td>
      <td>lam</td>
    </tr>
    <tr>
      <th>7</th>
      <td>112:3:2</td>
      <td>يَلِدۡ</td>
      <td>jalidQ</td>
    </tr>
    <tr>
      <th>8</th>
      <td>112:3:3</td>
      <td>وَلَمۡ</td>
      <td>walam</td>
    </tr>
    <tr>
      <th>9</th>
      <td>112:3:4</td>
      <td>يُولَدۡ</td>
      <td>ju:ladQQ</td>
    </tr>
    <tr>
      <th>10</th>
      <td>112:4:1</td>
      <td>وَلَمۡ</td>
      <td>walam</td>
    </tr>
    <tr>
      <th>11</th>
      <td>112:4:2</td>
      <td>يَكُن</td>
      <td>jaku</td>
    </tr>
    <tr>
      <th>12</th>
      <td>112:4:3</td>
      <td>لَّهُۥ</td>
      <td>llahu:</td>
    </tr>
    <tr>
      <th>13</th>
      <td>112:4:4</td>
      <td>كُفُوًا</td>
      <td>kufuwan</td>
    </tr>
    <tr>
      <th>14</th>
      <td>112:4:5</td>
      <td>أَحَدُۢ</td>
      <td>ʔaħadQQ</td>
    </tr>
  </tbody>
</table>
</div>

## Stops (Boundary Markers)

Optionally, pass a `stops=[]` list to force word/verse segmentation:

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
print(res.text)
print(res.phonemes_str())

res = pm.phonemize(ref, stops=["preferred_continue"])
print(res.phonemes_str())

res = pm.phonemize(ref, stops=["optional_stop"])
print(res.phonemes_str())
```

كَذٰلِكَ ٱلۡعَذَابُ‌ۖ وَلَعَذَابُ ٱلۡأَخِرَةِ أَكۡبَرُ‌ۚ لَوۡ كَانُواۡ يَعۡلَمُونَ ‏﴿٣٣﴾‏

kaða:lika lʕaða:b`u` walaʕaða:bu lʔaxirati ʔakba`ru` law ka:nu: jaʕlamu:n

kaða:lika lʕaða:b`QQ` walaʕaða:bu lʔaxirati ʔakba`ru` law ka:nu: jaʕlamu:n

kaða:lika lʕaða:b`u` walaʕaða:bu lʔaxirati ʔakba`r` law ka:nu: jaʕlamu:n


```python
ref = "44:43 - 44:44"
res = pm.phonemize(ref, stops=["verse"])
print(res.text)
print(res.phonemes_str(phoneme_sep="", word_sep=" ", verse_sep=""))

res = pm.phonemize(ref, stops=[])
print(res.phonemes_str(phoneme_sep="", word_sep=" ", verse_sep=""))
```

إِنَّ شَجَرَتَ ٱلزَّقُّومِ ‏﴿٤٣﴾‏ طَعَامُ ٱلۡأَثِيمِ ‏﴿٤٤﴾‏

ʔiña ʃaʒarata zzaqqu:`m` tˤaʕa:mu lʔaθi:m

ʔiña ʃaʒarata zzaqqu:`mi` tˤaʕa:mu lʔaθi:m

## Contributing

If you find any issues or have suggestions for improvements, please feel free to email me, open an issue or submit a pull request. 

The following features are yet to be implemented:
- Lam/Raa Tafkheem & Tarqeeq rules
- Support other qira'at/riwayat

## Credits

The project makes use of a modified version of the Quranic Universal Library's (QUL) [Hafs script with Tajweed](https://qul.tarteel.ai/resources/quran-script/58).

## Citing
