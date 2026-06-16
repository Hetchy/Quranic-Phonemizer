# Silent-Letter / Single-Pronounced-Grapheme Audit

## Why this exists

A phoneme always has a sound, but it is frequently written with **several
graphemes** of which only **one is actually pronounced** — the rest are silent
(hamza wasl, lam shamsiyah, the otiose alef, idgham-assimilated noon, …). The
Inspector Timestamps tab wants to highlight, per phoneme, the **one** grapheme
that is uttered, rather than lighting up the whole silent cluster.

This audit answers: *across the whole muṣḥaf, in both continuous and stopping
recitation, is every silent grapheme accounted for, so that each phoneme group
reduces to exactly one pronounced grapheme?*

Reproduce with `dev/audit_silent_letters.py` (`--mode continuous` /
`--mode random-stops`).

## How the letter-phoneme mapping already helps

`result.letter_phoneme_mappings()` already groups every silent grapheme into the
same flat entry as its sounding neighbour, so each entry maps *one-or-more
graphemes → a phoneme run*. The audit therefore reduces to two checks:

- **Check A — silent-letter completeness.** Every silent letter (no audible
  phoneme in the flat output) must carry a tajweed rule that explains the
  silence. A silent letter with no explaining rule is a missing/implicit rule.
- **Check B — single sounding grapheme.** Every flat entry must contain exactly
  one *distinct* sounding letter. Entries with ≥ 2 cannot be reduced to a single
  highlight target.

### "Sounding in the flat output" ≠ raw per-letter phonemes

Two redistributions mean the raw `letter_mappings[].phonemes` is **not** a
reliable highlight signal — `dev/audit_silent_letters.py::pronounced_in_flat`
mirrors both:

| Case | Raw mapping | Flat output (what to highlight) |
|---|---|---|
| **Iltiqaa** (long vowel shortened before hamza wasl, e.g. `فِى ٱل…`) | the vowel letter keeps the demoted short vowel | vowel letter is **silent**; the short vowel moves back onto the preceding consonant |
| **Waqf tanween** (stopping on `…ًا`) | the consonant carries the `a:` | the `a:` moves onto the **alef**, which becomes the sounding madd carrier |

Also note `vowel_silent` is **over-tagged** in the raw layer: it is attached to
pronounced madd carriers like the `ى` of `مُوسَىٰ` (which sounds `a:`).
`tajweed_mappings()` strips it from madd carriers, but anything reading the raw
`letter_mappings` must not treat a letter as silent just because it carries
`vowel_silent` — check the phonemes.

## Results — continuous (all 114 surahs at once)

```
words 77,433 · letters 326,199 · flat entries 304,667
silent letters 30,337 · multi-grapheme entries 29,574

CHECK A  silent letters with no explaining rule : 3,145
CHECK B  entries with ≥2 sounding graphemes      : 708
CHECK B  entries with 0 sounding graphemes (anom): 3
```

Silent letters, by explaining rule:

| Rule | Count |
|---|---|
| `hamza_wasl_silent` | 13,472 |
| `lam_shamsiyah` | 5,283 |
| `vowel_silent` | 4,051 |
| **(none — see Finding 1)** | **3,145** |
| `silent_iltiqaa_sakinayn` | 2,682 |
| `idgham_ghunnah_noon` | 1,022 |
| `idgham_bila_ghunnah_noon` | 338 |
| `idgham_mutamathilayn` | 148 |
| `idgham_shafawi` (target) | 125 |
| `idgham_mutajanisayn_kamil` | 58 |
| `idgham_mutaqaribayn` | 13 |

## Findings

### Finding 1 — the tanween alef/maksura is silent but carries no rule (3,145)

The **only** systematic Check A gap. The silent alef (`ـًا`, e.g. `نَارًا`,
`رِزْقًا`) and silent alef-maksura (`ـًى`, e.g. `هُدًى`) that follow a fathatan
are silent **when continuing** (the `an` nasal sits on the consonant; the alef
is the orthographic *alif al-wiqāyah*), yet they receive **no source rule** —
not even `vowel_silent`.

- Breakdown: 3,052 `ا` + 93 `ى`. (Context: the alef follows every consonant
  carrying fathatan — `ر ل م د ن ب ق ع …`.)
- It is **handled in the flat mapping** anyway: the merge falls back to a
  by-character `PREV` merge that the builder internally labels
  `vowel_lengthening_failure` (a tell-tale name), so the alef is silently glued
  to the consonant. The gap only bites a consumer that decides silence from
  **tajweed rules** instead of the flat grouping.
- **When stopping**, this same alef flips to the **sounding** madd carrier
  (madd ʿiwaḍ → `a:`); it is *not* a violation there. So any fix must be
  context-aware (silent continuing, sounding at waqf), exactly mirroring
  `pronounced_in_flat`.
- **Recommendation (needs a decision):** tag the continuing tanween alef/maksura
  with `vowel_silent` (or a dedicated `tanween_alef_silent`) so the tajweed
  layer is self-consistent. This adds rules to `tajweed_mappings()` output, so
  it is a deliberate change, not a silent bugfix.

### Finding 2 — `idgham_shafawi` is the only genuine "two sounding graphemes" case (708)

Every Check B ≥2-sounding entry is مْ + م (`لَهُم مَّرَضٌ` → `'م م'` →
`['m̃','a']`), where the source meem carries the geminated nasal and the target
meem its vowel — both audible. This is the single pattern where one phoneme
group cannot be reduced to one grapheme automatically.

`idgham_shafawi` is **dual**, and the renderer chooses per-context:

- **both sounding** (708) — target meem keeps its own vowel; *or*
- **target silent** (125, counted under `idgham_shafawi` in Check A) — when the
  target meem's vowel is absorbed by a following long vowel (`لَكُم مَّا` →
  source `م`=`['m̃']`, target `م`=`[]`).

**Highlight convention needed:** for the both-sounding case, pick one meem to
highlight (recommend the **second/target meem** — it bears the shaddah and the
held ghunnah). This is the one place the highlight rule must be hand-specified.

### Finding 3 — madd silah (`ۥ`/`ۦ`) silent at waqf is handled implicitly

The connecting silah (`ـهُۥ`, `ـهِۦ`) lengthens to `u:`/`i:` when continuing
into a consonant, and goes **silent when stopping** (`تَأْخُذُهُۥ` stop →
`'هۥ '` → `['h']`). Because the silah is an **extension** of the haa (not a base
letter), it merges into the haa entry and never appears as a competing sounding
grapheme — Check A skips it and Check B sees a single sounding haa. No rule is
attached, but there is no ambiguity. A highlighter must treat the silah
extension as silent-when-its-base-has-no-long-vowel.

### Finding 4 — multi-silent / cross-word chains already collapse correctly

Sequences of 2–3 silent graphemes, including across word boundaries
(`فِى ٱلْأَرْضِ` → `'ى ٱل'` → `['l']`: silent yaa + silent hamza-wasl + sounding
lam; cross-word noon idgham `'ن ل'`), all reduce to a single sounding grapheme.
No violations.

### Anomalies (3) — audit heuristic limitation, not a phonemizer bug

Three iltiqaa entries (`'ا '`→`['a']`, `'ى '`→`['i']`) hit the builder's
`vowel_entry_idx == 0` fallback: the long vowel is **not** demoted (kept as a
short vowel with a space suffix) because there is no preceding consonant in the
entry to receive it. `pronounced_in_flat` over-eagerly silences them. Cosmetic;
listed for completeness.

## Results — stopping (50k random waqf words)

For each of 50,000 randomly-sampled words, its verse is phonemized **stopping on
that word**, so the word is rendered in real waqf context.

```
words 978,669 · letters 4,089,311 · flat entries 3,824,053
silent letters 371,011

CHECK A  silent letters with no explaining rule : 27,697   (all char ا/ى, all continuing)
CHECK B  entries with ≥2 sounding graphemes      : 8,845    (all idgham_shafawi)
CHECK B  entries with 0 sounding graphemes (anom): 50       (iltiqaa heuristic edge)
```

**The decisive result: zero `stop=True` Check A violations.** Across 50k waqf
points, stopping introduces **no** new unexplained silent letter. Every Check A
violation is still the tanween alef/maksura **on a continuing word**
(26,547 `ا` + 1,150 `ى`) — when the stop actually lands on a tanween word the
alef becomes the sounding madd-ʿiwaḍ carrier, so it is not flagged. The waqf
machinery (madd ʿiwaḍ, silah-goes-silent, qalqala kubra, final sukun) is fully
covered by rules or by the flat grouping. Findings 1–4 are therefore identical
in both contexts; the audit is **complete for continuous and stopping**.

## Implications for the Timestamps highlight feature

1. The flat `letter_phoneme_mappings()` is **already** a near-perfect basis:
   every entry has exactly one sounding grapheme except the 708 idgham_shafawi
   entries. Highlight = the sounding grapheme of each entry.
2. The mapping does **not currently expose** *which* grapheme is the sounding
   one (it returns only `chars` + `phonemes`). The natural next step is a small
   API that, per entry, returns the sounding grapheme index — `pronounced_in_flat`
   already encodes the rule. Open question for the user before building it.
3. Deciding silence from **tajweed rules** instead of the flat grouping requires
   Finding 1 (tanween alef) to be fixed first.
4. `idgham_shafawi` needs an explicit highlight convention (Finding 2).

## Validation on real reciter stop points

`dev/audit_silent_letters.py --mode detailed --detailed <reciter>/detailed.json`
runs the same checks over a reciter's **real** recitation: each `detailed.json`
segment's `matched_ref` span is one recited unit (its first word a real ibtidaa,
its last word a real waqf). Validated across 5 reciters (from the
`quranic-inspector-fixtures` dataset — the full bucket was out of the available
token's scope):

| reciter | segments | Check A | Check B | violations at actual stop words |
|---|---|---|---|---|
| Husary | 10,581 | 1,908 | 713 | **0** |
| Abdul Basit | 10,257 | 1,966 | 725 | **0** |
| Islam Sobhi | 9,661 | 1,555 | 609 | **0** |
| Bandar Baleela | 12,543 | 1,864 | 734 | **0** |
| Abdullah Ali Jabir | 8,800 | 2,003 | 711 | **0** |

Every reciter reproduces the synthetic audit exactly: Check A is **only** the
continuing tanween alef/maksura, Check B is **only** idgham_shafawi, and
**zero violations land on the words where the reciter actually paused**. The
silent-rule coverage is complete at real waqf points.

## Tokenization for the highlight

See [`tokenization-reconciliation.md`](tokenization-reconciliation.md): the
bucket TS-shard `letters[]` tokenization equals the **letter-phoneme atoms**
(proven char-for-char on a real shard), so the silent/sounding classification
here maps straight onto the shard's letters for the phantom-highlight feature.

