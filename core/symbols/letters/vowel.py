from typing import List
from .letter import LetterSymbol

class VowelLetter(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if any(symbol.name == "SILENT" for symbol in self.other_symbols):
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
                    case ("i", yaa, None) if yaa in ["ي", "ى", "ۧ"]:
                        prev_letter.phonemes[-1] += ":"
                return []

        return super().phonemize_letter()