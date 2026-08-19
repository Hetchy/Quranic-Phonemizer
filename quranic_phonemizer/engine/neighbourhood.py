"""Where a rule may look: the next slot, and what lies between.

Rules query this instead of indexing the Score directly, so a boundary
junction blocks cross-word effects in one place. Built once and reused.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.address import BoundaryPlan, Junction, SlotId
from ..model.canon import Score, Slot


@dataclass(slots=True)
class Neighbourhood:
    score: Score
    boundaries: BoundaryPlan
    _flat: tuple[Slot, ...] = field(default=(), repr=False)
    _word: tuple[int, ...] = field(default=(), repr=False)

    def __post_init__(self) -> None:
        flat: list[Slot] = []
        words: list[int] = []
        for index, word in enumerate(self.score.words):
            for slot in word.slots:
                flat.append(slot)
                words.append(index)
        self._flat = tuple(flat)
        self._word = tuple(words)

    def _position(self, at: SlotId) -> int | None:
        position = at.ordinal
        if position < 0 or position >= len(self._flat) or self._flat[position].id != at:
            return None
        return position

    def slot(self, at: SlotId) -> Slot | None:
        position = self._position(at)
        return self._flat[position] if position is not None else None

    def word_of(self, at: SlotId) -> int | None:
        position = self._position(at)
        return self._word[position] if position is not None else None

    def after(self, at: SlotId) -> Slot | None:
        """The next slot in recitation order, or `None` when a junction blocks
        the view. A rule that cannot see across a stop cannot fire across it."""
        position = self._position(at)
        if position is None or position + 1 >= len(self._flat):
            return None
        following = self._flat[position + 1]
        return None if self._blocked(at, following.id) else following

    def raw_after(self, at: SlotId) -> Slot | None:
        """Return the next slot before special opening and junction blocking."""
        position = self._position(at)
        if position is None or position + 1 >= len(self._flat):
            return None
        return self._flat[position + 1]

    def before(self, at: SlotId) -> Slot | None:
        """The previous slot in recitation order, junctions ignored.

        Deliberately not the mirror of `after`: a stop blocks the view
        forward because recitation ends there, but the slot behind was said.
        """
        position = self._position(at)
        if not position:
            return None
        return self._flat[position - 1]

    def first_of_word(self, at: SlotId) -> bool:
        position = self._position(at)
        if position is None:
            return False
        word = self._word[position]
        return position == 0 or self._word[position - 1] != word

    def last_of_word(self, at: SlotId) -> bool:
        position = self._position(at)
        if position is None:
            return False
        word = self._word[position]
        end = position + 1 == len(self._flat)
        return end or self._word[position + 1] != word

    def crosses_word(self, at: SlotId) -> bool:
        following = self.after(at)
        return following is not None and self.word_of(at) != self.word_of(following.id)

    def _blocked(self, here: SlotId, following: SlotId) -> bool:
        left, right = self.word_of(here), self.word_of(following)
        if left is None or right is None or left == right:
            return False
        if self._spelled_out(left):
            # An opening of named letters ends as it would at a pause, however
            # the reading runs on: `نٓ وَٱلْقَلَمِ` keeps a clear noon and a plain
            # waw, and `طسٓ تِلْكَ` hides nothing. A name is spelled, not read,
            # so it does not run into the word after it. Only forward: a word
            # before an opening still meets it as an ordinary word.
            return True
        if self.score.words[left].sakt_after:
            # A sakt is a silence, so nothing carries across it. It is a Score
            # fact rather than a requested stop, and holds under any plan --
            # a caller that asks to join everything still cannot join `مَنْ ۜ رَاقٍ`.
            return True
        return self.boundaries.junctions[left] in (
            Junction.STOP,
            Junction.SAKT,
            Junction.EDGE,
        )

    def _spelled_out(self, word: int) -> bool:
        """A muqattaat opening: every slot of it is a letter's name."""
        slots = self.score.words[word].slots
        return bool(slots) and all(slot.spelled for slot in slots)
