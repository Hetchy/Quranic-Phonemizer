from __future__ import annotations

from ..model import Consonant, Harakah, Letter, Release, Segment, Vowel, VowelQuality
from ..rule_data import RuleConfig
from .boundaries import realize_boundary
from .context import LetterState, RuleContext
from .hamza_wasl import pronounce_hamza_wasl
from .idgham import pronounce_generic
from .meem import pronounce_meem
from .noon_tanween import pronounce_noon, pronounce_tanween
from .raa import pronounce_raa
from .vowels import pronounce_harakah, pronounce_vowel_letter


_VOWEL_LETTERS = {Letter.ALIF, Letter.ALIF_MAQSURA, Letter.WAW, Letter.YA}


def apply_rules(context: RuleContext, config: RuleConfig) -> None:
    for word in context.words:
        for state in word.letters:
            if state.resolved:
                continue
            realize_boundary(context, state)
            consonants, emphatic_vowel = _pronounce_letter(context, state, config)
            state.segments = consonants
            if state.tanween is not None:
                state.segments.extend(pronounce_tanween(context, state, config))
            else:
                state.segments.extend(pronounce_harakah(state, emphatic=emphatic_vowel))
            state.resolved = True


def _pronounce_letter(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> tuple[list[Segment], bool]:
    letter = state.form.letter
    if letter is Letter.HAMZA_WASL:
        return pronounce_hamza_wasl(context, state, config), False
    if letter is Letter.RA:
        return pronounce_raa(context, state, config)
    if letter is Letter.LAM and _is_allah_lam(context, state, config):
        state.force_long_vowel = True
        heavy = _allah_lam_is_heavy(context, state)
        return [Consonant(Letter.LAM, geminated=True, emphatic=heavy)], heavy
    if letter is Letter.NOON:
        return pronounce_noon(context, state, config), False
    if letter is Letter.MEEM:
        return pronounce_meem(context, state, config), False
    if letter in _VOWEL_LETTERS:
        return pronounce_vowel_letter(context, state, config), False
    if letter is Letter.TAA_MARBUTA:
        is_last = state.letter_index == len(context.word(state).letters) - 1
        if is_last and state.harakah is Harakah.SUKUN:
            return [Consonant(Letter.HA)], False
        return [Consonant(Letter.TAA_MARBUTA)], False
    if letter in config.qalqala and state.harakah is Harakah.SUKUN:
        return [
            Consonant(
                letter,
                geminated=state.shaddah,
                emphatic=letter in config.inherent_emphasis,
            ),
            Release.QALQALA,
        ], letter in config.inherent_emphasis

    emphatic = letter in config.inherent_emphasis
    return pronounce_generic(context, state, config, emphatic=emphatic), emphatic


def _is_allah_lam(
    context: RuleContext,
    state: LetterState,
    config: RuleConfig,
) -> bool:
    word = context.word(state)
    return (
        state.shaddah and state.letter_index > 0 and word.skeleton in config.allah_words
    )


def _allah_lam_is_heavy(context: RuleContext, state: LetterState) -> bool:
    previous = context.previous_segment(state)
    return isinstance(previous, Vowel) and previous.quality in {
        VowelQuality.A,
        VowelQuality.U,
    }
