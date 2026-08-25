# Lam taghliz iteration log

This records the test-first reconciliation for delivery-map order 11. Domain
expectations come from `research/v2/lam-taghliz.md` and its inclination
contract, not from the previous runtime output.

## Decision surface

The ordinary predicate weights an open lam immediately after sad, tah, or
zah in the same word when the trigger is sakin or has a short fatha. A long
trigger vowel separates the lam and is not an ordinary direct trigger. The
fixed precedence is coupled form, `salsal`, separated form, final-waqf form,
ordinary predicate, then shared behavior, with one weight owner at each lam.

The fixed coupled defaults are fath plus taghliz at the seven dhat-yaa sites
and taqlil plus tarqiq at the three verse-head sites. The five alif-separated
sites and nine final-waqf sites receive taghliz. The first lam at each of the
four `salsal` sites receives tarqiq; the second lam is not claimed. Taghliz
reaches the lam consonant and its dependent open vowel, including a long or
iwad realization. Taqlil and imala kubra remain distinct qualities.

Public variant selection remains deferred to order 14. Raa weighting remains
deferred to order 12.

## Selected-script audit

The independent source fixture contains 28 exact rows, partitioned as ten
coupled, five alif-separated, nine final-waqf, and four `salsal` sites. Each
row records both its King Fahd source address and canonical address. In
particular, source `20:85:1` projects to canonical `20:86:14`; it is not the
first word of canonical ayah 86.

The adapter fixtures inspect all six ordinary source-sequence families:
open and sakin sad, open and sakin tah, and open and sakin zah before an open
lam. They also inspect nearby article, long-trigger, closed-vowel, and sakin-
lam lookalikes. No source scalar or annotation is treated as a global taghliz
hint; the reviewed grapheme sequence supplies canonical structure and the
performance classifier owns the weight decision.

## Test-first reconciliation

| Failure or discrepancy | Classification | Resolution |
| --- | --- | --- |
| The pre-implementation focused run reported 56 expected-behavior failures while all source-projection fixtures already passed. | Missing vertical | Added the typed taghliz rule, the generic lam-weight classifier, the Warsh profile, and its rule binding only after the complete test surface was present. |
| Joined final-lam cases initially missed ordinary taghliz. | Classifier defect | Compare the preceding and target slots' owning words directly; the neighbourhood boundary helper describes the following boundary and was the wrong predicate here. |
| Joined tanwin has no separate transformed-vowel source column, while stopped iwad creates a rendered vowel and carrier. | Projection reconciliation | Keep taghliz on the lam and performed vowel in the joined state; at waqf, project it through the realized iwad vowel and carrier together with the existing madd owners. |
| A dropped maqsura under a joined boundary mask has no carrier source placement. | Projection reconciliation | Assert the surviving lam and performed-vowel reach in the joined state, and assert carrier reach only when the stopped realization retains it. |
| Four established Warsh expectations retained plain lam output at valid ordinary sites. | Earlier-test reconciliation | Updated those Warsh-only branches to the independently derived emphatic lam and dependent-A result; the Hafs expectations remain unchanged. |

The final focused reconciliation covers the new semantic, adapter, and
conformance suites together with the affected shared emphasis, assimilation,
and written-carrier cases. The local test-style gate still reports the two
pre-existing order-7 source-comment mismatches; neither file differs from the
order-10 base.
