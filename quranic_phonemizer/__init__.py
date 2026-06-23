"""
Core phonemizer modules.
"""

from .phonemizer import Phonemizer
from .location import Location
from .word import Word
from .symbols.symbol import Symbol
from .symbols.letters.letter import LetterSymbol
from .symbols.diacritic import DiacriticSymbol
from .symbols.extension import ExtensionSymbol
from .symbols.stop import StopSymbol
from .symbols.other import OtherSymbol
from .phonemizer import PhonemizeResult
from .mapping import (
    LetterMapping,
    WordMapping,
    AlignmentEntry,
    PhonemizationMapping,
)
from .tajweed_rule import TajweedRule, TajweedRuleTag
from .tajweed_mapping import TajweedMapping, TajweedWordMapping, TajweedEntry
from .letter_phoneme_mapping import FlatMappingResult
from .char_phoneme_mapping import Cell, CharWord, CharPhonemeResult
from .tajweed_classification import (
    CellRole,
    CellStatus,
    MergerClass,
    CrossWordMerger,
    CROSS_WORD_MERGERS,
    detect_cross_word_mergers,
    BRIDGE_RULE_VALUES,
    MERGER_ON_PREV_VALUES,
    BOTH_SOUND_VALUES,
    IDGHAM_SOURCE_TAG_VALUES,
    TANWEEN_ASSIMILATES_VALUES,
)
from .phonemes import (
    is_madd,
    is_short_vowel,
    is_geminate,
    is_nasalised,
    is_render_only,
    render_only_phonemes,
    nasalised_phonemes,
    diacritic_chars,
    SHORT_VOWEL_PHONEMES,
    VOWEL_CARRIER_CHARS,
)

__all__ = [
    'Phonemizer',
    'Location',
    'Word',
    'Symbol',
    'LetterSymbol',
    'DiacriticSymbol',
    'ExtensionSymbol',
    'StopSymbol',
    'OtherSymbol',
    'PhonemizeResult',
    'LetterMapping',
    'WordMapping',
    'AlignmentEntry',
    'PhonemizationMapping',
    'TajweedRule',
    'TajweedRuleTag',
    'TajweedMapping',
    'TajweedWordMapping',
    'TajweedEntry',
    'FlatMappingResult',
    'Cell',
    'CharWord',
    'CharPhonemeResult',
    # cross-word tajweed classification + the single detector
    'CellRole',
    'CellStatus',
    'MergerClass',
    'CrossWordMerger',
    'CROSS_WORD_MERGERS',
    'detect_cross_word_mergers',
    'BRIDGE_RULE_VALUES',
    'MERGER_ON_PREV_VALUES',
    'BOTH_SOUND_VALUES',
    'IDGHAM_SOURCE_TAG_VALUES',
    'TANWEEN_ASSIMILATES_VALUES',
    # phoneme predicates + derived sets
    'is_madd',
    'is_short_vowel',
    'is_geminate',
    'is_nasalised',
    'is_render_only',
    'render_only_phonemes',
    'nasalised_phonemes',
    'diacritic_chars',
    'SHORT_VOWEL_PHONEMES',
    'VOWEL_CARRIER_CHARS',
]
