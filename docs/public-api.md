# Public API and projections

This document describes the current schema-v1 graph. The accepted replacement
architecture and phased implementation plan are in
[design/consumer-analysis-projection.md](design/consumer-analysis-projection.md).
Until that cutover lands, this document remains the contract for the released
shape. Its output is untrusted differential evidence for the redesign, not a
correctness oracle: native laws and audited fixtures decide the new semantics.

The package has one public operation:

```python
from quranic_phonemizer import Phonemizer

result = Phonemizer().phonemize("1:1")
```

`Phonemizer` selects a riwayah, script, variant choices, and optional phoneme
distinctions. Each call returns a fresh `PhonemizeResult`: one self-contained,
index-addressed document holding the written text, canonical units, performed
sounds, applied rules, and the relations between them.

The root `README.md` documents ordinary use. This document describes the
result graph and the projections derived from it.

For one unusually large, bounded request, `phonemize(..., suspend_gc=True)`
defers CPython cyclic collection until the call returns. It does not change
the result and restores the caller's prior collector state, including after
an error. Cyclic GC is process-global, so this advanced option also defers
collection of unrelated cycles created by other threads during the call. Use
it only when the process has enough memory for the complete returned document.

## Result identity

Every result identifies the request and the choices that produced it:

| Member | Meaning |
| --- | --- |
| `ref` | Resolved Quran reference |
| `riwayah` | Selected transmission |
| `script` | Selected written orthography |
| `variant` | Resolved riwayah-specific choices |
| `extra_phonemes` | Optional output distinctions in force |
| `schema_version` | Version of the public document shape |
| `canon_digest` | Digest of the canonical passage |

The canonical digest is independent of public array indices. It identifies
the canonical reading used to build the result, not a particular projection.

## Nodes

Six arrays hold the public nodes. An array position is that node's identity
inside the result.

| Array | Holds |
| --- | --- |
| `words` | Source locations, word text, and resolved start/stop state |
| `glyphs` | Characters of the source script in source order |
| `rendered` | Characters of the recited spelling |
| `units` | Canonical letter positions and their vowel state |
| `sounds` | Performed sound features and rendered phoneme tokens |
| `rules` | Applied tajweed rule instances |

`units` are the public projection of the script-free Score. They do not retain
internal `SlotId` values. `sounds` are the public projection of Performance;
their `token` is resolved through the selected output alphabet.

## Edges

Three arrays hold relations. Their fields are integer indices into the node
arrays, so copying a result member by member preserves the whole graph.

### Spellings

`spellings` relates source glyphs to canonical units:

- `Supplies` says that a glyph supplies a named fact of a unit.
- `Witnesses` says that a glyph witnesses a performed rule outcome.
- `Decorates` attaches a visible glyph that supplies no canonical fact.
- `Structural` identifies source material outside the word/unit graph.

These edges preserve the distinction between what the script writes and what
the recitation knows. A unit does not point back into a particular script.

### Attributions

`attributions` relates canonical unit parts to performed sounds:

- `Hosts` names the primary unit part responsible for a sound.
- `MergedInto` records a contributor whose sound merged into its host.
- `Silent` records a unit part that produced no sound and why.

Every sound has one primary host. A merger has both the host relation and the
contributor relation; silence is represented explicitly rather than inferred
from a missing token.

### Modifiers

`modifiers` records a rule changing or classifying a sound:

- `Recolours` changes a sound feature such as emphasis or nasal place.
- `SetsLength` changes vowel length.
- `Classifies` attaches a rule classification without claiming ownership of
  the sound.

Rules themselves live in `rules`; modifier edges connect a particular rule
instance to the affected sound.

## The two texts

The result keeps the source spelling and the recited spelling as separate
arrays because neither is an edit list over the other.

```python
result.text()             # source spelling
result.text("recited")   # spelling of this performed reading
```

`glyphs` preserves exactly what the selected script supplied. `rendered`
represents what is recited after start, stop, elision, insertion, expansion,
and substitution have been resolved. Rendered glyphs retain provenance where
they came from source glyphs and reach into the canonical units they present.

A transformation can be many-to-one, one-to-many, inserted, or silent. That
is why source and recited text each receive their own alignment.

## Projections

The convenience methods derive views from the arrays; they do not hold a
second copy of the reading.

### Phonemes

```python
result.phonemes()
result.phonemes("word")
```

The ungrouped form returns tokens in performed order. Word grouping assigns a
sound to the word of its primary host, including when another word contributed
to a cross-word merger.

### Alignment

```python
result.alignment(text="source", grouping="glyph")
result.alignment(text="recited", grouping="cell")
```

`text` selects the glyph array. `grouping="glyph"` produces one pairing per
character; `grouping="cell"` groups a letter with its associated marks.

Each pairing identifies its glyphs, sounds it owns, sounds it shares, applied
rules, and whether its glyphs are silent. A performed sound with no presenting
glyph becomes a gap pairing whose `after` field anchors it in reading order.

### Respelling

```python
result.respelling(grouping="cell")
```

Respelling joins the source and recited alignments into corresponding blocks.
Blocks may contain several pairings on either side, which preserves expansions,
contractions, mergers, insertions, and deletions without pretending that the
transformation is character-for-character.

## Rules and teaching labels

A `RuleInstance` identifies the rule, its source unit when it has one, the
second unit the rule names when there is one, and optional teaching labels.
That second unit is another unit the rule is about or one its own edges acted
on -- a merger's host, a letter it silenced, a vowel it lengthened -- never a
unit it only read to decide. The rule list is
exhaustive for the performed passage, while labels such as `madd_badal` and
`silah` are derived classifications for presentation.

`tajweed_rules(riwayah)` lists the public identifiers and their English and
Arabic names. Rule indices attached to pairings point into the same `rules`
array published on the result.

## Schema stability

The canonical JSON-shaped representation is defined in
`quranic_phonemizer/phonemize/schema.py`. Its tagged unions and indices are
validated by `schema_checks.py` and the tests under `tests/schema/`.

Adding a node or edge union member changes the public document shape and
requires a schema-version change. Reordering internal model identifiers does
not, because assembly translates them into result-local indices.

## Implementation map

| Concern | Owner |
| --- | --- |
| Result object and convenience methods | `phonemize/document.py` |
| Node records | `phonemize/nodes.py` |
| Edge records | `phonemize/edges.py` |
| Internal-to-public assembly | `phonemize/assemble.py` |
| Source/recited alignment | `phonemize/pairing.py` |
| Respelling blocks | `phonemize/respell.py` |
| Recited spelling | `phonemize/recited.py` |
| Canonical serialization and validation | `phonemize/schema.py`, `schema_checks.py` |

For the upstream pipeline that produces these arrays, read
[architecture.md](architecture.md).
