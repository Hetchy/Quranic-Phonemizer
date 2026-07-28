# Review — simplicity

Lens: is this too much machinery for the problem? Reviewed `docs/adr/001–008`
(1,722 lines), `research/spines/*`, `research/evidence/internal-model-redesign.md`,
`docs/domain-facts.md`, the two corpora, the six frozen views under
`research/legacy-baselines/`, and the 2,033-line implementation it replaces.

Numbers marked *(measured)* are mine, taken against the two `quran.json` files
and the frozen baselines during this review.

---

## 0. Verdict up front

The spine is right-sized. The margins are not.

Every reviewer before me authored a competing design; every finding in
`convergence-a.md` and `convergence-c.md` is *add this*. Grep both for
"simplify", "premature", "YAGNI", "over-engineered": zero hits. Seven of the
ten binding rulings add a type, a field, an enum or a law. R5 and R7 are the
only two that delete anything, and R7 deletes members that were unreachable
rather than merely unused. That is a one-directional pressure, and it shows in
the result: nothing in this ADR set is *wrong* because it is too big, but about
a dozen named things are present because nobody was asked whether they should
be.

Honest size estimate for the implemented design: **~3,600–3,800 runtime lines
across 44 modules**, against 2,033 across 25 today — roughly 1.8×, buying a
second script, full attribution, named rules, an occurrence graph, and the
information behind six frozen projections. That is not architecture
astronautics. My deletions total roughly 350–500 lines and seven named
concepts — around 12% — and I do not believe a *much* smaller design can pass
ADR-008 (§4).

The set also has four genuine holes that the simplicity pass surfaced as a
by-product: F1, F7, F9 and F10 are correctness findings, not taste.

---

## 1. The deletion test

Ranked by what would actually hurt.

### F1. `SlotOrigin` is in the L1 comparator but has no script-independent definition, and `LEXICAL` has no valid instance

**Claim.** `Slot.origin` cannot be computed from one `Reading`, and one of its
three members has no example that survives the rest of the ADR set.

**Evidence.** ADR-001 §3.2 defines `WRITTEN` as "some script writes a base
letter for it". *Some script* quantifies over the riwayah's whole script set,
but `canon.build` receives a single `Reading` (ADR-003 §1) and cannot evaluate
that quantifier. So `origin` is either script-relative — in which case
including it in L1 equality (ADR-003 §3, ADR-008 §3, "equality is over the full
`Slot` tuple … `origin`") manufactures residue at the gate — or it means
something the builder cannot see.

Both stated `LEXICAL` examples are reclassified elsewhere in the same set as
field values on slots that *both* scripts write:

- "the hamzat al-waṣl IndoPak omits" — IndoPak omits the *mark*, not the
  letter. *(measured)* 1:1:2 is `ٱللَّهِ` / `اللّٰهِ`; 2:255:1 is `ٱللَّهُ` /
  `اَللّٰهُ`. The alef is present in both. What differs is `onset = WASL`, a
  field on an existing slot.
- "the Allah name's long ā" — ADR-002 §4.1 says explicitly this is "a canonical
  `Nucleus.Long(A)` on the lām slot", i.e. a nucleus value, not a slot.
  *(measured)* U+0670 occurs 9,726× in Uthmani and 12,596× in IndoPak; the
  Allah dagger is one of the deltas.

No canonical slot in the set is created by the lexicon. Insertions are
explicitly *not* slots (ADR-002 §4.1: "Only the iltiqāʾ repairs are genuinely
slot-less"), and the waṣl helping vowel "fills the waṣl slot's own nucleus".

**What should change.** Delete `LEXICAL`. `SlotOrigin` becomes `WRITTEN |
SPELLED`, or simply `spelled: bool` — `SPELLED` is the only member with a named
reader anywhere (ADR-005 §1's `spelling` toggle). Then either give `origin` a
script-independent definition or drop it from the L1 comparator. As written,
the gate compares a field neither adapter can compute the same way twice.

### F2. `ScoreRevision`, `migrations/`, S5 and the revision loader clause solve a problem that does not exist

**Claim.** The largest single deletion available. Zero users today, zero users
on the stated roadmap.

**Evidence.** ADR-001 §5.1 requires a monotonic revision plus a content hash on
every `Score`, a published `data/riwayat/<r>/migrations/<from>-<to>.yaml`
mapping each retired `SlotId` to a successor or `RETIRED`, a load error if a
bump ships without one, and a gate that "re-runs the L1 harness and every
fixture, and rewrites Ledger keys through the migration before validation".
Invariant S5 and one Ledger loader rejection case exist to support it.

Every artifact that holds a `SlotId` across a rebuild — `ledger.yaml`,
`variants.yaml`, the fixtures — is a file in *this* repository, edited by the
same person in the same commit as the Score change that invalidated it. Git is
the migration tool. The public surface is a list of phoneme strings (review
brief); no external consumer holds a `SlotId` at all. Zero riwayat have
shipped, so there is no revision 1 to migrate from.

Provenance is worth naming: this is a graft from spine C (settled-design §4),
the spine that lost the derived-versus-curated fork, and ADR-008 §4 justifies
it prospectively — "ADR-001 §5.1's revision and migration machinery is what
makes it possible" — for a fallback that may never fire.

There is also a structural cause worth stating rather than paying for.
Migrations are needed *because* `SlotId = (Location, ordinal)` is a positional
key that shifts when a slot is inserted. The design buys a versioning subsystem
to protect a fragile key. Hand-authored `slot: "2:245:14#5"` is also
unreviewable by a human reading `ledger.yaml`.

**What should change.** Delete `ScoreRevision` from `Score` and
`model/address.py`, delete `data/riwayat/<r>/migrations/`, delete ADR-001 §5.1,
invariant S5, and the stale-revision loader case. Keep a Score content hash if
you want cache invalidation — that is one function and no schema. Reinstate
§5.1 verbatim the day a second consumer holds `SlotId`s across a rebuild, or
the day the curated fallback fires. Consider separately whether a Ledger key
with a stable component (location + canonical letter + nth-of-that-letter)
removes the motivation entirely.

### F3. `Attribution` is a tag enum plus three tied `Optional`s where the design's own convention says use a union

**Claim.** The one place the design breaks its own convention 2, and it pays
for it with two runtime invariants.

**Evidence.** ADR-007 convention 2: "Closed structural unions are a
`TypeAlias` over frozen dataclasses, consumed with `match`." Convention 3:
"Prefer a union member over `Optional` … `None` appears only where an ADR
states an invariant tying it to another field (`Attribution.sound`)." The
convention names its own single exception, and the exception is this type. The
set applies the union treatment to `Nucleus`, `Sound`, `Spelling`, `Effect` and
`LedgerEntry` — five unions — and not to `Attribution`.

The cost is the `Attach` enum, three `| None` fields, and invariants P4
(`slots == () ⟹ kind is HOSTS and anchor is not None`), P5 (`kind is SILENT ⟺
sound is None ⟺ reason is not None`) and half of P6. Under a union all three
are type facts checked by mypy at zero runtime cost over ~3×10⁵ edges per
traversal.

**What should change.** `Attribution = Hosts | Inserted | MergedInto | Silent`,
where `Inserted` carries `anchor` and no `slots`. Delete `Attach`, the three
`Optional`s, P4 and P5. Nothing in ADR-002 §3's arity semantics changes —
`Inserted` is the `len(slots) == 0` row of the table, named.

### F4. `SilenceReason` is fully derivable from `Attribution.by`

**Claim.** A three-member enum, a field, an effect argument, half an invariant
and a governance rule, all recoverable from a field the design guarantees is
never null.

**Evidence.** ADR-002 §5 invariant: "Every `Attribution.by` is non-null …
No sound exists except as the output of a named occurrence." `Occurrence.rule`
is a closed 33-member enum containing `WASL_ELISION` and `WAQF_ENDING`.
`WASL_ELISION → WASL_ELISION`, `WAQF_ENDING → WAQF_DROP`, and where waqf
drops a ṣilah the slot's own `Nucleus` is `Silah`. Total, both directions.

Spine A's author made exactly this argument and conceded on it for insertions
(`convergence-a.md` §1.3): "I gave insertions a second closed enum naming their
reason; B derives the reason from `Attribution.by` — the occurrence's `Rule`
already names it. One enum fewer, no information lost." The identical argument
applies to silences and was never put.

**What should change.** Delete `SilenceReason`, `Attribution.reason`,
`Silence.reason` on the effect, the `reason` half of P5, and ADR-002 §4.2's
"adding a member requires a domain citation" governance. R7's substantive
finding survives untouched — it is an argument about which *rules* can silence
a *slot*, and it is what makes `SEAT`/`OTIOSE`/`ORTHOGRAPHIC_ZERO` unreachable
regardless of where the reason is stored.

### F5. `Colouring` is a `frozenset` on ~330,000 slots carrying information present at two words

**Claim.** An enum, a set-valued field on every `Slot`, a comparator column and
an open question, for two sites.

**Evidence.** *(measured, both corpora)*

| Mark | Uthmani | IndoPak |
|---|---:|---:|
| U+06EC tashīl | 1 occurrence, 1 word | 0 |
| U+06EB ishmām | 1 occurrence, 1 word | 0 |
| U+06EA imāla | 1 occurrence, 1 word | 0 |

ADR-001 §3.3 already routes imāla out of `Colouring` and into `Quality`, on the
argument that "it is a distinct vowel, not a modification of one". The same
argument routes ishmām — a realization of a damma — into `Quality` or a
`Nucleus` variant, and tashīl — a softened hamza onset — into `Onset`, which is
already a closed set of mutually exclusive onset modifications
(`PLAIN | GEMINATE | WASL`). No site carries two colourings and none ever can
under a two-member enum, so `frozenset` is speculative generality; the ADR
concedes as much ("if a third arrives that spans aspects, `colour` becomes
aspect-scoped").

**What should change.** `Onset` gains `TASHIL`; `Quality` or `Nucleus` absorbs
ishmām. Delete `Colouring`, `Slot.colour`, its column in the L1 comparator, and
open question 8, which exists only to worry about a field that need not exist.

### F6. `Participants` reconstructs nothing in the frozen coverage set

**Claim.** A six-variant tagged union whose only surviving content is one fact
that belongs in `Rule` instead.

**Evidence.** I read all six frozen views *(measured)*. The richest,
`character_phoneme_mappings`, is per-cell
`{chars, role, status, phonemes, phoneme_indices, tag, share_group,
source_letter_index(es), phoneme_rule_tags, secondary_tags}` — every field maps
onto `Spelling`, `Attribution.kind`, `Attribution.slots` (`share_group` *is*
arity), `Occurrence.rule` and `SoundId`. `tajweed_mappings` is
`{char, source_rules, target_rules}` — a rule tag plus a role, both on the edge
already. Neither carries a trigger letter, an emphasis cause, or madd carriers.

Of ADR-002 §5's five named variants, three are recoverable from
`Attribution.slots` plus the Score (idghām host, madd carrier slots, the
nūn/mīm trigger, which is the next slot). Two facts are genuinely new: qalqala
degree and the emphasis direct/look-back cause. The frozen vocabulary already
encodes degree as separate tags — *(measured)* 3,413 `qalqala_sughra`, 424
`qalqala_kubra` — while the design's `Rule` collapses both into one `QALQALA`.
That is the same un-collapsing failure the set indicts at `idgham.py:28`,
committed in the opposite direction.

**What should change.** Split `QALQALA` into `QALQALA_SUGHRA |
QALQALA_KUBRA | QALQALA_AKBAR`, consistent with the treatment of the four
idghām families and with the frozen tag vocabulary. Then delete `Participants`,
or reduce it to a single optional emphasis-cause field on `Occurrence`. A
tagged union with one variant carrying one fact is not an abstraction.

### F7. `Condition` has no consumer in a boundary-free Score, and duplicates the conditional nucleus members

**Claim.** Boundary-conditionality is modelled twice and only one of the two
mechanisms can reach the Score. This is a hole, not just redundancy.

**Evidence.** `Condition = ALWAYS | WHEN_STARTING | WHEN_STOPPING` is part of
the Ledger key (ADR-003 §7), the exception scope key (ADR-006 §4) and invariant
I3. ADR-006 §4.1 endorses two retiring exceptions as legitimate conditional
supplies — 27:36:8 "the real fact is a `WHEN_STOPPING` nucleus value" and
`started_ituuni` "the real fact is a `NUCLEUS = Long(I)` on a waṣl slot" under
`WHEN_STARTING`.

But ADR-001 §6 states the Score is boundary-free, and it is built once per
`(riwayah, revision, selection)`. `canon.build` has nowhere to put a
`WHEN_STOPPING` nucleus value. The design's answer for the one case it worked
through is the opposite mechanism: add a *nucleus member* that encodes the
condition (`PausalLong`, ADR-001 §3.3). Every `ledger.yaml` example in
ADR-007 §3 is `condition: ALWAYS`.

So the loader accepts entries the builder cannot consume, and I3 keys on a
field that is constant in every worked example.

**What should change.** Pick one mechanism. If conditionality lives in
`Nucleus` (`Silah`, `PausalLong`, and whatever 27:36:8 and `started_ituuni`
need), delete `Condition` from the Ledger key, from I3 and from ADR-006 §4's
scope key. If it lives in the Ledger, state how `canon.build` represents a
conditional fact in a boundary-free Score and say what `Silah` and `PausalLong`
are then for. Note that `PausalLong` — added during authoring as the worked
proof that the exception test works — is exactly the member that would be
unnecessary under the second option.

### F8. `Rule` names two different things, `SpellKind` names nothing, and `Spelling_` exists to dodge a collision

**Claim.** Vocabulary hygiene, in a set whose central claim is a closed
vocabulary.

**Evidence.**

- `Rule` is a `Protocol` with `look()` (ADR-004 §1) *and* "a closed StrEnum —
  the only rule vocabulary" (ADR-002 §5, used as such in ADR-003 §4's `Attests`).
  ADR-007 puts `Rule`, `RuleTag` and `Phase` all in `model/tajweed.py`, which
  cannot hold the Protocol: `look` takes a `Plan`, which lives in
  `engine/plan.py`, and `model` "imports nothing from this package".
- `RuleTag` appears exactly once in the whole set (ADR-004 §1, `tag: RuleTag`)
  and is a duplicate of the `Rule` enum.
- `SpellKind` appears only in ADR-007's `model/inscription.py` listing. ADR-003
  §4 replaced R2's flat record with a four-variant tagged union; `SpellKind` is
  a vestige of the shape R2 was written against and is defined nowhere.
- ADR-005 §1 declares `class Spelling_(StrEnum): COMPACT | EXPANDED` — a
  trailing underscore purely to avoid colliding with the `Spelling` union.
  Convention 1 bans names chosen for a symptom; a name whose only content is
  "not the other `Spelling`" is the same failure.
- Referenced but never defined anywhere in the set: `Trigger`, `Length`,
  `Option`, `Evidence`, `SoundSpec`, `ReleaseKind`.

**What should change.** One rule vocabulary, `Rule`, the enum, in `model/`.
Rename the classifier Protocol (`Classifier`) and move it to `engine/` or
`rules/`, where its `Plan` dependency is legal. Delete `RuleTag` and
`SpellKind` from the ADR-007 listing. Rename `Spelling_` (`SpellDepth`). Give
the six undefined names one line each, or the vocabulary is not closed.

### F9. The `Effect` union cannot express three of the four things `COLOUR` is assigned, and `Relength` lacks the aspect its conflict key uses

**Evidence.** ADR-004 §3: the `COLOUR` phase "decides tafkhīm/tarqīq, ghunnah
quality, imāla, tashīl". The only colouring effect is
`Recolour(slot, aspect, emphatic: bool)`. Ghunnah quality, imāla and tashīl
have no member. (Imāla and tashīl are canonical facts under ADR-001 §3.3, so
plausibly nothing is left for `COLOUR` to do with them — in which case the
phase table over-claims and should be corrected.) Separately,
`Relength(slot, length: Length)` carries no `aspect` while ADR-004 §4's
conflict table keys it on `(SlotId, Aspect)`, and `Length` is undefined.

**What should change.** Drop imāla and tashīl from the `COLOUR` row and add a
ghunnah-quality effect, or widen `Recolour` to a feature argument. Give
`Relength` an `aspect` or declare it nucleus-only and key it accordingly.
`Recolour` and `Relength` are the same operation — modify one feature of an
already-produced sound at `(slot, aspect)` — and merging them is available, but
I would leave them typed; that is a taste call, not a finding.

### F10. `Rule.SPELLING_EXPANSION` has no emitter

Expansion moved into `canon.build` (ADR-003 §2; ADR-004 §3 "There is no
`LEXICAL` phase"). `Occurrence` is the only path to sound (ADR-002 §5), but
`canon/` produces a `Score`, not a `Performance`, and no `rules/` module owns
this tag. Either the spelled slots' sounds come from ordinary rules — in which
case the member is dead and should go — or something in `canon/` emits
occurrences, in which case ADR-002 §5 needs a second emitter site named.

### F11. Six of the invariants are type facts, not runtime checks

ADR-008 §1: "Each is a one-pass assertion over a completed object, runnable on
the full corpus." S2 ("`Leen` does not exist"), S3 ("`ScoreWord` carries no
`advice` field"), S4 (ordinal contiguity — free if the ordinal *is* the tuple
index), P7 ("No `Attribution` and no `Occurrence` holds a `GraphemeId` or a
`Script`") and P4/P5 (F3) are statements about the source text, not about a
constructed object. They belong with X1–X3 as AST tests, or nowhere. They are
cheap, so this ranks low — but "26 invariants" reads heavier than it is, and
the actual count is 28.

Everything else in ADR-008 §1 survives the deletion test. I2, I3 (modulo F7),
I4, I5, E1–E5, A1, A2 and X1–X3 are real checks over real data.

### F12. The occurrence-volume worry is smaller than open question 3 implies

`PLAIN` will dominate the ~3×10⁵ estimate. After F6, `Participants` is empty
for most families and trivially empty for `PLAIN`, so `PLAIN` occurrences can
be interned to one object per traversal. Worth stating in ADR-008 §7.3 so that
phase 1's measurement is not later read as a reason to weaken "no sound without
a named occurrence", which is the invariant most worth keeping (§5).

---

## 2. Is the abstraction earned?

Two real users or a demonstrated need — not one plus a hypothetical.

| Seam | Users | Verdict |
|---|---|---|
| **Script** | 2, word-aligned, 77,433 slots each, neither mark inventory a superset | **Earned.** It is also the falsifier. Right. |
| **Notation** (`data/render/<notation>.yaml`, convention 10) | 2 historically | **Earned, and it looks speculative when it isn't.** The pre-refactor tree shipped `simple_mode.py` over `resources/simple_phonemes.yaml` — a second reduced-vocabulary notation, on the restore list. Say so in ADR-006 §3; otherwise the next reviewer deletes it. |
| **Riwayah** | 1 | **Earned on cost, not on users.** `rules_for(riwayah) -> RuleSet` is dependency injection; it costs a one-member enum and a mapping, and it deletes a named defect (`engine.py`'s unconditional `from .hafs import`). Keep. But a whole `model/riwayah.py` module for a one-member enum is the file-count rule past usefulness (§4). |
| **Ledger `Assert`** | both scripts, ~6,300 sites | **Earned, and the best-value idea in the set.** It converts marks the current parser silently discards into free regression oracles. |
| **`Aspect`** | 2 independent (the `كِتَٰبٌ` nucleus drop; the `(SlotId, Aspect)` conflict key) | **Earned twice.** See §5. |
| **`Participants`** | 0 demonstrable (F6) | Not earned. |
| **`ScoreRevision` / migrations** | 0 (F2) | Not earned. |
| **`Colouring`** | 2 words (F5) | Not earned as a separate axis. |
| **`Condition`** | 0 consumers (F7) | Not earned as written. |
| **Phases** | domain-facts invariant 8 | **Earned.** This is a domain fact made executable, not an architecture choice. |

**Where speculative generality hides behind a domain word:** `ScoreRevision`
(versioning), `Colouring` as a `frozenset` (extensibility), `Participants`
(attribution richness), `Condition` (boundary scope). Four, all small, all
named after real domain concepts, which is exactly why nobody caught them.

---

## 3. Is it simpler than what it replaces, where it counts?

**Size, honestly.** Estimated implemented totals:

| Package | Modules | Est. lines |
|---|---:|---:|
| `model/` | 9 | ~450 |
| `script/` | 5 | ~500 |
| `canon/` | 6 | ~900 |
| `engine/` | 5 | ~450 |
| `rules/` | 10 | ~900 |
| `render/` | 2 | ~180 |
| `corpus/`, `api`, `resources`, `dataio`, `riwayat` | 7 | ~280 |
| **total** | **44** | **~3,660** |

Against 2,033 lines in 25 modules today. **~1.8×**, plus ~1,000–1,400 test
lines for 22 fixtures, 28 invariants, the L1 harness and the round-trip. For
that you get a second script, an attribution graph, 33 named rules where today
one line implements four families, and enough retained structure to reconstruct
six frozen views. That trade is defensible.

**Could a much smaller design pass ADR-008?** No. ADR-008's cost is dominated
by three things that are not architecture choices: L1 equality over both
scripts (77,433 × 5 fields), the `write` round-trip (154,866 words), and the
derivation-class inventory that closes the L1 residue. Those come from the
falsifier — the second script — not from the design. Everything downstream of
"rules must not read orthography" follows from the *measured* 5,412-assimilation
nūn accident and the 13,483-versus-1 hamzat al-waṣl accident. You cannot get a
much smaller design that still passes; you can get a ~12% smaller one.

**Shape of the smaller design, in one paragraph, not designed here.** Keep the
three layers, the one-way reference, `canon.build`, both adapters, the
Supply/Assert Ledger, the effect model, the phase list and the whole of
ADR-008's gate. Collapse the four types in F1/F3/F4/F5 — `Attribution` becomes
a four-variant union, `SilenceReason` and `Colouring` and `SlotOrigin.LEXICAL`
disappear into `by.rule`, `Onset`/`Quality`, and nothing respectively. Delete
`ScoreRevision`, the migrations directory, `Participants` and `RuleTag`. Pick
one boundary-conditionality mechanism per F7. Merge `model/` into four or five
files instead of nine and drop `engine/registry.py` into `riwayat/hafs`. That
is roughly seven fewer named concepts, six fewer modules, six fewer invariants,
and no capability lost — the same ADR-008 §2 fixture list passes unchanged
except that fixtures 5 and 9 shrink.

---

## 4. The owner's own rules, audited against ADR-007

**KISS / DRY / YAGNI.** YAGNI is where the set is weakest (F2, F5, F6). DRY is
violated in four places, all small but all real: boundary-conditionality
modelled twice (F7), the rule vocabulary named twice (F8), the silence reason
stored twice (F4), and the stop-sign scalar classified twice in one YAML file
(ADR-007 §3 lists it under `structural:` *and* under `advice:`). KISS is
honoured in the parts that matter — one attribution relation with arity beat
spine A's facets and spine C's five roles, and that was the right call.

**Many small files — taken past the point of usefulness.** These six modules
will be under 40 lines for the life of the project, in a package whose own
convention 8 says 100–400:

| Module | Contents | Est. |
|---|---|---:|
| `model/riwayah.py` | one enum, one member | ~8 |
| `engine/registry.py` | `Riwayah -> RuleSet`, one riwayah | ~15 |
| `model/boundary.py` | a 4-member enum + a 1-field dataclass | ~20 |
| `model/address.py` | six type aliases (minus `ScoreRevision` per F2) | ~25 |
| `model/variant.py` | one `KhilafId` member, four sites | ~30 |
| `canon/select.py` | selection over one khilāf id | ~30 |

`model/` is ~450 lines of frozen dataclasses that every consumer imports
together, split nine ways. Four or five files is the honest split; `address` +
`riwayah` + `boundary` + `variant` are one file. Note also that the tree's own
convention implies a floor: 44 modules × 100 lines is 4,400, more than my
estimate for the whole package. Either the convention or the module count is
wrong, and it is the module count.

**Which module will be 900 lines.** ADR-007 §8 names two at-risk modules,
`engine/run.py` and `canon/derive.py`. It misses the biggest one.
`canon/build.py` gets one line in the tree — "the one entry: Reading ->
ScoreWord" — and must apply the Ledger, the article rule (11,995 slots), 526
waṣl skeletons, ~169 ṣilah exemption skeletons, five otiose classes, the Allah
lexeme (12 skeletons, 2,704 words), muqaṭṭaʿāt expansion and variant selection,
reconciling two evidence streams into byte-identical `Slot` tuples. That module
*is* the phase-1 gate. Add it to §8's at-risk list and say how it splits — by
fact class, not by phase, so each derivation class is one testable unit
matching ADR-008 fixture 6.

**One claim that is asserted rather than shown.** ADR-001 §2 concludes "the
adapters stay thin" and that spine A's headline cost is not paid. IndoPak has
85 distinct scalars, five polysemous marks, seat folding and combining hamza,
and ADR-003 §6.4 requires every `Evidences` declaration to be justified per
site class rather than per scalar count. Most of that weight lands in YAML,
which is the right call — but "thin" should be a phase-1 measurement recorded
in ADR-008 §5, not a premise in ADR-001.

**Where the conventions are excellent and should be kept verbatim.**
Convention 9 (errors name the address and both disagreeing sources; the
`expansion.py:42-50` same-sentinel-for-two-meanings pattern banned) is the
single best rule in the set. Convention 7 (no phoneme string outside `render/`,
no raw scalar comparison outside `script/`) is enforceable and load-bearing.
Convention 10 (instance-local resources, no module-level singleton) kills a
real class of bug. Moving `"ˤ"` and `":"` out of `rendering.py` into
`data/render/` is exactly right.

---

## 5. Complexity that pays for itself — what I would keep under a strict simplicity mandate

This section matters as much as the deletions.

1. **The script-free Score, both adapters, and L1 equality.** Non-negotiable.
   The 5,412 bare-nūn assimilations and the 13,483-versus-1 hamzat al-waṣl
   accident are proof that today's rules read orthography and would produce
   different phonemes on IndoPak. Nothing cheaper establishes that they don't.

2. **One-way reference, plus X1/X2 as AST tests.** The Performance layer having
   no grapheme field costs nothing at runtime and makes a bug class
   unwriteable. The import ban is one cheap test and it is, as ADR-007 §2 says,
   the only defence that survives a careless refactor. Two independent guards
   on one property is the right amount here, not belt-and-braces.

3. **Effects instead of neighbour mutation, and the per-phase conflict key.**
   This single decision deletes four named defects (`vowels.py:47`,
   `noon_tanween.py:31`, `meem.py:32`, `hafs.py:82`) and turns domain-facts
   invariant 2 from a comment into a runtime error. E1 is the highest-value
   invariant in ADR-008.

4. **`Aspect`.** Two members, earned twice: the `كِتَٰبٌ` waqf case where the
   nucleus drops while the onset sounds, and — separately and more importantly
   — as the conflict key, without which a `COLOUR`-phase onset recolour and a
   `LENGTH`-phase nucleus relength on the same slot collide spuriously. I would
   defend this one hardest of the contested additions. It is also the only
   ruling that made the design smaller in net terms: it discharged spine A's
   facet machinery and spine C's five roles at once.

5. **Arity as the sound-sharing mechanism.** `len(slots) == 0 | 1 | > 1` is the
   cheapest possible encoding of insertion, ordinary realization and joint
   ownership. It replaced two competing subsystems and survived both reviews.
   The frozen `share_group` field *(measured)* confirms it is exactly what the
   old public surface needed.

6. **Supply/Assert and the one-directional attestation law.** The only part of
   the design that *buys* rather than costs: ~6,300 sites of marks the current
   parser discards become free `MERGE`-phase oracles. The one-directionality is
   correct and measured — a bidirectional law fails on 2,415 words on day one.

7. **Occurrences as the only path to sound, including `PLAIN`.** Costs ~3×10⁵
   objects per traversal (mitigable, F12); buys the property that a projection
   cannot disagree with the engine, which is precisely what drifted in the
   legacy views. Without `PLAIN` you get a nullable `by` and a default path,
   which is the defect class being fixed.

8. **The `write` round-trip.** One assertion, 154,866 words, testing `Spelling`
   totality and adapter correctness simultaneously. Best value-per-line in the
   entire set, and neither of the other spines had it.

9. **The phase list.** Domain-facts invariant 8 states the dependency order as
   a domain fact. Five phases is the domain's number, not the architect's.

10. **ADR-008 §2's 22 fixtures.** Twelve named cases plus ten corpus-wide
    harnesses, for a ~3,700-line rewrite, is not excessive. It is under-priced
    if anything.

---

## 6. What I am least sure of

- **F6 (`Participants`).** The frozen baselines are a weaker bar than the
  eventual public projection API, which is out of scope here and therefore
  unmeasurable. If that API is going to expose domain-facts §4's "Classify"
  view — which letters participate in which named rule, as source or target,
  *with the trigger* — then the ikhfāʾ trigger letter may be a real requirement
  I am dismissing on the strength of a baseline that never carried it. I would
  hold F6 until the projection API is scoped; the `QALQALA` split is
  independently right either way.

- **F7.** I am confident there is a genuine hole — `Condition` has no consumer
  in a boundary-free Score — but not which side should give. Deleting
  `Condition` costs a mechanism for `WHEN_STARTING` facts that has no worked
  nucleus member yet; deleting the conditional nucleus members costs
  `PausalLong`, which ADR-006 §4.2 uses as its one worked proof that the
  exception test works. Someone with the domain should choose.

- **F1's severity.** If `origin` is quietly intended as "did *this* reading
  write it", the field is script-relative and the fix is to drop it from the
  comparator — cheap. If it is intended as canonical, the `LEXICAL` analysis
  stands and the member is empty. I am confident about `LEXICAL`; less
  confident about how much residue the field would actually produce at the
  gate, because that depends on a build I cannot run.

- **My line estimates in §3.** ±30%. The direction (roughly 1.8×, not 4×) is
  what I would stand behind; the absolute numbers are judgement.

---

## Verdict

**AMEND.** Author from this set after: F1 (`SlotOrigin.LEXICAL` deleted;
`origin` given a script-independent definition or removed from the L1
comparator), F2 (`ScoreRevision`, `migrations/` and S5 deleted), F3
(`Attribution` as a four-variant union; `Attach`, P4, P5 deleted), F4
(`SilenceReason` deleted), F5 (`Colouring` folded into `Onset`/`Quality`), F7
(one boundary-conditionality mechanism chosen), F8 (one `Rule` vocabulary;
`RuleTag`, `SpellKind`, `Spelling_` resolved; six undefined names defined), F9
and F10 (the `COLOUR` row and `SPELLING_EXPANSION` reconciled with the effect
union and the emitter set), and ADR-007 §1's `model/` collapsed from nine
modules to four or five with `canon/build.py` added to §8's at-risk list. F6
and F11 are optional. None of these is a load-bearing decision; the spine is
sound.
