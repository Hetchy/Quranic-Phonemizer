"""
Symbol parser for the Quranic phonemizer - Phase 2 implementation.
"""

from __future__ import annotations

from typing import List, Dict, Any
import unicodedata

from .symbols import Symbol, LetterSymbol, DiacriticSymbol, ExtensionSymbol, StopSymbol, OtherSymbol
from .location import Location


class SymbolParser:
    """Parses text into properly associated symbols for Quranic phonemization."""
    
    def __init__(self, symbol_mappings: Dict[str, Any]):
        self.symbol_mappings = symbol_mappings
        self._build_lookup_tables()
    
    def _build_lookup_tables(self) -> None:
        """Build lookup tables for efficient symbol identification."""
        self.letter_map = {}
        for letter_type, letter_info in self.symbol_mappings.get("letters", {}).items():
            self.letter_map[letter_info["char"]] = (letter_type, letter_info)
        
        self.diacritic_map = {}
        for diacritic_type, diacritic_info in self.symbol_mappings.get("diacritics", {}).items():
            self.diacritic_map[diacritic_info["char"]] = (diacritic_type, diacritic_info)
        
        self.extension_map = {}
        for extension_type, extension_info in self.symbol_mappings.get("extensions", {}).items():
            self.extension_map[extension_info["char"]] = (extension_type, extension_info)
        
        self.stop_sign_map = {}
        for stop_type, stop_info in self.symbol_mappings.get("stop_signs", {}).items():
            self.stop_sign_map[stop_info["char"]] = (stop_type, stop_info)
        
        self.other_map = {}
        for other_type, other_info in self.symbol_mappings.get("other", {}).items():
            self.other_map[other_info["char"]] = (other_type, other_info)
    
    def parse_word(self, text: str, location: Location) -> 'ParsedWord':
        """Parse a word text into a ParsedWord object with properly associated symbols."""
        word = ParsedWord(location=location, text=text)
        
        # Strip rule tags for character processing
        stripped_text = self._strip_rule_tags(text)
        
        # Parse symbols with proper association
        i = 0
        while i < len(stripped_text):
            char = stripped_text[i]
            
            # Skip whitespace
            if char.isspace():
                i += 1
                continue
            
            # Check if it's a stop sign
            if char in self.stop_sign_map:
                stop_type, stop_info = self.stop_sign_map[char]
                symbol = StopSymbol(char, stop_info.get("phoneme", ""), stop_type)
                word.symbols.append(symbol)
                word.stop_sign = symbol
                i += 1
                continue
            
            # Check if it's a letter
            if char in self.letter_map:
                letter_type, letter_info = self.letter_map[char]
                symbol = LetterSymbol(char, letter_info.get("phoneme"))
                word.symbols.append(symbol)
                i += 1
                continue
            
            # Check if it's a diacritic
            if char in self.diacritic_map:
                diacritic_type, diacritic_info = self.diacritic_map[char]
                symbol = DiacriticSymbol(char, diacritic_info.get("phoneme"), diacritic_type)
                # Associate with the previous letter if it exists
                if word.symbols and isinstance(word.symbols[-1], LetterSymbol):
                    letter = word.symbols[-1]
                    letter.add_diacritic(symbol)
                else:
                    # Diacritic without a letter - add as standalone symbol
                    word.symbols.append(symbol)
                i += 1
                continue
            
            # Check if it's an extension symbol
            if char in self.extension_map:
                extension_type, extension_info = self.extension_map[char]
                symbol = ExtensionSymbol(char, extension_info.get("phoneme"), extension_type)
                # Associate with the previous letter if it exists
                if word.symbols and isinstance(word.symbols[-1], LetterSymbol):
                    letter = word.symbols[-1]
                    letter.extension = symbol
                else:
                    # Extension without a letter - add as standalone symbol
                    word.symbols.append(symbol)
                i += 1
                continue
            
            # Check if it's a shaddah (special handling)
            if char in self.other_map and self.other_map[char][0] == "SHADDA":
                other_type, other_info = self.other_map[char]
                symbol = OtherSymbol(char, other_info.get("phoneme"))
                symbol.type = other_type
                # Associate shaddah with the previous letter
                if word.symbols and isinstance(word.symbols[-1], LetterSymbol):
                    letter = word.symbols[-1]
                    letter.has_shaddah = True
                else:
                    # Shaddah without a letter - add as standalone symbol
                    word.symbols.append(symbol)
                i += 1
                continue
            
            # Check if it's another "other" symbol
            if char in self.other_map:
                other_type, other_info = self.other_map[char]
                symbol = OtherSymbol(char, other_info.get("phoneme"))
                symbol.type = other_type
                word.symbols.append(symbol)
                i += 1
                continue
            
            # If we get here, it's an unknown symbol
            symbol = OtherSymbol(char)
            word.symbols.append(symbol)
            i += 1
        
        return word
    
    def _strip_rule_tags(self, text: str) -> str:
        """Remove rule tags from text for character processing."""
        import re
        stripped_text = re.sub(r"<rule class=[^>]+>", "", text)
        stripped_text = re.sub(r"</rule>", "", stripped_text)
        return stripped_text


class ParsedWord:
    """Represents a word with properly parsed and associated symbols."""
    
    def __init__(self, location: Location, text: str):
        self.location = location
        self.text = text
        self.symbols: List[Symbol] = []
        self.stop_sign: StopSymbol = None
    
    def debug_print(self) -> str:
        """Pretty print the word structure for debugging purposes."""
        result = f"Word at {self.location.location_key}:\n"
        result += f"  Text: {self.text}\n"
        if self.stop_sign:
            result += f"  Stop Sign: {self.stop_sign.char} (type: {self.stop_sign.type})\n"
        else:
            result += "  Stop Sign: None\n"
        
        result += "  Symbols:\n"
        for i, symbol in enumerate(self.symbols):
            symbol_type = symbol.__class__.__name__
            result += f"    {i}: {symbol_type} '{symbol.char}'"
            if symbol.phoneme:
                result += f" -> {symbol.phoneme}"
            if hasattr(symbol, 'type') and symbol.type:
                result += f" (type: {symbol.type})"
            
            # For letters, show associated diacritics and extensions
            if isinstance(symbol, LetterSymbol):
                if symbol.diacritics:
                    for diacritic in symbol.diacritics:
                        result += f" + diacritic '{diacritic.char}' -> {diacritic.phoneme}"
                        if diacritic.type:
                            result += f" (type: {diacritic.type})"
                if symbol.extension:
                    result += f" + extension '{symbol.extension.char}' -> {symbol.extension.phoneme}"
                    if symbol.extension.type:
                        result += f" (type: {symbol.extension.type})"
                if symbol.has_shaddah:
                    result += " + shaddah"
            result += "\n"
        
        return result
