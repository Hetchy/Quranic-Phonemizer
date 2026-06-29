"""
Word class for the Quranic phonemizer.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .symbols.letters.letter import LetterSymbol
from .location import Location
from .symbols.stop import StopSymbol
from .mapping import WordMapping, LetterMapping
from .tajweed_rule import TajweedRule, TajweedRuleTag


class Word:
    __slots__ = (
        "location", "text", "prev_word", "next_word", "letters",
        "phonemes", "stop_sign", "is_starting", "is_stopping",
        "_contextual_pronunciations",
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
        self._contextual_pronunciations: Optional[List[Dict[str, Any]]] = None

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

    def apply_contextual_pronunciations(self) -> None:
        """Apply context-dependent phoneme / tajweed / glyph adjustments after
        phonemization. Each entry targets the ``index``-th occurrence (1-based) of
        ``target_char`` in the word — so a repeated letter is addressable — gated by
        ``context`` (always / starting / stopping)."""
        if not self._contextual_pronunciations:
            return
        for override in self._contextual_pronunciations:
            context = override.get('context', 'always')
            if context == 'stopping' and not self.is_stopping:
                continue
            if context == 'starting' and not self.is_starting:
                continue
            target = override['target_char']
            want = override.get('index', 1)  # 1-based occurrence of target_char
            seen = 0
            for letter in self.letters:
                if letter.char != target:
                    continue
                seen += 1
                if seen != want:
                    continue
                if 'override_phonemes' in override:
                    letter.phonemes = list(override['override_phonemes'])
                if 'override_tajweed' in override:
                    letter._tajweed_rules = [
                        TajweedRuleTag(rule=TajweedRule(r), is_source=True)
                        for r in override['override_tajweed']
                    ]
                if 'override_char' in override:
                    letter.display_char = override['override_char']
                break

    def get_phonemes(self) -> List[str]:
        if self.phonemes:
            return self.phonemes
        phonemes = []
        extend = phonemes.extend
        for letter in self.letters:
            extend(filter(None, letter.phonemes))
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
            for ext in letter.extensions or ():
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

            tajweed_tags = list(letter._tajweed_rules) if letter._tajweed_rules else []

            lm = LetterMapping(
                index=i,
                char=letter.char,
                phonemes=phonemes,
                diacritic=letter.diacritic.name if letter.diacritic else None,
                has_shaddah=letter.has_shaddah,
                extensions=extension_mappings,
                other_symbols=other_symbols_mappings,
                tajweed_rules=tajweed_tags,
                display_char=letter.display_char,
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
