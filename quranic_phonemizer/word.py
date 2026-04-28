"""
Word class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .symbols.letters.letter import LetterSymbol
from .location import Location
from .symbols.stop import StopSymbol
from .tajweed_rule import TajweedRule, TajweedRuleTag


class Word:
    __slots__ = (
        "location", "text", "prev_word", "next_word", "letters",
        "phonemes", "stop_sign", "is_starting", "is_stopping",
        "_letter_overrides",
    )

    def __init__(self, location: Location, text: str = ""):
        self.location = location
        self.text = text
        self.prev_word: Optional[Word] = None
        self.next_word: Optional[Word] = None
        self.letters: List[LetterSymbol] = []
        self.phonemes: Optional[List[str]] = None
        self.stop_sign: Optional[StopSymbol] = None
        self.is_starting: bool = False
        self.is_stopping: bool = False
        self._letter_overrides: Optional[List[Dict[str, Any]]] = None

    def get_prev_letter(self, index: int, n: int = 1) -> Optional[LetterSymbol]:
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
        target_index = index + n
        if target_index < len(self.letters):
            return self.letters[target_index]
        elif self.next_word:
            overflow = target_index - len(self.letters)
            if overflow < len(self.next_word.letters):
                return self.next_word.letters[overflow]
        return None
    
    def phonemize(self) -> None:
        if self.phonemes:
            return
        for letter in self.letters:
            if not letter.is_phonemized:
                letter.phonemize()

    def apply_phoneme_overrides(self) -> None:
        """Apply letter-level phoneme and tajweed overrides after phonemization."""
        if not self._letter_overrides:
            return
        for override in self._letter_overrides:
            context = override.get('context', 'always')
            if context == 'stopping' and not self.is_stopping:
                continue
            if context == 'starting' and not self.is_starting:
                continue
            target = override['target_char']
            for letter in self.letters:
                if letter.char == target:
                    if 'override_phonemes' in override:
                        letter.phonemes = list(override['override_phonemes'])
                    if 'override_tajweed' in override:
                        letter._tajweed_rules = [
                            TajweedRuleTag(rule=TajweedRule(r), is_source=True)
                            for r in override['override_tajweed']
                        ]
                    break

    def get_phonemes(self) -> List[str]:
        if self.phonemes:
            return self.phonemes
        phonemes = []
        extend = phonemes.extend
        for letter in self.letters:
            extend(filter(None, letter.phonemes))
        return phonemes

    def debug_print(self) -> str:
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
            
            if letter.phonemes:
                result += f"      Phonemes: {letter.phonemes}\n"
            if letter.diacritic:
                result += f"      Diacritic: '{letter.diacritic.char}' -> {letter.diacritic.base_phoneme} (name: {letter.diacritic.name})\n"
            if letter.extensions:
                for ext in letter.extensions:
                    result += f"      Extension: '{ext.char}' -> {ext.base_phoneme} (name: {ext.name})\n"
            if letter.has_shaddah:
                result += "      Shaddah\n"
            if letter.other_symbols:
                result += "      Other symbols:\n"
                for j, other in enumerate(letter.other_symbols):
                    result += f"        {j}: '{other.char}' -> {other.base_phoneme} (name: {other.name})\n"
            if letter._tajweed_rules:
                result += f"      Tajweed Rules: {letter._tajweed_rules}\n"
        
        return result
