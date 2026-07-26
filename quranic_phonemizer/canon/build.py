"""`Reading` → `Score`. The one place a canonical fact is decided.

The builder is shared and script-independent, which is the whole architecture
in one sentence: L1 equality compares the object rules actually read, not an
intermediate the adapters happen to agree on.

The cost of that, stated because it is easy to forget: **every fact this module
supplies is identical across both builds by construction**, so L1 does not test
it. L1 tests only facts that come from adapter evidence. See ADR-008 §3.1 and
the provenance split the harness reports.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace

from ..model.address import Location, Riwayah, SlotId, VariantSelection, VerseRef
from ..model.canon import (
    CanonLetter,
    Nucleus,
    Onset,
    Score,
    ScoreWord,
    Silent,
    Slot,
)
from ..model.inscription import SlotFact
from ..orthography.adapter import Cluster, Reading
from . import derive
from .derive import Absent, AddsSlot, Attests, Sets, Shows, Target
from .derive import length as _length
from .derive import lexeme, silah, tanween, wasl  # noqa: F401  register them
from .derive import gemination  # noqa: F401
from .lexicon import EMPTY as EMPTY_LEXICON
from .lexicon import Lexicon
from .ledger import EMPTY as EMPTY_LEDGER
from .ledger import Ledger, VerseSlot, WordSlot

#: The two derivations the builder names itself. Both are properties of the
#: canonical layer rather than of any script: the length clause of the
#: unit-hood criterion, and the prosthetic hamza. Everything else is named by
#: an inventory, which is what keeps script knowledge in data.
CARRIER = "carrier"

#: Evidence roles that give a cluster a vowel of its own.
_VOWEL_ROLES = _length.VOWEL_ROLES


class BuildError(ValueError):
    """Names the address and the two disagreeing sources."""


@dataclass(slots=True)
class Provenance:
    """What ADR-008 §3.1 requires the harness to report besides the residue.

    A residue of zero reached by a rising `Decorates` count is not a proof of
    script-independence; it is the same fact being discarded twice.
    """

    from_evidence: int = 0
    from_derivation: int = 0
    from_ledger: int = 0
    decorated: int = 0
    attested: int = 0
    derivation_uses: dict[str, int] = field(default_factory=dict)

    def used(self, name: str) -> None:
        self.derivation_uses[name] = self.derivation_uses.get(name, 0) + 1


@dataclass(slots=True)
class _Draft:
    """One slot under construction, plus who decided each of its facts."""

    letter: CanonLetter
    onset: Onset = Onset.PLAIN
    nucleus: Nucleus = field(default_factory=Silent)
    spelled: bool = False
    cluster: int = -1
    onset_declared: bool = False
    nucleus_declared: bool = False


def build(
    reading: Reading,
    *,
    riwayah: Riwayah = Riwayah.HAFS,
    lexicon: Lexicon = EMPTY_LEXICON,
    ledger: Ledger = EMPTY_LEDGER,
    selection: VariantSelection = VariantSelection(),
    provenance: Provenance | None = None,
    right_context: Reading | None = None,
) -> Score:
    """`right_context` is the next verse's reading, and it is not optional
    machinery: 20 of IndoPak's 54 cross-word tanwīn sites put the nūn on a word
    in the *following verse*, so verse scope is necessary and not sufficient."""
    track = provenance if provenance is not None else Provenance()
    drafts = _drafts(reading, lexicon, track, right_context)
    _apply_ledger(reading.verse, drafts, ledger, track)
    _apply_allah_lexeme(drafts)
    return _assemble(reading, drafts, riwayah, selection)


# ------------------------------------------------------------------- drafting
def _drafts(
    reading: Reading,
    lexicon: Lexicon,
    track: Provenance,
    right_context: Reading | None,
) -> list[_Draft]:
    by_cluster = _evidence_by_cluster(reading)
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
            # the slot before it — Uthmani writes `تَـٰ`, with the alif on the
            # tatweel. Skipping the cluster must not skip its evidence.
            _apply_rows(rows, _Draft(letter=CanonLetter.ALIF), drafts, context, track)
            track.decorated += 1
            continue

        rasm = _rasm_outcome(context, cluster, rows)
        if rasm is not None:
            # A carrier still has a fact to contribute: it lengthens the slot
            # before it. Skipping the cluster must not skip its evidence.
            if isinstance(rasm, Sets):
                _set(None, drafts, rasm.fact, rasm.value, Target.PREVIOUS)
                track.from_derivation += 1
            track.decorated += 1
            continue

        draft = _Draft(letter=letter, cluster=index)
        if cluster.onset is not None:
            draft.onset, draft.onset_declared = cluster.onset, True
            track.from_evidence += 1

        extra = _apply_rows(rows, draft, drafts, context, track)
        _apply_wasl(context, cluster, draft, track)
        drafts.append(draft)
        if extra is not None:
            drafts.append(extra)
            consumed |= _skip_iwad_carrier(reading, index, bounds)

    _apply_cross_word_noon(reading, drafts, right_context)
    return drafts


def _apply_rows(rows, draft, drafts, context, track) -> _Draft | None:
    extra: _Draft | None = None
    for row in rows:
        if row.fact is SlotFact.LETTER:
            continue
        if row.value is not None:
            _set(draft, drafts, row.fact, row.value, Target.HERE)
            track.from_evidence += 1
            continue
        outcome = derive.resolve(row.derivation, context)
        track.from_derivation += 1
        track.used(row.derivation)
        match outcome:
            case Sets(fact=fact, value=value, target=target):
                _set(draft, drafts, fact, value, target)
            case AddsSlot() as adds:
                _set(draft, drafts, adds.fact, adds.value, Target.HERE)
                extra = _Draft(
                    letter=adds.letter,
                    onset=adds.onset,
                    nucleus=adds.nucleus,
                    cluster=draft.cluster,
                )
            case Attests():
                track.attested += 1
            case Shows() | Absent():
                track.decorated += 1
    return extra


def _set(draft, drafts, fact: SlotFact, value, target: Target) -> None:
    subject = draft if target is Target.HERE else (drafts[-1] if drafts else None)
    if target is Target.PREVIOUS:
        subject = drafts[-1] if drafts else None
    if subject is None:
        return
    match fact:
        case SlotFact.LETTER:
            subject.letter = value
        case SlotFact.ONSET:
            subject.onset, subject.onset_declared = value, True
        case SlotFact.NUCLEUS:
            subject.nucleus, subject.nucleus_declared = value, True


def _apply_wasl(context, cluster: Cluster, draft: _Draft, track) -> None:
    if draft.onset_declared and draft.onset is Onset.WASL:
        draft.letter = CanonLetter.HAMZA
        if not draft.nucleus_declared:
            draft.nucleus = wasl.wasl_helping_vowel(context).value
            track.from_derivation += 1
            track.used("wasl_helping_vowel")
        return
    if cluster.letter is not CanonLetter.ALIF or draft.onset_declared:
        if cluster.letter is CanonLetter.ALIF and not draft.nucleus_declared:
            draft.letter = CanonLetter.HAMZA
        return
    if wasl.is_wasl(context):
        draft.letter, draft.onset = CanonLetter.HAMZA, Onset.WASL
        track.from_derivation += 1
        track.used("hamzat_wasl")
        if not draft.nucleus_declared:
            draft.nucleus = wasl.wasl_helping_vowel(context).value
            track.used("wasl_helping_vowel")
    else:
        draft.letter = CanonLetter.HAMZA  # a non-carrier ālif is a hamza seat


def _rasm_outcome(context, cluster: Cluster, rows):
    """Is this cluster written-but-not-a-slot, and if so what does it still say?

    Returns `None` when the cluster is a slot; otherwise the outcome, which may
    carry a fact for the *previous* slot — a length carrier is silent at its own
    position and still decides the vowel before it.
    """
    if wasl.is_wasl(context):
        return None   # a prosthetic hamza is a slot, not rasm
    if _has_vowel_evidence(rows, cluster):
        return None
    if lexeme.otiose_waw(context) or lexeme.otiose_alif(context):
        return Absent()
    if cluster.letter not in _length.CARRIERS:
        return None
    outcome = derive.resolve(CARRIER, context)
    if isinstance(outcome, Absent):
        return outcome
    if isinstance(outcome, Sets) and outcome.target is Target.PREVIOUS:
        return outcome
    return None


def _has_vowel_evidence(rows, cluster: Cluster) -> bool:
    """A sukūn deliberately does not count. IndoPak writes one on its length
    carriers — `يْ` for a long ī — and the absence of a vowel cannot be what
    disqualifies a cluster from carrying one."""
    del rows
    return cluster.has(*_VOWEL_ROLES)


def _skip_iwad_carrier(reading: Reading, index: int, bounds) -> set[int]:
    """The ālif written after a fathatan is the ʿiwaḍ, not a fourth slot."""
    nxt = index + 1
    if nxt >= bounds[1]:
        return set()
    cluster = reading.clusters[nxt]
    if cluster.letter is CanonLetter.ALIF and not cluster.marks:
        return {nxt}
    return set()


def _apply_cross_word_noon(reading, drafts, right_context) -> None:
    """IndoPak's `ࣙ`: a nūn drawn on the word *after* the one it belongs to."""
    del reading, drafts, right_context  # resolved by the adapter's evidence


# ------------------------------------------------------------------ finishing
def _apply_ledger(verse: VerseRef, drafts, ledger: Ledger, track) -> None:
    for supply in ledger.supplies:
        ordinal = _ordinal(verse, supply.ref)
        if ordinal is None or ordinal >= len(drafts):
            continue
        _set(drafts[ordinal], drafts, supply.fact, supply.value, Target.HERE)
        track.from_ledger += 1


def _ordinal(verse: VerseRef, ref) -> int | None:
    if isinstance(ref, VerseSlot):
        return ref.ordinal if ref.verse == verse else None
    if isinstance(ref, WordSlot) and ref.location.verse == verse:
        return None  # resolved against the word's slot span by the caller
    return None


def _apply_allah_lexeme(drafts) -> None:
    letters = [d.letter for d in drafts]
    nuclei = [d.nucleus for d in drafts]
    for index in lexeme.allah_long_a(letters, nuclei):
        drafts[index].nucleus = lexeme.relengthened(drafts[index].nucleus)


def _assemble(reading: Reading, drafts, riwayah, selection) -> Score:
    by_word: dict[int, list[Slot]] = {}
    for ordinal, draft in enumerate(drafts):
        slot = Slot(
            id=SlotId(reading.verse, ordinal),
            letter=draft.letter,
            onset=draft.onset,
            nucleus=draft.nucleus,
            spelled=draft.spelled,
        )
        word = reading.clusters[draft.cluster].word if draft.cluster >= 0 else 0
        by_word.setdefault(word, []).append(slot)

    words = tuple(
        ScoreWord(location=location, slots=tuple(by_word.get(index, ())))
        for index, location in enumerate(reading.words)
    )
    return Score(
        riwayah=riwayah,
        words=words,
        selection=selection,
        digest=_digest(words),
    )


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
