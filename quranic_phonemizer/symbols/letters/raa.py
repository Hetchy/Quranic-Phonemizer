from typing import List
from .letter import LetterSymbol
from ...phoneme_registry import get_rule_phoneme
from ...tajweed_rule import TajweedRule


class Raa(LetterSymbol):
    __slots__ = ()

    def phonemize_letter(self) -> List[str]:
        prev = self.prev_letter()
        prev2 = self.prev_letter(2)
        nxt = self.next_letter()

        if not self.diacritic: # e.g. وَٱذۡكُر رَّبَّكَ
            self.set_tajweed_rule(TajweedRule.IDGHAM_MUTAMATHILAYN, target=self.next_letter())
            return []

        
        match self.diacritic.name:
            case "FATHA" | "FATHATAN" | "DAMMA" | "DAMMATAN":
                return self._heavy_phoneme()
            case "KASRA" | "KASRATAN":
                return self._light_phoneme()

            case "SUKUN":
                if not prev.diacritic:
                    match prev.char:
                        case "ٱ" | "ا" | "و":
                            return self._heavy_phoneme()
                        case "ي":
                            return self._light_phoneme()

                match prev.diacritic.name:
                    case "FATHA" | "DAMMA":
                        return self._heavy_phoneme()
                    case "KASRA":
                        if nxt and nxt.is_heavy and nxt.parent_word == self.parent_word:
                            return self._heavy_phoneme()
                        else:
                            return self._light_phoneme()

                    case "SUKUN":
                        if prev.char == "ي":
                            return self._light_phoneme()

                        match prev2.diacritic.name:
                            case "FATHA" | "DAMMA":
                                return self._heavy_phoneme()
                            case "KASRA":
                                return self._light_phoneme()

    def _heavy_phoneme(self) -> List[str]:
        self.set_tajweed_rule(TajweedRule.TAFKHEEM)
        return self.apply_shaddah(get_rule_phoneme("raa_heavy", "phoneme"))

    def _light_phoneme(self) -> List[str]:
        return super().phonemize_letter()
