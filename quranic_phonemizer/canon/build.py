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
    Nucleus,
    Onset,
    Quality,
    SlotOrigin,
)
from ..model.inscription import VOWEL_FACTS, Inscription, SlotFact
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
from .draft import (
    _Draft, decorated_offsets, letter_of, letter_offsets_of, nucleus_fact,
    set_fact,
)
from .juncture import apply_cross_word_noon
from .passes import LexemePass, apply_ledger, word_bounds
from .scribe import Scribe, record_attestations

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
    track.attested += record_attestations(scribe, reading, drafts)
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
    #: A seat nothing was ever written on is a Structural edge, not a slot --
    #: `orthography.cluster` already routed its offset there.
    bare_seats = frozenset(reading.structural)
    drafts: list[_Draft] = []
    consumed: set[int] = set()
    pending: list[int] = []
    bounds_by_word = word_bounds(reading)

    for index, cluster in enumerate(reading.clusters):
        if index in consumed or cluster.offset in bare_seats:
            continue
        bounds = bounds_by_word[cluster.word]
        context = _context(reading, index, bounds, drafts, lexicon)
        rows = by_cluster.get(index, ())
        letter = letter_of(rows, cluster)
        if _not_a_slot(letter, index in silenced and cluster.letter is not None,
                       context, cluster, rows, drafts, track, scribe, pending):
            continue
        before = len(drafts)
        if _slot_draft(index, cluster, letter, rows, context, drafts, track,
                       scribe):
            consumed |= _skip_iwad_carrier(reading, index, bounds, drafts,
                                           track, scribe)
        _flush_pending(pending, drafts, before, scribe, track)

    apply_cross_word_noon(reading, drafts, right_context, scribe)
    return drafts


def _decorate(scribe, offset: int, subject, track) -> None:
    scribe.decoration(offset, subject)
    track.decorated += 1


def _flush_pending(pending: list[int], drafts, before: int, scribe,
                   track) -> None:
    """A hamza seat's grapheme decorates the hamza it seats, which has no
    draft yet when the seat is visited, so its edge waits for one."""
    if not pending or len(drafts) <= before:
        return
    subject = drafts[before]
    for offset in pending:
        _decorate(scribe, offset, subject, track)
    pending.clear()


def _not_a_slot(letter, silenced: bool, context, cluster, rows, drafts, track,
                scribe, pending: list[int]) -> bool:
    """Written, but contributing only to another slot -- the one before it,
    or, for a hamza seat, the one after -- and still decorated."""
    if letter is None or silenced:
        _apply_rows(rows, _Draft(letter=letter or CanonLetter.ALIF), drafts,
                    context, track, scribe, cluster.offset,
                    force=Target.PREVIOUS)
        _decorate(scribe, cluster.offset, drafts[-1] if drafts else None, track)
        return True
    rasm = _rasm_outcome(context, cluster, rows, track)
    if rasm is None:
        return False
    outcome, offset = rasm
    if isinstance(outcome, Sets):
        # `offset` is the mark that carries the fact (a dagger, a pausal
        # sign), not the carrier's own base offset, so the two glyphs stay
        # distinguishable in the Inscription.
        set_fact(None, drafts, outcome.fact, outcome.value, Target.PREVIOUS,
                 scribe, offset)
        track.from_derivation += 1
    if isinstance(outcome, Absent) and outcome.shows is Target.HERE:
        pending.append(cluster.offset)
    else:
        subject = drafts[-1] if drafts else None
        evidenced = {offset} if isinstance(outcome, Sets) else ()
        for shown in decorated_offsets(rows, context, cluster.offset, evidenced):
            _decorate(scribe, shown, subject, track)
    return True


def _slot_draft(index: int, cluster, letter, rows, context, drafts, track,
                scribe) -> bool:
    """Append this cluster's slot. True when it also added a second one."""
    draft = _Draft(letter=letter, cluster=index)
    letter_offset, extra_offsets = letter_offsets_of(rows, cluster)
    scribe.evidence(letter_offset, draft, SlotFact.LETTER)
    for offset in extra_offsets:
        _decorate(scribe, offset, draft, track)
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
                scribe.evidence(offset, extra, nucleus_fact(extra.nucleus))
            case Attests():
                scribe.attestation(offset, draft)
                track.attested += 1
            case Shows() | Absent():
                _decorate(scribe, offset, draft, track)
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
        draft.nucleus = Nucleus.short(Quality.A)


def _rasm_outcome(context, cluster: Cluster, rows, track):
    """Is this cluster written but not a slot, and if so what fact does it
    still contribute to the previous slot, and from which offset?

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
    if cluster.has(*_VOWEL_ROLES, "consonantal_sukun"):
        return None
    if lexeme.hamza_seat(context):
        # The seat spells no sound of its own; what it spells is the hamza
        # after it, which has no draft yet at this point in the pass.
        return Absent(shows=Target.HERE), cluster.offset
    if lexeme.otiose_waw(context) or lexeme.otiose_alif(context):
        return Absent(), cluster.offset
    if cluster.letter not in CARRIERS:
        return None
    outcome = derive.resolve(CARRIER, context)
    track.used(CARRIER)
    if isinstance(outcome, Absent):
        return outcome, cluster.offset
    if isinstance(outcome, Sets) and outcome.target is Target.PREVIOUS:
        return outcome, cluster.offset
    return None


def _nucleus_destination(rows, context) -> tuple[bool, tuple | None]:
    """Where do this cluster's nucleus rows land: here, or on the slot before?

    A carried outcome pairs with the mark's own offset, not the carrier's,
    so a dagger's glyph is what the fact is spelled from.
    """
    carried = None
    for row in rows:
        if row.fact not in VOWEL_FACTS:
            continue
        if row.value is not None:
            if not row.value.is_silent:
                return True, None
            continue
        outcome = derive.resolve(row.derivation, context)
        if isinstance(outcome, AddsSlot):
            return True, None
        if isinstance(outcome, Sets):
            if outcome.target is Target.HERE:
                return True, None
            offset = row.offset if row.offset >= 0 else context.cluster.offset
            carried = (outcome, offset)
    return False, carried


def _skip_iwad_carrier(reading: Reading, index: int, bounds, drafts, track,
                       scribe) -> set[int]:
    """The alif written after a fathatan is the iwad, not a fourth slot.

    At a stop it lengthens the base vowel, not the noon it silences, so its
    glyph decorates the base slot `_slot_draft` appended, before the noon.
    """
    nxt = index + 1
    if nxt >= bounds[1]:
        return set()
    cluster = reading.clusters[nxt]
    if cluster.letter is CanonLetter.ALIF and not cluster.has(*_VOWEL_ROLES):
        # IndoPak draws its iqlab mark on this alif. An annotation does not
        # turn the iwad carrier into a slot.
        base = drafts[-2] if len(drafts) >= 2 else None
        _decorate(scribe, cluster.offset, base, track)
        return {nxt}
    return set()


# ------------------------------------------------------------------ finishing
def _evidence_by_cluster(reading: Reading) -> dict[int, tuple]:
    out: dict[int, list] = {}
    for row in reading.evidence:
        out.setdefault(row.cluster, []).append(row)
    return {index: tuple(rows) for index, rows in out.items()}


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
