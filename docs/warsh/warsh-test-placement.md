# Warsh test placement

This document audits how Warsh coverage fits the target test organization in
`test-refactor-plan.md`. It decides whether each phenomenon extends a shared
file, needs a Warsh-only file, or needs a shared foundation plus separate Hafs
and Warsh files.

The domain specifications remain in `research/v2/`. Public selector IDs,
values, defaults, and scopes remain in `../variants.md`. This document owns
test placement and riwayah naming only.

## Result

The planned organization is flexible enough for Warsh, but several broad
files must be split before implementation. The final organization follows
three rules:

1. `test_<phenomenon>.py` means the recitation law is shared. Its case table
   may contain shared sites, Hafs-only sites, Warsh-only sites, or riwayah
   picks when those rows still verify the same law.
2. `test_hafs_<phenomenon>.py` means the law, register, or selector exists only
   in the supported Hafs domain.
3. `test_warsh_<phenomenon>.py` means the law, register, or selector exists
   only in the supported Warsh domain.

The prefix describes domain ownership, not the origin of an example. A shared
ikhfaa file may use different clean corpus sites for Hafs and Warsh. A Warsh
naql case never belongs in that file merely because its final sound contains a
nasal or vowel.

When a broad subject has a small shared foundation but substantially different
riwayah laws, it uses all three forms. Raa is the clearest example:

- `test_raa.py` owns shared coloring and the shared lexical choices;
- `test_hafs_raa.py` owns Hafs structural branches; and
- `test_warsh_raa.py` owns Warsh structural and lexical branches.

This is preferable to parallel `hafs/` and `warsh/` trees. Shared rules stay
visibly shared, while a reviewer can open one prefixed file to inspect a
riwayah-specific domain.

## Revised phonemization tree

The following tree supersedes the file placement, but not the coverage method
or harness contract, in `test-refactor-plan.md`. Counts are logical review
cases. `V` marks a case added only in the final selector phase.

```text
tests/phonemize/                               # 508 cases: 436 fixed + 72V
  articles/                                   # 20
    test_lam_qamariyyah.py                    # 8
    test_lam_shamsiyyah.py                    # 9
    test_lam_contrasts.py                     # 3

  assimilation/                              # 29: 27 fixed + 2V
    test_mutamathilayn.py                     # 10
    test_mutaqaribayn.py                      # 3
    test_mutajanisayn_kamil.py                # 10
    test_mutajanisayn_naqis.py                # 4
    test_hafs_idgham_choices.py               # 2V

  emphasis/                                   # 97: 62 fixed + 35V
    test_istilaa.py                           # 12
    test_hafs_seen_sad.py                     # 4V
    test_raa.py                               # 6V
    test_hafs_raa.py                          # 19
    test_warsh_raa.py                         # 31: 11 fixed + 20V
    test_allah_lam.py                         # 8
    test_warsh_lam_taghliz.py                 # 17: 12 fixed + 5V

  hamza/                                      # 104: 90 fixed + 14V
    test_wasl_start.py                        # 14
    test_hafs_alism_ibtidaa.py                # 1V
    test_wasl_silent.py                       # 3
    test_iltiqa.py                            # 15
    test_seats.py                             # 5
    test_ibdal.py                             # 6
    test_tashil.py                            # 2
    test_warsh_naql.py                        # 16: 14 fixed + 2V
    test_warsh_single_hamza.py                # 15: 13 fixed + 2V
    test_istifham_article.py                  # 3V
    test_warsh_hamza_meetings.py              # 24: 18 fixed + 6V

  nasal/                                      # 57: 55 fixed + 2V
    test_ghunnah_mushaddadah.py               # 3
    test_idgham_bi_ghunnah.py                 # 6
    test_idgham_bila_ghunnah.py               # 4
    test_idgham_shafawi.py                    # 2
    test_ikhfaa.py                            # 13
    test_ikhfaa_shafawi.py                    # 2: 1 fixed + 1V
    test_iqlab.py                             # 6: 5 fixed + 1V
    test_izhar.py                             # 12
    test_izhar_shafawi.py                     # 5
    test_noon_partition.py                    # 4

  vowels/                                     # 149: 137 fixed + 12V
    inclination/                              # 49: 40 fixed + 9V
      test_quality.py                         # 6
      test_hafs_inclination.py                # 2
      test_warsh_inclination.py               # 20: 11 fixed + 9V
      test_warsh_inclination_classification.py # 14
      test_warsh_inclination_coloring.py      # 7

    madd/                                     # 65
      test_tabii.py                           # 3
      test_muttasil.py                        # 2
      test_munfasil.py                        # 5
      test_lazim.py                           # 2
      test_arid.py                            # 5
      test_leen.py                            # 4
      test_iwad.py                            # 4
      test_haa_silah.py                       # 5
      test_warsh_badal.py                     # 13
      test_warsh_leen_mahmuz.py               # 8
      test_warsh_mim_al_jam.py                # 7
      test_warsh_yaa_zawaid.py                # 7

    test_hafs_daaf_vowel.py                   # 1V
    test_pausal_vowels.py                     # 3
    test_final_glides.py                      # 9
    test_hafs_aatani.py                       # 1V
    test_seven_alifs.py                       # 13: 12 fixed + 1V
    test_written_carriers.py                  # 8

  test_muqattaat.py                           # 15: 14 fixed + 1V
  test_hafs_muqattaat.py                      # 1V
  test_qalqala.py                             # 13
  test_sakt.py                                # 5V
  test_silent_letters.py                      # 13
  test_taa_marbuta.py                         # 5
```

The ownership splits do not duplicate test volume. The final budget is 436
fixed/default and 72 selector cases. Multiple lexical forms of one selector
may require separate semantic rows even though the API metadata is one entry.

## Placement decisions

### Articles

The article law is shared. `test_lam_qamariyyah.py` and
`test_lam_shamsiyyah.py` remain unprefixed and may use different clean sites
to cover the fourteen letters for each riwayah. `test_lam_contrasts.py` owns
minimal negative shapes that resemble an article but are not one.

Warsh article naql does not belong here. Its cause is removal of a qata hamza
and transfer of its vowel, so `test_warsh_naql.py` owns it. The Hafs-only
`alism_ibtidaa` selector belongs in `test_hafs_alism_ibtidaa.py`; the related
Warsh article-start choice stays with naql because that file must verify that
the removed qata hamza is not restored.

### Assimilation

Ordinary mutamathilayn, mutaqaribayn, and mutajanisayn are shared laws and
retain unprefixed files. Clean Warsh rows can extend them as soon as the
adapter produces the same canonical participants.

There is no standalone fakk-al-idgham file and no `fakk_idgham` rule. The test
state is named `ibtidaa-on-host`: starting on word two makes the cross-word
merger unavailable and realizes its host once. That state belongs beside the
joined state and asserts the single host sound plus absence of the merger.

The Hafs choices at `ارْكَب مَّعَنَا` and `يَلْهَث ذَّلِكَ` are not generic
mutajanisayn examples. They move to `test_hafs_idgham_choices.py`, where the
final selector phase can test `irkab_maana` and `yalhath_dhalik` without
making the shared file appear route-dependent.

### Emphasis, raa, and lam

`test_istilaa.py` is shared. It covers the same seven-letter inventory and
dependent A coloring in both riwayat, using clean sites.

Raa needs the three-file split described above. The shared file owns the
sound/rule contract, dependent A coloring, and shared closed selectors. The
Hafs file owns its structural decision tree. The Warsh file owns the Warsh
tree, broad systematic scopes, lexical registers, exclusions, and state
masking. Combining all of that into one file would force a reviewer to
continually infer which tree an example belongs to.

`test_allah_lam.py` owns only the heavy, light, and context-conditioned forms
of the divine name. Ordinary light lam needs no dedicated sweep. Warsh
taghliz, Warsh tarqiq choices, dependent A coloring, alif separation,
final-lam waqf, and the salsal register belong in
`test_warsh_lam_taghliz.py`. A taghliz occurrence owns the lam and every
causally dependent A realization, including fatha, fathatan, a carrier, and
madd iwad.

The four Hafs seen/saad choices use `test_hafs_seen_sad.py`.

### Hamza

Hamza files own transformations and boundary causes. Vowel and madd files own
the resulting quality or length classification only.

- `test_wasl_start.py` owns the shared A/I/U derivation algorithm and a vetted
  riwayah-specific lexical input where necessary.
- `test_wasl_silent.py` owns the shared started-versus-joined onset behavior.
- `test_iltiqa.py` owns shared shortening and ordinary A/I repair after wasl
  elision. Its separate Warsh U-over-I section runs the same boundaries under
  Hafs so the different repairs and exact exclusions stay adjacent.
- `test_ibdal.py` owns generic replacement shapes, effects, and reach.
  `test_tashil.py` owns the generic eased-hamza shape, A/U/I nucleus pairing,
  Hafs-only extra-token fallback, and reach.
- `test_warsh_naql.py`, `test_warsh_single_hamza.py`, and
  `test_warsh_hamza_meetings.py` own the three Warsh classifiers and their
  closed registers.
- `test_istifham_article.py` is shared because the selector has the same
  semantic identity in both riwayat. It has three rows, one each for
  `ءَآلذَّكَرَيْنِ`, `ءَآلْـَٰٔنَ`, and `ءَآللَّهُ`, because their article,
  root-hamza, and Allah-lam consequences differ.

Tashil is not inclination. It is an eased hamza onset whose following nucleus
retains A, U, or I quality. Ibdal is not owned by madd merely because some
replacements create a long vowel. The hamza test proves the transformation
and its complete reach; the relevant madd test independently proves the
resulting `madd_tabii`, `madd_lazim`, or `madd_badal` classification. One
integration row may assert both rule families, but neither behavior is copied
into two exhaustive case tables.

Naql belongs to hamza because qata removal and restoration define the law.
Iltiqa also belongs to hamza because wasl elision creates the collision. The
inserted `iltiqa_haraka` reaches only its A/I/U sound; the host consonant or
nunation slot and any written mark own the character-side evidence.

### Nasal rules

All ordinary noon, tanwin, and meem laws remain shared. Their files should add
selected Warsh rows only where naql, mim al-jam, yaa-zawaid, and special
verse-edge behavior do not alter the local structure. The two nasal posture
selectors remain in the shared iqlab and ikhfaa-shafawi files because they
change realization, not riwayah law.

The shared nasal files also own pausal recovery. When a stop drops the final
haraka or tanwin from a lexical noon or meem, the surviving consonant is clear:
`izhar` for noon and `izhar_shafawi` for meem. When an explicit stop cancels a
cross-word idgham, ikhfaa, or iqlab, the same clear classification returns
even if the source script omitted a sukun in anticipation of joining. Four
dedicated cases cover noon/meem crossed with haraka/tanwin removal; existing
joined/stopped state matrices cover recovery from the cross-word families.

Mim al-jam does not move into `nasal/`. Its relevant Warsh behavior is a
joined-only U vowel whose principal branches are conditional madd in wasl.
`test_warsh_mim_al_jam.py` therefore lives under `vowels/madd/`. Ordinary
nasal consequences after that vowel may appear in a complete integration
span, but the mim-al-jam file owns the case.

### Vowels and madd

Pausal vowels, final glides, written carriers, and structural madd rules
retain unprefixed files. Ordinary A/I/U projection is already exercised by
the semantic cases and has no separate baseline file.
`daaf_haraka` is the separate Hafs-only lexical choice and lives in the
explicitly named `test_hafs_daaf_vowel.py`.

`test_seven_alifs.py` deliberately stays shared. The seven lexical forms are
one closed phenomenon whose boundary behavior differs by riwayah. Keeping its
Hafs and Warsh matrices adjacent makes the difference easier to verify than
two nearly parallel files. The file may use riwayah picks or separate compact
rows depending on whether the Arabic source span and explanation remain
readable.

Mim al-jam and yaa-zawaid are Warsh-only authored families under `madd/`.
Their files own the full wasl/waqf matrices, including mim's short-U iltiqa
branch and the one consonantal yaa-zawaid exception, so placing them by their
principal madd behavior does not split either family. Madd badal and madd leen
mahmuz also get Warsh-prefixed files because their public classifier/register
contracts are introduced by the Warsh implementation. Ordinary `madd_tabii`, `madd_muttasil`,
`madd_munfasil`, `madd_lazim`, `madd_arid`, `madd_leen`, and `madd_iwad`
remain shared.

### Inclination

Inclination needs a shared foundation and explicit riwayah files:

- `test_quality.py` owns typed FATH, TAQLIL, and KUBRA qualities, exact tokens,
  extra-phoneme collapse, and the invariant that typed quality and rule do not
  disappear when a rendered token collapses;
- `test_hafs_inclination.py` owns the Hafs fixed kubra case;
- `test_warsh_inclination.py` owns fixed, default, named, opening-letter, and
  selector behavior;
- `test_warsh_inclination_classification.py` owns generated predicate and
  register completeness; and
- `test_warsh_inclination_coloring.py` owns raa/lam coupling and boundary
  masking.

This is clearer than one overloaded inclination file and clearer than folding
inclination into general vowels. Inclination remains under `vowels/` because
it is vowel quality, while the subfolder makes its substantial classifier and
coupling surface discoverable.

### Muqattaat, qalqala, sakt, and lexical endings

`test_muqattaat.py` owns all fourteen unique opening forms. Every fixed/default
row asserts the complete phoneme sequence and every applicable rule with exact
source and sound reach; it is not a phoneme-only table. Riwayah picks keep
fixed Yaseen behavior and opening-letter inclination beside the same Arabic
form. The shared Noon selector is in this file. `test_hafs_muqattaat.py` owns
only the Hafs Yaseen selector; Warsh inclination selector matrices remain in
the inclination file and are integrated here only at their default.

Qalqala, silent letters, and taa marbuta remain shared. Their Warsh rows use
clean sites and the same rule IDs.

One `test_sakt.py` owns the shared `maliyah_halak` selector and all four
Hafs-only lexical sakt choices. Every row asserts sakt/idraj phonemes, blocked
or restored downstream rules, and its explicit-waqf mask. Sakt is a
continuing-reading junction; an explicit stop on the first word masks the
choice and uses normal waqf behavior.

No Tamanna behavior test is added. Its selector metadata is covered by the
generic catalogue contract, following the explicit ownership decision.

## Adapter and non-phonemization placement

Source-specific adapter tests are named explicitly:

```text
tests/adapter/
  test_warsh_corpus_alignment.py       # selected-source to canonical mapping
  test_warsh_script_projection.py      # King Fahd sequence projection
  test_inventory_contract.py           # shared package contract
  test_inscription.py                  # shared typed spelling relations
  test_attestations.py                 # shared evidence semantics
  test_hamza_seats.py                  # shared canonical seat behavior
  test_roundtrip.py                    # parameterized by package
  test_selectors.py                    # package-owned selector fixtures
```

Selected-source coordinates occur only in adapter fixtures and provenance
assertions. Semantic `Site` values use canonical/public coordinates.

API, document, engine, and schema tests remain unprefixed because they verify
public or package-agnostic architecture. They are parameterized by riwayah
where applicable. A prefixed file is justified only when its asserted domain
fact cannot exist for the other package.

The conformance tree becomes:

```text
tests/conformance/                         # 116 cases total
  test_hafs_legacy_parity.py               # 3
  test_rule_coverage.py                    # 70
  test_hafs_script_agreement.py            # 21
  test_warsh_registers.py                  # 16
  test_warsh_default_profile.py            # 6
```

Only Hafs currently has two supported scripts, so script agreement remains a
21-case Hafs gate. Warsh source-to-canonical agreement belongs in the adapter
alignment file, not in a fake second-script conformance matrix. The whole
planned logical suite is therefore 1,385 cases.

`test_rule_coverage.py` remains shared. It verifies that the `Rule` vocabulary
is global, every classifier declares its complete `emits` set, each riwayah
binds the intended classifiers through its `RuleSet`, shared rule IDs retain
one meaning, and a Warsh-only emitted rule is absent from the Hafs set unless
Hafs has its own classifier for that same rule.

## Adapter-first shared coverage

The first Warsh implementation PR should prove corpus alignment, sequence
projection, canonical construction, and already shared tajweed. It should not
wait for a Warsh snapshot or a Warsh-specific rule vertical.

Correct expectations can be authored before the adapter passes. A failure is
then high-confidence evidence of projection, canonical construction, hidden
Hafs coupling, or a missing shared binding, provided the case was vetted
against the selected script and the v2 domain specifications. Such failures
may guide implementation during the PR; they must not be committed as broad
permanent xfails.

### Extend immediately

| Shared owner | Warsh coverage target | Selection constraint |
| --- | --- | --- |
| Article lam | Similar coverage of all moon and sun letters | Avoid article-naql and istifham-article sites |
| Noon and tanwin | All 15 ikhfaa followers, six throat letters, four ghunnah-idgham hosts, two no-ghunnah hosts, and ba iqlab | Avoid naql, mim al-jam, yaa-zawaid, and special verse edges |
| Meem | Representative izhar, idgham, and ikhfaa | Avoid authored mim-al-jam behavior |
| Qalqala | All five letters and the existing state partitions | Avoid a span with unresolved Warsh hamza or inclination |
| Ordinary assimilation | Every host/source and complete/incomplete branch already judged shared | Avoid riwayah-specific lexical choices |
| Pausal endings | Representative pausal vowel, iwad, taa marbuta, and final-glide matrices | Use identical canonical boundary shapes |
| Structural madd | Comparable branch coverage for ordinary tabii, muttasil, munfasil, lazim, arid, leen, and iwad | Exclude badal, leen-mahmuz exceptions, and transformed hamza |
| Wasl | Vetted article, noun, verb, start, and elision rows | Use the Warsh lexical reading; do not copy the Hafs lexicon blindly |
| Ordinary carriers and seats | Representative common canonical shapes | Adapter glyph composition may differ, sound law must not |

Warsh does not need every Hafs example. It needs similar partition coverage.
Dense rows may cover several distinct triggers in one reviewed Arabic span,
with each occurrence asserted separately.

### Shared-file extension ledger

This ledger accounts for every planned unprefixed phonemization file. It says
how the compact Hafs coverage can admit Warsh without turning a shared file
into a mixed-domain catch-all.

| Planned shared file | Warsh placement | Expected case form | Timing |
| --- | --- | --- | --- |
| `articles/test_lam_qamariyyah.py` | Cover the same fourteen-letter partition with clean Warsh article sites | Reuse a shared site when clean; otherwise add a Warsh site row in the same trigger table | Adapter baseline |
| `articles/test_lam_shamsiyyah.py` | Cover the same fourteen-letter partition and atomic gemination | Same method as qamariyyah | Adapter baseline |
| `articles/test_lam_contrasts.py` | Recheck article, lexical lam, and one-lam spelling | Use a pick only for a small source selector difference | Adapter baseline where clean |
| `assimilation/test_mutamathilayn.py` | Cover the same source/host partitions | Shared row or clean Warsh substitute | Adapter baseline |
| `assimilation/test_mutaqaribayn.py` | Cover the same ordinary source/host partitions | Shared row or clean Warsh substitute | Adapter baseline |
| `assimilation/test_mutajanisayn_kamil.py` | Cover every shared complete-idgham branch | Shared row or clean Warsh substitute | Adapter baseline |
| `assimilation/test_mutajanisayn_naqis.py` | Cover every shared retained-feature branch | Separate Warsh row if the source selector changes materially | Adapter baseline after canonical feature support |
| `emphasis/test_istilaa.py` | Cover all seven letters and short, long, fathatan, and iwad A coloring | Shared site or same-table substitute | Adapter baseline |
| `emphasis/test_raa.py` | Exercise shared sound/reach and shared selectors only | Fixed shared rows first; selector rows last | Foundation, then variants |
| `emphasis/test_allah_lam.py` | Exercise heavy, light, and context-conditioned divine-name lam | Shared rows or clean substitutes | Adapter baseline |
| `hamza/test_wasl_start.py` | Cover the same morphology algorithm using Warsh lexical input | Separate row for a lexical reading difference; pick only the local expected vowel | Adapter baseline after alignment |
| `hamza/test_wasl_silent.py` | Cover ordinary joined elision | Shared rows where the canonical onset is WASL | Adapter baseline |
| `hamza/test_iltiqa.py` | Cover shared shortening and ordinary repair | Shared rows plus adjacent Hafs/Warsh U-over-I contrasts | Wasl/iltiqa vertical |
| `hamza/test_seats.py` | Verify shared canonical hamza-seat semantics | Source selectors may differ; canonical assertion stays shared | Adapter baseline |
| `hamza/test_ibdal.py` | Verify generic transformation primitives independent of classifier | Small typed fixtures, not a corpus sweep | RuleSet/hamza foundation |
| `hamza/test_tashil.py` | Verify eased onset plus A/U/I nucleus and Hafs rendering fallback | Small typed fixtures, not a corpus sweep | RuleSet/hamza foundation |
| `hamza/test_istifham_article.py` | Execute the same selector against each riwayah package | Three `VariantCase` rows for the three distinct lexical forms | Variants last |
| Every file under `nasal/` | Preserve the trigger partitions and pausal-clear recovery branches listed in the main plan | Clean Warsh rows share the file; output picks only where an optional public token differs; stopped idgham/ikhfaa/iqlab states recover clear noon/meem | Adapter baseline |
| `vowels/inclination/test_quality.py` | Verify typed quality and renderer semantics for both riwayat | Tiny explicit riwayah matrix | Model foundation |
| `vowels/madd/test_tabii.py` | Preserve ordinary carrier/source partitions | Clean shared rows | Adapter baseline |
| `vowels/madd/test_muttasil.py` | Preserve same-word qata-after-long structure | Avoid transformed Warsh hamza | Adapter baseline |
| `vowels/madd/test_munfasil.py` | Preserve cross-word qata-after-long structure | Avoid naql, mim al-jam, and yaa-zawaid | Adapter baseline |
| `vowels/madd/test_lazim.py` | Preserve fixed-sukun and geminate partitions | Clean shared rows | Adapter baseline |
| `vowels/madd/test_arid.py` | Preserve state matrix at plain waqf | Shared row or clean substitute | Adapter baseline |
| `vowels/madd/test_leen.py` | Preserve ordinary leen states | Exclude Warsh leen-mahmuz registers | Adapter baseline |
| `vowels/madd/test_iwad.py` | Preserve fathatan-to-pausal-A behavior and coloring | Shared state rows with clean contexts | Adapter baseline |
| `vowels/madd/test_haa_silah.py` | Verify pronoun-haa silah, blockers, waqf masking, and silah kubra | Shared compact state rows | Adapter baseline |
| `vowels/test_pausal_vowels.py` | Verify shared joined/stopped nucleus changes | Shared state rows | Adapter baseline |
| `vowels/test_final_glides.py` | Verify shared final waw/yaa boundary shapes | Shared rows where lexical reading agrees | Adapter baseline |
| `vowels/test_hafs_aatani.py` | Keep the Aatani waqf choice with its own lexical owner | One Hafs-only `VariantCase` | Variants last |
| `vowels/test_seven_alifs.py` | Put Hafs and Warsh matrices beside each other | Shared `StateCase` or paired rows by lexical form | Seven-alif vertical |
| `vowels/test_written_carriers.py` | Verify carrier/source relations independent of raw glyph form | Source-selector picks with one canonical expectation | Adapter baseline |
| `test_muqattaat.py` | Verify all fourteen forms, complete phonemes, and complete rule reach | One fixed/default row per form with small riwayah picks; shared Noon selector added last | Foundation through relevant verticals |
| `test_qalqala.py` | Preserve all five letters and state/degree partitions | Clean shared rows | Adapter baseline |
| `test_sakt.py` | Own shared Maliyah and the four Hafs lexical sites | Five `VariantCase` rows with sakt/idraj, downstream-rule, and waqf assertions | Variants last |
| `test_silent_letters.py` | Verify shared canonical silence and attribution | Shared row or source-selector pick | Adapter baseline |
| `test_taa_marbuta.py` | Verify shared pausal haa transformation | Shared state rows | Adapter baseline |

`Site.shared(...)` is not required merely because a file is shared. A shared
file asserts one shared law; it may use different corpus witnesses when that
makes each riwayah's source span cleaner and easier to review.

### Defer to owning vertical

Do not include these in the adapter baseline:

- naql or article naql;
- the Warsh U iltiqa register;
- Warsh single-hamza or hamza-meeting transformations;
- mim al-jam or yaa-zawaid;
- differing seven-alif branches;
- madd badal or madd leen mahmuz;
- inclination, Warsh raa, or lam taghliz;
- Warsh-specific muqattaat behavior; or
- any selector behavior.

The shared seven-alif file may exist after the mechanical refactor, but its
Warsh rows land with the seven-alif vertical rather than the adapter baseline.

## Site and expectation conventions

Use `Site.shared(...)` only when both riwayat use the same canonical reference
and span for the same law. A selected-source coordinate never enters it.

Use `pick(...)` when a small riwayah difference remains easy to compare in one
row, such as a phoneme string, source selector, or rule reach. Create separate
rows when the trigger, explanation, state matrix, or rule identity differs.
`pick` must not become a way to hide two unrelated tests behind one case ID.

A shared file may therefore contain:

- one row executed unchanged for both riwayat;
- one row with a shared site and a small expected-output pick;
- one Hafs site row and one Warsh site row covering the same partition; or
- a generated finite-alphabet reconciliation plus a small representative
  output table.

All phoneme expectations remain ASCII-space-separated inventory tokens.
Character and sound reach remain exact. Arabic comments stay beside the case
table so a domain reviewer never has to reconstruct the text from coordinates.

## Vertical implementation map

| Implementation vertical | Primary phonemization owner | Supporting tests |
| --- | --- | --- |
| Corpus and projection | Shared safe rows listed above | `adapter/test_warsh_*`, schema roundtrip |
| RuleSet foundation | Existing shared semantic rows | rule coverage, model vocabulary, API rules |
| Wasl | `hamza/test_wasl_start.py`, `test_wasl_silent.py` | adapter wasl projections |
| Iltiqa | `hamza/test_iltiqa.py` | effective-state engine tests |
| Naql | `hamza/test_warsh_naql.py` | register and source-attribution tests |
| Single hamza | generic ibdal/tashil plus `test_warsh_single_hamza.py` | effective madd and adapter source tests |
| Hamza meetings | `hamza/test_warsh_hamza_meetings.py` | effective madd and boundary plan tests |
| Mim al-jam | `vowels/madd/test_warsh_mim_al_jam.py` | joined-only identity and authored before-wasl contrast |
| Yaa-zawaid | `vowels/madd/test_warsh_yaa_zawaid.py` | joined-only model and authored-register tests |
| Seven alifs | `vowels/test_seven_alifs.py` | authored-register tests |
| Madd badal | `vowels/madd/test_warsh_badal.py` | provenance/effective-state tests, including badal plus arid at waqf |
| Madd leen mahmuz | `vowels/madd/test_warsh_leen_mahmuz.py` | register reconciliation |
| Inclination | shared quality plus three `test_warsh_inclination*` files | render, register, coupling tests |
| Raa | shared raa plus `test_warsh_raa.py` | authored-register tests |
| Lam taghliz | `emphasis/test_warsh_lam_taghliz.py` | coupling and register tests |
| Selectors | each semantic owner above | generic API catalogue last |

## Placement acceptance criteria

- every v2 phenomenon has one primary phonemization owner;
- no Warsh-only classifier is hidden in a generic shared file;
- no shared rule is duplicated into parallel Hafs and Warsh files merely
  because the source spelling or coordinate differs;
- pausal noon/meem recovery is asserted positively as izhar, not merely as
  absence of the joined idgham, ikhfaa, or iqlab rule;
- raa, inclination, and muqattaat expose their shared foundation without
  overloading one cross-riwayah file;
- hamza transformation and madd classification have distinct test ownership
  with one deliberate integration overlap;
- mim al-jam and yaa-zawaid remain intact authored families under `madd/`,
  including their non-madd boundary branches;
- all fourteen muqattaat forms assert phonemes and every applicable rule, and
  all five sakt selectors remain in one semantic file;
- every adapter-first Warsh row is independently vetted and free of an
  unresolved Warsh-specific phenomenon in its asserted span;
- shared coverage remains comparable, not necessarily site-for-site equal;
- selected-source coordinates stay in adapter provenance while semantic sites
  remain canonical;
- prefixed filenames match actual domain ownership; and
- selector behavior remains the final implementation phase.
