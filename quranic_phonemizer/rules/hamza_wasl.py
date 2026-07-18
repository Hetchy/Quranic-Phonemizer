from __future__ import annotations

from ..model import Consonant, Harakah, Letter, Vowel, VowelQuality
from ..rule_data import RuleConfig
from .context import LetterState, RuleContext


def pronounce_hamza_wasl(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> list:
    word = context.word(state)
    if state.letter_index == 0 and word.starting:
        skeleton = word.skeleton
        if _starts_with_any(
            skeleton,
            config.hamza_wasl_kasra_nouns + config.hamza_wasl_kasra_verbs,
        ):
            return [Consonant(Letter.HAMZA_WASL), Vowel(VowelQuality.I_VOWEL)]

        second = context.next_letter(state)
        third = context.next_letter(state, 2)
        if second is not None and second.form.letter is Letter.LAM:
            return [Consonant(Letter.HAMZA_WASL), Vowel(VowelQuality.A)]
        if third is not None:
            if third.form.harakah is Harakah.DAMMA:
                return [Consonant(Letter.HAMZA_WASL), Vowel(VowelQuality.U)]
            if third.form.harakah in {Harakah.FATHA, Harakah.KASRA}:
                return [Consonant(Letter.HAMZA_WASL), Vowel(VowelQuality.I_VOWEL)]

    if state.letter_index == 0:
        previous = context.previous_letter(state)
        if previous is None:
            return []
        if not previous.segments:
            previous = context.previous_letter(state, 2)
        if previous is not None and previous.form.tanween is not None:
            previous.segments.append(Vowel(VowelQuality.I_VOWEL))
        context.shorten_previous_vowel(state)
    return []


def _starts_with_any(
    value: tuple,
    patterns: tuple[tuple[Letter, ...], ...],
) -> bool:
    return any(value[: len(pattern)] == pattern for pattern in patterns)
