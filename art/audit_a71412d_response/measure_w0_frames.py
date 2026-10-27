#!/usr/bin/env python3
"""Measure the four original captures and four current B W0 CONCEPT stills.

Uses the exact pinned tools/design-metrics.py measure() function. W0 stills are
marketing composites, not Godot screenshots; these numbers are review flags only.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util
from pathlib import Path

EXPECTED_SHA = "77bb6a91edd691145924b63dad4c09d95e98c9525390dbbd986d27ca3bddebc7"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--spec-root", type=Path, required=True)
    ap.add_argument("--root", type=Path, default=Path(".")); ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(); tool = args.spec_root / "tools/design-metrics.py"
    if hashlib.sha256(tool.read_bytes()).hexdigest() != EXPECTED_SHA: raise ValueError("wrong design-metrics SHA")
    spec = importlib.util.spec_from_file_location("pinned_design_metrics", tool)
    dm = importlib.util.module_from_spec(spec); spec.loader.exec_module(dm)
    jobs = [("REF", args.spec_root / f"docs/apk-analysis/ramus/2026-10-23-phone/{n}.png") for n in ("p_2_Game", "slow_8_Game", "p_4_Game", "live_1_Game")]
    jobs += [("B_CONCEPT", args.root / f"art/w0-listing-b/huawei-appgallery/huawei_screenshot_{i}_450x800.png") for i in range(1, 5)]
    rows = []
    for group, path in jobs:
        m = dm.measure(str(path))
        rows.append({"set": group, "path": str(path.relative_to(args.root if group == "B_CONCEPT" else args.spec_root)),
                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "width": m["w"], "height": m["h"],
                     "contrast_p95_p05": round(m["luminance_p95"] - m["luminance_p05"], 4),
                     "accent_all_hues": m["accent_share"], "detail_gradient": m["detail_gradient"],
                     "mean_value": m["mean_value"], "mean_saturation": m["mean_saturation"],
                     "runtime_status": "REFERENCE_CAPTURE" if group == "REF" else "CONCEPT_NOT_RUNTIME"})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
    for r in rows: print(r["set"], r["path"], r["contrast_p95_p05"], r["accent_all_hues"], r["detail_gradient"])


if __name__ == "__main__": main()
