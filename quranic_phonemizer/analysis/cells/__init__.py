"""The educational cell view over a source view: words, sounds, and boundaries.

Columns nest into whole-word containers and between-word boundaries; one
CellSound per core sound, with a cross-word merger's sound held in its bridge.
"""
from __future__ import annotations

from .align import build_cell_sounds
from .columns import build_cell_words
from .dtos import (
    CellBoundary,
    CellBridge,
    CellColumn,
    CellGroup,
    CellGroupKind,
    CellRole,
    CellSide,
    CellSound,
    CellStatus,
    CellTier,
    CellView,
    CellWord,
)
from .laws import CellValidationError, validate_cell_columns, validate_cell_sounds
from .transform import transform_words
from .transform_laws import validate_transformed
from .view import build_cell_view
from .view_laws import validate_cell_view

__all__ = [
    "CellBoundary",
    "CellBridge",
    "CellColumn",
    "CellGroup",
    "CellGroupKind",
    "CellRole",
    "CellSide",
    "CellSound",
    "CellStatus",
    "CellTier",
    "CellValidationError",
    "CellView",
    "CellWord",
    "build_cell_sounds",
    "build_cell_view",
    "build_cell_words",
    "transform_words",
    "validate_cell_columns",
    "validate_cell_sounds",
    "validate_cell_view",
    "validate_transformed",
]
