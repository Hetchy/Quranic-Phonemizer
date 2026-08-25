# Warsh implementation status

> **Scope:** Warsh 'an Nafi' by tariq al-Azraq only.

This is the implementation handoff for the Warsh stack. The table is the
source of truth for delivery order, relevant specifications, current state,
and the PR or branch carrying each unit. A concluded research item is ready
to implement; it is not evidence that its runtime vertical exists.

## Delivery map

| Order | Workstream | Relevant research and contract | Status | PR or branch |
| ---: | --- | --- | --- | --- |
| 1 | Test audit and semantic-tree reorganization | [`test-audit.md`](test-audit.md), [`test-refactor-plan.md`](test-refactor-plan.md), [`warsh-test-placement.md`](warsh-test-placement.md) | **Complete** | Delivered with [PR #60](https://github.com/Hetchy/Quranic-Phonemizer/pull/60) |
| 2 | Warsh foundation: selected source, alignment, provenance, Uthmani adapter, package seam, and shared-rule baseline | [`script-projection.md`](research/v2/script-projection.md), [`phoneme-rule-inventory.md`](research/v2/phoneme-rule-inventory.md), [`codepoint-audit.md`](codepoint-audit.md) | **Complete** | [PR #60](https://github.com/Hetchy/Quranic-Phonemizer/pull/60) (merged) |
| 3 | Model foundation: declared classifier emissions, per-riwayah rule catalogue, typed taqlil/kubra, riwayah-owned kubra fallback, and neutral joined-only-long shape | [`phoneme-rule-inventory.md`](research/v2/phoneme-rule-inventory.md) | **Complete** | `feat/warsh-model-foundation`; consumed as the base of [PR #61](https://github.com/Hetchy/Quranic-Phonemizer/pull/61) |
| 4 | Wasl and iltiqa: start registers, U subregister, silent-qata starts, and boundary repair | [`wasl-hamza.md`](research/v2/wasl-hamza.md), [`iltiqa.md`](research/v2/iltiqa.md) | **Complete** | [PR #61](https://github.com/Hetchy/Quranic-Phonemizer/pull/61) (merged) |
| 5 | Naql: general, article, lexical, and boundary-specific transfer | [`naql.md`](research/v2/naql.md) | **Complete** | [PR #62](https://github.com/Hetchy/Quranic-Phonemizer/pull/62) (merged) |
| 6 | Hamza core: generic ibdal/tashil primitives and Warsh single hamza | [`single-hamza.md`](research/v2/single-hamza.md), [`phoneme-rule-inventory.md`](research/v2/phoneme-rule-inventory.md) | **Complete** | `feat/warsh-hamza-core`; variant-bearing `allai` deferred to order 14 |
| 7 | Madd badal and leen mahmuz. Implements badal mughayar bin-naql tests deferred in #62 | [`madd-badal.md`](research/v2/madd-badal.md), [`madd-leen-mahmuz.md`](research/v2/madd-leen-mahmuz.md), [`madd-counts.md`](research/v2/madd-counts.md) | **Pending** | Follows hamza core |
| 8 | Hamza meetings | [`hamza-meetings.md`](research/v2/hamza-meetings.md) | **Pending** | Follows madd badal and leen mahmuz |
| 9 | Joined-only and pausal shapes: mim al-jam, yaa zawaid, and seven alifs | [`mim-al-jam.md`](research/v2/mim-al-jam.md), [`yaa-zawaid.md`](research/v2/yaa-zawaid.md), [`seven-alifs.md`](research/v2/seven-alifs.md) | **Pending** | One mark-driven vertical, after hamza meetings |
| 10 | Inclination: taqlil, kubra, fath, registers, and precedence | [`inclination.md`](research/v2/inclination.md) | **Pending** | Follows joined-only and pausal shapes |
| 11 | Lam taghliz and its inclination coupling | [`lam-taghliz.md`](research/v2/lam-taghliz.md) | **Pending** | Follows inclination |
| 12 | Raa weighting and dependent vowel coloring | [`raa.md`](research/v2/raa.md) | **Pending** | Follows lam taghliz |
| 13 | Full-corpus attribution, default-profile conformance, and projection gates | [`script-projection.md`](research/v2/script-projection.md), [`phoneme-rule-inventory.md`](research/v2/phoneme-rule-inventory.md), [`conformance.md`](../conformance.md) | **Pending** | After all fixed rule verticals |
| 14 | Public variant catalogue and selectable behavior | [`variants.md`](../variants.md), plus the owning v2 research file for each phenomenon | **Pending** | Add last, in two or three owner-family PRs |
| 15 | Merge completed workstreams into the integration branch and open the overview PR to `main` | [`architecture.md`](../architecture.md), [`public-api.md`](../public-api.md), README.md, docs/design/public-api-facade.md | **Pending** | `feat/warsh-phonemizer` |

## Current implementation contract

- The runtime target is Warsh through al-Azraq. Other Warsh transmitters are
  outside scope.
- Warsh is single-script: the King Fahd corpus is the supported source. A
  reviewed mark-sequence family may supply the canonical fact it writes;
  unreviewed sequences fail projection rather than being guessed.
- Wasl, waqf, and ibtidaa are explicit boundary states. Closed lexical
  exceptions belong in reviewed authored data.
- The phonemizer classifies sounds and named rules, not recitation counts.
  Count-dependent transmission details do not add a length model.
- Rule occurrences name the acted-on unit, the changed or classified sound,
  and its owned source placement. Trigger-only context is not copied onto
  unrelated characters.
- Taqlil and imala kubra are distinct typed qualities. Warsh uses taqlil as
  its ordinary inclination fallback; kubra remains distinct where selected.
- Tashil preserves its typed eased-hamza state and attribution even when its
  optional rendering is collapsed to ordinary hamza. Ibdal names the replaced
  hamza as source and the replacement unit as host.
- Warsh adds `taqlil`, `taghliz`, `naql`, and `madd_leen_mahmuz` to the shared
  rule vocabulary. Each riwayah derives its public rule catalogue from the
  rule IDs emitted by its bound classifiers.

## Progress rules

- Use only **Pending**, **Ready**, **In progress**, **Blocked**, **Concluded**,
  and **Complete** in the delivery table.
- A runtime workstream is **Complete** only when its evidence, exceptions,
  tests, implementation, and applicable corpus gates agree.
- Keep domain evidence in `research/v2/`, historical material in
  `research/v1/`, API matrices in [`variants.md`](../variants.md), and
  exhaustive occurrence lists in authored data or tests.
- Implement fixed behavior before adding public variants. Recount the final
  semantic tree; planning case counts are not completion evidence.
- Run `python tools/gates.py --fast` during a workstream and the full
  `python tools/gates.py` before handing off runtime or corpus changes.

## Research boundaries

The v2 files are the normative Warsh implementation specifications. The v1
files are retained evidence only and may contain stale filenames, mixed routes,
or count-oriented claims. `docs/new-riwayah.md` remains tentative guidance,
not an established abstraction.
