from typing import List
from .letter import LetterSymbol

class VowelLetter(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if not self.diacritic: # vowel
            prev_letter = self.prev_letter()
            if prev_letter.phonemes and prev_letter.phonemes[-1] in ["a", "u", "i"]:
                prev_letter.phonemes[-1] += ":"
            else: 
                return ["vowel?"]

        return super().phonemize_letter()
            
