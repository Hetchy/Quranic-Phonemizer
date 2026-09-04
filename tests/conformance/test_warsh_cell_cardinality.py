"""Whole-corpus bounds for the semantic granularity of Warsh cells."""
from __future__ import annotations

import pytest

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import build_cell_view
from quranic_phonemizer.analysis.cells.dtos import CellRole, CellStatus
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.session import phonemize_request


def test_stopping_before_3_15_second_word_keeps_each_column_semantic():
    """Ibtidaa exposes both hamzas in `اَوْ۟نَبِّئُكُم`; they remain two
    vocalised groups rather than one four-sound source column."""
    reading = recitation(Riwayah.WARSH)
    pen = pen_for(reading.inventory(Script.UTHMANI))
    session = phonemize_request(
        reading, "3:15", stop_refs=("3:15:1",)
    )
    view = build_cell_view(
        session,
        ref="3:15",
        riwayah="warsh",
        script="uthmani",
        variant={},
        spelling="transformed",
        pen=pen,
    )

    word = view.words[1]
    assert max(len(column.owned_sound_ids) for column in word.columns) <= 2
    assert max(len(group.sound_ids) for group in word.groups) <= 3
    first, first_vowel, eased, eased_vowel = word.columns[:4]
    assert tuple(column.role for column in word.columns[:4]) == (
        CellRole.LETTER,
        CellRole.HARAKA,
        CellRole.LETTER,
        CellRole.HARAKA,
    )
    assert first.status is CellStatus.REPLACED
    assert eased.status is CellStatus.REPLACED
    assert eased_vowel.status is CellStatus.INSERTED
    assert first_vowel.source_character_ids
    assert eased.source_character_ids
    assert not eased_vowel.source_character_ids
    assert all(mark not in eased.text for mark in "ْ۟")


def _assert_madd_badal_only_labels_carriers(ref, view, bundle):
    badal = {
        occurrence.id for occurrence in bundle.rule_occurrences
        if occurrence.rule_id.value == "madd_badal"
    }
    columns = tuple(
        column for word in view.words for column in word.columns
    ) + tuple(
        column for boundary in view.boundaries for column in boundary.columns
    )
    for occurrence in badal:
        labelled = tuple(
            column for column in columns
            if occurrence in column.rule_occurrence_ids
        )
        assert all(column.role is CellRole.MADD for column in labelled), (
            f"{ref}: Madd Badal {occurrence.value} leaks onto "
            f"{[(column.id.value, column.role.value, column.text) for column in labelled]}"
        )


@pytest.mark.slow
@pytest.mark.parametrize("surah", range(1, 115))
@pytest.mark.parametrize("boundary_plan", ["joined", "all_stopped"])
def test_warsh_cells_have_semantic_sound_cardinality(surah, boundary_plan):
    """No column owns three sounds; only tanween groups may contain three."""
    reading = recitation(Riwayah.WARSH)
    pen = pen_for(reading.inventory(Script.UTHMANI))
    verses = sorted(
        verse for verse in reading.corpus.source_by_verse
        if verse.surah == surah
    )
    for verse in verses:
        ref = str(verse)
        locations = reading.corpus.locations(ref)
        stop_refs = (
            tuple(
                reading.corpus.public_ref(location) for location in locations[:-1]
            )
            if boundary_plan == "all_stopped"
            else ()
        )
        session = phonemize_request(reading, ref, stop_refs=stop_refs)
        metadata = dict(
            ref=ref, riwayah="warsh", script="uthmani", variant={}
        )
        bundle = build_bundle(session, **metadata)

        # build_cell_view applies the cardinality laws after every projection
        # and reports the exact offending column/group if this sweep regresses.
        view = build_cell_view(
            session,
            spelling="transformed",
            pen=pen,
            bundle=bundle,
            **metadata,
        )
        _assert_madd_badal_only_labels_carriers(ref, view, bundle)
        assert all(
            column.text != "۬" and column.text
            for word in view.words
            for column in word.columns
        ), f"{ref}: annotation-only cell survived semantic projection"
