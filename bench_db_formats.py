"""Benchmark candidate Quran-DB storage/load strategies.

Each format defines:
  - path      : on-disk file
  - load_fn   : runs in a fresh subprocess; returns nothing observable, but
                 must construct (lookup, sorted_keys) like the current loader

The bench harness spawns one subprocess per format and measures:
  - file size on disk
  - time to load + build sorted_keys index
  - RSS after load (idle, no queries)
  - time to do 1000 random verse-by-key lookups (to measure access cost)
  - RSS after lookups
  - time to dump all 77433 texts (i.e. resolve every entry)

Run after `build_db_formats.py`.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


FORMATS = {
    # name : (path under /tmp/quran_formats/, snippet variant id)
    "json_full":     "json_full.json",
    "json_slim":     "json_slim.json",
    "json_flat":     "json_flat.json",
    "tsv":           "tsv.tsv",
    "msgpack_dict":  "msgpack_dict.mp",
    "msgpack_flat":  "msgpack_flat.mp",
    "pickle_dict":   "pickle_dict.pkl",
    "pickle_flat":   "pickle_flat.pkl",
    "marshal_flat":  "marshal_flat.bin",
    "binary_blob":   "binary_blob.bin",
    "sqlite":        "quran.sqlite",
    "sqlite_mem":    "quran.sqlite",  # same file, but loaded into :memory:
    "binary_mmap":   "binary_blob.bin",  # same file, but accessed via mmap
}


# Subprocess driver. Each format provides a load() returning (lookup_fn, sorted_keys).
DRIVER = r"""
import sys, time, os, gc, struct, array, json, random, mmap

def rss_mb():
    with open('/proc/self/status') as f:
        for line in f:
            if line.startswith('VmRSS:'):
                return int(line.split()[1]) / 1024.0
    return -1

variant = sys.argv[1]
path = sys.argv[2]
gc.collect()
rss_baseline = rss_mb()

t0 = time.perf_counter()

if variant == 'json_full':
    with open(path) as f: db = json.load(f)
    sorted_keys = sorted(db.keys(), key=lambda k: tuple(int(x) for x in k.split(':')))
    lookup = lambda k: db[k]['text']
elif variant == 'json_slim':
    with open(path) as f: db = json.load(f)
    sorted_keys = sorted(db.keys(), key=lambda k: tuple(int(x) for x in k.split(':')))
    lookup = lambda k: db[k]
elif variant == 'json_flat':
    with open(path) as f: keys, texts = json.load(f)
    db = dict(zip(keys, texts))
    sorted_keys = keys  # already sorted
    lookup = lambda k: db[k]
elif variant == 'tsv':
    db = {}
    sorted_keys = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            k, t = line.rstrip('\n').split('\t', 1)
            db[k] = t
            sorted_keys.append(k)
    lookup = lambda k: db[k]
elif variant == 'msgpack_dict':
    import msgpack
    with open(path, 'rb') as f: db = msgpack.unpackb(f.read(), raw=False, strict_map_key=False)
    sorted_keys = sorted(db.keys(), key=lambda k: tuple(int(x) for x in k.split(':')))
    lookup = lambda k: db[k]
elif variant == 'msgpack_flat':
    import msgpack
    with open(path, 'rb') as f: keys, texts = msgpack.unpackb(f.read(), raw=False)
    db = dict(zip(keys, texts))
    sorted_keys = keys
    lookup = lambda k: db[k]
elif variant == 'pickle_dict':
    import pickle
    with open(path, 'rb') as f: db = pickle.load(f)
    sorted_keys = sorted(db.keys(), key=lambda k: tuple(int(x) for x in k.split(':')))
    lookup = lambda k: db[k]
elif variant == 'pickle_flat':
    import pickle
    with open(path, 'rb') as f: keys, texts = pickle.load(f)
    db = dict(zip(keys, texts))
    sorted_keys = keys
    lookup = lambda k: db[k]
elif variant == 'marshal_flat':
    import marshal
    with open(path, 'rb') as f: keys, texts = marshal.load(f)
    db = dict(zip(keys, texts))
    sorted_keys = keys
    lookup = lambda k: db[k]
elif variant == 'binary_blob':
    with open(path, 'rb') as f: data = f.read()
    n = struct.unpack_from('<I', data, 0)[0]
    offsets_size = (n + 1) * 4
    offsets = array.array('I')
    offsets.frombytes(data[4 : 4 + offsets_size])
    pos = 4 + offsets_size
    text_blob_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
    text_blob = data[pos : pos + text_blob_len]
    pos += text_blob_len
    keys_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
    keys_blob = data[pos : pos + keys_len].decode('ascii')
    sorted_keys = keys_blob[:-1].split('\n')  # strip trailing newline
    key_to_idx = {k: i for i, k in enumerate(sorted_keys)}
    def lookup(k, _b=text_blob, _o=offsets, _i=key_to_idx):
        idx = _i[k]
        return _b[_o[idx]:_o[idx+1]].decode('utf-8')
    del data
elif variant == 'binary_mmap':
    f = open(path, 'rb')
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    n = struct.unpack_from('<I', mm, 0)[0]
    offsets_size = (n + 1) * 4
    offsets = array.array('I')
    offsets.frombytes(bytes(mm[4 : 4 + offsets_size]))
    pos = 4 + offsets_size
    text_blob_len = struct.unpack_from('<I', mm, pos)[0]; pos += 4
    text_blob_start = pos
    pos += text_blob_len
    keys_len = struct.unpack_from('<I', mm, pos)[0]; pos += 4
    keys_blob = bytes(mm[pos : pos + keys_len]).decode('ascii')
    sorted_keys = keys_blob[:-1].split('\n')
    key_to_idx = {k: i for i, k in enumerate(sorted_keys)}
    def lookup(k, _mm=mm, _o=offsets, _b=text_blob_start, _i=key_to_idx):
        idx = _i[k]
        return _mm[_b + _o[idx] : _b + _o[idx+1]].decode('utf-8')
elif variant == 'sqlite':
    import sqlite3
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    sorted_keys = [r[0] for r in cur.execute('SELECT location FROM quran')]
    sorted_keys.sort(key=lambda k: tuple(int(x) for x in k.split(':')))
    def lookup(k, _cur=cur):
        return _cur.execute('SELECT text FROM quran WHERE location=?', (k,)).fetchone()[0]
elif variant == 'sqlite_mem':
    import sqlite3
    src = sqlite3.connect(path)
    conn = sqlite3.connect(':memory:')
    src.backup(conn)
    src.close()
    cur = conn.cursor()
    sorted_keys = [r[0] for r in cur.execute('SELECT location FROM quran')]
    sorted_keys.sort(key=lambda k: tuple(int(x) for x in k.split(':')))
    def lookup(k, _cur=cur):
        return _cur.execute('SELECT text FROM quran WHERE location=?', (k,)).fetchone()[0]
else:
    print(f'unknown variant: {variant}', file=sys.stderr)
    sys.exit(2)

t_load = time.perf_counter() - t0
gc.collect()
rss_after_load = rss_mb()

# 1000 random lookups
random.seed(42)
sample = random.sample(sorted_keys, 1000)
t0 = time.perf_counter()
for k in sample:
    _ = lookup(k)
t_random_lookups = time.perf_counter() - t0

# Full sweep: every entry
t0 = time.perf_counter()
total_chars = 0
for k in sorted_keys:
    total_chars += len(lookup(k))
t_full_sweep = time.perf_counter() - t0

gc.collect()
rss_after_sweep = rss_mb()

print(json.dumps({
    'variant': variant,
    'rss_baseline_mb': rss_baseline,
    'rss_after_load_mb': rss_after_load,
    'rss_after_sweep_mb': rss_after_sweep,
    't_load_ms': t_load * 1000,
    't_random1k_ms': t_random_lookups * 1000,
    't_full_sweep_ms': t_full_sweep * 1000,
    'total_chars': total_chars,
    'n_keys': len(sorted_keys),
}))
"""


def main() -> None:
    base = Path("/tmp/quran_formats")
    rows = []
    for name, fname in FORMATS.items():
        path = base / fname
        if not path.exists():
            print(f"missing {path}; run build_db_formats.py first", file=sys.stderr)
            sys.exit(1)
        size_kb = path.stat().st_size / 1024.0
        out = subprocess.check_output(
            [sys.executable, "-c", DRIVER, name, str(path)], text=True
        )
        rec = json.loads(out.strip())
        rec["file_kb"] = size_kb
        rows.append(rec)
        print(f"{name:14s}  file={size_kb:7.1f}KB  load={rec['t_load_ms']:7.1f}ms  "
              f"rss_load={rec['rss_after_load_mb']:6.1f}MB  rss_sweep={rec['rss_after_sweep_mb']:6.1f}MB  "
              f"rand1k={rec['t_random1k_ms']:6.2f}ms  fullsweep={rec['t_full_sweep_ms']:7.1f}ms")

    print()
    print("Markdown table:")
    print("| format | file (KB) | load (ms) | RSS after load (MB) | RSS after full sweep (MB) | 1000 random lookups (ms) | full sweep all 77k (ms) |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"| {r['variant']} | {r['file_kb']:.1f} | {r['t_load_ms']:.1f} | "
              f"{r['rss_after_load_mb']:.1f} | {r['rss_after_sweep_mb']:.1f} | "
              f"{r['t_random1k_ms']:.2f} | {r['t_full_sweep_ms']:.1f} |")


if __name__ == "__main__":
    main()
