# Phase E - the assertions the suite has been waiting for

Two units. Both need D4, because both ask the graph questions only
`PhonemizeResult` can answer.

---

## E1 - Rules asserted

`tests/README.md` says it plainly under "Still to do":

> Rules are not asserted yet: `source_of`, `host_of`, `rules_on_char` and
> `rules_on_sound` raise until the projection settles which unit a rule is read
> against. Sites are already chosen to carry those assertions.

`tests/support/reading.py` has four stubs raising `RulesPending`. Every test in
the suite asserts phoneme strings and silent characters and nothing about rule
identity, source letter or host letter. The projection has now settled it:
`RuleInstance` carries `rule`, `source`, `host` and `labels`, and `07-rules`
section 6 is where a letter and a sound relate to a rule differently.

**Files:** `tests/support/reading.py` (implement the four accessors against
`PhonemizeResult.rules` and the edge arrays), `tests/README.md` (delete the
"Still to do" paragraph), and rule assertions added to the per-rule files that
were written to carry them.

Also here: `laws/` still imports helpers from `conftest.py` and predates `Site`.
Migrate it.

Two assertions worth writing first, because both are already-known truths that
nothing checks:

- The rule is `iqlab` under either reading of the nasal place. The name cannot
  carry the difference, which is the whole reason
  [decisions.md](decisions.md) section 1 exists.
- An assimilated closure has no qalqala, read off `rules` rather than inferred
  from the token stream.

**Depends on** D4.

## E3 - The optional phonemes, on and off

Four toggles, none of which any test exercises. Each needs both readings at a
real site, in the file that owns the rule:

| toggle | off | on | site |
|---|---|---|---|
| `tashil` | `ʔ` | `ʔ̞` | 41:44:9 `ءَا۬عْجَمِىٌّ`, the only one |
| `emphatic_fatha` | `a` | `aˤ` | any istilaa letter with a fatha |
| `emphatic_ikhfaa` | `ŋ` | `ŋˤ` | an ikhfaa before an istilaa letter |
| `qalqala_degree` | `Q` | `Q` sughra, `QQ` kubra and akbar | all three degrees |

The gate is at the notation, so each test is one reading with
`extra_phonemes=()` and one with the toggle named, at the same site, asserting
two different token strings. A test that asserts only the default has asserted
nothing about the toggle.

`tests/nasal/test_nasal_place.py` is the shape to copy: a table of sites, the
default asserted separately from the selection, and a test that choosing one
point leaves the others alone.

**Depends on** D4, A8.

---

E2, the two nasal placement points, landed before Phase A as
`tests/nasal/test_nasal_place.py`, so that A8 could not remove the type carrying
the choice without a test saying so.
