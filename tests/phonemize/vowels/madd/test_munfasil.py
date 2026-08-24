from __future__ import annotations

import pytest

from tests.support import Case, R, Site, assert_case, case_runs, joining, pick, through


CASES = (
    # بِمَا أُنزِلَ
    Case(id="between-words", site=Site.shared("2:4", (3, 4)), read=through(),
         phonemes=("b i m a:", "ʔ u ŋ z i l"),
         char_rules=pick(
             hafs_uthmani={"ا": R("madd_munfasil")},
             hafs_indopak={"ا[1]": R("madd_munfasil")},
             warsh_uthmani={"ا": R("madd_munfasil")},
         ),
         sound_rules={"a:": R("madd_munfasil")}),
    # هَؤُلَاءِ
    Case(id="joined-rasm", site=Site(hafs=("2:31", (12,))), read=joining(),
         phonemes="h a: ʔ u l a: ʔ i",
         char_rules={"@dagger_alif": R("madd_munfasil"),
                     "ا": R("madd_muttasil")},
         sound_rules={"a:[1]": R("madd_munfasil"),
                      "a:[2]": R("madd_muttasil")}),
    # أَهَؤُلَاءِ
    Case(id="interrogative-prefix", site=Site(hafs=("34:40", (7,))), read=joining(),
         phonemes="ʔ a h a: ʔ u l a: ʔ i",
         char_rules=pick(
             hafs_uthmani={"@dagger_alif": R("madd_munfasil"),
                           "ا": R("madd_muttasil")},
             hafs_indopak={"@dagger_alif": R("madd_munfasil"),
                           "ا[2]": R("madd_muttasil")},
         ),
         sound_rules={"a:[1]": R("madd_munfasil"),
                      "a:[2]": R("madd_muttasil")}),
    # يَا أَيُّهَا
    Case(id="vocative", site=Site(hafs=("4:1", (1,))), read=joining(),
         phonemes="j a: ʔ a jj u h a",
         char_rules={"@dagger_alif": R("madd_munfasil")},
         sound_rules={"a:": R("madd_munfasil")}),
    # وَأَنَا۠ أَوَّلُ
    Case(id="pausal-alif-negative", site=Site(hafs=("6:163", (6,))), read=joining(),
         phonemes="w a ʔ a n a",
         absent_char_rules={"@pausal_alif": R("madd_munfasil")}),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_madd_munfasil(run):
    assert_case(run)
