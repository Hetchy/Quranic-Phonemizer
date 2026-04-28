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
    """Diacritic instances are cached and immutable. The is_* boolean
    predicates are pre-computed and stored as plain slot attributes (not
    @property descriptors) so look-ups in the hot phonemize_modifiers /
    apply_tanween paths are direct slot reads."""

    __slots__ = (
        "is_sukun", "is_fatha", "is_damma", "is_kasra",
        "is_tanween", "is_fathatan",
    )

    def __new__(cls, name: str, char: str, phoneme: Optional[str]):
        key = (name, char, phoneme)
        cached = _DIACRITIC_POOL.get(key)
        if cached is not None:
            return cached
        obj = super().__new__(cls)
        Symbol.__init__(obj, name, char, phoneme)
        obj.is_sukun = name == "SUKUN"
        obj.is_fatha = name == "FATHA"
        obj.is_damma = name == "DAMMA"
        obj.is_kasra = name == "KASRA"
        obj.is_fathatan = name == "FATHATAN"
        obj.is_tanween = name in ("FATHATAN", "DAMMATAN", "KASRATAN")
        _DIACRITIC_POOL[key] = obj
        return obj

    def __init__(self, name: str, char: str, phoneme: Optional[str]):
        # __new__ already initialised attributes (or returned a cached
        # instance). Skip re-initialisation to avoid redundant work.
        pass
