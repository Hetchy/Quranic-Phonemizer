from typing import List
from .letter import LetterSymbol
from ...phoneme_registry import get_rule_phoneme
from ...tajweed_rule import TajweedRule


class Meem(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.has_shaddah:
            self.set_tajweed_rule(TajweedRule.MEEM_GHUNNAH)
            return [get_rule_phoneme("idgham", "nasalized_map").get("m")]

        if self.diacritic:
            return [self.base_phoneme]

        next_letter = self.next_letter()

        # Ikhfaa Shafawi
        if self.is_last and next_letter.char == "ب":
            self.set_tajweed_rule(TajweedRule.IKHFAA_SHAFAWI, target=next_letter)
            return [get_rule_phoneme("ikhfaa", "shafawi_phoneme")]

        # Idgham Shafawi
        if self.is_last and next_letter.char == "م":
            self.set_tajweed_rule(TajweedRule.IDGHAM_SHAFAWI, target=next_letter)
            next_letter.mark_phonemized(next_letter.phonemize_modifiers(), affected_by=self)
            return [get_rule_phoneme("idgham", "nasalized_map").get("m")]

        # Izhar Shafawi
        return [self.base_phoneme]
