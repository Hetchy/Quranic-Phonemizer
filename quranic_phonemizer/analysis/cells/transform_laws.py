"""Validation the transformed cell view must pass before a consumer reads it.

An inserted column invents no source and anchors validly, a replaced or dropped
column keeps its provenance, and variant fields match the resolved selection.
"""
from __future__ import annotations

from ...model.address import VariantSelection
from ..checks import requirer
from ..source_dtos import SourceView
from .dtos import CellColumn, CellStatus, CellView
from .laws import CellValidationError

_require = requirer(CellValidationError)


def _all_columns(view: CellView) -> list[CellColumn]:
    out = [col for word in view.words for col in word.columns]
    for boundary in view.boundaries:
        out.extend(boundary.columns)
    return out


def _check_inserted(col: CellColumn, units: int) -> None:
    _require(
        not col.source_character_ids and not col.source_unit_ids,
        f"inserted column {col.id.value} invents a source character or unit",
    )
    _require(
        col.anchor_unit_id is not None and col.side is not None,
        f"inserted column {col.id.value} has no unit and side anchor",
    )
    _require(
        col.anchor_unit_id.value < units,
        f"inserted column {col.id.value} anchors to no source unit",
    )


def _check_replaced_dropped(
    col: CellColumn, source: SourceView, split_units: set[int]
) -> None:
    _require(
        bool(col.source_unit_ids),
        f"{col.status.value} column {col.id.value} spans no source unit",
    )
    units = [source.units[uid.value] for uid in col.source_unit_ids]
    split = any(unit.id.value in split_units for unit in units)
    expected = tuple(character for unit in units for character in unit.character_ids)
    if split:
        _require(
            bool(col.source_character_ids)
            and set(col.source_character_ids).issubset(expected),
            f"{col.status.value} column {col.id.value} names characters outside its source unit",
        )
    else:
        _require(
            col.source_character_ids == expected,
            f"{col.status.value} column {col.id.value} loses its source characters",
        )
    if col.status is CellStatus.DROPPED:
        text = (
            "".join(
                source.characters[item.value].text
                for item in col.source_character_ids
            )
            if split else "".join(unit.text for unit in units)
        )
        _require(
            col.text == text,
            f"dropped column {col.id.value} loses its source text",
        )


def _is_partitioned_unit(
    unit_id: int, columns: list[CellColumn], source: SourceView
) -> bool:
    """Recognize projections that partition one written compound by glyph."""
    roles = {column.role.value for column in columns}
    text = source.units[unit_id].text
    if (
        len(columns) != 2
        or any(not column.source_character_ids for column in columns)
        or not (
            (text in {"َا", "ُا", "ِا"} and roles == {"haraka", "letter"})
            or ("ٓ" in text and roles == {"letter", "madd"})
        )
    ):
        return False
    expected = sorted(character.value for character in source.units[unit_id].character_ids)
    got = sorted(
        character.value for column in columns
        for character in column.source_character_ids
    )
    return got == expected


def _variant_dependent(col: CellColumn) -> bool:
    return bool(
        col.owned_sound_ids or col.presented_sound_ids
    ) or col.status is CellStatus.DROPPED


def _check_variant(col: CellColumn, selection: VariantSelection) -> None:
    if col.variant_id is None:
        _require(
            col.variant_choice is None,
            f"column {col.id.value} names a variant choice with no variant",
        )
        return
    _require(
        col.variant_choice == selection.chosen(col.variant_id),
        f"column {col.id.value} variant choice is not the resolved selection",
    )
    _require(
        _variant_dependent(col),
        f"column {col.id.value} carries a variant on no dependent state",
    )


def _check_no_native_insertion_twins(columns: tuple[CellColumn, ...]) -> None:
    native = {
        (column.attached_to_column_id, column.role, column.text)
        for column in columns
        if column.attached_to_column_id is not None
        and column.source_character_ids
        and column.status is not CellStatus.DROPPED
    }
    for column in columns:
        if (
            column.status is not CellStatus.INSERTED
            or column.attached_to_column_id is None
        ):
            continue
        _require(
            (column.attached_to_column_id, column.role, column.text) not in native,
            f"inserted column {column.id.value} duplicates a written mark",
        )


def validate_transformed(
    view: CellView, source: SourceView, selection: VariantSelection
) -> None:
    units = len(source.units)
    columns_by_unit: dict[int, list[CellColumn]] = {}
    for word in view.words:
        for column in word.columns:
            for unit in column.source_unit_ids:
                columns_by_unit.setdefault(unit.value, []).append(column)
    split_units = {
        unit_id for unit_id, columns in columns_by_unit.items()
        if _is_partitioned_unit(unit_id, columns, source)
    }
    for word in view.words:
        _check_no_native_insertion_twins(word.columns)
    for col in _all_columns(view):
        if col.status is CellStatus.INSERTED:
            _check_inserted(col, units)
        elif col.status in (CellStatus.REPLACED, CellStatus.DROPPED):
            _check_replaced_dropped(col, source, split_units)
        _check_variant(col, selection)


__all__ = ["validate_transformed"]
