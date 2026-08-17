# Differences Between Warsh and Hafs Recitations


- They differ in the pronunciation of certain letters and words, some tajweed rules like madd (المد), and also in some vocabulary and word form variations, like مَلِك and مَالِك in Surat Al-Fatiha.

- **Note:** This is a brief summary, not an exhaustive breakdown. For full details, see the rest of the documentation files.

## Word Differences

In some words, the wording itself differs between the two narrations:

| Words in Warsh | Ref in Warsh | Words in Hafs | Ref in Hafs |
| --- | --- | --- | --- |
| مَلِكِ | 1:3 | مَٰلِكِ | 1:4 |
| يُخَٰدِعُونَ | 2:8 | يَخْدَعُونَ | 2:9 |
| يُكَذِّبُونَۖ | 2:9 | يَكْذِبُونَ | 2:10 |
| يُغْفَرْ | 2:57 | نَّغْفِرْ | 2:58 |

## The Word هُوَ in Surat Al-Hadid

In Warsh, Surat Al-Hadid 57:23 reads:

> وَمَنْ يَّتَوَلَّ فَإِنَّ اَ۬للَّهَ اَ۬لْغَنِيُّ اُ۬لْحَمِيدُۖ

In Hafs, the equivalent verse is 57:24:

> وَمَن يَتَوَلَّ فَإِنَّ اللَّهَ هُوَ الْغَنِيُّ الْحَمِيدُ

The difference lies in the word **هُوَ**, which is present in Hafs but absent in Warsh.

## Al-Madd (المد)

All madd rules are documented in `madd_rules_warsh.md`.

- **Madd Al-Badal**
  - Warsh reads madd al-badal with 2, 4, or 6 harakat (all documented in `madd_rules_warsh.md`).
  - Hafs reads madd al-badal with 2 harakat.
- **Madd Muttasil and Munfasil**
  - Warsh performs these with 6 harakat, while Hafs performs them with 4-5 harakat.
- **Madd Silat Meem Al-Jama'** (when followed by a hamzat qat')
  - Warsh reads it with 6 harakat.

## Al-Hamza (الهمز)

All hamza rules are documented in `hamz_takhefif.md`.

- Warsh uses four techniques: **Tasheel**, **Naql**, **al-Isqat**,and **Ibdal**.

## Imālah (الامالة)

- In Hafs, it occured in only one place, whereas in Warsh, it occured in multiple places. Check `imalah_rules.md` and `imalah_classification.md`.

## Tafkheem wa Tarqeeq (التفخيم والترقيق)

- They differ in Tafkheem and Tarqeeq of Rā’ and Lām, and all the rules are documented in `tafkheem_tarqeeq.md`.

## Al-Alifat As-Sab'a (The Seven Alifs - الألفات السبعة)

- These are seven Quranic words to which an elongation alif (الف المد) is attached. This alif is retained when pausing (waqf) and dropped when continuing the recitation (wasl).

| Narration | State | أَنَا | لَّٰكِنَّا | اِ۬لظُّنُونَاۖ | اَ۬لرَّسُولَاۖ | اَ۬لسَّبِيلَاۖ | سَلَٰسِلاٗ | قَوَارِيراٗۖ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hafs | Continuous reading (Waslan) | Dropped | Dropped | Dropped | Dropped | Dropped | Dropped | Dropped |
| Hafs | When pausing (Waqfan) | Retained | Retained | Retained | Retained | Retained | Retained (preferred view), or one may pause with a sakinah lam | Retained |
| Warsh | Continuous reading (Waslan) | Dropped, unless followed by a hamzat qat' that is fathah or dammah | Dropped | Retained | Retained | Retained | Tanwin with idgham | Tanwin with ikhfa' with tarqeeq of the raa |
| Warsh | When pausing (Waqfan) | Retained | Retained | Retained | Retained | Retained | Madd with 2 harakat | Madd with 2 harakat |

## Symbols and Signs in the Holy Qur'an 

> **Note:** The "Which Riwayah Used" column refers to which narration uses this symbol in our files (`Quran.json` and `Quran_warsh.json`) and not in the actual mus'haf.

| Symbol | Unicode | Interpretation | Which Riwayah Used |
| --- | --- | --- | --- |
| ◌ۖ | U+06D6 | Means "صل اولى" - continuing (wasl) is preferred | Both Riwayat |
| ◌ۗ | U+06D7 | Means "قف اولى" - stopping (waqf) is preferred | Hafs |
| ◌ۛ | U+06DB | Usually occurs twice simultaneously; means you cannot stop (waqf) at both places - you may stop at one of them, or not stop at all | Hafs |
| ◌ۢ | U+06E2 | Means Iqlab | Warsh |
| ◌ٓ | U+0653 | Means Madd | Both Riwayat |
| ◌۬ | U+06EC | Means Ibdal | Warsh, and only one occurrence in Hafs |
| ◌ۚ | U+06DA | Means both pause and continuation (wasl) are permissible | Hafs |
| ◌ۙ | U+06D9 | Means do not stop | Hafs |
| ◌ۘ | U+06D8 | Means one must stop (waqf) | Hafs |
| ◌۟ | U+06DF | Means the letter is not read and is completely ignored | Both Riwayat |
| ◌۠ | U+06E0 | Means the letter is read in waqf and ignored in wasl | Hafs |
| ◌ً<br>◌ٌ<br>◌ٍ | U+064B<br>U+064C<br>U+064D | Means the tanwin is pronounced | Both Riwayat |
| ◌ٖ<br>◌ٗ<br>◌ٞ | U+0656<br>U+0657<br>U+065E | Means there is idgham | Warsh |
| ◌ۜ | U+06DC | Means there is a saktah - a pause without breathing (waqf without nafas) | Hafs |
| ◌۪ | U+06EA | Means there is imalah | Warsh, and only one occurrence in Hafs |

## Sources


[الفرق بين رواية ورش عن نافع ورواية حفص عن عاصم](https://www.youtube.com/watch?v=cfhqOGqLerw&t=631s) 

[شرح مبسط للرموز والعلامات في القرآن الكريم](https://www.youtube.com/watch?v=U6i8okY_wn0)

[الألفات السبعة في القرآن الكريم عند ورش وحفص](https://www.youtube.com/watch?v=MHNk_N6eKfY)