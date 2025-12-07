from typing import List
from .letter import LetterSymbol
from core.mapping import MappingType


class VowelLetter(LetterSymbol):
    def _lengthen_compatible_phoneme(self, compatible_phonemes: List[str]) -> List[str]:
        prev_phoneme = self.prev_phoneme()
        if prev_phoneme in compatible_phonemes:
            # Remove short vowel from previous letter and return long vowel here
            result = self.find_prev_phoneme_letter()
            if result:
                letter, idx = result
                short_vowel = letter.phonemes.pop(idx)
                return [short_vowel + ":"]
        self.set_mapping(mapping_type=MappingType.SILENT)
        return []


class Alef(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            self.set_mapping(mapping_type=MappingType.SILENT, rule="alef_silent_always")
            return []
        if not self.parent_word.is_stopping and self.has_symbol("SILENT_AT_CONTINUATION"):
            self.set_mapping(mapping_type=MappingType.SILENT, rule="alef_silent_continuation")
            return []
        return self._lengthen_compatible_phoneme(["a", "aˤ"])


class AlefMaksura(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.diacritic or self.has_shaddah:
            return super().phonemize_letter()
        return self._lengthen_compatible_phoneme(["a", "aˤ", "i"])


class Waw(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            self.set_mapping(mapping_type=MappingType.SILENT, rule="waw_silent")
            return []
        if self.diacritic:
            return super().phonemize_letter()
        return self._lengthen_compatible_phoneme(["a", "u"])


class Yaa(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            self.set_mapping(mapping_type=MappingType.SILENT, rule="yaa_silent")
            return []
        if self.diacritic:
            return super().phonemize_letter()
        return self._lengthen_compatible_phoneme(["i"])
