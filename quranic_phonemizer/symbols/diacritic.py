"""
DiacriticSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple
from .symbol import Symbol


# Flyweight cache keyed by (name, char, phoneme). DiacriticSymbol is
# immutable in practice (no mutating methods, no mutable state), so a
# small set of canonical instances can be shared across hundreds of
# thousands of letter usages, eliminating per-call allocation.
_DIACRITIC_POOL: Dict[Tuple[str, str, Optional[str]], "DiacriticSymbol"] = {}


class DiacriticSymbol(Symbol):
    __slots__ = ()

    def __new__(cls, name: str, char: str, phoneme: Optional[str]):
        key = (name, char, phoneme)
        cached = _DIACRITIC_POOL.get(key)
        if cached is not None:
            return cached
        obj = super().__new__(cls)
        Symbol.__init__(obj, name, char, phoneme)
        _DIACRITIC_POOL[key] = obj
        return obj

    def __init__(self, name: str, char: str, phoneme: Optional[str]):
        # __new__ already initialised attributes (or returned a cached
        # instance). Skip re-initialisation to avoid redundant work.
        pass

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
        return self.name in ("FATHATAN", "DAMMATAN", "KASRATAN")

    @property
    def is_fathatan(self) -> bool:
        return self.name == "FATHATAN"
