# Architecture audit, July 2026

Four independent reviewers, no shared context beyond the ADRs and the gate
definitions, each given one angle and told to verify before asserting:

| | Angle | Report |
|---|---|---|
| A1 | Import graph, module ownership, dead code, docs layout, CI hygiene | structure |
| A2 | Data versus code: every file both directions, role strings, render encoding | data |
| A3 | Riwayah-agnosticism, audited against the Warsh codepoint audit and PR #37 | riwayah |
| A4 | Abstraction, domain modelling, ceremony, antipatterns | modelling |

Where several reached the same conclusion separately, that is recorded below as
convergence and treated as settled. Where one found something alone, it is
recorded with the evidence that makes it checkable.

## What converged

**Three reviewers rejected merging the three `khilaf.py`.** A1, A3 and A4 each
concluded independently that `canon/khilaf.py` (changes a Score),
`rules/khilaf.py` (chooses a Performance of one Score) and `riwayat/khilaf.py`
(loads and assembles) sit on a real layer seam. The defect is that the latter
two hardcode the Hafs catalogue, not that three files share a basename.

**Three reviewers found `polysemous` inert.** It is parsed
(`orthography/inventory.py:345`), stored on `MarkEntry`, and read by nothing.
The loader's own docstring claims it "forces the adapter to defer".

**Three reviewers found `attests` accepted with no loader.** It is in
`_SECTIONS` and reaches `require_keys`; `load_inventory` calls no
`_load_attests`. `Reading.attestations` is initialised, returned, and never
appended to.

**Three reviewers measured the render map independently and got the same
number.** 71 of 99 declared rows reached over the whole corpus in both scripts,
under both joined and stopped plans. All three also found that
`tools/build_render_map.py:18-47` restates every phoneme token in Python,
falsifying the header of `ipa.yaml`.

**Three reviewers found the same role-string duplication.** 19 of the 22 role
values the script YAMLs declare are repeated as Python literals, across
`spell.py`, `cluster.py`, `write.py`, and four `canon/derive/` modules.

**Three reviewers said the lexicon budgets belong to a gate, not to runtime
loading.** They are review thresholds; rejecting a resource at an arbitrary
ceiling does not prove the class is well-founded, and the mechanism misses both
duplicates and one whole unbudgeted section.

**Two reviewers found the vocalised-key notation has three writers and one
partial parser**, in `canon/passes.py`, `rules/khilaf.py`,
`tests/test_khilaf_sites.py`, with `canon/spell.py` holding the only decoder and
a different dialect from all of them.

## Critical, found alone

### The round-trip gate hashes a lossy projection

`_digest` (`canon/build.py:445`) serialises letter, onset, nucleus kind and
quality. It omits `Slot.annotations`, `Slot.origin`, `ScoreWord.sakt_after`,
`ScoreWord.location` and the selection. Both `tests/test_roundtrip.py:46` and
`tools/roundtrip.py:93` compare digests and nothing else, so a write-read cycle
that loses an annotation or a sakt reports 100%. `write.py:133` deliberately
skips annotations it expects re-derived, which is exactly the blind spot.

Fix: compare normalized Score structures; keep a digest only if its serialised
input is complete. Add one mutation test per omitted field.

### The seen/sad khilaf cannot be selected

`KhilafId.SEEN_SAD` exists (`model/address.py:126`) and `khilaf.yaml` has no
`seen_sad` section. Both scripts declare the mark as `fact: LETTER, value:
SEEN`, but base-letter evidence is emitted first and `_letter_of` returns the
first non-null row, so every site stays `SAD`. The public `VariantSelection`
vocabulary advertises a choice that changes nothing.

The accident is load-bearing: the same scalar is the sakt sign at five sites,
so "last row wins" would replace the host letter there. Two `LETTER` evidences
must be rejected, not ordered.

### Riwayah identity is forgeable end to end

`Reading` carries a script and no riwayah. `build` takes its own `riwayah`
argument defaulting to Hafs; `perform` takes another one, defaulting to Hafs,
despite receiving a Score that already has one. The Ledger requires a `riwayah`
key and never reads its value. `riwayat/hafs/resources.py:58` iterates the
global `Script` enum, so adding a Warsh script member makes the Hafs package
try to load a Hafs file that does not exist -- adding a script is not additive.

### There is no composition root, and a committed tool cannot be imported

ADR-007 names `api.py`; it does not exist. `tools/freeze_phonemes.py` imports
`quranic_phonemizer.api`, `quranic_phonemizer.resources` and `Phonemizer`, none
of which exist, and fails at import. `engine/boundary_plan.py::plan_from_request`
has no caller and is wholly unexecuted; `adapters_for` and `rules_for` likewise.

### `canon.derive` is an import cycle

`derive/__init__.py` defines the vocabulary and registry, then imports all six
implementations at the bottom; each implementation imports the parent. Import
order is a hidden registration mechanism.

## The rest, by owner

### Data versus code

- `role: str` is an untyped second semantic API. `Mark` keeps only
  `char`/`offset`/`role` although the loader parsed `fact`, `value`,
  `derivation` and the glyph capabilities. Propagate typed semantics; make
  `role` diagnostic text.
- `cluster.DAGGER` and `SEATABLE` are orthographic facts and belong in script
  YAML as per-scalar capabilities. `spell.HARAKAT` should be a query for typed
  nucleus evidence and belongs in neither place.
- `A -> ALIF`, `U -> WAW`, `I -> YA` and the imala base quality are properties
  of the canonical model and stay in source -- but centralized once, not
  duplicated in `write.py` and `derive/length.py`.
- `ALWAYS_RUN` and `SCRIPT_OPTIONAL` are patches over a one-directional
  contract check. Replace with derivation-registry metadata and explicit
  semantic alternative groups.
- `lexicon.yaml` lists the same skeleton three times across three sections;
  `frozenset` swallows it before the budget is counted.
- `ledger.yaml` asserts compare only `(ref, fact)`. `script`, `value` and
  `skeleton` are parsed and never checked against the supply or the script.
- The rule-table loader validates outcome keys against the whole `Rule` enum, so
  a madd rule is accepted as a noon follower.
- `require_keys` is the mechanism behind all of it: it proves a key is
  whitelisted, never that anything reads it.

### Abstraction

- `Insert`, `Inserted` and `Side` have no producer. `Realize.sounds` is a tuple
  the engine reads as `sounds[0]`. `Recolour` declares a `NASAL` feature no rule
  emits. `SoundSpec` aliases `Sound`.
- Producer census: 11 `Realize`, 5 `MergeInto`, 8 `Silence`, 0 `Insert`, 2
  `Recolour`, 3 `Relength`. The union earns itself; two of its members do not.
- `triggers` earns itself, measured: 5,741,140 possible classifier-slot checks
  reduce to 1,296,397. Deleting it adds about 4.44M `look` calls.
- `Scribe` keys spelling links on `id()` of a mutable draft and drops silently
  on a miss. Give drafts a stable id and make the miss loud.
- The five-object pass signature is why the package holds 28 `del` statements.
- `_before` / `_previous` / first- and last-of-word are reimplemented in four
  rule modules; a full-corpus run measured 23,526 extra `Score.slots()` calls
  and about 1,686,196 extra slot items inspected. The cost is real but the
  stronger defect is four divergent copies of one boundary semantics.
- Eight files check `schema_version: 1` with no migration, no second version and
  no independent consumer.

### Modelling, before projections become a contract

- `Onset` makes manner (`PLAIN`, `GEMINATE`, `TASHIL`) mutually exclusive with
  presence (`WASL`, `SILAH`). They are orthogonal.
- `SlotOrigin` answers three unrelated questions; `WRITTEN` carries no
  information and the enum forbids "spelled and nunation" for no domain reason.
- `Annotation` is documented as changing no sound, and `DIVINE_NAME` changes
  sound through `tafkheem.py:136`.
- `PausalLong` and `Silah` are boundary rules wearing nucleus kinds.

Moving `IMALA` from `Quality` to `Annotation` was judged correct by A4: the
named process persists whichever vowel the khilaf selects. It does not follow
that every disputed value needs a tag.

### Riwayah

- `data/shared/rules.yaml` declares Hafs research as riwayah-independent fact,
  and the overlay silently inherits omitted keys, so an incomplete Warsh file
  would mean "use Hafs" rather than "unreviewed". Make inheritance an explicit
  statement.
- The scalar inventory is `dict[str, Entry]`, one character at a time. Warsh has
  no `U+0671`; wasl is a multi-scalar sequence, `U+06EA/06EC/06DF` are
  sequence-dependent, and tanween composes a haraka with a mini meem. A
  declarative sequence layer belongs in `orthography/`, its table in
  `riwayat/warsh/`.
- Hafs-versus-Warsh parity is invalid as a gate: a riwayah is precisely a
  reading whose Score may differ. What transfers is the inventory totality, the
  clustering, and the Score as a meeting point for two scripts of *one* reading.
- The replacement is a per-riwayah conformance harness: intake closure,
  Inscription-Score closure, a reviewed rule matrix as the local oracle,
  hint-agreement where source marks never drive a rule, certified differential
  alignment over the aligned pairs partitioned by the audit's five classes, and
  internal completeness.

### Enforcement, so this does not recur

`tests/test_import_boundaries.py` walks only relative `ImportFrom` nodes, skips
any import whose package is absent from its table, and detects no cycles. Its 62
passing cases are why every `dataio` edge and the derive cycle are invisible.

The recurrence mechanism is general: each convention has a partial checker or
none. One `tools/structure_lint.py`, stdlib plus the existing YAML loader, with
checks registered as data:

`import-graph`, `unused-imports`, `dead-exports`, `dead-symbols`,
`module-size`, `orphan-data`, `code-data-duplication`, `tool-import-smoke`.

Each has a known expected output on today's tree, so the script can land in
report mode and be switched to enforcing one check at a time as the finite
backlog closes.

`comment_lint.py` budgets docstrings and never groups adjacent comment lines.
There are 84 multi-line inline-comment blocks holding 213 comment lines, and it
reports zero problems. Two of the seven policy classes -- whether a comment
explains a non-obvious why, and narration as a semantic category -- are not
reliably scriptable and stay review-owned; the other five can be tightened.

### Documents

`docs/` holds two research trees, three completed phase reports beside the
ADRs, gate bookkeeping, and a PR description presented as live documentation
that describes a package tree the code no longer has.

Convention adopted:

- `docs/adr/` -- only the README and numbered decision records.
- `docs/conformance/` -- current gate definitions, current residue, how to
  reproduce them.
- `docs/` -- maintained references describing the current release.
- `research/` -- provenance, citations, audits, source notes, generated
  evidence, completed phase reports. Never moved for age alone.
- `docs/archive/` -- documents once presented as current guidance and now
  replaced, moved in the same change that lands the replacement.

## What was rejected

Recorded so it is not re-litigated:

- Merging the three `khilaf.py`. Three reviewers, separately.
- Cross-riwayah phoneme parity as a correctness target.
- The global `Rule` enum as riwayah leakage: `RuleSet` already selects a subset,
  and a closed vocabulary is what gives occurrences stable public names.
- Refactoring `SlotOrigin` before a case needs two axes at once -- although its
  deletion is still wanted for the reasons above, no audited Warsh case is
  presently unrepresentable.
- `ledger.yaml` as a rule engine: `parse_value` accepts canonical values only,
  with no condition, effect or phase.
- `rules.yaml` as misplaced code: a finite decision table with overlap
  rejection.
- `muqattaat.yaml` as a Hafs fact, and its `names` ordering as execution order.
  The order is the fact.
- Splitting `orthography/inventory.py` on line count alone; its seams are
  consecutive and cohesive.
- Merging `rules/tables.py` with `riwayat/tables.py`: that would make `rules`
  import data loading.
- `dataio.py` at the root: a neutral leaf that imports no package module. The
  defect is that ADR-007's table omits it.
- Deleting the 28 unreached render rows on the reach count alone. Some are
  reachable only under a non-default khilaf.
- Adding a rule as shotgun surgery: tracing `IBDAL_HAMZA` finds five files --
  the rule vocabulary, the classifier, Hafs registration, and two tests.
- Explicit engine phases as temporal coupling: assimilation before realization
  is domain order. The real coupling is the hidden draft-identity contract.
