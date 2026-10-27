#!/usr/bin/env python3
"""
Build Wave W2 — ENEMY Lane (34 units) for Variant B ("Solar Neon Arcade-Pop").
Author branch: arena/eca8588b-windwings-space-shooter-game-p

Exact 34 units per art-planner.csv:
  - E-BODY   (AP-0046..AP-0068, 23 units): 128x128 RGBA (masters/ 256x256, rendered at 4x = 512x512)
  - E-BULLET (AP-0070..AP-0080, 11 units): 64x64 RGBA   (masters/ 128x128, rendered at 4x = 256x256)
"""

import csv
import json
import math
import os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHOR_BRANCH = "arena/eca8588b-windwings-space-shooter-game-p"
LICENSE_NOTE = "chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)"

# Enemy Invader Armada — Solar Neon Arcade-Pop Menace Palette
OUTLINE      = (22, 6, 48, 255)      # #160630 deep violet-indigo cel outline

CRIM_LIGHT   = (255, 112, 142, 255)
CRIM_BASE    = (255, 30, 86, 255)    # #FF1E56 hyper-crimson
CRIM_SHADE   = (168, 8, 52, 255)

MAGE_LIGHT   = (255, 136, 208, 255)
MAGE_BASE    = (255, 36, 150, 255)   # #FF2496 neon-magenta
MAGE_SHADE   = (158, 10, 92, 255)

VIOL_LIGHT   = (188, 118, 255, 255)
VIOL_BASE    = (123, 44, 191, 255)   # #7B2CBF electric-violet
VIOL_SHADE   = (66, 16, 120, 255)

HULL_LIGHT   = (124, 102, 184, 255)
HULL_BASE    = (72, 52, 128, 255)    # armored alien violet-steel
HULL_SHADE   = (38, 24, 78, 255)

AMBR_LIGHT   = (255, 242, 128, 255)
AMBR_BASE    = (255, 184, 0, 255)    # #FFB800 hazard solar-amber
AMBR_SHADE   = (196, 108, 0, 255)

CORE_WHITE   = (255, 252, 232, 255)
CORE_YELL    = (255, 232, 24, 255)
TOXIC_LIME   = (168, 255, 36, 255)


def downsample_straight_rgba(im, target_size):
    """Premultiplied Lanczos downsample -> unpremultiply back to straight RGBA (Gate A1)."""
    if im.size == target_size:
        return im.copy()
    arr = np.asarray(im, dtype=np.float32)
    a = arr[:, :, 3:4] / 255.0
    pm = np.concatenate([arr[:, :, :3] * a, arr[:, :, 3:4]], axis=2)
    pm_im = Image.fromarray(np.clip(np.round(pm), 0, 255).astype(np.uint8), "RGBA")
    pm_sm = pm_im.resize(target_size, Image.LANCZOS)
    s = np.asarray(pm_sm, dtype=np.float32)
    sa = s[:, :, 3:4] / 255.0
    rgb = np.where(sa > 1e-3, s[:, :, :3] / np.maximum(sa, 1e-3), 0.0)
    out = np.concatenate([np.clip(np.round(rgb), 0, 255), np.clip(np.round(s[:, :, 3:4]), 0, 255)], axis=2)
    out[out[:, :, 3] < 4] = 0
    for cy in (0, target_size[1] - 1):
        for cx in (0, target_size[0] - 1):
            out[cy, cx] = [0, 0, 0, 0]
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def draw_cel_poly(canvas, pts, base_c, shade_c, light_c, outline_w=6):
    """3-tone 30-deg top-left cel-shaded polygon with crisp dark violet-indigo outline."""
    if len(pts) < 3:
        return
    W, H = canvas.size
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.polygon(pts, fill=base_c)

    if shade_c is not None:
        s_pts = [(x + span * 0.14, y + span * 0.16) for (x, y) in pts]
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).polygon(pts, fill=shade_c)
        inv = Image.new("L", (W, H), 255)
        ImageDraw.Draw(inv).polygon([(x - span * 0.12, y - span * 0.14) for (x, y) in pts], fill=0)
        sh_a = np.minimum(np.asarray(mask), np.asarray(inv))
        sh_arr = np.asarray(sh).copy()
        sh_arr[:, :, 3] = sh_a
        layer = Image.alpha_composite(layer, Image.fromarray(sh_arr, "RGBA"))

    if light_c is not None:
        hi_pts = [(cx + (x - cx) * 0.68 - span * 0.08, cy + (y - cy) * 0.68 - span * 0.09) for (x, y) in pts]
        hi = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(hi).polygon(hi_pts, fill=light_c)
        hi_arr = np.asarray(hi).copy()
        hi_arr[:, :, 3] = np.minimum(hi_arr[:, :, 3], np.asarray(mask))
        layer = Image.alpha_composite(layer, Image.fromarray(hi_arr, "RGBA"))

    if outline_w > 0:
        od = ImageDraw.Draw(layer)
        closed = list(pts) + [pts[0]]
        od.line(closed, fill=OUTLINE, width=outline_w, joint="curve")
        r = outline_w * 0.45
        for px, py in pts:
            od.ellipse([px - r, py - r, px + r, py + r], fill=OUTLINE)

    canvas.alpha_composite(layer)


def mirror_pts(pts, cx):
    return [(2 * cx - x, y) for (x, y) in reversed(pts)]


def draw_sym(canvas, right_pts, cx, base_c, shade_c, light_c, outline_w=7):
    draw_cel_poly(canvas, mirror_pts(right_pts, cx), base_c, shade_c, light_c, outline_w=outline_w)
    draw_cel_poly(canvas, right_pts, base_c, shade_c, light_c, outline_w=outline_w)


def draw_menace_eye(canvas, cx, cy, rx, ry, ring_c=AMBR_BASE, core_c=CORE_YELL, outline_w=6):
    """Signature arcade enemy cyclops/core eye with white-hot glint."""
    r_pts = [(cx + math.cos(a) * rx * 1.32, cy + math.sin(a) * ry * 1.32) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
    draw_cel_poly(canvas, r_pts, ring_c, AMBR_SHADE, AMBR_LIGHT, outline_w=outline_w)
    c_pts = [(cx + math.cos(a) * rx, cy + math.sin(a) * ry) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
    draw_cel_poly(canvas, c_pts, core_c, CRIM_BASE, CORE_WHITE, outline_w=outline_w)
    d = ImageDraw.Draw(canvas)
    d.ellipse([cx - rx * 0.48, cy - ry * 0.52, cx - rx * 0.08, cy - ry * 0.12], fill=CORE_WHITE)


def draw_top_thruster(canvas, x, y_top, y_bot, w, outline_w=6):
    """Top-mounted thruster nozzle for downward-diving enemies."""
    pts = [(x - w * 0.62, y_top), (x + w * 0.62, y_top), (x + w * 0.46, y_bot), (x - w * 0.46, y_bot)]
    draw_cel_poly(canvas, pts, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT, outline_w=outline_w)
    ImageDraw.Draw(canvas).ellipse([x - w * 0.38, y_top - w * 0.22, x + w * 0.38, y_top + w * 0.22], fill=MAGE_LIGHT, outline=OUTLINE, width=3)


def draw_down_fang(canvas, x, y_base, y_tip, w, c_base=CRIM_BASE, c_sh=CRIM_SHADE, c_li=CRIM_LIGHT, outline_w=6):
    """Downward-pointing weapon fang / mandible."""
    pts = [(x - w * 0.55, y_base), (x + w * 0.55, y_base), (x, y_tip)]
    draw_cel_poly(canvas, pts, c_base, c_sh, c_li, outline_w=outline_w)


E_BODY_SPECS = [
    ("AP-0046", "1.",          "scout_dart",       "crimson", "b_enemy_crimson"),
    ("AP-0047", "14_2",        "viper_lance",      "crimson", "b_enemy_crimson"),
    ("AP-0048", "212_1",       "wasp_raider",      "magenta", "b_enemy_magenta"),
    ("AP-0049", "23_0",        "manta_glider",     "violet",  "b_enemy_violet"),
    ("AP-0050", "5_0",         "beetle_cruiser",   "crimson", "b_enemy_crimson"),
    ("AP-0051", "5_2",         "swarmling_pod",    "amber",   "b_enemy_amber"),
    ("AP-0052", "6.",          "stalker_blade",    "magenta", "b_enemy_magenta"),
    ("AP-0053", "7_1",         "dread_carrier",    "violet",  "b_enemy_violet"),
    ("AP-0054", "7_4",         "spire_frigate",    "crimson", "b_enemy_crimson"),
    ("AP-0055", "cb",          "centurion_mk1",    "crimson", "b_enemy_crimson"),
    ("AP-0056", "cb-",         "centurion_turret", "amber",   "b_enemy_amber"),
    ("AP-0057", "cb-009a",     "wingpod_wide",     "crimson", "b_enemy_crimson"),
    ("AP-0058", "cb-009b",     "wingpod_core",     "magenta", "b_enemy_magenta"),
    ("AP-0059", "cd",          "cyber_disc",       "violet",  "b_enemy_violet"),
    ("AP-0060", "da",          "void_sentinel",    "magenta", "b_enemy_magenta"),
    ("AP-0061", "droid",       "automaton_droid",  "amber",   "b_enemy_amber"),
    ("AP-0062", "droid1_timer","chrono_mine",      "amber",   "b_enemy_amber"),
    ("AP-0063", "e",           "phantom_hex",      "violet",  "b_enemy_violet"),
    ("AP-0064", "e_",          "reaper_scythe",    "crimson", "b_enemy_crimson"),
    ("AP-0065", "e_3308a",     "juggernaut_hull",  "crimson", "b_enemy_crimson"),
    ("AP-0066", "e_3308b",     "juggernaut_core",  "amber",   "b_enemy_amber"),
    ("AP-0067", "enemy_hp",    "hp_pip_bar",       "crimson", "b_enemy_hud"),
    ("AP-0068", "enemytut",    "target_drone",     "amber",   "b_enemy_amber"),
]

E_BULLET_SPECS = [
    ("AP-0070", "22_0",          "needle_dart",   "crimson", "b_ebullet_crimson"),
    ("AP-0071", "7_2",           "twin_fang",     "magenta", "b_ebullet_magenta"),
    ("AP-0072", "7_3",           "lance_spear",   "crimson", "b_ebullet_crimson"),
    ("AP-0073", "9.",            "beam_shard",    "amber",   "b_ebullet_amber"),
    ("AP-0074", "ebullet",       "nova_star",     "magenta", "b_ebullet_magenta"),
    ("AP-0075", "efx_bullethit", "hit_spark",     "amber",   "b_ebullet_amber"),
    ("AP-0076", "sword",         "energy_sword",  "crimson", "b_ebullet_crimson"),
    ("AP-0077", "warning",       "hazard_sign",   "amber",   "b_ebullet_amber"),
    ("AP-0078", "arrow",         "lock_chevron",  "crimson", "b_ebullet_crimson"),
    ("AP-0079", "blt",           "plasma_orb",    "crimson", "b_ebullet_crimson"),
    ("AP-0080", "blt_",          "ring_pulse",    "violet",  "b_ebullet_violet"),
]


def pal_tuple(pal):
    if pal == "crimson":
        return CRIM_BASE, CRIM_SHADE, CRIM_LIGHT
    if pal == "magenta":
        return MAGE_BASE, MAGE_SHADE, MAGE_LIGHT
    if pal == "violet":
        return VIOL_BASE, VIOL_SHADE, VIOL_LIGHT
    return AMBR_BASE, AMBR_SHADE, AMBR_LIGHT


def render_ebody(idx, variant, pal):
    """Render 1 of 23 distinct downward-facing Enemy silhouettes at 512x512 (4x of 128)."""
    S = 512
    cx, cy = S * 0.5, S * 0.5
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cb, cs, cl = pal_tuple(pal)

    if variant == "scout_dart":
        # AP-0046: Sleek downward arrowhead scout dart
        draw_top_thruster(im, cx, 56, 128, 66)
        w_r = [(cx + 42, 130), (cx + 188, 92), (cx + 145, 315), (cx + 46, 365)]
        draw_sym(im, w_r, cx, HULL_BASE, HULL_SHADE, HULL_LIGHT)
        st_r = [(cx + 68, 155), (cx + 162, 128), (cx + 132, 275), (cx + 65, 305)]
        draw_sym(im, st_r, cx, cb, cs, cl, outline_w=5)
        body = [(cx, 462), (cx + 76, 305), (cx + 64, 108), (cx - 64, 108), (cx - 76, 305)]
        draw_cel_poly(im, body, cb, cs, cl, outline_w=8)
        draw_menace_eye(im, cx, 248, 34, 46)

    elif variant == "viper_lance":
        # AP-0047: Twin-fang narrow dive interceptor
        draw_top_thruster(im, cx - 48, 52, 118, 46)
        draw_top_thruster(im, cx + 48, 52, 118, 46)
        fang_r = [(cx + 32, 245), (cx + 112, 225), (cx + 84, 466), (cx + 28, 385)]
        draw_sym(im, fang_r, cx, cb, cs, cl, outline_w=8)
        fin_r = [(cx + 72, 135), (cx + 168, 195), (cx + 142, 275), (cx + 76, 245)]
        draw_sym(im, fin_r, cx, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT, outline_w=6)
        hull = [(cx, 395), (cx + 72, 275), (cx + 68, 96), (cx - 68, 96), (cx - 72, 275)]
        draw_cel_poly(im, hull, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        draw_menace_eye(im, cx, 225, 36, 36, ring_c=MAGE_BASE, core_c=CORE_YELL)

    elif variant == "wasp_raider":
        # AP-0048: Insectoid wasp raider with swept wings + bottom stinger
        draw_down_fang(im, cx, 355, 468, 64, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT)
        w_r = [(cx + 45, 165), (cx + 215, 115), (cx + 225, 235), (cx + 68, 285)]
        draw_sym(im, w_r, cx, cb, cs, cl, outline_w=7)
        low_r = [(cx + 52, 265), (cx + 168, 315), (cx + 135, 385), (cx + 45, 345)]
        draw_sym(im, low_r, cx, VIOL_BASE, VIOL_SHADE, VIOL_LIGHT, outline_w=6)
        abdomen = [(cx, 82), (cx + 82, 165), (cx + 68, 365), (cx - 68, 365), (cx - 82, 165)]
        draw_cel_poly(im, abdomen, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        # Wasp hazard stripes
        for sy in (155, 205):
            st = [(cx - 62, sy), (cx + 62, sy), (cx + 58, sy + 26), (cx - 58, sy + 26)]
            draw_cel_poly(im, st, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT, outline_w=4)
        draw_menace_eye(im, cx, 295, 38, 32)

    elif variant == "manta_glider":
        # AP-0049: Wide-wingspan manta bomber (269x162 aspect -> wide silhouette)
        draw_top_thruster(im, cx - 72, 105, 168, 52)
        draw_top_thruster(im, cx + 72, 105, 168, 52)
        manta_r = [(cx + 40, 145), (cx + 236, 215), (cx + 212, 368), (cx + 118, 325), (cx + 48, 385)]
        draw_sym(im, manta_r, cx, cb, cs, cl, outline_w=8)
        trim_r = [(cx + 85, 195), (cx + 208, 235), (cx + 188, 325), (cx + 92, 285)]
        draw_sym(im, trim_r, cx, MAGE_BASE, MAGE_SHADE, MAGE_LIGHT, outline_w=5)
        draw_down_fang(im, cx - 125, 315, 415, 42, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT)
        draw_down_fang(im, cx + 125, 315, 415, 42, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT)
        core_b = [(cx, 418), (cx + 82, 315), (cx + 68, 132), (cx - 68, 132), (cx - 82, 315)]
        draw_cel_poly(im, core_b, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        draw_menace_eye(im, cx, 265, 44, 34, ring_c=CRIM_BASE, core_c=TOXIC_LIME)

    elif variant == "beetle_cruiser":
        # AP-0050: Heavy armored pincer beetle cruiser
        draw_top_thruster(im, cx, 48, 118, 92)
        # Giant bottom mandibles
        pinc_r = [(cx + 55, 335), (cx + 158, 355), (cx + 132, 468), (cx + 42, 455), (cx + 78, 395)]
        draw_sym(im, pinc_r, cx, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT, outline_w=8)
        shell_r = [(cx + 20, 96), (cx + 198, 155), (cx + 212, 335), (cx + 115, 385), (cx + 20, 365)]
        draw_sym(im, shell_r, cx, cb, cs, cl, outline_w=8)
        spine = [(cx, 88), (cx + 86, 155), (cx + 74, 375), (cx - 74, 375), (cx - 86, 155)]
        draw_cel_poly(im, spine, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        draw_menace_eye(im, cx, 255, 48, 42)

    elif variant == "swarmling_pod":
        # AP-0051: Compact swarm pod with 3 bottom spikes
        for sx in (cx - 72, cx, cx + 72):
            draw_down_fang(im, sx, 315, 428, 46, CRIM_BASE, CRIM_SHADE, CRIM_LIGHT)
        ear_r = [(cx + 105, 165), (cx + 178, 135), (cx + 168, 265), (cx + 108, 285)]
        draw_sym(im, ear_r, cx, VIOL_BASE, VIOL_SHADE, VIOL_LIGHT, outline_w=7)
        pts = [(cx + math.cos(a) * 138, 238 + math.sin(a) * 124) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
        draw_cel_poly(im, pts, cb, cs, cl, outline_w=8)
        draw_menace_eye(im, cx, 245, 46, 46, ring_c=CRIM_BASE, core_c=CORE_WHITE)

    elif variant == "stalker_blade":
        # AP-0052: Narrow vertical razor-blade drone
        draw_top_thruster(im, cx, 44, 112, 58)
        fin_r = [(cx + 42, 145), (cx + 128, 205), (cx + 112, 345), (cx + 38, 395)]
        draw_sym(im, fin_r, cx, VIOL_BASE, VIOL_SHADE, VIOL_LIGHT, outline_w=7)
        blade = [(cx, 474), (cx + 68, 335), (cx + 56, 98), (cx - 56, 98), (cx - 68, 335)]
        draw_cel_poly(im, blade, cb, cs, cl, outline_w=8)
        draw_menace_eye(im, cx, 245, 30, 56, ring_c=AMBR_BASE, core_c=TOXIC_LIME)

    elif variant == "dread_carrier":
        # AP-0053: Elongated heavy gunship carrier
        draw_top_thruster(im, cx - 68, 42, 108, 54)
        draw_top_thruster(im, cx + 68, 42, 108, 54)
        spon_r = [(cx + 76, 125), (cx + 182, 165), (cx + 176, 385), (cx + 95, 435), (cx + 72, 395)]
        draw_sym(im, spon_r, cx, cb, cs, cl, outline_w=8)
        hull = [(cx, 468), (cx + 88, 395), (cx + 92, 92), (cx - 92, 92), (cx - 88, 395)]
        draw_cel_poly(im, hull, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        bay = [(cx - 42, 145), (cx + 42, 145), (cx + 48, 365), (cx - 48, 365)]
        draw_cel_poly(im, bay, CRIM_BASE, CRIM_SHADE, CRIM_LIGHT, outline_w=6)
        draw_menace_eye(im, cx, 265, 36, 36)

    elif variant == "spire_frigate":
        # AP-0054: Armored gothic-neon spire frigate
        draw_top_thruster(im, cx, 46, 114, 72)
        wing_r = [(cx + 52, 165), (cx + 172, 235), (cx + 148, 355), (cx + 56, 335)]
        draw_sym(im, wing_r, cx, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=7)
        spire = [(cx, 472), (cx + 82, 325), (cx + 68, 102), (cx - 68, 102), (cx - 82, 325)]
        draw_cel_poly(im, spire, cb, cs, cl, outline_w=8)
        chev = [(cx, 435), (cx + 54, 315), (cx, 345), (cx - 54, 315)]
        draw_cel_poly(im, chev, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT, outline_w=5)
        draw_menace_eye(im, cx, 215, 36, 42)

    elif variant == "centurion_mk1":
        # AP-0055 (CB-001): Frontline Centurion saucer-claw fighter
        draw_down_fang(im, cx - 95, 325, 458, 52, cb, cs, cl)
        draw_down_fang(im, cx + 95, 325, 458, 52, cb, cs, cl)
        disc = [(cx + math.cos(a) * 196, 235 + math.sin(a) * 128) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        draw_cel_poly(im, disc, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        armor_r = [(cx + 28, 118), (cx + 182, 185), (cx + 165, 315), (cx + 35, 345)]
        draw_sym(im, armor_r, cx, cb, cs, cl, outline_w=6)
        draw_menace_eye(im, cx, 242, 48, 48)

    elif variant == "centurion_turret":
        # AP-0056 (CB-004): Quad-barrel octagonal gun platform
        for ang_d in (65, 115):
            rad = math.radians(ang_d)
            bx = cx + math.cos(rad) * 120
            draw_down_fang(im, bx, 335, 466, 48, CRIM_BASE, CRIM_SHADE, CRIM_LIGHT)
        oct_pts = [(cx + math.cos(a + math.pi / 8) * 176, 235 + math.sin(a + math.pi / 8) * 162) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        draw_cel_poly(im, oct_pts, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        in_pts = [(cx + math.cos(a + math.pi / 8) * 122, 235 + math.sin(a + math.pi / 8) * 112) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        draw_cel_poly(im, in_pts, cb, cs, cl, outline_w=6)
        draw_menace_eye(im, cx, 235, 46, 46, ring_c=CRIM_BASE, core_c=CORE_WHITE)

    elif variant == "wingpod_wide":
        # AP-0057 (CB-009a): Wide modular assault wing-unit
        for bx in (cx - 135, cx, cx + 135):
            draw_down_fang(im, bx, 305, 412, 44, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT)
        body = [(cx - 224, 185), (cx - 145, 128), (cx + 145, 128), (cx + 224, 185), (cx + 198, 332), (cx - 198, 332)]
        draw_cel_poly(im, body, cb, cs, cl, outline_w=8)
        plate = [(cx - 155, 162), (cx + 155, 162), (cx + 135, 295), (cx - 135, 295)]
        draw_cel_poly(im, plate, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=6)
        draw_menace_eye(im, cx, 228, 46, 34)

    elif variant == "wingpod_core":
        # AP-0058 (CB-009b): Compact vertical assault pod
        draw_top_thruster(im, cx, 58, 126, 68)
        draw_down_fang(im, cx, 355, 466, 72, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT)
        pod = [(cx, 98), (cx + 124, 175), (cx + 108, 365), (cx - 108, 365), (cx - 124, 175)]
        draw_cel_poly(im, pod, cb, cs, cl, outline_w=8)
        draw_menace_eye(im, cx, 245, 44, 44, ring_c=VIOL_BASE, core_c=TOXIC_LIME)

    elif variant == "cyber_disc":
        # AP-0059 (CD-series): Segmented rotary saw-saucer
        for k in range(8):
            a = k * (math.pi / 4)
            a2 = a + 0.34
            tooth = [
                (cx + math.cos(a - 0.22) * 155, cy + math.sin(a - 0.22) * 155),
                (cx + math.cos(a) * 228, cy + math.sin(a) * 228),
                (cx + math.cos(a2) * 162, cy + math.sin(a2) * 162),
            ]
            draw_cel_poly(im, tooth, CRIM_BASE, CRIM_SHADE, CRIM_LIGHT, outline_w=6)
        outer = [(cx + math.cos(a) * 168, cy + math.sin(a) * 168) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        draw_cel_poly(im, outer, cb, cs, cl, outline_w=8)
        inner = [(cx + math.cos(a) * 108, cy + math.sin(a) * 108) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
        draw_cel_poly(im, inner, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=6)
        draw_menace_eye(im, cx, cy, 48, 48)

    elif variant == "void_sentinel":
        # AP-0060 (DA-series): Four-pronged diamond void sentinel
        for ang in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            px, py = cx + math.cos(ang) * 226, cy + math.sin(ang) * 226
            perp_x, perp_y = -math.sin(ang) * 52, math.cos(ang) * 52
            bx, by = cx + math.cos(ang) * 92, cy + math.sin(ang) * 92
            prong = [(bx - perp_x, by - perp_y), (px, py), (bx + perp_x, by + perp_y)]
            draw_cel_poly(im, prong, cb, cs, cl, outline_w=7)
        dia = [(cx, cy - 138), (cx + 138, cy), (cx, cy + 138), (cx - 138, cy)]
        draw_cel_poly(im, dia, VIOL_BASE, VIOL_SHADE, VIOL_LIGHT, outline_w=8)
        draw_menace_eye(im, cx, cy, 48, 48, ring_c=AMBR_BASE, core_c=CORE_WHITE)

    elif variant == "automaton_droid":
        # AP-0061 (Droid): Mechanical security droid with articulated side claws + cyclops visor
        claw_r = [(cx + 115, 225), (cx + 212, 265), (cx + 195, 425), (cx + 135, 438), (cx + 148, 325)]
        draw_sym(im, claw_r, cx, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=7)
        dome = [(cx + math.cos(a) * 145, 235 + math.sin(a) * 142) for a in np.linspace(0, 2 * math.pi, 22, endpoint=False)]
        draw_cel_poly(im, dome, cb, cs, cl, outline_w=8)
        visor = [(cx - 105, 205), (cx + 105, 205), (cx + 92, 285), (cx - 92, 285)]
        draw_cel_poly(im, visor, OUTLINE, OUTLINE, HULL_SHADE, outline_w=6)
        draw_menace_eye(im, cx, 245, 40, 30, ring_c=CRIM_BASE, core_c=TOXIC_LIME)

    elif variant == "chrono_mine":
        # AP-0062 (Droid1_Timer): Ticking naval-style plasma countdown mine!
        for k in range(8):
            a = k * (math.pi / 4)
            sp = [
                (cx + math.cos(a - 0.16) * 148, cy + math.sin(a - 0.16) * 148),
                (cx + math.cos(a) * 224, cy + math.sin(a) * 224),
                (cx + math.cos(a + 0.16) * 148, cy + math.sin(a + 0.16) * 148),
            ]
            draw_cel_poly(im, sp, CRIM_BASE, CRIM_SHADE, CRIM_LIGHT, outline_w=6)
        orb = [(cx + math.cos(a) * 156, cy + math.sin(a) * 156) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        draw_cel_poly(im, orb, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        dial = [(cx + math.cos(a) * 104, cy + math.sin(a) * 104) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
        draw_cel_poly(im, dial, cb, cs, cl, outline_w=6)
        # Bold timer clock hands inside dial
        d = ImageDraw.Draw(im)
        d.line([(cx, cy), (cx, cy - 68)], fill=OUTLINE, width=14)
        d.line([(cx, cy), (cx + 54, cy + 24)], fill=CRIM_BASE, width=12)
        d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=CORE_WHITE, outline=OUTLINE, width=5)

    elif variant == "phantom_hex":
        # AP-0063 (E_3000x): Hexagonal stealth striker
        w_r = [(cx + 75, 145), (cx + 222, 185), (cx + 178, 395), (cx + 68, 345)]
        draw_sym(im, w_r, cx, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=7)
        hx = [(cx + math.cos(a - math.pi / 2) * 138, 255 + math.sin(a - math.pi / 2) * 165) for a in np.linspace(0, 2 * math.pi, 6, endpoint=False)]
        draw_cel_poly(im, hx, cb, cs, cl, outline_w=8)
        draw_menace_eye(im, cx, 255, 42, 42, ring_c=MAGE_BASE, core_c=CORE_YELL)

    elif variant == "reaper_scythe":
        # AP-0064 (E_3308_x): Crescent-scythe heavy attacker
        draw_top_thruster(im, cx, 52, 122, 68)
        scy_r = [(cx + 48, 128), (cx + 216, 175), (cx + 228, 345), (cx + 128, 462), (cx + 142, 315), (cx + 56, 265)]
        draw_sym(im, scy_r, cx, cb, cs, cl, outline_w=8)
        core = [(cx, 415), (cx + 76, 285), (cx + 62, 108), (cx - 62, 108), (cx - 76, 285)]
        draw_cel_poly(im, core, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        draw_menace_eye(im, cx, 235, 38, 44)

    elif variant == "juggernaut_hull":
        # AP-0065 (E_3308a): Twin-claw heavy assault hull
        draw_top_thruster(im, cx - 78, 48, 118, 58)
        draw_top_thruster(im, cx + 78, 48, 118, 58)
        claw_r = [(cx + 85, 115), (cx + 218, 155), (cx + 212, 385), (cx + 118, 466), (cx + 88, 365)]
        draw_sym(im, claw_r, cx, cb, cs, cl, outline_w=8)
        plate = [(cx - 108, 102), (cx + 108, 102), (cx + 95, 385), (cx, 435), (cx - 95, 385)]
        draw_cel_poly(im, plate, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        draw_menace_eye(im, cx, 255, 52, 42, ring_c=AMBR_BASE, core_c=TOXIC_LIME)

    elif variant == "juggernaut_core":
        # AP-0066 (E_3308b): Armored core reactor turret module
        for ang_d in (45, 135, 225, 315):
            a = math.radians(ang_d)
            lug = [
                (cx + math.cos(a - 0.28) * 135, cy + math.sin(a - 0.28) * 135),
                (cx + math.cos(a - 0.18) * 208, cy + math.sin(a - 0.18) * 208),
                (cx + math.cos(a + 0.18) * 208, cy + math.sin(a + 0.18) * 208),
                (cx + math.cos(a + 0.28) * 135, cy + math.sin(a + 0.28) * 135),
            ]
            draw_cel_poly(im, lug, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=7)
        ring = [(cx + math.cos(a) * 154, cy + math.sin(a) * 154) for a in np.linspace(0, 2 * math.pi, 22, endpoint=False)]
        draw_cel_poly(im, ring, cb, cs, cl, outline_w=8)
        draw_menace_eye(im, cx, cy, 64, 64, ring_c=CRIM_BASE, core_c=CORE_WHITE)

    elif variant == "hp_pip_bar":
        # AP-0067 (Enemy_Hp): Floating overhead Enemy HP bar widget (centered horizontal capsule)
        frame = [(52, 196), (460, 196), (478, 256), (460, 316), (52, 316), (34, 256)]
        draw_cel_poly(im, frame, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=8)
        # 4 bright crimson/amber health pips
        for k in range(4):
            x0 = 74 + k * 92
            pip = [(x0, 218), (x0 + 78, 218), (x0 + 78, 294), (x0, 294)]
            c_use = (CRIM_BASE, CRIM_SHADE, CRIM_LIGHT) if k < 3 else (AMBR_BASE, AMBR_SHADE, AMBR_LIGHT)
            draw_cel_poly(im, pip, *c_use, outline_w=5)

    elif variant == "target_drone":
        # AP-0068 (Enemytut): Tutorial bullseye target dummy drone
        wing_r = [(cx + 112, 195), (cx + 228, 165), (cx + 218, 335), (cx + 112, 315)]
        draw_sym(im, wing_r, cx, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=7)
        r1 = [(cx + math.cos(a) * 148, cy + math.sin(a) * 148) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        draw_cel_poly(im, r1, CRIM_BASE, CRIM_SHADE, CRIM_LIGHT, outline_w=8)
        r2 = [(cx + math.cos(a) * 98, cy + math.sin(a) * 98) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
        draw_cel_poly(im, r2, CORE_WHITE, AMBR_LIGHT, CORE_WHITE, outline_w=6)
        r3 = [(cx + math.cos(a) * 52, cy + math.sin(a) * 52) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
        draw_cel_poly(im, r3, cb, cs, cl, outline_w=6)

    return im


def render_ebullet(variant, pal):
    """Render 1 of 11 unmistakable high-contrast arcade Enemy Bullets at 256x256 (4x of 64)."""
    S = 256
    cx, cy = S * 0.5, S * 0.5
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cb, cs, cl = pal_tuple(pal)

    if variant == "needle_dart":
        # AP-0070: Downward plasma dart
        outer = [(cx, 232), (cx + 58, 92), (cx, 28), (cx - 58, 92)]
        draw_cel_poly(im, outer, cb, cs, cl, outline_w=8)
        core = [(cx, 196), (cx + 28, 98), (cx, 56), (cx - 28, 98)]
        draw_cel_poly(im, core, CORE_WHITE, CORE_YELL, CORE_WHITE, outline_w=4)

    elif variant == "twin_fang":
        # AP-0071: Forked twin-fang magenta bolt
        for ox in (-46, 46):
            fg = [(cx + ox, 228), (cx + ox + 36, 86), (cx + ox, 34), (cx + ox - 36, 86)]
            draw_cel_poly(im, fg, cb, cs, cl, outline_w=7)
            cr = [(cx + ox, 192), (cx + ox + 16, 94), (cx + ox, 60), (cx + ox - 16, 94)]
            draw_cel_poly(im, cr, CORE_WHITE, cl, CORE_WHITE, outline_w=3)

    elif variant == "lance_spear":
        # AP-0072: Elongated downward laser spear
        sp = [(cx, 240), (cx + 46, 156), (cx + 28, 22), (cx - 28, 22), (cx - 46, 156)]
        draw_cel_poly(im, sp, cb, cs, cl, outline_w=8)
        cr = [(cx, 212), (cx + 20, 148), (cx + 12, 42), (cx - 12, 42), (cx - 20, 148)]
        draw_cel_poly(im, cr, CORE_WHITE, CORE_YELL, CORE_WHITE, outline_w=3)

    elif variant == "beam_shard":
        # AP-0073: Solar-amber razor crystal shard
        sh = [(cx, 238), (cx + 54, 128), (cx, 18), (cx - 54, 128)]
        draw_cel_poly(im, sh, cb, cs, cl, outline_w=8)
        in_s = [(cx, 198), (cx + 24, 128), (cx, 58), (cx - 24, 128)]
        draw_cel_poly(im, in_s, CORE_WHITE, AMBR_LIGHT, CORE_WHITE, outline_w=3)

    elif variant == "nova_star":
        # AP-0074: Classic arcade 6-point glowing star-orb bullet
        pts = []
        for k in range(12):
            a = k * math.pi / 6 - math.pi / 2
            r = 108 if k % 2 == 0 else 56
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        draw_cel_poly(im, pts, cb, cs, cl, outline_w=7)
        orb = [(cx + math.cos(a) * 44, cy + math.sin(a) * 44) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
        draw_cel_poly(im, orb, CORE_WHITE, cl, CORE_WHITE, outline_w=4)

    elif variant == "hit_spark":
        # AP-0075: 8-spike impact burst
        pts = []
        for k in range(16):
            a = k * math.pi / 8
            r = 112 if k % 2 == 0 else 38
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        draw_cel_poly(im, pts, cb, cs, cl, outline_w=6)
        in_p = [(cx + math.cos(a) * 34, cy + math.sin(a) * 34) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
        draw_cel_poly(im, in_p, CORE_WHITE, CORE_YELL, CORE_WHITE, outline_w=3)

    elif variant == "energy_sword":
        # AP-0076: Blazing downward crimson energy sword projectile!
        guard = [(cx - 78, 76), (cx + 78, 76), (cx + 62, 108), (cx - 62, 108)]
        draw_cel_poly(im, guard, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT, outline_w=7)
        hilt = [(cx - 18, 22), (cx + 18, 22), (cx + 22, 80), (cx - 22, 80)]
        draw_cel_poly(im, hilt, HULL_BASE, HULL_SHADE, HULL_LIGHT, outline_w=6)
        blade = [(cx - 34, 98), (cx + 34, 98), (cx + 26, 188), (cx, 240), (cx - 26, 188)]
        draw_cel_poly(im, blade, cb, cs, cl, outline_w=7)
        core = [(cx - 14, 106), (cx + 14, 106), (cx, 214)]
        draw_cel_poly(im, core, CORE_WHITE, CORE_YELL, CORE_WHITE, outline_w=3)

    elif variant == "hazard_sign":
        # AP-0077: High-contrast arcade triangle '!' laser-lock warning sign
        tri = [(cx, 28), (228, 216), (28, 216)]
        draw_cel_poly(im, tri, AMBR_BASE, AMBR_SHADE, AMBR_LIGHT, outline_w=9)
        in_t = [(cx, 62), (198, 198), (58, 198)]
        draw_cel_poly(im, in_t, CRIM_BASE, CRIM_SHADE, CRIM_LIGHT, outline_w=6)
        bar = [(cx - 14, 96), (cx + 14, 96), (cx + 10, 156), (cx - 10, 156)]
        draw_cel_poly(im, bar, CORE_WHITE, CORE_WHITE, CORE_WHITE, outline_w=4)
        dot = [(cx + math.cos(a) * 14, 180 + math.sin(a) * 14) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        draw_cel_poly(im, dot, CORE_WHITE, CORE_WHITE, CORE_WHITE, outline_w=4)

    elif variant == "lock_chevron":
        # AP-0078: Sharp downward target-vector chevron arrow
        chev = [(42, 58), (cx, 134), (214, 58), (214, 132), (cx, 224), (42, 132)]
        draw_cel_poly(im, chev, cb, cs, cl, outline_w=8)
        in_c = [(68, 86), (cx, 148), (188, 86), (188, 124), (cx, 196), (68, 124)]
        draw_cel_poly(im, in_c, CORE_WHITE, AMBR_LIGHT, CORE_WHITE, outline_w=3)

    elif variant == "plasma_orb":
        # AP-0079: Signature arcade bullet-hell white-cored crimson orb
        r1 = [(cx + math.cos(a) * 96, cy + math.sin(a) * 96) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        draw_cel_poly(im, r1, cb, cs, cl, outline_w=8)
        r2 = [(cx + math.cos(a) * 64, cy + math.sin(a) * 64) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
        draw_cel_poly(im, r2, MAGE_LIGHT, cb, CORE_WHITE, outline_w=4)
        r3 = [(cx + math.cos(a) * 38, cy + math.sin(a) * 38) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
        draw_cel_poly(im, r3, CORE_WHITE, CORE_WHITE, CORE_WHITE, outline_w=0)

    elif variant == "ring_pulse":
        # AP-0080: Concentric violet-magenta donut ring bullet
        outer = [(cx + math.cos(a) * 102, cy + math.sin(a) * 102) for a in np.linspace(0, 2 * math.pi, 26, endpoint=False)]
        inner = [(cx + math.cos(a) * 52, cy + math.sin(a) * 52) for a in np.linspace(0, 2 * math.pi, 22, endpoint=False)]
        ring_poly = outer + list(reversed(inner))
        draw_cel_poly(im, ring_poly, cb, cs, cl, outline_w=7)
        mid_o = [(cx + math.cos(a) * 84, cy + math.sin(a) * 84) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        mid_i = [(cx + math.cos(a) * 68, cy + math.sin(a) * 68) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        draw_cel_poly(im, mid_o + list(reversed(mid_i)), CORE_WHITE, MAGE_LIGHT, CORE_WHITE, outline_w=0)

    return im


def measure_rgba(im):
    arr = np.asarray(im, dtype=np.float32)
    a = arr[:, :, 3]
    fg = a > 16
    if not np.any(fg):
        return 0.0, 0.0, 0.0
    rgb = arr[fg][:, :3] / 255.0
    mx = rgb.max(axis=1)
    mn = rgb.min(axis=1)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0.0)
    return round(float(mx.mean()), 3), round(float(sat.mean()), 3), round(float(fg.mean()), 3)


def main():
    records = []

    # 1. 23 E-BODY units
    for idx, (row_id, base, variant, pal, recipe) in enumerate(E_BODY_SPECS, 1):
        c4 = render_ebody(idx, variant, pal)
        m_im = downsample_straight_rgba(c4, (256, 256))
        s_im = downsample_straight_rgba(c4, (128, 128))
        fname = f"enemy_body_{idx:02d}_{variant}_128@{pal}.png"
        m_rel = f"masters/bodies/{fname}"
        s_rel = f"sprites/bodies/{fname}"
        os.makedirs(os.path.join(HERE, "masters/bodies"), exist_ok=True)
        os.makedirs(os.path.join(HERE, "sprites/bodies"), exist_ok=True)
        m_im.save(os.path.join(HERE, m_rel), "PNG", compress_level=9)
        s_im.save(os.path.join(HERE, s_rel), "PNG", compress_level=9)
        sa = np.asarray(s_im)
        assert sa[0, 0, 3] == 0 and sa[0, -1, 3] == 0 and sa[-1, 0, 3] == 0 and sa[-1, -1, 3] == 0
        val, ch, fill = measure_rgba(s_im)
        records.append({
            "row_id": row_id, "batch": "E-BODY", "unit_no": idx, "planner_base": base,
            "variant": variant, "delivered_px": "128x128", "master_px": "256x256",
            "source": m_rel, "file": s_rel, "license": LICENSE_NOTE,
            "author": AUTHOR_BRANCH, "recipe": recipe, "val": val, "chroma": ch, "fill": fill,
        })

    # 2. 11 E-BULLET units
    for idx, (row_id, base, variant, pal, recipe) in enumerate(E_BULLET_SPECS, 1):
        c4 = render_ebullet(variant, pal)
        m_im = downsample_straight_rgba(c4, (128, 128))
        s_im = downsample_straight_rgba(c4, (64, 64))
        fname = f"enemy_bullet_{idx:02d}_{variant}_64@{pal}.png"
        m_rel = f"masters/bullets/{fname}"
        s_rel = f"sprites/bullets/{fname}"
        os.makedirs(os.path.join(HERE, "masters/bullets"), exist_ok=True)
        os.makedirs(os.path.join(HERE, "sprites/bullets"), exist_ok=True)
        m_im.save(os.path.join(HERE, m_rel), "PNG", compress_level=9)
        s_im.save(os.path.join(HERE, s_rel), "PNG", compress_level=9)
        sa = np.asarray(s_im)
        assert sa[0, 0, 3] == 0 and sa[0, -1, 3] == 0 and sa[-1, 0, 3] == 0 and sa[-1, -1, 3] == 0
        val, ch, fill = measure_rgba(s_im)
        records.append({
            "row_id": row_id, "batch": "E-BULLET", "unit_no": idx, "planner_base": base,
            "variant": variant, "delivered_px": "64x64", "master_px": "128x128",
            "source": m_rel, "file": s_rel, "license": LICENSE_NOTE,
            "author": AUTHOR_BRANCH, "recipe": recipe, "val": val, "chroma": ch, "fill": fill,
        })

    with open(os.path.join(HERE, "w2b_units.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "w2b_units.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    print(f"SUCCESS: {len(records)} W2 ENEMY units exported (masters/ + sprites/)")


if __name__ == "__main__":
    main()
