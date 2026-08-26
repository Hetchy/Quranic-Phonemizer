# Public API facade plan

## Decision summary

The native projection has the right ownership and identity model, but its
construction recipe is too low-level for a public API. A caller should not
assemble a `Recitation`, `Session`, `AnalysisBundle`, `SourceView`, and
`CellView` by hand just to ask one question about a passage.

Add one root-package facade:

```python
from quranic_phonemizer import Phonemizer

reader = Phonemizer(
    extra_phonemes=(
        "emphatic_fatha",
        "emphatic_ikhfaa",
        "imala",
        "tashil",
    )
)
result = reader.analyse("2:255", stop_refs=("2:255:35",))
```

The returned `Result` is the one consumer surface. It exposes the eager core
and lazily builds the source, highlight, and cell projections:

```python
result.text()
result.phonemes()
result.phonemes(by="word")
result.words
result.boundaries
result.sounds
result.rule_occurrences
result.mergers
result.source()
result.highlights()
result.cells(spelling="source")
result.cells(spelling="transformed")
result.document("analysis_result")
result.document("cell_view", spelling="transformed")
```

This is a facade, not an adapter. It must return the existing native records,
preserve result-local IDs across every view, and make no semantic decisions
that are not already made by the producer.

### Standing relative to the native projection plan

This document changes the migration path in
`consumer-analysis-projection.md`, not its native DTO semantics. `analyse()`
is added and proved while the old projection remains available as differential
evidence. Once the facade and website equivalence gates pass, the pre-release
cutover removes `phonemize()`, `PhonemizeResult`, the public graph exports, and
the obsolete alignment, respelling, and general recited-text projections.
There is no deprecation cycle for an unreleased API.

Where the two documents disagree about the entry point or cutover timing, this
facade plan is authoritative. The native ownership, identity, boundary,
source, highlight, cell, and schema laws remain authoritative in the earlier
projection plan.

## Problem

The current native modules are intentionally separated:

| Concern | Current implementation seam |
| --- | --- |
| Riwayah and script loading | `api.recitation`, `model.address` |
| Request and boundary resolution | `session.phonemize_request` |
| Core analysis | `analysis.result.build_result` |
| Source characters and units | `analysis.source.build_source_view` |
| Highlight groups | `analysis.highlights.highlight_groups` |
| Educational cells | `analysis.cells.view.build_cell_view` |
| Transformed spelling | `orthography.write.pen_for` |
| JSON envelopes | `analysis.schema.*` |

Those boundaries are useful inside the package. They are not a suitable
consumer workflow. The existing documentation therefore makes simple tasks
look like dependency injection and implementation archaeology. In particular,
consumers should never need to know that transformed cells require a `Pen`, or
that source views need an `AnalysisBundle` and `InscriptionFacts`.

The facade must hide those details without collapsing the projections into one
untyped mega-object or making cells mandatory for phoneme-only callers.

## Goals

1. Provide one supported import for ordinary Python consumers.
2. Make phonemes, words, boundaries, sounds, rules, mergers, characters,
   highlights, and cells independently reachable.
3. Build each projection at most once and only when requested.
4. Keep one shared request/session and one result-local ID space.
5. Hide renderer construction details such as `pen_for`.
6. Make native JSON documents available without importing serializer modules.
7. Keep the wire schema and the `quran-cells` TypeScript consumer unchanged.
8. Leave advanced low-level modules available for maintainers and specialist
   consumers without presenting them as the normal path.

## Non-goals

- Do not add an adapter that changes native semantics.
- Do not merge source, analysis, and cell DTOs into one record shape.
- Do not make the rule catalogue part of the schema-versioned documents.
- Do not make cells or source tokenization part of a phoneme-only request.
- Do not infer rules, folds, mergers, silence, or transformed spelling in the
  facade.
- Do not change the schema-v2 wire vocabulary. Correctly classifying an authored
  Warsh stop mark with the existing `stop_sign` kind and boundary fields is a
  conformance repair, not a new wire concept.
- Do not make the TypeScript renderer depend on Python package internals.

## Proposed public surface

### Construction

`Phonemizer` remains the configuration object for a riwayah, script, variant
selection, and extra phonemes. Add `analyse()` beside the existing
`phonemize()` method:

```python
result = Phonemizer(
    riwayah="hafs",
    script="uthmani",
    variants={"iqlab_nasal": "bilabial"},
    extra_phonemes=("emphatic_fatha", "imala"),
).analyse(
    "2:255",
    stop_signs=("preferred_stop",),
)
```

The request arguments mirror `phonemize()`:

- `ref`: one word, verse, or verse range;
- `stop_signs`: configuration-scoped stop-advice names;
- `stop_refs`: word references at which to stop.

The returned type is `Result`. It is immutable from the caller's perspective;
projection caches are implementation details and do not alter its values.

### Configuration-scoped catalogues

Stop-sign classes, variants, and rules belong to the configured `Phonemizer`.
The facade must never expose the union of values packaged for every riwayah or
script:

```python
reader = Phonemizer(riwayah="hafs", script="uthmani")

reader.available_stop_signs
reader.available_variants
reader.tajweed_rules
```

`available_stop_signs` returns the names accepted by this reader's
`stop_signs` request argument. Every reader includes the synthetic `verse`
selector. The remaining names come from the selected `(riwayah, script)`
inventory, not from a process-wide enum: each script authors its own subset
and scalar mapping.
`available_variants` lists only the selected riwayah's khilaf points and
choices. `tajweed_rules` lists only rules the selected riwayah declares it can
emit, followed by its published silence reasons.

The currently packaged stop-sign catalogues are explicit contract fixtures:

```python
Phonemizer(riwayah="hafs", script="uthmani").available_stop_signs
# (
#     "verse", "preferred_continue", "preferred_stop", "optional_stop",
#     "compulsory_stop", "prohibited_stop", "either_stop",
# )

Phonemizer(riwayah="hafs", script="indopak").available_stop_signs
# the same seven names plus "permitted_stop"

Phonemizer(riwayah="warsh", script="uthmani").available_stop_signs
# ("verse", "optional_stop")
```

The packaged Warsh Uthmani source contains U+06D6 `ۖ` 9,948 times. It is a
written stop sign and must not disappear into the generic structural-separator
category. Warsh authors it as `optional_stop`; that semantic API name is how a
caller addresses it with `stop_signs=("optional_stop",)`. The resulting
boundary exposes the exact `stop_sign="ۖ"` and
`stop_advice=StopAdvice.OPTIONAL_STOP`. `stop_refs` remains available for
explicit word-addressed stops.

`verse` restores the legacy cross-ayah behavior without pretending that an
ayah boundary is an inventory-authored stop-advice glyph. It stops after each
selected source ayah in a multi-ayah request.

The existing root functions may remain as explicit metadata queries:

```python
available_stop_signs("hafs", script="uthmani")
available_variants("hafs")
tajweed_rules("hafs")
```

The configured properties and root functions must return equivalent values.
Invalid request values must be reported against the applicable selected
catalogue: `(riwayah, script)` for stop signs and `riwayah` for variants and
rules.

An unavailable stop class is an error even if another packaged configuration
uses the same name. Validation happens before boundary resolution:

```python
Phonemizer(riwayah="warsh").analyse(
    "1:1",
    stop_signs=("preferred_stop",),
)
# UnknownStopSign: ['preferred_stop'] is not available for warsh/uthmani;
# available stop signs: ['verse', 'optional_stop']
```

`UnknownStopSign` is a public `ValueError`. Multiple unknown or unavailable
names are reported together in sorted order. An empty tuple is always valid;
invalid `stop_refs` continue to use the existing reference errors.

### Core analysis

These properties return the existing native records:

```python
result.words
result.boundaries
result.sounds
result.rule_occurrences
result.mergers
```

The following methods remain convenience readers over the same core:

```python
result.text()                 # exact source spelling only
result.phonemes()             # performed order
result.phonemes(by="word")   # primary word allocation
```

There is no general recited or performed text. Transformed spelling is exposed
only by `result.cells(spelling="transformed")`, where every change has a native
cell status and provenance.

`result.analysis` may expose the underlying `AnalysisResult` for callers who
need its complete metadata (`ref`, `riwayah`, `variant`, `canon_digest`, and
`schema_version`). It is not a second result or a copied ID space.

### Boundaries

`result.boundaries` contains `N + 1` resolved boundaries for `N` words. These
are results, not a menu of options:

| State | Meaning |
| --- | --- |
| `start` | Leading request boundary before the first word. |
| `join` | Ordinary continuation across an internal boundary. |
| `sakt` | An authored breathless pause; it blocks cross-boundary interaction without applying waqf or ibtidaa. |
| `stop` | Waqf before the boundary; at an internal boundary it also implies ibtidaa on the following word. The trailing request boundary is always `stop`. |

Each boundary names its `before` and `after` word IDs, exact written
`stop_sign` if one exists, and riwayah-authored `stop_advice` if one exists.
Public documentation must show ordinary join, an explicit `stop_refs` stop, a
stop selected through a configuration-scoped `stop_signs` option, authored
sakt, and the trailing stop. It must state that callers request stops but never
request `sakt`; sakt is authored by the riwayah.

For Warsh, a boundary carrying `ۖ` is therefore represented even when the
caller does not select it: `stop_sign="ۖ"`,
`stop_advice=StopAdvice.OPTIONAL_STOP`, and state `join`. Selecting
`optional_stop` changes the applicable internal boundary state to `stop`.

### Rules

The facade exposes the native catalogue and occurrences together without
requiring a second top-level import:

```python
result.rule_catalogue
result.rule_definition("idgham_bi_ghunnah")
result.rule_occurrences
```

`rule_catalogue` is the selected riwayah's catalogue, equivalent to the
configured reader's `tajweed_rules`; it never exposes the combined inventory.
It is additive metadata and is not included in the versioned analysis
document. `rule_occurrences` remains the source of truth for what actually
happened in this request.

An occurrence may name both visible units and sounds because those fields
answer different questions: where the rule is placed in the source, and which
performed sounds it classified or changed. For example, today's native Hafs
contract places `lam_shamsiyyah` on the silent article lam and also names the
resulting doubled sun-letter sound. A cell renderer may choose to draw the
teaching label only on the letter row, but must not reinterpret the occurrence
or erase its affected-sound relationship.

### Source characters and units

Source data is requested explicitly:

```python
source = result.source()

for character in source.characters:
    print(character.index, character.text, character.kind)

for unit in source.units:
    print(unit.text, unit.kind, unit.silence, unit.rule_occurrence_ids)
```

`source()` returns the existing `SourceView`. It must not manufacture cells or
reconstruct transformed spelling. `characters` are exact source scalars;
`units` are the producer's tokenized letter-level surface.

### Highlights

```python
for group in result.highlights():
    print(group.unit_ids, group.sound_ids, group.ranges)
```

Highlight generation is selective and remains separate from cells. A caller
asking only for highlight ranges must not pay for transformed cell projection.

### Cells

```python
source_cells = result.cells(spelling="source")
transformed_cells = result.cells(spelling="transformed")
```

The facade owns the transformed-spelling pen internally. It chooses the pen
from the configured riwayah and script inventory and passes it to the native
cell builder. The caller never imports `pen_for`.

The two views remain producer-native `CellView` values. In particular:

- `status` is `present`, `inserted`, `replaced`, `dropped`, or `gap`;
- `role`, `tier`, and `attached_to_column_id` are producer fields;
- `CellBoundary.bridges` contains genuine shared merger sounds;
- sukun, maddah, dagger alif, maqsura folds, and boundary insertions are not
  re-derived by the facade.

### Versioned documents

Expose the existing wire envelopes through one method:

```python
analysis_payload = result.document("analysis_result")
source_payload = result.document("source_view")
highlight_payload = result.document("highlight_groups")
cell_payload = result.document("cell_view", spelling="transformed")
```

The four names deliberately retain the existing schema vocabulary:

| Kind | JSON envelope contents | Typical consumer |
| --- | --- | --- |
| `analysis_result` | Request metadata, source text, words, resolved boundaries, sounds, rule occurrences, and mergers. | NLP, speech, search, and general analysis. |
| `source_view` | Exact Unicode characters, producer-tokenized letter units, silence, and rule/merger placements. | Source-text inspection and annotation. |
| `highlight_groups` | Source ranges and unit IDs grouped by the sound IDs that activate them. | Audio-timed continuous-text highlighting. |
| `cell_view` | Source or transformed educational columns, sound cells, groups, runs, boundary columns, and merger bridges. | Tajweed tables and interactive teaching renderers. |

Each call returns a JSON-compatible dictionary stamped with `schema_version`.
Typed consumers already use `result.analysis`, `result.source()`,
`result.highlights()`, and `result.cells()`, so there is no `typed_document()`.
There is no `document("all")`; a caller requests only the envelope it needs.
The existing `analysis_document()`, `source_document()`,
`highlight_document()`, `cell_document()`, and `serialize_document()`
functions remain available as low-level APIs.

## Internal design

### Facade state

Add a small module, preferably `quranic_phonemizer/analysis/facade.py`, with a
private state object containing:

```text
session        resolved Session
facts          optional AnalysisFacts
inscription    optional InscriptionFacts
bundle         optional AnalysisBundle
analysis       eager AnalysisResult
source         cached SourceView
highlights     cached HighlightGroup tuple
cells[source]  cached CellView
cells[transformed] cached CellView
```

The exact fields may be lazy, but all projections must reuse the same session,
facts, inscription, bundle, and native IDs. A second call to `cells()` must
return the same value or an equivalent immutable value without recomputing it.

### Eager versus lazy work

`analyse()` must resolve boundaries and build the core `AnalysisResult`, because
that is the object that proves the request and its IDs. The following work is
lazy:

| Call | Required work |
| --- | --- |
| `phonemes()` | Core result only |
| `source()` | Source tokenization and source view |
| `highlights()` | Source view plus highlight grouping |
| `cells("source")` | Native source cells |
| `cells("transformed")` | Source cells plus transformed projection and pen |
| `document(kind)` | The corresponding typed projection, then serialization |

The implementation may build shared `facts`, `inscription`, and `bundle` on
the first source/cell request. It must not rebuild the session or call the
recitation engine a second time.

### Projection identity laws

The facade tests must enforce:

1. `result.analysis.sounds` and every cell sound use the same sound IDs.
2. Source unit IDs are shared by source and both cell spellings.
3. Rule occurrence IDs are shared by analysis, source placements, and cells.
4. Merger IDs and endpoint placements are shared by analysis and cell bridges.
5. `result.document("analysis_result")` equals serialization of
   `result.analysis` under the native serializer.
6. `result.document("cell_view", spelling="transformed")` equals serialization
   of `result.cells(spelling="transformed")`.
7. Request options are reflected identically in every projection.

### Errors

The facade should preserve existing domain errors for invalid references,
riwayat, scripts, variants, extra phonemes, and stop requests. It should add
only narrow argument errors for:

- an unknown document kind;
- an invalid cell spelling;
- an unsupported rule lookup.

No error should mention internal builders such as `build_bundle` or `pen_for`.

## Root exports

The ordinary path should be:

```python
from quranic_phonemizer import Phonemizer, Result
```

The root package should export the facade type and the stable configuration
types needed to construct it. Native DTOs may continue to be exported from
`quranic_phonemizer.analysis` for typed specialist consumers.

The following remain private implementation imports while their native
builders still have maintainers and tests as callers:

```python
quranic_phonemizer.session.phonemize_request
quranic_phonemizer.analysis.cells.view.build_cell_view
quranic_phonemizer.analysis.source.build_source_view
quranic_phonemizer.orthography.write.pen_for
```

They are not root exports, and public documentation must not teach them as the
normal workflow. Builder modules with no remaining internal caller after the
website migration are deleted in the cutover rather than retained as a second
public construction recipe.

## Cutover strategy

### Legacy projection

Keep the old projection only while it is needed for differential checks during
implementation. Once the facade, website, and wire-equivalence gates pass,
remove `Phonemizer.phonemize()`, `PhonemizeResult`, the root `edges` and `nodes`
exports, and the alignment, respelling, and general recited-text projection
modules. The package is pre-release, so there is no deprecation stage and no
release carrying two supported public architectures.

### Wire compatibility

The facade reads and emits the current schema version 2. A producer schema
change still
requires a schema-version bump and the corresponding major version of
`quran-cells`. Rule catalogue additions remain outside the document version.

The website backend can replace its direct builder imports with the facade
without changing its response shape. The TypeScript package remains a parser
and renderer of `{ analysis, cells }`; it does not need to know whether the
payload came from the facade or the current backend composition.

## Migration sequence

### Step 1: Centralize shared construction

- Repair the Warsh Uthmani inventory/projection seam first: author U+06D6 `ۖ`
  as `OPTIONAL_STOP` instead of a generic structural mark and project it as a
  `stop_sign` source character owned by its boundary.
- Prove on corpus and focused fixtures that all 9,948 Warsh occurrences remain
  exact source text, become typed stop signs rather than generic separators,
  and make an internal boundary stop only when `verse`, `optional_stop`, or an
  explicit `stop_refs` request applies; the passage-final boundary retains its
  ordinary mandatory stop.
- Refactor internal construction so `AnalysisResult`, source,
  highlights, and cells share one facts/inscription/bundle state.
- Keep existing builder functions callable and tested.
- Add internal helpers only where they remove duplicate work; do not expose
  builder implementation records through the facade.
- Prove that the shared path is value-identical to today's independent builders
  before exposing it publicly.

This is mostly orchestration because `build_bundle()` and
`build_source_view()` already accept shared facts and inscription. The cell
builder is the remaining seam: today it creates its own facts, inscription,
bundle, and source view. Refactoring that seam has correctness risk if a view
uses different extra-phoneme rendering, transformed pen, or result-local IDs,
and performance risk if a cache retains more passage state than the requested
projection needs. Equivalence, call-count, retained-memory, and concurrent
access tests are therefore part of this step rather than deferred facade tests.

### Step 2: Add the facade over shared construction

- Create `analysis/facade.py`.
- Add `Result` and its private projection cache.
- Implement `Phonemizer.analyse()` using the shared request path.
- Export `Result` and any public option aliases from the root package.

### Step 3: Add catalogues, errors, and JSON document access

- Add the configuration-scoped stop-sign, variant, and rule catalogues.
- Add `UnknownStopSign` and validate requested stop classes before boundary
  resolution.
- Implement `document(kind, spelling=...)`.
- Reuse existing document constructors and serializers.
- Add closure tests for analysis, source, highlights, and cells.

### Step 4: Migrate the website and prove equivalence

- In `C:/Users/ahmed/Documents/Work/my-projects/phonemizer-web`, replace the
  backend's direct imports of `phonemize_request`, `build_result`,
  `build_cell_view`, `pen_for`, and serializer composition with
  `Phonemizer.analyse()` and `Result.document()`.
- Preserve the `/api/analyse` response fields and values for the same riwayah,
  reference, stop plan, variants, and extra phonemes. The facade migration is
  wiring, not a website API redesign.
- Replace the website's process-wide default stop list with names from the
  configured `reader.available_stop_signs`. Preserve today's Hafs defaults.
  Publish `verse` for every reader and Warsh `optional_stop` as the name for
  its `ۖ` glyph; the UI may submit either class or explicit word stops.
- Publish the selected configuration's stop-sign, variant, and rule catalogues
  from `/api/meta`; the frontend must not reuse the Hafs catalogue for Warsh.
- Keep the backend's Digital Khatt override as host presentation data; it must
  not be written back into native transformed cells.
- Record old and facade responses for representative Hafs and Warsh passages,
  default and explicit stops, authored sakt, mergers, and transformed cells.
  Compare the full `analysis` and `cells` documents plus website `text`,
  `phonemes`, `stops`, and `dk`; every difference must be zero or an explicitly
  reviewed native correction.
- Run the website package parser, unit tests, build, layout audit, and browser
  sweep against the facade backend before removing the old path.

### Step 5: Cut over and document the public API

- Remove the legacy `phonemize()` public surface and every old projection module
  with no remaining internal caller.
- Make `README.md` the concise quick start and make `docs/public-api.md` the
  concise but comprehensive contract for construction, scoped catalogues,
  errors, core records, boundaries, source, highlights, cells, and documents.
- Include only small runnable snippets needed to explain each surface. Detailed
  generated examples, tutorials, and presentation walkthroughs belong in
  future README or consumer documentation, not this implementation step.
- Link to the `quran-cells` renderer contract without duplicating its layout or
  presentation documentation.

## Testing plan

### API shape tests

- `from quranic_phonemizer import Phonemizer, Result` succeeds.
- `Phonemizer().analyse("1:1")` returns `Result`.
- Every documented method returns the documented native type.
- configured and root stop-sign catalogues agree for every packaged
  `(riwayah, script)`;
- configured and root variant and rule catalogues agree for every packaged
  riwayah;
- no configured catalogue includes a value belonging only to another
  configuration;
- Warsh Uthmani publishes `verse` plus `optional_stop` for `ۖ`, accepts both
  selectors, reports the glyph and `StopAdvice.OPTIONAL_STOP` on the native
  boundary, and continues to accept valid `stop_refs`;
- requesting `preferred_stop` for Warsh raises `UnknownStopSign` and reports
  `verse` and `optional_stop` as the exact available classes;
- an invalid stop class for Hafs reports the selected script and the exact
  available values;
- Invalid arguments raise stable, user-facing errors.

### Projection tests

For representative passages including `1:1`, `2:2`, `2:255`, `3:103`,
`9:1`, `11:41`, `36:52`, and `43:65`:

- phoneme order matches the core sound order;
- word grouping follows primary sound ownership;
- source characters reproduce source text exactly;
- rules resolve from native occurrence IDs;
- mergers expose both endpoint words and one shared sound;
- source and transformed cells differ only where native statuses say they do;
- `source()` does not build cells;
- repeated projection calls reuse the cached values;
- all stop plans preserve shared IDs where the producer contract requires it.
- Warsh U+06D6 characters are `stop_sign` characters owned by the matching
  boundaries, never lexical units or generic separators.

### Wire tests

- Every facade document has `schema_version == 2`.
- The analysis and cell envelopes share sound, word, boundary, and rule IDs.
- Transformed cell serialization includes `inserted`, `replaced`, `dropped`, and
  `gap` statuses without frontend reconstruction.
- A schema mismatch remains the responsibility of the TypeScript consumer's
  `parse()` guard, not the facade.

### Consumer smoke test

Use a scratch Python script with only:

```python
from quranic_phonemizer import Phonemizer
```

The script must obtain phonemes, rules, source characters, a merger, and
transformed cells without importing any submodule. Serialize the result and
feed it to the published `quran-cells` parser in the existing TypeScript
fixture test.

### Performance test

Compare the facade against the current direct builder path:

- phoneme-only calls must not construct cells;
- source-only calls must not construct transformed cells;
- requesting all projections must not rerun boundary resolution or the engine;
- repeated calls on one `Result` must be materially cheaper than the first;
- the facade must not retain unrelated passage state after the `Result` is
  released.

## Acceptance criteria

The facade is ready when all of the following are true:

1. A normal consumer uses one root import and one `analyse()` call.
2. Phonemes, source characters, rules, mergers, and cells are each one or two
   obvious method/property accesses away.
3. No public example imports `phonemize_request`, `build_bundle`, `inscribe`,
   `build_source_view`, `build_cell_view`, or `pen_for`.
4. Native DTOs and IDs remain unchanged.
5. Stop-sign catalogues and validation are scoped by `(riwayah, script)`;
   every reader exposes `verse`; variant and rule catalogues are scoped by
   riwayah; Warsh Uthmani exposes `optional_stop` for `ۖ` and supports that
   class, `verse`, and `stop_refs` for requested stops.
6. The website backend uses only the facade and produces equivalent analysis,
   cells, text, phonemes, stops, and Digital Khatt data for the same requests.
7. `phonemize()`, `PhonemizeResult`, public graph exports, alignment,
   respelling, and general recited-text projections are absent from the shipped
   package.
8. The package and documentation explicitly distinguish eager core data from
   lazy selective projections.
9. `document()` supports all four existing schema kinds and `highlights()` is
   included in the first facade release.
10. The facade passes the full producer gates and the website parser, unit,
    build, layout, and browser gates.

## Resolved surface decisions

- The JSON-compatible envelope method is `document()`.
- `highlights()` is included in the first release.
