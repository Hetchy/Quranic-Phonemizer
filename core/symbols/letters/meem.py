from typing import List
from .letter import LetterSymbol
from core.phoneme_registry import get_rule_phoneme
from core.mapping import MappingType


class Meem(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.has_shaddah:
            self.set_mapping(rule="meem_ghunnah")
            return [get_rule_phoneme("idgham", "nasalized_map").get("m")]
        
        if self.diacritic:
            return [self.base_phoneme]
        
        next_letter = self.next_letter()

        # Ikhfaa Shafawi
        if self.is_last and next_letter.char == "ب":
            self.set_mapping(rule="ikhfaa_shafawi")
            next_letter.set_mapping(rule="ikhfaa_shafawi")
            return [get_rule_phoneme("ikhfaa", "shafawi_phoneme")]
        
        # Idgham Shafawi
        if self.is_last and next_letter.char == "م":
            self.set_mapping(mapping_type=MappingType.MANY_TO_ONE, rule="idgham_shafawi")
            next_letter.set_mapping(mapping_type=MappingType.MANY_TO_ONE, rule="idgham_shafawi")
            next_letter.mark_phonemized(next_letter.phonemize_modifiers(), affected_by=self)
            return [get_rule_phoneme("idgham", "nasalized_map").get("m")]
        
        # Izhar Shafawi
        return [self.base_phoneme]
