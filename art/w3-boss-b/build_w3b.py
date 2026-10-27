#!/usr/bin/env python3
"""
Build Wave W3 — BOSS Lane (42 units) for Variant B ("Solar Neon Arcade-Pop").
Author branch: arena/eca8588b-windwings-space-shooter-game-p

Exact 42 units per art-planner.csv:
  - B-BODY (AP-0117..AP-0120, 35 units): 512x512 RGBA + 512x512 masters/ (rendered at 2x = 1024x1024)
      * Every B-BODY has intentional combat asymmetry + >= 1 visually separated destructible glowing module!
  - B-PART (AP-0122..AP-0128,  7 units): 256x256 RGBA + 512x512 masters/ (rendered at 2x = 1024x1024)
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

OUTLINE    = (20, 6, 46, 255)

PALETTES = {
    "crimson": {
        "pri": ((255, 28, 84, 255),  (162, 8, 48, 255),  (255, 118, 148, 255)),
        "sec": ((74, 52, 132, 255),  (38, 24, 78, 255),  (128, 104, 192, 255)),
        "acc": ((255, 196, 12, 255), (196, 108, 0, 255), (255, 244, 136, 255)),
        "glow": (255, 238, 36, 255),
    },
    "violet": {
        "pri": ((132, 46, 212, 255), (68, 18, 128, 255), (196, 128, 255, 255)),
        "sec": ((52, 68, 148, 255),  (26, 36, 92, 255),  (108, 132, 218, 255)),
        "acc": ((255, 42, 156, 255), (168, 12, 96, 255), (255, 142, 212, 255)),
        "glow": (0, 238, 255, 255),
    },
    "emerald": {
        "pri": ((0, 218, 142, 255),  (0, 128, 82, 255),  (124, 255, 204, 255)),
        "sec": ((64, 48, 124, 255),  (34, 22, 74, 255),  (118, 98, 182, 255)),
        "acc": ((255, 196, 12, 255), (192, 104, 0, 255), (255, 242, 128, 255)),
        "glow": (186, 255, 36, 255),
    },
    "magenta": {
        "pri": ((255, 34, 148, 255), (162, 10, 88, 255), (255, 136, 208, 255)),
        "sec": ((62, 44, 128, 255),  (32, 20, 76, 255),  (118, 96, 188, 255)),
        "acc": ((0, 222, 255, 255),  (0, 136, 188, 255), (142, 252, 255, 255)),
        "glow": (255, 238, 52, 255),
    },
    "amber": {
        "pri": ((255, 168, 12, 255), (188, 92, 0, 255),  (255, 232, 118, 255)),
        "sec": ((82, 46, 128, 255),  (42, 20, 76, 255),  (138, 96, 188, 255)),
        "acc": ((255, 32, 92, 255),  (168, 8, 52, 255),  (255, 118, 152, 255)),
        "glow": (0, 242, 255, 255),
    },
}

CORE_WHITE = (255, 253, 238, 255)

# Exact 32 glyph boss IDs per ART_REDRAW_PLAN §1.3 (7001..7018 minus 7007/7008 = 16; 9002..9018 minus 9016 = 16 -> 32)
GLYPH_IDS = (
    [7001, 7002, 7003, 7004, 7005, 7006, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017, 7018]
    + [9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9017, 9018]
)
ARCHETYPES = ["citadel", "arachnid", "leviathan", "chronos", "seraph", "kraken", "scorpion", "colossus"]
PAL_KEYS = ["crimson", "violet", "emerald", "magenta", "amber"]


def downsample_straight_rgba(im, target_size):
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
    arr[arr[:, :, 3] < 4] = 0
    for cy in (0, target_size[1] - 1):
        for cx in (0, target_size[0] - 1):
            arr[cy, cx] = [0, 0, 0, 0]
    return Image.fromarray(arr, "RGBA")


def draw_cel_poly(canvas, pts, col_triple, outline_w=7):
    """Fast local-bbox 3-tone 30-deg top-left cel-shaded polygon so 1024x1024 bosses render in <0.1s each."""
    if len(pts) < 3:
        return
    base_c, shade_c, light_c = col_triple
    W, H = canvas.size
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = int(outline_w + 12)
    x0 = max(0, int(math.floor(min(xs))) - pad)
    y0 = max(0, int(math.floor(min(ys))) - pad)
    x1 = min(W, int(math.ceil(max(xs))) + pad)
    y1 = min(H, int(math.ceil(max(ys))) + pad)
    bw, bh = x1 - x0, y1 - y0
    if bw <= 2 or bh <= 2:
        return

    lpts = [(x - x0, y - y0) for (x, y) in pts]
    cx = sum(p[0] for p in lpts) / len(lpts)
    cy = sum(p[1] for p in lpts) / len(lpts)
    span = max(max(p[0] for p in lpts) - min(p[0] for p in lpts), max(p[1] for p in lpts) - min(p[1] for p in lpts), 1.0)

    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).polygon(lpts, fill=255)
    m_arr = np.asarray(mask)

    layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(lpts, fill=base_c)

    if shade_c is not None:
        inv = Image.new("L", (bw, bh), 255)
        ImageDraw.Draw(inv).polygon([(x - span * 0.11, y - span * 0.13) for (x, y) in lpts], fill=0)
        sh = np.zeros((bh, bw, 4), dtype=np.uint8)
        sh[:, :] = shade_c
        sh[:, :, 3] = np.minimum(m_arr, np.asarray(inv))
        layer = Image.alpha_composite(layer, Image.fromarray(sh, "RGBA"))

    if light_c is not None:
        hi = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        hi_pts = [(cx + (x - cx) * 0.68 - span * 0.08, cy + (y - cy) * 0.68 - span * 0.09) for (x, y) in lpts]
        ImageDraw.Draw(hi).polygon(hi_pts, fill=light_c)
        hi_arr = np.asarray(hi).copy()
        hi_arr[:, :, 3] = np.minimum(hi_arr[:, :, 3], m_arr)
        layer = Image.alpha_composite(layer, Image.fromarray(hi_arr, "RGBA"))

    if outline_w > 0:
        od = ImageDraw.Draw(layer)
        od.line(lpts + [lpts[0]], fill=OUTLINE, width=outline_w, joint="curve")
        r = outline_w * 0.45
        for px, py in lpts:
            od.ellipse([px - r, py - r, px + r, py + r], fill=OUTLINE)

    canvas.alpha_composite(layer, (x0, y0))


def reg_poly(cx, cy, rx, ry, n=16, rot=0.0):
    return [(cx + math.cos(a + rot) * rx, cy + math.sin(a + rot) * ry) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def draw_boss_core(canvas, cx, cy, rx, ry, acc_triple, glow_c, outline_w=8):
    draw_cel_poly(canvas, reg_poly(cx, cy, rx * 1.34, ry * 1.34, 18), acc_triple, outline_w=outline_w)
    glow_triple = (glow_c, acc_triple[0], CORE_WHITE)
    draw_cel_poly(canvas, reg_poly(cx, cy, rx, ry, 18), glow_triple, outline_w=outline_w - 1)
    d = ImageDraw.Draw(canvas)
    d.ellipse([cx - rx * 0.48, cy - ry * 0.52, cx - rx * 0.06, cy - ry * 0.10], fill=CORE_WHITE)


def draw_destructible_satellite(canvas, x, y, anchor_x, anchor_y, kind, P):
    """Visually separated destructible module linked by neon energy tether (mandatory Boss Gate!)."""
    d = ImageDraw.Draw(canvas)
    # Energy arc tether with gap so module reads as a separate destructible sub-target!
    d.line([(anchor_x, anchor_y), (x, y)], fill=OUTLINE, width=16)
    d.line([(anchor_x, anchor_y), (x, y)], fill=P["glow"], width=7)

    if kind == 0:
        # Detached Heavy Plasma Cannon Pod
        brl = [(x - 24, y + 40), (x + 24, y + 40), (x + 16, y + 148), (x - 16, y + 148)]
        draw_cel_poly(canvas, brl, P["acc"], outline_w=7)
        pod = reg_poly(x, y, 72, 68, 8, rot=math.pi / 8)
        draw_cel_poly(canvas, pod, P["pri"], outline_w=8)
        draw_boss_core(canvas, x, y, 30, 30, P["acc"], P["glow"], outline_w=6)
    elif kind == 1:
        # Detached Shield-Barrier Generator Orb
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            fin = [
                (x + math.cos(a - 0.25) * 52, y + math.sin(a - 0.25) * 52),
                (x + math.cos(a) * 96, y + math.sin(a) * 96),
                (x + math.cos(a + 0.25) * 52, y + math.sin(a + 0.25) * 52),
            ]
            draw_cel_poly(canvas, fin, P["acc"], outline_w=6)
        draw_cel_poly(canvas, reg_poly(x, y, 62, 62, 18), P["sec"], outline_w=8)
        draw_boss_core(canvas, x, y, 32, 32, P["pri"], P["glow"], outline_w=6)
    elif kind == 2:
        # Detached Rotary Buzzsaw Sub-Unit
        teeth = []
        for k in range(16):
            a = k * math.pi / 8
            r = 92 if k % 2 == 0 else 58
            teeth.append((x + math.cos(a) * r, y + math.sin(a) * r))
        draw_cel_poly(canvas, teeth, P["acc"], outline_w=7)
        draw_boss_core(canvas, x, y, 30, 30, P["pri"], P["glow"], outline_w=6)
    else:
        # Detached Missile Silo Battery
        box = [(x - 68, y - 58), (x + 68, y - 58), (x + 76, y + 66), (x - 76, y + 66)]
        draw_cel_poly(canvas, box, P["sec"], outline_w=8)
        for mx in (x - 34, x + 34):
            for my in (y - 22, y + 26):
                draw_cel_poly(canvas, reg_poly(mx, my, 18, 18, 12), P["acc"], outline_w=5)


def draw_asym_right_arm(canvas, cx, cy, arm_kind, P):
    """Heavy asymmetric right-side boss weapon arm so left != right on every single boss!"""
    if arm_kind == 0:
        # Giant Siege Railgun Arm extending down-right
        arm = [(cx + 145, cy - 85), (cx + 395, cy - 25), (cx + 415, cy + 285), (cx + 315, cy + 325), (cx + 255, cy + 95), (cx + 145, cy + 65)]
        draw_cel_poly(canvas, arm, P["sec"], outline_w=9)
        muzzle = [(cx + 322, cy + 265), (cx + 408, cy + 255), (cx + 382, cy + 418), (cx + 336, cy + 418)]
        draw_cel_poly(canvas, muzzle, P["acc"], outline_w=8)
    elif arm_kind == 1:
        # Articulated Crusher Pincer Claw on starboard side
        upper = [(cx + 150, cy - 60), (cx + 425, cy + 15), (cx + 448, cy + 215), (cx + 335, cy + 365), (cx + 312, cy + 205), (cx + 155, cy + 80)]
        draw_cel_poly(canvas, upper, P["pri"], outline_w=9)
        jaw = [(cx + 275, cy + 195), (cx + 332, cy + 358), (cx + 228, cy + 325)]
        draw_cel_poly(canvas, jaw, P["acc"], outline_w=8)
    elif arm_kind == 2:
        # Curved Aegis Shield-Blade Wing on starboard side
        blade = [(cx + 140, cy - 165), (cx + 445, cy - 95), (cx + 462, cy + 195), (cx + 295, cy + 385), (cx + 255, cy + 215), (cx + 145, cy + 55)]
        draw_cel_poly(canvas, blade, P["acc"], outline_w=9)
        in_b = [(cx + 205, cy - 95), (cx + 405, cy - 45), (cx + 412, cy + 165), (cx + 295, cy + 285)]
        draw_cel_poly(canvas, in_b, P["pri"], outline_w=6)
    else:
        # Triple-Barrel Gatling Broadside Pod on starboard side
        pod = [(cx + 155, cy - 95), (cx + 415, cy - 55), (cx + 425, cy + 165), (cx + 165, cy + 145)]
        draw_cel_poly(canvas, pod, P["sec"], outline_w=9)
        for k in range(3):
            bx = cx + 215 + k * 72
            brl = [(bx - 20, cy + 145), (bx + 20, cy + 145), (bx + 16, cy + 355 + k * 18), (bx - 16, cy + 355 + k * 18)]
            draw_cel_poly(canvas, brl, P["acc"], outline_w=7)


def render_boss_body(archetype, phase_cfg, pal_key):
    """Render 1 of 35 asymmetric 1024x1024 (2x of 512x512) Solar Neon Arcade-Pop Bosses."""
    S = 1024
    cx, cy = 512, 470
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    P = PALETTES[pal_key]

    # 1. Left-side separated destructible module (port side) + Right-side asymmetric weapon arm (starboard side)
    sat_x = 152 + (phase_cfg % 2) * 24
    sat_y = 635 - (phase_cfg // 2) * 95
    draw_destructible_satellite(im, sat_x, sat_y, cx - 155, cy + 35, phase_cfg, P)
    if phase_cfg in (2, 3):
        # Bonus upper-left destructible capacitor node on higher-tier bosses!
        draw_destructible_satellite(im, 168, 225, cx - 140, cy - 135, (phase_cfg + 1) % 4, P)

    draw_asym_right_arm(im, cx, cy, (phase_cfg + ARCHETYPES.index(archetype) if archetype in ARCHETYPES else phase_cfg) % 4, P)

    # 2. Top thrusters
    for tx in (cx - 115, cx, cx + 115):
        th = [(tx - 42, 72), (tx + 42, 72), (tx + 32, 165), (tx - 32, 165)]
        draw_cel_poly(im, th, P["acc"], outline_w=8)

    # 3. Archetype-specific main dreadnought chassis (port wing + central armored hull + menace core)
    if archetype == "emblem_s":
        # AP-0117 BossS: S-Crest Sovereign Dreadnought
        port_w = [(cx - 125, cy - 155), (86, cy - 85), (112, cy + 95), (cx - 135, cy + 125)]
        draw_cel_poly(im, port_w, P["pri"], outline_w=9)
        hull = [(cx, 855), (cx + 215, 625), (cx + 195, 165), (cx - 195, 165), (cx - 215, 625)]
        draw_cel_poly(im, hull, P["sec"], outline_w=10)
        plate = [(cx, 785), (cx + 148, 565), (cx + 128, 215), (cx - 128, 215), (cx - 148, 565)]
        draw_cel_poly(im, plate, P["pri"], outline_w=8)
        draw_boss_core(im, cx, cy - 10, 78, 92, P["acc"], P["glow"], outline_w=9)

    elif archetype == "overlord_x":
        # AP-0118 BossX: X-Winged Nova Overlord
        for sx, sy in [(-1, -1), (1, -1), (-1, 1)]:
            xw = [(cx + sx * 85, cy + sy * 65), (cx + sx * 415, cy + sy * 295), (cx + sx * 335, cy + sy * 355), (cx + sx * 55, cy + sy * 135)]
            draw_cel_poly(im, xw, P["pri"], outline_w=9)
        hull = reg_poly(cx, cy, 195, 235, 8, rot=math.pi / 8)
        draw_cel_poly(im, hull, P["sec"], outline_w=10)
        draw_boss_core(im, cx, cy, 86, 86, P["acc"], P["glow"], outline_w=9)

    elif archetype == "aegis_bastion":
        # AP-0119 Boss_Shields: Segmented Phalanx Barrier Carrier
        for k in range(3):
            a0 = math.pi * (0.18 + k * 0.24)
            a1 = a0 + 0.19
            sh = [
                (cx + math.cos(a0) * 385, cy + 60 + math.sin(a0) * 355),
                (cx + math.cos(a1) * 385, cy + 60 + math.sin(a1) * 355),
                (cx + math.cos(a1) * 315, cy + 60 + math.sin(a1) * 285),
                (cx + math.cos(a0) * 315, cy + 60 + math.sin(a0) * 285),
            ]
            draw_cel_poly(im, sh, P["acc"], outline_w=8)
        hull = [(cx - 265, cy - 185), (cx + 235, cy - 185), (cx + 265, cy + 145), (cx, cy + 285), (cx - 285, cy + 145)]
        draw_cel_poly(im, hull, P["pri"], outline_w=10)
        draw_boss_core(im, cx - 15, cy - 10, 92, 68, P["sec"], P["glow"], outline_w=9)

    elif archetype == "citadel":
        port_spon = [(cx - 145, cy - 195), (92, cy - 135), (84, cy + 115), (cx - 155, cy + 175)]
        draw_cel_poly(im, port_spon, P["sec"], outline_w=9)
        hull = [(cx - 195, 145), (cx + 195, 145), (cx + 225, 595), (cx, 835), (cx - 225, 595)]
        draw_cel_poly(im, hull, P["pri"], outline_w=10)
        for bx in (cx - 95, cx + 95):
            tur = [(bx - 28, 695), (bx + 28, 695), (bx + 18, 885), (bx - 18, 885)]
            draw_cel_poly(im, tur, P["acc"], outline_w=7)
        draw_boss_core(im, cx, cy, 82, 82, P["acc"], P["glow"], outline_w=9)

    elif archetype == "arachnid":
        # 3 articulated cyber-spider legs on port + 2 upper legs on starboard
        for k, ly in enumerate([-145, -15, 115]):
            leg = [(cx - 135, cy + ly), (72, cy + ly - 65), (48, cy + ly + 95 + k * 25), (108, cy + ly + 85 + k * 25), (125, cy + ly - 10), (cx - 135, cy + ly + 48)]
            draw_cel_poly(im, leg, P["acc"], outline_w=8)
        abdomen = reg_poly(cx - 24, 245, 185, 145, 16)
        draw_cel_poly(im, abdomen, P["sec"], outline_w=9)
        ceph = [(cx, 815), (cx + 185, 595), (cx + 165, 315), (cx - 165, 315), (cx - 185, 595)]
        draw_cel_poly(im, ceph, P["pri"], outline_w=10)
        # Cluster of 3 spider eyes!
        draw_boss_core(im, cx, 505, 68, 68, P["acc"], P["glow"], outline_w=8)
        draw_boss_core(im, cx - 95, 595, 34, 34, P["acc"], P["glow"], outline_w=6)
        draw_boss_core(im, cx + 95, 595, 34, 34, P["acc"], P["glow"], outline_w=6)

    elif archetype == "leviathan":
        # Wide Manta-Wing Sky Leviathan
        manta_l = [(cx - 95, 215), (42, 345), (68, 565), (cx - 125, 485)]
        draw_cel_poly(im, manta_l, P["pri"], outline_w=9)
        spine = [(cx, 895), (cx + 175, 565), (cx + 145, 155), (cx - 145, 155), (cx - 175, 565)]
        draw_cel_poly(im, spine, P["sec"], outline_w=10)
        armor = [(cx, 795), (cx + 118, 525), (cx + 95, 215), (cx - 95, 215), (cx - 118, 525)]
        draw_cel_poly(im, armor, P["pri"], outline_w=8)
        draw_boss_core(im, cx, 445, 88, 62, P["acc"], P["glow"], outline_w=9)

    elif archetype == "chronos":
        # Clockwork Gear-Fortress Dreadnought
        teeth = []
        for k in range(20):
            a = k * math.pi / 10
            r = 285 if k % 2 == 0 else 225
            teeth.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        draw_cel_poly(im, teeth, P["acc"], outline_w=9)
        dial = reg_poly(cx, cy, 198, 198, 22)
        draw_cel_poly(im, dial, P["sec"], outline_w=9)
        in_d = reg_poly(cx, cy, 138, 138, 20)
        draw_cel_poly(im, in_d, P["pri"], outline_w=7)
        # Asymmetric pendulum lance pointing down-left
        pend = [(cx - 32, cy + 95), (cx + 32, cy + 95), (cx - 45, 895), (cx - 105, 845)]
        draw_cel_poly(im, pend, P["acc"], outline_w=8)
        draw_boss_core(im, cx, cy, 66, 66, P["acc"], P["glow"], outline_w=8)

    elif archetype == "seraph":
        # Swept Solar-Blade Valkyrie Mecha
        for k in range(3):
            wy = 205 + k * 125
            wing = [(cx - 95, wy), (38 + k * 22, wy - 85), (62 + k * 22, wy + 45), (cx - 105, wy + 75)]
            draw_cel_poly(im, wing, P["acc"] if k % 2 == 0 else P["pri"], outline_w=8)
        torso = [(cx, 865), (cx + 165, 585), (cx + 185, 225), (cx, 135), (cx - 185, 225), (cx - 165, 585)]
        draw_cel_poly(im, torso, P["pri"], outline_w=10)
        crest = [(cx, 795), (cx + 92, 515), (cx, 225), (cx - 92, 515)]
        draw_cel_poly(im, crest, P["sec"], outline_w=8)
        draw_boss_core(im, cx, 465, 68, 96, P["acc"], P["glow"], outline_w=8)

    elif archetype == "kraken":
        # Bio-Cyber Squid Titan with curved tentacle whips
        for k, tx_end in enumerate([95, 215, 345]):
            tent = [(cx - 145 + k * 95, 625), (cx - 95 + k * 95, 625), (tx_end + 55, 915 - k * 25), (tx_end, 895 - k * 25)]
            draw_cel_poly(im, tent, P["acc"], outline_w=8)
        mantle = [(cx, 112), (cx + 235, 345), (cx + 185, 655), (cx - 185, 655), (cx - 235, 345)]
        draw_cel_poly(im, mantle, P["pri"], outline_w=10)
        plate = reg_poly(cx, 445, 145, 165, 14)
        draw_cel_poly(im, plate, P["sec"], outline_w=8)
        draw_boss_core(im, cx, 465, 84, 72, P["acc"], P["glow"], outline_w=9)

    elif archetype == "scorpion":
        # Heavy Pincer-Tail Warship with arching asymmetric overhead scorpion tail!
        tail = [(cx - 65, 165), (cx - 245, 88), (cx - 355, 215), (cx - 285, 335), (cx - 225, 245), (cx - 185, 168), (cx - 45, 225)]
        draw_cel_poly(im, tail, P["acc"], outline_w=9)
        hull = [(cx - 195, 205), (cx + 195, 205), (cx + 215, 635), (cx, 785), (cx - 215, 635)]
        draw_cel_poly(im, hull, P["sec"], outline_w=10)
        carapace = [(cx - 135, 255), (cx + 135, 255), (cx + 145, 615), (cx, 725), (cx - 145, 615)]
        draw_cel_poly(im, carapace, P["pri"], outline_w=8)
        draw_boss_core(im, cx, 485, 76, 76, P["acc"], P["glow"], outline_w=8)

    else:  # colossus
        # Combiner Mecha Dreadnought Torso with horned crown + chest reactor
        sh_l = [(cx - 135, 215), (56, 155), (78, 415), (cx - 155, 435)]
        draw_cel_poly(im, sh_l, P["acc"], outline_w=9)
        torso = [(cx - 195, 215), (cx + 195, 215), (cx + 165, 745), (cx, 845), (cx - 165, 745)]
        draw_cel_poly(im, torso, P["pri"], outline_w=10)
        head = [(cx, 108), (cx + 125, 185), (cx + 92, 315), (cx - 92, 315), (cx - 125, 185)]
        draw_cel_poly(im, head, P["sec"], outline_w=9)
        horn_l = [(cx - 75, 165), (cx - 185, 68), (cx - 125, 215)]
        horn_r = [(cx + 75, 165), (cx + 215, 52), (cx + 135, 215)]
        draw_cel_poly(im, horn_l, P["acc"], outline_w=7)
        draw_cel_poly(im, horn_r, P["acc"], outline_w=7)
        draw_boss_core(im, cx, 505, 92, 82, P["acc"], P["glow"], outline_w=9)

    return im


def render_boss_part(idx, variant, pal_key):
    """Render 1 of 7 modular 1024x1024 Boss Parts (masters 512x512, sprites 256x256)."""
    S = 1024
    cx, cy = 512, 512
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    P = PALETTES[pal_key]

    if variant == "command_head":
        horn_l = [(cx - 145, 295), (112, 118), (195, 415)]
        horn_r = [(cx + 145, 295), (912, 118), (829, 415)]
        draw_cel_poly(im, horn_l, P["acc"], outline_w=10)
        draw_cel_poly(im, horn_r, P["acc"], outline_w=10)
        helm = [(cx, 885), (795, 615), (745, 215), (279, 215), (229, 615)]
        draw_cel_poly(im, helm, P["pri"], outline_w=12)
        visor = [(315, 455), (709, 455), (665, 595), (359, 595)]
        draw_cel_poly(im, visor, P["sec"], outline_w=9)
        draw_boss_core(im, cx, 525, 86, 56, P["acc"], P["glow"], outline_w=9)

    elif variant == "chrono_gear_turret":
        teeth = []
        for k in range(16):
            a = k * math.pi / 8
            r = 415 if k % 2 == 0 else 318
            teeth.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        draw_cel_poly(im, teeth, P["pri"], outline_w=11)
        draw_cel_poly(im, reg_poly(cx, cy, 245, 245, 20), P["sec"], outline_w=10)
        brl = [(cx - 62, cy + 120), (cx + 62, cy + 120), (cx + 46, 935), (cx - 46, 935)]
        draw_cel_poly(im, brl, P["acc"], outline_w=10)
        draw_boss_core(im, cx, cy, 98, 98, P["acc"], P["glow"], outline_w=9)

    elif variant == "venom_fang_pod":
        fang_l = [(285, 545), (415, 545), (325, 915), (215, 765)]
        fang_r = [(609, 545), (739, 545), (809, 765), (699, 915)]
        draw_cel_poly(im, fang_l, P["acc"], outline_w=10)
        draw_cel_poly(im, fang_r, P["acc"], outline_w=10)
        sac = reg_poly(cx, 435, 315, 285, 18)
        draw_cel_poly(im, sac, P["pri"], outline_w=12)
        draw_boss_core(im, cx, 445, 112, 92, P["sec"], P["glow"], outline_w=10)

    elif variant == "broadside_railgun":
        mount = [(215, 128), (809, 128), (855, 565), (169, 565)]
        draw_cel_poly(im, mount, P["sec"], outline_w=12)
        for bx in (355, 669):
            brl = [(bx - 68, 525), (bx + 68, 525), (bx + 52, 925), (bx - 52, 925)]
            draw_cel_poly(im, brl, P["pri"], outline_w=10)
        draw_boss_core(im, cx, 355, 105, 85, P["acc"], P["glow"], outline_w=10)

    elif variant == "rotary_saw_ring":
        blades = []
        for k in range(24):
            a = k * math.pi / 12
            r = 435 if k % 2 == 0 else 285
            blades.append((cx + math.cos(a + (0.14 if k % 2 == 0 else 0)) * r, cy + math.sin(a + (0.14 if k % 2 == 0 else 0)) * r))
        draw_cel_poly(im, blades, P["pri"], outline_w=10)
        draw_cel_poly(im, reg_poly(cx, cy, 225, 225, 20), P["sec"], outline_w=10)
        draw_boss_core(im, cx, cy, 96, 96, P["acc"], P["glow"], outline_w=9)

    elif variant == "combiner_claw_arm":
        shld = [(285, 96), (765, 145), (795, 465), (255, 435)]
        draw_cel_poly(im, shld, P["pri"], outline_w=12)
        fore = [(335, 415), (715, 435), (755, 695), (295, 695)]
        draw_cel_poly(im, fore, P["sec"], outline_w=11)
        claw_l = [(285, 675), (445, 675), (395, 928), (225, 825)]
        claw_r = [(585, 675), (745, 675), (805, 825), (635, 928)]
        draw_cel_poly(im, claw_l, P["acc"], outline_w=10)
        draw_cel_poly(im, claw_r, P["acc"], outline_w=10)
        draw_boss_core(im, cx + 10, 555, 78, 68, P["acc"], P["glow"], outline_w=9)

    else:  # energy_snare_web
        d = ImageDraw.Draw(im)
        # Bold cel-outlined octagonal neon-plasma snare web!
        for rad in (165, 285, 405):
            pts = reg_poly(cx, cy, rad, rad, 8)
            d.line(pts + [pts[0]], fill=OUTLINE, width=26, joint="curve")
            d.line(pts + [pts[0]], fill=P["pri"][0], width=12, joint="curve")
        for k in range(8):
            a = k * math.pi / 4
            px, py = cx + math.cos(a) * 435, cy + math.sin(a) * 435
            d.line([(cx, cy), (px, py)], fill=OUTLINE, width=24)
            d.line([(cx, cy), (px, py)], fill=P["glow"], width=10)
            draw_cel_poly(im, reg_poly(px, py, 34, 34, 8), P["acc"], outline_w=7)
        draw_boss_core(im, cx, cy, 82, 82, P["acc"], P["glow"], outline_w=9)

    return im


def measure_rgba(im):
    arr = np.asarray(im, dtype=np.float32)
    fg = arr[:, :, 3] > 16
    rgb = arr[fg][:, :3] / 255.0
    mx = rgb.max(axis=1)
    mn = rgb.min(axis=1)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0.0)
    return round(float(mx.mean()), 3), round(float(sat.mean()), 3), round(float(fg.mean()), 3)


def main():
    records = []
    os.makedirs(os.path.join(HERE, "masters/bodies"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "sprites/bodies"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "masters/parts"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "sprites/parts"), exist_ok=True)

    # 1. Named B-BODY rows AP-0117..0119 (3 units) + 32 Glyph Bosses AP-0120 = 35 B-BODY units
    body_jobs = [
        ("AP-0117", "bosss",        "emblem_s",      0, "crimson", "boss_body_01_sovereign_s_512@crimson.png"),
        ("AP-0118", "bossx",        "overlord_x",    1, "magenta", "boss_body_02_overlord_x_512@magenta.png"),
        ("AP-0119", "boss_shields", "aegis_bastion", 2, "amber",   "boss_body_03_aegis_bastion_512@amber.png"),
    ]
    for g_idx, gid in enumerate(GLYPH_IDS):
        arch = ARCHETYPES[g_idx % 8]
        pcfg = g_idx // 8
        pal = PAL_KEYS[(g_idx * 2 + pcfg) % len(PAL_KEYS)]
        uno = g_idx + 4
        fname = f"boss_body_{uno:02d}_{arch}_mk{pcfg+1}_512@{pal}.png"
        body_jobs.append(("AP-0120", f"GLYPH-boss-{gid}", f"{arch}-mk{pcfg+1}", pcfg, pal, fname))

    for uno, (row_id, base, var, pcfg, pal, fname) in enumerate(body_jobs, 1):
        arch_key = var.split("-mk")[0]
        c2 = render_boss_body(arch_key, pcfg, pal)
        sp = downsample_straight_rgba(c2, (512, 512))
        m_rel = f"masters/bodies/{fname}"
        s_rel = f"sprites/bodies/{fname}"
        sp.save(os.path.join(HERE, m_rel), "PNG", compress_level=9)
        sp.save(os.path.join(HERE, s_rel), "PNG", compress_level=9)
        sa = np.asarray(sp)
        assert sa[0, 0, 3] == 0 and sa[0, -1, 3] == 0 and sa[-1, 0, 3] == 0 and sa[-1, -1, 3] == 0
        val, ch, fill = measure_rgba(sp)
        records.append({
            "row_id": row_id, "batch": "B-BODY", "unit_no": uno, "planner_base": base,
            "variant": var, "delivered_px": "512x512", "master_px": "512x512",
            "source": m_rel, "file": s_rel, "license": LICENSE_NOTE,
            "author": AUTHOR_BRANCH, "recipe": f"b_boss_{pal}", "val": val, "chroma": ch, "fill": fill,
        })

    # 2. 7 B-PART units (AP-0122..AP-0128)
    part_jobs = [
        ("AP-0122", "boss",                   "command_head",       "crimson"),
        ("AP-0123", "boss dong ho real",      "chrono_gear_turret", "amber"),
        ("AP-0124", "boss nhen doc xanh",     "venom_fang_pod",     "emerald"),
        ("AP-0125", "boss to vc ban 2 ben",   "broadside_railgun",  "crimson"),
        ("AP-0126", "minibosstronxoay",       "rotary_saw_ring",    "magenta"),
        ("AP-0127", "sieuhopthe tachbophan",  "combiner_claw_arm",  "violet"),
        ("AP-0128", "web",                    "energy_snare_web",   "emerald"),
    ]
    for pno, (row_id, base, var, pal) in enumerate(part_jobs, 1):
        c2 = render_boss_part(pno, var, pal)
        m_im = downsample_straight_rgba(c2, (512, 512))
        s_im = downsample_straight_rgba(c2, (256, 256))
        fname = f"boss_part_{pno:02d}_{var}_256@{pal}.png"
        m_rel = f"masters/parts/{fname}"
        s_rel = f"sprites/parts/{fname}"
        m_im.save(os.path.join(HERE, m_rel), "PNG", compress_level=9)
        s_im.save(os.path.join(HERE, s_rel), "PNG", compress_level=9)
        sa = np.asarray(s_im)
        assert sa[0, 0, 3] == 0 and sa[0, -1, 3] == 0 and sa[-1, 0, 3] == 0 and sa[-1, -1, 3] == 0
        val, ch, fill = measure_rgba(s_im)
        records.append({
            "row_id": row_id, "batch": "B-PART", "unit_no": pno, "planner_base": base,
            "variant": var, "delivered_px": "256x256", "master_px": "512x512",
            "source": m_rel, "file": s_rel, "license": LICENSE_NOTE,
            "author": AUTHOR_BRANCH, "recipe": f"b_bosspart_{pal}", "val": val, "chroma": ch, "fill": fill,
        })

    with open(os.path.join(HERE, "w3b_units.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "w3b_units.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    print(f"SUCCESS: {len(records)} W3 BOSS units exported (masters/ + sprites/)")


if __name__ == "__main__":
    main()
