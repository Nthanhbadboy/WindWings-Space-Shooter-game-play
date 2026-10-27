#!/usr/bin/env python3
"""
W1-PLAYER Variant B builder — WindWings (Godot port)
Vai: Art-designer-B  ·  Nhánh: arena/eca8588b-windwings-space-shooter-game-p

Style: SOLAR NEON ARCADE-POP (independent bright cel-shaded 2D arcade-pop direction:
pearl-white & electric cobalt-azure hulls, solar-gold stripes, neon-cyan canopies & lasers,
crisp deep-navy cel outlines, 3-tone stepped 30-deg top-left lighting, straight unpremultiplied RGBA).

Produces ALL 48 units of lane PLAYER from docs/art-plan/art-planner.csv @16761cd5c:
  - P-SHIP   (AP-0016): 25 units -> masters/ships/ (512x512) + sprites/ships/ (256x256 RGBA)
  - P-DRONE  (AP-0011): 13 units -> masters/drones/ (256x256) + sprites/drones/ (128x128 RGBA)
  - P-BULLET (AP-0002..0009): 8 units -> masters/bullets/ (2x) + sprites/bullets/ (6x 32x32 + 2x 32x512 RGBA)
  - P-FX     (AP-0013..0014): 2 units -> masters/fx/ (256x256) + sprites/fx/ (128x128 RGBA)
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

# Solar Neon 2.5D Semi-Realistic Metallic Alloy Palette (Variant B — zero cartoon outline!)
NAVY_OUTLINE = (18, 36, 82, 255)
PEARL_LIGHT  = (253, 254, 255, 255)
PEARL_BASE   = (208, 224, 246, 255)
PEARL_SHADE  = (68, 92, 138, 255)

AZURE_LIGHT  = (132, 212, 255, 255)
AZURE_BASE   = (26, 114, 244, 255)
AZURE_SHADE  = (10, 38, 108, 255)

GOLD_LIGHT   = (255, 250, 168, 255)
GOLD_BASE    = (248, 188, 18, 255)
GOLD_SHADE   = (118, 52, 4, 255)

TANG_LIGHT   = (255, 198, 102, 255)
TANG_BASE    = (246, 98, 16, 255)
TANG_SHADE   = (108, 26, 6, 255)

CYAN_WHITE   = (238, 255, 255, 255)
CYAN_LIGHT   = (136, 252, 255, 255)
CYAN_BASE    = (0, 218, 252, 255)
CYAN_SHADE   = (0, 82, 136, 255)

EMERALD_BASE = (12, 218, 158, 255)
EMER_LIGHT   = (156, 255, 226, 255)
EMER_BASE    = (12, 218, 158, 255)
EMER_SHADE   = (6, 78, 58, 255)
MAGENTA_BASE = (238, 38, 136, 255)


downsample_straight_rgba = pbr25d.downsample_straight_rgba

# Distinct sunlit 2.5D anodized metallic liveries across the 25-ship & 13-drone fleet (keeps Family 0 = Hero Pearl/Cobalt/Gold)
SHIP_LIVERIES = [
    # 0: Hero Brushed Titanium + Cobalt-Azure + Cyan Canopy
    {"hull": ((196, 214, 240, 255), (56, 78, 122, 255), (252, 254, 255, 255)),
     "wing": ((32, 118, 242, 255),  (10, 38, 108, 255), (142, 214, 255, 255)),
     "glass": (0, 232, 255)},
    # 1: Burnished Solar-Gold + Crimson-Ruby Alloy + Amber Canopy
    {"hull": ((236, 174, 28, 255),  (92, 42, 6, 255),   (255, 246, 168, 255)),
     "wing": ((214, 38, 82, 255),   (78, 10, 32, 255),  (255, 142, 172, 255)),
     "glass": (0, 238, 255)},
    # 2: Brushed Silver-Chrome + Emerald-Jade Alloy + Lime-Cyan Canopy
    {"hull": ((204, 218, 232, 255), (62, 78, 96, 255),  (252, 255, 255, 255)),
     "wing": ((18, 188, 136, 255),  (6, 68, 48, 255),   (138, 255, 214, 255)),
     "glass": (142, 255, 86)},
    # 3: Anodized Crimson-Rose + Brushed Titanium + Solar-Gold Canopy
    {"hull": ((222, 48, 98, 255),   (82, 12, 38, 255),  (255, 156, 188, 255)),
     "wing": ((182, 198, 224, 255), (52, 68, 98, 255),  (248, 252, 255, 255)),
     "glass": (255, 208, 28)},
    # 4: Iridescent Royal-Violet + Electric-Cyan Alloy + Magenta Canopy
    {"hull": ((132, 68, 228, 255),  (44, 16, 102, 255), (208, 166, 255, 255)),
     "wing": ((16, 176, 232, 255),  (8, 58, 104, 255),  (148, 244, 255, 255)),
     "glass": (255, 72, 188)},
    # 5: Special #25 Brushed Gunmetal-Silver Prototype
    {"hull": ((168, 178, 194, 255), (48, 54, 66, 255),  (242, 246, 252, 255)),
     "wing": ((108, 118, 136, 255), (32, 38, 48, 255),  (204, 214, 228, 255)),
     "glass": (180, 238, 255)},
]
ACTIVE_LIVERY = SHIP_LIVERIES[0]


def draw_cel_poly(canvas, pts, base_c, shade_c, light_c, outline_w=6, outline_c=NAVY_OUTLINE):
    if base_c == PEARL_BASE:
        base_c, shade_c, light_c = ACTIVE_LIVERY["hull"]
    elif base_c == AZURE_BASE:
        base_c, shade_c, light_c = ACTIVE_LIVERY["wing"]
    pbr25d.draw_25d_metal_poly(
        canvas, pts, base_c, shade_c, light_c,
        metallic=0.86, greebles=True, cast_ao=True, glow_vent_c=ACTIVE_LIVERY["glass"],
    )


def mirror_pts(pts, cx):
    return [(2 * cx - x, y) for (x, y) in pts]


def draw_sym_cel(canvas, right_pts, cx, base_c, shade_c, light_c, outline_w=6):
    left_pts = mirror_pts(right_pts, cx)
    draw_cel_poly(canvas, left_pts, base_c, shade_c, light_c)
    draw_cel_poly(canvas, right_pts, base_c, shade_c, light_c)


def draw_canopy(canvas, cx, y_top, y_bot, half_w, outline_w=6):
    h = y_bot - y_top
    collar = [
        (cx, y_top - h * 0.16),
        (cx + half_w * 1.28, y_top + h * 0.42),
        (cx + half_w * 1.12, y_bot + h * 0.14),
        (cx, y_bot + h * 0.24),
        (cx - half_w * 1.12, y_bot + h * 0.14),
        (cx - half_w * 1.28, y_top + h * 0.42),
    ]
    pbr25d.draw_25d_metal_poly(canvas, collar, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, metallic=0.90, greebles=False)
    glass = [
        (cx, y_top),
        (cx + half_w * 0.92, y_top + h * 0.36),
        (cx + half_w * 0.78, y_bot - h * 0.12),
        (cx, y_bot),
        (cx - half_w * 0.78, y_bot - h * 0.12),
        (cx - half_w * 0.92, y_top + h * 0.36),
    ]
    pbr25d.draw_25d_glass_dome(canvas, glass, core_rgb=ACTIVE_LIVERY["glass"], deep_rgb=(8, 30, 82))


def draw_gun_barrel(canvas, x, y_tip, y_base, w, outline_w=5):
    pts = [
        (x - w * 0.45, y_tip),
        (x + w * 0.45, y_tip),
        (x + w * 0.66, y_base),
        (x - w * 0.66, y_base),
    ]
    pbr25d.draw_25d_metal_poly(canvas, pts, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, metallic=0.88, greebles=False)
    tip = [
        (x - w * 0.56, y_tip - w * 0.28),
        (x + w * 0.56, y_tip - w * 0.28),
        (x + w * 0.56, y_tip + w * 0.42),
        (x - w * 0.56, y_tip + w * 0.42),
    ]
    pbr25d.draw_25d_metal_poly(canvas, tip, GOLD_BASE, GOLD_SHADE, GOLD_LIGHT, metallic=0.92, greebles=False)
    pbr25d.draw_25d_plasma_bloom(canvas, x, y_tip - w * 0.15, w * 0.62, w * 0.62, (0, 236, 255), strength=0.85)


def draw_thruster(canvas, x, y_top, y_bot, w, outline_w=5):
    pbr25d.draw_25d_plasma_bloom(canvas, x, y_bot + w * 0.38, w * 0.72, w * 1.15, (0, 228, 255), strength=0.95)
    bell = [
        (x - w * 0.48, y_top),
        (x + w * 0.48, y_top),
        (x + w * 0.68, y_bot),
        (x - w * 0.68, y_bot),
    ]
    pbr25d.draw_25d_metal_poly(canvas, bell, (96, 114, 152, 255), (28, 36, 62, 255), PEARL_LIGHT, metallic=0.92, greebles=False)
    pbr25d.draw_25d_plasma_bloom(canvas, x, y_bot + w * 0.04, w * 0.46, w * 0.34, (120, 248, 255), strength=0.95)


def draw_ship_tier_underlay(canvas, cx, sub, span):
    """Distinct structural tier silhouettes (Mk-I..Mk-V) so every unit in a 5-ship family has unique geometry."""
    if sub == 1:
        # Mk-II: Forward swept Solar-Gold nose canard blades
        can_r = [(cx + 42, 205), (cx + 195, 155), (cx + 210, 235), (cx + 55, 290)]
        draw_sym_cel(canvas, can_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=7)
    elif sub == 2:
        # Mk-III: Heavy Emerald-Cyan shoulder shield pods + wingtip crystal fins
        pod_r = [(cx + 102, 240), (cx + 185, 210), (cx + 205, 420), (cx + 112, 455)]
        draw_sym_cel(canvas, pod_r, cx, EMER_BASE, EMER_SHADE, EMER_LIGHT, outline_w=7)
        fin_r = [(cx + span - 20, 430), (cx + span + 62, 365), (cx + span + 48, 535), (cx + span - 15, 555)]
        draw_sym_cel(canvas, fin_r, cx, CYAN_BASE, CYAN_SHADE, CYAN_WHITE, outline_w=6)
    elif sub == 3:
        # Mk-IV: Elongated twin V-tail booms + Tangerine spear prongs
        vtail_r = [(cx + 88, 690), (cx + 245, 855), (cx + 195, 935), (cx + 68, 795)]
        draw_sym_cel(canvas, vtail_r, cx, TANG_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=7)
        prong_r = [(cx + 52, 165), (cx + 108, 72), (cx + 128, 225), (cx + 58, 250)]
        draw_sym_cel(canvas, prong_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=6)
    elif sub == 4:
        # Mk-V: Apex Overdrive deployed neon-cyan energy wing-blades + crown halo fins + rear overdrive tail
        blade_r = [(cx + span - 35, 300), (cx + span + 78, 195), (cx + span + 64, 465), (cx + span - 25, 520)]
        draw_sym_cel(canvas, blade_r, cx, CYAN_BASE, CYAN_SHADE, CYAN_WHITE, outline_w=7)
        crown_r = [(cx + 54, 175), (cx + 178, 92), (cx + 192, 195), (cx + 72, 260)]
        draw_sym_cel(canvas, crown_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=7)
        tail_r = [(cx + 92, 705), (cx + 255, 875), (cx + 205, 940), (cx + 76, 805)]
        draw_sym_cel(canvas, tail_r, cx, EMER_BASE, EMER_SHADE, EMER_LIGHT, outline_w=7)


def draw_ship_tier_crest(canvas, cx, sub):
    """Dorsal hull crest / nose spear overlay per tier."""
    if sub == 2:
        crest = [(cx, 575), (cx + 42, 650), (cx, 785), (cx - 42, 650)]
        draw_cel_poly(canvas, crest, EMER_BASE, EMER_SHADE, EMER_LIGHT, outline_w=6)
    elif sub == 3:
        spear = [(cx, 48), (cx + 34, 185), (cx, 235), (cx - 34, 185)]
        draw_cel_poly(canvas, spear, TANG_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=6)
    elif sub == 4:
        spear = [(cx, 42), (cx + 40, 178), (cx, 240), (cx - 40, 178)]
        draw_cel_poly(canvas, spear, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=6)
        crest = [(cx, 560), (cx + 48, 665), (cx, 825), (cx - 48, 665)]
        draw_cel_poly(canvas, crest, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=6)


MECHA_LIVERIES = [
    # 0: Hero Pearl-Titanium + Sunlit Cobalt-Azure + Solar-Gold Trim + Sapphire Canopy
    {
        "hull": ((214, 228, 248), (62, 84, 128), (254, 255, 255)),
        "sec":  ((32, 118, 244),  (12, 42, 112), (144, 214, 255)),
        "acc":  ((248, 186, 22),  (108, 48, 6),  (255, 248, 168)),
        "glass": ((12, 46, 136), (0, 208, 255), (198, 252, 255)),
        "glow": (0, 232, 255),
    },
    # 1: Burnished Solar-Gold + Brushed Titanium + Crimson Trim + Emerald Canopy
    {
        "hull": ((238, 178, 28),  (94, 44, 6),   (255, 246, 168)),
        "sec":  ((176, 192, 216), (52, 64, 88),  (244, 250, 255)),
        "acc":  ((224, 44, 88),   (84, 12, 34),  (255, 152, 182)),
        "glass": ((6, 68, 54), (16, 224, 158), (186, 255, 228)),
        "glow": (0, 238, 255),
    },
    # 2: Anodized Emerald-Jade + Solar-Gold + Pearl Trim + Cyan Canopy
    {
        "hull": ((22, 192, 138),  (8, 68, 48),   (148, 255, 218)),
        "sec":  ((196, 212, 232), (58, 74, 98),  (252, 255, 255)),
        "acc":  ((246, 188, 24),  (104, 46, 6),  (255, 248, 168)),
        "glass": ((10, 48, 138), (0, 218, 255), (196, 252, 255)),
        "glow": (72, 255, 196),
    },
    # 3: Anodized Crimson-Rose + Pearl-Silver + Solar-Gold Trim + Amber Canopy
    {
        "hull": ((226, 48, 96),   (86, 12, 38),  (255, 158, 188)),
        "sec":  ((198, 212, 234), (58, 72, 102), (250, 254, 255)),
        "acc":  ((248, 186, 24),  (108, 48, 6),  (255, 246, 168)),
        "glass": ((96, 38, 6), (255, 188, 24), (255, 246, 188)),
        "glow": (255, 196, 36),
    },
    # 4: Iridescent Royal-Violet + Electric-Cyan + Magenta Trim + Neon-Pink Canopy
    {
        "hull": ((136, 72, 232),  (46, 18, 106), (212, 172, 255)),
        "sec":  ((22, 178, 236),  (8, 58, 108),  (152, 244, 255)),
        "acc":  ((242, 52, 168),  (92, 12, 64),  (255, 164, 224)),
        "glass": ((78, 12, 86), (255, 64, 196), (255, 206, 246)),
        "glow": (255, 76, 208),
    },
    # 5: Prototype #25 / Drone #13 Brushed Gunmetal Stealth + Solar-Gold & Cyan Trim
    {
        "hull": ((156, 168, 188), (46, 54, 68),  (238, 244, 252)),
        "sec":  ((98, 112, 134),  (32, 38, 50),  (186, 202, 224)),
        "acc":  ((246, 184, 24),  (104, 46, 6),  (255, 246, 168)),
        "glass": ((12, 52, 138), (0, 218, 255), (198, 252, 255)),
        "glow": (0, 236, 255),
    },
]


def render_ship(unit_idx):
    """Render 1 of 25 commercial-grade 2.5D semi-realistic metallic starfighters at 1024x1024."""
    liv = MECHA_LIVERIES[5 if unit_idx == 25 else ((unit_idx - 1) % 5)]
    return mecha25d.render_commercial_ship(unit_idx, liv, os.path.join(HERE, "masters/_raw"))


def render_drone(unit_idx):
    """Render 1 of 13 commercial-grade articulated escort weapon drones at 512x512."""
    liv = MECHA_LIVERIES[5 if unit_idx == 13 else ((unit_idx - 1) % 5)]
    return mecha25d.render_commercial_drone(unit_idx, liv)


def _unused_legacy_ship_drone(unit_idx):
    S = 1024
    cx = S * 0.5
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fam = (unit_idx - 1) // 5       # 0..4
    sub = (unit_idx - 1) % 5        # 0..4
    ACTIVE_LIVERY = SHIP_LIVERIES[5 if unit_idx == 25 else ((fam + sub) % 5 if sub >= 3 else fam)]

    if fam == 0:
        # Family 0: WINDFANG — Forward-Swept Hero Interceptor (matches W0 hero starfighter!)
        span = 365 + sub * 14
        draw_ship_tier_underlay(im, cx, sub, span)
        tip_y = 330 - sub * 20
        root_y0, root_y1 = 390 - sub * 8, 665 + sub * 8
        # Gun barrels first (under wings)
        draw_gun_barrel(im, cx - 125 - sub * 8, 175 - sub * 10, 410, 26)
        draw_gun_barrel(im, cx + 125 + sub * 8, 175 - sub * 10, 410, 26)
        if sub >= 1:
            draw_gun_barrel(im, cx - span + 18, tip_y - 95, tip_y + 45, 22)
            draw_gun_barrel(im, cx + span - 18, tip_y - 95, tip_y + 45, 22)
        # Forward-swept main wings (cobalt blue outer + pearl inner)
        wing_r = [
            (cx + 68, root_y0),
            (cx + span, tip_y),
            (cx + span + 18, tip_y + 135 + sub * 10),
            (cx + 150, root_y1 + 25),
            (cx + 65, root_y1),
        ]
        draw_sym_cel(im, wing_r, cx, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=8)
        # Inner pearl wing plating
        inner_r = [
            (cx + 64, root_y0 + 18),
            (cx + span * 0.64, tip_y + 52),
            (cx + span * 0.60, tip_y + 155),
            (cx + 72, root_y1 - 18),
        ]
        draw_sym_cel(im, inner_r, cx, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=6)
        # Signature twin solar-gold wing stripes
        for k in range(2):
            off = k * 34
            st_r = [
                (cx + span * 0.66 + off, tip_y + 46 - off * 0.25),
                (cx + span * 0.73 + off, tip_y + 36 - off * 0.25),
                (cx + span * 0.71 + off, tip_y + 146 - off * 0.15),
                (cx + span * 0.64 + off, tip_y + 152 - off * 0.15),
            ]
            draw_sym_cel(im, st_r, cx, GOLD_BASE, GOLD_SHADE, GOLD_LIGHT, outline_w=4)
        # Wingtip pods
        pod_r = [
            (cx + span - 10, tip_y - 18),
            (cx + span + 26, tip_y + 10),
            (cx + span + 22, tip_y + 165),
            (cx + span - 12, tip_y + 145),
        ]
        draw_sym_cel(im, pod_r, cx, PEARL_BASE, AZURE_SHADE, PEARL_LIGHT, outline_w=7)
        # Rear tail stabilizers
        tail_r = [
            (cx + 55, 680),
            (cx + 185 + sub * 14, 775 + sub * 10),
            (cx + 155 + sub * 10, 845),
            (cx + 42, 790),
        ]
        draw_sym_cel(im, tail_r, cx, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=7)
        # Thrusters
        draw_thruster(im, cx - 66, 755, 865, 66, outline_w=7)
        draw_thruster(im, cx + 66, 755, 865, 66, outline_w=7)
        if sub == 4:
            draw_thruster(im, cx, 785, 895, 56, outline_w=7)
        # Central pearl-azure fuselage
        fuse = [
            (cx, 96 - sub * 6),
            (cx + 76, 255),
            (cx + 106, 540),
            (cx + 88, 780),
            (cx, 835),
            (cx - 88, 780),
            (cx - 106, 540),
            (cx - 76, 255),
        ]
        draw_cel_poly(im, fuse, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=9)
        nose_cap = [
            (cx, 96 - sub * 6),
            (cx + 58, 235),
            (cx, 285),
            (cx - 58, 235),
        ]
        draw_cel_poly(im, nose_cap, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=7)
        draw_canopy(im, cx, 305, 565, 52, outline_w=7)

    elif fam == 1:
        # Family 1: SOLARVIPER — Sharp Triangular Delta Dart
        span = 350 + sub * 16
        draw_ship_tier_underlay(im, cx, sub, span)
        draw_gun_barrel(im, cx - 88, 125, 310, 22)
        draw_gun_barrel(im, cx + 88, 125, 310, 22)
        if sub >= 2:
            draw_gun_barrel(im, cx - 220 - sub * 10, 420, 560, 22)
            draw_gun_barrel(im, cx + 220 + sub * 10, 420, 560, 22)
        # Canards on variants 1,3,4
        if sub in (1, 3, 4):
            can_r = [(cx + 42, 235), (cx + 155 + sub * 12, 290), (cx + 135 + sub * 10, 345), (cx + 46, 320)]
            draw_sym_cel(im, can_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=7)
        # Swept delta main wing
        delta_r = [
            (cx + 48, 240),
            (cx + span, 675 - sub * 18),
            (cx + span - 24, 790),
            (cx + 135, 735),
            (cx + 52, 775),
        ]
        draw_sym_cel(im, delta_r, cx, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=9)
        # Bold cobalt-blue delta chevron trim
        trim_r = [
            (cx + 76, 365),
            (cx + span - 28, 675 - sub * 18),
            (cx + span - 42, 748),
            (cx + 92, 650),
        ]
        draw_sym_cel(im, trim_r, cx, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=6)
        # Gold edge stripe
        st_r = [
            (cx + 115, 520),
            (cx + span - 52, 695 - sub * 14),
            (cx + span - 65, 735 - sub * 10),
            (cx + 118, 575),
        ]
        draw_sym_cel(im, st_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=5)
        draw_thruster(im, cx, 775, 895, 86, outline_w=8)
        if sub >= 1:
            draw_thruster(im, cx - 105, 745, 845, 52, outline_w=6)
            draw_thruster(im, cx + 105, 745, 845, 52, outline_w=6)
        fuse = [
            (cx, 78),
            (cx + 68, 280),
            (cx + 92, 620),
            (cx + 62, 800),
            (cx - 62, 800),
            (cx - 92, 620),
            (cx - 68, 280),
        ]
        draw_cel_poly(im, fuse, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=9)
        spine = [
            (cx, 95),
            (cx + 42, 290),
            (cx + 52, 745),
            (cx - 52, 745),
            (cx - 42, 290),
        ]
        draw_cel_poly(im, spine, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=6)
        draw_canopy(im, cx, 300, 560, 46, outline_w=7)

    elif fam == 2:
        # Family 2: SKYBASTION — Twin-Boom Heavy Siege Gunship
        boom_x = 185 + sub * 10
        outer_w = 365 + sub * 14
        draw_ship_tier_underlay(im, cx, sub, outer_w)
        # Heavy forward boom cannons
        draw_gun_barrel(im, cx - boom_x, 110 - sub * 6, 280, 32, outline_w=7)
        draw_gun_barrel(im, cx + boom_x, 110 - sub * 6, 280, 32, outline_w=7)
        if sub >= 2:
            draw_gun_barrel(im, cx - 72, 165, 320, 24, outline_w=6)
            draw_gun_barrel(im, cx + 72, 165, 320, 24, outline_w=6)
        # Outer stub wings
        stub_r = [
            (cx + boom_x + 35, 385),
            (cx + outer_w, 470 - sub * 20),
            (cx + outer_w - 10, 645 + sub * 12),
            (cx + boom_x + 35, 670),
        ]
        draw_sym_cel(im, stub_r, cx, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=8)
        gold_stub = [
            (cx + boom_x + 52, 465),
            (cx + outer_w - 22, 515 - sub * 14),
            (cx + outer_w - 28, 575 - sub * 10),
            (cx + boom_x + 52, 535),
        ]
        draw_sym_cel(im, gold_stub, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=5)
        # Cross bridge wing linking center hull to twin booms
        bridge = [
            (cx - boom_x, 370),
            (cx + boom_x, 370),
            (cx + boom_x, 635),
            (cx - boom_x, 635),
        ]
        draw_cel_poly(im, bridge, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=8)
        # Twin armored weapon booms
        boom_r = [
            (cx + boom_x, 185),
            (cx + boom_x + 58, 275),
            (cx + boom_x + 62, 765),
            (cx + boom_x, 825),
            (cx + boom_x - 54, 765),
            (cx + boom_x - 52, 275),
        ]
        draw_sym_cel(im, boom_r, cx, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=8)
        boom_cap_r = [
            (cx + boom_x, 185),
            (cx + boom_x + 48, 275),
            (cx + boom_x, 345),
            (cx + boom_x - 44, 275),
        ]
        draw_sym_cel(im, boom_cap_r, cx, TANG_BASE, TANG_SHADE, GOLD_BASE, outline_w=6)
        draw_thruster(im, cx - boom_x, 785, 895, 72, outline_w=7)
        draw_thruster(im, cx + boom_x, 785, 895, 72, outline_w=7)
        if sub in (1, 3, 4):
            draw_thruster(im, cx, 735, 845, 62, outline_w=7)
        # Central armored command nacelle
        pod = [
            (cx, 175 - sub * 12),
            (cx + 88, 305),
            (cx + 96, 680),
            (cx, 765),
            (cx - 96, 680),
            (cx - 88, 305),
        ]
        draw_cel_poly(im, pod, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=9)
        draw_canopy(im, cx, 325, 585, 56, outline_w=7)

    elif fam == 3:
        # Family 3: AEROFALCON — Swept-Back Double-Wing Raptor Striker
        span = 380 + sub * 14
        draw_ship_tier_underlay(im, cx, sub, span)
        sweep_y = 560 + sub * 20
        draw_gun_barrel(im, cx - 155, 250, 430, 24)
        draw_gun_barrel(im, cx + 155, 250, 430, 24)
        if sub >= 1:
            draw_gun_barrel(im, cx - 275 - sub * 8, 360, 510, 22)
            draw_gun_barrel(im, cx + 275 + sub * 8, 360, 510, 22)
        # Swept-back main raptor wings
        wing_r = [
            (cx + 65, 315),
            (cx + 245, 395),
            (cx + span, sweep_y),
            (cx + span - 35, sweep_y + 105),
            (cx + 210, 565),
            (cx + 68, 605),
        ]
        draw_sym_cel(im, wing_r, cx, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=9)
        wing_blue = [
            (cx + 72, 330),
            (cx + 235, 405),
            (cx + span - 16, sweep_y + 8),
            (cx + span - 42, sweep_y + 62),
            (cx + 85, 465),
        ]
        draw_sym_cel(im, wing_blue, cx, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=6)
        # Secondary rear scissor tail-wings
        rear_r = [
            (cx + 56, 635),
            (cx + 255 + sub * 16, 760 + sub * 10),
            (cx + 215 + sub * 14, 855),
            (cx + 48, 765),
        ]
        draw_sym_cel(im, rear_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=8)
        draw_thruster(im, cx - 58, 775, 890, 62, outline_w=7)
        draw_thruster(im, cx + 58, 775, 890, 62, outline_w=7)
        fuse = [
            (cx, 85),
            (cx + 72, 260),
            (cx + 96, 510),
            (cx + 76, 795),
            (cx, 845),
            (cx - 76, 795),
            (cx - 96, 510),
            (cx - 72, 260),
        ]
        draw_cel_poly(im, fuse, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=9)
        stripe_c = [
            (cx, 95),
            (cx + 38, 250),
            (cx, 310),
            (cx - 38, 250),
        ]
        draw_cel_poly(im, stripe_c, TANG_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=6)
        draw_canopy(im, cx, 295, 555, 48, outline_w=7)

    else:
        # Family 4: NOVAARC — Crescent / Halo Ring-Wing Experimental Starfighter
        rad = 330 + sub * 12
        draw_ship_tier_underlay(im, cx, sub, rad)
        cy_ring = 515
        # Outer crescent/ring wing via polygon segments
        outer_pts, inner_pts = [], []
        a_start = -math.pi * (0.82 + sub * 0.03)
        a_end = math.pi * (0.82 + sub * 0.03)
        steps = 28
        for k in range(steps + 1):
            ang = a_start + (a_end - a_start) * (k / steps) - math.pi / 2
            outer_pts.append((cx + math.cos(ang) * rad, cy_ring + math.sin(ang) * rad * 0.92))
            inner_pts.append((cx + math.cos(ang) * (rad - 86), cy_ring + math.sin(ang) * (rad - 86) * 0.92))
        ring_poly = outer_pts + list(reversed(inner_pts))
        draw_cel_poly(im, ring_poly, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=9)

        # Neon cyan glowing energy conduit inside ring
        mid_pts_o, mid_pts_i = [], []
        for k in range(steps + 1):
            ang = a_start + (a_end - a_start) * (k / steps) - math.pi / 2
            mid_pts_o.append((cx + math.cos(ang) * (rad - 26), cy_ring + math.sin(ang) * (rad - 26) * 0.92))
            mid_pts_i.append((cx + math.cos(ang) * (rad - 56), cy_ring + math.sin(ang) * (rad - 56) * 0.92))
        draw_cel_poly(im, mid_pts_o + list(reversed(mid_pts_i)), CYAN_BASE, CYAN_SHADE, CYAN_WHITE, outline_w=4)

        # Cross struts & forward prongs
        strut_r = [(cx + 62, 455), (cx + rad - 65, 430 - sub * 12), (cx + rad - 65, 525), (cx + 62, 555)]
        draw_sym_cel(im, strut_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=7)
        draw_gun_barrel(im, cx - 165 - sub * 10, 145, 315, 26)
        draw_gun_barrel(im, cx + 165 + sub * 10, 145, 315, 26)
        draw_thruster(im, cx - 64, 770, 885, 62, outline_w=7)
        draw_thruster(im, cx + 64, 770, 885, 62, outline_w=7)

        fuse = [
            (cx, 88),
            (cx + 76, 265),
            (cx + 92, 560),
            (cx + 74, 785),
            (cx, 835),
            (cx - 74, 785),
            (cx - 92, 560),
            (cx - 76, 265),
        ]
        draw_cel_poly(im, fuse, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=9)
        draw_canopy(im, cx, 295, 555, 50, outline_w=7)

    draw_ship_tier_crest(im, cx, sub)
    return im


def _unused_legacy_drone(unit_idx):
    """Legacy procedural drone replaced by mecha25d.render_commercial_drone."""
    global ACTIVE_LIVERY
    S = 512
    cx, cy = S * 0.5, S * 0.52
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fam = (unit_idx - 1) % 5
    ver = (unit_idx - 1) // 5
    ACTIVE_LIVERY = SHIP_LIVERIES[5 if unit_idx == 13 else ((unit_idx - 1) % 5)]

    # Distinct structural tier fins for ver=1 and ver=2 across all drone archetypes
    if ver == 1:
        fin_r = [(cx + 105, cy - 35), (cx + 225, cy - 115), (cx + 218, cy - 18), (cx + 115, cy + 25)]
        draw_sym_cel(im, fin_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=6)
        tail_r = [(cx + 42, cy + 105), (cx + 112, cy + 195), (cx + 75, cy + 215), (cx + 25, cy + 135)]
        draw_sym_cel(im, tail_r, cx, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=6)
    elif ver == 2:
        blade_r = [(cx + 95, cy - 85), (cx + 228, cy - 155), (cx + 225, cy + 65), (cx + 115, cy + 95)]
        draw_sym_cel(im, blade_r, cx, EMER_BASE, EMER_SHADE, EMER_LIGHT, outline_w=6)
        draw_gun_barrel(im, cx, 32, 130, 26, outline_w=6)

    if fam == 0:
        # Archetype 0: Orbital Shield Pod (matches W0 S3 wingman drone!)
        draw_gun_barrel(im, cx - 58 - ver * 12, 56, 165, 24, outline_w=6)
        draw_gun_barrel(im, cx + 58 + ver * 12, 56, 165, 24, outline_w=6)
        ear_r = [(cx + 125, cy - 85), (cx + 195 + ver * 12, cy - 45), (cx + 195 + ver * 12, cy + 55), (cx + 125, cy + 92)]
        draw_sym_cel(im, ear_r, cx, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=7)
        pts = [(cx + math.cos(a) * 148, cy + math.sin(a) * 148) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        draw_cel_poly(im, pts, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=8)
        ring = [(cx + math.cos(a) * 98, cy + math.sin(a) * 98) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
        draw_cel_poly(im, ring, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=6)
        core = [(cx + math.cos(a) * 56, cy + math.sin(a) * 56) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
        draw_cel_poly(im, core, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=6)
        ImageDraw.Draw(im).ellipse([cx - 22, cy - 28, cx - 2, cy - 8], fill=PEARL_LIGHT)

    elif fam == 1:
        # Archetype 1: Mini-Wing Interceptor Drone
        draw_gun_barrel(im, cx, 44, 155, 28, outline_w=6)
        w_r = [(cx + 38, cy - 75), (cx + 205, cy + 15 - ver * 22), (cx + 185, cy + 95), (cx + 42, cy + 75)]
        draw_sym_cel(im, w_r, cx, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=7)
        st_r = [(cx + 95, cy - 25), (cx + 165, cy + 12 - ver * 12), (cx + 155, cy + 58), (cx + 92, cy + 32)]
        draw_sym_cel(im, st_r, cx, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=5)
        draw_thruster(im, cx, cy + 105, cy + 175, 58, outline_w=6)
        body = [(cx, cy - 145), (cx + 68, cy - 35), (cx + 62, cy + 115), (cx - 62, cy + 115), (cx - 68, cy - 35)]
        draw_cel_poly(im, body, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=8)
        draw_canopy(im, cx, cy - 65, cy + 55, 34, outline_w=6)

    elif fam == 2:
        # Archetype 2: Hexagonal Gyro Blaster
        rot = ver * 0.26
        hex_pts = [(cx + math.cos(a + rot) * 168, cy + math.sin(a + rot) * 168) for a in np.linspace(0, 2 * math.pi, 6, endpoint=False)]
        draw_cel_poly(im, hex_pts, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=8)
        in_pts = [(cx + math.cos(a + rot) * 112, cy + math.sin(a + rot) * 112) for a in np.linspace(0, 2 * math.pi, 6, endpoint=False)]
        draw_cel_poly(im, in_pts, AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=6)
        core = [(cx + math.cos(a) * 58, cy + math.sin(a) * 58) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
        draw_cel_poly(im, core, CYAN_BASE, CYAN_SHADE, CYAN_WHITE, outline_w=6)
        draw_gun_barrel(im, cx - 72, 48, 135, 24, outline_w=6)
        draw_gun_barrel(im, cx + 72, 48, 135, 24, outline_w=6)

    elif fam == 3:
        # Archetype 3: Crescent Arc Emitter
        outer, inner = [], []
        for a in np.linspace(-2.2, 2.2, 22):
            ang = a - math.pi / 2
            outer.append((cx + math.cos(ang) * (185 + ver * 8), cy + 30 + math.sin(ang) * 175))
            inner.append((cx + math.cos(ang) * 102, cy + 45 + math.sin(ang) * 95))
        draw_cel_poly(im, outer + list(reversed(inner)), AZURE_BASE, AZURE_SHADE, AZURE_LIGHT, outline_w=8)
        pod = [(cx, cy - 85), (cx + 72, cy), (cx + 52, cy + 125), (cx - 52, cy + 125), (cx - 72, cy)]
        draw_cel_poly(im, pod, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=8)
        orb = [(cx + math.cos(a) * 44, cy + 10 + math.sin(a) * 44) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
        draw_cel_poly(im, orb, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=6)

    else:
        # Archetype 4: Twin-Pod Linked Satellite
        sep = 112 + ver * 14
        bar = [(cx - sep, cy - 34), (cx + sep, cy - 34), (cx + sep, cy + 38), (cx - sep, cy + 38)]
        draw_cel_poly(im, bar, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=7)
        draw_gun_barrel(im, cx - sep, 55, cy - 95, 26, outline_w=6)
        draw_gun_barrel(im, cx + sep, 55, cy - 95, 26, outline_w=6)
        pod_r = [(cx + sep, cy - 115), (cx + sep + 58, cy - 45), (cx + sep + 54, cy + 95), (cx + sep, cy + 138), (cx + sep - 52, cy + 95), (cx + sep - 52, cy - 45)]
        draw_sym_cel(im, pod_r, cx, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=8)
        core = [(cx + math.cos(a) * 48, cy + math.sin(a) * 48) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
        draw_cel_poly(im, core, CYAN_BASE, CYAN_SHADE, CYAN_WHITE, outline_w=6)

    return im


def render_bullet(kind):
    """Render 1 of 8 player bullets/beams at 4x resolution (2.5D glowing plasma & metallic rockets, zero dark cartoon border)."""
    if kind in ("beam", "beamheavy"):
        W, H = 128, 2048
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx = np.abs(xx - (W - 1) * 0.5)
        phase = 2.0 * math.pi * (yy % 256.0) / 256.0
        wave = np.sin(phase) * (3.5 if kind == "beam" else 6.5)
        sigma = (22.0 if kind == "beam" else 28.0) + wave

        corona = np.exp(-((dx / sigma) ** 2) * 1.45)
        mid = np.exp(-((dx / (sigma * 0.52)) ** 2) * 1.8)
        core = np.exp(-((dx / (sigma * 0.24)) ** 2) * 2.2)

        arr = np.zeros((H, W, 4), dtype=np.float32)
        c_out = np.array([18.0, 118.0, 255.0] if kind == "beam" else [255.0, 168.0, 16.0])
        c_mid = np.array([0.0, 236.0, 255.0] if kind == "beam" else [255.0, 232.0, 96.0])
        rgb = c_out[None, None, :] * (1.0 - mid[:, :, None]) + c_mid[None, None, :] * mid[:, :, None]
        if kind == "beamheavy":
            helix = np.exp(-(((xx - ((W - 1) * 0.5 + np.sin(phase * 2.0) * 18.0)) / 7.5) ** 2))
            rgb = np.clip(rgb + helix[:, :, None] * np.array([0.0, 180.0, 255.0])[None, None, :] * 0.65, 0.0, 255.0)
        rgb = rgb * (1.0 - core[:, :, None]) + 255.0 * core[:, :, None]
        alpha = np.clip(corona * 255.0, 0.0, 255.0)
        alpha[:, 0] = 0.0
        alpha[:, -1] = 0.0
        arr[:, :, :3] = np.clip(rgb, 0.0, 255.0)
        arr[:, :, 3] = alpha
        return Image.fromarray(np.round(arr).astype(np.uint8), mode="RGBA")

    S = 128
    cx, cy = S * 0.5, S * 0.5
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    if kind == "dronebolt":
        pbr25d.draw_25d_plasma_bloom(im, cx, cy, 30, 52, (0, 224, 255), strength=0.95)
        pts = [(cx, 12), (cx + 22, 46), (cx + 14, 112), (cx, 98), (cx - 14, 112), (cx - 22, 46)]
        pbr25d.draw_25d_glass_dome(im, pts, core_rgb=(120, 250, 255), deep_rgb=(0, 112, 210))
    elif kind == "plasmaorb":
        pbr25d.draw_25d_plasma_bloom(im, cx, cy, 48, 48, (0, 226, 255), strength=0.98)
        pts = [(cx + math.cos(a) * 34, cy + math.sin(a) * 34) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        pbr25d.draw_25d_glass_dome(im, pts, core_rgb=(180, 255, 255), deep_rgb=(12, 118, 232))
    elif kind == "missile":
        pbr25d.draw_25d_plasma_bloom(im, cx, 108, 18, 22, (255, 196, 24), strength=0.95)
        fin = [(cx - 36, 82), (cx + 36, 82), (cx + 28, 106), (cx - 28, 106)]
        pbr25d.draw_25d_metal_poly(im, fin, TANG_BASE, TANG_SHADE, GOLD_LIGHT, metallic=0.88, greebles=False)
        body = [(cx, 10), (cx + 21, 38), (cx + 21, 96), (cx - 21, 96), (cx - 21, 38)]
        pbr25d.draw_25d_metal_poly(im, body, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, metallic=0.90, greebles=False)
        head = [(cx, 10), (cx + 19, 38), (cx - 19, 38)]
        pbr25d.draw_25d_metal_poly(im, head, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, metallic=0.92, greebles=False)
    elif kind == "boltmk5":
        pbr25d.draw_25d_plasma_bloom(im, cx, cy, 44, 52, (255, 204, 24), strength=0.92)
        pts = [(cx, 10), (cx + 38, 54), (cx + 22, 72), (cx + 16, 114), (cx, 96), (cx - 16, 114), (cx - 22, 72), (cx - 38, 54)]
        pbr25d.draw_25d_metal_poly(im, pts, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, metallic=0.92, greebles=False)
    elif kind == "childbolt":
        pbr25d.draw_25d_plasma_bloom(im, cx, cy, 34, 48, (0, 232, 255), strength=0.95)
        pts = [(cx, 16), (cx + 26, cy), (cx, 112), (cx - 26, cy)]
        pbr25d.draw_25d_glass_dome(im, pts, core_rgb=(160, 252, 255), deep_rgb=(0, 128, 224))
    else:  # beamflare
        pbr25d.draw_25d_plasma_bloom(im, cx, cy, 48, 48, (16, 238, 176), strength=0.96)
        pts = [(cx + math.cos(k * math.pi / 8) * (48 if k % 2 == 0 else 16), cy + math.sin(k * math.pi / 8) * (48 if k % 2 == 0 else 16)) for k in range(16)]
        pbr25d.draw_25d_glass_dome(im, pts, core_rgb=(190, 255, 232), deep_rgb=(8, 148, 108))
    return im


def render_fx(kind):
    """Render 1 of 2 player FX sprites at 512x512 (volumetric plasma plume & starburst, zero cartoon outline)."""
    S = 512
    cx, cy = S * 0.5, S * 0.5
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    arr = np.zeros((S, S, 4), dtype=np.float32)

    if kind == "engineplume":
        t_y = np.clip((yy - 36.0) / 440.0, 0.0, 1.0)
        width_profile = (1.0 - t_y ** 1.25) * 92.0 * (0.65 + 0.55 * np.sin(np.clip(t_y * math.pi, 0.0, math.pi)))
        dx = np.abs(xx - cx) / np.maximum(width_profile, 2.0)
        plume = np.exp(-(dx * dx) * 1.4) * np.clip(1.0 - t_y, 0.0, 1.0) * (yy >= 36.0)
        core = np.exp(-(dx * dx) * 4.5) * np.clip(1.0 - t_y * 1.35, 0.0, 1.0) * (yy >= 40.0)
        diamonds = np.exp(-(((yy - 145.0) / 22.0) ** 2)) + np.exp(-(((yy - 235.0) / 18.0) ** 2)) * 0.8 + np.exp(-(((yy - 315.0) / 14.0) ** 2)) * 0.6
        core = np.clip(core + diamonds * np.exp(-(dx * dx) * 6.0) * 0.65, 0.0, 1.0)
        c_outer = np.array([255.0, 108.0, 18.0])
        c_mid = np.array([255.0, 214.0, 38.0])
        rgb = c_outer[None, None, :] * (1.0 - plume[:, :, None]) + c_mid[None, None, :] * plume[:, :, None]
        rgb = rgb * (1.0 - core[:, :, None]) + 255.0 * core[:, :, None]
        arr[:, :, :3] = np.clip(rgb, 0, 255)
        arr[:, :, 3] = np.clip(plume * 255.0, 0, 255)
    else:
        rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        ang = np.arctan2(yy - cy, xx - cx)
        rays8 = (0.5 + 0.5 * np.cos(ang * 8.0)) ** 3.2 * np.exp(-((rr / 195.0) ** 2))
        ring = np.exp(-(((rr - 162.0) / 14.0) ** 2)) * 0.65
        core = np.exp(-((rr / 76.0) ** 2))
        a = np.clip(rays8 + ring + core, 0.0, 1.0)
        wh = np.exp(-((rr / 48.0) ** 2))
        c_glow = np.array([0.0, 228.0, 255.0])
        rgb = c_glow[None, None, :] * (1.0 - wh[:, :, None]) + 255.0 * wh[:, :, None]
        arr[:, :, :3] = np.clip(rgb, 0, 255)
        arr[:, :, 3] = np.clip(a * 255.0, 0, 255)
    return Image.fromarray(np.round(arr).astype(np.uint8), "RGBA")


def measure_alpha_sprite(im):
    """Plan §4.9 exact measurement on PNG RGBA with mask alpha > 127."""
    arr = np.asarray(im, dtype=np.float32)
    mask = arr[:, :, 3] > 127.0
    total_px = arr.shape[0] * arr.shape[1]
    n = int(mask.sum())
    if n == 0:
        return {"colors_q32": 0, "val": 0.0, "val_std": 0.0, "dark": 0.0, "chroma": 0.0, "fill": 0.0}
    rgb = arr[:, :, :3][mask]
    q = (rgb.astype(np.uint8) // 8)
    colors_q32 = int(np.unique(q[:, 0].astype(np.int32) * 1024 + q[:, 1].astype(np.int32) * 32 + q[:, 2].astype(np.int32)).size)
    mx = rgb.max(axis=1)
    mn = rgb.min(axis=1)
    v = mx / 255.0
    chroma = (mx - mn) / 255.0
    dark = float((mx < 45.0).mean())
    return {
        "colors_q32": colors_q32,
        "val": round(float(v.mean()), 3),
        "val_std": round(float(v.std()), 3),
        "dark": round(dark, 3),
        "chroma": round(float(chroma.mean()), 3),
        "fill": round(n / total_px, 3),
    }


def save_unit(canvas_4x, master_size, export_size, rel_subpath, row_id, batch, unit_no, planner_base, variant, target_px, recipe):
    master_rel = f"masters/{rel_subpath}"
    sprite_rel = f"sprites/{rel_subpath}"
    master_full = os.path.join(HERE, master_rel)
    sprite_full = os.path.join(HERE, sprite_rel)
    os.makedirs(os.path.dirname(master_full), exist_ok=True)
    os.makedirs(os.path.dirname(sprite_full), exist_ok=True)

    master_im = downsample_straight_rgba(canvas_4x, master_size)
    sprite_im = downsample_straight_rgba(canvas_4x, export_size)

    # Verify 4 corners have alpha == 0 for non-beam sprites (beams also have x=0 & x=W-1 alpha==0)
    sa = np.asarray(sprite_im)[:, :, 3]
    assert sa[0, 0] == 0 and sa[0, -1] == 0 and sa[-1, 0] == 0 and sa[-1, -1] == 0, f"Corner alpha != 0 in {sprite_rel}"

    master_im.save(master_full, "PNG", compress_level=9)
    sprite_im.save(sprite_full, "PNG", compress_level=9)

    m = measure_alpha_sprite(sprite_im)
    return {
        "row_id": row_id,
        "batch": batch,
        "unit_no": str(unit_no),
        "planner_base": planner_base,
        "variant": variant,
        "target_px": target_px,
        "delivered_px": f"{export_size[0]}x{export_size[1]}",
        "master_px": f"{master_size[0]}x{master_size[1]}",
        "source": master_rel,
        "file": sprite_rel,
        "license": LICENSE_NOTE,
        "author": AUTHOR_BRANCH,
        "recipe": recipe,
        "bytes": os.path.getsize(sprite_full),
        **m,
    }


def main():
    records = []
    ship_fams = ["windfang", "solarviper", "skybastion", "aerofalcon", "novaarc"]

    # 1. P-SHIP: 25 units
    for i in range(1, 26):
        fam_name = ship_fams[(i - 1) // 5]
        sub_no = ((i - 1) % 5) + 1
        c4 = render_ship(i)
        rec = save_unit(
            c4, (512, 512), (256, 256),
            f"ships/player_ship_{i:02d}_256@solar.png",
            "AP-0016", "P-SHIP", i, "GLYPH-ship-10001..10999",
            f"{fam_name}-{sub_no}", 256, "b_ship_pearl_azure",
        )
        records.append(rec)

    # 2. P-DRONE: 13 units
    drone_fams = ["shieldpod", "miniwing", "hexgyro", "crescentarc", "twinpod"]
    for i in range(1, 14):
        fam_name = drone_fams[(i - 1) % 5]
        c4 = render_drone(i)
        rec = save_unit(
            c4, (256, 256), (128, 128),
            f"drones/player_drone_{i:02d}_128@cyan.png",
            "AP-0011", "P-DRONE", i, "GLYPH-drone-20001..20013",
            f"{fam_name}-{(i - 1) // 5 + 1}", 128, "b_drone_pearl_gold",
        )
        records.append(rec)

    # 3. P-BULLET: 8 units
    bullet_specs = [
        ("AP-0002", "dronebolt", "drone_laser", (64, 64), (32, 32), "player_bullet_dronebolt_32@cyan.png"),
        ("AP-0003", "beam", "laser", (64, 1024), (32, 512), "player_bullet_beam_32x512@cyan.png"),
        ("AP-0004", "beamheavy", "laserbeam_player", (64, 1024), (32, 512), "player_bullet_beamheavy_32x512@solar.png"),
        ("AP-0005", "plasmaorb", "plasmagun", (64, 64), (32, 32), "player_bullet_plasmaorb_32@cyan.png"),
        ("AP-0006", "missile", "rocket", (64, 64), (32, 32), "player_bullet_missile_32@solar.png"),
        ("AP-0007", "boltmk5", "blt_player_5.", (64, 64), (32, 32), "player_bullet_boltmk5_32@solar.png"),
        ("AP-0008", "childbolt", "drone_laser_child", (64, 64), (32, 32), "player_bullet_childbolt_32@cyan.png"),
        ("AP-0009", "beamflare", "plasma_beam_flare_green", (64, 64), (32, 32), "player_bullet_beamflare_32@emerald.png"),
    ]
    for row_id, kind, pbase, msz, esz, fname in bullet_specs:
        c4 = render_bullet(kind)
        rec = save_unit(
            c4, msz, esz, f"bullets/{fname}",
            row_id, "P-BULLET", kind, pbase, kind, 32, "b_bullet_neon_cyan",
        )
        records.append(rec)

    # 4. P-FX: 2 units
    fx_specs = [
        ("AP-0013", "engineplume", "afterburner", "player_fx_engineplume_128@solar.png"),
        ("AP-0014", "muzzleflash", "shooter", "player_fx_muzzleflash_128@cyan.png"),
    ]
    for row_id, kind, pbase, fname in fx_specs:
        c4 = render_fx(kind)
        rec = save_unit(
            c4, (256, 256), (128, 128), f"fx/{fname}",
            row_id, "P-FX", kind, pbase, kind, 128, "b_fx_neon_pop",
        )
        records.append(rec)

    assert len(records) == 48, f"Expected 48 PLAYER units, got {len(records)}"

    with open(os.path.join(HERE, "w1b_units.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, indent=1, ensure_ascii=False)

    fields = list(records[0].keys())
    with open(os.path.join(HERE, "w1b_units.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)

    print(f"SUCCESS: {len(records)} W1 PLAYER units exported (masters/ + sprites/) -> w1b_units.json & .csv")


if __name__ == "__main__":
    main()
