"""
Letter-to-phoneme mapping schema for reverse mapping support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .tajweed_rule import TajweedRuleTag


@dataclass
class ExtensionSymbolMapping:
    """Extension symbol (dagger alef, maddah, etc.) attached to a letter."""
    char: str
    name: str


@dataclass
class OtherSymbolMapping:
    """Other symbol (tatweel, stop signs, etc.) attached to a letter or word."""
    char: str
    name: str


@dataclass
class LetterMapping:
    index: int
    char: str
    phonemes: List[str]

    diacritic: Optional[str] = None  # Just the name, e.g. "FATHA"
    has_shaddah: bool = False

    # Extension symbols (dagger alef, maddah, hamza above/below, etc.)
    extensions: List[ExtensionSymbolMapping] = field(default_factory=list)

    # Other symbols (tatweel, stop signs, etc.) attached to this letter
    other_symbols: List[OtherSymbolMapping] = field(default_factory=list)

    # Structured tajweed rule tags.
    tajweed_rules: List[TajweedRuleTag] = field(default_factory=list)

@dataclass
class MaddMapping:
    """Mapping for a single madd (long vowel) occurrence."""
    phoneme_index: int          # Index in word's phoneme list
    phoneme: str                # The long vowel phoneme (e.g., "a:", "aˤ:")
    letter_index: int           # Letter that produces or carries this madd

    # Grapheme info
    vowel_grapheme: str         # Base vowel: ا, و, ي, ى, ٰ, ۥ, ۦ, ۧ
    has_maddah: bool = False    # Whether ٓ is also present

    # If vowel_grapheme is an extension, store its index
    extension_index: Optional[int] = None

    # Madd classification (populated later by rule detection)
    madd_type: Optional[str] = None

    # Special case: Allah (لفظ الجلالة) - implicit dagger alef
    is_lafdh_jalalah: bool = False

    # Special case: hamza + fathatan at end - becomes hamza + fatha + alef when stopping
    is_hamza_fathatan: bool = False


@dataclass
class WordMapping:
    location: str
    text: str
    phonemes: List[str]
    letter_mappings: List[LetterMapping]

    # Word-level symbols that appear before/after all letters
    leading_symbols: List[OtherSymbolMapping] = field(default_factory=list)
    trailing_symbols: List[OtherSymbolMapping] = field(default_factory=list)

    is_special_word: bool = False
    is_starting: bool = False
    is_stopping: bool = False

    # Madd mappings for this word
    madd_mappings: List[MaddMapping] = field(default_factory=list)


@dataclass
class AlignmentEntry:
    phoneme_index: int
    phoneme: str
    word_index: int
    letter_index: int
    source_char: str


@dataclass
class PhonemizationMapping:
    ref: str
    text: str
    words: List[WordMapping]
    phoneme_sequence: List[str]
    alignment: List[AlignmentEntry]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ref": self.ref,
            "text": self.text,
            "words": [
                {
                    "location": w.location,
                    "text": w.text,
                    "phonemes": w.phonemes,
                    "letter_mappings": [
                        {k: v for k, v in {
                            "index": lm.index,
                            "char": lm.char,
                            "phonemes": lm.phonemes,
                            "diacritic": lm.diacritic,
                            "has_shaddah": lm.has_shaddah if lm.has_shaddah else None,
                        }.items() if v is not None}
                        for lm in w.letter_mappings
                    ],
                    **({"is_special_word": True} if w.is_special_word else {}),
                    **({"is_starting": True} if w.is_starting else {}),
                    **({"is_stopping": True} if w.is_stopping else {}),
                    **({"madd_mappings": [
                        {k: v for k, v in {
                            "phoneme_index": mm.phoneme_index,
                            "phoneme": mm.phoneme,
                            "letter_index": mm.letter_index,
                            "vowel_grapheme": mm.vowel_grapheme,
                            "has_maddah": mm.has_maddah if mm.has_maddah else None,
                            "extension_index": mm.extension_index,
                            "madd_type": mm.madd_type,
                        }.items() if v is not None}
                        for mm in w.madd_mappings
                    ]} if w.madd_mappings else {}),
                }
                for w in self.words
            ],
            "phoneme_sequence": self.phoneme_sequence,
            "alignment": [
                {
                    "phoneme_index": a.phoneme_index,
                    "phoneme": a.phoneme,
                    "word_index": a.word_index,
                    "letter_index": a.letter_index,
                    "source_char": a.source_char,
                }
                for a in self.alignment
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
