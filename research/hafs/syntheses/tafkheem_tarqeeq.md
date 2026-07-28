# Tafkheem & Tarqeeq (Hafs Riwayah)

Analysis of tafkheem (heaviness) and tarqeeq (lightness) rules in Uthmanic Hafs v2.0 dataset.

**Source:** `data/QS - QIRAAT/Uthmanic Hafs v2.0/hafsData_v2-0.json`

---

## 0. Overview (نظرة عامة)

Every Arabic letter is either always heavy (mufakham), always light (muraqqaq), or conditional.

**Always heavy — 7 istilaa letters (حروف الاستعلاء):**

| Letter | Name |
|--------|------|
| خ | Khaa |
| ص | Sad |
| ض | Dad |
| غ | Ghayn |
| ط | Taa |
| ق | Qaf |
| ظ | Dhaa |

**Conditional — 3 letters:**

| Letter | Name | Condition |
|--------|------|-----------|
| ل | Lam | Heavy only in لفظ الجلالة (Allah words) when preceded by fatha or damma (section 1) |
| ر | Raa | Heavy or light depending on its own haraka and surrounding context (section 2) |
| ا | Alef | Takes the quality of the preceding consonant (section 3) |

**Always light — all remaining letters** (21 letters). These are never pronounced with tafkheem.

---

## 1. Lam of Lafz al-Jalalah (لام لفظ الجلالة)

The Lam in the name of Allah is pronounced heavy (mufakhkhamah) when preceded by fatha or damma, and light (muraqqaqah) when preceded by kasra.

**Total occurrences: 2,704**

### Word Patterns

12 word forms contain Lafz al-Jalalah. They split into three groups based on whether the haraka preceding the Lam with Shaddah is fixed or context-dependent.

#### A. Always Mufakham (preceded by Fatha) — 257

| # | Pattern | Count | Preceding Haraka |
|---|---------|------:|------------------|
| 1 | ءَآللَّهُ | 2 | Fatha on Hamza |
| 2 | وَٱللَّهُ | 240 | Fatha on Waw |
| 3 | فَٱللَّهُ | 6 | Fatha on Faa |
| 4 | تَٱللَّهِ | 8 | Fatha on Taa |
| 5 | وَتَٱللَّهِ | 1 | Fatha on Taa |

#### B. Always Muraqqaq (preceded by Kasra) — 289

| # | Pattern | Count | Preceding Haraka |
|---|---------|------:|------------------|
| 1 | لِلَّهِ | 116 | Kasra on first Lam |
| 2 | وَلِلَّهِ | 27 | Kasra on first Lam |
| 3 | فَلِلَّهِ | 6 | Kasra on first Lam |
| 4 | بِٱللَّهِ | 139 | Kasra on Ba |
| 5 | أَبِٱللَّهِ | 1 | Kasra on Ba |

#### C. Context-Dependent (starts with Hamza Wasl) — 2,158

These start with Hamza Wasl (ٱ), so the preceding haraka comes from the previous word. At ayah start, the implicit preceding haraka is fatha.

| # | Pattern | Count | After Fatha | After Damma | After Kasra |
|---|---------|------:|------------:|------------:|------------:|
| 1 | ٱللَّه | 2,153 | 1,291 | 439 | 423 |
| 2 | ٱللَّهُمَّ | 5 | 2 | 1 | 2 |
| | **Subtotal** | **2,158** | **1,293** | **440** | **425** |

##### ٱللَّه examples

| Ref | Preceding Word | Haraka | Ruling |
|-----|---------------|--------|--------|
| 2:7 | خَتَمَ | Fatha | Mufakham |
| 2:9 | يُخَٰدِعُونَ | Fatha | Mufakham |
| 2:10 | فَزَادَهُمُ | Damma | Mufakham |
| 2:64 | فَضۡلُ | Damma | Mufakham |
| 1:1 | بِسۡمِ | Kasra | Muraqqaq |
| 2:23 | دُونِ | Kasra | Muraqqaq |

##### ٱللَّهُمَّ — all 5 occurrences

| Ref | Preceding Word | Haraka | Ruling |
|-----|---------------|--------|--------|
| 3:26 | قُلِ | Kasra | Muraqqaq |
| 5:114 | مَرۡيَمَ | Fatha | Mufakham |
| 8:32 | قَالُواْ | Damma | Mufakham |
| 10:10 | سُبۡحَٰنَكَ | Fatha | Mufakham |
| 39:46 | قُلِ | Kasra | Muraqqaq |

##### Special Cases: Iltiqaa Kasra (2 occurrences)

When the preceding word ends in tanween fath and connects to Hamza Wasl, the iltiqaa (junction) rule produces an implicit kasra. This overrides the fathatan, making the Lam muraqqaqah.

| Ref | Preceding Word | Written Haraka | Effective Haraka | Ruling |
|-----|---------------|----------------|-----------------|--------|
| 7:164 | قَوۡمًا | Fathatan | Iltiqaa Kasra | Muraqqaq |
| 11:31 | خَيۡرًاۖ | Fathatan | Iltiqaa Kasra | Muraqqaq |

These are counted under "After Kasra" in the table above (effective haraka from iltiqaa).

### Note

Context-dependent patterns are analysed assuming continuous reading (wasl) for the entire verse. Stop signs within the verse are not considered. The only exception is the first word of an ayah, where the implicit preceding haraka is fatha.

### Summary

| Source | Mufakham | Muraqqaq | Total |
|--------|--------:|---------:|------:|
| Group A (always mufakham) | 257 | — | 257 |
| Group B (always muraqqaq) | — | 289 | 289 |
| Group C  | 1,733 | 425 | 2,158 |
| **Total** | **1,990 (73.6%)** | **714 (26.4%)** | **2,704** |

---

## 2. Raa Mufakhkhamah & Muraqqaqah (راء مفخمة ومرققة)

The letter Raa (ر) is pronounced heavy (mufakhkhamah) or light (muraqqaqah) based on the diacritic on the Raa itself and, when sakinah, on the surrounding context.

**Important:** When Raa is the last letter of a verse, the reader stops (waqf) and the written haraka drops — Raa becomes sakinah and must be classified by the sukun context rules, not the written diacritic.

**Total Raa occurrences: 12,403**

### Decision Tree

```
Raa
├── End of verse (waqf)?
│   ├── Fathatan → pronounced with fatha + alif (stays heavy)
│   └── Any other haraka → drops, treat as sakinah ↓
│
├── Fatha / Fathatan / Damma / Dammatan  →  Heavy
├── Kasra / Kasratan                      →  Light
├── Sakinah (sukun, explicit or waqf-induced):
│   ├── prev letter = hamza wasl (ٱ)? → skip (silent in wasl)
│   │   ├── start of ayah (no prev letter)                 →  Heavy (always)
│   │   └── otherwise: use letter before ٱ ↓
│   ├── prev letter has no haraka (madd letter):
│   │   ├── alif / waw                                     →  Heavy
│   │   └── yaa / alif maqsura                             →  Light
│   ├── prev letter = yaa with sukun (leen yaa)            →  Light
│   ├── prev haraka = Fatha / Damma                        →  Heavy
│   ├── prev haraka = Kasra
│   │   ├── next letter = mofakham (same word)             →  Heavy
│   │   └── otherwise                                      →  Light
│   └── prev also sukun
│       ├── prev-prev = madd alif/waw (no haraka)          →  Heavy
│       ├── prev-prev yaa with no haraka / sukun           →  Light
│       ├── prev-prev haraka = Fatha / Damma               →  Heavy
│       └── prev-prev haraka = Kasra                       →  Light
└── No diacritic (huruf muqattaah / idgham)                →  Special (10)
```


### Summary

| Classification | Count | % |
|----------------|------:|----:|
| Mufakhkhamah (heavy) | 9,608 | 77.5 |
| Muraqqaqah (light) | 2,785 | 22.5 |
| Special (no diacritic) | 10 | 0.1 |
| **Total** | **12,403** | **100.0** |

### A. Heavy Raa (مفخمة) — 9,608

| # | Rule | Condition | Count | % | Examples |
|---|------|-----------|------:|----:|----------|
| 1 | Direct Fatha | رَ | 4,775 | 49.7 | ٱلرَّحۡمَٰنِ, رَبِّ, رَسُولُ |
| 2 | Direct Damma | رُ | 2,120 | 22.1 | كَفَرُواْ, يَشۡعُرُونَ, رُسُلِنَا |
| 3 | Sakinah after Fatha | ـَرۡ | 1,205 | 12.5 | ٱلۡأَرۡضِ, فَٱرۡهَبُونِ, وَٱرۡكَعُواْ |
| 4 | Direct Fathatan | رًا | 591 | 6.2 | نَارٗا, كَثِيرٗا, خَيۡرًا |
| 5 | Sakinah after Damma | ـُرۡ | 353 | 3.7 | تُرۡجَعُونَ, ٱلۡفُرۡقَانَ, وَٱرۡزُقۡ |
| 6 | Direct Dammatan | رٌ | 320 | 3.3 | مُسۡتَقَرّٞ, خَيۡرٞ, قَدِيرٞ |
| 7 | Waqf: after long alif/waw | ـارِ → ـارْ | 137 | 1.4 | ٱلنَّارِ, ٱلصُّدُورِ, ٱلۡأُمُورِ |
| 8 | Waqf: after Fatha | ـَرِ → ـَرْ | 62 | 0.6 | ٱلۡأَبۡصَٰرِ, ٱلۡقَهَّٰرُ, وَٱلۡإِبۡكَٰرِ |
| 9 | Waqf: after Damma | ـُرِ → ـُرْ | 20 | 0.2 | ٱلنُّذُرُ, نُّكُرٍ, وَدُسُرٖ |
| 10 | Waqf: sukun-sukun, prev2 Fatha | ـَXرِ → ـَXرْ | 12 | 0.1 | ٱلۡقَدۡرِ, وَٱلۡفَجۡرِ, عَشۡرٖ |
| 11 | Sakinah after Kasra + next mofakham | ـِرۡ + خصضغطقظ | 6 | 0.1 | قِرۡطَاسٖ, فِرۡقَةٖ, مِرۡصَادٗا |
| 12 | Hamza wasl at start of ayah | ٱرۡ (first word) | 4 | 0.0 | ٱرۡجِعُوٓاْ, ٱرۡجِعۡ, ٱرۡكُضۡ, ٱرۡجِعِيٓ |
| 13 | Waqf: sukun-sukun, prev2 Damma | ـُXرِ → ـُXرْ | 2 | 0.0 | صُفۡرٞ, خُسۡرٍ |
| | **Total** | | **9,608** | **100.0** | |

### B. Light Raa (مرققة) — 2,785

| # | Rule | Condition | Count | % | Examples |
|---|------|-----------|------:|----:|----------|
| 1 | Direct Kasra | رِ | 2,160 | 77.6 | غَيۡرِ, أَبۡصَٰرِهِمۡ, ٱلۡأٓخِرِ |
| 2 | Sakinah after Kasra | ـِرۡ (no following mofakham) | 237 | 8.5 | تُنذِرۡهُمۡ, فِرۡعَوۡنَ, ذِرۡعًا |
| 3 | Waqf: after Yaa (madd) | ـيرٌ → ـيرْ | 178 | 6.4 | قَدِيرٞ, بَصِيرٞ, نَصِيرٍ |
| 4 | Direct Kasratan | رٍ | 170 | 6.1 | خَيۡرٖ, نَصِيرٍ, أَنصَارٍ |
| 5 | Waqf: after Kasra | ـِرّٞ → ـِرّْ | 37 | 1.3 | مُّسۡتَمِرّٞ, مُّسۡتَقِرّٞ, مُّنتَشِرٞ |
| 6 | Waqf: sukun-sukun, prev2 Kasra | ـِXرِ → ـِXرْ | 2 | 0.1 | ٱلذِّكۡرِ, حِجۡرٍ |
| 7 | Sakinah after Yaa (madd, prev word) | ـىٰ ٱرۡ | 1 | 0.0 | ٱرۡتَضَىٰ |
| | **Total** | | **2,785** | **100.0** | |

### C. Waqf Impact: End-of-Verse Raa (450 verses)

450 verses end with Raa as the final letter. At waqf, the haraka drops and Raa becomes sakinah. **291 of these (65%) change their classification** compared to their written diacritic.

| Waqf classification | Count |
|---------------------|------:|
| Heavy at waqf | 233 |
| Light at waqf | 217 |
| **Total** | **450** |
| **Changed from written** | **291** |

The two dominant waqf patterns:

**Heavy → Light (at waqf):** Words ending in ـيرٌ / ـيرُ (madd yaa before raa). The written dammatan/damma makes raa heavy, but at waqf it drops and the preceding yaa (with no haraka) makes it light. Examples: قَدِيرٞ, بَصِيرٞ, ٱلۡمَصِيرُ, خَبِيرٞ, نَصِيرٍ, كَبِيرٞ.

**Light → Heavy (at waqf):** Words ending in ـارِ / ـورِ (alif/waw before raa). The written kasra makes raa light, but at waqf it drops and the preceding long vowel (alif/waw) makes it heavy. Examples: ٱلنَّارِ, ٱلصُّدُورِ, ٱلۡأُمُورِ, ٱلدَّارِ, ٱلۡقُبُورِ.

### D. Heavy Exception: Kasra + mofakham (6 cases)

When Raa sakinah is preceded by kasra but followed by an mofakham letter (خصضغطقظ) in the same word, it is pronounced heavy despite the kasra.

| # | Ref | Word | mofakham Letter |
|---|-----|------|----------------|
| 1 | 6:7 | قِرۡطَاسٖ | ط |
| 2 | 9:107 | وَإِرۡصَادٗا | ص |
| 3 | 9:122 | فِرۡقَةٖ | ق |
| 4 | 26:63 | فِرۡقٖ | ق |
| 5 | 78:21 | مِرۡصَادٗا | ص |
| 6 | 89:14 | لَبِٱلۡمِرۡصَادِ | ص |

### F. Special Cases: No Diacritic (10 cases)

#### Huruf Muqattaah (الحروف المقطعة) — 6

The Raa in الٓر (Alif-Lam-Ra) at the start of surahs. Pronounced as the letter name "raa" with natural madd — heavy.

| Surah | Ref |
|-------|-----|
| Yunus | 10:1 |
| Hud | 11:1 |
| Yusuf | 12:1 |
| Ibrahim | 14:1 |
| Al-Hijr | 15:1 |

13:1 الٓمٓرۚ also contains Raa in the muqattaah sequence.

#### Idgham Mutamathilayn (إدغام متماثلين) — 3

The word وَٱذۡكُر appears 3 times (3:41, 7:205, 18:24) followed by رَّبَّكَ. The final Raa of وَٱذۡكُر merges into the initial Raa of رَّبَّكَ (idgham mutamathilayn — two identical letters merging). The first Raa is not pronounced, so tafkheem/tarqeeq does not apply to it. The second Raa (رَّ with shaddah and fatha) is heavy.

#### Imaalah (إمالة) — 1

11:41 مَجۡرٰىٰهَا — the only instance in Hafs where Raa is pronounced with imaalah (between heavy and light).

### G. Disputed Raa Words (خلاف) — 5 words, 22 occurrences

These words have a scholarly dispute (khilaf) on whether Raa is heavy or light in one reading context. The table shows the undisputed context, the disputed context, and the default (preferred) ruling.

| # | Word | Refs | Count | Undisputed | Disputed | Default |
|---|------|------|------:|------------|----------|---------|
| 1 | فِرۡقٖ | 26:63 | 1 | Waqf: tafkheem | **Wasl:** kasra + next قاف (istilaa) | Tafkheem |
| 2 | ٱلۡقِطۡرِ | 34:12 | 1 | Wasl: tarqeeq (kasra) | **Waqf:** prev طۡ (sukun, istilaa), prev-prev قِ (kasra) | Tarqeeq |
| 3 | مِصۡرَ | 10:87, 12:21, 12:99, 43:51 | 4 | Wasl: tafkheem (fatha) | **Waqf:** prev صۡ (sukun, istilaa), prev-prev مِ (kasra) | Tafkheem |
| 4 | نُذُرِ | 54:16,18,21,23,30,33,36,37,39 | 9 | Wasl: tarqeeq (kasra) | **Waqf:** prev ذُ (damma) | Tafkheem |
| 5 | يَسۡرِ / أَسۡرِ / فَأَسۡرِ | 89:4, 20:77, 26:52, 11:81, 15:65, 44:23 | 6 | Wasl: tarqeeq (kasra) | **Waqf:** prev سۡ (sukun), prev-prev fatha | Tarqeeq |

**Notes:**
- Cases 2, 3, 5 (except 89:4): dispute is at mid-ayah waqf only — our analysis covers wasl + end-of-ayah waqf, so these match the undisputed ruling.
- Case 4: all 9 are end-of-ayah. Also 54:5, 54:41 (ٱلنُّذُرُ with damma) are not disputed — heavy at both wasl and waqf.
- Case 5 (89:4 يَسۡرِ): end-of-ayah. Our waqf rule gives heavy (`prev2_fatha`), but default is tarqeeq.

---

## 3. Alef Mufakhkhamah & Muraqqaqah (ألف مفخمة ومرققة)

Alef has no inherent tafkheem or tarqeeq — it takes the quality of the consonant that precedes it. If the preceding consonant is heavy (mufakham), the alef is heavy; otherwise it is light.

**Total alef occurrences: 30,642** (excluding 3,631 mid-ayah cases — see below)

### Alef Types in the Uthmanic Text

Nine categories of alef sound are counted:

| # | Type | Unicode | Description |
|---|------|---------|-------------|
| 1 | Regular alef | ا U+0627 | Madd letter after fatha (excludes silent alef, tanween alef, alef before hamza wasl, and alef with U+06E0) |
| 2 | Maddah alef | آ (ا + U+0653) | Alef with maddah mark |
| 3 | Dagger alef | ٰ U+0670 | Superscript alef combining mark on a consonant |
| 4 | Alef maqsura + dagger | ىٰ (U+0649 + U+0670) | Alef maqsura with explicit dagger alef |
| 5 | Alef maqsura (waqf) | ى U+0649 | Alef maqsura without dagger at end of ayah only (9 cases) |
| 6 | Tanween alef (waqf) | ـًا | Tanween fath alef — only pronounced as alef at end-of-ayah waqf (884 cases) |
| 7 | Tanween maqsura (waqf) | ـًى | Tanween fath maqsura — only pronounced as alef at end-of-ayah waqf (8 cases) |
| 8 | Silent alef (waqf) | ا۠ (ا + U+06E0) | Alef with ۠ mark — silent in wasl, pronounced at waqf only (4 cases) |
| 9 | Implicit (Allah words) | — | Unwritten alef in لفظ الجلالة |

**Wasl exclusions:** Several alef types are only pronounced when stopping (waqf) and are silent in continuous reading (wasl):

- **Alef before hamza wasl:** When a word ends with alef (ا) and the next word starts with hamza wasl (ٱ), the alef is dropped in wasl (e.g. هَٰذَا ٱلَّذِي, يَٰٓأَيُّهَا ٱلنَّاسُ). Only counted at end-of-ayah (0 cases).
- **Alef with U+06E0 (۠):** The small high rectangular zero mark indicates the alef is written but silent in wasl, pronounced only at waqf (e.g. أَنَا۠, ٱلظُّنُونَا۠). 4 cases at end of ayah are kept.
- **Tanween fath alef:** When a word has tanween fath (e.g. نَارٗا, كَثِيرٗا), the alef is only pronounced as a long vowel at waqf. In wasl, the tanween "n" sound follows noon sakinah rules (idgham, ikhfaa, etc.). Same applies to tanween fath on alef maqsura (e.g. هُدٗى).
- **Alef with sukun (U+0652):** Always silent (e.g. ءَامَنُواْ) — excluded entirely.

**Excluded (mid-ayah, not pronounced as alef):**

| Category | Count | Examples |
|----------|------:|----------|
| Alef before hamza wasl (ا...ٱ) | 823 | ٱهۡدِنَا ٱلصِّرَٰطَ, وَلَا ٱلضَّآلِّينَ, وَقُودُهَا ٱلنَّاسُ |
| Alef maqsura before hamza wasl (ى...ٱ) | 569 | عَلَى ٱلۡعَٰلَمِينَ, مُوسَى ٱلۡكِتَٰبَ, إِلَى ٱلسَّمَآءِ |
| Alef with U+06E0 mid-ayah (ا۠) | 62 | أَنَا۠ أُحۡيِۦ, وَأَنَا۠ مَعَكُم, أَنَا۠ بِبَاسِطٖ |
| Tanween alef mid-ayah (ـًا) | 2,092 | نَارٗا فَلَمَّآ, فِرَٰشٗا وَٱلسَّمَآءَ, مَرَضٗاۖ وَلَهُمۡ |
| Tanween maqsura mid-ayah (ـًى) | 85 | هُدٗى لِّلۡمُتَّقِينَ, هُدٗى مِّن, هُدٗى فَمَن |
| **Total excluded** | **3,631** | |

### Decision Tree

```
Alef (any type)
├── What is the preceding consonant?
│   ├── Istilaa letter (خ ص ض غ ط ق ظ)              →  Heavy
│   ├── Raa (ر):
│   │   ├── Raa is heavy (section 2 rules)            →  Heavy
│   │   └── Raa is light (section 2 rules)            →  Light
│   ├── Lam (ل) in Allah word (implicit alef):
│   │   ├── Lam is heavy (section 1 rules)            →  Heavy
│   │   └── Lam is light (section 1 rules)            →  Light
│   └── Any other letter                              →  Light
```

### Summary

| Classification | Count | % |
|----------------|------:|----:|
| Mufakhkhamah (heavy) | 5,755 | 18.8 |
| Muraqqaqah (light) | 24,887 | 81.2 |
| **Total** | **30,642** | **100.0** |

### A. By Alef Type

| Alef Type | Heavy | Light | Total | Heavy examples (خ ص ض غ ط ق ظ ر) |
|-----------|------:|------:|------:|----------------------------------|
| Regular alef (ا) | 1,608 | 12,754 | 14,362 | بِٱتِّخَاذِكُمُ, بِّعَصَاكَ, غَالِبَ, وَسَطٗا, قَالُوٓاْ, ٱلۡعِظَامِ |
| Maddah alef (آ) | 232 | 2,713 | 2,945 | خَآئِفِينَۚ, بَصَآئِرُ, ٱلضَّآلِّينَ, ٱبۡتِغَآءَ, لِلطَّآئِفِينَ, قَآئِمَۢا, ٱلظَّآنِّينَ, صَفۡرَآءُ |
| Dagger alef (ٰ) | 1,258 | 6,226 | 7,484 | يُخَٰدِعُونَ, أَبۡصَٰرِهِمۡ, فَيُضَٰعِفَهُۥ, بِغَٰفِلٍ, ٱلشَّيۡطَٰنُ, قَٰنِتُونَ, ٱلظَّٰلِمِينَ, ٱلصِّرَٰطَ |
| Alef maqsura + dagger (ىٰ) | 368 | 1,874 | 2,242 | وَوَصَّىٰ, قَضَىٰٓ, وَلِتَصۡغَىٰٓ, ٱلۡوُسۡطَىٰ, فَتَلَقَّىٰٓ, لَظَىٰ, وَٱلنَّصَٰرَىٰ |
| Alef maqsura end-of-ayah (ى) | 4 | 5 | 9 | ٱلۡكُبۡرَى, ٱلۡأَشۡقَى, ٱلۡأَتۡقَى  |
| Tanween alef waqf (ـًا) | 294 | 590 | 884 | نَارٗا, كَثِيرٗا, خَيۡرًا |
| Tanween maqsura waqf (ـًى) | 0 | 8 | 8 | — |
| Silent alef waqf (ا۠) | 1 | 3 | 4 | قَوَارِيرَا۠ |
| Implicit (Allah words) | 1,990 | 714 | 2,704 | see section 1 |
| **Total** | **5,755** | **24,887** | **30,642** | |

### B. Heavy Alef — by Preceding Letter

| # | Preceding Letter | Regular | Maddah | Dagger | Maqsura | Tanween waqf | ا۠ waqf | Total |
|---|------------------|--------:|-------:|-------:|--------:|-------------:|--------:|------:|
| 1 | ق (qaf) | 1,056 | 49 | 140 | 62 | 24 | 0 | 1,331 |
| 2 | ر (heavy raa) | 245 | 69 | 271 | 236 | 253 | 1 | 1,075 |
| 3 | ص (sad) | 82 | 6 | 316 | 15 | 2 | 0 | 421 |
| 4 | خ (khaa) | 122 | 12 | 158 | 0 | 0 | 0 | 292 |
| 5 | ط (taa) | 45 | 38 | 139 | 6 | 7 | 0 | 235 |
| 6 | ظ (dhaa) | 12 | 1 | 157 | 2 | 4 | 0 | 176 |
| 7 | غ (ghayn) | 24 | 23 | 60 | 13 | 1 | 0 | 121 |
| 8 | ض (dad) | 22 | 34 | 17 | 38 | 3 | 0 | 114 |
| | **Subtotal** | **1,608** | **232** | **1,258** | **372** | **294** | **1** | **3,765** |
| 9 | ل (Allah heavy lam) | — | — | — | — | — | — | 1,990 |
| | **Total heavy** | | | | | | | **5,755** |

### C. Implicit Alef in Allah Words (لفظ الجلالة)

There is an implicit (unwritten) alef sound between the two lams in Allah words. This alef takes the tafkheem/tarqeeq of the lam — see section 1 for the full analysis.

| Classification | Count |
|----------------|------:|
| Heavy (lam mufakhkhamah) | 1,990 |
| Light (lam muraqqaqah) | 714 |
| **Total** | **2,704** |

### D. Special Case: Imaalah (1 case)

11:41 مَجۡرٰىٰهَا — the raa in this word is pronounced with imaalah (the only instance in Hafs). The dagger alef on raa and the alef maqsura with dagger have a special sound.
