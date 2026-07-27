"""The muqaṭṭaʿāt: letters that are *named* rather than read.

`الٓمٓ` is not a word — it is three letters said by their names, `ʔalif laam
miim`. ADR-005 §1 calls it the spelled toggle and ADR-001 §3.5b counts it as
the extreme case of one grapheme fanning to many slots: three compact
graphemes become seven.

Two things make it fit the design rather than fight it.

**It is a verse-level pass, not a derivation.** A per-cluster derivation
resolves one cluster to at most one extra slot (`AddsSlot`), and `ص` alone
becomes three. The pass list `canon/passes.py` introduced is exactly the shape
this needs, and this is its second member rather than its excuse.

**The names are slots, and the ordinary rules then apply to them.** Nothing
here knows that 2:1 reads `ʔalif laam-miim` with a ghunnah: the lām's final
mīm and the mīm's first mīm are two ordinary adjacent slots, and the mīm
family assimilates them because that is what it does. 7:1 gets its qalqala on
the ṣād's final dāl the same way. If the spelled letters needed special rules
the model would be wrong; they do not.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..dataio import load_yaml, require_keys
from ..model.canon import ABJAD, CanonLetter, Long, Quality, Short, Silent, SlotOrigin
from ..model.inscription import SlotFact
from ..orthography.adapter import Reading
from .derive.length import VOWEL_ROLES
from .draft import _Draft
from .passes import word_of

SCHEMA_VERSION = 1

#: Letter, then an optional vowel: lowercase short, uppercase long, absent
#: silent. The same notation the pausal lexemes are written in.
_QUALITY = {"a": Quality.A, "u": Quality.U, "i": Quality.I}

_LETTER_OF = {glyph: name for name, glyph in ABJAD.items()}


class SpellingError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Names:
    """Canonical letter → the slots its name is made of."""

    by_letter: dict[CanonLetter, tuple[tuple[CanonLetter, object], ...]]

    def spell(self, letter: CanonLetter):
        return self.by_letter.get(letter)


EMPTY = Names({})


def load_names(path: Path) -> Names:
    data = load_yaml(path)
    require_keys(data, {"schema_version", "names"}, name=str(path))
    if data["schema_version"] != SCHEMA_VERSION:
        raise SpellingError(
            f"{path}: schema_version {data['schema_version']!r}, expected "
            f"{SCHEMA_VERSION}"
        )
    by_letter: dict[CanonLetter, tuple] = {}
    for glyph, spelled in data["names"].items():
        letter = _canon(glyph, path)
        by_letter[letter] = tuple(_parse(spelled, path))
    return Names(by_letter)


def _canon(glyph: str, path: Path) -> CanonLetter:
    name = _LETTER_OF.get(glyph)
    if name is None:
        raise SpellingError(
            f"{path}: {glyph!r} is not a canonical letter. Keys are `ABJAD` "
            f"glyphs, never a script's own scalars."
        )
    return CanonLetter(name)


def _parse(spelled: str, path: Path):
    index = 0
    while index < len(spelled):
        letter = _canon(spelled[index], path)
        index += 1
        if index < len(spelled) and spelled[index] in _QUALITY:
            yield letter, Short(_QUALITY[spelled[index]])
            index += 1
        elif index < len(spelled) and spelled[index].lower() in _QUALITY:
            yield letter, Long(_QUALITY[spelled[index].lower()])
            index += 1
        else:
            yield letter, Silent()


def spell_muqattaat(names: Names):
    """Build the pass. Bound by the riwayah like the other lexeme passes."""

    def apply(reading: Reading, drafts: list, lexicon, scribe=None) -> None:
        del lexicon
        for word in range(len(reading.words)):
            if not _is_muqattaat(reading, word):
                continue
            span = [d for d in drafts if word_of(reading, d) == word]
            if not span:
                continue
            spelled = _spelled(reading, word, names)
            if spelled is None:
                continue
            first = drafts.index(span[0])
            for draft in span:
                drafts.remove(draft)
            drafts[first:first] = spelled
            if scribe is not None:
                # ADR-001 section 3.5b's extreme case, stated as edges: the
                # compact grapheme evidences every slot its name expands to,
                # so `الٓمٓصٓ` gives three graphemes reaching seven slots and
                # I7 holds without a special case for spelled words.
                for draft in spelled:
                    offset = reading.clusters[draft.cluster].offset
                    scribe.evidence(offset, draft, SlotFact.LETTER)
                    scribe.evidence(offset, draft, SlotFact.NUCLEUS)

    return apply


def _is_muqattaat(reading: Reading, word: int) -> bool:
    """A word in which nothing is voweled at all.

    Asked of the *clusters* rather than the drafted slots, because by then the
    waṣl derivation has given `ٱ` a helping vowel and `الٓمٓ` no longer looks
    bare — which is why an all-silent test over slots finds 17 of the 30 sites
    and misses every ālif-initial one.

    Not a location table. Which sūrahs open this way is a fact about the text
    and would need listing; *that a word of bare letters is named rather than
    read* is a rule, and it is the rule that does the work here.
    """
    clusters = [c for c in reading.clusters if c.word == word]
    if not clusters:
        return False
    return not any(cluster.has(*VOWEL_ROLES) for cluster in clusters)


def _spelled(reading: Reading, word: int, names: Names) -> list | None:
    """Spelled from the **clusters**, not from the drafted slots.

    By drafting time a derivation has already reshaped them: 19:1 `كٓهيعٓصٓ`
    loses its yāʾ, which the length rule absorbs into the hāʾ as a long vowel,
    and spelling the drafts gives `kaaf haa ʕayn saad` with the yāʾ's name
    missing. Nothing should be derived from these letters at all -- they are
    named, not read -- so the rasm is the right source and the absorption is
    simply not applicable here.
    """
    out: list[_Draft] = []
    for index, cluster in enumerate(reading.clusters):
        if cluster.word != word or cluster.letter is None:
            continue
        letters = names.spell(cluster.letter)
        if letters is None:
            # A bare word whose letter has no name is not muqaṭṭaʿāt, so the
            # whole word is left alone rather than half-spelled.
            return None
        for letter, nucleus in letters:
            out.append(
                _Draft(
                    letter=letter,
                    nucleus=nucleus,
                    cluster=index,
                    origin=SlotOrigin.SPELLED,
                )
            )
    return out or None
