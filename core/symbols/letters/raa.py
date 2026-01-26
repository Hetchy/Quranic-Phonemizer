from typing import List
from .letter import LetterSymbol
from core.phoneme_registry import get_rule_phoneme
from core.mapping import MappingType


class Raa(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        prev = self.prev_letter()
        prev2 = self.prev_letter(2)
        nxt = self.next_letter()

        if not self.diacritic: # e.g. وَٱذۡكُر رَّبَّكَ
            self.set_mapping(mapping_type=MappingType.SILENT, rule="idgham_mutamathilayn")
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
                        match prev2.diacritic.name:
                            case "FATHA" | "DAMMA":
                                return self._heavy_phoneme()
                            case "KASRA":
                                return self._light_phoneme()
    
    def _heavy_phoneme(self) -> List[str]:
        self.set_mapping(rule="raa_heavy")
        return self.apply_shaddah(get_rule_phoneme("raa_heavy", "phoneme"))

    def _light_phoneme(self) -> List[str]:
        self.set_mapping(rule="raa_light")
        return super().phonemize_letter()
