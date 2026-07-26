# Spine A — The canonical layer is a phonological skeleton, not a normalized orthography

Position: scripts do not converge on a cleaned-up letter sequence; they converge
on a stream of **canonical units** — consonant events with fused vocalization —
that is the recitation's skeleton. Carriers, otiose letters, and every mark are
demoted to the script layer and connected to that skeleton by one typed
attribution relation. Everything downstream (rules, segments, occurrences,
recited writing) addresses only the skeleton. The cost, stated up front: the
per-script canonicalizers become the thickest, most linguistically loaded code
in the system, and no grapheme-facing feature can ever read text directly — it
must traverse the attribution index.

## Object graph

```
L0  WrittenWord(script)         one per (word, script)
      Grapheme(scalar, offset, class, ortho_role, link: FacetRef|None)
        │  AttachmentIndex: (UnitAddr, Facet) ⇄ graphemes   [per script]
L1  CanonicalWord               one per word, script-independent, boundary-independent
      CanonicalUnit(addr, letter, vocalization, geminate, features)
      UnitAddr = (surah, ayah, word, unit_index)
L2  Realization                 one per request (BoundaryPlan applied)
      Occurrence(rule, participants: [(UnitAddr, Role)])
      Segment(kind, contributions: [(UnitAddr, Facet, ContribRole)],
              origin: InsertionOrigin|None, anchor, produced_by: OccurrenceId|None)
      Silence(UnitAddr, Facet, reason)
L3  Render                      pure table: segment feature bundle → token
```

A `RiwayahProfile` bundles: one `ScriptFrontEnd` per supported script (scalar
inventory + canonicalizer), the riwayah **location table**, the ordered rule
family registry, the variant catalog, and the render inventory. The engine
takes a profile and is riwayah-blind — this replaces the unconditional
`from .hafs import …` in `engine.py`.

## 1. Layers and addressing

Four layers, as above. The load-bearing decision is what a `CanonicalUnit` is:

- `letter: CanonicalLetter` — closed enum, the ~30 recitable letters plus
  `HAMZA_WASL` and `TAA_MARBUTA` (both behave distinctly, so both are letters).
- `vocalization: Vocalization` — closed enum fusing quality and length:
  `A | U | I | AA | UU | II | SAKIN | TANWIN_A | TANWIN_U | TANWIN_I | NONE`
  (`NONE` only for hamzat al-waṣl, whose start vowel is grammar-derived at L2).
- `geminate: bool`, `features: frozenset[UnitFeature]` — closed:
  `SILAH`, `LONG_AT_WAQF_ONLY` (the seven alifs), `SAKT_AFTER`, `IMALA`,
  `TASHIL`, `ISHMAM`, plus the madd-override features. Features are injected
  during canonicalization from script marks *or* the location table (§3).

What is **not** a unit: the alif of `قَالَ`, the maqṣūra seat of `عَلَىٰ`, the
otiose wāw-alif of `قَالُوا۟`, hamza seats, the tanwīn's companion alif. They
never sound as themselves in any boundary state, so they are L0 graphemes with
an `ortho_role` (closed: `BASE`, `VOWEL_SIGN`, `LENGTH_CARRIER`, `SEAT`,
`OTIOSE`, `VALIDATOR`) and, where relevant, a `link` to a unit **facet**.
Criterion for unit-hood: *can it produce sound at its own position in at least
one boundary state or reading?* Hamzat al-waṣl sounds at ibtidāʾ → unit. The
seven-alifs alif sounds at waqf → the length lives as `LONG_AT_WAQF_ONLY` on
the preceding unit's vowel, and the written alif is its `LENGTH_CARRIER`.

Addressing: `UnitAddr = location + unit_index` over the canonical stream. A
reference survives a script change because both scripts must produce the
**byte-identical unit stream** — this is not a type guarantee but a corpus-wide
CI invariant (77,433 words, both front-ends, streams compared). Grapheme
references exist only inside the per-script `AttachmentIndex`; no rule,
occurrence, exception, or projection ever holds one. Muqaṭṭaʿāt expand at
canonicalization (`الٓمٓ` → the units of *ʾalif lām mīm*, one grapheme linked
to many units), so unit addressing already covers the current `2:1:1:0`
sub-word hack, and the expanded final name meets the next word through the
ordinary cross-word mechanism — the `allow_forward_rules` blanket (and with it
the 27:1 ikhfāʾ defect) has no home to live in.

## 2. Attribution — one relation, two indexes

One relation: **Contribution** `(segment ⇄ (UnitAddr, Facet, ContribRole))`,
where `Facet ∈ {ONSET, VOWEL}` and `ContribRole` is closed:
`PRIMARY | MERGED_SOURCE | SUBSTITUTED | CONDITIONER`. Its complement is
**Silence** `(UnitAddr, Facet, reason)` with a closed `SilenceReason`
(`HAMZA_WASL_JOINED`, `SILAH_AT_WAQF`, `TANWIN_DROPPED_AT_WAQF`,
`FINAL_VOWEL_AT_WAQF`, …). The four required shapes:

- **Joint ownership.** `/aː/` in `قَالَ` is one Vowel segment contributing to
  the qāf unit (whose vocalization is `AA`) at facet `VOWEL`. Grapheme side,
  per script: fatha (`VOWEL_SIGN`) and alif (`LENGTH_CARRIER`) are both
  attached to that same `(unit, VOWEL)` facet. Joint ownership is the
  *composition* segment→facet→graphemes; no special case.
- **Cross-word merger.** One geminated Consonant segment with two
  contributions: `(wordA.unit_n, ONSET, MERGED_SOURCE)` and
  `(wordB.unit_0, ONSET, PRIMARY)` (§Demo 1).
- **Insertion.** A segment with zero contributions, an
  `origin: InsertionOrigin` (closed: `HAMZA_WASL_START_VOWEL`, `ILTIQA_KASRA`,
  `ILTIQA_FATHA`, `MADD_IWAD`, `ALLAH_ALIF`, `QALQALA_RELEASE`) and an
  `anchor: (UnitAddr, BEFORE|AFTER)` so recited-writing knows where to show it.
  The 3:1→3:2 fatha (evidence §4.2) is `ILTIQA_FATHA` — the third flavour of
  helping vowel becomes the third enum member of one mechanism, and the
  Allah-lām colour rule then sees a vowel where today it sees a consonant.
- **Deletion with a reason.** A facet with no contribution must carry a
  Silence record. Completeness invariant, engine-asserted: *every facet of
  every unit either contributes to ≥1 segment or is silenced with a reason;
  every segment has ≥1 contribution or an origin.* This is domain-facts
  invariants 3–4 made structural, and it is exactly what
  `owner.segments.pop(index)` and `following.segments = […]` destroy today.

Iqlāb/ikhfāʾ keep rule identity through `produced_by` (§4) while the Nasal
segment contributes to the nūn's unit with role `SUBSTITUTED` — the current
`Nasal`-collapses-three-rules defect dissolves without adding segment kinds.

## 3. The script boundary

The contract of a `ScriptFrontEnd`, per (riwayah, script):

1. **Total scalar classification.** Every scalar in the source is declared:
   letter (with precomposed decompositions — `أ` = hamza on alif seat), vowel
   sign, length mark, gemination, annotation, stop sign (mapped into the shared
   `StopSign` enum), or structural. Unknown scalar = parse error. No mark may
   be silently discarded — the current `structural:` dumping ground for `ۜ ۣ ۫`
   is the anti-pattern; every annotation must resolve to `VALIDATOR` of a
   named fact or be explicitly declared decorative.
2. **Canonicalization** to the unit stream, resolving what the script
   under-specifies *from three sources in fixed priority*: derivable
   orthographic convention → riwayah location table → error. A present script
   mark never drives; it **validates** — canonicalization cross-checks it
   against the derived/table fact and a mismatch is a build-time error.
3. **The equality invariant**: both front-ends produce identical unit streams
   corpus-wide. Phoneme identity then follows for free, because nothing below
   L1 reads L0.

What each source under-specifies, and who supplies the fact:

| Missing in script | Supplied by | Validated by |
|---|---|---|
| Uthmani bare consonant (no sukūn) | convention: bare = `SAKIN` | IndoPak's explicit `ْ` |
| Uthmani unmarked iqlāb | nothing needed — rule-derived at L2 | IndoPak `ۢ`/`ۭ` (546 sites) |
| IndoPak short fatha under dagger (`سُبْحٰنَهٗ`) | convention: dagger alone = `AA` | Uthmani's explicit fatha |
| IndoPak seven alifs (66 sites), ishmām 12:11, typed imāla/tashīl | location table | Uthmani's `۠ ۫ ۪ ۬` |
| Both: sakt at 2 of 5 sites (IndoPak), U+06DC ambiguity (Uthmani) | location table (`SAKT_AFTER` at the 5 sites; seen-variant at the 3 khilaf sites) | whichever marks exist |
| Uthmani 2:72 ornamental construct | script-scoped resolution entry (`riwayah × script` key) | IndoPak's plain hamza |

This kills the §2 accident: `noon_tanween.py:17`'s bare-vs-sukūn test cannot
be written, because by the time rules run the distinction no longer exists.
The 126 explicit-sukūn assimilation candidates are then handled by *named*
rules on canonical state: iẓhār muṭlaq (same-word nūn + yāʾ/wāw condition —
a real condition of the noon family, not a glyph shortcut) and `SAKT_AFTER`
blocking at 75:27/83:14.

## 4. Rule occurrences

`Occurrence(id, rule: Rule, participants: tuple[(UnitAddr, ParticipantRole)])`
where `Rule` is one closed enum covering every named decision — including the
"default" outcomes (`IZHAR_HALQI`, `IZHAR_MUTLAQ`, `IZHAR_SHAFAWI`,
`LAM_QAMARIYYAH`-is-implicit-no, see below) and the four idghām families as
distinct members (`MUTAMATHILAYN`, `MUTAQARIBAYN`, `MUTAJANISAYN_KAMIL`,
`MUTAJANISAYN_NAQIS`, `LAM_SHAMSIYYAH`), un-collapsing `idgham.py:28`.
`ParticipantRole` is closed: `TRIGGER | TARGET | BLOCKER | CONDITIONER`.

The structural guarantee: **occurrences are the only path to affected
segments.** A rule family returns an occurrence; the materializer builds the
segments *from* the occurrence's template and stamps them `produced_by`; the
contribution edges are emitted in the same act. A tajweed projection reads
occurrences and follows `produced_by` to segments; a phoneme projection reads
segments and follows `produced_by` back. There is no second derivation to
disagree — the current frozen-baseline distortion where muqaṭṭaʿāt tajweed
was hand-authored YAML while phonemes came from the pipeline becomes
unrepresentable. Trivial letters (plain bāʾ + fatha) have no occurrence and
`produced_by = None`; families that always decide (noon/tanween) always emit
one, so "no occurrence" never means "rule considered and defaulted".

## 5. Rule execution

Rules are pure functions over `(canonical stream, BoundaryPlan, earlier
decisions)` returning occurrences plus **claims** — `(UnitAddr, Facet) →
occurrence`. Nothing mutates a neighbour: idghām *claims* the next word's
first onset; the meem family claims the following bāʾ's nasality; the
materializer, which runs once after all phases, consults claims when emitting
each facet. At most one claim per (facet, phase) — a second claim raises,
turning the domain's mutual-exclusivity invariant (domain-facts §8.2) into an
assertion instead of an accident of execution order.

Three phases, mirroring domain-facts invariant 8:

- **A. Existence** — boundary transforms (waqf ending repairs, ibtidāʾ
  repairs), hamzat al-waṣl, noon/tanween family, meem family, generic idghām
  families, muqaṭṭaʿāt junctions, insertions. Decides *which* sounds exist.
- **B. Length** — madd classification, reading the phase-A "sound plan"
  (units + claims), not materialized segments: "is the next sound a hamza / a
  permanent sukūn / a ghunnah" is answerable from units and A-claims.
- **C. Colour** — tafkhīm (isti'lāʾ spread, rāʾ, Allah-lām, ghunnah colour),
  qalqala. Colour decisions decorate pending emissions.

Every family is the same shape — `decide(window) → occurrences` registered in
an ordered phase list on the profile. Rāʾ tafkhīm and Allah-lām tafkhīm are
two same-shaped entries in phase C: the Allah-lām's `if`-branch inside
`apply.py::_pronounce_letter` and rāʾ's private module both dissolve into the
registry. Riwayah-specific families (Warsh taqlīl, naql) are additional
registry entries, not engine edits.

## 6. Recited writing

A projection, not a rebuild: walk the chosen script's grapheme stream in
written order; for each grapheme, resolve through the AttachmentIndex to its
facet and ask the realization: contributed → emit recited form; silenced →
apply the *silent* toggle (show / hide / mark, with the `SilenceReason`
available for annotation); merged (`MERGED_SOURCE`) → the *merged* toggle
(show as written / show doubled target / hide). Insertions interleave by
anchor: `(UnitAddr, AFTER)` maps through the index to a position between
graphemes. Toggles:

- **basis**: source | recited (recited applies the facet resolution above);
- **silent**: shown | hidden | marked;
- **inserted**: shown | hidden;
- **form**: compact | expanded (expanded spells muqaṭṭaʿāt names and the
  tanwīn's nūn using unit provenance — one grapheme fanning out to many units
  is already stored).

Every toggle is a filter over stored relations; if any combination requires
recomputation, the completeness invariant of §2 was violated — this projection
is the model's acceptance test.

## 7. Variant selection (brief)

Two homes, split by one criterion: *does the choice alter canonical facts?*
Token khilaf (`m̃` vs `ŋ`) does not — it is a render-inventory selection at L3,
restoring the deleted overrides. Lexical khilaf does — the profile's
**variant catalog** holds `(UnitAddr, dimension, options, default)` (the 3
seen/ṣād sites), a `ReadingChoice` given at engine construction selects, and
the canonicalizer emits the chosen `CanonicalLetter` with provenance
`CHOSEN_VARIANT`. Emphasis, vowel colour, and the rāʾ look-back follow
automatically because they never see anything but the canonical letter.
Script marks at those sites validate that a catalog entry exists (§3.2).

## 8. Exceptions (brief)

A justified exception is a **fact in domain vocabulary consumed by a named
rule family as input**, keyed by
`(riwayah, script | *, location-or-UnitAddr, boundary-context)` — `script`
non-`*` only for orthography-resolution entries like 2:72. A patch is
recognizable by any of: expressed in output vocabulary (segments, phonemes —
today's `hafs.py` writes `Vowel(...)` lists directly), keyed by glyph
occurrence ("first letter matching HAMZA" — `hafs.py:_replace`), or named
after a site's symptom (`SECOND_HAMZA` for what is the 41:44 tashīl). Typed
replacements: `started_ituuni` becomes a hamza-waṣl-family start-repair fact;
`second_hamza` becomes the `TASHIL` unit feature; madd overrides become madd
features on units.

## Demonstrations (what is stored)

**1. Cross-word idghām — 2:5:4 `مِّن` → 2:5:5 `رَّبِّهِمْ`.** L1:
`…, A.2 = (NOON, SAKIN)`, `B.0 = (RA, A, geminate)`. In waṣl:
`Occurrence(IDGHAM_BILA_GHUNNAH, [(A.2, TRIGGER), (B.0, TARGET)])` claims both
onsets; one segment `Consonant(RA, geminated)` with contributions
`[(A.2, ONSET, MERGED_SOURCE), (B.0, ONSET, PRIMARY)]`. The nūn is not
"deleted": its sound is jointly the geminate. At waqf on A the family emits
`IZHAR` instead and B.0's written shadda is not realized (ibtidāʾ drop).
Uthmani writes A.2 bare; IndoPak writes explicit sukūn — same stored graph.

**2. One segment, three writings — the long ā.** Stored identically in all
cases: a consonant unit with vocalization `AA`, two segments (the consonant
and `aː`), with `aː → (unit, VOWEL)`.
`قَالَ`: attached graphemes fatha (`VOWEL_SIGN`) + alif (`LENGTH_CARRIER`).
Uthmani 2:5:2 `عَلَىٰ`: fatha + maqṣūra (`SEAT`) + dagger (`LENGTH_MARK`).
IndoPak `عَلٰي`: dagger alone (supplies quality *and* length) + otiose yāʾ.
Different attachment rows per script; identical L1 and L2 bytes.

**3. Silent grapheme, reason recoverable — two tiers.** Orthographic: the wāw
of 2:5:6 `وَأُو۟لَـٰٓئِكَ` is a grapheme with `ortho_role = OTIOSE`,
`link = None`; Uthmani's `۟` is its `VALIDATOR`; it is not a unit, so no
boundary state can ever sound it. Phonological: hamzat al-waṣl in `ٱهْدِنَا`
mid-verse *is* a unit; the realization stores
`Silence(unit, ONSET, HAMZA_WASL_JOINED)` in waṣl and contributions plus an
inserted start vowel at ibtidāʾ. The recited-writing silent toggle reads the
role in tier one and the reason in tier two.

**4. Same word, both scripts — 2:116:5 `سُبْحَـٰنَهُۥ` / `سُبْحٰنَهٗ`.**
Converged L1: `s(U) b(SAKIN) ḥ(AA) n(A) h(U→UU, +SILAH)`. Contributions:
Uthmani writes the ḥāʾ's fatha explicitly and splits silah across damma +
small wāw `ۥ`; IndoPak writes no fatha (dagger alone ⇒ `AA` by convention)
and one mark `ٗ` carrying damma + silah + length. Each script under-specifies
something the other writes; the canonicalizers supply the conventions; no
location-table entry is needed here. Where one would be: the seven alifs —
IndoPak contributes nothing at all 66 sites, the table supplies
`LONG_AT_WAQF_ONLY`, Uthmani's `۠` validates it.

## Costs, and what would change my mind

1. **Thick canonicalizers.** The hardest logic (seat resolution, dagger
   conventions, silah folding, precomposed hamza decomposition) moves into
   per-script front-end code. That code is riwayah × script specific and
   linguistically loaded — the opposite of a thin alias map. I accept this:
   the complexity exists either way, and here it is quarantined behind a
   corpus-tested equality invariant instead of leaking into rules.
2. **Indirection tax.** No feature may read `word.text`; inspectors, recited
   writing, and debugging all traverse AttachmentIndex. Tooling must be built
   early or development slows.
3. **Claim/materialize machinery** is heavier than direct emission for the
   ~80% of letters that are trivial.
4. **Equality is tested, not typed.** A canonicalizer bug produces divergent
   streams caught only by the corpus fixture — the type system cannot prove
   script-agnosticism.

Evidence that would settle open points: a spike proving unit streams align at
all 77,433 words under the unit-hood criterion (I verified the pattern at
sampled words only); confirmation that IndoPak writes explicit sukūn on *all*
cross-word assimilation sources; a domain citation for the يسٓ/نٓ wajh
question (flagged unverified in the evidence pack).

**Phase ordering:** (1) Uthmani front-end + L1, freeze a canonical-stream
snapshot; (2) IndoPak front-end to the equality invariant; (3) L2 engine to
phoneme parity against `tests/snapshots/phonemes/`; (4) occurrences +
recited-writing projection, validated against `research/legacy-baselines/` as
an information-coverage check.
