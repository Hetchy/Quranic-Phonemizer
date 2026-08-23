# Test suite

Hand-authored recitation examples live under `phonemize/`. Adapter, API,
document, engine, schema, and conformance tests stay outside it.

## Semantic cases

Regular examples use `Case`, `StateCase`, or `VariantCase` and one
parametrized assertion:

```python
# إِن تَنصُرُوا
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

Use one Arabic comment immediately before each case. Keep the full reviewed
span, boundary state, phonemes, source reach, and sound reach together.

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
- `joining()` starts on the focused span and joins its last word forward.
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

A merger reaches both written participating source letters: the assimilated
source and its host. Its `char_rules` entry must therefore name both letters,
while its `sound_rules` names the resulting geminate or the separately
retained components of an incomplete merger. A hidden terminal consonant in
a spelled muqattaat letter has no source glyph to name; that case names the
written host and hidden result sound only. The style gate rejects other
one-sided merger expectations.

## Layout

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
- `document/`: public graph, alignment, recited text, and labels.
- `engine/`: planning, neighbourhoods, interaction, and windowing.
- `schema/`: data/model validation.
- `conformance/`: corpus-wide and snapshot gates.

Variants remain the final implementation phase. Their behavior belongs in the
semantic owner; `api/test_variants.py` validates only catalogue mechanics.
