# Naql

This document owns Warsh transfer of an initial qata-hamza vowel to an
eligible sakin host, deletion of the qata onset, the definite-article form of
the same rule, and the two lexical boundary exceptions. It does not own
hamzat al-wasl or iltiqa al-sakinayn.

The only public choices in this chapter are `kitabiyah_inni` and the start
shape selected by `article_ibtidaa`; their values and defaults remain in
[`docs/variants.md`](../../../variants.md).

## General cross-word predicate

In joined speech, Warsh through al-Azraq applies naql when all of these hold:

1. the first word ends in an eligible sakin host;
2. the second word begins with a moving qata hamza;
3. the host is the final unit of its word and the qata is the initial unit of
   its word; and
4. the host is not a madd carrier and not plural mim.

The host receives exactly the qata's A, U, or I nucleus and the qata onset is
silent. Eligible hosts include an ordinary sahih consonant, the noon supplied
by tanwin, feminine taa, and a sakin leen waw or yaa. Al-Wafi states the
transfer, deletion, word-boundary conditions, A/U/I results, and exclusions
([Al-Wafi](https://islamweb.net/ar/library/content/245/18/)); Al-Nashr gives
the same predicate and detailed qualifications
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/113/)).

Some secondary summaries paraphrase the host as neither madd nor leen. That
is too narrow for this route. Al-Wafi explains the Shatibiyya word `صحيح` as
excluding a madd letter only and says explicitly that a leen letter remains
included: `احترازا عن حرف المد فقط، فيكون حرف اللين داخلا`
([Al-Wafi](https://islamweb.net/ar/library/content/245/18/)). The regular
predicate therefore keeps consonantal sakin waw and yaa but rejects a true
madd carrier.

Plural mim is excluded because its Warsh silah owns that boundary. A long
carrier is excluded because it is not a sakin sahih or leen host. A medial
sakin within an ordinary word is excluded; `ردءا` below is the single
authored lexical exception.

This vertical implements the ordinary short-vowel family only. An initial
hamza followed by a badal carrier is deferred to
[`madd-badal.md`](madd-badal.md): naql transfers the short haraka, while the
carrier separately owns the resulting length. Treating the whole long
nucleus as naql would collapse `badal mughayyar bin-naql` into the wrong
rule. The selected source has 193 initial-long shapes: 177 A, 13 U, and 3 I.
The 34 `ا۟وْ...` spellings are excluded because their waw is rasm-only and
their latent qata has a short damma. Three initial-long shapes are
hamza-meeting spellings owned by that chapter: 2:140:14, 20:22:10, and
58:13:1. The remaining 190 are badal mughayyar bin-naql: 186 within ayahs and
4 across ayah edges.

## Corpus size and data ownership

The selected corpus has 1,550 eligible within-ayah cross-word boundaries.
There are another 180 adjacent-ayah edges within the same surah that qualify
when the caller explicitly joins those ayahs. Thus a fully continuous
intra-surah plan exposes 1,730 general boundaries. Surah-transition insertion
or omission of basmala is outside this register.

These totals supersede a raw source-shape scan of 1,867 candidates: 1,568
within ayahs and 299 at verse edges. That scan treated every selected-script
bare initial alif as qata before resolving the canonical onset. Canonical
classification rejects 18 within-ayah and 119 verse-edge candidates that are
genuine wasl, a deleted/non-qata onset, a non-joinable edge, or a surah
transition. Conversely, it recovers eight within-ayah qata onsets written as
plain alif plus a combining hamza that the scalar-only scan missed. The
result is 1,550 within ayahs plus 180 joinable adjacent-ayah edges in the same
surah.

This large regular set is machine-owned. Its row predicate stores the source
and canonical refs of both words, host kind, qata vowel, and the exact source
evidence. It is not a hand-written 1,730-row exception list. The count is a
conformance assertion for the selected artifact.

Representative exact source cases are:

| Host | Selected source and refs | Canonical refs | Joined result span |
| --- | --- | --- | --- |
| Ordinary consonant | `قَدَ اَفْلَحَ`, 23:1:1-2 | 23:1:1-2 | `q aˤ d a f l a ħ a` |
| Tanwin noon | `عَذَابٌ اَلِيمٞۖ`, 2:103:11-12 | 2:104:11-12 | `... b u n a l i: m` |
| Tanwin noon before U | `يَوْمٍ ا۟جِّلَتْ`, 77:12:2-3 | 77:12:2-3 | `... m i n u ʒʒ i l a t` |
| Feminine taa | `بَغَتِ اِحْد۪يٰهُمَا`, 49:9:9-10 | 49:9:9-10 | `... t i ħ d ɛ: ...`; the omitted final nucleus is the ordinary selected Warsh taqlil result |
| Leen waw | `تَعَالَوَاْ اَتْلُ`, 6:152:2-3 | 6:151:2-3 | `... w a t l u`; the transferred A is on the existing waw host and the qata onset is absent |

In the last row the canonical host is a consonantal leen waw, it receives
short A, and the following qata is silenced.

## Boundary matrix for ordinary naql

For `قَدْ أَفْلَحَ`, the boundary outcomes are:

| Boundary state | Relevant sequence | Rule result |
| --- | --- | --- |
| Joined across the two words | `q aˤ d a f l a ħ a` | Emit `naql`; realize A on dal and silence the qata onset. This remains true if the reader later stops on `أفلح`. |
| Complete stop on `قد` | `q aˤ d Q`; if the requested range continues, then `ʔ a f l a ħ a` starts a new phrase | No naql across the stop. Ordinary qalqala owns `/Q/`; a following included word is ibtidaa with restored qata, not an unperformed word. |
| Ibtidaa at `أفلح` | `ʔ a f l a ħ a` | Restore the full qata onset and its A nucleus; no naql. |

Qata restoration is mandatory outside the joined boundary. Treating the
selected initial plain alif as WASL would incorrectly emit a hamza-wasl start
rule, lose
the qata on ibtidaa, and apply the wrong collision logic.

## Definite-article naql

The article lam is treated as the eligible host when the lexical base begins
with qata, such as `الأرض`, `الآخرة`, `الإيمان`, `الأولى`, and `الآن`. Although
article and base are one source word, this is the established article branch
of naql, not the exceptional medial-word rule. The qata vowel moves to lam and
the qata onset stays absent. Al-Nashr explicitly preserves this naql at
ibtidaa and gives the hamza-versus-lam starts
([source](https://www.islamweb.net/ar/library/content/70/114/)).

The complete selected-corpus register has 1,307 such article words. Of these,
1,283 retain a written article wasl alif, 22 suppress it after a prefixed lam
(`لِلْ...`, `لِّلْ...`, `وَلِلْ...`, `وَلَلْ...`, or `لَلْ...`), and the two
interrogative `ءَآلْـَٔـٰنَ` tokens at source/canonical 10:51 and 10:91 keep
the same internal root-qata naql. The public `istifham_article` choice owns
the preceding article-wasl treatment in those two words; it does not suppress
the internal `naql` rule. A prior 1,299 count was incomplete: it added only
16 of the 22 suppressed-alif prefix shapes to the 1,283 written-alif forms,
and omitted the remaining six prefix shapes plus the two interrogative
tokens.

For `اِ۬لَارْضِ`, source 2:10:7, canonical 2:11:7:

| State | Relevant sequence | Named rules |
| --- | --- | --- |
| Joined from a preceding word | `... l a rˤ dˤ i` | `naql` on lam/A/qata, plus `hamza_wasl_silent` on the article's genuine initial WASL unit. |
| Ibtidaa, `article_ibtidaa=hamza` | `ʔ a l a rˤ dˤ i` | `hamza_wasl_fatha` plus the same internal `naql`. |
| Ibtidaa, `article_ibtidaa=lam` | `l a rˤ dˤ i` | The start omits the article WASL unit; internal `naql` remains. |
| Waqf on the word | `... l a rˤ dˤ Q` | Internal `naql` remains; ordinary qalqala owns `/Q/` on the final dad. |

The qata hamza is never restored in this article family. `ٱلِاسْمُ` shares the
public start selector but is not a naql site: its internal onset is another
wasl hamza whose deletion has a different derivation.

## Fixed and selectable exceptions

### `ردءا`

`رِداٗ`, source and canonical 28:34:9, is the one within-word lexical naql
exception. Nafi transfers the hamza's A to dal and deletes the hamza in every
state ([Al-Wafi](https://islamweb.net/ar/library/content/245/18/)). Its actual
joined context `رِداٗ يُصَدِّقْنِےٓۖ`, source and canonical 28:34:9-10, is
`r i d a j̃ u sˤ aˤ dd i q Q n i:`: ordinary tanwin-to-yaa idgham owns
`/j̃/`, and ordinary qalqala owns `/Q/` on the sakin qaf. Complete waqf is
`r i d a:`, where `madd_iwad + madd_tabii` own the pausal long. Both states
emit `naql`; the waqf state additionally emits those two madd rules.

The selected source already writes the transformed form with no visible
hamza. Authored Warsh data supplies the latent qata responsibility so the
result can still explain why dal has A. This is not isqat and does not create
an `isqat` rule.

### `كتابيه إني`

The boundary `كِتَٰبِيَهْۖ إِنِّے`, source 69:18:9 -> 69:19:1, canonical
69:19:9 -> 69:20:1, has the public `kitabiyah_inni` choice. Al-Wafi confirms
both tahqiq and naql in connection and identifies tahqiq as the preferred
face ([source](https://islamweb.net/ar/library/content/245/18/)).

| Selected value | Wasl sequence | Rules |
| --- | --- | --- |
| `tahqiq` | `... h ʔ i ñ i:` | Haa remains sakin and qata is fully realized; no naql. Ordinary noon ghunnah owns `/ñ/`. |
| `naql` | `... h i ñ i:` | Emit `naql`; haa receives I and the qata onset is silent. Ordinary noon ghunnah owns `/ñ/`. |

A stop on `كتابيه` or ibtidaa at `إني` makes the selector inactive and
restores ordinary haa/qata behavior. Its public independence from
`maliyah_halak` is documented in [`docs/variants.md`](../../../variants.md).

## Rule reach and source evidence

Every `naql` occurrence names the latent or explicit qata as the transformed
source and the preceding consonant or nunation as its host. It reaches the
transferred A, U, or I sound. Source and transformed views place it on the
visible host vowel and the silenced/replaced qata units according to their
actual sound ownership or silence; a source haraka or deletion sign remains
attestation inside its owning unit rather than becoming an extra rule target.

The selected mushaf may draw the deleted qata with the same general kind of
small stroke used near hamzat al-wasl. Classical dabt explicitly distinguishes
the naql stroke from the wasl sign even though both indicate absence in joined
speech ([Daleel al-Hayran](https://www.islamweb.net/ar/library/content/243/298/)).
Projection must preserve that semantic distinction.

Under the single-script decision, the reviewed written-naql family supplies
the latent qata, its transferred vowel, and the host relation; the canonical
predicate and the 1,550/180/1,307 counts remain its conformance
reconciliation. The boundary plan still decides performance: qata restoration
at ibtidaa or across a stop is canonical behavior the written joined form
cannot express, so the latent structure is mandatory regardless of how the
fact was supplied.
