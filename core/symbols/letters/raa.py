from typing import List
from .letter import LetterSymbol
from core.phoneme_registry import get_rule_phoneme

class Raa(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        prev = self.prev_letter()
        prev2 = self.prev_letter(2)
        nxt = self.next_letter()

        if not self.diacritic:
            return [] # only in "وَٱذْكُر رَّبَّكَ" Idgham

        match self.diacritic.name: # check raa diacritic
            case "FATHA" | "FATHATAN" | "DAMMA" | "DAMMATAN":
                return self._heavy_phoneme()
            case "KASRA" | "KASRATAN":
                return self._light_phoneme()
            
            case "SUKUN": # check prev letter
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
                        return self._heavy_phoneme() if nxt.is_heavy else self._light_phoneme()
                    
                    case "SUKUN": # check prev prev letter
                        match prev2.diacritic.name:
                            case "FATHA" | "DAMMA":
                                return self._heavy_phoneme()
                            case "KASRA":
                                return self._light_phoneme()
    
    def _heavy_phoneme(self) -> List[str]:
        return self.apply_shaddah(get_rule_phoneme("raa_heavy", "phoneme"))

    def _light_phoneme(self) -> List[str]:
        return super().phonemize_letter()