# Design spine B — the Score

## Position

One canonical layer, the **Score**, sits between orthography and sound. It is
script-free and boundary-free, and it is the only thing rules read and the only
thing anything addresses. Its unit is not a letter but a **Slot** — one
canonical consonantal position plus its nucleus. Carriers, seats, otiose
letters and length marks are not slots; they are graphemes that *evidence* a
slot's facts. Everything else hangs off the Score by two typed relations, and
the performance layer contains no grapheme at all — so no rule can read one.

Cost up front: the Score is a lossy intermediate that must be **proved** equal
across scripts, and proving it is most of the work. See Costs.

## The object graph

```python
# ---- L1  Score : riwayah-scoped, script-free, boundary-free ---------------
SlotId = tuple[Location, int]               # ordinal over SLOTS, not letters
class CanonLetter(StrEnum): ...             # 29 members; no ALIF_MAQSURA, no ALEF_WASLA
class Onset(StrEnum):       PLAIN | GEMINATE | WASL
class Quality(StrEnum):     A | U | I | IMALA
Nucleus = Silent | Short(Quality) | Long(Quality) | Leen(Quality, Glide) | Nunated(Quality)
class Colouring(StrEnum):   TASHIL | ISHMAM
class SlotOrigin(StrEnum):  WRITTEN | LEXICAL | SPELLED

class Slot:       id: SlotId; letter: CanonLetter; onset: Onset
                  nucleus: Nucleus; colour: frozenset[Colouring]; origin: SlotOrigin
class ScoreWord:  location: Location; slots: tuple[Slot, ...]
                  advice: StopAdvice | None; sakt_after: bool

# ---- L0  Inscription : script-scoped, fan-in only ------------------------
class SlotFact(StrEnum):  LETTER | ONSET | NUCLEUS | COLOUR | SAKT | ADVICE
class SpellKind(StrEnum): EVIDENCES | REDUNDANT | STRUCTURAL
class Grapheme:  char: str; offset: int
class Spelling:  grapheme: int; slot: SlotId | None      # one per grapheme
                 kind: SpellKind; fact: SlotFact | None

# ---- L2  Performance : one traversal; mentions no grapheme ---------------
SoundId = tuple[Location, int]
Sound   = Consonant | Vowel | Nasal | Release            # typed; never strings
class Attach(StrEnum):        HOSTS | MERGED_INTO | SILENT
class SilenceReason(StrEnum): SEAT | OTIOSE | WASL_ELISION | WAQF_DROP
                            | SILAH_DROP | ORTHOGRAPHIC_ZERO
class Attribution: slots: tuple[SlotId, ...]; sound: SoundId | None
                   kind: Attach; reason: SilenceReason | None; by: OccurrenceId
class Occurrence:  id: OccurrenceId; rule: Rule; parts: Participants
```

---

## 1. Layers and addressing

| Layer | Scope | Varies with |
|---|---|---|
| **Inscription** — `Grapheme`, `Spelling` | word × script | script |
| **Score** — `Slot`, `ScoreWord` | word × riwayah | riwayah only |
| **Performance** — `Sound`, `Attribution`, `Occurrence` | traversal | riwayah, boundaries, khilāf |

Reference direction is one-way and that is the entire mechanism. `Spelling`
points *up* into the Score; `Attribution` runs `SlotId → SoundId`. **Nothing
points down at a grapheme.** Delete the Inscription layer and only the
source-text projection breaks. A rule that wants a glyph has no field to look
through.

`SlotId = (Location, ordinal)`, ordinal counting slots. That is what survives a
script change: `ءَامَنُوا۟` has six Uthmani base letters and `اٰمَنُوْا` has
five IndoPak ones, but both are four slots — `[ʔ aː][m a][n uː][seat]`. Every
stable external reference — occurrence, ledger entry, khilāf site, fixture — is
a `SlotId`; never a `SoundId`, never an offset, never "the nth glyph".

Four deliberate omissions from `Slot`, each load-bearing:

- **No bare-vs-sukūn.** `Nucleus.Silent` is one value; Uthmani's absent harakah
  and IndoPak's `ْ` are two spellings of it. This is the whole of evidence §2:
  the 5,412 assimilations stop depending on Uthmani writing the nūn bare, and
  the 1,590 iẓhār cases are decided by the following letter's class — where the
  domain puts the decision.
- **No madd mark.** Length is `Nucleus.Long`; `ٓ` and `࢜` spell as `REDUNDANT`.
  Domain-facts §5.6 says the maddah carries no information, so it must not be a
  canonical field — `LetterForm.length_marked` today reads it, putting a script
  artifact in the rule path.
- **No carrier slots.** `ا و ي` that only carry length or seat a tanween are
  graphemes evidencing the *preceding* slot's `NUCLEUS`.
- **No `ALIF_MAQSURA`, no `ALEF_WASLA`.** `ى ي ے` fold to `YA`; waṣl-hamza is
  `letter=HAMZA, onset=WASL`. Both are glyph distinctions, not canonical
  letters.

## 2. Attribution

**One relation, three kinds, two totality invariants.** Distinguishing
information lives on `reason` and the owning `Occurrence`, not on extra
relation types.

- **`HOSTS`** — the sound is realized at these slots' position. `len(slots) > 1`
  is joint ownership; `len(slots) == 0` is insertion.
- **`MERGED_INTO`** — silent at own position because the material is inside a
  sound hosted elsewhere. The pair (`MERGED_INTO`, `HOSTS`) sharing one
  `SoundId` *is* a merger — no source/target boolean, no flag on a slot.
- **`SILENT`** — no sound anywhere, with a closed `SilenceReason`.

| Demand | Shape |
|---|---|
| Harakah + carrier share one long vowel | one `HOSTS` edge on one slot; both graphemes reach it via `Spelling.fact = NUCLEUS` |
| Cross-word merger | `MERGED_INTO(slots=(w_n,), sound=S)` + `HOSTS(slots=(w_{n+1},), sound=S)`, same `by` |
| Insertion, no source grapheme | `HOSTS(slots=(), sound=S, by=…)` |
| Deletion with a reason | `SILENT(slots=(s,), sound=None, reason=…, by=…)` |

Invariants, both one-pass assertable: every `Grapheme` appears in exactly one
`Spelling`; every `Sound` in exactly one `HOSTS`, every `Slot` in at least one
`Attribution`, every `by` resolving. Joint ownership is expressed by *arity*.
That is the simplification over a six-kind alignment layer: `realizes`,
`carries` and `assimilated` are one edge, distinguished only by whether the
sound is hosted here, elsewhere, or nowhere.

## 3. The script boundary

```python
class ScriptAdapter(Protocol):
    script: Script
    def read(self, text: str, at: Location) -> tuple[ScoreWord, tuple[Grapheme, ...],
                                                     tuple[Spelling, ...]]
    def write(self, slots: Sequence[Slot], style: SpellStyle) -> str
```

**L1 — Score equality.** For one riwayah and any two of its scripts,
`read(uthmani, loc).score == read(indopak, loc).score` at every location.
77,433 assertions, not a design claim; everything here is downstream of that
test existing.

**L2 — One authority per fact.** For each `(riwayah, script, SlotFact)` the
authority is the script (a grapheme evidences it) or the **Ledger** (a location
table). Where both are present they must **agree**; disagreement raises, naming
both. That is "a present mark validates rather than drives" made enforceable.

**L3 — Closed vocabulary.** A grapheme may only evidence a fact already in
`SlotFact` × the canonical enums; otherwise it is `STRUCTURAL` or the parse
fails loudly. This kills `SourceMark.SECOND_HAMZA` — a name for one location's
*outcome*, living in the script layer — and kills today's `structural:` list,
which silently discards `ۜ`, `ۣ` and `۫`.

What each source under-specifies (counts from my spike; see Findings):

| Canonical fact | Uthmani | IndoPak | Authority when absent |
|---|---|---|---|
| `Nucleus.Silent` | absent harakah | `ْ` (62,383 v 37,148) | script rule; both total |
| `letter = HAMZA` | precomposed `أإؤئ` | seat + `ٔ ٕ`; initial voweled `ا`; post-sukūn `اٰ` | script rule; both total |
| `Onset.WASL` | `ٱ` ×**13,483** | ×**1** | **Ledger (article + closed lists)** |
| `ORTHOGRAPHIC_ZERO` | `۟` ×3,988 | ×26 | **Ledger** |
| seven alifs | `۠` ×66 | ×0 | **Ledger** ×66 |
| Allah's long ā | unwritten | `ٰ` written | Ledger for Uthmani; IndoPak validates |
| iqlāb | unwritten | `ۢ ۭ` ×546 | derived by rule; IndoPak validates |
| sakt | `ۜ` at 5 of 7 | `ࣝ` at 3 of 7 | **Ledger — neither script is authoritative** |
| seen/ṣād khilāf | `ۜ ۣ` ×3 | `ۜ` ×**4** | Ledger; sites disagree (Findings 2) |
| imāla, tashīl | `۪ ۬` | one generic `ؔ` | Ledger for IndoPak |
| ishmām 12:11 | `۫` | absent | Ledger |
| maddah | `ٓ` ×5,376 | `࢜` ×2,098 | **never canonical — `REDUNDANT`** |
| waqf advice | `ۖۗۚۘۙۛ` | `ؕ ࢵ ࢶ ࢷ ࢹ ࣝ` | script→`StopAdvice`; a hint, not a Slot fact |

The **Ledger** replaces both `exceptions.yaml` and the script "mark" table. Key
`(riwayah, script, SlotId, condition)` with
`condition ∈ {ALWAYS, WHEN_STARTING, WHEN_STOPPING}`; value type `SlotFact` —
the *same* closed union the adapter emits. Two modes, `Supply` and `Assert`,
differing only in whether the script is silent. Because the value is a fact and
not an effect, it cannot grow into a rule engine: there is no syntax in it for
"do something".

## 4. Rule occurrences

`Rule` is a closed `StrEnum`, one member per conventional named phenomenon
including the passive ones (`IZHAR_HALQI`, `TARQIQ`, `LAM_SHAMSIYYAH`,
`MADD_TABII`). The structural guarantee is an invariant, not a discipline:

> **No sound exists except as the output of a named occurrence.** Every
> `Attribution.by` is non-null, including for iẓhār, tarqīq and plain
> realization.

There is no default path producing a sound without a named decision. A tajweed
projection is `filter(edges, rule == X)`; a phoneme projection is
`render(sounds)`; a highlight projection is `edge.slots`. All three read the
same edge set, so **a projection cannot disagree with the engine, because there
is nothing else for it to read.** Contrast `rules/idgham.py:28` — bare and
unshadda'd ⇒ emit nothing — which implements lām shamsiyyah, mutamāthilayn,
mutaqāribayn and mutajānisayn kāmil in one line, four named rules with no
names, forcing any downstream view to re-derive them from tokens.

`Participants` is a tagged union, one variant per family: nūn/tanwīn records the
following letter as *trigger* not target; idghām records the host; qalqala its
degree and boundary; emphasis a typed direct/look-back cause. No `detail` dict,
no condition tree.

Cost: iẓhār and tarqīq are the commonest phenomena, so occurrences are roughly
as numerous as slots — order 10⁵ per full recitation, 2–3× a mutation model.
Measure in phase 1 rather than pre-optimise.

## 5. Rule execution

Every rule has one shape. There is no per-letter dispatch switch, because *the
switch is the asymmetry*: `rules/apply.py::_pronounce_letter` decides by
authorship which letters deserve a module, and rāʾ won while the lām of Allah
lost.

```python
class Rule(Protocol):
    tag: RuleTag
    phase: Phase
    triggers: frozenset[CanonLetter] | NucleusKind          # index key
    def look(self, score: Score, at: SlotId, plan: Plan) -> Verdict | None
```

`look` is **pure** — read-only Score, read-only accumulated Plan. A `Verdict` is
`(Occurrence, tuple[Effect, ...])`; an `Effect` names a *target* `SlotId` and a
typed change: `Realize`, `MergeInto(host)`, `Silence(reason)`, `Insert(after)`,
`Recolour`, `Relength`. The `Plan` is an append-only journal keyed by
`(SlotId, aspect)`. **A rule affects a neighbour by declaring an Effect naming
it, never by writing to it** — replacing
`following.segments = [...]; following.resolved = True`
(`noon_tanween.py:31`, `meem.py:32`) and `owner.segments.pop(index)`
(`vowels.py:47`), which destroys joint ownership at the moment it is created.

**Two Effects on the same `(slot, aspect)` in one phase is an error**, naming
both occurrences. Domain-facts invariant 2 says exactly one rule of a family
fires per trigger; asserting it turns every violation into a found bug instead
of silent last-writer-wins.

Phases are closed and ordered — domain-facts invariant 8 made executable. Within
a phase rules are unordered and conflicts are errors.

| Phase | Decides | Reads |
|---|---|---|
| `LEXICAL` | Allah skeleton, muqaṭṭaʿāt spelling, waṣl class, khilāf choice | Score |
| `BOUNDARY` | the §7 waqf/ibtidāʾ transform set | Score + traversal |
| `MERGE` | which sounds exist: all idghām families, nūn/mīm, shamsiyyah, waṣl elision + iltiqāʾ repair, orthographic silence | Score |
| `LENGTH` | madd classification | the sound stream from `MERGE` |
| `COLOUR` | tafkhīm/tarqīq, ghunnah quality, imāla/tashīl | Score + sounds |
| `RELEASE` | qalqala | whether the closure survived `MERGE` |

Rāʾ tarqīq and Allah-lām tafkhīm are both `COLOUR` rules with identical
signatures, differing only in their `look` bodies — one a look-back through a
sukūn plus a same-word isti'lāʾ look-ahead, the other a cross-word
previous-nucleus look-back. Adding either is the same act; that is the test the
current code fails.

Riwayah binding is `Riwayah → RuleSet` at engine construction, so `engine.py`'s
unconditional `from .hafs import …` disappears. `Riwayah` stays a closed enum;
this is not a plugin registry. Phoneme strings never enter this layer: the
render alphabet is a property of an *output notation*, versioned with the
projection, unreachable from any `Rule` — which also stops `"ˤ"` and `":"` being
hardcoded in `rendering.py` while their siblings live in YAML.

## 6. Recited writing

A projection over `(Score, Plan, Spelling)` with four independent toggles, using
the adapter's `write` — the inverse of `read`. Not a layer, not a rebuild.

| Toggle | Values | Acts on |
|---|---|---|
| `faithfulness` | `SOURCE` \| `RECITED` | which glyphs: original, or re-spelled from the *performed* slot state |
| `silence` | `SHOW` \| `HIDE` | filters slots whose edge kind is `SILENT` or `MERGED_INTO` |
| `insertions` | `SHOW` \| `HIDE` | `HOSTS` edges with `slots == ()` get spelled by `write` |
| `spelling` | `COMPACT` \| `EXPANDED` | whether `SlotOrigin.SPELLED` runs show as source word or spelled slots |

They are independent because they act on different things: one picks the
*source* of glyphs, two are *filters over edge kind*, one picks the *slot
population*. All sixteen combinations are defined; none is special-cased.

The current model cannot express this for one concrete reason:
`engine.py:79-82` flattens everything into `WordRealization.segments`, so at
output time there is no record of which slot a sound came from, whether a slot
was silent, or why. Retaining the Plan instead of flattening it is the entire
fix — which is why I refuse to add a layer for it.

Round-trip check, cheap and strong:
`write(read(t).score, SOURCE, SHOW, SHOW, COMPACT) == t` over 77,433 words in
both scripts. It tests `Spelling` totality and the adapter at once.

## 7. Variant selection *(brief)*

Two different things that must not share a home.

- **Lexical khilāf** (seen for ṣād) is a Score-time choice resolved in `LEXICAL`,
  phase 1. `Choice = (KhilafId, Option)` where `KhilafId` is a closed enum member
  whose site is a `SlotId` set; the selection travels with the request and
  defaults per riwayah. Selecting `س` sets `Slot.letter = SEEN`, so inherent
  emphasis, vowel colouring and the rāʾ look-back follow automatically. A
  render-time swap is structurally impossible: the renderer sees `Sound`s, and a
  `Sound` cannot name a letter the rules never received.
- **Token khilāf** (`m̃` v `ŋ` for iqlāb / ikhfāʾ shafawī) changes no rule input,
  so it is a render-alphabet choice. It belongs with the projection; restoring
  it is a regression fix.

## 8. Exceptions *(brief)*

> **A Ledger entry may only supply or assert a `SlotFact` that already exists in
> the canonical vocabulary, and the same fact must be derivable by rule wherever
> some script does write it.**

"At 2:245:14 this ṣād's letter is SEEN" — a `LETTER` fact, derivable from
IndoPak's `ۜ` elsewhere: justified. "At 27:36:8 delete the small yāʾ" — names an
effect no rule can produce and no script can evidence: symptom patch, and the
missing rule is the actual bug. If you cannot express your fix as a `SlotFact`,
you have found a missing rule.

Scope key `(riwayah, script, SlotId, condition)`; riwayah alone is wrong, per
evidence §3.4's Uthmani-only 2:72 case. This retires
`HafsExceptions.{second_hamza, stopped_small_ya, shortened_raa, started_ituuni}`
— four fields named after their symptoms, applied by `_replace(first letter
matching identity)`, which is "the nth occurrence of glyph X" wearing a hat.

---

## Demonstrations — what is *stored*

**1. Cross-word idghām — 2:5:4→2:5:5, `مِّن رَّبِّهِمْ`.** Uthmani writes the
nūn bare (`0645 0651 0650 0646`); IndoPak writes explicit sukūn (`… 0646 0652`).
Both read to `Slot(2:5:4#2, letter=NOON, onset=PLAIN, nucleus=Silent)`. Stored:

```
Sound r1 = Consonant(RA, geminate=True)                    # SoundId (2:5:5, 0)
Occ   o1 = Occurrence(IDGHAM_BILA_GHUNNAH, NoonRecord(trigger=RA))
Attr     = (slots=(2:5:4#2,), sound=r1, kind=MERGED_INTO, by=o1)
Attr     = (slots=(2:5:5#0,), sound=r1, kind=HOSTS,       by=o1)
```

One sound, two slots in two words, one occurrence, no mutation of the rāʾ's own
state. Under today's code IndoPak yields iẓhār here (`noon_tanween.py:17` treats
explicit sukūn as not-sākinah): evidence §2 at a single address.

**2. One long vowel, two spellings — 2:5:2 `عَلَىٰ` / `عَلٰي`.** Same word, same
riwayah, and the dagger sits on a *different letter* in each.

| | Uthmani `عَلَىٰ` | IndoPak `عَلٰي` |
|---|---|---|
| graphemes | `ع َ ل َ ى ٰ` | `ع َ ل ٰ ي` |
| slots | `[ʕ Short(A)] [l Long(A)]` | `[ʕ Short(A)] [l Long(A)]` |
| `Spelling` for slot #1 `NUCLEUS` | `َ` (on ل) **and** `ٰ` (on ى) | `ٰ` (on ل) |
| the `ى` / `ي` | `Spelling(slot=#1, EVIDENCES, NUCLEUS)` — not a slot | same |

Two graphemes in one script, one in the other, both evidencing one
`Nucleus.Long(A)` on one slot. Joint ownership is edge *arity*, so nothing in
the model counts graphemes. `ى` and `ي` are one `CanonLetter.YA`.

**3. A silent grapheme with a recoverable reason — 2:5:1 `أُو۟لَـٰٓئِكَ`.** The
wāw sounds nothing. Uthmani marks it `۟` U+06DF; IndoPak (`اُولٰ࢜ىِٕكَ`) marks
it not at all. Stored:

```
Spelling(grapheme=و, slot=2:5:1#0, kind=EVIDENCES, fact=NUCLEUS)  # u stays short
Attr = (slots=(2:5:1#0,), sound=u_short, kind=HOSTS, by=o_plain)
Ledger[(hafs, indopak, 2:5:1#0, ALWAYS)] = Supply(NUCLEUS=Short(U))
Ledger[(hafs, uthmani, 2:5:1#0, ALWAYS)] = Assert(NUCLEUS=Short(U))   # `۟` agrees
```

The reason is recoverable two ways and L2 forces them to agree. Note the wāw was
never a slot, so the truthful statement is "the nucleus stayed short", not "a
letter was silenced" — a distinction `SourceMark.SILENT_ALWAYS` cannot make.

**4. Both scripts, one word — 3:2:1 `ٱللَّهُ` / `اللّٰهُ`.** Each script
under-specifies a *different* fact of the *same* word, in opposite directions.
This is the case for the whole design.

| Slot | Fact | Uthmani | IndoPak |
|---|---|---|---|
| #0 `HAMZA, WASL, Silent` | `ONSET=WASL` | `ٱ` U+0671 evidences | **absent** → Ledger supplies (article) |
| #1 `LAM, PLAIN, Silent` | — | `ل` | `ل` |
| #2 `LAM, GEMINATE, Long(A)` | `NUCLEUS=Long(A)` | **absent** → Ledger supplies (Allah skeleton) | `ٰ` U+0670 evidences |
| #3 `HA, PLAIN, Short(U)` | — | `ه ُ` | `ه ُ` |

Convergence: an identical four-slot Score. Contribution: Uthmani gives the waṣl
onset, IndoPak gives the long ā, neither is a superset. The Ledger entries are
`Supply` in one script and `Assert` in the other for the *same fact*, and L2
cross-checks the pair.

## Findings

Spikes over both `quran.json` files. Evidence-pack §1, §4, §6–§8 not re-derived.

1. **A second, larger script accident than the nūn.** Uthmani writes `ٱ` U+0671
   **13,483** times over 13,482 words; IndoPak writes it **once**. 2,714 of
   those words carry it medially (`وَٱللَّهِ` → IndoPak `والله`). Hamzat al-waṣl
   governs elision, the ibtidāʾ helping vowel and both iltiqāʾ repairs — under
   IndoPak the glyph carrying it does not exist. Any rule reading
   `Letter.HAMZA_WASL` is as script-bound as the nūn rule, at 2.5× the count.
2. **A fourth seen/ṣād khilāf site.** IndoPak writes `ۜ` U+06DC at 2:245:14,
   7:69:22, 52:37:7 **and 88:22:3** (`بِمُصَۜيْطِرٍ`), where Uthmani marks
   nothing. Evidence §5 says "exactly 3 sites" — contradiction, and exactly the
   shape law L2 exists for.
3. **`ࢵ` U+08D5 is not a khilāf marker.** 95 IndoPak sites (2:16:5, 2:22:7, …):
   an ordinary waqf sign. Evidence §5's row "IndoPak mark: `ۜ` + `ࢵ`" conflates a
   pause sign with the khilāf mark.
4. **Both scripts have a polysemous mark, not just Uthmani.** IndoPak's
   `ࣝ` U+08DD has 7 sites: 3 sakt (36:52, 75:27, 83:14) and 4 word-final waqf
   (7:23:4 `أَنفُسَنَاࣝ`, 7:184:2, 12:29:4 `هٰذَاࣝ`, 28:23:24) — and it is
   *absent* at Uthmani's 18:1 and 69:28. The sakt fact is authoritative in
   **neither** script. The pack treats U+06DC's double meaning as an Uthmani
   quirk; it is structural in both sources, which is why "marks validate, the
   Ledger supplies" must be a law and not a convenience.
5. **The Slot hypothesis survives a cheap test.** A ~120-line naive
   canonicaliser with no Ledger yields an identical slot count for **73,104 of
   77,433 words (94.4%)** across the two scripts. The 4,329 residue is dominated
   by two named classes — medial `ٱ` (finding 1) and IndoPak's post-sukūn `اٰ`
   hamza spelling — plus a bug in my own spike. Indicative only: it compares slot
   *count* and letter skeleton, not full `Slot` equality. L1 remains unproven.
6. **Silence marks are near-absent from IndoPak.** `۟` U+06DF 3,988 v 26;
   `۠` U+06E0 66 v 0. ~4,000 silence facts are Ledger work under IndoPak, which
   sizes the Ledger honestly — it is not a handful of exceptions.

## Costs, and what would change my mind

- **The Score is lossy and must be proved.** If two scripts genuinely encode
  different recitations somewhere — not different spellings — L1 fails and the
  layer is wrong. 2:72 is the known candidate. Settle it by running L1 at all
  77,433 locations and reading the residue.
- **The Ledger is large.** Findings 1 and 6 imply order 10⁴ IndoPak entries —
  the real price of forbidding a script to drive a fact. Most should be
  derivable (the article, the closed waṣl lists), but I have not measured how
  many survive derivation, and that number decides whether this is a table or a
  rule set.
- **Occurrence volume** ~1 per slot. Unmeasured.
- **A slot can be demoted.** `هُوَ` → *huu* at waqf turns a consonant slot into a
  length carrier. Expressible as a `BOUNDARY` Effect leaving the slot with no
  `HOSTS` edge of its own — but it is the one place "a slot is a consonant
  position" bends, and I would watch it.
- **I refuse a recited-writing layer**, on the argument that `write` plus a
  retained Plan suffices. If some recited form needs a grapheme sequence no Slot
  can spell — a genuinely orthographic pausal convention — that argument fails
  and a fourth layer is warranted.

## Phase order

1. `read` for both Hafs scripts, `Spelling` totality, and the L1 equality
   harness. Nothing else is meaningful until the residue is known.
2. `write`, and the source round-trip over 77,433 × 2 words.
3. One vertical slice — nūn/tanwīn — through `MERGE`, producing Sounds,
   Attributions and Occurrences, proved on both scripts.
4. Boundary transforms and muqaṭṭaʿāt spelling — where evidence §4's two domain
   defects get fixed as rules, not exceptions.
5. Remaining families, then the projections.
