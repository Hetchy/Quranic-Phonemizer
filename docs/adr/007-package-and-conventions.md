# ADR-007: Package tree, module boundaries, data schemas, conventions

Status: **accepted**, amended after the simplicity and domain reviews.
Supersedes archived ADR-003 in full. The archived tree was never built; this one
is the target.

## 1. Package tree

```
quranic_phonemizer/
  __init__.py
  api.py                     entry point construction only

  model/                     pure data. Imports nothing from this package.
    address.py               Location, VerseRef, SlotId, SoundId, GraphemeId,
                             OccurrenceId, Riwayah, Script, Junction,
                             BoundaryPlan, KhilafId, Option, VariantSelection
    canon.py                 CanonLetter, Onset, Quality, Nucleus, Slot,
                             ScoreWord, Score, Rule, RuleFamily, Phase
    inscription.py           GraphemeClass, Grapheme, SlotFact, Spelling union,
                             StopAdvice, Inscription
    performance.py           Aspect, Sound union, NasalPlace, ReleaseKind,
                             SoundSpec, Attribution union, Occurrence,
                             Participants, Performance

  orthography/               L0 machinery ONLY. No concrete script here.
    adapter.py               ScriptAdapter protocol, Reading, Evidence
    inventory.py             scalar-inventory loader (schema, not content)
    cluster.py               shared grapheme clustering

  canon/                     L0 -> L1. Imports model + orthography.adapter.
    build.py                 the one entry: Reading -> Score. See §5.
    derive/                  one module per derivation class (§5)
    ledger.py                Ledger, Supply, Assert, loader + validation
    lexicon.py               canonical-skeleton lexicon
    spell.py                 muqattaat expansion (Slot.spelled)
    select.py                variant selection

  engine/                    L1 -> L2. Imports model only.
    classifier.py            the Classifier protocol
    plan.py                  Plan, Effect union, Verdict
    run.py                   phase driver, conflict detection, materialisation
    boundary_plan.py         plan_from_request
    laws.py                  totality + agreement assertions

  rules/                     Shared rule bodies. Imports model + engine.
    boundary.py              waqf / ibtidaa transforms (no single term)
    noon_sakinah.py  meem_sakinah.py  idgham.py  lam_shamsiyyah.py
    hamzat_wasl.py  madd.py  tafkheem.py  qalqala.py  plain.py

  riwayat/
    hafs/
      __init__.py            assembles RuleSet, adapters, resource paths
      rules.py               rules_for(HAFS)
      scripts/               THE concrete adapters live under the riwayah
        uthmani.py
        indopak.py

  render/                    Projection side. Imports model only.
    alphabet.py              Sound feature tuple -> token
    recite.py                the ADR-005 projection

  corpus/                    address resolution + the packed corpus reader
  resources.py               path bundle per (riwayah, script, notation)
  dataio.py                  YAML loading with duplicate-key rejection (keep)

  data/
    shared/tajweed.yaml
    render/<notation>.yaml
    riwayat/hafs/
      corpus/{quran_db.bin, surah_info.json}
      scripts/{uthmani.yaml, indopak.yaml}
      ledger.yaml
      lexicon.yaml
      spellings.yaml
      variants.yaml
```

**`model/` is four files, not nine.** The first draft split ~450 lines of frozen
dataclasses — which every consumer imports together — nine ways, six of them
under 40 lines forever, in a package whose own convention 10 says 100–400. Note
also that 44 modules × the convention's floor exceeds the estimate for the whole
package; the module count was wrong, not the convention.

### 1.1 Concrete adapters live under the riwayah

The first draft put `uthmani.py` and `indopak.py` flat inside `script/`, as
though a script were riwayah-agnostic. **Uthmani and IndoPak are both *Hafs*
scripts**, and that tree had no answer to "where does a Warsh script live". It
also contradicted this ADR's own data tree, which already gets it right at
`data/riwayat/hafs/scripts/{uthmani,indopak}.yaml`. Code and data now mirror
each other exactly:

```
quranic_phonemizer/riwayat/hafs/scripts/uthmani.py
quranic_phonemizer/data/riwayat/hafs/scripts/uthmani.yaml
```

`orthography/` holds only what is genuinely script-general: the
`ScriptAdapter` protocol, the inventory *schema* loader, and grapheme
clustering. It contains no scalar of any script. Adding Warsh adds
`riwayat/warsh/scripts/*.py` plus its YAML and touches nothing above.

On the name: `script/` was a poor label — it named the thing it did not
contain. `orthography/` is the domain word for a writing system considered in
general, which is precisely the seam. (`inscription/`, after the layer it emits,
was the alternative; it was rejected because `canon/` is likewise not named
`score/`, and naming one package for its output and another for its subject
would be the inconsistency.) The scoping fix is what matters; the label is a
one-line change if the owner prefers another.

**`data/riwayat/<r>/migrations/` is deleted** (ADR-001 §3.2). Git is the
migration tool.

**`engine/registry.py` is deleted**; `rules_for` lives in `riwayat/hafs/`, which
is where the one riwayah's assembly already is.

Off-runtime trees are unchanged: `tools/`, `tests/`, `docs/`,
`corpus_sources/`, `research/`.

## 2. Dependency direction

```
                       model
                     ↗   ↑   ↖
        orthography    engine    render
                  ↖       ↑
                   canon  rules
                        ↖   ↗
                        riwayat        (hafs/ = adapters + RuleSet + data)
```

| Package | May import | Must not import |
|---|---|---|
| `dataio` | stdlib, PyYAML | anything in the package |
| `model` | stdlib | anything in the package |
| `corpus` | `model` | everything else |
| `orthography` | `dataio`, `model` | `rules`, `engine`, `render`, `canon`, `riwayat` |
| `canon` | `dataio`, `model`, `orthography.adapter` | `rules`, `engine`, `render`, `riwayat` |
| `engine` | `model` | `orthography`, `canon`, `render`, `riwayat` |
| `rules` | `model`, `engine` | `orthography`, `canon`, `render`, `riwayat` |
| `render` | `dataio`, `model` | `rules`, `canon`, `engine`, `orthography` |
| `riwayat` | all of the above except `render` | — |
| `api` | all of the above except `dataio` | — |

`dataio` and `corpus` are leaves the earlier table omitted while the code
imported them. Every package that loads a resource reaches `dataio`; nothing
reaches `render`, so that permission is not granted until a caller needs it.

The table above is the one `tools/structure_lint.py` enforces, in both
directions: an edge it does not permit is an error, and so is a permission
nothing uses. No module may be reachable from itself.

`riwayat` binds one riwayah's adapters, its `RuleSet` and its resource paths.
`api.py` is the composition root above it: `recitation(riwayah)` returns a
`Recitation` holding everything that riwayah needs, and `Recitation.read`,
`.build` and `.perform` are the only calls a consumer makes. Nothing imports
either, which is what keeps a second riwayah additive -- it is one row in
`api.PACKAGES` and one package under `riwayat/`.

Riwayah identity travels with the data rather than as an argument. An
`Inventory` declares its riwayah and script and is rejected if the caller
believed otherwise; a `Reading` carries the riwayah its inventory declared;
`Score` takes it from the `Reading` and `Performance` from the `Score`. No
function on the path accepts a riwayah a caller could get wrong.

Two rules carry design weight and are tested, not merely documented:

- **`rules` must not import `orthography`.** The packaging expression of
  ADR-001 §1's one-way reference. With the absent grapheme field on
  `Performance`, two independent guards on one property.
- **`render` must not import `rules`, `canon` or `engine`.** A projection cannot
  re-detect a rule if it cannot import a classifier. Complements ADR-002 §5.

A consequence worth naming: `rules` cannot import `canon`, so the waṣl helping
vowel cannot be a `BOUNDARY`-phase decision — the waṣl derivation is not
legally reachable from a rule (ADR-003 §6.3).

Check: `tools/structure_lint.py` walks the AST of every module and asserts the
table, as a CI job of its own. It is the only defence that survives a careless
rewrite.

## 3. Data-file schemas

Every file carries `schema_version: 1`, is loaded through `dataio.load_yaml`
(duplicate keys rejected) with an exhaustive key check. **Data holds facts. No
file may contain a phoneme string, a rule-tag list, or an effect.** The one
exception is `data/render/`, whose entire purpose is the output alphabet and
which no rule may read.

### `data/riwayat/<r>/scripts/<script>.yaml` — the scalar inventory

Total over the script's scalars; an unlisted scalar is a parse error (L3).

```yaml
schema_version: 1
script: uthmani
riwayah: hafs

letters:                       # scalar -> CanonLetter, with seat folding
  "ا": ALIF
  "ٱ": {letter: HAMZA, onset: WASL}
  "أ": HAMZA
  "ى": YA
combining_hamza: ["ٔ", "ٕ"]     # folds its host seat into HAMZA

evidences:                     # scalar -> (SlotFact, value | derivation)
  "َ":  {fact: NUCLEUS, value: {kind: Short, quality: A}}
  "ْ":  {fact: NUCLEUS, value: {kind: Silent}}
  "ّ":  {fact: ONSET,   value: GEMINATE}
  "ٰ":  {fact: NUCLEUS, derivation: length_on_previous}
  "ۥ":  {fact: NUCLEUS, derivation: silah_waw}
  "۠":  {fact: NUCLEUS, value: {kind: PausalLong, quality: A}}
  "۪":  {fact: NUCLEUS, derivation: imala}
  "۬":  {fact: ONSET,   value: TASHIL}

attests:                       # scalar-in-position -> RuleFamily + anchor
  "ّ@word_initial": {family: ASSIMILATION, anchor: previous_word_final}

decorates:                     # supplies no fact, but names the slot it shows
  "ٓ":  {slot: long_nucleus}    # maddah -> the slot whose nucleus is long
  "۟":  {slot: host, constrains_host: DECORATES}
  "ا@otiose": {slot: previous}  # the otiose alef of qaaluu

advice:                        # per (riwayah, script). There is NO shared
  "ۖ": PREFERRED_CONTINUE      # stop-sign table anywhere in data/shared/.
  "ۗ": PREFERRED_STOP          # The ONLY listing of the stop-sign scalars;
  "ۚ": OPTIONAL_STOP           # they classify Spelling.Structural implicitly.
  "ۘ": COMPULSORY_STOP         # A coarser script maps to PERMITTED_STOP
  "ۙ": PROHIBITED_STOP         # rather than inventing a class (ADR-003 §5) —
  "ۛ": EITHER_STOP             # IndoPak's `ؕ` is the measured case.

structural: ["۞", "۩", " ", "ـ"]   # not part of any word, not advice;
                               # the tatweel is a typographic joiner (6,404 words)

polysemous:                    # meaning is site-dependent; the Ledger resolves
  "ۜ": [SAKT, KHILAF_SITE]     # it, never the scalar
```

Changes: `attests` names a `RuleFamily`, not a `Rule` (ADR-003 §4.1) — the first
draft made the adapter classify the idghām family. The stop-sign scalars are
listed once, under `advice:`; the first draft listed them under `structural:` as
well.

`polysemous` is not decoration. Uthmani `ۜ`, IndoPak `ࣝ`, IndoPak `ࢵ`, IndoPak
`ؔ` and IndoPak `ٖ` are all polysemous (ADR-003 §6.6). Declaring the ambiguity
forces the adapter to defer to the Ledger rather than guess.

### `data/riwayat/<r>/ledger.yaml`

```yaml
schema_version: 1
riwayah: hafs

supplies:
  - {slot: "2:245:14#5", skeleton: "ويبصط", fact: LETTER, value: SEEN,
     citation: "Shatibiyyah; khilaf site 1 of 4"}
  - {slot: "27:36:8#7", skeleton: "ءاتىن", fact: ONSET, value: SILAH,
     citation: "Hafs; pronoun ya dropped at waqf"}

asserts:
  - {script: uthmani, slot: "2:245:14#5", skeleton: "ويبصط",
     fact: LETTER, value: SEEN}
  - {script: indopak, slot: "88:22:3#3", skeleton: "بمصيطر",
     fact: LETTER, value: SEEN}
```

`condition:` is gone (ADR-001 §3.6). `skeleton:` is mandatory and validated,
which keeps a verse-scoped ordinal reviewable and catches ordinal drift.

Loader rejects: duplicate `Supply` for one key; out-of-vocabulary value; orphan
`Assert`; a key that is not a `SlotId`; a mismatched `skeleton`; a value in
output vocabulary.

### `data/riwayat/<r>/lexicon.yaml`

Canonical skeletons — script-independent by construction.

```yaml
schema_version: 1
allah: ["ءلله", "وءلله", ...]                # 12 skeletons, 2,704 words
wasl_article: {prefix: [HAMZA, LAM], onset: WASL, helping_vowel: A}
wasl_particles: ["ءن", "ءذ", "ءذا"]           # ~3; the rest is 3 rules, not a list
wasl_exempt: [...]                           # <=30: proper nouns, form-IV nouns
silah_exempt: [...]                          # ~169 skeletons
otiose_waw_alif: {rule: final_waw_then_alif} # 3,640 sites
```

The `helping_vowel` field is required by ADR-003 §6.3: the waṣl slot's canonical
nucleus *is* the helping vowel, and 181 IndoPak sites evidence it.

### `data/riwayat/<r>/spellings.yaml`

```yaml
schema_version: 1
forms: ["الم", "المص", ...]                  # 14 compact forms
names: {"ص": "صَادْ", "م": "مِيمْ", ...}      # 14 recited spellings
```

Only the compact-to-spelling map is stored. Segments, letter mappings and
tajweed blocks are derived by running the spelled slots through the ordinary
pipeline; the hand-authored tajweed YAML that evidence §8 records as "assertions
rather than derivations" is deleted.

### `data/render/<notation>.yaml`

The only file containing output symbols. Keyed on the **complete** `Sound`
feature tuple, with no composition performed in Python — `"ˤ"` and `":"` move
here from `rendering.py:86-88`, emphasis is encoded one way rather than two, and
`(NOON, geminate, nasal)` maps to the single token `ñ` because that is what the
frozen snapshot contains (ADR-002 §6.1).

Two notations are expected: the IPA-style default and the restored reduced
vocabulary of the deleted `simple_mode.py`.

## 4. Naming and code conventions

0. **One transliteration convention, matching existing repository usage.**
   Measured across `docs/domain-facts.md`, the package and the frozen baselines,
   the repository already spells long vowels doubled: `idgham` (48 uses),
   `qalqala` (22), `ikhfaa` (18), `sakinah` (11), `shafawi` (9), `izhar` (7),
   **`tafkheem` (5)**, `haqiqi` (3), **`tarqeeq` (1)**. That is the convention.
   The first draft spelled these `TAFKH-I-M` / `TARQ-I-Q`, a third convention
   matching neither the repository nor the owner; they are corrected to
   `TAFKHEEM` / `TARQEEQ` throughout `Rule` and the module names.
   Do not introduce a scholarly-diacritic form (`tafkhīm`) in identifiers; prose
   may use diacritics freely, identifiers may not.

   **Rule modules take the conventional tajweed term** where one exists —
   `tafkheem.py`, `noon_sakinah.py`, `meem_sakinah.py`, `lam_shamsiyyah.py`,
   `hamzat_wasl.py`, `idgham.py`, `madd.py`, `qalqala.py`. Where no single
   conventional term covers the module's scope, an English structural name is
   correct rather than an invented one: `boundary.py` spans waqf *and* ibtidāʾ,
   and `plain.py` names an absence. Inventing `waqf_ibtidaa.py` would be worse
   than either.

1. **No type, field, enum member or file named after the symptom it fixes or the
   location it serves.** Names are domain terms (`Silah`, `PausalLong`,
   `IZHAR_MUTLAQ`) or structural terms (`Slot`, `Attribution`, `Ledger`).
   `SourceMark.SECOND_HAMZA` and `OrthographicHint.SMALL_YA_LETTER` are the
   anti-patterns. A name whose only content is "not the other X" — the first
   draft's `Spelling_` — is the same failure.
2. **Closed linguistic sets are `StrEnum`.** Closed structural unions are a
   `TypeAlias` over frozen dataclasses, consumed with `match`. The first draft
   named itself one exception to this (`Attribution`); there is now none.
3. **Prefer a union member over `Optional`.** `Nucleus.Silent`, not
   `nucleus: Nucleus | None`.
4. **One name per concept.** `Rule` is the closed enum and nothing else; the
   Protocol is `Classifier`. `RuleTag` and `SpellKind` are deleted — the first
   was a duplicate of `Rule`, the second a vestige of the flat `Spelling` record
   that ADR-003 §4 replaced with a union.
5. **Every referenced name is defined.** `Trigger`, `Length`, `SoundSpec`
   (ADR-004 §§1–2), `Option` (ADR-006 §2), `Evidence` (ADR-003 §1),
   `ReleaseKind` (ADR-002 §6). The first draft referenced six names it never
   defined; a vocabulary with undefined members is not closed.
6. **Every model type is `@dataclass(frozen=True, slots=True)`** with
   `from __future__ import annotations`. The `Plan` is the only append-only
   structure and it is not in `model/`.
7. **Comparable rules get comparable structure.** Same phase ⇒ same signature,
   same registration. No inline branch inside a generic emitter.
8. **All intra-package imports are relative.**
9. **No phoneme string outside `render/`. No raw scalar comparison outside
   the adapters.** Both are import-testable.
10. **File and function size.** Files 100–400 lines, functions under 50.
11. **Errors name the address and the two disagreeing sources.** Every law fails
    loudly with a `SlotId`; none returns a sentinel. The
    `expansion.py:42-50` pattern — the same `()` for "not muqaṭṭaʿāt" and
    "muqaṭṭaʿāt with unexpected diacritics" — is banned.
12. **Resources are instance-local.** No module-level singleton cache, no
    process-global override. Two riwayāt, two scripts and two notations must
    coexist in one process, keyed by immutable identity.

## 5. Modules at risk of growing past the size rule

- **`canon/build.py` — the largest, and the phase-1 gate itself.** It applies
  the Ledger, the three waṣl rules (ADR-003 §6.1), ~169 ṣilah
  exemption skeletons, five otiose classes, the Allah lexeme, muqaṭṭaʿāt
  expansion and variant selection, reconciling two evidence streams into
  byte-identical `Slot` tuples. **It splits by fact class, not by phase**:
  `canon/derive/` holds one module per derivation class, so each is one testable
  unit matching ADR-008 fixture 6 and each appears by name in the L1 residue
  report.
- `engine/run.py` — split by phase if it grows.
- `riwayat/hafs/scripts/indopak.py` — 85 distinct scalars and five polysemous marks. Most of
  the weight belongs in YAML; how much actually does is ADR-008 §5's phase-1
  measurement, not a premise (ADR-001 §2).

## 6. `Grapheme` carries its class and index

```python
class GraphemeClass(StrEnum):
    BASE | HARAKA | TANWEEN | SHADDA | LENGTH_CARRIER | SMALL_VOWEL
        | MADD_SIGN | SILENCE_SIGN | ANNOTATION | ADVICE | STRUCTURAL

@dataclass(frozen=True, slots=True)
class Grapheme:
    id:    GraphemeId          # (VerseRef, codepoint offset) — position-ordered
    char:  str
    cls:   GraphemeClass
    index: int                 # ordinal within its word
```

`cls` and `index` exist for one demonstrated consumer. The frozen
`character_phoneme_mappings` baseline has `role: madd` (53,155 cells) and
`role: tanween` (8,893 cells), which are **not** reconstructible from
`Spelling` alone — the carrier grapheme, the haraka grapheme and the tanwīn mark
all classify `fact = NUCLEUS`. `source_letter_index` likewise needs `index`.
Everything else in that baseline reconstructs from `Spelling`, the
`Attribution` variant, arity and `Occurrence.rule`. A projection run measured
**99.11% role agreement** (579,064 of 584,249 cells) with no rules engine at
all, which is the strongest evidence the inversion works.

### 6.1 The `role` vocabulary is ruled here, not left to the implementor

> **`role` names what the grapheme contributes to the sound.
> `Grapheme.cls` names what the grapheme is.**

The two axes are independent and the projection reads the first. The decisive
case, **3,063 cells**, is the tanwīn ʿiwaḍ alef: `tanween` by origin, `madd` by
what it does at waqf. Under the rule it is **`madd`**, which also matches the
frozen baseline and so keeps fixture 25 green. `Grapheme.cls` still records
`TANWEEN`, so nothing is lost — the origin remains queryable, it simply is not
what `role` reports.

The same rule settles the other measured disagreement classes without further
adjudication: 795 `base` vs `madd` and 231 `madd` vs `base` are carrier-or-slot
questions answered by which slot the `Spelling` names; 338 `haraka` vs `base` by
`fact`. The 758 marks the model does not classify (seen/ṣād, iqlāb, imāla) are
`Decorates` rows under ADR-003 §4.0 and fold into the base cell as the baseline
does.

## 7. What is deleted

`model/orthography.py` (`SourceMark`, `OrthographicHint`, `LetterForm`,
`LetterUnit`), `model/segments.py`'s `Nasal`, `parsing.py`, `hafs.py`,
`expansion.py`, `rule_data.py`, `rendering.py`, `resources.py`'s path bundle,
`rules/context.py`, `rules/apply.py`,
`data/riwayat/hafs/{script,exceptions}.yaml`,
`data/shared/{render,muqattaat}.yaml`. Nothing in `docs/archive/` is a reference
for the replacements.
