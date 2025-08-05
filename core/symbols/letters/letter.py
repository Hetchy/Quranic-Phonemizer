#!/usr/bin/env python3
"""
LetterSymbol class for the Quranic phonemizer.
Moved into core/symbols/letters/ directory.
"""

from __future__ import annotations

from typing import List, Optional, final

from ..symbol import Symbol
from ..diacritic import DiacriticSymbol
from ..extension import ExtensionSymbol
from ..other import OtherSymbol

class LetterSymbol(Symbol):
    """Represents a consonant or vowel letter with associated diacritics, extensions, and other symbols."""

    def __init__(self, char: str, base_phoneme: str):
        super().__init__(char, base_phoneme)

        self.parent_word: Word
        self.index_in_word: int
        self.has_shaddah: bool = False
        self.diacritic: Optional[DiacriticSymbol] = None
        self.extension: Optional[ExtensionSymbol] = None
        self.other_symbols: List[OtherSymbol] = []

        self.phonemes: List[str] = []
        self.is_phonemized: bool = False
        self.affected_by: Optional["LetterSymbol"] = None

    def prev_letter(self, n: int = 1) -> Optional["LetterSymbol"]:
        return self.parent_word.get_prev_letter(self.index_in_word, n)

    def next_letter(self, n: int = 1) -> Optional["LetterSymbol"]:
        return self.parent_word.get_next_letter(self.index_in_word, n)

    @property
    def is_last(self) -> bool:
        return self.index_in_word == len(self.parent_word.letters) - 1
    
    @property
    def is_first(self) -> bool:
        return self.index_in_word == 0

    @property
    def is_heavy(self) -> bool:
        return self.char in ["خ", "ص", "ض", "غ", "ط", "ق", "ظ"]

    @property
    def is_qalqala(self) -> bool:
        return self.char in ["ق", "ط", "ب", "ج", "د"]

    @property
    def is_ikhfaa(self) -> bool:
        return self.char in ["ت", "ث", "ج", "د", "ذ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك"]

    @property
    def is_idgham(self) -> bool:
        return self.char in ["ي", "ن", "م", "و"]

    @property
    def has_sukun(self) -> bool:
        return self.diacritic and self.diacritic.is_sukun()

    @property
    def has_fatha(self) -> bool:
        return self.diacritic and self.diacritic.is_fatha()

    @property
    def has_damma(self) -> bool:
        return self.diacritic and self.diacritic.is_damma()

    @property
    def has_kasra(self) -> bool:
        return self.diacritic and self.diacritic.is_kasra()

    @property
    def has_tanween(self) -> bool:
        return self.diacritic and self.diacritic.is_tanween()

    @property
    def can_phonemize(self) -> bool:
        return not self.is_phonemized

    def mark_phonemized(self, phonemes: List[str], affected_by: Optional["LetterSymbol"] = None) -> None:
        self.phonemes = phonemes
        self.is_phonemized = True
        self.affected_by = affected_by

    @final
    def phonemize(self) -> List[str]:
        if self.is_last and self.parent_word.is_stopping:
            self.diacritic = DiacriticSymbol("ۡ", "SUKUN")
        return self.phonemize_letter() + self.phonemize_modifiers()

    def phonemize_letter(self) -> List[str]:
        if not self.diacritic: # silent
            return []
        return [self.apply_shaddah()]

    def phonemize_modifiers(self) -> List[str]:
        if self.has_tanween:
            # split tanween into two phonemes e.g. ["a", "n"]
            return [self.diacritic.base_phoneme[0], self.diacritic.base_phoneme[1]]

        out = []
        if self.diacritic:
            out.append(self.diacritic.base_phoneme)
        # if self.extension and self.extension.base_phoneme:
        #     out.append(self.extension.base_phoneme)
        return out

    def apply_shaddah(self) -> str:
        if self.has_shaddah and not (self.is_first and self.parent_word.is_starting):
            return self.base_phoneme + self.base_phoneme
        return self.base_phoneme
