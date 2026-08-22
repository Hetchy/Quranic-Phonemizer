"""The four wire documents: analysis result, source view, highlights, cells.

Each stamps `schema_version` at its top level and wraps one built record; the
schema of a document pins that version with a `const`.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from ..cells.dtos import CellView
from ..highlight_dtos import HighlightGroup
from ..ids import SCHEMA_VERSION
from ..result import AnalysisResult
from ..source_dtos import SourceView
from .reflect import id_record_map, json_schema
from .serialize import Json, to_json


@dataclass(frozen=True, slots=True)
class AnalysisDocument:
    schema_version: int
    result: AnalysisResult


@dataclass(frozen=True, slots=True)
class SourceDocument:
    schema_version: int
    source: SourceView


@dataclass(frozen=True, slots=True)
class HighlightDocument:
    schema_version: int
    highlight_groups: tuple[HighlightGroup, ...]


@dataclass(frozen=True, slots=True)
class CellDocument:
    schema_version: int
    cell_view: CellView


def analysis_document(result: AnalysisResult) -> AnalysisDocument:
    return AnalysisDocument(SCHEMA_VERSION, result)


def source_document(source: SourceView) -> SourceDocument:
    return SourceDocument(SCHEMA_VERSION, source)


def highlight_document(groups: tuple[HighlightGroup, ...]) -> HighlightDocument:
    return HighlightDocument(SCHEMA_VERSION, tuple(groups))


def cell_document(view: CellView) -> CellDocument:
    return CellDocument(SCHEMA_VERSION, view)


#: The wire document type behind each kind name, in a stable order.
KINDS: dict[str, type] = {
    "analysis_result": AnalysisDocument,
    "source_view": SourceDocument,
    "highlight_groups": HighlightDocument,
    "cell_view": CellDocument,
}


def serialize_document(document: object) -> Json:
    return to_json(document)


@lru_cache(maxsize=None)
def _id_map() -> dict:
    return id_record_map(tuple(KINDS.values()))


def document_schema(kind: str) -> dict:
    if kind not in KINDS:
        raise ValueError(f"unknown document kind {kind!r}; expected {sorted(KINDS)}")
    schema = json_schema(KINDS[kind], _id_map())
    root = schema["$defs"][KINDS[kind].__name__]
    root["properties"]["schema_version"]["const"] = SCHEMA_VERSION
    return schema


__all__ = [
    "AnalysisDocument",
    "CellDocument",
    "HighlightDocument",
    "KINDS",
    "SourceDocument",
    "analysis_document",
    "cell_document",
    "document_schema",
    "highlight_document",
    "serialize_document",
    "source_document",
]
