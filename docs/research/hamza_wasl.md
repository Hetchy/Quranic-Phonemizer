# Hamza Wasl (ٱ)

Analysis of hamza wasl in Uthmanic Hafs v2.0 dataset.

**Source:** `data/QS - QIRAAT/Uthmanic Hafs v2.0/UthmanicHafs_v2-0 data/hafsData_v2-0.json`

---

## Encoding

- Encoded as **U+0671**, distinct from regular Alef (U+0627)
- Carries no combining diacritics in this dataset

## Total Occurrences

| Metric | Value |
|--------|------:|
| Total occurrences | 13,483 |
| Words containing it | 13,482 |
| Unique word forms | 3,416 |
| Ayas containing it | 4,798 / 6,236 (76.9%) |
| Present in every surah | Yes |

Note 49:11 ٱلِٱسۡمُ is the only word with two instances —  بِئۡسَ ٱلِٱسۡمُ ٱلۡفُسُوقُ                             

## Functional Breakdown

| Function | Count | % |
|----------|------:|:---:|
| Definite article (ٱل) | 11,995 | 89.0% |
| Non-article (verb/noun) | 1,487 | 11.0% |

## Position in Word

| Position | Count | % |
|----------|------:|:---:|
| First character of word token | 10,772 | 79.9% |
| Non-first character (after prefix) | 2,710 | 20.1% |

The 2,710 non-first cases are words where ٱ follows an attached prefix (e.g. وَٱلَّذِينَ, بِٱللَّهِ, فَٱتَّقُواْ).

## Pronounced

Only applies when ٱ is the first character of a word token (10,772 occurrences).

| Rule | Vowel | Condition | Count | % | Examples |
|------|-------|-----------|------:|:---:|---------|
| A | Fatha | ٱل (nouns) | 9,998 | 92.8% | ٱللَّهِ (1:1), ٱلرَّحۡمَٰنِ (1:1) |
| B | Kasra | 3rd letter has fatha or kasra | 504 | 4.7% | ٱهۡدِنَا (1:6), ٱشۡتَرَوُاْ (2:16), ٱسۡتَوۡقَدَ (2:17) |
| C | Damma | 3rd letter has damma | 151 | 1.4% | ٱعۡبُدُواْ (2:21), ٱسۡجُدُواْ (2:34), ٱسۡكُنۡ (2:35) |

### Special Cases

All follow **Rule B (kasra)**.

**Nouns (99):**

| Word | Count | Examples |
|------|------:|---------|
| ٱسم | 19 | ٱسۡمَ (5:4), ٱسۡمُهُۥ (2:114) |
| ٱمرؤ | 6 | ٱمۡرُؤٌاْ (4:176), ٱمۡرِيٕٖ (24:11) |
| ٱمرأة | 20 | ٱمۡرَأَتُ (3:35), ٱمۡرَأَتَهُۥ (7:83), ٱمۡرَأَتَيۡنِ (28:23) |
| ٱبن | 32 | ٱبۡنَ (2:87), ٱبۡنَهُۥ (11:42), ٱبۡنَكَ (12:81) |
| ٱبنة | 2 | ٱبۡنَتَيَّ (28:27), ٱبۡنَتَ (66:12) |
| ٱثنان | 13 | ٱثۡنَيۡنِ (6:143), ٱثۡنَانِ (5:106), ٱثۡنَا (9:36) |
| ٱثنتان | 7 | ٱثۡنَتَا (2:60), ٱثۡنَتَيۡنِ (4:11), ٱثۡنَتَيۡ (7:160) |

**Verbs (18):**

| Word | Count | Examples |
|------|------:|---------|
| ٱئتوا | 14 | ٱئۡتُونِي (10:79), ٱئۡتِنَا (7:77), ٱئۡتِيَا (41:11) |
| ٱبنوا | 2 | ٱبۡنُواْ (18:21, 37:97) |
| ٱقضوا | 1 | ٱقۡضُوٓاْ (10:71) |
| ٱمشوا | 1 | ٱمۡشُواْ (38:6) |

**Other (2):**

| Word | Ref | Note |
|------|-----|------|
| ٱدَّارَكُواْ | 7:38 | 3rd letter is alef  |
| ٱثَّاقَلۡتُمۡ | 9:38 | 3rd letter is alef |

## Silent

Applies to all other cases — when ٱ is not the start of recitation. The hamza is dropped and the preceding word connects directly to what follows.

| Context | Count | % | Examples |
|---------|------:|:---:|---------|
| First char, non-first word in recitation (conditionally silent) | 10,545 | 79.6% | ٱللَّهِ, ٱلَّذِينَ, ٱتَّقُواْ |
| Non-first char (after prefix, always silent) | 2,710 | 20.4% | وَٱللَّهُ, بِٱللَّهِ, فَٱتَّقُواْ |
| **Total silent** | **13,255** | **98.3%** | |

Only 227 occurrences (1.7%) are first-char of the first word in an aya.

### Prefixes

The 2,710 prefixed cases attach these particles before ٱ:

| Prefix | Count | % | Examples |
|--------|------:|:---:|---------|
| وَ | 1,666 | 61.44% | وَٱلَّذِينَ (2:4), وَٱللَّهُ (2:19), وَّٱلَّذِينَ (16:128) |
| بِ  | 601 | 22.18% | بِٱلۡغَيۡبِ (2:3), بِٱللَّهِ (2:8), بِٱلۡهُدَىٰ (2:16) |
| فَ  | 354 | 13.06% | فَٱتَّقُواْ (2:24), فَٱرۡهَبُونِ (2:40), فَٱتَّقُونِ (2:41) |
| كَ  | 42 | 1.55% | كَٱلۡحِجَارَةِ (2:74), كَٱلَّذِي (2:259), كَٱلۡأُنثَىٰۖ (3:36) |
| وَبِ | 16 | 0.59% | وَبِٱلۡأٓخِرَةِ (2:4), وَبِٱلۡيَوۡمِ (2:8), وَبِٱلۡوَٰلِدَيۡنِ (2:83) |
| لَ | 15 | 0.55% | لَٱنفَضُّواْ (3:159), لَّٱتَّبَعۡنَٰكُمۡۗ (3:167), لَٱسۡتَكۡثَرۡتُ (7:188) |
| تَ / وَتَ  | 9 | 0.33% | تَٱللَّهِ (12:73), وَتَٱللَّهِ (21:57) |
| لِ  | 2 | 0.07% | لِٱمۡرَأَتِهِۦٓ (12:21), لِٱبۡنِهِۦ (31:13) |
| أَفَبِ | 2 | 0.07% | أَفَبِٱلۡبَٰطِلِ (16:72,29:67) |
| أَفَ | 1 | 0.04% | أَفَٱتَّخَذۡتُم (13:16) |
| أَبِ | 1 | 0.04% | أَبِٱللَّهِ (9:65) |
| لَبِ | 1 | 0.04% | لَبِٱلۡمِرۡصَادِ (89:14) |

### Iltiqaa Sakinayn

Cross-word cases where ٱ is the first character of the next word token. Includes 10,545 within-aya cases and 216 cross-aya cases (10,761 total). In addition to the hamza wasl being silent, the pronunciation across the two words is modified. There are two subcases:

| Ending type | Within | Cross | Total | % |
|-------------|-------:|------:|------:|:---:|
| Other (no iltiqaa) | 7,782 | 144 | 7,926 | 73.7% |
| Long vowel | 2,717 | 13 | 2,730 | 25.4% |
| Tanween | 46 | 59 | 105 | 1.0% |

#### Tanween (105 cases)

An implicit kasra sound is added after the tanween. All cases are closed tanween.

| Tanween | Within | Cross | Total | Within examples | Cross examples |
|---------|-------:|------:|------:|-----------------|----------------|
| Kasratan | 21 | 16 | 37 | بَعۡضٍۗ ٱنظُرۡ (6:65), يَوۡمَئِذٍ ٱلۡحَقُّ (7:8) | نَصِيرٍ ٱلَّذِينَ (2:120-121), هَادٍ ٱللَّهُ (13:7-8) |
| Fathatan (with alef seat) | 10 | 23 | 33 | خَيۡرًا ٱلۡوَصِيَّةُ (2:180), مَثَلًا ٱلۡقَوۡمُ (7:177) | شَهِيدًا ٱلرِّجَالُ (4:33-34), فَتِيلًا ٱنظُرۡ (4:49-50) |
| Dammatan | 12 | 20 | 32 | خَيۡرٌۚ ٱهۡبِطُواْ (2:61), ثَلَٰثَةٌۚ ٱنتَهُواْ (4:171) | حَكِيمٌ ٱلطَّلَٰقُ (2:228-229), عَلِيمٌ ٱللَّهُ (2:256-257) |
| Fathatan (direct) | 3 | 0 | 3 | جَزَآءً ٱلۡحُسۡنَىٰ (18:88), سَوَآءً ٱلۡعَٰكِفُ (22:25) | — |

#### Long Vowel (2,730 cases)

The long vowel is shortened — only the short diacritic sound remains. Waw/yaa only count as long vowels when bare (no diacritics).

| Vowel ending | Within | Cross | Total | Within examples | Cross examples |
|--------------|-------:|------:|------:|-----------------|----------------|
| Alef (ا) | 822 | 0 | 822 | ٱهۡدِنَا ٱلصِّرَٰطَ (1:6), وَلَا ٱلضَّآلِّينَ (1:7) | — |
| Yaa (ي) | 765 | 3 | 768 | فِي ٱلۡأَرۡضِ (2:11), ٱلَّذِي ٱسۡتَوۡقَدَ (2:17) | أَخِي ٱشۡدُدۡ (20:30-31), لِنَفۡسِي ٱذۡهَبۡ (20:41-42) |
| Alef Maqsura (ى) | 569 | 10 | 579 | عَلَى ٱللَّهِ (3:122), إِلَى ٱلَّذِينَ (4:58) | ٱلۡعُلَى ٱلرَّحۡمَٰنُ (20:4-5), ٱلۡكُبۡرَى ٱذۡهَبۡ (20:23-24) |
| Waw + Silent Alef (واْ) | 543 | 0 | 543 | قَالُواْ ٱدۡعُ (2:68), فَٱتَّقُواْ ٱلنَّارَ (2:24) | — |
| Waw (و) | 18 | 0 | 18 | ذُو ٱلۡفَضۡلِ (2:105), ذُو ٱنتِقَامٍ (3:4) | — |

Note: Words ending in alef maqsura (ى) normally carry dagger alef (ىٰ) in this dataset, but the dagger is consistently stripped when followed by ٱ. This encoding reflects the shortened vowel.
