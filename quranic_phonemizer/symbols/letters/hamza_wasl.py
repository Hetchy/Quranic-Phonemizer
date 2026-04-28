from typing import List
from .letter import LetterSymbol
from ...tajweed_rule import TajweedRule


class HamzaWasl(LetterSymbol):
    __slots__ = ()

    # Special nouns that get kasra when starting
    HAMZA_WASL_NOUN_PATTERNS = [
        ['ٱ', 'س', 'م'],            # ٱسم
        ['ٱ', 'ب', 'ن'],            # ٱبن, ٱبنة
        ['ٱ', 'م', 'ر'],            # ٱمرأة, ٱمرُؤٌ, ٱمرِئٍ
        ['ٱ', 'ث', 'ن', 'ا', 'ن'],  # ٱثنان
    ]

    # Special imperative verbs that get kasra when starting
    HAMZA_WASL_VERB_PATTERNS = [
        ['ٱ', 'ب', 'ن', 'و'],    # ٱبنو
        ['ٱ', 'ق', 'ض', 'و'],    # ٱقضو
        ['ٱ', 'ئ', 'ت', 'و'],    # ٱئتو
        ['ٱ', 'م', 'ش', 'و'],    # ٱمشو
        ['ٱ', 'د', 'ا', 'ر'],    # ٱدَّارَكُوا (7:38)
        ['ٱ', 'ث', 'ا', 'ق'],    # ٱثَّاقَلْتُمْ (9:38)
    ]

    def phonemize_letter(self) -> List[str]:
        if self.is_first and self.parent_word.is_starting:
            # Check special words first (both sets get kasra)
            if self._is_special_noun() or self._is_special_verb():
                self.set_tajweed_rule(TajweedRule.HAMZA_WASL_KASRA)
                return [self.base_phoneme, "i"]

            second_letter = self.next_letter(1)
            third_letter = self.next_letter(2)

            if second_letter and second_letter.char == "ل":
                self.set_tajweed_rule(TajweedRule.HAMZA_WASL_FATHA)
                return [self.base_phoneme, "a"]

            if third_letter and third_letter.diacritic:
                if third_letter.has_damma:
                    self.set_tajweed_rule(TajweedRule.HAMZA_WASL_DAMMA)
                    return [self.base_phoneme, "u"]
                if third_letter.has_fatha or third_letter.has_kasra:
                    self.set_tajweed_rule(TajweedRule.HAMZA_WASL_KASRA)
                    return [self.base_phoneme, "i"]

        if self.is_first:  # Iltiqaa Sakinayn
            prev_letter = self.prev_letter(1)
            if not prev_letter:
                self.set_tajweed_rule(TajweedRule.HAMZA_WASL_SILENT)
                return []

            if not prev_letter.phonemes:
                prev_letter = self.prev_letter(2)

            # Case 1: tanween
            # Note: tanween+vowel cases can't both fire — appended "i" isn't a long vowel
            if prev_letter.has_tanween:
                prev_letter.phonemes.append("i")
                prev_letter.set_tajweed_rule(TajweedRule.ILTIQAA_SAKINAYN_TANWEEN)

            # Case 2: Long vowel demotion to short
            prev_phoneme = self.prev_phoneme()
            if prev_phoneme in ["a:", "aˤ:", "u:", "i:"]:
                self.modify_prev_phoneme(prev_phoneme[:-1])
                prev_letter.set_tajweed_rule(TajweedRule.SILENT_ILTIQAA_SAKINAYN)

        # Fallthrough: always tag HAMZA_WASL_SILENT
        self.set_tajweed_rule(TajweedRule.HAMZA_WASL_SILENT)
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
