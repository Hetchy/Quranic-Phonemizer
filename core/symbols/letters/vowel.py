from typing import List
from .letter import LetterSymbol

class VowelLetter(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if any(symbol.name == "SILENT_ALWAYS" for symbol in self.other_symbols):
            return []

        if not self.parent_word.is_stopping and any(symbol.name == "SILENT_AT_CONTINUATION" for symbol in self.other_symbols):
            return []
            
        if not self.diacritic:
            prev_letter = self.prev_letter(1)
            if prev_letter.phonemes:
                match (
                    prev_letter.phonemes[-1], 
                    self.char, 
                    self.extension.name if self.extension else None
                ):
                    case ("a", vowel, DAGGER_ALEF) if vowel in ["و", "ى"]:
                        prev_letter.phonemes[-1] += ":"
                    case ("a", "ا", None):
                        prev_letter.phonemes[-1] += ":"
                    case ("u", "و", None):
                        prev_letter.phonemes[-1] += ":"
                    case ("i", yaa, None) if yaa in ["ي", "ۧ"]:
                        prev_letter.phonemes[-1] += ":"
                return []

        return super().phonemize_letter()

class AlefMaksuraLetter(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.diacritic or self.has_shaddah: # treat as Yaa
            return super().phonemize_letter()

        prev_phoneme = self.prev_phoneme()
        if prev_phoneme in ["a", "i"]:
            self.modify_prev_phoneme(prev_phoneme + ":")
            return []
            
        return []