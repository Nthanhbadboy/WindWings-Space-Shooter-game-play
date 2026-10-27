#!/usr/bin/env python3
"""Independently measure pinned A/B PNG exports with the planner's own code.

This is only an inventory/classification/CSV wrapper: every pixel metric is
computed by the unmodified ``measure_asset.measure_png`` from planner commit
100cfcebc38c. Full-frame W0 images deliberately have no sprite band verdict.
See AUDIT_A_B_STYLES.md for source pinning and interpretation limitations.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import os
from pathlib import Path
import sys

PLANNER_SHA256 = "c33182347dabf7e1eba4a3278d298a62a89a43ccbc2ae75e3ba0d6181a22b053"
CSV_PATHS = {
    "A": ["art/w1-player/w1_units.csv", "art/w2-enemy/w2_units.csv",
          "art/w3-boss/w3_units.csv", "art/w4-fx-item/w4_units.csv"],
    "B": ["art/w1-player-b/w1b_units.csv", "art/w2-enemy-b/w2b_units.csv",
          "art/w3-boss-b/w3b_units.csv", "art/w4-core-b/w4b_units.csv",
          "art/w5-full-b/w5b_units.csv"],
}
BATCH_CLASS = {
    "P-SHIP": "ship", "P-DRONE": "drone", "P-BULLET": "bullet", "P-FX": "fx",
    "E-BODY": "enemy", "E-BULLET": "bullet", "B-BODY": "boss", "B-PART": "boss",
    "I-DROP": "item", "F-BOOM": "fx", "F-ENEMY": "fx", "F-GLOW": "fx",
    "G-PARALLAX": "bg", "G-UI": "ui", "U-HUD": "ui", "U-ICON": "ui",
    "U-KIT": "ui", "U-META": "ui", "U-SHOP": "ui",
}
# Store frames are samples, not all 25 exports and not separate sprite masks.
W0_FILES = (
    "amazon-appstore/amazon_icon_large_512x512.png",
    "amazon-appstore/amazon_promo_1024x500.png",
    "huawei-appgallery/huawei_screenshot_1_450x800.png",
    "huawei-appgallery/huawei_screenshot_2_450x800.png",
    "huawei-appgallery/huawei_screenshot_4_450x800.png",
)
MEASURER = None


def load_planner(path: Path):
    global MEASURER
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != PLANNER_SHA256:
        raise ValueError(f"Wrong planner measure_asset.py SHA-256: {digest}")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(path.parent))
    import measure_asset  # type: ignore[import-not-found]  # pinned upstream module
    MEASURER = measure_asset


def inventory(roots: dict[str, Path]) -> list[dict[str, str]]:
    tasks = []
    for variant in ("A", "B"):
        root = roots[variant]
        for rel in CSV_PATHS[variant]:
            csv_path = root / rel
            with csv_path.open(encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    batch = row["batch"]
                    if batch not in BATCH_CLASS:
                        raise ValueError(f"Unmapped planner batch {batch} in {csv_path}")
                    # B's HP pip is a HUD, despite the inherited E-BODY label.
                    cls = "ui" if variant == "B" and row["row_id"] == "AP-0067" else BATCH_CLASS[batch]
                    rel_png = (Path(rel).parent / row["file"]).as_posix()
                    tasks.append(dict(variant=variant, wave=Path(rel).parent.name,
                                      batch=batch, cls=cls, row_id=row["row_id"],
                                      name=row["variant"], path=rel_png, root=str(root)))
        w0 = "art/w0-listing" + ("-b" if variant == "B" else "")
        for path in W0_FILES:
            tasks.append(dict(variant=variant, wave=Path(w0).name, batch="W0-FRAME",
                              cls="frame", row_id="", name=Path(path).stem,
                              path=f"{w0}/{path}", root=str(root)))
    tasks.append(dict(variant="B", wave="w0-build-icons-b", batch="W0-ICON", cls="frame",
                      row_id="", name="android-xxhdpi", root=str(roots["B"]),
                      path="art/w0-build-icons-b/mipmap-xxhdpi/ic_launcher.png"))
    return tasks


def measure(task: dict[str, str]) -> dict[str, object]:
    from PIL import Image
    assert MEASURER is not None
    path = Path(task["root"]) / task["path"]
    result: dict[str, object] = {k: v for k, v in task.items() if k != "root"}
    try:
        result["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as im:
            result["width"], result["height"], result["mode"] = im.width, im.height, im.mode
            result["full_opaque"] = int(im.convert("RGBA").getchannel("A").getextrema() == (255, 255))
        # No new metric algorithm: EXACT unmodified planner function.
        metrics = MEASURER.measure_png(path)
        for key in ("grad_stops", "outline_px", "detail", "dark_edge", "val", "val_std",
                    "dark", "chroma", "colors", "fill", "sat_v25"):
            result[key] = f"{metrics[key]:.6f}"
        cls = task["cls"]
        if cls == "frame":
            result["style_outside"] = result["palette_outside"] = "not-applicable-frame"
            result["outline_gt_1"] = "not-applicable-frame"
        else:
            result["style_outside"] = ";".join(k for k, limits in MEASURER.STYLE_BANDS[cls].items()
                                                if not MEASURER.in_band(metrics[k], limits))
            result["palette_outside"] = ";".join(k for k, limits in MEASURER.BANDS[cls].items()
                                                  if not MEASURER.in_band(metrics[k], limits))
            result["outline_gt_1"] = str(int(metrics["outline_px"] > 1.0))
        result["error"] = ""
    except Exception as exc:  # preserve failed files in the output, never silently omit
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--a-root", type=Path, required=True, help="extracted pinned A tree")
    ap.add_argument("--b-root", type=Path, required=True, help="extracted pinned B tree")
    ap.add_argument("--planner", type=Path, required=True, help="pinned planner measure_asset.py")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    if args.workers < 1:
        ap.error("--workers must be >= 1")
    # Fail before spawning any process on a missing/wrong tool or bad input inventory.
    load_planner(args.planner.resolve())
    tasks = inventory({"A": args.a_root.resolve(), "B": args.b_root.resolve()})
    columns = ["variant", "wave", "batch", "cls", "row_id", "name", "path", "sha256", "width",
               "height", "mode", "full_opaque", "grad_stops", "outline_px", "detail", "dark_edge",
               "val", "val_std", "dark", "chroma", "colors", "fill", "sat_v25", "style_outside",
               "palette_outside", "outline_gt_1", "error"]
    print(f"Measuring {len(tasks)} PNGs, {args.workers} workers; upstream SHA-256 {PLANNER_SHA256}", flush=True)
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=args.workers, initializer=load_planner, initargs=(args.planner.resolve(),)
    ) as pool:
        rows = []
        for i, row in enumerate(pool.map(measure, tasks, chunksize=1), 1):
            rows.append(row)
            if i % 50 == 0 or i == len(tasks):
                print(f"{i}/{len(tasks)}", flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    failures = [r for r in rows if r.get("error")]
    print(f"Wrote {len(rows)} records to {args.out}; read/measurement errors: {len(failures)}", flush=True)
    for row in failures[:20]:
        print(f"ERROR {row['variant']} {row['path']}: {row['error']}", file=sys.stderr)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
