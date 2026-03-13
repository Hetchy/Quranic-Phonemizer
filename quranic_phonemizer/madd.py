"""
Madd (long vowel) detection and classification module.

This module handles:
1. Building madd mappings from phoneme sequences
2. Classifying madd types (wajib muttasil, jaiz munfasil)
3. Special cases (tanween+alef, hamza+fathatan, lafdh jalalah)
"""

from typing import List

from .mapping import MaddMapping, WordMapping
from .symbols.letters.lam import Lam

# Long vowel phonemes
LONG_VOWELS = {"a:", "aˤ:", "u:", "i:"}

# Short vowel phonemes (fatha only for leen)
SHORT_FATHA = {"a", "aˤ"}

# Leen consonants (yaa/waw as consonants, not vowels)
LEEN_CONSONANTS = {"j", "w"}

# Shaddah phonemes for madd lazim detection
SHADDAH_PHONEMES = {
    "bb", "tt", "θθ", "ʒʒ", "ħħ", "xx", "dd", "ðð", "rr", "rˤrˤ", "zz", "ss", "ʃʃ", "sˤsˤ", 
    "dˤdˤ", "tˤtˤ", "ðˤðˤ", "ʕʕ", "ff", "qq", "kk", "ll", "lˤlˤ", "hh", "ww", "jj"
}

# Ghunnah phonemes for madd lazim detection
GHUNNAH_PHONEMES = {"m̃", "ñ"}

# Letters that can be vowel graphemes
VOWEL_LETTERS = {"ا", "و", "ي", "ى", "ۧ"}

# Extensions that can be vowel graphemes
VOWEL_EXTENSIONS = {"DAGGER_ALEF", "MINI_WAW", "MINI_YA_END"}

# Hamza phoneme (glottal stop)
HAMZA_PHONEME = 'ʔ'

# Hardcoded lazim override locations
LAZIM_OVERRIDE_LOCATIONS = {"10:51:7", "10:91:1"}

# Hardcoded natural madd locations for special words
# These have long vowels that need explicit tabi'i classification
NATURAL_MADD_LOCATIONS = {"11:41:6", "2:72:4"}

# Particle letters: vocative يا and demonstrative ها
# When dagger alef sits on these, the hamza belongs to the next (joined) word
_PARTICLE_LETTERS = {'ي', 'ه'}


def build_madd_mappings(word_mappings: List[WordMapping]) -> None:
    """Scan phoneme sequences for long vowels and link to graphemes.
    
    Populates madd_mappings on each WordMapping with MaddMapping entries
    for every long vowel phoneme found.
    """
    for word_map in word_mappings:
        # Build cumulative phoneme index to letter index mapping
        phoneme_to_letter = []
        for letter_map in word_map.letter_mappings:
            for _ in letter_map.phonemes:
                phoneme_to_letter.append(letter_map.index)
        
        for ph_idx, phoneme in enumerate(word_map.phonemes):
            if phoneme not in LONG_VOWELS:
                continue
            
            # Find which letter produced this phoneme
            if ph_idx >= len(phoneme_to_letter):
                continue
            letter_idx = phoneme_to_letter[ph_idx]
            letter_map = word_map.letter_mappings[letter_idx]
            
            vowel_grapheme = None
            extension_index = None
            has_maddah = False
            
            # Check extensions for maddah
            for ext in letter_map.extensions:
                if ext.name == "MADDAH":
                    has_maddah = True
                    break
            
            # Check for vowel extension (dagger alef, mini waw/yaa)
            for ext_idx, ext in enumerate(letter_map.extensions):
                if ext.name in VOWEL_EXTENSIONS:
                    vowel_grapheme = ext.char
                    extension_index = ext_idx
                    break
            
            # Check if this letter has tanween and is followed by silent yaa/alef
            # In this case, skip creating MaddMapping for this letter - the silent letter is the madd
            # Example: طُوًى - waw has tanween fatha, yaa is silent - only yaa should be madd
            if (letter_map.diacritic in ('FATHATAN', 'DAMMATAN', 'KASRATAN') and
                letter_idx + 1 < len(word_map.letter_mappings)):
                next_letter = word_map.letter_mappings[letter_idx + 1]
                if next_letter.char in {'ا', 'ى', 'ي'} and len(next_letter.phonemes) == 0:
                    # Skip this consonant - the silent yaa/alef will be handled by _handle_tanween_alef_case
                    continue
            
            # Otherwise check if it's a vowel letter
            if not vowel_grapheme and letter_map.char in VOWEL_LETTERS:
                vowel_grapheme = letter_map.char
            
            # Fallback: check if char string contains a vowel letter or dagger alef
            # (for special words where combined chars like 'دَّٰ' contain the dagger alef)
            if not vowel_grapheme:
                for char in letter_map.char:
                    if char in VOWEL_LETTERS or char == '\u0670':  # U+0670 is dagger alef
                        vowel_grapheme = char
                        break
            
            if vowel_grapheme:
                word_map.madd_mappings.append(MaddMapping(
                    phoneme_index=ph_idx,
                    phoneme=phoneme,
                    letter_index=letter_idx,
                    vowel_grapheme=vowel_grapheme,
                    has_maddah=has_maddah,
                    extension_index=extension_index,
                ))
        
        # Special case: tanween fatha + silent alef at word end
        _handle_tanween_alef_case(word_map)
        
        # Special case: hamza + fathatan at word end
        _handle_hamza_fathatan_case(word_map)
        
        # Special case: Lafdh al-Jalalah (Allah) - implicit dagger alef
        _handle_lafdh_jalalah_case(word_map, phoneme_to_letter)


def _handle_tanween_alef_case(word_map: WordMapping) -> None:
    """Handle tanween fatha + silent alef at word end.
    
    When stopping, the tanween is dropped and alef becomes madd.
    """
    if not word_map.is_stopping or len(word_map.letter_mappings) < 2:
        return
    
    last_letter = word_map.letter_mappings[-1]
    prev_letter = word_map.letter_mappings[-2]
    
    # Check if last letter is silent alef or alef maksura
    if (last_letter.char in {'ا', 'ى'} and 
        len(last_letter.phonemes) == 0 and
        prev_letter.diacritic == 'FATHATAN'):
        # This alef is a madd when stopping
        word_map.madd_mappings.append(MaddMapping(
            phoneme_index=-1,
            phoneme='a:',
            letter_index=last_letter.index,
            vowel_grapheme='ا',
            has_maddah=False,
            extension_index=None,
        ))


def _handle_hamza_fathatan_case(word_map: WordMapping) -> None:
    """Handle hamza + fathatan at word end.
    
    When stopping, becomes hamza + fatha + alef (the alef is the madd).
    """
    if not word_map.is_stopping or not word_map.letter_mappings:
        return
    
    last_letter = word_map.letter_mappings[-1]
    
    # Check if last letter is hamza with fathatan
    if (last_letter.char == 'ء' and last_letter.diacritic == 'FATHATAN'):
        # The alef that will be added is a madd when stopping
        word_map.madd_mappings.append(MaddMapping(
            phoneme_index=-1,
            phoneme='a:',
            letter_index=last_letter.index,
            vowel_grapheme='ا',
            has_maddah=False,
            extension_index=None,
            is_hamza_fathatan=True,
        ))


def _handle_lafdh_jalalah_case(word_map: WordMapping, phoneme_to_letter: List[int]) -> None:
    """Handle Lafdh al-Jalalah (Allah) - implicit dagger alef.
    
    The word Allah has an implicit long vowel on the second lam with shaddah.
    """
    if not is_lafdh_jalalah(word_map):
        return
    
    # Find the lam with shaddah that produces the long vowel
    for letter_map in word_map.letter_mappings:
        if letter_map.char == 'ل' and letter_map.has_shaddah:
            # Check if this lam produces a long vowel
            has_long_vowel = any(ph in LONG_VOWELS for ph in letter_map.phonemes)
            if has_long_vowel:
                # Find the phoneme index
                for ph_idx, ph in enumerate(word_map.phonemes):
                    if ph in LONG_VOWELS:
                        if ph_idx < len(phoneme_to_letter):
                            if phoneme_to_letter[ph_idx] == letter_map.index:
                                word_map.madd_mappings.append(MaddMapping(
                                    phoneme_index=ph_idx,
                                    phoneme=ph,
                                    letter_index=letter_map.index,
                                    vowel_grapheme='',
                                    has_maddah=False,
                                    extension_index=None,
                                    is_lafdh_jalalah=True,
                                ))
                                break
                break


def is_lafdh_jalalah(word_map: WordMapping) -> bool:
    """Check if word is a form of Allah (لفظ الجلالة).
    
    Uses patterns defined in Lam.ALLAH_LETTER_PATTERNS.
    """
    if len(word_map.letter_mappings) < 3:
        return False
    
    word_letters = [lm.char for lm in word_map.letter_mappings]
    
    for pattern_letters in Lam.ALLAH_LETTER_PATTERNS.values():
        if len(word_letters) == len(pattern_letters):
            if all(wl == pl for wl, pl in zip(word_letters, pattern_letters)):
                return True
    return False


def classify_madd_types(word_mappings: List[WordMapping]) -> None:
    """Classify madd types based on what follows the long vowel.
    
    Madd types:
    - wajib_muttasil: long vowel followed by hamza in SAME word
    - jaiz_munfasil: long vowel followed by hamza in NEXT word
    
    Uses flat phoneme sequence to check if next phoneme is hamza,
    then determines same/different word based on word boundaries.
    """
    # Build flat phoneme sequence with word boundaries
    flat_phonemes = []
    phoneme_word_map = []
    
    for word_idx, word_map in enumerate(word_mappings):
        for ph in word_map.phonemes:
            flat_phonemes.append(ph)
            phoneme_word_map.append(word_idx)
    
    # Classify each madd
    for word_idx, word_map in enumerate(word_mappings):
        for mm in word_map.madd_mappings:
            # Skip special cases
            if mm.is_lafdh_jalalah or mm.is_hamza_fathatan:
                continue
            
            # Skip if no valid phoneme index
            if mm.phoneme_index < 0:
                continue
            
            # Calculate global phoneme index
            global_ph_idx = 0
            for w_idx in range(word_idx):
                global_ph_idx += len(word_mappings[w_idx].phonemes)
            global_ph_idx += mm.phoneme_index
            
            # Check if next phoneme in flat sequence is hamza
            next_global_idx = global_ph_idx + 1
            if next_global_idx < len(flat_phonemes):
                next_phoneme = flat_phonemes[next_global_idx]
                if next_phoneme == HAMZA_PHONEME:
                    # Hamza follows - now determine same or different word
                    next_word_idx = phoneme_word_map[next_global_idx]
                    if next_word_idx == word_idx:
                        mm.madd_type = 'wajib_muttasil'
                    elif not word_map.is_stopping:
                        # Cross-word munfasil only when continuing to next word
                        mm.madd_type = 'jaiz_munfasil'
                elif next_phoneme in SHADDAH_PHONEMES or next_phoneme in GHUNNAH_PHONEMES:
                    # Shaddah or ghunnah follows - madd lazim (only within same word)
                    next_word_idx = phoneme_word_map[next_global_idx]
                    if next_word_idx == word_idx:
                        mm.madd_type = 'lazim'
    
    # Apply munfasil overrides for special cases
    _apply_munfasil_overrides(word_mappings)
    
    # Apply lazim overrides for special cases (alef before lam)
    _apply_lazim_overrides(word_mappings)
    
    # Apply natural madd overrides for special words
    _apply_natural_madd_overrides(word_mappings)
    
    # Classify 'arid lissukun (only for stopping words)
    _classify_arid_lissukun(word_mappings)
    
    # Classify leen (only for stopping words)
    _classify_leen(word_mappings)


def _apply_munfasil_overrides(word_mappings: List[WordMapping]) -> None:
    """Reclassify particle-joined words from muttasil to munfasil.

    Words like يَـٰٓأَيُّهَا (ya + ayyuha) and هَـٰٓؤُلَآءِ (ha + ulaa'i) have a
    vocative يا or demonstrative ها particle graphically joined to the next word.
    The dagger alef on the particle is followed by hamza in the same graphical word,
    so classify_madd_types() marks it as wajib_muttasil. But linguistically the hamza
    belongs to a separate word, so the correct classification is jaiz_munfasil.

    Detection: a muttasil madd on dagger alef (ٰ) where the carrier letter is ي or ه.
    """
    for word_map in word_mappings:
        for mm in word_map.madd_mappings:
            if mm.madd_type != 'wajib_muttasil':
                continue
            if mm.vowel_grapheme != 'ٰ':
                continue
            letter = word_map.letter_mappings[mm.letter_index]
            if letter.char in _PARTICLE_LETTERS:
                mm.madd_type = 'jaiz_munfasil'


def _apply_lazim_overrides(word_mappings: List[WordMapping]) -> None:
    """Apply lazim overrides for special cases (alef before lam).
    
    These are specific word locations where the first alef should be classified as lazim.
    """
    for word_map in word_mappings:
        if word_map.location in LAZIM_OVERRIDE_LOCATIONS:
            # Set only the FIRST unclassified madd to lazim
            for mm in word_map.madd_mappings:
                if mm.madd_type is None:
                    mm.madd_type = 'lazim'
                    break  # Only the first one


def _apply_natural_madd_overrides(word_mappings: List[WordMapping]) -> None:
    """Apply natural madd classification for hardcoded special words.
    
    These are words like مَجْر۪ىٰهَا (11:41:6) and فَٱدَّٰرَْٰٔتُمْ (2:72:4) that have
    long vowels needing explicit tabi'i (natural madd) classification.
    """
    for word_map in word_mappings:
        if word_map.location == '11:41:6':
            # مَجْر۪ىٰهَا - Add madd for the silent alef at the end (letter index 5)
            # The a: from הָ (letter 4) is combined with final alef (letter 5)
            # Check if we already have a madd for the final alef
            has_final_alef = any(mm.letter_index == 5 for mm in word_map.madd_mappings)
            if not has_final_alef:
                word_map.madd_mappings.append(MaddMapping(
                    phoneme_index=-1,  # Not tied to specific phoneme
                    phoneme='a:',
                    letter_index=5,
                    vowel_grapheme='ا',
                    has_maddah=False,
                    extension_index=None,
                    madd_type=None,  # Natural/tabi'i
                ))




def _classify_arid_lissukun(word_mappings: List[WordMapping]) -> None:
    """Classify 'arid lissukun madd type.
    
    'Arid lissukun occurs when:
    - Word is stopping (last word in verse/segment)
    - Last phoneme is any consonant (becomes sukun when stopping)
    - Phoneme before it is a long vowel
    
    The long vowel can be extended 2, 4, or 6 counts when stopping.
    
    Special case: If last phoneme is "Q" (qalqala marker), ignore it and
    look at the phoneme before that.
    """
    # Find stopping words
    for word_map in word_mappings:
        if not word_map.is_stopping:
            continue
        
        if len(word_map.phonemes) < 2:
            continue
        
        # Get effective last phonemes, ignoring Q if present
        phonemes = word_map.phonemes
        effective_last_idx = len(phonemes) - 1
        
        # If last phoneme is Q, look back one more
        if phonemes[-1] == 'Q' and len(phonemes) >= 3:
            last_phoneme = phonemes[-2]
            second_last_phoneme = phonemes[-3]
            vowel_phoneme_idx = len(phonemes) - 3
        else:
            last_phoneme = phonemes[-1]
            second_last_phoneme = phonemes[-2]
            vowel_phoneme_idx = len(phonemes) - 2
        
        # Check if second-to-last is a long vowel and last is NOT a vowel
        if second_last_phoneme in LONG_VOWELS and last_phoneme not in LONG_VOWELS:
            # Find the madd mapping for this long vowel
            for mm in word_map.madd_mappings:
                if mm.phoneme_index == vowel_phoneme_idx:
                    # Only set if not already classified as something else
                    if mm.madd_type is None:
                        mm.madd_type = 'arid_lissukun'


def _classify_leen(word_mappings: List[WordMapping]) -> None:
    """Classify leen madd type.
    
    Leen occurs when stopping and word ends with pattern:
    - fatha (a) + yaa/waw consonant (j/w) + any consonant
    
    The yaa/waw is a consonant (not a vowel), preceded by fatha.
    When stopping, this creates a leen sound that can be extended.
    
    Note: Leen is NOT a regular madd (no long vowel phoneme), but it's
    highlighted similarly for tajweed analysis. We create a special
    MaddMapping for it.
    """
    for word_map in word_mappings:
        if not word_map.is_stopping:
            continue
        
        if len(word_map.phonemes) < 3:
            continue
        
        # Get effective phonemes, ignoring Q if present at end
        phonemes = word_map.phonemes
        if phonemes[-1] == 'Q' and len(phonemes) >= 4:
            # Ignore Q, look at previous 3
            third_last = phonemes[-4]  # Should be fatha
            second_last = phonemes[-3]  # Should be j or w
            last = phonemes[-2]  # Consonant (not Q)
            leen_ph_idx = len(phonemes) - 3
        else:
            # Pattern: ...a j/w <any>
            third_last = phonemes[-3]  # Should be fatha
            second_last = phonemes[-2]  # Should be j or w
            last = phonemes[-1]  # Any consonant
            leen_ph_idx = len(phonemes) - 2
        
        # Check the pattern - last must NOT be a long vowel or Q (arid takes precedence, Q already handled above)
        if third_last in SHORT_FATHA and second_last in LEEN_CONSONANTS and last not in LONG_VOWELS and last != 'Q':
            # Find which letter produced the leen consonant (j/w)
            # Build phoneme_to_letter mapping
            phoneme_to_letter = []
            for letter_map in word_map.letter_mappings:
                for _ in letter_map.phonemes:
                    phoneme_to_letter.append(letter_map.index)
            
            
            if leen_ph_idx < len(phoneme_to_letter):
                letter_idx = phoneme_to_letter[leen_ph_idx]
                letter_map = word_map.letter_mappings[letter_idx]
                
                # Create a leen mapping (not a regular madd, but similar display)
                word_map.madd_mappings.append(MaddMapping(
                    phoneme_index=leen_ph_idx,
                    phoneme=second_last,  # j or w
                    letter_index=letter_idx,
                    vowel_grapheme=letter_map.char,  # ي or و
                    has_maddah=False,
                    extension_index=None,
                    madd_type='leen',
                ))
