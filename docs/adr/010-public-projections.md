# ADR-010: One relational trace beside the phoneme stream

Status: **proposed**. Uthmani/Hafs is the first contract; IndoPak is explicitly
deferred.

## Context

The legacy API exposed five answers to one question: phonemes, flat
letter/phoneme groups, character cells, Tajweed mappings, and silent flags.
Each non-phoneme view walked the mutable mapping again. That produced useful
application behaviour, but also several places to redistribute waqf vowels,
shortened carriers, assimilated letters, the Allah dagger alif, and expanded
muqattaat.

The replacement model already contains the facts those views inferred:
`Inscription` records source graphemes and canonical relationships;
`Performance` records sounds, silence, insertion, mergers and their causes;
and `Score` is their stable join. Publishing those internal objects is not a
public API, but publishing another cell DTO for each use case would recreate
the legacy disagreement.

## Decision

There are **two public projections**:

1. **`phonemes`** — the ordered token stream, optionally partitioned by word.
2. **`trace`** — one normalized relational description of source writing,
   canonical anchors, performed sounds, transformations and Tajweed
   occurrences.

Silent flags, letter animation groups, character cells, Tajweed-coloured
script, recited Arabic, MFA timing attachment and Inspector rows are **queries
or serializers over `trace`**, not additional semantic projections.

This is not one giant nested cell tree. `trace` is a small set of tables joined
by opaque IDs. A grapheme, realization, sound and occurrence is stored once
even when applications join them differently.

## Normative shape

Names remain provisional until the schema spike, but these cardinalities and
ownership rules are the decision.

```python
Trace(
    ref, script,
    boundaries: tuple[WordBoundary, ...],
    graphemes: tuple[ProjectedGrapheme, ...],
    anchors: tuple[Anchor, ...],
    realizations: tuple[Realization, ...],
    sounds: tuple[ProjectedSound, ...],
    occurrences: tuple[ProjectedOccurrence, ...],
)
```

### Graphemes

Every Unicode scalar in the selected Uthmani source appears exactly once,
including spaces, stop signs, verse marks, madd signs and silence signs.

```python
ProjectedGrapheme(
    id, char, source_index, word,
    kind,                         # base/haraka/tanween/shadda/carrier/mark/structural
    anchors: tuple[AnchorId, ...],
)
```

`kind` is coarse orthographic identity, not a claim about audibility. A carrier
is not necessarily long or sounding. `source_index` is for source slicing;
transformed output never uses it as its join key.

### Anchors

An anchor is the public, script-neutral address of one aspect of one canonical
slot:

```python
Anchor(id, word, ordinal, aspect)       # aspect = onset | nucleus
```

It keeps final-vowel deletion distinct from an onset while hiding the internal
`Slot` vocabulary. One grapheme may show several anchors (tanween), several
graphemes may show one anchor (haraka plus carrier), and an inserted
realization may have an anchor without a grapheme.

### Realizations

`Realization` is the only public cross-layer edge:

```python
Realization(
    id,
    anchors: tuple[AnchorId, ...],
    graphemes: tuple[GraphemeId, ...],
    sounds: tuple[SoundId, ...],
    produced_by: OccurrenceId,
    effect,       # realize | merge | delete | insert | replace | shorten
    role,         # host | contributor
)
```

Lists may be empty only where the domain requires it: unwritten material has
no grapheme; silence has no sound; and only the already-admitted slot-less
insertion has no anchor. `effect` is a closed presentation vocabulary derived
mechanically from attribution and canonical/performed state. It does not name
a rule. `produced_by` supplies the exact reason, so there is no parallel
`SilenceReason` enum.

`role` retains both sides of idgham and other shared sounds without choosing a
UI policy. An animator may light the host only or every contributor.

### Sounds

```python
ProjectedSound(id, index, word, token, features)
```

`index` is utterance-global and total. `word` is performance ownership, so a
cross-word merger belongs to its host word. MFA timestamps attach to
`SoundId`/`index`, never to a letter entry. Word-local indices are a convenience
serializer, not authoritative identity.

### Occurrences

```python
ProjectedOccurrence(
    id, rule, family,
    participants: tuple[Participant, ...],
    realizes: tuple[RealizationId, ...],
)
Participant(anchor, role)              # trigger/source/target/carrier/host
```

Occurrences are exhaustive, including plain and classification-only rules.
Participant roles are closed and family-checked. This is the information
needed by error correction and granular Tajweed colouring: which canonical
positions participated, what each did, and which graphemes and sounds they
reach.

A production edge has one cause, while madd, tafkheem and other classifiers
may overlap it. Those classifiers use the occurrence-to-realization join; they
are not squeezed into `Realization.produced_by` or a one-tag cell.

## Query recipes, not new contracts

| Application answer | Query over `trace` |
|---|---|
| silent flag | grapheme has no sounded realization; also return deleting occurrence |
| phoneme/letter co-highlight | sound → realizations → host and contributor graphemes |
| one preferred animated letter | choose host graphemes as an explicit UI policy |
| letter timing | union timestamp intervals for its sounded realizations |
| silent-letter timing | use a merger host; otherwise adjacency is an explicit client policy |
| Tajweed on letters | occurrence → participants/realizations → anchors → graphemes |
| Tajweed on phonemes | occurrence → realizations → sounds |
| coloured Quran text | assign all overlapping occurrences to source-ordered graphemes |
| Inspector cells | group graphemes/virtual insertions by word, anchor and kind |
| recited Arabic | serialize realizations under a named writing preset |
| letter-level MFA labels | group contiguous sounds by a declared anchor policy |

Helpers for these recipes may ship, but contain no detector or second semantic
snapshot.

## Rejected alternatives

* **Four atomic mapping projections:** silence, Tajweed, ownership and writing
  are slices of one many-to-many relation; separate DTOs duplicate IDs and
  disagree on boundary transformations.
* **Character cells as the sole projection:** cells are a useful presentation
  model, but one tag loses overlaps, source and virtual characters mix, and
  `share_group` hides a many-to-many edge.
* **Publish `Score`, `Inscription`, `Performance`:** this couples consumers to
  engine vocabulary and internal redundancy.
* **Nest everything below words/cells:** cross-word occurrences and shared
  sounds would be duplicated or parent-dependent. A convenience serializer
  may nest references; the normative schema remains normalized.

## Compatibility and scope

Legacy outputs are migration oracles, not new contracts. Adapters may recreate
them from `trace` while migrating. IDs are opaque and request-scoped. Enum
additions are additive within a schema major version; changed field meaning is
breaking. Ordering is normative only where documented.

The first release supports Uthmani/Hafs. The schema avoids glyph-specific
assumptions, but IndoPak is not an acceptance gate.

## Consequences

Consumers wanting phonemes get a tuple. Every richer application pays for one
trace and chooses grouping and visual priority without re-running domain
logic. Before acceptance, the implementation must complete occurrence
participants, classification joins and orthographic non-sounding edges.
