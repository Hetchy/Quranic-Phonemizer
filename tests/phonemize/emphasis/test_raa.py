from __future__ import annotations

import pytest

from quranic_phonemizer.model.address import KhilafId
from tests.support import (
    Expect,
    R,
    Site,
    VariantCase,
    assert_case,
    case_runs,
    isolated,
    joining,
    selected,
)


REGISTERS = {
    KhilafId.RAA_FIRQ_WASL: (
        (Site(hafs=("26:63", (11,))), 11, False),
    ),
    KhilafId.RAA_ALQITR_WAQF: (
        (Site(hafs=("34:12", (10,))), 10, True),
    ),
    KhilafId.RAA_MISR_WAQF: (
        (Site(hafs=("12:99", (10,))), 10, True),
        (Site(hafs=("12:21", (5,))), 5, True),
        (Site(hafs=("43:51", (10,))), 10, True),
        (Site(hafs=("10:87", (8,))), 8, True),
    ),
    KhilafId.RAA_NUTHUR_WAQF: (
        (Site(hafs=("54:16", (4,))), 4, True),
        (Site(hafs=("54:18", (6,))), 6, True),
        (Site(hafs=("54:21", (4,))), 4, True),
        (Site(hafs=("54:30", (4,))), 4, True),
        (Site(hafs=("54:37", (9,))), 9, True),
        (Site(hafs=("54:39", (3,))), 3, True),
    ),
    KhilafId.RAA_YASR_WAQF: (
        (Site(hafs=("89:4", (3,))), 3, True),
    ),
    KhilafId.RAA_ASR_WAQF: (
        (Site(hafs=("20:77", (6,))), 6, True),
        (Site(hafs=("26:52", (5,))), 5, True),
        (Site(hafs=("11:81", (9,))), 9, True),
        (Site(hafs=("15:65", (1,))), 1, True),
        (Site(hafs=("44:23", (1,))), 1, True),
    ),
}


def _weight(read, phonemes: str, weight: str) -> Expect:
    if weight == "heavy":
        return Expect(
            read=read,
            phonemes=phonemes,
            char_rules={"ر": R("tafkheem")},
            sound_rules={"rˤ": R("tafkheem")},
        )
    return Expect(
        read=read,
        phonemes=phonemes,
        char_rules={"ر": R("tarqeeq")},
        sound_rules={"r": R("tarqeeq")},
    )


def _case(
    case_id: str,
    selector: KhilafId,
    stopped: bool,
    heavy: str,
    light: str,
    default: str,
    masked: str,
    masked_weight: str,
) -> VariantCase:
    site, _, _ = REGISTERS[selector][0]
    active_read = isolated() if stopped else joining()
    masked_read = joining() if stopped else isolated()
    return VariantCase(
        id=case_id,
        site=site,
        selector=selector,
        faces={
            "heavy": _weight(active_read, heavy, "heavy"),
            "light": _weight(active_read, light, "light"),
        },
        default=default,
        masked=_weight(masked_read, masked, masked_weight),
    )


CASES = (
    # فِرْقٍ
    _case("firq", KhilafId.RAA_FIRQ_WASL, False,
          "f i rˤ q i ŋ", "f i r q i ŋ", "heavy", "f i rˤ q Q", "heavy"),
    # ٱلْقِطْرِ
    _case("alqitr", KhilafId.RAA_ALQITR_WAQF, True,
          "ʔ a l q i tˤ Q rˤ", "ʔ a l q i tˤ Q r", "light",
          "ʔ a l q i tˤ Q r i", "light"),
    # مِصْرَ
    _case("misr", KhilafId.RAA_MISR_WAQF, True,
          "m i sˤ rˤ", "m i sˤ r", "heavy", "m i sˤ rˤ aˤ", "heavy"),
    # وَنُذُرِ
    _case("wanuthur", KhilafId.RAA_NUTHUR_WAQF, True,
          "w a n u ð u rˤ", "w a n u ð u r", "heavy",
          "w a n u ð u r i", "light"),
    # يَسْرِ
    _case("yasr", KhilafId.RAA_YASR_WAQF, True,
          "j a s rˤ", "j a s r", "light", "j a s r i", "light"),
    # أَسْرِ
    _case("asr", KhilafId.RAA_ASR_WAQF, True,
          "ʔ a s rˤ", "ʔ a s r", "light", "ʔ a s r i", "light"),
)

REGISTER_CASES = tuple(
    pytest.param(
        selector,
        site,
        word,
        stopped,
        id=f"{selector.value}-{site.address('hafs').verse}-{word}",
    )
    for selector, sites in REGISTERS.items()
    for site, word, stopped in sites
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_raa_variants(run):
    assert_case(run)


@pytest.mark.parametrize(("selector", "site", "word", "stopped"), REGISTER_CASES)
def test_every_raa_register_site_accepts_both_faces(selector, site, word, stopped):
    heavy = selected(site, word, selector, "heavy", stopped=stopped)
    light = selected(site, word, selector, "light", stopped=stopped)
    assert heavy.sounds(word) != light.sounds(word)
