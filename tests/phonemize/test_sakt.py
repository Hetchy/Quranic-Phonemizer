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
    explicit,
    through,
)

CASES = (
    # Hafs: عِوَجَاۜ قَيِّمًا
    VariantCase(
        id="iwaja-qayyima",
        site=Site(hafs=("18:1", (11, 12))),
        selector=KhilafId.IWAJA_QAYYIMA,
        faces={
            "sakt": Expect(
                read=through(),
                phonemes=("ʕ i w a ʒ a:", "q aˤ jj i m a:"),
                all_rules=R(
                    "madd_iwad", "madd_tabii", "tafkheem", "tarqeeq",
                    "waqf_diacritic_drop",
                ),
            ),
            "idraj": Expect(
                read=through(),
                phonemes=("ʕ i w a ʒ a ŋ", "q aˤ jj i m a:"),
                all_rules=R(
                    "ikhfaa", "madd_iwad", "madd_tabii", "tafkheem",
                    "pausal_alif", "tarqeeq", "waqf_diacritic_drop",
                ),
                sound_rules={"ŋ": R("ikhfaa", "tafkheem")},
            ),
        },
        default="sakt",
        masked=Expect(
            read=explicit(ibtidaa=11, waqf=(11, 12)),
            phonemes=("ʕ i w a ʒ a:", "q aˤ jj i m a:"),
            all_rules=R(
                "madd_iwad", "madd_tabii", "tafkheem", "tarqeeq",
                "waqf_diacritic_drop",
            ),
        ),
    ),
    # Hafs: مَنْ ۜ رَاقٍ
    VariantCase(
        id="man-raq",
        site=Site(hafs=("75:27", (2, 3))),
        selector=KhilafId.MAN_RAQ,
        faces={
            "sakt": Expect(
                read=through(),
                phonemes=("m a n", "rˤ aˤ: q Q"),
                all_rules=R(
                    "izhar", "madd_arid_lissukun", "qalqala_kubra",
                    "tafkheem", "waqf_diacritic_drop",
                ),
                char_rules={"ن": R("izhar")},
                sound_rules={"n": R("izhar")},
                absent_char_rules={"ن": R("idgham_bila_ghunnah")},
            ),
            "idraj": Expect(
                read=through(),
                phonemes=("m a", "rˤrˤ aˤ: q Q"),
                all_rules=R(
                    "idgham_bila_ghunnah", "madd_arid_lissukun",
                    "qalqala_kubra", "tafkheem", "waqf_diacritic_drop",
                ),
                char_rules={"ن": R("idgham_bila_ghunnah")},
                absent_char_rules={"ن": R("izhar")},
            ),
        },
        default="sakt",
        masked=Expect(
            read=explicit(ibtidaa=2, waqf=(2, 3)),
            phonemes=("m a n", "rˤ aˤ: q Q"),
            all_rules=R(
                "izhar", "madd_arid_lissukun", "qalqala_kubra",
                "tafkheem", "waqf_diacritic_drop",
            ),
            char_rules={"ن": R("izhar")},
            absent_char_rules={"ن": R("idgham_bila_ghunnah")},
        ),
    ),
    # Hafs: بَلْ ۜ رَانَ
    VariantCase(
        id="bal-ran",
        site=Site(hafs=("83:14", (2, 3))),
        selector=KhilafId.BAL_RAN,
        faces={
            "sakt": Expect(
                read=through(),
                phonemes=("b a l", "rˤ aˤ: n"),
                all_rules=R(
                    "izhar", "madd_arid_lissukun", "tafkheem", "tarqeeq",
                    "waqf_diacritic_drop",
                ),
                absent_char_rules={"ل": R("idgham_mutaqaribayn")},
            ),
            "idraj": Expect(
                read=through(),
                phonemes=("b a", "rˤrˤ aˤ: n"),
                all_rules=R(
                    "idgham_mutaqaribayn", "izhar", "madd_arid_lissukun",
                    "tafkheem", "waqf_diacritic_drop",
                ),
                char_rules={"ل": R("idgham_mutaqaribayn")},
            ),
        },
        default="sakt",
        masked=Expect(
            read=explicit(ibtidaa=2, waqf=(2, 3)),
            phonemes=("b a l", "rˤ aˤ: n"),
            all_rules=R(
                "izhar", "madd_arid_lissukun", "tafkheem", "tarqeeq",
                "waqf_diacritic_drop",
            ),
            absent_char_rules={"ل": R("idgham_mutaqaribayn")},
        ),
    ),
    # Hafs: مَالِيَهْ ۜ هَلَكَ
    VariantCase(
        id="maliyah-halak",
        site=Site(hafs=("69:28", (4, 5))),
        selector=KhilafId.MALIYAH_HALAK,
        faces={
            "sakt": Expect(
                read=through(),
                phonemes=("m a: l i j a h", "h a l a k"),
                all_rules=R("madd_tabii", "tarqeeq", "waqf_diacritic_drop"),
                absent_char_rules={"ه[1]": R("idgham_mutamathilayn")},
            ),
            "idgham": Expect(
                read=through(),
                phonemes=("m a: l i j a", "hh a l a k"),
                all_rules=R(
                    "idgham_mutamathilayn", "madd_tabii", "tarqeeq",
                    "waqf_diacritic_drop",
                ),
                char_rules={
                    "ه[1]": R("idgham_mutamathilayn"),
                    "ه[2]": R("idgham_mutamathilayn"),
                },
            ),
        },
        default="sakt",
        masked=Expect(
            read=explicit(ibtidaa=4, waqf=(4, 5)),
            phonemes=("m a: l i j a h", "h a l a k"),
            all_rules=R("madd_tabii", "tarqeeq", "waqf_diacritic_drop"),
            absent_char_rules={"ه[1]": R("idgham_mutamathilayn")},
        ),
    ),
    # Warsh: مَالِيَهۖ هَّلَكَ
    VariantCase(
        id="maliyah-halak-warsh",
        site=Site(warsh=("69:28", (4, 5))),
        selector=KhilafId.MALIYAH_HALAK,
        faces={
            "idgham": Expect(
                read=through(),
                phonemes=("m a: l i j a", "hh a l a k"),
                char_rules={
                    "ه[1]": R("idgham_mutamathilayn"),
                    "ه[2]": R("idgham_mutamathilayn"),
                },
            ),
            "sakt": Expect(
                read=through(),
                phonemes=("m a: l i j a h", "h a l a k"),
                absent_char_rules={"ه[1]": R("idgham_mutamathilayn")},
            ),
        },
        default="idgham",
        masked=Expect(
            read=explicit(ibtidaa=4, waqf=(4, 5)),
            phonemes=("m a: l i j a h", "h a l a k"),
            absent_char_rules={"ه[1]": R("idgham_mutamathilayn")},
        ),
    ),
)


@pytest.mark.parametrize("run", case_runs(CASES))
def test_sakt(run):
    assert_case(run)
