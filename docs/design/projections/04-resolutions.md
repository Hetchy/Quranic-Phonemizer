# 04 - Resolutions: what the review asked, and what was decided

Status: **decisions**. Answers [03-review](03-review.md) item by item at head
`9c7b810`. Every claim here was re-verified against source at this head; where
the review's own census was wrong, the correction is stated and marked.

Decisions taken by the project owner are marked **[owner]**. Everything else is
resolved against the source or against a measurement recorded here.

Cross-reference style is settled by this document and applied when 00-02 are
edited: `00-audit §4.1`, `01-design §6`, `02-gate §3.1`, `03-vocabulary D2`,
`ADR-013 §4`, `04-resolutions B1`. A bare `§N` always means this document.

## 0. Summary

Four owner decisions, one new blocker the review did not find, two of the
review's own claims corrected.

| | Decision |
|---|---|
| **[owner]** cross-word merged sound | the **host word** owns it. Legacy's allocation is reproduced inside the legacy adapter, never in the native projection |
| **[owner]** public type names | one namespaced module; domain names kept unchanged; nothing re-exported bare at package root |
| **[owner]** rule vocabulary | the 40-member `Rule` plus the 7-member `RuleFamily`. No third grouping axis |
| **[owner]** plain attribution | `by` becomes optional. `Rule.PLAIN` leaves the public enum; absence of `by` *is* plain |

Two new blockers, both the same shape - a live type or name with no producer,
hidden inside the verse-mode parity floor:

- **B5**, `Rule.MADD_TABII` has no producer for ordinary madd tabii, which is
  the most frequent tag in the entire legacy corpus.
- **B6**, nothing in the package emits an insertion, so the 46 sites needing
  a helping kasra are each missing a phoneme.

New design question, raised by the owner and answered with a measurement in
§5: consumer overload is an **API** gap, not a projection gap. `Mappings`
grows a read API; it does not split, and named profiles stay closed because
the payload evidence ADR-013 asked for now exists and does not justify them.

Review claims corrected: **N1** (`TARQEEQ` emits no `Recolour`), **N2** (`Word`
does not collide, and the package already carries two internal name
collisions).

---

## 1. Blockers

### B1. The classification law, made unconditional and per-occurrence

**Upheld, with both of the review's corrections and one of its own.** The set
has 20 members (`model/canon.py:334-368`), not 18, and membership is per-rule
while the fact is per-occurrence: `PausalGlide` mints a `Rule.MADD_TABII`
occurrence whose effects are `Realize` plus `MergeInto`
(`rules/madd.py:65-80`), so that occurrence owns a `Hosts` edge today.

**N1 - the review is wrong about `TARQEEQ`.** 03-review B1 says
"`TAFKHEEM`/`TARQEEQ` reach a sound through `Recolour`". `Tarqeeq.look` returns
`_classification(Rule.TARQEEQ, at)` with an empty effect tuple
(`rules/annotation.py:129`, `:24-27`). Tarqeeq emits nothing at all. It reaches
its sound through `Classifies`, like the izhars, not through `Recolours`.

**The law, restated.** Drop the conditional form. Every occurrence in the
document, whatever its rule, must reach at least one sound through at least one
edge:

> Every occurrence owns at least one `Hosts`, `Inserted`, `MergedInto` or
> `Silent` attribution, **or** at least one `Recolours`, `Relengths` or
> `Classifies` modifier. The only occurrences exempt are those whose rule is in
> the closed soundless list `{ISHMAM, SAKT}`, and an exempt occurrence must
> still name every participant its family's schema requires.

A build that emits zero `Classifies` edges now fails on the first izhar in the
corpus. The old form ("every classification-only rule *that names a sound* has
a `Classifies` edge") was satisfied verbatim by emitting nothing.

`CLASSIFICATION_ONLY` stays in `model/canon.py` as the trigger set the law is
checked over, but its docstring stops claiming that its members own no sound:
one member has an occurrence shape that does.

**The 20 members, and the edge each occurrence must reach.**

| Rule | Minted by | Effects today | Edge after C2 | The sound it reaches |
|---|---|---|---|---|
| `izhar_halqi` | `NoonSakinah` | none | `Classifies` | the noon's onset consonant |
| `izhar_mutlaq` | `NoonSakinah` | none | `Classifies` | the noon's onset consonant |
| `izhar_shafawi` | `MeemSakinah` | none | `Classifies` | the meem's onset consonant |
| `lam_qamariyyah` | `ArticleLam` | none | `Classifies` | the article lam's onset consonant |
| `idgham_mutajanisayn_naqis` | `Idgham` | none | `Classifies` | the source's onset consonant, which survives |
| `tafkheem` | `Emphasis` | `Recolour` x1 or x2 | `Recolours` x1 or x2 | the consonant, and its fatha where emphasis spreads |
| `tarqeeq` | `Tarqeeq` | **none** | `Classifies` | the raa's onset consonant |
| `iltiqa_repair` | `IltiqaRepair` | `Relength(SHORT)` | `Relengths`, or `Hosts` via `Insertion` after C8 | the long vowel it shortens; or the helping kasra it inserts (**B6**) |
| `imala` | `CanonicalColour` | none | `Classifies` | the nucleus vowel, quality `e` |
| `tashil` | `CanonicalColour` | none | `Classifies` | the hamza's onset consonant |
| `ishmam` | `CanonicalColour` | none | **none** | soundless: see below |
| `silah` | `Silah` | none | `Classifies` | the nucleus long vowel |
| `sakt` | `Sakt` | none | **none** | soundless: see below |
| `wasl_start` | `WaslHamza` | none | `Classifies` x2 | the prosthetic hamza's onset consonant and its helping vowel |
| `madd_tabii` | `PausalGlide` only | `Realize` + `MergeInto` | **`Hosts` + `MergedInto`** | it owns its sound. See **B5** for the ordinary case |
| `madd_wajib_muttasil` | `MaddClass` | none | `Classifies` | the long vowel |
| `madd_jaiz_munfasil` | `MaddClass` | none | `Classifies` | the long vowel |
| `madd_lazim` | `MaddClass` | none | `Classifies` | the long vowel |
| `madd_arid_lil_sukun` | `MaddClass` | none | `Classifies` | the long vowel |
| `madd_leen` | `MaddLeen` | none | `Classifies` | the leen letter's **onset consonant**. See **N3** |

**The two soundless exceptions, named.**

- `ishmam` is lips rounding to show a vowel that is not pronounced. At 12:11
  the vowel it gestures at is merged away, so there is no sound to classify.
  The occurrence carries its target participant and nothing else.
- `sakt` is a pause, not a sound, and the fact it records is already published
  as `Word.junction_after = sakt`. The occurrence names the word-final unit as
  its participant.

Both are closed by name. Adding a third requires editing this list, which is
the point of a closed list.

**N3 - madd leen classifies a consonant, not a vowel.** `MaddLeen` fires on a
unit whose nucleus is `SILENT` (`rules/madd.py:214`) and emits nothing, so the
only sound at that unit is the waw or yaa **consonant**. The model never
lengthens a leen. That is defensible - the leen is a glide held longer, not a
segment change, and the notation has no token for it - but the projection must
say so rather than leave a `Classifies` edge pointing somewhere a reader does
not expect. `01-design §6` states it; `02-gate §6` gets a leen fixture that
asserts the edge lands on the consonant.

**Lands in:** 00-audit §4.1 (18 -> 20, and the per-occurrence correction);
01-design §6 (the table above, and the corrected closing claim); 02-gate §4.4
(the unconditional law).

### B2. Ishmam keeps a canonical home

**Upheld.** The Uthmani inventory declares `U+06EB` as
`{fact: ANNOTATION, cls: annotation, role: ishmam, value: ISHMAM}`
(`data/riwayat/hafs/scripts/uthmani.yaml:79`), live at 12:11, and
`orthography/write.py::_slot` writes any slot annotation whose value names a
pen role (`write.py:185-191`). Removing `ISHMAM` from the slot with no
replacement canonical input loses the round-trip mark and the only input from
which `rules/annotation.py` emits the occurrence.

**Decision: ishmam takes the same carve-out imala takes.** It stays a canonical
fact on the unit under whatever name `03-vocabulary D2` settles on, and the
occurrence is the classification over it - the shape `DIVINE_NAME` gets. The
alternative (teaching `write` the selection) moves khilaf resolution into the
writer for one site, and D2's own argument against that for imala applies
unchanged here.

This means D2's sentence "`IMALA` and `ISHMAM` are rule occurrences and are not
unit tags" is false as stated for both members, not just imala. It becomes:
both remain canonical unit facts, and both additionally get an occurrence.

**Lands in:** 03-vocabulary D2; ADR-013 §4; 00-audit §4.6 (which currently ends
"`ISHMAM` is unaffected: no script writes it and `write` never reads it" - both
halves are false).

### B3. The gate, made executable

Three legs, three resolutions.

**Leg 1 - word grouping. [owner] The host word owns a merged sound.**
`render/recite.py:50-79` credits a cross-word merged sound to the word whose
unit carries the `Hosts` edge, and that is the promise `phonemes` publishes.
Legacy's allocation is not a promise of the *native* projection.

It remains a promise of the *legacy adapter*, and no fifth disposition is
added. The `Hosts`/`MergedInto` pair records both sides, so re-slicing to
legacy's allocation is a pure function of the document - which is precisely the
claim the redesign makes. `tools/parity.py`'s current bucketing ("A sound
merged across a word boundary can be credited to either word") stops being an
excuse and becomes the adapter's job.

If a merger site turns out **not** to be reconstructable, that is a measured
finding, and it is recorded as a residue class in
`docs/conformance/gate-residues.md` under leg 2's mechanism - not as a new
disposition invented in advance of evidence.

**Leg 2 - the corrections ledger already exists and is called
`docs/conformance/gate-residues.md`.** 02-gate's phrase "a reviewed corrections
ledger" appears three times and names nothing. The artifact that already plays
the role has 56 classified regression rows, a domain reason per class, and a
ratchet in `tools/floor.py`. 02-gate §1's `correction` disposition points at it
and adopts its form: a named class, the evidence for the direction, and a floor
that may only rise. Verse and continuous rows inherit the class of their
word-mode origin.

**Leg 3 - the job, named.** 02-gate §7 currently requires a full-matrix pass
with no runner. What lands:

| | Concretely |
|---|---|
| harness | `tools/projection_parity.py --adapter NAME --mode word\|verse\|continuous`, printing `N/M rows match (P%)` in the shape `floor.py` already scrapes |
| registry | one `floor.py::HARNESS` entry per adapter; the entry's value grows from `(script, label)` to `(script, argv, label)` so a second axis does not need six scripts |
| floors | six adapters x three modes, seeded from the first measured run and recorded in `gates.yml`, never guessed |
| CI job | a `projections` job in `.github/workflows/gates.yml`, beside `regression` |
| schema tests | `tests/test_projection_schema.py` hosts 02-gate §5's negative tests |
| domain tests | `tests/test_projection_domain.py` hosts §6's adequacy matrix |
| residue report | a new section of `docs/conformance/gate-residues.md`, plus a machine-readable copy uploaded as a CI artifact |
| sample | a fixed deterministic ref set runs on every pull request; the full `1-114` matrix gates the merge |

**Lands in:** 02-gate §1, §3, §3.1, §7; `docs/conformance/gate-residues.md`
(new sections); `tools/floor.py`; `.github/workflows/gates.yml`.

### B4. Plain is an absence. [owner]

`by` becomes `int | None`. An attribution with no `by` means no rule claimed
this outcome: the Score's own value, realized by default. `Rule.PLAIN` leaves
the public `Rule` enum and no plain occurrence appears in `occurrences`.

The referential law in 02-gate §4.2 becomes "every `by` that is present
resolves to an occurrence", which is still falsifiable and still unconditional
over the edges that carry one.

Two reasons this is the right side of the choice, beyond the schema being
self-consistent:

- `rules_by_sound(s)` returning `[plain]` for most sounds in the corpus is
  exactly 00-audit F1's complaint restated. Absence is the honest encoding of
  absence.
- `Rule.PLAIN` is currently mapped in `FAMILY_OF` to `RuleFamily.ELISION`
  (`model/canon.py:330`), which it is not. Dropping the member drops the wrong
  answer with it.

The engine may keep minting its synthetic plain occurrence internally; this is
a wire-format decision, and the builder omits the field for it. Whether
`Rule.PLAIN` also leaves the internal enum is C6's question, not this one.

**Lands in:** 01-design §3.5, §4.2; 02-gate §4.2, §4.3.

### B5. `madd_tabii` has no producer, and it is the most common tag in the corpus

**New. Not in the review.** `Rule.MADD_TABII` is minted in exactly one place:
`PausalGlide` (`rules/madd.py:67`). `MaddClass` deliberately does not emit it -
"`MADD_TABII` is deliberately not emitted here: it is the default that holds
wherever none of the five outcomes applies" (`rules/madd.py:145-147`) - and
returns `None` for that case.

So an ordinary madd tabii - the `aa` of `qaaluu`, the dagger alef of the divine
name - produces **no occurrence at all**. Not an occurrence with a missing
edge: nothing.

Measured against the frozen baseline
(`research/legacy-baselines/verse.tajweed_mappings.jsonl.gz`, all 77,481 rows):

```
41543  source_rules: madd_tabii     <- the single most frequent legacy tag
31715  source_rules: tafkheem
13252  source_rules: hamza_wasl_silent
 5283  source_rules: lam_shamsiyah
 4568  source_rules: vowel_silent
```

`madd_tabii` is 30% of all legacy rule attributions. The `tajweed_mappings`
adapter cannot reproduce one of them, and no amount of `Classifies` fixes it,
because `Classifies` needs an occurrence to hang off.

This is the real cause of 00-audit F1's headline. F1 says `AnchoredSound.rule`
is `plain` for every madd vowel because the sound edge is missing; for madd
tabii specifically the *occurrence* is missing too.

**Fix - C5.** `MaddClass` emits `Rule.MADD_TABII` as its fifth outcome instead
of returning `None`: a classification-only verdict on every long-vowel nucleus
that no other madd rule claims. One branch rather than a sixth classifier,
because `MaddClass` already computes the negative and because "exactly one rule
of a family fires per trigger" (`domain-facts.md` §8.2) is easier to hold in
one place.

Scope and risk:

- No effect is emitted, so no sound changes and no parity floor moves.
- Occurrence counts change corpus-wide, so any fixture or digest that counts
  occurrences regenerates in the same commit.
- The interaction with `silah` needs one fixture and a stated rule: a `SILAH`
  nucleus sounds long when joined and already has its own occurrence, so the
  tabii default must not also fire there. `MaddClass.triggers` currently
  includes `NucleusKind.SILAH`.
- `PAUSAL_LONG` at a joined word is entangled with **M1** below; the tabii
  default must not fire on a nucleus whose length is itself in dispute until
  M1 is settled.

**Lands in:** 00-audit §4.1 and F1; 01-design §6 (as C5); 02-gate §6 (madd
row, and a tabii fixture); `rules/madd.py`.

### B6. Nothing inserts, so 46 words are missing a phoneme

**New. Not in the review.** `Inserted` is a live attribution type with a
docstring naming its case - "the 3:1 iltiqa fatha is the only genuinely
slot-less sound in the design" (`model/performance.py:102-104`) - and
**zero producers**. `Insert` is constructed nowhere in the package; the only
mention outside `engine/plan.py`'s own definition is the `conflict_key` match
arm.

Measured over the whole corpus in verse mode:

```
Inserted attributions, whole corpus:            0
tanween meeting a wasl hamza inside a verse:   46
of those 46, agreeing with legacy:              0
```

Every one is the same shape - the helping kasra that `domain-facts.md` §5.7
requires when a tanween meets a sakin, simply absent:

```
2:61:30    خَيْرٌ ۚ ٱهْبِطُوا۟     got  x aˤ j rˤ u n      want x aˤ j rˤ u n i
2:180:9    خَيْرًا ٱلْوَصِيَّةُ      got  x aˤ j rˤ aˤ n     want x aˤ j rˤ aˤ n i
4:171:31   ثَلَـٰثَةٌ ۚ ٱنتَهُوا۟    got  θ a l a: θ a t u n  want θ a l a: θ a t u n i
```

46 is exactly legacy's `iltiqaa_sakinayn_tanween` count in the frozen
baseline. `ILTIQA_REPAIR` exists, and its family is already
`RuleFamily.INSERTION` (`model/canon.py:326`) - but its only effect is
`Relength(SHORT)`, the *shortening* branch of iltiqa. The *insertion* branch
was never written, and the family name has been advertising the gap.

Like M1, this hides inside the verse-mode parity floor: word mode stops after
every word, so no cross-word iltiqa fires and none of the 46 appears among
`gate-residues.md`'s 56 classified rows. Verse mode is at 97.674% and its
residue is described only as "the same classes, plus propagation".

Consequences for the contract, beyond the missing sound:

- 02-gate §4.3's four insertion laws are **vacuous**. A build emitting no
  insertions passes all of them.
- 02-gate §6's `slotless repair` family row has no live case to fixture.
- `Insertion` is a dead type in the public schema, so no consumer has ever
  had to handle it and nothing proves the anchor-and-side encoding works.

**Fix - C8.** `IltiqaRepair` grows its second branch: where the sakin the madd
meets is reached across a tanween rather than a long vowel, emit
`Insert(anchor=(noon, AFTER), NUCLEUS, Vowel(I))` instead of `Relength`. One
classifier, two branches, because it is one domain rule with two repairs.

The other insertion the docstring names - the fatha on `الٓمٓ`'s final meem
before `ٱللَّهُ` at 3:1-2 - is cross-verse and this scan does not reach it. It
needs the continuous path (M10) to test, and it is a second fixture rather
than a second rule.

**Lands in:** 00-audit §4 (as a new gap); 01-design §6 (as C8); 02-gate §4.3
and §6; `rules/madd.py`.

---

## 2. Majors

### M1. D4's "no code change" is false, and the behaviour under it is a defect

**Upheld, and open question 2 is now answered by measurement.**

`engine/run.py:180-182` classifies `NucleusKind.PAUSAL_LONG` as long in the
plain path without consulting the boundary plan, and no join-path rule shortens
it. `rules/boundary.py:78-81` realizes it long *at a stop*, so the pausal case
is handled twice and the joined case is handled wrongly.

Measured: every verse containing a pausal-long unit, performed with all words
joined, compared against `research/legacy-baselines/verse.phonemes.jsonl.gz`.

```
pausal-long word occurrences: 79
disagree with legacy:         69

2:258:21   JOINED   أَنَا۠      got ['ʔ','a','n','a:']   want ['ʔ','a','n','a']
3:81:30    JOINED   وَأَنَا۠     got ['w','a','ʔ','a','n','a:'] want [...,'n','a']
```

Every disagreement is the same shape and the same word. The ten that agree are
verse-final, where the stop makes it long and both implementations say `a:`.

The domain sides with legacy: `PausalLong` is documented "short in wasl, long
at pause. The seven alifs" (`model/canon.py:150-155`), `domain-facts.md` §5.8
says the rectangular-zero alef "is silent in wasl but sounds 2 counts at waqf",
and §7.6 repeats it. **This is a live defect worth roughly 69 words of the
verse-mode parity floor**, currently absorbed and unclassified - it appears in
no `gate-residues.md` class.

Consequences for the documents:

- D4's decision survives untouched: the fact is lexical, decided in
  `canon/derive/` from the script and the lexicon, and moving it to the
  boundary rule would put lexicon lookup inside `rules/`.
- D4's *code* claim does not. `03-vocabulary §7` changes D4 from "none" to a
  docstring plus a rule fix, and §5's "no code change" sentence is struck.
- Open question 2 is closed: it is a defect. It is out of scope for this
  documentation PR and becomes a named follow-up with the measurement above as
  its regression test, plus a new `gate-residues.md` class so the floor stops
  hiding it.

### M2. Word-envelope fields

**Upheld.** `location`, `text`, `is_starting`, `is_stopping` are carried on
every legacy row (`b3bc53a:tajweed_mapping.py`, `char_phoneme_mapping.py`), and
`location` is the SDK's join key. All four are derivable from 01-design §3.1:
`Word.location`, `Word.text`, `Word.starts`, and `junction_after is stop`.

The row group is added to 00-audit §1's table and to 02-gate §3.3 and §3.5.

The result-envelope counters (`ref`, `entry_count`, `word_count`,
`phoneme_count`) are derivable from array lengths and get an explicit
`retirement` in 02-gate §3.1: a consumer computes `len(words)` rather than
reading a field the producer could get wrong.

### M3. The legacy surface inventory

**Upheld.** `PhonemizeResult.get_mapping()` (with `AlignmentEntry` and
`LetterMapping.display_char`), `text()`, `phonemes_str()`,
`phonemes_list(split=...)`, `show_table()` and `save()` are exported and
README-documented at `b3bc53a` and appear in no document. Dispositions:

| Legacy call | Disposition |
|---|---|
| `text()`, `phonemes_str()`, `phonemes_list(split=...)` | `addition` - trivial adapters over `phonemes` and `Word.text`; named in 02-gate §3.1 so they are not silently dropped |
| `get_mapping()` / `AlignmentEntry` | adapter over `letter_phoneme_mappings`; `display_char` comes from recited writing, so it is gated on 01-design §5 being total |
| `show_table()`, `save()` | `retirement` - presentation and IO, not contract. Named with this document as the approval |
| `mode="simple"` | `retirement`, already approved in 03-review |

### M4. The rule census

**Upheld.** The legacy enum at `b3bc53a` has 33 members
(`quranic_phonemizer/tajweed_rule.py`), not 30. 00-audit §5's mapping table
omits `HAMZA_WASL_SILENT`, whose branch counterpart is the renamed
`WASL_ELISION`.

Measured over the frozen verse baseline, 26 of the 33 actually occur, and
`hamza_wasl_silent` is the third most frequent tag in the corpus at 13,252
attributions. The rename is not cosmetic and the adapter test pins it by name.

### M5. Iqlab

**Upheld on both counts.**

- Legacy *did* tag noon iqlab. `b3bc53a:tajweed_classification.py` includes
  `iqlab_noon` in `NOON_RULE_TAGS`, and the frozen baseline carries 270
  `iqlab_noon` attributions against 292 `iqlab_tanween`. 00-audit §2.1's row
  "legacy tags iqlab only on tanween, never on noon" is wrong; what is
  tanween-only is the *synthesized mini-meem cell*.
- Uthmani writes no iqlab meem to bind. `U+06E2`/`U+06ED` are IndoPak;
  Uthmani iqlab is unmarked (`corpus_sources/riwayat/hafs/scripts/README.md`),
  and the exhaustive Uthmani mark inventory contains none.

So 01-design §9's first shipping question aims C3 at a glyph that does not
exist in the script this design is scoped to. It is rewritten: the question is
whether the *IndoPak* inventory binds it, deferred with IndoPak; and exact
legacy compatibility for `character_phoneme_mappings` needs a presentation
adapter that synthesizes the mini-meem cell where legacy promised it, which is
02-gate §3.5's job and not a graph fact.

### M6. Participant roles

**Upheld.** Under 01-design §3.5's definitions the sakin noon of an idgham is
the `source` and the following letter the `trigger`; 02-gate §3.3 says "the
disappearing trigger", which is the opposite assignment. No document contains a
worked role assignment for any family.

Also upheld: C1 touches behaviour. `engine/plan.py:156-164`
(`assimilated_from`) reads `parts.slots[:1]`, and `engine/laws.py:154-164`
(`check_attestations`) derives attested families from *all* participant slots.
01-design §6's "no rule behaviour changes as part of C1-C4" weakens to "no
verdict changes, and the two participant-order readers are converted with a
pinning test".

A role table with one worked example per family lands in 01-design §3.5. The
worked examples themselves live in the examples document (§5 below), and the
role assignment for every family is settled there before C1 is implemented.

### M7. `Evidences.fact` publishes members the public `Unit` cannot answer

**Upheld.** `SlotFact.SAKT` and `SlotFact.ANNOTATION` are live producers
(`orthography/inventory.py:166-168`, `canon/ledger.py:130`,
`canon/passes.py:92`), but the §3.2 `Unit` has no annotation field and sakt
lives on `Word.junction_after`.

Resolution: narrow the public enum to `letter | onset | nucleus`. The sakt
grapheme reaches its word through `Decorates` on the word-final unit plus
`Presents` its `sakt` occurrence; the annotation graphemes reach their unit the
same way. B2 changes this slightly - if ishmam and imala stay canonical unit
facts, `ANNOTATION` has a real `Unit` field to point at and may stay. That
choice is D2's, and this document records that the public enum follows D2
rather than leading it.

### M8. `source_index` is three indices

**Upheld.** `model/inscription.py:39` documents `Grapheme.index` as "Ordinal
within its word. The frozen baseline's `source_letter_index`" - word-local.
01-design §3.3 defines `source_index` as the ordinal in the requested
inscription, and 02-gate §4.2 depends on that reading while §3.5 equates it
with the word-local legacy key.

Resolution: publish both, named for what they are. `Glyph.word_index` is the
word-local ordinal and is the legacy join key; `Glyph.source_index` is the
scalar's ordinal in the whole requested inscription and is what §4.2's
concatenation law walks. Non-base scalars count in both.

### M9. The one-question criterion at the projection boundary

**Upheld.** 03-vocabulary §8 claims the criterion "every field a projection
exposes answers one question" is met by 01-design §3.2 - the section that
republishes the two-axis `Onset` and says SDKs "may derive" booleans.

Resolution: retire the criterion at the projection boundary and say why.
`Onset` is a closed five-member enum whose every impossible combination has a
recorded domain reason (03-vocabulary §4), and a consumer matching on five
names is not worse off than one matching on two booleans with three impossible
pairs. §8's third bullet is rewritten to state that, rather than asserting
compliance §3.2 declines.

### M10. `continuous` has no execution path

**Upheld.** `tools/parity.py` is verse-by-verse by design
(`MODES = ("word", "verse")`, and its comment says continuous "joins across
verse boundaries, which a verse-by-verse harness cannot plan for"). The frozen
continuous reference is one 77,433-word request whose
`character_phoneme_mappings` alone is 135 MB uncompressed, and 01-design §1.2
forbids partial emission.

Resolution: state the request the harness issues per mode.

| Mode | Request the harness issues |
|---|---|
| `word` | one request per verse, `BoundaryPlan` all `STOP` |
| `verse` | one request per verse, `BoundaryPlan` all `JOIN` with an `EDGE` at the end |
| `continuous` | one request per **surah**, joined throughout, with a one-word overlap on each side used only to resolve cross-boundary rules and then discarded |

The overlap is one word because `domain-facts.md` §3.2 fixes the maximum
cross-word rule reach at one word of lookahead. The seam-equivalence argument
is a law: a surah-chunked continuous run and a hypothetical whole-corpus run
agree on every sound, because no rule reads past the overlap. That law is
testable on a pair of adjacent surahs without ever materializing 135 MB.

### M11. Public type names. [owner]

**Corrected, then resolved.**

**N2 - the review's list is wrong twice.** There is no `class Word` anywhere in
the package, so `Word` does not collide; nine names do, not ten. And the
package *already* carries two internal collisions: `Silent` is both a nucleus
(`model/canon.py:123`) and an attribution (`model/performance.py:124`), and
`Attests` is both a spelling edge (`model/inscription.py:60`) and a derivation
outcome (`canon/derive/vocabulary.py:49`). "Two types with one name in one
package" is therefore already a per-module convention in practice, which
weakens the reason 01-design §1.3 gives for rejecting `Reading` - though not
the decision, since eight modules import `Reading` under that name and nothing
imports a public `Mappings`.

**[owner] decision: one namespaced public module, domain names unchanged.**
The public document types live in a single module and are never re-exported
bare at package root, so a consumer writes `mappings.Hosts` and an internal
reader is never in doubt about which `Hosts` is meant. `SoundNode` reverts to
`Sound`; the `Node` suffix 01-design §3.4 introduced for this reason is
withdrawn.

Convention 1 is restated to match what the code does: **one type per name per
module**, plus a named list of words that are deliberately reused across the
model and public boundary because they mean the same thing at both.

---

## 3. Minors

Each is accepted as written unless noted.

- **`TajweedEntry.to_dict` omits empty rule lists.** 02-gate §3.3 states that
  absent equals empty. Confirmed against the frozen baseline: a row with no
  rules is `{"char": "ه"}` with neither key present.
- **Split-extension rows and `EXTENSION_FALLBACK_CHARS`.** Added to §3.3, which
  currently omits what §3.2 spells out for `silent_flags`.
- **Manifest digests** are over the uncompressed JSONL, not the committed
  `.gz`; 02-gate §2 says so. The manifest also pins no script, riwayah or
  notation while `MappingsRequest` carries all three; those three fields are
  added to the manifest.
- **The phonemes baseline is committed twice** (`research/legacy-baselines/`
  and `tests/snapshots/phonemes/`, byte-identical). `tests/snapshots/` becomes
  the reference and `research/` points at it. 02-gate states the script scope
  of every adapter: Uthmani only, because legacy has no IndoPak oracle.
- **`MappingsRequest.boundaries`, `Word.junction_after`, `Word.starts`** store
  one fact three ways. `BoundaryPlan.started_on` already derives `starts`. The
  two `Word` fields are kept for ergonomics and named in 01-design §2 as the
  sanctioned exception to the single-direction rule, with the derivation
  written out so a consumer can check them against each other.
- **`Recolours.feature` and `Relengths.length`** publish `engine/plan.py`
  enums. `SoundFeature` and `Length` move into `model/` as part of C2.
- **`score_digest: str` is singular** while C4 assembles one document from N
  per-verse Scores. C4 defines the range digest: the digest of the ordered
  tuple of per-verse digests, so it is stable under the same range and differs
  under any other.
- **`CanonicalVariantSelection` is undefined.** The model type is
  `VariantSelection`; the field is renamed and the canonical ordering rule -
  khilaf ids sorted by name, options by their declared order - is stated in
  01-design §2.
- **`Unit.spelled`** is renamed `letter_name` for the wire, since "spelled"
  reads as "is written" next to `Glyph` and `spellings`. This is the same class
  of problem as `nunation`, and both are settled by the vocabulary document
  (§5), not here.
- **F8** (`render/recite.py` occupies ADR-005's `recite` name) gets an owner:
  it is renamed as part of C4, which is the commit that introduces the public
  entry point and would otherwise ship the collision.
- **Unfalsifiable laws.** 02-gate §4's "the correct `SlotFact`", "its intended
  typed edge" and "compatible with the glyph's spelling edges" name their
  expected edge and value or move to §6's fixture matrix. The iqlab law is
  struck rather than rewritten - see M5, Uthmani has no iqlab meem.
- **`phonemes` has no consumer row** in 01-design §8, and the render marker `Q`
  (`data/render/ipa.yaml`, `qalqala`) is indistinguishable from a segment in
  the flat token list. Resolution: the alignable/marker distinction is **not**
  P1's job. `phonemes` is a token stream and `Q` is a token in it; a consumer
  that needs to exclude render-only markers from an index uses `Mappings`,
  where the `Release` sound is a typed node it can filter. That is stated in
  §1.1 as a reason to use `Mappings`, and §6 gets a `Release`-token fixture.
- **`Sound.word` for merged and inserted sounds** follows the existing policy
  in `render/recite.py:50-79`: the host unit's word, and an inserted sound
  bucketed by its anchor unit's word regardless of `Side`. Stated in
  01-design §3.4, with a `Side.BEFORE`-at-word-start fixture in §6.

---

## 4. Open questions, closed

| | Question | Answer |
|---|---|---|
| 1 | Cross-word merged-sound ownership: promise or defect? | **[owner]** Neither. The host owns it natively; legacy's allocation is adapter-only. B3 leg 1 |
| 2 | Is long-when-joined `PAUSAL_LONG` correct Hafs? | **No.** Measured: 69 of 79 occurrences disagree with legacy, all `ana` -> `ana:`. A live defect, named as a follow-up. M1 |
| 3 | D1/D2 ordering against C1-C4 | D1 and D2 land **first**, before 02-gate §7 step 1, because D1 regenerates every digest and fixture and D2 decides the `Unit` shape the schema freezes. 02-gate §7 becomes a seven-step list beginning with them |
| 4 | `MappingsRequest.ref` grammar | `ref` addresses **words**, not only verses: `surah:ayah:word` at both ends, with the word part optional and defaulting to the first and last word of the named verse. §2's fixtures need a range beginning inside a verse, and a verse-only grammar cannot express one |
| 5 | `Attests` versus `Presents(OccurrenceRef)` | They are independent, and `Presents` is not the resolution of `Attests`. `Attests` is a *script* claim ("this shadda witnesses an assimilation here") made by the inventory with no knowledge of which rule fired; `Presents` is a *performance* link made after the rules ran. A glyph can attest a family that no occurrence produced - that is exactly what `engine/laws.py::check_attestations` reports, one-directionally, and the corpus has 178 such Uthmani rows today. Stated in 01-design §4.4 |

---

## 5. One document, or several? A read API, not more projections

Raised by the owner: if a consumer only wants to know which tajweed rules
apply to a verse, is handing them `Mappings` an overload? Should there be
several smaller projections instead of one large one?

Three different questions wear one coat here, and they have different answers.

| | Question | Answer |
|---|---|---|
| 1 | What does the producer **compute and serialize**? | One document. 01-design §1.2 stands, and §5.1 below is the evidence it invited |
| 2 | What does a caller **receive over a wire**? | A transport concern. Field selection at the transport layer needs no second contract |
| 3 | What does a consumer **call**? | **A read API on the document.** This is the real gap, and it is new work |

The overload is real. It is an API gap, not a projection gap, and the two have
very different costs: a method is a pure function of a document a consumer
already holds, with no schema version, no digest, no gate law and no way to
disagree with the graph. A second projection is a second contract.

### 5.1 The size argument, measured

ADR-013 §6 said named profiles reopen "on evidence, not on principle: a
measured request payload too large for a real read path". The measurement was
never taken. It has been now - node and edge counts from the branch at this
head, sized against a representative serialized row per array.

| Verse | Words | Total | `glyphs` | `sounds` | `spellings` | `units` | `attributions` | `occurrences` | `words` |
|---|---|---|---|---|---|---|---|---|---|
| 1:1 | 4 | 14 KB | 19% | 17% | 19% | 16% | 15% | 10% | 4% |
| 2:5 | 8 | 26 KB | 22% | 22% | 19% | 15% | 14% | 5% | 4% |
| 2:255 | 50 | 141 KB | 20% | 23% | 18% | 15% | 14% | 6% | 5% |
| 2:282 | 128 | 408 KB | 20% | 23% | 17% | 15% | 14% | 5% | 4% |

Two things fall out, and both cut against splitting.

**No array dominates.** The distribution is flat and stable across verse
lengths. A tajweed-only profile - `occurrences` plus `units` plus `words`,
because resolving a noon from a tanween needs the unit - is **25%** of the
document. Dropping five of seven arrays buys 4x. It does not buy an order of
magnitude, because there is no single array to drop.

**Compression already buys 31x.** The frozen
`continuous.character_phoneme_mappings` baseline is 135,147,272 bytes of JSONL
and 4,291,471 bytes on disk as `.gz`. This shape of document - repeated keys,
small integer values, a closed string vocabulary - compresses at 31.5:1. At
that ratio 2:255 is roughly **4.5 KB** on the wire and 2:282 roughly 13 KB.

A 4x saving on a 4.5 KB payload is not a reason to ship a second contract, and
it is certainly not a reason to make every completeness law in 02-gate §4
conditional on which arrays were requested. **The evidence ADR-013 asked for
has arrived, and it says no.** The size driver is the requested *range*, which
is the caller's choice and already under their control.

### 5.2 The change-rate test, applied

01-design §1.1 splits `phonemes` from `Mappings` on change rate, not
convenience: the token stream is stable across every schema evolution of the
graph, so folding them together would make a consumer who wanted a list of
strings inherit breakage from graph changes that did not affect them.

Apply the same test to a hypothetical `tajweed` projection. It changes when
the rule vocabulary changes, when participant roles change, when a family is
split - which is exactly when `Mappings` changes, because it is the same
graph. Same change rate, so no split.

And the second half of the test is worse for it. Two projections that must be
**joined by the consumer** carry coupling cost, which is what made the five
legacy views drift. "Colour the script by rule" needs rules *and* spellings;
"which letters are silent" needs attributions *and* contributions. A `tajweed`
projection and a `script` projection would be re-joined by every consumer that
does anything visual - which is most of them.

### 5.3 The decision: a read API on `Mappings`

`Mappings` grows methods that answer the audited consumer questions directly,
each a pure function over the arrays. 01-design §5 already names seven derived
indexes and calls them SDK helpers in an aside. They stop being an aside and
become the documented entry point: the graph is what you reach for when a
method does not exist, not what you start from.

The surface, from 00-audit §2's census of what consumers actually invent:

```text
m.rules()                  every occurrence, with role-labelled units,
                           the sounds it reaches, and the glyphs to point at
m.rules_at(word=3)         the same, filtered
m.rules_on(glyph=12)       what to colour this glyph with
m.silences()               every unheard glyph, with the rule that took it
m.tokens()                 the flat token stream
m.tokens_by_word()         grouped, host-owns allocation
m.letters()                the legacy letter-to-phoneme grouping
m.recited_text()           recited writing, ADR-005's serializer
m.display_glyph(sound, policy)   which glyph to paint for a sound
```

Each returns a small frozen record, not a slice of the graph. Each is
documented with a four-line example. None of them is a wire format, so adding
`m.rules_by_family()` in a later release breaks nothing and needs no schema
version.

[05-vocabulary §1](05-vocabulary.md) is written as the reader-facing form of
this list and becomes the README's usage section when C4 lands - the root
`README.md` currently documents a `Phonemizer` class this branch does not
have, and it is rewritten in the same commit.

### 5.4 What is deliberately not added

- **No per-array flags.** Unchanged from 01-design §1.2: they are not
  independent, referential integrity forces a dependency order, and every
  gate law would become conditional on what was asked for.
- **No named profiles.** ADR-013 §6's condition for reopening was a
  measurement; §5.1 is that measurement and it does not justify them. The
  paragraph is amended to record the number rather than the promise, so this
  is not re-litigated without new evidence - a *bulk* build over a whole
  surah or the whole corpus would be new evidence, and that path already
  lands in a shard writer that repacks into its own rows.
- **No third projection.** §5.2.

**Lands in:** 01-design §1 and §5; ADR-013 §6 (the measurement replaces the
promise); 05-vocabulary §1; and `README.md` with C4.

## 6. Model work, restated

01-design §6's C1-C4, plus what this document adds.

| | Change | New? |
|---|---|---|
| C1 | semantic participant roles, with a per-family schema | roles settled by the examples document before implementation |
| C2 | retained modifier provenance: `Recolours`, `Relengths`, `Classifies` | `SoundFeature` and `Length` move into `model/` |
| C3 | total glyph contribution: `Presents` / `OrthographicOnly` | the iqlab meem drops out of scope with M5 |
| C4 | ref-to-document orchestration | also renames `render/recite.py` (F8) and defines the range digest |
| **C5** | `MaddClass` emits `madd_tabii` as its fifth outcome | **new, B5** |
| **C6** | `Rule.PLAIN` leaves the public enum; `by` becomes optional | **new, B4** |
| **C7** | the read API on `Mappings`, and the README rewritten around it | **new, §5.3**. Ships with C4, because it is what makes C4's entry point usable |
| **C8** | `IltiqaRepair` grows its insertion branch | **new, B6**. The one change here that alters sounds, so it moves the parity floor |
| D1 | `SlotOrigin` -> two booleans | lands first, before C1 |
| D2 | `DIVINE_NAME` -> `LexemeClass`; imala **and ishmam** stay canonical facts with occurrences over them | amended by B2 |

Named follow-ups, outside this design:

- the `PAUSAL_LONG` joined-length defect (M1), with the 69-word measurement as
  its regression test and a new `gate-residues.md` class until it is fixed.

C5, C8 and the M1 follow-up are the three that touch rule behaviour. C8 and M1
move the verse-mode parity floor - upward, since both currently disagree with
legacy and legacy is right in both. They are sequenced before the gate's step
1, or the floors are seeded against known-wrong output.

## 7. What still needs agreement before implementation

Two documents, in this order, and neither is written yet:

1. **05 - the public contract in plain words.** Every public name, what it
   means in domain terms, why it is spelled that way, and what was rejected.
   Written for a consumer who wants to know which tajweed rules apply to a
   verse and should not have to learn `Aspect`, `Onset` and `Hosts` to find
   out. It settles `nunation` against `tanween`, `spelled` against
   `letter_name`, and the rest of that class.
2. **06 - worked examples.** One contract example per linguistic case and per
   rule case, in a form a human can scan. It is where C1's role assignments
   are settled per family, and where every claim in 02-gate §6's adequacy
   matrix acquires a concrete row.
