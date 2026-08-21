"""`AnalysisResult`: the native public result.

A thin reader over a validated bundle. Nothing in the package imports this
module; it sits at the top and only reads the records below it.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..session import Session
from .build import build_bundle
from .dtos import AnalysisBundle, Boundary, Merger, RuleOccurrence, Sound, Word
from .laws import validate


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """One request's analysis: its source text, performed tokens, and the
    words, boundaries, sounds, occurrences, and mergers that relate them."""

    ref: str
    riwayah: str
    script: str
    variant: dict
    extra_phonemes: frozenset[str]
    schema_version: int
    canon_digest: str

    words: tuple[Word, ...]
    boundaries: tuple[Boundary, ...]
    sounds: tuple[Sound, ...]
    rule_occurrences: tuple[RuleOccurrence, ...]
    mergers: tuple[Merger, ...]

    _source_text: str
    _tokens: tuple[str, ...]

    def text(self) -> str:
        return self._source_text

    def phonemes(
        self, by: str | None = None
    ) -> tuple[str, ...] | tuple[tuple[str, ...], ...]:
        if by not in (None, "word"):
            raise ValueError(f"by must be None or 'word', got {by!r}")
        if by is None:
            return self._tokens
        return tuple(
            tuple(self._tokens[sound.value] for sound in word.sound_ids)
            for word in self.words
        )


def _from_bundle(bundle: AnalysisBundle) -> AnalysisResult:
    return AnalysisResult(
        ref=bundle.ref,
        riwayah=bundle.riwayah,
        script=bundle.script,
        variant=bundle.variant,
        extra_phonemes=bundle.extra_phonemes,
        schema_version=bundle.schema_version,
        canon_digest=bundle.canon_digest,
        words=bundle.words,
        boundaries=bundle.boundaries,
        sounds=bundle.sounds,
        rule_occurrences=bundle.rule_occurrences,
        mergers=bundle.mergers,
        _source_text=bundle.source_text,
        _tokens=bundle.tokens,
    )


def build_result(
    session: Session,
    *,
    ref: str,
    riwayah: str,
    script: str,
    variant: dict,
    extra_phonemes: frozenset[str] = frozenset(),
) -> AnalysisResult:
    bundle = build_bundle(
        session,
        ref=ref,
        riwayah=riwayah,
        script=script,
        variant=variant,
        extra_phonemes=extra_phonemes,
    )
    validate(bundle)
    return _from_bundle(bundle)


__all__ = ["AnalysisResult", "build_result"]
