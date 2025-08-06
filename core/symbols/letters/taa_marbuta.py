from typing import List
from .letter import LetterSymbol

class TaaMarbuta(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.is_last and self.has_sukun:
            return ["h"]
        return [self.base_phoneme]
