# What this checkout reads

Not an oracle. `phonemes/` holds the frozen legacy output, which is a different
implementation with known defects and is only ever a change detector. These
files hold what **this** branch reads, so a change can be attributed to the
commit that made it instead of to the whole branch at the end.

```
python tools/snapshot.py diff tests/snapshots/head/word.jsonl.gz /tmp/now.jsonl.gz
```

A unit that means to move output regenerates these in the same commit, and the
diff is what the commit message has to account for. A unit that does not mean
to move output regenerates nothing, and a reviewer running the diff should see
zero.

`word` and `verse` only. `continuous` is quadratic in the length of a reading
and takes far longer than the two gated modes, and no gate floors it.
