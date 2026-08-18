# New riwayah

> **Status: tentative and indicative.** This repository has not implemented a
> second riwayah. The boundaries and checks below are a working hypothesis
> derived from the current Hafs implementation; they are not a final design or
> a compatibility promise.

The runtime is riwayah-agnostic, but this repository currently ships only
Hafs. The likely extension shape is a new package of corpus, script adapters,
canonical data, variants, and rules rather than conditional branches through
the Hafs implementation. Implementing another riwayah may expose assumptions
that require this shape to change.

The Warsh script evidence already collected for that work is kept separately
in [warsh/codepoint-audit.md](warsh/codepoint-audit.md).

## Indicative package boundary

`quranic_phonemizer/api.py` is the composition root. Its `PACKAGES` table maps
a `Riwayah` to a package exposing the same assembly surface as
`quranic_phonemizer/riwayat/hafs/`:

- identity and supported scripts;
- a packed corpus;
- one `ScriptAdapter` per supported script;
- a ledger, lexicon, khilaf catalogue, and ordered lexeme passes;
- a `RuleSet` assembled for that riwayah.

The resulting `Recitation` still follows the shared `read -> build -> perform`
pipeline described in [architecture.md](architecture.md). `Reading`, `Score`,
`Performance`, and the public result graph do not become riwayah-specific
types.

## Indicative data boundary

A new package owns its files under `quranic_phonemizer/data/riwayat/<name>/`.
The Hafs layout shows the current contract:

```text
corpus/
scripts/
khilaf.yaml
ledger.yaml
lexicon.yaml
rules.yaml       # only when shared rule tables need overrides
```

Shared Arabic facts remain under `data/shared/`. A fact belongs there only
when the reading does not change it. Riwayah-specific pronunciation or
orthographic interpretation belongs to the new package even when Hafs happens
to use the shared default today.

## Open script boundary

Each supported script supplies an `Inventory` and a `ScriptAdapter`. The
adapter must turn the corpus spelling into a `Reading`; downstream canonical
and tajweed code must not inspect raw script characters.

Warsh cannot be added by copying a Hafs inventory alone. Its audited marks
include facts expressed by scalar sequences and neighbouring marks. The
orthography layer therefore needs a reviewed representation for those
sequence-dependent facts before a Warsh adapter can be complete. That is the
open engineering decision recorded by the codepoint audit.

## Likely rules and variants boundary

`riwayat/<name>/rules.py` constructs the riwayah's `RuleSet` from typed rule
objects and its rule tables. Differences belong in selected classifiers or
data supplied to them, not in `if riwayah == ...` branches inside shared rules.

The riwayah's khilaf file defines its own selectable readings and defaults.
Those selections may affect canonical construction or performance, but the
public selection mechanism and result metadata remain shared.

## Candidate conformance checks

A second riwayah would need its own evidence rather than parity with Hafs.
Candidate checks are:

1. every corpus scalar is classified by its script inventory;
2. every grapheme is structural or participates in the inscription graph;
3. every canonical slot has written evidence or a cited ledger entry;
4. source marks attest derived rules rather than driving them;
5. every shipped rule is exercised by reviewed examples;
6. two scripts of the same riwayah agree where they encode the same reading.

Cross-riwayah equality is not a gate: a riwayah is allowed to change the
canonical reading and its performance.

## Questions still to verify

The following are research categories, not decided schema fields:

- which rule conditions, closed lists, and contextual locations differ;
- which phenomena require riwayah-specific algorithms, such as imala or
  taqlil, tashil or ibdal, and naql;
- how the source orthography, diacritic conventions, and word or verse
  segmentation differ;
- whether the output alphabet needs additional sound qualities;
- whether sequence-dependent script facts fit the current inventory and
  adapter boundary.

The first real implementation must answer these from an authenticated corpus,
reviewed recitation sources, and executable examples. Until then this document
is orientation, not specification.
