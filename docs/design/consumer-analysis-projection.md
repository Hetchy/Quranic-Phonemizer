# Consumer analysis projection

Status: accepted implementation direction, with the small open decisions in
section 21 still to be closed by fixtures.

Target baseline: riwayah-agnostic-refactor at 789a459.

This document is the implementation plan for replacing the current public
graph and its alignment, respelling, and derived-label projections. It also
defines the domain contract needed by the website, QUA v11 compatibility
adapter, Inspector, and continuous-text highlighting.

The current projections are not a correctness oracle. They contain known
modelling and assembly errors. A frozen build of them is useful only as
untrusted differential evidence: every match and every difference still has
to be judged against native laws and reviewed fixtures.

## 1. Decision

Keep the Score, Inscription, and Performance separation inside the engine,
correcting it where the audit found ambiguous or inaccurate facts. Replace
the serialized six-node, three-edge graph with a native AnalysisResult built
directly from the resolved Session.

The new public result has:

- the exact source text and ordered phonemes;
- words and resolved boundaries;
- ordered sounds;
- applied tajweed rules and their actual targets;
- genuine cross-word mergers;
- an exact source-character and letter-unit view;
- an optional continuous-text highlight grouping;
- an optional educational cell view in source or transformed presentation.

There is no general recited or performed text, no public graph, no public edit
language, and no generic source-to-performed correspondence model.
Transformed spelling exists only inside the educational cell view.

The old projections are removed after cutover. Compatibility is provided by a
thin QUA v11 adapter over the native result, not by retaining two live public
architectures.

## 2. Standing principles

1. Start from consumer questions. A consumer should ask directly for text,
   phonemes, rules on letters, rules on sounds, silent letters, mergers,
   boundaries, cells, or highlighting.
2. Keep domain knowledge in the phonemizer. Consumers must not inspect Unicode
   codepoints, infer tajweed from rule IDs, rebuild letter groups, fold silent
   letters, or discover cross-word effects.
3. Keep ownership honest. A silent letter owns no sound. A useful highlighting
   relationship is published separately rather than disguised as ownership.
4. Expose actual output, not a menu of hypothetical output. A boundary reports
   its resolved state; it does not publish allowed-states machinery.
5. Use ordinary tajweed terminology. Avoid graph, canonical-part, render-glyph,
   reachability, and phonemization-pipeline jargon in the consumer contract.
6. Fold semantically identical rules in the internal model before projection.
   Do not make every consumer repeat a presentation fold.
7. Keep independent choices independent. Variants and extra phonemes have
   separate catalogues, request fields, result fields, and website sections.
8. Keep views selective. Reading phonemes or rules does not build cells.
   Continuous-text highlighting does not build transformed cells.
9. Prefer one obvious owner. The phonemizer owns semantics; an SDK adapter owns
   legacy wire translation; a frontend owns layout, colour, interaction, and
   typography.
10. KISS and YAGNI apply to both data and code. Add a field only when a named
    consumer use case and a fixture require it.
11. Delete misleading abstractions instead of adding a corrective facade over
    them.
12. A legacy match is not proof of correctness. A native law or audited fixture
    is required for every semantic decision.

## 3. Consumer questions the API must answer

The contract is complete when it answers these without reconstruction:

- What exact Qur'anic text was selected?
- What phonemes are performed, globally or by word?
- Which written unit owns or presents each sound?
- Which written units are silent, and why?
- Which rule applies to a visible unit?
- Which rule applies to a sound?
- Which units from adjacent words share one merged sound?
- What happened at each boundary?
- How should the word, letter, and phoneme cells be aligned?
- Which source units should highlight together for a timed sound or set of
  sounds?
- Which khilaf choices and optional phoneme distinctions can be selected?

It is explicitly not a goal to expose:

- internal Score slots, unit parts, graph edges, or rule trigger context;
- a generic graph traversal API;
- a general transformed-text string;
- a generic text diff or correspondence language;
- UI colours, CSS lanes, tooltip placement, or component state;
- all possible boundary states on every returned boundary;
- teaching families or a second hierarchy over tajweed rules;
- audio, playback, timestamps, or reciter data.

## 4. Public Python API

The ordinary entry point remains familiar:

~~~python
from quranic_phonemizer import Phonemizer

pm = Phonemizer()
result = pm.phonemize("1:1")
~~~

The result exposes a small eager core and selective views:

~~~python
result.text()                         # exact source text only
result.phonemes()                     # tokens in performed order
result.phonemes("word")               # tokens grouped by word allocation

result.words
result.boundaries
result.sounds
result.rule_occurrences
result.mergers

result.source                         # characters, letter units, placements
result.highlight_groups()             # continuous source-text highlighting
result.cells(
    presentation="transformed",       # or "source"
    words=None,
)
~~~

Riwayah metadata remains separate:

~~~python
tajweed_rules("hafs")
available_variants("hafs")
available_extra_phonemes("hafs", alphabet="ipa")
~~~

The request and result retain separate variant and extra-phoneme values:

~~~python
pm = Phonemizer(
    variants={"iqlab_nasal": "bilabial"},
    extra_phonemes=("emphatic_fatha",),
)
result = pm.phonemize("1:1")

result.variant
result.extra_phonemes
~~~

There is no available_options function and no common option union with a kind
field.

## 5. Result identity and IDs

AnalysisResult identifies the exact computation:

| Field | Meaning |
| --- | --- |
| ref | Resolved Qur'an reference |
| riwayah | Selected transmission |
| script | Selected source script |
| alphabet | Selected phoneme alphabet |
| variant | Resolved khilaf choices |
| extra_phonemes | Resolved optional distinctions |
| schema_version | Version of this native DTO contract |
| canon_digest | Digest of the canonical source passage |

IDs are result-local, opaque, typed identifiers. Array position is not public
identity. Every published reference is validated in both directions where a
back-reference exists.

Core IDs remain stable across selective views of the same result. Asking for
cells does not mint a second sound or rule identity space.

## 6. Core DTOs

### 6.1 Word

| Field | Meaning |
| --- | --- |
| id | Result-local word ID |
| ref | Canonical word reference |
| text | Exact source word text |
| before_boundary_id | Boundary immediately before this word |
| after_boundary_id | Boundary immediately after this word |
| sound_ids | Sounds allocated to this word in performed order |

A word's text is source text. It is never a transformed reconstruction.
Cross-word sharing is reported by Merger rather than hidden inside word
allocation.

### 6.2 Boundary

There are N + 1 boundaries for N words:

| Field | Meaning |
| --- | --- |
| id | Result-local boundary ID |
| before | Word before the boundary, if any |
| after | Word after the boundary, if any |
| state | start, join, sakt, or stop |
| stop_sign | Exact written stop or sakt sign at this boundary, if any |

The four states mean:

- start: the leading request boundary;
- join: an ordinary internal continuation;
- sakt: an authored breathless pause that blocks cross-boundary interaction
  without applying waqf or ibtidaa;
- stop: waqf before the boundary and, if another word follows, ibtidaa on that
  following word.

The trailing request boundary is stop. An internal stop therefore already
means both stop before and start after; no second boolean is needed.

There is no edge state, left-word/right-word terminology, advice field, or
allowed_states field. At an ordinary internal boundary, no stop override
resolves to join and a stop override resolves to stop. At an authored sakt
place, no override resolves to sakt and a stop override resolves to stop.
Callers never request sakt as a generic choice, and an authored sakt never
resolves to a false ordinary join.

The website displays stop_sign when present and a visual | | fallback when it
is absent. SourceView carries any exact sign characters through boundary_id.
The fallback is presentation, not source text.

### 6.3 Sound

| Field | Meaning |
| --- | --- |
| id | Result-local sound ID |
| order | Total performed order |
| token | Token in the selected alphabet |
| word_id | Primary word allocation |
| rule_occurrence_ids | Rules that classify or change this sound |

Features needed by a supported alphabet may be added as typed fields only
when the renderer or a named consumer requires them. Do not expose the entire
internal sound object as an untyped features dictionary.

### 6.4 Rule definition

tajweed_rules returns one RuleDefinition per native rule:

| Field | Meaning |
| --- | --- |
| id | Stable rule identifier |
| name | Concise ordinary English/transliterated name |
| arabic_name | Arabic name |
| summary | One short, neutral explanation suitable for hover |

The phonemizer owns these semantic names and summaries. Consumers own colour,
underline styling, order, and whether a particular UI hides or visually
groups rules. There are no family labels and no projection-level folding.

If two items are one rule semantically, they are folded in the internal rule
inventory. A consumer must never inspect letters and reclassify a generic
internal occurrence just to obtain the native public rule.

### 6.5 Rule occurrence

| Field | Meaning |
| --- | --- |
| id | Result-local occurrence ID |
| rule_id | Native RuleDefinition ID |
| word_ids | Words actually affected |
| boundary_ids | Boundaries whose resolved behavior is part of the effect |
| sound_ids | Sounds actually classified or changed |

SourceView adds visible-unit placements for the same occurrence ID. CellView
adds column and sound-cell placements. Trigger-only context remains private.

An occurrence never publishes a second participant merely because that
letter caused the classifier to fire. It publishes a participant only when
the rule classifies, changes, silences, inserts, replaces, or merges it.

### 6.6 Merger

Merger is reserved for a genuine shared sound across adjacent words:

| Field | Meaning |
| --- | --- |
| id | Result-local merger ID |
| boundary_id | Crossed boundary |
| before_word_id | Contributing word before the boundary |
| after_word_id | Hosting word after the boundary |
| sound_id | One shared sound |
| rule_occurrence_ids | Assimilation rule occurrences |

This is the compact answer to “which phoneme is shared between these two
words?” SourceView adds MergerPlacement with merger_id, before_unit_ids, and
after_unit_ids for the exact written characters. Keeping that placement in the
source view means phonemes-only callers do not pay for source tokenization.
Neither record is a generic edge.

Iltiqa kasra and iltiqa fatha are not mergers: they insert a vowel at a
boundary but do not make two letters share a sound. Their RuleOccurrence names
the boundary, and transformed cells place their inserted group at that
boundary. The frontend does not need to special-case their rule IDs.

## 7. Exact source view

SourceView is the only general character surface. It preserves the selected
script exactly.

### 7.1 Character

Character is one Unicode scalar:

| Field | Meaning |
| --- | --- |
| id | Result-local character ID |
| index | Scalar order in result.text() |
| text | Exact scalar |
| role | lexical, separator, or stop_sign |
| word_id | Owning word, when lexical |
| boundary_id | Owning boundary, when a stop sign or structural separator |
| letter_unit_id | Owning LetterUnit, when lexical |

Concatenating characters in order reproduces result.text() exactly.
A Character is exactly one of:

- lexical, with word_id and letter_unit_id;
- separator, with boundary_id;
- stop_sign, with boundary_id.

This makes an orphan character a validation error rather than an undocumented
“structural” exception.

### 7.2 Letter unit

LetterUnit is the semantic and educational unit over source characters:

| Field | Meaning |
| --- | --- |
| id | Result-local unit ID |
| word_id | Owning word |
| character_ids | Exact source characters in this unit |
| ranges | Ordered half-open Unicode-scalar ranges in result.text() |
| text | Their exact concatenation |
| role | Plain consumer-facing role |
| written_on_unit_id | Carrier/seat unit this mark is written on, when any |
| owned_sound_ids | Sounds this unit genuinely produces |
| presented_sound_ids | Additional non-owned sounds visibly shared here |
| rule_occurrence_ids | Rules placed on this visible unit |
| silence | Typed silence reason, or null |

The initial role vocabulary is limited to what rendering needs: letter,
haraka, sukun, tanween, small_vowel, small_hamza, mini_noon, madd_sign, and
other_mark. It is not a mirror of internal SlotFact names.

The tokenization is normative:

- a base letter is a unit;
- dagger alif and every other sounded small vowel are their own units;
- a small or combining hamza is its own unit, including carrier-seat cases;
- small waw and small yaa are their own units;
- mini noon is its own unit;
- haraka is its own unit;
- sukun is its own unit; it owns no sound but is not a “silent letter” and has
  no SilenceReason merely because it denotes the absence of a vowel;
- tanween is its own unit;
- shadda stays a Character but is included in the main letter unit;
- a Quranic silence mark stays a Character but is included in the main letter
  unit it marks;
- stop signs are boundary characters, not word letter units.

Character, LetterUnit, and shaping clusters are not required to coincide.
This is intentional. A main unit can have multiple ranges when an independently
tokenized haraka occurs between its base and shadda. written_on_unit_id states
orthographic carrier/seat attachment; it is not educational CellGroup
membership. The source string remains continuous and font-shaped as one string,
while producer-supplied scalar ranges state exact semantics.

### 7.3 Ownership, presentation, and silence

owned_sound_ids is causal ownership. presented_sound_ids is additional,
non-owning visible sharing. The two arrays are disjoint:

- an ordinary pronounced unit owns its sound and has no need to repeat it as
  presented;
- a merger contributor does not own the host's sound but may present the
  shared sound;
- a genuinely silent letter owns and presents no sound and has a silence
  reason;
- a shadda or silence mark can be soundless notation inside another unit
  without itself becoming a silent-letter unit;
- a sukun is its own soundless notation unit without a SilenceReason.

Each source sound has at most one owning unit. No unit repeats one sound ID in
both arrays.

This prevents two opposite errors: treating every absent sound as accidental,
and assigning a sound to a silent glyph merely to make highlighting easy.

### 7.4 Source rule placements

SourceView publishes RulePlacement records:

| Field | Meaning |
| --- | --- |
| rule_occurrence_id | Existing occurrence |
| unit_ids | Exact visible source units to underline or hover |

SourceView also publishes MergerPlacement:

| Field | Meaning |
| --- | --- |
| merger_id | Existing core merger |
| before_unit_ids | Exact contributing source units before the boundary |
| after_unit_ids | Exact hosting/presenting source units after the boundary |

An occurrence can legitimately have:

- sound targets and visible-unit targets;
- only sound targets;
- only visible-unit targets;
- a boundary target with no invented source letter.

Empty sets are explicit and tested. Consumers do not infer placements by
searching neighboring codepoints.

## 8. Continuous-text highlighting

Cell ownership is not enough for teleprompters. result.highlight_groups()
publishes the domain-selected co-highlighting relation without pretending it
is sound ownership:

| Field | Meaning |
| --- | --- |
| id | Result-local highlight group ID |
| unit_ids | Source units highlighted together |
| ranges | Ordered, non-overlapping half-open scalar ranges in result.text() |
| sound_ids | Sounds that activate this group |

The projection preserves exact source text and QPC shaping. The consumer maps
timed sound IDs to these groups; timestamps remain outside the phonemizer.

The phonemizer, not the consumer, decides silent folding and co-highlighting:

- silent leading units may fold forward where the reading requires it;
- silent trailing units may fold backward where the reading requires it;
- a merger may co-highlight contributor and host units;
- inserted sounds highlight their domain-selected source anchor;
- structural stop-sign characters are not folded into lexical highlighting.

These are audited per transformation family. They are not implemented as a
single adjacency guess. A consumer that wants to skip all silent participation
may ignore the optional highlight view and use honest unit ownership instead.

In the full view, every sound occurs in exactly one HighlightGroup. A merger's
shared sound therefore activates one group containing every source range that
must co-highlight on both sides of the boundary. Ranges are producer-derived;
the consumer never coalesces Character IDs or guesses a silent fold.

## 9. Educational cell view

CellView is a producer-built layout contract, not a second text surface. It
contains whole-word containers, letter columns, aligned sound cells, boundary
insertions, and merger bridges.

The two presentations are:

- source: source letter units only, with performed sounds anchored to them;
- transformed: the educational cell spelling after insertions, replacements,
  omissions, and boundary effects.

There is no promise that concatenating transformed columns produces a
general-purpose text string.

### 9.1 Shape

~~~text
CellView
  words: CellWord[]
  boundaries: CellBoundary[]

CellWord
  word_id
  groups: CellGroup[]

CellBoundary
  boundary_id
  groups: CellGroup[]
  bridges: CellBridge[]

CellGroup
  id
  columns: CellColumn[]
  sounds: CellSound[]

CellColumn
  id
  role = letter | haraka | sukun | tanween | madd | mark | nasal_substitute | gap
  text
  source_character_ids[]
  source_unit_ids[]
  placement = main | above | below
  attached_to_column_id
  change = unchanged | inserted | replaced | omitted | gap
  tanween_form = stacked | open | null
  variant_id
  variant_choice
  anchor_unit_id
  side = before | after
  owned_sound_ids[]
  presented_sound_ids[]
  rule_occurrence_ids[]
  silence

CellSound
  sound_id
  column_ids[]
  rule_occurrence_ids[]

CellBridge
  merger_id
  before_group_ids[]
  after_group_ids[]
  sound: CellSound
~~~

The public cell DTO is nested in render order so a website can render it
without rebuilding lookup maps. IDs remain only where alignment or a bridge
crosses nested ownership. A private normalized index may exist inside the
package.

CellGroup is educational grouping. It must not be overloaded as orthographic
shaping or canonical-slot identity. CellBoundary orders every boundary-owned
group at that exact boundary. No group-kind taxonomy is needed until a fixture
proves one.

### 9.2 Normative tokenization and alignment

- The whole word is the outer visible cell.
- Every base, small vowel, small hamza, small waw/yaa, and mini noon unit gets
  its own main column.
- Base letters, small hamzas, and mini noon use role=letter. Sounded small
  vowels, small waw/yaa, vowel carriers, and madd signs use role=madd.
- Haraka, sukun, and tanween get separate smaller columns. Above/below
  placement and attached_to_column_id identify the exact main column they ride;
  shared group membership alone is not used as an attachment guess.
- Shadda and silence marks are composed directly into their main column text.
  They never open their own columns.
- Long-vowel quality and carrier may occupy separate columns in one group.
  One CellSound can span both.
- A silent or omitted letter still has a column so it can be greyed; it has no
  overflowing placeholder phoneme.
- source_character_ids and source_unit_ids are provenance, not displayed-text
  IDs. An inserted transformed column leaves both empty and has either an
  anchor_unit_id plus before/after side or boundary ownership.
- A replacement retains the exact replaced source provenance and uses change
  = replaced.
- A cell whose displayed state or sound participation depends on a selected
  variant carries its variant_id and variant_choice. Both are null when the
  selected variant does not affect that cell in the resolved boundary state,
  so adapters and settings UIs never infer provenance from codepoints or rule
  IDs.
- An omitted transformed column retains its exact source text and provenance
  so it can be greyed, while owning and presenting no performed sound.
- A source presentation sound with no honest source presenter receives an
  empty role=gap, change=gap column anchored to a unit/side or boundary. It has
  empty source provenance and no owned/presented sound; CellSound references
  it only for alignment. This does not invent a source glyph or ownership.
- Iltiqa insertion is an ordered boundary-owned group between two CellWords.
- A genuine idgham or other merger uses CellBridge with the shared CellSound.
- CellBridge uses plural group endpoints because one merger can span multiple
  educational groups.
- A merger's one primary CellSound lives inside its boundary's CellBridge, not
  again inside the host CellGroup. It renders exactly once between the words;
  its column_ids still align the contributor and host columns for
  co-highlighting.
- Sukun visibility, maddah folding, pausal zero, and carrier-seat handling are
  settled by the producer. Frontends never inspect codepoints or rule IDs to
  repair the rows.

Iqlab is also producer-owned. Transformed cells expose the silent/replaced
source component and a separate role=nasal_substitute column with exact sound
ownership. A script adapter may render a Digital Khatt mini meem or the
QPC-compatible no-glyph form, but neither SDK nor frontend discovers the split
by checking rule_id == iqlab.

The producer also sets tanween_form to stacked or open. Script adapters choose
the supported glyph for that declared form; they never derive open tanween by
inspecting a tanween codepoint together with a tajweed rule ID.

### 9.3 Rules in cells

Rules on visible letters attach to CellColumn.rule_occurrence_ids. Rules on
sounds attach to CellSound.rule_occurrence_ids. Both refer to the same native
occurrences and definitions.

Multiple rules may coexist, including:

- madd_iwad with madd_tabii;
- ordinary madd_silah with madd_tabii;
- madd_silah with jaiz or wajib before hamza;
- pausal_alif with madd_tabii;
- waqf drops with the rule naming the resulting long vowel.

The website can give overlapping rules separate underline lanes or a compact
combined hover. It must not invent a semantic fold.

### 9.4 Selective serialization

In process, a CellView refers to IDs on its AnalysisResult. A standalone JSON
cell envelope includes every referenced word, boundary, sound, rule occurrence,
rule definition, merger, source unit, source character, and silence reason.
The same closure rule applies to a standalone source or highlight envelope.

A core-only envelope contains no source-unit or source-character reference.
A source-only envelope contains no cell reference. Result-local IDs are
preserved across scopes.

For word-scoped cells:

- requested CellWords and their owned boundary groups are complete;
- every referenced source/core record is included;
- a bridge is emitted only when both endpoint groups are present;
- a scoped contributor can still present an externally hosted sound without a
  dangling bridge.

Every envelope validator has mutation tests for missing, mistyped, duplicated,
wrong-kind, and contradictory references.

## 10. Native analysis laws

The implementation must enforce these before serialization:

1. Source characters concatenate exactly to result.text().
2. Word text concatenates from its lexical source characters exactly.
3. N words have N + 1 boundaries, with one leading start and one trailing
   stop.
4. Boundary before/after are typed WordId or null, with exact
   leading/internal/trailing cardinality; word and boundary references are
   mutually consistent.
5. Ordinary no-override/override resolves join/stop; authored sakt
   no-override/override resolves sakt/stop. Sakt is never treated as waqf,
   ibtidaa, or ordinary join.
6. Every sound has one total order and one primary word allocation.
7. Word.sound_ids and Sound.word_id are exact ordered inverses.
8. Sound.rule_occurrence_ids and RuleOccurrence.sound_ids agree.
9. Every public rule target is actually affected; trigger-only context is not
   leaked as a target.
10. Source RulePlacement and LetterUnit rule queries agree with the same
    occurrence IDs.
11. Every Merger crosses one adjacent boundary and shares exactly one sound.
12. Every MergerPlacement resolves to one core Merger and agrees with its
    words, boundary, and sound.
13. Iltiqa insertions never appear as Merger records.
14. Every Character is exactly lexical-unit-owned, boundary-owned, or an
    explicitly typed passage separator.
15. Every sounded small vowel, small hamza, small waw/yaa, and mini noon has
    its own LetterUnit.
16. LetterUnit ranges reproduce exactly its character_ids, even when
    non-contiguous.
17. Every source sound has at most one owner; owned and presented sound arrays
    are disjoint.
18. Shadda and silence marks do not create their own educational columns.
19. A unit with a silence reason has no owned or presented sounds.
20. Cell columns partition every included display item in render order.
21. Above/below attachment resolves to an exact sibling column.
22. In a full CellView, every core sound appears in exactly one primary
    CellSound, either inside one CellGroup or one CellBridge.
23. A non-gap group CellSound's columns agree with the owning/presenting
    columns in its group. A gap CellSound is the only group exception to that
    agreement.
24. A gap column has empty provenance, ownership, and presentation and exactly
    one valid unit/side anchor or boundary owner.
25. Every CellBridge resolves to one Merger, owns the same primary CellSound,
    and its endpoint groups contain the MergerPlacement's contributor
    presenters and host owner. The bridged sound has no duplicate inline
    CellSound.
26. No iltiqa boundary group creates a CellBridge.
27. CellSound column references are ordered and nonempty, using an honest gap
    column where no source presenter exists.
28. Cell groups, boundary groups, sound spans, and bridge endpoints are closed:
    every referenced ID exists in the selected CellView.
29. A transformed inserted column has no invented source character or unit and
    has a valid unit/side anchor or boundary owner.
30. A transformed replaced or omitted column retains exact source provenance;
    an omitted column retains source text.
31. A column's variant_id and variant_choice are either both null or match the
    resolved result selection and accompany an actual variant-dependent
    displayed state or sound participation.
32. Highlight groups refer only to source units and existing sounds; their
    ranges are ordered and non-overlapping.
33. A full highlight view contains every sound exactly once.
34. Validators reject missing, duplicated, contradictory, and wrong-kind IDs
    even when the underlying integer value exists in another ID space.
35. Native tests pass when every legacy projection module is unavailable.

## 11. Rule-model audit before DTO freeze

The current enum has 41 members at the target head, but that number is not a
contract. It mixes genuine rules, overloaded pausal outcomes, and a synthetic
orthographic-silence classification. Separately, the current result path also
adds derived teaching labels outside the enum; the redesign removes that
second mechanism by making the useful classifications native.

The candidate native Hafs inventory is 44 IDs:

~~~text
izhar
ikhfaa
iqlab
idgham_bi_ghunnah
idgham_bila_ghunnah
ghunnah_mushaddadah
izhar_shafawi
ikhfaa_shafawi
idgham_shafawi
idgham_mutamathilayn
idgham_mutaqaribayn
idgham_mutajanisayn_kamil
idgham_mutajanisayn_naqis
lam_shamsiyyah
lam_qamariyyah
qalqala_sughra
qalqala_kubra
qalqala_akbar
tafkheem
tarqeeq
imala
tashil
ishmam
madd_tabii
madd_wajib_muttasil
madd_jaiz_munfasil
madd_lazim
madd_arid_lissukun
madd_leen
madd_iwad
madd_badal
madd_silah
ibdal_hamza
hamza_wasl_silent
hamza_wasl_fatha
hamza_wasl_kasra
hamza_wasl_damma
iltiqa_kasra
iltiqa_fatha
iltiqa_shortening
waqf_diacritic_drop
waqf_silah_drop
waqf_taa_marbuta
pausal_alif
~~~

This is a candidate to prove with exhaustive fixtures, not a count to protect
for its own sake.

### 11.1 Accepted folds and renames

- Keep izhar for noon/tanween, izhar_shafawi for meem, and lam_qamariyyah for
  the article lam as three distinct rules. Keep ikhfaa_shafawi distinct.
- Rename ikhfaa_haqiqi to ikhfaa.
- Rename madd_arid_lil_sukun to madd_arid_lissukun.
- Rename iwad to madd_iwad.
- Rename wasl_elision to hamza_wasl_silent.
- Rename taa_marbuta_pausal to waqf_taa_marbuta.
- Keep the existing ibdal_hamza identifier but correct its participants to
  target the lexical hamza that is replaced, not hamzat-wasl as if it were the
  replaced consonant.
- Split wasl_start into hamza_wasl_fatha, hamza_wasl_kasra, and
  hamza_wasl_damma. The domain already resolves the starting vowel; clients
  should not derive the public rule name from it.
- Remove orthographic_silence from Rule. It is a source-unit state, not a
  recitation rule occurrence.

### 11.2 Madd badal, iwad, and silah

madd_badal remains first-class:

- ordinary badal emits madd_badal and madd_tabii;
- if another cause determines a contextual length, badal remains present and
  the contextual madd replaces tabii;
- no sughra/kubra teaching layer is added.

madd_iwad names the fathatan-to-long-aa transformation and co-occurs with
madd_tabii for the resulting natural length.

There is one madd_silah:

- ordinary silah emits madd_silah plus madd_tabii;
- before qualifying hamza it emits madd_silah plus madd_jaiz_munfasil or
  madd_wajib_muttasil, without madd_tabii;
- at waqf it emits no madd_silah and uses waqf_silah_drop.

No silah_sughra or silah_kubra identifier is introduced.

### 11.3 Hamzat-wasl and ibdal

hamza_wasl_silent names the wasl outcome in which the prosthetic consonant and
its helping vowel are not pronounced.

At ibtidaa before a quiescent lexical hamza:

- the appropriate hamza_wasl_kasra or hamza_wasl_damma occurrence names the
  starting quality;
- ibdal_hamza targets the following lexical hamza that is replaced/silenced;
- the starting vowel is lengthened with the matching quality;
- visible letter and sound placements record both effects without claiming
  that hamzat-wasl itself was the replaced hamza.

### 11.4 Waqf decomposition

Delete generic pausal_sukun. It currently overloads unrelated events.

Use these exact outcomes:

| Outcome | Native occurrences |
| --- | --- |
| Ordinary final fatha, damma, or kasra | waqf_diacritic_drop |
| Dammatan or kasratan | one waqf_diacritic_drop on the written tanween |
| Non-taa-marbuta fathatan becoming long aa | waqf_diacritic_drop + madd_iwad + madd_tabii |
| Taa marbuta with any haraka or tanween | waqf_diacritic_drop + waqf_taa_marbuta |
| Performed silah suppressed | waqf_silah_drop; no madd_silah |
| Compatible final waw/yaa becoming long | waqf_diacritic_drop + madd_tabii |
| Aatani hadhf at 27:36:8 | yaa_aatani_waqf variant omission plus waqf_diacritic_drop on each actually omitted vowel mark; no glide rule |
| Aatani ithbat at 27:36:8 | waqf_diacritic_drop on the final fatha + madd_tabii |
| Authored seven-alif realization | pausal_alif + madd_tabii |

waqf_diacritic_drop is one character-only occurrence per omitted written
haraka or tanween. A tanween scalar receives one occurrence even though its
recitation contains a vowel and nunation. The occurrence targets the source
diacritic, owns no performed sound, and never underlines the base consonant
merely because that consonant becomes sakin.

For iwad, waqf_diacritic_drop names the removed fathatan, madd_iwad names the
replacement transformation, and madd_tabii names the resulting long sound.

waqf_taa_marbuta names only the taa-to-haa consonant substitution. Associated
vowel or tanween loss remains one waqf_diacritic_drop.

There is no waqf_glide_drop rule. The only genuinely deleted written glide is
the optional yaa of Aatani, and that outcome is already first-class as
yaa_aatani_waqf=hadhf. At waqf with hadhf, its transformed yaa column remains
present with change=omitted so it can be greyed; it owns and presents no sound
and carries variant_id=yaa_aatani_waqf, variant_choice=hadhf. At waqf with
ithbat, the retained, sounding yaa column carries the same variant_id with
variant_choice=ithbat and contributes to the resulting i:. At wasl the two
selections produce identical cells, so their per-column variant provenance is
null. Ordinary final waw/yaa cases are not deletion: after the diacritic drops,
the letter contributes to a natural long vowel under madd_tabii.

### 11.5 Pausal alif

pausal_alif is restricted to the authored seven-alif boundary alternation:

- at wasl it names the shortened outcome and silent carrier;
- at waqf it names the realized long aa and co-occurs with madd_tabii;
- it never means every final alif;
- its long waqf outcome never receives waqf_diacritic_drop.

This prevents both pausal_alif and the removed pausal_sukun from becoming
miscellaneous waqf buckets.

### 11.6 Ibtidaa shadda drop

Remove fakk_idgham from Rule. It changes and classifies no sound: the written
word-initial shadda attests a merger with the preceding word, and at ibtidaa
that merger simply does not occur. The existing reverse classifier duplicates
the merger tables and can drift from the actual idgham laws.

Model the visible outcome directly from source attestation plus resolved
performance:

- joined: retain the shadda and publish the genuine merger bridge;
- started: the transformed main column uses change=replaced, omits only the
  shadda from text, retains its complete source-character provenance, and
  aligns the one plain consonant;
- source presentation: retain the literal written shadda;
- publish no rule underline, fake merger, or preceding-word participant.

Use ibtidaa_shadda_drop as the implementation and fixture name. It is not a
tajweed Rule or hover label. The shorter ibtidaa_shadda is avoided because it
does not say whether the shadda is applied or omitted.

### 11.7 Internal occurrence correction

The current Participants.host is overloaded as merger host, classifier
context, and occasional public second participant. The assembler then drops
most second participants through an allowlist. This is lossy and misleading.

Replace it with explicit internal roles:

- subjects: parts actually classified or transformed;
- context: trigger-only parts needed to decide the rule;
- boundary: resolved boundary when behavior depends on it;
- effects: changed sounds, silence, insertion, replacement, or merger.

Only subjects and effects become public targets. Context stays private. A
genuine merger carries explicit before/after contributors rather than abusing
a generic host field.

## 12. Variants and extra phonemes

available_variants returns VariantDefinition records with:

- id;
- concise name and summary;
- default choice;
- ordered choices, each with value, label, and alphabet-specific phoneme
  preview where meaningful.

available_extra_phonemes returns ExtraPhonemeDefinition records with:

- id;
- concise name and summary;
- default enabled state;
- disabled and enabled token previews for the chosen alphabet.

This is enough for intuitive UI without prescribing a widget. For example,
the iqlab and ikhfaa-shafawi variants can render as a two-choice phoneme
selector showing the two resulting tokens. Boolean extra distinctions can use
a compact toggle with before/after token previews.

Catalogue IDs, choices, defaults, and request validation are exact tests.
Neither catalogue imports or wraps the other.

## 13. Ownership across repositories

### 13.1 Phonemizer owns

- source characters and letter-unit tokenization;
- rule inventory, names, short hover summaries, and occurrences;
- rules on visible units and sounds;
- true sound ownership, shared presentation, and silence reasons;
- resolved boundary behavior and stop signs;
- mergers and boundary insertions;
- source/transformed cell grouping and alignment;
- continuous-text highlight groups, including silent folding;
- variants and optional-phoneme catalogues.

### 13.2 QUA SDK integration owns

- translating native DTOs to the frozen v11 shard wire schema;
- converting native IDs to shard-local IDs;
- attaching reciter, timing, and shard transport metadata;
- documented legacy vocabulary translation.

It must not scan codepoints, regroup columns, infer carrier/haraka spans, fold
silent units, discover mergers, or classify rules.

### 13.3 Inspector owns

- rendering the producer-supplied rows and spans;
- CSS, colour, hover, selection, and responsive behavior;
- timestamp and audio interaction for QUA;
- development diagnostics.

The current Inspector reconstructs groups, spanning sounds, riding marks,
iqlab splits, and iltiqa placement. Those domain decisions move to the
phonemizer. Inspector code remaining after migration should be recognizably
presentational.

### 13.4 Website owns

- request state and URL state;
- surah/ayah controls and uniform random-ayah interaction;
- stop-cell click interaction;
- settings layout;
- copying text or phonemes;
- responsive visual presentation.

It consumes the phonemizer directly through its own thin backend and has no
QUA SDK dependency.

## 14. QUA v11 compatibility and 114-shard gate

The native contract is not shaped around v11. A thin adapter preserves v11
while QUA and Inspector migrate.

Expected vocabulary translations include:

| Native | Frozen v11 |
| --- | --- |
| izhar on noon/tanween | izhar |
| izhar_shafawi | izhar_shafawi |
| lam_qamariyyah | omitted |
| ikhfaa | ikhfaa |
| ghunnah_mushaddadah | ghunnah |
| qalqala_akbar | qalqala_kubra |
| tarqeeq | omitted |
| madd_arid_lissukun | madd_arid_lil_sukun |
| hamza_wasl_silent | hamza_wasl_elision |
| hamza_wasl_fatha/kasra/damma | same exact v11 tag |
| ibdal_hamza | ibdal_hamza |
| iltiqa_shortening | iltiqaa |
| iltiqa_kasra | iltiqaa_kasra |
| iltiqa_fatha | iltiqaa_fatha |
| waqf_taa_marbuta | taa_marbuta_pausal |
| waqf_diacritic_drop | place pausal_sukun on the corresponding legacy cell and deduplicate within that cell's rules array |
| waqf_diacritic_drop with non-taa-marbuta madd_iwad | omit pausal_sukun; keep madd_iwad + madd_tabii |
| waqf_silah_drop | pausal_sukun |
| yaa_aatani_waqf=hadhf omitted yaa | place pausal_sukun on the omitted yaa's legacy cell from explicit variant provenance, then deduplicate within that cell's rules array |
| ordinary madd_badal + madd_tabii | madd_tabii |
| madd_badal + contextual madd | contextual madd only; suppress badal and compatibility tabii |
| ordinary madd_silah + madd_tabii | madd_tabii |
| madd_silah + jaiz/wajib | exact jaiz/wajib v11 tag, without duplicate tabii |
| pausal_alif at wasl | omitted |
| pausal_alif at waqf | pausal_sukun |
| native orthographic-silence state | orthographic_silence |

The adapter maps each native drop placement to its corresponding frozen-v11
cell and de-duplicates only within that cell's rules array. It suppresses this
mapping only for non-taa-marbuta iwad fathatan. The mapping is verified against
the actual v11 type before implementation; this table is not permission to
emit a made-up tag.
Exact fixtures cover ordinary and contextual badal, every final haraka/tanween
form, taa marbuta with and without each tanween type, stopped silah, both
Aatani choices at wasl and waqf, and pausal alif in both boundary states.

Run the adapter over all 114 v11 shards for one fully migrated reciter with
waqf/ibtidaa information. Compare:

- reference and word order;
- exact source characters;
- phoneme order and tokens;
- source unit and cell grouping;
- sound-to-column spans;
- rules on letters and sounds;
- silent and omitted units;
- mergers and cross-word bridges;
- boundary start, join, sakt, and stop behavior.

Every difference receives exactly one reviewed category:

1. adapter-exact parity;
2. documented vocabulary translation;
3. corrected native domain behavior with a fixture/law;
4. deliberate QPC Hafs script/font difference;
5. frontend repair moved into the producer;
6. unresolved defect, which fails the gate.

Frozen old output is evidence, not expected truth. Snapshot regeneration alone
cannot approve categories 2 through 5.

## 15. Removing the old projection stack

Do not place the native result on top of the existing serialized graph.

| Current module | Disposition |
| --- | --- |
| phonemize/document.py | Rewrite as the native result and selective-view owner |
| phonemize/schema.py and schema checks | Rewrite with typed closed-reference validation |
| phonemize/nodes.py | Delete |
| phonemize/edges.py | Delete |
| phonemize/assemble.py | Delete after native assembly replaces it |
| phonemize/pairing.py | Delete |
| phonemize/reach.py | Delete |
| phonemize/respell.py | Delete |
| phonemize/legacy_views.py | Delete |
| phonemize/labels.py | Delete after rules become native |
| phonemize/derived.py | Move proven facts to their actual owner, then delete |
| phonemize/recited.py | Delete; add a separately named private transformed-cell builder with no general text writer |
| phonemize/ordering.py | Keep only if it is pure Performance ordering; otherwise replace |

The exact filenames must be refreshed against the implementation branch before
deletion, but the architectural disposition is binding.

The one permitted private flow is:

~~~text
Session -> AnalysisFacts -> core / source / highlights / cells
~~~

AnalysisFacts is a compact immutable cache of already resolved facts, not a
second public model and not another serialization format. Cells consume those
facts and source units; they do not revisit Performance to reclassify rules.

tools/structure_lint.py must enforce:

- native analysis modules may import Session, model, and direct rendering
  owners, but not legacy projection modules;
- the literal banned set is assemble, nodes, edges, derived, pairing, reach,
  respell, legacy_views, and the old recited module;
- neither direct nor transitive dependencies from native analysis reach that
  banned set;
- transformed-cell builder AST checks ban rule-ID branching, Unicode/codepoint
  classification, and direct script-inventory lookup;
- public exports match an exact allowlist;
- graph node/edge and transformed-text types are not exported;
- the candidate-wheel manifest proves every deleted projection module is
  absent;
- the native API works while all legacy modules are unavailable.

Rollback is the prior commit and frozen wheel, not a compatibility flag that
keeps both architectures in the candidate package.

## 16. Website implementation

### 16.1 Product scope

The first public demo shows only the most relevant projections:

- exact Qur'anic source text;
- copy text;
- copy phonemes;
- whole-word educational cells with aligned letters and phonemes;
- rules on letters and rules on sounds;
- clickable boundary stop cells;
- variants;
- extra phonemes;
- a link to the latest PyPI release;
- a link to GitHub.

It does not include audio, playback, timestamps, a written/recited toggle,
respelling, graph inspection, keyboard-only rule interaction, or long teaching
panels.

Rule explanation is hover-only and concise. The legend is built from rules
actually present in the result plus tajweed_rules metadata. There is no
click-to-lock explanation.

### 16.2 Main flow

1. Load a sensible default ayah.
2. Select surah and ayah, enter a reference, or choose Random ayah.
3. Render exact source text in QPC Hafs.
4. Render whole-word cells in RTL reading order.
5. Click an internal stop-sign cell to add/remove a stop override: the visible
   result switches join/stop ordinarily and sakt/stop at an authored sakt site.
6. Change a variant or extra-phoneme setting and re-render the same reference.
7. Copy only source text or phonemes.

Random ayah is uniform over the global ayah population. Choose one integer in
the inclusive global ayah range, then map it through cumulative surah counts.
Do not choose a random surah first. Tests cover first, last, and every surah
transition.

### 16.3 Cell behavior

- Word is the outer cell; letter columns and phoneme cells are inside it.
- Letter and phoneme rows align from producer-supplied spans.
- Silent letters have no phantom phoneme cell and do not shift later
  alignment.
- Omitted letters remain visible and greyed where educationally useful.
- Inserted and replaced columns use a restrained dashed visual.
- Haraka and tanween are smaller above/below columns attached to the main
  letter group.
- Shadda and silence marks stay in the main cell.
- Genuine cross-word mergers retain the in-between bridge presentation.
- Iltiqa boundary insertion appears between words without masquerading as a
  merger.
- Rule underlines attach to the exact producer-supplied letter or sound cell.
- Every cell has a content-based minimum inline size large enough for its
  Arabic or phoneme content. It never shrinks until text overflows the box.
- Long ayat wrap by whole-word containers. A word does not split its internal
  grid across lines.
- Mobile preserves readable minimum cells and uses horizontal containment only
  where an unusually long word cannot fit.

### 16.4 Settings

Variants and extra phonemes are separate visual sections. Render from their
separate catalogues rather than hardcoded frontend inventories.

Choice presentation follows the data:

- two phoneme outcomes use a compact segmented phoneme selector;
- boolean extra distinctions use a toggle with concise token previews;
- larger choice sets use a compact select only if segmented choices no longer
  fit;
- default and current state are visually obvious;
- changing a setting preserves the current ayah and boundary choices.

### 16.5 Stop cells

Every internal word boundary receives a small between-word control:

- exact stop sign when one is written;
- | | fallback otherwise;
- current state visible without explanatory prose;
- hover label may say Join, Stop, or Sakt;
- click is the only required interaction for the first release.

The frontend sends only stop overrides and renders the returned resolved
state. It never requests sakt or applies waqf, ibtidaa, or sakt transformations
itself.

## 17. QPC Hafs font and script gate

Use the supplied Uthmanic Hafs v2.0 font from the QUD source, copied into the
web repository with provenance and license information. Apply it only to
Qur'anic source and letter-cell text; the interface and phoneme rows use the
normal UI font.

Before accepting it:

1. Collect every Unicode scalar in the full Hafs source corpus.
2. Collect every scalar emitted by transformed cells.
3. Check the font cmap covers the complete set.
4. Shape representative clusters with the browser/HarfBuzz path.
5. Render screenshot fixtures for dagger alif, small vowels, small hamzas,
   mini noon, carrier seats, shadda, silence marks, tanween, madd marks, stop
   signs, stacked/open tanween, pausal alif, ibdal, iqlab, iltiqa, and mergers.
6. Confirm there is no fallback font in those fixtures.
7. Confirm source text round-trips exactly and transformed cells do not require
   Digital Khatt-only glyph conventions.

The iqlab mini-meem presentation used by Digital Khatt is intentionally not
copied. QPC Hafs source/script behavior determines the letter cells; the
selected iqlab phonemes still appear in the phoneme row and variant control.

## 18. Web repository and deployment

The current web repository is a one-commit FastAPI/static app importing an
obsolete core package and pinning the phonemizer Git main branch. Treat it as a
replacement, not an incremental UI reskin.

Recommended maintainable shape:

- FastAPI remains a thin Python backend over quranic-phonemizer;
- a small TypeScript component frontend owns the interactive nested cell UI;
- generated API types or runtime schema validation catch DTO drift;
- the backend serializes only the views requested by this demo;
- frontend components never import a tajweed rule-ID switch.

The first endpoints are:

| Endpoint | Purpose |
| --- | --- |
| GET /api/meta | Surahs, rule definitions, separate setting catalogues, package/schema versions, links |
| POST /api/analyse | Source text, phonemes, boundaries, transformed cells, occurring rules |
| GET /api/random-ayah | Uniform global ayah mapped to surah and ayah |

The exact frontend library remains an implementation-time choice after a small
cell-layout spike. Plain untyped JavaScript is not acceptable for the nested
DTO; a framework is not justified unless the spike shows it materially
simplifies state and layout.

Dependency policy:

- production pins an exact released PyPI version and lock/hash;
- never deploy from Git main;
- coordinated CI can build the phonemizer wheel from the target commit and
  install that artifact into web tests;
- GET /api/meta exposes package and schema versions;
- web CI fails on an unexpected schema version.

Release order:

1. build and test the phonemizer candidate wheel;
2. install that exact wheel in the web staging build;
3. run API, font, screenshot, mobile, and smoke gates;
4. publish the phonemizer release;
5. update the web lock to that exact version;
6. deploy and smoke-test production;
7. retain the previous web image and phonemizer wheel for rollback.

There is no deployment manifest in the current web repository. Before choosing
a platform, audit the current domain/DNS and hosting owner. Prefer one
container deployment for FastAPI plus static assets on the existing supported
platform. Do not split the app across new services without an operational
need.

## 19. Implementation phases

### Phase 0: freeze untrusted evidence

- Build and hash a wheel from the old projection baseline.
- Save representative old outputs and all 114 v11 shards outside the candidate
  package.
- Record known incorrect categories.
- Add a differential runner that executes old and new wheels in separate
  environments.

Exit: comparisons are reproducible without importing legacy modules into the
new package.

### Phase 1: correct the internal rule model

- Replace overloaded occurrence participants with subjects, context, boundary,
  and effects.
- Apply accepted folds, renames, and splits.
- Make badal, iwad, and silah overlaps native.
- Replace generic pausal_sukun with the precise diacritic, silah, taa-marbuta,
  and pausal-alif outcomes.
- Remove waqf_glide_drop and model Aatani directly as the
  yaa_aatani_waqf variant outcome.
- Delete or privatize the misleading generic Onset.GLIDE abstraction if the
  implementation audit confirms its only use is Aatani.
- Correct ibdal targets and pausal-alif direction.
- Demote orthographic silence from Rule.
- Remove fakk_idgham and its reverse merger-table classifier.
- Add ibtidaa_shadda_drop transformed-cell fixtures at every affected start
  site.
- Add exhaustive occurrence target fixtures before DTO work.

Exit: the internal model states the facts the consumer contract needs without
teaching-label or assembler repair.

### Phase 2: prove source-unit and cell tokenization

- Encode the exact Character and LetterUnit laws.
- Build a fixture matrix for every small mark, carrier, seat, attachment, and
  silence case.
- Port the correct QUA v11 cell behavior into producer-owned expected fixtures.
- Specify the neutral iqlab source/substitute split for every supported script.
- Make stacked/open tanween a producer fact and fixture its script-specific
  glyph rendering.
- Resolve sukun visibility, maddah folding, and pausal zero explicitly.
- Run the QPC font coverage and shaping spike.

Exit: no frontend rule or codepoint heuristic is needed to produce rows.

### Phase 3: implement the native core

- Rewrite AnalysisResult and typed DTOs.
- Build the private AnalysisFacts cache directly from Session.
- Assemble words, boundaries, sounds, rules, and mergers only from those
  resolved facts.
- Add closed-reference validation and deterministic ordering.
- Implement separate catalogue functions.

Exit: text, phonemes, boundaries, sounds, rules, and mergers pass native laws
without any legacy projection import.

### Phase 4: implement source and highlights

- Build exact Characters and LetterUnits.
- Attach rule placements and honest sound ownership.
- Add typed silence reasons.
- Implement highlight groups for silent folding, insertions, and mergers.
- Compare the highlight view with audited legacy teleprompter cases, not blind
  legacy equality.

Exit: continuous source-text highlighting needs only sound timing IDs.

### Phase 5: implement cells

- Build source and transformed CellViews from native facts.
- Add whole-word groups, attached marks, sound spans, omission/replacement
  state, boundary insertion groups, and merger bridges.
- Prohibit rule-ID and codepoint reconstruction in the cell builder.

Exit: the QUA Inspector and website can render rows without domain repairs.

### Phase 6: schema, transport, and compatibility adapter

- Freeze typed JSON schema for the native result and each selective view.
- Implement a shadow thin v11 adapter in the QUA integration owner while the
  old QUA path remains available only in its frozen comparison environment.
- Run the 114-shard classified comparison between those separate paths.
- Add exact wheel/API export tests.

Exit: native semantics and frozen v11 wire compatibility are separately green.

### Phase 7: destructive cutover

- Remove the old graph/projection modules according to section 15.
- Update README and public API documentation to the consumer contract.
- Build the release-candidate wheel after deletion.
- Prove old public types and modules are absent.
- Re-run native, schema, export, wheel-manifest, and all 114-shard gates against
  that exact post-deletion wheel.

Exit: there is one public architecture.

### Phase 8: migrate QUA and Inspector

- Replace SDK cell reconstruction with native consumption plus v11 translation.
- Remove Inspector grouping, folding, and rule reconstruction.
- Run PR 78/81 and audio PR 233/234 behavior fixtures against the new owner.
- Re-run the 114-shard gate after deleting the old SDK reconstruction.
- Review the final diff for any domain decision still duplicated.

Exit: SDK is a wire adapter and Inspector is a renderer.

### Phase 9: rebuild the website

- Replace the obsolete backend import and dependency.
- Add the thin analysis/meta/random API.
- Implement the cell-layout spike, then the typed components.
- Apply the Impeccable design pass for hierarchy, spacing, responsive behavior,
  state clarity, and visual restraint.
- Add QPC font, rule hover, stop toggles, settings, random ayah, and copy
  actions.
- Run screenshot, interaction, accessibility-smoke, and mobile gates.

Exit: the public demo meets section 16 without frontend domain logic.

### Phase 10: release and deploy

- Publish the phonemizer package.
- Pin the exact release in the web lock.
- Deploy staging then production using section 18.
- Verify PyPI and GitHub links, version display, random ayah, representative
  rules, stop toggles, and mobile layout.

Exit: both repositories are released from mutually tested immutable artifacts.

## 20. Test and acceptance gates

### 20.1 Fast package gate

- formatter and lint;
- type checking;
- tools/comment_lint.py;
- tools/structure_lint.py;
- targeted rule and DTO tests;
- schema closed-reference tests;
- tests with legacy modules unavailable.

### 20.2 Rule hard-case gate

At minimum:

- distinct noon/tanween izhar, izhar shafawi, and lam qamariyyah;
- ikhfaa and ikhfaa shafawi;
- every idgham merger family;
- ibtidaa shadda drop at every affected start site, with no Rule occurrence;
- ordinary/contextual badal;
- ordinary/contextual/stopped silah;
- madd iwad overlap;
- three hamzat-wasl start vowels;
- hamza-wasl silence and ibdal;
- iltiqa kasra, fatha, and shortening;
- one waqf_diacritic_drop per omitted written haraka/tanween;
- stopped silah;
- both Aatani variant choices at wasl and waqf, with variant provenance and no
  glide-drop Rule;
- compatible final waw/yaa lengthening;
- taa marbuta;
- seven pausal alifs in wasl and waqf;
- sakt versus stop;
- ishmam soundless gesture semantics.

Each asserts exact subjects, context privacy, sound targets, source placements,
boundary placements, and overlaps.

### 20.3 Source/highlight/cell gate

- full corpus source reconstruction;
- exact unit inventory and no accidental unit merges;
- independent small vowels, small hamzas, small waw/yaa, and mini noon;
- shadda and silence-mark composition;
- attached haraka and tanween columns;
- silent ownership emptiness;
- merger presentation and co-highlighting;
- iltiqa boundary insertion without Merger;
- all transformed insertion/replacement/omission families;
- no overflowing representative Arabic or phoneme cell;
- no rule-ID/codepoint branches in consumers.

### 20.4 Full compatibility gate

- all 114 reciter shards;
- every difference classified;
- no unresolved category;
- adapter emits only frozen v11 tags;
- native tests contain no v11 expectations;
- legacy equality never substitutes for a native law.

### 20.5 Performance gate

Measure cold and warm construction for one ayah, one surah, and the full Qur'an:

- core only;
- source;
- highlight groups;
- one word of cells;
- one ayah of cells.

Views are cached immutably after first construction. Phonemes-only use must not
pay for source tokenization or cells beyond the unavoidable engine result.

### 20.6 Website gate

- uniform global random-ayah mapping;
- selector/ref URL state;
- ordinary join/stop and authored sakt/stop;
- variant and extra-phoneme settings remain separate;
- iqlab/ikhfaa-shafawi phoneme-choice previews;
- exact text and phoneme copy only;
- hover-only rule explanation;
- no audio/playback affordance;
- no source/transformed switch in the first release;
- QPC font coverage and no fallback;
- desktop, narrow mobile, RTL, and long-ayah screenshots;
- content-based cell minimum size and no overflow;
- exact package/schema version match;
- PyPI latest and GitHub links.

## 21. Open decisions register

These do not block Phase 1:

| Decision | Default direction | Closing evidence |
| --- | --- | --- |
| Exact typed silence reasons | Small stable enum by real cause, not one value per rule | Full silent-unit fixture matrix |
| Sukun visibility in transformed cells | Producer chooses one consistent QUA-derived result | Cell fixture and QPC rendering review |
| Maddah and pausal-zero folding | Producer-owned, never Inspector-owned | v11 fixture audit |
| Exact per-script glyph for nasal substitute and open tanween | Semantic role/form is native; glyph is script-owned | QPC and Digital Khatt fixture matrix |
| Exact TypeScript UI library | Smallest typed component solution after spike | Cell-layout/state spike |
| Current production host | Reuse existing viable container host | DNS/hosting audit |

Adding or removing a rule after this point requires changing its internal law,
native fixtures, metadata, v11 mapping, and website legend behavior together.

## 22. Definition of done

The redesign is complete when:

1. Consumers can obtain text, phonemes, boundaries, sounds, rules, mergers,
   source units, highlights, or cells directly and selectively.
2. Variants and extra phonemes remain independent catalogues and settings.
3. Boundaries use before/after plus start, join, sakt, or stop, with no edge,
   advice, or allowed-states output.
4. Silent letters own no sounds, while optional highlight groups encode
   domain-correct folding.
5. Source and transformed cell presentations share native sound/rule IDs, but
   no general transformed text exists.
6. Letter tokenization, attached marks, sound spans, mergers, and boundary
   insertions are producer-owned.
7. The audited native rule inventory and targets are correct before DTO freeze.
8. The old graph, alignment, respelling, teaching-label, and general recited
   text projection code is removed from the shipped package.
9. QUA v11 compatibility passes all 114 shards through a thin classified
   adapter.
10. QUA SDK and Inspector contain no duplicated domain reconstruction.
11. The website renders the QPC Hafs script/font pair, intuitive cells, stop
    toggles, separate settings, uniform random ayah, copy actions, and links
    without audio or unnecessary explanatory UI.
12. Production pins the exact tested phonemizer release and both repositories
    have an immutable rollback artifact.
