"""
NOON letter class with specific phonemization rules.
"""

from typing import List, Dict, Any, Optional
from ..letter import LetterSymbol


class NoonLetter(LetterSymbol):
    """NOON letter with specific phonemization rules."""
    
    def phonemize(self) -> List[str]:
        """Phonemize NOON based on Tajweed rules."""
        phonemes = []
        
        # Use neighbour helpers
        next_letter = self.next_letter()
        
        # Ghunnah (nasalization) when NOON has shaddah
        if self.has_shaddah:
            # Use nasalized version of noon
            phonemes.append("ñ")  # Using the nasalized phoneme from rule config
            return phonemes
        
        # Check for Iqlab rule
        if not self.diacritic and next_letter and next_letter.char == "ب":
            # Iqlab when followed by baa
            phonemes.append("m̃")  # Using the iqlab phoneme from rule config
            # Mark next letter as affected (will not be phonemized)
            next_letter.mark_phonemized([], affected_by=self)
            return phonemes
        
        # Check for Ikhfaa rule
        # Ikhfaa letters: ت ث ج د ذ ز س ش ص ض ط ظ ف ق ك
        ikhfaa_letters = ["ت", "ث", "ج", "د", "ذ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك"]
        if not self.diacritic and next_letter and next_letter.char in ikhfaa_letters:
            # Ikhfaa - use the light or heavy phoneme based on the next letter
            phonemes.append("ŋ")  # Using the ikhfaa phoneme from rule config
            # Mark next letter as affected (will not be phonemized)
            next_letter.mark_phonemized([], affected_by=self)
            return phonemes
        
        # Check for Idgham rule
        # Idgham letters (yanmu): ي ر ز س ش ص ض ط ظ ف ق ك ل م ن ه
        idgham_letters = ["ي", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك", "ل", "م", "ن", "ه"]
        if not self.diacritic and next_letter and next_letter.char in idgham_letters:
            # Idgham without ghunnah
            # Mark next letter as affected (will not be phonemized)
            next_letter.mark_phonemized([], affected_by=self)
            return []  # Return empty list as the noon is assimilated
        
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
