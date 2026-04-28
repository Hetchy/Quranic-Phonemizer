from typing import List
from ...phoneme_registry import get_rule_phoneme
from ...tajweed_rule import TajweedRule
from .letter import LetterSymbol
from ..extension import ExtensionSymbol


class Lam(LetterSymbol):
    __slots__ = ()

    ALLAH_LETTER_PATTERNS = {
        'ءَآللَّهُ': ['ء', 'ا', 'ل', 'ل', 'ه'],
        'وَٱللَّهُ': ['و', 'ٱ', 'ل', 'ل', 'ه'],
        'فَٱللَّهُ': ['ف', 'ٱ', 'ل', 'ل', 'ه'],
        'تَٱللَّهِ': ['ت', 'ٱ', 'ل', 'ل', 'ه'],
        'وَتَٱللَّهِ': ['و', 'ت', 'ٱ', 'ل', 'ل', 'ه'],
        'لِلَّهِ': ['ل', 'ل', 'ه'],
        'وَلِلَّهِ': ['و', 'ل', 'ل', 'ه'],
        'فَلِلَّهِ': ['ف', 'ل', 'ل', 'ه'],
        'بِٱللَّهِ': ['ب', 'ٱ', 'ل', 'ل', 'ه'],
        'أَبِٱللَّهِ': ['أ', 'ب', 'ٱ', 'ل', 'ل', 'ه'],
        'ٱللَّهُمَّ': ['ٱ', 'ل', 'ل', 'ه', 'م'],
        'ٱللَّهَ': ['ٱ', 'ل', 'ل', 'ه'],
    }

    # Bucket patterns by length so _word_contains_Allah can early-exit on
    # word length mismatch without iterating every pattern.
    _PATTERNS_BY_LEN: dict = {}

    def phonemize_letter(self) -> List[str]:
        if self._word_contains_Allah():
            self.add_extension(ExtensionSymbol("DAGGER_ALEF", "", None))
            if self.is_heavy:
                self.set_tajweed_rule(TajweedRule.TAFKHEEM)
                return [get_rule_phoneme("lam_heavy", "phoneme")]
        return super().phonemize_letter()

    @property
    def is_heavy(self) -> bool:
        # a: is for ءَآللَّهُ
        return self._word_contains_Allah() and self.prev_phoneme() in ("a", "aˤ", "a:", "u")

    def _word_contains_Allah(self) -> bool:
        if not self.has_shaddah or self.is_first:
            return False
        letters = self.parent_word.letters
        candidates = Lam._PATTERNS_BY_LEN.get(len(letters))
        if not candidates:
            return False
        word_letters = [letter.char for letter in letters]
        for pattern in candidates:
            if word_letters == pattern:
                return True
        return False


# Populate length-bucketed patterns once at import time.
for _pattern in Lam.ALLAH_LETTER_PATTERNS.values():
    Lam._PATTERNS_BY_LEN.setdefault(len(_pattern), []).append(_pattern)
