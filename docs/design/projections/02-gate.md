# 02 - The equivalence and completeness gate

Status: **proposed**. The acceptance criterion for [01-contract](01-contract.md).

## 1. What the gate proves

Two independent proofs:

1. **Legacy preservation.** Every legacy field promised during migration is
   reproduced exactly by a pure adapter over `Mappings`.
2. **Graph completeness.** Every typed relation is complete and obeys its
   domain laws, including facts for which legacy has no oracle.

Passing only the first would preserve legacy loss. Passing only the second
would permit consumer regressions.

The frozen legacy data is an information-coverage reference, not a
correctness oracle. A mismatch has exactly one disposition:

| | |
|---|---|
| `regression` | unexplained; the gate fails |
| `correction` | one exact old and new case in `docs/conformance/corrections.md`, with its domain reason and a regression test |
| `addition` | excluded from the legacy adapter, required by a completeness law |
| `retirement` | a named legacy presentation promise, approved before the gate runs |

There is no broad exemption for changed tokens or additive fields. A token
correction is allowlisted at the affected refs and boundary modes.

## 2. Frozen reference and execution matrix

`research/legacy-baselines/manifest.json` pins the legacy revision, the
reference range, native row shapes, byte counts and digests for phonemes,
tajweed mappings, letter-to-phoneme mappings, character-to-phoneme mappings,
silent flags and phonetic text. The harness verifies every digest before
comparison and never regenerates the reference from the current checkout.

The bulk corpus runs in three modes: `continuous` (no requested stops),
`verse`, and `word`. A separate fixture matrix covers what those modes do not:

- a range beginning inside a verse, including one that clips a ledger-addressed
  word;
- an arbitrary internal stop;
- sakt;
- a cross-word and a cross-verse join;
- a multi-verse range in one index space;
- every non-default variant point;
- each stop-advice policy that changes the resulting boundary plan.

Where the pinned legacy API can express the request, the fixture compares both
implementations; otherwise it asserts the domain result and the laws directly.
The report says which kind of oracle each fixture used.

Continuous mode is assembled in chunks. The overlap must exceed the longest
cross-word reach any rule takes, and the equivalence law is stated over the
**whole document**, not over its sounds: an overlap too short invents rule
instances while leaving every token identical.

## 3. Exact legacy adapters

`tools/projection_parity.py` is the harness, with a CI job and a residue path
under `docs/conformance/`. For each manifest mode it loads `Mappings` for the
same request, applies one pure adapter per legacy view, compares native rows
including field and row order, reports residues by adapter, field, rule, mode
and cause, and exits non-zero for any residue without an approved disposition.

Counts and merge-direction agreement are diagnostics. The acceptance test is
exact equality after the documented adapter.

| Legacy view | Promise |
|---|---|
| `phonemes` | exact tokens and word grouping |
| `phonetic_text` | exact lines and order |
| `silent_flags` | exact tuple rows after legacy tokenization |
| `tajweed_mappings` | exact legacy rule vocabulary and source and target rows after the vocabulary adapter, the target reconstructed from the trigger the rule read |
| `letter_phoneme_mappings` | exact characters, tokens, grouping, row order and merge direction |
| `character_phoneme_mappings` | exact cells and every legacy field after the presentation adapter |

Each is subject to the correction entries. No field is declared retired; if one
cannot be reconstructed, the design is incomplete until it is made derivable or
explicitly retired with consumer approval.

### 3.1 `silent_flags`

For each non-structural source token, the adapter reads the glyph pairings
for its glyphs and applies the legacy silence policy over the sounds they
show. It distinguishes a glyph showing a hosted sound from one showing a
merged one and from one showing none at all, and never infers glyph
audibility from whether a
related unit has any sound. That is what makes a carrier waw silent while the
dagger on the same vowel remains sounded.

It then applies the legacy scalar grouping exactly: dagger alif, mini-waw and
mini-yaa stay separate; other combining marks rejoin their base. Named cases
that must be exact: a silent carrier waw under a dagger alif; mini-waw and
mini-yaa silah at pause; taa marbuta at pause; every legacy catch-all silence
row, each of which must resolve to a rule name.

### 3.2 `tajweed_mappings`

Rule instances supply `source` and `host`; the glyph pairings locate the
glyphs; attribution and modifier edges locate the affected sound. A versioned
table maps each public rule to the legacy names and trigger splits. Rules
legacy could not name are filtered from the compatibility view and checked by
the completeness laws instead.

The adapter reproduces every legacy word split, character string, source and
target rule list, and row order.

### 3.3 `letter_phoneme_mappings`

This adapter owns the legacy presentation grouping. It starts from source
glyph order, typed spelling edges and part-bearing attributions, then applies
the versioned legacy merge policy. Row-for-row equality, including silent
units merged left or right, lam shamsiyyah and hamza wasl elision, idgham source and
host grouping, iltiqa shortening, waqf tanween and the otiose alif, and
muqattaat expansions.

### 3.4 `character_phoneme_mappings`

| Cell field | Source |
|---|---|
| `chars` | source spelling, or the rendered glyph |
| `role` | folded glyph kind |
| `status` | `from_glyphs` presence and difference |
| `phonemes` | the sounds the glyph's pairing owns and shares |
| `phoneme_indices` | sound indices rebased word-local |
| `tag` | legacy priority over compatible rule instances |
| `secondary_tags` | the remaining compatible instances |
| `phoneme_rule_tags` | the pairing's rules, and those on its sounds' attribution and modifier edges |
| `share_group` | units on joint or shared sound relations |
| `source_letter_index` | source glyph index |
| `source_letter_indices` | spelling edges back to source glyphs |

Row order per word is part of the promise: a shipped consumer keys persisted
records on cell position.

The priority order and the role fold are compatibility policy in this adapter,
not facts in the core schema. Named fixtures cover every former frontend
synthesis: helping vowels in all qualities, the iltiqa repair, the divine
name's dagger alif, madd iwad at pause, dropped silah, taa marbuta, the iqlab
noon and small meem, and each muqattaat opening.

## 4. Completeness laws

These run over the whole corpus in all three boundary modes.

### 4.1 Envelope and indices

- Request identity, variant, and `canon_digest` are present.
- Canonical serialization of the same request is byte-stable.
- Every index is in range and points to the declared node kind.
- Node order is reading order, and one index space spans the request.
- Changing riwayah, script, variant, boundary plan or canonical data changes
  the corresponding identity field.

### 4.2 Spelling

- Every source scalar produces exactly one `Glyph`.
- Concatenating `char` in `source_index` order reproduces the requested source
  text exactly, including internal spaces and structural marks.
- Every glyph participates in at least one spelling edge.
- A glyph carrying the `Structural` edge has no word and no other spelling edge, and no glyph supplying a canonical fact carries it.
- Every `Supplies` edge names the correct fact; every `Witnesses` and
  `Decorates` edge the unit it marks.
- Many-to-many edges for long-vowel carriers, tanween and muqattaat are
  present rather than collapsed.
- A dagger over a written carrier supplies the vowel; the carrier does not.

### 4.3 Attribution

- For each unit and each part, at most one realization is stated: hosted,
  merged, or silent. A release sound is an addition rather than a realization,
  so a part may carry one of each and no more.
- A part with no realization is absent, and the converse holds: its canonical
  vowel is absent in both forms and no rule sounded it. This is the check that
  keeps absence from hiding a realization the producer dropped.
- Every sound has exactly one primary origin, one `Hosts`. `MergedInto` never
  becomes a second owner.
- Every merger is a `Hosts` and `MergedInto` pair sharing sound and rule
  instance, with distinct host and contributor units.
- Every silence names a rule instance and carries no sound.
- Every release sound is hosted on a consonant, never on a vowel, and no part
  carries two of them.
- Every attribution names exactly one unit.
- A consonant can host while the same unit's vowel is silent.

### 4.4 Rules and modifiers

- Every `source` and `host` names a valid unit, `source` is the unit the rule
  is about for every rule alike, and only a merger carries a host.
- Every applied recolour and length change has exactly one retained modifier
  edge carrying its value.
- Every classification-only rule that names a sound has a `Classifies` edge,
  and the sound it names exists.
- Every rule instance owns at least one attribution or one modifier edge. The
  only exemptions are the rules that produce no sound at all: ishmam and
  `orthographic_silence`.

### 4.5 What a glyph shows

Every law here is over `alignment(text=t, grouping="glyph")`, whose rows are
one glyph each.
- **Under `text="recited"`, no sound takes a gap pairing.** Every sound the
  performance produced is presented by some rendered glyph, because the
  recited text is by definition what recitation writes. This is the converse
  of the glyph-side law and the one that catches a sound nothing points at.
  Over the source text it does not hold and must not be asserted: a sound the
  source does not write is exactly what a gap pairing is for.
- Every sound and every rule instance a pairing names resolves, and is
  compatible with its glyph's spelling edges.
- Structural glyphs take no pairing.
- A haraka and an ordinary carrier may both present one hosted vowel sound.
- A carrier under a dagger does not present the vowel; the dagger does. What
  else the carrier presents is its own business: a waw under a dagger presents
  the consonant it is.
- A maddah may present a target although it supplies no canonical fact.
- A soundless process mark may present its rule instance without a fabricated
  sound.
- No adapter or serializer infers glyph audibility from unit audibility.

### 4.6 Alignment

For every combination of `text` and `grouping`:

- **The pairings partition the selected text's glyph array.** Every glyph
  appears in exactly one pairing, except those carrying the `Structural`
  spelling edge, which have none. The edge decides this, never `kind`, and
  `01-contract` item 18 is what makes the two agree: a tatweel and a stop sign
  both carry the edge and both take no pairing.
- **The pairings and their gap pairings cover every sound exactly once in
  `sounds`.** A sound may appear in any number of `shares` lists.
- A gap pairing has no glyphs of the selected text, exactly one owned sound,
  and an `after` naming an existing pairing or absent when the sound precedes
  every one.
- A sound takes a gap pairing exactly when no glyph of the selected text
  presents it. How it was attributed does not enter into it.
- `shares` names only sounds owned by another pairing.
- `silent` names glyphs whose silence a rule names: those showing a `Silent`
  attribution and those carrying an `orthographic_silence`, and nothing else. A
  mark that states a fact and makes no sound is not silent.
- Under `text="recited"`, `silent` is empty.
- Every block of `respelling` names at least one pairing, its pairings are of
  the matching text, and the blocks partition both alignments.
- Ownership follows the published order, and the order is total: no pairing
  set requires a tiebreak the order does not decide.

### 4.7 Recited writing

- The writer is total for every unit that has a recited representation.
- Every rendered glyph either names the source glyphs it renders or names none,
  and one that names none carries the character to draw.
- Source glyph order and values never change.
- No rendered glyph carries an empty character.

### 4.8 Converse laws

Every law above starts from what the producer emitted. These start from what
the text contains and require the producer to have explained it. Each trigger
reads only canonical facts and the boundary plan; none reads a performance
result, because a predicate that reads the answer cannot check it.

"Joined" below means the plan does not stop or sakt between the two units; a
cross-word trigger that omits it fires at every stop and is not a law but a
guaranteed failure.

| Trigger, read from the Score and the plan | Requires |
|---|---|
| a vowel canonically long | a madd rule instance |
| a vowel long in its stopped form, on a stopped word | a madd rule instance |
| a vowel long in its joined form, on a joined word | a madd rule instance |
| a silent waw or yaa after a short a, whose following letter the stop silences | `madd_leen` |
| a sakin noon or a tanween, joined to a following consonant, and not itself vowelled by an iltiqa | one of the noon rules |
| a sakin meem, joined to a following consonant | one of the meem rules |
| a geminate noon or meem | `ghunnah_mushaddadah` |
| two identical, close or homorganic consonants, the first sakin and joined to the second | an idgham rule |
| a definite article lam before a letter | `lam_shamsiyyah` or `lam_qamariyyah` |
| a consonant that sounds only when started on, word-initial and started on | `hamza_wasl_start` |
| a consonant that sounds only when started on, not started on or not word-initial | `hamza_wasl_elision` |
| two sakins meeting across a word boundary and joined | `iltiqa_shortening` or `iltiqa_kasra` |
| a qalqala letter with a silent vowel, not merged away | a qalqala rule at the right degree |
| an istilaa letter, or a raa in a colouring context | `tafkheem` or `tarqeeq` |
| a taa marbuta at a stop | `taa_marbuta_pausal` |
| a quiescent hamza the reading substitutes for a vowel | `ibdal_hamza` |
| a final short vowel at a stop, or a tanween at a stop, or a silah vowel at a stop | `pausal_sukun` |
| an imala, ishmam or tashil mark | that rule |
| an ikhfaa before an istilaa letter | a heavy ghunnah |
| a written letter the canonical layer returns its no-sound verdict for | `orthographic_silence` |

The heavy ghunnah row is the ikhfaa's own: the rule already reads the letter
that follows in order to fire, so it is the rule that sets the colour, and the
row needs no second rule.

Sakt has no row, because it is not a rule. It is a fact of the word and its
converse belongs with the boundary plan, which is where its data is short: the
sites are canonical and the set is the union of what both scripts evidence, so
the site one script cannot address is still a site.

The qalqala row's "not merged away" is not a derived fact and must not be
written as one. A gate that asks the producer whether it merged something is
checking the producer against itself. The condition is canonical: a closure is
consumed when the next consonant is identical, close or homorganic to it and
the two are joined, which is the merger table of
[07-rules](07-rules.md) over letters and the boundary plan.
Restating it here is what makes this a converse law rather than a mirror.

There is no row for madd iwad, madd badal or silah. Each is a description of a
configuration rather than an outcome, so the rows above already require the
madd rule and the silence that make it up.

## 5. Schema and negative tests

The JSON schema uses tagged unions for vowel, sound, spelling, attribution
and modifier values. Tests reject at least: a nullable quality on an
incompatible vowel kind; a sound carrying fields from two kinds;
`Structural` with a unit or word; `Supplies` without a fact; an attribution
naming two units; `Silent` carrying a sound; an attribution without a part; a
merger without its host; a pairing target out of range or of the wrong
kind; a non-structural glyph in no pairing; a rendered glyph with an empty
character; a gap row with glyphs; duplicate canonical relations; an unknown
schema version.

Round-trip tests cover canonical JSON and schema evolution. Adding a union
member requires a version change and a negative test showing older readers
fail clearly rather than misinterpret it.

## 6. Domain adequacy

Each area has joined, stopped and started fixtures. An unmodelled
relationship blocks the contract; an adapter may not repair it.

| Area | Must be represented |
|---|---|
| short and long vowels | base, haraka, carrier fan-in, shared sound, distinct pairing |
| silent carriers | otiose alif, waw, yaa and maqsura; silence sign; dagger seat against sounded dagger |
| hamza wasl | source glyph, start vowel, joined deletion, repair, article lam |
| tanween | one mark reaching vowel and noon; carrier silence when joined; waqf iwad |
| silah | written or virtual extension, joined length, pausal deletion |
| divine name | heavy or light lam, written or virtual dagger, waqf change |
| mergers | within-word and cross-word source, host, contributor, shared sound, complete and partial forms |
| noon and meem | source and host, for noon, tanween and meem |
| madd | haraka, carrier, mark, subtype, cause, boundary change |
| qalqala | closure and release, one instance, consonant reach, stop degree |
| emphasis | consonant and governed vowel reach, including raa and the divine name |
| muqattaat | compact glyph to spelled units, sounds and rules |
| waqf endings | vowel deletion with the consonant retained, taa marbuta, iwad, arid, leen, qalqala |
| ibtidaa | start boundary, wasl vowel, gemination, right context |
| marks and advice | imala, ishmam, tashil, sakt, seen and sad, iqlab, maddah, stop advice |
| the iltiqa repair | order, rule instance, sound, gap row, rendered form |
| source structure | spaces, tatweel, stop signs and verse markers round-trip exactly |

## 7. The consumer gate

Legacy parity proves the old views survive. It does not prove the contract is
sufficient for a product surface, because legacy is what the frontend had to
work around. The second gate takes a real cell shard consumer and requires
every fact its frontend synthesizes to fall out of `Mappings` with no
downstream invention.

Pinning is in three parts, because they move independently: the **schema
version**, the **repository revision** that defines it, and the **data
revision** that published the shards. A shard set is a valid oracle only at a
schema version whose cell facts exist; earlier versions omit them and readers
must tolerate their absence.

Two shape facts constrain the comparison and are known before it runs:

- a shard segment addresses a single verse, and a continuously recited span is
  a run of segments flagged as joined. The gate's unit of request is that run,
  which is a multi-verse `ref`, so this depends on request orchestration.
- the shard records junction at verse granularity and has no per-word
  junction, so a mid-verse stop is not representable in it. Fixtures that need
  one assert against the domain instead.

The comparison is against the shard's canonically serialized fact set, never
against the frontend's rendered output: the synthesized tags are what the gate
exists to remove, so using them as the oracle would be circular.

## 8. Order and CI policy

1. Build the model work in [01-contract](01-contract.md) section 9, each with
   its local laws.
2. Define the versioned schema and its negative tests.
3. Assemble a single-verse `Mappings` and pass the domain adequacy matrix.
4. Implement request orchestration for ranges, internal boundaries and
   variants.
5. Implement `tools/projection_parity.py`; verify the frozen manifest.
6. Pass each adapter in all three modes.
7. Pass the extended request matrix and the completeness suite.

A deterministic sample and all negative tests run on every pull request. The
full corpus matrix is required before the public replacement merges. CI
publishes the residue report even on success; merge requires zero unexplained
residues and a corrections file whose entries all have domain tests.

## 9. Structural constraints

`tools/structure_lint.py` runs in CI and decides two things this design cannot
leave open:

- The public surface is a **package**, not one module. The internal types it
  mirrors already exceed the per-file line limit before the envelope, the read
  API and its return records are added.
- The package must declare itself in the allowed-imports map before anything
  may reach it. It needs the render, orthography and corpus layers, and unlike
  the composition root it is itself imported, so its position in the layer
  graph is part of the implementation, not an afterthought.

Public names that nothing internal imports must be listed as public API or the
dead-export check fails.
