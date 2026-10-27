#!/usr/bin/env python3
"""Measure B pass-2 W1 plus indexed enemy/boss samples with the pinned planner.

No pixel metrics are implemented here: measure_snapshots delegates to the
unmodified planner measure_asset.measure_png. Sample boss IDs are matched by
both manifests and the decoded boss/sprite index. Old B measurements are in
asset_metrics.csv, and source hashes must match before comparing revisions.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import measure_snapshots as base

WAVES = {
    "w1-player-b": None,  # full 48-piece PLAYER batch
    "w2-enemy-b": {
        "enemy_body_01_scout_dart_128@crimson.png",
        "enemy_body_06_swarmling_pod_128@amber.png",
        "enemy_body_18_phantom_hex_128@violet.png",
    },
    "w3-boss-b": {
        "boss_body_04_citadel_mk1_512@crimson.png",
        "boss_body_05_arachnid_mk1_512@emerald.png",
        "boss_body_06_leviathan_mk1_512@amber.png",
        "boss_body_07_chronos_mk1_512@violet.png",
        "boss_body_08_seraph_mk1_512@magenta.png",
    },
}
MANIFESTS = {
    "w1-player-b": "w1b_units.csv",
    "w2-enemy-b": "w2b_units.csv",
    "w3-boss-b": "w3b_units.csv",
}
COLUMNS = ["variant", "wave", "batch", "cls", "row_id", "name", "path", "sha256", "width",
           "height", "mode", "full_opaque", "grad_stops", "outline_px", "detail", "dark_edge",
           "val", "val_std", "dark", "chroma", "colors", "fill", "sat_v25", "style_outside",
           "palette_outside", "outline_gt_1", "error"]


def inventory(root: Path) -> list[dict[str, str]]:
    result = []
    found = {key: set() for key in WAVES}
    for wave, selected in WAVES.items():
        folder = root / "art" / wave
        with (folder / MANIFESTS[wave]).open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                basename = Path(row["file"]).name
                if selected is not None and basename not in selected:
                    continue
                if row["batch"] not in base.BATCH_CLASS:
                    raise ValueError(f"Unknown class in {wave}: {row['batch']}")
                cls = "ui" if row["row_id"] == "AP-0067" else base.BATCH_CLASS[row["batch"]]
                rel = (Path("art") / wave / row["file"]).as_posix()
                result.append(dict(variant="B", wave=wave, batch=row["batch"], cls=cls,
                                   row_id=row["row_id"], name=row["variant"], path=rel,
                                   root=str(root)))
                found[wave].add(basename)
    for wave, selected in WAVES.items():
        if selected is not None and found[wave] != selected:
            raise ValueError(f"Missing/extra selections in {wave}: {selected ^ found[wave]}")
    if len(found["w1-player-b"]) != 48 or len(result) != 56:
        raise ValueError(f"Expected 48 W1 + 3 enemy + 5 boss, found {len(result)}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--b-root", type=Path, required=True, help="extracted B pass-2 tree")
    parser.add_argument("--planner", type=Path, required=True, help="pinned measure_asset.py")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be at least 1")
    root, planner = args.b_root.resolve(), args.planner.resolve()
    base.load_planner(planner)  # verifies upstream script SHA-256 before measuring
    tasks = inventory(root)
    print(f"Measuring {len(tasks)} PNGs using pinned planner; workers={args.workers}", flush=True)
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=args.workers, initializer=base.load_planner, initargs=(planner,)
    ) as pool:
        rows = []
        for count, row in enumerate(pool.map(base.measure, tasks, chunksize=1), 1):
            rows.append(row)
            if count % 10 == 0 or count == len(tasks):
                print(f"{count}/{len(tasks)}", flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    errors = [row for row in rows if row.get("error")]
    print(f"Wrote {len(rows)} records to {args.out}; errors: {len(errors)}", flush=True)
    for row in errors:
        print(f"ERROR {row['path']}: {row['error']}", file=sys.stderr)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
