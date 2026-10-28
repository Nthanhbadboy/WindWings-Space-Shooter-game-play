#!/usr/bin/env python3
"""Build review-only, same-footprint comparisons for the a71412d3 findings.

The reference is never copied into a game asset. Every row records the source
sheet/crop and SHA-256. Run with an extracted pinned spec tree, for example:
  python3 art/audit_a71412d_response/build_comparisons.py \
    --spec-root /tmp/ww_tools --out art/audit_a71412d_response/comparisons
"""
from __future__ import annotations
import argparse, csv, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def font(n, bold=False): return ImageFont.truetype(FONT_B if bold else FONT, n)


def foreground_box(im):
    im = im.convert("RGB"); w, h = im.size; xy = []
    for y in range(h):
        for x in range(w):
            r, g, b = im.getpixel((x, y)); mx = max(r, g, b); mn = min(r, g, b)
            if mx >= 75 or (mx >= 50 and mx - mn >= 18): xy.append((x, y))
    if not xy: return (0, 0, w, h)
    return (max(0, min(x for x, y in xy) - 3), max(0, min(y for x, y in xy) - 3),
            min(w, max(x for x, y in xy) + 4), min(h, max(y for x, y in xy) + 4))


def ref_image(spec, ref):
    kind, rel, tile, box, mode = ref
    im = Image.open(spec / rel).convert("RGB")
    if kind == "screen": return im, rel, (0, 0, im.width, im.height), mode
    col, row = (tile - 1) % 8, (tile - 1) // 8
    x, y = col * 150, 26 + row * 150
    bounds = (x + box[0], y + box[1], x + box[2], y + box[3]) if box else (x, y, x + 150, min(y + 134, im.height))
    if mode == "subject" and not box:
        dx0, dy0, dx1, dy1 = foreground_box(im.crop(bounds))
        bounds = (bounds[0] + dx0, bounds[1] + dy0, bounds[0] + dx1, bounds[1] + dy1)
    return im.crop(bounds), rel, bounds, mode


def candidate(path, mode):
    im = Image.open(path).convert("RGBA")
    if mode == "subject" and im.getchannel("A").getextrema() != (255, 255):
        mask = im.getchannel("A").point(lambda a: 255 if a > 8 else 0)
        bb = mask.getbbox()
        if bb: im = im.crop((max(0, bb[0] - 3), max(0, bb[1] - 3), min(im.width, bb[2] + 3), min(im.height, bb[3] + 3)))
    return im


def fit(im, n=194):
    scale = n / max(im.width, im.height)
    return im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.Resampling.LANCZOS)


def checker(n=220):
    im = Image.new("RGB", (n, n), (38, 38, 42)); d = ImageDraw.Draw(im)
    for y in range(0, n, 12):
        for x in range(0, n, 12):
            if (x // 12 + y // 12) % 2: d.rectangle((x, y, x + 11, y + 11), fill=(50, 50, 54))
    return im


def tile(name, number, box=None, mode="subject"):
    filename = f"{name}.jpg" if name.startswith("unclassified-") else f"{name}-01.jpg"
    return ("tile", f"docs/assets/contact-sheets/{filename}", number, box, mode)


def screen(name): return ("screen", f"docs/apk-analysis/ramus/2026-10-23-phone/{name}.png", None, None, "frame")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--spec-root", type=Path, required=True)
    ap.add_argument("--root", type=Path, default=Path(".")); ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(); spec = args.spec_root.resolve(); root = args.root.resolve(); args.out.mkdir(parents=True, exist_ok=True)
    B = lambda rel: rel
    boards = [
        ("01_hero_calibration", "P0 HERO / decoded player IDs — REF vs Variant B", [
            ("Ship 10001 / hero candidate", tile("ships", 1), B("art/w1-player-b/sprites/ships/player_ship_01_256@solar.png")),
            ("Ship 10004 / twin-prong gunship", tile("ships", 4), B("art/w1-player-b/sprites/ships/player_ship_04_256@solar.png")),
            ("Ship 10008 / astrolabe ring", tile("ships", 8), B("art/w1-player-b/sprites/ships/player_ship_08_256@solar.png")),
            ("Ship 10012 / mecha-valkyrie", tile("ships", 12), B("art/w1-player-b/sprites/ships/player_ship_12_256@solar.png")),
            ("Ship 10013 / articulated heavy wings", tile("ships", 13), B("art/w1-player-b/sprites/ships/player_ship_13_256@solar.png")),
            ("Ship 10015 / tri-hull nacelles", tile("ships", 15), B("art/w1-player-b/sprites/ships/player_ship_15_256@solar.png")),
            ("Ship 10016 / crescent phantom", tile("ships", 16), B("art/w1-player-b/sprites/ships/player_ship_16_256@solar.png")),
            ("Ship 10025 / twin-rotor stealth", tile("ships", 25), B("art/w1-player-b/sprites/ships/player_ship_25_256@solar.png")),
            ("Drone 20001 / sniper turret pod", tile("drones", 1), B("art/w1-player-b/sprites/drones/player_drone_01_128@cyan.png")),
            ("Drone 20004 / orb + hinged guards", tile("drones", 4), B("art/w1-player-b/sprites/drones/player_drone_04_128@cyan.png")),
            ("Drone 20005 / twin-prong drone", tile("drones", 5), B("art/w1-player-b/sprites/drones/player_drone_05_128@cyan.png")),
        ]),
        ("02_boss_decoded_ids", "W3 / exact decoded boss IDs 7001–7010 — REF vs Variant B", [
            (f"Boss {gid}", tile("bosses", tile_no), B(f"art/w3-boss-b/sprites/bodies/{file}"))
            for gid, tile_no, file in [
                (7001, 2, "boss_body_04_citadel_mk1_512@crimson.png"),
                (7002, 3, "boss_body_05_arachnid_mk1_512@emerald.png"),
                (7003, 4, "boss_body_06_leviathan_mk1_512@amber.png"),
                (7004, 5, "boss_body_07_chronos_mk1_512@violet.png"),
                (7005, 6, "boss_body_08_seraph_mk1_512@magenta.png"),
                (7006, 7, "boss_body_09_kraken_mk1_512@crimson.png"),
                (7010, 9, "boss_body_11_colossus_mk1_512@amber.png"),
            ]
        ]),
        ("03_enemy_anchors", "W2 / dedicated enemy anchors (zero player/boss reuse) — REF vs Variant B", [
            ("Orb / central core", tile("enemy", 1), B("art/w2-enemy-b/sprites/bodies/enemy_body_06_swarmling_pod_128@amber.png")),
            ("Red hull / items #2", tile("items", 2), B("art/w2-enemy-b/sprites/bodies/enemy_body_05_beetle_cruiser_128@crimson.png")),
            ("Green hull / items #3", tile("items", 3), B("art/w2-enemy-b/sprites/bodies/enemy_body_18_phantom_hex_128@violet.png")),
            ("Narrow red dart / Enemytut #16", tile("enemy", 16), B("art/w2-enemy-b/sprites/bodies/enemy_body_01_scout_dart_128@crimson.png")),
            ("AP-0067 Enemy_Hp white fill", tile("enemy", 2), B("art/w2-enemy-b/sprites/bodies/enemy_body_22_hp_pip_bar_128@crimson.png")),
        ]),
        ("04_w5_semantics", "W5 / function-specific slots — REF vs Variant B", [
            ("ShopIcon 2871", tile("ui", 50), B("art/w5-full-b/sprites/ui/u-shop/ui_ap_0443_shop_shopping_basket_256@crimson.png")),
            ("nennutevent 2943", tile("unclassified-24", 34), B("art/w5-full-b/sprites/ui/u-shop/ui_ap_0462_shop_event_banner_frame_256@azure.png")),
            ("Blink 2895", tile("unclassified-02", 57), B("art/w5-full-b/sprites/ui/u-kit/ui_ap_0264_kit_blink_horizontal_flare_256@cyan.png")),
            ("Goicoin1 3045 / coin pile", tile("unclassified-12", 14), B("art/w5-full-b/sprites/ui/u-icon/ui_ap_0191_icon_coin_pile_64@solar.png")),
        ]),
        ("05_w0_concept_hierarchy", "W0 / gameplay reference vs CONCEPT stills (not runtime captures)", [
            ("Scene 1 / formation", screen("p_2_Game"), B("art/w0-listing-b/huawei-appgallery/huawei_screenshot_1_450x800.png")),
            ("Scene 2 / boss staging", screen("slow_8_Game"), B("art/w0-listing-b/huawei-appgallery/huawei_screenshot_2_450x800.png")),
            ("Scene 3 / player + effects", screen("p_4_Game"), B("art/w0-listing-b/huawei-appgallery/huawei_screenshot_3_450x800.png")),
            ("Scene 4 / beam + impact", screen("live_1_Game"), B("art/w0-listing-b/huawei-appgallery/huawei_screenshot_4_450x800.png")),
        ]),
    ]
    index = []
    for name, title, rows in boards:
        width, left, top, row_h = 570, 24, 96, 278
        out = Image.new("RGB", (width, top + row_h * len(rows) + 38), (13, 18, 28)); d = ImageDraw.Draw(out)
        d.text((left, 13), title, fill=(241, 244, 249), font=font(17, True))
        d.text((left, 42), "Same maximum subject/frame footprint · reference-only · NOT game assets", fill=(188, 198, 210), font=font(10))
        d.text((left, 68), "REFERENCE", fill=(114, 206, 221), font=font(12, True))
        d.text((left + 270, 68), "VARIANT B / CURRENT HEAD", fill=(114, 206, 221), font=font(12, True))
        for n, (label, ref, rel) in enumerate(rows, 1):
            y = top + (n - 1) * row_h
            d.text((left, y), f"{n}. {label}", fill=(242, 224, 178), font=font(12, True))
            rim, rrel, rbox, mode = ref_image(spec, ref)
            path = root / rel
            for x, im in ((left, rim), (left + 270, candidate(path, mode))):
                base = checker(); fitted = fit(im).convert("RGBA")
                base.paste(fitted, ((220 - fitted.width) // 2, (220 - fitted.height) // 2), fitted)
                out.paste(base, (x, y + 23)); d.rectangle((x, y + 23, x + 220, y + 243), outline=(66, 79, 99), width=1)
            d.text((left, y + 249), Path(rrel).name + (f" #{ref[2]}" if ref[2] else ""), fill=(183, 193, 208), font=font(9))
            d.text((left + 270, y + 249), Path(rel).name[:39], fill=(183, 193, 208), font=font(9))
            index.append({"board": name + ".png", "row": n, "description": label, "reference": rrel,
                          "tile": ref[2] or "", "reference_crop_xyxy": str(rbox), "reference_sha256": sha(spec / rrel),
                          "display_mode": mode, "candidate_path": rel, "candidate_sha256": sha(path)})
        d.text((left, out.height - 25), "Static visual evidence only; runtime/pivot/motion remain UNVERIFIED.", fill=(153, 165, 183), font=font(10))
        out.save(args.out / (name + ".png"), optimize=True)
        print(args.out / (name + ".png"))
    with (args.out / "index.csv").open("w", encoding="utf-8", newline="") as f:
        fields = list(index[0]); w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(index)
    print(f"Indexed {len(index)} pairs")


if __name__ == "__main__": main()
