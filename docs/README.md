# Documents

Where a document lives says what it is for. There is one rule per tree, and a
document moves when its status changes, never for age alone.

| Tree | Holds |
|---|---|
| `docs/` | Maintained references describing the current release. |
| `docs/adr/` | Numbered decision records, and nothing else. |
| `docs/conformance/` | What each gate measures, its current residue, and how to reproduce it. |
| `docs/archive/` | Guidance that was once current and has been replaced. Moved in the same change that lands the replacement. |
| `research/` | Provenance, citations, audits, source notes, generated evidence, completed phase reports. |

The distinction that matters: `docs/` describes what the code does now and is
wrong if the code changes; `research/` records what was found or decided at a
point in time and stays true whatever the code does next.

## Current references

- [projection-redesign.md](projection-redesign.md) — legacy audit, model gaps,
  the two-projection target, and its Uthmani delivery plan.
- [domain-facts.md](domain-facts.md) — the reading facts the package encodes.
- [mualem_conversion.md](mualem_conversion.md) — the Mualem notation mapping.
- [hafs/](hafs/) — the public projections: tajweed, letter-phoneme and
  character-phoneme mappings, and the silent-letter audit.
- [adr/](adr/README.md) — the design, in order.
- [conformance/](conformance/gate-residues.md) — every row behind every gate
  that is short of 100%, and which direction it is wrong in.
