"""Hash the downstream shards, which live outside the tree.

    $ python tools/shards.py {write,verify} <dir> <manifest.json>
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

#: The shard schema this repository knows how to read.
SCHEMA = 11


def describe(directory: Path) -> dict:
    rows = {}
    schemas = set()
    for path in sorted(directory.glob("*.json.gz")):
        raw = path.read_bytes()
        document = json.loads(gzip.decompress(raw))
        schemas.add(document["_meta"]["schema_version"])
        rows[path.name] = {
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    return {"schema_versions": sorted(schemas), "shards": rows}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("write", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)

    found = describe(args.directory)
    if found["schema_versions"] != [SCHEMA]:
        print(f"schema {found['schema_versions']}, expected [{SCHEMA}]")
        return 1

    if args.action == "write":
        args.manifest.write_text(json.dumps(found, indent=1), encoding="utf-8")
        print(f"{len(found['shards'])} shards written")
        return 0

    recorded = json.loads(args.manifest.read_text(encoding="utf-8"))["shards"]
    wrong = [
        name for name in sorted(set(recorded) | set(found["shards"]))
        if recorded.get(name) != found["shards"].get(name)
    ]
    for name in wrong:
        print(f"{name} does not match the manifest")
    print(f"{len(found['shards'])} shards checked, {len(wrong)} problems")
    return 1 if wrong else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
