#!/usr/bin/env python3
"""
DiacriticSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from .symbol import Symbol


class DiacriticSymbol(Symbol):
    """Represents a short vowel or other diacritical mark."""
    def __init__(self, char: str, phoneme: Optional[str] = None, type_name: str = ""):
        super().__init__(char, phoneme)
        self.type = type_name

    def is_tanween(self) -> bool:
        """Check if this diacritic is a tanween."""
        return self.type in ["FATHATAN", "DAMMATAN", "KASRATAN"]

    def is_sukoon(self) -> bool:
        """Check if this diacritic is a sukoon."""
        return self.type == "SUKUN"
