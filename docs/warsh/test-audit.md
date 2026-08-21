# Current test-suite audit

This is the read-only checkpoint for the test reorganization. It accounts for
the current suite before any test file is moved or rewritten.

The executable target tree, case budgets, harness contract, coverage method,
PR sequence, and acceptance criteria are in
[`test-refactor-plan.md`](test-refactor-plan.md).
The shared versus riwayah-prefixed placement audit is in
[`warsh-test-placement.md`](warsh-test-placement.md).

## Recommendation

Put every hand-authored recitation behavior test under one root:

```text
tests/
  phonemize/
    articles/
    assimilation/
    emphasis/
    hamza/
    nasal/
    vowels/
      inclination/
      madd/
    test_muqattaat.py
    test_qalqala.py
    test_sakt.py
    test_silent_letters.py
    test_taa_marbuta.py
  adapter/
  api/
  conformance/
  document/
  engine/
  schema/
  support/
  snapshots/
```

The boundary is based on the question a test answers:

- `phonemize/`: what is recited, which named rule applies, and which exact
  source character and performed sound it reaches;
- `adapter/`: how selected-script text becomes canonical reading facts and
  inscription relations;
- `api/`: requests, results, options, catalogues, and public defaults;
- `document/`: assembly, alignment, recited spelling, labels, and respelling;
- `engine/`: generic build, planning, neighbourhood, conflict, and windowing
  invariants;
- `schema/`: closed model and serialized/data-loader contracts;
- `conformance/`: corpus-wide coverage, cross-script agreement, parity, and
  snapshots.

This avoids two bad outcomes: mixing adapter/API/snapshot tests with tajweed
examples, and duplicating the semantic tree under `hafs/` and `warsh/`.

The `phonemize/` folders name sound domains, not runtime circumstances:

- `articles/` owns the pronounced or assimilated definite-article lam;
- `assimilation/` owns consonant-to-consonant idgham and its release at a
  reading start;
- `emphasis/` owns tafkheem, tarqiq, and lam taghliz, including dependent A
  coloring;
- `hamza/` owns wasl, iltiqa, ibdal, tashil, naql, seats, and hamza meetings;
- `nasal/` owns noon, tanwin, meem, and ghunnah behavior;
- `vowels/` owns vowel quality, length, inserted or removed vowels, joined-only
  vowels, final-glide vocalization, and the seven alifs.
- `vowels/inclination/` owns fath, taqlil, and imala kubra realization,
  classification, coupled coloring, and the relevant fixed or selected sites.

`test_silent_letters.py` stays at the semantic root because written-but-unsaid
letters form one focused behavior, not a growing hierarchy. Their low-level
source recognition still belongs in `adapter/`.

Waqf, wasl, and ibtidaa remain explicit states inside those files. They do not
own folders. A boundary can alter a hamza, vowel, consonant, or assimilation;
grouping those unrelated outputs under `boundary/` or `waqf/` obscures the
actual implementation owner. Likewise, `adjacent` merely describes where a
trigger sits, and `rasm` describes written evidence rather than the resulting
sound.

### Rule and behavior ownership

The current rule vocabulary and the reviewed Warsh additions fit the tree
without a boundary or waqf bucket:

| Owner | Rules and behaviors |
| --- | --- |
| `articles/` | `lam_shamsiyyah`, `lam_qamariyyah`, and article/non-article contrasts |
| `assimilation/` | `idgham_mutamathilayn`, `idgham_mutaqaribayn`, both `idgham_mutajanisayn` forms, and `fakk_idgham` |
| `emphasis/` | `tafkheem`, `tarqeeq`, `taghliz`, raa weight, lam weight, and dependent A coloring including fathatan and iwad |
| `hamza/` | `wasl_start`, `wasl_elision`, `iltiqa_haraka`, `iltiqa_shortening`, `ibdal_hamza`, `tashil`, `naql`, hamza seats, and hamza meetings |
| `nasal/` | `izhar`, `ikhfaa_haqiqi`, `iqlab`, noon idgham, the three shafawi rules, and `ghunnah_mushaddadah` |
| `vowels/` | `iwad`, `pausal_sukun`, `pausal_alif`, ordinary vowel quality, final glides, joined-only vowels, and seven alifs |
| `vowels/inclination/` | `imala`, `taqlil`, their exact vowel quality, coupled consonant coloring, and site classification |
| `vowels/madd/` | every structural madd class, `madd_badal`, and `madd_leen_mahmuz` |
| root focused files | qalqala, muqattaat, sakt, silent written letters, Tamanna ishmam, and `taa_marbuta_pausal` |

The state that activates a rule is covered in the owning test. For example,
`pausal_sukun` lives with vowels because it removes the final vowel; a stopped
raa exception lives with emphasis because the changed result is raa weight;
and a stopped hamza face lives with hamza. This keeps all boundaries visible
without making boundary state the top-level taxonomy.

Iltiqa is the deliberate exception to a purely result-shaped placement. Its
repair haraka and shortening affect the preceding word, but every modeled
trigger is the elision of a following hamzat al-wasl. Keeping
`hamza/test_iltiqa.py` beside the wasl start/elision files gives a verifier one
complete wasl boundary family and matches the implementation dependency. The
asserted `iltiqa_haraka` occurrence still reaches only the inserted vowel; the
host consonant or nunation slot is source ownership, not a classified
consonant sound.

## Baseline

- 67 Python test files contain 491 top-level test functions.
- Parameterization expands them to 1,340 collected cases.
- The fast gate currently reports 1,336 passed and 4 skipped.
- There are 80 Python files under `tests/` after helpers and package markers
  are included, plus 2 Markdown files.
- No current test is marked `engine_bug`; that marker appears only in the
  README.

Commands used for the checkpoint:

```text
python -m pytest --collect-only -q
python tools/gates.py --fast
```

The same commands must give 1,340 collected and 1,336 passed / 4 skipped after
the mechanical move. `git diff --exit-code -- tests/snapshots` must also stay
clean.

## Domain-review and test-style audit

### Verdict

The semantic tests are not uniformly chaotic, but they do not yet give a
domain verifier one predictable review path. The best files already use a
compact case table with Arabic beside each row, complete phoneme expectations,
and a small mechanical parametrized test. Other files spread the site at the
top, the Arabic inside a distant function, and the expected rule ownership
across several assertions. A reviewer then has to read every test body even
when nineteen bodies differ only in data.

The existing README convention is directionally right:

- show the full Arabic span beside every semantic case;
- assert the complete phoneme result for the shown span;
- assert the rule on its responsible source character and resulting sound;
- include the neighbour whenever the result depends on it; and
- keep distinct boundary states explicit.

It is followed strongly in files such as `test_rasm.py`, `test_iwad.py`, and
`test_raa.py`, and in the row comments of the large article and nasal tables.
It is not consistent across the suite: some parameter tables omit readable
case IDs, some tests have no Arabic beside the case, `test_madd.py` mixes
comments and test docstrings despite the README rule, and several files assert
only a phoneme or character rule where exact sound reach is part of the public
contract.

The current helpers also make a visually precise assertion less precise than
it looks. `rules_on_char(word, char)` unions every repeated matching character
in the word, `rules_on_sound(word, token)` unions every repeated matching
token, and `source_of()` / `host_of()` select the first occurrence in the
reading. Those helpers must be replaced by exact occurrence targeting before
the Warsh lexical and repeated-letter cases are considered authoritative.

### Required semantic-file shape

A regular rule file should be reviewable from its data section. Use small
tables grouped by domain branch, normally:

1. positive trigger cases;
2. boundary/state cases;
3. exclusions or minimal contrasts; and
4. a closed occurrence register when the domain defines one.

Each semantic row should expose, together in one place:

- canonical `Site` and boundary plan;
- the complete Arabic text as an adjacent comment;
- the complete expected phoneme sequence for the shown span;
- expected rules on the responsible source glyph/unit;
- expected rules on the resulting sound;
- any expected silent source material; and
- a readable pytest case ID based on the word or rule branch, not only a
  coordinate.

The common case must stay compact. The declared `Site` is the focused span,
so a one-word expectation is a string rather than a map repeating its word
number. A literal glyph or sound token selects the unique match inside that
span. Only an actually ambiguous case adds a one-based `[n]` suffix, such as
`"ن[2]"` or `"ŋ[2]"`. The harness must reject both an unresolved ambiguous
literal and a needless occurrence suffix.

Every phoneme expectation is a space-separated token string and is compared
to `Reading.sounds()`, not to an unparsed concatenation. A one-token result is
the only valid expectation without a space. Geminates such as `jj`, `ñ`, and
`lˤlˤ`, long vowels such as `a:`, and a qalqala release `Q` are each atomic
inventory tokens; a release remains separate from its consonant, for example
`q Q`.

Use two rule maps rather than a verbose reach object:

```python
# وَأَنتُمْ
pytest.param(
    Case(
        site=Site(hafs=("2:42", (7,))),
        read=isolated(),
        phonemes="w a ʔ a ŋ t u m",
        char_rules={"ن": R("ikhfaa_haqiqi")},
        sound_rules={"ŋ": R("ikhfaa_haqiqi")},
    ),
    id="taa",
)
```

Where the same rule is named in both maps, `assert_case` must prove that one
rule occurrence connects the resolved source and sound; two unrelated
occurrences with the same rule ID do not satisfy the case. Multiple rules stay
on the same sound line:

```python
sound_rules={"ŋ": R("ikhfaa_haqiqi", "tafkheem")}
```

For a multiword `Site`, `phonemes` is a tuple in declared word order and
`through()` defaults to starting on the first declared word and stopping on
the last. `joining()` and `isolated()` likewise infer their word from a
one-word site. Absolute word numbers belong in `Site`, not throughout the
expected result.

One or two parametrized test functions should apply those rows mechanically.
A domain verifier should audit the tables and read the assertion machinery
once. Keep a named test body only when it proves a genuinely different law
that cannot be expressed clearly as another row.

Full phoneme strings remain valuable: they reveal ordinary qalqala, nasal
assimilation, emphasis, gemination, and downstream boundary behavior that a
local token assertion can miss. Keep the shown span as short as the rule
allows, however. Do not append unrelated words merely to make the example
look realistic, and do not use a partial word string that hides an unresolved
ordinary rule.

### Cross-riwayah cases

Use `Site.shared` when canonical/public coordinates and the focused word span
are the same, without repeating the address:

```python
site=Site.shared("2:42", (7,), riwayat=("hafs", "warsh"))
```

Use `Site(hafs=..., warsh=...)` only when a canonical coordinate or focused
span genuinely differs. Selected-source coordinates and exact script text
remain adapter provenance, not semantic `Site` data.

A plain expectation applies to every declared riwayah. If the same domain
case differs only in output detail, use `pick` at that field:

```python
site=Site(hafs=("1:4", (1,)), warsh=("1:3", (1,)))
phonemes=pick(hafs="m a: l i k", warsh="m a l i k")
```

`char_rules` and `sound_rules` may likewise use `pick` when only their target
token or rule set differs inside the same domain case.

If applicability, rule identity, boundary behavior, or the domain explanation
differs, use separate Hafs and Warsh rows rather than hiding two laws inside
one `pick`. When selected Arabic differs materially, put one adjacent Arabic
comment per riwayah above the shared row.

### Visually subtle source marks

Keep all map keys as strings, but reserve an `@name` namespace for registered
semantic source selectors. A key without `@` is a literal visible grapheme
cluster; a key with `@` is resolved through the test selector registry. Initial
registered names include `@dammatan`, `@fathatan`, `@kasratan`,
`@dagger_alif`, `@small_noon`, `@small_yaa`, and `@small_waw`. The Arabic
comment still shows the complete selected text naturally:

```python
# حَيَّةٌ تَسْعَىٰ
char_rules={"@dammatan": R("ikhfaa_haqiqi")}
```

The registry belongs in `tests/support/selectors.py`. Each entry is a typed
predicate over inscription facts/roles, not an unreviewed global codepoint
alias, and adapter tests prove its resolution in every supported script. An
unknown `@name` fails collection. A registered selector may also use `[n]`
only when more than one match exists. Semantic-test failures print the
selector name, resolved codepoints, source word, and a bracketed or
caret-marked target so a reviewer never has to distinguish two invisible
marks inside quotes.

### Mechanical enforcement

Add a typed `Case` / `StateCase` harness and a test-style lint integrated into
`tools/gates.py`:

- construction validates one-word string versus multiword tuple shape and
  aligns it to the `Site` span;
- every phoneme string must use exactly one ASCII space between known inventory
  tokens, with no leading or trailing whitespace;
- `isolated()`, `joining()`, and `through()` derive their ordinary words from
  the span and reject contradictory boundary intent;
- literal and registered glyph selectors and sound tokens must resolve exactly
  once inside the focused span;
- a `[n]` occurrence suffix is accepted only when the unqualified target is
  ambiguous;
- the shared-rule maps must resolve to the same rule occurrence and exact
  source-to-sound reach;
- every `pytest.param` case needs a readable `id` and an immediately adjacent
  Arabic comment;
- raw subtle combining-mark keys are rejected in favor of registered `@name`
  selectors, and unknown selector names are rejected;
- duplicate case fingerprints with the same site, boundary, and asserted
  contract are reported across semantic files; and
- regular case-table tests use the shared assertion function. A genuinely
  custom law may use a named test body, but must not reproduce a table case.

These checks make concise syntax the easiest valid syntax. Review comments no
longer carry the burden of policing word-number repetition or ambiguous
occurrence selection.

### Redundancy and justified coverage

Many collected cases are justified, but several current suites cross two
independent dimensions without gaining another implementation partition.
After the behavior-preserving move, consolidate them as follows:

- Keep exhaustive finite trigger partitions once: all article moon/sun
  letters, every distinct raa/lam decision branch, each taa-marbuta shape,
  the seven alifs, and every reviewed closed Warsh exception set.
- Do not cross every nasal trigger letter with both a written noon and tanwin.
  Current ikhfa has 30 trigger rows for 15 followers, izhar has 18 trigger rows
  for six throat letters, and idgham-bi-ghunnah has 16 rows around four hosts
  before its representation checks. Sweep the trigger alphabet once, then use
  a small orthogonal representation set for internal noon, cross-word noon,
  all three tanwin marks, verse seams, and any heavy-nasal coloring.
- Fold paired joined/stopped bodies in `test_iwad.py`, `test_final_glides.py`,
  and `test_silah.py` into one row containing both state outcomes. The states
  still execute separately; the reviewer no longer rereads duplicated setup.
- Convert the nineteen distinct raa conditions to tables, but do not delete
  them: they are separate rule branches rather than duplicate examples.
- Split `test_madd.py` by madd class. Keep one positive per structural branch
  and only the negative contrasts that prevent a plausible overmatch.
- Dissolve the semantic parts of `laws/test_minimal_pairs.py`,
  `test_attestation_law.py`, `test_boundary_split.py`, `test_madd_tabii.py`, and
  `test_seven_alifs.py` into their owners. Preserve only genuinely different
  adapter, graph, or attribution invariants; do not rerun the same recitation
  merely under a second organizational label.
- For a large corpus register, test the full positive/exclusion set as data
  and use a few representatives for full phonemes and rule reach. Do not turn
  every coordinate into an identical end-to-end reading test.

The target is not the fewest tests. It is one test per meaningful partition:
trigger class, canonical/source representation, boundary state, rule-reach
shape, or authenticated exception. Extra examples with none of those changes
increase review cost without increasing confidence.

### Tamanna

Tamanna ishmam is not part of the generic nasal family. Keep one focused
`phonemize/test_tamanna.py` regression because it has a distinct public sound
and rule occurrence and later gains selectable behavior. Do not build a
generic ishmam or nasal matrix around it. At the variants-last stage, extend
that same file with the alternate face instead of duplicating the default in
an API test.

## Existing semantic suites

The collected count includes parameterized cases, so every currently
collected case is accounted for by its file row.

| Current file | Cases | Responsibility and strength | Proposed destination |
| --- | ---: | --- | --- |
| `adjacent/test_lam_qamariyyah.py` | 15 | Strong black-box moon-letter coverage, boundary, phonemes and rule reach. | `phonemize/articles/test_lam_qamariyyah.py` |
| `adjacent/test_lam_shamsiyyah.py` | 15 | Strong sun-letter coverage; includes one-lam rasm and joined elision. | `phonemize/articles/test_lam_shamsiyyah.py` |
| `adjacent/test_lam_that_is_not_the_article.py` | 3 | Minimal contrasts for article lam, form-VIII lam, and interrogative article. | `phonemize/articles/test_lam_contrasts.py` |
| `adjacent/test_mutajanisayn_kamil.py` | 11 | Strong complete-merger coverage, stop reversal, ghunnah, source and host. | `phonemize/assimilation/test_mutajanisayn_kamil.py` |
| `adjacent/test_mutajanisayn_naqis.py` | 4 | Focused incomplete-merger sound and retained emphasis. | `phonemize/assimilation/test_mutajanisayn_naqis.py` |
| `adjacent/test_mutamathilayn.py` | 12 | Cross-word and internal mergers, stop reversal, qalqala suppression. | `phonemize/assimilation/test_mutamathilayn.py` |
| `adjacent/test_mutaqaribayn.py` | 4 | Lam-to-raa, qaf-to-kaf, and stop reversal. | `phonemize/assimilation/test_mutaqaribayn.py` |
| `boundary/test_hamza_wasl_elision.py` | 14 | Article, verb, noun, and divine-name elision with sound and source reach. | `phonemize/hamza/test_wasl_elision.py` |
| `boundary/test_hamza_wasl_start.py` | 18 | A/I/U start vowel classes and lexical contrasts. | `phonemize/hamza/test_wasl_start.py` |
| `boundary/test_ibdal_hamza.py` | 6 | Started silent-root-hamza replacement and joined countercases. | `phonemize/hamza/test_ibdal.py` |
| `boundary/test_iltiqa_shortening.py` | 21 | Madd shortening, consonant repair, tanwin repair, and negative cases caused by joined wasl hamza. | `phonemize/hamza/test_iltiqa.py` |
| `nasal/test_ghunnah_mushaddadah.py` | 3 | Doubled noon/meem and a non-doubled contrast. | `phonemize/nasal/test_ghunnah_mushaddadah.py` |
| `nasal/test_idgham_bi_ghunnah.py` | 21 | Noon/tanwin, every host, letter-name and verse-seam coverage. | `phonemize/nasal/test_idgham_bi_ghunnah.py` |
| `nasal/test_idgham_bila_ghunnah.py` | 6 | Lam/raa hosts, noon/tanwin, stop and verse-seam coverage. | `phonemize/nasal/test_idgham_bila_ghunnah.py` |
| `nasal/test_idgham_shafawi.py` | 3 | Meem merger, stop reversal, and verse seam. | `phonemize/nasal/test_idgham_shafawi.py` |
| `nasal/test_ikhfaa_haqiqi.py` | 36 | Exhaustive follower letters, noon/tanwin, seam, ownership, optional token. | `phonemize/nasal/test_ikhfaa_haqiqi.py` |
| `nasal/test_ikhfaa_shafawi.py` | 2 | Meem-before-baa and stop reversal. | `phonemize/nasal/test_ikhfaa_shafawi.py` |
| `nasal/test_iqlab.py` | 13 | Noon/tanwin, internal/cross-word/seam and character ownership. | `phonemize/nasal/test_iqlab.py` |
| `nasal/test_izhar.py` | 22 | Exhaustive throat letters, noon/tanwin and verse seam. | `phonemize/nasal/test_izhar.py` |
| `nasal/test_izhar_mutlaq.py` | 4 | Closed four-word exception family. | `phonemize/nasal/test_izhar_mutlaq.py` |
| `nasal/test_izhar_shafawi.py` | 3 | Internal and cross-word clear meem. | `phonemize/nasal/test_izhar_shafawi.py` |
| `tafkheem/test_istilaa.py` | 19 | Heavy-letter inventory, light contrasts, dependent A coloring, extras. | `phonemize/emphasis/test_istilaa.py` |
| `tafkheem/test_lam.py` | 17 | Divine-name lam contexts and ordinary-lam contrasts. | `phonemize/emphasis/test_lam.py` |
| `tafkheem/test_raa.py` | 19 | Systematic Hafs raa conditions in moving, sakin, stopped, and doubled forms. | `phonemize/emphasis/test_raa.py` |
| `waqf/test_final_glides.py` | 22 | Joined consonantal glides versus stopped long vowels. | `phonemize/vowels/test_final_glides.py` |
| `waqf/test_iwad.py` | 8 | Every tanwin quality in joined and stopped states. | `phonemize/vowels/madd/test_iwad.py` |
| `waqf/test_pausal_sukun.py` | 6 | A/U/I final vowels in joined and stopped states. | `phonemize/vowels/test_pausal_vowels.py` |
| `waqf/test_seven_alifs.py` | 18 | Seven pausal alifs plus round-zero and Salasila behavior. | `phonemize/vowels/test_seven_alifs.py`; absorb the canonical-shape tests below. |
| `waqf/test_silah.py` | 12 | Pronoun-haa joined-only length and blockers. | `phonemize/vowels/test_joined_only.py`; later include mim al-jam and vocalic yaa zawaid. |
| `waqf/test_taa_marbuta_pausal.py` | 10 | Every final-vowel/tanwin shape in joined and stopped states. | `phonemize/test_taa_marbuta.py` |
| `test_madd.py` | 21 | Strong behavior but too broad: tabii, muttasil, munfasil, lazim, arid, leen, iwad and exclusions. | Split across `phonemize/vowels/madd/test_tabii.py`, `test_muttasil.py`, `test_munfasil.py`, `test_lazim.py`, `test_arid.py`, and `test_leen.py`. |
| `test_muqattaat.py` | 27 | Opening-name phonemes, state stability, final noon/meem behavior. | `phonemize/test_muqattaat.py` |
| `test_qalqala.py` | 19 | Every letter and degree, negative cases, boundary and token toggle. | `phonemize/test_qalqala.py` |
| `test_rasm.py` | 25 | Strong pronunciation tests for silent written letters, hamza seats, and vowel carriers. | Split between `phonemize/test_silent_letters.py`, `phonemize/hamza/test_seats.py`, and `phonemize/vowels/test_written_carriers.py`; keep low-level projection fixtures in `adapter/`. |
| `test_one_offs.py` | 10 | Catch-all mixing inclination, ishmam, tashil, sakt, small noon and seat handling. | Delete after the case-level split below. |
| `test_khilaf.py` | 87 | Public catalogue and unrelated selector behavior in one file. | Do not touch until the final variant phase; then split catalogue to `api/test_variants.py` and behavior beside each semantic owner. |

### `test_one_offs.py` case split

| Cases | Destination |
| --- | --- |
| Majraha inclination and its extra token | `phonemize/vowels/inclination/test_quality.py` |
| Tamanna ishmam | `phonemize/test_tamanna.py`; keep one focused regression, not a nasal-family test |
| Aajamiyy tashil and its extra token | `phonemize/hamza/test_tashil.py` |
| Man Raq, Bal Ran, and Maliyah sakt | `phonemize/test_sakt.py` |
| Nunji small noon | semantic assertion in `phonemize/nasal/test_ikhfaa_haqiqi.py`; source-sequence fixture in `adapter/` |
| Iddaratum dagger/seat behavior | semantic assertion in `phonemize/hamza/test_seats.py`; seat projection in `adapter/test_hamza_seats.py` |

## Current `laws/` disposition

`laws/` is not a coherent test category. The files below divide into engine,
document, API, schema, conformance, and ordinary phonemization behavior.

| Current file | Cases | Actual responsibility | Proposed destination |
| --- | ---: | --- | --- |
| `laws/test_anchored_projection.py` | 11 | Inscription reachability plus public source/sound projection. | Split reachability to `adapter/test_inscription.py`; alignment assertions to `document/test_source_alignment.py`. |
| `laws/test_attestation_law.py` | 8 | Written-shadda accounting plus ordinary mutamathilayn behavior. | `adapter/test_attestations.py`; merge semantic sites into `phonemize/assimilation/test_mutamathilayn.py`. |
| `laws/test_boundary_split.py` | 1 | Exact consonant/vowel rule ownership at stopped taa marbuta. | Merge into `phonemize/test_taa_marbuta.py`. |
| `laws/test_build_contract.py` | 8 | Canon builder inputs, draft identity, edge withdrawal, replacement spans. | `engine/test_canon_build.py` |
| `laws/test_continuous_assembly.py` | 8 | Public request boundaries mixed with window assembly. | Request cases to `api/test_requests.py`; window privacy/equivalence to `engine/test_windowing.py`. |
| `laws/test_extra_phonemes.py` | 7 | Public token toggles and graph invariance. | `api/test_extra_phonemes.py` |
| `laws/test_fakk_idgham.py` | 3 | A named semantic classification and joined countercase. | `phonemize/assimilation/test_fakk_idgham.py` |
| `laws/test_inscription_hygiene.py` | 8 | Grapheme/spelling relation invariants and source projection edge cases. | `adapter/test_inscription.py` |
| `laws/test_madd_tabii.py` | 3 | Exact tabii classification over ordinary and boundary-created lengths. | `phonemize/vowels/madd/test_tabii.py` |
| `laws/test_minimal_pairs.py` | 19 | Valuable semantic contrasts, but no single conformance responsibility. | Dissolve into the semantic owners listed below. |
| `laws/test_model_vocabulary.py` | 19 | Closed typed model and effect/edge vocabulary. | `schema/test_model_vocabulary.py` |
| `laws/test_neighbourhood.py` | 6 | Generic engine traversal and stop visibility. | `engine/test_neighbourhood.py` |
| `laws/test_noon_family.py` | 11 | Domain partition mixed with generic planning/conflict invariants. | Domain partition/reach to `phonemize/nasal/test_noon_family.py`; generic conflict/ownership checks to `engine/test_rule_plan.py`. |
| `laws/test_pairing.py` | 404 | Public alignment partition and ownership over a broad sample. | `document/test_alignment.py` |
| `laws/test_parity_floor.py` | 3 | Slow legacy phoneme parity ratchets. | `conformance/test_legacy_parity.py` |
| `laws/test_phonemizer.py` | 17 | Public request/result/document surface. | `api/test_phonemizer.py` |
| `laws/test_recited_text.py` | 13 | Recited Arabic writer and source provenance. | `document/test_recited_text.py` |
| `laws/test_request_grammar.py` | 16 | Public reference grammar and ledger-clipped ranges. | `api/test_requests.py` |
| `laws/test_respelling.py` | 12 | Public respelling block partition. | `document/test_respelling.py` |
| `laws/test_roundtrip.py` | 18 | Canonical score writing and rereading. | `adapter/test_roundtrip.py` |
| `laws/test_rule_coverage.py` | 62 | Rule reachability and conflict freedom over the corpus sample. | `conformance/test_rule_coverage.py` |
| `laws/test_script_agreement.py` | 21 | Cross-script same-reading cases. | `conformance/test_script_agreement.py` |
| `laws/test_seven_alifs.py` | 9 | Canonical site discrimination for pausal alifs. | Merge into `phonemize/vowels/test_seven_alifs.py`. |
| `laws/test_teaching_labels.py` | 6 | Public rule labels. | `document/test_labels.py`; update when badal becomes a first-class rule. |

### `test_minimal_pairs.py` case split

| Contrast or invariant | Destination |
| --- | --- |
| Seven-alif versus ordinary alif | `phonemize/vowels/test_seven_alifs.py` |
| Final glide versus ordinary consonantal glide | `phonemize/vowels/test_final_glides.py` |
| Article lam versus form-VIII lam | `phonemize/articles/test_lam_contrasts.py` |
| Prosthetic versus lexical hamza | `phonemize/hamza/test_wasl_start.py` |
| Complete/incomplete merger interactions with qalqala and emphasis | corresponding `phonemize/assimilation/` merger file |
| Qalqala release ordering | `phonemize/test_qalqala.py` |
| Plural meem before wasl | `phonemize/hamza/test_iltiqa.py` |
| Muqattaat name seam | `phonemize/test_muqattaat.py` |
| Divine name versus ordinary lexical lam | `phonemize/emphasis/test_lam.py` |
| Written silent letters, hamza seats, and vowel-carrier contrasts | corresponding root `test_silent_letters.py`, `phonemize/hamza/`, or `phonemize/vowels/` file |

After this split there is no useful `minimal_pairs` conformance file. The
pair is strongest beside the rule whose overreach it prevents.

### `test_rasm.py` case split

`rasm` is not retained as a phonemization domain. The existing file contains
three different kinds of behavior:

| Cases | Destination |
| --- | --- |
| Written-but-unpronounced alif, waw, and yaa forms, including plural-alif and `مِا۟ئَة`-type spellings | `phonemize/test_silent_letters.py` |
| Hamza seats and seatless hamza in forms such as `لُؤْلُؤ`, `يُؤْمِنُونَ`, `يَأْكُلُونَ`, `خَاطِئَة`, and `ٱلْمَلَائِكَة` | `phonemize/hamza/test_seats.py` |
| Dagger-alif and other written vowel-carrier forms such as the `صَلَوٰة`, `زَكَوٰة`, and `حَيَوٰة` families | `phonemize/vowels/test_written_carriers.py` |
| Exact grapheme recognition, composition, and inscription relations for all of the above | focused fixtures under `adapter/` |

The semantic tests assert the final sounds and any named rule. The adapter
fixtures assert how the selected script supplied or attested the canonical
fact. Neither side should infer recitation from a raw codepoint in isolation.

## Schema, adapter, and root infrastructure

| Current file | Cases | Responsibility | Proposed destination |
| --- | ---: | --- | --- |
| `schema/test_canonical_roundtrip.py` | 5 | Public canonical JSON stability and schema versioning. | Keep. |
| `schema/test_inventory_contract.py` | 13 | Script-inventory loading, roles, capabilities and derivation registration. | `adapter/test_inventory_contract.py` |
| `schema/test_ledger.py` | 19 | Ledger schema, ownership, values, witnesses and address failures. | Keep. |
| `schema/test_lexicon.py` | 14 | Lexicon schema, budgets and match modes. | Keep. |
| `schema/test_negative_cases.py` | 22 | Public document schema rejection and pairing validation. | Keep. |
| `schema/test_render_map.py` | 15 | Typed sound-to-token inventory and notation YAML closure. | Keep as `schema/test_phoneme_inventory.py`; it is inventory validation, not a recitation example. |
| `test_canon_seat_decoration.py` | 3 | Low-level marked seat projection and deferred decoration. | `adapter/test_hamza_seats.py` |
| `conftest.py` | - | Slow marker plus Hafs-bound package/corpus/build fixtures. | Keep only generic pytest policy globally; move package/source/build helpers into `support/` and make them riwayah-owned. |
| `support/site.py` | - | Per-riwayah site address. | Keep, but semantic refs become canonical/public and source refs move to adapter fixtures. |
| `support/reading.py` | - | Full semantic-test assembly and weak occurrence lookup. | Keep, generalize package/script loading, and add exact source/unit/sound occurrence selectors. |
| `support/boundary.py` | - | Intent-based boundary plans. | Keep. |
| `support/__init__.py` | - | Public test-helper surface and riwayah parametrization. | Keep; use package-supported scripts rather than a global script list. |
| `README.md` | - | Current Site style and old layout. | Rewrite after the move; remove raw-riwayah-address and current-output-as-oracle advice. |

## Package markers

| Current marker | Disposition |
| --- | --- |
| `tests/__init__.py` | Keep. |
| `adjacent/__init__.py` | Replace with `phonemize/articles/__init__.py` and `phonemize/assimilation/__init__.py`. |
| `boundary/__init__.py` | Dissolve; move each case to its sound-domain owner. |
| `nasal/__init__.py` | Move to `phonemize/nasal/__init__.py`. |
| `tafkheem/__init__.py` | Move to `phonemize/emphasis/__init__.py`. |
| `waqf/__init__.py` | Dissolve; move vowel endings to `phonemize/vowels/` and taa marbuta to its focused root file. |
| `laws/__init__.py` | Delete after `laws/` is dissolved. |
| `schema/__init__.py` | Keep. |

Create package markers for the new `phonemize`, `adapter`, `api`,
`conformance`, `document`, `engine`, and semantic subpackages only where
imports or test tooling require them. Do not add an empty package merely to
mirror a rule phase.

## Snapshot families

Snapshots stay outside `phonemize/`. They are conformance artifacts, not
hand-authored pronunciation specifications.

| Family | Current contents | Responsibility | Disposition |
| --- | --- | --- | --- |
| `snapshots/head` | `word` 77,433 rows; `verse` 77,433; `alignment` 464,598; README | Current-checkout token and graph change detection. | Keep unchanged during the move. |
| `snapshots/phonemes` | word/verse/continuous, each 77,433 rows, plus manifest | Frozen legacy phoneme parity input. | Keep unchanged; not a correctness oracle. |
| `snapshots/legacy-api` | 18 gzip files across 3 modes and 6 legacy views, plus manifest | Frozen legacy information-coverage reference. | Keep unchanged; do not extend to Warsh. |

Warsh snapshots begin only after the fixed/default implementation is complete.
They must identify riwayah, script, boundary profile, extra-phoneme profile,
and default-variant profile in their manifest rather than relying on folder
context.

## Harness findings

The current Site-style tests are the right basis for cross-riwayah behavior,
but the helpers need four changes after the mechanical move:

1. `Site` must use canonical/public references. A separate adapter fixture
   records selected-source reference, exact source text, and alignment.
2. Script enumeration must come from the riwayah package. The current global
   `Script` iteration assumes both Hafs scripts belong to every riwayah.
3. `source_of()` and `host_of()` return the first rule occurrence in the whole
   reading; `rules_on_char()` and `rules_on_sound()` union repeated matching
   tokens. Add exact word/occurrence selectors before Warsh exception tests.
4. `reading()` currently contains Hafs-shaped editable-corpus assumptions and
   treats only Uthmani as packed. Move corpus/script loading behind each
   riwayah package.

The current suite has 266 direct `r.phonemes` assertions, 194 character-rule
queries, and 102 sound-rule queries. The style is valuable; the addressing is
the weak part.

## Adapter-first Warsh expansion

It is correct to add Warsh expectations to existing semantic tests before new
Warsh-only rules, provided each case is independently vetted. A failure in a
clean shared case is then high-confidence evidence of adapter projection,
canonical construction, or hidden Hafs coupling.

Do not mechanically add Warsh to every Site. Classify each current case:

### Good adapter-baseline candidates

- ordinary letters and harakat;
- qalqala examples whose surrounding context has no Warsh-specific operation;
- ordinary noon/tanwin/meem families away from naql and mim-al-jam sites;
- ordinary consonant assimilation and article-lam cases;
- ordinary pausal sukun, iwad, taa marbuta and clean final glides;
- ordinary structural madd examples away from badal, leen-mahmuz exclusions,
  and transformed hamza;
- clean hamzat-al-wasl starts and elisions whose Warsh morphology is verified;
- rasm cases where the Warsh source sequence has been explicitly projected
  and both readings genuinely produce the same canonical fact.

For these, extend every vetted existing case rather than adding one token
sample per rule. Use `pick()` only when a small expected detail differs.

### Cases that wait for a vertical

- iltiqa U-repair and Warsh-specific written linking vowels;
- naql and article-naql starts;
- single-hamza ibdal/tashil and hamza meetings;
- transformed-hamza madd attribution;
- mim al-jam, yaa zawaid, and Warsh seven-alif behavior;
- madd badal and leen mahmuz;
- inclination, Warsh raa, and lam taghliz;
- muqattaat affected by inclination or opening-boundary choices;
- every public selector.

Avoid a whole-word expectation if the word or its neighbour also contains an
unimplemented Warsh phenomenon. Prefer a clean occurrence or a local canonical
projection assertion.

## Recommended sequence

1. Approve this path map.
2. Perform a mechanical move only; do not change test bodies or expectations.
3. Generalize the harness while preserving all Hafs results.
4. Add the Warsh adapter, complete source-to-canonical alignment, and adapter
   fixtures.
5. Extend vetted existing `phonemize/` cases to Warsh and treat failures as
   adapter/shared-engine defects.
6. Implement each Warsh v2 vertical with its owning test file and independent
   closed-set register.
7. Run full default-profile conformance and add Warsh snapshots.
8. Split and implement variants last.
