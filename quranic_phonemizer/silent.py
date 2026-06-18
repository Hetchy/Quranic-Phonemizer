"""
Per-grapheme silent flags for the Timestamps highlight.

A phoneme is written with several graphemes but only one is pronounced; the rest
are silent (hamza wasl, lam shamsiyah, the otiose tanween alef, an assimilated
noon, …). The Inspector Timestamps tab splits every letter into its own cell and
highlights the cell being uttered — so it needs, per written grapheme, whether
that grapheme is silent (skip it) or sounding (highlight it).

``build_silent_flags`` returns one ``(char, silent, mark)`` triple per written
grapheme (base letters + split extensions) in reading order — the exact order and
tokenization of the bucket TS-shard ``letters[]`` (proven 1:1 against a real
shard). The consumer zips it straight onto the shard letters. ``char`` is bare
(matches the shard); ``mark`` is the silence-indicating combining mark written
above the grapheme (the SILENT_ALWAYS / SILENT_AT_CONTINUATION small-zero,
U+06DF / U+06E0) or ``""`` — surfaced from ``other_symbols`` (which
``get_full_char`` omits) so the consumer can render it on the grapheme.

``silent`` is the *linguistic* fact: the grapheme produces no audible phoneme at
its own position in the final (post-redistribution) output. The dagger alef
(U+0670) is an unconditional madd and always sounds; a silah (mini waw/yaa,
U+06E5/U+06E6) is the attached pronoun and so is always the WORD-FINAL letter — it
drops at waqf. A mini-waw that is NOT word-final (وَٱلْغَاوُۥنَ → ``...و ۥ ن``) is a
stem long vowel, not a silah, and always sounds. A carrier waw (صَلَوٰة, زَكَوٰة) is a silent seat for a dagger-alef
madd — when the shard splits the dagger off, the waw grapheme is silent and the
dagger carries the sound. Cross-word idgham mergers are reported by their linguistic silence
too; keeping both bridge letters highlighted is a rendering choice the consumer
applies on top (it already owns the bridge tile).

``sounding_in_flat`` mirrors the two redistributions the flat builder applies on
top of the raw per-letter phonemes, so the flag is correct for BOTH continuous
and stopping recitation:
  - iltiqaa: a shortened long vowel before hamza wasl moves to the preceding
    consonant; the vowel letter goes silent.
  - waqf tanween: when stopping, the long vowel moves from the tanween consonant
    onto the otherwise-silent alef / alef-maksura, which becomes the carrier.
"""

from __future__ import annotations

from typing import List, Tuple

from .tajweed_rule import TajweedRule
from .letter_phoneme_mapping import TANWEEN_DIACRITICS, get_full_char, is_madd_phoneme
from .mapping import PhonemizationMapping, WordMapping

# Extension graphemes the bucket TS-shard splits into their OWN ``letters[]``
# entry: dagger alef, mini waw, mini yaa. The maddah (ٓ U+0653) and other
# combining marks stay merged with their base letter (so آ = ا+ٓ is one entry),
# matching the aligner's tokenization exactly.
_SPLIT_EXTENSIONS = {"ٰ", "ۥ", "ۦ"}  # ٰ ۥ ۦ

# A long vowel shortened before hamza wasl is stored on the vowel letter as one
# of these short vowels, then moved to the preceding consonant by the flat builder.
_SHORT_VOWELS = {"a", "aˤ", "u", "i"}

# The silah (mini waw / mini yaa, U+06E5 / U+06E6) is a conditional madd —
# pronounced in wasl, dropped at waqf — so it is silent only when its word stops.
# The dagger alef (U+0670, the third split extension) is an unconditional madd that
# always sounds.
_SILAH_EXTENSIONS = {"ۥ", "ۦ"}


def _is_carrier_waw(lm) -> bool:
    """A waw that is a silent seat for a dagger-alef madd (صَلَوٰة, زَكَوٰة, ٱلْحَيَوٰة).

    It carries a dagger alef and contributes only the madd — no consonant ``w`` —
    so when the shard splits the dagger into its own grapheme, the waw itself is
    silent and the split-off dagger carries the sound. A consonant waw + dagger
    (وَٰعَدْنَا → ``w`` then madd) keeps its ``w`` and is NOT a carrier; a plain
    long-vowel waw (نُوحٍ) has no dagger.
    """
    if lm.char != "و":
        return False
    if not any(getattr(ext, "name", "") == "DAGGER_ALEF" for ext in lm.extensions):
        return False
    return bool(lm.phonemes) and all(is_madd_phoneme(p) for p in lm.phonemes)


def _silent_mark(lm) -> str:
    """The silence-indicating combining mark above ``lm`` (the SILENT_ALWAYS /
    SILENT_AT_CONTINUATION small-zero, U+06DF / U+06E0), or ``""``. It lives in
    ``other_symbols`` — which ``get_full_char`` omits — so the highlight can render
    it on the grapheme."""
    for sym in getattr(lm, "other_symbols", None) or []:
        if sym.name.startswith("SILENT"):
            return sym.char
    return ""


def sounding_in_flat(word: WordMapping, li: int) -> bool:
    """Whether the letter at ``li`` contributes an audible phoneme at its own
    grapheme position in the final flat output (i.e. is a highlight target)."""
    lm = word.letter_mappings[li]
    if lm.phonemes:
        src = {t.rule for t in lm.tajweed_rules if t.is_source}
        if (TajweedRule.SILENT_ILTIQAA_SAKINAYN in src
                and len(lm.phonemes) == 1 and lm.phonemes[0] in _SHORT_VOWELS):
            return False  # demoted to the preceding consonant
        return True
    # raw-silent: the waqf-tanween redistribution target becomes the madd carrier
    if word.is_stopping and lm.char in ("ا", "ى") and li > 0:
        prev = word.letter_mappings[li - 1]
        if (prev.diacritic in TANWEEN_DIACRITICS
                and prev.phonemes and ":" in prev.phonemes[-1]):
            return True
    return False


def build_silent_flags(mapping: PhonemizationMapping) -> List[Tuple[str, bool, str]]:
    """``[(char, silent, mark), ...]`` — one per written grapheme, in reading order.

    ``char`` is the bare grapheme (base letter or split extension) matching the
    shard tokenization; ``silent`` its linguistic silence at its own position;
    ``mark`` the silence-indicating combining mark above it (or ``""``). The base
    grapheme owns the letter's ``silent`` and ``mark``; the dagger alef madd
    always sounds while the silah drops at waqf.
    """
    flags: List[Tuple[str, bool, str]] = []
    for word in mapping.words:
        for li, lm in enumerate(word.letter_mappings):
            silent = not sounding_in_flat(word, li)
            mark = _silent_mark(lm)
            carrier_waw = _is_carrier_waw(lm)
            # Tokenize exactly like the bucket shard: the standalone extension
            # graphemes (dagger alef, mini waw/yaa) become their own tokens, while
            # every other combining mark (the maddah ٓ, …) merges onto the grapheme
            # it follows — so e.g. a madd-silah is one ``ۦٓ`` token, not ``ۦ`` + ``ٓ``.
            tokens: List[str] = []
            for ch in get_full_char(lm):
                if not tokens or ch in _SPLIT_EXTENSIONS:
                    tokens.append(ch)
                else:
                    tokens[-1] += ch
            is_word_final = li == len(word.letter_mappings) - 1
            for i, tok in enumerate(tokens):
                if tok[0] in _SPLIT_EXTENSIONS:
                    # Dagger alef is an unconditional madd — always sounds. A silah
                    # (mini waw/yaa) drops at waqf, but ONLY a true silah — which is
                    # always the WORD-FINAL letter (the attached pronoun هُۥ / هِۦ). A
                    # mini-waw mid-word (وَٱلْغَاوُۥنَ → ...و ۥ ن) is a stem long vowel,
                    # not a silah, so it always sounds.
                    silent_ext = (
                        tok[0] in _SILAH_EXTENSIONS and is_word_final and word.is_stopping
                    )
                    flags.append((tok, silent_ext, ""))
                elif i == 0:
                    # The base grapheme (token 0) owns the letter's silent + mark —
                    # but a carrier waw split from its dagger (صَلَوٰة) is a mute seat:
                    # the waw is silent, the split-off dagger carries the madd.
                    flags.append((tok, silent or (carrier_waw and len(tokens) > 1), mark))
                else:
                    flags.append((tok, False, ""))
    return flags
