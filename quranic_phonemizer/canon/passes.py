"""Verse-level passes: the Ledger, the lexemes, and the juncture repairs.

Runs after every cluster is drafted, over a whole word or verse at once -
which the per-cluster derivation registry cannot express.
"""
from __future__ import annotations

from typing import Protocol

from ..model.address import VariantSelection, VerseRef
from ..model.canon import (
    ABJAD,
    Annotation,
    CanonLetter,
    NucleusKind,
    Onset,
    PausalLong,
    Quality,
    Short,
)
from ..model.inscription import SlotFact
from ..orthography.adapter import Reading
from .derive import Target, lexeme
from .draft import _Draft, fact_of, set_fact
from .ledger import Ledger, VerseSlot, WordSlot
from .lexicon import Lexicon
from .scribe import Scribe


class LedgerAddressError(ValueError):
    """An entry for this verse that does not resolve to a slot."""


class LedgerWitnessError(ValueError):
    """A script asserted to write a fact that it does not write."""


def word_of(reading: Reading, draft) -> int:
    """Which word a drafted slot belongs to. Shared with `canon/build.py`,
    which imports this module rather than the other way round."""
    return reading.clusters[draft.cluster].word if draft.cluster >= 0 else -1

# The scribe is in the signature because a pass may *create* slots -- spelling
# `الٓمٓصٓ` turns three into seven -- and every slot must trace to a grapheme.
# The selection is, because a khilaf can put a different vowel in the Score.
# A pass needing neither `del`s them, so what it ignores is visible where it
# is ignored rather than absent from the signature.
class LexemePass(Protocol):
    """A pass over the drafted slots of a whole verse, after every per-cluster
    derivation has run."""

    def __call__(
        self,
        reading: Reading,
        drafts: list[_Draft],
        lexicon: Lexicon,
        scribe: Scribe | None,
        selection: VariantSelection,
    ) -> None: ...


def apply_ledger(reading: Reading, drafts, ledger: Ledger, track) -> None:
    """Applies each Ledger entry for this verse; raises if one fails to resolve.

    An entry that silently matches nothing is worse than no entry: it reads
    as coverage that was never checked.
    """
    _check_witnesses(reading, drafts, ledger)
    for supply in ledger.supplies:
        if not _addresses(supply.ref, reading.verse):
            continue
        ordinal = _resolve(reading, drafts, supply.ref)
        _check_skeleton(reading, drafts, ordinal, supply.skeleton)
        set_fact(drafts[ordinal], drafts, supply.fact, supply.value, Target.HERE)
        track.from_ledger += 1


def _check_witnesses(reading: Reading, drafts, ledger: Ledger) -> None:
    """An assert claims this script writes the fact itself, so it is checked
    before any supply is applied -- otherwise it agrees with the supply."""
    for row in ledger.asserts:
        if row.script is not reading.script:
            continue
        if not _addresses(row.ref, reading.verse):
            continue
        ordinal = _resolve(reading, drafts, row.ref)
        _check_skeleton(reading, drafts, ordinal, row.skeleton)
        written = fact_of(drafts[ordinal], row.fact)
        # A draft holds the set of its annotations, so agreement is membership.
        agrees = (
            row.value in written
            if row.fact is SlotFact.ANNOTATION
            else written == row.value
        )
        if not agrees:
            raise LedgerWitnessError(
                f"{reading.verse} slot {ordinal}: {row.script.value} is said "
                f"to write {row.fact.value} {row.value!r}, and writes "
                f"{written!r}. An assert records what a script already says."
            )


def _resolve(reading: Reading, drafts, ref) -> int:
    """The verse ordinal an entry names. Unresolvable is an error, not a skip."""
    ordinal = _ordinal(reading, drafts, ref)
    if ordinal is None or ordinal >= len(drafts):
        raise LedgerAddressError(
            f"{reading.verse}: ledger entry {ref} does not resolve to a slot "
            f"-- the verse has {len(drafts)} slots. The index is zero-based "
            f"within its word; check the word number too."
        )
    return ordinal


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


def _check_skeleton(reading: Reading, drafts, ordinal: int, claimed: str) -> None:
    """The mandatory `skeleton` is what catches ordinal drift. Without it a
    Ledger entry silently starts describing a different slot."""
    word = word_of(reading, drafts[ordinal])
    actual = "".join(
        ABJAD[d.letter.value] for d in drafts if word_of(reading, d) == word
    )
    if actual != claimed:
        raise LedgerAddressError(
            f"{reading.verse} slot {ordinal}: ledger entry claims skeleton "
            f"{claimed!r} but the word is {actual!r}. The ordinal has "
            f"drifted, or the entry names the wrong word."
        )


def _apply_allah_lexeme(
    reading: Reading, drafts, lexicon, scribe, selection
) -> None:
    """Word by word, not verse by verse: the lexeme is a property of one word.

    Run over the whole verse instead, a word ending in lam or hamza would
    lend its last slot to the next word's opening lam.
    """
    del scribe, selection
    for word_index in range(len(reading.words)):
        span = [d for d in drafts if word_of(reading, d) == word_index]
        letters = [d.letter for d in span]
        nuclei = [d.nucleus for d in span]
        onsets = [d.onset for d in span]
        for index in lexeme.divine_name(letters, nuclei, onsets, lexicon):
            span[index].annotations |= {Annotation.DIVINE_NAME}
        for index in lexeme.allah_long_a(letters, nuclei, onsets, lexicon):
            span[index].nucleus = lexeme.RELENGTHENED_A


#: What the plural meem attaches to. `ـكُمْ` and `ـهُمْ`, in either person.
PLURAL_HOSTS = frozenset({CanonLetter.KAF, CanonLetter.HEH})


def connect_plural_meem(
    reading: Reading, drafts, lexicon, scribe, selection
) -> None:
    """The plural pronoun's meem takes a damma before a prosthetic hamza.

    The hamza drops when the words are joined and bares the quiescent letter
    behind it, so the meem is voweled to keep two of them from meeting.
    """
    del lexicon, scribe, selection
    spans = [
        [d for d in drafts if word_of(reading, d) == word]
        for word in range(len(reading.words))
    ]
    for index, span in enumerate(spans[:-1]):
        following = spans[index + 1]
        if not following or following[0].onset is not Onset.WASL:
            continue
        if _plural_meem(span):
            span[-1].nucleus = Short(Quality.U)


def _plural_meem(span) -> bool:
    """Quiescent, because a script that vowels it has said so already."""
    return (
        len(span) >= 2
        and span[-1].letter is CanonLetter.MEEM
        and span[-1].nucleus.kind is NucleusKind.SILENT
        and span[-2].letter in PLURAL_HOSTS
    )


def _apply_pausal_lexemes(
    reading: Reading, drafts, lexicon: Lexicon, scribe, selection
) -> None:
    """The seven alifs. Uthmani marks them `۠`; IndoPak writes a plain final
    alif, indistinguishable from an ordinary length carrier - so the fact is
    lexical, not orthographic."""
    del scribe, selection
    if not lexicon.pausal_lexemes:
        return
    for word_index in range(len(reading.words)):
        span = [d for d in drafts if word_of(reading, d) == word_index]
        if not span:
            continue
        if lexicon.is_pausal(vocalised(span)):
            span[-1].nucleus = PausalLong(Quality.A)


def vocalised(span) -> str:
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

#: The passes every riwayah runs, in order: two lexemes and one juncture. A
#: list rather than a hardcoded sequence in `build`, so a riwayah that reads
#: a lexeme differently swaps the list instead of editing the builder.
LEXEME_PASSES: tuple[LexemePass, ...] = (
    _apply_allah_lexeme,
    _apply_pausal_lexemes,
    connect_plural_meem,
)
