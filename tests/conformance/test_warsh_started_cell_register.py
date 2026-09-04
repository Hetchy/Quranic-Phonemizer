"""Closed transformed-cell register for Warsh marked word starts."""
from __future__ import annotations

from collections import Counter

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import (
    CellRole,
    CellStatus,
    build_cell_view,
)
from quranic_phonemizer.analysis.facts import analyse
from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Riwayah, Script
from quranic_phonemizer.model.canon import CanonLetter
from quranic_phonemizer.model.performance import Consonant, Vowel
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.render.alphabet import packaged_alphabet
from quranic_phonemizer.riwayat.warsh.resources import corpus
from quranic_phonemizer.session import phonemize_request


def _started_view(warsh, pen, ref):
    session = phonemize_request(warsh, ref)
    metadata = dict(ref=ref, riwayah="warsh", script="uthmani", variant={})
    facts = analyse(session, packaged_alphabet())
    bundle = build_bundle(session, facts=facts, **metadata)
    view = build_cell_view(
        session, spelling="transformed", pen=pen, facts=facts,
        bundle=bundle, **metadata,
    )
    return facts, bundle, view.words[0]


def _is_started_long_hamza(facts, bundle) -> bool:
    if len(bundle.sounds) < 2:
        return False
    onset = facts.sounds[bundle.sounds[0].id.value].value
    vowel = facts.sounds[bundle.sounds[1].id.value].value
    return (
        isinstance(onset, Consonant)
        and onset.letter is CanonLetter.HAMZA
        and isinstance(vowel, Vowel)
        and vowel.long
    )


def test_every_marked_warsh_long_hamza_start_has_one_quality_carrier_group():
    warsh = recitation(Riwayah.WARSH)
    pen = pen_for(warsh.inventory(Script.UTHMANI))
    selected = corpus()
    candidates = [
        (location, entry) for location, entry in selected.entries.items()
        if entry.text.startswith(("اٰ", "ا۟"))
    ]
    long_starts = Counter()
    for location, entry in candidates:
        ref = selected.public_ref(location)
        facts, bundle, word = _started_view(warsh, pen, ref)
        assert all(column.text != "۟" for column in word.columns), ref
        if not _is_started_long_hamza(facts, bundle):
            continue
        long_starts[entry.text[:2]] += 1
        sound = bundle.sounds[1]
        cell = next(item for item in word.sounds if item.sound_id == sound.id)
        columns = [
            column for column in word.columns if column.id in cell.column_ids
        ]
        group = next(item for item in word.groups if sound.id in item.sound_ids)
        assert [column.role for column in columns] == [
            CellRole.HARAKA,
            CellRole.MADD,
        ], ref
        assert columns[0].status in {
            CellStatus.PRESENT,
            CellStatus.INSERTED,
            CellStatus.REPLACED,
        }, ref
        if columns[0].status is CellStatus.INSERTED:
            assert not columns[0].source_character_ids, ref
        assert columns[0].attached_to_column_id == columns[1].id, ref
        assert group.column_ids == cell.column_ids == tuple(
            column.id for column in columns
        ), ref

    assert len(candidates) == 299
    # The two started jaa_aal words, `ا۟لَ`, carry the restored long qata.
    assert long_starts == {"اٰ": 177, "ا۟": 14}
