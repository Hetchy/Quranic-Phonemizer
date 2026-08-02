"""Compare Uthmani phoneme output against the frozen snapshots.

Run: python tools/parity.py [--mode word|verse] [--limit N]
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from quranic_phonemizer.api import alphabet as load_alphabet  # noqa: E402
from quranic_phonemizer.api import recitation  # noqa: E402
from quranic_phonemizer.engine.laws import (  # noqa: E402
    check_inscription,
    check_performance,
)
from quranic_phonemizer.model.address import (  # noqa: E402
    BoundaryPlan,
    Junction,
    Riwayah,
    Script,
    VerseRef,
)
from quranic_phonemizer.render.recite import phonemes_by_word  # noqa: E402

SNAPSHOTS = ROOT / "tests" / "snapshots" / "phonemes"


#: `continuous` joins across verse boundaries, so its unit is the surah, not
#: the verse: one `Reading` per surah, every junction a join. Legacy froze it
#: as a single call over the whole mushaf, so the seams between surahs are the
#: one place this harness and that baseline can legitimately differ.
MODES = ("word", "verse", "continuous")


def plan_for(mode: str, words: int) -> BoundaryPlan:
    """`word` stops after every word; the others join and stop at the end."""
    if mode == "word":
        return BoundaryPlan((Junction.STOP,) * (words - 1) + (Junction.EDGE,))
    return BoundaryPlan((Junction.JOIN,) * (words - 1) + (Junction.EDGE,))


def units(hafs, mode: str):
    """The stretches a mode reads at once: a surah continuously, else a verse.

    `read` takes the words it is given, so a stretch that spans verses is one
    reading and a rule can cross the seam inside it.
    """
    packed = hafs.corpus
    for surah in range(1, 115):
        verses = [
            VerseRef(surah, ayah)
            for ayah in range(1, len(packed.surah_info[str(surah)]) + 1)
        ]
        if mode == "continuous":
            words = tuple(word for v in verses for word in hafs.words(v))
            yield verses[0], words
        else:
            for verse in verses:
                yield verse, hafs.words(verse)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="word", choices=MODES)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--show", type=int, default=12)
    args = parser.parse_args()

    hafs, alphabet = recitation(Riwayah.HAFS), load_alphabet()
    packed = hafs.corpus

    matched = total = 0
    bucketed = 0
    mismatches: list[tuple[str, list, list]] = []
    diffs: collections.Counter[str] = collections.Counter()

    with gzip.open(SNAPSHOTS / f"{args.mode}.jsonl.gz", "rt", encoding="utf-8") as fh:
        expected = (json.loads(line) for line in fh)
        for verse, source in units(hafs, args.mode):
            built = hafs.build(hafs.read(Script.UTHMANI, verse, source))
            score = built.score
            check_inscription(built.inscription, score)
            performance = hafs.perform(
                score, plan_for(args.mode, len(score.words))
            )
            check_performance(performance, score)
            produced = phonemes_by_word(performance, score, alphabet)
            got_words = [list(word) for word in produced]
            want_words = [next(expected) for _ in got_words]
            wrong = [
                index
                for index, (got, want) in enumerate(zip(got_words, want_words))
                if got != want
            ]
            total += len(got_words)
            matched += len(got_words) - len(wrong)
            if _same_sequence(got_words, want_words):
                bucketed += len(wrong)
            else:
                for index in wrong:
                    got, want = got_words[index], want_words[index]
                    diffs[_signature(got, want)] += 1
                    if len(mismatches) < args.show:
                        where = source[index][0]
                        mismatches.append((
                            f"{where.surah}:{where.ayah}:{where.word}",
                            got, want,
                        ))
            if args.limit and total >= args.limit:
                break

    print(f"{args.mode}: {matched}/{total} words match "
          f"({100 * matched / total:.3f}%)")
    if bucketed:
        # A sound merged across a word boundary can be credited to either word.
        phonemes = matched + bucketed
        print(f"   of which {bucketed} differ only in which word owns a sound "
              f"merged across a boundary; the verse sequence is identical")
        print(f"   phoneme sequence: {phonemes}/{total} "
              f"({100 * phonemes / total:.3f}%)")
    if diffs:
        print("\nmismatch shapes:")
        for signature, count in diffs.most_common(15):
            print(f"   {count:6d}  {signature}")
        print("\nexamples:")
        for location, got, want in mismatches:
            print(f"   {location:12s} got  {got}")
            print(f"   {'':12s} want {want}")
    return 0 if matched == total else 1


def _same_sequence(got: list[list], want: list[list]) -> bool:
    """Same phonemes in the same order, ignoring where the words are cut."""
    return [t for word in got for t in word] == [t for word in want for t in word]


def _signature(got: list, want: list) -> str:
    if len(got) != len(want):
        extra = [t for t in want if t not in got][:2]
        missing = [t for t in got if t not in want][:2]
        return f"len {len(got)}v{len(want)} want+{extra} got+{missing}"
    pairs = [(g, w) for g, w in zip(got, want) if g != w][:2]
    return " ".join(f"{g}->{w}" for g, w in pairs)


if __name__ == "__main__":
    raise SystemExit(main())
