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
- [Stops (Waqf)](#stops-waqf)
- [Outputs](#outputs)
- [Phonemes](#phonemes)
- [Recited Text](#recited-text)
- [Alignment](#alignment)
- [Respelling](#respelling)
- [Tajweed Rules](#tajweed-rules)
- [Optional Phonemes](#optional-phonemes)
- [Variants](#variants)
- [Contributing](#contributing)
- [Credits](#credits)
- [Citing](#citing)

## Phoneme Inventory

The phoneme inventory uses the standard International Phonetic Alphabet (IPA) [Arabic phonemes](https://en.wikipedia.org/wiki/Help%3AIPA/Arabic) alongside custom phonemes for Tajweed rules, totalling 67 phonemes, rising to 73 when every [optional phoneme](#optional-phonemes) is enabled.

All phonemes are defined in [data/render/ipa.yaml](quranic_phonemizer/data/render/ipa.yaml).

### Consonants

| **Letter** | **Phoneme** | **Letter** | **Phoneme** | **Letter** | **Phoneme** |
|:---:|:---:|:---:|:---:|:---:|:---:|
| ء , أ , إ , ؤ , ئ , ٱ | `ʔ` | ز | `z` / `zz` | ف | `f` / `ff` |
| ب | `b` / `bb` | س | `s` / `ss` | ق | `q` / `qq` |
| ت , ة | `t` / `tt` | ش | `ʃ` / `ʃʃ` | ك | `k` / `kk` |
| ث | `θ` / `θθ` | ص | `sˤ` / `sˤsˤ` | ل | `l` / `ll` / `lˤlˤ` |
| ج | `ʒ` / `ʒʒ` | ض | `dˤ` / `dˤdˤ` | م | `m` |
| ح | `ħ` / `ħħ` | ط | `tˤ` / `tˤtˤ` | ن | `n` |
| خ | `x` / `xx` | ظ | `ðˤ` / `ðˤðˤ` | ه | `h` / `hh` |
| د | `d` / `dd` | ع | `ʕ` / `ʕʕ` | و | `w` / `ww` |
| ذ | `ð` / `ðð` | غ | `ɣ` | ي , ى | `j` / `jj` |
| ر | `r` / `rr` / `rˤ` / `rˤrˤ` | | | | |

Gemination (shaddah) is represented by repeating the phoneme to create new distinct phonemes. There is no gemination for `m` / `n` (modelled as tajweed instead), and none for `ʔ` / `ɣ` (they do not occur geminated in the Qurʾān).

### Vowels

| **Vowel** | **Phoneme** |
|:---:|:---:|
| َ | `a` |
| ُ | `u` |
| ِ | `i` |
| ا , ى | `a:` |
| و | `u:` |
| ي , ى | `i:` |

`aˤ` is added by the `emphatic_fatha` optional phoneme; emphatic alef is always `aˤ:`. `e:` is added by `imala`.

### Tajweed Phonemes

| **Rule** | **Phoneme** |
|:---:|:---:|
| Iqlab | `ŋ` |
| Ikhfaa Haqiqi | `ŋ` |
| Ikhfaa Shafawi | `ŋ` |
| Idgham bi-Ghunnah | `ñ` / `m̃` / `j̃` / `w̃` |
| Idgham Shafawi | `m̃` |
| Ghunnah Mushaddadah | `ñ` / `m̃` |
| Qalqala | `Q` |
| Tafkheem | `lˤlˤ` (Lam in "Allah")<br>`rˤ` / `rˤrˤ` (Raa) |

Iqlab and Ikhfaa Shafawi also have a `m̃` reading, selected as a [variant](#variants). Heavy Ikhfaa `ŋˤ` and extended Qalqala `QQ` are [optional phonemes](#optional-phonemes).

## Usage

### Installation

```bash
pip install quranic-phonemizer
```

Python 3.11 or newer is required.

### Quick Start

```python
from quranic_phonemizer import Phonemizer

pm = Phonemizer()
res = pm.phonemize("1:1")
print(res.text())
print(" ".join(res.phonemes()))
```

```
بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ
b i s m i ll a: h i rˤrˤ a ħ m a: n i rˤrˤ a ħ i: m
```

`Phonemizer()` is built once and reused; every call to `phonemize()` returns a fresh `PhonemizeResult`. Hafs is the only riwaya shipped, and `supported_riwayat()` lists what a build has.

## Input References
`phonemize()` accepts a variety of flexible formats to specify which part of the Qurʾān to phonemize:

| Format Example | Meaning |
| --------------- | -----------------------------------------------------|
| `"1"`           | Entire chapter 1                                     |
| `"1:1"`         | Verse 1 of chapter 1                                 |
| `"1:1:1"`       | Word 1 of verse 1 of chapter 1                       |
| `"1:1 - 1:4"`   | Verse range: 1:1 through 1:4                         |
| `"1:1:1 - 1:1:4"` | Word range: word 1 of 1:1 through word 4 of 1:1    |
| `"113 - 114"`   | Chapter range: 113 through 114                       |

Both ends of a range must be the same depth: chapter to chapter, verse to verse, or word to word.

## Stops (Waqf)

Words in a request are joined by default, and its last word is always stopped on. Pass `stop_signs=[]` to stop at Qurʾanic stop signs, and/or `stop_refs=[]` to stop at specific words:

| Stop key | Symbol |
| ---------------------- | ------ |
| `"preferred_continue"` | ۖ      |
| `"preferred_stop"`     | ۗ      |
| `"optional_stop"`      | ۚ      |
| `"compulsory_stop"`    | ۘ      |
| `"prohibited_stop"`    | ۙ      |
| `"either_stop"`        | ۛ      |

```python
ref = "68:33"
res = pm.phonemize(ref)
print(res.text())
print(" ".join(res.phonemes()))

print(" ".join(pm.phonemize(ref, stop_signs=["preferred_continue"]).phonemes()))
print(" ".join(pm.phonemize(ref, stop_signs=["optional_stop"]).phonemes()))
```

```
كَذَٰلِكَ ٱلْعَذَابُ ۖ وَلَعَذَابُ ٱلْـَٔاخِرَةِ أَكْبَرُ ۚ لَوْ كَانُوا۟ يَعْلَمُونَ
k a ð a: l i k a l ʕ a ð a: b u w a l a ʕ a ð a: b u l ʔ a: x i rˤ a t i ʔ a k b a rˤ u l a w k a: n u: j a ʕ l a m u: n
k a ð a: l i k a l ʕ a ð a: b Q w a l a ʕ a ð a: b u l ʔ a: x i rˤ a t i ʔ a k b a rˤ u l a w k a: n u: j a ʕ l a m u: n
k a ð a: l i k a l ʕ a ð a: b u w a l a ʕ a ð a: b u l ʔ a: x i rˤ a t i ʔ a k b a rˤ l a w k a: n u: j a ʕ l a m u: n
```

The first stop turns `ٱلْعَذَابُ` into `...b Q`, the second drops the final damma of `أَكْبَرُ`.

To stop at the end of every verse, pass each verse's last word to `stop_refs`:

```python
res = pm.phonemize("112", stop_refs=["112:1:4", "112:2:2", "112:3:4"])
for word, sounds in zip(res.words, res.phonemes("word")):
    print(word.location, word.text, " ".join(sounds))
```

```
112:1:1 قُلْ q u l
112:1:2 هُوَ h u w a
112:1:3 ٱللَّهُ lˤlˤ a: h u
112:1:4 أَحَدٌ ʔ a ħ a d Q
112:2:1 ٱللَّهُ ʔ a lˤlˤ a: h u
112:2:2 ٱلصَّمَدُ sˤsˤ a m a d Q
112:3:1 لَمْ l a m
112:3:2 يَلِدْ j a l i d Q
112:3:3 وَلَمْ w a l a m
112:3:4 يُولَدْ j u: l a d Q
112:4:1 وَلَمْ w a l a m
112:4:2 يَكُن j a k u
112:4:3 لَّهُۥ ll a h u:
112:4:4 كُفُوًا k u f u w a n
112:4:5 أَحَدٌ ʔ a ħ a d Q
```

## Outputs

`phonemize()` returns a `PhonemizeResult`. The methods answer the common questions; the arrays under them are the same answer in full detail, and index into each other.

| Member | Description |
| ------ | ----------- |
| `ref` | The resolved reference string |
| `riwayah`, `script` | What produced this result |
| `variant` | Every [variant](#variants) point with the option in force |
| `extra_phonemes` | The [optional phonemes](#optional-phonemes) enabled |
| `phonemes(by)` | Phoneme tokens; `by="word"` groups them per word |
| `text(which)` | `"source"` for the written text, `"recited"` for the recited text |
| `alignment(text, grouping)` | Which characters produced which phonemes |
| `respelling(grouping)` | The written text against the recited text, block by block |
| `words` | One per word: location, text, whether it is started on or stopped on |
| `units` | One per letter: the letter, whether it is geminate, and the vowel after it |
| `sounds` | One per phoneme: its token and the features behind it |
| `rules` | One per tajweed rule applied: the rule, its source letter and its host letter |
| `glyphs`, `rendered` | One per character of the written and the recited text |
| `spellings`, `attributions`, `modifiers` | The edges joining glyphs, units, sounds and rules |
| `schema_version`, `canon_digest` | The shape of this result, and a digest of the passage it was built from |

## Phonemes

`phonemes()` returns the reading in order. `phonemes("word")` groups it by word.

```python
res = pm.phonemize("1:1")
for word, sounds in zip(res.words, res.phonemes("word")):
    print(word.location, word.text, " ".join(sounds))
```

```
1:1:1 بِسْمِ b i s m i
1:1:2 ٱللَّهِ ll a: h i
1:1:3 ٱلرَّحْمَـٰنِ rˤrˤ a ħ m a: n i
1:1:4 ٱلرَّحِيمِ rˤrˤ a ħ i: m
```

`ٱللَّهِ` starts at `ll` because its hamza wasl is elided when joined. Where a rule merges a letter into the next word, the phoneme belongs to the word that holds it:

```python
res = pm.phonemize("2:5:4-2:5:5")
for word, sounds in zip(res.words, res.phonemes("word")):
    print(word.location, word.text, " ".join(sounds))
```

```
2:5:4 مِّن m i
2:5:5 رَّبِّهِمْ rˤrˤ a bb i h i m
```

## Recited Text

`text("recited")` returns the Arabic text as it is actually recited, with the transforms that starting on and stopping on a word apply.

```python
for ref in ("1:2", "1:6", "2:2:1"):
    res = pm.phonemize(ref)
    print(res.text(), "->", res.text("recited"))
```

```
ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَـٰلَمِينَ -> أَلْحَمْدُ لِلَّآهِ رَبِّ لْعَآلَمِىٓنْ
ٱهْدِنَا ٱلصِّرَٰطَ ٱلْمُسْتَقِيمَ -> إِهْدِنَ صِّرَآطَ لْمُسْتَقِىٓمْ
ذَٰلِكَ -> ذَآلِكْ
```

## Alignment

`alignment()` pairs characters with the phonemes they produced. `text` selects which text to pair against, `"source"` or `"recited"`; `grouping` is `"glyph"` for one pairing per character, or `"cell"` to group each letter with its own vowel marks.

Each pairing carries indices into the result's arrays: `glyphs` (or `rendered`), the `sounds` it owns, `shares` for sounds it presents but another pairing owns, `silent` for characters that produced nothing, and `rules`.

```python
res = pm.phonemize("1:1:2")
for pairing in res.alignment(text="source", grouping="cell"):
    chars = "".join(res.glyphs[g].char for g in pairing.glyphs)
    sounds = [res.sounds[s].token for s in pairing.sounds]
    rules = [res.rules[r].rule.value for r in pairing.rules]
    print(f"{chars!r} {sounds} {rules}")
```

```
'ٱ' ['ʔ'] ['wasl_start']
'' ['a'] []
'ل' [] ['lam_shamsiyyah', 'tafkheem']
'لَّ' ['lˤlˤ', 'a:'] ['lam_shamsiyyah', 'madd_arid_lil_sukun', 'tafkheem']
'هِ' ['h'] ['pausal_sukun']
```

A pairing with no characters is a phoneme no letter wrote, such as the helping fatha above; its `after` field names the pairing it follows. A pairing with no phonemes is a silent letter, such as the lam of the definite article assimilated into the lam after it.

## Respelling

`respelling()` runs both alignments and returns the blocks where the written text and the recited text correspond. Each block holds indices into the two alignments.

```python
res = pm.phonemize("1:2")
source = res.alignment(text="source", grouping="cell")
recited = res.alignment(text="recited", grouping="cell")
for block in res.respelling():
    before = "".join(res.glyphs[g].char for i in block.source for g in source[i].glyphs)
    after = "".join(res.rendered[g].char for i in block.recited for g in recited[i].glyphs)
    print(f"{before!r} -> {after!r}")
```

```
'ٱ' -> 'أَ'
'لْ' -> 'لْ'
'حَ' -> 'حَ'
'مْ' -> 'مْ'
'دُ' -> 'دُ'
'لِ' -> 'لِ'
'لَّ' -> 'لَّآ'
'هِ' -> 'هِ'
'رَ' -> 'رَ'
'بِّ' -> 'بِّ'
'ٱ' -> ''
'لْ' -> 'لْ'
'ع' -> 'ع'
'َـٰ' -> 'َآ'
'لَ' -> 'لَ'
'م' -> 'م'
'ِي' -> 'ِىٓ'
'نَ' -> 'نْ'
```

## Tajweed Rules

`rules` holds every rule the passage applied. `source` is the letter the rule is about, and `host` the letter it merges into; only a merger has a host. Both are indices into `units`. Cross-word rules disappear when stopping, and rules such as `qalqala_kubra` and `madd_arid_lil_sukun` only appear at a stop.

```python
res = pm.phonemize("2:8:3-2:8:4")
print(res.text(), "|", " ".join(res.phonemes()))
for rule in res.rules:
    source = res.units[rule.source].letter.value if rule.source is not None else None
    host = res.units[rule.host].letter.value if rule.host is not None else None
    print(rule.rule.value, source, host)
```

```
مَن يَقُولُ | m a j̃ a q u: l
pausal_sukun lam None
idgham_bi_ghunnah noon ya
madd_arid_lil_sukun qaf None
tafkheem qaf None
```

Some rules also carry teaching `labels` for the cases they are taught under: `madd_badal`, `silah` and `silah_kubra`.

```python
res = pm.phonemize("104:3")
print(res.text())
for rule in res.rules:
    if rule.labels:
        print(res.words[res.units[rule.source].word].text, rule.rule.value, rule.labels)
```

```
يَحْسَبُ أَنَّ مَالَهُۥٓ أَخْلَدَهُۥ
مَالَهُۥٓ madd_jaiz_munfasil ('silah', 'silah_kubra')
```

`tajweed_rules("hafs")` lists all 40 rule identifiers with their English and Arabic names.

```python
from quranic_phonemizer import tajweed_rules

for row in tajweed_rules("hafs")[:4]:
    print(row)
```

```
('izhar', 'Izhar', 'إظهار')
('ikhfaa_haqiqi', 'Ikhfaa Haqiqi', 'إخفاء حقيقي')
('iqlab', 'Iqlab', 'إقلاب')
('idgham_bi_ghunnah', 'Idgham bi-Ghunnah', 'إدغام بغنة')
```

## Optional Phonemes

Five distinctions are not written by default. Pass `extra_phonemes` to spend a phoneme on any of them.

| Name | Distinction |
| ---- | ----------- |
| `emphatic_fatha` | A short fatha next to an emphatic letter becomes `aˤ` |
| `emphatic_ikhfaa` | Ikhfaa before an istilaa letter becomes `ŋˤ` |
| `qalqala_degree` | Qalqala kubra and akbar become `QQ`, apart from sughra `Q` |
| `tashil` | An eased hamza becomes `ʔ̞` |
| `imala` | The inclined vowel becomes `e:`, otherwise read as `i:` |

```python
for extra in ((), ("emphatic_fatha",)):
    print(" ".join(Phonemizer(extra_phonemes=extra).phonemize("1:1").phonemes()))

for extra in ((), ("qalqala_degree",)):
    print(" ".join(Phonemizer(extra_phonemes=extra).phonemize("111:1:5").phonemes()))

for extra in ((), ("emphatic_ikhfaa",)):
    print(" ".join(Phonemizer(extra_phonemes=extra).phonemize("107:5:3-107:5:4").phonemes()))

for extra in ((), ("imala",)):
    print(" ".join(Phonemizer(extra_phonemes=extra).phonemize("11:41:6").phonemes()))
```

```
b i s m i ll a: h i rˤrˤ a ħ m a: n i rˤrˤ a ħ i: m
b i s m i ll a: h i rˤrˤ aˤ ħ m a: n i rˤrˤ aˤ ħ i: m
w a t a bb Q
w a t a bb QQ
ʕ a ŋ sˤ a l a: t i h i m
ʕ a ŋˤ sˤ a l a: t i h i m
m a ʒ Q r i: h a:
m a ʒ Q r e: h a:
```

## Variants

Where Hafs admits more than one reading, `available_variants()` lists the points and their options, and `variants` selects one. The result reports back what was in force in its `variant` attribute.

```python
from quranic_phonemizer import available_variants

print(sorted(available_variants("hafs")))
print(available_variants("hafs")["iqlab_nasal"])
```

```
['alism_ibtidaa', 'almusaytirun', 'bal_ran', 'bastah', 'bimusaytir', 'daaf_haraka', 'ikhfaa_shafawi_nasal', 'iqlab_nasal', 'irkab_maana', 'istifham_article', 'iwaja_qayyima', 'maliyah_halak', 'man_raq', 'marqadina_hadha', 'noon_wasl', 'raa_alqitr_waqf', 'raa_asr_waqf', 'raa_firq', 'raa_misr_waqf', 'raa_wanuthur_waqf', 'raa_yasr_waqf', 'salasila_waqf', 'tamanna_noon', 'yaa_aatani_waqf', 'yabsut', 'yalhath_dhalik', 'yaseen_wasl']
{'options': ['open', 'closed'], 'default': 'open'}
```

Every variant takes one scalar option name. A grouped variant applies at all
of its covered locations:

```python
closed = Phonemizer(variants={"iqlab_nasal": "closed"})

print(pm.phonemize("2:56:3-2:56:4").text())
print(" ".join(pm.phonemize("2:56:3-2:56:4").phonemes()))
print(" ".join(closed.phonemize("2:56:3-2:56:4").phonemes()))
```

```
مِّن بَعْدِ
m i ŋ b a ʕ d Q
m i m̃ b a ʕ d Q
```

The word-specific variants are scalar too. Their IDs name the covered form and
the junction restriction where one applies:

```python
heavy = Phonemizer(variants={"raa_yasr_waqf": "heavy"})

print(pm.phonemize("89:4").text())
print(" ".join(pm.phonemize("89:4").phonemes()))
print(" ".join(heavy.phonemize("89:4").phonemes()))
```

```
وَٱلَّيْلِ إِذَا يَسْرِ
w a ll a j l i ʔ i ð a: j a s r
w a ll a j l i ʔ i ð a: j a s rˤ
```

See [the variants catalogue](docs/variants.md) for all IDs, defaults,
locations, phoneme effects, and tajweed projections. The fixed Hafs imala
shown above is not a variant; its rendering is selected through the `imala`
extra phoneme.

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
