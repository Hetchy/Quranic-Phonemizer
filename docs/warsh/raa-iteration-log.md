# Raa weighting iteration log

This records the test-first reconciliation for delivery-map order 12. Domain
expectations come from `research/v2/raa.md`, its cited sources, and the
completed inclination and lam-taghliz contracts rather than from previous
runtime output.

## Decision surface

The fixed classifier resolves the performed boundary state, exact fixed and
named registers, systematic moving-raa predicates, then the ordinary moving
or sakin law. A same-word original kasra or sakin yaa lightens a moving raa;
an intervening isti'la consonant blocks the kasra cause except for khaa, and a
following same-word isti'la consonant blocks either cause. Temporary and
cross-word kasras do not qualify.

The selected default face is implemented for every accepted choice. Public
selectors and alternate faces remain deferred to order 14. Inclination keeps
precedence over ordinary moving-raa weight, while lam taghliz and its vowel
coloring remain independent owners.

One `tafkheem` or `tarqeeq` occurrence owns the raa consonant and the source
character that supplies it. When the raa owns a performed A nucleus, the same
occurrence also reaches its short, carrier-long, or `madd_iwad` vowel sound
and the rendered carrier. It does not reach the composite tanwin cell or erase
an independent isti'la coloring cause.

## Selected-script audit

The authored evidence table contains 198 exact finite rows. Every row stores
its King Fahd source address, canonical address, selected text, owner, and raa
ordinal separately. The adapter checks the complete text and Unicode names;
the runtime never infers weight from a source color or alternate tanwin mark.

Corpus lookalike scans covered the three foreign-name families, repeated-raa
forms, `عشير`, the pausal `مصر`/`القطر`/`أسر`/`نذر` families, both supported
fathatan forms, and following/intervening isti'la shapes. Exact coordinate
registers are used for the foreign names: a consonant-suffix shortcut also
matched unrelated `عُمُراٗ` and `مُّعَمَّرٖ` and was rejected.

## Test-first reconciliation

| Failure or discrepancy | Classification | Resolution |
| --- | --- | --- |
| The pre-implementation focused run could not collect the raa projection, semantic, and conformance suites because the typed Warsh raa module did not exist. | Missing vertical | Added the generic classifier, authored Warsh profile, binding, and reach only after the complete initial tests were present. |
| The first runtime pass left 13 semantic failures. | Test/runtime reconciliation | Corrected independently checked source coordinates and unambiguous selectors, then fixed performed-A and boundary handling; no expectation was copied from a source color. |
| The pre-adapter research totals of 255 fathatan and 837 damma targets did not reconcile. | Stale research estimate | The independent canonical scan finds 276 fathatan and 855 damma precursor candidates. The following-isti'la check removes one damma target; named exclusions leave 259 and 851. The research contract and assertions now carry those executable totals. |
| The repeated-heavy table claimed ten sites but listed nine. | Register omission | Added the second `ضِرَاراٗ` at canonical 2:231 and retained the ten-site subtotal. |
| A letter-suffix implementation counted five apparent `عمران` shapes although the name occurs three times. | Ownership defect | Replaced all three foreign-name suffixes with exact 69-, 43-, and 3-member authored registers and added both false-positive lookalikes as conformance negatives. |
| The completed seven-alifs suite retained an order-12 strict xfail for the two `قَوَارِيراٗ` raas. | Earlier-vertical dependency resolved | Removed the xfail after raa-dependent fathatan and iwad coloring passed in both boundary states. |
| Three shared semantic rows still expected Hafs weight for Warsh at `خَيْرٌ`, `قِرَدَةً`, and `يُبْصِرُونَ`. | Earlier-test reconciliation | Split only the Warsh phoneme branches to their systematic light-raa results; the owning iltiqa, izhar, and qalqala assertions are unchanged. |

The final focused reconciliation includes projection, semantic, finite-register,
systematic-count, seven-alifs, inclination, lam-taghliz, and shared-emphasis
coverage. The fast and full gate results are recorded in the pull request.
