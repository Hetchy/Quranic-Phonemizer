"""
Parser for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml
import json
import re

from .loader import load_db, keys_for_reference
from .location import Location
from .word import Word
from .symbols.letters.letter import LetterSymbol
from .symbols.diacritic import DiacriticSymbol
from .symbols.extension import ExtensionSymbol
from .symbols.stop import StopSymbol
from .symbols.other import OtherSymbol

from .symbols.letters.noon import Noon
from .symbols.letters.meem import Meem
from .symbols.letters.hamza_wasl import HamzaWasl
from .symbols.letters.qalqala_letter import Qalqala
from .symbols.letters.taa_marbuta import TaaMarbuta
from .symbols.letters.vowel import AlefMaksura
from .symbols.letters.vowel import Alef
from .symbols.letters.vowel import Waw
from .symbols.letters.vowel import Yaa
from .symbols.letters.lam import Lam
from .symbols.letters.raa import Raa

DATA_DIR = Path(__file__).resolve().parent.parent / "resources"

LETTER_CLASSES: dict[str, type[LetterSymbol]] = {
    "ٱ": HamzaWasl,
    "ل": Lam,
    "م": Meem,
    "ن": Noon,
    "ة": TaaMarbuta,
    "ر": Raa,

    "ق": Qalqala,
    "ط": Qalqala,
    "ب": Qalqala,
    "ج": Qalqala,
    "د": Qalqala,

    "ا": Alef,
    "ى": AlefMaksura,
    "و": Waw,
    "ي": Yaa,
    "ۧ":  Yaa, # mini yaa
}

def _load_special_words(yaml_path: str | Path) -> Dict[str, List[str]]:
    """
    Load special words and their phonemes from YAML file.
    
    Parameters
    ----------
    yaml_path : str | Path
        Path to the special_words.yaml file
        
    Returns
    -------
    Dict[str, List[str]]
        Dictionary mapping location keys to phoneme lists
    """
    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
    special_words_map = {}
    
    for word_entry in data['special_words']:
        text = word_entry['text']
        phonemes = word_entry['phonemes']
        locations = word_entry['locations']
        
        for location in locations:
            special_words_map[location] = phonemes
    
    return special_words_map


def _get_special_word_phonemes(location_key: str, special_words_map: Dict[str, List[str]]) -> Optional[List[str]]:
    """
    Get phonemes for a special word at a specific location.
    
    Parameters
    ----------
    location_key : str
        Location key in format "surah:verse:word"
    special_words_map : Dict[str, List[str]]
        Dictionary mapping location keys to phoneme lists
        
    Returns
    -------
    Optional[List[str]]
        Phonemes for the special word, or None if not found
    """
    return special_words_map.get(location_key)


class Parser:
    """Parses text into properly associated symbols for Quranic phonemization."""
    
    def __init__(self, symbol_mappings: Dict[str, Any], special_words_path: str | Path = DATA_DIR / "special_words.yaml"):
        self.symbol_mappings = symbol_mappings
        self.special_words_map = _load_special_words(special_words_path)
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
    
    def parse_word(self, text: str, location: Location) -> Word:
        """Parse a word text into a Word object with properly associated symbols."""
        word = Word(location=location, text=text)
        
        # Check if this is a special word and set phonemes if found
        special_phonemes = _get_special_word_phonemes(location.location_key, self.special_words_map)
        if special_phonemes:
            word.phonemes = special_phonemes
            return word
        
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
                symbol = StopSymbol(stop_type, char, stop_info.get("phoneme", ""))
                word.stop_sign = symbol
                i += 1
                continue
            
            # Check if it's a letter
            if char in self.letter_map:
                letter_type, letter_info = self.letter_map[char]
                letter_class = LETTER_CLASSES.get(char, LetterSymbol)
                letter = letter_class(letter_type, char, letter_info.get("phoneme", ""))
                
                # Look ahead for associated diacritics, extensions, and shaddah
                j = i + 1
                while j < len(stripped_text):
                    next_char = stripped_text[j]
                    
                    # Check for diacritics
                    if next_char in self.diacritic_map:
                        diacritic_type, diacritic_info = self.diacritic_map[next_char]
                        diacritic = DiacriticSymbol(diacritic_type, next_char, diacritic_info.get("phoneme"))
                        letter.diacritic = diacritic
                        j += 1
                        continue
                    
                    # Check for extensions
                    elif next_char in self.extension_map:
                        extension_type, extension_info = self.extension_map[next_char]
                        extension = ExtensionSymbol(extension_type, next_char, extension_info.get("phoneme"))
                        letter.extension = extension
                        j += 1
                        continue
                    
                    # Check for shaddah
                    elif next_char == "ّ":
                        letter.has_shaddah = True
                        j += 1
                        continue
                    
                    # Check for other symbols that should be associated with this letter
                    elif next_char in self.other_map:
                        other_type, other_info = self.other_map[next_char]
                        other = OtherSymbol(other_type, next_char, other_info.get("phoneme"))
                        letter.other_symbols.append(other)
                        j += 1
                        continue
                    
                    # If it's not an associated symbol, break the loop
                    else:
                        break
                
                # Set parent references
                letter.parent_word = word
                letter.index_in_word = len(word.letters)
                word.letters.append(letter)
                
                # Update i to j to skip processed characters
                i = j
                continue
            
            # If we get here, it's an unknown symbol - treat as other
            other = OtherSymbol("UNKNOWN", char, None)
            # Associate with the previous letter if it exists
            if word.letters:
                letter = word.letters[-1]
                letter.other_symbols.append(other)

            i += 1
        
        return word
    
    def _strip_rule_tags(self, text: str) -> str:
        """Remove rule tags from text for character processing."""
        stripped_text = re.sub(r"<rule class=[^>]+>", "", text)
        stripped_text = re.sub(r"</rule>", "", stripped_text)
        return stripped_text
    
    def load_words(self, ref: str, db_path: str | Path = DATA_DIR / "Quran.json", *, stop_types: List[str] = []) -> List[Word]:
        """Load words for a reference range and annotate boundaries."""
        db = load_db(db_path)
        locations = keys_for_reference(ref, db)
        words: List[Word] = []

        for loc in locations:
            raw = db[loc]["text"]
            location_obj = Location.from_key(loc)
            word = self.parse_word(raw, location_obj)
            words.append(word)

        self._link_words(words)
        self._annotate_boundaries(words, stop_types=stop_types)
        return words
    
    def _link_words(self, words: List[Word]) -> None:
        """Link words with references to previous and next words."""
        for i, word in enumerate(words):
            if i > 0:
                word.prev_word = words[i - 1]
            if i < len(words) - 1:
                word.next_word = words[i + 1]
    
    def _annotate_boundaries(self, words: List[Word], *, stop_types: List[str]) -> None:
        """Set is_starting / is_stopping flags on each word.

        Parameters
        ----------
        words : List[Word]
            Sequence of words.
        stop_types : list[str]
            Stop sign types that should be treated as hard boundaries. If empty, no stop signs count.
        """
        words[0].is_starting = True
        words[-1].is_stopping = True

        stop_types = [s.lower() for s in stop_types]

        for idx, word in enumerate(words):
            # Stop-sign logic
            if word.stop_sign and word.stop_sign.name.lower() in stop_types:
                word.is_stopping = True
                if word.next_word:
                    word.next_word.is_starting = True

        if "verse" in stop_types:
            for idx, word in enumerate(words):
                prev_word = word.prev_word
                next_word = word.next_word
                # Start of verse
                if prev_word is None or prev_word.location.ayah_num != word.location.ayah_num:
                    word.is_starting = True
                # End of verse
                if next_word is None or next_word.location.ayah_num != word.location.ayah_num:
                    word.is_stopping = True


def load_symbol_mappings(map_path: str | Path = DATA_DIR / "base_phonemes.yaml") -> Dict[str, Any]:
    """Load symbol mappings from YAML file."""
    with Path(map_path).expanduser().open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)
