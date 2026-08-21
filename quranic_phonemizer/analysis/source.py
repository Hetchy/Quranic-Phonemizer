"""Assemble the source view: the exact characters and the units over them.

A native build off the inscription and performance tiers, reusing the core
bundle for the sound, occurrence and merger identities the units reference.
"""
from __future__ import annotations

from collections import defaultdict

from ..render.alphabet import packaged_alphabet
from ..session import Session
from . import ids
from .build import build_bundle
from .facts import analyse
from .glyphs import Glyph, GlyphKind
from .inscription import InscriptionFacts, inscribe
from .source_dtos import (
    Character,
    CharacterKind,
    LetterUnit,
    MergerPlacement,
    RulePlacement,
    SourceView,
)
from .source_laws import validate_source_view
from .source_ownership import Ownership, ownership
from .source_placements import Placements, placements
from .source_units import Tokenization, UnitDraft, tokenize


def _character(glyph: Glyph, tok: Tokenization, boundary: int) -> Character:
    index = glyph.source_index
    if glyph.kind is GlyphKind.STOP_SIGN or index in tok.sakt_seen_glyphs:
        return _boundary_char(glyph, CharacterKind.STOP_SIGN, boundary)
    if glyph.word is None:
        return _boundary_char(glyph, CharacterKind.SEPARATOR, boundary)
    return Character(
        id=ids.CharacterId(index),
        index=index,
        text=glyph.char,
        kind=CharacterKind.LEXICAL,
        word_id=ids.WordId(glyph.word),
        boundary_id=None,
        letter_unit_id=ids.LetterUnitId(tok.unit_of_glyph[index]),
    )


def _boundary_char(glyph: Glyph, kind: CharacterKind, boundary: int) -> Character:
    return Character(
        id=ids.CharacterId(glyph.source_index),
        index=glyph.source_index,
        text=glyph.char,
        kind=kind,
        word_id=None,
        boundary_id=ids.BoundaryId(boundary),
        letter_unit_id=None,
    )


def _characters(insc: InscriptionFacts, tok: Tokenization) -> tuple[Character, ...]:
    out: list[Character] = []
    current: int | None = None
    for glyph in insc.glyphs:
        lexical = (
            glyph.word is not None
            and glyph.kind is not GlyphKind.STOP_SIGN
            and glyph.source_index not in tok.sakt_seen_glyphs
        )
        if lexical:
            current = glyph.word
        boundary = current + 1 if current is not None else 0
        out.append(_character(glyph, tok, boundary))
    return tuple(out)


def _ranges(glyphs: list[int]) -> tuple[tuple[int, int], ...]:
    out: list[list[int]] = []
    for g in glyphs:
        if out and out[-1][1] == g:
            out[-1][1] = g + 1
        else:
            out.append([g, g + 1])
    return tuple((lo, hi) for lo, hi in out)


def _owned_by_unit(own: Ownership) -> dict[int, list[int]]:
    out: dict[int, list[int]] = defaultdict(list)
    for sound, unit in own.owner.items():
        out[unit].append(sound)
    return out


def _silence(own: Ownership, index: int):
    reason = own.silence.get(index)
    return ids.OccurrenceId(reason) if isinstance(reason, int) else reason


def _presented_by_unit(own: Ownership) -> dict[int, list[int]]:
    out: dict[int, list[int]] = defaultdict(list)
    for sound, units in own.presenters.items():
        for unit in units:
            out[unit].append(sound)
    return out


def _letter_unit(
    index: int,
    draft: UnitDraft,
    insc: InscriptionFacts,
    tok: Tokenization,
    own: Ownership,
    plc: Placements,
    owned: dict[int, list[int]],
    presented: dict[int, list[int]],
) -> LetterUnit:
    written_on = draft.written_on_anchor
    return LetterUnit(
        id=ids.LetterUnitId(index),
        word_id=ids.WordId(draft.word),
        character_ids=tuple(ids.CharacterId(g) for g in draft.glyphs),
        ranges=_ranges(draft.glyphs),
        text="".join(insc.glyphs[g].char for g in draft.glyphs),
        kind=draft.kind,
        written_on_unit_id=(
            None if written_on is None
            else ids.LetterUnitId(tok.unit_of_anchor[written_on])
        ),
        owned_sound_ids=tuple(ids.SoundId(s) for s in sorted(owned.get(index, ()))),
        presented_sound_ids=tuple(
            ids.SoundId(s) for s in sorted(presented.get(index, ()))
        ),
        rule_occurrence_ids=tuple(
            ids.OccurrenceId(o) for o in plc.unit_occurrences.get(index, ())
        ),
        silence=_silence(own, index),
    )


def build_source_view(
    session: Session,
    *,
    ref: str,
    riwayah: str,
    script: str,
    variant: dict,
    extra_phonemes: frozenset[str] = frozenset(),
) -> SourceView:
    bundle = build_bundle(
        session, ref=ref, riwayah=riwayah, script=script, variant=variant,
        extra_phonemes=extra_phonemes,
    )
    facts = analyse(session, packaged_alphabet(), extra_phonemes=extra_phonemes)
    insc = inscribe(session)
    sakt_words = frozenset(
        i for i, word in enumerate(session.score.words) if word.sakt_after
    )
    tok = tokenize(insc, sakt_words)
    own = ownership(facts, tok, insc)
    plc = placements(own, bundle.sounds, bundle.rule_occurrences, bundle.mergers)

    owned = _owned_by_unit(own)
    presented = _presented_by_unit(own)
    units = tuple(
        _letter_unit(i, draft, insc, tok, own, plc, owned, presented)
        for i, draft in enumerate(tok.units)
    )
    view = SourceView(
        text=bundle.source_text,
        characters=_characters(insc, tok),
        units=units,
        rule_placements=_rule_placements(plc),
        merger_placements=_merger_placements(plc),
    )
    validate_source_view(view, bundle)
    return view


def _rule_placements(plc: Placements) -> tuple[RulePlacement, ...]:
    return tuple(
        RulePlacement(
            ids.OccurrenceId(occ),
            tuple(ids.LetterUnitId(u) for u in units),
        )
        for occ, units in plc.rule_placements
    )


def _merger_placements(plc: Placements) -> tuple[MergerPlacement, ...]:
    return tuple(
        MergerPlacement(
            ids.MergerId(merger),
            tuple(ids.LetterUnitId(u) for u in before),
            tuple(ids.LetterUnitId(u) for u in after),
        )
        for merger, before, after in plc.merger_placements
    )


__all__ = ["build_source_view"]
