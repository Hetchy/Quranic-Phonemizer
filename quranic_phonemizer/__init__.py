"""Quranic phonemizer. `Phonemizer(...).phonemize(ref)` is the entry point;
`KhilafId`/`Option`/`VariantSelection` are the vocabulary for stating a
khilaf choice, which `available_variants()` lists."""
from .model.address import KhilafId, Option, VariantSelection
from .phonemize import (
    Phonemizer,
    PhonemizeResult,
    available_variants,
    edges,
    nodes,
    supported_riwayat,
    tajweed_rules,
)

__all__: list[str] = [
    "KhilafId",
    "Option",
    "Phonemizer",
    "PhonemizeResult",
    "VariantSelection",
    "available_variants",
    "edges",
    "nodes",
    "supported_riwayat",
    "tajweed_rules",
]
