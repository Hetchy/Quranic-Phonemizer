# Review — domain conformance, delivery, extensibility, and the gate

Lens: does the model match the domain, does it deliver what the owner asked
for, and will it extend. Reviewed against `docs/adr/001`–`008`,
`docs/domain-facts.md`, `research/spines/`, `research/evidence/`, and both
corpora. Every count below was measured in this review against
`corpus_sources/riwayat/hafs/scripts/{uthmani,indopak}/quran.json` or against
the frozen snapshots; where I re-measured a pack figure and it held, I say so.

**Verdict: AMEND.** Named changes in §6.

---

## 1. What is right — stated once, not re-litigated

These are correct and I have nothing to add:

- **The one-way reference and the absent grapheme field** (ADR-001 §1). This is
  the right structural answer to evidence §2, and it is genuinely structural
  rather than disciplinary. The X1/X3 packaging tests are a proper second guard.
- **One attribution relation with arity as the sound-sharing mechanism**
  (ADR-002 §3). Domain-facts §4's "a sound may be shared by several graphemes"
  and §6's "one sound jointly owned by graphemes in two different words" both
  fall out with no extra machinery. Facets and five-role schemes were rightly
  rejected.
- **`Aspect`** (R1). The `كِتَٰبٌ` case is real and the two-member closure is
  correctly argued from the Slot's own field partition.
- **Occurrences as the only path to sound** (ADR-002 §5) plus the `render`
  import ban (ADR-007 §2). Two independent guards on "a projection cannot
  disagree with the engine" is the single best idea in the set.
- **Effects instead of neighbour mutation** (ADR-004 §2), and conflict-as-error
  as the executable form of domain-facts invariant 2.
- **The khilāf split** (ADR-006 §1). Lexical khilāf resolving before the Score
  so that emphasis, vowel colouring and the rāʾ look-back follow, with a
  render-time swap made structurally impossible, is exactly right and is the
  part of the design I would change least.
- **`Nucleus.PausalLong` as a worked instance of the exception test**
  (ADR-001 §3.3, ADR-006 §4.2). Adding a vocabulary member rather than an
  escape hatch is the correct move and it is correctly justified.
- **`sakt_after` stays on `ScoreWord` while advice leaves**, split on "does a
  rule read it" (ADR-003 §5). Two glyph classes that look identical, separated
  on a principled test.
- **The Supply/Assert asymmetry and the one-directional attestation law**
  (R8, ADR-003 §4.1). I re-measured the shadda ʿāridah inventory:
  **5,761 IndoPak / 3,722 Uthmani**, matching the ADR exactly. A bidirectional
  law would indeed fail on thousands of words. Correct call.
- **`Riwayah` as a closed enum, no plugin registry, no YAML effect engine**
  (ADR-004 §6). The honest contract.

I also re-measured the ṣilah polysemy finding (ADR-003 §6.4) and the 4
seen/ṣād sites (ADR-006 §2); both hold.

---

## 2. Findings, ranked by what would actually hurt

### D1 — Tanwīn idghām needs two effects on one conflict key. E1 raises at ~4,746 sites. **Critical.**

**Claim.** `Nucleus.Nunated(Quality)` folds a *consonant* (the nūn) into a
*nucleus*. ADR-004 §4 keys every effect on `(SlotId, Aspect)` and makes two
effects on one key within one phase an error (E1). For tanwīn idghām the vowel
stays on the tanwīn slot and the nūn merges into the next word's onset. That is
`Realize(slot, NUCLEUS, (Vowel,))` **and**
`MergeInto(slot, NUCLEUS, host=next, host_aspect=ONSET)` — two effects, one
key, one phase (`MERGE`).

**Evidence.** Measured over the Uthmani corpus: tanwīn-final words followed by
an idghām letter — **3,858 bi-ghunnah + 888 bila-ghunnah = 4,746 sites**
(plus 304 iqlāb and 1,995 ikhfāʾ which are fine, being single `Realize`s with a
sound tuple). The current engine's output confirms the split ownership:
`هُدًى مِّن` renders `h u d a` · `m̃ i` — the vowel on word *n*, the nūn's sound
on word *n+1*.

ADR-002 §7 anticipates the *edges* ("a `Nunated` nucleus hosts a vowel and a
nūn, two `HOSTS` edges on one aspect") and explicitly says uniqueness applies to
effects, not edges — which is precisely what creates the contradiction, because
those two edges here require two different effect kinds. `Realize`'s sound tuple
solves iẓhār/ikhfāʾ/iqlāb and does not solve idghām, and `MergeInto` has no
residual-sounds field.

This also makes the nūn-sākinah/tanwīn family structurally asymmetric — the
same rule merges an `ONSET` when the trigger is a nūn slot and a `NUCLEUS` when
it is a tanwīn — against domain-facts invariant 1 ("every noon-sakinah rule has
a tanween twin") and against the owner's "no asymmetry between rule families".

**What should change.** Either give `MergeInto` a `residual: tuple[SoundSpec, ...]`
field (cheapest, additive, keeps `Nunated`), or make E1's key
`(SlotId, Aspect, sound_index)`, or split the tanwīn nūn into its own
`SlotOrigin.LEXICAL` slot so the family has one shape. ADR-004 must state which
and show the `هُدًى مِّن` trace. This is the one finding I would not let through
to implementation unresolved.

---

### D2 — Deleting `Consonant.nasalized` makes 10,667 output tokens unreachable. Phoneme parity cannot pass. **Critical.**

**Claim.** ADR-002 §6 states `Consonant` carries no `nasalized` flag and that
"the render map keys on the feature bundle". The feature bundle is
`(letter, geminate, emphatic)`. Nasalization is then invisible to `render/`,
and fixture 20 (phoneme parity, both scripts, three modes) cannot pass.

**Evidence.** Token histogram of `tests/snapshots/phonemes/continuous.jsonl.gz`:

| token | count | plain sibling | count |
|---|---:|---|---:|
| `ñ` | 4,098 | (no `nn` exists) | — |
| `m̃` | 3,254 | `m` | 22,174 |
| `w̃` | 2,192 | `ww` | 279 |
| `j̃` | 1,123 | `jj` | 1,080 |

**10,667 tokens in continuous mode alone.** `w̃` and `ww` are distinct tokens
produced from the same letter with the same gemination; the only thing that
separates them today is `Consonant.nasalized`. Verified live:
`3:1` → `ʔ a l i f l a: m̃ i: m`.

The ADR's stated motive is to fix `rendering.py:75`, which drops `geminated` and
`emphatic` when `nasalized` is set. That defect is fixed by making the render
map *compose* the features, not by deleting one of them. The diagnosis is
inverted.

Note the inconsistency with ADR-006 §3, which correctly adds `NasalPlace` to
`Nasal` precisely so that a computed feature can reach output. The identical
argument applies to the nasalized consonant and is not made.

**What should change.** `Sound.Consonant` gains a nasal/ghunnah feature (or
`Sound` gains a `NasalizedConsonant` member). Alternatively state explicitly
that `render/` keys on `(feature bundle, occurrence rule)` — but that weakens
ADR-002 §5's projection story and should not be chosen silently.

---

### D3 — A slot that exists in waṣl and vanishes at waqf cannot be expressed, and ADR-006 §4.1's fix for it is demonstrably wrong. **Major.**

**Claim.** ADR-006 §4.1 rules `HafsExceptions.stopped_small_ya` a symptom patch
and says "the real fact is a `WHEN_STOPPING` nucleus value". It is not, and no
`WHEN_STOPPING` nucleus value produces the right output.

**Evidence.** Measured live at 27:36:8 (`ءَاتَىٰنِۧ`):

```
joined   : ʔ a: t a: n i j a
stopped  : ʔ a: t a: n
```

At waqf the mini-yāʾ's **onset disappears too**, not just its nucleus. A Ledger
`Supply(NUCLEUS = Silent, WHEN_STOPPING)` on that slot leaves the onset
sounding and yields `ʔ aː t aː n i j`. `Onset` is `PLAIN | GEMINATE | WASL` —
there is no absent value — so no `SlotFact` value can silence an onset
conditionally either. And no rule can derive it: `Rule.triggers` indexes on
"letters, or a nucleus kind", the nucleus here is an ordinary `Short(A)`, and
nothing on the `Slot` marks it as a pronoun ṣilah yāʾ.

The mechanism to *express* the outcome exists —
`SILENT(slots=(ya,), aspect=ONSET, reason=SILAH_DROP)` plus the same on
`NUCLEUS` — but nothing in the design can *decide* to emit it. By ADR-006 §4.2's
own corollary that is a missing vocabulary member, not a solved case.

The neighbouring row is wrong the same way. `HafsExceptions.second_hamza` is
ruled a patch and "the real fact is `COLOUR = TASHIL` at 41:44". Measured
output at 41:44:9 is `ʔ a ʔ a ʕ ʒ a m i jj u` — **two hamza slots**. Uthmani
writes `ءَا۬عْجَمِىٌّ`; without a canonical `LETTER = HAMZA` + `NUCLEUS = Short(A)`
on the alif's position, that alif is a length carrier and the output becomes
`ʔ aː ʕ ʒ …`. `COLOUR = TASHIL` alone changes nothing, because `Sound` has no
tashīl feature at all (see D8) — so the *stated* fix both under-specifies the
Score and cannot reach the renderer.

**What should change.** ADR-006 §4.1's table is the worked demonstration of the
exception test; two of its four rows are wrong and must be re-derived against
actual output. Then either add a boundary-conditional slot-presence mechanism
(a `SlotFact.PRESENCE` with a condition, or a ṣilah-pronoun marker the boundary
rule can trigger on), or accept these as the design's own exception-test failure
and add the vocabulary member.

---

### D4 — `Attests(rule: Rule)` forces the script adapter to classify the idghām family. **Major.**

**Claim.** ADR-003 §4 types attestation as `Attests(grapheme, rule: Rule, anchor)`
and ADR-007 §3's inventory schema shows
`"ّ@word_initial": {rule: IDGHAM_BI_GHUNNAH, anchor: previous_word_final}`.
The adapter must therefore name one `Rule`. That is tajweed classification
inside the script layer, contradicting ADR-001 §2 ("adapters extract evidence…
the linguistics is shared and written once").

**Evidence.** I classified all word-initial shaddas by what precedes them:

| preceding word ends in | IndoPak | Uthmani | rule attested |
|---|---:|---:|---|
| tanwīn | 3,407 | 2,089 | `IDGHAM_BI_GHUNNAH` / `BILA_GHUNNAH` |
| nūn | 1,360 | 624 | `IDGHAM_BI_GHUNNAH` / `BILA_GHUNNAH` |
| mīm | 821 | 833 | `IDGHAM_SHAFAWI` |
| lām | 110 | 110 | `IDGHAM_MUTAQARIBAYN` / `MUTAMATHILAYN` |
| alif (otiose, real final wāw) | 20 | 22 | `IDGHAM_MUTAMATHILAYN` |
| tāʾ | 17 | 17 | `IDGHAM_MUTAMATHILAYN` / `MUTAJANISAYN_KAMIL` |
| bāʾ | 8 | 8 | `IDGHAM_MUTAMATHILAYN` |
| dāl | 8 | 8 | `IDGHAM_MUTAJANISAYN_KAMIL` |
| rāʾ, dhāl | 6 | 6 | `MUTAQARIBAYN` / `MUTAJANISAYN_KAMIL` |

At least **seven** distinct `Rule` members behind one scalar-in-position, and
choosing between them requires knowing the previous word's final letter class,
whether the tanwīn nūn is bi- or bila-ghunnah, and the idghām pair tables. That
is `rules/idgham.py`'s job, relocated into `script/indopak.py`.

**What should change.** `Attests` should carry a rule *class* — either a new
closed `RuleFamily` enum or `frozenset[Rule]` — and A1 becomes "the engine
produces an occurrence of *some* rule in the attested class at `s`". This keeps
all 9,483 oracles and removes the linguistics from the adapter. Additive.

---

### D5 — The gate rests on one invariant that is true by construction and one test that is gameable. **Major.**

The whole architecture is bet on ADR-008 §3. Two problems.

**(a) S1 is unfalsifiable.** "Every `Slot` satisfies the unit-hood criterion
evaluated over canonical context." The criterion is prose, and `canon.build`
constructs slots *by* it. No wrong implementation fails S1 — there is no oracle
independent of the builder. It is the single most load-bearing invariant in the
set and it asserts nothing.

A falsifiable substitute exists and is cheap: **every slot must have a `HOSTS`
edge on at least one aspect under at least one of the three renditions** (waṣl,
stopped-on, started-on). That is exactly the criterion, it is a one-pass check
over three traversals, and a carrier wrongly promoted to slot-hood fails it.

Same for S2 (a type check mypy already does), S3 (a dataclass-field check), P7
(no field exists to hold the value), and E4 (the rule author *declares* itself
classification-only, so nothing can fail). None of these is harmful, but five of
twenty-six invariants are true by construction and the count of twenty-six
should not be read as twenty-six checks.

**(b) The L1 residue can be driven to zero without proving anything.**
`canon.build` is shared and script-independent by design (ADR-001 §2), so
**every fact it supplies is identical across both builds by construction**. L1
only tests facts that come from adapter evidence. Any residue row can therefore
be eliminated by moving that fact out of adapter evidence and into a derivation
keyed on the canonical skeleton or a Ledger `Supply` — after which the two
builds agree trivially. The reversal trigger's clauses 1–3 and the ~50-supply
budget are the intended guards, and I4 (an `Assert` must exist and agree) is a
real one.

But there is an unguarded escape: **reclassify the disagreeing grapheme as
`Inert`.** L3/I1 force every scalar to be *classified*, and `Inert` ("carries no
canonical fact") is a legal classification that files no `Assert` and produces
no residue row. ADR-001 §2 actively pushes in this direction — it celebrates
thin adapters as a benefit — and nothing counts or bounds the outcome.

**What should change.** Replace S1 with the three-rendition `HOSTS` check. Add
to §3: the harness must report, per riwayah, the **provenance split** (facts
from adapter evidence / derivation / Ledger) and the count of `Inert`
classifications for scalars that the *other* script's inventory maps to a fact
class. A residue of zero reached by a rising `Inert` count is not a proof of
script-independence, and the report must be able to show that.

---

### D6 — The hamzat al-waṣl helping vowel is a canonical fact with no assigned supplier, and IndoPak evidences it at 162 sites. **Major.**

**Claim.** ADR-003 §6's supplier table lists `Onset.WASL` (supplier: article
rule + skeleton lexicon) and nothing about the *vowel* the waṣl slot takes at
ibtidāʾ. Domain-facts §5.7 makes it a three-branch grammatical decision.
Neither script writes it in Uthmani, so it looks like a non-fact — but it is not.

**Evidence.** Of 10,768 Uthmani words beginning with `ٱ`, IndoPak writes an
explicit haraka on the corresponding alif at **162 sites**:

| IndoPak second scalar | count | example |
|---|---:|---|
| fatha | 118 | 1:2:1 `ٱلْحَمْدُ` → `اَلْحَمْدُ` (article → fatha) |
| kasra | 44 | 1:6:1 `ٱهْدِنَا` → `اِهْدِنَا` (verb, third letter kasra) |
| damma | 0 | — |

Both classes agree with the domain-facts §5.7 derivation, so these 162 sites are
a **free oracle for the helping-vowel rule** — better than an oracle, they are
`Evidences` rows that will collide with the derivation if it is wrong.

The consequence is architectural, not cosmetic. If the waṣl slot's canonical
nucleus is `Silent`, IndoPak's fatha at 1:2:1 is explicit evidence contradicting
it, and L2 disagreement fails the build at 162 sites. The design works if the
canonical nucleus *is* the helping vowel (`Short(A)`/`Short(I)`/`Short(U)`),
silenced by `WASL_ELISION` in waṣl and realized at ibtidāʾ — which is consistent
with ADR-002 §4.1's one-liner ("the hamzat al-waṣl start vowel fills the waṣl
slot's own nucleus") but is stated nowhere as a canon.build obligation.

It matters *which* layer decides, because `rules/` may not import `canon`
(ADR-007 §2) and the 526-skeleton lexicon lives there. If the helping vowel is a
`BOUNDARY`-phase decision, the rule has no legal access to the lexicon.

**What should change.** Add a row to ADR-003 §6's table: helping-vowel nucleus,
Uthmani writes nothing, IndoPak writes it at 162 sites, supplier = article rule
+ waṣl-skeleton lexicon in `canon.build`. State that the value is canonical and
elided in waṣl. Add the 162 sites to the fixture list.

---

### D7 — `read` and `canon.build` are word-scoped, but IndoPak carries cross-word evidence at 54 sites the attestation inventory misses. **Moderate.**

**Claim.** `ScriptAdapter.read(text, at: Location) -> Reading` and
`canon/build.py: Reading -> ScoreWord` are per-word. At least one IndoPak
grapheme class supplies a canonical fact about the *previous* word.

**Evidence.** IndoPak U+08D9 ARABIC SMALL LOW NOON WITH KASRA occurs at **54
sites**, all word-initial on a hamzat-al-waṣl word, and **53 of 54 follow a word
that Uthmani writes with tanwīn**:

```
2:180:9-10  U: خَيْرًا  ٱلْوَصِيَّةُ     I: خَيْرَاۚۖ  اࣙلْوَصِيَّةُ
7:8:2-3     U: يَوْمَئِذٍ ٱلْحَقُّ        I: يَوْمَىِٕذِ  اࣙلْحَقُّ
```

IndoPak splits the tanwīn across the boundary: it writes the vowel on word *n*
(dropping the tanwīn mark) and depicts the nūn-plus-helping-kasra on word *n+1*
as `ࣙ`. This is orthography recording the *performed* iltiqāʾ repair — exactly
R2's `Attests` case, at the exact site class (`slots == ()` insertions) that
motivated adopting `anchor`. It is not in ADR-003 §4.1's inventory, which lists
only the 10 muqaṭṭaʿāt sites, 546 iqlāb marks and the shadda ʿāridah.

The same 54 sites are a measured L1 residue class. I compared tanwīn presence
across the two scripts word by word: **55 words disagree** — 54 IndoPak-drops
(the sites above) and **1 the other way** (18:1:11, Uthmani `عِوَجَاۜ` with a
plain fatha under the sakt, IndoPak `عِوَجًا` with fathatan). That is a small,
named, both-directional class, which is good news for the L1 gate's
tractability — but resolving it correctly requires reading word *n+1*'s
graphemes while building word *n*'s Score, which the signature forbids.

**What should change.** Make `read` verse-scoped
(`read(text, at: VerseRef) -> Reading` over the verse's words) and
`canon.build` verse-scoped. Add U+08D9 to the attestation inventory as
`Attests(ILTIQA_REPAIR, anchor=previous_word_final)` — 54 free oracles for the
insertion-with-anchor machinery, which currently has exactly one (3:1). Add the
55-word tanwīn class to the L1 derivation registry by name.

---

### D8 — The `Rule` enum and the `Recolour` effect are both under-powered relative to ADR-004 §3's own phase table. **Moderate.**

Three distinct gaps, one theme: the COLOUR phase cannot do what ADR-004 §3 says
it does.

1. **Missing `Rule` members.** ADR-004 §3 says `COLOUR` decides
   "tafkhīm/tarqīq, ghunnah quality, **imāla, tashīl**". `Rule` (ADR-002 §5) has
   no `IMALA`, `TASHIL` or `ISHMAM` member, and ADR-002 §5's invariant is that
   every attribution has a non-null `by` resolving to an `Occurrence` carrying a
   `Rule`. So imāla (11:41), tashīl (41:44) and ishmām (12:11) have no legal
   occurrence tag. Also missing: `LAM_QAMARIYYAH` — ADR-002 §5 names it in prose
   ("including for iẓhār, tarqīq, lām qamariyyah and plain realization") but the
   enum has no member, so a projection cannot answer "which lāms are qamariyyah"
   while it can answer the shamsiyyah question. And ṣilah realization in waṣl
   has no tag although `SILAH_DROP` exists as a silence reason.

2. **`Recolour(slot, aspect, emphatic: bool)`.** Domain-facts §4's colour
   vocabulary is tafkhīm, ghunnah nasalization, imāla, tashīl, rawm/ishmām. A
   boolean covers one of five. Imāla is rescued by `Quality.IMALA` and tashīl/
   ishmām by `Slot.colour` — but then ADR-004 §3's claim that the COLOUR phase
   *decides* them is false; `canon.build` and the Ledger decide them
   (ADR-003 §6 lists both as Ledger-supplied). The two ADRs disagree about which
   layer owns imāla and tashīl.

3. **`Sound` cannot carry tashīl or rawm.**
   `Consonant(letter, geminate, emphatic)` has no softened-hamza feature, so
   `Colouring.TASHIL` has no path to output. Today the 41:44 output is `ʔ a`
   with no distinction, so parity is unaffected — but "the real fact is
   `COLOUR = TASHIL`" (ADR-006 §4.1) is then a fact that provably cannot affect
   anything, which is a strange thing for the exception test's worked example to
   be.

**What should change.** Add the missing `Rule` members. Either widen `Recolour`
to carry a `Colouring`/`Quality` payload or delete the COLOUR-phase claim over
imāla and tashīl from ADR-004 §3 and say plainly that they are Score facts. Say
explicitly whether tashīl is intended to be audible.

---

### D9 — L2's scoping clause and I3 do not state their scope, and under one reading I3 is violated by every voweled slot. **Moderate.**

**Claim.** L2 says exactly one `Supply` per `(riwayah, SlotId, SlotFact,
condition)` and that a present glyph is never the canonical supplier. The
scoping clause then makes a *script convention* ("in Uthmani, U+064E evidences
`Short(A)`") a legitimate `Supply`. But a script convention is script-scoped by
construction. If both scripts' conventions are Supplies, every ordinary voweled
slot has two Supplies and I3 fails corpus-wide. If only one counts, the Score is
derived from a privileged script.

The intended reading is almost certainly **per-build** — one `Supply` within one
`(script → Score)` construction, with L1 as the cross-script check. Under that
reading the design is coherent, but "a present glyph is never the canonical
supplier" becomes false as a description of what actually happens: via declared
conventions, present glyphs supply the overwhelming majority of canonical facts,
and the Ledger covers the residue. That is fine and honest; it just is not what
R8 says.

**What should change.** One sentence in ADR-003 §3 stating that L2/I3 are
per-build, and one in §7 stating that I3's loader check is over `ledger.yaml`
only. Otherwise two gate invariants have undefined scope.

---

### D10 — The worked slot example in ADR-001 §5 is arithmetically wrong. **Minor, but it is the only worked example of the addressing scheme.**

ADR-001 §5: "`ءَامَنُوا۟` has six Uthmani base letters and `اٰمَنُوْا` has five
IndoPak ones, and both are four slots — `[ʔ aː][m a][n uː][seat]`."

Base-letter counts are right (verified: 6 and 5, at 2:9:4). The slot count is
**three**, not four. Measured output is `ʔ aː m a n uː`. The listed fourth
element "[seat]" is the otiose alef, which the unit-hood criterion excludes
(§3.1 length clause), which §4 lists under "No carrier slots", and which
ADR-005 §5 itself classifies `Inert` in the parallel `أُو۟لَـٰٓئِكَ` case. The
example contradicts three other sections of the same ADR set.

---

### D11 — Advice-driven plans being script-relative breaks the owner's byte-identity requirement at the shipped API surface. **Minor as design, notable as delivery.**

ADR-003 §5 states it plainly and honestly, and ADR-008 §7.5 keeps it open. But
the shipped API *is* `phonemize(ref, stop_signs=[...])`. Under the design,
`stop_signs=["preferred_stop"]` yields different phonemes per script, so the
requirement "phonemes byte-identical across different source scripts of the same
riwayah" holds per boundary plan and not per call.

Worth noting that R3's reasoning is the inverse of L2's: for every other fact,
"the two scripts write different glyphs" is the reason to *derive canonically
and let glyphs assert*; for advice alone it is the reason to declare it not a
canonical fact. Only 4,359 words carry a sign and the advice *classes* are
riwayah-level editorial facts with script-specific glyph conventions — the same
shape as everything else. I am least confident about this finding: advice
genuinely has no phonetic content, and R3's position is defensible. I raise it
because the owner's requirement is stated in terms the API exposes.

---

### D12 — Round-trip totality has an unstated ordering dependency. **Minor.**

Fixture 1 is `write(read(t), SOURCE_FORM, COMPACT) == t` over 77,433 × 2 words.
Measured: **4,575 Uthmani words contain an internal space** (`'مَنْ ۜ'`,
`'مَّرْقَدِنَا ۜ ۗ'` — two structural marks, in order), and **6,404 contain a
tatweel**. `Spelling.Structural(grapheme)` carries no position and
`Inert(grapheme, near)` carries only a coarse slot reference, so exact
reproduction depends on `GraphemeId` being position-ordered — which the ADRs
never say. One sentence in ADR-001 §5 or ADR-007 §1 fixes it.

---

## 3. Did it deliver what was asked?

| Requirement (owner's words) | Verdict | What a caller can and cannot build |
|---|---|---|
| Phonemes byte-identical across source scripts of the same riwayah | **Partial** | The architecture is right (shared `canon.build`, no grapheme field, L1 + fixture 20). But it holds per *boundary plan*, not per API call (D11), and L1's own strength is weaker than presented (D5). Unproved by design; phase 1 is the whole question, correctly stated. |
| Tajweed rules linked to graphemes **and** phonemes so projections are easy | **Delivered** | grapheme →`Spelling`→ slot+aspect →`Attribution`→ sound →`by`→ `Occurrence`. Complete, closed, and guarded twice. Caveats: missing `Rule` members (D8) means imāla/tashīl/ishmām/lām-qamariyyah occurrences cannot be tagged; D2 means the nasal distinction cannot reach output. |
| Phonetic text as a first-class projection with levels and toggles | **Partial** | ADR-005's four toggles cover silent letters ✓, inserted graphemes ✓, muqaṭṭaʿāt expansion ✓, wasl/ibtidāʾ word effects ✓ (the `Performance` carries the plan). **"Removed and added diacritics" is only half-covered**: `faithfulness` is one axis conflating glyph source with performed state, so "show the source diacritic, marked as removed" is computable from `SILENT` edges but is not a toggle. "Levels" has no counterpart at all — there is no ordering or nesting of the four axes. The public API is explicitly out of scope, which is legitimate, but that is where "levels" lives. |
| Khilāf selectable as arguments — token choice and per-location lexical choice | **Delivered (mechanism)** | Both kinds, split on the right test, in the right layers, with the render-time swap made structurally impossible. Token khilāf is expressible because `Nasal` gained `place`. The argument surface itself is out of scope. Note the asymmetry with D2: the same "a computed feature cannot reach output" problem is fixed for `Nasal` and created for `Consonant`. |
| Riwayah-agnostic **and** script-agnostic | **Delivered (structurally)** | `rules_for(riwayah)`, no `from .hafs import`, no grapheme or script field on `Performance`, X1/X2/X3 as AST tests. This is the requirement the design serves best. |
| No symptom-named fields | **Delivered** | ADR-007 §4.1 states the rule; ADR-006 §4.1 retires all four current offenders. Two of the four replacement diagnoses are wrong (D3), but the *naming* requirement is met. |
| No asymmetry between rule families | **Partial** | The per-letter dispatch switch is correctly killed (ADR-004 §1) and all rules share one shape and one index. But: the nūn/tanwīn family has two triggers and two merge shapes (D1); `LAM_SHAMSIYYAH` has a `Rule` member and `LAM_QAMARIYYAH` does not; the madd family gets six members while tafkhīm/tarqīq get one each. |

---

## 4. Extensibility, walked through

### (a) Warsh — new rules, new script, possibly different word division

Answerable entirely from the documents, and the answer is **additive throughout**.
This is a real strength; I could not make it break.

| Change | Where | Additive? |
|---|---|---|
| new riwayah | `model/riwayah.py` `Riwayah` enum; `riwayat/warsh/`; `data/riwayat/warsh/*` | yes |
| new script(s) | `model/inscription.py` `Script`; `script/warsh_*.py`; inventory YAML | yes |
| taqlīl (bayna-bayna) | `Quality` += `TAQLIL`; flows into every `Nucleus` member and `Sound.Vowel` unchanged | yes |
| naql, ibdāl, tashīl-as-rule | new `Rule` members; new `rules/*.py`; `rules_for(WARSH)` | yes |
| naql's deleted hamza | **`SilenceReason` += a member** — naql silence is neither `WASL_ELISION` nor `WAQF_DROP` nor `SILAH_DROP` | yes, but note R7's claim that `SilenceReason` is "traversal reasons only" does not survive Warsh |
| different rasm / otiose letters | script inventory + `canon` derivation classes, riwayah-scoped | yes |
| different word division | **not a problem** — Warsh has its own `Riwayah`, its own corpus, its own `Location`s | n/a |

The one correction: ADR-001 §5.2 records word join/split as a limit and
`docs/domain-facts.md` §1 frames it as a riwayah-level concern. They are
different problems. Across riwayāt it is a non-issue; within a riwayah it is
extension (b). The ADR conflates them and should separate the sentences.

### (b) A third Hafs script that splits or joins words differently — **this is a break, and larger than ADR-001 §5.2 admits**

ADR-001 §5.2 is honest that `Location`-scoped ordinals fail and says "it affects
only the container". That understates it, because ADR-001 §5 also says
"**every stable reference in the system is a `SlotId`**".

What actually changes:

| Artifact | Change |
|---|---|
| `model/address.py` | `SlotId` key shape → verse-scoped |
| `ScriptAdapter.read(text, at: Location)` | **signature break** — a script that joins two words cannot emit two `Reading`s |
| `canon/build.py: Reading -> ScoreWord` | **signature break** — same |
| `ScoreWord` | `Location`-keyed; the container itself is the unit that no longer aligns |
| `ledger.yaml`, `variants.yaml` | every row rekeyed |
| `migrations/*.yaml` | the migration format is itself `SlotId`-keyed |
| every fixture in ADR-008 §2 | rekeyed |

Two things make this urgent rather than theoretical. First, the two present Hafs
witnesses agree on word division **only because the importer forced them to** —
`tools/import_indopak_source.py` splits 37:130 `اِلْيَاسِيْنَ` into two words to
match Uthmani. The premise is manufactured, not observed. Second, D7 shows
IndoPak *already* carries evidence that crosses a word boundary, so the
word-scoped signature is already insufficient for the two scripts in hand.

Making `read` and `canon.build` verse-scoped and slot ordinals verse-scoped
**now** costs almost nothing (no data files exist yet) and converts a break into
a non-event. That is the single cheapest hardening available in this review.

### (c) Restoring `character_phoneme_mappings` from the frozen baseline — **additive, one missing field**

I read the frozen baseline. Rows are per source word; cells carry
`chars, role, status, phonemes, phoneme_indices, tag, share_group,
source_letter_index(es), phoneme_rule_tags, secondary_tags`. Corpus totals:
591,293 cells, 109,458 with a `share_group`.

| Baseline field | Reconstructed from | ADR sections touched |
|---|---|---|
| `chars` | `Grapheme` via `Spelling` | none |
| `phonemes`, `phoneme_indices` | `Spelling` → `(slot, aspect)` → `Attribution.sound` | none |
| `share_group` (109,458) | `Attribution.slots` arity / shared `SoundId` | none |
| `status: present/dropped/inserted` | `Attach` = `HOSTS`/`SILENT`/`slots == ()` | none |
| `status: shortened` (5,368) | `HOSTS` short sound + `ILTIQA_REPAIR` occurrence | none |
| `tag` (25 distinct) | `Occurrence.rule` | needs D8's missing members |
| `role: base / haraka` | `SlotFact` `LETTER` vs `NUCLEUS` | none |
| **`role: madd` (53,155), `role: tanween` (8,893)** | **not reconstructible** — the carrier grapheme and the haraka grapheme both classify `fact=NUCLEUS`, as does the tanwīn mark | **`model/inscription.py`: `Grapheme` needs a grapheme-class field** |
| `source_letter_index` | grapheme order within the word | needs `Grapheme` to carry its index |

So: a new module under `render/` (which may import `model`, and `Inscription`
lives in `model/`, so no dependency rule bends), plus one field on `Grapheme`.
No ADR decision is reversed. Fixture 21 would have caught the missing field,
which is the coverage check working as designed — good.

That I could answer all three from the documents, with only (b) coming out as a
break, is itself the finding: the extensibility claims mostly hold.

---

## 5. Open questions — are they the right nine?

**Right and well-stated:** §7.1 (L1 residue — correctly named as *the* question),
§7.2 (ṣilah closure), §7.3 (occurrence volume), §7.4 (`write` totality),
§7.6 (word join/split), §7.7 (يسٓ/نٓ wajh).

**Weak:** §7.8 (`Colouring` aspect-scoping). This is not open — ADR-001 §3.3
states the resolution ("each determines its own aspect without a field") and
ADR-002 §2 tabulates it. It is a recorded forward trigger, which is a different
thing, and listing it alongside "is the whole architecture viable" flattens the
list.

**Checkable now, and I checked it:** §7.9 (IndoPak's 4 extra `ࣝ` sites). Three of
the four sit at a word where Uthmani writes an ordinary waqf sign
(7:184:2 `ۗ`, 12:29:4 `ۚ`, 28:23:24 `ۖ`); only 7:23:4 has no Uthmani mark at all.
That is consistent with the evidence pack's classification and is strong enough
to close the question as "advice, not sakt, pending a domain reference for
7:23:4". It does not need to occupy a slot on a nine-item list.

**Missing, and should be on it** (in order):

1. Whether the tanwīn nūn can be merged without violating E1 (D1). This is a
   design question, not an implementation detail, and it is the largest.
2. How nasalization reaches output after `Consonant.nasalized` is deleted (D2).
   10,667 tokens; fixture 20 depends on the answer.
3. Which layer supplies the hamzat al-waṣl helping vowel, given 162 IndoPak
   evidence sites (D6).
4. Whether L1 can be satisfied by relocating facts rather than deriving them —
   i.e. what the harness must report besides the residue (D5b).
5. Whether the boundary-conditional slot at 27:36:8 is expressible (D3). The set
   currently asserts it is settled.
6. Whether `Attests` may name a single `Rule` (D4).

---

## 6. What should change before authoring — the AMEND list

Blocking:

1. **D1** — resolve tanwīn idghām against E1. Name the mechanism in ADR-004 §2/§4
   and show the `هُدًى مِّن` trace.
2. **D2** — restore a nasal feature to `Sound.Consonant`, or state that `render/`
   keys on `(features, rule)` and accept the consequence for ADR-002 §5.
3. **D3** — re-derive ADR-006 §4.1's four-row table against measured output; two
   rows are wrong. Then either add the vocabulary member for boundary-conditional
   slot presence or record 27:36:8 as an open exception-test failure.
4. **D4** — `Attests` carries a rule class, not a `Rule`; A1 adjusted to match.
5. **D5** — replace S1 with the three-rendition `HOSTS` check; add the provenance
   split and the `Inert` count to the ADR-008 §3 report.

Strongly recommended, cheap now and expensive later:

6. **D7 / (b)** — make `read`, `canon.build` and slot ordinals verse-scoped. Add
   U+08D9 (54 sites) to the attestation inventory and the 55-word tanwīn class to
   the derivation registry.
7. **D6** — add the helping-vowel row to ADR-003 §6 and the 162 sites to the
   fixtures.
8. **D8** — add the missing `Rule` members; reconcile ADR-004 §3 and ADR-003 §6
   on who owns imāla and tashīl.

Editorial:

9. **D9** — state L2/I3 scope. **D10** — fix the `ءَامَنُوا۟` example.
   **D12** — state that `GraphemeId` is position-ordered. Move §7.8 and §7.9 off
   the open list; add the six items from §5 above.

---

## 7. Where I am least confident

- **D11** (advice / script-relative plans). R3's position is defensible and the
  ADR states the consequence honestly. I raise it because the owner's requirement
  is phrased at the API surface, not because I think R3 is wrong.
- **D9** (L2 scope). I am confident the text is ambiguous; I am less confident it
  would actually mislead an implementor, who would probably reach the per-build
  reading unaided.
- **D3's second half** (41:44). I verified that `COLOUR = TASHIL` alone cannot
  produce the measured `ʔ a ʔ a`, but I did not establish what the *right*
  canonical description of `ءَا۬` is — only that the ADR's is incomplete.
- I did **not** attempt to falsify the unit-hood criterion by finding a word no
  `Slot` sequence can represent. I probed the hard cases named in the documents
  (ṣilah, leen, `هُوَ` at waqf, the seven alifs, tanwīn, hamzat al-waṣl, the
  muqaṭṭaʿāt) plus 27:36:8 and 41:44, and only 27:36:8 resisted. A systematic
  sweep over all 77,433 words is phase 1's job and I could not substitute for it.

---

**Verdict: AMEND** — items 1–5 of §6 are blocking; 6–8 are cheap now and
expensive after any data file exists.
