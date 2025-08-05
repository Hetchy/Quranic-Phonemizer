#!/usr/bin/env python3
from typing import List, Dict, Any, Optional
from .letter import LetterSymbol

from core.phoneme_registry import get_rule_phoneme

class NoonLetter(LetterSymbol):
    def phonemize_letter(self):
        if self.has_shaddah:
            return ["ñ"]
        if self.diacritic or (self.is_last and self.parent_word.is_stopping):
            return [self.base_phoneme]
        
        next_letter = self.next_letter()
        if not next_letter:
            return ["n?"]

        # Iqlab
        if next_letter.char == "ب":
            return ["m̃"]
        
        # Ikhfaa    
        if next_letter.is_ikhfaa:
            return ["ŋ"] if next_letter.is_heavy else ["ŋ"]
        
        # Idgham
        if next_letter.is_idgham:
            nasal_map = get_rule_phoneme("idgham", "nasalized_map")
            target_phoneme = nasal_map.get(next_letter.base_phoneme)
            next_letter.mark_phonemized([target_phoneme], affected_by=self)
            return []
        
        return ["n??"]