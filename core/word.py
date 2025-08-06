"""
Word class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import List, Optional, Dict

from .symbols.letters.letter import LetterSymbol
from .location import Location
from .symbols.stop import StopSymbol

class Word:
    def __init__(self, location: Location, text: str = ""):
        self.location = location
        self.text = text
        self.prev_word: Optional[Word] = None
        self.next_word: Optional[Word] = None
        self.letters: List[LetterSymbol] = []
        self.phonemes: Optional[List[str]] = None
        self.stop_sign: Optional[StopSymbol] = None
        self.is_starting: bool = False  # True if this word is the start after a pause
        self.is_stopping: bool = False  # True if this word is paused at

    def get_prev_letter(self, index: int, n: int = 1) -> Optional[LetterSymbol]:
        """Get the previous letter in the current word or last letter of previous word."""
        target_index = index - n
        if target_index >= 0:
            return self.letters[target_index]
        elif self.prev_word and self.prev_word.letters:
            underflow = abs(target_index)
            prev_letters_count = len(self.prev_word.letters)
            if underflow <= prev_letters_count:
                return self.prev_word.letters[prev_letters_count - underflow]
        return None
        
    def get_next_letter(self, index: int, n: int = 1) -> Optional[LetterSymbol]:
        """Get the next letter in the current or next word."""
        target_index = index + n
        if target_index < len(self.letters):
            return self.letters[target_index]
        elif self.next_word:
            overflow = target_index - len(self.letters)
            if overflow < len(self.next_word.letters):
                return self.next_word.letters[overflow]
        return None
    
    def phonemize(self) -> None:
        """Phonemize the word by processing all letters and collecting their phonemes."""
        if self.phonemes: # special case for words that are phonemized already
            return
        
        for i, letter in enumerate(self.letters):
            if letter.can_phonemize():
                letter.phonemize()

    def get_phonemes(self) -> List[str]:
        if self.phonemes:
            return self.phonemes
        
        phonemes = []
        for letter in self.letters:
            phonemes.extend(ph for ph in letter.phonemes if ph)
        
        return phonemes

    def debug_print(self) -> str:
        """Pretty print for debugging purposes."""
        result = f"Word at {self.location.location_key}:\n"
        result += f"  Text: {self.text}\n"
        if self.stop_sign:
            result += f"  Stop Sign: {self.stop_sign.char} (name: {self.stop_sign.name})\n"
        else:
            result += "  Stop Sign: None\n"
        
        result += "  is_starting: " + str(self.is_starting) + "\n"
        result += "  is_stopping: " + str(self.is_stopping) + "\n"
        
        result += "  Letters:\n"
        for i, letter in enumerate(self.letters):
            result += f"    {i}: Letter '{letter.char}' -> {letter.base_phoneme}\n"
            
            # Show sequential phonemization attributes
            if letter.phonemes:
                result += f"      Phonemes: {letter.phonemes}\n"
            if letter.affected_by:
                result += f"      Affected By: '{letter.affected_by.char}'\n"
            
            # Show diacritic
            if letter.diacritic:
                result += f"      Diacritic: '{letter.diacritic.char}' -> {letter.diacritic.base_phoneme} (name: {letter.diacritic.name})\n"
            
            # Show extension
            if letter.extension:
                result += f"      Extension: '{letter.extension.char}' -> {letter.extension.base_phoneme} (name: {letter.extension.name})\n"
            
            # Show shaddah
            if letter.has_shaddah:
                result += "      Shaddah\n"
            
            # Show other symbols
            if letter.other_symbols:
                result += "      Other symbols:\n"
                for j, other in enumerate(letter.other_symbols):
                    result += f"        {j}: '{other.char}' -> {other.base_phoneme} (name: {other.name})\n"
        
        return result
