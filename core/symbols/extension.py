#!/usr/bin/env python3
"""
ExtensionSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from .symbol import Symbol


class ExtensionSymbol(Symbol):
    """Represents symbols that extend vowels or have special phonetic properties."""
    def __init__(self, name: str, char: str, phoneme: Optional[str] = None):
        super().__init__(name, char, phoneme)
