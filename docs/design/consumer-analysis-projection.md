# Consumer analysis projection

Status: accepted implementation direction, with the small open decisions in
section 21 still to be closed by fixtures.

Target baseline: riwayah-agnostic-refactor at 789a459.

This document is the implementation plan for replacing the current public
graph and its alignment, respelling, and derived-label projections. It also
defines the domain contract needed by the website, QUA v11 compatibility
adapter, Inspector, and continuous-text highlighting.

The current projections are not a correctness oracle, and a frozen build of
them is useful only as untrusted differential evidence: every match and every
difference still has to be judged against native laws and reviewed fixtures.

That is a statement about their standing, not an accusation. The case for
replacing them is that two public models is the cost, not that the old one is
wrong. Section 11 audits real defects and every one of them is in the rule
model this document keeps; the projection modules are being retired because a
consumer should not have to traverse a graph to ask what a letter sounds, and
because maintaining a second public architecture to answer that is the
expense. A module whose callers are all gone but which has no successor is made
private and retargeted rather than deleted; section 15 marks those rows Retain
private.

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
result.cells(presentation="transformed")   # or "source"
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

schema_version is a monotonic integer, matching the shard convention. It is
bumped when a DTO field or a role, change, state, or placement value is added,
removed, or changes meaning, and when a law changes what a consumer may rely
on. A rule added to or removed from the inventory does not bump it: the
catalogue is data reached through tajweed_rules, which is what section 12.1
keeps out of the shape.

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

Sakt coverage is what the ledger authors. Not every site a reader may take a
sakt at carries one, so a boundary the ledger does not name resolves to join
like any other; 18:1:11 is the case to know. Adding a site is a ledger change,
not a contract change.

stop_sign is single-valued. One site writes two marks at the same boundary --
36:52 carries both a sakt seen and a preferred-stop sign -- and there the
stop advice wins and the sakt mark is not published. A boundary shows the
reader one sign.

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

SourceView carries any exact sign characters through boundary_id, and CellView
gives every internal boundary a stop-sign column so a consumer never reads the
sign back out of word text. The | | fallback is presentation, not source text.

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
the boundary, and transformed cells place their inserted column at that
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
| silence | Why this unit is silent: null, a rule occurrence ID, or orthographic |

The role vocabulary is letter, haraka, sukun, and tanween. It is not a mirror of internal SlotFact names, and it has no
catch-all member: the script inventory is total over its scalars, so a mark
with no role is a producer bug, not an “other”.

The tokenization is normative. A scalar opens its own unit when it occupies
the vowel position, or when it owns a sound in some boundary state. Every
other mark folds into the unit whose fact it states:

- a base letter is a unit, and so is every letter the rasm leaves out and
  writes small: combining hamza, small waw, small yaa, and mini noon. These
  are letters, not marks, and they take role=letter;
- haraka, sukun, and tanween each occupy the vowel position, so each is a
  unit. A sukun owns no sound but is not a silent letter and has no silence
  reason merely because it denotes the absence of a vowel;
- dagger alif is a unit and takes role=letter. It is a written alif the rasm
  leaves out, like the small waw and small yaa beside it. Whether any of them
  lengthens the vowel before it or stands as a consonant of its own is a
  canonical fact, not a written one, so that split belongs to the cell column
  role and not here;
- the mini seen of a seen/saad khilaf is a unit, on the same test as any
  letter: it can own the sound its site reads. The base saad can own it
  instead, so the two are a pair and the resolved variant silences one of
  them. Its above/below position states which reading the site takes by
  default;
- shadda, maddah, the Quranic silence mark, the pausal zero of the seven
  alifs, the imala, ishmam, and tashil marks, and a tatweel seat all stay
  Characters inside the unit they qualify. None owns a sound and none occupies
  the vowel position: the box that owns the fact carries the mark and the
  rules placed on it;
- stop signs, sakt signs, and separators are boundary characters, not word
  letter units.

Character, LetterUnit, and shaping clusters are not required to coincide.
This is intentional. A main unit can have multiple ranges when an independently
tokenized haraka occurs between its base and shadda. written_on_unit_id states
orthographic carrier/seat attachment; it is not cell-column attachment. The source string remains continuous and font-shaped as one string,
while producer-supplied scalar ranges state exact semantics.

### 7.3 Ownership, presentation, and silence

owned_sound_ids is causal ownership. presented_sound_ids is additional,
non-owning visible sharing. The two arrays are disjoint:

- an ordinary pronounced unit owns its sound and has no need to repeat it as
  presented;
- a merger contributor does not own the host's sound but may present the
  shared sound;
- a genuinely silent letter owns and presents no sound and has a silence
  reason. That reason is the rule occurrence that silenced it, so a consumer
  resolves it to a RuleDefinition and gets the name and summary the phonemizer
  already owns. There is no second vocabulary of causes to drift from the
  rules;
- the one silence no rule accounts for is a letter the script writes and the
  reading does not read -- the alif of قَالُوا۟ -- which after 11.1 has no
  occurrence to name. It takes the literal orthographic. Those are the only
  two forms silence takes;
- a shadda or silence mark can be soundless notation inside another unit
  without itself becoming a silent-letter unit;
- a sukun is its own soundless notation unit without a silence reason.

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

### 8.1 The relation is the legacy letter-phoneme entry, made native

A HighlightGroup is one entry of the legacy letter-phoneme mapping described
in docs/legacy/letter-phoneme-mappings.md, expressed in native IDs instead of
concatenated characters and phoneme strings. That specification already names
every fold this view needs, and it already carries programmatic validation.
It is the source for the folding rules below and for laws 33a to 33d; it is
not an oracle for any individual result.

The phonemizer, not the consumer, decides silent folding and co-highlighting.
There are exactly three fold directions, and every silent unit takes one:

- back: a silent unit joins the group of the unit before it. Silent alif, waw,
  and yaa; the alif after tanween; the skipped mini yaa of a stopped Aatani.
- forward: a silent unit at a word start joins the group of the next sounding
  unit. Silent hamzat wasl, the article lam before a sun letter, and the
  hamzat wasl or silent long vowel of an iltiqa.
- across: a silent unit at a word end joins the first sounding unit of the
  next word. Cross-word idgham of every family, and the iltiqa chain.

A unit that keeps a sound of its own never folds. That is what separates
idgham, which folds across, from ikhfaa and iqlab, which do not: the nasalized
noon still sounds, so it holds its own group and the boundary stays between
two groups.

A merger co-highlights contributor and host in one group. An inserted sound
joins the group of its domain-selected source anchor. Structural separators
and stop signs belong to no group.

Each fold is stated per transformation family, not implemented as a single
adjacency guess. A consumer that wants to skip all silent participation may
ignore this view and use honest unit ownership from section 7 instead.

### 8.2 What makes a highlight view wrong

Coverage, not comparison, is the acceptance evidence. A missing sound and a
letter that never lights up are both failures, and only the first is caught by
counting sounds. Laws 32 to 33d state both directions, and they are checkable
over the whole corpus today without timestamps, a reciter, or legacy output.

Ranges are producer-derived; the consumer never coalesces Character IDs or
guesses a silent fold.

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
  columns: CellColumn[]
  sounds: CellSound[]

CellBoundary
  boundary_id
  columns: CellColumn[]
  sounds: CellSound[]
  bridges: CellBridge[]

CellColumn
  id
  role = letter | haraka | sukun | tanween | madd | stop_sign | gap
  text
  source_character_ids[]
  source_unit_ids[]
  placement = main | above | below
  attached_to_column_id
  change = unchanged | inserted | replaced | omitted | gap
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
  before_column_ids[]
  after_column_ids[]
  sound: CellSound
~~~

The public cell DTO is nested in render order so a website can render it
without rebuilding lookup maps. IDs remain only where alignment or a bridge
crosses nested ownership. A private normalized index may exist inside the
package.

There is no grouping level between a word and its columns. A column carries
its own attachment (placement plus attached_to_column_id) and its own sound
participation, and CellSound.column_ids carries the alignment, so a group would
only restate what those already say. A renderer that wants a box around a
letter and its marks draws it from attachment, which the producer supplies;
it does not infer one.

CellBoundary orders every boundary-owned column at that exact boundary.

### 9.2 Normative tokenization and alignment

- The whole word is the outer visible cell.
- Columns follow units. Every LetterUnit of the included words gets exactly
  one column, and no scalar that 7.2 folded into a unit gets one, so the
  column set is decided by tokenization rather than by a second list here.
- A role=letter unit takes a main column: role=letter when the canon reads it
  as a consonant, role=madd when it reads it as a long-vowel carrier. Full
  alif, waw and yaa carriers, small waw and yaa, and the dagger alif all take
  role=madd on that test; the mini noon of 21:88 takes role=letter.
- Haraka, sukun, and tanween take separate smaller columns. Above/below
  placement and attached_to_column_id identify the exact main column they ride;
  attachment is stated, never guessed from adjacency.
- A unit that pairs with the base letter it rides for the same sound takes a
  smaller column with that placement and attached_to_column_id rather than a
  main one. The mini seen of a seen/saad khilaf is the only Hafs case: it and the saad it rides are a
  pair, the resolved variant sounds one and silences the other, and both carry
  the variant_id and variant_choice that decided it.
- Shadda, maddah, the silence mark, the pausal zero, imala, ishmam, tashil,
  and a tatweel seat are composed directly into their main column text. They
  never open their own columns, and the rules placed on them underline the
  main column by law 23a.
- Long-vowel quality and carrier may occupy separate columns. One CellSound
  spans both.
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
- Every internal CellBoundary carries one role=stop_sign column. Its text is
  the exact written sign when the boundary has one and empty when it does not,
  so a consumer renders the pause control from the column and never reads a
  sign back out of word text. The column owns no sound. A frontend paints the
  | | fallback for an empty one, and decides from Boundary.state whether to
  show, grey, or hide it -- which is what lets a stopped reading lift the sign
  out of the word box it is written inside.
- Iltiqa insertion is an ordered boundary-owned column between two CellWords.
- A genuine idgham or other merger uses CellBridge with the shared CellSound.
- CellBridge uses plural column endpoints because one merger can span the
  contributor's and the host's columns on each side.
- A merger's one CellSound lives inside its boundary's CellBridge, not
  again inside the host CellWord. It renders exactly once between the words;
  its column_ids still align the contributor and host columns for
  co-highlighting.
- Carrier-seat handling is settled by the producer. Frontends never inspect
  codepoints to repair the rows.

The producer does not publish a glyph choice. Open tanween follows from the
occurrence already on the tanween unit -- it is open under idgham, ikhfaa, and
iqlab and stacked otherwise -- and the iqlab meem follows the same way, whether
a script writes it as a mini meem beside the noon or splits a tanween into a
haraka plus a mini meem. Both are the script's own convention over facts the
result already states, so neither earns a field or a column role.

This is not the codepoint inference principle 2 forbids. A consumer must not
work out that a rule applies; here the producer has already said which rule
applies to which unit, and a font or script adapter is only choosing how to
draw it. Deciding tajweed is the producer's; drawing it is the renderer's.

### 9.3 Rules in cells

Rules on visible letters attach to CellColumn.rule_occurrence_ids. Rules on
sounds attach to CellSound.rule_occurrence_ids. Both are projections of the
source and core arrays, never an independent classification: a column takes
the placements that name its own source units, and a sound cell takes exactly
what its Sound already names. Laws 23a and 23b state both derivations, so the
cell builder has nothing left to decide and no reason to read a rule ID.

An inserted column has no source units, so it carries no rules of its own. It
always owns a sound, and its label comes from that CellSound. The dropped
kasra of an iltiqa and the connecting vowel of a hamzat wasl are labelled on
the phoneme row, not the letter row.

Multiple rules may coexist, including:

- madd_iwad with madd_tabii;
- ordinary madd_silah with madd_tabii;
- madd_silah with jaiz before a hamza opening the next word;
- pausal_alif with madd_tabii;
- waqf drops with the rule naming the resulting long vowel.

The website can give overlapping rules separate underline lanes or a compact
combined hover. It must not invent a semantic fold.

### 9.4 Selective serialization

In process, a CellView refers to IDs on its AnalysisResult. A standalone JSON
cell envelope includes every referenced word, boundary, sound, rule occurrence,
rule definition, merger, source unit, and source character.
The same closure rule applies to a standalone source or highlight envelope.

A core-only envelope contains no source-unit or source-character reference.
A source-only envelope contains no cell reference. Result-local IDs are
preserved across scopes.

A CellView covers the whole requested passage. Cells are not scoped to a
subset of a result's words, because a word is scoped by the request instead:
phonemize("2:255:9") already resolves that word with a leading start and a
trailing stop, so no cross-word merger exists to lose. Slicing a result after
its boundaries were resolved in context would invent a word whose merged sound
belongs to a neighbour that is no longer there.

Every envelope validator has mutation tests for missing, mistyped, duplicated,
wrong-kind, and contradictory references.

## 10. Native analysis laws

The implementation must enforce these before serialization. A law's number is
its identifier and is stable: a new law is inserted with a suffixed number
rather than renumbering the ones after it.

1. Source characters concatenate exactly to result.text().
2. Word text concatenates from its lexical source characters exactly.
3. N words have N + 1 boundaries, with one leading start and one trailing
   stop.
4. Boundary before/after are typed WordId or null, with exact
   leading/internal/trailing cardinality; word and boundary references are
   mutually consistent.
5. At an internal boundary, ordinary no-override/override resolves join/stop
   and authored sakt no-override/override resolves sakt/stop. Sakt is never treated as waqf,
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
15. Every scalar that occupies the vowel position, and every letter the rasm
    leaves out and writes small, has its own LetterUnit, whether or not it
    sounds in the resolved boundary state.
16. LetterUnit ranges reproduce exactly its character_ids, even when
    non-contiguous.
17. Every source sound has at most one owner; owned and presented sound arrays
    are disjoint.
18. A scalar that 7.2 folds into a unit creates no column of its own.
19. A unit with a silence reason has no owned or presented sounds. The reason
    is either a rule occurrence that resolves in this result and lists the
    unit among its effects, or the literal orthographic; never both, and never
    a free-text or invented cause.
20. Every lexical source character of an included word appears in exactly one
    column's source_character_ids, and columns are in render order. Every
    LetterUnit of an included word has exactly one column.
20a. Every internal boundary of an included passage has exactly one
    role=stop_sign column, which owns no sound.
21. Above/below attachment resolves to an exact main column in the same
    CellWord or CellBoundary.
21a. A riding column's attached_to_column_id is the column of the unit its
    written_on_unit_id names. Where that unit has no main column of its own,
    it is the main column of the unit owning the sound the rider qualifies.
    Attachment is never derived from adjacency.
22. Every core sound appears in exactly one CellSound, held by one
    CellWord, one CellBoundary, or one CellBridge.
23. A non-gap CellSound's columns are exactly the columns that own or present
    its sound. A gap CellSound is the only exception to that agreement.
23a. A column's rule_occurrence_ids are exactly the source RulePlacement
    occurrences whose unit_ids intersect that column's source_unit_ids. A
    column with no source units carries none.
23b. A CellSound's rule_occurrence_ids are exactly its Sound's
    rule_occurrence_ids.
23c. A column's silence is exactly the silence of its source unit where it has
    one, and null for an inserted, gap, or boundary-owned column. The cell
    builder decides no silence of its own.
24. A gap column has empty provenance, ownership, presentation, and silence,
    and exactly one valid unit/side anchor or boundary owner.
25. Every CellBridge resolves to one Merger, owns the same CellSound, and its
    endpoint columns are the MergerPlacement's contributor presenters and host
    owner. The bridged sound has no duplicate CellSound.
26. No iltiqa boundary column creates a CellBridge.
27. CellSound column references are ordered and nonempty, using an honest gap
    column where no source presenter exists.
28. Word columns, boundary columns, sound spans, and bridge endpoints are
    closed: every referenced ID exists in the selected CellView.
29. A transformed inserted column has no invented source character or unit and
    has a valid unit/side anchor or boundary owner.
30. A transformed replaced or omitted column retains exact source provenance;
    an omitted column retains source text.
31. A column's variant_id and variant_choice are either both null or match the
    resolved result selection and accompany an actual variant-dependent
    displayed state or sound participation.
32. Highlight groups refer only to source units and existing sounds; their
    ranges are ordered and non-overlapping.
33. A highlight view contains every sound exactly once.
33a. A highlight view contains every lexical source unit exactly once,
    and the union of its ranges equals the lexical span of result.text().
    Separator and stop-sign characters are the only exclusions.
33b. Every highlight group holds at least one sound and at least one unit that
    owns a sound. No group is silent-only, and no sound is orphaned from a
    sounding presenter.
33c. Every long-vowel sound has a madd unit in its own group, except the Allah
    dagger alif, hamza with fathatan, and muqattaat.
33d. A unit that owns a sound is alone in its group unless a merger, an
    insertion anchor, or a long vowel's carrier put another unit there. Ikhfaa,
    iqlab, and their shafawi counterparts therefore never fold across a
    boundary, because the nasalized unit still owns its sound.
33e. Every published ID array has one stated order and is deterministic across
    runs of the same request: sounds and columns in render order, occurrences
    in the order their rules fired, and every back-reference in the order of
    the array it points into.
34. Validators reject missing, duplicated, contradictory, and wrong-kind IDs
    even when the underlying integer value exists in another ID space.
35. Native tests pass when every legacy projection module is unavailable.
36. No public DTO field, role, change, placement, or state value is named for
    one riwayah, one script, or one site. A reading's vocabulary reaches a
    consumer only through the rule, variant, and extra-phoneme catalogues.

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
- tafkheem and tarqeeq read as a pair but are not symmetric, and the asymmetry
  is deliberate. tafkheem covers the isti'la letters, contextual raa, the lam
  of the divine name, and the nasal hum of an ikhfaa; tarqeeq covers raa alone,
  because every other letter's thinness is the absence of a rule rather than
  one. Each RuleDefinition summary states its own scope so a legend does not
  imply the pair covers one axis.
- madd_lazim is one rule over kalimi and harfi, muthaqqal and mukhaffaf, and
  the leen-lazim case. The four subtypes and leen-lazim are a teaching layer
  the producer does not publish; a consumer that teaches them derives them from
  the unit and the following sakin.
- Remove orthographic_silence from Rule. It is a source-unit state, not a
  recitation rule occurrence.

### 11.2 Madd badal, iwad, and silah

madd_badal remains first-class:

- ordinary badal emits madd_badal alone. It names the same two harakat
  madd_tabii names, so the two are mutually exclusive and never co-occur;
- if another cause determines a contextual length, badal remains present and
  the contextual madd names the length;
- no sughra/kubra teaching layer is added.

A consumer that does not teach badal separately may fold madd_badal into
madd_tabii for presentation. The producer does not fold it, because the two
name different causes of the same length.

madd_iwad names the fathatan-to-long-aa transformation and co-occurs with
madd_tabii for the resulting natural length.

There is one madd_silah:

- ordinary silah emits madd_silah plus madd_tabii;
- before a hamza opening the next word it emits madd_silah plus
  madd_jaiz_munfasil, without madd_tabii;
- at waqf it emits no madd_silah and uses waqf_silah_drop.

Silah is never muttasil. The lengthened vowel belongs to the pronoun haa and
the qualifying hamza opens the following word, so the meeting is always across
a boundary. Only madd_jaiz_munfasil can accompany it.

No silah_sughra or silah_kubra identifier is introduced.

### 11.3 Hamzat-wasl and ibdal

hamza_wasl_silent names the wasl outcome in which the prosthetic consonant and
its helping vowel are not pronounced.

At ibtidaa before a quiescent lexical hamza:

- the appropriate hamza_wasl_kasra or hamza_wasl_damma occurrence names the
  starting quality;
- ibdal_hamza targets the following lexical hamza that is replaced/silenced;
- the starting vowel is lengthened with the matching quality, and that length
  is madd_badal: a hamza followed by a long vowel of its own quality is exactly
  what badal names, so the occurrence pair is ibdal_hamza plus madd_badal,
  without madd_tabii, under the ordinary badal rule of 11.2;
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
| Performed silah suppressed | waqf_diacritic_drop on the haa's written haraka + waqf_silah_drop; no madd_silah |
| Compatible final waw/yaa becoming long | waqf_diacritic_drop + madd_tabii |
| Aatani hadhf at 27:36:8 | yaa_aatani_waqf variant omission plus waqf_diacritic_drop on each actually omitted vowel mark, and madd_arid_lissukun on the long aa the newly quiescent noon now closes; no glide rule |
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

waqf_silah_drop is scoped the same way: it names only the loss of the small
waw or yaa that carried the length. The haa's own written haraka is an omitted
haraka like any other and takes its own waqf_diacritic_drop, so both dropped
scalars of `تَأْخُذُهُۥ` are separately placeable.

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

### 12.1 One shape, many readings

The DTO shape is riwayah-independent. Words, boundaries, sounds, letter units,
columns, occurrences, mergers, and highlight groups describe any reading; only
the vocabulary filling them is a riwayah's own, and it is reached through
tajweed_rules(riwayah), available_variants(riwayah), and
available_extra_phonemes(riwayah). Adding Warsh adds rule IDs, variant IDs,
and script inventories. It adds no public field, no role, and no column kind.

Law 36 states this, and it is what keeps a Hafs peculiarity out of the shape.
The mini seen of a seen/saad khilaf is the case that tested it: Warsh does not
write that codepoint at all, so a role named for it would have been a Hafs word
in a shared vocabulary. It does not need one. It is a letter that the resolved
variant may or may not sound, which the column already says with placement,
silence, variant_id, and variant_choice.

This document otherwise describes Hafs, because Hafs is what ships. The 44
rule IDs, the variant catalogue, and the QPC font gate of section 17 are that
reading's content, not the contract's shape.

## 13. Ownership across repositories

### 13.1 Phonemizer owns

- source characters and letter-unit tokenization;
- rule inventory, names, short hover summaries, and occurrences;
- rules on visible units and sounds;
- true sound ownership, shared presentation, and silence reasons;
- resolved boundary behavior and stop signs;
- mergers and boundary insertions;
- source/transformed cell columns, attachment, and alignment;
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
iqlab rows, and iltiqa placement. The domain decisions move to the
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
| ordinary madd_badal | madd_tabii |
| madd_badal + contextual madd | contextual madd only; suppress badal |
| ordinary madd_silah + madd_tabii | madd_tabii |
| madd_silah + madd_jaiz_munfasil | exact madd_jaiz_munfasil v11 tag, without duplicate tabii |
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
- source unit tokenization and cell columns;
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

Two of these are decided mechanically rather than by review. Category 1 is
whatever compares equal. Every emitted tag, CellRole and CellStatus is asserted
to be a member of TajweedRule, CellRole and CellStatus imported from the pinned
qua_shared commit, so an invalid value fails the gate outright and can never be
filed as category 2. Categories 2 to 5 each require the row of section 14 or
14.1 that predicted them, named in the classification; a difference no row
predicts is category 6 by default, which is what stops category 2 absorbing
anything that merely looks like a translation.

Frozen old output is evidence, not expected truth. Snapshot regeneration alone
cannot approve categories 2 through 5.

### 14.1 Cell differences already known and decided

Four cell differences are settled in advance, measured against a full v11
reciter at phonemizer_version 2.13. Each is category 3, and the adapter
produces the v11 shape from the native one rather than the native model
adopting it:

| v11 | Native | Why |
| --- | --- | --- |
| The maddah takes its own madd cell and carries the rule | The maddah folds into the letter it marks, and the rule lands on that letter | A bar over a mark claims a length the mark does not own. The letter is what is read long |
| The pausal zero takes a madd cell, as a length carrier | It folds, and is a silence sign | It writes an absence: the alif it sits on is silent when joined to. A zero is not a carrier |
| The mini seen of a seen/saad khilaf composes into the saad | It is a unit with its own column, paired with the saad | One of the two is read and the other is not. Composing them cannot show which, and cannot carry the variant that decides it |
| A sukun is status=dropped | A sukun is an ordinary present unit that owns no sound | Nothing is dropped. The mark is written and read as the absence of a vowel, which is not the same as a letter the reading discards |

The 121,746 v11 cells carrying a share_group are the same relation section 8
publishes as highlight groups, and its two commonest shapes -- a haraka with
its carrier, and a haraka with two -- are what laws 33a to 33d cover.


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
| phonemize/names.py | Rewrite as the RuleDefinition, VariantDefinition, and ExtraPhonemeDefinition catalogue owner |
| phonemize/session.py | Keep; it is the resolved request the native flow starts from |
| phonemize/request.py | Keep |
| phonemize/span.py | Keep; refresh its overlap rationale once fakk_idgham is gone |
| phonemize/boundaries.py | Keep; it is the source of Boundary state |
| phonemize/runtime.py | Keep |
| phonemize/__init__.py | Rewrite as the facade over the native result |

A row reading Delete may become Retain private under 15.1 if its callers are
gone and nothing succeeds it; the manifest check of this section applies only
to rows still marked Delete, so a deliberately retained private module is not
indistinguishable from a missed one.

The dispositions are binding. The filenames and the caller counts below are
measured at the target baseline; re-measure them at the implementation branch
before acting, because a caller added since then changes the order rather than
the outcome.

### 15.1 A module leaves when its last caller does

Deletion is caller-driven, one module at a time, and never a single cutover
commit. A module on this table is removed in the change that retires its last
caller, and until then it stays and stays private. A module whose callers are
all gone but which has no successor is made private and retargeted rather than
deleted.

This matters because the callers are not only the public result. Counted at
the target baseline:

| Caller | Delete-list modules it uses |
| --- | --- |
| tests/support/reading.py | edges, nodes, assemble, document, labels, pairing, legacy_views |
| tools/parity.py, tools/cross_parity.py, tools/snapshot.py | legacy_views |
| tools/benchmark.py | assemble, labels, document, schema |
| tests/laws/test_pairing.py, test_respelling.py, test_recited_text.py, test_teaching_labels.py | the module each is named for |
| tests/laws/test_anchored_projection.py, test_parity_floor.py, test_continuous_assembly.py, test_madd_tabii.py, test_minimal_pairs.py, test_script_agreement.py | legacy_views, though none is named for it |

tests/support/reading.py is the harness 36 of the 67 test files run through.
legacy_views backs the cross-script and regression corpus gates, the suite gate
through six law tests, and the structure gate itself, because structure_lint
import-smokes every committed tool and tools/snapshot.py is one of them. A
cutover that deletes these modules in one commit takes the rule suite and three
gates down together, and nothing is left to prove the cutover did no harm.

So the order is fixed: retarget the harness onto the native result first, then
the gate tools, then every test that reaches a delete-list module -- whether or
not it is named for one -- is either rewritten against a native law or removed
with that module in the same change.
Only then does the module go. Every step keeps all eight gates green, which is
what makes the previous commit a real rollback rather than a nominal one.

The one permitted private flow is:

~~~text
(Session, resolved request, Alphabet) -> AnalysisFacts
        -> core / source / highlights / cells
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
- an inline message for a reference that does not parse or falls outside the
  Qur'an, leaving the previous result on screen;
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
  letter column.
- Shadda and silence marks stay in the main cell.
- Genuine cross-word mergers retain the in-between bridge presentation.
- Iltiqa boundary insertion appears between words without masquerading as a
  merger.
- Rule underlines attach to the exact producer-supplied letter or sound cell.
- Every cell has a content-based minimum inline size large enough for its
  Arabic or phoneme content. It never shrinks until text overflows the box.
- A column whose sound list is far longer than one -- the alif of `الٓمٓ` says
  five -- stretches its phoneme row under one letter rather than borrowing the
  columns beside it.
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
| POST /api/analyse | Source text, phonemes, boundaries, transformed cells, occurring rules. 400 with a typed reason for an unparseable or out-of-range reference |
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
- Split the Onset.GLIDE branch out of the generic pausal-sukun occurrence and
  re-express it as the yaa_aatani_waqf variant outcome. No waqf_glide_drop rule
  is added, and the abstraction is privatized: its only shipped use is the one
  ledger row for 27:36:8.
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
- Enumerate v11 cell behaviours as candidate cases. Each one is closed against
  a native law or a docs/hafs/research citation before its fixture is written;
  a v11 behaviour with no native justification is recorded in section 21 as
  open, not ported. Section 14.1 lists the four already decided against v11.
- Fixture the iqlab and open-tanween rows as facts about units and
  occurrences, with no glyph choice in the result.
- Fixture every folded mark against its main column, and every unit role
  against its column.
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
- Carry each silence reason from the occurrence that caused it, and the
  literal orthographic where no rule did.
- Implement highlight groups with the three fold directions of 8.1.
- Run laws 32 to 33d over the whole corpus in every boundary state. The units
  they name are the folds nobody has decided yet; each one is closed against a
  native law or a docs/hafs/research citation, not against legacy output.

Exit: continuous source-text highlighting needs only sound timing IDs, and
laws 32 to 33d hold over the full corpus with no exemption list.

### Phase 5: implement cells

- Build source and transformed CellViews from native facts.
- Add whole-word columns, attached marks, sound spans, omission/replacement
  state, boundary insertion columns, and merger bridges.
- Prohibit rule-ID and codepoint reconstruction in the cell builder.

Exit: the QUA Inspector and website can render rows without domain repairs.

### Phase 6: schema, transport, and compatibility adapter

- Freeze typed JSON schema for the native result and each selective view.
- Implement a shadow thin v11 adapter in the QUA integration owner while the
  old QUA path remains available only in its frozen comparison environment.
- Run the 114-shard classified comparison between those separate paths.
- Add exact wheel/API export tests.

Exit: native semantics and frozen v11 wire compatibility are separately green.

### Phase 7: retire the old projection stack

Not one commit. Section 15.1 is the order, and every step lands green:

- Retarget tests/support/reading.py onto the native result.
- Retarget tools/parity.py, cross_parity.py, snapshot.py, and benchmark.py.
- For each remaining module, rewrite the tests named for it against a native
  law or remove them in the same change that removes it, then remove it.
- Make private anything that has no successor and no caller left.
- Update README and public API documentation to the consumer contract.
- Build the release-candidate wheel once the table is empty.
- Prove old public types and modules are absent.
- Re-run all eight gates plus native, schema, export, wheel-manifest, and the
  114-shard gate against that exact wheel.

Exit: there is one public architecture, and every commit on the way to it had
a working test suite.

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

Every RuleDefinition returned by tajweed_rules("hafs") appears in at least one
hard-case fixture. A rule with no fixture fails the gate, which is what keeps
this list honest as the inventory changes rather than freezing today's 29.

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
- full corpus highlight coverage in every boundary state: laws 32 to 33d with
  no exempted unit;
- one fixture per fold direction of 8.1, including the ikhfaa and iqlab cases
  that must not fold;
- iltiqa boundary insertion without Merger;
- all transformed insertion/replacement/omission families;
- all thirty muqattaat openings, over their fourteen distinct skeletons: one
  letter unit owning several sounds, with no extension splitting inside a
  spelled-out name;
- no overflowing representative Arabic or phoneme cell;
(A ban on rule-ID and codepoint branching in consumers is not checkable from
this repository. It is an exit criterion of phases 8 and 9 instead: an
Inspector lint rejecting a rule-ID comparison outside its renderer registry,
and the qua-sdk equivalent.)

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
- an invalid and an out-of-range reference both render the inline message and
  leave the previous result standing;
- exact package/schema version match;
- PyPI latest and GitHub links.

## 21. Open decisions register

These do not block Phase 1:

| Decision | Default direction | Closing evidence |
| --- | --- | --- |
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
