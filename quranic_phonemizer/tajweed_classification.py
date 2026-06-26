"""Cross-word tajweed merger classification + the single cross-word detector.

This is the **one** place that answers "which tajweed rules behave how across a
word boundary" and "where does a cross-word merger fire in a mapping". Everything
that used to hand-maintain a subset of these rule names — the SDK's ``BRIDGE_RULES``
/ ``_MERGER_ON_PREV``, the cell builder's ``_IDGHAM_SOURCE_TAGS`` /
``_CROSS_WORD_BASE_MERGE_RULES``, the flat letter-mapping's ``CROSS_WORD_*`` sets,
the FE's assimilating-tanwīn set — derives from the single ``CROSS_WORD_MERGERS``
registry here.

A rule's cross-word behaviour has several **orthogonal** axes, deliberately kept
separate (collapsing them is what made the copies drift):

- ``bridge`` — produces a co-light merger phoneme an aligner should tag as a
  cross-word bridge tile (the 8 idgham mergers). ikhfaa/iqlab are cross-word but
  non-merging, so ``bridge=False``.
- ``side`` — where the merger phoneme sits: ``"prev"`` (the prev word's tail —
  idgham shafawi only) or ``"curr"`` (the curr word's head — every other merger).
- ``both_sound`` — both boundary letters voice (idgham shafawi).
- ``tanween_assimilates`` — a tanwīn whose nūn-sound assimilates into the next
  word, so a renderer draws the *open* tanwīn form rather than the stacked one.
- ``flat_attr`` — the flat letter-mapping re-attribution class
  (``"merge"`` / ``"both"`` / ``"non_merge"``). This is a DIFFERENT question from
  ``bridge``: the two ``idgham_*_tanween`` rules are ``bridge=True`` *and*
  ``flat_attr="non_merge"`` at once. Keeping them as separate columns preserves
  both historical answers.

The cell role/status string vocabulary lives here too (as ``str``-mixed enums so
JSON serialisation is byte-identical to the former bare strings).

Imports only ``tajweed_rule`` + the stdlib — no YAML, no mapping — so importing
this module is cheap and triggers no data load.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .tajweed_rule import TajweedRule


# =============================================================================
# Cell vocabulary (str-mixed enums — values byte-identical to the former consts)
# =============================================================================

class CellRole(str, Enum):
    """The per-character cell roles emitted by ``character_phoneme_mappings``."""
    BASE = "base"        # consonant / consonantal vowel-letter / hamza / hamza-wasl
    HARAKA = "haraka"    # fatha / damma / kasra / sukun
    TANWEEN = "tanween"  # fathatan / dammatan / kasratan
    MADD = "madd"        # long-vowel carrier: ا و ي ى, mini ۥ ۦ ۧ, dagger-alef ٰ

    __str__ = str.__str__  # str()/f-string yield the value, not "CellRole.BASE"


class CellStatus(str, Enum):
    """The per-character cell statuses."""
    PRESENT = "present"      # explicit, sounded
    INSERTED = "inserted"    # implicit, no source char
    DROPPED = "dropped"      # source char present but silent in this context
    REPLACED = "replaced"    # sound changed from the written form (madd-iwad)
    SHORTENED = "shortened"  # long vowel reduced; carrier silenced (iltiqaa)

    __str__ = str.__str__


# =============================================================================
# Cross-word merger classification
# =============================================================================

@dataclass(frozen=True)
class MergerClass:
    """How one tajweed rule behaves across a word boundary (see module docstring)."""
    bridge: bool
    side: str  # "prev" | "curr"
    both_sound: bool
    tanween_assimilates: bool
    flat_attr: str  # "merge" | "both" | "non_merge"
    # The merger co-lights both graphemes (source ↔ receiver share a group, so the
    # silent source un-greys + lights through the merger). True for the noon/tanwīn
    # idghams, shafawi, and — among the consonant idghams — ONLY mutamāthilayn;
    # mutaqāribayn / mutajānisayn are tagged (underline + tooltip) but NOT co-lit, so
    # their source stays silent.
    co_light: bool = False


# One entry per cross-word-capable rule. The single source the derived views and
# the detector read from.
CROSS_WORD_MERGERS: dict[TajweedRule, MergerClass] = {
    # --- bridges: noon idgham (merger on curr head) ---
    TajweedRule.IDGHAM_GHUNNAH_NOON:
        MergerClass(bridge=True, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="merge", co_light=True),
    TajweedRule.IDGHAM_BILA_GHUNNAH_NOON:
        MergerClass(bridge=True, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="merge", co_light=True),
    TajweedRule.IDGHAM_MUTAMATHILAYN:
        MergerClass(bridge=True, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="merge", co_light=True),
    TajweedRule.IDGHAM_MUTAQARIBAYN:
        MergerClass(bridge=True, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="merge"),
    TajweedRule.IDGHAM_MUTAJANISAYN_KAMIL:
        MergerClass(bridge=True, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="merge"),
    # --- bridge: shafawi (merger on prev tail, both letters sound) ---
    TajweedRule.IDGHAM_SHAFAWI:
        MergerClass(bridge=True, side="prev", both_sound=True, tanween_assimilates=False, flat_attr="both", co_light=True),
    # --- bridges: tanwīn idgham (merger on curr head, tanwīn assimilates) ---
    TajweedRule.IDGHAM_GHUNNAH_TANWEEN:
        MergerClass(bridge=True, side="curr", both_sound=False, tanween_assimilates=True, flat_attr="non_merge", co_light=True),
    TajweedRule.IDGHAM_BILA_GHUNNAH_TANWEEN:
        MergerClass(bridge=True, side="curr", both_sound=False, tanween_assimilates=True, flat_attr="non_merge", co_light=True),
    # --- non-bridges: ikhfaa / iqlab (cross-word but non-merging) ---
    TajweedRule.IKHFAA_TANWEEN:
        MergerClass(bridge=False, side="curr", both_sound=False, tanween_assimilates=True, flat_attr="non_merge"),
    TajweedRule.IKHFAA_NOON:
        MergerClass(bridge=False, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="non_merge"),
    TajweedRule.IQLAB_NOON:
        MergerClass(bridge=False, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="non_merge"),
    TajweedRule.IQLAB_TANWEEN:
        MergerClass(bridge=False, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="non_merge"),
    TajweedRule.IKHFAA_SHAFAWI:
        MergerClass(bridge=False, side="curr", both_sound=False, tanween_assimilates=False, flat_attr="non_merge"),
}


# --- derived views (computed once) -------------------------------------------

# The 8 cross-word merger rules an aligner tags as a bridge phone.
BRIDGE_RULE_VALUES: frozenset[str] = frozenset(
    r.value for r, m in CROSS_WORD_MERGERS.items() if m.bridge
)

# The lone rule whose merger sits at the PREV word's tail.
MERGER_ON_PREV_VALUES: frozenset[str] = frozenset(
    r.value for r, m in CROSS_WORD_MERGERS.items() if m.side == "prev"
)

# Both-letters-sound mergers (a consonant idgham whose two base graphemes co-light).
BOTH_SOUND_VALUES: frozenset[str] = frozenset(
    r.value for r, m in CROSS_WORD_MERGERS.items() if m.both_sound
)

# Idghams whose SOURCE cell is found by its tag in `_link_cross_word` to co-light
# with the receiver (curr-head mergers): the noon/tanwīn idghams + mutamāthilayn.
# Shafawi co-lights too but via the `both_sound` branch (prev-tail), so it's excluded
# here. mutaqāribayn/mutajānisayn are NOT co-lit (`co_light=False`) — tagged only.
IDGHAM_SOURCE_TAG_VALUES: frozenset[str] = frozenset(
    r.value for r, m in CROSS_WORD_MERGERS.items() if m.co_light and not m.both_sound
)

# Tanwīn rules whose nūn-sound assimilates → a renderer draws the open tanwīn form.
TANWEEN_ASSIMILATES_VALUES: frozenset[str] = frozenset(
    r.value for r, m in CROSS_WORD_MERGERS.items() if m.tanween_assimilates
)

# Flat letter-mapping re-attribution views (consumed by letter_phoneme_mapping).
CROSS_WORD_MERGE_RULES: frozenset[TajweedRule] = frozenset(
    r for r, m in CROSS_WORD_MERGERS.items() if m.flat_attr == "merge"
)
CROSS_WORD_BOTH_MERGE_RULES: frozenset[TajweedRule] = frozenset(
    r for r, m in CROSS_WORD_MERGERS.items() if m.flat_attr == "both"
)
CROSS_WORD_NON_MERGE_RULES: frozenset[TajweedRule] = frozenset(
    r for r, m in CROSS_WORD_MERGERS.items() if m.flat_attr == "non_merge"
)

# Ordered tag-priority tuples for picking a single tanwīn / noon rule tag on a
# cell (a letter carries at most one, so the order is only a deterministic
# tie-break). Owned here so they are not re-listed at the call site.
TANWEEN_RULE_TAGS: tuple[str, ...] = (
    "iqlab_tanween", "ikhfaa_tanween",
    "idgham_ghunnah_tanween", "idgham_bila_ghunnah_tanween",
)
NOON_RULE_TAGS: tuple[str, ...] = (
    "iqlab_noon", "ikhfaa_noon",
    "idgham_ghunnah_noon", "idgham_bila_ghunnah_noon",
)
# Base-cell rules carried as a SOURCE on the letter itself (not a noon/tanwīn rule
# routed to a diacritic): plain ghunnah on a mushaddad nūn/mīm, and the two meem-
# sākin shafawi rules. ``idgham_shafawi`` also co-lights cross-word via
# ``_link_cross_word`` (which assigns the share_group); this tuple supplies its
# missing cell tag on the source mīm.
GHUNNAH_BASE_TAGS: tuple[str, ...] = (
    "noon_ghunnah", "meem_ghunnah", "ikhfaa_shafawi", "idgham_shafawi",
)
# Consonant idgham source rules carried on the source letter cell itself. The
# fully-merged (silent) sources route through ``_silent_cell_tag``; this tuple
# supplies the cell tag for the one whose source SOUNDS — mutajānisayn nāqiṣ — so it
# still underlines + names the rule.
CONSONANT_IDGHAM_RULE_TAGS: tuple[str, ...] = (
    "idgham_mutamathilayn", "idgham_mutaqaribayn",
    "idgham_mutajanisayn_kamil", "idgham_mutajanisayn_naqis",
)


# =============================================================================
# The single cross-word merger detector
# =============================================================================

@dataclass(frozen=True)
class CrossWordMerger:
    """One detected cross-word merger boundary in a mapping."""
    prev_word_index: int
    curr_word_index: int
    rule: str
    side: str          # "prev" | "curr"
    both_sound: bool


def detect_cross_word_mergers(mapping) -> list[CrossWordMerger]:
    """Return every cross-word *bridge* merger in a ``PhonemizationMapping``.

    A boundary fires when any source rule on the prev word (scanned END-TO-FRONT,
    so a tanwīn's source on its carrying consonant is found) matches a target rule
    on the curr word's FIRST letter and is one of the 8 ``bridge`` rules. The
    first matching rule wins (``sorted(...)[0]`` tie-break — at most one fires in
    practice). The lone cell builder + the SDK shard bridge tagger both consume
    this, so "where does idgham fire" is implemented exactly once.
    """
    out: list[CrossWordMerger] = []
    words = mapping.words
    for i in range(len(words) - 1):
        prev, curr = words[i], words[i + 1]
        if not prev.letter_mappings or not curr.letter_mappings:
            continue
        curr_targets = {
            t.rule.value for t in curr.letter_mappings[0].tajweed_rules if not t.is_source
        }
        rule = None
        for e in reversed(prev.letter_mappings):
            srcs = {t.rule.value for t in e.tajweed_rules if t.is_source}
            cross = (srcs & curr_targets) & BRIDGE_RULE_VALUES
            if cross:
                rule = sorted(cross)[0]
                break
        if rule is None:
            continue
        mc = CROSS_WORD_MERGERS[TajweedRule(rule)]
        out.append(CrossWordMerger(
            prev_word_index=i, curr_word_index=i + 1,
            rule=rule, side=mc.side, both_sound=mc.both_sound,
        ))
    return out
