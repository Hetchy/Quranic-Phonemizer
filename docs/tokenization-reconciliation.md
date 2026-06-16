# Tokenization Reconciliation — tajweed vs letter-phoneme vs the TS shard

For the Timestamps-tab highlight we need to know which grapheme tokenization the
bucket uses and how it lines up with the phonemizer's two tokenizations, so a
silent/sounding classification can be stamped onto the bucket's letters.

Reproduce with `dev/reconcile_tokenization.py [--shard <decompressed-shard.json>]`.

## The three tokenizations

| | atoms | extensions | lafdh jalalah (Allah) | muqattaat | silent letters |
|---|---|---|---|---|---|
| **`tajweed_mappings()`** | per grapheme | split (`ٰ ۥ ۦ`) | **injects a synthetic `ٰ`** for the implicit madd | **spelled out as letter names** (`أَلِف لَام`) | own entry, rule-tagged |
| **`letter_phoneme_mappings()`** | per grapheme of the **actual written text** | split | kept as written (`ٱلله`, no synthetic char) | kept as written (`الٓمٓ`) | **grouped** into the sounding neighbour's entry |
| **bucket TS shard `letters[]`** | per grapheme of the **actual written text** | split | kept as written | kept as written | own `[char,s,e]` entry, **same timespan** as the sounding neighbour |

## Part 1 — tajweed and letter-phoneme atoms diverge (107/114 surahs)

The two phonemizer tokenizations are **not** atom-identical. Across 1-114 they
differ in exactly two constructs:

- **lafdh jalalah** — 2,704 words. `tajweed_mappings()` adds a synthetic dagger
  alef grapheme for Allah's implicit long vowel; `letter_phoneme_mappings()`
  carries the `a:` phoneme with no extra grapheme (Rule-4 exempt).
- **muqattaat** — 30 words. `tajweed_mappings()` returns the spelled-out letter
  names; `letter_phoneme_mappings()` keeps the written disconnected letters.

So a consumer that wants to align against the **written text** must use the
letter-phoneme atoms (or the raw `get_mapping()` graphemes), NOT the tajweed
tokenization.

## Part 2 — the shard matches the letter-phoneme atoms (proven on real data)

On the published Nasser al-Qatami fixture (`reciters/<slug>/timestamps/101.json.gz`),
the shard's per-word `letters[]` char sequence equals the phonemizer's per-word
grapheme sequence (base char + split extensions) **char-for-char**:

```
surah 101: segments 27/27 fully match · words 85/85 match
surah 102: segments 20/20 fully match · words 61/61 match
```

So the **bucket letter tokenization == the letter-phoneme atoms** (per written
grapheme, extensions split) — *not* the tajweed atoms.

## How the shard already encodes the grouping

The shard does not merge silent letters, but it gives a silent letter the **same
`[start,end]` as its sounding neighbour** and emits no dedicated phone for it:

```
مَا ٱلْقَارِعَةُ →  letters ['ٱ',1927,2127] ['ل',1927,2127] …   phones ['l',1927,2127] …
أَدْرَىٰكَ        →  letters ['ى',7250,7700] ['ٰ',7250,7700] …   phones ['aˤ:',7250,7700] …
```

That shared-timespan pair is the FE's "two letters, one cell". It is the shard's
implicit version of the letter-phoneme **grouping** — the sounding grapheme owns
the phone, the silent grapheme rides its span.

## Implication for the silent-tag / phantom-highlight feature

Because the shard atoms equal the letter-phoneme atoms 1:1, the letter-phoneme
silent/sounding classification (`dev/audit_silent_letters.py::pronounced_in_flat`)
maps straight onto the shard `letters[]`:

- For each shard letter, mark it **silent** iff its grapheme is non-sounding in
  the letter-phoneme view (the merged-in graphemes — hamza wasl, lam shamsiyah,
  assimilated noon, the otiose tanween alef, the silah at waqf, …).
- The FE skips highlighting silent-tagged letters; within a shared-timespan
  group only the one sounding grapheme lights up.
- Persist the flag as a 4th slot on the letter triple (`[char,s,e,silent]`) at
  shard-build time (the build path already imports the phonemizer — see
  QUA `qua_shared/timestamps_bridges.py` / `timestamps_pipeline.py`).

**Two cases need the letter-phoneme view, not tajweed** (Part 1): the shard's
Allah and muqattaat letters only line up with the letter-phoneme atoms, so the
silent flags must be derived from `letter_phoneme_mappings()`, never from
`tajweed_mappings()`.

**One genuinely ambiguous case** carries over from the silent-letter audit:
`idgham_shafawi` (مْ+م) has two sounding graphemes sharing one merged nasal — a
highlight convention (recommend the second/target meem) is still needed.

## Can the Inspector infer silence from the shard alone? (No)

Tempting alternative: skip the phonemizer at render time and hard-code a rule
inside the Inspector off the shard's own timing — a silent letter is the one
that shares an exact `[start,end]` with its neighbour (`dev/reconcile_tokenization.py`
Part 3, tested against the phonemizer ground truth on the Nasser fixture):

- **Completeness is fine** — every ground-truth silent grapheme IS duplicate-span
  (0 misses). The signal finds the *cell*.
- **But it cannot pick the sounding member.** 38 *sounding* graphemes also share a
  span and would be wrongly skipped, because the sounding grapheme's position
  inside a duplicate-span group is **not fixed**:
  - silent-prefix clusters → sounding is **last**: `ٱل`, `ٱلن`, `ٱلت` (hamza wasl
    + lam shamsiyah silent, then the sun letter sounds).
  - base + trailing extension → sounding is **first**: `هۥ`, `ىٰ` (the base sounds,
    the silah / dagger rides after it).
  - and the continuing tanween alef (`ـًا`: sound→silent) puts the silent letter
    **after** the sounding one — the opposite of `ٱل`.

No positional rule separates these without re-encoding *which letters are silent*
(hamza wasl, lam shamsiyah, tanween alef, assimilated noon, extensions, …) and
*which phone belongs to which letter* — i.e. re-implementing the phonemizer
inside the Inspector. The duplicate-span structure is also an **aligner
behaviour**, not a guarantee, so depending on it is fragile.

### The reconciliation, by contrast, is trivial

The shard atoms equal the letter-phoneme atoms 1:1 (Part 2), and the shard-build
path already phonemizes each segment for the cross-word bridges. So the silent
flag is computed **once, at build time**, straight from
`letter_phoneme_mappings()` (the phonemizer is the single source of the silence
rules), stamped as a 4th letter slot, and the FE just reads it. No silence logic,
and no token reconciliation, leaks into the Inspector or the FE.

