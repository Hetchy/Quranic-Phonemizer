from __future__ import annotations

from ..model import (
    Consonant,
    Harakah,
    Letter,
    SourceMark,
    Vowel,
    VowelQuality,
)
from ..rule_data import RuleConfig
from .context import LetterState, RuleContext
from .idgham import pronounce_generic


def pronounce_harakah(state: LetterState, *, emphatic: bool) -> list:
    if state.harakah is None or state.harakah is Harakah.SUKUN:
        return []
    quality = state.harakah.quality
    if quality is None:
        return []
    return [
        Vowel(
            quality,
            long=state.form.length_marked or state.force_long_vowel,
            emphatic=emphatic and quality is VowelQuality.A,
        )
    ]


def _lengthen_previous(
    context: RuleContext,
    state: LetterState,
    compatible: frozenset[VowelQuality],
) -> list:
    slot = context.previous_segment_slot(state)
    if slot is None:
        return []
    owner, index = slot
    segment = owner.segments[index]
    if (
        not isinstance(segment, Vowel)
        or segment.long
        or segment.quality not in compatible
    ):
        return []
    owner.segments.pop(index)
    return [Vowel(segment.quality, long=True, emphatic=segment.emphatic)]


def pronounce_vowel_letter(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> list:
    letter = state.form.letter
    word = context.word(state)

    if state.form.has_mark(SourceMark.SILENT_ALWAYS):
        return []

    if letter is Letter.ALIF:
        if state.form.has_mark(SourceMark.SILENT_IN_WASL) and not word.stopping:
            return []
        return _lengthen_previous(
            context,
            state,
            frozenset({VowelQuality.A}),
        )

    if letter is Letter.ALIF_MAQSURA:
        if state.harakah is not None or state.tanween is not None or state.shaddah:
            return pronounce_generic(context, state, config)
        is_last = state.letter_index == len(word.letters) - 1
        previous = context.previous_letter(state)
        if is_last and word.stopping and previous and previous.form.tanween is None:
            segment = context.previous_segment(state)
            if (
                not isinstance(segment, Vowel)
                or segment.long
                or segment.quality
                not in {
                    VowelQuality.A,
                    VowelQuality.I_VOWEL,
                }
            ):
                return [Consonant(Letter.YA)]
        return _lengthen_previous(
            context,
            state,
            frozenset({VowelQuality.A, VowelQuality.I_VOWEL, VowelQuality.IMALA}),
        )

    if letter is Letter.WAW:
        following = context.next_letter(state)
        if (
            following is not None
            and following.form.letter is Letter.WAW
            and following.form.shaddah
            and not word.stopping
        ):
            return []
        if following is not None and following.form.letter is Letter.ALIF:
            previous = context.previous_letter(state)
            if (
                word.stopping
                and previous is not None
                and previous.form.harakah is Harakah.FATHA
                and state.form.harakah is None
                and state.form.tanween is None
                and not state.form.length_marked
            ):
                return [Consonant(Letter.WAW)]
            after_alif = context.next_letter(state, 2)
            if (
                after_alif is not None
                and after_alif.form.letter is Letter.WAW
                and after_alif.form.shaddah
            ):
                return []
        previous = context.previous_letter(state)
        stopped_carrier = (
            state.harakah is Harakah.SUKUN
            and state.letter_index == len(word.letters) - 1
            and word.stopping
            and not state.shaddah
            and previous is not None
            and previous.form.harakah is Harakah.DAMMA
        )
        if (
            state.harakah is not None or state.tanween is not None
        ) and not stopped_carrier:
            return pronounce_generic(context, state, config)
        return _lengthen_previous(
            context,
            state,
            frozenset({VowelQuality.A, VowelQuality.U}),
        )

    if letter is Letter.YA:
        previous = context.previous_letter(state)
        stopped_carrier = (
            state.harakah is Harakah.SUKUN
            and state.letter_index == len(word.letters) - 1
            and word.stopping
            and not state.shaddah
            and previous is not None
            and previous.form.harakah is Harakah.KASRA
        )
        if (
            state.harakah is not None or state.tanween is not None
        ) and not stopped_carrier:
            return pronounce_generic(context, state, config)
        following = context.next_letter(state)
        if following is not None and following.form.letter is Letter.YA:
            return []
        return _lengthen_previous(
            context,
            state,
            frozenset({VowelQuality.I_VOWEL}),
        )

    raise ValueError(f"Not a vowel letter: {letter}")
