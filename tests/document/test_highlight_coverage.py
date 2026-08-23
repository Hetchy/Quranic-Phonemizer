"""Continuous-text highlight groups cover every sound and every letter.

Coverage is the acceptance: the laws hold over a curated site list and the whole
corpus, in every boundary state, with no exemption list.
"""
from __future__ import annotations

import dataclasses

import pytest

from quranic_phonemizer.analysis import ids
from quranic_phonemizer.analysis.build import build_bundle
from quranic_phonemizer.analysis.dtos import BoundaryState
from quranic_phonemizer.analysis.highlight_dtos import HighlightGroup
from quranic_phonemizer.analysis.highlight_laws import (
    HighlightValidationError,
    validate_highlight_groups,
)
from quranic_phonemizer.analysis.highlights import highlight_groups
from quranic_phonemizer.analysis.source import build_source_view
from quranic_phonemizer.analysis.source_dtos import LetterUnitKind
from quranic_phonemizer.model.address import Script
from quranic_phonemizer.orthography.inventory import InventoryError
from quranic_phonemizer.model.canon import Rule
from quranic_phonemizer.session import phonemize_request

#: One site per fold direction and hard case: a silent alif that folds back,
#: an alif after tanween, the iwad alif maksura at a stop, the seen/saad pair;
#: an elided hamzat wasl and an assimilated article lam that fold forward; the
#: iltiqa vowel chain and cross-word idgham of the noon and the tanween that
#: fold across; ikhfaa and iqlab that keep their own group; the muqattaat and
#: the carrier-less divine name that the long vowel law excepts.
SITES = [
    ("1:1", {}),
    ("1:1:2", {}),
    ("112:1", {}),
    ("2:6:3", {}),
    ("2:4:8-2:4:9", {}),
    ("2:26:18-2:26:19", {}),
    ("2:11:6-2:11:7", {}),
    ("2:245:14", {}),
    ("36:52-36:53", {}),
    ("2:1", {}),
    ("2:255", {}),
    ("11:41", {}),
    ("2:5:3", {"stop_refs": ["2:5:3"]}),
    ("18:38", {"stop_refs": ["18:38:1"]}),
    ("1:2", {"stop_refs": ["1:2:1"]}),
]


def _built(hafs, ref, kwargs, script=Script.UTHMANI):
    session = phonemize_request(hafs, ref, script=script, **kwargs)
    bundle = build_bundle(
        session, ref=ref, riwayah="hafs", script=script.value, variant={}
    )
    view = build_source_view(session, bundle=bundle)
    return bundle, view, highlight_groups(view, bundle)


def _is_long(token: str) -> bool:
    return ("ː" in token) or (":" in token)


def _rule_names(bundle, sound) -> set[str]:
    rule_of = {occ.id.value: occ.rule_id.value for occ in bundle.rule_occurrences}
    return {rule_of[o.value] for o in sound.rule_occurrence_ids}


def _is_carrier(bundle, view, unit_id) -> bool:
    """A written madd carrier is a source letter that sounds no consonant of its
    own: a bare alif, waw, or yaa, or a silent length letter folded in."""
    unit = view.units[unit_id]
    if unit.kind is not LetterUnitKind.LETTER:
        return False
    return not any(
        not _is_long(bundle.sounds[s.value].token) for s in unit.owned_sound_ids
    )


def _owns_consonant(bundle, unit) -> bool:
    return any(
        not _is_long(bundle.sounds[s.value].token) for s in unit.owned_sound_ids
    )


def _long_vowel_violations(bundle, view, groups) -> list[str]:
    """Every long vowel has a madd unit alone with its own owner in its group,
    except where the script writes no carrier: a muqattaat letter spelling its
    own name, or the divine name and hamza with fathatan seated on a haraka."""
    owner_unit = {
        sound.value: unit.id.value
        for unit in view.units
        for sound in unit.owned_sound_ids
    }
    group_of = {
        sound.value: group for group in groups for sound in group.sound_ids
    }
    out: list[str] = []
    for sound in bundle.sounds:
        if not _is_long(sound.token):
            continue
        group = group_of[sound.id.value]
        owner = view.units[owner_unit[sound.id.value]]
        if any(_is_carrier(bundle, view, u.value) for u in group.unit_ids):
            foreign = [
                u.value
                for u in group.unit_ids
                if u.value != owner.id.value
                and _owns_consonant(bundle, view.units[u.value])
            ]
            if foreign:
                out.append(
                    f"{bundle.ref}: long {sound.id.value} shares its group "
                    f"with {foreign}"
                )
            continue
        # No carrier in the group; excused only where the script writes none:
        # the divine name and hamza with fathatan seat the length on a mark, a
        # muqattaat letter spells the length into its own name.
        seated_on_mark = owner.kind is not LetterUnitKind.LETTER
        muqattaat = _owns_consonant(bundle, owner) and (
            Rule.IMALA.value not in _rule_names(bundle, sound)
        )
        if not (seated_on_mark or muqattaat):
            out.append(f"{bundle.ref}: long {sound.id.value} has no madd unit")
    return out


def _group_of_unit(groups) -> dict[int, HighlightGroup]:
    return {u.value: group for group in groups for u in group.unit_ids}


# --- the laws over a curated site list ------------------------------------


@pytest.mark.parametrize(("ref", "kwargs"), SITES)
def test_the_groups_validate_and_cover_the_long_vowels(hafs, ref, kwargs):
    bundle, view, groups = _built(hafs, ref, kwargs)
    validate_highlight_groups(groups, view, bundle)
    assert not _long_vowel_violations(bundle, view, groups)


def test_the_site_set_exercises_every_boundary_state(hafs):
    states: set[BoundaryState] = set()
    for ref, kwargs in SITES:
        bundle, _, _ = _built(hafs, ref, kwargs)
        states |= {b.state for b in bundle.boundaries}
    assert states == set(BoundaryState)


# --- each fold direction, pinned ------------------------------------------


def test_an_elided_hamzat_wasl_folds_forward(hafs):
    """The prosthetic hamza is silent and joins the sounding letter after it,
    never a group of its own."""
    _, view, groups = _built(hafs, "1:1", {})
    of_unit = _group_of_unit(groups)
    wasl = next(u for u in view.units if u.text == "ٱ" and u.silence)
    lam = next(u for u in view.units if "لّ" in u.text)  # shaddad lam
    assert of_unit[wasl.id.value] is of_unit[lam.id.value]


def test_a_prefixed_wasl_still_folds_forward_not_into_the_prefix(hafs):
    """A hamzat wasl carries a sounding prefix vowel before it in the same word
    (2:3 bi-al-ghayb). It still elides into the letter after it; folding it back
    into the prefix -- the adjacency guess -- is the direction bug."""
    _, view, groups = _built(hafs, "2:3", {})
    of_unit = _group_of_unit(groups)
    wasl = next(
        u for i, u in enumerate(view.units)
        if isinstance(u.silence, ids.OccurrenceId)
        and u.text == "ٱ"
        and i > 0
        and view.units[i - 1].word_id == u.word_id
        and (
            view.units[i - 1].owned_sound_ids
            or view.units[i - 1].presented_sound_ids
        )
    )
    after = view.units[wasl.id.value + 1]
    before = view.units[wasl.id.value - 1]
    assert after.owned_sound_ids
    assert of_unit[wasl.id.value] is of_unit[after.id.value]
    assert of_unit[wasl.id.value] is not of_unit[before.id.value]


def test_an_iltiqa_vowel_chains_across_the_boundary(hafs):
    """The shortened long vowel is silent at a word end and joins the next
    word's first sounding letter, not its own word."""
    bundle, view, groups = _built(hafs, "2:11:6-2:11:7", {})
    of_unit = _group_of_unit(groups)
    yaa = next(u for u in view.units if u.text == "ى" and u.silence)
    lam_l = next(
        u for u in view.units
        if any(bundle.sounds[s.value].token == "l" for s in u.owned_sound_ids)
    )
    assert of_unit[yaa.id.value] is of_unit[lam_l.id.value]
    assert yaa.word_id != lam_l.word_id


def test_cross_word_idgham_folds_across_but_ikhfaa_does_not(hafs):
    """The assimilated noon has no sound and joins the host across the boundary;
    the nasalized noon keeps its own sound and holds its own group."""
    bundle, view, groups = _built(hafs, "2:26:18-2:26:19", {})
    of_unit = _group_of_unit(groups)
    silent_noon = next(
        u for u in view.units
        if u.text == "ن" and not u.owned_sound_ids and u.presented_sound_ids
    )
    shared = {s.value for s in silent_noon.presented_sound_ids}
    host = next(
        u for u in view.units
        if any(s.value in shared for s in u.owned_sound_ids)
    )
    assert of_unit[silent_noon.id.value] is of_unit[host.id.value]
    assert silent_noon.word_id != host.word_id

    ikbundle, ikview, ikgroups = _built(hafs, "2:4:8-2:4:9", {})
    ik_of = _group_of_unit(ikgroups)
    nasal_noon = next(
        u for u in ikview.units
        if u.text == "ن"
        and any(ikbundle.sounds[s.value].token == "ŋ" for s in u.owned_sound_ids)
    )
    group = ik_of[nasal_noon.id.value]
    assert group.unit_ids == (nasal_noon.id,)


def test_a_seen_saad_pair_is_one_group(hafs):
    """The unread base and the mini seen written on it share one group and one
    sound."""
    _, view, groups = _built(hafs, "2:245:14", {})
    of_unit = _group_of_unit(groups)
    rider = next(u for u in view.units if u.written_on_unit_id is not None)
    base = view.units[rider.written_on_unit_id.value]
    assert of_unit[rider.id.value] is of_unit[base.id.value]


def test_the_madd_carrier_is_a_group_apart_from_its_consonant(hafs):
    """The dagger alif holds the long vowel in its own group; the consonant
    before it lights separately."""
    bundle, view, groups = _built(hafs, "1:1", {})
    of_unit = _group_of_unit(groups)
    dagger = next(u for u in view.units if u.text == "ٰ")
    meem = view.units[dagger.id.value - 2]  # the consonant meem before the seat
    assert meem.text == "م"
    assert of_unit[dagger.id.value] is not of_unit[meem.id.value]


# --- the whole corpus, opt-in ---------------------------------------------


def _hold(hafs, ref, kwargs, script) -> None:
    bundle, view, groups = _built(hafs, ref, kwargs, script)
    validate_highlight_groups(groups, view, bundle)
    violations = _long_vowel_violations(bundle, view, groups)
    assert not violations, violations


@pytest.mark.slow
def test_the_laws_hold_over_the_whole_corpus(hafs, packed):
    info = packed.surah_info
    uthmani = 0
    indopak = 0
    for surah in range(1, 115):
        for ayah in range(1, len(info[str(surah)]) + 1):
            ref = f"{surah}:{ayah}"
            words = info[str(surah)][ayah - 1]
            # Stop after every internal word so the paused plan really differs
            # from the joined one; a bare verse ref names no internal boundary.
            stops = [f"{ref}:{word}" for word in range(1, words)]
            for kwargs in ({}, {"stop_refs": stops}):
                _hold(hafs, ref, kwargs, Script.UTHMANI)
                uthmani += 1
                try:
                    _hold(hafs, ref, kwargs, Script.INDOPAK)
                except InventoryError:
                    # The IndoPak inventory does not declare every corpus
                    # scalar; where it cannot read the verse there is nothing
                    # to highlight. The law itself carries no site exemption.
                    continue
                indopak += 1
    assert uthmani > 12000
    assert indopak > 1500


# --- the checks bite -------------------------------------------------------


def _reindexed(groups: list[HighlightGroup]) -> tuple[HighlightGroup, ...]:
    ordered = sorted(
        groups, key=lambda g: g.sound_ids[0].value if g.sound_ids else 1 << 30
    )
    return tuple(
        dataclasses.replace(g, id=ids.HighlightId(order))
        for order, g in enumerate(ordered)
    )


def test_a_unit_dropped_from_every_group_fails_coverage(hafs):
    bundle, view, groups = _built(hafs, "1:1", {})
    victim = next(g for g in groups if len(g.unit_ids) > 1)
    dropped = victim.unit_ids[-1]
    kept = {tuple(r) for r in view.units[dropped.value].ranges}
    thinned = dataclasses.replace(
        victim,
        unit_ids=victim.unit_ids[:-1],
        ranges=tuple(r for r in victim.ranges if tuple(r) not in kept),
    )
    broken = tuple(g if g is not victim else thinned for g in groups)
    with pytest.raises(HighlightValidationError):
        validate_highlight_groups(broken, view, bundle)


def test_a_silent_only_group_fails(hafs):
    """A folded silent unit hoisted into its own group, carrying a sound no unit
    in it owns, has no sounding presenter and is rejected."""
    bundle, view, groups = _built(hafs, "2:5:3", {"stop_refs": ["2:5:3"]})
    pair = next(
        g for g in groups
        if len(g.unit_ids) == 2
        and not view.units[g.unit_ids[-1].value].owned_sound_ids
    )
    owner_id, silent_id = pair.unit_ids[0], pair.unit_ids[1]
    silent = view.units[silent_id.value]
    owner = view.units[owner_id.value]
    silent_only = HighlightGroup(
        id=ids.HighlightId(0),
        unit_ids=(silent_id,),
        ranges=silent.ranges,
        sound_ids=pair.sound_ids,
    )
    stripped = HighlightGroup(
        id=ids.HighlightId(0), unit_ids=(owner_id,), ranges=owner.ranges,
        sound_ids=(),
    )
    rest = [g for g in groups if g is not pair] + [silent_only, stripped]
    broken = _reindexed(rest)
    with pytest.raises(HighlightValidationError):
        validate_highlight_groups(broken, view, bundle)


def test_ikhfaa_folded_across_fails_the_owner_law(hafs):
    """Merging the nasalized noon's group with the letter after it makes a group
    with two owners nothing links; the multi-owner law rejects it."""
    bundle, view, groups = _built(hafs, "2:4:8-2:4:9", {})
    of_unit = _group_of_unit(groups)
    noon = next(
        u for u in view.units
        if u.text == "ن"
        and any(bundle.sounds[s.value].token == "ŋ" for s in u.owned_sound_ids)
    )
    noon_group = of_unit[noon.id.value]
    after = min(
        (g for g in groups if g is not noon_group and g.sound_ids
         and g.sound_ids[0].value > noon_group.sound_ids[-1].value),
        key=lambda g: g.sound_ids[0].value,
    )
    merged = HighlightGroup(
        id=ids.HighlightId(0),
        unit_ids=tuple(sorted(noon_group.unit_ids + after.unit_ids)),
        ranges=tuple(sorted(noon_group.ranges + after.ranges)),
        sound_ids=tuple(sorted(noon_group.sound_ids + after.sound_ids)),
    )
    rest = [g for g in groups if g not in (noon_group, after)] + [merged]
    broken = _reindexed(rest)
    with pytest.raises(HighlightValidationError):
        validate_highlight_groups(broken, view, bundle)


def test_a_long_vowel_merged_into_its_consonant_fails_the_long_vowel_law(hafs):
    """The long vowel law bites: fold the dagger alif's group into the consonant
    before it and the long vowel no longer stands alone."""
    bundle, view, groups = _built(hafs, "1:1", {})
    of_unit = _group_of_unit(groups)
    dagger = next(u for u in view.units if u.text == "ٰ")
    madd_group = of_unit[dagger.id.value]
    meem_group = of_unit[dagger.id.value - 2]
    merged = HighlightGroup(
        id=madd_group.id,
        unit_ids=tuple(sorted(madd_group.unit_ids + meem_group.unit_ids)),
        ranges=tuple(sorted(madd_group.ranges + meem_group.ranges)),
        sound_ids=tuple(sorted(madd_group.sound_ids + meem_group.sound_ids)),
    )
    rest = [g for g in groups if g not in (madd_group, meem_group)] + [merged]
    broken = _reindexed(rest)
    assert _long_vowel_violations(bundle, view, broken)


def _singles(groups) -> list[HighlightGroup]:
    return [g for g in groups if len(g.unit_ids) == 1 and len(g.sound_ids) == 1]


def test_swapped_units_between_groups_fails_the_sound_owner_law(hafs):
    """Two groups keep their sounds but trade unit_ids and ranges; neither
    group's sound now resolves to an owner or presenter inside it."""
    bundle, view, groups = _built(hafs, "1:1", {})
    a, b = _singles(groups)[0], _singles(groups)[1]
    swapped_a = dataclasses.replace(a, unit_ids=b.unit_ids, ranges=b.ranges)
    swapped_b = dataclasses.replace(b, unit_ids=a.unit_ids, ranges=a.ranges)
    broken = tuple(
        swapped_a if g is a else swapped_b if g is b else g for g in groups
    )
    with pytest.raises(HighlightValidationError):
        validate_highlight_groups(broken, view, bundle)


def test_swapped_ranges_between_groups_fail_the_range_law(hafs):
    """Ranges no longer coalesce from each group's own units."""
    bundle, view, groups = _built(hafs, "1:1", {})
    a, b = _singles(groups)[0], _singles(groups)[1]
    broken = tuple(
        dataclasses.replace(a, ranges=b.ranges) if g is a
        else dataclasses.replace(b, ranges=a.ranges) if g is b
        else g
        for g in groups
    )
    with pytest.raises(HighlightValidationError):
        validate_highlight_groups(broken, view, bundle)


def test_overlapping_ranges_across_groups_fail_the_range_law(hafs):
    """One group swallows a scalar a distant group still owns; each group's
    ranges match its own units, yet the two overlap across the text."""
    bundle, view, groups = _built(hafs, "1:1", {})
    early = groups[0]
    later = next(g for g in groups if g.ranges[0][0] > early.ranges[-1][1])
    grown = dataclasses.replace(
        later,
        unit_ids=tuple(sorted(later.unit_ids + early.unit_ids)),
        ranges=tuple(sorted(later.ranges + early.ranges)),
    )
    broken = tuple(grown if g is later else g for g in groups)
    with pytest.raises(HighlightValidationError):
        validate_highlight_groups(broken, view, bundle)


def test_a_sound_id_in_place_of_a_highlight_id_fails(hafs):
    """A group keyed by a SoundId of the same integer as its position is a
    wrong-kind id, rejected though the integer matches its order."""
    bundle, view, groups = _built(hafs, "1:1", {})
    first = groups[0]
    mistyped = dataclasses.replace(first, id=ids.SoundId(first.id.value))
    broken = (mistyped,) + tuple(groups[1:])
    with pytest.raises(HighlightValidationError):
        validate_highlight_groups(broken, view, bundle)


def test_removing_the_madd_units_from_an_imala_group_fails(hafs):
    """Strip the written madd letters out of the imala group and the long vowel
    has no carrier left, though its owner still sounds its consonant."""
    bundle, view, groups = _built(hafs, "11:41", {})
    imala = next(
        s for s in bundle.sounds
        if _is_long(s.token) and Rule.IMALA.value in _rule_names(bundle, s)
    )
    group = next(
        g for g in groups if any(s.value == imala.id.value for s in g.sound_ids)
    )
    kept = tuple(
        u for u in group.unit_ids if not _is_carrier(bundle, view, u.value)
    )
    ranges = tuple(
        sorted(span for u in kept for span in view.units[u.value].ranges)
    )
    thinned = dataclasses.replace(group, unit_ids=kept, ranges=ranges)
    broken = tuple(thinned if g is group else g for g in groups)
    assert _long_vowel_violations(bundle, view, broken)
