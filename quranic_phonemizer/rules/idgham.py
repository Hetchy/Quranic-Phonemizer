from __future__ import annotations

from ..model import Consonant
from ..rule_data import RuleConfig
from .context import LetterState, RuleContext


def _is_partial_assimilation(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> bool:
    following = context.next_letter(state)
    if following is None:
        return False
    return following.form.letter in config.partial_assimilation.get(
        state.form.letter, ()
    )


def pronounce_generic(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
    *,
    emphatic: bool = False,
) -> list:
    if state.harakah is None and state.tanween is None and not state.shaddah:
        if _is_partial_assimilation(context, state, config):
            return [Consonant(state.form.letter, emphatic=emphatic)]
        return []
    return [
        Consonant(
            state.form.letter,
            geminated=state.shaddah,
            emphatic=emphatic,
        )
    ]
