"""The nested cell view: words, between-word boundaries, and merger bridges.

The view laws run in every boundary state and both scripts: one stop-sign per
after-word boundary, one cell per sound, sound bridges, no iltiqa bridge, closure.
"""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.cells import (
    CellBridge,
    CellColumn,
    CellRole,
    CellStatus,
    CellTier,
    CellValidationError,
    CellView,
    build_cell_view,
    validate_cell_view,
)
from quranic_phonemizer.analysis.cells.view_laws import _check_no_iltiqa_bridge
from quranic_phonemizer.analysis.dtos import BoundaryState
from quranic_phonemizer.analysis.ids import CellColumnId, LetterUnitId, SoundId
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.model.address import Script, VerseRef
from quranic_phonemizer.orthography.write import pen_for
from quranic_phonemizer.session import phonemize_request
from quranic_phonemizer.session.boundaries import resolve_boundaries
from quranic_phonemizer.session.core import Session

#: One reference per boundary state and hard case: a lone word, a start, joined
#: words, a cross-word idgham of noon and of tanween with a sakt, an iltiqa, a
#: tanween idgham, a long ayah, and internal stops.
SITES = [
    ("1:1:1", {}),
    ("112:1", {}),
    ("1:1", {}),
    ("36:52-36:53", {}),
    ("3:1-3:2", {}),
    ("2:5", {}),
    ("2:255", {}),
    ("52:1:1", {}),
    ("18:38", {"stop_refs": ["18:38:1"]}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]


def _build(hafs, ref, kwargs, script="uthmani"):
    session = phonemize_request(hafs, ref, **kwargs)
    view = build_cell_view(session, ref=ref, riwayah="hafs", script=script, variant={})
    bundle = build_bundle(session, ref=ref, riwayah="hafs", script=script, variant={})
    source = build_source_view(session, bundle=bundle)
    return view, bundle, source


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


def _columns(view: CellView) -> dict[int, CellColumn]:
    out = {c.id.value: c for w in view.words for c in w.columns}
    out.update((c.id.value, c) for b in view.boundaries for c in b.columns)
    return out


def _all_cells(view: CellView):
    cells = [c for w in view.words for c in w.sounds]
    cells.extend(bridge.sound for w in view.words for bridge in w.bridges)
    for b in view.boundaries:
        cells.extend(b.sounds)
        cells.extend(br.sound for br in b.bridges)
    return cells


def _a_bridge_boundary(view: CellView):
    return next(b for b in view.boundaries if b.bridges)


# ---- the laws over every boundary state ----

@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_the_view_laws_hold(hafs, ref, kwargs):
    view, bundle, source = _build(hafs, ref, kwargs)
    validate_cell_view(view, bundle, source)


def _boundary_signs(source, boundary_id):
    return tuple(
        c for c in source.characters
        if c.boundary_id is not None
        and c.boundary_id.value == boundary_id
        and c.kind.value == "stop_sign"
    )


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_every_after_word_boundary_has_one_stop_sign(hafs, ref, kwargs):
    view, bundle, source = _build(hafs, ref, kwargs)
    after_word = {
        b.id.value: b for b in bundle.boundaries
        if b.before is not None
    }
    assert {cb.boundary_id.value for cb in view.boundaries} == set(after_word)
    for cb in view.boundaries:
        signs = [c for c in cb.columns if c.role.value == "stop_sign"]
        assert len(signs) == 1
        assert not signs[0].owned_sound_ids and not signs[0].presented_sound_ids
        written = _boundary_signs(source, cb.boundary_id.value)
        assert signs[0].text == "".join(c.text for c in written)
        assert signs[0].source_character_ids == tuple(c.id for c in written)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_every_core_sound_has_exactly_one_cell(hafs, ref, kwargs):
    view, bundle, _ = _build(hafs, ref, kwargs)
    got = sorted(cell.sound_id.value for cell in _all_cells(view))
    assert got == sorted(s.id.value for s in bundle.sounds)
    assert len(got) == len(set(got))


def test_the_sites_exercise_every_boundary_state(hafs):
    states: set[BoundaryState] = set()
    for ref, kwargs in SITES:
        _, bundle, _ = _build(hafs, ref, kwargs)
        states |= {b.state for b in bundle.boundaries}
    assert states == set(BoundaryState)


# ---- the cross-word merger bridge ----

def test_a_cross_word_merger_sound_lives_in_the_bridge_not_the_host_word(hafs):
    """Each merged sound renders once in its bridge, spanning the contributor's
    presenter column and the host's owner column, and no longer inside the host
    word."""
    view, bundle, _ = _build(hafs, "36:52-36:53", {})
    columns = _columns(view)
    assert bundle.mergers
    for merger in (m for m in bundle.mergers if m.boundary_id is not None):
        host = next(w for w in view.words if w.word_id == merger.after_word_id)
        assert merger.sound_id not in {c.sound_id for c in host.sounds}
        bridge = next(
            br for b in view.boundaries for br in b.bridges
            if br.merger_id == merger.id
        )
        assert bridge.sound.sound_id == merger.sound_id
        presenter = columns[bridge.before_column_ids[0].value]
        owner = columns[bridge.after_column_ids[0].value]
        assert merger.sound_id in presenter.presented_sound_ids
        assert merger.sound_id in owner.owned_sound_ids


def test_idgham_of_noon_and_of_tanween_both_bridge(hafs):
    view, _, _ = _build(hafs, "36:52-36:53", {})
    columns = _columns(view)
    contributor_roles = {
        columns[br.before_column_ids[0].value].role
        for b in view.boundaries for br in b.bridges
    }
    assert CellRole.LETTER in contributor_roles
    assert CellRole.TANWEEN in contributor_roles


def test_the_sakt_sign_rides_its_boundary_column(hafs):
    """The written sakt sign at the end of the ayah lives on the boundary's
    stop-sign column, not the word text, so a stopped reading can lift it out."""
    view, bundle, source = _build(hafs, "36:52-36:53", {})
    sakt = next(b for b in bundle.boundaries if b.state is BoundaryState.SAKT)
    cb = next(b for b in view.boundaries if b.boundary_id == sakt.id)
    sign = next(c for c in cb.columns if c.role.value == "stop_sign")
    written = _boundary_signs(source, cb.boundary_id.value)
    assert sign.text == "".join(c.text for c in written)
    assert sign.text


def test_a_two_sign_boundary_keeps_both_written_signs(hafs):
    """The sakt boundary at 36:52 carries a sakt sign and a stop-advice sign; the
    stop-sign column holds both, in text order, and names both characters."""
    view, bundle, source = _build(hafs, "36:52-36:53", {})
    sakt = next(b for b in bundle.boundaries if b.state is BoundaryState.SAKT)
    cb = next(b for b in view.boundaries if b.boundary_id == sakt.id)
    sign = next(c for c in cb.columns if c.role.value == "stop_sign")
    written = _boundary_signs(source, cb.boundary_id.value)
    sakt_sign, stop_advice_sign = chr(0x06DC), chr(0x06D7)
    assert len(written) == 2
    assert sign.text == sakt_sign + stop_advice_sign
    assert sign.source_character_ids == tuple(c.id for c in written)
    assert len(sign.source_character_ids) == 2


def test_a_single_sign_boundary_shows_its_one_sign(hafs):
    """A boundary with one written sign shows exactly that sign and names its one
    character."""
    view, _, source = _build(hafs, "2:5", {})
    seen = False
    for cb in view.boundaries:
        written = _boundary_signs(source, cb.boundary_id.value)
        if len(written) != 1:
            continue
        sign = next(c for c in cb.columns if c.role.value == "stop_sign")
        assert sign.text == written[0].text
        assert sign.source_character_ids == (written[0].id,)
        if sign.text == chr(0x06D6):
            seen = True
    assert seen, "expected the single U+06D6 sign at 2:5"


def test_an_internal_stop_has_an_empty_stop_sign(hafs):
    view, bundle, _ = _build(hafs, "18:38", {"stop_refs": ["18:38:1"]})
    stop = next(
        b for b in bundle.boundaries
        if b.state is BoundaryState.STOP and b.before is not None and b.after is not None
    )
    cb = next(b for b in view.boundaries if b.boundary_id == stop.id)
    sign = next(c for c in cb.columns if c.role.value == "stop_sign")
    assert sign.text == ""


def test_a_clipped_range_end_is_not_a_verse_end(hafs):
    view, _, _ = _build(hafs, "35:29:1-35:29:10", {})
    assert view.boundaries[-1].verse_end is None


def test_an_actual_verse_end_is_marked_in_a_clipped_range(hafs):
    view, _, _ = _build(hafs, "35:29:10-35:29:16", {})
    assert view.boundaries[-1].verse_end == 29


def test_an_iltiqa_boundary_carries_no_bridge(hafs):
    """The connecting vowel of the meem into the divine name is an insertion,
    not a merger, so its boundary carries no bridge."""
    view, bundle, _ = _build(hafs, "3:1-3:2", {})
    assert not any(m.boundary_id is not None for m in bundle.mergers)
    assert all(not cb.bridges for cb in view.boundaries)


def test_a_spelled_name_merger_lives_inside_its_word(hafs):
    view, bundle, _ = _build(hafs, "2:1", {})
    mergers = [m for m in bundle.mergers if m.boundary_id is None]
    assert len(mergers) == 1
    bridge = view.words[0].bridges[0]
    merger = mergers[0]
    assert bridge.merger_id == merger.id
    assert bridge.sound.sound_id == merger.sound_id
    assert bridge.before_column_ids and bridge.after_column_ids


# ---- each law bites under its own violation ----

def _inserted_column(new_id: int) -> CellColumn:
    return CellColumn(
        id=CellColumnId(new_id),
        role=CellRole.HARAKA,
        text="",
        source_character_ids=(),
        source_unit_ids=(),
        tier=CellTier.MAIN,
        attached_to_column_id=None,
        status=CellStatus.INSERTED,
        rule_occurrence_ids=(),
        silence=None,
        variant_id=None,
        variant_choice=None,
        owned_sound_ids=(),
        presented_sound_ids=(),
        anchor_unit_id=LetterUnitId(0),
        side=None,
    )


def _replace_boundary(view: CellView, boundary_id, **changes) -> CellView:
    boundaries = tuple(
        dataclasses.replace(b, **changes) if b.boundary_id == boundary_id else b
        for b in view.boundaries
    )
    return dataclasses.replace(view, boundaries=boundaries)


def test_a_boundary_with_no_stop_sign_fails_law_20a(hafs):
    view, bundle, source = _build(hafs, "1:1", {})
    cb = view.boundaries[0]
    broken = _replace_boundary(view, cb.boundary_id, columns=())
    with pytest.raises(CellValidationError):
        validate_cell_view(broken, bundle, source)


def test_two_stop_signs_fail_law_20a(hafs):
    view, bundle, source = _build(hafs, "1:1", {})
    cb = view.boundaries[0]
    broken = _replace_boundary(view, cb.boundary_id, columns=(*cb.columns, cb.columns[0]))
    with pytest.raises(CellValidationError):
        validate_cell_view(broken, bundle, source)


def test_a_stop_sign_that_owns_a_sound_fails_law_20a(hafs):
    view, bundle, source = _build(hafs, "1:1", {})
    cb = view.boundaries[0]
    sign = dataclasses.replace(cb.columns[0], owned_sound_ids=(SoundId(0),))
    broken = _replace_boundary(view, cb.boundary_id, columns=(sign,))
    with pytest.raises(CellValidationError):
        validate_cell_view(broken, bundle, source)


def test_a_merger_sound_duplicated_in_the_host_word_fails_law_22(hafs):
    view, bundle, source = _build(hafs, "36:52-36:53", {})
    merger = bundle.mergers[0]
    bridge = next(
        br for b in view.boundaries for br in b.bridges if br.merger_id == merger.id
    )
    words = tuple(
        dataclasses.replace(w, sounds=(*w.sounds, bridge.sound))
        if w.word_id == merger.after_word_id else w
        for w in view.words
    )
    with pytest.raises(CellValidationError):
        validate_cell_view(dataclasses.replace(view, words=words), bundle, source)


def test_a_missing_cell_fails_law_22(hafs):
    view, bundle, source = _build(hafs, "1:1:1", {})
    words = (dataclasses.replace(view.words[0], sounds=view.words[0].sounds[:-1]),)
    with pytest.raises(CellValidationError):
        validate_cell_view(dataclasses.replace(view, words=words), bundle, source)


def test_a_column_owning_more_than_two_sounds_fails_the_group_law(hafs):
    session = phonemize_request(hafs, "1:1")
    metadata = dict(ref="1:1", riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **metadata)
    source = build_source_view(session, bundle=bundle)
    view = build_cell_view(
        session,
        spelling="transformed",
        pen=pen_for(hafs.inventory(Script.UTHMANI)),
        bundle=bundle,
        **metadata,
    )
    word = view.words[0]
    target = word.columns[0]
    broken_column = dataclasses.replace(
        target, owned_sound_ids=tuple(sound.sound_id for sound in word.sounds[:3])
    )
    broken_word = dataclasses.replace(
        word,
        columns=tuple(
            broken_column if column is target else column for column in word.columns
        ),
    )
    broken = dataclasses.replace(view, words=(broken_word, *view.words[1:]))

    with pytest.raises(CellValidationError, match="more than two sounds"):
        validate_cell_view(broken, bundle, source)


def test_a_bridge_endpoint_off_the_host_fails_law_25(hafs):
    view, bundle, source = _build(hafs, "36:52-36:53", {})
    cb = _a_bridge_boundary(view)
    other = next(
        c.id for w in view.words for c in w.columns
        if c.id != cb.bridges[0].after_column_ids[0]
    )
    bad = dataclasses.replace(cb.bridges[0], after_column_ids=(other,))
    broken = _replace_boundary(view, cb.boundary_id, bridges=(bad, *cb.bridges[1:]))
    with pytest.raises(CellValidationError):
        validate_cell_view(broken, bundle, source)


def test_a_bridge_resolving_to_no_merger_fails_law_25(hafs):
    from quranic_phonemizer.analysis.ids import MergerId

    view, bundle, source = _build(hafs, "36:52-36:53", {})
    cb = _a_bridge_boundary(view)
    bad = dataclasses.replace(cb.bridges[0], merger_id=MergerId(999))
    broken = _replace_boundary(view, cb.boundary_id, bridges=(bad, *cb.bridges[1:]))
    with pytest.raises(CellValidationError):
        validate_cell_view(broken, bundle, source)


def test_an_iltiqa_insertion_given_a_bridge_fails_law_26(hafs):
    view, bundle, source = _build(hafs, "36:52-36:53", {})
    cb = _a_bridge_boundary(view)
    inserted = _inserted_column(9000)
    routed = dataclasses.replace(
        cb.bridges[0], before_column_ids=(inserted.id,)
    )
    broken = _replace_boundary(
        view, cb.boundary_id,
        columns=(*cb.columns, inserted), bridges=(routed, *cb.bridges[1:]),
    )
    with pytest.raises(CellValidationError):
        validate_cell_view(broken, bundle, source)


def test_law_26_in_isolation_rejects_an_inserted_bridge_endpoint(hafs):
    view, bundle, _ = _build(hafs, "36:52-36:53", {})
    cb = _a_bridge_boundary(view)
    inserted = _inserted_column(9000)
    routed = dataclasses.replace(cb.bridges[0], after_column_ids=(inserted.id,))
    broken = _replace_boundary(
        view, cb.boundary_id,
        columns=(*cb.columns, inserted), bridges=(routed, *cb.bridges[1:]),
    )
    with pytest.raises(CellValidationError):
        _check_no_iltiqa_bridge(broken, bundle)


def test_law_26_bites_a_bridge_over_the_real_host_owned_iltiqa(hafs):
    """The iltiqa vowel lives on its boundary but is never a merger bridge."""
    from quranic_phonemizer.analysis.ids import MergerId

    ref = "3:1-3:2"
    session = phonemize_request(hafs, ref)
    kw = dict(ref=ref, riwayah="hafs", script="uthmani", variant={})
    bundle = build_bundle(session, **kw)
    view = build_cell_view(
        session, **kw, spelling="transformed",
        pen=pen_for(hafs.inventory(Script.UTHMANI)),
    )
    occ = next(
        o for o in bundle.rule_occurrences if o.rule_id.value == "iltiqa_haraka"
    )
    assert occ.boundary_ids and occ.sound_ids
    boundary_id = occ.boundary_ids[0]
    boundary = next(b for b in view.boundaries if b.boundary_id == boundary_id)
    cell = next(c for c in boundary.sounds if c.sound_id == occ.sound_ids[0])
    bridge = CellBridge(
        merger_id=MergerId(0),
        before_column_ids=cell.column_ids,
        after_column_ids=cell.column_ids,
        sound=cell,
    )
    broken = _replace_boundary(view, boundary_id, bridges=(bridge,))
    with pytest.raises(CellValidationError, match="iltiqa"):
        _check_no_iltiqa_bridge(broken, bundle)


def test_a_dangling_bridge_endpoint_fails_law_28(hafs):
    view, bundle, source = _build(hafs, "36:52-36:53", {})
    cb = _a_bridge_boundary(view)
    bad = dataclasses.replace(cb.bridges[0], after_column_ids=(CellColumnId(9999),))
    broken = _replace_boundary(view, cb.boundary_id, bridges=(bad, *cb.bridges[1:]))
    with pytest.raises(CellValidationError):
        validate_cell_view(broken, bundle, source)


# ---- the whole corpus ----

@pytest.mark.slow
def test_the_view_laws_hold_over_the_whole_corpus(hafs, packed, sources):
    """Build the view for every verse joined and stopped after each internal
    word, in both scripts, and validate. A cross-word idgham raises a bridge;
    an iltiqa never does, and no boundary insertion column arises in Hafs."""
    info = packed.surah_info
    bridges = 0
    inserted = 0
    checked = 0
    for surah in range(1, 115):
        for ayah in range(1, len(info[str(surah)]) + 1):
            ref = f"{surah}:{ayah}"
            words_n = info[str(surah)][ayah - 1]
            stops = [f"{ref}:{word}" for word in range(1, words_n)]
            for kwargs in ({}, {"stop_refs": stops}):
                view, bundle, source = _build(hafs, ref, kwargs)
                validate_cell_view(view, bundle, source)
                bridges += sum(len(b.bridges) for b in view.boundaries)
                inserted += sum(
                    1 for b in view.boundaries for c in b.columns
                    if c.status is CellStatus.INSERTED
                )
                checked += 1
            for stop_refs in ((), tuple(stops)):
                session = _indopak_session(hafs, sources, surah, ayah, stop_refs)
                kw = dict(ref=ref, riwayah="hafs", script="indopak", variant={})
                view = build_cell_view(session, **kw)
                bundle = build_bundle(session, **kw)
                source = build_source_view(session, bundle=bundle)
                validate_cell_view(view, bundle, source)
                bridges += sum(len(b.bridges) for b in view.boundaries)
                checked += 1
    assert checked > 24000
    assert bridges > 0
    assert inserted == 0
