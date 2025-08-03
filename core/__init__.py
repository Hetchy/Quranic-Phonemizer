"""
Core phonemizer modules.
"""

from .phonemizer import Phonemizer as OriginalPhonemizer
from .phonemizer_refactored import Phonemizer as RefactoredPhonemizer
from .location import Location
from .word import Word
from .symbols import Symbol, LetterSymbol, DiacriticSymbol, ExtensionSymbol, StopSymbol, OtherSymbol
from .rule import Rule
from .word_processor import WordProcessor
from .phonemize_result import PhonemizeResult
from .phoneme import Other

__all__ = [
    'OriginalPhonemizer',
    'RefactoredPhonemizer',
    'Phonemizer',
    'Location',
    'Word',
    'Symbol',
    'LetterSymbol',
    'DiacriticSymbol',
    'ExtensionSymbol',
    'StopSymbol',
    'OtherSymbol',
    'Rule',
    'WordProcessor',
    'PhonemizeResult',
    'Other'
]

# For backward compatibility, we'll use the refactored version as the default
Phonemizer = RefactoredPhonemizer

