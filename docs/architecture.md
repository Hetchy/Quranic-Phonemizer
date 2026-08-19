# Architecture

This is the code-first entry point to the current package architecture. It
describes how a public request becomes canonical units, performed sounds, and
the index-addressed result document. It is intentionally not a tajweed
reference; the Hafs reading represented by the package is described separately
in [hafs/research/recitation-overview.md](hafs/research/recitation-overview.md).

## The shape of a request

The package has one public operation: `Phonemizer(...).phonemize(ref,
stop_signs=(), stop_refs=(), suspend_gc=False) -> PhonemizeResult`.

[`quranic_phonemizer/phonemize/__init__.py`](../quranic_phonemizer/phonemize/__init__.py)
implements that facade. Construction resolves and loads a riwayah, chooses a
script and variant selection, loads the output alphabet, and builds a script
writer. A call then follows one request path:

`ref -> locations and corpus words -> Reading -> Built(Score, Inscription) -> BoundaryPlan -> Performance -> Assembled public graph -> PhonemizeResult and its projections`

[`quranic_phonemizer/phonemize/session.py`](../quranic_phonemizer/phonemize/session.py)
owns the request-shaped part of this flow. It resolves the reference, builds
one score over the requested span, resolves stops, and performs the score.
[`quranic_phonemizer/phonemize/assemble.py`](../quranic_phonemizer/phonemize/assemble.py)
then translates model identifiers into the public result's array indices.

The composition root is [`quranic_phonemizer/api.py`](../quranic_phonemizer/api.py), not the facade. `recitation(riwayah)` assembles a `Recitation` containing the corpus, adapters, canonical data, variants, lexeme passes, and rules for one riwayah. It decides no linguistic fact; it wires owners together and offers `read`, `build`, and `perform`.

## Reading, Score, and Performance

The three principal representations deliberately answer different questions.

### Reading: what this script wrote

[`quranic_phonemizer/orthography/`](../quranic_phonemizer/orthography/)
is the script boundary. A script inventory classifies every scalar, and the
shared cluster reader turns corpus text into a `Reading`: grapheme clusters
and marks; literal evidence or named canonical derivations; attestations and
decorations; structural offsets; and per-word stop advice.

The adapter extracts evidence but does not decide the canonical reading. A
mark either carries a typed value or names a derivation that the canonical
layer will run. Both shipped scripts use the same clustering code; their YAML
inventories are the script-specific input.

### Score: the canonical reading

[`quranic_phonemizer/model/canon.py`](../quranic_phonemizer/model/canon.py)
defines the `Score`. It is a sequence of `ScoreWord`s containing `Slot`s. A
slot has a canonical letter, an onset, a joined/stopped nucleus, an origin,
and canonical annotations. The score also carries the riwayah, variant
selection, and a digest over all canonical word and slot fields.

The type has no script, grapheme, output token, or requested boundary plan.
Reading-inherent boundary alternatives live inside the nucleus, while the
caller's join/stop choices do not. `sakt_after` is a canonical word fact.

[`quranic_phonemizer/canon/build.py`](../quranic_phonemizer/canon/build.py)
is the sole owner of `Reading -> Score`. It drafts slots from evidence, runs
registered derivations, applies authored ledger supplies and verse-level
lexeme passes, performs required juncture repairs, and freezes the result.
[`quranic_phonemizer/canon/assemble.py`](../quranic_phonemizer/canon/assemble.py)
assigns verse-wide `SlotId` ordinals and computes the digest.

The builder is shared by the scripts. Script independence is structural - the score cannot name a script - and is measured by `l1`, which compares both builds field by field and ratchets its documented residue.

### Performance: what this traversal sounds

[`quranic_phonemizer/model/performance.py`](../quranic_phonemizer/model/performance.py)
defines the performed reading. A `Performance` contains typed sounds,
occurrences of named rules, attribution edges, modifier edges, the variant
selection, and the `BoundaryPlan` that produced it. It has no script or
grapheme field.

A `BoundaryPlan` has one junction after each word. The request resolver in
[`quranic_phonemizer/engine/boundary_plan.py`](../quranic_phonemizer/engine/boundary_plan.py)
combines explicit stop requests, script stop advice, score-level sakt, and the
end of the requested span. Rules see neighbouring slots through
[`quranic_phonemizer/engine/neighbourhood.py`](../quranic_phonemizer/engine/neighbourhood.py),
which blocks forward visibility at stops, sakt, request edges, and the special
end of a spelled-out opening.

## Inscription is a sideways relation

`Inscription` is not a fourth pipeline stage. `Reading` produces `Score` and
`Inscription` side by side; only the score continues to `Performance`.
Inscription records `grapheme -> slot` relations and is defined in
[`quranic_phonemizer/model/inscription.py`](../quranic_phonemizer/model/inscription.py).

The spelling union distinguishes:

- `Evidences`: a grapheme supplies a named canonical fact of a slot;
- `Attests`: a grapheme witnesses a performance outcome at an anchor slot;
- `Decorates`: a grapheme is attached to a slot but supplies no canonical fact;
- `Structural`: a grapheme belongs to no word or slot.

[`quranic_phonemizer/canon/scribe.py`](../quranic_phonemizer/canon/scribe.py)
records these edges while facts are being decided. This timing matters: after
drafts have moved, split, or disappeared, their original target cannot be
reconstructed reliably. References run upward from graphemes to slots; a
`Score` never points back to script evidence.

This separation lets both script alignments target the same canonical shape
without making spelling a property of a slot. It also keeps performance rules
from inspecting glyphs: written tajweed marks may attest an outcome, but the
rule engine classifies that outcome from canonical facts.

## Rule execution and ownership

Generic classifier implementations live in
[`quranic_phonemizer/rules/`](../quranic_phonemizer/rules/). The engine in
[`quranic_phonemizer/engine/`](../quranic_phonemizer/engine/) owns traversal,
effect recording, conflicts, and materialisation; it does not own a riwayah's
choice of classifiers.

`RuleSet` groups classifiers by phase for one riwayah. A pure
`Classifier.look(...)` query returns a `Verdict` - one named `Occurrence` plus
declarative effects - or nothing. `Plan` is the append-only journal with
same-phase conflict detection, and `Performance` is its materialised result.

Phases are ordered as boundary, merge, length, colour, and release. Rules
within one phase have no precedence. Two effects claiming the same target in
the same phase raise a conflict instead of using last-writer-wins behaviour.
Rules affect neighbours only by returning effects that name them.

Effects can realize, merge, silence, or insert a sound, or modify colour or
length. After rule effects are recorded,
[`quranic_phonemizer/engine/run.py`](../quranic_phonemizer/engine/run.py)
fills every unclaimed consonant or present vowel from the score, resolves
mergers, and retains modifier and classification edges. A merger is the pair
of a primary `Hosts` edge and a `MergedInto` edge sharing a sound and an
occurrence; deletion is an explicit `Silent` edge.

[`quranic_phonemizer/riwayat/hafs/rules.py`](../quranic_phonemizer/riwayat/hafs/rules.py)
binds the currently shipped classifiers and data tables into Hafs' `RuleSet`.
Riwayah differences belong at that binding point: the generic engine does not
branch on a riwayah name.

## The public result graph

`PhonemizeResult` is defined in
[`quranic_phonemizer/phonemize/document.py`](../quranic_phonemizer/phonemize/document.py).
Its durable content is six node arrays and three edge arrays. Every edge field
is an integer index into one of those arrays, never an internal `SlotId`,
`SoundId`, or `OccurrenceId`.

| Array | Meaning |
| --- | --- |
| `words` | locations, source word text, and resolved boundary facts |
| `glyphs` | source scalars in source order |
| `rendered` | recited-text scalars, including source provenance and unit reach |
| `units` | the public projection of canonical slots |
| `sounds` | performed sound features plus the alphabet token |
| `rules` | applied rule instances, with source and merger host units |
| `spellings` | source glyph-to-unit supplies, witnesses, decorations, or structure |
| `attributions` | hosted, merged, or silent unit parts |
| `modifiers` | recolour, length, and classification relations from rules to sounds |

The concrete node and edge records are in
[`quranic_phonemizer/phonemize/nodes.py`](../quranic_phonemizer/phonemize/nodes.py)
and [`quranic_phonemizer/phonemize/edges.py`](../quranic_phonemizer/phonemize/edges.py).
Assembly also derives the recited spelling from the performed sounds, retains
`from_glyphs` provenance for rendered glyphs, and represents orthographic
silence as rule instances needed by the public graph.

Only [`quranic_phonemizer/render/alphabet.py`](../quranic_phonemizer/render/alphabet.py)
turns a typed sound into a phoneme token. The decision layers carry sound
features, not output strings. Optional phoneme distinctions are also resolved
at this notation boundary.

The convenience methods are projections over the arrays. `phonemes()` reads
tokens in performed order; `text()` concatenates source or rendered glyphs;
`alignment()` pairs glyphs with owned/shared sounds, silence, and rules; and
`respelling()` closes source and recited alignments under provenance and sound
ownership.

Alignment is implemented by
[`quranic_phonemizer/phonemize/pairing.py`](../quranic_phonemizer/phonemize/pairing.py)
and supports glyph or cell grouping. A sound with no presenting glyph in the
selected text becomes a gap pairing with an `after` anchor. Respelling in
[`quranic_phonemizer/phonemize/respell.py`](../quranic_phonemizer/phonemize/respell.py)
uses union-find so many-to-one and one-to-many spelling changes remain one
block.

[`quranic_phonemizer/phonemize/legacy_views.py`](../quranic_phonemizer/phonemize/legacy_views.py)
contains pre-`Session` helpers for internal callers that directly hold a raw
`Score`, `Inscription`, and `Performance`. They are not a second public
assembly path and should not be used to define new output contracts.

## Data and extension seams

Runtime resources are package data under
[`quranic_phonemizer/data/`](../quranic_phonemizer/data/). Ownership follows
what the data varies with:

- `riwayat/hafs/corpus/` holds the packed source text and address metadata;
- `riwayat/hafs/scripts/` holds one total scalar inventory per shipped script;
- `riwayat/hafs/ledger.yaml` supplies authored canonical facts and script
  witnesses;
- `riwayat/hafs/lexicon.yaml` holds canonical-skeleton lexical classes;
- `riwayat/hafs/khilaf.yaml` defines the riwayah's selectable disagreements;
- `shared/` holds morphology, rule letter tables, and letter-name spellings;
- `render/ipa.yaml` holds the output alphabet shared across riwayat.

[`quranic_phonemizer/corpus.py`](../quranic_phonemizer/corpus.py) owns packed corpus addressing and decoding. [`quranic_phonemizer/dataio.py`](../quranic_phonemizer/dataio.py) provides the strict YAML loader: duplicate keys, missing required keys, and unknown keys are errors at the relevant resource loaders.

The current build packages Hafs with Uthmani and IndoPak scripts. The existing
riwayah seam is explicit: `Riwayah` and `api.PACKAGES` enumerate shipped
readings, while a package under `riwayat/` supplies resources, adapters,
lexeme passes, and a bound `RuleSet`. The script seam is likewise explicit:
`Script`, the riwayah's `SCRIPTS`, and a script inventory are closed lists;
the shared adapter and builder consume their typed output. These are extension
points in the current code, not evidence that another riwayah or script is
already implemented.

## Enforced dependency direction

[`tools/structure_lint.py`](../tools/structure_lint.py) treats the import graph
as an allow-list. It rejects undeclared package edges, unused permissions, and
module cycles. `dataio` and `model` are leaves. `corpus` depends only on
`model`; `orthography` on `dataio` and `model`; `canon` on those three;
`engine` on `model`; `rules` on `engine` and `model`; and `render` on `dataio`
and `model`. `riwayat` binds those lower layers, `api` composes them, and
`phonemize` sits above `api` to publish the request-shaped result.

Two restrictions are especially load-bearing: `canon` may reach
`orthography` only through its adapter protocol, and neither `orthography` nor
`render` can import the engine or rules. The lint also keeps phoneme strings
inside `render/`, checks public/dead exports, and enforces size limits.

## Core invariants and their checks

The architecture relies on executable laws rather than comments alone:

- a score contains canonical facts, not script or boundary-plan state;
- every score slot is reached by at least one inscription spelling edge;
- every performed sound has exactly one primary origin;
- every canonical consonant and present vowel is hosted, merged, or explicitly
  silenced;
- every merger has both its host and contributor relation;
- every rule occurrence produces an attribution or modifier, or belongs to
  the declared classification-only set;
- modifier references resolve and conflicting effects fail loudly;
- inventories and the render alphabet are total over their closed vocabularies;
- spelling a score and rebuilding it closes on the same score, even when the
  emitted text is not byte-identical to the source;
- public indices, tagged unions, rendered glyphs, mergers, and relations pass
  schema checks.

Model-level performance and inscription laws live in
[`quranic_phonemizer/engine/laws.py`](../quranic_phonemizer/engine/laws.py).
Public document validation lives in
[`quranic_phonemizer/phonemize/schema_checks.py`](../quranic_phonemizer/phonemize/schema_checks.py).
Corpus-wide laws and loader rejection tests live in
[`tests/laws/`](../tests/laws/) and [`tests/schema/`](../tests/schema/).

CI runs the gates registered in [`tools/gates.py`](../tools/gates.py):

| Gate | Architectural question |
| --- | --- |
| `suite` | Do rule fixtures, laws, and schema tests pass? |
| `comments` | Do comments and docstrings obey the source policy? |
| `structure` | Does the import, size, export, role, and token boundary hold? |
| `cross-script` | Do Uthmani and IndoPak produce the same performed tokens in the compared modes? |
| `regression` | Did output move against the frozen legacy change detector? |
| `roundtrip` | Does score writing and rebuilding close? |
| `attestation` | Does every written shadda attestation resolve to a merger occurrence? |
| `l1` | Where do the scripts' canonical score fields still disagree? |

The corpus gates are ratchets, not blanket claims of perfection. Their current
known residue and rationale are maintained in
[conformance.md](conformance.md). The
regression snapshots preserve prior output and are a change detector, not an
independent correctness oracle. Test case conventions and the rule-oriented
suite layout are documented in [`tests/README.md`](../tests/README.md).

## Where to start reading

For a new contributor, this order minimizes backtracking:

1. [`model/canon.py`](../quranic_phonemizer/model/canon.py), then
   `model/inscription.py` and `model/performance.py` for the three graphs.
2. [`api.py`](../quranic_phonemizer/api.py) and
   [`phonemize/session.py`](../quranic_phonemizer/phonemize/session.py) for composition and call flow.
3. [`orthography/cluster.py`](../quranic_phonemizer/orthography/cluster.py) and
   [`canon/build.py`](../quranic_phonemizer/canon/build.py) for evidence becoming slots.
4. [`engine/run.py`](../quranic_phonemizer/engine/run.py), `engine/plan.py`, and
   one classifier family under `rules/` for execution.
5. [`phonemize/assemble.py`](../quranic_phonemizer/phonemize/assemble.py) and
   `phonemize/document.py` for the public graph and projections.
6. [`tests/README.md`](../tests/README.md), then the nearest rule and law tests.

Use
[hafs/research/recitation-overview.md](hafs/research/recitation-overview.md)
when the question is what Hafs reading fact the package represents,
[public-api.md](public-api.md) for the published result graph, and
[new-riwayah.md](new-riwayah.md) for tentative work toward another riwayah.
Source code and executable gates remain authoritative for what exists now.
