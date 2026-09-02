"""Project source letter units into sound-owned animation paint targets."""
from __future__ import annotations

from collections import defaultdict

from ..model.rule import Rule
from . import ids
from .dtos import AnalysisBundle
from .source_dtos import AnimationPolicy, AnimationToken, LetterUnit, LetterUnitKind

_TATWEEL = "ـ"
_READING_AID_SEEN = frozenset({"ۜ", "ۣ"})


class AnimationProjectionError(ValueError):
    """The source ownership graph cannot name a sounding highlight target."""


def _ordered_characters(group: list[LetterUnit]) -> tuple[ids.CharacterId, ...]:
    return tuple(sorted(
        (character for unit in group for character in unit.character_ids),
        key=lambda item: item.value,
    ))


def _character_text(group: list[LetterUnit]) -> dict[int, str]:
    return {
        character.value: scalar
        for unit in group
        for character, scalar in zip(unit.character_ids, unit.text, strict=True)
    }


def _paint_characters(
    characters: tuple[ids.CharacterId, ...], text_by_character: dict[int, str]
) -> tuple[ids.CharacterId, ...]:
    """A tatweel seats a separately drawn small letter but owns no ink target."""
    painted = tuple(
        character
        for character in characters
        if text_by_character[character.value] != _TATWEEL
    )
    return painted or characters


def _highlight_presented_sounds(
    sounds: tuple[ids.SoundId, ...], bundle: AnalysisBundle
) -> tuple[ids.SoundId, ...]:
    """Exclude a solar article lam's geometric presentation from audibility."""
    return tuple(
        sound
        for sound in sounds
        if not any(
            bundle.rule_occurrences[occurrence.value].rule_id.value
            == Rule.LAM_SHAMSIYYAH.value
            for occurrence in bundle.sounds[sound.value].rule_occurrence_ids
        )
    )


def build_animation_tokens(
    units: tuple[LetterUnit, ...], bundle: AnalysisBundle
) -> tuple[AnimationToken, ...]:
    """Use source units and sound ownership as the animation-token authority.

    A riding source unit stays with the letter it is written on. Every other
    letter unit is one target. Soundless targets co-highlight the next sounding
    target, or the previous sounding target when they trail the reading, which
    is the established timing-letter allocation convention.
    """
    letters = [unit for unit in units if unit.kind is LetterUnitKind.LETTER]
    letter_ids = {unit.id.value for unit in letters}
    groups: dict[int, list[LetterUnit]] = defaultdict(list)
    for unit in letters:
        # These marks select between their own seen and the written sad. They
        # need separate paint targets even though the mark is positioned on the
        # sad; the active variant assigns the sound to exactly one of them.
        host = None if unit.text in _READING_AID_SEEN else unit.written_on_unit_id
        key = host.value if host is not None and host.value in letter_ids else unit.id.value
        groups[key].append(unit)
    ordered = [groups[key] for key in sorted(groups)]

    unit_to_token = {
        unit.id.value: token_id
        for token_id, group in enumerate(ordered)
        for unit in group
    }
    reading_aid_pair: dict[int, int] = {}
    for token_id, group in enumerate(ordered):
        for unit in group:
            if unit.text not in _READING_AID_SEEN or unit.written_on_unit_id is None:
                continue
            host = unit_to_token[unit.written_on_unit_id.value]
            reading_aid_pair[token_id] = host
            reading_aid_pair[host] = token_id
    sound_owner = {
        sound.value: unit_to_token[unit.id.value]
        for unit in letters
        for sound in unit.owned_sound_ids
    }
    owned_by_token = [tuple(dict.fromkeys(
        sound for unit in group for sound in unit.owned_sound_ids
    )) for group in ordered]
    presented_by_token = [tuple(dict.fromkeys(
        sound for unit in group for sound in unit.presented_sound_ids
    )) for group in ordered]
    direct_by_token = [tuple(dict.fromkeys((
        *owned,
        *(sound for sound in presented if sound.value not in sound_owner),
    ))) for owned, presented in zip(owned_by_token, presented_by_token, strict=True)]
    timing_owner = dict(sound_owner)
    for token_id, direct in enumerate(direct_by_token):
        for sound in direct:
            timing_owner.setdefault(sound.value, token_id)
    timed = [index for index, direct in enumerate(direct_by_token) if direct]
    audible_target = {index: index for index in timed}
    for token_id, (direct, presented) in enumerate(
        zip(direct_by_token, presented_by_token, strict=True)
    ):
        if direct or not presented:
            continue
        targets = {timing_owner[sound.value] for sound in presented}
        if len(targets) != 1:
            raise AnimationProjectionError(
                f"animation token {token_id} presents sounds owned by {sorted(targets)}"
            )
        audible_target[token_id] = targets.pop()
    audible = sorted(audible_target)
    audible_by_word: dict[int, list[int]] = defaultdict(list)
    for index in audible:
        audible_by_word[ordered[index][0].word_id.value].append(index)
    if ordered and not timed:
        raise AnimationProjectionError("the reading has no sounding animation token")

    tokens: list[AnimationToken] = []
    for token_id, group in enumerate(ordered):
        primary = group[0]
        unit_ids = tuple(sorted((unit.id for unit in group), key=lambda item: item.value))
        character_ids = _ordered_characters(group)
        text_by_character = _character_text(group)
        owned = owned_by_token[token_id]
        presented = presented_by_token[token_id]
        direct = direct_by_token[token_id]
        sounds = tuple(dict.fromkeys((
            *owned,
            *_highlight_presented_sounds(presented, bundle),
        )))
        target: int | None = None
        policy = AnimationPolicy.TIMED
        if not direct:
            if presented:
                target = audible_target[token_id]
            else:
                word_audible = audible_by_word[primary.word_id.value]
                following = [index for index in word_audible if index > token_id]
                preceding = [index for index in word_audible if index < token_id]
                rule_ids = {
                    bundle.rule_occurrences[item.value].rule_id.value
                    for unit in group
                    for item in unit.rule_occurrence_ids
                }
                paired = reading_aid_pair.get(token_id)
                if paired is not None and paired in audible_target:
                    target = audible_target[paired]
                elif Rule.HAMZA_WASL_SILENT.value in rule_ids and following:
                    target = audible_target[following[0]]
                elif preceding:
                    target = audible_target[preceding[-1]]
                elif following:
                    target = audible_target[following[0]]
                else:
                    global_following = [index for index in audible if index > token_id]
                    global_preceding = [index for index in audible if index < token_id]
                    if global_following:
                        target = audible_target[global_following[0]]
                    elif global_preceding:
                        target = audible_target[global_preceding[-1]]
                    else:
                        raise AnimationProjectionError(
                            f"animation token {token_id} has no sounding neighbour"
                        )
            policy = (
                AnimationPolicy.COHIGHLIGHT_PREVIOUS
                if target < token_id else AnimationPolicy.COHIGHLIGHT_NEXT
            )
        tokens.append(AnimationToken(
            id=ids.AnimationTokenId(token_id),
            word_id=primary.word_id,
            source_unit_ids=unit_ids,
            character_ids=character_ids,
            paint_character_ids=_paint_characters(character_ids, text_by_character),
            text="".join(text_by_character[character.value] for character in character_ids),
            sound_ids=sounds,
            policy=policy,
            target_token_id=None if target is None else ids.AnimationTokenId(target),
        ))
    return tuple(tokens)


__all__ = ["AnimationProjectionError", "build_animation_tokens"]
