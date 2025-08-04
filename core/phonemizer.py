"""
core/phonemizer.py
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
from .location import Location
from core.symbols.symbol import Symbol
from core.symbols.letter import LetterSymbol
from core.symbols.diacritic import DiacriticSymbol
from core.symbols.extension import ExtensionSymbol
from core.symbols.other import OtherSymbol
from core.symbols.stop import StopSymbol
from core.symbols.letters.noon import NoonLetter
from core.symbols.letters.meem import MeemLetter
from core.symbols.letters.hamza_wasl import HamzaWaslLetter
from core.parser import Parser, ParsedWord
from core.word import Word
from core.word_processor import WordProcessor
from .word_processor import WordProcessor
from .phonemize_result import PhonemizeResult

# Data directory
DATA_DIR = Path(__file__).resolve().parent.parent / "resources"


def load_symbol_mappings(map_path: str | Path = DATA_DIR / "base_phonemes.yaml") -> Dict[str, Any]:
    """Load symbol mappings from YAML file."""
    with Path(map_path).expanduser().open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def parse_word(text: str, location: Location, symbol_mappings: Dict[str, Any]) -> Word:
    """Parse a word text into a Word object with letters and their associated symbols."""
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
    
    # Parse letters with their associated symbols
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
            stop_symbol = StopSymbol(char, stop_info.get("phoneme", ""), stop_info["type"])
            word.stop_sign = stop_symbol
            i += 1
            continue
        
        # Check if it's a letter
        if char in letter_map:
            letter_type, letter_info = letter_map[char]
            # Create complex letter instances for special cases
            if char == "ن":  # NOON
                letter = NoonLetter(char, letter_info.get("phoneme"))
            elif char == "م":  # MEEM
                letter = MeemLetter(char, letter_info.get("phoneme"))
            elif char == "ٱ":  # HAMZA_WASL
                letter = HamzaWaslLetter(char, letter_info.get("phoneme"))
            else:
                letter = LetterSymbol(char, letter_info.get("phoneme"))
            
            # Look ahead for associated diacritics, extensions, and shaddah
            j = i + 1
            while j < len(stripped_text):
                next_char = stripped_text[j]
                
                # Check for diacritics (only the 7 defined ones)
                if next_char in diacritic_map:
                    diacritic_type, diacritic_info = diacritic_map[next_char]
                    diacritic = DiacriticSymbol(next_char, diacritic_info.get("phoneme"), diacritic_type)
                    letter.add_diacritic(diacritic)
                    j += 1
                
                # Check for extensions
                elif next_char in extension_map:
                    extension_type, extension_info = extension_map[next_char]
                    extension = ExtensionSymbol(next_char, extension_info.get("phoneme"), extension_type)
                    letter.extension = extension
                    j += 1
                
                # Check for shaddah (special handling)
                elif next_char in other_map and other_map[next_char]["type"] == "SHADDA":
                    letter.has_shaddah = True
                    j += 1
                
                # Check for other symbols
                elif next_char in other_map:
                    other_info = other_map[next_char]
                    other = OtherSymbol(next_char, other_info.get("phoneme"))
                    other.type = other_info["type"]
                    letter.other_symbols.append(other)
                    j += 1
                
                # If next char is a letter, stop looking ahead
                elif next_char in letter_map:
                    break
                
                # Unknown character
                else:
                    other = OtherSymbol(next_char)
                    letter.other_symbols.append(other)
                    j += 1
            
            # Link contextual references for option-2 design
            letter.parent_word = word
            letter.index_in_word = len(word.letters)
            word.letters.append(letter)
            i = j
            continue
    
    return word


def link_words(words: List[Word]) -> None:
    """Link words with references to previous and next words."""
    for i, word in enumerate(words):
        if i > 0:
            word.previous_word = words[i - 1]
        if i < len(words) - 1:
            word.next_word = words[i + 1]


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
    
    # Link words for sequential phonemization
    link_words(words)
    
    return words


class Phonemizer:
    """Main phonemizer class for the refactored implementation."""
    def __init__(
        self,
        db_path: str | Path = DATA_DIR / "Quran.json",
        map_path: str | Path = DATA_DIR / "base_phonemes.yaml",
    ) -> None:
        self.db_path = str(db_path)
        self.map_path = str(map_path)
        # For phonemization approach
        self.word_processor = WordProcessor()
        
    def load_words(self, ref: str) -> List[Word]:
        """Load words for a reference range."""
        return load_words(ref, self.db_path, self.map_path)
    
    def phonemize(
        self,
        ref: str,
        *,
        stops: List[str] = [],
    ) -> PhonemizeResult:
        """
        Phonemize a reference range.
        
        Parameters
        ----------
        ref : str
            Qurʾānic reference.
        stops : List[str], default []
            List of stop types to mark as boundaries.
            
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
