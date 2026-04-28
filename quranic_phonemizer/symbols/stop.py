"""
StopSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from .symbol import Symbol


class StopSymbol(Symbol):
    """Represents a stopping sign in the script."""

    __slots__ = ()

    def __init__(self, name: str, char: str, phoneme: Optional[str] = None):
        super().__init__(name, char, phoneme)
