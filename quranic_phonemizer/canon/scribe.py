"""Records `Spelling` edges - grapheme to Score - while the Score is decided.

Recorded here, not reconstructed afterwards, because which slot a mark lands
on is only known at the moment `_set` picks its target.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass, field

from ..model.address import GraphemeId, SlotId, VerseRef
from ..model.inscription import (
    Attests,
    Decorates,
    Evidences,
    Inscription,
    SlotFact,
    Spelling,
    Structural,
)


class OrphanedEdgeError(ValueError):
    """A recorded edge points at a draft no slot came from."""


@dataclass(slots=True)
class Scribe:
    """Collects the edges. One per `build` call, discarded after `finish`.

    Drafts are identified by `_Draft.uid`, so a pass that drops one has to
    say what becomes of its edges rather than leaving them to fall out.
    """

    verse: VerseRef
    evidences: list[tuple[int, int, SlotFact]] = field(default_factory=list)
    decorates: list[tuple[int, int]] = field(default_factory=list)
    attests: list[tuple[int, int]] = field(default_factory=list)

    def evidence(self, offset: int, subject, fact: SlotFact) -> None:
        """`subject` is the draft the fact landed on, which is not always the
        cluster that carried the mark."""
        if offset >= 0 and subject is not None:
            self.evidences.append((offset, subject.uid, fact))

    def withdraw_evidence(self, offset: int, subject, fact: SlotFact) -> None:
        """Remove one interpretation of a glyph before replacing it."""
        self.evidences = [
            row for row in self.evidences
            if row != (offset, subject.uid, fact)
        ]

    def evidence_offsets(self, subject, fact: SlotFact) -> tuple[int, ...]:
        """The source offsets currently spelling one draft fact."""
        return tuple(
            offset for offset, uid, existing in self.evidences
            if uid == subject.uid and existing is fact
        )

    def decoration(self, offset: int, subject) -> None:
        if offset >= 0 and subject is not None:
            self.decorates.append((offset, subject.uid))

    def attestation(self, offset: int, anchor) -> None:
        if offset >= 0 and anchor is not None:
            self.attests.append((offset, anchor.uid))

    def withdraw(self, drafts) -> None:
        """Every edge into these drafts, dropped. For a pass that replaces a
        span wholesale: the graphemes are re-evidenced onto what replaces it."""
        gone = {draft.uid for draft in drafts}
        self.evidences = [row for row in self.evidences if row[1] not in gone]
        self.decorates = [row for row in self.decorates if row[1] not in gone]
        self.attests = [row for row in self.attests if row[1] not in gone]

    def retarget(self, offsets, subjects, target) -> None:
        """Move selected source edges from replaced drafts onto their survivor."""
        wanted = set(offsets)
        old = {subject.uid for subject in subjects}
        self.evidences = [
            (offset, target.uid, fact) if offset in wanted and uid in old
            else (offset, uid, fact)
            for offset, uid, fact in self.evidences
        ]
        self.decorates = [
            (offset, target.uid) if offset in wanted and uid in old else (offset, uid)
            for offset, uid in self.decorates
        ]
        self.attests = [
            (offset, target.uid) if offset in wanted and uid in old else (offset, uid)
            for offset, uid in self.attests
        ]

    def finish(self, reading, drafts, ordinals: dict[int, int]) -> Inscription:
        spellings: list[Spelling] = []
        for offset, key, fact in self.evidences:
            slot = _slot(self.verse, ordinals, key, offset)
            spellings.append(Evidences(_grapheme(self.verse, offset), slot, fact))
        for offset, key in self.decorates:
            slot = _slot(self.verse, ordinals, key, offset)
            spellings.append(Decorates(_grapheme(self.verse, offset), slot))
        for offset, key in self.attests:
            slot = _slot(self.verse, ordinals, key, offset)
            spellings.append(Attests(_grapheme(self.verse, offset), slot))
        for offset in reading.structural:
            spellings.append(Structural(_grapheme(self.verse, offset)))
        spellings.extend(self._decorations(reading, drafts, ordinals))
        return Inscription(
            verse=self.verse,
            script=reading.script,
            words=reading.words,
            graphemes=reading.graphemes,
            spellings=tuple(spellings),
            advice=reading.advice,
        )


    def _decorations(self, reading, drafts, ordinals):
        """`Decoration` carries a cluster, not a slot, because the adapter does
        not know which clusters become slots. A mark on rasm has no cluster
        of its own, so it falls back to the last slot before it."""
        by_cluster = {
            draft.cluster: ordinals[draft.uid]
            for draft in drafts
            if draft.cluster >= 0
        }
        ordered = sorted(by_cluster)
        for decoration in reading.decorations:
            ordinal = by_cluster.get(decoration.cluster)
            if ordinal is None:
                preceding = bisect_left(ordered, decoration.cluster) - 1
                if preceding < 0:
                    continue
                ordinal = by_cluster[ordered[preceding]]
            offset = decoration.offset
            if offset < 0:
                continue
            yield Decorates(
                _grapheme(self.verse, offset), SlotId(self.verse, ordinal)
            )


def _slot(verse: VerseRef, ordinals: dict[int, int], key: int, offset: int) -> SlotId:
    """A miss is a written character anchored to no sound, which is invisible
    in output and in every gate. It raises instead."""
    ordinal = ordinals.get(key)
    if ordinal is None:
        raise OrphanedEdgeError(
            f"{verse.surah}:{verse.ayah} offset {offset}: edge into draft "
            f"{key}, which no slot came from. A pass that drops a draft must "
            f"withdraw its edges."
        )
    return SlotId(verse, ordinal)


def _grapheme(verse: VerseRef, offset: int) -> GraphemeId:
    return GraphemeId(verse, offset)


def record_attestations(scribe: Scribe, reading, drafts) -> int:
    """Carry adapter witnesses onto the surviving canonical slot drafts."""
    by_cluster = {draft.cluster: draft for draft in drafts if draft.cluster >= 0}
    existing = set(scribe.attests)
    added = 0
    for attestation in reading.attestations:
        anchor = by_cluster.get(attestation.cluster)
        row = None if anchor is None else (attestation.offset, anchor.uid)
        if row is not None and row not in existing:
            scribe.attestation(attestation.offset, anchor)
            existing.add(row)
            added += 1
    return added
