"""Muqattaat: letters that are named rather than read.

`الٓمٓ` is not a word - it is letters said by their names (`alif laam miim`),
expanded by a verse-level pass into ordinary slots.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..dataio import load_yaml, require_keys
from ..model.canon import ABJAD, CanonLetter, Long, Quality, Short, Silent, SlotOrigin
from ..model.inscription import SlotFact
from ..orthography.adapter import Reading
from .draft import _Draft
from .passes import word_of

SCHEMA_VERSION = 1

#: A vowel of the reading. Excludes the shadda, which records an assimilation
#: between two letter names rather than a nucleus.
HARAKAT = frozenset(
    {"fatha", "damma", "kasra", "fathatan", "dammatan", "kasratan", "sukun"}
)

#: Letter, then an optional vowel: lowercase short, uppercase long, absent
#: silent. The same notation the pausal lexemes are written in.
_QUALITY = {"a": Quality.A, "u": Quality.U, "i": Quality.I}

_LETTER_OF = {glyph: name for name, glyph in ABJAD.items()}


class SpellingError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Muqattaat:
    """Which openings are named rather than read, and how each letter is
    called."""

    openings: frozenset[str]
    """Letter skeletons, in `ABJAD` glyphs."""

    by_letter: dict[CanonLetter, tuple[tuple[CanonLetter, object], ...]]

    def is_opening(self, skeleton: str) -> bool:
        return skeleton in self.openings

    def spell(self, letter: CanonLetter):
        return self.by_letter.get(letter)


EMPTY = Muqattaat(frozenset(), {})


def load_muqattaat(path: Path) -> Muqattaat:
    data = load_yaml(path)
    require_keys(data, {"schema_version", "openings", "names"}, name=str(path))
    if data["schema_version"] != SCHEMA_VERSION:
        raise SpellingError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    by_letter: dict[CanonLetter, tuple] = {}
    for glyph, spelled in data["names"].items():
        letter = _canon(glyph, path)
        by_letter[letter] = tuple(_parse(spelled, path))
    openings = frozenset(data["openings"])
    for skeleton in openings:
        for glyph in skeleton:
            _canon(glyph, path)
    return Muqattaat(openings, by_letter)


def _canon(glyph: str, path: Path) -> CanonLetter:
    name = _LETTER_OF.get(glyph)
    if name is None:
        raise SpellingError(
            f"{path}: {glyph!r} is not a canonical letter. Keys are `ABJAD` "
            f"glyphs, never a script's own scalars."
        )
    return CanonLetter(name)


def _parse(spelled: str, path: Path):
    index = 0
    while index < len(spelled):
        letter = _canon(spelled[index], path)
        index += 1
        if index < len(spelled) and spelled[index] in _QUALITY:
            yield letter, Short(_QUALITY[spelled[index]])
            index += 1
        elif index < len(spelled) and spelled[index].lower() in _QUALITY:
            yield letter, Long(_QUALITY[spelled[index].lower()])
            index += 1
        else:
            yield letter, Silent()


def spell_muqattaat(names: Muqattaat):
    """Build the pass. Bound by the riwayah like the other lexeme passes."""

    def apply(reading: Reading, drafts: list, lexicon, scribe=None) -> None:
        del lexicon
        for word in range(len(reading.words)):
            if not _is_muqattaat(reading, word, names):
                continue
            span = [d for d in drafts if word_of(reading, d) == word]
            if not span:
                continue
            spelled = _spelled(reading, word, names)
            if spelled is None:
                continue
            first = drafts.index(span[0])
            for draft in span:
                drafts.remove(draft)
            drafts[first:first] = spelled
            if scribe is not None:
                # The compact grapheme evidences every slot its name expands
                # to, so `الٓمٓصٓ` gives three graphemes reaching seven slots,
                # keeping every slot traceable to a grapheme.
                for draft in spelled:
                    offset = reading.clusters[draft.cluster].offset
                    scribe.evidence(offset, draft, SlotFact.LETTER)
                    scribe.evidence(offset, draft, SlotFact.NUCLEUS)

    return apply


def _is_muqattaat(reading: Reading, word: int, names: Muqattaat) -> bool:
    """One of the named openings, voweled nowhere but its last letter. Read
    from the clusters, where `ٱ` has not yet been given a helping vowel."""
    clusters = [c for c in reading.clusters if c.word == word]
    if not clusters or any(cluster.has(*HARAKAT) for cluster in clusters[:-1]):
        return False
    skeleton = "".join(
        ABJAD[c.letter.value] for c in clusters if c.letter is not None
    )
    return names.is_opening(skeleton)


def _spelled(reading: Reading, word: int, names: Muqattaat) -> list | None:
    """Spelled from the clusters, not the drafted slots: a derivation may
    have already absorbed a bare yaa into a neighboring long vowel there,
    but these letters are named, not read, so that absorption does not apply.
    """
    out: list[_Draft] = []
    for index, cluster in enumerate(reading.clusters):
        if cluster.word != word or cluster.letter is None:
            continue
        letters = names.spell(cluster.letter)
        if letters is None:
            # A bare word whose letter has no name is not muqattaat, so the
            # whole word is left alone rather than half-spelled.
            return None
        for letter, nucleus in letters:
            out.append(
                _Draft(
                    letter=letter,
                    nucleus=nucleus,
                    cluster=index,
                    origin=SlotOrigin.SPELLED,
                )
            )
    return out or None
