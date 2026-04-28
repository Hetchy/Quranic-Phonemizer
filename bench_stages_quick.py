"""Quick per-stage breakdown for phonemize("1-114"), one run.

Monkey-patches the same stages the earlier breakdown used so numbers are
directly comparable. Then runs cProfile on the hottest stage to see
function-level cost.
"""
from __future__ import annotations

import cProfile
import pstats
import time
from io import StringIO


def patch_and_time():
    from quranic_phonemizer import parser as parser_mod
    from quranic_phonemizer import word as word_mod
    from quranic_phonemizer.symbols.letters import letter as letter_mod
    from quranic_phonemizer import loader as loader_mod
    from quranic_phonemizer import phonemizer as phon_mod

    timings = {}

    def wrap(name, fn):
        def w(*a, **k):
            t0 = time.perf_counter()
            r = fn(*a, **k)
            timings[name] = timings.get(name, 0.0) + (time.perf_counter() - t0)
            return r
        return w

    # Wrap key stages
    parser_mod.Parser.parse_word = wrap("parse_word_total", parser_mod.Parser.parse_word)
    parser_mod.Parser._link_words = wrap("link_words", parser_mod.Parser._link_words)
    parser_mod.Parser._annotate_boundaries = wrap("annotate_boundaries", parser_mod.Parser._annotate_boundaries)
    word_mod.Word.phonemize = wrap("word_phonemize_total", word_mod.Word.phonemize)
    word_mod.Word.get_phonemes = wrap("word_get_phonemes_total", word_mod.Word.get_phonemes)
    word_mod.Word.apply_phoneme_overrides = wrap("apply_overrides_total", word_mod.Word.apply_phoneme_overrides)
    letter_mod.LetterSymbol.phonemize = wrap("letter_phonemize_total", letter_mod.LetterSymbol.phonemize)
    loader_mod.keys_for_reference = wrap("keys_for_reference", loader_mod.keys_for_reference)

    return timings


def main():
    timings = patch_and_time()

    from quranic_phonemizer import Phonemizer
    t0 = time.perf_counter()
    p = Phonemizer()
    init_s = time.perf_counter() - t0

    # Warm: ensure caches/JIT-ish first call done outside the timed run
    t0 = time.perf_counter()
    r = p.phonemize("1-114")
    total = time.perf_counter() - t0

    print(f"init_s = {init_s*1000:.1f} ms")
    print(f"total phonemize('1-114') = {total*1000:.1f} ms")
    print()
    print(f"{'stage':<30} {'ms':>10}   {'%':>6}")
    print("-" * 52)
    rows = sorted(timings.items(), key=lambda x: -x[1])
    for name, secs in rows:
        print(f"{name:<30} {secs*1000:>10.1f}   {secs/total*100:>5.1f}%")

    # Now profile parse_word for function-level breakdown
    print("\n=== cProfile of phonemize('1-114') ===")
    pr = cProfile.Profile()
    pr.enable()
    p.phonemize("1-114")
    pr.disable()
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(25)
    print(s.getvalue())

    print("\n=== cProfile (sorted by tottime) ===")
    s2 = StringIO()
    pstats.Stats(pr, stream=s2).sort_stats("tottime").print_stats(25)
    print(s2.getvalue())


if __name__ == "__main__":
    main()
