# ADR-003: Data-file architecture — what each file owns

Status: **proposed** — companion to ADR-001 (the model these files feed) and
ADR-002 (the hygiene they must satisfy). Produced from a full inventory of
every datum the system consumes today (resource files **and** all
Python-hardcoded domain data) plus a target-design review.

---

## 1. Design stance

1. **One owner per fact class.** Script owns *what a codepoint is*; the
   inventory owns *what bytes come out*; rules own *when a detector fires*;
   skeletons/locations own *which words deviate*; the corpus owns *the text*.
   Files reference each other only by **name** (LetterId, ConsonantId,
   RuleId) — never by glyph or token.
2. **Glyphs are values, never keys**, and appear in exactly one file
   (`script.yaml`). ASCII English/transliterated names are the keys and the
   cross-file currency. This is what makes the ADR-002 C1 literal gate
   trivially enforceable over data too: Arabic bytes anywhere else fail CI.
3. **Output tokens live only in the inventory render tables** (ADR-001 §6).
   No phoneme strings in rules, skeletons, locations, or spelled names —
   payloads are typed segment/patch specs.
4. **No deep-merge engine.** DRY comes from file-granular composition via a
   per-riwaya manifest with one trivial merge rule (§5).

## 2. Why: the current state (inventory findings)

The audit confirmed the mess and sized it:

- **`base_phonemes.yaml` conflates three facts per row** — classification
  (this is a consonant), identity (this is *lam*), and render byte (`l`) —
  and enforces classification by YAML *section*, which doesn't even hold
  (shadda lives in `other:` but is special-cased in the parser; mini-noon, a
  rule nasal, sits in `letters:`). Composite values (`FATHATAN: "an"` split
  back by string indexing) and load-bearing emptiness (`ALEF: ""` meaning
  "silent by default") encode behavior as string shape.
- **Dead data**: `cp` on every entry is read by nobody; `phoneme` on
  extensions/stop-signs/other is always `""` and never used;
  `NATURAL_MADD_LOCATIONS` in `madd.py` is declared but never read (the
  location is re-hardcoded inline with a magic letter index);
  `MADD_TYPE_MAP["iwad"]` is a dead key.
- **Two divergent codepoint registries**: `word.py QURANIC_SYMBOLS` and
  `base_phonemes.yaml` name the same codepoints differently
  (`SILENT_ALWAYS` vs `SMALL_HIGH_ROUNDED_ZERO`) and disagree in coverage
  (`END_OF_AYAH` only in word.py). Worse, the corpus contains codepoints in
  *neither* (آ U+0622, CGJ U+034F).
- **Config-by-comment**: `rule_phonemes.yaml`'s alternate tokens live in
  comments; the S1/S2/S3 marks' meanings live in comments while their
  behavior lives in a different file keyed by location.
- **The redundancy ledger**: the long-vowel carrier set exists in ~6 copies
  (with undocumented ± deltas), the isti'laa set exists twice *in two
  alphabets* (glyphs in `letter.py`, IPA in `char_phoneme_mapping.py`), the
  silah/extension split-sets exist six times, geminate detection exists as
  both an algorithm and a 26-token enumeration, and the noon vs tanween
  decision logic is fully duplicated.
- **Latent bugs found**: `EITHER_STOP` is defined but silently excluded from
  `valid_stop_signs`; `letter.py` constructs its waqf sukun with the wrong
  glyph (U+06DF, the round zero); sakt marks are parsed and then ignored
  (no sakt behavior exists).
- **Data the new model needs that exists nowhere**: madd counts per type,
  the izhar throat-letter set (izhar is an else-branch today), the 14 sun
  letters (shamsiyah is a fallback, not a set), LetterId identities for
  skeleton folding, a spelled-name table for muqatta'at, stop-sign
  semantics, simple mode as a render column.

## 3. The file set

```
quranic_phonemizer/resources/
├── shared/                       # riwaya-INVARIANT
│   ├── script.yaml               # codepoint allowlist: NAME → char/kind/letter
│   ├── inventory.yaml            # phoneme inventory + render tables (full+simple)
│   └── spelled_names.yaml        # muqatta'a letter-name segment specs + display
├── hafs/
│   ├── spec.yaml                 # MANIFEST: riwaya stamp + composition list
│   ├── rules/
│   │   ├── noon_tanween.yaml     # the 5-way decision table + izhar-mutlaq + iqlab_ident
│   │   ├── meem.yaml             # meem-sakinah table
│   │   ├── idgham.yaml           # consonant pair maps + sun letters
│   │   ├── qalqala.yaml          # trigger letters
│   │   ├── tafkheem.yaml         # isti'laa set, raa tree params, Allah-lam table
│   │   ├── madd.yaml             # counts per madd rule id
│   │   ├── hamza_wasl.yaml       # ibtidaa vowel-choice table
│   │   ├── vowel_letters.yaml    # carrier → compatible vowel qualities
│   │   └── waqf.yaml             # stop-sign semantics; waqf-transform params
│   ├── skeletons.yaml            # canonical-form overrides (Allah, specials, muqatta'at, particles)
│   ├── locations.yaml            # true per-location residue, typed patches
│   └── corpus/
│       ├── quran_db.bin          # per-riwaya text db
│       └── surah_info.json       # per-riwaya verse/word counts (addressing)
└── warsh/                        # deltas only
    ├── spec.yaml
    ├── script.yaml               # Warsh-only codepoints/marks (adds to shared)
    ├── inventory.yaml            # adds imala "e", taqleel, …
    ├── rules/…                   # only families whose tables differ
    ├── skeletons.yaml · locations.yaml
    └── corpus/…                  # always full — text is never shared
```

Closed vocabularies (`GraphemeKind`, `Boundary`, `OverrideCondition`,
`MaddType`, `LetterId`, patch ops) are **StrEnums in code** per ADR-002 A4 —
not data. Open vocabularies (`RuleId`, `ConsonantId`, `VowelQuality`) are
strings validated at load against the registries.

### 3.1 `shared/script.yaml` — codepoint → kind + letter (the Epic-1a allowlist)

```yaml
schema_version: 1
scope: shared
graphemes:                    # NAME → classification; glyphs appear here ONLY
  ALEF:             {char: "ا", kind: vowel_letter, letter: alef}
  ALEF_MADDAH:      {char: "آ", kind: vowel_letter, letter: alef}   # in corpus, absent today
  HAMZA:            {char: "ء", kind: consonant,    letter: hamza}
  HAMZA_ABOVE_ALEF: {char: "أ", kind: consonant,    letter: hamza}  # …all 7 seats → hamza
  HAMZA_WASL:       {char: "ٱ", kind: hamza_wasl,   letter: hamza_wasl}
  LAM:              {char: "ل", kind: consonant,    letter: lam}
  TAA_MARBUTA:      {char: "ة", kind: consonant,    letter: taa_marbuta}
  FATHA:            {char: "َ",  kind: haraka,  value: a}
  SUKUN:            {char: "ْ",  kind: haraka,  value: sukun}
  FATHATAN:         {char: "ً",  kind: tanween, value: a}    # no "an" composite; noon is the detector's
  SHADDAH:          {char: "ّ",  kind: shaddah}
  DAGGER_ALEF:      {char: "ٰ",  kind: extension, letter: alef}
  MINI_WAW:         {char: "ۥ",  kind: extension, letter: waw}
  ROUND_ZERO:       {char: "۟",  kind: silence_mark}
  RECT_ZERO:        {char: "۠",  kind: silence_mark}
  SAKT_SEEN:        {char: "ۜ",  kind: mark, asserts: sakt}   # mark IS the sakt data source
  IQLAB_MEEM_ABOVE: {char: "ۢ",  kind: mark, asserts: iqlab}
  IMALA_MARK:       {char: "۪",  kind: mark, asserts: imala}  # was "S1" + comment
  PREFERRED_STOP:   {char: "ۗ",  kind: stop_sign}
  END_OF_AYAH:      {char: "۝",  kind: stop_sign}             # unified from word.py
  CGJ:              {char: "͏",  kind: mark}                   # U+034F, in corpus (2:72:4)
skeleton_fold:                # normalization for the skeleton matcher (one function, D2)
  alef_maksura: yaa
```

Decisions: `cp` **deleted** (derivable; the loader prints `U+XXXX` in
errors). Harakat/tanween carry a `value:` vowel quality — kills the `"an"`
composite. Marks carry an optional `asserts:` rule hint so validation can
cross-check the text against the detectors (e.g. sakt behavior is driven by
the mark itself — the four sakt locations need no location table). This one
file absorbs and retires `word.py QURANIC_SYMBOLS` and the S1/S2/S3
name-by-comment entries, and must **cover the corpus completely** (the
Epic-1a validator enforces it).

### 3.2 `shared/inventory.yaml` — the only home of output tokens

```yaml
schema_version: 1
scope: shared
consonants:                   # ConsonantId → render columns (+ nasal variant where it exists)
  ba:    {full: "b",  simple: "b"}
  sad:   {full: "sˤ", simple: "sˤ"}       # phonemic emphatic kept in simple
  noon:  {full: "n",  simple: "n", nasal: {full: "ñ", simple: "n"}}
  meem:  {full: "m",  simple: "m", nasal: {full: "m̃", simple: "m"}}
  waw:   {full: "w",  simple: "w", nasal: {full: "w̃", simple: "w"}}
  yaa:   {full: "j",  simple: "j", nasal: {full: "j̃", simple: "j"}}
placeless_nasal:              # Consonant.ident == None (ikhfaa / iqlab)
  light: {full: "ŋ", simple: "ŋ"}
  heavy: {full: "ŋ", simple: "ŋ"}         # Hafs renders both ŋ; a riwaya may split
vowels:
  a: {full: "a", simple: "a", emphatic_full: "aˤ", emphatic_simple: "a"}
  i: {full: "i", simple: "i", emphatic_full: "iˤ", emphatic_simple: "i"}
  u: {full: "u", simple: "u", emphatic_full: "uˤ", emphatic_simple: "u"}
features:                     # compositional operators over the base token
  long:     {op: suffix, full: ":", simple: ":"}
  emphatic: {op: suffix, full: "ˤ", simple: ""}     # allophonic rˤ/lˤ → r/l in simple
  geminate: {op: repeat, full: double, simple: single}
  qalqala:  {op: emit,   full: "Q",  simple: ""}    # the 1→n expansion: d → (d, Q)
```

This reproduces every payload of `rule_phonemes.yaml` + `simple_phonemes.yaml`
compositionally: `lˤlˤ` = lam + emphatic + geminate; heavy raa = raa +
emphatic; ikhfaa heavy/light = placeless nasal ± emphatic colour; simple-mode
geminate collapse = `repeat: single`. Both files **die**, along with their
config-by-comment alternates (alternates belong to git history or another
riwaya's inventory) and the three scattered copies of the
combining-marks/geminate-strip conventions. Render totality over the feature
lattice is validated at load (§7.3).

### 3.3 `hafs/rules/*.yaml` — one small file per detector family

All letter references are LetterIds. Representative examples:

```yaml
# rules/noon_tanween.yaml — exhaustive, mutually exclusive (domain-facts §8.2)
table:
  izhar_halqi:         {letters: [hamza, ha, ain, hha, ghain, kha], effect: keep}
  idgham_ghunnah:      {letters: [yaa, noon, meem, waw],            effect: merge_nasal}
  idgham_bila_ghunnah: {letters: [lam, raa],                        effect: merge_plain}
  iqlab:               {letters: [ba],                              effect: hidden_meem}
  ikhfaa:              {letters: [ta, tha, jeem, dal, thal, zain, seen, sheen,
                                  sad, dad, tta, dtha, fa, qaf, kaf], effect: nasalize}
izhar_mutlaq: {cross_word_only: [yaa, waw]}     # same-word ي/و does not assimilate
iqlab_ident: meem
```

```yaml
# rules/madd.yaml — counts per rule id (ADR-002 A5: never Python defaults)
counts:
  madd_tabii:          {min: 2, max: 2}
  madd_wajib_muttasil: {min: 4, max: 5}
  madd_jaiz_munfasil:  {min: 2, max: 5}     # 2 = qasr
  madd_lazim:          {min: 6, max: 6}
  madd_arid_lissukun:  {min: 2, max: 6}
  madd_leen:           {min: 2, max: 6}
  madd_silah_sughra:   {min: 2, max: 2}
  madd_silah_kubra:    {min: 2, max: 5}     # follows munfasil
  madd_iwad:           {min: 2, max: 2}
  madd_badal:          {min: 2, max: 2}
```

`rules/idgham.yaml`: mutaqaribayn/mutajanisayn pair maps (naqis marked, →
`complete: false`) + the 14 **sun letters** (today an inference-by-fallback).
`rules/tafkheem.yaml`: isti'laa set, the raa tree parameters (incl. the
kasra-then-isti'laa closed list and khilaf defaults), the Allah-lam colour
table (`heavy_after: [a, u]`, `verse_start_implicit: a`).
`rules/hamza_wasl.yaml`: the ibtidaa vowel table (article→a; third-letter
u→u else i); the special-word *lists* live in skeletons.
`rules/vowel_letters.yaml`: carrier LetterId → compatible vowel *qualities*
(today phoneme-string lists in `vowel.py`).
`rules/waqf.yaml`: stop-sign semantics (which signs are stop-capable —
fixing the silent `EITHER_STOP` exclusion) + waqf-transform parameters.
`rules/qalqala.yaml`: `letters: [qaf, tta, ba, jeem, dal]` — currently
duplicated between `letter.py` and the parser's subclass dispatch table.

### 3.4 `hafs/skeletons.yaml` + `shared/spelled_names.yaml`

Skeleton entries are normalized LetterId tuples (post `skeleton_fold`) +
condition + rule — covering the 12 Allah patterns, the hamza-wasl special
nouns/verbs (prefix match, incl. 7:38/9:38), the يَـٰٓ/هَـٰٓ particles
(munfasil reclass), and the 14 distinct muqatta'at (condition:
`surah_initial` — replacing 29 hardcoded location keys).

The muqatta'at payload is the big win: `shared/spelled_names.yaml` holds one
**typed segment spec per letter name** —

```yaml
names:
  sad:  {display: "صَادْ", segments: [{c: sad}, {v: a, long: true}, {c: dal}]}
  meem: {display: "مِيمْ", segments: [{c: meem}, {v: i, long: true}, {c: meem}]}
  ain:  {display: "عَيْنْ", segments: [{c: ain}, {v: a}, {c: yaa}, {c: noon}]}  # leen
```

— and the **ordinary detectors run over the spliced segments**: madd lazim
vs tabii, ikhfaa/idgham between names, qalqala on صٓ's *d*, tafkheem — all
*derived*, not hand-frozen. This deletes ~90% of today's 592-line
`muqattaat.yaml` (the triple text/phonemes/tajweed representation kept
consistent by hand). Only the name spellings, displays, and the two
narration exceptions (يسٓ 36:1, نٓ 68:1 — location entries) remain as data.

### 3.5 `hafs/locations.yaml` — typed patches, no strings

Patch ops are a closed StrEnum mirroring the effect verbs (`set`, `respell`,
`silence`, `insert_after`, `annotate`); segments addressed by base-letter
ordinal, never phoneme index; display transforms reference LetterIds.

```yaml
entries:
  - {location: "11:41:6", condition: always, rule: imala,
     patch: [{op: set, letter: 2, vowel: {quality: e}},
             {op: set, letter: 3, vowel: {quality: e, long: true}}]}
  - {location: "27:36:8", condition: when_stopping, rule: pronoun_drop,
     patch: [{op: silence, letter: 5}, {op: set, letter: 4, vowel: null}]}
  - {location: "10:79:3", condition: when_starting, rule: ibtidaa_rasm_repair,
     patch: [{op: respell, letter: 1, segments: [{v: i, long: true}], display: yaa}]}
  - {location: "36:1:1", condition: always, rule: izhar_narration,
     patch: [{op: annotate, rule: izhar}]}
```

Absorbs all of `contextual_pronunciations.yaml` (payloads translated from
phoneme strings to typed specs), `madd.py`'s override-location constants
(including the never-read `NATURAL_MADD_LOCATIONS`), and the narration
exceptions. The ٱئۡتُونِى family arguably becomes a skeleton entry later;
migrate as locations first (behavior-preserving), reclassify after.

### 3.6 Corpus — `hafs/corpus/{quran_db.bin, surah_info.json}`

Formats unchanged; **paths riwaya-scoped** (text, rasm, segmentation, and
verse numbering are all per-riwaya). `dev/Quran.json` remains the editable
source per riwaya; `surah_info.json` doubles as the address validator for
`locations.yaml`.

## 4. Format and conventions

- **YAML for every hand-maintained file** — comments are load-bearing for
  domain citations (`# domain-facts §5.5`, `# only نَخۡلُقكُّم`) and are the
  only sanctioned home for Arabic examples outside `script.yaml` values.
  JSON/binary for the machine-generated corpus. No TOML (nests poorly).
- Keys/ids in ASCII per the ADR-002 C9 glossary (one canonical
  transliteration: `ikhfaa`, never `ikhfa`).
- Every file opens with `schema_version:` + `riwaya: <name>` or
  `scope: shared`; the loader cross-checks the stamp against the manifest.
- Safe-load only; duplicate keys and anchors/aliases rejected (silent-merge
  hazards).
- CI lint: Arabic codepoints in any resource file outside `script.yaml`
  values or comments fail (data-side extension of the C1 gate).

## 5. Riwaya layering: shared/ + riwaya dir, composed by a manifest

Rejected: riwaya sections inside files (Warsh edits churn Hafs-reviewed
files); full directory copies (violates DRY — the alphabet defined twice);
recursive deep-merge overlays (the framework ADR-002 warns against, and a
deep-merged decision table can silently go non-exhaustive).

**Chosen:** the loader reads only `spec.yaml`:

```yaml
riwaya: warsh
compose:
  script:        [shared/script.yaml, warsh/script.yaml]
  inventory:     [shared/inventory.yaml, warsh/inventory.yaml]   # adds "e", taqleel
  spelled_names: [shared/spelled_names.yaml]
  rules:         [hafs/rules/, warsh/rules/]    # NO — see merge rule below
  skeletons:     [warsh/skeletons.yaml]
  locations:     [warsh/locations.yaml]
corpus: warsh/corpus/
```

**The one merge rule:** *within a manifest section, files are read in listed
order and a later file replaces or adds whole top-level entries by key;
there is no recursive merge, so overriding any part of an entry means
restating that entire entry.* The ~10-line loop implementing this is the
entire engine, and the merged result is validated as a whole (so a partial
override can't leave a decision table non-exhaustive).

Granularity is deliberate: entries that are jointly constrained (a decision
table) are one key — overriding means restating the whole table, which is
what a reviewing scholar needs to see anyway. Independent entries (one madd
count, one consonant's render row) override singly. **Rules composition
ruling:** whether Warsh's `rules:` composes over Hafs's (`[hafs/rules/,
warsh/rules/]`) or stands alone is decided per Epic-1b findings — default to
**standalone per-family files** (a Warsh scholar reviews a complete
`warsh/rules/noon_tanween.yaml`, not a patch chain), composing only over
`shared/`. If a family proves byte-identical to Hafs, its file is a copy
whose diff is empty — explicit and reviewable.

## 6. Migration map (old → new)

| Old | New | Notes |
|---|---|---|
| `base_phonemes.yaml` `cp` fields | **DELETE** | never read |
| `base_phonemes.yaml` letters `{char}` + section | `shared/script.yaml` `kind` + `letter` | classification-by-section dies |
| `base_phonemes.yaml` letters `phoneme` | `inventory.yaml consonants` | identity/render split |
| `FATHATAN "an"` etc. composites | script `value: a` + detector noon | string-indexing dies |
| `phoneme: ""` on extensions/stop-signs/other | **DELETE** | dead fields |
| `rule_phonemes.yaml` (all) | `inventory.yaml` (nasal columns, placeless_nasal, features.qalqala) + `rules/noon_tanween.yaml iqlab_ident` | rule params and tokens separated; commented alternates deleted |
| `simple_phonemes.yaml` (whole file) | `inventory.yaml` simple columns | string surgery dies |
| `muqattaat.yaml` letter phonemes + tajweed_mapping | `shared/spelled_names.yaml` + detectors | ~90% deleted; display kept |
| `muqattaat.yaml` 29 location keys | `skeletons.yaml` `surah_initial` entries | portable across riwayat |
| `contextual_pronunciations.yaml` | `locations.yaml` typed patches | string payloads → typed specs |
| `surah_info.json`, `quran_db.bin` | `hafs/corpus/` | riwaya-scoped path |
| `letter.py` `_HEAVY/_QALQALA/_IKHFAA/_IDGHAM_GHUNNAH_CHARS`, iqlab ب, bila-ghunnah [ل ر], izhar else-branch | `rules/{tafkheem,qalqala,noon_tanween}.yaml` | izhar throat set becomes explicit data |
| `letter.py classify_idgham_silent_type` pair maps + shamsiyah fallback | `rules/idgham.yaml` incl. `sun_letters` | naqis → `complete: false` |
| `letter.py` waqf transforms (incl. the U+06DF-as-sukun bug) | `rules/waqf.yaml` + waqf pass | bug fixed by construction (script kinds) |
| `lam.py ALLAH_LETTER_PATTERNS` + heavy condition | `skeletons.yaml` + `rules/tafkheem.yaml allah_lam` | three importers → one owner |
| `hamza_wasl.py` patterns + vowel logic + iltiqaa lists | `skeletons.yaml` + `rules/hamza_wasl.yaml` | long-vowel list dies (typed `.long`) |
| `vowel.py` compatibility lists | `rules/vowel_letters.yaml` | qualities, not tokens |
| `raa.py` decision tree constants | `rules/tafkheem.yaml raa` | traversal stays in detector |
| `madd.py` token sets (LONG_VOWELS, SHADDAH_PHONEMES 26-enum, GHUNNAH_PHONEMES, LEEN_CONSONANTS, HAMZA_PHONEME) | **DELETE** | typed segment features replace token scanning |
| `madd.py` LAZIM/NATURAL override locations, `_PARTICLE_LETTERS` | `locations.yaml` / `skeletons.yaml` | never-read constant resolved |
| madd counts (nowhere today) | `rules/madd.yaml` | **new data** |
| `word.py QURANIC_SYMBOLS` + `DIACRITICS` string | `shared/script.yaml` | divergent registry unified |
| `phonemizer.py valid_stop_signs` | `rules/waqf.yaml` | EITHER_STOP inconsistency fixed explicitly |
| projection split-sets (`_SPLIT_EXTENSIONS`, `SILAH_EXTENSION_NAMES`, `MADD_EXTENSION_NAMES`, `SPLITTABLE_EXTENSIONS`, `ISTILAA_CONSONANT_PHONES`, `GLIDE_PHONEMES`, …) | **DELETE** | six near-copies die with the model — projections read `kind`/features |
| `phonemes.py` predicates, `phoneme_registry.py`, `set_phoneme_override` | **DELETE** | ADR-002 A3; render tables replace |
| `phonetic_text.py` glyph transform rows, Arabic-digit maps ×3 | a small written-render section (owner: inventory or a `display.yaml`; decide at implementation) | single copy |
| `text_matcher` normalization (incl. hardcoded آ→ا ×5) | derived from script `letter` + `skeleton_fold` | one normalization source |
| `<rule>` tag-stripping regexes (×8 call sites) | **DELETE** | legacy markup, corpus contains none |

## 7. Load-time validation (ADR-002 C5; every failure names file + key)

1. **Script**: chars unique; kinds/letters valid enums; harakat/tanween all
   carry `value:`; **complete corpus coverage** (every codepoint in
   `quran_db.bin` classified — catches آ/CGJ-class gaps; this is the Epic-1a
   validator wired into load).
2. **Inventory closure**: every consonant LetterId has a ConsonantId
   realization; every haraka `value` ∈ vowels; placeless_nasal present.
3. **Render totality** (B10 at load): every producible feature combination
   renders in both columns — B10 can then never fail per-recitation.
4. **Rules reference-check**: every LetterId in any table exists in script;
   `iqlab_ident` ∈ inventory.
5. **Decision-table contracts on the *merged* result**: noon/meem tables
   pairwise disjoint and jointly exhaustive over consonant/vowel-letter
   LetterIds; pair maps don't collide with shamsiyah.
6. **Madd**: every counts key is a registered RuleId; `min ≤ max`; every
   madd rule a detector can emit has a row (no Python fallback).
7. **Skeletons**: letters are valid *normalized* LetterIds; rules exist;
   every muqatta'a letter has a spelled name; **each skeleton matches ≥ 1
   corpus word** (kills today's silent-pattern-typo failure mode).
8. **Locations**: addresses exist per `surah_info.json`; patch ordinals
   within word bounds; payload ids valid; no duplicate (location,
   condition).
9. **Manifest**: composed files exist; stamps match; merged sections
   validate as wholes.

## 8. Recommendation summary

- Replace the five resource YAMLs with the §3 file set: `script` /
  `inventory` / `rules/*` / `skeletons` / `locations` / `spelled_names` /
  `corpus`, split `shared/` + per-riwaya, glued by a dumb manifest with
  whole-key replacement — no deep merge, no inheritance chains.
- YAML for hand-files (comments carry citations), JSON/binary for corpus;
  glyphs only as `script.yaml` values; ASCII names everywhere else;
  schema-stamped and safe-loaded.
- Delete outright: `cp`, all dead `phoneme: ""` fields, `rule_phonemes.yaml`
  and `simple_phonemes.yaml` (compositional render replaces both), ~90% of
  `muqattaat.yaml` (detectors over spliced spelled names), the six
  projection split-set copies, the token-set constants in `madd.py`, the
  `<rule>` regexes, and `phoneme_registry.py`.
- Add the data that exists nowhere: madd counts, izhar throat letters, sun
  letters, stop-sign semantics, spelled names, skeleton fold, mark
  `asserts` hints.
- Fix by construction the found inconsistencies: the dual codepoint
  registry, EITHER_STOP, the U+06DF sukun glyph, unread
  `NATURAL_MADD_LOCATIONS`, corpus codepoints missing from the allowlist.

Open items: whether the phonetic-text written-render rows live in
`inventory.yaml` or a sibling `display.yaml` (decide when porting that
projection); whether ٱئۡتُونِى graduates from locations to a skeleton entry;
the exact `rules/waqf.yaml` schema once the waqf pass is specced.
