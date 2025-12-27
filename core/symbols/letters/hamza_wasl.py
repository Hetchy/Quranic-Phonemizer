from typing import List
from .letter import LetterSymbol
from core.mapping import MappingType


class HamzaWasl(LetterSymbol):
    def phonemize_letter(self) -> List[str]:
        if self.is_first and self.parent_word.is_starting:
            second_letter = self.next_letter(1)
            third_letter = self.next_letter(2)
            
            if second_letter and second_letter.char == "ل":
                self.set_mapping(rule="hamza_wasl_fatha")
                return [self.base_phoneme, "a"]
            
            if third_letter and third_letter.diacritic:
                if third_letter.has_damma:
                    self.set_mapping(rule="hamza_wasl_damma")
                    return [self.base_phoneme, "u"]
                if third_letter.has_fatha or third_letter.has_kasra:
                    self.set_mapping(rule="hamza_wasl_kasra")
                    return [self.base_phoneme, "i"]
            
        if self.is_first:  # Iltiqaa Sakinayn
            prev_letter = self.prev_letter(1)
            if not prev_letter:
                self.set_mapping(mapping_type=MappingType.SILENT, rule="hamza_wasl_silent")
                return []

            if not prev_letter.phonemes:
                prev_letter = self.prev_letter(2)
                
            # Case 1: tanween
            if prev_letter.has_tanween:
                prev_letter.phonemes.append("i")
                self.set_mapping(mapping_type=MappingType.SILENT, rule="iltiqaa_tanween")

            # Case 2: Long vowel demotion to short
            prev_phoneme = self.prev_phoneme()
            if prev_phoneme in ["a:", "aˤ:", "u:", "i:"]:
                self.modify_prev_phoneme(prev_phoneme[:-1])
                self.set_mapping(mapping_type=MappingType.SILENT, rule="iltiqaa_vowel")

        self.set_mapping(mapping_type=MappingType.SILENT, rule="hamza_wasl_silent")
        return []
