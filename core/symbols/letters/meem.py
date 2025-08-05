#!/usr/bin/env python3
from typing import List
from .letter import LetterSymbol

class MeemLetter(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.has_shaddah:
            return ["m̃"]
        if self.diacritic:
            return [self.base_phoneme]
        if self.is_last and self.parent_word.is_stopping:
            return [self.base_phoneme]
        
        next_letter = self.next_letter()
        if not next_letter:
            return ["m?"]

        # ikhfaa shafawi
        if self.is_last and next_letter.char == "ب":
            return ["ɱ"]
        
        # idgham shafawi
        if self.is_last and next_letter.char == "م":
            next_letter.mark_phonemized([], affected_by=self)
            return ["m̃"]
            
        return ["m??"]
