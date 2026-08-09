# Corrections against the frozen legacy snapshot

Unit A5 keyed the seven alifs by word location instead of by vocalised
skeleton. The skeleton `أَنَا`/`وَأَنَا`/`فَأَنَا` recurs 68 times; a
vocalised-skeleton lexicon marked all of them pausal, but Uthmani draws the
rectangular-zero mark `۠` at only 61 of those sites plus five one-off word
sites (`لكنا`, `الظنونا`, `الرسولا`, `السبيلا`, `قواريرا` at 76:15), 66 in
total -- confirmed by a direct scan of the Uthmani source for `U+06E0`, which
also matches the count `research/spines/spine-b.md` section 3 and
`docs/adr/003-script-boundary.md` section 6.2 both record.

## The seven corrected refs

| Ref | Was | Now |
|---|---|---|
| 2:160:9 | `أَنَا` sited by skeleton, pausal | sited by word location, ordinary long |
| 15:49:4 | pausal | ordinary long |
| 15:89:3 | pausal | ordinary long |
| 20:13:1 | pausal | ordinary long |
| 20:14:2 | pausal | ordinary long |
| 27:9:3 | pausal | ordinary long |
| 28:30:16 | pausal | ordinary long |

These seven are exactly the sites where the skeleton matched but Uthmani
draws no `۠`. `tests/laws/test_seven_alifs.py` pins the corrected fact at
each ref, and pins a marked site (2:258:21) as pausal in both scripts.

## No token moves

The correction is a canonical-model fact (`Nucleus.is_long` in place of
`Nucleus.is_pausal_long`), and `python tools/snapshot.py diff` against both
head snapshots reports zero words changed; `regression` and `cross-script`
hold their existing floors unmoved. Every one of the seven refs is followed,
once joined, by a word whose real onset (past an eliding hamzat wasl) is
quiescent -- `rules/madd.py`'s `IltiqaRepair` already shortens a word-final
long vowel in that position, independently of whether the canonical fact is
`long` or `pausal_long`. The rectangular zero is drawn exactly where that
independent shortening would not otherwise apply, which is also why these
seven never needed it.

The unit's own entry expected `regression` and `cross-script` to move; they
did not, for the reason above. This correction is recorded here as the unit
requires regardless, because the underlying fact changed even though no
token did.

## Unit A8, corrected: the heavy hum is not yet spent

Item 13 gives ikhfaa haqiqi's hum a `Recolours` edge before one of the five
istilaa letters its own trigger can reach without going to `izhar`: saad,
dad, tah, zah and qaf. That edge is a model fact and stands. A8 also made
`render/alphabet.py::_hum` spend a token for it unconditionally, which
`01-contract` section 3.2 and `decisions.md` section 7 both place among the
three distinctions the notation carries but does not always spend a token
on, `emphatic_ikhfaa` defaulting off same as `eased` and the qalqala degree.
`_hum` now validates `heavy_hum` against the data without composing it,
exactly as `_consonant` already treats `eased`.

**The 246 words A8 moved in word mode, 879 in verse mode, move back.** Every
one reverts the single-token substitution `ŋˤ` -> `ŋ`; `python
tools/snapshot.py diff` against the pre-fix head snapshot reports no other
shape. A representative spread:

| Ref | A8 | Corrected |
|---|---|---|
| 2:27:2 | `jaŋˤquduːn` | `jaŋquduːn` |
| 5:72:33 | `ʔaŋˤsˤaːr` | `ʔaŋsˤaːr` |
| 10:39:15 | `faŋˤðˤur` | `faŋðˤur` |
| 21:65:9 | `jaŋˤtˤiquːn` | `jaŋtˤiquːn` |
| 35:11:24 | `juŋˤqaˤsˤ` | `juŋqaˤsˤ` |
| 48:3:1 | `wajaŋˤsˤuraˤk` | `wajaŋsˤuraˤk` |

`tools/gates.py`'s `regression` floors move from `99.604`/`96.771` back to
`99.921`/`97.852` (word/verse), which is where A8 found them; `cross-script`
does not move. `docs/conformance/gate-residues.md` drops the class.

## d890419, corrected: the provenance claim

The commit's own body says "no phoneme, floor or provenance-gated count
moves." Phonemes and floors did not; the `l1` gate's `Decorates` count did,
by construction -- `letter_offsets_of`/`stray_letter_offsets` decorate
offsets `_slot_draft` previously left with no spelling edge at all, and
`Decorates` is exactly what a decoration adds. Against the pre-fix baseline:

| Script | Decorates before | Decorates after | Delta |
|---|---|---|---|
| uthmani | 56245 | 57065 | +820 |
| indopak | 47928 | 49840 | +1912 |

`Decorates` is not a ceiling `l1` gates on -- residue (18, unchanged) is --
so neither number failed anything. But the `l1` harness prints its own
warning directly above these two rows: a zero residue reached by a rising
`Decorates` count is not a proof of script-independence, which is the
condition this delta is. The commit body's "no ... count moves" undersells
that by two classes' worth: it is true of the counts the gate ceilings, not
of every count the gate prints.

## The dead `سلسبيلا` entry

`lexicon.yaml`'s `pausal_lexemes` section carried a second entry,
`"سaلسaبiلa"`, aimed at 76:18 `سَلْسَبِيلًا`. Its vocalised key never matched
that word -- the tanween noon the word ends in adds a final unvoweled
letter the key did not account for -- so the entry never fired and 76:18 has
always read as an ordinary tanween. Uthmani draws no `۠` there either. This
unit removes the section rather than repairing the entry.

## The alignment the register's last four entries moved

No phoneme moves: `regression`, `cross-script`, `roundtrip`, `attestation` and
`l1` all report the numbers they reported before, and the recited text is
unchanged. What moves is who owns a sound.

`tests/snapshots/head/alignment.jsonl.gz` is the new baseline: a digest per
word for each of the six published views. Against the same file built before
these changes, of 464,598 rows (77,433 words, six views each):

| View | Rows moved |
|---|---|
| `source` by glyph | 8,678 |
| `source` by cell | 2,732 |
| `respell` by glyph | 8,678 |
| `respell` by cell | 0 |
| `recited` by either | 0 |

Every moved word is accounted for, and 232 of them moved for two reasons at
once rather than one:

| Cause | Words |
|---|---|
| a seat stopped owning what it never supplied | 5,946 |
| a carrier whose length `iltiqa_shortening` took back | 2,439 |
| both of those in one word | 231 |
| a carrier whose length `pausal_alif` took back | 61 |
| that and a seat in one word | 1 |

The seven alifs are the `pausal_alif` rows: `أَنَا۠` joined reads `ʔana`, so the
`۠` supplying a length nobody says now shows the rule and presents nothing,
and the fatha owns the vowel.

The cell view moves for exactly the 2,732 words holding a silenced carrier,
and for none of the 6,177 holding only a seat: a seat shares its letter's cell
with the dagger either way, so only the per-glyph attribution changes there.
Silencing a glyph does not move it out of its cell, which is why `respell` by
cell holds still. `recited` moving nothing is the check that publishing
`RenderGlyph.unit` replaced the internal link exactly.

## The degree a tanween hid

Stopping on a word whose last letter carries a tanween, the echo on that
letter was filed as the light degree. `qalqala.py` chose the degree by asking
whether the letter is the word's last slot, and a tanween's noon is a slot
after it. The stop silences that noon, so the letter is the last one still
sounding and never the last one written. The question is now asked of the
slots the stop leaves sounding.

No phoneme moves: the alphabet gives one token to all three degrees, so this
is what a consumer reads and not what a reciter says. Corpus-wide, at verse
joining:

| Degree | Before | After |
|---|---|---|
| `qalqala_sughra` | 3,604 | 3,414 |
| `qalqala_kubra` | 232 | 422 |
| `qalqala_akbar` | 1 | 1 |

190 words move, and they move in all four alignment views because a pairing
names its rules; `respelling` holds still, its blocks naming no rule.
