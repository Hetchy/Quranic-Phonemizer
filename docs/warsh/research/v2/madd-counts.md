# Warsh madd counts

This note records the received durations for Warsh through al-Azraq so that
rule names and exceptional words can be checked against the domain. Duration
is not part of the phonemizer's sound model. It is not a setting, variant, or
phoneme distinction, and tests must not infer a count from the `:` token.

The public API therefore returns the same broad long-vowel token for every
received duration. It classifies why that vowel is long. The Warsh chapter of
Al-Wafi gives the three badal faces, the two leen-mahmuz faces, and the fixed
and route-dependent exceptions ([Al-Wafi, madd and qasr](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1)).

## Count catalogue

| Effective rule | Received count for al-Azraq | Runtime consequence | Source |
| --- | --- | --- | --- |
| `madd_tabii` | 2 | One ordinary long token. | [Al-Wafi, base madd](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1) |
| `madd_iwad` | 2 | One A-long token created from final fathatan at waqf; the same sound also has `madd_tabii`. | [Al-Nashr, the stop-created replacement](https://islamweb.net/ar/library/content/70/99/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%88%D9%82%D9%88%D8%B9-%D8%AD%D8%B1%D9%81-%D8%A7%D9%84%D9%85%D8%AF-%D8%A8%D8%B9%D8%AF-%D8%A7%D9%84%D9%87%D9%85%D8%B2) |
| `madd_silah` before a non-hamza | 2 | Its joined-only long has `madd_silah + madd_tabii`. | [Al-Wafi, silah under base madd](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1) |
| `madd_muttasil` | 6 | One long token with the muttasil rule. | [Moroccan Ministry lesson on muttasil and munfasil](https://www.habous.gov.ma/%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D8%AC-%D8%A7%D9%84%D8%AA%D8%B9%D9%84%D9%8A%D9%85-%D8%A7%D9%84%D8%B9%D8%AA%D9%8A%D9%82-%D8%A7%D9%84%D8%B1%D8%A6%D9%8A%D8%B3%D9%8A%D8%A9/1703-%D8%A7%D9%84%D9%85%D8%B1%D8%AD%D9%84%D8%A9-%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89/%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF/%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF-%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89-%D8%A5%D8%B9%D8%AF%D8%A7%D8%AF%D9%8A-%D8%B9%D8%AA%D9%8A%D9%82/17848-%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF-%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%80%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1-%D8%A7%D9%84%D9%80%D9%85%D8%AF-%D8%A7%D9%84%D9%85%D8%AA%D8%B5%D9%84-%D9%88%D8%A7%D9%84%D9%80%D9%85%D9%86%D9%81%D8%B5%D9%84.html) |
| `madd_munfasil` | 6 | One long token with the munfasil rule. This includes qualifying pronoun silah, mim al-jam', retained `أنا`, and yaa-zawaid; pronoun silah also retains `madd_silah`. | [Moroccan Ministry lesson on muttasil and munfasil](https://www.habous.gov.ma/%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D8%AC-%D8%A7%D9%84%D8%AA%D8%B9%D9%84%D9%8A%D9%85-%D8%A7%D9%84%D8%B9%D8%AA%D9%8A%D9%82-%D8%A7%D9%84%D8%B1%D8%A6%D9%8A%D8%B3%D9%8A%D8%A9/1703-%D8%A7%D9%84%D9%85%D8%B1%D8%AD%D9%84%D8%A9-%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89/%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF/%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF-%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89-%D8%A5%D8%B9%D8%AF%D8%A7%D8%AF%D9%8A-%D8%B9%D8%AA%D9%8A%D9%82/17848-%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF-%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%80%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1-%D8%A7%D9%84%D9%80%D9%85%D8%AF-%D8%A7%D9%84%D9%85%D8%AA%D8%B5%D9%84-%D9%88%D8%A7%D9%84%D9%80%D9%85%D9%86%D9%81%D8%B5%D9%84.html) |
| `madd_lazim` | 6 | One long token with the lazim rule. | [Al-Wafi, madd before permanent sukun](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1) |
| `madd_arid_lissukun` | 2, 4, or 6 | One long token with the arid rule. | [Al-Nashr, route correlations at a stop](https://islamweb.net/ar/library/content/70/102/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%82%D9%88%D8%A7%D8%B9%D8%AF-%D9%81%D9%8A-%D9%87%D8%B0%D8%A7-%D8%A7%D9%84%D8%A8%D8%A7%D8%A8-%D9%85%D9%87%D9%85%D8%A9) |
| `madd_leen` at waqf | 2, 4, or 6 | The glide remains `/w/` or `/j/`; the rule records the pausal lengthening. | [Al-Wafi, ordinary leen at waqf](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1) |
| `madd_badal` | 2, 4, or 6 | The long token carries `madd_badal`; independently applicable arid, lazim, or muttasil classifications overlap it. | [Al-Nashr, madd after hamza](https://islamweb.net/ar/library/content/70/99/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%88%D9%82%D9%88%D8%B9-%D8%AD%D8%B1%D9%81-%D8%A7%D9%84%D9%85%D8%AF-%D8%A8%D8%B9%D8%AF-%D8%A7%D9%84%D9%87%D9%85%D8%B2), [route correlations at a stop](https://islamweb.net/ar/library/content/70/102/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%82%D9%88%D8%A7%D8%B9%D8%AF-%D9%81%D9%8A-%D9%87%D8%B0%D8%A7-%D8%A7%D9%84%D8%A8%D8%A7%D8%A8-%D9%85%D9%87%D9%85%D8%A9) |
| `madd_leen_mahmuz` | 4 or 6 | The same `/w/` or `/j/` token carries the leen-mahmuz rule in wasl and waqf. | [Al-Wafi, leen followed by hamza](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1) |

The identity rules coexist with the effective count rule: pronoun silah keeps
`madd_silah`, mim al-jam keeps `madd_mim_al_jam`, and a long yaa-zawaid keeps
`madd_yaa_zawaid`.

The five plural `سَوْءَات` sites are the closed combined exception. Their
received `(leen-mahmuz, badal)` pairs are `(none, 2)`, `(none, 4)`,
`(none, 6)`, and `(4, 4)`; a 6-count leen face is not received there. The
runtime nevertheless emits both semantic rule IDs in every face because it
does not encode duration
([Al-Wafi, the Saw'at combinations](https://quranpedia.net/book/436/1/83)).

The Moroccan teaching profile uses tawassut, 4 counts, for badal and
leen-mahmuz, but the other authenticated al-Azraq faces remain domain facts
([Moroccan Ministry, badal](https://www.habous.gov.ma/2012-05-28-10-40-28/1703-%D8%A7%D9%84%D9%83%D8%AA%D8%A8-%D8%A7%D9%84%D9%85%D8%AF%D8%B1%D8%B3%D9%8A%D8%A9/%D8%A7%D9%84%D9%85%D8%B1%D8%AD%D9%84%D8%A9-%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89/%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF/%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF-%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89-%D8%A5%D8%B9%D8%AF%D8%A7%D8%AF%D9%8A-%D8%B9%D8%AA%D9%8A%D9%82/17852-%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF-%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%80%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1-%D8%A7%D9%84%D9%80%D9%85%D8%AF-%D9%84%D9%84%D9%87%D9%85%D8%B2-%D8%A7%D9%84%D9%85%D8%BA%D9%8A%D8%B1-%D8%A7%D9%84%D9%80%D9%85%D8%AF-%D8%A7%D9%84%D8%B9%D8%A7%D8%B1%D8%B6-%D9%84%D9%84%D8%B3%D9%83%D9%88%D9%86-%D9%85%D8%AF-%D8%A7%D9%84%D8%A8%D8%AF%D9%84.html),
[Moroccan Ministry, leen](https://www.habous.gov.ma/component/content/article/13481-%D8%A7%D9%84%D8%AA%D8%AC%D9%88%D9%8A%D8%AF-%D8%A7%D9%84%D9%85%D8%AF%D9%88%D8%AF-%D8%A7%D9%84%D8%AE%D8%A7%D8%B5%D8%A9-%D8%A7%D9%84%D8%AC%D8%B2%D8%A1-%D8%A7%D9%84%D8%AB%D8%A7%D9%84%D8%AB.html?Itemid=766)).

## Rule identity is independent of count

- Ordinary badal remains `madd_badal` at a fixed-qasr exception. The exception
  changes duration, not semantic origin.
- A long created by general hamza ibdal is not automatically badal. It receives
  `ibdal_hamza` and the effective `madd_tabii` or `madd_lazim` rule.
- The ibtidaa carrier in `اَ۪يتِ` and related wasl-onset + root-hamza forms is
  the important exception: it has a preceding realized hamza and replaces the
  second hamza, so it receives `ibdal_hamza + madd_badal`. In connected wasl
  the wasl hamza elides and the root hamza is
  replaced from the preceding pronounced vowel; that long has
  `ibdal_hamza + madd_tabii` without `madd_badal`.
- Ordinary `ءَادَمَ` has only `madd_badal` on `/a:/`. A badal long overlaps
  with independently applicable `madd_arid_lissukun`, `madd_lazim`, or
  `madd_muttasil`. At waqf on `مَـَٔابٖۖ`, selected source `13:30:8`,
  canonical `13:29:8`, `/a:/` therefore has
  `madd_badal + madd_arid_lissukun`.
- A stopped fathatan long has `madd_iwad + madd_tabii`; iwad names the
  exchange and tabii names the resulting ordinary long structure.
- A joined pronoun-haa long has `madd_silah` plus `madd_tabii`, or
  `madd_silah` plus `madd_munfasil` before a qata hamza.
- Mim al-jam', yaa-zawaid, and retained `أنا` create canonical boundary shapes.
  The ordinary madd classifier then sees the resulting long and the following
  hamza. They do not create three new madd rule IDs.
- The five plural `سَوْءَات` sites still receive `madd_leen_mahmuz`; their
  restricted count combinations do not turn the rule off.
- The first waw of `اَ۬لْمَوْءُۥدَةُ` and the waw of `مَوْئِلاٗ` are the only
  fixed no-`madd_leen_mahmuz` exclusions. "Qasr" there means no leen madd, not
  a two-count long vowel.

## Correlations stay out of the runtime

Authenticated paths correlate some badal, arid, ordinary leen, and
leen-mahmuz counts. Al-Nashr explicitly treats those combinations as route
constraints rather than independent free choices
([Al-Nashr, count correlations](https://islamweb.net/ar/library/content/70/102/%D9%81%D8%B5%D9%84-%D9%81%D9%8A-%D9%82%D9%88%D8%A7%D8%B9%D8%AF-%D9%81%D9%8A-%D9%87%D8%B0%D8%A7-%D8%A7%D9%84%D8%A8%D8%A7%D8%A8-%D9%85%D9%87%D9%85%D8%A9)).
The phonemizer neither asks for these counts nor validates a tariq. Its tests
assert the correct long or glide sound, named rule, boundary state, and source
reach. The closed duration exceptions are retained in
[`madd-badal.md`](madd-badal.md) and
[`madd-leen-mahmuz.md`](madd-leen-mahmuz.md) only to prevent a duration fact
from being mistaken for a classifier exception.
