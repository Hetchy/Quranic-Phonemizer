"""The rule and silence-reason vocabulary: names and summaries per identifier.

Each row is the English name, the Arabic name, and a one-sentence summary
suitable for hover; every projection that publishes an identifier reads here.
"""
from __future__ import annotations

from .canon import Rule
from .inscription import SilenceReason

RULE_DEFINITIONS: dict[Rule, tuple[str, str, str]] = {
    Rule.IZHAR: (
        "Izhar", "إظهار",
        "A quiescent noon or tanween keeps its own sound before a throat letter.",
    ),
    Rule.IKHFAA: (
        "Ikhfaa", "إخفاء",
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
        "The letter is sounded light.",
    ),
    Rule.TAQLIL: (
        "Taqlil", "تقليل",
        "An open vowel is inclined to the intermediate Warsh quality.",
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
        "A reading preserves a damma gesture: either silently with the lips, "
        "or as the smaller opening component of a predominantly kasra vowel.",
    ),
    Rule.MADD_TABII: (
        "Madd Tabii", "مد طبيعي",
        "A long vowel is held for its plain length, with nothing after it to extend it.",
    ),
    Rule.MADD_MUTTASIL: (
        "Madd Muttasil", "مد متصل",
        "A long vowel is extended before a hamza in the same word.",
    ),
    Rule.MADD_MUNFASIL: (
        "Madd Munfasil", "مد منفصل",
        "A long vowel is extended before a hamza opening the next word.",
    ),
    Rule.MADD_LAZIM: (
        "Madd Lazim", "مد لازم",
        "A long vowel is extended before a letter the reading keeps quiescent.",
    ),
    Rule.MADD_ARID_LISSUKUN: (
        "Madd Arid Lissukun", "مد عارض للسكون",
        "A long vowel is extended before a letter the stop makes quiescent.",
    ),
    Rule.MADD_LEEN: (
        "Madd Leen", "مد لين",
        "A waw or yaa after a fatha is extended before a letter the stop makes quiescent.",
    ),
    Rule.MADD_IWAD: (
        "Madd Iwad", "مد عوض",
        "A fathatan stopped on is exchanged for a long aa.",
    ),
    Rule.MADD_BADAL: (
        "Madd Badal", "مد بدل",
        "A long vowel keeps its after-hamza identity when that hamza is realized or changed.",
    ),
    Rule.MADD_LEEN_MAHMUZ: (
        "Madd Leen Mahmuz", "مد اللين المهموز",
        "A quiescent waw or yaa after fatha is extended before a hamza in the same word.",
    ),
    Rule.MADD_SILAH: (
        "Madd Silah", "مد صلة",
        "A pronoun haa is drawn out because the word is joined to the one after it.",
    ),
    Rule.MADD_MIM_AL_JAM: (
        "Madd Mim al-Jam", "مد ميم الجمع",
        "A plural-pronoun mim is drawn out before a qata hamza.",
    ),
    Rule.MADD_YAA_ZAWAID: (
        "Madd Yaa Zawaid", "مد ياءات الزوائد",
        "A retained extra yaa is drawn out in a joined reading.",
    ),
    Rule.IBDAL_HAMZA: (
        "Ibdal Hamza", "إبدال الهمزة",
        "A hamza is replaced by its performed carrier or glide.",
    ),
    Rule.NAQL: (
        "Naql", "نقل",
        "A qata hamza's vowel moves to the quiescent letter before it and the hamza itself is not sounded.",
    ),
    Rule.HAMZA_WASL_SILENT: (
        "Hamza Wasl Silent", "حذف همزة الوصل",
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
    Rule.ILTIQA_HARAKA: (
        "Iltiqa Haraka", "تحريك التقاء الساكنين",
        "A canonically vowel-absent unit receives a short vowel where two quiescent sounds would meet.",
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

#: A silence reason is not a rule, but results publish its identifier on the
#: letters it leaves unsaid, so the vocabulary resolves it like one.
SILENCE_DEFINITIONS: dict[SilenceReason, tuple[str, str, str]] = {
    SilenceReason.ORTHOGRAPHIC: (
        "Orthographic Silence", "حرف لا ينطق به",
        "A letter the script writes and no reading ever says.",
    ),
}

__all__ = ["RULE_DEFINITIONS", "SILENCE_DEFINITIONS"]
