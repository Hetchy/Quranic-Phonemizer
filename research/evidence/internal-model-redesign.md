# Evidence pack — internal-model redesign

Shared factual substrate for the design round. Every number here was measured
against the repository at `e0d9fb9` on 2026-07-26, not quoted from a prior
document. Where a claim could not be measured it is marked **unverified**.

Design agents must treat this file as the source of facts and must not
re-derive them. If a spike contradicts something here, that contradiction is a
finding — report it.

---

## 1. What actually landed

`e0d9fb9` replaced a 7,372-line implementation with 2,388 lines.

| Area | Files |
|---|---|
| entry | `api.py`, `engine.py`, `result.py` |
| model | `model/orthography.py`, `model/segments.py`, `model/recitation.py` |
| rules | `rules/{apply,context,boundaries,noon_tanween,meem,idgham,raa,hamza_wasl,vowels}.py` |
| support | `corpus.py`, `parsing.py`, `expansion.py`, `rendering.py`, `rule_data.py`, `resources.py`, `dataio.py`, `hafs.py` |
| data | `data/shared/{tajweed,render,muqattaat}.yaml`, `data/riwayat/hafs/{script,exceptions}.yaml` |

Roughly 5,000 of the deleted lines were public surface, not internal
machinery: `tajweed_mappings`, `letter_phoneme_mappings`,
`character_phoneme_mappings`, `phonetic_text`, `silent_flags`, simple mode,
`save`, `show_table`, text matching, and the runtime phoneme overrides.

### Phoneme parity is real — independently verified

The legacy tree at `b3bc53a` was exported and run over 1–114 in all three
boundary modes and byte-compared against `tests/snapshots/phonemes/`:

| Mode | Bytes | Match |
|---|---:|---|
| continuous | 2,285,752 | exact |
| verse stops | 2,264,215 | exact |
| stop on every word | 2,208,316 | exact |

Caveat on provenance: `tools/freeze_phonemes.py` calls `.recitation.words`,
which did not exist at `b3bc53a`. Both the tool and the snapshots were added in
`e0d9fb9`, so the manifest's `source_revision: b3bc53a` is not provable from
inside the repository. The comparison above is what establishes it.

---

## 2. The orthographic accident under the nūn rules

Nūn followed by a letter, whole corpus:

| Written state | Following class | Count |
|---|---|---:|
| bare (no harakah, no tanween, no shaddah) | assimilating | **5,412** |
| bare | iẓhār (throat) | 0 |
| explicit sukūn `نْ` | iẓhār | 1,590 |
| explicit sukūn `نْ` | assimilating | **126** |

The 126 decompose exactly:

| Count | Case | Example |
|---:|---|---|
| 122 | same-word `نْ` + `ي` | `ٱلدُّنْيَا` — iẓhār muṭlaq |
| 3 | same-word `نْ` + `و` | `قِنْوَانٌ` — iẓhār muṭlaq |
| 1 | cross-word `نْ` + `ر` | 75:27 `مَنْ ۜ رَاقٍ` — sakt blocks idghām |

`rules/noon_tanween.py:17` treats *explicit sukūn as not-sākinah*. Output is
correct for all 1,716 explicit-sukūn cases — but by coincidence of Uthmani
orthography, which writes the nūn bare exactly when assimilation fires. Three
distinct domain rules (nūn sākinah, iẓhār muṭlaq, sakt-blocks-idghām) are
collapsed into one glyph shortcut. The same shortcut appears for lām at 83:14
`بَلْ رَانَ`. `meem.py:17` uses the identical shortcut.

Under IndoPak, which writes explicit sukūn throughout, all 5,412 assimilations
would disappear. This is the single sharpest argument for the canonical
boundary.

---

## 3. Two script sources, word-aligned

See `corpus_sources/riwayat/hafs/scripts/README.md` for the full comparison.
Headline: 77,433 slots each, 6,236 of 6,236 ayahs matching, 69 vs 85 distinct
scalars, and neither script's mark inventory is a superset of the other's.

Load-bearing consequences:

1. **Mark semantics are script-scoped.** Uthmani types imāla (`۪`), tashīl
   (`۬`), ishmām (`۫`); IndoPak marks 11:41 and 41:44 with one *generic*
   "noted here" flag `ؔ` U+0614 (45 sites, mostly waqf and verse-number
   annotations) and omits ishmām entirely.
2. **Coverage is asymmetric both ways.** IndoPak marks the seen/ṣād khilaf more
   explicitly than Uthmani (`ۜ` plus `ࢵ` U+08D5) and marks iqlāb explicitly
   (546 sites) where Uthmani marks it not at all.
3. **A location table must be able to supply what a script omits**, with a
   present mark validating rather than driving. Uthmani drops the seven-alifs
   distinction nowhere but IndoPak drops it at all 66 sites.
4. **Exception scope is `riwayah × script`.** 2:72 exists only because Uthmani
   writes an ornamental dagger-alef construct; IndoPak resolves it to a plain
   hamza. Filing it under `riwayat/hafs/exceptions.yaml` is the wrong key.

---

## 3b. Hamzat al-waṣl — a second, larger script accident

`ٱ` U+0671 appears **13,483 times in Uthmani** and **once in IndoPak** (3:78:23,
evidently an inconsistency in that source). Hamzat al-waṣl governs elision, the
ibtidāʾ helping vowel, and both iltiqāʾ repairs. Any rule matching
`Letter.HAMZA_WASL` — as `rules/apply.py:39` and `rules/hamza_wasl.py` do — is
as script-bound as the nūn shortcut in §2, at 2.5× the volume.

### How much of it is derivable?

Measured over the 13,482 Uthmani word slots carrying it:

| Count | Class | Supplied by |
|---:|---|---|
| 11,995 (89%) | the article `ٱل` | one rule |
| 774 | initial, non-article | canonical skeleton lexicon |
| 713 | medial, non-article (`وَٱدْعُوا۟`) | same lexicon |

The 1,487 non-article slots reduce to **526 distinct canonical skeletons**
(`ٱبتغ`, `ٱتبع`, `ٱسم`, `ٱبن`, `ٱئتونى`, …) — Arabic morphology, keyed by
canonical skeleton, therefore script-independent and riwayah-scoped.

The always-silent mark decomposes the same way. Of 3,970 Uthmani `۟` sites:

| Count | Class |
|---:|---|
| 3,640 (92%) | otiose alef after word-final wāw (`كَفَرُوا۟`) — one rule |
| ~300 | five small lexical classes (`أُو۟لَـٰٓئِكَ` 255, `ٱمْرُؤٌا۟` 42, `مِا۟ئَة` 10) |
| ~25 | genuine one-offs |

**Consequence for the design:** supplying what IndoPak omits is not a table of
~10⁴ location rows. It is two rules, one canonical lexicon of order 10², and a
few dozen one-offs. A location table that grows to 10⁴ entries is a signal that
a rule is missing, not that the corpus is irregular.

## 4. Two domain defects, both inherited from legacy and preserved by parity

### 4.1 `طسٓ` 27:1 into `تِلْكَ` — missing ikhfāʾ

`طسٓ` expands to `طَا` + `سِينْ`; the final nūn is permanently sākin and the
next word starts `ت`, an ikhfāʾ letter.

| Reading | Current | Correct |
|---|---|---|
| joined | `tˤ aˤ: s i: n` | `tˤ aˤ: s i: ŋ` |
| stopped on 27:1:1 | `tˤ aˤ: s i: n` | unchanged |

Cause: `expansion.py:76` sets `allow_forward_rules=index < last`, blanket-
blocking the final expanded name from seeing the next word. That substitutes
one blanket block for the two named Hafs exceptions that actually exist.

Regression guards — these must not move: `يسٓ` 36:1 and `نٓ` 68:1 stay clear
`n` before `و` (named exceptions); `طسٓمٓ` 26:1/28:1 stay `m` (iẓhār shafawī);
`عٓسٓقٓ` 42:2 and `قٓ` 50:1 end `f`; `صٓ` 38:1, `الٓمٓصٓ` 7:1, `كٓهيعٓصٓ` 19:1
end `d Q`.

### 4.2 `الٓمٓ` 3:1 into `ٱللَّهُ` 3:2 — missing iltiqāʾ repair

Final sākin mīm of `مِيمْ` meets the sākin first half of the geminate lām once
the hamzat al-waṣl is dropped in waṣl. Hafs repairs with a **fatha**, not the
usual kasra.

| Reading | Current | Correct |
|---|---|---|
| joined | `… m` · `ll a: h u` | `… m a` · `lˤlˤ aˤ: h u` |
| verse stops | `… m` · `ʔ a lˤlˤ aˤ: h u` | unchanged |

Two defects from one cause: the missing vowel also flips the Name's lām from
heavy to light, because `rules/apply.py:84` looks at the previous *segment* and
finds a consonant. IndoPak writes this word as `ال࢜مَّ࢜` — with the fatha —
independently confirming the expected output. 2:1 is `ال࢜مّ࢜`, no fatha, and
must not move; 29–32:1 are unaffected.

This is the **third** flavour of inserted helping vowel, alongside the
hamzat-al-waṣl vowel (fatha/kasra/damma by grammar) and the iltiqāʾ kasra after
tanween. Three flavours is an argument for one attributed insertion mechanism.

---

## 5. Khilaf seeds (kinds 1 and 2 only — in scope for the design)

### Token/inventory choice

Legacy exposed `iqlab_phoneme` and `ikhfaa_shafawi_phoneme` as call-time
overrides; `e0d9fb9` deleted both. Restoring selectable `m̃` vs `ŋ` is partly a
regression fix. Note that `render.yaml` currently maps `nasal` and
`nasal_emphatic` to the *same* token `ŋ`, and `Nasal.emphatic` is computed at
`noon_tanween.py:29,67` but cannot affect output.

### Per-location lexical khilaf — seen for ṣād, 4 union sites

**Corrected 2026-07-26.** An earlier revision of this file claimed exactly 3
sites and named `ࢵ` U+08D5 as a khilaf marker. Both were wrong.

| Location | Word (Uthmani) | Uthmani mark | IndoPak mark |
|---|---|---|---|
| 2:245:14 | `وَيَبْصُۜطُ` | `ۜ` U+06DC | `ۜ` U+06DC |
| 7:69:22 | `بَصْۜطَةً` | `ۜ` U+06DC | `ۜ` U+06DC |
| 52:37:7 | `ٱلْمُصَۣيْطِرُونَ` | `ۣ` U+06E3 | `ۜ` U+06DC |
| 88:22:3 | `بِمُصَيْطِرٍ` | **none** | `ۜ` U+06DC |

`ࢵ` U+08D5 is an ordinary IndoPak waqf sign at 95 sites (`بِالْهُدٰيࣕ`,
`فِيْهِࣕ`, `بِنَا࢜ءًࣕ`), unrelated to khilaf.

Neither script carries the full inventory: Uthmani marks 3 sites with two
different scalars, IndoPak marks 4 with one. The khilaf inventory is therefore
a riwayah fact that a present mark validates — it cannot be derived from either
script.

Selecting `س` changes the **canonical letter**, which changes inherent
emphasis, vowel colouring, and the rāʾ look-back. Variant selection therefore
cannot live in the renderer; it must resolve before the rules run.

### Polysemous marks exist in *both* scripts

Uthmani `ۜ` U+06DC, 7 sites: sakt at 18:1:11, 36:52:6, 69:28:4, 75:27:2,
83:14:2; seen-khilaf at 2:245:14, 7:69:22. `script.yaml` currently lists `ۜ`
under `structural`, so **both** meanings are discarded at parse time. `ۣ`
U+06E3 and `۫` U+06EB (ishmām, 12:11:6) are likewise discarded.

IndoPak `ࣝ` U+08DD, 7 sites: sakt at 36:52:6, 75:27:2, 83:14:2; word-final
waqf at 7:23:4, 7:184:2, 12:29:4, 28:23:24. It is **absent** at Uthmani's
18:1:11 and 69:28:4.

So the sakt fact is authoritative in **neither** script — 5 Uthmani sites and 3
IndoPak sites, overlapping in 3. Marks-validate-tables-supply has to be a law,
not a convenience.

### Out of scope, recorded as open research

`يسٓ وَٱلْقُرْءَانِ` and `نٓ وَٱلْقَلَمِ`: two wajhs (iẓhār and idghām) are
commonly reported for Hafs via Shāṭibiyyah with iẓhār practised. **Unverified**
— needs a domain reference. Also unverified: whether 69:28 and 18:1 sakt are
obligatory or permissible, and the `ضُؔعْفٍ` 30:54 damma/fatha khilaf which
IndoPak flags.

---

## 6. Lexical-table coverage (previously untested)

| Table | Entries | Corpus matches | Note |
|---|---:|---:|---|
| `allah_words` | 12 skeletons | 2,704 words | 178 words contain shaddah-lām + hāʾ and are correctly *not* matched (`كُلَّهَا`, `لَعَلَّهُمْ`, `لَّهُۥ`) |
| `muqattaat.forms` | 14 forms | 30 expansions | 0 form-matched-but-not-expanded |
| `hamza_wasl` kasra patterns | 10 prefixes | 95 words | prefix matching is load-bearing: `ٱءتو` matches 7 words, of which only the 5 `ٱئْتُونِى` are in `started_ituuni`; 20:64 and 45:25 `ٱئْتُوا۟` correctly are not |

---

## 7. Structural findings in the landed code

Attribution is not merely absent — it is destroyed during the run:

- `rules/vowels.py:47` — `owner.segments.pop(index)`: the long vowel is removed
  from the harakah's owner and re-emitted owned by the carrier. Joint ownership
  is unrecoverable.
- `rules/noon_tanween.py:31`, `rules/meem.py:32` — assimilation writes
  `following.segments = [...]` and sets `resolved = True`. The target's own
  realization is overwritten by its neighbour; the source/target relation is
  not recorded.
- `engine.py:79-82` — everything is flattened into `WordRealization.segments`.

Named rules dissolved into emergent behaviour:

- `rules/idgham.py:28` — bare and unshadda'd ⇒ emit nothing. That one line
  implements lām shamsiyyah, mutamāthilayn, mutaqāribayn, and mutajānisayn
  kāmil at once. The only surviving pair table is `{ط: [ت]}`. The four families
  are indistinguishable in the model, and any bare consonant is silenced with
  no check that a valid partner follows.
- `model/segments.py:25` — `Nasal` collapses ikhfāʾ ḥaqīqī, iqlāb, and ikhfāʾ
  shafawī into one value with no rule identity.

Riwayah seam is a path bundle, not a seam:

- `resources.py:9` — `RiwayahResources` holds seven `Path`s and no behaviour.
- `engine.py:8,38,77` — `from .hafs import …`, called unconditionally. Adding
  Warsh means editing `engine.py`.
- `parsing.py` — aliases apply to letters, harakāt, tanween, small vowels and
  shaddah, but marks (`:162`), letter hints (`:90`), stop signs (`:131`) and
  structural chars are matched on the **raw** scalar. The generic alias map is
  partial.

Symptom-named types:

- `SourceMark.SECOND_HAMZA` (`orthography.py:92`) names U+06EC after the
  outcome at one location, in the *script* layer, while 41:44 is *also* a
  location exception. `OrthographicHint` (`orthography.py:95`) has one member
  existing solely to find one letter at 27:36:8, although U+06E7 occurs 39
  times. `hafs.py:82` `_replace` overwrites the first letter matching a letter
  identity; `hafs.py:79` maps a HAMZA letter to a `Vowel` segment.

Other hygiene: `"ˤ"` and `":"` are hardcoded in `rendering.py:86-88` while
every other symbol is data; emphasis is encoded two incompatible ways (baked
into `ص: sˤ` vs overlaid via `emphatic: {ر: rˤ}`); `rendering.py:75` silently
drops `geminated` and `emphatic` when `nasalized` is set; `stop_refs` are
unvalidated so a typo is a silent no-op (`engine.py:132`); `StopSign.EITHER_STOP`
is parseable but not requestable; `expansion.py:42-50` returns the same `()` for
"not muqaṭṭaʿāt" and "muqaṭṭaʿāt with unexpected diacritics".

---

## 8. Frozen legacy projections

`research/legacy-baselines/` holds the pre-refactor public views for 1–114 in
all three boundary modes, produced by `tools/freeze_legacy_baselines.py` from
the `b3bc53a` export. See its `manifest.json` for row counts and hashes.

These are an **information-coverage reference, not a correctness oracle.** The
question they answer is whether the new internal model retains enough to
reconstruct them. Known distortions to expect:

- row granularity differs per view — `tajweed_mappings` emits extra rows for
  expanded muqaṭṭaʿāt sub-words (locations like `2:1:1:0`), while
  `character_phoneme_mappings` is one row per source word;
- `tajweed_mappings` entries omit some diacritics that
  `character_phoneme_mappings` retains;
- muqaṭṭaʿāt tajweed came from a hand-authored YAML block, not from the
  pipeline, so those rows are assertions rather than derivations;
- both muqaṭṭaʿāt defects in §4 are baked into every view.
