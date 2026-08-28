"""Fixed inclination registers and selected-script canonical supplies."""
from __future__ import annotations

from ...canon.passes import word_spans
from ...model.address import Location
from ...model.canon import CanonLetter, Nucleus, Quality, SlotOrigin, VowelState
from ...model.inscription import SlotFact


FIXED_KUBRA = frozenset({Location(20, 1, 1)})
HAA_OPENINGS = frozenset(Location(surah, 1, 1) for surah in range(40, 47))
RAA_OPENINGS = frozenset(Location(surah, 1, 1) for surah in range(10, 16))
VERSE_HEAD_SURAHS = frozenset({20, 53, 70, 75, 79, 80, 87, 91, 92, 93, 96})

HAA_VERSE_HEADS = frozenset(
    {
        Location(79, 27, 6), Location(79, 28, 3), Location(79, 29, 4),
        Location(79, 30, 4), Location(79, 31, 4), Location(79, 32, 2),
        Location(79, 42, 5), Location(79, 44, 3), Location(79, 45, 5),
        Location(79, 46, 9),
        Location(91, 1, 2), Location(91, 2, 3), Location(91, 3, 3),
        Location(91, 4, 3), Location(91, 5, 3), Location(91, 6, 3),
        Location(91, 7, 3), Location(91, 8, 3), Location(91, 9, 4),
        Location(91, 10, 4), Location(91, 11, 3), Location(91, 12, 3),
        Location(91, 13, 7), Location(91, 14, 7), Location(91, 15, 3),
    }
)

LAM_DHAT_YAA = frozenset({
    Location(2, 125, 11), Location(17, 18, 16), Location(84, 12, 1),
    Location(87, 12, 2), Location(88, 4, 1), Location(92, 15, 2),
    Location(111, 3, 1),
})
LAM_VERSE_HEADS = frozenset({
    Location(75, 31, 4), Location(87, 15, 4), Location(96, 10, 3),
})
_NAML_YAA_ZAWAID = Location(27, 36, 8)

_OPENING_TEXTS = frozenset({
    "أَلَٓر۪ۖ", "أَلَٓمِّٓر۪ۖ", "كَٓه۪ي۪عَٓصَٓۖ", "طَه۪ۖ",
    "ح۪مِٓۖ", "ح۪مِٓ",
})
_STOP_SIGNS = frozenset("ۖۗۘۙۚۛۜ۩ٓ")

# `رأى` before a following-word sakin is written without either inclination
# witness in the connected Warsh source. Both qualities return at a stop.
# These are canonical/internal corpus coordinates. Their Warsh public refs are
# 6:78:2, 6:79:2, 16:85:2, 16:86:2, 18:52:1, and 33:22:2.
RAA_SEEN_BEFORE_SAKIN = frozenset({
    Location(6, 77, 2), Location(6, 78, 2),
    Location(16, 85, 2), Location(16, 86, 2),
    Location(18, 53, 1), Location(33, 22, 2),
})


def mark_sequence_family(text: str, offset: int) -> str:
    """Classify one U+06EA by its complete local sequence family."""
    if text.startswith("ا") and offset in {1, 2}:
        return "initial_alif"
    following = text[offset + 1:offset + 2]
    if following in {"ا", "ى", "ي", "ے"}:
        return "carrier"
    if following == "ٰ":
        return "dagger"
    return "special"


def is_inclination_witness(text: str, offset: int) -> bool:
    family = mark_sequence_family(text, offset)
    if family in {"carrier", "dagger"}:
        return text[offset + 1:offset + 2] != "ے"
    return family == "special" and (
        text in _OPENING_TEXTS or _is_raa_short_witness(text, offset)
    )


def _is_raa_short_witness(text: str, offset: int) -> bool:
    """The first of the two marks in the exact `رأى` sequence family."""
    before = text[:offset]
    return (
        (before.endswith("ر") or before.endswith("رّ"))
        and text[offset + 1:offset + 4] in {"ء۪ا", "أ۪ى"}
    )


def _word_text(reading, word: int) -> str:
    offsets = {
        cluster.offset for cluster in reading.clusters if cluster.word == word
    }
    offsets.update(
        mark.offset
        for cluster in reading.clusters if cluster.word == word
        for mark in cluster.marks
    )
    by_offset = {glyph.id.offset: glyph.char for glyph in reading.graphemes}
    return "".join(by_offset[offset] for offset in sorted(offsets))


def _marked_clusters(reading, word: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (index, mark.offset)
        for index, cluster in enumerate(reading.clusters)
        if cluster.word == word
        for mark in cluster.marks
        if mark.role == "inclination_witness"
    )


def _target_for_cluster(span, cluster: int):
    candidates = [
        draft for draft in span
        if draft.cluster == cluster and draft.nucleus.quality is Quality.A
    ]
    if not candidates:
        return None
    return next((draft for draft in candidates if draft.nucleus.sounds_long), candidates[-1])


def _quality(location: Location) -> Quality:
    if location in FIXED_KUBRA:
        return Quality.KUBRA
    if location in LAM_DHAT_YAA:
        return Quality.A
    return Quality.TAQLIL


def _supply_marked(reading, span, word: int, location: Location, scribe) -> None:
    for cluster, offset in _marked_clusters(reading, word):
        target = _target_for_cluster(span, cluster)
        if target is None:
            continue
        target.nucleus = target.nucleus.with_quality(_quality(location))
        if target.origin is SlotOrigin.SPELLED:
            scribe.evidence(offset, target, SlotFact.VOWEL_QUALITY)


def _supply_raa_before_sakin(span, location: Location) -> None:
    """Restore both `رأى` inclinations only in the stopped state."""
    if location not in RAA_SEEN_BEFORE_SAKIN:
        return
    raa = next((draft for draft in span if draft.letter is CanonLetter.RA), None)
    hamza = next(
        (
            draft for draft in span
            if draft.letter is CanonLetter.HAMZA and draft.nucleus.sounds_long
        ),
        None,
    )
    if raa is None or hamza is None:
        raise ValueError(f"{location}: incomplete رأى before-sakin projection")
    raa.nucleus = Nucleus(
        raa.nucleus.joined,
        VowelState(raa.nucleus.stopped.form, Quality.TAQLIL),
    )
    hamza.nucleus = Nucleus(
        hamza.nucleus.joined,
        VowelState(hamza.nucleus.stopped.form, Quality.TAQLIL),
    )


def _supply_fathatan_dhat_yaa(text: str, span, location: Location) -> None:
    plain = text.rstrip("".join(_STOP_SIGNS))
    if not plain.endswith("ىٗ") or location in LAM_DHAT_YAA:
        return
    if not span or span[-1].origin is not SlotOrigin.NUNATION:
        return
    target = span[-2]
    if target.nucleus.quality is Quality.A:
        target.nucleus = Nucleus(
            target.nucleus.joined,
            VowelState(target.nucleus.stopped.form, Quality.TAQLIL),
        )


def _collapse_final_yaa(drafts, span, scribe):
    if len(span) < 2:
        return None
    carrier, target = span[-1], span[-2]
    if not (
        carrier.letter is CanonLetter.YA
        and carrier.nucleus.is_silent
        and target.nucleus.is_short
        and target.nucleus.quality is Quality.A
    ):
        return None
    offsets = scribe.evidence_offsets(carrier, SlotFact.LETTER)
    scribe.withdraw((carrier,))
    drafts.remove(carrier)
    target.nucleus = Nucleus.long(Quality.TAQLIL)
    for offset in offsets:
        scribe.evidence(offset, target, SlotFact.VOWEL_LENGTH)
    return target


def _supply_verse_head(reading, drafts, span, word: int, location, scribe) -> None:
    if (
        location.surah not in VERSE_HEAD_SURAHS
        or word != len(reading.words) - 1
        or location in HAA_VERSE_HEADS
        or location in LAM_DHAT_YAA
    ):
        return
    if any(draft.nucleus.quality in {Quality.TAQLIL, Quality.KUBRA} for draft in span):
        return
    target = _collapse_final_yaa(drafts, span, scribe)
    if target is not None:
        return
    target = span[-1]
    if target.nucleus.is_long and target.nucleus.quality is Quality.A:
        target.nucleus = target.nucleus.with_quality(Quality.TAQLIL)


def _repair_naml_badal_carrier(drafts, span, location, scribe) -> None:
    """Restore Naml's plain alif before the marked medial dhat-yaa as badal.

    This exact interaction was deferred by the yaa-zawaid vertical.
    """
    if location != _NAML_YAA_ZAWAID or len(span) < 3:
        return
    vowel, carrier = span[:2]
    if not (
        vowel.letter is CanonLetter.HAMZA
        and vowel.nucleus.is_short
        and vowel.nucleus.quality is Quality.A
        and carrier.letter is CanonLetter.HAMZA
    ):
        return
    offsets = scribe.evidence_offsets(carrier, SlotFact.LETTER)
    scribe.withdraw((carrier,))
    drafts.remove(carrier)
    span.remove(carrier)
    vowel.nucleus = Nucleus.long(Quality.A)
    for offset in offsets:
        scribe.evidence(offset, vowel, SlotFact.VOWEL_LENGTH)


def supply_inclination(reading, drafts, lexicon, scribe, selection) -> None:
    """Apply the fixed al-Azraq profile after selected-script projection."""
    del lexicon, selection
    if scribe is None:
        return
    spans = word_spans(reading, drafts)
    for word, (location, span) in enumerate(zip(reading.words, spans)):
        if not span:
            continue
        _repair_naml_badal_carrier(drafts, span, location, scribe)
        text = _word_text(reading, word)
        _supply_marked(reading, span, word, location, scribe)
        _supply_raa_before_sakin(span, location)
        _supply_fathatan_dhat_yaa(text, span, location)
        _supply_verse_head(reading, drafts, span, word, location, scribe)


__all__ = [
    "FIXED_KUBRA",
    "HAA_OPENINGS",
    "HAA_VERSE_HEADS",
    "LAM_DHAT_YAA",
    "LAM_VERSE_HEADS",
    "RAA_OPENINGS",
    "RAA_SEEN_BEFORE_SAKIN",
    "VERSE_HEAD_SURAHS",
    "is_inclination_witness",
    "mark_sequence_family",
    "supply_inclination",
]
