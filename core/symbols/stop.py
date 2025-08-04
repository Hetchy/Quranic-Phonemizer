#!/usr/bin/env python3
"""
StopSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from .symbol import Symbol


class StopSymbol(Symbol):
    """Represents a stopping sign in the script."""
    def __init__(self, char: str, phoneme: Optional[str] = None, type_name: str = ""):
        super().__init__(char, phoneme)
        self.type = type_name
