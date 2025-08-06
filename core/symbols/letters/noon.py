from typing import List
from .letter import LetterSymbol

from core.phoneme_registry import get_rule_phoneme

class Noon(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.has_shaddah:
            return [get_rule_phoneme("idgham", "nasalized_map").get("n")]
        
        if self.diacritic:
            return [self.base_phoneme]
        
        next_letter = self.next_letter()

        # Iqlab
        if next_letter.char == "ب":
            return [get_rule_phoneme("iqlab", "phoneme")]
        
        # Ikhfaa    
        if next_letter.is_ikhfaa:
            ikhfaa_key = "heavy_phoneme" if next_letter.is_heavy else "light_phoneme"
            return [get_rule_phoneme("ikhfaa", ikhfaa_key)]
        
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
        
        return [self.base_phoneme]