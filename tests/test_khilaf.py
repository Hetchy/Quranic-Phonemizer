from __future__ import annotations

import pytest

from quranic_phonemizer import Phonemizer, available_variants
from quranic_phonemizer.model.canon import CanonLetter, Onset, Quality, Rule
from quranic_phonemizer.model.inscription import SilenceReason
from tests.support import KhilafId, Option, Site, VariantSelection, reading

FIRQ = Site(hafs=("26:63", (11,)))
ALQITR = Site(hafs=("34:12", (10,)))
MISR_YUSUF_1 = Site(hafs=("12:99", (10,)))
MISR_YUSUF_2 = Site(hafs=("12:21", (5,)))
MISR_ZUKHRUF = Site(hafs=("43:51", (10,)))
BIMISR = Site(hafs=("10:87", (8,)))
NUTHUR_16 = Site(hafs=("54:16", (4,)))
NUTHUR_18 = Site(hafs=("54:18", (6,)))
NUTHUR_21 = Site(hafs=("54:21", (4,)))
NUTHUR_30 = Site(hafs=("54:30", (4,)))
NUTHUR_37 = Site(hafs=("54:37", (9,)))
NUTHUR_39 = Site(hafs=("54:39", (3,)))
BINUTHUR_23 = Site(hafs=("54:23", (3,)))
BINUTHUR_33 = Site(hafs=("54:33", (4,)))
BINUTHUR_36 = Site(hafs=("54:36", (5,)))
YASR = Site(hafs=("89:4", (3,)))
ASR_TAHA = Site(hafs=("20:77", (6,)))
ASR_SHUARAA = Site(hafs=("26:52", (5,)))
FAASR_HUD = Site(hafs=("11:81", (9,)))
FAASR_HIJR = Site(hafs=("15:65", (1,)))
FAASR_DUKHAN = Site(hafs=("44:23", (1,)))

AATANI = Site(hafs=("27:36", (8,)))
DAAF = Site(hafs=("30:54", (5, 10, 17)))

YABSUT = Site(hafs=("2:245", (14,)))
BASTAH = Site(hafs=("7:69", (22,)))
AL_MUSAYTIRUN = Site(hafs=("52:37", (7,)))
BIMUSAYTIR = Site(hafs=("88:22", (3,)))

YA_SEEN = Site(hafs=("36:1", (1,)))
NOON = Site(hafs=("68:1", (1,)))

AL_DHAKRAYN_1 = Site(hafs=("6:143", (10,)))
AL_DHAKRAYN_2 = Site(hafs=("6:144", (8,)))
AL_AAN_1 = Site(hafs=("10:51", (7,)))
AL_AAN_2 = Site(hafs=("10:91", (1,)))
AL_LAH_1 = Site(hafs=("10:59", (14,)))
AL_LAH_2 = Site(hafs=("27:59", (9,)))

MIN_BADI = Site(hafs=("2:56", (3, 4)))
SUMMUN_BUKMUN = Site(hafs=("2:18", (1, 2)))
HUM_BIMUMININ = Site(hafs=("2:8", (10, 11)))

IWAJA_SAKT = Site(hafs=("18:1", (11,)))
MARQADINA_SAKT = Site(hafs=("36:52", (6, 7)))
MAN_RAQIN_SAKT = Site(hafs=("75:27", (2, 3)))
BAL_RANA_SAKT = Site(hafs=("83:14", (2, 3)))

SITES_WITH_SAKT_SEEN = (
    (IWAJA_SAKT, 11),
    (MARQADINA_SAKT, 6),
    (MAN_RAQIN_SAKT, 2),
    (BAL_RANA_SAKT, 2),
)

VARIANTS = {
    "seen_sad_yabsut": (["seen", "saad"], "seen"),
    "seen_sad_bastah": (["seen", "saad"], "seen"),
    "seen_sad_al_musaytirun": (["saad", "seen"], "saad"),
    "seen_sad_bimusaytir": (["saad", "seen"], "saad"),
    "iqlab_nasal": (["assimilated", "bilabial"], "assimilated"),
    "ikhfaa_shafawi_nasal": (["assimilated", "bilabial"], "assimilated"),
    "raa_firq_wasl": (["heavy", "light"], "heavy"),
    "raa_alqitr_waqf": (["light", "heavy"], "light"),
    "raa_misr_waqf": (["heavy", "light"], "heavy"),
    "raa_nuthur_waqf": (["heavy", "light"], "heavy"),
    "raa_yasr_waqf": (["light", "heavy"], "light"),
    "raa_asr_waqf": (["light", "heavy"], "light"),
    "daaf_haraka": (["fatha", "damma"], "fatha"),
    "yaa_aatani_waqf": (["hadhf", "ithbat"], "hadhf"),
    "noon_yaseen_wasl": (["izhar", "idgham"], "izhar"),
    "madd_lazim_tasheel": (["madd_lazim", "tasheel"], "madd_lazim"),
}

RAA_CASES = (
    (KhilafId.RAA_FIRQ_WASL, FIRQ, 11, False, "firˤqiŋ", "firqiŋ"),
    (KhilafId.RAA_ALQITR_WAQF, ALQITR, 10, True, "ʔalqitˤQrˤ", "ʔalqitˤQr"),
    (KhilafId.RAA_MISR_WAQF, MISR_YUSUF_1, 10, True, "misˤrˤ", "misˤr"),
    (KhilafId.RAA_MISR_WAQF, MISR_YUSUF_2, 5, True, "misˤrˤ", "misˤr"),
    (KhilafId.RAA_MISR_WAQF, MISR_ZUKHRUF, 10, True, "misˤrˤ", "misˤr"),
    (KhilafId.RAA_MISR_WAQF, BIMISR, 8, True, "bimisˤrˤ", "bimisˤr"),
    (KhilafId.RAA_NUTHUR_WAQF, NUTHUR_16, 4, True, "wanuðurˤ", "wanuður"),
    (KhilafId.RAA_NUTHUR_WAQF, NUTHUR_18, 6, True, "wanuðurˤ", "wanuður"),
    (KhilafId.RAA_NUTHUR_WAQF, NUTHUR_21, 4, True, "wanuðurˤ", "wanuður"),
    (KhilafId.RAA_NUTHUR_WAQF, NUTHUR_30, 4, True, "wanuðurˤ", "wanuður"),
    (KhilafId.RAA_NUTHUR_WAQF, NUTHUR_37, 9, True, "wanuðurˤ", "wanuður"),
    (KhilafId.RAA_NUTHUR_WAQF, NUTHUR_39, 3, True, "wanuðurˤ", "wanuður"),
    (KhilafId.RAA_NUTHUR_WAQF, BINUTHUR_23, 3, True, "biñuðurˤ", "biñuður"),
    (KhilafId.RAA_NUTHUR_WAQF, BINUTHUR_33, 4, True, "biñuðurˤ", "biñuður"),
    (KhilafId.RAA_NUTHUR_WAQF, BINUTHUR_36, 5, True, "biñuðurˤ", "biñuður"),
    (KhilafId.RAA_YASR_WAQF, YASR, 3, True, "jasrˤ", "jasr"),
    (KhilafId.RAA_ASR_WAQF, ASR_TAHA, 6, True, "ʔasrˤ", "ʔasr"),
    (KhilafId.RAA_ASR_WAQF, ASR_SHUARAA, 5, True, "ʔasrˤ", "ʔasr"),
    (KhilafId.RAA_ASR_WAQF, FAASR_HUD, 9, True, "faʔasrˤ", "faʔasr"),
    (KhilafId.RAA_ASR_WAQF, FAASR_HIJR, 1, True, "faʔasrˤ", "faʔasr"),
    (KhilafId.RAA_ASR_WAQF, FAASR_DUKHAN, 1, True, "faʔasrˤ", "faʔasr"),
)

SEEN_SAD_CASES = (
    (KhilafId.SEEN_SAD_YABSUT, YABSUT, 14, 3, "wajabQsutˤQ", "wajabQsˤutˤQ"),
    (KhilafId.SEEN_SAD_BASTAH, BASTAH, 22, 1, "bastˤaˤh", "basˤtˤaˤh"),
    (KhilafId.SEEN_SAD_AL_MUSAYTIRUN, AL_MUSAYTIRUN, 7, 3,
     "ʔalmusajtˤirˤu:n", "ʔalmusˤaˤjtˤirˤu:n"),
    (KhilafId.SEEN_SAD_BIMUSAYTIR, BIMUSAYTIR, 3, 2,
     "bimusajtˤir", "bimusˤaˤjtˤir"),
)

MADD_CASES = (
    (AL_DHAKRAYN_1, 10, "ʔa:ððakarˤaˤjn", "ʔaʔaððakarˤaˤjn"),
    (AL_DHAKRAYN_2, 8, "ʔa:ððakarˤaˤjn", "ʔaʔaððakarˤaˤjn"),
    (AL_AAN_1, 7, "ʔa:lʔa:n", "ʔaʔalʔa:n"),
    (AL_AAN_2, 1, "ʔa:lʔa:n", "ʔaʔalʔa:n"),
    (AL_LAH_1, 14, "ʔa:lˤlˤaˤ:h", "ʔaʔalˤlˤaˤ:h"),
    (AL_LAH_2, 9, "ʔa:lˤlˤaˤ:h", "ʔaʔalˤlˤaˤ:h"),
)

NASAL_CASES = (
    (KhilafId.IQLAB_NASAL, MIN_BADI, 3, 4, "miŋ", "mim̃", "iqlab"),
    (KhilafId.IQLAB_NASAL, SUMMUN_BUKMUN, 1, 2,
     "sˤum̃uŋ", "sˤum̃um̃", "iqlab"),
    (KhilafId.IKHFAA_SHAFAWI_NASAL, HUM_BIMUMININ, 10, 11,
     "huŋ", "hum̃", "ikhfaa_shafawi"),
)


def _selection(khilaf: KhilafId, option: str) -> VariantSelection:
    return VariantSelection((Option(khilaf, option),))


def _at(site, word, khilaf, option, *, stopped=True, extra=None):
    boundary = {"isolated": word} if stopped else {"ibtidaa": word, "wasl": word}
    kwargs = {"selection": _selection(khilaf, option), **boundary}
    if extra is not None:
        kwargs["extra_phonemes"] = extra
    return reading(site, **kwargs)


def _rules(result) -> set[Rule]:
    return {occurrence.rule for occurrence in result.performance.occurrences}


def test_the_public_catalogue_and_resolved_defaults_are_scalar():
    # بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ
    expected = {
        name: {"options": options, "default": default}
        for name, (options, default) in VARIANTS.items()
    }
    assert available_variants("hafs") == expected
    resolved = Phonemizer().phonemize("1:1").variant
    assert resolved == {name: default for name, (_, default) in VARIANTS.items()}
    assert "imala_quality" not in resolved


@pytest.mark.parametrize(
    ("khilaf", "site", "word", "stopped", "heavy", "light"), RAA_CASES
)
def test_every_raa_form_has_both_weights_and_the_matching_rule(
    khilaf, site, word, stopped, heavy, light
):
    # فِرْقٍ وَٱلْقِطْرِ وَمِصْرَ وَبِمِصْرَ وَنُذُرِ وَيَسْرِ وَأَسْرِ وَفَأَسْرِ
    thick = _at(site, word, khilaf, "heavy", stopped=stopped)
    thin = _at(site, word, khilaf, "light", stopped=stopped)
    assert thick.phonemes(word) == heavy
    assert thin.phonemes(word) == light
    assert "tafkheem" in thick.rules_on_char(word, "ر")
    assert "tarqeeq" in thin.rules_on_char(word, "ر")
    assert "tafkheem" in thick.rules_on_sound(word, "rˤ")
    assert "tarqeeq" in thin.rules_on_sound(word, "r")


@pytest.mark.parametrize(
    ("khilaf", "site", "word", "stopped", "heavy", "light"), RAA_CASES
)
def test_every_raa_form_uses_its_default_only_at_its_named_junction(
    khilaf, site, word, stopped, heavy, light
):
    # فِرْقٍ وَٱلْقِطْرِ وَمِصْرَ وَبِمِصْرَ وَنُذُرِ وَيَسْرِ وَأَسْرِ وَفَأَسْرِ
    boundary = {"isolated": word} if stopped else {"ibtidaa": word, "wasl": word}
    default = reading(site, **boundary)
    expected = heavy if VARIANTS[khilaf.value][1] == "heavy" else light
    assert default.phonemes(word) == expected
    other_heavy = _at(site, word, khilaf, "heavy", stopped=not stopped)
    other_light = _at(site, word, khilaf, "light", stopped=not stopped)
    assert other_heavy.phonemes(word) == other_light.phonemes(word)


def test_aatani_keeps_or_drops_the_final_yaa_only_at_waqf():
    # ءَاتَىٰنِۦَ
    hadhf = _at(AATANI, 8, KhilafId.YAA_AATANI_WAQF, "hadhf")
    ithbat = _at(AATANI, 8, KhilafId.YAA_AATANI_WAQF, "ithbat")
    assert hadhf.phonemes(8) == "ʔa:ta:n"
    assert ithbat.phonemes(8) == "ʔa:ta:ni:"
    joined_hadhf = _at(
        AATANI, 8, KhilafId.YAA_AATANI_WAQF, "hadhf", stopped=False
    )
    joined_ithbat = _at(
        AATANI, 8, KhilafId.YAA_AATANI_WAQF, "ithbat", stopped=False
    )
    assert joined_hadhf.phonemes(8) == joined_ithbat.phonemes(8)


def test_aatani_hadhf_stops_on_the_noon_and_lengthens_before_it():
    """The yaa is written but absent at the pause, so the noon is the letter
    the stop silences and the `aa` before it is aridah, not tabii -- the same
    shape as `لِلَّهِ`, whose written last letter is also the one stopped on.
    """
    # ءَاتَىٰنِۦَ
    hadhf = _at(AATANI, 8, KhilafId.YAA_AATANI_WAQF, "hadhf")
    assert Rule.MADD_ARID_LISSUKUN in _rules(hadhf)
    assert hadhf.rules_on_sound(8, "a:") >= {"madd_arid_lissukun"}


def test_the_omitted_yaa_names_no_rule_of_its_own():
    """Leaving the yaa off is the variant's outcome, not a rule: the letter is
    silenced for a variant reason, and only the harakat it leaves unsaid -- the
    noon's kasra and the yaa's own fatha -- drop under waqf_diacritic_drop."""
    # ءَاتَىٰنِۦَ
    assert not any(
        rule.value.startswith("waqf_glide") for rule in Rule
    )
    hadhf = _at(AATANI, 8, KhilafId.YAA_AATANI_WAQF, "hadhf")
    assert hadhf.phonemes(8) == "ʔa:ta:n"
    selection = hadhf.performance.selection
    assert selection.chosen(KhilafId.YAA_AATANI_WAQF) == "hadhf"
    assert hadhf.silent(8) == {"ۧ", "َ", "ِ"}
    word = {slot.id for slot in hadhf.score.words[7].slots}
    drops = [
        o for o in hadhf.performance.occurrences
        if o.rule is Rule.WAQF_DIACRITIC_DROP and o.subjects[0] in word
    ]
    assert len(drops) == 2
    assert len({o.id for o in drops}) == 2
    # the yaa letter itself is silenced for a variant reason, naming no rule
    glide = [
        o for o in hadhf.performance.occurrences
        if o.rule is SilenceReason.VARIANT and o.subjects[0] in word
    ]
    assert len(glide) == 1


def test_the_kept_yaa_leaves_only_its_own_haraka_dropped():
    # ءَاتَىٰنِۦَ
    ithbat = _at(AATANI, 8, KhilafId.YAA_AATANI_WAQF, "ithbat")
    assert ithbat.silent(8) == {"َ"}
    drops = [
        o for o in ithbat.performance.occurrences
        if o.rule is Rule.WAQF_DIACRITIC_DROP
        and o.subjects[0] in {s.id for s in ithbat.score.words[7].slots}
    ]
    assert len(drops) == 1


@pytest.mark.parametrize(
    ("word", "fatha", "damma"),
    ((5, "dˤaˤʕf", "dˤuʕf"), (10, "dˤaˤʕf", "dˤuʕf"),
     (17, "dˤaˤʕfa:", "dˤuʕfa:")),
)
def test_daaf_haraka_changes_all_three_scores_and_phonemes(word, fatha, damma):
    # ضَعْفٍ وَضَعْفًا وَضَعْفٍ
    opened = _at(DAAF, word, KhilafId.DAAF_HARAKA, "fatha")
    rounded = _at(DAAF, word, KhilafId.DAAF_HARAKA, "damma")
    assert opened.score.words[word - 1].slots[0].nucleus.quality is Quality.A
    assert rounded.score.words[word - 1].slots[0].nucleus.quality is Quality.U
    assert opened.phonemes(word) == fatha
    assert rounded.phonemes(word) == damma


@pytest.mark.parametrize(
    ("khilaf", "site", "word", "slot", "seen", "saad"), SEEN_SAD_CASES
)
def test_each_seen_saad_word_changes_score_sound_and_tafkheem(
    khilaf, site, word, slot, seen, saad
):
    # يَبْصُطُ وَبَصْطَةً وَٱلْمُصَيْطِرُونَ وَبِمُصَيْطِرٍ
    plain = _at(site, word, khilaf, "seen")
    emphatic = _at(site, word, khilaf, "saad")
    assert plain.score.words[word - 1].slots[slot].letter is CanonLetter.SEEN
    assert emphatic.score.words[word - 1].slots[slot].letter is CanonLetter.SAD
    assert plain.phonemes(word) == seen
    assert emphatic.phonemes(word) == saad
    assert "tafkheem" not in plain.rules_on_sound(word, "s")
    assert "tafkheem" in emphatic.rules_on_sound(word, "sˤ")


@pytest.mark.parametrize(
    ("khilaf", "site", "word", "slot", "seen", "saad"), SEEN_SAD_CASES
)
def test_each_seen_saad_word_uses_the_published_default(
    khilaf, site, word, slot, seen, saad
):
    # يَبْصُطُ وَبَصْطَةً وَٱلْمُصَيْطِرُونَ وَبِمُصَيْطِرٍ
    result = reading(site, isolated=word)
    expected = saad if VARIANTS[khilaf.value][1] == "saad" else seen
    assert result.phonemes(word) == expected


@pytest.mark.parametrize(("site", "word"), SITES_WITH_SAKT_SEEN)
def test_small_seen_at_sakt_sites_is_not_a_seen_saad_choice(site, word):
    # عِوَجَاۜ وَمَرْقَدِنَاۜ وَمَنْۜ رَاقٍ وَبَلْۜ رَانَ
    first, last = site.address("hafs").words[0], site.address("hafs").words[-1]
    plain = reading(site, ibtidaa=first, waqf=last)
    picked = reading(
        site,
        selection=_selection(KhilafId.SEEN_SAD_YABSUT, "saad"),
        ibtidaa=first,
        waqf=last,
    )
    assert picked.phonemes(word) == plain.phonemes(word)
    assert picked.score.words[word - 1].slots == plain.score.words[word - 1].slots


@pytest.mark.parametrize(
    ("khilaf", "site", "word", "last", "assimilated", "bilabial", "rule"),
    NASAL_CASES,
)
def test_nasal_place_choices_change_only_the_nasal_realization(
    khilaf, site, word, last, assimilated, bilabial, rule
):
    # مِّن بَعْدِ وَصُمٌّ بُكْمٌ وَهُم بِمُؤْمِنِينَ
    common = {"ibtidaa": word, "waqf": last}
    generic = reading(site, selection=_selection(khilaf, "assimilated"), **common)
    lips = reading(site, selection=_selection(khilaf, "bilabial"), **common)
    assert generic.phonemes(word) == assimilated
    assert lips.phonemes(word) == bilabial
    assert generic.source_of(rule) == lips.source_of(rule)
    assert generic.host_of(rule) is None and lips.host_of(rule) is None
    generic_occurrence = next(o for o in generic.performance.occurrences if o.rule.value == rule)
    lips_occurrence = next(o for o in lips.performance.occurrences if o.rule.value == rule)
    assert generic_occurrence.subjects == lips_occurrence.subjects
    assert generic_occurrence.context == lips_occurrence.context


def test_selecting_one_nasal_point_leaves_the_other_at_default():
    # مِّن بَعْدِ وَهُم بِمُؤْمِنِينَ
    iqlab = reading(
        HUM_BIMUMININ,
        selection=_selection(KhilafId.IQLAB_NASAL, "bilabial"),
        ibtidaa=10,
        waqf=11,
    )
    shafawi = reading(
        MIN_BADI,
        selection=_selection(KhilafId.IKHFAA_SHAFAWI_NASAL, "bilabial"),
        ibtidaa=3,
        waqf=4,
    )
    assert iqlab.phonemes(10) == "huŋ"
    assert shafawi.phonemes(3) == "miŋ"


@pytest.mark.parametrize(
    ("site", "clear_opening", "clear_next", "merged_opening", "merged_next"),
    ((YA_SEEN, "ja:si:n", "walqurˤʔa:ni", "ja:si:", "w̃alqurˤʔa:ni"),
     (NOON, "nu:n", "walqaˤlami", "nu:", "w̃alqaˤlami")),
)
def test_noon_yaseen_wasl_selects_izhar_or_idgham_with_ownership(
    site, clear_opening, clear_next, merged_opening, merged_next
):
    # يسٓ وَٱلْقُرْءَانِ وَنٓ وَٱلْقَلَمِ
    clear = _at(site, 1, KhilafId.NOON_YASEEN_WASL, "izhar", stopped=False)
    merged = _at(site, 1, KhilafId.NOON_YASEEN_WASL, "idgham", stopped=False)
    assert (clear.phonemes(1), clear.phonemes(2)) == (clear_opening, clear_next)
    assert (merged.phonemes(1), merged.phonemes(2)) == (
        merged_opening, merged_next
    )
    assert Rule.IZHAR in _rules(clear)
    assert Rule.IDGHAM_BI_GHUNNAH in _rules(merged)
    assert merged.host_of("idgham_bi_ghunnah") == "و"
    assert merged.rules_on_sound(2, merged.sounds(2)[0]) == {
        "idgham_bi_ghunnah"
    }


@pytest.mark.parametrize(("site", "expected"), ((YA_SEEN, "ja:si:n"), (NOON, "nu:n")))
def test_noon_yaseen_idgham_never_crosses_a_waqf(site, expected):
    # يسٓ وَنٓ
    result = _at(site, 1, KhilafId.NOON_YASEEN_WASL, "idgham")
    assert result.phonemes(1) == expected
    assert Rule.IDGHAM_BI_GHUNNAH not in _rules(result)
    # A stop leaves the noon closing the opening to its own plain articulation,
    # which is the reading the idgham would otherwise have replaced.
    assert result.rules_on_sound(1, result.sounds(1)[-1]) == {"izhar"}


@pytest.mark.parametrize(("site", "word", "madd", "tasheel"), MADD_CASES)
def test_all_six_madd_lazim_sites_take_either_canonical_structure(
    site, word, madd, tasheel
):
    # ءَآلذَّكَرَيْنِ وَءَآلْـَٰٔنَ وَءَآللَّهُ
    long_reading = _at(site, word, KhilafId.MADD_LAZIM_TASHEEL, "madd_lazim")
    eased_reading = _at(site, word, KhilafId.MADD_LAZIM_TASHEEL, "tasheel")
    assert long_reading.phonemes(word) == madd
    assert eased_reading.phonemes(word) == tasheel
    assert long_reading.score.words[word - 1].slots[0].nucleus.is_long
    eased = eased_reading.score.words[word - 1].slots
    assert eased[0].nucleus.is_short and eased[1].onset is Onset.TASHIL
    assert Rule.MADD_LAZIM in _rules(long_reading)
    assert Rule.TASHIL in _rules(eased_reading)
    assert Rule.MADD_LAZIM not in _rules(eased_reading)


@pytest.mark.parametrize(("site", "word", "madd", "tasheel"), MADD_CASES)
def test_madd_lazim_tasheel_choice_is_unchanged_by_waqf_or_wasl(
    site, word, madd, tasheel
):
    # ءَآلذَّكَرَيْنِ وَءَآلْـَٰٔنَ وَءَآللَّهُ
    for stopped in (True, False):
        long_reading = _at(
            site, word, KhilafId.MADD_LAZIM_TASHEEL, "madd_lazim",
            stopped=stopped,
        )
        eased_reading = _at(
            site, word, KhilafId.MADD_LAZIM_TASHEEL, "tasheel",
            stopped=stopped,
        )
        assert Rule.MADD_LAZIM in _rules(long_reading)
        assert Rule.TASHIL in _rules(eased_reading)


def test_tasheel_keeps_the_article_lam_assimilated_in_al_dhakrayn():
    # ءَآلذَّكَرَيْنِ
    result = _at(
        AL_DHAKRAYN_1, 10, KhilafId.MADD_LAZIM_TASHEEL, "tasheel"
    )
    assert result.phonemes(10) == "ʔaʔaððakarˤaˤjn"
    assert "l" not in result.phonemes(10)
    assert "lam_shamsiyyah" in result.rules_on_char(10, "ل")
    assert result.rules_on_sound(10, "ðð") == {"lam_shamsiyyah"}


def test_tasheel_extra_phoneme_only_changes_the_eased_hamza_token():
    # ءَآلْـَٰٔنَ
    plain = _at(AL_AAN_1, 7, KhilafId.MADD_LAZIM_TASHEEL, "tasheel", extra=())
    extra = _at(
        AL_AAN_1, 7, KhilafId.MADD_LAZIM_TASHEEL, "tasheel",
        extra=("tashil",),
    )
    assert plain.phonemes(7) == "ʔaʔalʔa:n"
    assert extra.phonemes(7) == "ʔaʔ̞alʔa:n"
    assert plain.rules_on_char(7, "ا") >= {"tashil"}
    assert extra.rules_on_sound(7, "ʔ̞") == {"tashil"}


@pytest.mark.parametrize(
    "removed", ("raa_tafkheem", "yaa_ithbat", "seen_sad", "nucleus_vowel")
)
def test_removed_aggregate_ids_are_rejected(removed):
    # فِرْقٍ وَءَاتَىٰنِۦَ وَيَبْصُطُ وَضَعْفٍ
    with pytest.raises(ValueError):
        Phonemizer(variants={removed: "unused"})


def test_nested_and_duplicate_scalar_selections_are_rejected():
    # مِصْرَ وَبِمِصْرَ وَضَعْفٍ
    with pytest.raises(TypeError, match="scalar strings"):
        Phonemizer(variants={"raa_misr_waqf": {"misr": "light"}})
    with pytest.raises(TypeError):
        Option(KhilafId.RAA_MISR_WAQF, "light", "misr")
    duplicate = VariantSelection(
        (Option(KhilafId.DAAF_HARAKA, "fatha"),
         Option(KhilafId.DAAF_HARAKA, "damma"))
    )
    with pytest.raises(ValueError, match="more than one"):
        reading(DAAF, selection=duplicate, isolated=5)


def test_invalid_scalar_choice_is_rejected_before_phonemizing():
    # ضَعْفٍ
    with pytest.raises(ValueError, match="not an option"):
        Phonemizer(variants={"daaf_haraka": "kasra"})
