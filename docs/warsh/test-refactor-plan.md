# Test refactor plan

This document is the executable plan for reorganizing the current tests and
adding Warsh coverage. It owns the target tree, logical case budgets, compact
test style, harness contract, coverage method, migration order, and acceptance
criteria.

The domain truth stays in `docs/warsh/research/v2/`. Public selector IDs,
values, defaults, and scopes stay in `docs/variants.md`. This document does not
repeat those specifications. `warsh-test-placement.md` owns the shared versus
riwayah-prefixed file split and the adapter-first Warsh extension audit.

## Outcome

The refactor must produce one semantically organized phonemization suite for
all riwayat. It must not produce parallel `hafs/` and `warsh/` test trees.

The target has these properties:

- all hand-authored recitation examples live under `tests/phonemize/`;
- adapter, API, document, engine, schema, conformance, and snapshots do not
  mix with phonemization examples;
- each Warsh implementation vertical has an obvious owning test file;
- wasl, waqf, ibtidaa, and sakt are state dimensions inside semantic owners,
  not top-level folders;
- complete phoneme spans, source reach, sound reach, and state are visible in
  compact case tables;
- finite alphabets and closed registers are exhaustive;
- representation and state dimensions are tested orthogonally instead of as
  unjustified Cartesian products; and
- variants are implemented and tested only in the final phase.

## What a case count means

The tree below counts logical review cases, not pytest's final collected node
count.

A logical case is one adjacent Arabic example and one domain claim that a
reviewer verifies as a unit. One case may execute:

- multiple boundary states through `StateCase`;
- every declared riwayah and its supported scripts;
- several exact source and sound assertions; and
- every value of one selector through `VariantCase` in the final phase.

The harness reports each state, riwayah, script, selector value, and exact
occurrence as a separate subcheck. A failure remains narrow even when the
reviewer reads one compact row.

`V` in the tree means a logical case added in the final variant phase. The
fixed/default target is 436 cases. The final target is 508 cases, consisting
of 436 fixed/default cases plus 72 semantic selector cases. The generic API
contract covers the metadata of all 71 public selectors in `docs/variants.md`;
per the explicit test-ownership decision, `tamanna_noon` does not get another
phonemization behavior case.

Large occurrence registers are not expanded into hundreds of full-output
cases. They have:

1. a test-owned exact register;
2. one generated completeness/reconciliation test; and
3. representative full-output cases for every distinct implementation
   branch, state, and rule-reach shape.

Changing a planned count is allowed only with an updated coverage matrix. A
count is a review budget backed by coverage, not a target to pad.

## Target tree and case budgets

Every Python test file in the target tree is listed below. Helper and data
files are included for discoverability even when they contain no cases.

```text
tests/
  README.md
  __init__.py
  conftest.py

  phonemize/                                      # 508 cases: 436 fixed + 72V
    __init__.py

    articles/                                     # 20 cases
      __init__.py
      test_lam_qamariyyah.py                      # 8
      test_lam_shamsiyyah.py                      # 9
      test_lam_contrasts.py                       # 3

    assimilation/                                 # 29 cases: 27 fixed + 2V
      __init__.py
      test_mutamathilayn.py                       # 10
      test_mutaqaribayn.py                        # 3
      test_mutajanisayn_kamil.py                  # 10
      test_mutajanisayn_naqis.py                  # 4
      test_hafs_idgham_choices.py                 # 2V

    emphasis/                                     # 97 cases: 62 fixed + 35V
      __init__.py
      test_istilaa.py                             # 12
      test_hafs_seen_sad.py                       # 4V
      test_raa.py                                 # 6V
      test_hafs_raa.py                            # 19
      test_warsh_raa.py                           # 31: 11 fixed + 20V
      test_allah_lam.py                           # 8
      test_warsh_lam_taghliz.py                   # 17: 12 fixed + 5V

    hamza/                                        # 104 cases: 90 fixed + 14V
      __init__.py
      test_wasl_start.py                          # 14
      test_hafs_alism_ibtidaa.py                  # 1V
      test_wasl_silent.py                         # 3
      test_iltiqa.py                              # 15
      test_seats.py                               # 5
      test_ibdal.py                               # 6
      test_tashil.py                              # 2
      test_warsh_naql.py                          # 16: 14 fixed + 2V
      test_warsh_single_hamza.py                  # 15: 13 fixed + 2V
      test_istifham_article.py                    # 3V
      test_warsh_hamza_meetings.py                # 24: 18 fixed + 6V

    nasal/                                        # 57 cases: 55 fixed + 2V
      __init__.py
      test_ghunnah_mushaddadah.py                 # 3
      test_idgham_bi_ghunnah.py                   # 6
      test_idgham_bila_ghunnah.py                 # 4
      test_idgham_shafawi.py                      # 2
      test_ikhfaa.py                              # 13
      test_ikhfaa_shafawi.py                      # 2: 1 fixed + 1V
      test_iqlab.py                               # 6: 5 fixed + 1V
      test_izhar.py                               # 12
      test_izhar_shafawi.py                       # 5
      test_noon_partition.py                      # 4

    vowels/                                       # 149 cases: 137 fixed + 12V
      __init__.py

      inclination/                                # 49 cases: 40 fixed + 9V
        __init__.py
        test_quality.py                           # 6
        test_hafs_inclination.py                  # 2
        test_warsh_inclination.py                 # 20: 11 fixed + 9V
        test_warsh_inclination_classification.py  # 14
        test_warsh_inclination_coloring.py        # 7

      madd/                                       # 65 cases
        __init__.py
        test_tabii.py                             # 3
        test_muttasil.py                          # 2
        test_munfasil.py                          # 5
        test_lazim.py                             # 2
        test_arid.py                              # 5
        test_leen.py                              # 4
        test_iwad.py                              # 4
        test_haa_silah.py                         # 5
        test_warsh_badal.py                       # 13
        test_warsh_leen_mahmuz.py                 # 8
        test_warsh_mim_al_jam.py                  # 7
        test_warsh_yaa_zawaid.py                  # 7

      test_hafs_daaf_vowel.py                     # 1V
      test_pausal_vowels.py                       # 3
      test_final_glides.py                        # 9
      test_hafs_aatani.py                         # 1V
      test_seven_alifs.py                         # 13: 12 fixed + 1V
      test_written_carriers.py                    # 8

    test_muqattaat.py                             # 15: 14 fixed + 1V
    test_hafs_muqattaat.py                        # 1V
    test_qalqala.py                               # 13
    test_sakt.py                                  # 5V
    test_silent_letters.py                        # 13
    test_taa_marbuta.py                           # 5

  adapter/                                        # 99 cases total
    __init__.py
    test_warsh_corpus_alignment.py                # 8
    test_warsh_script_projection.py               # 24
    test_inventory_contract.py                    # 13
    test_inscription.py                           # 12
    test_attestations.py                          # 8
    test_hamza_seats.py                           # 6
    test_roundtrip.py                             # 18
    test_selectors.py                             # 10

  api/                                            # 55 cases total
    __init__.py
    test_phonemizer.py                            # 17
    test_requests.py                              # 20
    test_extra_phonemes.py                        # 8
    test_variants.py                              # 10, final phase only

  conformance/                                    # 116 cases total
    __init__.py
    test_hafs_legacy_parity.py                    # 3
    test_rule_coverage.py                         # 70
    test_hafs_script_agreement.py                  # 21
    test_warsh_registers.py                       # 16
    test_warsh_default_profile.py                 # 6

  document/                                       # 446 cases total
    __init__.py
    test_alignment.py                             # 404 generated samples
    test_source_alignment.py                      # 6
    test_recited_text.py                          # 16
    test_respelling.py                            # 12
    test_labels.py                                # 8

  engine/                                         # 34 cases total
    __init__.py
    test_canon_build.py                           # 8
    test_windowing.py                             # 4
    test_neighbourhood.py                         # 6
    test_rule_plan.py                             # 8
    test_effective_state.py                       # 8

  schema/                                         # 102 cases total
    __init__.py
    test_canonical_roundtrip.py                   # 5
    test_ledger.py                                # 19
    test_lexicon.py                               # 14
    test_negative_cases.py                        # 22
    test_phoneme_inventory.py                     # 18
    test_model_vocabulary.py                      # 24

  support/                                        # 20 harness cases total
    __init__.py
    assertions.py
    boundary.py
    case.py
    reading.py
    selectors.py
    site.py
    test_case_contract.py                         # 20

  data/
    warsh/
      hamza_meetings.json
      inclination.json
      lam.json
      naql.json
      raa.json
      seven_alifs.json
      single_hamza.json
      yaa_zawaid.json

  snapshots/
    head/
    legacy-api/
    phonemes/
    warsh/                                        # added only after fixed conformance
```

The whole final tree has a logical budget of 1,385 cases. That number is not
expected to equal pytest collection because semantic rows expand by state,
riwayah, and script. The important totals for domain review are 436 fixed
phonemization cases, 72 variant phonemization cases, and 508 final cases under
`phonemize/`.

## Why these semantic counts are sufficient

### Articles: 20 cases

The current suite spends 30 rows on one article per row. A corpus set-cover
over one- and two-word spans finds all 14 sun-letter hosts in 9 rows and all
14 moon-letter hosts in 8 rows. These rows also include both an article at the
start of the span and an article reached after a preceding word, so wasl start
and elision are not a second alphabet sweep.

Examples of dense rows are:

- `وَٱلتِّينِ وَٱلزَّيْتُونِ`, 95:1: taa and zay;
- `ٱلنَّجْمُ ٱلثَّاقِبُ`, 86:3: noon and tha;
- `ٱلْوَسْوَاسِ ٱلْخَنَّاسِ`, 114:4: waw and kha; and
- `ٱلْبَلَدِ ٱلْأَمِينِ`, 95:3: baa and hamza.

`test_lam_contrasts.py` keeps three negative/minimal contrasts: true article
lam, lexical lam, and the one-lam written form. The interrogative/article
shape is owned completely by `hamza/test_istifham_article.py`; repeating it
here would add no independent assertion. A dense positive table must not
replace an overreach test.

### Nasal families: 57 cases

The target keeps every trigger letter and every materially different source
representation without testing every trigger against every representation.

For `ikhfaa`, a corpus set-cover proves that 10 one- or two-word rows
cover all 15 followers. The rows deliberately mix a written noon and tanwin
where possible. Two orthogonal rows cover a verse seam and the optional
emphatic nasal token, and one owns the mini-noon form, for 13 total cases.

The 10 trigger rows include:

| Span | Followers covered |
| --- | --- |
| `تِجَارَةٍ تُنجِيكُم` 61:10 | taa, jeem |
| `إِنسٌ قَبْلَهُمْ` 55:74 | seen, qaf |
| `بِقَدَرٍ فَأَنشَرْنَا` 43:11 | fa, sheen |
| `أَندَادًا ذَٰلِكَ` 41:9 | dal, thal |
| `مَعِيشَةً ضَنكًا` 20:124 | dad, kaf |
| `حِينَئِذٍ تَنظُرُونَ` 56:84 | taa, zah |
| `مَيِّتٍ فَأَنزَلْنَا` 7:57 | fa, zay |
| `قِنطَارًا فَلَا` 4:20 | tah, fa |
| `إِن تَنصُرُوا` 47:7 | ta, sad |
| `وَٱلْأُنثَىٰ` 2:178 | tha |

Repeated followers in this set are acceptable when they are the cheapest way
to reach a second uncovered letter. They are not counted as extra coverage.

For the other noon families:

- six throat letters use five dense trigger rows plus one seam row and one
  source-representation row, for 7 `izhar` cases;
- the four `idgham_bi_ghunnah` hosts use four trigger rows plus three rows for
  the missing tanwin quality, muqattaat origin, and verse seam, for 7 cases;
- lam and raa use two trigger rows plus noon/tanwin and state contrasts, for 4
  `idgham_bila_ghunnah` cases;
- iqlab has one host letter, so its six fixed cases cover internal noon,
  cross-word noon, all three tanwin qualities, and a seam without pretending
  these are six trigger rules; and
- the four `izhar_mutlaq` words are a test-owned register inside
  `test_izhar.py`, with three full phoneme cases: one ordinary member, one
  prefixed member, and one contrast. The subcase does not need another file.

Four dedicated pausal-clear cases cover a separate boundary branch that the
trigger alphabets do not prove:

| Surviving base | Dropped ending | Example | Required stopped result |
| --- | --- | --- | --- |
| noon | short haraka | `نَسْتَعِينُ`, 1:5:4 | Audible `/n/` with `izhar` after the damma drops |
| noon | tanwin | `مُبِينٌ`, 37:113:10 | The tanwin noon drops; the lexical `/n/` remains with `izhar` |
| meem | short haraka | `مَرْيَمَ`, 2:87:12 | Audible `/m/` with `izhar_shafawi` after the fatha drops |
| meem | tanwin | `عَلِيمٌ`, 2:29:19 | The tanwin noon drops; the lexical `/m/` remains with `izhar_shafawi` |

The clear-rule occurrence reaches the surviving noon or meem character and
sound. It does not attach to the dropped tanwin mark. The pausal rule still
owns removal of the haraka or tanwin.

Existing cross-word rows in `test_idgham_bi_ghunnah.py`,
`test_idgham_bila_ghunnah.py`, and `test_idgham_shafawi.py` gain a stopped
state. In that state the forward host is invisible, the joined idgham rule is
absent, and the surviving source consonant must recover `izhar` or
`izhar_shafawi`. This is required even when the selected script writes no
sukun on that noon or meem because its ordinary joined reading assimilates.
The corresponding cross-word ikhfaa and iqlab state matrices enforce the same
general stop-recovery law without adding separate logical cases for every
next-letter class.

`test_noon_partition.py` is not another example sweep. Its four generated
cases prove that every relevant next-letter class belongs to exactly one noon
family, every emitted family reaches one source and one result, exceptions are
disjoint, and no plan contains competing noon rules. Its boundary invariant
also proves that a stop blocks every cross-word noon family and gives any
surviving audible noon the clear `izhar` classification.

### Assimilation: 29 cases

Every distinct source/host pair remains covered. Repeated joined and stopped
bodies become state matrices. Complete and incomplete mutajanisayn stay in
separate files because they have different sound and emphasis contracts.

There is no standalone `test_fakk_idgham.py` and no `fakk_idgham` rule. The
tested event is simpler: ibtidaa on word two makes its cross-word merger
unavailable, so the host is pronounced once rather than as the second half of
a geminate. Tests name this state `ibtidaa-on-host`, keep it beside the joined
state, and assert the single host sound plus absence of the merger rule.

The two final variant cases in `test_hafs_idgham_choices.py` own
`irkab_maana` and `yalhath_dhalik`. They are not duplicated in the shared
mutajanisayn file or in an API behavior suite.

### Emphasis: 97 cases

`test_istilaa.py` covers the seven letters once, then separately covers every
dependent A shape: short fatha, fathatan, long alif, and pausal iwad. A heavy
or taghliz source colors its causally dependent A realization; a light source
removes only that cause.

`test_raa.py` owns two shared coloring/reach cases and the six shared lexical
selectors. `test_hafs_raa.py` keeps all 19 distinct Hafs decision branches.
`test_warsh_raa.py` owns the Warsh structural branches and representative
closed-scope shapes required by `raa.md`. Closed lexical positions are
register data, not repeated full-output tests. Its 20 Warsh-only selector rows
are added last.

`test_allah_lam.py` owns only the divine-name forms: heavy standalone forms,
light prefixed forms, and the joined fatha/damma versus kasra condition. An
ordinary light lam needs no dedicated semantic sweep. The Warsh structural
taghliz, selected tarqiq, dependent short/long/fathatan coloring, coupled
inclination sites, and register representatives live in
`test_warsh_lam_taghliz.py`. Its five selector rows are added last.

`test_hafs_seen_sad.py` exists only in the final phase for the four Hafs
seen/saad selectors. Keeping them together is clearer than hiding letter
identity changes inside raa or general vowel tests.

### Hamza: 104 cases

The folder follows implementation ownership rather than source spelling:

- `test_wasl_start.py` covers article A, heard and patterned noun I, verb I/U,
  every temporary-damma family, the Warsh lexical-input contrast, and both
  started silent-root-hamza carrier qualities; the Hafs-only al-ism selector
  has its own final-phase file;
- `test_wasl_silent.py` covers the shared joined-elision classes,
  including exact onset/nucleus reach and lexical-qata contrasts;
- `test_iltiqa.py` covers shared shortening and ordinary A/I repair, then
  compares the Warsh U register and its exclusions directly with Hafs;
- `test_ibdal.py` and `test_tashil.py` prove the generic transformation,
  phoneme inventory, effective madd, extra-token behavior, and exact reach;
- `test_warsh_single_hamza.py` owns the morphology-backed and lexical Warsh
  classifiers;
- `test_istifham_article.py` owns three `VariantCase` rows for the distinct
  lexical forms `ءَآلذَّكَرَيْنِ`, `ءَآلْـَٰٔنَ`, and `ءَآللَّهُ`. Repeated
  occurrences reconcile through the closed register; the forms stay separate
  because article assimilation, internal root-hamza behavior, and Allah-lam
  coloring differ; and
- `test_warsh_hamza_meetings.py` owns one-word and cross-word A/U/I matrices,
  fixed exclusions, and narrow registers.

This split avoids repeating generic ibdal/tashil mechanics in every lexical
classifier test. The classifier file asserts that the correct transformation
was selected; the generic file exhausts how that transformation is rendered
and attributed.

The 16 silent-root-hamza starts, 25 iwaa exclusions, 56 fixed single-hamza
ibdal tokens, 60 one-word meetings, 156 cross-word meetings, and other closed
sets are independent data registers. Only distinct structural branches get
full manual phoneme cases.

### Vowels and madd: 149 cases

`test_pausal_vowels.py`, `test_final_glides.py`, `test_iwad.py`, and
`test_taa_marbuta.py` use state matrices. Joined and stopped outcomes remain
separate executed checks but one reviewed row.

Ordinary A/I/U projection is exercised throughout the semantic suite and
does not need a separate short-vowel file. The Hafs `ضَعْف` selector remains
the explicitly named `test_hafs_daaf_vowel.py`.

The seven alifs keep one row per distinct lexical/orthographic shape. Repeated
members with identical behavior move to the register. The unrelated Aatani
waqf selector is isolated in `test_hafs_aatani.py`.

Pronoun-haa silah is owned by `madd/test_haa_silah.py`, including ordinary
silah, its blockers, waqf masking, and silah kubra before hamza. Warsh mim
al-jam and yaa zawaid retain
separate domain files under `madd/`: most performed branches are conditional
`madd_tabii` or `madd_jaiz_munfasil` in wasl, and their acceptance matrices
are organized by those resulting madd classes. Each file also owns its
non-madd branch, including mim before wasl and the single consonantal
yaa-zawaid site, so the authored family is not fragmented.

The old mixed `test_madd.py` is split by public rule. Each madd file covers
only its structural predicate, boundary masks, exclusions, effective-state
creation where relevant, and exact sound/source reach. Counts are not public
phonemes and do not multiply behavior cases.

Inclination has five owners:

- `test_quality.py`: shared typed fath, taqlil, and kubra sound/render
  mechanics;
- `test_hafs_inclination.py`: the fixed Hafs kubra case;
- `test_warsh_inclination.py`: fixed, default, opening-letter, and selectable
  Warsh outcomes;
- `test_warsh_inclination_classification.py`: generated predicate/register
  completeness and overlap rejection; and
- `test_warsh_inclination_coloring.py`: raa/lam dependency and carrier
  masking.

### Focused root files: 51 cases

`test_muqattaat.py` has one fixed/default case for each of the fourteen unique
forms: `الم`, `المص`, `الر`, `المر`, `كهيعص`, `طه`, `طسم`, `طس`, `يس`, `ص`,
`حم`, `حم عسق`, `ق`, and `ن`. Every case asserts both the complete phoneme
sequence and every applicable rule on its exact source and sound: letter-name
madd, nasal behavior, qalqala, emphasis, inclination, and boundary behavior.
Riwayah picks keep the same form adjacent when the fixed/default output
differs. The shared `noon_wasl` selector is the fifteenth case;
`test_hafs_muqattaat.py` contains only the Hafs `yaseen_wasl` selector. Warsh
opening inclination selectors remain in the inclination owner and are
integrated into the default muqattaat rows without duplicating their variant
matrix.

Qalqala keeps every letter and materially distinct degree/state but removes
repeated bodies. Silent written letters remain one focused semantic file while
their low-level source recognition lives in adapter tests.

Tamanna is not placed under nasal and receives no new phonemization behavior
test. Its public metadata remains covered by the generated API contract. One
`test_sakt.py` owns the shared Maliyah selector and the four Hafs-only lexical
sakt choices. All five rows assert sakt versus idraj phonemes, the precise
downstream rule blocked or restored, and the explicit-waqf mask. Sakt is the
common phenomenon, so splitting the Hafs sites into another file would make
review harder without clarifying ownership.

## Compact semantic case style

### One dense case, two independently checked occurrences

The example below covers tanwin-before-taa and written-noon-before-jeem in one
review row. The harness still reports them separately.

```python
# تِجَـٰرَةٍ تُنجِيكُم
pytest.param(
    Case(
        site=Site(hafs=("61:10", (7, 8))),
        read=through(),
        phonemes=(
            "t i ʒ a: rˤ aˤ t i ŋ",
            "t u ŋ ʒ i: k u m",
        ),
        char_rules={
            "@kasratan": R("ikhfaa"),
            "ن": R("ikhfaa"),
        },
        sound_rules={
            "ŋ[1]": R("ikhfaa"),
            "ŋ[2]": R("ikhfaa"),
        },
    ),
    id="ta-jeem",
)
```

`[1]` and `[2]` are required here because the full focused span has two `ŋ`
tokens. A one-word case with one noon and one nasal uses plain `"ن"` and
`"ŋ"`; adding `[1]` there is rejected as noise.

### One state matrix, not repeated test bodies

```python
# إِثْمًا
StateCase(
    site=Site(hafs=("4:48", (19,))),
    states={
        "joined": Expect(
            read=joining(),
            phonemes="ʔ i θ m a n",
        ),
        "stopped": Expect(
            read=isolated(),
            phonemes="ʔ i θ m a:",
            char_rules={"@fathatan": R("iwad")},
            sound_rules={"a:": R("iwad")},
        ),
    },
)
```

The exact production site may change during authoring if another word gives a
cleaner span. The shape is the contract: one domain row, two independently
reported states.

## Harness contract

### `Case`, `StateCase`, and `VariantCase`

`Case` owns one state. `StateCase` owns a common site and several named state
expectations. `VariantCase`, introduced only in the final phase, owns one
public selector and includes:

- every legal value;
- the project default;
- active and masked boundary states;
- exact sound and source reach; and
- exclusions or same-ID riwayah differences where applicable.

The common assertion engine handles all three. Regular semantic files should
have one or two parametrized test functions; reviewers inspect tables, not
dozens of mechanical bodies.

### Sites and riwayat

Use canonical/public coordinates in semantic cases.

```python
Site.shared("2:42", (7,), riwayat=("hafs", "warsh"))
```

Use per-riwayah site values only when canonical coordinates or focused spans
actually differ. Selected-source coordinates and exact source text belong in
adapter fixtures.

Plain expected values apply to all declared riwayat. `pick()` is limited to a
small output detail under the same domain law. Different applicability, rule
identity, state behavior, or explanation requires separate rows.

### Boundary plans

Keep `BoundaryPlan` and `Junction` as the underlying model. The semantic
shorthands are:

- `isolated()`: start and stop on the one focused word;
- `joining()`: start on the focused word and continue to its required
  neighbour;
- `through()`: start on the first word and stop on the last word of a
  multiword site; and
- an explicit plan only for a non-default interior stop, start, sakt, or
  cross-ayah seam.

An interior explicit stop followed by another included word makes that next
word an ibtidaa. It does not make the word unperformed. Sakt is continuation,
not waqf.

### Phoneme strings

Every expected sequence is parsed as inventory tokens separated by exactly
one ASCII space. Leading whitespace, trailing whitespace, double spaces,
concatenated tokens, and unknown tokens fail collection.

Atomic tokens include:

- geminates such as `jj`, `ñ`, `m̃`, and `lˤlˤ`;
- long vowels such as `a:` and `ɛ:`; and
- qalqala release `Q`, which remains separate from its consonant: `q Q`.

The comparison target is `Reading.sounds()`. No semantic test compares an
unparsed concatenated string.

### Exact source and sound selectors

All selectors remain strings.

- A plain string is a visible grapheme cluster or exact sound token.
- An `@name` is a registered semantic source selector.
- A `named-letter/cell` string selects one transformed cell inside a fully
  spelled muqattaat run. The run and literal cell are matched without Arabic
  combining marks; `@fatha`, `@damma`, `@kasra`, and `@madd` select cell roles.
- An `@inserted/cell` string selects an inserted transformed cell that has no
  source glyph, such as the iwad alif created after final hamza.
- A one-based `[n]` suffix is allowed only when the unsuffixed target is
  ambiguous inside the focused span.

For example, `لام/@madd` names the alif carrier in the spelled name of lam,
`ميم/م[2]` names the terminal meem rather than the compact source glyph, and
`@inserted/ا` names a created iwad carrier rather than the source tanwin.

The initial registry is:

| Selector | Typed meaning |
| --- | --- |
| `@fatha`, `@damma`, `@kasra`, `@sukun`, `@shadda` | ordinary haraka or shadda role |
| `@fathatan`, `@dammatan`, `@kasratan` | canonical tanwin quality, independent of source glyph form |
| `@dagger_alif`, `@madd_sign` | the corresponding inscription role/fact |
| `@hamza_mark` | a combining hamza source when the script does not use a full seated letter |
| `@small_noon`, `@small_waw`, `@small_yaa` | a mini-letter role supplying or attesting the named canonical fact |
| `@mini_meem` | the reviewed Warsh iqlab hint inside a noon/tanwin composition |
| `@round_zero`, `@rectangular_zero` | the reviewed alif-silence/pausal convention |
| `@imala_mark`, `@tashil_mark`, `@ishmam_mark` | vowel-quality or annotation evidence, not the rule trigger |
| `@sakt_mark`, `@stop_mark` | structural boundary evidence in adapter tests |

The registry is typed over inscription relations and canonical facts. It is
not a global Unicode alias table. For example, U+06EA cannot globally mean
imala because the selected Warsh source uses it in several sequence roles.

An adapter test proves every registered selector for every supported script.
An unknown selector fails collection. Raw subtle combining marks are rejected
as semantic mapping keys.

### Rule reach

Use two compact maps:

```python
char_rules={"ن": R("ikhfaa")}
sound_rules={"ŋ": R("ikhfaa", "tafkheem")}
```

When the same rule appears in both maps, the assertion must find one rule
occurrence connecting those exact targets. Matching two unrelated occurrences
with the same ID does not pass.

For recoloring rules, target every causally owned A realization: short fatha,
fathatan, long alif, and iwad. Lightening removes only that owner's cause; it
must not remove emphasis independently supplied elsewhere.

`iltiqa_haraka` reaches only the inserted A/I/U sound. The source consonant or
nunation slot and any written linking mark own character reach, but the base
consonant sound is not classified by `iltiqa_haraka`.

## Mechanical enforcement

`tests/support/test_case_contract.py` and a fast-gate style check enforce:

1. exactly one ASCII space between known phoneme tokens;
2. one-word string versus multiword tuple shape;
3. site/span and boundary-plan consistency;
4. unique literal, registered selector, and sound resolution;
5. `[n]` only when the unsuffixed target is ambiguous;
6. connected char/sound reach for a shared rule ID;
7. both participating cells for every merger assertion, including expanded
   muqattaat source and host cells;
8. literal ordinary alif, waw, yaa, and wasl alif rather than semantic aliases;
9. a readable `pytest.param` ID and immediately adjacent Arabic comment;
10. no raw subtle combining-mark mapping keys;
11. no duplicate semantic fingerprint across files;
12. a test-owned closed register rather than importing runtime authored data;
13. one declared owner for every public rule under each riwayah RuleSet; and
14. use of the shared table assertion for regular semantic cases.

Failure output includes the selector, resolved codepoints, source word,
highlighted target, sound index, rule occurrence, riwayah, script, and state.

## Coverage authoring method

Every semantic refactor follows this sequence:

1. List the domain partitions from v2 or the established Hafs source.
2. Map every current test to a partition, representation, state, reach
   invariant, exclusion, or duplicate.
3. Search the corpus for one- and two-word candidates containing several
   uncovered occurrences of the same rule.
4. Run a greedy set-cover only to suggest compact candidates.
5. Manually verify Arabic, domain classification, complete phonemes, and rule
   reach from the normative docs and source.
6. Add orthogonal cases for representation, boundary, extras, and exclusions
   not already covered by the trigger sweep.
7. Record removed current tests in a deletion ledger with the surviving case
   that owns their distinct assertion.
8. Add a generated register/conformance check where the domain is finite.

Current engine output may locate candidates and expose ordinary shared rules.
It is not the oracle for Warsh expectations. A dense example is rejected if
its shown span contains an unresolved or unimplemented Warsh-specific
phenomenon.

The corpus query used to choose cases must be retained as a deterministic
tool or documented command. The chosen case table is hand-authored and stable;
tests do not run an optimizer during collection.

## Adapter-first Warsh baseline

The first Warsh PR adds corpus alignment and script projection before a new
Warsh tajweed classifier. It should then extend vetted shared semantic cases.

Good early shared cases include:

- ordinary letters and harakat;
- qalqala away from a Warsh-specific boundary;
- noon, tanwin, and meem families away from naql or mim al-jam;
- ordinary consonant assimilation and article lam;
- safe pausal vowels, iwad, taa marbuta, and final glides;
- safe structural madd; and
- verified ordinary wasl starts/elisions.

A failure in one of these independently reviewed shared cases is strong
evidence of adapter projection, canonical construction, hidden Hafs coupling,
or a genuinely missing shared rule. It is not permission to copy the current
wrong output into the expectation.

The adapter PR must not add Warsh snapshots. It proves that the source can be
projected and that already shared rules come for free where their canonical
inputs agree.

## PR sequence

1. **Mechanical move.** Move and rename files only. Preserve every unique
   assertion and every Hafs snapshot byte-for-byte.
2. **Harness.** Add `Case`, `StateCase`, exact selectors, spaced phonemes,
   package-aware riwayah iteration, and style lint without changing behavior.
3. **Semantic compaction.** Apply the coverage method folder by folder. Every
   deletion must have a coverage-ledger entry. Reach the 436 fixed/default
   case budget with equal or stronger coverage.
4. **Warsh adapter.** Add source/public alignment, script projection,
   selector fixtures, smoke construction, and vetted shared semantic rows.
5. **RuleSet foundation.** Add global rule vocabulary, riwayah-bound
   classifiers, complete `emits` declarations, typed taqlil/taghliz, and
   effective-state madd support with schema/engine/API tests.
6. **Wasl and iltiqa.** Implement `wasl-hamza.md` and `iltiqa.md` with their
   owning adapter and phonemization files.
7. **Naql.** Implement `naql.md`, including A/I/U transfer, tanwin, article
   starts, qata restoration, and the exact register.
8. **Single hamza.** Implement `single-hamza.md` plus generic ibdal/tashil
   mechanics and reach.
9. **Hamza meetings.** Implement `hamza-meetings.md` and its one-word,
   cross-word, exception, and boundary matrices.
10. **Joined-only vowels.** Implement mim al-jam and yaa zawaid after the
    neutral joined-only model exists.
11. **Seven alifs and madd.** Implement the fixed matrices, badal, and leen
    mahmuz with effective-structure classification.
12. **Inclination.** Implement quality, classification, opening, and coupled
    coloring files.
13. **Raa.** Implement structural branches and independent closed registers.
14. **Lam/taghliz.** Implement taghliz, tarqiq, dependent A coloring, and
    independent closed registers.
15. **Default conformance.** Prove rule reachability, conflict freedom,
    register reconciliation, cross-script agreement, and only then add Warsh
    default-profile snapshots.
16. **Variants last.** Add the 72 semantic `VariantCase` rows and the small
    generic API contract covering all 71 selectors. Do not recreate a
    cross-domain khilaf behavior file.

## Acceptance criteria

### Mechanical reorganization

- every current test has a recorded destination;
- no `adjacent/`, `boundary/`, `waqf/`, `tafkheem/`, `laws/`, root catch-all,
  or giant `test_khilaf.py` remains;
- collection succeeds after the move;
- the fast gate is green; and
- all existing Hafs snapshot files remain unchanged.

### Harness and style

- every semantic expected sequence is inventory-tokenized with ASCII spaces;
- ordinary alif, waw, yaa, and wasl alif use literal script forms rather than
  semantic source aliases;
- unique targets never carry an occurrence suffix;
- subtle marks use the reviewed selector registry;
- repeated glyphs/sounds are addressed exactly, never unioned accidentally;
- every merger assertion names both participating cells; muqattaat mergers
  name their expanded source and host cells;
- state matrices replace repeated joined/stopped bodies;
- case tables contain Arabic, site, state, full phonemes, char reach, sound
  reach, and readable IDs together; and
- the fast gate rejects every style or targeting violation described above.

### Coverage and compaction

- every distinct current law, trigger partition, source representation,
  boundary state, exclusion, and public reach invariant survives in the
  coverage ledger;
- all 14 sun letters, 14 moon letters, 15 ikhfa letters, six throat letters,
  four ghunnah-idgham hosts, two no-ghunnah hosts, seven istilaa letters, five
  qalqala letters, seven alifs, and every distinct raa/lam branch remain
  exhaustive;
- final noon and meem recover clear classification after pausal haraka or
  tanwin removal, and an explicit stop recovers it when a cross-word idgham,
  ikhfaa, or iqlab is masked;
- every one of the fourteen unique muqattaat forms has a complete phoneme and
  exact rule-reach expectation, not a phoneme-only smoke row;
- the three istifham-article forms each receive a semantic selector row;
- no trigger alphabet is needlessly crossed with every representation;
- no large closed register becomes a full-output test per member;
- no duplicate semantic fingerprint remains; and
- each target file stays within its planned case budget unless its coverage
  matrix documents why another case is necessary.

### Warsh fixed/default implementation

- every v2 phenomenon has one obvious owning test file and implementation PR;
- semantic sites use canonical/public coordinates;
- adapter fixtures preserve selected-source coordinates and source text;
- every manual token belongs to the reviewed phoneme inventory;
- every named rule reaches the exact required sound and source material;
- closed registers are independent of production authored data;
- shared rules use shared cases rather than duplicated riwayah files;
- all fixed/default semantic and conformance gates pass before snapshots; and
- Warsh snapshots are added only for the complete default profile.

### Variants

- variants are the final phase;
- all 71 selectors have exactly one semantic owner, with 72 behavior rows
  because the three distinct istifham-article forms share one selector;
- `tamanna_noon` has catalogue/default validation only, by explicit decision;
- every legal value, default, active state, masked state, register, exclusion,
  and same-ID riwayah difference is tested;
- arbitrary explicit combinations remain accepted without a tariq validator;
- generic catalogue validation stays in `api/test_variants.py`; and
- no variant's sound behavior is duplicated in the API file.

## Validation commands

Use these at each relevant stage:

```text
python -m pytest --collect-only -q
python tools/gates.py --fast
git diff --exit-code -- tests/snapshots
```

Run the full gate before handing off adapter, runtime, corpus, schema,
snapshot, or broad test changes:

```text
python tools/gates.py
```
