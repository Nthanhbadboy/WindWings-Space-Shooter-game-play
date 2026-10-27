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
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import pbr25d
import mecha25d

AUTHOR_BRANCH = "arena/eca8588b-windwings-space-shooter-game-p"
LICENSE_NOTE = "chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)"

OUTLINE    = (32, 22, 64, 255)

PALETTES = {
    "crimson": {
        "pri": ((228, 34, 82, 255),  (74, 8, 28, 255),   (255, 148, 174, 255)),
        "sec": ((98, 112, 158, 255), (28, 34, 58, 255),  (192, 206, 236, 255)),
        "acc": ((248, 184, 18, 255), (96, 46, 4, 255),   (255, 248, 162, 255)),
        "glow": (255, 238, 42, 255),
    },
    "violet": {
        "pri": ((132, 54, 214, 255), (42, 14, 86, 255),  (208, 158, 255, 255)),
        "sec": ((78, 102, 168, 255), (24, 34, 68, 255),  (176, 198, 244, 255)),
        "acc": ((236, 42, 152, 255), (84, 10, 54, 255),  (255, 156, 218, 255)),
        "glow": (0, 238, 255, 255),
    },
    "emerald": {
        "pri": ((16, 204, 138, 255), (6, 68, 46, 255),   (142, 255, 212, 255)),
        "sec": ((92, 106, 148, 255), (28, 34, 56, 255),  (186, 198, 228, 255)),
        "acc": ((248, 184, 18, 255), (96, 46, 4, 255),   (255, 246, 158, 255)),
        "glow": (176, 255, 48, 255),
    },
    "magenta": {
        "pri": ((228, 38, 146, 255), (76, 10, 52, 255),  (255, 156, 218, 255)),
        "sec": ((88, 98, 148, 255),  (26, 32, 58, 255),  (182, 196, 232, 255)),
        "acc": ((0, 208, 246, 255),  (6, 68, 108, 255),  (156, 252, 255, 255)),
        "glow": (255, 238, 52, 255),
    },
    "amber": {
        "pri": ((238, 164, 18, 255), (88, 42, 4, 255),   (255, 238, 146, 255)),
        "sec": ((102, 88, 148, 255), (32, 24, 58, 255),  (192, 182, 232, 255)),
        "acc": ((228, 34, 88, 255),  (78, 8, 32, 255),   (255, 146, 176, 255)),
        "glow": (0, 242, 255, 255),
    },
}

CORE_WHITE = (255, 253, 238, 255)

GLYPH_IDS = (
    [7001, 7002, 7003, 7004, 7005, 7006, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017, 7018]
    + [9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9017, 9018]
)
ARCHETYPES = ["citadel", "arachnid", "leviathan", "chronos", "seraph", "kraken", "scorpion", "colossus"]
PAL_KEYS = ["crimson", "violet", "emerald", "magenta", "amber"]

downsample_straight_rgba = pbr25d.downsample_straight_rgba


def draw_cel_poly(canvas, pts, col_triple, outline_w=7):
    base_c, shade_c, light_c = col_triple
    pbr25d.draw_25d_metal_poly(
        canvas, pts, base_c, shade_c, light_c,
        metallic=0.88, greebles=True, cast_ao=True, glow_vent_c=(0, 232, 255),
    )


def reg_poly(cx, cy, rx, ry, n=16, rot=0.0):
    return [(cx + math.cos(a + rot) * rx, cy + math.sin(a + rot) * ry) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def draw_boss_core(canvas, cx, cy, rx, ry, acc_triple, glow_c, outline_w=8):
    pbr25d.draw_25d_metal_poly(canvas, reg_poly(cx, cy, rx * 1.36, ry * 1.36, 20), acc_triple[0], acc_triple[1], acc_triple[2], metallic=0.92, greebles=False)
    pbr25d.draw_25d_plasma_bloom(canvas, cx, cy, rx * 1.18, ry * 1.18, glow_c[:3], strength=0.72)
    pbr25d.draw_25d_glass_dome(canvas, reg_poly(cx, cy, rx, ry, 20), core_rgb=glow_c[:3], deep_rgb=(42, 8, 36))


def draw_destructible_satellite(canvas, x, y, anchor_x, anchor_y, kind, P):
    """Visually separated destructible module linked by glowing 2.5D plasma energy tether (zero cartoon outline)."""
    teth = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(teth)
    td.line([(anchor_x, anchor_y), (x, y)], fill=(*P["glow"][:3], 185), width=16)
    teth = teth.filter(ImageFilter.GaussianBlur(radius=5.0))
    td2 = ImageDraw.Draw(teth)
    td2.line([(anchor_x, anchor_y), (x, y)], fill=(255, 255, 255, 235), width=5)
    canvas.alpha_composite(teth)

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


def draw_twin_heavy_arms(canvas, cx, cy, arm_kind, P):
    """Balanced yet tactically asymmetric heavy port & starboard boss weapon arms
    (e.g. Port Crusher Pincer Claw + Starboard Siege Railgun — commercial mecha-boss silhouette!)."""
    for s in (-1, 1):
        def m(pts):
            out = [(cx + s * (x - cx), y) for (x, y) in pts]
            return out if s == 1 else list(reversed(out))

        ak = arm_kind if s == 1 else ((arm_kind + 1) % 4)
        if ak == 0:
            arm = [(cx + 145, cy - 85), (cx + 395, cy - 25), (cx + 415, cy + 285), (cx + 315, cy + 325), (cx + 255, cy + 95), (cx + 145, cy + 65)]
            draw_cel_poly(canvas, m(arm), P["sec"], outline_w=9)
            mecha25d.draw_gun_barrel(canvas, cx + s * 362, cy + 245, cy + 448, w=72, barrels=2, glow_rgb=P["glow"][:3])
        elif ak == 1:
            upper = [(cx + 150, cy - 60), (cx + 425, cy + 15), (cx + 448, cy + 215), (cx + 335, cy + 365), (cx + 312, cy + 205), (cx + 155, cy + 80)]
            draw_cel_poly(canvas, m(upper), P["pri"], outline_w=9)
            jaw = [(cx + 275, cy + 195), (cx + 332, cy + 358), (cx + 228, cy + 325)]
            draw_cel_poly(canvas, m(jaw), P["acc"], outline_w=8)
            mecha25d.metal(canvas, mecha25d.reg_poly(cx + s * 325, cy + 195, 36, 36, 16), mecha25d.GUNMETAL, greebles=False, chamfer=0.0)
        elif ak == 2:
            blade = [(cx + 140, cy - 165), (cx + 445, cy - 95), (cx + 462, cy + 195), (cx + 295, cy + 385), (cx + 255, cy + 215), (cx + 145, cy + 55)]
            draw_cel_poly(canvas, m(blade), P["acc"], outline_w=9)
            in_b = [(cx + 205, cy - 95), (cx + 405, cy - 45), (cx + 412, cy + 165), (cx + 295, cy + 285)]
            draw_cel_poly(canvas, m(in_b), P["pri"], outline_w=6)
            mecha25d.draw_plasma_trough(canvas, cx + s * 315, cy + 65, 48, 148, P["glow"][:3], cells=4)
        else:
            pod = [(cx + 155, cy - 95), (cx + 415, cy - 55), (cx + 425, cy + 165), (cx + 165, cy + 145)]
            draw_cel_poly(canvas, m(pod), P["sec"], outline_w=9)
            mecha25d.draw_gun_barrel(canvas, cx + s * 295, cy + 135, cy + 395, w=118, barrels=3, glow_rgb=P["glow"][:3])


def render_boss_body(archetype, phase_cfg, pal_key):
    """Render 1 of 35 1024x1024 (2x of 512x512) Commercial 2.5D Metallic Boss Dreadnoughts."""
    S = 1024
    cx, cy = 512, 470
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    P = PALETTES[pal_key]

    # 0. Dark brushed-gunmetal heavy mechanical superstructure & forward chin cannons
    mecha25d.draw_ribbed_spine(im, cx, 135, 815, 165, 195, n_ribs=8)
    for s in (-1, 1):
        mecha25d.draw_gun_barrel(im, cx + s * 135, 655, 905, w=48, barrels=2, glow_rgb=P["glow"][:3])

    # 1. Separated destructible satellite modules (asymmetric layout on odd phases, twin + flank on Mk3/4)
    sat_dx = 384 - (phase_cfg % 2) * 18
    sat_y_l = 185 + (phase_cfg % 2) * 68
    sat_y_r = 225 - (phase_cfg % 2) * 32
    draw_destructible_satellite(im, cx - sat_dx, sat_y_l, cx - 165, cy - 125, phase_cfg, P)
    draw_destructible_satellite(im, cx + sat_dx, sat_y_r, cx + 165, cy - 115, (phase_cfg + 1) % 4, P)
    if phase_cfg in (2, 3):
        draw_destructible_satellite(im, cx - 398, 735, cx - 225, cy + 165, (phase_cfg + 2) % 4, P)

    draw_twin_heavy_arms(im, cx, cy, (phase_cfg + (ARCHETYPES.index(archetype) if archetype in ARCHETYPES else 0)) % 4, P)

    # 2. Stepped multi-petal dark-gunmetal rear turbine thrusters
    for tx, tw in [(cx - 132, 92), (cx, 112), (cx + 132, 92)]:
        mecha25d.draw_jet_nozzle(im, tx, 168, tw, 92, P["glow"][:3], pointing_down=False)

    # 3. Archetype-specific symmetrical multi-layered dreadnought chassis + glowing reactor core(s)
    if archetype == "emblem_s":
        for s in (-1, 1):
            wing = [(cx + s * 125, cy - 155), (cx + s * 426, cy - 85), (cx + s * 400, cy + 95), (cx + s * 135, cy + 125)]
            draw_cel_poly(im, wing if s == 1 else list(reversed(wing)), P["pri"], outline_w=9)
        hull = [(cx, 855), (cx + 215, 625), (cx + 195, 165), (cx - 195, 165), (cx - 215, 625)]
        draw_cel_poly(im, hull, P["sec"], outline_w=10)
        plate = [(cx, 785), (cx + 148, 565), (cx + 128, 215), (cx - 128, 215), (cx - 148, 565)]
        draw_cel_poly(im, plate, P["pri"], outline_w=8)
        draw_boss_core(im, cx, cy - 10, 78, 92, P["acc"], P["glow"], outline_w=9)

    elif archetype == "overlord_x":
        for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            xw = [(cx + sx * 85, cy + sy * 65), (cx + sx * 425, cy + sy * 305), (cx + sx * 335, cy + sy * 365), (cx + sx * 55, cy + sy * 135)]
            draw_cel_poly(im, xw, P["pri"], outline_w=9)
        hull = reg_poly(cx, cy, 205, 240, 8, rot=math.pi / 8)
        draw_cel_poly(im, hull, P["sec"], outline_w=10)
        in_h = reg_poly(cx, cy, 138, 165, 8, rot=math.pi / 8)
        draw_cel_poly(im, in_h, P["pri"], outline_w=8)
        draw_boss_core(im, cx, cy, 86, 86, P["acc"], P["glow"], outline_w=9)

    elif archetype == "aegis_bastion":
        for k in range(4):
            a0 = math.pi * (0.14 + k * 0.19)
            a1 = a0 + 0.15
            sh = [
                (cx + math.cos(a0) * 395, cy + 55 + math.sin(a0) * 355),
                (cx + math.cos(a1) * 395, cy + 55 + math.sin(a1) * 355),
                (cx + math.cos(a1) * 315, cy + 55 + math.sin(a1) * 285),
                (cx + math.cos(a0) * 315, cy + 55 + math.sin(a0) * 285),
            ]
            draw_cel_poly(im, sh, P["acc"], outline_w=8)
        hull = [(cx - 275, cy - 185), (cx + 275, cy - 185), (cx + 285, cy + 145), (cx, cy + 295), (cx - 285, cy + 145)]
        draw_cel_poly(im, hull, P["pri"], outline_w=10)
        deck = [(cx - 195, cy - 135), (cx + 195, cy - 135), (cx + 185, cy + 110), (cx, cy + 215), (cx - 185, cy + 110)]
        draw_cel_poly(im, deck, P["sec"], outline_w=8)
        draw_boss_core(im, cx, cy - 10, 92, 68, P["acc"], P["glow"], outline_w=9)

    elif archetype == "citadel":
        for s in (-1, 1):
            spon = [(cx + s * 145, cy - 195), (cx + s * 420, cy - 135), (cx + s * 428, cy + 115), (cx + s * 155, cy + 175)]
            draw_cel_poly(im, spon if s == 1 else list(reversed(spon)), P["sec"], outline_w=9)
        hull = [(cx - 195, 145), (cx + 195, 145), (cx + 225, 595), (cx, 835), (cx - 225, 595)]
        draw_cel_poly(im, hull, P["pri"], outline_w=10)
        bridge = [(cx - 125, 225), (cx + 125, 225), (cx + 145, 545), (cx, 715), (cx - 145, 545)]
        draw_cel_poly(im, bridge, P["sec"], outline_w=8)
        for bx in (cx - 98, cx + 98):
            tur = [(bx - 28, 695), (bx + 28, 695), (bx + 18, 885), (bx - 18, 885)]
            draw_cel_poly(im, tur, P["acc"], outline_w=7)
        draw_boss_core(im, cx, cy, 82, 82, P["acc"], P["glow"], outline_w=9)

    elif archetype == "arachnid":
        for s in (-1, 1):
            for k, ly in enumerate([-145, -15, 115]):
                leg = [
                    (cx + s * 135, cy + ly),
                    (cx + s * 440, cy + ly - 65),
                    (cx + s * 468, cy + ly + 95 + k * 25),
                    (cx + s * 404, cy + ly + 85 + k * 25),
                    (cx + s * 385, cy + ly - 10),
                    (cx + s * 135, cy + ly + 48),
                ]
                draw_cel_poly(im, leg if s == 1 else list(reversed(leg)), P["acc"], outline_w=8)
        abdomen = reg_poly(cx, 245, 195, 145, 16)
        draw_cel_poly(im, abdomen, P["sec"], outline_w=9)
        ceph = [(cx, 825), (cx + 195, 595), (cx + 175, 315), (cx - 175, 315), (cx - 195, 595)]
        draw_cel_poly(im, ceph, P["pri"], outline_w=10)
        draw_boss_core(im, cx, 505, 68, 68, P["acc"], P["glow"], outline_w=8)
        draw_boss_core(im, cx - 95, 595, 34, 34, P["acc"], P["glow"], outline_w=6)
        draw_boss_core(im, cx + 95, 595, 34, 34, P["acc"], P["glow"], outline_w=6)

    elif archetype == "leviathan":
        for s in (-1, 1):
            manta = [(cx + s * 95, 215), (cx + s * 470, 345), (cx + s * 444, 585), (cx + s * 125, 495)]
            draw_cel_poly(im, manta if s == 1 else list(reversed(manta)), P["pri"], outline_w=9)
        spine = [(cx, 895), (cx + 175, 565), (cx + 145, 155), (cx - 145, 155), (cx - 175, 565)]
        draw_cel_poly(im, spine, P["sec"], outline_w=10)
        armor = [(cx, 795), (cx + 118, 525), (cx + 95, 215), (cx - 95, 215), (cx - 118, 525)]
        draw_cel_poly(im, armor, P["pri"], outline_w=8)
        draw_boss_core(im, cx, 445, 88, 62, P["acc"], P["glow"], outline_w=9)

    elif archetype == "chronos":
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
        for s in (-1, 1):
            pend = [(cx + s * 32, cy + 125), (cx + s * 92, cy + 125), (cx + s * 118, 885), (cx + s * 48, 865)]
            draw_cel_poly(im, pend if s == 1 else list(reversed(pend)), P["acc"], outline_w=8)
        draw_boss_core(im, cx, cy, 66, 66, P["acc"], P["glow"], outline_w=8)

    elif archetype == "seraph":
        for s in (-1, 1):
            for k in range(3):
                wy = 205 + k * 125
                wing = [(cx + s * 95, wy), (cx + s * (474 - k * 22), wy - 85), (cx + s * (450 - k * 22), wy + 45), (cx + s * 105, wy + 75)]
                draw_cel_poly(im, wing if s == 1 else list(reversed(wing)), P["acc"] if k % 2 == 0 else P["pri"], outline_w=8)
        torso = [(cx, 865), (cx + 165, 585), (cx + 185, 225), (cx, 135), (cx - 185, 225), (cx - 165, 585)]
        draw_cel_poly(im, torso, P["pri"], outline_w=10)
        crest = [(cx, 795), (cx + 92, 515), (cx, 225), (cx - 92, 515)]
        draw_cel_poly(im, crest, P["sec"], outline_w=8)
        draw_boss_core(im, cx, 465, 68, 96, P["acc"], P["glow"], outline_w=8)

    elif archetype == "kraken":
        for k, dx in enumerate([-235, -120, 0, 120, 235]):
            tent = [(cx + dx * 0.55 - 26, 615), (cx + dx * 0.55 + 26, 615), (cx + dx + 22, 905 - abs(k - 2) * 28), (cx + dx - 22, 905 - abs(k - 2) * 28)]
            draw_cel_poly(im, tent, P["acc"], outline_w=8)
        mantle = [(cx, 112), (cx + 245, 345), (cx + 195, 655), (cx - 195, 655), (cx - 245, 345)]
        draw_cel_poly(im, mantle, P["pri"], outline_w=10)
        plate = reg_poly(cx, 445, 145, 165, 14)
        draw_cel_poly(im, plate, P["sec"], outline_w=8)
        draw_boss_core(im, cx, 465, 84, 72, P["acc"], P["glow"], outline_w=9)

    elif archetype == "scorpion":
        for s in (-1, 1):
            tail = [(cx + s * 65, 165), (cx + s * 245, 88), (cx + s * 365, 215), (cx + s * 295, 345), (cx + s * 225, 245), (cx + s * 185, 168), (cx + s * 45, 225)]
            draw_cel_poly(im, tail if s == 1 else list(reversed(tail)), P["acc"], outline_w=9)
        hull = [(cx - 195, 205), (cx + 195, 205), (cx + 215, 635), (cx, 785), (cx - 215, 635)]
        draw_cel_poly(im, hull, P["sec"], outline_w=10)
        carapace = [(cx - 135, 255), (cx + 135, 255), (cx + 145, 615), (cx, 725), (cx - 145, 615)]
        draw_cel_poly(im, carapace, P["pri"], outline_w=8)
        draw_boss_core(im, cx, 485, 76, 76, P["acc"], P["glow"], outline_w=8)

    else:  # colossus
        for s in (-1, 1):
            sh = [(cx + s * 135, 215), (cx + s * 456, 155), (cx + s * 434, 415), (cx + s * 155, 435)]
            draw_cel_poly(im, sh if s == 1 else list(reversed(sh)), P["acc"], outline_w=9)
        torso = [(cx - 195, 215), (cx + 195, 215), (cx + 165, 745), (cx, 845), (cx - 165, 745)]
        draw_cel_poly(im, torso, P["pri"], outline_w=10)
        head = [(cx, 108), (cx + 125, 185), (cx + 92, 315), (cx - 92, 315), (cx - 125, 185)]
        draw_cel_poly(im, head, P["sec"], outline_w=9)
        horn_l = [(cx - 75, 165), (cx - 195, 58), (cx - 125, 215)]
        horn_r = [(cx + 75, 165), (cx + 195, 58), (cx + 125, 215)]
        draw_cel_poly(im, horn_l, P["acc"], outline_w=7)
        draw_cel_poly(im, horn_r, P["acc"], outline_w=7)
        draw_boss_core(im, cx, 505, 92, 82, P["acc"], P["glow"], outline_w=9)

    # 4. Universal Multi-Layered Dreadnought Sub-Plating, VLS Missile Bays, Cheek Mandibles & Plasma Troughs!
    for s in (-1, 1):
        # Upper shoulder armored VLS micro-missile pod cowling
        vls_box = [(cx + s * 118, 235), (cx + s * 255, 265), (cx + s * 238, 375), (cx + s * 112, 355)]
        mecha25d.metal(im, mecha25d.orient(vls_box, s), mecha25d.GUNMETAL, greebles=False)
        for mx_i in range(2):
            for my_i in range(2):
                cell_x = cx + s * (152 + mx_i * 52)
                cell_y = 282 + my_i * 46
                mecha25d.metal(im, mecha25d.reg_poly(cell_x, cell_y, 18, 18, 10), P["acc"], greebles=False, chamfer=0.0)
        # Flanking glowing plasma cooling troughs beside central boss core
        mecha25d.draw_plasma_trough(im, cx + s * 142, 475, 42, 136, P["glow"][:3], cells=4)
        # Lower forward cheek mandible armor plate (breaks up any smooth prow!)
        mand = [(cx + s * 56, 635), (cx + s * 178, 585), (cx + s * 148, 765), (cx + s * 42, 815)]
        draw_cel_poly(im, mecha25d.orient(mand, s), P["acc"], outline_w=7)

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
        web = Image.new("RGBA", im.size, (0, 0, 0, 0))
        wd = ImageDraw.Draw(web)
        for rad in (165, 285, 405):
            pts = reg_poly(cx, cy, rad, rad, 8)
            wd.line(pts + [pts[0]], fill=(*P["pri"][0][:3], 220), width=22, joint="curve")
        for k in range(8):
            a = k * math.pi / 4
            px, py = cx + math.cos(a) * 435, cy + math.sin(a) * 435
            wd.line([(cx, cy), (px, py)], fill=(*P["glow"][:3], 220), width=18)
        web = web.filter(ImageFilter.GaussianBlur(radius=5.5))
        wd2 = ImageDraw.Draw(web)
        for rad in (165, 285, 405):
            pts = reg_poly(cx, cy, rad, rad, 8)
            wd2.line(pts + [pts[0]], fill=(255, 255, 255, 235), width=6, joint="curve")
        im.alpha_composite(web)
        for k in range(8):
            a = k * math.pi / 4
            px, py = cx + math.cos(a) * 435, cy + math.sin(a) * 435
            draw_cel_poly(im, reg_poly(px, py, 36, 36, 8), P["acc"], outline_w=7)
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
