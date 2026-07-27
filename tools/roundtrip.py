"""ADR-005 §4's gate: every Score can be spelled, and spells back to itself.

    text -> read -> build -> Score
                              |
                            write -> text' -> read -> build -> Score'
    assert Score == Score'

Not byte-identity with the source. `read` deliberately discards what the Score
does not need — Uthmani's dagger is an abbreviation of a haraka plus a carrier
and both give the same slot — so demanding `text' == text` would be demanding
that the canonical layer keep script detail, which is the opposite of the
design. What §4 actually asks is whether the layer holds anything no
orthography can express, and Score → text → Score answers exactly that.

A `WriteError` is the real failure: it means a canonical fact this script has
no scalar for. A digest mismatch is weaker — the spelling was legal but was
read back as a different Score — and its shapes are reported separately.

Run:  python tools/roundtrip.py [--script uthmani|indopak] [--limit N]
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
from quranic_phonemizer.model.address import Location, Script, VerseRef  # noqa: E402
from quranic_phonemizer.orthography.write import (  # noqa: E402
    WriteError,
    pen_for,
    write_verse,
)
from quranic_phonemizer.riwayat.hafs import (  # noqa: E402
    ledger,
    lexeme_passes,
    lexicon,
    script_adapter,
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
            return f"nucleus {a.nucleus.kind.value}->{b.nucleus.kind.value}"
    return "equal digest but unequal"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", default="uthmani",
                        choices=[s.value for s in Script])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--show", type=int, default=8)
    args = parser.parse_args()

    script = Script(args.script)
    adapter = script_adapter(script)
    pen = pen_for(adapter.inventory)
    shared = {"lexicon": lexicon(), "ledger": ledger(),
              "passes": lexeme_passes()}
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
        before = build(adapter.read(ref, verses[key]), **shared).score
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
            after = build(adapter.read(ref, words), **shared).score
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
