# Warsh Riwaya Abstraction — Plan

## Goal

Generalize the phonemizer so it can support a second riwaya (Warsh, via one
chosen tariq) alongside the current Hafs, with shared logic shared and only the
genuinely-different parts forked. A new riwaya is "the same content with minor
surface differences" — different letters for the same words, different
diacritics, possibly different verse splits and word join/split — plus a smaller
set of genuinely contextual differences: tajweed rules, orthography, and the
Unicode representations used to encode them.

The blocker today is **not** the surface differences (those mostly arrive for
free from the script). The blocker is that the domain knowledge — tajweed
trigger sets, special-word tables, vowel-compatibility lists, IPA literals,
stop/start transforms, and the corpus shape itself — is **hardcoded in Python**,
keyed off Hafs glyphs. A different script silently no-ops those rules. So the
real work is a refactor that makes riwaya context, orthography/phoneme relations,
tajweed rules, and the corpus first-class and data-driven.

## Guiding principles

1. **Hafs output stays byte-identical** through the entire refactor (Epics 3a and
   3b). New behavior only enters in Epic 4 (Warsh data). Every refactor step is
   regression-locked against a characterization net.
2. **Domain knowledge lives in data, not code.** No Arabic glyph literals, no IPA
   literals, no location literals embedded in Python control flow. Everything
   keyed by a riwaya-scoped, pluggable data contract.
3. **One canonical internal model; views project from it.** The three output
   formats must derive from a single source of truth, not re-walk and re-derive.
4. **Tests before the code they protect.** Characterization net first (locks
   Hafs), then refactor; Warsh expected-cases authored from research, red until
   Epic 4.
5. **Prove the seam on a thin slice before generalizing.** Avoid designing an
   abstraction against a single example.

## Epic overview

| Epic | Title | Depends on | Can run parallel with |
|---|---|---|---|
| 0 | Scope & decisions | — | — |
| 1a | Script / Unicode / font research (+ CI validator) | 0 | 1b, 2-Hafs |
| 1b | Tajweed / linguistic research | 0 | 1a, 2-Hafs |
| 2 | Test nets (Hafs characterization + Warsh red cases) | Hafs-net: 0; Warsh cases: 1b | 1a, 1b |
| 3a | Internal-model rework (riwaya-agnostic, byte-identical) | 2 (Hafs net), design ADR | — |
| 3b | Riwaya abstraction seam + corpus/addressing | 3a, Warsh spike | — |
| 4 | Warsh implementation | 1a, 1b, 3b, 2 (Warsh cases) | — |
| 5 | Wrap-up & documentation | 4 | — |

Parallelism: Epic 1a, 1b, and the Hafs characterization net (part of Epic 2) can
start immediately and concurrently. The refactor (3a -> 3b) is strictly
sequential and gated. Epic 4 is the only place new behavior lands.

---

## Epic 0 — Scope & decisions

**Goal:** Pin the scope decisions that gate every downstream epic. These are
choices, not research deliverables; Epic 1 supplies the evidence, Epic 0 records
the call.

**Decisions to record:**
- [ ] Which Warsh tariq (e.g. al-Azraq vs al-Asbahani). Warsh has internal
      variation; pick one line of transmission.
- [ ] Which script source becomes canonical (candidates surveyed in Epic 1a).
- [ ] Which display font is the target (drives the compatibility constraints).
- [ ] Refactor ambition: FULL internal-model rework (retire thin Symbol classes,
      first-class diacritics/mini-vowels/stopping, collapse the three re-walks).
      Confirmed.

---

## Epic 1a — Script / Unicode / font research (+ CI validator)

**Goal:** Choose the Warsh script and prove it is machine-tractable and
display-compatible. Engineering-flavored research; runs parallel to 1b.

**Scope / tasks:**
- [ ] Survey available Warsh scripts and digital sources (Quran.com / King Fahd,
      QUL, Tanzil, and others). Catalogue per source: encoding,
      Unicode codepoints used, diacritic conventions, verse/word segmentation.
- [ ] Assess orthography information content: does the script encode phoneme
      hints in the orthography (preferred), or hide them so they must be inferred
      from domain knowledge? Score each candidate.
- [ ] **Build a Unicode-audit validator (shippable tool)** For a given
      script file: every codepoint is explainable (in an allowlist with a
      meaning), no stray/random characters, report unknown codepoints with
      locations.
- [ ] Digital font compatibility: Survey Warsh
      fonts compatible with the script. Asses if Digital Khatt is compatible with Warsh, or which fonts support Warsh. Assess how well each script matches the chosen
      display font. Document the mapping
      required to go from script -> font agreement.
- [ ] Produce a comparison matrix and a recommendation feeding the Epic 0 script
      and font decisions.

**Acceptance:**
- [ ] `dev/` validator script that fails on unexplained codepoints.
- [ ] Comparison matrix committed under `docs/research/warsh/script-survey.md`.
- [ ] A recommended (script source, font) pair with the required mapping documented.

**Key existing references:** `dev/README.md` (DB/source contract, risk register),
`dev/build_quran_db.py`, `quranic_phonemizer/resources/surah_info.json`,
`dev/unicode_occurences/`.

---

## Epic 1b — Tajweed / linguistic research

**Goal:** Document Warsh tajweed and orthography rules in a form a domain expert
can verify and an AI agent can implement against the existing Hafs code. Research
is written down before any code, and is **diffed against the existing Hafs rules**
since most rules are shared with only contextual differences.

**Scope / tasks:**
- [ ] For each tajweed rule, document the Warsh rule with 1-2 worked examples,
      optionally noting "same as Hafs" or the precise difference. Some examples:
      noon/tanween rules (idgham, ikhfaa, iqlab, izhar), meem sakinah, qalqala,
      lam (shamsiyah/qamariyah, lam of the name of Allah), raa heaviness/lightness,
      ghunnah, tafkheem/tarqeeq, and the madd family.
- [ ] Madd lengths: document Warsh madd measures where they differ from Hafs
      (e.g. madd lazim, munfasil, badal).
- [ ] Imala and other Warsh-characteristic phenomena: document occurrences and
      conditioning.
- [ ] Special / contextual pronunciation cases (per-location overrides) for Warsh.
- [ ] Stopping (waqf) and starting (ibtidaa) rules for Warsh.
- [ ] Unique phonemes in this riwaya not present in the Hafs inventory, and suggested IPA (or otherwise) phoneme symbols.
- [ ] Orthography differences and how they map to pronunciation.
- [ ] Cite sources (books, recordings, videos) per rule so each is independently verifiable.

**Acceptance:**
- [ ] `docs/research/warsh/[documents].md`, structured rule-by-rule, examples, citations, Hafs relationship.
- [ ] List of "new vs Hafs" deltas that becomes the Epic 2 Warsh test backlog and the Epic 4 implementation backlog.

**Key existing references:** `quranic_phonemizer/resources/base_phonemes.yaml`,
`rule_phonemes.yaml`, `muqattaat.yaml`, `contextual_pronunciations.yaml`,
`quranic_phonemizer/tajweed_rule.py` (the 33-rule enum),
`tajweed-mappings.md`, and the Hafs rule code under
`quranic_phonemizer/symbols/letters/`.

---

## Epic 2 — Test nets

**Goal:** Build the safety net before refactoring, and the Warsh target before
implementing. Two distinct nets.

### 2A — Hafs characterization net (start now, parallel)
- [ ] Golden tests at the **stable public boundary** only: `phonemes_str`,
      `letter_phoneme_mappings`, `char_phoneme_mappings`, `tajweed_mappings`,
      `phonetic_text` — for a broad, representative reference set (incl. stops,
      muqattaat, lafdh al-jalalah, hamza wasl, tanween-at-waqf, idgham/ikhfaa/iqlab
      cases).
- [ ] Lock the outputs so Epic 3a/3b can prove **byte-identical** Hafs behavior.
- [ ] Do **not** test internal classes slated for restructure (DiacriticSymbol,
      ExtensionSymbol shapes, etc.) — test behavior, not soon-to-change structure.

### 2B — Warsh expected cases (after 1b; red until Epic 4)
- [ ] Hand-author expected phonemes for 1-2 cases of every tajweed rule and every
      contextual pronunciation, prioritizing the Hafs deltas from 1b (the things
      Hafs does not even test today).
- [ ] First-class tests for the tajweed rules and mappings under Warsh.
- [ ] Keep these red (xfail/skip-marked) until Epic 4 turns them green.

**Acceptance:**
- [ ] Hafs characterization net green and wired into CI as the refactor gate.
- [ ] Warsh expected-case suite committed, red, enumerating the target behavior.

---

## Epic 3a — Internal-model rework (riwaya-agnostic, byte-identical)

**Goal:** Clean the core so the abstraction seam becomes obvious — **without any
new domain knowledge and without changing Hafs output**. Gated by a design ADR;
verified entirely by the Hafs characterization net.

**Design ADR (do first):** decide and record the target patterns before coding —
e.g. domain-adapter vs subclass-per-letter for riwaya-specific behavior; the
canonical internal model shape; how diacritics/mini-vowels/stopping become
first-class; how the three views project from one model.

**Scope / tasks:**
- [ ] **Lift hardcoded domain data into the data contract.** Move the ~26+
      violations out of Python: tajweed trigger sets (`letter.py:22-25`
      `_HEAVY_CHARS` / `_QALQALA_CHARS` / `_IKHFAA_CHARS` / `_IDGHAM_GHUNNAH_CHARS`),
      idgham pair-maps (`letter.py:278-293`), Allah patterns (`lam.py:11-24`),
      hamza-wasl noun/verb patterns (`hamza_wasl.py:10-25`), vowel-compatibility
      lists (`vowel.py`), IPA literals (the emphatic and length markers, `["h"]`,
      `["w"]`, hardcoded short/long vowels in `madd.py`, `silent.py`,
      `letter_phoneme_mapping.py`, `char_phoneme_mapping.py`, `word.py`).
- [ ] **First-class diacritics.** Collapse the thin `DiacriticSymbol` data-holder
      into a clean first-class representation with its own typed rules (keep the
      flyweight/perf win if measured to matter).
- [ ] **First-class mini-vowel graphemes.** Promote `ExtensionSymbol` from a
      metadata bag (whose only effect is `if self.extensions: result += length`)
      into first-class units carrying their own phonemes and rules; stop manually
      appending dagger-alef from `Lam`.
- [ ] **First-class stopping/starting.** Extract waqf/ibtidaa out of the
      `LetterSymbol.phonemize()` template (`letter.py:149-165`) and the ~12 letter
      classes (`vowel.py`, `qalqala_letter.py`, `taa_marbuta.py`, `hamza_wasl.py`,
      `madd.py`, `silent.py`, `phonetic_text.py`) into a single StoppingContext /
      domain pattern computed once and threaded through.
- [ ] **One canonical model; collapse the re-walks.** Store phoneme indices, madd
      types, and rule tags once on the canonical model and have
      `letter_phoneme_mapping`, `char_phoneme_mapping`, and `tajweed_mapping`
      project from it instead of independently re-deriving
      (`char_phoneme_mapping.py` `_letter_pairs` / `_madd_type_indices`, etc.).
- [ ] Retire the now-unnecessary `Symbol` / `Diacritic` cruft and any remap glue
      this exposes.

**Acceptance:**
- [ ] ADR committed under `docs/adr/`.
- [ ] Hafs characterization net **byte-identical**; no behavior change.
- [ ] No Arabic-glyph / IPA / location literals remain in Python control flow
      (validator/grep gate in CI).

---

## Epic 3b — Riwaya abstraction seam + corpus/addressing

**Goal:** Introduce the riwaya axis through the cleaned model, with Hafs still the
only implementation and **still byte-identical**.

**Warsh spike (do first):** prove the seam end-to-end on a handful of Warsh words
plus one rule that genuinely differs from Hafs, to validate the chosen pattern
before generalizing. Throwaway-quality; informs/locks the seam design.

**Scope / tasks:**
- [ ] **Riwaya as a first-class context**, threaded through `Phonemizer`,
      `Parser`, the loader, and `Location` — replacing the module-level singletons.
- [ ] **Parametrize the data files by riwaya.** Make `PhonemeRegistry` and
      `specials.py` riwaya-scoped (sibling data sets or a riwaya key); remove the
      hardcoded single-file paths. Shared rules stay shared; only deltas fork.
- [ ] **Abstract the corpus + addressing** (the most coupled layer):
      - Loader is a module-level singleton keyed positionally off `surah_info.json`
        with `uint16` word indices and a fixed 114-surah / `(surah, ayah, word)`
        assumption (`loader.py`).
      - Support a per-riwaya corpus (its own `Quran.json` -> `quran_db.bin` +
        `surah_info.json`) and per-riwaya verse/word shape, so Warsh's differing
        verse splits and word join/split are representable.
      - Make `Location` riwaya-aware and move the hardcoded location references
        (`madd.py` `LAZIM_OVERRIDE_LOCATIONS` / `NATURAL_MADD_LOCATIONS`, etc.)
        into riwaya-scoped data.
- [ ] Make `TajweedRule` riwaya-tolerant (registry / per-riwaya rule set rather
      than one Hafs-shaped enum), as needed by the data above.
- [ ] Plug Hafs through the new seam as the sole implementation.

**Acceptance:**
- [ ] Hafs runs entirely through the riwaya seam; characterization net still
      byte-identical.
- [ ] Loading a (stub) second corpus with a different verse/word shape does not
      break addressing — proven by a shape-divergence test.
- [ ] Spike documented; seam design locked.

---

## Epic 4 — Warsh implementation

**Goal:** Land Warsh by adding data and the minimal Warsh-specific rule code on
top of the seam. This is the first epic that introduces new behavior.

**Scope / tasks:**
- [ ] Add the Warsh corpus from the Epic 0 script decision, through the Epic 1a validator.
- [ ] Add Warsh data files, phonemes, rules as riwaya-scoped siblings.
- [ ] Implement the genuine Warsh rule deltas from 1b (e.g. imala, differing madd
      measures, any orthography-driven differences) via the adapter/fork pattern
      chosen in the 3a ADR.
- [ ] Turn the Epic 2B Warsh expected-case suite green.

**Acceptance:**
- [ ] All Warsh expected-cases pass; Hafs characterization net still byte-identical.
- [ ] `Phonemizer(riwaya="warsh")` (or equivalent) produces verified output for the
      research-covered cases.

---

## Epic 5 — Wrap-up & documentation

**Goal:** Make the new capability discoverable and maintainable.

**Scope / tasks:**
- [ ] Update `README.md`, the architecture docs, and the
      `.claude/skills/quranic-phonemizer` references for the riwaya axis.
- [ ] Document how to add a future riwaya (the data-contract + adapter recipe).
- [ ] Document the per-riwaya corpus/DB build workflow (extends `dev/README.md`).
- [ ] Final cleanup pass; ensure CI runs both riwayat and the Unicode validator.

**Acceptance:**
- [ ] Docs updated and consistent with code; CI green across both riwayat.

---

## Appendix — verified codebase findings (grounding)

Captured during planning to anchor the refactor scope:

- Hardcoded tajweed trigger sets: `symbols/letters/letter.py:22-25`.
- Idgham pair-maps inside a method: `symbols/letters/letter.py:278-293`.
- Stop/start transforms baked into the phonemize template:
  `symbols/letters/letter.py:149-165`; further stop/start logic across
  `vowel.py`, `qalqala_letter.py`, `taa_marbuta.py`, `hamza_wasl.py`, `madd.py`,
  `silent.py`, `phonetic_text.py`, set in `parser.py` `_annotate_boundaries`.
- Special-word tables hardcoded in Python (not even in YAML): `lam.py:11-24`
  (Allah patterns), `hamza_wasl.py:10-25` (hamza-wasl noun/verb patterns).
- Thin data-holder classes: `DiacriticSymbol` (flyweight, no rules),
  `ExtensionSymbol` (metadata only; single `length` effect at `letter.py:217`).
- Corpus coupling: `loader.py` module-level singleton, positional keying off
  `surah_info.json`, `uint16` word index, 114-surah / `(surah, ayah, word)`
  assumption; hardcoded location refs in `madd.py`.
- Three output views re-walk and re-derive the same data
  (`char_phoneme_mapping.py` `_letter_pairs` / `_madd_type_indices`;
  parallel logic in `letter_phoneme_mapping.py` and `tajweed_mapping.py`).
- ~26+ hardcoded Arabic-glyph / IPA / location literals across `madd.py`,
  `silent.py`, `letter_phoneme_mapping.py`, `char_phoneme_mapping.py`, `word.py`,
  and the letter classes.
- Three divergent tokenizations (tajweed vs letter-phoneme vs TS shard) differ on
  107/114 surahs: `docs/tokenization-reconciliation.md`.
