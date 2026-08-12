"""A public `ref` to the words it addresses.

`corpus.locations` rejects a ref outside the corpus or of mixed depth; this
adds the one guard that needs the ledger: no clipping a verse it counts into.
"""
from __future__ import annotations

from ..canon.ledger import Ledger, VerseSlot
from ..corpus import PackedCorpus
from ..model.address import Location, VerseRef


class ClippedLedgerVerseError(ValueError):
    """A sub-verse range would break a verse-scoped ledger ordinal."""


def resolve_words(
    corpus: PackedCorpus, ledger: Ledger, ref: str
) -> tuple[Location, ...]:
    """The words `ref` addresses, in reading order."""
    locations = corpus.locations(ref)
    _guard_clipped_verses(corpus, ledger, locations)
    return locations


def _guard_clipped_verses(
    corpus: PackedCorpus, ledger: Ledger, locations: tuple[Location, ...]
) -> None:
    """A verse-scoped ordinal counts slots from the verse's first word, so a
    range keeping only part of that verse resolves it against the wrong slot.
    A word-scoped entry clips freely: a word the range drops is never built.
    """
    addressed = _verse_slot_verses(ledger)
    if not addressed:
        return
    kept: dict[VerseRef, int] = {}
    for location in locations:
        kept[location.verse] = kept.get(location.verse, 0) + 1
    for verse in sorted(addressed & kept.keys()):
        whole = corpus.surah_info[str(verse.surah)][verse.ayah - 1]
        if kept[verse] != whole:
            raise ClippedLedgerVerseError(
                f"the range keeps {kept[verse]} of {verse}'s {whole} words, "
                f"and the riwayah's ledger counts slots from that verse's "
                f"first word; request all of {verse} or none of it"
            )


def _verse_slot_verses(ledger: Ledger) -> frozenset[VerseRef]:
    return frozenset(
        entry.ref.verse
        for entry in (*ledger.supplies, *ledger.asserts)
        if isinstance(entry.ref, VerseSlot)
    )
