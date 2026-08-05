"""`PhonemizeResult`: the public result object.

`phonemes()` and `text()` read straight off `Assembled`'s node arrays;
`alignment()`/`respelling()` delegate to `pairing.py`/`respell.py`.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import edges as ed
from . import nodes as nd
from .assemble import Assembled
from .pairing import Pairing, alignment as _alignment
from .respell import Block, respelling as _respelling

#: The shape of this document. A union member added to `schema.py` bumps it.
SCHEMA_VERSION = "1"


def phonemes(
    assembled: Assembled, by: str | None = None
) -> tuple[str, ...] | tuple[tuple[str, ...], ...]:
    if by not in (None, "word"):
        raise ValueError(f"by must be None or 'word', got {by!r}")
    tokens = tuple(sound.token for sound in assembled.sounds)
    return tokens if by is None else _by_word(assembled, tokens)


def _by_word(
    assembled: Assembled, tokens: tuple[str, ...]
) -> tuple[tuple[str, ...], ...]:
    word_of_sound = _sound_words(assembled)
    buckets: list[list[str]] = [[] for _ in assembled.words]
    for index, token in enumerate(tokens):
        word = word_of_sound.get(index)
        if word is not None:
            buckets[word].append(token)
    return tuple(tuple(bucket) for bucket in buckets)


def _sound_words(assembled: Assembled) -> dict[int, int]:
    """Map each sound to its primary origin's word."""
    return {
        a.sound: assembled.units[a.unit].word
        for a in assembled.attributions
        if isinstance(a, ed.Hosts)
    }


def text(assembled: Assembled, which: str = "source") -> str:
    if which not in ("source", "recited"):
        raise ValueError(f"which must be 'source' or 'recited', got {which!r}")
    glyphs = assembled.glyphs if which == "source" else assembled.rendered
    return "".join(glyph.char for glyph in glyphs)


@dataclass(frozen=True, slots=True)
class PhonemizeResult:
    """The whole document. Every projection derives from these members, so a
    result copied member by member projects the same as the one built."""

    ref: str
    riwayah: str
    script: str
    variant: dict
    extra_phonemes: frozenset[str]
    schema_version: str
    canon_digest: str

    words: tuple[nd.Word, ...]
    glyphs: tuple[nd.Glyph, ...]
    rendered: tuple[nd.RenderGlyph, ...]
    units: tuple[nd.Unit, ...]
    sounds: tuple[nd.Sound, ...]
    rules: tuple[nd.RuleInstance, ...]

    spellings: tuple[ed.SpellingEdge, ...]
    attributions: tuple[ed.AttributionEdge, ...]
    modifiers: tuple[ed.ModifierEdge, ...]

    def _assembled(self) -> Assembled:
        """The nine arrays this document is, ready for a projection."""
        return Assembled(
            words=self.words, glyphs=self.glyphs, rendered=self.rendered,
            units=self.units, sounds=self.sounds, rules=self.rules,
            spellings=self.spellings, attributions=self.attributions,
            modifiers=self.modifiers,
        )

    def phonemes(
        self, by: str | None = None
    ) -> tuple[str, ...] | tuple[tuple[str, ...], ...]:
        return phonemes(self._assembled(), by)

    def text(self, which: str = "source") -> str:
        return text(self._assembled(), which)

    def alignment(
        self, *, text: str = "source", grouping: str = "glyph"
    ) -> tuple[Pairing, ...]:
        return _alignment(self._assembled(), text=text, grouping=grouping)

    def respelling(self, *, grouping: str = "cell") -> tuple[Block, ...]:
        return _respelling(self._assembled(), grouping=grouping)


def build_result(
    *,
    ref: str,
    riwayah: str,
    script: str,
    variant: dict,
    extra_phonemes: frozenset[str],
    canon_digest: str,
    assembled: Assembled,
) -> PhonemizeResult:
    return PhonemizeResult(
        ref=ref, riwayah=riwayah, script=script, variant=variant,
        extra_phonemes=extra_phonemes, schema_version=SCHEMA_VERSION,
        canon_digest=canon_digest,
        words=assembled.words, glyphs=assembled.glyphs,
        rendered=assembled.rendered, units=assembled.units,
        sounds=assembled.sounds, rules=assembled.rules,
        spellings=assembled.spellings, attributions=assembled.attributions,
        modifiers=assembled.modifiers,
    )


__all__ = ["PhonemizeResult", "SCHEMA_VERSION", "build_result", "phonemes", "text"]
