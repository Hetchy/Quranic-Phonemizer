"""Compare Uthmani and IndoPak, performed and rendered, word by word.

Run: python tools/cross_parity.py [--mode word|verse] [--limit N]
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from l1_harness import load_verses  # noqa: E402

from quranic_phonemizer.canon.build import build  # noqa: E402
from quranic_phonemizer.engine.laws import (  # noqa: E402
    check_inscription,
    check_performance,
)
from quranic_phonemizer.engine.run import perform  # noqa: E402
from quranic_phonemizer.model.address import (  # noqa: E402
    BoundaryPlan,
    Junction,
    Script,
    VerseRef,
)
from quranic_phonemizer.render.alphabet import load_alphabet  # noqa: E402
from quranic_phonemizer.render.recite import phonemes_by_word  # noqa: E402
from quranic_phonemizer.riwayat.hafs import (  # noqa: E402
    HAFS,
    ledger,
    lexeme_passes,
    lexicon,
    script_adapter,
)

ALPHABET = ROOT / "quranic_phonemizer" / "data" / "render" / "ipa.yaml"

#: Which script's residue rows are shown, and which side of a pair is "got".
LEFT, RIGHT = Script.UTHMANI, Script.INDOPAK

#: Same two modes as tools/parity.py, for the same reason: verse by verse cannot join across verses.
MODES = ("word", "verse")


def plan_for(mode: str, words: int) -> BoundaryPlan:
    """Same boundary-plan construction as tools/parity.py."""
    if mode == "word":
        return BoundaryPlan((Junction.STOP,) * (words - 1) + (Junction.EDGE,))
    return BoundaryPlan((Junction.JOIN,) * (words - 1) + (Junction.EDGE,))


def render_verse(adapter, ref: VerseRef, words, shared, mode: str, alphabet):
    built = build(adapter.read(ref, words), **shared)
    score = built.score
    check_inscription(built.inscription, score)
    performance = perform(score, HAFS, plan_for(mode, len(score.words)))
    check_performance(performance, score)
    return [list(word) for word in phonemes_by_word(performance, score, alphabet)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="word", choices=MODES)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--show", type=int, default=12)
    args = parser.parse_args()

    alphabet = load_alphabet(ALPHABET)
    shared = {"lexicon": lexicon(), "ledger": ledger(),
              "passes": lexeme_passes()}
    adapters = {script: script_adapter(script) for script in (LEFT, RIGHT)}
    sources = {script: load_verses(script.value) for script in (LEFT, RIGHT)}

    matched = total = 0
    skipped_verses = 0
    examples: list[tuple[str, list, list]] = []
    diffs: collections.Counter[str] = collections.Counter()

    for key in sorted(sources[LEFT]):
        if key not in sources[RIGHT]:
            skipped_verses += 1
            continue
        ref = VerseRef(*key)
        rendered = {
            script: render_verse(
                adapters[script], ref, sources[script][key], shared,
                args.mode, alphabet,
            )
            for script in (LEFT, RIGHT)
        }
        left, right = rendered[LEFT], rendered[RIGHT]
        if len(left) != len(right):
            # A word-count disagreement is a join/split difference, not a phoneme one.
            skipped_verses += 1
            diffs[f"word count {len(left)}v{len(right)}"] += 1
            continue
        for index, (got, want) in enumerate(zip(left, right)):
            total += 1
            if got == want:
                matched += 1
                continue
            diffs[_signature(got, want)] += 1
            if len(examples) < args.show:
                examples.append(
                    (f"{key[0]}:{key[1]}:{index + 1}", got, want)
                )
        if args.limit and total >= args.limit:
            break

    if not total:
        print("no comparable words")
        return 1
    print(f"{args.mode}: {matched}/{total} words agree across scripts "
          f"({100 * matched / total:.3f}%)")
    if skipped_verses:
        print(f"   {skipped_verses} verses not compared (word-count disagreement)")
    if diffs:
        print("\nmismatch shapes:")
        for signature, count in diffs.most_common(15):
            print(f"   {count:6d}  {signature}")
        print(f"\nexamples ({LEFT.value} = got, {RIGHT.value} = want):")
        for location, got, want in examples:
            print(f"   {location:12s} got  {got}")
            print(f"   {'':12s} want {want}")
    return 0 if matched == total else 1


def _signature(got: list, want: list) -> str:
    if len(got) != len(want):
        extra = [t for t in want if t not in got][:2]
        missing = [t for t in got if t not in want][:2]
        return f"len {len(got)}v{len(want)} want+{extra} got+{missing}"
    pairs = [(g, w) for g, w in zip(got, want) if g != w][:2]
    return " ".join(f"{g}->{w}" for g, w in pairs)


if __name__ == "__main__":
    raise SystemExit(main())
