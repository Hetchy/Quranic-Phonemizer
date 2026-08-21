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
from .derivations import (
    decoration_targets,
    open_vowel_units,
    shortened_carriers,
    silent_groups,
)
from .facts import AnalysisFacts, analyse
from .glyphs import Glyph, GlyphKind, glyph_kind_of
from .inscription import (
    Decorated,
    InscriptionFacts,
    Structural,
    Supplied,
    Witnessed,
    inscribe,
)
from .sounds import SoundFact

__all__ = [
    "AnalysisFacts",
    "Classified",
    "Decorated",
    "Glyph",
    "GlyphKind",
    "Hosted",
    "Insertion",
    "InscriptionFacts",
    "Merged",
    "Recoloured",
    "Relengthened",
    "Silenced",
    "SoundFact",
    "Structural",
    "Supplied",
    "Witnessed",
    "analyse",
    "decoration_targets",
    "glyph_kind_of",
    "inscribe",
    "open_vowel_units",
    "shortened_carriers",
    "silent_groups",
]
