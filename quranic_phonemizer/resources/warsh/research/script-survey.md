# Script/Fonts Comparison Matrix - Warsh Variants

| | **King Fahd warshData** | **Quranpedia warshData** |
|---|---|---|
| **Structural issues** | • None  | • Records are not in Qur'anic order - the `ayat` array is sorted by surah number as a string, not numerically<br>• `juz` field has a bug: 26 records have `juz: 0`<br>• A stray Arabic-Indic numeral is embedded mid-text, e.g. 16:123 |
| **Encoding issues** | • Every aya_text in the script ends with a non-breaking space <br> (U+00A0) followed by a character that looks like a random Arabic ligature, e.g. ﰀ, ﰅ, ﱺ. <br> They aren't real ligatures. They're a font-dependent hack for <br> the ayah-end number. We can get rid of them easily by running strip_flagged_chars.py.| • None |
| **Font 1 : uthmanic-warsh-V21.ttf** | MISSING UNICODES from font: 0 | MISSING UNICODES from font: 0 |
| **Font 2 : digital-khatt-v1.otf** | MISSING UNICODES from font: 6 | MISSING UNICODES from font: 5 |
| **Font 3 : digital-khatt-indopak.otf** | MISSING UNICODES from font: 7 | MISSING UNICODES from font: 6 |

## Selection

**Chosen script: King Fahd warshData.** It requires no restructuring, encoding issues are easy to fix, and the script is ready to use.

**Chosen font: uthmanic-warsh-V21.ttf.** It renders all the Unicode codepoints required by the King Fahd warshData script, and is purpose-built for Warsh script data.