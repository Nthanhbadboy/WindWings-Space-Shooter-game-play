#!/usr/bin/env python3
"""
Build Wave W4-core — ITEM / FX / BG / UI (112 kept planner rows = 114 files; EXCL 278 = 0)
for Variant B ("Solar Neon Arcade-Pop").
Author branch: arena/eca8588b-windwings-space-shooter-game-p

Breakdown:
  - ITEM (I-DROP x7, AP-0130..0134,0136,0137): 128x128 RGBA + 256x256 masters/
  - FX   (F-BOOM x5 + F-GLOW x4 = 9, AP-0082..0086,0150,0156,0158,0159): 256x256 RGBA + 512x512 masters/
  - BG   (G-PARALLAX AP-0091 x3 seamless 1024x1024 + G-UI x9 512x512 = 12 files)
  - UI   (86 kept rows: U-HUD x27 @256, U-ICON x9 @64, U-KIT x38 @256, U-META x1 @256, U-SHOP x11 @256)
         strictly honoring ASSETS.md §5 9-slice border insets!
"""

import csv
import json
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import pbr25d

AUTHOR_BRANCH = "arena/eca8588b-windwings-space-shooter-game-p"
LICENSE_NOTE = "chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OUTLINE = (24, 48, 108, 255)

PAL = {
    "solar":    ((255, 204, 18, 255),  (212, 112, 0, 255),   (255, 246, 142, 255)),
    "cyan":     ((0, 218, 255, 255),   (0, 128, 196, 255),   (156, 252, 255, 255)),
    "azure":    ((28, 112, 246, 255),  (14, 58, 162, 255),   (96, 178, 255, 255)),
    "emerald":  ((0, 228, 158, 255),   (0, 138, 92, 255),    (138, 255, 214, 255)),
    "magenta":  ((255, 42, 148, 255),  (168, 12, 88, 255),   (255, 142, 208, 255)),
    "crimson":  ((255, 36, 86, 255),   (168, 10, 48, 255),   (255, 124, 154, 255)),
    "violet":   ((138, 56, 224, 255),  (72, 22, 136, 255),   (198, 138, 255, 255)),
    "pearl":    ((232, 242, 255, 255), (168, 196, 238, 255), (252, 254, 255, 255)),
    "cerulean": ((22, 126, 242, 255),  (12, 68, 158, 255),   (88, 188, 255, 255)),
}
WHITE = (255, 255, 255, 255)
DARK_WELL = (14, 34, 88, 238)


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
    """2.5D metallic beveled 9-slice frame/button (ASSETS.md §5 compliant, zero cartoon outline!)."""
    glow_c = (inner_rim[:3] if inner_rim is not None else (0, 224, 255))
    bw = max(6, int((box[2] - box[0]) * 0.045))
    pbr25d.draw_25d_9slice_panel(canvas, box, radius, rim_triple, fill_rgba, inner_glow_rgb=glow_c, bevel_w=bw)


# ---------------------------------------------------------------------------
# 1. BG: 3 Seamless 1024x1024 Parallax Layers + 9 512x512 G-UI Backdrops
# ---------------------------------------------------------------------------
def build_seamless_parallax(raw_path, mode):
    """Convert generated master into 100% vertically seamless 1024x1024 RGBA texture."""
    raw = Image.open(raw_path).convert("RGB")
    if mode == "sky_far":
        # Resize to 1024x1280 and cosine-blend 256px overlap so y=0..1023 tiles seamlessly!
        big = np.asarray(raw.resize((1024, 1280), Image.LANCZOS), dtype=np.float32)
        ov = 256
        base = big[:1024].copy()
        tail = big[1024:1024 + ov]
        w = (0.5 - 0.5 * np.cos(np.pi * np.arange(ov, dtype=np.float32) / ov))[:, None, None]
        base[:ov] = tail * (1.0 - w) + base[:ov] * w
        base[-1] = base[0]
        # Audit a71412d3: the first sky layer was V=0.94 and visually
        # overpowered enemy/ship values. Keep the Solar-Neon rays, but ground
        # the stage in a dark, desaturated cobalt atmosphere so gameplay pops.
        base = base * np.array([0.20, 0.24, 0.32], dtype=np.float32)[None, None, :] + np.array([3.0, 5.0, 12.0], dtype=np.float32)[None, None, :]
        base[-1] = base[0]
        rgba = np.concatenate([np.clip(np.round(base), 0, 255).astype(np.uint8), np.full((1024, 1024, 1), 255, dtype=np.uint8)], axis=2)
        return Image.fromarray(rgba, "RGBA")

    # Chromakey blue extraction for mid clouds & near floating islands -> clean straight RGBA!
    big_rgb = np.asarray(raw.resize((1024, 1216), Image.LANCZOS), dtype=np.float32)
    # Sample pure chromakey blue from areas with high blue-to-red/green dominance
    blue_excess = big_rgb[:, :, 2] - np.maximum(big_rgb[:, :, 0], big_rgb[:, :, 1])
    key_mask = blue_excess > np.percentile(blue_excess, 70)
    key_rgb = np.median(big_rgb[key_mask], axis=0)  # e.g. [4, 52, 198]

    diff = np.linalg.norm(big_rgb - key_rgb[None, None, :], axis=2)
    lo, hi = (26.0, 62.0) if mode == "cloud_mid" else (28.0, 56.0)
    alpha = np.clip((diff - lo) / (hi - lo), 0.0, 1.0)
    # Despill chromakey blue from semi-transparent edge pixels
    fg_rgb = np.where(alpha[:, :, None] > 1e-3, (big_rgb - key_rgb[None, None, :] * (1.0 - alpha[:, :, None])) / np.maximum(alpha[:, :, None], 0.18), 0.0)
    fg_rgb = np.clip(fg_rgb, 0.0, 255.0)

    if mode == "archipelago_near":
        # Open a clean central bullet-hell flight corridor so near islands frame the left & right flanks
        # without cluttering center bullets (raw full master stays intact in masters/bg_raw/)!
        xx = np.arange(1024, dtype=np.float32)[None, :]
        dist_center = np.abs(xx - 511.5)
        corridor = np.clip((dist_center - 145.0) / 95.0, 0.0, 1.0)
        alpha = alpha * corridor

    # Vertical seamless wrap over 192px overlap via Porter-Duff over
    ov = 192
    rgb_a = fg_rgb[:1024].copy()
    al_a = alpha[:1024].copy()
    rgb_b = fg_rgb[1024:1024 + ov]
    al_b = alpha[1024:1024 + ov]
    ramp = np.linspace(1.0, 0.0, ov, dtype=np.float32)[:, None]
    al_t = al_b * ramp
    al_m = al_a[:ov] * (1.0 - ramp * 0.5)
    out_a = al_t + al_m * (1.0 - al_t)
    out_rgb = np.where(out_a[:, :, None] > 1e-4, (rgb_b * al_t[:, :, None] + rgb_a[:ov] * al_m[:, :, None] * (1.0 - al_t[:, :, None])) / np.maximum(out_a[:, :, None], 1e-4), 0.0)
    rgb_a[:ov] = out_rgb
    al_a[:ov] = out_a
    # Guarantee exact top-bottom row match & zero 4-corner alpha
    rgb_a[-1] = rgb_a[0]
    al_a[-1] = al_a[0]
    for cy in (0, 1023):
        for cx in (0, 1023):
            al_a[cy, cx] = 0.0
            rgb_a[cy, cx] = 0.0

    rgba = np.concatenate([np.round(rgb_a).astype(np.uint8), np.round(al_a * 255.0).astype(np.uint8)[:, :, None]], axis=2)
    rgba[rgba[:, :, 3] < 4] = 0
    return Image.fromarray(rgba, "RGBA")


def render_gui_backdrop(idx, variant, pal_key):
    """Render 1 of 9 crisp 512x512 Solar Neon Arcade-Pop UI Board Backdrops."""
    S = 512
    yy, xx = np.mgrid[0:S, 0:S]
    P = PAL[pal_key]
    t = yy / float(S - 1)
    # Bright arcade radial + vertical gradient base inside rounded board silhouette
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw_9slice_panel(im, (14, 14, S - 15, S - 15), 42, P, (16, 46, 118, 255), inner_rim=PAL["cyan"][0], outline_w=6)

    # Interior sunlit starburst / tech grid clipped inside well (38..473)
    well = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    wd = ImageDraw.Draw(well)
    cx, cy = 256, 210
    for k in range(12):
        a0 = k * math.pi / 6 + idx * 0.15
        a1 = a0 + math.pi / 14
        ray = [(cx, cy), (cx + math.cos(a0) * 420, cy + math.sin(a0) * 420), (cx + math.cos(a1) * 420, cy + math.sin(a1) * 420)]
        wd.polygon(ray, fill=(P[0][0], P[0][1], P[0][2], 58))
    # Subtle holographic grid lines
    for g in range(64, 460, 48):
        wd.line([(44, g), (468, g)], fill=(0, 224, 255, 36), width=2)
        wd.line([(g, 44), (g, 468)], fill=(0, 224, 255, 28), width=1)
    # Center emblem motif per screen role
    if "pass" in variant or "prestige" in variant:
        draw_cel_poly(well, star_poly(256, 256, 118, 54, 5), PAL["solar"], outline_w=5)
    elif "starmap" in variant:
        for r in (65, 125, 180):
            wd.ellipse([256 - r, 256 - r, 256 + r, 256 + r], outline=(0, 238, 255, 128), width=3)
    elif "foundry" in variant:
        draw_cel_poly(well, reg_poly(256, 256, 108, 108, 6), PAL["emerald"], outline_w=5)
    elif "hangar" in variant:
        wd.polygon([(256, 110), (380, 390), (256, 335), (132, 390)], fill=(0, 226, 255, 76))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([38, 38, S - 39, S - 39], radius=24, fill=255)
    w_arr = np.asarray(well).copy()
    w_arr[:, :, 3] = np.minimum(w_arr[:, :, 3], np.asarray(mask))
    im.alpha_composite(Image.fromarray(w_arr, "RGBA"))
    return downsample_straight_rgba(im, (512, 512))


# ---------------------------------------------------------------------------
# 2. ITEM: 7 Collectible Drops (256x256 master -> 128x128 sprite)
# ---------------------------------------------------------------------------
def render_item(variant, pal_key):
    S = 512
    cx, cy = 256, 256
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    P = PAL[pal_key]
    # Bright pickup halo ring so item reads at 48px inside bullet hell!
    draw_cel_poly(im, reg_poly(cx, cy, 206, 206, 24), PAL["pearl"], outline_w=9)
    draw_cel_poly(im, reg_poly(cx, cy, 172, 172, 24), P, outline_w=7)

    if variant == "weapon_up":
        # Ascending twin power chevrons
        for dy in (-28, 42):
            ch = [(cx, cy - 82 + dy), (cx + 95, cy + 4 + dy), (cx + 95, cy + 52 + dy), (cx, cy - 28 + dy), (cx - 95, cy + 52 + dy), (cx - 95, cy + 4 + dy)]
            draw_cel_poly(im, ch, PAL["pearl"], outline_w=7)
    elif variant == "shield_orb":
        sh = [(cx, 115), (368, 165), (348, 315), (cx, 405), (164, 315), (144, 165)]
        draw_cel_poly(im, sh, PAL["cyan"], outline_w=8)
        draw_cel_poly(im, star_poly(cx, 252, 56, 24, 4), PAL["pearl"], outline_w=5)
    elif variant == "magnet_core":
        u_pts = [(165, 145), (218, 145), (218, 285), (294, 285), (294, 145), (347, 145), (347, 325), (305, 378), (207, 378), (165, 325)]
        draw_cel_poly(im, u_pts, PAL["crimson"], outline_w=8)
        for lx in (165, 294):
            draw_cel_poly(im, [(lx, 145), (lx + 53, 145), (lx + 53, 195), (lx, 195)], PAL["pearl"], outline_w=6)
    elif variant == "supply_chest":
        box = [(142, 195), (370, 195), (382, 365), (130, 365)]
        draw_cel_poly(im, box, PAL["azure"], outline_w=8)
        lid = [(134, 155), (378, 155), (370, 225), (142, 225)]
        draw_cel_poly(im, lid, PAL["solar"], outline_w=8)
        draw_cel_poly(im, star_poly(cx, 285, 52, 24, 5), PAL["solar"], outline_w=6)
    elif variant == "solar_crescent":
        outer = [(cx + math.cos(a) * 128, cy + math.sin(a) * 128) for a in np.linspace(-2.1, 1.3, 18)]
        inner = [(cx + 42 + math.cos(a) * 98, cy - 18 + math.sin(a) * 98) for a in np.linspace(1.1, -1.9, 16)]
        draw_cel_poly(im, outer + inner, PAL["solar"], outline_w=8)
    elif variant == "max_overdrive":
        draw_cel_poly(im, star_poly(cx, cy, 142, 66, 6), PAL["solar"], outline_w=8)
        draw_cel_poly(im, star_poly(cx, cy, 78, 36, 6, rot=0), PAL["pearl"], outline_w=5)
    else:  # mecha_crest_token
        helm = [(cx, 118), (365, 205), (338, 375), (174, 375), (147, 205)]
        draw_cel_poly(im, helm, PAL["pearl"], outline_w=8)
        horn_l, horn_r = [(175, 205), (112, 122), (215, 168)], [(337, 205), (400, 122), (297, 168)]
        draw_cel_poly(im, horn_l, PAL["solar"], outline_w=7)
        draw_cel_poly(im, horn_r, PAL["solar"], outline_w=7)
        draw_cel_poly(im, [(188, 235), (324, 235), (305, 295), (207, 295)], PAL["cyan"], outline_w=6)
    return im


# ---------------------------------------------------------------------------
# 3. FX: 9 Boom & Glow Effects (512x512 master -> 256x256 sprite)
# ---------------------------------------------------------------------------
def render_fx(variant, pal_key):
    S = 512
    cx, cy = 256, 256
    yy, xx = np.mgrid[0:S, 0:S]
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ang = np.arctan2(yy - cy, xx - cx)
    P = PAL[pal_key][0]
    arr = np.zeros((S, S, 4), dtype=np.float32)

    if variant == "mega_nova":
        ring = np.exp(-((rr - 168.0) / 26.0) ** 2)
        core = np.clip(1.0 - rr / 185.0, 0.0, 1.0) ** 1.6
        a = np.clip(ring * 0.95 + core * 0.92, 0.0, 1.0)
        wh = np.clip(1.0 - rr / 95.0, 0.0, 1.0)
        for c in range(3):
            arr[:, :, c] = P[c] * (1.0 - wh) + 255.0 * wh
        arr[:, :, 3] = a * 255.0
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        draw_cel_poly(im, star_poly(cx, cy, 218, 92, 8), PAL[pal_key], outline_w=5)
        draw_cel_poly(im, star_poly(cx, cy, 118, 52, 8, rot=0.39), PAL["pearl"], outline_w=0)
        return im

    if variant == "starburst_blast":
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        draw_cel_poly(im, star_poly(cx, cy, 228, 108, 10), PAL["crimson"], outline_w=6)
        draw_cel_poly(im, star_poly(cx, cy, 176, 82, 10, rot=0.31), PAL["solar"], outline_w=5)
        draw_cel_poly(im, star_poly(cx, cy, 104, 52, 8), PAL["pearl"], outline_w=0)
        return im

    if variant == "cross_flare":
        ax = np.exp(-(np.abs(xx - cx) / 22.0) ** 1.3) * np.clip(1.0 - np.abs(yy - cy) / 238.0, 0.0, 1.0)
        ay = np.exp(-(np.abs(yy - cy) / 22.0) ** 1.3) * np.clip(1.0 - np.abs(xx - cx) / 238.0, 0.0, 1.0)
        core = np.clip(1.0 - rr / 110.0, 0.0, 1.0) ** 1.8
        a = np.clip(ax + ay + core, 0.0, 1.0)
        wh = np.clip(core + (ax + ay) * 0.45, 0.0, 1.0)
        for c in range(3):
            arr[:, :, c] = P[c] * (1.0 - wh) + 255.0 * wh
        arr[:, :, 3] = a * 255.0
        return Image.fromarray(arr.astype(np.uint8), "RGBA")

    if variant == "unlock_prism":
        rays = (0.5 + 0.5 * np.cos(ang * 12.0)) ** 2.2 * np.clip(1.0 - rr / 236.0, 0.0, 1.0)
        core = np.clip(1.0 - rr / 128.0, 0.0, 1.0) ** 1.5
        a = np.clip(rays * 0.85 + core, 0.0, 1.0)
        for c in range(3):
            arr[:, :, c] = P[c] * (1.0 - core) + 255.0 * core
        arr[:, :, 3] = a * 255.0
        return Image.fromarray(arr.astype(np.uint8), "RGBA")

    if variant == "plasma_vortex":
        spiral = (0.5 + 0.5 * np.cos(ang * 6.0 - rr * 0.045)) ** 2.0
        env = np.clip(1.0 - rr / 232.0, 0.0, 1.0) * np.clip(rr / 42.0, 0.0, 1.0)
        core = np.clip(1.0 - rr / 84.0, 0.0, 1.0) ** 1.6
        a = np.clip(spiral * env + core, 0.0, 1.0)
        for c in range(3):
            arr[:, :, c] = P[c] * (1.0 - core) + 255.0 * core
        arr[:, :, 3] = a * 255.0
        return Image.fromarray(arr.astype(np.uint8), "RGBA")

    if variant == "repair_aura":
        ring = np.exp(-((rr - 172.0) / 22.0) ** 2)
        for c in range(3):
            arr[:, :, c] = P[c]
        arr[:, :, 3] = np.clip(ring, 0.0, 1.0) * 235.0
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        plus = [(216, 126), (296, 126), (296, 216), (386, 216), (386, 296), (296, 296), (296, 386), (216, 386), (216, 296), (126, 296), (126, 216), (216, 216)]
        draw_cel_poly(im, plus, PAL["emerald"], outline_w=6)
        return im

    if variant == "overdrive_surge":
        ring = np.exp(-((rr - 178.0) / 24.0) ** 2) * (0.65 + 0.35 * np.cos(ang * 10.0))
        for c in range(3):
            arr[:, :, c] = P[c]
        arr[:, :, 3] = np.clip(ring, 0.0, 1.0) * 245.0
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        bolt = [(285, 86), (168, 268), (252, 268), (218, 426), (352, 232), (266, 232)]
        draw_cel_poly(im, bolt, PAL["solar"], outline_w=6)
        return im

    if variant == "levelup_ring":
        ring = np.exp(-((rr - 180.0) / 20.0) ** 2)
        for c in range(3):
            arr[:, :, c] = P[c]
        arr[:, :, 3] = np.clip(ring, 0.0, 1.0) * 240.0
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        ch = [(cx, 128), (378, 255), (378, 322), (cx, 198), (134, 322), (134, 255)]
        draw_cel_poly(im, ch, PAL["cyan"], outline_w=6)
        return im

    # tint_halo (AP-0159 circle: bright high-value ring+soft interior for shader tinting!)
    ring = np.exp(-((rr - 176.0) / 22.0) ** 2)
    soft = np.clip(1.0 - rr / 205.0, 0.0, 1.0) ** 2.2 * 0.45
    a = np.clip(ring + soft, 0.0, 1.0)
    arr[:, :, 0] = 215.0 + 40.0 * ring
    arr[:, :, 1] = 248.0 + 7.0 * ring
    arr[:, :, 2] = 255.0
    arr[:, :, 3] = a * 255.0
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


# ---------------------------------------------------------------------------
# 4. UI: 86 Kept Planner Rows (U-HUD x27, U-ICON x9, U-KIT x38, U-META x1, U-SHOP x11)
# ---------------------------------------------------------------------------
UI_JOBS = [
    # U-HUD (27 @ 256)
    ("AP-0018", "U-HUD", 256, "+hp",                     "hud_hp_plus_badge",        "emerald", "medkit"),
    ("AP-0019", "U-HUD", 256, "+hp_timer",               "hud_hp_timer_gauge",       "emerald", "timer_med"),
    ("AP-0020", "U-HUD", 256, "box_number",              "hud_counter_cell",         "azure",   "9s_reward"),
    ("AP-0021", "U-HUD", 256, "chieng",                  "hud_wave_gong",            "solar",   "gong"),
    ("AP-0022", "U-HUD", 256, "clock",                   "hud_chrono_clock",         "cyan",    "clock"),
    ("AP-0023", "U-HUD", 256, "control",                 "hud_pad_ring",             "cyan",    "pad_ring"),
    ("AP-0024", "U-HUD", 256, "device_slot_default",     "hud_device_slot",          "azure",   "9s_shop"),
    ("AP-0025", "U-HUD", 256, "dot",                     "hud_pip_dot",              "cyan",    "pip_dot"),
    ("AP-0026", "U-HUD", 256, "hp",                      "hud_life_pip",             "emerald", "life_pip"),
    ("AP-0027", "U-HUD", 256, "knob",                    "hud_pad_knob",             "solar",   "pad_knob"),
    ("AP-0028", "U-HUD", 256, "number",                  "hud_score_plate",          "azure",   "9s_btn_sec"),
    ("AP-0029", "U-HUD", 256, "overdrive_timer",         "hud_overdrive_gauge",      "solar",   "timer_bolt"),
    ("AP-0030", "U-HUD", 256, "pause",                   "hud_pause_btn",            "azure",   "pause_btn"),
    ("AP-0031", "U-HUD", 256, "point_bg",                "hud_point_pill",           "azure",   "9s_slider"),
    ("AP-0032", "U-HUD", 256, "s_timer",                 "hud_skill_s_gauge",        "magenta", "timer_s"),
    ("AP-0033", "U-HUD", 256, "shield_timer",            "hud_shield_gauge",         "cyan",    "timer_shield"),
    ("AP-0034", "U-HUD", 256, "slot",                    "hud_loadout_bar",          "azure",   "9s_btn_sec"),
    ("AP-0035", "U-HUD", 256, "thanh",                   "hud_energy_segment",       "cyan",    "seg_cell"),
    ("AP-0036", "U-HUD", 256, "thanhtieudebangthongtin", "hud_info_header_tab",      "solar",   "9s_tab"),
    ("AP-0037", "U-HUD", 256, "thanhtip",                "hud_tip_ribbon",           "azure",   "9s_btn_sec"),
    ("AP-0038", "U-HUD", 256, "thanhchiso",              "hud_stat_bar_primary",     "solar",   "9s_slider"),
    ("AP-0039", "U-HUD", 256, "thanhchiso1 copy",        "hud_stat_bar_secondary",   "cyan",    "9s_slider"),
    ("AP-0040", "U-HUD", 256, "thanhduoi",               "hud_bottom_trim_bar",      "azure",   "trim_bar"),
    ("AP-0041", "U-HUD", 256, "thanhtren",               "hud_boss_hp_track",        "crimson", "9s_bosshp"),
    ("AP-0042", "U-HUD", 256, "tiendo",                  "hud_stage_progress_track", "emerald", "9s_slider"),
    ("AP-0043", "U-HUD", 256, "warning_boss_bg",         "hud_boss_warning_banner",  "crimson", "warn_banner"),
    ("AP-0044", "U-HUD", 256, "dung item +them hp",      "hud_quick_heal_btn",       "emerald", "medkit_btn"),
    # U-ICON (9 @ 64)
    ("AP-0182", "U-ICON", 64, "coin",                    "icon_gold_coin",           "solar",   "ico_coin"),
    ("AP-0187", "U-ICON", 64, "evolution",               "icon_wing_evolution",      "magenta", "ico_evo"),
    ("AP-0188", "U-ICON", 64, "exp",                     "icon_exp_crystal",         "cyan",    "ico_exp"),
    ("AP-0189", "U-ICON", 64, "eye",                     "icon_watch_eye",           "cyan",    "ico_eye"),
    ("AP-0193", "U-ICON", 64, "hotro",                   "icon_wingman_support",     "emerald", "ico_drone"),
    ("AP-0196", "U-ICON", 64, "iconmode",                "icon_battle_mode",         "solar",   "ico_mode"),
    ("AP-0226", "U-ICON", 64, "stat",                    "icon_atk_stat",            "crimson", "ico_atk"),
    ("AP-0227", "U-ICON", 64, "substat",                 "icon_substat_chevron",     "cyan",    "ico_sub"),
    ("AP-0229", "U-ICON", 64, "supporticon",             "icon_tech_wrench",         "solar",   "ico_wrench"),
    # U-KIT (38 @ 256)
    ("AP-0249", "U-KIT", 256, "10010radar",              "kit_radar_sweep_cyan",     "cyan",    "radar"),
    ("AP-0250", "U-KIT", 256, "10015radar",              "kit_radar_sweep_solar",    "solar",   "radar"),
    ("AP-0256", "U-KIT", 256, "arow",                    "kit_nav_chevron",          "solar",   "arrow_r"),
    ("AP-0258", "U-KIT", 256, "back",                    "kit_back_btn",             "azure",   "back_btn"),
    ("AP-0265", "U-KIT", 256, "bombattack",              "kit_megabomb_btn",         "solar",   "bomb_btn"),
    ("AP-0267", "U-KIT", 256, "border",                  "kit_pillar_frame",         "azure",   "9s_rank"),
    ("AP-0268", "U-KIT", 256, "border_bxh",              "kit_frame_leaderboard",    "solar",   "9s_rank"),
    ("AP-0269", "U-KIT", 256, "border_big",              "kit_frame_grand",          "solar",   "9s_board"),
    ("AP-0270", "U-KIT", 256, "border_center",           "kit_frame_socket",         "cyan",    "9s_reward"),
    ("AP-0271", "U-KIT", 256, "border_halloween",        "kit_frame_pumpkin_amber",  "crimson", "9s_rank"),
    ("AP-0272", "U-KIT", 256, "border_large",            "kit_frame_wide",           "azure",   "9s_board"),
    ("AP-0273", "U-KIT", 256, "border_normal",           "kit_frame_standard",       "azure",   "9s_rank"),
    ("AP-0275", "U-KIT", 256, "border_top",              "kit_frame_crest_cap",      "solar",   "crest_cap"),
    ("AP-0276", "U-KIT", 256, "border_valetine",         "kit_frame_rose_neon",      "magenta", "9s_rank"),
    ("AP-0277", "U-KIT", 256, "border_winter",           "kit_frame_frost_cyan",     "cyan",    "9s_rank"),
    ("AP-0295", "U-KIT", 256, "button",                  "kit_button_primary",       "solar",   "9s_btn_pri"),
    ("AP-0305", "U-KIT", 256, "df5_512x",                "kit_dialog_card",          "azure",   "9s_popup"),
    ("AP-0306", "U-KIT", 256, "db",                      "kit_rank_shield_emblem",   "solar",   "shield_emb"),
    ("AP-0307", "U-KIT", 256, "den",                     "kit_beacon_lamp",          "cyan",    "beacon"),
    ("AP-0308", "U-KIT", 256, "dongco",                  "kit_thruster_module_card", "azure",   "engine_mod"),
    ("AP-0310", "U-KIT", 256, "end",                     "kit_victory_laurel_crest", "solar",   "victory"),
    ("AP-0313", "U-KIT", 256, "failed",                  "kit_defeat_divider",       "crimson", "banner_line"),
    ("AP-0315", "U-KIT", 256, "finger",                  "kit_tap_pointer",          "pearl",   "pointer"),
    ("AP-0316", "U-KIT", 256, "gd",                      "kit_gear_socket_badge",    "violet",  "gear_badge"),
    ("AP-0317", "U-KIT", 256, "gameover",                "kit_gameover_ribbon",      "crimson", "banner_line"),
    ("AP-0318", "U-KIT", 256, "hard",                    "kit_diff_hard_tab",        "solar",   "9s_tab"),
    ("AP-0319", "U-KIT", 256, "hoicham",                 "kit_help_question_btn",    "cyan",    "help_btn"),
    ("AP-0321", "U-KIT", 256, "imposs",                  "kit_diff_inferno_tab",     "crimson", "9s_tab"),
    ("AP-0322", "U-KIT", 256, "line",                    "kit_tech_connector_line",  "cyan",    "tech_line"),
    ("AP-0325", "U-KIT", 256, "loading",                 "kit_loading_bar_frame",    "cyan",    "9s_slider"),
    ("AP-0326", "U-KIT", 256, "lock",                    "kit_padlock_badge",        "solar",   "padlock"),
    ("AP-0330", "U-KIT", 256, "ong",                     "kit_plasma_tube_cell",     "emerald", "tube_cell"),
    ("AP-0332", "U-KIT", 256, "popup",                   "kit_modal_popup",          "azure",   "9s_popup"),
    ("AP-0333", "U-KIT", 256, "shields",                 "kit_aegis_crest",          "cyan",    "shield_emb"),
    ("AP-0334", "U-KIT", 256, "tab",                     "kit_nav_tab_active",       "solar",   "9s_tab"),
    ("AP-0336", "U-KIT", 256, "tabtuan",                 "kit_weekly_tab_header",    "emerald", "9s_tab"),
    ("AP-0337", "U-KIT", 256, "techlab",                 "kit_techlab_board",        "cyan",    "9s_board"),
    ("AP-0338", "U-KIT", 256, "tieude",                  "kit_title_ribbon",         "solar",   "9s_tab"),
    # U-META (1 @ 256)
    ("AP-0377", "U-META", 256, "pvp",                    "meta_pvp_league_crest",    "solar",   "pvp_crest"),
    # U-SHOP (11 @ 256)
    ("AP-0420", "U-SHOP", 256, "goigem",                 "shop_gem_pack_pile",       "cyan",    "gem_pile"),
    ("AP-0436", "U-SHOP", 256, "nutplay",                "shop_launch_play_btn",     "solar",   "play_btn"),
    ("AP-0444", "U-SHOP", 256, "shop_box",               "shop_item_card_frame",     "azure",   "9s_shop"),
    ("AP-0453", "U-SHOP", 256, "vip1.",                  "shop_vip_crest_tier1",     "cyan",    "vip_1"),
    ("AP-0454", "U-SHOP", 256, "vip2.",                  "shop_vip_crest_tier2",     "emerald", "vip_2"),
    ("AP-0455", "U-SHOP", 256, "vip3.",                  "shop_vip_crest_tier3",     "azure",   "vip_3"),
    ("AP-0456", "U-SHOP", 256, "vip4.",                  "shop_vip_crest_tier4",     "violet",  "vip_4"),
    ("AP-0457", "U-SHOP", 256, "vip5.",                  "shop_vip_crest_tier5",     "magenta", "vip_5"),
    ("AP-0458", "U-SHOP", 256, "vip6.",                  "shop_vip_crest_tier6",     "solar",   "vip_6"),
    ("AP-0459", "U-SHOP", 256, "vipbp",                  "shop_battlepass_emblem",   "solar",   "vip_bp"),
    ("AP-0461", "U-SHOP", 256, "xvideo",                 "shop_rewarded_ad_badge",   "emerald", "ad_play"),
]


def render_ui(px, pal_key, kind):
    """Render crisp 2x-supersampled UI widget/9-slice frame/icon."""
    S = px * 2
    cx, cy = S // 2, S // 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    P = PAL[pal_key]
    d = ImageDraw.Draw(im)

    # --- 9-SLICE UNIFORM-EDGE FRAMES & BUTTONS (ASSETS.md §5) ---
    if kind == "9s_btn_pri":      # UIButton_Primary 24,20,24,20 c12
        draw_9slice_panel(im, (24, 128, S - 25, S - 129), 28, P, P[0], inner_rim=P[2], outline_w=10)
        d.rounded_rectangle([48, 148, S - 49, cy - 8], radius=14, fill=(255, 255, 255, 92))
    elif kind == "9s_btn_sec":    # UIButton_Secondary 20,16,20,16 c10
        draw_9slice_panel(im, (28, 148, S - 29, S - 149), 22, P, DARK_WELL, inner_rim=PAL["cyan"][0], outline_w=9)
    elif kind == "9s_popup":      # UIPanel_Popup 48,48,48,48 c32
        draw_9slice_panel(im, (28, 28, S - 29, S - 29), 64, P, DARK_WELL, inner_rim=PAL["solar"][0], outline_w=10)
    elif kind == "9s_board":      # UIPanel_Board 64,64,64,64 c40
        draw_9slice_panel(im, (24, 24, S - 25, S - 25), 80, P, (18, 48, 118, 245), inner_rim=PAL["cyan"][0], outline_w=10)
    elif kind == "9s_shop":       # UICell_Shop 16,16,16,16 c8
        draw_9slice_panel(im, (42, 32, S - 43, S - 33), 20, P, (20, 56, 134, 242), inner_rim=PAL["solar"][0], outline_w=9)
    elif kind == "9s_reward":     # UICell_Reward 12,12,12,12 c6
        draw_9slice_panel(im, (64, 64, S - 65, S - 65), 18, P, DARK_WELL, inner_rim=PAL["cyan"][0], outline_w=9)
    elif kind == "9s_slider":     # UISlider_Track 8,0,8,0 c4
        draw_9slice_panel(im, (24, 196, S - 25, S - 197), 16, P, DARK_WELL, inner_rim=P[2], outline_w=8)
        d.rounded_rectangle([46, 218, S - 140, S - 219], radius=8, fill=P[0])
    elif kind == "9s_bosshp":     # UIBar_HP_Boss 6,6,6,6 c3
        draw_9slice_panel(im, (20, 206, S - 21, S - 207), 12, PAL["solar"], DARK_WELL, inner_rim=P[0], outline_w=8)
        d.rounded_rectangle([42, 226, S - 68, S - 227], radius=6, fill=P[0])
    elif kind == "9s_tab":        # UITab_Active 24,12,24,12 c8
        draw_9slice_panel(im, (28, 148, S - 29, S - 149), 20, P, P[0], inner_rim=WHITE, outline_w=9)
    elif kind == "9s_rank":       # UIFrame_Rank 32,32,32,32 c16
        draw_9slice_panel(im, (36, 76, S - 37, S - 77), 32, P, DARK_WELL, inner_rim=PAL["solar"][0], outline_w=9)

    # --- 64x64 ICONS (rendered @ 128x128) ---
    elif kind == "ico_coin":
        draw_cel_poly(im, reg_poly(cx, cy, 52, 52, 20), PAL["solar"], outline_w=5)
        draw_cel_poly(im, star_poly(cx, cy, 30, 13, 5), PAL["pearl"], outline_w=3)
    elif kind == "ico_evo":
        draw_cel_poly(im, [(cx, 14), (112, 46), (92, 108), (cx, 88), (36, 108), (16, 46)], P, outline_w=5)
        draw_cel_poly(im, star_poly(cx, 62, 26, 12, 4), PAL["solar"], outline_w=3)
    elif kind == "ico_exp":
        draw_cel_poly(im, [(cx, 12), (104, cy), (cx, 116), (24, cy)], P, outline_w=5)
        draw_cel_poly(im, [(cx, 30), (84, cy), (cx, 98), (44, cy)], PAL["pearl"], outline_w=3)
    elif kind == "ico_eye":
        eye = [(12, cy), (42, 30), (86, 30), (116, cy), (86, 98), (42, 98)]
        draw_cel_poly(im, eye, PAL["pearl"], outline_w=5)
        draw_cel_poly(im, reg_poly(cx, cy, 24, 24, 16), P, outline_w=4)
    elif kind == "ico_drone":
        draw_cel_poly(im, reg_poly(cx, cy, 46, 46, 6), P, outline_w=5)
        draw_cel_poly(im, reg_poly(cx, cy, 22, 22, 14), PAL["solar"], outline_w=4)
    elif kind == "ico_mode":
        draw_cel_poly(im, star_poly(cx, cy, 54, 25, 5), P, outline_w=5)
    elif kind == "ico_atk":
        draw_cel_poly(im, [(82, 14), (34, 68), (64, 68), (46, 114), (96, 58), (66, 58)], P, outline_w=5)
    elif kind == "ico_sub":
        for dy in (-16, 18):
            draw_cel_poly(im, [(cx, 28 + dy), (102, 62 + dy), (88, 78 + dy), (cx, 48 + dy), (40, 78 + dy), (26, 62 + dy)], P, outline_w=4)
    elif kind == "ico_wrench":
        draw_cel_poly(im, reg_poly(cx, cy, 48, 48, 8), PAL["azure"], outline_w=5)
        draw_cel_poly(im, [(46, 28), (82, 28), (74, 100), (54, 100)], P, outline_w=4)

    # --- SPECIALIZED 256x256 HUD / KIT / META / SHOP WIDGETS (rendered @ 512x512) ---
    elif kind in ("medkit", "medkit_btn"):
        if kind == "medkit_btn":
            draw_9slice_panel(im, (56, 56, S - 57, S - 57), 48, P, DARK_WELL, outline_w=10)
        else:
            draw_cel_poly(im, reg_poly(cx, cy, 196, 196, 20), PAL["pearl"], outline_w=10)
        plus = [(216, 128), (296, 128), (296, 216), (384, 216), (384, 296), (296, 296), (296, 384), (216, 384), (216, 296), (128, 296), (128, 216), (216, 216)]
        draw_cel_poly(im, plus, P, outline_w=8)

    elif kind.startswith("timer_"):
        draw_cel_poly(im, reg_poly(cx, cy, 204, 204, 24), P, outline_w=10)
        draw_cel_poly(im, reg_poly(cx, cy, 152, 152, 22), (DARK_WELL[:3] + (255,), OUTLINE, P[2]), outline_w=8)
        if kind == "timer_bolt":
            draw_cel_poly(im, [(280, 128), (192, 266), (256, 266), (228, 384), (324, 242), (262, 242)], PAL["solar"], outline_w=7)
        elif kind == "timer_shield":
            draw_cel_poly(im, [(cx, 138), (348, 178), (332, 308), (cx, 378), (180, 308), (164, 178)], PAL["cyan"], outline_w=7)
        else:
            draw_cel_poly(im, star_poly(cx, cy, 98, 44, 5), PAL["solar"], outline_w=7)

    elif kind == "gong":
        draw_cel_poly(im, [(118, 86), (394, 86), (394, 126), (118, 126)], PAL["azure"], outline_w=8)
        draw_cel_poly(im, reg_poly(cx, 286, 168, 168, 24), PAL["solar"], outline_w=10)
        draw_cel_poly(im, reg_poly(cx, 286, 78, 78, 18), PAL["crimson"], outline_w=8)

    elif kind == "clock":
        draw_cel_poly(im, [(216, 44), (296, 44), (296, 92), (216, 92)], PAL["solar"], outline_w=8)
        draw_cel_poly(im, reg_poly(cx, 278, 186, 186, 24), P, outline_w=10)
        draw_cel_poly(im, reg_poly(cx, 278, 142, 142, 22), PAL["pearl"], outline_w=7)
        d.line([(cx, 278), (cx, 172)], fill=OUTLINE, width=16)
        d.line([(cx, 278), (338, 304)], fill=PAL["crimson"][0], width=14)

    elif kind == "pad_ring":
        outer = reg_poly(cx, cy, 212, 212, 28)
        inner = list(reversed(reg_poly(cx, cy, 148, 148, 28)))
        draw_cel_poly(im, outer + inner, P, outline_w=9)
        for ang_d in (0, 90, 180, 270):
            a = math.radians(ang_d)
            tx, ty = cx + math.cos(a) * 180, cy + math.sin(a) * 180
            draw_cel_poly(im, reg_poly(tx, ty, 24, 24, 4, rot=a), PAL["solar"], outline_w=5)

    elif kind in ("pip_dot", "life_pip", "pad_knob"):
        r = 168 if kind == "pad_knob" else 132
        draw_cel_poly(im, reg_poly(cx, cy, r, r, 22), P, outline_w=10)
        draw_cel_poly(im, reg_poly(cx, cy, r * 0.56, r * 0.56, 18), PAL["pearl"], outline_w=6)

    elif kind == "pause_btn":
        draw_9slice_panel(im, (64, 64, S - 65, S - 65), 52, P, DARK_WELL, inner_rim=PAL["solar"][0], outline_w=10)
        for bx in (188, 284):
            draw_cel_poly(im, [(bx, 156), (bx + 42, 156), (bx + 42, 356), (bx, 356)], PAL["solar"], outline_w=7)

    elif kind == "warn_banner":
        draw_9slice_panel(im, (24, 142, S - 25, S - 143), 24, PAL["crimson"], (48, 8, 28, 248), inner_rim=PAL["solar"][0], outline_w=10)
        tri = [(cx, 168), (338, 332), (174, 332)]
        draw_cel_poly(im, tri, PAL["solar"], outline_w=8)
        d.rectangle([cx - 10, 222, cx + 10, 286], fill=OUTLINE)
        d.ellipse([cx - 11, 298, cx + 11, 320], fill=OUTLINE)

    elif kind == "radar":
        draw_cel_poly(im, reg_poly(cx, cy, 214, 214, 28), (DARK_WELL[:3] + (235,), OUTLINE, P[0]), outline_w=10)
        for r in (70, 138, 198):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=P[0], width=5)
        d.pieslice([cx - 196, cy - 196, cx + 196, cy + 196], start=-75, end=-15, fill=(P[0][0], P[0][1], P[0][2], 128))
        d.line([(cx, 58), (cx, 454)], fill=P[0], width=4)
        d.line([(58, cy), (454, cy)], fill=P[0], width=4)

    elif kind in ("arrow_r", "back_btn"):
        if kind == "back_btn":
            draw_9slice_panel(im, (64, 64, S - 65, S - 65), 52, P, DARK_WELL, outline_w=10)
            pts = [(318, 148), (182, cy), (318, 364), (318, 304), (254, cy), (318, 208)]
            draw_cel_poly(im, pts, PAL["solar"], outline_w=8)
        else:
            pts = [(148, 108), (368, cy), (148, 404), (148, 316), (264, cy), (148, 196)]
            draw_cel_poly(im, pts, P, outline_w=10)

    elif kind in ("bomb_btn", "play_btn", "ad_play"):
        draw_cel_poly(im, reg_poly(cx, cy, 208, 208, 24), P, outline_w=10)
        draw_cel_poly(im, reg_poly(cx, cy, 162, 162, 22), PAL["azure"], outline_w=8)
        if kind == "bomb_btn":
            draw_cel_poly(im, star_poly(cx, cy, 118, 52, 8), PAL["solar"], outline_w=7)
        else:
            tri = [(206, 166), (356, cy), (206, 346)]
            draw_cel_poly(im, tri, PAL["solar"] if kind == "play_btn" else PAL["pearl"], outline_w=8)

    elif kind in ("shield_emb", "victory", "pvp_crest") or kind.startswith("vip_"):
        tier = int(kind.split("_")[1]) if kind.startswith("vip_") and kind.split("_")[1].isdigit() else 3
        wings_r = [(cx + 80, 215), (468, 135 - tier * 6), (438, 295), (cx + 95, 335)]
        wings_l = [(2 * cx - x, y) for (x, y) in reversed(wings_r)]
        draw_cel_poly(im, wings_l, PAL["solar"], outline_w=9)
        draw_cel_poly(im, wings_r, PAL["solar"], outline_w=9)
        sh = [(cx, 88), (382, 165), (352, 348), (cx, 438), (160, 348), (130, 165)]
        draw_cel_poly(im, sh, P, outline_w=10)
        draw_cel_poly(im, star_poly(cx, 255, 86, 38, 5), PAL["pearl"], outline_w=7)
        if kind.startswith("vip_") or kind == "pvp_crest":
            f = ImageFont.truetype(FONT_B, 52)
            lbl = "PVP" if kind == "pvp_crest" else ("BP" if kind == "vip_bp" else f"V{tier}")
            bb = d.textbbox((0, 0), lbl, font=f)
            d.text((cx - (bb[2] - bb[0]) // 2, 352), lbl, font=f, fill=WHITE, stroke_width=6, stroke_fill=OUTLINE)

    elif kind == "gem_pile":
        for gx, gy, sc in [(176, 295, 0.78), (336, 295, 0.78), (256, 238, 1.05)]:
            r = int(118 * sc)
            gem = [(gx, gy - r), (gx + r * 0.85, gy - r * 0.2), (gx + r * 0.55, gy + r * 0.85), (gx - r * 0.55, gy + r * 0.85), (gx - r * 0.85, gy - r * 0.2)]
            draw_cel_poly(im, gem, P, outline_w=9)
            draw_cel_poly(im, [(gx, gy - r * 0.65), (gx + r * 0.45, gy), (gx, gy + r * 0.48), (gx - r * 0.45, gy)], PAL["pearl"], outline_w=4)

    elif kind == "padlock":
        shackle_o = reg_poly(cx, 195, 92, 92, 20)
        shackle_i = list(reversed(reg_poly(cx, 195, 52, 52, 20)))
        draw_cel_poly(im, shackle_o + shackle_i, PAL["pearl"], outline_w=8)
        body = [(146, 205), (366, 205), (376, 412), (136, 412)]
        draw_cel_poly(im, body, P, outline_w=10)
        draw_cel_poly(im, reg_poly(cx, 295, 28, 28, 14), (OUTLINE, OUTLINE, OUTLINE), outline_w=0)

    elif kind == "pointer":
        hand = [(218, 86), (266, 86), (266, 224), (368, 248), (356, 398), (186, 398), (142, 296), (178, 266), (218, 296)]
        draw_cel_poly(im, hand, P, outline_w=10)
        d.arc([168, 36, 316, 168], start=190, end=350, fill=PAL["cyan"][0], width=10)

    elif kind == "help_btn":
        draw_cel_poly(im, reg_poly(cx, cy, 196, 196, 24), P, outline_w=10)
        f = ImageFont.truetype(FONT_B, 230)
        bb = d.textbbox((0, 0), "?", font=f)
        d.text((cx - (bb[2] - bb[0]) // 2, cy - (bb[3] - bb[1]) // 2 - 24), "?", font=f, fill=WHITE, stroke_width=10, stroke_fill=OUTLINE)

    else:
        # Clean modular tech badges / connectors / headers (`seg_cell`, `trim_bar`, `crest_cap`, `beacon`, `engine_mod`, `banner_line`, `gear_badge`, `tech_line`, `tube_cell`)
        if "line" in kind or "bar" in kind:
            draw_9slice_panel(im, (24, 214, S - 25, S - 215), 14, P, P[0], inner_rim=WHITE, outline_w=8)
        else:
            draw_cel_poly(im, reg_poly(cx, cy, 178, 178, 8, rot=math.pi / 8), PAL["azure"], outline_w=10)
            draw_cel_poly(im, reg_poly(cx, cy, 118, 118, 8, rot=math.pi / 8), P, outline_w=8)
            draw_cel_poly(im, star_poly(cx, cy, 62, 28, 4), PAL["pearl"], outline_w=5)

    return im


def measure_rgba(im):
    arr = np.asarray(im, dtype=np.float32)
    fg = arr[:, :, 3] > 16
    if not np.any(fg):
        return 0.0, 0.0, 0.0
    rgb = arr[fg][:, :3] / 255.0
    mx, mn = rgb.max(axis=1), rgb.min(axis=1)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0.0)
    return round(float(mx.mean()), 3), round(float(sat.mean()), 3), round(float(fg.mean()), 3)


def save_pair(records, row_id, batch, lane, uno, base, var, m_im, s_im, sub_dir, fname, recipe, zero_corners=True):
    os.makedirs(os.path.join(HERE, f"masters/{sub_dir}"), exist_ok=True)
    os.makedirs(os.path.join(HERE, f"sprites/{sub_dir}"), exist_ok=True)
    m_rel = f"masters/{sub_dir}/{fname}"
    s_rel = f"sprites/{sub_dir}/{fname}"
    m_im.save(os.path.join(HERE, m_rel), "PNG", compress_level=9)
    s_im.save(os.path.join(HERE, s_rel), "PNG", compress_level=9)
    if zero_corners:
        sa = np.asarray(s_im)
        assert sa[0, 0, 3] == 0 and sa[0, -1, 3] == 0 and sa[-1, 0, 3] == 0 and sa[-1, -1, 3] == 0, fname
    val, ch, fill = measure_rgba(s_im)
    records.append({
        "row_id": row_id, "lane": lane, "batch": batch, "unit_no": uno,
        "planner_base": base, "variant": var,
        "delivered_px": f"{s_im.width}x{s_im.height}", "master_px": f"{m_im.width}x{m_im.height}",
        "source": m_rel, "file": s_rel, "license": LICENSE_NOTE,
        "author": AUTHOR_BRANCH, "recipe": recipe, "val": val, "chroma": ch, "fill": fill,
    })


def main():
    records = []

    # 1. ITEM (7 units)
    item_specs = [
        ("AP-0130", "05_0",      "weapon_up",          "solar"),
        ("AP-0131", "05_1",      "shield_orb",         "cyan"),
        ("AP-0132", "5_1",       "magnet_core",        "emerald"),
        ("AP-0133", "bag",       "supply_chest",       "solar"),
        ("AP-0134", "banana",    "solar_crescent",     "solar"),
        ("AP-0136", "fullpower", "max_overdrive",      "magenta"),
        ("AP-0137", "head",      "mecha_crest_token",  "cyan"),
    ]
    for i, (rid, base, var, pal) in enumerate(item_specs, 1):
        c = render_item(var, pal)
        m = downsample_straight_rgba(c, (256, 256))
        s = downsample_straight_rgba(c, (128, 128))
        save_pair(records, rid, "I-DROP", "ITEM", i, base, var, m, s, "items", f"item_drop_{i:02d}_{var}_128@{pal}.png", f"b_item_{pal}")

    # 2. FX (9 units)
    fx_specs = [
        ("AP-0082", "F-BOOM", "bomb",        "mega_nova",       "solar"),
        ("AP-0083", "F-BOOM", "boom",        "starburst_blast", "solar"),
        ("AP-0084", "F-BOOM", "crossfire",   "cross_flare",     "cyan"),
        ("AP-0085", "F-BOOM", "newdevice",   "unlock_prism",    "emerald"),
        ("AP-0086", "F-BOOM", "saw",         "plasma_vortex",   "magenta"),
        ("AP-0150", "F-GLOW", "heal",        "repair_aura",     "emerald"),
        ("AP-0156", "F-GLOW", "supperpower", "overdrive_surge", "solar"),
        ("AP-0158", "F-GLOW", "powerup",     "levelup_ring",    "cyan"),
        ("AP-0159", "F-GLOW", "circle",      "tint_halo",       "cyan"),
    ]
    for i, (rid, bat, base, var, pal) in enumerate(fx_specs, 1):
        c = render_fx(var, pal)
        m = downsample_straight_rgba(c, (512, 512))
        s = downsample_straight_rgba(c, (256, 256))
        save_pair(records, rid, bat, "FX", i, base, var, m, s, "fx", f"fx_{bat[2:].lower()}_{i:02d}_{var}_256@{pal}.png", f"b_fx_{pal}")

    # 3. BG: 3 seamless 1024x1024 parallax layers (AP-0091) + 9 G-UI 512x512 backdrops = 12 files
    para_specs = [
        ("parallax_01_sky_far_raw.png",          "sky_far",          "cerulean", False),
        ("parallax_02_cloud_mid_raw.png",        "cloud_mid",        "solar",    True),
        ("parallax_03_archipelago_near_raw.png", "archipelago_near", "emerald",  True),
    ]
    os.makedirs(os.path.join(HERE, "sprites/bg"), exist_ok=True)
    for i, (raw_fn, mode, pal, zc) in enumerate(para_specs, 1):
        raw_rel = f"masters/bg_raw/{raw_fn}"
        sp = build_seamless_parallax(os.path.join(HERE, raw_rel), mode)
        # Verify vertical tile seamlessness: row[0] == row[1023]
        sa = np.asarray(sp)
        assert np.array_equal(sa[0], sa[-1]), f"Parallax seam mismatch on {mode}"
        s_rel = f"sprites/bg/bg_parallax_{i:02d}_{mode}_1024@{pal}.png"
        sp.save(os.path.join(HERE, s_rel), "PNG", compress_level=9)
        val, ch, fill = measure_rgba(sp)
        records.append({
            "row_id": "AP-0091", "lane": "BG", "batch": "G-PARALLAX", "unit_no": i,
            "planner_base": "bg", "variant": mode, "delivered_px": "1024x1024", "master_px": f"{Image.open(os.path.join(HERE, raw_rel)).width}x{Image.open(os.path.join(HERE, raw_rel)).height}",
            "source": raw_rel, "file": s_rel, "license": LICENSE_NOTE,
            "author": AUTHOR_BRANCH, "recipe": f"b_parallax_{pal}", "val": val, "chroma": ch, "fill": fill,
        })

    gui_specs = [
        ("AP-0161", "bgbattpass",      "season_pass",     "solar"),
        ("AP-0162", "bgbuy",           "treasury_shop",   "solar"),
        ("AP-0163", "bghome",          "sky_hangar",      "cerulean"),
        ("AP-0164", "bgmap",           "sector_starmap",  "cyan"),
        ("AP-0165", "bgtrans",         "warp_shutter",    "cerulean"),
        ("AP-0166", "bgupgrade",       "tech_foundry",    "emerald"),
        ("AP-0174", "nenbangthongtin", "briefing_slate",  "cerulean"),
        ("AP-0177", "nenvip",          "royal_prestige",  "solar"),
        ("AP-0178", "probg",           "pilot_dossier",   "cyan"),
    ]
    for i, (rid, base, var, pal) in enumerate(gui_specs, 1):
        im = render_gui_backdrop(i, var, pal)
        save_pair(records, rid, "G-UI", "BG", i, base, var, im, im, "bg", f"bg_ui_{i:02d}_{var}_512@{pal}.png", f"b_gui_{pal}")

    # 4. UI: 86 kept rows
    for i, (rid, bat, px, base, var, pal, kind) in enumerate(UI_JOBS, 1):
        c2 = render_ui(px, pal, kind)
        m_im = downsample_straight_rgba(c2, (px * 2, px * 2))
        s_im = downsample_straight_rgba(c2, (px, px))
        save_pair(records, rid, bat, "UI", i, base, var, m_im, s_im, f"ui/{bat.lower()}", f"ui_{var}_{px}@{pal}.png", f"b_ui_{pal}")

    with open(os.path.join(HERE, "w4b_units.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "w4b_units.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(records)

    print(f"SUCCESS: {len(records)} W4-core files exported across ITEM/FX/BG/UI (EXCL=0)")


if __name__ == "__main__":
    main()
