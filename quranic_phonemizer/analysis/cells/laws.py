"""Validation the source cell columns must pass before a consumer reads them.

One column per unit; every lexical character in one column in render order; a
riding mark on a main column of its word and slot; unit rules and silence exact.
"""
from __future__ import annotations

from ..source_dtos import CharacterKind, SourceView
from .dtos import CellColumn, CellTier, CellWord


class CellValidationError(ValueError):
    """Source cell columns that do not close over their source view."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CellValidationError(message)


def _by_unit(columns: list[CellColumn]) -> dict[int, CellColumn]:
    out: dict[int, CellColumn] = {}
    for col in columns:
        _require(len(col.source_unit_ids) == 1, "a source column spans not one unit")
        uid = col.source_unit_ids[0].value
        _require(uid not in out, f"unit {uid} has two columns")
        out[uid] = col
    return out


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
        if unit.written_on_unit_id is not None:
            _require(seat.id == unit.written_on_unit_id, "attachment ignores written_on")
        else:
            _require(
                slot_of_unit.get(unit.id.value) == slot_of_unit.get(seat.id.value),
                "attachment crosses a slot",
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
    columns = [col for word in words for col in word.columns]
    by_unit = _by_unit(columns)
    _require(len(by_unit) == len(view.units), "there is not one column per unit")
    _check_coverage(columns, view)
    _check_order(words, view)
    for word in words:
        _check_attachment(word, view, slot_of_unit)
    _check_rules(columns, view)
    _check_silence(by_unit, view)


__all__ = ["CellValidationError", "validate_cell_columns"]
