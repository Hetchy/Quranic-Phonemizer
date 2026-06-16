# Tajweed Linguistics Reference

This reference explains the tajweed rules implemented by the Quranic Phonemizer for those unfamiliar with Arabic phonetics and Quranic recitation.

## What is Tajweed?

Tajweed (تجويد, "embellishment") is the set of phonological rules governing how the Quran must be recited aloud. These rules specify precise articulation points, nasalization, assimilation, vowel lengthening, and other phonetic phenomena that differ from conversational Arabic. Tajweed is traditionally learned orally, but this phonemizer encodes these rules systematically.

The phonemizer implements tajweed for the **Hafs recitation** (riwaya), the most widely used of the ten canonical readings of the Quran.

## Arabic Phonetic Basics

### Letters and Diacritics

Arabic script is an abjad — consonant letters carry the word's skeletal structure, while short vowels are written as small marks (diacritics) above or below:

| Diacritic | Name | Sound | IPA |
|-----------|------|-------|-----|
| فَ | Fatha | "a" as in "cat" | `a` |
| فُ | Damma | "u" as in "put" | `u` |
| فِ | Kasra | "i" as in "sit" | `i` |
| فْ | Sukun | No vowel (consonant only) | — |
| فّ | Shaddah | Gemination (double consonant) | e.g. `bb` |

### Long Vowels

Long vowels are formed when a short vowel is followed by a matching "vowel letter":

| Short + Letter | Result | IPA |
|----------------|--------|-----|
| Fatha + alef (ا) | Long "aa" | `a:` |
| Damma + waw (و) | Long "uu" | `u:` |
| Kasra + yaa (ي) | Long "ii" | `i:` |

Some long vowels use special extension characters instead of full letters: dagger alef (ٰ), mini waw (ۥ), mini yaa (ۦ). These appear as small superscript marks.

### Tanween (Nunation)

Tanween adds an /n/ sound after a short vowel at the end of a word:

| Tanween | Sound | IPA |
|---------|-------|-----|
| فً (fathatan) | "an" | `an` |
| فٌ (dammatan) | "un" | `un` |
| فٍ (kasratan) | "in" | `in` |

### Emphatic Consonants (Tafkheem Letters)

Seven Arabic consonants are pronounced with the back of the tongue raised toward the palate, producing a "heavy" or emphatic quality:

**ص ض ط ظ** (always emphatic) + **خ غ ق** (istilaa consonants)

These letters spread their heaviness to adjacent vowels. A fatha after ط sounds like a deeper "aw" rather than a bright "a" — the phonemizer represents this with `aˤ` (pharyngealized).

## Rule Categories

### 1. Nasalization Rules (Noon and Meem)

Noon (ن) and meem (م) with sukun interact with the following letter in specific ways. These rules depend on what letter comes next.

**Ghunnah** (غنة, "nasalization"): A prolonged nasal sound (2 counts) through the nose. Occurs naturally with noon or meem carrying shaddah.

| Rule | Arabic Name | What Happens | Phonemizer |
|------|-------------|--------------|------------|
| **Ikhfaa** | إخفاء | Noon/tanween "hidden" before 15 specific letters — partial nasalization | `ŋ` |
| **Ikhfaa Shafawi** | إخفاء شفوي | Meem sakin hidden before baa (ب) — lip-based nasalization | `ŋ` |
| **Iqlab** | إقلاب | Noon/tanween before baa (ب) converts to meem sound | `ŋ` |
| **Idgham with Ghunnah** | إدغام بغنة | Noon/tanween merges into ي ن م و with nasalization | `ñ m̃ j̃ w̃` |
| **Idgham without Ghunnah** | إدغام بلا غنة | Noon/tanween fully merges into ل ر without nasalization | Silent noon |
| **Idgham Shafawi** | إدغام شفوي | Meem sakin merges into following meem with nasalization | `m̃` |

### 2. Assimilation Rules (Idgham Types)

Beyond noon/meem-specific rules, Arabic has general assimilation when similar consonants meet:

| Rule | Arabic Name | What Happens |
|------|-------------|--------------|
| **Idgham Mutamathilayn** | إدغام متماثلين | Identical letters merge — first becomes silent, second gets shaddah |
| **Idgham Mutaqaribayn** | إدغام متقاربين | Letters with close articulation points merge |
| **Idgham Mutajanisayn Kamil** | إدغام متجانسين كامل | Letters sharing the same articulation point merge fully |
| **Idgham Mutajanisayn Naqis** | إدغام متجانسين ناقص | Partial assimilation — source changes but is not fully silent |
| **Lam Shamsiyah** | لام شمسية | The lam of the definite article (ال) is silent before 14 "sun letters" |

### 3. Qalqala (Echoing)

Five letters — **ق ط ب ج د** — produce a slight bouncing/echoing sound when they carry sukun:

- **Qalqala Sughra** (minor): Mid-word or mid-verse — subtle bounce (`Q`)
- **Qalqala Kubra** (major): At a stop — stronger bounce (`QQ`)

### 4. Tafkheem (Heaviness)

Beyond the inherently emphatic consonants, two letters gain heaviness contextually:

- **Raa** (ر): Heavy when carrying fatha or damma, or sukun after fatha/damma. Light when carrying kasra or sukun after kasra.
- **Lam** (ل): Heavy only in the word "Allah" (الله) when the preceding vowel is fatha or damma.

Heavy pronunciation is represented with pharyngealization markers: `rˤ`, `rˤrˤ`, `lˤlˤ`, `aˤ`, `aˤ:`.

### 5. Hamza Wasl (Connecting Hamza)

The character ٱ (hamza wasl) at the start of a word behaves differently depending on context:

- **Mid-verse (connecting):** Silent — the word flows from the previous word
- **Starting:** Pronounced with a vowel:
  - Fatha (أَ) — before the definite article (ال)
  - Kasra (إِ) — most verbs and nouns
  - Damma (أُ) — verbs with damma pattern

### 6. Iltiqaa Sakinayn (Meeting of Two Sukuns)

Arabic phonology avoids two consecutive consonants without a vowel between them. When this occurs at a word boundary:

- A long vowel before hamza wasl gets **shortened** (the vowel letter becomes silent)
- Tanween before hamza wasl gets an **extra kasra** to break the cluster

### 7. Madd (Vowel Lengthening)

Madd rules specify how long a vowel should be held. Duration is measured in "counts" (harakat):

| Rule | Arabic Name | Duration | Cause |
|------|-------------|----------|-------|
| **Madd Tabii** | مد طبيعي | 2 counts | Natural long vowel, no special cause |
| **Madd Wajib Muttasil** | مد واجب متصل | 4–5 counts | Long vowel followed by hamza in same word |
| **Madd Jaiz Munfasil** | مد جائز منفصل | 2–4–5 counts | Long vowel at word end, hamza in next word |
| **Madd Lazim** | مد لازم | 6 counts | Long vowel followed by sukun/shaddah in same word |
| **Madd Arid Lissukun** | مد عارض للسكون | 2–4–6 counts | Long vowel before a letter that gets sukun from stopping |
| **Madd Leen** | مد لين | 2–4–6 counts | Fatha + waw/yaa sakin before a stopping sukun |

## Waqf (Stopping) Effects

Stopping at the end of a phrase changes the phonetics of the final word:

1. **Final vowel removed** — last letter gets sukun (no vowel)
2. **Taa marbuta** (ة) — pronounced as haa (ه) with sukun
3. **Fathatan** (ً) — becomes a long "aa" (madd iwad) instead of "an"
4. **Qalqala letters** — gain echoing sound at the stop
5. **Cross-word rules disappear** — each word becomes self-contained

Starting on a word also has effects: hamza wasl is pronounced, and first-letter shaddah may be removed.

## Huroof Muqattaat (Disconnected Opening Letters)

Fourteen surahs begin with mysterious letter combinations (e.g., الم, حم, كهيعص). These are recited by spelling out each letter name with specific tajweed rules between them, including madd lazim (6-count lengthening) and idgham between adjacent letter names.

## Cross-Word Interaction

Many tajweed rules operate across word boundaries — the last letter of one word interacts with the first letter of the next. The phonemizer models this through doubly-linked Word objects, where each letter can inspect and mutate its neighbors' phonemes. This is critical for rules like idgham, ikhfaa, and iltiqaa that span two words.
