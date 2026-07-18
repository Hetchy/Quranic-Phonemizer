from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

from quranic_phonemizer.api import Phonemizer
from quranic_phonemizer.corpus import load_corpus
from quranic_phonemizer.model import Riwayah
from quranic_phonemizer.resources import resources_for


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "tests" / "snapshots" / "phonemes"


def _git_revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _snapshot_bytes(words: list[list[str]]) -> bytes:
    lines = (
        json.dumps(word, ensure_ascii=False, separators=(",", ":")) for word in words
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _write_gzip(path: Path, content: bytes) -> None:
    path.write_bytes(gzip.compress(content, compresslevel=9, mtime=0))


def freeze(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    phonemizer = Phonemizer()
    word_count = len(phonemizer.phonemize("1-114").recitation.words)
    resources = resources_for(Riwayah.HAFS)
    corpus = load_corpus(resources.corpus, resources.addresses)
    modes = {
        "continuous": {},
        "verse": {"stop_signs": ("verse",)},
        "word": {
            "stop_refs": tuple(str(location) for location in corpus.locations("1-114"))
        },
    }
    manifest = {
        "schema": 1,
        "source_revision": _git_revision(),
        "reference": "1-114",
        "word_count": word_count,
        "encoding": "utf-8 JSON array per source word, gzip compressed",
        "modes": {},
    }

    for name, stop_arguments in modes.items():
        result = phonemizer.phonemize("1-114", **stop_arguments)
        words = result.phonemes_list("word")
        if len(words) != word_count:
            raise RuntimeError(f"{name}: expected {word_count} words, got {len(words)}")

        content = _snapshot_bytes(words)
        filename = f"{name}.jsonl.gz"
        _write_gzip(output_dir / filename, content)
        manifest["modes"][name] = {
            "file": filename,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        print(f"{name}: {len(content)} bytes")

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="ascii",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    freeze(args.output.resolve())


if __name__ == "__main__":
    main()
