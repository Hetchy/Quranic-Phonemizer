# The test suite

One file per rule, named for the rule it owns, holding every letter and every
junction that rule admits.

## Writing a case

```python
BISMI_ALLAHI = Site(hafs=("1:1", (1, 2)))


@for_each_riwayah(BISMI_ALLAHI, ibtidaa=1, waqf=2)
def test_a_prosthetic_hamza_drops_when_the_word_before_it_joins(r):
    # بِسْمِ ٱللَّهِ
    assert r.phonemes(1) == "bismi"
    assert r.phonemes(2) == "lla:h"
```

### Site

`Site(hafs=("1:1", (1, 2)))` — the address of the case, per riwayah.

- `"1:1"` is `surah:ayah`.
- `(1, 2)` are the word numbers within that verse, counting from 1.
- One keyword per riwayah (`hafs=`, `warsh=`), because the same words take
  different word numbers under a different transmission. A riwayah the build
  does not ship is skipped, not failed.

`r.phonemes(n)` and `r.silent(n)` take those same word numbers. When a plan
reads past the end of a verse the next verse continues the numbering, so
`r.phonemes(n + 1)` is the word after the last one.

### Junctions

The boundary keyword says what happens around the word. All of them start on
the first word of the site.

| Keyword | Meaning |
| --- | --- |
| `isolated=n` | started on and stopped on — the word alone |
| `ibtidaa=a, waqf=b` | start on `a`, join through, stop after `b` |
| `ibtidaa=a, wasl=a` | start on `a` and join it forward |

- **ibtidaa** — starting a reading on this word.
- **waqf** — stopping on it.
- **wasl** — joining it to what follows. On a verse-final word this reads the
  next verse into the same score, so a rule can cross the seam.

### Conventions

- Site constants in CAPS at the top of the file.
- No docstrings on tests. One comment per test: the Arabic, every word of it.
- A one-word case only when one word is the whole story. If the reading depends
  on a neighbour — a tanween that merges, a hamza that elides, a vowel that
  shortens — the neighbour goes in the site and in the assertions.
- Either a parametrized table or named tests for a group of cases, never both
  over the same sites.

## Tests that fail on purpose

A test says what the reading **should** be. Where the engine disagrees the test
fails, and that failure is the record of the bug. Mark it
`@pytest.mark.engine_bug` with one comment saying in plain words what the engine
does instead — no phoneme strings, the comment lint allows only Arabic script as
non-ASCII.

```
python -m pytest -m engine_bug   # just the known-wrong readings
python -m pytest --runslow       # plus the corpus-wide parity floors
```

CI runs the whole suite and a marked test fails it. Never change a correct
expectation to match the engine. The mark comes off when the engine agrees, not
the expectation.

## Layout

| Path | Holds |
| --- | --- |
| `support/` | `Site`, `for_each_riwayah`, `reading` |
| `nasal/` | quiescent noon, tanween, quiescent meem |
| `adjacent/` | a rule across two touching letters: idgham, the article lam |
| `tafkheem/` | the istilaa letters, the divine name's lam, raa |
| `waqf/` | pausal sukun, iwad, taa marbuta, silah, pausal alifs, final glides |
| `boundary/` | hamzat al-wasl, iltiqa, ibdal |
| `test_rasm.py` | letters written and never said |
| `test_madd.py`, `test_qalqala.py` | the lengths; the five qalqala letters |
| `test_muqattaat.py`, `test_khilaf.py`, `test_one_offs.py` | as named |
| `laws/` | invariants over the whole corpus, and the parity floors |
| `schema/` | what the loaders must reject |

A folder exists only when it holds more than one file.

### Rule assertions

Every case in a rule file says three things: what the word reads, that the
rule is read off the right character, and that it is read onto the right
sound.

```python
assert r.phonemes(3) == "miŋ"
assert "iqlab" in r.rules_on_char(3, "ن")
assert r.rules_on_sound(3, "ŋ") == {"iqlab"}
```

`rules_on_char` takes `in`, because one character carries several rules at
once -- a qaf is both a qalqalah letter and an istilaa one. `rules_on_sound`
takes `==` where the sound is the rule's own product, and `in` where another
rule colours it. Where a rule does not apply, say so: a stop that undoes a
merger asserts the merger's name is **not** on the character.

Neither reading follows from the phoneme string. `iqlab` is the same name
whether the hum takes a place or not; a letter that merges away carries the
merger's rule and nothing else; `madd_tabii` and `orthographic_silence` name
an outcome and add no sound at all.

`source_of(rule)` and `host_of(rule)` name the character supplying a rule's
source and host unit -- `None` from `host_of` where the rule is not a merger.
Both read the first instance in the whole reading, so prefer
`rules_on_char` when the site is one word of several.

A tanween's rule is read off the mark, not off the letter under it. A table
that sweeps letters asserts the sound; one site per mark asserts the
character.

`laws/` still imports helpers from `conftest.py` and predates `Site`.
