"""Reproducible time and Python-allocation benchmarks for public requests."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import pathlib
import platform
import statistics
import sys
import time
import tracemalloc
from collections.abc import Callable

ROOT = pathlib.Path(os.environ.get(
    "PHONEMIZER_BENCH_ROOT", pathlib.Path(__file__).resolve().parent.parent
))
sys.path.insert(0, str(ROOT))

from quranic_phonemizer import Phonemizer  # noqa: E402
from quranic_phonemizer.phonemize import names  # noqa: E402
from quranic_phonemizer.phonemize.assemble import assemble  # noqa: E402
from quranic_phonemizer.session import resolve_boundaries  # noqa: E402
from quranic_phonemizer.phonemize.document import build_result  # noqa: E402
from quranic_phonemizer.session import resolve_words  # noqa: E402
from quranic_phonemizer.session import phonemize_request  # noqa: E402
from quranic_phonemizer.session import Session  # noqa: E402
from quranic_phonemizer.phonemize.schema import canonical_bytes  # noqa: E402


DEFAULT_REFS = ("1:1:1", "1", "55")
CLOCK = time.process_time


def _timed(call: Callable, repeats: int, batch: int = 1) -> tuple[float, object]:
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


def _constructor_scale(count: int) -> dict[str, float | int]:
    gc.collect()
    tracemalloc.start()
    started = CLOCK()
    instances = [Phonemizer() for _ in range(count)]
    elapsed = (CLOCK() - started) * 1_000
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del instances
    return {"count": count, "ms": elapsed, "bytes": current, "peak_bytes": peak}


def _stage_times(phonemizer, ref: str, repeats: int) -> dict[str, float]:
    names_ = (
        "resolve", "corpus", "read", "build", "boundaries", "perform",
        "assemble", "result",
    )
    samples = []
    for _ in range(repeats):
        gc.collect()
        points = [CLOCK()]
        recitation = phonemizer._recitation
        locations = resolve_words(recitation.corpus, recitation.ledger, ref)
        points.append(CLOCK())
        words = tuple(
            (location, recitation.corpus.word(location)) for location in locations
        )
        points.append(CLOCK())
        reading = recitation.read(phonemizer._script, locations[0].verse, words)
        points.append(CLOCK())
        built = recitation.build(reading, selection=phonemizer._selection)
        points.append(CLOCK())
        boundaries = resolve_boundaries(
            built.inscription.advice, locations, built.score
        )
        points.append(CLOCK())
        performance = recitation.perform(
            built.score, boundaries, selection=phonemizer._selection
        )
        points.append(CLOCK())
        session = Session(
            locations, built.score, built.inscription, boundaries, performance
        )
        assembled = assemble(
            session, phonemizer._pen, phonemizer._alphabet,
            extra_phonemes=phonemizer._extra,
        )
        points.append(CLOCK())
        build_result(
            ref=ref, riwayah=phonemizer.riwayah,
            script=phonemizer._script.value,
            variant=names.resolved_variant(
                recitation.khilaf, phonemizer._selection
            ),
            extra_phonemes=phonemizer._extra,
            canon_digest=session.score.digest,
            assembled=assembled,
        )
        points.append(CLOCK())
        samples.append([
            (points[index + 1] - points[index]) * 1_000
            for index in range(len(names_))
        ])
    return {
        name: statistics.median(values)
        for name, values in zip(names_, zip(*samples))
    }


def _projection_times(result, repeats: int) -> dict[str, float]:
    calls = {
        "phonemes": lambda: result.phonemes(),
        "phonemes_by_word": lambda: result.phonemes("word"),
        "source_text": lambda: result.text(),
        "recited_text": lambda: result.text("recited"),
        "source_alignment_glyph": lambda: result.alignment(),
        "source_alignment_cell": lambda: result.alignment(grouping="cell"),
        "recited_alignment_glyph": lambda: result.alignment(text="recited"),
        "recited_alignment_cell": lambda: result.alignment(
            text="recited", grouping="cell"
        ),
        "respelling": lambda: result.respelling(),
        "canonical_bytes": lambda: canonical_bytes(result),
    }
    batch = 100 if len(result.words) <= 50 else 10
    return {
        name: _timed(call, repeats, batch)[0] for name, call in calls.items()
    }


def benchmark(
    refs: list[str], repeats: int, projection_repeats: int, internals: bool,
    stages: bool, constructors: int, suspend_gc: bool,
) -> dict:
    started = CLOCK()
    phonemizer = Phonemizer()
    init_ms = (CLOCK() - started) * 1_000
    started = CLOCK()
    Phonemizer()
    warm_init_ms = (CLOCK() - started) * 1_000
    cases = []
    for ref in refs:
        call = lambda ref=ref: phonemizer.phonemize(
            ref, suspend_gc=suspend_gc
        )
        result = call()
        request_batch = 100 if len(result.words) <= 4 else (
            10 if len(result.words) <= 50 else 1
        )
        request_ms, result = _timed(call, repeats, request_batch)
        retained, peak = _memory_bytes(call)
        payload = canonical_bytes(result)
        case = {
            "ref": ref,
            "words": len(result.words),
            "units": len(result.units),
            "sounds": len(result.sounds),
            "request_ms": request_ms,
            "retained_python_bytes": retained,
            "peak_python_bytes": peak,
            "canonical_sha256": hashlib.sha256(payload).hexdigest(),
            "projections_ms": _projection_times(result, projection_repeats),
        }
        if internals:
            session = phonemize_request(
                phonemizer._recitation, ref, script=phonemizer._script,
                selection=phonemizer._selection,
            )
            case["session_sha256"] = hashlib.sha256(
                repr(session).encode("utf-8")
            ).hexdigest()
        if stages:
            case["stages_ms"] = _stage_times(phonemizer, ref, repeats)
        cases.append(case)
    output = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "clock": "process_time",
        "init_ms": init_ms,
        "warm_init_ms": warm_init_ms,
        "repeats": repeats,
        "projection_repeats": projection_repeats,
        "suspend_gc": suspend_gc,
        "cases": cases,
    }
    if constructors:
        output["constructor_scale"] = _constructor_scale(constructors)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("refs", nargs="*", default=DEFAULT_REFS)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--projection-repeats", type=int, default=5)
    parser.add_argument("--fingerprint-internals", action="store_true")
    parser.add_argument("--stages", action="store_true")
    parser.add_argument("--constructors", type=int, default=0)
    parser.add_argument("--suspend-gc", action="store_true")
    args = parser.parse_args()
    print(json.dumps(
        benchmark(
            args.refs, args.repeats, args.projection_repeats,
            args.fingerprint_internals, args.stages, args.constructors,
            args.suspend_gc,
        ),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
