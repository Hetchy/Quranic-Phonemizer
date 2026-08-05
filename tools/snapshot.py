"""Which words this checkout reads differently. A floor says only how many.

Run: python tools/snapshot.py write PATH [--mode word|verse|continuous|alignment]
     python tools/snapshot.py diff OLD NEW [--show N]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from quranic_phonemizer import Phonemizer  # noqa: E402
from quranic_phonemizer.api import alphabet as load_alphabet  # noqa: E402
from quranic_phonemizer.api import recitation  # noqa: E402
from quranic_phonemizer.model.address import Riwayah, Script  # noqa: E402
from quranic_phonemizer.phonemize.legacy_views import phonemes_by_word  # noqa: E402
from tools.parity import MODES, plan_for, units  # noqa: E402

ALIGNMENT = "alignment"


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


def _join(values) -> str:
    return ",".join(str(v) for v in values)


def _pairing(result, pairing) -> list[str]:
    """Rules by name: an index into `rules` does not survive a change."""
    return [
        f"glyphs={_join(pairing.glyphs)}",
        f"sounds={_join(pairing.sounds)}",
        f"shares={_join(pairing.shares)}",
        f"silent={_join(pairing.silent)}",
        f"rules={_join(sorted(result.rules[i].rule.value for i in pairing.rules))}",
        f"after={pairing.after}",
    ]


def _word_of(glyphs, indices, fallback: int) -> int:
    """A gap pairing writes no glyph, so it counts against its neighbour."""
    for index in indices:
        word = glyphs[index].word
        if word is not None:
            return word
    return fallback


def _digests(result, lines: dict[tuple[int, str], list[str]]) -> None:
    """One line per row, bucketed by the word it falls in."""
    word = 0
    for text in ("source", "recited"):
        glyphs = result.glyphs if text == "source" else result.rendered
        for pairing in result.alignment(text=text, grouping="glyph"):
            word = _word_of(glyphs, pairing.glyphs, word)
            lines.setdefault((word, text), []).extend(_pairing(result, pairing))
    # A block names source and recited *pairings*, so its glyphs come through
    # the cell alignment it was built from.
    cells = result.alignment(text="source", grouping="cell")
    for block in result.respelling(grouping="cell"):
        written = [g for cell in block.source for g in cells[cell].glyphs]
        word = _word_of(result.glyphs, written, word)
        lines.setdefault((word, "respell"), []).append(
            f"{_join(block.source)}>{_join(block.recited)}"
        )


def _views(ref: str, result):
    """Who owns each sound, and how the two texts pair, per word. A digest:
    the whole view is megabytes, and what a diff needs is where it moved."""
    lines: dict[tuple[int, str], list[str]] = {}
    _digests(result, lines)
    for (word, view), rows in sorted(lines.items()):
        blob = "\n".join(rows).encode("utf-8")
        yield {
            "ref": f"{ref}:{word + 1}|{view}",
            "tokens": [hashlib.sha256(blob).hexdigest()[:12]],
        }


def _alignment_rows(limit: int | None = None):
    """One row per pairing, over every verse, through the public surface."""
    hafs, phonemizer = recitation(Riwayah.HAFS), Phonemizer()
    for seen, (verse, _) in enumerate(units(hafs, "verse")):
        if limit is not None and seen >= limit:
            return
        ref = f"{verse.surah}:{verse.ayah}"
        yield from _views(ref, phonemizer.phonemize(ref))


def write(path: pathlib.Path, mode: str, limit: int | None = None) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = _alignment_rows(limit) if mode == ALIGNMENT else _rows(mode)
    count = 0
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    noun = "rows" if mode == ALIGNMENT else "words"
    print(f"{mode}: wrote {count} {noun} to {path}")
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
    w.add_argument("--mode", default="word", choices=(*MODES, ALIGNMENT))
    w.add_argument("--limit", type=int, default=None, help="first N verses")
    d = sub.add_parser("diff")
    d.add_argument("old", type=pathlib.Path)
    d.add_argument("new", type=pathlib.Path)
    d.add_argument("--show", type=int, default=20)
    args = parser.parse_args()

    if args.action == "write":
        return write(args.path, args.mode, args.limit)
    return diff(args.old, args.new, args.show)


if __name__ == "__main__":
    raise SystemExit(main())
