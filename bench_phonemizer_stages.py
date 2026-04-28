"""Per-stage benchmark harness for the Phonemizer.

This script monkey-patches the relevant methods in the quranic_phonemizer
package to record cumulative time spent in each stage of `Phonemizer.phonemize()`,
plus a separate breakdown for `Phonemizer.__init__`.

It runs:
  1) 5 single-test cases, 3 runs each in separate Python subprocesses
     (mirroring the existing harness style in `bench_phonemizer.py`)
  2) A 5-call same-process slowdown experiment for `phonemize("1-114")`
     that captures per-call wall time, RSS memory, gc.get_count(),
     len(gc.get_objects()), and per-stage breakdown across calls.

Usage:
    python bench_phonemizer_stages.py                 # run everything
    python bench_phonemizer_stages.py --child <test>  # used internally for subprocess isolation

Results are printed as JSON lines with a final Markdown summary.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

# ---------- shared test definitions ----------
ALL_STOPS = [
    "verse",
    "preferred_continue",
    "preferred_stop",
    "optional_stop",
    "compulsory_stop",
    "prohibited_stop",
]

TESTS = OrderedDict([
    ("verse_2_255",          {"ref": "2:255"}),
    ("surah_2",              {"ref": "2"}),
    ("surah_2_verse_stops",  {"ref": "2", "stop_signs": ["verse"]}),
    ("quran_full",           {"ref": "1-114"}),
    ("quran_full_all_stops", {"ref": "1-114", "stop_signs": ALL_STOPS}),
])

# Stages we will time. Order matters for nice display.
STAGE_KEYS = [
    # init breakdown (only populated for the init record)
    "init.load_symbol_mappings",
    "init.parser_create",          # Parser(...) constructor (special words + lookup tables)
    "init.text_matcher_create",    # TextMatcher(...) constructor (DB load)
    "init.surah_info_load",
    "init.total",
    # phonemize stages
    "validate_refs",
    "parser.load_words",
    "parser.load_words.load_db",
    "parser.load_words.keys_for_reference",
    "parser.load_words.parse_words_loop",
    "parser.load_words.link_and_annotate",
    "phonemize.word_phonemize_loop",
    "phonemize.word_phonemize_loop.letter_phonemize_total",
    "phonemize.apply_phoneme_overrides_loop",
    "phonemize.get_phonemes_loop",
    "phonemize.result_construct",
    "phonemize.total",
]


# ---------- instrumentation ----------
class StageTimer:
    """Cumulative per-call stage timer. Reset before each call."""
    def __init__(self) -> None:
        self.times: dict[str, float] = {}
        self.counts: dict[str, int] = {}

    def add(self, key: str, dt: float) -> None:
        self.times[key] = self.times.get(key, 0.0) + dt
        self.counts[key] = self.counts.get(key, 0) + 1

    def reset(self) -> None:
        self.times.clear()
        self.counts.clear()

    def snapshot(self) -> dict[str, float]:
        return dict(self.times)


# Single global timer used by the patched methods.
TIMER = StageTimer()


def install_instrumentation():
    """Monkey-patch package functions/methods to record stage times into TIMER."""
    # We import the module objects (not symbols) so wrappers are visible to all callers.
    import quranic_phonemizer.phonemizer as ph_mod
    import quranic_phonemizer.parser as parser_mod
    import quranic_phonemizer.word as word_mod
    import quranic_phonemizer.loader as loader_mod
    import quranic_phonemizer.symbols.letters.letter as letter_mod

    pc = time.perf_counter

    # ---- init sub-stage timing ----
    orig_load_symbol_mappings = parser_mod.load_symbol_mappings
    def patched_load_symbol_mappings(*a, **kw):
        t0 = pc()
        try:
            return orig_load_symbol_mappings(*a, **kw)
        finally:
            TIMER.add("init.load_symbol_mappings", pc() - t0)
    # patch in BOTH the parser module and the phonemizer module (already imported by name)
    parser_mod.load_symbol_mappings = patched_load_symbol_mappings
    ph_mod.load_symbol_mappings = patched_load_symbol_mappings

    orig_parser_init = parser_mod.Parser.__init__
    def patched_parser_init(self, *a, **kw):
        t0 = pc()
        try:
            return orig_parser_init(self, *a, **kw)
        finally:
            TIMER.add("init.parser_create", pc() - t0)
    parser_mod.Parser.__init__ = patched_parser_init

    # TextMatcher.__init__ — patch by attribute
    from quranic_phonemizer.text_matcher import TextMatcher
    orig_tm_init = TextMatcher.__init__
    def patched_tm_init(self, *a, **kw):
        t0 = pc()
        try:
            return orig_tm_init(self, *a, **kw)
        finally:
            TIMER.add("init.text_matcher_create", pc() - t0)
    TextMatcher.__init__ = patched_tm_init

    # Phonemizer.__init__ — wrap whole thing, plus measure surah_info read by wrapping json.load
    orig_phon_init = ph_mod.Phonemizer.__init__
    def patched_phon_init(self, *a, **kw):
        t_start = pc()
        # Use a marker dict to time only the second json.load call (surah_info)
        # — but easier: just wrap json.load through a context. Since loader.load_db has its own
        # JSON read, separate that out in load_words below. Here we time the surah_info read by
        # subtracting (init.total minus everything else) — nope, that's inaccurate.
        # Instead: directly time the surah_info read using a side import.
        import json as _json
        orig_json_load = _json.load
        # only first call inside phonemizer __init__ is surah_info because text_matcher uses load_db (wrapped separately)
        state = {"caught": False}
        def wrapped_json_load(fp, *aa, **kk):
            if not state["caught"]:
                t = pc()
                try:
                    return orig_json_load(fp, *aa, **kk)
                finally:
                    TIMER.add("init.surah_info_load", pc() - t)
                    state["caught"] = True
            return orig_json_load(fp, *aa, **kk)
        _json.load = wrapped_json_load
        try:
            return orig_phon_init(self, *a, **kw)
        finally:
            _json.load = orig_json_load
            TIMER.add("init.total", pc() - t_start)
    ph_mod.Phonemizer.__init__ = patched_phon_init

    # ---- loader stages (called from parser.load_words) ----
    orig_load_db = loader_mod.load_db
    def patched_load_db(*a, **kw):
        t0 = pc()
        try:
            return orig_load_db(*a, **kw)
        finally:
            TIMER.add("parser.load_words.load_db", pc() - t0)
    loader_mod.load_db = patched_load_db
    parser_mod.load_db = patched_load_db  # parser imported via `from .loader import load_db`

    orig_keys_for_ref = loader_mod.keys_for_reference
    def patched_keys_for_ref(*a, **kw):
        t0 = pc()
        try:
            return orig_keys_for_ref(*a, **kw)
        finally:
            TIMER.add("parser.load_words.keys_for_reference", pc() - t0)
    loader_mod.keys_for_reference = patched_keys_for_ref
    parser_mod.keys_for_reference = patched_keys_for_ref

    # ---- Parser.load_words wrap (total + parse loop + link+annotate) ----
    orig_load_words = parser_mod.Parser.load_words

    def patched_load_words(self, ref, db_path=None, *, stop_signs=[], stop_refs=[]):
        # Re-implement with timing markers around the parse-words loop and link+annotate.
        from quranic_phonemizer.location import Location
        if db_path is None:
            from quranic_phonemizer.parser import DATA_DIR as _DD
            db_path = _DD / "Quran.json"

        t_total = pc()
        # load_db and keys_for_reference are individually timed via wrappers
        db = loader_mod.load_db(db_path)
        locations = loader_mod.keys_for_reference(ref, db)

        t_loop = pc()
        words = []
        for loc in locations:
            raw = db[loc]["text"]
            location_obj = Location.from_key(loc)
            word = self.parse_word(raw, location_obj)
            words.append(word)
        TIMER.add("parser.load_words.parse_words_loop", pc() - t_loop)

        t_la = pc()
        self._link_words(words)
        self._annotate_boundaries(words, stop_signs=stop_signs, stop_refs=stop_refs)
        TIMER.add("parser.load_words.link_and_annotate", pc() - t_la)

        TIMER.add("parser.load_words", pc() - t_total)
        return words

    parser_mod.Parser.load_words = patched_load_words

    # ---- LetterSymbol.phonemize timing (sum of all letter calls inside Word.phonemize loop) ----
    orig_letter_phonemize = letter_mod.LetterSymbol.phonemize
    def patched_letter_phonemize(self):
        t0 = pc()
        try:
            return orig_letter_phonemize(self)
        finally:
            TIMER.add("phonemize.word_phonemize_loop.letter_phonemize_total", pc() - t0)
    letter_mod.LetterSymbol.phonemize = patched_letter_phonemize

    # ---- Phonemizer.phonemize wrap: re-implement around stage markers ----
    # We replace it entirely so each stage's wall time is measured exactly
    # at the same code points as the original implementation. We keep the
    # original semantics by delegating to original sub-methods.
    orig_phonemize = ph_mod.Phonemizer.phonemize

    def patched_phonemize(
        self,
        ref=None,
        *,
        ref_text=None,
        stop_signs=[],
        stop_refs=[],
        debug=False,
        iqlab_phoneme=None,
        ikhfaa_shafawi_phoneme=None,
        mode="full",
    ):
        # Reset per-call cumulative timers BEFORE timing total.
        TIMER.reset()
        t_total = pc()

        # We assume `ref` is a traditional reference (the benchmark only uses traditional refs).
        # That keeps the patched wrapper simple — text-matching paths skipped.
        if mode not in ("full", "simple"):
            raise ValueError(f"Invalid mode: {mode!r}")
        if ref is None and ref_text is None:
            raise ValueError("Either 'ref' or 'ref_text' must be provided")

        match_score = None

        t = pc()
        self._validate_refs(ref)
        TIMER.add("validate_refs", pc() - t)

        invalid_stops = set(stop_signs) - self.valid_stop_signs
        if invalid_stops:
            raise ValueError(f"Invalid stop sign types: {invalid_stops}")

        # parser.load_words is wrapped (records its own total + sub-stages).
        words = self.parser.load_words(
            ref, self.db_path, stop_signs=stop_signs, stop_refs=stop_refs,
        )

        t = pc()
        for word in words:
            word.phonemize()
        TIMER.add("phonemize.word_phonemize_loop", pc() - t)

        t = pc()
        for word in words:
            word.apply_phoneme_overrides()
        TIMER.add("phonemize.apply_phoneme_overrides_loop", pc() - t)

        t = pc()
        all_phonemes = []
        for word in words:
            all_phonemes.append(word.get_phonemes())
        TIMER.add("phonemize.get_phonemes_loop", pc() - t)

        t = pc()
        result = ph_mod.PhonemizeResult(
            ref, " ".join(w.text for w in words), all_phonemes, words,
            stop_signs, stop_refs, match_score, mode,
        )
        TIMER.add("phonemize.result_construct", pc() - t)

        TIMER.add("phonemize.total", pc() - t_total)
        return result

    ph_mod.Phonemizer.phonemize = patched_phonemize


# ---------- runners ----------
def _build_kwargs(spec):
    kwargs = {}
    if "stop_signs" in spec:
        kwargs["stop_signs"] = list(spec["stop_signs"])
    return kwargs


def _rss_kb_self() -> int:
    """Read VmRSS in kB from /proc/self/status (Linux). Returns 0 on failure."""
    try:
        with open("/proc/self/status", "r") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except Exception:
        pass
    return 0


def child_run_test(name: str, repeat: int) -> None:
    """Run a single test in this (subprocess) process and print JSON lines."""
    spec = TESTS[name]
    kwargs = _build_kwargs(spec)

    install_instrumentation()
    # Reset TIMER before init so init.* stages are clean.
    TIMER.reset()

    t0 = time.perf_counter()
    from quranic_phonemizer import Phonemizer
    phonemizer = Phonemizer()
    init_elapsed = time.perf_counter() - t0
    init_stages = TIMER.snapshot()

    # Emit init record
    init_record = {
        "test": name,
        "kind": "init",
        "init_s": init_elapsed,
        "stages": init_stages,
    }
    print(json.dumps(init_record), flush=True)

    for i in range(1, repeat + 1):
        t0 = time.perf_counter()
        result = phonemizer.phonemize(spec["ref"], **kwargs)
        elapsed = time.perf_counter() - t0
        stages = TIMER.snapshot()
        n_words = len(result._nested)
        print(json.dumps({
            "test": name,
            "kind": "run",
            "run": i,
            "elapsed_s": elapsed,
            "n_words": n_words,
            "stages": stages,
        }), flush=True)


def child_slowdown_experiment(repeat: int) -> None:
    """Run phonemize('1-114') `repeat` times in same process; report mem + stages."""
    install_instrumentation()
    TIMER.reset()

    t0 = time.perf_counter()
    from quranic_phonemizer import Phonemizer
    phonemizer = Phonemizer()
    init_elapsed = time.perf_counter() - t0
    init_stages = TIMER.snapshot()

    print(json.dumps({
        "test": "slowdown_quran_full",
        "kind": "init",
        "init_s": init_elapsed,
        "stages": init_stages,
    }), flush=True)

    prev_objs = len(gc.get_objects())
    for i in range(1, repeat + 1):
        t0 = time.perf_counter()
        result = phonemizer.phonemize("1-114")
        elapsed = time.perf_counter() - t0
        stages = TIMER.snapshot()
        rss_kb = _rss_kb_self()
        gc_counts = gc.get_count()
        cur_objs = len(gc.get_objects())
        n_words = len(result._nested)
        # discard result reference for next iteration
        del result
        print(json.dumps({
            "test": "slowdown_quran_full",
            "kind": "run",
            "run": i,
            "elapsed_s": elapsed,
            "rss_kb": rss_kb,
            "gc_count": list(gc_counts),
            "gc_n_objects": cur_objs,
            "gc_n_objects_delta": cur_objs - prev_objs,
            "n_words": n_words,
            "stages": stages,
        }), flush=True)
        prev_objs = cur_objs


# ---------- top-level orchestration ----------
def parent_main(repeat: int, log_path: Path) -> None:
    """Run all tests in subprocesses, capture output, then format Markdown."""
    log_lines: list[str] = []
    all_records: list[dict] = []

    def record_line(line: str) -> None:
        log_lines.append(line)
        # also stream to stdout
        print(line, flush=True)

    # 1) Per-test runs (each test in a fresh subprocess)
    for name in TESTS:
        record_line(f"## RUN {name}")
        cmd = [PYTHON, str(REPO_ROOT / "bench_phonemizer_stages.py"), "--child", name, "--repeat", str(repeat)]
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        if proc.returncode != 0:
            record_line(f"# ERROR running {name}: rc={proc.returncode}")
            record_line(proc.stderr)
            continue
        for line in proc.stdout.splitlines():
            record_line(line)
            try:
                rec = json.loads(line)
                all_records.append(rec)
            except json.JSONDecodeError:
                pass
        if proc.stderr.strip():
            record_line("# STDERR: " + proc.stderr.strip()[:500])

    # 2) Slowdown experiment (single subprocess, 5 calls)
    record_line("## RUN slowdown_quran_full")
    cmd = [PYTHON, str(REPO_ROOT / "bench_phonemizer_stages.py"), "--child-slowdown", "--repeat", "5"]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        record_line(f"# ERROR running slowdown: rc={proc.returncode}")
        record_line(proc.stderr)
    else:
        for line in proc.stdout.splitlines():
            record_line(line)
            try:
                rec = json.loads(line)
                all_records.append(rec)
            except json.JSONDecodeError:
                pass

    # ---------- Build Markdown summary ----------
    record_line("")
    record_line("# Markdown summary")
    record_line("")

    # Per-test mean across runs
    record_line("## Per-stage breakdown (mean of 3 runs, seconds)")
    record_line("")
    # Stages we actually display (init.* shown in a separate table)
    phonemize_stages = [s for s in STAGE_KEYS if not s.startswith("init.")]

    # Header
    header = ["stage"] + list(TESTS.keys())
    record_line("| " + " | ".join(header) + " |")
    record_line("|" + "|".join(["---"] * len(header)) + "|")

    # Aggregate per-test mean
    means: dict[str, dict[str, float]] = {t: {} for t in TESTS}
    for rec in all_records:
        if rec.get("kind") != "run":
            continue
        t = rec["test"]
        if t not in means:
            continue
        for k, v in rec["stages"].items():
            means[t].setdefault(k, []).append(v)

    def fmt(v):
        if v is None:
            return "-"
        if v < 1e-3:
            return f"{v*1e6:.0f}us"
        if v < 1.0:
            return f"{v*1e3:.1f}ms"
        return f"{v:.3f}s"

    for stage in phonemize_stages:
        row = [stage]
        for t in TESTS:
            samples = means[t].get(stage)
            if samples:
                row.append(fmt(sum(samples) / len(samples)))
            else:
                row.append("-")
        record_line("| " + " | ".join(row) + " |")

    # Init breakdown (one column per test — should be similar but reported per-process)
    record_line("")
    record_line("## Phonemizer.__init__ breakdown (one process per test)")
    record_line("")
    init_recs = {r["test"]: r for r in all_records if r.get("kind") == "init" and r["test"] in TESTS}
    init_stages_to_show = [s for s in STAGE_KEYS if s.startswith("init.")]
    header = ["stage"] + list(TESTS.keys())
    record_line("| " + " | ".join(header) + " |")
    record_line("|" + "|".join(["---"] * len(header)) + "|")
    for stage in init_stages_to_show:
        row = [stage]
        for t in TESTS:
            r = init_recs.get(t)
            if r is None:
                row.append("-")
            else:
                v = r["stages"].get(stage)
                row.append(fmt(v) if v is not None else "-")
        record_line("| " + " | ".join(row) + " |")

    # 5-call slowdown
    record_line("")
    record_line("## Same-process slowdown experiment: phonemize('1-114') x 5")
    record_line("")
    slow_runs = [r for r in all_records if r.get("test") == "slowdown_quran_full" and r.get("kind") == "run"]
    if slow_runs:
        # Headline table: per-call wall + memory + obj counts
        record_line("| call | elapsed_s | RSS (MB) | gc.get_count | n_objects | n_objects_delta |")
        record_line("|---|---|---|---|---|---|")
        for r in slow_runs:
            record_line(
                f"| {r['run']} | {r['elapsed_s']:.3f} | {r['rss_kb']/1024:.1f} | "
                f"{r['gc_count']} | {r['gc_n_objects']} | {r['gc_n_objects_delta']} |"
            )

        # Stage shift table
        record_line("")
        record_line("### Per-stage shift across 5 calls (seconds)")
        record_line("")
        header = ["stage"] + [f"call{r['run']}" for r in slow_runs]
        record_line("| " + " | ".join(header) + " |")
        record_line("|" + "|".join(["---"] * len(header)) + "|")
        for stage in [s for s in STAGE_KEYS if not s.startswith("init.")]:
            row = [stage]
            for r in slow_runs:
                v = r["stages"].get(stage)
                row.append(fmt(v) if v is not None else "-")
            record_line("| " + " | ".join(row) + " |")

    # Persist log
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"\n# Log saved to {log_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--child", help="Run named test in this process (subprocess mode)")
    p.add_argument("--child-slowdown", action="store_true", help="Run slowdown experiment in this process")
    p.add_argument("--repeat", type=int, default=3)
    p.add_argument("--log", default="/tmp/bench_stages_results.log")
    args = p.parse_args()

    if args.child:
        child_run_test(args.child, args.repeat)
        return
    if args.child_slowdown:
        child_slowdown_experiment(args.repeat)
        return

    parent_main(args.repeat, Path(args.log))


if __name__ == "__main__":
    main()
