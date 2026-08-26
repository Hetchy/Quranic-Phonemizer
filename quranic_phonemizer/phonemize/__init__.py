"""The public projection: `Phonemizer` loads a riwayah, a script and a
selection once, on construction; `.phonemize(ref)` resolves, builds,
performs and assembles one `PhonemizeResult` per call.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..api import UnknownRiwayah, alphabet as load_alphabet, recitation
from ..model.address import Script
from ..orthography.write import pen_for
from ..render.alphabet import allowed_extra_phonemes, effective_extra_phonemes
from . import edges, names, nodes
from .assemble import assemble
from .document import PhonemizeResult, build_result
from .runtime import suspend_collection
from ..session import phonemize_request

supported_riwayat = names.supported_riwayat
available_variants = names.available_variants
tajweed_rules = names.tajweed_rules


class UnknownExtraPhoneme(ValueError):
    """A rendering distinction not optional for the selected riwayah."""


@dataclass(frozen=True)
class Phonemizer:
    riwayah: str = "hafs"
    script: str | None = None
    variants: dict | None = None
    extra_phonemes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        riwayah = names.check_riwayah(self.riwayah)
        requested = frozenset(self.extra_phonemes)
        allowed = allowed_extra_phonemes(riwayah)
        unknown = requested - allowed
        if unknown:
            raise UnknownExtraPhoneme(
                f"{sorted(unknown)} is not optional for {riwayah.value}; "
                f"choose from {sorted(allowed)}"
            )
        script = Script(self.script) if self.script else names.DEFAULT_SCRIPT[riwayah]
        loaded = recitation(riwayah)
        selection = names.to_selection(self.variants)
        loaded.khilaf.validate(selection)
        object.__setattr__(self, "_recitation", loaded)
        object.__setattr__(self, "_script", script)
        object.__setattr__(self, "_alphabet", load_alphabet())
        object.__setattr__(self, "_pen", pen_for(loaded.inventory(script)))
        object.__setattr__(self, "_selection", selection)
        object.__setattr__(self, "_extra", requested)
        object.__setattr__(
            self, "_render_extra", effective_extra_phonemes(riwayah, requested)
        )

    def phonemize(
        self,
        ref: str,
        *,
        stop_signs: Sequence[str] = (),
        stop_refs: Sequence[str] = (),
        suspend_gc: bool = False,
    ) -> PhonemizeResult:
        if suspend_gc:
            with suspend_collection():
                return self._phonemize(ref, stop_signs, stop_refs)
        return self._phonemize(ref, stop_signs, stop_refs)

    def _phonemize(
        self,
        ref: str,
        stop_signs: Sequence[str],
        stop_refs: Sequence[str],
    ) -> PhonemizeResult:
        session = phonemize_request(
            self._recitation, ref, script=self._script,
            stop_signs=stop_signs, stop_refs=stop_refs,
            selection=self._selection,
        )
        assembled = assemble(
            session, self._pen, self._alphabet,
            extra_phonemes=self._render_extra,
        )
        return build_result(
            ref=ref, riwayah=self.riwayah, script=self._script.value,
            variant=names.resolved_variant(self._recitation.khilaf, self._selection),
            extra_phonemes=self._extra, canon_digest=session.score.digest,
            assembled=assembled,
        )


__all__ = [
    "Phonemizer",
    "PhonemizeResult",
    "UnknownExtraPhoneme",
    "UnknownRiwayah",
    "available_variants",
    "edges",
    "nodes",
    "supported_riwayat",
    "tajweed_rules",
]
