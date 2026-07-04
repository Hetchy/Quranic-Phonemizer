# ADR-001 (v2): Canonical internal model — two spines, typed segments, tajweed first-class

Status: **proposed** (Epic 3a design ADR). v2 is a from-scratch design: it does
NOT work backwards from today's classes or output contracts. A new public
contract may replace the six current views (version bump accepted).

Companion: `docs/domain-facts.md` — the domain ground truth this model encodes.
Reviewed by three independent design reviews (domain-modeling, adversarial
edge-case stress test over 16 hard cases, simplicity/API); their forced
decisions are folded in and credited inline as [D]/[A]/[S].

---

## 1. The core decision: two spines joined by `spelling`

The domain facts describe **two independent sequences with a many-to-many
alignment**, not one tree:

- **Written spine**: the text as a flat list of `Grapheme`s (every codepoint
  that appears, classified by the riwaya's script data). Pure orthography —
  no phonology, no status, no phonemes. Silent letters stay here untouched
  (domain-facts §8.3: every grapheme is written whether or not it sounds).
- **Sound spine**: the recitation as a flat, **utterance-level** list of typed
  `Segment`s (Consonant / Vowel) — the articulation events. Flat and global,
  not nested under words, because sounds cross words (cross-word idgham
  today; Warsh naql moves a vowel spelled in word N+1 to sound in word N —
  retrofitting a global stream later would be expensive [A]).

The alignment is **one field**: `Segment.spelling: tuple[grapheme_id, ...]`
(0..n). This single relation dissolves the entire hard-case ledger with no
auxiliary structures:

| Domain fact | Representation |
|---|---|
| long vowel jointly owned by haraka + carrier | one `Vowel`, `spelling=(haraka, carrier)` |
| cross-word idgham geminate | one `Consonant`, `spelling` spanning two words |
| idgham shafawi "both meems sound" | same — both meems in one segment's spelling |
| inserted sound (hamza-wasl vowel, iltiqaa kasra, 'iwad alef, Allah *aa*) | segment with `spelling=()` |
| silent grapheme (idgham source, hamza wasl, shamsiyah lam, otiose alef) | grapheme referenced by **no** segment |
| one grapheme → many sounds (muqatta'a صٓ → *ṣaad*) | many segments, each `spelling=(صٓ,)` |

Consequently the v1 model's `Unit`, `role`, `status`, `share_group`,
`MaddInfo`, `written_delta`, and the `Phoneme` class are **all deleted** [S].
Everything they stored is either a link (`spelling`) or an annotation
(`RuleApplication`, §3), and therefore cannot drift between views:

- *silent* = grapheme not in any spelling (attribution = the RuleApplication
  that names it);
- *inserted* = empty spelling;
- *replaced / shortened* = the RuleApplication that did it.

**The segment IS the phoneme.** No phoneme strings exist inside the model.
Rules condition on typed features (`.geminate`, `.nasal`, `.quality`) — never
string parsing. Output tokens (IPA-ish strings, including simple mode) are a
per-riwaya **render table** keyed on segment features (§6). IPA lives only in
data files, which is the byte-controllability seam.

## 2. The Pydantic draft

Minimal by construction: every field below is forced by a case in
`domain-facts.md` or by a reviewer-verified hard case. Anything speculative
was explicitly killed (§9). Ids are integer indices into the flat arrays of
`Recitation` — serializable, acyclic, O(1) to resolve [S].

```python
from enum import Enum
from typing import Literal, Annotated, Union
from pydantic import BaseModel, ConfigDict, Field


# ─── written spine ───────────────────────────────────────────────────────

class GraphemeKind(str, Enum):
    CONSONANT = "consonant"          # incl. all hamza seats
    VOWEL_LETTER = "vowel_letter"    # ا و ي ى and mini/dagger forms
    HAMZA_WASL = "hamza_wasl"
    HARAKA = "haraka"
    TANWEEN = "tanween"
    SHADDAH = "shaddah"
    EXTENSION = "extension"          # dagger alef, mini waw/yaa, maddah
    SILENCE_MARK = "silence_mark"    # round / rectangular zero
    MARK = "mark"                    # sakt seen, iqlab meem, other small marks
    STOP_SIGN = "stop_sign"

class Grapheme(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int                    # == index in Recitation.graphemes
    char: str                  # the raw codepoint(s)
    kind: GraphemeKind         # from the riwaya ScriptSpec — only classification
    word: int                  # index into Recitation.words
    seat: int                  # letter-grouping index (base + its marks share a
                               # seat; extensions share the carrier's seat)
    letter: str | None = None  # LetterId for base letters ("lam", "hamza_wasl");
                               # None for marks/harakat — the skeleton currency
    display: str | None = None # contextual display override (ئ rendered as ي)
```

Extensions and silence marks are **their own graphemes** (first-class): a
dagger alef can be a segment's sole spelling, which is all "extension
first-class" requires [D]. There is **no Cluster class**: the seat index *is*
the grouping, and views that need per-letter grouping do `groupby(seat)` at
projection time [S]. There is no written-layer fusion for tajweed-fused
letters — fusion exists only on the sound spine as shared spelling (silent
letters must remain written; mergers cross words).

```python
# ─── sound spine ─────────────────────────────────────────────────────────

class Consonant(BaseModel):
    model_config = ConfigDict(frozen=True)
    kind: Literal["consonant"] = "consonant"
    id: int                          # == index in Recitation.segments
    word: int                        # home word (where the sound lands)
    spelling: tuple[int, ...]        # grapheme ids; () => inserted
    ident: str | None                # ConsonantId into the riwaya inventory;
                                     # None = placeless nasal (ikhfaa/iqlab) [A]
    geminate: bool = False
    nasal: bool = False              # ghunnah hold
    emphatic: bool = False           # tafkheem resolved
    qalqala: bool = False            # echo release

class Vowel(BaseModel):
    model_config = ConfigDict(frozen=True)
    kind: Literal["vowel"] = "vowel"
    id: int
    word: int
    spelling: tuple[int, ...]
    quality: str                     # VowelQuality into the inventory
                                     # ("a","i","u"; Warsh adds "e" imala, …)
    long: bool = False               # short vs long; counts live on the
                                     # MaddApplication (leen has no vowel) [A]
    emphatic: bool = False

Segment = Annotated[Union[Consonant, Vowel], Field(discriminator="kind")]
```

Only two segment types. Reviewed alternatives and why they died: an `Echo`
segment (qalqala) would reintroduce the skip-Q hack into every scan of "the
last consonant" — the flag keeps rule code clean and the renderer expands it
to today's discrete `Q` token (§6) [A]; a `Pause` segment for sakt is
unnecessary — sakt is a word-boundary fact that *blocks* detectors, carried
on the Word (below); rawm/ishmam/hams are performance annotations, not
articulation structure — representable later as annotation rule applications
if ever produced; `release=UNRELEASED` had no case needing it (naqis = two
consonants + a non-merging application) [A].

```python
# ─── tajweed, first-class ────────────────────────────────────────────────
# Applications are typed by the domain's EFFECT verbs (domain-facts §4), so a
# participant's role is the field name — never a stringly-typed role [D].
# The rule id (riwaya-scoped registry key) carries the §5 family identity.

class _App(BaseModel):
    model_config = ConfigDict(frozen=True)
    rule: str                        # RuleId, e.g. "ikhfaa_tanween", "madd_lazim"

class Assimilation(_App):            # idgham family, iqlab, lam shamsiyah
    kind: Literal["assimilation"] = "assimilation"
    source: tuple[int, ...]          # trigger grapheme ids (the silenced noon /
                                     # tanween / lam / first letter)
    target: int                      # the resulting segment id
    complete: bool = True            # False = mutajanisayn naqis: source keeps
                                     # its own segment; nothing merges [A]

class Silence(_App):                 # a grapheme sounds nothing, and why
    kind: Literal["silence"] = "silence"
    grapheme: int
    # rule covers both tajweed reasons ("hamza_wasl_silent") and orthographic
    # conventions ("otiose_alef", "tanween_alef") — closes the known
    # continuing-tanween-alef attribution gap from the silent-letter audit

class Insertion(_App):               # sound with no written source
    kind: Literal["insertion"] = "insertion"
    segment: int                     # ("hamza_wasl_vowel", "iltiqaa_kasra",
                                     #  "madd_iwad", "allah_alef")

class Madd(_App):                    # length classification (madd + leen)
    kind: Literal["madd"] = "madd"
    segment: int                     # the Vowel — or the glide Consonant (leen)
    counts_min: int                  # resolved from riwaya data per rule
    counts_max: int                  # (2,2) tabii; (4,5) muttasil; (2,6) arid

class Substitution(_App):            # sounds other than written
    kind: Literal["substitution"] = "substitution"
    segment: int                     # ("taa_marbuta_haa", "iltiqaa_shortening",
    grapheme: int                    #  "alef_maksura_consonant", "tasheel")

class Annotation(_App):              # no structural change: izhar, tafkheem/
    kind: Literal["annotation"] = "annotation"       # tarqeeq, qalqala degree,
    graphemes: tuple[int, ...] = ()                  # hamza-wasl vowel choice,
    segment: int | None = None                       # sakt-blocked-rule record

RuleApplication = Annotated[
    Union[Assimilation, Silence, Insertion, Madd, Substitution, Annotation],
    Field(discriminator="kind"),
]
```

Six effect shapes cover all 33+ Hafs rules and the known Warsh additions
(imala = Annotation + Vowel quality; naql = Insertion/Silence pair). Detectors
*apply* effects to segments **and** append the application; the application is
the durable annotation (what the tajweed view reads), the segment features
are the durable result (what the renderer reads). Neither is re-derived.

```python
# ─── result aggregate ────────────────────────────────────────────────────

class Boundary(str, Enum):
    WASL = "wasl"; WAQF = "waqf"; IBTIDAA = "ibtidaa"    # ibtidaa may combine
                                                          # with waqf on one word

class Word(BaseModel):
    model_config = ConfigDict(frozen=True)
    index: int
    location: str                    # riwaya-scoped address ("2:255:3")
    text: str
    starting: bool = False           # ibtidaa here
    stopping: bool = False           # waqf after this word
    sakt_after: bool = False         # blocks cross-word detectors, no waqf
    stop_sign: str | None = None

class Recitation(BaseModel):
    model_config = ConfigDict(frozen=True)
    ref: str
    riwaya: str
    words: tuple[Word, ...]
    graphemes: tuple[Grapheme, ...]      # id == index
    segments: tuple[Segment, ...]        # id == index; recitation order
    rules: tuple[RuleApplication, ...]
```

One `Recitation` = **one traversal** (one boundary assignment), exactly as
today. The three renditions of a word differ by the closed §7 transform set,
so a consumer wanting wasl *and* waqf phonemizes twice; because cross-word
rules couple neighbours, the Recitation — not the Word — is the only valid
re-run/cache unit [A]. Simultaneous multi-state representation was
considered and rejected as scope creep.

## 3. Tajweed first-class: detectors + applications, two axes

The domain has two orthogonal taxonomies and the model keeps them apart [D]:

- **Rule families** (domain-facts §5 — noon/tanween, meem, idgham, qalqala,
  tafkheem, madd, hamza-wasl, …) are the *decision* axis → **detectors**:
  one plain function per family in a flat registry, its decision table and
  trigger sets read from riwaya data. ~12 functions, each one screen.
- **Effect verbs** (domain-facts §4 — substitute, silence, insert, lengthen,
  colour, classify) are the *mutation* axis → the **RuleApplication union**
  above.

Worked detector (noon/tanween family) against the model:

```python
@register("noon_tanween")
def detect_noon_tanween(b: Builder, spec: RiwayaSpec) -> None:
    table = spec.rules.noon_tanween        # exhaustive, mutually exclusive —
    for trig in b.noon_or_tanween_triggers():          # no priority order
        nxt = b.next_sounding(trig, cross_word=not trig.word.stopping)
        if nxt is None:            # waqf: rule self-cancels, no code needed
            continue
        if b.sakt_blocks(trig, nxt) or b.izhar_mutlaq(trig, nxt):
            b.add(Annotation(rule="izhar", graphemes=trig.grapheme_ids)); continue
        rule, effect = table.classify(nxt.letter)
        n_seg = b.noon_segment(trig)       # the /n/ this trigger sounds
        match effect:
            case "keep":                   # izhar
                b.add(Annotation(rule=rule, graphemes=trig.grapheme_ids))
            case "nasalize":               # ikhfaa — placeless nasal
                b.set(n_seg, ident=None, nasal=True, emphatic=b.heavy(nxt))
                b.add(Substitution(rule=rule, segment=n_seg.id, grapheme=trig.gid))
            case "hidden_meem":            # iqlab
                b.set(n_seg, ident=spec.rules.iqlab_ident, nasal=True)
                b.add(Substitution(rule=rule, segment=n_seg.id, grapheme=trig.gid))
            case "merge_nasal" | "merge_plain":        # idgham (may cross word)
                b.delete(n_seg)
                tgt = b.first_consonant(nxt)
                b.set(tgt, geminate=True, nasal=(effect == "merge_nasal"),
                      spelling=tgt.spelling + trig.grapheme_ids)   # joint ownership
                b.add(Assimilation(rule=rule, source=trig.grapheme_ids, target=tgt.id))
```

What this kills from today's code: `mark_phonemized` neighbour-mutation
hacks, `detect_cross_word_mergers` reverse-engineering, the tanween/noon rule
duplication (same trigger stream), and the "rules that disappear when
stopping" special-casing (`next_sounding` returning None *is* the
cancellation).

## 4. The riwaya seam

Per the maintainer's direction: **a base class holds the shared machinery;
riwaya subclasses override only deltas** — with the guard that a subclass
overrides *data and pass composition*, never inlines domain logic (that was
the original Warsh blocker) [S].

```python
class RiwayaSpec(BaseModel):             # the entire per-riwaya DATA surface
    model_config = ConfigDict(frozen=True)
    name: str
    script: ScriptSpec                   # codepoint → GraphemeKind (+ LetterId)
    inventory: PhonemeInventory          # ident/quality + features → token,
                                         #   simple-mode token (render tables)
    rules: RuleData                      # trigger sets, pair maps, decision
                                         #   tables, madd counts, iqlab ident
    skeletons: tuple[SkeletonEntry, ...] # canonical-form overrides (§5)
    locations: tuple[LocationEntry, ...] # true per-location residue (§5)

class Riwaya:
    """Base class: tokenizer, boundary assignment, builder, freeze, and the
    default detector pipeline. Subclasses provide a spec and may extend or
    reorder PIPELINE — they do not override detector internals."""
    spec: RiwayaSpec
    PIPELINE: tuple[str, ...] = (
        "specials_splice",       # skeleton-matched words (muqattaat, …)
        "ibtidaa_repairs",       # hamza-wasl vowel, initial-shaddah drop
        "waqf_transforms",       # final-cluster transforms, 'iwad, taa marbuta
        "assimilation",          # noon/tanween, meem, idgham pairs, shamsiyah
        "letters",               # base realization, shaddah, vowel letters,
                                 #   iltiqaa, qalqala flag
        "colouring",             # tafkheem (isti'laa, raa tree, Allah lam)
        "madd",                  # one scan of the realized segments
        "overrides",             # skeleton + location tables, context-gated
    )
    def phonemize(self, ref, *, stops) -> Recitation: ...   # shared, final

class Hafs(Riwaya):
    spec = load_spec("resources/hafs")

class Warsh(Riwaya):
    spec = load_spec("resources/warsh")
    PIPELINE = Riwaya.PIPELINE[:6] + ("imala", "naql") + Riwaya.PIPELINE[6:]
```

A new riwaya = a data bundle + optionally a few new *registered* detector
functions named in its pipeline. Pass ordering is an inspectable tuple
mirroring the genuine domain dependency chain (domain-facts §8.8), not
OO dispatch order.

## 5. Overrides: canonical skeletons first, locations last

Locations don't transfer across riwayat (verse numbering differs); word
shapes do. So the primary override key is the **skeleton**: the tuple of
base-letter identities (`Grapheme.letter`) of a word, normalized (hamza
seats → hamza, ى/ي → yaa; hamza-wasl kept distinct), with a structural
condition:

```python
class OverrideCondition(str, Enum):
    ALWAYS = "always"; WHEN_STARTING = "when_starting"
    WHEN_STOPPING = "when_stopping"; SURAH_INITIAL = "surah_initial"

class SkeletonEntry(BaseModel):
    model_config = ConfigDict(frozen=True)
    letters: tuple[str, ...]         # ("hamza_wasl","lam","lam","ha") = ٱللَّه
    condition: OverrideCondition = OverrideCondition.ALWAYS
    rule: str                        # detector/patch to apply

class LocationEntry(BaseModel):
    model_config = ConfigDict(frozen=True)
    location: str
    condition: OverrideCondition
    rule: str
```

Skeleton-keyed (portable across riwayat): the Allah patterns, hamza-wasl
special nouns/verbs, the muqatta'at (skeleton + `SURAH_INITIAL`), particle
words (يَـٰٓ / هَـٰٓ munfasil reclassification). Location-keyed residue (~a
dozen Hafs entries): imala 11:41, tasheel 41:44, the four sakts, ha'-sakt
spots, 27:36, the madd-lazim overrides, the yaa-narration exceptions.
Override *payloads* are expressed in typed segment terms (patch specs), never
raw phoneme strings — a string escape hatch would gut the no-strings bet [A].

## 6. Rendering: the only place output bytes exist

`render(segment, inventory, mode) -> tuple[str, ...]` — a data-table lookup
keyed on segment features, expanding one segment to *n* tokens
deterministically (n>1 exactly for the qalqala echo: `d` → `("d","Q")`;
geminates are one token `"bb"`; simple mode is a second column of the same
table, where e.g. `Q` renders to nothing and nasals denasalize) [A].

Phone positions (today's `phoneme_indices`, alignment) are computed by
enumerating the rendered stream — true by construction, no stored indices.
**Risk #1 of this whole design** is the fidelity of this table: it must
regenerate today's token stream byte-identically across 326k letters. It is
only provable against the Epic 2A characterization net, which therefore gates
the model, and the first migration step is building this render table and
diffing it against current output.

## 7. The public contract

`Recitation` replaces the six views. With one precomputed reverse index
(`spelled = union of all segment spellings`):

| Today's view | Under the new contract |
|---|---|
| `phonemes_*` | `[render(s) for s in rec.segments]` — one-liner |
| `silent_flags` | `[(g.char, g.id not in spelled) for g in rec.graphemes]` — one-liner |
| `get_mapping` / alignment | segments already carry `spelling`; enumerate — one-liner |
| `phonetic_text` | render + break on `segment.word` — near one-liner |
| `character_phoneme_mappings` | thin projection: one cell per grapheme + per inserted segment; indices by enumeration |
| `letter_phoneme_mappings` | thin projection: `groupby(seat)`, fold silent seats into the neighbour their sound merged into (direction read off `spelling` spans — the three re-implementations die) |
| `tajweed_mappings` | thin projection: `rules` filtered per grapheme (source/target = typed fields); muqatta'at spelled-out display from riwaya data |

Three thin projection methods + four one-liners, all reading one frozen
object — drift is structurally impossible. Whether to keep the old methods as
compatibility shims is a packaging decision, not a design one.

## 8. Worked example — غَفُورٞ رَّحِيمٌ (cross-word idgham bila ghunnah + long vowels)

Wasl traversal, segments (abbreviated):

```
s0 Consonant(ghayn, emphatic)   spelling=(غ,)          Annotation(tafkheem)
s1 Vowel(a, emphatic)           spelling=(fatha,)
s2 Consonant(faa)               spelling=(ف,)
s3 Vowel(u, long)               spelling=(damma, و)     Madd(tabii, 2..2)
s4 Consonant(raa, emphatic)     spelling=(ر,)          Annotation(tafkheem)
s5 Vowel(u)                     spelling=(dammatan,)
s6 Consonant(raa, geminate)     spelling=(dammatan, ر₂, shaddah₂)   ← spans words
                                 Assimilation(idgham_bila_ghunnah_tanween,
                                              source=(dammatan,), target=s6)
s7 Vowel(a) … s9 Vowel(i, long) spelling=(kasra, ي)     Madd(tabii, 2..2)
s10 Consonant(meem)  s11 Vowel(u)  s12 Consonant(noon)
```

The tanween's noon sounds nowhere — no segment; its grapheme is named by the
Assimilation. Waqf traversal on رَّحِيمٌ: identical through s8; s9's madd
becomes `Madd(arid, 2..6)`; s11/s12 don't exist (`Silence(tanween_drop)`);
s10 is final. The wasl/waqf diff is three applications — domain invariant
§8.5 made literal. Ibtidaa on رَّحِيمٌ: no assimilation fired, so s6 is simply
`Consonant(raa)` — the trace-shaddah's conditionality falls out of whether
the rule ran.

## 9. Kill list (what died in review, so it stays dead)

From v1: `Unit` (overloaded god-object), `role`/`status` enums (derivable),
`ShareGroup` (is `spelling`), `MaddInfo`+`MaddMapping` (is the Madd
application), `written_delta` (phonetic text is a render), `Phoneme` class +
feature bag (segment IS the phoneme), nested `Cluster` container (seat
index), per-letter tag lists.
From review candidates: `Echo`/`Pause` segment types, `Release` enum incl.
`UNRELEASED`, `Ghunnah` object with counts (bool until a consumer proves it
needs the hold length), `pausal` field (rawm/ishmam not produced today),
`RawSegment` string escape hatch, per-state simultaneous segment sets,
synthetic spelled-grapheme layer for muqatta'at (spelled-name display is
riwaya data + per-segment rules; revisit only if the tajweed projection
proves it insufficient).

## 10. Pydantic pragmatics (326k graphemes, ~400k segments)

- Build phase: mutable `@dataclass(slots=True)` builder objects; detectors
  call builder methods (`b.set/delete/add`), which maintain the reverse
  indices — segments are only frozen into Pydantic models at `freeze()`.
- Contract leaves (`Grapheme`, segments, applications): if profiling shows
  model construction dominating, ship them as frozen slotted dataclasses
  (Pydantic v2 serializes stdlib dataclasses natively) or construct via
  `model_construct()`; validate only in tests / `validate=True`.
- Enums `str`-backed; rule ids and render tokens interned.

## 11. Risks (ranked) and open questions

1. **Render-table fidelity** (§6) — make-or-break, provable only against the
   characterization net; build it first.
2. **Muqatta'at projection granularity** — the killed spelled-grapheme layer
   is the fallback if data-driven spelled display proves insufficient.
3. **Global stream ownership** — committed now (naql); `segment.word` is the
   sounding home, spelling is the truth of sharing.
4. **Placeless nasal** (`ident=None`) — inventory must render it (heavy/light
   ŋ from `emphatic`), and detectors must not assume `ident` is set.
5. **Override payload migration** — today's contextual YAML speaks phoneme
   strings and display chars; rewriting it as typed patches is real work and
   the likeliest place a string hatch sneaks back in.

Open: exact `RuleData` schema per family; whether `Hafs`/`Warsh` classes stay
or collapse to `Riwaya(spec)` once real (defer until Warsh lands); whether the
compat shims for today's six views ship at all.
