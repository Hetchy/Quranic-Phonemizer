# Hamza-meetings iteration log

## Pre-implementation partition

The complete order-8 tests were collected before runtime code existed. The
focused run stopped at collection on the intentionally absent
`riwayat.warsh.hamza_meetings` module; adapter and semantic expectations were
therefore not reachable yet.

## Reconciliation

- The first projection run established the exact 60 one-word and 156
  across-word partitions, including both cross-ayah rows and every authored
  exception.
- The first semantic run exposed selected spellings that had been classified
  as wasl, naql, or a folded carrier. Projection now restores their qata
  identity before boundary rules run, and naql excludes the closed meeting
  starts.
- Relengthened meeting carriers initially received no structural madd because
  the generic classifier only dispatched canonical long vowels. Short
  carriers relengthened by an earlier phase now dispatch through the same
  following-context classifier, producing lazim before a permanent sakin and
  tabii otherwise.
- Tashil expectations now exercise both renderings: the typed eased onset,
  occurrence, and source reach persist when the optional `tashil` token is
  disabled.
- Two existing munfasil fixtures that join into an I+I meeting now carry
  Warsh-specific expected output: meeting ibdal fuses the following qata
  carrier while leaving the two preceding madd classifications intact.
- Raa coloring in the `زكرياء إنا` context remains owned by delivery order 12;
  this vertical asserts only the Hamza replacement and does not pre-implement
  that later rule.
