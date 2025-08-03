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
from typing import List, Dict

from .word import Word

@dataclass
class PipelineContext:
    """A context object to pass through the pipeline."""
    rule_configs: Dict[str, Dict[str, str]]

class PipelineStage(ABC):
    """An abstract base class for a stage in the processing pipeline."""
    
    @abstractmethod
    def process(self, words: List[Word], context: PipelineContext) -> List[Word]:
        pass


class CompositePipelineStage(PipelineStage):
    """A pipeline stage that is composed of other stages."""
    
    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages
    
    def process(self, words: List[Word], context: PipelineContext) -> List[Word]:
        for stage in self.stages:
            words = stage.process(words, context)
        return words 