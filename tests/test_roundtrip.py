"""Phase 2: ADR-005 §4. Every Score can be spelled, and spells back to itself.

The gate §4 states is **totality** — no Score holds a fact the orthography
cannot express — and that is what `WriteError` would report. The digest
round-trip is a stronger claim layered on top, and its residue is named in
`docs/adr/phase-2-report.md` rather than hidden.

Not byte-identity with the source. `read` deliberately discards what the Score
does not need, so demanding `text' == text` would demand that the canonical
layer keep script detail — the opposite of the design.
"""
from __future__ import annotations

import pytest

from conftest import built_for, words_of
from quranic_phonemizer.canon.build import build
from quranic_phonemizer.model.address import Location, Script, VerseRef
from quranic_phonemizer.orthography.write import Pen, WriteError, pen_for, write_verse
from quranic_phonemizer.riwayat.hafs import script_adapter

VERSES = [(1, 1), (1, 7), (2, 2), (7, 1), (18, 1), (36, 1), (112, 1), (114, 6)]


@pytest.fixture(scope="module")
def pen() -> Pen:
    return pen_for(script_adapter(Script.UTHMANI).inventory)


@pytest.mark.parametrize(("surah", "ayah"), VERSES)
def test_every_score_can_be_spelled(packed, shared, pen, surah, ayah):
    """Totality — the gate itself. A `WriteError` means the canonical layer is
    holding something no orthography can express, which is the shape of a
    missing layer."""
    score = built_for(packed, shared, surah, ayah).score
    spelled = write_verse(score, pen)
    assert len(spelled) == len(score.words)
    assert all(text for text in spelled)


@pytest.mark.parametrize(("surah", "ayah"), VERSES)
def test_spelling_reads_back_to_the_same_score(packed, shared, pen, surah, ayah):
    score = built_for(packed, shared, surah, ayah).score
    spelled = write_verse(score, pen)
    words = tuple(
        (Location(surah, ayah, index + 1), text)
        for index, text in enumerate(spelled)
    )
    again = build(
        script_adapter(Script.UTHMANI).read(VerseRef(surah, ayah), words),
        **shared,
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
