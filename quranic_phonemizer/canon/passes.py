"""Verse-level passes: the Ledger, and a riwayah's word-level lexemes.

Split from `canon/build.py`, which does the per-cluster drafting and had grown
past the size this project holds itself to. The seam is real rather than
arbitrary: everything here runs **after** every cluster has been drafted and
reads a whole word or verse at once, which is exactly what the per-cluster
derivation registry cannot express.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

from ..model.address import VerseRef
from ..model.canon import ABJAD, Onset, PausalLong, Quality
from ..model.inscription import SlotFact
from ..orthography.adapter import Reading
from .derive import Target, lexeme
from .draft import set_fact
from .ledger import Ledger, VerseSlot, WordSlot
from .lexicon import Lexicon


class LedgerAddressError(ValueError):
    """An entry for this verse that does not resolve to a slot."""


def word_of(reading: Reading, draft) -> int:
    """Which word a drafted slot belongs to. Shared with `canon/build.py`,
    which imports this module rather than the other way round."""
    return reading.clusters[draft.cluster].word if draft.cluster >= 0 else -1

#: A pass over the drafted slots of a whole verse, after every per-cluster
#: derivation has run. `(reading, drafts, lexicon) -> None`.
LexemePass: TypeAlias = Callable[[Reading, list, object], None]


def apply_ledger(reading: Reading, drafts, ledger: Ledger, track) -> None:
    """An entry for *this* verse that does not resolve is an error.

    It used to be a bare `continue`, which put the skeleton check -- the thing
    documented as catching ordinal drift -- behind the failure it exists to
    catch. Four of ten shipped entries silently did nothing, and one of them
    named a word whose skeleton would have rejected it outright. A Ledger with
    entries that never fire is worse than no Ledger: it reads as coverage.
    """
    for supply in ledger.supplies:
        if not _addresses(supply.ref, reading.verse):
            continue
        ordinal = _ordinal(reading, drafts, supply.ref)
        if ordinal is None or ordinal >= len(drafts):
            raise LedgerAddressError(
                f"{reading.verse}: ledger entry {supply.ref} does not resolve "
                f"to a slot -- the verse has {len(drafts)} slots. The index is "
                f"zero-based within its word; check the word number too."
            )
        _check_skeleton(reading, drafts, ordinal, supply)
        set_fact(drafts[ordinal], drafts, supply.fact, supply.value, Target.HERE)
        track.from_ledger += 1


def _addresses(ref, verse: VerseRef) -> bool:
    """Is this entry about this verse at all? Separating the two meanings of
    an unresolved address is what lets the second one be loud."""
    if isinstance(ref, VerseSlot):
        return ref.verse == verse
    return isinstance(ref, WordSlot) and ref.location.verse == verse


def _ordinal(reading: Reading, drafts, ref) -> int | None:
    """A verse-scoped ordinal is robust and unreadable, so entries may be
    written word-relative and are resolved here (ADR-001 §5.1)."""
    if isinstance(ref, VerseSlot):
        return ref.ordinal if ref.verse == reading.verse else None
    if not isinstance(ref, WordSlot) or ref.location.verse != reading.verse:
        return None
    word = ref.location.word - 1
    span = [i for i, d in enumerate(drafts) if word_of(reading, d) == word]
    return span[ref.index] if 0 <= ref.index < len(span) else None


def _check_skeleton(reading: Reading, drafts, ordinal: int, supply) -> None:
    """The mandatory `skeleton` is what catches ordinal drift. Without it a
    Ledger entry silently starts describing a different slot."""
    word = word_of(reading, drafts[ordinal])
    actual = "".join(
        ABJAD[d.letter.value] for d in drafts if word_of(reading, d) == word
    )
    if actual != supply.skeleton:
        raise LedgerAddressError(
            f"{reading.verse} slot {ordinal}: ledger entry claims skeleton "
            f"{supply.skeleton!r} but the word is {actual!r}. The ordinal has "
            f"drifted, or the entry names the wrong word."
        )


def _apply_allah_lexeme(reading: Reading, drafts, lexicon=None) -> None:
    """Word by word, not verse by verse.

    The lexeme is a property of one word. Run over the whole verse, a word
    ending in lām or hamza lends its last slot to the next word's opening lām
    and `لَّهُم` acquires the divine name's long ā.
    """
    del lexicon
    for word_index in range(len(reading.words)):
        span = [d for d in drafts if word_of(reading, d) == word_index]
        letters = [d.letter for d in span]
        nuclei = [d.nucleus for d in span]
        for index in lexeme.allah_long_a(letters, nuclei):
            span[index].nucleus = lexeme.relengthened(span[index].nucleus)


def _apply_pausal_lexemes(reading: Reading, drafts, lexicon: Lexicon) -> None:
    """The seven alifs. Uthmani marks them `۠` at 66 sites; IndoPak writes a
    plain final ālif, indistinguishable by any IndoPak grapheme from an
    ordinary length carrier — so the fact is lexical, not orthographic."""
    if not lexicon.pausal_lexemes:
        return
    for word_index in range(len(reading.words)):
        span = [d for d in drafts if word_of(reading, d) == word_index]
        if not span:
            continue
        if lexicon.is_pausal(_vocalised(span)):
            span[-1].nucleus = PausalLong(Quality.A)


def _vocalised(span) -> str:
    """A skeleton that also spells its vowels.

    Plain letters are not enough here: `أَنَا` and `إِنَّا` share the letters
    ء-ن, and only the vowels tell them apart. Still one string, still keyed by
    canonical facts, still readable in the YAML.
    """
    out = []
    for draft in span:
        quality = getattr(draft.nucleus, "quality", None)
        out.append(
            ABJAD[draft.letter.value]
            + ("~" if draft.onset is Onset.GEMINATE else "")
            + (quality.value if quality else "")
        )
    return "".join(out)

#: Hafs' word-level lexeme passes, in order. A parameter rather than three
#: calls inside `build`, because these are the one part of `canon/` that is a
#: riwayah's facts rather than the shared mechanism: the divine name's shape
#: and the seven alifs are Hafs, and a second riwayah replaces the list instead
#: of editing the builder. `_apply_ledger` stays in `build` -- the Ledger is
#: already a parameter, so it is generic.
LEXEME_PASSES: tuple[LexemePass, ...] = (
    _apply_allah_lexeme,
    _apply_pausal_lexemes,
)
