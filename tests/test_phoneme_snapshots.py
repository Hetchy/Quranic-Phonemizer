"""Phase 6's gate: phoneme parity against the frozen snapshots.
from __future__ import annotations


Skipped until `render/` exists. Kept rather than deleted because it is
the oracle the whole refactor is measured against — the snapshots are
files, so they outlive the implementation that produced them.
"""
import pytest

pytest.skip(
    "render/ lands in phase 6; the snapshots are the gate for it",
    allow_module_level=True,
)


import gzip
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from quranic_phonemizer.api import Phonemizer
from quranic_phonemizer.corpus import load_corpus
from quranic_phonemizer.model import (
    BoundaryMode,
    Consonant,
    Letter,
    Location,
    Riwayah,
    Tanween,
    Vowel,
    VowelQuality,
)
from quranic_phonemizer.parsing import ScriptParser
from quranic_phonemizer.dataio import load_yaml
from quranic_phonemizer.rendering import load_render_config, render_segment
from quranic_phonemizer.resources import resources_for


SNAPSHOTS = Path(__file__).parent / "snapshots" / "phonemes"


def _snapshot_bytes(words: list[list[str]]) -> bytes:
    lines = (
        json.dumps(word, ensure_ascii=False, separators=(",", ":")) for word in words
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


@pytest.mark.parametrize("mode", ["continuous", "verse", "word"])
def test_full_quran_phonemes_match_frozen_legacy(mode: str) -> None:
    manifest = json.loads((SNAPSHOTS / "manifest.json").read_text(encoding="ascii"))
    metadata = manifest["modes"][mode]
    expected = gzip.decompress((SNAPSHOTS / metadata["file"]).read_bytes())
    kwargs = _stop_arguments(mode)
    actual = _snapshot_bytes(
        Phonemizer().phonemize("1-114", **kwargs).phonemes_list("word")
    )

    assert len(actual) == metadata["bytes"]
    assert hashlib.sha256(actual).hexdigest() == metadata["sha256"]
    assert actual == expected


def test_hafs_source_tokenization_is_byte_exact() -> None:
    resources = resources_for(Riwayah.HAFS)
    corpus = load_corpus(resources.corpus, resources.addresses)
    script = ScriptParser(resources.script)

    for location in corpus.locations("1-114"):
        text = corpus.word(location)
        assert script.parse_word(text, location).reconstruct() == text


def test_script_alias_can_normalize_alternate_tanween(
    tmp_path: Path,
) -> None:
    resources = resources_for(Riwayah.HAFS)
    data = load_yaml(resources.script)
    open_dammatan = "\N{ARABIC OPEN DAMMATAN}"
    data["aliases"][open_dammatan] = Tanween.DAMM.value
    path = tmp_path / "script.yaml"
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    word = ScriptParser(path).parse_word(f"ب{open_dammatan}", Location(1, 1, 1))

    assert word.reconstruct() == f"ب{open_dammatan}"
    assert word.letters[0].form.tanween is Tanween.DAMM


def test_recitation_retains_source_segments_and_boundaries() -> None:
    result = Phonemizer().phonemize("11:41:6")
    word = result.recitation.words[0]

    assert word.source.reconstruct() == word.source.text
    assert any(
        isinstance(segment, Vowel) and segment.quality is VowelQuality.IMALA
        for segment in word.segments
    )
    assert word.boundary_after is BoundaryMode.EDGE


@pytest.mark.parametrize(
    ("ref", "stop_refs", "expected"),
    [
        ("41:44:9", (), ["ʔ", "a", "ʔ", "a", "ʕ", "ʒ", "a", "m", "i", "jj"]),
        ("11:41:6", (), ["m", "a", "ʒ", "Q", "r", "i:", "h", "a:"]),
        ("27:36:8", ("27:36:8",), ["ʔ", "a:", "t", "a:", "n"]),
        (
            "2:72:4",
            (),
            ["f", "a", "dd", "a:", "rˤ", "aˤ", "ʔ", "t", "u", "m"],
        ),
        ("21:88:7", (), ["n", "u", "ŋ", "ʒ", "i:"]),
        ("10:79:3", (), ["ʔ", "i:", "t", "u:", "n", "i:"]),
    ],
)
def test_hafs_contextual_pronunciations_are_preserved(
    ref: str,
    stop_refs: tuple[str, ...],
    expected: list[str],
) -> None:
    result = Phonemizer().phonemize(ref, stop_refs=stop_refs)

    assert result.phonemes_list() == [expected]


def test_unimplemented_warsh_phonology_fails_closed() -> None:
    with pytest.raises(NotImplementedError):
        Phonemizer(Riwayah.WARSH)


def test_stop_api_preserves_legacy_stop_signs_and_refs() -> None:
    by_sign = Phonemizer().phonemize("112", stop_signs=["verse"])
    by_ref = Phonemizer().phonemize(
        "112",
        stop_refs=["112:1:4", "112:2:2", "112:3:5"],
    )

    assert by_sign.phonemes_list() == by_ref.phonemes_list()
    assert by_sign.stop_signs == ["verse"]
    assert by_ref.stop_refs == ["112:1:4", "112:2:2", "112:3:5"]


def test_invalid_stop_sign_fails_with_stable_message() -> None:
    with pytest.raises(ValueError, match=r"Invalid stop sign types: \['bad'\]"):
        Phonemizer().phonemize("1:1", stop_signs=["bad"])


def test_geminated_emphatic_consonant_is_one_inventory_token() -> None:
    resources = resources_for(Riwayah.HAFS)
    config = load_render_config(resources.render)

    assert (
        render_segment(Consonant(Letter.RA, geminated=True, emphatic=True), config)
        == "rˤrˤ"
    )


def _stop_arguments(mode: str) -> dict[str, tuple[str, ...]]:
    if mode == "continuous":
        return {}
    if mode == "verse":
        return {"stop_signs": ("verse",)}
    resources = resources_for(Riwayah.HAFS)
    corpus = load_corpus(resources.corpus, resources.addresses)
    return {"stop_refs": tuple(str(location) for location in corpus.locations("1-114"))}
