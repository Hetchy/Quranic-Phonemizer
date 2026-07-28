# ADR-004: Rule execution — phases, the Plan, and the boundary plan

Status: **accepted**, amended after the simplicity and domain reviews.
**§8 records one decision still open.** Supersedes archived ADR-001 §6.

## 1. Decision

Every rule has one shape. There is no per-letter dispatch switch, because *the
switch is the asymmetry*: `rules/apply.py::_pronounce_letter` decides by
authorship which letters deserve a module, and rāʾ won while the lām of Allah
lost an inline `if`-branch.

```python
Trigger = frozenset[CanonLetter] | frozenset[NucleusKind] | frozenset[Onset]

class Classifier(Protocol):
    rule:     Rule                    # the closed enum; there is no `RuleTag`
    phase:    Phase
    triggers: Trigger                 # index key

    def look(self, score: Score, plan: Plan, at: SlotId,
             boundaries: BoundaryPlan) -> Verdict | None: ...
```

`look` is **pure**: a read-only `Score`, a read-only accumulated `Plan`, an
address, and the traversal. It returns a `Verdict` or `None`. It never writes.

The Protocol is named `Classifier`, not `Rule`. The first draft used one name
for both the Protocol and the closed enum and placed both in `model/`, which
cannot hold the Protocol — `look` takes a `Plan`, and `model` imports nothing
from the package. `Rule` the enum lives in `model/canon.py`; `Classifier` lives
in `engine/`.

## 2. Effects, not mutation

```python
class Side(StrEnum):          BEFORE | AFTER
class Length(StrEnum):        SHORT | LONG
class SoundFeature(StrEnum):  EMPHATIC | NASAL

Effect =  Realize(slot: SlotId, aspect: Aspect, sounds: tuple[SoundSpec, ...])
        | MergeInto(slot: SlotId, aspect: Aspect,
                    host: SlotId, host_aspect: Aspect)
        | Silence(slot: SlotId, aspect: Aspect)
        | Insert(anchor: tuple[SlotId, Side], aspect: Aspect,
                 sounds: tuple[SoundSpec, ...])
        | Recolour(slot: SlotId, aspect: Aspect,
                   feature: SoundFeature, value: bool)
        | Relength(slot: SlotId, length: Length)     # NUCLEUS by definition

@dataclass(frozen=True, slots=True)
class Verdict:
    occurrence: Occurrence
    effects:    tuple[Effect, ...]
```

`SoundSpec` is a `Sound` with its context-dependent features left unset — the
materialiser fills `emphatic` and `nasal` from later-phase `Recolour` effects.

A rule affects a neighbour by **declaring an effect naming it**, never by
writing to it. This replaces, precisely:

- `noon_tanween.py:31` and `meem.py:32` —
  `following.segments = [...]; following.resolved = True`;
- `vowels.py:47` — `owner.segments.pop(index)`, which destroys joint ownership
  at the moment it is created;
- `hafs.py:82` — `_replace(first letter matching identity)`, which is "the nth
  occurrence of glyph X" in disguise.

Changes from the first draft:

- **`Silence` loses its `reason`.** The reason is the verdict's own
  `Occurrence.rule` (ADR-002 §4.1); `SilenceReason` is deleted.
- **`Recolour` carries a feature, not a bare `emphatic: bool`.** A boolean
  covered one of the two things the `COLOUR` phase actually decides; ghunnah
  quality had no member at all.
- **`Relength` is declared nucleus-only** and keys on `(SlotId, NUCLEUS)`. The
  first draft gave it no aspect while the conflict table keyed it on one.
- **`Length` and `Trigger` are defined**, along with `SoundSpec` (above),
  `Option` (ADR-006 §2), `Evidence` (ADR-003 §1) and `ReleaseKind`
  (ADR-002 §6). The first draft referenced six names it never defined.

## 3. Phases

Closed and ordered — domain-facts invariant 8 made executable. Within a phase
rules are unordered and conflicts are errors.

| Phase | Decides | Reads |
|---|---|---|
| `BOUNDARY` | the domain-facts §7 waqf/ibtidāʾ transform set; ʿiwaḍ; tāʾ marbūṭa at waqf; `Onset.WASL`/`Onset.SILAH` resolution; `Nucleus.Silah`/`PausalLong` resolution | Score + `BoundaryPlan` |
| `MERGE` | which sounds exist: all idghām families, the nūn family (one shape for nūn sākinah and tanwīn alike — ADR-001 §3.5b), mīm, lām shamsiyyah/qamariyyah, waṣl elision, the iltiqāʾ repairs | Score + `BOUNDARY` output |
| `LENGTH` | madd classification, including leen (R5) | the sound stream from `MERGE` |
| `COLOUR` | **tafkhīm/tarqīq and ghunnah quality** | Score + sounds |
| `RELEASE` | qalqala, and its degree | whether the closure survived `MERGE` |

The `COLOUR` row no longer claims imāla and tashīl. Both are canonical Score
facts (ADR-001 §3.3–3.4) supplied by `canon.build` and the Ledger; the `COLOUR`
phase emits their `IMALA`/`TASHIL` occurrences so that every attribution has a
`by`, but it does not *decide* them. The first draft had ADR-004 and ADR-003
disagreeing about which layer owned them.

There is **no `LEXICAL` phase**. Allah-lexeme recognition, muqaṭṭaʿāt spelling,
the hamzat al-waṣl lexical class and its helping vowel (ADR-003 §6.3), and
variant selection all run in `canon.build`, before the Score exists.

`allow_forward_rules` does not exist. Evidence §4.1's missing 27:1 ikhfāʾ came
from `expansion.py:76` blanket-blocking the final expanded name; with expansion
before the Score, spelled slots are ordinary slots. The two genuine Hafs
exceptions (`يسٓ` 36:1, `نٓ` 68:1) become Ledger entries or named rules.

## 4. The Plan and conflict

```python
class Plan:
    """Append-only journal. Keyed for conflict detection, ordered for replay."""
    def record(self, phase: Phase, verdict: Verdict) -> None: ...
    def sounds_so_far(self) -> Sequence[Sound]: ...
```

Conflict keys, per phase:

| Effect | Key |
|---|---|
| `Realize`, `MergeInto`, `Silence`, `Recolour` | `(SlotId, Aspect)` |
| `Relength` | `(SlotId, NUCLEUS)` |
| `Insert` | `(anchor_slot, Side)` |

> **E1. Two effects on one key within one phase is an error**, raising with both
> occurrence tags and both rule names.

Domain-facts invariant 2 says exactly one rule of a family fires per trigger and
that the families' conditions are mutually exclusive. Asserting it turns every
violation into a found bug instead of silent last-writer-wins. Across phases the
key may repeat: `MERGE` may realize a consonant that `COLOUR` later recolours —
which is the second, and arguably more important, justification for `Aspect`.

Two further execution constraints:

- No cross-word effect may cross a `STOP` or `SAKT` junction.
- Every occurrence must point to at least one effect that produced a sound, or
  be declared classification-only on its `Rule` member.

## 5. The boundary plan

```python
class Junction(StrEnum):  JOIN | SAKT | STOP | EDGE

@dataclass(frozen=True, slots=True)
class BoundaryPlan:
    junctions: tuple[Junction, ...]     # one per word: the junction AFTER it
```

- `JOIN` — cross-word rules fire.
- `SAKT` — a breathless pause: cross-word rules are **blocked**, no waqf
  transform is applied to the preceding word, and the following word is not
  started on.
- `STOP` — waqf transforms apply to the preceding word, cross-word rules are
  cancelled, and the following word is started on.
- `EDGE` — the requested range ends. Same ending transform as `STOP`; the
  distinction exists so a projection can tell a chosen stop from the end of the
  request.

Derived, not stored: a word is *started on* iff the junction before it is `STOP`
or `EDGE`, or it is first in the range; *stopped on* iff the junction after it
is `STOP` or `EDGE`.

**Constraint from the Score.** A `ScoreWord.sakt_after` forces `SAKT` unless the
plan selects `STOP`. It may never be `JOIN`. This makes 75:27 `مَنْ ۜ رَاقٍ` a
domain fact rather than the glyph shortcut evidence §2 describes.

**Construction.** `engine.plan_from_request` takes an `Inscription`, because
advice lives there (ADR-003 §5). Two scripts yield two plans from one request;
that is correct and stated. `stop_refs` are validated and an unknown reference
raises, closing the silent no-op at `engine.py:132`.

## 6. Riwayah binding

```python
@dataclass(frozen=True, slots=True)
class RuleSet:
    phases: Mapping[Phase, tuple[Classifier, ...]]

# both live in riwayat/<r>/ — the one package that may import anything
def rules_for(riwayah: Riwayah) -> RuleSet: ...
def adapters_for(riwayah: Riwayah) -> Mapping[Script, ScriptAdapter]: ...
```

The engine takes a `RuleSet`; `engine.py`'s unconditional `from .hafs import …`
disappears. Adapters bind the same way and from the same place — a riwayah owns
its scripts (ADR-007 §1.1), so `rules_for` and `adapters_for` are siblings. `Riwayah` stays a **closed enum** — supporting a riwayah requires
code, fixtures and packaged resources. This is not a plugin registry and there
is no generic YAML effect engine.

When research proves a riwayah delta, one typed classifier is swapped in the
phase list; both return the same effect vocabulary and record the same `Rule`
member. No profile subclasses, no `if riwayah == …` inside a rule.

## 7. What no rule may do

- Read a grapheme. There is no field (ADR-001 §1).
- Read a phoneme string. The render alphabet lives in `render/` and is
  unreachable from `rules/` by packaging (ADR-007 §2).
- Import `canon/`. This is why the waṣl helping vowel cannot be a `BOUNDARY`
  decision (ADR-003 §6.3) — the waṣl derivation is not legally reachable.
- Write to another rule's target, or to the Score.
- Consult `Script` or `StopAdvice`.

## 8. A1 — the tanwīn nūn and E1. **Ruled: option 3.**

`Nucleus.Nunated` is deleted; the tanwīn nūn is its own slot (ADR-001 §3.5b).
The record of how the decision was reached is kept below, because the reasoning
generalises: a design rule catching a modelling error is the healthy direction,
and weakening an invariant to fit the model is not.

### 8.1 The problem, confirmed live

`Nucleus.Nunated(Quality)` folds a *consonant* — the nūn — into a *nucleus*. At
an assimilating tanwīn the vowel stays on the tanwīn slot while the nūn merges
into the next word's onset:

```
2:5:3-2:5:5   هُدًى مِّن رَّبِّهِمْ  →  h u d a | m̃ i | rˤrˤ aˤ bb i h i m
```

The `a` is on word *n*; the nūn's sound is on word *n+1*. That requires
`Realize(slot, NUCLEUS, (Vowel,))` **and**
`MergeInto(slot, NUCLEUS, host=next, host_aspect=ONSET)` — two effects, one
key, one phase. **E1 raises.**

Measured over the Uthmani corpus, of 8,893 words carrying tanwīn: **4,671
followed by an idghām letter** (3,858 bi-ghunnah, 813 bila-ghunnah). The 304
iqlāb and 1,997 ikhfāʾ sites are fine — a single `Realize` with a two-sound
tuple. 1,921 are iẓhār.

It also makes the nūn/tanwīn family **structurally asymmetric**: the same rule
merges an `ONSET` when the trigger is a nūn slot and a `NUCLEUS` when it is a
tanwīn slot — against domain-facts invariant 1 ("every noon-sakinah rule has a
tanween twin") and against the owner's "no asymmetry between rule families".

### 8.2 Options

| | Mechanism | L1 equality | Attribution invariants | Slot ordinals |
|---|---|---|---|---|
| **1** | `MergeInto` gains `residual: tuple[SoundSpec, ...]` | unaffected | unaffected | unaffected |
| **2** | E1's key becomes `(SlotId, Aspect, sound_index)` | unaffected | unaffected | unaffected |
| **3** | **The tanwīn nūn becomes its own slot**; `Nucleus.Nunated` deleted | unaffected — both scripts write the tanwīn scalars (U+064B–D), 8,893 v 8,840 words, and the net 53-word gap is ADR-003 §6.5's named 55-word class (54 one way, 1 the other) | improved: one `Hosts` per aspect; `(slot, aspect)` becomes unique across edges too | **+1 slot on 8,893 words**; free today, nothing authored |
| **4** | `Aspect` gains a `CODA` member | unaffected | unaffected | unaffected |

**Costs in detail.**

*Option 1* is cheapest and additive, but `MergeInto` then both merges and
realizes, muddying the effect vocabulary, and it leaves the family asymmetry
untouched. It treats the symptom.

*Option 2* is circular — `sound_index` indexes a sound list that does not exist
until effects are applied — and it weakens E1 from "one rule per family per
trigger" to "one rule per sound", losing the domain invariant E1 exists to
assert. **Reject.**

*Option 3* deletes the category error. Every nūn rule then triggers on a `NOON`
slot with `nucleus=Silent` and merges its `ONSET`: tanwīn and nūn sākinah become
literally the same rule with the same trigger, which is what domain-facts §5.1
says they are ("tanween *is* a short vowel + noon"). `Realize` lands on the base
slot's `NUCLEUS`, `MergeInto` on the nūn slot's `ONSET` — two keys, E1
satisfied. ʿiwaḍ at waqf becomes `Relength` on the base plus `Silence` on the
nūn slot; dammatan/kasratan at waqf become two `Silence`s. The iltiqāʾ kasra
after tanwīn stops being an insertion and becomes the nūn slot's own nucleus —
which **also explains IndoPak's `ࣙ`** (ADR-003 §6.5), a glyph that depicts
exactly a nūn-plus-kasra on the following word.

Costs: one tanwīn mark must evidence facts on two slots — already routine, since
three compact muqaṭṭaʿāt graphemes fan to seven slots — and `write` must spell a
slot *pair* as one grapheme, likewise already required for muqaṭṭaʿāt. Slot
ordinals shift on 8,893 words, which is free while no data file exists and
expensive after.

*Option 4* is option 3 without the honesty: a `CODA` aspect that only ever holds
a nūn is `Nunated` renamed, and it breaks `Aspect`'s closure argument (the
slot's own field partition) unless `Slot` gains a third field.

### 8.3 The ruling: option 3

The decisive argument is not E1 but the **unit-hood criterion**. The tanwīn nūn
sounds as a plain `n` at its own position wherever iẓhār applies — `عَذَابٌ` →
`ʕ a ð aː b u n`, `سَوَآءٌ` → `s a w aː ʔ u n`. By ADR-001 §3.1 that makes it a
slot. It always was one; `Nunated` was a criterion violation that E1 surfaced.

(Two independent counts of the iẓhār sites were taken — 1,921 counting every
tanwīn word followed by a throat letter, and 1,188 restricting to cross-word
junctions within a verse. Different scoping, same conclusion, and the criterion
argument needs only one example.)

Option 3 is therefore not a workaround but the correction the criterion already
required, and it pays for itself three more times: it removes the family
asymmetry, it removes one of only two genuine insertion cases, and it turns 54
IndoPak graphemes from an unexplained attestation into ordinary evidence.

Option 2 was rejected on the same principle from the other side: dropping E1
from "one rule per family per trigger" to "one rule per sound" would have cost
the domain-facts invariant E1 exists to enforce, in order to accommodate a model
error. Option 1 leaves one family with two merge shapes; option 4 is option 3
with the honesty removed.

### 8.4 Edits committed

| ADR | Change |
|---|---|
| 001 §3.4 | `Nucleus.Nunated` deleted |
| 001 §3.5b | new — the two-slot tanwīn shape and what it buys |
| 002 §4.2 | the 3:1 fatha is now the *only* slot-less sound |
| 002 §7 | `(slot, aspect)` is now unique across edges; the counter-example is gone |
| 003 §6 table, §6.5 | `ࣙ` reclassified from `Attests(INSERTION)` to ordinary `Evidences` |
| 004 §3 | `MERGE` names one nūn family, not two triggers |
| 008 fixtures 6, 9, 17 | tanwīn class re-derived; `كِتَٰبٌ` trace gains a slot; the U+08D9 oracle moves from attestation to evidence |
| 008 §7 | A1 removed from the open list |

`Effect` (§2), the phase list (§3) and the conflict keys (§4) are unchanged.
