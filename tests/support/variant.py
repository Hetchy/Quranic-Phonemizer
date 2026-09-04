"""Small helpers for behavior tests of the current scalar selector API."""
from __future__ import annotations

from quranic_phonemizer.model.address import KhilafId, Option, VariantSelection

from .reading import reading


def selection(khilaf: KhilafId, option: str) -> VariantSelection:
    return VariantSelection((Option(khilaf, option),))


def selected(site, word: int, khilaf: KhilafId, option: str, *, stopped=True,
             extra=None, riwayah="hafs"):
    boundary = {"isolated": word} if stopped else {"ibtidaa": word, "wasl": word}
    kwargs = {"selection": selection(khilaf, option), **boundary,
              "riwayah": riwayah}
    if extra is not None:
        kwargs["extra_phonemes"] = extra
    return reading(site, **kwargs)


def spaced(result, word: int) -> str:
    return " ".join(result.sounds(word))
