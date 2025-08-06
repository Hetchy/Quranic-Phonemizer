from typing import List
from .letter import LetterSymbol

class QalqalaLetter(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.has_sukun:
            # Qalqala Kubra
            if self.is_last and self.parent_word.is_stopping:
                return [self.apply_shaddah(), "Q"]

            # Qalqala Sughra
            return [self.apply_shaddah(), "Q"]

        return super().phonemize_letter()
    