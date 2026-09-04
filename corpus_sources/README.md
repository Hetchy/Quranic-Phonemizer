# Corpus sources

This tree contains editable inputs used to build packaged runtime corpora. It
is not installed with the package.

Each reading is a direct child of this directory:

- `hafs/` contains the Uthmani source and the aligned IndoPak fixture.
- `warsh/` contains its pinned upstream data, normalized source, and font.

Regenerate the packed Hafs Uthmani runtime projection with:

```bash
python tools/build_hafs_corpus.py
```

The builder verifies that the source word count matches
`quranic_phonemizer/data/riwayat/hafs/corpus/surah_info.json` before replacing
the packaged binary.

Warsh is not yet a runtime reading. Its source preparation is documented in
`warsh/README.md` and reproduced by `tools/import_warsh_source.py`.
