# Phases 3, 5 and 6 — the engine, the rules, and phoneme parity

Phase 2 (`write` and the round-trip) is deferred behind these, deliberately.
Parity is the deliverable the whole rebuild is measured against, and `write` is
a projection whose foundations phase 6 supplies; doing it first would have
delayed the only number that says whether the rebuild works.

## 1. Where it stands

| | |
|---|---|
| word-mode parity | **77,197 / 77,433 — 99.695%** |
| L1 residue | 120 rows over 286,968 slots |
| laws | pass on every verse of the corpus |
| tests | 88 passing |
| cost | ~22s for the corpus, single-threaded |

Neither gate is green. Both residues are bounded, named, and listed in §4.

## 2. What the phases proved

**Phase 3 — the effect model, E1, and A1's ruling.** The nūn family is one
classifier on one trigger: a `NOON` slot with a `Silent` nucleus, merging its
`ONSET`. Nūn sākinah and tanwīn are literally the same rule, which is what
ADR-004 §8 ruled and what domain-facts §5.1 says they are. The five outcomes
partition the alphabet — asserted in a test — so E1 cannot fire inside the
family and a sixth branch would be a partition error rather than a precedence
question.

**Phase 5 — the un-collapsing.** `rules/idgham.py` replaces the condition the
old implementation used (a bare consonant followed by a silent one), which
stood in for at least four named rules and lost every name. One classifier,
three tables: which table a pair falls in is data, and giving each family its
own `look` would reintroduce the per-letter dispatch ADR-004 §1 removes.

**Phase 6 — the projection.** `render/` imports `model` only, so a projection
cannot re-detect a rule even if it wanted to. The phoneme sequence is a *view*
of the attribution edges — ordered by `(ordinal, aspect)` — never a second
computation, which is the packaging half of ADR-002 §5's guarantee.

## 3. What the laws caught

Every item below was found by an assertion firing, not by reading code. This
is the return on writing them.

| law | what it caught |
|---|---|
| **P3** | a materialisation order bug — merge targets are usually realized by the plain default, so resolving merges first left half a merger behind |
| **P4** | the merging rule must **own** the merged sound. Caught twice, on idghām and again on the pausal glide: `Relength` leaves the long vowel owned by plain realization, and then the two halves do not share an occurrence |
| **E1** | three real overlaps — `WaqfEnding` against `TaaMarbutaAtWaqf`, and the article lām against like-into-like idghām. Each time the fix was to make the conditions mutually exclusive, never to rank them |
| **E4** | two rules that fired and left no edge, which turned out to be genuine classification-only members the vocabulary had not declared |
| import guard | output notation leaking into `canon/` twice, once in prose |
| lexicon budget | `wasl_exempt` set below the class it had to hold |

## 4. Residue, by class

**Parity (236 words).** `r`/`rˤ` at 26 sites where the rāʾ rules are still
partial; `u`/`u:` at 28; the muqaṭṭaʿāt, which are phase 4; `ٱلْتَقَتَا`, where
`is_article_lam` cannot see that a form-VIII verb is not the article; and a
long tail of ones and twos.

**L1 (120 rows).** Unchanged in shape from the phase-1 report: muqaṭṭaʿāt,
per-site Ledger material, ṣilah scope, and the final-mīm helper vowel.

One measured trade to record: resolving the geminate yāʾ for parity moved L1
from 96 to 120. The two gates are not independent, and a change made for one
must be re-measured against the other. That is a property of the design being
one pipeline rather than two, and it is the right property — but it means
neither number can be quoted alone.

## 5. Findings the ADRs should absorb

**5.1 `PLAIN` cannot be a classifier.** It would collide with every merging
family on the same conflict key, and resolving that needs an ordering *within*
a phase, which ADR-004 §3 rules out. It is a materialisation default: the
engine fills whatever no verdict claimed and tags it `Rule.PLAIN`. The
invariant survives — no sound exists except as the output of a named
occurrence — and E1 stays a genuine error. ADR-004 should say so, because the
alternative reading of §3 makes the phase list unimplementable.

**5.2 A1 lost a distinction waqf needs.** Collapsing the tanwīn nūn and a root
nūn into one shape is the ruling's whole point, but at a stop they differ:
`هُدًى` drops its nūn and leaves the ʿiwaḍ, `مِن` keeps its own. Nothing else in
the Score separates them, and asking the orthography would put a glyph back
inside a rule. `SlotOrigin` returns with exactly the two conditions ADR-001
§3.2 set for reinstating it — a script-independent definition (it names the
producing module, which is shared code) and a real consumer (two).

**5.3 `TAFKHEEM` is classification-only and ADR-002 §5.1 does not say so.** It
lists `TARQEEQ` and not its twin. Both emit `Recolour`, which modifies a sound
rather than producing one, so neither owns an attribution and a projection
finds them through `Occurrence.parts`. Listing one and not the other is the
asymmetry the set removes everywhere else.

**5.4 `Recolour` and `Relength` do not claim a slot.** They modify a sound;
counting them as claims leaves the sound unrealized. Worth stating in ADR-004
§2 next to the effect table, because the distinction is invisible from the
type.

**5.5 A lexeme whose key cannot separate it is a Ledger entry.** `لَٰكِنَّ` and
`لَّـٰكِنَّا۠` share a vocalised skeleton even with vowels and gemination spelled;
so do `ٱلرَّسُولَ` and `ٱلرَّسُولَا۠`. A lexeme entry there breaks 27 words to fix
one. The rule the design already states — *a location table growing toward
10⁴ means a rule is missing* — needs its converse said too: **a rule that
cannot key on anything the Score holds is a Ledger entry, and four of them are
not a failure.**

**5.6 One guard was written and reverted, which is worth recording.** "Only a
canonically silent glide is a madd carrier" is false: `هُوَ` and `يَعْفُوَا۟` have
the same shape and different endings, and the guard cost 900 words to fix one.
The one stays in the residue.
