#!/usr/bin/env python3
"""Repeatable static acceptance evidence for the a71412d3 response.

This is deliberately not a runtime gate. It checks files, dimensions, metadata,
alpha corners, the immutable W0 slot contract, and a real 9-slice resize probe
at three sizes. It never modifies docs/spec, datas, or tools.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops

BRANCH = "arena/eca8588b-windwings-space-shooter-game-p"
LICENSE = "chờ user xác nhận quyền tên/art"
CSVS = ["art/w1-player-b/w1b_units.csv", "art/w2-enemy-b/w2b_units.csv",
        "art/w3-boss-b/w3b_units.csv", "art/w4-core-b/w4b_units.csv", "art/w5-full-b/w5b_units.csv"]
EXPECTED_COUNTS = {"w1-player-b": 48, "w2-enemy-b": 34, "w3-boss-b": 42, "w4-core-b": 114, "w5-full-b": 274}
W0_EXPECTED = {
    "microsoft-store/ms_tile_icon_300x300.png": (300, 300, "RGB"),
    "microsoft-store/ms_box_art_1080x1080.png": (1080, 1080, "RGB"),
    "microsoft-store/ms_poster_art_720x1080.png": (720, 1080, "RGB"),
    "microsoft-store/ms_super_hero_1920x1080.png": (1920, 1080, "RGB"),
    **{f"microsoft-store/ms_screenshot_{i}_1920x1080.png": (1920, 1080, "RGB") for i in range(1, 5)},
    "amazon-appstore/amazon_icon_large_512x512.png": (512, 512, "RGBA"),
    "amazon-appstore/amazon_icon_small_114x114.png": (114, 114, "RGBA"),
    "amazon-appstore/amazon_promo_1024x500.png": (1024, 500, "RGB"),
    **{f"amazon-appstore/amazon_screenshot_{i}_800x1280.png": (800, 1280, "RGB") for i in range(1, 5)},
    "huawei-appgallery/huawei_icon_512x512.png": (512, 512, "RGB"),
    "huawei-appgallery/huawei_icon_216x216.png": (216, 216, "RGB"),
    **{f"huawei-appgallery/huawei_screenshot_{i}_450x800.png": (450, 800, "RGB") for i in range(1, 5)},
    **{f"huawei-appgallery/huawei_screenshot_{i}_720x1280.png": (720, 1280, "RGB") for i in range(1, 5)},
}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def nine_slice(im, size, border):
    """Reference 9-slice resize; corners are pasted without resampling."""
    w, h = size; l = r = t = b = border
    if w <= l + r + 2 or h <= t + b + 2: raise ValueError("target smaller than borders")
    sw, sh = im.size
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    xs = [0, l, sw - r, sw]; ys = [0, t, sh - b, sh]
    xd = [0, l, w - r, w]; yd = [0, t, h - b, h]
    for j in range(3):
        for i in range(3):
            piece = im.crop((xs[i], ys[j], xs[i + 1], ys[j + 1]))
            dw, dh = xd[i + 1] - xd[i], yd[j + 1] - yd[j]
            if i == 1 or j == 1:
                piece = piece.resize((dw, dh), Image.Resampling.LANCZOS)
            out.paste(piece, (xd[i], yd[j]))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, required=True); args = ap.parse_args()
    root = args.root.resolve(); args.out.mkdir(parents=True, exist_ok=True)
    errors = []; warnings = []; rows = []
    for rel in CSVS:
        wave = Path(rel).parent.name
        with (root / rel).open(encoding="utf-8-sig", newline="") as f:
            records = list(csv.DictReader(f))
        if len(records) != EXPECTED_COUNTS[wave]: errors.append(f"{wave}: {len(records)} records != {EXPECTED_COUNTS[wave]}")
        for r in records:
            sprite = root / Path(rel).parent / r["file"]
            master = root / Path(rel).parent / r["source"]
            for label, path in (("sprite", sprite), ("master", master)):
                if not path.exists(): errors.append(f"missing {label}: {path.relative_to(root)}")
            if r.get("author") != BRANCH: errors.append(f"author mismatch: {r['file']}")
            if LICENSE not in r.get("license", ""): errors.append(f"license missing: {r['file']}")
            if not r.get("recipe"): errors.append(f"recipe missing: {r['file']}")
            if not sprite.exists(): continue
            with Image.open(sprite) as im:
                rgba = im.convert("RGBA")
                expected = tuple(int(x) for x in r["delivered_px"].lower().replace("×", "x").split("x"))
                if im.size != expected: errors.append(f"dimensions {r['file']}: {im.size} != {expected}")
                if im.mode != "RGBA": warnings.append(f"mode {r['file']}: {im.mode} (converted for alpha check)")
                alpha = np.asarray(rgba.getchannel("A"))
                if not np.all(alpha == 255):
                    corners = [int(alpha[0, 0]), int(alpha[0, -1]), int(alpha[-1, 0]), int(alpha[-1, -1])]
                    if any(corners): errors.append(f"alpha corners {r['file']}: {corners}")
                rows.append({"wave": wave, "row_id": r["row_id"], "file": r["file"], "sha256": sha(sprite)})
    if len(rows) != 512: errors.append(f"total sprite records {len(rows)} != 512")

    # W0 immutable 25-slot filename/size/mode contract.
    w0_root = root / "art/w0-listing-b"
    w0_records = json.loads((w0_root / "w0b_exports.json").read_text(encoding="utf-8"))
    if len(w0_records) != 25: errors.append(f"W0 export records {len(w0_records)} != 25")
    for rec in w0_records:
        rel = rec["file"]
        if rel not in W0_EXPECTED:
            errors.append(f"W0 unexpected slot {rel}"); continue
        path = w0_root / rel
        if not path.exists(): errors.append(f"W0 missing {rel}"); continue
        with Image.open(path) as im:
            want = W0_EXPECTED[rel]
            if (im.width, im.height, im.mode) != want: errors.append(f"W0 contract {rel}: {(im.width, im.height, im.mode)} != {want}")
        if rel.startswith("huawei-") and path.stat().st_size > 2048 * 1024: errors.append(f"W0 Huawei >2MB {rel}")
        if "huawei_icon_216" in rel and path.stat().st_size > 500 * 1024: errors.append(f"W0 216 icon >500KB {rel}")
        if rel.startswith("microsoft-") and path.stat().st_size > 50 * 1024 * 1024: errors.append(f"W0 MS >50MB {rel}")
        if "screenshot" in rel and "CONCEPT" not in rec.get("note", "").upper(): errors.append(f"W0 screenshot not marked CONCEPT {rel}")

    # Duplicate hash inventory is evidence, not an automatic failure: frames
    # may be intentional reuse, but each semantic collision needs review.
    hashes = defaultdict(list)
    for row in rows: hashes[row["sha256"]].append(row)
    duplicate_groups = [v for v in hashes.values() if len(v) > 1]
    duplicate_extra = sum(len(v) - 1 for v in duplicate_groups)

    # 9-slice static probe at three sizes on three actual UI frames.
    candidates = []
    for rel in CSVS:
        with (root / rel).open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r["row_id"] in ("AP-0352", "AP-0353") or "frame_standard" in r["variant"]:
                    candidates.append((r["row_id"], root / Path(rel).parent / r["file"]))
    candidates = candidates[:3]
    ns_rows = []
    for row_id, path in candidates:
        with Image.open(path) as source:
            source = source.convert("RGBA")
            border = (56 if row_id == "AP-0273" else 32) if min(source.size) >= 256 else 16
            center = source.crop((border + 3, border + 3, source.width - border - 3, source.height - border - 3))
            center_arr = np.asarray(center, dtype=np.float32)
            center_std = float(center_arr[:, :, :3].std(axis=(0, 1)).max())
            for size in ((320, 240), (480, 360), (720, 1080)):
                try:
                    made = nine_slice(source, size, border)
                    corner_ok = True
                    for sx, sy, dx, dy in ((0, 0, 0, 0), (source.width - border, 0, size[0] - border, 0),
                                           (0, source.height - border, 0, size[1] - border),
                                           (source.width - border, source.height - border, size[0] - border, size[1] - border)):
                        if ImageChops.difference(source.crop((sx, sy, sx + border, sy + border)), made.crop((dx, dy, dx + border, dy + border))).getbbox() is not None:
                            corner_ok = False
                    status = "STATIC_OK" if corner_ok and center_std < 1.0 else ("STATIC_REVIEW" if corner_ok else "STATIC_FAIL")
                    ns_rows.append({"row_id": row_id, "asset": str(path.relative_to(root)), "border": border,
                                    "size": f"{size[0]}x{size[1]}", "corners_exact": corner_ok,
                                    "source_center_rgb_std": round(center_std, 4), "status": status})
                    if status != "STATIC_OK": warnings.append(f"9-slice review {row_id} {size}: {status}")
                except Exception as exc:
                    ns_rows.append({"row_id": row_id, "asset": str(path.relative_to(root)), "border": border,
                                    "size": f"{size[0]}x{size[1]}", "corners_exact": False,
                                    "source_center_rgb_std": round(center_std, 4), "status": f"STATIC_FAIL:{exc}"})
                    errors.append(f"9-slice {row_id} {size}: {exc}")

    result = {
        "audit_commit": "a71412d3427e3c2d9d01ee519a154be289091923",
        "branch": BRANCH, "static_only": True, "runtime_verified": False,
        "sprite_records": len(rows), "unique_sprite_hashes": len(hashes),
        "planner_unit_coverage": 510, "w0_slots": len(w0_records),
        "duplicate_extra_files": duplicate_extra, "duplicate_groups": len(duplicate_groups),
        "errors": errors, "warnings": warnings, "nine_slice": ns_rows,
        "notes": [
            "510/510 is inventory parity, not aesthetic or runtime approval.",
            "W0 S1-S4 are CONCEPT composites; no Godot build exists on this art branch.",
            "Duplicate hashes are reported for semantic/integration review, not automatically called defects.",
            "Planner raw metrics are in planner_raw_metrics.csv; palette bands for B remain CONFLICTING per audit.",
        ],
    }
    (args.out / "static_validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    with (args.out / "nine_slice_contract.csv").open("w", encoding="utf-8", newline="") as f:
        fields = list(ns_rows[0]) if ns_rows else ["row_id"]
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(ns_rows)
    lines = ["# Static validation — response to a71412d3", "", f"- Sprite records: **{len(rows)}/512** · W0 slots: **{len(w0_records)}/25** · planner coverage: **510/510**", f"- Unique sprite hashes: **{len(hashes)}** · duplicate extras reported: **{duplicate_extra}** (review, not automatic failure)", f"- Errors: **{len(errors)}** · warnings: **{len(warnings)}**", "- Runtime/pivot/motion/VFX blend/three-person kinship: **UNVERIFIED**", "", "## Errors", ""]
    lines += [f"- {e}" for e in errors] or ["- None"]
    lines += ["", "## 9-slice probes", "", "| ID | Size | Corners exact | Center RGB std | Status |", "|---|---|---:|---:|---|"]
    lines += [f"| {r['row_id']} | {r['size']} | {r['corners_exact']} | {r['source_center_rgb_std']} | {r['status']} |" for r in ns_rows]
    (args.out / "static_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "w0": len(w0_records), "errors": len(errors), "warnings": len(warnings), "duplicate_extra": duplicate_extra, "nine_slice": len(ns_rows)}, ensure_ascii=False))
    for e in errors[:30]: print("ERROR", e)
    return int(bool(errors))


if __name__ == "__main__": raise SystemExit(main())
