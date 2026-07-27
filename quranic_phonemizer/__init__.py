"""Quranic phonemizer. No composition root yet: what is exported is the
vocabulary for stating a khilaf choice, which `riwayat.hafs.khilaf().points()`
lists."""
from .model.address import KhilafId, Option, VariantSelection

__all__: list[str] = ["KhilafId", "Option", "VariantSelection"]
