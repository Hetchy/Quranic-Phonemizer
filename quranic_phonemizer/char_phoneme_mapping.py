"""
Character-level phoneme mapping (haraka / tanween cells).

Where ``letter_phoneme_mappings`` aligns one entry per *letter*, this maps one
**cell per written character** — base letter, every haraka / tanween, the long-vowel
carrier — plus the rule-inserted *implicit* units (hamza-waṣl connecting vowel,
iltiqāʾ kasra, the Allah dagger-alef, the madd-ʿiwaḍ alef). A downstream forced
aligner's per-phoneme timestamps then drive per-diacritic cell highlighting.

The output is **canonical domain knowledge only** — roles, statuses, tajweed rule
tags, and phoneme indices. No script/visual details (mini-meem glyphs, open/closed
tanween forms, above/below placement, dotted-circle bases) are baked here; a consumer
(e.g. the Inspector) derives all of that from the rule ``tag`` + the diacritic char.

Each cell carries ``phoneme_indices`` — **word-local** indices into the word's phoneme
sequence (``word.phonemes`` order, == the order a forced aligner's per-word phones
follow). They are taken from the **raw per-letter walk** (the same walk
``Phonemizer._build_alignment`` and ``madd.build_madd_mappings`` use), never a
redistributed view: iltiqāʾ demotion and waqf-tanween redistribution change which
*cell displays* a phoneme, never the phoneme's index. An index referenced by more than
one cell is always an intentional shared-timing group (long vowel: haraka + carrier).

This module is purely additive — it reads ``get_mapping()`` read-only and changes
nothing about the letter-phoneme, silent, or tajweed outputs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .mapping import PhonemizationMapping, WordMapping, LetterMapping
from .letter_phoneme_mapping import (
    should_split_extension,
    is_madd_phoneme,
    get_full_char,
    get_merge_info,
    TANWEEN_DIACRITICS,
    SHORT_VOWEL_PHONEMES,
)
from .silent import sounding_in_flat, _is_carrier_waw
from .specials import get_tajweed_mapping
from .tajweed_classification import (
    CellRole,
    CellStatus,
    TANWEEN_RULE_TAGS,
    NOON_RULE_TAGS,
    GHUNNAH_BASE_TAGS,
    IDGHAM_SOURCE_TAG_VALUES,
    detect_cross_word_mergers,
)
from .phonemes import (
    VOWEL_CARRIER_CHARS,
    diacritic_chars,
    is_geminate,
    is_madd,
    is_nasalised,
    is_render_only,
    is_short_vowel,
)
from .tajweed_mapping import HEAVY_VOWEL_PHONEMES

# Shaddah (gemination mark) — composed onto a geminated base cell's chars so a
# renderer reads it from the canonical text instead of inferring it from the
# phoneme shape.
SHADDA = "ّ"  # U+0651

# Pronoun-haa ṣilah extensions (mini-waw ۥ / mini-yaa ۦ). At wasl these carry a
# long vowel and split into their own madd cell (should_split_extension); at waqf
# the ṣilah drops, so the extension produces no phoneme and would otherwise stay
# glued onto the haa base char — B2 splits it into a silent dropped madd cell.
SILAH_EXTENSION_NAMES = frozenset({"MINI_WAW", "MINI_YA_END"})

# Iqlab tanwīn split — the doubled tanwīn sounds [short-vowel, nasal mīm]. B1
# decomposes it into a plain haraka (the short vowel) + a mini-meem cell (the
# nasal), the meem glyph mirroring the renderer's IQLAB_FORM: a small high meem
# (U+06E2) above a fatḥa/ḍamma, a small low meem (U+06ED) below a kasra.
MEEM_HI = "ۢ"  # U+06E2 ARABIC SMALL HIGH MEEM ISOLATED FORM
MEEM_LO = "ۭ"  # U+06ED ARABIC SMALL LOW MEEM
IQLAB_MINI_MEEM = {"FATHATAN": MEEM_HI, "DAMMATAN": MEEM_HI, "KASRATAN": MEEM_LO}
# The bare short-vowel mark a doubled tanwīn decomposes to (fatḥatan→fatḥa, …).
IQLAB_SHORT_VOWEL = {"FATHATAN": "َ", "DAMMATAN": "ُ", "KASRATAN": "ِ"}

# Madd rule tag values (the muqaṭṭaʿāt YAML uses these enum strings verbatim as
# source_rules; the FE colours madd_lazim/wajib/jaiz/arid/leen, ṭabīʿī uncoloured).
MADD_RULE_TAGS = frozenset({
    "madd_tabii", "madd_lazim", "madd_arid_lissukun", "madd_leen",
    "madd_wajib_muttasil", "madd_jaiz_munfasil",
})
# Per-phoneme rule families for the muqaṭṭaʿ phoneme_rule_tags walk. A nasal-rule
# lands on the name's nasal phone (the merged m̃ of لَآم's idgham-shafawi, the ŋ of
# عَيْن's ikhfaa); a madd-rule lands on the long-vowel (or the leen glide when the
# name has no long vowel — عَيْن's يْ glide). The nasal rules are the noon + ghunnah
# tag tuples; the merger SOURCE side (the لَآم closing م that merged away) leaves no
# phone on its own letter, so the receiving مّيٓم letter's nasal carries the tag via
# its target_rules.
GLIDE_PHONEMES = frozenset({"j", "w"})

# Qalqala tier order for a base cell: kubra (at waqf / a final sākin) wins over
# sughra (mid-word). Picked from the letter's OWN source rules — a qalqala letter
# carries exactly one of these — so the cell names the precise variant instead of
# the bare "qalqala". Both stay uncoloured downstream (name-only).
QALQALA_RULE_ORDER = ("qalqala_kubra", "qalqala_sughra")


# =============================================================================
# Vocabulary — short aliases to the canonical enums (str values unchanged, so
# the serialized cell rows are byte-identical). The diacritic name→char map,
# the vowel-carrier set, the render-only marker set, and the tanwīn/noon rule
# tag tuples now come from phonemes / tajweed_classification (single owners).
# =============================================================================

# Roles
BASE = CellRole.BASE          # consonant / consonantal vowel-letter / hamza / hamza-wasl
HARAKA = CellRole.HARAKA      # fatha / damma / kasra / sukun
TANWEEN = CellRole.TANWEEN    # fathatan / dammatan / kasratan
MADD = CellRole.MADD          # long-vowel carrier: ا و ي ى, mini ۥ ۦ ۧ, dagger-alef ٰ

# Statuses
PRESENT = CellStatus.PRESENT
INSERTED = CellStatus.INSERTED
DROPPED = CellStatus.DROPPED
REPLACED = CellStatus.REPLACED
SHORTENED = CellStatus.SHORTENED


# =============================================================================
# Data classes
# =============================================================================

@dataclass
class Cell:
    """One written-character (or implicit) cell.

    ``phoneme_indices`` are **word-local** indices into the word's phoneme
    sequence; ``[]`` means the cell is silent in this context.

    ``phoneme_rule_tags`` is an OPTIONAL list parallel to ``phoneme_indices``
    (same length), each entry a per-phoneme tajweed tag or ``None``. It is set
    only on muqaṭṭaʿāt letter cells, whose single bare-letter grapheme sounds out
    a multi-letter name carrying several distinct rules (the merged nasal, the
    long-vowel madd, the leen glide, the qalqala echo). When empty, a consumer
    falls back to the cell's single ``tag``.

    ``secondary_tags`` holds extra rules that co-occur on this grapheme but lose
    the single-``tag`` priority pick — in practice ``["tafkheem"]`` on a heavy
    madd carrier or qalqala letter, where ``tag`` is the madd/qalqala rule. A
    consumer renders them as additional badges stacked on the primary ``tag``."""
    chars: str
    role: str
    status: str
    phonemes: List[str] = field(default_factory=list)
    phoneme_indices: List[int] = field(default_factory=list)
    tag: Optional[str] = None
    share_group: Optional[int] = None
    source_letter_index: int = -1
    source_letter_indices: List[int] = field(default_factory=list)
    phoneme_rule_tags: List[Optional[str]] = field(default_factory=list)
    secondary_tags: List[str] = field(default_factory=list)

    def to_list(self) -> list:
        """Full dump (incl. ``phonemes`` + ``source_letter_indices`` +
        ``phoneme_rule_tags``). This is the phonemizer's own serialization — NOT
        the Timestamps shard row, which a downstream consumer (the SDK) projects
        in a different field order; do not conflate the two positionally.
        ``phoneme_rule_tags`` then ``secondary_tags`` are appended last (additive
        slots) so a reader of an older row tolerates their absence."""
        return [
            self.chars, self.role, self.status,
            list(self.phonemes), list(self.phoneme_indices),
            self.tag, self.share_group,
            self.source_letter_index, list(self.source_letter_indices),
            list(self.phoneme_rule_tags), list(self.secondary_tags),
        ]

    def to_dict(self) -> dict:
        return {
            "chars": self.chars,
            "role": self.role,
            "status": self.status,
            "phonemes": list(self.phonemes),
            "phoneme_indices": list(self.phoneme_indices),
            "tag": self.tag,
            "share_group": self.share_group,
            "source_letter_index": self.source_letter_index,
            "source_letter_indices": list(self.source_letter_indices),
            "phoneme_rule_tags": list(self.phoneme_rule_tags),
            "secondary_tags": list(self.secondary_tags),
        }


@dataclass
class CharWord:
    location: str
    text: str
    is_starting: bool
    is_stopping: bool
    cells: List[Cell] = field(default_factory=list)


# =============================================================================
# Per-letter helpers
# =============================================================================

def _source_rules(lm: LetterMapping) -> set:
    return {t.rule.value for t in lm.tajweed_rules if t.is_source}


# Flat-builder reasons (get_merge_info) that name a true no-rule silence gap — the
# letter went silent with no recognised tajweed rule. These map to a single literal
# ``silent_unclassified`` so a consumer can surface "we couldn't classify this".
_SILENT_GAP_REASONS = frozenset({
    "idgham_unknown", "vowel_lengthening_failure", "unknown_silent",
})


def _silent_cell_tag(lm: LetterMapping, word: WordMapping, li: int) -> Optional[str]:
    """Source silence rule for a raw-silent letter cell (no phoneme at its slot).

    Classified by the SAME flat-builder ``get_merge_info`` the silent-flags path
    uses, so the cell names exactly why the grapheme went mute:

      - idgham-source silence (noon/meem merging into the next letter), lam_shamsiyah,
        hamza_wasl_silent, silent_iltiqaa_sakinayn → the rule's own value (meaningful,
        recoverable),
      - the ``vowel_silent`` catch-all → ``vowel_silent`` (kept whole — sub-reasons
        not split),
      - a true no-rule gap (idgham_unknown / vowel_lengthening_failure / unknown_silent)
        → the literal ``silent_unclassified``.

    Returns ``None`` for a mundane silence the caller leaves generic (a waqf sukun /
    silah-drop never reaches here; this path is only the silent BASE letter cell)."""
    reason = get_merge_info(lm, word, li).rule
    if not reason:
        return None
    if reason in _SILENT_GAP_REASONS:
        return "silent_unclassified"
    return reason


def _dropped_silah_chars(lm: LetterMapping, word: WordMapping) -> Optional[str]:
    """The mini-waw/mini-yaa ṣilah glyph on a pronoun-haa whose ṣilah dropped at
    waqf (so ``should_split_extension`` finds no madd phoneme to split out). Returns
    the extension chars when the word is stopping and the ṣilah produced no madd
    phoneme on this letter, else None — the wasl case keeps going through the normal
    extension split."""
    if not word.is_stopping:
        return None
    if any(is_madd_phoneme(ph) for ph in lm.phonemes):
        return None
    silah = [ext for ext in lm.extensions
             if ext.char and ext.name in SILAH_EXTENSION_NAMES]
    if not silah:
        return None
    return "".join(ext.char for ext in silah)


def _pick_tag(rules: set, order: Tuple[str, ...]) -> Optional[str]:
    for r in order:
        if r in rules:
            return r
    return None


def _letter_pairs(word: WordMapping) -> List[List[Tuple[int, str]]]:
    """Per-letter list of (word_local_phoneme_index, phoneme) — the RAW walk."""
    out: List[List[Tuple[int, str]]] = []
    idx = 0
    for lm in word.letter_mappings:
        pairs = [(idx + j, p) for j, p in enumerate(lm.phonemes)]
        idx += len(lm.phonemes)
        out.append(pairs)
    return out


def _lafdh_jalalah_indices(word: WordMapping) -> set:
    """Word-local phoneme indices that are the implicit Allah dagger-alef madd."""
    return {mm.phoneme_index for mm in word.madd_mappings
            if mm.is_lafdh_jalalah and mm.phoneme_index >= 0}


def _madd_type_indices(word: WordMapping) -> Dict[int, str]:
    """Word-local phoneme index -> ``madd_<type>`` tag for every madd, classified
    or ṭabīʿī (wajib_muttasil / jaiz_munfasil / lazim / arid_lissukun / leen, else
    plain ``madd_tabii``).

    A ``madd_type is None`` entry is a regular ṭabīʿī madd and maps to
    ``madd_tabii`` (uncoloured downstream, name-only) — EXCEPT the implicit Allah
    dagger-alef (``is_lafdh_jalalah``), which keeps its own ``allah_dagger_alef``
    tag (resolved at the call site) and so is excluded here. Implicit-only entries
    (``phoneme_index < 0``) are skipped. The carrier cell reads its own phoneme
    index from this map; the paired haraka is never tagged (a madd colours only the
    carrier grapheme)."""
    out: Dict[int, str] = {}
    for mm in word.madd_mappings:
        if mm.phoneme_index < 0:
            continue
        mtype = getattr(mm, "madd_type", None)
        if mtype:
            out[mm.phoneme_index] = f"madd_{mtype}"
        elif not mm.is_lafdh_jalalah:
            out[mm.phoneme_index] = "madd_tabii"
    return out


# =============================================================================
# Builder
# =============================================================================

def _special_subword_rules(subword: dict) -> Tuple[set, set]:
    """(source_rules, target_rules) flattened across a muqaṭṭaʿ name's entries.
    Both sides matter for the per-phoneme walk: a cross-letter idgham's SOURCE م
    (the لَآم tail that merged away) leaves no phone on its own letter, so the
    receiving name's nasal carries the rule via its ``target_rules``."""
    src: set = set()
    tgt: set = set()
    for e in subword.get("entries", []):
        src.update(e.get("source_rules", []))
        tgt.update(e.get("target_rules", []))
    return src, tgt


def _special_madd_tag(rules: set) -> Optional[str]:
    """The name's madd subtype (madd_lazim / madd_tabii …) — the muqaṭṭaʿ cell's
    headline ``tag``. عَيْن's leen is named with a madd_lazim, so even a name with
    no long-vowel phone reports its madd here (the cell underlines as madd)."""
    return next((r for r in rules if r in MADD_RULE_TAGS), None)


def _special_phoneme_tags(subword: dict, lp: List[Tuple[int, str]]) -> List[Optional[str]]:
    """Per-phoneme tags for ONE muqaṭṭaʿ letter, parallel to ``lp`` (its
    (index, phoneme) pairs). The name's rules are placed on the phone each
    concerns, identified by phone shape within this single letter (each relevant
    shape occurs at most once per name part):

      - the merged/ikhfaa nasal (m̃ ñ ŋ …) gets the idgham/ikhfaa/ghunnah rule,
      - the long-vowel madd phone gets the madd rule; a name with no long vowel
        but a leen glide (عَيْن's يْ → j) puts the madd on the glide,
      - the qalqala consonant AND its render-only Q echo get qalqala_kubra,
      - every other phone is None.

    madd_tabii / qalqala / tafkheem ride through here even though the FE palette
    leaves them uncoloured (a faithful renderer keys the colour, not this list)."""
    src, tgt = _special_subword_rules(subword)
    rules = src | tgt
    madd_tag = _special_madd_tag(rules)
    nasal_tag = _pick_tag(rules, NOON_RULE_TAGS + GHUNNAH_BASE_TAGS)
    has_qalqala = "qalqala_kubra" in rules
    has_long_vowel = any(is_madd(ph) for _, ph in lp)

    # The nasal rule lands on exactly ONE phone — the merger/ikhfaa target. Prefer
    # a nasalised phone (the idgham m̃), else the first plain nasal (the ikhfaa ŋ);
    # the name's other meem (مّيٓم's trailing م) is untouched.
    nasal_pos = -1
    if nasal_tag:
        nasal_pos = next((k for k, (_, ph) in enumerate(lp) if is_nasalised(ph)), -1)
        if nasal_pos < 0:
            nasal_pos = next(
                (k for k, (_, ph) in enumerate(lp) if ph in {"ŋ", "n", "m"}), -1)

    tags: List[Optional[str]] = []
    for k, (_, ph) in enumerate(lp):
        if has_qalqala and is_render_only(ph):
            tags.append("qalqala_kubra")
        elif nasal_tag and k == nasal_pos:
            tags.append(nasal_tag)
        elif madd_tag and is_madd(ph):
            tags.append(madd_tag)
        elif madd_tag and not has_long_vowel and ph in GLIDE_PHONEMES:
            tags.append(madd_tag)  # leen glide (عَيْن يْ → j)
        else:
            tags.append(None)

    # The qalqala consonant (the phone right before the Q echo) co-carries the rule
    # so a renderer underlines the dāl/qāf itself, not just the silent echo.
    if has_qalqala:
        for k in range(1, len(lp)):
            if is_render_only(lp[k][1]) and tags[k - 1] is None:
                tags[k - 1] = "qalqala_kubra"
    return tags


def _special_word_cells(word: WordMapping) -> List[Cell]:
    """Muqaṭṭaʿāt / hardcoded words: one cell per sounding letter. A spelled-out name
    renders as its single bare-letter grapheme (لام is one ل glyph, not ل+phantom-alef),
    so each letter stays ONE cell. The cell's headline ``tag`` is the name's LETTER-tier
    madd (madd_lazim نُوٓنْ / لَآم, madd_tabii هَا, عَيْن's leen → madd_lazim); the new
    ``phoneme_rule_tags`` then carries the finer per-phone rules the bare-letter cell
    would otherwise smear — the merged nasal's idgham_shafawi, the ikhfaa nasal's
    ikhfaa_noon, the long vowel / leen glide's madd, the dāl/Q qalqala. Both come from
    the grapheme-aligned YAML ``tajweed_mapping`` (the same source ``tajweed_mappings()``
    trusts). A name with neither madd nor nasal (the أَلِفْ head of الٓم) stays an
    untagged BASE cell."""
    cells: List[Cell] = []
    pairs = _letter_pairs(word)
    subwords = get_tajweed_mapping(word.location) or []
    sub_i = 0
    for li, lm in enumerate(word.letter_mappings):
        lp = pairs[li]
        if not lp:
            continue  # inert (e.g. trailing stop-sign entry " ۚ")
        subword = subwords[sub_i] if sub_i < len(subwords) else {}
        sub_i += 1

        rule_tags = _special_phoneme_tags(subword, lp)
        src, tgt = _special_subword_rules(subword)
        madd_tag = _special_madd_tag(src | tgt)
        # A named madd (every letter but the bare أَلِفْ head) underlines + groups
        # as MADD; only a rule-free head stays a plain BASE cell.
        role = MADD if madd_tag else BASE
        cells.append(Cell(
            chars=get_full_char(lm), role=role, status=PRESENT,
            phonemes=[p for _, p in lp], phoneme_indices=[i for i, _ in lp],
            tag=madd_tag, source_letter_index=li, source_letter_indices=[li],
            phoneme_rule_tags=rule_tags,
        ))
    return cells


def _word_cells(word: WordMapping) -> List[Cell]:
    pairs = _letter_pairs(word)
    n_letters = len(word.letter_mappings)
    lafdh_idx = _lafdh_jalalah_indices(word)
    madd_types = _madd_type_indices(word)

    cells: List[Cell] = []
    # Routed-to-next-letter state, keyed by the *target* letter index.
    force_dropped: set = set()              # iltiqaa: vowel letter silenced
    force_madd_iwad: Dict[int, Tuple[int, str]] = {}  # li -> (index, phoneme) of the a:

    for li in range(n_letters):
        lm = word.letter_mappings[li]
        lp = pairs[li]
        diac = lm.diacritic
        rules = _source_rules(lm)
        full = get_full_char(lm)

        # ---- a letter that was routed into by a previous letter --------------
        if li in force_madd_iwad:
            idx, ph = force_madd_iwad[li]
            cells.append(Cell(
                chars=full, role=MADD, status=REPLACED,
                phonemes=[ph], phoneme_indices=[idx], tag="madd_iwad",
                source_letter_index=li, source_letter_indices=[li],
            ))
            continue
        if li in force_dropped:
            cells.append(Cell(
                chars=full, role=MADD, status=SHORTENED,
                phonemes=[], phoneme_indices=[], tag="iltiqaa",
                source_letter_index=li, source_letter_indices=[li],
            ))
            continue

        # ---- split into consonant / modifier --------------------------------
        # A letter may be raw-silent (lp empty) yet still carry a diacritic — e.g.
        # an idgham-shafawi meem whose consonant merged cross-word AND whose vowel
        # lengthened onto the next letter (مَّا). Such a letter flows through here
        # so its diacritic still gets a cell (absorbed into the following madd).
        if diac is not None or lm.has_shaddah:
            cons_pairs, mod_pairs = lp[:1], lp[1:]
        else:
            cons_pairs, mod_pairs = lp, []

        # Qalqala echo always rides the base cell.
        q_pairs = [p for p in mod_pairs if is_render_only(p[1])]
        mod_pairs = [p for p in mod_pairs if not is_render_only(p[1])]

        # Extension split (dagger-alef / mini-waw / mini-yaa carrying a long vowel
        # on the SAME letter): the madd phoneme moves to its own MADD cell.
        split = should_split_extension(lm, word)
        # A silent carrier-waw seat (صَلَوٰة, زَكَوٰة): should_split_extension suppresses
        # the split as a vowel-letter-all-madd carrier, but the shard tokenizes the
        # dagger-alef as its own grapheme and flags the waw silent (silent.py). Force
        # the same split at the cell tier so the waw greys and the dagger carries the
        # madd, instead of merging into one وٰ carrier cell.
        if not split and _is_carrier_waw(lm):
            dagger = "".join(ext.char for ext in lm.extensions
                             if ext.name == "DAGGER_ALEF" and ext.char)
            madd_ph = next((p for p in reversed(lm.phonemes) if is_madd_phoneme(p)), None)
            if dagger and madd_ph is not None:
                split = (dagger, madd_ph)
        madd_pair = None
        madd_chars = None
        if split:
            madd_chars, _ = split
            # last madd phoneme among this letter's (non-Q) pairs
            for p in reversed(cons_pairs + mod_pairs):
                if is_madd_phoneme(p[1]):
                    madd_pair = p
                    break
            if madd_pair is not None:
                if madd_pair in mod_pairs:
                    mod_pairs = [p for p in mod_pairs if p != madd_pair]
                elif madd_pair in cons_pairs:
                    cons_pairs = [p for p in cons_pairs if p != madd_pair]
            base_chars = full.replace(madd_chars, "", 1)
        else:
            base_chars = full

        # Dropped pronoun-haa ṣilah at waqf: the mini-waw/yaa carried a long vowel
        # at wasl but the ṣilah dropped at the stop, so should_split_extension found
        # no madd phoneme and the glyph would stay glued onto the haa base. Strip it
        # off the base and remember it — a silent dropped MADD cell is emitted below.
        dropped_silah_chars = None
        if not split:
            dropped_silah_chars = _dropped_silah_chars(lm, word)
            if dropped_silah_chars:
                base_chars = base_chars.replace(dropped_silah_chars, "", 1)

        base_pairs = cons_pairs + q_pairs

        # Implicit Allah dagger-alef: a madd in mod with no grapheme.
        allah_pair = None
        if not split:
            for p in list(mod_pairs):
                if p[0] in lafdh_idx and is_madd_phoneme(p[1]):
                    allah_pair = p
                    mod_pairs = [q for q in mod_pairs if q != p]
                    break

        # ---- emit the letter-sound cell (BASE or MADD) ----------------------
        base_is_vowel_carrier = (
            diac is None and not lm.has_shaddah and lm.char in VOWEL_CARRIER_CHARS
            and all(is_madd_phoneme(p[1]) for p in base_pairs) and base_pairs
        )
        # Waqf consonant→vowel carrier: a word-final و/ى lengthened from the
        # preceding haraka (هُوَ / هِىَ / نِعْمَتِىَ). Its OWN written diacritic
        # (the trailing fatḥa) is dropped at the stop, so it never qualifies as a
        # plain vowel carrier (which requires diac is None), yet its base phoneme
        # is the long vowel. Promote it to a madd carrier so the FE groups it with
        # the stolen ḍamma/kasra (share_group already forms); the trailing fatḥa
        # falls out as a separate dropped haraka cell below. Tagged ʿāriḍ-li-s-sukūn
        # (consistent with the ʿiwaḍ-alef / Allah-dagger carriers at waqf).
        waqf_vowel_carrier = (
            not base_is_vowel_carrier and word.is_stopping and not split
            and not lm.has_shaddah and lm.char in VOWEL_CARRIER_CHARS
            and diac is not None and not mod_pairs and base_pairs
            and all(is_madd_phoneme(p[1]) for p in base_pairs)
        )
        base_role = MADD if (base_is_vowel_carrier or waqf_vowel_carrier) else BASE
        base_tag = None
        if base_role == BASE and not base_pairs:
            # Raw-silent letter: name the source silence rule (idgham-source merge,
            # lam_shamsiyah, hamza_wasl_silent, silent_iltiqaa_sakinayn, the
            # vowel_silent catch-all) or the silent_unclassified no-rule gap.
            base_tag = _silent_cell_tag(lm, word, li)
        elif base_role == BASE:
            base_tag = (_pick_tag(rules, NOON_RULE_TAGS)
                        or _pick_tag(rules, GHUNNAH_BASE_TAGS)
                        or (madd_types.get(base_pairs[0][0]) if base_pairs else None)
                        or (_pick_tag(rules, QALQALA_RULE_ORDER) if q_pairs else None)
                        or ("tafkheem" if "tafkheem" in rules else None))
        elif waqf_vowel_carrier:
            # ʿāriḍ-li-s-sukūn at the stop. A plain ṭabīʿī madd (now mapped to
            # madd_tabii) does NOT override that — only a CLASSIFIED non-tabii type
            # (the rare case the mapping already pins it) wins.
            mtype = madd_types.get(base_pairs[0][0])
            base_tag = mtype if (mtype and mtype != "madd_tabii") else "madd_arid_lissukun"
        elif base_pairs:  # standalone long-vowel carrier (ا/آ/و/ي) — its madd type
            base_tag = madd_types.get(base_pairs[0][0])
        # Compose the canonical shaddah onto a mushaddad base (the aligner's bare
        # letter char carries none) so a renderer reads the gemination from chars.
        # A plain geminate (rˤrˤ, ll…) is detected from the phoneme; a mushaddad
        # nūn/mīm sounds a NASALISED geminate (ñ/m̃, which is_geminate misses), so
        # gate that on the letter's own shaddah — never adds one to an idgham
        # receiver that merely sounds ñ/m̃ without a written shaddah (يَقُول's yāʾ).
        if (base_pairs and SHADDA not in base_chars
                and (is_geminate(base_pairs[0][1])
                     or (is_nasalised(base_pairs[0][1]) and lm.has_shaddah))):
            base_chars = base_chars + SHADDA
        # Heaviness (tafkheem) co-occurs with a madd / qalqala that wins the single
        # ``tag`` pick (a heavy ا carrier, a heavy قْ/طْ). Preserve it as a secondary
        # rule so a renderer can stack the tafkheem badge on the primary one. A heavy
        # vowel CARRIER (the full alef after a heavy consonant) carries no tafkheem on
        # its own ``lm`` — its heaviness is the long-vowel phoneme itself — so detect
        # it from the phoneme too, mirroring tajweed_mapping's HEAVY_VOWEL_PHONEMES.
        base_heavy = ("tafkheem" in rules
                      or any(p[1] in HEAVY_VOWEL_PHONEMES for p in base_pairs))
        base_secondary = ["tafkheem"] if (base_heavy and base_tag != "tafkheem") else []
        cells.append(Cell(
            chars=base_chars, role=base_role,
            status=PRESENT if base_pairs else DROPPED,
            phonemes=[p for _, p in base_pairs],
            phoneme_indices=[i for i, _ in base_pairs],
            tag=base_tag,
            source_letter_index=li, source_letter_indices=[li],
            secondary_tags=base_secondary,
        ))

        # ---- madd extension cell --------------------------------------------
        # (dagger-alef / mini-waw / mini-yaa carrier on the same letter — its madd type)
        if split and madd_pair is not None:
            # The split madd carrier (dagger-alef / mini-waw/yaa) inherits the
            # letter's heaviness too (e.g. صٰ): stack tafkheem on its madd tag.
            madd_secondary = ["tafkheem"] if "tafkheem" in rules else []
            cells.append(Cell(
                chars=madd_chars, role=MADD, status=PRESENT,
                phonemes=[madd_pair[1]], phoneme_indices=[madd_pair[0]],
                tag=madd_types.get(madd_pair[0]),
                source_letter_index=li, source_letter_indices=[li],
                secondary_tags=madd_secondary,
            ))

        # ---- dropped pronoun-haa ṣilah cell (waqf) --------------------------
        # The ṣilah glyph keeps its own MADD cell (status=dropped, no phoneme) so
        # the renderer shows هـ | (silent haraka + silent ṣilah) instead of gluing
        # the mini-waw/yaa onto the haa. The dropped haraka rides it as a silent
        # vowel group below.
        if dropped_silah_chars:
            cells.append(Cell(
                chars=dropped_silah_chars, role=MADD, status=DROPPED,
                phonemes=[], phoneme_indices=[],
                source_letter_index=li, source_letter_indices=[li],
            ))

        # ---- implicit Allah dagger-alef cell --------------------------------
        # ṭabīʿī when continuing (tag=allah_dagger_alef); at waqf it becomes madd
        # ʿāriḍ — the classified madd type wins so the carrier reads its rule.
        if allah_pair is not None:
            cells.append(Cell(
                chars="", role=MADD, status=INSERTED,
                phonemes=[allah_pair[1]], phoneme_indices=[allah_pair[0]],
                tag=madd_types.get(allah_pair[0], "allah_dagger_alef"),
                source_letter_index=li, source_letter_indices=[li],
            ))

        # ---- hamza-wasl pronounced: connecting vowel is implicit ------------
        # When started on, ٱ sounds as [ʔ, V] with no written haraka; split the
        # connecting vowel V into its own INSERTED cell (it has no source char).
        if lm.char == "ٱ" and diac is None and len(base_pairs) >= 2:
            base_cell = next(c for c in reversed(cells)
                             if c.source_letter_index == li and c.role == BASE)
            v_idx, v_ph = base_cell.phoneme_indices[1], base_cell.phonemes[1]
            base_cell.phonemes = base_cell.phonemes[:1]
            base_cell.phoneme_indices = base_cell.phoneme_indices[:1]
            cells.append(Cell(
                chars="", role=HARAKA, status=INSERTED,
                phonemes=[v_ph], phoneme_indices=[v_idx], tag="hamza_wasl_vowel",
                source_letter_index=li, source_letter_indices=[li],
            ))

        # ---- haraka / tanween cell ------------------------------------------
        if diac is None:
            continue

        diac_char = diacritic_chars().get(diac, "")
        is_tanween = diac in TANWEEN_DIACRITICS

        # madd-iwad: tanween-fath at waqf realises a compensating madd (a:); the
        # fatḥatan drops and the madd rides an alef. When a silent alef / alef-maksura
        # is WRITTEN after it (عَلِيمًا) that grapheme carries it (force_madd_iwad
        # routes the madd to the next letter's cell). When none is written — the word
        # ends in hamza (مَآءً) — the alef is purely implicit: emit it as an INSERTED
        # graphemeless MADD cell, exactly like the Allah dagger-alef.
        if (is_tanween and word.is_stopping and mod_pairs
                and is_madd_phoneme(mod_pairs[-1][1])):
            madd_iwad = mod_pairs[-1]
            mod_pairs = [p for p in mod_pairs if p != madd_iwad]
            cells.append(Cell(
                chars=diac_char, role=TANWEEN, status=DROPPED,
                phonemes=[], phoneme_indices=[], tag="madd_iwad",
                source_letter_index=li, source_letter_indices=[li],
            ))
            if (li + 1 < n_letters
                    and word.letter_mappings[li + 1].char in ("ا", "ى")
                    and not pairs[li + 1]):
                force_madd_iwad[li + 1] = madd_iwad
            else:
                cells.append(Cell(
                    chars="", role=MADD, status=INSERTED,
                    phonemes=[madd_iwad[1]], phoneme_indices=[madd_iwad[0]],
                    tag="madd_iwad",
                    source_letter_index=li, source_letter_indices=[li],
                ))
            continue

        # iltiqaa kasra: izhar tanween + next-word hamza-wasl -> [V, n, i]; the
        # trailing kasra is an inserted bridge cell.
        iltiqaa_kasra = None
        if is_tanween and len(mod_pairs) == 3 and mod_pairs[-1][1] == "i":
            iltiqaa_kasra = mod_pairs[-1]
            mod_pairs = mod_pairs[:-1]

        if is_tanween:
            tan_tag = _pick_tag(rules, TANWEEN_RULE_TAGS)

            # iqlab tanwīn split: the doubled tanwīn sounds [short-vowel, nasal];
            # emit the vowel as a plain (untagged) haraka and the nasal as its own
            # mini-meem cell carrying the iqlab tag, both anchored to the base so a
            # renderer groups them per-column [base, haraka, mini-meem].
            if (tan_tag == "iqlab_tanween" and len(mod_pairs) == 2
                    and diac in IQLAB_MINI_MEEM):
                v_idx, v_ph = mod_pairs[0]
                n_idx, n_ph = mod_pairs[1]
                cells.append(Cell(
                    chars=IQLAB_SHORT_VOWEL[diac], role=HARAKA, status=PRESENT,
                    phonemes=[v_ph], phoneme_indices=[v_idx], tag=None,
                    source_letter_index=li, source_letter_indices=[li],
                ))
                cells.append(Cell(
                    chars=IQLAB_MINI_MEEM[diac], role=TANWEEN, status=INSERTED,
                    phonemes=[n_ph], phoneme_indices=[n_idx], tag="iqlab_tanween",
                    source_letter_index=li, source_letter_indices=[li],
                ))
                continue

            status = PRESENT
            if word.is_stopping and not mod_pairs:
                status = DROPPED  # dammatan/kasratan dropped at waqf
            cells.append(Cell(
                chars=diac_char, role=TANWEEN, status=status,
                phonemes=[p for _, p in mod_pairs],
                phoneme_indices=[i for i, _ in mod_pairs], tag=tan_tag,
                source_letter_index=li, source_letter_indices=[li],
            ))
            if iltiqaa_kasra is not None:
                cells.append(Cell(
                    chars="", role=HARAKA, status=INSERTED,
                    phonemes=[iltiqaa_kasra[1]], phoneme_indices=[iltiqaa_kasra[0]],
                    tag="iltiqaa_kasra",
                    source_letter_index=li, source_letter_indices=[li],
                ))
            continue

        # plain haraka (fatha/damma/kasra) or sukun
        if diac == "SUKUN":
            cells.append(Cell(
                chars=diac_char, role=HARAKA, status=PRESENT,
                phonemes=[], phoneme_indices=[],
                source_letter_index=li, source_letter_indices=[li],
            ))
            continue

        if mod_pairs:
            # straightforward short/long vowel sitting on this letter
            cells.append(Cell(
                chars=diac_char, role=HARAKA, status=PRESENT,
                phonemes=[p for _, p in mod_pairs],
                phoneme_indices=[i for i, _ in mod_pairs],
                source_letter_index=li, source_letter_indices=[li],
            ))
            continue

        if split and madd_pair is not None:
            # long vowel via same-letter extension: haraka shares the madd index
            cells.append(Cell(
                chars=diac_char, role=HARAKA, status=PRESENT,
                phonemes=[madd_pair[1]], phoneme_indices=[madd_pair[0]],
                source_letter_index=li, source_letter_indices=[li],
            ))
            continue

        # haraka with no own phoneme: absorbed by the following vowel letter.
        nxt = li + 1
        nxt_pairs = pairs[nxt] if nxt < n_letters else []
        if nxt_pairs and word.letter_mappings[nxt].char in VOWEL_CARRIER_CHARS:
            nidx, nph = nxt_pairs[0]
            if sounding_in_flat(word, nxt) and is_madd_phoneme(nph):
                # long vowel: haraka + carrier share the long-vowel index
                cells.append(Cell(
                    chars=diac_char, role=HARAKA, status=PRESENT,
                    phonemes=[nph], phoneme_indices=[nidx],
                    source_letter_index=li, source_letter_indices=[li],
                ))
                continue
            if not sounding_in_flat(word, nxt) and nph in SHORT_VOWEL_PHONEMES:
                # iltiqaa shortening: haraka takes the short vowel; carrier silenced
                cells.append(Cell(
                    chars=diac_char, role=HARAKA, status=SHORTENED,
                    phonemes=[nph], phoneme_indices=[nidx], tag="iltiqaa",
                    source_letter_index=li, source_letter_indices=[li],
                ))
                force_dropped.add(nxt)
                continue

        # fallback: emit an empty haraka cell (covered by index-coverage check)
        cells.append(Cell(
            chars=diac_char, role=HARAKA, status=DROPPED,
            phonemes=[], phoneme_indices=[],
            source_letter_index=li, source_letter_indices=[li],
        ))

    _reorder_dropped_silah(cells)
    return cells


def _reorder_dropped_silah(cells: List[Cell]) -> None:
    """Move a dropped pronoun-haa ṣilah cell to just after the haa's own haraka.

    The ṣilah glyph is emitted right after its base (before the haa's ḍamma/kasra),
    but orthographically the haraka sits on the haa and precedes the mini-waw/yaa.
    At waqf the pair is silent (no shared vowel group to re-sort downstream), so the
    raw cell order is what renders — reorder to ``[base, haraka, ṣilah]``. The
    dropped ṣilah is the only MADD cell that is ``DROPPED`` yet keeps its glyph."""
    for i, c in enumerate(cells):
        if not (c.role == MADD and c.status == DROPPED and c.chars):
            continue
        silah = cells.pop(i)
        for j in range(i, len(cells)):
            if (cells[j].role == HARAKA
                    and cells[j].source_letter_index == silah.source_letter_index):
                cells.insert(j + 1, silah)
                return
        cells.insert(i, silah)  # no haraka on the letter — leave as emitted
        return


def _assign_intra_word_share_groups(cells: List[Cell], start_gid: int) -> int:
    """Group cells (within one word) that reference the same phoneme index."""
    by_index: Dict[int, List[Cell]] = {}
    for c in cells:
        for i in c.phoneme_indices:
            by_index.setdefault(i, []).append(c)
    gid = start_gid
    assigned: Dict[int, int] = {}  # phoneme index -> group id
    for i, group in by_index.items():
        if len(group) < 2:
            continue
        g = assigned.get(i)
        if g is None:
            g = gid
            gid += 1
        for c in group:
            if c.share_group is None:
                c.share_group = g
        assigned[i] = g
    return gid


def _link_cross_word(words: List[CharWord], mapping: PhonemizationMapping, start_gid: int) -> int:
    """Co-highlight cross-word idgham mergers: the two graphemes that voice as one
    sound share a group, so the consumer lights both through the merger.

    Boundaries come from the single ``detect_cross_word_mergers`` (the same detector
    the SDK shard bridge tagger uses). Co-lighting is scoped — as before — to the
    tagged noon/tanwīn idghams and the both-sound shafawi merge:

      - tanwīn / noon idgham (``side == "curr"``, tagged) — the tagged cell of word
        N and the first sounding base of word N+1 (the merger lands on N+1's head).
      - consonant idgham shafawi (``both_sound``) — word N's last sounding BASE and
        word N+1's first sounding BASE (the merger m̃ lands on N's tail; N+1's base
        carries only the following vowel).

    (mutamathilayn / mutaqaribayn / mutajanisayn are bridges but not cell co-light
    sources, matching the historical scope.)"""
    gid = start_gid
    for m in detect_cross_word_mergers(mapping):
        cur, nxt = words[m.prev_word_index], words[m.curr_word_index]
        if m.both_sound:
            # Idgham shafawi: the receiver is the next word's FIRST base (the meem),
            # which may own NO phoneme — the merged consonant lives on the source
            # meem, and a following long vowel sits on its own alef/madd (مَّا → the
            # aː is on the alef). Don't require phoneme_indices, else the meem is
            # never linked and greys out.
            recv = next((c for c in nxt.cells if c.role == BASE), None)
            source = next((c for c in reversed(cur.cells)
                           if c.role == BASE and c.phoneme_indices), None)
        elif m.rule in IDGHAM_SOURCE_TAG_VALUES:
            recv = next((c for c in nxt.cells if c.role == BASE and c.phoneme_indices), None)
            source = next((c for c in cur.cells if c.tag in IDGHAM_SOURCE_TAG_VALUES), None)
        else:
            continue
        if recv is None or source is None:
            continue
        if source.share_group is None and recv.share_group is None:
            g = gid
            gid += 1
        else:
            g = source.share_group if source.share_group is not None else recv.share_group
        source.share_group = recv.share_group = g
        # Idgham shafawi convergence: the receiving meem's BASE sounds the following
        # short vowel (the consonant merged into the source meem's m̃, which carries
        # the whole geminated nasal). Move that vowel onto the meem's own haraka — its
        # OWN interval, NOT the merger group — and strip it off the base, so the base
        # owns no phoneme and co-lights purely through the nasal/share union, exactly
        # like an idgham-ghunnah/noon receiver. This keeps the vowel off the base
        # (so it aligns under its haraka) and out of the union (so looping the haraka
        # no longer intersects either meem's cell span).
        if recv.phonemes and is_short_vowel(recv.phonemes[0]):
            absorbed = next(
                (c for c in nxt.cells
                 if c.role == HARAKA and not c.phoneme_indices
                 and c.source_letter_index == recv.source_letter_index),
                None,
            )
            if absorbed is not None:
                absorbed.phoneme_indices = list(recv.phoneme_indices)
                absorbed.phonemes = list(recv.phonemes)
                absorbed.status = PRESENT
                recv.phoneme_indices = []
                recv.phonemes = []
    return gid


def build_char_phoneme_mapping(mapping: PhonemizationMapping) -> List[CharWord]:
    words: List[CharWord] = []
    gid = 0
    for wm in mapping.words:
        cells = (_special_word_cells(wm) if wm.is_special_word else _word_cells(wm))
        gid = _assign_intra_word_share_groups(cells, gid)
        words.append(CharWord(
            location=wm.location, text=wm.text,
            is_starting=wm.is_starting, is_stopping=wm.is_stopping, cells=cells,
        ))
    gid = _link_cross_word(words, mapping, gid)
    return words


# =============================================================================
# Validation
# =============================================================================

def validate(words: List[CharWord], mapping: PhonemizationMapping) -> List[str]:
    violations: List[str] = []

    for wi, (cw, wm) in enumerate(zip(words, mapping.words)):
        n_ph = len(wm.phonemes)
        # (1) index coverage: every word-local phoneme index referenced >=1 time
        seen: Dict[int, int] = {}
        for c in cw.cells:
            for i in c.phoneme_indices:
                if not (0 <= i < n_ph):
                    violations.append(
                        f"{wm.location}: cell {c.chars!r} index {i} out of range 0..{n_ph}")
                seen[i] = seen.get(i, 0) + 1
        missing = [i for i in range(n_ph) if i not in seen]
        if missing:
            violations.append(f"{wm.location}: phoneme indices not covered: {missing} "
                              f"(phonemes={wm.phonemes})")
        # (2) shared index => same share_group
        for i, count in seen.items():
            if count > 1:
                groups = {c.share_group for c in cw.cells if i in c.phoneme_indices}
                if None in groups or len(groups) != 1:
                    violations.append(
                        f"{wm.location}: phoneme index {i} shared by cells without one "
                        f"share_group (groups={groups})")
        # (3) char completeness: each letter's diacritic char appears in a cell.
        # An iqlab tanwīn is decomposed into [short-vowel haraka, mini-meem] cells
        # (B1), so its doubled-tanwīn glyph is intentionally absent — the
        # iqlab_tanween-tagged mini-meem cell stands in for it.
        for li, lm in enumerate(wm.letter_mappings):
            if lm.diacritic and not wm.is_special_word:
                dc = diacritic_chars().get(lm.diacritic, "")
                anchored = [c for c in cw.cells if c.source_letter_index == li]
                iqlab_split = (lm.diacritic in IQLAB_MINI_MEEM
                               and any(c.tag == "iqlab_tanween" for c in anchored))
                if dc and not iqlab_split and not any(dc in c.chars for c in anchored):
                    violations.append(
                        f"{wm.location}: letter {li} ({lm.char!r}) diacritic "
                        f"{lm.diacritic} has no cell")

    # (4) phonemes match the resolved phoneme strings at their indices
    offset = 0
    for cw, wm in zip(words, mapping.words):
        for c in cw.cells:
            for ph, i in zip(c.phonemes, c.phoneme_indices):
                if 0 <= i < len(wm.phonemes) and wm.phonemes[i] != ph:
                    violations.append(
                        f"{wm.location}: cell {c.chars!r} phoneme {ph!r} != "
                        f"phonemes[{i}]={wm.phonemes[i]!r}")
        offset += len(wm.phonemes)

    return violations


# =============================================================================
# Public result
# =============================================================================

@dataclass
class CharPhonemeResult:
    words: List[CharWord]
    mapping: PhonemizationMapping
    ref: str = ""

    def to_list(self) -> list:
        return [[c.to_list() for c in w.cells] for w in self.words]

    def to_dict(self) -> dict:
        return {
            "ref": self.ref,
            "words": [
                {
                    "location": w.location,
                    "text": w.text,
                    "is_starting": w.is_starting,
                    "is_stopping": w.is_stopping,
                    "cells": [c.to_dict() for c in w.cells],
                }
                for w in self.words
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def validate(self) -> List[str]:
        return validate(self.words, self.mapping)

    def save(self, path: str, indent: int = 2) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json(indent=indent))
