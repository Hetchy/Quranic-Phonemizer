"""Coalesce scalar positions into ordered half-open [lo, hi) spans."""
from __future__ import annotations

from collections.abc import Iterable


def coalesce(positions: Iterable[int]) -> tuple[tuple[int, int], ...]:
    spans: list[list[int]] = []
    for value in sorted(positions):
        if spans and spans[-1][1] == value:
            spans[-1][1] = value + 1
        else:
            spans.append([value, value + 1])
    return tuple((lo, hi) for lo, hi in spans)


__all__ = ["coalesce"]
