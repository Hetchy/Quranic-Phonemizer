"""The resolved request: words, boundaries, and the built score for a passage.

This layer answers what a reference reads under a boundary plan. It knows
nothing of the public projection built on top of it.
"""
from __future__ import annotations

from .boundaries import resolve_boundaries
from .core import Session, phonemize_request
from .request import resolve_words
from .span import windows

__all__ = [
    "Session",
    "phonemize_request",
    "resolve_boundaries",
    "resolve_words",
    "windows",
]
