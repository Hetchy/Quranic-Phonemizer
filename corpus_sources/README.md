# Corpus sources

This tree contains editable inputs used to build packaged runtime corpora. It
is not installed with the package.

The Hafs source is `riwayat/hafs/quran.json`. Regenerate its packed runtime
projection with:

```bash
python tools/build_hafs_corpus.py
```

The builder verifies that the source word count matches
`quranic_phonemizer/data/riwayat/hafs/corpus/surah_info.json` before replacing
the packaged binary.
