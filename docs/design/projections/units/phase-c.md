# Phase C - rules with no producer

Four units. Nothing here can start until A4 lands. Then C1 with C4, then C2
with C3. C1 and C2 both rewrite `rules/madd.py`, so they are serial with
respect to each other.

---

## C1 - Split the boundary rules; produce the iltiqa helping vowel

**Items 26, 27. Medium.**

`rules/boundary.py` has one `Rule.WAQF_ENDING` covering four distinct outcomes.
`TanweenAtWaqf` mints either `WAQF_ENDING` or `IWAD`, and `TaaMarbutaAtWaqf`
mints `WAQF_ENDING` with `variant=1` purely to dodge an id collision in the
laws. The contract wants three names: `pausal_sukun`, `taa_marbuta_pausal`, and
`iwad`, which is already its own rule and keeps its name.

Item 26's iltiqa helping vowel is constructed nowhere. It is the vowel of the
unit the reading vowels, a tanween's noon, hosted on a vowel part the canon
leaves absent. `Inserted` exists in the model and no rule uses it.

**Files:** `rules/boundary.py` (**load-bearing**, 272 lines), `rules/madd.py`
`IltiqaRepair` (rename to `iltiqa_shortening`), `model/canon.py` `Rule`,
`riwayat/hafs/rules.py`, `tests/laws/test_rule_coverage.py`.

**Depends on** A2, A4. **Moves** `regression`.

Settles open question 6's first clause: `01-contract` section 7.2's stop effects
are exclusive **per part**, not per unit, which is exactly what `variant=1` is
papering over. `tests/laws/test_rule_coverage.py::test_no_two_rules_claim_the_same_slot_and_aspect`
is the local gate. Correct the contract's wording here.

## C2 - Madd for its ordinary cases; teaching labels derived

**Items 23, 40. Medium.**

`rules/madd.py` `MaddClass` deliberately does not emit `madd_tabii`, so the only
producer is the pausal glide. An ordinary long vowel, a silah vowel and a
stopped seven-alif produce no instance at all, which is why the first three
converse rows of `02-gate` section 4.8 fail today.

Item 40's four teaching labels are computed nowhere. Each is a predicate over
an instance and the unit it names, so they are derived where the instance is
assembled and mint no instance of their own. That places them in the public
package's assembly step, not in `rules/`.

**Files:** `rules/madd.py` (**load-bearing**), `model/canon.py` `Rule`, the
label derivation in `phonemize/labels.py`, `tests/laws/test_rule_coverage.py`.

**Depends on** A4, C1. **Moves** `regression` in instance count only: a flood of
new instances and no new sounds. No token may change, so
`tools/snapshot.py diff` must report zero.

## C3 - `orthographic_silence`, and the two unnamed rules

**Items 24, 25. Medium.**

`canon/derive/lexeme.py` already identifies the seats (`otiose_waw`,
`hamza_seat`, `alif_in_leen`, `otiose_alif`) and `canon/build.py`
`_rasm_outcome` consumes the verdicts, but nothing mints a rule, the field
naming the unit each shows against is written and never read, and one seat class
reaches no spelling edge at all.

It stays **one** rule: a letter never said and a seat silent only when joined
are the same outcome, and the boundary tells them apart without a second name.

Item 25's two rules are mandatory, corpus-wide, and have no name anywhere in the
tree: dropping a word-initial shadda when a word is started on, and the role a
word-final yaa, waw or alif maqsura takes at a pause. They are `06-two-texts`
rows 9 and 29, which is where the transformation each performs is written down.

**Files:** new rule modules under `rules/`, `canon/derive/lexeme.py`,
`canon/build.py`, `model/canon.py` `Rule`, `riwayat/hafs/rules.py`,
`tests/laws/test_rule_coverage.py`.

**Depends on** A2, B1: the verdict must reach a spelling edge. **Moves**
`regression`, `cross-script` and `l1`. Item 25's role flip is a real output
change, so regenerate the head snapshots and record the refs.

## C4 - Mergers keep the host's ghunnah; a spelled name is closed

**Items 28 (the merger half), 30, 31. Small to medium.**

`rules/idgham.py` builds the merged host consonant with no nasal fact. The
corpus has one merger of that family whose host is a nasal letter, 11:42
`ٱرْكَب مَّعَنَا`, held today without a hum. `rules/lam_shamsiyyah.py` already
sets it, so the shape to copy is in the tree.

Item 31: the noon that ends a disjoined-letter opening takes the nasal rules of
the word after it, so `طسٓ` hums into `تِلْكَ` and `نٓ` merges into `وَٱلْقَلَمِ` and
loses its own consonant. A unit whose origin is `muqattaat` neither takes a rule
from another word nor gives one, and the last unit of the last name takes the
plain-articulation rule of its own letter: `izhar` after a noon and
`izhar_shafawi` after a meem, which the meem-final openings need. The rules
between the names of one opening are unaffected.

`rules/noon_sakinah.py` `_between_names` already treats a spelled seam as a
boundary; nothing stops a muqattaat unit taking a rule from the next word.

The three disputed sites are khilaf points rather than exceptions, and wiring
them is out of scope here.

**Files:** `rules/idgham.py`, `rules/noon_sakinah.py`, `rules/meem_sakinah.py`,
`engine/neighbourhood.py` `after`, `riwayat/tables.py`,
`tests/test_muqattaat.py`, `tests/laws/test_minimal_pairs.py`.

**Depends on** A3 (the closure reads `origin`, not family) and A8
(`Consonant.ghunnah`). **Moves** `regression`: 11:42, and every muqattaat-final
noon and meem. Regenerate the head snapshots.
