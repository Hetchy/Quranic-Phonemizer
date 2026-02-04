#!/usr/bin/env python3
"""
Convert phonemizer output to flat many-to-many letter-phoneme mappings.

This script takes PhonemizationMapping from the phonemizer and converts it to the
flat [chars, phonemes] format defined in docs/many-to-many-mapping-research.md.

Every entry has at least one phoneme (no empty entries). Silent letters merge
into adjacent entries. Word boundaries are signaled by spaces in the chars field.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from core.phonemizer import Phonemizer
from core.mapping import (
    PhonemizationMapping,
    WordMapping,
    LetterMapping,
    MappingType,
)


# =============================================================================
# Constants: Rule Classification
# =============================================================================

# Group 1: Silent letters that merge LEFT within-word
LEFT_MERGE_RULES: Set[str] = {
    "alef_silent_always",
    "alef_silent_continuation",
    "waw_silent",
    "yaa_silent",
    "tanween_alif",
    "special_stop_skip",
}

# Group 3: Silent letters that merge RIGHT within-word
RIGHT_MERGE_RULES: Set[str] = {
    "hamza_wasl_silent",
    "lam_shamsiyah",
    "iltiqaa_tanween",
    "iltiqaa_vowel",
}

# Group 2: Silent at word-end -> cross-word MERGE with next word's first letter
CROSS_WORD_MERGE_RULES: Set[str] = {
    "idgham_ghunnah_noon",
    "idgham_bila_ghunnah_noon",
    "idgham_mutajanisayn_kamil",
    "idgham_mutamathilayn",
    "idgham_mutaqaribayn",
}

# Within-word RIGHT merge (same rules as cross-word but at non-final position)
WITHIN_WORD_RIGHT_MERGE_RULES: Set[str] = {
    "idgham_mutamathilayn",
    "idgham_mutaqaribayn",
    "idgham_mutajanisayn_kamil",
}

# Cross-word MERGE where BOTH letters have phonemes (combined into one entry)
CROSS_WORD_BOTH_MERGE_RULES: Set[str] = {
    "idgham_shafawi",
}

# Non-merge cross-word: last letter has phonemes, just add space suffix
CROSS_WORD_NON_MERGE_RULES: Set[str] = {
    "ikhfaa_noon",
    "iqlab_noon",
    "ikhfaa_tanween",
    "iqlab_tanween",
    "ikhfaa_shafawi",
    "idgham_ghunnah_tanween",
    "idgham_bila_ghunnah_tanween",
}

# Vowel letter characters
VOWEL_LETTER_CHARS: Set[str] = {"ا", "و", "ي", "ى"}

# Madd extension names eligible for splitting
MADD_EXTENSION_NAMES: Set[str] = {"DAGGER_ALEF", "MADDAH", "MINI_WAW", "MINI_YA_END"}

# Short vowel phonemes (for iltiqaa detection)
SHORT_VOWEL_PHONEMES: Set[str] = {"a", "aˤ", "u", "i"}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class MergeInfo:
    """Merge direction and rule for a letter."""
    direction: str  # "LEFT", "RIGHT", "CROSS_WORD_MERGE", "CROSS_WORD_BOTH", "CROSS_WORD_NON_MERGE", "NONE"
    rule: str = ""


@dataclass
class ProtoEntry:
    """Intermediate entry before final merging."""
    chars: str
    phonemes: List[str]
    letter_indices: List[int] = field(default_factory=list)
    merge_info: Optional[MergeInfo] = None


@dataclass
class CrossWordAction:
    """Action to take at a word boundary."""
    action: str  # "MERGE", "BOTH_MERGE", "NON_MERGE", "ILTIQAA_VOWEL", "NORMAL", "FINAL"
    rule: str = ""


# =============================================================================
# Utility Functions
# =============================================================================

def is_madd_phoneme(ph: str) -> bool:
    """Check if a phoneme is a long vowel (madd)."""
    return ":" in ph


def get_full_char(letter: LetterMapping) -> str:
    """Build the full character string including extensions."""
    ext_chars = "".join(ext.char for ext in letter.extensions if ext.char)
    return letter.char + ext_chars


def is_silent(letter: LetterMapping) -> bool:
    """Check if a letter produces no phonemes."""
    return len(letter.phonemes) == 0 or letter.mapping_type == MappingType.SILENT


def get_merge_info(letter: LetterMapping, word: WordMapping, idx: int) -> MergeInfo:
    """Determine the merge direction for a letter."""
    rules = set(letter.letter_rules) if letter.letter_rules else set()
    is_last = idx == len(word.letter_mappings) - 1

    # Non-silent letters: check for cross-word effects
    if not is_silent(letter):
        # Idgham shafawi: both meems merge (first has phonemes)
        if CROSS_WORD_BOTH_MERGE_RULES & rules and is_last:
            rule = (CROSS_WORD_BOTH_MERGE_RULES & rules).pop()
            return MergeInfo("CROSS_WORD_BOTH", rule)

        # Non-merge cross-word effects
        if CROSS_WORD_NON_MERGE_RULES & rules and is_last:
            rule = (CROSS_WORD_NON_MERGE_RULES & rules).pop()
            return MergeInfo("CROSS_WORD_NON_MERGE", rule)

        return MergeInfo("NONE")

    # Silent letter: determine merge direction

    # Group 1: LEFT merge
    if LEFT_MERGE_RULES & rules:
        rule = (LEFT_MERGE_RULES & rules).pop()
        return MergeInfo("LEFT", rule)

    # Group 3: RIGHT merge within-word
    # Special case: mid-word hamza wasl merges LEFT instead of RIGHT
    if RIGHT_MERGE_RULES & rules:
        rule = (RIGHT_MERGE_RULES & rules).pop()
        if rule == "hamza_wasl_silent" and idx > 0:
            # Mid-word hamza wasl merges LEFT
            return MergeInfo("LEFT", rule)
        return MergeInfo("RIGHT", rule)

    # Group 2: within-word vs cross-word idgham
    if WITHIN_WORD_RIGHT_MERGE_RULES & rules:
        rule = (WITHIN_WORD_RIGHT_MERGE_RULES & rules).pop()
        if is_last:
            return MergeInfo("CROSS_WORD_MERGE", rule)
        else:
            return MergeInfo("RIGHT", rule)

    if CROSS_WORD_MERGE_RULES & rules:
        rule = (CROSS_WORD_MERGE_RULES & rules).pop()
        return MergeInfo("CROSS_WORD_MERGE", rule)

    # Fallback for silent letters with no recognized rule
    if letter.char in VOWEL_LETTER_CHARS:
        return MergeInfo("LEFT", "vowel_lengthening_failure")

    return MergeInfo("LEFT", "unknown_silent")


def should_split_extension(letter: LetterMapping, word: WordMapping) -> Optional[Tuple[str, str]]:
    """
    Check if a letter's madd extension should be split into its own entry.

    Returns (extension_chars, madd_phoneme) if split needed, else None.
    Note: extension_chars may be multiple chars if there are multiple madd extensions.
    """
    # Must have extensions with non-empty char and madd-eligible name
    madd_exts = [
        ext for ext in letter.extensions
        if ext.char and ext.name in MADD_EXTENSION_NAMES
    ]
    if not madd_exts:
        return None

    # Must have a madd phoneme in the letter's phonemes
    madd_phonemes = [ph for ph in letter.phonemes if is_madd_phoneme(ph)]
    if not madd_phonemes:
        return None

    # Rule 4b exceptions:

    # Alef maksura + dagger alef: reinforcing extension, don't split
    if letter.char == "ى" and any(ext.name == "DAGGER_ALEF" for ext in madd_exts):
        return None

    # Vowel letter where ALL phonemes are madd (it's a carrier, not consonant)
    if letter.char in VOWEL_LETTER_CHARS:
        non_madd = [ph for ph in letter.phonemes if not is_madd_phoneme(ph)]
        if not non_madd:
            return None

    # Get ALL madd extension chars combined (they form a unit)
    # e.g., ٰٓ (dagger alef + maddah) stays together
    ext_chars = "".join(ext.char for ext in madd_exts)

    # Take the last madd phoneme (typically the extension's)
    madd_ph = madd_phonemes[-1]

    return (ext_chars, madd_ph)


# =============================================================================
# Proto-Entry Building
# =============================================================================

def build_word_proto_entries(word: WordMapping) -> List[ProtoEntry]:
    """Build proto-entries for a word, applying extension splitting."""
    entries = []

    for i, letter in enumerate(word.letter_mappings):
        full_char = get_full_char(letter)
        phonemes = list(letter.phonemes)
        merge = get_merge_info(letter, word, i)

        # Check extension splitting (Rule 4)
        split_result = should_split_extension(letter, word)
        if split_result:
            ext_char, madd_ph = split_result

            # Remove madd phoneme from letter's phonemes (last occurrence)
            phonemes_copy = list(phonemes)
            for j in range(len(phonemes_copy) - 1, -1, -1):
                if is_madd_phoneme(phonemes_copy[j]):
                    madd_ph = phonemes_copy.pop(j)
                    break

            # Remove extension char from full_char
            base_char = full_char.replace(ext_char, "", 1)

            # Create consonant entry
            entries.append(ProtoEntry(
                chars=base_char,
                phonemes=phonemes_copy,
                letter_indices=[i],
                merge_info=merge if not phonemes_copy else MergeInfo("NONE"),
            ))
            # Create extension entry (always has phoneme, never merges)
            entries.append(ProtoEntry(
                chars=ext_char,
                phonemes=[madd_ph],
                letter_indices=[i],
                merge_info=MergeInfo("NONE"),
            ))
        else:
            entries.append(ProtoEntry(
                chars=full_char,
                phonemes=phonemes,
                letter_indices=[i],
                merge_info=merge,
            ))

    return entries


def build_special_word_entries(word: WordMapping) -> List[ProtoEntry]:
    """Build proto-entries for a special word.

    Special words (muqatta'at) have pre-computed phonemes that spell out the letter names.
    NO extension splitting is done because the phoneme order matters for alignment and
    the madd phoneme may be in the middle of the letter's pronunciation (e.g., meem = "m̃ i: m").

    However, silent letters (like hamza wasl) still need to be merged.
    """
    entries = []

    for i, letter in enumerate(word.letter_mappings):
        full_char = get_full_char(letter)
        phonemes = list(letter.phonemes)

        # Check if this letter is silent and needs merging
        if not phonemes:
            # Determine merge direction
            rules = set(letter.letter_rules) if letter.letter_rules else set()

            # RIGHT merge (hamza wasl at start)
            if rules & RIGHT_MERGE_RULES or "hamzat_wasl" in rules:
                entries.append(ProtoEntry(
                    chars=full_char,
                    phonemes=[],
                    letter_indices=[i],
                    merge_info=MergeInfo("RIGHT", "special_word_silent"),
                ))
            # LEFT merge (default for silent in special words)
            else:
                entries.append(ProtoEntry(
                    chars=full_char,
                    phonemes=[],
                    letter_indices=[i],
                    merge_info=MergeInfo("LEFT", "special_word_silent"),
                ))
        else:
            entries.append(ProtoEntry(chars=full_char, phonemes=phonemes, letter_indices=[i]))

    # Apply within-word merging for silent letters
    return merge_within_word(entries)


# =============================================================================
# Within-Word Merging
# =============================================================================

def merge_within_word(entries: List[ProtoEntry]) -> List[ProtoEntry]:
    """
    Merge silent entries LEFT or RIGHT within a word.

    Phase 1: RIGHT merges (accumulate silent chars, prepend to next non-silent)
    Phase 2: LEFT merges (append silent chars to previous entry)
    """
    # Phase 1: RIGHT merges
    merged = []
    pending_right_chars = ""
    pending_right_indices: List[int] = []

    for entry in entries:
        mi = entry.merge_info
        if mi and mi.direction == "RIGHT" and not entry.phonemes:
            # Accumulate for right merge
            pending_right_chars += entry.chars
            pending_right_indices.extend(entry.letter_indices)
        else:
            if pending_right_chars:
                # Prepend accumulated chars to this entry
                entry = ProtoEntry(
                    chars=pending_right_chars + entry.chars,
                    phonemes=entry.phonemes,
                    letter_indices=pending_right_indices + entry.letter_indices,
                    merge_info=entry.merge_info,
                )
                pending_right_chars = ""
                pending_right_indices = []
            merged.append(entry)

    # Handle dangling right-merge at end (edge case)
    if pending_right_chars:
        merged.append(ProtoEntry(
            chars=pending_right_chars,
            phonemes=[],
            letter_indices=pending_right_indices,
        ))

    # Phase 2: LEFT merges
    final = []
    for entry in merged:
        mi = entry.merge_info
        if mi and mi.direction == "LEFT" and not entry.phonemes:
            if final:
                prev = final[-1]
                final[-1] = ProtoEntry(
                    chars=prev.chars + entry.chars,
                    phonemes=prev.phonemes,
                    letter_indices=prev.letter_indices + entry.letter_indices,
                    merge_info=prev.merge_info,
                )
            else:
                # No previous entry (edge case)
                final.append(entry)
        else:
            final.append(entry)

    return final


# =============================================================================
# Cross-Word Handling
# =============================================================================

def detect_cross_word_type(
    prev_entries: List[ProtoEntry],
    prev_word: WordMapping,
    next_word: Optional[WordMapping],
    next_entries: Optional[List[ProtoEntry]],
) -> CrossWordAction:
    """Determine the action to take at a word boundary."""
    if not next_word or not next_entries:
        return CrossWordAction("FINAL")

    last_entry = prev_entries[-1]
    mi = last_entry.merge_info

    # Cross-word merge: silent letter at end merges with next word's first
    if mi and mi.direction == "CROSS_WORD_MERGE":
        return CrossWordAction("MERGE", mi.rule)

    # Cross-word both merge: both letters have phonemes, combine
    if mi and mi.direction == "CROSS_WORD_BOTH":
        return CrossWordAction("BOTH_MERGE", mi.rule)

    # Non-merge cross-word: space suffix
    if mi and mi.direction == "CROSS_WORD_NON_MERGE":
        return CrossWordAction("NON_MERGE", mi.rule)

    # Check for iltiqaa_vowel: ONLY when the vowel letter at end of prev word
    # is SILENT (empty phonemes). If it has phonemes (even short vowel), the
    # iltiqaa has already been handled by the phonemizer and we just add space.
    if not last_entry.phonemes:
        # Check if it's an iltiqaa case by looking at the letter rules
        last_letter = prev_word.letter_mappings[-1]
        if last_letter.letter_rules and "iltiqaa_vowel" in last_letter.letter_rules:
            return CrossWordAction("ILTIQAA_VOWEL", "iltiqaa_vowel")

    return CrossWordAction("NORMAL")


def handle_iltiqaa_vowel(
    prev_entries: List[ProtoEntry],
    prev_word: WordMapping,
    next_entries: List[ProtoEntry],
    next_word: WordMapping,
) -> Tuple[List[ProtoEntry], List[ProtoEntry]]:
    """
    Handle iltiqaa_vowel cross-word effect.

    Two cases:
    1. Standard case: The phonemizer stores the demoted short vowel on the vowel letter.
       We need to move it back to the preceding consonant.
    2. Special word case: The vowel letter is already silent (phonemes moved during
       special word processing). We just need to chain it with the cross-word merge.

    In both cases, we chain all trailing silent entries from prev word + leading
    silent from next word into the first non-silent entry of next word.
    """
    # Find the vowel letter that has iltiqaa_vowel
    iltiqaa_letter_idx = None
    for i in range(len(prev_word.letter_mappings) - 1, -1, -1):
        lm = prev_word.letter_mappings[i]
        if lm.letter_rules and "iltiqaa_vowel" in lm.letter_rules:
            iltiqaa_letter_idx = i
            break

    if iltiqaa_letter_idx is None:
        return prev_entries, next_entries

    # Find the corresponding entry
    vowel_entry_idx = None
    for eidx, entry in enumerate(prev_entries):
        if iltiqaa_letter_idx in entry.letter_indices:
            vowel_entry_idx = eidx
            break

    if vowel_entry_idx is None:
        return prev_entries, next_entries

    new_prev = list(prev_entries)

    # Check if we need to move a phoneme (standard case) or if it's already silent (special word case)
    iltiqaa_letter = prev_word.letter_mappings[iltiqaa_letter_idx]
    vowel_entry = new_prev[vowel_entry_idx]

    if iltiqaa_letter.phonemes and vowel_entry_idx > 0:
        # Standard case: move demoted short vowel to preceding consonant
        if len(iltiqaa_letter.phonemes) == 1 and iltiqaa_letter.phonemes[0] in SHORT_VOWEL_PHONEMES:
            demoted_phoneme = iltiqaa_letter.phonemes[0]
            consonant_entry_idx = vowel_entry_idx - 1
            cons_entry = new_prev[consonant_entry_idx]

            new_prev[consonant_entry_idx] = ProtoEntry(
                chars=cons_entry.chars,
                phonemes=cons_entry.phonemes + [demoted_phoneme],
                letter_indices=cons_entry.letter_indices,
                merge_info=cons_entry.merge_info,
            )

            new_prev[vowel_entry_idx] = ProtoEntry(
                chars=vowel_entry.chars,
                phonemes=[],  # now silent
                letter_indices=vowel_entry.letter_indices,
                merge_info=MergeInfo("CROSS_WORD_SILENT", "iltiqaa_vowel"),
            )
    # else: vowel letter is already silent (special word case), no phoneme to move

    # Collect trailing silent entries from prev_entries starting at vowel_entry_idx
    silent_chain_chars = ""
    merge_start_idx = vowel_entry_idx
    for eidx in range(vowel_entry_idx, len(new_prev)):
        entry = new_prev[eidx]
        if not entry.phonemes:
            silent_chain_chars += entry.chars
        else:
            # Entry has phonemes, stop collecting
            merge_start_idx = eidx
            break
    else:
        # All entries from vowel_entry_idx onward are silent
        merge_start_idx = len(new_prev)

    # Add space for word boundary
    silent_chain_chars += " "

    # Collect leading silent entries from next_entries
    first_non_silent_idx = 0
    for eidx, entry in enumerate(next_entries):
        if not entry.phonemes:
            silent_chain_chars += entry.chars
            first_non_silent_idx = eidx + 1
        else:
            break

    # Merge silent chain into first non-silent entry of next word
    if first_non_silent_idx < len(next_entries):
        target = next_entries[first_non_silent_idx]
        merged_entry = ProtoEntry(
            chars=silent_chain_chars + target.chars,
            phonemes=target.phonemes,
            letter_indices=target.letter_indices,
            merge_info=target.merge_info,
        )
        new_next = [merged_entry] + list(next_entries[first_non_silent_idx + 1:])
    else:
        # All next entries are silent (edge case)
        new_next = next_entries

    # Trim prev_entries: remove from vowel_entry_idx onward (the silent entries we chained)
    new_prev = new_prev[:vowel_entry_idx]

    return new_prev, new_next


# =============================================================================
# Main Conversion
# =============================================================================

def build_flat_mapping(
    mapping: PhonemizationMapping,
    words: Optional[List[WordMapping]] = None,
) -> List[Tuple[str, List[str]]]:
    """Convert PhonemizationMapping to flat [chars, phonemes] sequence.

    Args:
        mapping: The full phonemization mapping (provides context for special rules)
        words: Optional filtered word list. If None, uses mapping.words.
               Useful for generating flat mapping for a word range subset.
    """
    if words is None:
        words = mapping.words

    # Phase 1: Build proto-entries per word
    all_word_entries: List[List[ProtoEntry]] = []
    for word in words:
        if word.is_special_word:
            entries = build_special_word_entries(word)
        else:
            entries = build_word_proto_entries(word)
            entries = merge_within_word(entries)
        all_word_entries.append(entries)

    # Phase 2: Handle cross-word effects and word boundaries
    flat: List[Tuple[str, List[str]]] = []
    i = 0

    while i < len(all_word_entries):
        entries = all_word_entries[i]
        is_last = i == len(all_word_entries) - 1
        next_entries = all_word_entries[i + 1] if not is_last else None
        next_word = words[i + 1] if not is_last else None

        action = detect_cross_word_type(entries, words[i], next_word, next_entries)

        if action.action == "FINAL":
            # Last word: no space suffix
            flat.extend((e.chars, e.phonemes) for e in entries)

        elif action.action == "MERGE":
            # Cross-word merge: last entry (silent) + first of next -> single entry with space
            last = entries[-1]
            first_next = next_entries[0]
            merged_chars = last.chars + " " + first_next.chars
            merged_phonemes = first_next.phonemes

            flat.extend((e.chars, e.phonemes) for e in entries[:-1])
            flat.append((merged_chars, merged_phonemes))
            all_word_entries[i + 1] = list(next_entries[1:])

        elif action.action == "BOTH_MERGE":
            # Both letters have phonemes, combine into one entry
            last = entries[-1]
            first_next = next_entries[0]
            merged_chars = last.chars + " " + first_next.chars
            merged_phonemes = last.phonemes + first_next.phonemes

            flat.extend((e.chars, e.phonemes) for e in entries[:-1])
            flat.append((merged_chars, merged_phonemes))
            all_word_entries[i + 1] = list(next_entries[1:])

        elif action.action == "ILTIQAA_VOWEL":
            new_prev, new_next = handle_iltiqaa_vowel(
                entries, words[i], next_entries, next_word
            )
            flat.extend((e.chars, e.phonemes) for e in new_prev)
            all_word_entries[i + 1] = new_next

        elif action.action == "NON_MERGE":
            # Space suffix on last entry
            entries_out = list(entries)
            last = entries_out[-1]
            entries_out[-1] = ProtoEntry(
                chars=last.chars + " ",
                phonemes=last.phonemes,
                letter_indices=last.letter_indices,
            )
            flat.extend((e.chars, e.phonemes) for e in entries_out)

        else:  # "NORMAL"
            # Normal word boundary: space suffix on last entry
            entries_out = list(entries)
            last = entries_out[-1]
            entries_out[-1] = ProtoEntry(
                chars=last.chars + " ",
                phonemes=last.phonemes,
                letter_indices=last.letter_indices,
            )
            flat.extend((e.chars, e.phonemes) for e in entries_out)

        i += 1

    return flat


# =============================================================================
# Validation
# =============================================================================

# Valid madd graphemes for Rule 4
MADD_GRAPHEMES: Set[str] = {"ا", "و", "ي", "ى", "ٰ", "ۥ", "ۦ", "ۧ", "ٓ"}


def validate_rule_4(
    flat: List[Tuple[str, List[str]]], mapping: PhonemizationMapping
) -> List[str]:
    """
    Rule 4: Madd phoneme ↔ grapheme correspondence.

    Every long vowel phoneme (containing ':') must have a corresponding
    madd grapheme in the same entry's chars string, unless exempt.

    Exceptions (no grapheme required):
    - Special words: madd phonemes are part of letter name spelling
    - Allah (is_lafdh_jalalah): implicit dagger alef with no grapheme
    - Hamza + fathatan at stopping (is_hamza_fathatan): tanween becomes a:
    """
    violations = []

    # Build set of global phoneme indices that are exempt
    exempt_indices: Set[int] = set()
    phoneme_offset = 0

    for word in mapping.words:
        if word.is_special_word:
            # All phonemes in special words are exempt
            for i in range(len(word.phonemes)):
                exempt_indices.add(phoneme_offset + i)
        else:
            # Check madd_mappings for Allah and hamza+fathatan exceptions
            for mm in word.madd_mappings:
                if mm.is_lafdh_jalalah or mm.is_hamza_fathatan:
                    # phoneme_index can be -1 meaning "last phoneme"
                    if mm.phoneme_index == -1:
                        exempt_indices.add(phoneme_offset + len(word.phonemes) - 1)
                    else:
                        exempt_indices.add(phoneme_offset + mm.phoneme_index)

        phoneme_offset += len(word.phonemes)

    # Validate each flat entry
    current_idx = 0
    for entry_idx, (chars, phonemes) in enumerate(flat):
        # Count non-exempt madd phonemes
        non_exempt_madd = 0
        for i, ph in enumerate(phonemes):
            if ":" in ph and (current_idx + i) not in exempt_indices:
                non_exempt_madd += 1

        # Count madd graphemes (excluding spaces)
        madd_grapheme_count = sum(1 for c in chars if c in MADD_GRAPHEMES)

        if non_exempt_madd > madd_grapheme_count:
            violations.append(
                f"Rule 4: Entry {entry_idx} [{chars!r}] has {non_exempt_madd} "
                f"non-exempt madd phonemes but only {madd_grapheme_count} graphemes"
            )

        current_idx += len(phonemes)

    return violations


def validate_rule_9(
    flat: List[Tuple[str, List[str]]], mapping: PhonemizationMapping
) -> List[str]:
    """
    Rule 9: No orphaned silent letters.

    After merging, every entry's phonemes must come from at least one
    non-silent LetterMapping. An entry is "orphaned" if all its contributing
    letters were silent yet the entry has phonemes.

    Implementation: Uses phoneme tracking instead of character matching.
    For each phoneme in the flat output, we know it came from a specific
    letter in the original mapping. If an entry has phonemes, at least one
    of those phonemes must have come from a non-silent letter.

    Since we already validate phoneme sequence match, this rule is effectively
    guaranteed by the code structure. We implement it as a consistency check.
    """
    violations = []

    # Build a map from global phoneme index to whether its source letter was silent
    # A phoneme's source letter is determined by letter.phonemes
    phoneme_is_from_silent: List[bool] = []

    for word in mapping.words:
        for letter in word.letter_mappings:
            is_silent = len(letter.phonemes) == 0
            # Each phoneme from this letter maps to its silent status
            for _ in letter.phonemes:
                phoneme_is_from_silent.append(is_silent)

    # Validate each flat entry
    # If an entry has phonemes, at least one must be from a non-silent letter
    current_idx = 0
    for entry_idx, (chars, phonemes) in enumerate(flat):
        if phonemes:
            # Get the silent status of each phoneme in this entry
            entry_phoneme_indices = range(current_idx, current_idx + len(phonemes))

            # Check bounds (should always be valid if phoneme sequence matches)
            if current_idx + len(phonemes) <= len(phoneme_is_from_silent):
                all_from_silent = all(
                    phoneme_is_from_silent[i] for i in entry_phoneme_indices
                )
                if all_from_silent:
                    violations.append(
                        f"Rule 9: Entry {entry_idx} [{chars!r}] has phonemes {phonemes} "
                        f"but all phonemes came from silent letters"
                    )

        current_idx += len(phonemes)

    return violations


def validate(flat: List[Tuple[str, List[str]]], mapping: PhonemizationMapping) -> List[str]:
    """Run validation rules. Returns list of violation messages."""
    violations = []

    # Rule 1: No empty phonemes
    for i, (chars, phonemes) in enumerate(flat):
        if len(phonemes) == 0:
            violations.append(f"Rule 1: Entry {i} [{chars!r}] has empty phonemes")

    # Rule 2: Character coverage
    all_chars = "".join(chars.replace(" ", "") for chars, _ in flat)
    expected_chars = ""
    for word in mapping.words:
        for letter in word.letter_mappings:
            expected_chars += get_full_char(letter)

    if all_chars != expected_chars:
        violations.append(
            f"Rule 2: Character mismatch.\n"
            f"  Got:      {all_chars!r}\n"
            f"  Expected: {expected_chars!r}"
        )

    # Rule 4: Madd phoneme ↔ grapheme correspondence
    violations.extend(validate_rule_4(flat, mapping))

    # Rule 5: Space placement
    total_spaces = sum(chars.count(" ") for chars, _ in flat)
    expected_spaces = len(mapping.words) - 1
    if total_spaces != expected_spaces:
        violations.append(f"Rule 5: Expected {expected_spaces} spaces, got {total_spaces}")

    # Rule 9: No orphaned silent letters
    violations.extend(validate_rule_9(flat, mapping))

    # Phoneme sequence match
    flat_phonemes = []
    for _, phonemes in flat:
        flat_phonemes.extend(phonemes)

    if flat_phonemes != mapping.phoneme_sequence:
        violations.append(
            f"Phoneme mismatch: flat has {len(flat_phonemes)}, expected {len(mapping.phoneme_sequence)}"
        )
        # Show first difference
        for i, (got, exp) in enumerate(zip(flat_phonemes, mapping.phoneme_sequence)):
            if got != exp:
                violations.append(f"  First diff at index {i}: got {got!r}, expected {exp!r}")
                break

    return violations


# =============================================================================
# Output Formatting
# =============================================================================

def format_flat_mapping(flat: List[Tuple[str, List[str]]], as_json: bool = False) -> str:
    """Format the flat mapping for display."""
    if as_json:
        return json.dumps(flat, ensure_ascii=False, indent=2)

    lines = []
    for chars, phonemes in flat:
        lines.append(f'["{chars}", {phonemes}]')
    return "\n".join(lines)


def format_by_verse(
    flat: List[Tuple[str, List[str]]],
    mapping: PhonemizationMapping,
) -> str:
    """Format flat mapping grouped by verse.

    Tracks word boundaries by counting spaces in flat entries.
    Each space = word boundary, so we advance word index after each space.
    """
    # Build word index to verse mapping
    word_to_verse = {}
    for i, word in enumerate(mapping.words):
        verse = word.location.rsplit(":", 1)[0]  # e.g., "1:1" from "1:1:1"
        word_to_verse[i] = verse

    lines = []
    current_verse = None
    verse_entries: List[Tuple[str, List[str]]] = []
    word_idx = 0

    for chars, phonemes in flat:
        # Get verse for current word
        verse = word_to_verse.get(word_idx, current_verse or "unknown")

        if current_verse is None:
            current_verse = verse

        # Check if we've moved to a new verse
        if verse != current_verse:
            # Output previous verse
            lines.append(f"--- {current_verse} ---")
            for c, p in verse_entries:
                lines.append(f'["{c}", {p}]')
            lines.append("")
            verse_entries = []
            current_verse = verse

        # Add entry to current verse
        verse_entries.append((chars, phonemes))

        # Advance word index by number of spaces (word boundaries)
        word_idx += chars.count(" ")

    # Output last verse
    if verse_entries:
        lines.append(f"--- {current_verse} ---")
        for c, p in verse_entries:
            lines.append(f'["{c}", {p}]')

    return "\n".join(lines)


# =============================================================================
# Public API
# =============================================================================

@dataclass
class FlatMappingResult:
    """Result of flat mapping conversion for external use."""
    entries: List[Tuple[str, List[str]]]
    mapping: PhonemizationMapping
    ref: str = ""  # Optional, may be empty if mapping provided directly

    def to_list(self) -> List[Tuple[str, List[str]]]:
        """Return entries as a list of (chars, phonemes) tuples."""
        return self.entries

    def to_json(self, indent: int = 2) -> str:
        """Return entries as JSON string."""
        return json.dumps(self.entries, ensure_ascii=False, indent=indent)

    def to_dict(self) -> dict:
        """Return full result as dictionary."""
        return {
            "ref": self.ref,
            "entries": self.entries,
            "entry_count": len(self.entries),
            "word_count": len(self.mapping.words),
            "phoneme_count": len(self.mapping.phoneme_sequence),
        }

    def validate(self) -> List[str]:
        """Run validation rules. Returns list of violation messages (empty if valid)."""
        return validate(self.entries, self.mapping)

    def save(self, path: str, indent: int = 2) -> None:
        """Save entries to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=indent)

    def format_by_verse(self) -> str:
        """Format entries grouped by verse."""
        return format_by_verse(self.entries, self.mapping)


def get_flat_mapping(
    ref: str = "",
    mapping: Optional[PhonemizationMapping] = None,
    words: Optional[List[WordMapping]] = None,
    stops: Optional[List[str]] = None,
    validate_result: bool = False,
) -> FlatMappingResult:
    """
    Generate flat many-to-many letter-phoneme mapping for a Quran reference.

    Args:
        ref: Quran reference (e.g., "1" for Al-Fatiha, "2:255" for Ayat al-Kursi).
             Optional if mapping is provided directly.
        mapping: Pre-computed PhonemizationMapping. If provided, skips phonemization.
                 This is useful to avoid redundant phonemization when the mapping
                 is already available from a prior phonemize() call.
        words: Optional filtered word list. If None, uses mapping.words.
               Useful for generating flat mapping for a subset of words (e.g., when
               aligning a word range like "76:11:6-76:12:5" where the mapping
               contains full verses but only a subset of words are needed).
        stops: Stop types (default: ["verse"]). Only used if mapping is None.
        validate_result: If True, raises ValueError on validation failure

    Returns:
        FlatMappingResult with entries and metadata

    Raises:
        ValueError: If validate_result=True and validation fails, or if neither
                    ref nor mapping is provided.

    Example:
        >>> from scripts.prepare_mfa_mappings import get_flat_mapping
        >>> result = get_flat_mapping("1", stops=["verse"])
        >>> for chars, phonemes in result.entries[:3]:
        ...     print(f"{chars} -> {phonemes}")
        ب -> ['b', 'i']
        س -> ['s']
        م  -> ['m', 'i']

        # With pre-computed mapping (avoids redundant phonemization):
        >>> from core.phonemizer import Phonemizer
        >>> pm = Phonemizer()
        >>> phon_result = pm.phonemize("1:1")
        >>> mapping = phon_result.get_mapping()
        >>> result = get_flat_mapping(mapping=mapping)

        # With filtered words (for word range alignment):
        >>> filtered_words = [w for w in mapping.words if w.location >= "7:2:3"]
        >>> result = get_flat_mapping(mapping=mapping, words=filtered_words)
    """
    if mapping is None:
        # Phonemize only if mapping not provided
        if not ref:
            raise ValueError("Either ref or mapping must be provided")
        if stops is None:
            stops = ["verse"]
        phonemizer = Phonemizer()
        phon_result = phonemizer.phonemize(ref, stops=stops)
        mapping = phon_result.get_mapping()

    flat = build_flat_mapping(mapping, words=words)

    result = FlatMappingResult(entries=flat, mapping=mapping, ref=ref)

    if validate_result:
        violations = result.validate()
        if violations:
            raise ValueError(f"Validation failed:\n" + "\n".join(violations))

    return result


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Convert phonemizer output to flat MFA mappings"
    )
    parser.add_argument(
        "--ref",
        default="1",
        help="Reference to phonemize (default: chapter 1)"
    )
    parser.add_argument(
        "--stops",
        nargs="*",
        default=["verse"],
        help="Stop types (default: verse)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation rules"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--by-verse",
        action="store_true",
        help="Group output by verse"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (saves as JSON)"
    )
    args = parser.parse_args()

    # Get flat mapping
    result = get_flat_mapping(args.ref, stops=args.stops)

    # Save to file if requested
    if args.output:
        result.save(args.output)
        print(f"Saved to {args.output}")
    # Output to stdout
    elif args.by_verse:
        print(result.format_by_verse())
    else:
        print(format_flat_mapping(result.entries, as_json=args.json))

    # Validation
    if args.validate:
        print("\n--- Validation ---")
        violations = result.validate()
        if violations:
            for v in violations:
                print(f"VIOLATION: {v}")
            sys.exit(1)
        else:
            print("All validation rules passed.")


if __name__ == "__main__":
    main()
