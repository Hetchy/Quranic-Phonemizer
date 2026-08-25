"""The authored Warsh hamza-meeting register and its closed partitions."""

from collections import Counter

from quranic_phonemizer.model.address import Location
from quranic_phonemizer.riwayat.warsh.hamza_meetings import meeting_rows


def test_the_one_word_register_is_the_documented_sixty():
    rows = [row for row in meeting_rows() if row.scope == "one_word"]
    assert len(rows) == 60
    assert Counter((row.first.name, row.second.name) for row in rows) == Counter({
        ("A", "A"): 25,
        ("A", "I"): 32,
        ("A", "U"): 3,
    })
    assert Counter(row.owner for row in rows) == Counter({
        "hamza_dhat_fath": 20,
        "fixed_tashil": 40,
    })


def test_the_across_word_register_is_the_documented_156():
    rows = [row for row in meeting_rows() if row.scope != "one_word"]
    assert len(rows) == 156
    assert Counter((row.first.name, row.second.name) for row in rows) == Counter({
        ("A", "A"): 30,
        ("I", "I"): 37,
        ("U", "U"): 1,
        ("A", "I"): 19,
        ("A", "U"): 1,
        ("I", "A"): 29,
        ("U", "A"): 13,
        ("U", "I"): 26,
    })
    assert Counter(row.scope for row in rows) == Counter({
        "joined_words": 154,
        "joined_ayahs": 2,
    })


def test_every_authored_exception_is_closed():
    by_exception = {
        name: {row.canonical for row in meeting_rows() if row.exception == name}
        for name in ("aimma", "aajami", "triple", "jaa_aal", "kasr_yaa")
    }
    assert by_exception == {
        "aimma": {
            Location(9, 12, 11), Location(21, 73, 2), Location(28, 5, 10),
            Location(28, 41, 2), Location(32, 24, 3),
        },
        "aajami": {Location(41, 44, 9)},
        "triple": {
            Location(7, 123, 3), Location(20, 71, 2),
            Location(26, 49, 2), Location(43, 58, 2),
        },
        "jaa_aal": {Location(15, 61, 3), Location(54, 41, 3)},
        "kasr_yaa": {Location(2, 31, 13), Location(24, 33, 33)},
    }


def test_every_row_carries_the_machine_contract():
    for row in meeting_rows():
        assert row.source
        assert row.canonical
        assert row.first.name in {"A", "I", "U"}
        assert row.second.name in {"A", "I", "U"}
        assert row.scope in {"one_word", "joined_words", "joined_ayahs"}
        assert row.owner
        assert row.exception in {None, "aimma", "aajami", "triple", "jaa_aal", "kasr_yaa"}
