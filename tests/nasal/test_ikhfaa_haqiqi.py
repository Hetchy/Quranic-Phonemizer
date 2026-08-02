from __future__ import annotations

import pytest

from tests.support import Site, for_each_riwayah, reading

MIN_ZULUMAT = Site(hafs=("6:63", (4, 5)))

INSIDE_ONE_WORD = [
    ("2:42", 7, "waʔaŋtum"),        # وَأَنتُمْ
    ("53:21", 4, "ʔalʔuŋθa:"),      # ٱلْأُنثَىٰ
    ("21:9", 4, "faʔaŋʒajna:hum"),  # فَأَنجَيْنَـٰهُمْ
    ("3:163", 3, "ʕiŋdQ"),          # عِندَ
    ("18:4", 1, "wajuŋðir"),        # وَيُنذِرَ
    ("15:90", 2, "ʔaŋzalna:"),      # أَنزَلْنَا
    ("16:4", 2, "ʔalʔiŋsa:n"),      # ٱلْإِنسَـٰنَ
    ("23:31", 2, "ʔaŋʃaʔna:"),      # أَنشَأْنَا
    ("7:192", 7, "jaŋsˤurˤu:n"),    # يَنصُرُونَ
    ("56:29", 2, "maŋdˤu:dQ"),      # مَّنضُودٍ
    ("37:92", 4, "taŋtˤiqu:n"),     # تَنطِقُونَ
    ("7:14", 2, "ʔaŋðˤirni:"),      # أَنظِرْنِىٓ
    ("2:3", 8, "juŋfiqu:n"),        # يُنفِقُونَ
    ("7:119", 3, "waŋqaˤlabu:"),    # وَٱنقَلَبُوا۟
    ("2:52", 3, "ʕaŋkum"),          # عَنكُم
]

TANWEEN_ACROSS_A_BOUNDARY = [
    ("20:20", (4, 5), ("ħajjatuŋ", "tasʕa:")),         # حَيَّةٌ تَسْعَىٰ
    ("3:197", (2, 3), ("qaˤli:luŋ", "θum̃")),          # قَلِيلٌ ثُمَّ
    ("18:8", (5, 6), ("sˤaˤʕi:daŋ", "ʒurˤuza:")),      # صَعِيدًا جُرُزًا
    ("78:34", (1, 2), ("wakaʔsaŋ", "diha:qaˤ:")),      # وَكَأْسًا دِهَاقًا
    ("29:57", (2, 3), ("nafsiŋ", "ða:ʔiqaˤh")),        # نَفْسٍ ذَآئِقَةُ
    ("55:52", (4, 5), ("fa:kihatiŋ", "zawʒa:n")),      # فَـٰكِهَةٍ زَوْجَانِ
    ("21:26", (4, 5), ("waladaŋ", "subQħa:nah")),      # وَلَدًا سُبْحَـٰنَهُۥ
    ("19:32", (5, 6), ("ʒabba:rˤaˤŋ", "ʃaqijja:")),    # جَبَّارًا شَقِيًّا
    ("69:6", (4, 5), ("biri:ħiŋ", "sˤaˤrˤsˤaˤrˤ")),    # بِرِيحٍ صَرْصَرٍ
    ("25:39", (1, 2), ("wakullaŋ", "dˤaˤrˤaˤbQna:")),  # وَكُلًّا ضَرَبْنَا
    ("51:53", (5, 6), ("qaˤwmuŋ", "tˤaˤ:ɣu:n")),       # قَوْمٌ طَاغُونَ
    ("4:57", (19, 20), ("ðˤillaŋ", "ðˤaˤli:la:")),     # ظِلًّا ظَلِيلًا
    ("6:86", (5, 6), ("wakullaŋ", "fadˤdˤaˤlna:")),    # وَكُلًّا فَضَّلْنَا
    ("16:117", (1, 2), ("mata:ʕuŋ", "qaˤli:l")),       # مَتَـٰعٌ قَلِيلٌ
    ("17:43", (5, 6), ("ʕuluwwaŋ", "kabi:rˤaˤ:")),     # عُلُوًّا كَبِيرًا
]


@pytest.mark.parametrize(("ref", "word", "expected"), INSIDE_ONE_WORD)
def test_every_hiding_letter_hides_a_written_noon(ref, word, expected):
    site = Site(hafs=(ref, (word,)))
    assert reading(site, isolated=word).phonemes(word) == expected


@pytest.mark.parametrize(
    ("ref", "words", "expected"), TANWEEN_ACROSS_A_BOUNDARY
)
def test_every_hiding_letter_hides_a_tanween_noon(ref, words, expected):
    first, last = words
    r = reading(Site(hafs=(ref, words)), ibtidaa=first, waqf=last)
    assert (r.phonemes(first), r.phonemes(last)) == expected


@for_each_riwayah(MIN_ZULUMAT, ibtidaa=4, waqf=5)
def test_a_noon_is_hidden_when_the_hiding_letter_starts_a_word(r):
    # مِّن ظُلُمَـٰتِ
    assert r.phonemes(4) == "miŋ"
    assert r.phonemes(5) == "ðˤuluma:t"
