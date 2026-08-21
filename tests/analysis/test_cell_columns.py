"""The source cell columns hold one column per letter unit over a source view.

Correctness is judged by the column laws run in every boundary state: one column
per unit in render order, riding marks on a main column, rules and silence exact.
"""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer.analysis.cells import (
    CellRole,
    CellStatus,
    CellTier,
    CellValidationError,
    build_cell_words,
    validate_cell_columns,
)
from quranic_phonemizer.analysis.cells.laws import _by_unit
from quranic_phonemizer.analysis.inscription import inscribe
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.analysis.source_dtos import CharacterKind, LiteralSilence
from quranic_phonemizer.model.address import (
    KhilafId,
    Option,
    VariantSelection,
)
from quranic_phonemizer.session import phonemize_request

#: One reference per boundary state and hard case: a word isolated, a start,
#: joined words, ikhfaa, a cross-word idgham merger, muqattaat, a long ayah, the
#: seen/saad khilaf, a dagger alif, a tatweel seat, and internal stops.
SITES = [
    ("1:1:1", {}),
    ("112:1", {}),
    ("1:1", {}),
    ("2:5", {}),
    ("36:52-36:53", {}),
    ("3:1-3:2", {}),
    ("2:255", {}),
    ("2:245:14", {}),
    ("2:2:1", {}),
    ("52:1:1", {}),
    ("18:38", {"stop_refs": ["18:38:1"]}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]

#: The small high rounded zero, marking a written letter no reading pronounces.
_SILENT_ZERO = "۟"
#: The tatweel seat a mark is written on, folded into the unit it qualifies.
_TATWEEL = "ـ"
#: The dagger alif the rasm leaves out, a carrier where the reading lengthens.
_DAGGER = "ٰ"


def _build(hafs, ref, kwargs, selection=VariantSelection()):
    session = phonemize_request(hafs, ref, selection=selection, **kwargs)
    view = build_source_view(
        session, ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    words = build_cell_words(
        session, ref=ref, riwayah="hafs", script="uthmani", variant={}
    )
    insc = inscribe(session)
    slot_of_unit = {
        u.id.value: insc.slot_of[min(c.value for c in u.character_ids)]
        for u in view.units if u.character_ids
    }
    return view, words, slot_of_unit


def _columns(words):
    return [col for word in words for col in word.columns]


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_one_column_per_unit_covering_the_characters_in_order(hafs, ref, kwargs):
    view, words, _ = _build(hafs, ref, kwargs)
    columns = _columns(words)
    assert len(columns) == len(view.units)
    lexical = sorted(
        c.id.value for c in view.characters if c.kind is CharacterKind.LEXICAL
    )
    covered = sorted(cid.value for col in columns for cid in col.source_character_ids)
    assert covered == lexical
    for word in words:
        firsts = [min(c.value for c in col.source_character_ids) for col in word.columns]
        assert firsts == sorted(firsts) and len(firsts) == len(set(firsts))


#: The shadda, folded into the letter it geminates rather than opening a unit.
_SHADDA = "ّ"


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_a_folded_scalar_opens_no_column(hafs, ref, kwargs):
    view, words, _ = _build(hafs, ref, kwargs)
    columns = _columns(words)
    assert all(len(col.source_unit_ids) == 1 for col in columns)
    # A shadda folds into the letter it geminates, so it never stands alone.
    for unit in view.units:
        if _SHADDA not in unit.text:
            continue
        held = [c for c in columns if unit.id in c.source_unit_ids]
        assert len(held) == 1 and len(held[0].text) > 1 and _SHADDA in held[0].text


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_roles_follow_the_unit_kind_and_the_reading(hafs, ref, kwargs):
    view, words, _ = _build(hafs, ref, kwargs)
    kind_role = {
        "haraka": CellRole.HARAKA,
        "sukun": CellRole.SUKUN,
        "tanween": CellRole.TANWEEN,
    }
    for col in _columns(words):
        unit = view.units[col.source_unit_ids[0].value]
        if unit.kind.value in kind_role:
            assert col.role is kind_role[unit.kind.value]
        else:
            assert col.role in (CellRole.LETTER, CellRole.MADD)


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_attachment_resolves_to_a_main_column_of_the_word_and_slot(hafs, ref, kwargs):
    view, words, slot_of_unit = _build(hafs, ref, kwargs)
    for word in words:
        mains = {col.id.value for col in word.columns if col.tier is CellTier.MAIN}
        by_id = {col.id.value: col for col in word.columns}
        for col in word.columns:
            if col.tier is CellTier.MAIN:
                assert col.attached_to_column_id is None
                continue
            assert col.attached_to_column_id.value in mains
            unit = view.units[col.source_unit_ids[0].value]
            seat = view.units[by_id[col.attached_to_column_id.value].source_unit_ids[0].value]
            if unit.written_on_unit_id is not None:
                assert seat.id == unit.written_on_unit_id
            else:
                assert slot_of_unit[unit.id.value] == slot_of_unit[seat.id.value]


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_column_rules_are_its_unit_placements(hafs, ref, kwargs):
    view, words, _ = _build(hafs, ref, kwargs)
    by_unit: dict[int, set[int]] = {}
    for placement in view.rule_placements:
        for unit in placement.unit_ids:
            by_unit.setdefault(unit.value, set()).add(placement.rule_occurrence_id.value)
    for col in _columns(words):
        expected = by_unit.get(col.source_unit_ids[0].value, set())
        assert {o.value for o in col.rule_occurrence_ids} == expected


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_column_silence_and_status_are_the_units(hafs, ref, kwargs):
    view, words, _ = _build(hafs, ref, kwargs)
    for col in _columns(words):
        unit = view.units[col.source_unit_ids[0].value]
        assert col.silence == unit.silence
        expected = CellStatus.DROPPED if unit.silence is not None else CellStatus.PRESENT
        assert col.status is expected


def test_the_sites_exercise_every_boundary_state(hafs):
    from quranic_phonemizer.analysis.build import build_bundle
    from quranic_phonemizer.analysis.dtos import BoundaryState

    states: set[BoundaryState] = set()
    for ref, kwargs in SITES:
        session = phonemize_request(hafs, ref, **kwargs)
        bundle = build_bundle(
            session, ref=ref, riwayah="hafs", script="uthmani", variant={}
        )
        states |= {b.state for b in bundle.boundaries}
    assert states == set(BoundaryState)


@pytest.mark.slow
def test_the_cell_column_laws_hold_over_the_whole_corpus(hafs, packed):
    """build_cell_words validates the columns against their source view; run it
    over every verse joined and stopped after each internal word, so the laws
    bite in every boundary state, not only on the curated sites."""
    from quranic_phonemizer.model.address import Script
    from quranic_phonemizer.orthography.inventory import InventoryError

    info = packed.surah_info
    uthmani = 0
    indopak = 0
    for surah in range(1, 115):
        for ayah in range(1, len(info[str(surah)]) + 1):
            ref = f"{surah}:{ayah}"
            words = info[str(surah)][ayah - 1]
            stops = [f"{ref}:{word}" for word in range(1, words)]
            for kwargs in ({}, {"stop_refs": stops}):
                _build(hafs, ref, kwargs)
                uthmani += 1
                try:
                    session = phonemize_request(
                        hafs, ref, script=Script.INDOPAK, **kwargs
                    )
                    build_cell_words(
                        session, ref=ref, riwayah="hafs", script="indopak",
                        variant={},
                    )
                except InventoryError:
                    continue
                indopak += 1
    assert uthmani > 12000
    assert indopak > 1500


def test_a_long_vowel_is_a_madd_carrier_with_the_haraka_above_it(hafs):
    """The waw of الطور carries the long vowel and takes a main madd column; the
    damma before it rides that column, attached above."""
    _, words, _ = _build(hafs, "52:1:1", {})
    columns = _columns(words)
    carrier = next(c for c in columns if c.role is CellRole.MADD)
    assert carrier.tier is CellTier.MAIN
    riders = [c for c in columns if c.attached_to_column_id == carrier.id]
    assert riders and all(c.role is CellRole.HARAKA for c in riders)
    assert all(c.tier in (CellTier.ABOVE, CellTier.BELOW) for c in riders)


def test_a_tatweel_seat_folds_into_one_column(hafs):
    """The tatweel is written on to seat a mark; it opens no column and stays
    inside the unit it lengthens."""
    view, words, _ = _build(hafs, "2:5", {})
    seat_units = [u for u in view.units if _TATWEEL in u.text]
    assert seat_units
    for unit in seat_units:
        held = [c for c in _columns(words) if unit.id in c.source_unit_ids]
        assert len(held) == 1 and _TATWEEL in held[0].text


def test_a_dagger_alif_is_madd_where_it_carries_and_a_letter_where_silent(hafs):
    """The dagger alif carries the long vowel in لكن and takes a madd column;
    in ذلك the fatha owns the length and the written alif is a dropped letter."""
    _, carrying, _ = _build(hafs, "18:38", {"stop_refs": ["18:38:1"]})
    carrier = next(
        c for c in _columns(carrying)
        if c.text == _DAGGER and c.role is CellRole.MADD
    )
    assert carrier.status is CellStatus.PRESENT

    _, silent, _ = _build(hafs, "2:2:1", {})
    dropped = next(c for c in _columns(silent) if c.text == _DAGGER)
    assert dropped.role is CellRole.LETTER and dropped.status is CellStatus.DROPPED


def test_a_silent_rasm_alif_is_a_dropped_letter_by_orthography(hafs):
    """A written alif the reading never says keeps its column so it can be
    greyed, owns no sound, and is silent by orthography."""
    seen = 0
    for ref, kwargs in SITES:
        _, words, _ = _build(hafs, ref, kwargs)
        for col in _columns(words):
            if _SILENT_ZERO not in col.text:
                continue
            seen += 1
            assert col.role is CellRole.LETTER
            assert col.status is CellStatus.DROPPED
            assert col.silence is LiteralSilence.ORTHOGRAPHIC
    assert seen


def test_the_seen_sad_pair_is_two_columns_carrying_the_variant_on_both(hafs):
    """Where the script writes the mini seen the site has two columns, one main
    and one riding it; the reading sounds one and drops the other, and both
    carry the selected khilaf as the choice flips which is dropped."""
    for choice, dropped_text in (("seen", "ص"), ("saad", "ۜ")):
        selection = VariantSelection(
            (Option(KhilafId.SEEN_SAD_YABSUT, choice),)
        )
        view, words, _ = _build(hafs, "2:245:14", {}, selection)
        pair = [
            c for c in _columns(words)
            if c.variant_id is KhilafId.SEEN_SAD_YABSUT
        ]
        assert len(pair) == 2
        assert all(c.variant_choice == choice for c in pair)
        riding = next(c for c in pair if c.tier is not CellTier.MAIN)
        base = next(c for c in pair if c.tier is CellTier.MAIN)
        assert riding.attached_to_column_id == base.id
        dropped = next(c for c in pair if c.status is CellStatus.DROPPED)
        assert dropped_text in dropped.text
        present = next(c for c in pair if c.status is CellStatus.PRESENT)
        assert present.silence is None


def test_the_default_seen_sad_site_is_two_columns_without_a_variant(hafs):
    view, words, _ = _build(hafs, "2:245:14", {})
    riders = [
        c for c in _columns(words)
        if view.units[c.source_unit_ids[0].value].written_on_unit_id is not None
    ]
    assert len(riders) == 1
    assert all(c.variant_id is None for c in _columns(words))


@pytest.mark.parametrize(
    "option",
    [
        Option(KhilafId.MADD_LAZIM_TASHEEL, "tasheel"),
        Option(KhilafId.IQLAB_NASAL, "assimilated"),
        Option(KhilafId.SEEN_SAD_BASTAH, "seen"),
    ],
)
def test_a_foreign_khilaf_leaves_the_seen_sad_pair_unmarked(hafs, option):
    """Selecting a khilaf that does not govern this pair's word -- another
    site's seen/saad among them -- marks neither cell of the pair."""
    _, words, _ = _build(hafs, "2:245:14", {}, VariantSelection((option,)))
    assert all(c.variant_id is None for c in _columns(words))


def _replace_column(words, target, **changes):
    out = []
    for word in words:
        cols = tuple(
            dataclasses.replace(col, **changes) if col.id == target else col
            for col in word.columns
        )
        out.append(dataclasses.replace(word, columns=cols))
    return tuple(out)


def test_validation_rejects_a_dropped_character(hafs):
    view, words, slot = _build(hafs, "1:1", {})
    first = words[0].columns[0]
    broken = _replace_column(
        words, first.id, source_character_ids=first.source_character_ids[1:]
    )
    with pytest.raises(CellValidationError):
        validate_cell_columns(broken, view, slot)


def test_validation_rejects_attachment_to_another_slot(hafs):
    view, words, slot = _build(hafs, "1:1:1", {})
    rider = next(c for c in _columns(words) if c.tier is not CellTier.MAIN)
    other_main = next(
        c for c in _columns(words)
        if c.tier is CellTier.MAIN and c.id != rider.attached_to_column_id
        and slot[view.units[c.source_unit_ids[0].value].id.value]
        != slot[view.units[rider.source_unit_ids[0].value].id.value]
    )
    broken = _replace_column(words, rider.id, attached_to_column_id=other_main.id)
    with pytest.raises(CellValidationError):
        validate_cell_columns(broken, view, slot)


def test_validation_rejects_a_rule_on_the_wrong_column(hafs):
    view, words, slot = _build(hafs, "112:1", {})
    placement = view.rule_placements[0]
    target_unit = placement.unit_ids[0].value
    clean = next(
        c for c in _columns(words)
        if placement.rule_occurrence_id not in c.rule_occurrence_ids
        and c.source_unit_ids[0].value != target_unit
    )
    broken = _replace_column(
        words, clean.id,
        rule_occurrence_ids=(placement.rule_occurrence_id,),
    )
    with pytest.raises(CellValidationError):
        validate_cell_columns(broken, view, slot)


def test_validation_rejects_an_invented_silence(hafs):
    view, words, slot = _build(hafs, "1:1", {})
    sounding = next(
        c for c in _columns(words)
        if c.silence is None and c.status is CellStatus.PRESENT
    )
    broken = _replace_column(
        words, sounding.id, silence=LiteralSilence.ORTHOGRAPHIC
    )
    with pytest.raises(CellValidationError):
        validate_cell_columns(broken, view, slot)


def test_by_unit_rejects_two_columns_for_one_unit(hafs):
    view, words, _ = _build(hafs, "1:1:1", {})
    columns = _columns(words)
    doubled = columns + [columns[0]]
    with pytest.raises(CellValidationError):
        _by_unit(doubled)
