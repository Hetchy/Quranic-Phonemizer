# Current implementation to target-model mapping

> **Archived 2026-07-26.** Historical record only — do not read this as a
> description of the current codebase or of the accepted design. A new ADR
> set is being written to supersede it.
>
> Reason: maps 35 pre-refactor production modules to target owners. Those
> modules no longer exist; most of the target owners were never built.

Status: audit record for the riwāyah refactor. Audited on 2026-07-16 at
`49f568e` on `riwayah-refactor`; rechecked against unchanged production code
on 2026-07-17 while refining the occurrence, renderer, and muqaṭṭaʿāt model.

This document is the bridge between “the new model looks plausible” and “we
know where today's behavior goes.” It covers all 35 production Python files
(7,372 lines), the five `dev/*.py` tools, runtime resource schemas, package
exports, workflows, and current tests/baselines. It is not a claim that current
behavior is correct; known defects are separated from parity requirements
below.

## 1. End-to-end ownership

```text
request/ref/ref_text/stop policy
  -> riwayah-scoped corpus + matcher
  -> exact source Graphemes
  -> source-adapter normalization to source-only LetterUnits
  -> lexical expansion + resolved boundaries -> RecitedWords/Letters
  -> baseline sound Segments
  -> shared rule passes + explicit riwayah pipeline classifiers
  -> TajweedOccurrence union (including MaddOccurrence) / RealizationRecord
  -> RecitedGraphemes + full RenderedPhonemes
  -> clean public projections
```

No projection may call a detector that can disagree with the canonical
occurrences. Existing views are behavior evidence, not schemas the new model
must preserve byte-for-byte. Each is retained as a thin projection,
redesigned, or explicitly retired.

## 2. Production-module migration map

| Current file(s) | Current responsibility | Target owner |
|---|---|---|
| `phonemizer.py` | public facade; reference detection/validation; text matching; stop validation; global phoneme overrides; orchestration; every result view/save format | thin facade and request resolver; immutable instance config; one `Recitation`; new projections |
| `loader.py`, `location.py` | one packed DB, one global `surah_info`, reference expansion, numeric address | `CorpusSpec` inside enum-keyed `RiwayahResources`; riwayah/config-keyed cache; corpus-scoped `Location`; one reference parser shared by facade/matcher/loader |
| `text_matcher.py` | source-character validation, Hafs-specific normalization/stripping, corpus preprocessing, scoped/unscoped fuzzy matching | riwayah-scoped matcher whose searchable normalization is supplied by the source adapter and whose cache key includes corpus + normalization identity |
| `parser.py` | YAML symbol factories, compact special-word short circuit, raw character attachment, contextual override attachment, word linking, stop/start flags | script tokenizer + canonicalizer; lexical expansion resolver; boundary resolver; no pronunciation mutation |
| `word.py` | mutable neighbour graph, two-pass phonemization, contextual mutations, mapping snapshot | utterance builder over indexed units/segments; typed exception pass; immutable word slices in final result |
| `symbols/symbol.py`, `diacritic.py`, `extension.py`, `stop.py`, `other.py` | runtime objects created from the Hafs symbol YAML | `Harakah` (including sukūn), `Tanween`, first-class `SmallVowel`, structural/hint enums, and source `Grapheme`s; remove the legacy generic extension class after the switch |
| `symbols/letters/letter.py` | central state machine: baseline consonant, shaddah, tanween, generic idghām, silence, neighbour mutation, source/target tags | baseline segment builder plus `rules/idgham.py`, `rules/noon_tanween.py`, and typed realization records |
| `symbols/letters/noon.py` | nūn/tanwīn-facing ikhfāʾ, iqlāb, idghām, ghunnah | shared `rules/noon_tanween.py`; canonical named rules with trigger kind |
| `symbols/letters/meem.py` | mīm sākinah and mushaddadah behavior | shared `rules/meem_sakinah.py`; ghunnah/idghām occurrences |
| `symbols/letters/hamza_wasl.py` | ibtidāʾ vowel selection, waṣl silence, iltiqāʾ mutation of previous vowel | shared `rules/hamza_wasl.py` + `rules/boundaries.py`; realization records, not invented Tajweed ids |
| `symbols/letters/vowel.py` | alef/wāw/yāʾ/alef maqṣūrah carrier decisions, silence, shortening, contextual consonant use | shared vowel-realization pass operating on semantic marks/features; dedicated madd occurrence pass runs after boundary/assimilation realization |
| `symbols/letters/raa.py`, `lam.py` | tafkhīm/tarqīq and lām shamsiyyah/Name-of-Allah behavior | `rules/raa.py`, `rules/lam.py`, `rules/idgham.py`; source glyphs only in script adapters |
| `symbols/letters/qalqala_letter.py`, `taa_marbuta.py` | qalqalah rendering and final tāʾ marbūṭah realization | `rules/qalqalah.py`, `rules/waqf.py`; qalqalah context on one occurrence |
| `phoneme_registry.py`, `phonemes.py` | global YAML caches/overrides and predicates inferred from output strings | immutable `RenderConfig`; typed segment features are rule predicates; retain token helpers only if the new public renderer API needs them |
| `madd.py` | rediscover long vowels from token strings and post-classify them, including location overrides and waqf cases | `rules/madd.py` records the `MaddOccurrence` Tajwīd variant while segments/typed causes are known; contexts cover Allah/ʿiwaḍ/ṣilah/muqaṭṭaʿāt; typed named exception sets only where current behavior requires them |
| `mapping.py` | mutable legacy word/letter/madd/alignment DTOs and serialization | replace with direct immutable projections over `Recitation`; keep individual DTOs only when their use is justified |
| `tajweed_rule.py` | mixed enum of Tajweed, madd, silence, and boundary mechanics; source/target boolean | conventional occurrence variants, `MaddType`/`MaddContext`, and `RealizationReason` from `docs/tajweed-model.md` |
| `tajweed_mapping.py` | rebuild per-grapheme tags; post-apply madd; use hand-authored special mappings | pure projection from the one Tajwīd occurrence union and source/recited graphemes |
| `tajweed_classification.py` | cross-word behavior registry, bridge/co-light metadata, cell enums, detector | canonical occurrence relationships and alignments; retire detector/bridge policy; keep cell enums only if the new API retains that presentation |
| `letter_phoneme_mapping.py` | split extensions; redistribute waqf/iltiqāʾ; merge silent glyphs prev/next/across words; special-word path | projection from source attribution, rendered-token spans, boundaries, and typed realization reasons; no Tajweed detection |
| `char_phoneme_mapping.py` | per-character roles/statuses, inserted/dropped/replaced/shortened cells, token indices, share groups, rule priorities | projection from Graphemes, RecitedGraphemes, rendered-token spans, occurrences, and realization records |
| `silent.py` | shard-specific grapheme tokenization and independent silence reconstruction | replace with alignment query; retain shard tokenization only if still a supported output |
| `phonetic_text.py` | separately rebuild transformed Arabic at waqf/ibtidāʾ and special words | `RECITED_ARABIC` renderer preset over stored recited graphemes; options cover inserted/silent/expanded display; no rule logic |
| `simple_mode.py` | token-string replacement and geminate collapse | presentation renderer over full rendered tokens; structural projections always use full mode |
| `specials.py` | global, default-path cache for muqaṭṭaʿāt display and hand-authored Tajweed mapping | riwayah lexical-expansion registry; parse the one recited spelling; no independent mapping cache |
| `__init__.py` | exports facade plus many internal classes, constants, predicates, and detector APIs | deliberately curated new public surface; remove accidental internals rather than freezing them forever |

## 3. Current rule/state mapping

| Current state mutation or inferred fact | Canonical representation |
|---|---|
| `letter.phonemes` and `modify_prev_phoneme()` | builder-owned segment replacement/removal with stable segment ids until freeze |
| `letter._tajweed_rules` source/target tags | one typed occurrence variant; subject/result in its core, family-specific following/reason fields, and a target only for actual assimilation |
| `word.is_starting`, `word.is_stopping` | resolved `WordBoundary` sequence with causes |
| `display_char` and phonetic-text glyph edits | source-linked `RecitedGrapheme`s plus typed realization reason |
| empty `letter.phonemes` | no segment attribution plus a typed silence/assimilation reason |
| `MaddMapping` found by `":"`/token set | `MaddOccurrence` in the Tajwīd union, linked to affected segment(s), recited carrier graphemes, typed cause, and context; plural segments support leen honestly; waqf ʿiwaḍ and ṣilah are contexts rather than fabricated exclusive types |
| qalqalah `Q` render-only token | one qalqalah segment/occurrence rendered to attributed output tokens |
| cell `phoneme_indices` | word-local indices assigned from ordered `RenderedPhoneme`s |
| cell `share_group` | connected source graphemes sharing occurrence segment(s); group number is projection-local |
| cell `present/inserted/dropped/replaced/shortened` | optional presentation enum derived from source/recited/segment attribution; retain only if consumers still need cells |
| flat-map `PREV/NEXT/CROSS_WORD_*` strings | old grouping policy; redesign around direct alignment/occurrence links instead of promoting these strings into the model |
| contextual `override_phonemes/tajweed/char` | named typed exception implemented in Python, with only riwayah-scoped locations/payload in data |

## 4. Current capabilities that migration must account for

### Current finite exceptions and expansions

The audit did not leave `contextual_pronunciations.yaml` as one undifferentiated
escape hatch. Each current row has a proposed owner:

| Current case | Target owner |
|---|---|
| 41:44 second-hamza/tashīl site | one named Hafs hamza-realization handler plus location fixture; decide the exact supported sound from the current contract/research before naming it `TASHIL` |
| 11:41 imālah | Hafs adapter recognizes the `۪` marked-vowel sequence; concrete Hafs marked-vowel classifier returns `IMALA`; no location patch |
| 27:36 stopped-on mini-yāʾ/pronoun form | named Hafs waqf exception and `RealizationEvent` until/unless a general written pattern is proved |
| 2:72 ornamental dagger-alef form | source-adapter sequence fixture plus ordinary carrier/emphasis logic; remove the location phoneme patch if the normalized spelling fully explains it |
| 21:88 mini-nūn ikhfāʾ | source adapter emits the canonical nūn/tanwīn input from the reviewed small-nūn sequence; shared ikhfāʾ derives the result |
| started-on `ٱئْتُونِى` locations | named Hafs ibtidāʾ handler with locations in `exceptions.yaml`; inserted/carrier sounds have realization provenance |
| 10:51 and 10:91 madd-lāzim overrides | named Hafs madd exception unless the new semantic sequence classifier makes the override unnecessary |
| compact muqaṭṭaʿāt | all fourteen Arabic recited names parsed by the ordinary pipeline; following Qurʾānic word remains in context; clear-nūn `يسٓ`/`نٓ` and connected Āl ʿImrān are named Hafs exception fixtures |

Every row is tested before the generic patch schema is deleted. A source mark
which fully explains a case moves to normalization/classification; only a true closed
location list remains in exceptions data.

### Construction and request

The current constructor accepts `db_path`, `map_path`, `muqattaat_path`,
`contextual_pronunciations_path`, and `extra_symbols`. The new constructor uses
`riwayah` plus immutable instance configuration. Old path-injection arguments
are not architectural requirements; either replace them with explicit
`RiwayahResources`/test factories or retain a narrowly justified development API.

`phonemize()` behavior inventory covers `ref`, text-as-`ref`, `ref_text`, scoped text
matching, `stop_signs`, `stop_refs`, `debug`, the two phoneme overrides, and
`mode`. Raw riwayah stop glyphs normalize first. Global token overrides become
immutable renderer configuration.

### Result and serialization

For each item, PR 8 records `retain`, `redesign`, or `retire` and supplies a
semantic regression where it remains supported:

- `phonemes_list()` for `word`, `verse`, and `both`;
- `phonemes_str()` separator and verse-boundary behavior;
- `text()` and verse-number insertion;
- `phonetic_text()` including all waqf/ibtidāʾ transforms;
- `tajweed_mappings()`, `silent_flags()`, `letter_phoneme_mappings()`,
  `character_phoneme_mappings()`, and `get_mapping()`;
- `show_table()` with and without pandas;
- `save()` JSON, CSV, mapping, Tajweed, letter, and character formats;
- special sub-locations, global and word-local indices, `match_score`, and
  empty-result behavior where retained;
- every current name in `quranic_phonemizer.__all__`, with an explicit keep or
  removal decision.

Simple mode affects raw phoneme/table/save views only today. Structural views
continue to use the full vocabulary.

## 5. Resource migration map

| Current resource | Target |
|---|---|
| `quran_db.bin`, `surah_info.json` | paired files under each `data/riwayat/<id>/corpus`; loader validates word-slot count and address shape together |
| `base_phonemes.yaml` | replace with glyph-first source aliases and shared/riwayah render data; no English-id scalar registry and no universal glyph semantics |
| `rule_phonemes.yaml` | render-token config, instance-local overrides |
| `simple_phonemes.yaml` | shared presentation-render config unless a real riwayah delta is proved |
| `contextual_pronunciations.yaml` | named typed exceptions with riwayah-scoped locations; remove generic override operations; move Hafs imala to the marked-vowel classifier |
| `muqattaat.yaml` | one shared Arabic spelling per letter name; remove copied phonemes, `letter_mappings`, and `tajweed_mapping`; keep only typed location exceptions |
| `resources/tajweed_occurences/` | source material under `research/phonemizer/tajweed-occurrences/`; promote small executable cases to `tests/fixtures/` and stable conclusions to docs |
| `out/` | generated artifacts under ignored `build/`; record only concise reviewed conclusions in the relevant doc |

The wheel configuration must recurse into nested riwāyah data folders. The current
`resources/*` package-data pattern does not.

`base_phonemes.yaml` is fully decomposed rather than renamed wholesale:

| Current section/value family | Target owner |
|---|---|
| ordinary Arabic `letters` | glyph-first baseline `Letter`/consonant data; hamza seats normalize to semantic glottal stop while source is preserved |
| fatha/damma/kasra/sukūn | `Harakah`; explicit sukūn remains distinct from bare |
| three tanween marks | `Tanween`; Warsh aliases/composites normalize in its source adapter |
| dagger alef, mini wāw, mini yāʾ | first-class `SmallVowel`; no generic extension class |
| maddah | source orthographic sign/hint; madd derives from semantic carrier/context |
| stop signs, rub-el-hizb, sajdah | structural source inputs and boundary/address policy; never letters/phonemes |
| shaddah | first-class gemination input |
| `SILENT_ALWAYS`, `SILENT_AT_CONTINUATION` | source-convention hints consumed by typed realization; Warsh reuses the same scalars only through sequence fixtures |
| mini mīm | iqlāb hint or part of composite tanween; not a pronounced/small vowel |
| mini sīn/nūn and `S1/S2/S3` | reviewed source hint/marked-sequence inputs; contextual meaning stays in adapters/typed handlers |
| tatweel/RLM/formatting | exact source grapheme with structural/ignored alignment |

The IPA-like `phoneme` values move to shared semantic render maps. They no
longer define the source scalar's universal meaning or drive rules.

## 6. Development tooling and workflows

| Current file | Refactor role |
|---|---|
| `dev/build_quran_db.py` | move to `tools/corpus/build_db.py`; drive it from a riwayah corpus manifest and preserve reproducibility checks |
| `dev/audit_silent_letters.py` | move to `tools/audit/`; compare canonical alignment/reasons instead of maintaining a second list of “silent rules” |
| `dev/catalog_cells.py` | move to `tools/audit/`; use only while deciding whether the old cell presentation survives |
| `dev/reconcile_tokenization.py` | turn its known Tajweed/flat/shard divergences (muqaṭṭaʿāt and synthetic Allah dagger) into model/projection fixtures |
| ignored local `dev/helpers.py` | stale package-relative imports and old JSON/global DB assumptions; extract any still-useful audit routines into `tools/audit/`, otherwise retire; never make it a runtime abstraction |
| `scripts/analyse_tajweed_overlaps.py` | move to `tools/audit/`; consume canonical typed occurrences, compare semantic overlaps, and write generated reports only under `build/reports/` |
| `scripts/analyze_haraka_phoneme_mapping.py` | retain only as a pre-migration audit under `research/phonemizer/experiments/` if its legacy string-attribution report is still needed; direct source-to-segment alignment replaces the inference in the new model |
| `scripts/compare_full_quran.py` | move to `tools/audit/compare_full_quran.py`; compare explicit semantic/render projections against the external implementation and write reports under `build/reports/` |
| `scripts/convert_transcript.py` | keep with the external `quran-transcript` comparison experiment under `research/phonemizer/experiments/`, not runtime or build code; its mojibake/static conversion tables must be repaired before reuse |
| `scripts/export_tajweed_mappings.py` | replace with a projection-only `tools/audit/export_occurrences.py`; export typed occurrences from the ordinary pipeline and delete its special muqaṭṭaʿāt reconstruction |
| `scripts/find_top_verses.py` | move to `tools/audit/`; query the typed occurrence projection instead of parsing legacy rule strings and separate madd DTOs, with generated rankings under `build/` |
| `scripts/generate_lpm_baseline.py` | use only as a migration gate after replacing its missing `scripts.prepare_mfa_mappings` import with the new alignment projection; retire the legacy baseline once semantic fixtures cover the retained contract |
| `.github/workflows/sync-quran-db.yml` | parameterize/iterate corpus manifests and verify each committed binary/address pair |
| `.github/workflows/publish.yml` | run tests and inspect/install built wheel/sdist before publishing; current workflow only builds and uploads |
| `research/hafs/syntheses/`, `dev/tajweed_occurences/` | move phonemizer source prose/assets to `research/phonemizer/`, unrelated study to `research/quranic-studies/`, executable cases to `tests/fixtures/`, and stable conclusions to docs; none is runtime data |

Corpus source must live outside the runtime wheel, but its manifest,
transformation steps, and binary build must be reproducible per riwāyah. A
generic Arabic-block cleaner is not an acceptable build step.

## 7. Tests and uncovered behavior

Current automated coverage is strong only for one view:

- 114 full-surah flat letter/phoneme baseline cases;
- 60 targeted Tajweed mapping cases in the JSON suite;
- eight silent-flag cases.

There are no direct tests for core phoneme output, character mappings,
phonetic text, mapping serialization, text matching, constructor overrides,
riwāyah/cache isolation, packaging, or public exports.

Confirmed current defects are not parity requirements:

1. `ref_text` and text-as-`ref` reach `TextMatcher._preprocess_database()`,
   which calls `_DB.items()` even though `_DB` has no `items`; the path raises
   `AttributeError`.
2. `load_db(db_path)` caches one global `_DB` without including `db_path`, and
   always derives offsets from the one global `surah_info.json`; two corpora
   cannot safely coexist.
3. runtime phoneme overrides are process-global and persist across calls.
4. `pyproject.toml` claims Python `>=3.8`; the target now explicitly requires
   Python 3.11+.
5. nested riwāyah resources would be absent from the current wheel.

A full 1–114 scan with verse stopping also confirmed that the current
character model currently emits exactly four roles (`base`, `haraka`,
`tanween`, `madd`) and five statuses (`present`, `inserted`, `dropped`,
`replaced`, `shortened`). These remain closed projection enums, not resource
opcodes. The scan found 30 compact special-word occurrences and only the six
stored madd classifications listed in ADR-001; `madd_iwad`, `iltiqaa`,
`allah_dagger_alef`, and `hamza_wasl_vowel` occur as character-view context
tags rather than evidence for new Tajweed or madd types.

Each defect needs a regression test and an intentional fix. The new
architecture must not depend on defective behavior.

## 8. Readiness conclusion

Every current production module now has a target owner. The Hafs refactor and
accepted Warsh source-adapter subset are implementation-ready in the PR
sequence in `warsh-integration-plan.md`. Full Warsh pronunciation remains
blocked only on the explicit linguistic/script unknowns in that plan, not on
an underspecified internal model.
