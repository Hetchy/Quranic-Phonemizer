# Projection round-trip, run as a spike

Second half of the phase-1 question. The L1 spike proved the two scripts build
the same Score. This one asks the property the consumers actually buy: **can
`Spelling` be inverted, per script, so that each grapheme can be told what it
contributes?**

Method: instrument `canon.build` to record the downward link (source scalar →
slot, role), run over all 77,433 Uthmani words, and compare per-scalar against
the frozen `word.character_phoneme_mappings` baseline — 601,728 cells with
`role ∈ {base, haraka, madd, tanween}` and `status ∈ {present, dropped,
inserted, replaced}`. Uthmani only; it is the only script with an oracle.

## Result

| | |
|---|---|
| role agreement | **579,064 / 584,249 — 99.11%** |
| slots reached by no grapheme | **5,831** Uthmani / **5,795** IndoPak |
| legacy has a cell, model has none | **5,044** — all the maddah `ٓ` |
| model claims silence, legacy gives phonemes | **100** |

## P1 — `Inert` is two different claims, and ADR-003 §4 conflates them

§4 classifies the maddah as `Inert`: "carries no information the rules do not
supply". For rule derivation that is **true**. For projection it is **false**:
measured, 5,044 maddah scalars are `role: madd`, `status: present`, **with
phonemes**, tagged `madd_lazim` / `madd_wajib_muttasil` / `madd_tabii`. It is
exactly the grapheme a reader highlights to show a madd.

`Inert` currently means both "supplies no canonical fact" and "contributes
nothing you can see". Those are different, and the second is what the use case
cares about. The maddah is the first and not the second.

**Change**: either give `Inert` a mandatory slot link (`near` becomes
non-optional and load-bearing rather than "only so recited writing can place
it"), or add a fifth `Spelling` member — supplies nothing, projects onto a
slot. The first is smaller and probably right.

This is the largest finding, and it lands directly on the stated use case: the
design as written would make a madd-highlighting projection impossible in
Uthmani without reaching around `Spelling`.

## P2 — downward totality is not a law, and is violated by construction

**5,831 Uthmani and 5,795 IndoPak slots have no grapheme pointing at them** —
every one of them a tanwīn nūn slot (`ن silent`). ADR-001 §3.5b says
many-to-many `Spelling` "already supports" one grapheme evidencing two slots.
Measured, it does not merely support it: **5,831 slots per script exist only
if it happens**, and nothing in ADR-008 §1 requires it.

L3 gives upward totality (every scalar resolves to exactly one `Spelling`).
There is no downward counterpart, so a projection cannot be guaranteed to
answer "which glyphs produced this sound".

**Change**: add to ADR-008 §1.2 — *every slot is the target of at least one
`Spelling`*. Fixture: the 8,893 tanwīn words, both scripts. Note the two counts
differ by 36, which is the already-named §6.5 split class.

## P3 — `role` reconstructs, but its vocabulary needs deciding, not inferring

99.11%, and every disagreement class is nameable:

| n | disagreement |
|---:|---|
| 3,063 | tanwīn ʿiwaḍ alef: model `tanween`, legacy `madd` |
| 795 | `base` vs `madd` — carrier-or-slot |
| 758 | marks the model does not classify (seen/ṣād, iqlāb, imāla) which legacy folds into the base cell |
| 338 | `haraka` vs `base` |
| 231 | `madd` vs `base` |

ADR-008 fixture 25's claim — that `role: madd` (53,155) and `role: tanween`
(8,893) need `Grapheme.cls` — holds. But the ʿiwaḍ alef is a genuine
either-way call (`tanween` by origin, `madd` by what it does at waqf), and
3,063 cells hang on it. That belongs in an ADR, not in the implementor's
judgement.

## P4 — 100 dishonest silences, and they are P1 again

93 of them are the `ى` of `هُدًى` / `أَذًى` — `madd/replaced`, tag `madd_iwad`.
The maqsura carries the ʿiwaḍ lengthening at waqf; the model links it to
nothing. Same shape as the maddah: a grapheme that supplies no canonical fact
but is the one a projection must point at.

That the total is only 100 out of 601,728 is the good news — the `Inert`
escape hatch is not being abused at scale. The abuse that matters is the one
the ADR **mandates** (P1), not the ones an implementation drifts into.

## P5 — ADR-008 §3.1's guard has now been run once

Open question 2 says the anti-gaming guard "has never been run" and its
thresholds are undefined. First execution:

| | Uthmani | IndoPak |
|---|---:|---:|
| slots | 286,943 | 286,900 |
| scalars | 638,424 | 645,069 |
| `Inert` scalars | 13,452 | 14,934 |
| `Structural` scalars | 9,152 | 5,674 |

Cross-script asymmetries — the exact signature §3.1 asks for:

- **IndoPak `ي` inert ×1,972**, where Uthmani maps `ي` to a fact almost always
  — the rasm yāʾ standing in for the alef maqsura. Explainable.
- **Uthmani `۟` ×3,988 against IndoPak ×26** — the explicit silent-seat marker.
  Explainable; it is §6's already-named otiose-wāw class.

Neither is a fact being discarded. **The guard produces a small, readable
signal rather than noise**, which is the thing open question 2 doubted. It
still needs a stated threshold, but it is now a working instrument.

## P6 — the worked example of why script-agnosticism matters for projections

The legacy baseline already carries `status: inserted` cells with empty
`chars`: the hamzat al-waṣl helping vowel (10,772 sites, tag
`hamza_wasl_vowel`) and the Allah dagger (5). Uthmani writes no grapheme for
them, so legacy invents a grapheme-less cell.

Under the new design the waṣl helping vowel **is** the slot's own nucleus
(ADR-003 §6.3). So the same slot projects as an *inserted* cell in Uthmani and
as a *present haraka* cell in IndoPak at the 181 sites IndoPak writes it —
from one Score, with no special-casing. That is script-agnosticism paying off
in the projection layer rather than in phonemes, and it is the clearest
argument in the set for why the two scripts are worth carrying.

## Verdict

The inversion works — 99.11% role agreement with no rules engine at all. What
it exposes is not a modelling failure but **two missing laws**: `Inert` must
distinguish "supplies nothing" from "shows nothing" (P1), and every slot must
be reachable from a grapheme (P2). Both are small ADR amendments. Neither
changes the layer structure.

What is still untested: the rule→grapheme join. Reconstructing `tag`
(`madd_tabii`, `ikhfaa_noon`, `qalqala_kubra` …) needs the engine, which is
phase 3. The `Attests(family) + anchor` design is the mechanism, and this run
neither confirms nor refutes it.
