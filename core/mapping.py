"""
Letter-to-phoneme mapping schema for reverse mapping support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class MappingType(Enum):
    STANDARD = "standard"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    SILENT = "silent"
    CROSS_WORD = "cross_word"
    SPECIAL = "special"
    CONTEXTUAL = "contextual"


@dataclass
class LetterMapping:
    index: int
    char: str
    phonemes: List[str]
    
    diacritic: Optional[str] = None  # Just the name, e.g. "FATHA"
    has_shaddah: bool = False
    
    mapping_type: MappingType = MappingType.STANDARD
    rule: Optional[str] = None


@dataclass
class WordMapping:
    location: str
    text: str
    phonemes: List[str]
    letter_mappings: List[LetterMapping]
    
    is_special_word: bool = False
    is_starting: bool = False
    is_stopping: bool = False


@dataclass
class AlignmentEntry:
    phoneme_index: int
    phoneme: str
    word_index: int
    letter_index: int
    source_char: str
    rule: Optional[str] = None


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
                            "mapping_type": lm.mapping_type.value if lm.mapping_type != MappingType.STANDARD else None,
                            "rule": lm.rule,
                        }.items() if v is not None}
                        for lm in w.letter_mappings
                    ],
                    **({"is_special_word": True} if w.is_special_word else {}),
                    **({"is_starting": True} if w.is_starting else {}),
                    **({"is_stopping": True} if w.is_stopping else {}),
                }
                for w in self.words
            ],
            "phoneme_sequence": self.phoneme_sequence,
            "alignment": [
                {k: v for k, v in {
                    "phoneme_index": a.phoneme_index,
                    "phoneme": a.phoneme,
                    "word_index": a.word_index,
                    "letter_index": a.letter_index,
                    "source_char": a.source_char,
                    "rule": a.rule,
                }.items() if v is not None}
                for a in self.alignment
            ],
        }
    
    def to_json(self, indent: int = 2) -> str:
        import json
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
