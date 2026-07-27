"""Verse-level passes: the Ledger, and a riwayah's word-level lexemes.

Runs after every cluster is drafted, over a whole word or verse at once -
which the per-cluster derivation registry cannot express.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

from ..model.address import VerseRef
from ..model.canon import Annotation, ABJAD, Onset, PausalLong, Quality
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
#: derivation has run. `(reading, drafts, lexicon, scribe) -> None`.
#:
#: The scribe is in the signature because a pass may *create* slots -- spelling
#: `الٓمٓصٓ` turns three into seven -- and every slot must trace to a grapheme.
#: A pass that only mutates existing slots can ignore it.
LexemePass: TypeAlias = Callable[[Reading, list, object, object], None]


def apply_ledger(reading: Reading, drafts, ledger: Ledger, track) -> None:
    """Applies each Ledger entry for this verse; raises if one fails to resolve.

    An entry that silently matches nothing is worse than no entry: it reads
    as coverage that was never checked.
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
    """A verse-scoped ordinal is robust but unreadable, so entries may also
    be written word-relative and are resolved to a verse ordinal here."""
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


def _apply_allah_lexeme(reading: Reading, drafts, lexicon=None, scribe=None) -> None:
    """Word by word, not verse by verse: the lexeme is a property of one word.

    Run over the whole verse instead, a word ending in lam or hamza would
    lend its last slot to the next word's opening lam.
    """
    del lexicon, scribe
    for word_index in range(len(reading.words)):
        span = [d for d in drafts if word_of(reading, d) == word_index]
        letters = [d.letter for d in span]
        nuclei = [d.nucleus for d in span]
        onsets = [d.onset for d in span]
        for index in lexeme.divine_name(letters, nuclei, onsets):
            span[index].annotations |= {Annotation.DIVINE_NAME}
        for index in lexeme.allah_long_a(letters, nuclei, onsets):
            span[index].nucleus = lexeme.relengthened(span[index].nucleus)


def _apply_pausal_lexemes(
    reading: Reading, drafts, lexicon: Lexicon, scribe=None
) -> None:
    """The seven alifs. Uthmani marks them `۠`; IndoPak writes a plain final
    alif, indistinguishable from an ordinary length carrier - so the fact is
    lexical, not orthographic."""
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

    Plain letters are not enough: `أَنَا` and `إِنَّا` share the letters ء-ن,
    and only the vowels tell them apart.
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

#: Hafs' word-level lexeme passes, in order. A list rather than a hardcoded
#: sequence in `build`, because this is riwayah-specific: a second riwayah
#: swaps the list instead of editing the builder.
LEXEME_PASSES: tuple[LexemePass, ...] = (
    _apply_allah_lexeme,
    _apply_pausal_lexemes,
)
