# ADR-013: Public projections preserve the domain edges

Status: superseded by [docs/design/projections/](../design/projections/)

The decisions below were taken before the contract was written against the
layered model. Where this record and that document set disagree, the document
set is authoritative.

## Context

ADR-005 deferred the public projection API. The projection audit established
that four of the five legacy APIs are four views of one graph, and that the
fifth rebuilt recited Arabic from rule names for want of the same graph. Two
proposed replacements then exposed a real design choice:

- a normalized graph preserves the model's typed relations, but needs an
  explicit request envelope and a serious migration gate;
- a convenient document supplies that envelope and gate, but flattening the
  relations into arrays on nodes loses distinctions the domain requires.

The loss is not theoretical. One grapheme may evidence different facts on
several slots, an `Attests` edge is not an `Evidences` edge, and a structural
grapheme belongs to no word. Likewise, a final consonant may realize its onset
while its nucleus is silent at pause. A `sound` list on a unit cannot express
that without recovering `Aspect` from the sound kind, which ADR-002 forbids.

## Decision

### 1. The public document is an identified snapshot

`Mappings` carries a schema version and the complete identity of the request:
reference, riwayah, script, notation, canonicalized variant selection, boundary
plan, and Score digest. Two documents are comparable only when those fields
match.

Array indices are request-local identifiers. The JSON contract does not call a
bare integer or bare slot label stable. A durable address, if an API later
needs one, must include the riwayah, canonicalized selection, Score digest, and
schema edition that give the label its meaning.

### 2. Nodes do not absorb relations

`Mappings` publishes ordered node arrays for words, glyphs, units, sounds, and
occurrences, plus four relation arrays:

- `spellings` is the exact `Evidences | Attests | Decorates | Structural`
  union from ADR-003;
- `attributions` is the exact
  `Hosts | Inserted | MergedInto | Silent` union from ADR-002, including
  `Aspect`, insertion side, sound, and occurrence;
- `modifiers` links an occurrence to each sound it recolours, relengthens, or
  classifies without owning;
- `contributions` links each non-structural glyph to the exact performance
  edge or occurrence it presents, or marks it as orthographic-only.

The contribution relation is necessary even though spelling and attribution
are already present. A haraka, a length carrier, and a dagger can reach the
same nucleus while presenting different performance outcomes. In particular,
a carrier under a dagger can be orthographic-only while the dagger presents
the long vowel. Unit audibility cannot decide glyph audibility.

The serialized graph stores one direction for every relationship. Reverse
indexes such as glyphs for a unit, sounds for a unit, rules for a sound, and
units for a word are named derived helpers. They are not duplicate facts in
the wire format.

No semantic `owner` is stored on a sound. Display ownership is a rendering
policy over attribution and contribution edges. This matters when the haraka
and its carrier both evidence the same unit: choosing a unit cannot choose the
glyph that should be painted.

### 3. Public values exclude invalid combinations

The public nucleus is a discriminated value:

`Silent | Short(quality) | Long(quality) | Silah(quality) |
PausalLong(quality)`.

It is not a nullable quality beside an independently set length. The `Onset`
enum stays intact because the completed census found no domain state it cannot
represent. Madd counts and durations are properties of the tariq a reciter
takes, not canonical facts, and are not added to `Unit`.

`RuleFamily` and execution phase are derived from `Rule` by total registries.
They are not repeated on each occurrence. An occurrence retains its ordered,
role-labelled participants; ownership, insertion, merger, silence, and
modification stay on the relation whose meaning they define.

### 4. Lexical identity is not a recitation process

The pending canonical-vocabulary change is amended:

- `DIVINE_NAME` becomes a word-level `LexemeClass`;
- `IMALA` and `ISHMAM` are rule occurrences and are not unit tags;
- `SlotOrigin` still decomposes into the independent `nunation` and `spelled`
  facts;
- `SILAH` and `PAUSAL_LONG` remain conditional nucleus kinds.

A one-member lexical enum is intentional. It gives lexical identity a stable
category without mixing it with processes merely because only one lexical
class is currently consumed.

### 5. Recited writing is a derived view

The core graph preserves source glyphs and domain relations. A recited-writing
serializer may derive render glyphs from `write`, contributions, attributions,
and insertion anchors. A slotless insertion is represented by its before/after
anchor and its rendered sound; it is not forced into a fake unit or an empty
source glyph.

### 6. The document is named `Mappings` and is emitted whole

`Reading` is unavailable: `orthography/adapter.py` already defines it for the
parsed script side and eight modules import it, so a public `Reading` would be
two types with one name in one package. The word is triple-booked besides,
since a reading is also what `Riwayah` names. `Mappings` carries the migration
lineage from the legacy `*_mappings` views instead.

There are no per-array flags selecting what to build or serialize. The flags
would not be independent -- referential integrity forces a dependency order,
and the closed subsets collapse to three profiles of which only one saves real
work, with no consumer for it. Conditional emission would also make every
completeness law in the gate conditional on what was requested. If a measured
payload or a named consumer later justifies selection, the answer is closed,
dependency-complete named profiles rather than free booleans.

## Consequences

The document is slightly more relational than a convenience DTO, but every
legacy view becomes a pure adapter over one lossless source. Consumers that
want convenience use derived indexes rather than receiving contradictory
forward and reverse arrays.

ADR-001 is amended only for the `SlotOrigin` decomposition and word-level
lexical identity. ADR-002 and ADR-003 are reaffirmed at the public boundary:
their typed edges are part of the contract, not internal detail.
