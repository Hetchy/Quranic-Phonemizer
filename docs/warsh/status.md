# Warsh implementation status

> **Scope:** Warsh 'an Nafi' by tariq al-Azraq only.
>
> This page records the current implementation state and the decisions needed
> to continue the work across multiple PRs. The normative domain and model
> specifications are in [`research/v2/`](research/v2/), historical notes are
> preserved in [`research/v1/`](research/v1/), source-encoding findings belong
> in `codepoint-audit.md`, and public contracts belong in their API
> documentation. This is not a changelog or a domain specification.

The Warsh runtime has not been implemented. The domain, variant, and phoneme
audits are sufficiently complete to plan the work. A **concluded** research
status means that a decision is ready to implement, not that runtime support
exists. Authenticated corpus evidence, stronger primary sources, and executable
validation may still correct a concluded decision.

## Current state

| Workstream | State | Current result |
| --- | --- | --- |
| Source and codepoint audit | Concluded | Sequence-aware adapter requirements identified; runtime adapter not built |
| Warsh domain research | Concluded | Rule families, boundary behavior, and exception sets audited for implementation planning |
| Variant design | Concluded | Public scopes, values, defaults, registers, and interactions are recorded in [`../variants.md`](../variants.md) |
| Phoneme and rule vocabulary | Concluded | Required additions and reused sound primitives identified; not implemented |
| Cross-riwayah variant audit | Concluded | Shared IDs and riwayah-specific defaults and site scopes are recorded in [`../variants.md`](../variants.md) |
| Test organization | Plan complete | The current-suite audit is in [`test-audit.md`](test-audit.md), the target tree and harness are in [`test-refactor-plan.md`](test-refactor-plan.md), and shared/Hafs/Warsh file ownership is in [`warsh-test-placement.md`](warsh-test-placement.md); no test file has been moved and no Warsh fixture has been added |
| Canonical and model changes | Not started | Required foundation work is listed below |
| Warsh corpus integration | Not started | No production corpus package, adapter, or address normalization exists |
| Warsh rules | Not started | No Warsh classifier set or authored exception data exists |
| Full-corpus conformance | Not started | No end-to-end Warsh output exists to validate |

## V2 specification map

| Specification | Ownership |
| --- | --- |
| [`phoneme-rule-inventory.md`](research/v2/phoneme-rule-inventory.md) | Typed sounds, rule IDs, rule reach, rendering, and riwayah-scoped rule sets |
| [`script-projection.md`](research/v2/script-projection.md) | Selected King Fahd source, address alignment, provenance, and orthographic projection |
| [`wasl-hamza.md`](research/v2/wasl-hamza.md) | Wasl start quality, elision, silent-qata starts, and article-istifham interaction |
| [`iltiqa.md`](research/v2/iltiqa.md) | A/I/U repair and shortening after wasl elision |
| [`single-hamza.md`](research/v2/single-hamza.md) | Single-hamza ibdal, lexical easing, omissions, and closed exceptions |
| [`naql.md`](research/v2/naql.md) | General, article, lexical, and boundary-specific naql |
| [`hamza-meetings.md`](research/v2/hamza-meetings.md) | One-word and two-word hamza meetings and their fixed exceptions |
| [`madd-counts.md`](research/v2/madd-counts.md) | Received duration facts that remain outside the runtime length model |
| [`madd-badal.md`](research/v2/madd-badal.md) | Badal origin, effective madd overlap, and duration-only exceptions |
| [`madd-leen-mahmuz.md`](research/v2/madd-leen-mahmuz.md) | Structural leen-mahmuz classification and its exact exclusions |
| [`mim-al-jam.md`](research/v2/mim-al-jam.md) | Joined mim shape before qata and its madd consequences |
| [`yaa-zawaid.md`](research/v2/yaa-zawaid.md) | Joined-only and consonantal added-yaa facts |
| [`seven-alifs.md`](research/v2/seven-alifs.md) | Fixed lexical alif boundary matrices |
| [`inclination.md`](research/v2/inclination.md) | Taqlil, kubra, fath, fixed registers, and inclination precedence |
| [`raa.md`](research/v2/raa.md) | Structural and authored Warsh raa weight plus dependent vowel coloring |
| [`lam-taghliz.md`](research/v2/lam-taghliz.md) | Lam taghliz, tarqiq, inclination coupling, and boundary exceptions |

## Agreed foundations

- The implementation target is Warsh through al-Azraq. Other transmitters from
  Warsh, such as al-Asbahani, are outside the runtime scope.
- The phonemizer classifies sounds and named rules, not recitation counts.
  Count-dependent transmission details do not introduce a length model.
- Variants are scoped to the domain choice they control. The API does not
  validate combinations as reconstructions of one historical tariq.
- Defaults may differ by riwayah and should reflect the recommended or
  prevalent reading rather than accidentally preserving Hafs defaults. On
  modeled dimensions, each riwayah's complete default vector must remain a
  coherent popular baseline, even though arbitrary explicit overrides are
  accepted.
- Script-specific sequences are normalized in `orthography/`. Raw Unicode
  marks may attest a reading but do not decide a tajweed rule.
- Wasl, waqf, and ibtidaa remain explicit boundary states.
- Closed lexical exceptions belong in reviewed authored data.
- Where a rule affects both performed sound and written source, its public
  occurrence must reach both.
- Every eventual Hafs-Warsh phoneme difference must be attributable to a
  canonical text difference, a named rule, or a selected variant.

## Concluded output-model decisions

- Taqlil is a first-class vowel quality and rule. Its broad rendering is
  `/ɛ, ɛː/`.
- Imala kubra is distinct from taqlil and broadly renders `/e, eː/`.
- Warsh uses taqlil as its ordinary inclination fallback. Kubra remains
  controlled by the existing `imala` extra-phoneme facility where applicable.
- Tashil keeps its typed eased-hamza state and rule attribution even when its
  optional token distinction is disabled and rendered as ordinary hamza.
- Taghliz is distinct from generic tafkheem and uses the existing emphatic
  single-lam sound `/lˤ/`. Gemination remains independent.
- Existing light and heavy raa sounds are sufficient.
- Ibdal and the resulting madd classification apply to the replacement sound
  and the responsible source character or characters.
- Naql does not require a new phoneme. Isqat receives no runtime rule of its
  own.
- The refined rule vocabulary adds `taqlil`, `taghliz`, `naql`,
  `madd_badal`, `madd_leen_mahmuz`, and `iltiqa_haraka`; `imala` classifies
  kubra, and `iltiqa_haraka` replaces the I-only `iltiqa_kasra` name.
- `Rule` remains a global semantic vocabulary, but every riwayah binds its own
  `RuleSet`. Each classifier declares the complete set of rule IDs it can
  emit, and `tajweed_rules(riwayah)` is derived from those bound emitted sets.
- The complete selector catalogue and finite public registers are in
  [`../variants.md`](../variants.md); executable occurrence inventories belong
  with their semantic tests.

The complete sound, rule, reach, and binding contract is in
[`research/v2/phoneme-rule-inventory.md`](research/v2/phoneme-rule-inventory.md).
The selected-script and address-provenance contract is in
[`research/v2/script-projection.md`](research/v2/script-projection.md).

## Required model work

None of this work has started. These are implementation recommendations, not
claims about the current runtime.

1. Represent taqlil and imala kubra as distinct typed vowel qualities rather
   than overloading `Quality.E`.
2. Make kubra's collapsed rendering riwayah-owned: Hafs falls back to `/i/`,
   while Warsh falls back to taqlil.
3. Classify madd from the effective structure after transformations such as
   ibdal.
4. Project applicable ibdal, madd, and other rule occurrences onto both
   performed sounds and source characters.
5. Resolve selector-driven raa and lam weight before colouring the following
   fatha or alif, and project that causal choice onto sound and source.
6. Preserve exact inclination in recited spelling independently of whether an
   extra phoneme rendering is enabled.
7. Replace the pronoun-specific `is_silah` model name with a neutral
   joined-only-long shape usable by pronoun silah, Warsh yaa zawaid, and mim
   al-jam'.
8. Build a sequence-aware Warsh script adapter and checked transformation
   manifest. Do not introduce universal scalar mappings for context-dependent
   marks.
9. Integrate a Warsh riwayah package through the existing composition boundary
   and refine that tentative boundary only when real implementation evidence
   requires it.
10. Give every classifier a declared set of rule IDs it can emit. Build
    `tajweed_rules(riwayah)` from the classifiers bound by that riwayah rather
    than from one nominal rule per classifier or from the global rule enum.
11. Generate a complete source-to-canonical address alignment for the selected
    Warsh artifact and preserve typed source provenance separately from public
    canonical locations.

## Test work

Test organization must be refactored before existing cases are extended or new
Warsh failures are added. The read-only checkpoint is complete in
[`test-audit.md`](test-audit.md). The executable refactor specification is
[`test-refactor-plan.md`](test-refactor-plan.md), and the concise handoff is
[`tests-task.md`](tests-task.md). The remaining test work must:

- mechanically move every current test to its audited semantic owner;
- refactor the harness and compact duplicate coverage before adding Warsh;
- extend every vetted shared case to Warsh through the adapter baseline;
- preserve an executable inventory of every researched exception; and
- keep public variant behavior until the final test and implementation phase.

The target tree has 474 fixed/default phonemization review cases and 70 final
variant behavior cases. The generic API contract covers all 71 selector
metadata rows; `tamanna_noon` intentionally has no new behavior case. Actual
pytest collection expands semantic rows by state, riwayah, script, and exact
occurrence.

## Delivery sequence

Exact PR boundaries may change, but each unit must remain independently
reviewable:

1. Audit and reorganize the existing tests.
2. Add the Warsh source artifact, full source-to-canonical alignment, minimal
   source-provenance plumbing, script adapter, and vetted shared-rule tests.
   Do not add a new Warsh tajweed classifier in this step.
3. Complete the shared model foundations for inclination qualities,
   riwayah-scoped emitted-rule declarations, rule attribution, effective madd
   classification, and neutral joined-only longs.
4. Add narrow fixed-rule vertical PRs, with failing cases first: inclination;
   hamza, naql, ibdal, and tashil; raa; lam and taghliz; joined-only vowel
   phenomena; madd classifications; and remaining lexical differences.
5. Run full-corpus attribution and default-profile conformance checks for both
   Hafs and Warsh.
6. Add the public variant catalogue and selectable behavior last, colocated
   with the semantic tests that own each phenomenon.
7. Merge completed workstreams into `feat/warsh-phonemizer`. Its eventual PR
   to `main` should give a high-level overview and link the constituent PRs.

## Progress convention

- Use only **Pending**, **Ready**, **In progress**, **Blocked**, **Concluded**,
  and **Complete** as workstream states.
- Update this page only when a workstream changes state or a foundation
  decision changes.
- Do not append dated diary entries, commit summaries, or completed-task logs.
- Keep reviewed domain evidence in `research/v2/`, historical notes in
  `research/v1/`, API matrices in their contract document, and exhaustive
  occurrence lists in authored data or tests.
- A runtime workstream is complete only when its evidence, exceptions, tests,
  implementation, and applicable corpus gates agree.
- Record an open question here only when it blocks the next implementation
  step.
- Run `python tools/gates.py --fast` during a workstream and the full
  `python tools/gates.py` before handing off runtime or corpus changes.

## Documentation cautions

The v2 research files are the normative Warsh domain and implementation
specifications. The files under `research/v1/` are evidence inputs only. They
were imported from earlier PRs and contain broad, route-mixed, count-oriented,
incomplete, or insufficiently sourced claims. Primary domain sources, the
selected script, and the reviewed v2 specifications take precedence.

- `research/v1/overview.md` contains stale filenames and introductory source
  material; do not implement from it directly.
- `research/v1/hamza.md` and `research/v1/madd.md` contain categories that do
  not map one-to-one onto runtime rules or length settings.
- `research/v1/imalah-classification.md` is a retained position map, not the
  authority for pronunciation semantics.
- `codepoint-audit.md` describes an audited source snapshot. Recheck its counts
  and hashes against the corpus actually ingested.
- [`../new-riwayah.md`](../new-riwayah.md) remains tentative guidance until a
  second riwayah is implemented.
