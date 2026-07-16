# ADR-003: Code, runtime data, corpus builds, evidence, and research

Status: **accepted for implementation** — companion to ADR-001/002.

The previous proposal was too loose in both directions: it implied that rules
could "live in data", while also putting copied `hafs/rules` and `warsh/rules`
trees under resources. That would produce an opaque rule DSL and defeat the
shared refactor. This ADR defines a strict ownership boundary and removes the
ambiguous `dev/` bucket.

## 1. Ownership rule

Put a fact in **typed Python code** when it describes how pronunciation is
computed:

- pass ordering and boundary interaction;
- nūn/tanwīn and mīm realization;
- idghām/ikhfāʾ/iqlāb sound construction;
- rāʾ and lām tafkhīm/tarqīq decisions;
- hamzat al-waṣl and iltiqāʾ al-sākinayn;
- vowel-carrier, waqf, ibtidāʾ, and madd classification logic;
- contextual Unicode sequence interpretation;
- a genuine riwāyah algorithm delta.

Put a fact in **runtime data** when it is finite, declarative, reviewed, and
loaded without executing an algorithm:

- corpus/address data;
- simple source-scalar aliases and inventories;
- finite letter groups and pair tables;
- rendered phoneme tokens;
- muqaṭṭaʿāt recited spellings;
- locations for a named typed exception;
- provenance/schema ids.

Put a fact in **evidence** when it directly justifies a shipped behavior but is
not loaded at runtime: occurrence lists, reviewed script fixtures, comparison
reports, screenshots, citations, and audit outputs.

Put exploratory material in **research**. Nothing in research is authoritative
or importable by the package.

Put reproducible generated intermediates/reports in **build**. Nothing in
build is a hand-maintained source of truth or imported at runtime.

The decisive YAML test is: can a reviewer understand the field without
mentally executing a program? If not, it is code.

## 2. Target repository layout

```text
quranic_phonemizer/
├── model/                         # frozen target dataclasses/enums
├── corpus/                        # runtime DB/index loading and refs
├── script/                        # tokenizer + source adapters
├── rules/                         # shared rule implementations
├── riwayat/
│   ├── registry.py                # RiwayahSpec registration
│   ├── hafs/                      # only Hafs policy/adapter code
│   └── warsh/                     # only proved Warsh policy/adapter code
├── render/                        # semantic segment -> output token
├── projections/                   # new public views
└── data/                          # only files shipped in wheel
    ├── shared/
    │   ├── tajweed.yaml           # finite shared letter/pair sets
    │   ├── render.yaml            # full/simple token maps
    │   └── muqattaat.yaml         # Arabic compact letter -> recited spelling
    └── riwayat/
        ├── hafs/
        │   ├── riwayah.yaml       # ids, provenance, file references
        │   ├── script.yaml        # simple scalar aliases/inventory
        │   ├── exceptions.yaml    # locations by typed exception id
        │   └── corpus/{quran_db.bin,surah_info.json}
        └── warsh/
            └── ...

corpora/                           # build inputs; not shipped
├── hafs/
│   ├── manifest.yaml              # provenance/licence/checksums
│   ├── source/                    # immutable downloaded/original files
│   ├── transforms.yaml            # reviewed source -> canonical manifest
│   └── canonical/words.json       # reviewable DB input
└── warsh/
    └── ...

tools/
├── corpus/                        # clean/split/pack/reproduce commands
└── audit/                         # Unicode, alignment, coverage reports

evidence/                          # reviewed product evidence; not shipped
├── script/
│   ├── hafs/conventions.md        # semantic/hint/ignored source conventions
│   ├── warsh/conventions.md
│   └── hafs-warsh/                # comparison matrices/fixtures
├── tajweed/hafs/
└── exceptions/hafs/

research/                          # exploratory notes/assets; not authoritative
├── domain/
├── sources/
└── experiments/

tests/fixtures/                    # small executable expected cases
build/                             # ignored/generated intermediates and reports
docs/                              # decisions, contracts, explanations
```

There is no generic `dev/`. Existing files move by purpose:

| Current material | Destination |
|---|---|
| `dev/Quran.json` | `corpora/hafs/canonical/words.json` |
| PR raw/cleaned/split Warsh corpus | raw under `corpora/warsh/source`; reviewed canonical words under `canonical`; generated cleaned/split copies under `build` |
| `dev/build_quran_db.py` | `tools/corpus/build_db.py` |
| Unicode/silence/catalog scripts | `tools/audit/` |
| reviewed Tajwīd occurrence lists and screenshots | `evidence/tajweed/hafs/` |
| exploratory prose or unrelated Qurʾānic study | `research/domain/` or `research/sources/` |
| full-corpus generated comparisons | `build/reports/`; commit only a reviewed summary under `evidence/` when needed |
| runtime `resources/tajweed_occurences/` | move to evidence; it must not ship |

## 3. Shared code and sparse riwāyah deltas

Shared rule implementations live once under `rules/`. Shared finite tables
live once under `data/shared/`. A riwāyah directory contains only:

- its corpus and source-script aliases;
- its true location exceptions;
- its renderer differences, if any;
- policy functions or replacement tables proven to differ.

There is no `data/riwayat/hafs/rules/` mirrored into
`data/riwayat/warsh/rules/`. If both riwāyāt use the same nūn/tanwīn table,
Warsh has no copy. If research proves a whole finite family differs, the
riwāyah replaces that named table as a complete validated unit; recursive deep
merging is forbidden.

Complex variation uses policy functions in `riwayat/<id>/rules.py`, composed
through `RulePolicies`. Functions are imported by Python registration, never
named as YAML strings.

## 4. Glyph-first data

Do not repeat an English letter id, codepoint integer, Unicode name, and glyph
for the same scalar. The glyph is the primary key; audit tools derive
codepoint/name/count.

Shared finite rule data is compact Arabic:

```yaml
schema_version: 1

noon_tanween:
  izhar_halqi: "ءهعحغخ"
  idgham_bi_ghunnah: "ينمو"
  idgham_bila_ghunnah: "لر"
  iqlab: "ب"
  ikhfaa_haqiqi: "تثجدذزسشصضطظفقك"

meem_sakinah:
  ikhfaa_shafawi: "ب"
  idgham_shafawi: "م"
```

The loader converts each glyph to the `Letter` enum, rejects duplicates and
overlap, and proves the exhaustive partition. Python implements what iqlāb or
ikhfāʾ does. The file never says `effect: merge_plain`, `keep`, `nasalize`, or
`silent`.

A simple source-script alias can also be glyph-first:

```yaml
schema_version: 1

single_marks:
  "ٖ": {tanween: kasr}
  "ٗ": {tanween: fath}
  "ٞ": {tanween: damm}
  "ے": {letter_family: "ى"}
```

The values are loaded into closed enums. Contextual patterns such as initial
`اَ۬`, the polymorphic `۪`, combining-hamza sequences, and mini-mīm iqlāb
compositions stay in the source adapter with exact fixtures. In particular,
harakah+mini-mīm normalizes to a canonical `Tanween` plus a hint, while
bare-nūn+mini-mīm normalizes to nūn sākinah plus the same hint. Forcing either
into a scalar-only table would recreate the bug this refactor is meant to
remove.

## 5. Phoneme and Tajwīd data

There is no `tajweed_phonemes.yaml` which assigns mutation effects to rules.

Rules create semantic segments—for example a hidden nasal, a nasalized target,
an emphatic rāʾ, or a qalqalah consonant. `data/shared/render.yaml` maps those
semantic values/features to output tokens. A sparse riwāyah render override is
allowed when the same semantic result is intentionally rendered differently.
Runtime user overrides are immutable per phonemizer instance.

Baseline written-letter mappings are also glyph-first. A renderer table may
use `"ب": "b"`, `"ر": "r"`, and Arabic vowel-mark keys. Non-written semantic
sounds use typed semantic ids because there is no honest source glyph for a
placeless nasal or qalqalah release.

Changing a token never changes a rule decision or occurrence. Rule code never
searches for `:`, `~`, `Q`, or another token convention.

## 6. Madd

There is no madd duration data and no `min`/`max`. The six supported
`MaddType`s are code enums; the shared Python classifier records a type, vowel
segment, carrier, and cause.

No `silah_sughra`, `silah_kubra`, or `badal` row is added because it exists in
a textbook. Ṣilah context belongs to the relevant realization policy. A new
madd type lands only with a supported riwāyah example, implementation, API
need, and regression test.

## 7. Muqaṭṭaʿāt

Store the only non-derivable input: the Arabic recited name.

```yaml
schema_version: 1
names:
  "ص": "صَادْ"
  "م": "مِيمْ"
  "ع": "عَيْنْ"
```

`display`, `segments`, long-vowel flags, leen flags, phoneme arrays,
letter mappings, and Tajwīd mappings are derived from that spelling by the
normal pipeline. In particular, `عَيْنْ` visibly contains the information
needed to derive its short vowel, yāʾ/leen relationship, and final nūn.

The compact corpus text identifies the opening, so location lists are omitted
unless a demonstrated ambiguity requires them. A riwāyah-specific recited
name is a sparse override.

## 8. Typed exceptions, not patches

Data may associate locations with a named exception implemented in Python:

```yaml
schema_version: 1
riwayah: hafs

started_iituni:
  - "10:79:3"
  - "12:50:3"
  - "12:54:3"
  - "12:59:5"
  - "46:4:18"
```

It may not contain a general list of `set_phonemes`, `clear_tajweed`,
`replace_char`, or `insert_after` operations. That would be a second untyped
phonemizer. When a recurring exception needs a small typed payload, define a
schema and Python handler for that family only.

Hafs 11:41 imālah should not remain a location exception once the source
adapter recognizes its marked `۪` vowel sequence. The mark produces a typed
marked-vowel input and the Hafs policy classifies it. This same seam permits
Warsh marked vowels without copying the hardcoded Hafs location.

## 9. Corpus build contract

Each `corpora/<riwayah>/manifest.yaml` records:

- source URI/provider, retrieved version/date, licence and redistribution
  decision;
- immutable source hashes;
- canonical address/basmalah/structural-token policy;
- ordered transformation ids and expected counts;
- canonical word JSON hash;
- generated DB/index hashes and schema versions.

`transforms.yaml` lists each removal or replacement semantically. A transform
may say that one presentation-form ayah-number glyph and trailing NBSP are
removed per raw verse, with exact input/output counts. It may not say "delete
whatever the Arabic-block validator flagged".

The build is:

```text
corpora/<id>/source
  -> reviewed transforms
  -> build/corpora/<id>/normalized + inventories + reports
  -> corpora/<id>/canonical/words.json (reviewed/committed input)
  -> build/corpora/<id>/quran_db.bin + surah_info.json
  -> verified copy under package data
```

CI rebuilds and compares the committed runtime pair. It also checks that
structural glyphs such as rub-el-hizb did not accidentally become lexical word
addresses.

## 10. PR #37 disposition

PR #37 remains useful intake work: it supplies the source, font, raw/cleaned
artifacts, word corpus, parameterization direction, and inventory utilities.
It is not a Warsh rule implementation.

Accepted direction:

- separate Warsh corpus/address data;
- immutable raw source and reproducible transforms;
- font coverage as a display check;
- parameterized corpus packing.

Required changes:

- replace Arabic-block acceptance with the semantic inventory in
  `docs/warsh-script-codepoint-audit.md`;
- replace generic flagged-character deletion with the transform manifest;
- correct stale/incorrect metadata (`U+0656`, `U+06EC`, `U+06EA`, cleaned
  distinct count, and the small-mīm description);
- keep the font, raw source, and reports outside the runtime wheel;
- do not merge PR formatting churn in shared phoneme/muqattaʿāt resources as
  evidence of Warsh support.

## 11. Packaging

Only `quranic_phonemizer/data/**` ships. Package-data configuration must be
recursive for YAML/JSON/BIN files. Wheel and sdist are installed in clean
environments and smoke-tested for Hafs plus a Warsh source-normalization case.

Runtime imports from `corpora/`, `tools/`, `evidence/`, `research/`, `build/`,
or repository-relative paths are forbidden.

## 12. Migration order

1. Create the target folders and move evidence/research/tooling without
   changing runtime behavior.
2. Add corpus manifests and a reproducible Hafs build; import PR Warsh inputs
   under the same contract.
3. Add glyph-first shared/runtime schemas and validators only when their first
   consumer exists.
4. Implement Hafs and proved-Warsh source adapters.
5. Port one shared rule family end to end.
6. Port remaining Hafs behavior; replace generic contextual patches as their
   typed handlers land.
7. Switch to the new API/pipeline and remove old resources/re-derivers.
8. Add only researched Warsh policy/table/render deltas.
