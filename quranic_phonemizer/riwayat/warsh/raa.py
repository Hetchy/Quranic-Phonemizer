"""Authored al-Azraq raa registers and their fixed profile."""
from __future__ import annotations

from dataclasses import dataclass

from ...model.address import Location, SourceLocation
from ...model.canon import CanonLetter as L
from ...rules.raa import RaaKey, RaaProfile

_ARTIFACT = "king-fahd-warsh-v2"


@dataclass(frozen=True, slots=True)
class RaaSite:
    owner: str
    source: SourceLocation
    canonical: Location
    text: str
    raa: int = 1

    @property
    def key(self) -> RaaKey:
        return self.canonical, self.raa


def _site(owner, source, canonical, text, raa=1) -> RaaSite:
    return RaaSite(
        owner, SourceLocation(_ARTIFACT, *source), Location(*canonical), text, raa
    )


SITES = (
    _site("raa_fixed_ibrahim_heavy", (2, 123, 3), (2, 124, 3), "إِبْرَٰهِـيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 124, 10), (2, 125, 10), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 124, 14), (2, 125, 14), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 125, 3), (2, 126, 3), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (2, 126, 3), (2, 127, 3), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (2, 129, 5), (2, 130, 5), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 131, 3), (2, 132, 3), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (2, 132, 20), (2, 133, 20), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 134, 10), (2, 135, 10), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 135, 10), (2, 136, 10), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 139, 4), (2, 140, 4), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 257, 6), (2, 258, 6), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (2, 257, 15), (2, 258, 15), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (2, 257, 25), (2, 258, 25), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (2, 259, 3), (2, 260, 3), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (3, 33, 7), (3, 33, 7), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (3, 64, 6), (3, 65, 6), "إِبْرَٰهِيمَۖ"),
    _site("raa_fixed_ibrahim_heavy", (3, 66, 3), (3, 67, 3), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (3, 67, 4), (3, 68, 4), "بِإِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (3, 83, 10), (3, 84, 10), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (3, 95, 6), (3, 95, 6), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (3, 97, 5), (3, 97, 5), "إِبْرَٰهِيمَۖ"),
    _site("raa_fixed_ibrahim_heavy", (4, 53, 13), (4, 54, 13), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (4, 124, 12), (4, 125, 12), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (4, 124, 16), (4, 125, 16), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (4, 162, 13), (4, 163, 13), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (6, 75, 3), (6, 74, 3), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (6, 76, 3), (6, 75, 3), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (6, 84, 4), (6, 83, 4), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (6, 163, 4), (6, 161, 11), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (9, 71, 2), (9, 70, 12), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (9, 115, 4), (9, 114, 4), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (9, 115, 20), (9, 114, 20), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (11, 68, 4), (11, 69, 4), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (11, 73, 4), (11, 74, 4), "اِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (11, 74, 2), (11, 75, 2), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (11, 75, 1), (11, 76, 1), "يَٰٓإِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (12, 6, 20), (12, 6, 20), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (12, 38, 4), (12, 38, 4), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (14, 37, 3), (14, 35, 3), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (15, 51, 4), (15, 51, 4), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (16, 120, 2), (16, 120, 2), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (16, 123, 7), (16, 123, 7), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (19, 40, 4), (19, 41, 4), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (19, 46, 6), (19, 46, 6), "يَٰٓإِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (19, 58, 17), (19, 58, 17), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (21, 51, 3), (21, 51, 3), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (21, 60, 7), (21, 60, 7), "إِبْرَٰهِيمُۖ"),
    _site("raa_fixed_ibrahim_heavy", (21, 62, 6), (21, 62, 6), "يَٰٓإِبْرَٰهِيمُۖ"),
    _site("raa_fixed_ibrahim_heavy", (21, 68, 7), (21, 69, 7), "إِبْرَٰهِيمَۖ"),
    _site("raa_fixed_ibrahim_heavy", (22, 24, 3), (22, 26, 3), "لِإِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (22, 41, 2), (22, 43, 2), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (22, 76, 17), (22, 78, 17), "إِبْرَٰهِيمَۖ"),
    _site("raa_fixed_ibrahim_heavy", (26, 69, 4), (26, 69, 4), "ا۪بْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (29, 15, 1), (29, 16, 1), "وَإِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (29, 31, 4), (29, 31, 4), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (33, 7, 9), (33, 7, 9), "وَإِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (37, 83, 4), (37, 83, 4), "لَإِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (37, 104, 3), (37, 104, 3), "يَّٰٓإِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (37, 109, 3), (37, 109, 3), "إِبْرَٰهِيمَۖ"),
    _site("raa_fixed_ibrahim_heavy", (38, 44, 3), (38, 45, 3), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (42, 11, 15), (42, 13, 15), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (43, 25, 3), (43, 26, 3), "إِبْرَٰهِيمُ"),
    _site("raa_fixed_ibrahim_heavy", (51, 24, 5), (51, 24, 5), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (53, 36, 1), (53, 37, 1), "وَإِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (57, 25, 4), (57, 26, 4), "وَإِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (60, 4, 7), (60, 4, 7), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (60, 4, 35), (60, 4, 35), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_ibrahim_heavy", (87, 19, 2), (87, 19, 2), "إِبْرَٰهِيمَ"),
    _site("raa_fixed_israil_heavy", (2, 39, 2), (2, 40, 2), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (2, 46, 2), (2, 47, 2), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (2, 82, 5), (2, 83, 5), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (2, 121, 2), (2, 122, 2), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (2, 209, 3), (2, 211, 3), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (2, 244, 7), (2, 246, 7), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (3, 48, 9), (3, 49, 4), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (3, 93, 6), (3, 93, 6), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (3, 93, 10), (3, 93, 10), "إِسْرَآءِيلُ"),
    _site("raa_fixed_israil_heavy", (5, 13, 6), (5, 12, 6), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (5, 34, 7), (5, 32, 7), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (5, 72, 5), (5, 70, 5), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (5, 74, 14), (5, 72, 14), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (5, 80, 6), (5, 78, 6), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (5, 112, 50), (5, 110, 50), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (7, 104, 18), (7, 105, 18), "إِسْرَآءِيلَۖ"),
    _site("raa_fixed_israil_heavy", (7, 133, 22), (7, 134, 22), "إِسْرَآءِيلَۖ"),
    _site("raa_fixed_israil_heavy", (7, 136, 18), (7, 137, 18), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (7, 138, 3), (7, 138, 3), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (10, 90, 3), (10, 90, 3), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (10, 90, 24), (10, 90, 24), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (10, 93, 4), (10, 93, 4), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (17, 2, 7), (17, 2, 7), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (17, 4, 4), (17, 4, 4), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (17, 101, 9), (17, 101, 9), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (17, 104, 5), (17, 104, 5), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (19, 58, 18), (19, 58, 18), "وَإِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (20, 46, 9), (20, 47, 9), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (20, 78, 2), (20, 80, 2), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (20, 92, 15), (20, 94, 15), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (26, 16, 5), (26, 17, 5), "إِسْرَآءِيلَۖ"),
    _site("raa_fixed_israil_heavy", (26, 21, 8), (26, 22, 8), "إِسْرَآءِيلَۖ"),
    _site("raa_fixed_israil_heavy", (26, 59, 4), (26, 59, 4), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (26, 197, 9), (26, 197, 9), "إِسْرَآءِيلَۖ"),
    _site("raa_fixed_israil_heavy", (27, 78, 7), (27, 76, 7), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (32, 23, 14), (32, 23, 14), "إِسْرَآءِيلَۖ"),
    _site("raa_fixed_israil_heavy", (40, 53, 7), (40, 53, 7), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (43, 59, 10), (43, 59, 10), "إِسْرَآءِيلَۖ"),
    _site("raa_fixed_israil_heavy", (44, 29, 4), (44, 30, 4), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (45, 15, 4), (45, 16, 4), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (46, 9, 14), (46, 10, 14), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (61, 6, 7), (61, 6, 7), "إِسْرَآءِيلَ"),
    _site("raa_fixed_israil_heavy", (61, 14, 26), (61, 14, 26), "إِسْرَآءِيلَ"),
    _site("raa_fixed_imran_heavy", (3, 33, 9), (3, 33, 9), "عِمْرَٰنَ"),
    _site("raa_fixed_imran_heavy", (3, 35, 4), (3, 35, 4), "عِمْرَٰنَ"),
    _site("raa_fixed_imran_heavy", (66, 12, 3), (66, 12, 3), "عِمْرَٰنَ"),
    _site("raa_fixed_repeated_heavy", (2, 229, 13), (2, 231, 13), "ضِرَاراٗ"),
    _site("raa_fixed_repeated_heavy", (6, 7, 19), (6, 6, 19), "مِّدْرَاراٗۖ"),
    _site("raa_fixed_repeated_heavy", (9, 108, 4), (9, 107, 4), "ضِرَاراٗ"),
    _site("raa_fixed_repeated_heavy", (11, 52, 10), (11, 52, 10), "مِّدْرَاراٗ"),
    _site("raa_fixed_repeated_heavy", (18, 18, 19), (18, 18, 19), "فِرَاراٗ"),
    _site("raa_fixed_repeated_heavy", (33, 13, 25), (33, 13, 25), "فِرَاراٗۖ"),
    _site("raa_fixed_repeated_heavy", (33, 16, 4), (33, 16, 4), "اُ۬لْفِرَارُ"),
    _site("raa_fixed_repeated_heavy", (71, 6, 5), (71, 6, 5), "فِرَاراٗۖ"),
    _site("raa_fixed_repeated_heavy", (71, 9, 7), (71, 9, 7), "إِسْرَاراٗ"),
    _site("raa_fixed_repeated_heavy", (71, 11, 4), (71, 11, 4), "مِّدْرَاراٗ"),
    _site("raa_fixed_hidhrahum_light", (4, 101, 26), (4, 102, 26), "حِذْرَهُمْ"),
    _site("raa_fixed_other_ashir_light", (22, 13, 10), (22, 13, 10), "اَ۬لْعَشِيرُۖ"),
    _site("raa_fixed_other_ashir_light", (26, 213, 2), (26, 214, 2), "عَشِيرَتَكَ"),
    _site("raa_fixed_other_ashir_light", (58, 21, 21), (58, 22, 21), "عَشِيرَتَهُمُۥٓۖ"),
)


def _keys(*rows: tuple[int, int, int]) -> frozenset[RaaKey]:
    return frozenset((Location(*row), 1) for row in rows)


BY_OWNER = {
    "raa_fixed_ibrahim_heavy": _keys(
        (2, 124, 3), (2, 125, 10), (2, 125, 14), (2, 126, 3),
        (2, 127, 3), (2, 130, 5), (2, 132, 3), (2, 133, 20),
        (2, 135, 10), (2, 136, 10), (2, 140, 4), (2, 258, 6),
        (2, 258, 15), (2, 258, 25), (2, 260, 3), (3, 33, 7),
        (3, 65, 6), (3, 67, 3), (3, 68, 4), (3, 84, 10),
        (3, 95, 6), (3, 97, 5), (4, 54, 13), (4, 125, 12),
        (4, 125, 16), (4, 163, 13), (6, 74, 3), (6, 75, 3),
        (6, 83, 4), (6, 161, 11), (9, 70, 12), (9, 114, 4),
        (9, 114, 20), (11, 69, 4), (11, 74, 4), (11, 75, 2),
        (11, 76, 1), (12, 6, 20), (12, 38, 4), (14, 35, 3),
        (15, 51, 4), (16, 120, 2), (16, 123, 7), (19, 41, 4),
        (19, 46, 6), (19, 58, 17), (21, 51, 3), (21, 60, 7),
        (21, 62, 6), (21, 69, 7), (22, 26, 3), (22, 43, 2),
        (22, 78, 17), (26, 69, 4), (29, 16, 1), (29, 31, 4),
        (33, 7, 9), (37, 83, 4), (37, 104, 3), (37, 109, 3),
        (38, 45, 3), (42, 13, 15), (43, 26, 3), (51, 24, 5),
        (53, 37, 1), (57, 26, 4), (60, 4, 7), (60, 4, 35),
        (87, 19, 2),
    ),
    "raa_fixed_israil_heavy": _keys(
        (2, 40, 2), (2, 47, 2), (2, 83, 5), (2, 122, 2),
        (2, 211, 3), (2, 246, 7), (3, 49, 4), (3, 93, 6),
        (3, 93, 10), (5, 12, 6), (5, 32, 7), (5, 70, 5),
        (5, 72, 14), (5, 78, 6), (5, 110, 50), (7, 105, 18),
        (7, 134, 22), (7, 137, 18), (7, 138, 3), (10, 90, 3),
        (10, 90, 24), (10, 93, 4), (17, 2, 7), (17, 4, 4),
        (17, 101, 9), (17, 104, 5), (19, 58, 18), (20, 47, 9),
        (20, 80, 2), (20, 94, 15), (26, 17, 5), (26, 22, 8),
        (26, 59, 4), (26, 197, 9), (27, 76, 7), (32, 23, 14),
        (40, 53, 7), (43, 59, 10), (44, 30, 4), (45, 16, 4),
        (46, 10, 14), (61, 6, 7), (61, 14, 26),
    ),
    "raa_fixed_imran_heavy": _keys((3, 33, 9), (3, 35, 4), (66, 12, 3)),
    "raa_fixed_repeated_heavy": _keys(
        (2, 231, 13), (9, 107, 4), (18, 18, 19), (33, 13, 25),
        (71, 6, 5), (33, 16, 4), (71, 9, 7), (6, 6, 19),
        (11, 52, 10), (71, 11, 4),
    ),
    "raa_fixed_hidhrahum_light": _keys((4, 102, 26)),
    "raa_fixed_other_ashir_light": _keys((22, 13, 10), (26, 214, 2), (58, 22, 21)),
}


def _union(*owners: str) -> frozenset[RaaKey]:
    return frozenset().union(*(BY_OWNER[owner] for owner in owners))


PROFILE = RaaProfile(
    by_owner=BY_OWNER,
    heavy=_union(
        "raa_fixed_ibrahim_heavy", "raa_fixed_israil_heavy",
        "raa_fixed_imran_heavy", "raa_fixed_repeated_heavy",
    ),
    light=_union(
        "raa_fixed_hidhrahum_light", "raa_fixed_other_ashir_light",
    ),
    always_heavy=frozenset({L.KHA, L.SAD, L.DAD, L.TAH, L.ZAH, L.GHAIN, L.QAF}),
)


__all__ = ["BY_OWNER", "PROFILE", "RaaKey", "RaaSite", "SITES"]
