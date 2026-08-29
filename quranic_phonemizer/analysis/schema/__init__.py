"""The versioned wire schema for the native result and its selective views.

A total serializer to plain JSON, a JSON Schema reflected from the record types
with closed id references, and the checks that validate a serialized document.
"""
from __future__ import annotations

from .documents import (
    KINDS,
    AnalysisDocument,
    CellDocument,
    HighlightDocument,
    SourceDocument,
    analysis_document,
    cell_document,
    document_schema,
    highlight_document,
    serialize_document,
    source_document,
)
from .refs import (
    closed_reference_errors,
    combined_reference_errors,
    validation_errors,
)
from .serialize import to_json

__all__ = [
    "AnalysisDocument",
    "CellDocument",
    "HighlightDocument",
    "KINDS",
    "SourceDocument",
    "analysis_document",
    "cell_document",
    "closed_reference_errors",
    "combined_reference_errors",
    "document_schema",
    "highlight_document",
    "serialize_document",
    "source_document",
    "to_json",
    "validation_errors",
]
