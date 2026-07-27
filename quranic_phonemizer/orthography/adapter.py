"""The script boundary: what an adapter may emit, and what it may not decide.

An adapter extracts evidence; `canon.build` authors the Score. A mark either
carries a literal value or names a derivation -- the adapter never computes it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

from ..model.address import Location, Script, VerseRef
from ..model.canon import CanonLetter, Onset, RuleFamily
from ..model.inscription import Grapheme, SlotFact, StopAdvice


@dataclass(frozen=True, slots=True)
class Mark:
    """One non-base scalar, already classified by the inventory."""

    char: str
    offset: int
    role: str
    """The inventory key that classified it. Appears verbatim in diagnostics."""


@dataclass(slots=True)
class Cluster:
    """A base scalar and the marks written on it -- the draft slot sequence.

    Not itself a slot: deciding which clusters become slots is `canon.build`'s
    job, not this module's.
    """

    base: str
    offset: int
    marks: list[Mark] = field(default_factory=list)
    word: int = 0
    index: int = 0
    """Ordinal within its word."""

    letter: CanonLetter | None = None
    """What the inventory says this base scalar is. `None` for a bare seat."""
    onset: Onset | None = None
    """An onset the *glyph* declares, as Uthmani's `ٱ` declares WASL."""
    dagger_host: bool = False
    """Rasm with no letter identity of its own: it may carry a lengthening
    dagger for the previous slot (Uthmani `ى`, `و`)."""
    bare_rasm: bool = False
    """Bare and word-final, the glyph stands for an unwritten alif."""
    marked_script: bool = False
    """This script marks every letter it sounds, so no mark at all is rasm."""
    omitted: bool = False
    """A letter of the reading the rasm leaves out, written small."""
    rasm_only: bool = False
    """The glyph never spells a sound of its own."""

    def mark(self, role: str) -> Mark | None:
        for mark in self.marks:
            if mark.role == role:
                return mark
        return None

    def has(self, *roles: str) -> bool:
        return any(mark.role in roles for mark in self.marks)


@dataclass(frozen=True, slots=True)
class Evidence:
    """A canonical fact a script writes, or a derivation it defers to."""

    cluster: int
    fact: SlotFact
    value: object | None = None
    derivation: str | None = None
    offset: int = -1
    """Source offset of the scalar that carries it; -1 when the base carries it."""

    def __post_init__(self) -> None:
        if (self.value is None) == (self.derivation is None):
            raise ValueError(
                f"evidence for cluster {self.cluster} {self.fact.value} must "
                f"carry exactly one of `value` or `derivation`"
            )


@dataclass(frozen=True, slots=True)
class Attestation:
    """A grapheme witnessing a performance outcome. Names a rule family,
    never a specific rule -- choosing among idgham variants is tajweed
    classification and belongs elsewhere."""

    cluster: int
    family: RuleFamily
    offset: int


@dataclass(frozen=True, slots=True)
class Decoration:
    """Supplies no canonical fact, but names the slot it shows."""

    cluster: int
    offset: int
    target: str = "host"
    """Which slot it decorates, resolved by `canon.build`."""
    silences: bool = False
    """The mark declares its host to be rasm, outranking any derivation --
    a stated fact rather than a hint."""


@dataclass(frozen=True, slots=True)
class Reading:
    """One verse, as one script wrote it, with nothing decided."""

    verse: VerseRef
    script: Script
    words: tuple[Location, ...]
    clusters: tuple[Cluster, ...]
    evidence: tuple[Evidence, ...]
    attestations: tuple[Attestation, ...]
    decorations: tuple[Decoration, ...]
    graphemes: tuple[Grapheme, ...]
    advice: tuple[StopAdvice | None, ...]
    structural: tuple[int, ...]
    """Offsets of scalars that are not part of any word."""

    def word_bounds(self, word_index: int) -> tuple[int, int]:
        lo = hi = -1
        for i, cluster in enumerate(self.clusters):
            if cluster.word != word_index:
                continue
            lo = i if lo < 0 else lo
            hi = i
        return lo, hi + 1
