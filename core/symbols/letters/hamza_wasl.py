#!/usr/bin/env python3
from typing import List, Dict, Any, Optional
from .letter import LetterSymbol

class HamzaWaslLetter(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.is_first and self.parent_word.is_starting:
            second_letter = self.next_letter(1)
            third_letter = self.next_letter(2)
            
            # noun case
            if second_letter and second_letter.char == "ل":
                return [self.base_phoneme, "a"]
            
            # verb case
            if third_letter and third_letter.diacritic:
                if third_letter.has_damma:
                    return [self.base_phoneme, "u"]
                if third_letter.has_fatha or third_letter.has_kasra:
                    return [self.base_phoneme, "i"]
            
        if self.is_first: # Iltiqaa Sakinayn
            prev_letter = self.prev_letter(1)
            if not prev_letter:
                return []

            if not prev_letter.phonemes:
                prev_letter = self.prev_letter(2)
                
            # case 1
            if prev_letter.has_tanween:
                prev_letter.phonemes.append("i")

            # case 2
            prev_phoneme = self.prev_phoneme()
            if prev_phoneme in ["a:", "u:", "i:"]:
                self.modify_prev_phoneme(prev_phoneme[0])

        # otherwise it is silent
        return []
