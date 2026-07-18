from __future__ import annotations

from ..model import Consonant, Harakah, Letter, Nasal, Vowel, VowelQuality
from ..rule_data import RuleConfig
from .context import LetterState, RuleContext
from .vowels import pronounce_harakah


def pronounce_noon(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> list:
    if state.shaddah:
        return [Consonant(Letter.NOON, nasalized=True)]

    contextual_sukun = (state.harakah is None and state.tanween is None) or (
        context.word(state).expanded and state.harakah is Harakah.SUKUN
    )
    if not contextual_sukun:
        return [Consonant(Letter.NOON)]

    following = context.next_letter(state)
    if following is None:
        return [Consonant(Letter.NOON)]
    target = following.form.letter

    if target in config.noon_iqlab or target in config.noon_ikhfaa:
        return [Nasal(target in config.inherent_emphasis)]
    if target in config.noon_idgham_ghunnah:
        following.segments = [Consonant(target, nasalized=True)]
        following.segments.extend(pronounce_harakah(following, emphatic=False))
        following.resolved = True
        return []
    if target in config.noon_idgham_plain:
        return []
    return [Consonant(Letter.NOON)]


def pronounce_tanween(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> list:
    if state.tanween is None:
        return []

    emphatic = state.tanween.quality is VowelQuality.A and (
        state.form.letter in config.inherent_emphasis or state.form.letter is Letter.RA
    )
    vowel = Vowel(state.tanween.quality, emphatic=emphatic)
    following = context.next_letter(state)
    if following is None:
        return []

    if following.form.letter in {Letter.ALIF, Letter.ALIF_MAQSURA}:
        if context.word(state).stopping:
            return [Vowel(state.tanween.quality, long=True, emphatic=emphatic)]
        following.segments = []
        following.resolved = True
        following = context.next_letter(state, 2)
        if following is None:
            return [Vowel(state.tanween.quality, long=True, emphatic=emphatic)]

    target = following.form.letter
    if target in config.noon_iqlab or target in config.noon_ikhfaa:
        return [vowel, Nasal(target in config.inherent_emphasis)]
    if target in config.noon_idgham_ghunnah:
        following.segments = [Consonant(target, nasalized=True)]
        following.segments.extend(pronounce_harakah(following, emphatic=False))
        following.resolved = True
        return [vowel]
    if target in config.noon_idgham_plain:
        return [vowel]
    return [vowel, Consonant(Letter.NOON)]
