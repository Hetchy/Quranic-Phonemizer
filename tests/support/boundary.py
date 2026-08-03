"""Boundary plans by intent rather than by junction arithmetic.

A plan holds the junction after each word, so starting on a word is a stop
recorded on the word before it.
"""
from __future__ import annotations

from quranic_phonemizer.model.address import BoundaryPlan, Junction


class UnreachableWasl(ValueError):
    """Asking for a joined reading of a word with nothing after it."""


def _requested(value) -> tuple[int, ...]:
    if value is None:
        return ()
    return (value,) if isinstance(value, int) else tuple(value)


def plan_for(
    words: int,
    *,
    wasl=None,
    waqf=None,
    ibtidaa=None,
    isolated=None,
) -> BoundaryPlan:
    """Every word joined, then a stop wherever an argument asks for one."""
    junctions = [Junction.JOIN] * words
    junctions[-1] = Junction.EDGE

    def stop_after(word: int) -> None:
        if word < words:
            junctions[word - 1] = Junction.STOP

    for word in _requested(waqf) + _requested(isolated):
        stop_after(word)
    for word in _requested(ibtidaa) + _requested(isolated):
        stop_after(word - 1)

    for word in _requested(wasl):
        if word == words:
            raise UnreachableWasl(
                f"word {word} has nothing after it to join into"
            )
        if junctions[word - 1] is not Junction.JOIN:
            raise UnreachableWasl(
                f"word {word} is asked to join forward and to stop"
            )
    return BoundaryPlan(tuple(junctions))


def reaches_past(words: int, *, wasl=None, **_) -> bool:
    """Whether the plan asks the last word of the verse to join forward."""
    return words in _requested(wasl)
