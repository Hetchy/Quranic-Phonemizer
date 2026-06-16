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
(U+0670) is an unconditional madd and always sounds; the silah (mini waw/yaa,
U+06E5/U+06E6) is a conditional madd that drops at waqf, so it is silent only when
its word stops. Cross-word idgham mergers are reported by their linguistic silence
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
from .letter_phoneme_mapping import TANWEEN_DIACRITICS, get_full_char
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
    ``mark`` the silence-indicating combining mark above it (or ``""``). The run
    carrying the base letter owns the base ``silent`` and ``mark``; the dagger
    alef madd always sounds while the silah drops at waqf.
    """
    flags: List[Tuple[str, bool, str]] = []
    for word in mapping.words:
        for li, lm in enumerate(word.letter_mappings):
            silent = not sounding_in_flat(word, li)
            mark = _silent_mark(lm)
            cur = ""
            base_pending = True  # the run carrying the base letter owns silent+mark
            for ch in get_full_char(lm):
                if ch in _SPLIT_EXTENSIONS:
                    if cur:
                        flags.append((cur, silent if base_pending else False,
                                      mark if base_pending else ""))
                        base_pending = False
                        cur = ""
                    flags.append((ch, ch in _SILAH_EXTENSIONS and word.is_stopping, ""))
                else:
                    cur += ch
            if cur:
                flags.append((cur, silent if base_pending else False,
                              mark if base_pending else ""))
    return flags
