"""Score facts that need an occurrence so a projection can find them.

Imāla, tashīl, ishmām, ṣilah and sakt are **canonical facts** — they are
decided by `canon.build` and the Ledger and are already sitting on the Slot
when the engine starts (ADR-004 §3). None of them needs a rule to *happen*.

What they need is an occurrence, because ADR-002 §5 says no sound exists except
as the output of a named one, and because a tajweed projection asked "what is
happening at this letter" must be able to answer "ishmām" as readily as it
answers "ikhfāʾ". Without these, five members of the rule vocabulary were
declared and never produced, and a consumer could see the *sound* change with
no name attached to it.

They emit no effects. The sound is produced by the plain default, coloured by
the canonical fact it already carries, which is why every rule here is declared
classification-only.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import Plan, Verdict, mint
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import NucleusKind, Onset, Phase, Quality, Rule
from ..model.performance import Occurrence, Participants


def _classification(rule: Rule, at: SlotId, *others: SlotId) -> Verdict:
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants((at, *others))), ()
    )


@dataclass(frozen=True, slots=True)
class CanonicalColour:
    """Imāla, tashīl and ishmām — one classifier, because they are one kind of
    fact: a quality or an onset the Score already carries.

    `Quality.IMALA` and `Quality.ISHMAM` are nucleus qualities and
    `Onset.TASHIL` is an onset, so the three are found by looking at the slot
    and nothing else. Three separate classifiers would have three identical
    bodies (ADR-004 §1).
    """

    rule: Rule = Rule.IMALA
    phase: Phase = Phase.COLOUR
    triggers: frozenset = frozenset(
        {Quality.IMALA, Quality.ISHMAM, Onset.TASHIL}
    )

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot = near.slot(at)
        if slot is None:
            return None
        if slot.onset is Onset.TASHIL:
            return _classification(Rule.TASHIL, at)
        quality = getattr(slot.nucleus, "quality", None)
        if quality is Quality.IMALA:
            return _classification(Rule.IMALA, at)
        if quality is Quality.ISHMAM:
            return _classification(Rule.ISHMAM, at)
        return None


@dataclass(frozen=True, slots=True)
class Silah:
    """The pronoun hāʾ's vowel, which is long in waṣl and absent at pause.

    Conditionality is in the type — `Nucleus.Silah` — so nothing here decides
    anything. The occurrence records *that this is the ṣilah* and not an
    ordinary long ī or ū, which is a distinction the phonemes lose and a
    projection needs.
    """

    rule: Rule = Rule.SILAH
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({NucleusKind.SILAH})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if slot.nucleus.kind is not NucleusKind.SILAH:
            return None
        if boundaries.stopped_on(word):
            # At a pause the ṣilah is not there at all, so there is nothing to
            # name. `WaqfEnding` accounts for the slot.
            return None
        return _classification(Rule.SILAH, at)


@dataclass(frozen=True, slots=True)
class Sakt:
    """The brief cut without a breath, at Hafs' four sites.

    `ScoreWord.sakt_after` reached the Score for the first time when
    `SlotFact.SAKT` was wired; before that it was parsed at two entry points
    and dropped at the third, so 18:1 carried no sakt at all.
    """

    rule: Rule = Rule.SAKT
    phase: Phase = Phase.BOUNDARY
    triggers: frozenset = frozenset()

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        word = near.word_of(at)
        if word is None or not near.score.words[word].sakt_after:
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        return _classification(Rule.SAKT, at)


@dataclass(frozen=True, slots=True)
class Tarqeeq:
    """The twin of `TAFKHEEM`, which the vocabulary declared and nothing emitted.

    A rāʾ that is *not* heavy is light, and light is a fact a reciter is taught
    explicitly rather than as an absence — so a projection that can point at
    every tafkhīm and at no tarqīq is telling half the story. It is
    classification-only for the same reason its twin is: the light rāʾ is the
    plain realization, with no `Recolour` to apply.

    Scoped to the rāʾ. The lām's light case is the *absence* of the divine
    name, which is not a tajweed event and would fire on every lām in the
    Qurʾān.
    """

    rule: Rule = Rule.TARQEEQ
    phase: Phase = Phase.COLOUR
    triggers: frozenset = frozenset({L.RA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del boundaries
        from .tafkheem import is_heavy

        slot = near.slot(at)
        if slot is None or slot.letter is not L.RA:
            return None
        if is_heavy(near, slot, plan):
            return None
        return _classification(Rule.TARQEEQ, at)
