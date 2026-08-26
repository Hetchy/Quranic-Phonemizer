"""Closed registers and canonical precedence for fixed Warsh inclination."""
from __future__ import annotations

from collections import Counter

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Location, Riwayah, Script
from quranic_phonemizer.model.canon import Quality
from quranic_phonemizer.riwayat.warsh.inclination import (
    FIXED_KUBRA,
    HAA_OPENINGS,
    HAA_VERSE_HEADS,
    LAM_DHAT_YAA,
    LAM_VERSE_HEADS,
    RAA_OPENINGS,
    VERSE_HEAD_SURAHS,
    mark_sequence_family,
)
from quranic_phonemizer.riwayat.warsh.resources import corpus


def _score_word(location: Location):
    package = recitation(Riwayah.WARSH)
    words = package.words(location.verse)
    built = package.build(package.read(Script.UTHMANI, location.verse, words))
    return built.score.words[location.word - 1]


def _qualities(location: Location) -> tuple[Quality, ...]:
    return tuple(
        slot.nucleus.stopped.quality
        for slot in _score_word(location).slots
        if slot.nucleus.stopped.quality is not None
    )


def test_the_u06ea_sequence_partition_is_exhaustive():
    counts = Counter()
    for entry in corpus().entries.values():
        for offset, char in enumerate(entry.text):
            if char == "۪":
                counts[mark_sequence_family(entry.text, offset)] += 1

    assert counts == Counter({
        "initial_alif": 692,
        "carrier": 1700,
        "dagger": 145,
        "special": 32,
    })


def test_the_closed_precedence_registers_have_the_documented_sizes():
    assert len(FIXED_KUBRA) == 1
    assert len(HAA_OPENINGS) == 7
    assert len(RAA_OPENINGS) == 6
    assert len(HAA_VERSE_HEADS) == 25
    assert len(LAM_DHAT_YAA) == 7
    assert len(LAM_VERSE_HEADS) == 3
    assert VERSE_HEAD_SURAHS == frozenset({20, 53, 70, 75, 79, 80, 87, 91, 92, 93, 96})


@pytest.mark.parametrize("location", sorted(FIXED_KUBRA))
def test_fixed_kubra_precedes_the_mark_supplied_taqlil_default(location):
    assert Quality.KUBRA in _qualities(location)
    assert Quality.TAQLIL not in _qualities(location)


@pytest.mark.parametrize("location", sorted(HAA_OPENINGS | RAA_OPENINGS))
def test_every_fixed_opening_is_taqlil(location):
    assert Quality.TAQLIL in _qualities(location)


@pytest.mark.parametrize("location", sorted(LAM_DHAT_YAA))
def test_lam_dhat_yaa_reserves_its_default_fath_for_the_coupled_owner(location):
    assert Quality.TAQLIL not in _qualities(location)


@pytest.mark.parametrize("location", sorted(LAM_VERSE_HEADS))
def test_lam_verse_heads_expose_the_default_inclination_side(location):
    assert Quality.TAQLIL in _qualities(location)


@pytest.mark.parametrize("location", sorted(HAA_VERSE_HEADS))
def test_pronominal_haa_heads_keep_the_fixed_default_fath(location):
    assert Quality.TAQLIL not in _qualities(location)

