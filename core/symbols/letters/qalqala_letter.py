from typing import List
from .letter import LetterSymbol
from core.phoneme_registry import get_rule_phoneme

class Qalqala(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.has_sukun:
            # Qalqala Kubra
            if self.is_last and self.parent_word.is_stopping:
                return self.apply_shaddah() + [get_rule_phoneme("qalqala", "kubra")]

            # Qalqala Sughra
            return self.apply_shaddah() + [get_rule_phoneme("qalqala", "sughra")]

        return super().phonemize_letter()
    