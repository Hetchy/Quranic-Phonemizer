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
carrier, or stop-created long A from `iwad`. Tafkheem or taghliz adds the
owner's emphasis cause; tarqiq removes only that owner's cause. The A becomes
plain only when no independent isti'la consonant or other owner still requires
emphasis.

The consonant weight and dependent-vowel coloring are two sound targets of one
occurrence. It reaches the consonant sound and source consonant, the A-vowel
sound, and every source unit responsible for that realized A, including fatha,
fathatan, a carrier/alif, or an iwad witness as applicable. This directional
propagation does not recolor an unrelated vowel before the consonant.

Lam uses `taghliz`; `tafkheem` remains the raa/general emphasis name. The
distinct terminology follows the classical Warsh lam chapter
([Al-Nashr](https://www.islamweb.net/ar/library/content/70/190/)). Gemination
is orthogonal, so the same emphatic LAM type represents a single `lˤ` or a
geminated `lˤlˤ` token.

## Rule vocabulary

The following rules are the Warsh-specific additions or semantic refinements
to the shared rule vocabulary. One identifier has one meaning across every
riwayah that binds it.

| Rule ID | Kind | Classified or changed sound |
| --- | --- | --- |
| `taqlil` | Classification | A vowel whose exact quality is `TAQLIL`. |
| `imala` | Classification | A vowel whose exact quality is `KUBRA`. |
| `taghliz` | Recoloring | A lam and its causally dependent A nucleus become emphatic. |
| `naql` | Transformation | The eligible preceding sakin receives the qata vowel and the qata onset becomes silent. |
| `madd_badal` | Classification | An eligible after-hamza long carrier with badal origin, normally replacing an underlying second hamza. General single-hamza ibdal is excluded. |
| `madd_leen_mahmuz` | Classification | An eligible sakin waw or yaa immediately followed by hamza. |
| `iltiqa_haraka` | Transformation | A preceding consonant or nunation receives the required A, I, or U repair vowel after wasl elision. |

`iltiqa_haraka` replaces the overly narrow name `iltiqa_kasra`: Warsh has
authenticated U repairs as well as the ordinary I repair. The vowel quality is
carried by the resulting sound, not encoded in the rule name.

The following existing shared identifiers retain their established meaning:

- `tashil` classifies an eased hamza, regardless of token collapse;
- `ibdal_hamza` names replacement of a hamza by a vowel carrier or moving
  consonant;
- `tafkheem` and `tarqeeq` classify the effective raa/general weight;
- `madd_tabii`, `madd_wajib_muttasil`, `madd_jaiz_munfasil`, `madd_lazim`,
  `madd_arid_lil_sukun`, `madd_leen`, and `iwad` keep their shared meanings;
- `wasl_start`, `wasl_elision`, and `iltiqa_shortening` keep their shared
  boundary meanings; and
- the shared noon, meem, idgham, article, qalqala, pausal, and taa-marbuta
  rules are not renamed for Warsh.

There is no `fath`, `kubra`, `isqat`, `mim_al_jam`, `yaa_zawaid`, or
`seven_alifs` rule ID:

- Fath is the absence of an inclination classification.
- Kubra is the exact vowel quality classified by `imala`.
- Isqat in the selected corpus is canonical absence, not a performed deletion.
- Mim al-jam, yaa zawaid, and the seven alifs first define canonical
  joined/stopped vowel shapes. Existing madd and boundary rules classify the
  resulting performance.

## Rule reach

A rule is not correct merely because its identifier appears. Its occurrence
must reach every sound and source unit that explains the transformation.

| Rule | Required reach |
| --- | --- |
| `taqlil`, `imala` | The vowel sound, fatha, carrier/alif, and any source inclination witness. |
| `taghliz` | The lam sound and source lam; its dependent A-vowel sound and the fatha, fathatan, carrier, or iwad source units that realize it. |
| `tafkheem`, `tarqeeq` on raa | The raa sound and source raa; its dependent A-vowel sound and the fatha, fathatan, carrier, or iwad source units that realize it. |
| `tarqeeq` on an owned lam choice | The lam sound and source lam; its dependent A-vowel sound and the fatha, fathatan, carrier, or iwad source units that realize it. Ordinary unowned light lam emits no `tarqeeq`. |
| `tashil` | The eased consonant sound and the responsible hamza source, even when rendered as plain `ʔ`. |
| `ibdal_hamza` | The replacement vowel or consonant sound and every source unit that creates or selects it: the replaced hamza or replacement spelling, plus the realized wasl unit or immediately preceding vowel witness when that context determines the result. |
| `madd_badal` | The resulting long-vowel sound, its carrier or replacement source, and the source hamza provenance that makes it badal. A transformed hamza does not remove that reach. |
| Effective madd after ibdal or on a badal carrier | The resulting long-vowel sound and the same source units that own the created carrier, plus any further causal unit required by the effective classification, such as the following fixed sukun for `madd_lazim`. |
| `madd_leen_mahmuz` | The target sakin `/w/` or `/j/` sound; the target waw/yaa and following hamza source units. The preceding fatha is a predicate only. |
| `naql` | The source qata unit, the preceding host consonant or nunation, the transferred vowel sound, and their source glyphs. |
| `iltiqa_haraka` | Only the realized A, I, or U vowel through `rules_on_sound()`. The repaired consonant or nunation is the source owner and exposes the rule through `rules_on_char()`, together with a written linking-haraka witness where present; its base consonant sound is not classified. |

A pure ibdal-created long vowel normally carries both `ibdal_hamza` and
`madd_tabii`. A fixed following sukun instead produces `madd_lazim`. When the
long vowel is semantically badal, `madd_badal` also classifies it. These are
independent facts on one sound, not mutually exclusive labels.

For the hamzat-wasl plus root-hamza family, ibtidaa therefore puts
`ibdal_hamza`, `madd_badal`, and `madd_tabii` on the result sound and the
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
`madd_jaiz_munfasil` remains one classifier identity even when Warsh-specific
mim-al-jam data creates additional qualifying vowels.

Riwayah-scoped binding is also the ownership boundary for defaults and optional
rendering. A Warsh package supplies kubra's taqlil fallback and its default
extra-phoneme set; the shared renderer receives those values without importing
or comparing a riwayah enum.

The public setting distinguishes omission from an exact override:

- `extra_phonemes=None` resolves the owning riwayah's defaults; and
- an explicit tuple is the complete requested set, including an empty tuple
  which disables every optional token distinction.

This distinction is required so a caller can disable a Warsh default without
changing the underlying eased, inclined, or emphatic sound facts.

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
