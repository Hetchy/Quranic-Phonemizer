"""
Word class for the Quranic phonemizer.
"""

from __future__ import annotations

import re
from typing import List, Optional

from .symbols.letters.letter import LetterSymbol
from .location import Location
from .symbols.stop import StopSymbol
from .mapping import WordMapping, LetterMapping


class Word:
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

    def build_mapping(self) -> WordMapping:
        letter_mappings = []
        for i, letter in enumerate(self.letters):
            lm = LetterMapping(
                index=i,
                char=letter.char,
                phonemes=list(letter.phonemes) if letter.phonemes else [],
                diacritic=letter.diacritic.name if letter.diacritic else None,
                has_shaddah=letter.has_shaddah,
                mapping_type=letter.mapping_type,
                rule=letter.rule,
            )
            letter_mappings.append(lm)
        
        clean_text = re.sub(r"</?rule[^>]*?>", "", self.text)
        
        return WordMapping(
            location=self.location.location_key,
            text=clean_text,
            phonemes=self.get_phonemes(),
            letter_mappings=letter_mappings,
            is_special_word=self.phonemes is not None,
            is_starting=self.is_starting,
            is_stopping=self.is_stopping,
        )

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
            if letter.affected_by:
                result += f"      Affected By: '{letter.affected_by.char}'\n"
            if letter.diacritic:
                result += f"      Diacritic: '{letter.diacritic.char}' -> {letter.diacritic.base_phoneme} (name: {letter.diacritic.name})\n"
            if letter.extension:
                result += f"      Extension: '{letter.extension.char}' -> {letter.extension.base_phoneme} (name: {letter.extension.name})\n"
            if letter.has_shaddah:
                result += "      Shaddah\n"
            if letter.other_symbols:
                result += "      Other symbols:\n"
                for j, other in enumerate(letter.other_symbols):
                    result += f"        {j}: '{other.char}' -> {other.base_phoneme} (name: {other.name})\n"
            if letter.rule:
                result += f"      Rule: {letter.rule}\n"
        
        return result
