"""Readable boundary intents used by semantic case tables."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReadSpec:
    kind: str
    boundary: tuple[tuple[str, int | tuple[int, ...]], ...] = ()

    def kwargs(self, words: tuple[int, ...]) -> dict:
        if not words:
            raise ValueError("a semantic case needs focused words")
        first, last = words[0], words[-1]
        if self.kind == "isolated":
            if len(words) != 1:
                raise ValueError("isolated() requires one focused word")
            return {"isolated": first}
        if self.kind == "joining":
            return {"ibtidaa": first, "wasl": last}
        if self.kind == "through":
            return {"ibtidaa": first, "waqf": last}
        if self.kind == "explicit":
            return dict(self.boundary)
        raise ValueError(f"unknown read intent {self.kind!r}")


def isolated() -> ReadSpec:
    return ReadSpec("isolated")


def joining() -> ReadSpec:
    return ReadSpec("joining")


def through() -> ReadSpec:
    return ReadSpec("through")


def explicit(**boundary) -> ReadSpec:
    return ReadSpec("explicit", tuple(boundary.items()))
