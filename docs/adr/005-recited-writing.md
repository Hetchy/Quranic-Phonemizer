# ADR-005: Recited writing is a projection, not a layer

Status: **accepted**, amended after the simplicity and domain reviews.
Supersedes archived ADR-001 §2 "Recited writing", which proposed a
`RecitedWord`/`RecitedLetter` layer that was never built.

Scope note: this ADR designs the *mechanism* by which recited text is derived.
The public projection API is out of scope by the brief and is not designed here.

## 1. Decision

Recited writing is a projection over `(Score, Plan, Spelling)` using the
adapter's `write` — the inverse of `read`. No fourth layer.

```python
class Faithfulness(StrEnum):  SOURCE | RECITED
class Visibility(StrEnum):    SHOW | HIDE
class SpellDepth(StrEnum):    COMPACT | EXPANDED

def recite(performance, inscription, *,
           faithfulness: Faithfulness,
           silence:      Visibility,
           insertions:   Visibility,
           depth:        SpellDepth) -> str: ...
```

| Toggle | Acts on |
|---|---|
| `faithfulness` | which glyphs: the original graphemes, or a re-spelling of each slot's *performed* state |
| `silence` | filters slots attributed `Silent` or `MergedInto`, and the `Decorates` graphemes bound to them |
| `insertions` | `Inserted` edges are spelled by `write` at their `anchor` |
| `depth` | whether `Slot.spelled` runs appear as their compact graphemes or as spelled slots |

The four are independent because they act on different things: one picks the
*source* of glyphs, two are *filters over classification*, one picks the *slot
population*. All sixteen combinations are defined and none is special-cased.

(The first draft named the fourth enum `Spelling_`, a trailing underscore whose
only content was "not the other `Spelling`" — the same failure convention 1
bans. It is `SpellDepth`.)

## 2. Why no layer is needed

The current model cannot express any of this for one concrete reason:
`engine.py:79-82` flattens everything into `WordRealization.segments`, so at
output time there is no record of which slot a sound came from, whether a slot
was silent, or why. Retaining the `Plan` instead of flattening it is the entire
fix.

The three things recited text needs, and where each comes from:

| Need | Source |
|---|---|
| glyphs for sounds with no source grapheme | `ScriptAdapter.write` |
| which graphemes to drop, and why | the `Attribution` variant plus `by.rule`, or the `Spelling` classification |
| the performed state of each slot | the retained `Plan` |

`Insert` effects carry an `anchor: (SlotId, Side)` (ADR-002 §4.1), so placement
does not ride on `SoundId` stream order.

## 3. `write`

```python
def write(self, slots: Sequence[Slot], style: SpellStyle) -> str: ...
```

`write` is total over the canonical vocabulary for its script: every legal
`Slot` and every legal `SoundSpec` must have a spelling in every script of the
riwayah. A `SpellStyle` selects `SOURCE_FORM` (spell the Score slot) or
`PERFORMED_FORM` (spell the slot as the Plan left it — gemination from idghām,
a dropped final vowel, an inserted repair vowel).

Round-trip obligation, and the reason `write` is preferred over a rebuild:

> `write(read(verse_text).slots, SOURCE_FORM, COMPACT) == verse_text`
> for all 6,236 verses — 77,433 words — in both scripts.

This tests `Spelling` totality and adapter correctness in one assertion.
Neither of the other two spines has an equivalent.

The round-trip is stated over the **verse**, following ADR-001 §5's
verse-scoping, and it depends on `GraphemeId` being position-ordered: measured,
4,575 Uthmani words contain an internal space (`'مَّرْقَدِنَا ۜ ۗ'` carries two
structural marks in order) and 6,404 contain a tatweel, none of which
`Structural` positions on its own.

## 4. The renderability trigger

Spine B refused a recited-writing layer on the argument that `write` plus a
retained `Plan` suffices. `convergence-c.md` §3.3 correctly named the trigger
for that refusal failing, and it is adopted verbatim as a gate:

> Before a fourth layer is ruled out, a total `write` check must pass over: the
> 3:1 connected mīm fatha; hamzat al-waṣl helping vowels in all three
> grammatical flavours; madd ʿiwaḍ; tāʾ marbūṭa at waqf; and every muqaṭṭaʿāt
> expansion. **If any recited form requires an Arabic sequence that no `Slot`
> or `SoundSpec` can spell, the refusal has failed its own trigger and a
> recited-writing layer is warranted.**

This is a phase-2 gate (ADR-008 §4.2). Until it passes, "no fourth layer" is a
hypothesis, not a decision.

## 5. Worked shapes

**Silence shown vs hidden — `أُو۟لَـٰٓئِكَ` 2:5:1.** The wāw is not a slot
(unit-hood criterion). Uthmani classifies it `Decorates` and its `۟` constrains that
classification; IndoPak (`اُولٰ࢜ىِٕكَ`) writes no mark and the derivation
supplies the same classification. `silence=HIDE` drops both graphemes; `SHOW`
keeps them. Neither script needs a `Silent` attribution, because nothing was
silenced — the nucleus simply stayed short. Measured output `ʔ u l aː ʔ i k`
confirms four slots and no wāw among them.

**Merger — 2:5:4→2:5:5 `مِّن رَّبِّهِمْ`.** `RECITED` + `silence=HIDE`
re-spells the nūn slot as nothing and the rāʾ slot as geminate, so the output
carries the shadda that IndoPak already writes and Uthmani does not. The same
Plan yields `SOURCE` + `silence=SHOW` as the untouched original.

**Compact vs expanded — 3:1.** `COMPACT` emits the three graphemes of `الٓمٓ`
through their `Spelling` rows. `EXPANDED` spells the seven `Slot.spelled`
slots — `أَلِفْ` 3, `لَامْ` 2, `مِيمْ` 2 — and, with `insertions=SHOW`, the
anchored iltiqāʾ fatha, reproducing IndoPak's `ال࢜مَّ࢜` from Uthmani input,
which is the observable form of the evidence §4.2 fix.

## 6. What is not covered

Recorded rather than glossed. The owner's requirement names "removed and added
diacritics" and "levels". `faithfulness` is a single axis conflating *glyph
source* with *performed state*, so "show the source diacritic, marked as
removed" is computable from the `Silent` edges but is not one of the four
toggles. "Levels" — an ordering or nesting of the axes — has no counterpart
here at all. Both live in the public projection API, which is out of scope by
the brief; this ADR guarantees only that the information they need is stored.
