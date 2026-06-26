"""Phoneme-shape predicates — the single source for "what kind of phone is this".

Consumers (the cell builder, the SDK shard annotator, and — via the cell facts —
the inspector) ask THESE functions instead of re-implementing string tests or
re-listing phoneme sets. Two families:

- **Algorithmic** (no data): ``is_madd``, ``is_short_vowel``, ``is_geminate``.
- **YAML-derived** (lazy): ``is_nasalised`` / ``nasalised_phonemes`` (the idgham
  ``nasalized_map``), ``is_render_only`` / ``render_only_phonemes`` (the qalqala
  echo — render-only markers that carry no grapheme and are excluded from the
  flat phoneme index), and ``diacritic_chars`` (the canonical diacritic name→char
  map). These load the phoneme YAML on FIRST CALL only, so importing this module
  (and ``quranic_phonemizer``) triggers no data load.
"""

from __future__ import annotations

from . import phoneme_registry as _reg

# Short vowel phonemes (the canonical owner — letter_phoneme_mapping re-exports).
SHORT_VOWEL_PHONEMES: frozenset[str] = frozenset({"a", "aˤ", "u", "i"})

# Letters that can carry a long vowel (ا و ي ى + the mini-yaa-middle ۧ) — the
# canonical owner (madd re-exports as VOWEL_LETTERS).
VOWEL_CARRIER_CHARS: frozenset[str] = frozenset({"ا", "و", "ي", "ى", "ۧ"})

# Stripped before the geminate doubled-halves test: emphatic, length, ASCII
# length colon, combining nasal tilde — none of which a geminate consonant carries.
_GEMINATE_STRIP = str.maketrans("", "", "ˤː:̃")


def is_madd(ph: str) -> bool:
    """A long vowel (madd) phoneme — carries the length mark ``:``."""
    return ":" in ph


def is_short_vowel(ph: str) -> bool:
    """A short vowel phoneme (``a``/``aˤ``/``u``/``i``)."""
    return ph in SHORT_VOWEL_PHONEMES


def is_geminate(ph: str) -> bool:
    """A doubled (shaddah/idgham) consonant — two identical halves once emphatic /
    length / tilde marks are stripped (``bb``, ``ll``, ``rˤrˤ`` …)."""
    if not ph:
        return False
    base = ph.translate(_GEMINATE_STRIP)
    n = len(base)
    return n >= 2 and n % 2 == 0 and base[: n // 2] == base[n // 2:]


# --- lazy YAML-derived sets --------------------------------------------------

_NASAL: frozenset[str] | None = None
_RENDER_ONLY: frozenset[str] | None = None
_DIAC_CHARS: dict[str, str] | None = None


def nasalised_phonemes() -> frozenset[str]:
    """The nasalised merger phonemes (idgham ``nasalized_map`` values: ñ m̃ j̃ w̃)."""
    global _NASAL
    if _NASAL is None:
        nmap = _reg.get_rule_section("idgham").get("nasalized_map", {}) or {}
        _NASAL = frozenset(v for v in nmap.values() if v)
    return _NASAL


def is_nasalised(ph: str) -> bool:
    """A nasalised merger phoneme (ñ m̃ j̃ w̃)."""
    return ph in nasalised_phonemes()


def render_only_phonemes() -> frozenset[str]:
    """Render-only markers an aligner may store that are NOT letter-derived and so
    are excluded from the flat phoneme index — the qalqala echo (``Q``). Derived
    from the ``qalqala`` YAML section, so it tracks the data (e.g. a future ``QQ``)
    instead of being hardcoded in every consumer."""
    global _RENDER_ONLY
    if _RENDER_ONLY is None:
        _RENDER_ONLY = frozenset(
            v for v in _reg.get_rule_section("qalqala").values() if v
        )
    return _RENDER_ONLY


def is_render_only(ph: str) -> bool:
    """True for a render-only marker (the qalqala echo) — see ``render_only_phonemes``."""
    return ph in render_only_phonemes()


def diacritic_chars() -> dict[str, str]:
    """Canonical diacritic name → Unicode char (FATHA→ َ …), from the phoneme YAML."""
    global _DIAC_CHARS
    if _DIAC_CHARS is None:
        _DIAC_CHARS = dict(_reg.get_diacritic_chars())
    return _DIAC_CHARS
