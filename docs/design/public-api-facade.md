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
reading = reader.analyse("2:255", stop_refs=("2:255:35",))
```

The returned `Reading` is the one consumer surface. It exposes the eager core
and lazily builds the source, highlight, and cell projections:

```python
reading.text()
reading.phonemes()
reading.phonemes(by="word")
reading.words
reading.boundaries
reading.sounds
reading.rule_occurrences
reading.mergers
reading.source()
reading.highlights()
reading.cells(spelling="source")
reading.cells(spelling="transformed")
reading.document("analysis")
reading.document("cells")
```

This is a facade, not an adapter. It must return the existing native records,
preserve result-local IDs across every view, and make no semantic decisions
that are not already made by the producer.

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
- Do not change the schema-v1 wire vocabulary.
- Do not make the TypeScript renderer depend on Python package internals.

## Proposed public surface

### Construction

`Phonemizer` remains the configuration object for a riwayah, script, variant
selection, and extra phonemes. Add `analyse()` beside the existing
`phonemize()` method:

```python
reading = Phonemizer(
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
- `stop_signs`: named written-stop classes;
- `stop_refs`: word references at which to stop;
- `suspend_gc`: optional compatibility/performance control if retained by the
  existing high-level method.

The returned type is `Reading`. It is immutable from the caller's perspective;
projection caches are implementation details and do not alter its values.

### Core analysis

These properties return the existing native records:

```python
reading.words
reading.boundaries
reading.sounds
reading.rule_occurrences
reading.mergers
```

The following methods remain convenience readers over the same core:

```python
reading.text()                 # source spelling
reading.text("recited")        # performed spelling
reading.phonemes()             # performed order
reading.phonemes(by="word")   # primary word allocation
```

`reading.analysis` may expose the underlying `AnalysisResult` for callers who
need its complete metadata (`ref`, `riwayah`, `variant`, `canon_digest`, and
`schema_version`). It is not a second result or a copied ID space.

### Rules

The facade exposes the native catalogue and occurrences together without
requiring a second top-level import:

```python
reading.rule_catalogue
reading.rule_definition("idgham_bi_ghunnah")
reading.rule_occurrences
```

`rule_catalogue` is additive metadata and is not included in the versioned
analysis document. `rule_occurrences` remains the source of truth for what
actually happened in this request. A convenience iterator may be added if
experience shows that joining a definition to an occurrence is still too
verbose:

```python
for use in reading.rule_uses():
    print(use.definition.name, use.occurrence.sound_ids)
```

If `rule_uses()` is added, `use.definition` and `use.occurrence` must be views
over the existing records, not a new rule-classification system.

### Source characters and units

Source data is requested explicitly:

```python
source = reading.source()

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
for group in reading.highlights():
    print(group.unit_ids, group.sound_ids, group.ranges)
```

Highlight generation is selective and remains separate from cells. A caller
asking only for highlight ranges must not pay for transformed cell projection.

### Cells

```python
source_cells = reading.cells(spelling="source")
transformed_cells = reading.cells(spelling="transformed")
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
analysis_payload = reading.document("analysis")
source_payload = reading.document("source")
highlight_payload = reading.document("highlights")
cell_payload = reading.document("cells", spelling="transformed")
```

Each result is a JSON-compatible dictionary stamped with `schema_version`.
`document("all")` may return a dictionary containing the selected envelopes,
but it must not introduce a third top-level schema version. The existing
`analysis_document()`, `cell_document()`, and `serialize_document()` functions
remain available as low-level APIs.

The facade should also offer a typed document method if callers need to avoid
JSON conversion:

```python
reading.typed_document("cells")
```

The exact name is an implementation choice; the important contract is that
serialization and typed access share the same cached projection.

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

1. `reading.analysis.sounds` and every cell sound use the same sound IDs.
2. Source unit IDs are shared by source and both cell spellings.
3. Rule occurrence IDs are shared by analysis, source placements, and cells.
4. Merger IDs and endpoint placements are shared by analysis and cell bridges.
5. `reading.document("analysis")` equals serialization of
   `reading.analysis` under the native serializer.
6. `reading.document("cells", spelling="transformed")` equals serialization
   of `reading.cells(spelling="transformed")`.
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
from quranic_phonemizer import Phonemizer, Reading
```

The root package should export the facade type and the stable configuration
types needed to construct it. Native DTOs may continue to be exported from
`quranic_phonemizer.analysis` for typed specialist consumers.

The following remain non-primary implementation imports:

```python
quranic_phonemizer.session.phonemize_request
quranic_phonemizer.analysis.cells.view.build_cell_view
quranic_phonemizer.analysis.source.build_source_view
quranic_phonemizer.orthography.write.pen_for
```

They should not be removed in the facade release, but new documentation and
examples must stop teaching them as the normal workflow.

## Compatibility strategy

### Existing `phonemize()`

Keep `Phonemizer.phonemize()` in the first facade release. It returns the
existing `PhonemizeResult` and remains compatible with callers using
`text()`, `phonemes()`, `alignment()`, and `respelling()`.

Document `analyse()` as the canonical native API. Do not silently change the
return type of `phonemize()`.

In a later major release, `phonemize()` may delegate to the same internal
session builder, but it must continue to return its documented result type
until an explicit deprecation cycle is complete.

### Wire compatibility

The facade reads and emits schema version 1. A producer schema change still
requires a schema-version bump and the corresponding major version of
`quran-cells`. Rule catalogue additions remain outside the document version.

The website backend can replace its direct builder imports with the facade
without changing its response shape. The TypeScript package remains a parser
and renderer of `{ analysis, cells }`; it does not need to know whether the
payload came from the facade or the current backend composition.

## Migration sequence

### Step 1: Add the facade without changing builders

- Create `analysis/facade.py`.
- Add `Reading` and its private projection cache.
- Implement `Phonemizer.analyse()` using the existing request path.
- Export `Reading` and any public option aliases from the root package.

### Step 2: Centralize shared construction

- Refactor the facade's internal construction so `AnalysisResult`, source,
  highlights, and cells share one facts/inscription/bundle state.
- Keep existing builder functions callable and tested.
- Add internal helpers only where they remove duplicate work; do not expose
  builder implementation records through the facade.

### Step 3: Add typed and JSON document access

- Implement `document(kind, spelling=...)`.
- Reuse existing document constructors and serializers.
- Add closure tests for analysis, source, highlights, and cells.

### Step 4: Migrate the website backend

- Replace direct imports of `phonemize_request`, `build_result`, and
  `build_cell_view` in `app/main.py` with `Phonemizer` and `Reading`.
- Keep the response fields and stop semantics byte-compatible except for
  intentionally documented native fixes.
- Keep the backend's Digital Khatt override as host presentation data; it must
  not be written back into native transformed cells.

### Step 5: Rewrite public documentation

- Make `docs/public-api.md` lead with the facade.
- Move the builder recipe to an advanced implementation section.
- Add runnable examples for phonemes, characters, rules, mergers, source
  cells, transformed cells, and JSON documents.
- Link the Python facade guide to the `quran-cells` renderer consumer guide.

### Step 6: Deprecation review

- Measure whether any public caller still needs the old projection as a
  separate construction path.
- If appropriate, add a deprecation notice only after the facade has been
  released and exercised by the website and an external scratch consumer.

## Testing plan

### API shape tests

- `from quranic_phonemizer import Phonemizer, Reading` succeeds.
- `Phonemizer().analyse("1:1")` returns `Reading`.
- Every documented method returns the documented native type.
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

### Wire tests

- Every facade document has `schema_version == 1`.
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
- repeated calls on one `Reading` must be materially cheaper than the first;
- the facade must not retain unrelated passage state after the `Reading` is
  released.

## Acceptance criteria

The facade is ready when all of the following are true:

1. A normal consumer uses one root import and one `analyse()` call.
2. Phonemes, source characters, rules, mergers, and cells are each one or two
   obvious method/property accesses away.
3. No public example imports `phonemize_request`, `build_bundle`, `inscribe`,
   `build_source_view`, `build_cell_view`, or `pen_for`.
4. Native DTOs and IDs remain unchanged.
5. The website backend uses the facade without an adapter or response-shape
   change.
6. Existing `Phonemizer.phonemize()` callers continue to work.
7. The package and documentation explicitly distinguish eager core data from
   lazy selective projections.
8. The facade passes the full producer gates and the website's existing tests.

## Open decisions before implementation

These choices should be settled in the implementation PR, not by allowing
multiple competing public names:

1. `Reading` versus `Analysis` for the facade return type. `Reading` is the
   recommended name because it covers phonemes, source, boundaries, and cells
   without implying that cells are the whole result.
2. `document()` versus `wire()` for JSON-compatible envelopes. `document()` is
   recommended because the wire envelope is a document, not an arbitrary
   transport operation.
3. Whether `rule_uses()` is needed after real examples are written. Start with
   `rule_catalogue`, `rule_definition()`, and `rule_occurrences`; add the
   joined convenience only if it removes repeated consumer code.
4. Whether `highlights()` belongs in the first release or follows source and
   cells. The implementation should support it without making it mandatory in
   the initial facade surface.
