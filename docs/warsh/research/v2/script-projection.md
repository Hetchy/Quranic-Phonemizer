# King Fahd Warsh script projection

This document defines how the selected King Fahd Warsh source becomes typed
orthographic evidence and canonical reading facts. It is the normative adapter
contract for this source. It does not decide tajwid from a Unicode scalar.

The detailed historical count audit remains in
[`docs/warsh/codepoint-audit.md`](../../codepoint-audit.md). Domain rules and
manual sound outcomes belong to the other v2 documents. Source provenance,
hashes, and regeneration remain in
[`corpus_sources/warsh/README.md`](../../../../corpus_sources/warsh/README.md).

## Selected artifact

The runtime candidate is
`corpus_sources/warsh/scripts/king-fahd/quran.json`, regenerated from the pinned
upstream artifact by `tools/import_warsh_source.py`.

| Property | Required value |
| --- | ---: |
| Verse records | 6,214 |
| Lexical word records | 77,425 |
| Distinct scalars in lexical words | 62 |
| Standalone rub-el-hizb records | 0 |
| U+06DE in lexical words | 0 |

The importer removes one presentation-form verse-number glyph per verse,
14 right-to-left marks, and 435 standalone rub-el-hizb tokens before assigning
word positions. These removals are structural normalization; they do not
delete a Quranic sound.

The public script value is the existing `uthmani`, with `uthmani` as the Warsh
default. Script compatibility is keyed by `(riwayah, script)`, so
`(warsh, uthmani)` binds this King Fahd corpus and its adapter while
`(hafs, uthmani)` keeps the existing Hafs package. Reusing the style name must
not make either package reuse the other reading's corpus or source sequences.

Every retained word preserves its exact source text and source address. The
keys in `quran.json` are source addresses, not public `Location` values. Warsh
ayah numbering differs from the canonical/public numbering at some locations,
including boundaries that are split or merged differently. Research fixtures
therefore record both:

```text
source_ref:    the key in quran.json
canonical_ref: the public Quran reference
source_text:   the exact selected-script word
```

No implementation may silently substitute a Hafs coordinate for a Warsh
source coordinate.

### Address alignment contract

Import must generate a versioned, complete source-to-canonical alignment
artifact. Each retained word or aligned span records:

```text
source_ref:       location in the selected King Fahd artifact
canonical_ref:    public Quran location or aligned public span
source_boundary:  source verse membership and edge
source_ordinal:   stable lexical order within the selected artifact
```

The artifact is generated from reviewed alignment data, not a table of ad hoc
ayah offsets. It must represent split and merged verse boundaries explicitly.
Validation proves complete source-word coverage, canonical coverage, monotonic
word order, uniqueness except at declared spans, and preservation of every
source verse edge.

Runtime lookup is canonical-addressed. Public `VerseRef` and `Location` values
always mean the canonical/public address. A separate typed source-provenance
record on the inscription or grapheme retains `source_ref`, source text, and
the source artifact identity. The implementation must not overload the one
public address type with source numbering. Until that provenance and alignment
artifact exist, the selected script is research-readable but not a complete
runtime adapter.

## Projection boundary

Projection answers only these questions:

1. Which source scalars form one grapheme or meaningful sequence?
2. Which canonical letter, onset, nucleus, nunation, or structural fact does
   that sequence supply?
3. Does a mark supply the fact, merely attest it, decorate it, or carry no
   lexical unit?
4. Which exact source glyphs own the resulting canonical fact?

Because Warsh is single-script by decision, a reviewed sequence family may
answer question 2 richly: it may supply the wasl start quality, an
inclination-bearing nucleus quality, latent naql structure, a joined-only
slot, or a pausal-alif shape directly, with the research-derived predicates
and counts kept as conformance reconciliation. Projection still does not
answer whether a raa or lam is light, which selector face applies, which madd
classification applies, or any boundary-plan-dependent performance such as
qata restoration or wasl elision. Those outcomes are derived from canonical
content, boundaries, riwayah data, and variants.

## Projection classes

### Ordinary shared sequences

Ordinary Arabic letters, fatha, damma, kasra, shadda, sukun, standard hamza
seats, and the established carrier families use the shared cluster reader.
Their corpus frequency does not create a Warsh rule fork.

Letter identity remains contextual where Arabic orthography requires it. Waw
and yaa may be consonants or carriers; an alif may be a carrier, a wasl seat, or
part of a reviewed hamza sequence. The adapter emits typed evidence rather than
making that decision from the scalar name.

An ordinary U+0652 sukun written directly on alif is a silence sign: the alif
is rasm-only and cannot be a consonant. The selected artifact contains 3,716
such sequences. U+0652 on waw or yaa remains contextual because either letter
may instead be a consonant. The 220 explicit-hamza `أُوْ...` tokens and 34
latent-hamza `ا۟وْ...` tokens form one reviewed silent-waw family. The latter
is a contextual Naql spelling: ibtidaa restores a short qata damma, joined
Naql transfers that short damma, and the written waw remains rasm-only in both
states. Initial `ا۟و...` without waw sukun is the distinct sounded Warsh badal
carrier family.

### Alternate tanwin

The selected source supplements ordinary tanwin with three alternate marks:

| Source mark | Canonical value | Corpus count |
| --- | --- | ---: |
| `ٗ` | Fath nunation | 2,916 |
| `ٞ` | Damm nunation | 1,815 |
| `ٖ` | Kasr nunation | 1,935 |

Both visual forms of one quality create the same canonical nunation slot. The
exact glyph remains in the inscription, and its visual convention may be
validated against the independently derived noon/tanwin rule. It never selects
idgham, ikhfaa, or izhar by itself.

### Hamzat al-wasl sequences

The source contains no U+0671. It writes initial alif plus a haraka and one of
several small marks. U+06EC occurs 10,055 times, U+06DF 281 times, and U+06EA
2,569 times overall, but none has one global meaning.

Reviewed initial sequence families create a canonical WASL onset. The start
vowel is independently derived from the riwayah's lexical and morphological
facts, then checked against the source convention. The visible ordinary haraka
cannot be treated as that vowel in isolation:

| Selected source text | Canonical interpretation at word start |
| --- | --- |
| `اِ۬لْحَمْدُ`, source 1:1:1 | Article wasl, started with `ʔ a`, not a literal initial `i`. |
| `اَ۪بْنَ`, source 2:86:11 | Wasl noun, started with `ʔ i`, not the visible fatha. |
| `اَ۟سْتُحِقَّ`, source 5:109:12 | Warsh passive verb, started with `ʔ u`. |

The complete sequence, lexical analysis, and riwayah reading must agree. An
unreviewed initial-alif sequence is rejected rather than guessed. See
[`wasl-hamza.md`](wasl-hamza.md) for the domain derivation.

### U+06EA vowel-quality evidence

U+06EA is overloaded in this source:

- 692 occurrences belong to initial-alif wasl sequences;
- most remaining occurrences are attached to a consonant in a potential
  inclination sequence; and
- a small residue has special contexts requiring explicit fixtures.

It therefore never means `TAQLIL` or `KUBRA` by scalar identity. After the
adapter has excluded the wasl sequence family and the explicit residue
fixtures, a reviewed vowel-quality sequence supplies the inclination-bearing
nucleus quality directly. Named registers, coupled owners, and public
selectors still override or own their sites, and the domain predicates in
[`inclination.md`](inclination.md) remain the conformance reconciliation for
the supplied set.

The v1 `imalah-classification.md` file classified every word containing U+06EA
and is retained only as historical research. It is not a pronunciation
register. The normative register is generated from the predicates and authored
exceptions in [`inclination.md`](inclination.md), then reconciled against every
source witness.

### Yaa-family bases and small carriers

Yeh barree `ے` occurs 2,996 times and projects into the existing yaa/alif-
maqsura family according to its sequence. It does not add a consonant or
phoneme. The exact base remains visible in the source inscription.

Small yaa and small waw likewise require context:

- an ordinary carrier supplies the existing I or U vowel;
- a pronoun carrier may evidence the shared pronoun-silah shape;
- a Warsh yaa-zawaid site supplies an authored joined-only yaa fact; and
- a plural-mim small waw may evidence Warsh mim-al-jam.

The scalar never decides among those roles. See [`yaa-zawaid.md`](yaa-zawaid.md)
and [`mim-al-jam.md`](mim-al-jam.md).

### Mini-mim and composite tanwin

U+06E2 occurs 575 times. The selected source uses it with either bare noon or
an ordinary haraka:

| Source composition | Canonical projection |
| --- | --- |
| Noon plus mini-mim | Noon sakinah plus an iqlab attestation. |
| Fatha plus mini-mim | One fath nunation slot plus an iqlab attestation. |
| Damma plus mini-mim | One damm nunation slot plus an iqlab attestation. |
| Kasra plus mini-mim | One kasr nunation slot plus an iqlab attestation. |

The haraka and mini-mim together spell one nunation fact; the mini-mim is not a
second vowel or a pronounced meem. Iqlab is still derived from canonical noon
or nunation followed by baa. A disagreement between the attestation and the
derived rule is a validation failure.

### Hamza transformations

The selected script often writes the result of a Warsh transformation. The
adapter must retain enough underlying structure and typed provenance for the
rule engine to explain that result.

| Selected source example | Required canonical/domain distinction |
| --- | --- |
| `قَدَ اَفْلَحَ`, source 23:1:1-2 | The second word has latent qata; the moved fatha is a naql witness, not wasl. |
| `عَذَابٌ اَلِيمٞۖ`, source 2:103:11-12 | Nunation is canonical even though its received naql vowel is not a tanwin glyph. |
| `يُومِنُونَ`, source 2:2:2 | A written replacement carrier may attest ibdal without requiring a synthetic sounded hamza slot. |
| A written eased-hamza mark | It attests tashil at a reviewed site; legal alternatives and boundary restoration still come from domain data. |

Ordinary cross-word naql restores qata when starting at the second word or
stopping before it. Modeling its alif as WASL would produce false wasl rules
and make restoration impossible. See [`naql.md`](naql.md),
[`single-hamza.md`](single-hamza.md), and
[`hamza-meetings.md`](hamza-meetings.md).

Fixed isqat spellings contain no canonical hamza or sound. The absence is a
lexical projection fact and does not create an `isqat` rule or ghost unit.

### Structural and stop material

Stop signs, sajdah signs, tatweel, presentation aids, and layout marks never
create letter or vowel units. They remain structural graphemes or typed stop
advice under the selected source convention.

A stop sign supplies advice, not a tajwid outcome. The boundary resolver
combines source advice with explicit caller stops, canonical sakt facts, and
the request edge. A rule must not inspect the stop-sign glyph.

## Source evidence relations

The internal inscription model has four relation types:

| Internal relation | Public edge | Meaning |
| --- | --- | --- |
| `Evidences` | `Supplies` | The glyph establishes a named canonical fact such as letter identity, onset, vowel quality, vowel length, vowel absence, or tajwid-mark evidence. |
| `Attests` | `Witnesses` | The glyph witnesses a derived performance outcome without selecting it. |
| `Decorates` | `Decorates` | The glyph belongs to a unit but changes no canonical or performed fact. |
| `Structural` | `Structural` | The glyph belongs to layout or boundary advice and creates no lexical unit. |

Each emitted relation has exactly one of these roles. One recognized sequence
or source glyph may emit several nonconflicting relations when it carries
several responsibilities. For example, a composite tanwin-plus-mini-mim
sequence supplies one nunation fact and separately attests the derived iqlab
outcome. It may not silently supply a rule merely because the selected mushaf
prints a teaching mark.

## Lexical reading differences

The corpus text is the authority for fixed wording and morphology differences,
such as the absence or presence of a word or a different inflected form. These
differences become ordinary canonical letters and vowels through projection;
they do not require a prose patch table or a rule named after Hafs-versus-Warsh
difference.

Closed pronunciation facts not written by the source at all, such as raa and
lam weights and selector faces, belong in Warsh authored data. No second Warsh
script is planned, so the adapter may key its supplied facts to this source's
reviewed Unicode conventions.

The selected source has 1,464 relative-pronoun forms whose lam immediately
before dhal or taa does not carry every mark that spells its pronunciation.
This includes bare and proclitic forms such as `اِ۬لذِے`, `اُ۬لذِينَ`,
`اَ۬لتِے`, `بِالتِے`, and `لِلذِينَ`; some proclitic forms carry a shadda on
the preceding lam instead. Projection restores canonical `/ll a/` on the
relative-pronoun lam. It does not claim ordinary article-plus-solar-letter
words whose solar letter carries shadda, such as `اُ۬لذِّيبُ`; those retain
ordinary lam-shamsiyyah assimilation as `/ðð/`.

## Adapter acceptance checks

The Warsh adapter is complete only when all of the following hold:

- all 62 retained scalars occur in an accepted sequence or declared structural
  role;
- each overloaded scalar is tested by sequence family, including rejection of
  an unknown sequence;
- every accepted sequence has exact source-text fixtures and canonical output;
- every source word retains its original glyphs and source address;
- the generated alignment covers every source word and every canonical word or
  declared span exactly as its schema permits;
- canonical/public lookup never accepts a source coordinate by accident;
- split and merged verse boundaries round-trip through typed source provenance;
- source rule hints agree with independently derived rules across the corpus;
- every inclination, wasl, ibdal, tashil, naql, mim-al-jam, and yaa-zawaid
  witness reconciles with its domain register;
- rebuilding a recited spelling never requires a rule to inspect source glyphs;
- every retained scalar family projects into a correct `analysis/cells`
  column, including alternate tanwin, small carriers, mini-mim, the U+06EA
  families, and yeh barree, so the inspector cell grid needs no separate
  mapping layer;
- fixed lexical omissions create neither ghost units nor synthetic rules; and
- an unsupported sequence fails with its source location and scalars instead of
  receiving a best-effort pronunciation.

The projection fixtures establish what the source writes. The domain documents
and their rule tests establish what Warsh reads and performs.
