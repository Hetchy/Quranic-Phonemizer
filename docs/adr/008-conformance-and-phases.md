# ADR-008: Conformance, gating, and phase order

Status: **accepted**, amended after the simplicity and domain reviews.
Supersedes archived ADR-002. This is the document the implementation round is
gated on. Nothing here is advisory.

## 1. Invariants

Split into two groups, because the first draft presented 26 checks of which
several were true by construction. **Group A is a runtime assertion over a
constructed object. Group B is a type or AST fact**, checked once by mypy or by
`tests/test_import_boundaries.py`, and it proves nothing about data.

### 1.1 Group A — Score (ADR-001)

| # | Invariant |
|---|---|
| S1 | **Every slot hosts a sound on at least one aspect under at least one of the three renditions** (waṣl, stopped-on, started-on). |

S1 replaces the first draft's "every `Slot` satisfies the unit-hood criterion",
which was unfalsifiable: the criterion is prose and `canon.build` constructs
slots *by* it, so no wrong implementation could fail. The three-rendition form is
the same statement with an oracle independent of the builder — a carrier wrongly
promoted to slot-hood hosts nothing in any rendition and fails. It is one pass
over three traversals.

Note what S1 does **not** prove: it cannot catch a slot that should exist and
does not. That direction is covered only by fixture 24 (phoneme parity)
and by L1 — see §6.

### 1.2 Group A — Inscription (ADR-003)

| # | Invariant |
|---|---|
| I1 | Every scalar of every verse resolves to exactly one `Spelling`. An unlisted scalar raises. |
| I2 | `Evidences.fact` is in the canonical vocabulary and its value is legal for that fact. |
| I3 | Exactly one `Supply` per `(SlotId, SlotFact)` **per build**. The loader check is over `ledger.yaml` only. |
| I4 | Every `Assert` has a matching `Supply` and agrees with it. |
| I5 | Every `Attests.anchor` resolves to a slot in the Score. |
| I6 | A polysemous scalar never determines a fact by itself; the Ledger resolves it. Six are known (ADR-003 §6.6). |
| I7 | **Every slot is the target of at least one `Spelling`** — downward totality, the counterpart to L3 (ADR-003 §4.2). |
| I8 | `Decorates` names a slot; the field is not optional. |

### 1.3 Group A — Performance (ADR-002)

| # | Invariant |
|---|---|
| P1 | Every `Sound` appears in exactly one `Hosts` or `Inserted`. |
| P2 | Every `Attribution.by` resolves to an `Occurrence`. |
| P3 | For every slot and every aspect with canonical content there is an attribution or an explicit `Silent` edge. `ONSET` always has content; `NUCLEUS` has content unless `nucleus is Silent`. |
| P4 | Every `MergedInto` edge's sound has a `Hosts` edge with the same `by`. |

The first draft's P4 and P5 are gone: the `Attribution` union makes them type
facts (ADR-002 §1).

### 1.4 Group A — Execution (ADR-004)

| # | Invariant |
|---|---|
| E1 | At most one effect per conflict key per phase (ADR-004 §4). |
| E2 | No cross-word effect crosses a `STOP` or `SAKT` junction. |
| E3 | A `sakt_after` junction is `SAKT` or `STOP`, never `JOIN`. |
| E4 | Every occurrence either produced a sound or is declared classification-only. |
| E5 | An unknown `stop_ref` raises. |

E4 is weak by construction — the rule author declares its own
classification-only status — and is retained only as a consistency check between
the `Rule` member's declaration and what it emits.

### 1.5 Group A — Agreement (ADR-003 §4.1)

| # | Invariant |
|---|---|
| A1 | If a script attests family `F` at slot `s`, the engine produces an occurrence of some rule in `F` with `s` among its participants, under the all-join plan. One-directional. |
| A2 | An `Assert` disagreeing with its `Supply` raises, naming supplier, witness and `SlotId`. |

### 1.6 Group B — type and AST facts

`Nucleus` has no `Leen`; `ScoreWord` has no `advice`; slot ordinals are the
tuple index; no `Attribution` or `Occurrence` holds a `GraphemeId` or a
`Script`; `rules` does not import `orthography`; `render` does not import
`rules`, `canon`, `engine` or `orthography`; no phoneme string outside
`render/`; no raw scalar comparison outside the adapters.

## 2. Fixture checklist

Each fixture is a named test with a stated falsifier. "Both scripts" means the
fixture runs twice and the phoneme output must be byte-identical.

**Boundary and layer**
1. Round trip: `write(read(verse), SOURCE_FORM, COMPACT) == verse`, 6,236
   verses × 2 scripts (77,433 words each). Includes the 4,575 words with an
   internal space and 6,404 with a tatweel.
2. `Spelling` totality **both ways**: every grapheme classified (I1) and every
   slot reached (I7), both scripts.
27. **Downward totality at the hard case**: the 8,893 tanwīn words in both
   scripts, asserting that the tanwīn scalar reaches *both* the base slot and
   the nūn slot. Measured, the first draft left **5,831 Uthmani / 5,795 IndoPak**
   slots unreached — all tanwīn nūns — so this fixture is the one that would
   have caught it.
28. **Madd highlighting**: the 5,044 maddah scalars project `role: madd`,
   `status: present`, with the sound of the slot they decorate; and the 93
   `هُدًى` / `أَذًى` maqsura seats project `madd` / `replaced`. Fails on any
   return to an optional slot link (ADR-003 §4.0).
3. Import-boundary AST test (§1.6).

**Score construction**
4. L1 equality harness (§3). The gate.
5. Ledger loader rejection cases: duplicate supply, out-of-vocabulary value,
   orphan assert, non-`SlotId` key, mismatched `skeleton`, output-vocabulary
   value.
6. Derivation classes, each with positive, neighbouring-negative and
   both-script cases, **each a named module under `canon/derive/`**: article
   `ٱل` (11,995), waṣl skeletons (526), **waṣl helping vowel — 181 IndoPak
   evidence sites, 118 fatha / 44 kasra / 19 damma**, otiose wāw-alif (3,640),
   silent-letter lexical classes (~300 over 5 classes), ṣilah pronoun rule
   (2,213 positive) with its exemption lexicon (~169 skeletons), Allah lexeme
   (2,704 words, 178 correct non-matches), **the two-slot tanwīn** (8,893
   Uthmani / 8,840 IndoPak words) and its **split-across-a-boundary class**
   (54 IndoPak `ࣙ` sites plus 18:1:11 the other way).

**Attribution**
7. Joint ownership: `عَلَىٰ` / `عَلٰي` — two graphemes in one script, one in the
   other, one `Hosts` edge either way.
8. Cross-word merger: 2:5:4→2:5:5 `مِّن رَّبِّهِمْ`, both scripts,
   `MergedInto` + `Hosts` sharing a `SoundId` and an `OccurrenceId`.
9. Nucleus-scoped silence at waqf: `كِتَٰبٌ` — four slots `[k i][t aː][b u]
   [n Silent]`; at waqf the bāʾ's onset hosts, its nucleus is `Silent`, and the
   tanwīn nūn slot is `Silent` on both aspects. The case R1 exists for, now with
   A1's extra slot.
10. Insertion with an anchor: the 3:1 iltiqāʾ fatha.
11. Carrier silence, tanwīn ʿiwaḍ, final wāw/yāʾ role change.
12. `هُوَ` → *huu* at waqf: the wāw is a slot and takes `MergedInto` (R5).
13. **`Onset.SILAH` at 27:36:8**: joined `ʔ aː t aː n i j a`, stopped
    `ʔ aː t aː n` — both aspects silenced, not just the nucleus. **Must also
    assert `Nucleus.Long(I)` at a sample of the other 38 U+06E7 sites**
    (`إِبْرَٰهِـۧمَ`), or it tests a scalar rather than a fact (ADR-003 §6.6).
14. **41:44:9**: two hamza slots, output `ʔ a ʔ a ʕ ʒ a m i jj`.

**Attestation oracles** (ADR-003 §4.1)
15. 10 muqaṭṭaʿāt attestation sites.
16. 546 IndoPak iqlāb marks.
17. **54 IndoPak U+08D9 sites**, of which **34 resolve within the verse and 20
    need the one-word right context** (ADR-003 §6.5) — the fixture that
    distinguishes verse scope from sufficient scope — under A1 these are `Evidences`, not
    attestations: `ࣙ` evidences `LETTER = NOON` + `NUCLEUS = Short(I)` on the
    tanwīn nūn slot of the *previous* word. They are the fixture for
    verse-scoped `read`, and the reason the 8,893/8,840 tanwīn counts reconcile.
    The 3:1 fatha remains the only slot-less insertion oracle.
18. Attesting shadda under the **Performance predicate** (ADR-003 §4.3):
    **11,488 Uthmani / 13,538 IndoPak** sites, of which 3,722 / 5,761 are the
    word-initial subset the positional rule caught. Must include the
    word-internal families — lām shamsiyyah, article-before-geminated-lām,
    form-VIII, and 5:28:2 `بَسَطْتَ`/`بَسَطْتَّ` — and must **not** fire at the
    ~93 length-carrier look-alikes (`دَآبَّةٍ`, `ٱلضَّآلِّينَ`). Evaluated under
    the all-join plan, so it is a phase-3 fixture, not phase 1; the per-family
    split is measured there.
18b. **6 final-mīm helper-vowel sites** (ADR-003 §6.7) as
    `Attests(INSERTION, anchor=mīm slot)`.

**Rules and defects**
19. Evidence §4.1: 27:1 `طسٓ` → `تِلْكَ` gives `ŋ` joined, `n` stopped, with all
    regression guards unmoved (36:1, 68:1, 26:1, 28:1, 42:2, 50:1, 38:1, 7:1,
    19:1).
20. Evidence §4.2: 3:1 → 3:2 produces the fatha and the heavy lām joined;
    2:1 unchanged; 29–32:1 unaffected.
21. Phase conflict: a deliberately duplicated effect raises with both occurrence
    tags.
22. **Lexical khilāf**: all 4 seen/ṣād sites, each option changing emphasis and
    the rāʾ look-back downstream.
22b. **Realization khilāf**: `IQLAB_NASAL` at 503 sites (304 tanwīn + bāʾ, 199
    nūn sākinah + bāʾ) and `IKHFAA_SHAFAWI_NASAL` at 483, each option changing
    `Nasal.place` and nothing else — same `Occurrence`, same participants, same
    `emphatic` (always `False`, bāʾ not being an istiʿlāʾ letter). Asserts that
    the choice is invisible to `render/`, which holds no branch, and to the
    attestation law, which names a `RuleFamily`. The `ASSIMILATED` default must
    reproduce fixture 24 byte for byte.
23. **Qalqala degree**: `QALQALA_SUGHRA` / `KUBRA` / `AKBAR` tagged separately,
    against the frozen counts (3,413 sughrā, 424 kubrā).

**Output**
24. Phoneme parity against `tests/snapshots/phonemes/` in all three boundary
    modes, both scripts. **Includes the 10,667 nasalized-consonant tokens** —
    `ñ` 4,098, `m̃` 3,254, `w̃` 2,192, `j̃` 1,123 — which the render map must
    reach through `Consonant.nasal` (ADR-002 §6.1).
25. Information coverage against `research/legacy-baselines/` — a coverage
    check, not a correctness oracle (evidence §8). `role: madd` (53,155) and
    `role: tanween` (8,893) require `Grapheme.cls` (ADR-007 §6).
26. `write` renderability gate (ADR-005 §4).

## 3. The L1 harness (R10)

```
for each verse in the riwayah:
    a = canon.build(uthmani.read(text_u, verse), ledger, lexicon, selection)
    b = canon.build(indopak.read(text_i, verse), ledger, lexicon, selection)
    compare a.slots with b.slots, field by field
```

- Comparison is **full `Slot` tuple equality**: `letter`, `onset`, `nucleus`,
  `spelled`. `origin` is gone (ADR-001 §3.2); comparing it would have
  manufactured thousands of residue rows at the 2,714 medial-`ٱ` words.
- Residue rows are
  `(verse, ordinal, field, uthmani_value, indopak_value, derivation_class)`.
- `derivation_class` must be a module under `canon/derive/`. `UNCLASSIFIED` is
  the failure value.
- The report must be **empty**. A nonzero residue is a failed equality proof,
  not "mostly named".
- The harness emits `Score.digest` per riwayah.

### 3.1 What the harness must report besides the residue

Because `canon.build` is shared and script-independent (ADR-001 §2), **every
fact it supplies is identical across both builds by construction**. L1 therefore
tests only facts that come from adapter evidence, and any residue row can be
driven to zero by moving that fact out of adapter evidence — into a derivation
or a Ledger `Supply` — after which the two builds agree trivially.

Clauses 1–3 of §4 and the ~50-supply budget guard the derivation and Supply
routes. The remaining route is to reclassify a disagreeing grapheme as
`Decorates`: I1 forces every scalar to be *classified*, and `Decorates` is a
legal classification that files no `Assert` and produces no residue row.

The harness therefore also reports, per riwayah:

- **the provenance split** — how many canonical facts came from adapter
  evidence, from a derivation, and from the Ledger;
- **the `Decorates` count for scalars that the *other* script's inventory maps
  to a fact class** — the signature of a fact being discarded rather than
  reconciled.

**First execution (phase-1 spike), recorded as the baseline:**

| | Uthmani | IndoPak |
|---|---:|---:|
| slots | 286,943 | 286,900 |
| scalars | 638,424 | 645,069 |
| non-supplying (`Decorates`) | 13,452 | 14,934 |
| `Structural` | 9,152 | 5,674 |

The two cross-script asymmetries it surfaced were **IndoPak `ي` ×1,972** (the
rasm yāʾ standing in for the alef maqsura, where Uthmani maps `ي` to a fact) and
**Uthmani `۟` ×3,988 against IndoPak ×26** (§6's otiose-wāw class). Both are
explainable and neither is a discarded fact. **The guard produces a small
readable signal rather than noise** — which is what open question 2 doubted, and
it no longer does.

A residue of zero reached by a rising `Decorates` count is still not a proof of
script-independence. The threshold remains unset; §4.2 states the budget.

## 4. The reversal trigger (R9)

If derivation fails, the fallback is spine C's **curated Score** — a versioned
authored artifact with the scripts as witnesses. That is a promotion of the same
canonical layer, not a redesign.

**Derivation is accepted only when** the L1 mismatch set is empty and every
derivation class has code, fixtures and a bounded fact schema.

**The fallback fires if** any of:

1. any residue row is `UNCLASSIFIED`;
2. a class needs `script_id` to choose a canonical fact;
3. a supposed derivation is a per-location output patch (ADR-006 §4);
4. any Ledger entry contradicts a script's **explicit evidence** — fires
   immediately.

More than ~50 uncited one-off `Supply` entries is a **warning**, not a fire.

### 4.2 Declared budgets — gate numbers, not guidance

The Ledger budget above governs *per-location* entries and says nothing about
the derivation side, which is where the real authoring cost sits. Both are now
gate numbers, declared before implementation and held to:

| Budget | Number | Source |
|---|---:|---|
| waṣl lexical entries | **≤ 30** | ADR-003 §6.1. Was 575 skeletons; the lexicon collapsed to 3 morphological rules + ~3 particle entries reaching 98.19%, with the residue in six named closed classes. A rise past 30 means a rule is missing, not that the corpus is irregular |
| ṣilah exemption skeletons | **≤ 169** | ADR-003 §6.4, measured |
| any *other* derivation lexicon | **≤ 100**, or it needs its own ADR row | ceiling, not a measurement |
| uncited one-off `Supply` entries | ~50 | §4 |
| `Decorates` scalars, per script | **≤ 15,000** | baseline 13,452 / 14,934 (§3.1); a rise without a named class is the gaming signal |

Exceeding a budget is not an automatic reversal — it is a required review of the
class inventory before the gate can be called green.

### 4.1 "Explicit evidence" is defined

> A script gives explicit evidence for a fact when its declared inventory
> contains a grapheme class evidencing that fact class **and an instance is
> present at the site**. A value produced by a derivation in the absence of any
> such grapheme is a default, not evidence.

Without this, the seven alifs fire clause 4 on day one: IndoPak writes `اَنَا`
and the ordinary length derivation yields `Long(A)`, which the Ledger's
`PausalLong(A)` overrides at all 66 sites. IndoPak's inventory contains no
grapheme distinguishing pausal-only length, so it gives no evidence and the
override is legitimate. Had IndoPak written a length grapheme and the Ledger
said `Silent`, that is a genuine contradiction and should fire.

## 5. Phase order

Each phase states what it proves and what falsifies it. A phase does not start
until the previous one's gate is green.

### Phase 0 — model and boundaries
`model/` (four files), the import-boundary test, the Ledger loader with its
rejection cases. **Proves** the vocabulary is closed and the dependency direction
holds. **Falsified by** any type needing a field no ADR names, or any referenced
name still undefined (ADR-007 §4.5).

A1 is ruled (ADR-004 §8): `Nucleus` has no `Nunated` and the tanwīn nūn is its
own slot. `Nucleus` is a phase-0 artifact, so this is settled before any code
depends on it.

### Phase 1 — the two adapters and the Score. *The gate.*
Both `read` implementations, the scalar inventories, `canon.build`, the
`canon/derive/` registry, and the L1 harness. **Proves** script-independence, or
does not. **Falsified by** a nonempty residue after the committed closure, or by
a residue driven to zero with a rising `Decorates` count (§3.1).

Measure here, not later, and record in this ADR:

- occurrence count per traversal (estimated ~3×10⁵) and peak graph size;
- validation time over the full corpus × 3 boundary modes;
- **how thin the adapters actually are** — Python lines in
  `riwayat/*/scripts/` versus
  declarative lines in the inventories. ADR-001 §2 asserts thinness; this is
  where it becomes a fact or does not.

### Phase 2 — `write` and recited writing
`write` for both scripts, the verse round-trip, the ADR-005 §4 renderability
gate. **Proves** `Spelling` totality, adapter correctness, and that no fourth
layer is needed. **Falsified by** any recited form requiring an Arabic sequence
no `Slot` or `SoundSpec` can spell.

### Phase 3 — one vertical slice: nūn and tanwīn
`engine/`, the `MERGE` phase, and the nūn/tanwīn family end to end on both
scripts. **Proves** the effect model, E1, and the attestation law against the
546 iqlāb marks. **Falsified by** a rule that cannot express its outcome in the
`Effect` union, or by A1 failing on a script that is right.

This is the slice ADR-004 §8 is about. Under A1's ruling the nūn family has one
shape, so nūn sākinah and tanwīn are the *same* rule on the same trigger; if
that is wrong, it fails here at ~4,671 sites.

### Phase 4 — boundaries and spelling expansion
`BOUNDARY` phase, the `BoundaryPlan`, muqaṭṭaʿāt, and both evidence §4 defects
fixed **as rules, not exceptions**. **Proves** the boundary object and that
`allow_forward_rules` has no home. **Falsified by** either defect requiring a
Ledger entry that fails ADR-006 §4.

### Phase 5 — remaining families
`idgham`, `meem`, `shamsiyyah`, `wasl`, `madd` (incl. leen), `emphasis`,
`qalqala`. **Proves** the un-collapsing of `idgham.py:28` into named rules.
**Falsified by** two families needing different shapes.

### Phase 6 — render and projections
`render/`, phoneme parity in three modes on both scripts, the legacy-baseline
coverage check. **Proves** the model retains enough to reconstruct the frozen
views. **Falsified by** a baseline column that cannot be reconstructed from
stored relations.

## 6. What each gate does *not* prove

- Phoneme parity does not prove correctness. Both evidence §4 defects are baked
  into every frozen view; parity is preserved *until* phase 4 deliberately
  breaks it, and the diff must then be exactly those two defects.
- The legacy baselines are an information-coverage reference only (evidence §8).
- L1 proves the two Hafs witnesses agree. It says nothing about a third witness
  or about Warsh. And per §3.1 it says nothing about facts `canon.build`
  supplies.
- Group B invariants (§1.6) prove nothing about data.
- **S1 is one-directional.** It catches a carrier wrongly promoted to slot-hood,
  because such a slot hosts nothing in any rendition. It cannot catch the
  opposite error — a slot that *should* exist and does not. That direction is
  covered only by fixture 24 (phoneme parity) and by L1, both of which are
  indirect. A1 is the worked example: `Nucleus.Nunated` hid a missing slot for
  the whole first draft, and S1 would not have found it.

## 7. Open questions

Not resolved by assertion anywhere in this set. Ordered by what would hurt most.

1. **L1 residue.** Unproved. The 94.4% slot-count figure is not an L1
   measurement. Phase 1's gate is the whole question.
2. **Whether L1 can be satisfied by relocating facts rather than deriving
   them.** *Downgraded: the guard now runs; the threshold is still unset.* First
   execution is recorded in §3.1 and produced a small readable signal — two
   named, explainable cross-script asymmetries rather than noise. §4.2 now
   states budgets. What remains open is the **threshold**: "non-increasing
   across runs" is a shape, not a bound, and no run has yet tested whether a
   legitimate derivation and a discarded fact can be told apart when they are
   the same size.
2b. ~~**Whether the 575 waṣl skeletons are independently justifiable as Arabic
   morphology.**~~ **Closed, favourably.** The lexicon was an artifact of asking
   the wrong script: a bare IndoPak initial alef *is* a hamzat al-waṣl (13,274
   bare-waṣl against 16 bare-qaṭʿ, all muqaṭṭaʿāt plus 3:158:5), so `Onset.WASL`
   is a declared script convention in both scripts and L1 tests two derivations
   against each other rather than one against a table learned from the other.
   What remains is three morphological rules plus ~3 particle entries, 98.19% as
   a total decision procedure with 2 misses, both already Ledger sites
   (ADR-003 §6.1).

   **Keep the caveat, because it is the reusable part.** Those rules were still
   validated against Uthmani's `ٱ` — the same ground truth the lexicon came
   from. What changed is not the evidence but the *checkability of the
   artifact*: a 575-row skeleton list can only be confirmed by the corpus that
   produced it; three rules can be checked against a grammar by someone who has
   never seen the corpus, and all three are in every tajwīd primer. **Any future
   derivation class is held to that test**, not to its residue count.
3. **`Onset` conflates two axes, and Warsh is where that bill comes due.**
   `Onset` is `PLAIN | GEMINATE | WASL | SILAH | TASHIL`: `GEMINATE` is a
   manner, `WASL` and `SILAH` are boundary-conditional *presence*, `TASHIL` is a
   manner again. A flat mutually-exclusive enum works only because no geminate
   waṣl-hamza and no geminate ṣilah-yāʾ occurs — **a fact about Hafs, not a
   structural guarantee.** The consequence is specifically for Warsh: naql
   moves a hamza's vowel onto a preceding sākin consonant, and taqlīl, ibdāl and
   Warsh's own ṣilah behaviour all touch onset manner and onset presence
   together. The first Warsh onset that is simultaneously geminate and
   boundary-conditional forces `Onset` to split into two fields — a manner and a
   presence — which changes `Slot`, the L1 comparator, and `Aspect`'s closure
   argument (two members because a `Slot` has two aspects). Deciding this before
   Warsh research is premature; deciding it *during* Warsh implementation is
   late. Flag it at the start of any Warsh phase.
4. **Ṣilah derivation closure.** ADR-003 §6.4 measures the shape (one lexeme
   rule + ~169 exemption skeletons) but the exemption lexicon is not authored,
   and the 37 IndoPak-only yāʾ-side sites are not classified — at least three
   are not ṣilah at all.
5. **Advice-driven plans are script-relative** (ADR-003 §5). The shipped surface
   is `phonemize(ref, stop_signs=[...])`, so byte-identity across scripts holds
   per *boundary plan* and not per call. The domain review notes that R3's
   reasoning is the inverse of L2's, and is itself least confident here. The
   distinguishing test — no rule reads advice — is stated; whether the entry
   point should require a `Script`, or a riwayah-level advice table should be
   curated, touches the public surface and is out of scope.
6. **`write` totality.** ADR-005 §4's gate is unrun; "no fourth layer" is a
   hypothesis.
7. **Occurrence volume and graph cost.** Estimated ~3×10⁵ per traversal,
   unmeasured. `PLAIN` will dominate and its occurrences are internable to one
   object per traversal, so this is a measurement, **not** a reason to weaken
   "no sound without a named occurrence" — the invariant most worth keeping.
8. **Word join/split within a riwayah.** Verse-scoping reduces the break to the
   `ScoreWord` container (ADR-001 §5.2). The premise that the two witnesses
   agree is constructed, not observed.
9. **`يسٓ` / `نٓ` wajh.** Two wajhs reported for Hafs via Shāṭibiyyah;
   **unverified**. Also unverified: whether 18:1 and 69:28 sakt are obligatory
   or permissible, and the 30:54 `ضُؔعْفٍ` khilāf.
10. **Whether tashīl and ishmām should be audible.** Recorded and projectable
    but not rendered (ADR-002 §6.2). Needs a notation with symbols for them.
11. **The full variant surface — a future ADR-009.** ADR-006 §5 records the
    target shape (~40 khilāf options, the `MoshafAttributes` reference) and the
    two categories this design has already excluded: **madd lengths are
    durations** and nothing here stores duration; **`recitation_speed` and
    `takbeer` are performance settings** and are out of scope. The open part is
    the **third variant shape — rule *selection*** (iẓhār instead of idghām),
    which changes which `Occurrence` fires rather than which `Sound` it emits,
    and which §2 and §3 of ADR-006 do not cover. The requirement is only that
    `VariantSelection` extends to it without a redesign. Do not open ADR-009
    before the public projection API is scoped; they share a surface.

Closed since the first draft: **A1** (ruled — ADR-004 §8); `Colouring`
aspect-scoping (the field is deleted); and IndoPak's four extra `ࣝ` sites —
three of the four sit where Uthmani writes an ordinary waqf sign (7:184:2 `ۗ`,
12:29:4 `ۚ`, 28:23:24 `ۖ`), which closes them as advice pending a domain
reference for 7:23:4 alone.

Note that §6's S1 caveat is a property of the gate rather than an open question:
it is not going to be resolved, only compensated for by fixtures.
