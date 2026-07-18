from __future__ import annotations

from collections.abc import Iterable

from .engine import PhonemeEngine
from .model import Riwayah
from .result import PhonemizeResult


class Phonemizer:
    def __init__(self, riwayah: Riwayah = Riwayah.HAFS):
        self._engine = PhonemeEngine(riwayah)

    def phonemize(
        self,
        ref: str,
        *,
        stop_signs: Iterable[str] = (),
        stop_refs: Iterable[str] = (),
    ) -> PhonemizeResult:
        return PhonemizeResult(
            self._engine.phonemize(
                ref,
                stop_signs=stop_signs,
                stop_refs=stop_refs,
            )
        )
