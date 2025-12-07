"""
LetterSymbol class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import List, Optional, final, TYPE_CHECKING

from ..symbol import Symbol
from ..diacritic import DiacriticSymbol
from ..extension import ExtensionSymbol
from ..other import OtherSymbol

from core.phoneme_registry import get_rule_phoneme
from core.mapping import MappingType

if TYPE_CHECKING:
    from core.word import Word


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
        
        # Mapping metadata
        self._mapping_type: MappingType = MappingType.STANDARD
        self._rule: Optional[str] = None

    def prev_letter(self, n: int = 1) -> Optional["LetterSymbol"]:
        return self.parent_word.get_prev_letter(self.index_in_word, n)

    def next_letter(self, n: int = 1) -> Optional["LetterSymbol"]:
        return self.parent_word.get_next_letter(self.index_in_word, n)
        
    def prev_phoneme(self) -> Optional[str]:
        current_word = self.parent_word
        current_index = self.index_in_word
        
        while current_index > 0:
            current_index -= 1
            prev_letter = current_word.letters[current_index]
            if prev_letter.phonemes and prev_letter.phonemes:
                return prev_letter.phonemes[-1]
        
        prev_word = current_word.prev_word
        if prev_word:
            for letter in reversed(prev_word.letters):
                if letter.phonemes and letter.phonemes:
                    return letter.phonemes[-1]

        return None
        
    def find_prev_phoneme_letter(self) -> Optional[tuple["LetterSymbol", int]]:
        current_word = self.parent_word
        current_index = self.index_in_word
        
        while current_index > 0:
            current_index -= 1
            prev_letter = current_word.letters[current_index]
            if prev_letter.phonemes and prev_letter.phonemes:
                return (prev_letter, len(prev_letter.phonemes) - 1)
        
        prev_word = current_word.prev_word
        if prev_word.letters:
            for letter in reversed(prev_word.letters):
                if letter.phonemes and letter.phonemes:
                    return (letter, len(letter.phonemes) - 1)

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

    def set_mapping(self, mapping_type: MappingType = None, rule: str = None):
        """Set mapping metadata for this letter."""
        if mapping_type is not None:
            self._mapping_type = mapping_type
        if rule is not None:
            self._rule = rule

    def _determine_mapping_type(self) -> MappingType:
        if self._mapping_type != MappingType.STANDARD:
            return self._mapping_type
        if not self.phonemes:
            return MappingType.SILENT
        if self.has_shaddah or (self.diacritic and self.diacritic.is_tanween):
            return MappingType.ONE_TO_MANY
        if self._rule:
            return MappingType.CONTEXTUAL
        return MappingType.STANDARD

    @property
    def mapping_type(self) -> MappingType:
        return self._determine_mapping_type()
    
    @property
    def rule(self) -> Optional[str]:
        return self._rule

    @final
    def phonemize(self) -> List[str]:
        if self.is_first and self.parent_word.is_starting:
            self.has_shaddah = False

        if self.is_last and self.parent_word.is_stopping:
            if self.char == "ء" and self.has_fathatan:
                self.diacritic = DiacriticSymbol("FATHA", "َ", "a")
                self.extend()
            elif self.char in ["ى", "ا"]:
                self.diacritic = None
            else:
                self.diacritic = DiacriticSymbol("SUKUN", "۟", None)
        
        self.phonemes = self.phonemize_letter() + self.phonemize_modifiers()
        return self.phonemes

    def phonemize_letter(self) -> List[str]:
        if not self.diacritic and not self.has_shaddah:
            self.set_mapping(mapping_type=MappingType.SILENT, rule="idgham_other")
            return []
        return self.apply_shaddah()

    def apply_shaddah(self, phoneme: Optional[str] = None) -> List[str]:
        if self.has_shaddah:
            base = phoneme or self.base_phoneme
            return [base + base]
        return [phoneme or self.base_phoneme]

    def phonemize_modifiers(self) -> List[str]:
        if not self.diacritic:
            return []
        if self.has_sukun:
            return []
        if self.has_tanween:
            return self.apply_tanween()

        result = self.diacritic.base_phoneme
        if self.has_fatha and (self.is_heavy or self.char == "ر"):
            result += "ˤ"
        if self.extension:
            result += ":"
        return [result]

    def apply_tanween(self) -> List[str]:
        short_vowel_ph = self.diacritic.base_phoneme[0]
        noon_ph = self.diacritic.base_phoneme[1]

        next_letter = self.next_letter(1)
        if not next_letter:
            return []

        if next_letter.char in ["ا", "ى"]:
            if self.parent_word.is_stopping:
                self.set_mapping(rule="waqf_tanween")
                return [short_vowel_ph + ":"]
            else:
                next_letter.mark_phonemized(None, affected_by=self.diacritic)
                next_letter.set_mapping(mapping_type=MappingType.SILENT, rule="tanween_alif")
                next_letter = self.next_letter(2)
                if not next_letter:
                    return [short_vowel_ph + ":"]
            
        # Iqlab
        if next_letter.char == "ب":
            self.set_mapping(rule="iqlab_tanween")
            next_letter.set_mapping(rule="iqlab_tanween")
            return [short_vowel_ph, get_rule_phoneme("iqlab", "phoneme")]

        # Ikhfaa
        if next_letter.is_ikhfaa:
            self.set_mapping(rule="ikhfaa_tanween")
            next_letter.set_mapping(rule="ikhfaa_tanween")
            ikhfaa_key = "heavy_phoneme" if next_letter.is_heavy else "light_phoneme"
            return [short_vowel_ph, get_rule_phoneme("ikhfaa", ikhfaa_key)]
        
        # Idgham Ghunnah
        if next_letter.is_idgham_ghunnah:
            self.set_mapping(mapping_type=MappingType.MANY_TO_ONE, rule="idgham_ghunnah_tanween")
            next_letter.set_mapping(mapping_type=MappingType.MANY_TO_ONE, rule="idgham_ghunnah_tanween")
            nasal_map = get_rule_phoneme("idgham", "nasalized_map")
            target_phoneme = nasal_map.get(next_letter.base_phoneme)
            next_letter.has_shaddah = False
            next_phonemes = [target_phoneme] + next_letter.phonemize_modifiers()
            next_letter.mark_phonemized(next_phonemes, affected_by=self)
            return [short_vowel_ph]

        # Idgham no Ghunnah
        if next_letter.char in ["ل", "ر"]:
            self.set_mapping(mapping_type=MappingType.MANY_TO_ONE, rule="idgham_bila_ghunnah_tanween")
            next_letter.set_mapping(mapping_type=MappingType.MANY_TO_ONE, rule="idgham_bila_ghunnah_tanween")
            return [short_vowel_ph]

        # Izhar
        self.set_mapping(rule="izhar_tanween")
        return [short_vowel_ph, noon_ph]

    def has_symbol(self, symbol_name: str) -> bool:
        return any(symbol.name == symbol_name for symbol in self.other_symbols)
        
    def extend(self):
        if not self.extension:
            self.extension = ExtensionSymbol("", "", None)

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
