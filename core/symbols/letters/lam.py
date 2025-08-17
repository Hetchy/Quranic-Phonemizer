from typing import List
from core.phoneme_registry import get_rule_phoneme
from .letter import LetterSymbol
from core.symbols.extension import ExtensionSymbol

class Lam(LetterSymbol):
    ALLAH_LETTER_PATTERNS = {
        # always heavy
        'ءَآللَّهُ': ['ء', 'ا', 'ل', 'ل', 'ه'],
        'وَٱللَّهُ': ['و', 'ٱ', 'ل', 'ل', 'ه'],
        'فَٱللَّهُ': ['ف', 'ٱ', 'ل', 'ل', 'ه'],
        'تَٱللَّهِ': ['ت', 'ٱ', 'ل', 'ل', 'ه'],
        'وَتَٱللَّهِ': ['و', 'ت', 'ٱ', 'ل', 'ل', 'ه'],
        
        # always light
        'لِلَّهِ': ['ل', 'ل', 'ه'],
        'وَلِلَّهِ': ['و', 'ل', 'ل', 'ه'],
        'فَلِلَّهِ': ['ف', 'ل', 'ل', 'ه'],
        'بِٱللَّهِ': ['ب', 'ٱ', 'ل', 'ل', 'ه'],
        'أَبِٱللَّهِ': ['أ', 'ب', 'ٱ', 'ل', 'ل', 'ه'],

        # heavy or light
        'ٱللَّهُمَّ': ['ٱ', 'ل', 'ل', 'ه', 'م'],
        'ٱللَّهَ': ['ٱ', 'ل', 'ل', 'ه'],
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def phonemize_letter(self) -> List[str]:        
        if self._word_contains_Allah():
            self.extension = ExtensionSymbol("DAGGER_ALEF", "", None)
            if self.is_heavy:
                return [get_rule_phoneme("lam_heavy", "phoneme")]

        return super().phonemize_letter()

    @property
    def is_heavy(self) -> bool:
        return self._word_contains_Allah() and self.prev_phoneme() in ["a", "a:", "u"]
    
    def _word_contains_Allah(self) -> bool:
        if not self.has_shaddah or self.is_first:
            return False

        word_letters = [letter.char for letter in self.parent_word.letters]
        for pattern_letters in self.ALLAH_LETTER_PATTERNS.values():
            if self._letters_match(word_letters, pattern_letters):
                return True
        
        return False

    def _letters_match(self, word_letters: List[str], pattern_letters: List[str]) -> bool:
        if len(word_letters) != len(pattern_letters):
            return False
            
        for word_letter, pattern_letter in zip(word_letters, pattern_letters):
            if word_letter != pattern_letter:
                return False
                
        return True