# 01 - Two projections over one lossless graph

Status: **proposed**. Depends on [00-audit](00-audit.md) and
[ADR-013](../../adr/013-public-projection-foundations.md).
Scope: Uthmani, Hafs.

## 1. The decision

Two public projections, and no third.

| | Name | Shape | For |
|---|---|---|---|
| **P1** | `phonemes` | ordered notation tokens, with word boundaries | consumers that want only sound |
| **P2** | `Reading` | identified nodes plus typed relation arrays | every script, alignment, and tajweed consumer |

`Reading` replaces `character_phoneme_mappings`,
`letter_phoneme_mappings`, `silent_flags`, and `tajweed_mappings`. The four
legacy APIs were four traversals of the same join, with different relationship
losses. Publishing four smaller documents would require every consumer to
reconstruct that join again.

This does not force every consumer to load every relation. Named JSON fields
are independently ignorable, and an SDK may provide lazy indexes or narrower
views. The contract has one source of truth even when transport layers select
only part of it.

## 2. Identity and identifiers

A `Reading` is a snapshot of one fully identified request:

```python
@dataclass(frozen=True)
class Reading:
    schema_version: str
    request: ReadingRequest
    score_digest: str

    words: tuple[Word, ...]
    glyphs: tuple[Glyph, ...]
    units: tuple[Unit, ...]
    sounds: tuple[SoundNode, ...]
    occurrences: tuple[Occurrence, ...]

    spellings: tuple[SpellingEdge, ...]
    attributions: tuple[AttributionEdge, ...]
    modifiers: tuple[ModifierEdge, ...]
    contributions: tuple[GlyphContributionEdge, ...]


@dataclass(frozen=True)
class ReadingRequest:
    ref: str
    riwayah: Riwayah
    script: Script
    notation: str
    selection: CanonicalVariantSelection
    boundaries: BoundaryPlan
```

`selection` is serialized in canonical order. `boundaries` records starts,
stops, sakt, and edges rather than only the stop-sign policy that produced
them. `score_digest` identifies the canonical data against which indices were
resolved.

Every reference inside the document is an integer index into one array.
Indices are local to this document. A bare slot label is not advertised as a
durable external identifier: riwayah, selection, corpus revision, and schema
edition all affect what it means. A future durable key must include that
identity explicitly.

The wire format stores each relationship once. Reverse indexes such as
`units_by_word`, `glyphs_by_unit`, `sounds_by_unit`, and
`occurrences_by_sound` are pure SDK helpers and are never serialized as
parallel facts.

## 3. Nodes

Nodes carry intrinsic values and ordering. Relations live in section 4.

### 3.1 `Word`

```python
location: Location
text: str
starts: bool
junction_after: Junction       # join | sakt | stop | edge
advice: StopAdvice | None
lexeme: LexemeClass | None     # currently divine_name
```

`junction_after` is the complete boundary fact; `stops` would duplicate it.
`starts` is independent because a range may begin inside a verse or word
sequence. `lexeme` is lexical identity, not a tajweed tag. The occurrence that
applies tafkheem to the relevant lam remains in the performance graph.

Word membership points from a child node to its word. The corresponding word
lists are derived indexes.

### 3.2 `Unit`

```python
word: int
letter: CanonLetter
onset: Onset
nucleus: Nucleus
nunation: bool
spelled: bool
```

`Nucleus` is the existing discriminated union:

```python
Silent | Short(quality) | Long(quality) | Silah(quality) | PausalLong(quality)
```

This forbids combinations such as `quality=None, length=long`. `Silah` and
`PausalLong` remain lexical, boundary-conditional kinds; the performed sound
still depends on the requested boundary plan.

`Onset` remains one enum because the corpus and riwayah census found no valid
combination it cannot express. SDKs may derive `geminate`, `prosthetic`, and
`conditional` booleans for display. They are not additional wire facts.

There are deliberately no glyph, sound, rule, silence-reason, or rendered-text
fields on a unit. Those are relations or derived views. Madd counts and
durations are also absent: they belong to realization or teaching policy, not
to the canonical slot.

### 3.3 `Glyph`

```python
word: int | None
char: str
cls: GraphemeClass
source_index: int
```

The index is the scalar's ordinal in the requested inscription. A structural
glyph has `word=None`; it is not forced into a neighbouring word. A glyph does
not flatten all its spelling edges into `units`, `fact`, and `attests`, because
one glyph can participate in several differently typed edges.

### 3.4 `SoundNode`

```python
word: int
token: str
spec: Consonant | Vowel | Nasal | Release
```

`token` is the selected notation's serialization of `spec`. The discriminated
sound value already carries letter, quality, length, emphasis, gemination,
nasality, place, or release kind where those concepts apply. A flat record
with all of those fields optional would admit impossible sound states.

A sound has no stored unit, owner, merge source, insertion anchor, or rule
list. Each is stated exactly by a relation in section 4.

### 3.5 `Occurrence`

```python
rule: Rule
participants: tuple[Participant, ...]


@dataclass(frozen=True)
class Participant:
    anchor: AspectRef
    role: ParticipantRole      # trigger | source | target | context


@dataclass(frozen=True)
class AspectRef:
    unit: int
    aspect: Aspect
```

Participants explain why a rule matched. Attribution and modifier edges
explain what it did. This avoids a generic `effect` string that duplicates and
weakens those relations.

Roles are closed and checked against the rule family's participant schema.
`trigger` is the condition that made the rule applicable; `source` is its
canonical locus; `target` is the affected anchor; and `context` records a
required participant with none of those meanings. `host`, `contributor`, and
`carrier` are not repeated here: attribution edges state host and contributor,
while spelling and contribution edges state carrier participation.

`RuleFamily` and execution `Phase` are total functions of `Rule` in versioned
registries. They are derived rather than repeated in every occurrence.
`Rule.PLAIN` produces no occurrence; absence of a rule is plain.

## 4. Typed relations

The public graph keeps the distinctions already settled in ADR-002 and
ADR-003.

### 4.1 Spelling

```python
Evidences(glyph: int, unit: int, fact: SlotFact)
Attests(glyph: int, family: RuleFamily, anchor: int)
Decorates(glyph: int, unit: int)
Structural(glyph: int)

SpellingEdge = Evidences | Attests | Decorates | Structural
```

This preserves many-to-many script evidence without conflating its meaning.
The long-vowel haraka and carrier may both reach one unit through distinct
edges. A compact muqattaat grapheme may evidence facts on several units.
`Attests` witnesses a performance family without asserting a canonical fact.
`Structural` has no unit and no word.

### 4.2 Attribution

```python
Hosts(units: tuple[int, ...], aspect: Aspect, sound: int, by: int)
Inserted(anchor: tuple[int, Side], aspect: Aspect, sound: int, by: int)
MergedInto(units: tuple[int, ...], aspect: Aspect, sound: int, by: int)
Silent(units: tuple[int, ...], aspect: Aspect, by: int)

AttributionEdge = Hosts | Inserted | MergedInto | Silent
```

`Aspect` is mandatory. A final consonant can host an onset sound while a
separate nucleus attribution is silent at pause. That fact cannot be recovered
from sound kind.

`Inserted` preserves both the anchor and before/after side, so the 3:1 iltiqa
vowel needs neither a fake unit nor an empty glyph. A merger is a `Hosts` edge
and a `MergedInto` edge sharing sound and occurrence. Joint hosting remains a
tuple of units; it is not reduced to one preferred owner.

### 4.3 Modification

```python
Recolours(sound: int, by: int, feature: SoundFeature, value: bool)
Relengths(sound: int, by: int, length: Length)
Classifies(sound: int, by: int)

ModifierEdge = Recolours | Relengths | Classifies
```

These edges retain the occurrence after the engine applies an effect.
`Classifies` connects a classification-only occurrence to a sound without
claiming ownership. A soundless gesture such as ishmam is still represented by
its occurrence and target participant; it does not receive a fake sound.

### 4.4 Glyph contribution

```python
Presents(glyph: int, target: PerformanceRef)
OrthographicOnly(glyph: int)

PerformanceRef = AttributionRef | ModifierRef | OccurrenceRef
GlyphContributionEdge = Presents | OrthographicOnly
```

Each reference variant is a tagged index into the named relation or occurrence
array. A glyph may have several `Presents` edges. `OrthographicOnly` is
exclusive and means the glyph has no performance contribution; its spelling
edge still states its canonical or structural attachment.

This relation cannot be inferred from unit audibility. A haraka and carrier
can evidence the same nucleus and share its vowel, while a carrier waw under a
dagger is orthographic-only and the dagger presents the vowel. A maddah can
present an attribution or modifier despite supplying no canonical fact. A
soundless ishmam mark can present its occurrence without fabricating a sound.

## 5. Derived views, not stored facts

The following conveniences have named definitions:

```text
units_by_word(w)       = units whose word is w
glyphs_by_unit(u)      = spelling edges naming u
sounds_by_unit(u, a)   = attribution edges naming u and aspect a
rules_by_sound(s)      = occurrences reached by attribution or modifier edges
performance_by_glyph(g)= targets of Presents edges for g
family(o)              = FAMILY_OF[occurrences[o].rule]
phase(o)               = PHASE_OF[occurrences[o].rule]
```

Display ownership is also derived, but it is explicitly a rendering policy,
not domain ownership:

```text
display_glyph(sound, policy)
  = choose among glyphs whose Presents targets reach sound
```

This can choose a haraka or a length carrier. A stored `owner: Unit` cannot,
because both glyphs may evidence the same unit.

Recited writing is a separate serializer over `write`, spelling, contribution,
attribution, and insertion anchors. It may return render glyphs with
source-glyph links. For a slotless insertion it writes the inserted sound at
its anchor side. Source glyphs remain unchanged, and no core `Unit.glyphs`
field is promised non-empty.

Legacy presentation states become pure derivations:

```text
inserted  = an Inserted attribution
dropped   = a source glyph Presents a Silent attribution, or is OrthographicOnly
merged    = paired Hosts and MergedInto attributions
replaced  = rendered writing differs from source spelling
shortened = a Relengths edge to short
present   = none of the above
```

## 6. Model work required

The projection exposes four gaps that must be fixed before it ships.

**C1 - semantic participant roles.** Replace the unlabelled
`Participants.slots` tuple with ordered `Participant(AspectRef, role)` values.
This is not a mechanical first/other split: each rule family must define its
allowed and required trigger, source, target, and context roles. Tests assert
the roles for cross-word assimilation, madd, boundary elision, and
classification-only rules.

**C2 - retained modifier provenance.** When the engine applies `Recolour` or
`Relength`, retain the occurrence-to-sound edge and its value. Add
`Classifies` for a classification-only occurrence that names a sound. This
closes the current loss between verdict application and `Performance`.

**C3 - total glyph contribution.** Build the cross-layer join that tells which
performance targets each glyph presents. Every non-structural glyph has one or
more `Presents` edges or exactly one `OrthographicOnly` edge. The construction
must distinguish a sounded dagger from its silent carrier, a sounded maddah
from an otiose seat, and a performance deletion from orthographic zero. If
the source model cannot determine a link, it must be fixed below the
projection; serializers may not detect the answer from tokens or rule names.

**C4 - ref-to-document orchestration.** Resolve `(ref, boundary policy,
selection)` through the selected corpus, build the Score and Inscription, run
the Performance, and assemble one index space across the requested range.
Internal starts, arbitrary stops, sakt, and cross-verse joins use the same
path; they are not separate projection modes.

No rule behaviour changes as part of C1-C4. `CLASSIFICATION_ONLY` remains a
valid statement that an occurrence owns no sound.

## 7. Rule vocabulary

Keep the branch `Rule` set:

1. Names are trigger-independent. Noon and tanween ikhfa share one rule; the
   trigger is a participant and `unit.nunation`.
2. `FAMILY_OF` is total, so a coarse legend is derived without serializing a
   second classification beside every occurrence.
3. Degrees remain distinct rules, such as the qalqala and idgham degrees.

Omit `Rule.PLAIN` from occurrences. Do not split `TAFKHEEM` by cause: the
occurrence participants and lexical identity state why it applied.

## 8. What consumers read

| Application | Reads |
|---|---|
| Inspector cells | nodes plus spelling, contribution, attribution, and modifier indexes |
| Silent highlighting | `Presents(Silent)` and `OrthographicOnly` contribution edges |
| Disjoint timing | a chosen `display_glyph` policy |
| Co-highlighting | all units on the relevant `Hosts` edge |
| Cross-word bridge | paired `Hosts` and `MergedInto` edges |
| Flat letter mappings | a legacy adapter over spelling and attribution |
| Tajweed-coloured script | contribution edges to occurrences, attributions, and modifiers |
| Tajweed ASR | sounds, occurrences, modifiers, and request selection |
| Custom notation | the same graph with a different `token` serializer |

## 9. Shipping questions

The graph shape is settled by ADR-013. Three empirical gate items remain:

1. Does the Uthmani inventory bind every iqlab small meem through a typed
   spelling edge?
2. Is recited writing total for every unit and slotless insertion in the
   corpus?
3. Does every preserved legacy field round-trip exactly in continuous, verse,
   and word boundary modes?

[02-equivalence-gate](02-equivalence-gate.md) makes each one executable.
