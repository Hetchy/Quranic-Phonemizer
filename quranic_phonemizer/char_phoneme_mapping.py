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
    TANWEEN_DIACRITICS,
    SHORT_VOWEL_PHONEMES,
)
from .silent import sounding_in_flat
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
    is_nasalised,
    is_render_only,
    is_short_vowel,
)

# Shaddah (gemination mark) — composed onto a geminated base cell's chars so a
# renderer reads it from the canonical text instead of inferring it from the
# phoneme shape.
SHADDA = "ّ"  # U+0651


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
    """
    chars: str
    role: str
    status: str
    phonemes: List[str] = field(default_factory=list)
    phoneme_indices: List[int] = field(default_factory=list)
    tag: Optional[str] = None
    share_group: Optional[int] = None
    source_letter_index: int = -1
    source_letter_indices: List[int] = field(default_factory=list)

    def to_list(self) -> list:
        """Full 9-field dump (incl. ``phonemes`` + ``source_letter_indices``). This
        is the phonemizer's own serialization — NOT the 7-slot Timestamps shard
        row, which a downstream consumer (the SDK) projects in a different field
        order; do not conflate the two positionally."""
        return [
            self.chars, self.role, self.status,
            list(self.phonemes), list(self.phoneme_indices),
            self.tag, self.share_group,
            self.source_letter_index, list(self.source_letter_indices),
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
    """Word-local phoneme index -> ``madd_<type>`` tag for every CLASSIFIED madd
    (wajib_muttasil / jaiz_munfasil / lazim / arid_lissukun / leen).

    Regular ṭabīʿī madds (``madd_type is None``) and implicit-only entries
    (``phoneme_index < 0``) are skipped, so they stay untagged. The carrier cell
    reads its own phoneme index from this map; the paired haraka is never tagged
    (a madd colours only the carrier grapheme)."""
    return {mm.phoneme_index: f"madd_{mm.madd_type}"
            for mm in word.madd_mappings
            if getattr(mm, "madd_type", None) and mm.phoneme_index >= 0}


# =============================================================================
# Builder
# =============================================================================

def _special_word_cells(word: WordMapping) -> List[Cell]:
    """Muqaṭṭaʿāt / hardcoded words: one BASE cell per sounding letter."""
    cells: List[Cell] = []
    pairs = _letter_pairs(word)
    for li, lm in enumerate(word.letter_mappings):
        lp = pairs[li]
        if not lp:
            continue  # inert (e.g. trailing stop-sign entry " ۚ")
        cells.append(Cell(
            chars=get_full_char(lm), role=BASE, status=PRESENT,
            phonemes=[p for _, p in lp], phoneme_indices=[i for i, _ in lp],
            source_letter_index=li, source_letter_indices=[li],
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
        base_role = MADD if base_is_vowel_carrier else BASE
        base_tag = None
        if base_role == BASE:
            base_tag = (_pick_tag(rules, NOON_RULE_TAGS)
                        or _pick_tag(rules, GHUNNAH_BASE_TAGS)
                        or (madd_types.get(base_pairs[0][0]) if base_pairs else None)
                        or ("qalqala" if q_pairs else None))
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
        cells.append(Cell(
            chars=base_chars, role=base_role,
            status=PRESENT if base_pairs else DROPPED,
            phonemes=[p for _, p in base_pairs],
            phoneme_indices=[i for i, _ in base_pairs],
            tag=base_tag,
            source_letter_index=li, source_letter_indices=[li],
        ))

        # ---- madd extension cell --------------------------------------------
        # (dagger-alef / mini-waw / mini-yaa carrier on the same letter — its madd type)
        if split and madd_pair is not None:
            cells.append(Cell(
                chars=madd_chars, role=MADD, status=PRESENT,
                phonemes=[madd_pair[1]], phoneme_indices=[madd_pair[0]],
                tag=madd_types.get(madd_pair[0]),
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

    return cells


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
        recv = next((c for c in nxt.cells if c.role == BASE and c.phoneme_indices), None)
        if recv is None:
            continue
        if m.both_sound:
            source = next((c for c in reversed(cur.cells)
                           if c.role == BASE and c.phoneme_indices), None)
        elif m.rule in IDGHAM_SOURCE_TAG_VALUES:
            source = next((c for c in cur.cells if c.tag in IDGHAM_SOURCE_TAG_VALUES), None)
        else:
            continue
        if source is None:
            continue
        if source.share_group is None and recv.share_group is None:
            g = gid
            gid += 1
        else:
            g = source.share_group if source.share_group is not None else recv.share_group
        source.share_group = recv.share_group = g
        # Absorbed-vowel co-light: when the receiving base sounds a short vowel
        # (idgham shafawi — the consonant merged, so the base carries only the
        # following vowel), its dropped haraka on the same letter sounds that
        # vowel. Point the haraka at the vowel + join the merger group so a
        # renderer co-lights it instead of greying it (no phoneme inference).
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
                absorbed.share_group = g
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
        # (3) char completeness: each letter's diacritic char appears in a cell
        for li, lm in enumerate(wm.letter_mappings):
            if lm.diacritic and not wm.is_special_word:
                dc = diacritic_chars().get(lm.diacritic, "")
                anchored = [c for c in cw.cells if c.source_letter_index == li]
                if dc and not any(dc in c.chars for c in anchored):
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
