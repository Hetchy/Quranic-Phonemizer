"""Phase 6's gate: phoneme parity against the frozen snapshots.

Parity does not prove correctness — both evidence §4 defects are baked into
every frozen view. What it proves is that the rebuild reproduces the behaviour
the old implementation had, so any later change is a deliberate one.

It is **not** a cross-script test — it runs Uthmani only. `tools/cross_parity.py`
is the one that asks whether the two scripts agree, and the two harnesses are
insensitive to opposite failures: this one cannot see a script fact leaking,
because it runs one script; that one cannot see a missing rule, because a rule
absent from both scripts leaves them agreeing. Neither substitutes for the other.

Run:  python tools/parity.py [--mode word|verse] [--limit N]
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

from quranic_phonemizer.canon.build import build  # noqa: E402
from quranic_phonemizer.engine.laws import (  # noqa: E402
    check_inscription,
    check_performance,
)
from quranic_phonemizer.engine.run import perform  # noqa: E402
from quranic_phonemizer.model.address import (  # noqa: E402
    BoundaryPlan,
    Junction,
    Location,
    Script,
    VerseRef,
)
from quranic_phonemizer.render.alphabet import load_alphabet  # noqa: E402
from quranic_phonemizer.render.recite import phonemes_by_word  # noqa: E402
from quranic_phonemizer.riwayat.hafs import (  # noqa: E402
    HAFS,
    corpus,
    ledger,
    lexeme_passes,
    lexicon,
    script_adapter,
)

SNAPSHOTS = ROOT / "tests" / "snapshots" / "phonemes"
ALPHABET = ROOT / "quranic_phonemizer" / "data" / "render" / "ipa.yaml"


#: Modes this harness can actually produce. `continuous` is deliberately not
#: here: it joins *across* verse boundaries, and a harness that runs verse by
#: verse cannot build that plan. It used to be offered anyway, against the
#: continuous snapshot, and reported 84.379% — a number that measured the
#: harness's own limitation and not the pipeline. 1:2:4 is the worked example:
#: the verse oracle ends `…n`, the continuous oracle ends `…n a`.
MODES = ("word", "verse")


def plan_for(mode: str, words: int) -> BoundaryPlan:
    """`word` stops after every word; `verse` joins within a verse and stops at
    its end."""
    if mode == "word":
        return BoundaryPlan((Junction.STOP,) * (words - 1) + (Junction.EDGE,))
    return BoundaryPlan((Junction.JOIN,) * (words - 1) + (Junction.EDGE,))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="word", choices=MODES)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--show", type=int, default=12)
    args = parser.parse_args()

    packed, alphabet = corpus(), load_alphabet(ALPHABET)
    shared = {"lexicon": lexicon(), "ledger": ledger(),
              "passes": lexeme_passes()}
    adapter = script_adapter(Script.UTHMANI)

    matched = total = 0
    bucketed = 0
    mismatches: list[tuple[str, list, list]] = []
    diffs: collections.Counter[str] = collections.Counter()

    with gzip.open(SNAPSHOTS / f"{args.mode}.jsonl.gz", "rt", encoding="utf-8") as fh:
        expected = (json.loads(line) for line in fh)
        for surah in range(1, 115):
            for ayah in range(1, len(packed.surah_info[str(surah)]) + 1):
                count = packed.surah_info[str(surah)][ayah - 1]
                words = tuple(
                    (Location(surah, ayah, w), packed.word(Location(surah, ayah, w)))
                    for w in range(1, count + 1)
                )
                built = build(
                    adapter.read(VerseRef(surah, ayah), words), **shared
                )
                score = built.score
                check_inscription(built.inscription, score)
                performance = perform(
                    score, HAFS, plan_for(args.mode, len(score.words))
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
                    continue
                for index in wrong:
                    got, want = got_words[index], want_words[index]
                    diffs[_signature(got, want)] += 1
                    if len(mismatches) < args.show:
                        mismatches.append(
                            (f"{surah}:{ayah}:{index + 1}", got, want)
                        )
                if args.limit and total >= args.limit:
                    break
            if args.limit and total >= args.limit:
                break

    print(f"{args.mode}: {matched}/{total} words match "
          f"({100 * matched / total:.3f}%)")
    if bucketed:
        # A sound merged across a word boundary has to land in one bucket or
        # the other, and this harness and the old implementation disagree
        # about which -- `قُلُوبِهِم مَّرَضٌ` puts the merged mim on the second
        # word here and on the first there. The verse reads identically. It is
        # a projection API question, not a phoneme one, and counting it as a
        # defect left 1,439 benign rows in a detector whose whole job is to
        # make a real change stand out.
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
