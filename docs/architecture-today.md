# Architecture today — the current codebase, for the phase-3 implementor

A snapshot of how the existing code works, so a future implementor reading
`domain-facts.md` and ADR-001/002/003 has today's context and can decide what
to build on versus restart. Written before target-model implementation;
nothing here is aspirational — this is what ships now.

The package is a Hafs-only grapheme-to-phoneme converter: give it a Quran
reference (or fuzzy Arabic text), get IPA-ish phonemes plus several mapping
views for forced alignment, tajweed highlighting, and display.

## 1. Tree

```
quranic_phonemizer/                (~7,400 lines, 35 py files; tests live separately)
├── __init__.py                    # exports Phonemizer plus many internal helpers/types
├── phonemizer.py          (713)   # entry point: Phonemizer + PhonemizeResult (the views)
├── parser.py              (462)   # text → Word/LetterSymbol; boundary annotation
├── word.py                (234)   # Word: letters, prev/next links, contextual overrides
├── loader.py              (203)   # quran_db.bin reader; ref-range → location keys
├── location.py             (34)   # "s:v:w" address value object
├── text_matcher.py        (849)   # fuzzy Arabic-text → reference resolution
├── symbols/
│   ├── symbol.py           (19)   # base: (name, char, base_phoneme)
│   ├── diacritic.py        (48)   # flyweight haraka/tanween holder
│   ├── extension.py / other.py / stop.py   # thin data holders
│   └── letters/
│       ├── letter.py      (361)   # LetterSymbol: THE core — phonemize() template,
│       │                          #   trigger sets, tanween rules, idgham pair maps
│       ├── noon.py, meem.py       # noon/meem sakinah rules
│       ├── lam.py                 # Allah patterns + heavy lam
│       ├── raa.py                 # tafkheem/tarqeeq decision tree
│       ├── vowel.py       (128)   # Alef/AlefMaksura/Waw/Yaa lengthen-or-silence
│       ├── hamza_wasl.py   (97)   # ibtidaa vowel + iltiqaa repairs
│       ├── qalqala_letter.py, taa_marbuta.py
├── madd.py                (470)   # POST-PASS: find + classify long vowels (MaddMapping)
├── phonemes.py             (96)   # string predicates over phoneme tokens (":" in ph …)
├── phoneme_registry.py    (119)   # YAML loader + get_rule_phoneme + GLOBAL overrides
├── tajweed_rule.py         (92)   # the 33-rule enum + interned TajweedRuleTag
├── tajweed_classification.py (241)# cross-word merger registry (anti-drift module)
├── mapping.py             (161)   # WordMapping/LetterMapping/MaddMapping dataclasses
├── letter_phoneme_mapping.py (845)# VIEW: letter↔phonemes flat entries (aligner)
├── char_phoneme_mapping.py (1104) # VIEW: per-character Cells (finest mapping)
├── tajweed_mapping.py     (163)   # VIEW: per-grapheme rule annotations
├── phonetic_text.py       (261)   # VIEW: recited-form Arabic re-rendering
├── silent.py              (154)   # VIEW: per-grapheme silent flags (TS-shard aligned)
├── simple_mode.py          (78)   # simple-vocabulary collapse (string surgery)
├── specials.py             (49)   # muqattaat display/tajweed lookups
└── resources/                     # see ADR-003 for the target code/resource boundary
    ├── base_phonemes.yaml         # symbol registry: letters/diacritics/extensions/…
    ├── rule_phonemes.yaml         # rule output tokens (ikhfaa ŋ, nasal map, Q, …)
    ├── simple_phonemes.yaml       # simple-mode replace/collapse rules
    ├── muqattaat.yaml             # hard per-letter phonemes + tajweed for 29 openings
    ├── contextual_pronunciations.yaml  # per-location phoneme/tajweed/display patches
    ├── quran_db.bin, surah_info.json   # corpus (77,433 words) + addressing

dev/                               # not shipped
├── Quran.json                     # editable corpus source (location → text)
├── build_quran_db.py              # Quran.json → quran_db.bin (dedup, uint16)
├── reconcile_tokenization.py      # proves/polices the three views' tokenization drift
├── audit_silent_letters.py, catalog_cells.py   # analysis harnesses
├── tajweed_occurences/, unicode_occurences/    # research corpora/notes

docs/hafs/                         # the output contracts + rule research
docs/adr/                          # the phase-3 target design (001/002/003)
```

## 2. The pipeline, end to end

`Phonemizer.phonemize(ref, stop_signs=[...], stop_refs=[...])` is the only
stateful pass; everything else re-derives from its result.

1. **Resolve the reference** — `text_matcher` fuzzy-matches Arabic text to a
   `s:v:w` range if needed; `_validate_refs` bounds-checks against
   `surah_info.json`.
2. **Load words** — `loader` maps the range to location keys and raw word
   texts from `quran_db.bin`.
3. **Parse** (`parser.parse_word`) — each word's text is tokenized
   char-by-char via dispatch tables built from `base_phonemes.yaml`: a base
   letter char instantiates a `LetterSymbol` *subclass* chosen by the
   hardcoded `LETTER_CLASSES` map (ن→Noon, ر→Raa, ق→Qalqala, …); following
   chars attach as diacritic / extensions / shaddah / other-symbols.
   Muqattaat words short-circuit: their phonemes come pre-baked from
   `muqattaat.yaml`. Words are then linked (prev/next) and
   `_annotate_boundaries` sets `is_starting`/`is_stopping` from stop signs,
   verse ends, and explicit stop refs.
4. **Phonemize** — `word.phonemize()` calls `letter.phonemize()` on each
   letter in order. This is the heart and the main wart:
   - `LetterSymbol.phonemize()` (letter.py:142) is a `@final` template: it
     *temporarily mutates* the letter's diacritic/shaddah to apply
     waqf/ibtidaa transforms, calls `phonemize_letter()` (overridden per
     subclass) + `phonemize_modifiers()`, tags tajweed rules as a side
     effect, then **restores the written state** — so the recited form
     survives only in `letter.phonemes: List[str]`.
   - Rules fire through OO dispatch with **neighbour mutation**: Noon's
     idgham calls `next_letter.mark_phonemized(...)` so the target is
     skipped when its own turn comes; vowel letters *pop* the previous
     letter's short vowel to lengthen it; hamza-wasl rewrites the previous
     word's last phoneme (iltiqaa). Evaluation order is implicit in the
     left-to-right walk.
   - Phonemes are bare strings ("bb", "aˤ:", "ñ", "Q"); rule output tokens
     come from `phoneme_registry.get_rule_phoneme` (module-global, with
     runtime override globals).
   - Tajweed tags attach to *letters* (`TajweedRuleTag(rule, is_source)`),
     never to phonemes.
5. **Contextual overrides** — `word.apply_contextual_pronunciations()`
   patches phonemes/tajweed/display per `contextual_pronunciations.yaml`.
6. **Views** — the returned `PhonemizeResult` holds the `Word` graph and
   derives everything else lazily:
   - `get_mapping()` snapshots words into `WordMapping`/`LetterMapping`
     dataclasses, then runs **madd as a post-pass** (`madd.py`): re-walk the
     phoneme strings, find long vowels, attach `MaddMapping`s, classify
     types by looking at the *next phoneme* across a re-flattened global
     sequence, plus hardcoded location overrides.
   - `letter_phoneme_mappings()` / `character_phoneme_mappings()` /
     `tajweed_mappings()` / `silent_flags()` / `phonetic_text()` each
     re-walk that mapping with their own helpers, re-deriving silence
     directions, waqf-tanween redistribution, iltiqaa demotion, extension
     splitting, and cross-word mergers **independently** (three-plus copies
     of several of these; `tajweed_classification.py` exists specifically
     to stop the cross-word copies drifting, and
     `dev/reconcile_tokenization.py` polices the residual divergence).
   - `simple_mode` collapses the output vocabulary by string surgery, on
     the raw phoneme views only.

Stops/starts are caller-chosen per call, so one word has up to three
renditions; each `phonemize()` call computes exactly one traversal.

## 3. Where the domain knowledge lives today

Roughly half in data, half in code. ADR-003 records the revised ownership
rules for the replacement. Today, trigger sets, idgham pair maps, Allah patterns,
hamza-wasl patterns, vowel-compatibility lists, the raa tree, waqf
transforms, and all madd logic are **Python**; letter/diacritic chars and
rule output tokens are **YAML**; muqattaat and contextual overrides are
YAML but with raw phoneme-string payloads. The izhar throat set and sun-letter
set are implicit in control flow rather than named once. The package does not
store madd performance counts, which the revised ADRs intentionally keep out of
the phonemizer model.

## 4. Known problems (why the ADRs exist)

ADR-001 and ADR-003 record the model and resource decisions. Summary of the
current problems:
bare-string phonemes probed by string shape; realization as OO dispatch with
neighbour mutation; waqf transforms computed then discarded and re-inferred
by four views; madd as a re-walking post-pass stored in a parallel
structure; letter-level rule tags forcing per-phoneme re-matching; six views
that re-derive and measurably drift; hardcoded domain data keyed off Hafs
glyphs (the Warsh blocker); module-global state (`phoneme_registry`
overrides, loader singleton); a dual codepoint registry and several latent
bugs (see ADR-003). A test suite does exist: it includes full-surah
letter/phoneme baselines, targeted tajwīd mapping cases, and silent-letter
tests. The characterization work is to preserve that oracle and fill stable
public-boundary gaps, not to create a net from nothing.

## 5. Refactor-on-top vs start fresh — the inputs

What the target design (ADR-001/002/003) requires replacing:

- raw-glyph-dependent rule decisions and implicit neighbour mutation in the
  `symbols/` hierarchy;
- phoneme-string inspection as the carrier of domain state;
- madd and tajwīd facts re-derived by output views;
- global loader/phoneme configuration;
- hard-coded muqattaʿāt phoneme/tajwīd triples that duplicate a derivable
  recited spelling.

Exact module deletion is deliberately deferred until the side-by-side model
passes parity. Existing rule functions remain the executable specification,
and existing resource files are migrated only when their new consumer exists.

What is useful as input/evidence regardless of path:

- **The corpus artifacts and packer behavior**: `dev/Quran.json`,
  `build_quran_db.py`, `quran_db.bin`, and `surah_info.json`. The target moves
  build inputs/tools out of `dev/`, adds manifests, and loads the runtime pair
  through an immutable `RiwayahSpec`; the current global loader is not reused
  structurally.
- **`text_matcher.py`** — self-contained, feeds the API, and can consume the
  canonical script-normalization layer rather than raw-glyph tables.
- **`location.py`**, the reference grammar and bounds validation in
  `phonemizer.py`.
- **The public capabilities** exposed by `Phonemizer`/`PhonemizeResult` are a
  migration checklist. Exact method/DTO/serialization shape may be redesigned;
  every capability must be retained, intentionally changed, or retired.
- **The rule *logic* as executable specification**: `letter.py`, `noon.py`,
  `vowel.py`, `raa.py`, `hamza_wasl.py`, `madd.py` encode hundreds of
  verified micro-decisions (edge-case comments included). They should be
  read as the reference implementation while writing detectors, then
  deleted — not ported structurally.
- **The current analysis harnesses and `docs/hafs/` contracts** are behavior
  evidence. ADR-003 relocates reviewed material under `evidence/`, exploratory
  material under `research/`, and runnable tools under `tools/`.

Practical implication: the new model warrants **new foldering** (`model/`,
`script/`, `rules/`, `render/`, `projections/`, `riwayat/`, and layered runtime
data per ADR-003) built beside the old code for semantic comparison rather
than in-place mutation of `symbols/`. Exact legacy schema parity is not a gate;
the old pipeline is deleted after every current responsibility has an approved
new owner and regression coverage.
