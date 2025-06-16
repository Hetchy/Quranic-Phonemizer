"""
Abstract parent for every tajweed-rule module.

A concrete rule file must define:

    class RuleImpl(PipelineStage):
        name = "some_rule_name"
        def process(self, tokens: list[Token], context: PipelineContext) -> List[Token]:
            ...

`process` receives the *live* token list and is free to mutate.
"""

from __future__ import annotations
from abc import abstractmethod
from typing import Dict, List, Any

from ..tokenizer import Token
from ..phoneme import Phoneme, create_phoneme

from ..pipeline import PipelineStage, PipelineContext


class Rule(PipelineStage):
    """Common interface for all rule plug-ins."""

    name: str = "base"
    config: Dict[str, Any] = {}  # Will be populated from rule_phonemes.yaml
    
    def __init__(self, config: dict):
        """Initialize shared resources."""
        self.config = config

    @abstractmethod
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        """Process tokens and return modified tokens"""
    
    def _create_phoneme(self, phoneme_str: str, category: str = "letters") -> Phoneme:
        """Helper to create Phoneme objects from strings during rule processing"""
        return create_phoneme(phoneme_str, category)
