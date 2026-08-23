"""Khilaf choices that change the canonical Score."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.address import KhilafId, Location
from ..model.canon import CanonLetter, Nucleus, Onset, Quality, SlotOrigin
from ..model.inscription import SlotFact
from ..orthography.adapter import Reading
from .draft import _Draft
from .passes import vocalised, word_spans


@dataclass(frozen=True, slots=True)
class VowelSite:
    khilaf: KhilafId
    index: int
    options: dict[str, Quality]
    default: str
    forms: frozenset[str]


@dataclass(frozen=True, slots=True)
class VowelKhilaf:
    sites: tuple[VowelSite, ...] = ()

    def of(self, form: str) -> VowelSite | None:
        return next((site for site in self.sites if form in site.forms), None)


@dataclass(frozen=True, slots=True)
class LetterSite:
    khilaf: KhilafId
    location: Location
    index: int
    options: dict[str, CanonLetter]
    default: str


@dataclass(frozen=True, slots=True)
class MaddSite:
    khilaf: KhilafId
    locations: frozenset[Location]
    default: str


@dataclass(frozen=True, slots=True)
class CanonicalKhilaf:
    vowel: VowelKhilaf = field(default_factory=VowelKhilaf)
    letters: tuple[LetterSite, ...] = ()
    madd: MaddSite | None = None


def apply_canonical_khilaf(khilaf: CanonicalKhilaf):
    """Build the pass that applies every Score-changing choice."""

    def apply(reading: Reading, drafts, lexicon, scribe, selection) -> None:
        del lexicon
        spans = word_spans(reading, drafts)
        for location, span in zip(reading.words, spans):
            if not span:
                continue
            _apply_vowel(khilaf.vowel, span, selection)
            _apply_letter(khilaf.letters, location, span, selection)
            _apply_madd(
                khilaf.madd, location, span, drafts, reading, scribe, selection
            )

    return apply


def _apply_vowel(khilaf, span, selection) -> None:
    site = khilaf.of(vocalised(span))
    if site is None:
        return
    chosen = selection.chosen(site.khilaf) or site.default
    quality = _chosen(site.khilaf, chosen, site.options)
    span[site.index].nucleus = span[site.index].nucleus.with_quality(quality)


def _apply_letter(sites, location, span, selection) -> None:
    site = next((item for item in sites if item.location == location), None)
    if site is None:
        return
    chosen = selection.chosen(site.khilaf) or site.default
    span[site.index].letter = _chosen(site.khilaf, chosen, site.options)


def _apply_madd(site, location, span, drafts, reading, scribe, selection) -> None:
    if site is None or location not in site.locations:
        return
    chosen = selection.chosen(site.khilaf) or site.default
    if chosen == "madd_lazim":
        return
    if chosen != "tasheel":
        _invalid(site.khilaf, chosen, ("madd_lazim", "tasheel"))
    first = span[0]
    length_offsets = scribe.evidence_offsets(first, SlotFact.VOWEL_LENGTH)
    quality_offsets = scribe.evidence_offsets(first, SlotFact.VOWEL_QUALITY)
    cluster, source_offset = _tashil_source(
        reading, first, length_offsets, quality_offsets
    )
    first.nucleus = Nucleus.short(Quality.A)
    eased = _Draft(
        letter=CanonLetter.HAMZA,
        onset=Onset.TASHIL,
        nucleus=Nucleus.short(Quality.A),
        origin=SlotOrigin.WRITTEN,
        cluster=cluster,
        onset_declared=True,
        nucleus_declared=True,
    )
    drafts.insert(drafts.index(first) + 1, eased)
    for offset in length_offsets:
        scribe.withdraw_evidence(offset, first, SlotFact.VOWEL_LENGTH)
    if not quality_offsets and length_offsets:
        scribe.evidence(length_offsets[0], first, SlotFact.VOWEL_QUALITY)
    scribe.evidence(source_offset, eased, SlotFact.LETTER)


def _tashil_source(
    reading, first, length_offsets, quality_offsets,
) -> tuple[int, int]:
    """Locate the written second hamza, including compact script forms."""
    own_offset = (
        length_offsets[0]
        if length_offsets
        else quality_offsets[0]
        if quality_offsets
        else reading.clusters[first.cluster].offset
    )
    following = first.cluster + 1
    if following >= len(reading.clusters):
        return first.cluster, own_offset
    cluster = reading.clusters[following]
    if (
        cluster.word == reading.clusters[first.cluster].word
        and cluster.seat
    ):
        return following, cluster.offset
    return first.cluster, own_offset


def _chosen(khilaf, chosen, options):
    try:
        return options[chosen]
    except KeyError:
        _invalid(khilaf, chosen, options)


def _invalid(khilaf, chosen, options) -> None:
    raise ValueError(
        f"{khilaf.value}: {chosen!r} is not an option; expected one of "
        f"{sorted(options)}"
    )
