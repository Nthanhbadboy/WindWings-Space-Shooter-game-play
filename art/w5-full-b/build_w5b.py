#!/usr/bin/env python3
"""
Build Wave W5-full — Remaining 274 Non-EXCL Planner Units for Variant B ("Solar Neon Arcade-Pop"),
completing 510/510 (100%) of all non-EXCL units in art-planner.csv (EXCL 278 = 0).

Also builds art/w0-build-icons-b/ (ICO-06 Windows multi-res .ico + ICO-07 Android mipmap set)
without modifying art/w0-listing-b/ (25 store slots kept 100% immutable).
"""

import csv
import json
import math
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import pbr25d

AUTHOR_BRANCH = "arena/eca8588b-windwings-space-shooter-game-p"
LICENSE_NOTE = "chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OUTLINE = (24, 48, 108, 255)
DARK_WELL = (14, 34, 88, 238)
WHITE = (255, 255, 255, 255)

PAL = {
    "solar":    ((255, 204, 18, 255),  (208, 108, 0, 255),   (255, 246, 142, 255)),
    "cyan":     ((0, 218, 255, 255),   (0, 128, 196, 255),   (156, 252, 255, 255)),
    "azure":    ((28, 112, 246, 255),  (14, 58, 162, 255),   (96, 178, 255, 255)),
    "emerald":  ((0, 228, 158, 255),   (0, 138, 92, 255),    (138, 255, 214, 255)),
    "magenta":  ((255, 42, 148, 255),  (168, 12, 88, 255),   (255, 142, 208, 255)),
    "crimson":  ((255, 36, 86, 255),   (168, 10, 48, 255),   (255, 124, 154, 255)),
    "violet":   ((138, 56, 224, 255),  (72, 22, 136, 255),   (198, 138, 255, 255)),
    "pearl":    ((232, 242, 255, 255), (168, 196, 238, 255), (252, 254, 255, 255)),
    "slate":    ((92, 118, 168, 255),  (48, 66, 108, 255),   (148, 176, 224, 255)),
    "cerulean": ((22, 126, 242, 255),  (12, 68, 158, 255),   (88, 188, 255, 255)),
}


def downsample_straight_rgba(im, target_size, zero_corners=True):
    if im.size == target_size:
        arr = np.asarray(im).copy()
    else:
        f = np.asarray(im, dtype=np.float32)
        a = f[:, :, 3:4] / 255.0
        pm = Image.fromarray(np.clip(np.round(np.concatenate([f[:, :, :3] * a, f[:, :, 3:4]], axis=2)), 0, 255).astype(np.uint8), "RGBA")
        s = np.asarray(pm.resize(target_size, Image.LANCZOS), dtype=np.float32)
        sa = s[:, :, 3:4] / 255.0
        rgb = np.where(sa > 1e-3, s[:, :, :3] / np.maximum(sa, 1e-3), 0.0)
        arr = np.concatenate([np.clip(np.round(rgb), 0, 255), np.clip(np.round(s[:, :, 3:4]), 0, 255)], axis=2).astype(np.uint8)
    if zero_corners:
        arr[arr[:, :, 3] < 4] = 0
        for cy in (0, target_size[1] - 1):
            for cx in (0, target_size[0] - 1):
                arr[cy, cx] = [0, 0, 0, 0]
    return Image.fromarray(arr, "RGBA")


def reg_poly(cx, cy, rx, ry, n=16, rot=0.0):
    return [(cx + math.cos(a + rot) * rx, cy + math.sin(a + rot) * ry) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def star_poly(cx, cy, r_out, r_in, n_pts=5, rot=-math.pi / 2):
    pts = []
    for k in range(n_pts * 2):
        a = rot + k * math.pi / n_pts
        r = r_out if k % 2 == 0 else r_in
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def draw_cel_poly(canvas, pts, col_triple, outline_w=6):
    base_c, shade_c, light_c = col_triple
    pbr25d.draw_25d_metal_poly(
        canvas, pts, base_c, shade_c, light_c,
        metallic=0.86, greebles=False, cast_ao=True, glow_vent_c=(0, 228, 255),
    )


def draw_9slice_panel(canvas, box, radius, rim_triple, fill_rgba, inner_rim=None, outline_w=8):
    glow_c = (inner_rim[:3] if inner_rim is not None else (0, 224, 255))
    bw = max(6, int((box[2] - box[0]) * 0.045))
    pbr25d.draw_25d_9slice_panel(canvas, box, radius, rim_triple, fill_rgba, inner_glow_rgb=glow_c, bevel_w=bw)


def draw_centered_label(canvas, cx, cy, text, size, fill=WHITE, stroke_w=3):
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(FONT_B, size)
    bb = d.textbbox((0, 0), text, font=f)
    tx, ty = cx - (bb[2] - bb[0]) // 2, cy - (bb[3] - bb[1]) // 2 - size // 8
    d.text((tx + 2, ty + 3), text, font=f, fill=(8, 18, 48, 185))
    d.text((tx, ty), text, font=f, fill=fill)


# Functional English slug mapping so ZERO legacy Vietnamese/APK raw names leak into filenames
CLEAN_UI_SLUGS = {
    "goicoin": "coin_pack", "iconnhanqua": "gift_claim", "manh": "shard_base",
    "manhcraft": "shard_craft", "manhdrone": "drone_shard_t1", "manhdrone2.": "drone_shard_t2",
    "manhdrone3.": "drone_shard_t3", "manhdrone4.": "drone_shard_t4", "soluong": "qty_badge",
    "soluongitem": "item_qty_badge", "timesudungitem": "item_duration", "xich": "chain_lock",
    "giap": "armor_stat", "phukien": "accessory_mod", "tang suc manh": "atk_boost",
    "ti le power": "power_rate", "x150%coins": "coin_x150_boost", "manhplane": "ship_shard_t1",
    "manhplane2.": "ship_shard_t2", "manhplane3.": "ship_shard_t3", "manhplane4.": "ship_shard_t4",
    "+button": "plus_btn", "11_5": "tech_node_a", "22_1": "tech_node_b", "bom": "bomb_icon",
    "bangthongtin": "info_panel", "bong den": "hint_bulb", "hoisinh": "revive_wings",
    "mini1.": "mini_badge", "tabngay": "daily_tab", "vetinh": "satellite_pod",
    "tron xoay": "rotary_dial", "xd": "confirm_badge", "botro": "support_slot",
    "chonbotro": "support_picker", "khung": "frame_base", "khungavatar": "frame_avatar",
    "khungblackbox": "frame_blackbox", "khungfree": "frame_free", "khungiconrank": "frame_rank_icon",
    "khungicontallent": "frame_talent_icon", "khunglevelicontallent": "frame_talent_lvl",
    "khungpvp": "frame_pvp", "khungselecticontallent": "frame_talent_sel", "khungvip": "frame_vip",
    "khunghop": "frame_crate", "khungkynangvatphamroi": "frame_drop_skill", "khunglvvip": "frame_vip_lvl",
    "khungmode": "frame_mode", "khungnangcap": "frame_upgrade", "khungnv": "frame_quest",
    "khungselect": "frame_selected", "khungskill": "frame_skill", "khungskillhotro": "frame_support_skill",
    "khungthongtinhard": "frame_hard_info", "khungthongtinvip": "frame_vip_info",
    "khungvatphambf": "frame_buff_item", "khungvatphamroi": "frame_loot_drop",
    "selectbotro": "support_selected", "khung chinh": "frame_main", "khung de cac goi": "frame_pack_tray",
    "khung dem so": "frame_digit_counter", "khung doi": "frame_team", "khung time": "frame_timer",
    "khung vang ten": "frame_gold_nameplate", "randombotro": "support_random", "a": "grade_a_emblem",
    "hotsale%": "hotsale_percent", "nutads": "btn_watch_ad", "nutbuyskin": "btn_buy_skin",
    "nutchedo": "btn_game_mode", "nutgift": "btn_gift_box", "nutrs": "btn_reset",
    "nuttech": "btn_tech_tree", "nutuplv": "btn_level_up", "nutwatchads": "btn_reward_video",
    "vip0.": "vip_crest_tier0", "nennutevent": "btn_event_banner",
}


def clean_slug(base):
    if base in CLEAN_UI_SLUGS:
        return CLEAN_UI_SLUGS[base]
    s = base.lower().replace("+", "plus_").replace("%", "pct").replace(" ", "_").replace(".", "")
    s = re.sub(r"[^a-z0-9_]+", "_", s).strip("_")
    return s or "unit"


# ---------------------------------------------------------------------------
# 1. ITEM (+2: AP-0135 foot, AP-0138 rock)
# ---------------------------------------------------------------------------
def render_w5_item(base):
    S = 512
    cx, cy = 256, 256
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if base == "foot":
        draw_cel_poly(im, reg_poly(cx, cy, 204, 204, 24), PAL["pearl"], outline_w=9)
        draw_cel_poly(im, reg_poly(cx, cy, 170, 170, 24), PAL["cyan"], outline_w=7)
        boot = [(185, 128), (295, 128), (295, 268), (376, 305), (376, 368), (165, 368)]
        draw_cel_poly(im, boot, PAL["solar"], outline_w=8)
        wing = [(185, 175), (105, 125), (132, 235), (185, 245)]
        draw_cel_poly(im, wing, PAL["pearl"], outline_w=7)
        return im, "booster_thruster_boot", "solar"
    # rock -> glowing prism meteorite crystal
    draw_cel_poly(im, reg_poly(cx, cy, 204, 204, 24), PAL["pearl"], outline_w=9)
    draw_cel_poly(im, reg_poly(cx, cy, 170, 170, 24), PAL["violet"], outline_w=7)
    rock = [(256, 108), (368, 178), (382, 312), (278, 396), (154, 348), (136, 206)]
    draw_cel_poly(im, rock, PAL["magenta"], outline_w=8)
    draw_cel_poly(im, [(256, 148), (328, 215), (268, 336), (186, 265)], PAL["cyan"], outline_w=6)
    return im, "prism_meteorite", "violet"


# ---------------------------------------------------------------------------
# 2. FX (+17: AP-0088 @128 + 16 F-GLOW @256)
# ---------------------------------------------------------------------------
FX_MAP = {
    "fxenemy":             ("enemy_hit_spark",      "crimson", "burst"),
    "beemap":              ("hex_sector_pulse",     "solar",   "hex"),
    "blackhold":           ("singularity_vortex",   "violet",  "vortex"),
    "circle_blue":         ("azure_shock_ring",     "cyan",    "ring1"),
    "circle_blue copy":    ("twin_ripple_ring",     "cyan",    "ring2"),
    "circle_mask_bigboss": ("boss_target_sigil",    "crimson", "sigil"),
    "fx_footbroken":       ("armor_shatter_burst",  "solar",   "shards"),
    "gate":                ("stargate_portal_major","cyan",    "portal_lg"),
    "gatenho":             ("stargate_portal_minor","emerald", "portal_sm"),
    "ghost":               ("dash_afterimage",      "cyan",    "ghost"),
    "glow":                ("solar_radial_bloom",   "solar",   "bloom"),
    "lastboss":            ("omega_boss_corona",    "magenta", "corona"),
    "light":               ("sunbeam_flash_ray",    "solar",   "ray"),
    "overtime":            ("overtime_alarm_pulse", "crimson", "alarm"),
    "point_talent":        ("talent_node_star",     "emerald", "star4"),
    "square64x":           ("holo_tile_highlight",  "cyan",    "square"),
    "victory":             ("victory_sunburst",     "solar",   "victory"),
}


def render_w5_fx(base):
    slug, pal_key, mode = FX_MAP[base]
    S = 512
    cx, cy = 256, 256
    yy, xx = np.mgrid[0:S, 0:S]
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ang = np.arctan2(yy - cy, xx - cx)
    P = PAL[pal_key][0]
    arr = np.zeros((S, S, 4), dtype=np.float32)

    if mode in ("ring1", "ring2", "sigil", "alarm"):
        r_main = np.exp(-((rr - 178.0) / 20.0) ** 2)
        if mode == "ring2":
            r_main = np.clip(r_main + np.exp(-((rr - 116.0) / 16.0) ** 2) * 0.85, 0.0, 1.0)
        for c in range(3):
            arr[:, :, c] = P[c] * 0.75 + 255.0 * 0.25 * r_main
        arr[:, :, 3] = r_main * 245.0
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        if mode == "sigil":
            for k in range(8):
                a = k * math.pi / 4
                tx, ty = cx + math.cos(a) * 178, cy + math.sin(a) * 178
                draw_cel_poly(im, reg_poly(tx, ty, 24, 24, 4, rot=a), PAL["solar"], outline_w=5)
        elif mode == "alarm":
            draw_cel_poly(im, star_poly(cx, cy, 108, 46, 6), PAL["solar"], outline_w=6)
        return im, slug, pal_key

    if mode in ("vortex", "portal_lg", "portal_sm"):
        rad = 188.0 if mode != "portal_sm" else 138.0
        swirl = (0.5 + 0.5 * np.cos(ang * 6.0 + rr * 0.05)) ** 1.8 * np.exp(-((rr - rad * 0.72) / 56.0) ** 2)
        rim = np.exp(-((rr - rad) / 18.0) ** 2)
        a = np.clip(swirl + rim, 0.0, 1.0)
        for c in range(3):
            arr[:, :, c] = P[c] * (1.0 - rim * 0.5) + 255.0 * (rim * 0.5)
        arr[:, :, 3] = a * 250.0
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        if mode.startswith("portal"):
            draw_cel_poly(im, reg_poly(cx, cy, rad + 16, rad + 16, 6) + list(reversed(reg_poly(cx, cy, rad - 16, rad - 16, 6))), PAL[pal_key], outline_w=6)
        return im, slug, pal_key

    if mode == "square":
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw_9slice_panel(im, (68, 68, S - 69, S - 69), 28, PAL[pal_key], (0, 218, 255, 64), inner_rim=WHITE, outline_w=7)
        return im, slug, pal_key

    if mode == "hex":
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        for hx, hy in [(cx, cy), (cx - 110, cy - 64), (cx + 110, cy - 64), (cx - 110, cy + 64), (cx + 110, cy + 64)]:
            draw_cel_poly(im, reg_poly(hx, hy, 58, 58, 6), PAL[pal_key], outline_w=6)
        return im, slug, pal_key

    if mode == "ghost":
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ship_sil = [(cx, 68), (328, 215), (436, 305), (412, 375), (305, 345), (cx, 438), (207, 345), (100, 375), (76, 305), (184, 215)]
        draw_cel_poly(im, ship_sil, PAL["cyan"], outline_w=6)
        a_arr = np.asarray(im).copy()
        a_arr[:, :, 3] = (a_arr[:, :, 3].astype(np.float32) * 0.72).astype(np.uint8)
        return Image.fromarray(a_arr, "RGBA"), slug, pal_key

    # Radial rays / bursts / bloom / corona / shards / star4 / victory
    n_sp = {"burst": 8, "shards": 7, "bloom": 0, "corona": 12, "ray": 4, "star4": 4, "victory": 10}[mode]
    core = np.clip(1.0 - rr / 215.0, 0.0, 1.0) ** 1.7
    if n_sp > 0:
        rays = (0.5 + 0.5 * np.cos(ang * n_sp)) ** 2.4 * np.clip(1.0 - rr / 242.0, 0.0, 1.0)
        a = np.clip(core * 0.8 + rays * 0.9, 0.0, 1.0)
    else:
        a = core
    wh = np.clip(1.0 - rr / 96.0, 0.0, 1.0)
    for c in range(3):
        arr[:, :, c] = P[c] * (1.0 - wh) + 255.0 * wh
    arr[:, :, 3] = a * 255.0
    im = Image.fromarray(arr.astype(np.uint8), "RGBA")
    if mode in ("burst", "victory", "star4"):
        draw_cel_poly(im, star_poly(cx, cy, 198, 72, max(4, n_sp)), PAL[pal_key], outline_w=5)
    return im, slug, pal_key


# ---------------------------------------------------------------------------
# 3. BG (+34: 25 G-PARALLAX @1024x1024 + 9 G-UI @512x512)
# ---------------------------------------------------------------------------
def render_w5_parallax(base):
    S = 1024
    cx, cy = 512, 512
    # Full-bleed seamless sky/stage backdrops (4 units: bgnormal, nen, nenboss, nenboss_left)
    if base in ("bgnormal", "nen", "nenboss", "nenboss_left"):
        yy, xx = np.mgrid[0:S, 0:S]
        ang_y = 2.0 * np.pi * yy / S
        w = 0.5 - 0.5 * np.cos(ang_y)  # exact periodic function -> row[0] == row[1023]!
        arr = np.zeros((S, S, 4), dtype=np.uint8)
        if "boss" in base:
            arr[:, :, 0] = (48 + 145 * w).astype(np.uint8)
            arr[:, :, 1] = (14 + 28 * w).astype(np.uint8)
            arr[:, :, 2] = (92 + 88 * w).astype(np.uint8)
            arr[:, :, 3] = 255 if base != "nenboss_left" else np.clip(255 - (xx * 255 // 520), 0, 255).astype(np.uint8)
            pal = "crimson"
            slug = "stage_boss_alert_sky" if base == "nenboss" else "stage_boss_flank_curtain"
        else:
            arr[:, :, 0] = (18 + 52 * w).astype(np.uint8)
            arr[:, :, 1] = (112 + 96 * w).astype(np.uint8)
            arr[:, :, 2] = (232 + 22 * w).astype(np.uint8)
            arr[:, :, 3] = 255
            pal = "cerulean"
            slug = "stage_sky_normal" if base == "bgnormal" else "stage_sky_horizon"
        im = Image.fromarray(arr, "RGBA")
        if base == "nenboss_left":
            arr_c = np.asarray(im).copy()
            arr_c[0, -1] = arr_c[-1, -1] = [0, 0, 0, 0]
            im = Image.fromarray(arr_c, "RGBA")
        return im, slug, pal, (base == "nenboss_left" and False)

    # Isolated RGBA 1024x1024 celestial planets, galaxies, star-nodes, clouds & asteroids!
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    if base in ("earth", "jupiter", "mars", "moon", "saturn", "venus", "planetut"):
        p_cfg = {
            "earth":    ("planet_earth_terra",   "cerulean", (18, 96, 232),   (36, 198, 108),  (124, 224, 255), False),
            "jupiter":  ("planet_jupiter_giant", "solar",    (232, 162, 74),  (196, 78, 48),   (255, 224, 156), False),
            "mars":     ("planet_mars_crimson",  "crimson",  (186, 56, 36),   (255, 168, 32),  (255, 118, 72),  False),
            "moon":     ("planet_luna_pearl",    "pearl",    (194, 206, 228), (112, 126, 154), (225, 240, 255), False),
            "saturn":   ("planet_saturn_ringed", "solar",    (236, 192, 96),  (184, 128, 62),  (132, 238, 255), True),
            "venus":    ("planet_venus_amber",   "magenta",  (204, 88, 178),  (255, 196, 76),  (255, 156, 238), False),
            "planetut": ("planet_tutorial_orb",  "emerald",  (18, 186, 134),  (48, 238, 212),  (148, 255, 232), True),
        }[base]
        slug, pal, col_a, col_b, atmo_c, has_ring = p_cfg
        yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
        R = 296.0
        nx = (xx - cx) / R
        ny = (yy - cy) / R
        r2 = nx * nx + ny * ny
        inside = r2 <= 1.0
        nz = np.sqrt(np.maximum(0.0, 1.0 - r2))

        # Rotated ring coordinates if ringed
        ca, sa = math.cos(-0.26), math.sin(-0.26)
        rx_r = ((xx - cx) * ca - (yy - cy) * sa) / 456.0
        ry_r = ((xx - cx) * sa + (yy - cy) * ca) / 138.0
        rr_e = np.sqrt(rx_r * rx_r + ry_r * ry_r)
        ring_band = np.clip(1.0 - np.abs(rr_e - 0.84) / 0.16, 0.0, 1.0) * (0.68 + 0.32 * np.sin(rr_e * 92.0))

        # Procedural spherical surface texture
        lon = np.arctan2(nx, nz + 1e-4)
        lat = np.arcsin(np.clip(ny, -1.0, 1.0))
        f1 = np.sin(lon * 3.0 + 0.7) * np.cos(lat * 2.6 - 0.3) + 0.55 * np.sin(lon * 7.0 - lat * 5.0)
        if base in ("jupiter", "saturn"):
            pat = 0.5 + 0.5 * np.sin(lat * 14.0 + 0.35 * np.sin(lon * 4.0))
        elif base == "earth":
            pat = np.clip((f1 + 0.18) * 2.8, 0.0, 1.0)
        elif base == "moon":
            cr = np.zeros_like(nx)
            for cx0, cy0, cr0 in [(-0.32, -0.28, 0.22), (0.35, -0.05, 0.17), (-0.08, 0.36, 0.25), (0.22, 0.42, 0.13), (-0.48, 0.18, 0.15)]:
                d2 = (nx - cx0) ** 2 + (ny - cy0) ** 2
                cr += np.where(d2 < cr0 * cr0, -0.45 + 0.85 * (np.sqrt(d2) / cr0) ** 3, 0.0)
            pat = np.clip(0.35 + 0.25 * f1 + cr, 0.0, 1.0)
        else:
            pat = np.clip(0.5 + 0.48 * f1, 0.0, 1.0)

        surf = np.zeros((S, S, 3), dtype=np.float32)
        for c in range(3):
            surf[:, :, c] = col_a[c] * (1.0 - pat) + col_b[c] * pat
        if base == "earth":
            clouds = np.clip(np.sin(lon * 5.0 + lat * 4.0) * np.cos(lon * 9.0 - lat * 6.0) - 0.15, 0.0, 1.0) * 0.85
            for c in range(3):
                surf[:, :, c] = surf[:, :, c] * (1.0 - clouds) + 250.0 * clouds

        # 3D Spherical Terminator lighting + Rayleigh atmospheric rim + volcanic fissures on Mars/Venus
        ndotl = np.clip(nx * (-0.54) + ny * (-0.56) + nz * 0.63, -1.0, 1.0)
        lit = 0.12 + 0.96 * (np.clip((ndotl + 0.16) / 1.16, 0.0, 1.0) ** 0.88)
        spec = np.clip(nx * (-0.28) + ny * (-0.32) + nz * 0.90, 0.0, 1.0) ** 22 * (0.45 if base == "earth" else 0.18)
        fres = ((1.0 - nz) ** 2.6) * np.clip(ndotl + 0.45, 0.15, 1.0) * 0.92

        out = np.zeros((S, S, 4), dtype=np.float32)
        # Outer atmospheric halo outside R
        halo_a = np.where(~inside, np.exp(-((np.sqrt(r2) - 1.0) * 14.0) ** 2) * (r2 < 1.38) * np.clip(ndotl + 0.55, 0.2, 1.0) * 185.0, 0.0)
        for c in range(3):
            out[:, :, c] = atmo_c[c]
        out[:, :, 3] = halo_a

        # Back half of rings (ry_r < 0)
        if has_ring:
            bk = (ry_r < 0) & (ring_band > 0.01) & (~inside)
            for c in range(3):
                out[:, :, c] = np.where(bk, atmo_c[c] * 0.85 + 38.0, out[:, :, c])
            out[:, :, 3] = np.where(bk, np.maximum(out[:, :, 3], ring_band * 215.0), out[:, :, 3])

        # Planet sphere body (with antialiased 2px edge)
        edge_aa = np.clip((1.0 - np.sqrt(r2)) * (R * 0.5), 0.0, 1.0)
        for c in range(3):
            pcol = surf[:, :, c] * lit + 255.0 * spec + atmo_c[c] * fres
            if base in ("mars", "venus"):
                lava = np.clip(np.abs(np.sin(lon * 8.0 + lat * 6.0)) - 0.92, 0.0, 0.08) * 12.5 * (1.0 - np.clip(ndotl, 0.0, 1.0))
                pcol += (255.0 if c == 0 else (165.0 if c == 1 else 40.0)) * lava
            out[:, :, c] = np.where(edge_aa > 0, pcol, out[:, :, c])
        out[:, :, 3] = np.maximum(out[:, :, 3], edge_aa * 255.0)

        # Front half of rings (ry_r >= 0)
        if has_ring:
            fr = (ry_r >= 0) & (ring_band > 0.01)
            ra = ring_band * 0.86
            for c in range(3):
                rc = atmo_c[c] * 0.78 + 56.0
                out[:, :, c] = np.where(fr, out[:, :, c] * (1.0 - ra) + rc * ra, out[:, :, c])
            out[:, :, 3] = np.where(fr, np.maximum(out[:, :, 3], ra * 255.0), out[:, :, 3])

        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), slug, pal, True

    if base in ("galaxy", "selectmap_nebula"):
        yy, xx = np.mgrid[0:S, 0:S]
        rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        ang = np.arctan2(yy - cy, xx - cx)
        spiral = (0.5 + 0.5 * np.cos(ang * (2.0 if base == "galaxy" else 3.0) - rr * 0.016)) ** 1.7
        env = np.clip(1.0 - rr / 468.0, 0.0, 1.0) ** 1.4
        core = np.clip(1.0 - rr / 165.0, 0.0, 1.0) ** 1.8
        a = np.clip(spiral * env + core, 0.0, 1.0)
        arr = np.zeros((S, S, 4), dtype=np.uint8)
        c1 = np.array([0, 224, 255] if base == "galaxy" else [168, 64, 255], dtype=np.float32)
        c2 = np.array([255, 218, 92], dtype=np.float32)
        rgb = c1[None, None, :] * (1.0 - core[:, :, None]) + c2[None, None, :] * core[:, :, None]
        arr[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        arr[:, :, 3] = (a * 245.0).astype(np.uint8)
        slug = "cosmic_spiral_galaxy" if base == "galaxy" else "starmap_nebula_cloud"
        pal = "cyan" if base == "galaxy" else "violet"
        return Image.fromarray(arr, "RGBA"), slug, pal, True

    if base == "cloud":
        for bx, by, br in [(340, 560, 175), (512, 470, 225), (695, 555, 180), (495, 610, 185)]:
            draw_cel_poly(im, reg_poly(bx, by, br, int(br * 0.78), 22), PAL["pearl"], outline_w=10)
        return im, "cumulus_cloud_cluster", "pearl", True

    if base == "asteroid":
        for ax, ay, ar in [(315, 365, 145), (675, 445, 185), (435, 685, 155)]:
            pts = [(ax + math.cos(a) * ar * (0.82 + 0.22 * ((k * 3) % 2)), ay + math.sin(a) * ar * 0.88) for k, a in enumerate(np.linspace(0, 2 * math.pi, 9, endpoint=False))]
            draw_cel_poly(im, pts, PAL["slate"], outline_w=10)
        return im, "asteroid_field_cluster", "slate", True

    if base == "dautau":
        bow = [(cx, 128), (795, 465), (745, 865), (279, 865), (229, 465)]
        draw_cel_poly(im, bow, PAL["azure"], outline_w=12)
        draw_cel_poly(im, [(cx, 195), (665, 485), (635, 815), (389, 815), (359, 485)], PAL["pearl"], outline_w=9)
        draw_cel_poly(im, [(415, 355), (609, 355), (585, 565), (439, 565)], PAL["cyan"], outline_w=8)
        return im, "carrier_bow_platform", "azure", True

    # Remaining 9 starmap star / border nodes (`legendstar*`, `playerstar*`, `pvp_star`, `rate_star`, `stagestar*`)
    pal = "magenta" if "legend" in base else ("cyan" if "player" in base else ("crimson" if "pvp" in base else "solar"))
    is_border = "border" in base
    if is_border:
        outer = star_poly(cx, cy, 418, 212, 5)
        inner = list(reversed(star_poly(cx, cy, 326, 162, 5)))
        draw_cel_poly(im, outer + inner, PAL[pal], outline_w=10)
        if "onmap" in base:
            draw_cel_poly(im, reg_poly(cx, cy, 448, 448, 28) + list(reversed(reg_poly(cx, cy, 412, 412, 28))), PAL["cyan"], outline_w=8)
    else:
        draw_cel_poly(im, star_poly(cx, cy, 412, 196, 5), PAL[pal], outline_w=12)
        draw_cel_poly(im, star_poly(cx, cy, 216, 98, 5), PAL["pearl"], outline_w=7)
    return im, f"starmap_{clean_slug(base)}", pal, True


def render_w5_gui(base):
    S = 512
    pal = "crimson" if "red" in base else ("emerald" if "watch" in base else ("solar" if "avatar" in base else "azure"))
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rad = 24 if "input" in base or "nut" in base else 44
    y_pad = 148 if ("input" in base or "nut" in base) else 20
    draw_9slice_panel(im, (20, y_pad, S - 21, S - 1 - y_pad), rad, PAL[pal], (16, 44, 112, 248), inner_rim=PAL["cyan"][0], outline_w=8)
    return im, f"panel_{clean_slug(base)}", pal


# ---------------------------------------------------------------------------
# 4. UI (+221: U-ICON x58 @64, U-KIT x59 @256, U-META x53 @256, U-SHOP x51 @256)
# ---------------------------------------------------------------------------
def render_w5_ui(batch, px, base):
    S = px * 2  # 128 for 64px icons, 512 for 256px widgets
    cx, cy = S // 2, S // 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    slug = clean_slug(base)

    # Pick vibrant semantic palette
    if any(k in base for k in ("vip", "coin", "gold", "star", "sale", "price", "key", "arena", "ranks", "rankss", "boxs")):
        pal = "solar"
    elif any(k in base for k in ("gem", "exp", "shield", "drone", "time", "select", "vetinh", "radar")):
        pal = "cyan"
    elif any(k in base for k in ("heal", "free", "add", "+button", "up", "video", "watch", "gift")):
        pal = "emerald"
    elif any(k in base for k in ("enemy", "red", "alert", "bom", "crit", "hard", "heart", "noads")):
        pal = "crimson"
    elif any(k in base for k in ("random", "rankx", "boxv", "efect", "craft")):
        pal = "magenta"
    elif "gray" in base:
        pal = "slate"
    else:
        pal = "azure"
    P = PAL[pal]

    # --- A. 64x64 U-ICON (rendered at S=128) ---
    if px == 64:
        ow = 5
        draw_cel_poly(im, reg_poly(cx, cy, 54, 54, 16), PAL["azure"], outline_w=ow)
        if "manh" in base:
            # Puzzle/blueprint shard + tier pips (1..4)
            tier = 4 if "4" in base else (3 if "3" in base else (2 if "2" in base else 1))
            draw_cel_poly(im, [(34, 24), (94, 24), (104, 86), (64, 106), (24, 86)], P, outline_w=4)
            for t in range(tier):
                tx = cx - (tier - 1) * 11 + t * 22
                d.ellipse([tx - 6, 88, tx + 6, 100], fill=PAL["solar"][0], outline=OUTLINE, width=2)
        elif "coin" in base or "sell" in base:
            draw_cel_poly(im, reg_poly(cx, cy, 42, 42, 18), PAL["solar"], outline_w=4)
            draw_centered_label(im, cx, cy, "$" if "sell" in base else "C", 42)
        elif "gem" in base:
            draw_cel_poly(im, [(cx, 18), (102, 52), (84, 106), (44, 106), (26, 52)], PAL["cyan"], outline_w=4)
        elif "key" in base:
            draw_cel_poly(im, reg_poly(46, 52, 24, 24, 14), PAL["solar"], outline_w=4)
            draw_cel_poly(im, [(64, 44), (108, 44), (108, 60), (96, 60), (96, 76), (82, 76), (82, 60), (64, 60)], PAL["solar"], outline_w=4)
        elif "lock" in base or "xich" in base:
            draw_cel_poly(im, [(36, 52), (92, 52), (96, 104), (32, 104)], PAL["solar"], outline_w=4)
            d.arc([42, 22, 86, 68], 180, 360, fill=WHITE, width=7)
        elif "setting" in base:
            draw_cel_poly(im, star_poly(cx, cy, 46, 32, 8), PAL["pearl"], outline_w=4)
            draw_cel_poly(im, reg_poly(cx, cy, 18, 18, 12), PAL["azure"], outline_w=4)
        elif "time" in base or "ring" in base:
            draw_cel_poly(im, reg_poly(cx, cy, 44, 44, 18), PAL["cyan"], outline_w=4)
            draw_cel_poly(im, reg_poly(cx, cy, 28, 28, 16), PAL["pearl"], outline_w=3)
            d.line([(cx, cy), (cx, 38)], fill=OUTLINE, width=5)
            d.line([(cx, cy), (82, cy + 8)], fill=PAL["crimson"][0], width=4)
        elif "enemy" in base:
            draw_cel_poly(im, [(cx, 106), (100, 62), (88, 24), (40, 24), (28, 62)], PAL["crimson"], outline_w=4)
            d.ellipse([44, 48, 58, 62], fill=PAL["solar"][0])
            d.ellipse([70, 48, 84, 62], fill=PAL["solar"][0])
        elif "shield" in base or "giap" in base:
            draw_cel_poly(im, [(cx, 20), (98, 36), (90, 82), (cx, 108), (38, 82), (30, 36)], P, outline_w=4)
        elif "magnet" in base:
            u_pts = [(32, 26), (52, 26), (52, 74), (76, 74), (76, 26), (96, 26), (96, 84), (80, 104), (48, 104), (32, 84)]
            draw_cel_poly(im, u_pts, PAL["crimson"], outline_w=4)
            d.rectangle([32, 24, 52, 42], fill=PAL["pearl"][0], outline=OUTLINE, width=3)
            d.rectangle([76, 24, 96, 42], fill=PAL["pearl"][0], outline=OUTLINE, width=3)
        elif "power" in base or "suc manh" in base:
            bolt = [(72, 18), (34, 68), (62, 68), (52, 110), (94, 56), (66, 56)]
            draw_cel_poly(im, bolt, PAL["solar"], outline_w=4)
        elif "crit" in base:
            draw_cel_poly(im, [(28, 96), (92, 24), (102, 34), (38, 106)], PAL["crimson"], outline_w=4)
            draw_cel_poly(im, [(100, 96), (36, 24), (26, 34), (90, 106)], PAL["solar"], outline_w=4)
        elif "card" in base or "redeem" in base or "quest" in base:
            draw_9slice_panel(im, (26, 30, 102, 98), 12, P, DARK_WELL, outline_w=4)
            d.line([(40, 52), (88, 52)], fill=PAL["solar"][0], width=6)
            d.line([(40, 72), (76, 72)], fill=PAL["cyan"][0], width=5)
        elif "nhanqua" in base:
            draw_9slice_panel(im, (28, 44, 100, 102), 10, PAL["crimson"], PAL["crimson"][0], outline_w=4)
            d.rectangle([56, 36, 72, 102], fill=PAL["solar"][0], outline=OUTLINE, width=3)
            draw_cel_poly(im, [(24, 34), (104, 34), (100, 54), (28, 54)], PAL["solar"], outline_w=4)
        elif "hangar" in base or "mode" in base:
            ship = [(cx, 22), (82, 64), (104, 86), (78, 88), (cx, 104), (50, 88), (24, 86), (46, 64)]
            draw_cel_poly(im, ship, PAL["cyan"], outline_w=4)
        elif "profile" in base:
            draw_cel_poly(im, reg_poly(cx, 44, 18, 18, 14), PAL["pearl"], outline_w=4)
            draw_cel_poly(im, [(32, 102), (42, 70), (86, 70), (96, 102)], PAL["cyan"], outline_w=4)
        elif "add" in base or "use" in base or "support" in base:
            plus = [(52, 26), (76, 26), (76, 52), (102, 52), (102, 76), (76, 76), (76, 102), (52, 102), (52, 76), (26, 76), (26, 52), (52, 52)]
            draw_cel_poly(im, plus, PAL["emerald"], outline_w=4)
        elif "lv" in base or "exp" in base:
            up = [(cx, 20), (100, 64), (80, 64), (80, 104), (48, 104), (48, 64), (28, 64)]
            draw_cel_poly(im, up, PAL["emerald" if "lv" in base else "cyan"], outline_w=4)
        elif "random" in base:
            draw_centered_label(im, cx, cy, "?", 66, fill=PAL["solar"][0], stroke_w=5)
        else:
            draw_cel_poly(im, reg_poly(cx, cy, 38, 38, 6), P, outline_w=4)
            draw_cel_poly(im, star_poly(cx, cy, 26, 12, 4), PAL["pearl"], outline_w=3)
        return im, f"icon_{slug}", pal

    # --- B. 15 Locked Boss Codex Silhouette Badges (AP-0278..0292 boss*gray) ---
    if "boss" in base and "gray" in base:
        bnum = int(re.sub(r"\D+", "", base) or "2")
        draw_9slice_panel(im, (40, 40, S - 41, S - 41), 44, PAL["slate"], (18, 30, 64, 248), inner_rim=PAL["cyan"][0], outline_w=9)
        # Distinct boss codex silhouette inside badge per boss number!
        wings = [(cx - 60, 150), (96, 120 + (bnum % 4) * 28), (118, 330), (cx, 408), (S - 118, 330), (S - 96, 120 + ((bnum + 2) % 4) * 28), (cx + 60, 150)]
        draw_cel_poly(im, wings, ((34, 48, 86, 255), (20, 28, 56, 255), (62, 84, 136, 255)), outline_w=7)
        draw_centered_label(im, cx, 265, f"B{bnum}", 64, fill=PAL["cyan"][2])
        return im, f"kit_codex_{slug}", "slate"

    # --- C. 9-SLICE FRAMES / BOXES / BUTTONS / TABS (`khung*`, `border*`, `panel*`, `tab*`, `nut*`, `btn*`, `box*`) ---
    if base.startswith("khung") or "border" in base or "panel" in base or base in ("bangthongtin", "cell_selected", "cover", "videobox"):
        rad = 64 if ("chinh" in base or "panel" in base or "bang" in base) else 34
        y0 = 136 if ("ten" in base or "time" in base or "so" in base) else 36
        draw_9slice_panel(im, (36, y0, S - 37, S - 1 - y0), rad, P, DARK_WELL, inner_rim=PAL["solar" if pal != "solar" else "cyan"][0], outline_w=9)
        return im, f"{batch[2:].lower()}_{slug}", pal

    if base.startswith("box") or "gift" in base or "newpack" in base:
        # Treasure / Gacha Supply Crates (`boxn`, `boxf`, `boxs`, `boxss`, `boxv`, `boxdrone`, `gift_box`)
        draw_9slice_panel(im, (68, 128, S - 69, S - 56), 28, P, (24, 58, 138, 255), inner_rim=PAL["solar"][0], outline_w=10)
        lid = [(54, 86), (S - 55, 86), (S - 68, 166), (68, 166)]
        draw_cel_poly(im, lid, PAL["solar"], outline_w=9)
        lbl = base.replace("box", "").upper()[:3] or "BOX"
        if "gift" in base:
            lbl = "GIFT"
        elif "pack" in base:
            lbl = "NEW"
        draw_centered_label(im, cx, 295, lbl, 68)
        return im, f"shop_{slug}", pal

    if base.startswith("nut") or "btn" in base or "button" in base or "tab" in base or "buy" in base or base in ("30day", "7day", "fday", "price", "bigsale", "hotsale", "hotsale%", "freebp", "healderbp"):
        draw_9slice_panel(im, (28, 136, S - 29, S - 137), 28, P, P[0], inner_rim=WHITE, outline_w=10)
        d.rounded_rectangle([52, 156, S - 53, cy - 6], radius=14, fill=(255, 255, 255, 88))
        tag = {
            "+button": "+", "closebutton": "X", "upgradebutton": "UP", "30day": "30D", "7day": "7D",
            "fday": "1D", "bigsale": "SALE", "hotsale": "HOT", "hotsale%": "%", "freebp": "FREE",
            "buybp": "PASS", "price": "GOLD", "nutads": "ADS", "nutbuyskin": "SKIN", "nutchedo": "MODE",
            "nutrs": "RST", "nuttech": "TECH", "nutuplv": "LV+", "nutwatchads": "VID", "nennutevent": "EVENT",
            "btn_arena": "PVP", "btn_video": "VID", "btn_startplay": "PLAY", "buttoncraft": "CRAFT",
            "buttontab": "TAB", "tabngay": "DAY", "tabbp": "BP", "healderbp": "BATTLE",
            "backbutton": "<",
        }.get(base, "")
        if tag:
            draw_centered_label(im, cx, cy, tag, 72)
        return im, f"{batch[2:].lower()}_{slug}", pal

    if base.startswith("line") or base == "fillred":
        draw_9slice_panel(im, (24, 212, S - 25, 299), 20, P, P[0], inner_rim=WHITE, outline_w=8)
        return im, f"{batch[2:].lower()}_{slug}", pal

    if base in ("backmap", "backtotop", "backup", "change", "tron xoay"):
        draw_cel_poly(im, reg_poly(cx, cy, 184, 184, 24), PAL["azure"], outline_w=10)
        arr_pts = [(136, cy), (268, 132), (268, 208), (384, 208), (384, 304), (268, 304), (268, 380)]
        if base in ("backtotop", "backup"):
            arr_pts = [(cx, 124), (384, 260), (308, 260), (308, 384), (204, 384), (204, 260), (128, 260)]
        draw_cel_poly(im, arr_pts, PAL["solar" if "change" in base or "xoay" in base else "cyan"], outline_w=9)
        return im, f"{batch[2:].lower()}_{slug}", pal

    if base == "bom":
        draw_cel_poly(im, reg_poly(cx, 286, 152, 152, 24), PAL["slate"], outline_w=10)
        d.line([(cx, 134), (346, 78)], fill=PAL["solar"][0], width=14)
        draw_cel_poly(im, star_poly(356, 74, 48, 20, 6), PAL["crimson"], outline_w=6)
        return im, f"{batch[2:].lower()}_{slug}", "crimson"

    if base == "bong den":
        draw_cel_poly(im, reg_poly(cx, 216, 132, 132, 24), PAL["solar"], outline_w=10)
        draw_9slice_panel(im, (196, 324, 316, 416), 18, PAL["slate"], PAL["pearl"][0], outline_w=8)
        return im, f"{batch[2:].lower()}_{slug}", "solar"

    if base == "enegry":
        draw_cel_poly(im, reg_poly(cx, cy, 188, 188, 8, rot=math.pi / 8), PAL["azure"], outline_w=10)
        bolt = [(292, 86), (156, 268), (252, 268), (216, 426), (356, 236), (260, 236)]
        draw_cel_poly(im, bolt, PAL["solar"], outline_w=9)
        return im, f"{batch[2:].lower()}_{slug}", "solar"

    if base in ("vetinh", "dronel"):
        draw_9slice_panel(im, (52, 204, 176, 308), 16, PAL["cyan"], PAL["azure"][0], outline_w=8)
        draw_9slice_panel(im, (336, 204, 460, 308), 16, PAL["cyan"], PAL["azure"][0], outline_w=8)
        draw_cel_poly(im, reg_poly(cx, cy, 88, 112, 8), PAL["pearl"], outline_w=9)
        draw_cel_poly(im, reg_poly(cx, cy, 42, 42, 16), PAL["solar"], outline_w=7)
        return im, f"{batch[2:].lower()}_{slug}", "cyan"

    if base in ("about", "notice", "rename", "add", "avatarp", "community"):
        draw_cel_poly(im, reg_poly(cx, cy, 186, 186, 24), P, outline_w=10)
        lbl = {"about": "i", "notice": "!", "rename": "ED", "add": "+", "avatarp": "ID", "community": "HUB"}[base]
        draw_centered_label(im, cx, cy, lbl, 112)
        return im, f"{batch[2:].lower()}_{slug}", pal

    # --- D. RANK / MEDAL / VIP / MODE CRESTS & SPECIAL EMBLEMS ---
    if any(k in base for k in ("rank", "medal", "vip", "pvp", "combat_unlock", "endless", "hoisinh", "heart", "noads", "alert", "checkbox")):
        if base == "heart":
            h_pts = [(cx, 418), (428, 256), (412, 138), (326, 98), (cx, 168), (186, 98), (100, 138), (84, 256)]
            draw_cel_poly(im, h_pts, PAL["crimson"], outline_w=10)
        elif base == "checkbox":
            draw_9slice_panel(im, (96, 96, S - 97, S - 97), 24, PAL["azure"], DARK_WELL, outline_w=9)
            chk = [(148, 262), (226, 342), (376, 168), (342, 136), (224, 274), (180, 228)]
            draw_cel_poly(im, chk, PAL["emerald"], outline_w=7)
        elif base == "noads":
            draw_cel_poly(im, reg_poly(cx, cy, 196, 196, 24), PAL["crimson"], outline_w=10)
            draw_centered_label(im, cx, cy, "AD", 110)
            d.line([(128, 384), (384, 128)], fill=WHITE, width=22)
        else:
            wings_r = [(cx + 76, 215), (464, 136), (432, 298), (cx + 92, 336)]
            wings_l = [(2 * cx - x, y) for (x, y) in reversed(wings_r)]
            draw_cel_poly(im, wings_l, PAL["solar"], outline_w=9)
            draw_cel_poly(im, wings_r, PAL["solar"], outline_w=9)
            sh = [(cx, 88), (380, 166), (348, 348), (cx, 436), (164, 348), (132, 166)]
            draw_cel_poly(im, sh, P, outline_w=10)
            lbl = {"ranka": "A", "ranks": "S", "rankss": "SS", "rankx": "X", "vip0.": "V0", "vip": "VIP", "endless": "INF"}.get(base, "")
            if lbl:
                draw_centered_label(im, cx, 256, lbl, 96)
            else:
                draw_cel_poly(im, star_poly(cx, 255, 84, 38, 5), PAL["pearl"], outline_w=7)
        return im, f"{batch[2:].lower()}_{slug}", pal

    # Default crisp octagonal/star arcade badge for remaining kit/meta/shop utility tokens
    draw_cel_poly(im, reg_poly(cx, cy, 186, 186, 8, rot=math.pi / 8), PAL["azure"], outline_w=10)
    draw_cel_poly(im, reg_poly(cx, cy, 132, 132, 8, rot=math.pi / 8), P, outline_w=8)
    draw_cel_poly(im, star_poly(cx, cy, 74, 34, 5), PAL["pearl"], outline_w=6)
    return im, f"{batch[2:].lower()}_{slug}", pal


def measure_rgba(im):
    arr = np.asarray(im, dtype=np.float32)
    fg = arr[:, :, 3] > 16
    if not np.any(fg):
        return 0.0, 0.0, 0.0
    rgb = arr[fg][:, :3] / 255.0
    mx, mn = rgb.max(axis=1), rgb.min(axis=1)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0.0)
    return round(float(mx.mean()), 3), round(float(sat.mean()), 3), round(float(fg.mean()), 3)


def build_packaging_icons():
    """Export ICO-06 (windwings.ico) & ICO-07 (Android mipmap-* ic_launcher.png) in art/w0-build-icons-b/
    from our W0 Solar-Neon icon master without altering art/w0-listing-b/!"""
    src_master = os.path.join(ROOT, "art/w0-listing-b/masters/icon_master.png")
    out_dir = os.path.join(ROOT, "art/w0-build-icons-b")
    os.makedirs(os.path.join(out_dir, "masters"), exist_ok=True)
    im = Image.open(src_master).convert("RGBA")
    im1024 = im.resize((1024, 1024), Image.LANCZOS)
    im1024.save(os.path.join(out_dir, "masters/icon_master_1024.png"), "PNG", compress_level=9)

    # ICO-06: multi-res Windows .ico (16, 24, 32, 48, 256)
    im1024.save(os.path.join(out_dir, "windwings.ico"), format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (256, 256)])

    # ICO-07: Android mipmap launcher set (48, 72, 96, 144, 192)
    mipmaps = [("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)]
    for bucket, sz in mipmaps:
        mdir = os.path.join(out_dir, f"mipmap-{bucket}")
        os.makedirs(mdir, exist_ok=True)
        im1024.resize((sz, sz), Image.LANCZOS).save(os.path.join(mdir, "ic_launcher.png"), "PNG", compress_level=9)


def main():
    spec = json.load(open(os.path.join(HERE, "w5b_plan_spec.json"), encoding="utf-8"))
    records = []

    for idx, row in enumerate(spec, 1):
        rid = row["row_id"]
        lane = row["lane"]
        bat = row["batch"]
        base = row["base_name"]
        px = row["target_px"]

        if lane == "ITEM":
            c, slug, pal = render_w5_item(base)
            m_im = downsample_straight_rgba(c, (256, 256))
            s_im = downsample_straight_rgba(c, (128, 128))
            sub, fname, zc = "items", f"item_{rid.lower().replace('-','_')}_{slug}_128@{pal}.png", True
        elif lane == "FX":
            c, slug, pal = render_w5_fx(base)
            m_im = downsample_straight_rgba(c, (px * 2, px * 2))
            s_im = downsample_straight_rgba(c, (px, px))
            sub, fname, zc = "fx", f"fx_{rid.lower().replace('-','_')}_{slug}_{px}@{pal}.png", True
        elif lane == "BG" and bat == "G-PARALLAX":
            c, slug, pal, zc = render_w5_parallax(base)
            s_im = downsample_straight_rgba(c, (1024, 1024), zero_corners=zc)
            m_im = s_im
            sub, fname = "bg/parallax", f"bg_{rid.lower().replace('-','_')}_{slug}_1024@{pal}.png"
        elif lane == "BG":
            s_im, slug, pal = render_w5_gui(base)
            s_im = downsample_straight_rgba(s_im, (512, 512))
            m_im = s_im
            sub, fname, zc = "bg/gui", f"bg_{rid.lower().replace('-','_')}_{slug}_512@{pal}.png", True
        else:  # UI (221 units)
            c, slug, pal = render_w5_ui(bat, px, base)
            m_sz = (128, 128) if px == 64 else (256, 256)
            m_im = downsample_straight_rgba(c, m_sz)
            s_im = downsample_straight_rgba(c, (px, px))
            sub, fname, zc = f"ui/{bat.lower()}", f"ui_{rid.lower().replace('-','_')}_{slug}_{px}@{pal}.png", True

        os.makedirs(os.path.join(HERE, f"masters/{sub}"), exist_ok=True)
        os.makedirs(os.path.join(HERE, f"sprites/{sub}"), exist_ok=True)
        m_rel = f"masters/{sub}/{fname}"
        s_rel = f"sprites/{sub}/{fname}"
        m_im.save(os.path.join(HERE, m_rel), "PNG", compress_level=9)
        s_im.save(os.path.join(HERE, s_rel), "PNG", compress_level=9)
        if zc:
            sa = np.asarray(s_im)
            assert sa[0, 0, 3] == 0 and sa[0, -1, 3] == 0 and sa[-1, 0, 3] == 0 and sa[-1, -1, 3] == 0, fname
        val, ch, fill = measure_rgba(s_im)
        records.append({
            "row_id": rid, "lane": lane, "batch": bat, "unit_no": idx,
            "planner_base": base, "variant": slug,
            "delivered_px": f"{s_im.width}x{s_im.height}", "master_px": f"{m_im.width}x{m_im.height}",
            "source": m_rel, "file": s_rel, "license": LICENSE_NOTE,
            "author": AUTHOR_BRANCH, "recipe": f"b_{lane.lower()}_{pal}",
            "val": val, "chroma": ch, "fill": fill,
        })

    with open(os.path.join(HERE, "w5b_units.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "w5b_units.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    build_packaging_icons()
    print(f"SUCCESS: {len(records)} W5-full units + build packaging icons exported!")


if __name__ == "__main__":
    main()
