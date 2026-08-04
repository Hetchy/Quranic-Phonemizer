from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

TA_SEEN_MEEM = Site(hafs=("26:1", (1,)))
AZEEMUN = Site(hafs=("2:7", (12,)))

NOON_ACROSS_A_BOUNDARY = [
    ("3:74", (3, 4), ("ma", "j̃aʃa:ʔ")),           # مَن يَشَآءُ
    ("7:110", (2, 3), ("ʔa", "j̃uxriʒakum")),      # أَن يُخْرِجَكُم
    ("21:9", (5, 6), ("wama", "ñaʃa:ʔ")),          # وَمَن نَّشَآءُ
    ("16:4", (3, 4), ("mi", "ñutˤQfah")),          # مِن نُّطْفَةٍ
    ("3:60", (5, 6), ("taku", "m̃in")),            # تَكُن مِّنَ
    ("3:158", (1, 2), ("walaʔi", "m̃uttum")),      # وَلَئِن مُّتُّمْ
    ("14:16", (1, 2), ("mi", "w̃arˤaˤ:ʔih")),      # مِّن وَرَآئِهِۦ
    ("26:85", (2, 3), ("mi", "w̃arˤaˤθah")),       # مِن وَرَثَةِ
]

TANWEEN_ACROSS_A_BOUNDARY = [
    ("2:179", (4, 5), ("ħaja:tu", "j̃a:ʔuli:")),        # حَيَوٰةٌ يَـٰٓأُو۟لِى
    ("6:105", (7, 8), ("liqaˤwmi", "j̃aʕlamu:n")),      # لِقَوْمٍ يَعْلَمُونَ
    ("19:41", (7, 8), ("sˤiddi:qaˤ", "ñabijja:")),      # صِدِّيقًا نَّبِيًّا
    ("25:51", (6, 7), ("qaˤrˤjati", "ñaði:rˤaˤ:")),     # قَرْيَةٍ نَّذِيرًا
    ("2:5", (3, 4), ("huda", "m̃in")),                  # هُدًى مِّن
    ("3:51", (7, 8), ("sˤirˤaˤ:tˤu", "m̃ustaqi:m")),    # صِرَٰطٌ مُّسْتَقِيمٌ
    ("3:34", (4, 5), ("baʕdˤi", "w̃alˤlˤaˤ:h")),        # بَعْضٍ وَٱللَّهُ
    ("3:46", (5, 6), ("wakahla", "w̃amin")),            # وَكَهْلًا وَمِنَ
]


#: One site per tanween mark this file's table reaches, to say which
#: character the rule is read off.
EACH_TANWEEN_MARK = [
    ("2:179", (4, 5), "ٌ"),   # حَيَوٰةٌ يَـٰٓأُو۟لِى
    ("2:5", (3, 4), "ً"),     # هُدًى مِّن
    ("6:105", (7, 8), "ٍ"),   # لِقَوْمٍ يَعْلَمُونَ
]


@pytest.mark.parametrize(("ref", "words", "expected"), NOON_ACROSS_A_BOUNDARY)
def test_a_quiescent_noon_merges_with_a_hum_into_each_letter(
    ref, words, expected
):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected
    assert "idgham_bi_ghunnah" in r.rules_on_char(first, "ن")
    assert r.rules_on_sound(last, r.sounds(last)[0]) == {"idgham_bi_ghunnah"}


@pytest.mark.parametrize(
    ("ref", "words", "expected"), TANWEEN_ACROSS_A_BOUNDARY
)
def test_a_tanween_merges_with_a_hum_into_each_letter(ref, words, expected):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected
    assert r.rules_on_sound(last, r.sounds(last)[0]) == {"idgham_bi_ghunnah"}


@pytest.mark.parametrize(("ref", "words", "mark"), EACH_TANWEEN_MARK)
def test_the_rule_is_read_off_the_tanween_mark(ref, words, mark):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert "idgham_bi_ghunnah" in r.rules_on_char(first, mark)


@for_each_riwayah(TA_SEEN_MEEM, isolated=1)
def test_the_noon_of_a_letter_name_merges_into_the_next_name(r):
    # طسٓمٓ
    assert r.phonemes(1) == "tˤaˤ:si:m̃i:m"
    # the noon is spelled by the name of the seen, so no written ن carries it
    assert r.rules_on_sound(1, "m̃") == {"idgham_bi_ghunnah"}


@for_each_riwayah(AZEEMUN, ibtidaa=12, wasl=12)
def test_a_tanween_at_a_verse_end_merges_into_the_next_verse(r):
    # عَظِيمٌ وَمِنَ
    assert r.phonemes(12) == "ʕaðˤi:mu"
    assert r.phonemes(13) == "w̃amina"
    assert "idgham_bi_ghunnah" in r.rules_on_char(12, "ٌ")
    assert r.rules_on_sound(13, "w̃") == {"idgham_bi_ghunnah"}
