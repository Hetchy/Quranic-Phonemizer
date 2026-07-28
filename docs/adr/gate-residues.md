# What is not 100%, and why

The floors in `.github/workflows/gates.yml` are not all 1.000. This file names
every row behind every one of them, so a floor short of 100% is a claim that
can be checked rather than a number nobody looks at.

| Gate | Now | Residue |
|---|---|---|
| cross-script, word | 99.997% | 2 words |
| cross-script, verse | **100.000%** | none |
| round-trip, uthmani | **100.000%** | none |
| regression, word | 99.926% | 57 words |
| regression, verse | 97.674% | see below |
| L1 | 18 rows over 287,057 slots | |
| attestations | 178 uthmani, 239 indopak | |

## Cross-script — 2 words

Both are IndoPak writing the elided form of an iltiqa al-sakinayn, and both
join to the same sounds as Uthmani; only the artificial stop that word mode
forces separates them.

| Ref | Uthmani | IndoPak | Joined |
|---|---|---|---|
| 26:61:2 | `تَرَآءَا` | `تَرَآءَ` | `tarˤaˤ:ʔa lʒamʕa:ni` both |
| 59:9:2 | `تَبَوَّءُو` | `تَبَوَّءُ` | `tabawwaʔu dda:rˤaˤ` both |

## Regression — 57 words

The oracle is the previous implementation with its own defects frozen in, so
this gate is a change detector and not a target. Every row is one of six
classes, and each class is a disagreement whose direction is established
independently of the oracle.

**19 + 5 — the small yaa and the small waw** (`يُحْىِۦ`, `وَلِىِّۦ`,
`ءَاتَىٰنَِۧ`, `تَلْوُۥٓا۟`, `فَأْوُۥٓا۟`, `لِتَسْتَوُۥا۟`). Uthmani writes
the vowel with `ۦ` and `ۥ`; the oracle drops it and ends the word on the
consonant. `juħj` for `يُحْىِۦ` says no vowel is written where one is.

**11 — the quiescent hamza after a prosthetic one** (`ٱئْتِ`, `ٱئْتُوا۟`,
`ٱئْذَن`, `ٱؤْتُمِنَ`). Read alone, every one of these is started on, and a
quiescent hamza after a started prosthetic one becomes the madd of its
vowel: `ʔi:ti`, not `ʔiʔti`.

**10 — the disputed raa** (`مِصْرَ` ×4 heavy, `يَسْرِ`/`أَسْرِ`/`فَأَسْرِ` ×6
light). `docs/hafs/research/tafkheem_tarqeeq.md` §2G tabulates both defaults
and records that the oracle's mechanical rule diverges from them at 89:4. All
ten are khilaf sites, so the other wajh is selectable.

**7 — a waw carrying fatha before the otiose alif** (`يَعْفُوَا۟`,
`أَتْلُوَا۟`, `لِّيَرْبُوَا۟`, `لِّيَبْلُوَا۟`, `وَنَبْلُوَا۟`,
`لِّتَتْلُوَا۟`, `نَّدْعُوَا۟`). The stop drops the fatha and leaves a waw
quiescent after a damma, which is madd tabii by definition. The oracle
answers this shape two ways: `هُوَ` gives `hu:` and `يَعْفُوَا۟` gives
`jaʕfuw`, so it contradicts itself rather than us.

**5 — the dual construct** (`طَرَفَىِ`, `يَـٰصَـٰحِبَىِ` ×2, `يَدَىِ`,
`ثُلُثَىِ`). The kasra on the yaa is there to meet the wasl hamza of the next
word, which is what proves the yaa is a consonant. Stopping gives `-ay`; the
oracle's `-aa` is the nominative of a word standing in the genitive.

## Verse mode

The same classes, plus the rows where a word-mode difference propagates into
its neighbour once the words are joined.
