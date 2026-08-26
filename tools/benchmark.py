"""Reproducible timing and allocation benchmarks for the public facade."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import pathlib
import platform
import statistics
import sys
import time
import tracemalloc
from collections.abc import Callable

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from quranic_phonemizer import Phonemizer  # noqa: E402

DEFAULT_REFS = ("1:1:1", "1", "55")
CLOCK = time.process_time


def _timed(call: Callable, repeats: int, batch: int = 1):
    samples = []
    result = None
    for _ in range(repeats):
        gc.collect()
        started = CLOCK()
        for _ in range(batch):
            result = call()
        samples.append((CLOCK() - started) * 1_000 / batch)
    return statistics.median(samples), result


def _memory_bytes(call: Callable) -> tuple[int, int]:
    gc.collect()
    tracemalloc.start()
    result = call()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del result
    return current, peak


def _cached(call: Callable, repeats: int) -> float:
    call()
    return _timed(call, repeats, 100)[0]


def _projection_times(reader, ref: str, repeats: int) -> dict[str, float]:
    result = reader.analyse(ref)
    source_first, _ = _timed(result.source, 1)
    highlight_first, _ = _timed(result.highlights, 1)
    source_cells_first, _ = _timed(
        lambda: result.cells(spelling="source"), 1
    )
    transformed_first, _ = _timed(
        lambda: result.cells(spelling="transformed"), 1
    )
    return {
        "phonemes_cached_ms": _cached(result.phonemes, repeats),
        "source_first_ms": source_first,
        "source_cached_ms": _cached(result.source, repeats),
        "highlights_first_ms": highlight_first,
        "highlights_cached_ms": _cached(result.highlights, repeats),
        "source_cells_first_ms": source_cells_first,
        "source_cells_cached_ms": _cached(
            lambda: result.cells(spelling="source"), repeats
        ),
        "transformed_cells_first_ms": transformed_first,
        "transformed_cells_cached_ms": _cached(
            lambda: result.cells(spelling="transformed"), repeats
        ),
    }


def benchmark(refs: list[str], repeats: int) -> dict:
    started = CLOCK()
    reader = Phonemizer()
    init_ms = (CLOCK() - started) * 1_000
    cases = []
    for ref in refs:
        call = lambda ref=ref: reader.analyse(ref)
        result = call()
        batch = 100 if len(result.words) <= 4 else 10 if len(result.words) <= 50 else 1
        request_ms, result = _timed(call, repeats, batch)
        retained, peak = _memory_bytes(call)
        payload = json.dumps(
            result.document("analysis_result"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        cases.append({
            "ref": ref,
            "words": len(result.words),
            "sounds": len(result.sounds),
            "request_ms": request_ms,
            "retained_python_bytes": retained,
            "peak_python_bytes": peak,
            "analysis_sha256": hashlib.sha256(payload).hexdigest(),
            "projections_ms": _projection_times(reader, ref, repeats),
        })
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "clock": "process_time",
        "init_ms": init_ms,
        "repeats": repeats,
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("refs", nargs="*", default=DEFAULT_REFS)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(
        benchmark(args.refs, args.repeats), ensure_ascii=False, indent=2
    ))


if __name__ == "__main__":
    main()
