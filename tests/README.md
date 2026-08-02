# The test suite

One file per rule. A file is named for the rule it owns and holds every letter
and every path that rule admits, read at every junction that changes it.

## Layout

| Path | Holds |
| --- | --- |
| `support/` | `Site`, `for_each_riwayah`, `reading` — the only way a test reaches the engine |
| `nasal/` | what a quiescent noon, a tanween and a quiescent meem do to what follows |
| `adjacent/` | a rule read across two touching letters: the four idgham, and the article lam |
| `tafkheem/` | heaviness — the istilaa letters, the divine name's lam, and raa |
| `waqf/` | what a stop does: pausal sukun, iwad, taa marbuta, silah, the pausal alifs, final glides |
| `boundary/` | what a start or a join does: hamzat al-wasl, iltiqa, ibdal |
| `rasm/` | letters the script writes and the reading never says |
| `test_madd.py` | the six lengths, one file — see *Why madd is one file* below |
| `test_qalqala.py` | five letters across three degrees, one file |
| `test_muqattaat.py` | the fourteen openings |
| `test_khilaf.py` | the documented points of legitimate disagreement |
| `test_one_offs.py` | phenomena with a single site: imala, ishmam, tashil, sakt, the small noon |
| `laws/` | invariants that hold over the whole corpus, not over one site |
| `schema/` | what the loaders must reject |

A folder exists only when it holds more than one file. Everything else is a
file at the top.

## Writing a case

```python
BISMI_ALLAHI = Site(hafs=("1:1", (1, 2)))


@for_each_riwayah(BISMI_ALLAHI, ibtidaa=1, waqf=2)
def test_a_prosthetic_hamza_drops_when_the_word_before_it_joins(r):
    # بِسْمِ ٱللَّهِ
    assert r.phonemes(1) == "bismi"
    assert r.phonemes(2) == "lla:h"
```

- **The site keys its address per riwayah.** Word indices are riwayah data, so
  adding a transmission is a row on the `Site`, not a restructure.
- **Boundary state is an argument**, never arithmetic in the test:
  `isolated=N` starts on a word and stops on it, `ibtidaa=a, waqf=b` starts on
  `a` and stops after `b`, `ibtidaa=a, wasl=a` starts on `a` and joins it
  forward. A verse-final word may join: the next verse is supplied as its right
  context.
- **Every site is started on.** A case that begins mid-verse reads as a
  fragment, and the prosthetic hamza it opens with goes silent for no reason
  the file gives.
- **A one-word case is only allowed when one word is the whole story.** If the
  reading depends on what follows — a tanween that merges, a hamza that elides,
  a vowel that shortens at the seam — the neighbour belongs in the site and in
  the assertions. A reader must see *why* the value is right without opening
  the corpus.
- **One comment per test: the Arabic.** No docstrings. The test name is the
  sentence.

## Tests that fail on purpose

A test asserts the **correct** reading, not the one the engine produces today.
Where the two differ the test fails, and that failure is the record of the bug.
Such a test is marked `@pytest.mark.engine_bug` and carries a second comment
naming what the engine currently emits.

```
python -m pytest -m engine_bug        # just the known-wrong readings
python -m pytest -m "not engine_bug"  # what should be green
```

Currently recorded:

| Where | Correct | Engine today |
| --- | --- | --- |
| The seven pausal alifs joined forward — `waqf/test_seven_alifs.py` | short: `ʔana`, `ʔassabi:la`, … | long at either junction |
| `أَمِ ٱرْتَابُوٓا۟` joined — `tafkheem/test_raa.py` | `rˤta:bu:`, heavy | `rta:bu:`, light |
| `مَنْ ۜ رَاقٍ` — `test_one_offs.py` | the sakt holds the noon clear | the noon merges into the raa |
| `أَثْقَلَت دَّعَوَا` — `adjacent/test_mutajanisayn_kamil.py` | the taa merges wholly into the daal | the taa is sounded and the daal stays single |
| `ٱلْتَقَى` started on — `boundary/test_hamza_wasl_start.py` | a form eight kasra | the fatha the article takes |

The first two are regressions against the published phonemizer, which reads
them correctly. The mark that distinguishes the two pausal alif families is the
telling case: the engine handles the round zero correctly at both junctions and
does not consult the rectangular one at all.

## Why madd is one file

The six madd differ in length, and length is one token whatever produces it —
the model stores no duration. Six files could asserts only that a long vowel is
long, six times over. What is visible is the junction, and that is what the
file tests. When duration reaches the phoneme layer this becomes a folder.

## Still to do

**Rules are not asserted anywhere yet.** `source_of`, `host_of`,
`rules_on_char` and `rules_on_sound` raise until the projection settles which
unit a rule is read against. Every file below will gain rule assertions at that
point; the sites are already chosen to carry them.

| Where | What it still needs |
| --- | --- |
| `nasal/` | the remaining izhar shafawi letters; noon and tanween in the scripts other than Uthmani |
| `adjacent/` | mutajanisayn across the remaining articulation pairs; the article lam under a second riwayah |
| `tafkheem/` | whether a heavy letter should colour a damma, not only a fatha and an alif |
| `waqf/` | the stop signs themselves — which stops the mushaf marks, and what each permits |
| `boundary/` | sakt as a junction of its own; iltiqa where the repair inserts rather than shortens |
| `rasm/` | the remaining otiose letters, and whether a carrier of length counts as silent |
| `test_khilaf.py` | the khilaf beyond raa tafkheem once more are declared |
| `laws/` | these still import helpers from `conftest.py` and predate `Site`; they should move onto it |

Waiting on: the projection, for rule assertions; a second packaged riwayah, for
the `Site` rows that are already declared but skipped; duration in the phoneme
layer, for madd to become a folder.
