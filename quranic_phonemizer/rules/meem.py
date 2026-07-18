from __future__ import annotations

from ..model import Consonant, Harakah, Letter, Nasal
from ..rule_data import RuleConfig
from .context import LetterState, RuleContext
from .vowels import pronounce_harakah


def pronounce_meem(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> list:
    if state.shaddah:
        return [Consonant(Letter.MEEM, nasalized=True)]

    contextual_sukun = (state.harakah is None and state.tanween is None) or (
        context.word(state).expanded and state.harakah is Harakah.SUKUN
    )
    if not contextual_sukun:
        return [Consonant(Letter.MEEM)]

    word = context.word(state)
    is_last = state.letter_index == len(word.letters) - 1
    following = context.next_letter(state)
    if not is_last or following is None:
        return [Consonant(Letter.MEEM)]

    if following.form.letter in config.meem_ikhfaa:
        return [Nasal()]
    if following.form.letter in config.meem_idgham:
        following.segments = pronounce_harakah(following, emphatic=False)
        following.resolved = True
        return [Consonant(Letter.MEEM, nasalized=True)]
    return [Consonant(Letter.MEEM)]
