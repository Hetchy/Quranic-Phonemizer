# Madd badal

`madd_badal` classifies a long carrier immediately after hamza, normally where
the carrier replaces an underlying second hamza. Warsh through al-Azraq
preserves that identity when the relevant hamza context is realized or is
changed by tashil, ibdal, or naql. Al-Wafi states the rule for both realized
and changed hamza and gives the three received duration faces
([Al-Wafi, madd after hamza](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1)).

The classifier is first class even though the phonemizer does not encode
counts. A fixed-qasr word still receives `madd_badal`.

## Canonical and performed result

The ordinary example is `ءَادَمَ`, selected source `2:30:2`, canonical
`2:31`. Its relevant performance in wasl, waqf, and ibtidaa is the same:

```text
source text:     ءَادَمَ
target tokens:   ʔ a: d a m a
target rules:    madd_badal + madd_tabii on a:
```

Stopping on the word removes its final short vowel but does not change the
initial long: `ʔ a: d a m`. Starting at the word produces the same initial
`ʔ a:`. The duration face never changes these tokens.

`madd_badal` is an origin classification, while `madd_tabii`,
`madd_arid_lil_sukun`, or another madd rule describes the effective context.
They may therefore coexist on one vowel. In `إِسْرَآءِيلَ`, for example, the
I-long after hamza is badal; if waqf makes the final lam sakin, that same long
also has the effective arid classification. Al-Nashr distinguishes the
after-hamza origin from the contextual and route restrictions
([Al-Nashr, madd after hamza](https://islamweb.net/ar/library/content/70/99/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%88%D9%82%D9%88%D8%B9-%D8%AD%D8%B1%D9%81-%D8%A7%D9%84%D9%85%D8%AF-%D8%A8%D8%B9%D8%AF-%D8%A7%D9%84%D9%87%D9%85%D8%B2)).

## Attribution

For a realized hamza plus carrier:

- the long-vowel sound receives `madd_badal` and its effective madd rule;
- the source hamza and the source carrier or vowel witness receive
  `madd_badal` through `rules_on_char()`;
- the effective madd occurrence reaches that same long sound and carrier; and
- the hamza sound does not receive `madd_badal`, because it is the cause, not
  the lengthened sound.

When the hamza is transformed, the transformation occurrence and both madd
occurrences retain their own identities. The responsible hamza/replacement
source glyphs must expose `ibdal_hamza`, `madd_badal`, and the effective madd
tag through character projection when all three facts apply. No tag may exist
only on a rendered phoneme.

## Modified badal and general ibdal are different

The after-hamza origin survives an independently classified change to that
hamza. A badal site changed by naql, tashil, or ibdal therefore keeps
`madd_badal`; the transformation rule reaches its own source and result
participants ([Al-Wafi, changed hamza remains in the chapter](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1)).

General single-hamza ibdal does not by itself satisfy that origin predicate.
Selected source `2:2:2`, canonical `2:3`, writes `يُومِنُونَ` for underlying
hamza replacement:

```text
source text:     يُومِنُونَ
target tokens:   j u: m i n u: n a
first u: rules:  ibdal_hamza + madd_tabii
first u: absent: madd_badal
```

The source hamza/replacement character and the `/u:/` sound both expose
`ibdal_hamza` and `madd_tabii`. If pure ibdal instead creates a long before a
fixed sukun, the effective tag is `madd_lazim`. The `ibdal` face of
`istifham_article` in `ءَآلْـَٔـٰنَ` is the model case: the replaced article
hamza and resulting `/a:/` receive `ibdal_hamza` and `madd_lazim`. See the
selector contract in [`../../../variants.md`](../../../variants.md).

An ibdal result that is a moving waw or yaa is a consonant plus short vowel,
not a long vowel, and receives no madd rule.

## Duration exceptions

These are duration facts, not removals from `madd_badal`. Al-Wafi groups two
named families and three general families under the fixed-qasr exceptions;
Al-Nashr confirms the same underlying distinctions
([Al-Wafi, exception set](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1),
[Al-Nashr, detailed exception analysis](https://islamweb.net/ar/library/content/70/99/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%88%D9%82%D9%88%D8%B9-%D8%AD%D8%B1%D9%81-%D8%A7%D9%84%D9%85%D8%AF-%D8%A8%D8%B9%D8%AF-%D8%A7%D9%84%D9%87%D9%85%D8%B2)).

| Closed family | Selected-script example | Domain count fact | Runtime classification |
| --- | --- | --- | --- |
| `إِسْرَآءِيلَ`, wherever it occurs | Source `2:39:2`, canonical `2:40` | The I-long after hamza is fixed at 2 in wasl. At a stop, an applicable pausal context may supply arid faces. | Keep `madd_badal`; add the effective madd rule. |
| The inflectional family of `يُوَ۬اخِذُ` | Source `16:61:2`, canonical `16:61` | Fixed at 2. | Keep `madd_badal` on the after-hamza A-long. The hamza transformation is independently attributed. |
| A sound consonant is sakin immediately before the hamza in the same word | `اِ۬لْقُرْءَانُ`, source `2:184:6`, canonical `2:185`; `اُ۬لظَّمْـَٔانُ`, `24:38:7`, canonical `24:39`; `مَسْـُٔولاٗۖ`, `17:34:17`, canonical `17:34`; `مَذْءُوماٗ`, `7:17:4`, canonical `7:18` | Fixed at 2 for the long after that hamza. The predicate is structural, not a four-word lookup. | Keep `madd_badal` plus the effective madd rule. |
| A carrier after a realized hamzat wasl at ibtidaa | `اُ۪يتُونِے`, source/canonical `10:79:3`; `اِ۟وتُمِنَ`, source `2:282:16`, canonical `2:283:16` | Fixed at 2 in the started state. | Keep `madd_badal + madd_tabii + ibdal_hamza` at ibtidaa. Connected wasl is the different state specified below. |
| A fathatan stop creates an iwad alif after hamza | `هُزُؤاٗۖ`, source `18:55:18`, canonical `18:56` | The stop-created alif is fixed at 2. | This long is `iwad`, not `madd_badal`; the semantic badal carrier is absent. |

The first-waw exclusion in `اَ۬لْمَوْءُۥدَةُ` does not suppress the second
waw's badal. The first `/w/` has no `madd_leen_mahmuz`; the following `/u:/`
still has all three received badal counts and receives `madd_badal` plus
`madd_tabii` ([Al-Wafi, the two distinct waws](https://quranpedia.net/book/436/1/83)).

## Related start and lexical cases

Traditional count chapters also list forms that must not be misclassified in
the runtime:

- At ibtidaa on forms such as `اَ۪يتِ`, `اُ۪يتُونِے`, and `اِ۟وتُمِنَ`, the
  realized wasl onset precedes a sakin root hamza. That root hamza is replaced
  by a same-quality long carrier. In connected wasl, the wasl onset elides but
  Warsh still replaces the exposed root hamza using the immediately preceding
  pronounced vowel. The exact state matrix is:

  | State and selected source | Relevant result | Rules on replacement long |
  | --- | --- | --- |
  | Ibtidaa at `اُ۪يتُونِے`, source/canonical `10:79:3` | `ʔ i: t u: n i:` | `ibdal_hamza + madd_badal + madd_tabii` on the first `/i:/`; `wasl_start` separately on `/ʔ/` |
  | Joined `فِرْعَوْنُ اُ۪يتُونِے`, source/canonical `10:79:2-3` | `... n u: t u: n i:` | `ibdal_hamza + madd_tabii` on `/u:/`; no `madd_badal` |
  | Joined `اَ۬لسَّمَٰوَٰتِ اِ۪يتُونِے`, source `46:3:17-18`, canonical `46:4:17-18` | `... t i: t u: n i:` | `ibdal_hamza + madd_tabii` on `/i:/`; no `madd_badal` |
  | Waqf before the host | No host sound | No replacement occurrence; a later start uses the ibtidaa row |

  Stopping on the host after either a joined or started entry does not change
  its initial replacement. In a joined row, both the preceding vowel witness
  and root-hamza source unit expose `ibdal_hamza` and `madd_tabii`; in the
  ibtidaa row, the wasl and root-hamza source units expose all three madd and
  transformation facts. Al-Wafi calls the started realization the
  after-hamzat-wasl fixed-qasr family and explicitly derives its carrier by
  replacing the second, sakin hamza; the connected replacement follows the
  ordinary single-hamza rule
  ([Al-Wafi, after hamzat wasl](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1),
  [Al-Nashr, start-only badal family](https://islamweb.net/ar/library/content/70/99/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%88%D9%82%D9%88%D8%B9-%D8%AD%D8%B1%D9%81-%D8%A7%D9%84%D9%85%D8%AF-%D8%A8%D8%B9%D8%AF-%D8%A7%D9%84%D9%87%D9%85%D8%B2),
  [Al-Wafi, connected single-hamza ibdal](https://www.islamweb.net/ar/library/content/245/17/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%87%D9%85%D8%B2-%D8%A7%D9%84%D9%85%D9%81%D8%B1%D8%AF)).
- The second long in the two `ءَآلْـَٔـٰنَ` forms, canonical `10:51` and
  `10:91`, and the changed beginning of `عَاداٗ اَ۬لُّاول۪ىٰ`, canonical
  `53:50`, have route-dependent count restrictions. Their semantic and
  transformation tags do not depend on those duration correlations
  ([Al-Nashr, these two changed cases](https://islamweb.net/ar/library/content/70/102/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%82%D9%88%D8%A7%D8%B9%D8%AF-%D9%81%D9%8A-%D9%87%D8%B0%D8%A7-%D8%A7%D9%84%D8%A8%D8%A7%D8%A8-%D9%85%D9%87%D9%85%D8%A9)).

No count or cross-count validator belongs in the phonemizer.

## Ownership and acceptance checks

- Canonical projection supplies the hamza, carrier, and their provenance.
- The Warsh rule package binds the reusable badal-origin classifier.
- The duration exception families remain research data. They do not enter the
  sound model or variant API.
- Tests cover realized, naql-changed, tashil-changed, and ibdal-changed badal;
  the three fixed-qasr classifier families; iwad as a non-badal
  counterexample; the started triple classification versus connected
  `ibdal_hamza + madd_tabii` after hamzat-wasl elision; the second waw of
  `اَ۬لْمَوْءُۥدَةُ`; and wasl, waqf, and ibtidaa attribution on both sounds
  and characters.
- A corpus audit must be able to explain every `madd_badal` from semantic
  origin, not from a maddah glyph. A maddah is evidence only.
