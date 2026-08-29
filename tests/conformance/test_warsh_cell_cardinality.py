"""Whole-corpus bounds for the semantic granularity of Warsh cells."""
from __future__ import annotations

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.analysis.cells import build_cell_view
from quranic_phonemizer.model.address import Riwayah, Script
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.session import phonemize_request


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

        # build_cell_view applies the cardinality laws after every projection
        # and reports the exact offending column/group if this sweep regresses.
        build_cell_view(
            session,
            ref=ref,
            riwayah="warsh",
            script="uthmani",
            variant={},
            spelling="transformed",
            pen=pen,
        )
