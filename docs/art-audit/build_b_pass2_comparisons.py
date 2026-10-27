#!/usr/bin/env python3
"""Review-only original/old/new comparisons for B pass-2, not game assets.

For subjects, the first three columns fit the visible bounding boxes to the
same maximum footprint. The last column, where shown, is the new *full canvas*
resized to 64x64 actual display pixels, not an engine screenshot. Original
JPEG tiles are low-resolution; their enlarged detail cannot prove line width.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
import build_comparisons as common


def ship(n: int) -> str:
    return f"art/w1-player-b/sprites/ships/player_ship_{n:02d}_256@solar.png"


def boss(n: int, name: str, color: str) -> str:
    return f"art/w3-boss-b/sprites/bodies/boss_body_{n:02d}_{name}_512@{color}.png"


def frame(n: int) -> str:
    return f"art/w0-listing-b/huawei-appgallery/huawei_screenshot_{n}_450x800.png"


# Labels disclose when an original is a visual analogue rather than a verified
# unit-number mapping. Boss rows use explicit GLYPH-boss-ID manifest mapping.
LATEST_W5_PATHS = {
    "art/w5-full-b/sprites/ui/u-shop/ui_ap_0443_shop_shopicon_256@azure.png":
        "art/w5-full-b/sprites/ui/u-shop/ui_ap_0443_shop_shopping_basket_256@crimson.png",
    "art/w5-full-b/sprites/ui/u-shop/ui_ap_0462_shop_btn_event_banner_256@azure.png":
        "art/w5-full-b/sprites/ui/u-shop/ui_ap_0462_shop_event_banner_frame_256@azure.png",
    "art/w5-full-b/sprites/ui/u-kit/ui_ap_0264_kit_blink_256@azure.png":
        "art/w5-full-b/sprites/ui/u-kit/ui_ap_0264_kit_blink_horizontal_flare_256@cyan.png",
    "art/w5-full-b/sprites/ui/u-icon/ui_ap_0191_icon_coin_pack_64@solar.png":
        "art/w5-full-b/sprites/ui/u-icon/ui_ap_0191_icon_coin_pile_64@solar.png",
}

BOARDS = [
    ("12_b_pass2_player", "PLAYER B: original vs pass-1 vs pass-2", True, [
        ("Hero #01 / ref ship #1 (visual analogue)", common.sheet("ships", 1), ship(1)),
        ("Hero #04 / ref ship #4 (visual analogue)", common.sheet("ships", 4), ship(4)),
        ("Fleet #08 / ref ship #8 (visual analogue)", common.sheet("ships", 8), ship(8)),
        ("Fleet #12 / ref ship #12 (visual analogue)", common.sheet("ships", 12), ship(12)),
        ("Drone #04 / ref drone #4 (visual analogue)", common.sheet("drones", 4),
         "art/w1-player-b/sprites/drones/player_drone_04_128@cyan.png"),
    ]),
    ("13_b_pass2_w0", "W0 B: reference frames vs concept revisions", False, [
        ("Icon finish only: original ship is NOT the original store icon", common.sheet("ships", 1),
         "art/w0-listing-b/amazon-appstore/amazon_icon_large_512x512.png"),
        ("Scene 1: formation (not same frame or runtime)", common.screen("p_2_Game"), frame(1)),
        ("Scene 2: boss (not same frame or runtime)", common.screen("slow_8_Game"), frame(2)),
        ("Scene 3: action (not same frame or runtime)", common.screen("p_4_Game"), frame(3)),
        ("Scene 4: beam/impact (not same frame or runtime)", common.screen("live_1_Game"), frame(4)),
    ]),
    ("14_b_pass2_boss", "BOSS B: mapped IDs in both manifests", False, [
        ("ID 7001 / original bosses-01 #2", common.sheet("bosses", 2), boss(4, "citadel_mk1", "crimson")),
        ("ID 7002 / original bosses-01 #3", common.sheet("bosses", 3), boss(5, "arachnid_mk1", "emerald")),
        ("ID 7003 / original bosses-01 #4", common.sheet("bosses", 4), boss(6, "leviathan_mk1", "amber")),
        ("ID 7004 / original bosses-01 #5", common.sheet("bosses", 5), boss(7, "chronos_mk1", "violet")),
        ("ID 7005 / original bosses-01 #6", common.sheet("bosses", 6), boss(8, "seraph_mk1", "magenta")),
    ]),
    ("15_b_pass2_enemy", "ENEMY B: three illustrative analogues", False, [
        ("Pod / orb analogue; not a proven unit ID", common.sheet("enemy", 1),
         "art/w2-enemy-b/sprites/bodies/enemy_body_06_swarmling_pod_128@amber.png"),
        ("Hex hull / green hull; not a proven unit ID", common.sheet("items", 3),
         "art/w2-enemy-b/sprites/bodies/enemy_body_18_phantom_hex_128@violet.png"),
        ("Red dart: original source crop just 27 x 28 pixels", common.sheet("enemy", 30, (57, 63, 84, 91)),
         "art/w2-enemy-b/sprites/bodies/enemy_body_01_scout_dart_128@crimson.png"),
    ]),
    ("16_b_pass2_w5", "W5 B: semantic slots still collapse to same bytes", False, [
        ("ShopIcon / AP-0443 (same bytes as AP-0462)", common.sheet("ui", 50),
         "art/w5-full-b/sprites/ui/u-shop/ui_ap_0443_shop_shopicon_256@azure.png"),
        ("Event slot / AP-0462 (same bytes as AP-0443)", common.sheet("unclassified-24", 34),
         "art/w5-full-b/sprites/ui/u-shop/ui_ap_0462_shop_btn_event_banner_256@azure.png"),
        ("Blink / AP-0264 (same bytes as AP-0251 tech node)", common.sheet("unclassified-02", 57),
         "art/w5-full-b/sprites/ui/u-kit/ui_ap_0264_kit_blink_256@azure.png"),
        ("Coin pack / AP-0191 (same bytes as AP-0181 coin icon)", common.sheet("unclassified-12", 14),
         "art/w5-full-b/sprites/ui/u-icon/ui_ap_0191_icon_coin_pack_64@solar.png"),
    ]),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec-root", type=Path, required=True)
    ap.add_argument("--old-root", type=Path, required=True)
    ap.add_argument("--new-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--latest", action="store_true", help="compare round-2 against audit-response")
    args = ap.parse_args()
    spec, old, new = args.spec_root.resolve(), args.old_root.resolve(), args.new_root.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    index = []
    boards = list(BOARDS)
    if args.latest:
        boards.append(("17_b_pass2_unfixed_fleet", "PLAYER B: unchanged fleet samples", True, [
            (f"Ship #{n:02d} / ref #{n} (declared ID; binding unknown)", common.sheet("ships", n), ship(n))
            for n in (2, 6, 11, 23, 25)
        ]))
        boards.append(("18_b_pass2_core", "W4/W5 B: background, FX and item samples", False, [
            ("Sky layer / atmospheric analogue", common.sheet("background", 9, mode="frame"),
             "art/w4-core-b/sprites/bg/bg_parallax_01_sky_far_1024@cerulean.png"),
            ("Earth-like planet / visual analogue", common.sheet("background", 20),
             "art/w5-full-b/sprites/bg/parallax/bg_ap_0094_planet_earth_terra_1024@cerulean.png"),
            ("Jupiter / visual analogue", common.sheet("background", 43),
             "art/w5-full-b/sprites/bg/parallax/bg_ap_0096_planet_jupiter_giant_1024@solar.png"),
            ("Shield-like pickup / visual analogue", common.sheet("items", 1),
             "art/w4-core-b/sprites/items/item_drop_02_shield_orb_128@cyan.png"),
            ("Impact / explosion analogue", common.sheet("bullet", 20),
             "art/w4-core-b/sprites/fx/fx_boom_02_starburst_blast_256@solar.png"),
        ]))
    for name, title, has_64, rows in boards:
        if args.latest:
            number, rest = name.split("_b_pass2_", 1)
            name = f"{int(number) + 5:02d}_b_latest_{rest}"
            if rest == "player":
                title = "PLAYER B: original vs round-2 vs audit-response"
            elif rest == "w5":
                title = "W5 B: function-specific response vs round-2"
        cell, gap, left, top, row_h = 220, 30, 26, 107, 273
        cols = 4 if has_64 else 3
        width = left * 2 + cols * cell + (cols - 1) * gap
        out = Image.new("RGB", (width, top + row_h * len(rows) + 42), (13, 18, 28))
        draw = ImageDraw.Draw(out)
        draw.text((left, 13), title, fill=(241, 244, 249), font=common.font(21, True))
        draw.text((left, 44), "Reference-only | equal maximum footprint | old/new are pinned PNG exports",
                  fill=(188, 198, 210), font=common.font(12))
        labels = (["REFERENCE", "B ROUND-2", "B RESPONSE"] if args.latest else
                  ["REFERENCE", "B PASS-1", "B PASS-2"]) + (["NEW: 64 PX CANVAS"] if has_64 else [])
        for n, label in enumerate(labels):
            draw.text((left + n * (cell + gap), 71), label, fill=(114, 206, 221), font=common.font(13, True))
        for number, (label, ref, rel) in enumerate(rows, 1):
            y = top + (number - 1) * row_h
            if args.latest and rel in LATEST_W5_PATHS:
                label = label.split(" (same bytes")[0] + " / revised slot"
            draw.text((left, y), f"{number}. {label}", fill=(242, 224, 178), font=common.font(12, True))
            ref_im, ref_rel, bounds, mode = common.reference(spec, ref)
            new_rel = LATEST_W5_PATHS.get(rel, rel) if args.latest else rel
            old_path, new_path = old / rel, new / new_rel
            if not old_path.is_file() or not new_path.is_file():
                raise FileNotFoundError(f"Missing old/new asset: {rel} / {new_rel}")
            imgs = [ref_im, common.candidate(old_path, mode), common.candidate(new_path, mode)]
            if has_64:
                small = Image.open(new_path).convert("RGBA")
                small.thumbnail((64, 64), Image.Resampling.LANCZOS)
                imgs.append(small)
            for col, im in enumerate(imgs):
                x = left + col * (cell + gap)
                base = common.checker(cell)
                pic = (im if has_64 and col == 3 else common.fit(im, 194)).convert("RGBA")
                base.paste(pic, ((cell - pic.width) // 2, (cell - pic.height) // 2), pic)
                out.paste(base, (x, y + 22))
                draw.rectangle((x, y + 22, x + cell, y + 22 + cell), outline=(66, 79, 99), width=1)
            captions = [Path(ref_rel).name + (f" #{ref[2]}" if ref[2] else ""),
                        Path(rel).name, Path(new_rel).name] + (["entire canvas, not runtime"] if has_64 else [])
            for col, caption in enumerate(captions):
                draw.text((left + col * (cell + gap), y + 246), common.shorten(caption, 35),
                          fill=(183, 193, 208), font=common.font(10))
            index.append({"board": name + ".png", "row": number, "description": label,
                          "reference": ref_rel, "ref_tile": ref[2] or "",
                          "reference_crop_xyxy": str(bounds), "reference_sha256": common.sha(spec / ref_rel),
                          "display_mode": mode, "old_candidate_path": rel, "new_candidate_path": new_rel,
                          "old_sha256": common.sha(old_path), "new_sha256": common.sha(new_path),
                          "last_column": "64px full canvas; simulated" if has_64 else ""})
        draw.text((left, out.height - 27),
                  "Original JPEG crops are reference-only; 64px samples are static, not gameplay.",
                  fill=(153, 165, 183), font=common.font(11))
        output = args.out / (name + ".png")
        out.save(output, optimize=True)
        print(f"{output}: {len(rows)} rows", flush=True)
    fields = ["board", "row", "description", "reference", "ref_tile", "reference_crop_xyxy",
              "reference_sha256", "display_mode", "old_candidate_path", "new_candidate_path",
              "old_sha256", "new_sha256", "last_column"]
    index_name = "latest_index.csv" if args.latest else "pass2_index.csv"
    with (args.out / index_name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(index)
    print(f"{len(index)} reference rows indexed", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
