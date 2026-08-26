# Performance

The public facade separates eager analysis from lazy selective projections.
Measure the operation your consumer actually performs rather than assuming a
cell-heavy request represents a phoneme-only caller.

## Reproducible benchmark

From the repository root:

```bash
python tools/benchmark.py
python tools/benchmark.py 1:1 2:255 55 --repeats 5
```

The JSON report records:

- Python and platform details;
- reader construction time;
- median eager `analyse()` time and Python allocation measurements;
- the schema-v2 analysis document digest;
- first and cached timings for source, highlights, source cells, and
  transformed cells.

Use `python tools/compare_perf.py <base> [<candidate>]` to compare two git
revisions on the same host. It alternates execution order and reports a
regression when the median request ratio exceeds the configured tolerance.

## Work performed by each call

| Call | Work |
| --- | --- |
| `reader.analyse(ref)` | Reference resolution, canonical build, boundary resolution, performance, native facts, inscription facts, bundle, and `AnalysisResult`. |
| `result.phonemes()` | Reads eager core tokens only. |
| `result.source()` | Builds and caches source characters, units, and placements. |
| `result.highlights()` | Reuses the source view and builds highlight groups. |
| `result.cells(spelling="source")` | Reuses shared state and builds native source cells. |
| `result.cells(spelling="transformed")` | Reuses shared state and applies the configured pen to native cells. |
| `result.document(kind)` | Builds only the selected typed projection, then serializes its native envelope. |

The projection cache is result-local and guarded for concurrent access.
Repeated calls return the same immutable value and do not rerun the engine or
boundary resolver.

## Large requests

One whole-surah or whole-Quran request keeps its complete score, inscription,
performance, bundle, and any requested projection cache alive for as long as
the `Result` remains reachable. Prefer verse or bounded-range requests unless
cross-verse behavior requires a larger span. Do not request transformed cells
for a caller that only needs phonemes or continuous-text highlights.

When comparing retained memory, release the result and run collection before
measuring the next case. Loaded riwayah resources and the alphabet are cached
process-locally and intentionally remain shared across readers.
