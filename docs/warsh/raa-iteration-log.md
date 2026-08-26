# Raa weighting iteration log

This records the test-first reconciliation for delivery-map order 12. Domain
expectations come from `research/v2/raa.md`, its cited sources, and the
completed inclination and lam-tafkheem contracts rather than from previous
runtime output.

## Decision surface

The fixed classifier resolves the performed boundary state, genuinely fixed
lexical exclusions, then the ordinary moving or sakin law. A same-word
original kasra or sakin yaa lightens a moving raa; an intervening isti'la
consonant blocks the kasra cause except for khaa, and a following same-word
isti'la consonant blocks either cause. Temporary and cross-word kasras do not
qualify.

No shared, systematic, lexical, pausal, or cross-word variant owner is bound
in this vertical. Their registers, alternate faces, selector behavior, and
variant-specific conformance counts remain wholly deferred to order 14.
Systematic damma and fathatan shapes retain the inherited heavy result until
their owners are implemented; other variant-bearing shapes receive only the
generic fallback and have no authored expectation here.

One `tafkheem` or `tarqeeq` occurrence owns the raa consonant and the source
character that supplies it. When the raa owns a performed A nucleus, the same
occurrence also reaches its short or carrier-long vowel sound and rendered
carrier. It does not erase an independent isti'la coloring cause. Inclination
keeps precedence over ordinary moving-raa weight, while lam tafkheem and its
vowel coloring remain independent owners.

## Selected-script audit

The authored evidence table contains 129 exact rows for the fixed exclusions:
69 Ibrahim forms, 43 Israil forms, three Imran forms, ten repeated-raa heavy
forms, one fixed-light `حِذْرَهُمْ`, and three other fixed-light `عشير` forms.
Every row stores its King Fahd source address, canonical address, selected
text, owner, and raa ordinal separately. The adapter checks the complete text
and Unicode names; the runtime never infers weight from a source color or
alternate mark.

Corpus lookalike scans covered the three foreign-name families, repeated-raa
forms, and the fixed light families. Exact coordinate registers are used for
the foreign names: a consonant-suffix shortcut also matched unrelated
`عُمُراٗ` and `مُّعَمَّرٖ` and was rejected.

## Test-first reconciliation

| Failure or discrepancy | Classification | Resolution |
| --- | --- | --- |
| The pre-implementation focused run could not collect the raa projection, semantic, and conformance suites because the typed Warsh raa module did not exist. | Missing vertical | Added the generic classifier, fixed Warsh profile, binding, and reach only after the initial tests were present. |
| The first runtime pass left structural and projection failures. | Test/runtime reconciliation | Corrected independently checked source coordinates and selectors, then fixed performed-A and boundary handling; no expectation was copied from a source color. |
| The repeated-heavy table claimed ten sites but listed nine. | Register omission | Added the second `ضِرَاراٗ` at canonical 2:231 and retained the ten-site subtotal. |
| A letter-suffix implementation counted five apparent `عمران` shapes although the name occurs three times. | Ownership defect | Replaced all three foreign-name suffixes with exact 69-, 43-, and 3-member authored registers and added both false-positive lookalikes as conformance negatives. |
| The seven-alifs suite carries a strict xfail for the selectable Qawarira raa face. | Deferred variant | Retained the strict xfail because neither a selected face nor its dependent coloring belongs to the fixed classifier. |

The focused order-12 suite covers the moving predicates, isti'la blockers,
khaa exception, sakin and boundary law, dependent short and carrier A
coloring, all six fixed owner families, exact source projection, finite
subtotals, duplicate ownership, and false-positive lookalikes. Variant-owned
registers and expectations are absent.
