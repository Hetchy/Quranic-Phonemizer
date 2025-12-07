from typing import List
from .letter import LetterSymbol
from core.phoneme_registry import get_rule_phoneme


class Qalqala(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.has_sukun:
            if self.is_last and self.parent_word.is_stopping:
                self.set_mapping(rule="qalqala_kubra")
                return self.apply_shaddah() + [get_rule_phoneme("qalqala", "kubra")]
            
            self.set_mapping(rule="qalqala_sughra")
            return self.apply_shaddah() + [get_rule_phoneme("qalqala", "sughra")]
        
        return super().phonemize_letter()
