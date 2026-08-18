# Waqf & Ibtidaa Tajweed Rules

Analysis of the Waqf (Stopping) and Ibtidaa (Starting) rules in Uthmanic Hafs v2.0 dataset.

**Source:** `data/QS - QIRAAT/Uthmanic Hafs v2.0/hafsData_v2-0.json`

---

## 1. Waqf Symbols (علامات الوقف في المصحف الشريف)

### Scope

This section covers the standard Waqf symbols (stopping marks) used in the Uthmani Mushaf in Hafs 'an 'Asim.

**Definitions:**
*   **Waqf (الوقف):** قطع الصوت والسكوت على آخر الكلمة زمناً يتنفس فيه القارئ بنية استئناف القراءة.  
    Pausing the recitation at the end of a word, cutting the sound with the intention of resuming.
*   **Qat' (القطع):** قطع القراءة بنية الانتهاء منها.  
    Ending the recitation with the intention of concluding.
*   **Waqf Symbols:** Marks placed above or near specific words in the Mushaf to guide the reciter on where to stop, continue, or pause.

| # | Rule | Arabic | Description | Count | % |
|---|------|--------|-------------|------:|:---:|
| **—** | **Waqf Symbols** | **علامات الوقف** | | **4,272** | **100%** |
| 1 | Waqf Lazim | وقف لازم (مـ) | Obligatory stop; continuing may alter meaning | 21 | 0.5% |
| 2 | Waqf Ja'iz Mutasawi | وقف جائز متساوي (ج) | Stopping and continuing are equally permissible | 2,083 | 48.8% |
| 3 | Al-Wasl Awla | الوصل أولى (صلى) | Continuing is preferred over stopping | 1,651 | 38.6% |
| 4 | Al-Waqf Awla | الوقف أولى (قلى) | Stopping is preferred over continuing | 511 | 12.0% |
| 5 | Mu'anaqah (Ta'anuk) | معانقة (∴ ∴) | Paired stops: stop at one but not both | 3 | 0.1% |

### Waqf Lazim (وقف لازم — مـ) — 21
الوقف الذي يجب على القارئ الوقوف عنده لئلا يتغير المعنى. هو نوع فرعي من الوقف التام، يلزم الوقف عليه لأن الوصل يوهم معنى غير مراد.

**Occurs when:** The symbol (مـ) appears above a word, indicating that continuing would distort the intended meaning.

**Technical Detection:**
*   **Unicode Pattern:** `U+06D8` (Small High Meem Initial — ۘ)
*   **Visual:** The letter Meem (مـ) appears as a small mark above the word.

| Examples (Ref: Surah:Verse:Word) | Context |
| -------- | ------- |
|   وَلاَ يَحْزُنكَ قَوْلُهُمْ ۘ إِنَّ الْعِزَّةَ لِلّهِ جَمِيعاً (10:65:1)   |   Stop on **(قَوْلُهُمْ)** is obligatory. Continuing without stopping may imply that "All honor belongs to Allah" is part of "their words" rather than a new divine statement.   |

### Waqf Ja'iz Mutasawi (وقف جائز متساوي — ج) — 2,083
الموضع الذي يستوي فيه الوقف والوصل.

**Occurs when:** The symbol (ج) appears above a word.

**Technical Detection:**
*   **Unicode Pattern:** `U+06DA` (Small High Jeem — ۚ)
*   **Visual:** The letter Jeem (ج) appears as a small mark above the word.

| Examples (Ref: Surah:Verse:Word) | Context |
| -------- | ------- |
|   يَسۡـَٔلُهُۥ مَن فِي ٱلسَّمَٰوَٰتِ وَٱلۡأَرۡضِۚ كُلَّ يَوۡمٍ هُوَ فِي شَأۡنٍ (55:29:5)   |   Stop on **(ٱلۡأَرۡضِ)** is permissible. Continuing without stopping provides better meaning flow.   |

### Al-Wasl Awla (الوصل أولى — صلى) — 1,651
الوقف جائز لكن الوصل أولى.

**Occurs when:** The symbol (صلى) appears above a word.

**Technical Detection:**
*   **Unicode Pattern:** `U+06D6` (Small High Sad-Lam-Ya — ۖ)
*   **Visual:** The letters (صلى) appear as a small mark above the word.

| Examples (Ref: Surah:Verse:Word) | Context |
| -------- | ------- |
|   سَبَّحَ لِلَّهِ مَا فِي ٱلسَّمَٰوَٰتِ وَٱلۡأَرۡضِۖ وَهُوَ ٱلۡعَزِيزُ ٱلۡحَكِيمُ (57:1:7)   |   Stop on **(ٱلۡأَرۡضِ)** is permissible. Continuing without stopping provides better meaning flow.   |

### Al-Waqf Awla (الوقف أولى — قلى) — 511
الوقف جائز والوقف أولى من الوصل.

**Occurs when:** The symbol (قلى) appears above a word.

**Technical Detection:**
*   **Unicode Pattern:** `U+06D7` (Small High Qaf-Lam-Ya — ۗ)
*   **Visual:** The letters (قلى) appear as a small mark above the word.

| Examples (Ref: Surah:Verse:Word) | Context |
| -------- | ------- |
|   إِلَّا مَن كَانَ هُودًا أَوۡ نَصَٰرَىٰۗ تِلۡكَ أَمَانِيُّهُمۡۗ قُلۡ هَاتُواْ بُرۡهَٰنَكُمۡ (2:111:10)   |   Stop on **(نَصَٰرَىٰ)** is permissible. Stopping provides better meaning flow.   |

### Mu'anaqah / Ta'anuk (معانقة — ∴ ∴) — 6
علامتا وقف متقابلتان: إذا وقفت على أحدهما لا تقف على الآخر.

**Occurs when:** Two paired stop marks appear close together (∴ ∴). The reciter must stop at one of the two marked positions but not at both.

**Technical Detection:**
*   **Unicode Pattern:** `U+06DB` (Small High Three Dots — ۛ)
*   **Visual:** Three-dot marks (∴) appear at two nearby positions in the verse.

| Examples (Ref: Surah:Verse:Word) | Context |
| -------- | ------- |
|   ذَٰلِكَ ٱلۡكِتَٰبُ لَا رَيۡبَۛ فِيهِۛ هُدٗى لِّلۡمُتَّقِين (2:2:3)   |   Stop on **(رَيۡبَ)** is permissible but continue on **(فِيهِ)** without stoping   |

---

## 2. Waqf Types (أقسام الوقف)

### Scope

This section covers the four types of Waqf (stopping). The first three (Intizari, Ikhtibari, Idtirari) are non-voluntary and context-specific, while the fourth (Ikhtiyari) is voluntary and is the core of Waqf science.

**الوقف:** قطع الصوت عن قراءة القرآن زمناً يتنفس فيه، ثم يعاود القراءة. وينقسم إلى أربعة أنواع.

| # | Rule | Arabic | Description |
| - | ---- | ------ | ----------- |
| 1 | Waqf Intizari | الوقف الانتظاري | وقف جائز في مقام الشرح وتعليم القراءات |
| 2 | Waqf Ikhtibari | الوقف الاختباري | لا يكون إلا في مقام الاختبار والتعليم |
| 3 | Waqf Idtirari | الوقف الاضطراري | مضطر لعطاس أو ضيق النفس أو السعال أو النسيان وغير ذلك |
| 4 | Waqf Ikhtiyari | الوقف الاختياري | وقوف القارئ بإرادته بدون أسباب خارجة — وهو أربعة أنواع |

### 2.1 Waqf Intizari (الوقف الانتظاري)
وقف جائز في مقام الشرح وتعليم القراءات.

**Occurs when:** The reciter stops to explain or teach the various Qira'at (readings). This is a permitted stop within the context of instruction.

| Feature | Description |
| --- | --- |
| **How to Identify** | The context of Jam' (combining qiraat) or teaching. The reciter pauses to present or explain each variant. |
| **Performance** | Stop on the word, recite or explain the variant, then resume or repeat with the next variant. |
| **Ruling** | Permissible when combining qiraat or in a teaching context. A specialized practice. |
| **Examples** | Stopping to present the Hafs and Warsh variants of the same word. |

### 2.2 Waqf Ikhtibari (الوقف الاختباري)
لا يكون إلا في مقام الاختبار والتعليم.

**Occurs when:** A teacher asks a student to stop on a specific word to test their knowledge of how to pronounce it (e.g., maqtu' vs. mawsul, ta marbuta vs. mabsuta).

| Feature | Description |
| --- | --- |
| **How to Identify** | Instructional context: a teacher explicitly requests a stop on a specific word. |
| **Performance** | Stop on the requested word, demonstrating the correct pronunciation and form. Then resume reading. |
| **Ruling** | Permissible for educational purposes only. Not a natural reading practice. |
| **Examples** | Teacher requests stop on a word with Ta Marbuta to test if the student converts it to Ha. |

### 2.3 Waqf Idtirari (الوقف الاضطراري)
مضطر لعطاس أو ضيق النفس أو السعال أو النسيان، وغير ذلك.

**Occurs when:** The reciter is forced to stop due to an external cause (shortness of breath, coughing, sneezing, forgetting).

| Feature | Description |
| --- | --- |
| **How to Identify** | The reciter stops unexpectedly at any word due to a physical or external cause. |
| **Performance** | يجوز الوقف في أي موضع عند الضرورة، ثم يعود القارئ للبدء من كلمة تسبق موضع الوقف ليصل الكلام ببعضه ويستقيم المعنى، إلا إذا كان الوقف على كلمة الابتداء بما بعدها حسن. |
| **Ruling** | Permissible at any position when forced. The reciter must go back and restart from a point where the meaning connects properly. |
| **Examples** | Any word where the reciter runs out of breath. |

### 2.4 Waqf Ikhtiyari (الوقف الاختياري)
وقوف القارئ بإرادته، بدون أسباب خارجة. **وهو أربعة أنواع:**

**Definition:** أن يقف القارئ باختياره وإرادته. The reciter chooses to stop at a specific point. This type is subdivided into four levels based on the completeness of meaning and syntactic/semantic dependency.

| # | Rule | Arabic | Description | Mushaf Symbol | Count | % |
|---|------|--------|-------------|:-------------:|------:|:---:|
| **—** | **Waqf Ikhtiyari** | **الوقف الاختياري** | **—** | **—** | **—** | **100%** |
| 1a | Waqf Tamm | الوقف التام | الوقف على ما تم معناه ولم يتعلق بما بعده لا لفظاً ولا معنى | — | — | — |
| 1b | Waqf Tamm Muqayyad / Lazim | وقف تام مقيد / لازم | تم المعنى للوقف، وإذا وصل يفسد المعنى | **مـ** | 21 | 0.5% |
| 1c | Waqf Tamm Mutlaq | وقف تام مطلق | تم المعنى للوقف، وإذا وصل لا يُفسد المعنى | **قلى** | 511 | 12.0% |
| 2 | Waqf Kaafi | الوقف الكافي | الوقف على ما تم معناه، وتعلق بما بعده في المعنى دون اللفظ | **ج** | 2,083 | 48.8% |
| 3 | Waqf Hasan | الوقف الحسن | الوقف على ما تم معناه، وتعلق بما بعده لفظاً ومعنى | **صلى** | 1,651 | 38.6% |
| 4 | Waqf Qabih | الوقف القبيح | الوقف على ما لم يتم معناه، لشدة تعلقه بما بعده لفظاً ومعنى | **—** | **—** | **—** |

#### 2.4.1 Waqf Tamm (الوقف التام)
الوقف على ما تم معناه **ولم يتعلق بما بعده لا لفظاً ولا معنى**، ويكون دائماً في نهاية القصص، أو آخر السور ورؤوس الآيات.

**Occurs when:** The meaning is fully complete, with no dependency on what follows in either syntax (i'rab) or meaning. Typically at the end of a Surah, end of a verse, end of a story, or transition between topics (e.g., from Jannah to Nar).

| Feature | Description |
| --- | --- | 
| **How to Identify** | End of a Surah, end of a story, or end of a complete topic. No syntactic or semantic connection to what follows. |
| **Performance** | Stop and breathe. Start the next phrase independently. |
| **Ruling** | Best type of stop. يحسن الوقف عليه والابتداء بما بعده. Encouraged (Mustahabb). |
| **Examples** | الوقف على **ٱلۡمُفۡلِحُونَ (2:5:end)** في سورة البقرة، والوقف على **لِلۡكَٰفِرِينَ (2:24:end)** قبل بدء الحديث عن الجنة. |

##### 2.4.1b Waqf Tamm Muqayyad / Lazim (وقف تام مقيد / لازم — مـ)

تم المعنى للوقف، **وإذا وصل يفسد المعنى**. هو نوع فرعي من التام، يلزم الوقف عليه لأن الوصل يوهم معنى غير مراد.

| Feature | Description |
| --- | --- |
| **How to Identify** | Continuing without stopping would create an unintended meaning or attribution. Marked with **(مـ)** (`U+06D8` — ۘ) in the Mushaf. |
| **Mushaf Symbol** | **مـ** |
| **Ruling** | Obligatory stop. Continuing is considered a form of Waqf Qabih (ugly reading). |
| **Example** | إِنَّمَا يَسۡتَجِيبُ ٱلَّذِينَ يَسۡمَعُونَۘ وَٱلۡمَوۡتَىٰ يَبۡعَثُهُمُ ٱللَّهُ ثُمَّ إِلَيۡهِ يُرۡجَعُونَ (6:36) - **Stop on (يَسۡمَعُونَ)**|

##### 2.4.1c Waqf Tamm Mutlaq (وقف تام مطلق — قلى)

تم المعنى للوقف، **وإذا وصل لا يُفسد المعنى**.

| Feature | Description |
| --- | --- |
| **How to Identify** | The meaning is complete and stopping is preferred, but continuing does not distort the meaning. Marked with **(قلى)** (`U+06D7` — ۗ) in the Mushaf. |
| **Mushaf Symbol** | **قلى** |
| **Ruling** | Stopping is preferred (Awla) but continuing is permissible. |
| **Example** | قَالُوٓاْ أَنُؤۡمِنُ كَمَآ ءَامَنَ ٱلسُّفَهَآءُ (2:13) - **Stop on (ٱلسُّفَهَآءُ)** |

#### 2.4.2 Waqf Kaafi (الوقف الكافي — ج)
الوقف على ما تم معناه، **وتعلق بما بعده في المعنى دون اللفظ**. (المعنى تم، وإذا وصل لا بأس، لأن الحكم العام مازال قائماً).

**Occurs when:** The meaning is understandable and complete, but a semantic (not syntactic) connection exists with what follows.

| Feature | Description |
| --- | --- |
| **How to Identify** | Meaning is complete. There is a semantic relationship with the continuation, but no syntactic dependency (i'rab). Marked with **(ج)** (`U+06DA` — ۚ) in the Mushaf. |
| **Mushaf Symbol** | **ج** |
| **Performance** | Stop and breathe. Starting from the stopped point or the next is both acceptable. يحسن الوقف عليه ويحسن الابتداء بما بعده. |
| **Ruling** | Permissible and common. |
| **Examples** |ٞ يَجۡعَلُونَ أَصَٰبِعَهُمۡ فِيٓ ءَاذَانِهِم مِّنَ ٱلصَّوَٰعِقِ حَذَرَ ٱلۡمَوۡتِۚ (2:19) - **Stop on (ٱلۡمَوۡتِۚ)** |

#### 2.4.3 Waqf Hasan (الوقف الحسن — صلى)
الوقف على ما تم معناه، **وتعلق بما بعده لفظاً ومعنى**. (ويكون أحياناً رأس آية).

**Occurs when:** A reasonable meaning is conveyed, but both syntax (i'rab) and meaning depend on what follows.

| Feature | Description |
| --- | --- |
| **How to Identify** | Gives a good partial meaning, but is linked to the next words both syntactically and semantically. Marked with **(صلى)** (`U+06D6` — ۖ) in the Mushaf. |
| **Mushaf Symbol** | **صلى** |
| **Performance** | يحسن الوقف عليه لإفادته المعنى، لكن **لا يحسن الابتداء بما بعده** إلا إذا كان على **رأس آية** اتباعاً للسنة. If stopping mid-verse, it is better to repeat this word when continuing. |
| **Ruling** | Permissible but less preferred. Starting from the next word is only acceptable if it is the head of a verse (رأس آية). |
| **Examples** | الوقف على (الْحَمْدُ للّهِ) جائز، لكن لا يبتدأ بـ (رب العالمين) إلا وصلاً، بينما يجوز الوقف على (الْعَالَمِينَ) والبدء بـ (الرحمن الرحيم) لأنها رأس آية.<br>يَكَادُ ٱلۡبَرۡقُ يَخۡطَفُ أَبۡصَٰرَهُمۡ (2:20) - **Stop on (أَبۡصَٰرَهُمۡ)** |

#### 2.4.4 Waqf Qabih (الوقف القبيح — لا)
الوقف على ما لم يتم معناه، **لشدة تعلقه بما بعده لفظاً ومعنى**. (كأن يقف على المبتدأ دون الخبر، والفعل دون الفاعل).

**Occurs when:** Stopping leads to an incomplete or misleading meaning, or implies something contrary to the intended divine meaning.

| Feature | Description |
| --- | --- |
| **How to Identify** | The phrase is incomplete or creates a distorted, disrespectful, or heretical meaning on its own. |
| **Mushaf Symbol** | None |
| **Performance** | لا يجوز تعمده إلا لضرورة، وإذا وقف يعيد ما قبله. Do not stop intentionally. If forced (e.g., out of breath), resume from before the stop point. |
| **Ruling** | Forbidden (Haram) if intentional. Forgiven if by necessity (e.g., out of breath, coughing). |
| **Examples** | إِنَّمَا يَسْتَجِيبُ الَّذِينَ يَسْمَعُونَ وَالْمَوْتَىٰ يَبْعَثُهُمُ اللَّهُ (6:36) - **Stop on (وَالْمَوْتَىٰ)** |
---

### 2.5 Phonetic Effects at Stop (التأثيرات الصوتية عند الوقف)

#### Scope

This section covers the phonetic phenomena that occur when stopping on the last letter of a word in Hafs 'an 'Asim. The golden rule: **"لا يوقف على متحرك بحركة كاملة"** — No word is stopped upon with a full vowel.


| # | Rule | Arabic | Description |
|---|------|--------|-------------|
| **—** | **Phonetic Effects at Stop** | **التأثيرات الصوتية عند الوقف** | |
| 1 | Sukoon 'Arid | السكون العارض | Placing temporary Sukoon on the last letter |
| 2 | Madd 'Iwad | مد العوض | Substituting Tanween Fatha with an Alif |
| 3 | Rawm | الروم | Partially pronouncing the vowel upon stopping |
| 4 | Ishmaam | الإشمام | Lip rounding to indicate Damma without sound |
| 5 | Ha' as-Sakt | هاء السكت | Appending a silent Ha upon stopping |
| 6 | Qalqalah | القلقلة | Vibration in the articulation point upon stopping |
| 7 | Hams | الهمس | Flow of breath (whispering) upon stopping |
| 8 | Istitaalah | الاستطالة | Extending the sound in the articulation point |
| 9 | Nabr | النبر | Pressure on doubled letters upon stopping |
| 10 | Madd 'Arid & Leen | المد العارض واللين | Prolonging Madd at stop |
| 11 | The 7 Alifs | الألفات السبع | Pronouncing silent Alifs when stopping |
| 12 | Noon/Tanween Rules | أحكام النون الساكنة والتنوين | Idgham, Iqlab, and Ikhfaa are cancelled |
| 13 | Meem Sakinah Rules | أحكام الميم الساكنة | Ikhfaa Shafawi and Idgham Shafawi are cancelled |
| 14 | Madd Munfasil | المد المنفصل | Reverts to Madd Tabee'i|
| 15 | Madd Silah | مد الصلة | Stopped with silent Ha |
| 16 | Omitted Madd | المد المحذوف | Original Madd restored when stopping |
| 17 | Shadda 'Aridah | الشدة العارضة | Word started without emphasis |

#### Sukoon 'Arid (السكون العارض)
تسكين آخر الكلمة عند الوقف عليها. السكون المحض: عند الوقف على كلمة تنتهي بحركة، يتم تحويل الحركة إلى سكون.

**Occurs when:** The reciter stops on any word ending with a voweled letter.

**Technical Detection:**
*   **Unicode Pattern:** Any final letter with a vowel mark (`U+064E` Fatha, `U+064F` Damma, `U+0650` Kasra) — the vowel is ignored at stop.
*   **Visual:** No visual change in the Mushaf. The written vowel remains but is dropped in pronunciation.

| Feature | Description |
| --- | --- |
| **How to Identify** | Any voweled letter at the end of a word when the reciter chooses to stop. |
| **Performance** | Remove the vowel and pronounce the letter with Sukoon. |
| **Related Madd** | Enables Madd 'Arid lil-Sukoon (2, 4, or 6 counts) if preceded by a Madd letter. المد العارض للسكون ينشأ غالباً بسبب الوقف بالسكون. |
| **Examples** | نَسۡتَعِينُ ← **نَسۡتَعِينْ** <br> (المُنكَرِ) ← **المنكَرْ** <br> (الأمورُ) ← **الأمورْ** <br> (العذابَ) ← **العذابْ** <br> (عليمٌ) ← **عليمْ** <br> (من خيرٍ) ← **من خيرْ** |

#### Rawm (الروم)
الإتيان ببعض الحركة (نحو الثلث) عند الوقف. يجوز الإتيان ببعض الحركة (روم).

**Occurs when:** Stopping on a letter with Damma or Kasra. **Not applicable** to Fatha.

**Technical Detection:**
*   **Unicode Pattern:** Performance-level rule. Applies to any final letter with `U+064F` (Damma) or `U+0650` (Kasra).
*   **Visual:** No visual change in the Mushaf; it is a performance-level rule.

| Feature | Description |
| --- | --- |
| **Applicable Vowels** | Damma (ضمة) and Kasra (كسرة) only. **Not Fatha.** |
| **Performance** | Reduce the vowel to approximately one-third of its full sound. |
| **Effect on Madd** | If Rawm is applied, Madd 'Arid lil-Sukoon is shortened to 2 counts only. |
| **Who Perceives It** | Can be heard by someone close but not by someone distant. يسمعه القريب دون البعيد. |
| **Examples** | نَسۡتَعِينُ → نَسۡتَعِينُ̊ (partial Damma, approx. one-third). |

#### Ishmaam (الإشمام)
ضم الشفتين بعد تسكين الحرف الأخير إشارةً إلى الضمة دون صوت.

**Occurs when:** Stopping on a letter with Damma only. **Not applicable** to Fatha or Kasra.

**Technical Detection:**
*   **Unicode Pattern:** Performance-level rule. Applies to any final letter with `U+064F` (Damma) only.
*   **Visual:** The Mushaf text visually remains unchanged upon Waqf; it is a performance-level rule (lip movement only).

| Feature | Description |
| --- | --- |
| **Applicable Vowels** | Damma (ضمة) only. **Not Fatha or Kasra.** |
| **Performance** | After pronouncing the letter with Sukoon, round the lips as if about to say Damma. No sound is produced. |
| **Effect on Madd** | If Ishmaam is applied, Madd 'Arid lil-Sukoon follows the standard stop rules (2, 4, or 6 counts). |
| **Who Perceives It** | Can be seen by someone watching the lips but not heard. يراه القريب ولا يسمعه. |
| **Examples** | نَسۡتَعِينُ → نَسۡتَعِينْ + lip rounding (visual Damma indication). |

#### Ha' as-Sakt (هاء السكت)
هاء ساكنة تلحق آخر الكلمة عند الوقف فاذا وصلت تسقط.

**Occurs when:** Specific words are stopped upon, typically words ending in a short vowel that would otherwise be lost.

**Technical Detection:**
*   **Unicode Pattern:** `U+0647` (Ha) + `U+06E1` (Small High Dotless Head of Khah) — appearing as (هۡ) at word end.
*   **Visual:** A small Ha (هۡ) is permanently written at the end of certain words in the Mushaf.

| Feature | Description |
| --- | --- |
| **How to Identify** | Specific words listed in Hafs narration (e.g., words ending in Yaa or voweled Ha). |
| **Performance** | Append a silent Ha (هْ) after the last letter when stopping. |
| **Mandatory Cases** | Obligatory in Hafs: مَالِيَهۡ (69:28)، كِتَٰبِيَهۡ (69:25)، حِسَابِيَهۡ (69:26)، سُلۡطَٰنِيَهۡ (69:29). |
| **Optional Cases** | Some cases allow both stopping with or without Ha' as-Sakt. |
| **Examples** | مَالِيَهۡ (69:28) — Stop: "maaliyah"; كِتَٰبِيَهۡ (69:25) — Stop: "kitaabiyah". |

#### Madd 'Iwad (مد العوض)
يُبدل التنوين المفتوح ألفاً تمد بمقدار حركتين.

**Occurs when:** Stopping on a word ending with Tanween Fatha.

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with a letter bearing Tanween Fatha. |
| **Performance** | The Tanween sound is dropped and replaced with an Alif prolonged for 2 counts. |
| **Tafkheem/Tarqeeq** | The Alif follows the letter before it in heaviness/lightness (e.g., heavy in زهوقاً, light in حسيباً). |
| **Exception** | If the word ends in Ta Marbuta (ةً), stop with a silent Ha instead (e.g., بغتةً ← بغتهْ). |
| **Examples** | (حسيباً) ← **حسيبَا** <br> (مُسمّىً) ← **مسمّا** |

#### Qalqalah upon Stop (القلقلة عند الوقف)
الإتيان باهتزاز في المخرج عند الوقف على حروف (ق، ط، ب، ج، د).

**Occurs when:** Stopping on a letter of Qalqalah.

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with (ق، ط، ب، ج، د) which becomes Sakin at stop. |
| **Performance** | Vibration in the articulation point. |
| **Levels at Stop** | **Kubra (Major):** If the letter is Mushaddad (naturally doubled).<br>**Wusta (Medium):** If the letter is un-Mushaddad. |
| **Examples** | **Kubra:** (وتَبَّ) <br> **Wusta:** (كسَبَ)، (لهَبٍ)، (حطَبِ) |

#### Hams upon Stop (الهمس عند الوقف)
يجب جريان النفس عند الوقف على أي من حروف الهمس (فحثه شخص سكت).

**Occurs when:** Stopping on one of the Hams letters.

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with a Hams letter which becomes Sakin at stop. |
| **Performance** | Flow of breath (whispering) must clearly occur upon stopping. |
| **Examples** | الهاء في (بِهِ) ← **بِهْ** <br> (القسمةَ) ← **القسمهْ** |

#### Istitaalah upon Stop (الاستطالة عند الوقف)
الوقف بصفة **الاستطالة** (امتداد الصوت في المخرج من حافة اللسان).

**Occurs when:** Stopping on the letter Daad (ض).

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with the letter Daad (ض). |
| **Performance** | Extending the sound in the articulation point from the edge of the tongue. |
| **Cautions** | Avoid touching the tips of the upper incisors (to prevent sounding like ظ) or the roots (to prevent bouncing like a qalqalah د). |
| **Examples** | (الأرض) |

#### Nabr on Shaddah (النبر على الحرف المشدد)
الوقف بالسكون مع **النبر** (الضغط على الحرف) لتوضيح الشدة.

**Occurs when:** Stopping on a word ending with a Shaddah.

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with a doubled letter (Shaddah). |
| **Performance** | Stop with Sukoon and Nabr (pressure) to clarify the Shaddah. |
| **Exception** | If the letter is Noon or Meem, stop with Ghunnah Akmal Ma Takoon instead of mere Nabr. |
| **Examples** | (إليَّ) ← **إليْ** (مع نبر) <br> (وليٍّ) ← **وليْ** (مع نبر) <br> **Ghunnah:** (ثُمَّ) ← **ثُمْ~** |

#### Madd 'Arid Lil-Sukun & Leen (المد العارض للسكون ولين الوقف)
إطالة الصوت بحرف المد أو اللين عند الوقف بالسكون العارض.

**Occurs when:** The letter before the last is a Madd or Leen letter, and the reciter stops on the last letter.

| Feature | Description |
| --- | --- |
| **Madd 'Arid** | A Madd letter before the last letter. Prolonged **(2, 4, or 6 counts)**. e.g., (مبلسون), (مبين), (الله). |
| **Madd Leen** | A Leen letter (و، ي) with Fatha before it, before the last letter. Prolonged **(2, 4, or 6 counts)**. e.g., (قريش), (خوف). |
| **Exception (Leen)**| If the Leen letter is the very last letter, stop with Sukoon only (no madd). e.g., (وتواصوْا). |

#### The Seven Alifs (الألفات السبع)
تثبت الألف وقفاً وتسقط وصلاً.

**Occurs when:** Stopping on one of the specific 7 words ending in an Alif with a rectangular zero.

| Feature | Description |
| --- | --- |
| **How to Identify** | Words ending in Alif with a rectangular zero (صفر مستطيل). |
| **Performance** | Pronounced as a normal Alif (2 harakat) upon stopping, but dropped entirely when connecting. |
| **The 7 Words** | أَنَا۠(18:34)، لَّٰكِنَّا۠(18:38)، ٱلظُّنُونَا۠(33:10)، ٱلرَّسُولَا۠(33:66)، ٱلسَّبِيلَا۠ (33:67)، سَلَٰسِلَاْ(76:4)، قَوَارِيرَا۠ (76:15). |
| **Examples** | (الرسولا) ← وصلاً: **الرسولَ** <br> وقفاً: **الرسولا** |

#### Cancellation of Noon Sakinah / Tanween Rules (إلغاء أحكام النون الساكنة والتنوين)
تلغى أحكام الإدغام والإقلاب والإخفاء عند الوقف على النون الساكنة أو التنوين.

**Occurs when:** Stopping on a word that ends with Noon Sakinah or Tanween that would normally connect to the next word with a Tajweed rule.

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with Noon Sakinah or Tanween. |
| **Performance** | The connection to the next letter is broken. **Rule Removed:** Idgham, Iqlab, and Ikhfaa are cancelled. Noon reverts to Izhaar with Sukoon. |
| **Examples** | **Idgham:** (مَن يَقُولُ) (2:8:3) ← وقفاً: **مَنۡ** <br> **Ikhfaa:** (مِن ثَمَرَةٖ) (2:25:16) ← وقفاً: **مِنۡ** <br> **Iqlab:** (مِنۢ بَعۡد) (2:27:5) ← وقفاً: **مِنۡ** <br> **Tanween:** (غَفُورٞ رَّحِيم) (2:173:24) ← وقفاً: **غَفُورْ** |

#### Cancellation of Meem Sakinah Rules (إلغاء أحكام الميم الساكنة)
تلغى أحكام الإخفاء الشفوي والإدغام الشفوي عند الوقف على الميم الساكنة.

**Occurs when:** Stopping on a word that ends with Meem Sakinah which normally connects to the next word with a rule.

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with Meem Sakinah. |
| **Performance** | The connection to the next letter is broken. **Rule Removed:** Ikhfaa Shafawi and Idgham Shafawi are cancelled. Meem reverts to Izhaar with Sukoon. |
| **Examples** | **Ikhfaa Shafawi:** (تَرۡمِيهِم بِحِجَارَةٖ) (105:4:1) ← وقفاً: **تَرۡمِيهِمۡ** <br> **Idgham Shafawi:** (لَهُم مَّا يَشَآءُونَ) (39:34:1) ← وقفاً: **لَهُمۡ** |

#### Removal of Madd Munfasil (سقوط المد المنفصل)
يعود المد المنفصل إلى مد طبيعي عند الوقف لزوال السبب (الهمز).

**Occurs when:** Stopping on a word ending with a Madd letter, where the next word begins with Hamza.

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with a Madd letter followed by a Hamza in the next word. |
| **Performance** | The connection between words is broken. **Madd Removed:** Reverts to Madd Tabee'i (2 counts). |
| **Examples** | (يؤمنوا) |

#### Removal of Madd Silah (سقوط مد الصلة)
يسقط مد الصلة (الكبرى والصغرى) عند الوقف على هاء الضمير.

**Occurs when:** Stopping on a word ending with Ha' Dhamir (هاء الضمير) that has Madd Silah.

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with a voweled Ha' (ه) with a Silah sign. |
| **Performance** | The connection between words is broken. **Madd Removed:** Stopped with a silent Ha. |
| **Examples** | (بِهِ) ← **بِهْ** |

#### Restoration of Omitted Madd (إثبات المد المحذوف لالتقاء الساكنين)
يثبت حرف المد المحذوف وصلاً للتخلص من التقاء الساكنين، وذلك عند الوقف.

**Occurs when:** Stopping on a word that ends with a Madd letter which is dropped in continuous reading (Ilteqa Sakinain).

| Feature | Description |
| --- | --- |
| **How to Identify** | Word ends with a Madd letter, followed by a Sakin letter in the next word. |
| **Performance** | Dropped Madd letter due to next Sakin letter. **Madd Restored:** Original Madd (2 counts) restored at stop. |
| **Examples** | • **Yaa:** (فِي السَّمَاءِ) ← stop on **(فِي)** <br>• **Alif:** (وَقَالَا الْحَمْدُ) ← stop on **(وَقَالَا)** <br>• **Waw:** (قَالُوا الْحَمْدُ) ← stop on **(قَالُوا)** <br>• **Yaa:** (حَاضِرِي الْمَسْجِدِ) ← stop on **(حَاضِرِي)** |

#### Removal of Shadda 'Aridah (سقوط الشدة العارضة)
تسقط الشدة العارضة الناتجة عن الوصل عند الابتداء بالكلمة.

**Occurs when:** Starting on a word that had a temporary Shadda due to the previous word.

| Feature | Description |
| --- | --- |
| **How to Identify** | Start of Word has a temporary Shadda due to a previous word's Tajweed rule (e.g. Idgham). |
| **Performance** | If stopping on the preceding word, **Shadda Removed.** The word must be started without emphasis. |
| **Examples** | (مِن مَّالٖ) (23:44:5) ← ابتداءً بالثانية: **مَالٖ** <br> (مِن نُّطۡفَةٖ) (16:13:3) ← ابتداءً: **نُطۡفَةٖ** |

---

### 2.6 Special Stop Cases — Rasm (أحكام الوقف الخاصة بالرسم القرآني)

#### Scope

This section covers the detailed rules for stopping on specific words that follow special Quranic orthography (Rasm) rules. These rules affect how words are pronounced at stop.


| # | Rule | Arabic | Description |
|---|------|--------|-------------|
| **—** | **Special Stop Cases (Rasm)** | **أحكام الوقف الخاصة بالرسم** | |
| 1 | Ta Marbuta / Mabsuta | الوقف على تاء التأنيث | Stop behavior depends on whether the Ta is round (ة) or extended (ت) |
| 2 | Maqtu' wal-Mawsul | المقطوع والموصول | Affects whether words can be separated at stop |
| 3 | Special Words | كلمات مفردة | Unique words with specific stop pronunciation |

#### Ta Marbuta / Mabsuta (الوقف على تاء التأنيث)
يتغير نطق تاء التأنيث عند الوقف عليها بحسب رسمها (مبسوطة أم مربوطة).

**Rule:** The pronunciation of the feminine Ta changes at stop depending on its written form in the Rasm.

##### Ta Marbuta (التاء المربوطة — ة)

| Feature | Description |
| --- | --- |
| **Stop Behavior** | تنقلب عند الوقف إلى **"هاء ساكنة" مهموسة**. Converts to a silent, whispered Ha (هْ) when stopping. |
| **Examples** | رَحْمَةٌ → **(رَحْمَهْ)** at stop. <br> (القسمةَ) → **(القسمهْ)** <br> (بآيةٍ) → **(بآيهْ)** |

##### Ta Mabsuta (التاء المبسوطة — ت)

| Feature | Description |
| --- | --- |
| **Stop Behavior** | يوقف عليها **بالتاء الساكنة** كما هي. Stopped upon with a silent Ta (تْ) as written. |
| **Ruling** | هذه التاء المبسوطة لابد ان تأتي مضافة بعدها مضاف اليه دائما. This open Ta must always come as a *Mudaf* (annexed), followed by a *Mudaf Ilayh* (genitive). These specific words are written with Ta Mabsuta in the Uthmani Rasm and must be memorized. |

| Word | Arabic | Ref | Example |
| --- | --- | --- | --- |
| **Rahmat** | رَحْمَت | Az-Zukhruf (43:32) | أَهُمْ يَقْسِمُونَ رَحْمَتَ رَبِّكَ |
| **Rahmat** | رَحْمَت | Az-Zukhruf (43:32) | وَرَحْمَتُ رَبِّكَ خَيْرٌ مِّمَّا يَجْمَعُونَ |
| **Rahmat** | رَحْمَت | Al-A'raf (7:56) | إِنَّ رَحْمَتَ اللَّهِ قَرِيبٌ مِّنَ الْمُحْسِنِينَ |
| **Rahmat** | رَحْمَت | Ar-Rum (30:50) | فَانظُرْ إِلَى آثَارِ رَحْمَتِ اللَّهِ |
| **Rahmat** | رَحْمَت | Hud (11:73) | رَحْمَتُ اللَّهِ وَبَرَكَاتُهُ عَلَيْكُمْ أَهْلَ الْبَيْتِ |
| **Rahmat** | رَحْمَت | Maryam (19:2) | ذِكْرُ رَحْمَتِ رَبِّكَ عَبْدَهُ زَكَرِيَّا |
| **Rahmat** | رَحْمَت | Al-Baqarah (2:218) | أُولَٰئِكَ يَرْجُونَ رَحْمَتَ اللَّهِ |
| **Ni'mat** | نِعْمَت | Al-Baqarah (2:231) | وَاذْكُرُوا نِعْمَتَ اللَّهِ عَلَيْكُمْ (الموضع الأخير بالبقرة) |
| **Ni'mat** | نِعْمَت | An-Nahl (16:72) | وَبِنِعْمَتِ اللَّهِ هُمْ يَكْفُرُونَ |
| **Ni'mat** | نِعْمَت | An-Nahl (16:83) | يَعْرِفُونَ نِعْمَتَ اللَّهِ ثُمَّ يُنكِرُونَهَا |
| **Ni'mat** | نِعْمَت | An-Nahl (16:114) | وَاشْكُرُوا نِعْمَتَ اللَّهِ إِن كُنتُمْ إِيَّاهُ تَعْبُدُونَ |
| **Ni'mat** | نِعْمَت | Ibrahim (14:28) | أَلَمْ تَرَ إِلَى الَّذِينَ بَدَّلُوا نِعْمَتَ اللَّهِ كُفْرًا |
| **Ni'mat** | نِعْمَت | Ibrahim (14:34) | وَإِن تَعُدُّوا نِعْمَتَ اللَّهِ لَا تُحْصُوهَا |
| **Ni'mat** | نِعْمَت | Al-Ma'idah (5:11) | اذْكُرُوا نِعْمَتَ اللَّهِ عَلَيْكُمْ إِذْ هَمَّ قَوْمٌ (عقود الثاني) |
| **Ni'mat** | نِعْمَت | Luqman (31:31) | تَجْرِي فِي الْبَحْرِ بِنِعْمَتِ اللَّهِ |
| **Ni'mat** | نِعْمَت | Fatir (35:3) | يَا أَيُّهَا النَّاسُ اذْكُرُوا نِعْمَتَ اللَّهِ عَلَيْكُمْ |
| **Ni'mat** | نِعْمَت | At-Tur (52:29) | فَمَا أَنتَ بِنِعْمَتِ رَبِّكَ بِكَاهِنٍ وَلَا مَجْنُونٍ |
| **Ni'mat** | نِعْمَت | Ali 'Imran (3:103) | وَاذْكُرُوا نِعْمَتَ اللَّهِ عَلَيْكُمْ إِذْ كُنتُمْ أَعْدَاءً |
| **La'nat** | لَعْنَت | Ali 'Imran (3:61) | فَنَجْعَل لَّعْنَتَ اللَّهِ عَلَى الْكَاذِبِينَ |
| **La'nat** | لَعْنَت | An-Nur (24:7) | أَنَّ لَعْنَتَ اللَّهِ عَلَيْهِ إِن كَانَ مِنَ الْكَاذِبِينَ |
| **Imra'at** | امْرَأَت | Yusuf (12:30, 51) | امْرَأَتُ الْعَزِيزِ (وردت في موضعين بالسورة) |
| **Imra'at** | امْرَأَت | Ali 'Imran (3:35) | إِذْ قَالَتِ امْرَأَتُ عِمْرَانَ |
| **Imra'at** | امْرَأَت | Al-Qasas (28:9) | وَقَالَتِ امْرَأَتُ فِرْعَوْنَ قُرَّتُ عَيْنٍ لِّي وَلَكَ |
| **Imra'at** | امْرَأَت | At-Tahrim (66:10) | امْرَأَتَ نُوحٍ، وَامْرَأَتَ لُوطٍ |
| **Imra'at** | امْرَأَت | At-Tahrim (66:11) | امْرَأَتَ فِرْعَوْنَ |
| **Ma'siyat** | مَعْصِيَت | Al-Mujadilah (58:8, 9) | وَمَعْصِيَتِ الرَّسُولِ (موضعان في السورة) |
| **Shajarat** | شَجَرَت | Ad-Dukhan (44:43) | إِنَّ شَجَرَتَ الزَّقُومِ |
| **Sunnat** | سُنَّت | Fatir (35:43) | سُنَّتَ الْأَوَّلِينَ، لِسُنَّتِ اللَّهِ، وَلَن تَجِدَ لِسُنَّتِ اللَّهِ |
| **Sunnat** | سُنَّت | Al-Anfal (8:38) | فَقَدْ مَضَتْ سُنَّتُ الْأَوَّلِينَ |
| **Sunnat** | سُنَّت | Ghafir (40:85) | سُنَّتَ اللَّهِ الَّتِي قَدْ خَلَتْ فِي عِبَادِهِ |
| **Qurrat** | قُرَّت | Al-Qasas (28:9) | قُرَّتُ عَيْنٍ لِّي وَلَكَ |
| **Jannat** | جَنَّت | Al-Waqi'ah (56:89) | فَرَوْحٌ وَرَيْحَانٌ وَجَنَّتُ نَعِيمٍ |
| **Fitrat** | فِطْرَت | Ar-Rum (30:30) | فِطْرَتَ اللَّهِ الَّتِي فَطَرَ النَّاسَ عَلَيْهَا |
| **Baqiyyat** | بَقِيَّت | Hud (11:86) | بَقِيَّتُ اللَّهِ خَيْرٌ لَّكُمْ |
| **Ibnat** | ابْنَت | At-Tahrim (66:12) | وَمَرْيَمَ ابْنَتَ عِمْرَانَ |
| **Kalimat** | كَلِمَت | Al-A'raf (7:137) | وَتَمَّتْ كَلِمَتُ رَبِّكَ الْحُسْنَىٰ (أوسط الأعراف) |
| **Others** | أخرى | - | بَيِّنَتٖ، غيابت، جمالت |

#### Maqtu' wal-Mawsul (المقطوع والموصول)
تأثيره: يؤثر على إمكانية فصل الكلمات، فلا يوقف على الكلمة الأولى إذا كانت موصولة.

**Rule:** Whether a word is written as one unit (Mawsul) or two separate units (Maqtu') in the Rasm affects where the reciter can stop.

| Type | Rule | Examples |
| --- | --- | --- |
| **Mawsul (الموصول)** | يجب الوقف على الثانية (المتصلة). Must stop on the combined word, not the first part. | (لِئَلاَّ)، (بِئْسَمَا)، (وَأَلَّوِ)، **(يَبْنَؤُمَّ)**، **(يَوْمَهُمْ)** |
| **Maqtu' (المقطوع)** | يجوز الوقف اضطراراً على الأولى. May stop on the first word if forced. | (أَن لَّا): يجوز الوقف على "أن" <br> **(أَيَّمَا تَدْعُوا)**: can stop on أَيًّا <br> **(وَلاتَ حِينَ)**: stop on وَلاتْ <br> **(قَالَ ابْنَ أُمَّ)** |
| **Special Cases** | حالات خاصة | **(إِلْ يَاسِينَ)**: cannot stop on آل <br> **(كَالُوهُمْ/وَزَنُوهُمْ)**: stop on Meem <br> Note: **(يَا)** (Vocative/النداء) and **(هَا)** (Alerting/التنبيه) cannot be stopped on independently because they are connected in the Uthmani Rasm to the following word.<br> • **(يَا)** is joined in words like: (يَأَيُّهَا ، يَآدَمُ ، يَنُوحُ ، يَمَرْيَمُ ، يَبَنِي ، يَقَوْمِ ، يَأَهْلَ)<br> • **(هَا)** is joined in words like: (هَأَنتُمْ ، هَؤُلاءِ ، هَذَا ، هَذِهِ ، هَذَانِ) |

#### الحروف المحذوفة رسماً وما يشابهها

##### Words Ending in Deleted Alif (الألف المحذوفة)

| Description | Arabic | Example / Rule |
| --- | --- | --- |
| **Word Ayyuh (أَيُّه)** | الأصل الوقف عليها بالألف (أَيُّهَا). | في 3 مواضع رسمت بدون ألف فيوقف عليها بالهاء الساكنة: (أَيُّهَ الْمُؤْمِنُونَ)، (يَا أَيُّهَ السَّاحِرُ)، (أَيُّهَ الثَّقَلَانِ). |
| **Interrogative Ma (ما الاستفهام)** | المسبوقة بحرف جر. | Prepositions attached to this (e.g., فِيمَ, بِمَ, مِمَّ) stop with Sukoon on Meem and no Alif. |
| **Light Noon of Emphasis** | نون التوكيد الخفيفة. | Stopped on with Alif (Madd Iwad): وَلَيَكُونًا → (وليكونا)، لَنَسْفَعًا → (لنسفعا). |

##### Words Ending in Deleted Waw (الواو المحذوفة)
Words drawn without the final Waw are stopped upon with **Sukoon** and no Waw: (وَيَدْعْ، يَمْحْ، يوم يَدْعْ، سَنَدْعْ، وصَالِحْ).

##### Words Ending in Deleted Yaa (الياء المحذوفة)
Words drawn without the final Yaa are stopped by dropping the Yaa and applying **Sukoon** to the preceding letter: (بِهَادْ، يُرِدْنْ، صَالْ، فَمَا تُغْنْ، الْجَوَارْ، يُؤْتْ، وَاخْشَوْنْ، نُنْجْ، بِالْوَادْ، يُنَادْ، لَهَادْ).

**The "Two Yaas" Exception (Ibn Al-Jazari):**
Words drawn with one Yaa structurally but stopped on with two Yaas: (لا يَسْتَحْيِي، يُحْيِي، لَمُحْيِي الْمَوْتَى).

##### Hamzas Drawn on Yaa/Waw (الهمزة المتطرفة على واو أو ياء)
The carrier letter is ignored and the stop is on a static Hamza (Sukoon).
* **Yaa Carrier:** (مِنْ وَرَاءِ) → (وَرَاءْ), (تِلْقَاءِ), (إِيتَاءِ).
* **Waw Carrier:** (جَزَاءُ) → (جَزَاءْ), (تَفْتَأُ), (شُرَكَاءُ).

##### Word: مالِ (Maal)

| Feature | Description |
| --- | --- |
| **Rasm** | رسمت اللام الجارة مفصولة في 4 مواضع. The prepositional Lam is written separated from what follows in 4 positions. |
| **Stop Rule** | فيجوز الوقف على اللام (اختباراً). Stopping on the Lam is permitted (for testing purposes). |
| **Example** | فَمَالِ هَـؤُلاء الْقَوْمِ |

### 2.7 Breathless Pauses (السكتات الواجبة والجائزة)

**السكت (Sakt):** Cutting the sound for a short time without taking a breath. It is normally performed to preserve meaning or as a specific narration rule.

#### Mandatory Saktas (سكتات واجبة)
There are 4 obligatory spots in Hafs 'an 'Asim (via Shatibiyyah) during continuation (Wasl). Note: These are obligatory only if the reciter continues (connecting words). An actual breathing stop (Waqf) is allowed at these positions as an alternative.

| Surah (Verse) | Position | Note |
| --- | --- | --- |
| **Al-Kahf (1-2)** | On عِوَجًا before قَيِّمًا | Stopped with Sakt and Madd Iwad. |
| **Ya-Sin (52)** | On مِنْ مَرْقَدِنَا before هَذَا | |
| **Al-Qiyamah (27)** | On مَنْ before رَاقٍ | |
| **Al-Mutaffifin (14)** | On بَلْ before رَانَ | |

#### Permissible Saktas (سكتات جائزة)
There are 2 spots where Sakt is an allowed option among others.

| Position | Options | Description |
| --- | --- | --- |
| **Between Al-Anfal and At-Tawbah** | Waqf, Sakt, or Wasl | There are complex options (15 total faces if stopped/sakt on عَلِيمٌ) connecting the end of Surah Al-Anfal with the beginning of Surah At-Tawbah. |
| **Al-Haqqah (28-29)** | Waqf, Sakt, or Wasl with Idgham | Contextual options on مَاهِيَهْ * هَلَكَ. Sakt prevents the Idgham of the two Ha's. |

---

## 3. Ibtidaa Types (أنواع الابتداء)

### Scope

**الابتداء:** الشروع في بدء قراءة القرآن بعد قطع أو وقف. وينقسم إلى نوعين.

1. **الابتداء الحقيقي (Real Start):** Starting a completely new recitation session. Starting mid-story is considered ugly (e.g., أَلا إِنَّهُمْ هُمُ الْمُفْسِدُونَ), while starting at the beginning of any Surah is always permissible.
2. **الابتداء الإضافي (Additional Start):** Occurs after a breathing pause during an ongoing recitation session. It is categorized based on its syntactic and semantic connection to the preceding words.

This section covers the rules of Ibtidaa (starting/resuming recitation) in Hafs 'an 'Asim. Ibtidaa is considered the counterpart of Waqf — a correct stop must be paired with a correct start.

| # | Rule | Arabic | Description |
| - | ---- | ------ | ----------- |
| 1 | Ibtidaa Mamnou' (Qabih) | الابتداء الممنوع (القبيح) | البدء بكلمة قرآنية يعطي معنى ناقصاً أو فاسداً أو مرفوضاً — غير جائز |
| 2 | Ibtidaa Ja'iz | الابتداء الجائز | البدء بكلمة قرآنية يعطي معنى صحيحاً — وهو ثلاثة أنواع |
| 2.1 | Ibtidaa Tamm | الابتداء التام | ليس بينها وبين ما قبلها تعلق لفظي ولا معنوي |
| 2.2 | Ibtidaa Kaafi | الابتداء الكافي | بينها وبين ما قبلها تعلق معنوي لا لفظي |
| 2.3 | Ibtidaa Hasan | الابتداء الحسن | بينها وبين ما قبلها تعلق معنوي ولفظي |

### 3.1 Ibtidaa Mamnou' / Qabih (الابتداء الممنوع — القبيح)
هو البدء بكلمة قرآنية بينها وبين ما قبلها تعلق معنوي ولفظي، إلا أن البدء به يعطي معنى ناقصاً أو فاسداً أو مرفوضاً، ولا يصح البدء به مطلقاً. **ويُسمى القبيح** لأن الابتداء به يُفسد المعنى، أو يوهم معنى غير ما أراده الله عز وجل.

**Occurs when:** Starting at this point leads to a distorted, incomplete, or heretical meaning. This is the most dangerous type.

**Rule:** إذا وقف القارئ مضطراً، وجب عليه الرجوع كلمة أو كلمتين للبدء بما يتصل معناه. If the reciter stopped by necessity, they must go back one or two words to start from a valid point.

| Feature | Description |
| --- | --- |
| **How to Identify** | The starting point is mid-phrase, creating a misleading meaning. |
| **Performance** | Forbidden to start here intentionally. Go back to a valid starting point. |
| **Ruling** | حكمه غير جائز. Forbidden (Haram) if intentional. |
| **Examples** | Stopping on مَثَلُهُمْ كَمَثَلِ الَّذِي اسْتَوْقَدَ نَارًا and starting with فَلَمَّا أَضَاءَتْ. <br> Stopping on مَثَلا مَا and starting with مَا بَعُوضَةً... |

#### Types of Ugly Starting (أنواع الابتداء القبيح)

| Type | Description | Example |
| --- | --- | --- |
| **Starting with an adjective (Sifa)** | البدء بصفة. Starting with a descriptive word separated from what it describes. | الوقف على "لهم مغفرة وأجر" والبدء بـ **(عَظِيمٌ)** — "Great" without context. |
| **Starting with a causal particle** | البدء بأداة تعليل توهم معنى باطلاً. Starting with a reason clause that implies a false cause. | البدء بـ **(لِيَشْتَرُواْ بِهِ ثَمَناً قَلِيلاً)** بعد الوقف على "من عند الله" — implies buying for a low price is from Allah. |
| **Changing grammatical meaning** | تغيير المعنى الإعرابي. Starting at a point that changes the syntactic parsing. | البدء بـ **(وَالرَّاسِخُونَ فِي الْعِلْمِ...)** باعتبارها جملة استئنافية, وهو ما يغير المعنى التفسيري مقارنة بوصلها — changes who knows the interpretation. |

### 3.2 Ibtidaa Ja'iz (الابتداء الجائز)
**وهو ثلاثة أنواع:**

#### 3.2.1 Ibtidaa Tamm (الابتداء التام)
وهو البدء بكلمة قرآنية **ليس بينها وبين ما قبلها تعلق لفظي ولا معنوي**.

**Occurs when:** Beginning from a phrase that is completely independent from what precedes it.

| Feature | Description |
| --- | --- |
| **How to Identify** | Start of a new Surah, topic, or story. No dependency on the preceding text. |
| **Performance** | Begin naturally with Basmala if at the start of a Surah (except At-Tawbah). |
| **Ruling** | Best type of starting. Encouraged (Mustahabb). |
| **Examples** | Starting with وَلَقَدْ أَرْسَلْنَا نُوحًا after stopping at أَفَلا تَذَكَّرُونَ in Surah Hud. |

#### 3.2.2 Ibtidaa Kaafi (الابتداء الكافي)
البدء بكلمة قرآنية **بينها وبين ما قبلها تعلق معنوي لا لفظي**.

**Occurs when:** The starting point has semantic linkage to what precedes it, but no syntactic (i'rab) dependency.

| Feature | Description |
| --- | --- |
| **How to Identify** | A new clause that is semantically linked but syntactically independent from what precedes. |
| **Performance** | Start naturally. Only valid as an "Additional Start" (الابتداء الإضافي), not a "Real Start". |
| **Ruling** | Permissible and common. |
| **Examples** | Starting with فَقَالَ الْمَلأُ الَّذِينَ كَفَرُوا after stopping at عَذَابَ يَوْمٍ أَلِيمٍ. |

#### 3.2.3 Ibtidaa Hasan (الابتداء الحسن)
البدء بكلمة **بينها وبين ما قبلها تعلق معنوي ولفظي**، ولا يصح البدء بما بعده لتعلقه به من جهة اللفظ والمعنى جميعاً.

**Occurs when:** A reasonable meaning can be understood, but both syntax and meaning are linked to what precedes.

| Feature | Description |
| --- | --- |
| **How to Identify** | Starting gives a partial but acceptable meaning. |
| **Performance** | The stop before it must have been on a verse ending (رأس آية). |
| **Ruling** | Permissible but less preferred unless starting at the beginning of an Ayah. |
| **Examples** | Surah As-Saffat: starting with وَبِاللَّيْلِ. <br> Surah Al-Baqarah: starting with فِي الدُّنْيَا وَالآخِرَةِ. |

### Impact of Ibtidaa on Tajweed

| Rule | Description | Effect |
| --- | --- | --- |
| **Hamzat al-Wasl (همزة الوصل)** | تسقط وصلاً، ولكن عند الابتداء تثبت وتتحول إلى همزة قطع متحركة. | Dropped when connecting (Wasl), but when starting (Ibtidaa) it is pronounced as a full Hamza with a vowel (Damm, Fath, or Kasr) based on Sarf rules. |

### 3.3 Educational/Testing Starts (الابتداء الاختباري على كلمات مخصوصة)
كيفية الابتداء بكلمات مخصوصة عند اختبار المعلم للطالب.

| Word Category | Example / Word | How to Start (Pronunciation) |
| --- | --- | --- |
| **Hamzat Wasl in Verbs** | ثُمَّ لْيَقْطَعْ | Read as **(لِيَقْطَع)** with Kisrah on Lam. |
| **Hamzat Wasl in Nouns** | وَأَصْحَابُ الأَيْكَةِ | Read as **(الأيْكَة)** with Fathah on the Hamzat Wasl. |
| **Bisa Alismu** | بِئْسَ الاِسْمُ | Two valid ways: **(اَلِاسْم)** or **(لِاسْم)**. |
| **Allahumma** | اللَّهُمَّ | Always with Fathah: **(اَللَّهُمَّ)**. |
| **Alutumina** | الَّذِي اؤْتُمِنَ | Read as **(أُوتُمِن)** (Damma on Hamza, second Hamza becomes Waw). |
| **Nouns with Kisrah** | إِنِ امْرُؤٌ | **(اِمْرُؤ)** |
| | عِيسَى ابْنَ مَرْيَمَ | **(اِبْن)** |
| | وَامْرَأَتُ | **(اِمْرَأَة)** |
| **Verbs with Temporary Damma** | (امْشُوا، اقْضُوا، ابْنُوا) | Read with Kisrah on Hamzat Wasl: **(اِمْشُوا، اِقْضُوا...)**. |
| **Iituni** | ائْتُونِي | Read as **(اِيتُونِي)** with Kisrah, changing the second Hamza to Yaa. |

---
