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
from .tajweed_rule import TajweedRule, TajweedRuleTag

DATA_DIR = Path(__file__).resolve().parent / "resources"

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

def _load_letter_overrides(yaml_path: str | Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load letter-level phoneme overrides keyed by location."""
    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    overrides_map: Dict[str, List[Dict[str, Any]]] = {}
    for entry in data.get('letter_overrides', []):
        loc = entry['location']
        overrides_map.setdefault(loc, []).append(entry)
    return overrides_map


def _load_special_words(yaml_path: str | Path) -> Dict[str, Dict[str, Any]]:
    """
    Load special words and their letter mappings from YAML file.
    
    Parameters
    ----------
    yaml_path : str | Path
        Path to the special_words.yaml file
        
    Returns
    -------
    Dict[str, Dict[str, Any]]
        Dictionary mapping location keys to special word data including:
        - 'phonemes': List[str] - word-level phonemes
        - 'letter_mappings': List[Dict] - per-letter mapping with char, phonemes, rules
    """
    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
    special_words_map = {}
    
    for word_entry in data['special_words']:
        text = word_entry['text']
        letter_mappings = word_entry.get('letter_mappings', [])
        
        # Build word-level phonemes by concatenating letter phonemes
        word_phonemes = []
        for letter_map in letter_mappings:
            word_phonemes.extend(letter_map.get('phonemes', []))
        
        locations = word_entry['locations']
        
        tajweed_mapping = word_entry.get('tajweed_mapping')

        for location in locations:
            special_words_map[location] = {
                'text': text,
                'phonemes': word_phonemes,
                'letter_mappings': letter_mappings,
                'tajweed_mapping': tajweed_mapping,
            }
    
    return special_words_map


def _get_special_word_data(location_key: str, special_words_map: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Get data for a special word at a specific location.
    
    Parameters
    ----------
    location_key : str
        Location key in format "surah:verse:word"
    special_words_map : Dict[str, Dict[str, Any]]
        Dictionary mapping location keys to special word data
        
    Returns
    -------
    Optional[Dict[str, Any]]
        Special word data including phonemes and letter_mappings, or None if not found
    """
    return special_words_map.get(location_key)


class Parser:
    """Parses text into properly associated symbols for Quranic phonemization."""
    
    def __init__(self, symbol_mappings: Dict[str, Any], special_words_path: str | Path = DATA_DIR / "special_words.yaml"):
        self.symbol_mappings = symbol_mappings
        self.special_words_map = _load_special_words(special_words_path)
        self.letter_overrides_map = _load_letter_overrides(special_words_path)
        self._build_lookup_tables()
    
    def _build_lookup_tables(self) -> None:
        """Build lookup tables for efficient symbol identification.

        In addition to the per-category maps used by reflective code paths,
        we build pre-baked dispatch tables used by parse_word's hot loops:

        - _outer_dispatch maps each "outer" char (letter or stop-sign) to
          a tuple describing exactly what to construct.
        - _modifier_dispatch maps each "inner" char (diacritic / extension /
          shaddah / other) to a pre-built singleton symbol or marker.

        Each dispatch entry is shaped (kind, payload, ...) so parse_word
        can do a single dict.get + tuple unpack instead of running 4-5
        membership checks per character.
        """
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

        # Pre-baked dispatch tables for parse_word's hot loops.
        outer = {}
        for char, (letter_type, info) in self.letter_map.items():
            cls = LETTER_CLASSES.get(char, LetterSymbol)
            outer[char] = ("L", cls, letter_type, info.get("phoneme", ""))
        for char, (stop_type, info) in self.stop_sign_map.items():
            stop_sym = StopSymbol(stop_type, char, info.get("phoneme", ""))
            outer[char] = ("S", stop_sym)
        self._outer_dispatch = outer

        modifier = {}
        for char, (diacritic_type, info) in self.diacritic_map.items():
            diac = DiacriticSymbol(diacritic_type, char, info.get("phoneme"))
            modifier[char] = ("D", diac)
        for char, (extension_type, info) in self.extension_map.items():
            ext = ExtensionSymbol(extension_type, char, info.get("phoneme"))
            modifier[char] = ("E", ext)
        for char, (other_type, info) in self.other_map.items():
            other_sym = OtherSymbol(other_type, char, info.get("phoneme"))
            modifier[char] = ("O", other_sym)
        modifier["ّ"] = ("SH",)
        self._modifier_dispatch = modifier
    
    def parse_word(self, text: str, location: Location) -> Word:
        """Parse a word text into a Word object with properly associated symbols."""
        word = Word(location=location, text=text)

        # Check if this is a special word with letter mappings
        special_data = self.special_words_map.get(location.location_key)
        if special_data:
            word.phonemes = special_data['phonemes']
            letter_mappings = special_data.get('letter_mappings', [])
            
            # Create letter symbols from letter_mappings
            for letter_map in letter_mappings:
                full_char = letter_map['char']
                phonemes = letter_map.get('phonemes', [])

                # Check if this char is a stop sign (may include leading space)
                char_stripped = full_char.strip()
                if char_stripped in self.stop_sign_map:
                    stop_type, stop_info = self.stop_sign_map[char_stripped]
                    word.stop_sign = StopSymbol(stop_type, char_stripped, stop_info.get("phoneme", ""))
                    continue  # Don't add as a letter

                # Extract base letter (first character) and modifiers
                # This ensures is_ikhfaa and similar checks work correctly
                base_char = full_char[0] if full_char else ''
                modifiers = full_char[1:] if len(full_char) > 1 else ''

                # Get letter class and create symbol using base char
                letter_class = LETTER_CLASSES.get(base_char, LetterSymbol)
                letter_type = base_char
                base_phoneme = ""

                # Look up in letter_map for proper letter type if exists
                if base_char in self.letter_map:
                    letter_type, letter_info = self.letter_map[base_char]
                    base_phoneme = letter_info.get("phoneme", "")

                letter = letter_class(letter_type, base_char, base_phoneme)

                # Process modifiers (diacritics, extensions, shaddah, other)
                for mod_char in modifiers:
                    if mod_char in self.diacritic_map:
                        diacritic_type, diacritic_info = self.diacritic_map[mod_char]
                        diacritic = DiacriticSymbol(diacritic_type, mod_char, diacritic_info.get("phoneme"))
                        letter.diacritic = diacritic
                    elif mod_char in self.extension_map:
                        extension_type, extension_info = self.extension_map[mod_char]
                        extension = ExtensionSymbol(extension_type, mod_char, extension_info.get("phoneme"))
                        letter.add_extension(extension)
                    elif mod_char == "ّ":
                        letter.has_shaddah = True
                    elif mod_char in self.other_map:
                        other_type, other_info = self.other_map[mod_char]
                        other = OtherSymbol(other_type, mod_char, other_info.get("phoneme"))
                        letter.add_other_symbol(other)

                letter.phonemes = phonemes
                letter.parent_word = word
                letter.index_in_word = len(word.letters)
                word.letters.append(letter)

            # Populate _tajweed_rules from single-entry tajweed_mapping (non-muqattaat)
            tajweed_mapping = special_data.get('tajweed_mapping')
            if tajweed_mapping and len(tajweed_mapping) == 1:
                tm_entries = tajweed_mapping[0].get('entries', [])
                for letter, tm_entry in zip(word.letters, tm_entries):
                    for rule_str in tm_entry.get('source_rules', []):
                        try:
                            letter.add_tajweed_rule(
                                TajweedRuleTag(rule=TajweedRule(rule_str), is_source=True))
                        except ValueError:
                            pass

            return word
        
        # The Quran DB and special_words.yaml contain no <rule> tags, so the
        # raw text can be parsed directly without stripping.
        n = len(text)
        outer = self._outer_dispatch
        modifier = self._modifier_dispatch
        word_letters = word.letters

        # Parse symbols with proper association
        i = 0
        while i < n:
            char = text[i]

            # Skip whitespace cheaply (most common skip case)
            if char == " ":
                i += 1
                continue

            entry = outer.get(char)
            if entry is None:
                if char.isspace():
                    i += 1
                    continue
                # Unknown symbol — attach to previous letter if any
                if word_letters:
                    word_letters[-1].add_other_symbol(OtherSymbol("UNKNOWN", char, None))
                i += 1
                continue

            kind = entry[0]
            if kind == "S":
                word.stop_sign = entry[1]
                i += 1
                continue

            # kind == "L"
            _, letter_class, letter_type, base_phoneme = entry
            letter = letter_class(letter_type, char, base_phoneme)

            # Look ahead for associated modifiers
            j = i + 1
            while j < n:
                m = modifier.get(text[j])
                if m is None:
                    break
                mk = m[0]
                if mk == "D":
                    letter.diacritic = m[1]
                elif mk == "E":
                    letter.add_extension(m[1])
                elif mk == "SH":
                    letter.has_shaddah = True
                else:  # mk == "O"
                    letter.add_other_symbol(m[1])
                j += 1

            letter.parent_word = word
            letter.index_in_word = len(word_letters)
            word_letters.append(letter)
            i = j
        
        # Attach letter overrides if any exist for this location
        overrides = self.letter_overrides_map.get(location.location_key)
        if overrides:
            word._letter_overrides = overrides

        return word

    def _strip_rule_tags(self, text: str) -> str:
        """Remove rule tags from text for character processing."""
        stripped_text = re.sub(r"<rule class=[^>]+>", "", text)
        stripped_text = re.sub(r"</rule>", "", stripped_text)
        return stripped_text
    
    def load_words(self, ref: str, db_path: str | Path = DATA_DIR / "Quran.json", *, stop_signs: List[str] = [], stop_refs: List[str] = []) -> List[Word]:
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
        self._annotate_boundaries(words, stop_signs=stop_signs, stop_refs=stop_refs)
        return words
    
    def _link_words(self, words: List[Word]) -> None:
        """Link words with references to previous and next words."""
        for i, word in enumerate(words):
            if i > 0:
                word.prev_word = words[i - 1]
            if i < len(words) - 1:
                word.next_word = words[i + 1]
    
    def _annotate_boundaries(self, words: List[Word], *, stop_signs: List[str], stop_refs: List[str] = []) -> None:
        """Set is_starting / is_stopping flags on each word.

        Parameters
        ----------
        words : List[Word]
            Sequence of words.
        stop_signs : list[str]
            Stop sign types that should be treated as hard boundaries. If empty, no stop signs count.
        stop_refs : list[str]
            Explicit location references (e.g. '2:3:5') whose words should be marked as stopping.
        """
        words[0].is_starting = True
        words[-1].is_stopping = True

        stop_signs = [s.lower() for s in stop_signs]

        for idx, word in enumerate(words):
            # Stop-sign logic
            if word.stop_sign and word.stop_sign.name.lower() in stop_signs:
                word.is_stopping = True
                if word.next_word:
                    word.next_word.is_starting = True

        if "verse" in stop_signs:
            for idx, word in enumerate(words):
                prev_word = word.prev_word
                next_word = word.next_word
                # Start of verse
                if prev_word is None or prev_word.location.ayah_num != word.location.ayah_num:
                    word.is_starting = True
                # End of verse
                if next_word is None or next_word.location.ayah_num != word.location.ayah_num:
                    word.is_stopping = True

        # Explicit stop refs
        if stop_refs:
            stop_ref_set = {r.strip() for r in stop_refs}
            for word in words:
                if word.location.location_key in stop_ref_set:
                    word.is_stopping = True
                    if word.next_word:
                        word.next_word.is_starting = True


def load_symbol_mappings(map_path: str | Path = DATA_DIR / "base_phonemes.yaml") -> Dict[str, Any]:
    """Load symbol mappings from YAML file."""
    with Path(map_path).expanduser().open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)
