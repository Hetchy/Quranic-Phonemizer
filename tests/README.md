# Test suite

Hand-authored recitation examples live under `phonemize/`. Adapter, analysis,
API, engine, schema, and conformance tests stay outside it.

## Semantic cases

Regular examples use `Case`, `StateCase`, or `VariantCase` and one
parametrized assertion:

```python
# Hafs: إِن تَنصُرُوا
StateCase(
    id="taa-sad-boundary",
    site=Site(hafs=("47:7", (4, 5))),
    states={
        "joined": Expect(
            read=through(),
            phonemes=("ʔ i ŋ", "t a ŋ sˤ u rˤ u:"),
            char_rules={"ن[1]": R("ikhfaa")},
            sound_rules={"ŋ[1]": R("ikhfaa")},
        ),
        "stopped": Expect(
            read=explicit(ibtidaa=4, waqf=(4, 5)),
            phonemes=("ʔ i n", "t a ŋ sˤ u rˤ u:"),
            char_rules={"ن[1]": R("izhar")},
            sound_rules={"n": R("izhar")},
        ),
    },
)
```

Every expected phoneme is an inventory token separated by exactly one ASCII
space. Geminates such as `ll`, `ñ`, and `m̃` are one token. Qalqala release is
separate from its consonant: `q Q`.

Put an exact source block immediately before every semantic row, including a
row created by a helper such as `wasl_case()` or `_pausal()`:

```python
# Hafs: وَبِٱلْيَوْمِ ٱلْـَٔاخِرِ
# Warsh: وَبِالْيَوْمِ اِ۬لَاخِرِ
Case(...)
```

Use one labeled line for a Hafs-only or Warsh-only site. Use both lines for a
shared site, even when the displayed words happen to look the same. The text
is the exact focused span from the packaged corpus, including its marks and
reading-specific spelling; do not normalize it, transliterate it, or add a
separate `Uthmani` line. Script-only differences remain in the relevant
`pick()` maps and selectors. The comment block belongs to the tuple/helper
invocation that creates the row, not to an inner expectation.

The source-comment style gate recomputes these lines from the corpus and
rejects missing, mislabeled, stale, or out-of-order text. Keep the full
reviewed span, boundary state, phonemes, source reach, and sound reach
together.

`Case` owns one reading state. `StateCase` keeps several boundary states for
one site together. `VariantCase` keeps the active values, default, and masked
state of one selector together; it belongs in the selector's semantic file,
not in the generic API catalogue test.

## Sites and riwayat

Semantic sites use canonical/public coordinates:

```python
Site(hafs=("2:5", (3, 4)))
Site.shared("2:5", (3, 4), riwayat=("hafs", "warsh"))
```

`case_runs()` executes every declared riwayah that is packaged and every
script that package ships. Use `pick()` only for a small script or riwayah
difference under the same domain law. A different rule, scope, or explanation
gets its own case.

Source-corpus coordinates belong in adapter fixtures, not semantic sites.
For an explicit cross-ayah boundary, the focused word numbers may continue
through the flattened next ayah; the case must provide the exact boundary
plan so the seam is visible to the reviewer.

## Boundary intents

- `isolated()` starts and stops on one focused word.
- `joining()` starts on the focused span and joins its last word forward. Do
  not use it for a hand-authored semantic row because that forward word is
  absent from the reviewed output. To test a joined seam, include both words
  in the `Site`, exact source comment, and expected phonemes, then use
  `through()` or an equivalent explicit plan that joins inside the span.
- `through()` starts on the first focused word and stops on the last.
- `explicit()` handles an interior stop, cross-ayah seam, or other exact plan.

Waqf and ibtidaa are state dimensions inside the semantic owner. Sakt is a
continuing junction, not waqf; an explicit stop masks the cross-word behavior.

## Source and sound selectors

Plain strings select a visible source glyph or exact sound token. Registered
`@selectors` identify script-neutral roles such as `@fathatan`,
`@dagger_alif`, `@small_noon`, and `@imala_mark`. A one-based `[n]` suffix is
required only when the unsuffixed selector is ambiguous and is rejected when
the target is unique.

A `named-letter/cell` string selects a transformed cell inside a fully spelled
muqattaat run. For example, `لام/@madd` selects the alif carrier in the spelled
name of lam, while `ميم/م[2]` selects the final meem in the spelled name of
meem. Arabic combining marks are ignored in the run and literal-cell names;
`@fatha`, `@damma`, `@kasra`, and `@madd` select the corresponding cell role.
The `@inserted/cell` scope selects a source-less transformed cell; for example,
`@inserted/ا` names the iwad alif created after a final hamza.

Ordinary alif, waw, yaa, and wasl alif are visible letters, so select their
literal script forms, using `pick()` only when the shipped scripts differ.
They never receive semantic aliases such as `@long_a` or `@wasl_alif`.

Subtle combining marks must use a registered selector. The registry is
sequence-aware; it is not a global Unicode alias table.

## Rule reach

Use compact source and sound maps:

```python
char_rules={"ن": R("ikhfaa")}
sound_rules={"ŋ": R("ikhfaa", "tafkheem")}
```

When the same rule is present in both maps, `assert_case()` requires one
occurrence connecting those exact targets. It does not accept unrelated
occurrences with the same rule ID.

A merger reaches both participating cells: the assimilated source and its
host. Its `char_rules` entry must therefore name both letters, while its
`sound_rules` names the resulting geminate or the separately retained
components of an incomplete merger. Muqattaat cases use `named-letter/cell`
selectors to name both expanded endpoints. The style gate rejects one-sided
merger expectations.

## Layout

A semantic file owns one coherent rule or family and normally exposes one
`CASES` collection. Keep representative morphological forms in semantic cases;
put exhaustive token registers in conformance tests. Add another file only
when a distinct domain owner would make the combined file misleading.

- `phonemize/articles/`: article lam behavior.
- `phonemize/assimilation/`: adjacent consonant mergers.
- `phonemize/emphasis/`: raa, istilaa, Allah-lam, and Hafs seen/saad choices.
- `phonemize/hamza/`: wasl, iltiqa, ibdal, tashil, and hamza meetings.
- `phonemize/nasal/`: noon, tanwin, and meem families.
- `phonemize/vowels/`: vowel state, carriers, seven alifs, and inclination.
- `phonemize/vowels/madd/`: one file per madd classifier or authored family.
- root `phonemize/` files: muqattaat, qalqala, sakt, silent letters, and taa
  marbuta.
- `adapter/`: source recognition and projection.
- `api/`: request and metadata contracts, never phonemization behavior.
- `analysis/`: native result, source, highlights, cells, facade, and wire laws.
- `engine/`: planning, neighbourhoods, interaction, and windowing.
- `schema/`: data/model validation.
- `conformance/`: corpus-wide and snapshot gates.

Variants remain the final implementation phase. Their behavior belongs in the
semantic owner; `api/test_variants.py` validates only catalogue mechanics.
