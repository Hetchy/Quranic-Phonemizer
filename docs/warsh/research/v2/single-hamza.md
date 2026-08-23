# Warsh single hamza

This document owns Warsh treatment of one lexical qata hamza when no adjacent
qata hamza creates a hamza meeting. It specifies the regular morphology-backed
ibdal predicates, their fixed exclusions, and the closed lexical readings that
do not follow those predicates. Ordinary naql is in [`naql.md`](naql.md), and
adjacent hamzas are in [`hamza-meetings.md`](hamza-meetings.md).

Public values, defaults, and selector scopes remain in
[`docs/variants.md`](../../../variants.md). Source marks attest the selected
reading; they never decide whether a canonical hamza qualifies.

## Regular ibdal predicates

### Sakin root-initial hamza

Warsh replaces a canonically sakin hamza that is the first radical of its
lexeme with a pure carrier matching the immediately preceding performed vowel:

| Preceding vowel | Result | Example span |
| --- | --- | --- |
| A | long A | `يَالَمُونَ`, source 4:103:10, canonical 4:104:10: `j a: l a m ...` |
| U | long U | `يُومِنُونَ`, source 2:2:2, canonical 2:3:2: `j u: m i n ...` |
| I | long I | connected `اَ۬لذِے اؤتمن`, source 2:282:15-16, canonical 2:283:15-16: `... ð i: t u m i n a` |

The rule and its matching-carrier result are stated directly in Al-Wafi's
single-hamza chapter
([source](https://www.islamweb.net/ar/library/content/245/17/)). The I example
also shows the boundary-sensitive silent-qata start family: at ibtidaa the
special wasl-plus-qata outcome in [`wasl-hamza.md`](wasl-hamza.md) applies;
after wasl elision, the preceding performed vowel controls this ordinary
single-hamza replacement.

The pure carrier emits `ibdal_hamza` and normally `madd_tabii` on the same
result vowel. A fixed following sukun changes the structural madd
classification to `madd_lazim`. General single-hamza ibdal is not
`madd_badal`: the latter is reserved for the badal-origin predicate specified
in [`madd-badal.md`](madd-badal.md).

### Open root-initial hamza after U

Warsh also replaces an open root-initial hamza after U with a moving waw. The
three independent conditions are canonical hamza quality A, preceding
performed U in the same lexical word, and first-radical morphology. A U at the
end of a preceding word does not qualify this single-word predicate. Al-Wafi
states all three
([source](https://www.islamweb.net/ar/library/content/245/17/)).

For `مُّوَ۬جَّلاٗۖ`, source and canonical 3:145:10, a context-complete joined
span at source and canonical 3:145:9-12, through following `يُرِدْ`, begins
`... b a m̃ u w a ʒʒ a l a w̃ a m a j̃ u ...`. The replacement is consonantal
`w` plus short A, not `u:`. The held `/m̃/`, `/w̃/`, and `/j̃/` are independent
ordinary tanwin or noon idgham results at the three word boundaries; none
alters ibdal. Emit `ibdal_hamza` on the moving waw, the source hamza, and the
source units that attest its replacement. Emit no madd rule for that replacement.

Both regular predicates apply in wasl, waqf, and ibtidaa. Boundary planning
may change a preceding vowel or expose a sakin root hamza after wasl elision,
so that predicate consumes the effective performed left context while
retaining the canonical morphology that establishes the hamza's radical
position. The open-after-U predicate keeps its same-word boundary as well as
its morphological conditions.

## Authored tahqiq exclusion

The regular sakin predicate excludes the seven iwaa lexemes `المأوى`,
`مأواه`, `مأواهم`, `مأواكم`, `فأووا`, `تؤوي`, and `تؤويه`. They keep a full
hamza in every state. Al-Wafi explicitly identifies this lexical family as the
exception to Warsh ibdal
([source](https://www.islamweb.net/ar/library/content/245/17/)).

The selected corpus contains 25 tokens in this exclusion register. It is
machine-owned by canonical lexeme, not by a source-codepoint pattern. The
register stores all source and canonical refs and includes the spelling
variants and attached conjunctions or prepositions of the same seven lexemes.
No `ibdal_hamza` or replacement madd is emitted for them.

The complete register is:

| Family | Count | Selected source refs | Canonical refs |
| --- | ---: | --- | --- |
| `المأوى` | 4 | 32:19:8; 53:15:3; 79:38:4; 79:40:4 | 32:19:8; 53:15:3; 79:39:4; 79:41:4 |
| `مأواه` | 3 | 3:162:10; 5:74:28; 8:16:17 | 3:162:10; 5:72:28; 8:16:17 |
| `مأواهم` | 12 | 3:151:15; 3:197:4; 4:96:24; 4:120:2; 9:74:8; 9:96:13; 10:8:2; 13:20:24; 17:97:22; 24:55:8; 32:20:4; 66:9:8 | 3:151:15; 3:197:4; 4:97:24; 4:121:2; 9:73:8; 9:95:13; 10:8:2; 13:18:24; 17:97:22; 24:57:8; 32:20:4; 66:9:8 |
| `مأواكم` | 3 | 29:24:22; 45:33:9; 57:14:10 | 29:25:22; 45:34:9; 57:15:10 |
| `فأووا` | 1 | 18:16:7 | 18:16:7 |
| `تؤوي` | 1 | 33:51:5 | 33:51:5 |
| `تؤويه` | 1 | 70:13:3 | 70:13:3 |

## Fixed lexical ibdal

The following forms are authored inclusions even where the general predicates
above do not establish the result. The complete selected register contains 56
tokens:

| Family | Count | Exact scope and representative selected text | Result kind and rule |
| --- | ---: | --- | --- |
| `بئر` | 1 | `وَبِيرٖ`, source 22:43:11, canonical 22:45:11 | Pure I carrier: `... b i: r ...`; `ibdal_hamza` plus `madd_tabii`. |
| `بئس` | 41 | Every token of the `بئس` lexical family, including attached `و`, `ف`, and `ل`; representative `بِيسَمَا`, source 2:89:1, canonical 2:90:1 | Pure I carrier: `b i: s ...`; `ibdal_hamza` plus `madd_tabii`. |
| `ذئب` | 3 | Canonical 12:13, 12:14, and 12:17 | Pure I carrier, affected lexical prefix `ð i: b ...`; `ibdal_hamza` plus `madd_tabii`. |
| `سأل` | 1 | `سَالَ`, source and canonical 70:1:1 | Pure A carrier: `s a: l a`; `ibdal_hamza` plus `madd_tabii`. |
| `النسيء` | 1 | `اَ۬لنَّسِيُّ`, source and canonical 9:37:2 | Moving yaa assimilates with the lexical yaa: `... s i jj u`; `ibdal_hamza`, no replacement madd. |
| `لئلا` | 3 | Source 2:149:15, 4:164:4, and 57:28:1; canonical 2:150:15, 4:165:4, and 57:29:1 | Moving yaa with A: `l i j a ll a:`; `ibdal_hamza`, no replacement madd. |
| `لأهب` | 1 | `لِاَهَبَ`, source 19:18:6, canonical 19:19:6 | Moving yaa with A: `l i j a h a b a`; `ibdal_hamza`, no replacement madd. |
| `منسأته` | 1 | `مِنسَاتَهُۥۖ فَلَمَّا`, source and canonical 34:14:13-14 | Joined pure A carrier: `m i ŋ s a: t a h u: f a ...`; ordinary ikhfa owns `/ŋ/`, while `ibdal_hamza` plus `madd_tabii` own the replacement A-long. The final `/u:/` independently has `madd_silah + madd_tabii`. |
| `يأجوج` and `مأجوج` | 4 | Source 18:90:5-6 and 21:95:4-5; canonical 18:94:5-6 and 21:96:4-5 | Pure A carriers: `j a: ʒ u: ʒ a` and `m a: ʒ u: ʒ a` at 18:94; the two 21:96 forms end in `/u/` instead. Each replacement has `ibdal_hamza` plus `madd_tabii`. |

Al-Wafi gives `بئر`, every `بئس`, the three `ذئب` sites, `لئلا`, and
`النسيء` in the single-hamza chapter
([source](https://www.islamweb.net/ar/library/content/245/17/)). The Warsh
reading of `لأهب` is documented in its surah chapter
([source](https://www.islamweb.net/ar/library/content/245/57/)); the remaining
fixed readings are attested in the Warsh/Shatibiyya profile
([source](https://quranpedia.net/book-attachment/20149/78184)). These are
lexical canonical facts even when the selected script already writes the
replacement and contains no visible hamza.

## Selectable lexical treatment

### Arayta family

The 34 `أرأيت`-family tokens use `hamza_arayta` in all states. The complete
canonical register, its values, and the ten bare-form waqf fallbacks are in
[`docs/variants.md`](../../../variants.md). Al-Nashr establishes the lexical
faces and the pausal restriction
([family](https://islamweb.net/ar/library/content/70/111/),
[waqf](https://islamweb.net/ar/library/content/70/112/)).

For `اَرَٰٓيْتَ`, source and canonical 107:1:1:

| Effective face | Relevant result | Rules |
| --- | --- | --- |
| Tashil | `ʔ a rˤ aˤ ʔ̞ a j t a` | `tashil` on the eased onset and source hamza; ordinary raa `tafkheem` remains separate. |
| Ibdal | `ʔ a rˤ aˤ: j t a` | `ibdal_hamza` and the effective structural madd on the replacement vowel; ordinary raa `tafkheem` also colors that A-long. |

At complete waqf on a bare unsuffixed form, the ibdal selection falls back to
tashil as specified by the public contract. Joined and suffixed forms do not
take that fallback.

### Ha antum

The four tokens use `ha_antum` in all states. Their selected and canonical
refs are 3:65:1 -> 3:66:1, 3:119:1 -> 3:119:1, 4:108:1 -> 4:109:1, and
47:39:1 -> 47:38:1. Al-Nashr authenticates all three public faces
([source](https://islamweb.net/ar/library/content/70/111/)).

For selected `هَآنتُمْ`, source 3:65:1, the relevant results are:

| Effective face | Relevant result | Rules |
| --- | --- | --- |
| Hadhf | `h a ʔ̞ a ŋ t u m` | Separator alif is absent; `tashil` remains on the eased hamza. |
| Ibdal | `h a: ŋ t u m` | Hamza becomes a pure A carrier before the fixed sakin noon; `ibdal_hamza` plus `madd_lazim`. |
| Ithbat | `h a: ʔ̞ a ŋ t u m` | Separator alif remains with `madd_munfasil`; `tashil` reaches the eased hamza. |

All three rows also carry ordinary `ikhfaa` on `ŋ`, because the sakin
noon of `أنتم` precedes taa. That rule and its source reach are unchanged by
the hamza face. In the ithbat row, the long belongs to the graphically joined
alerting particle `ها`, so the ordinary madd owner is munfasil rather than
muttasil. In the ibdal row, the replacement A is followed by the fixed sakin
noon and therefore receives `madd_lazim`, not `madd_tabii`. This is the
classical `المد المشبع للساكنين` face
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/111/?idfrom=&idto=&start=)).

The names above describe outcomes only; the public option order and default
are not duplicated here.

## Fixed tashil and canonical absence

The supported al-Azraq profile keeps fixed tashil at all four `اللائي` tokens:

| Selected source ref | Canonical ref | Exact selected text |
| --- | --- | --- |
| 33:4:12 | 33:4:12 | `اُ۬ل۪ےْ` |
| 58:2:12 | 58:2:12 | `اَ۬ل۪ےْ` |
| 65:4:1 | 65:4:1 | `وَال۪ےْ` |
| 65:4:12 | 65:4:12 | `وَال۪ےْ` |

The reading is established in Al-Wafi's lexical chapter
([source](https://www.islamweb.net/ar/library/content/245/68/)). In continuing
reading, including ibtidaa followed by continuation, the final hamza remains
typed as eased and emits `tashil`; disabling the extra `tashil` token renders
that onset as plain `ʔ` but removes neither the typed state nor the rule. At
ordinary full-sukun waqf, the eased final hamza instead becomes a pure sakin
yaa: the result has consonantal `/j/` with `ibdal_hamza`, not `tashil`. A
tashil face through rawm is outside the boundary model.

The selected isqat spellings are canonical absence, not a runtime deletion:

| Selected text | Selected source ref | Canonical ref |
| --- | --- | --- |
| `وَالصَّٰبِينَ` | 2:61:7 | 2:62:7 |
| `وَالصَّٰبُونَ` | 5:71:6 | 5:69:6 |
| `وَالصَّٰبِينَ` | 22:17:6 | 22:17:6 |
| `يُضَٰهُونَ` | 9:30:14 | 9:30:14 |

Projection creates no ghost hamza for these four forms. They emit no `isqat`,
`ibdal_hamza`, or `tashil` occurrence.

## Rule reach and machine data

Every `ibdal_hamza` occurrence names the replaced hamza or authored latent
hamza as its source and the replacement carrier or consonant as its host. It
reaches the replacement sound. When the result is a long carrier, its effective
madd occurrence independently reaches that same result sound. Visible source
and cell placements follow sound ownership and silence rather than tagging all
predicate context. A moving waw or yaa receives `ibdal_hamza` but no invented
madd.

Every `tashil` occurrence reaches the eased onset and responsible source
hamza even when the extra token is disabled. Its following A, U, or I remains
an independent nucleus and is never folded into the eased consonant type.

The regular morphology-backed ibdal register has no accepted aggregate total
yet. Implementation must generate it from canonical root position, hamza
quality, and effective left context, subtract the 25 iwaa exclusions, then
reconcile it to source evidence. Tests must not freeze a count derived only
from selected-script marks. Separately, authored data must assert the complete
56 fixed-ibdal tokens, 34 Arayta tokens, four Ha-antum tokens, four Allai
tokens, and four canonical-absence spellings above.
