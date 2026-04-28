"""Immutable records that carry exactly the data the result + mapping methods
need, freed from the live Word/LetterSymbol object graph.

After phonemization, ``Phonemizer`` retains only a list of ``WordRecord``s
inside ``PhonemizeResult``; the heavy ``Word``/``LetterSymbol`` objects are
released. All mapping/output paths read from these records.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .location import Location
from .mapping import (
    ExtensionSymbolMapping,
    LetterMapping,
    OtherSymbolMapping,
    WordMapping,
)
from .tajweed_rule import TajweedRuleTag


_RULE_TAG_RE = re.compile(r"</?rule[^>]*?>")

# Quranic symbol characters (stop signs, rub el hizb, etc.) — used by
# leading-symbol extraction. Must match the historic set used by
# Word.build_mapping.
_QURANIC_SYMBOLS = {
    "ۖ": "PREFERRED_CONTINUE",
    "ۗ": "PREFERRED_STOP",
    "ۘ": "COMPULSORY_STOP",
    "ۙ": "PROHIBITED_STOP",
    "ۚ": "OPTIONAL_STOP",
    "ۛ": "EITHER_STOP",
    "ۜ": "SMALL_HIGH_SEEN",
    "۝": "END_OF_AYAH",
    "۞": "START_OF_RUB_EL_HIZB",
    "۟": "SMALL_HIGH_ROUNDED_ZERO",
    "۠": "SMALL_HIGH_UPRIGHT_RECT",
    "۩": "PLACE_OF_SAJDAH",
}
_DIACRITIC_SKIP = " ًٌٍَُِّْ"


@dataclass(slots=True)
class LetterRecord:
    """Per-letter snapshot. Captures everything mapping/output methods read."""

    index: int
    char: str
    phonemes: List[str]
    diacritic: Optional[str]                    # diacritic.name, e.g. "FATHA"
    has_shaddah: bool
    extensions: List[ExtensionSymbolMapping]    # already in mapping-record shape
    other_symbols: List[OtherSymbolMapping]
    tajweed_rules: List[TajweedRuleTag]         # interned flyweights from live phase

    def has_symbol(self, name: str) -> bool:
        return any(s.name == name for s in self.other_symbols)


@dataclass(slots=True)
class WordRecord:
    """Per-word snapshot, taken once the live Word has finished phonemizing
    and its neighbours are settled."""

    location: Location
    text: str                                    # raw text, with rule tags if any
    letter_records: List[LetterRecord]
    phonemes: List[str]                          # flat phonemes for this word
    is_starting: bool
    is_stopping: bool
    is_special_word: bool
    stop_sign: Optional[Tuple[str, str]]         # (char, name) or None
    leading_symbols: List[OtherSymbolMapping]


def _extract_leading_symbols(text: str, first_letter_char: str) -> List[OtherSymbolMapping]:
    """Mirror Word.build_mapping's leading-symbol scan: find Quranic symbols
    that appear before the first letter character in the raw word text."""
    leading: List[OtherSymbolMapping] = []
    if not text or not first_letter_char:
        return leading
    text_before_first_letter = text.split(first_letter_char)[0]
    for char in text_before_first_letter:
        if char in _DIACRITIC_SKIP:
            continue
        sym_name = _QURANIC_SYMBOLS.get(char)
        if sym_name is not None:
            leading.append(OtherSymbolMapping(char=char, name=sym_name))
    return leading


def extract_record(word) -> WordRecord:
    """Snapshot a fully-phonemized + override-applied Word into a record.

    The Word is expected to be in its final state (apply_phoneme_overrides
    already run) and its neighbours settled (no future cross-word write
    will reach into its letters). The driver in Phonemizer.phonemize is
    responsible for calling this only at that point.
    """
    letter_records: List[LetterRecord] = []
    for i, lt in enumerate(word.letters):
        ext_list = lt.extensions or ()
        other_list = lt.other_symbols or ()
        tajweed_list = lt._tajweed_rules or ()
        letter_records.append(
            LetterRecord(
                index=i,
                char=lt.char,
                phonemes=list(lt.phonemes) if lt.phonemes else [],
                diacritic=lt.diacritic.name if lt.diacritic else None,
                has_shaddah=lt.has_shaddah,
                extensions=[
                    ExtensionSymbolMapping(char=e.char, name=e.name)
                    for e in ext_list
                ],
                other_symbols=[
                    OtherSymbolMapping(char=s.char, name=s.name)
                    for s in other_list
                ],
                tajweed_rules=list(tajweed_list),
            )
        )

    # Flat phonemes for the whole word. Mirrors Word.get_phonemes().
    if word.phonemes:                                   # special-word preset path
        flat: List[str] = list(word.phonemes)
    else:
        flat = []
        for lr in letter_records:
            for p in lr.phonemes:
                if p:
                    flat.append(p)

    first_char = word.letters[0].char if word.letters else ""
    leading = _extract_leading_symbols(word.text, first_char)

    stop_sign: Optional[Tuple[str, str]] = None
    if word.stop_sign is not None:
        stop_sign = (word.stop_sign.char, word.stop_sign.name)

    return WordRecord(
        location=word.location,
        text=word.text,
        letter_records=letter_records,
        phonemes=flat,
        is_starting=word.is_starting,
        is_stopping=word.is_stopping,
        is_special_word=word.phonemes is not None,
        stop_sign=stop_sign,
        leading_symbols=leading,
    )


def build_word_mapping_from_record(rec: WordRecord) -> WordMapping:
    """Construct a WordMapping (the existing mapping-record dataclass) from
    a WordRecord. Replaces Word.build_mapping().
    """
    letter_mappings = [
        LetterMapping(
            index=lr.index,
            char=lr.char,
            phonemes=list(lr.phonemes),
            diacritic=lr.diacritic,
            has_shaddah=lr.has_shaddah,
            extensions=list(lr.extensions),
            other_symbols=list(lr.other_symbols),
            tajweed_rules=list(lr.tajweed_rules),
        )
        for lr in rec.letter_records
    ]
    trailing: List[OtherSymbolMapping] = []
    if rec.stop_sign is not None:
        trailing.append(
            OtherSymbolMapping(char=rec.stop_sign[0], name=rec.stop_sign[1])
        )
    clean_text = _RULE_TAG_RE.sub("", rec.text)
    return WordMapping(
        location=rec.location.location_key,
        text=clean_text,
        phonemes=list(rec.phonemes),
        letter_mappings=letter_mappings,
        leading_symbols=list(rec.leading_symbols),
        trailing_symbols=trailing,
        is_special_word=rec.is_special_word,
        is_starting=rec.is_starting,
        is_stopping=rec.is_stopping,
    )
