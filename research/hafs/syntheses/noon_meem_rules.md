# Noon & Meem Tajweed Rules (Hafs Riwayah)

Analysis of the Noon and Meem rules (Sakinah, Mushaddadah, and huroof Muqatta'ah) in Uthmanic Hafs v2.0 dataset.

**Source:** `data/QS - QIRAAT/Uthmanic Hafs v2.0/hafsData_v2-0.json`

---

## Functional Breakdown

| # | Rule | Arabic | Count | % |
|---|------|--------|------:|:---:|
| **1** | **Noon Sakinah & Tanween** | | **17,338** | **53.8%** |
| 1.1 | Izhaar Halqi | إظهار حلقي | 2,564 | 8.0% |
| 1.2a | Idgham with Ghunnah | إدغام بغنة | 4,318 | 13.4% |
| 1.2b | Idgham without Ghunnah | إدغام بغير غنة | 2,653 | 8.2% |
| 1.3 | Iqlab | إقلاب | 497 | 1.5% |
| 1.4 | Ikhfaa Haqiqi | إخفاء حقيقي | 7,305 | 22.7% |
| 1.5 | Sakt | السكت المانع | 1 | 0.0% |
| **2** | **Meem Sakinah** | | **7,521** | **23.3%** |
| 2.1 | Ikhfaa Shafawi | إخفاء شفوي | 496 | 1.5% |
| 2.2 | Idgham Shafawi | إدغام شفوي | 871 | 2.7% |
| 2.3 | Izhaar Shafawi | إظهار شفوي | 6,154 | 19.1% |
| **3** | **Noon & Meem Mushaddadah** | | **7,342** | **22.8%** |
| 3.1 | Noon Mushaddadah | النون المشددة | 3,886 | 12.1% |
| 3.2 | Meem Mushaddadah | الميم المشددة | 1,059 | 3.3% |
| 3.3 | Shadda Aridah | الشدة العارضة | 2,016 | 6.2% |
| **4** | **Huroof Muqatta'at** | | **21** | **0.1%** |
| 4.1 | Idgham Meem (Lam) | إدغام الميم (ل) | 8 | 0.0% |
| 4.2 | Idgham Noon (Seen) | إدغام النون (س) | 2 | 0.0% |
| 4.3 | Ikhfaa Noon (Seen→Qaf) | إخفاء النون (س) | 1 | 0.0% |
| 4.4 | Madd & Ikhfaa (Ain) | مد وإخفاء (ع) | 8 | 0.0% |
| 4.5 | Izhaar (Narration) | إظهار الرواية | 2 | 0.0% |
| | **Grand Total** | | **32,222** | |

### By Section

| Section | Count | % |
|---------|------:|:---:|
| 1. Noon Sakinah & Tanween | 17,338 | 53.8% |
| 2. Meem Sakinah | 7,521 | 23.3% |
| 3. Noon & Meem Mushaddadah | 7,342 | 22.8% |
| 4. Huroof Muqatta'at | 21 | 0.1% |

---

## 1. Noon Sakinah and Tanween

### Scope

This section covers the rules applied to Noon Sakinah and Tanween in Hafs ‘an ‘Asim.

**Definitions:**
*   **Noon Sakinah:** A Noon free from any vowel (Fatha, Damma, Kasra) that is fixed in pronunciation and writing, both in continuing and stopping.
*   **Tanween:** An extra Noon Sakinah attached to the end of nouns phonetically but not in writing, and in continuing but not in stopping.

| # | Rule | Arabic | Description | Count |
| - | ---- | ------ | ----------- | -----:|
| 1 | Izhaar Halqi | إظهار حلقي | Clear pronunciation without extra ghunnah | 2,564 |
| 2a | Idgham with Ghunnah | إدغام بغنة | Merging with nasalization (ي، ن، م، و) | 4,318 |
| 2b | Idgham without Ghunnah | إدغام بغير غنة | Complete merging without nasalization (ل، ر) | 2,653 |
| 3 | Iqlab | إقلاب | Transformation of Noon/Tanween into a hidden Meem | 497 |
| 4 | Ikhfaa Haqiqi | إخفاء حقيقي | Hiding the Noon/Tanween with nasalization | 7,305 |
| 5 | Sakt | السكت المانع | Brief pause preventing Idgham | 1 |
| | **Total** | | | **17,338** |

### Izhaar Halqi (إظهار حلقي) — 2,564
إخراج الحرف من مخرجه بلا غنة زائدة (فصل النون/التنوين عن التالي بلا سكت).

**Occurs when followed by:** Throat Letters (ء، هـ، ع، ح، غ، خ)

**Technical Detection:**
*   **Unicode Pattern:** Noon (`U+0646`) with `U+06E1` (Small High Dotless Head of Khah) on top of it, or Aligned Tanween (`U+064B` (Fathatan), `U+064C` (Dammatan), `U+064D` (Kasratan))
*   **Visual:** Small head of Kha (حـ) above Noon; Tanween vowels are aligned (stacked directly).

| Following Letter | Examples (Ref: Surah:Verse:Word) |
| ---------------- | -------- |
|   ء (Hamza)   |   وَيَنۡـَٔوۡنَ (6:26:4)، مَّنۡ أَعۡرَضَ (20:100:1)، وَجَنَّٰتٍ أَلۡفَافً (78:16:1)   |
|   هـ (Ha)   |   مِّنۡهُم (2:75:7)،  مِنۡ هَاد (13:33:38)،  قَوۡمٍ هَاد (13:7:11)   |
|   ع (Ain)   |    مِنۡ عَاصِمٖۗ (40:16:1)،  شَيۡءٍ عَلِيمٌ (2:115:1)   |
|   ح (Ha)   |   يَنۡحِتُونَ (15:82:1)،  عَزِيزٌ حَكِيم (2:220:1)   |
|   غ (Ghain)   |   مِنۡ غِسۡلِينٖ (69:36:1)،  عَفُوًّا غَفُورًا (35:28:1)   |
|   خ (Kha)   |    وَٱلۡمُنۡخَنِقَةُ (5:3)،  ذَرَّةٍ خَيۡرٗا (99:7:1)   |

### Idgham (الإدغام)
Use of merging. Classified into Idgham with Ghunnah (Nasalization) and without Ghunnah.

#### Idgham with Ghunnah (إدغام بغنة) — 4,318
دمج النون الساكنة أو التنوين في (ي، ن، م، و) مع بقاء الغنة.

**Occurs when followed by:** (ي، ن، م، و)

**Technical Detection:**
*   **Unicode Pattern:** Bare Noon (`U+0646`), or `U+065E` (Fatha with Two Dots), `U+0657` (Inverted Damma), `U+0656` (Subscript Alef) (Sequential Tanween)
*   **Visual:** Noon is bare (no sukoon); Tanween vowels are sequential (offset).

| Following Letter | Type | Examples (Ref: Surah:Verse:Word) |
| ---------------- | ---- | -------- |
|   ي (Ya)   |   Deficient (Naqis)   |   مَن يَقُولُ (2:8:3)،   يَوۡمَئِذٖ يَتَذَكَّرُ (89:23:4)   |
|   ن (Noon)   |   Complete (Kamil)   |   إِن نَّفَعَتِ (87:9:2)،  يَوۡمَئِذٖ نَّاعِمَةٞ (88:8:2)   |
|   م (Meem)   |   Complete (Kamil)   |   مِّن مَّآءٖ مَّهِين (32:8:6)، َا مَلِكٗا نُّقَٰتِل   |
|   و (Waw)   |   Deficient (Naqis)   |    مِن وَلِيّ (2:107:14)،  يَوۡمَئِذٖ وَاجِفَة (79:8:2)  |

#### Ghunnah Quality: Mufakhamah and Muraqqaqah (الغنةالمرققة و المفخمة)

الغنة تابعة لما بعدها تفخيماً وترقيقاً — The Ghunnah follows the letter that comes after it in terms of heaviness (Tafkhim) and lightness (Tarqiq).

##### **Light Ghunnah (الغنة المرققة):**

The Ghunnah is always pronounced light (Muraqqaqah) when followed by any of the remaining (non-heavy) letters. This includes the Idgham letters themselves (ي، ن، م، و) when they are not from the heavy set.

| Category | Examples |
| -------- | -------- |
|   Light letters   |   هَٰٓأَنتُمۡ (3:66:1)، أَنفُسِكُمۡ (9:128:5)، عَنكُمۡ (16:54:5)   |

#### Idgham without Ghunnah (إدغام بغير غنة) — 2,653
دمج النون الساكنة أو التنوين تماماً في (ل، ر) بلا غنة.

**Occurs when followed by:** (ل، ر)

**Technical Detection:**
*   **Unicode Pattern:** Bare Noon (`U+0646`), or `U+065E` (Fatha with Two Dots), `U+0657` (Inverted Damma), `U+0656` (Subscript Alef) (Sequential Tanween) + `U+0651` (Shadda) on next letter.

| Following Letter | Examples (Ref: Surah:Verse:Word) |
| ---------------- | -------- |
|   ل (Lam)   |    مِن لَّدُنكَ (3:8:10)،  هُدٗى لِّلۡمُتَّقِينَ (2:2:6)   |
|   ر (Ra)   |    مِّن رَّبِّهِمۡۖ (2:5:4)،  غَفُورٞ رَّحِيم (2:173:24)  |

#### Exceptions
**Izhaar Mutlaq (الإظهار المطلق):**
If the Noon Sakinah and the Idgham letter (Yaa or Waw) meet in the **same word**, Idgham is forbidden to preserve the meaning.
*   **Examples:** الدنيا (Ad-Dunya), بنيان (Bunyan), قنوان (Qinwan), صنوان (Sinwan).

### Iqlab (إقلاب) — 497
قلب النون الساكنة أو التنوين ميماً مخفاة عند الباء بغنة.

**Occurs when followed by:** (ب)

**Technical Detection:**
*   **Unicode Pattern:** Specific combinations involving the small Meem (`U+06E2` (Small High Meem Isolated) or `U+06ED` (Small Low Meem)).

| Type | Unicode Combination | Visual | Examples (Ref: Surah:Verse:Word) |
| ---- | ------------------- | ------ | -------- |
|   **Noon**   |   `U+0646` + `U+06E2` (Small High Meem Isolated)   |   Small High Meem above Noon   |  مِنۢ بَعۡد (2:27:5)،  مِنۢ بَعۡضٖۗ (3:34:3)   |
|   **Tanween Fatha**   |   `U+064E` (Fatha) + `U+06E2` (Small High Meem Isolated)   |   Single Fatha + Small High Meem   |   سميعاً بصيرا (4:58:24)  |
|   **Tanween Damma**   |   `U+064F` (Damma) + `U+06E2` (Small High Meem Isolated)   |   Single Damma + Small High Meem   |   سَمِيعُۢ بَصِيرٞ (22:61:14)   |
|   **Tanween Kasra**   |   `U+0650` (Kasra) + `U+06ED` (Small Low Meem)   |   Single Kasra + Small Low Meem   |   يَوۡمَئِذِۭ بِجَهَنَّمَ (89:23:2)  |

### Ikhfaa Haqiqi (إخفاء حقيقي) — 7,305
ستر النون الساكنة أو التنوين عند مخرج التالي بغنة.

**Occurs when followed by:** The remaining 15 letters (ت، ث، ج، د، ذ، ز، س، ش، ص، ض، ط، ظ، ف، ق، ك).

**Technical Detection:**
*   **Unicode Pattern:** Bare Noon (`U+0646`), or `U+065E` (Fatha with Two Dots), `U+0657` (Inverted Damma), `U+0656` (Subscript Alef) (Sequential Tanween).
*   **Visual:** Noon is bare; Tanween vowels are sequential.

| Following Letter | Examples (Ref: Surah:Verse:Word) |
| ---------------- | -------- |
|   ت (Ta)   |   فَمَن تَطَوَّع (2:184:20)، فَمَن تَابَ (5:39:1)   |
|   ث (Tha)   |   مِن ثَمَرَةٖ (2:25:16)،  فَمَن ثَقُلَتۡ (7:8:4)   |
|   ج (Jeem)   |   فَأَنجَيۡنَٰهُم (21:9:4)،  إِن جَآءَكُم (49:6:4)  |
|   د (Dal)   |   أَندَادٗا (2:22:21)،  مِن دُونِ (2:165:5)   |
|   ذ (Thal)   |    مُنذِرُونَ (26:208:7)، َ وَمِن ذُرِّيَّتِيۖ (2:124:13)  |
|   ز (Zay)   |   أُنزِلَ (2:4:4)، فَإِن زَلَلۡتُم (2:209:1)   |
|   س (Seen)   |   نَنسَخۡ (2:106:3)، ۡ مِن سُوٓء (3:30:12)  |
|   ش (Sheen)   |    مَّنشُور (52:3:3)،  فَمَن شَآء (18:29:5)  |
|   ص (Sad)   |   بَقَرَةٞ صَفۡرَآءُ (2:69:13)، مَنصُورًا (17:33:22)  |
|   ض (Dad)   |   مَّنضُودٖ (11:82:12)،  مَّن ضَلَّ (5:105:8)   |
|   ط (Ta)   |    مَنطِقَ (27:16:8)، اْ مِن طَيِّبَٰتِ   |
|   ظ (Zha)   |   تَنظُرُونَ (2:50:10)، هُم مِّن ظَهِيرٖ   |
|   ف (Fa)   |    أَنفُسِهِمۡ (2:265:10)، ْ مَن فَعَلَ (21:59:2)  |
|   ق (Qaf)   |    مُنقَلِبُونَ (7:125:5)،  مِن قَرۡيَةٍ (15:4:3)   |
|   ك (Kaf)   |   ٱلۡمُنكَرِ (3:110:10)، مَن كَانَ (2:97:2)   |

#### Ghunnah Quality: Mufakhamah and Muraqqaqah (الغنة المفخمة والمرققة)

الغنة تابعة لما بعدها تفخيماً وترقيقاً — The Ghunnah follows the letter that comes after it in terms of heaviness (Tafkhim) and lightness (Tarqiq).

##### **Heavy Ghunnah (الغنة المفخمة):**

The Ghunnah is pronounced heavy (Mufakhamah) when the Noon Sakinah or Tanween is followed by one of the heavy (Musta'liyah) letters: **(ص، ض، ط، ظ، ق)**. This applies regardless of the vowel on the heavy letter (Fatha, Damma, or Kasra).

| Heavy Letter | Examples |
| ------------ | -------- |
|   ص (Sad)   |   مَنصُورًا (17:33:22)، وَلَمَن صَبَر (42:43:1)، ِۦ قَوۡمٗا صَٰلِحِين (12:9:13)   | 
|   ض (Dad)   |   مَّنضُودٖ (56:29:2)، ا قَوۡمٗا ضَآلِّين (23:106:7)   |
|   ط (Ta)   |   فَٱنطَلَقُواْ (68:23:1)،  مَآءٗ طَهُورٗ (25:50:12)   |
|   ظ (Zha)   |   مَن ظَلَم (27:11:2)،  ظِلّٗا ظَلِيل (4:57:19)   |
|   ق (Qaf)   |   مُنقَلَبٗا (18:36:12)، وَفَتۡحٞ قَرِيبٞ (61:13:6)   |

> **Note on Qaf (ق) with Kasra:** When there is a Kasra under the Qaf, the Ghunnah is at its weakest level of heaviness, because Qaf with Kasra is at its lowest level of Tafkhim. The Qaf is Musta'li Munfatih (an elevated but non-enclosed letter), making the Ghunnah relatively lighter compared to the other heavy letters. Compare: the Ghunnah in **ٞ مِّن صِيَام** (2:195:29) (stronger) vs. **مِن قِيَام** (51:45:3) (weaker).

#### Special Case: Sakt (السكت المانع) — 1
A brief pause (Sakt) that prevents Idgham despite the conditions being met.

**Example:**
*   **وقيل من راق** (Al-Qiyamah: 27) | وَقِيلَ مَنۡۜ رَاقٖ |
    *   Noon is followed by Ra (usually Idgham), but the Sakt sign `U+06DC` (Small High Seen) or specific narration rules require a pause, preserving the clear Noon.

### Impact of Waqf (Stopping) on Rules

In computational Tajweed, **Waqf** (stopping) changes the state of the letter and often cancels the rule if it depends on the following word.

| Condition | Effect of Stopping | Outcome (Rule Change) |
| --- | --- | --- |
| **Idgham / Iqlab / Ikhfaa** (End of Word) | The connection to the next letter is broken. | **Rule Removed.** The Noon reverts to **Izhaar** (Clear Noon with Sukoon). <br> *Example:* Stop on `من` in `وَقِيلَ مَنۡۜ رَاقٖ` -> Pronounce `Mn`. |
| **Tanween Damma / Kasra** | The Tanween sound is dropped. | **Rule Removed.** The letter becomes Sakin (Silent). <br> *Example:* `عليمٌ` -> `Aleem`. |
| **Tanween Fatha** | The Tanween is substituted with Alif. | **Madd Added (Madd 'Iwad).** <br> *Example:* `عليماً` -> `Aleemaa`. |

### Tanween Fatha at Stop (أحكام تنوين الفتح عند الوقف)

| Rule | Description | Condition | Unicode Pattern | Visual Detection | Performance | Stop Effect | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- |
|   **Madd 'Iwad (General)**   |   Substituting Tanween Fatha with an Alif upon stopping   |   End of Accusative Noun   |   `U+064B` (Fathatan), `U+0627`   |   Two Fathas followed generally by Alif   |   Prolong the letter for 2 counts instead of Tanween   |   Tanween turns into prolonged Alif   |   عليماً (4:11:70)، حكيماً (4:11:71)  |
|   **Exception: Ta Marbuta**   |   Turning Ta Marbuta into Ha upon stopping   |   End of Feminine Word   |   `U+0629`, `U+064B` (Fathatan)   |   Ta Marbuta with Tanween   |   Pronounce Ta as clear silent Ha   |   Delete Tanween and turn Ta into Ha   |   جنةً -> `jannah`   |
|   **Exception: Ism Maqsur**   |   Deleting Tanween and keeping Alif Maqsur   |   Nouns ending in (ى)   |   `U+0649`, `U+064B` (Fathatan)   |   Alif Maqsura (ى) with Tanween   |   Prolong Alif for 2 counts (Natural Madd)   |   Delete Tanween and keep the Madd   |   هدىً (2:2:6)، طوىً (20:12:9)  |
|   **Appendix: Noon Tawkid**   |   Noon of emphasis written as Tanween Fatha   |   Surah Yusuf & Al-Alaq   |   `U+0646`, `U+064B` (Fathatan) (visually)   |   Noon attached to verb written as Tanween   |   Treated like Accusative Nouns   |   Substitute Noon with Alif prolonged for 2 counts   |    وَلَيَكُونٗا (12:32:17)،   لَنَسۡفَعَۢا (96:15:5)   |

---

## 2. Meem Sakinah Rules

### Scope

This section covers the rules applied to Meem Sakinah (a Meem with no vowel) in Hafs ‘an ‘Asim.

**Definitions:**
*   **Meem Sakinah:** A Meem (`م`) free from any vowel (Fatha, Damma, Kasra) that is fixed in pronunciation and writing.
*   **The Three Rules:** Ikhfaa Shafawi, Idgham Shafawi (Mithlayn Sagheer), and Izhaar Shafawi.

| # | Rule | Arabic | Description | Count |
| - | ---- | ------ | ----------- | -----:|
| 1 | Ikhfaa Shafawi | إخفاء شفوي | Hiding the Meem when followed by Baa | 496 |
| 2 | Idgham Shafawi | إدغام شفوي | Merging the Meem when followed by another Meem | 871 |
| 3 | Izhaar Shafawi | إظهار شفوي | Clear pronunciation when followed by any other letter | 6,154 |
| | **Total** | | | **7,521** |

### Ikhfaa Shafawi (إخفاء شفوي) — 496
ستر الميم عند ملاقاتها للباء مع الغنة.

**Occurs when followed by:** (ب)

**Technical Detection:**
*   **Unicode Pattern:** `U+0645` (Bare Meem) followed by `ب`.
*   **Visual:** Meem is bare (no sukoon sign).

| Following Letter | Examples (Ref: Surah:Verse:Word) |
| ---------------- | -------- |
|   ب (Baa)   |   تَرۡمِيهِم بِحِجَارَةٖ (105:4:1)،  يَعۡتَصِم بِٱللَّهِ (3:101:11)   |

### Idgham Shafawi (إدغام شفوي) — 871
Also called Idgham Mithlayn Sagheer (إدغام مثلين صغير). Merging the Meem Sakinah into a following Meem.

**Occurs when followed by:** (م)

**Technical Detection:**
*   **Unicode Pattern:** `U+0645` (Bare Meem) followed by `م` with `U+0651` (Shadda).
*   **Visual:** Meem is bare, following Meem has Shadda.

| Following Letter | Examples (Ref: Surah:Verse:Word) |        
| ---------------- | -------- |        
|   م (Meem)   |    لَهُم مَّا يَشَآءُونَ (39:34:1)،  فِي قُلُوبِهِم مَّرَضٞ   |

### Izhaar Shafawi (إظهار شفوي) — 6,154
نطق الميم واضحة دون غنة زائدة.

**Occurs when followed by:** All letters except (ب) and (م).

**Technical Detection:**
*   **Unicode Pattern:** `U+06E1` (Small High Dotless Head of Khah) on the Meem (`U+0645`).
*   **Visual:** Small head of Kha (حـ) above Meem.

| Following Letter | Examples (Ref: Surah:Verse:Word) | Note |
| ---------------- | -------- | ---- |
|   و (Waw)   |    يَسۡتَهۡزِئُ بِهِمۡ وَيَمُدُّهُمۡ (2:15:2)   |   **Izhaar Shadid:** Be careful not to hide Meem here.   |
|   ف (Fa)   |   بِذَنۢبِهِمۡ فَسَوَّىٰهَا (91:14:6)   |   **Izhaar Shadid:** Be careful not to hide Meem here.   |
|   Others   |    أَنۡعَمۡتَ (1:7:3)، لَعَلَّكُمۡ تَتَّقُونَ (2:21:10)   |   Standard clear pronunciation.   |

### Impact of Waqf (Stopping) on Rules

| Rule | Effect of Stopping | Outcome (Rule Change) | Examples |
| --- | --- | --- | --- |
|   **Ikhfaa Shafawi** (Meem-Baa)   |   Connection to 'Baa' is broken.   |   **Rule Removed.** Meem becomes clearly pronounced (Izhaar) with Sukoon.   |   `تَرۡمِيهِم بِحِجَارَةٖ`-> `tarmeehem`   |
|   **Idgham Shafawi** (Meem-Meem)   |   Connection to second 'Meem' is broken.   |   **Rule Removed.** First Meem becomes clearly pronounced (Izhaar) with Sukoon.   |   `لَهُم مَّا يَشَآءُونَ` -> `lahum`     |
|   **Izhaar Shafawi**   |   No change in status.   |   **Remains Izhaar.** Meem is pronounced clearly with Sukoon.   |   `هُمْ فِيهَا` -> `hum`   |

---

## 3. Noon and Meem Mushaddadah

### Scope

This section covers the rules applied to Noon and Meem with Shadda (Ghunnah Mushaddadah) in Hafs ‘an ‘Asim.

**Definitions:**
*   **Ghunnah:** A nasal sound emitted from the nose (Khayshum). It is an intrinsic characteristic of the Noon and Meem.
*   **Mushaddadah:** Emphasized (doubled) letter, marked with a Shadda (`ّ`).
*   **Level of Ghunnah:** The strongest level of Ghunnah (Akmal Ma Takoon) occurs in the Mushaddadah.

| # | Rule | Arabic | Description | Count |
| - | ---- | ------ | ----------- | -----:|
| 1 | Noon Mushaddadah | النون المشددة | Emphasized Noon with prolonged Ghunnah | 3,886 |
| 2 | Meem Mushaddadah | الميم المشددة | Emphasized Meem with prolonged Ghunnah | 1,059 |
| 3 | Shadda 'Aridah | الشدة العارضة | Temporary emphasis due to Idgham (merging) | 2,016 |
| | **Total** | | | **7,342** |

### Noon Mushaddadah (النون المشددة) — 3,886
نون مضاعفة أصلية تخرج بغنة مشبعة (أكمل ما تكون).

**Technical Detection:**
*   **Unicode Pattern:** `U+0646` (Noon) + `U+0651` (Shadda).
*   **Location:** Middle or end of the word.

| Feature | Description |
| --- | --- |
| **How to Identify** | Presence of Shadda mark above the Noon. |
| **Performance** | Press the tongue tip against the gums with prolonged Ghunnah (approx. 2 counts). |
| **Effect of Stop** | The Ghunnah remains fixed (Nabr) even when stopping. |
| **Examples** | إِنَّآ(2:119:1)،  ٱلنَّاسِ(114:1:1)،  ٱلۡجَنَّةَ(2:35:1) |

### Meem Mushaddadah (الميم المشددة) — 1,059
ميم مضاعفة أصلية تخرج بغنة مشبعة (أكمل ما تكون).

**Technical Detection:**
*   **Unicode Pattern:** `U+0645` (Meem) + `U+0651` (Shadda).
*   **Location:** Middle or end of the word.

| Feature | Description |
| --- | --- |
| **How to Identify** | Presence of Shadda mark above the Meem. |
| **Performance** | Complete closure of lips with prolonged Ghunnah (approx. 2 counts). |
| **Effect of Stop** | The Ghunnah remains fixed (Nabr) even when stopping. |
| **Examples** | حَمَّالَةَ(111:4:2)،  ثُمَّ(2:74:1)، عَمَّا(2:134:13) |

### Shadda 'Aridah (الشدة العارضة) — 2,016
علامة ضبط لإدغام سابق وليست أصلية في الكلمة.

**Technical Detection:**
*   **Unicode Pattern:** Noon, Meem, or Tanween followed by Noon with Shadda (`U+0651`) or Meem with Shadda (`U+0651`).
*   **Context:** Preceded by a letter causing Idgham (e.g., Noon Sakinah or Tanween merging into it).

| Feature | Description |
| --- | --- |
| **How to Identify** | Shadda at the very beginning of the word. |
| **Comparison** | Distinct from original Shadda which is part of the root/word structure. |
| **Performance** | Treated as emphasized (Mushaddad) only when connecting (Wasl). |
| **Effect of Start** | If starting from this word, the Shadda is ignored/removed. |
| **Effect of Stop (Preceding Word)** | If stopping on the previous word, the connection is broken. | **Rule Removed.** This word must be started without Shadda. |
| **Examples** | مِن مَّالٖ (23:44:5)، مِن نُّطۡفَةٖ(16:13:3) |

---

## 4. Huroof Muqatta'at (Disjoint Letters)

### Scope

This section covers the rules applied to the Disjoint Letters (Huroof Muqatta'at) appearing at the beginning of 29 Surahs in Hafs ‘an ‘Asim. Specifically focusing on the interaction between the ending of one letter and the beginning of the next (e.g., Noon of "Seen" meeting Meem of "Meem").

**Definitions:**
*   **Huroof Muqatta'at:** Unique letter combinations at the start of certain Surahs. Pronounced by spelling out their names (e.g., Alif, Lam, Meem).
*   **Target Letters:** Letters ending in Noon or Meem that interact with what follows:
    *   **Lam (لام):** Ends in Meem.
    *   **Seen (سين):** Ends in Noon.
    *   **Meem (ميم):** Begins with Meem.
    *   **Ain (عين):** Contains a Yaa Leen and ends in Noon.
    *   **Noon (نون):** Ends in Noon.

| # | Rule | Arabic | Description | Count |
| - | ---- | ------ | ----------- | -----:|
| 1 | Idgham of Meem (Lam) | إدغام الميم (ل) | Merging the Meem of "Lam" into the Meem of "Meem" | 8 |
| 2 | Idgham of Noon (Seen) | إدغام النون (س) | Merging the Noon of "Seen" into the Meem of "Meem" | 2 |
| 3 | Ikhfaa of Noon (Seen) | إخفاء النون (س) | Hiding the Noon of "Seen" before Qaf | 1 |
| 4 | Madd and Ikhfaa (Ain) | مد وإخفاء (ع) | Lengthening the Yaa of "Ain" and hiding its Noon | 8 |
| 5 | Izhaar (Narration) | إظهار الرواية | Exceptions where Noon is pronounced clearly despite Idgham rule | 2 |
| | **Total** | | | **21** |

### Idgham of Meem (Lam) (إدغام الميم في الميم) — 8
إدغام ميم "لام" في ميم "ميم".

**Occurs in:** Alif-Lam-Meem (الٓمٓ), Alif-Lam-Meem-Sad (الٓمٓصٓ), Alif-Lam-Meem-Ra (الٓمٓر).

**Technical Detection:**
*   **Unicode Pattern:** `U+0644` (Lam) + `U+0653` (Maddah Above) followed by `U+0645` (Meem) + `U+0651` (Shadda).
*   **Example:** الٓمٓ (2:1)
    *   Pronunciation: Alif Laaam-Meem.
    *   Mechanism: The Meem at the end of "Laam" meets the Meem at the start of "Meem" = Idgham Shafawi (Mithlayn).

### Idgham of Noon (Seen) (إدغام النون في الميم) — 2
إدغام نون "سين" في ميم "ميم".

**Occurs in:** Ta-Seen-Meem (طسٓمٓ).

**Technical Detection:**
*   **Unicode Pattern:** `U+0633` (Seen) + `U+0653` (Maddah Above) followed by `U+0645` (Meem) + `U+0651` (Shadda).
*   **Example:** طسٓمٓ (26:1)
    *   Pronunciation: Taa Seem-Meem.
    *   Mechanism: The Noon at the end of "Seen" meets the Meem at the start of "Meem" = Idgham with Ghunnah.

### Ikhfaa of Noon (Seen) (إخفاء النون عند القاف) — 1
إخفاء نون "سين" عند القاف.

**Occurs in:** Ain-Seen-Qaf (عٓسٓقٓ).

**Technical Detection:**
*   **Unicode Pattern:** `U+0633` (Seen) + `U+0653` (Maddah Above) followed by `U+0642` (Qaf).
*   **Example:** عٓسٓقٓ (42:2)
    *   Pronunciation: 'Aiiin Seee(ng) Qaaaf.
    *   Mechanism: The Noon at the end of "Seen" meets Qaf = Ikhfaa Haqiqi.

### Madd and Ikhfaa (Ain) (مد وإخفاء عين) — 8
مد لين العين مع إخفاء نونها.

**Occurs in:** Kaf-Ha-Ya-Ain-Sad (كٓهيعٓصٓ), Ain-Seen-Qaf (عٓسٓقٓ).

**Technical Detection:**
*   **Unicode Pattern:** `U+0639` (Ain) + `U+0653` (Maddah Above).
*   **Example:** كٓهيعٓصٓ (19:1)
    *   Pronunciation: ...'Aiiin Saaad.
    *   Mechanism:
        1.  **Madd Leen:** The Yaa inside "Ain" is lengthened 4 or 6 counts (6 is preferred).
        2.  **Ikhfaa:** The Noon at the end of "Ain" meets Sad or Seen = Ikhfaa Haqiqi.

### Izhaar (Narration Exceptions) (إظهار الرواية) — 2
إظهار نون "نون" أو "سين" وصلاً (Exceptions in Hafs).

**Occurs in:** Ya-Seen (يسٓ), Noon (ن).

**Technical Detection:**
*   **Unicode Pattern:** `U+0646` (Noon) or `U+0633` (Seen) followed by `U+0648` (Waw).
*   **Marking:** Presence of `U+06E1` (Small High Dotless Head of Khah) on the Noon/Seen instead of being bare.

| Surah | Ayah | Letters | Rule | Mechanism |
| ----- | ---- | ------- | ---- | --------- |
| **Ya-Seen (36)** | 1-2 |(36:1) يسٓ وَالْقُرْآنِ | Izhaar Mutlaq (Narration) | Pronounce "Seen" clearly despite connecting to Waw. |
| **Al-Qalam (68)** | 1 |(68:1:1) نٓۚ وَٱلۡقَلَ | Izhaar Mutlaq (Narration) | Pronounce "Noon" clearly despite connecting to Waw. |

### Impact of Waqf (Stopping) on Rules

| Rule | Context | Effect of Stopping (Hypothetical/Test) |
| --- | --- | --- |
| **Idgham (Between Letters)** | e.g., Lam-Meem in `الم` | **Rule Removed.** The first letter (Lam) is pronounced with clear Meem (Izhaar) and Madd Lazim (6 counts). |
| **Ikhfaa (Between Letters)** | e.g., Seen-Qaf in `عسق` | **Rule Removed.** The first letter (Seen) is pronounced with clear Noon (Izhaar) and Madd Lazim (6 counts). |
| **End of Letter Group** | e.g., End of `الم` | **Fixed Sukoon.** The final letter follows the standard pause rule (Madd Lazim 6 counts + Sukoon). |
