"""
Per-grapheme silent flags for the Timestamps highlight.

A phoneme is written with several graphemes but only one is pronounced; the rest
are silent (hamza wasl, lam shamsiyah, the otiose tanween alef, an assimilated
noon, …). The Inspector Timestamps tab splits every letter into its own cell and
highlights the cell being uttered — so it needs, per written grapheme, whether
that grapheme is silent (skip it) or sounding (highlight it).

``build_silent_flags`` returns one ``(char, silent)`` pair per written grapheme
(base letters + split extensions) in reading order — the exact order and
tokenization of the bucket TS-shard ``letters[]`` (proven 1:1 against a real
shard). The consumer zips it straight onto the shard letters.

``silent`` is the *linguistic* fact: the grapheme produces no audible phoneme at
its own position in the final (post-redistribution) output. Extensions are never
silent — they carry the madd. Cross-word idgham mergers are reported by their
linguistic silence too; keeping both bridge letters highlighted is a rendering
choice the consumer applies on top (it already owns the bridge tile).

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


def build_silent_flags(mapping: PhonemizationMapping) -> List[Tuple[str, bool]]:
    """``[(char, silent), ...]`` — one per written grapheme, in reading order.

    Base letters carry their sounding/silent fact; extensions (dagger alef,
    maddah, mini waw/yaa) are written madd graphemes and are never silent.
    """
    flags: List[Tuple[str, bool]] = []
    for word in mapping.words:
        for li, lm in enumerate(word.letter_mappings):
            silent = not sounding_in_flat(word, li)
            # Walk base+extensions in textual order, splitting only the
            # standalone extension graphemes; the run carrying the base letter
            # keeps the letter's silent flag, split extensions always sound.
            cur = ""
            base_pending = True  # the run carrying the base letter owns ``silent``
            for ch in get_full_char(lm):
                if ch in _SPLIT_EXTENSIONS:
                    if cur:
                        flags.append((cur, silent if base_pending else False))
                        base_pending = False
                        cur = ""
                    flags.append((ch, False))
                else:
                    cur += ch
            if cur:
                flags.append((cur, silent if base_pending else False))
    return flags
