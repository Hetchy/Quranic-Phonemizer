"""Shared grapheme clustering: scalars in, a `Reading` out.

Both adapters run this same code; only their inventory differs.
"""
from __future__ import annotations

from ..model.address import Location, VerseRef
from ..model.canon import CanonLetter
from ..model.inscription import Grapheme, GraphemeClass, SlotFact, StopAdvice
from .adapter import Attestation, Cluster, Decoration, Evidence, Reading
from .inventory import Inventory, InventoryError, LetterEntry, MarkEntry

#: The small alif, which is a hamza's rest as readily as a seat is.
DAGGER = "dagger"


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
            # The space between two words, on a par with one inside a word's
            # own text: both are structural glyphs, not silent bookkeeping.
            self._grapheme(" ", self.offset, GraphemeClass.STRUCTURAL)
            self.structural.append(self.offset)
            self.offset += 1
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
            rasm_only=entry.rasm_only,
            seat=entry.seat,
            marked_script=self.inventory.marks_what_it_sounds,
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
        if entry.omitted:
            self._omitted_letter(char, offset, entry)
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
            if self.clusters[index].seat:
                self._fold_to_hamza(index, offset)
            else:
                self.clusters[index].marks.pop()
                self._release_dagger_seat(index)
                # The `_grapheme` above already recorded this offset.
                self._omitted_letter(char, offset, entry, already_written=True)
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

    def _release_dagger_seat(self, index: int) -> None:
        """A hamza drawn on a small alif rather than on a letter: the alif is
        its rest, so it lengthens nothing. 2:72 `فَٱدَّٰرَٰٔتُمْ`."""
        marks = self.clusters[index].marks
        if not marks or marks[-1].role != DAGGER:
            return
        seat = marks.pop()
        self.evidence = [
            e for e in self.evidence
            if not (e.cluster == index and e.offset == seat.offset)
        ]
        # It still shows the slot it rests on, so the reading can say it was
        # written; without this the alif reaches no slot and no rule at all.
        self.decorations.append(Decoration(index, seat.offset))

    def _omitted_letter(
        self, char: str, offset: int, entry: MarkEntry, *,
        already_written: bool = False,
    ) -> None:
        """A letter of the reading the rasm leaves out, written small.

        Takes the position before it if that one has no letter of its own,
        and a position of its own otherwise.
        """
        if not already_written:
            self._grapheme(char, offset, entry.cls)
        held = self.clusters[-1] if self.clusters else None
        if (
            held is None
            or held.letter is not None
            or len(self.clusters) <= self._word_start
        ):
            self.clusters.append(
                Cluster(
                    base=char,
                    offset=offset,
                    word=self.word_index,
                    index=self.letter_index,
                    marked_script=self.inventory.marks_what_it_sounds,
                )
            )
            self.letter_index += 1
        index = len(self.clusters) - 1
        self.clusters[index].letter = entry.value
        self.clusters[index].omitted = True
        self.clusters[index].dagger_host = False
        self.clusters[index].marks.append(_mark_of(char, offset, entry))
        self.decorations = [d for d in self.decorations if d.cluster != index]
        self.evidence.append(
            Evidence(index, SlotFact.LETTER, value=entry.value, offset=offset)
        )

    def _seat(self, char: str, offset: int) -> None:
        """A base position with no letter identity: it can host a hamza or a
        lengthening dagger. `finish` decides whether it ends up structural or
        decorating a slot, once anything written on it is known.
        """
        self._grapheme(char, offset, GraphemeClass.STRUCTURAL)
        self.clusters.append(
            Cluster(
                base=char,
                offset=offset,
                word=self.word_index,
                index=self.letter_index,
                dagger_host=True,
                seat=True,
            )
        )

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
        self.clusters[index].seat = False

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
        bare_seats = [
            cluster.offset for cluster in self.clusters
            if cluster.seat and cluster.letter is None and not cluster.marks
        ]
        return Reading(
            verse=self.verse,
            riwayah=self.inventory.riwayah,
            script=self.inventory.script,
            words=locations,
            clusters=tuple(self.clusters),
            evidence=tuple(self.evidence),
            attestations=tuple(self.attestations),
            decorations=tuple(self.decorations),
            graphemes=tuple(self.graphemes),
            advice=tuple(self.advice),
            structural=tuple(self.structural) + tuple(bare_seats),
        )


def _mark_of(char: str, offset: int, entry: MarkEntry):
    from .adapter import Mark

    return Mark(char=char, offset=offset, role=entry.role)


def _grapheme_id(verse: VerseRef, offset: int):
    from ..model.address import GraphemeId

    return GraphemeId(verse, offset)


__all__ = ["read_verse"]
