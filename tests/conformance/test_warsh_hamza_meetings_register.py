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


def test_the_across_word_register_is_the_documented_154():
    rows = [row for row in meeting_rows() if row.scope != "one_word"]
    assert len(rows) == 154
    assert Counter((row.first.name, row.second.name) for row in rows) == Counter({
        ("A", "A"): 30,
        ("I", "I"): 35,
        ("U", "U"): 1,
        ("A", "I"): 19,
        ("A", "U"): 1,
        ("I", "A"): 29,
        ("U", "A"): 13,
        ("U", "I"): 26,
    })
    assert Counter(row.scope for row in rows) == Counter({
        "joined_words": 152,
        "joined_ayahs": 2,
    })


def test_long_vowels_after_qata_are_not_across_word_meetings():
    sources = {row.source for row in meeting_rows() if row.scope != "one_word"}
    assert not sources & {
        "9:64:13",
        "11:69:3",
        "12:16:2",
        "12:38:4",
        "30:9:7",
        "71:6:4",
    }


def test_the_two_joined_ayah_rows_are_exact_and_none_crosses_a_surah():
    across = [row for row in meeting_rows() if row.scope != "one_word"]
    joined_ayahs = {
        (row.previous, row.canonical, row.source, row.first.name, row.second.name)
        for row in across if row.scope == "joined_ayahs"
    }
    assert joined_ayahs == {
        (Location(14, 27, 18), Location(14, 28, 1), "14:30:1", "U", "A"),
        (Location(19, 2, 5), Location(19, 3, 1), "19:2:1", "A", "I"),
    }
    assert all(row.previous.surah == row.canonical.surah for row in across)


def test_every_authored_exception_is_closed():
    by_exception = {
        name: {row.canonical for row in meeting_rows() if row.exception == name}
        for name in (
            "aimma", "aajami", "triple", "jaa_aal", "kasr_yaa",
            "fused_badal",
        )
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
        "fused_badal": {Location(46, 32, 15)},
    }


def test_every_row_carries_the_machine_contract():
    for row in meeting_rows():
        assert row.source
        assert row.canonical
        assert row.first.name in {"A", "I", "U"}
        assert row.second.name in {"A", "I", "U"}
        assert row.scope in {"one_word", "joined_words", "joined_ayahs"}
        assert row.owner
        assert row.exception in {None, "aimma", "aajami", "triple", "jaa_aal", "kasr_yaa", "fused_badal"}
