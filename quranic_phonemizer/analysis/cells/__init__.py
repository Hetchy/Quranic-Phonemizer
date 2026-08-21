"""The educational cell view over a source view: one column per letter unit.

The source cells nest into whole-word containers, each column carrying its
role, tier, attachment, provenance, status, silence, and unit rules.
"""
from __future__ import annotations

from .columns import build_cell_words
from .dtos import CellColumn, CellRole, CellStatus, CellTier, CellWord
from .laws import CellValidationError, validate_cell_columns

__all__ = [
    "CellColumn",
    "CellRole",
    "CellStatus",
    "CellTier",
    "CellValidationError",
    "CellWord",
    "build_cell_words",
    "validate_cell_columns",
]
