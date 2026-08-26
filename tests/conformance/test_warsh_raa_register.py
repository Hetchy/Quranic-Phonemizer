from __future__ import annotations

from collections import Counter
from functools import lru_cache
import unicodedata

import pytest

from quranic_phonemizer.api import recitation
from quranic_phonemizer.model.address import Location, Riwayah, Script, VerseRef
from quranic_phonemizer.model.canon import (
    CanonLetter as L,
    Onset,
    Quality,
    SlotOrigin,
    VowelForm,
)
from quranic_phonemizer.riwayat.warsh.raa import PROFILE, RaaKey
from tests.support import Site, reading


FIVE_WORDS = frozenset({
    Location(2, 200, 10), Location(18, 70, 12), Location(18, 83, 9),
    Location(20, 99, 13), Location(20, 113, 14), Location(21, 48, 7),
    Location(33, 41, 6), Location(37, 3, 2), Location(37, 168, 4),
    Location(65, 10, 16), Location(77, 5, 2), Location(18, 90, 15),
    Location(18, 71, 15), Location(20, 100, 8), Location(25, 22, 9),
    Location(25, 53, 14),
})
IBRAH_KIBRAHU = frozenset({
    Location(3, 13, 27), Location(12, 111, 5), Location(16, 66, 5),
    Location(23, 21, 5), Location(24, 44, 8), Location(79, 26, 4),
    Location(24, 11, 24),
})
WIZRA_UKHRA = frozenset({
    Location(6, 164, 19), Location(17, 15, 14), Location(35, 18, 4),
    Location(39, 7, 18), Location(53, 38, 4),
})
PAUSAL = frozenset({
    Location(10, 87, 8), Location(12, 21, 5), Location(12, 99, 10),
    Location(43, 51, 10), Location(34, 12, 10), Location(89, 4, 3),
    Location(11, 81, 9), Location(15, 65, 1), Location(44, 23, 1),
    Location(54, 16, 4), Location(54, 18, 6), Location(54, 21, 4),
    Location(54, 30, 4), Location(54, 37, 9), Location(54, 39, 3),
})
REPEATED_HEAVY = frozenset({
    Location(2, 231, 13), Location(9, 107, 4), Location(18, 18, 19), Location(33, 13, 25),
    Location(71, 6, 5), Location(33, 16, 4), Location(71, 9, 7),
    Location(6, 6, 19), Location(11, 52, 10), Location(71, 11, 4),
})
OTHER_ASHIR = frozenset({
    Location(22, 13, 10), Location(26, 214, 2), Location(58, 22, 21),
})


def _keys(locations, raa=1) -> frozenset[RaaKey]:
    return frozenset((location, raa) for location in locations)


def test_finite_register_subtotals_and_exact_members_are_stable():
    assert PROFILE.by_owner["raa_five_words"] == _keys(FIVE_WORDS)
    assert PROFILE.by_owner["raa_ibrah_kibrahu"] == _keys(IBRAH_KIBRAHU)
    assert PROFILE.by_owner["raa_wizra_ukhra"] == _keys(WIZRA_UKHRA)
    assert PROFILE.by_owner["raa_fixed_repeated_heavy"] == _keys(REPEATED_HEAVY)
    assert PROFILE.by_owner["raa_fixed_other_ashir_light"] == _keys(OTHER_ASHIR)
    assert PAUSAL == frozenset(
        location for owner in (
            "raa_misr_waqf", "raa_alqitr_waqf", "raa_yasr_waqf",
            "raa_asr_waqf", "raa_wanuthur_waqf",
        ) for location, _ in PROFILE.by_owner[owner]
    )
    assert Counter({owner: len(keys) for owner, keys in PROFILE.by_owner.items()})[
        "raa_five_words"
    ] == 16


def test_no_finite_target_has_two_all_state_weight_owners():
    all_state = [
        keys for owner, keys in PROFILE.by_owner.items()
        if owner not in {
            "raa_misr_waqf", "raa_alqitr_waqf", "raa_yasr_waqf",
            "raa_asr_waqf", "raa_wanuthur_waqf",
            "raa_wizra_ukhra", "raa_hasirat_suduruhum",
        }
    ]

    assert sum(map(len, all_state)) == len(set().union(*all_state))


@lru_cache(maxsize=None)
def _score(verse: VerseRef):
    package = recitation(Riwayah.WARSH)
    words = package.words(verse)
    return package.build(package.read(Script.UTHMANI, verse, words)).score


def _structural_trigger(slots, at: int) -> bool:
    if any(
        slot.letter in {L.KHA, L.SAD, L.DAD, L.TAH, L.ZAH, L.GHAIN, L.QAF}
        for slot in slots[at + 1:]
    ):
        return False
    before = slots[at - 1] if at else None
    if (
        before is not None
        and before.letter is L.YA
        and before.nucleus.joined.form is VowelForm.ABSENT
    ):
        return True
    if (
        before is not None
        and before.nucleus.joined.quality is Quality.I
        and before.onset is not Onset.WASL
    ):
        return True
    if at < 2 or before is None:
        return False
    trigger = slots[at - 2]
    return (
        before.nucleus.joined.form is VowelForm.ABSENT
        and before.letter not in {L.SAD, L.TAH, L.QAF, L.DAD, L.ZAH, L.GHAIN}
        and trigger.nucleus.joined.quality is Quality.I
        and trigger.onset is not Onset.WASL
    )


def _systematic_candidates():
    package = recitation(Riwayah.WARSH)
    verses = sorted({location.verse for location in package.corpus.entries})
    found = {"raa_fathatan": set(), "raa_damma": set()}
    for verse in verses:
        for word in _score(verse).words:
            raa = 0
            for at, slot in enumerate(word.slots):
                if slot.letter is not L.RA:
                    continue
                raa += 1
                if not _structural_trigger(word.slots, at):
                    continue
                following = word.slots[at + 1] if at + 1 < len(word.slots) else None
                if slot.nucleus.joined.quality is Quality.U:
                    found["raa_damma"].add((word.location, raa))
                elif (
                    slot.nucleus.joined.quality is Quality.A
                    and following is not None
                    and following.origin is SlotOrigin.NUNATION
                ):
                    found["raa_fathatan"].add((word.location, raa))
    return found


def test_systematic_scopes_reconcile_to_the_pinned_acceptance_counts():
    found = _systematic_candidates()
    fathatan = found["raa_fathatan"] - PROFILE.systematic_exclusions
    damma = found["raa_damma"] - PROFILE.systematic_exclusions

    assert len(found["raa_fathatan"]) == 276
    assert len(found["raa_damma"]) == 854
    assert len(fathatan) == 259
    assert len(damma) == 851


def test_fixed_lexeme_subtotals_match_the_closed_foreign_name_families():
    package = recitation(Riwayah.WARSH)

    def plain(text: str) -> str:
        return "".join(
            char for char in unicodedata.normalize("NFD", text)
            if unicodedata.category(char)[0] != "M" and char != "ـ"
        )

    families = {
        "raa_fixed_ibrahim_heavy": ("ابرهيم", 69),
        "raa_fixed_israil_heavy": ("اسراءيل", 43),
        "raa_fixed_imran_heavy": ("عمرن", 3),
    }
    for owner, (skeleton, count) in families.items():
        found = {
            (location, 1)
            for location in package.corpus.entries
            if plain(package.corpus.entries[location].text).endswith(skeleton)
        }
        assert len(found) == count
        assert PROFILE.by_owner[owner] == found

    assert (Location(10, 16, 14), 1) not in PROFILE.heavy  # عُمُراٗ
    assert (Location(35, 11, 22), 1) not in PROFILE.heavy  # مُّعَمَّرٖ


@pytest.mark.parametrize(
    ("location", "sound"),
    (
        (Location(2, 61, 32), "rˤ"),
        (Location(18, 96, 19), "rˤ"),
        (Location(20, 77, 6), "r"),
        (Location(26, 52, 5), "r"),
        (Location(54, 23, 3), "rˤ"),
        (Location(54, 33, 4), "rˤ"),
        (Location(54, 36, 5), "rˤ"),
        (Location(4, 102, 26), "r"),
        (Location(22, 13, 10), "r"),
        (Location(26, 214, 2), "r"),
        (Location(58, 22, 21), "r"),
    ),
)
def test_every_negative_register_member_keeps_its_fixed_pausal_weight(
    location, sound,
):
    result = reading(
        Site(warsh=(str(location.verse), (location.word,))),
        "warsh",
        Script.UTHMANI,
        isolated=location.word,
    )

    assert sound in result.sounds(location.word)
    assert ({"r", "rˤ"} - {sound}).isdisjoint(result.sounds(location.word))


@pytest.mark.parametrize(
    ("location", "joined_sound", "stopped_sound"),
    (
        (Location(26, 63, 11), "r", "r"),
        (Location(10, 87, 8), "rˤ", "rˤ"),
        (Location(34, 12, 10), "r", "r"),
        (Location(89, 4, 3), "r", "r"),
        (Location(11, 81, 9), "r", "rˤ"),
        (Location(54, 16, 4), "r", "r"),
    ),
)
def test_each_pausal_owner_covers_ibtidaa_wasl_and_full_sukun_waqf(
    location, joined_sound, stopped_sound,
):
    site = Site(warsh=(str(location.verse), (location.word,)))
    joined = reading(
        site,
        "warsh",
        Script.UTHMANI,
        ibtidaa=location.word,
        wasl=location.word,
    )
    stopped = reading(
        site,
        "warsh",
        Script.UTHMANI,
        isolated=location.word,
    )

    assert joined_sound in joined.sounds(location.word)
    assert stopped_sound in stopped.sounds(location.word)
