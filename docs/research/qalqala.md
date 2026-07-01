# Qalqala

Analysis of qalqala rules in Uthmanic Hafs v2.0 dataset. Qalqala (قلقلة) is the echoing/bouncing articulation that occurs when one of five specific letters is sakin (vowelless).

**Source:** `data/QS - QIRAAT/Uthmanic Hafs v2.0/UthmanicHafs_v2-0 data/hafsData_v2-0.json`

---

## Scope

The five qalqala letters (حروف القلقلة) are: **ق ط ب ج د** — mnemonic: **قُطْب جَدّ**.

### Tajweed classification

| Level | Arabic | Condition | Strength |
|-------|--------|-----------|----------|
| Sughra | صغرى | Mid-word sakin (sukun) | Lightest |
| Kubra | كبرى | End-of-word sakin (when pausing) | Moderate |
| Akbar | أكبر | End-of-word shaddah (when pausing) | Strongest |

## Detection

In the Uthmanic text, a qalqala letter is sakin when it carries sukun (ۡ) or is bare (no combining diacritics). End-of-word shaddah (ّ) counts because when pausing, the haraka drops and both components of the doubled letter become sakin. Mid-word shaddah does **not** count — the haraka is pronounced, so the letter is not truly sakin.

### Exclusions

The following bare-letter patterns are excluded because they represent other rules, not qalqala:

| Exclusion | Count | Reason |
|-----------|------:|--------|
| Idgham Mutajanisayn Kamil د→ت (within-word) | 38 | Covered under idgham — dal assimilates into ta |
| Idgham Mutajanisayn Naqis ط→ت (within-word) | 4 | Covered under idgham — partial assimilation |
| Idgham Mutaqaribayn ق→ك (within-word) | 1 | Covered under idgham — qaf assimilates into kaf |
| Cross-word idgham (end-of-word bare + next word shaddah) | 16 | Covered under idgham — assimilation across word boundary |
| Huruf Muqatta'at (isolated letters) | 6 | طه, طسٓمٓ, طسٓ, عٓسٓقٓ, قٓ — pronounced with long vowels, not sakin |

Two bare cases (فَٱرۡغَب 94:8, وَٱقۡتَرِب۩ 96:19) are included — they are end-word in a surah where the sukun mark is omitted due to assimilation with basmala, but when stopping they represent the sukun and Qalqala.

### Special inclusions — Huruf Muqatta'at صٓ

The letter صٓ in muqatta'at is pronounced "صَادْ" — the final دْ is sakin, producing qalqala kubra on the dal. These 3 cases are counted under **د end-word sukun**:

| Text | Location | Pronunciation |
|------|----------|---------------|
| الٓمٓصٓ | 7:1 | ألف لام ميم **صَادْ** |
| كٓهيعٓصٓ | 19:1 | كاف ها يا عين **صَادْ** |
| صٓ | 38:1 | **صَادْ** |

---

## Functional Breakdown

| Letter | Sughra (mid sukun) | Kubra (end sukun) | Akbar (end shaddah) | Total | % |
|--------|-------------------:|------------------:|--------------------:|------:|:---:|
| ق | 508 | 8 | 262 | 778 | 19.4% |
| ط | 134 | 8 | 0 | 142 | 3.5% |
| ب | 1,093 | 43 | 212 | 1,348 | 33.7% |
| ج | 645 | 13 | 14 | 672 | 16.8% |
| د | 543 | 425 | 94 | 1,062 | 26.5% |
| **Total** | **2,923** | **497** | **582** | **4,002** | |

### By level

| Level | Count | % |
|-------|------:|:---:|
| Sughra (mid-word sukun) | 2,923 | 73.0% |
| Kubra (end-word sukun) | 497 | 12.4% |
| Akbar (end-word shaddah) | 582 | 14.5% |

---

## ق (Qaf) — 778

### Mid-word sukun — 508

| Examples | Ref |
|----------|-----|
| رَزَقۡنَٰهُمۡ | 2:3 |
| وَيَقۡطَعُونَ | 2:27 |
| تَقۡرَبَا | 2:35 |
| يُقۡبَلُ | 2:48 |
| خَلَقۡنَا | 15:26 |

Top forms: خَلَقۡنَا (×18), رَزَقۡنَٰهُمۡ (×9), أَقۡرَبُ (×8), أُقۡسِمُ (×8), خَلَقۡنَٰكُمۡ (×6).

### End-word sukun — 8

All 8 unique forms (each ×1):

| Word | Ref |
|------|-----|
| وَٱرۡزُقۡ | 2:126 |
| فَٱفۡرُقۡ | 5:25 |
| يَسۡرِقۡ | 12:77 |
| وَتَصَدَّقۡ | 12:88 |
| ذُقۡ | 44:49 |
| لِيُنفِقۡ | 65:7 |
| فَلۡيُنفِقۡ | 65:7 |
| يُخۡلَقۡ | 89:8 |

### End-word shaddah — 262

Dominated by derivatives of حَقّ (the truth/right):

| Word | Count | Examples |
|------|------:|---------|
| بِٱلۡحَقِّ | 47 | 2:119, 2:213, 3:3 |
| ٱلۡحَقُّ | 37 | 2:26, 2:91, 2:144 |
| ٱلۡحَقِّ | 26 | 2:213, 3:154, 5:77 |
| ٱلۡحَقَّ | 18 | 2:42, 2:146, 3:60 |
| حَقَّ | 14 | 2:121, 3:102, 6:91 |
| بِٱلۡحَقِّۚ | 12 | 2:71, 2:252, 6:30 |
| بِٱلۡحَقِّۖ | 10 | 6:73, 6:114, 7:43 |
| أَحَقُّ | 9 | 2:228, 2:247, 5:107 |
| حَقّٞ | 9 | 3:86, 10:55, 18:21 |

50 unique forms in total.

---

## ط (Ta) — 142

### Mid-word sukun — 134

| Examples | Ref |
|----------|-----|
| أَفَتَطۡمَعُونَ | 2:75 |
| شَطۡرَ | 2:144 |
| يَطۡهُرۡنَۖ | 2:222 |
| نُّطۡفَةٖ | 16:4 |
| يَطۡبَعُ | 7:101 |

Top forms: نُّطۡفَةٖ (×6), شَطۡرَ (×3), يَطۡبَعُ (×3), نُّطۡفَةٍ (×3).

### End-word sukun — 8

7 unique forms:

| Word | Count | Ref |
|------|------:|-----|
| تُحِطۡ | 2 | 18:68, 27:22 |
| فَٱهۡبِطۡ | 1 | 7:13 |
| ٱهۡبِطۡ | 1 | 11:48 |
| تُسَٰقِطۡ | 1 | 19:25 |
| فَأَسۡقِطۡ | 1 | 26:187 |
| نُسۡقِطۡ | 1 | 34:9 |
| تُشۡطِطۡ | 1 | 38:22 |

### End-word shaddah — 0

No cases in the Quran. The letter ط never appears with shaddah at the end of a word, making it the only qalqala letter without akbar.

---

## ب (Ba) — 1,348

### Mid-word sukun — 1,093

| Examples | Ref |
|----------|-----|
| قَبۡلِكَ | 2:4 |
| أَبۡصَٰرِهِمۡ | 2:7 |
| يُبۡصِرُونَ | 2:17 |
| قَبۡلُ | 2:89 |
| إِبۡرَٰهِيمَ | 3:33 |

Top forms: قَبۡلُ (×45), إِبۡرَٰهِيمَ (×35), قَبۡلِ (×25), قَبۡلِكَ (×24), سُبۡحَٰنَ (×19).

### End-word sukun — 43

30 unique forms. Top forms:

| Word | Count | Refs |
|------|------:|------|
| هَبۡ | 4 | 3:38, 25:74, 26:83, 37:100 |
| ٱذۡهَبۡ | 4 | 17:63, 20:24, 20:42, 79:17 |
| وَهَبۡ | 2 | 3:8, 38:35 |
| يَنقَلِبۡ | 2 | 3:144, 67:4 |
| يَكۡسِبۡ | 2 | 4:111, 4:112 |
| فَٱذۡهَبۡ | 2 | 5:24, 20:97 |
| وَٱضۡرِبۡ | 2 | 18:45, 36:13 |
| فَٱرۡتَقِبۡ | 2 | 44:10, 44:59 |

Plus 22 forms appearing once each, including وَتُبۡ (2:128), فَلۡيَكۡتُبۡ (2:282), فَٱنصَبۡ (94:7), فَٱرۡغَب (94:8), وَٱقۡتَرِب۩ (96:19).

### End-word shaddah — 212

36 unique forms. Top forms:

| Word | Count | Examples |
|------|------:|---------|
| رَبِّ | 80 | 1:2, 2:126, 2:260 |
| يُحِبُّ | 39 | 2:190, 2:195, 2:205 |
| رَبُّ | 18 | 6:164, 7:54, 9:129 |
| رَّبِّ | 18 | 7:61, 7:67, 7:104 |
| بِرَبِّ | 8 | 7:121, 20:70, 26:47 |
| رَبَّ | 5 | 5:28, 26:77, 27:91 |
| رَّبُّ | 5 | 13:16, 19:65, 23:86 |
| وَرَبُّ | 5 | 23:86, 26:26, 37:5 |

---

## ج (Jim) — 672

### Mid-word sukun — 645

| Examples | Ref |
|----------|-----|
| يَجۡعَلُونَ | 2:19 |
| تَجۡرِي | 2:25 |
| أَتَجۡعَلُ | 2:30 |
| تَجۡزِي | 2:48 |
| أَجۡمَعِينَ | 2:161 |

Top forms: تَجۡرِي (×48), أَجۡمَعِينَ (×23), نَجۡزِي (×19), ٱلۡمُجۡرِمِينَ (×18), أَجۡرًا (×13).

### End-word sukun — 13

7 unique forms:

| Word | Count | Refs |
|------|------:|------|
| فَٱخۡرُجۡ | 4 | 7:13, 15:34, 28:20, 38:77 |
| تَخۡرُجۡ | 3 | 20:22, 27:12, 28:32 |
| ٱخۡرُجۡ | 2 | 7:18, 12:31 |
| يُخۡرِجۡ | 1 | 2:61 |
| يَخۡرُجۡ | 1 | 4:100 |
| أَخۡرِجۡ | 1 | 14:5 |
| وَيُخۡرِجۡ | 1 | 47:37 |

### End-word shaddah — 14

11 unique forms, all related to حَجّ (pilgrimage):

| Word | Count | Refs |
|------|------:|------|
| ٱلۡحَجِّ | 3 | 2:196, 2:196, 9:3 |
| ٱلۡحَجَّ | 2 | 2:196, 2:197 |
| حَجَّ | 1 | 2:158 |
| وَٱلۡحَجِّۗ | 1 | 2:189 |
| ٱلۡحَجُّ | 1 | 2:197 |
| ٱلۡحَجِّۗ | 1 | 2:197 |
| حَآجَّ | 1 | 2:258 |
| حِجُّ | 1 | 3:97 |
| ٱلۡحَآجِّ | 1 | 9:19 |
| بِٱلۡحَجِّ | 1 | 22:27 |
| فَجٍّ | 1 | 22:27 |

---

## د (Dal) — 1,062

### Mid-word sukun — 543

| Examples | Ref |
|----------|-----|
| وَٱدۡعُواْ | 2:23 |
| عَدۡلٞ | 2:48 |
| وَٰعَدۡنَا | 2:51 |
| ٱدۡخُلُواْ | 2:58 |
| يَدۡعُونَ | 2:221 |

Top forms: يَدۡعُونَ (×23), تَدۡعُونَ (×16), أَدۡرَىٰكَ (×13), ٱدۡخُلُواْ (×11).

### End-word sukun — 425

The largest end-word sukun category of any letter, dominated by the particle قَدۡ and its prefixed forms.

38 unique forms plus 3 special muqatta'at صاد cases (see [Special inclusions](#special-inclusions--huruf-muqattaʼat-صٓ)). Top forms:

| Word | Count | Examples |
|------|------:|---------|
| قَدۡ | 118 | 2:60, 2:118, 2:134 |
| وَلَقَدۡ | 115 | 2:65, 2:87, 2:99 |
| فَقَدۡ | 50 | 2:108, 2:231, 2:269 |
| وَقَدۡ | 40 | 2:75, 2:237, 2:246 |
| لَقَدۡ | 35 | 3:164, 5:70, 5:72 |
| لَّقَدۡ | 13 | 3:181, 5:17, 5:73 |
| يَجِدۡ | 7 | 2:196, 4:92, 4:100 |
| يُرِدۡ | 5 | 3:145, 6:125, 22:25 |

The قَدۡ family alone (قَدۡ, وَلَقَدۡ, فَقَدۡ, وَقَدۡ, لَقَدۡ, لَّقَدۡ) accounts for 371 of 425 cases (87.3%).

### End-word shaddah — 94

38 unique forms. Top forms:

| Word | Count | Examples |
|------|------:|---------|
| أَشَدُّ | 18 | 2:74, 2:165, 2:191 |
| أَشَدَّ | 9 | 2:200, 4:77, 5:82 |
| وَأَعَدَّ | 7 | 4:93, 9:100, 33:8 |
| أَعَدَّ | 7 | 4:102, 9:89, 33:29 |
| يُرَدُّ | 6 | 6:147, 12:110, 16:70 |
| يَوَدُّ | 5 | 2:96, 2:105, 4:42 |
| قُدَّ | 3 | 12:26, 12:27, 12:28 |
| مَرَدَّ | 3 | 13:11, 30:43, 42:47 |

---

## Notable Patterns

### Letter frequency

ب accounts for 33.7% of all qalqala, driven by the high sughra count from قَبۡل and إِبۡرَٰهِيم derivatives, plus end-word akbar from رَبّ (Lord) inflections.

### Level distribution by letter

| Letter | % Sughra | % Kubra | % Akbar | Pattern |
|--------|--------:|--------:|--------:|---------|
| ق | 65.3% | 1.0% | 33.7% | High akbar (حقّ family) |
| ط | 94.4% | 5.6% | 0.0% | Almost entirely sughra; no akbar |
| ب | 81.1% | 3.2% | 15.7% | Sughra-dominant |
| ج | 96.0% | 1.9% | 2.1% | Almost entirely sughra |
| د | 51.1% | 40.0% | 8.9% | Highest kubra rate (قدۡ family) |

### قَدۡ dominance in kubra dal

The particle قَدۡ and its prefixed variants (وَلَقَدۡ, فَقَدۡ, وَقَدۡ, لَقَدۡ, لَّقَدۡ) account for 371 of 425 kubra dal cases (87.3%), and 371 of 497 total kubra cases across all letters (74.6%).
