from typing import List
from .letter import LetterSymbol
from core.mapping import MappingType


class HamzaWasl(LetterSymbol):
    # Special nouns that get kasra when starting
    HAMZA_WASL_NOUN_PATTERNS = [
        ['ٱ', 'س', 'م'],            # ٱسم
        ['ٱ', 'ب', 'ن'],            # ٱبن
        ['ٱ', 'م', 'ر', 'أ', 'ة'],  # ٱمرأة
        ['ٱ', 'ث', 'ن', 'ا', 'ن'],  # ٱثنان
    ]

    # Special imperative verbs that get kasra when starting
    HAMZA_WASL_VERB_PATTERNS = [
        ['ٱ', 'ب', 'ن', 'و'],  # ٱبنو
        ['ٱ', 'ق', 'ض', 'و'],  # ٱقضو
        ['ٱ', 'ئ', 'ت', 'و'],  # ٱئتو
        ['ٱ', 'م', 'ش', 'و'],  # ٱمشو
    ]

    def phonemize_letter(self) -> List[str]:
        if self.is_first and self.parent_word.is_starting:
            # Check special words first (both sets get kasra)
            if self._is_special_noun() or self._is_special_verb():
                self.set_mapping(rule="hamza_wasl_kasra")
                return [self.base_phoneme, "i"]

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

    def _is_special_noun(self) -> bool:
        """Check if word matches a special noun pattern."""
        return self._matches_any_pattern(self.HAMZA_WASL_NOUN_PATTERNS)

    def _is_special_verb(self) -> bool:
        """Check if word matches a special verb pattern."""
        return self._matches_any_pattern(self.HAMZA_WASL_VERB_PATTERNS)

    def _matches_any_pattern(self, patterns: List[List[str]]) -> bool:
        """Check if word starts with any of the given letter patterns."""
        word_letters = [letter.char for letter in self.parent_word.letters]
        for pattern in patterns:
            if self._starts_with_pattern(word_letters, pattern):
                return True
        return False

    def _starts_with_pattern(self, word_letters: List[str], pattern: List[str]) -> bool:
        """Check if word letters start with the given pattern."""
        if len(word_letters) < len(pattern):
            return False
        for i, pattern_letter in enumerate(pattern):
            if word_letters[i] != pattern_letter:
                return False
        return True
