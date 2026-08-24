# Warsh implementation status

> **Scope:** Warsh 'an Nafi' by tariq al-Azraq only.
>
> This page records the current implementation state and the decisions needed
> to continue the work across multiple PRs. The normative domain and model
> specifications are in [`research/v2/`](research/v2/), historical notes are
> preserved in [`research/v1/`](research/v1/), source-encoding findings belong
> in `codepoint-audit.md`, and public contracts belong in their API
> documentation. This is not a changelog or a domain specification.

The Warsh foundation runtime is implemented: canonical/public alignment,
selected-source provenance, the King Fahd Uthmani adapter, package composition,
and the shared-rule baseline are executable. Warsh-specific rule verticals and
variants are not part of that baseline. A **concluded** research status means
that a decision is ready to implement, not that its runtime vertical exists.

## Current state

| Workstream | State | Current result |
| --- | --- | --- |
| Source and codepoint audit | Complete | All 62 retained scalars and the foundation sequence families are accepted and fixture-backed |
| Warsh domain research | Concluded | Rule families, boundary behavior, and exception sets audited for implementation planning |
| Variant design | Concluded | Public scopes, values, defaults, registers, and interactions are recorded in [`../variants.md`](../variants.md) |
| Phoneme and rule vocabulary | Concluded | Required additions and reused sound primitives identified; not implemented |
| Cross-riwayah variant audit | Concluded | Shared IDs and riwayah-specific defaults and site scopes are recorded in [`../variants.md`](../variants.md) |
| Test organization | Concluded | Compact semantic tree, projection-aware ownership, RAR reconciliation, coverage registry, and duplicate removal are complete; Warsh fixtures can extend these owners |
| Canonical and model changes | In progress | Source provenance and the shared package seam are complete; Warsh-only sound and rule additions remain below |
| Warsh corpus integration | Complete | The pinned alignment covers 77,425 source words and 77,433 canonical words/spans with typed provenance |
| Warsh rules | In progress | The shared-rule baseline is bound; Warsh-specific classifiers and authored registers remain unimplemented |
| Full-corpus conformance | Not started | No Warsh-specific default-profile conformance baseline exists yet |

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
| [`madd-badal.md`](research/v2/madd-badal.md) | Badal identity, its lazim or muttasil combinations, and duration-only exceptions |
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
- Warsh is single-script by decision: the King Fahd corpus is the only
  supported Warsh script, and no second-script generality is required. A
  reviewed mark-sequence family may therefore directly supply the canonical
  fact it writes: wasl start quality, inclination-bearing vowel quality,
  latent naql structure, joined-only slots, and pausal-alif shapes. Script-
  specific sequences remain normalized in `orthography/`; rules still classify
  canonical facts, an unreviewed sequence still fails projection, and the
  research-derived predicates and register counts in `research/v2/` become
  conformance reconciliation rather than required runtime derivations. Weights,
  selector faces, and boundary-plan-dependent performance stay outside the
  script: the corpus writes one default joined reading and carries no emphasis
  marks.
- Wasl, waqf, and ibtidaa remain explicit boundary states.
- Closed lexical exceptions belong in reviewed authored data.
- Rule occurrences name acted-on units, sounds actually classified or changed,
  and visible source/cell placements derived from ownership. Trigger-only
  context must not be copied onto unrelated characters.
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
- Ibdal names the replaced hamza as source and the replacement unit as host;
  the replacement sound independently receives every applicable madd rule.
- Naql does not require a new phoneme. Isqat receives no runtime rule of its
  own.
- RAR already supplies `madd_badal`, `madd_iwad`, `madd_silah`, and the general
  `iltiqa_haraka`. Warsh adds `taqlil`, `taghliz`, `naql`, and
  `madd_leen_mahmuz`; `imala` classifies kubra.
- Warsh badal replaces ordinary `madd_tabii`. In both Hafs and Warsh,
  `madd_badal` remains present when waqf also establishes
  `madd_arid_lissukun`; independently applicable `madd_lazim` or
  `madd_muttasil` may overlap as well. A stopped fathatan has
  `madd_iwad + madd_tabii`, and pronoun silah has `madd_silah` plus
  `madd_tabii` or `madd_munfasil`.
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

RAR completed the shared projection and much of the Hafs-side rule foundation.
The remaining items are the Warsh-specific extensions or general seams that a
second riwayah now requires.

1. Represent taqlil and imala kubra as distinct typed vowel qualities rather
   than overloading `Quality.E`.
2. Make kubra's collapsed rendering riwayah-owned: Hafs falls back to `/i/`,
   while Warsh falls back to taqlil.
3. Bind the existing effective madd machinery to Warsh transformations and
   preserve the complete additive rule set on each long sound.
4. Emit Warsh occurrences through RAR's source/host, sound, SourceView, and
   CellView contracts without tagging trigger-only characters.
5. Resolve selector-driven raa and lam weight before coloring the following
   fatha or alif, and project that causal choice onto sound and source.
6. Preserve exact inclination in recited spelling independently of whether an
   extra phoneme rendering is enabled.
7. Replace the pronoun-specific `is_silah` model name with a neutral
   joined-only-long shape usable by pronoun silah, Warsh yaa zawaid, and mim
   al-jam'.
8. Give every classifier a declared set of rule IDs it can emit. Build
    `tajweed_rules(riwayah)` from the classifiers bound by that riwayah rather
    than from one nominal rule per classifier or from the global rule enum.

## Test work

The compact semantic harness, target tree, and full RAR projection suites are
reconciled. Hand-authored phonemization behavior has one owner under
`tests/phonemize/`; domain minimal pairs live under conformance, public variant
metadata under API, and fully spelled muqattaat retain complete phoneme and
rule assertions. The audit remains in
[`test-audit.md`](test-audit.md), the target and acceptance contract in
[`test-refactor-plan.md`](test-refactor-plan.md), and Warsh file ownership in
[`warsh-test-placement.md`](warsh-test-placement.md).

- keep the vetted shared cases green for both packaged riwayat;
- preserve executable inventories of every researched exception; and
- implement new Warsh fixed behavior before adding public variants last.

RAR is authoritative for current source/host semantics, cell placement,
overlapping madd identities, and fully spelled muqattaat. Reconciled tests must
preserve those behaviors while retaining compact domain-reviewable cases. The
pre-merge case counts remain planning inputs, not completion evidence; task
completion requires recounting the final collected semantic tree.

## Delivery sequence

Exact PR boundaries may change, but each unit must remain independently
reviewable. Items 1 and 2 are complete; the remaining agreed grouping is:

1. Audit and reorganize the existing tests. Complete.
2. The Warsh source artifact, full source-to-canonical alignment, source
   provenance, script adapter, package, and vetted shared-rule tests form the
   completed foundation. No Warsh-specific classifier belongs to this unit.
3. Model foundation, one PR: classifier `emits` declarations and a
   per-riwayah `tajweed_rules` derived from the bound sets; TAQLIL and KUBRA
   as typed qualities with the riwayah-owned kubra fallback; the neutral
   joined-only-long shape replacing `is_silah`. The `iltiqa_haraka` rename and
   the public `tajweed_rules(riwayah)` entry point already exist.
4. Vertical PRs, failing cases first, in dependency order:
   wasl plus iltiqa (registers, U subregister, silent-qata starts);
   naql; hamza core (generic ibdal/tashil primitives plus single hamza);
   madd badal plus leen mahmuz; hamza meetings; joined-only and pausal shapes
   (mim al-jam, yaa-zawaid, seven alifs in one mark-driven PR); inclination;
   lam taghliz; raa. Inclination precedes lam taghliz, which precedes raa,
   because of the coupled owner and the inclination-created light raa.
5. Run full-corpus attribution and default-profile conformance checks for both
   Hafs and Warsh. This unit also owns two projection gates: the analysis cell
   grid builds for every Warsh corpus word with no unowned sound, unknown
   glyph, or orphan cell; and every retained Warsh scalar family reaches a
   correct `analysis/cells` column, so the published result is directly
   consumable by the phonemizer web inspector without further work.
6. Add the public variant catalogue and selectable behavior last, colocated
   with the semantic tests that own each phenomenon, split into two or three
   PRs by owner family rather than one catch-all.
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
