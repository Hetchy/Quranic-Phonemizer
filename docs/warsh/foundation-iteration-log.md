# Warsh foundation iteration review

This review records how adapter-first test failures were classified. It is a
compact audit trail for the foundation, not a Warsh domain specification. The
normative rules remain in [`research/v2/`](research/v2/), and semantic test
ownership remains in [`warsh-test-placement.md`](warsh-test-placement.md).

## Delivered boundary

The foundation contains:

- the selected King Fahd Warsh source under the public `uthmani` script name;
- a generated source-to-canonical alignment with typed source provenance;
- a total 62-scalar inventory plus sequence-sensitive projection;
- a Warsh package bound to the existing shared canonical builder and shared
  tajwid classifiers; and
- vetted shared semantic cases running under both Hafs and Warsh.

It does not contain Warsh-specific naql, inclination, hamza transformation,
raa, taghliz, mim al-jam, yaa-zawaid, badal, leen-mahmuz, seven-alif, or
variant behavior.

## Alignment result

The generated artifact has 77,426 rows. It covers 77,425 selected-source words
and 77,433 canonical words or declared spans exactly once and monotonically.
The seven word-cardinality edits are executable fixtures:

| Canonical/public span | Selected-source span |
| --- | --- |
| `1:1:1-4` | absent |
| `15:7:1-2` | `15:7:1` |
| `27:20:4-5` | `27:20:4` |
| `36:22:1-2` | `36:21:1` |
| `40:26:13-14` | `40:26:13` |
| `57:24:10` | absent |
| `72:16:1` | `72:16:1-2` |

Runtime words use canonical/public `Location`. Every retained source scalar
keeps a `SourceGraphemeRef` containing the artifact identity, source word
address, and scalar offset. A separator inserted between two source words has
no fabricated source reference. Every coordinate inside a multiword canonical
span resolves to its one aligned runtime word; the runtime does not duplicate
that word or its sounds.

## Failure classification

| Observation | Classification | Resolution and rationale |
| --- | --- | --- |
| Canonical and selected-source ayah numbering diverged after Fatiha and at several later boundaries. | Adapter/model bug | Added a complete generated alignment. Offsets or ad hoc coordinate substitutions would not preserve split and merged verse edges. |
| A canonical verse gap could make a joined test read into the next verse. | Harness bug | Boundary reach now uses canonical `surah_info`, while `words()` returns only source-backed runtime words. Missing public words cannot silently change the requested junction. |
| Declaring a not-yet-packaged riwayah constructed its closed enum too early. | Harness bug | `Site.shipped()` compares declared package names. Dormant rows remain inert until a package is registered. |
| Initial `ا` plus haraka plus `۬`, `۟`, or `۪` did not reach the literal wasl alif. | Adapter bug | The complete sequence supplies WASL onset evidence from all three source scalars. The canonical wasl derivation still decides the helping vowel. |
| Noninitial `۪` was treated like the same initial wasl mark. | Adapter bug | Outside the reviewed initial sequence it supplies A-quality evidence only. Inclination quality remains a later Warsh classifier decision. |
| The source writes many fathatan forms after their iwad alif. | Adapter bug | Reversed alif-fathatan order attaches the nunation fact to the preceding sounded base and retains the alif as the iwad carrier. |
| Haraka plus mini-meem was being read as a short vowel plus an extra mark. | Adapter bug | The pair supplies one tanwin fact; mini-meem separately attests the derived iqlab result and never becomes a sounded meem. |
| Final `و` plus `اْ` could leave the rasm alif sounded. | Adapter bug | The source sukun decorates and silences the final alif. Tests cover long, leen, and short preceding waw shapes. |
| A sounded yaa before a combining hamza could be consumed as the hamza seat. | Adapter bug | A sukun-bearing waw or yaa remains a glide, followed by a distinct combining-hamza letter. `شَئْاٗ` is the direct fixture. |
| A dagger immediately before standalone sakin hamza could create a false long vowel. | Adapter bug | The dagger is retained as the hamza seat decoration and supplies no length. `فَادَّٰرَٰءْتُمْ` is the direct fixture. |
| The selected source contracts the written divine name in `لله`. | Shared canonical bug exposed by the adapter | The shared lexeme pass recovers the omitted shadda and fatha from the canonical divine-name class; script codepoints do not decide the rule. |
| A bare `للـه` skeleton also occurs inside `يضلله`. | Shared lexical false positive | Contracted divine-name recovery is limited to word-initial `لله`, optionally after `و` or `ف`; the verbal suffix remains an ordinary lam plus pronoun haa. |
| Several shared tests differed only because the selected source contains a fixed lexical reading, a Warsh-only rule site, or unresolved variant behavior. | Test-site bug | The row received a small `pick`, a clean Warsh substitute under the same law, or remained Hafs-only. No adapter branch was added to imitate Hafs text. |
| Article naql, inclination, mim al-jam, transformed hamza, seven alifs, and selectors contaminated otherwise shared examples. | Out of foundation scope | Those rows remain with their owning Warsh vertical. A passing baseline must not pre-encode their future result as an orthographic rule. |

## Executable review targets

`tests/adapter/test_warsh_corpus_alignment.py` owns artifact identity,
coverage, monotonicity, the seven spans, public lookup, and typed source
provenance. `tests/adapter/test_warsh_script_projection.py` owns the 62-scalar
inventory and every sequence family above. The shared semantic tree owns rule
and sound behavior; it does not repeat selected-source coordinates.

The RAR projection tests separately own three insertion cases requested during
the audit: a boundary-owned `iltiqa_haraka`, the Uthmani small-waw carrier at
`17:7`, and the Uthmani small-yaa carrier at `2:124`.

The complete semantic suite passes for the package baseline, and an explicit
all-corpus sweep builds every one of the 6,235 nonempty public verse buckets
and all 77,424 runtime word entries.

The case-by-case decision record is
[`foundation-test-reconciliation.md`](foundation-test-reconciliation.md).

## Madd badal invariant

Warsh `madd_badal` replaces ordinary `madd_tabii`. In both Hafs and Warsh,
it remains present when waqf independently establishes
`madd_arid_lissukun`; `madd_muttasil` or `madd_lazim` may overlap as well.
The foundation adds no Warsh badal classifier; this invariant is retained here
so later rule tests assert the complete contextual rule set.
