#!/usr/bin/env python3
from typing import List, Dict, Any, Optional
from .letter import LetterSymbol

class HamzaWaslLetter(LetterSymbol):
    def phonemize(self) -> List[str]:
        if self.is_first and self.parent_word.is_starting:
            second_letter = self.next_letter(1)
            third_letter = self.next_letter(2)
            
            # noun case
            if second_letter and second_letter.char == "ل":
                return ["ʔ", "a"]
            
            # verb case
            if third_letter and third_letter.diacritic:
                if third_letter.has_damma:
                    return ["ʔ", "u"]
                if third_letter.has_fatha or third_letter.has_kasra:
                    return ["ʔ", "i"]
            
            return ["ʔ?"]
        
        if self.is_first: # Iltiqaa Sakinayn
            prev_letter = self.prev_letter(1)

            if prev_letter.has_tanween:
                prev_letter.phonemes.append("i")

            elif prev_letter.phonemes and prev_letter.phonemes[-1] in ["a:", "u:", "i:"]:
                prev_letter.phonemes[-1] -= ":"
            
        # otherwise it is silent
        return []
