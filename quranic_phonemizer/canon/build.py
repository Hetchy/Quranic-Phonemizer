"""`Reading` to `Score`: the one place a canonical fact is decided.

Shared and script-independent, so equivalent evidence from either script
must resolve to the same Score.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace

from ..model.address import Location, Riwayah, SlotId, VariantSelection, VerseRef
from ..model.canon import (
    ABJAD,
    CanonLetter,
    Nucleus,
    NucleusKind,
    Onset,
    PausalLong,
    Quality,
    Score,
    Short,
    SlotOrigin,
    ScoreWord,
    Silent,
    Slot,
)
from ..model.inscription import Inscription, SlotFact
from ..orthography.adapter import Cluster, Reading
from . import derive
from .derive import Absent, AddsSlot, Attests, Sets, Shows, Target
from .derive import length as _length
from .derive import lexeme, silah, tanween, wasl
from .lexicon import EMPTY as EMPTY_LEXICON
from .lexicon import Lexicon
from .ledger import EMPTY as EMPTY_LEDGER
from .ledger import Ledger, VerseSlot, WordSlot
from .draft import _Draft, set_fact
from .passes import LEXEME_PASSES, LexemePass, apply_ledger, word_of
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
    riwayah: Riwayah = Riwayah.HAFS,
    lexicon: Lexicon = EMPTY_LEXICON,
    ledger: Ledger = EMPTY_LEDGER,
    selection: VariantSelection = VariantSelection(),
    provenance: Provenance | None = None,
    right_context: Reading | None = None,
    passes: tuple[LexemePass, ...] | None = None,
) -> Built:
    """`right_context` is the next verse's reading and is not optional: some
    cross-word tanween sites put the noon on a word in the following verse,
    so verse scope alone is not sufficient."""
    track = provenance if provenance is not None else Provenance()
    scribe = Scribe(reading.verse)
    drafts = _drafts(reading, lexicon, track, right_context, scribe)
    apply_ledger(reading, drafts, ledger, track)
    for lexeme_pass in (passes if passes is not None else LEXEME_PASSES):
        lexeme_pass(reading, drafts, lexicon, scribe, selection)
    score, ordinals = _assemble(reading, drafts, riwayah, selection)
    return Built(score, scribe.finish(reading, drafts, ordinals))


def score_of(reading: Reading, **kwargs) -> Score:
    """The Score alone, for callers that genuinely do not want the edges."""
    return build(reading, **kwargs).score


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
        if letter is None:
            # A bare seat is not a slot, but it may still carry a dagger for
            # the slot before it - Uthmani writes `تَـٰ`, with the alif on the
            # tatweel. Skipping the cluster must not skip its evidence.
            _apply_rows(rows, _Draft(letter=CanonLetter.ALIF), drafts, context,
                        track, scribe, cluster.offset, force=Target.PREVIOUS)
            scribe.decoration(cluster.offset, drafts[-1] if drafts else None)
            track.decorated += 1
            continue

        if index in silenced and cluster.letter is not None:
            # The script wrote a silence sign on this letter - Uthmani's `۟`.
            # A mark that says "this is rasm" outranks any derivation.
            _apply_rows(rows, _Draft(letter=letter), drafts, context, track,
                        scribe, cluster.offset, force=Target.PREVIOUS)
            scribe.decoration(cluster.offset, drafts[-1] if drafts else None)
            track.decorated += 1
            continue

        rasm = _rasm_outcome(context, cluster, rows, track)
        if rasm is not None:
            # A carrier still has a fact to contribute: it lengthens the slot
            # before it. Skipping the cluster must not skip its evidence.
            if isinstance(rasm, Sets):
                set_fact(None, drafts, rasm.fact, rasm.value, Target.PREVIOUS,
                     scribe, cluster.offset)
                track.from_derivation += 1
            else:
                scribe.decoration(cluster.offset, drafts[-1] if drafts else None)
            track.decorated += 1
            continue

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
        if extra is not None:
            drafts.append(extra)
            consumed |= _skip_iwad_carrier(reading, index, bounds)

    _apply_cross_word_noon(reading, drafts, right_context, scribe)
    return drafts


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
            case Attests(family=family):
                scribe.attestation(offset, family, draft)
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
    if cluster.letter not in _length.CARRIERS:
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


def _split_tanween_words(reading: Reading) -> set[int]:
    """Words whose predecessor carries a tanween this script drew here.

    IndoPak splits it across the boundary: the vowel stays on word n, and
    the noon-plus-kasra is drawn as a mark on word n+1.
    """
    out = set()
    for cluster in reading.clusters:
        if cluster.has(tanween.CROSS_WORD_ROLE):
            out.add(cluster.word)
    return out


def _split_tanween_offset(reading: Reading, word: int) -> int:
    """Where the mark that supplies the noon is actually written."""
    for cluster in reading.clusters:
        if cluster.word != word:
            continue
        mark = cluster.mark(tanween.CROSS_WORD_ROLE)
        if mark is not None:
            return mark.offset
    return -1


def _apply_cross_word_noon(reading, drafts, right_context, scribe) -> None:
    """Give word n the noon slot that word n+1 is carrying for it.

    Some cross-word tanween sites span a verse boundary, so this pass needs
    one word of right context.
    """
    marked = _split_tanween_words(reading)
    if right_context is not None and 0 in _split_tanween_words(right_context):
        marked.add(len(reading.words))
    for word_index in sorted(marked):
        donor = word_index - 1
        if donor < 0:
            continue
        span = [d for d in drafts if word_of(reading, d) == donor]
        if not span:
            continue
        last = span[-1]
        if last.letter is CanonLetter.NOON and last.nucleus.kind is NucleusKind.SILENT:
            continue  # already a tanween noon; nothing was split
        quality = getattr(last.nucleus, "quality", Quality.A)
        last.nucleus = Short(quality)
        noon = _Draft(
            letter=CanonLetter.NOON,
            onset=Onset.PLAIN,
            nucleus=Silent(),
            cluster=last.cluster,
            origin=SlotOrigin.NUNATION,
        )
        drafts.insert(drafts.index(last) + 1, noon)
        # The noon is written on the next word, so the grapheme that reaches
        # it is that word's mark, not the donor's.
        offset = _split_tanween_offset(reading, word_index)
        if offset >= 0:
            scribe.evidence(offset, noon, SlotFact.LETTER)
            scribe.evidence(offset, noon, SlotFact.NUCLEUS)


# ------------------------------------------------------------------ finishing
def _assemble(
    reading: Reading, drafts, riwayah, selection,
) -> tuple[Score, dict[int, int]]:
    by_word: dict[int, list[Slot]] = {}
    ordinals: dict[int, int] = {}
    sakt: set[int] = set()
    for ordinal, draft in enumerate(drafts):
        ordinals[id(draft)] = ordinal
        slot = Slot(
            id=SlotId(reading.verse, ordinal),
            letter=draft.letter,
            onset=draft.onset,
            nucleus=draft.nucleus,
            origin=draft.origin,
            annotations=frozenset(draft.annotations),
        )
        word = reading.clusters[draft.cluster].word if draft.cluster >= 0 else 0
        by_word.setdefault(word, []).append(slot)
        if draft.sakt_after:
            sakt.add(word)

    words = tuple(
        ScoreWord(
            location=location,
            slots=tuple(by_word.get(index, ())),
            sakt_after=index in sakt,
        )
        for index, location in enumerate(reading.words)
    )
    return Score(
        riwayah=riwayah,
        words=words,
        selection=selection,
        digest=_digest(words),
    ), ordinals


def _digest(words: tuple[ScoreWord, ...]) -> str:
    text = "|".join(
        f"{slot.letter.value}:{slot.onset.value}:{slot.nucleus.kind.value}:"
        f"{getattr(slot.nucleus, 'quality', '')}"
        for word in words
        for slot in word.slots
    )
    return hashlib.blake2b(text.encode("utf-8"), digest_size=16).hexdigest()


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
