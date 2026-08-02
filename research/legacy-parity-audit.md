# Legacy parity audit — whole Quran, three gate modes

Audit of the current riwayah-agnostic engine against the frozen legacy
baselines in `tests/snapshots/phonemes/`, over all 77,433 words of surahs
1–114, in `continuous`, `verse` and `word` mode.

Every number and every phoneme string below was produced by running the code.
Nothing is quoted from memory.

Transliteration follows `.claude/rules/transliteration.md`: plain ASCII, no
diacritics (idgham, ikhfaa, izhar, tarqeeq, tafkheem, qalqalah, sakt, waqf,
wasl, aridah, muqattaat).

---

## 0. Baseline validation — the snapshots are real legacy output

A published legacy build (`quranic-phonemizer` **2.9**, from
`quranic_phonemizer-2.9.dist-info`) was run live over 15 disjoint chunks
spanning 1:1–114:6 (surahs 1, 2, 4, 7, 9, 12, 18, 24, 36, 43, 55, 78, 109,
114), in each of the three modes, using the exact `_stop_arguments` contract
from `tools/freeze_legacy_baselines.py`. The first and last word of each chunk
were excluded because a chunk edge is a ref edge in legacy and not a corpus
edge.

| mode | words compared | drift vs snapshot |
|---|---:|---:|
| continuous | 2,695 | **0** |
| verse | 2,695 | **0** |
| word | 2,695 | **0** |

A further 16 individually targeted live legacy calls (2:61:30, 68:1, 75:27,
83:14, 31:18, 7:189, 69:28–29, 24:50:5) also matched the snapshot exactly.

**Conclusion: no drift. The frozen snapshots are faithful published-v2.9
behaviour and are a valid stand-in for legacy throughout this report.**

---

## 1. Summary

"Boundary-only" = words that differ *solely* in which side of a word boundary
owns a sound that was merged across it; the phoneme sequence of the reading is
identical. That is not a difference in the reading and is excluded from the
genuine count. It is computed here per *run of adjacent differing words* and
then aligned token-by-token, which is strictly finer than `tools/parity.py`'s
per-verse `_same_sequence` test; the `parity.py` number is given alongside for
comparison.

| mode | total words | matching | match % | boundary-only | genuine differences | classes |
|---|---:|---:|---:|---:|---:|---:|
| `word` | 77,433 | 77,377 | **99.9277%** | 0 (parity.py: 0) | **56** | 5 |
| `verse` | 77,433 | 75,632 | **97.6741%** | 1,667 (parity.py: 1,626) | **134** | 10 |
| `continuous` — per-verse harness, as specified | 77,433 | 72,716 | **93.9083%** | 2,795 (parity.py: 1,017) | 1,922 | see §2 |
| `continuous` — surah-joined (true continuous) | 77,433 | 75,550 | **97.5682%** | 1,670 | **213** | 12 |

All four runs completed over the full corpus. No sampling anywhere. Runtimes:
26 s per mode for the per-verse runs, 414 s for the surah-joined continuous run.

**Genuine differences, true readings only** (`word` 56 + `verse` 134 +
surah-joined `continuous` 213) = **403 word-differences**, falling into
**17 distinct classes**: **7 regressions**, **7 justified fixes**,
**3 unclear / khilaf**.

The claim that the refactor introduced no regressions is **false**. Seven
distinct regression classes exist. Two of them are large (112 and 73 words in
continuous mode) and one of them silently discards a named Hafs exception that
`docs/domain-facts.md` and `docs/adr/004-rule-execution.md` both require.

`docs/conformance/gate-residues.md` documents only the 56 `word`-mode
differences, and its five classes are confirmed correct by this audit. It says
nothing about the 134 `verse`-mode ones beyond "the same classes, plus …
propagation into its neighbour", which is **not true**: seven of the ten
verse-mode classes do not occur in word mode at all, and six of those are
regressions.

---

## 2. A note on `continuous` mode: the harness prescription does not work

The prescribed plan — build each verse separately, plan
`(JOIN,)*n` with `right_context = next verse's Reading` — cannot reproduce
continuous recitation, and its 93.9083% is mostly a measurement artifact, not
an engine result.

`Recitation.build` takes a `right_context` but there is no `left_context`, and
`Recitation.perform` is verse-scoped: `BoundaryPlan.started_on(0)` is
unconditionally `True` because `before(0)` is `None`. Consequently every
verse-initial word is performed as if speech began there, and every verse-final
sound is performed without sight of the next verse. `right_context` turns out
to be consumed only by `canon/juncture.py::apply_cross_word_noon`, which
repairs the *IndoPak* split-tanween spelling; for Uthmani it is a no-op.

Of the 1,922 genuine word-differences that plan produces, **1,783 (92.8%) are
this harness artifact**:

| artifact shape | count | what it is |
|---|---:|---|
| `n w` → `w̃`, `n` → `ŋ`, `n j` → `j̃`, `n l` → `ll`, `n m` → `m̃`, `n rˤ` → `rˤrˤ`, `n n` → `ñ`, `n r` → `rr` | 1,547 | verse-final tanween/noon not assimilated to the next verse's first letter (idgham, ikhfaa, iqlab all missed) |
| `ʔ a` → `-`, `ʔ i` → `-`, `ʔ u` → `-`, `ʔ` → `-`, `ʔ a` → `i`, `ʔ u` → `i`, `ʔ a lˤlˤ aˤ:` → `i ll a:` … | 236 | verse-initial hamzat wasl pronounced instead of elided into the previous verse |

The engine **is** capable of true continuous reading: `Recitation.read` accepts
an arbitrary word tuple, so a whole surah can be read as one `Reading`. Built
that way — one `Reading` per surah, plus one word of overlap on each side so
that surah junctions are joined too, plan `(JOIN,)*(n-1) + (EDGE,)` — the
engine reproduces the legacy cross-verse sandhi exactly, e.g.
2:7:12 عَظِيمٌ `ʕ a ðˤ i: m u` + 2:8:1 وَمِنَ `w̃ a m i n a`.

**All continuous-mode findings below are from the surah-joined run
(97.5682%).** Anyone re-running `tools/parity.py` should implement continuous
this way; the per-verse plan measures the harness, not the engine.

---

## 3. `word` mode — 99.9277%, 56 genuine differences, 0 regressions

Ordered by count. This is the set already documented in
`docs/conformance/gate-residues.md`; the audit confirms all five classes and
their direction.

### W1 — small yaa / small waw carries the word's final vowel — 23 — JUSTIFIED FIX

| | |
|---|---|
| 2:26:4 | `j a s t a ħ j i:` ← legacy `j a s t a ħ j` (يَسْتَحْىِۦٓ) |
| 2:258:18 | `j u ħ j i:` ← legacy `j u ħ j` (يُحْىِۦ) |
| 7:127:17 | `w a n a s t a ħ j i:` ← legacy `w a n a s t a ħ j` (وَنَسْتَحْىِۦ) |
| 4:135:29 | `t a l w u:` ← legacy `t a l w` (تَلْوُۥٓا۟) |
| 12:101:14 | `w a l i jj i:` ← legacy `w a l i jj` (وَلِىِّۦ) |
| 43:13:1 | `l i t a s t a w u:` ← legacy `l i t a s t a w` (لِتَسْتَوُۥا۟) |

Current is correct. `ۦ` (U+06E6) and `ۥ` (U+06E5) *are* the word's final long
vowel; legacy ends the word on a bare consonant with no vowel at all, which is
not pronounceable.

### W2 — quiescent hamza after a started hamzat wasl — 11 — JUSTIFIED FIX

| | |
|---|---|
| 6:71:29 | `ʔ i: t i n a:` ← legacy `ʔ i ʔ t i n a:` (ٱئْتِنَا) |
| 10:15:11 | `ʔ i: t` ← legacy `ʔ i ʔ t` (ٱئْتِ) |
| 20:64:4 | `ʔ i: t u:` ← legacy `ʔ i ʔ t u:` (ٱئْتُوا۟) |
| 9:49:4 | `ʔ i: ð a n` ← legacy `ʔ i ʔ ð a n` (ٱئْذَن) |
| 2:283:16 | `ʔ u: t u m i n` ← legacy `ʔ u ʔ t u m i n` (ٱؤْتُمِنَ) |

Current is correct. Started on, a quiescent hamza after a prosthetic hamza
becomes the madd of that hamza's vowel (ibdal): `ʔi:ti`, not `ʔiʔti`.

### W3 — waw with fatha before the otiose alif, at waqf — 7 — JUSTIFIED FIX

| | |
|---|---|
| 2:237:18 | `j a ʕ f u:` ← legacy `j a ʕ f u w` (يَعْفُوَا۟) |
| 27:92:2 | `ʔ a t l u:` ← legacy `ʔ a t l u w` (أَتْلُوَا۟) |
| 18:14:12 | `n a d Q ʕ u:` ← legacy `n a d Q ʕ u w` (نَّدْعُوَا۟) |
| 30:39:5 | `l i j a rˤ b u:` ← legacy `l i j a rˤ b u w` (لِّيَرْبُوَا۟) |
| 47:4:28 | `l i j a b Q l u:` ← legacy `l i j a b Q l u w` (لِّيَبْلُوَا۟) |

Current is correct. Stopping drops the fatha, leaving a quiescent waw after a
damma, which is madd tabii by definition. Legacy is self-contradictory here:
it gives `hu:` for هُوَ and `jaʕfuw` for يَعْفُوَا۟ on the same shape.

### W4 — dual construct, stopped on — 5 — JUSTIFIED FIX

| | |
|---|---|
| 11:114:3 | `tˤ aˤ rˤ aˤ f a j` ← legacy `tˤ aˤ rˤ aˤ f a:` (طَرَفَىِ) |
| 12:39:1 | `j a: sˤ aˤ: ħ i b a j` ← legacy `… a:` (يَـٰصَـٰحِبَىِ) |
| 12:41:1 | same (يَـٰصَـٰحِبَىِ) |
| 49:1:7 | `j a d a j` ← legacy `j a d a:` (يَدَىِ) |
| 73:20:8 | `θ u l u θ a j` ← legacy `θ u l u θ a:` (ثُلُثَىِ) |

Current is correct. The kasra on the yaa exists to meet the next word's wasl
hamza, which proves the yaa is a consonant; stopping gives `-ay`. Legacy's
`-aa` is the nominative form of a word standing in the genitive.

### W5 — the disputed raa — 10 — UNCLEAR (khilaf; current matches the documented default)

| | |
|---|---|
| 11:81:9 | `f a ʔ a s r` vs legacy `f a ʔ a s rˤ` (فَأَسْرِ) |
| 15:65:1 | `f a ʔ a s r` vs legacy `f a ʔ a s rˤ` (فَأَسْرِ) |
| 20:77:6 | `ʔ a s r` vs legacy `ʔ a s rˤ` (أَسْرِ) |
| 89:4:3 | `j a s r` vs legacy `j a s rˤ` (يَسْرِ) |
| 10:87:8 | `b i m i sˤ rˤ` vs legacy `b i m i sˤ r` (بِمِصْرَ) |
| 12:99:10 | `m i sˤ rˤ` vs legacy `m i sˤ r` (مِصْرَ) |

Both words are named khilaf sites. `research/hafs/syntheses/tafkheem_tarqeeq.md`
§2G records the preferred defaults at waqf as **tarqeeq** for
يَسْرِ/أَسْرِ/فَأَسْرِ and **tafkheem** for مِصْرَ; current matches both,
legacy applies a purely mechanical "preceding sakin, then fatha → heavy" rule
and lands on the other wajh in both. Current is the better default; neither is
wrong outright.

---

## 4. `verse` mode — 97.6741%, 134 genuine differences, 6 regression classes

1,667 further words differ only in boundary ownership and are excluded.
Regressions first, then by count.

### V1 — REGRESSION — tanween loses its linking kasra before a hamzat wasl — 46

| | |
|---|---|
| 2:61:30 | `x aˤ j rˤ u n` vs legacy `x aˤ j rˤ u n i` (خَيْرٌ ٱهْبِطُوا۟) |
| 2:180:9 | `x aˤ j rˤ aˤ n` vs legacy `… aˤ n i` (خَيْرًا ٱلْوَصِيَّةُ) |
| 4:171:31 | `θ a l a: θ a t u n` vs legacy `… u n i` (ثَلَـٰثَةٌ ٱنتَهُوا۟) |
| 7:8:2 | `j a w m a ʔ i ð i n` vs legacy `… i n i` (يَوْمَئِذٍ ٱلْحَقُّ) |
| 11:42:8 | `n u: ħ u n` vs legacy `n u: ħ u n i` (نُوحٌ ٱبْنَهُۥ) |
| 9:30:3 | `ʕ u z a j rˤ u n` vs legacy `… u n i` (عُزَيْرٌ ٱبْنُ) |

**Legacy is right.** All 46 (and all 112 in continuous mode) are a tanween
immediately followed by a word beginning with `ٱ` (U+0671) — verified
mechanically for every one. Iltiqa al-sakinayn: the quiescent noon of the
tanween meets the quiescent letter after the elided hamzat wasl and must take
a kasra — *khayrun-i-hbitu*, *nuhun-ibnahu*. The current engine emits no vowel
at all, leaving two quiescent consonants in contact. This is the largest
single defect in the engine and it is unimplemented, not mis-triggered: the
kasra never appears anywhere in the corpus.

### V2 — REGRESSION — final pausal/otiose alif not dropped when joined — 69

| | |
|---|---|
| 2:258:21 | `ʔ a n a:` vs legacy `ʔ a n a` (أَنَا۠) |
| 3:81:30 | `w a ʔ a n a:` vs legacy `w a ʔ a n a` (وَأَنَا۠) |
| 18:38:1 | `… n a:` vs legacy `… n a` (لَّـٰكِنَّا۠) |
| 18:39:15 | `ʔ a n a:` vs legacy `ʔ a n a` (أَنَا۠) |
| 43:81:6 | `f a ʔ a n a:` vs legacy `f a ʔ a n a` (فَأَنَا۠) |
| 2:160:9 | `w a ʔ a n a:` vs legacy `w a ʔ a n a` (وَأَنَا ٱلتَّوَّابُ) |

**Legacy is right.** 66 of the 73 (continuous count) carry `۠` U+06E0, the
mark that says the alif is sounded at waqf and silent at wasl; the current
engine never consults it when joining. The remaining 7 are أَنَا written
without the mark but followed by a hamzat wasl (2:160:9, 15:49:4, 15:89:3,
20:13:1, 20:14:2, 27:9:3, 28:30:16), where the long alif must in any case be
dropped before the following quiescent letter. The engine does shorten
correctly in the general case — مُوسَى ٱلْكِتَـٰبَ gives `m u: s a`, فِى ٱلسَّمَـٰوَٰتِ
gives `f i:` — so the failure is specific to this lexical family.

### V3 — REGRESSION — raa after an elided hamzat wasl read light — 8

| | |
|---|---|
| 24:50:5 | `r t a: b u:` vs legacy `rˤ t a: b u:` (أَمِ ٱرْتَابُوٓا۟) |
| 5:106:35 | `r t a b Q t u m` vs legacy `rˤ …` (إِنِ ٱرْتَبْتُمْ) |
| 17:24:9 | `r ħ a m h u m a:` vs legacy `rˤ …` (رَّبِّ ٱرْحَمْهُمَا) |
| 21:28:11 | `r t a dˤ aˤ:` vs legacy `rˤ …` (لِمَنِ ٱرْتَضَىٰ) |
| 23:99:8 | `r ʒ i ʕ u: n` vs legacy `rˤ …` (رَبِّ ٱرْجِعُونِ) |
| 72:27:3 | `r t a dˤ aˤ:` vs legacy `rˤ …` (مَنِ ٱرْتَضَىٰ) |

**Legacy is right.** This is one of the two already-known regressions,
confirmed and now shown to have eight sites, not one. The kasra before each
raa is aridah — it belongs to a hamzat wasl or to the preceding word's linking
vowel and is incidental — so it does not lighten the raa; a quiescent raa
after an aridah kasra takes tafkheem. Current applies rule `tarqeeq` at every
one of the eight (rules on the word confirm `tarqeeq` + `wasl_elision`).

### V4 — REGRESSION — isti'la in the *next* word wrongly makes the raa heavy — 3

| | |
|---|---|
| 31:18:2 | `t u sˤ aˤ ʕʕ i rˤ` vs legacy `… i r` (تُصَعِّرْ خَدَّكَ) |
| 70:5:1 | `f a sˤ b i rˤ` vs legacy `… i r` (فَٱصْبِرْ صَبْرًا) |
| 71:1:7 | `ʔ a ŋ ð i rˤ` vs legacy `… i r` (أَنذِرْ قَوْمَكَ) |

**Legacy is right.** A quiescent raa after an original kasra is heavy only when
an isti'la letter follows **in the same word** (قِرْطَاس, مِرْصَاد, فِرْقَة). خ, ص
and ق here belong to the following word, so the raa stays light. These three
are the textbook counter-examples. Current annotates the word `tafkheem`.

### V5 — REGRESSION — idgham mutajanisayn taa → dal not applied across a word boundary — 2

| | |
|---|---|
| 7:189:20–21 | `ʔ a θ q aˤ l a t` + `d a ʕ a w a` vs legacy `ʔ a θ q aˤ l a` + `dd a ʕ a w a` (أَثْقَلَت دَّعَوَا) |
| 10:89:3–4 | `ʔ u ʒ i: b a t` + `d a ʕ w a t u k u m a:` vs legacy `ʔ u ʒ i: b a` + `dd a …` (أُجِيبَت دَّعْوَتُكُمَا) |

**Legacy is right.** A quiescent taa before a dal merges completely. The
mushaf's shadda on the dal is the orthographic statement of exactly that.
Current pronounces both letters separately.

### V6 — REGRESSION — idgham applied at a sakt site — 2

| | |
|---|---|
| 75:27:2–3 | `m a` + `rˤrˤ aˤ: q Q` vs legacy `m a n` + `rˤ aˤ: q Q` (مَنْ ۜ رَاقٍ) |
| 83:14:2–3 | `b a` + `rˤrˤ aˤ: n a` vs legacy `b a l` + `rˤ aˤ: n a` (بَلْ ۜ رَانَ) |

**Legacy is right.** The sakt at these two of Hafs's four sakt sites is
precisely what prevents the idgham; the noon of مَنْ and the lam of بَلْ stay
audible. Current lists both `sakt` **and** `idgham_bila_ghunnah` /
`idgham_mutaqaribayn` on the same word — it recognises the sakt and then
assimilates through it anyway.

### V7 — REGRESSION — the muqattaat clear-noon exception lost — 2 words (1 site here)

| | |
|---|---|
| 68:1:1–2 | `ñ u:` + `w̃ a l q aˤ l a m i` vs legacy `n u: n` + `w a l q aˤ l a m i` (نٓ وَٱلْقَلَمِ) |

**Legacy is right, and the current engine contradicts this repository's own
specification.** `docs/domain-facts.md` line 344: "narration exceptions (يسٓ
and نٓ keep a clear noon before a following waw)".
`research/hafs/syntheses/noon_meem_rules.md` tabulates both as *izhar mutlaq*.
`docs/adr/004-rule-execution.md` and `docs/adr/008-conformance-and-phases.md`
both name 36:1 and 68:1 as guarded fixtures. The current engine applies
ordinary idgham bi ghunnah instead. 36:1 does not surface in `verse` mode
because the two words fall in different verses; it appears in continuous mode
(§5).

### V8 — UNCLEAR — the disputed raa, joined — 1

89:4:3 يَسْرِ `j a s r` vs legacy `j a s rˤ`. Same khilaf as W5.

### V9 — UNCLEAR — notation for idgham mutajanisayn baa → meem — 1

11:42:15 ٱرْكَب مَّعَنَا: current `mm a ʕ a n a:`, legacy `m̃ a ʕ a n a:`. The
merged meem should be both geminate and carry ghunnah. `data/render/ipa.yaml`
offers `m` / `m̃` and gemination by doubling, but no geminate-plus-nasal token,
so current keeps the gemination and loses the ghunnah mark while legacy keeps
the ghunnah and loses the gemination. Both are lossy; this is a notation gap,
not a phonological verdict. Note current *does* emit `m̃` for idgham shafawi
(3:81:31), so it is at least inconsistent with itself.

### V10 — JUSTIFIED FIX — ikhfaa after a muqattaat noon — 1

27:1:1 طسٓ تِلْكَ: current `tˤ aˤ: s i: ŋ`, legacy `tˤ aˤ: s i: n`. The final
noon of سٓ meets a taa, an ikhfaa letter, and there is no named exception here
(the exception is only before waw at 36:1/68:1). Current is right.

---

## 5. `continuous` mode (surah-joined) — 97.5682%, 213 genuine differences

1,670 further words differ only in boundary ownership. Continuous mode is a
superset of verse mode: the same classes, with extra instances at verse and
surah junctions, plus four classes that only a joined reading can expose.

| class | count | verdict |
|---|---:|---|
| C1 = V1 tanween loses its linking kasra before hamzat wasl | 112 | **REGRESSION** |
| C2 = V2 final pausal/otiose alif not dropped when joined | 73 | **REGRESSION** |
| C3 = V3 raa after an elided hamzat wasl read light | 9 | **REGRESSION** |
| C4 = V7 muqattaat clear-noon exception lost | 4 | **REGRESSION** |
| C5 = V4 isti'la in the next word makes the raa heavy | 3 | **REGRESSION** |
| C6 — legacy drops the tanween noon at a surah junction | 3 | JUSTIFIED FIX |
| C7 = V5 idgham mutajanisayn taa → dal | 2 | **REGRESSION** |
| C8 = V6 idgham applied at a sakt site | 2 | **REGRESSION** |
| C9 — legacy drops a final quiescent baa at a surah junction | 2 | JUSTIFIED FIX |
| C10 = V10 ikhfaa after a muqattaat noon (27:1:1) | 1 | JUSTIFIED FIX |
| C11 — مَالِيَهْ هَلَكَ: idgham vs sakt-izhar | 1 | UNCLEAR (khilaf) |
| C12 = V9 notation for idgham baa → meem (11:42:15) | 1 | UNCLEAR |

Notes on the classes that are new in this mode.

**C2 extra sites.** Joining across verse ends exposes four more `۠` words that
verse mode never joins: 33:10:16 ٱلظُّنُونَا۠, 33:66:11 ٱلرَّسُولَا۠,
33:67:8 ٱلسَّبِيلَا۠, 76:15:8 قَوَارِيرَا۠ — e.g. 76:15:8 current
`q aˤ w a: r i: rˤ aˤ:` vs legacy `q aˤ w a: r i: rˤ aˤ`. All four are the
same regression as أَنَا۠.

**C3 extra site, 38:42:1** ٱرْكُضْ after وَعَذَابٍ, where the two regressions
compound: current `w̃ a ʕ a ð a: b i n` `r k u dˤ` against legacy
`w̃ a ʕ a ð a: b i n i` `rˤ k u dˤ` — the linking kasra is missing *and* the
raa is light.

**C4 — the second muqattaat site.** 36:1:1–36:2:1 يسٓ وَٱلْقُرْءَانِ: current
`j̃ a: s i:` + `w̃ a l q u rˤ ʔ a: n i`, legacy `j a: s i: n` + `w a l …`.
Legacy is right, for the reason given in V7.

**C6 — JUSTIFIED FIX, 3 words.** At a surah junction legacy loses the tanween
noon entirely:

| | |
|---|---|
| 6:165:21 | current `rˤrˤ aˤ ħ i: m u n` vs legacy `rˤrˤ aˤ ħ i: m u` (رَّحِيمٌ · الٓمٓصٓ) |
| 31:34:27 | current `x aˤ b i: rˤ u n` vs legacy `x aˤ b i: rˤ u` (خَبِيرٌ · الٓمٓ) |
| 106:1:1 | current `ll i ʔ i: l a: f i` vs legacy `l i ʔ i: l a: f i` (مَّأْكُولٍ · لِإِيلَـٰفِ) |

The first two are izhar before the hamza of the muqattaat and the noon must
sound; the third is idgham bila ghunnah into the lam, which is why current
geminates it. Legacy simply deletes the noon in all three. Current is right.

**C9 — JUSTIFIED FIX, 2 words.** Legacy deletes the final quiescent baa at a
surah junction: 94:8:3 فَٱرْغَب current `f a rˤ ɣ aˤ b Q` vs legacy
`f a rˤ ɣ aˤ`; 96:19:5 وَٱقْتَرِب current `w a q Q t a r i b Q` vs legacy
`w a q Q t a r i`. Current is right, qalqalah sughra included.

**C11 — UNCLEAR.** 69:28:4–29:1 مَالِيَهْ هَلَكَ: current `m a: l i j a hh a l a k a`
(idgham of the two haa's), legacy `m a: l i j a h h a l a k a` (clear).
`research/hafs/syntheses/waqf_ibtidaa.md` line 620 records both as legitimate
for Hafs — "Waqf, Sakt, or Wasl with Idgham … Sakt prevents the Idgham of the
two Ha's". Legacy takes the sakt-izhar wajh, current takes the idgham wajh.
Neither is wrong; the engine is silently choosing one, and there is no khilaf
option in `khilaf.yaml` for it.

---

## 6. Regressions, consolidated

Seven classes where legacy was right and the current engine is wrong, with
their worst-case (continuous) counts:

| # | class | continuous | verse | word | severity |
|---|---|---:|---:|---:|---|
| R1 | tanween loses its linking kasra before a hamzat wasl | 112 | 46 | 0 | unimplemented rule; largest defect |
| R2 | final pausal/otiose alif (`۠` U+06E0, and أَنَا) not dropped in wasl | 73 | 69 | 0 | mark never consulted when joining |
| R3 | raa after an elided hamzat wasl read light (aridah kasra) | 9 | 8 | 0 | `tarqeeq` fires where `tafkheem` is due |
| R4 | isti'la in the *next* word makes a quiescent raa heavy | 3 | 3 | 0 | isti'la lookup crosses a word boundary |
| R5 | idgham mutajanisayn taa → dal across a word boundary | 2 | 2 | 0 | rule not reaching across the boundary |
| R6 | idgham applied at a sakt site (75:27, 83:14) | 2 | 2 | 0 | `sakt` and `idgham` fire together |
| R7 | muqattaat clear-noon exception lost (36:1, 68:1) | 4 | 2 | 0 | documented Hafs exception missing |

`word` mode is clean: **all 56 of its differences are justified fixes or
khilaf**, and the `docs/conformance/gate-residues.md` account of them is
accurate. Every regression is a *joined-reading* regression, which is exactly
why a gate that only checks `word` mode found none of them.

## 7. Justified fixes, consolidated

| # | class | count | mode |
|---|---|---:|---|
| F1 | small yaa / small waw carries the final vowel | 23 | word |
| F2 | quiescent hamza after a started hamzat wasl → madd | 11 | word |
| F3 | waw with fatha before the otiose alif at waqf → madd tabii | 7 | word |
| F4 | dual construct gives `-ay` when stopped on | 5 | word |
| F5 | legacy drops the tanween noon at a surah junction | 3 | continuous |
| F6 | legacy drops a final quiescent baa at a surah junction | 2 | continuous |
| F7 | ikhfaa after the muqattaat noon of طسٓ (27:1:1) | 1 | verse, continuous |

## 8. Unclear

| # | class | count | note |
|---|---|---:|---|
| U1 | disputed raa: مِصْرَ ×4, أَسْرِ/فَأَسْرِ/يَسْرِ ×6 | 10 | both are named khilaf; current matches the defaults recorded in `tafkheem_tarqeeq.md` §2G, legacy does not |
| U2 | مَالِيَهْ هَلَكَ (69:28–29) | 1 | both wajh legitimate; current takes idgham, legacy takes sakt-izhar |
| U3 | geminate-plus-ghunnah meem (11:42:15) | 1 | notation gap in `ipa.yaml`; both sides lossy |

---

## 9. Method

- Engine: `quranic_phonemizer.api.recitation(Riwayah.HAFS)`, `Script.UTHMANI`,
  `render.recite.phonemes_by_word`, with `engine.laws.check_inscription` and
  `check_performance` asserted on every verse of every run.
- Plans: `word` = `(STOP,)*(n-1) + (EDGE,)`; `verse` = `(JOIN,)*(n-1) + (EDGE,)`;
  `continuous` run twice — once per verse with `(JOIN,)*n` and
  `right_context = next verse` as specified (§2), and once per surah with
  `(JOIN,)*(n-1) + (EDGE,)` over a `Reading` holding the whole surah plus one
  overlap word on each side, taking only the surah's own words.
- Comparison: word-by-word against `tests/snapshots/phonemes/{mode}.jsonl.gz`
  in canonical order. Adjacent differing words are grouped into runs and their
  token streams aligned with `difflib.SequenceMatcher`; a run whose two streams
  are equal is boundary-ownership only, and within a run only the tokens inside
  a non-equal opcode are counted as genuine.
- Nothing in this report is sampled or extrapolated. Every count is a full
  77,433-word pass.
