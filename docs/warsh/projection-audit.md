# Warsh native-cell projection audit

## Mechanical gate

Run:

```powershell
python -m tools.warsh_projection_audit
python -m tools.warsh_projection_audit --hamza
```

The audit reads the selected King Fahd Warsh corpus through the public
`Phonemizer` facade. It builds the analysis result, source view, highlights,
and both cell spellings, then serializes every public document form. It also
requires sounds, source units, rule occurrences, and boundary mergers to close
over the IDs exposed by those views. For every source scalar it requires one
of these declared destinations:

- one source-backed word cell in both views;
- a source unit expanded by a declared `CellRun` for a disjoint-letter name;
- a boundary stop-sign cell; or
- a structural boundary character, such as a separator.

The audit records the unit kind, cell role, tier, transformed status, and
route for every Unicode scalar. It retries a failed ten-ayah batch one verse
at a time so a projection failure has an exact Warsh source reference.

All 62 non-space selected-source scalars have at least one declared route.
The sweep traverses all 6214 Warsh source verses. Successful verse projections
in the current run produced 726320 character records including generated
inter-word separators; the 23 blocked verses listed below are excluded from
that count.

## Hamza forms

Each form below reaches a source-backed word cell. A combining hamza folds
with its seat into that letter cell; it is not discarded or emitted as an
unattached mini-cell.

| Code point | Glyph | Source count | Cell behavior |
| --- | --- | ---: | --- |
| `U+0621` | `ء` | 2596 | standalone hamza letter cell |
| `U+0623` | `أ` | 6179 | seated hamza letter cell; may be replaced or dropped by performance |
| `U+0624` | `ؤ` | 185 | waw-seated hamza letter cell |
| `U+0625` | `إ` | 4241 | below-alif seated hamza letter cell; may be replaced or dropped |
| `U+0626` | `ئ` | 678 | yaa-seated hamza letter cell |
| `U+0654` | `ٔ` | 622 | combining hamza above folded into its source-backed letter cell |
| `U+0655` | `ٕ` | 45 | combining hamza below folded into its source-backed letter cell |

## Warsh mark families

| Code point | Glyph | Source count | Native projection |
| --- | --- | ---: | --- |
| `U+0656` | `ٖ` | 1935 | one kasratan cell below its base |
| `U+0657` | `ٗ` | 2916 | one fathatan cell above its base |
| `U+065E` | `ٞ` | 1815 | one dammatan cell above its base |
| `U+06E2` | `ۢ` | 575 | independent attached mini-meem cell; native iqlab owner where active |
| `U+06EA` | `۪` | 2569 | sequence-classified mark folded into its owning unit |
| `U+06EC` | `۬` | 10055 | sequence-classified wasl/article mark folded into its owning unit |
| `U+06DF` | `۟` | 281 | sequence-classified damm/wasl/silence sign |
| `U+06D2` | `ے` | 2996 | source-backed yaa-family letter or carrier cell |

The mini-meem and naql haraka attestations are carried from `Reading` into
`Inscription`. A joined native mini-meem owns the iqlab nasal sound and keeps
its source character and unit IDs; the adjacent vowel or tanwin remains a
separate attached cell.

## Naql projection

Ordinary joined naql uses the written host haraka, not an inserted boundary
haraka. The host haraka owns the transferred short vowel and the naql
occurrence. The qata alif and its attached haraka remain separate
source-backed cells, both dropped and silent by the same occurrence. The
boundary has no naql column or bridge. Iltiqa remains the owner of inserted
boundary short-vowel columns.

## Known full-corpus residue

Twenty-three verses currently fail before scalar closure can be checked. They are
ratcheted in `tests/conformance/test_warsh_cell_projection.py`.

| Failure class | References |
| --- | --- |
| transformed cells omit a result sound | `2:1`, `3:1`, `7:1`, `13:1`, `26:1`, `28:1`, `29:1`, `30:1`, `31:1`, `32:1` |
| source ownership has no sound or silence | `3:93`, `27:62`, `27:64`, `27:65`, `27:66` |
| transformed sound spans an unknown column | `11:87`, `27:29`, `27:32`, `27:39`, `35:28` |
| riding cell has no main attachment | `12:90`, `37:52` |
| lexical glyph is classified as a separator | `37:53` |

These are projection blockers, not unclassified Unicode scalars. Every one of
the 62 scalar types is represented by successfully projected occurrences,
but complete occurrence-by-occurrence closure remains pending until these
23 verses close across every public view.
