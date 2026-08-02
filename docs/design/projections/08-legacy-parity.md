# 08 - Parity with the shipped cell schema

Status: **proposed**. Scope: Uthmani, Hafs.

There is a consumer already in production drawing per-character cells against
recitation timings, and it is the reason `character_phoneme_mappings` exists.
This document reads its shipped data against
[01-contract](01-contract.md) and answers one question: can that view be drawn
from `Mappings`. Nothing here proposes a field; the answer is a derivation per
column.

---

## 1. What the consumer receives

A timestamp shard carries, per word, a letter tier, a phoneme tier and a
**cell** tier. A cell is one row of nine positional slots:

| Slot | Name | Holds |
|---|---|---|
| 0 | `chars` | the source character or characters, empty when nothing wrote it |
| 1 | `role` | `base` · `haraka` · `tanween` · `madd` |
| 2 | `status` | `present` · `inserted` · `dropped` · `replaced` · `shortened` |
| 3 | `phoneme_indices` | into the word's phoneme tier, empty when the cell makes no sound |
| 4 | `source_letter_index` | the letter the cell sits on |
| 5 | `tag` | one rule key |
| 6 | `share_group` | cells with one id light together |
| 7 | `phoneme_rule_tags` | one rule key per phoneme, on a muqattaat cell |
| 8 | `secondary_tags` | the rules slot 5 could not hold |

The client draws one text, the source, and decorates it. There is no recited
string in the shard: the mini meem of an iqlab, the open and closed forms of a
tanween and every placement decision are computed in the client from `tag` and
`chars`.

Two of the nine slots exist because an earlier one could not say enough. Slot 5
holds one rule, so slot 8 was added for the rest of them; the cell of a
disjoined-letter opening owns a whole letter name, so slot 7 was added to reach
inside it. `Pairing.rules` is a list and a spelled name's units are published,
so neither has anything to add here.

---

## 2. Column by column

| Slot | Read from |
|---|---|
| `chars` | the pairing's glyphs, under `grouping="glyph"` |
| `role` | `Glyph.kind`, which is finer and folds onto the four |
| `status` | section 3 |
| `phoneme_indices` | `sounds` and `shares` together |
| `source_letter_index` | the unit a `Supplies` edge names, and `Glyph.word_index` |
| `tag`, `secondary_tags` | `rules`, which does not rank them |
| `share_group` | section 4 |
| `phoneme_rule_tags` | the units of the spelled name, each with its own rules |

**The shard's cell is one scalar and its renderer's group is a letter.** The
shard splits a haraka from its letter and fuses a shadda into it, so its row
for the meem of مُّبِينٍ is `مّ`; that is `grouping="glyph"` with the shadda
folded back onto the base it decorates, which is one rule and the only place
the two shapes part. The renderer then groups those rows again, and what it
groups them into is `grouping="cell"`. The two levels are the two the contract
publishes, and the shard is the lower one because it is a transport.

---

## 3. The five statuses

`status` is one column and four different facts, which is why it is the only
column that does not map to a field.

| Status | Read from | Distinguished by |
|---|---|---|
| `present` | the pairing owns or shares a sound | - |
| `dropped` | the glyph is in `silent` | - |
| `inserted` | the pairing is a gap pairing, `after` placing it | - |
| `shortened` | the glyph is in `silent` under `iltiqa_shortening` | the rule |
| `replaced` | the pairing owns a sound and its block's recited side differs | the block |

`dropped` and `shortened` are one thing to this contract and two to the shard,
and the rule that silenced the glyph is what tells them apart -- which is what
the client does with them anyway, since it reads `tag` before it decides what
to draw. `replaced` is the fathatan seat that sounds only at a stop, and it is
a fact about the two texts rather than about the glyph, so `respelling` is
where it is.

The client's own code reads two of the five. Silence is
`status == "dropped"`, an insertion is `status == "inserted"` or an iwad tag,
and the other two reach the screen through `tag` and through an empty
`phoneme_indices`. So the derivations that have to be exact are the two the
contract answers with a field.

---

## 4. The share group, and the animation unit

A long vowel is written twice, once as a haraka and once as the letter that
carries it, and both cells hold the same phoneme index and one `share_group`
so a client lights them together. A cross-word idgham does the same across the
boundary: the tanween of وَكِتَابٍ and the meem of مُّبِينٍ share a group.

`sounds` and `shares` are that, with the ownership question answered. The
group is the set of pairings naming one sound in either list, so no id is
needed and no client has to union anything; and section 6.1 says which of them
owns it, which the shard leaves to whoever reads it. A client that wants the
id keeps the sound's index and has exactly the shipped behaviour.

**The animation unit is the cell, and the renderer already agrees.** Its
groups are `base`, a consonant with the short haraka that vowels it, and
`vowel`, the haraka with the carrier it pairs with, and its own comment says
the base of a long vowel renders separately. That is
[01-contract](01-contract.md) section 6.4 clause for clause: `مَا` is `م` then
`َا`, and `ءَايَـٰتُ` is `ي` then `َٰ`.

This is why `glyph` is the wrong grouping to hand a renderer. A font colours a
letter, a haraka does not highlight on its own and a maddah does not animate
on its own; `glyph` is one row per scalar and asks the client to fold. A client
animating inside a disjoined-letter opening still reads the units, which are
ordered and are what the shard's slot 7 was added to reach.

The shipped data agrees on where a dagger belongs and on the one place a mark
must not fuse. Its cells for the seat of وَنَادَىٰ are `ىٰ` and the fatha
before it under one share group, and for ءَايَـٰتُ the dagger alone with its
fatha the same way -- in both, the mark and its quality are one thing and the
letter they follow is another. Fusing the mark into the letter, which is what a
font-shaping cluster does, would put a long vowel and the consonant before it
in one animation frame.

---

## 5. Where the shard is behind, and where the contract is

The one place the shard is the better record is the disjoined-letter opening
noon. Its data says the noon of طسٓ is plain and the noon of نٓ is plain, and
the package this contract is written against hums the first into تِلْكَ and
merges the second into وَٱلْقَلَمِ. [07-rules](07-rules.md) section 2.1 states
the law and [01-contract](01-contract.md) section 8 checks it.

The one place parity is not wanted is the shadda a started-on word keeps. A
word whose first letter carries the trace of the previous word's idgham is not
said doubled when recitation begins there, and the shard's cell keeps the
shadda anyway; that is a defect of the cells and not behaviour to reproduce.
The recited text drops it, which is
[06-two-texts](06-two-texts.md) row 9.

Three things the contract publishes that the shard cannot.

- **A release is a sound.** The shard's `Q` is a rendering artefact with no
  slot of its own, so a client keeps a second index space with the releases
  taken out and a rule tag has to be walked one place forward to reach the
  bounce it belongs to. Here a qalqala is a `Sound` with a kind, hosted beside
  the consonant, and there is one index space.
- **Rules are a list.** The shard picks one and carries the remainder in a
  slot added later, so a heavy madd is a primary and a secondary. Here the
  pairing names all of them and no rule is more primary than another.
- **The recited text is a text.** The shard has cell statuses, and every
  question about what recitation writes is answered in the client from `tag`
  and `chars`. Here `rendered` is a second array a client concatenates, and
  [06-two-texts](06-two-texts.md) is the whole of the relationship.

Nothing the shard carries is unreachable, and the two columns a client
actually branches on are the two with a field behind them.

---

## 6. The flat mapping, and which way a silence merges

`letter_phoneme_mappings` is the other shipped consumer and it asks a question
the cells do not: **it never emits a soundless row.** Every entry has at least
one phoneme, so a glyph the reading silences is folded into a neighbour and the
consumer highlighting a row always has something to hear.

Its sounding rows are the cell grouping. A letter is bare and the mark that
carries its length is the row after it -- `م` then `آ`, `ه` then `ۥ`, `ت` then
`ٰ`, `ف` then `ي` -- and a disjoined-letter opening is one row per name. The
one difference is the characters: a flat entry drops the harakat and keeps the
letters, where a cell keeps what is written.

So the flat mapping is the cell grouping with the soundless cells folded, and
the fold is the only thing a consumer needs that is not already a field.

| The silenced glyph | Merges |
|---|---|
| shares a sound | forward, into the pairing that owns it |
| shares nothing | backward, into the pairing before it |
| shares nothing, and is first in its word | forward |

Forward is every assimilation and the elided seat: the article lam into its sun
letter, an idgham source into its host, and into the next word where the host
is there. Backward is `orthographic_silence`: the alif of the plural waw, the
seat under a tanween at a join, the otiose alif. The third row is the wasl
hamza, which is word-initial by definition and so has nothing behind it to join;
it needs no rule of its own, because a glyph with nothing before it in its word
has one direction available.

A forward merge across a boundary carries the space, and the shipped rows show
it: the baa of ٱرْكَب and the meem of مَّعَنَا are one entry whose characters
are `ب م`.

**This is what makes the highlighting the same.** A consumer wanting the flat
rows walks the cells, and where one is `silent` it reads `shares` for the
direction; a consumer wanting to light the silent glyph on its own has the cell
the flat mapping folded away, which the flat mapping cannot give back.
