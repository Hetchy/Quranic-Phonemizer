"""Phase 2 — extra candidates beyond bench_db_formats.py.

Adds:
  - orjson_flat: JSON parsed by orjson (C-accelerated)
  - binary_dict: same on-disk file as binary_blob, but eagerly build dict[key, text]
                  (one decode pass at load, then plain dict lookups thereafter)
  - binary_mmap_eager: mmap the file, eager decode -> dict[key, text]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

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

if variant == 'orjson_flat':
    import orjson
    with open(path, 'rb') as f: keys, texts = orjson.loads(f.read())
    db = dict(zip(keys, texts))
    sorted_keys = keys
    lookup = lambda k: db[k]
elif variant == 'binary_dict':
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
    sorted_keys = keys_blob[:-1].split('\n')
    # Eager decode into dict
    db = {}
    for i, k in enumerate(sorted_keys):
        db[k] = text_blob[offsets[i]:offsets[i+1]].decode('utf-8')
    del data, text_blob
    lookup = lambda k: db[k]
elif variant == 'binary_mmap_eager':
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
    db = {}
    for i, k in enumerate(sorted_keys):
        db[k] = mm[text_blob_start + offsets[i] : text_blob_start + offsets[i+1]].decode('utf-8')
    mm.close()
    f.close()
    lookup = lambda k: db[k]
else:
    print(f'unknown variant: {variant}', file=sys.stderr); sys.exit(2)

t_load = time.perf_counter() - t0
gc.collect()
rss_after_load = rss_mb()

random.seed(42)
sample = random.sample(sorted_keys, 1000)
t0 = time.perf_counter()
for k in sample:
    _ = lookup(k)
t_random_lookups = time.perf_counter() - t0

t0 = time.perf_counter()
total_chars = 0
for k in sorted_keys:
    total_chars += len(lookup(k))
t_full_sweep = time.perf_counter() - t0

gc.collect()
rss_after_sweep = rss_mb()

print(json.dumps({
    'variant': variant,
    'rss_after_load_mb': rss_after_load,
    'rss_after_sweep_mb': rss_after_sweep,
    't_load_ms': t_load * 1000,
    't_random1k_ms': t_random_lookups * 1000,
    't_full_sweep_ms': t_full_sweep * 1000,
    'total_chars': total_chars,
}))
"""

CASES = {
    "orjson_flat": "json_flat.json",
    "binary_dict": "binary_blob.bin",
    "binary_mmap_eager": "binary_blob.bin",
}


def main() -> None:
    base = Path("/tmp/quran_formats")
    for name, fname in CASES.items():
        path = base / fname
        out = subprocess.check_output(
            [sys.executable, "-c", DRIVER, name, str(path)], text=True
        )
        rec = json.loads(out.strip())
        size_kb = path.stat().st_size / 1024.0
        print(f"{name:18s}  file={size_kb:7.1f}KB  load={rec['t_load_ms']:7.1f}ms  "
              f"rss_load={rec['rss_after_load_mb']:6.1f}MB  rss_sweep={rec['rss_after_sweep_mb']:6.1f}MB  "
              f"rand1k={rec['t_random1k_ms']:6.2f}ms  fullsweep={rec['t_full_sweep_ms']:7.1f}ms")


if __name__ == "__main__":
    main()
