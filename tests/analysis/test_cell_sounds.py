"""One CellSound per core sound, spanning the columns that own or present it.

The sound laws run in every boundary state: every sound in one cell, its span
the owner and presenter columns, its rules its sound's, a gap where none presents.
"""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import (
    CellColumn,
    CellRole,
    CellSide,
    CellStatus,
    CellTier,
    CellValidationError,
    build_cell_sounds,
    build_cell_words,
    validate_cell_sounds,
)
from quranic_phonemizer.analysis.dtos import Sound
from quranic_phonemizer.analysis.ids import (
    CellColumnId,
    CharacterId,
    LetterUnitId,
    OccurrenceId,
    SoundId,
    WordId,
)
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.model.address import Script, VerseRef
from quranic_phonemizer.session import phonemize_request
from quranic_phonemizer.session.boundaries import resolve_boundaries
from quranic_phonemizer.session.core import Session

#: One reference per boundary state and hard case: a word isolated, a start,
#: joined words, a cross-word idgham merger, a long ayah, a dagger-alif long
#: vowel, a hamzat wasl started, and internal stops.
SITES = [
    ("1:1:1", {}),
    ("112:1", {}),
    ("1:1", {}),
    ("2:5", {}),
    ("36:52-36:53", {}),
    ("3:1-3:2", {}),
    ("2:255", {}),
    ("52:1:1", {}),
    ("1:2:1", {}),
    ("18:38", {"stop_refs": ["18:38:1"]}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]

#: The hamzat wasl alif; started, it carries a glottal stop and a connecting
#: vowel the rasm writes no haraka for.
_WASL_ALIF = "ٱ"


def _build(hafs, ref, kwargs):
    session = phonemize_request(hafs, ref, **kwargs)
    bundle = build_bundle(
        session, ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    view = build_source_view(session, bundle=bundle)
    words = build_cell_words(session, bundle=bundle, view=view)
    return words, bundle, view


def _indopak_session(hafs, sources, surah, ayah, stop_refs=()):
    verse = VerseRef(surah, ayah)
    words = sources[Script.INDOPAK][(surah, ayah)]
    locations = tuple(location for location, _ in words)
    built = hafs.build(hafs.read(Script.INDOPAK, verse, words))
    boundaries = resolve_boundaries(
        built.inscription.advice, locations, built.score, stop_refs=stop_refs
    )
    performance = hafs.perform(built.score, boundaries)
    return Session(
        locations, built.score, built.inscription, boundaries, performance
    )


def _cells(words):
    return [cell for word in words for cell in word.sounds]


def _column(words, column_id):
    return next(c for w in words for c in w.columns if c.id == column_id)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_every_core_sound_has_exactly_one_cell(hafs, ref, kwargs):
    words, bundle, _ = _build(hafs, ref, kwargs)
    got = sorted(cell.sound_id.value for cell in _cells(words))
    assert got == sorted(s.id.value for s in bundle.sounds)
    assert len(got) == len(set(got))


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_a_cell_spans_exactly_its_owner_and_presenter_columns(hafs, ref, kwargs):
    words, _, _ = _build(hafs, ref, kwargs)
    for cell in _cells(words):
        expected = [
            c.id for w in words for c in w.columns
            if cell.sound_id in c.owned_sound_ids
            or cell.sound_id in c.presented_sound_ids
        ]
        assert list(cell.column_ids) == expected
        assert cell.column_ids


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_a_cell_carries_its_sounds_rules(hafs, ref, kwargs):
    words, bundle, _ = _build(hafs, ref, kwargs)
    rules = {s.id: s.rule_occurrence_ids for s in bundle.sounds}
    for cell in _cells(words):
        assert cell.rule_occurrence_ids == rules[cell.sound_id]


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_the_sound_laws_hold(hafs, ref, kwargs):
    words, bundle, _ = _build(hafs, ref, kwargs)
    validate_cell_sounds(words, bundle.sounds)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_no_gap_column_where_the_source_presents_every_sound(hafs, ref, kwargs):
    """Hafs owns every performed sound on a source unit, so the honest-gap
    branch never fires: no reference in either boundary state mints a gap."""
    words, _, _ = _build(hafs, ref, kwargs)
    assert not [c for w in words for c in w.columns if c.role is CellRole.GAP]


def test_a_long_vowel_is_one_cell_over_carrier_and_haraka(hafs):
    """The alif of لَآ carries the long vowel and the fatha before it presents
    it: one CellSound spanning the haraka column and the madd column."""
    words, _, _ = _build(hafs, "2:255:2", {})
    long_vowel = next(
        cell for cell in _cells(words) if len(cell.column_ids) == 2
    )
    carrier = _column(words, long_vowel.column_ids[1])
    haraka = _column(words, long_vowel.column_ids[0])
    assert carrier.role is CellRole.MADD
    assert long_vowel.sound_id in carrier.owned_sound_ids
    assert haraka.role is CellRole.HARAKA
    assert long_vowel.sound_id in haraka.presented_sound_ids


def test_a_short_vowel_is_one_cell_over_one_column(hafs):
    words, bundle, _ = _build(hafs, "1:1:1", {})
    haraka_cell = next(
        cell for cell in _cells(words)
        if _column(words, cell.column_ids[0]).role is CellRole.HARAKA
        and len(cell.column_ids) == 1
    )
    assert len(haraka_cell.column_ids) == 1


def test_the_hamzat_wasl_connecting_vowel_is_presented_by_its_alif(hafs):
    """Started, ٱلْحَمْد opens on a glottal stop and a connecting vowel. The alif
    owns both, so the connecting vowel's cell spans the alif column, honestly
    presented -- Hafs spells no presenter-less sound, so it is no gap."""
    words, bundle, view = _build(hafs, "1:2:1", {})
    alif = next(
        c for w in words for c in w.columns if c.text == _WASL_ALIF
    )
    assert len(alif.owned_sound_ids) == 2
    for sound in alif.owned_sound_ids:
        cell = next(c for c in _cells(words) if c.sound_id == sound)
        assert alif.id in cell.column_ids
        assert _column(words, cell.column_ids[0]).role is not CellRole.GAP


def test_a_cross_word_merger_contributor_presents_the_host_sound(hafs):
    """The noon of the first word assimilates into the meem of the next: the
    merged sound's cell spans the contributor column and the host column across
    the boundary, held by the host word."""
    words, bundle, _ = _build(hafs, "36:52-36:53", {})
    merger = bundle.mergers[0]
    host_word = next(
        w for w in words if w.word_id == merger.after_word_id
    )
    cell = next(c for c in host_word.sounds if c.sound_id == merger.sound_id)
    columns = [_column(words, cid) for cid in cell.column_ids]
    assert len(columns) == 2
    presenter, owner = columns
    assert merger.sound_id in presenter.presented_sound_ids
    assert merger.sound_id in owner.owned_sound_ids
    assert presenter.source_unit_ids and owner.source_unit_ids


# ---- the honest gap column, exercised directly ----

def _letter(col_id, unit_id, owned):
    return CellColumn(
        id=CellColumnId(col_id),
        role=CellRole.LETTER,
        text="x",
        source_character_ids=(CharacterId(col_id),),
        source_unit_ids=(LetterUnitId(unit_id),),
        tier=CellTier.MAIN,
        attached_to_column_id=None,
        status=CellStatus.PRESENT,
        rule_occurrence_ids=(),
        silence=None,
        variant_id=None,
        variant_choice=None,
        owned_sound_ids=(SoundId(owned),),
        presented_sound_ids=(),
        anchor_unit_id=None,
        side=None,
    )


def _synthetic():
    from quranic_phonemizer.analysis.cells.dtos import CellWord

    columns = (_letter(0, 0, 0), _letter(1, 1, 1))
    word = CellWord(WordId(0), columns, ())
    sounds = (
        Sound(SoundId(0), 0, "a", WordId(0), ()),
        Sound(SoundId(1), 1, "b", WordId(0), ()),
        Sound(SoundId(2), 2, "c", WordId(0), (OccurrenceId(5),)),
    )
    return (word,), sounds


def test_a_presenter_less_sound_mints_an_honest_gap_column():
    words, sounds = _synthetic()
    aligned = build_cell_sounds(words, sounds)
    gaps = [c for w in aligned for c in w.columns if c.role is CellRole.GAP]
    assert len(gaps) == 1
    gap = gaps[0]
    assert gap.status is CellStatus.GAP
    assert not gap.source_unit_ids and not gap.source_character_ids
    assert not gap.owned_sound_ids and not gap.presented_sound_ids
    assert gap.anchor_unit_id == LetterUnitId(1) and gap.side is CellSide.AFTER
    cell = next(c for w in aligned for c in w.sounds if c.sound_id == SoundId(2))
    assert cell.column_ids == (gap.id,)
    assert cell.rule_occurrence_ids == (OccurrenceId(5),)
    validate_cell_sounds(aligned, sounds)


def test_gap_alignment_holds_and_a_missing_cell_fails_law_22():
    words, sounds = _synthetic()
    aligned = build_cell_sounds(words, sounds)
    dropped = dataclasses.replace(aligned[0], sounds=aligned[0].sounds[:-1])
    with pytest.raises(CellValidationError):
        validate_cell_sounds((dropped,), sounds)


def test_an_extra_cell_fails_law_22():
    words, sounds = _synthetic()
    aligned = build_cell_sounds(words, sounds)
    doubled = dataclasses.replace(
        aligned[0], sounds=(*aligned[0].sounds, aligned[0].sounds[0])
    )
    with pytest.raises(CellValidationError):
        validate_cell_sounds((doubled,), sounds)


def test_a_span_over_a_non_owning_column_fails_law_23():
    words, sounds = _synthetic()
    aligned = build_cell_sounds(words, sounds)
    cells = list(aligned[0].sounds)
    cells[0] = dataclasses.replace(
        cells[0], column_ids=(CellColumnId(0), CellColumnId(1))
    )
    broken = dataclasses.replace(aligned[0], sounds=tuple(cells))
    with pytest.raises(CellValidationError):
        validate_cell_sounds((broken,), sounds)


def test_wrong_rules_fail_law_23b():
    words, sounds = _synthetic()
    aligned = build_cell_sounds(words, sounds)
    cells = list(aligned[0].sounds)
    cells[0] = dataclasses.replace(cells[0], rule_occurrence_ids=(OccurrenceId(9),))
    broken = dataclasses.replace(aligned[0], sounds=tuple(cells))
    with pytest.raises(CellValidationError):
        validate_cell_sounds((broken,), sounds)


def test_an_empty_span_fails_law_27():
    words, sounds = _synthetic()
    aligned = build_cell_sounds(words, sounds)
    cells = list(aligned[0].sounds)
    cells[0] = dataclasses.replace(cells[0], column_ids=())
    broken = dataclasses.replace(aligned[0], sounds=tuple(cells))
    with pytest.raises(CellValidationError):
        validate_cell_sounds((broken,), sounds)


def test_hanging_a_presenter_less_sound_on_a_letter_fails_law_27():
    """The gap sound's cell moved onto a real letter column, the gap column
    dropped: no honest gap where none presents the sound."""
    words, sounds = _synthetic()
    aligned = build_cell_sounds(words, sounds)
    word = aligned[0]
    columns = tuple(c for c in word.columns if c.role is not CellRole.GAP)
    cells = tuple(
        dataclasses.replace(c, column_ids=(CellColumnId(1),))
        if c.sound_id == SoundId(2) else c
        for c in word.sounds
    )
    broken = dataclasses.replace(word, columns=columns, sounds=cells)
    with pytest.raises(CellValidationError):
        validate_cell_sounds((broken,), sounds)


def test_the_sites_exercise_every_boundary_state(hafs):
    from quranic_phonemizer.analysis.dtos import BoundaryState

    states: set[BoundaryState] = set()
    for ref, kwargs in SITES:
        _, bundle, _ = _build(hafs, ref, kwargs)
        states |= {b.state for b in bundle.boundaries}
    assert states == set(BoundaryState)


@pytest.mark.slow
def test_the_cell_sound_laws_hold_over_the_whole_corpus(hafs, packed, sources):
    """Run the sound laws over every verse joined and stopped after each
    internal word, in both scripts. Hafs presents every sound, so the corpus
    mints no gap column; the laws still bite on a broken cell."""
    info = packed.surah_info
    gaps = 0
    checked = 0
    for surah in range(1, 115):
        for ayah in range(1, len(info[str(surah)]) + 1):
            ref = f"{surah}:{ayah}"
            words_n = info[str(surah)][ayah - 1]
            stops = [f"{ref}:{word}" for word in range(1, words_n)]
            for kwargs in ({}, {"stop_refs": stops}):
                words, bundle, _ = _build(hafs, ref, kwargs)
                validate_cell_sounds(words, bundle.sounds)
                gaps += sum(
                    1 for w in words for c in w.columns if c.role is CellRole.GAP
                )
                checked += 1
            for stop_refs in ((), tuple(stops)):
                session = _indopak_session(hafs, sources, surah, ayah, stop_refs)
                bundle = build_bundle(
                    session, ref=ref, riwayah="hafs", script="indopak", variant={}
                )
                words = build_cell_words(session, bundle=bundle)
                validate_cell_sounds(words, bundle.sounds)
                checked += 1
    assert checked > 24000
    assert gaps == 0


def test_validation_rejects_a_gap_column_that_is_not_an_honest_gap():
    words, sounds = _synthetic()
    aligned = build_cell_sounds(words, sounds)
    gap = next(c for w in aligned for c in w.columns if c.role is CellRole.GAP)
    for broken in (
        dataclasses.replace(gap, role=CellRole.LETTER),
        dataclasses.replace(gap, anchor_unit_id=None, side=None),
        dataclasses.replace(gap, source_unit_ids=(LetterUnitId(0),)),
    ):
        patched = tuple(
            dataclasses.replace(
                w, columns=tuple(broken if c.id == gap.id else c for c in w.columns)
            )
            for w in aligned
        )
        with pytest.raises(CellValidationError):
            validate_cell_sounds(patched, sounds)
