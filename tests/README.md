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
- One keyword per riwayah (`hafs=`, `warsh=`). The address is riwayah data:
  transmissions divide verses differently, so the same words can take a
  different ayah number as well as different word numbers.

`r.phonemes(n)` and `r.silent(n)` take those same word numbers. When a plan
reads past the end of a verse the next verse continues the numbering, so
`r.phonemes(n + 1)` is the word after the last one.

### Which riwayat a case runs under

`for_each_riwayah` runs the body once per riwayah the site declares **and** the
build ships. So the site's keywords are the whole control:

```python
BOTH = Site(hafs=("2:5", (3, 4)), warsh=("2:5", (3, 4)))   # runs under each
HAFS_ONLY = Site(hafs=("2:5", (3, 4)))                     # runs under Hafs
```

A declared riwayah the build does not package is dropped from the run, not
failed. If that leaves nothing, the case is skipped with a reason rather than
passing silently — so a Warsh-only case is honest on a Hafs-only build.

Declare only the riwayat the case is actually about. A rule that exists in one
transmission and not another belongs in a site naming just that one; do not
declare a riwayah so a row looks complete.

### When the riwayat disagree

Same case, same site, different expected reading — `r.pick` chooses by the
riwayah the body is running under:

```python
MALIK = Site(hafs=("1:4", (1,)), warsh=("1:3", (1,)))


@for_each_riwayah(MALIK, isolated=1)
def test_the_word_is_read_as_each_transmission_has_it(r):
    # مَـٰلِكِ in Hafs, مَلِكِ in Warsh
    assert r.phonemes(1) == r.pick(hafs="ma:lik", warsh="malik")
```

The keywords are riwayah names, matching the site's. A riwayah running but not
named raises `KeyError`, so adding a transmission cannot silently reuse
another's expectation, and the failure names the riwayah that has no answer.

Note the two addresses. Warsh does not count the basmala as a verse of
al-Fatiha, so the same word sits at a different ayah number, and it is written
differently as well as read differently. That is why a site keys its whole
address per riwayah instead of sharing one and varying the expectation: by the
time the readings disagree, the words they belong to may not even be in the
same place.

Fill each value by running that riwayah, never by reasoning about what it
should be. A row written ahead of the build that can read it is a guess wearing
an assertion, and this suite is arranged to prevent exactly that.

Reach for it only where the reading genuinely differs. Where it does not, one
assertion covering every riwayah is the stronger statement, since it says the
transmissions agree. And where the difference is the whole point of the case,
prefer separate tests named for what each transmission does — `pick` is for a
detail inside a shared case, not a way to fold two rules into one body.

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
| `waqf/` | diacritic drops, iwad, taa marbuta, silah, badal, pausal alifs, final glides |
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
source and host unit -- `None` from `host_of` where the rule acted on its own
unit alone.
Both read the first instance in the whole reading, so prefer
`rules_on_char` when the site is one word of several.

A tanween's rule is read off the mark, not off the letter under it. A table
that sweeps letters asserts the sound; one site per mark asserts the
character.

`laws/` still imports helpers from `conftest.py` and predates `Site`.
