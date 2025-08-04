#!/usr/bin/env python3
"""
LetterSymbol class for the Quranic phonemizer.
Moved into core/symbols/letters/ directory.
"""

from __future__ import annotations

from typing import List, Optional

from ..symbol import Symbol
from ..diacritic import DiacriticSymbol
from ..extension import ExtensionSymbol
from ..other import OtherSymbol
from core.phoneme_registry import get_base_phoneme


class LetterSymbol(Symbol):
    """Represents a consonant or vowel letter with associated diacritics, extensions, and other symbols."""

    def __init__(self, char: str, phoneme: Optional[str] = None):
        resolved_phoneme = phoneme if phoneme is not None else get_base_phoneme(char)
        super().__init__(char, resolved_phoneme)

        self.parent_word: Optional["Word"] = None 
        self.index_in_word: Optional[int] = None
        self.diacritic: Optional[DiacriticSymbol] = None
        self.extension: Optional[ExtensionSymbol] = None
        self.has_shaddah: bool = False
        self.other_symbols: List[OtherSymbol] = []

        self.phonemes: List[str] = []
        self.is_phonemized: bool = False
        self.affected_by: Optional["LetterSymbol"] = None
        self.affects: List["LetterSymbol"] = []


    @property
    def prev_letter(self) -> Optional["LetterSymbol"]:
        if self.parent_word is None or self.index_in_word is None:
            return None
        return self.parent_word.get_previous_letter(self.index_in_word)

    def next_letter(self, n: int = 1) -> Optional["LetterSymbol"]:
        if self.parent_word is None or self.index_in_word is None:
            return None
        return self.parent_word.get_next_letter(self.index_in_word, n)

    # ------------------------------------------------------------------
    # Basic operations --------------------------------------------------
    # ------------------------------------------------------------------
    def add_diacritic(self, diacritic: DiacriticSymbol) -> None:
        self.diacritic = diacritic

    def can_phonemize(self) -> bool:
        return not self.is_phonemized

    def mark_phonemized(self, phonemes: List[str], affected_by: Optional["LetterSymbol"] = None) -> None:
        self.phonemes = phonemes
        self.is_phonemized = True
        self.affected_by = affected_by

    def add_affects(self, letter: "LetterSymbol") -> None:
        self.affects.append(letter)

    # ------------------------------------------------------------------
    # Phonemization API --------------------------------------------------
    # ------------------------------------------------------------------
    def phonemize(self) -> List[str]:
        return self.phonemize_letter() + self.phonemize_modifiers()

    def phonemize_letter(self) -> List[str]:
        """Phoneme(s) produced by the letter itself (override in subclasses)."""
        return [self.phoneme]

    def phonemize_modifiers(self) -> List[str]:
        """Phonemes coming from diacritics, extensions and other symbols."""
        out: List[str] = []
        if self.diacritic and self.diacritic.phoneme:
            out.append(self.diacritic.phoneme)
        if self.extension and self.extension.phoneme:
            out.append(self.extension.phoneme)
        return out

    # ------------------------------------------------------------------
    # Helper boolean checks ---------------------------------------------
    # ------------------------------------------------------------------
    def get_primary_diacritic(self) -> Optional[DiacriticSymbol]:
        if not self.diacritic:
            return None
        if not self.diacritic.is_sukoon() and not self.diacritic.is_tanween():
            return self.diacritic
        return None

    def has_vowel_diacritic(self) -> bool:
        return bool(self.get_primary_diacritic())

    def is_heavy(self) -> bool:
        return self.char in ["خ", "ص", "ض", "غ", "ط", "ق", "ظ"]

    def is_qalqala(self) -> bool:
        return self.char in ["ق", "ط", "ب", "ج", "د"]

    def is_ikhfaa(self) -> bool:
        return self.char in [
            "ت", "ث", "ج", "د", "ذ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك",
        ]

    def is_noon(self) -> bool:
        return self.char == "ن"

    def is_meem(self) -> bool:
        return self.char == "م"

    def has_sukoon(self) -> bool:
        return self.diacritic and self.diacritic.is_sukoon()

    def has_tanween(self) -> bool:
        return self.diacritic and self.diacritic.is_tanween()

    def is_baa(self) -> bool:
        return self.char == "ب"
