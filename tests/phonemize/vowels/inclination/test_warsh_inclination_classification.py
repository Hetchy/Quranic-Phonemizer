"""Closed registers and canonical precedence for fixed Warsh inclination."""
from __future__ import annotations

from collections import Counter

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Location, Riwayah, Script
from quranic_phonemizer.model.canon import CanonLetter as L
from quranic_phonemizer.model.canon import Quality
from quranic_phonemizer.riwayat.warsh.inclination import (
    FIXED_KUBRA,
    HAA_OPENINGS,
    HAA_VERSE_HEADS,
    LAM_COUPLED_WAQF_ONLY,
    LAM_DHAT_YAA,
    LAM_VERSE_HEADS,
    NAMED_SITES,
    RAA_OPENINGS,
    RAA_SEEN_BEFORE_SAKIN,
    VERSE_HEAD_SURAHS,
    dhat_yaa_locations,
    dhat_yaa_register,
    is_inclination_witness,
    mark_sequence_family,
)
from quranic_phonemizer.riwayat.warsh.lam import SITES as LAM_SITES
from quranic_phonemizer.riwayat.warsh.resources import corpus

_MARKED_RAA_SEEN = frozenset({
    Location(6, 76, 5), Location(11, 70, 2),
    Location(12, 24, 8), Location(12, 28, 2),
    Location(20, 10, 2), Location(21, 36, 2),
    Location(27, 10, 4), Location(27, 40, 16),
    Location(28, 31, 5), Location(35, 8, 6),
    Location(37, 55, 2), Location(53, 11, 5),
    Location(53, 13, 2), Location(53, 18, 2),
    Location(81, 23, 2), Location(96, 7, 2),
})


def _score_word(location: Location):
    package = recitation(Riwayah.WARSH)
    words = package.words(location.verse)
    built = package.build(package.read(Script.UTHMANI, location.verse, words))
    return built.score.words[location.word - 1]


def _qualities(location: Location) -> tuple[Quality, ...]:
    return tuple(
        slot.nucleus.stopped.quality
        for slot in _score_word(location).slots
        if slot.nucleus.stopped.quality is not None
    )


def test_the_u06ea_sequence_partition_is_exhaustive():
    counts = Counter()
    for entry in corpus().entries.values():
        for offset, char in enumerate(entry.text):
            if char == "۪":
                counts[mark_sequence_family(entry.text, offset)] += 1

    assert counts == Counter({
        "initial_alif": 692,
        "carrier": 1700,
        "dagger": 145,
        "special": 32,
    })


def test_the_short_taqlil_audit_is_exactly_the_raa_seen_family():
    found = frozenset(
        location
        for location, entry in corpus().entries.items()
        for offset, char in enumerate(entry.text)
        if char == "۪"
        and mark_sequence_family(entry.text, offset) == "special"
        and is_inclination_witness(entry.text, offset)
        and entry.text[:offset].endswith(("ر", "رّ"))
        and entry.text[offset + 1:offset + 4] in {"ء۪ا", "أ۪ى"}
    )

    assert found == _MARKED_RAA_SEEN


@pytest.mark.parametrize("location", sorted(_MARKED_RAA_SEEN))
def test_every_marked_raa_seen_has_both_taqlil_witnesses(location):
    slots = _score_word(location).slots
    raa = next(slot for slot in slots if slot.letter is L.RA)
    hamza = next(slot for slot in slots if slot.letter is L.HAMZA)

    assert raa.nucleus.joined.form.value == "short"
    assert raa.nucleus.joined.quality is Quality.TAQLIL
    assert hamza.nucleus.joined.quality is Quality.TAQLIL


@pytest.mark.parametrize("location", sorted(RAA_SEEN_BEFORE_SAKIN))
def test_every_pre_sakin_raa_seen_opens_in_wasl_and_returns_at_waqf(location):
    slots = _score_word(location).slots
    raa = next(slot for slot in slots if slot.letter is L.RA)
    hamza = next(
        slot for slot in slots
        if slot.letter is L.HAMZA and slot.nucleus.sounds_long
    )

    assert (raa.nucleus.joined.quality, raa.nucleus.stopped.quality) == (
        Quality.A, Quality.TAQLIL,
    )
    assert (hamza.nucleus.joined.quality, hamza.nucleus.stopped.quality) == (
        Quality.A, Quality.TAQLIL,
    )


def test_the_closed_precedence_registers_have_the_documented_sizes():
    assert len(FIXED_KUBRA) == 1
    assert len(HAA_OPENINGS) == 7
    assert len(RAA_OPENINGS) == 6
    assert len(RAA_SEEN_BEFORE_SAKIN) == 6
    assert len(HAA_VERSE_HEADS) == 25
    assert len(LAM_DHAT_YAA) == 7
    assert len(LAM_VERSE_HEADS) == 3
    assert VERSE_HEAD_SURAHS == frozenset({20, 53, 70, 75, 79, 80, 87, 91, 92, 93, 96})


@pytest.mark.parametrize("location", sorted(FIXED_KUBRA))
def test_fixed_kubra_precedes_the_mark_supplied_taqlil_default(location):
    assert Quality.KUBRA in _qualities(location)
    assert Quality.TAQLIL not in _qualities(location)


@pytest.mark.parametrize("location", sorted(HAA_OPENINGS | RAA_OPENINGS))
def test_every_fixed_opening_is_taqlil(location):
    assert Quality.TAQLIL in _qualities(location)


@pytest.mark.parametrize("location", sorted(LAM_DHAT_YAA))
def test_lam_dhat_yaa_reserves_its_default_fath_for_the_coupled_owner(location):
    assert Quality.TAQLIL not in _qualities(location)


@pytest.mark.parametrize("location", sorted(LAM_VERSE_HEADS))
def test_lam_verse_heads_expose_the_default_inclination_side(location):
    assert Quality.TAQLIL in _qualities(location)


@pytest.mark.parametrize("location", sorted(HAA_VERSE_HEADS))
def test_pronominal_haa_heads_keep_the_fixed_default_fath(location):
    assert Quality.TAQLIL not in _qualities(location)


def _verse_lengths() -> dict[tuple[int, int], int]:
    lengths: dict[tuple[int, int], int] = {}
    for location in corpus().entries:
        key = (location.surah, location.ayah)
        lengths[key] = max(lengths.get(key, 0), location.word)
    return lengths


def test_the_dhat_yaa_register_is_closed_and_disjoint():
    rows = dhat_yaa_register()
    assert len(rows) == 1154
    locations = dhat_yaa_locations()
    assert len(locations) == len(rows)
    owned_elsewhere = (
        FIXED_KUBRA | HAA_OPENINGS | RAA_OPENINGS | HAA_VERSE_HEADS
        | LAM_DHAT_YAA | LAM_VERSE_HEADS | RAA_SEEN_BEFORE_SAKIN
        | _MARKED_RAA_SEEN | frozenset(NAMED_SITES)
        | frozenset(site.canonical for site in LAM_SITES)
    )
    assert not locations & owned_elsewhere
    lengths = _verse_lengths()
    verse_final = {
        location for location in locations
        if location.surah in VERSE_HEAD_SURAHS
        and location.word == lengths[(location.surah, location.ayah)]
    }
    fathatan = {
        _row_location(row) for row in rows if row["requires"] == "waqf"
    }
    # Fixed verse heads stay out of the register; a fathatan host is the
    # one shape the verse-head predicate never owns.
    assert verse_final <= fathatan


def _row_location(row) -> Location:
    return Location(*(int(part) for part in row["canonical"].split(":")))


def test_every_dhat_yaa_row_matches_its_written_shape():
    entries = corpus().entries
    for row in dhat_yaa_register():
        location = _row_location(row)
        text = entries[location].text
        assert text == row["text"], row["canonical"]
        witness = any(
            char == "۪" and is_inclination_witness(text, offset)
            for offset, char in enumerate(text)
        )
        fathatan = text.rstrip("ۖۗۘۙۚۛۜ۩ٓ").endswith("ىٗ")
        if row["requires"] == "waqf":
            assert fathatan and not witness, row["canonical"]
        else:
            assert witness, row["canonical"]


def test_dhat_yaa_spot_members_and_exclusions():
    locations = dhat_yaa_locations()
    assert Location(2, 16, 5) in locations       # بِالْهُد۪ىٰ
    assert Location(2, 5, 3) in locations        # هُدىٗ
    assert Location(8, 43, 8) not in locations   # arakahum
    assert Location(2, 6, 8) not in locations    # أَبْصٰ۪رِهِمْ, alif before raa
    assert Location(2, 19, 19) not in locations  # بِالْكٰ۪فِرِينَ
    assert Location(20, 2, 5) not in locations   # verse head in surah 20
    assert Location(79, 43, 4) not in locations  # ذِكْر۪يٰهَآ, fixed taqlil


def test_the_lam_registers_and_masks_agree_across_modules():
    by_owner: dict[str, set[Location]] = {}
    for site in LAM_SITES:
        by_owner.setdefault(site.owner, set()).add(site.canonical)
    assert by_owner["lam_dhat_yaa"] == set(LAM_DHAT_YAA)
    assert by_owner["lam_verse_heads"] == set(LAM_VERSE_HEADS)
    waqf_junctions = {
        site.canonical for site in LAM_SITES if site.junction == "waqf"
        and site.owner == "lam_dhat_yaa"
    }
    assert waqf_junctions == set(LAM_COUPLED_WAQF_ONLY)
