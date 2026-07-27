"""Records `Spelling` edges - grapheme to Score - while the Score is decided.

Recorded here, not reconstructed afterwards, because which slot a mark lands
on is only known at the moment `_set` picks its target.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model.address import GraphemeId, SlotId, VerseRef
from ..model.canon import RuleFamily
from ..model.inscription import (
    Attests,
    Decorates,
    Evidences,
    Inscription,
    SlotFact,
    Spelling,
    Structural,
)


@dataclass(slots=True)
class Scribe:
    """Collects the edges. One per `build` call, discarded after `finish`.

    Drafts are identified by `id()`, valid only while `build`'s own list
    keeps them alive.
    """

    verse: VerseRef
    evidences: list[tuple[int, int, SlotFact]] = field(default_factory=list)
    decorates: list[tuple[int, int]] = field(default_factory=list)
    attests: list[tuple[int, RuleFamily, int]] = field(default_factory=list)

    def evidence(self, offset: int, subject, fact: SlotFact) -> None:
        """`subject` is the draft the fact landed on, which is not always the
        cluster that carried the mark."""
        if offset >= 0 and subject is not None:
            self.evidences.append((offset, id(subject), fact))

    def decoration(self, offset: int, subject) -> None:
        if offset >= 0 and subject is not None:
            self.decorates.append((offset, id(subject)))

    def attestation(self, offset: int, family: RuleFamily, anchor) -> None:
        if offset >= 0 and anchor is not None:
            self.attests.append((offset, family, id(anchor)))

    def finish(self, reading, drafts, ordinals: dict[int, int]) -> Inscription:
        spellings: list[Spelling] = []
        for offset, key, fact in self.evidences:
            slot = _slot(self.verse, ordinals, key)
            if slot is not None:
                spellings.append(Evidences(_grapheme(self.verse, offset), slot, fact))
        for offset, key in self.decorates:
            slot = _slot(self.verse, ordinals, key)
            if slot is not None:
                spellings.append(Decorates(_grapheme(self.verse, offset), slot))
        for offset, family, key in self.attests:
            slot = _slot(self.verse, ordinals, key)
            if slot is not None:
                spellings.append(Attests(_grapheme(self.verse, offset), family, slot))
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
            draft.cluster: ordinals[id(draft)]
            for draft in drafts
            if draft.cluster >= 0 and id(draft) in ordinals
        }
        ordered = sorted(by_cluster)
        for decoration in reading.decorations:
            ordinal = by_cluster.get(decoration.cluster)
            if ordinal is None:
                earlier = [c for c in ordered if c < decoration.cluster]
                if not earlier:
                    continue
                ordinal = by_cluster[earlier[-1]]
            offset = decoration.offset
            if offset < 0:
                continue
            yield Decorates(
                _grapheme(self.verse, offset), SlotId(self.verse, ordinal)
            )


def _slot(verse: VerseRef, ordinals: dict[int, int], key: int) -> SlotId | None:
    ordinal = ordinals.get(key)
    return None if ordinal is None else SlotId(verse, ordinal)


def _grapheme(verse: VerseRef, offset: int) -> GraphemeId:
    return GraphemeId(verse, offset)
