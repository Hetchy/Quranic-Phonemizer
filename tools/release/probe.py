"""Digest one reading per line, under whichever public API the install has.

This runs inside the release venv as well as the working tree, so it may only
use surfaces old releases already published. `analyse` and typed documents are
recent; `phonemize` and per-word phonemes go back further.

    python tools/release/probe.py --riwayah hafs --refs refs.txt --out digests.jsonl

One verse is requested at a time and released before the next, because a
surah-wide or corpus-wide request keeps its whole score alive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

#: Both extreme boundary plans: read straight through, and stopped everywhere.
PLANS = ("straight", "stopped")


def _capabilities(reader) -> dict:
    return {
        "analyse": hasattr(reader, "analyse"),
        "documents": hasattr(reader, "analyse") and hasattr(
            reader.analyse("1:1"), "document"
        ),
    }


def _read(reader, ref: str, stops: tuple[str, ...], able: dict):
    call = reader.analyse if able["analyse"] else reader.phonemize
    return call(ref, stop_refs=stops)


def _word_refs(result) -> tuple[str, ...]:
    """Word references, however this release spells them."""
    words = result.words
    if words and hasattr(words[0], "ref"):
        return tuple(word.ref for word in words)
    return tuple(str(word.location) for word in words)


def _structure(result) -> str | None:
    """The typed documents, which only recent releases publish."""
    if not hasattr(result, "document"):
        return None
    return json.dumps(
        [
            result.document("analysis_result"),
            result.document("cell_view", spelling="transformed"),
        ],
        ensure_ascii=False, sort_keys=True, default=str,
    )


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _reading(reader, ref: str, plan: str, able: dict) -> dict:
    straight = _read(reader, ref, (), able)
    stops = _word_refs(straight) if plan == "stopped" else ()
    result = _read(reader, ref, stops, able) if stops else straight
    words = [list(word) for word in result.phonemes(by="word")]
    structure = _structure(result)
    return {
        "ref": ref,
        "plan": plan,
        "refs": list(_word_refs(result)),
        "words": words,
        "phonemes_digest": _digest(json.dumps(words)),
        "structure_digest": None if structure is None else _digest(structure),
        "structure": structure,
    }


def _emit(row: dict, detail: bool) -> str:
    keep = ("ref", "plan", "phonemes_digest", "structure_digest")
    if detail:
        keep += ("refs", "words", "structure")
    return json.dumps({key: row[key] for key in keep}, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--riwayah", default="hafs")
    parser.add_argument("--refs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--detail", action="store_true")
    args = parser.parse_args()

    from quranic_phonemizer import Phonemizer, supported_riwayat

    if args.riwayah not in {str(name) for name in supported_riwayat()}:
        args.out.write_text("", encoding="utf-8")
        print(json.dumps({"unsupported_riwayah": args.riwayah}))
        return 0

    reader = Phonemizer(riwayah=args.riwayah)
    able = _capabilities(reader)
    refs = args.refs.read_text(encoding="utf-8").split()
    with args.out.open("w", encoding="utf-8") as sink:
        for ref in refs:
            for plan in PLANS:
                try:
                    row = _reading(reader, ref, plan, able)
                except Exception as error:  # noqa: BLE001 - a failure is a finding
                    sink.write(json.dumps({
                        "ref": ref, "plan": plan,
                        "error": f"{type(error).__name__}: {error}",
                    }) + "\n")
                    continue
                sink.write(_emit(row, args.detail) + "\n")
    print(json.dumps({"capabilities": able, "verses": len(refs)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
