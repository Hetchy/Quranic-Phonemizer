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
from .build import build_bundle
from .catalogue import UnknownRiwayah, rule_definitions, tajweed_rules
from .derivations import (
    decoration_targets,
    open_vowel_units,
    shortened_carriers,
    silent_groups,
)
from .dtos import (
    AnalysisBundle,
    Boundary,
    BoundaryState,
    Merger,
    RuleDefinition,
    RuleOccurrence,
    Sound,
    Word,
)
from .facts import AnalysisFacts, analyse
from .glyphs import Glyph, GlyphKind, glyph_kind_of
from .ids import (
    SCHEMA_VERSION,
    BoundaryId,
    MergerId,
    OccurrenceId,
    RuleId,
    SoundId,
    WordId,
)
from .inscription import (
    Decorated,
    InscriptionFacts,
    Structural,
    Supplied,
    Witnessed,
    inscribe,
)
from .laws import ValidationError, validate
from .result import AnalysisResult, build_result
from .sounds import SoundFact

__all__ = [
    "SCHEMA_VERSION",
    "AnalysisBundle",
    "AnalysisFacts",
    "AnalysisResult",
    "Boundary",
    "BoundaryId",
    "BoundaryState",
    "Classified",
    "Decorated",
    "Glyph",
    "GlyphKind",
    "Hosted",
    "Insertion",
    "InscriptionFacts",
    "Merged",
    "Merger",
    "MergerId",
    "OccurrenceId",
    "Recoloured",
    "Relengthened",
    "RuleDefinition",
    "RuleId",
    "RuleOccurrence",
    "Silenced",
    "Sound",
    "SoundFact",
    "SoundId",
    "Structural",
    "Supplied",
    "UnknownRiwayah",
    "ValidationError",
    "Witnessed",
    "Word",
    "WordId",
    "analyse",
    "build_bundle",
    "build_result",
    "decoration_targets",
    "glyph_kind_of",
    "inscribe",
    "open_vowel_units",
    "rule_definitions",
    "shortened_carriers",
    "silent_groups",
    "tajweed_rules",
    "validate",
]
