# 05 - The brief for a modelling review

You are reviewing whether this design **carves the domain at its joints**. Not
whether its claims are true - five rounds have checked that, and the claims
are true. Every defect this brief is written to catch survived those rounds
because it was consistent with the code, consistent with itself, and wrong.

**Read:** `01-contract`, `02-gate`, `03-examples`, `06-two-texts`,
`07-rules`, plus
`../03-canonical-vocabulary.md` and `../../domain-facts.md`.

**Against:** the sources in section 2, in the order of authority given there.

---

## 1. The rule that makes this review different

**The code agreeing with the document is not evidence that either is right.**

A projection must not be designed to conform to the internal model, and must
not be designed to contradict it. Where the two agree and the shape is still
wrong, both change. Section 9 of `01-contract` is where a model change is
recorded; a finding that ends "and the model does this too" is a finding
about two things, not a defence of one.

The corollary: **do not accept a shape because it is implemented.** The
question is never "does the code do this", it is "is this the right set of
things to say about recitation".

---

## 2. What to check against, and how far to trust it

Four sources, and they do not carry equal weight. When they disagree, the one
higher on this list wins.

| | Source | Trust |
|---|---|---|
| 1 | `corpus_sources/riwayat/hafs/scripts/uthmani/quran.json` | the script text. Ground truth for what is written, full stop |
| 2 | today's phoneme output, from the code at this head | **correct**. If a change would alter a token, the change is wrong |
| 3 | the legacy rules and mappings on `main`, and the frozen baselines under `research/legacy-baselines/` | **almost always right**. A disagreement is usually the model's fault, occasionally legacy's |
| 4 | `../../domain-facts.md` | authoritative guidance, not a constitution |

**On 2.** The token stream is the one thing this project has got right, and it
is the hardest constraint in this review. Any proposed model change - splitting
a type, moving an attribution, deleting a value - must leave every phoneme in
the corpus identical unless you can show the current token is wrong. Run it
both ways and diff. A finding that silently changes output is not a
simplification, it is a regression wearing one's clothes.

This is also what makes shape defects findable. If the tokens are right and
the shape is wrong, the wrongness is entirely in how the facts are arranged -
which is what the defect classes below are for.

**On 3.** Legacy is a coverage reference: it knows about cases the new model
may have dropped, and its rule and mapping vocabulary encodes distinctions
somebody needed. It is not an oracle, and its own manifest says so. Use it to
find what is missing, not to settle what is right.

**On 4.** `domain-facts.md` is the project's record of Hafs and is the first
place to check a domain claim. It is also incomplete, and underspecified in
places: it does not define izhar mutlaq, and its silence on a case is not
evidence the case does not exist. Where it is silent or thin, say so and reach
for a teaching source rather than inferring from the code - the code is where
the questionable shapes live.

**When 2 and 4 disagree**, that is a real finding either way: either the model
is producing a correct token for the wrong reason, or the domain record is
wrong. Say which you think it is and what would settle it.

---

## 3. Rules of evidence

1. Census before arguing. Every enum, every union, every optional field: how
   many members, how many sites each, over the whole corpus in both boundary
   modes. A value with one site is a finding until proven otherwise.
2. No claim without a `file.py:line` or a number you produced.
3. State a confidence and a falsifier per finding.
3a. For any finding that proposes a model change, say what it does to the
   token stream. "No change" is the expected answer and must be shown, not
   asserted.
4. Say what you could not verify, and why.
5. A finding that **removes** a concept outranks one that adds. If you propose
   an addition, name the consumer and what it lets them do today.

---

## 4. The defect classes

Each was found in this design after it had passed a review that checked every
claim. Assume each has more instances.

**D1. More than one axis in one type.** Enum values that are not alternatives
to the same question. *Found:* the consonant's five values answered three
questions - is the letter doubled, does the consonant sound at all, and how is
it articulated. **Test:** name the question each value answers. If there are
two questions, there are two fields.

**D2. A one-member value.** A value with one site is usually a different thing
wearing the type's clothes. *Found:* two of the consonant's five values had a
single site each in the whole corpus. **Test:** census every member. Ask what
would break if it were deleted and its site handled by what it actually is.

**D3. One name, two referents.** *Found:* `silah` named a consonant present
only when joined, and a vowel long only when joined, on two different types
with nothing in common. **Test:** grep each domain term across the model. Two
hits on two types is a finding unless they are the same fact.

**D4. A product wearing a sum's clothes.** N named variants that are a small
cross-product of independent fields. *Found:* five vowel variants were two
fields, each `absent | short | long`. **Test:** tabulate the variants as a
grid. If the grid reads cleanly, the variants were rows. Distinguish cells
that are *impossible* from cells merely *unattested* - the second is data, the
first is a law.

**D5. A sum wearing a product's clothes.** Independent booleans encoding a
closed set, admitting a state that cannot exist. *Found:* two booleans that
were one field with three values, whose fourth combination was meaningless.
**Test:** for every pair of booleans on a type, is every combination real?

**D6. A bag.** A field that groups by where a value came from rather than what
it means, so a reader must classify before reading. *Found:* an envelope
holding transmission, script, notation, schema version and a digest, on the
theory that some were infrastructure. **Test:** can you name the grouping
without using the words "internal", "metadata" or "provenance"?

**D7. Speculative generality.** A field, parameter or policy with one possible
value and no named consumer for a second. *Found:* a notation field, with one
notation shipped. **Test:** what breaks today if it is deleted? If nothing,
it is added when a second value exists.

**D8. A missing relationship.** *Found:* the design named four things a
consumer wants - script, recited text, sound, rules - and served five of their
six pairings through one method, leaving the sixth reachable only by walking a
field. **Test:** list the entities. List every pair. For each, name the call.

**D9. A borrowed name.** Vocabulary from a neighbouring field that describes a
different object, or engineering vocabulary in a domain register. *Found:*
onset and nucleus, which are parts of a syllable, for the parts of a unit,
which is not a syllable; `repair` for a tajweed phenomenon; `row` and `cell`
for a domain pairing. **Test:** would a teacher of tajweed recognise the word
as naming this thing?

**D10. A policy explained in prose.** A paragraph describing how something is
decided has cases, and prose hides the ones it does not mention. *Found:*
which unit hosts a merged sound, argued in a paragraph, when it is a table
with one row per merging rule. **Test:** for every "usually", "except" or
"the relevant" in the documents, produce the full table.

**D11. A derivation described rather than published.** If a consumer must
rebuild a label from a paragraph, they will rebuild it differently.

**D12. Cardinality never stated.** *Found:* the unit's own fields - can both
be absent, can neither, is a unit ever a grapheme cluster - answered nowhere.
**Test:** for every type, state whether each field is optional, what the full
value set is, and which combinations are impossible.

**D13. A domain claim that is merely plausible.** A statement about recitation
that reads well and is not what Hafs does. **Test:** check it against
`domain-facts.md` and against a teaching source. Do not assume a term means
what its English calque suggests.

---

## 5. Method

Do these before forming an opinion.

0. **Baseline the tokens.** Dump every phoneme in the corpus, both boundary
   modes, before you touch anything. That file is what every proposed change
   is diffed against.
1. **Census.** Every enum member, union variant and optional field, over the
   whole corpus, in joined and stopped modes. Report the distribution.
2. **Grid every union.** Two axes if you can find them. Mark each cell
   impossible, unattested, or populated.
3. **Pair every entity.** Script, recited text, unit, sound, rule, word. For
   each pair, name the call that answers it or record that none does.
4. **Walk one real screen.** Take a consumer that exists - a timestamps
   viewer, a teleprompter, a tajweed-coloured mushaf - and build it from the
   published surface only. Name what is missing or awkward.
5. **Read the names aloud in the domain.** For each public name, ask whether
   it is the word the domain uses, a calque, or an engineering import.

---

## 6. What is settled

Owner decisions. Challenge only with evidence unavailable when they were
made - a measurement, a code path, a named consumer.

- Two projections, `phonemes` and the graph; one document, no profiles.
- `alignment(text=, grouping=)`, its two axes and four values; pairings carry
  both texts; co-highlighting is a field, not a policy.
- No rule family anywhere.
- Teaching labels that describe a configuration are derived, not minted.
- A release is hosted on the consonant, as an addition.
- `is_stopped_on` is true for the last word of a request.
- No counts, statistics or history in the documents.
- ASCII transliteration, no diacritics, no section sign, em dash or curly
  quotes.

Nothing awaits an owner decision today. If a
finding is genuinely a question for the owner, mark it **FOR OWNER**.

---

## 7. Output

1. **Verdict** - one line.
2. **Findings**, ordered by how much they simplify. Each with its evidence,
   the defect class, a confidence and a falsifier. Say for each whether it is
   a document change, a model change, or both.
3. **FOR OWNER.**
4. **What holds** - the shapes you tried to break and could not, so the next
   round does not re-examine them.

Do not restate the documents. Assume the reader wrote them.
