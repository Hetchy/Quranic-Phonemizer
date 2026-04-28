"""Bench dedup'd DB formats end-to-end (load time, RSS, lookup speed).

Each variant runs in a fresh subprocess. Compares against the existing
texts/flat/blob/mmap formats from loader.py.

Variants:
  - texts                : current default (texts only, dict-of-strings)
  - flat                 : [keys, texts] parallel arrays
  - blob                 : binary blob, eager read
  - mmap                 : binary blob, mmap + lazy decode
  - dedup_naive_eager    : dedup'd JSON, build dict with shared str objects
  - dedup_naive_blob     : dedup'd binary, eager read, shared str values
  - dedup_naive_mmap     : dedup'd binary, mmap + decode-then-intern
  - dedup_smart_eager    : dedup'd by core+decoration; reconstruct full text
"""
from __future__ import annotations

import json
import subprocess
import sys

DRIVER = r"""
import sys, os, gc, time, json, struct, array, mmap
from pathlib import Path

def rss_mb():
    with open('/proc/self/status') as f:
        for line in f:
            if line.startswith('VmRSS:'):
                return int(line.split()[1]) / 1024.0

variant = sys.argv[1]
res = Path('quranic_phonemizer/resources')
tmp = Path('/tmp/quran_formats')

gc.collect()
rss_baseline = rss_mb()
t0 = time.perf_counter()

if variant == 'texts':
    with (res / 'quran_db_texts.json').open(encoding='utf-8') as f:
        texts = json.load(f)
    with (res / 'surah_info.json').open(encoding='utf-8') as f:
        info = json.load(f)
    keys = []
    for s in range(1, 115):
        s_str = str(s)
        for v_idx, v_info in enumerate(info[s_str]['verses'], start=1):
            v = v_idx
            prefix = s_str + ':' + str(v) + ':'
            for w in range(1, v_info['num_words'] + 1):
                keys.append(prefix + str(w))
    db = dict(zip(keys, texts))
    sorted_keys = keys
    def lookup(k): return db[k]

elif variant == 'flat':
    with (res / 'quran_db_flat.json').open(encoding='utf-8') as f:
        keys, texts = json.load(f)
    db = dict(zip(keys, texts))
    sorted_keys = keys
    def lookup(k): return db[k]

elif variant == 'blob':
    with (res / 'quran_db_blob.bin').open('rb') as f:
        data = f.read()
    n = struct.unpack_from('<I', data, 0)[0]
    offs = array.array('I')
    offs.frombytes(data[4:4 + (n + 1) * 4])
    pos = 4 + (n + 1) * 4
    tlen = struct.unpack_from('<I', data, pos)[0]; pos += 4
    text_blob = data[pos:pos + tlen]; pos += tlen
    klen = struct.unpack_from('<I', data, pos)[0]; pos += 4
    keys = data[pos:pos + klen].decode('ascii').rstrip('\n').split('\n')
    key_to_idx = {k: i for i, k in enumerate(keys)}
    sorted_keys = keys
    def lookup(k, _b=text_blob, _o=offs, _i=key_to_idx):
        i = _i[k]
        return _b[_o[i]:_o[i+1]].decode('utf-8')

elif variant == 'mmap':
    fh = (res / 'quran_db_blob.bin').open('rb')
    mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
    n = struct.unpack_from('<I', mm, 0)[0]
    offs = array.array('I')
    offs.frombytes(bytes(mm[4:4 + (n + 1) * 4]))
    pos = 4 + (n + 1) * 4
    tlen = struct.unpack_from('<I', mm, pos)[0]; pos += 4
    tstart = pos
    with (res / 'surah_info.json').open(encoding='utf-8') as f:
        info = json.load(f)
    verse_start = {}
    sorted_tuples = []
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
    def lookup(k, _mm=mm, _o=offs, _b=tstart, _vs=verse_start):
        a, b, c = k.split(':', 2)
        i = _vs[(int(a), int(b))] + int(c) - 1
        return _mm[_b + _o[i]:_b + _o[i+1]].decode('utf-8')
    sorted_keys = [f'{s}:{v}:{w}' for s, v, w in sorted_tuples]

elif variant == 'dedup_naive_eager':
    # JSON [unique_texts, indices].
    with (tmp / 'dedup_naive.json').open(encoding='utf-8') as f:
        unique_texts, indices = json.load(f)
    with (res / 'surah_info.json').open(encoding='utf-8') as f:
        info = json.load(f)
    keys = []
    for s in range(1, 115):
        s_str = str(s)
        for v_idx, v_info in enumerate(info[s_str]['verses'], start=1):
            v = v_idx
            prefix = s_str + ':' + str(v) + ':'
            for w in range(1, v_info['num_words'] + 1):
                keys.append(prefix + str(w))
    # Build dict: many keys point to the SAME str object via shared index.
    db = {k: unique_texts[idx] for k, idx in zip(keys, indices)}
    sorted_keys = keys
    def lookup(k): return db[k]

elif variant == 'dedup_naive_blob':
    with (tmp / 'dedup_naive_blob.bin').open('rb') as f:
        data = f.read()
    n, m = struct.unpack_from('<II', data, 0)
    pos = 8
    offs = array.array('I')
    offs.frombytes(data[pos:pos + (m + 1) * 4]); pos += (m + 1) * 4
    tlen = struct.unpack_from('<I', data, pos)[0]; pos += 4
    text_blob = data[pos:pos + tlen]; pos += tlen
    word_indices = array.array('H')
    word_indices.frombytes(data[pos:pos + 2 * n])
    # Eager-decode unique texts into Python str objects (shared)
    unique_texts = [text_blob[offs[i]:offs[i+1]].decode('utf-8') for i in range(m)]
    with (res / 'surah_info.json').open(encoding='utf-8') as f:
        info = json.load(f)
    keys = []
    for s in range(1, 115):
        s_str = str(s)
        for v_idx, v_info in enumerate(info[s_str]['verses'], start=1):
            v = v_idx
            prefix = s_str + ':' + str(v) + ':'
            for w in range(1, v_info['num_words'] + 1):
                keys.append(prefix + str(w))
    db = {k: unique_texts[idx] for k, idx in zip(keys, word_indices)}
    sorted_keys = keys
    def lookup(k): return db[k]

elif variant == 'dedup_naive_mmap':
    fh = (tmp / 'dedup_naive_blob.bin').open('rb')
    mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
    n, m = struct.unpack_from('<II', mm, 0)
    pos = 8
    offs = array.array('I')
    offs.frombytes(bytes(mm[pos:pos + (m + 1) * 4])); pos += (m + 1) * 4
    tlen = struct.unpack_from('<I', mm, pos)[0]; pos += 4
    tstart = pos; pos += tlen
    word_indices = array.array('H')
    word_indices.frombytes(bytes(mm[pos:pos + 2 * n]))
    with (res / 'surah_info.json').open(encoding='utf-8') as f:
        info = json.load(f)
    verse_start = {}
    sorted_tuples = []
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
    sorted_keys = None
    def lookup(k, _mm=mm, _o=offs, _b=tstart, _vs=verse_start, _wi=word_indices):
        a, b, c = k.split(':', 2)
        word_idx = _vs[(int(a), int(b))] + int(c) - 1
        u_idx = _wi[word_idx]
        return _mm[_b + _o[u_idx]:_b + _o[u_idx + 1]].decode('utf-8')

elif variant == 'dedup_smart_eager':
    with (tmp / 'dedup_smart.json').open(encoding='utf-8') as f:
        cores, deco_strs, core_idxs, deco_idxs = json.load(f)
    # Decode decoration signatures into list of (pos, char) tuples
    deco_sigs = []
    for s in deco_strs:
        if not s:
            deco_sigs.append(())
        else:
            sig = []
            for piece in s.split(';'):
                pos, ch = piece.split(':', 1)
                sig.append((int(pos), ch))
            deco_sigs.append(tuple(sig))
    # Build full strings by applying decoration to cores
    with (res / 'surah_info.json').open(encoding='utf-8') as f:
        info = json.load(f)
    keys = []
    for s in range(1, 115):
        s_str = str(s)
        for v_idx, v_info in enumerate(info[s_str]['verses'], start=1):
            v = v_idx
            prefix = s_str + ':' + str(v) + ':'
            for w in range(1, v_info['num_words'] + 1):
                keys.append(prefix + str(w))
    # Pre-build full strings for each (core_idx, deco_idx) pair encountered.
    pair_cache = {}
    full_texts = []
    for ci, di in zip(core_idxs, deco_idxs):
        key = (ci, di)
        if key not in pair_cache:
            core = cores[ci]
            sig = deco_sigs[di]
            if not sig:
                pair_cache[key] = core
            else:
                # Insert decoration chars at the recorded positions.
                buf = list(core)
                # positions are in the FULL text, so we have to insert in order
                for pos, ch in sig:
                    buf.insert(pos, ch)
                pair_cache[key] = ''.join(buf)
        full_texts.append(pair_cache[key])
    db = dict(zip(keys, full_texts))
    sorted_keys = keys
    def lookup(k): return db[k]

else:
    raise SystemExit('unknown variant: ' + variant)

t_load = time.perf_counter() - t0
gc.collect()
rss_after_load = rss_mb()

# 50 verse-style lookups (small workload)
import random
random.seed(42)
all_keys = sorted_keys if sorted_keys is not None else [f'{s}:{v}:{w}' for s, v, w in sorted_tuples]
sample = random.sample(all_keys, 50)
gc.collect()
t_v = time.perf_counter()
for k in sample:
    _ = lookup(k)
t_50_verse = time.perf_counter() - t_v
gc.collect()
rss_after_verse = rss_mb()

# Full sweep
t_s = time.perf_counter()
total = 0
for k in all_keys:
    total += len(lookup(k))
t_sweep = time.perf_counter() - t_s
gc.collect()
rss_after_sweep = rss_mb()

print(json.dumps({
    'variant': variant,
    'rss_baseline_mb': rss_baseline,
    'rss_after_load_mb': rss_after_load,
    'rss_after_verse_mb': rss_after_verse,
    'rss_after_sweep_mb': rss_after_sweep,
    't_load_ms': t_load * 1000,
    't_50_verse_us': t_50_verse * 1e6,
    't_full_sweep_ms': t_sweep * 1000,
    'total_chars': total,
}))
"""

VARIANTS = [
    ("texts",              "quranic_phonemizer/resources/quran_db_texts.json"),
    ("flat",               "quranic_phonemizer/resources/quran_db_flat.json"),
    ("blob",               "quranic_phonemizer/resources/quran_db_blob.bin"),
    ("mmap",               "quranic_phonemizer/resources/quran_db_blob.bin"),
    ("dedup_naive_eager",  "/tmp/quran_formats/dedup_naive.json"),
    ("dedup_naive_blob",   "/tmp/quran_formats/dedup_naive_blob.bin"),
    ("dedup_naive_mmap",   "/tmp/quran_formats/dedup_naive_blob.bin"),
    ("dedup_smart_eager",  "/tmp/quran_formats/dedup_smart.json"),
]


def main():
    from pathlib import Path
    rows = []
    for variant, path in VARIANTS:
        size_kb = Path(path).stat().st_size / 1024.0
        out = subprocess.check_output([sys.executable, "-c", DRIVER, variant], text=True)
        rec = json.loads(out.strip())
        rec["file_kb"] = size_kb
        rows.append(rec)

    print(f"{'variant':22s}  file(KB)   load(ms)  rss_load(MB)  rss_verse(MB)  rss_sweep(MB)  50verse(us)  fullsweep(ms)")
    for r in rows:
        print(f"{r['variant']:22s}  {r['file_kb']:7.1f}   {r['t_load_ms']:7.1f}  "
              f"{r['rss_after_load_mb']:11.1f}   {r['rss_after_verse_mb']:11.1f}    "
              f"{r['rss_after_sweep_mb']:11.1f}    {r['t_50_verse_us']:7.1f}      "
              f"{r['t_full_sweep_ms']:7.1f}")

    print()
    print("Markdown table:")
    print("| variant | file (KB) | load (ms) | RSS after load (MB) | RSS after verse (MB) | RSS after sweep (MB) | 50 verse lookups (µs) | full sweep (ms) |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        print(f"| {r['variant']} | {r['file_kb']:.1f} | {r['t_load_ms']:.1f} | "
              f"{r['rss_after_load_mb']:.1f} | {r['rss_after_verse_mb']:.1f} | {r['rss_after_sweep_mb']:.1f} | "
              f"{r['t_50_verse_us']:.1f} | {r['t_full_sweep_ms']:.1f} |")


if __name__ == "__main__":
    main()
