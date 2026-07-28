# Convergence findings from spine C

## 1. Where B is genuinely better

**Claim.** B is the better baseline at the layer boundary. Its `Slot` is a
phonological position rather than a normalized letter, and its one-way
`Spelling → Score → Performance` reference direction makes script-independence
structural. C required discipline and a tested invariant; B leaves rules no
grapheme field to inspect. That subsumes C's `SourceWitness`/`WitnessLink`
boundary mechanism for the ordinary case.

**Evidence.** The adjudication's reasons are concrete: B's performance layer
contains no grapheme, and `write(read(t)) == t` tests adapter totality and
source spelling together. C's separate `RecitedUnit` graph is not needed if a
retained Plan plus `write` can spell every stored transformation. B's edge
arity is also cleaner than C's five attribution roles: more than one slot is
joint ownership, no slots is insertion, and `MERGED_INTO + HOSTS` is a merger.
The new measurements remove B's largest cost estimate: hamzat al-waṣl is one
article rule plus 526 canonical skeletons, while the silent mark is one otiose
wāw rule, five small lexical classes, and a few dozen one-offs.

**What should change.** Keep B's Score, Slot, Ledger container, Plan, and
`write` round-trip. Do not reintroduce a curated third corpus or a fourth text
layer merely because C had one. Treat C's score-revision/address-migration
obligation and projection dependency rule as already-adopted safeguards, not
reasons to reopen the baseline.

## 2. Where B lost something important

**Claim.** B's arity compression is too lossy at the attribution boundary.
`Attribution(slots, sound, kind, reason, by)` identifies a Slot, but not the
part of that Slot which is being carried, shortened, replaced, or silenced.
`Spelling.fact = NUCLEUS` explains evidence for a long vowel, but does not by
itself express which sound relation belongs to the onset versus the nucleus.

**Evidence.** C's `ComponentRef`/facet distinction handled cases B still has
to squeeze into a slot-level edge: a carrier may be silent while the onset
sounds; a final vowel may be dropped while the consonant remains; a tanween
component may be replaced at waqf while the base stays; and a full carrier and
its harakah may share one segment with different roles. The settled design
leaves this unmentioned. The open `هُوَ → huu` case is the warning: B says the
Slot can end with no `HOSTS` edge of its own, but does not say whether that is a
boundary change to the Slot, a nucleus-only attribution, or a hidden second
position.

**What should change.** Retain one relation and B's arity rule, but add a
closed `Aspect` (at least `ONSET` and `NUCLEUS`) to each attribution/effect. A
`SILENT` or `MERGED_INTO` edge must name the aspect it suppresses; a `HOSTS`
edge must say which aspect owns the sound. This is not a second alignment
table and does not weaken B's one-relation invariant. Add fixtures for carrier
silence, waqf vowel drop, tanween ʿiwaḍ, and final wāw/yāʾ role change.

**Claim.** B also loses C's separation between canonical authority and witness
evidence. Its Ledger is an excellent container, but its current L2 wording
allows “the script” or “the Ledger” to be the authority for a fact on a
per-script basis.

**Evidence.** A script may write a fact that the other script omits; present
marks must validate, not drive. If Uthmani supplies a fact in one row and the
Ledger supplies it for IndoPak, the canonical fact has two apparent suppliers
unless the record distinguishes supply from assertion. A polysemous sakt mark
in both scripts makes this a correctness issue, not terminology.

**What should change.** Use B's `Ledger` as the indexed store, but adopt C's
stronger `Supply/Assert` semantics: exactly one canonical `Supply` for a
`(riwayah, SlotId, fact, condition)`, from a script-independent derivation or a
typed Ledger entry; zero or more script-scoped `Assert`s. A present glyph is
never the canonical supplier. A disagreement names the supplier and the
asserting witness and fails. This preserves B's cheap storage while making
one-authority-per-fact executable.

## 3. Gaps in the merged design

**Highest priority: exact L1 equality is still unproved.** The 94.4% figure is
slot-count and letter-skeleton agreement from a naive canonicalizer, not
equality of `Slot.letter`, `onset`, `nucleus`, `colour`, and other canonical
fields. The 4,329 residue is said to be dominated by named classes, but it has
not been enumerated after those classes are applied. Until that happens, the
derived Score is an attractive hypothesis, not a script-independence proof.

**Second: the Ledger's residual classes need typed ownership.** “Two rules, a
lexicon of order 10², and a few dozen one-offs” is a cost result, not a
mechanism. The 526 skeletons, the five silent-letter classes, and every one-off
need closed derivation classes or typed fact entries. A raw location list would
recreate the exception patching B rejects.

**Third: `write` renderability is open at exactly the dangerous point.** B's
projection is sufficient only if every recited form can be spelled from Slot
state plus a Plan anchor. The merged design has no explicit typed representation
for a recited form that is not a Slot spelling. The 3:1 connected mīm fatha,
hamza-wasl helping vowels, madd-ʿiwaḍ, taa marbuta at waqf, and muqaṭṭaʿāt
expansion must all pass a total `write` check before a separate layer is ruled
out. If any case needs a new Arabic sequence with no Slot spelling, B's refusal
of a recited-writing layer has failed its own trigger.

**Fourth: boundary role transitions are asserted, not typed.** `STOP`, `SAKT`,
`JOIN`, and `EDGE` need an explicit boundary object and conflict rules. In
particular, `SAKT` blocks cross-word rules without applying waqf transforms,
while `STOP` changes the effective final form. The Plan must make those
differences visible to every phase, not leave them as an effect convention.

**Fifth: occurrence volume and invariant cost remain unmeasured.** B names
plain iẓhār and tarqīq as occurrences, plausibly producing order 10⁵ records.
Measure memory, serialization, and validation over the full corpus before
freezing the aggregate representation. The unverified `يسٓ`/`نٓ` wajh remains a
domain decision, not a modeling detail.

## 4. What the merged design needs before implementation is committed

1. Define an exact L1 comparator and immutable score hash. Compare every
   canonical field at every aligned Slot, not slot count or skeleton only.
   Produce a residue report whose rows are `(location, ordinal, field,
   Uthmani, IndoPak, derivation_class)`. The report must be empty after the
   approved derivation closure; no unclassified row is acceptable.

2. Make the Ledger typed and total. Its loader should reject duplicate
   suppliers, a `Supply` without a canonical vocabulary value, an `Assert`
   without a corresponding fact, a script-specific value that rules can see,
   and a location entry that is really an output patch. Keep the measured
   lexical classes as canonical-skeleton rules, not thousands of rows.

3. Add `Aspect` to B's single attribution relation and enforce these
   invariants: every sound has exactly one `HOSTS` edge (possibly jointly
   owned); every written aspect either has an edge or a reasoned `SILENT` edge;
   every insertion has zero Slot inputs and a typed originating occurrence;
   every merger has one `MERGED_INTO` and one or more `HOSTS` edges tied to one
   occurrence. This preserves B's relation while retaining C's provenance
   precision.

4. Specify a typed Plan vocabulary for inserted semantic forms and anchors,
   then run `write(read(t), SOURCE, SHOW, HIDE, COMPACT) == t` for both scripts
   and all 77,433 words. Add recited-writing fixtures for the four boundary
   modes, muqaṭṭaʿāt, and the two evidence-pack defects. Promote a fourth layer
   only if an observed form cannot be represented by those Plan facts.

5. Measure occurrence count, peak graph size, and validation time on the full
   corpus. Add phase-level conflict assertions: two effects on one
   `(SlotId, Aspect)` in a phase fail; no cross-word effect crosses `STOP` or
   `SAKT`; every named occurrence points to the effect that produced its sound.

## 5. The derived-versus-curated fork

**Verdict on the decision.** Derived is the right direction, but the recorded
reversal trigger is not sharp enough to fire. C's original structural argument
was too pessimistic about cost: 89% of hamzat al-waṣl cases are one rule, the
remaining 1,487 are 526 canonical skeletons, and 92% of the always-silent mark
is one rule. Those measurements make a curated 77,433-word Score a poor
default.

The trigger “if the L1 equality residue does not reduce to named, derivable
classes” is underspecified in three ways:

- “L1 equality” is not defined; the measured 94.4% is not L1 equality at all.
- “named” has no registry, and “derivable” does not say whether a
  script-specific branch or a location patch qualifies.
- It has no terminal condition or action: one cannot tell when the residue is
  closed or when to promote the Score to an authored artifact.

Replace it with this executable trigger: after applying a fixed,
script-independent set of derivation classes and typed Ledger supplies, compare
the complete canonical Slot tuples. Accept derivation only when the mismatch
set is empty and every class has code, fixtures, and a bounded fact schema. Fire
the curated-Score reversal if any mismatch remains unclassified, if a class
needs `script_id` to choose a canonical fact, or if the supposed derivation is
actually a per-location output patch. A nonzero residual is not “mostly named”;
it is a failed equality proof. The class inventory and exact comparator must be
committed before the derived architecture is treated as settled.

## Verdict

The merged design is close, and B should remain the baseline, but it is not
ready to author without the exact L1 residue closure and facet-aware
attribution. **REVISE**.
