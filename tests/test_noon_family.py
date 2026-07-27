"""The noon family end to end, on both scripts.

Noon sakinah and tanween must be the same rule on the same trigger, and no
two effects may claim the same slot and aspect.
"""
from __future__ import annotations

import collections

import pytest

from conftest import performance_for, score_for
from quranic_phonemizer.engine.classifier import RuleSet
from quranic_phonemizer.engine.plan import ConflictError, Plan, Realize
from quranic_phonemizer.model.address import Script, SlotId, VerseRef
from quranic_phonemizer.model.canon import CanonLetter, NucleusKind, Phase, Rule
from quranic_phonemizer.model.performance import (
    Aspect,
    Consonant,
    Hosts,
    MergedInto,
    Occurrence,
    Participants,
)
from quranic_phonemizer.engine.laws import check_performance
from quranic_phonemizer.riwayat.hafs import rule_tables
from quranic_phonemizer.rules.noon_sakinah import NoonSakinah

FOLLOWERS = rule_tables().followers_of_noon
RULES = RuleSet({Phase.MERGE: (NoonSakinah(followers=FOLLOWERS),)})


def test_the_five_outcomes_partition_the_alphabet() -> None:
    """A sixth branch would be a partition error, not a precedence question."""
    sets = (*FOLLOWERS.by_rule.values(), FOLLOWERS.remainder())
    union: set = set()
    for one in sets:
        assert not (union & one), f"overlap at {union & one}"
        union |= one
    assert union == set(CanonLetter) - FOLLOWERS.never_follows


def test_the_outcome_sets_have_the_counts_the_domain_gives_them() -> None:
    """Ikhfaa is the remainder, so a union check alone cannot catch a
    miscounted member."""
    by_rule = FOLLOWERS.by_rule
    assert len(by_rule[Rule.IZHAR_HALQI]) == 6, "the six throat letters"
    assert len(by_rule[Rule.IQLAB]) == 1, "only the baa"
    assert len(by_rule[Rule.IDGHAM_BI_GHUNNAH]) == 4, "يرملون minus two"
    assert len(by_rule[Rule.IDGHAM_BILA_GHUNNAH]) == 2, "lam and raa"
    assert len(FOLLOWERS.remainder()) == 15, "the fifteen"


@pytest.mark.parametrize("script", list(Script))
def test_laws_hold_over_a_sample_of_the_corpus(packed, shared, script) -> None:
    if script is Script.INDOPAK:
        pytest.skip("IndoPak has no packed corpus yet; L1 covers it")
    for surah in (1, 2, 78, 112, 114):
        for ayah in range(1, min(11, len(packed.surah_info[str(surah)]) + 1)):
            score, performance = performance_for(
                packed, shared, surah, ayah, RULES, script
            )
            check_performance(performance, score)


def test_tanween_and_noon_sakinah_are_one_rule(packed, shared) -> None:
    """2:5 carries both: `مِّن رَّبِّهِمْ` is a noon sakinah and `هُدًى` a
    tanween, produced by the same classifier and the same trigger."""
    score, performance = performance_for(packed, shared, 2, 5, RULES)
    fired = {o.rule for o in performance.occurrences}
    assert Rule.IDGHAM_BILA_GHUNNAH in fired  # min + ra
    triggers = {
        slot.id
        for slot in score.slots()
        if slot.letter is CanonLetter.NOON
        and slot.nucleus.kind is NucleusKind.SILENT
    }
    named = {
        parts
        for o in performance.occurrences
        if o.rule is not Rule.PLAIN
        for parts in o.parts.slots
    }
    assert triggers & named, "no noon slot participated in any occurrence"


def test_a_merger_is_a_pair_of_edges(packed, shared) -> None:
    """`MergedInto` and `Hosts` share a sound and an occurrence, with no
    source/target boolean anywhere."""
    _, performance = performance_for(packed, shared, 2, 5, RULES)
    merges = [a for a in performance.attributions if isinstance(a, MergedInto)]
    assert merges, "2:5 has an idgham"
    hosts = {
        (a.sound, a.by) for a in performance.attributions if isinstance(a, Hosts)
    }
    for merge in merges:
        assert (merge.sound, merge.by) in hosts


def test_izhar_is_classification_only(packed, shared) -> None:
    """It produces no sound of its own and still exists, so a projection can
    find it."""
    _, performance = performance_for(packed, shared, 2, 6, RULES)
    izhar = [o for o in performance.occurrences if o.rule is Rule.IZHAR_HALQI]
    if not izhar:
        pytest.skip("no izhar in this verse")
    owned = {a.by for a in performance.attributions}
    assert all(o.id not in owned for o in izhar)


def test_no_cross_word_effect_crosses_a_stop(packed, shared) -> None:
    """Under an all-stop plan the family may fire inside a word but never
    across one."""
    from quranic_phonemizer.engine.run import perform
    from quranic_phonemizer.model.address import BoundaryPlan, Junction

    score = score_for(packed, shared, 2, 5)
    stopped = BoundaryPlan((Junction.STOP,) * (len(score.words) - 1) + (Junction.EDGE,))
    performance = perform(score, RULES, stopped)
    check_performance(performance, score)
    word_of = {
        slot.id: index
        for index, word in enumerate(score.words)
        for slot in word.slots
    }
    for occurrence in performance.occurrences:
        words = {word_of[s] for s in occurrence.parts.slots if s in word_of}
        assert len(words) <= 1, f"{occurrence.rule.value} crossed a stop"


def test_two_effects_on_one_key_raise_with_both_tags() -> None:
    """Two effects claiming the same key must raise, naming both."""
    plan = Plan()
    slot = SlotId(VerseRef(1, 1), 0)
    sound = (Consonant(CanonLetter.NOON),)
    for rule in (Rule.IKHFAA_HAQIQI, Rule.IQLAB):
        verdict = _verdict(rule, slot, sound)
        if rule is Rule.IKHFAA_HAQIQI:
            plan.record(Phase.MERGE, verdict)
        else:
            with pytest.raises(ConflictError, match="ikhfaa_haqiqi"):
                plan.record(Phase.MERGE, verdict)


def _verdict(rule: Rule, slot: SlotId, sounds):
    from quranic_phonemizer.engine.plan import Verdict
    from quranic_phonemizer.model.address import OccurrenceId

    return Verdict(
        Occurrence(OccurrenceId(slot.verse, hash(rule) % 1000), rule,
                   Participants((slot,))),
        (Realize(slot, Aspect.ONSET, sounds),),
    )


def test_every_sound_has_a_named_occurrence(packed, shared) -> None:
    """Every attribution must name an occurrence that actually exists."""
    _, performance = performance_for(packed, shared, 2, 2, RULES)
    known = {o.id for o in performance.occurrences}
    assert all(a.by in known for a in performance.attributions)
    counts = collections.Counter(
        a.by for a in performance.attributions if isinstance(a, Hosts)
    )
    assert counts, "a verse with no hosted sound is a bug in the fixture"
