#!/usr/bin/env python3
"""Static P0 hero probe: 64px readability + region-level planner measurements."""
from __future__ import annotations
import argparse, csv, importlib.util
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "art"))
import pbr25d


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--spec-root", type=Path, required=True)
    ap.add_argument("--planner", type=Path, required=True); ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("hero_planner", args.planner)
    ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
    sprite_path = ROOT / "art/w1-player-b/sprites/ships/player_ship_01_256@solar.png"
    sprite = Image.open(sprite_path).convert("RGBA")
    regions = {
        "nose_cowling": (105, 24, 151, 70),
        "canopy_frame": (108, 58, 148, 118),
        "port_armor": (54, 105, 105, 171),
        "starboard_armor": (151, 105, 202, 171),
        "engine_cluster": (100, 171, 156, 226),
    }
    rows = []
    for name, box in regions.items():
        crop = sprite.crop(box)
        crop.save(args.out / f"{name}.png")
        vals, mask, w, h = ma.grid_from_image(crop)
        raw = crop.tobytes()
        pixels = [(raw[i], raw[i + 1], raw[i + 2]) for i, m in zip(range(0, len(raw), 4), mask) if m]
        sm = ma.style_metrics(vals, mask, w, h)
        mm = ma.metrics_from_pixels(pixels)
        rows.append({"region": name, "crop_xyxy": str(box), **{k: f"{v:.6f}" for k, v in {**mm, **sm}.items()},
                     "note": "region proxy; not an independent per-panel approval"})
    with (args.out / "hero_panel_metrics.csv").open("w", encoding="utf-8", newline="") as f:
        fields = list(rows[0]); w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(rows)

    # Reference tile #1, current 256px export, actual 64px export and silhouette.
    ref_sheet = Image.open(args.spec_root / "docs/assets/contact-sheets/ships-01.jpg").convert("RGB")
    ref = ref_sheet.crop((0, 26, 150, 160))
    actual64 = pbr25d.downsample_straight_rgba(sprite, (64, 64))
    black = Image.new("RGBA", (64, 64), (8, 12, 22, 255)); black.putalpha(actual64.getchannel("A"))
    board = Image.new("RGB", (1040, 640), (13, 18, 30)); d = ImageDraw.Draw(board)
    fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    d.text((24, 16), "P0 HERO 10001 · static technical probe (not a lock / not runtime)", font=ImageFont.truetype(fb, 21), fill=(255, 230, 108))
    d.text((24, 49), "Reference vs 256px export vs actual 64px read + alpha silhouette; region metrics use unmodified planner functions", font=ImageFont.truetype(fr, 12), fill=(190, 211, 229))
    def checker(size):
        im = Image.new("RGBA", size, (38, 38, 42, 255)); dd = ImageDraw.Draw(im); step = 12
        for y in range(0, size[1], step):
            for x in range(0, size[0], step):
                if (x // step + y // step) % 2: dd.rectangle((x, y, x + step - 1, y + step - 1), fill=(50, 50, 54, 255))
        return im
    for x, label, im, size in ((24, "REF ships-01 #1", ref, (200, 200)), (264, "B hero 256px", sprite, (200, 200)), (504, "B actual 64px", actual64, (200, 200)), (744, "64px alpha silhouette", black, (200, 200))):
        d.text((x, 91), label, font=ImageFont.truetype(fb, 13), fill=(110, 225, 245))
        base = checker((200, 200)); thumb = im.convert("RGBA").resize((180, 180), Image.LANCZOS); base.alpha_composite(thumb, (10, 10)); board.paste(base.convert("RGB"), (x, 116))
    d.text((24, 340), "Region crops (same exported sprite; see hero_panel_metrics.csv for raw values)", font=ImageFont.truetype(fb, 15), fill=(110, 225, 245))
    for i, (name, box) in enumerate(regions.items()):
        x = 24 + i * 200
        crop = sprite.crop(box).resize((150, 150), Image.LANCZOS)
        base = checker((170, 170)); base.alpha_composite(crop, (10, 10)); board.paste(base.convert("RGB"), (x, 372))
        d.text((x + 5, 550), name, font=ImageFont.truetype(fr, 11), fill=(206, 219, 232))
    d.text((24, 601), "Static only: no motion/0.2s test, no engine pivot/placement, no auditor aesthetic verdict.", font=ImageFont.truetype(fr, 12), fill=(164, 181, 201))
    board.save(args.out / "hero_64px_probe.png", optimize=True)
    print(args.out / "hero_64px_probe.png")


if __name__ == "__main__": main()
