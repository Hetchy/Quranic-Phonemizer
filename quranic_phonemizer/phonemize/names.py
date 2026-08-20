"""The three module functions, and the vocabulary `Phonemizer` reads a
`variants` argument against and reports one back with.
"""
from __future__ import annotations

from ..api import PACKAGES, UnknownRiwayah, recitation
from ..model.address import KhilafId, Option, Riwayah, Script, VariantSelection
from ..model.canon import Rule

#: Hafs is Uthmani by default; a second riwayah adds its own row.
DEFAULT_SCRIPT: dict[Riwayah, Script] = {Riwayah.HAFS: Script.UTHMANI}

#: `identifier` is the model's own `Rule.value`. Each row is the rule's
#: English and Arabic name and a one-sentence summary of what it does.
#: The boundary rules -- the three hamza wasl starts, `hamza_wasl_silent`
#: and `pausal_alif` -- are real, minted rules and are included as the
#: model spells them.
RULE_DEFINITIONS: dict[Rule, tuple[str, str, str]] = {
    Rule.IZHAR: (
        "Izhar", "إظهار",
        "A quiescent noon or tanween keeps its own sound before a throat letter.",
    ),
    Rule.IKHFAA: (
        "Ikhfaa Haqiqi", "إخفاء حقيقي",
        "A quiescent noon or tanween is hidden as a hum held at the following letter's place.",
    ),
    Rule.IQLAB: (
        "Iqlab", "إقلاب",
        "A quiescent noon or tanween becomes a hummed meem before baa.",
    ),
    Rule.IDGHAM_BI_GHUNNAH: (
        "Idgham bi-Ghunnah", "إدغام بغنة",
        "A quiescent noon or tanween merges into the letter after it and the hum is kept.",
    ),
    Rule.IDGHAM_BILA_GHUNNAH: (
        "Idgham bila-Ghunnah", "إدغام بلا غنة",
        "A quiescent noon or tanween merges into a following lam or raa with no hum.",
    ),
    Rule.GHUNNAH_MUSHADDADAH: (
        "Ghunnah Mushaddadah", "غنة مشددة",
        "A doubled noon or meem is held on its hum.",
    ),
    Rule.IZHAR_SHAFAWI: (
        "Izhar Shafawi", "إظهار شفوي",
        "A quiescent meem keeps its own sound before a letter that is neither meem nor baa.",
    ),
    Rule.IKHFAA_SHAFAWI: (
        "Ikhfaa Shafawi", "إخفاء شفوي",
        "A quiescent meem is hidden as a hum on the lips before baa.",
    ),
    Rule.IDGHAM_SHAFAWI: (
        "Idgham Shafawi", "إدغام شفوي",
        "A quiescent meem merges into a following meem.",
    ),
    Rule.IDGHAM_MUTAMATHILAYN: (
        "Idgham Mutamathilayn", "إدغام متماثلين",
        "A quiescent letter merges into an identical letter after it.",
    ),
    Rule.IDGHAM_MUTAQARIBAYN: (
        "Idgham Mutaqaribayn", "إدغام متقاربين",
        "A quiescent letter merges into a letter of a near place after it.",
    ),
    Rule.IDGHAM_MUTAJANISAYN_KAMIL: (
        "Idgham Mutajanisayn Kamil", "إدغام متجانسين كامل",
        "A quiescent letter merges completely into a letter of its own place.",
    ),
    Rule.IDGHAM_MUTAJANISAYN_NAQIS: (
        "Idgham Mutajanisayn Naqis", "إدغام متجانسين ناقص",
        "A quiescent letter merges into a letter of its own place but keeps a trait of its own.",
    ),
    Rule.LAM_SHAMSIYYAH: (
        "Lam Shamsiyyah", "لام شمسية",
        "The article's lam merges into the sun letter after it.",
    ),
    Rule.LAM_QAMARIYYAH: (
        "Lam Qamariyyah", "لام قمرية",
        "The article's lam keeps its own sound before a moon letter.",
    ),
    Rule.QALQALA_SUGHRA: (
        "Qalqala Sughra", "قلقلة صغرى",
        "A quiescent qalqala letter inside the reading is released with a light echo.",
    ),
    Rule.QALQALA_KUBRA: (
        "Qalqala Kubra", "قلقلة كبرى",
        "A qalqala letter the stop makes quiescent is released with a fuller echo.",
    ),
    Rule.QALQALA_AKBAR: (
        "Qalqala Akbar", "قلقلة أكبر",
        "A doubled qalqala letter stopped on is released with the fullest echo.",
    ),
    Rule.TAFKHEEM: (
        "Tafkheem", "تفخيم",
        "The letter is sounded heavy, and a fatha on it with it.",
    ),
    Rule.TARQEEQ: (
        "Tarqeeq", "ترقيق",
        "The raa is sounded light.",
    ),
    Rule.IMALA: (
        "Imala", "إمالة",
        "A long aa is tilted towards a long ee.",
    ),
    Rule.TASHIL: (
        "Tashil", "تسهيل",
        "A hamza is eased rather than fully articulated.",
    ),
    Rule.ISHMAM: (
        "Ishmam", "إشمام",
        "The lips round for a vowel that is not sounded.",
    ),
    Rule.MADD_TABII: (
        "Madd Tabii", "مد طبيعي",
        "A long vowel is held for its plain length, with nothing after it to extend it.",
    ),
    Rule.MADD_WAJIB_MUTTASIL: (
        "Madd Wajib Muttasil", "مد واجب متصل",
        "A long vowel is extended before a hamza in the same word.",
    ),
    Rule.MADD_JAIZ_MUNFASIL: (
        "Madd Jaiz Munfasil", "مد جائز منفصل",
        "A long vowel is extended before a hamza opening the next word.",
    ),
    Rule.MADD_LAZIM: (
        "Madd Lazim", "مد لازم",
        "A long vowel is extended before a letter the reading keeps quiescent.",
    ),
    Rule.MADD_ARID_LISSUKUN: (
        "Madd Arid lil-Sukun", "مد عارض للسكون",
        "A long vowel is extended before a letter the stop makes quiescent.",
    ),
    Rule.MADD_LEEN: (
        "Madd Leen", "مد لين",
        "A waw or yaa after a fatha is extended before a letter the stop makes quiescent.",
    ),
    Rule.MADD_IWAD: (
        "Iwad", "عوض",
        "A fathatan stopped on is exchanged for a long aa.",
    ),
    Rule.MADD_BADAL: (
        "Madd Badal", "مد بدل",
        "A long vowel on a hamza stands in for a second hamza the reading does not say.",
    ),
    Rule.MADD_SILAH: (
        "Madd Silah", "مد صلة",
        "A pronoun haa is drawn out because the word is joined to the one after it.",
    ),
    Rule.IBDAL_HAMZA: (
        "Ibdal Hamza", "إبدال الهمزة",
        "Started on, a prosthetic hamza lengthens its vowel over the quiescent hamza after it.",
    ),
    Rule.HAMZA_WASL_SILENT: (
        "Hamza Wasl Elision", "حذف همزة الوصل",
        "A prosthetic hamza is not sounded when the word before it is joined to it.",
    ),
    Rule.HAMZA_WASL_FATHA: (
        "Hamza Wasl with Fatha", "همزة الوصل بالفتح",
        "A prosthetic hamza the reading starts on is sounded with a fatha.",
    ),
    Rule.HAMZA_WASL_KASRA: (
        "Hamza Wasl with Kasra", "همزة الوصل بالكسر",
        "A prosthetic hamza the reading starts on is sounded with a kasra.",
    ),
    Rule.HAMZA_WASL_DAMMA: (
        "Hamza Wasl with Damma", "همزة الوصل بالضم",
        "A prosthetic hamza the reading starts on is sounded with a damma.",
    ),
    Rule.ILTIQA_KASRA: (
        "Iltiqa Kasra", "كسر التقاء الساكنين",
        "A tanween noon takes a kasra so that it does not meet the quiescent letter after it.",
    ),
    Rule.ILTIQA_FATHA: (
        "Iltiqa Fatha", "فتح التقاء الساكنين",
        "A spelled-out letter takes a fatha so that it does not meet the quiescent letter after it.",
    ),
    Rule.ILTIQA_SHORTENING: (
        "Iltiqa Shortening", "قصر عند التقاء الساكنين",
        "A long vowel is shortened where it would meet a quiescent letter.",
    ),
    Rule.WAQF_DIACRITIC_DROP: (
        "Waqf Diacritic Drop", "حذف الحركة عند الوقف",
        "A haraka or tanween written at the end of a word stopped on is not sounded.",
    ),
    Rule.WAQF_SILAH_DROP: (
        "Waqf Silah Drop", "حذف الصلة عند الوقف",
        "The length drawing out a pronoun haa is absent when the word is stopped on.",
    ),
    Rule.WAQF_TAA_MARBUTA: (
        "Taa Marbuta at a Pause", "تاء مربوطة عند الوقف",
        "A final taa marbuta is sounded as a haa at a stop.",
    ),
    Rule.PAUSAL_ALIF: (
        "Pausal Alif", "ألف الوقف",
        "A pausal alif is sounded long at a stop and shortened where the word "
        "is joined to the one after it.",
    ),
}


def supported_riwayat() -> tuple[str, ...]:
    return tuple(sorted(r.value for r in PACKAGES))


def tajweed_rules(riwayah: str) -> tuple[tuple[str, str, str, str], ...]:
    """One row per rule: identifier, English name, Arabic name, summary."""
    check_riwayah(riwayah)
    return tuple(
        (rule.value, *definition) for rule, definition in RULE_DEFINITIONS.items()
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
    "RULE_DEFINITIONS",
    "available_variants",
    "check_riwayah",
    "resolved_variant",
    "supported_riwayat",
    "tajweed_rules",
    "to_selection",
]
