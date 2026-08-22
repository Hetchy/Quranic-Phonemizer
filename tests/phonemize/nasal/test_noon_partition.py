from __future__ import annotations

from conftest import performance_for, score_for
from quranic_phonemizer.engine.classifier import RuleSet
from quranic_phonemizer.engine.laws import check_performance
from quranic_phonemizer.engine.plan import Phase
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction
from quranic_phonemizer.model.canon import CanonLetter, Rule
from quranic_phonemizer.riwayat.hafs import rule_tables
from quranic_phonemizer.rules.noon_sakinah import NoonSakinah


FOLLOWERS = rule_tables().followers_of_noon
RULES = RuleSet({Phase.MERGE: (NoonSakinah(followers=FOLLOWERS),)})


def test_the_noon_outcomes_partition_the_alphabet():
    sets = (*FOLLOWERS.by_rule.values(), FOLLOWERS.remainder())
    union: set[CanonLetter] = set()
    for one in sets:
        assert not union & one
        union |= one
    assert union == set(CanonLetter) - FOLLOWERS.never_follows


def test_each_noon_family_has_its_complete_trigger_set():
    by_rule = FOLLOWERS.by_rule
    assert len(by_rule[Rule.IZHAR]) == 6
    assert len(by_rule[Rule.IQLAB]) == 1
    assert len(by_rule[Rule.IDGHAM_BI_GHUNNAH]) == 4
    assert len(by_rule[Rule.IDGHAM_BILA_GHUNNAH]) == 2
    assert len(FOLLOWERS.remainder()) == 15


def test_tanwin_and_written_noon_use_the_same_classifier(packed, hafs):
    score, performance = performance_for(packed, hafs, 2, 5, RULES)
    triggers = {
        slot.id
        for slot in score.slots()
        if slot.letter is CanonLetter.NOON and slot.nucleus.is_silent
    }
    named = {
        slot
        for occurrence in performance.occurrences
        for slot in (occurrence.parts.source, occurrence.parts.host)
        if slot is not None
    }
    assert Rule.IDGHAM_BILA_GHUNNAH in {
        occurrence.rule for occurrence in performance.occurrences
    }
    assert triggers & named


def test_no_noon_family_crosses_an_explicit_stop(packed, hafs):
    score = score_for(packed, hafs, 2, 5)
    boundaries = BoundaryPlan(
        (Junction.STOP,) * (len(score.words) - 1) + (Junction.EDGE,)
    )
    performance = perform(score, RULES, boundaries)
    check_performance(performance, score)
    word_of = {
        slot.id: index
        for index, word in enumerate(score.words)
        for slot in word.slots
    }
    for occurrence in performance.occurrences:
        participants = (occurrence.parts.source, occurrence.parts.host)
        words = {
            word_of[slot]
            for slot in participants
            if slot is not None and slot in word_of
        }
        assert len(words) <= 1
