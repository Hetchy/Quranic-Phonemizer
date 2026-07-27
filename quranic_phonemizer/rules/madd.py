"""Length at the edges: the glide that becomes the vowel before it.

`هُوَ` is R5's case. At a stop the fatha drops and Hafs does not leave a bare
glide — the wāw merges into the damma before it and the word ends long. A final
yāʾ after a kasra does the same.

It is a `MergedInto` rather than a `Relength` plus a `Silence`, because the two
sounds are one: the pair of edges sharing a `SoundId` *is* the merger, and a
projection asking which letters produced the long vowel gets both of them.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..engine.neighbourhood import Neighbourhood
from ..engine.plan import (
    Length,
    MergeInto,
    Plan,
    Realize,
    Relength,
    Verdict,
    mint,
)
from ..model.address import BoundaryPlan, SlotId
from ..model.canon import CanonLetter as L
from ..model.canon import NucleusKind, Onset, Phase, Quality, Rule
from ..model.performance import Aspect, Occurrence, Participants, Vowel

#: Which glide lengthens which vowel.
GLIDE_OF = {Quality.U: L.WAW, Quality.I: L.YA}


@dataclass(frozen=True, slots=True)
class PausalGlide:
    rule: Rule = Rule.MADD_TABII
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None or not boundaries.stopped_on(word):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        if slot.onset is Onset.GEMINATE:
            # A doubled glide is a consonant — `ٱلْعَلِىُّ` ends `-iyy`, not
            # `-ii`. Only a single glide carries the vowel before it.
            return None
        before = _before(near, at)
        if before is None or before.nucleus.kind is not NucleusKind.SHORT:
            return None
        if GLIDE_OF.get(before.nucleus.quality) is not slot.letter:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.MADD_TABII, at),
                Rule.MADD_TABII,
                Participants((before.id, at)),
            ),
            (
                # The rule realizes the merged sound itself. `Relength` would
                # leave the long vowel owned by plain realization, and then
                # the two halves of the merger would not share an occurrence
                # — which is exactly what P4 asserts they must.
                Realize(
                    before.id,
                    Aspect.NUCLEUS,
                    (Vowel(before.nucleus.quality, long=True),),
                ),
                MergeInto(at, Aspect.ONSET, before.id, Aspect.NUCLEUS),
            ),
        )


@dataclass(frozen=True, slots=True)
class IltiqaRepair:
    """Two sākins meet, so the madd letter goes.

    `ٱهْدِنَا ٱلصِّرَٰطَ` is read `ihdina-ṣ-ṣirāṭ`: the ālif of `نَا` is itself
    sākin, the lām of the article behind the elided waṣl hamza is sākin, and
    Arabic does not begin a syllable with two of them. The long vowel shortens.

    This is one rule and it is 2,688 words — `a:`→`a` at 1,413 sites, `i:`→`i`
    at 764, `u:`→`u` at 511 — which was 57% of the whole regression residue and
    read as a long tail of unrelated defects. It needs no corpus: every tajwīd
    primer states it.

    It emits `Relength` rather than realizing the vowel itself. The vowel is
    still plainly realized — nothing merges, nothing is deleted, only its
    length changes — so unlike `PausalGlide` this rule does not own a sound,
    which is why `ILTIQA_REPAIR` is declared classification-only alongside
    `TAFKHEEM` and `TARQEEQ`.
    """

    rule: Rule = Rule.ILTIQA_REPAIR
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({NucleusKind.LONG, NucleusKind.SILAH})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan, boundaries
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if slot.nucleus.kind not in (NucleusKind.LONG, NucleusKind.SILAH):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != at:
            return None
        following = near.after(at)
        if following is None:
            # `after` already refuses to look across a stop, which is the whole
            # boundary condition: at a pause there is no second sākin to meet,
            # and the madd stands. No rule here reads the plan.
            return None
        if following.onset is Onset.WASL:
            # The waṣl hamza and its helping vowel are exactly what a join
            # removes, so the sākin the madd actually meets is the consonant
            # behind it — the lām of `ٱلصِّرَٰطَ`. Read from the Score rather
            # than from the plan: `Onset.WASL` *means* "absent when joined to",
            # so this is the canonical statement of the same fact and does not
            # make a LENGTH rule depend on what BOUNDARY happened to record.
            following = near.after(following.id)
            if following is None:
                return None
        if following.nucleus.kind is not NucleusKind.SILENT:
            return None
        return Verdict(
            Occurrence(
                mint(Rule.ILTIQA_REPAIR, at),
                Rule.ILTIQA_REPAIR,
                Participants((at, following.id)),
            ),
            (Relength(at, Length.SHORT),),
        )


def _before(near: Neighbourhood, at: SlotId):
    flat = near.score.slots()
    for index, slot in enumerate(flat):
        if slot.id == at:
            return flat[index - 1] if index else None
    return None


@dataclass(frozen=True, slots=True)
class MaddClass:
    """Which madd this long vowel is — one classifier, five outcomes.

    The model stores no duration (ADR-006 §5), so every outcome here is
    classification-only and none of them changes a sound. That is exactly why
    they are worth having: the *length* is the one thing a phoneme string
    cannot carry, so a consumer that wants to know whether a madd is two counts
    or six has to read the occurrence. Five members of the vocabulary were
    declared for this and none of them fired.

    `MADD_TABII`, the natural two-count madd, is deliberately not emitted here.
    It is the default that holds wherever none of these five applies, and
    naming it at every long vowel in the Qurʾān would add ~10^5 occurrences per
    traversal to say "nothing special is happening" (ADR-008 open question 7).
    `PausalGlide` emits it where it is a *rule* rather than a default.
    """

    rule: Rule = Rule.MADD_LAZIM
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset(
        {NucleusKind.LONG, NucleusKind.PAUSAL_LONG, NucleusKind.SILAH}
    )

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if slot.nucleus.kind not in self.triggers:
            return None
        slots = near.score.words[word].slots
        final = bool(slots) and slots[-1].id == at

        if final and boundaries.stopped_on(word):
            # Nothing follows inside the word and the boundary ends it, so the
            # madd stands alone. `WaqfEnding` owns what happens to the letter.
            return None

        following = near.after(at)
        if following is None:
            return None

        if following.letter is L.HAMZA:
            # Muttaṣil when the hamza is in the same word, munfaṣil when it
            # opens the next. The distinction is *joined-ness*, which is why
            # this is one rule with two names rather than two rules.
            rule = (
                Rule.MADD_JAIZ_MUNFASIL if final else Rule.MADD_WAJIB_MUTTASIL
            )
            return _classify(rule, at, following.id)

        if following.nucleus.kind is NucleusKind.SILENT:
            # A sākin that is there in the Score is permanent — `ٱلضَّآلِّينَ`,
            # and every muqaṭṭaʿ letter whose name ends in one. Lāzim.
            return _classify(Rule.MADD_LAZIM, at, following.id)

        after = near.after(following.id)
        if after is None and boundaries.stopped_on(near.word_of(following.id)):
            # The following letter is voweled in the Score and loses that vowel
            # only because the reciter stops here. ʿĀriḍ li-s-sukūn: the same
            # shape as lāzim, made temporary by the boundary plan alone.
            return _classify(Rule.MADD_ARID_LIL_SUKUN, at, following.id)
        return None


@dataclass(frozen=True, slots=True)
class MaddLeen:
    """A wāw or yāʾ sākin after a fatha, before a letter made sākin by the stop.

    Not a long vowel — `خَوْف`, `بَيْت` — so it is not in `MaddClass`'s trigger
    set and cannot be a branch of it. The diphthong lengthens at a pause and
    stays short otherwise, which is why the boundary plan is the whole
    condition.
    """

    rule: Rule = Rule.MADD_LEEN
    phase: Phase = Phase.LENGTH
    triggers: frozenset = frozenset({L.WAW, L.YA})

    def look(
        self, near: Neighbourhood, plan: Plan, at: SlotId,
        boundaries: BoundaryPlan,
    ) -> Verdict | None:
        del plan
        slot, word = near.slot(at), near.word_of(at)
        if slot is None or word is None:
            return None
        if slot.nucleus.kind is not NucleusKind.SILENT:
            return None
        if slot.onset is Onset.GEMINATE:
            return None
        before = _before(near, at)
        if before is None or before.nucleus.kind is not NucleusKind.SHORT:
            return None
        if before.nucleus.quality is not Quality.A:
            return None
        following = near.after(at)
        if following is None or not boundaries.stopped_on(word):
            return None
        slots = near.score.words[word].slots
        if not slots or slots[-1].id != following.id:
            # Only the letter the stop actually silences counts.
            return None
        return _classify(Rule.MADD_LEEN, at, following.id)


def _classify(rule: Rule, at: SlotId, other: SlotId) -> Verdict:
    return Verdict(
        Occurrence(mint(rule, at), rule, Participants((at, other))), ()
    )
