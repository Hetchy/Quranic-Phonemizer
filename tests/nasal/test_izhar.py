from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

SALAMUN_HIYA = Site(hafs=("97:5", (1, 2)))
QADIRUN = Site(hafs=("2:106", (19,)))

INSIDE_ONE_WORD = [
    ("6:26", 4, "wajanʔawn"),         # وَيَنْـَٔوْنَ
    ("7:25", 6, "waminha:"),          # وَمِنْهَا
    ("1:7", 3, "ʔanʕamt"),            # أَنْعَمْتَ
    ("108:2", 3, "wanħarˤ"),          # وَٱنْحَرْ
    ("17:51", 15, "fasajunɣidˤu:n"),  # فَسَيُنْغِضُونَ
    ("5:3", 12, "walmunxaˤniqaˤh"),   # وَٱلْمُنْخَنِقَةُ
]

NOON_ACROSS_A_BOUNDARY = [
    ("6:72", (1, 2), ("waʔan", "ʔaqi:mu:")),   # وَأَنْ أَقِيمُوا۟
    ("23:97", (5, 6), ("min", "hamaza:t")),    # مِنْ هَمَزَٰتِ
    ("2:227", (1, 2), ("waʔin", "ʕazamu:")),   # وَإِنْ عَزَمُوا۟
    ("22:21", (3, 4), ("min", "ħadi:dQ")),     # مِنْ حَدِيدٍ
    ("41:32", (2, 3), ("min", "ɣaˤfu:rˤ")),    # مِّنْ غَفُورٍ
    ("20:4", (2, 3), ("mim̃an", "xaˤlaqQ")),   # مِّمَّنْ خَلَقَ
]

TANWEEN_ACROSS_A_BOUNDARY = [
    ("2:45", (5, 6), ("lakabi:rˤaˤtun", "ʔilla:")),  # لَكَبِيرَةٌ إِلَّا
    ("52:15", (1, 2), ("ʔafasiħrˤun", "ha:ða:")),    # أَفَسِحْرٌ هَـٰذَآ
    ("2:18", (2, 3), ("bukmun", "ʕumj")),            # بُكْمٌ عُمْىٌ
    ("16:6", (3, 4), ("ʒama:lun", "ħi:n")),          # جَمَالٌ حِينَ
    ("16:21", (1, 2), ("ʔamwa:tun", "ɣaˤjr")),       # أَمْوَٰتٌ غَيْرُ
    ("19:3", (4, 5), ("nida:ʔan", "xaˤfijja:")),     # نِدَآءً خَفِيًّا
]


#: One site per tanween mark this file's table reaches, to say which
#: character the rule is read off.
EACH_TANWEEN_MARK = [
    ("2:45", (5, 6), "ٌ"),   # لَكَبِيرَةٌ إِلَّا
    ("19:3", (4, 5), "ً"),   # نِدَآءً خَفِيًّا
]


@pytest.mark.parametrize(("ref", "word", "expected"), INSIDE_ONE_WORD)
def test_every_throat_letter_keeps_a_written_noon_clear(ref, word, expected):
    site = Site(hafs=(ref, (word,)))
    r = reading(site, isolated=word)
    assert r.phonemes(word) == expected
    assert "izhar" in r.rules_on_char(word, "ن")
    assert r.rules_on_sound(word, "n") == {"izhar"}


@pytest.mark.parametrize(("ref", "words", "expected"), NOON_ACROSS_A_BOUNDARY)
def test_every_throat_letter_keeps_a_noon_clear_across_a_seam(
    ref, words, expected
):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected
    assert "izhar" in r.rules_on_char(first, "ن")
    assert r.rules_on_sound(first, "n") == {"izhar"}


@pytest.mark.parametrize(
    ("ref", "words", "expected"), TANWEEN_ACROSS_A_BOUNDARY
)
def test_every_throat_letter_keeps_a_tanween_noon_clear(ref, words, expected):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected
    assert r.rules_on_sound(first, "n") == {"izhar"}


@pytest.mark.parametrize(("ref", "words", "mark"), EACH_TANWEEN_MARK)
def test_the_rule_is_read_off_the_tanween_mark(ref, words, mark):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert "izhar" in r.rules_on_char(first, mark)


@for_each_riwayah(SALAMUN_HIYA, ibtidaa=1, waqf=2)
def test_a_tanween_before_a_throat_letter_keeps_its_own_noon(r):
    # سَلَـٰمٌ هِىَ
    assert r.phonemes(1) == "sala:mun"
    assert r.phonemes(2) == "hi:"
    assert "izhar" in r.rules_on_char(1, "ٌ")
    assert r.rules_on_sound(1, "n") == {"izhar"}


@for_each_riwayah(QADIRUN, ibtidaa=19, wasl=19)
def test_a_tanween_at_a_verse_end_keeps_its_noon_clear_across_the_seam(r):
    # قَدِيرٌ أَلَمْ
    assert r.phonemes(19) == "qaˤdi:rˤun"
    assert r.phonemes(20) == "ʔalam"
    assert "izhar" in r.rules_on_char(19, "ٌ")
    assert r.rules_on_sound(19, "n") == {"izhar"}
