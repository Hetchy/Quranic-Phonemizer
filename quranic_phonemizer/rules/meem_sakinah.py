"""Ghunnah on a doubled noon or meem, and the meem sakinah family."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import MergeInto, Phase, Plan, Realize, Verdict, mint
from ..model.address import BoundaryPlan, Junction, KhilafId, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import Onset, Rule, SlotOrigin
from ..model.performance import Aspect, Consonant, Occurrence
from .lam_shamsiyyah import ArticleShape
from .ownership import is_performed_quiescent
from .khilaf import nasal_place
from .tables import MEEM_OUTCOMES, Followers

NASAL_LETTERS = frozenset({L.NOON, L.MEEM})


@dataclass(frozen=True, slots=True)
class GhunnahMushaddadah:
    """A doubled noon or meem is nasalized wherever it stands. Nothing merges,
    so this is not an idgham."""

    sun: frozenset = frozenset()
    """The letters the article assimilates into. `ٱلْمَغْضُوبِ` has a meem
    behind a silent lam and is not doubled, so the set is asked, not the shape."""

    article: ArticleShape = field(default_factory=ArticleShape)
    """`ٱلنَّاسِ` is doubled by the article, not in the Score, and is a ghunnah
    all the same. `ArticleLam` realizes that one, so this only names it."""

    rule: Rule = Rule.GHUNNAH_MUSHADDADAH
    phase: Phase = Phase.MERGE
    triggers: frozenset = field(default=NASAL_LETTERS)
    emits: frozenset = frozenset({Rule.GHUNNAH_MUSHADDADAH})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot = near.slot(at)
        if slot is None or slot.letter not in NASAL_LETTERS:
            return None
        occurrence = Occurrence(
            mint(Rule.GHUNNAH_MUSHADDADAH, at),
            Rule.GHUNNAH_MUSHADDADAH,
            (at,),
        )
        if slot.onset is not Onset.GEMINATE:
            if not self._doubled_by_the_article(near, at):
                return None
            return Verdict(occurrence, ())
        return Verdict(
            occurrence,
            (
                Realize(
                    at,
                    Aspect.CONSONANT,
                    Consonant(slot.letter, geminate=True, ghunnah=True),
                ),
            ),
        )

    def _doubled_by_the_article(self, near: Neighbourhood, at: SlotId) -> bool:
        """A nasal sun letter the article's lam has assimilated into."""
        slot, before = near.slot(at), near.before(at)
        return (
            slot is not None
            and slot.letter in self.sun
            and before is not None
            and before.nucleus.is_silent
            and self.article(near, before.id)
        )


@dataclass(frozen=True, slots=True)
class MeemSakinah:
    """One classifier for the whole family, because the family has one shape."""

    followers: Followers
    rule: Rule = Rule.IZHAR_SHAFAWI
    phase: Phase = Phase.MERGE
    triggers: frozenset = field(default=frozenset({L.MEEM}))
    emits: frozenset = MEEM_OUTCOMES | {Rule.IZHAR_SHAFAWI}

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        slot = near.slot(at)
        # A repaired meeting leaves this one voweled, and so not a sakin at all.
        if not is_performed_quiescent(slot, plan, at):
            return None
        word = near.word_of(at)
        clear = word is not None and near.last_of_word(at) and (
            boundaries.stopped_on(word)
            or boundaries.after(word) is Junction.SAKT
        )
        following = near.after(at)
        if following is None:
            if clear or (
                slot.origin is SlotOrigin.SPELLED and near.last_of_word(at)
            ):
                # The meem closing a disjoined-letter opening takes its own
                # plain articulation rather than reaching into the next word.
                return _verdict(Rule.IZHAR_SHAFAWI, at, (), ())
            return None

        match self.followers.of(following.letter):
            case Rule.IKHFAA_SHAFAWI:
                # Hidden with ghunnah, not replaced.
                return _ikhfaa_verdict(near, at, following.id)
            case Rule.IDGHAM_SHAFAWI:
                return _verdict(
                    Rule.IDGHAM_SHAFAWI, at, (),
                    (
                        Realize(
                            following.id,
                            Aspect.CONSONANT,
                            Consonant(L.MEEM, geminate=True, ghunnah=True),
                        ),
                        MergeInto(at, Aspect.CONSONANT, following.id, Aspect.CONSONANT),
                    ),
                )
        # Izhar shafawi produces no sound of its own; the occurrence exists so
        # a projection can find it.
        return _verdict(Rule.IZHAR_SHAFAWI, at, (following.id,), ())


def _verdict(rule: Rule, at: SlotId, context: tuple, effects: tuple) -> Verdict:
    """`context` holds a following letter the rule read and left alone; the
    idgham realizes the one it names, so its second unit is an effect."""
    return Verdict(Occurrence(mint(rule, at), rule, (at,), context), effects)


def _ikhfaa_verdict(near: Neighbourhood, at: SlotId, following: SlotId) -> Verdict:
    letter = nasal_place(near.score.selection, KhilafId.IKHFAA_SHAFAWI_NASAL)
    effect = Realize(at, Aspect.CONSONANT, Consonant(letter, ghunnah=True))
    return _verdict(Rule.IKHFAA_SHAFAWI, at, (following,), (effect,))
