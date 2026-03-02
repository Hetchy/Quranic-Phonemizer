"""
Base Symbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from abc import ABC, abstractmethod


class Symbol(ABC):
    """Abstract base class for all symbols in a word."""
    def __init__(self, name: str, char: str, phoneme: Optional[str] = None):
        self.name = name
        self.char = char
        self.base_phoneme = phoneme
