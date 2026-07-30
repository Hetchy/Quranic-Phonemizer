# 07 - The brief for the next adversarial review

You are reviewing a design that has already survived three review rounds and
one long owner session. Everything easy is gone. Your job is to find what is
still wrong before anyone writes code or generates the worked examples.

**Read:** `00-audit`, `01-design`, `02-equivalence-gate`, `03-review`,
`04-resolutions`, `05-vocabulary`, `06-examples`, plus
`../03-canonical-vocabulary.md` and `../../adr/013-public-projection-foundations.md`.

**Verify against:** the source at this branch head, and the pinned legacy
revision `b3bc53a`.

---

## 1. Rules of evidence

This is the part that matters. The last round's four blockers were all
documentation defects that three reviewers had missed **because nobody
re-counted anything**.

1. **No claim without a citation or a measurement.** `file.py:line` for
   behaviour; a number you produced for anything countable. "This seems
   inconsistent" is not a finding.
2. **Re-count every census you rely on, including the ones this document set
   already corrected.** Two counts in `00-audit §5` and `§4.1` were wrong and
   were repeated through three later documents before anyone ran
   `len(list(Rule))`. Assume the same is true of a number you have not
   personally re-derived.
3. **Run the corpus.** Most claims here are decidable in under a minute:
   build every verse, perform it, count. `tools/parity.py` is the pattern;
   `research/legacy-baselines/*.jsonl.gz` is the oracle; `tools/floor.py`
   shows the harness contract.
4. **A wrong finding costs more than a missed one.** State a confidence and
   say what would falsify you.

---

## 2. Defect classes already found here

These are patterns, not a checklist. Each one was found at least once. Assume
each has more instances.

**D1 - a census nobody re-counted.** `CLASSIFICATION_ONLY` documented as 18
members, actually 20. `Rule` documented as 40 members, actually 39. Both in
the same document, one section apart.

**D2 - a public name with zero producers.** `Inserted` is a live attribution
type with a docstring naming its case and **no code constructs it** - 0
occurrences corpus-wide against 46 sites that need one. The four-role
participant vocabulary had a `context` role and nothing in the corpus has a
third participant. `Ghunnah.emphatic` cannot be set by any rule and the
alphabet raises on it. **Ask of every enum member, every type, every field:
what produced this, and how many times?**

**D3 - a rule name with no producer for its commonest case.**
`Rule.MADD_TABII` is minted only by `PausalGlide`, so ordinary madd tabii -
41,543 legacy attributions, the most frequent tag in the corpus - has no rule
instance at all.

**D4 - a law that runs one direction.** Every law in `02-gate §4` starts from
what the producer emitted and checks it is well formed. None started from what
the *text* contains and checked the producer explained it. That is why D2 and
D3 survived. `04 §6.1` adds the converse; **check whether its eleven
predicates are correct, complete, and actually cheap to evaluate.**

**D5 - a law satisfied by emitting nothing.** "Every classification-only rule
*that names a sound* has a `Classifies` edge" is true of a build with zero
`Classifies` edges. Look for more conditionals that make a law vacuous.

**D6 - a law stated and never run.** `02-gate §4.2` requires every glyph to
participate in a spelling edge. 6,379 of 638,425 do not.

**D7 - a criterion naming an artifact that does not exist.** "A reviewed
corrections ledger" appeared three times and named nothing;
`tools/projection_parity.py` was "planned" with no CI job, no `HARNESS` entry
and no residue path.

**D8 - two ways to say one fact.** `Junction` plus `Word.starts` plus
`BoundaryPlan`, when only two booleans were ever read. `Rule.SILAH` beside a
`silah` nucleus kind. A `tokens()` method beside the `phonemes` projection.
**Every remaining redundancy is a place two answers can disagree.**

**D9 - a name that transmits the wrong intent.** `nunation` for tanween.
`nasal` on a noon, which reads as tautological when it means "held with
ghunnah". `Aspect` for "which half of a unit". `Evidences` against `Attests` -
two English near-synonyms carrying the sharpest distinction in the contract.

**D10 - a rule named for its cause.** `waqf_ending` carried six unrelated
outcomes because they shared "the reciter stopped". Check whether the
replacement did the same thing again under a new name.

**D11 - an error no existing gate can see.** The iwad's alif is attributed to
the noon that goes silent rather than the base that lengthens. Tokens are
identical, so phoneme parity is blind to it. **What else is only wrong in the
edges?**

**D12 - a hand-typed value in a document claiming generated examples.**
`06`'s first example contained `m̃m̃`; the alphabet does not double a nasal and
the real token is `m̃`. Re-derive every literal in `06`.

---

## 3. The hit list

Specific claims that are load-bearing and under-verified. Not exhaustive, and
finding something not on it is worth more than confirming something on it.

1. **The `cells` partition law may be unsatisfiable.** `05 §2.2` requires
   every grouping to partition the glyphs *and* cover every sound exactly
   once. Under `font` grouping, a cross-word merged sound is presented by
   glyphs in two cells in two different words. Which cell owns it? Either the
   law is wrong or the grouping is.
2. **Did `pausal_sukun` recreate `waqf_ending`?** It now covers a silenced
   short nucleus, a dropped dammatan or kasratan, an absent silah vowel, and a
   dropped pronoun yaa onset. If those are four things, D10 happened twice.
3. **Two participant roles may not be enough to fix what C1 was for.**
   `PausalGlide` passes `(before, at)` where everything else passes
   `(at, other)`. Labelling still needs a per-rule decision about which member
   is `source`. Was anything actually gained over the tuple?
4. **`is_stopped_on` for the last word of a request.** `BoundaryPlan` treats
   `EDGE` and `STOP` alike. Is the last word of a range that continues
   elsewhere genuinely stopped on, and does any rule behave differently if it
   is not?
5. **`notation` lives under `provenance` while `Sound.token` is top-level.** A
   consumer reading tokens must reach into provenance to know what they mean.
   Is that the right split, or did N8 push a load-bearing field out of sight?
6. **Capabilities 2 and 5 are gated on an unbuilt mechanism.** The recited
   writing serializer is 00-audit §4.4's unbuilt ADR-005 machinery, and `write`
   totality is unproven over its trigger set. How much of the design's claimed
   value depends on something nobody has built?
7. **Can C3 actually attribute all 6,379 orphan glyphs**, or are some
   genuinely unattributable - in which case the law needs an exception list
   and the ceiling never reaches zero?
8. **The QUA cell-shard gate was designed without reading the QUA repository.**
   Check `04 §6.2` against the actual shard schema and say what it gets wrong.
9. **B1's soundless exemption list is `{ISHMAM, SAKT}`.** Re-derive it after
   the vocabulary changes. Is it still exactly two?
10. **The read API was designed from an audit, not from a consumer.** Take one
    real screen of the timestamps viewer and try to build it from `m.rules`,
    `m.cells`, `m.silences`, `m.recited_text`. Name what is missing.
11. **The payload measurement used estimated row sizes**, not a real
    serializer. Re-derive it if the conclusion matters to you.
12. **`Supplies` / `Witnesses` is proposed for the public surface while the
    model keeps `Attests`.** Two names for one edge across a boundary is D8's
    shape. Is the rename worth that?

---

## 4. What is settled, and what challenging it costs

These were decided by the project owner with reasons recorded in `04` and
`05`. You may challenge any of them, but **only with evidence that was not
available when the decision was made** - a measurement, a consumer
requirement, a code path. Re-arguing them from taste wastes the round.

- One document, not several. Named profiles stay closed (`04 §5`).
- The host word owns a cross-word merged sound (`04 B3`).
- Domain names in one namespaced public module (`04 M11`).
- `Rule` plus `RuleFamily`, no third grouping axis (`05 §5`).
- `by` optional; no `plain` in the public vocabulary (`04 B4`).
- Two groupings, `faithful` and `font` (`05 §2.2`).
- `is_` on booleans; `variant`, not `khilaf`.

The owner's standing instruction across this whole design is **keep it
simple**. A finding that removes a concept is worth more than one that adds
one. If you propose an addition, say what it lets a named consumer do that
they cannot do today.

---

## 5. Output

Mirror `03-review`: a verdict, then **Blockers / Major / Minor**, then **Open
questions**, then **What holds**.

- A **blocker** stops implementation: the design cannot be built as written,
  or would ship a defect.
- Every finding names its evidence inline - `file.py:line`, a count, or a
  baseline row.
- Say plainly what you could not verify and why.
- End with **What holds**: the parts you tried to break and could not. That
  section is as useful as the findings, because it is what the next round does
  not have to re-examine.

Do not restate the documents back. Assume the reader wrote them.
