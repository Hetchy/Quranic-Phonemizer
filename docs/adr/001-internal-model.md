# ADR-001: Canonical internal model — grapheme-cluster tokenization + rule passes

Status: **proposed** (Epic 3a design ADR, per `docs/warsh-integration-plan.md`)

Companion: `docs/domain-facts.md` (the domain ground truth this model must
represent).

---

## 1. Context — what the current model is and why it hurts

Today's de-facto internal model is `Word → List[LetterSymbol]`, where a
`LetterSymbol` is *already* a grapheme cluster (base char + diacritic +
shaddah + extensions + marks). That part is right. The problems are in what
happens after tokenization:

1. **Phonemes are bare strings.** `letter.phonemes: List[str]`. Every property
   a view needs (is it long? geminate? nasal? render-only?) is re-derived by
   string inspection (`":" in ph`, doubled-halves checks, membership in
   hardcoded sets like `LONG_VOWELS` in `madd.py:16`). IPA literals are
   sprinkled through control flow.
2. **Realization happens as a side effect of OO dispatch.** Each
   `LetterSymbol.phonemize()` mutates itself and sometimes its neighbour
   (`noon.py` marks the next letter phonemized; `vowel.py` pops the previous
   letter's phoneme; `hamza_wasl.py` rewrites the previous word's last
   phoneme). Order of evaluation is implicit and fragile.
3. **Waqf/ibtidaa transforms are computed and thrown away.**
   `letter.py:143-178` mutates diacritic/shaddah, phonemizes, then *restores*
   the written state. The recited form survives only in the phoneme strings,
   so every view re-infers the waqf transform from
   `(written diacritic, is_stopping)` independently — `phonetic_text.py`,
   `letter_phoneme_mapping.py:252-295` (`redistribute_waqf_tanween`),
   `silent.py:91-107` (`sounding_in_flat`), and `char_phoneme_mapping.py`
   inline, four separate re-implementations.
4. **Madd is a post-pass that re-walks everything.** `build_madd_mappings` +
   `classify_madd_types` rebuild `phoneme_to_letter` index maps (three times
   in `madd.py` alone), scan a re-flattened global phoneme sequence, and store
   the result in a *parallel* structure (`MaddMapping`) that views then
   re-project (`_madd_type_indices` in char view, `_apply_madd_rules` in
   tajweed view — independently).
5. **Rule tags attach to letters, not sounds.** A letter with several phonemes
   (a muqatta'a alef sounds five phonemes) cannot say which phoneme carries
   which rule, so the char view maintains a parallel
   `phoneme_rule_tags` mechanism and matches rules to phones *by phoneme
   shape* (`_special_phoneme_tags`).
6. **Six views re-derive from scratch and drift.** `get_mapping`,
   `letter_phoneme_mappings`, `character_phoneme_mappings`,
   `tajweed_mappings`, `silent_flags`, `phonetic_text` each walk the letter
   graph with overlapping-but-different helpers. Known drift: the
   extension-split sets differ (letter view splits MADDAH, tajweed view does
   not, silent/char views split only `ٰ ۥ ۦ`); the iltiqaa and waqf-tanween
   redistributions exist in three copies; `dev/reconcile_tokenization.py`
   exists solely to police the divergence.
7. **Domain data is hardcoded** (trigger sets, idgham pair maps, Allah
   patterns, hamza-wasl patterns, location literals) — the direct Warsh
   blocker catalogued in the integration plan.

Meanwhile the **richest structure in the codebase is built last**: the char
view's `Cell` (role / status / phonemes / phoneme_indices / tag /
share_group / source letters) — with a validated coverage invariant — is
derived at the very end from everything else. It is, almost exactly, the
canonical model we lack.

## 2. Decision drivers

From the integration plan's guiding principles:

- One canonical internal model; views are pure projections.
- Tajweed is first-class (rules, sources/targets, madd subtypes on the model,
  not re-derived).
- Riwaya-agnostic shape; riwaya-specific *content* lives in data.
- Hafs output stays byte-identical through the refactor (including each
  view's current, deliberately divergent tokenization).
- Tokenization should give us the grapheme↔phoneme relationship "for free"
  rather than re-deriving it per view.

## 3. Options considered

### Option A — rich tokenizer: clusters emit phonemes at tokenization time

Tokenize straight into cluster objects that *are* the char-phoneme cells,
each knowing its phonemes. Rejected as the sole mechanism: realization is not
a function of the cluster alone. It depends on the next/previous word, the
boundary state, word patterns, the already-realized sound stream, and
per-location tables (`docs/domain-facts.md` §3). A tokenizer that resolves all
of that is just today's entangled phonemize step wearing a new name, and every
riwaya difference would fork the tokenizer itself.

### Option B — orthographic tokenization + ordered rule passes over one token stream (recommended)

Tokenization is purely orthographic and deterministic (script data only).
Realization is a fixed, explicit sequence of rule passes that *annotate* the
token stream in place, producing first-class sound objects attached to the
units they belong to. The annotated stream — words → clusters → units →
phonemes — is the canonical model; every view is a stateless projection.
This is the user-suggested "simple tokenization + post-pass with rules", and
it matches how the domain actually factors (orthography vs phonology).

### Option C — keep letter-class dispatch, store more on the way through

Minimal change: keep `phonemize()` OO dispatch but persist the waqf-transformed
state, madd types, and per-phoneme tags. Rejected: it fixes re-derivation but
keeps domain knowledge in subclass control flow (the Warsh blocker), keeps the
implicit evaluation order and neighbour mutation, and keeps phonemes as
strings.

**Decision: Option B.**

## 4. The model

Names are provisional. All classes are plain data (dataclasses); no behaviour
beyond convenience accessors. Everything glyph- or IPA-valued comes from the
riwaya's data files, never from literals.

```
Riwaya                          # the context object threaded everywhere
├── script: ScriptSpec          # codepoint classification: base letters, harakat,
│                               #   tanween, shaddah, extensions, silence marks,
│                               #   stop signs, sakt marks (Epic 1a allowlist)
├── phonemes: PhonemeInventory  # symbol → PhonemeSpec (features below)
├── rules: RuleData             # trigger sets, pair maps, word patterns,
│                               #   rule phonemes, madd lengths
├── overrides: LocationTable    # muqattaat, contextual pronunciations,
│                               #   madd overrides — (location, context) → data
└── corpus: Corpus              # per-riwaya text + addressing (Epic 3b)

Phoneme (interned, from PhonemeInventory)
├── symbol: str                 # the IPA-ish token, unchanged for output
└── features: long, geminate, nasal, emphatic_colored, render_only,
               short_vowel, vowel_quality, simple_form   # kills string parsing

Utterance                       # one phonemize() result, one traversal
├── riwaya, ref, words: [Word]

Word
├── location, text, stop_sign
├── boundary: BoundaryState     # is_starting, is_stopping (+ sakt-after flag)
├── clusters: [Cluster]
└── prev/next links

Cluster                         # == today's LetterSymbol, orthographic only
├── index_in_word
├── base: Grapheme              # char + script classification
├── haraka: Grapheme | None     # haraka OR tanween (exclusive), written form
├── shaddah: bool
├── extensions: [Grapheme]      # dagger alef, mini waw/yaa, maddah
├── marks: [Grapheme]           # silence marks, small-high letters, unknowns
└── units: [Unit]               # filled by realization; empty after tokenize

Unit                            # == today's char-view Cell, now canonical
├── role: BASE | HARAKA | TANWEEN | MADD | INSERTED
├── source: which grapheme(s) of the cluster it stands for; [] if inserted
├── status: PRESENT | SILENT | INSERTED | REPLACED | SHORTENED
├── silence_reason: RuleRef | orthographic-convention key (when SILENT)
├── phonemes: [Phoneme]         # [] if silent
├── rules: [RuleTag]            # per-UNIT tags, source/target, incl. madd
│                               #   subtype — no parallel MaddMapping
├── madd: MaddInfo | None       # type + count range, on the madd unit itself
├── share: ShareGroup | None    # joint ownership: haraka+carrier long vowel,
│                               #   idgham source+target (may span words)
└── written_delta: ... | None   # recited-form delta for phonetic_text
                                #   (waqf sukun, iwad alef, started hamza vowel)
```

Key commitments:

- **The Unit is the atom.** Today's char-view `Cell` semantics (roles,
  statuses, share groups, the "raw-walk index" invariant) are promoted from
  last-derived view to the canonical store. `phoneme_indices` disappear as
  stored data — a unit *owns* its Phoneme objects, and any flat index space
  (word-local for the char view, global for alignment) is computed by
  enumeration at projection time, which makes the invariant true by
  construction.
- **Insertions are units with no source** (hamza-wasl vowel, iltiqaa kasra,
  madd-'iwad alef, Allah dagger, qalqala echo as a render-only phoneme on the
  base unit). Substitutions are `REPLACED` units keeping their source
  graphemes. Silences are `SILENT` units with a reason. This is exactly the
  hard-case list from the char-mapping contract, now representable once.
- **Cross-word sharing is a ShareGroup**, created by the same pass that
  performs the merger — `detect_cross_word_mergers`-style reverse engineering
  from rule tags is deleted.
- **Waqf/ibtidaa are recorded, not recomputed.** Realization runs for the
  requested traversal (as today), but every boundary-state effect lands on the
  model as a unit status/delta. Views stop re-inferring stop transforms.
- **Rules attach to units**, with `is_source`/`is_target` preserved; madd
  subtype is just another rule tag on the madd unit (plus `MaddInfo` for the
  count). The letter-level tag list and `MaddMapping` both retire.

### What tokenization gives us for free

`tokenize(word_text, script) → [Cluster]` is a pure function of the script
data. Because the Unit skeleton (base unit, haraka unit, extension units) is
mechanically derivable from a Cluster, the grapheme↔phoneme scaffolding of
*both* mapping views exists before any rule runs; realization only fills
phonemes, statuses, insertions, and shares. The TS-shard tokenization and
`silent_flags` become `for unit in ...` loops.

## 5. Construction pipeline

Explicit ordered passes replace dispatch-order side effects. Each pass is a
linear scan over the linked word/cluster stream with a bounded window, reads
the riwaya's `RuleData`, and only *adds* to the model (fills units, sets
statuses, tags rules). Later passes may read earlier passes' phonemes — this
matches domain invariant §8 of `domain-facts.md` (assimilation → silencing →
lengthening → classification → colouring is a genuine dependency order, not an
implementation accident).

```
1. tokenize            per word: text → clusters (+ stop sign, marks)
2. link + boundaries   prev/next links; is_starting/is_stopping from stop
                       signs / verse ends / stop_refs (as today)
3. splice specials     locations in the override table get their unit
                       streams built from data (muqattaat) — same model,
                       so the "spelled-out vs written" divergence becomes a
                       projection choice, not a fork
4. boundary transforms ibtidaa: hamza-wasl vowel insertion, initial-shaddah
                       drop; waqf: final-cluster transforms (sukun, iwad,
                       taa-marbuta, hamza+fathatan) — recorded as unit
                       statuses + written_deltas
5. assimilation        noon/tanween table, meem sakinah, consonant idgham
                       pairs, lam shamsiyah — silencing sources, substituting
                       targets, creating ShareGroups (incl. cross-word)
6. letter realization  base consonants, shaddah doubling, vowel letters
                       (lengthen-or-silence), taa marbuta, qalqala echo,
                       hamza-wasl iltiqaa repairs
7. colouring           tafkheem (isti'laa, raa tree, Allah-lam), heavy
                       vowels, ghunnah quality
8. madd classification one scan of the realized units (long-vowel units are
                       already first-class — no phoneme_to_letter rebuild):
                       muttasil/munfasil/lazim/arid/leen/iwad/silah + the
                       override table
9. contextual overrides  per-location table, context-gated (always /
                       starting / stopping)
10. freeze             model becomes read-only; all views project from it
```

Passes 4–9 are where letter-subclass logic goes. The *structural* logic stays
Python (one module per family, operating on units); every set, pair map, word
pattern, phoneme literal, and location list it consults moves to
riwaya-scoped data — satisfying the Epic 3a "no glyph/IPA/location literals in
control flow" gate. A fully declarative rule DSL was considered and rejected
as over-engineering for ~33 rules; the seam that matters for Warsh is
data-driven *parameters* + per-riwaya pass composition (a riwaya can add a
pass, e.g. Warsh imala/naql, or swap one).

## 6. Views as projections

| View | Projection |
|---|---|
| `phonemes_*` | concatenate unit phonemes (simple mode = `phoneme.simple_form`) |
| `character_phoneme_mappings` | units almost verbatim; word-local indices by enumeration |
| `letter_phoneme_mappings` | group units by cluster; fold SILENT units into their sounding neighbour using `silence_reason` + share direction (the PREV/NEXT/CROSS-WORD logic becomes one table) |
| `tajweed_mappings` | rule tags per cluster/extension unit; muqattaat projected spelled-out; synthetic Allah dagger = the inserted unit it already is |
| `silent_flags` | `(grapheme, unit.status is SILENT-at-position, mark)` per written grapheme |
| `phonetic_text` | render `written_delta ?? written form` per cluster |
| alignment / `get_mapping` | enumerate phonemes with back-pointers (unit → cluster → word) |

The three views' *deliberate* tokenization differences (letter view splits
MADDAH; tajweed view spells muqattaat and injects the Allah dagger; shard
tokenization splits only `ٰ ۥ ۦ`) are preserved byte-identically as explicit
per-view projection options over the same units — documented in one place
instead of encoded in four copies of a split-set constant.

## 7. Hard-case ledger (must-represent checklist)

Every case below is representable in the model without special view logic;
this is the acceptance checklist for the design:

| Case | Representation |
|---|---|
| inserted vowel/grapheme (hamza-wasl vowel, iltiqaa kasra, iwad alef, Allah dagger) | INSERTED unit, `source=[]`, tagged |
| substitution (iqlab, nasalized idgham target, taa marbuta *h*, consonant ى at waqf) | REPLACED unit keeping source graphemes |
| silent grapheme (idgham source, hamza wasl, shamsiyah lam, otiose alef) | SILENT unit + `silence_reason` |
| one grapheme → many phonemes (muqatta'a names, started hamza-wasl, tanween) | one unit, many Phonemes (per-phoneme rules via unit split where the domain splits: tanween = its own unit) |
| many graphemes → one phoneme (haraka+carrier long vowel; idgham geminate) | ShareGroup |
| cross-word merger | ShareGroup spanning words, created by pass 5 |
| waqf-variant output (all of domain-facts §7) | unit status + written_delta recorded by pass 4/8 |
| tanween-at-waqf redistribution (long vowel moves to the alef) | the alef's madd unit becomes PRESENT with the phoneme; tanween unit REPLACED — no re-derivation |
| iltiqaa shortening/demotion | SHORTENED unit + share with the consonant that displays it |
| leen (no long-vowel phoneme) | MaddInfo on the consonantal و/ي unit |
| qalqala echo (`Q`) | render-only Phoneme on the base unit |
| sakt | word-level flag from the mark; blocks pass 5 at that boundary |
| silah drop at waqf | extension unit SILENT-when-stopping |
| muqattaat | data-built unit streams (pass 3) |
| per-location overrides incl. imala/tasheel | pass 9 table, context-gated |
| known gap: continuing tanween-alef has no rule (silent-letter audit finding 1) | `silence_reason` takes an orthographic-convention key, so the fact is stored even where no tajweed rule exists |

## 8. Migration path (fits Epic 3a scope)

1. Land the Hafs characterization net first (Epic 2A) — the byte-identical
   gate for everything below.
2. Introduce `Phoneme` + `PhonemeInventory` (feature-carrying, interned);
   replace string-predicate helpers behind the same functions.
3. Introduce `Unit` construction *inside* the current pipeline: build units
   from today's letter state at the point the char view builds cells, then
   port `character_phoneme_mappings` to project from units (its validator is
   the proof harness).
4. Port `silent_flags`, `letter_phoneme_mappings`, `tajweed_mappings`,
   `phonetic_text` to project from units, deleting their private
   re-derivations one at a time (each deletion gated by the net).
5. Invert control: replace `LetterSymbol.phonemize()` dispatch with the
   ordered passes (4–9), moving each letter subclass's logic into its pass and
   its data into the riwaya files. Madd module folds into pass 8.
6. Retire `MaddMapping`, letter-level tag lists, `DiacriticSymbol`/
   `ExtensionSymbol` thinness, and `dev/reconcile_tokenization.py`'s policing
   role (keep it as a regression test).

Step order is chosen so every step is independently shippable and
regression-locked; the riwaya seam (Epic 3b) then threads `Riwaya` through
`Phonemizer`/`Parser`/loader without touching the model again.

## 9. Open questions

- **Expose `.tokenize()` publicly?** Recommendation: keep the model internal
  in 3a; the char view already exposes unit semantics. Decide public exposure
  after Warsh proves the shape (a public canonical model is a compatibility
  contract we shouldn't sign twice).
- **Unit granularity for tanween**: model as one unit (mirrors the written
  single diacritic; the vowel and noon phonemes both live on it) — the char
  view currently decomposes iqlab tanween into haraka + mini-meem cells, which
  becomes a projection split. Confirm during step 3.
- **Traversal caching**: today one `phonemize()` = one traversal (one
  boundary assignment). Keep that; representing all three renditions
  simultaneously (wasl+waqf+ibtidaa per word) is possible in this model
  (status sets keyed by state) but is scope creep — revisit only if a consumer
  needs it.
- **Performance**: LetterSymbol was hand-optimized (slots, flyweights,
  dispatch tables). Units add allocations (~3–5 per cluster). Keep the
  characterization net paired with a perf benchmark; interning Phonemes and
  slotted dataclasses should keep this within budget, but measure before
  committing to per-unit richness everywhere.
