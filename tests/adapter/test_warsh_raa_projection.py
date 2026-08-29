from __future__ import annotations

import unicodedata
from dataclasses import dataclass

import pytest

from quranic_phonemizer.model.address import Location, Script, SourceLocation
from quranic_phonemizer.model.canon import CanonLetter
from quranic_phonemizer.riwayat.warsh.raa import BY_OWNER, SITES
from quranic_phonemizer.riwayat.warsh.resources import (
    ARTIFACT,
    corpus,
    script_adapter,
)


@dataclass(frozen=True, slots=True)
class Fixture:
    owner: str
    source: tuple[int, int, int]
    canonical: tuple[int, int, int]
    text: str


FIXTURES = (
    Fixture(
        "raa_fixed_ibrahim_heavy",
        (2, 124, 10),
        (2, 125, 10),
        "إِبْرَٰهِيمَ",
    ),
    Fixture(
        "raa_fixed_israil_heavy",
        (2, 39, 2),
        (2, 40, 2),
        "إِسْرَآءِيلَ",
    ),
    Fixture(
        "raa_fixed_imran_heavy",
        (3, 33, 9),
        (3, 33, 9),
        "عِمْرَٰنَ",
    ),
    Fixture(
        "raa_fixed_repeated_heavy",
        (2, 229, 13),
        (2, 231, 13),
        "ضِرَاراٗ",
    ),
    Fixture(
        "raa_fixed_hidhrahum_light",
        (4, 101, 26),
        (4, 102, 26),
        "حِذْرَهُمْ",
    ),
    Fixture(
        "raa_fixed_other_ashir_light",
        (22, 13, 10),
        (22, 13, 10),
        "اَ۬لْعَشِيرُۖ",
    ),
)


def _entry(location: Location):
    return corpus().entries[corpus().canonical_to_runtime[location]]


def test_runtime_fixtures_match_the_independent_selected_source_rows():
    fixture_keys = {
        (fixture.owner, Location(*fixture.canonical)) for fixture in FIXTURES
    }
    actual = tuple(
        Fixture(
            site.owner,
            (site.source.surah, site.source.ayah, site.source.word),
            (site.canonical.surah, site.canonical.ayah, site.canonical.word),
            site.text,
        )
        for site in SITES
        if (site.owner, site.canonical) in fixture_keys
    )

    assert actual == FIXTURES


def test_every_finite_register_member_has_separate_source_and_canonical_evidence():
    actual = {(site.owner, site.key) for site in SITES}
    expected = {
        (owner, key)
        for owner, keys in BY_OWNER.items()
        for key in keys
    }

    assert actual == expected
    assert len(SITES) == len(actual)
    for site in SITES:
        entry = _entry(site.canonical)
        assert entry.text == site.text
        assert entry.sources[0].location == site.source
        assert tuple(unicodedata.name(char) for char in entry.text)


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda row: row.owner)
def test_every_fixture_preserves_exact_text_codepoints_and_alignment(fixture):
    location = Location(*fixture.canonical)
    entry = _entry(location)

    assert entry.text == fixture.text
    assert entry.sources[0].location == SourceLocation(ARTIFACT, *fixture.source)
    assert tuple(unicodedata.name(char) for char in entry.text)


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda row: row.owner)
def test_every_fixture_projects_an_ordinary_canonical_raa(fixture):
    location = Location(*fixture.canonical)
    reading = script_adapter(Script.UTHMANI).read(
        location.verse, ((location, fixture.text),)
    )

    assert any(cluster.letter is CanonLetter.RA for cluster in reading.clusters)
    assert all(
        mark.role not in {"tafkheem", "tarqeeq"}
        for cluster in reading.clusters
        for mark in cluster.marks
    )


@pytest.mark.parametrize(
    ("ref", "text"),
    (
        ((10, 16, 14), "عُمُراٗ"),
        ((35, 11, 22), "مُّعَمَّرٖ"),
        ((63, 4, 18), "فَاحْذَرْهُمْۖ"),
    ),
)
def test_source_lookalikes_supply_structure_without_a_weight_hint(ref, text):
    location = Location(*ref)
    entry = _entry(location)
    reading = script_adapter(Script.UTHMANI).read(
        location.verse, ((location, entry.text),)
    )

    assert entry.text == text
    assert any(cluster.letter is CanonLetter.RA for cluster in reading.clusters)
    assert all(
        mark.role not in {"tafkheem", "tarqeeq"}
        for cluster in reading.clusters
        for mark in cluster.marks
    )
