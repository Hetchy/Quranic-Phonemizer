#!/usr/bin/env python3
"""
HAMZA_WASL letter class with specific phonemization rules.
"""

from typing import List, Dict, Any, Optional
from ..letter import LetterSymbol


class HamzaWaslLetter(LetterSymbol):
    """HAMZA_WASL letter with specific phonemization rules."""
    
    def phonemize(self) -> List[str]:
        """Phonemize HAMZA_WASL based on Tajweed rules."""
        phonemes = []
        
        # Determine position in word
        if self.index_in_word is None or self.parent_word is None:
            return phonemes
        index = self.index_in_word
        word = self.parent_word
        
        # Check if this is the first letter of the word
        if index == 0:
            # Get the second and third letters if they exist
            second_letter = word.letters[1] if len(word.letters) > 1 else None
            third_letter = word.letters[2] if len(word.letters) > 2 else None
            
            # If second letter is lam, use hamza + fatha
            if second_letter and second_letter.char == "ل":
                phonemes.append("ʔ")  # Hamza phoneme
                phonemes.append("a")  # Fatha phoneme
                return phonemes
            
            # If third letter has damma, use hamza + damma
            if third_letter and third_letter.diacritic and third_letter.diacritic.char == "ُ":
                phonemes.append("ʔ")  # Hamza phoneme
                phonemes.append("u")  # Damma phoneme
                return phonemes
            
            # If third letter has fatha or kasra, use hamza + kasra
            if third_letter and third_letter.diacritic:
                if third_letter.diacritic.char in ["َ", "ِ"]:
                    phonemes.append("ʔ")  # Hamza phoneme
                    phonemes.append("i")  # Kasra phoneme
                    return phonemes
            
            # Otherwise use "?" to identify edge cases
            phonemes.append("?")
            return phonemes
        
        # If not the first letter of a word, it should not be phonemized
        return phonemes
