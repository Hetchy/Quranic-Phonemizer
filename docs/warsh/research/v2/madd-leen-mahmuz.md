# Madd leen mahmuz

`madd_leen_mahmuz` classifies a sakin waw or yaa preceded by fatha and
immediately followed by hamza in the same word. The performed sound remains
the glide `/w/` or `/j/`; `:` is never added to that token. The classification
applies in wasl, waqf, and ibtidaa. Al-Wafi defines the same-word predicate and
the Warsh faces, and gives the two lexical exclusions
([Al-Wafi, madd and qasr](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1),
[Al-Wafi, focused leen discussion](https://quranpedia.net/book/436/1/83)).

Duration is not represented by the phonemizer. The received 4 and 6 count
faces therefore have the same tokens and rule occurrence; see
[`madd-counts.md`](madd-counts.md).

## Structural case

Selected source `3:48:21`, canonical `3:49`, is `كَهَيْـَٔةِ`:

```text
state       complete word tokens    rule on sound
wasl        k a h a j ʔ a t i       madd_leen_mahmuz on j
waqf        k a h a j ʔ a h         madd_leen_mahmuz on j
ibtidaa     k a h a j ʔ a t i       madd_leen_mahmuz on j
```

The final taa-marbuta behavior is independent. A word-final hamza does not
change the predicate: stopping on `شَےْءٖ`, selected source `2:19:24`,
canonical `2:20:24`, retains `/ʃ a j ʔ/` and the `madd_leen_mahmuz`
occurrence. Ordinary `madd_leen` must not be added at waqf to a glide already
classified as `madd_leen_mahmuz`; the hamza-conditioned rule is the more
specific explanation in both states. Al-Wafi explicitly applies the rule
whether the hamza follows in the middle or at the end of the word
([source](https://quranpedia.net/book/436/1/83)).

## Sound and character attribution

One occurrence has the following reach:

- The occurrence classifies the `/w/` or `/j/` glide only. The preceding vowel
  and following `/ʔ/` are conditions, not sounds being lengthened.
- Source and cell placements put it on the sakin waw or yaa that owns the
  glide. The preceding fatha and following hamza are trigger-only context and
  do not receive the rule merely because they establish the predicate. The
  core classifier still inspects them through canonical structure, including
  when the script uses a composite hamza scalar.
- A waqf rule on the word ending remains a separate occurrence. It does not
  replace or duplicate the leen-mahmuz occurrence.

The predicate is semantic, not a search for a particular hamza code point or
maddah. Canonical projection must first expose the fatha, glide, and qata
onset with source provenance. This matters at the four selected spellings
`تَاْيْـَٔسُواْ`, `يَاْيْـَٔسُ` twice, and `لِشَاْےْءٍ`: a source-only alif
stands between the written fatha and sakin yaa, but the projected performed
structure still has fatha + `/j/` + hamza.

## The five Saw'at sites

The plural family has restricted count combinations with madd badal, but the
leen-mahmuz classification itself never disappears. Al-Wafi names `سَوْءَات`
as the correlated family and distinguishes its allowed faces
([Al-Wafi, the Saw'at combinations](https://quranpedia.net/book/436/1/83)).
The exact research-only count pairs are recorded in
[`madd-counts.md`](madd-counts.md).
The selected corpus contains exactly five sites:

| Selected source ref | Canonical ref | Exact selected text |
| --- | --- | --- |
| `7:19:10` | `7:20` | `سَوْءَٰتِهِمَاۖ` |
| `7:21:8` | `7:22` | `سَوْءَٰتُهُمَا` |
| `7:25:8` | `7:26` | `سَوْءَٰتِكُمْ` |
| `7:26:15` | `7:27` | `سَوْءَٰتِهِمَآۖ` |
| `20:118:5` | `20:121` | `سَوْءَٰتُهُمَا` |

For every row the relevant wasl and ibtidaa span is `/s a w ʔ a:/` and the
`/w/` receives `madd_leen_mahmuz`; the following long receives
`madd_badal` plus its effective madd tag. Waqf changes only the word ending.
The phonemizer exposes no selector or count correlation for this family.

The singular `سَوْءَةَ` is not in this special count family. Its two selected
occurrences, source `5:33:10` and `5:33:21`, canonical `5:31`, still satisfy
the ordinary structural `madd_leen_mahmuz` predicate. This counterexample
prevents an implementation from keying the classifier to the plural spelling
alone ([Al-Wafi uses the singular as the ordinary example](https://islamweb.net/ar/library/content/245/13/%D8%A8%D8%A7%D8%A8-%D8%A7%D9%84%D9%85%D8%AF-%D9%88%D8%A7%D9%84%D9%82%D8%B5%D8%B1)).

## Exactly two no-rule exclusions

Al-Wafi excludes exactly the first waw of `اَ۬لْمَوْءُۥدَةُ` and the waw of
`مَوْئِلاٗ`. Here traditional qasr means an unlengthened glide, not a
two-count long vowel ([focused source](https://quranpedia.net/book/436/1/83)).

| Selected source ref | Canonical ref | Exact selected text | Required result |
| --- | --- | --- | --- |
| `18:57:19` | `18:58` | `مَوْئِلاٗۖ` | The `/w/` has no `madd_leen_mahmuz` in any state. When joined into the following `وَتِلْكَ`, the span is `/m a w ʔ i l a w̃ a .../`: ordinary tanwin-to-waw idgham owns `/w̃/`. Waqf is `/m a w ʔ i l a:/`, with `madd_iwad + madd_tabii` on the final `/a:/`. |
| `81:8:2` | `81:8` | `اَ۬لْمَوْءُۥدَةُ` | The first `/w/` has no `madd_leen_mahmuz`. The second waw represents `/u:/` and independently receives `madd_badal` plus `madd_tabii`. |

For `اَ۬لْمَوْءُۥدَةُ`, the relevant started sequence is
`/ʔ a l m a w ʔ u: d a t u/`; at waqf its ending changes according to the
shared taa-marbuta rule, while the two waw decisions remain unchanged. No
source unit or transformed cell in the excluded fatha-waw-hamza span may carry
`madd_leen_mahmuz`.

These are classifier exclusions only. They are not variants and they do not
remove the independently valid badal classification from the second waw of
`اَ۬لْمَوْءُۥدَةُ`.

## Ownership and acceptance checks

- Shared canonical structure supplies the fatha + sakin glide + qata
  adjacency and source provenance.
- The Warsh rule package binds the structural classifier and owns the two
  no-rule exclusions. The five Saw'at entries are a closed research register
  for count verification, not runtime branching.
- The pinned selected corpus reconciles to exactly 304 semantic candidates:
  297 ordinary cases (including the two singular `سَوْءَةَ` occurrences), five
  plural Saw'at cases, and the two no-rule exclusions. The emitted total is
  therefore exactly 302 `madd_leen_mahmuz` occurrences. Assert all four
  subtotals so that a source-codepoint scan cannot silently replace the
  canonical predicate.
- Tests cover waw and yaa, medial and final hamza, wasl/waqf/ibtidaa, both
  exclusions, the second waw badal in `اَ۬لْمَوْءُۥدَةُ`, all five Saw'at
  sites, and sound/character reach.
- No duration token, duration selector, or count validator is introduced.
