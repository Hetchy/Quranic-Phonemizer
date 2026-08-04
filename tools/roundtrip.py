"""Check that every Score can be spelled and read back to an identical Score.

    text -> read -> build -> Score -> write -> text' -> read -> build -> Score'

Run: python tools/roundtrip.py [--script uthmani|indopak] [--limit N]
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

from quranic_phonemizer.api import recitation  # noqa: E402
from quranic_phonemizer.model.address import (  # noqa: E402
    Location,
    Riwayah,
    Script,
    VerseRef,
)
from quranic_phonemizer.orthography.write import (  # noqa: E402
    WriteError,
    pen_for,
    write_verse,
)


def _shape(before, after) -> str:
    """Where the two Scores first disagree, as a class rather than a site."""
    left, right = before.slots(), after.slots()
    if len(left) != len(right):
        return f"slot count {len(left)}v{len(right)}"
    for a, b in zip(left, right):
        if a.letter is not b.letter:
            return f"letter {a.letter.value}->{b.letter.value}"
        if a.onset is not b.onset:
            return f"onset {a.onset.value}->{b.onset.value}"
        if a.nucleus != b.nucleus:
            return f"nucleus {a.nucleus}->{b.nucleus}"
        if a.origin is not b.origin:
            return f"origin {a.origin.value}->{b.origin.value}"
        if a.annotations != b.annotations:
            return (f"annotations {sorted(x.value for x in a.annotations)}"
                    f"->{sorted(x.value for x in b.annotations)}")
    if [w.sakt_after for w in before.words] != [w.sakt_after for w in after.words]:
        return "sakt_after"
    return "equal digest but unequal"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default="uthmani",
                        choices=[s.value for s in Script])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--show", type=int, default=8)
    args = parser.parse_args()

    script = Script(args.script)
    hafs = recitation(Riwayah.HAFS)
    pen = pen_for(hafs.inventory(script), hafs.muqattaat.named_by())
    verses = load_verses(script.value)

    closed = total = 0
    unspellable = 0
    shapes: collections.Counter[str] = collections.Counter()
    examples: list[tuple[str, str]] = []

    for key in sorted(verses):
        if args.limit and total >= args.limit:
            break
        ref = VerseRef(*key)
        total += 1
        before = hafs.build(hafs.read(script, ref, verses[key])).score
        try:
            spelled = write_verse(before, pen)
        except WriteError as error:
            unspellable += 1
            shapes[f"WriteError: {error}"] += 1
            continue
        words = tuple(
            (Location(key[0], key[1], index + 1), text)
            for index, text in enumerate(spelled)
        )
        try:
            after = hafs.build(hafs.read(script, ref, words)).score
        except Exception as error:  # noqa: BLE001 - reported, not swallowed
            shapes[f"unreadable: {type(error).__name__}"] += 1
            if len(examples) < args.show:
                examples.append((f"{ref}", str(error)[:100]))
            continue
        if after.digest == before.digest:
            closed += 1
            continue
        shape = _shape(before, after)
        shapes[shape] += 1
        if len(examples) < args.show:
            examples.append((f"{ref}", f"{shape}   {spelled[:2]}"))

    print(f"{script.value}: {closed}/{total} verses round-trip "
          f"({100 * closed / total:.3f}%)")
    print(f"   unspellable (WriteError): {unspellable}")
    if shapes:
        print("\ndisagreement shapes:")
        for shape, count in shapes.most_common(12):
            print(f"   {count:6d}  {shape}")
        print("\nexamples:")
        for ref, detail in examples:
            print(f"   {ref:10s} {detail}")
    return 0 if closed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
