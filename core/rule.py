"""
Rule base class for the Quranic phonemizer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Rule(ABC):
    """Abstract base class for Tajweed rules."""
    @abstractmethod
    def apply(self, phonemes: List[str], context: Dict[str, Any]) -> List[str]:
        """Apply the rule to the phonemes."""
        pass
