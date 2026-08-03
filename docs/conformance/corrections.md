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

## The dead `سلسبيلا` entry

`lexicon.yaml`'s `pausal_lexemes` section carried a second entry,
`"سaلسaبiلa"`, aimed at 76:18 `سَلْسَبِيلًا`. Its vocalised key never matched
that word -- the tanween noon the word ends in adds a final unvoweled
letter the key did not account for -- so the entry never fired and 76:18 has
always read as an ordinary tanween. Uthmani draws no `۠` there either. This
unit removes the section rather than repairing the entry.
