"""
SequentialWordProcessor class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

from .word import Word
from .symbols.letters.letter import LetterSymbol


class WordProcessor:
    """Orchestrates the conversion of a Word to its phonemes."""
    def __init__(self):
        pass
    
    def process_word(self, word: Word) -> List[str]:
        """Process a single word."""
        for i, letter in enumerate(word.letters):
            if letter.can_phonemize:
                self.process_letter(letter, word, i)
        
        return self.collect_phonemes(word)
    
    def process_letter(self, letter: LetterSymbol, word: Word, index: int) -> None:
        phonemes = letter.phonemize()
        letter.mark_phonemized(phonemes)
    
    def collect_phonemes(self, word: Word) -> List[str]:
        """Collect all phonemes from letters in the word."""
        phonemes = []
        for letter in word.letters:
            phonemes.extend([p for p in letter.phonemes if p])
        return phonemes
