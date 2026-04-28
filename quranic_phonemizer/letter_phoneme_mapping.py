"""
Letter-to-phoneme flat mapping for forced alignment.

Converts PhonemizationMapping into flat [chars, phonemes] entries where every
entry has at least one phoneme. Silent letters merge into adjacent entries.
Word boundaries are signaled by spaces in the chars field.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set

from .tajweed_rule import TajweedRule
from .mapping import (
    PhonemizationMapping,
    WordMapping,
    LetterMapping,
)


# =============================================================================
# Constants: TajweedRule-Based Merge Classification
# =============================================================================

# Silent letters that merge NEXT within-word
NEXT_MERGE_TAJWEED_RULES: Set[TajweedRule] = {
    TajweedRule.HAMZA_WASL_SILENT,
    TajweedRule.LAM_SHAMSIYAH,
    TajweedRule.ILTIQAA_SAKINAYN_TANWEEN,
    TajweedRule.SILENT_ILTIQAA_SAKINAYN,
}

# Silent at word-end → cross-word MERGE with next word's first letter
CROSS_WORD_MERGE_TAJWEED_RULES: Set[TajweedRule] = {
    TajweedRule.IDGHAM_GHUNNAH_NOON,
    TajweedRule.IDGHAM_BILA_GHUNNAH_NOON,
    TajweedRule.IDGHAM_MUTAJANISAYN_KAMIL,
    TajweedRule.IDGHAM_MUTAMATHILAYN,
    TajweedRule.IDGHAM_MUTAQARIBAYN,
}

# Within-word NEXT merge (same rules as cross-word but at non-final position)
WITHIN_WORD_NEXT_MERGE_TAJWEED_RULES: Set[TajweedRule] = {
    TajweedRule.IDGHAM_MUTAMATHILAYN,
    TajweedRule.IDGHAM_MUTAQARIBAYN,
    TajweedRule.IDGHAM_MUTAJANISAYN_KAMIL,
}

# Cross-word MERGE where BOTH letters have phonemes (combined into one entry)
CROSS_WORD_BOTH_MERGE_TAJWEED_RULES: Set[TajweedRule] = {
    TajweedRule.IDGHAM_SHAFAWI,
}

# Non-merge cross-word: last letter has phonemes, just add space suffix
CROSS_WORD_NON_MERGE_TAJWEED_RULES: Set[TajweedRule] = {
    TajweedRule.IKHFAA_NOON,
    TajweedRule.IQLAB_NOON,
    TajweedRule.IKHFAA_TANWEEN,
    TajweedRule.IQLAB_TANWEEN,
    TajweedRule.IKHFAA_SHAFAWI,
    TajweedRule.IDGHAM_GHUNNAH_TANWEEN,
    TajweedRule.IDGHAM_BILA_GHUNNAH_TANWEEN,
}

# Vowel letter characters
VOWEL_LETTER_CHARS: Set[str] = {"ا", "و", "ي", "ى"}

# Madd extension names eligible for splitting
MADD_EXTENSION_NAMES: Set[str] = {"DAGGER_ALEF", "MADDAH", "MINI_WAW", "MINI_YA_END"}

# Short vowel phonemes (for iltiqaa detection)
SHORT_VOWEL_PHONEMES: Set[str] = {"a", "aˤ", "u", "i"}

# Tanween diacritic names
TANWEEN_DIACRITICS: Set[str] = {"FATHATAN", "KASRATAN", "DAMMATAN"}

# Valid madd graphemes for Rule 4
MADD_GRAPHEMES: Set[str] = {"ا", "و", "ي", "ى", "ٰ", "ۥ", "ۦ", "ۧ", "ٓ"}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class MergeInfo:
    """Merge direction and rule for a letter."""
    direction: str  # "PREV", "NEXT", "CROSS_WORD_MERGE", "CROSS_WORD_BOTH", "CROSS_WORD_NON_MERGE", "NONE"
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

def _get_source_rules(letter: LetterMapping) -> Set[TajweedRule]:
    """Extract source TajweedRule enums from a letter's tajweed_rules."""
    return {t.rule for t in letter.tajweed_rules if t.is_source}


def is_madd_phoneme(ph: str) -> bool:
    """Check if a phoneme is a long vowel (madd)."""
    return ":" in ph


def get_full_char(letter: LetterMapping) -> str:
    """Build the full character string including extensions."""
    ext_chars = "".join(ext.char for ext in letter.extensions if ext.char)
    return letter.char + ext_chars


def is_silent(letter: LetterMapping) -> bool:
    """Check if a letter produces no phonemes."""
    return len(letter.phonemes) == 0


def get_merge_info(letter: LetterMapping, word: WordMapping, idx: int) -> MergeInfo:
    """Determine the merge direction for a letter."""
    rules = _get_source_rules(letter)
    is_last = idx == len(word.letter_mappings) - 1

    # Non-silent letters: check for cross-word effects
    if not is_silent(letter):
        if CROSS_WORD_BOTH_MERGE_TAJWEED_RULES & rules and is_last:
            rule = (CROSS_WORD_BOTH_MERGE_TAJWEED_RULES & rules).pop()
            return MergeInfo("CROSS_WORD_BOTH", rule.value)

        if CROSS_WORD_NON_MERGE_TAJWEED_RULES & rules and is_last:
            rule = (CROSS_WORD_NON_MERGE_TAJWEED_RULES & rules).pop()
            return MergeInfo("CROSS_WORD_NON_MERGE", rule.value)

        return MergeInfo("NONE")

    # Silent letter: determine merge direction

    # NEXT merge
    if NEXT_MERGE_TAJWEED_RULES & rules:
        rule = (NEXT_MERGE_TAJWEED_RULES & rules).pop()
        return MergeInfo("NEXT", rule.value)

    # Within-word vs cross-word idgham
    if WITHIN_WORD_NEXT_MERGE_TAJWEED_RULES & rules:
        rule = (WITHIN_WORD_NEXT_MERGE_TAJWEED_RULES & rules).pop()
        if is_last:
            return MergeInfo("CROSS_WORD_MERGE", rule.value)
        else:
            return MergeInfo("NEXT", rule.value)

    if CROSS_WORD_MERGE_TAJWEED_RULES & rules:
        rule = (CROSS_WORD_MERGE_TAJWEED_RULES & rules).pop()
        return MergeInfo("CROSS_WORD_MERGE", rule.value)

    # PREV merge: VOWEL_SILENT or any untagged silent letter
    if TajweedRule.VOWEL_SILENT in rules:
        return MergeInfo("PREV", "vowel_silent")

    # Fallback for silent letters with no recognized rule
    if letter.char in VOWEL_LETTER_CHARS:
        return MergeInfo("PREV", "vowel_lengthening_failure")

    return MergeInfo("PREV", "unknown_silent")


def should_split_extension(letter: LetterMapping, word: WordMapping) -> Optional[Tuple[str, str]]:
    """
    Check if a letter's madd extension should be split into its own entry.

    Returns (extension_chars, madd_phoneme) if split needed, else None.
    """
    madd_exts = [
        ext for ext in letter.extensions
        if ext.char and ext.name in MADD_EXTENSION_NAMES
    ]
    if not madd_exts:
        return None

    madd_phonemes = [ph for ph in letter.phonemes if is_madd_phoneme(ph)]
    if not madd_phonemes:
        return None

    # Alef maksura + dagger alef: reinforcing extension, don't split
    if letter.char == "ى" and any(ext.name == "DAGGER_ALEF" for ext in madd_exts):
        return None

    # Vowel letter where ALL phonemes are madd (it's a carrier, not consonant)
    if letter.char in VOWEL_LETTER_CHARS:
        non_madd = [ph for ph in letter.phonemes if not is_madd_phoneme(ph)]
        if not non_madd:
            return None

    ext_chars = "".join(ext.char for ext in madd_exts)
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

        split_result = should_split_extension(letter, word)
        if split_result:
            ext_char, madd_ph = split_result

            phonemes_copy = list(phonemes)
            for j in range(len(phonemes_copy) - 1, -1, -1):
                if is_madd_phoneme(phonemes_copy[j]):
                    madd_ph = phonemes_copy.pop(j)
                    break

            base_char = full_char.replace(ext_char, "", 1)

            entries.append(ProtoEntry(
                chars=base_char,
                phonemes=phonemes_copy,
                letter_indices=[i],
                merge_info=merge if not phonemes_copy else MergeInfo("NONE"),
            ))
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


def redistribute_waqf_tanween(entries: List[ProtoEntry], word: WordMapping) -> List[ProtoEntry]:
    """Move waqf_tanween long vowel from consonant to the following alef.

    When stopping with fathatan, the phonemizer places 'a:' on the consonant
    and the alef is silent. For alignment, the alef should carry the 'a:'
    (consistent with normal vowel lengthening where the vowel letter owns the
    long vowel phoneme).

    Derived from context: letter has tanween diacritic + word is stopping +
    next letter is silent alef/alef-maksura + last phoneme is long vowel.
    """
    result = list(entries)
    for i in range(len(result) - 1):
        entry = result[i]
        next_entry = result[i + 1]

        if not entry.letter_indices or not next_entry.letter_indices:
            continue

        letter = word.letter_mappings[entry.letter_indices[0]]
        next_letter = word.letter_mappings[next_entry.letter_indices[0]]

        if (letter.diacritic not in TANWEEN_DIACRITICS
                or not word.is_stopping
                or next_letter.char not in ("ا", "ى")
                or next_entry.phonemes
                or not entry.phonemes
                or ":" not in entry.phonemes[-1]):
            continue

        long_vowel = entry.phonemes[-1]
        result[i] = ProtoEntry(
            chars=entry.chars,
            phonemes=entry.phonemes[:-1],
            letter_indices=entry.letter_indices,
            merge_info=entry.merge_info,
        )
        result[i + 1] = ProtoEntry(
            chars=next_entry.chars,
            phonemes=[long_vowel],
            letter_indices=next_entry.letter_indices,
            merge_info=MergeInfo("NONE"),
        )
    return result


def build_special_word_entries(word: WordMapping) -> List[ProtoEntry]:
    """Build proto-entries for a special word (muqatta'at).

    Silent letters still need to be merged. Uses tajweed_rules for
    merge direction classification.
    """
    entries = []

    for i, letter in enumerate(word.letter_mappings):
        full_char = get_full_char(letter)
        phonemes = list(letter.phonemes)

        if not phonemes:
            rules = _get_source_rules(letter)

            if rules & NEXT_MERGE_TAJWEED_RULES or TajweedRule.HAMZA_WASL_SILENT in rules:
                entries.append(ProtoEntry(
                    chars=full_char,
                    phonemes=[],
                    letter_indices=[i],
                    merge_info=MergeInfo("NEXT", "special_word_silent"),
                ))
            else:
                entries.append(ProtoEntry(
                    chars=full_char,
                    phonemes=[],
                    letter_indices=[i],
                    merge_info=MergeInfo("PREV", "special_word_silent"),
                ))
        else:
            entries.append(ProtoEntry(chars=full_char, phonemes=phonemes, letter_indices=[i]))

    return merge_within_word(entries)


# =============================================================================
# Within-Word Merging
# =============================================================================

def merge_within_word(entries: List[ProtoEntry]) -> List[ProtoEntry]:
    """
    Merge silent entries within a word.

    Phase 1: NEXT merges (accumulate silent chars, prepend to next non-silent)
    Phase 2: PREV merges (append silent chars to previous entry)
    """
    # Phase 1: NEXT merges
    merged = []
    pending_next_chars = ""
    pending_next_indices: List[int] = []

    for entry in entries:
        mi = entry.merge_info
        if mi and mi.direction == "NEXT" and not entry.phonemes:
            pending_next_chars += entry.chars
            pending_next_indices.extend(entry.letter_indices)
        else:
            if pending_next_chars:
                entry = ProtoEntry(
                    chars=pending_next_chars + entry.chars,
                    phonemes=entry.phonemes,
                    letter_indices=pending_next_indices + entry.letter_indices,
                    merge_info=entry.merge_info,
                )
                pending_next_chars = ""
                pending_next_indices = []
            merged.append(entry)

    if pending_next_chars:
        merged.append(ProtoEntry(
            chars=pending_next_chars,
            phonemes=[],
            letter_indices=pending_next_indices,
        ))

    # Phase 2: PREV merges
    final = []
    for entry in merged:
        mi = entry.merge_info
        if mi and mi.direction == "PREV" and not entry.phonemes:
            if final:
                prev = final[-1]
                final[-1] = ProtoEntry(
                    chars=prev.chars + entry.chars,
                    phonemes=prev.phonemes,
                    letter_indices=prev.letter_indices + entry.letter_indices,
                    merge_info=prev.merge_info,
                )
            else:
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

    if mi and mi.direction == "CROSS_WORD_MERGE":
        return CrossWordAction("MERGE", mi.rule)

    if mi and mi.direction == "CROSS_WORD_BOTH":
        return CrossWordAction("BOTH_MERGE", mi.rule)

    if mi and mi.direction == "CROSS_WORD_NON_MERGE":
        return CrossWordAction("NON_MERGE", mi.rule)

    # Check for iltiqaa_vowel: vowel letter with demoted short vowel
    # chains cross-word into the next word. Search backwards since the
    # iltiqaa letter may not be the last (e.g., silent alef follows waw).
    for i in range(len(prev_word.letter_mappings) - 1, -1, -1):
        lm = prev_word.letter_mappings[i]
        if TajweedRule.SILENT_ILTIQAA_SAKINAYN in _get_source_rules(lm):
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
    """
    # Find the vowel letter that has SILENT_ILTIQAA_SAKINAYN
    iltiqaa_letter_idx = None
    for i in range(len(prev_word.letter_mappings) - 1, -1, -1):
        lm = prev_word.letter_mappings[i]
        if TajweedRule.SILENT_ILTIQAA_SAKINAYN in _get_source_rules(lm):
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

    # If the vowel entry is at index 0 (no preceding consonant to receive
    # the demoted phoneme — e.g., consonant was consumed by a prior cross-word
    # merge), fall back to normal word boundary (space suffix).
    if vowel_entry_idx == 0:
        result_prev = list(prev_entries)
        last = result_prev[-1]
        result_prev[-1] = ProtoEntry(
            chars=last.chars + " ",
            phonemes=last.phonemes,
            letter_indices=last.letter_indices,
        )
        return result_prev, next_entries

    new_prev = list(prev_entries)

    iltiqaa_letter = prev_word.letter_mappings[iltiqaa_letter_idx]
    vowel_entry = new_prev[vowel_entry_idx]

    if iltiqaa_letter.phonemes:
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
                phonemes=[],
                letter_indices=vowel_entry.letter_indices,
                merge_info=MergeInfo("CROSS_WORD_SILENT", "iltiqaa_vowel"),
            )

    # Collect trailing silent entries from prev_entries starting at vowel_entry_idx
    silent_chain_chars = ""
    merge_start_idx = vowel_entry_idx
    for eidx in range(vowel_entry_idx, len(new_prev)):
        entry = new_prev[eidx]
        if not entry.phonemes:
            silent_chain_chars += entry.chars
        else:
            merge_start_idx = eidx
            break
    else:
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
        new_next = next_entries

    new_prev = new_prev[:vowel_entry_idx]

    return new_prev, new_next


# =============================================================================
# Main Conversion
# =============================================================================

def build_letter_phoneme_mapping(
    mapping: PhonemizationMapping,
    words: Optional[List[WordMapping]] = None,
) -> List[Tuple[str, List[str]]]:
    """Convert PhonemizationMapping to flat [chars, phonemes] sequence."""
    if words is None:
        words = mapping.words

    # Phase 1: Build proto-entries per word
    all_word_entries: List[List[ProtoEntry]] = []
    for word in words:
        if word.is_special_word:
            entries = build_special_word_entries(word)
        else:
            entries = build_word_proto_entries(word)
            entries = redistribute_waqf_tanween(entries, word)
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
            flat.extend((e.chars, e.phonemes) for e in entries)

        elif action.action == "MERGE":
            last = entries[-1]
            first_next = next_entries[0]
            merged_chars = last.chars + " " + first_next.chars
            merged_phonemes = first_next.phonemes

            flat.extend((e.chars, e.phonemes) for e in entries[:-1])
            flat.append((merged_chars, merged_phonemes))
            all_word_entries[i + 1] = list(next_entries[1:])

        elif action.action == "BOTH_MERGE":
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
            entries_out = list(entries)
            last = entries_out[-1]
            entries_out[-1] = ProtoEntry(
                chars=last.chars + " ",
                phonemes=last.phonemes,
                letter_indices=last.letter_indices,
            )
            flat.extend((e.chars, e.phonemes) for e in entries_out)

        else:  # "NORMAL"
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

def validate_rule_4(
    flat: List[Tuple[str, List[str]]], mapping: PhonemizationMapping
) -> List[str]:
    """Rule 4: Madd phoneme <-> grapheme correspondence."""
    violations = []

    exempt_indices: Set[int] = set()
    phoneme_offset = 0

    for word in mapping.words:
        if word.is_special_word:
            for i in range(len(word.phonemes)):
                exempt_indices.add(phoneme_offset + i)
        else:
            for mm in word.madd_mappings:
                if mm.is_lafdh_jalalah or mm.is_hamza_fathatan:
                    if mm.phoneme_index == -1:
                        exempt_indices.add(phoneme_offset + len(word.phonemes) - 1)
                    else:
                        exempt_indices.add(phoneme_offset + mm.phoneme_index)

        phoneme_offset += len(word.phonemes)

    current_idx = 0
    for entry_idx, (chars, phonemes) in enumerate(flat):
        non_exempt_madd = 0
        for i, ph in enumerate(phonemes):
            if ":" in ph and (current_idx + i) not in exempt_indices:
                non_exempt_madd += 1

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
    """Rule 9: No orphaned silent letters."""
    violations = []

    phoneme_is_from_silent: List[bool] = []

    for word in mapping.words:
        for letter in word.letter_mappings:
            is_silent_letter = len(letter.phonemes) == 0
            for _ in letter.phonemes:
                phoneme_is_from_silent.append(is_silent_letter)

    current_idx = 0
    for entry_idx, (chars, phonemes) in enumerate(flat):
        if phonemes:
            entry_phoneme_indices = range(current_idx, current_idx + len(phonemes))

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

    # Rule 4: Madd phoneme <-> grapheme correspondence
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
        for i, (got, exp) in enumerate(zip(flat_phonemes, mapping.phoneme_sequence)):
            if got != exp:
                violations.append(f"  First diff at index {i}: got {got!r}, expected {exp!r}")
                break

    return violations


# =============================================================================
# Public API
# =============================================================================

@dataclass
class FlatMappingResult:
    """Result of flat mapping conversion."""
    entries: List[Tuple[str, List[str]]]
    mapping: PhonemizationMapping
    ref: str = ""

    def to_list(self) -> List[Tuple[str, List[str]]]:
        return self.entries

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.entries, ensure_ascii=False, indent=indent)

    def to_dict(self) -> dict:
        return {
            "ref": self.ref,
            "entries": self.entries,
            "entry_count": len(self.entries),
            "word_count": len(self.mapping.words),
            "phoneme_count": len(self.mapping.phoneme_sequence),
        }

    def validate(self) -> List[str]:
        return validate(self.entries, self.mapping)

    def save(self, path: str, indent: int = 2) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=indent)

    def format_by_verse(self) -> str:
        return format_by_verse(self.entries, self.mapping)


def format_by_verse(
    flat: List[Tuple[str, List[str]]],
    mapping: PhonemizationMapping,
) -> str:
    """Format flat mapping grouped by verse."""
    word_to_verse = {}
    for i, word in enumerate(mapping.words):
        verse = word.location.rsplit(":", 1)[0]
        word_to_verse[i] = verse

    lines = []
    current_verse = None
    verse_entries: List[Tuple[str, List[str]]] = []
    word_idx = 0

    for chars, phonemes in flat:
        verse = word_to_verse.get(word_idx, current_verse or "unknown")

        if current_verse is None:
            current_verse = verse

        if verse != current_verse:
            lines.append(f"--- {current_verse} ---")
            for c, p in verse_entries:
                lines.append(f'["{c}", {p}]')
            lines.append("")
            verse_entries = []
            current_verse = verse

        verse_entries.append((chars, phonemes))
        word_idx += chars.count(" ")

    if verse_entries:
        lines.append(f"--- {current_verse} ---")
        for c, p in verse_entries:
            lines.append(f'["{c}", {p}]')

    return "\n".join(lines)
