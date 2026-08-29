from __future__ import annotations

import collections

import pytest
from conftest import performance_for

from quranic_phonemizer.engine.classifier import RuleSet
from quranic_phonemizer.engine.laws import check_performance
from quranic_phonemizer.engine.plan import ConflictError, Phase, Plan, Realize, Verdict
from quranic_phonemizer.model.address import OccurrenceId, Script, SlotId, VerseRef
from quranic_phonemizer.model.canon import CanonLetter, Rule
from quranic_phonemizer.model.performance import (
    Aspect,
    Consonant,
    Hosts,
    MergedInto,
    Occurrence,
)
from quranic_phonemizer.riwayat.hafs import rule_tables
from quranic_phonemizer.rules.noon_sakinah import NoonSakinah

FOLLOWERS = rule_tables().followers_of_noon
RULES = RuleSet({Phase.MERGE: (NoonSakinah(followers=FOLLOWERS),)})


@pytest.mark.parametrize("script", list(Script))
def test_rule_plan_laws_hold_over_a_corpus_sample(packed, hafs, script):
    if script is Script.INDOPAK:
        pytest.skip("IndoPak has no packed corpus yet; L1 covers it")
    for surah in (1, 2, 78, 112, 114):
        for ayah in range(1, min(11, len(packed.surah_info[str(surah)]) + 1)):
            score, performance = performance_for(
                packed, hafs, surah, ayah, RULES, script
            )
            check_performance(performance, score)


def test_full_rules_share_nasal_merger_ownership(packed, hafs):
    score, performance = performance_for(packed, hafs, 2, 1)
    check_performance(performance, score)


def test_a_merger_has_matching_source_and_host_edges(packed, hafs):
    _, performance = performance_for(packed, hafs, 2, 5, RULES)
    merges = [a for a in performance.attributions if isinstance(a, MergedInto)]
    hosts = {
        (a.sound, a.by) for a in performance.attributions if isinstance(a, Hosts)
    }
    assert merges
    assert all((merge.sound, merge.by) in hosts for merge in merges)


def test_classification_only_rules_still_name_their_sound(packed, hafs):
    _, performance = performance_for(packed, hafs, 2, 6, RULES)
    izhar = [o for o in performance.occurrences if o.rule is Rule.IZHAR]
    attributed = {a.by for a in performance.attributions}
    classified = {m.by for m in performance.modifiers}
    assert izhar
    assert all(o.id not in attributed and o.id in classified for o in izhar)


def test_conflicting_effects_name_the_existing_rule():
    plan = Plan()
    slot = SlotId(VerseRef(1, 1), 0)
    sound = Consonant(CanonLetter.NOON)
    for rule in (Rule.IKHFAA, Rule.IQLAB):
        occurrence = Occurrence(
            OccurrenceId(slot.verse, hash(rule) % 1000), rule, (slot,)
        )
        verdict = Verdict(
            occurrence, (Realize(slot, Aspect.CONSONANT, sound),)
        )
        if rule is Rule.IKHFAA:
            plan.record(Phase.MERGE, verdict)
        else:
            with pytest.raises(ConflictError, match="ikhfaa"):
                plan.record(Phase.MERGE, verdict)


def test_every_attribution_names_a_real_occurrence(packed, hafs):
    _, performance = performance_for(packed, hafs, 2, 2, RULES)
    known = {o.id for o in performance.occurrences}
    assert all(a.by is None or a.by in known for a in performance.attributions)
    counts = collections.Counter(
        a.by for a in performance.attributions if isinstance(a, Hosts)
    )
    assert counts
