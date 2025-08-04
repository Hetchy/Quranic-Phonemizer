#!/usr/bin/env python3
"""
MEEM letter class with specific phonemization rules.
"""

from typing import List, Dict, Any, Optional
from ..letter import LetterSymbol


class MeemLetter(LetterSymbol):
    """MEEM letter with specific phonemization rules."""
    
    def phonemize(self) -> List[str]:
        """Phonemize MEEM based on Tajweed rules."""
        phonemes = []
        
        # Use neighbour helpers
        next_letter = self.next_letter()
        
        # Ghunnah (nasalization) when MEEM has shaddah
        if self.has_shaddah:
            # Use nasalized version of meem
            phonemes.append("m̃")  # Using the nasalized phoneme from rule config
            return phonemes
        
        # Check for Ikhfaa Shafawi rule
        if not self.diacritic and next_letter and next_letter.char == "ب":
            # Ikhfaa Shafawi when followed by baa
            phonemes.append("ɱ")  # Using the shafawi phoneme from rule config
            # Mark next letter as affected (will not be phonemized)
            next_letter.mark_phonemized([], affected_by=self)
            return phonemes
        
        # Check for Idgham Shafawi rule
        if not self.diacritic and next_letter and next_letter.char == "م":
            # Idgham Shafawi when followed by another meem
            phonemes.append("m̃")  # Nasalized meem
            # Mark next letter as affected (will not be phonemized)
            next_letter.mark_phonemized([], affected_by=self)
            return phonemes
        
        # Normal phonemization if none of the special rules apply
        if self.phoneme:
            phonemes.append(self.phoneme)
            
        # Add diacritic phoneme if present
        if self.diacritic and self.diacritic.phoneme:
            phonemes.append(self.diacritic.phoneme)
        
        # Add extension phoneme if present
        if self.extension and self.extension.phoneme:
            phonemes.append(self.extension.phoneme)
        
        # Add other symbols phonemes
        for other in self.other_symbols:
            if other.phoneme:
                phonemes.append(other.phoneme)
        
        return phonemes
