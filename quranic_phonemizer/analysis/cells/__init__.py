"""The educational cell view over a source view: columns and their sounds.

Columns nest into whole-word containers; one CellSound per core sound spans the
columns that own or present it, or a gap column where the source presents none.
"""
from __future__ import annotations

from .align import build_cell_sounds
from .columns import build_cell_words
from .dtos import (
    CellColumn,
    CellRole,
    CellSide,
    CellSound,
    CellStatus,
    CellTier,
    CellWord,
)
from .laws import CellValidationError, validate_cell_columns, validate_cell_sounds

__all__ = [
    "CellColumn",
    "CellRole",
    "CellSide",
    "CellSound",
    "CellStatus",
    "CellTier",
    "CellValidationError",
    "CellWord",
    "build_cell_sounds",
    "build_cell_words",
    "validate_cell_columns",
    "validate_cell_sounds",
]
