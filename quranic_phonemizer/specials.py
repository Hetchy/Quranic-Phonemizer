"""
Special word handling for location-specific phonemization rules.

Some words require special handling when phonemizing, especially for
stopping (waqf) scenarios.
"""

from typing import Dict, Set, Optional, Tuple

# Letters (by char) to skip during phonemization when stopping at these locations.
# Format: {location: set(letter_chars_to_skip)}
STOPPING_SKIP_LETTERS: Dict[str, Set[str]] = {
    # 27:36:8 - ءَاتَىٰنَِۧ
    # When stopping, ignore the small high yaa (U+06E7) letter entirely
    "27:36:8": {"\u06E7"},
}

# Diacritic overrides when stopping at specific locations.
# Format: {location: {letter_index: new_diacritic_name}}
# If new_diacritic_name is None, the diacritic is removed (becomes sukun-like behavior).
STOPPING_DIACRITIC_OVERRIDES: Dict[str, Dict[int, Optional[str]]] = {
    # 27:36:8 - ءَاتَىٰنَِۧ
    # When stopping, the kasra on noon (index 4) should become sukun
    # This makes the phoneme 'n' instead of 'n i'
    "27:36:8": {4: "SUKUN"},  # noon at index 4 gets sukun
}


def get_stopping_skip_letters(location: str) -> Set[str]:
    """
    Get the set of letter characters to skip when stopping at a location.
    
    Args:
        location: Word location key (e.g., "27:36:8")
        
    Returns:
        Set of letter characters to skip during phonemization
    """
    return STOPPING_SKIP_LETTERS.get(location, set())


def should_skip_letter_for_stopping(location: str, letter_char: str) -> bool:
    """
    Check if a letter should be skipped for phonemization when stopping.
    
    Args:
        location: Word location key
        letter_char: Letter character
        
    Returns:
        True if this letter should be ignored when stopping
    """
    skip_set = STOPPING_SKIP_LETTERS.get(location)
    if skip_set:
        return letter_char in skip_set
    return False


def get_stopping_diacritic_override(location: str, letter_index: int) -> Tuple[bool, Optional[str]]:
    """
    Check if a letter's diacritic should be overridden when stopping.
    
    Args:
        location: Word location key
        letter_index: Index of the letter in the word
        
    Returns:
        Tuple of (has_override, new_diacritic_name).
        If has_override is True, the diacritic should be replaced with new_diacritic_name.
    """
    overrides = STOPPING_DIACRITIC_OVERRIDES.get(location)
    if overrides and letter_index in overrides:
        return (True, overrides[letter_index])
    return (False, None)
