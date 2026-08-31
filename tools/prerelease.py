"""Report what a release would change, before the tag is cut.

Nothing here decides whether to release. Every check reports and the run
always succeeds, so the reports are read rather than obeyed.

    python tools/prerelease.py --web ../phonemizer-web

Three reports:

  render     every reading the site draws, and every variant option, still
             produces a payload its renderer can join. Needs `--web`.
  phonemes   per-word phonemes across the whole corpus, both readings and both
             boundary plans, against the newest release on PyPI.
  structure  the same sweep over the typed analysis and cell documents: rule
             placements, phoneme and character attributions, roles, and cell
             status. Only comparable when the baseline publishes them too.

The corpus is walked one verse at a time in short-lived shard processes, and
only digests are kept. A whole-surah or whole-corpus request would hold its
entire score alive, and keeping every reading's documents in memory to diff
them later would cost far more than re-reading the few that moved.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
import urllib.request
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The working tree is the candidate, ahead of any installed copy of the package.
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "release"))

from compare import classify, detail, load  # noqa: E402

PROBE = ROOT / "tools" / "release" / "probe.py"
PYPI = "https://pypi.org/pypi/quranic-phonemizer/json"
RIWAYAT = ("hafs", "warsh")

#: Verses per shard process. Each one exits before the next starts, so the
#: producer's process-local caches never accumulate across the corpus.
SHARD = 400


def _latest_release() -> str:
    with urllib.request.urlopen(PYPI, timeout=30) as response:
        return json.load(response)["info"]["version"]


def _baseline_python(work: Path, version: str) -> Path:
    """A throwaway venv holding the published release."""
    home = work / "baseline-venv"
    python = home / ("Scripts" if os.name == "nt" else "bin") / "python"
    if not python.exists():
        venv.create(home, with_pip=True)
    subprocess.run(
        [str(python), "-m", "pip", "install", "-q", f"quranic-phonemizer=={version}"],
        check=True,
    )
    return python


def _verses(riwayah: str) -> list[str]:
    from quranic_phonemizer.api import recitation
    from quranic_phonemizer.model.address import Riwayah

    info = recitation(Riwayah(riwayah)).corpus.surah_info
    return [
        f"{surah}:{ayah}"
        for surah in sorted(int(key) for key in info)
        for ayah in range(1, len(info[str(surah)]) + 1)
    ]


def _run_shard(python: Path, riwayah: str, refs: Path, out: Path, tree: bool,
               detailed: bool) -> str:
    """One probe process. The working tree is put ahead of any installed copy."""
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT) if tree else ""
    command = [
        str(python), str(PROBE), "--riwayah", riwayah,
        "--refs", str(refs), "--out", str(out),
    ] + (["--detail"] if detailed else [])
    done = subprocess.run(
        command, cwd=ROOT, env=environment, capture_output=True, text=True,
    )
    if done.returncode != 0:
        raise RuntimeError(f"probe failed for {riwayah}:\n{done.stderr[-2000:]}")
    return done.stdout.strip()


def _sweep(python: Path, riwayah: str, refs: list[str], work: Path, label: str,
           workers: int, detailed: bool = False) -> Path:
    """Shard a reference list across probe processes and join the digests."""
    shards = [refs[at:at + SHARD] for at in range(0, len(refs), SHARD)] or [[]]
    jobs = []
    for index, shard in enumerate(shards):
        listing = work / f"{label}-{riwayah}-{index}.refs"
        listing.write_text("\n".join(shard), encoding="utf-8")
        jobs.append((listing, work / f"{label}-{riwayah}-{index}.jsonl"))
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        list(pool.map(
            lambda job: _run_shard(python, riwayah, job[0], job[1],
                                   label == "candidate", detailed),
            jobs,
        ))
    joined = work / f"{label}-{riwayah}{'-detail' if detailed else ''}.jsonl"
    with joined.open("w", encoding="utf-8") as sink:
        for _, part in jobs:
            sink.write(part.read_text(encoding="utf-8"))
    return joined


def _diff(python: Path, riwayah: str, work: Path, workers: int) -> dict:
    """Digest both installs, then re-read only the readings that disagree."""
    refs = _verses(riwayah)
    print(f"  {riwayah}: {len(refs)} verses", flush=True)
    baseline = load(_sweep(python, riwayah, refs, work, "baseline", workers))
    if not baseline:
        return {"unsupported": True, "compared": 0, "verses": len(refs)}
    candidate = load(_sweep(python, riwayah, refs, work, "candidate", workers))
    report = classify(baseline, candidate)
    changed = sorted({
        tuple(entry.split(" ")) for entry in report["phonemes"] + report["structure"]
    })
    report["changed_verses"] = sorted({key[0] for key in changed})
    if changed:
        print(f"  {riwayah}: re-reading {len(report['changed_verses'])} changed verses",
              flush=True)
        both = [
            load(_sweep(python, riwayah, report["changed_verses"], work, label,
                        workers, detailed=True))
            for label in ("baseline", "candidate")
        ]
        report["details"] = detail(both[0], both[1], changed)
    return report


def _render_audit(web: Path) -> dict:
    """The website's own corpus and variant sweep, run against this tree."""
    environment = dict(os.environ, PYTHONPATH=str(ROOT))
    done = subprocess.run(
        [sys.executable, "scripts/audit-verses.py"],
        cwd=web, env=environment, capture_output=True, text=True,
    )
    lines = done.stdout.splitlines()
    return {
        "exit_code": done.returncode,
        "summary": lines[-1] if lines else "",
        "failures": [line for line in lines if line.startswith(("FAIL", "STALL"))],
    }


def _print(report: dict) -> None:
    print("\n=== prerelease " + "=" * 50)
    print(f"baseline {report['baseline']}   candidate working tree")
    render = report.get("render")
    if render:
        print(f"render: {render['summary']}")
        for line in render["failures"][:20]:
            print(f"  {line}")
    for riwayah, one in report["readings"].items():
        if one.get("unsupported"):
            print(f"{riwayah}: not published by the baseline; nothing to compare")
            continue
        print(
            f"{riwayah}: {one['compared']} readings compared, "
            f"{len(one['phonemes'])} phoneme changes, "
            f"{len(one['structure'])} structural changes "
            f"({one['structure_compared']} comparable), "
            f"{len(one['errors'])} errors"
        )
        for line in one["errors"][:5]:
            print(f"  error {line}")
        for row in one.get("details", [])[:5]:
            for line in (row["phonemes"] + row["structure"])[:4]:
                print(f"  {row['ref']} {row['plan']}: {line}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", help="release to compare against")
    parser.add_argument("--web", type=Path, help="the website checkout")
    parser.add_argument("--riwayah", choices=("both", *RIWAYAT), default="both")
    parser.add_argument("-j", type=int, default=0)
    parser.add_argument("--work", type=Path, default=ROOT / ".prerelease")
    parser.add_argument("--report", type=Path, default=ROOT / ".prerelease/report.json")
    args = parser.parse_args()

    started = time.perf_counter()
    args.work.mkdir(parents=True, exist_ok=True)
    workers = args.j or max(1, (os.cpu_count() or 4) - 2)
    version = args.baseline or _latest_release()
    print(f"baseline {version}, {workers} workers", flush=True)
    python = _baseline_python(args.work, version)

    report = {"baseline": version, "readings": {}}
    if args.web:
        print("render audit", flush=True)
        report["render"] = _render_audit(args.web)
    names = RIWAYAT if args.riwayah == "both" else (args.riwayah,)
    for riwayah in names:
        report["readings"][riwayah] = _diff(python, riwayah, args.work, workers)
        if not report["readings"][riwayah]["compared"]:
            report["readings"][riwayah]["unsupported"] = True

    report["seconds"] = round(time.perf_counter() - started, 1)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    _print(report)
    print(f"\nfull report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
