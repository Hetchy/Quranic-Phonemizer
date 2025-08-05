"""
Word class for the Quranic phonemizer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .symbols.letter import LetterSymbol
    from .location import Location

from .symbols.stop import StopSymbol


@dataclass
class Word:
    location: Location
    letters: List[LetterSymbol] = field(default_factory=list)
    text: str = ""
    stop_sign: Optional[StopSymbol] = None
    previous_word: Optional[Word] = None
    next_word: Optional[Word] = None

    is_starting: bool = False  # True if this word is the start after a pause
    is_stopping: bool = False  # True if this word is paused at 

    def get_prev_letter(self, index: int, n: int = 1) -> Optional[LetterSymbol]:
        """Get the previous letter in the current word or last letter of previous word."""
        if index > 0:
            return self.letters[index - n]
        elif self.previous_word and self.previous_word.letters:
            return self.previous_word.letters[-1]
        return None
        
    def get_next_letter(self, index: int, n: int = 1) -> Optional[LetterSymbol]:
        """Get the next letter in the current word or first letter(s) of next word."""
        if index + n < len(self.letters):
            return self.letters[index + n]
        elif self.next_word and self.next_word.letters:
            return self.next_word.letters[0]
        return None
        
    def get_letter_at(self, index: int) -> Optional[LetterSymbol]:
        """Get the letter at the specific index in the current word."""
        if 0 <= index < len(self.letters):
            return self.letters[index]
        return None

    def debug_print(self) -> str:
        """Pretty print the word structure for debugging purposes."""
        result = f"Word at {self.location.location_key}:\n"
        result += f"  Text: {self.text}\n"
        if self.stop_sign:
            result += f"  Stop Sign: {self.stop_sign.char} (type: {self.stop_sign.type})\n"
        else:
            result += "  Stop Sign: None\n"
        
        # Show word linking information
        if self.previous_word:
            result += f"  Previous Word: {self.previous_word.location.location_key}\n"
        else:
            result += "  Previous Word: None\n"
            
        if self.next_word:
            result += f"  Next Word: {self.next_word.location.location_key}\n"
        else:
            result += "  Next Word: None\n"
        
        result += "  Letters:\n"
        for i, letter in enumerate(self.letters):
            result += f"    {i}: Letter '{letter.char}' -> {letter.phoneme}\n"
            
            # Show sequential phonemization attributes
            result += f"      Is Phonemized: {letter.is_phonemized}\n"
            if letter.phonemes:
                result += f"      Phonemes: {letter.phonemes}\n"
            if letter.affected_by:
                result += f"      Affected By: '{letter.affected_by.char}'\n"
            if letter.affects:
                affected_chars = [f"'{l.char}'" for l in letter.affects]
                result += f"      Affects: {', '.join(affected_chars)}\n"
            
            # Show diacritic
            if letter.diacritic:
                result += f"      Diacritic: '{letter.diacritic.char}' -> {letter.diacritic.phoneme} (type: {letter.diacritic.type})\n"
            
            # Show extension
            if letter.extension:
                result += f"      Extension: '{letter.extension.char}' -> {letter.extension.phoneme} (type: {letter.extension.type})\n"
            
            # Show shaddah
            if letter.has_shaddah:
                result += "      Shaddah: ّ (gemination)\n"
            
            # Show other symbols
            if letter.other_symbols:
                result += "      Other symbols:\n"
                for j, other in enumerate(letter.other_symbols):
                    result += f"        {j}: '{other.char}' -> {other.phoneme}\n"
        
        return result
