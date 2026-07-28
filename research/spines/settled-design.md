# Settled design — adjudication of spines A, B, C

Orchestrator decision, 2026-07-26. Three spines were written independently and
blind (`spine-a.md`, `spine-b.md`, `spine-c.md`) from one evidence pack. This
records what is settled, what was chosen over what, and what remains open.

## 1. Settled by convergence

All three spines reached these independently. They are decisions, not options.

1. A **script-free canonical layer** sits between orthography and sound and is
   the only thing rules read or address.
2. Its unit is **not a letter**. Carriers, seats, otiose letters and length
   marks are demoted to evidence for a unit's facts.
3. **Bare-versus-sukūn is collapsed at that boundary.** All three identified
   this as what kills evidence §2.
4. **One attribution relation**, not separate alignment / silence / merge /
   insertion tables.
5. Rules are **pure functions returning declared effects**. No neighbour
   mutation. Two effects on one target is an error, not a precedence.
6. **Occurrences are the only path to sounds**, so a projection cannot disagree
   with the engine.
7. **Marks validate; tables supply.** Never the reverse.
8. **Variant selection resolves before rules**, on the canonical layer.
9. The **exception scope key includes script**, not riwayah alone.

Also unanimous and unprompted: the current `structural:` dumping ground and
`SourceMark.SECOND_HAMZA` are anti-patterns.

## 2. The chosen spine

**Spine B is the spine.** Its object graph, layer names, relations, phases, and
the Ledger are the baseline. Reasons it was chosen over A and C:

- **Script-independence is structural, not disciplinary.** Reference direction
  is one-way — `Spelling` points up into the Score, `Attribution` runs
  `SlotId → SoundId`, and the performance layer has no grapheme field. A rule
  that wants a glyph has nowhere to look. A achieves the same property by
  discipline plus a tested invariant.
- **`write` as the inverse of `read`.** Recited writing becomes a projection
  rather than a fourth layer, and it yields a total round-trip test —
  `write(read(t)) == t` over 77,433 × 2 words — which tests `Spelling`
  totality and the adapter at once. Neither A nor C has this.
- **Joint ownership by edge arity.** `len(slots) > 1` is shared ownership,
  `len(slots) == 0` is insertion. One relation with three kinds replaces A's
  facet machinery and C's five roles.

## 3. The fork that was decided

| | A and B | C |
|---|---|---|
| canonical layer | **derived** per script by an adapter | **curated** as a versioned artifact; scripts are witnesses |
| script equality | proved by a corpus-wide equality test | structural — one score, one rule run |
| cost | adapters carry the linguistic load | a third 77,433-word artifact to author, version, migrate |

**Decision: derived.** C is right that a tested invariant is weaker than a
structural one, but C pays for the guarantee with a new curated corpus, and the
evidence says derivation is tractable: B's naive ~120-line canonicaliser, with
no Ledger at all, already yields identical slot counts for 73,104 of 77,433
words (94.4%), residue dominated by two named classes.

**Reversal trigger, recorded:** if the L1 equality residue does not reduce to
named, derivable classes, C's curated score is the fallback. That is a
promotion of the same canonical layer to an authored artifact, not a redesign.

## 4. Grafts onto B

- **From A — the unit-hood criterion.** *Can it produce sound at its own
  position in at least one boundary state or reading?* B asserts its four
  omissions from `Slot`; A gives the rule that generates them. Adopt A's, and
  state B's omissions as consequences of it.
- **From C — score revision and address migration.** `SlotId` is stable until
  someone corrects the corpus. C is the only spine that says what happens then.
  Adopt an explicit score revision plus a migration obligation.
- **From C — projection packages do not import classifiers.** A
  dependency-direction rule, enforceable in packaging and CI, complementing B's
  "no sound without a named occurrence". Two independent guards on one property.
- **From C — recorded risk.** A future witness with genuine word join/split
  breaks `WordKey` / location-scoped slot ordinals as the primary container.
  Record as a known limit, not a solved problem.

## 5. Measurement that resolved B's stated cost

B's largest unknown was Ledger size; it estimated order 10⁴ IndoPak entries and
said that number decides "whether this is a table or a rule set". Measured:

**Hamzat al-waṣl**, 13,482 Uthmani word slots: 11,995 (89%) are the article
`ٱل` — one rule; the remaining 1,487 reduce to **526 distinct canonical
skeletons**.

**Always-silent `۟`**, 3,970 sites: 3,640 (92%) are the otiose alef after
word-final wāw — one rule; ~300 fall into five small lexical classes; ~25 are
genuine one-offs.

So the Ledger is **two rules, a canonical lexicon of order 10², and a few dozen
one-offs** — not 10⁴ location rows. And the lexicon is Arabic morphology keyed
by canonical skeleton, so it is script-independent and riwayah-scoped by
nature. B's architecture is materially cheaper than B assumed.

**Derived design rule:** a location table growing toward 10⁴ entries is a signal
that a rule is missing, not that the corpus is irregular.

## 6. Corrections to the evidence pack

Spine B's spikes corrected four claims; all four were verified independently and
the pack and `corpus_sources/riwayat/hafs/scripts/README.md` are now fixed.

| Was | Is |
|---|---|
| seen/ṣād khilaf at exactly 3 sites | **4 union sites** — 88:22:3 is marked in IndoPak, unmarked in Uthmani |
| `ࢵ` U+08D5 is an IndoPak khilaf marker | an ordinary waqf sign, 95 sites |
| polysemous marks are an Uthmani quirk | IndoPak's `ࣝ` is polysemous too — 3 sakt + 4 waqf, missing 2 of Uthmani's. Sakt is authoritative in neither script |
| (not previously stated) | `ٱ` U+0671: 13,483 in Uthmani, **1** in IndoPak — a script accident 2.5× the nūn one |

## 7. Open, and who owes an answer

1. **L1 equality residue.** 94.4% slot-count agreement is indicative, not proof;
   it compares slot count and letter skeleton, not full `Slot` equality. The
   residue must be enumerated and named before implementation commits.
2. **Occurrence volume.** B's model emits an occurrence per sound including
   iẓhār and tarqīq — order 10⁵ per full recitation, unmeasured.
3. **Slot demotion.** `هُوَ` → *huu* at waqf turns a consonant slot into a
   length carrier. B expresses it as a `BOUNDARY` effect leaving the slot with
   no `HOSTS` edge; it is the one place "a slot is a consonant position" bends.
4. **Recited-writing layer.** B refuses one, arguing `write` plus a retained
   Plan suffices. If a pausal convention needs a grapheme sequence no Slot can
   spell, that argument fails and a fourth layer is warranted.
5. **يسٓ / نٓ wajh** — still unverified against a domain reference.

## 9. Convergence round — rulings

Both spine authors reviewed the adjudication against their own designs
(`convergence-a.md`, `convergence-c.md`). Verdicts: A `CONVERGE` with two
required amendments, C `REVISE`. Rulings below are binding on authoring; the
author may contest any of them with reasons before writing.

### R1. Attribution carries a closed `Aspect`. Arity is retained.

The two reviews disagreed. A conceded that B's edge arity plus `Spelling`
fan-in subsumes A's facets; C argued slot-level attribution is too lossy and
proposed adding `Aspect` (`ONSET`/`NUCLEUS`).

**Ruling: adopt `Aspect` on every attribution and effect; keep arity for sound
sharing.** The disagreement is narrower than it looks and resolves on one case.
For a `HOSTS` edge the aspect is inferable from the sound's kind — which is
exactly A's named residue, the "Sound-kind ↔ SlotFact correspondence", and A
itself observes that relying on it is the downstream re-derivation B forbids.
For a `SILENT` edge there is no sound to infer from: at waqf the final vowel
drops while the consonant still sounds, so the slot already satisfies B's
"every Slot in at least one Attribution" through its consonant edge and **the
dropped nucleus goes unrecorded**. A's own §2.4 partition, which keeps
`WAQF_DROP` and `SILAH_DROP` as traversal reasons, presumes nucleus-scoped
silence without naming it.

One closed enum field discharges C's correctness case and A's residue together,
and leaves B's one-relation invariant intact. A's facet machinery stays
rejected; C's five roles stay rejected.

### R2. `SpellKind.ATTESTS` and the L2 agreement extension. Highest priority.

A measurable class of graphemes evidences a **performance outcome**, not a
Score fact, and B's `Spelling`/Ledger are closed over `SlotFact`, so the
IndoPak adapter hard-fails at 2:1:1 on real input. Confirmed cases: the
muqaṭṭaʿāt idghām shadda written at 2:1, 3:1, 29:1; the 3:1 iltiqāʾ fatha whose
referent sound has `slots == ()`; word-initial shadda ʿāridah (**3,710**
Uthmani / **5,761** IndoPak, measured); and the 546 IndoPak iqlāb marks, whose
promised validation currently has no mechanism.

Adopt `SpellKind.ATTESTS` with referent `(Rule, anchor SlotId)`, and extend the
agreement law: *if a script attests rule R at slot s, the engine must produce an
occurrence of R there in waṣl; disagreement raises.* This converts otherwise
unclassifiable graphemes into regression oracles for the `MERGE` phase.

### R3. Stop advice leaves the Score.

Measured over both corpora: 4,102 words carry a sign in both scripts, 1,447 in
exactly one, and only **320 of the 4,102 agree on sign class** — IndoPak
collapses Uthmani's `ۚ`, `ۖ` and `ۗ` into `ؕ`. Advice is a mushaf convention,
legitimately script-scoped. Leaving `advice` on `ScoreWord` would put thousands
of rows into the L1 residue that the reversal trigger reads.

Move advice to the Inscription layer, mapped per script into the shared
`StopAdvice` enum. State the consequence plainly: an advice-driven boundary
plan is **script-relative**, so phoneme identity across scripts holds per
*boundary plan*, not per advice request. Do not average the two conventions.

### R4–R7. Adopted without contest

- **R4.** Add nucleus kind `Silah(Quality)`. `Long(U)` cannot express a vowel
  that drops at waqf, and deriving silah from "written small" is a script read.
- **R5.** Delete `Nucleus.Leen`. Leen is a `LENGTH`-phase occurrence over
  (short-a slot, sākin glide slot, waqf). Keeping it in the Score hoists a
  performance fact into L1 and leaves the glide's consonant hostless. This also
  dissolves open item §7.3 — the `هُوَ` wāw is a slot by criterion and takes a
  `MERGED_INTO` edge at waqf; nothing bends.
- **R6.** The unit-hood graft is criterion **plus** a companion principle, plus
  a clause. A showed the criterion alone generates one of B's four omissions.
  Companion principle: *the Score stores recitation facts; distinct spellings of
  one fact collapse to it, and letter identity is phonological, not glyphic.*
  Clause: *contributing length to a neighbouring slot's nucleus is not "sound at
  its own position"* — without it the seven-alifs alif and the ṣilah minis
  become slots.
- **R7.** Partition `SilenceReason`. `SEAT`, `OTIOSE` and `ORTHOGRAPHIC_ZERO`
  describe graphemes the criterion excludes from slot-hood, so a slot-attached
  `SILENT` edge can never carry them. Orthographic non-sounding is a
  `Spelling` fact; `SilenceReason` keeps traversal reasons only.

### R8. Ledger uses Supply/Assert semantics

Exactly one canonical `Supply` per `(riwayah, SlotId, fact, condition)`, from a
script-independent derivation or a typed entry; zero or more script-scoped
`Assert`s. **A present glyph is never the canonical supplier.** Disagreement
names the supplier and the asserting witness and fails. Sharper than "the
authority is the script or the Ledger", and with polysemous marks in both
scripts it is a correctness matter.

### R9. The reversal trigger, sharpened

Both reviews independently judged the §3 trigger unable to fire. Replacement:

> Evaluated at the end of phase 1, over **full canonical `Slot` tuple
> equality** — letter, onset, nucleus, colour, origin — after the §3b
> derivation classes and R3's advice removal are implemented. Derivation is
> accepted only when the mismatch set is **empty** and every class has code,
> fixtures, and a bounded fact schema.
>
> The fallback to a curated Score fires if: any residue row is unclassified; or
> a class needs `script_id` to choose a canonical fact; or a supposed derivation
> is a per-location output patch; or **any Ledger entry contradicts a script's
> explicit evidence** — that last is the Score claiming authority it has not
> earned, and fires immediately.

A nonzero residue is a failed equality proof, not "mostly named". More than ~50
one-off Ledger entries lacking a domain citation is a warning to review the
class inventory, not an automatic fire.

### R10. The L1 harness

Defined over full `Slot` equality, not slot count and skeleton — B's 94.4% is
count-and-skeleton only. Residue rows are
`(location, ordinal, field, uthmani, indopak, derivation_class)` and the report
must be empty after the approved closure.

### R9 amendment — "explicit evidence" defined

Raised during authoring and **accepted**. Clause 4 as I wrote it —
*any Ledger entry contradicting a script's explicit evidence fires immediately* —
misfires on the seven alifs on day one. IndoPak writes `اَنَا` with no mark, the
ordinary length derivation yields `Long(A)`, and the Ledger's `PausalLong(A)`
overrides it at all 66 sites. That is not the Score claiming unearned authority;
it is a script that has no way to say the thing.

Adopted definition:

> A script gives explicit evidence for a fact when its declared inventory
> contains a grapheme class evidencing that fact class **and an instance is
> present at the site**. A value produced by a derivation in the absence of any
> such grapheme is a default, not evidence.

The clause keeps its teeth: had IndoPak written a length grapheme and the Ledger
said `Silent`, that is a genuine contradiction and fires. Without the
definition the derived architecture would have failed over 66 words for the
wrong reason.

### Three authoring changes beyond the rulings — accepted

1. **The Score is built by a shared step after `read`, not inside the adapter.**
   R2's attestation anchors are otherwise dangling. This also means spine A's
   headline cost — thick per-script canonicalisers — is not paid: adapters
   extract evidence, one shared `canon.build` produces the Score.
2. **New nucleus kind `PausalLong(Quality)`** for the seven alifs. IndoPak
   supplies no mark, so the Ledger must supply a value, and that value has to
   exist in the canonical vocabulary. This is ADR-006's own exception test
   working as intended: the fix could not be expressed, so a vocabulary member
   was missing.
3. **Insertion `anchor: (SlotId, Side)` adopted now**, not held as a fallback.
   R2's law says a script attests rule R *at slot s*, and the 3:1 iltiqāʾ fatha
   has `slots == ()` — without an anchor the law is unenforceable at the very
   site that motivated it.

### Measurements corrected during authoring

- Muqaṭṭaʿāt attestation sites are **10**, not the 3 cited in R2 — 2:1, 3:1,
  7:1, 13:1, 26:1, 28:1, 29:1–32:1. Verified. Only 3:1 additionally carries the
  iltiqāʾ fatha.
- The attestation law must be **one-directional**. Word-initial shadda ʿāridah
  disagrees on ~2,400 words (~2,230 IndoPak-only, ~180 Uthmani-only, detector
  sensitive at the margin). Silence is not denial.
- Ṣilah is derivable after all: the naive rule's 3,094 false positives collapse
  to ~169 canonical skeletons, 2,688 of them the Allah lexeme the Score already
  recognises.
- A **fifth polysemous mark**: IndoPak `ٖ` U+0656 writes both ṣilah and ordinary
  long ī, so the scripts README's clean 1,257/1,257 ṣilah correspondence holds
  for the wāw side only.

### Carried forward, not rulings

Occurrence volume is ~3×10⁵ per traversal by A's estimate — measure in phase 1,
not a design risk. Insertion placement currently rides on `SoundId` stream
order; state that dependency, with `anchor: (SlotId, BEFORE|AFTER)` as the
fallback. Score revision and address migration still need at minimum "what
invalidates a `SlotId` and who publishes the map". The `يسٓ`/`نٓ` wajh remains
an unverified domain question.

## 10. Review round and the A1 ruling

After authoring, two Opus reviewers went over the ADR set from lenses no
designer had applied — simplicity/overengineering, and domain conformance,
delivery and extensibility (`research/reviews/`). Neither had authored a
competing spine, so neither carried the incentive to add that every previous
reviewer had. Both returned `AMEND`, and between them found four correctness
holes the design round had missed.

Blocking, all verified against the corpora before being acted on:

- deleting `Consonant.nasalized` made **10,667** frozen-snapshot tokens
  unreachable (`ñ` 4,098, `m̃` 3,254, `w̃` 2,192, `j̃` 1,123), so the design's own
  phoneme-parity fixture could not pass;
- `SlotOrigin` sat in the L1 comparator while being defined script-relatively —
  ~13,482 spurious residue rows, the gate failing on day one;
- `Nucleus.Nunated` could not survive E1;
- ADR-006's exception-test table, the set's own worked demonstration, was wrong
  in two of four rows.

**A1 ruled: the tanwīn nūn becomes its own slot; `Nunated` deleted.** What
decided it was the unit-hood criterion, not the invariant. At iẓhār sites the
tanwīn nūn sounds as a plain `n` at its own position — verified, `عَذَابٌ` →
`ʕaða:bun` — so it always was a slot and `Nunated` was a criterion violation
that E1 merely surfaced. Weakening E1 to accommodate the model (option 2) was
rejected on the principle that a design rule catching a modelling error is the
healthy direction.

Two corrections ran the other way. The author showed my A2 instruction —
"make the key composable over all features" — breaks parity if read as symbol
concatenation: the snapshot has **zero** `nn` against 4,098 `ñ`. Composability
must mean a total data lookup over the complete feature tuple. And it corrected
the reviewers three times with measurements, including 19 damma sites that make
all three branches of the domain-facts §5.7 hamzat-al-waṣl derivation
evidenced rather than two.

Recurring failure mode worth naming, since it appeared three times in one day
from three different authors including me: **a field that silently encodes which
script you happened to read.** R9's seven-alifs misfire, `SlotOrigin`, and
`ScoreWord.advice` are the same bug wearing different names. Any new canonical
field should be asked, explicitly, whether two witnesses could disagree on it.

## 8. Scope reminders

Unchanged from the spine brief. This round produces documents only, no
production code. Not in scope: the public projection API, Warsh phonology.
Khilaf covers token choice and per-location lexical choice only.
