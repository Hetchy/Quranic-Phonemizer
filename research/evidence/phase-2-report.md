# Phase 2 — `write`, and what the round-trip proves

Run last rather than first, which ADR-008 §5 orders the other way. The reason
is in the phase-3–6 report: parity is the number that says whether the rebuild
works, and `write` is a projection whose foundations phase 6 supplies. Running
it now, after `Spelling` exists, made it a smaller job than it would have been.

## 1. The gate is totality, and it is green

ADR-005 §4 asks one thing: **is the canonical layer holding anything no
orthography can express?** A `WriteError` is that failure, and there are none.

| | |
|---|---|
| verses spelled without a `WriteError` | **6,236 / 6,236** |
| verses whose spelling reads back to the same Score | 6,161 / 6,236 — 98.797% |
| `Pen` coverage of `CanonLetter` | total, asserted |

"No fourth layer is needed" stops being a hypothesis (ADR-008 open question 6).

## 2. What the round-trip is *not*

It is not byte-identity with the source, and demanding that would be demanding
the opposite of the design. `read` deliberately discards what the Score does
not need — Uthmani's dagger and an explicit haraka-plus-carrier give the same
slot — so `write` cannot put back what was never kept, and should not pretend
to. The invariant that is both true and worth having is **Score → text →
Score**.

## 3. `write` has no table of its own

The spelling is the script's own inventory read backwards. The inventory
already says *this scalar evidences `Short(A)`*; `write` asks it which scalar
evidences `Short(A)`. A second table would be the same facts written twice and
the two would drift — which is exactly what `data/shared/tajweed.yaml` did
before it was deleted.

Two consequences fell out of that rather than being designed:

- `dagger_host` is already the inventory's word for "this glyph may stand for
  length rather than for itself", so the carrier map is simply the entries the
  letter map takes second. No new declaration.
- A script that spells something a different way needs no code. It needs a
  different inventory, which it already has.

## 4. Residue: 75 verses, four classes

| count | class |
|---|---|
| 71 | `nucleus long→short` |
| 1 | `nucleus long→long` |
| 1 | `nucleus short→short` |
| 1 | `slot count 9v10` |
| 1 | `onset tashil→plain` |

The large class is one shape and is **not** the carrier scalar — spelling the
carrier with Uthmani's bare `ى` rather than the consonantal `ي` was tried and
moved nothing. It is a legal spelling that the length derivation reads back as
short, and it is unclassified beyond that. Stated rather than closed, because
guessing at it is how a rule turns into an exception.

The `tashil→plain` row is honest by construction: `write` spells the base vowel
and leaves the annotation to recited writing, so the tashīl onset is genuinely
dropped. Imāla and ishmām spell as their base quality for the same reason and
happen to read back unchanged.

## 5. What this adds to the foundation

- **A third script is cheaper again.** `write` is inherited, not implemented: a
  new inventory gives a new `Pen` for free.
- **Projections can point back at text.** `render/anchored.py` answers which
  graphemes produced a sound in the *source*; `write` produces text for a Score
  that has no source, which is what recited writing needs (ADR-005 §2).
- **The gate is in CI**, as a ratchet like the other four.
