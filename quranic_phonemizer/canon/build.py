"""`Reading` to `Score`: the one place a canonical fact is decided.

Shared and script-independent, so equivalent evidence from either script
must resolve to the same Score.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from ..model.address import VariantSelection
from ..model.canon import (
    CARRIERS,
    CanonLetter,
    NucleusKind,
    Onset,
    Quality,
    Short,
    SlotOrigin,
)
from ..model.inscription import Inscription, SlotFact
from ..orthography.adapter import Cluster, Reading
from . import derive
from .derive import Absent, AddsSlot, Attests, Sets, Shows, Target
from .derive import length as _length
from .derive import lexeme, tanween, wasl
from .lexicon import EMPTY as EMPTY_LEXICON
from .lexicon import Lexicon
from .ledger import EMPTY as EMPTY_LEDGER
from .ledger import Ledger
from .assemble import assemble
from .draft import _Draft, set_fact
from .juncture import apply_cross_word_noon
from .passes import LexemePass, apply_ledger
from .scribe import Scribe

#: The two derivations the builder names itself. Both are properties of the
#: canonical layer rather than of any script: the length clause of the
#: unit-hood criterion, and the prosthetic hamza. Everything else is named by
#: an inventory, which is what keeps script knowledge in data.
CARRIER = "carrier"

#: Evidence roles that give a cluster a vowel of its own.
_VOWEL_ROLES = _length.VOWEL_ROLES


class BuildError(ValueError):
    """Names the address and the two disagreeing sources."""


@dataclass(frozen=True, slots=True)
class Built:
    """One verse, one script: the canonical layer and the edges up into it.

    Two objects, not one: an `Inscription` names slots, but a `Score` may
    not name a grapheme, so the reference only runs one way.
    """

    score: Score
    inscription: Inscription


@dataclass(slots=True)
class Provenance:
    """Counts the harness reports besides the residue.

    A residue of zero reached by a rising `Decorates` count is not proof of
    script-independence; it is the same fact discarded twice.
    """

    from_evidence: int = 0
    from_derivation: int = 0
    from_ledger: int = 0
    decorated: int = 0
    attested: int = 0
    derivation_uses: dict[str, int] = field(default_factory=dict)

    def used(self, name: str) -> None:
        self.derivation_uses[name] = self.derivation_uses.get(name, 0) + 1


def build(
    reading: Reading,
    *,
    lexicon: Lexicon = EMPTY_LEXICON,
    ledger: Ledger = EMPTY_LEDGER,
    selection: VariantSelection = VariantSelection(),
    provenance: Provenance | None = None,
    right_context: Reading | None = None,
    passes: tuple[LexemePass, ...],
) -> Built:
    """`right_context` is the next verse's reading and is not optional: a
    cross-word tanween site can put the noon on a word in the next verse.
    `passes` has no default; a defaulted one would not be the riwayah's own."""
    track = provenance if provenance is not None else Provenance()
    scribe = Scribe(reading.verse)
    drafts = _drafts(reading, lexicon, track, right_context, scribe)
    apply_ledger(reading, drafts, ledger, track)
    for lexeme_pass in passes:
        lexeme_pass(reading, drafts, lexicon, scribe, selection)
    score, ordinals = assemble(reading, drafts, selection)
    return Built(score, scribe.finish(reading, drafts, ordinals))


# ------------------------------------------------------------------- drafting
def _drafts(
    reading: Reading,
    lexicon: Lexicon,
    track: Provenance,
    right_context: Reading | None,
    scribe: Scribe,
) -> list[_Draft]:
    by_cluster = _evidence_by_cluster(reading)
    silenced = {d.cluster for d in reading.decorations if d.silences}
    drafts: list[_Draft] = []
    consumed: set[int] = set()

    for index, cluster in enumerate(reading.clusters):
        if index in consumed:
            continue
        bounds = reading.word_bounds(cluster.word)
        context = _context(reading, index, bounds, drafts, lexicon)
        rows = by_cluster.get(index, ())
        letter = _letter_of(rows, cluster)
        if _not_a_slot(letter, index in silenced and cluster.letter is not None,
                       context, cluster, rows, drafts, track, scribe):
            continue
        if _slot_draft(index, cluster, letter, rows, context, drafts, track,
                       scribe):
            consumed |= _skip_iwad_carrier(reading, index, bounds)

    apply_cross_word_noon(reading, drafts, right_context, scribe)
    return drafts



def _not_a_slot(letter, silenced: bool, context, cluster, rows, drafts, track,
                scribe) -> bool:
    """Written, but contributing only to the slot before it.

    A bare seat, a silence sign, or a length carrier. Skipping the cluster
    must not skip its evidence.
    """
    if letter is None or silenced:
        _apply_rows(rows, _Draft(letter=letter or CanonLetter.ALIF), drafts,
                    context, track, scribe, cluster.offset,
                    force=Target.PREVIOUS)
        scribe.decoration(cluster.offset, drafts[-1] if drafts else None)
        track.decorated += 1
        return True
    rasm = _rasm_outcome(context, cluster, rows, track)
    if rasm is None:
        return False
    if isinstance(rasm, Sets):
        set_fact(None, drafts, rasm.fact, rasm.value, Target.PREVIOUS, scribe,
                 cluster.offset)
        track.from_derivation += 1
    else:
        scribe.decoration(cluster.offset, drafts[-1] if drafts else None)
    track.decorated += 1
    return True


def _slot_draft(index: int, cluster, letter, rows, context, drafts, track,
                scribe) -> bool:
    """Append this cluster's slot. True when it also added a second one."""
    draft = _Draft(letter=letter, cluster=index)
    if cluster.onset is not None:
        draft.onset, draft.onset_declared = cluster.onset, True
        track.from_evidence += 1
        scribe.evidence(cluster.offset, draft, SlotFact.ONSET)
    scribe.evidence(cluster.offset, draft, SlotFact.LETTER)
    extra = _apply_rows(rows, draft, drafts, context, track, scribe,
                        cluster.offset)
    _apply_wasl(context, cluster, draft, track)
    _apply_tashil(draft)
    drafts.append(draft)
    if extra is None:
        return False
    drafts.append(extra)
    return True


def _apply_rows(rows, draft, drafts, context, track, scribe, base_offset,
                force=None) -> _Draft | None:
    """`force` redirects every fact to the previous slot. A seat has no slot of
    its own, so what it carries belongs to the one before it - which is how
    Uthmani writes `تَـٰ` and `هِـۧم`."""
    extra: _Draft | None = None
    for row in rows:
        if row.fact is SlotFact.LETTER:
            continue
        offset = row.offset if row.offset >= 0 else base_offset
        if row.value is not None:
            set_fact(draft, drafts, row.fact, row.value, force or Target.HERE,
                 scribe, offset)
            track.from_evidence += 1
            continue
        outcome = derive.resolve(row.derivation, context)
        track.from_derivation += 1
        track.used(row.derivation)
        match outcome:
            case Sets(fact=fact, value=value, target=target):
                set_fact(draft, drafts, fact, value, force or target, scribe, offset)
            case AddsSlot() as adds:
                set_fact(draft, drafts, adds.fact, adds.value, Target.HERE,
                     scribe, offset)
                extra = _Draft(
                    letter=adds.letter,
                    onset=adds.onset,
                    nucleus=adds.nucleus,
                    cluster=draft.cluster,
                    origin=SlotOrigin.NUNATION,
                )
                # The tanween mark writes *both* slots: the host's vowel and
                # the noon. Without this edge the noon would be a slot no
                # grapheme reaches.
                scribe.evidence(offset, extra, SlotFact.LETTER)
                scribe.evidence(offset, extra, SlotFact.NUCLEUS)
            case Attests():
                scribe.attestation(offset, draft)
                track.attested += 1
            case Shows() | Absent():
                scribe.decoration(offset, draft)
                track.decorated += 1
    return extra


#: The two derivations `_apply_wasl` resolves by name rather than calling
#: directly, because "the derivation ran" and "the call happened" are two
#: statements that can drift apart, and a fabricated provenance entry is
#: worse than a missing one.
WASL_ONSET = "hamzat_wasl"
WASL_VOWEL = "wasl_helping_vowel"


def _apply_wasl(context, cluster: Cluster, draft: _Draft, track) -> None:
    def helping_vowel() -> None:
        outcome = derive.resolve(WASL_VOWEL, context)
        draft.nucleus = outcome.value
        track.from_derivation += 1
        track.used(WASL_VOWEL)

    if draft.onset_declared and draft.onset is Onset.WASL:
        draft.letter = CanonLetter.HAMZA
        if not draft.nucleus_declared:
            helping_vowel()
        return
    if cluster.letter is not CanonLetter.ALIF or draft.onset_declared:
        if cluster.letter is CanonLetter.ALIF and not draft.nucleus_declared:
            draft.letter = CanonLetter.HAMZA
        return
    if wasl.is_wasl(context):
        draft.letter = CanonLetter.HAMZA
        draft.onset = derive.resolve(WASL_ONSET, context).value
        track.from_derivation += 1
        track.used(WASL_ONSET)
        if not draft.nucleus_declared:
            helping_vowel()
    else:
        draft.letter = CanonLetter.HAMZA  # a non-carrier ālif is a hamza seat


def _apply_tashil(draft: _Draft) -> None:
    """A facilitated hamza is voweled: the alif the mark is written on stands
    for a hamza with fatha, and the mark says how to say it, not whether."""
    if draft.onset is Onset.TASHIL and not draft.nucleus_declared:
        draft.nucleus = Short(Quality.A)


def _rasm_outcome(context, cluster: Cluster, rows, track):
    """Is this cluster written but not a slot, and if so what fact does it
    still contribute to the previous slot?

    Returns `None` when the cluster is a slot.
    """
    if wasl.is_wasl(context):
        return None   # a prosthetic hamza is a slot, not rasm
    # A dagger's own script decides whether it is this cluster's nucleus or
    # a carried one for the slot before it; only nucleus destination can
    # tell, not the letter itself.
    own, carried = _nucleus_destination(rows, context)
    if own:
        return None
    if carried is not None:
        return carried
    if cluster.has(*_VOWEL_ROLES):
        return None
    if (
        lexeme.hamza_seat(context)
        or lexeme.otiose_waw(context)
        or lexeme.otiose_alif(context)
    ):
        return Absent()
    if cluster.letter not in CARRIERS:
        return None
    outcome = derive.resolve(CARRIER, context)
    track.used(CARRIER)
    if isinstance(outcome, Absent):
        return outcome
    if isinstance(outcome, Sets) and outcome.target is Target.PREVIOUS:
        return outcome
    return None


def _nucleus_destination(rows, context) -> tuple[bool, object | None]:
    """Where do this cluster's nucleus rows land: here, or on the slot before?

    A sukun counts as neither - IndoPak writes one on length carriers like
    `يْ`, and absence of a vowel cannot be what makes a cluster a slot.
    """
    carried = None
    for row in rows:
        if row.fact is not SlotFact.NUCLEUS:
            continue
        if row.value is not None:
            if row.value.kind is not NucleusKind.SILENT:
                return True, None
            continue
        outcome = derive.resolve(row.derivation, context)
        if isinstance(outcome, AddsSlot):
            return True, None
        if isinstance(outcome, Sets):
            if outcome.target is Target.HERE:
                return True, None
            carried = outcome
    return False, carried


def _skip_iwad_carrier(reading: Reading, index: int, bounds) -> set[int]:
    """The alif written after a fathatan is the iwad, not a fourth slot."""
    nxt = index + 1
    if nxt >= bounds[1]:
        return set()
    cluster = reading.clusters[nxt]
    if cluster.letter is CanonLetter.ALIF and not cluster.has(*_VOWEL_ROLES):
        # IndoPak draws its iqlab mark on this alif. An annotation does not
        # turn the iwad carrier into a slot.
        return {nxt}
    return set()


# ------------------------------------------------------------------ finishing
def _evidence_by_cluster(reading: Reading) -> dict[int, tuple]:
    out: dict[int, list] = {}
    for row in reading.evidence:
        out.setdefault(row.cluster, []).append(row)
    return {index: tuple(rows) for index, rows in out.items()}


def _letter_of(rows, cluster: Cluster) -> CanonLetter | None:
    for row in rows:
        if row.fact is SlotFact.LETTER and row.value is not None:
            return row.value
    return cluster.letter


def _context(reading, index, bounds, drafts, lexicon) -> derive.Context:
    previous = drafts[-1] if drafts else None
    return derive.Context(
        clusters=reading.clusters,
        index=index,
        word_bounds=bounds,
        previous_nucleus=previous.nucleus if previous else None,
        previous_letter=previous.letter if previous else None,
        lexicon=lexicon,
    )


__all__ = ["build", "BuildError", "Provenance", "replace"]
