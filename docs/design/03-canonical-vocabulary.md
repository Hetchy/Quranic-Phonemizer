# 03 - The canonical vocabulary, before projections fix it

Status: **resolved**, pending the code changes in §7. The audit this document
asked for has been done; the census is §2-§5 and the decisions are §6.
Blocks: [projections/01-design](projections/01-design.md).

## 1. Why this one had a deadline

A `Slot` is what a projection projects. Once `Reading` is public, `Onset` and
`SlotOrigin` are in a consumer's `match` statement and changing them is a
breaking release. The census below was the precondition.

The audit rejected refactoring `SlotOrigin` on the grounds that no audited Warsh
case needs two of its axes at once. That rejection was about *urgency*. What
follows answers the correctness question it deferred.

---

## 2. Census: `SlotOrigin`

Every branch in the package, and which of the three questions it asks.

| Site | Member | Question |
|---|---|---|
| `orthography/write.py:151,155` | `NUNATION` | is this a tanween noon? |
| `rules/boundary.py:196,254,262` | `NUNATION` | is this a tanween noon? |
| `orthography/write.py:162,166` | `SPELLED` | is this part of a letter name? |
| `rules/noon_sakinah.py:80,81` | `SPELLED` | is this part of a letter name? |
| `model/canon.py:178` (`.spelled`) | `SPELLED` | is this part of a letter name? |
| -- | `WRITTEN` | **read by nothing** |

Ten branches, each asking exactly one question. `WRITTEN` has zero readers and
means "neither of the other two". The enum is also hashed into the round-trip
digest at `canon/assemble.py:61` as `slot.origin.value`.

**The decomposition is mechanical.**

## 3. Census: `Annotation` against sound

| Member | Read by | Emits | Sound-neutral? |
|---|---|---|---|
| `IMALA` | `rules/annotation.py:52`, `orthography/write.py:44,202` | a classification-only `Verdict` with no effects | yes |
| `ISHMAM` | `rules/annotation.py:54` | a classification-only `Verdict` with no effects | yes |
| `DIVINE_NAME` | `canon/passes.py:119` (set), `rules/tafkheem.py:135` (read) | gates a `Recolour(EMPHATIC)` on the lam | **no** |

`DIVINE_NAME` is alone, as suspected. The documented invariant "a canonical fact
that changes no sound" is false for exactly one member.

The important observation the original draft did not make: **the invariant was
never what let a projection ignore annotations when computing phonemes.** A
projection computes phonemes from the `Performance`, which is a list of `Sound`s
-- it never reads `Slot.annotations` at all. The promise was load-bearing for
nothing.

## 4. Census: `Onset`

Two axes in one field: manner (`PLAIN`, `GEMINATE`, `TASHIL`) and presence
(`WASL`, `SILAH`).

Producers, which is where the impossible combinations are decided:

| Member | Produced by | Population |
|---|---|---|
| `GEMINATE` | `canon/derive/gemination.py` (the shadda) | any consonant |
| `WASL` | `canon/derive/wasl.py:172` (`ٱ`) | a prosthetic hamza only |
| `TASHIL` | the inventory (`orthography/inventory.py:272`) | a hamza only |
| `SILAH` | `data/riwayat/hafs/ledger.yaml:60` -- **one slot**, `27:36:8#3` | the yaa ithbat |
| `PLAIN` | the default, and `derive/tanween.py`, `canon/juncture.py` | everything else |

Every manner-presence pair, with a reason:

| | `PLAIN` | `GEMINATE` | `TASHIL` |
|---|---|---|---|
| present | ordinary | ordinary | the two hamzas of `ءَاعْجَمِىٌّ` 41:44 |
| `WASL` | ordinary | impossible in Hafs: the prosthetic hamza is never doubled | impossible: tashil is a hamza softening, wasl a hamza deletion |
| `SILAH` | the 27:36 yaa | impossible in Hafs: nothing doubles a dropped glide | impossible: the silah letter is never a hamza |

Every impossibility is "impossible in Hafs" or "impossible by the definition of
one of the two members". Only the middle column's first row is a genuine
riwayah-scoped claim, and Warsh has no attested geminate prosthetic hamza
either. **No case in the domain needs both axes at once.**

Worth recording because grepping the package for a producer finds none:
`Onset.SILAH` is set from data, not code. It is live.

## 5. Census: `PausalLong` and `Silah` as nucleus kinds

Question 4 asked whether a `PausalLong` nucleus is ever correct at a slot the
plan does not stop at, on the theory that if it never is, the kind is a cache of
a boundary fact.

It is never correct at a joined slot -- `rules/boundary.py:78` only realizes the
long vowel under `boundaries.stopped_on(word)`. But the conclusion does not
follow, for a reason the original draft missed:

**The boundary rule cannot derive the fact.** Which alifs are the seven, and
which haa carries a silah, are *lexical* facts, decided in `canon/derive/` from
the script and the lexicon before any boundary is known. If the nucleus were
plain, the boundary rule would need the lexicon, which would put lexical lookup
inside `rules/` and break the layering ADR-001 sets up.

So the fact belongs on the slot. What is wrong is only the *reading* of
`NucleusKind` as a single axis of inherent length. It has two:

- inherent: `SILENT`, `SHORT`, `LONG`
- boundary-conditional: `SILAH` (long joined, absent at pause), `PAUSAL_LONG`
  (short joined, long at pause)

No code change. `Reading` publishes `conditional: bool` so no consumer has to
learn this (projections/01-design §3.2).

---

## 6. Decisions

**D1 -- `SlotOrigin` decomposes into two booleans.** `nunation: bool` and
`spelled: bool` on `Slot`, replacing `origin`. Every one of the ten branches
converts one-for-one; `WRITTEN` is `not nunation and not spelled` and nothing
asks. `Slot.spelled` stays as a field instead of a property. The digest at
`canon/assemble.py:61` takes the two flags in place of `origin.value`, which
changes every digest -- so the ledger fixtures regenerate in the same commit.

Rejected: keeping the enum and documenting the pair as impossible. A slot cannot
be both spelled and nunation *today*, but nothing in the domain says a spelled
letter name may never end in tanween, and the enum makes that unsayable for no
gain.

**D2 -- `Annotation` is renamed `SlotTag`, and the sound-neutrality promise is
dropped.** A `SlotTag` is a tag a slot carries, with no claim about sound.
`DIVINE_NAME` keeps its membership; §3 shows the promise it violated bought
nothing. The guarantee consumers actually need -- "phonemes are computed without
reading tags" -- is delivered by the layering, since the phoneme sequence comes
from `Performance` and `Performance` has no tag field.

Rejected: moving `DIVINE_NAME` out. It would need a `lexeme identity` field that
exists for one member, which is a worse trade than an honest type name.

**D3 -- `Onset` is not split.** The census found no possible manner-presence
combination the enum cannot express, and every impossibility has a domain
reason recorded in §4's table. Splitting buys nothing today and the projection
publishes `geminate` and `prosthetic` as independent booleans regardless
(projections/01-design §3.2), so no consumer inherits the coupling.

This is a reversal of the acceptance criterion "every `Slot` field answers one
question", and deliberately: the criterion is a heuristic for finding fields
that cannot say something true. §4 establishes there is nothing true `Onset`
cannot say. The heuristic loses to the evidence.

Reopens if: a riwayah needs a geminate prosthetic hamza, or `TASHIL` grows a
second member (Warsh's `naql` is a candidate, and it is a *deletion*, so it
would sit on the presence axis with `WASL`).

**D4 -- `PausalLong` and `Silah` stay.** §5. Documented as the
boundary-conditional half of `NucleusKind`, with a docstring that says so, and
the projection hides the distinction behind one boolean.

---

## 7. What lands

| | Change | Size |
|---|---|---|
| D1 | `SlotOrigin` -> `nunation` + `spelled`; 10 branches; digest; fixtures | medium |
| D2 | `Annotation` -> `SlotTag`; rename only | small |
| D3 | none | -- |
| D4 | `NucleusKind` docstring names the two axes | trivial |

Two further changes are required by the projection design and are recorded
there rather than here, because they are about `Performance`, not the canonical
vocabulary: labelling `Participants` (projections/01-design §4, C1) and keeping
the modifier edge (C2).

## 8. Acceptance, restated

- No enum member means "none of the others". Met by D1; `PLAIN` in `Onset` is
  the articulated default, not an absence.
- Any type documented as sound-neutral is sound-neutral. Met by D2, which
  removes the false documentation rather than the true member.
- Every field a *projection* exposes answers one question. Met by
  projections/01-design §3.2, which is where the criterion belongs -- `Slot` is
  internal and may carry a compressed enum if the compression is proven lossless.
