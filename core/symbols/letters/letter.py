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

from core.phoneme_registry import get_rule_phoneme

class LetterSymbol(Symbol):
    """Represents a consonant or vowel letter with associated diacritics, extensions, and other symbols."""

    def __init__(self, name: str, char: str, base_phoneme: str):
        super().__init__(name, char, base_phoneme)

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
        
    def prev_phoneme(self) -> Optional[str]:
        """
        Get the previous phoneme by looking at previous letters.
        Starts from the immediately previous letter and works backwards until a phoneme is found.
        Returns None if no previous phoneme is found.
        """
        # Start with the current word
        current_word = self.parent_word
        current_index = self.index_in_word
        
        # Look at previous letters in the current word
        while current_index > 0:
            current_index -= 1
            prev_letter = current_word.letters[current_index]
            if prev_letter.phonemes and prev_letter.phonemes:
                return prev_letter.phonemes[-1]  # Return the last phoneme of the previous letter
        
        # If no phoneme found in current word, check previous word
        prev_word = current_word.prev_word
        if prev_word:
            for letter in reversed(prev_word.letters):
                if letter.phonemes and letter.phonemes:
                    return letter.phonemes[-1]  # Return the last phoneme

        return None
        
    def find_prev_phoneme_letter(self) -> Optional[tuple["LetterSymbol", int]]:
        """
        Find the letter containing the previous phoneme and the index of that phoneme.
        Returns a tuple of (letter, phoneme_index) or None if no previous phoneme is found.
        This allows direct modification of the previous phoneme.
        """
        # Start with the current word
        current_word = self.parent_word
        current_index = self.index_in_word
        
        # Look at previous letters in the current word
        while current_index > 0:
            current_index -= 1
            prev_letter = current_word.letters[current_index]
            if prev_letter.phonemes and prev_letter.phonemes:
                return (prev_letter, len(prev_letter.phonemes) - 1)  # Return letter and index of last phoneme
        
        # If no phoneme found in current word, check previous word
        prev_word = current_word.prev_word
        if prev_word.letters:
            for letter in reversed(prev_word.letters):
                if letter.phonemes and letter.phonemes:
                    return (letter, len(letter.phonemes) - 1)  # Return letter and index of last phoneme

        return None
        
    def modify_prev_phoneme(self, new_phoneme: str) -> bool:
        result = self.find_prev_phoneme_letter()
        if result:
            letter, phoneme_idx = result
            letter.phonemes[phoneme_idx] = new_phoneme
            return True
        return False
        
    def can_phonemize(self) -> bool:
        return not self.is_phonemized

    def mark_phonemized(self, phonemes: Optional[List[str]] = None, affected_by: Optional["LetterSymbol"] = None):
        self.phonemes = phonemes or []
        self.is_phonemized = True
        self.affected_by = affected_by

    @final
    def phonemize(self) -> List[str]:
        # remove shaddah when starting at a word
        if self.is_first and self.parent_word.is_starting:
            self.has_shaddah = False

        # change diacritics when stopping at a word
        if self.is_last and self.parent_word.is_stopping:
            if self.char == "ء" and self.has_fathatan:
                self.diacritic = DiacriticSymbol("FATHA", "َ", "a")
            elif self.char in ["ى", "ا"]:
                self.diacritic = None
            else:
                self.diacritic = DiacriticSymbol("SUKUN", "۟", None)
        
        self.phonemes = self.phonemize_letter() + self.phonemize_modifiers()
        return self.phonemes

    def phonemize_letter(self) -> List[str]:
        if not self.diacritic and not self.has_shaddah: # silent
            return []
        
        return [self.apply_shaddah()]

    def apply_shaddah(self) -> str:
        if self.has_shaddah:
            return self.base_phoneme + self.base_phoneme
        
        return self.base_phoneme

    def phonemize_modifiers(self) -> List[str]:
        if self.has_tanween:
            return self.apply_tanween()
        
        if not self.diacritic:
            return []

        if self.has_sukun:
            return []
            
        return [self.diacritic.base_phoneme + (":" if self.extension else "")]

    def apply_tanween(self) -> List[str]:
        # split tanween
        short_vowel_ph = self.diacritic.base_phoneme[0]
        noon_ph        = self.diacritic.base_phoneme[1]

        next_letter = self.next_letter(1)
        if not next_letter:
            return []

        if next_letter.char in ["ا", "ى"]:
            if self.parent_word.is_stopping:
                return [short_vowel_ph + ":"] # tanween becomes long vowel
            else:
                next_letter.mark_phonemized(None, affected_by=self.diacritic)
                next_letter = self.next_letter(2)
                if not next_letter:
                    return [short_vowel_ph + ":"]
            
        # Iqlab
        if next_letter.char == "ب":
            return [short_vowel_ph, "m̃"]

        # Ikhfaa
        if next_letter.is_ikhfaa:
            return [short_vowel_ph, "ŋ" if next_letter.is_heavy else "ŋ"]
        
        # Idgham Ghunnah
        if next_letter.is_idgham_ghunnah:
            nasal_map = get_rule_phoneme("idgham", "nasalized_map")
            target_phoneme = nasal_map.get(next_letter.base_phoneme)
            next_letter.has_shaddah = False
            next_phonemes = [target_phoneme] + next_letter.phonemize_modifiers()
            next_letter.mark_phonemized(next_phonemes, affected_by=self)
            return [short_vowel_ph]

        # Idgham no Ghunnah
        if next_letter.char in ["ل", "ر"]:
            return [short_vowel_ph]

        # Ith-har
        return [short_vowel_ph, noon_ph]

    def has_symbol(self, symbol_name: str) -> bool:
        return any(symbol.name == symbol_name for symbol in self.other_symbols)
        
    @property
    def is_first(self) -> bool:
        return self.index_in_word == 0
    
    @property
    def is_last(self) -> bool:
        return self.index_in_word == len(self.parent_word.letters) - 1

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
    def is_idgham_ghunnah(self) -> bool:
        return self.char in ["ي", "ن", "م", "و"]

    @property
    def has_sukun(self) -> bool:
        return self.diacritic and self.diacritic.is_sukun

    @property
    def has_fatha(self) -> bool:
        return self.diacritic and self.diacritic.is_fatha

    @property
    def has_damma(self) -> bool:
        return self.diacritic and self.diacritic.is_damma

    @property
    def has_kasra(self) -> bool:
        return self.diacritic and self.diacritic.is_kasra

    @property
    def has_tanween(self) -> bool:
        return self.diacritic and self.diacritic.is_tanween

    @property
    def has_fathatan(self) -> bool:
        return self.diacritic and self.diacritic.is_fathatan