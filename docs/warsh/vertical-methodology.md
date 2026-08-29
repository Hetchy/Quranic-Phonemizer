# Warsh vertical methodology

This document defines the required workflow for every Warsh runtime vertical.
It applies to fixed behavior first and to selectable behavior when the variants
workstream begins. The owning v2 research file remains the domain authority;
[`research/v2/script-projection.md`](research/v2/script-projection.md) remains
the source-to-canonical contract, and [`../../tests/README.md`](../../tests/README.md)
remains the semantic-test format contract.

## 1. Establish the domain contract

Before changing tests or runtime code, read the owning v2 research document
and its cited sources. Write down the vertical's complete decision surface:

- the fixed rule and every accepted face;
- wasl, waqf, ibtidaa, and internal-boundary behavior;
- regular predicates, lexical families, closed exceptions, and exact scopes;
- sound, rule, source, and host ownership;
- interactions with earlier and later verticals;
- behavior implemented now, accepted variants deferred to the variants
  workstream, and behavior owned by a later vertical.

Do not derive an expected pronunciation from current phonemizer output. The
runtime is evidence about the present implementation, not a domain source.

## 2. Inspect the selected script

Inspect the exact King Fahd Warsh text and Unicode code points for every
representative sequence before authoring its expectation. The inspection must
cover the whole grapheme sequence, not an isolated scalar, and must determine
whether each source element:

- supplies a canonical letter, onset, nucleus, nunation, annotation, or
  boundary shape;
- attests an independently derived reading;
- decorates an owned unit; or
- is structural and carries no lexical unit.

Corpus searches must identify lookalike sequences, prefixes, suffixes, and
exceptional contexts. A scalar or visual mark does not receive one global
meaning merely because it is frequent.

Warsh is intentionally supported in one selected script. A reviewed source
sequence may therefore supply a canonical fact directly when the script writes
that fact or a stable reading-specific convention. This is not the Hafs
two-script agreement problem: Warsh does not need a script-independent
derivation merely to simulate a second script that is not supported.

The permission is bounded. Script evidence does not by itself decide a public
variant, a boundary-dependent performance, a madd classification, or another
rule outside projection. Unreviewed sequences fail projection rather than
receiving a best-effort interpretation. Research predicates and independently
generated counts remain conformance checks on any script-supplied register.

## 3. Use comparisons as diagnostics

When a form is ambiguous, compare whichever independent evidence is useful for
that case:

- the equivalent Hafs source spelling and its code points;
- the Hafs canonical score or performed phoneme output;
- another published mushaf or trustworthy cross-reading presentation; and
- related inflections and spellings elsewhere in the Warsh corpus.

These comparisons can reveal a selected-script convention, missing written
detail, a genuine riwayah difference, or a current adapter defect. They are
diagnostic rather than automatically authoritative: the Warsh research and
selected Warsh script still decide the Warsh expectation.

## 4. Write the complete tests first

All tests for the vertical must be authored before production implementation
begins. The pre-implementation test set includes:

1. semantic cases for every distinct rule, morphology, and boundary state;
2. adapter fixtures for every selected-script sequence family and dangerous
   lookalike;
3. negative cases proving that nearby forms are not claimed;
4. independently derived conformance registers and family subtotals; and
5. interaction cases whose dependency belongs to another vertical.

Semantic cases use exact corpus text and domain-derived phonemes. Prefer one
isolated word when the rule is word-internal. Include multiple words only when
the boundary is part of the behavior, and make the complete boundary plan and
both words visible.

Use representative semantic cases for distinct meanings and morphological
forms. Exhaustive locations belong in conformance tests instead of repeated
semantic rows. Fixed behavior must not absorb an accepted variant, and a
variant-bearing form must not receive a convenient fixed expectation.

Run the focused tests before implementation and record the failure partition.
A correct expectation may fail because this vertical is absent or because a
scheduled later vertical owns part of the result. Keep the correct expectation
and state that dependency explicitly; do not rewrite it to match incomplete
runtime output or hide a broad family behind permanent xfails.

No classifier, source register, canonical pass, or rule binding is added until
this test set has been reviewed against the research and selected script.

## 5. Implement from projection upward

Implement only the behavior established by the tests, in this order:

1. recognize and validate reviewed selected-script sequences;
2. project their canonical facts and exact source evidence;
3. add any required typed canonical or performance vocabulary;
4. implement the smallest generic classifier that expresses the domain rule;
5. bind it through the Warsh package with authored predicates or exceptions;
6. project rule reach to the responsible source, host, and performed sound; and
7. add public selection only in the variants workstream.

Do not create a classifier name that combines independent rules. Ibdal, madd,
inclination, coloring, assimilation, and boundary changes retain separate
owners even when they reach the same sound. Do not add implementation-authored
locations merely to make a corpus total or current output pass.

## 6. Reconcile and validate

After implementation:

- run the semantic and adapter tests first;
- inspect every changed failure as a domain or projection question before
  changing an expectation; record every iteration and whether the test or
  implementation resolved it;
- reconcile implementation registers against the independent conformance
  derivation and its family subtotals;
- run `python tools/quick.py <targeted tests...>` while iterating; and
- rely on the pull-request checks for the full ordinary suite and required
  structural and source-context validation.

A vertical is complete only when its research contract, selected-script
projection, semantic cases, negative cases, registers, runtime behavior, rule
reach, and applicable gates agree. Green tests produced by copying current
output are not completion evidence.

## 7. Handoff

The pull request states what is implemented, what is deferred, and the exact
validation state. Update [`status.md`](status.md) only when the workstream state
changes. Variants remain deferred until the variants workstream unless the
delivery map explicitly changes their order.
