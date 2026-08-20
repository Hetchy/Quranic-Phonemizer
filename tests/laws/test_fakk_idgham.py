"""fakk_idgham: said when a reading starts where a cross-word merger would
have fired instead of joining into it.
"""
from __future__ import annotations

from conftest import score_for
from quranic_phonemizer.engine.run import perform
from quranic_phonemizer.model.address import BoundaryPlan, Junction
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.model.performance import (
    Classifies,
    Consonant,
    effect_targets,
)
from quranic_phonemizer.riwayat.hafs import HAFS


def _started_at(score, word_number: int) -> BoundaryPlan:
    """A stop right before `word_number`; every other junction joins."""
    total = len(score.words)
    return BoundaryPlan(
        tuple(
            Junction.STOP if index == word_number - 2 else Junction.JOIN
            for index in range(total - 1)
        )
        + (Junction.EDGE,)
    )


def test_fakk_idgham_fires_where_the_merger_would_have(packed, hafs) -> None:
    # 2:56:2-3, بَعَثْنَٰكُم مِّن: the meem of مِّن carries the rasm's shadda.
    score = score_for(packed, hafs, 2, 56)
    meem = score.words[2].slots[0]
    performance = perform(score, HAFS, _started_at(score, 3))

    fired = [o for o in performance.occurrences if meem.id in o.subjects]
    assert [o.rule for o in fired] == [Rule.FAKK_IDGHAM]
    assert fired[0].context == (score.words[1].slots[-1].id,)


def test_the_joined_reading_takes_the_merger_instead(packed, hafs) -> None:
    from quranic_phonemizer.engine.boundary_plan import all_join

    score = score_for(packed, hafs, 2, 56)
    meem = score.words[2].slots[0]
    performance = perform(score, HAFS, all_join(len(score.words)))

    targets = effect_targets(performance)
    fired = {
        o.rule for o in performance.occurrences
        if meem.id in o.subjects + o.context + targets.get(o.id, ())
    }
    assert Rule.FAKK_IDGHAM not in fired
    assert Rule.IDGHAM_SHAFAWI in fired


def test_fakk_idgham_changes_no_sound(packed, hafs) -> None:
    """Classification only: the meem is plain either way, so removing the
    rule would lose the attribution and not a single token."""
    score = score_for(packed, hafs, 2, 56)
    meem = score.words[2].slots[0]
    performance = perform(score, HAFS, _started_at(score, 3))

    sound = dict(performance.sounds)
    hosted = next(
        s for s in performance.attributions
        if meem.id in getattr(s, "slots", ())
    )
    consonant = sound[hosted.sound]
    assert isinstance(consonant, Consonant) and not consonant.geminate

    classified = {m.sound for m in performance.modifiers
                  if isinstance(m, Classifies)}
    assert hosted.sound in classified
