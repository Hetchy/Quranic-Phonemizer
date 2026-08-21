"""Build the source cell columns of a request from its source view.

Role and tier come from the unit kind and the reading; a riding mark attaches to
the main column its written_on names, or of the carrier or seat it qualifies.
"""
from __future__ import annotations

from dataclasses import dataclass

from ...model.address import KhilafId, Location, Option, SlotId, VariantSelection
from ...model.performance import Consonant, Quality, Vowel
from ...render.alphabet import packaged_alphabet
from ...session import Session
from ..facts import AnalysisFacts, analyse
from ..ids import CellColumnId
from ..inscription import InscriptionFacts, inscribe
from ..source import build_source_view
from ..source_dtos import LetterUnit, LetterUnitKind, SourceView
from .dtos import CellColumn, CellRole, CellStatus, CellTier, CellWord
from .laws import validate_cell_columns


@dataclass(frozen=True, slots=True)
class _Reading:
    """What the reading says about the units, keyed for column decisions."""

    long_vowel_orders: frozenset[int]
    consonant_orders: frozenset[int]
    canonical_quality: dict[int, Quality | None]
    slot_of_unit: dict[int, SlotId]
    owner_of_sound: dict[int, int]
    main_units: tuple[int, ...]
    variant_of_unit: dict[int, Option]
    below_units: frozenset[int]
    written_on: dict[int, int]


#: Where the rasm writes a base letter and a mini seen riding it, the read half
#: turns on one seen/saad khilaf, one per word it covers.
_SEEN_SAD_SITES: dict[Location, KhilafId] = {
    Location(2, 245, 14): KhilafId.SEEN_SAD_YABSUT,
    Location(7, 69, 22): KhilafId.SEEN_SAD_BASTAH,
    Location(52, 37, 7): KhilafId.SEEN_SAD_AL_MUSAYTIRUN,
    Location(88, 22, 3): KhilafId.SEEN_SAD_BIMUSAYTIR,
}


def _reading(view: SourceView, facts: AnalysisFacts, insc: InscriptionFacts,
             locations: tuple[Location, ...], selection: VariantSelection) -> _Reading:
    long_vowel = frozenset(
        i for i, f in enumerate(facts.sounds)
        if isinstance(f.value, Vowel) and f.value.long
    )
    consonant = frozenset(
        i for i, f in enumerate(facts.sounds) if isinstance(f.value, Consonant)
    )
    slot_of_unit = {
        unit.id.value: insc.slot_of[min(c.value for c in unit.character_ids)]
        for unit in view.units if unit.character_ids
    }
    canonical_quality = {
        uid: facts.slots[facts.slot_index[slot]].nucleus.quality
        for uid, slot in slot_of_unit.items()
    }
    owner = {
        s.value: unit.id.value for unit in view.units for s in unit.owned_sound_ids
    }
    main = tuple(
        unit.id.value for unit in view.units
        if unit.kind is LetterUnitKind.LETTER and unit.written_on_unit_id is None
    )
    below = frozenset(
        unit.id.value for unit in view.units
        if any(c.value in insc.below for c in unit.character_ids)
    )
    written_on = {
        unit.id.value: unit.written_on_unit_id.value
        for unit in view.units if unit.written_on_unit_id is not None
    }
    return _Reading(
        long_vowel, consonant, canonical_quality, slot_of_unit, owner, main,
        _variant_of_unit(view, locations, selection), below, written_on,
    )


def _variant_of_unit(
    view: SourceView, locations: tuple[Location, ...], selection: VariantSelection
) -> dict[int, Option]:
    """On both cells of a riding-letter pair, the seen/saad khilaf governing the
    pair's word, but only where this request selects that khilaf's option."""
    out: dict[int, Option] = {}
    for unit in view.units:
        if unit.kind is not LetterUnitKind.LETTER or unit.written_on_unit_id is None:
            continue
        khilaf = _SEEN_SAD_SITES.get(locations[unit.word_id.value])
        if khilaf is None:
            continue
        choice = selection.chosen(khilaf)
        if choice is None:
            continue
        option = Option(khilaf, choice)
        out[unit.id.value] = option
        out[unit.written_on_unit_id.value] = option
    return out


def _role(unit: LetterUnit, reading: _Reading) -> CellRole:
    if unit.kind is LetterUnitKind.HARAKA:
        return CellRole.HARAKA
    if unit.kind is LetterUnitKind.SUKUN:
        return CellRole.SUKUN
    if unit.kind is LetterUnitKind.TANWEEN:
        return CellRole.TANWEEN
    carries = any(s.value in reading.long_vowel_orders for s in unit.owned_sound_ids)
    return CellRole.MADD if carries else CellRole.LETTER


def _rides(unit: LetterUnit) -> bool:
    return unit.kind is not LetterUnitKind.LETTER or unit.written_on_unit_id is not None


def _tier(unit: LetterUnit, reading: _Reading) -> CellTier:
    """The written position of a riding mark, invariant of the boundary. A
    riding letter (the mini seen) takes its script's own position; a haraka or
    tanween is below for a kasra or kasratan and above otherwise."""
    if not _rides(unit):
        return CellTier.MAIN
    if unit.kind is LetterUnitKind.LETTER:
        return CellTier.BELOW if unit.id.value in reading.below_units else CellTier.ABOVE
    quality = reading.canonical_quality.get(unit.id.value)
    return CellTier.BELOW if quality is Quality.I else CellTier.ABOVE


def _main_of_slot(unit_id: int, reading: _Reading) -> int | None:
    slot = reading.slot_of_unit.get(unit_id)
    seats = [
        u for u in reading.main_units
        if reading.slot_of_unit.get(u) == slot and u != unit_id
    ]
    consonants = [u for u in seats if _owns_consonant(u, reading)]
    picked = consonants or seats
    return picked[0] if picked else None


def _followed_to_main(target: int, reading: _Reading) -> int | None:
    """A written_on target may itself be a riding mark -- the iqlab meem sits on
    the tanween, not the letter. Follow it to the main column it rests on."""
    main = set(reading.main_units)
    seen: set[int] = set()
    while target not in main:
        nxt = reading.written_on.get(target)
        if nxt is None or nxt in seen:
            return _main_of_slot(target, reading)
        seen.add(target)
        target = nxt
    return target


def _seat_unit(unit: LetterUnit, reading: _Reading) -> int | None:
    """The main letter or carrier a riding mark attaches to: the unit its
    written_on names, the carrier owning a long vowel it presents, or the
    consonant seat of its own slot."""
    if unit.written_on_unit_id is not None:
        return _followed_to_main(unit.written_on_unit_id.value, reading)
    for sound in unit.presented_sound_ids:
        if sound.value not in reading.long_vowel_orders:
            continue
        owner = reading.owner_of_sound.get(sound.value)
        if owner is not None:
            return owner
    return _main_of_slot(unit.id.value, reading)


def _owns_consonant(unit_id: int, reading: _Reading) -> bool:
    return any(
        owned == unit_id and sound in reading.consonant_orders
        for sound, owned in reading.owner_of_sound.items()
    )


def _column(unit: LetterUnit, reading: _Reading,
            column_of_unit: dict[int, int]) -> CellColumn:
    role = _role(unit, reading)
    tier = _tier(unit, reading)
    attached = None
    if tier is not CellTier.MAIN:
        seat = _seat_unit(unit, reading)
        attached = None if seat is None else CellColumnId(column_of_unit[seat])
    status = CellStatus.DROPPED if unit.silence is not None else CellStatus.PRESENT
    option = reading.variant_of_unit.get(unit.id.value)
    return CellColumn(
        id=CellColumnId(column_of_unit[unit.id.value]),
        role=role,
        text=unit.text,
        source_character_ids=unit.character_ids,
        source_unit_ids=(unit.id,),
        tier=tier,
        attached_to_column_id=attached,
        status=status,
        rule_occurrence_ids=unit.rule_occurrence_ids,
        silence=unit.silence,
        variant_id=None if option is None else option.khilaf,
        variant_choice=None if option is None else option.name,
    )


def _anchor(unit: LetterUnit) -> int:
    return min(c.value for c in unit.character_ids)


def _words(view: SourceView, reading: _Reading) -> tuple[CellWord, ...]:
    by_word: dict[int, list[LetterUnit]] = {}
    for unit in view.units:
        by_word.setdefault(unit.word_id.value, []).append(unit)
    ordered = {w: sorted(units, key=_anchor) for w, units in by_word.items()}

    column_of_unit: dict[int, int] = {}
    for word in sorted(ordered):
        for unit in ordered[word]:
            column_of_unit[unit.id.value] = len(column_of_unit)

    out: list[CellWord] = []
    for word in sorted(ordered):
        columns = tuple(
            _column(unit, reading, column_of_unit) for unit in ordered[word]
        )
        out.append(CellWord(view.units[ordered[word][0].id.value].word_id, columns))
    return tuple(out)


def build_cell_words(
    session: Session,
    *,
    ref: str,
    riwayah: str,
    script: str,
    variant: dict,
    extra_phonemes: frozenset[str] = frozenset(),
) -> tuple[CellWord, ...]:
    view = build_source_view(
        session, ref=ref, riwayah=riwayah, script=script, variant=variant,
        extra_phonemes=extra_phonemes,
    )
    facts = analyse(session, packaged_alphabet(), extra_phonemes=extra_phonemes)
    insc = inscribe(session)
    reading = _reading(
        view, facts, insc, session.locations, session.performance.selection
    )
    words = _words(view, reading)
    validate_cell_columns(words, view, reading.slot_of_unit)
    return words


__all__ = ["build_cell_words"]
