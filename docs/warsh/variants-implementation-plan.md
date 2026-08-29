# Warsh variant implementation plan

This is the working agreement for workstream 14: publishing and realizing the
Warsh selector catalogue from [`docs/variants.md`](../variants.md). It fixes
the groups, display names, catalogue mechanics, behavior contract, test
placement, and PR order before any rule code is written, per the requirements
recorded on the Hafs variants PR (#76).

The catalogue content itself (IDs, options, defaults, scopes, exclusions,
sources) is already approved in `docs/variants.md` and is not restated here.

## Inventory

Warsh publishes 57 selectors: 12 shared with Hafs and 45 Warsh-only.

- Shared: `iqlab_nasal`, `ikhfaa_shafawi_nasal`, `tamanna_noon`,
  `noon_wasl`, `istifham_article`, `maliyah_halak`, `raa_firq`,
  `raa_alqitr_waqf`, `raa_misr_waqf`, `raa_wanuthur_waqf`, `raa_yasr_waqf`,
  `raa_asr_waqf`.
- Warsh-only: 2 boundary, 9 hamza, 9 inclination (including the two coupled
  lam selectors), 5 lam, 3 systematic raa, 17 lexical raa.

## Shared-ID policy

A shared selector is the same `KhilafId` attribute, the same option
vocabulary, and the same rule machinery in both riwayat. Only the per-riwayah
`khilaf.yaml` row differs: forms or locations in that riwayah's coordinates,
and possibly a different default (`raa_asr_waqf` is `light` in Hafs and
`heavy` in Warsh) or a narrower scope (`raa_asr_waqf` covers three sites in
Warsh; `raa_wanuthur_waqf` interacts with the fixed joined yaa).

Consequences:

- No new code path for a shared ID. The `raa_weight` sited machinery,
  `nasal_place`, and the sakt/rule kinds already consult the selection
  generically; Warsh binds them with its own yaml rows. There is no yaml
  include or merge mechanism, and none is added: a shared selector is the
  same ID authored in both files.
- The Warsh package wires `apply_canonical_khilaf` in its resources (today
  only Hafs does) so Score-changing kinds such as `tamanna` and
  `madd_tasheel` realize; the nasal selectors' current silent fallback to
  the open default in Warsh becomes a real published choice.
- `SitedKhilaf` keys on the vocalised skeleton, so each riwayah's `forms`
  are spelled from its own corpus vocalisation.
- Shared IDs keep the same `group` and display name in both catalogues, so
  the website renders one consistent identity across riwayah pages.
- `schema/test_khilaf_catalogue.py` gains a cross-riwayah law: an ID present
  in both catalogues has identical options (as sets) and identical group;
  defaults and occurrence registers may differ.

## Groups and display names

Display names keep the established law: `id.replace("_", " ").title()`.
Identity work goes into the ID; explanation goes into `description`, which
carries the Arabic forms and scope notes.

Existing group IDs are reused for shared selectors; four groups are new.

| Group | Selectors | Count |
| --- | --- | ---: |
| `word_readings` | `tamanna_noon`, `istifham_article` | 2 |
| `nasal_variants` (hidden) | `iqlab_nasal`, `ikhfaa_shafawi_nasal` | 2 |
| `joined_readings` | `noon_wasl`, `kitabiyah_inni`, `maliyah_halak` | 3 |
| `stopping_starting` | `article_ibtidaa` | 1 |
| `hamza_readings` (new) | `hamza_dhat_fath`, `hamza_muttafiq`, `hamza_damm_kasr`, `jaa_aal`, `hamza_arayta`, `ha_antum`, `hamza_kasr_yaa`, `hamza_aimma`, `allai_waqf` | 9 |
| `inclination` (new) | `dhat_yaa`, `arakahum`, `al_jar`, `jabbarin`, `haa_verse_heads`, `maryam_haa_yaa`, `yaseen_yaa` | 7 |
| `lam_pronunciation` (new) | `lam_dhat_yaa`, `lam_verse_heads`, `lam_separated_by_alif`, `lam_final_waqf`, `lam_after_taa`, `lam_after_zhaa`, `lam_salsal` | 7 |
| `raa_pronunciation` | all 26 raa selectors: the six shared, `raa_fathatan`, `raa_damma`, and the lexical registers | 26 |

Decisions embedded in the table:

- The coupled `lam_dhat_yaa` and `lam_verse_heads` live in
  `lam_pronunciation`: the lam weight is the audible identity of the group,
  and keeping every lam-weight selector in one section beats splitting the
  coupled pair away from the five plain lam selectors.
- All raa selectors stay in one `raa_pronunciation` group. The catalogue
  entry gains an optional `subgroup` key, exposed on the public catalogue
  row, so the website can subcategorize without a second group:
  `systematic` on `raa_fathatan` and `raa_damma`, `lexical` on the rest
  (including the six shared, whose Hafs rows gain the same key).
- `kitabiyah_inni` is a wasl-boundary naql face, so it sits with
  `joined_readings` rather than the hamza group.
- `maliyah_halak` moves from `sakt` to `joined_readings`. The shared-ID
  same-group law makes this a Hafs yaml change too, landing in the setup
  PR; the Hafs `sakt` group keeps `iwaja_qayyima`, `man_raq`, and
  `bal_ran`, and Warsh has no `sakt` group.

## Catalogue mechanics

`khilaf.yaml` for Warsh follows the Hafs schema (version 3): a `variants`
section binding each ID to its kind, options, default, forms or locations,
and junction; and a `catalogue` section with group, display name,
description, visibility, and occurrences.

Static occurrence registers come straight from the closed registers in
`docs/variants.md` (for example the 34 `hamza_arayta` sites, the five
`hamza_aimma` sites, the `raa_five_words` register, the 25
`haa_verse_heads` endings). Every closed-register selector is
`website_visible: true` with enumerated occurrences.

The three general hamza-meeting selectors are also closed: the authored
`data/riwayat/warsh/hamza_meetings.json` register already tags every row
with its owner (`hamza_dhat_fath` 20, `hamza_muttafiq` 62,
`hamza_damm_kasr` 26). Duplicating 108 spans into the yaml would violate
single ownership, so the catalogue entry gains an optional `register` source
key: the loader resolves those occurrences from the authored register at
load time, and `occurrence_count` is real, not `None`.

Five selectors are genuinely structural and cannot enumerate in authored
data: `dhat_yaa`, `raa_fathatan`, `raa_damma`, `lam_after_taa`, and
`lam_after_zhaa`.

- They use `dynamic_scope` but, unlike the Hafs nasal selectors, they are
  real recitation choices and stay `website_visible: true`. The Hafs
  precedent (dynamic implies hidden) was a property of the two nasal
  rendering controls, not a law.
- The website discovers their occurrences per analysis:
  `variant_occurrences()` is extended so a dynamic selector reports an
  occurrence wherever its classifier consulted the selection inside the
  analysed window, with the same wire shape (`variant_id`, `selected`,
  `word_ids`, `anchor`, `requires`, `active`, `masked`) as static rows.
  This is the single wire extension the website needs; everything else
  reuses the Hafs contract.

The two nasal selectors remain hidden in both riwayat.

### Descriptions

The Hafs criterion carries over: a description is added only when the
occurrences span distinct words or a general scope the ID cannot convey; a
single-form selector needs none (`raa_misr_waqf` precedent). The shared
`istifham_article` and `raa_wanuthur_waqf` keep their Hafs descriptions.
Warsh selectors receiving one:

| Selector | Description carries |
| --- | --- |
| `hamza_dhat_fath` | general one-word scope, example form, fixed-tashil exclusions |
| `hamza_muttafiq` | matching-vowel across-word scope, example |
| `hamza_damm_kasr` | damm-kasr across-word scope, example |
| `jaa_aal` | the two `جَآءَ آلُ` phrases |
| `hamza_arayta` | the `أَرَءَيْت` lexical family |
| `hamza_kasr_yaa` | the two exceptional boundaries |
| `article_ibtidaa` | `ٱلِاسْمُ` plus internal-naql articles, example |
| `dhat_yaa` | yaa-origin final alifs, examples |
| `haa_verse_heads` | the pronominal-haa endings, `ذِكْرَاهَا` exclusion |
| `maryam_haa_yaa` | Haa and Yaa of `كهيعص` |
| `lam_dhat_yaa` | the seven sad-lam forms, examples |
| `lam_verse_heads` | the `صَلَّى` verse endings |
| `lam_separated_by_alif` | the five alif-separated words |
| `lam_final_waqf` | the six final-lam word shapes |
| `lam_after_taa` | general taa-lam scope, example |
| `lam_after_zhaa` | general zhaa-lam scope, example |
| `raa_fathatan` | general fathatan scope, example, exclusions |
| `raa_damma` | general damma scope, example |
| `raa_ishruna_kibr` | the grouped `عِشْرُونَ` and `كِبْرٌ` pair |
| `raa_five_words` | the five transmitted words |
| `raa_alif_ayn` | the three word shapes |
| `raa_alif_hamza` | the `ٱفْتِرَآءً` and `مِرَآءً` forms |
| `raa_dual_alif` | the four dual forms |
| `raa_ibrah_kibrahu` | the `عِبْرَة` family plus `كِبْرَهُ` |
| `raa_hidhrakum` | the two forms, `حِذْرَهُمْ` exclusion |

Single-form selectors (`ha_antum`, `hamza_aimma`, `allai_waqf`,
`lam_salsal`, the lexical one-word raa selectors, `kitabiyah_inni`,
`raa_wizra_ukhra`, and the openings) carry no description.

### Occurrence counts

Counts are the authored-register cardinality that lands in the catalogue;
`dynamic` marks the five structural selectors plus the two nasal controls.

| Selector | Count | Selector | Count |
| --- | ---: | --- | ---: |
| `tamanna_noon` | 1 | `raa_firq` | 1 |
| `istifham_article` | 6 | `raa_alqitr_waqf` | 1 |
| `noon_wasl` | 1 | `raa_misr_waqf` | 4 |
| `kitabiyah_inni` | 1 | `raa_wanuthur_waqf` | 6 |
| `maliyah_halak` | 1 | `raa_yasr_waqf` | 1 |
| `article_ibtidaa` | dynamic | `raa_asr_waqf` | 3 |
| `hamza_dhat_fath` | 20 | `raa_fathatan` | dynamic |
| `hamza_muttafiq` | 62 | `raa_damma` | dynamic |
| `hamza_damm_kasr` | 26 | `raa_ishruna_kibr` | 2 |
| `jaa_aal` | 2 | `raa_alishraq` | 1 |
| `hamza_arayta` | 34 | `raa_hayran` | 1 |
| `ha_antum` | 4 | `raa_bisharar` | 1 |
| `hamza_kasr_yaa` | 2 | `raa_five_words` | 16 |
| `hamza_aimma` | 5 | `raa_sihra` | 1 |
| `allai_waqf` | 4 | `raa_iram` | 1 |
| `dhat_yaa` | dynamic | `raa_alif_ayn` | 4 |
| `arakahum` | 1 | `raa_alif_hamza` | 3 |
| `al_jar` | 2 | `raa_dual_alif` | 4 |
| `jabbarin` | 2 | `raa_ashiratukum` | 1 |
| `haa_verse_heads` | 25 | `raa_wizraka` | 1 |
| `maryam_haa_yaa` | 1 | `raa_dhikraka` | 1 |
| `yaseen_yaa` | 1 | `raa_wizra_ukhra` | 5 |
| `lam_dhat_yaa` | 7 | `raa_ijrami` | 1 |
| `lam_verse_heads` | 3 | `raa_hidhrakum` | 2 |
| `lam_separated_by_alif` | 5 | `raa_ibrah_kibrahu` | 7 |
| `lam_final_waqf` | 9 | `iqlab_nasal` | dynamic |
| `lam_after_taa` | dynamic | `ikhfaa_shafawi_nasal` | dynamic |
| `lam_after_zhaa` | dynamic | `lam_salsal` | 4 |

Derivations for the compound counts: `raa_asr_waqf` is the three `فَاسْرِ`
sites only (the two `أَنِ ٱسْرِ` sites are fixed light); `raa_five_words`
is 11 `ذِكْرًا` + 1 `سِتْرًا` + 1 `إِمْرًا` + 1 `وِزْرًا` + 2 `حِجْرًا`;
`lam_final_waqf` is 3 `يُوصَلَ` + `فَصَلَ` + `فَصَّلَ` + `وَبَطَلَ` + 2
`ظَلَّ` + `وَفَصْلَ`; `haa_verse_heads` is 79:27-32, 79:42, 79:44-46, and
91:1-15 with 79:43 excluded; `raa_ibrah_kibrahu` is the six `عِبْرَة`
family sites plus `كِبْرَهُ`; the three hamza-meeting counts come from the
authored register's owner tags. `article_ibtidaa` is dynamic over the
naql-article register (1,307 words) plus `ٱلِاسْمُ`; enumerating it
statically would duplicate the naql register, so it reports through the
dynamic path.

## Behavior contract

The PR 76 lessons are binding:

- A face is a transformation matrix, not a phoneme patch. Before rules are
  written, each selector gets its per-face outcomes across canonical
  reading, source and cell shape, sounds, ownership, rules, mergers, and
  every active or masked boundary state. The owning v2 research file already
  carries the domain half; the matrix rows become the `VariantCase`
  expectations.
- Boundary coupling is bidirectional. `requires` drives both directions: a
  waqf-only face is masked under wasl and recovers ordinary behavior; the
  masked state is asserted, not assumed.
- An inactive written glyph stays visible and soundless without a fabricated
  rule; no width changes, no dropped marks.
- Defaults reproduce today's corpus output. Workstreams 5 through 12
  implemented the default faces as fixed behavior; publishing the catalogue
  must not change the default-profile digests or conformance snapshots.
  Any deviation discovered while wiring a selector is a bug in one of the
  two, to be reconciled explicitly, never absorbed silently.

Warsh-specific realizations, from `phoneme-rule-inventory.md`:

- An eased hamza always renders `ʔ̞`; `tashil` is rejected in
  `extra_phonemes` for Warsh, while the `tashil` rule still classifies the
  eased sound.
- An ibdal face carries `ibdal_hamza` plus the effective madd on the result
  sound and responsible sources; a face producing a moving consonant invents
  no madd.
- `fath`/`taqlil` faces change the typed vowel quality; `taqlil` classifies
  the inclined result. Fath is the absence of the classification.
- Raa and lam weight faces recolor the dependent A vowel in both the sound
  and cell projections; an independent emphasis cause is never removed.
- The coupled lam selectors set vowel quality and lam weight as one
  scalar; at the two wasl-masking sites the selection manifests only at
  waqf.

## Test placement

Per `tests/README.md`: behavior lives in the semantic owner as
`VariantCase` rows; `api/test_variants.py` stays catalogue mechanics only.
No site is duplicated to create a selector-specific file.

| Selector family | Owner file |
| --- | --- |
| Shared, systematic, and lexical raa | `phonemize/emphasis/test_warsh_raa.py` (shared sites may extend `emphasis/test_raa.py` cases with a warsh riwayah where the law is identical) |
| Lam selectors | `phonemize/emphasis/test_warsh_lam_tafkheem.py` |
| Inclination and coupled lam | `phonemize/vowels/inclination/test_warsh_inclination.py` |
| General hamza meetings, `jaa_aal`, `hamza_kasr_yaa` | `phonemize/hamza/test_warsh_hamza_meetings.py` |
| `hamza_arayta`, `ha_antum`, `hamza_aimma`, `allai_waqf`, `hamza_dhat_fath` | `phonemize/hamza/test_warsh_single_hamza.py` |
| `kitabiyah_inni`, `article_ibtidaa` | `phonemize/hamza/test_warsh_naql.py` |
| `noon_wasl`, `istifham_article`, `tamanna_noon`, `maliyah_halak`, nasal | extend the existing shared-site owners (`test_muqattaat.py`, `hamza/test_istifham_article.py`, `vowels/test_ishmam.py`, `test_sakt.py`, `nasal/test_iqlab.py`, `nasal/test_ikhfaa_shafawi.py`) with warsh coverage |
| Qawarira raa face | `phonemize/vowels/test_seven_alifs.py`: the standing xfail flips to live `VariantCase` rows in the raa PR |

Conformance and schema:

- Closed registers (arayta, aimma, five words, haa verse heads, lexical raa
  registers, lam waqf registers) are asserted exhaustively in
  `conformance/test_warsh_registers.py` or the existing per-family register
  files, not in semantic cases.
- `schema/test_khilaf_catalogue.py` gains the Warsh yaml plus the
  cross-riwayah shared-ID law.
- `api/test_variants.py` gains the Warsh `VARIANTS` dict, replaces
  `available_variants("warsh") == {}`, asserts the shared-ID default
  divergences, and asserts dynamic-scope occurrence reporting on one
  systematic selector.
- Register sweeps follow the Hafs pattern (`tests/support/variant.py`):
  every site of a closed-register selector accepts both faces, asserted in
  one sweep next to the semantic rows, as `test_raa.py` and
  `test_istifham_article.py` already do.
- The corpus conformance registers run the default profile with an empty
  selection (`--runslow`/`--runaudit` pytest markers; the old
  `tools/gates.py` floors are gone). Each variants PR must leave those
  default-profile registers green unchanged.

Variant-pending policy: a face that cannot bind yet is authored as its final
`VariantCase` in the owner file under `xfail(strict=True)` naming the
selector ID, exactly like the qawarira precedent. The mark is removed in the
PR that binds the selector; no placeholder sites, no parallel files. This
stays within the existing no-broad-permanent-xfails rule
(`vertical-methodology.md`): each mark is one selector, one owner file, and
dies in a named PR. Because the three PRs land in a fixed order, only faces
owned by a later PR in the sequence may carry the mark at any commit.

## Reconciliation items before PR 1

- Done: `docs/conformance.md` re-measured against the shipped defaults.
  Word-mode residue is 70 (the `ithbat` 27:36 yaa and the six light
  `وَنُذُرِ` endings joined it); verse-mode sequence residue is nine words,
  all khilaf defaults; the word floor is re-pinned at 0.9990 with the
  corrected readings held by the aatani and raa `VariantCase` tests.
- The Warsh `عَاداٗ اَ۬لُّولَىٰ` junction, canonical 53:50, is fixed
  behavior, not a selector. In wasl, Warsh transfers the article hamza's
  damma to lam and the tanwin then merges into that moving lam by the
  ordinary idgham bila ghunnah; the selected script writes the shadda. The
  waw-hamz and tanwin-izhar faces at this site belong to Qalun. At ibtidaa
  the two naql-article starts are already owned by `article_ibtidaa`,
  whose scope names `ٱلْأُولَى`; the route-dependent waw duration is
  outside the sound-length model per `madd-badal.md`. The pending work is
  the fixed tanwin-into-naql-lam interaction; implementing it removes the
  register carve-out in `docs/conformance.md`. It lands with PR 3's
  boundary work or earlier as a standalone fix.

## PR order

A setup PR precedes the family PRs and carries everything more than one
family needs, so the families touch only their own domains afterward:

0. **Setup** — the Warsh `khilaf.yaml` scaffold and its wiring
   (`load_khilaf` path, `apply_canonical_khilaf` in Warsh resources), the
   `subgroup` and `register` catalogue keys with their schema tests, the
   dynamic `variant_occurrences()` wire extension, the 45 Warsh `KhilafId`
   constants, and the `maliyah_halak` group move in the Hafs yaml (the
   `docs/conformance.md` refresh is already applied on the branch). No
   Warsh selector is published yet:
   the scaffold keeps `available_variants("warsh")` empty until a family
   binds rows, because a published-but-unbound selector would be a silent
   no-op.

Then three owner-family PRs onto `feat/warsh-phonemizer`, raa first
because its machinery is fully proven by Hafs:

1. **Raa** — 26 selectors: six shared rows in the Warsh yaml, the three
   systematic selectors consulted inside the raa classifier's eligibility
   path, the 17 lexical registers, boundary behavior (`heavy_wasl`,
   bisharar's split, wizra-ukhra wasl-only), and the qawarira xfail
   resolution.
2. **Inclination and lam** — 14 selectors: the general and lexical
   inclination faces, opening-letter faces, coupled lam with its wasl
   masking, and the five lam selectors with their waqf ownership rules.
3. **Hamza and boundaries** — 17 selectors: the hamza meeting generals and
   their lexical carve-outs, the single-word hamza families with the arayta
   waqf fallback, `allai_waqf`, `kitabiyah_inni`, `article_ibtidaa`, plus
   the shared `noon_wasl`, `istifham_article`, `tamanna_noon`,
   `maliyah_halak`, and nasal rows. This PR completes the catalogue and
   flips the full `available_variants("warsh")` assertion.

Each PR ships its yaml rows, rules, semantic `VariantCase` rows, register
conformance, and website-wire assertions together, and leaves the default
digests unchanged.

## Parallelization and signoff

After the setup PR, the three family PRs are largely independent: raa,
inclination/lam, and hamza/boundary bind disjoint classifiers, own
disjoint semantic test files, and touch different rule modules. They can
run in parallel worktrees. The known contention is mechanical, not
semantic:

- all three append to `data/riwayat/warsh/khilaf.yaml`,
  `tests/api/test_variants.py`'s `VARIANTS` dict, and the bindings in
  `riwayat/warsh/rules.py` — disjoint hunks, trivial rebases;
- merges are serialized (whichever finishes first lands first), and the
  final family PR flips the full-catalogue assertions;
- any hardcoded catalogue-length assertion is written against the family's
  own additions, not a global count, until the last PR pins the total.

Each family passes two approval gates before implementation:

1. **Shape signoff** — a per-face transformation matrix for every selector
   in the family: canonical reading, source and cell shape, sounds,
   ownership, rules, mergers, and each active or masked boundary state.
   Approved before any test or rule code.
2. **Test approval** — the authored `VariantCase` rows, register sweeps,
   and wire assertions on the branch, reviewed before the rules that make
   them pass.

The three shape documents can be drafted up front and signed off as a
batch, so the parallel implementation phase is not serialized on review.
