from typing import List
from .letter import LetterSymbol
from core.phoneme_registry import get_rule_phoneme

class Meem(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.has_shaddah:
            return [get_rule_phoneme("idgham", "nasalized_map").get("m")]
        
        if self.diacritic:
            return [self.base_phoneme]
        
        next_letter = self.next_letter()

        # ikhfaa shafawi
        if self.is_last and next_letter.char == "ب":
            return [get_rule_phoneme("ikhfaa", "shafawi_phoneme")]
        
        # idgham shafawi
        if self.is_last and next_letter.char == "م":
            next_letter.mark_phonemized(next_letter.phonemize_modifiers(), affected_by=self)
            return [get_rule_phoneme("idgham", "nasalized_map").get("m")]
            
        return [self.base_phoneme]
