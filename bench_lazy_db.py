"""Bench lazy DB variants — pay-as-you-go alternatives to the current texts loader.

Each variant is run in a fresh subprocess. Three RSS checkpoints:
  1. After Phonemizer-equivalent init (open file + minimal index)
  2. After 100 verse-level random lookups
  3. After full sweep (touches every entry)

Variants:
  - eager_dict      : current behaviour. Reads whole file, builds dict[key, text].
  - lazy_dict       : reads whole file but only builds dict on first access (cached).
  - mmap_index_eager: mmap file. Eager offsets + key→idx dict + sorted_keys.
                      __getitem__ slices mmap and decodes UTF-8.
  - mmap_index_lazy : mmap file. Build verse_start_idx from surah_info (no key→idx
                      dict). Compute idx from key string at lookup time.
                      No eager 77k-entry sorted_keys list.
  - sqlite_disk     : SQLite on disk; SELECT on each lookup.
"""
from __future__ import annotations

import json
import subprocess
import sys

DRIVER = r"""
import sys, os, gc, time, json, struct, array, mmap, sqlite3, random
from pathlib import Path

def rss_mb():
    with open('/proc/self/status') as f:
        for line in f:
            if line.startswith('VmRSS:'):
                return int(line.split()[1]) / 1024.0
    return -1

variant = sys.argv[1]
res = Path('quranic_phonemizer/resources')

gc.collect()
rss_baseline = rss_mb()

# --- INIT (Phonemizer-equivalent open + index build) ---
t_init0 = time.perf_counter()

if variant == 'eager_dict':
    with (res / 'quran_db_texts.json').open(encoding='utf-8') as f:
        texts = json.load(f)
    with (res / 'surah_info.json').open(encoding='utf-8') as f:
        info = json.load(f)
    keys, tuples = [], []
    for s in range(1, 115):
        s_str = str(s)
        for v_idx, v_info in enumerate(info[s_str]['verses'], start=1):
            v = v_idx
            prefix = s_str + ':' + str(v) + ':'
            for w in range(1, v_info['num_words'] + 1):
                keys.append(prefix + str(w))
                tuples.append((s, v, w))
    db = dict(zip(keys, texts))
    sorted_keys, sorted_tuples = keys, tuples
    def lookup(k): return db[k]

elif variant == 'mmap_index_eager':
    f = open(res / 'quran_db_blob.bin', 'rb')
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    n = struct.unpack_from('<I', mm, 0)[0]
    offsets = array.array('I')
    offsets.frombytes(bytes(mm[4 : 4 + (n + 1) * 4]))
    pos = 4 + (n + 1) * 4
    text_blob_len = struct.unpack_from('<I', mm, pos)[0]; pos += 4
    text_blob_start = pos; pos += text_blob_len
    keys_len = struct.unpack_from('<I', mm, pos)[0]; pos += 4
    keys_blob = bytes(mm[pos : pos + keys_len]).decode('ascii').rstrip('\n')
    sorted_keys = keys_blob.split('\n')
    sorted_tuples = [tuple(int(x) for x in k.split(':')) for k in sorted_keys]
    key_to_idx = {k: i for i, k in enumerate(sorted_keys)}
    def lookup(k, _mm=mm, _o=offsets, _b=text_blob_start, _idx=key_to_idx):
        i = _idx[k]
        return _mm[_b + _o[i] : _b + _o[i + 1]].decode('utf-8')

elif variant == 'mmap_index_lazy':
    f = open(res / 'quran_db_blob.bin', 'rb')
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    n = struct.unpack_from('<I', mm, 0)[0]
    offsets = array.array('I')
    offsets.frombytes(bytes(mm[4 : 4 + (n + 1) * 4]))
    pos = 4 + (n + 1) * 4
    text_blob_len = struct.unpack_from('<I', mm, pos)[0]; pos += 4
    text_blob_start = pos
    # Skip keys section entirely. Build verse_start_idx from surah_info.
    with (res / 'surah_info.json').open(encoding='utf-8') as info_f:
        info = json.load(info_f)
    verse_start = {}  # (s, v) -> base idx
    sorted_tuples = []
    sorted_keys = None  # built on demand
    base = 0
    for s in range(1, 115):
        s_str = str(s)
        for v_idx, v_info in enumerate(info[s_str]['verses'], start=1):
            v = v_idx
            verse_start[(s, v)] = base
            nw = v_info['num_words']
            for w in range(1, nw + 1):
                sorted_tuples.append((s, v, w))
            base += nw
    def lookup(k, _mm=mm, _o=offsets, _b=text_blob_start, _vs=verse_start):
        s_str, v_str, w_str = k.split(':', 2)
        i = _vs[(int(s_str), int(v_str))] + int(w_str) - 1
        return _mm[_b + _o[i] : _b + _o[i + 1]].decode('utf-8')

elif variant == 'sqlite_disk':
    # Reads quran.sqlite produced by `build_db_formats.py` (under /tmp/quran_formats/).
    # That script must have been run before this variant.
    sqlite_path = Path('/tmp/quran_formats/quran.sqlite')
    if not sqlite_path.exists():
        raise SystemExit('run build_db_formats.py first to produce ' + str(sqlite_path))
    conn = sqlite3.connect(str(sqlite_path))
    cur = conn.cursor()
    sorted_keys = [r[0] for r in cur.execute('SELECT location FROM quran')]
    sorted_keys.sort(key=lambda k: tuple(int(x) for x in k.split(':')))
    sorted_tuples = [tuple(int(x) for x in k.split(':')) for k in sorted_keys]
    def lookup(k, _cur=cur):
        return _cur.execute('SELECT text FROM quran WHERE location=?', (k,)).fetchone()[0]

else:
    raise SystemExit('unknown variant: ' + variant)

t_init = time.perf_counter() - t_init0
gc.collect()
rss_after_init = rss_mb()

# Generate sample keys deterministically
random.seed(42)
n_total = 77433
all_idxs = list(range(n_total))

# Make sure we have a list of all keys (some variants don't eagerly build sorted_keys)
def all_keys(_st=sorted_tuples, _sk=sorted_keys):
    if _sk is not None:
        return _sk
    return [f'{s}:{v}:{w}' for s, v, w in _st]

# 100 verse-style lookups
verse_keys = [all_keys()[random.randint(0, n_total - 1)] for _ in range(100)]
gc.collect()
rss_before_verse = rss_mb()
t_v0 = time.perf_counter()
for k in verse_keys:
    _ = lookup(k)
t_verse = time.perf_counter() - t_v0
gc.collect()
rss_after_verse = rss_mb()

# Full sweep — touch everything
ks = all_keys()
gc.collect()
rss_before_sweep = rss_mb()
t_s0 = time.perf_counter()
total = 0
for k in ks:
    total += len(lookup(k))
t_sweep = time.perf_counter() - t_s0
gc.collect()
rss_after_sweep = rss_mb()

print(json.dumps({
    'variant': variant,
    'rss_baseline_mb': rss_baseline,
    'rss_after_init_mb': rss_after_init,
    'rss_after_verse_mb': rss_after_verse,
    'rss_after_sweep_mb': rss_after_sweep,
    't_init_ms': t_init * 1000,
    't_100_verse_ms': t_verse * 1000,
    't_full_sweep_ms': t_sweep * 1000,
    'total_chars': total,
}))
"""

VARIANTS = ["eager_dict", "mmap_index_eager", "mmap_index_lazy", "sqlite_disk"]


def main():
    rows = []
    for v in VARIANTS:
        out = subprocess.check_output([sys.executable, "-c", DRIVER, v], text=True)
        rec = json.loads(out.strip())
        rows.append(rec)

    print(f"{'variant':18s}  init  rss_init  rss_verse  rss_sweep  100verse  fullsweep")
    for r in rows:
        print(f"{r['variant']:18s}  {r['t_init_ms']:5.1f}ms  "
              f"{r['rss_after_init_mb']:7.1f}MB  {r['rss_after_verse_mb']:8.1f}MB  "
              f"{r['rss_after_sweep_mb']:8.1f}MB  {r['t_100_verse_ms']:7.2f}ms  "
              f"{r['t_full_sweep_ms']:8.1f}ms")


if __name__ == "__main__":
    main()
