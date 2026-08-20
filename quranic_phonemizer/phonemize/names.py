"""The three module functions, and the vocabulary `Phonemizer` reads a
`variants` argument against and reports one back with.
"""
from __future__ import annotations

from ..api import PACKAGES, UnknownRiwayah, recitation
from ..model.address import KhilafId, Option, Riwayah, Script, VariantSelection
from ..model.canon import Rule

#: Hafs is Uthmani by default; a second riwayah adds its own row.
DEFAULT_SCRIPT: dict[Riwayah, Script] = {Riwayah.HAFS: Script.UTHMANI}

#: `identifier` is the model's own `Rule.value`. Two boundary rules --
#: `wasl_start`/`hamza_wasl_silent`, and `pausal_alif`, are real, minted
#: rules and are included as the model spells them.
RULE_NAMES: dict[Rule, tuple[str, str]] = {
    Rule.IZHAR: ("Izhar", "إظهار"),
    Rule.IKHFAA: ("Ikhfaa Haqiqi", "إخفاء حقيقي"),
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
    Rule.MADD_ARID_LISSUKUN: ("Madd Arid lil-Sukun", "مد عارض للسكون"),
    Rule.MADD_LEEN: ("Madd Leen", "مد لين"),
    Rule.MADD_IWAD: ("Iwad", "عوض"),
    Rule.IBDAL_HAMZA: ("Ibdal Hamza", "إبدال الهمزة"),
    Rule.HAMZA_WASL_SILENT: ("Hamza Wasl Elision", "حذف همزة الوصل"),
    Rule.WASL_START: ("Hamza Wasl Start", "همزة الوصل عند الابتداء"),
    Rule.ILTIQA_KASRA: ("Iltiqa Kasra", "كسر التقاء الساكنين"),
    Rule.ILTIQA_FATHA: ("Iltiqa Fatha", "فتح التقاء الساكنين"),
    Rule.ILTIQA_SHORTENING: ("Iltiqa Shortening", "قصر عند التقاء الساكنين"),
    Rule.PAUSAL_SUKUN: ("Pausal Sukun", "سكون الوقف"),
    Rule.WAQF_TAA_MARBUTA: ("Taa Marbuta at a Pause", "تاء مربوطة عند الوقف"),
    Rule.PAUSAL_ALIF: ("Pausal Alif", "ألف الوقف"),
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
    return khilaf.points()


def resolved_variant(khilaf, selection: VariantSelection) -> dict[str, str]:
    """Return the scalar choice resolved for every published variant."""
    return {
        point.value: spec.choose(selection)
        for point, spec in khilaf.variants.items()
    }


def to_selection(variants: dict | None) -> VariantSelection:
    """Convert the public scalar mapping into a typed selection."""
    if not variants:
        return VariantSelection()
    options = []
    for key, value in variants.items():
        khilaf = KhilafId(key)
        if not isinstance(value, str):
            raise TypeError(
                f"{key}: variant choices are scalar strings, got "
                f"{type(value).__name__}"
            )
        options.append(Option(khilaf, value))
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
