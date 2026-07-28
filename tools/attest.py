"""Every family a script attests must be produced by some occurrence.

Run: python tools/attest.py [--script uthmani|indopak] [--limit N]
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
from quranic_phonemizer.engine.laws import check_attestations  # noqa: E402
from quranic_phonemizer.engine.run import perform  # noqa: E402
from quranic_phonemizer.model.address import (  # noqa: E402
    BoundaryPlan,
    Junction,
    Script,
    VerseRef,
)
from quranic_phonemizer.model.inscription import Attests  # noqa: E402
from quranic_phonemizer.riwayat.hafs import (  # noqa: E402
    HAFS,
    ledger,
    lexeme_passes,
    lexicon,
    script_adapter,
)


def unmet(adapter, ref: VerseRef, words, shared) -> tuple[list[str], int]:
    built = build(adapter.read(ref, words), **shared)
    score = built.score
    plan = BoundaryPlan(
        (Junction.JOIN,) * (len(score.words) - 1) + (Junction.EDGE,)
    )
    performance = perform(score, HAFS, plan)
    attested = [
        (s.anchor, s.family)
        for s in built.inscription.spellings
        if isinstance(s, Attests)
    ]
    return check_attestations(attested, performance, plan), len(attested)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default="uthmani",
                        choices=[s.value for s in Script])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--show", type=int, default=8)
    args = parser.parse_args()

    script = Script(args.script)
    adapter = script_adapter(script)
    shared = {"lexicon": lexicon(), "ledger": ledger(),
              "passes": lexeme_passes()}
    verses = load_verses(script.value)

    families: collections.Counter[str] = collections.Counter()
    examples: list[str] = []
    total = 0
    for index, key in enumerate(sorted(verses)):
        if args.limit and index >= args.limit:
            break
        problems, attested = unmet(adapter, VerseRef(*key), verses[key], shared)
        total += attested
        for problem in problems:
            families[problem.split("attests ")[1].split(" but")[0]] += 1
            if len(examples) < args.show:
                examples.append(problem)

    count = sum(families.values())
    print(f"{script.value}: unmet attestations: {count} of {total}")
    for family, number in families.most_common():
        print(f"   {number:6d}  {family}")
    if examples:
        print("\nexamples:")
        for problem in examples:
            print(f"   {problem}")
    return 0 if count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
