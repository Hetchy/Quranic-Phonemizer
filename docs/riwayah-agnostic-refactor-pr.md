# PR: Rebuild the phoneme pipeline around canonical recitation data

## Context

The legacy implementation produced correct Hafs output, but its runtime model
mixed source Unicode, mutable letter objects, Tajweed decisions, output symbols,
display projections, and location-specific fixes. Adding Warsh on top of that
shape would have duplicated Hafs assumptions rather than isolating what is
actually shared.

This PR replaces that runtime with a smaller phoneme-only pipeline. It keeps the
existing `stop_signs` and `stop_refs` API and freezes the legacy Hafs phoneme
output before changing the implementation. It does not claim to implement
Warsh phonology or the future Tajweed/letter-alignment projections.

## What changed

- Source text is parsed into canonical typed graphemes before pronunciation.
- A riwayah resource boundary selects the corpus, source aliases, and explicit
  exceptions. Unsupported Warsh execution fails closed.
- Phonological rules operate on typed letters, harakat, tanween, small vowels,
  consonants, vowels, nasals, and releases rather than output strings.
- Rendering is the only step that assigns IPA/custom inventory symbols.
- Shared YAML stores finite facts and mappings. Conditional behavior stays in
  Python.
- Hafs location exceptions are typed numeric locations with named handlers;
  they are not arbitrary replacement phoneme strings.
- The old `StopMode` abstraction and `IdghamKind.NONE` classifier were removed.
- Research, editable corpus sources, build tools, runtime data, and tests now
  have separate roots.

## Runtime structure

```text
quranic_phonemizer/
  api.py                 public Phonemizer entry point
  engine.py              pipeline orchestration and requested boundaries
  corpus.py              packed corpus and reference resolution
  parsing.py             source scalar to canonical grapheme parsing
  model/
    orthography.py       canonical script vocabulary and source ledger
    segments.py          phonological output values
    recitation.py        realized words and boundaries
  rules/                 shared pronunciation algorithms by concern
  rule_data.py           typed loading of finite shared rule facts
  hafs.py                explicit Hafs-only contextual exceptions
  rendering.py           segment to output inventory symbol
  result.py              phoneme-only public projection
  resources.py           riwayah resource selection
  data/
    shared/              render inventory, muqattaat names, shared facts
    riwayat/hafs/         aliases, exceptions, and packed corpus

corpus_sources/          editable, non-runtime corpus inputs
research/                non-runtime notes and generated evidence
tools/                   executable build and snapshot tooling
tests/                   committed full-corpus phoneme gates
```

The former one-file `corpus/`, `script/`, `render/`, `projections/`, and
`riwayat/` packages were collapsed into named modules. Empty legacy
`resources/` and `symbols/` paths were removed.

## Data conventions

The typed model is the canonical vocabulary. Hafs `script.yaml` does not list
every letter, harakah, tanween mark, or small vowel again. Its `aliases` map
contains only non-identity source encodings, and the parser can map any source
scalar to any canonical letter/harakah/tanween/small-vowel scalar. This is the
many-to-one boundary needed for open/closed tanween or other script-specific
encodings.

Arabic and phoneme symbols are plain YAML scalars so quote glyphs do not obscure
them. Unordered finite letter groups are YAML lists. Ordered lexical forms such
as muqattaat spellings and lafz al-jalalah skeletons remain strings because
their order is the fact being represented. Exception locations are numeric
triples such as `[41, 44, 9]`, not colon-delimited magic strings.

The remaining repeated letter keys in `render.yaml` are not a second alphabet
declaration. They define the separate canonical-letter-to-output-symbol
relationship. Shared rule lists likewise define membership in phonological
classes, not letter identity.

## Hafs contextual pronunciation audit

The old contextual-pronunciation file contained six behaviors. They now have
the following ownership:

| Legacy case | Current ownership | Reason |
|---|---|---|
| `41:44:9` second hamza | typed Hafs exception | one location; the glyph pattern is not evidence of a general rule |
| `11:41:6` imala | source mark plus shared raa/vowel realization | `۪` explicitly encodes imala |
| `27:36:8` stopped mini ya | typed Hafs exception, stopping only | the special result is location-limited; the same source scalar occurs elsewhere |
| `2:72:4` shortened raa | typed Hafs exception | the ornamental pattern is location-limited |
| `21:88:7` mini noon | Hafs alias to canonical noon, then shared ikhfaa | `ۨ` is a source representation of noon, so context derives the rule |
| started `ٱئْتُونِى` at five locations | typed Hafs exception, starting only | genuine lexical/location exception |

Each case has a named regression test. The distinction is deliberate: a
behavior is generalized only when the source encoding has a stable semantic
meaning, not merely because a unique location can be detected from its glyphs.

## Output token semantics

One semantic segment renders to one output inventory token. A geminated
consonant remains one token because the legacy inventory treats values such as
`bb` and `rˤrˤ` as distinct tokens. Rendering duplicates the complete base
symbol, so each half retains its emphatic marker. A long vowel similarly
renders as one token such as `a:`. A focused test locks the emphatic geminate
case.

## Compatibility and regression evidence

- `phonemize(ref, stop_signs=[...], stop_refs=[...])` remains the stopping API.
- No extra stop-mode enum is exposed.
- Full Quran output is byte-identical to the frozen legacy implementation for:
  continuous recitation, verse stops, and a stop after every word.
- The gates cover all 77,433 Hafs source words.
- Parsing reconstructs every source word byte-for-byte.
- The current Hafs corpus contains 4,359 stop-sign-bearing words and no word
  with more than one stop sign, so the present singular source field is not
  lossy for the shipped corpus.

## Adversarial review findings

### Resolved in this PR

1. Canonical source symbols were declared both in Python and wholesale in
   script YAML. The YAML now stores aliases only.
2. Finite rule sets were encoded as concatenated strings. They are now lists.
3. Symbol-heavy YAML used quotes that obscured glyphs. Symbols are plain
   scalars where YAML permits it.
4. Generic package folders implied layers they did not contain. Single-file
   layers are modules now.
5. Runtime resources and two copies of Tajweed research were mixed together.
   Runtime data, research, corpus sources, and tools are separate.
6. Complete idgham classifications were loaded although they made no phoneme
   decision. Only the partial assimilation pair that changes output remains.
7. Several one-off Hafs cases had been incorrectly promoted into generic raa,
   vowel, and boundary rules. They are explicit exceptions again.
8. `LetterUnit.source` duplicated information already retained in the exact
   source grapheme ledger. It was removed.

### Lingering architectural issues

1. **The internal result is phoneme-ready, not Tajweed-projection-ready.**
   `LetterState` owns segments while rules run, but `engine.py` flattens those
   segments into `WordRealization` and discards durable letter attribution.
   Tajweed occurrences, source/target relationships, silent-letter reasons,
   and inserted realization units cannot yet be projected from the result.
2. **Rules communicate by mutation and execution order.** Noon, meem, idgham,
   hamza-wasl, and vowel logic can mutate a following or previous letter and
   mark it resolved. Exact Hafs parity proves the present order, but there is no
   explicit dependency model or rule-event ledger.
3. **No first-class Tajweed occurrence exists in runtime code.** File names and
   phonological branches implement Tajweed behavior, but they do not retain
   rule identity. This PR must not be described as delivering Tajweed
   annotations.
4. **The phonological feature model permits combinations the renderer does not
   define.** For example, a nasalized consonant bypasses gemination and
   emphasis rendering. Current rules do not create invalid combinations, but
   the model does not enforce that invariant.
5. **Warsh remains an architectural seam, not a proven implementation.** The
   generic alias map can express many-to-one source encodings, but no Warsh
   corpus, contextual rules, exception inventory, or parity fixtures are
   shipped.
6. **Some lexical tables remain exact skeleton lists.** Hamza-wasl starting
   forms and lafz al-jalalah cannot safely be reduced to a local letter pattern
   (many non-jalalah words contain shaddah lam before ha). These tables are
   justified, but they need dedicated corpus-coverage tests.
7. **The packed corpus reader trusts committed offsets and indices.** It checks
   total word count but not offset monotonicity, index bounds, trailing bytes,
   or byte order on non-little-endian hosts.
8. **Several design documents still describe the larger pre-implementation
   package tree.** They are useful decision history but are not all accurate as
   current-code documentation after the simplification in this PR.

## Merge assessment

The implementation is ready as a Hafs phoneme-only replacement: the public
projection in scope is preserved across all three full-corpus boundary modes,
source parsing is exact, and unsupported riwayat fail closed.

It is not yet a complete answer to the earlier goal of projecting Tajweed,
letter-to-phoneme attribution, silent graphemes, and realization detail from a
single clean model. Calling it "Tajweed first-class" or "Warsh implemented"
would overstate what the code proves.

## Recommended next steps

1. Reconcile the ADR target trees and implementation mapping with this smaller
   landed structure before presenting the docs as current architecture.
2. Design the smallest durable per-letter realization record that retains
   emitted segments and explicit source/target rule occurrences. Validate it
   against worked iqlab, ikhfaa, idgham, qalqala, madd, waqf, muqattaat,
   implicit-vowel, and silent-letter examples before implementing projections.
3. Make rule-order dependencies explicit through tests before attempting to
   replace mutation with a more elaborate engine.
4. Add coverage checks for the justified lexical tables and schema validation
   for resource types.
5. Add the Warsh source corpus and script aliases first. Reuse shared rules by
   default and add riwayah-specific behavior only where real Warsh evidence and
   phoneme deltas require it.
