from typing import List
from .letter import LetterSymbol

class QalqalaLetter(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if not self.is_last and self.has_sukun:
            return [self.apply_shaddah(), "Q"]

        if self.is_last and self.has_sukun and self.parent_word.is_stopping:
            return [self.apply_shaddah(), "Q"]

        return super().phonemize_letter()
    