"""
core/phonemizer_refactored.py
=============================
Refactored phonemizer implementation using word-based structures.

This is the new implementation following the refactoring plan, Phase 1.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pathlib import Path
from abc import ABC, abstractmethod
import yaml
import json
import re

from .loader import load_db, keys_for_reference
from .symbols import Symbol, LetterSymbol, DiacriticSymbol, ExtensionSymbol, StopSymbol, OtherSymbol
from .location import Location
from .word import Word
from .rule import Rule
from .word_processor import WordProcessor
from .phonemize_result import PhonemizeResult

# Data directory
DATA_DIR = Path(__file__).resolve().parent.parent / "resources"


def load_symbol_mappings(map_path: str | Path = DATA_DIR / "base_phonemes.yaml") -> Dict[str, Any]:
    """Load symbol mappings from YAML file."""
    with Path(map_path).expanduser().open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def parse_word(text: str, location: Location, symbol_mappings: Dict[str, Any]) -> Word:
    """Parse a word text into a Word object with Symbol instances."""
    word = Word(location=location, text=text)
    
    # Strip rule tags for character processing
    stripped_text = re.sub(r"<rule class=[^>]+>", "", text)
    stripped_text = re.sub(r"</rule>", "", stripped_text)
    
    # Build lookup tables for efficient symbol identification
    letter_map = {}
    for letter_type, letter_info in symbol_mappings.get("letters", {}).items():
        letter_map[letter_info["char"]] = (letter_type, letter_info)
    
    diacritic_map = {}
    for diacritic_type, diacritic_info in symbol_mappings.get("diacritics", {}).items():
        diacritic_map[diacritic_info["char"]] = (diacritic_type, diacritic_info)
    
    extension_map = {}
    for extension_type, extension_info in symbol_mappings.get("extensions", {}).items():
        extension_map[extension_info["char"]] = (extension_type, extension_info)
    
    stop_sign_map = {}
    for stop_type, stop_info in symbol_mappings.get("stop_signs", {}).items():
        stop_sign_map[stop_info["char"]] = (stop_type, stop_info)
    
    other_map = {}
    for other_type, other_info in symbol_mappings.get("other", {}).items():
        other_info["type"] = other_type  # Add type to other_info for later use
        other_map[other_info["char"]] = other_info
    
    # Parse symbols with proper association
    i = 0
    while i < len(stripped_text):
        char = stripped_text[i]
        
        # Skip whitespace
        if char.isspace():
            i += 1
            continue
        
        # Check if it's a stop sign
        if char in stop_sign_map:
            stop_info = stop_sign_map[char]
            symbol = StopSymbol(char, stop_info.get("phoneme", ""), stop_info["type"])
            word.symbols.append(symbol)
            word.stop_sign = symbol
            i += 1
            continue
        
        # Check if it's a letter
        if char in letter_map:
            letter_type, letter_info = letter_map[char]
            symbol = LetterSymbol(char, letter_info.get("phoneme"))
            
            # Look ahead for associated diacritics, extensions, and shaddah
            j = i + 1
            while j < len(stripped_text):
                next_char = stripped_text[j]
                
                # Check for diacritics
                if next_char in diacritic_map:
                    diacritic_type, diacritic_info = diacritic_map[next_char]
                    diacritic_symbol = DiacriticSymbol(next_char, diacritic_info.get("phoneme"), diacritic_type)
                    symbol.add_diacritic(diacritic_symbol)
                    j += 1
                
                # Check for extensions
                elif next_char in extension_map:
                    extension_type, extension_info = extension_map[next_char]
                    extension_symbol = ExtensionSymbol(next_char, extension_info.get("phoneme"), extension_type)
                    symbol.extension = extension_symbol
                    j += 1
                
                # Check for shaddah (special handling)
                elif next_char in other_map and other_map[next_char]["type"] == "SHADDA":
                    symbol.has_shaddah = True
                    j += 1
                
                # Check for other symbols
                elif next_char in other_map:
                    other_info = other_map[next_char]
                    other_symbol = OtherSymbol(next_char, other_info.get("phoneme"))
                    other_symbol.type = other_info["type"]
                    # Only add as diacritic if it's one of the 7 allowed diacritics
                    if next_char in diacritic_map:
                        symbol.add_diacritic(other_symbol)
                    j += 1
                
                # If next char is a letter, stop looking ahead
                elif next_char in letter_map:
                    break
                
                # Unknown character
                else:
                    other_symbol = OtherSymbol(next_char)
                    # Only add as diacritic if it's one of the 7 allowed diacritics
                    if next_char in diacritic_map:
                        symbol.add_diacritic(other_symbol)
                    j += 1
            
            word.symbols.append(symbol)
            i = j
            continue
        
        # If we get here, it's an unknown symbol that's not associated with a letter
        symbol = OtherSymbol(char)
        word.symbols.append(symbol)
        i += 1
    
    return word


def load_words(ref: str, db_path: str | Path = DATA_DIR / "Quran.json",
               map_path: str | Path = DATA_DIR / "base_phonemes.yaml") -> List[Word]:
    """Load words for a reference range."""
    db = load_db(db_path)
    symbol_mappings = load_symbol_mappings(map_path)
    locations = keys_for_reference(ref, db)
    
    words = []
    for loc in locations:
        raw = db[loc]["text"]
        if isinstance(raw, list):
            raw = "".join(raw)
        
        location_obj = Location.from_key(loc)
        word = parse_word(raw, location_obj, symbol_mappings)
        words.append(word)
    
    return words


class WordProcessor:
    """Orchestrates the conversion of a Word to its phonemes."""
    def __init__(self, rules: List[Rule] = None):
        self.rules = rules or []
    
    def process_word(self, word: Word) -> List[str]:
        """Process a single word and return its phonemes."""
        # Start with the basic phonemes from symbols
        phonemes = []
        for symbol in word.symbols:
            # Add the base letter phoneme
            if symbol.phoneme:
                phonemes.append(symbol.phoneme)
            
            # For LetterSymbols, add associated diacritic phonemes
            if isinstance(symbol, LetterSymbol):
                for diacritic in symbol.diacritics:
                    if diacritic.phoneme:
                        phonemes.append(diacritic.phoneme)
                
                # Add extension phoneme if present
                if symbol.extension and symbol.extension.phoneme:
                    phonemes.append(symbol.extension.phoneme)
        
        # Apply rules
        context = {"word": word}
        for rule in self.rules:
            phonemes = rule.apply(phonemes, context)
        
        return phonemes


# Rule class is now imported from .rule
# class Rule(ABC):
#     """Abstract base class for Tajweed rules."""
#     @abstractmethod
#     def apply(self, phonemes: List[str], context: Dict[str, Any]) -> List[str]:
#         """Apply the rule to the phonemes."""
#         pass


class PhonemizeResult:
    """Result of phonemization process."""
    def __init__(self, reference: str, text: str, phonemes: List[List[str]]):
        self.reference = reference
        self.text = text
        self.phonemes = phonemes


class Phonemizer:
    """Main phonemizer class for the refactored implementation."""
    def __init__(
        self,
        db_path: str | Path = DATA_DIR / "Quran.json",
        map_path: str | Path = DATA_DIR / "base_phonemes.yaml",
    ) -> None:
        self.db_path = str(db_path)
        self.map_path = str(map_path)
        # For phase 1, we don't implement rules yet
        self.word_processor = WordProcessor()
    
    def phonemize(
        self,
        ref: str,
        *,
        stops: List[str] = [],
        global_index: bool = False,
    ) -> PhonemizeResult:
        """
        Phonemize a reference range.
        
        Parameters
        ----------
        ref : str
            Qurʾānic reference.
        stops : List[str], default []
            List of stop types to mark as boundaries.
        global_index : bool, default False
            If True, interpret ref as a global index.
            
        Returns
        -------
        PhonemizeResult
            Object containing reference, text and phonemes.
        """
        # Load words
        words = load_words(ref, self.db_path, self.map_path)
        
        # Process each word
        all_phonemes = []
        full_text = " ".join(word.text for word in words)
        
        for word in words:
            phonemes = self.word_processor.process_word(word)
            all_phonemes.append(phonemes)
        
        return PhonemizeResult(ref, full_text, all_phonemes)
