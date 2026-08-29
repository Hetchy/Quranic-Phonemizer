"""The catalogue and the fixture registry are the same inventory.

Read both ways, with no list of exceptions: a rule published with no case
fails here, and so does a registered rule the catalogue dropped.
"""
from __future__ import annotations

from quranic_phonemizer import tajweed_rules
from tests.hardcase.registry import RULE_FIXTURES, FixtureRef


def _catalogued() -> set[str]:
    return {
            rule.id.value
        for riwayah in ("hafs", "warsh")
        for rule in tajweed_rules(riwayah)
    }


def test_every_catalogued_rule_has_a_fixture():
    uncovered = sorted(_catalogued() - set(RULE_FIXTURES))
    assert not uncovered, (
        f"published with no fixture: {uncovered}. Write the case; there is "
        f"no deferred list to put it on."
    )


def test_every_registered_fixture_names_a_catalogued_rule():
    stale = sorted(set(RULE_FIXTURES) - _catalogued())
    assert not stale, f"registered but not published: {stale}"


def test_every_registered_fixture_is_a_nonempty_tuple_of_cases():
    for rule, fixtures in RULE_FIXTURES.items():
        assert isinstance(fixtures, tuple), rule
        assert fixtures, rule
        assert all(isinstance(fixture, FixtureRef) for fixture in fixtures), rule
        assert all(fixture.source.startswith("tests/") for fixture in fixtures), rule
