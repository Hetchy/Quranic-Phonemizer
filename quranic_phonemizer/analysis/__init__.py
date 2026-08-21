"""The native projection's private facts, derived straight from a `Session`.

It reimplements the derivations it needs, reading only the resolved request,
the model, and the notation, and reaches nothing of the public assembler.
"""
from __future__ import annotations

from .attributions import (
    Classified,
    Hosted,
    Insertion,
    Merged,
    Recoloured,
    Relengthened,
    Silenced,
)
from .facts import AnalysisFacts, analyse
from .sounds import SoundFact

__all__ = [
    "AnalysisFacts",
    "Classified",
    "Hosted",
    "Insertion",
    "Merged",
    "Recoloured",
    "Relengthened",
    "Silenced",
    "SoundFact",
    "analyse",
]
