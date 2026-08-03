"""A classifier's interface, and the `RuleSet` that dispatches to it.

Every rule shares one signature, so per-letter handling is a matter of
authorship rather than a growing if/elif chain.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeAlias

from ..model.address import BoundaryPlan, SlotId
from ..model.canon import (
    Annotation,
    CanonLetter,
    NucleusKind,
    Onset,
    Rule,
)
from .neighbourhood import Neighbourhood
from .plan import Phase, Plan, Verdict

Trigger: TypeAlias = (
    frozenset[CanonLetter] | frozenset[NucleusKind] | frozenset[Onset]
    | frozenset[Annotation]
)


class Classifier(Protocol):
    """`look` is pure: it reads `Score`, `Plan`, and the traversal, and
    returns a `Verdict` or `None` without mutating any of them."""

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
    """The classifiers bound to each phase for one riwayah.

    A riwayah difference is expressed by swapping a classifier, never by a
    branch inside one.
    """

    phases: dict[Phase, tuple[Classifier, ...]]

    def for_phase(self, phase: Phase) -> tuple[Classifier, ...]:
        return self.phases.get(phase, ())

    def rules(self) -> frozenset[Rule]:
        return frozenset(
            classifier.rule
            for classifiers in self.phases.values()
            for classifier in classifiers
        )
