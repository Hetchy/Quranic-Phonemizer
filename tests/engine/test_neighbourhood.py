"""Where a slot is, asked once.

Three rule modules each carried their own "the slot before this one". These
tests pin the answers the shared one has to keep giving.
"""
from __future__ import annotations

from conftest import score_for

from quranic_phonemizer.engine.boundary_plan import all_join
from quranic_phonemizer.engine.neighbourhood import Neighbourhood
from quranic_phonemizer.model.address import BoundaryPlan, Junction, SlotId


def _near(packed, hafs, surah: int, ayah: int, boundaries=None) -> Neighbourhood:
    score = score_for(packed, hafs, surah, ayah)
    plan = boundaries or all_join(len(score.words))
    return Neighbourhood(score=score, boundaries=plan)


def test_before_walks_the_verse_in_recitation_order(packed, hafs) -> None:
    near = _near(packed, hafs, 1, 2)
    flat = near.score.slots()
    for index, slot in enumerate(flat):
        got = near.before(slot.id)
        want = flat[index - 1] if index else None
        assert got is want, f"at {slot.id} ({index})"


def test_the_first_slot_of_a_verse_has_nothing_before_it(packed, hafs) -> None:
    near = _near(packed, hafs, 1, 2)
    assert near.before(near.score.slots()[0].id) is None


def test_an_unknown_slot_has_no_neighbours(packed, hafs) -> None:
    near = _near(packed, hafs, 1, 2)
    stranger = SlotId(near.score.words[0].location.verse, 9999)
    assert near.before(stranger) is None
    assert near.first_of_word(stranger) is False
    assert near.last_of_word(stranger) is False


def test_a_stop_blocks_the_view_forward_but_not_backward(packed, hafs) -> None:
    """The asymmetry three rule modules relied on and none of them wrote down:
    recitation ends at a stop, but the slot behind it was still said."""
    score = score_for(packed, hafs, 1, 2)
    stops = BoundaryPlan((Junction.STOP,) * (len(score.words) - 1) + (Junction.EDGE,))
    near = Neighbourhood(score=score, boundaries=stops)
    flat = score.slots()
    crossings = [
        (flat[index - 1], slot)
        for index, slot in enumerate(flat)
        if index and near.word_of(slot.id) != near.word_of(flat[index - 1].id)
    ]
    assert crossings, "verse has no word boundary to test"
    for earlier, later in crossings:
        assert near.after(earlier.id) is None
        assert near.before(later.id) is earlier


def test_first_and_last_of_word_agree_with_the_score(packed, hafs) -> None:
    near = _near(packed, hafs, 2, 1)
    for word in near.score.words:
        if not word.slots:
            continue
        for position, slot in enumerate(word.slots):
            assert near.first_of_word(slot.id) is (position == 0)
            assert near.last_of_word(slot.id) is (position == len(word.slots) - 1)


def test_a_one_slot_word_is_both_its_first_and_its_last(packed, hafs) -> None:
    near = _near(packed, hafs, 108, 1)
    singles = [word for word in near.score.words if len(word.slots) == 1]
    for word in singles:
        only = word.slots[0].id
        assert near.first_of_word(only) and near.last_of_word(only)
