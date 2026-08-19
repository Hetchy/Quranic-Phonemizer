# Performance

This report compares pristine commit `b6f9ebc` with the optimized working
tree on 2026-08-18. Measurements used Python 3.13.3 on Windows 11. Request
and projection timings are median process CPU time, with garbage collection
before each sample. Small cases are batched to overcome the Windows process
clock's 15.625 ms resolution. Memory is Python allocation size measured by
`tracemalloc`, not process RSS.

Run the benchmark with:

```console
python tools/benchmark.py --repeats 3 --projection-repeats 3 \
  --fingerprint-internals --stages
```

Set `PHONEMIZER_BENCH_ROOT` to another checkout to compare implementations.
Add `--suspend-gc` to measure the explicit large-batch mode.

## End-to-end requests

All cases use one warmed `Phonemizer` and the default Hafs, Uthmani, connected
reading configuration.

| Reference | Words | Before | After | Speedup | Retained before | Retained after | Peak before | Peak after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `1:1:1` | 1 | 1.406 ms | 1.250 ms | 1.13x | 10.6 KiB | 9.9 KiB | 15.9 KiB | 14.9 KiB |
| `1` | 29 | 56.250 ms | 40.625 ms | 1.38x | 272.1 KiB | 258.3 KiB | 496.9 KiB | 475.0 KiB |
| `55` | 351 | 1,687.500 ms | 515.625 ms | 3.27x | 2.68 MiB | 2.49 MiB | 5.81 MiB | 5.46 MiB |

The increasing speedup is the intended result of removing quadratic work.
The 351-word request performs 69.4% less CPU work. Its retained result graph
uses 6.9% less Python memory and its request peak is 5.9% lower. Most retained
memory is the required public graph itself.

## Full Quran

A separate maximum-scale run phonemized `1-114` with one warmed facade and
sampled process RSS every 20 ms. It did not enable `tracemalloc`, profiling,
serialization, or any projection. The second run passed `suspend_gc=True`;
all public graph counts and the canonical digest were identical.

| Measure | Default | Suspended GC |
| --- | ---: | ---: |
| Words | 77,433 | 77,433 |
| Request CPU time | 252.719 s | 174.500 s |
| Elapsed time on the contended host | 352.913 s | 182.124 s |
| CPU time per word | 3.264 ms | 2.254 ms |
| Baseline process RSS | 33.6 MiB | 33.3 MiB |
| Returned-result process RSS | 872.8 MiB | 870.6 MiB |
| Increment retained by the result | 839.2 MiB | 837.4 MiB |
| Peak process RSS | 1,192.1 MiB | 1,186.4 MiB |
| Incremental peak | 1,158.5 MiB | 1,153.1 MiB |

Suspending collection removes 31.0% of request CPU work, a 1.45x speedup,
without increasing peak memory. The elapsed-time comparison is less reliable
than process CPU because the two runs saw different host contention.

The returned document contains 715,856 source glyphs, 728,878 rendered glyphs,
287,057 canonical units, 479,954 sounds, 149,352 rule instances, 788,030
spelling edges, 519,297 attribution edges, and 71,957 modifier edges. A caller
that needs this single index space should budget at least 1.3 GiB of available
memory plus application headroom. A caller that only needs corpus-wide derived
values should request surahs or smaller spans separately so each rich result
can be released before the next one.

The option is explicit because CPython cyclic GC is process-global. Nested and
concurrent opted-in calls are reference-counted and the previous collector
state is restored after the last one exits, including on failure. Unrelated
cycles created by other threads are nevertheless retained until then.

## Profile by pipeline stage

The 351-word case isolates the regression clearly.

| Stage | Before | After | Change |
| --- | ---: | ---: | ---: |
| Read orthography | 46.875 ms | 46.875 ms | unchanged |
| Build canonical score | 906.250 ms | 109.375 ms | 8.29x faster |
| Perform rules | 453.125 ms | 125.000 ms | 3.63x faster |
| Assemble public graph | 250.000 ms | 218.750 ms | 1.14x faster |

Reference resolution, boundary planning, labeling, and result wrapping are
each below one process-clock tick at this scale.

The original profiler recorded 2,016,144 calls to `word_of`, 518,339 full
effect-journal iterations, and 1,681 full grapheme-bound scans for this one
request. The optimized profile removes those repeated scans. Canonical passes
group drafts once, merge/silence checks use an indexed set, word bounds are
built once, and neighborhood and public-assembly lookups use canonical
ordinals instead of duplicate identifier dictionaries.

## Projections

Projection timings use the already-built 351-word result.

| Projection | Before | After |
| --- | ---: | ---: |
| Source alignment, glyph | 98.438 ms | 93.750 ms |
| Source alignment, cell | 95.313 ms | 85.938 ms |
| Recited alignment, glyph | 78.125 ms | 65.625 ms |
| Recited alignment, cell | 64.063 ms | 56.250 ms |
| Respelling | 171.875 ms | 170.313 ms |
| Canonical serialization | 142.188 ms | 154.688 ms |

Alignment now builds its part indices in one traversal and derives each
pairing's presented sounds and rules together. Canonical serialization was
not changed; its observed difference is benchmark variation on a saturated
host rather than a changed algorithm or document.

## Repeated construction

Ten additional `Phonemizer` instances previously reparsed and retained
53,025,675 bytes of duplicate resources and used 15,828 ms of process CPU
under `tracemalloc`. They now retain 32,616 bytes and complete below one
15.625 ms clock tick. Corpus, ledger, lexicon, khilaf, rule tables, inventories,
and alphabet data are shared process-locally; each facade and its mutable
adapter mapping remain distinct.

## Equivalence

The benchmark fingerprints both the complete internal `Session` representation
and the canonical public bytes. Before and after hashes match at every scale:

| Reference | Internal session SHA-256 | Canonical public SHA-256 |
| --- | --- | --- |
| `1:1:1` | `72432d009d6f50daacd303bc9d1b184b636e19ea2e837462d3f26c56ab29e77c` | `7d753d9aace567dbfe30b28e9feb8d41b466af56a629bf332a270a8203304f0f` |
| `1` | `b661ceb35dedf8cdda522797dc8d572685b1eb5d9e2fb87472cae465eea81247` | `d0baae8895b4c69373850e770110a0b1e5d72519d578a545bf3cd81f38b1a319` |
| `55` | `74b742f78046e15cf4d94a6cf5be1b09e7fbbfc2d54ec33c6ea64f2985c40447` | `00adc139c37042375b0ded6d5438b60a5634588aa4e5748f02b88e032d697186` |

These fingerprints cover canonical units, inscription edges, performed
sounds, rule occurrences, attributions, modifiers, boundaries, every public
node and edge array, rendered text, labels, phoneme tokens, and metadata.
Repository gates remain the corpus-wide compatibility check.

The final `python tools/gates.py` run passed all registered gates: 1,338 unit
and law tests, comment and structure lint, 77,433-word cross-script and frozen
regression comparisons, 6,236-verse round-trip, attestation ratchets, and the
287,057-slot canonical agreement ratchet. Every existing floor, ceiling, and
residue was unchanged.
