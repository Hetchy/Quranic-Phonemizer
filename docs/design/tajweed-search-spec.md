# Tajweed Search Specification

Status: consumer and domain specification
Scope: search behavior, taxonomy, UX contract, corpus indexing, package boundary, and phonemizer audit requirements
Out of scope: frontend implementation, API implementation, and final corpus classification changes

## 1. Purpose

Tajweed Search finds Qur'an verses that contain a specified Tajweed rule under a specified recitation-boundary plan.

The atomic navigation result is always a verse. A rule occurrence may be anchored to one word, several words, or a specific letter/vowel, but the first search result is a verse containing one or more matching occurrences.

The search must support:

- a simple consumer path for common rule searches;
- progressively more granular, domain-correct refinements;
- boundary-sensitive reclassification;
- stable counts for an entire corpus;
- later drill-down to the exact source and host words;
- reuse by future consumers through an independent search package.

This document separates:

- confirmed consumer requirements;
- provisional domain categories awaiting corpus and phonemizer audits;
- implementation choices that still need benchmarking.

## 2. Core decisions

### 2.1 Search target

Every query has exactly one primary searchable target.

Broad families are grouping and navigation labels only. They are not executable search targets. For example:

- **Idgham** is a grouping label; **Idgham bi-ghunnah** is a target.
- **Madd** is a grouping label; **Madd Munfasil** is a target.
- **Qalqala** is a grouping label; **Qalqala Kubra** is a target.
- **Iltiqa as-Sakinayn** is a grouping label; **Iltiqa Haraka** and **Iltiqa Shortening** are targets.

An exact target may have optional refinements. A target with no meaningful refinements executes directly.

There is no arbitrary OR across unrelated primary targets. A query such as “Ikhfaa or Madd” is not part of the first search model.

### 2.2 Facet semantics

- Facets belonging to different dimensions are combined with AND.
- Multiple values selected within one facet are combined with OR.
- An untouched facet means “any applicable value.”
- Impossible or inapplicable values are not offered.
- Valid values that currently produce zero matches remain visible with a zero count.
- Facet availability is determined by the rule catalog; result counts change with the active boundary plan.
- A facet is only shown when it has meaningful variation for that target.
- A fixed property is shown as a description or badge, not as a pointless selector.

### 2.3 Counts

The system reports two separate counts:

- matching verses;
- matching rule occurrences.

For example: “84 verses · 119 occurrences.”

Occurrences, not letters or sounds, are counted.

- One ordinary rule event counts once.
- A cross-word merger counts once even when it has source and host words.
- A classification-only occurrence counts once.
- Multiple occurrences in one word count multiple times.
- Multiple occurrences in one verse count multiple times.
- Cross-rule overlap is allowed. The same performed material may count under
  multiple exact rules, such as **Madd Tabii** and **Madd Badal** in Hafs.
  Riwayah-scoped classifiers still decide which combinations are valid.
- Counts are scoped to the one target in the current query. Separate searches may return the same verse independently.

### 2.4 Result granularity

The result unit is the verse. The result row should expose:

- verse reference;
- selected target name;
- number of matching occurrences in that verse;
- stable Quran-order position.

The initial row does not need to enumerate causes when a cause facet is unrestricted. Cause-by-cause breakdown is deferred to the detail view.

When the user opens a verse:

- the exact source and host words can be shown;
- a merger can highlight both words while remaining one occurrence;
- a single word can show several occurrences;
- the actual affected letter or vowel can be shown;
- special rules are anchored to their actual affected unit, not merely to the containing word.

## 3. Boundary plans

Boundary behavior is one query-wide setting. It is not a per-rule facet.

Verse ending is always a stop. Every query also begins at the first word of each verse. A selected internal stop creates an ibtidaa state at the following word.

The available plans are alternatives, not an “advanced mode.”

### 3.1 Verse-end-only

Default plan:

- stop at every verse end;
- join at internal word boundaries;
- preserve authored sakt;
- ignore internal stop-sign advice for the purpose of stopping.

This produces the stable baseline counts.

### 3.2 Selected stop-sign categories

The user selects any combination of available stop-sign categories. The selected categories are unioned: a stop is simulated at every sign belonging to any selected category.

For the Hafs Uthmani corpus, the core categories are:

- preferred continue;
- preferred stop;
- optional stop;
- compulsory stop;
- prohibited stop;
- either stop.

Prohibited stops are allowed as an analytical choice. The search does not need a special warning or blocking condition.

The sign class is a candidate stop location; the plan determines whether that location is simulated as a stop.

Script- or riwayah-specific sign classes, such as permitted stop where applicable, belong in the relevant corpus catalog.

### 3.3 Every-word

Every internal word boundary is treated as a candidate stop. Verse ends are also stops.

This plan ignores the selected stop-sign checklist. It exists to investigate effects that are rare under printed stop signs but appear when a reader stops at particular word positions.

### 3.4 Sakt

An authored sakt remains sakt in every plan. It is not silently converted into a full stop.

### 3.5 Dynamic effects

Changing the boundary plan may change:

- whether a cross-word rule occurs;
- the performed haraka or sukun;
- the classification of Raa;
- Madd Munfasil;
- Madd Iwad, Madd Arid li-s-Sukun, and Madd Leen;
- Qalqala degree;
- Hamza Wasl outcome;
- Iltiqa rules;
- other rule-specific performed results.

Pause-created Qalqala and pause-created Raa Tafkheem/Tarqeeq are not separate generic Waqf targets. They remain occurrences of their parent rules, evaluated under the active plan.

## 4. Search sidebar contract

This is a behavior and information-architecture specification, not a frontend implementation.

Recommended conceptual structure:

~~~text
Tajweed Search

Primary rule
  [exact target selector]

Rule refinements
  [target-specific facets, only when meaningful]

Boundary plan
  [Verse ends only]              default
  [Selected stop-sign categories]
  [Every word]

  If selected stop-sign categories:
    [preferred continue] [preferred stop] [optional]
    [compulsory] [prohibited] [either]

Results
  [matching verses] verses · [occurrences] occurrences

Result filters, V1
  Surah: [one or more surahs]
~~~

Behavior:

1. The primary selector presents grouping labels for organization but permits selection only of exact targets.
2. Choosing a target reveals only that target's meaningful facets.
3. Facets use “Any” as the default and may support multi-selection within one dimension.
4. The static scope of a target is shown as “within word,” “across word,” or “either.”
5. A scope selector appears only when the target supports both within-word and across-word cases.
6. The boundary plan is always available and can recalculate counts.
7. The selected stop-sign checklist appears only for the selected-stop-sign plan.
8. Every-word does not expose stop-sign checkboxes.
9. No control is labeled “advanced mode.”
10. Exact targets with no facets execute directly.
11. A singleton target or singleton facet can redirect directly to its one verse while still respecting the active boundary plan.
12. Search labels reuse the phonemizer's existing English Tajweed display names wherever possible. Arabic labels may be added later.
13. New labels are added only where the search taxonomy introduces a genuinely new distinction.
14. V1 includes a categorical Surah filter supporting one Surah or a list of Surahs.

The sidebar should make the current query legible as a sentence-like summary, for example:

“Ikhfaa · Noon Sakinah · across word · follower: ث or ذ · verse ends only.”

## 4.1 V1 result filters

V1 includes a Surah filter after the rule and boundary controls.

- It supports one Surah or multiple Surahs.
- Multiple Surahs are combined with OR within the filter.
- The filter is applied after rule matching and before pagination.
- Surah selection does not change the query's rule semantics or boundary plan.
- The selected Surah set is part of the query cache key and shareable query state.

V1 does not include compound multi-target queries, custom result sorting, or numeric range sliders beyond the categorical Surah filter.

## 5. Search taxonomy

The following sections describe the exact targets and their refinements.

### 5.1 Noon Sakinah and Tanween

Noon Sakinah/Tanween is a grouping label only.

#### Ikhfaa

Optional facets:

- source form: explicit Noon Sakinah or tanween;
- position: within word or across word;
- follower letter: one or more of the fifteen Ikhfaa letters.

There is no separate heavy-Ikhfaa search. Heavy or light performance belongs under the Ikhfaa search and its letter/following context.

#### Iqlab

Optional facets:

- source form: explicit Noon Sakinah or tanween.

- position: within word or across word, with tanween/within-word combinations omitted.

Fixed property:

- follower is baa;
- the target's overall static scope is either, because explicit Noon Sakinah may occur within or across a word while tanween is word-final.

No follower-letter selector is shown.

#### Idgham bi-ghunnah

Optional facets:

- source form: explicit Noon Sakinah or tanween;
- follower letter: meem, noon, waw, or yaa.

Fixed property:

- scope is across word.

Within-word Noon Sakinah before waw or yaa is not this target; it belongs to Izhar Mutlaq.

#### Idgham bila ghunnah

Optional facets:

- source form: explicit Noon Sakinah or tanween;
- follower letter: lam or Raa.

Fixed property:

- scope is across word.

#### Izhar Halqi

Optional facets:

- source form: explicit Noon Sakinah or tanween;
- follower letter: the six throat letters;
- position: within word or across word.

Impossible combinations, especially tanween within a word, are not offered.

#### Izhar Mutlaq

This is an exact target with no additional letter selector.

Fixed properties:

- explicit Noon Sakinah;
- within word;
- the target is the named Izhar Mutlaq rule itself.

### 5.2 Meem Sakinah

Meem Sakinah is a grouping label only.

#### Izhar Shafawi

Optional facet:

- follower letter from the legal set: all applicable letters except baa and meem.

The source is fixed as meem.

#### Ikhfaa Shafawi

Fixed properties:

- source is meem;
- follower is baa;
- scope is across word.

No follower selector is shown.

#### Idgham Shafawi

Fixed properties:

- source is meem;
- follower is meem;
- scope is across word.

It remains boundary-sensitive even though it has no additional facet.

### 5.3 Other Idgham

Idgham remains grouping-only. The exact targets are:

- Idgham Mutamathilayn;
- Idgham Mutaqaribayn;
- Idgham Mutajanisayn Kamil;
- Idgham Mutajanisayn Naqis.

The pair selector exposes only legal directional pairs. It must not offer arbitrary source/follower combinations.

Current implementation-derived legal-pair candidates include:

- Mutaqaribayn: lam → Raa; qaf → kaf;
- Mutajanisayn Kamil: baa → meem, dal → taa, taa → dal, taa → tah, tha → thal, thal → zhaa;
- Mutajanisayn Naqis: tah → taa.

The complete pair table and each pair's static scope require a corpus audit before being treated as final.

### 5.4 Article Lam

Exact targets:

- Lam Shamsiyyah;
- Lam Qamariyyah.

Each target has an optional following-letter facet restricted to its legal sun-letter or moon-letter set.

The rule remains searchable without choosing a letter.

### 5.5 Qalqala

Qalqala is grouping-only. Exact targets are:

- Qalqala Sughra;
- Qalqala Kubra;
- Qalqala Akbar.

Each exact target has an optional letter facet over the five Qalqala letters.

The active boundary plan determines whether a final Qalqala site is Sughra, Kubra, Akbar, or absent. Pause-created degree changes remain under Qalqala, not under a generic Waqf target.

### 5.6 Ghunnah

Exact target:

- Ghunnah Mushaddadah.

Optional facet:

- sounded letter: Noon or Meem.

Merger and classification overlap must not erase this independent target.

### 5.7 Raa and Lam Allah weight

The searchable subjects are:

- Raa;
- Lam Allah.

The user must select the outcome:

- Tafkheem;
- Tarqeeq.

Cause is optional. Therefore:

“Raa → Tafkheem” is valid without choosing a cause, while a cause selection narrows it.

#### Raa → Tafkheem causes

The intended mutually exclusive consumer categories are:

- Raa with fatha;
- Raa with fathatan;
- Raa with damma;
- Raa with dammatan;
- Raa sakin after fatha;
- Raa sakin after damma;
- Raa sakin after a sakin consonant preceded by fatha;
- Raa sakin after a sakin consonant preceded by damma;
- Raa sakin after long alif;
- Raa sakin after long waw;
- Raa sakin after the temporary vowel of Hamza Wasl;
- Raa sakin after kasra followed by a heavy letter in the same word.

#### Raa → Tarqeeq causes

- Raa with kasra;
- Raa with kasratan;
- Raa sakin after kasra;
- Raa sakin after a sakin consonant preceded by kasra;
- Raa sakin after a normal/full long yaa;
- Raa sakin after yaa leen.

The two-sakin descriptions must explicitly say “sakin consonant.” They must not be presented as orthographic silence categories.

Alif maqṣūra is not included in the normal/full long-yaa cause. A current corpus scan found no applicable alif-maqṣūra-before-Raa cases; the domain category still requires later audit.

Tanween causes are based on the performed state under the active boundary plan. If a stop removes a tanween and produces a sakin Raa, the performed search classification becomes the relevant sakin cause. There is no separate “original metadata” search concept.

#### Lam Allah causes

Lam Allah intentionally remains simpler:

Tafkheem:

- after fatha;
- after damma.

Tarqeeq:

- after kasra.

Lam Allah does not inherit the Raa two-sakin cause ladder unless a later domain audit demonstrates a valid consumer-facing distinction.

#### Imaalah interaction

Imaalah is a vowel-level rule, not a Raa target. A vowel may match Imaalah while the affected Raa independently matches Raa Tafkheem or Tarqeeq. Both rule occurrences may count.

### 5.8 Madd

Madd is grouping-only. Exact targets are:

- Madd Tabii;
- Madd Muttasil;
- Madd Munfasil;
- Madd Lazim;
- Madd Arid li-s-Sukun;
- Madd Leen;
- Madd Iwad;
- Madd Badal;
- Madd Silah.

Named Madd rules may overlap with Madd Tabii. A two-count result can count under both the named rule and Madd Tabii when both classifications apply.

For Madd targets, performed vowel quality and written carrier/form are independent refinements wherever meaningful.

#### Madd Tabii

Optional facets:

- performed quality: a, i, or u;
- carrier/form: full carrier, dagger alif, small waw, small yaa, alif maqṣūra, and other applicable written forms.

#### Madd Muttasil

Optional facets:

- performed vowel quality;
- written carrier/form.

The within-word hamza condition is intrinsic to the rule and is not a user-selected detection mechanism.

#### Madd Munfasil

Optional facets:

- performed vowel quality;
- written carrier/form;
- seam type:
  - ordinary word-boundary munfasil;
  - lexical munfasil hidden inside a rasm-joined word.

#### Madd Lazim

Optional subtype:

- Kalimi Muthaqqal;
- Kalimi Mukhaffaf;
- Harfi Muthaqqal;
- Harfi Mukhaffaf.

Selecting Madd Lazim without a subtype matches all four.

#### Madd Arid li-s-Sukun

Optional facets:

- performed vowel quality;
- written carrier/form.

The stop-created sukun is controlled by the boundary plan, not by a separate pause-cause selector.

#### Madd Leen

Optional facet:

- carrier: waw or yaa.

The active boundary plan determines where the stop-created Madd Leen occurs.

#### Madd Iwad

Optional subtype:

- fathatan → pausal alif;
- fathatan on final hamza.

The boundary plan determines whether the pausal form occurs.

#### Madd Badal

Optional carrier/form refinements are allowed. Madd Badal is a separate exact target from Ibdal Hamza, even where their written or performed material overlaps.

#### Madd Silah

Optional facets:

- Silah Sughra or Silah Kubra;
- vowel form: waw or yaa.

The ordinary vowel glyph/form remains available as a normal facet.

### 5.9 Hamza replacement

#### Ibdal Hamza

Optional carrier subtype:

- alif;
- waw;
- yaa.

This target is separate from Madd Badal.

### 5.10 Hamza Wasl

Hamza Wasl is grouping-only. Exact targets are:

- Hamza Wasl Silent;
- Hamza Wasl Fatha;
- Hamza Wasl Kasra;
- Hamza Wasl Damma.

Silent applies when joined. The three vocalized targets apply when started. The boundary plan determines which outcome is performed.

### 5.11 Iltiqa as-Sakinayn

Iltiqa as-Sakinayn is grouping-only. Exact targets are:

- Iltiqa Haraka;
- Iltiqa Shortening.

#### Iltiqa Haraka

The hierarchy is haraka-first:

- resulting Kasra:
  - tanween form: fathatan, dammatan, or kasratan;
- resulting Fatha:
  - the singleton known case of joining 3:1 into 3:2.

The Fatha branch remains visible as a valid choice and redirects directly to its singleton occurrence.

No Damma branch is assumed until a corpus audit confirms one.

#### Iltiqa Shortening

The refinement is the long-vowel carrier shape that is shortened, not the vowel quality that remains:

- tentatively alif;
- tentatively waw;
- tentatively alif maqṣūra.

This carrier inventory is explicitly provisional and must be confirmed from the corpus and phonemizer model.

### 5.12 Special rules

Exact targets:

- Imaalah;
- Tashil;
- Ishmam.

In current Hafs, each occurs once, so these are practically direct verse redirects. They remain first-class exact targets for future riwayah support.

Each occurrence is anchored to its actual affected vowel, hamza, or ending unit.

### 5.13 Orthographic Silence

Exact target:

- Orthographic Silence.

Optional facet:

- silent written-letter kind, such as alif, waw, yaa, or another applicable carrier.

There is no boundary facet because this is an inherent rasm/orthographic property.

Variant silence is not searchable.

### 5.14 Pausal Alif

Exact target:

- Pausal Alif.

Optional selector:

- authored lexical form/site among the seven recognized forms.

The selector is lexical/site-based, not a raw glyph search. Repeated occurrences count separately even when the same lexical form is selected.

### 5.15 Excluded Waqf bookkeeping

These are not searchable targets:

- Waqf Diacritic Drop;
- Waqf Silah Drop;
- Taa Marbuta at Pause.

They may remain internal phonemizer facts or explanatory detail, but they do not appear in the Tajweed search target catalog.

Meaningful effects remain searchable under their parent rules:

- Madd Iwad;
- Madd Arid li-s-Sukun;
- Madd Leen;
- Qalqala degrees;
- Raa Tafkheem/Tarqeeq;
- Pausal Alif.

## 6. Static corpus computation

### 6.1 Principle

The web request must not invoke the full phonemizer over the Qur'an.

The phonemizer is used offline to compile an immutable search corpus. Runtime search performs catalog validation, bitmap/set intersection, verse aggregation, and pagination only.

Do not precompute every possible combination of facets. Precompute atomic occurrence facts and build indexes that support runtime AND/OR filtering.

### 6.2 Boundary scenario compilation

For the current Hafs Uthmani stop-sign vocabulary there are six core sign classes. The selected-sign plan therefore has up to 2^6 = 64 global sign masks, including the empty mask equivalent to verse-end-only.

Add one additional every-word scenario.

The initial static scenario set is therefore:

- 64 selected-stop-sign masks;
- 1 every-word scenario.

Verse-end behavior and authored sakt are included in every scenario.

The exact number becomes 2^N + 1 for a riwayah/script with N sign classes.

The compiler should run the authoritative phonemizer once per scenario, collect all target/facet occurrences, and emit a deterministic artifact. A later optimization may deduplicate boundary-independent facts and store a scenario bitmask, but correctness comes first.

### 6.3 What is precomputed

Precompute:

- verse and word identity;
- boundary identity, word position, and printed stop-sign class;
- performed rule occurrences;
- exact target;
- facet values;
- static within/across scope;
- source and host word IDs;
- affected unit IDs when available;
- classification-only versus sound-changing classification;
- scenario membership;
- occurrence count contribution.

Do not precompute:

- every possible Boolean query;
- every possible combination of facet values;
- UI-specific result layouts;
- transient pagination state.

### 6.4 Static indexes

At minimum, the index needs:

- target → occurrence bitmap;
- target/facet/value → occurrence bitmap;
- scenario → occurrence bitmap or scenario bitmask on each occurrence;
- occurrence → verse;
- occurrence → source/host words;
- verse-order table;
- per-verse occurrence counts for common target-only queries.

A query intersects the target bitmap with each selected facet bitmap, applies the scenario, then:

1. maps surviving occurrences to verses;
2. groups by verse;
3. counts occurrences;
4. orders verses in Quran order;
5. returns the requested page.

### 6.5 Artifact layout

Recommended logical artifact:

~~~text
manifest
  corpus_id
  riwayah
  script
  phonemizer_version
  search_catalog_version
  scenario_count
  checksums

catalog
  grouping labels
  exact targets
  facets
  legal values
  static scopes
  status: confirmed/provisional/audit-required

verses
  verse_id
  surah
  ayah
  Quran-order ordinal

words
  word_id
  verse_id
  word ordinal

boundaries
  boundary_id
  verse_id
  preceding word
  following word
  sign class
  authored sakt flag

occurrences
  occurrence_id
  scenario_id or scenario bitmask
  verse_id
  target_id
  facet values
  source word IDs
  host word IDs
  affected unit IDs
  scope

indexes
  compressed target/facet bitmaps
  occurrence-to-verse map
  verse-order map
~~~

The serving artifact should be immutable and content-addressed by its manifest. A small catalog JSON can be served separately to the web client, while the occurrence index remains server-side.

### 6.6 Storage recommendation

Start with a static read-only artifact plus a search service. Do not introduce a mutable relational database unless operational requirements demand it.

Recommended implementation options to benchmark:

1. compressed bitmap files plus memory-mapped occurrence arrays;
2. read-only SQLite with bitmap or integer indexes;
3. a columnar artifact for build/verification and a compact serving artifact.

For this corpus size, a static artifact is preferable to runtime phonemization and should be simpler to version, deploy, cache, and reproduce.

Known corpus scale from the current Hafs/Uthmani sweep:

- 6,236 verses;
- 77,433 words.

The exact occurrence volume and artifact size must be measured after all scenarios are compiled. A planning envelope for fully materialized scenario rows is several million rows and potentially tens to a few hundred megabytes compressed, depending on whether word-level drill-down data is included. This is an estimate, not a measured requirement.

The benchmark must report:

- raw occurrence rows;
- compressed artifact size;
- resident memory;
- catalog size;
- bitmap size;
- build time;
- query latency by target complexity.

## 7. Runtime service contract

The search package should expose a framework-neutral API, with a web adapter layered on top.

Conceptual operations:

~~~text
load_catalog(corpus, riwayah, script)
validate_query(query, catalog)
execute(query, index)
get_verse_occurrences(verse, query_context)
~~~

Conceptual HTTP endpoints:

~~~text
GET  /tajweed-search/catalog
POST /tajweed-search/query
GET  /tajweed-search/verses/{verse_id}/occurrences
~~~

The query request should include:

- corpus/riwayah/script;
- exact target;
- facet selections;
- boundary plan;
- selected stop-sign categories if applicable;
- page and page size.

The response should include:

- catalog/search version;
- normalized query;
- active boundary plan;
- matching verse count;
- occurrence count;
- paginated verse results;
- optional detail token for drill-down.

The service should reject:

- broad grouping labels as executable targets;
- impossible facet combinations;
- unknown catalog values;
- unsupported riwayah/script combinations.

## 8. Latency and operational targets

These are initial acceptance targets to validate with benchmarks:

- catalog request from cache: under 100 ms server-side;
- warm target-only query: p95 under 50 ms;
- warm multi-facet query: p95 under 100 ms;
- first paginated result including counts: p95 under 150 ms;
- cold index load: under 2 seconds where practical;
- no request-time full-corpus phonemization;
- deterministic response for identical query and artifact version.

If an index is memory-mapped or loaded into process memory, deploy one read-only artifact per corpus/riwayah/script version. Cache the most common baseline and selected-stop scenarios, but do not make correctness depend on cache state.

## 9. Package boundary

Recommended initial package boundary:

~~~text
quranic_search/
  __init__.py
  core/
    models.py
    catalog.py
    query.py
    results.py
  tajweed/
    catalog.py
    facets.py
    scope.py
    rules.py
  build/
    compile_corpus.py
    boundary_scenarios.py
    validate.py
  index/
    build.py
    storage.py
    bitmaps.py
  service/
    protocol.py
    adapter.py
~~~

The core package should not know Tajweed terminology. The Tajweed adapter owns:

- target catalog;
- facets;
- legal pairs;
- scope declarations;
- display-name mapping;
- search-only derived causes.

The build adapter may depend on quranic_phonemizer. The query and index runtime should depend only on the compiled artifact and the generic search core.

Initially, this can ship inside the same Python distribution while remaining a separate top-level package. Publishing it as an independent package later is a pending packaging decision.

The package must have a small public API and should not expose internal bitmap/storage details to future consumers.

## 10. Phonemizer changes and audits

The searcher should not assume that the current phonemizer's rule enum is already the final search taxonomy.

### 10.1 Raa causes

Current implementation behavior can determine heaviness, but it does not necessarily emit all named consumer causes. The search work needs an audit of:

- direct fatha/fathatan/damma/dammatan/kasra/kasratan;
- Raa sakin after fatha, damma, or kasra;
- two-sakin paths with the preceding fatha/damma/kasra;
- long alif and long waw;
- normal/full long yaa;
- yaa leen;
- temporary Hamza Wasl;
- kasra followed by an in-word heavy letter;
- verse-start and other edge paths.

The final cause partition must be mutually exclusive within each outcome, with examples and counts proving coverage.

The current implementation's look-back logic should be audited because a generic “first heard vowel” result is not enough to expose the two-sakin cause labels.

### 10.2 Boundary scope

Every exact target and, where necessary, every legal pair needs a static scope classification:

- within word;
- across word;
- either.

The scope should be derived once from domain facts and stored in the catalog. Active stop plans determine whether a performed occurrence exists; they do not change the scope label.

### 10.3 Occurrence model

Audit that every rule occurrence exposes enough provenance for:

- verse aggregation;
- source and host word drill-down;
- exact affected unit;
- one occurrence per rule event;
- multiple events in one word;
- cross-rule overlap;
- classification-only rules.

If the current occurrence model already has word, boundary, and sound IDs, the search adapter should use those rather than inventing parallel location semantics.

### 10.4 Facet provenance

Confirm or add structured values for:

- Noon versus tanween;
- within-word versus across-word;
- legal follower/pair;
- Raa cause;
- Lam Allah cause;
- Qalqala degree and letter;
- Madd quality and carrier/form;
- Madd Lazim subtype;
- Madd Munfasil seam;
- Madd Silah type and vowel form;
- Madd Iwad subtype;
- Ibdal Hamza carrier;
- Iltiqa Haraka result and tanween form;
- Iltiqa Shortening carrier shape;
- Hamza Wasl outcome;
- orthographic silence letter kind;
- Pausal Alif lexical/site identity.

### 10.5 Special-rule anchors

Verify that Imaalah, Tashil, and Ishmam occurrences are anchored to the affected unit, not only to the containing word.

Imaalah must remain independent from Raa weight classification.

### 10.6 Script and riwayah audit

Hafs/Uthmani should be the first indexed corpus.

Other scripts and riwayat require their own:

- stop-sign catalog;
- orthographic carrier mapping;
- special-rule inventory;
- display-name mapping;
- scenario count;
- corpus audit.

The current project has a known IndoPak corpus/inventory issue involving unsupported written forms. That must be fixed or explicitly excluded before an IndoPak index is published.

### 10.7 Documentation audit

Existing research documentation contains useful domain material but may describe implementation-era categories that are not the final consumer taxonomy. In particular, the Raa documentation should be updated after the cause audit so that:

- the two-sakin causes are explicit;
- “sakin consonant” is used instead of ambiguous “silent consonant”;
- alif maqṣūra is not presented as the normal long-yaa-before-Raa cause;
- Waqf is not presented as the cause of Raa weight;
- special vowel rules are not confused with Raa classification.

## 11. Corpus audit and build validation plan

Before publishing the first static artifact:

1. Compile every boundary scenario.
2. Record counts by exact target, facet, scope, and scenario.
3. Verify that verse-end-only matches the baseline expected counts.
4. Verify that each stop-sign category changes only the rules it should affect.
5. Verify every-word behavior independently.
6. Verify authored sakt remains sakt.
7. Verify prohibited stops are accepted.
8. Verify all illegal facet combinations are absent.
9. Verify all legal values have deterministic counts, including zero.
10. Verify cross-word mergers count once.
11. Verify multiple occurrences in one word count multiple times.
12. Verify cross-rule overlap.
13. Verify the three singleton special rules.
14. Verify Raa cause mutual exclusivity and coverage.
15. Verify the provisional Iltiqa Shortening carrier inventory.
16. Verify every legal Idgham direction and scope.
17. Verify source/host/affected-unit drill-down references.
18. Verify index output is deterministic and checksummed.

Known current corpus facts useful for the first audit:

- 6,236 verses and 77,433 words in the Hafs/Uthmani sweep;
- stop-sign classes are unevenly distributed, so zero and low-count facets are expected;
- Imaalah, Tashil, and Ishmam each occur once in current Hafs;
- the current scan found no applicable normal long-yaa/alif-maqṣūra-before-Raa case.

## 12. Post-V1 advanced search ideas

These ideas are intentionally outside the first release. They should be designed against the same normalized query and static index rather than added as ad-hoc frontend-only filters.

### 12.1 Compound AND queries

Allow a query to contain multiple independent exact-target clauses joined by AND.

Example:

~~~text
Verses containing:
  Madd Munfasil
AND
  Qalqala Kubra
AND
  Raa → Tafkheem, cause: Raa sakin after damma
~~~

Rules:

- each clause has its own exact target and optional facets;
- the result verse must contain at least one occurrence satisfying every clause;
- one global boundary plan applies to all clauses in the compound query;
- each clause retains its own occurrence count in the result detail;
- no OR, NOT, or arbitrary Boolean nesting is included in the first compound-query version;
- the result summary should expose the number of matching verses and a per-clause occurrence breakdown.

The implementation can intersect each clause's verse bitmap. It must not run the phonemizer at request time.

For compound queries, the aggregate occurrence count and the default sorting metric require a final product decision. The safest initial presentation is per-clause counts, with no misleading single total.

### 12.2 Bidirectional result sorting

V1 keeps Quran order ascending as the default. A later version may offer ascending and descending sorting by:

1. Quran order;
2. number of matching instances in the verse;
3. verse length in words.

Sorting requirements:

- every sort direction is explicit: ascending or descending;
- ties use Quran order ascending as the deterministic secondary key;
- sorting is applied after the base query, boundary plan, and Surah filter;
- pagination is performed after sorting;
- the selected sort and direction are part of the query state and cache key.

For a single-target query, “number of matching instances” means the occurrence count for that target after all facets and the active boundary plan are applied. For compound queries, whether this means total occurrences across clauses or a selected clause remains pending; per-clause sorting is the safer first implementation.

### 12.3 Numeric result filters

Later versions may add numeric filters after the base rule query and Surah filter.

#### Instances per verse

Add a dual-ended range control for the number of matching occurrences in a verse.

- The range is inclusive.
- A single-number selector is represented by minimum equal to maximum.
- The initial minimum and maximum are derived from the current query result set.
- The range is recalculated when the base rule query, boundary plan, or Surah filter changes.
- If the result set has one possible value, the control is displayed as a single value rather than a misleading range.
- An empty result set has no numeric range to display.

#### More than one instance in a word

Add a rule-specific filter for cases where the selected target or facet occurs more than once in the same word.

The initial useful form is a single threshold such as “at least 2 occurrences in one word.” It can later become a minimum/maximum per-word range if corpus use demonstrates a need.

This filter is offered only when the selected target/facets can produce a single-word occurrence anchor. It is hidden for targets that are inherently cross-word-only and for query shapes whose occurrence footprint cannot be assigned to one word.

For rules supporting both within-word and across-word occurrences, the exact behavior of this filter requires one further decision: whether it considers only within-word occurrences or allows a compound word-level metric after a scope restriction. The safer default is to expose it only after the query is restricted to a single-word scope.

#### Verse length

Add a dual-ended range control for verse length in words.

- The range is inclusive.
- A single-number selector is minimum equal to maximum.
- Bounds are derived from the current query result set.
- Verse length is a static corpus fact and does not change with the boundary plan.
- The filter is applied before sorting and pagination.

### 12.4 Very advanced boundary comparison

Later research-oriented search may compare two boundary plans directly.

- **Boundary delta:** find occurrences created, removed, or reclassified between plan A and plan B, such as Raa Tafkheem → Tarqeeq or Qalqala Sughra → Kubra.
- **Boundary stability:** find occurrences whose rule and classification remain unchanged under all available plans, or only under a selected set of plans.

These are comparisons between performed states, not new Tajweed rule targets.

### 12.5 Very advanced cross-rule location relationships

Compound AND clauses may later be narrowed by where their matching occurrences relate to one another:

- same affected unit, using a shared phoneme or source character anchor;
- same word;
- same ordered pair of words, especially for cross-word rules.

These refinements operate across exact rule targets. They are substantially later than ordinary verse-level AND because they require compatible occurrence anchors and explicit relationship semantics.

### 12.6 Distribution and density exploration

Allow a selected exact rule or facet to be explored by:

- occurrence and matching-verse distribution by Surah;
- normalized density within each Surah, preferably occurrences per 1,000 words;
- comparison with the same rule or facet's global corpus density, such as “1.8× the Quran-wide density”;
- optional aggregation by Makki versus Madani classification.

Raw counts must remain visible beside normalized density so a small Surah is not made to look disproportionately important. Makki/Madani classification must come from an explicit, versioned metadata source.

### 12.7 Additional precomputed metrics

To support these filters without runtime corpus work, the index should include or cheaply derive:

- Surah ID for every verse;
- verse word count;
- target occurrence count per verse and scenario;
- target/facet occurrence count per verse and scenario;
- maximum matching occurrence count in any one word;
- per-word occurrence counts for targets whose scope permits this metric;
- per-clause verse bitmaps for compound queries;
- performed rule/classification state by boundary scenario for delta and stability queries;
- source-character, phoneme, word, and ordered word-pair anchors for cross-rule relationships;
- per-Surah word totals, verse totals, target/facet counts, and global density baselines;
- versioned Makki/Madani metadata where that exploration is enabled.

The static artifact should expose these as immutable numeric columns or compact side indexes. The server should calculate slider bounds from the already-filtered result set, not scan the original Quran text.

## 13. Pending decisions and status policy

The final implementation plan should carry a status for every target and facet:

- Confirmed: agreed consumer/domain requirement;
- Provisional: intended category, pending corpus or phonemizer confirmation;
- Audit required: cannot be finalized without examples/counts;
- Implementation choice: backend decision pending benchmark.

Current pending items:

1. Confirm the exact Iltiqa Shortening carrier inventory.
2. Complete the mutually exclusive Raa cause audit, including edge cases.
3. Complete the legal-pair and scope audit for all articulatory Idgham rules.
4. Decide whether structured cause classifications belong in the phonemizer, the search adapter, or both on a case-by-case basis.
5. Benchmark static artifact formats and choose bitmap versus read-only SQLite serving.
6. Choose the final package name and whether it remains in the current distribution or becomes separately publishable.
7. Confirm the first supported corpus matrix: Hafs/Uthmani only, or additional script/riwayah artifacts.
8. Finalize the web API's pagination, caching, and deployment details after latency measurements.
9. Define the aggregate occurrence count and default sorting metric for compound AND queries.
10. Confirm whether the per-word multiplicity filter requires an explicit single-word scope restriction for every target that supports both scopes.
11. Select and version the Makki/Madani metadata source before exposing that distribution grouping.

## 14. Definition of done for the search feature

The feature is ready for implementation when:

- the exact target catalog is versioned;
- every target has a documented facet set and static scope;
- boundary scenarios are deterministic;
- all excluded mechanical Waqf rules are absent from the search catalog;
- all agreed overlap and count semantics pass tests;
- the first corpus artifact is generated and checksummed;
- query latency meets the agreed benchmark;
- the web service can serve catalog and verse results without invoking the phonemizer;
- verse drill-down can locate source, host, and affected units;
- provisional categories are visibly marked in internal documentation and are not silently treated as finalized domain truth.
