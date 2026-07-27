"""Khilaf the Score carries: a word two readings vowel differently.

Separate from `rules/khilaf.py`, which chooses between two performances of
one Score. Here the Scores themselves differ, so the choice is made at build.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.address import KhilafId
from ..model.canon import Quality, Short
from ..orthography.adapter import Reading
from .passes import vocalised, word_of


@dataclass(frozen=True, slots=True)
class VowelSite:
    """One word, and which of its slots the readings disagree about."""

    index: int
    options: dict[str, Quality]
    default: str
    forms: frozenset[str]
    """Every vocalised spelling either wajh writes, so the word is recognised
    whichever one its script chose."""


@dataclass(frozen=True, slots=True)
class VowelKhilaf:
    """Sites keyed by canonical letters, which is what a caller selects on."""

    sites: dict[str, VowelSite] = field(default_factory=dict)

    def of(self, form: str) -> tuple[str, VowelSite] | None:
        for name, site in self.sites.items():
            if form in site.forms:
                return name, site
        return None

    def points(self) -> dict[str, dict[str, object]]:
        """What a caller may choose, without reading the data file."""
        return {
            name: {"options": sorted(site.options), "default": site.default}
            for name, site in self.sites.items()
        }


def apply_vowel_khilaf(khilaf: VowelKhilaf):
    """Build the pass. Bound by the riwayah like the other lexeme passes."""

    def apply(reading: Reading, drafts, lexicon, scribe, selection) -> None:
        del lexicon, scribe
        if not khilaf.sites:
            return
        for word in range(len(reading.words)):
            span = [d for d in drafts if word_of(reading, d) == word]
            found = khilaf.of(vocalised(span)) if span else None
            if found is None:
                continue
            name, site = found
            chosen = selection.chosen(KhilafId.NUCLEUS_VOWEL, site=name)
            span[site.index].nucleus = Short(
                site.options[chosen or site.default]
            )

    return apply
