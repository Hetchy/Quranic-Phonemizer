# Public projection redesign: legacy audit and delivery plan

This document turns the legacy evidence into a delivery plan for **Hafs,
Uthmani script**. Legacy applications test information sufficiency; they do
not dictate the public shape. IndoPak projection work is deferred.

## Executive conclusion

Ship the smallest useful surface:

* retain **phonemes** as the direct fundamental projection;
* add one lossless **relational trace** joining writing, canonical anchors,
  performed sound, transformations and Tajweed occurrences; and
* implement cells, silence, timing groups, letter maps, recited writing and
  coloured text as helpers/serializers over that trace.

This is two projections but only one rich schema. It preserves arbitrary
many-to-many relationships instead of baking the Inspector's grouping or a
teleprompter's preferred highlight into domain data.

## 1. Legacy projection audit

### Flat letter/phoneme mappings

The flat view guaranteed non-empty phoneme groups and absorbed silent letters
into a neighbour. It was convenient for aligner labels and animation: spaces
encoded boundaries, extensions were split, and silence merged PREV, NEXT or
across words.

That linear tape erased the reason a letter was silent, made merge direction a
policy, used source strings as keys, redistributed waqf-tanween and iltiqa
sounds, special-cased muqattaat, and failed the “one sounding grapheme” premise
for idgham shafawi.

**Retain:** sound order, word ownership, MFA grouping and every contributor.
**Retire:** non-empty entry invariants, embedded spaces, PREV/NEXT and
redistributed presentation ownership as canonical facts.

### Silent flags

The boolean view existed because flat groups did not identify their silent
members. The audit found continuing tanween alif/maqsura without an explaining
tag, context-dependent silah extensions, and idgham-shafawi cases where a flag
alone could not drive co-highlighting.

**Retain:** explicit absence with a typed cause and the relation from an
assimilated letter to its host sound. **Retire:** a separate truth source and
inference from Tajweed tag names.

### Tajweed mappings

The per-letter view usefully distinguished source and target rules and allowed
overlaps. It still reconstructed rules after phonemization and faced unstable
placement questions: madd on carrier/base, qalqala on echo/consonant, tafkheem
on vowel/consonant, synthetic Allah dagger alif and muqattaat overrides.

**Retain:** occurrence identity, exact rule, typed participants, grapheme and
sound reachability, overlaps and boundary context. **Retire:** parallel rule
vocabulary, post-hoc detection and placement priority hidden in a serializer.

### Character cells

This was the most mature legacy view. One source or implicit unit carried
role, status, phonemes, indices, a tag, share group and source-letter indices.
Its useful requirements are:

* every scalar is addressable and source-ordered;
* implicit units and transformations are visible;
* several marks may share one timing interval;
* one written unit may reach several sounds; and
* provenance survives spelling expansion.

Its debts must not become ontology. Cells mix source scalars with empty-string
virtual cells; duplicate word-local phoneme indices; use `share_group` as a
surrogate edge; lose overlaps through one `tag`; conflate orthographic role
with performance status; and compose shadda into source `chars` for a renderer.

The trace can reproduce cells; cells cannot reproduce the trace without these
special conventions.

## 2. Consumer sufficiency

### Inspector

Inspector needs source-order scalars, virtual writing, roles, replacements,
silence reasons, merger contributors/hosts, ordered sounds and every Tajweed
rule on both writing and sound. The trace supplies all of them. Grey, underline,
co-highlight and colour priority remain explicit presentation choices.

### Timestamp shards and teleprompter

Forced-alignment timestamps belong to performed sounds. Joining by `SoundId`
avoids choosing which duplicated cell owns a long vowel. Realization edges give
all co-highlighted graphemes; merger roles allow either host-only or all-letter
animation. A purely orthographic silent mark has no natural timestamp, so
adjacency/duration synthesis must remain an animator policy.

### Letter-level MFA

MFA needs a linear label stream although the domain is a graph. A helper can
coalesce ordered sounds by a declared host/contributor policy and return trace
IDs with its labels. Alignment then joins back without matching Arabic strings.

### Future colouring and correction

Granular colouring requires overlapping occurrences, not a winning tag. Error
correction requires rule identity/family, participant roles, expected sound
features and written targets. The same joins provide these without an
error-correction projection. Madd counts, selected duration and cause must be
structured semantics rather than parsed from names or tokens.

## 3. Current model readiness

### Present foundations

* Distinct grapheme, slot, sound and occurrence IDs prevent cross-domain key
  confusion.
* `Spelling` retains evidence, attestation, decoration and structural writing.
* `Attribution` distinguishes hosting, insertion, merger contribution and
  silence.
* Every attribution names an occurrence, so its cause is recoverable.
* `Aspect` preserves onset/nucleus ownership.
* Variant selection and boundary plan travel with the produced performance.

### Gaps before a public contract

1. **Orthographic zero is not performance silence.** Seats, otiose carriers,
   madd signs and decorations may lack a slot attribution. Trace construction
   needs a total grapheme row and explicit orthographic contribution, not only
   `render.anchored()`'s performed `Silent` rows.
2. **Participants lack roles.** The current tuple cannot say trigger, source,
   target, host, carrier or affected vowel. Define family-specific variants.
3. **Classification overlaps need a join.** A production attribution has one
   `by`, while madd, tafkheem and tarqeeq can classify its realization too.
4. **Anchoring over-collects marks.** Current `Decorates`/`Attests` lookup can
   attach a mark to either aspect. Highlight-self, highlight-anchor and
   evidence-for-rule are separate relations and must be defined.
5. **Inserted writing differs from inserted sound.** An unwritten helping
   vowel can have a slot; the 3:1 repair is slot-less. Only renderers invent
   display glyphs.
6. **Effects need mechanical definitions.** `replace` and `shorten` are useful,
   but must derive from canonical/performed state rather than string tests.
7. **Madd detail is incomplete for correction.** Add cause and
   permitted/selected duration semantics, with the evaluated realization.
8. **Order and ID scope need contracts.** Define cross-word merger, structural
   grapheme and slot-less-insertion order plus deterministic serialization.
9. **Recited writing remains derived.** Expose deletion/virtual edges so
   ADR-005 presets never become join keys or stored layers.
10. **Design 03 awaits implementation.** Keep its internal vocabulary out of
    the public trace while applying its resolved decomposition.

## 4. Uthmani knowledge checklist

The spike needs joined, stopped and started examples where applicable:

| Family | Relationships that must be representable |
|---|---|
| short/long vowel | base, haraka, carrier fan-in; shared timing without duplicate sound |
| silent carriers | otiose alif/waw/ya/maqsura, silence signs and typed cause |
| hamzat al-wasl | source, start vowel, joined deletion, repair and article lam |
| tanween | one mark to vowel+nun; continuing alif silence; waqf iwad carrier |
| silah | written/virtual extension, joined length and pausal deletion |
| Allah | lexical class, heavy/light lam, virtual/written dagger alif, waqf change |
| mergers | within/cross-word source, host, shared sound, complete/partial forms |
| noon/meem | trigger/source/target roles and nasal placement for noon/tanween |
| madd | haraka/carrier/mark, subtype, cause, counts and boundary change |
| qalqala | closure/release, one occurrence, consonant and stop degree |
| emphasis | consonant and governed vowel reach; raa and divine-name cases |
| muqattaat | compact glyph to spelled anchors/sounds/rules without cached mapping |
| waqf endings | vowel deletion, ta marbuta, iwad, arid/leen and qalqala |
| ibtida | start boundary, wasl vowel, gemination and right context |
| marks | imala, ishmam, tashil, sakt, seen/sad, iqlab, maddah and advice |
| slot-less repair | side/order, virtual edge, occurrence, sound and rendered form |

An unmodelled row blocks the contract; serializers may not repair it.

## 5. Trace invariants

1. Concatenated source graphemes exactly reproduce the input.
2. Every grapheme appears once and is anchor-linked or orthographic-only.
3. Every sound appears once in performance order and has a realization.
4. Every realization has one production occurrence and all IDs resolve.
5. Every deletion has no sound and a non-plain cause.
6. Every merger exposes contributor and host reaching one sound/occurrence.
7. Every insertion has an anchor or explicit side-of-anchor placement.
8. Every occurrence exposes typed participants and affected realizations,
   including classification-only occurrences.
9. No projection runs detectors, derives semantics from output tokens or
   chooses a visual priority.
10. Nested serializers round-trip to the same normalized trace and IDs.

## 6. Delivery plan

### A. Evidence and schema spike

1. Extract representative legacy rows and full-corpus counts for every family.
2. Build an internal normalized trace over Score/Inscription/Performance.
3. Recreate legacy cells, Tajweed maps, silence and letter groups from it.
4. Classify mismatches as retired presentation policy or internal knowledge
   gaps; fix the latter below projections.

### B. Model completion

1. Add family-typed participants and occurrence/realization coverage.
2. Make orthographic-only contribution total.
3. Define the closed transformation derivation table.
4. Add structured madd duration/cause semantics.
5. Implement design 03's vocabulary resolution.

### C. Contract and helpers

1. Accept ADR-010 with concrete Python/JSON schema, ordering, evolution and
   errors.
2. Ship `phonemes()` and `trace()`.
3. Add non-normative indices for grapheme, sound and occurrence; timing
   attachment; and source/recited-writing serializers.
4. Keep legacy adapters only through migration and label their grouping and
   colour priorities as legacy policy.

### D. Gates

Run full-corpus continuous, verse-edge, word-edge, targeted waqf and ibtida
traversals. Require invariants, baseline explainability, deterministic JSON
round-trip and a consumer fixture recreating Inspector/timestamp joins without
importing `canon`, `rules` or `engine`.

## 7. Non-goals and checkpoints

Non-goals are IndoPak parity in the first implementation, a universal UI cell,
fabricated silent timing, public internal dataclasses, and preservation of
legacy whitespace/merge-direction/empty-cell/single-tag conventions.

The spike has three schema questions: exact participant roles by family,
whether transformed Arabic returns virtual glyph records or a string plus
references, and whether sound features are always included or opt-in. None
requires another top-level projection. The number remains two unless a fact
cannot be queried without rerunning domain logic.
