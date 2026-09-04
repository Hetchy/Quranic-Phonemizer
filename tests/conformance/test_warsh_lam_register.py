from __future__ import annotations

from collections import Counter
from functools import lru_cache

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Location, Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import CanonLetter, Rule
from tests.support.boundary import plan_for

COUPLED_DHAT_YAA = frozenset({
    Location(2, 125, 11), Location(17, 18, 16), Location(84, 12, 1),
    Location(87, 12, 2), Location(88, 4, 1), Location(92, 15, 2),
    Location(111, 3, 1),
})
COUPLED_VERSE_HEADS = frozenset({
    Location(75, 31, 4), Location(87, 15, 4), Location(96, 10, 3),
})
SEPARATED = frozenset({
    Location(2, 233, 36), Location(4, 128, 13), Location(20, 86, 14),
    Location(21, 44, 6), Location(57, 16, 21),
})
FINAL_WAQF = frozenset({
    Location(2, 27, 14), Location(2, 249, 2), Location(6, 119, 11),
    Location(7, 118, 3), Location(13, 21, 8), Location(13, 25, 14),
    Location(16, 58, 5), Location(38, 20, 5), Location(43, 17, 8),
})
SALSAL = frozenset({
    Location(15, 26, 5), Location(15, 28, 9), Location(15, 33, 8),
    Location(55, 14, 4),
})


@lru_cache(maxsize=None)
def _built(verse: VerseRef):
    package = recitation(Riwayah.WARSH)
    words = package.words(verse)
    return package, words, package.build(
        package.read(Script.UTHMANI, verse, words)
    )


def _target(location: Location):
    _, _, built = _built(location.verse)
    lams = [
        slot for slot in built.score.words[location.word - 1].slots
        if slot.letter is CanonLetter.LAM
    ]
    return lams[0]


def _weight_rules(location: Location, *, stopped: bool) -> tuple[Rule, ...]:
    package, words, built = _built(location.verse)
    boundary = (
        plan_for(len(words), isolated=location.word)
        if stopped else plan_for(
            len(words), ibtidaa=location.word, wasl=location.word
        )
    )
    performance = package.perform(built.score, boundary)
    target = _target(location)
    return tuple(
        occurrence.rule
        for occurrence in performance.occurrences
        if target.id in occurrence.subjects
        and occurrence.rule in {Rule.TAFKHEEM, Rule.TARQEEQ}
    )


def test_the_finite_register_subtotals_are_exact_and_disjoint():
    registers = {
        "coupled": COUPLED_DHAT_YAA | COUPLED_VERSE_HEADS,
        "separated": SEPARATED,
        "final_waqf": FINAL_WAQF,
        "salsal": SALSAL,
    }

    assert Counter({name: len(rows) for name, rows in registers.items()}) == Counter({
        "coupled": 10,
        "separated": 5,
        "final_waqf": 9,
        "salsal": 4,
    })
    assert sum(map(len, registers.values())) == len(set().union(*registers.values()))
    assert Location(21, 44, 6) in SEPARATED
    assert Location(21, 44, 6) not in FINAL_WAQF


@pytest.mark.parametrize("location", sorted(COUPLED_DHAT_YAA))
def test_every_default_dhat_yaa_pair_is_fath_plus_one_tafkheem(location):
    assert _weight_rules(location, stopped=True) == (Rule.TAFKHEEM,)


@pytest.mark.parametrize("location", sorted(COUPLED_VERSE_HEADS))
def test_every_default_verse_head_pair_is_taqlil_plus_one_tarqiq(location):
    assert _weight_rules(location, stopped=True) == (Rule.TARQEEQ,)


@pytest.mark.parametrize("location", sorted(SEPARATED))
def test_every_alif_separated_default_has_one_tafkheem_owner(location):
    assert _weight_rules(location, stopped=True) == (Rule.TAFKHEEM,)


@pytest.mark.parametrize("location", sorted(FINAL_WAQF))
def test_final_lam_waqf_replaces_the_ordinary_owner_without_stacking(location):
    assert _weight_rules(location, stopped=True) == (Rule.TAFKHEEM,)
    assert _weight_rules(location, stopped=False) == (Rule.TAFKHEEM,)


@pytest.mark.parametrize("location", sorted(SALSAL))
def test_salsal_keeps_both_pronounced_lams_explicitly_light(location):
    package, words, built = _built(location.verse)
    performance = package.perform(
        built.score, plan_for(len(words), isolated=location.word)
    )
    lams = [
        slot for slot in built.score.words[location.word - 1].slots
        if slot.letter is CanonLetter.LAM
    ]
    by_lam = {
        lam.id: tuple(
            occurrence.rule
            for occurrence in performance.occurrences
            if lam.id in occurrence.subjects
            and occurrence.rule in {Rule.TAFKHEEM, Rule.TARQEEQ}
        )
        for lam in lams
    }

    assert len(lams) == 2
    assert by_lam[lams[0].id] == (Rule.TARQEEQ,)
    assert by_lam[lams[1].id] == (Rule.TARQEEQ,)


@pytest.mark.parametrize(
    "location",
    (
        Location(2, 25, 5),
        Location(3, 191, 17),
        Location(2, 210, 8),
        Location(2, 264, 27),
        Location(2, 16, 5),
    ),
)
def test_nearby_shapes_and_an_unrelated_inclination_witness_are_not_claimed(
    location,
):
    package, words, built = _built(location.verse)
    performance = package.perform(
        built.score, plan_for(len(words), isolated=location.word)
    )
    target_lams = {
        slot.id for slot in built.score.words[location.word - 1].slots
        if slot.letter is CanonLetter.LAM
    }

    assert not any(
        occurrence.rule is Rule.TAFKHEEM
        and target_lams.intersection(occurrence.subjects)
        for occurrence in performance.occurrences
    )
