"""Semantic sound-cardinality bounds for transformed cell groups."""
from __future__ import annotations

from ..checks import requirer
from .dtos import CellRole, CellView
from .laws import CellValidationError

_require = requirer(CellValidationError)


def check_cell_cardinality(view: CellView) -> None:
    """A lexical column owns at most two sounds; only tanween groups may own
    three.  Muqattaat are named-letter runs, not lexical grapheme cells: one
    compact source glyph legitimately owns the sounds of the whole letter
    name, while its transformed view expands that run into ordinary cells.
    """
    for word in view.words:
        # Source spelling intentionally keeps compact source ownership.  The
        # semantic bound applies after projection, whose words have groups.
        if not word.groups or word.runs:
            continue
        columns = {column.id: column for column in word.columns}
        overfull_column = next(
            (
                column for column in word.columns
                if len(column.owned_sound_ids) > 2
            ),
            None,
        )
        _require(
            overfull_column is None,
            "column "
            f"{overfull_column.id.value if overfull_column is not None else '?'} "
            "owns more than two sounds",
        )
        overfull_group = next(
            (group for group in word.groups if len(group.sound_ids) > 3), None
        )
        _require(
            overfull_group is None,
            "visual group "
            f"{overfull_group.key.value if overfull_group is not None else '?'} "
            "owns more than three sounds",
        )
        unlicensed_three = next(
            (
                group for group in word.groups
                if len(group.sound_ids) == 3
                and not any(
                    columns[column].role is CellRole.TANWEEN
                    for column in group.column_ids
                )
            ),
            None,
        )
        _require(
            unlicensed_three is None,
            "three-sound visual group "
            f"{unlicensed_three.key.value if unlicensed_three is not None else '?'} "
            "has no tanween",
        )


__all__ = ["check_cell_cardinality"]
