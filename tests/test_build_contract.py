"""What `canon.build` requires of its caller, and what it promises back."""
from __future__ import annotations

import inspect

import pytest

from quranic_phonemizer.canon.build import build
from quranic_phonemizer.model.address import Script, VerseRef


def _reading(hafs, surah: int = 112, ayah: int = 2):
    verse = VerseRef(surah, ayah)
    return hafs.read(Script.UTHMANI, verse, hafs.words(verse))


def test_a_pass_list_never_arrives_by_default(hafs) -> None:
    """A riwayah that forgot its own passes used to get the shared two and a
    working pipeline that was not its own."""
    assert inspect.signature(build).parameters["passes"].default is inspect.Parameter.empty
    with pytest.raises(TypeError, match="passes"):
        build(_reading(hafs), lexicon=hafs.lexicon, ledger=hafs.ledger)
