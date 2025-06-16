"""
core/pipeline.py
================
Pipeline infrastructure for processing tokens through various stages.

Provides:
- PipelineContext: Shared context passed between pipeline stages
- PipelineStage: Abstract base class for all pipeline stages  
- CompositePipelineStage: A pipeline stage that contains multiple sub-stages
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from .tokenizer import Token

@dataclass
class PipelineContext:
    """Shared context passed between pipeline stages"""
    db_path: str
    ref: str
    stops: List[str] = field(default_factory=list)


class PipelineStage(ABC):
    """Base class for all pipeline stages"""
    
    @abstractmethod
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        """Process tokens and return modified tokens"""


class CompositePipelineStage(PipelineStage):
    """A pipeline stage that contains multiple sub-stages"""
    
    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages
    
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for stage in self.stages:
            tokens = stage.process(tokens, context)
        return tokens 