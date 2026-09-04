"""Import the King Fahd Warsh text as an editable word-level source.

Run: python tools/import_warsh_source.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WARSH_DIR = REPO_ROOT / "corpus_sources" / "warsh"
SRC = WARSH_DIR / "upstream" / "king-fahd-v2.json"
DST = WARSH_DIR / "scripts" / "king-fahd" / "quran.json"

EXPECTED_SOURCE_SHA256 = (
    "c6017e688cc599d88f6fdb1a19cafc9c51d024b3530955f1a878f17d26b9bcbc"
)
EXPECTED_VERSES = 6_214
EXPECTED_WORDS = 77_425
EXPECTED_PRESENTATION_MARKERS = EXPECTED_VERSES
EXPECTED_RIGHT_TO_LEFT_MARKS = 14
EXPECTED_RUB_MARKERS = 435

RUB_EL_HIZB = "\N{ARABIC START OF RUB EL HIZB}"
RIGHT_TO_LEFT_MARK = "\N{RIGHT-TO-LEFT MARK}"


def _is_presentation_marker(char: str) -> bool:
    return 0xFB50 <= ord(char) <= 0xFDFF


def _load_source(path: Path) -> list[dict]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED_SOURCE_SHA256:
        raise SystemExit(
            f"Unexpected upstream SHA-256 for {path}: {digest}. Review the "
            "new source before changing the pinned digest."
        )
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or len(raw) != EXPECTED_VERSES:
        raise SystemExit(
            f"Expected {EXPECTED_VERSES:,} verse records, found {len(raw):,}."
        )
    return raw


def _clean_verse(text: str) -> tuple[str, Counter[str]]:
    removed: Counter[str] = Counter()
    kept = []
    for char in text:
        if _is_presentation_marker(char) or char == RIGHT_TO_LEFT_MARK:
            removed[char] += 1
        else:
            kept.append(char)
    return "".join(kept), removed


def _word_payload(records: list[dict]) -> tuple[dict[str, dict], Counter[str]]:
    payload: dict[str, dict] = {}
    removed: Counter[str] = Counter()
    previous = (0, 0)
    running_id = 1

    for record in records:
        surah = int(record["sura_no"])
        ayah = int(record["aya_no"])
        location = (surah, ayah)
        if location <= previous:
            raise SystemExit(f"Verse records are out of order at {surah}:{ayah}.")
        previous = location

        cleaned, verse_removed = _clean_verse(record["aya_text"])
        presentation_count = sum(
            count
            for char, count in verse_removed.items()
            if _is_presentation_marker(char)
        )
        if presentation_count != 1:
            raise SystemExit(
                f"{surah}:{ayah} has {presentation_count} presentation markers; "
                "expected exactly one verse-number glyph."
            )
        removed.update(verse_removed)

        words = [word for word in cleaned.split() if word != RUB_EL_HIZB]
        removed[RUB_EL_HIZB] += len(cleaned.split()) - len(words)
        for position, text in enumerate(words, start=1):
            key = f"{surah}:{ayah}:{position}"
            payload[key] = {
                "id": running_id,
                "surah": str(surah),
                "ayah": str(ayah),
                "word": str(position),
                "location": key,
                "text": text,
            }
            running_id += 1

    return payload, removed


def _validate(payload: dict[str, dict], removed: Counter[str]) -> None:
    expected = {
        "word slots": (len(payload), EXPECTED_WORDS),
        "presentation markers": (
            sum(
                count
                for char, count in removed.items()
                if _is_presentation_marker(char)
            ),
            EXPECTED_PRESENTATION_MARKERS,
        ),
        "right-to-left marks": (
            removed[RIGHT_TO_LEFT_MARK],
            EXPECTED_RIGHT_TO_LEFT_MARKS,
        ),
        "rub el hizb markers": (removed[RUB_EL_HIZB], EXPECTED_RUB_MARKERS),
    }
    mismatches = [
        f"{name}: expected {wanted:,}, found {actual:,}"
        for name, (actual, wanted) in expected.items()
        if actual != wanted
    ]
    if mismatches:
        raise SystemExit("Import validation failed: " + "; ".join(mismatches))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=SRC)
    parser.add_argument("--output", type=Path, default=DST)
    args = parser.parse_args()

    payload, removed = _word_payload(_load_source(args.input.resolve()))
    _validate(payload, removed)

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {output}: {len(payload):,} word slots")


if __name__ == "__main__":
    main()
