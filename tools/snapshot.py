"""Which words this checkout reads differently. A floor says only how many.

Run: python tools/snapshot.py write PATH [--mode word|verse|continuous]
     python tools/snapshot.py diff OLD NEW [--show N]
"""
from __future__ import annotations

import argparse
import gzip
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from quranic_phonemizer.api import alphabet as load_alphabet  # noqa: E402
from quranic_phonemizer.api import recitation  # noqa: E402
from quranic_phonemizer.model.address import Riwayah, Script  # noqa: E402
from quranic_phonemizer.render.recite import phonemes_by_word  # noqa: E402
from tools.parity import MODES, plan_for, units  # noqa: E402


def _rows(mode: str):
    """One row per word: its location, and the tokens this checkout reads."""
    hafs, alphabet = recitation(Riwayah.HAFS), load_alphabet()
    for verse, source in units(hafs, mode):
        built = hafs.build(hafs.read(Script.UTHMANI, verse, source))
        performance = hafs.perform(
            built.score, plan_for(mode, len(built.score.words))
        )
        produced = phonemes_by_word(performance, built.score, alphabet)
        for (where, _), tokens in zip(source, produced):
            yield {
                "ref": f"{where.surah}:{where.ayah}:{where.word}",
                "tokens": list(tokens),
            }


def write(path: pathlib.Path, mode: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        for row in _rows(mode):
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    print(f"{mode}: wrote {count} words to {path}")
    return 0


def _read(path: pathlib.Path) -> dict[str, list[str]]:
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return {r["ref"]: r["tokens"] for r in map(json.loads, fh)}


def diff(old: pathlib.Path, new: pathlib.Path, show: int) -> int:
    before, after = _read(old), _read(new)
    gone = sorted(before.keys() - after.keys())
    fresh = sorted(after.keys() - before.keys())
    moved = [r for r in before if r in after and before[r] != after[r]]

    print(f"{len(before)} words before, {len(after)} after")
    if gone or fresh:
        print(f"  {len(gone)} refs gone, {len(fresh)} refs new")
    print(f"  {len(moved)} words read differently")
    for ref in moved[:show]:
        print(f"   {ref:12s} was  {' '.join(before[ref])}")
        print(f"   {'':12s} now  {' '.join(after[ref])}")
    if len(moved) > show:
        print(f"   ... and {len(moved) - show} more")
    return 1 if moved or gone or fresh else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    w = sub.add_parser("write")
    w.add_argument("path", type=pathlib.Path)
    w.add_argument("--mode", default="word", choices=MODES)
    d = sub.add_parser("diff")
    d.add_argument("old", type=pathlib.Path)
    d.add_argument("new", type=pathlib.Path)
    d.add_argument("--show", type=int, default=20)
    args = parser.parse_args()

    if args.action == "write":
        return write(args.path, args.mode)
    return diff(args.old, args.new, args.show)


if __name__ == "__main__":
    raise SystemExit(main())
