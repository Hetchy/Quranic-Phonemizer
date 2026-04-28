"""
Phonetic text rendering — converts phonemized words into display text
as it would be recited (with stopping transforms, hamza wasl, etc.).

Operates purely on WordRecord / LetterRecord snapshots; never touches the
live Word/LetterSymbol graph.
"""

from __future__ import annotations

import re
from typing import List, Optional, TYPE_CHECKING

from .parser import load_symbol_mappings
from .specials import get_display_text
from .symbols.letters.lam import Lam
from .tajweed_rule import TajweedRule

if TYPE_CHECKING:
    from .records import LetterRecord, WordRecord

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

# Hamza wasl TajweedRule → replacement char + haraka char
_HAMZA_WASL_RULES = {
    TajweedRule.HAMZA_WASL_FATHA: (_char("letters", "HAMZA_ABOVE_ALEF"), _char("diacritics", "FATHA")),
    TajweedRule.HAMZA_WASL_DAMMA: (_char("letters", "HAMZA_ABOVE_ALEF"), _char("diacritics", "DAMMA")),
    TajweedRule.HAMZA_WASL_KASRA: (_char("letters", "HAMZA_BELOW_ALEF"), _char("diacritics", "KASRA")),
}

# Map diacritic names → chars (for assembling output)
_DIAC_CHARS = {name: entry["char"] for name, entry in _DIACRITICS.items()}

_ARABIC_DIGITS = {
    '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
    '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
}


_RULE_TAG_RE = re.compile(r"</?rule[^>]*?>")


def build_phonetic_text(
    records: List["WordRecord"],
    word_sep: str = " ",
    verse_sep: str = "\n",
) -> str:
    parts: list[str] = []
    prev_verse: Optional[str] = None

    for rec in records:
        cur_verse = str(rec.location.ayah_num)
        if prev_verse is not None and cur_verse != prev_verse:
            arabic_num = "".join(_ARABIC_DIGITS[d] for d in prev_verse)
            parts.append(f" {arabic_num} ")
            parts.append(verse_sep)
        elif prev_verse is not None:
            parts.append(word_sep)
        parts.append(build_word_phonetic_text(rec))
        prev_verse = cur_verse

    # Final verse marker
    if prev_verse is not None:
        arabic_num = "".join(_ARABIC_DIGITS[d] for d in prev_verse)
        parts.append(f" {arabic_num} ")

    return "".join(parts)


def build_word_phonetic_text(rec: "WordRecord") -> str:
    # 1. Huroof muqattaat short-circuit
    display = get_display_text(rec.location.location_key)
    if display is not None:
        return _wrap_word(rec, display)

    letter_records = rec.letter_records
    if not letter_records:
        return ""

    # Pre-compute Allah detection
    allah_lam_idx = _get_allah_lam_index(letter_records)

    n = len(letter_records)
    segments: list[str] = []
    for idx, lr in enumerate(letter_records):
        seg = _build_letter_segment(lr, idx, n, rec, allah_lam_idx)
        if seg is not None:
            segments.append(seg)

    return _wrap_word(rec, "".join(segments))


def _wrap_word(rec: "WordRecord", core: str) -> str:
    """Prepend leading symbols and append stop sign to the core word text."""
    parts: list[str] = []

    # Leading symbols (e.g. rub el hizb ۞) from rec.text before first letter
    if rec.text and rec.letter_records:
        clean = _RULE_TAG_RE.sub("", rec.text)
        first_char = rec.letter_records[0].char
        idx = clean.find(first_char)
        if idx > 0:
            parts.append(clean[:idx])

    parts.append(core)

    # Trailing stop sign
    if rec.stop_sign is not None:
        parts.append(" ")
        parts.append(rec.stop_sign[0])

    return "".join(parts)


def _build_letter_segment(
    lr: "LetterRecord",
    idx: int,
    n_letters: int,
    rec: "WordRecord",
    allah_lam_idx: int,
) -> Optional[str]:
    is_first = idx == 0
    is_last = idx == n_letters - 1
    starting = rec.is_starting
    stopping = rec.is_stopping
    location_key = rec.location.location_key

    # F. Location-specific skip (removed — now handled by letter_overrides)

    letter_char = lr.char
    shaddah = lr.has_shaddah
    diac_name = lr.diacritic                       # already a name string or None
    extensions = lr.extensions or ()
    insert_alef = False

    hamza_wasl_char = _char("letters", "HAMZA_WASL")
    alef_char = _char("letters", "ALEF")
    alef_maksura_char = _char("letters", "ALEF_MAKSURA")
    taa_marbuta_char = _char("letters", "TAA_MARBUTA")
    hamza_char = _char("letters", "HAMZA")

    # A. Hamza wasl (starting + first letter + char == ٱ)
    if starting and is_first and letter_char == hamza_wasl_char:
        source_rules = {tag.rule for tag in lr.tajweed_rules if tag.is_source}
        for rule, (repl_char, haraka) in _HAMZA_WASL_RULES.items():
            if rule in source_rules:
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
        next_lr = rec.letter_records[idx + 1]
        if diac_name == "FATHATAN" and next_lr.char in (alef_char, alef_maksura_char):
            diac_name = "FATHA"

    # E. Penultimate sukun before SILENT_ALWAYS
    if stopping and not is_last:
        next_lr = rec.letter_records[idx + 1]
        next_is_last = (idx + 1) == (n_letters - 1)
        if next_is_last and next_lr.has_symbol("SILENT_ALWAYS"):
            if diac_name in _HARAKA_NAMES:
                diac_name = "SUKUN"

    # F. Location-specific diacritic overrides (removed — now handled by letter_overrides)

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


def _is_allah_word(letter_records: List["LetterRecord"]) -> bool:
    letter_chars = [lr.char for lr in letter_records]
    for pattern_letters in Lam.ALLAH_LETTER_PATTERNS.values():
        if letter_chars == list(pattern_letters):
            return True
    return False


def _get_allah_lam_index(letter_records: List["LetterRecord"]) -> int:
    """Find the index of the second lam (the one with shaddah) in an Allah word.
    Returns -1 if not an Allah word."""
    if not _is_allah_word(letter_records):
        return -1
    lam_char = _char("letters", "LAM")
    for i, lr in enumerate(letter_records):
        if lr.char == lam_char and lr.has_shaddah:
            return i
    return -1
