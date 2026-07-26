"""Freeze the pre-refactor public projections as a coverage corpus.

The refactor at ``e0d9fb9`` removed every projection except phonemes. Those
removed views are the only full-corpus record of which graphemes the old
engine believed participated in which Tajweed rule, which were silent, and how
the recited Arabic differed from the source. They are needed as an
*information-coverage* reference for the new internal model: the question they
answer is "can the new model reconstruct this", not "is the old output right".
Several of these views have known defects, catalogued in the design evidence.

The legacy package is not in the working tree. Export it first, then point this
tool at the export:

    $ git archive b3bc53a | tar -x -C /tmp/legacy
    $ python tools/freeze_legacy_baselines.py --legacy-root /tmp/legacy \\
          --revision b3bc53a

Each view is written as gzip-compressed JSON Lines, one line per source word,
plus a manifest recording byte length and SHA-256 for every file.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "research" / "legacy-baselines"
REFERENCE = "1-114"


def _as_plain(value: Any) -> Any:
    """Reduce a legacy DTO to JSON-safe primitives."""
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return {k: _as_plain(v) for k, v in vars(value).items()}
    if isinstance(value, dict):
        return {str(k): _as_plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_as_plain(item) for item in value]
    return value


def _views(result: Any) -> dict[str, Callable[[], Any]]:
    """Projections keyed by the name they had in the legacy API.

    Row granularity is deliberately not normalised. ``phonemes`` and
    ``character_phoneme_mappings`` are one row per source word;
    ``tajweed_mappings`` emits extra rows for expanded muqattaat sub-words;
    ``letter_phoneme_mappings`` is a flat entry stream. Preserving each view's
    own shape is the point, since the divergence between them is itself
    evidence about what the old model could and could not express.
    """
    return {
        "phonemes": lambda: result.phonemes_list("word"),
        "tajweed_mappings": lambda: _as_plain(result.tajweed_mappings())["words"],
        "letter_phoneme_mappings": lambda: _as_plain(
            result.letter_phoneme_mappings()
        )["entries"],
        "character_phoneme_mappings": lambda: _as_plain(
            result.character_phoneme_mappings()
        )["words"],
        "silent_flags": lambda: [list(item) for item in result.silent_flags()],
        "phonetic_text": lambda: result.phonetic_text().splitlines(),
    }


# Views whose row count must equal the source word count; the rest are free.
PER_WORD_VIEWS = frozenset({"phonemes", "character_phoneme_mappings"})


def _jsonl(rows: list[Any]) -> bytes:
    lines = (
        json.dumps(row, ensure_ascii=False, separators=(",", ":"), default=str)
        for row in rows
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _stop_arguments(mode: str, locations: list[str]) -> dict[str, Any]:
    if mode == "continuous":
        return {}
    if mode == "verse":
        return {"stop_signs": ["verse"]}
    return {"stop_refs": locations}


def freeze(legacy_root: Path, revision: str, output_dir: Path) -> None:
    sys.path.insert(0, str(legacy_root))
    from quranic_phonemizer import Phonemizer  # noqa: PLC0415 - legacy import

    output_dir.mkdir(parents=True, exist_ok=True)
    phonemizer = Phonemizer()

    info_path = legacy_root / "quranic_phonemizer" / "resources" / "surah_info.json"
    info = json.loads(info_path.read_text(encoding="utf-8"))
    locations = [
        f"{surah}:{ayah}:{word}"
        for surah in range(1, 115)
        for ayah, count in enumerate(info[str(surah)], start=1)
        for word in range(1, count + 1)
    ]

    manifest: dict[str, Any] = {
        "schema": 1,
        "legacy_revision": revision,
        "reference": REFERENCE,
        "word_count": len(locations),
        "purpose": "information-coverage reference for the new internal model",
        "caveat": "legacy output has known defects; this is not a correctness oracle",
        "encoding": "gzip JSON Lines, one line per source word",
        "modes": {},
    }

    for mode in ("continuous", "verse", "word"):
        result = phonemizer.phonemize(
            REFERENCE, **_stop_arguments(mode, locations)
        )
        entries: dict[str, Any] = {}
        for name, build in _views(result).items():
            rows = build()
            if name in PER_WORD_VIEWS and len(rows) != len(locations):
                raise SystemExit(
                    f"{mode}/{name}: expected {len(locations)} rows, got {len(rows)}"
                )
            content = _jsonl(rows)
            filename = f"{mode}.{name}.jsonl.gz"
            (output_dir / filename).write_bytes(
                gzip.compress(content, compresslevel=9, mtime=0)
            )
            entries[name] = {
                "file": filename,
                "rows": len(rows),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
            print(f"{mode}/{name}: {len(content):,} bytes")
        manifest["modes"][mode] = entries

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="ascii"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-root", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    freeze(args.legacy_root.resolve(), args.revision, args.output.resolve())


if __name__ == "__main__":
    main()
