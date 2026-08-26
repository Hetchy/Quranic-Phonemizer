# Warsh phoneme and rule inventory

This document defines the typed sound and rule vocabulary used by the Warsh
research specifications. It is a modeling contract, not a claim that every
token below is a narrow acoustic transcription. Domain sources establish the
relative sound and the recitation rule; the project representation states how
that fact is preserved in the phonemizer.

Public selector IDs, values, defaults, and scopes remain in
[`docs/variants.md`](../../../variants.md). The other v2 documents own the
triggers, boundaries, and exception registers for the rules listed here.

## Sequence notation

Manual examples use the project's IPA-like output tokens, separated by spaces.
`:` marks a long vowel. Gemination is encoded inside one rendered consonant
token, for example `ll` or `rˤrˤ`, rather than as two space-separated
sounds. A held ghunnah already is the complete geminated token: `ñ` for noon
and `m̃` for meem.
The qalqala release is a separate sound token, so write `d Q` or `q Q`, never
`dQ` or `qQ`. Manual sequences show the distinct `tashil`,
`emphatic_fatha`, and `emphatic_ikhfaa` outputs whenever those distinctions
apply: `ʔ̞`, `aˤ`, and `ŋˤ`, respectively. Inclination examples state the
`imala` setting when it changes the rendered token. Qalqala examples use the
collapsed `Q` token unless degree is the subject of the example. These are
valid exact alphabet tokens, not claims about the public default set.
Disabling an extra may collapse a rendered token, but it never removes the
underlying typed fact or rule occurrence.
Arabic text is copied exactly from the selected King Fahd Warsh corpus.

```text
ʔ a      plain hamza followed by fatha
ʔ̞ i     eased hamza followed by kasra
j i      consonantal yaa followed by kasra
a:       long fath
lˤ aˤ:   emphatic lam followed by its emphatic long a-vowel
```

The notation is broad. In particular, `ʔ̞` is a stable project token for an
eased hamza, not a claim that every reciter produces one invariant phone.

## Warsh vowel qualities

The transmitted ordering is fath, then taqlil, then imala kubra in the
direction of kasra and yaa. The Egyptian Ministry of Awqaf defines taqlil as
the midpoint between fath and full imala, while kubra approaches kasra and
yaa more strongly. It does not prescribe exact IPA targets
([source](https://awkafonline.gov.eg/content-sections/116/5028/%D8%A7%D9%84%D8%A5%D9%85%D8%A7%D9%84%D8%A9-%D9%88%D8%A7%D9%84%D8%AA%D9%82%D9%84%D9%8A%D9%84)).

| Typed quality | Short token | Long token | Domain meaning |
| --- | --- | --- | --- |
| `A` | `a` | `a:` | Fath. |
| `TAQLIL` | `ɛ` | `ɛ:` | Imala sughra: between fath and kubra. |
| `KUBRA` | `e` | `e:` | Imala kubra: the stronger inclination. |

`ɛ` and `e` are broad engineering representatives of the relative categories.
They are not percentages, invariant formant targets, or claims that one French
vowel exactly equals a transmitted Arabic realization.

Taqlil is an ordinary Warsh sound distinction. It is never controlled by an
extra-phoneme toggle. Kubra is a typed quality even when its distinct output
token is collapsed:

| Typed sound | `imala` enabled | `imala` disabled |
| --- | --- | --- |
| Warsh `KUBRA` | `e` or `e:` | `ɛ` or `ɛ:` |
| Warsh `TAQLIL` | `ɛ` or `ɛ:` | `ɛ` or `ɛ:` |

The renderer receives the kubra fallback from the riwayah package. It does not
branch on the riwayah name. The typed quality and the `imala` rule remain
unchanged when the token collapses.

## Tashil and ibdal sounds

Tashil is conditioned by the vowel of the eased hamza. The classical
description places an open hamza between hamza and alif, a kasr hamza between
hamza and yaa, and a damm hamza between hamza and waw
([Al-Wafi](https://www.islamweb.net/ar/library/content/245/14/)). The model
therefore keeps one eased onset plus an independent A, U, or I nucleus:

| Typed sounds | Broad tokens with `tashil` | Tokens without `tashil` |
| --- | --- | --- |
| eased hamza + A | `ʔ̞ a` | `ʔ a` |
| eased hamza + U | `ʔ̞ u` | `ʔ u` |
| eased hamza + I | `ʔ̞ i` | `ʔ i` |

The extra-phoneme setting changes only the first token. The consonant remains
typed as eased and the `tashil` rule remains present on the sound and source
hamza. A renderer that offers narrower phonetics may use the adjacent nucleus
as the easing target without changing the public sound inventory.

Ibdal is a transformation, not another phoneme. A pure replacement uses an
ordinary vowel carrier, while a moving replacement uses an ordinary waw or
yaa consonant. Al-Wafi distinguishes pure ibdal from a pronunciation retaining
hamza quality ([source](https://www.islamweb.net/ar/library/index.php?ID=12&bk_no=245&idfrom=16&idto=16&page=bookcontents_ver3)).

| Ibdal result | Typed result | Broad tokens |
| --- | --- | --- |
| Pure alif | long A | `a:` |
| Pure waw carrier | long U | `u:` |
| Pure yaa carrier | long I | `i:` |
| Moving waw | WAW + its performed A, U, or I nucleus | `w a`, `w u`, or `w i` |
| Moving yaa | YA + its performed A, U, or I nucleus | `j a`, `j u`, or `j i` |

The moving forms are consonants followed by an independently typed nucleus;
they are not long vowels merely because the replacement is waw or yaa. Fixed
Warsh forms such as `مُوَ۬جَّلاٗ`, `يُوَ۬اخِذُ`, and `لِيَ۬لَّا` require the
actual A nucleus rather than an I-only shortcut. Whether a pure carrier receives
`madd_tabii`, `madd_lazim`, `madd_badal`, or another madd classification is a
separate rule decision.

## Emphasis and coloring

The existing consonant inventory already represents light and emphatic raa and
lam:

| Typed sound | Light | Emphatic |
| --- | --- | --- |
| RA | `r` | `rˤ` |
| LAM | `l` | `lˤ` |
| A vowel | `a` or `a:` | `aˤ` or `aˤ:` |

When a raa or lam is the cause of emphasis on its A nucleus, that vowel follows
the effective consonant result regardless of how the boundary state realizes
it. The nucleus may be short A from fatha or fathatan, lexical long A from a
carrier, or stop-created long A from `madd_iwad`. Tafkheem or taghliz adds the
owner's emphasis cause; tarqiq removes only that owner's cause. The A becomes
plain only when no independent isti'la consonant or other owner still requires
emphasis.

The consonant weight and dependent-vowel coloring are two sound targets of one
occurrence. It reaches the consonant sound and the dependent A-vowel sound.
The source view places it on units that own those sounds, while the transformed
cell view places it on the consonant and rendered vowel/carrier columns. A
composite tanwin column retains its noon rule but does not receive a vowel-
color occurrence merely because its A sound is colored. This directional
propagation does not recolor an unrelated vowel before the consonant.

Lam uses `taghliz`; `tafkheem` remains the raa/general emphasis name. The
distinct terminology follows the classical Warsh lam chapter
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/190/)). Gemination
is orthogonal, so the same emphatic LAM type represents a single `lˤ` or a
geminated `lˤlˤ` token.

## Rule vocabulary

The following rules are the Warsh-specific additions or semantic refinements
to the shared rule vocabulary. `madd_badal` and `iltiqa_haraka` already exist
in the shared RAR catalogue; the Warsh package reuses them. The other rows are
new global identifiers which only the Warsh rule set binds. One identifier has
one meaning across every riwayah that binds it.

| Rule ID | Kind | Classified or changed sound |
| --- | --- | --- |
| `taqlil` | Classification | A vowel whose exact quality is `TAQLIL`. |
| `imala` | Classification | A vowel whose exact quality is `KUBRA`. |
| `taghliz` | Recoloring | A lam and its causally dependent A nucleus become emphatic. |
| `naql` | Transformation | The eligible preceding sakin receives the qata vowel and the qata onset becomes silent. |
| `madd_badal` | Classification | An eligible after-hamza long carrier with badal origin, normally replacing an underlying second hamza. General single-hamza ibdal is excluded. |
| `madd_leen_mahmuz` | Classification | An eligible sakin waw or yaa immediately followed by hamza. |
| `madd_mim_al_jam` | Classification | The joined-only long U of the plural-pronoun mim before qata. |
| `madd_yaa_zawaid` | Classification | A retained extra yaa realized as joined-only long I. |
| `iltiqa_haraka` | Transformation | A preceding consonant or nunation receives the required A, I, or U repair vowel after wasl elision. |

`iltiqa_haraka` replaces the overly narrow name `iltiqa_kasra`: Warsh has
authenticated U repairs as well as the ordinary I repair. The vowel quality is
carried by the resulting sound, not encoded in the rule name.

The following existing shared identifiers retain their established meaning:

- `tashil` classifies an eased hamza, regardless of token collapse;
- `ibdal_hamza` names replacement of a hamza by a vowel carrier or moving
  consonant;
- `tafkheem` and `tarqeeq` classify the effective raa/general weight;
- `madd_tabii`, `madd_muttasil`, `madd_munfasil`, `madd_lazim`,
  `madd_arid_lissukun`, `madd_leen`, `madd_iwad`, `madd_badal`, and
  `madd_silah` keep their shared meanings;
- `hamza_wasl_fatha`, `hamza_wasl_kasra`, and `hamza_wasl_damma` name the
  three start vowels separately; `hamza_wasl_silent` names the joined
  deletion; and `iltiqa_shortening` keeps its shared boundary meaning; and
- the shared noon, meem, idgham, article, qalqala, pausal, and taa-marbuta
  rules are not renamed for Warsh.

There is no `fath`, `kubra`, `isqat`, or `seven_alifs` rule ID:

- Fath is the absence of an inclination classification.
- Kubra is the exact vowel quality classified by `imala`.
- Isqat in the selected corpus is canonical absence, not a performed deletion.
- The seven alifs define canonical joined/stopped vowel shapes whose existing
  madd and boundary rules classify the resulting performance.

Mim al-jam and yaa zawaid also define canonical joined/stopped shapes, but
their long results retain public identity through `madd_mim_al_jam` and
`madd_yaa_zawaid`. These coexist with the effective madd classifier, just as
`madd_silah` coexists with `madd_tabii` or `madd_munfasil` for pronoun haa.

## Rule reach

A rule is not correct merely because its identifier appears. The core
occurrence names its acted-on source unit and, when applicable, a second unit
the rule itself acts on. Trigger-only context remains private. The analysis
projection then publishes the sounds actually classified or changed and
places the occurrence on visible units and cells from sound ownership and
silence, rather than copying every core participant onto every glyph.

| Rule | Required reach |
| --- | --- |
| `taqlil`, `imala` | The vowel sound and its visible vowel/carrier cells; an inclination witness stays provenance inside the owning unit rather than becoming an independent rule target. |
| `taghliz` | The lam sound and its dependent A-vowel sound. Transformed cells place the occurrence on the lam and vowel/carrier columns, but not on a composite tanwin column. |
| `tafkheem`, `tarqeeq` on raa | The raa sound and its dependent A-vowel sound. Transformed cells place the occurrence on the raa and vowel/carrier columns, but not on a composite tanwin column. |
| `tarqeeq` on an owned lam choice | The lam and dependent A sounds and their transformed columns. Ordinary unowned light lam emits no `tarqeeq`. |
| `tashil` | The eased consonant sound and the responsible hamza source; Warsh renders the sound as `ʔ̞`. |
| `ibdal_hamza` | The replacement vowel or consonant sound and every source unit that creates or selects it: the replaced hamza or replacement spelling, plus the realized wasl unit or immediately preceding vowel witness when that context determines the result. |
| `madd_badal` | The resulting long-vowel sound, its carrier or replacement source, and the source hamza provenance that makes it badal. A transformed hamza does not remove that reach. |
| Effective madd after ibdal or on a badal carrier | The resulting long-vowel sound and the same source units that own the created carrier, plus any further causal unit required by the effective classification, such as the following fixed sukun for `madd_lazim`. |
| `madd_leen_mahmuz` | The target sakin `/w/` or `/j/` sound; the target waw/yaa and following hamza source units. The preceding fatha is a predicate only. |
| `naql` | The source qata unit, the preceding host consonant or nunation, the transferred vowel sound, and their source glyphs. |
| `iltiqa_haraka` | Only the inserted A, I, or U sound. Its transformed column and sound cell live on the boundary; the preceding consonant or nunation sound and base column do not receive the rule. The core occurrence still names the repaired slot as its subject and the wasl slot as private trigger context. |

A pure ibdal-created long vowel normally carries both `ibdal_hamza` and
`madd_tabii`. A fixed following sukun instead produces `madd_lazim`. When the
long vowel is semantically badal, `madd_badal` replaces the ordinary
`madd_tabii` classification; `madd_arid_lissukun`, `madd_lazim`, or
`madd_muttasil` may still overlap when independently applicable.

For the hamzat-wasl plus root-hamza family, ibtidaa therefore puts
`ibdal_hamza` and `madd_badal` on the result sound and the
responsible wasl/root-hamza source units. Connected speech instead puts
`ibdal_hamza` and `madd_tabii` on the result sound, the preceding vowel
witness, and the root-hamza source; `madd_badal` is absent because the
pronounced preceding hamza is absent.

Contextual madd classification must inspect the effective performed structure
after earlier hamza and boundary transformations, or be scheduled directly by
the effect that creates the long. It must not inspect only immutable canonical
long nuclei: that would miss an ibdal-created long. Conversely, a qata slot
consumed or silenced by the transformation cannot independently trigger a
second madd. `madd_badal` uses semantic provenance in addition to this
effective shape, so origin and current context remain independent classifiers.

### Additive madd identities

Tests assert the complete rule set on a long sound, including the narrow
contexts where independent madd classifications overlap:

- an ordinary Warsh badal has `madd_badal` without `madd_tabii`; at waqf,
  `madd_arid_lissukun` is added when the stop creates its context, and
  `madd_lazim` or `madd_muttasil` may likewise overlap;
- a stopped fathatan replacement has `madd_iwad + madd_tabii`;
- a joined pronoun-haa length has `madd_silah + madd_tabii`, or
  `madd_silah + madd_munfasil` before a qata hamza; and
- a general ibdal-created carrier has `ibdal_hamza` plus its effective madd,
  but receives `madd_badal` only when semantic badal origin is independently
  established.

Warsh badal therefore differs from the additive Hafs model. Its duration does
not create a `madd_tabii` tag, and counts remain outside the sound model.

## Riwayah-scoped rule sets

The `Rule` vocabulary is global so a semantic rule has one public identifier.
The active rule set is riwayah-scoped:

1. Each riwayah package binds its own classifiers by execution phase.
   Every bound classifier declares the complete `emits: frozenset[Rule]` it
   can produce; a grouped classifier is not represented by one nominal rule.
2. Generic classifier implementations receive typed tables, lexical predicates,
   variant appliers, and authored site data from that package.
3. A classifier never branches on a riwayah name.
4. A shared rule is bound in both packages under the same ID. Its tables may be
   inherited from shared data or replaced by a reviewed riwayah override.
5. A rule absent from a riwayah is not bound merely because its ID exists in
   the global vocabulary.
6. Closed lexical exceptions and occurrence registers live under the owning
   riwayah, not in shared code.
7. `tajweed_rules(riwayah)` unions the declared emitted-rule sets reachable
   from that riwayah's bound `RuleSet`, rather than reading one `.rule` field
   per classifier or returning every member of the global enum.

For example, one madd classifier may emit every applicable madd ID and one
canonical-color classifier may emit `imala`, `tashil`, or `ishmam`; their
declared sets make all of those IDs visible to the catalogue. The generic
naql classifier can be reusable code, but only the
Warsh package binds it with the al-Azraq matcher and exception data. Shared
`madd_munfasil` remains one classifier identity even when Warsh-specific
mim-al-jam data creates additional qualifying vowels.

Riwayah-scoped binding is also the ownership boundary for defaults and optional
rendering. A Warsh package supplies kubra's taqlil fallback and fixes tashil to
the eased `ʔ̞` token; the shared renderer receives those values without
inferring them from the sound alone.

The public setting distinguishes omission from an exact override:

- `extra_phonemes=None` resolves the owning riwayah's optional defaults; and
- an explicit tuple is the complete requested set, including an empty tuple
  which disables every optional token distinction.

Fixed riwayah notation is outside that set: Warsh tashil remains `ʔ̞`, and
requesting `tashil` as an extra is invalid.

## Conformance checks

The completed implementation must make these statements executable:

- every typed sound has a render token under every supported extra-phoneme
  selection;
- disabling an extra token changes no score field, sound feature, rule,
  source reach, recited spelling fact, or canonical digest;
- a rule reported by `tajweed_rules(riwayah)` is bound in that riwayah, and an
  unbound rule is absent;
- shared rule IDs have the same semantics across riwayat;
- each transformation occurrence reaches its source and result participants;
- taqlil and kubra remain distinguishable even when kubra renders as taqlil;
- tashil retains A, U, or I context even when its onset token collapses; and
- raa/lam-dependent A-vowel coloring agrees with the effective consonant
  weight in both sound and character projections.
