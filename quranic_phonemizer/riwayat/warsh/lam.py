"""Authored al-Azraq lam registers and their selector profile."""
from __future__ import annotations

from dataclasses import dataclass

from ...model.address import KhilafId, Location, SourceLocation
from ...rules.lam import (
    GeneralLamChoice,
    LamChoice,
    LamKey,
    LamProfile,
    general_sites,
)
from ..khilaf import VariantSpan

_ARTIFACT = "king-fahd-warsh-v2"

#: The waqf-only junction on 2:125 and 87:12 is the wasl mask: the inclined
#: alif is unavailable in wasl and the ordinary sad trigger reads tafkheem.
SELECTOR_JUNCTIONS = {
    "lam_dhat_yaa": "all",
    "lam_verse_heads": "all",
    "lam_separated_by_alif": "all",
    "lam_final_waqf": "waqf",
    "lam_salsal": "all",
}

GENERAL_SELECTORS = {
    "lam_after_taa": "eligible_lam_taa",
    "lam_after_zhaa": "eligible_lam_zhaa",
}


@dataclass(frozen=True, slots=True)
class LamSite:
    owner: str
    source: SourceLocation
    canonical: Location
    text: str
    lam: int = 1
    junction: str | None = None

    @property
    def key(self) -> LamKey:
        return self.canonical, self.lam


def _site(owner, source, canonical, text, junction=None) -> LamSite:
    return LamSite(
        owner,
        SourceLocation(_ARTIFACT, *source),
        Location(*canonical),
        text,
        junction=junction,
    )


SITES = (
    _site("lam_dhat_yaa", (2, 124, 11), (2, 125, 11), "مُصَلّىٗۖ",
          junction="waqf"),
    _site("lam_dhat_yaa", (17, 18, 16), (17, 18, 16), "يَصْلَيٰهَا"),
    _site("lam_dhat_yaa", (84, 12, 1), (84, 12, 1), "وَيُصَلَّىٰ"),
    _site("lam_dhat_yaa", (87, 12, 2), (87, 12, 2), "يَصْلَى",
          junction="waqf"),
    _site("lam_dhat_yaa", (88, 4, 1), (88, 4, 1), "تَصْلَىٰ"),
    _site("lam_dhat_yaa", (92, 15, 2), (92, 15, 2), "يَصْلَيٰهَآ"),
    _site("lam_dhat_yaa", (111, 3, 1), (111, 3, 1), "سَيَصْلَىٰ"),
    _site("lam_verse_heads", (75, 30, 4), (75, 31, 4), "صَلّ۪ىٰۖ"),
    _site("lam_verse_heads", (87, 15, 4), (87, 15, 4), "فَصَلّ۪ىٰۖ"),
    _site("lam_verse_heads", (96, 10, 3), (96, 10, 3), "صَلّ۪ىٰٓۖ"),
    _site("lam_separated_by_alif", (2, 231, 36), (2, 233, 36), "فِصَالاً"),
    _site("lam_separated_by_alif", (4, 127, 13), (4, 128, 13), "يَّصَّٰلَحَا"),
    _site("lam_separated_by_alif", (20, 85, 1), (20, 86, 14), "اَفَطَالَ"),
    _site("lam_separated_by_alif", (21, 44, 6), (21, 44, 6), "طَالَ"),
    _site("lam_separated_by_alif", (57, 15, 21), (57, 16, 21), "فَطَالَ"),
    _site("lam_final_waqf", (2, 26, 14), (2, 27, 14), "يُّوصَلَ"),
    _site("lam_final_waqf", (2, 247, 2), (2, 249, 2), "فَصَلَ"),
    _site("lam_final_waqf", (6, 120, 11), (6, 119, 11), "فَصَّلَ"),
    _site("lam_final_waqf", (7, 117, 3), (7, 118, 3), "وَبَطَلَ"),
    _site("lam_final_waqf", (13, 23, 8), (13, 21, 8), "يُّوصَلَ"),
    _site("lam_final_waqf", (13, 26, 14), (13, 25, 14), "يُّوصَلَ"),
    _site("lam_final_waqf", (16, 58, 5), (16, 58, 5), "ظَلَّ"),
    _site("lam_final_waqf", (38, 19, 5), (38, 20, 5), "وَفَصْلَ"),
    _site("lam_final_waqf", (43, 16, 8), (43, 17, 8), "ظَلَّ"),
    _site("lam_salsal", (15, 26, 5), (15, 26, 5), "صَلْصَٰلٖ"),
    _site("lam_salsal", (15, 28, 9), (15, 28, 9), "صَلْصَٰلٖ"),
    _site("lam_salsal", (15, 33, 8), (15, 33, 8), "صَلْصَٰلٖ"),
    _site("lam_salsal", (55, 12, 4), (55, 14, 4), "صَلْصَٰلٖ"),
)


def selector_profile(definitions) -> LamProfile:
    """Bind every published lam selector over the authored registers."""
    selected = {}
    for site in SITES:
        khilaf = KhilafId(site.owner)
        definition = definitions.get(khilaf)
        if definition is None:
            continue
        selected[site.key] = LamChoice(
            khilaf,
            site.junction or SELECTOR_JUNCTIONS[site.owner],
            definition.default,
        )
    generals = {}
    for owner in GENERAL_SELECTORS:
        khilaf = KhilafId(owner)
        definition = definitions.get(khilaf)
        if definition is not None:
            generals[owner] = GeneralLamChoice(khilaf, definition.default)
    return LamProfile(
        selected=selected,
        taa=generals.get("lam_after_taa"),
        zhaa=generals.get("lam_after_zhaa"),
    )


def catalogue_registers() -> dict[str, tuple[VariantSpan, ...]]:
    """Occurrence spans per lam selector, in the source's own coordinates."""
    registers: dict[str, list[VariantSpan]] = {
        owner: [] for owner in SELECTOR_JUNCTIONS
    }
    for site in SITES:
        word = Location(site.source.surah, site.source.ayah, site.source.word)
        requires = site.junction or SELECTOR_JUNCTIONS[site.owner]
        registers[site.owner].append(VariantSpan((word,), "word", requires))
    return {owner: tuple(spans) for owner, spans in registers.items()}


def dynamic_sites(profile: LamProfile) -> dict:
    """Structural resolvers for the taa and zhaa general selectors."""

    def resolve(score, boundaries):
        return general_sites(score, boundaries, profile)

    return {scope: resolve for scope in GENERAL_SELECTORS.values()}


__all__ = [
    "GENERAL_SELECTORS",
    "LamSite",
    "SELECTOR_JUNCTIONS",
    "SITES",
    "catalogue_registers",
    "dynamic_sites",
    "selector_profile",
]
