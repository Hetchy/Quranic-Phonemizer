# Recitation Domain Facts

Domain inventory stated in domain language, with no proposed code structure.
It is distilled from today's Hafs implementation, the `docs/hafs/` research
documents, and the mapping contracts. It contains both implemented behavior
and broader recitation facts; it is **not** a requirement that the first
riwāyah abstraction model every item. Implemented facts and selected-Warsh
deltas enter the model only with public behavior and tests. Hafs-specific
instantiations are marked. Performance duration is not a phonemizer output.

---

## 1. The writing system — what exists on the page

### 1.1 Structure

- The corpus is a sequence of **words**, grouped into **verses**, grouped into
  **surahs**. Every word has an exact **location** (surah:verse:word). Different
  riwayat may split verses and join/split words differently — location shape is
  per-riwaya.
- A word is a sequence of **letter clusters**. A letter cluster is:
  - exactly one **base letter** (consonant, vowel letter, hamza, or hamza
    al-wasl), plus
  - at most one **haraka** (fatha / damma / kasra / sukun) **or** one
    **tanween** (fathatan / dammatan / kasratan) — never both, plus
  - optionally a **shaddah** (gemination mark), which combines with a haraka or
    tanween, plus
  - zero or more first-class **small vowels**: dagger alef, mini waw, and mini
    yaa — written small but capable of carrying the same vowel sound as a full
    carrier, plus
  - zero or more **orthographic signs/hints**, including maddah and the small
    mīm used to show iqlāb, plus
  - zero or more **silence marks**: the round zero ("always silent") and the
    rectangular zero ("silent when continuing") — written on a big letter to
    say it does *not* sound, plus
  - zero or more other small marks (small high seen = sakt, small high/low meem
    = iqlab hint, etc.).
- A word may carry a **stop sign** (a symbol between words). Stop signs never
  make a sound; they only advise whether the reciter may/should/must not stop
  there.
- A letter with *no* haraka, tanween, or shaddah is **bare**. A bare consonant
  is functionally vowelless (sakin), like one bearing sukun — but bare vs
  explicit-sukun is orthographically meaningful (bare often signals a
  following assimilation).

### 1.2 Orthographic facts

- **Tanween occurs only at the end of a word** (it is case marking). Its
  companion: a fathatan is usually followed by an otiose alef or alef maksura
  seat that is silent in continuation.
- **Shaddah means the consonant is doubled** (a sakin copy followed by a
  voweled copy).
- **Word-initial shaddah** is never a root gemination; it is the written trace
  of an idgham from the previous word ("shadda 'aridah"). It only sounds
  doubled when the words are actually joined.
- The **small vowels can sound despite their size**: dagger alef = a long *aa*,
  mini waw/yaa at word end = the pronoun silah vowel, mini yaa mid-word = a
  yaa. The same source form may be silenced by boundary rules. (The maddah is
  different: a reading aid written over already-long
  madds, carrying no information the rules don't supply.) The silence marks
  do the opposite: a big letter that does not sound.
- Some sounds have **no written letter at all** and must be inserted by rule:
  the helping vowel of hamza al-wasl when starting, the helping kasra at a
  two-sukoon meeting, the long *aa* inside the word Allah, the substitute alef
  of tanween at pause.
- The same sound can be written with **several different glyphs** (all hamza
  seats sound as the glottal stop; ى and ي both sound as yaa), and one glyph
  can sound differently by context (waw as consonant *w* vs long *uu*; taa
  marbuta as *t* or *h*).

---

## 2. The recitation states

Every stretch of recitation is read under exactly one traversal of three
boundary states per word:

- **wasl** (connected): the word is joined to its neighbours; cross-word rules
  fire.
- **waqf** (stopping): recitation pauses *after* this word; the word's ending
  is transformed (see §7) and cross-word rules with the next word are
  cancelled.
- **ibtidaa** (starting): recitation begins *at* this word; word-initial
  repairs apply (hamza al-wasl sounds, initial shaddah is dropped).

Golden rules of the domain:

1. **You cannot stop on a full vowel** — the last letter is silenced (sukun) or
   the ending is otherwise repaired (madd 'iwad, taa marbuta → h, rawm/ishmam
   nuances).
2. **You cannot start on a vowelless letter** — hamza al-wasl exists precisely
   to supply a starting vowel and disappears when not needed.
3. **Two vowelless letters cannot meet across a join** (iltiqaa al-sakinayn) —
   the first is repaired: a long vowel shortens, or a helping kasra is inserted
   after tanween.

Which words stop/start is *not* fully encoded in the script: verse ends are
customary stops, stop signs advise, and the reciter (or caller) chooses. So
the same written word has **up to three renditions** (connected, stopped-on,
started-on), and the differences are systematic, not arbitrary.

---

## 3. What a rule may condition on (the axes)

Every rule in the domain conditions on some subset of:

1. **The cluster itself** — base letter identity, short vowel/tanween/small
   vowel, shaddah, sukun, and orthographic hints.
2. **Neighbouring clusters** — usually the immediately next or previous
   letter, occasionally two away (raa looks back two; hamza al-wasl looks at
   the *third* letter of the word). **Neighbour lookups cross word
   boundaries** when the words are joined.
3. **Position in word** — first letter, last letter, mid-word.
4. **Boundary state** — wasl / waqf / ibtidaa of this word (and, for
   cross-word rules, of the pair).
5. **The word as a whole** — pattern matching on the word's letter skeleton
   (the Allah patterns, the hamza-wasl special nouns/verbs).
6. **The exact location** — a closed list of per-location exceptions (imala,
   tasheel, sakt, madd overrides, contextual pronunciations, muqatta'at).
7. **Previously computed sound** — some rules read the *sound* stream, not the
   letters: madd classification looks at the next *phoneme* (is it hamza? a
   geminate? a ghunnah?); vowel-letter lengthening looks at the previous
   *phoneme*.

No rule needs anything else. In particular, no rule needs more than
one-word lookahead, and location-conditioned rules are closed finite lists.

---

## 4. What a rule may do (the effect vocabulary)

Every rule's effect is a combination of:

- **Substitute** a sound (iqlab: noon → hidden meem; idgham with ghunnah: next
  consonant → its nasalized form; taa marbuta at pause → h; alef maksura at
  pause → consonant yaa).
- **Delete / silence** a sound (idgham source letter, lam shamsiyah, hamza
  al-wasl in wasl, otiose alef, tanween's noon in idgham).
- **Insert** a sound with no written source (hamza-wasl helping vowel, iltiqaa
  kasra, madd-'iwad alef, the Allah long *aa*, qalqala echo).
- **Lengthen / shorten** a vowel (vowel letters and small letters lengthen the
  preceding short vowel; iltiqaa shortens a long vowel; waqf lengthens
  fathatan into *aa*).
- **Colour** a sound (tafkheem: emphatic consonant colouring spreads to its
  fatha; ghunnah nasalization; imala; tasheel; rawm/ishmam at pause).
- **Classify** without changing sound (madd subtype + its count; rule tags for
  display: which letters participate in which named rule, as source or
  target).

Deleted letters remain *written*; the domain therefore always distinguishes
**the written grapheme** from **whether and what it sounds** — and a sound may
be shared by several graphemes (a long vowel is "owned" jointly by the haraka
and its carrier letter; an idgham geminate is owned jointly by the silent
source and the sounding target, possibly across a word boundary).

---

## 5. Rule families

Notation per rule: *trigger → effect*. ⇄ = may cross a word boundary.
⏸ = depends on waqf/ibtidaa state.

### 5.1 Noon sakinah and tanween

The trigger is either **a bare/sakin noon** or **a tanween** — the same rule
set applies to both, because tanween *is* a short vowel + noon. Since tanween
is word-final and noon sakinah may be word-final, all of these rules ⇄. The
decision is made by the next sounding letter (skipping the otiose alef):

| Next letter | Rule | Effect |
|---|---|---|
| ء ه ع ح غ خ (throat) | **izhar** | noon sounds clearly (`n`) |
| ي ن م و | **idgham with ghunnah** | noon deleted; next consonant nasalized and doubled ⇄ |
| ل ر | **idgham without ghunnah** | noon deleted entirely ⇄ |
| ب | **iqlab** | noon → hidden meem (nasal) ⇄ |
| the remaining 15 | **ikhfaa** | noon → nasal (ŋ), coloured heavy before heavy letters ⇄ |

- **Izhar mutlaq** (Hafs): noon + ي/و *within the same word* does NOT
  assimilate (الدنيا، بنيان، قنوان، صنوان) — idgham with ghunnah is
  cross-word (or across the tanween boundary) only for ي/و.
- **Sakt blocks the rule** (Hafs): at 75:27 (مَنۡ رَاقٖ) the sakt prevents the
  expected noon→raa idgham.
- ⏸ At waqf on the tanween word, all of these are cancelled — see §7 for what
  tanween itself becomes.
- Mushaddad noon (نّ) is its own rule: **noon ghunnah**, the strongest
  nasalization, held ~2 counts, kept even at waqf.

### 5.2 Meem sakinah

Word-final sakin meem, decided by the next word's first letter (all ⇄):

- before ب → **ikhfaa shafawi** (hidden meem, nasal);
- before م → **idgham shafawi** (merged into a doubled nasal meem; *both*
  written meems are considered sounding);
- anything else → **izhar shafawi** (clear `m`; extra care before و and ف).
- Mushaddad meem (مّ) → **meem ghunnah**, as for noon.

### 5.3 Idgham of adjacent consonants (non-noon/meem)

A bare/sakin consonant followed by a specific partner assimilates. The source
letter goes silent and the target sounds doubled (written shaddah on the
target usually confirms it). Pairs are a closed list (Hafs):

- **mutamathilayn** (identical letters), e.g. د→د, ل→ل, و→و ⇄;
- **mutaqaribayn** (near articulation): ل→ر ⇄; ق→ك (one word: نَخۡلُقكُّم);
- **mutajanisayn kamil** (same articulation point, complete): ذ→ظ, د→ت, ت→د,
  ت→ط, ث→ذ, ب→م ⇄;
- **mutajanisayn naqis** (incomplete): ط→ت only — the ط keeps its sound body
  (and its tafkheem); only partially assimilates; the ت is *not* doubled.
- **lam shamsiyah**: the article's lam before the 14 sun letters is a special
  case of this family — lam silent, sun letter doubled. Within-word ل→ل is
  shamsiyah, not mutamathilayn. Before moon letters the lam simply sounds
  (lam qamariyah — the unmarked default).
- Sakt blocks idgham (Hafs 83:14 بَلۡ رَانَ).
- ⏸ Cross-word idgham is cancelled at waqf on the first word; word-initial
  shaddah is dropped at ibtidaa on the second.

### 5.4 Qalqala

The five letters ق ط ب ج د, when vowelless, get an **echo/rebound** after the
closure:

- **sughra** (minor): vowelless mid-word or mid-recitation;
- **kubra** (major): word-final at waqf ⏸ (the waqf sukun creates it);
- **akbar** (strongest): word-final *shaddah* at waqf ⏸ (doubled closure).
- A qalqala letter whose sukun is consumed by idgham does **not** qalqala
  (the closure never releases).

### 5.5 Tafkheem / tarqeeq (heaviness)

- The seven isti'laa letters خ ص ض غ ط ق ظ are **always heavy**; heaviness
  colours their fatha (and fathatan) toward *aˤ*. All other letters are always
  light except three conditional ones:
- **Lam of the word Allah**: heavy after fatha/damma, light after kasra. The
  preceding vowel may come from the previous word ⇄; at a verse start the
  implicit predecessor is fatha. Special: a preceding tanween resolved by
  iltiqaa kasra makes it light (7:164, 11:31). The word Allah is recognized by
  a closed list of word skeletons (ٱللَّه، لِلَّه، بِٱللَّه، ٱللَّهُمَّ …).
- **Raa**: heavy with fatha/damma (and their tanweens), light with kasra. A
  vowelless raa takes the previous vowel's quality (fatha/damma → heavy,
  kasra → light), looking through another sukun to the vowel before it —
  *except* kasra + a following isti'laa letter in the same word makes it
  heavy (فِرۡقٖ etc., a closed list; some are scholarly khilaf). ⏸ At waqf the
  final raa's written vowel is silenced first, so its heaviness is
  re-decided by the sukun rules — ~65% of verse-final raas flip class.
- **Long alef** is coloured by the consonant it follows (heavy after a heavy
  consonant), including the implicit Allah alef.
- Ghunnah is likewise coloured by the *following* letter (heavy before
  isti'laa).

### 5.6 Madd (vowel length)

The long vowels are *aa/uu/ii*: a short vowel + matching vowel letter (or
small letter). Performance duration is deliberately absent from the target
phonemizer model.

| Type/context | Trigger | Target-model treatment |
|---|---|---|
| **tabii'** (natural) | nothing special follows | supported `MaddType` |
| **badal** | hamza *before* the long vowel | not a distinct type in current output |
| **wajib muttasil** | hamza follows in the *same* word | supported `MaddType` |
| **jaiz munfasil** | hamza begins the *next* word ⇄, only in wasl ⏸ | supported `MaddType` |
| **lazim** | permanent sukun/shaddah/ghunnah follows in the same word | supported `MaddType` |
| **'arid lil-sukoon** | waqf sukun follows ⏸ | supported `MaddType` |
| **leen** | fatha + consonantal و/ي + waqf sukun ⏸ (not a long vowel) | supported `MaddType` |
| **silah context** | a pronoun/plural small vowel sounds in wasl and drops at waqf ⏸ | realization context, not assumed to be a `MaddType` |
| **'iwad** | fathatan at waqf → substitute alef ⏸ | realization event, not a distinct current `MaddType` |

- Graphically-joined particles (vocative يَـٰٓ, demonstrative هَـٰٓ) look like
  muttasil but are linguistically munfasil (separate words joined in rasm).
  240 sites, 22 written forms. A proclitic or the interrogative hamza may
  stand before the particle without changing this — أَهَـٰٓؤُلَآءِ (5:53,
  6:53, 7:49, 34:40) and وَهَـٰٓؤُلَآءِ (17:20) separate where هَـٰٓؤُلَآءِ
  does, since neither touches the ها|أولاء seam. هَآؤُمُ (69:19) is the same
  shape and is **not** one of them: its hamza is a radical of هاء, so it is
  muttasil. Only a lexicon separates the two.
- Madd lazim kalimi mukhaffaf exists in exactly one Hafs word (ءَآلۡـَٰٔنَ,
  10:51 & 10:91). Madd lazim kalimi **muthaqqal** is the far commoner half —
  a long vowel before a shadda in the same word, ٱلضَّآلِّينَ, دَآبَّةٍ,
  ٱلْحَآقَّةُ. A geminate is a sakin plus a voweled letter, so it meets a madd
  exactly as a written sukun does.
- Which letter a stop lands on is not the last slot of the word. A tanween
  noon is written after its letter and the stop drops it, so عَظِيمٌ stops on
  the meem — that is what makes the ī before it 'arid, and the yaa of
  قُرَيْشٍ a leen. And a stop silences only a **short** vowel: مُوسَىٰ and
  قَوْلِى end long, nothing goes quiescent, and neither 'arid nor leen
  applies ⏸.
- The article doubles a sun noon (ٱلنَّاسِ), so that noon is a ghunnah
  mushaddadah as much as the canonical one in ءَامَنَّا — 618 sites. A sun
  **meem** does not exist; ٱلْمَغْضُوبِ keeps its lam.
- At waqf, a munfasil reverts to tabii' (the next word never arrives) ⏸.
- The dagger alef is an unconditional madd (always sounds). The maddah mark
  carries **no information of its own** — it is written over madds that the
  rules above already classify as longer-than-natural; classification never
  needs it.
- Today's public classifier implements tabiiʿ, wājib muttaṣil, jāʾiz munfaṣil,
  lāzim, ʿāriḍ lil-sukūn, and leen. Badal, silah subcategories, and ʿiwaḍ as a
  distinct public `MaddType` are not added merely because they are useful
  linguistic descriptions; a supported riwāyah behavior and tests must
  require them.

### 5.7 Hamza al-wasl

- **In wasl: silent.** Its neighbours join directly, which may create an
  iltiqaa al-sakinayn on the previous word ⇄:
  - previous word ends in a long vowel → shorten it;
  - previous word ends in tanween → insert a helping kasra after the noon.
- **At ibtidaa: it sounds as hamza + a helping vowel** ⏸ chosen by grammar:
  - before the article's lam → fatha;
  - special nouns (ٱسم ٱبن ٱبنة ٱمرؤ ٱمرأة ٱثنان ٱثنتان) and a closed list of
    imperative verbs → kasra;
  - otherwise a verb: look at its third letter's vowel — damma → damma,
    fatha/kasra → kasra.

### 5.8 Vowel letters and silence

- A vowel letter (ا و ي ى and the small letters) **lengthens the previous
  short vowel** when compatible (alef after fatha; waw after damma — or the
  fatha of the archaic spellings صَلَوٰة-type; yaa after kasra; alef maksura
  after fatha or kasra). When incompatible or redundant, the vowel letter is
  **silent**.
- The **otiose alef** after waw of the plural (قَالُوا۟) is always silent; the
  rectangular-zero alef (أَنَا۠) is silent in wasl but sounds 2 counts at waqf
  ⏸ (the "seven alifs" of Hafs).
- A carrier waw/yaa bearing a dagger alef (صَلَوٰة) is a silent seat; the
  dagger carries the sound.
- ⏸ At waqf, a final ى/و/ي with a haraka can flip role: after an
  incompatible vowel it sounds as a consonant (ٱلۡبَغۡىِ); after a compatible
  one it becomes the long vowel (هُوَ → *huu*).
- Silence is a *positional* fact: an assimilated letter, a hamza wasl, a
  shamsiyah lam, an otiose alef are all written-but-unsounded, and which
  graphemes are silent **changes with the boundary state** ⏸.

### 5.9 Taa marbuta

- In wasl: sounds *t*. At waqf: sounds *h* (whispered) ⏸ — and the tanween on
  it drops entirely (no madd 'iwad). Words written with open taa (رَحۡمَت …)
  stop on *t* instead (rasm-driven, closed list).

### 5.10 Sakt and other pause phenomena

- **Sakt**: a breathless pause mid-wasl, marked by the small high seen. Hafs
  has four mandatory sakts (18:1→2, 36:52, 75:27, 83:14) and two permissible
  ones. A sakt blocks cross-word assimilation without triggering waqf
  transforms.
- **Rawm** (voicing ⅓ of a final damma/kasra) and **ishmam** (lip-rounding a
  final damma) are waqf-time performance variants; **ishmam also occurs once
  mid-word** in Hafs (12:11 تَأۡمَ۫نَّا) on an assimilated damma.
- **Ha' as-sakt**: a pausal *h* written in the text (كِتَٰبِيَهۡ …), mandatory
  at four Hafs locations.

### 5.11 Muqatta'at (the opening letters)

- The disconnected letters are recited as their **spelled names** (ص = *ṣaad*,
  م = *miim* …): one written grapheme → a whole syllable of phonemes.
- Within the spelled names, the ordinary rules apply *between* names: madd
  lazim (6) on the ل م س ك ع ص ن ق names, natural madd (2) on ح ي ط ه ر,
  and ع alone reaches its lazim through a **leen** — *ʿayn* is fatha, sakin
  yaa, sakin noon — so it is classified there rather than by the long-vowel
  classifier (19:1 and 42:2),
  idgham/ikhfaa between a name's final noon/meem and the next name's first
  letter, boundary-dependent qalqala on صٓ's *d* (kubrā when stopped),
  tafkheem on the heavy names — plus two
  narration exceptions (يسٓ and نٓ keep a clear noon before a following waw).
- The final expanded name remains connected to the following Qurʾānic word
  unless the selected boundary stops. This exposes continued طسٓ→تِلْكَ
  ikhfāʾ and the special connected Āl ʿImrān الم→اللَّهُ realization.
- The shared spellings cover fourteen names and fourteen compact resource
  forms at thirty source locations across 29 surah openings; only demonstrated
  boundary/location exceptions are per-location facts.

### 5.12 Per-location exceptions (Hafs closed lists)

- **Imala** (vowel bent toward *e*): exactly one word, مَجۡر۪ىٰهَا 11:41.
- **Tasheel** (softened hamza): exactly one word, ءَا۬عۡجَمِيٌّ 41:44.
- Madd-lazim overrides (10:51, 10:91), natural-madd overrides (11:41, 2:72),
  hamza-wasl irregular verbs (7:38, 9:38), started-on ٱئۡتُونِى (helping long
  *ii* seat), mini-noon ikhfaa (21:88), stop-specific pronoun drop (27:36).
- These are the domain's escape hatch: a finite table of
  (location, context, override) facts, where context ∈ {always, when
  starting, when stopping}.

---

## 6. Cross-word phenomena (summary)

Rules that reach across the space between words when joined:

- all noon-sakinah/tanween rules (§5.1) — including the *merger* variants
  where the sound physically lives on the next word's first letter;
- meem sakinah rules (§5.2);
- consonant idgham pairs (§5.3);
- madd jaiz munfasil (§5.6) — the trigger hamza is next word's first sound;
- hamza-wasl iltiqaa (§5.7) — the repair lands on the *previous* word;
- Allah-lam heaviness (§5.5) — conditioned by the previous word's last vowel.

A cross-word merger means one *sound* is jointly owned by graphemes in two
different words. Any model must represent that sharing.

---

## 7. What changes at a stop (waqf) — consolidated

On the stopped-on word:

1. Final full vowel → **sukun** (with rawm/ishmam as performance variants).
2. Final **fathatan** → long *aa* on the companion alef (**madd 'iwad**);
   final dammatan/kasratan → dropped.
3. Final **taa marbuta** → *h* (tanween drops silently).
4. Final **hamza + fathatan** → hamza + fatha + inserted alef madd.
5. Waqf sukun creates: **qalqala kubra/akbar**, **madd 'arid lil-sukoon**,
   **madd leen**.
6. **Silah** mini waw/yaa drops. The rectangular-zero alef *sounds*.
7. **Munfasil** madd reverts to natural; all cross-word rules with the next
   word are cancelled (noon/meem/idgham → izhar; the next word's initial
   shaddah is only dropped if it is *started* on).
8. Final raa heaviness is re-decided (§5.5).
9. Word-final ى/و/ي role may flip (§5.8).

On a started-on word (ibtidaa):

1. Hamza al-wasl sounds with its grammatical vowel (§5.7).
2. Word-initial (idgham-trace) shaddah is dropped.
3. Rasm-driven start repairs (ٱئۡتُونِى → *iituunii*, etc. — per-location).

---

## 8. Invariants

1. **Tanween is word-final** and is always "short vowel + noon"; every
   noon-sakinah rule has a tanween twin.
2. **Exactly one rule of a family fires per trigger** — each family's
   decision table (e.g. noon/tanween) is exhaustive and its conditions are
   mutually exclusive, so no priority or evaluation order is needed.
3. **Every written grapheme either sounds at its own position, or is silent
   with a reason** (a named rule or orthographic convention) — and the set of
   silent graphemes is a function of the boundary state.
4. **Every sound is attributable**: to a grapheme, to a shared grapheme group
   (long vowels, geminates, cross-word mergers), or to a named insertion rule.
5. **The three renditions** (wasl/waqf/ibtidaa) of a word differ only by the
   closed transform set of §7 — everything else is stable.
6. **Location-specific behaviour is a closed, finite table**, never open-ended
   computation.
7. Madd classification depends only on: what follows the long vowel (hamza /
   permanent sukun / waqf sukun / nothing), whether that is in the same word,
   and the boundary state — plus the closed override table.
8. The rules are ordered by dependency, not simultaneous: assimilation and
   silencing decide *which* sounds exist; lengthening/madd classification then
   reads the resulting sound stream; colouring (tafkheem/ghunnah quality)
   reads the letters around it. (This ordering is what makes "sound stream"
   conditioning in §3.7 well-defined.)

---

## 9. What may vary by riwāyah (not a storage mandate)

The same broad phenomena recur across riwāyāt, but their conditions,
realizations, and source orthographies may differ. This does **not** imply that
all domain knowledge belongs in data files. Algorithms stay in shared/riwāyah
Python; only corpora, script inventories, finite tables, token choices, and
true exception lists are candidates for resources.

Candidate Warsh-vs-Hafs delta classes to verify are:

- **Conditions and closed lists**: madd classifications/choices, contextual
  locations, and special words. Duration choices are research context, not
  fields in the phonemizer result.
- **Riwāyah-specific algorithms**: imālah/taqlīl, tashīl/ibdāl, naql, and
  any interactions established by the linguistic delta matrix.
- **Different orthography**: different rasm, different diacritic conventions,
  different otiose letters, possibly different verse/word segmentation.
- **Different phoneme inventory**: new vowel qualities (imala *e*), and
  possibly different choices for the rule phonemes (ikhfaa nasal, etc.).

The riwāyah-independent seam is narrower: exact source graphemes normalize to
canonical letter units; typed sound segments align back to those graphemes;
named tajwīd/madd occurrences record their participants. The model does not
encode a universal generic effect vocabulary.
