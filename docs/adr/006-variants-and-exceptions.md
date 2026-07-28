# ADR-006: Variant selection and what may be an exception

Status: **accepted**, amended after the simplicity and domain reviews.
Supersedes archived ADR-001 §§3, 5 and the `exceptions.yaml` schema.

## 1. One mechanism, resolved at two layers

**A khilāf option never names a glyph.** It names a canonical fact or a named
realization; the output symbol follows from the notation and is not a choice the
caller makes. The first draft got this wrong for the second kind, framing it as
a render-alphabet selection between `m̃` and `ŋ`; §3 corrects it.

Split by one test: **which layer does the chosen fact belong to?**

| | Lexical khilāf | Realization khilāf |
|---|---|---|
| example | `س` for `ص` at 4 sites | meem-ghunnah vs ikhfāʾ for iqlāb, 986 sites |
| the value is | a `CanonLetter` | a `NasalPlace` |
| alters | `Slot.letter` — a Score fact | which `Sound` a named rule emits — a Performance fact |
| resolved | `canon.build`, before the Score exists | the `MERGE` phase, in `rules/` |
| consequence | emphasis, vowel colouring, rāʾ look-back all follow | the token follows from the notation |

Both are entries in one `VariantSelection`, read by the pipeline. **`render/`
holds no selection at all** — it maps a complete `Sound` feature tuple to a
token and has no branch a caller can steer. `data/render/<notation>.yaml`
remains, but it is a notation, not a variant.

The two do not collapse to a single resolution point, and should not: the Score
is rule-free, so storing "which nasal the iqlāb rule will choose" in it would
hoist a performance fact into L1 — exactly what R5 deleted `Nucleus.Leen` for.
One mechanism, two layer-appropriate resolution points, zero render-time
branches.

## 2. Lexical khilāf

```python
class KhilafId(StrEnum):                              # closed; §3 adds to it
    SEEN_FOR_SAD | ...
Option = CanonLetter | Onset | Nucleus | NasalPlace   # a canonical or sound value

@dataclass(frozen=True, slots=True)
class KhilafSite:
    id:       KhilafId
    slots:    frozenset[SlotId]
    options:  tuple[Option, ...]         # canonical values, not glyphs
    default:  Option
    skeleton: str                        # loader-validated (ADR-001 §5.1)

VariantSelection = Mapping[KhilafId, Option]          # riwayah default fills gaps
```

The selection is part of the Score's identity (`Score.selection`), so a `SlotId`
is meaningful only under a stated selection. Selecting `س` sets
`Slot.letter = SEEN`, and a render-time swap is **structurally impossible**: the
renderer sees `Sound`s, and a `Sound` cannot name a letter the rules never
received.

Sites are 4, not 3 (evidence §5, corrected): 2:245:14, 7:69:22, 52:37:7 and
88:22:3. Uthmani marks 3 with two different scalars; IndoPak marks 4 with one;
88:22:3 is unmarked in Uthmani. Neither script carries the inventory, so the
site list is a Ledger `Supply` with a domain citation and each present mark is
an `Assert`.

The 30:54 `ضُؔعْفٍ` damma/fatha khilāf that IndoPak flags is **unverified**
(evidence §5) and is not in the catalogue. Adding it requires a domain
reference, not a glyph.

## 3. Realization khilāf

Restores the `iqlab_phoneme` and `ikhfaa_shafawi_phoneme` overrides deleted at
`e0d9fb9` — but as a choice between **named realizations**, not symbols. The
caller selects whether the nasal of iqlāb, and that of ikhfāʾ shafawī, is
realized as a hidden mīm (a bilabial nasal held with ghunnah) or as the generic
ikhfāʾ nasal. That distinction is exactly `NasalPlace` (ADR-002 §6), which is a
`Sound` feature, so the choice is set by the `MERGE`-phase classifier and the
renderer is not involved.

```python
class KhilafId(StrEnum):
    SEEN_FOR_SAD | IQLAB_NASAL | IKHFAA_SHAFAWI_NASAL | ...
```

Measured site counts, all nasal-before-bāʾ:

| Khilāf | Sites | Composition |
|---|---:|---|
| `IQLAB_NASAL` | **503** | 304 tanwīn + bāʾ, 199 nūn sākinah + bāʾ |
| `IKHFAA_SHAFAWI_NASAL` | **483** | mīm sākinah + bāʾ |

The Hafs default is `ASSIMILATED` for both, which is what the frozen snapshot
contains; `BILABIAL` is the alternative. Three things the choice does **not**
touch, checked against the sites:

- **the rule identity** — the occurrence is `IQLAB` or `IKHFAA_SHAFAWI` either
  way, so a tajweed projection is unaffected and ADR-003 §4.1's attestation law
  (which names a `RuleFamily`) cannot be perturbed by it;
- **`Nasal.emphatic`** — bāʾ is not an istiʿlāʾ letter, so `emphatic` is `False`
  at all 986 sites and the two axes never interact;
- **duration** — the ghunnah count is a performance value this model does not
  store (§5).

Nothing in the two realizations falls outside `NasalPlace`. Had it — a
gemination difference, say — `Nasal` would have needed a second feature and the
choice would still not have been a glyph.

This also fixes `render.yaml` mapping `nasal` and `nasal_emphatic` to the same
`ŋ`, which makes the computed `Nasal.emphatic` unable to reach output at all.

**Not in scope here: rule-selection khilāf.** Choosing iẓhār *instead of* idghām
for a nūn, or iẓhār instead of ikhfāʾ shafawī for a mīm, changes which
`Occurrence` fires rather than which `Sound` it emits. That is a third shape;
§5 records that the variant type must be extensible to it without a redesign.

A notation is a versioned file under `data/render/`, **not** under
`data/riwayat/` — it is a property of the output, not of the riwayah, and after
this correction it carries no variant at all. The seam has **two real users**:
the pre-refactor tree shipped `simple_mode.py` over
`resources/simple_phonemes.yaml`, a reduced-vocabulary notation on the restore
list. Recorded so it is not read as speculative and deleted.

## 4. Exceptions

Everything that was `exceptions.yaml` is a Ledger entry (ADR-003 §7). One test
separates a justified entry from a symptom patch:

> **A Ledger entry may only supply or assert a `SlotFact` value that already
> exists in the canonical vocabulary, and the same fact must be derivable by
> rule wherever some script does write it.**

The scope key is `(riwayah, script | *, SlotId)`. `script` is non-`*` only for
source-convention resolution, such as Uthmani's ornamental 2:72 construct, which
IndoPak resolves to a plain hamza (evidence §3.4). Riwayah alone is the wrong
key.

**`Condition` is deleted from the key** (ADR-001 §3.6). The Score is
boundary-free, so there was nowhere for a `WHEN_STOPPING` value to go;
conditionality lives in the canonical vocabulary (`Onset.WASL`, `Onset.SILAH`,
`Nucleus.Silah`, `Nucleus.PausalLong`) or in a `BOUNDARY` rule.

### 4.1 Applying the test — re-derived against measured output

The first draft's table was the set's worked demonstration of the exception
test, and **two of its four rows were wrong**. Both are corrected here, and both
corrections cost a vocabulary member or a second slot — which is the test
working, not failing.

| Candidate | Verdict | Canonical fact |
|---|---|---|
| "at 2:245:14 this slot's `LETTER` is `SEEN`" | **justified** | a `LETTER` fact, derivable from IndoPak's `ۜ` at the other sites |
| "at these 66 slots the `NUCLEUS` is `PausalLong(A)`" | **justified** | Uthmani's `۠` asserts it; the vocabulary member was added rather than the rule bypassed |
| `HafsExceptions.shortened_raa` | **patch** | it emits an emphatic rāʾ plus a vowel, i.e. output vocabulary; the real fact is a `NUCLEUS` length |
| `HafsExceptions.started_ituuni` | **patch, and not a Ledger entry at all** | `ٱئْتُونِى` started on is a sākin hamza after a helping kasra becoming a long ī — a derivable `BOUNDARY` rule (ADR-001 §3.6) |
| `HafsExceptions.stopped_small_ya` | **patch — but the first draft's replacement was also wrong** | see §4.2 |
| `HafsExceptions.second_hamza` | **patch — but the first draft's replacement was also wrong** | see §4.3 |

### 4.2 27:36:8 — the fix is `Onset.SILAH`, not a nucleus value

Measured:

```
joined  : ʔ aː t aː n i j a
stopped : ʔ aː t aː n
```

The first draft said "the real fact is a `WHEN_STOPPING` nucleus value". It is
not. At waqf the pronoun yāʾ's **onset disappears as well as its nucleus**; a
`Supply(NUCLEUS = Silent)` leaves the onset sounding and yields
`ʔ aː t aː n i j`. `Onset` had no absent value, so no `SlotFact` value could
silence an onset either — and no rule could *decide* to, because nothing on the
`Slot` marked the yāʾ as a pronoun ṣilah.

`Onset.SILAH` (ADR-001 §3.3, §3.5) is the canonical fact: an onset that sounds
in connection and vanishes at pause, the exact mirror of `Onset.WASL`. It
indexes as a `Classifier.triggers` key, and a `BOUNDARY` rule silences both
aspects. Justified — and the third worked instance of §4.4's corollary.

### 4.3 41:44 — the fix is a second hamza slot, and tashīl is inaudible

Measured output at 41:44:9 is `ʔ a ʔ a ʕ ʒ a m i jj` — **two hamza slots**.
Uthmani writes `ءَا۬عْجَمِىٌّ`. The first draft said "the real fact is
`COLOUR = TASHIL`", which both under-specifies the Score and cannot reach the
renderer:

- without a canonical `LETTER = HAMZA` plus `NUCLEUS = Short(A)` at the alif's
  position, that alif is an ordinary length carrier and the output is
  `ʔ aː ʕ ʒ …`;
- `Sound` has no tashīl feature, so `TASHIL` alone changes nothing audible.

The canonical facts are therefore two Ledger `Supply` rows — `LETTER = HAMZA`
and `NUCLEUS = Short(A)` on the second slot — plus `Onset.TASHIL` on it. Both
kinds of row are ordinary canonical values, so the entry is justified; but
`TASHIL` is **recorded and projectable, not audible** (ADR-002 §6.2), and saying
so is the honest form of the claim.

### 4.4 The corollary

> If you cannot express your fix as a `SlotFact` value, you have found a missing
> rule or a missing vocabulary member — not an exception.

This set now contains three worked instances: `Nucleus.PausalLong` for the seven
alifs, `Onset.SILAH` for 27:36:8, and the second hamza slot at 41:44. Two of the
three were found by review rather than by authoring, which is the honest record
of how well the test self-applies.

### 4.5 Budget

A `Supply` without a `citation` is permitted but counted. More than ~50 uncited
one-off supplies is a warning to review the derivation-class inventory (R9), not
an automatic reversal. A Ledger growing toward 10⁴ entries means a rule is
missing (ADR-003 §6.4).

## 5. Deferred — the eventual variant surface

**Recorded, not designed.** The variant mechanism will eventually take every
khilāf point as one optional struct passed to `phonemize`, with riwayah
defaults filling omissions. The reference shape is `MoshafAttributes` in
[quran-muaalem](https://github.com/obadx/quran-muaalem), roughly 40 options
across five groups:

| Group | Example | Shape in this design |
|---|---|---|
| per-location letter realization | rāʾ tafkheem / tarqeeq / at waqf | lexical khilāf — a Score fact (§2) |
| rule realization | ikhfāʾ vs meem for the nasal | realization khilāf — a `Sound` feature (§3) |
| **rule selection** | noon/meem iẓhār vs idghām | **third shape, not designed** — changes which `Occurrence` fires |
| hamzat al-waṣl | tasheel / madd | mixed: a Score fact plus, for madd, a duration |
| saken-before-hamz, per-location sakt | taḥqeeq / general vs local sakt; sakt / waqf / idrāj | a Score fact (`sakt_after`) plus a `BoundaryPlan` constraint |

**The requirement is that the variant type is extensible to that shape without a
redesign — not that it covers it now.** `VariantSelection` is already a mapping
from a closed `KhilafId` to a canonical value, read at two pipeline points; the
third shape adds a resolution point in the classifier registry, not a new type.

**Two of that option set are excluded by decisions already made here**, stated
explicitly so they are not reintroduced by copying the list:

1. **Madd lengths are durations** (2 / 3 / 4 / 5 counts). This model stores no
   duration anywhere — domain-facts §5.6 puts performance duration outside the
   phonemizer, and the archived ADR-001 §9 rejected madd timing fields. A madd
   *classification* (`MADD_LAZIM` and the rest) is a `Rule`; a madd *count* is
   not representable and must not become one.
2. **`recitation_speed` and `takbeer` are performance settings**, not
   phonological facts, and are out of scope for this package entirely.

A future ADR-009 owns this. It should not begin before the public projection API
is scoped, because the two share a surface.
