"""A public `ref` to the words it addresses.

`corpus.locations` rejects a ref outside the corpus or of mixed depth; this
adds the one guard that needs the ledger: no clipping a whole word of it.
"""
from __future__ import annotations

from ..canon.ledger import Ledger, WordSlot
from ..corpus import PackedCorpus
from ..model.address import Location


class ClippedLedgerWordError(ValueError):
    """A sub-verse range would drop a word the ledger authors a fact for."""


def resolve_words(
    corpus: PackedCorpus, ledger: Ledger, ref: str
) -> tuple[Location, ...]:
    """The words `ref` addresses, in reading order."""
    locations = corpus.locations(ref)
    _guard_ledger_words(locations, ledger)
    return locations


def _guard_ledger_words(
    locations: tuple[Location, ...], ledger: Ledger
) -> None:
    """A sub-verse range that touches a verse must not drop one of its
    ledger-addressed words: the ledger's fact is authored for that whole
    word, not for whichever part of the verse a range happens to keep."""
    selected = frozenset(locations)
    verses = frozenset(location.verse for location in locations)
    dropped = sorted(
        word
        for word in _word_slot_locations(ledger)
        if word.verse in verses and word not in selected
    )
    if dropped:
        raise ClippedLedgerWordError(
            f"the range excludes {dropped[0]}, which the riwayah's ledger "
            f"addresses as a whole word; request all of {dropped[0].verse} "
            f"or none of it"
        )


def _word_slot_locations(ledger: Ledger) -> frozenset[Location]:
    return frozenset(
        entry.ref.location
        for entry in (*ledger.supplies, *ledger.asserts)
        if isinstance(entry.ref, WordSlot)
    )
