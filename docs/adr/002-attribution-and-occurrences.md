# ADR-002: One attribution relation, and occurrences as the only path to sound

Status: **accepted**, amended after the simplicity and domain reviews.
Supersedes archived ADR-001 §§4–5 and the `Alignment` layer it proposed.

## 1. Decision

One relation connects the Score to sound. It is a **four-variant tagged union**,
carries a closed `Aspect`, and uses arity for sound-sharing. There is no
separate alignment, silence, merge or insertion table, and no facet machinery.

```python
class Aspect(StrEnum):  ONSET | NUCLEUS

Attribution =   Hosts(slots: tuple[SlotId, ...], aspect: Aspect,
                      sound: SoundId, by: OccurrenceId)
              | Inserted(anchor: tuple[SlotId, Side], aspect: Aspect,
                         sound: SoundId, by: OccurrenceId)
              | MergedInto(slots: tuple[SlotId, ...], aspect: Aspect,
                           sound: SoundId, by: OccurrenceId)
              | Silent(slots: tuple[SlotId, ...], aspect: Aspect,
                       by: OccurrenceId)
```

The first draft used an `Attach` tag enum with three tied `Optional`s, which
broke this set's own conventions 2 and 3 (ADR-007 §4) — and named itself as the
single exception to convention 3. The union restores them and turns invariants
P4 and P5 into type facts checked once by mypy rather than runtime assertions
over ~3×10⁵ edges per traversal.

`Attach` and `SilenceReason` are deleted. `Inserted` is the `len(slots) == 0`
row of §3's table, named.

## 2. `Aspect` (R1)

`Aspect` has exactly two members because a `Slot` is definitionally an onset
plus a nucleus. The enum *is* the slot's own field partition; a third member
would mean the slot gained a third field.

R1 was issued as a cost against spine B's compression. It is not one — spine B
already keyed its Plan on `(SlotId, aspect)` with `aspect` as an unnamed
informal notion. R1 types a field the design was already using, so the Plan's
conflict key (ADR-004 §4) and `Attribution.aspect` are the same closed enum.
The correctness case R1 cites is real and was unhandled:

> At waqf, `كِتَٰبٌ` → `kitaːb`. The final bāʾ's onset still sounds; its
> nucleus (the tanwīn) drops. Without an aspect, the slot satisfies "every slot
> appears in at least one attribution" through its consonant edge and **the
> dropped nucleus goes unrecorded**.

`Aspect` also **fully discharges** the residue A named in `convergence-a.md` §3.
Answering "which graphemes own *this* sound" is
`sound → attribution → (slot, aspect) → Spelling rows whose fact matches that
aspect`, where the correspondence is total and closed:

| `Aspect` | `SlotFact` values that belong to it |
|---|---|
| `ONSET` | `LETTER`, `ONSET` |
| `NUCLEUS` | `NUCLEUS` |

`SAKT` is a word-boundary fact and is not aspect-scoped. No inference from sound
kind is required anywhere, so A's "Sound-kind ↔ SlotFact correspondence" is not
needed and must not be written.

## 3. Arity

| `len(slots)` | Variant | Meaning |
|---:|---|---|
| 0 | `Inserted` | no slot owns the sound; `anchor` places it |
| 1 | `Hosts` / `MergedInto` / `Silent` | ordinary realization, merge source, or silence |
| >1 | `Hosts` / `MergedInto` / `Silent` | joint ownership: one sound owned by several slots, possibly in different words |

This replaces spine A's facets and spine C's five roles. It survived both design
reviews and both amendment reviews unchanged, and the frozen
`character_phoneme_mappings` baseline confirms it is what the old public surface
needed: its `share_group` field (109,458 cells) *is* arity.

## 4. The four required shapes

| Demand | Stored as |
|---|---|
| Harakah and carrier share one long vowel | one `Hosts(slots=(s,), aspect=NUCLEUS)`; both graphemes reach it through `Spelling` rows with `fact=NUCLEUS` — the fan-in is script-scoped, the edge is not |
| Cross-word merger | `MergedInto(slots=(w_n,), aspect, sound=S)` **plus** `Hosts(slots=(w_{n+1},), aspect, sound=S)`, both with the same `by` |
| Insertion with no source grapheme | `Inserted(anchor=(s, AFTER), aspect, sound=S, by=…)` |
| Deletion with a reason | `Silent(slots=(s,), aspect, by=…)` — the reason is `by.rule` |

There is no source/target boolean and no `assimilated` flag on a slot. A merger
*is* the pair of edges sharing a `SoundId` and an `OccurrenceId`.

### 4.1 The silence reason is `by.rule`

`SilenceReason` is deleted. `Attribution.by` is guaranteed non-null (§5) and
`Occurrence.rule` is a closed enum containing `WASL_ELISION`, `WAQF_ENDING` and
`SILAH`, so the reason is recoverable in full, in both directions, with no
parallel enum.

This is exactly the argument spine A's author made for `InsertionOrigin` and
conceded (`convergence-a.md` §1.3): "B derives the reason from
`Attribution.by` — the occurrence's `Rule` already names it. One enum fewer, no
information lost." Nobody applied it to silences.

R7's substantive finding survives untouched: `SEAT`, `OTIOSE` and
`ORTHOGRAPHIC_ZERO` describe graphemes the unit-hood criterion excludes from
slot-hood, so no slot-attached silence can carry them regardless of where the
reason is stored. Orthographic non-sounding is a `Spelling` classification
(ADR-003 §4). Warsh naql, which the domain review notes is neither elision nor
waqf-drop nor ṣilah, becomes a `Rule` member — which is where a named
phonological process belongs.

### 4.2 The insertion anchor

R2's agreement law is stated as "if a script attests at **slot s**". The 3:1
iltiqāʾ fatha's referent sound has no slot, so without an anchor the law has no
address to check at exactly the site that motivated it. Stream-order placement
is also precisely the implicit convention this design exists to eliminate.

Note which repairs are **not** insertions. The Allah name's long ā is a
canonical `Nucleus.Long(A)` on the lām slot. The hamzat al-waṣl start vowel
fills the waṣl slot's own nucleus (ADR-003 §6.3). The iltiqāʾ kasra after tanwīn
fills the tanwīn nūn's own nucleus (ADR-001 §3.5b). **The 3:1 fatha is the only
genuinely slot-less sound in the design**, which is why its 54 IndoPak cousins
at ADR-003 §6.5 turned out to be evidence rather than attestation.

## 5. Occurrences are the only path to sound

```python
@dataclass(frozen=True, slots=True)
class Occurrence:
    id:     OccurrenceId
    rule:   Rule                  # closed StrEnum — the only rule vocabulary
    parts:  Participants          # tagged union, one variant per family
```

> **Invariant.** Every `Attribution.by` is non-null, including for iẓhār,
> tarqīq, lām qamariyyah and plain realization. No sound exists except as the
> output of a named occurrence.

A tajweed projection is `filter(attributions, occurrence.rule == X)`; a phoneme
projection is `render(sounds)`; a highlight projection is `attribution.slots`.
All three read the same edge set, so a projection **cannot** disagree with the
engine. ADR-007 §2 adds an independent packaging guard on the same property.

### 5.1 `Rule`

One vocabulary, one name, one place (`model/canon.py`). The `RuleTag` alias is
deleted; the rule-implementation Protocol is renamed `Classifier` and lives in
`engine/` where its `Plan` dependency is legal (ADR-004 §1).

```
IZHAR_HALQI  IZHAR_MUTLAQ  IKHFAA_HAQIQI  IQLAB  IDGHAM_BI_GHUNNAH
IDGHAM_BILA_GHUNNAH  GHUNNAH_MUSHADDADAH
IZHAR_SHAFAWI  IKHFAA_SHAFAWI  IDGHAM_SHAFAWI
IDGHAM_MUTAMATHILAYN  IDGHAM_MUTAQARIBAYN
IDGHAM_MUTAJANISAYN_KAMIL  IDGHAM_MUTAJANISAYN_NAQIS
LAM_SHAMSIYYAH  LAM_QAMARIYYAH
QALQALA_SUGHRA  QALQALA_KUBRA  QALQALA_AKBAR
TAFKHEEM  TARQEEQ  IMALA  TASHIL  ISHMAM
MADD_TABII  MADD_WAJIB_MUTTASIL  MADD_JAIZ_MUNFASIL  MADD_LAZIM
MADD_ARID_LIL_SUKUN  MADD_LEEN  IWAD
WASL_ELISION  WASL_START  ILTIQA_REPAIR  WAQF_ENDING  SILAH  SAKT
PLAIN
```

Changes from the first draft:

- **`SPELLING_EXPANSION` deleted.** Expansion moved into `canon.build`, which
  produces a `Score`, not a `Performance`; no `rules/` module owned the tag and
  nothing could emit it. The spelled slots' sounds come from ordinary rules.
- **`QALQALA` split three ways**, matching the four-way idghām split and the
  frozen tag vocabulary (measured: 3,413 `qalqala_sughra`, 424
  `qalqala_kubra`). Collapsing the degrees was the same failure this set
  indicts at `idgham.py:28`, committed in the opposite direction.
- **`LAM_QAMARIYYAH` added.** The first draft named it in prose while the enum
  had no member, so a projection could answer the shamsiyyah question and not
  its complement.
- **`IMALA`, `TASHIL`, `ISHMAM` added.** Each is a canonical Score fact
  (ADR-001 §3.3–3.4) whose realization still needs an occurrence tag, because
  every attribution's `by` must resolve.
- **`SILAH` added**, covering both the waṣl realization and the pausal drop of
  `Nucleus.Silah` and `Onset.SILAH`.
- **`IWAD` added** as its own member rather than a `Participants` detail.

Each `Rule` member declares a `RuleFamily` (ADR-003 §4.1) and whether it is
classification-only (`TARQEEQ`, the madd family and the iẓhār family produce no
sound of their own).

`Participants` is **held, not deleted**. The simplicity review flagged it as its
own least-certain finding: the frozen baselines carry no trigger letter, but the
public projection API — out of scope here — is where domain-facts §4's
"Classify" view would live, and that view wants the ikhfāʾ trigger. Revisit when
that API is scoped. Variants carry family-specific canonical participants only;
no `detail` dict, no condition tree, no free-form strings.

## 6. Sounds

```python
class NasalPlace(StrEnum):   BILABIAL | ASSIMILATED
class ReleaseKind(StrEnum):  QALQALA

Sound =   Consonant(letter: CanonLetter, geminate: bool,
                    emphatic: bool, nasal: bool)
        | Vowel(quality: Quality, long: bool, emphatic: bool)
        | Nasal(place: NasalPlace, emphatic: bool)
        | Release(kind: ReleaseKind)
```

### 6.1 `Consonant.nasal` is restored

The first draft deleted the nasalization flag, arguing the render map would key
on "the feature bundle". The bundle was `(letter, geminate, emphatic)`, X2
forbids `render` importing `rules` so `Attribution.by` was unreachable, and the
result made **10,667 tokens in the frozen continuous snapshot unreachable** —
measured exactly: `ñ` 4,098, `m̃` 3,254, `w̃` 2,192, `j̃` 1,123. `w̃` and `ww`
(279) are distinct tokens from the same letter with the same gemination.
Fixture 20 could not have passed.

The diagnosis was inverted. `rendering.py:75`'s defect is that the render key is
**not composable** — it returns the nasalized symbol and silently drops
`geminated` and `emphatic`. The fix is a composable key, not a deleted feature.

**Composable does not mean mechanically derived.** The render map is data
(ADR-007 §3): it maps a complete feature tuple to a token, and it may map
`(NOON, geminate=True, nasal=True)` to the single token `ñ`. Any Python-side
rule that concatenated or doubled symbols would break parity, since the snapshot
has 4,098 `ñ` and zero `nn`. The lookup is total over the feature space and
performs no composition of its own.

`NasalPlace` on `Nasal` is separately justified and kept: evidence §7 records
that today's `Nasal` collapses ikhfāʾ ḥaqīqī, iqlāb and ikhfāʾ shafawī into one
value with no rule identity. `BILABIAL` versus `ASSIMILATED` is a place of
articulation — a phonological fact, not a rule name — and it is what makes
`Nasal.emphatic` able to reach output at all.

It is also the **whole content of the realization khilāf** (ADR-006 §3): the
choice a caller makes for iqlāb and ikhfāʾ shafawī is a `NasalPlace`, so it is
set by the `MERGE`-phase rule and never by the renderer. The Hafs default for
all three rules is `ASSIMILATED`, which is what the frozen snapshot contains;
`BILABIAL` is selectable at the 986 measured sites.

One notational consequence, stated so it is not read as a modelling error:
`Nasal(BILABIAL)` and `Consonant(MEEM, nasal=True)` are different sounds that
the current notation renders with the same token `m̃`. The notation is coarser
than the model, which is allowed — the render map is a total lookup and may map
two distinct feature tuples to one symbol. What is *not* allowed is the reverse:
a model that cannot distinguish them.

The inconsistency the domain review names is real and is now removed: the same
"a computed feature must reach output" argument justified `NasalPlace` and was
not applied to the nasalized consonant.

### 6.2 What `Sound` still cannot carry

`Onset.TASHIL` (41:44) and `Quality.ISHMAM` (12:11) are canonical Score facts
with occurrence tags, but `Sound` has no tashīl or ishmām feature. Measured
current output at 41:44:9 is `ʔ a ʔ a ʕ ʒ a m i jj` and at 12:11 the ishmām is
not distinguished, so parity is unaffected and the render map maps both to their
plain tokens today. Stated plainly so it is a decision and not an oversight:
**tashīl and ishmām are recorded and projectable but not currently audible.**
Making either audible is a render-map change plus a `Sound` feature, and needs a
notation that has a symbol for it.

## 7. Totality invariants

Asserted in one pass over a completed `Performance`. These are domain-facts
invariants 3–4 made structural, and they are what `owner.segments.pop(index)`
and `following.segments = [...]` destroy today.

1. Every `Grapheme` appears in exactly one `Spelling`.
2. Every `Sound` appears in exactly one `Hosts` or `Inserted`.
3. Every `Attribution.by` resolves to an `Occurrence`.
4. For every slot and every aspect that has canonical content, there is either
   an attribution or an explicit `Silent` edge. "Has canonical content" is
   defined precisely: `ONSET` always does; `NUCLEUS` does unless
   `nucleus is Silent`. A canonically absent nucleus is not a silenced one and
   requires no edge.
5. Every `MergedInto` edge's sound has a `Hosts` edge with the same `by`.

P4 and P5 of the first draft are gone: the union makes them type facts.

With `Nucleus.Nunated` deleted (ADR-001 §3.5b), **`(slot, aspect)` is now unique
across attributions as well as across effects**. The first draft's only
counter-example was the tanwīn nucleus hosting both a vowel and a nūn on one
aspect, which was the category error A1 removed. The uniqueness is not asserted
as an invariant — a future family could legitimately need two sounds on one
aspect — but its current absence is a signal that the Slot model is coherent,
and a new counter-example should be examined before it is accepted.
