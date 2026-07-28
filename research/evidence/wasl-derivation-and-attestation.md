# Two follow-ups: the waṣl lexicon, and the attestation trigger

Both were left open by the amendment round. The first was ADR-008's open
question 2b — the sharpest thing in the set. The second was a 1,700-site
disagreement between two counts of the same rule.

## 1. The 575-skeleton lexicon was an artifact of asking the wrong script

Open question 2b: the waṣl lexicon was learned from Uthmani's own U+0671
positions, so reproducing the corpus proves nothing about it. If it is a
transcription of one script's glyph positions rather than Arabic morphology,
the derived architecture is undemonstrated.

It is not morphology, and it is also not needed. **IndoPak declares the fact
directly.** Measured over all 20,894 word-initial alef sites:

| Uthmani says | IndoPak alef is bare | count |
|---|---|---:|
| waṣl | bare | 13,274 |
| waṣl | carries a haraka | 186 |
| qaṭʿ | carries a haraka | 13,394 |
| qaṭʿ | bare | 16 — all muqaṭṭaʿāt, plus 3:158:5 |

A bare initial alef is a hamzat al-waṣl. The convention is total in the
direction that matters, and under L2 a declared script convention is a
legitimate `Supply` — the same standing `Nucleus.Silent` already has.

So the lexicon is only needed to resolve the **186 sites where IndoPak writes
the helping vowel**. Of those the article rule takes 121, leaving **64 sites
over 42 skeletons** — not 1,489 over 575.

### And the 64 are derivable too

Every one of the 42 is an imperative or a form VII–X verb — `انظر`, `اذهب`,
`ادخلوا`, `اهدنا`, `اتخذوا`, `اقرأ`, `انطلقوا`. That is a rule, not a list.
Written as one, with **no lexicon at all**:

1. **The article**, including before a geminated lām (`الَّذِينَ`, `الَّيْلِ`).
2. **Assimilated form VIII** — hamza + a geminate drawn from the set the
   infixed tāʾ assimilates into (`ت د ط ز ص ض ظ ث ذ`), and never fatha-vowelled.
3. **Otherwise**: hamza + a quiescent consonant, where the written vowel equals
   the classical helping-vowel derivation (damma iff the third letter carries
   damma, else kasra).

Rule 3 is what does the work, and it is self-checking: a hamzat qaṭʿ carries
its own morphological vowel, which the helping-vowel derivation does not
predict. `أُنزِلَ` writes damma where the derivation says kasra → qaṭʿ.
`اُنْظُرْ` writes damma and the derivation says damma → waṣl. Form IV always
writes fatha, and the helping vowel is fatha only for the article.

Measured as a total decision procedure over all 20,894 sites:

| | correct | missed | false + |
|---|---:|---:|---:|
| rules alone | 95.80% | 2 | 876 |
| rules + **3** particle entries (`إن`, `إذ`, `إذا`) | **98.19%** | **2** | 376 |

**The two misses are 46:4:18 `ٱئْتُونِى` and 49:11:30 `ٱلِٱسْمُ`** — both already
named Ledger sites in the set.

The 376 residual false positives are not a long tail; they are six named closed
classes of Arabic, none of them corpus-specific:

- proper nouns — `إبراهيم` 58, `إسرائيل` 41, `إبليس` 8, `إسحاق` 6;
- the `أولو` / `أوتوا` class, 45 — already a named class (the otiose wāw);
- form-IV verbal nouns — `إثم`, `إيمان`, `إحسان`, `إلقاء`, `ألف`, `أمانة`;
- `إذًا`, which is `إذا` under tanwīn and should fold into the particle entry;
- muqaṭṭaʿāt, already excluded elsewhere.

**Conclusion.** ADR-003 §6.1's "1,487 reduce to 526 distinct canonical
skeletons" reduces further, to **three morphological rules plus roughly 25–30
lexical entries a grammarian would name without seeing this corpus**. That is
the check open question 2b asked for, and the answer is favourable: the
derivation is morphology. ADR-008 §4.2's ~575-skeleton budget should be cut by
an order of magnitude, and ADR-003 §6's supplier row for `Onset.WASL` should
read *script convention, both total* — like `Nucleus.Silent` — with the rules
above as the cross-check L1 then actually tests.

Caveat, stated because it is the same trap: the *rules* were validated against
Uthmani's `ٱ` as ground truth. Unlike a lexicon, a rule can be checked against
a grammar independently, and these three are in every tajwīd primer. That is
the difference between this and what it replaces, and it is the whole argument.

## 2. The attestation trigger: the 1,700-site gap is a layer question

The amendment round left two counts of A2's canonical trigger unreconciled —
mine at 9,048 / 11,100 and the ADR's at ~10,772 / ~12,789. Measured, the gap is
neither arithmetic nor a scoping slip:

| trigger evaluated on | Uthmani | IndoPak |
|---|---:|---:|
| word-initial only (ADR-003 §4.1 as written) | 3,722 | 5,761 |
| the **Score** — predecessor slot's nucleus is `Silent` | 9,048 | 11,100 |
| the **waṣl performance** — the preceding *sound* is silent | 11,488 | 13,538 |

The 2,440-site difference is exactly **the article before a geminated lām**. In
the Score the waṣl slot carries the helping vowel — `Short(A)`, which ADR-003
§6.3 makes a stated obligation — so its successor's predecessor is *not*
`Silent`. In waṣl that vowel is elided, so it is.

Both figures are right about different things, and the ADR's sits between them,
so its four-class decomposition needs re-deriving whichever reading wins.

**The resolution is that neither of us stated it correctly.** My recommendation
was to restate the trigger "in Score terms". That is half right — the
*positional* formulation should go — but the replacement does not belong in the
Score. ADR-003 §4.1 property 2 already says attestation is evaluated in waṣl,
and invariant A1 already evaluates under the all-join plan. So:

> A shadda attests `ASSIMILATION` when, under the all-join boundary plan, the
> sound preceding it is silent.

That is a Performance-level predicate, consistent with the two things §4.1
already says, and it fixes the fixture at the **11,488 / 13,538** reading. It
also means A2 is not evidence that the Score needs a new field — which was the
risk in my original phrasing.
