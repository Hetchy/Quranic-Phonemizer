# Test suite coverage and quality review

Reviewed at ~631–683 collected cases (the count moved during the review; another
author was editing `tests/` throughout, and several of the duplication problems
noted in §4 were being repaired as this was written). Every claim below was
checked by running code, not by reading alone.

Transliteration follows `.claude/rules/transliteration.md`: plain ASCII, no
diacritics (idgham, ikhfaa, izhar, tafkheem, tarqeeq, qalqalah, sakt, waqf,
wasl, iltiqa, muqattaat).

---

## Verdict

The suite is now **broad across letters and narrow across junctions**: 27 of the
43 named rules have every letter or path they admit covered, but the coverage is
concentrated in exactly two junctions — a word started on and stopped on, or a
two-word window started on the first and stopped after the last — and the
whole-corpus parity audit proves that *every one of the seven known regressions
lives in a joined reading*. Four of those seven regressions (R1 tanween's linking
kasra, R4 isti'la across a word boundary, R6 idgham through a sakt, R7 the
muqattaat clear noon) have **no test at all**; I reproduced all four live against
the current engine. Only **four parametrized cases in the entire suite** read
across a verse seam, and all four are inside one `engine_bug`-marked test, so no
green test exercises the harness's `wasl=N`-past-the-verse-end path — the path
that the parity audit shows is where 1,547 of the cross-verse differences live.
On top of that, a whole dimension of the rule vocabulary is currently
unassertable: the three qalqalah degrees and the six madd types render to the
same token, `Reading.rules_on_char`/`source_of` still raise `RulesPending`, and
so eleven rules are "covered" only in the sense that their phonemes are right.
Structurally the suite is in good shape and the conventions in `tests/README.md`
are largely honoured; what it lacks is the junction axis and a corpus-wide
ratchet.

---

## 1. Rule coverage matrix

Vocabulary taken from `Rule` in `quranic_phonemizer/model/canon.py:237` ("The
only rule vocabulary"), 43 members plus `PLAIN`. Case counts are collected
tests at the time of review and include riwayah/script parametrization.

**Totals: 1 UNCOVERED, 15 THIN, 27 ADEQUATE.**

### Noon sakinah and tanween

| Rule | Owner | Cases | Verdict |
|---|---|---:|---|
| `izhar_halqi` | `nasal/test_izhar.py` | 23 | **ADEQUATE** — all 6 throat letters in three positions each: inside one word, noon across a seam, tanween across a seam. |
| `izhar_mutlaq` | `nasal/test_izhar.py` (`MUTLAQ`) | 4 | **ADEQUATE** — the closed list is exactly the four words and all four are there. Mis-filed (see §4) and phoneme-identical to `izhar_halqi`, so no assertion tells them apart. |
| `ikhfaa_haqiqi` | `nasal/test_ikhfaa_haqiqi.py` | 31 | **ADEQUATE** — 15 of 15 hiding letters inside one word and 15 of 15 for tanween across a seam. One gap in a path, not a letter: only **1 of 15** letters is tested for a *quiescent noon* meeting the hiding letter across a word seam (`مِّن ظُلُمَـٰتِ`). The heavy colouring of the hidden ghunnah before an isti'la letter cannot be tested at all: `data/render/ipa.yaml` offers one `assimilated: "ŋ"` and no emphatic form. |
| `iqlab` | `nasal/test_iqlab.py` | 10 | **ADEQUATE** — baa is the whole rule; tested inside a word, across a seam for noon and for tanween, and cancelled at a stop. |
| `idgham_bi_ghunnah` | `nasal/test_idgham_bi_ghunnah.py` | 17 | **ADEQUATE** — all 4 letters (ي ن م و) for a quiescent noon and again for tanween, plus the muqattaat noon into a following name. |
| `idgham_bila_ghunnah` | `nasal/test_idgham_bila_ghunnah.py` | 1 | **THIN** — one case, noon + raa. Missing noon + lam, tanween + lam, tanween + raa (3 of the 4 paths), and the sakt block at 83:14 (= R6). |
| `ghunnah_mushaddadah` | `nasal/test_ghunnah_mushaddadah.py` | 1 | **THIN** — one case, a doubled meem, one junction. No doubled noon (`إِنَّ`, `ٱلنَّاسِ`) as its own subject, and the domain fact that the ghunnah is held even at waqf is never asserted. |

### Meem sakinah

| Rule | Owner | Cases | Verdict |
|---|---|---:|---|
| `izhar_shafawi` | `nasal/test_izhar_shafawi.py` | 2 | **THIN** — 2 of 26 letters (daal, taa), and both are word-internal meems. There is **no cross-word case anywhere in the suite**, although a word-final quiescent meem before the next word is the rule's whole subject. `domain-facts.md` §5.2 singles out waw and faa for "extra care"; neither is tested. Already on the README TODO. |
| `ikhfaa_shafawi` | `nasal/test_ikhfaa_shafawi.py` | 1 | **THIN** — baa is the whole rule, so the letter axis is complete, but one case at one junction, no waqf cancellation, and the assertion silently takes one wajh of a declared khilaf (see §4). |
| `idgham_shafawi` | `nasal/test_idgham_shafawi.py` | 1 | **THIN** — meem is the whole rule; one case, one junction, no waqf cancellation. |

### Adjacent consonants and the article lam

| Rule | Owner | Cases | Verdict |
|---|---|---:|---|
| `idgham_mutamathilayn` | `adjacent/test_mutamathilayn.py` | 10 | **ADEQUATE** — nine distinct letters across a seam plus one inside a word. |
| `idgham_mutaqaribayn` | `adjacent/test_mutaqaribayn.py` | 3 | **ADEQUATE** — lam into raa (several sites) and the single qaf-into-kaf site `نَخْلُقكُّم`; the pair list is closed and both members are present. Missing the sakt block at 83:14 (= R6). |
| `idgham_mutajanisayn_kamil` | `adjacent/test_mutajanisayn_kamil.py` | 10 | **ADEQUATE** — all six documented pairs are present, including ت→د as a marked `engine_bug`. |
| `idgham_mutajanisayn_naqis` | `adjacent/test_mutajanisayn_naqis.py` | 4 | **ADEQUATE** — ط→ت is the whole rule, four sites. |
| `lam_shamsiyyah` | `adjacent/test_lam_shamsiyyah.py` | 15 | **ADEQUATE** — all 14 sun letters, plus the joined-into case. |
| `lam_qamariyyah` | `adjacent/test_lam_qamariyyah.py` | 15 | **ADEQUATE** — all 14 moon letters, plus the joined-forward case. |

### Qalqalah

| Rule | Owner | Cases | Verdict |
|---|---|---:|---|
| `qalqala_sughra` | `test_qalqala.py` | 16 total | **THIN** |
| `qalqala_kubra` | " | " | **THIN** |
| `qalqala_akbar` | " | " | **THIN** |

Five letters are listed for sughra and for kubra and four for akbar (no doubled
tah at a stop exists in the corpus), so the letter axis is nearly complete. But
all three degrees render to the same token `Q`, the file asserts only phoneme
strings, and `rules_on_char` raises — so **no assertion in the file can tell the
three rules apart**, and the file's three headings are documentation, not tests.
Two entries are filed under the wrong heading and this matches a real engine
misclassification: `("2:19", 18, "muħi:tˤQ")` مُحِيطٌ and `("2:19", 7,
"warˤaˤʕdQ")` وَرَعْدٌ are word-final qalqalah letters revealed by the pausal drop
of a tanween, i.e. **kubra** by `domain-facts.md` §5.4, and the engine emits
`qalqala_sughra` for both (verified via `performance.occurrences`; also for
2:10:8 عَذَابٌ, asserted in `waqf/test_pausal_sukun.py`). The engine gets
`qalqala_kubra` right when the dropped vowel is a plain damma (1:2:1 ٱلْحَمْدُ),
so the bug is specific to tanween-final words. It is invisible to phonemes and
therefore invisible to the parity audit as well.

### Heaviness and the one-off colourings

| Rule | Owner | Cases | Verdict |
|---|---|---:|---|
| `tafkheem` | `tafkheem/test_istilaa.py` (19), `test_lam.py` (12), `test_raa.py` (19) | 50 | **ADEQUATE** on letters: all 7 isti'la letters heavy with 5 light counterparts; the divine name's lam after fatha, damma, kasra, started on, and three lookalikes that must stay light; raa vowelled, quiescent, after each vowel, with an isti'la letter behind it, doubled, after a quiescent yaa. The README TODO "whether a heavy letter should colour a damma" is now discharged (QUL, KHUDHU, GHUFRANAK, SUDURUHUM). Missing: R4, the isti'la letter in the *next* word; the documented exception that a tanween resolved by an iltiqa kasra leaves the divine lam light (7:164, 11:31) — no test names either site. |
| `tarqeeq` | `tafkheem/test_raa.py`, `test_khilaf.py` | — | **ADEQUATE** on letters, but see junctions: 19 of the 20 raa cases are read `isolated`, and `domain-facts.md` §5.5 says roughly 65% of verse-final raas change class between the two junctions. |
| `imala` | `test_one_offs.py` | 1 | **ADEQUATE** — one site exists in the corpus and it is tested. |
| `tashil` | `test_one_offs.py` | 1 | **ADEQUATE** — same. |
| `ishmam` | `test_one_offs.py` | 1 | **ADEQUATE** for the rule as modelled (the mid-word site 12:11); pausal rawm/ishmam are not in the vocabulary. |

### Madd

| Rule | Owner | Cases | Verdict |
|---|---|---:|---|
| `madd_tabii` | `test_madd.py` | 9 total | **THIN** |
| `madd_wajib_muttasil` | " | " | **THIN** |
| `madd_jaiz_munfasil` | " | " | **THIN** |
| `madd_lazim` | " | " | **THIN** |
| `madd_arid_lil_sukun` | " | " | **THIN** |
| `madd_leen` | " | " | **THIN** |

One site each, and — as with qalqalah — **no assertion distinguishes one type
from another**, because length is one token and the rule name is unreachable.
`test_madd.py` is currently a set of nine phoneme assertions that would all still
pass if the classifier assigned every madd the same type. Specific missing paths:
munfasil reverting to tabii when the first word is stopped on (only the joined
side of `بِمَآ أُنزِلَ` is tested); madd lazim kalimi mukhaffaf (10:51, 10:91);
the graphically-joined particles (vocative `يَـٰٓ`) that look muttasil and are
munfasil.

### Boundary, waqf, and the rest

| Rule | Owner | Cases | Verdict |
|---|---|---:|---|
| `iwad` | `waqf/test_iwad.py` | 8 | **ADEQUATE** — fathatan on a maqsura and on an alif, both junctions, with dammatan/kasratan as the negative controls; the taa marbuta case lives correctly in `waqf/test_taa_marbuta_pausal.py`. One missing path: final hamza + fathatan (`domain-facts.md` §7.4), e.g. 2:22:11 مَآءً → `ma:ʔa:` stopped, `ma:ʔaŋ` joined — verified reachable, untested. |
| `ibdal_hamza` | `boundary/test_ibdal_hamza.py` | 6 | **ADEQUATE** — three words, each at both junctions (started on it, and joined into from the word before). This is the best-shaped file in the suite. |
| `wasl_elision` | `boundary/test_hamza_wasl_elision.py` | 14 | **ADEQUATE** — the article, four verbs, all six irregular nouns, the divine name. Missing: elision at a verse seam. |
| `wasl_start` | `boundary/test_hamza_wasl_start.py` | 18 | **ADEQUATE** — article/fatha, verb-with-damma ×3, verb-without ×3, all seven kasra nouns, the divine name, plus a marked `engine_bug` for the form VIII lookalike. Missing: the irregular hamza-wasl verbs at 7:38 and 9:38 started on. |
| `iltiqa_repair` | `boundary/test_iltiqa_shortening.py` | 13 | **THIN** — two of the three documented repairs: a long vowel shortening (6 cases) and a helping vowel on the previous word (7 cases). The third, **tanween + hamzat wasl takes a linking kasra**, is entirely absent — that is R1, the largest defect in the engine. |
| `waqf_ending` | `waqf/test_pausal_sukun.py` (6), `test_taa_marbuta_pausal.py` (10), `test_final_glides.py` (8), `test_seven_alifs.py` (18) | 42 | **ADEQUATE** — every final short vowel and tanween, both junctions; taa marbuta after each tanween and a plain fatha; final waw/yaa flipping role; both pausal alif families. Missing: the open-taa closed list (e.g. 30:50:4 رَحْمَتِ → `rˤaˤħmat` at a stop, verified reachable, untested), ha' as-sakt (`كِتَٰبِيَهْ`), and the stop signs themselves (README TODO). |
| `silah` | `waqf/test_silah.py` | 12 | **ADEQUATE** — damma-haa and kasra-haa, both junctions, with two negative controls. Missing the stop-specific pronoun drop at 27:36. |
| `sakt` | `test_one_offs.py` | 1 | **UNCOVERED** — the single case reads 75:27 word 2 `isolated`, i.e. stopped on, where nothing the sakt does can be observed: it passes today and would still pass with the sakt removed. The rule's entire content is that it blocks a cross-word assimilation in a *joined* reading, and that is R6. Of Hafs's four mandatory sakt sites (18:1→2, 36:52, 75:27, 83:14) three are untested and the fourth is tested at the junction where it cannot matter. |
| `plain` | — | — | n/a |

### Not a `Rule`, but a subject with a file

`test_muqattaat.py` (14) covers all fourteen openings, all stopped on. `rasm/`
(25) covers the otiose alif, waw and yaa, hamza seats and the alif inside a leen.
`test_khilaf.py` (19) covers `RAA_TAFKHEEM` at all nine sited words; of the seven
`KhilafId` members, only that one and `nucleus_vowel` (one weak case) and
`imala_quality` (indirectly, via `test_one_offs`) are touched at all —
`seen_sad`, `iqlab_nasal`, `ikhfaa_shafawi_nasal` and `yaa_ithbat` have no test.
I verified `IKHFAA_SHAFAWI_NASAL` is genuinely reachable: selecting `"bilabial"`
turns `huŋ` into `hum̃`.

---

## 2. Junction coverage

This is the axis the suite is weakest on, and the parity audit says it is the
only axis where regressions have ever been found (`word` mode is clean: all 56
differences are justified fixes or khilaf).

### The two shapes the suite actually uses

Every behavioural file uses one of two shapes, and only two:

- **`isolated=N` / `ibtidaa=N, waqf=N`** — one word started on and stopped on.
  Used by `tafkheem/` (43 of 44 cases), `rasm/` (all 25), `test_qalqala.py`,
  `test_one_offs.py`, `test_muqattaat.py`, and the "stopped on" half of `waqf/`.
- **`ibtidaa=first, waqf=last`** — a two-word window, started on the first and
  stopped after the last. Used by all of `adjacent/`, `boundary/`, and the
  cross-word half of `nasal/`.

`waqf/` is the exception and the model to copy: every file there pairs
`isolated=N` with `ibtidaa=N, wasl=N`, so each subject is asserted at both
junctions.

### Verse-seam joining: 4 cases, all of them failing on purpose

I instrumented `tests.support.reading.reaches_past` and ran the whole suite. The
harness's read-into-the-next-verse path fires **four times in the entire suite**,
all four in
`waqf/test_seven_alifs.py::test_each_pausal_alif_falls_silent_when_the_reading_carries_on`
(the verse-final `۠` words 76:15:8, 33:10:16, 33:66:11, 33:67:8), and that test
is marked `engine_bug`. **No passing test reads across a verse boundary.** The
capability works — I confirmed 2:7:12 + 2:8:1 gives `ʕaðˤi:mu` `w̃amina`, exactly
the cross-verse sandhi the parity audit reports — it is simply unused.

Rules that should be tested across a verse seam and are not:

- **the whole noon/tanween family** — a verse-final tanween meeting the next
  verse's first letter is 1,547 of the audit's cross-verse differences, i.e. the
  single largest class of cross-verse behaviour in the corpus. No test.
- **`wasl_elision`** — a verse-initial hamzat wasl elided into the previous
  verse, 236 words in the audit. No test.
- **`idgham_bi_ghunnah` / `ikhfaa_haqiqi` / `iqlab` / `izhar_halqi`** — same
  trigger, verse-final. No test.
- **the muqattaat** — 36:1 يسٓ is a whole verse, so R7's second site can *only*
  be reached across the seam. No test.
- **`waqf_ending` vs. joining at a verse end** — the customary stop is at a verse
  end, so the contrast "verse end stopped on / verse end joined" is the most
  common junction a reciter meets, and it appears nowhere.

### Rules tested at only one junction

- `sakt` — stopped on only, which is the junction where it does nothing.
- `ghunnah_mushaddadah` — one junction; the "held even at waqf" fact untested.
- `ikhfaa_shafawi`, `idgham_shafawi`, `idgham_bila_ghunnah` — joined only; no
  test that stopping on the first word cancels them. (`iqlab`, `ikhfaa_haqiqi`
  and `idgham_bi_ghunnah` do have that cancellation case; these three do not.)
- `izhar_shafawi` — two word-internal cases; no junction at all.
- `tafkheem`/`tarqeeq` on a final raa — 19 stopped-on cases, 1 joined.
- `tafkheem` on the isti'la letters — 19 cases, every one `isolated`.
- all six madd types — one junction each except leen and munfasil.
- the muqattaat — all fourteen stopped on, none joined forward (which is where
  R7 and the 27:1 ikhfaa into تِلْكَ live).
- `imala`, `tashil`, `ishmam` — one junction; defensible, they are word-internal.

### Junction cases that exist nowhere in the suite

- **A stop placed *between* the two words of a cross-word rule**, for the
  `adjacent/` family. `domain-facts.md` §5.3 says cross-word idgham is cancelled
  at waqf on the first word; no test asserts it for any of the four idgham.
- **Word-initial shadda dropped at ibtidaa** (`domain-facts.md` §7, ibtidaa 2).
  It happens incidentally — starting on 2:5:4 مِّن gives `mi`, not `mmi` — but no
  test owns it, and nothing would catch it regressing.

---

## 3. The seven regressions

**3 of 7 have a covering test.** All seven were reproduced live against the
current engine while writing this.

| # | Class | Covered? | Test |
|---|---|---|---|
| R1 | tanween loses its linking kasra before a hamzat wasl (112 words) | **NO** | No test in the suite reads a tanween-final word joined into a word beginning with `ٱ`. I checked every joined-tanween assertion in `waqf/` — none of them has a hamzat wasl as its neighbour, so the suite does not even cement the bug; it is simply silent. Verified: `2:61:30` + `31` gives `xaˤjrˤun` `hbitˤu:` (legacy `xaˤjrˤuni`), `11:42:8` + `9` gives `nu:ħun` `bQnah` (legacy `nu:ħuni`). `boundary/test_iltiqa_shortening.py` owns the rule this belongs to and covers the other two repairs only. **The largest gap in the suite.** |
| R2 | final pausal/otiose alif not dropped when joined (73) | **YES** | `waqf/test_seven_alifs.py::test_each_pausal_alif_falls_silent_when_the_reading_carries_on`, `engine_bug`, 7 sites, and the four verse-final ones are the suite's only seam-crossing reads. |
| R3 | raa after an elided hamzat wasl read light (9) | **YES, partially** | `tafkheem/test_raa.py::test_an_incidental_kasra_before_it_leaves_the_raa_heavy`, `engine_bug`, at 24:50 only. The audit names eight sites; the other seven (5:106, 17:24, 21:28, 23:99, 72:27, 38:42, …) are untested, and 38:42 is the one where R1 and R3 compound. |
| R4 | isti'la in the *next* word wrongly makes the raa heavy (3) | **NO** | No test at 31:18, 70:5 or 71:1. Verified: `31:18:2` joined gives `tusˤaˤʕʕirˤ` (should be `…ir`), `70:5:1` gives `fasˤbirˤ`, `71:1:7` gives `ʔaŋðirˤ`. These are the three textbook counter-examples and `tafkheem/test_raa.py` has none of them. |
| R5 | idgham mutajanisayn taa → dal across a boundary (2) | **YES** | `adjacent/test_mutajanisayn_kamil.py::test_a_quiescent_taa_merges_wholly_into_a_following_daal`, `engine_bug`, at 7:189. The second site 10:89 is untested. |
| R6 | idgham applied at a sakt site (2) | **NO** | `test_one_offs.py::test_a_sakt_breaks_the_reading_without_stopping_it` reads 75:27 word 2 `isolated`, which stops before the sakt can block anything; it passes and is unaffected by the bug. Verified: joined, `75:27:2–3` gives `ma` + `rˤrˤaˤ:qQ` and `83:14:2–3` gives `ba` + `rˤrˤaˤ:n` — the engine assimilates straight through both sakts. 83:14 has no test of any kind. |
| R7 | muqattaat clear-noon exception lost (4) | **NO** | `test_muqattaat.py` asserts `nu:n` for 68:1 and `ja:si:n` for 36:1 — both **stopped on**, where the engine is right. Verified: joined, `68:1:1–2` gives `nu:` + `w̃alqaˤlam` instead of `nu:n` + `walqaˤlam`. 36:1 needs a verse seam to reach at all. This is the regression that contradicts `docs/domain-facts.md` line 344 and two ADRs, and the file that owns the subject tests only the safe junction. |

---

## 4. Quality problems

### 4a. Asserted values that cannot be understood without the corpus

`tests/README.md`: "A one-word case is only allowed when one word is the whole
story… A reader must see *why* the value is right without opening the corpus."

Several instances in `waqf/` and `test_khilaf.py` were **repaired during this
review** by the concurrent author (the sites now name the neighbour and assert
it: e.g. `waqf/test_iwad.py` now asserts `r.phonemes(4) == "m̃in"` alongside
`huda`). What remains:

- `waqf/test_silah.py::test_a_haa_before_a_quiescent_letter_gets_no_length`
  (ANNAHU, 2:26:16) — asserts `ʔañahu` with a short haa. The reason is that the
  next word is ٱلْحَقُّ, whose elided hamzat wasl leaves a quiescent lam; the test
  neither names nor asserts that word, so the one interesting case in the file
  reads as an unexplained exception. Its sibling
  `test_a_haa_after_a_quiescent_letter_gets_no_length` (FIHI) is self-contained
  and fine.
- `tests/test_khilaf.py:17` — `("26:63", 11, …, "firˤqiŋ", …)`. The final `ŋ` is
  ikhfaa of this word's tanween into the *next* word, which the row does not
  name. The other eight rows are now self-contained.
- `tests/test_madd.py::test_a_long_vowel_before_a_letter_the_stop_silences` uses
  `@for_each_riwayah(YUNFIQUN, ibtidaa=8)` with no `waqf`. It reads as a stop
  only because word 8 happens to be the last of 2:3 — junction arithmetic the
  reader has to do, which is exactly what `tests/README.md` says the boundary
  arguments exist to prevent. Same in the ADDALLIN case below it.

### 4b. Duplicated subjects

The parallel expansion introduced systematic duplication; the concurrent author
appears to be removing it (`tafkheem/test_raa.py` went 36 → 19 cases and
`waqf/test_pausal_sukun.py` 12 → 6 while this was written). What is still
duplicated **across files**:

- `1:2:1` ٱلْحَمْدُ `ʔalħamdQ` is asserted in three files:
  `adjacent/test_lam_qamariyyah.py`, `nasal/test_izhar_shafawi.py`,
  `test_qalqala.py` (KUBRA).
- `1:6:2` ٱلصِّرَٰطَ `ʔasˤsˤirˤaˤ:tˤQ` in three: `tafkheem/test_istilaa.py`,
  `adjacent/test_lam_shamsiyyah.py`, `test_qalqala.py`.
- `2:29:1` هُوَ `hu:` in three: `waqf/test_final_glides.py`, `test_madd.py`,
  `laws/test_minimal_pairs.py`.
- `2:5:1` أُو۟لَـٰٓئِكَ in three: `test_madd.py`, `rasm/test_otiose_waw.py`,
  `laws/test_minimal_pairs.py`.
- `1:7:9` ٱلضَّآلِّينَ in two: `tafkheem/test_istilaa.py`, `test_madd.py`.
- `2:10:10` بِمَا in two: `test_madd.py`, `test_qalqala.py`.
- `6:143:10` ءَآلذَّكَرَيْنِ in three:
  `adjacent/test_lam_that_is_not_the_article.py`, `test_madd.py`,
  `laws/test_script_agreement.py`.
- `1:7:3` أَنْعَمْتَ in two: `nasal/test_izhar.py`, `nasal/test_izhar_shafawi.py`
  (defensible — two different rules on one word — but both assert the whole
  string, so a change to either rule fails both).

`test_madd.py` is the worst offender: five of its nine cases are another file's
subject, which is a consequence of the "six madds, one token" problem — with no
madd type to assert, the file has nothing of its own to say.

### 4c. Engine behaviour asserted as correct where it is classically wrong

- **`tests/test_qalqala.py`, `SUGHRA` list** — `("2:19", 18, "muħi:tˤQ")` and
  `("2:19", 7, "warˤaˤʕdQ")` are word-final qalqalah letters at a stop, i.e.
  **kubra**, and the engine classifies them `qalqala_sughra` (verified). The
  assertion cannot see the difference, so the test passes either way, but the
  file's grouping records the wrong answer as the intended one. Same word shape
  in `waqf/test_pausal_sukun.py` (2:10:8 عَذَابٌ). Not in the parity audit — it is
  invisible to phonemes — so this is a *new* finding: a rule-classification bug
  with no gate on it.
- **`tests/nasal/test_ikhfaa_shafawi.py:11`** asserts `huŋ`. `ŋ` is
  `nasals.assimilated`, the token for a hidden *noon*; ikhfaa shafawi is a meem
  hidden at the lips and stays bilabial. The project itself treats this as a
  khilaf (`KhilafId.IKHFAA_SHAFAWI_NASAL`, default `ASSIMILATED`), and I verified
  the other wajh is reachable and gives `hum̃`. The test takes the default
  silently, names no khilaf, and has no counterpart for the other wajh — so a
  disputed rendering is recorded as the settled reading. Either mark it as a
  khilaf case in `test_khilaf.py` or rule on the default; `khilaf.yaml` currently
  declares no entry for this point at all.
- No test asserts the wrong side of R1–R7. R2, R3, R5 are correctly marked
  `engine_bug`; R1, R4, R6, R7 have no test to be wrong with. The 10 failing
  cases under `-m engine_bug` are all legitimate, and `-m "not engine_bug"` is
  green (672 passed, 1 skipped at review time).

### 4d. Weak assertions

- `tests/test_khilaf.py:65` — `assert r.phonemes(5)`. Truthiness of a non-empty
  string; the only way this fails is if the word produces no phonemes at all. The
  test name promises that a vowel khilaf is settled before performance; it should
  assert the settled value (`dˤaˤʕf` / `dˤuʕf`) for both options.
- `tests/test_khilaf.py::test_both_wajh_are_reachable` — asserts only
  `heavy != light`. It would pass if both wajh were wrong, or swapped. Assert the
  two values.
- `tests/test_qalqala.py:64` — `assert "Q" not in r.phonemes(10)` immediately
  after `assert r.phonemes(10) == "bima:"`. Cannot fail independently.
- `tests/laws/test_roundtrip.py:32` — `assert all(text for text in spelled)`:
  non-emptiness only.
- `tests/laws/test_anchored_projection.py:107` — `assert any(not sound.graphemes
  for sound in view.sounds)`: one unanchored sound anywhere satisfies it.
- `tests/laws/test_noon_family.py:84` — `assert triggers & named` is truthiness
  of a set intersection; and
  `test_izhar_is_classification_only` calls `pytest.skip` if the chosen verse has
  no izhar, so it will pass silently the day the classifier stops firing there.
  (It does not skip today; only one test skips, the IndoPak one.)

### 4e. Filing against `tests/README.md`'s layout

- `izhar_mutlaq` is its own `Rule` but lives inside `nasal/test_izhar.py`, which
  owns `izhar_halqi`. "One file per rule" says it should be
  `nasal/test_izhar_mutlaq.py`.
- `nasal/test_izhar_shafawi.py` contains only word-internal meems, i.e. it tests
  a position the meem sakinah family is not about; the cross-word cases the rule
  is defined by are absent rather than mis-filed.
- `waqf/test_seven_alifs.py` holds the round-zero alif (`قَوَارِيرَا۟`, `سَلَـٰسِلَا۟`)
  as a contrast family. By the layout table the round zero is `rasm/` ("letters
  the script writes and the reading never says"); keeping the contrast pair
  together is defensible, but `rasm/test_otiose_alif.py` currently has no idea
  the rectangular zero exists.
- `test_madd.py` — see 4b; five of nine cases belong to `waqf/` or `rasm/`.
- `laws/` still imports helpers from `conftest.py` and predates `Site`, as the
  README's own TODO says. `laws/test_minimal_pairs.py` and
  `laws/test_script_agreement.py` are the two files that *can* assert rule names
  today (they read `performance.occurrences` directly), and they are the natural
  home for the qalqalah-degree and madd-type assertions the `Site` harness cannot
  make.
- `tests/snapshots/phonemes/*.jsonl.gz` — the frozen legacy baselines — are read
  by `tools/parity.py` and **by no test at all**. There is no gate in the suite
  on corpus-wide parity, in any mode. That is the structural reason all seven
  regressions landed.

---

## 5. Ranked worklist

1. Add the R1 family to `boundary/test_iltiqa_shortening.py`: tanween joined into
   a hamzat wasl takes a linking kasra (2:61:30, 11:42:8, 9:30:3, 4:171:31,
   7:8:2), marked `engine_bug` — 112 words, the largest defect, and an
   unimplemented rule with no test anywhere.
2. Add a `continuous`-mode parity gate to `laws/`, surah-joined as
   `research/legacy-parity-audit.md` §2 prescribes, ratcheted on the frozen
   snapshots — the suite has no corpus-wide gate at all, which is why seven
   regressions landed.
3. Give every cross-word rule a verse-seam case with `wasl=N` on a verse-final
   word: no passing test in the suite crosses a seam, and the audit puts 1,547
   cross-verse differences there.
4. Test R7 at the junction that matters: 68:1 joined forward (`nu:n` +
   `walqaˤlam`) and 36:1 across the seam into 36:2 — a documented Hafs exception
   the engine silently discards.
5. Test R6: 75:27 and 83:14 read **joined**, asserting the sakt blocks the
   idgham; today's single sakt case is stopped on and cannot fail.
6. Test R4: 31:18, 70:5, 71:1 joined, asserting the raa stays light when the
   isti'la letter is in the next word.
7. Move the rule-name assertions the `Site` harness cannot make into `laws/`:
   assert `qalqala_kubra` at a tanween-final qalqalah letter (this fails today —
   the engine says sughra) and assert one occurrence per madd type.
8. Fill `izhar_shafawi`: the remaining letters, and at least one cross-word case
   — the rule's defining position has zero tests.
9. Fill `idgham_bila_ghunnah`: noon + lam, tanween + lam, tanween + raa (3 of 4
   paths missing from a one-case file).
10. Add the waqf-cancellation case for each cross-word rule that lacks one
    (`idgham_bila_ghunnah`, `ikhfaa_shafawi`, `idgham_shafawi`, and all four
    `adjacent/` idgham): a stop between the pair must undo the merger.
11. Give the muqattaat a joined half — all fourteen are stopped on today, so
    27:1's ikhfaa into تِلْكَ and 3:1's connected الم→اللَّهُ are untested.
12. Rule on `IKHFAA_SHAFAWI_NASAL` and make `nasal/test_ikhfaa_shafawi.py` say
    which wajh it asserts; add the other wajh (`hum̃`) to `test_khilaf.py`, which
    covers only `RAA_TAFKHEEM` of seven khilaf points.
13. Balance `tafkheem/test_raa.py` across junctions — 19 stopped-on cases against
    1 joined, for a rule whose class flips at ~65% of verse-final sites.
14. Fix the weak assertions: `test_khilaf.py:65` truthiness, `test_both_wajh_are_reachable`
    asserting only inequality, `test_qalqala.py:64` redundant, and the
    `pytest.skip` fallback in `laws/test_noon_family.py`.
15. Finish the de-duplication already in progress: fold `test_madd.py`'s five
    borrowed subjects back into `waqf/` and `rasm/`, split `izhar_mutlaq` into its
    own file, and remove the three-file repeats of `ʔalħamdQ` and
    `ʔasˤsˤirˤaˤ:tˤQ`.
