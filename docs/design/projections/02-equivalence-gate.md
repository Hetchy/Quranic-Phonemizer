# 02 - The equivalence and completeness gate

Status: **proposed**. This is the acceptance criterion for
[01-design](01-design.md).

## 1. What the gate proves

Replacement needs two independent proofs:

1. **Legacy preservation.** Every legacy field promised during migration is
   reproduced exactly by a pure adapter over `Reading`.
2. **Graph completeness.** Every new typed relation is complete and obeys its
   domain laws, including facts for which legacy has no oracle.

Passing only the first would preserve legacy loss. Passing only the second
would permit accidental consumer regressions.

The frozen legacy data is an information-coverage reference, not a correctness
oracle. A mismatch has exactly one of these dispositions:

- `regression`: unexplained, and the gate fails;
- `correction`: one exact old/new case in a reviewed corrections ledger, with
  its domain reason and regression test;
- `addition`: excluded from the legacy adapter but required by a new-graph law;
- `retirement`: an explicitly named legacy presentation promise, approved
  before the gate runs.

There is no broad exemption for changed tokens or additive fields. A token
correction is allowlisted at the affected refs and boundary modes. A new edge
must pass completeness laws even though the legacy side cannot contain it.

## 2. Frozen reference and execution matrix

`research/legacy-baselines/manifest.json` is the source of truth. It pins
legacy revision `b3bc53a`, reference `1-114`, native row shapes, byte counts,
and SHA-256 digests for:

- phonemes;
- tajweed mappings;
- letter-to-phoneme mappings;
- character-to-phoneme mappings;
- silent flags;
- phonetic text.

The harness verifies every manifest digest before comparison. It does not
silently regenerate the reference from the current checkout.

The full-corpus baseline runs in all three committed modes:

| Mode | Boundary meaning |
|---|---|
| `continuous` | no requested stops |
| `verse` | stop at verse boundaries |
| `word` | stop after every source word |

Those modes cover the bulk corpus but not request orchestration. A separate
fixture matrix covers:

- a range beginning inside a verse;
- an arbitrary internal stop;
- sakt;
- a cross-word and cross-verse join;
- a multi-verse range in one index space;
- every non-default `VariantSelection` point;
- each stop-advice policy that changes the resulting `BoundaryPlan`.

Where the pinned legacy API can express the request, the fixture compares both
implementations. Otherwise it asserts the domain result and graph laws
directly. The report says which kind of oracle each fixture used.

## 3. Exact legacy adapters

`tools/projection_parity.py` is the planned harness. For each manifest mode it:

1. loads `Reading` for the same source request;
2. applies one pure adapter per legacy view;
3. compares native rows, field order where positional, values, and row order;
4. reports residues by adapter, field, rule, boundary mode, and cause;
5. exits non-zero for any residue without an approved disposition.

Counts and merge-direction agreement are diagnostics, not equivalence. The
acceptance test is exact equality after the documented adapter.

### 3.1 Preserved and intentionally changed promises

| Legacy view | Migration promise |
|---|---|
| `phonemes` | exact tokens and word grouping, except exact correction-ledger entries |
| `phonetic_text` | exact lines and order, except the same correction entries |
| `silent_flags` | exact tuple rows after legacy tokenization |
| `tajweed_mappings` | exact legacy rule vocabulary and source/target rows after the vocabulary adapter |
| `letter_phoneme_mappings` | exact characters, tokens, grouping, row order, and merge direction |
| `character_phoneme_mappings` | exact cells and every legacy field after the presentation adapter |

No current field is declared retired. If exact letter grouping or a cell field
cannot be reconstructed, the design is incomplete until the field is either
made derivable or explicitly retired with consumer approval.

New rule families and richer edges do not appear as surprise extra rows in a
legacy adapter. The adapter selects the legacy vocabulary; the completeness
suite separately proves the new facts exist.

### 3.2 `silent_flags`

For each non-structural source token:

```text
links  = contribution edges for the token's source glyphs
silent = the legacy silence policy over Presents targets and OrthographicOnly
mark   = the silence-sign glyph presenting the same outcome, or ""
```

The policy distinguishes `Presents(Hosts)`, `Presents(Silent)`,
`Presents(MergedInto)`, and `OrthographicOnly`; it never infers glyph
audibility from whether a related unit has any sound. This is what makes the
carrier waw silent while the dagger on the same nucleus remains sounded.

The adapter then applies the legacy scalar grouping exactly: dagger alif,
mini-waw, and mini-yaa remain separate where legacy separated them; other
combining marks rejoin their base. The following named cases must be exact:

- a silent carrier waw under dagger alif;
- mini-waw and mini-yaa silah at pause;
- taa marbuta at pause;
- all legacy `vowel_silent` rows.

Every `Presents(Silent)` outcome must name an occurrence.
`OrthographicOnly` instead keeps its script reason in the glyph's spelling
edges; it does not fabricate a performance occurrence. The residue report
groups `vowel_silent` by the typed case and fails if any row has neither.

### 3.3 `tajweed_mappings`

Occurrence participants supply trigger, source, target, and context anchors;
contribution edges locate the source glyphs; attribution and modifier edges
locate the affected sound. A versioned vocabulary table maps the current
`Rule` to the legacy rule names and trigger splits.

Source and target are reconstructed from semantic roles, not tuple position.
For assimilation, the disappearing trigger and receiving target are distinct
even though both relate to one sound. New rules such as explicit izhar are
filtered from the compatibility view and checked by graph completeness.

The adapter must reproduce every legacy word split, character string,
`source_rules`, `target_rules`, and row order exactly.

### 3.4 `letter_phoneme_mappings`

This adapter intentionally owns the legacy presentation grouping. It starts
from source glyph order, typed spelling edges, and aspect-bearing
attributions, then applies the versioned legacy merge policy.

The test is row-for-row equality, including:

- silent units merged left or right;
- lam-shamsiyyah and wasl elision;
- idgham source and host grouping;
- iltiqa shortening;
- waqf tanween and the otiose alif;
- muqattaat expansions.

Agreement only on merge direction is insufficient. The public claim is that
the old view is derivable, so its exact grouping must be derivable.

### 3.5 `character_phoneme_mappings`

Every legacy field is adapted:

| Cell field | Source in `Reading` |
|---|---|
| `chars` | source spelling or derived recited writing |
| `role` | folded `GraphemeClass` |
| `status` | typed glyph contribution plus source/rendered difference |
| `phonemes` | sound targets reached by glyph contribution |
| `phoneme_indices` | sound indices rebased word-local |
| `tag` | legacy priority over compatible occurrences |
| `secondary_tags` | remaining compatible occurrences |
| `phoneme_rule_tags` | occurrences reached by contribution, attribution, and modifier edges |
| `share_group` | units on joint or shared sound relations |
| `source_letter_index` | source glyph index |
| `source_letter_indices` | spelling edges back to source glyphs |

The priority order and four-role fold are compatibility policy in this adapter,
not facts copied into the core schema.

Named fixtures cover every former frontend synthesis: helping vowels in all
qualities, 3:1 iltiqa insertion, divine-name dagger alif, madd iwad at pause,
dropped silah, taa marbuta, iqlab noon and small meem, and each muqattaat
opening.

## 4. Graph completeness laws

These laws run over the entire corpus in all three boundary modes.

### 4.1 Envelope and indices

- `schema_version`, request identity, canonical selection, boundary plan, and
  `score_digest` are present.
- Canonical serialization of the same request is byte-stable.
- Every index is in range and points to the declared node kind.
- Node order is reading order and one index space spans the whole request.
- Changing riwayah, selection, boundary plan, notation, or Score changes the
  corresponding identity field; caches cannot alias the documents.

### 4.2 Spelling

- Every source scalar produces exactly one `Glyph` node.
- Concatenating `glyph.char` in `source_index` order reproduces the requested
  source text as the exact Unicode scalar sequence, including internal spaces
  and structural marks.
- Every glyph participates in at least one spelling edge.
- `Structural` glyphs have `word=None` and no unit-bearing spelling edge.
- Every `Evidences` edge has the correct `SlotFact`.
- Every `Attests` edge names a valid family and anchor.
- Every `Decorates` edge names the unit it visually marks.
- Many-to-many edges for long-vowel carriers, tanween, and muqattaat are
  present rather than collapsed.
- Every iqlab small meem is bound by its intended typed edge.

### 4.3 Attribution

- For each unit and each applicable `Aspect`, exactly one performed outcome is
  stated: hosted, merged, or silent.
- Every sound has exactly one primary origin: one `Hosts` edge or one
  `Inserted` edge. `MergedInto` never becomes a second owner.
- Every insertion has a valid anchor, side, aspect, sound, and occurrence.
- Every merger has a `Hosts` and `MergedInto` pair sharing sound and
  occurrence, with distinct host and contributor units.
- Every silence has an occurrence reason and no sound.
- Joint hosts preserve all participating units.
- The final-consonant pause fixture proves that an onset can host while the
  same unit's nucleus is silent.

### 4.4 Occurrences, participants, and modifiers

- Every participant names a valid `(unit, Aspect)` anchor.
- Every occurrence has valid, ordered roles under its rule family's schema,
  including required and repeatable role cardinalities.
- Every target participant is reached by an attribution or modifier when the
  rule changes or classifies a sound.
- Every applied `Recolour` and `Relength` has exactly one retained modifier
  edge with its value.
- Every classification-only rule that names a sound has a `Classifies` edge.
- Soundless ishmam has a target participant and no fabricated sound.
- `FAMILY_OF` and `PHASE_OF` are total for every public `Rule`.
- Deriving reverse indexes introduces no duplicate or dangling relation.

### 4.5 Glyph contribution

- Every non-structural glyph has one or more `Presents` edges or exactly one
  `OrthographicOnly` edge, never both.
- Every `Presents` target resolves to an attribution, modifier, or occurrence
  and is compatible with the glyph's spelling edges.
- Structural glyphs have no contribution edge.
- A haraka and ordinary carrier may both present one hosted nucleus sound.
- A carrier under a dagger is `OrthographicOnly`; the dagger presents the
  hosted nucleus sound.
- A maddah may present a performance target even though `Decorates` supplies
  no canonical fact.
- A soundless process mark may present its occurrence without a fabricated
  sound.
- No adapter or serializer infers glyph audibility from unit audibility.

### 4.6 Recited writing

- `write` is total for every unit that has a recited representation.
- Every rendered glyph links either to source contribution and spelling edges
  or to one inserted sound and its anchor side.
- Source glyph order and values never change.
- An insertion needs neither a fake unit nor `char=""`.
- Source and rendered strings reproduce every legacy `present`, `inserted`,
  `dropped`, `replaced`, and `shortened` case through the definitions in
  01-design.

## 5. Schema and negative tests

The JSON schema uses tagged unions for nucleus, sound, spelling, attribution,
modifier, and glyph-contribution values. Tests reject at least:

- a nullable quality paired with an incompatible nucleus kind;
- a sound with fields from two sound variants;
- `Structural` carrying a unit or word;
- `Evidences` without a fact;
- `Inserted` without a side;
- `Silent` carrying a sound;
- an attribution without `Aspect`;
- a merger without its matching host;
- a `Presents` edge with an out-of-range or wrong-kind target;
- a glyph carrying both `Presents` and `OrthographicOnly`;
- a non-structural glyph with no contribution edge;
- an out-of-range or wrong-kind index;
- duplicate canonical relations;
- an unknown schema version.

Round-trip tests cover canonical JSON, optional SDK-derived indexes, and schema
evolution. Adding a union member requires a schema-version change and a
negative test showing older readers fail clearly rather than misinterpret it.

## 6. Domain adequacy matrix

Each applicable family has joined, stopped, and started fixtures. An
unmodelled relationship blocks the contract; an adapter or serializer may not
repair it.

| Family | Relationships that must be represented |
|---|---|
| short and long vowels | base, haraka, carrier fan-in, shared sound, and distinct glyph contribution |
| silent carriers | otiose alif, waw, yaa, and maqsura; silence sign; dagger seat versus sounded dagger |
| hamza wasl | source glyph, start vowel, joined deletion, repair, and article lam |
| tanween | one mark to vowel and nunation anchors; continuing carrier silence; waqf iwad |
| silah | written or virtual extension, joined length, and pausal deletion |
| divine name | word lexical class, heavy or light lam occurrence, written or virtual dagger, and waqf change |
| mergers | within-word and cross-word source, host, contributor, shared sound, complete and partial forms |
| noon and meem | source, trigger, target roles and nasal placement for noon, tanween, and meem |
| madd | haraka, carrier, mark, subtype, participant-derived cause, and boundary change |
| qalqala | closure and release, one occurrence, consonant reach, and stop degree |
| emphasis | consonant and governed vowel reach, including raa and divine-name cases |
| muqattaat | compact glyph to spelled units, sounds, and rules without a cached mapping |
| waqf endings | nucleus deletion with onset retained, ta marbuta, iwad, arid, leen, and qalqala |
| ibtida | start boundary, wasl vowel, gemination, and right context |
| marks and advice | imala, ishmam, tashil, sakt, seen/sad, iqlab, maddah, and stop advice |
| slotless repair | side, order, occurrence, sound, contribution-free insertion, and rendered form |
| source structure | spaces, internal spaces, tatweel, stop signs, and verse markers round-trip exactly |

Madd cause is required through rule and participant semantics. Permitted and
selected counts remain outside this contract until request identity includes
the transmission path or realization policy that makes them authoritative.

## 7. Order and CI policy

1. Implement C1-C3 with their local laws.
2. Define the versioned JSON schema and negative tests.
3. Assemble a single-verse `Reading` and pass the domain adequacy matrix.
4. Implement C4 for ranges, internal boundaries, and selections.
5. Implement `tools/projection_parity.py`; verify the frozen manifest.
6. Pass each exact adapter in continuous, verse, and word modes.
7. Pass the extended request matrix and full graph-completeness suite.

A small deterministic sample and all negative tests run on every pull request.
The full `1-114` matrix is required before the public replacement merges. CI
publishes the structured residue report even on success; merge requires zero
unexplained residues and a corrections ledger whose entries all have domain
tests.
