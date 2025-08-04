#!/usr/bin/env python3
"""
OtherSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from .symbol import Symbol


class OtherSymbol(Symbol):
    """A catch-all for any other symbols that may appear."""
    def __init__(self, char: str, phoneme: Optional[str] = None):
        super().__init__(char, phoneme)
