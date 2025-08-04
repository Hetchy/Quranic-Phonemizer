#!/usr/bin/env python3
"""
Base Symbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Optional
from abc import ABC, abstractmethod


class Symbol(ABC):
    """Abstract base class for all symbols in a word."""
    def __init__(self, char: str, phoneme: Optional[str] = None):
        self.char = char
        self.phoneme = phoneme
