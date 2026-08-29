"""Validation the source cell columns must pass before a consumer reads them.

One column per unit, its characters and text that unit's; every lexical
character once in render order; a riding mark on a main column; rules exact.
"""
from __future__ import annotations

from ..checks import requirer
from ..dtos import Sound
from ..source_dtos import CharacterKind, SourceView
from .dtos import CellColumn, CellRole, CellSound, CellStatus, CellTier, CellWord


class CellValidationError(ValueError):
    """Source cell columns that do not close over their source view."""


_require = requirer(CellValidationError)


def _by_unit(columns: list[CellColumn]) -> dict[int, CellColumn]:
    out: dict[int, CellColumn] = {}
    for col in columns:
        _require(len(col.source_unit_ids) == 1, "a source column spans not one unit")
        uid = col.source_unit_ids[0].value
        _require(uid not in out, f"unit {uid} has two columns")
        out[uid] = col
    return out


def _check_unit_binding(columns: list[CellColumn], view: SourceView) -> None:
    for col in columns:
        unit = view.units[col.source_unit_ids[0].value]
        _require(
            col.source_character_ids == unit.character_ids,
            "a column's characters are not its unit's",
        )
        _require(col.text == unit.text, "a column's text is not its unit's")


def _check_coverage(columns: list[CellColumn], view: SourceView) -> None:
    lexical = sorted(
        c.id.value for c in view.characters if c.kind is CharacterKind.LEXICAL
    )
    got = sorted(cid.value for col in columns for cid in col.source_character_ids)
    _require(got == lexical, "columns do not cover the lexical characters once")


def _check_order(words: tuple[CellWord, ...], view: SourceView) -> None:
    for word in words:
        last = -1
        for col in word.columns:
            if col.status is CellStatus.GAP:
                continue
            unit = view.units[col.source_unit_ids[0].value]
            _require(unit.word_id == word.word_id, "a column sits in the wrong word")
            first = min(c.value for c in col.source_character_ids)
            _require(first > last, "columns are out of render order")
            last = first


def _check_attachment(
    word: CellWord, view: SourceView, slot_of_unit: dict[int, object]
) -> None:
    columns = {col.id.value: col for col in word.columns}
    mains = {cid for cid, col in columns.items() if col.tier is CellTier.MAIN}
    for col in word.columns:
        if col.tier is CellTier.MAIN:
            _require(col.attached_to_column_id is None, "a main column attaches out")
            continue
        _require(col.attached_to_column_id is not None, "a riding column attaches to nothing")
        target = col.attached_to_column_id.value
        _require(target in mains, "attachment is not a main column of the word")
        unit = view.units[col.source_unit_ids[0].value]
        seat = view.units[columns[target].source_unit_ids[0].value]
        # A written_on target that is itself riding -- the iqlab meem on the
        # tanween -- seats on a main of that target's slot, not the target.
        seated_on = unit.written_on_unit_id.value if unit.written_on_unit_id else unit.id.value
        _require(
            slot_of_unit.get(seat.id.value) == slot_of_unit.get(seated_on),
            "attachment leaves the mark's slot: "
            f"word={word.word_id.value} column={col.id.value} text={col.text!r} "
            f"unit={unit.id.value} seated_on={seated_on} "
            f"target={target} seat_unit={seat.id.value} "
            f"mark_slot={slot_of_unit.get(seated_on)!r} "
            f"seat_slot={slot_of_unit.get(seat.id.value)!r}",
        )


def _check_rules(columns: list[CellColumn], view: SourceView) -> None:
    by_unit: dict[int, set[int]] = {}
    for placement in view.rule_placements:
        for unit in placement.unit_ids:
            by_unit.setdefault(unit.value, set()).add(placement.rule_occurrence_id.value)
    for col in columns:
        expected: set[int] = set()
        for unit in col.source_unit_ids:
            expected |= by_unit.get(unit.value, set())
        _require(
            {o.value for o in col.rule_occurrence_ids} == expected,
            "a column's rules disagree with its unit placements",
        )


def _check_silence(by_unit: dict[int, CellColumn], view: SourceView) -> None:
    for uid, col in by_unit.items():
        _require(
            col.silence == view.units[uid].silence,
            f"column for unit {uid} invents a silence",
        )


def validate_cell_columns(
    words: tuple[CellWord, ...], view: SourceView, slot_of_unit: dict[int, object]
) -> None:
    columns = [
        col for word in words for col in word.columns
        if col.status is not CellStatus.GAP
    ]
    by_unit = _by_unit(columns)
    _require(len(by_unit) == len(view.units), "there is not one column per unit")
    _check_unit_binding(columns, view)
    _check_coverage(columns, view)
    _check_order(words, view)
    for word in words:
        _check_attachment(word, view, slot_of_unit)
    _check_rules(columns, view)
    _check_silence(by_unit, view)


def _spans(words: tuple[CellWord, ...]) -> dict[int, list[CellColumn]]:
    """Per sound, the source columns whose own set names it, in render order."""
    out: dict[int, list[CellColumn]] = {}
    for word in words:
        for col in word.columns:
            for sound in (*col.owned_sound_ids, *col.presented_sound_ids):
                out.setdefault(sound.value, []).append(col)
    return out


def _render_index(words: tuple[CellWord, ...]) -> dict[int, int]:
    return {
        col.id.value: i
        for i, col in enumerate(col for word in words for col in word.columns)
    }


def _check_sound_coverage(words: tuple[CellWord, ...], sounds: tuple[Sound, ...]) -> None:
    held: dict[int, int] = {}
    for word in words:
        for cell in word.sounds:
            sid = cell.sound_id.value
            _require(sid not in held, f"sound {sid} has two cells")
            held[sid] = word.word_id.value
    _require(
        set(held) == {s.id.value for s in sounds},
        "the sound cells are not exactly the core sounds",
    )
    for sound in sounds:
        _require(
            held[sound.id.value] == sound.word_id.value,
            f"sound {sound.id.value} is held by the wrong word",
        )


def _check_gap_columns(columns: dict[int, CellColumn]) -> None:
    """A gap column is role and status gap, carries no provenance, ownership or
    silence, and anchors to exactly one unit/side."""
    for col in columns.values():
        if col.status is not CellStatus.GAP:
            continue
        _require(col.role is CellRole.GAP, f"gap column {col.id.value} is not role gap")
        _require(
            not col.source_character_ids and not col.source_unit_ids
            and not col.owned_sound_ids and not col.presented_sound_ids
            and col.silence is None,
            f"gap column {col.id.value} carries provenance, sound, or silence",
        )
        _require(
            col.anchor_unit_id is not None and col.side is not None,
            f"gap column {col.id.value} has no unit and side anchor",
        )


def _check_span(cell: CellSound, spans: dict[int, list[CellColumn]],
                columns: dict[int, CellColumn]) -> None:
    expected = [col.id for col in spans.get(cell.sound_id.value, ())]
    if expected:
        _require(list(cell.column_ids) == expected,
                 f"sound {cell.sound_id.value} spans other than its columns")
    else:
        _require(len(cell.column_ids) == 1,
                 f"presenter-less sound {cell.sound_id.value} spans not one gap")
        gap = columns[cell.column_ids[0].value]
        _require(gap.status is CellStatus.GAP,
                 f"sound {cell.sound_id.value} hangs on a non-gap column")


def _check_ordered_nonempty(cell: CellSound, render: dict[int, int]) -> None:
    _require(bool(cell.column_ids), f"sound {cell.sound_id.value} spans nothing")
    positions = [render[c.value] for c in cell.column_ids]
    _require(positions == sorted(set(positions)),
             f"sound {cell.sound_id.value} span is out of render order")


def validate_cell_sounds(
    words: tuple[CellWord, ...], sounds: tuple[Sound, ...]
) -> None:
    spans = _spans(words)
    render = _render_index(words)
    columns = {col.id.value: col for word in words for col in word.columns}
    rules = {s.id.value: s.rule_occurrence_ids for s in sounds}
    _check_sound_coverage(words, sounds)
    _check_gap_columns(columns)
    for word in words:
        for cell in word.sounds:
            _check_span(cell, spans, columns)
            _check_ordered_nonempty(cell, render)
            _require(
                cell.rule_occurrence_ids == rules[cell.sound_id.value],
                f"sound {cell.sound_id.value} cell rules are not its sound's",
            )


__all__ = [
    "CellValidationError",
    "validate_cell_columns",
    "validate_cell_sounds",
]
