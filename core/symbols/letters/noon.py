#!/usr/bin/env python3
from typing import List, Dict, Any, Optional
from .letter import LetterSymbol

from core.phoneme_registry import get_rule_phoneme

class NoonLetter(LetterSymbol):
    def phonemize_letter(self):
        if self.has_shaddah:
            return ["ñ"]
        if self.diacritic:
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
        
        # Idgham Ghunnah
        if next_letter.is_idgham_ghunnah:
            nasal_map = get_rule_phoneme("idgham", "nasalized_map")
            target_phoneme = nasal_map.get(next_letter.base_phoneme)
            next_letter.has_shaddah = False
            next_phonemes = [target_phoneme] + next_letter.phonemize_modifiers()
            next_letter.mark_phonemized(next_phonemes, affected_by=self)
            return []

        # Idgham no Ghunnah
        if next_letter.char in ["ل", "ر"]:
            return []
        
        return ["n??"]