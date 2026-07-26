"""One rule shape, and the index that dispatches to it.

Every rule has the same signature, because *the switch is the asymmetry*: a
per-letter dispatch decides by authorship which letters deserve a module, and
that is how rāʾ won one while the lām of Allah lost an inline `if`-branch.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter, NucleusKind, Onset, Phase, Rule
from .neighbourhood import Neighbourhood
from .plan import Plan, Verdict

Trigger: TypeAlias = (
    frozenset[CanonLetter] | frozenset[NucleusKind] | frozenset[Onset]
)


class Classifier(Protocol):
    """`look` is pure: a read-only `Score`, a read-only accumulated `Plan`, an
    address, and the traversal. It returns a `Verdict` or `None`. It never
    writes, and it cannot — nothing it is handed is mutable."""

    rule: Rule
    phase: Phase
    triggers: Trigger

    def look(
        self,
        near: Neighbourhood,
        plan: Plan,
        at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None: ...


@dataclass(frozen=True, slots=True)
class RuleSet:
    """What a riwayah binds. Swapping one classifier is how a riwayah delta
    is expressed — no profile subclasses, no `if riwayah == …` inside a rule."""

    phases: dict[Phase, tuple[Classifier, ...]]

    def for_phase(self, phase: Phase) -> tuple[Classifier, ...]:
        return self.phases.get(phase, ())

    def rules(self) -> frozenset[Rule]:
        return frozenset(
            classifier.rule
            for classifiers in self.phases.values()
            for classifier in classifiers
        )
