"""Every Score can be spelled, and spells back to itself.

Not byte-identity with the source: `read` discards script detail the
Score does not need.
"""
from __future__ import annotations

import pytest
from conftest import built_for

from quranic_phonemizer.model.address import Location, Script, VerseRef
from quranic_phonemizer.orthography.write import Pen, WriteError, pen_for, write_verse
from quranic_phonemizer.riwayat.hafs import muqattaat, script_adapter

pytestmark = pytest.mark.audit

VERSES = [(1, 1), (1, 7), (2, 2), (7, 1), (18, 1), (36, 1), (112, 1), (114, 6)]


@pytest.fixture(scope="module")
def pen() -> Pen:
    return pen_for(script_adapter(Script.UTHMANI).inventory,
                   muqattaat().named_by())


@pytest.mark.parametrize(("surah", "ayah"), VERSES)
def test_every_score_can_be_spelled(packed, hafs, pen, surah, ayah):
    """A `WriteError` means the canonical layer holds a fact no orthography
    can express."""
    score = built_for(packed, hafs, surah, ayah).score
    spelled = write_verse(score, pen)
    assert len(spelled) == len(score.words)
    assert all(text for text in spelled)


@pytest.mark.parametrize(("surah", "ayah"), VERSES)
def test_spelling_reads_back_to_the_same_score(packed, hafs, pen, surah, ayah):
    score = built_for(packed, hafs, surah, ayah).score
    spelled = write_verse(score, pen)
    words = tuple(
        (Location(surah, ayah, index + 1), text)
        for index, text in enumerate(spelled)
    )
    again = hafs.build(
        hafs.read(Script.UTHMANI, VerseRef(surah, ayah), words)
    ).score
    assert again.digest == score.digest


def test_the_pen_is_total_over_the_alphabet(pen):
    """`write` must cover `CanonLetter`, not most of it. Falsified by a letter
    the inventory declares only as rasm."""
    from quranic_phonemizer.model.canon import CanonLetter

    missing = sorted(
        letter.value for letter in CanonLetter if letter not in pen.letters
    )
    assert not missing, f"no scalar writes {missing}"


def test_an_unwritable_fact_raises_rather_than_guessing(pen):
    """A `Pen` with nothing in it must fail loudly. Silently emitting an empty
    string would make the round-trip pass while spelling nothing."""
    empty = Pen(letters={}, roles={}, onsets={}, carriers={})
    with pytest.raises(WriteError):
        empty.letter(next(iter(pen.letters)))
