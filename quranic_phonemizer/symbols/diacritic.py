"""
DiacriticSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from .symbol import Symbol


class DiacriticSymbol(Symbol):
    def __init__(self, name: str, char: str, phoneme: Optional[str]):
        super().__init__(name, char, phoneme)

    @property
    def is_sukun(self) -> bool:
        return self.name == "SUKUN"

    @property
    def is_fatha(self) -> bool:
        return self.name == "FATHA"

    @property
    def is_damma(self) -> bool:
        return self.name == "DAMMA"

    @property
    def is_kasra(self) -> bool:
        return self.name == "KASRA"

    @property
    def is_tanween(self) -> bool:
        return self.name in ["FATHATAN", "DAMMATAN", "KASRATAN"]

    @property
    def is_fathatan(self) -> bool:
        return self.name == "FATHATAN"
        