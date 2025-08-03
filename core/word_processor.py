"""
WordProcessor class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .rule import Rule
    from .word import Word


class WordProcessor:
    """Orchestrates the conversion of a Word to its phonemes."""
    def __init__(self, rules: List[Rule] = None):
        self.rules = rules or []
    
    def process_word(self, word: Word) -> List[str]:
        """Process a single word and return its phonemes."""
        # Start with the basic phonemes from symbols
        phonemes = []
        for symbol in word.symbols:
            if symbol.phoneme:
                phonemes.append(symbol.phoneme)
        
        # Apply rules
        context = {"word": word}
        for rule in self.rules:
            phonemes = rule.apply(phonemes, context)
        
        return phonemes
