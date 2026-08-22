from __future__ import annotations

import pytest

from tests.support import (
    Expect,
    R,
    Site,
    StateCase,
    assert_case,
    case_runs,
    isolated,
    joining,
    pick,
)


CASES = (
    # عِوَجَاۜ قَيِّمًا
    StateCase(
        id="iwaja-qayyima",
        site=Site(hafs=("18:1", (11,))),
        states={
            "sakt": Expect(
                read=joining(),
                phonemes=pick(
                    hafs_uthmani="ʕ i w a ʒ a:",
                    hafs_indopak="ʕ i w a ʒ a ŋ",
                ),
            ),
            "stopped": Expect(
                read=isolated(),
                phonemes="ʕ i w a ʒ a:",
            ),
        },
    ),
    # مَرْقَدِنَاۜ هَذَا
    StateCase(
        id="marqadina-hadha",
        site=Site(hafs=("36:52", (6,))),
        states={
            "sakt": Expect(read=joining(), phonemes="m a rˤ q aˤ d i n a:"),
            "stopped": Expect(read=isolated(), phonemes="m a rˤ q aˤ d i n a:"),
        },
    ),
    # مَنْۜ رَاقٍ
    StateCase(
        id="man-raq",
        site=Site(hafs=("75:27", (2,))),
        states={
            "sakt": Expect(
                read=joining(),
                phonemes="m a n",
                char_rules={"ن": R("izhar")},
                sound_rules={"n": R("izhar")},
                absent_char_rules={"ن": R("idgham_bila_ghunnah")},
            ),
            "stopped": Expect(
                read=isolated(),
                phonemes="m a n",
                char_rules={"ن": R("izhar")},
                sound_rules={"n": R("izhar")},
                absent_char_rules={"ن": R("idgham_bila_ghunnah")},
            ),
        },
    ),
    # بَلْۜ رَانَ
    StateCase(
        id="bal-ran",
        site=Site(hafs=("83:14", (2,))),
        states={
            "sakt": Expect(
                read=joining(),
                phonemes="b a l",
                absent_char_rules={"ل": R("idgham_mutaqaribayn")},
            ),
            "stopped": Expect(
                read=isolated(),
                phonemes="b a l",
                absent_char_rules={"ل": R("idgham_mutaqaribayn")},
            ),
        },
    ),
    # مَالِيَهْۜ هَلَكَ
    StateCase(
        id="maliyah-halak",
        site=Site(hafs=("69:28", (4,))),
        states={
            "sakt": Expect(
                read=joining(),
                phonemes="m a: l i j a h",
                absent_char_rules={"ه": R("idgham_mutamathilayn")},
            ),
            "stopped": Expect(
                read=isolated(),
                phonemes="m a: l i j a h",
                absent_char_rules={"ه": R("idgham_mutamathilayn")},
            ),
        },
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_sakt(run):
    assert_case(run)
