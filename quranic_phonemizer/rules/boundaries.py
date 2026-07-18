from __future__ import annotations

from ..model import Harakah, Letter, SourceMark, Tanween
from .context import LetterState, RuleContext


def realize_boundary(context: RuleContext, state: LetterState) -> None:
    word = context.word(state)
    if state.letter_index == 0 and word.starting:
        state.shaddah = False

    is_last = state.letter_index == len(word.letters) - 1
    if is_last and word.stopping:
        if state.form.letter is Letter.HAMZA and state.form.tanween is Tanween.FATH:
            state.tanween = None
            state.harakah = Harakah.FATHA
            state.force_long_vowel = True
        elif state.form.letter is Letter.ALIF or (
            state.form.letter is Letter.ALIF_MAQSURA
            and state.form.harakah is not Harakah.SUKUN
        ):
            state.harakah = None
            state.tanween = None
        else:
            state.harakah = Harakah.SUKUN
            state.tanween = None
        return

    following = context.next_letter(state)
    if (
        word.stopping
        and (state.form.harakah is not None or state.form.tanween is not None)
        and following is not None
        and following.word_index == state.word_index
        and following.letter_index == len(word.letters) - 1
        and following.form.has_mark(SourceMark.SILENT_ALWAYS)
    ):
        state.harakah = Harakah.SUKUN
        state.tanween = None
