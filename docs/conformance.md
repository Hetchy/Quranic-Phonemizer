# Manual audit residues

The cross-script, legacy regression, roundtrip, attestation, and L1 tools are
manual diagnostics rather than automated gates. This file records their known
residue so a deliberate manual run has an explainable baseline.

The frozen legacy snapshot is a change detector rather than a correctness
oracle. A deliberate correction may therefore lower a parity floor; the same
change must update this file and leave a regression test for the corrected
reading.

| Gate | Now | Residue |
|---|---|---|
| cross-script, word | 99.997% | 2 words |
| cross-script, verse | **100.000%** | none |
| round-trip, uthmani | **100.000%** | none |
| regression, word | 99.910% | 70 words |
| regression, verse | 97.839% | see below |
| L1 | 17 rows over 287,057 slots | |
| attestations | 176 uthmani, 237 indopak | |

## Cross-script — 2 words

Both are IndoPak writing the elided form of an iltiqa al-sakinayn, and both
join to the same sounds as Uthmani; only the artificial stop that word mode
forces separates them.

| Ref | Uthmani | IndoPak | Joined |
|---|---|---|---|
| 26:61:2 | `تَرَآءَا` | `تَرَآءَ` | `tarˤaˤ:ʔa lʒamʕa:ni` both |
| 59:9:2 | `تَبَوَّءُو` | `تَبَوَّءُ` | `tabawwaʔu dda:rˤaˤ` both |

## Regression — 70 words

The oracle is the previous implementation with its own defects frozen in, so
this gate is a change detector and not a target. Every row is one of six
classes, and each class is a disagreement whose direction is established
independently of the oracle.

**20 + 3 — the small yaa and the small waw** (`يُحْىِۦ`, `وَلِىِّۦ`,
`تَلْوُۥٓا۟`, `فَأْوُۥٓا۟`, `لِتَسْتَوُۥا۟`). Uthmani writes the vowel with
`ۦ` and `ۥ`; the oracle drops it and ends the word on the consonant. `juħj`
for `يُحْىِۦ` says no vowel is written where one is.

The twentieth yaa row is `ءَاتَىٰنَِۧ` 27:36, the `yaa_aatani_waqf` khilaf
site: the published default is ithbat, which sounds the final yaa at the
stop, while the oracle drops it. The hadhf face remains selectable.

**11 — the quiescent hamza after a prosthetic one** (`ٱئْتِ`, `ٱئْتُوا۟`,
`ٱئْذَن`, `ٱؤْتُمِنَ`). Read alone, every one of these is started on, and a
quiescent hamza after a started prosthetic one becomes the madd of its
vowel: `ʔi:ti`, not `ʔiʔti`.

**16 — the disputed raa** (`مِصْرَ` ×4 heavy, `يَسْرِ`/`أَسْرِ`/`فَأَسْرِ`
×6 light, `وَنُذُرِ` ×6 light). `hafs/research/tafkheem-tarqeeq.md` §2G
tabulates the defaults and records that the oracle's mechanical rule
diverges from them at 89:4; the oracle also reads the six `raa_wanuthur_waqf`
endings heavy where the published default is light. All sixteen are khilaf
sites, so the other wajh is selectable.

**2 — the seen-default Seen/Saad sites** (`يَبْصُطُ` 2:245:14,
`بَصْطَةً` 7:69:22). The written small seen is above the saad at both sites,
so `seen` is the published default and `saad` remains selectable. The frozen
oracle reads saad at both.

**7 — a waw carrying fatha before the otiose alif** (`يَعْفُوَا۟`,
`أَتْلُوَا۟`, `لِّيَرْبُوَا۟`, `لِّيَبْلُوَا۟`, `وَنَبْلُوَا۟`,
`لِّتَتْلُوَا۟`, `نَّدْعُوَا۟`). The stop drops the fatha and leaves a waw
quiescent after a damma, which is madd tabii by definition. The oracle
answers this shape two ways: `هُوَ` gives `hu:` and `يَعْفُوَا۟` gives
`jaʕfuw`, so it contradicts itself rather than us.

**5 — form VIII with lam for its first radical** (`ٱلْتَقَى` ×3,
`ٱلْتَقَتَا`, `ٱلْتَقَيْتُمْ`). Started on, the oracle gives `ʔaltaqaa`. Fatha is
the article's helping vowel and the article makes nouns; these are verbs, and
a verb takes a damma only when its third letter carries one. The third letter
here carries a fatha, so the prosthetic hamza takes a kasra: `ʔiltaqaa`. What
separates them from `ٱلتَّقْوَىٰ` is written in both scripts -- taa is a sun
letter, so the article before one always spells the shadda of its
assimilation, and these words have none.

**5 — the dual construct** (`طَرَفَىِ`, `يَـٰصَـٰحِبَىِ` ×2, `يَدَىِ`,
`ثُلُثَىِ`). The kasra on the yaa is there to meet the wasl hamza of the next
word, which is what proves the yaa is a consonant. Stopping gives `-ay`; the
oracle's `-aa` is the nominative of a word standing in the genitive.

## Warsh wasl and iltiqa registers

`tests/conformance/test_warsh_registers.py` asserts the reviewed counts from
`docs/warsh/research/v2/wasl-hamza.md` and `iltiqa.md`: the canonical start
register (13,480 onsets, 11,982 A / 1,097 I / 401 U), the sixteen started
silent-qata forms, the 38-row damm connected-form register, and the generated tanwin
repair family (44 sites, 40 I / 4 U). The runtime start quality is supplied
by the source wasl mark; the register test reconciles every supplied mark
against the canonical derivation, whose closed disagreements are the passive
`اَ۟سْتُحِقَّ` delta, the temporary-damm `اتقوا` family, the passive
`اَ۟تُّبِعُواْ`, and the Warsh-only wasl readings of `اتبع` and `اسر`.

Known residue deferred to later verticals:

- The `التي` family is written without its geminate lam in this source and
  currently reads a single lam; its start quality is already the article's A.
- The joined outcomes of the sixteen silent-qata words use the connected
  single-hamza chapter and land with that vertical; only their started forms
  are asserted here.
- The general 1,665-site connected-vowel partition (770 A / 381 I / 514 U)
  remains a documented research invariant, not a count of public
  `iltiqa_haraka` occurrences. Only runtime-inserted tanwin and spelled-name
  vowels receive that rule; lexical and morphological connected forms do not.

## Warsh naql registers

The naql vertical cleared the earlier article residue: `وَالَارْضِ` and its
family now project their wasl onset, the carried article vowel, and the
`naql` annotation, so `hamza_wasl_silent`/`hamza_wasl_fatha` behave normally
around the internal naql.

`tests/conformance/test_warsh_registers.py` asserts the mechanical latent
register generated from the supplied script families and canonical hosts:

- 1,658 within-ayah short-qata boundaries, every one after a matching written
  moved haraka or a tanwin host: 1,589 written-haraka forms (A/I/U) and
  69 damm-stroke forms.
- 308 adjacent-ayah short-qata edges: 306 tanwin-final hosts, the one written
  moved haraka of `وَانْحَرِ` before 108:3, and one spelled-opening edge at
  canonical 29:1 -> 29:2. Five further latent verse starts open a surah and
  join nothing. The spelled-opening edge does not perform naql: a
  disjoined-letter opening ends as it would at a pause, so `اَحَسِبَ` keeps
  its restored qata even when the reader runs on.
- Of 227 selected-script initial-long shapes (177 A, 47 U, and 3 I), 224 are
  badal mughayyar bin-naql: 208 within ayahs and 16 across ayah edges. The
  other three are hamza-meeting forms at 2:140:14, 20:22:10, and 58:13:1.
  Ordinary naql does not transfer a long nucleus.
- The article register is exactly the documented 1,307: 1,283 written
  article alifs (955 wasl-marked, 328 prefixed bare), 22 suppressed-alif
  prefix forms, and the two interrogative tokens; the reviewed long bases
  cover 214 tokens.
- The one adjacent-ayah boundary written with a full qata after a sakin host
  is `كِتَٰبِيَهْۖ إِنِّے`, matching the authored tahqiq-default exclusion.

The research file's 1,550 within-ayah and 180 adjacent-ayah subtotals in
`docs/warsh/research/v2/naql.md` are not reproducible from the supplied
families under any principled cut; the mechanical totals above supersede
them for conformance. Two more intentional deltas against that file's
tables: dad is not a qalqala letter, so waqf on `اِ۬لَارْضِ` ends
`l a rˤ dˤ` with no release; and the received `عَاداٗ اَ۬لُّاول۪ىٰ` junction
stays outside both the article family and the tanwin repair register until
its idgham-with-naql face is implemented.

## Verse mode

97.839% counts a word wrong when a sound merged across a boundary is credited
to the neighbour; the harness prints the phoneme sequence separately, and
that is 77,424 of 77,433. The nine words left are the two Seen/Saad sites
above, `يَسْرِ` at 89:4, and the six verse-final `وَنُذُرِ` endings, all
already listed under the disputed raa. `ءَاتَىٰنَِۧ` does not appear: it is
mid-verse, so verse mode joins it and the waqf-only selector is masked.
