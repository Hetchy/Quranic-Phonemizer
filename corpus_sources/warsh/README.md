# Warsh corpus sources

This directory preserves the source material selected for the Warsh reading.
It is not installed with the package.

```text
warsh/
├── fonts/
│   └── uthmanic-warsh.ttf
├── scripts/
│   └── king-fahd/
│       └── quran.json
└── upstream/
    └── king-fahd-v2.json
```

`upstream/king-fahd-v2.json` is the unmodified verse-level input added in
PR #37. It was declared there as King Fahd Complex mushaf data, version 2,
but the PR did not record its upstream URL or license. Its pinned SHA-256 is
`c6017e688cc599d88f6fdb1a19cafc9c51d024b3530955f1a878f17d26b9bcbc`.

`scripts/king-fahd/quran.json` is the normalized word-level source corrected
in PR #57. Regenerate it with:

```bash
python tools/import_warsh_source.py
```

The importer validates the pinned input and Quran order, removes the one
font-dependent presentation-form verse-number glyph from each verse, removes
14 right-to-left marks, and excludes 435 standalone rub-el-hizb markers from
lexical word slots. The expected result is 6,214 verses and 77,425 words.

The font is retained with the corpus material because it covers the source's
codepoints and was used when evaluating the script. It is not runtime data.
Its original download URL and license were not recorded in either PR.
