#!/usr/bin/env python3
"""
DiacriticSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from .symbol import Symbol


class DiacriticSymbol(Symbol):
    def __init__(self, char: str, type_name: str, phoneme: Optional[str] = None):
        super().__init__(char, phoneme)
        self.type = type_name

    @property
    def is_sukun(self) -> bool:
        return self.type == "SUKUN"

    @property
    def is_fatha(self) -> bool:
        return self.type == "FATHA"

    @property
    def is_damma(self) -> bool:
        return self.type == "DAMMA"

    @property
    def is_kasra(self) -> bool:
        return self.type == "KASRA"

    @property
    def is_tanween(self) -> bool:
        return self.type in ["FATHATAN", "DAMMATAN", "KASRATAN"]

    @property
    def is_fathatan(self) -> bool:
        return self.type == "FATHATAN"
        