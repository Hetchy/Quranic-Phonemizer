from __future__ import annotations

from ..model import (
    Consonant,
    Harakah,
    Letter,
    SourceMark,
    Tanween,
    Vowel,
    VowelQuality,
)
from ..rule_data import RuleConfig
from .context import LetterState, RuleContext
from .idgham import pronounce_generic


def pronounce_raa(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> tuple[list, bool]:
    if state.form.has_mark(SourceMark.IMALA):
        return [Consonant(Letter.RA), Vowel(VowelQuality.IMALA)], False
    if state.harakah is None and state.tanween is None:
        return pronounce_generic(context, state, config), False

    heavy = _is_heavy(context, state, config)
    return [Consonant(Letter.RA, geminated=state.shaddah, emphatic=heavy)], heavy


def _is_heavy(context: RuleContext, state: LetterState, config: RuleConfig) -> bool:
    if state.tanween in {Tanween.FATH, Tanween.DAMM}:
        return True
    if state.tanween is Tanween.KASR:
        return False
    if state.harakah in {Harakah.FATHA, Harakah.DAMMA}:
        return True
    if state.harakah is Harakah.KASRA:
        return False

    previous = context.previous_letter(state)
    if previous is None:
        return False
    previous_harakah = previous.form.harakah
    if previous_harakah is None and previous.form.tanween is None:
        if previous.form.letter in {Letter.HAMZA_WASL, Letter.ALIF, Letter.WAW}:
            return True
        if previous.form.letter is Letter.YA:
            return False
    if previous_harakah in {Harakah.FATHA, Harakah.DAMMA}:
        return True
    if previous_harakah is Harakah.KASRA:
        following = context.next_letter(state)
        return bool(
            following
            and following.word_index == state.word_index
            and following.form.letter in config.inherent_emphasis
        )
    if previous_harakah is Harakah.SUKUN:
        if previous.form.letter is Letter.YA:
            return False
        before = context.previous_letter(state, 2)
        return bool(before and before.form.harakah in {Harakah.FATHA, Harakah.DAMMA})
    return False
