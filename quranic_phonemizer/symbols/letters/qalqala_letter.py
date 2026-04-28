from typing import List
from .letter import LetterSymbol
from ...phoneme_registry import get_rule_phoneme
from ...tajweed_rule import TajweedRule


class Qalqala(LetterSymbol):
    __slots__ = ()

    def phonemize_letter(self) -> List[str]:
        if self.has_sukun:
            if self.is_last and self.parent_word.is_stopping:
                self.set_tajweed_rule(TajweedRule.QALQALA_KUBRA)
                return self.apply_shaddah() + [get_rule_phoneme("qalqala", "kubra")]

            self.set_tajweed_rule(TajweedRule.QALQALA_SUGHRA)
            return self.apply_shaddah() + [get_rule_phoneme("qalqala", "sughra")]

        return super().phonemize_letter()
