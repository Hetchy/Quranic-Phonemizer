# Hafs script sources

Two orthographies of the **same riwayah**, word-aligned slot for slot. They
exist so that script independence is a testable property rather than a design
claim: the same recitation written two ways must produce the same phonemes.

| Script | Slots | Distinct scalars | Shipped |
|---|---:|---:|---|
| `uthmani/quran.json` | 77,433 | 69 | yes — source of the packaged `quran_db.bin` |
| `indopak/quran.json` | 77,433 | 85 | no — alignment fixture only |

Only Uthmani builds the runtime corpus. `tools/build_hafs_corpus.py` refuses to
overwrite the packaged binary from any other script; pass `--output-dir` to
build one elsewhere.

## Uthmani

The long-standing source. Unchanged by the IndoPak import beyond moving one
directory level down.

## IndoPak

Imported from the Digital Khatt IndoPak text via
`tools/import_indopak_source.py`, which applies exactly two structural changes
and then validates the result against `surah_info.json`:

1. **Verse markers dropped.** Upstream carries 83,668 slots because every ayah
   ends with a U+06DD end-of-ayah token plus Arabic-Indic digits. That token is
   a marker, not a recited word.
2. **37:130 split.** Upstream writes `اِلْيَاسِيْنَ` as one word; Uthmani splits
   it into `إِلْ` + `يَاسِينَ`. The importer splits at the sukun boundary and
   verifies the boundary really is a sukun before doing so.

After both, 6,236 of 6,236 ayahs match Uthmani word-for-word.

### Why this pair is a useful adversary

The two scripts disagree in ways that break any rule reading source glyphs
directly rather than canonical state:

| Fact | Uthmani | IndoPak |
|---|---|---|
| hamzat al-wasl | `ٱ` U+0671 ×**13,483** | ×**1** (only 3:78:23) |
| hamza seats | precomposed `أ إ ؤ ئ` | combining hamza on a bare seat |
| silah waw | `ۥ` U+06E5 ×1257 | `ٗ` U+0657 ×1257 |
| madd sign | `ٓ` U+0653 | `࢜` U+089C |
| iqlab | not marked at all | `ۢ` U+06E2 ×492, `ۭ` U+06ED ×54 |
| always-silent | `۟` U+06DF ×3,970 | ×26 |
| waqf signs | `ۖ ۗ ۚ ۘ ۙ ۛ` | a different set, `ؕ ࢵ ࢶ ࢷ ࢹ` |
| sakt | `ۜ` at 5 sites | `ࣝ` U+08DD at 3 of those 5, plus 4 elsewhere |
| seen/sad khilaf | `ۜ` ×2 and `ۣ` ×1 | `ۜ` ×4 — includes 88:22:3, unmarked in Uthmani |
| imala 11:41, tashil 41:44 | typed marks `۪` and `۬` | one generic "noted here" flag, `ؔ` U+0614 |
| ishmam 12:11, seven alifs ×66 | typed marks | absent |
| 2:72 ornamental dagger alef | present | resolved to a plain hamza |

`ࢵ` U+08D5 is an ordinary IndoPak waqf sign (95 sites), not a khilaf marker.

Consequences the internal model has to answer for:

- A mark's meaning is **script-scoped**, and coverage is asymmetric in both
  directions. Neither script is a superset of the other.
- **Polysemy is structural, not an Uthmani quirk.** Uthmani `ۜ` means sakt or
  seen-khilaf depending on site; IndoPak `ࣝ` means sakt or word-final waqf.
  The sakt inventory is authoritative in neither.
- Some per-location facts exist in one script and not the other, so a location
  table has to be able to supply what a script under-specifies, with a present
  mark used to validate rather than to drive. The 2:72 case shows that an
  exception's scope key is `riwayah x script`, not riwayah alone.
- **Supplying what a script omits is mostly rules, not rows.** 89% of the
  13,482 waṣl sites are the article and 92% of the 3,970 always-silent sites
  are the otiose alef after word-final wāw; the remainder reduces to a
  ~526-entry canonical skeleton lexicon plus a few dozen one-offs. See
  `research/evidence/internal-model-redesign.md` §3b. A location table growing
  to 10⁴ entries means a rule is missing.

Sanity check worth knowing: IndoPak writes 3:1 as `ال࢜مَّ࢜` — with the fatha on
the meem that the connected reading of `الٓمٓ ٱللَّهُ` requires, and which the
current engine does not produce. 2:1 has no such fatha. The second script
independently confirms the expected output.
