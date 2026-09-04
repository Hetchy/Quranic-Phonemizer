from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, joining, pick, through

CASES = (
    # Hafs: بِمَآ أُنزِلَ
    # Warsh: بِمَآ أُنزِلَ
    Case(id="between-words", site=Site.shared("2:4", (3, 4)), read=through(),
         phonemes=("b i m a:", "ʔ u ŋ z i l"),
         char_rules=pick(
             hafs_uthmani={"ا": R("madd_munfasil")},
             hafs_indopak={"ا[1]": R("madd_munfasil")},
             warsh_uthmani={"ا": R("madd_munfasil")},
         ),
         sound_rules={"a:": R("madd_munfasil")}),
    # Hafs: هَـٰٓؤُلَآءِ
    # Warsh: هَٰٓؤُلَآءِ
    Case(id="joined-rasm", site=Site.shared("2:31", (12,)), read=joining(),
         phonemes=pick(
             hafs="h a: ʔ u l a: ʔ i",
             warsh="h a: ʔ u l a: ʔ",
         ),
         char_rules={"@dagger_alif": R("madd_munfasil"),
                     "ا": R("madd_muttasil")},
         sound_rules={"a:[1]": R("madd_munfasil"),
                      "a:[2]": R("madd_muttasil")}),
    # Hafs: أَهَـٰٓؤُلَآءِ
    # Warsh: أَهَٰٓؤُلَآءِ
    Case(id="interrogative-prefix", site=Site.shared("34:40", (7,)), read=joining(),
         phonemes=pick(
             hafs="ʔ a h a: ʔ u l a: ʔ i",
             warsh="ʔ a h a: ʔ u l a: ʔ",
         ),
         char_rules=pick(
             hafs_uthmani={"@dagger_alif": R("madd_munfasil"),
                           "ا": R("madd_muttasil")},
             hafs_indopak={"@dagger_alif": R("madd_munfasil"),
                           "ا[2]": R("madd_muttasil")},
             warsh_uthmani={"@dagger_alif": R("madd_munfasil"),
                             "ا": R("madd_muttasil")},
         ),
         sound_rules={"a:[1]": R("madd_munfasil"),
                      "a:[2]": R("madd_muttasil")}),
    # Hafs: يَـٰٓأَيُّهَا
    # Warsh: يَٰٓأَيُّهَا
    Case(id="vocative", site=Site.shared("4:1", (1,)), read=joining(),
         phonemes="j a: ʔ a jj u h a",
         char_rules={"@dagger_alif": R("madd_munfasil")},
         sound_rules={"a:": R("madd_munfasil")}),
    # Hafs: وَأَنَا۠
    Case(id="pausal-alif-negative", site=Site(hafs=("6:163", (6,))), read=joining(),
         phonemes="w a ʔ a n a",
         absent_char_rules={"@pausal_alif": R("madd_munfasil")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_madd_munfasil(run):
    assert_case(run)
