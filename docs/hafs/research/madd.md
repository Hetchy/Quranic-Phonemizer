# Madd (Hafs Riwayah)

Analysis of madd (vowel prolongation) rules in Uthmanic Hafs v2.0 dataset.

Source:
data/QS - QIRAAT/Uthmanic Hafs v2.0/hafsData_v2-0.json

# Scope

This document covers madd categories in Hafs ‘an ‘Asim:
| # | Rule               | Arabic            | Description                              |
| - | ------------------ | ----------------- | ---------------------------------------- |
| 1 | Madd Tabee‘i       | مد طبيعي          | No hamzah or sukoon after madd letter    |
| 2 | Madd Badal         | مد بدل            | Hamzah precedes madd letter in same word |
| 3 | Madd Muttasil      | مد متصل           | Hamzah follows madd letter in same word  |
| 4 | Madd Munfasil      | مد منفصل          | Hamzah begins next word                  |
| 5 | Madd Lazim         | مد لازم           | Permanent sukoon after madd letter       |
| 6 | Madd ‘Arid         | مد عارض للسكون    | Sukoon due to stop                       |
| 7 | Madd Leen          | مد لين            | Waw/yaa saakin preceded by fatḥa at stop |
| 8 | Madd in Muqatta‘at | مد الحروف المقطعة | Prolongation in disjoint letters         |


# Madd Tabee‘i (مد طبيعي)
هو إطالة الصوت بحرف من حروف المد الثلاثة إذا لم يأتِ بعده همز ولا سكون

Length: 2 harakat

Occurs when a madd letter is not followed by hamzah or sukoon.

| Word    | Ref   |
| ------- | ----- |
| قَالَ   | 2:30  |
| يَقُولُ | 2:8   |
| فِي     | 1:7   |
| نُوحِي  | 7:101 |
## Note

    If followed by hamzah → becomes Muttasil or Munfasil

    If followed by permanent sukoon → becomes Lazim

    If followed by temporary sukoon (stop) → becomes ‘Arid

  So technically, it has no exception, but it can change category depending on context.
# Madd Badal (مد بدل)
هو أن يتقدم الهمز على حرف المد في كلمة واحدة.

Length in Hafs: 2 harakat (fixed)

| Word      | Ref   |
| --------- | ----- |
| آمَنُوا   | 2:9   |
| إِيمَانًا | 2:143 |
| أُوتُوا   | 2:101 |
| ءَامَنَ   | 3:84  |

Note: No extension beyond 2 in Hafs.
      No exception in Hafs.

# Madd Muttasil (مد متصل)
هو أن يأتي بعد حرف المد همز في نفس الكلمة.

Length in Hafs: 4–5 harakat

| Word       | Ref  |
| ---------- | ---- |
| جَاءَ      | 2:87 |
| السَّمَاءِ | 2:22 |
| سُوءَ      | 2:49 |
| أُولَٰئِكَ | 2:5  |

Obligatory extension.
## Exceptions
   Cannot be shortened to 2 in Hafs
   Only variation: 4 or 5
# Madd Munfasil (مد منفصل)
هو أن يقع حرف المد في آخر كلمة، ويأتي الهمز في أول الكلمة التي بعدها.

Length in Hafs: 4–5 harakat

| Phrase               | Ref   |
| -------------------- | ----- |
| فِي أَنفُسِكُمْ      | 2:235 |
| بِمَا أُنزِلَ        | 2:4   |
| إِنَّا أَعْطَيْنَاكَ | 108:1 |
| قَالُوا آمَنَّا      | 2:136 |

## Exceptions

    In theoretical riwayah, qasr (2) is transmitted

    But in common Hafs performance today → no qasr
## Special Case in Madd Munfasil (Within the Same Word)
Although the hamzah is not in a separate written word, scholars classify this word under the ruling of Madd Munfasil.

| Word         | Analysis                          | Type                                        | Ruling in Ḥafṣ |
| ------------ | --------------------------------- | ------------------------------------------- | -------------- |
| هَٰؤُلَاءِ   | ها التنبيه + أولاء                | Madd Munfasil (Constructive / Ruling-based) | 4 or 5 counts  |
| أَهَٰؤُلَاءِ | همزة الاستفهام + ها التنبيه + أولاء | Madd Munfasil (Constructive / Ruling-based) | 4 or 5 counts  |
| وَهَٰؤُلَاءِ | واو + ها التنبيه + أولاء          | Madd Munfasil (Constructive / Ruling-based) | 4 or 5 counts  |
| يَٰأَيُّهَا  | يا النداء + أيها                  | Madd Munfasil (Constructive / Ruling-based) | 4 or 5 counts  |
| هَٰأَنتُمْ   | ها التنبيه + أنتم                 | Madd Munfasil (Constructive / Ruling-based) | 4 or 5 counts  |

The prefix does not move the seam. أهؤلاء occurs 4 times — 5:53, 6:53, 7:49,
34:40 — and the interrogative hamza stands *before* ها, never between ها and
أولاء, so the first madd is separated there exactly as it is without it. The
prefixed forms are the whole of the disagreement between annotators: cpfair's
`quran-tajweed` data, for instance, splits هَٰٓأَنتُمْ (munfasil) from
هَٰٓؤُلَآءِ (muttasil) in one and the same ayah, 3:66, which tracks whether the
following hamza is written standalone أ or carried ؤ and is not a tajweed
distinction. quran.com's tajweed edition does not separate munfasil from
muttasil at all: بِمَآ أُنزِلَ and هَٰٓؤُلَآءِ are both `madda_obligatory`.

The counter-example is هَآؤُمُ (69:19), same shape and **not** a joined
particle: its hamza is the third radical of the imperative noun هاء, so it is
wajib muttasil. Only a lexicon separates the two.

## For this reason, it takes the ruling of: Madd Munfasil (4–5 counts in Ḥafṣ).

  The word has a compound linguistic structure.

  There is a phonetic separation between the madd letter and the hamzah.

  The hamzah is not directly attached to the madd letter in the same way as in Madd Muttasil.


# Madd Lazim (مد لازم)
هو أن يأتي بعد حرف المد سكون أصلي ثابت وصلاً ووقفًا.
Length: 6 harakat (mandatory)

Occurs when madd letter is followed by permanent sukoon.

## A) Kalimi Muthaqqal (كلمي مثقل)

Madd letter + shaddah

| Word         | Ref   |
| ------------ | ----- |
| الضَّالِّينَ | 1:7   |
| آلآنَ        | 10:51 |
| الحَاقَّةُ   | 69:1  |
## B) Kalimi Mukhaffaf (كلمي مخفف)

Hafs allows two ways at six locations in three word forms:

| Form       | References       | First option | Second option |
| ---------- | ---------------- | ------------ | ------------- |
| al-dhakrayn | 6:143, 6:144    | madd lazim   | tasheel       |
| al-aan      | 10:51, 10:91    | madd lazim   | tasheel       |
| al-lah      | 10:59, 27:59    | madd lazim   | tasheel       |

The `madd_lazim` option keeps the long a. The `tasheel` option reads two
hamzas, with the second hamza eased. This choice is the same in waqf and wasl;
the boundary does not select or normalize either option. In `al-dhakrayn`,
tasheel does not expose the article lam: lam-shamsiyyah assimilation remains,
so the dhal remains doubled.

## C) Harfi (in Muqatta‘at)

Occurs in disjoint letters
## Example:
|الم | 2:1 | 

## Exceptions

Outside the six madd-lazim-or-tasheel locations above, madd lazim is not
shortened.

# Madd ‘Arid lil-Sukoon (مد عارض للسكون)
هو أن يأتي بعد حرف المد سكون عارض بسبب الوقف.

Length: 2 / 4 / 6

Occurs only at stop.

| Word (when stopping) | Ref |
| -------------------- | --- |
| الْعَالَمِينَ        | 1:2 |
| الرَّحِيمِ           | 1:3 |
| نَسْتَعِينُ          | 1:5 |

## Exceptions

   Only applies at stop

   If continuing (wasl) → reverts to original rule (usually Tabee‘i)

# Madd Leen (مد لين)
هو إطالة الواو أو الياء الساكنتين المفتوح ما قبلهما عند الوقف.

## Pattern:

وْ or يْ 

     preceded by fatḥa

     stop required

Length at stop: 2 / 4 / 6

| Word    | Ref   |
| ------- | ----- |
| خَوْف   | 2:38  |
| بَيْت   | 2:125 |
| قُرَيْش | 106:1 |

## Exceptions

 No madd in wasl

 Only at stop

# Madd in Muqatta‘at (الحروف المقطعة)
هو المد الواقع في أسماء الحروف المقطعة في أوائل السور.
Appears in 29 surahs.

Each letter is pronounced independently.

## Letters with 6 Harakat (Lazim Harfi)

These contain internal madd + permanent sukoon.

| Letter | Example Surah |
| ------ | ------------- |
| ل      | الم (2:1)     |
| م      | الم (2:1)     |
| س      | يس (36:1)     |
| ك      | كهيعص (19:1)  |
| ع      | كهيعص (19:1)  |
| ص      | ص (38:1)      |
| ن      | ن (68:1)      |
| ق      | ق (50:1)      |
All extended 6 harakat.

## Letters with Natural Madd (2 Harakat)
| Letter | Example    |
| ------ | ---------- |
| ح      | حم (40:1)  |
| ي      | يس (36:1)  |
| ط      | طه (20:1)  |
| ه      | طه (20:1)  |
| ر      | الر (10:1) |

Extended 2 harakat only.

##  ملاحظات خاصة برواية حفص
- المد اللازم لا يُقصر أبدًا
- مد البدل ثابت على حركتين
- مد اللين خاص بالوقف فقط
- المد المنفصل لا يُقصر في الأداء المشهور

---




