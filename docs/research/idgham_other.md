# Idgham

Analysis of non-noon/tanween idgham rules in Uthmanic Hafs v2.0 dataset. These are cases where a consonant letter is silent (or partially silent) because it assimilates into the following letter.

**Source:** `data/QS - QIRAAT/Uthmanic Hafs v2.0/UthmanicHafs_v2-0 data/hafsData_v2-0.json`

---

## Scope

This document covers four rule categories:

| # | Rule | Arabic | Description |
|---|------|--------|-------------|
| 1 | Lam Shamsiyah | لام شمسية | Lam of the definite article assimilates into a following "sun letter" |
| 2 | Idgham Mutaqaribayn | إدغام متقاربين | Letters from nearby articulation points — first assimilates into second |
| 3 | Idgham Mutamathilayn | إدغام متماثلين | Identical adjacent letters — first is silent, second is doubled |
| 4 | Idgham Mutajanisayn | إدغام متجانسين | Letters sharing the same articulation point — first assimilates into second |


## Detection

In the Uthmanic text, within-word idgham is identified by a bare letter (no combining diacritics) followed by a letter with shaddah (ّ). Cross-word idgham is identified by a word-final letter with sukun (ۡ) or bare, followed by a matching letter (typically with shaddah) at the start of the next word. For words ending in واْ (waw al-jama'a + silent alef), the effective final consonant is the و, not the alef.

Exception: Mutajanisayn Naqis (ط→ت) — the assimilation is incomplete, so the receiving letter does not carry shaddah.

## Functional Breakdown

| Rule | Within-word | Cross-word | Total | % |
|------|------------:|-----------:|------:|:---:|
| Lam Shamsiyah | 5,283 | 0 | 5,283 | 95.9% |
| Idgham Mutaqaribayn | 1 | 12 | 13 | 0.2% |
| Idgham Mutamathilayn | 4 | 144 | 148 | 2.7% |
| Idgham Mutajanisayn Kamil | 38 | 20 | 58 | 1.1% |
| Idgham Mutajanisayn Naqis | 4 | 0 | 4 | 0.1% |

---

## Lam Shamsiyah

The lam of the definite article (ال) is silent before any of the 14 sun letters (حروف شمسية): ت ث د ذ ر ز س ش ص ض ط ظ ل ن. The following letter carries shaddah.

### Total

| Metric | Value |
|--------|------:|
| Non-ل targets | 2,709 |
| ل (Allah) | 2,557 |
| ل (non-Allah) | 17 |
| **Total** | **5,283** |

### Prefixes

All 5,283 cases involve the definite article lam. The article appears after various attached prefixes:

| Prefix | Count | % | Examples |
|--------|------:|:---:|---------|
| ٱل (no prefix) | 4,436 | 84.0% | ٱللَّهِ (1:1), ٱلرَّحۡمَٰنِ (1:1), ٱلرَّحِيمِ (1:1) |
| وَٱل | 473 | 9.0% | وَٱللَّهُ (2:19), وَٱلسَّمَآءَ (2:22), وَٱلصَّلَوٰةِۚ (2:45) |
| بِٱل | 212 | 4.0% | بِٱللَّهِ (2:8), بِٱلصَّبۡرِ (2:45) |
| لِل / لِّل | 119 | 2.3% | لِلنَّاسِ (2:83), لِلظَّٰلِمِينَ (2:270), لِلرَّحۡمَٰنِ (19:26) |
| فَٱل | 12 | 0.2% | فَٱللَّهُ (2:113), فَٱلصَّٰلِحَٰتُ (4:34) |
| وَلِل | 8 | 0.2% | وَلِلرِّجَالِ (2:228), وَلِلنِّسَآءِ (4:7, 4:32), وَلِلسَّيَّارَةِۖ (5:96), وَلَلدَّارُ (6:32), وَلِلرَّسُولِ (8:24, 8:41, 59:7) |
| تَٱل | 8 | 0.2% | تَٱللَّهِ (12:73, 12:85, 12:91, 12:95, 16:56, 16:63, 26:97, 37:56) |
| كَٱل | 5 | 0.1% | كَٱلطَّوۡدِ (26:63), كَٱلظُّلَلِ (31:32), كَٱلرَّمِيمِ (51:42), كَٱلدِّهَانِ (55:37), كَٱلصَّرِيمِ (68:20) |
| ءَٱل | 4 | 0.1% | ءَآلذَّكَرَيۡنِ (6:143, 6:144), ءَآللَّهُ (10:59, 27:59) |
| وَبِٱل | 3 | 0.1% | وَبِٱلنَّجۡمِ (16:16), وَبِٱلرَّسُولِ (24:47), وَبِٱلزُّبُرِ (35:25) |
| فَلِل | 1 | 0.0% | فَلِلذَّكَرِ (4:176) |
| أَبِٱل | 1 | 0.0% | أَبِٱللَّهِ (9:65) |
| وَتَٱل | 1 | 0.0% | وَتَٱللَّهِ (21:57) |

The لِل / لِّل cases (119 + 8 وَلِل + 1 فَلِل = 128) drop the alef wasla entirely — the preposition لِ attaches directly to the article lam.

### By Target Shams Letter

| Letter | Count | % | Examples |
|--------|------:|:---:|---------|
| ل | 2,574 | 48.7% | ٱللَّهِ (1:1), ٱللَّطِيفُ (6:103) |
| ن | 617 | 11.7% | ٱلنَّاسِ (2:8), ٱلنَّارَ (2:24) |
| س | 589 | 11.1% | ٱلسُّفَهَآءُۗ (2:13), ٱلسَّمَآءِ (2:19) |
| ر | 312 | 5.9% | ٱلرَّحۡمَٰنِ (1:1), ٱلرَّحِيمِ (1:1) |
| ص | 298 | 5.6% | ٱلصِّرَٰطَ (1:6), ٱلصَّلَوٰةَ (2:3) |
| د | 215 | 4.1% | ٱلدِّينِ (1:4), ٱلدِّمَآءَ (2:30) |
| ش | 206 | 3.9% | ٱلشَّجَرَةَ (2:35), ٱلشَّيۡطَٰنُ (2:36) |
| ظ | 142 | 2.7% | ٱلظَّٰلِمِينَ (2:35), ٱلظُّلُمَٰتِ (2:257) |
| ط | 84 | 1.6% | ٱلطُّورَ (2:63), لِلطَّآئِفِينَ (2:125) |
| ت | 65 | 1.2% | ٱلتَّوَّابُ (2:37), ٱلتَّهۡلُكَةِ (2:195) |
| ز | 61 | 1.2% | ٱلزَّكَوٰةَ (2:43), ٱلزَّادِ (2:197) |
| ذ | 55 | 1.0% | ٱلذِّلَّةُ (2:61), ٱلذَّهَبِ (3:14) |
| ض | 40 | 0.8% | ٱلضَّآلِّينَ (1:7), ٱلضَّلَٰلَةَ (2:16) |
| ث | 25 | 0.5% | ٱلثَّمَرَٰتِ (2:22)|

Of the 2,574 ل→ل cases, 2,557 are Allah (ٱللَّه / ٱللَّهُمَّ) and 17 are other words: بِٱللَّغۡوِ (3), ٱللَّطِيفُ (2), ٱللَّعۡنَةُ (2), ٱللَّٰعِنُونَ, ٱللَّعۡنَةَ, ٱللَّٰعِبِينَ, ٱللَّغۡوِ, ٱللَّغۡوَ, ٱللَّٰتَ, ٱللَّمَمَ, ٱللُّؤۡلُؤُ, ٱللُّؤۡلُوِٕ, ٱللَّوَّامَةِ.

---

## Idgham Mutaqaribayn

Letters from nearby (not identical) articulation points. Only two pairs occur in the Quran.

| Scope | Count |
|-------|------:|
| Within-word | 1 |
| Cross-word | 12 |
| **Total** | **13** |

### ل→ر (12 cross-word, all with shaddah)

| Word pair | Ref |
|-----------|-----|
| بَل رَّفَعَهُ | 4:158 |
| بَل رَّبُّكُمۡ | 21:56 |
| قُل رَّبِّيٓ | 18:22, 28:85 |
| قُل رَّبِّ | 23:93 |
| وَقُل رَّبِّ | 17:24, 17:80, 20:114, 23:29, 23:97, 23:118 |
| فَقُل رَّبُّكُمۡ | 6:147 |

Note: بَلۡۜ رَانَ (83:14) is excluded — the ۜ (small high seen) marks a sakt (brief pause) in Hafs riwayah, which prevents the idgham from occurring.

### ق→ك

The only within-word case:

| Word | Ref |
|------|-----|
| نَخۡلُقكُّم | 77:20 |

---


## Idgham Mutamathilayn

Two identical adjacent letters where the first is silent and the second carries shaddah.

### Total

| Scope | Count | % |
|-------|------:|:---:|
| Within-word | 4 | 2.7% |
| Cross-word | 144 | 97.3% |
| **Total** | **148** | |

### Within-Word

Only 4 within-word cases exist in the entire Quran, all non-lam pairs.

| Pair | Count  | Examples |
|------|------|---------|
| ه→ه | 2  | يُوَجِّههُّ (16:76), يُكۡرِههُّنَّ (24:33) |
| ي→ي | 1  | بِأَييِّكُمُ (68:6) |
| ك→ك | 1  | يُدۡرِككُّمُ (4:78) |

Note: م→م and ن→ن are excluded — these fall under meem sakinah (idgham shafawi) and noon sakinah (idgham ghunnah) rules respectively.

### Cross-Word

Occurs when the last letter of a word matches the first letter of the next word. All cases have shaddah on the receiving letter.

| Pair | Count | % | Examples |
|------|------:|:---:|---------|
| ل→ل | 98 | 68.1% | أَقُل لَّكُمۡ (2:33), بَل لَّعَنَهُمُ (2:88) |
| و→و | 23 | 16.0% | عَصَواْ وَّكَانُواْ (2:61), أَو وَّزَنُوهُمۡ (83:3) |
| ت→ت | 8 | 5.6% | رَبِحَت تِّجَٰرَتُهُمۡ (2:16), طَلَعَت تَّزَٰوَرُ (18:17) |
| ب→ب | 7 | 4.9% | ٱضۡرِب بِّعَصَاكَ (2:60), وَلۡيَكۡتُب بَّيۡنَكُمۡ (2:282) |
| ر→ر | 3 | 2.1% | وَٱذۡكُر رَّبَّكَ (3:41, 7:205, 18:24) |
| ع→ع | 2 | 1.4% | تَسۡتَطِع عَّلَيۡهِ (18:78), تَسۡطِع عَّلَيۡهِ (18:82) |
| د→د | 1 | 0.7% | وَقَد دَّخَلُواْ (5:61) |
| ف→ف | 1 | 0.7% | يُسۡرِف فِّي (17:33) |
| ذ→ذ | 1 | 0.7% | إِذ ذَّهَبَ (21:87) |

22 of the 23 و→و cases follow the واْ وَّ pattern — waw al-jama'a followed by a silent alef, then a waw with shaddah at the start of the next word.

---

## Idgham Mutajanisayn

Letters from the same articulation point (مخرج). Two subtypes: Kamil (complete assimilation — first letter fully silent) and Naqis (incomplete — first letter partially preserved).

### Naqis (Incomplete)

Only the pair ط→ت. The ط retains its emphatic quality (tafkheem) and its base phoneme is partially preserved. The ت does **not** carry shaddah.

| Word | Ref |
|------|-----|
| بَسَطتَ | 5:28 |
| فَرَّطتُمۡ | 12:80 |
| أَحَطتُ | 27:22 |
| فَرَّطتُ | 39:56 |

### Kamil (Complete)

| Pair | Articulation | Within | Cross | Total | Examples |
|------|-------------|-------:|------:|------:|---------|
| ب→م | Labial (شفوية) | 0 | 1 | 1 | ٱرۡكَب مَّعَنَا (11:42) |
| ت→د | Tongue tip (طرف اللسان) | 0 | 2 | 2 | أَثۡقَلَت دَّعَوَا (7:189), أُجِيبَت دَّعۡوَتُكُمَا (10:89) |
| ت→ط | Tongue tip (طرف اللسان) | 0 | 7 | 7 | وَدَّت طَّآئِفَةٞ (3:69), وَقَالَت طَّآئِفَةٞ (3:72), (3:122)|
| ث→ذ | Tongue tip (طرف اللسان) | 0 | 1 | 1 | يَلۡهَثۚ ذَّٰلِكَ (7:176) |
| د→ت | Tongue tip (طرف اللسان) | 38 | 7 | 45 | أَرَدتُّمۡ (2:233), وَعَدتَّنَا (3:194)|
| ذ→ظ | Tongue tip (طرف اللسان) | 0 | 2 | 2 | إِذ ظَّلَمُوٓاْ (4:64), إِذ ظَّلَمۡتُمۡ (43:39) |
| **Total** |  | **38** | **20** | **58** |

The د→ت pair dominates (45/58 = 77.6%). All 38 within-word cases are د→ت, making it the only pair that occurs inside a single word token.

**Within-word د→ت — all 32 unique forms:**

| Root | Word | Count | Refs |
|------|------|------:|------|
| ر-ي-د | أَرَدتُّمۡ | 2 | 2:233, 20:86 |
| | أَرَدتُّمُ | 1 | 4:20 |
| | أَرَدتُّ | 1 | 11:34 |
| | فَأَرَدتُّ | 1 | 18:79 |
| و-ع-د | وَعَدتَّنَا | 1 | 3:194 |
| | تَوَاعَدتُّمۡ | 1 | 8:42 |
| | وَوَعَدتُّكُمۡ | 1 | 14:22 |
| | وَعَدتَّهُمۡ | 1 | 40:8 |
| و-ج-د | وَجَدتُّمُوهُمۡۖ | 1 | 4:89 |
| | وَجَدتُّم | 1 | 7:44 |
| | وَجَدتُّمُوهُمۡ | 1 | 9:5 |
| | وَجَدتُّ | 1 | 27:23 |
| | وَجَدتُّهَا | 1 | 27:24 |
| | وَجَدتُّمۡ | 1 | 43:24 |
| ع-ه-د | عَٰهَدتَّ | 1 | 8:56 |
| | عَٰهَدتُّمۡ | 4 | 9:1, 9:4, 9:7, 16:91 |
| ر-و-د | رَٰوَدتُّهُۥ | 2 | 12:32, 12:51 |
| | رَٰوَدتُّنَّ | 1 | 12:51 |
| ش-ه-د | أَشۡهَدتُّهُمۡ | 1 | 18:51 |
| | شَهِدتُّمۡ | 1 | 41:21 |
| ع-ب-د | عَبَّدتَّ | 1 | 26:22 |
| | عَبَدتُّمۡ | 1 | 109:4 |
| ع-ق-د | عَقَّدتُّمُ | 1 | 5:89 |
| أ-ي-د | أَيَّدتُّكَ | 1 | 5:110 |
| ط-ر-د | طَرَدتُّهُمۡۚ | 1 | 11:30 |
| ح-ص-د | حَصَدتُّمۡ | 1 | 12:47 |
| ص-د-د | صَدَدتُّمۡ | 1 | 16:94 |
| ع-و-د | عُدتُّمۡ | 1 | 17:8 |
| ك-ي-د | كِدتَّ | 2 | 17:74, 37:56 |
| ر-د-د | رُّدِدتُّ | 1 | 18:36 |
| و-ل-د | وُلِدتُّ | 1 | 19:33 |
| م-ه-د | وَمَهَّدتُّ | 1 | 74:14 |