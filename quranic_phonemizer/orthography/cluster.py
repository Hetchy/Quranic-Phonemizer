"""Shared grapheme clustering: scalars in, a `Reading` out.

Both adapters run this same code; only their inventory differs.
"""
from __future__ import annotations

from ..model.address import Location, Script, VerseRef
from ..model.canon import CanonLetter, Onset
from ..model.inscription import Grapheme, GraphemeClass, SlotFact, StopAdvice
from .adapter import Attestation, Cluster, Decoration, Evidence, Reading
from .inventory import Inventory, InventoryError, LetterEntry, MarkEntry


def read_verse(
    inventory: Inventory,
    verse: VerseRef,
    words: tuple[tuple[Location, str], ...],
) -> Reading:
    state = _ReadState(inventory, verse)
    for word_index, (location, text) in enumerate(words):
        state.begin_word(word_index)
        for char in text:
            state.consume(char)
        state.end_word()
    return state.finish(tuple(location for location, _ in words))


class _ReadState:
    """One pass over a verse. Split out so `read_verse` stays a description."""

    def __init__(self, inventory: Inventory, verse: VerseRef) -> None:
        self.inventory = inventory
        self.verse = verse
        self.offset = 0
        self.word_index = 0
        self.letter_index = 0
        self.clusters: list[Cluster] = []
        self.graphemes: list[Grapheme] = []
        self.evidence: list[Evidence] = []
        self.attestations: list[Attestation] = []
        self.decorations: list[Decoration] = []
        self.structural: list[int] = []
        self.advice: list[StopAdvice | None] = []
        self._word_advice: StopAdvice | None = None
        self._word_start = 0

    # -- word framing ------------------------------------------------------
    def begin_word(self, word_index: int) -> None:
        if self.offset:
            self.offset += 1  # the space that separates two words in the verse
        self.word_index = word_index
        self.letter_index = 0
        self._word_advice = None
        self._word_start = len(self.clusters)

    def end_word(self) -> None:
        self.advice.append(self._word_advice)

    # -- scalars -----------------------------------------------------------
    def consume(self, char: str) -> None:
        offset = self.offset
        self.offset += 1
        entry = self.inventory.classify(char)
        if isinstance(entry, LetterEntry):
            self._letter(char, offset, entry)
        else:
            self._mark(char, offset, entry)

    def _letter(self, char: str, offset: int, entry: LetterEntry) -> None:
        self._grapheme(char, offset, GraphemeClass.BASE)
        cluster = Cluster(
            base=char,
            offset=offset,
            word=self.word_index,
            index=self.letter_index,
            letter=entry.letter,
            onset=entry.onset,
            dagger_host=entry.dagger_host,
            bare_rasm=entry.bare_rasm,
        )
        self.letter_index += 1
        self.clusters.append(cluster)
        index = len(self.clusters) - 1
        self.evidence.append(
            Evidence(index, SlotFact.LETTER, value=entry.letter, offset=offset)
        )
        if entry.onset is not None:
            self.evidence.append(
                Evidence(index, SlotFact.ONSET, value=entry.onset, offset=offset)
            )

    def _mark(self, char: str, offset: int, entry: MarkEntry) -> None:
        if entry.structural:
            self._grapheme(char, offset, entry.cls)
            self.structural.append(offset)
            return
        if entry.advice is not None:
            self._grapheme(char, offset, GraphemeClass.ADVICE)
            self.structural.append(offset)
            self._word_advice = entry.advice
            return
        if char in self.inventory.seats:
            self._seat(char, offset)
            return
        if not self.clusters or len(self.clusters) <= self._word_start:
            raise InventoryError(
                f"{self.verse}: U+{ord(char):04X} {char!r} opens a word; a "
                f"mark must be written on a base scalar"
            )
        self._grapheme(char, offset, entry.cls)
        index = len(self.clusters) - 1
        self.clusters[index].marks.append(_mark_of(char, offset, entry))

        if char in self.inventory.combining_hamza:
            self._fold_to_hamza(index, offset)
            return
        if entry.decorates is not None:
            self.decorations.append(
                Decoration(index, offset, entry.decorates, entry.silences)
            )
            return
        if entry.fact is not None:
            self.evidence.append(
                Evidence(
                    index,
                    entry.fact,
                    value=entry.value,
                    derivation=entry.derivation,
                    offset=offset,
                )
            )

    def _seat(self, char: str, offset: int) -> None:
        """A base position with no letter identity: it can host a hamza or a
        lengthening dagger, and shows nothing on its own."""
        self._grapheme(char, offset, GraphemeClass.STRUCTURAL)
        self.clusters.append(
            Cluster(
                base=char,
                offset=offset,
                word=self.word_index,
                index=self.letter_index,
                dagger_host=True,
            )
        )
        index = len(self.clusters) - 1
        self.decorations.append(Decoration(index, offset, "host"))

    def _fold_to_hamza(self, index: int, offset: int) -> None:
        """A seat bearing a combining hamza is a hamza: fold the seat into
        the hamza's letter identity."""
        self.evidence = [
            e
            for e in self.evidence
            if not (e.cluster == index and e.fact is SlotFact.LETTER)
        ]
        self.decorations = [d for d in self.decorations if d.cluster != index]
        self.evidence.append(
            Evidence(index, SlotFact.LETTER, value=CanonLetter.HAMZA, offset=offset)
        )
        self.clusters[index].letter = CanonLetter.HAMZA
        self.clusters[index].dagger_host = False
        self.clusters[index].bare_rasm = False

    def _grapheme(self, char: str, offset: int, cls: GraphemeClass) -> None:
        self.graphemes.append(
            Grapheme(
                id=_grapheme_id(self.verse, offset),
                char=char,
                cls=cls,
                index=self.letter_index,
            )
        )

    def finish(self, locations: tuple[Location, ...]) -> Reading:
        return Reading(
            verse=self.verse,
            script=self.inventory.script,
            words=locations,
            clusters=tuple(self.clusters),
            evidence=tuple(self.evidence),
            attestations=tuple(self.attestations),
            decorations=tuple(self.decorations),
            graphemes=tuple(self.graphemes),
            advice=tuple(self.advice),
            structural=tuple(self.structural),
        )


def _mark_of(char: str, offset: int, entry: MarkEntry):
    from .adapter import Mark

    return Mark(char=char, offset=offset, role=entry.role)


def _grapheme_id(verse: VerseRef, offset: int):
    from ..model.address import GraphemeId

    return GraphemeId(verse, offset)


__all__ = ["read_verse", "Script", "Onset"]
