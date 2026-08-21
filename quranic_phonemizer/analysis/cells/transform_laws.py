"""Validation the transformed cell view must pass before a consumer reads it.

An inserted column invents no source and anchors validly, a replaced or dropped
column keeps its provenance, and variant fields match the resolved selection.
"""
from __future__ import annotations

from ...model.address import VariantSelection
from ..source_dtos import SourceView
from .dtos import CellColumn, CellStatus, CellView
from .laws import _require


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


def _check_replaced_dropped(col: CellColumn, source: SourceView) -> None:
    _require(
        len(col.source_unit_ids) == 1,
        f"{col.status.value} column {col.id.value} spans not one source unit",
    )
    unit = source.units[col.source_unit_ids[0].value]
    _require(
        col.source_character_ids == unit.character_ids,
        f"{col.status.value} column {col.id.value} loses its source characters",
    )
    if col.status is CellStatus.DROPPED:
        _require(
            col.text == unit.text,
            f"dropped column {col.id.value} loses its source text",
        )


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


def validate_transformed(
    view: CellView, source: SourceView, selection: VariantSelection
) -> None:
    units = len(source.units)
    for col in _all_columns(view):
        if col.status is CellStatus.INSERTED:
            _check_inserted(col, units)
        elif col.status in (CellStatus.REPLACED, CellStatus.DROPPED):
            _check_replaced_dropped(col, source)
        _check_variant(col, selection)


__all__ = ["validate_transformed"]
