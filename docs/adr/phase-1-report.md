# Phase 1 report — the script boundary, measured

ADR-008 §5 requires phase 1 to measure four things and record them here rather
than assert them. This is that record. It also states, honestly, what the gate
has *not* reached.

## 1. L1 residue

| | |
|---|---|
| verses | 6,236 × 2 scripts |
| words | 77,433 |
| slots | 286,968 |
| **residue** | **108 rows** — 40 `onset`, 49 `nucleus`, 19 `count` |

**99.96% slot agreement.** The gate demands zero, so phase 1 is **not green**.
What it has established is that the residue is bounded, enumerable and named:
§4 lists every remaining class and where it closes.

The trajectory is the useful part. The first run of the real pipeline produced
3,602 residue rows over 300 verses. Five of the reductions came from the design
catching a distinction rather than a typo, and those are recorded in §5 because
they are the argument for the architecture, not incidental debugging.

## 2. How thin the adapters actually are

ADR-001 §2 asserted the adapters would stay thin, then **withdrew the claim as
a premise** and made it a phase-1 measurement. Measured:

| | lines |
|---|---:|
| `riwayat/hafs/scripts/uthmani.py` | 11 |
| `riwayat/hafs/scripts/indopak.py` | 11 |
| `riwayat/hafs/resources.py` (shared assembly) | 52 |
| `data/riwayat/hafs/scripts/uthmani.yaml` | 94 |
| `data/riwayat/hafs/scripts/indopak.yaml` | 95 |

**22 lines of Python against 189 declarative lines.** Both adapter modules are
identical but for the `Script` member they name; every scalar of both writing
systems is data. IndoPak's 85 distinct scalars and five polysemous marks landed
in YAML, which is where ADR-001 §2 predicted most of the weight would go.

The claim is therefore upheld — with one correction to how it was framed. The
adapters are thin because the *derivations* absorbed the work, not because the
work vanished: `canon/derive/` is 7 modules and ~600 lines, and it is shared
across both scripts and every future one. That is the trade the design makes,
and it is the right one, but "thin adapters" alone would misdescribe it.

## 3. Cost

| | |
|---|---|
| build | ~7.7s for 1,000 verses × 2 scripts, single-threaded |
| full corpus | ~50s for both scripts |
| peak graph | one verse at a time; nothing accumulates across verses |

Occurrence volume is not measurable yet — no rule has run. That measurement
belongs to phase 3.

## 4. The residue, by class, with its closure

| n | class | closes in |
|---:|---|---|
| ~22 | muqaṭṭaʿāt — `الٓمٓ`, `الٓر`, `حمٓ`, `طسٓمٓ` | phase 4, `canon/spell.py` |
| ~20 | hamza + lām lexemes — `ألف`, `ألقى`, `ألزم`, `ألهم`, `ألسنة`, `ألوان` | lexicon, §6 |
| ~14 | per-site: `رَءَا` ×5, `تَرَٰٓءَا`, `ضُؔعْفٍ` ×3, `تَأْمَ۫نَّا`, 41:44, 11:41 | Ledger |
| 7 | ṣilah scope — `بِهِ`, `يُحْـِۧىَ`, `وَلِـِّۧىَ` | `silah_exempt`, unauthored |
| 6 | final-mīm helper vowel — `أَنفُسَكُمُ ۖ`, `بَيْنَكُمُ ۖ` | `Attests(INSERTION)`, ADR-003 §6 row missing |
| 5 | istifhām + article — `ءَآللَّهُ`, `ءَآلْـَٔـٰنَ` | Ledger |
| 2 | `ٱئْتُونِى` 46:4:18, `ٱلِٱسْمُ` 49:11:30 | already named Ledger sites |

None of these needed a vocabulary member the ADR set lacks. That is the result
worth stating: **the canonical model survived contact with a second orthography
without growing a field.**

## 5. What the residue taught, that the design should keep

Five reductions were the design catching a real distinction. Each is recorded
where the next reader will meet it, not only here.

1. **Rasm-hood cannot be decided before the cluster's own nucleus is resolved.**
   A dagger on IndoPak's ālif is madd badal and the cluster is a slot; the same
   mark on Uthmani's wāw in `ٱلصَّلَوٰةَ` lengthens the slot before it and the
   cluster is rasm. Nothing about the glyph says which — only where its nucleus
   lands does.
2. **One inventory key was doing two jobs.** `slot: host` meant both "this
   letter is rasm" and "this annotates the letter", so IndoPak's combining
   grapheme joiner was silencing live carriers. An entry now says `silences`
   when it means it, and the joiner is declared `structural`, which is what it
   is.
3. **A sukūn cannot disqualify a length carrier.** IndoPak writes one *on* its
   carriers — `يْ` for a long ī — and the absence of a vowel is not evidence of
   having one.
4. **The order of the checks in `is_wasl` is load-bearing.** The article puts a
   lām at the second position of every word it prefixes, and several lexeme
   entries begin hamza + lām, so consulting the lexeme list first makes `ءلق`
   swallow `القرآن`: residue 108 → 671. Measured twice, and now stated in both
   modules.
5. **Verse scope was necessary and not sufficient.** 20 of IndoPak's 54
   cross-word tanwīn sites put the nūn in the *following verse*, so
   `canon.build` takes one word of right context. This is the correction
   ADR-001 §5 already owed.

## 6. Budgets — and one that was set too low

ADR-008 §4.2's budgets are gates, and one of them fired during implementation.
That is the guard working, so the number is corrected here with its reason.

| section | budget | actual |
|---|---:|---:|
| `wasl_particles` | 10 | 3 |
| `wasl_exempt` | 30 | 24 |
| `pausal_lexemes` | 10 | 7 |
| `silah_exempt` | 200 | 0, unauthored |

`wasl_exempt` is **inside** its budget at 24 and will not stay there. The
budget was set from the waṣl analysis's 64-site / 42-skeleton residue, which
counted only the sites where IndoPak writes the helping vowel. Closing the ~20
hamza + lām words in §4 takes it to ~44, and the honest ceiling is **60**.

The reason is not corpus irregularity, and the budget rule is right to demand
one: `ال` is genuinely ambiguous between the article and a root lām, and no
orthographic test separates them. `ألف` and `الفجر` begin identically. That is
a lexical fact about Arabic, and a lexical fact is what the list is for — the
distinction the design cares about is that a *rule* can be checked against a
grammar by someone who has never seen this corpus, and these entries can be
checked against a dictionary the same way. Neither can be confirmed only by the
corpus that produced it, which is what the 575-skeleton table could not say.

Recommendation for ADR-008 §4.2: raise `wasl_exempt` to 60 and record that the
figure now covers a class the original analysis did not reach.

## 7. Provenance and the `Decorates` count (ADR-008 §3.1)

Reported per run, because a residue driven to zero by a rising `Decorates`
count is not a proof of script-independence.

| | Uthmani | IndoPak |
|---|---:|---:|
| facts from adapter evidence | 270,338 | 235,749 |
| facts from a derivation | 95,534 | 100,297 |
| facts from the Ledger | 0 | 0 |
| `Decorates` | 50,981 | 44,906 |
| attestations | 9,048 | 11,100 |

Two things to note. The Ledger is still **empty** — every fact so far comes
from evidence or a rule, which is the stronger position and is why §4's
per-site classes are still open. And the attestation counts land at exactly the
Score-level reading of the canonical trigger measured during the design round
(9,048 / 11,100), which is an independent cross-check that the implementation
and the analysis are describing the same thing.
