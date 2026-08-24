"""The transformed cell view: the source-to-recited delta and its laws.

Laws 29, 30, 31 run in every boundary state and both scripts: inserted anchors,
replaced and dropped provenance, and variant fields against the selection.
"""
from __future__ import annotations

import dataclasses
from types import SimpleNamespace

import pytest

from quranic_phonemizer.analysis.cells import (
    CellRole,
    CellSide,
    CellStatus,
    CellValidationError,
    build_cell_view,
    validate_transformed,
)
from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells.transform import _inserted_column
from quranic_phonemizer.analysis.facts import analyse
from quranic_phonemizer.analysis.ids import LetterUnitId
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.model.address import (
    KhilafId, Option, Script, VariantSelection, VerseRef,
)
from quranic_phonemizer.model.canon import Quality
from quranic_phonemizer.model.performance import Vowel
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.render.alphabet import packaged_alphabet
from quranic_phonemizer.session import phonemize_request
from quranic_phonemizer.session.boundaries import resolve_boundaries
from quranic_phonemizer.session.core import Session

#: One reference per boundary state and hard case: a lone word, a start, joined
#: words, an idgham with a sakt, an iltiqa, a tanween idgham, a long ayah, a
#: started prosthetic hamza, and internal stops.
SITES = [
    ("1:1:1", {}),
    ("112:1", {}),
    ("1:1", {}),
    ("36:52-36:53", {}),
    ("3:1-3:2", {}),
    ("2:5", {}),
    ("2:255", {}),
    ("46:4:18", {}),
    ("18:38", {"stop_refs": ["18:38:1"]}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]


@pytest.fixture(scope="module")
def pen(hafs):
    return pen_for(hafs.inventory(Script.UTHMANI))


def _build(hafs, pen, ref, kwargs, selection=VariantSelection()):
    session = phonemize_request(hafs, ref, selection=selection, **kwargs)
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    view = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    source = build_source_view(session, bundle=build_bundle(session, **kw))
    return view, source, session


def _columns(view):
    out = [c for w in view.words for c in w.columns]
    for b in view.boundaries:
        out.extend(b.columns)
    return out


# ---- the laws over every boundary state ----

@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_the_transformed_laws_hold(hafs, pen, ref, kwargs):
    view, source, session = _build(hafs, pen, ref, kwargs)
    validate_transformed(view, source, session.performance.selection)


def test_visual_insertions_do_not_invent_performance_insertions(hafs, pen):
    """A transformed view may supply visual columns without changing facts."""
    inserted = 0
    for ref, kwargs in SITES:
        view, _, session = _build(hafs, pen, ref, kwargs)
        inserted += sum(
            c.status is CellStatus.INSERTED for c in _columns(view)
        )
        assert not analyse(session, packaged_alphabet()).insertions
    assert inserted > 0


# ---- the concrete cases the laws exercise ----

def test_the_ibdal_started_prosthetic_hamza_is_replaced(hafs, pen):
    """The started prosthetic hamza replaces its silent connector column.
    The lexical hamza becomes its source-backed replacement carrier."""
    view, source, _ = _build(hafs, pen, "46:4:18", {})
    columns = {c.source_unit_ids[0].value: c
               for c in _columns(view) if c.source_unit_ids}
    prosthetic = columns[0]
    assert prosthetic.status is CellStatus.REPLACED
    assert prosthetic.text == pen.seated_hamza(Quality.I)
    assert prosthetic.text != source.units[0].text
    assert prosthetic.source_unit_ids == (LetterUnitId(0),)
    lexical = columns[1]
    assert lexical.status is CellStatus.REPLACED
    assert lexical.role is CellRole.MADD
    assert lexical.text == pen.performed_carrier(Quality.I)[1]
    assert lexical.source_unit_ids == (LetterUnitId(1), LetterUnitId(2))
    helping = next(c for c in _columns(view) if not c.source_character_ids)
    assert helping.text == pen.short_vowel(Quality.I)
    assert helping.status is CellStatus.INSERTED


def test_a_silent_alif_is_dropped(hafs, pen):
    """The unread alif of قالوا owns no sound; its column is dropped and keeps
    its exact source text so a consumer can grey it."""
    view, source, _ = _build(hafs, pen, "2:11", {})
    dropped = [
        c for c in _columns(view)
        if c.status is CellStatus.DROPPED and c.text.startswith("ا")
    ]
    assert dropped
    for col in dropped:
        unit = source.units[col.source_unit_ids[0].value]
        assert col.text == unit.text
        assert not col.owned_sound_ids and not col.presented_sound_ids


def test_the_taa_marbuta_at_waqf_is_read_as_a_haa(hafs, pen):
    """Stopped on, a taa marbuta is performed as a haa, a letter mismatch that
    replaces the column with the performed haa and its pausal sukun."""
    from quranic_phonemizer.model.canon import CanonLetter

    view, _, _ = _build(hafs, pen, "2:3", {"stop_refs": [f"2:3:{w}" for w in range(1, 6)]})
    haa = [c for c in _columns(view) if c.status is CellStatus.REPLACED
           and c.text == pen.letter(CanonLetter.HEH) + pen.role("sukun")]
    assert haa


@pytest.mark.parametrize(("ref", "expected"), [
    ("78:2:2", "أْ"),
    ("10:4:8", "أْ"),
    ("5:29:12", "ءْ"),
    ("10:15:24", "ءْ"),
    ("5:29:4", "ءْ"),
    ("2:166:2", "أْ"),
    ("55:22:3", "ؤْ"),
    ("2:15:2", "ئْ"),
])
def test_a_pausal_hamza_uses_the_preceding_vowels_seat(
    hafs, pen, ref, expected
):
    view, _, _ = _build(hafs, pen, ref, {})
    hamza = [c for c in view.words[0].columns if c.text == expected][-1]
    assert hamza.status is CellStatus.REPLACED


def test_a_joined_hamza_keeps_its_written_seat(hafs, pen):
    view, _, _ = _build(hafs, pen, "78:2:2-78:2:3", {})
    assert any(c.text == "إ" and c.status is CellStatus.PRESENT
               for c in view.words[0].columns)


def test_the_source_spelling_is_unchanged(hafs, pen):
    """The transformed view is additive: the default source spelling is what it
    was, column for column."""
    session = phonemize_request(hafs, "46:4:18")
    kw = dict(ref="46:4:18", riwayah="hafs", script="uthmani", variant={})
    source_view = build_cell_view(session, **kw)
    again = build_cell_view(session, spelling="source", **kw)
    assert source_view == again
    transformed = build_cell_view(session, spelling="transformed", pen=pen, **kw)
    assert transformed != source_view


# ---- the seen/saad variant carries onto the transformed cells ----

def test_the_seen_sad_pair_carries_the_variant(hafs, pen):
    """At a selected seen/saad khilaf both cells of the pair carry the variant;
    one sounds and one is silent, and both name the resolved choice."""
    selection = VariantSelection((Option(KhilafId.SEEN_SAD_YABSUT, "seen"),))
    view, source, session = _build(hafs, pen, "2:245:14", {}, selection)
    pair = [c for c in _columns(view) if c.variant_id is KhilafId.SEEN_SAD_YABSUT]
    assert len(pair) == 2
    assert all(c.variant_choice == "seen" for c in pair)
    validate_transformed(view, source, session.performance.selection)


# ---- law 29: the inserted column ----

def _fake_facts(value):
    return SimpleNamespace(sounds=[SimpleNamespace(value=value)])


def test_the_inserted_column_builder_makes_a_valid_anchor(hafs, pen):
    """The insertion machinery builds a column with empty source provenance, a
    unit/side anchor, its performed sound, and its label from the pen."""
    facts = _fake_facts(Vowel(Quality.I))
    col = _inserted_column(9000, LetterUnitId(0), CellSide.BEFORE, 0, facts, pen)
    assert col.status is CellStatus.INSERTED
    assert not col.source_character_ids and not col.source_unit_ids
    assert col.anchor_unit_id == LetterUnitId(0) and col.side is CellSide.BEFORE
    assert col.owned_sound_ids and col.text == pen.role("kasra")


def _view_with_inserted(hafs, pen, col):
    view, source, session = _build(hafs, pen, "1:1:1", {})
    word = dataclasses.replace(
        view.words[0], columns=(*view.words[0].columns, col)
    )
    return dataclasses.replace(view, words=(word,)), source, session


def test_law_29_accepts_a_valid_inserted_column(hafs, pen):
    col = _inserted_column(9000, LetterUnitId(0), CellSide.AFTER, 0,
                           _fake_facts(Vowel(Quality.A)), pen)
    view, source, session = _view_with_inserted(hafs, pen, col)
    validate_transformed(view, source, session.performance.selection)


def test_law_29_bites_an_invented_source_unit(hafs, pen):
    col = _inserted_column(9000, LetterUnitId(0), CellSide.AFTER, 0,
                           _fake_facts(Vowel(Quality.A)), pen)
    col = dataclasses.replace(col, source_unit_ids=(LetterUnitId(0),))
    view, source, session = _view_with_inserted(hafs, pen, col)
    with pytest.raises(CellValidationError):
        validate_transformed(view, source, session.performance.selection)


def test_law_29_bites_an_anchorless_insertion(hafs, pen):
    col = _inserted_column(9000, LetterUnitId(0), CellSide.AFTER, 0,
                           _fake_facts(Vowel(Quality.A)), pen)
    col = dataclasses.replace(col, anchor_unit_id=None)
    view, source, session = _view_with_inserted(hafs, pen, col)
    with pytest.raises(CellValidationError):
        validate_transformed(view, source, session.performance.selection)


def test_law_29_bites_an_anchor_past_the_source_units(hafs, pen):
    col = _inserted_column(9000, LetterUnitId(9999), CellSide.AFTER, 0,
                           _fake_facts(Vowel(Quality.A)), pen)
    view, source, session = _view_with_inserted(hafs, pen, col)
    with pytest.raises(CellValidationError):
        validate_transformed(view, source, session.performance.selection)


# ---- law 30: replaced and dropped keep their provenance ----

def _first(view, status):
    return next(
        (c for c in _columns(view) if c.status is status), None
    )


def test_law_30_bites_a_replaced_column_that_loses_its_characters(hafs, pen):
    view, source, session = _build(hafs, pen, "46:4:18", {})
    replaced = _first(view, CellStatus.REPLACED)
    assert replaced is not None
    broken = _swap(view, replaced, source_character_ids=())
    with pytest.raises(CellValidationError):
        validate_transformed(broken, source, session.performance.selection)


def test_law_30_bites_a_dropped_column_that_loses_its_text(hafs, pen):
    view, source, session = _build(hafs, pen, "2:11", {})
    dropped = _first(view, CellStatus.DROPPED)
    assert dropped is not None
    broken = _swap(view, dropped, text=dropped.text + "x")
    with pytest.raises(CellValidationError):
        validate_transformed(broken, source, session.performance.selection)


# ---- law 31: variant fields match the resolved selection ----

def test_law_31_bites_a_variant_choice_with_no_variant(hafs, pen):
    view, source, session = _build(hafs, pen, "1:1", {})
    col = view.words[0].columns[0]
    broken = _swap(view, col, variant_choice="seen")
    with pytest.raises(CellValidationError):
        validate_transformed(broken, source, session.performance.selection)


def test_law_31_bites_a_choice_off_the_resolved_selection(hafs, pen):
    selection = VariantSelection((Option(KhilafId.SEEN_SAD_YABSUT, "seen"),))
    view, source, session = _build(hafs, pen, "2:245:14", {}, selection)
    pair = next(c for c in _columns(view) if c.variant_id is KhilafId.SEEN_SAD_YABSUT)
    broken = _swap(view, pair, variant_choice="saad")
    with pytest.raises(CellValidationError):
        validate_transformed(broken, source, session.performance.selection)


def _swap(view, target, **changes):
    replaced = dataclasses.replace(target, **changes)
    words = tuple(
        dataclasses.replace(w, columns=tuple(
            replaced if c is target else c for c in w.columns
        )) for w in view.words
    )
    boundaries = tuple(
        dataclasses.replace(b, columns=tuple(
            replaced if c is target else c for c in b.columns
        )) for b in view.boundaries
    )
    return dataclasses.replace(view, words=words, boundaries=boundaries)


# ---- the whole corpus ----

def _indopak_session(hafs, sources, surah, ayah, stop_refs=()):
    verse = VerseRef(surah, ayah)
    words = sources[Script.INDOPAK][(surah, ayah)]
    locations = tuple(location for location, _ in words)
    built = hafs.build(hafs.read(Script.INDOPAK, verse, words))
    boundaries = resolve_boundaries(
        built.inscription.advice, locations, built.score, stop_refs=stop_refs
    )
    performance = hafs.perform(built.score, boundaries)
    return Session(locations, built.score, built.inscription, boundaries, performance)


@pytest.mark.slow
def test_the_transformed_laws_hold_over_the_whole_corpus(hafs, packed, sources):
    """Build the transformed view for every verse joined and stopped after each
    internal word, in both scripts, and hold the transformed cell laws."""
    info = packed.surah_info
    pens = {s: pen_for(hafs.inventory(s)) for s in Script}
    replaced = inserted = checked = 0
    for surah in range(1, 115):
        for ayah in range(1, len(info[str(surah)]) + 1):
            ref = f"{surah}:{ayah}"
            n = info[str(surah)][ayah - 1]
            stops = [f"{ref}:{w}" for w in range(1, n)]
            for kwargs in ({}, {"stop_refs": stops}):
                session = phonemize_request(hafs, ref, **kwargs)
                kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
                view = build_cell_view(session, spelling="transformed",
                                       pen=pens[Script.UTHMANI], **kw)
                source = build_source_view(session, bundle=build_bundle(session, **kw))
                validate_transformed(view, source, session.performance.selection)
                replaced += sum(1 for c in _columns(view)
                                if c.status is CellStatus.REPLACED)
                inserted += sum(1 for c in _columns(view)
                                if c.status is CellStatus.INSERTED)
                checked += 1
            for stop_refs in ((), tuple(stops)):
                session = _indopak_session(hafs, sources, surah, ayah, stop_refs)
                kw = dict(ref=ref, riwayah="hafs", script="indopak", variant={})
                view = build_cell_view(session, spelling="transformed",
                                       pen=pens[Script.INDOPAK], **kw)
                source = build_source_view(session, bundle=build_bundle(session, **kw))
                validate_transformed(view, source, session.performance.selection)
                inserted += sum(1 for c in _columns(view)
                                if c.status is CellStatus.INSERTED)
                checked += 1
    assert checked > 24000
    assert replaced > 0
    assert inserted > 0
