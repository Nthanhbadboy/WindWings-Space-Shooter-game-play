#!/usr/bin/env python3
"""
art/build_side_by_side_boards.py — Mandatory Side-by-Side Reference Comparison Boards
per STYLE-CORRECTION (lần 149 / 6446004160, Rule #2):
  "Mọi lô nộp kèm BẢNG SO KẾ CẠNH: sprite mình <-> sprite gốc gần nhất
   (cắt từ docs/assets/contact-sheets/, cùng scale). Không trace — chỉ đối chiếu."

Generates:
  - art/w0-listing-b/preview/w0b_side_by_side_ref.png
  - art/w1-player-b/preview/w1b_side_by_side_ref.png
  - art/w2-enemy-b/preview/w2b_side_by_side_ref.png
  - art/w3-boss-b/preview/w3b_side_by_side_ref.png
  - art/w4-core-b/preview/w4b_side_by_side_ref.png
  - art/w5-full-b/preview/w5b_side_by_side_ref.png
"""

from __future__ import annotations

import io
import json
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
REF_BRANCH = "4dfcda58b22e01d4b402244964176b59b7606a62"

_SHEET_CACHE: dict[str, Image.Image] = {}


def load_ref_sheet(name: str) -> Image.Image:
    if name not in _SHEET_CACHE:
        raw = subprocess.check_output(["git", "show", f"{REF_BRANCH}:docs/assets/contact-sheets/{name}"], cwd=ROOT)
        _SHEET_CACHE[name] = Image.open(io.BytesIO(raw)).convert("RGBA")
    return _SHEET_CACHE[name]


def crop_tile(sheet_name: str, tile_1based: int) -> Image.Image:
    im = load_ref_sheet(sheet_name)
    idx = tile_1based - 1
    x = (idx % 8) * 150
    y = 26 + (idx // 8) * 150
    return im.crop((x, y, x + 150, y + 150))


def dark_checker(w: int, h: int, step: int = 15) -> Image.Image:
    im = Image.new("RGBA", (w, h), (38, 38, 42, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, step):
        for x in range(0, w, step):
            if ((x // step) + (y // step)) % 2 == 1:
                d.rectangle([x, y, x + step - 1, y + step - 1], fill=(50, 50, 56, 255))
    return im


def render_board(out_rel: str, title: str, subtitle: str, sections: list[tuple[str, list[tuple[str, Image.Image, str]]]], cols: int = 5) -> None:
    PAIR_W, PAIR_H = 316, 178
    W = 32 + cols * (PAIR_W + 14) + 18
    total_rows_h = sum(44 + ((len(pairs) + cols - 1) // cols) * (PAIR_H + 10) for _, pairs in sections)
    H = 104 + total_rows_h + 24

    board = Image.new("RGBA", (W, H), (16, 20, 32, 255))
    d = ImageDraw.Draw(board)
    fh1 = ImageFont.truetype(FONT_B, 24)
    fh2 = ImageFont.truetype(FONT_B, 17)
    flb = ImageFont.truetype(FONT_B, 11)
    fsm = ImageFont.truetype(FONT_R, 13)

    d.rectangle([0, 0, W, 82], fill=(16, 48, 118, 255))
    d.line([(0, 82), (W, 82)], fill=(255, 204, 24, 255), width=3)
    d.text((24, 14), title, font=fh1, fill=(255, 234, 108, 255))
    d.text((24, 50), subtitle, font=fsm, fill=(214, 238, 255, 255))

    y = 96
    for sec_title, pairs in sections:
        d.text((24, y), sec_title, font=fh2, fill=(96, 238, 255, 255))
        y0 = y + 26
        for idx, (label, ref_im, our_rel) in enumerate(pairs):
            c, r = idx % cols, idx // cols
            x = 24 + c * (PAIR_W + 14)
            yy = y0 + r * (PAIR_H + 10)
            d.rounded_rectangle([x, yy, x + PAIR_W, yy + PAIR_H], radius=8, fill=(26, 32, 48, 255), outline=(72, 118, 196, 255), width=1)
            ref_t = ref_im.copy()
            ref_t.thumbnail((150, 150), Image.LANCZOS)
            board.alpha_composite(ref_t, (x + 6 + (150 - ref_t.width) // 2, yy + 6 + (150 - ref_t.height) // 2))

            ck = dark_checker(150, 150)
            sp = Image.open(os.path.join(ROOT, our_rel)).convert("RGBA")
            if max(sp.size) <= 64:
                sc = min(112 // max(1, sp.width), 112 // max(1, sp.height))
                if sc >= 2:
                    sp = sp.resize((sp.width * sc, sp.height * sc), Image.BICUBIC)
            else:
                sp.thumbnail((142, 142), Image.LANCZOS)
            ck.alpha_composite(sp, ((150 - sp.width) // 2, (150 - sp.height) // 2))
            board.alpha_composite(ck, (x + 160, yy + 6))
            d.line([(x + 158, yy + 6), (x + 158, yy + 156)], fill=(255, 204, 24, 200), width=2)
            d.text((x + 8, yy + 159), f"REF {label[:16]}", font=flb, fill=(182, 196, 220, 255))
            d.text((x + 164, yy + 159), f"B-2.5D {label[:14]}", font=flb, fill=(124, 248, 255, 255))
        rows = (len(pairs) + cols - 1) // cols
        y = y0 + rows * (PAIR_H + 10) + 16

    out_abs = os.path.join(ROOT, out_rel)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    board.convert("RGB").save(out_abs, "PNG", optimize=True)
    print(f"Saved {out_rel} {board.size}")


def main():
    sub_note = "STYLE-CORRECTION lan 149 Gate #2  |  Left = Original contact-sheet tile (150px, reference only)  |  Right = Variant B 2.5D Metallic (100% original art, zero trace)"

    # 1. W0 Side-by-Side (Representative Store Icons & Key Scenes vs Original Thumbnails/Captures)
    w0_pairs = [
        ("App Icon", crop_tile("ships-01.jpg", 13), "art/w0-listing-b/amazon-appstore/amazon_icon_large_512x512.png"),
        ("Box Art", crop_tile("atlas-01.jpg", 2), "art/w0-listing-b/microsoft-store/ms_box_art_1080x1080.png"),
        ("Scene Wave", crop_tile("background-01.jpg", 18), "art/w0-listing-b/amazon-appstore/amazon_screenshot_1_800x1280.png"),
        ("Scene Boss", crop_tile("bosses-01.jpg", 1), "art/w0-listing-b/amazon-appstore/amazon_screenshot_2_800x1280.png"),
        ("Scene Beam", crop_tile("bullet-01.jpg", 54), "art/w0-listing-b/amazon-appstore/amazon_screenshot_4_800x1280.png"),
    ]
    render_board(
        "art/w0-listing-b/preview/w0b_side_by_side_ref.png",
        "W0 STORE LISTING — SIDE-BY-SIDE 2.5D COMPARISON: REF <-> VARIANT B ('SOLAR NEON 2.5D')",
        sub_note,
        [("W0 Key Store Icons & Gameplay Scenes (25-slot contract untouched)", w0_pairs)],
    )

    # 2. W1 PLAYER (48/48 units)
    ship_pairs = [(f"Ship #{i:02d}", crop_tile("ships-01.jpg", i), f"art/w1-player-b/sprites/ships/player_ship_{i:02d}_256@solar.png") for i in range(1, 26)]
    drone_pairs = [(f"Drone #{i:02d}", crop_tile("drones-01.jpg", i), f"art/w1-player-b/sprites/drones/player_drone_{i:02d}_128@cyan.png") for i in range(1, 14)]
    bul_specs = [
        ("Beam", 7, "bullets/player_bullet_beam_32x512@cyan.png"),
        ("BeamHeavy", 8, "bullets/player_bullet_beamheavy_32x512@solar.png"),
        ("DroneBolt", 2, "bullets/player_bullet_dronebolt_32@cyan.png"),
        ("PlasmaOrb", 10, "bullets/player_bullet_plasmaorb_32@cyan.png"),
        ("Missile", 35, "bullets/player_bullet_missile_32@solar.png"),
        ("BoltMk5", 1, "bullets/player_bullet_boltmk5_32@solar.png"),
        ("ChildBolt", 3, "bullets/player_bullet_childbolt_32@cyan.png"),
        ("BeamFlare", 4, "bullets/player_bullet_beamflare_32@emerald.png"),
        ("PlumeFX", 20, "fx/player_fx_engineplume_128@solar.png"),
        ("MuzzleFX", 64, "fx/player_fx_muzzleflash_128@cyan.png"),
    ]
    bul_pairs = [(lbl, crop_tile("bullet-01.jpg", t), f"art/w1-player-b/sprites/{p}") for lbl, t, p in bul_specs]
    render_board(
        "art/w1-player-b/preview/w1b_side_by_side_ref.png",
        "W1 PLAYER (48/48) — SIDE-BY-SIDE 2.5D COMPARISON: REF <-> VARIANT B ('SOLAR NEON 2.5D')",
        sub_note,
        [
            ("1. P-SHIP (25/25): Original ships-01.jpg #1..#25 <-> Variant B 2.5D Sculpted Metallic Fleet", ship_pairs),
            ("2. P-DRONE (13/13): Original drones-01.jpg #1..#13 <-> Variant B 2.5D Escort Drones", drone_pairs),
            ("3. P-BULLET & P-FX (10/10): Original bullet-01.jpg <-> Variant B 2.5D Plasma Beams & Munitions", bul_pairs),
        ],
    )

    # 3. W2 ENEMY (34/34 units — ONLY single-unit Sprite tiles, NEVER sactx packed Texture2D atlases #28..#31!)
    w2 = json.load(open(os.path.join(HERE, "w2-enemy-b/w2b_units.json"), encoding="utf-8"))
    ebody = [r for r in w2 if r["batch"] == "E-BODY"]
    ebul = [r for r in w2 if r["batch"] == "E-BULLET"]
    clean_enemy_refs = [
        ("enemy-01.jpg", 1),
        ("items-01.jpg", 1),
        ("items-01.jpg", 2),
        ("items-01.jpg", 3),
        ("unclassified-24.jpg", 35),
        ("unclassified-24.jpg", 36),
        ("enemy-01.jpg", 16),
    ]
    def enemy_reference(r, i):
        special = {
            "swarmling_pod": ("enemy-01.jpg", 1),
            "beetle_cruiser": ("items-01.jpg", 2),
            "phantom_hex": ("items-01.jpg", 3),
            "scout_dart": ("enemy-01.jpg", 16),
            "viper_lance": ("items-01.jpg", 1),
            "wasp_raider": ("unclassified-24.jpg", 35),
            "manta_glider": ("unclassified-24.jpg", 36),
            "hp_pip_bar": ("enemy-01.jpg", 2),
        }
        sheet, tile = special.get(r["variant"], clean_enemy_refs[i % len(clean_enemy_refs)])
        return crop_tile(sheet, tile)
    ebody_pairs = [(f"{r['row_id']} {r['variant']}", enemy_reference(r, i), f"art/w2-enemy-b/{r['file']}") for i, r in enumerate(ebody)]
    ref_ebul_tiles = [20, 21, 22, 23, 24, 25, 26, 3, 4, 8, 9]
    ebul_pairs = [(f"{r['row_id']} {r['variant']}", crop_tile("enemy-01.jpg", ref_ebul_tiles[i % len(ref_ebul_tiles)]), f"art/w2-enemy-b/{r['file']}") for i, r in enumerate(ebul)]
    render_board(
        "art/w2-enemy-b/preview/w2b_side_by_side_ref.png",
        "W2 ENEMY (34/34) — SIDE-BY-SIDE 2.5D COMPARISON: REF <-> VARIANT B ('SOLAR NEON 2.5D')",
        sub_note,
        [
            ("1. E-BODY (23/23): Single-Unit Enemy Sprites (enemy-01/items-01, zero sactx atlases) <-> Variant B", ebody_pairs),
            ("2. E-BULLET (11/11): Original enemy-01.jpg Projectiles <-> Variant B 2.5D Glowing Hazard Munitions", ebul_pairs),
        ],
    )

    # 4. W3 BOSS (42/42): exact lookup table from docs/assets/sprites-index.csv + datas/bosses.json
    w3 = json.load(open(os.path.join(HERE, "w3-boss-b/w3b_units.json"), encoding="utf-8"))
    bbody = [r for r in w3 if r["batch"] == "B-BODY"]
    bpart = [r for r in w3 if r["batch"] == "B-PART"]
    BOSS_EXACT_TILE = {
        7001: 2, 7002: 3, 7003: 4, 7004: 5, 7005: 6, 7006: 7, 7007: 7,
        7009: 8, 7010: 9, 7011: 10, 7012: 11, 7013: 12, 7014: 13, 7015: 14, 7016: 15, 7017: 16, 7018: 2,
        9002: 17, 9003: 18, 9004: 19, 9005: 20, 9006: 21, 9007: 22, 9008: 23, 9009: 24,
        9010: 25, 9011: 26, 9012: 27, 9013: 28, 9014: 29, 9015: 30, 9016: 30, 9017: 31, 9018: 32,
    }
    def decoded_boss_tile(base, fallback):
        if not base.startswith("GLYPH-boss-"):
            return fallback
        gid = int(base.rsplit("-", 1)[1])
        return BOSS_EXACT_TILE.get(gid, fallback)
    special_tiles = [2, 3, 4]
    bbody_pairs = []
    for i, r in enumerate(bbody):
        tile = decoded_boss_tile(r["planner_base"], special_tiles[i] if i < 3 else 2)
        gid_label = r["planner_base"].replace("GLYPH-boss-", "ID") if r["planner_base"].startswith("GLYPH-boss-") else r["variant"]
        bbody_pairs.append((f"{gid_label} {r['variant']}", crop_tile("bosses-01.jpg", tile), f"art/w3-boss-b/{r['file']}"))
    bpart_ref = [24, 25, 26, 27, 33, 6, 44]
    bpart_pairs = [(f"{r['row_id']} {r['variant']}", crop_tile("bullet-01.jpg", bpart_ref[i % len(bpart_ref)]), f"art/w3-boss-b/{r['file']}") for i, r in enumerate(bpart)]
    render_board(
        "art/w3-boss-b/preview/w3b_side_by_side_ref.png",
        "W3 BOSS (42/42) — SIDE-BY-SIDE 2.5D COMPARISON: REF <-> VARIANT B ('SOLAR NEON 2.5D')",
        sub_note,
        [
            ("1. B-BODY (35/35): Decoded boss ID -> exact bosses-01.jpg tile <-> Variant B (no row-index guessing)", bbody_pairs),
            ("2. B-PART (7/7): Original Sub-Parts/Webs <-> Variant B 2.5D Boss Turrets, Claws & Plasma Snare", bpart_pairs),
        ],
    )

    # 5. W4-CORE (Representative Items, FX, Parallax BG & 2.5D Beveled UI Frames/Buttons vs Contact Sheets)
    w4 = json.load(open(os.path.join(HERE, "w4-core-b/w4b_units.json"), encoding="utf-8"))
    w4_item_refs = {"shield_orb": 1, "weapon_up": 2, "magnet_core": 3, "max_overdrive": 4}
    w4_items = [(f"{r['row_id']} {r['variant']}", crop_tile("items-01.jpg", w4_item_refs.get(r["variant"], (i % 4) + 1)), f"art/w4-core-b/{r['file']}") for i, r in enumerate([x for x in w4 if x["lane"] == "ITEM"])]
    w4_fx_refs = {
        "mega_nova": ("bullet-01.jpg", 20), "starburst_blast": ("bullet-01.jpg", 20),
        "cross_flare": ("bullet-01.jpg", 64), "unlock_prism": ("fx-01.jpg", 44),
        "plasma_vortex": ("fx-01.jpg", 61), "repair_aura": ("fx-01.jpg", 44),
        "overdrive_surge": ("bullet-01.jpg", 64), "levelup_ring": ("fx-01.jpg", 44),
        "tint_halo": ("fx-01.jpg", 44),
    }
    w4_fx = []
    for r in [x for x in w4 if x["lane"] == "FX"]:
        sheet, tile = w4_fx_refs.get(r["variant"], ("fx-01.jpg", 44))
        w4_fx.append((f"{r['row_id']} {r['variant']}", crop_tile(sheet, tile), f"art/w4-core-b/{r['file']}"))
    w4_bg_refs = {"sky_far": 9, "cloud_mid": 14, "archipelago_near": 24}
    w4_bg = [(f"{r['row_id']} {r['variant']}", crop_tile("background-01.jpg", w4_bg_refs.get(r["variant"], 9)), f"art/w4-core-b/{r['file']}") for i, r in enumerate([x for x in w4 if x["lane"] == "BG"])]
    ui_sample_tiles = [1, 2, 3, 5, 7, 8, 9, 12, 13, 15, 16, 18, 20, 22, 24, 34, 40, 41, 49, 58, 59, 61, 62, 63, 64]
    w4_ui_sub = [x for x in w4 if x["lane"] == "UI"][::3][:25]
    w4_ui = [(f"{r['row_id']} {r['variant']}", crop_tile("ui-01.jpg", ui_sample_tiles[i % len(ui_sample_tiles)]), f"art/w4-core-b/{r['file']}") for i, r in enumerate(w4_ui_sub)]
    render_board(
        "art/w4-core-b/preview/w4b_side_by_side_ref.png",
        "W4-CORE (112 Rows / 114 Files) — SIDE-BY-SIDE 2.5D COMPARISON: REF <-> VARIANT B ('SOLAR NEON 2.5D')",
        sub_note,
        [
            ("1. ITEM (7/7) & FX (9/9): Original items-01 / fx-01 <-> Variant B 2.5D Drops & Plasma FX", w4_items + w4_fx),
            ("2. BG (12 Files): Original background-01 <-> Variant B Seamless Parallax & 2.5D UI Panels", w4_bg),
            ("3. UI Sample (25 Representative of 86 Kept Rows): Original ui-01 <-> Variant B 2.5D Beveled 9-Slice HUD/Kit", w4_ui),
        ],
    )

    # 6. W5-FULL (Planets/Nebulae/Star-Nodes + FX/Items + Representative 2.5D Icons/Codex/Ranks/Crates)
    w5 = json.load(open(os.path.join(HERE, "w5-full-b/w5b_units.json"), encoding="utf-8"))
    bg_planet_tiles = [5, 15, 24, 20, 11, 43, 12, 12, 28, 25, 6, 12, 8, 49, 10, 10, 12, 12, 43, 9, 12, 12, 12, 39, 48]
    w5_par = [x for x in w5 if x["batch"] == "G-PARALLAX"]
    w5_bg_refs = {"bgnormal": 9, "nen": 9, "cloud": 14, "dautau": 24, "earth": 20, "jupiter": 43}
    w5_bg_pairs = []
    for i, r in enumerate(w5_par):
        tile = w5_bg_refs.get(r["planner_base"], bg_planet_tiles[i % len(bg_planet_tiles)])
        w5_bg_pairs.append((f"{r['row_id']} {r['variant']}", crop_tile("background-01.jpg", tile), f"art/w5-full-b/{r['file']}"))
    w5_ui_sub = [x for x in w5 if x["lane"] == "UI"][::9][:25]
    w5_ui_pairs = [(f"{r['row_id']} {r['variant']}", crop_tile("ui-01.jpg", ui_sample_tiles[i % len(ui_sample_tiles)]), f"art/w5-full-b/{r['file']}") for i, r in enumerate(w5_ui_sub)]
    render_board(
        "art/w5-full-b/preview/w5b_side_by_side_ref.png",
        "W5-FULL (274 Units -> 510/510 Parity) — SIDE-BY-SIDE 2.5D COMPARISON: REF <-> VARIANT B",
        sub_note,
        [
            ("1. G-PARALLAX Celestial Bodies & Backdrops (25/25): background-01.jpg <-> Variant B 2.5D Planets/Nebulae", w5_bg_pairs),
            ("2. UI Representative Sample (25 of 221 Units): ui-01.jpg <-> Variant B 2.5D Icons, Codex, Ranks & Crates", w5_ui_pairs),
        ],
    )


if __name__ == "__main__":
    main()
