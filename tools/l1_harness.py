"""Compare Uthmani and IndoPak canon-built scores field by field; residue should be empty.

Also reports the provenance split and the `Decorates` count alongside the residue.

Run: python tools/l1_harness.py [--limit N] [--show CLASS]
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from quranic_phonemizer.canon.build import Provenance, build  # noqa: E402
from quranic_phonemizer.model.address import (  # noqa: E402
    Location,
    Script,
    VerseRef,
)
from quranic_phonemizer.riwayat.hafs import (  # noqa: E402
    ledger,
    lexeme_passes,
    lexicon,
    script_adapter,
)

SOURCES = ROOT / "corpus_sources" / "riwayat" / "hafs" / "scripts"


def load_verses(script: str) -> dict[tuple[int, int], list[tuple[Location, str]]]:
    raw = json.loads((SOURCES / script / "quran.json").read_text(encoding="utf-8"))
    verses: dict[tuple[int, int], list[tuple[Location, str]]] = (
        collections.defaultdict(list)
    )
    for key, record in raw.items():
        surah, ayah, word = (int(part) for part in key.split(":"))
        verses[(surah, ayah)].append((Location(surah, ayah, word), record["text"]))
    for words in verses.values():
        words.sort(key=lambda pair: pair[0].word)
    return verses


def describe(slot) -> str:
    quality = getattr(slot.nucleus, "quality", None)
    nucleus = slot.nucleus.kind.value + (f":{quality.value}" if quality else "")
    onset = "" if slot.onset.value == "plain" else f"/{slot.onset.value}"
    return f"[{slot.letter.value}{onset} {nucleus}]"


def compare(a, b) -> list[tuple[int, str, str, str]]:
    """Residue rows: (ordinal, field, uthmani_value, indopak_value)."""
    left, right = a.slots(), b.slots()
    if len(left) != len(right):
        return [(-1, "count", str(len(left)), str(len(right)))]
    rows = []
    for ordinal, (x, y) in enumerate(zip(left, right)):
        for field in ("letter", "onset", "nucleus", "spelled"):
            if getattr(x, field) != getattr(y, field):
                rows.append((ordinal, field, describe(x), describe(y)))
    return rows


def _successors(order) -> dict:
    return {key: order[i + 1] for i, key in enumerate(order[:-1])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--show", default="")
    parser.add_argument("--examples", type=int, default=10)
    args = parser.parse_args()

    uthmani, indopak = load_verses("uthmani"), load_verses("indopak")
    order = sorted(uthmani)
    successor = _successors(order)
    assert set(uthmani) == set(indopak), "the two corpora disagree on verses"

    adapters = {s: script_adapter(s) for s in Script}
    shared = {"lexicon": lexicon(), "ledger": ledger(),
              "passes": lexeme_passes()}
    tracks = {s: Provenance() for s in Script}

    residue: collections.Counter[str] = collections.Counter()
    examples: dict[str, list] = collections.defaultdict(list)
    words_seen = slots_seen = 0

    for index, key in enumerate(sorted(uthmani)):
        if args.limit and index >= args.limit:
            break
        verse = VerseRef(*key)
        scores = {}
        for script, source in ((Script.UTHMANI, uthmani), (Script.INDOPAK, indopak)):
            reading = adapters[script].read(verse, tuple(source[key]))
            following = successor.get(key)
            right = (
                adapters[script].read(VerseRef(*following), tuple(source[following]))
                if following
                else None
            )
            scores[script] = build(
                reading, provenance=tracks[script], right_context=right, **shared
            ).score
        words_seen += len(uthmani[key])
        slots_seen += len(scores[Script.UTHMANI].slots())

        for ordinal, field, left, right in compare(
            scores[Script.UTHMANI], scores[Script.INDOPAK]
        ):
            residue[field] += 1
            if len(examples[field]) < args.examples:
                examples[field].append((str(verse), ordinal, left, right))

    total = sum(residue.values())
    print(f"verses {index + 1}  words {words_seen}  slots {slots_seen}")
    print(f"\nL1 residue: {total}")
    for field, count in residue.most_common():
        print(f"   {field:10s} {count}")

    print("\nprovenance - a zero residue reached by a rising")
    print("Decorates count is not a proof of script-independence:")
    for script, track in tracks.items():
        print(
            f"   {script.value:8s} evidence {track.from_evidence:7d} "
            f"derivation {track.from_derivation:7d} ledger {track.from_ledger:5d} "
            f"decorates {track.decorated:6d} attests {track.attested:6d}"
        )
    print("\nderivation use:")
    names = sorted(
        set(tracks[Script.UTHMANI].derivation_uses)
        | set(tracks[Script.INDOPAK].derivation_uses)
    )
    for name in names:
        u = tracks[Script.UTHMANI].derivation_uses.get(name, 0)
        i = tracks[Script.INDOPAK].derivation_uses.get(name, 0)
        print(f"   {name:22s} uthmani {u:7d}   indopak {i:7d}")

    if args.show:
        print(f"\n--- {args.show}")
        for row in examples[args.show]:
            print("   ", row)
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
