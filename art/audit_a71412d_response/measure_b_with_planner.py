#!/usr/bin/env python3
"""Measure Variant B exports with the auditor's exact pinned planner function.

Response to a71412d3427e3c2d9d01ee519a154be289091923.
This wrapper does not implement or modify any pixel metric. It calls the
unmodified measure_asset.measure_png at planner commit 100cfcebc3 and records
raw values plus class-band membership. Palette bands are Ink & Ember anchored
and are CONFLICTING for Solar Neon B; they are evidence, not an approval gate.
RUNTIME remains unverified.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import importlib.util
from pathlib import Path

PLANNER_SHA256 = "c33182347dabf7e1eba4a3278d298a62a89a43ccbc2ae75e3ba0d6181a22b053"
BATCH_CLASS = {
    "P-SHIP": "ship", "P-DRONE": "drone", "P-BULLET": "bullet", "P-FX": "fx",
    "E-BODY": "enemy", "E-BULLET": "bullet", "B-BODY": "boss", "B-PART": "boss",
    "I-DROP": "item", "F-BOOM": "fx", "F-ENEMY": "fx", "F-GLOW": "fx",
    "G-PARALLAX": "bg", "G-UI": "ui", "U-HUD": "ui", "U-ICON": "ui",
    "U-KIT": "ui", "U-META": "ui", "U-SHOP": "ui",
}
CSVS = (
    "art/w1-player-b/w1b_units.csv", "art/w2-enemy-b/w2b_units.csv",
    "art/w3-boss-b/w3b_units.csv", "art/w4-core-b/w4b_units.csv",
    "art/w5-full-b/w5b_units.csv",
)
MEASURER = None


def load_planner(path: Path):
    global MEASURER
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != PLANNER_SHA256:
        raise ValueError(f"Wrong planner measure_asset.py SHA-256: {digest}")
    spec = importlib.util.spec_from_file_location("pinned_measure_asset", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    MEASURER = module


def inventory(root: Path):
    tasks = []
    for rel in CSVS:
        csv_path = root / rel
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                batch = row["batch"]
                cls = "ui" if row["row_id"] == "AP-0067" else BATCH_CLASS[batch]
                tasks.append({
                    "wave": Path(rel).parent.name, "batch": batch, "cls": cls,
                    "row_id": row["row_id"], "name": row["variant"],
                    "path": (Path(rel).parent / row["file"]).as_posix(),
                    "root": str(root),
                })
    return tasks


def measure(task):
    from PIL import Image
    path = Path(task["root"]) / task["path"]
    result = {k: v for k, v in task.items() if k != "root"}
    try:
        result["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as im:
            result["width"], result["height"], result["mode"] = im.width, im.height, im.mode
            result["full_opaque"] = int(im.convert("RGBA").getchannel("A").getextrema() == (255, 255))
        m = MEASURER.measure_png(path)
        for key in ("grad_stops", "outline_px", "detail", "dark_edge", "val", "val_std",
                    "dark", "chroma", "colors", "fill", "sat_v25"):
            result[key] = f"{m[key]:.6f}"
        cls = task["cls"]
        result["style_outside"] = ";".join(
            k for k, limits in MEASURER.STYLE_BANDS[cls].items()
            if not MEASURER.in_band(m[k], limits))
        result["palette_outside"] = ";".join(
            k for k, limits in MEASURER.BANDS[cls].items()
            if not MEASURER.in_band(m[k], limits))
        result["outline_gt_1"] = str(int(m["outline_px"] > 1.0))
        result["error"] = ""
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--planner", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    load_planner(args.planner.resolve())
    tasks = inventory(args.root.resolve())
    columns = ["wave", "batch", "cls", "row_id", "name", "path", "sha256", "width", "height",
               "mode", "full_opaque", "grad_stops", "outline_px", "detail", "dark_edge", "val",
               "val_std", "dark", "chroma", "colors", "fill", "sat_v25", "style_outside",
               "palette_outside", "outline_gt_1", "error"]
    print(f"Measuring {len(tasks)} B PNGs with unmodified planner {PLANNER_SHA256}", flush=True)
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=args.workers, initializer=load_planner, initargs=(args.planner.resolve(),)
    ) as pool:
        rows = []
        for i, row in enumerate(pool.map(measure, tasks, chunksize=1), 1):
            rows.append(row)
            if i % 25 == 0 or i == len(tasks):
                print(f"{i}/{len(tasks)}", flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    errors = [r for r in rows if r["error"]]
    print(f"Wrote {len(rows)} rows to {args.out}; errors={len(errors)}", flush=True)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
