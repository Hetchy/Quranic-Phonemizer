"""Quranic phonemizer. `api.recitation(riwayah)` is the entry point; what is
re-exported here is the vocabulary for stating a khilaf choice, which
`Recitation.khilaf.points()` lists."""
from .model.address import KhilafId, Option, VariantSelection

__all__: list[str] = ["KhilafId", "Option", "VariantSelection"]
