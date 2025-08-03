"""
Symbol classes for the Quranic phonemizer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class Symbol(ABC):
    """Abstract base class for all symbols in a word."""
    def __init__(self, char: str, phoneme: Optional[str] = None):
        self.char = char
        self.phoneme = phoneme


class LetterSymbol(Symbol):
    """Represents a consonant or vowel letter."""
    def __init__(self, char: str, phoneme: Optional[str] = None):
        super().__init__(char, phoneme)
        self.diacritics: List[DiacriticSymbol] = []
        self.extension: Optional[ExtensionSymbol] = None
        self.has_shaddah: bool = False

    def add_diacritic(self, diacritic: DiacriticSymbol) -> None:
        """Add a diacritic to this letter."""
        self.diacritics.append(diacritic)
        
    def get_primary_diacritic(self) -> Optional[DiacriticSymbol]:
        """Get the primary diacritic (vowel) for this letter."""
        for diacritic in self.diacritics:
            if not diacritic.is_sukoon() and not diacritic.is_tanween():
                return diacritic
        return None

    def has_vowel_diacritic(self) -> bool:
        """Check if the letter has a vowel diacritic."""
        return any(not d.is_sukoon() and not d.is_tanween() for d in self.diacritics)

    def is_heavy(self) -> bool:
        """Check if the letter is heavy (has a shaddah or is inherently heavy)."""
        return self.has_shaddah

    def is_qalqala(self) -> bool:
        """Check if the letter is a qalqalah letter."""
        return self.char in ['ق', 'ط', 'ب', 'ج', 'د']

    def is_ikhfaa(self) -> bool:
        """Check if the letter is involved in ikhfaa rules."""
        return self.char in ['ت', 'ث', 'ج', 'د', 'ذ', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ف', 'ق', 'ك']

    def is_noon(self) -> bool:
        """Check if the letter is a noon."""
        return self.char == 'ن'

    def is_meem(self) -> bool:
        """Check if the letter is a meem."""
        return self.char == 'م'

    def has_sukoon(self) -> bool:
        """Check if the letter has a sukoon."""
        return any(d.is_sukoon() for d in self.diacritics)

    def has_tanween(self) -> bool:
        """Check if the letter has tanween."""
        return any(d.is_tanween() for d in self.diacritics)


class DiacriticSymbol(Symbol):
    """Represents a short vowel or other diacritical mark."""
    def __init__(self, char: str, phoneme: Optional[str] = None, type_name: str = ""):
        super().__init__(char, phoneme)
        self.type = type_name

    def is_tanween(self) -> bool:
        """Check if this diacritic is a tanween."""
        return self.type in ["FATHATAN", "DAMMATAN", "KASRATAN"]

    def is_sukoon(self) -> bool:
        """Check if this diacritic is a sukoon."""
        return self.type == "SUKUN"


class ExtensionSymbol(Symbol):
    """Represents symbols that extend vowels or have special phonetic properties."""
    def __init__(self, char: str, phoneme: Optional[str] = None, type_name: str = ""):
        super().__init__(char, phoneme)
        self.type = type_name


class StopSymbol(Symbol):
    """Represents a stopping sign in the script."""
    def __init__(self, char: str, phoneme: Optional[str] = None, type_name: str = ""):
        super().__init__(char, phoneme)
        self.type = type_name


class OtherSymbol(Symbol):
    """A catch-all for any other symbols that may appear."""
    def __init__(self, char: str, phoneme: Optional[str] = None):
        super().__init__(char, phoneme)
