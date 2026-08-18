"""Import the Digital Khatt IndoPak Hafs text as a second editable script source.

Drops each ayah's end-of-ayah token and applies listed word splits to word-align with Uthmani.

Run: python tools/import_indopak_source.py --input path/to/source.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "corpus_sources" / "hafs" / "scripts"
DST = SCRIPTS_DIR / "indopak" / "quran.json"
SURAH_INFO = (
    REPO_ROOT
    / "quranic_phonemizer"
    / "data"
    / "riwayat"
    / "hafs"
    / "corpus"
    / "surah_info.json"
)

END_OF_AYAH = "\N{ARABIC END OF AYAH}"
SUKUN = "\N{ARABIC SUKUN}"

# (surah, ayah, upstream word) -> leading prefix that becomes the first split word.
SPLIT_WORDS = {(37, 130, 3): "اِلْ"}


def _key(surah: int, ayah: int, word: int) -> str:
    return f"{surah}:{ayah}:{word}"


def _load_upstream(path: Path) -> dict[tuple[int, int, int], str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    words: dict[tuple[int, int, int], str] = {}
    for entry in raw.values():
        text = entry["text"]
        if END_OF_AYAH in text:
            continue
        location = (int(entry["surah"]), int(entry["ayah"]), int(entry["word"]))
        words[location] = text
    return words


def _apply_splits(
    words: dict[tuple[int, int, int], str],
) -> dict[tuple[int, int, int], str]:
    """Split the listed words, shifting the rest of their ayah up by one."""
    result: dict[tuple[int, int, int], str] = {}
    shifted: Counter[tuple[int, int]] = Counter()
    for (surah, ayah, word), text in sorted(words.items()):
        target = word + shifted[(surah, ayah)]
        prefix = SPLIT_WORDS.get((surah, ayah, word))
        if prefix is None:
            result[(surah, ayah, target)] = text
            continue
        if not text.startswith(prefix):
            raise SystemExit(
                f"{_key(surah, ayah, word)}: expected the word to start with "
                f"{prefix!r} but found {text!r}; the upstream text changed."
            )
        if not prefix.endswith(SUKUN):
            raise SystemExit(
                f"{_key(surah, ayah, word)}: split prefix {prefix!r} does not "
                "end on a sukun, so the boundary is not a safe split point."
            )
        result[(surah, ayah, target)] = prefix
        result[(surah, ayah, target + 1)] = text[len(prefix) :]
        shifted[(surah, ayah)] += 1
    return result


def _validate(words: dict[tuple[int, int, int], str]) -> None:
    info = json.loads(SURAH_INFO.read_text(encoding="utf-8"))
    expected_total = sum(count for surah in info.values() for count in surah)
    if len(words) != expected_total:
        raise SystemExit(
            f"IndoPak source has {len(words)} words but surah_info.json implies "
            f"{expected_total}."
        )

    counts: Counter[tuple[int, int]] = Counter()
    for surah, ayah, _ in words:
        counts[(surah, ayah)] += 1

    mismatched = []
    for surah in range(1, 115):
        for ayah, expected in enumerate(info[str(surah)], start=1):
            actual = counts.get((surah, ayah), 0)
            if actual != expected:
                mismatched.append((surah, ayah, expected, actual))
    if mismatched:
        preview = ", ".join(
            f"{surah}:{ayah} expected {expected} got {actual}"
            for surah, ayah, expected, actual in mismatched[:5]
        )
        raise SystemExit(
            f"{len(mismatched)} ayahs have a different word count: {preview}"
        )

    for surah, ayah, word in words:
        if word < 1 or word > counts[(surah, ayah)]:
            raise SystemExit(f"Out-of-range word number at {_key(surah, ayah, word)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DST)
    args = parser.parse_args()

    words = _apply_splits(_load_upstream(args.input.resolve()))
    _validate(words)

    payload = {
        _key(*location): {"location": _key(*location), "text": text}
        for location, text in sorted(words.items())
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output}: {len(payload):,} word slots")


if __name__ == "__main__":
    main()
