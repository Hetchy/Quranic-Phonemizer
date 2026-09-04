"""Corpus-wide pausal ownership of Warsh's native noon iqlab mark."""
from __future__ import annotations

import pytest

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import build_cell_view
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.session import phonemize_request


@pytest.mark.slow
def test_every_stopped_native_noon_iqlab_mark_uses_waqf_drop():
    reading = recitation(Riwayah.WARSH)
    pen = pen_for(reading.inventory(Script.UTHMANI))
    sites = tuple(
        location for location in reading.corpus.entries
        if reading.corpus.word(location).endswith("نۢ")
    )

    assert len(sites) == 199
    for location in sites:
        ref = reading.corpus.public_ref(location)
        session = phonemize_request(reading, ref, stop_refs=(ref,))
        kw = dict(ref=ref, riwayah="warsh", script="uthmani", variant={})
        bundle = build_bundle(session, **kw)
        source = build_source_view(session, bundle=bundle)
        view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
        rules = {
            occurrence.id: occurrence.rule_id.value
            for occurrence in bundle.rule_occurrences
        }
        unit = next(item for item in source.units if item.text == "ۢ")
        cell = next(
            column for word in view.words for column in word.columns
            if column.text == "ۢ"
        )

        assert rules[unit.silence] == "waqf_diacritic_drop", ref
        assert cell.silence == unit.silence, ref

