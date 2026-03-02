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

        # One-off fix: 41:44:10 waw should be nasalized after special word 41:44:9
        if (self.location.location_key == "41:44:10" and
            self.prev_word and
            self.prev_word.phonemes and  # prev word is a special word
            self.letters and self.letters[0].phonemes):
            # Replace 'w' with nasalized 'w̃' for idgham ghunnah
            if self.letters[0].phonemes[0] == "w":
                self.letters[0].phonemes[0] = "w̃"
                self.letters[0].set_mapping(rule="idgham_ghunnah_tanween")

    def get_phonemes(self) -> List[str]:
        if self.phonemes:
            return self.phonemes
        phonemes = []
        for letter in self.letters:
            phonemes.extend(ph for ph in letter.phonemes if ph)
        return phonemes

    def build_mapping(self) -> WordMapping:
        from .mapping import ExtensionSymbolMapping, OtherSymbolMapping

        letter_mappings = []
        leading_symbols = []
        trailing_symbols = []

        # Quranic symbol characters (stop signs, rub el hizb, etc.)
        QURANIC_SYMBOLS = {
            '\u06D6': 'PREFERRED_CONTINUE',
            '\u06D7': 'PREFERRED_STOP',
            '\u06D8': 'COMPULSORY_STOP',
            '\u06D9': 'PROHIBITED_STOP',
            '\u06DA': 'OPTIONAL_STOP',
            '\u06DB': 'EITHER_STOP',
            '\u06DC': 'SMALL_HIGH_SEEN',
            '\u06DD': 'END_OF_AYAH',
            '\u06DE': 'START_OF_RUB_EL_HIZB',
            '\u06DF': 'SMALL_HIGH_ROUNDED_ZERO',
            '\u06E0': 'SMALL_HIGH_UPRIGHT_RECT',
            '\u06E9': 'PLACE_OF_SAJDAH',
        }

        # Diacritics to skip
        DIACRITICS = '\u064E\u064F\u0650\u0652\u064B\u064C\u064D\u0651'

        # Extract leading symbols from text (symbols that appear before first letter)
        if self.text and self.letters:
            first_letter_char = self.letters[0].char
            text_before_first_letter = self.text.split(first_letter_char)[0]

            # Check for Quranic symbols in the leading text
            for char in text_before_first_letter:
                # Skip whitespace and diacritics
                if char in f' {DIACRITICS}':
                    continue

                # Check if this is a known Quranic symbol
                if char in QURANIC_SYMBOLS:
                    leading_symbols.append(
                        OtherSymbolMapping(char=char, name=QURANIC_SYMBOLS[char])
                    )

        for i, letter in enumerate(self.letters):
            phonemes = list(letter.phonemes) if letter.phonemes else []

            # Build extension mappings if present
            extension_mappings = []
            for ext in letter.extensions:
                extension_mappings.append(ExtensionSymbolMapping(
                    char=ext.char,
                    name=ext.name
                ))

            # Build other symbols mappings
            other_symbols_mappings = []
            if letter.other_symbols:
                for sym in letter.other_symbols:
                    other_symbols_mappings.append(
                        OtherSymbolMapping(char=sym.char, name=sym.name)
                    )

            # Get letter_rules - special words set letter_rules directly, regular use rules property
            # Note: getattr returns None if not set, but special words set [] for empty rules
            letter_rules_attr = getattr(letter, 'letter_rules', None)
            rules = letter_rules_attr if letter_rules_attr is not None else letter.rules

            lm = LetterMapping(
                index=i,
                char=letter.char,
                phonemes=phonemes,
                diacritic=letter.diacritic.name if letter.diacritic else None,
                has_shaddah=letter.has_shaddah,
                extensions=extension_mappings,
                other_symbols=other_symbols_mappings,
                mapping_type=letter.mapping_type,
                letter_rules=rules,
                phoneme_rules=[[] for _ in phonemes],
            )
            letter_mappings.append(lm)

        # Extract word-level trailing symbols (stop signs)
        if self.stop_sign:
            trailing_symbols.append(
                OtherSymbolMapping(char=self.stop_sign.char, name=self.stop_sign.name)
            )

        clean_text = re.sub(r"</?rule[^>]*?>", "", self.text)

        return WordMapping(
            location=self.location.location_key,
            text=clean_text,
            phonemes=self.get_phonemes(),
            letter_mappings=letter_mappings,
            leading_symbols=leading_symbols,
            trailing_symbols=trailing_symbols,
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
            if letter.extensions:
                for ext in letter.extensions:
                    result += f"      Extension: '{ext.char}' -> {ext.base_phoneme} (name: {ext.name})\n"
            if letter.has_shaddah:
                result += "      Shaddah\n"
            if letter.other_symbols:
                result += "      Other symbols:\n"
                for j, other in enumerate(letter.other_symbols):
                    result += f"        {j}: '{other.char}' -> {other.base_phoneme} (name: {other.name})\n"
            if letter.rules:
                result += f"      Rules: {letter.rules}\n"
        
        return result
