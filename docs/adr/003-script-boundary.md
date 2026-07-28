# ADR-003: The script boundary — adapters, Spelling, and the Ledger

Status: **accepted**, amended after the simplicity and domain reviews.
Supersedes archived ADR-001 §2 "Canonical spelling" and ADR-003's
data-ownership map.

## 1. Decision

A `ScriptAdapter` extracts evidence; shared code builds the Score. Three laws
govern the boundary. Facts a script under-specifies come from a derivation or
from the **Ledger**, never from the presence of a glyph at a location.

```python
class ScriptAdapter(Protocol):
    script: Script                                  # closed enum per riwayah

    def read(self, text: str, at: VerseRef) -> Reading: ...
    def write(self, slots: Sequence[Slot], style: SpellStyle) -> str: ...

@dataclass(frozen=True, slots=True)
class Evidence:
    slot_hint: int                       # index into the draft slot sequence
    fact:      SlotFact
    value:     object                    # a canonical value of that fact

@dataclass(frozen=True, slots=True)
class Reading:
    verse:     VerseRef
    graphemes: tuple[Grapheme, ...]
    spellings: tuple[Spelling, ...]
    evidence:  tuple[Evidence, ...]
    advice:    tuple[StopAdvice | None, ...]   # per word; Inscription layer
```

**`read` is verse-scoped, not word-scoped** (ADR-001 §5). The word-scoped
signature was already insufficient for the two scripts in hand — see §6.5 — and
verse-scoping costs nothing today.

## 2. Why the Score is built after `read`, not inside it

R2 requires a grapheme to be able to attest at an **anchor `SlotId`**. IndoPak
writes such a grapheme inside compact muqaṭṭaʿāt words — measured, at **ten**
sites, not the three the convergence reviews cite:

| Sites | Uthmani | IndoPak | Attests |
|---|---|---|---|
| 2:1, 29:1, 30:1, 31:1, 32:1 | `الٓمٓ` | `ال࢜مّ࢜` | shadda on mīm: assimilation between the spelled names *lām* → *mīm* |
| 3:1 | `الٓمٓ` | `ال࢜مَّ࢜` | the same shadda **plus** a fatha — the 3:1 iltiqāʾ repair of evidence §4.2 |
| 7:1 | `الٓمٓصٓ` | `ال࢜مّ࢜ص࢜` | same shadda |
| 13:1 | `الٓمٓر` | `ال࢜مّ࢜رٰࣞ` | same shadda, plus a dagger evidencing `رَا` |
| 26:1, 28:1 | `طسٓمٓ` | `طٰس࢜مّ࢜` | shadda on mīm: assimilation of *sīn*'s final nūn → *mīm* |

The anchor slots exist only after spelling expansion. If expansion ran as a rule
phase, those anchors would dangle and R2 would be unenforceable at the sites
that motivated it. Expansion, the Ledger, the lexicon and variant selection all
run in `canon.build`, before the Score exists and before any rule runs.

## 3. The three laws

**L1 — Score equality.** For one riwayah and one variant selection, every script
of that riwayah must produce the **identical `Score`**. Equality is over the
full `Slot` tuple — `letter`, `onset`, `nucleus`, `spelled` — at every slot.
This is 77,433 words of assertions (ADR-008 §3), not a design claim.
`SlotOrigin` is gone from both the type and the comparator (ADR-001 §3.2).

**L2 — One canonical supplier per fact (R8).** Within one `(script → Score)`
build there is **exactly one `Supply`** for each `(SlotId, SlotFact)`, from a
script-independent derivation or a typed Ledger entry, and **zero or more**
script-scoped `Assert`s. Disagreement names the supplier and the asserting
witness and fails the build.

*Scope, stated because the first draft left it undefined.* **L2 and I3 are
per-build.** Both scripts' declared conventions are legitimate suppliers within
their own build; L1 is the cross-script check that they agreed. I3's loader
check is over `ledger.yaml` only.

*What R8's slogan actually means.* The supplier is the **derivation**, not the
glyph. A script convention — "in Uthmani, U+064E on a slot's base evidences
`NUCLEUS = Short(A)`" — is a total function from that script's writing system to
a fact, declared once in the inventory, and is a legitimate `Supply`. What L2
forbids is a *particular glyph occurrence at a particular location* being the
authority for that location. Honesty requires adding what the first draft
elided: via declared conventions, **present glyphs supply the large majority of
canonical facts**, and the Ledger covers the residue. "A present glyph is never
the canonical supplier" is true of the Ledger's domain and false as a
description of the whole pipeline.

**L3 — Closed vocabulary.** Every scalar of every verse resolves to exactly one
`Spelling`. An unclassified scalar is a parse error. This kills the current
`script.yaml: structural:` dumping ground, which silently discards `ۜ`, `ۣ` and
`۫`, and kills `SourceMark.SECOND_HAMZA`, which names one location's *outcome*
inside the script layer.

## 4. `Spelling` (R2)

A tagged union, four members. The first draft's flat record with a `SlotFact`
had no legal classification for a grapheme that witnesses a *performance*
outcome, so the IndoPak adapter hard-failed at 2:1:1 on real input.

```python
class SlotFact(StrEnum):  LETTER | ONSET | NUCLEUS | SAKT

Spelling =  Evidences(grapheme: GraphemeId, slot: SlotId, fact: SlotFact)
          | Attests(grapheme: GraphemeId, family: RuleFamily, anchor: SlotId)
          | Decorates(grapheme: GraphemeId, slot: SlotId)      # slot is MANDATORY
          | Structural(grapheme: GraphemeId)
```

- **`Evidences`** — the grapheme supplies or asserts a canonical fact of a named
  slot. (`COLOUR` is gone: tashīl folded into `Onset`, ishmām into `Quality`.)
- **`Attests`** — the grapheme witnesses a performance outcome. See §4.1.
- **`Decorates`** — the grapheme supplies **no canonical fact** but is bound to a
  named slot, so a projection can point at it: the maddah `ٓ`/`࢜`, the silence
  zero `۟`, the otiose alef of `قَالُوا۟`, the ʿiwaḍ maqsura seat of `هُدًى`.
- **`Structural`** — not part of the word: space, **tatweel**, sajdah, hizb,
  verse marker, and the stop-sign scalars, which are classified here **and**
  mapped to `StopAdvice` in the inventory's `advice:` table (ADR-007 §3).

### 4.0 Why `Inert` became `Decorates` with a mandatory slot

`Inert` asserted two different things at once — *supplies no fact* and
*contributes nothing you can see* — and the second is false for its largest
member. Measured against the frozen baseline: **5,044 maddah scalars are
`role: madd`, `status: present`, with phonemes**, tagged `madd_lazim` /
`madd_wajib_muttasil` / `madd_tabii`. It is precisely the glyph a reader
highlights to see a madd. A further **93** are the `ى` of `هُدًى` / `أَذًى`,
`madd/replaced`, tag `madd_iwad` — 93 of the run's 100 total dishonest silences.
Under the first draft's `near: SlotId | None`, a madd-highlighting projection in
Uthmani was impossible without reaching around `Spelling`.

For *fact supply* the old text was right and is unchanged: the maddah carries no
information the rules do not supply (domain-facts §5.6). Only the projection
claim was wrong.

**Decision: mandatory slot link, not a fifth `Spelling` member.** Three reasons.

1. **The fifth member would have no instances.** It would distinguish "supplies
   nothing but shows something" from "supplies nothing and shows nothing" — and
   once the tatweel is correctly `Structural` (it is a typographic joiner, no
   more part of the word than the 4,575 internal spaces already classified
   there), the second class is empty in both corpora. A union member with no
   instances is not an abstraction; that is the argument that deleted
   `SlotOrigin.LEXICAL`, applied consistently.
2. **`Grapheme.cls` already carries the axis a fifth member would encode.**
   `MADD_SIGN`, `SILENCE_SIGN`, `LENGTH_CARRIER` (ADR-007 §6) say *what kind* of
   non-supplying grapheme this is. A fifth `Spelling` member would duplicate it.
3. **It makes §4.2's downward-totality law stateable without a hole**, exactly
   where projections need it most: every `Spelling` except `Structural` names a
   slot, full stop.

The rename is not cosmetic. `Inert` misled the author of this ADR set into a
wrong call on the largest grapheme class it governs, which is direct evidence
against the name under ADR-007 convention 1.

A mark may constrain the classification of its host grapheme: Uthmani's `۟`
requires its host to classify `Decorates`, and a derivation saying otherwise
raises. This is an adapter-internal consistency check, not a fifth relation.

### 4.2 Downward totality is a law

L3 gives *upward* totality — every scalar resolves to exactly one `Spelling`.
There was no counterpart, so nothing guaranteed a projection could answer "which
glyphs produced this sound".

> **Every slot is the target of at least one `Spelling`.**

Measured, the first draft violated this **by construction**: 5,831 Uthmani and
5,795 IndoPak slots were reached by no grapheme at all, every one of them a
tanwīn nūn. ADR-001 §3.5b said many-to-many `Spelling` "already supports" one
grapheme evidencing two slots; those slots *exist only if it happens*, and
nothing required it. The law now does, and the fixture is the 8,893 tanwīn words
in both scripts (ADR-008 fixture 27).

The 5,831/5,795 difference of 36 is **not** explained by §6.5's class, whose
sizes are 54 and 1. It is an unexplained artifact of the spike's own
instrumentation and is recorded as such rather than attributed.

### 4.3 Attestation names a family, and is stated over slots

The first draft typed attestation as `Attests(grapheme, rule: Rule, anchor)`.
That relocates tajweed classification into the adapter: measured, word-initial
shadda spans **at least seven** distinct `Rule` members, and choosing between
them requires the previous word's final letter class, the bi-/bila-ghunnah
split, and the idghām pair tables.

| Preceding word ends in | IndoPak | Uthmani |
|---|---:|---:|
| tanwīn | 3,407 | 2,089 |
| nūn | 1,360 | 624 |
| mīm | 821 | 833 |
| lām | 110 | 110 |
| alif, tāʾ, bāʾ, dāl, rāʾ, dhāl | 59 | 61 |

`RuleFamily` is a closed enum of what an adapter can genuinely see:

```python
class RuleFamily(StrEnum):
    ASSIMILATION | NASALIZATION | INSERTION | LENGTHENING | EMPHASIS | RELEASE
```

A word-initial shadda attests `ASSIMILATION` — "something merged into this
onset" — which needs no tajweed knowledge at all. Every `Rule` member declares
its family (ADR-002 §5.1), and the family split also gives projections a coarse
grouping for free.

> **The attestation law (A1).** If a script attests family `F` at anchor slot
> `s`, the engine must produce an occurrence of **some** rule in `F` whose
> participants include `s`, evaluated under the **all-join boundary plan**.
> Disagreement raises.

#### The shadda trigger is a Performance predicate

The first draft's inventory keyed on `"ّ@word_initial"` — a glyph position, both
too narrow and the wrong kind of statement. An intermediate proposal restated it
over the Score ("the predecessor slot's nucleus is `Silent`"). Measured, the two
readings differ by 2,440 sites and **neither the positional nor the Score
formulation is correct**:

| trigger evaluated on | Uthmani | IndoPak |
|---|---:|---:|
| word-initial only | 3,722 | 5,761 |
| the **Score** — predecessor slot's nucleus is `Silent` | 9,048 | 11,100 |
| the **waṣl performance** — the preceding *sound* is silent | **11,488** | **13,538** |

The 2,440-site gap is exactly the article before a geminated lām: in the Score
the waṣl slot carries its helping vowel (`Short(A)`, which §6.3 makes an
obligation), so the predecessor is not `Silent`; in waṣl that vowel is elided,
so it is.

> A shadda attests `ASSIMILATION` when, **under the all-join boundary plan, the
> sound preceding it is silent**, and the shadda's own slot is not canonically
> `Onset.GEMINATE`.

This is a **Performance-level predicate**, which is consistent with the two
things §4.1 already said — property 2 evaluates attestation in waṣl, and
invariant A1 evaluates under the all-join plan. Stating it at the Score level
would have been a category error, and it is worth naming the risk that avoids:
**A2 is not evidence that the Score needs a new field.** The Score is unchanged.

The word-internal set is not noise. It decomposes into named families — lām
shamsiyyah, the article before a geminated lām, form-VIII assimilated tāʾ
(`فَٱتَّقُوا۟`), and idghām mutajānisayn including 5:28:2 `بَسَطْتَ`/`بَسَطْتَّ` and
77:20:2 `نَخْلُقكُّم`. **The per-family counts given in an earlier draft
(5,283 / 1,455 / 260 / ~52) were derived from a letter-unit approximation that
matches neither reading above and do not survive; they are withdrawn.** The
families are real, the split between them is a phase-1 measurement once the
`MERGE` phase can produce the all-join plan.

*Method note.* A count over letter *units* rather than sounds adds ~93 false
hits (`دَآبَّةٍ`, `ٱلضَّآلِّينَ`) where a bare length carrier looks silent. Under
the predicate the alif is not a sound-bearing position at all, so the rule
correctly does not fire — the correctness depends on the length-carrier and
article derivations already being right.

Three properties, each deliberate:

1. **One-directional.** Attestation ⇒ occurrence, never the reverse. The
   word-initial subset agrees on 3,534 words, with 2,227 IndoPak-only (2:7:9
   `غِشَاوَةٌ` → 2:7:10 `وَّلَهُمْ`, Uthmani `وَلَهُمْ`) and 188 Uthmani-only
   (2:105:1 `مَّا`, IndoPak `مَا`). Neither inventory is a superset; a
   bidirectional law fails on 2,415 words.
2. **Evaluated in waṣl.** A mushaf writes the connected reading.
3. **Not a Score fact.** Word-initial gemination is waṣl-only — it drops at
   ibtidāʾ — so `ONSET = GEMINATE` would be false, and the 2,415-word
   disagreement would land in the L1 residue the reversal trigger reads. The
   `not canonically GEMINATE` clause is what separates this from root gemination
   (`مُحَمَّد`), where the preceding slot is voweled and the shadda is an
   ordinary `Evidences(ONSET)`.

## 5. Stop advice leaves the Score (R3)

Measured over both corpora, counting the stop-sign scalars each script declares:

| | Count |
|---|---:|
| words carrying a sign in **both** scripts | 4,025 |
| Uthmani only | 334 |
| IndoPak only | 1,098 |
| of the 4,025, **identical scalar set** | **333** |

IndoPak's `ؕ` U+0615 absorbs Uthmani's `ۚ` (optional stop, 1,578), `ۖ`
(preferred continue, 673) **and** `ۗ` (preferred stop, 575) — three classes into
one. A further 599 map `ۖ` → `ۚ`.

Advice is a mushaf convention, legitimately script-scoped.

> **The stop-sign inventory is per `(riwayah, script)`. There is no shared
> stop-sign table.** It lives in
> `data/riwayat/<r>/scripts/<script>.yaml` beside that script's other scalars
> (ADR-007 §3), never in `data/shared/`, so there is nothing for two scripts to
> conflict over. `StopAdvice` — the *class* vocabulary — is shared; the mapping
> from scalars into it is not.

> **An advice-driven boundary plan is script-relative.** Phoneme identity across
> scripts holds per *boundary plan*, not per advice request.

A script's mapping may be **coarser** than another's, and that is expressed
rather than papered over. IndoPak's `ؕ` absorbs three Uthmani classes, so
mapping it to any one of them would invent a distinction the source does not
make. `StopAdvice` therefore carries a coarse member:

```python
class StopAdvice(StrEnum):
    PREFERRED_CONTINUE | PREFERRED_STOP | OPTIONAL_STOP
    COMPULSORY_STOP | PROHIBITED_STOP | EITHER_STOP
    PERMITTED_STOP            # a stop is allowed, class unspecified
```

`PERMITTED_STOP` exists because 2,826 IndoPak `ؕ` sites correspond to three
distinct Uthmani classes; it is the honest target for a convention that does not
distinguish them. Note that `EITHER_STOP` is now requestable, closing the
"parseable but not requestable" defect in evidence §7.

The domain review correctly observes that R3's reasoning is the **inverse** of
L2's: everywhere else, "the two scripts write different glyphs" is the reason to
derive canonically and let glyphs assert. The distinguishing fact is that advice
has no phonetic content and no rule reads it, whereas every other divergence is
about a sound. That test is what also keeps `sakt_after` on `ScoreWord` — sakt
blocks cross-word assimilation, so a rule reads it. Two glyph classes that look
alike, separated on whether a rule consumes them. The consequence at the API
surface is open question 5 (ADR-008 §7).

## 6. What each source under-specifies

Counts measured over both `quran.json` files. "Supplier" is the `Supply` under
L2; the other script's glyph, where present, is an `Assert`.

| Canonical fact | Uthmani writes | IndoPak writes | Supplier |
|---|---|---|---|
| `Nucleus.Silent` | absence of harakah | `ْ` (37,148 v 62,383) | script convention, both total |
| `letter = HAMZA` | precomposed `أإؤئ` | seat + `ٔ ٕ`; initial voweled `ا`; post-sukūn `اٰ` | script convention, both total |
| `Onset.WASL` | `ٱ` ×13,483 | a **bare** initial alef | **script convention, both total** (§6.1) |
| **waṣl helping vowel** | nothing | **186 sites** (§6.1, §6.3) | article rule + 2 further rules (§6.1) |
| silent seat (`Decorates`) | `۟` ×3,988 in 3,970 words | ×26 | otiose-wāw rule + 5 lexical classes |
| `Nucleus.PausalLong` | `۠` ×66 | ×**0** | Ledger ×66 (§6.2) |
| `Nucleus.Silah` | `ۥ` ×1,257 / `ۦ` ×956 | `ٗ` ×1,257 / `ٖ` ×993 | pronoun rule + exemption lexicon (§6.4) |
| `Onset.SILAH` | `ۧ` at 27:36:8 | — | Ledger (ADR-001 §3.5) |
| Allah's long ā | unwritten | `ٰ` written | Allah lexeme (12 skeletons, 2,704 words) |
| iqlāb | unwritten | `ۢ ۭ` ×546 | derived by rule; IndoPak `Attests(NASALIZATION)` |
| tanwīn nūn split across a boundary | `ٍ` on word *n* | `ࣙ` on word *n+1* ×54 (§6.5) | script convention, both total |
| `sakt_after` | `ۜ` at 5 of 7 | `ࣝ` at 3 of 7 | **Ledger — neither script is authoritative** |
| seen/ṣād khilāf | `ۜ ۣ` ×3 | `ۜ` ×4 | Ledger, 4 union sites (evidence §5) |
| imāla, tashīl | `۪ ۬` ×1 each | one generic `ؔ` | Ledger |
| ishmām 12:11 | `۫` ×1 | absent | Ledger |
| maddah | `ٓ` ×5,376 | `࢜` ×2,098 | none — `Decorates` the long-nucleus slot (§4.0) |
| final-mīm iltiqāʾ helper | damma/kasra ×6 | `ْ` | none — `Attests(INSERTION)` (§6.7) |
| advice | `ۖۗۚۘۙۛ` | `ؕ ࢵ ࢶ ࢷ ࢹ ࣝ` | not a Score fact (§5) |

### 6.1 Hamzat al-waṣl — a script convention, not a lexicon

The first draft, and evidence §3b, treated waṣl-hood as something Uthmani
declares and IndoPak omits, to be recovered by an article rule plus a lexicon of
526 — later 575 — canonical skeletons. Open question 2b asked whether that
lexicon was Arabic morphology or a transcription of Uthmani's own `ٱ`
positions. **It was the latter, and it is also unnecessary: IndoPak declares the
fact directly.** Measured over all 20,894 initial-alef sites:

| Uthmani | IndoPak alef | count |
|---|---|---:|
| waṣl | bare | 13,274 |
| waṣl | carries a haraka | 186 |
| qaṭʿ | carries a haraka | 13,394 |
| qaṭʿ | bare | 16 — all muqaṭṭaʿāt, plus 3:158:5 |

**A bare initial alef is a hamzat al-waṣl.** The convention is total in the
direction that matters, so under L2 it is a legitimate `Supply` with exactly the
standing `Nucleus.Silent` already has — a declared script convention, not a
glyph occurrence. `Onset.WASL` therefore has the same supplier status in both
scripts, and L1 genuinely *tests* the two derivations against each other instead
of testing one against a table learned from the other.

A derivation is needed only for the **186 sites where IndoPak writes the helping
vowel**. The article takes 121, leaving 64 over 42 skeletons — and those 42 are
all imperatives or form VII–X verbs, which is a rule, not a list:

1. **The article**, including before a geminated lām (`ٱلَّذِينَ`, `ٱلَّيْلِ`).
2. **Assimilated form VIII** — hamza + a geminate from the set the infixed tāʾ
   assimilates into (`ت د ط ز ص ض ظ ث ذ`), never fatha-vowelled.
3. **Otherwise** — hamza + a quiescent consonant, where the written vowel equals
   the classical helping-vowel derivation (damma iff the third letter carries
   damma, else kasra).

Rule 3 is self-checking, which is why it works: a hamzat qaṭʿ carries its *own*
morphological vowel, which the helping-vowel derivation does not predict.
`أُنزِلَ` writes damma where the derivation says kasra → qaṭʿ. `اُنْظُرْ` writes
damma and the derivation says damma → waṣl.

As a total decision procedure over all 20,894 sites: rules alone **95.80%**;
rules plus **three** particle entries (`إن`, `إذ`, `إذا`) **98.19%**, with
exactly **two** misses — 46:4:18 `ٱئْتُونِى` and 49:11:30 `ٱلِٱسْمُ`, both already
named Ledger sites. The 376 residual false positives are six named closed
classes of Arabic, not a tail: proper nouns (`إبراهيم` 58, `إسرائيل` 41,
`إبليس` 8, `إسحاق` 6), the `أولو`/`أوتوا` class (45, already named for the
otiose wāw), form-IV verbal nouns, `إذًا` folding into the particle entry, and
muqaṭṭaʿāt.

**Why this closes open question 2b where the lexicon did not.** The rules were
still validated against Uthmani's `ٱ` as ground truth — the same data the
lexicon was learned from. The difference is not the evidence, it is the
**checkability of the artifact**: a 575-row skeleton list can only be confirmed
by the corpus it came from, whereas these three rules can be checked against a
grammar by someone who has never seen this corpus, and all three are in every
tajwīd primer. That distinction is the whole argument, and it is the test any
future derivation class should be held to.

(The 186 here and the 181 in §6.3 differ because §6.3 counts only words
*beginning* with `ٱ`; this table counts every waṣl site.)

### 6.2 The seven alifs

66 sites. IndoPak writes `اَنَا` — a plain final alif, indistinguishable by any
IndoPak grapheme from an ordinary length carrier. The Ledger supplies
`NUCLEUS = PausalLong(A)`; Uthmani's `۠` asserts it.

**This is the case that requires "explicit evidence" to be defined**, because
R9's fourth fallback clause fires if any Ledger entry contradicts a script's
explicit evidence, and IndoPak's bare alef would by default derive `Long(A)`:

> A script gives **explicit evidence** for a fact when its declared inventory
> contains a grapheme class evidencing that fact class, **and an instance is
> present at the site**. A value produced by a derivation in the *absence* of
> any such grapheme is a default, not evidence, and a Ledger `Supply` may
> override a default without tripping the reversal trigger.

IndoPak's inventory contains no grapheme distinguishing pausal-only length, so
it gives no evidence here. Had IndoPak written `ٰ` and the Ledger said `Silent`,
that is a contradiction and fires.

### 6.3 The waṣl helping vowel — a fact with no assigned supplier

The first draft's table listed `Onset.WASL` and said nothing about the *vowel*
the waṣl slot takes at ibtidāʾ, which domain-facts §5.7 makes a three-branch
grammatical decision. Measured, of 10,768 Uthmani words beginning with `ٱ`,
IndoPak writes an explicit haraka on the corresponding alef at **181 sites**:

| IndoPak scalar | Count | Example | Domain branch |
|---|---:|---|---|
| fatha | 118 | 1:2:1 `ٱلْحَمْدُ` → `اَلْحَمْدُ` | article → fatha |
| kasra | 44 | 1:6:1 `ٱهْدِنَا` → `اِهْدِنَا` | verb, third letter kasra |
| damma | **19** | 4:50:1 `ٱنظُرْ` → `اُنْظُرْ` | verb, third letter damma |

(The domain review reported 162 sites and "damma 0". The damma branch exists at
19 sites, so **all three** branches of the derivation carry IndoPak evidence.)

The consequence is architectural. These are `Evidences` rows: if the canonical
nucleus of a waṣl slot were `Silent`, IndoPak's fatha at 1:2:1 would contradict
it and L2 would fail the build at 181 sites. The design works only if **the
canonical nucleus of a waṣl slot is the helping vowel itself** —
`Short(A)`/`Short(I)`/`Short(U)` — silenced by `WASL_ELISION` in connection and
realized at ibtidāʾ. That is now a stated `canon.build` obligation, not an
inference from ADR-002 §4.2's one-liner.

It matters which layer decides: `rules/` may not import `canon/` (ADR-007 §2)
and the waṣl derivation lives there, so the helping vowel cannot be a
`BOUNDARY`-phase decision.

### 6.4 Ṣilah — a derivation class measured for this ADR

Naive rule — *word-final hāʾ bearing damma or kasra, preceded by a voweled
letter* — yields **5,250 candidates against 2,213 marked Uthmani sites**: 3,094
false positives. Those reduce to **169 distinct canonical skeletons**, of which
`الله` (2,153), `والله` (240), `بالله` (139), `لله` (116) and `ءله` (40) account
for 2,688. The Allah lexeme is already a Score-level lexical fact, so
recognising it first drops the residue to ~406 words over ~164 skeletons; 95% of
the original false positives are covered by 37 skeletons.

Same shape as §6.1, and now stated as a design rule:

> **A location table growing toward 10⁴ entries is a signal that a rule is
> missing, not that the corpus is irregular.**

### 6.5 IndoPak carries cross-word evidence — U+08D9, 54 sites

`ࣙ` U+08D9 ARABIC SMALL LOW NOON WITH KASRA occurs at 54 IndoPak sites, all
word-initial on a hamzat-al-waṣl word, and — measured — **all 54** follow a word
that Uthmani writes with tanwīn:

```
2:180:9-10      U: خَيْرًا  ٱلْوَصِيَّةُ    I: خَيْرَاۚۖ  اࣙلْوَصِيَّةُ
4:36:32-4:37:1  U: فَخُورًا  ٱلَّذِينَ     I: فَخُوْرَا  اࣙلَّذِيْنَ
```

IndoPak splits the tanwīn across the boundary: the vowel on word *n* with the
tanwīn mark dropped, and the nūn-plus-helping-kasra depicted on word *n+1* as
`ࣙ`.

Under A1's ruling (ADR-001 §3.5b) that is **ordinary `Evidences`**, not an
attestation. The tanwīn nūn is a slot, so `ࣙ` evidences `LETTER = NOON` and
`NUCLEUS = Short(I)` on it, exactly as Uthmani's `ٍ` evidences the same two
slots without splitting them across the boundary. IndoPak was writing the
correct model all along, and the design now agrees with the orthography rather
than explaining it away.

#### The class is 55 words, and it is one class, not two

Measured over both corpora, of the words whose tanwīn presence disagrees:

| n | shape |
|---:|---|
| **34** | Uthmani tanwīn, IndoPak `ࣙ` on the next word **in the same verse** |
| **20** | Uthmani tanwīn, IndoPak `ࣙ` on the next word **in the next verse** |
| **0** | Uthmani tanwīn with no IndoPak compensation anywhere |
| **1** | the reverse — 18:1:11, Uthmani `عِوَجَاۜ` with a plain fatha under the sakt, IndoPak `عِوَجًا` with fathatan |

**There is no "IndoPak simply omits the tanwīn" class.** Every one of the 54 has
its compensation on the following word. The `34` that appears in the phase-1
spike's residue table is not a separate class — it is the *intra-verse subset*,
i.e. exactly the part that verse scope resolves.

#### Consequence: verse scope is necessary but not sufficient

ADR-001 §5 justified verse-scoping on this class. That justification was
incomplete: **20 of the 54 cross a verse boundary**, and
`read(text, at: VerseRef)` cannot see the next verse's first word either.

`canon.build` therefore takes the verse's `Reading` **plus a bounded one-word
right context** — the first word of the next verse, or `None` at the corpus end:

```python
def build(reading: Reading, right: Reading | None, ledger, lexicon,
          selection) -> tuple[ScoreWord, ...]: ...
```

One word, not one verse and not unbounded, because domain-facts §3 already
states the ceiling: *no rule needs more than one-word lookahead*. The same bound
now applies to Score construction, which is the honest form of the claim §5 was
reaching for.

### 6.6 Finding: six polysemous marks, and the ṣilah family is three of them

The wāw side is a clean 1:1 — U+06E5 ×1,257 and U+0657 ×1,257 at the same 1,257
words. The yāʾ side is not: U+06E6 ×956 against U+0656 ×993, the 956 shared plus
**37 IndoPak-only**, and at least three of those 37 are not ṣilah — at 11:41:6
(`مَجْرٖىهَا`) and 17:55:10 / 19:58:7 (`النَّبِيّٖنَ`) IndoPak's `ٖ` writes an
ordinary long ī.

**Uthmani U+06E7 is the sixth, and it is the one fixture 13 rests on.** 39
sites: `Onset.SILAH` at 27:36:8 (ADR-001 §3.5) and an **ordinary long ī** at the
other 38 — `إِبْرَٰهِـۧمَ` ×~30, `ٱلنَّبِيِّـۧنَ` and kin. ADR-001 §3.5 treated the
scalar as if it monosemously marked ṣilah; it does not, and neither does its
IndoPak counterpart U+0656.

The running list is therefore six: Uthmani `ۜ`, Uthmani `ۧ`, IndoPak `ࣝ`,
IndoPak `ࢵ`, IndoPak `ؔ`, IndoPak `ٖ`. Equal counts are not evidence of a 1:1
mapping, and **no `Evidences` or `Decorates` declaration may be justified per
scalar — only per site class.** Where the classes cannot be separated by a
derivation over canonical context, the Ledger separates them, which is what
27:36:8 requires: one `Supply(ONSET = SILAH)` at that slot, and the ordinary
long-ī derivation everywhere else.

The separation is therefore the Ledger and `canon/derive/`, and nothing else.
An earlier implementation also recorded the ambiguity as a `polysemous` section
in each inventory, which named the senses and then left the scalar's primary
declaration in force — a note about the problem rather than the mechanism that
solves it. It has been removed; a scalar is ambiguous exactly when a `Supply`
or a derivation says so.

Consequence for **fixture 13**: it must assert both halves — `Onset.SILAH` at
27:36:8 *and* `Nucleus.Long(I)` at a sample of the 38 — or it tests a scalar
rather than a fact and passes for the wrong reason.

### 6.7 Uthmani writes a performance fact — the final-mīm helper vowel

Measured, **6 words** where Uthmani writes a damma or kasra on a word-final mīm
and IndoPak writes sukūn: 6:20:7 `أَبْنَآءَهُمُ ۘ`, 6:93:34 `أَنفُسَكُمُ ۖ`,
8:60:19 `تَعْلَمُونَهُمُ`, 22:72:22 `ذَٰلِكُمُ ۗ`, 42:15:18 `بَيْنَكُمُ ۖ`,
42:15:29 `وَبَيْنَكُمُ ۖ`.

That vowel is the iltiqāʾ helper on the plural mīm — a `BOUNDARY` outcome, not a
canonical fact. Under L2 an `Evidences` row would contradict the canonical
`Silent` and fail the build.

The correct classification is **`Attests(INSERTION, anchor=the mīm slot)`**:
existing vocabulary doing exactly its job. The engine must produce an
`ILTIQA_REPAIR` occurrence whose participants include that slot, under the
all-join plan — six more free oracles for the phase-3 insertion machinery.

Declaring it `Decorates` instead would be wrong twice over: the vowel *sounds*,
so §4.0's whole point applies; and dissolving a residue row by declaring a
grapheme non-supplying is the §3.1 gaming route. **§4.0 and this section are the
same principle applied to two different glyph classes** — one that shows without
supplying, one that witnesses a performance outcome. Neither may be swept into
the no-fact member.

## 7. The Ledger

```python
LedgerEntry =  Supply(slot: SlotId, fact: SlotFact, value, skeleton: str,
                      citation: str)
             | Assert(script: Script, slot: SlotId, fact: SlotFact, value,
                      skeleton: str)
```

- The **value type is a canonical `SlotFact` value** — the same closed union the
  adapters emit. There is no syntax for "do something", so the Ledger cannot
  grow into a rule engine.
- **`Condition` is deleted** (ADR-001 §3.6). The Score is boundary-free, so
  `canon.build` had nowhere to put a `WHEN_STOPPING` value; every worked example
  was `ALWAYS`. Conditionality lives in the canonical vocabulary.
- `skeleton` is mandatory and validated against the Score — it keeps a
  verse-scoped ordinal reviewable and catches ordinal drift (ADR-001 §5.1).
- `Supply` is script-independent and carries a `citation`; `Assert` is
  script-scoped and carries none.
- The loader rejects: a duplicate `Supply` for one key; a value outside the
  canonical vocabulary; an `Assert` with no matching `Supply`; a key that is not
  a `SlotId`; a `skeleton` that does not match; and any entry expressed in
  output vocabulary.
- The Ledger replaces `data/riwayat/hafs/exceptions.yaml` entirely. ADR-006 §4
  governs what may become an entry.
