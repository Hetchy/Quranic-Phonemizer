# Spine C — the riwāyah is the score; scripts are witnesses

## Position and core graph

The identity-bearing object is a **canonical riwāyah score**, not either
orthographic corpus. Uthmani and IndoPak are independently preserved witnesses
aligned to that score. This is the only contract strong enough to make
script-independence a guarantee rather than a hope that two normalizers happen
to agree.

```text
SourceWitness ──WitnessLink──> CanonicalScore
  exact scalars                 words → units → addressable components
                                      │
                         selected variant + boundary plan
                                      ▼
                               RealizationGraph
               recited units · semantic segments · applications
                         \_____ AttributionEdge _____/
                                      │
                                      ▼
                                 projections
```

`SourceWitness` is byte-exact. `CanonicalScore` contains recitation inputs
only: canonical letter identity, vowel gesture (including sākin/tanwīn and
quantity), gemination, lexical roles, stop advice, variant sites, and finite
location facts. It contains neither IPA tokens nor rule labels. The selected
`RealizationGraph` contains ordered semantic `RecitedUnit` and `Segment` nodes,
plus the decisions and attribution that produced them. Output strings are
renderer products, never domain state or data-file payloads.

## 1. Layers and addressing

Three layers are sufficient:

1. `SourceWitness(script_id, words, graphemes, clusters)` preserves every
   scalar, offset, attachment, and structural sign.
2. `CanonicalScore(riwayah, words, components, variant_sites)` is the
   script-independent rule input.
3. `RealizationGraph(score_revision, selection, boundaries, recited_units,
   segments, applications, attributions)` is one requested traversal.

The canonical address is
`ComponentRef(WordKey, UnitKey, ComponentKind)`. `WordKey` and `UnitKey` belong
to the versioned riwāyah score; they are not offsets in a source string.
`ComponentKind` is closed (`BASE`, `VOCALISM`, `GEMINATION`, `SMALL_VOWEL`,
and the other reviewed linguistic components). Repeated components use stable
component keys assigned in the score, never “the nth occurrence of glyph X.”
Expanded letter names receive
`RecitedUnitRef(expansion_application, name_key, unit_key)`, so they cannot be
confused with source words or fabricated sub-locations.

`WitnessLink(graphemes, component, evidence_role)` is many-to-many and
witness-local. Replacing Uthmani with IndoPak replaces grapheme ids and links,
but all rules, occurrences, and realization references still use the same
canonical component ids. Request-local segment ids are allowed because their
parent score revision, variant selection, and boundary plan are stored.

The unresolved risk is future source tokenization that disagrees with the
riwāyah's word division. The present two Hafs witnesses are slot-aligned. A
third witness with a genuine join/split would settle whether `WordKey` can
remain the primary container or must become a verse-scoped lexical-token key;
component identity and witness linking do not otherwise change.

## 2. Attribution

Use one sound/writing attribution relation, not separate alignment, silence,
merge, and insertion tables:

```text
AttributionEdge(
  origin: ComponentRef | ApplicationRef,
  result: SegmentRef | RecitedUnitRef | None,
  role: REALIZES | CARRIES | CO_REALIZES | INSERTS | SUPPRESSES,
  application: ApplicationRef | None
)
```

The closed roles describe facts, not executable effects. Constraints make the
cases precise:

- a harakah and full carrier have two edges to the same vowel segment
  (`REALIZES`, `CARRIES`);
- a cross-word merger gives both words' components edges to the same result
  (`CO_REALIZES` for the assimilated subject, `REALIZES` for the target), tied
  to one application;
- an insertion originates at its application, never at a fictitious source
  grapheme;
- a deletion/silence is `SUPPRESSES` with `result=None` and a mandatory
  application or typed orthographic convention.

`WitnessLink` is deliberately not a second attribution system: it says how a
script evidences canonical facts. Following it backwards turns canonical
attribution into Uthmani- or IndoPak-grapheme attribution. Shared result ids,
not projection-local “share groups,” express joint ownership.

## 3. The script boundary

Each riwāyah packages a versioned `CanonicalScore`. A `ScriptAdapter` has the
exact contract:

```text
parse exact witness
  → WitnessParse(graphemes, clusters, observations)
align(WitnessParse, CanonicalScore, script-scoped facts)
  → WitnessLink[] | diagnostic failure
```

The adapter does not return the object consumed by rules. It must account for
every source scalar, align every recitation-bearing observation to the
already-addressed score, and validate any redundant hint. Missing evidence is
permitted only where a reviewed score or location fact supplies it. Conflicting
evidence fails at the exact location. Therefore equal `(riwayah,
score_revision, variant_selection, boundary_plan, render_profile)` necessarily
means equal segments and byte-identical phonemes, regardless of `script_id`.

The sources under-specify different facts:

| Witness limitation | Supplying mechanism |
|---|---|
| Uthmani writes 5,412 assimilating nūns bare; explicit sukūn is not a reliable rule switch | canonical `SAKIN` vocalism plus the nūn decision table; bare/marked remains witness evidence |
| Uthmani omits iqlāb marks | derive iqlāb from canonical subject, next letter, and boundary |
| IndoPak uses plain initial alef where Uthmani types hamzat al-waṣl | canonical lexical identity |
| IndoPak's generic “noted here” mark does not type imāla/tashīl, and it omits ishmām and the seven-alifs distinction | typed riwāyah location facts; a present mark only validates |
| Uthmani `ۜ` means either sakt or a sīn/ṣād choice | location-addressed `BoundaryFact` or `VariantSite`, never scalar meaning |
| hamza seats, madd signs, silence signs, and stop signs differ | script-scoped sequence parsers normalize to closed canonical values |
| Uthmani's ornamental 2:72 construct has no IndoPak counterpart | a `(riwayah, script, canonical address)` normalization case which disappears at this boundary |

Finite source inventories, canonical letter/vowel facts, pair sets, variant
choices, and exception locations may be data. Algorithms, rule applications,
phoneme strings, and rule-tag lists may not.

## 4. Rule occurrences

A named decision is a typed `Application` union. Tajwīd variants include
`NoonApplication`, `MeemApplication`, `IdghamApplication`,
`QalqalahApplication`, `EmphasisApplication`, and `MaddApplication`;
boundary, lexical expansion, orthographic silence, and helping-vowel decisions
are `RealizationApplication` variants rather than invented Tajwīd names.
Each variant has a common id plus family-specific canonical participants,
context, result segment ids, and its attribution-edge ids. For example, an
ikhfāʾ application has a subject and following trigger but no target; an
idghām application requires a target.

The graph builder commits the application, its new/replaced segments, and its
attribution edges atomically. It rejects dangling participants, a claimed
result not created by that application, and invalid family shapes. There is no
`rules: [...]` field on letters. A later tajwīd or highlighting projection can
only traverse stored applications and their participants; projection packages
do not import classifiers. That dependency boundary structurally prevents a
projection from re-detecting a different rule.

## 5. Rule execution

Execution is an explicit dependency DAG over immutable snapshots:

```text
variant selection
  → lexical expansion
  → boundary resolution (JOIN / STOP / SAKT / EDGE)
  → effective forms and boundary repairs
  → baseline segments and carrier roles
  → coalescence/silence (nūn, mīm, all idghām families)
  → quantity and madd classification
  → emphasis, ghunnah colouring, qalqalah
```

A classifier reads a `StageView` and returns addressed `ApplicationDelta`s; it
never mutates a letter or neighbouring word. Nūn idghām affects the next
letter by naming its `ComponentRef` and prior segment in the delta. Deltas from
one stage are validated for conflicting claims and batch-committed before the
next snapshot. Exhaustive families produce exactly one decision; unrelated
feature axes may compose only through an explicit later stage.

Comparable families get comparable modules and return comparable applications.
`classify_raa_emphasis`, `classify_allah_lam_emphasis`, and
`classify_inherent_emphasis` are peers in the emphasis stage; none is an
inline branch in a generic letter emitter. Nūn, mīm, lām shamsiyyah, and the
other assimilation families are peers in coalescence. Their algorithms remain
typed Python; only closed sets and pair facts are declarative. A genuine
riwāyah delta replaces one classifier through explicit pipeline construction,
not a generic YAML effect engine.

## 6. Recited writing

Recited writing is already present in the graph. Each `RecitedUnit` stores a
semantic Arabic form, reading order, sound attribution, and exactly one origin:
canonical components or an application. A suppressed source unit remains in
the graph with a reason; an inserted unit has application provenance.
`ExpansionGroup(compact_components, expanded_units)` stores both sides of a
lexical expansion such as muqaṭṭaʿāt. A waqf substitution creates a recited
form linked to the source component and the waqf application rather than
editing source text.

A text projection consequently performs selection only:

- source versus recited follows witness graphemes or recited forms;
- silent shown/hidden retains or filters `SUPPRESSES` units;
- inserted shown/hidden retains or filters application-origin units;
- compact/expanded chooses the corresponding side of `ExpansionGroup`.

No option invokes hamzat-al-waṣl, waqf, silence, or expansion logic. Thus
phonetic text, inspection text, and exact source text remain views of one
realization instead of independent rebuilds.

## 7. Variant selection

Khilāf lives in `VariantSite(ComponentRef, allowed canonical choices, default
choice, riwayah provenance)`. A request or immutable phonemizer profile supplies
`VariantSelection`; the riwāyah default fills omissions. Selection materializes
the chosen canonical component before expansion, boundaries, or rules.
Choosing `س` instead of `ص` therefore changes the actual selected
`LetterIdentity`, and emphasis, vowel colouring, rāʾ look-back, occurrences,
segments, and rendering all follow naturally. The renderer never sees an
unresolved variant.

## 8. Exceptions

A justified exception names a domain fact, has typed preconditions and a
Python handler returning the same application shape as an ordinary rule, and
has positive, neighbouring-negative, boundary, and witness-equivalence cases.
Its data contains only reviewed addresses (and a small typed payload when the
fact genuinely varies). A patch that says “replace these segments,” “clear
this tag,” or targets a glyph because current output is wrong is rejected.

There are two honest scope keys:

- source-convention cases:
  `(Riwayah, ScriptId, CanonicalAddress, SourcePattern)`;
- recitation cases:
  `(Riwayah, CanonicalAddress, BoundaryMode, VariantSelection)`, omitting
  axes the typed handler proves irrelevant.

The first must leave no script-specific state after alignment. The second is
evaluated identically for every witness.

## Stored walkthroughs

**Cross-word idghām, `مِن رَّبِّهِمْ` (2:26:18–19).** Uthmani `مِن` links a
bare nūn to canonical `SAKIN`; IndoPak `مِنْ` links nūn plus explicit sukūn to
the same component. With a `JOIN` boundary,
`IdghamApplication(BILA_GHUNNAH, subject=nūn, target=rāʾ, result=s_rraa)` is
stored. The nūn and rāʾ have edges to `s_rraa` across two `WordKey`s; the
nūn's `CO_REALIZES` edge and application recover why it has no independent
sound.

**Long vowel, two writings.** In a full-carrier spelling such as `قَالَ`, the
fatha `REALIZES` one `VowelSegment(A,LONG)` and alef `CARRIES` it. In a
dagger-alef spelling such as `ٱلرَّحْمَـٰنِ`, the fatha and dagger-alef point
to the same segment type with the same two roles; the carrier's witness
grapheme is merely different. No segment has a “small” flag.

**Silent grapheme.** In joined `بِسْمِ ٱللَّهِ`, the canonical
hamzat-al-waṣl component has
`AttributionEdge(component, None, SUPPRESSES, wasl_application)`. Exact source
text retains `ٱ` (or its IndoPak spelling); recited text may filter it; the
reason remains queryable.

**One word in both scripts, 1:1:2.** Uthmani stores `ٱللَّهِ`; IndoPak stores
`اللّٰهِ`. Uthmani directly evidences hamzat al-waṣl and fatha but has no
dagger alef. IndoPak directly evidences dagger alef but its plain alef does not
type waṣl and it omits the fatha. Both align to the same canonical
hamzat-al-waṣl, geminated lām, long-A vowel gesture, hāʾ, and kasra; the
riwāyah lexical record supplies what each witness omits. Alignment succeeds
only if that canonical word hash agrees, after which the two rule runs are the
same run.

## Main cost

This design pays for an additional curated artifact: the canonical score and
versioned witness alignments. Every corpus correction, new script, or lexical
variant must preserve canonical ids or publish an address migration, and
validation tooling becomes substantial. That duplication is intentional. It
moves uncertainty out of phonological code and makes “same riwāyah, same
choices, same boundaries ⇒ identical phonemes” an enforceable invariant.
