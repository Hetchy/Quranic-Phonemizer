"""
PhonemizeResult class for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import List


class PhonemizeResult:
    """Result of phonemization process."""
    def __init__(self, reference: str, text: str, phonemes: List[List[str]]):
        self.reference = reference
        self.text = text
        self.phonemes = phonemes
