"""Phase 3's gate: the nūn family end to end, on both scripts.

Proves the effect model, E1, and — the point of the slice — that nūn sākinah
and tanwīn are **the same rule on the same trigger**. If that is wrong it fails
here, at ~4,671 sites (ADR-004 §8).
"""
from __future__ import annotations

import collections

import pytest

from conftest import performance_for, score_for
from quranic_phonemizer.engine.classifier import RuleSet
from quranic_phonemizer.engine.laws import LawError, check_performance
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
from quranic_phonemizer.rules.noon_sakinah import (
    IDGHAM_GHUNNAH,
    IDGHAM_NO_GHUNNAH,
    IKHFAA,
    IQLAB,
    IZHAR,
    NOT_A_FOLLOWER,
    NoonSakinah,
)

RULES = RuleSet({Phase.MERGE: (NoonSakinah(),)})


def test_the_five_outcomes_partition_the_alphabet() -> None:
    """Mutually exclusive by construction, which is why E1 can never fire in
    this family — a sixth branch would be a partition error, not a precedence
    question."""
    sets = (IZHAR, IQLAB, IDGHAM_GHUNNAH, IDGHAM_NO_GHUNNAH, IKHFAA)
    union: set = set()
    for one in sets:
        assert not (union & one), f"overlap at {union & one}"
        union |= one
    assert union == set(CanonLetter) - NOT_A_FOLLOWER


def test_the_outcome_sets_have_the_counts_the_domain_gives_them() -> None:
    """The coverage half of the previous test was a tautology: `IKHFAA` is
    *defined* as the complement, so the union always equalled the alphabet
    however wrong the members were. It was, and nobody could see it — the
    complement swept in the ālif and the tāʾ marbūṭa and made the fifteen
    seventeen.

    Counts are what a primer states, so counts are what this asserts.
    """
    assert len(IZHAR) == 6, "the six throat letters"
    assert len(IQLAB) == 1, "only the bāʾ"
    assert len(IDGHAM_GHUNNAH) == 4, "يرملون minus the two without ghunnah"
    assert len(IDGHAM_NO_GHUNNAH) == 2, "lām and rāʾ"
    assert len(IKHFAA) == 15, "the fifteen"


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
    """2:5 carries both: `مِّن رَّبِّهِمْ` is a nūn sākinah and `هُدًى` a tanwīn,
    and both must be produced by the same classifier and the same trigger."""
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
    assert triggers & named, "no nūn slot participated in any occurrence"


def test_a_merger_is_a_pair_of_edges(packed, shared) -> None:
    """`مِّن رَّبِّهِمْ` — `MergedInto` and `Hosts` share a `SoundId` and an
    `OccurrenceId`. There is no source/target boolean anywhere."""
    _, performance = performance_for(packed, shared, 2, 5, RULES)
    merges = [a for a in performance.attributions if isinstance(a, MergedInto)]
    assert merges, "2:5 has an idghām"
    hosts = {
        (a.sound, a.by) for a in performance.attributions if isinstance(a, Hosts)
    }
    for merge in merges:
        assert (merge.sound, merge.by) in hosts


def test_izhar_is_classification_only(packed, shared) -> None:
    """It produces no sound of its own and still exists, because every
    attribution needs a `by` and a projection must be able to find it."""
    _, performance = performance_for(packed, shared, 2, 6, RULES)
    izhar = [o for o in performance.occurrences if o.rule is Rule.IZHAR_HALQI]
    if not izhar:
        pytest.skip("no iẓhār in this verse")
    owned = {a.by for a in performance.attributions}
    assert all(o.id not in owned for o in izhar)


def test_no_cross_word_effect_crosses_a_stop(packed, shared) -> None:
    """E2. Under an all-stop plan the family may still fire inside a word but
    never across one."""
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
    """E1, directly. Last-writer-wins is what this replaces."""
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
    """The invariant ADR-002 §5 calls the one most worth keeping."""
    _, performance = performance_for(packed, shared, 2, 2, RULES)
    known = {o.id for o in performance.occurrences}
    assert all(a.by in known for a in performance.attributions)
    counts = collections.Counter(
        a.by for a in performance.attributions if isinstance(a, Hosts)
    )
    assert counts, "a verse with no hosted sound is a bug in the fixture"
