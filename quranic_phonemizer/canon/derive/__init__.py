"""Derivations: the facts no script writes, resolved in one shared place.

A scalar either carries a canonical value outright or names a derivation
here; no derivation may consult a `Script`.
"""
from __future__ import annotations

from . import gemination, length, lexeme, silah, tanween, wasl
from .vocabulary import (
    Absent,
    AddsSlot,
    Attests,
    Context,
    Derivation,
    Outcome,
    Sets,
    Shows,
    Target,
    register,
    registered,
    required_roles,
    resolve,
)

__all__ = [
    "Absent", "AddsSlot", "Attests", "Context", "Derivation", "Outcome",
    "Sets", "Shows", "Target", "gemination", "length", "lexeme", "register",
    "registered", "required_roles", "resolve", "silah", "tanween", "wasl",
]
