# Review: what these documents still get wrong

Consolidated review of 00-audit, 01-design, 02-equivalence-gate, ADR-013, and
03-canonical-vocabulary at head `366c0c9`, by three independent reviewers (two
model families), every load-bearing claim re-verified against the source at
this head and the pinned legacy revision `b3bc53a`. Verdict: not ready to
implement. Four blockers, all documentation defects; none forces abandoning
the two-projection design.

Prior review rounds read the documents against each other and fixed what that
finds (F7 withdrawn, F4 corrected, F11 added). The defect class that survived
is different: census claims that were never re-counted against the code, and
gate criteria that name artifacts which do not exist.

## Blockers

### B1. F1's premise is false and the law that fixes it is circular

00-audit §4.1 says `CLASSIFICATION_ONLY` holds 18 rules that emit no
sound-producing effect, so `AnchoredSound.rule` is `plain` for every madd
vowel. Both halves fail against the source:

- The set has 20 members, not 18 (`model/canon.py:334-368`).
- Membership is per-rule; the fact is per-occurrence. `PausalGlide` mints a
  `Rule.MADD_TABII` occurrence whose effects are `Realize` plus `MergeInto`
  (`rules/madd.py:65-80`). Materialisation turns that `Realize` into a
  `Hosts` attribution owned by the madd occurrence (`engine/run.py:190-209`),
  and `render/anchored.py` exposes it as `AnchoredSound.rule`. At least this
  madd vowel is owned by `MADD_TABII` today, not `PLAIN`.

01-design §6's closing claim -- "`CLASSIFICATION_ONLY` remains a valid
statement that an occurrence owns no sound" -- is therefore false for a live
occurrence. And 02-gate §4.4's law, "Every classification-only rule that
names a sound has a `Classifies` edge", is conditional on the thing it is
supposed to guarantee: a build that emits zero `Classifies` edges satisfies
it verbatim. F1 is the audit's first finding and the whole tajweed payload
hangs on it; as specified, the payload can ship empty and pass the gate.

Fix: make the law unconditional and per-occurrence -- every occurrence that
owns no `Hosts`/`Inserted`/`MergedInto`/`Silent` edge must carry at least one
`Classifies`, `Recolours`, or `Relengths` edge, with a closed named list of
soundless exceptions. Add a table to 01-design §6 listing all 20 members of
`CLASSIFICATION_ONLY` against the edge kind each occurrence must reach and
the sound it reaches it through, and correct §6's per-occurrence claim. The
18 count in 00-audit §4.1 must also become 20, and the set's members do not
behave alike (`TAFKHEEM`/`TARQEEQ` reach a sound through `Recolour`,
`ILTIQA_REPAIR` through `Relength`, `ISHMAM` reaches none, the madd rules
need `Classifies` except when they realize) -- the table has to say which.

### B2. The ishmam census is wrong, so D2 as documented breaks the round-trip

03-canonical-vocabulary D2 and ADR-013 §4 rest on the claim that no script
writes ishmam and `write` never reads it, so moving `Annotation` members off
the slot is harmless. False: the Uthmani inventory declares U+06EB as
`fact: ANNOTATION, cls: annotation, role: ishmam, value: ISHMAM`
(`data/riwayat/hafs/scripts/uthmani.yaml:79`), live in the corpus at 12:11,
and `orthography/write.py::_slot` serializes any slot annotation whose value
is a pen role (`write.py:183-190`). Removing `ISHMAM` from the slot without a
replacement canonical input loses the Uthmani round-trip mark and the only
input from which `rules/annotation.py` emits the soundless occurrence.

This is exactly the hazard F11 records for `IMALA` -- which the documents
did catch. D2 needs the same carve-out for ishmam that imala got: either
ishmam stays a canonical fact under whatever name D2 chooses, or `write`
learns the selection. 00-audit §4.6 and 03 D2 should both name it.

### B3. The equivalence gate is not executable as written

Three independent legs, each sufficient to stall the gate on day one:

1. **Word grouping is promised exactly and already diverges.** 02-gate §3.1
   pins `phonemes` to "exact tokens and word grouping", and §3 forecloses the
   weaker check ("Counts and merge-direction agreement are diagnostics, not
   equivalence"). But the branch deliberately allocates a cross-word merged
   sound to the other word than legacy did: `tools/parity.py` buckets these
   separately ("A sound merged across a word boundary can be credited to
   either word"), a 3000-word run shows 68 of 73 divergent words are
   ownership-only, and CI's committed floor is `regression verse 97.674`
   (`.github/workflows/gates.yml`) -- roughly 1,800 words corpus-wide. None
   of §1's four dispositions fits: tokens are identical so it is not a
   `correction`, no graph law requires it so it is not an `addition`, and
   §3.1 retires nothing. The gate needs a decision -- is legacy's allocation
   a promise or a defect? -- and, if a defect, a fifth disposition
   (`reallocation`), scoped to `Hosts`/`MergedInto` pairs that cross a join,
   pinned to the merger sites, with the token-sequence-equality invariant
   that replaces grouping equality there.
2. **The `correction` disposition names an artifact that does not exist.**
   "A reviewed corrections ledger" appears three times in 02-gate and
   nowhere else in the repository; no entry is enumerated and the exempted
   set is pinned to no ref. Meanwhile the artifact that already plays this
   role -- `docs/conformance/gate-residues.md`, 56 classified regression
   rows with a domain reason per class, ratcheted by `tools/floor.py` -- is
   never referenced. Point §1 at it, adopt its class-plus-ratchet form, and
   state that verse and continuous rows inherit the class of their word-mode
   origin.
3. **Nothing runs the gate.** §3 names `tools/projection_parity.py` as
   "planned" and §7 requires a full-matrix pass before merge, but no CI job,
   no `floor.py::HARNESS` entry, no test module, and no residue-report path
   is named. `floor.py` is a closed registry that scrapes specific stdout
   shapes; a harness it does not know is not gateable. §7 should name the
   `gates.yml` job, the `HARNESS` entry and starting floor, the fixed sample
   refs, the test file hosting §5's negative tests, and where the residue
   report lands.

### B4. The schema omits `Rule.PLAIN` while keeping every `by` mandatory

01-design says "`Rule.PLAIN` produces no occurrence; absence of a rule is
plain" (§3.5) and "Omit `Rule.PLAIN` from occurrences" (§7), while §4.2 keeps
`by: int` mandatory on every attribution edge and requires all references
valid. The engine mints a synthetic plain occurrence and uses its id as
`Hosts.by` for every unclaimed ordinary sound (`engine/run.py:141-156`) --
most sounds in the corpus. As written, the wire document has a dangling `by`
on every plain attribution. Pick one: keep a plain occurrence in the array,
make `by` optional with a stated meaning for its absence, or define an
explicit origin sentinel. Say it in §3.5 and make §4.2's referential law
match.

## Major

1. **D4's "no code change" is false.** `engine/run.py:181` classifies
   `NucleusKind.PAUSAL_LONG` as long in the plain path without consulting
   the boundary plan, and no join-path rule shortens it; `rules/boundary.py`
   is not "alone" in realizing the long vowel. The D4 decision (the fact is
   lexical, it stays in the lexicon) survives; its code claim and the
   short-when-joined semantics it asserts do not. See open question 2.
2. **Word-envelope fields are frozen, consumed, and unadapted.** The legacy
   rows carry `location`, `text`, `is_starting`, `is_stopping`
   (`b3bc53a:tajweed_mapping.py`, `char_phoneme_mapping.py`; measured key
   union of `research/legacy-baselines/`), `location` being the SDK's join
   key. 00-audit §1's table and 02-gate §3.3/§3.5 omit all four while §3.5
   claims every legacy field is adapted. All are derivable from 01-design
   §3.1 (`Word.location/.text/.starts/.junction_after`); add the row group
   to both adapters. The result-envelope counters (`ref`, `entry_count`,
   `word_count`, `phoneme_count`) were also dropped by the freeze itself and
   need an explicit disposition.
3. **The legacy surface inventory is narrower than the legacy surface.**
   `PhonemizeResult.get_mapping()` (with `AlignmentEntry`,
   `LetterMapping.display_char`), `text()`, `phonemes_str()`,
   `phonemes_list(split=...)`, `show_table()`, `save()` are exported and
   README-documented at `b3bc53a` and appear in no document. §3.1 forbids
   silent retirement, so each needs an adapter or a named `retirement`.
   `mode="simple"` is resolved below.
4. **The rule census is wrong.** The legacy enum at `b3bc53a` has 33
   members, not 30 (`tajweed_rule.py`), and the mapping table omits
   `HAMZA_WASL_SILENT`, whose branch counterpart is the renamed
   `WASL_ELISION` -- a rename the exact `source_rules`/`target_rules`
   adapter must state and test.
5. **The iqlab finding is mischaracterized twice.** Legacy did tag noon
   iqlab (`b3bc53a:tajweed_classification.py` includes `iqlab_noon` in
   `NOON_RULE_TAGS`); the synthesized mini-meem cell is tanween-only. And
   Uthmani has no small-meem glyph to bind -- U+06E2/U+06ED are IndoPak;
   Uthmani iqlab is unmarked (`corpus_sources/riwayat/hafs/scripts/
   README.md`), and the exhaustive Uthmani mark inventory contains no iqlab
   meem. 01-design §9's shipping question aims C3 at a source glyph that
   does not exist; exact legacy compatibility needs a presentation adapter
   that synthesizes the mini-meem where legacy promised it.
6. **The participant role vocabulary is inconsistent at its one decision
   point.** Under 01-design §3.5's definitions the sakin noon of an idgham
   is the `source` and the following letter the `trigger`; 02-gate §3.3
   says "the disappearing trigger". No document contains a worked role
   assignment for any family. C1 also touches behaviour the docs say it
   cannot: `engine/plan.py:156` (`assimilated_from`) reads participant
   order and `engine/laws.py:154` derives attested families from all
   participant slots, so 01-design §6's "no rule behaviour changes" must
   weaken to "no verdict changes, and the two participant-order readers are
   converted with a pinning test". Put a role table with one worked example
   per family in §3.5.
7. **`Evidences.fact` publishes members the public `Unit` cannot answer.**
   `SlotFact.SAKT` and `SlotFact.ANNOTATION` are live producers
   (`canon/draft.py`, `orthography/inventory.py:166-168`), but the §3.2
   `Unit` has no annotation field (correct under D2) and sakt lives on
   `Word.junction_after`. Narrow the public enum to
   `letter | onset | nucleus` and route annotation and sakt graphemes
   through `Attests` plus `Presents`, or give `Evidences` a payload and say
   where a sakt edge is read.
8. **`source_index` is three indices.** 01-design §3.3 defines it as the
   ordinal in the requested inscription; 02-gate §4.2 depends on that
   reading; 02-gate §3.5 equates it with legacy `source_letter_index`,
   which `model/inscription.py:39` documents as word-local. The legacy key
   is word-local. Publish both fields or state the derivation, including
   how non-base scalars count.
9. **03 §8 claims the one-question criterion is met by the section that
   declines it.** 03 §4 shows `Onset` carries two axes; 01-design §3.2
   republishes the same enum on the public `Unit` and says SDKs "may
   derive" booleans. Either retire the criterion at the projection boundary
   and say why a two-axis enum is acceptable in a consumer match, or
   publish the derived booleans as wire fields. Do not leave §8 asserting
   what §3.2 declines.
10. **`continuous` has no execution path.** `tools/parity.py` is verse-by-
    verse by design (`MODES = ("word", "verse")`), the frozen continuous
    reference is one 77,433-word request (135 MB uncompressed for
    `character_phoneme_mappings` alone), and 01-design §1.2 forbids partial
    emission. State per mode the request the harness issues, and for
    continuous either "one document" with the measured payload or a
    chunking rule with overlap at least the maximum cross-word rule reach
    and a seam-equivalence argument.
11. **The public type names break the rule that rejected `Reading`.**
    `Occurrence`, `Hosts`, `Inserted`, `MergedInto`, `Silent`, `Evidences`,
    `Attests`, `Decorates`, `Structural`, `Word` all collide with id-bearing
    model types of the same name and different field types -- the "two types
    with one name in one package" objection §1.3 uses. §3.4 renames `Sound`
    to `SoundNode` for exactly this reason and applies it nowhere else. Add
    the rule: which id-free model types are re-exported verbatim, and how
    the id-bearing ones are distinguished.

## Minor

- `TajweedEntry.to_dict` omits `source_rules`/`target_rules` when empty;
  §3.3 must say absent equals empty or the adapter fails a comparison it
  should pass. §3.3 also omits the split-extension rows and
  `EXTENSION_FALLBACK_CHARS` that §3.2 spells out for `silent_flags`.
- Manifest digests are over the uncompressed JSONL, not the committed `.gz`;
  02-gate §2 should say so. The manifest also pins no script, riwayah, or
  notation, while `MappingsRequest` carries all three.
- The phonemes baseline is committed twice (`research/legacy-baselines/`,
  `tests/snapshots/phonemes/`, byte-identical); one should reference the
  other, and 02 should state the script scope of the adapters
  (Uthmani-only; legacy has no IndoPak oracle).
- `MappingsRequest.boundaries`, `Word.junction_after`, and `Word.starts`
  store one fact three ways against §2's single-direction rule;
  `BoundaryPlan.started_on` already derives `starts`. Keep the ergonomic
  fields if wanted, but name them as the sanctioned exception.
- `Recolours.feature` and `Relengths.length` publish `engine/plan.py`
  enums; move `SoundFeature` and `Length` into `model/` as part of C2.
- `score_digest: str` is singular while C4 assembles one document from N
  per-verse Scores; define the range digest in C4.
- `CanonicalVariantSelection` is undefined; the model type is
  `VariantSelection` and the canonical ordering rule is unstated.
- `Unit.spelled` means "part of a muqattaat letter name" but reads as "is
  written" next to `Glyph` and `spellings`; publish as `letter_name`.
- F8 (`render/recite.py` occupies ADR-005's `recite` name; `phonemes` is
  already a function there) has no owner in any work list.
- Several §4 laws have no falsifiable predicate ("the correct `SlotFact`",
  "its intended typed edge", "compatible with the glyph's spelling edges");
  name the expected edge and value or move them to §6's fixture matrix.
  The iqlab law should read `Attests(family=nasalization, anchor=noon)`.
- `phonemes` has no row in 01-design §8's consumer table, and the render
  marker `Q` (`data/render/ipa.yaml`, `qalqala`) is indistinguishable from
  a segment in the flat token list -- the one SDK invention (the indexable-
  unit coordinate space) that survives the rewrite. State whether the
  alignable/marker distinction is P1's job or the reason alignment
  consumers use `Mappings`, and add a `Release`-token fixture to §6.
- `SoundNode.word` assignment is unstated for merged and inserted sounds;
  `render/recite.py:59-74` is the existing policy (host slot's word;
  inserted bucketed by anchor ignoring `Side`), which is exactly the
  boundary allocation legacy re-sliced around. State it and add a
  `Side.BEFORE`-at-word-start fixture.
- Cross-reference style is mixed (`ADR-013 §4`, `02-gate §3`,
  `section 4.1`); 00-audit's closing section cites a bare "§2.1" in a
  sentence about ADR-013 where it means its own §2.1.

## Resolved here

**`mode="simple"` is retired.** Decision by the project owner in this
review. The reduced vocabulary (`simple_mode.py`,
`resources/simple_phonemes.yaml` at `b3bc53a`) gets no successor notation
and no adapter; 00-audit's inventory should record it as consumed-by-nobody
and 02-gate §3.1 should list it under `retirement` with this document as
the named approval.

## Open questions

1. Cross-word merged-sound ownership: is legacy's allocation a promise or a
   defect? Everything about B3's first leg follows from the answer.
2. Is the engine's long-when-joined `PAUSAL_LONG` behaviour correct Hafs, or
   a live defect the parity floor absorbs? Out of scope for these documents
   but the answer decides how M1 is worded.
3. D1/D2 ordering: 02-gate §7 sequences C1-C4 and never places D1
   (`SlotOrigin` decomposition, which regenerates every digest and fixture)
   or D2 (whose output is the `Unit` shape the schema freezes). The gate's
   step 1 cannot start against the current model.
4. `MappingsRequest.ref` grammar: §2's fixtures require a range beginning
   inside a verse, but whether `ref` addresses words or only verses is
   unstated.
5. `Attests` versus `Presents(OccurrenceRef)` for the same glyph: is
   `Presents` the resolution of an `Attests` edge and required wherever one
   exists, or independent? C3's implementer needs the rule.

## What holds

The core design survives this review intact: keying on the `Slot`, the
merger as a `Hosts`/`MergedInto` pair (mirroring the live law at
`engine/laws.py:90-103`), mandatory `Aspect` on every attribution, the
`Presents`/`OrthographicOnly` contribution relation, and the four-
disposition gate that refuses a blanket additive exemption. §3.5's eleven
cell fields match the measured key union of the frozen baselines exactly.
The blockers are census and specification defects in the documents, not
holes in the model the documents design toward.
