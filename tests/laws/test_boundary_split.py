"""The waqf-ending split: `pausal_sukun`, `waqf_taa_marbuta`, `madd_iwad`.

A stopped taa marbuta names two rules on one unit -- one per part -- which a
shared rule identity could not do.
"""
from __future__ import annotations

from conftest import score_for
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction
from quranic_phonemizer.model.canon import CanonLetter, Rule
from quranic_phonemizer.model.performance import Aspect, Consonant, Hosts, Silent
from quranic_phonemizer.riwayat.hafs import HAFS


def _stopped_on(score, word_number: int) -> BoundaryPlan:
    """`word_number` counts from one, as a test case names a word."""
    return BoundaryPlan(
        tuple(
            Junction.STOP if word == word_number - 1 else Junction.JOIN
            for word in range(len(score.words) - 1)
        )
        + (Junction.EDGE,)
    )


def test_a_stopped_taa_marbuta_names_two_rules_one_per_part(packed, hafs) -> None:
    """`ٱلصَّلَاةَ` at 2:3:5, stopped on: the vowel goes silent under
    `pausal_sukun` and the consonant is realized as haa under
    `waqf_taa_marbuta` -- two occurrences, not one shared identity."""
    score = score_for(packed, hafs, 2, 3)
    taa = score.words[4].slots[-1]
    performance = perform(score, HAFS, _stopped_on(score, 5))

    by_rule = {o.rule: o for o in performance.occurrences if taa.id in o.subjects}
    assert Rule.PAUSAL_SUKUN in by_rule
    assert Rule.WAQF_TAA_MARBUTA in by_rule
    assert by_rule[Rule.PAUSAL_SUKUN].id != by_rule[Rule.WAQF_TAA_MARBUTA].id

    silences = {
        a.by for a in performance.attributions
        if isinstance(a, Silent) and taa.id in a.slots and a.aspect is Aspect.VOWEL
    }
    assert silences == {by_rule[Rule.PAUSAL_SUKUN].id}

    hosts = {
        a.by: a.sound for a in performance.attributions
        if isinstance(a, Hosts) and taa.id in a.slots and a.aspect is Aspect.CONSONANT
    }
    assert hosts[by_rule[Rule.WAQF_TAA_MARBUTA].id] is not None
    sound = dict(performance.sounds)[hosts[by_rule[Rule.WAQF_TAA_MARBUTA].id]]
    assert isinstance(sound, Consonant) and sound.letter is CanonLetter.HEH


def test_a_boundary_rule_names_the_junction_it_resolved(packed, hafs) -> None:
    """Stopping on word 5 of 2:3 reads the junction after it; starting there
    reads the one before, which is a different junction on the same word."""
    score = score_for(packed, hafs, 2, 3)
    stopped = perform(score, HAFS, _stopped_on(score, 5))
    waqf = next(
        o for o in stopped.occurrences if o.rule is Rule.WAQF_TAA_MARBUTA
    )
    assert waqf.boundary == 4

    started = perform(score, HAFS, _stopped_on(score, 4))
    wasl = next(
        o for o in started.occurrences
        if o.rule is Rule.WASL_START and o.subjects[0] == score.words[4].slots[0].id
    )
    assert wasl.boundary == 3
