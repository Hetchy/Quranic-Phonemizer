from typing import List
from .letter import LetterSymbol
from ...phoneme_registry import get_rule_phoneme
from ...tajweed_rule import TajweedRule


class Noon(LetterSymbol):
    __slots__ = ()

    def phonemize_letter(self) -> List[str]:
        if self.has_shaddah:
            self.set_tajweed_rule(TajweedRule.NOON_GHUNNAH)
            return [get_rule_phoneme("idgham", "nasalized_map").get("n")]

        if self.diacritic:
            return [self.base_phoneme]

        next_letter = self.next_letter()

        # Iqlab
        if next_letter.char == "ب":
            self.set_tajweed_rule(TajweedRule.IQLAB_NOON, target=next_letter)
            return [get_rule_phoneme("iqlab", "phoneme")]

        # Ikhfaa
        if next_letter.is_ikhfaa:
            self.set_tajweed_rule(TajweedRule.IKHFAA_NOON, target=next_letter)
            ikhfaa_key = "heavy_phoneme" if next_letter.is_heavy else "light_phoneme"
            return [get_rule_phoneme("ikhfaa", ikhfaa_key)]

        # Idgham Ghunnah
        if next_letter.is_idgham_ghunnah:
            self.set_tajweed_rule(TajweedRule.IDGHAM_GHUNNAH_NOON, target=next_letter)
            nasal_map = get_rule_phoneme("idgham", "nasalized_map")
            target_phoneme = nasal_map.get(next_letter.base_phoneme)
            # Note: Don't clear has_shaddah - it's part of the canonical text and should be preserved
            next_phonemes = [target_phoneme] + next_letter.phonemize_modifiers()
            next_letter.mark_phonemized(next_phonemes)
            return []

        # Idgham no Ghunnah
        if next_letter.char in ["ل", "ر"]:
            self.set_tajweed_rule(TajweedRule.IDGHAM_BILA_GHUNNAH_NOON, target=next_letter)
            return []

        # Izhar
        return [self.base_phoneme]
