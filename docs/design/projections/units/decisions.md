# Decisions taken before the work started

`09-open-questions.md` asked what this set had not settled. These are the
answers. Where an answer contradicts the contract, **the answer wins and the
contract is corrected in the unit that implements it** - the register says an
entry implementation closes is struck in the same change.

---

## 1. A hum carries no place. The letter carries it.

Closes open question 1. Item 10 lands **unmodified**: the standalone `Nasal`
type goes, and a hummed consonant is `Consonant(letter, ghunnah=True)`.

Gemination already separates the two noon hums, which is why item 10 says the
notation gains one key:

| written | sound | token |
|---|---|---|
| `أَنتُمْ` ikhfaa, no letter hosts the hum | `Consonant(noon, ghunnah=True)` | `ŋ` |
| `ٱلنَّاسِ` a held noon holding its hum | `Consonant(noon, ghunnah=True, geminate=True)` | `ñ` |
| `ثُمَّ` a held meem holding its hum | `Consonant(meem, ghunnah=True, geminate=True)` | `m̃` |

The two nasal placement points **stay**. `KhilafId.IQLAB_NASAL` and
`KhilafId.IKHFAA_SHAFAWI_NASAL` remain in `available_variants`, and the reading
rides on the letter the rule mints:

| reading | sound | token |
|---|---|---|
| `assimilated`, the default | `Consonant(noon, ghunnah=True)` | `ŋ` |
| `bilabial` | `Consonant(meem, ghunnah=True)` | `m̃` |

For ikhfaa shafawi the source unit is a meem and the default reading publishes a
**noon**-lettered hum. That is what "assimilated, the lips never close" means,
and the attribution edge still names the meem it came from.

`01-contract` section 3.1's "The two nasal placement points are not here" and
section 4.4's "needs no place of articulation" are both wrong and are corrected
by unit A8.

## 2. An eased hamza is a boolean on the consonant.

Closes open question 3. `Consonant` gains `eased: bool`, in exactly the shape
`emphatic` and `ghunnah` already have, and `ipa.yaml` gains
`hamza: {plain: "ʔ", eased: "ʔ̞"}`.

The sound always carries `eased=True` at the site. `extra_phonemes` decides
whether the alphabet honours it or falls back to `ʔ`, which is item 39's
"gated at the notation" and nowhere else. One corpus site, `41:44:9`.

`01-contract` section 9 item 1's "Manner is not published at all" is corrected
by unit A8: `emphatic` and `ghunnah` were already published, and this is a
third of the same kind.

## 3. The cell law names the letter, and tanween is its exception.

Closes open question 4. The tanween mark writes the noon it introduces, which
`canon/build.py` already records as a `LETTER` fact and says so in a comment.

- `01-contract` section 4.2's "a unit no glyph writes" is **wrong** and is
  corrected by unit B2.
- `02-gate` section 4.6's cell law is reworded to name the `letter` fact rather
  than the `consonant` fact, and states tanween as an exception. Unit D3.
- The many-to-many tanween edges stay present rather than collapsed, as
  `02-gate` section 4.2 and `07-rules` section 6 case 2 both already say.
- Every cell table in `03-examples` stands as drawn.

## 4. `main` waits.

`feat/public-projection` branches from `riwayah-agnostic-refactor`, and that
branch reaches `main` only once `Phonemizer` exists. The refactor deleted all 42
legacy modules including the public API, so merging it to `main` today would
publish a release with no public surface at all.

## 5. `Phonemizer()` defaults to hafs and uthmani.

`Phonemizer(riwayah="hafs", script=None, variants=None, extra_phonemes=())`, and
a bare `Phonemizer()` is legal. The PR 50 comment saying riwayah is mandatory is
stale; `01-contract` section 1.1 is right.

## 6. The old projections retire; the composition root does not.

Unit D4 deletes `render/anchored.py` and `render/recite.py`, which
`phonemize/pairing.py` and `phonemize/document.py` replace. `api.recitation()`
stays as the internal composition root that `phonemize/` imports, which is the
layering `02-gate` section 9 anticipates. Every test and tool keeps its
`quranic_phonemizer.api` import.

## 7. The two new tokens.

| toggle | default off gives | on gives |
|---|---|---|
| `tashil` | `ʔ` | `ʔ̞` |
| `emphatic_fatha` | `a` | `aˤ`, which the alphabet already ships |
| `emphatic_ikhfaa` | `ŋ` | `ŋˤ`, a new entry on the noon |
| `qalqala_degree` | `Q` everywhere | `Q` sughra, `QQ` kubra and akbar |

`ŋˤ` reuses the raised ayin the alphabet already carries on `aˤ`, `lˤ` and `rˤ`.
The alphabet raises outright on an emphatic nasal today, so unit A8 adds the
entry as the second half of item 13.

## 8. The corrected `أَنَا۠` refs are allowlisted.

Unit A5 corrects every `أَنَا۠` in the corpus, which is long when joined today and
should be short. `02-gate` section 1 requires those refs be named so the parity
report reports them rather than swallowing them. They go in
`docs/conformance/corrections.md` with the regression test, in the same commit
that moves the floor.
