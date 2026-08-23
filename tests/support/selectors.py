"""Compact, exact selectors for source glyphs and performed sounds."""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from quranic_phonemizer.model.canon import CanonLetter, Quality, VowelForm
from quranic_phonemizer.phonemize import edges as ed
from quranic_phonemizer.phonemize import nodes as nd


class SelectorError(ValueError):
    """A selector is unknown, ambiguous, redundant, or has no target."""


_OCCURRENCE = re.compile(r"^(.*)\[([1-9][0-9]*)\]$")


@dataclass(frozen=True, slots=True)
class ParsedSelector:
    name: str
    occurrence: int | None


def parse_selector(value: str) -> ParsedSelector:
    match = _OCCURRENCE.fullmatch(value)
    if match is None:
        return ParsedSelector(value, None)
    return ParsedSelector(match.group(1), int(match.group(2)))


def _supplies(assembled, glyph: int, fact: ed.Fact | None = None):
    return tuple(
        edge for edge in assembled.spellings
        if isinstance(edge, ed.Supplies)
        and edge.glyph == glyph
        and (fact is None or edge.fact is fact)
    )


def _quality(assembled, glyph: int, quality: Quality) -> bool:
    return any(
        assembled.units[edge.unit].vowel.quality is quality
        for edge in _supplies(assembled, glyph, ed.Fact.VOWEL_QUALITY)
    )


def _length(assembled, glyph: int, quality: Quality) -> bool:
    supplied = any(
        assembled.units[edge.unit].vowel.quality is quality
        for edge in _supplies(assembled, glyph, ed.Fact.VOWEL_LENGTH)
    )
    marked = (
        assembled.glyphs[glyph].kind is nd.GlyphKind.SMALL_VOWEL
        and _quality(assembled, glyph, quality)
        and any(
            assembled.units[edge.unit].vowel.joined.form is VowelForm.LONG
            for edge in _supplies(assembled, glyph)
        )
    )
    return supplied or marked


def _letter(assembled, glyph: int, letter: CanonLetter) -> bool:
    return any(
        assembled.units[edge.unit].letter is letter
        for edge in _supplies(assembled, glyph, ed.Fact.LETTER)
    )


def _pausal_alif(assembled, glyph: int) -> bool:
    return assembled.glyphs[glyph].char == "ا" and any(
        assembled.units[edge.unit].vowel.joined.form is VowelForm.SHORT
        and assembled.units[edge.unit].vowel.stopped.form is VowelForm.LONG
        for edge in assembled.spellings
        if getattr(edge, "glyph", None) == glyph
        and getattr(edge, "unit", None) is not None
    )


def _tanween(assembled, glyph: int, quality: Quality) -> bool:
    for edge in _supplies(assembled, glyph):
        unit = assembled.units[edge.unit]
        if unit.origin is not nd.UnitOrigin.TANWEEN or edge.unit == 0:
            continue
        host = assembled.units[edge.unit - 1]
        if host.word == unit.word and host.vowel.quality is quality:
            return True
    return False


GlyphPredicate = Callable[[object, int], bool]


_GLYPH_SELECTORS: dict[str, GlyphPredicate] = {
    "@pausal_alif": _pausal_alif,
    "@yaa": lambda a, g: _letter(a, g, CanonLetter.YA),
    "@fatha": lambda a, g: a.glyphs[g].kind is nd.GlyphKind.HARAKA
    and _quality(a, g, Quality.A),
    "@damma": lambda a, g: a.glyphs[g].kind is nd.GlyphKind.HARAKA
    and _quality(a, g, Quality.U),
    "@kasra": lambda a, g: a.glyphs[g].kind is nd.GlyphKind.HARAKA
    and _quality(a, g, Quality.I),
    "@sukun": lambda a, g: a.glyphs[g].kind is nd.GlyphKind.SUKUN,
    "@shadda": lambda a, g: a.glyphs[g].kind is nd.GlyphKind.SHADDA,
    "@fathatan": lambda a, g: _tanween(a, g, Quality.A),
    "@dammatan": lambda a, g: _tanween(a, g, Quality.U),
    "@kasratan": lambda a, g: _tanween(a, g, Quality.I),
    "@dagger_alif": lambda a, g: a.glyphs[g].char == "ٰ",
    "@madd_sign": lambda a, g: a.glyphs[g].kind is nd.GlyphKind.MADD_SIGN,
    "@hamza_mark": lambda a, g: a.glyphs[g].char in {"ٔ", "ٕ"},
    "@small_noon": lambda a, g: a.glyphs[g].char == "ۨ"
    and _letter(a, g, CanonLetter.NOON),
    "@small_waw": lambda a, g: a.glyphs[g].kind is not nd.GlyphKind.HARAKA
    and (_quality(a, g, Quality.U) or _length(a, g, Quality.U)),
    "@small_yaa": lambda a, g: a.glyphs[g].char == "ۦ"
    or (
        a.glyphs[g].kind is not nd.GlyphKind.HARAKA
        and (_quality(a, g, Quality.I) or _length(a, g, Quality.I))
    ),
    "@mini_meem": lambda a, g: a.glyphs[g].char in {"ۢ", "ۭ"},
    "@round_zero": lambda a, g: a.glyphs[g].char == "۟",
    "@rectangular_zero": lambda a, g: a.glyphs[g].char == "۠",
    "@imala_mark": lambda a, g: a.glyphs[g].char in {"۪", "ٖ"},
    "@tashil_mark": lambda a, g: a.glyphs[g].char == "۬",
    "@ishmam_mark": lambda a, g: a.glyphs[g].char == "۫",
    "@sakt_mark": lambda a, g: a.glyphs[g].char == "ۜ",
    "@stop_mark": lambda a, g: a.glyphs[g].kind is nd.GlyphKind.STOP_SIGN,
}


def registered_selectors() -> frozenset[str]:
    return frozenset(_GLYPH_SELECTORS)


def subtle_literal(value: str) -> bool:
    """A combining-only literal is unreadable beside Python quotes."""
    return bool(value) and all(unicodedata.category(char).startswith("M") for char in value)


def _choose(selector: ParsedSelector, candidates: tuple[int, ...], kind: str) -> int:
    if not candidates:
        raise SelectorError(f"{selector.name!r} resolves to no {kind}")
    if selector.occurrence is None:
        if len(candidates) != 1:
            raise SelectorError(
                f"{selector.name!r} resolves to {len(candidates)} {kind}s; add [n]"
            )
        return candidates[0]
    if len(candidates) == 1:
        raise SelectorError(
            f"{selector.name!r} is unique; [{selector.occurrence}] is noise"
        )
    index = selector.occurrence - 1
    if index >= len(candidates):
        raise SelectorError(
            f"{selector.name!r}[{selector.occurrence}] exceeds {len(candidates)} {kind}s"
        )
    return candidates[index]


def resolve_glyph(assembled, words: Iterable[int], value: str) -> int:
    selector = parse_selector(value)
    focused = {word - 1 for word in words}
    if selector.name.startswith("@"):
        predicate = _GLYPH_SELECTORS.get(selector.name)
        if predicate is None:
            raise SelectorError(f"unknown source selector {selector.name!r}")
    else:
        if subtle_literal(selector.name):
            raise SelectorError(
                f"subtle mark {selector.name!r} needs a registered @selector"
            )
        predicate = lambda a, g: a.glyphs[g].char == selector.name
    candidates = tuple(
        index for index, glyph in enumerate(assembled.glyphs)
        if glyph.word in focused and predicate(assembled, index)
    )
    return _choose(selector, candidates, "source targets")


def resolve_sound(assembled, sound_words: dict[int, int], words: Iterable[int], value: str) -> int:
    selector = parse_selector(value)
    if selector.name.startswith("@"):
        raise SelectorError(f"sound selector cannot be semantic: {selector.name!r}")
    focused = {word - 1 for word in words}
    candidates = tuple(
        index for index, sound in enumerate(assembled.sounds)
        if sound.token == selector.name and sound_words.get(index) in focused
    )
    return _choose(selector, candidates, "sounds")
