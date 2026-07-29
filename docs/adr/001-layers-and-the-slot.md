# ADR-001: Three layers, one-way reference, and the Slot

Status: **accepted**, amended after the simplicity and domain reviews.
Supersedes archived ADR-001 §§1–2.

## 1. Decision

Three layers and two relations. Reference direction is one-way: `Spelling`
points *up* from a grapheme into the Score; `Attribution` runs from `SlotId`s to
`SoundId`s. **Nothing points down at a grapheme.**

| Layer | Contents | Scope | Varies with |
|---|---|---|---|
| **Inscription** | `Grapheme`, `Spelling`, `StopAdvice` | verse × script | script |
| **Score** | `Slot`, `ScoreWord` | verse × riwayah × variant selection | riwayah, selection |
| **Performance** | `Sound`, `Attribution`, `Occurrence` | one traversal | riwayah, boundary plan, selection |

The Performance layer has **no grapheme field and no script field**. A rule that
wants to inspect a glyph has nowhere to look. Delete the Inscription layer and
only source-text projections break. This is the property the whole design
exists to obtain, and it is structural rather than a tested discipline.

### 1.1 What this design is for

**Phonemes are the test, not the product.** Consumers take script text plus
*projections* — tajweed occurrences linked to graphemes, orthography↔sound
relationships, silent letters with reasons — with phonemes optional or absent
entirely. Byte-identical phonemes across two orthographies is the property that
*proves* the canonical layer is real; it is not what most callers want from it.

Read the rest of this set with that ordering. Where a decision trades projection
fidelity against phoneme convenience, projection fidelity wins — ADR-003 §4.0 is
the worked case, and it went the wrong way in the first draft precisely because
the ordering was not written down.

The clearest single argument for carrying two scripts is a projection argument,
not a phoneme one. The frozen baseline already emits grapheme-less
`status: inserted` cells for the hamzat al-waṣl helping vowel at **10,772
sites** (tag `hamza_wasl_vowel`) and the Allah dagger at 5: Uthmani writes no
glyph, so the legacy view had to invent a cell with empty `chars`. Under
ADR-003 §6.3 that vowel **is** the waṣl slot's own nucleus, so **one Score
projects it as an inserted cell in Uthmani and as an ordinary present-haraka
cell at the 181 sites IndoPak writes it** — same slot, same fact, no
special-casing anywhere. The second script did not just validate the first; it
supplied the evidence that turned an invented cell into a derived one.

## 2. The Score is built by a shared step, not by the adapter

```
   verse text ──riwayat/hafs/scripts/uthmani.read──┐
                                     ├──> canon.build ──> Score
   verse text ──riwayat/hafs/scripts/indopak.read──┘        ▲
                                              │
                        Ledger · lexicon · variant selection · spelling expansion
```

A `ScriptAdapter` extracts **evidence** — graphemes, their `Spelling`
classification, and the canonical facts its own writing system determines
totally. It does not author the Score. Everything a script under-specifies is
supplied by `canon.build`, which is shared, script-independent, and the sole
home of the Ledger, the canonical-skeleton lexicon, muqaṭṭaʿāt spelling and
variant selection.

Two consequences, both load-bearing:

1. **L1 equality (ADR-003 §3) compares the object rules actually read**, not an
   intermediate the adapters happen to agree on.
2. **`Spelling` anchors exist.** The muqaṭṭaʿāt attestations of ADR-003 §2
   anchor at slots created by spelling expansion; if expansion ran after the
   Score, those anchors would dangle.

A third consequence was claimed in the first draft and is **withdrawn**: that
"the adapters stay thin" and spine A's headline cost is not paid. IndoPak has
85 distinct scalars, five polysemous marks, seat folding and combining hamza,
and ADR-003 §6.4 requires every `Evidences` declaration to be justified per site
class. Most of that weight lands in YAML rather than Python, which is the right
place for it, but *how thin* is a phase-1 measurement (ADR-008 §5), not a
premise.

Note the corresponding risk: because `canon.build` is shared, any fact it
supplies is identical across both builds **by construction**, so L1 does not
test it. See ADR-008 §3.1.

## 3. What a Slot is

### 3.1 The criterion

> **Unit-hood criterion.** A canonical position exists where something can
> produce sound *at its own position* in at least one boundary state or reading.
>
> **Length clause.** Contributing length to a neighbouring slot's nucleus is not
> "sound at its own position". Only an onset consonant or an independent vowel
> is.
>
> **Companion principle.** The Score stores recitation facts. Distinct spellings
> of one fact collapse to it, and letter identity is phonological, not glyphic.

The criterion is evaluated over **canonical context, not glyph shape**. A sākin
wāw after a fatha is a leen glide and sounds as a consonant — a slot. A sākin
wāw after a damma is a length carrier — not a slot. The same glyph, decided by
the preceding nucleus. Glyph size is likewise irrelevant: the mini-nūn `ۨ` at
21:88 sounds as an onset and is a slot; the dagger alef never does and is not.

The criterion is prose and therefore cannot itself be an invariant. Its
falsifiable form is ADR-008 §1.1's S1: **every slot hosts a sound on at least
one aspect under at least one of the three renditions.**

### 3.2 The type

```python
SlotId = tuple[VerseRef, int]          # ordinal over SLOTS in the verse, §5

@dataclass(frozen=True, slots=True)
class Slot:
    id:      SlotId
    letter:  CanonLetter               # closed; 30 members
    onset:   Onset                     # closed; 5 members, §3.3
    nucleus: Nucleus                   # closed union, §3.4
    spelled: bool                      # produced by muqaṭṭaʿāt expansion

@dataclass(frozen=True, slots=True)
class ScoreWord:
    location:   Location
    slots:      tuple[Slot, ...]
    sakt_after: bool                   # a recitation fact; advice is not

@dataclass(frozen=True, slots=True)
class Score:
    riwayah:   Riwayah
    words:     tuple[ScoreWord, ...]
    selection: VariantSelection
    digest:    str                     # content hash; the L1 harness emits it
```

**`SlotOrigin` is deleted.** It had no script-independent definition:
`WRITTEN` was specified as "*some script* writes a base letter for it", a
quantifier over the riwayah's whole script set that `canon.build` — which
receives one `Reading` — cannot evaluate. Measured, the classification diverges
by script at the **2,714 Uthmani words carrying a medial `ٱ`**, where IndoPak
writes no alef at all (`وَٱللَّهِ` → `والله`). With `origin` in the L1 comparator
that is thousands of spurious residue rows before any real disagreement is
examined — the same failure class as the R9 seven-alifs misfire.

(The simplicity review argued `LEXICAL` has *no* valid instance. That is not
quite right — the 2,714 medial cases are genuine instances. But they are
instances of a *script-relative* classification, which is the fatal property, so
the conclusion holds and the field goes.)

`spelled: bool` survives because it has one script-independent definition
("produced by `canon/spell.py`") and one named reader (ADR-005 §1's `spelling`
toggle). It is identical across builds by construction, so comparing it is free
and proves nothing (ADR-008 §3.1).

**`ScoreRevision`, `data/riwayat/<r>/migrations/` and invariant S5 are
deleted.** Every artifact holding a `SlotId` across a rebuild — `ledger.yaml`,
`variants.yaml`, the fixtures — is a file in this repository, edited in the same
commit as the change that invalidated it. Git is the migration tool. No external
consumer holds a `SlotId`. `Score.digest` survives as a bare content hash
because ADR-008 §3 already has the harness emitting one. Reinstate the machinery
the day a second consumer holds `SlotId`s across a rebuild, or the day the
curated fallback fires.

### 3.3 Onset

```python
class Onset(StrEnum):
    PLAIN | GEMINATE | WASL | SILAH | TASHIL
```

`Onset` is the closed set of mutually exclusive onset states, and it is where
**boundary-conditional onset presence** lives:

- `WASL` — the onset sounds only at ibtidāʾ (hamzat al-waṣl).
- `SILAH` — the onset sounds only in connection and vanishes at pause. Added
  after the domain review; see §3.5.
- `TASHIL` — a softened hamza (41:44). Absorbed from the deleted `Colouring`.

`WASL` and `SILAH` are exact mirrors, which is why they belong on one axis.

### 3.4 The nucleus vocabulary

```python
class Quality(StrEnum):    A | U | I | IMALA | ISHMAM

Nucleus =   Silent                 # no vowel at this position
          | Short(Quality)
          | Long(Quality)
          | Silah(Quality)         # long in waṣl, absent in waqf
          | PausalLong(Quality)    # short in waṣl, long in waqf
```

- `Silent` is **one value**. Uthmani's absent harakah and IndoPak's `ْ` are two
  spellings of it. This is what kills evidence §2.
- `Silah` (R4) and `PausalLong` encode boundary-conditional *length*; `Onset`
  encodes boundary-conditional *presence*. Together they are the design's single
  mechanism for conditionality — see §3.6.
- **`Nunated` is deleted** (ADR-004 §8). A tanwīn is a `Short(Quality)` nucleus
  on the base slot **plus a following slot** `(letter=NOON, onset=PLAIN,
  nucleus=Silent)`. It folded a consonant into a nucleus, which was a violation
  of §3.1: measured, the tanwīn nūn sounds as a plain `n` at its own position
  wherever iẓhār applies (`عَذَابٌ` → `ʕ a ð aː b u n`, `سَوَآءٌ` →
  `s a w aː ʔ u n`), so by the criterion it was always a slot. See §3.7.
- `Leen` is deleted (R5): leen is a `LENGTH`-phase occurrence, not a nucleus.

**`Colouring` and `Slot.colour` are deleted.** A `frozenset` on ~330,000 slots
carried information present at three words — measured, U+06EC tashīl ×1, U+06EB
ishmām ×1, U+06EA imāla ×1, all Uthmani-only, none in IndoPak. This ADR already
routed imāla into `Quality` on the argument that it is a distinct vowel rather
than a modification of one; the same argument routes ishmām into `Quality` and
tashīl into `Onset`, both already closed sets of mutually exclusive states. No
site carries two colourings and none can.

### 3.5 `Onset.SILAH` — the third instance of the exception test

Measured at 27:36:8 `ءَاتَىٰنِۧ`:

```
joined  : ʔ aː t aː n i j a
stopped : ʔ aː t aː n
```

At waqf the pronoun yāʾ's **onset disappears as well as its nucleus**. The first
draft of ADR-006 §4.1 called this "a `WHEN_STOPPING` nucleus value", which is
wrong: silencing only the nucleus yields `ʔ aː t aː n i j`. No `Nucleus` value
and no pre-amendment `Onset` value expresses it, and no rule could *decide* to
emit the double silence, because nothing on the `Slot` marked the yāʾ as a
pronoun ṣilah.

`Onset.SILAH` is that mark. It is a canonical Score fact, it indexes as a
`Classifier.triggers` key, and a `BOUNDARY` rule silences both aspects at pause.
This is the exception test working for the third time: a fix that could not be
expressed meant a missing vocabulary member, not a licence to patch.

**The glyph does not supply it.** Uthmani's `ۧ` U+06E7 occurs at 39 sites, and
only 27:36:8 is ṣilah; the other 38 are an ordinary long ī (`إِبْرَٰهِـۧمَ`,
`ٱلنَّبِيِّـۧنَ`). It is the sixth polysemous mark on the running list
(ADR-003 §6.6). `Onset.SILAH` is therefore a Ledger `Supply` at one slot with a
domain citation, and the long-ī derivation covers the rest — not a scalar
mapping. An earlier draft of this section read the scalar as monosemous, which
would have mis-derived 38 sites.

### 3.5b Tanwīn is two slots (A1, ruled)

```
عَذَابٌ   →  [ʕ Short(A)] [ð Long(A)] [b Short(U)] [n Silent]
             ʕ a ð aː b u n
```

One tanwīn grapheme evidences facts on **two** slots — `NUCLEUS = Short(q)` on
the base slot, and `LETTER = NOON` + `NUCLEUS = Silent` on a new following slot.
Many-to-many `Spelling` already supports this; three compact muqaṭṭaʿāt
graphemes fan to seven slots.

What this buys, beyond satisfying E1 (ADR-004 §8):

- **The nūn/tanwīn family has one shape.** Every rule triggers on a `NOON` slot
  with `nucleus = Silent` and merges its `ONSET`. Tanwīn and nūn sākinah become
  literally the same rule with the same trigger, which is what domain-facts §5.1
  says they are.
- **One fewer insertion.** The iltiqāʾ kasra after tanwīn is no longer a
  slot-less insert; it is the nūn slot's own nucleus. Only the 3:1 fatha remains
  genuinely slot-less.
- **IndoPak's `ࣙ` is explained.** ADR-003 §6.5's 54 sites depict exactly a
  nūn-plus-kasra on the following word, which is now an ordinary `Evidences`
  row rather than an attestation of an insertion.
- ʿiwaḍ at waqf is `Relength` on the base plus `Silence` on the nūn slot;
  dammatan and kasratan at waqf are two `Silence`s.

Cost: +1 slot on the 8,893 words carrying tanwīn, and `write` must spell a slot
*pair* as one grapheme — likewise already required for muqaṭṭaʿāt. Both are free
today because no data file exists. L1 is unaffected: both scripts write the same
tanwīn scalars (U+064B–D), 8,893 Uthmani words against 8,840 IndoPak, and the
gap is §6.5's already-named 55-word class.

### 3.6 One conditionality mechanism

`Condition` (`ALWAYS | WHEN_STARTING | WHEN_STOPPING`) is **deleted** from the
Ledger key, from the exception scope key and from invariant I3. The Score is
boundary-free and built once, so `canon.build` had nowhere to put a
`WHEN_STOPPING` value; the loader accepted entries the builder could not
consume, and every worked example in the set was `ALWAYS`.

Conditionality lives in exactly one place: **the canonical vocabulary**.

| Conditional fact | Member |
|---|---|
| onset sounds only when starting | `Onset.WASL` |
| onset sounds only when connecting | `Onset.SILAH` |
| vowel long when connecting, absent at pause | `Nucleus.Silah` |
| vowel short when connecting, long at pause | `Nucleus.PausalLong` |
| everything else | a `BOUNDARY`-phase rule |

`HafsExceptions.started_ituuni` retires under the last row: `ٱئْتُونِى` started
on is a sākin hamza after a helping kasra becoming a long ī — a derivable
boundary rule, not a location fact.

## 4. The four omissions, as consequences

| Omission | Generated by |
|---|---|
| No carrier slots | the criterion + length clause |
| No `ALIF_MAQSURA`, no `ALEF_WASLA` in `CanonLetter` | the companion principle |
| No bare-vs-sukūn | the companion principle |
| No madd mark | ADR-003 L3 — the maddah evidences no fact at all |

`CanonLetter` has 30 members: the 28 letters of the alphabet, plus `HAMZA`,
plus `TAA_MARBUTA` — the latter retained because its waṣl/waqf alternation is
canonical and rasm-conditioned. That is today's 32-member `Letter` enum minus
`ALEF_WASLA` (an onset, not a letter) and `ALIF_MAQSURA` (a glyph, not a
letter). `ى`, `ی`, `ے` fold to `YA`; hamzat al-waṣl is
`letter=HAMZA, onset=WASL`; hamza seats fold into the hamza's letter identity.

## 5. Addressing

`SlotId = (VerseRef, ordinal)`, the ordinal counting slots across the **verse**,
not the word.

Verse-scoping is a change from the first draft, adopted because the word-scoped
signature was already insufficient for the two scripts in hand: IndoPak's
`ࣙ` U+08D9 carries evidence about the *previous* word at 54 sites
(ADR-003 §6.5), which `read(text, at: Location)` cannot see. It also removes a
latent break — see §5.2. It costs nothing today because no data file exists yet.

**Verse scope is necessary but not sufficient**, and the first draft overstated
it. Measured, of those 54 sites **34 have the mark in the same verse and 20 have
it in the next**. `canon.build` therefore takes the verse's `Reading` plus a
bounded **one-word right context**:

```python
def build(reading: Reading, right: Reading | None, ledger, lexicon,
          selection) -> tuple[ScoreWord, ...]: ...
```

One word, not one verse and not unbounded, because domain-facts §3 already fixes
the ceiling — *no rule needs more than one-word lookahead*. The same bound now
governs Score construction. The verse remains the addressing container; the
lookahead is evidence-only and contributes no slots.

It survives a script change because both scripts must produce the same slot
tuple (ADR-003 §3). Measured at 2:9:4: `ءَامَنُوا۟` has six Uthmani base letters
and `اٰمَنُوْا` has five IndoPak ones, and both are **three** slots —
`[ʔ aː][m a][n uː]`, output `ʔ aː m a n uː`. The otiose alef is not a fourth
slot; the length clause excludes it and ADR-003 §4 classifies it `Decorates`. (The
first draft said four slots and listed a `[seat]`, contradicting three other
sections of this set.)

**Every stable reference in the system is a `SlotId`**: occurrence participants,
Ledger keys, khilāf sites, effect targets, insertion anchors, test fixtures.
Never a `SoundId` (request-local), never a byte offset, never "the nth
occurrence of glyph X".

`GraphemeId = (VerseRef, offset)` and **is position-ordered**: `offset` is the
codepoint index within the verse text, so the graphemes of a verse in
`GraphemeId` order reproduce the source exactly. Fixture 1's round-trip depends
on this — measured, 4,575 Uthmani words contain an internal space and 6,404
contain a tatweel, and `Structural` carries no position of its own.

`SoundId = (VerseRef, seq)` is request-local and valid only inside one
`Performance`, which carries the `VariantSelection` and `BoundaryPlan` that
produced it.

### 5.1 Ledger keys stay human-checkable

A verse-scoped ordinal is robust and unreadable. Every Ledger and variant entry
therefore carries a mandatory `skeleton` field — the canonical letters of the
word containing the slot — which the loader validates against the Score. It
catches ordinal drift and makes `ledger.yaml` reviewable by a human. Entries may
be written with a word-relative alias (`2:245:14#5`) which the loader resolves
and normalizes.

### 5.2 Recorded limit — and a correction

Across riwayāt, differing word division is a **non-issue**: Warsh has its own
`Riwayah`, corpus and `Location`s. The first draft conflated this with the
within-riwayah case; they are different problems.

Within a riwayah, a third witness that joins or splits words differently is a
real break — `ScoreWord` is `Location`-keyed and is itself the unit that would
stop aligning. Verse-scoping `read`, `canon.build` and slot ordinals (§5) moves
the break from "every signature, every data file, every fixture" to "the
`ScoreWord` container only".

The correction the first draft owed: the two present Hafs witnesses agree on
word division **because the importer forced them to**.
`tools/import_indopak_source.py` splits 37:130 `اِلْيَاسِيْنَ` into two words to
match Uthmani. The premise is constructed, not observed.

## 6. Consequences

- Rules cannot read orthography. The bug class represented by
  `noon_tanween.py:17` becomes unwriteable.
- The Score is **selection-dependent** (ADR-006).
- The Score is **boundary-free**. Everything in domain-facts §7 is a
  Performance fact; §3.6's vocabulary members name boundary-*conditional* values
  without making the Score boundary-dependent.
- L1 equality (ADR-008 §3) is the proof obligation this ADR creates. It is not
  discharged.
