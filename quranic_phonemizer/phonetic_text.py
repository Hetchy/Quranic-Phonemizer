"""
Phonetic text rendering — converts phonemized Words into display text
as it would be recited (with stopping transforms, hamza wasl, etc.).

All transforms are read-only: no Word/LetterSymbol objects are mutated.
"""

from __future__ import annotations

import re
from typing import List, Optional, TYPE_CHECKING

from .parser import load_symbol_mappings
from .specials import (
    get_display_text,
    should_skip_letter_for_stopping,
    get_stopping_diacritic_override,
)
from .symbols.letters.lam import Lam

if TYPE_CHECKING:
    from .word import Word
    from .symbols.letters.letter import LetterSymbol

# ── Load chars from YAML (single source of truth) ─────────────────
_mappings = load_symbol_mappings()


def _char(category: str, name: str) -> str:
    return _mappings[category][name]["char"]


# Letters
_LETTERS = _mappings["letters"]
_DIACRITICS = _mappings["diacritics"]
_EXTENSIONS = _mappings["extensions"]
_OTHER = _mappings["other"]

# Extension chars to strip when stopping on last letter
_STOP_STRIP_EXTENSIONS = {
    _char("extensions", "MINI_WAW"),
    _char("extensions", "MINI_YA_END"),
    _char("extensions", "MADDAH"),
}

# Diacritic names that count as harakaat (replaced by sukun when stopping)
_HARAKA_NAMES = {"FATHA", "DAMMA", "KASRA", "FATHATAN", "DAMMATAN", "KASRATAN"}

# Hamza wasl rule → replacement char + haraka char
_HAMZA_WASL_RULES = {
    "hamza_wasl_fatha": (_char("letters", "HAMZA_ABOVE_ALEF"), _char("diacritics", "FATHA")),
    "hamza_wasl_damma": (_char("letters", "HAMZA_ABOVE_ALEF"), _char("diacritics", "DAMMA")),
    "hamza_wasl_kasra": (_char("letters", "HAMZA_BELOW_ALEF"), _char("diacritics", "KASRA")),
}

# Map diacritic names → chars (for assembling output)
_DIAC_CHARS = {name: entry["char"] for name, entry in _DIACRITICS.items()}

_ARABIC_DIGITS = {
    '0': '\u0660', '1': '\u0661', '2': '\u0662', '3': '\u0663', '4': '\u0664',
    '5': '\u0665', '6': '\u0666', '7': '\u0667', '8': '\u0668', '9': '\u0669',
}

_RULE_TAG_RE = re.compile(r"</?rule[^>]*?>")


def build_phonetic_text(
    words: List["Word"],
    word_sep: str = " ",
    verse_sep: str = "\n",
) -> str:
    parts: list[str] = []
    prev_verse: Optional[str] = None

    for word in words:
        cur_verse = str(word.location.ayah_num)
        if prev_verse is not None and cur_verse != prev_verse:
            arabic_num = "".join(_ARABIC_DIGITS[d] for d in prev_verse)
            parts.append(f" {arabic_num} ")
            parts.append(verse_sep)
        elif prev_verse is not None:
            parts.append(word_sep)
        parts.append(build_word_phonetic_text(word))
        prev_verse = cur_verse

    # Final verse marker
    if prev_verse is not None:
        arabic_num = "".join(_ARABIC_DIGITS[d] for d in prev_verse)
        parts.append(f" {arabic_num} ")

    return "".join(parts)


def build_word_phonetic_text(word: "Word") -> str:
    # 1. Huroof muqattaat short-circuit
    display = get_display_text(word.location.location_key)
    if display is not None:
        return _wrap_word(word, display)

    letters = word.letters
    if not letters:
        return ""

    # Pre-compute Allah detection
    allah_lam_idx = _get_allah_lam_index(letters)

    n = len(letters)
    segments: list[str] = []
    for idx, lt in enumerate(letters):
        seg = _build_letter_segment(lt, idx, n, word, allah_lam_idx)
        if seg is not None:
            segments.append(seg)

    return _wrap_word(word, "".join(segments))


def _wrap_word(word: "Word", core: str) -> str:
    """Prepend leading symbols and append stop sign to the core word text."""
    parts: list[str] = []

    # Leading symbols (e.g. rub el hizb ۞) from word.text before first letter
    if word.text and word.letters:
        clean = _RULE_TAG_RE.sub("", word.text)
        first_char = word.letters[0].char
        idx = clean.find(first_char)
        if idx > 0:
            parts.append(clean[:idx])

    parts.append(core)

    # Trailing stop sign
    if word.stop_sign:
        parts.append(" ")
        parts.append(word.stop_sign.char)

    return "".join(parts)


def _build_letter_segment(
    lt: "LetterSymbol",
    idx: int,
    n_letters: int,
    word: "Word",
    allah_lam_idx: int,
) -> Optional[str]:
    is_first = idx == 0
    is_last = idx == n_letters - 1
    starting = word.is_starting
    stopping = word.is_stopping
    location_key = word.location.location_key

    # F. Location-specific skip
    if stopping and should_skip_letter_for_stopping(location_key, lt.char):
        return None

    letter_char = lt.char
    shaddah = lt.has_shaddah
    diac_name = lt.diacritic.name if lt.diacritic else None
    extensions = lt.extensions
    insert_alef = False

    hamza_wasl_char = _char("letters", "HAMZA_WASL")
    alef_char = _char("letters", "ALEF")
    alef_maksura_char = _char("letters", "ALEF_MAKSURA")
    taa_marbuta_char = _char("letters", "TAA_MARBUTA")
    hamza_char = _char("letters", "HAMZA")

    # A. Hamza wasl (starting + first letter + char == ٱ)
    if starting and is_first and letter_char == hamza_wasl_char:
        rules = lt.rules
        for rule_name, (repl_char, haraka) in _HAMZA_WASL_RULES.items():
            if rule_name in rules:
                return repl_char + haraka
        # Fallback: fatha (al- definite article pattern)
        return _char("letters", "HAMZA_ABOVE_ALEF") + _char("diacritics", "FATHA")

    # B. Starting shaddah removal
    if starting and is_first:
        shaddah = False

    # C. Stopping last-letter transforms
    if stopping and is_last:
        # C0: Deleted yaa/waw — mini yaa on non-haa letter (e.g. alef maksura)
        #     is a deleted root letter, not silah → skip all stopping transforms
        ha_char = _char("letters", "HA")
        has_mini_ext = any(e.char in _STOP_STRIP_EXTENSIONS for e in extensions)
        if has_mini_ext and letter_char != ha_char:
            pass  # keep letter as-is (kasra + mini yaa preserved)
        else:
            # C1: Remove mini extensions (silah on haa)
            extensions = [e for e in extensions if e.char not in _STOP_STRIP_EXTENSIONS]

            # C2: Taa marbuta → haa + sukun
            if letter_char == taa_marbuta_char:
                letter_char = _char("letters", "HA")
                diac_name = "SUKUN"

            # C3: Hamza + fathatan → fatha + insert alef (madd iwad for hamza)
            elif letter_char == hamza_char and diac_name == "FATHATAN":
                diac_name = "FATHA"
                insert_alef = True

            # C4: General haraka/tanween → sukun
            elif diac_name in _HARAKA_NAMES:
                if letter_char in (alef_char, alef_maksura_char):
                    diac_name = None
                else:
                    diac_name = "SUKUN"

    # D. Madd iwad — tanween+alef pattern (second-to-last letter)
    if stopping and not is_last and idx == n_letters - 2:
        next_lt = word.letters[idx + 1]
        if diac_name == "FATHATAN" and next_lt.char in (alef_char, alef_maksura_char):
            diac_name = "FATHA"

    # E. Penultimate sukun before SILENT_ALWAYS
    if stopping and not is_last:
        next_lt = word.letters[idx + 1]
        if next_lt.is_last and next_lt.has_symbol("SILENT_ALWAYS"):
            if diac_name in _HARAKA_NAMES:
                diac_name = "SUKUN"

    # F. Location-specific diacritic overrides
    if stopping:
        has_override, new_diac = get_stopping_diacritic_override(location_key, idx)
        if has_override:
            diac_name = new_diac

    # G. Allah dagger alef
    allah_extra = ""
    if allah_lam_idx >= 0 and idx == allah_lam_idx:
        allah_extra = _char("other", "TATWEEL") + _char("extensions", "DAGGER_ALEF")

    # 3. Assemble segment
    parts = [letter_char]
    if shaddah:
        parts.append(_char("other", "SHADDA"))
    if diac_name:
        diac_char = _DIAC_CHARS.get(diac_name)
        if diac_char:
            parts.append(diac_char)
    for ext in extensions:
        if ext.char:
            parts.append(ext.char)
    if allah_extra:
        parts.append(allah_extra)
    if insert_alef:
        parts.append(alef_char)

    return "".join(parts)


def _is_allah_word(letters: List["LetterSymbol"]) -> bool:
    letter_chars = [lt.char for lt in letters]
    for pattern_letters in Lam.ALLAH_LETTER_PATTERNS.values():
        if letter_chars == pattern_letters:
            return True
    return False


def _get_allah_lam_index(letters: List["LetterSymbol"]) -> int:
    """Find the index of the second lam (the one with shaddah) in an Allah word.
    Returns -1 if not an Allah word."""
    if not _is_allah_word(letters):
        return -1
    lam_char = _char("letters", "LAM")
    for i, lt in enumerate(letters):
        if lt.char == lam_char and lt.has_shaddah:
            return i
    return -1
