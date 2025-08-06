from typing import List
from .letter import LetterSymbol

class VowelLetter(LetterSymbol):
    def _lengthen_compatible_phoneme(self, compatible_phonemes: List[str]) -> List[str]:
        prev_phoneme = self.prev_phoneme()
        if prev_phoneme in compatible_phonemes:
            self.modify_prev_phoneme(prev_phoneme + ":")
        return []

class Alef(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            return []

        if not self.parent_word.is_stopping and self.has_symbol("SILENT_AT_CONTINUATION"):
            return []  # e.g. أَنَا۠

        return self._lengthen_compatible_phoneme(["a"])

class AlefMaksura(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.diacritic or self.has_shaddah:
            # treat as Yaa
            return super().phonemize_letter()
        
        return self._lengthen_compatible_phoneme(["a", "i"])

class Waw(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            return []  # e.g. أُو۟لَـٰٓئِكَ

        if self.diacritic:
            return super().phonemize_letter()

        return self._lengthen_compatible_phoneme(["a", "u"])

class Yaa(VowelLetter):
    def phonemize_letter(self) -> List[str]:
        if self.has_symbol("SILENT_ALWAYS"):
            return []  # e.g. أَفَإِي۟ن

        if self.diacritic:
            return super().phonemize_letter()

        return self._lengthen_compatible_phoneme(["i"])