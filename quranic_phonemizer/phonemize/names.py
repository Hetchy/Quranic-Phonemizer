"""The three module functions, and the vocabulary `Phonemizer` reads a
`variants` argument against and reports one back with.
"""
from __future__ import annotations

from ..api import PACKAGES, UnknownRiwayah, recitation
from ..model.address import KhilafId, Option, Riwayah, Script, VariantSelection
from ..model.canon import Rule

#: Hafs is Uthmani by default; a second riwayah adds its own row.
DEFAULT_SCRIPT: dict[Riwayah, Script] = {Riwayah.HAFS: Script.UTHMANI}

#: The two points a selection names without a site: `chosen()` reads the
#: point alone. `rules.khilaf.NASAL_PLACES` is the engine's own copy of this
#: vocabulary; `phonemize` may not import `rules`, so this is the API-facing
#: restatement of the same two names.
_NASAL_POINTS = (KhilafId.IQLAB_NASAL, KhilafId.IKHFAA_SHAFAWI_NASAL)
_NASAL_OPTIONS = ("assimilated", "bilabial")
_NASAL_DEFAULT = "assimilated"

#: The two points `rules/khilaf.py` settles word by word, and the two
#: `canon/khilaf.py` settles at build. `seen_sad` has neither: it is
#: published and unwired.
_SITED_POINTS = (KhilafId.RAA_TAFKHEEM, KhilafId.YAA_ITHBAT)
_VOWEL_POINTS = (KhilafId.NUCLEUS_VOWEL, KhilafId.IMALA_QUALITY)

#: `identifier` is the model's own `Rule.value`. Two boundary rules --
#: `wasl_start`/`wasl_elision`, and `pausal_alif`, are real, minted
#: rules and are included as the model spells them.
RULE_NAMES: dict[Rule, tuple[str, str]] = {
    Rule.IZHAR: ("Izhar", "إظهار"),
    Rule.IKHFAA_HAQIQI: ("Ikhfaa Haqiqi", "إخفاء حقيقي"),
    Rule.IQLAB: ("Iqlab", "إقلاب"),
    Rule.IDGHAM_BI_GHUNNAH: ("Idgham bi-Ghunnah", "إدغام بغنة"),
    Rule.IDGHAM_BILA_GHUNNAH: ("Idgham bila-Ghunnah", "إدغام بلا غنة"),
    Rule.GHUNNAH_MUSHADDADAH: ("Ghunnah Mushaddadah", "غنة مشددة"),
    Rule.IZHAR_SHAFAWI: ("Izhar Shafawi", "إظهار شفوي"),
    Rule.IKHFAA_SHAFAWI: ("Ikhfaa Shafawi", "إخفاء شفوي"),
    Rule.IDGHAM_SHAFAWI: ("Idgham Shafawi", "إدغام شفوي"),
    Rule.IDGHAM_MUTAMATHILAYN: ("Idgham Mutamathilayn", "إدغام متماثلين"),
    Rule.IDGHAM_MUTAQARIBAYN: ("Idgham Mutaqaribayn", "إدغام متقاربين"),
    Rule.IDGHAM_MUTAJANISAYN_KAMIL: ("Idgham Mutajanisayn Kamil", "إدغام متجانسين كامل"),
    Rule.IDGHAM_MUTAJANISAYN_NAQIS: ("Idgham Mutajanisayn Naqis", "إدغام متجانسين ناقص"),
    Rule.LAM_SHAMSIYYAH: ("Lam Shamsiyyah", "لام شمسية"),
    Rule.LAM_QAMARIYYAH: ("Lam Qamariyyah", "لام قمرية"),
    Rule.QALQALA_SUGHRA: ("Qalqala Sughra", "قلقلة صغرى"),
    Rule.QALQALA_KUBRA: ("Qalqala Kubra", "قلقلة كبرى"),
    Rule.QALQALA_AKBAR: ("Qalqala Akbar", "قلقلة أكبر"),
    Rule.TAFKHEEM: ("Tafkheem", "تفخيم"),
    Rule.TARQEEQ: ("Tarqeeq", "ترقيق"),
    Rule.IMALA: ("Imala", "إمالة"),
    Rule.TASHIL: ("Tashil", "تسهيل"),
    Rule.ISHMAM: ("Ishmam", "إشمام"),
    Rule.MADD_TABII: ("Madd Tabii", "مد طبيعي"),
    Rule.MADD_WAJIB_MUTTASIL: ("Madd Wajib Muttasil", "مد واجب متصل"),
    Rule.MADD_JAIZ_MUNFASIL: ("Madd Jaiz Munfasil", "مد جائز منفصل"),
    Rule.MADD_LAZIM: ("Madd Lazim", "مد لازم"),
    Rule.MADD_ARID_LIL_SUKUN: ("Madd Arid lil-Sukun", "مد عارض للسكون"),
    Rule.MADD_LEEN: ("Madd Leen", "مد لين"),
    Rule.IWAD: ("Iwad", "عوض"),
    Rule.IBDAL_HAMZA: ("Ibdal Hamza", "إبدال الهمزة"),
    Rule.WASL_ELISION: ("Hamza Wasl Elision", "حذف همزة الوصل"),
    Rule.WASL_START: ("Hamza Wasl Start", "همزة الوصل عند الابتداء"),
    Rule.ILTIQA_KASRA: ("Iltiqa Kasra", "كسر التقاء الساكنين"),
    Rule.ILTIQA_SHORTENING: ("Iltiqa Shortening", "قصر عند التقاء الساكنين"),
    Rule.PAUSAL_SUKUN: ("Pausal Sukun", "سكون الوقف"),
    Rule.TAA_MARBUTA_PAUSAL: ("Taa Marbuta at a Pause", "تاء مربوطة عند الوقف"),
    Rule.PAUSAL_ALIF: ("Pausal Alif", "ألف الوقف"),
    Rule.FAKK_IDGHAM: ("Fakk Idgham", "فك الإدغام"),
    Rule.ORTHOGRAPHIC_SILENCE: ("Orthographic Silence", "حرف لا ينطق به"),
}


def supported_riwayat() -> tuple[str, ...]:
    return tuple(sorted(r.value for r in PACKAGES))


def tajweed_rules(riwayah: str) -> tuple[tuple[str, str, str], ...]:
    check_riwayah(riwayah)
    return tuple(
        (rule.value, english, arabic)
        for rule, (english, arabic) in RULE_NAMES.items()
    )


def available_variants(riwayah: str) -> dict[str, dict]:
    khilaf = recitation(check_riwayah(riwayah)).khilaf
    out: dict[str, dict] = {point.value: {} for point in KhilafId}
    for point in _SITED_POINTS:
        out[point.value] = khilaf.sited[point].points()
    for point in _VOWEL_POINTS:
        out[point.value] = {
            name: spec for name, spec in khilaf.vowel.points().items()
            if spec["khilaf"] == point.value
        }
    for point in _NASAL_POINTS:
        out[point.value] = {
            "options": sorted(_NASAL_OPTIONS), "default": _NASAL_DEFAULT,
        }
    return out


def resolved_variant(khilaf, selection: VariantSelection) -> dict[str, object]:
    """Every site `available_variants` names, with the value this selection
    actually reads there -- the override if one was made, else the default."""
    out: dict[str, object] = {point.value: {} for point in KhilafId}
    for point in _SITED_POINTS:
        out[point.value] = {
            site: selection.chosen(point, site=site) or spec["default"]
            for site, spec in khilaf.sited[point].points().items()
        }
    for point in _VOWEL_POINTS:
        out[point.value] = {
            name: selection.chosen(point, site=name) or spec["default"]
            for name, spec in khilaf.vowel.points().items()
            if spec["khilaf"] == point.value
        }
    for point in _NASAL_POINTS:
        out[point.value] = selection.chosen(point) or _NASAL_DEFAULT
    return out


def to_selection(variants: dict | None) -> VariantSelection:
    """`variants={"point": "name"}` broadcasts; `{"point": {"site": "name"}}`
    names one."""
    if not variants:
        return VariantSelection()
    options = []
    for key, value in variants.items():
        khilaf = KhilafId(key)
        if isinstance(value, str):
            options.append(Option(khilaf, value))
        else:
            options.extend(
                Option(khilaf, name, site) for site, name in value.items()
            )
    return VariantSelection(tuple(options))


def check_riwayah(riwayah: str) -> Riwayah:
    try:
        name = Riwayah(riwayah)
    except ValueError:
        raise UnknownRiwayah(
            f"{riwayah!r} is not a riwayah; this build ships "
            f"{[r.value for r in PACKAGES]}"
        ) from None
    if name not in PACKAGES:
        raise UnknownRiwayah(
            f"{riwayah!r} is not packaged; this build ships "
            f"{[r.value for r in PACKAGES]}"
        )
    return name


__all__ = [
    "DEFAULT_SCRIPT",
    "RULE_NAMES",
    "available_variants",
    "check_riwayah",
    "resolved_variant",
    "supported_riwayat",
    "tajweed_rules",
    "to_selection",
]
