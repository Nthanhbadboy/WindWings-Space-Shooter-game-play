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
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHOR_BRANCH = "arena/eca8588b-windwings-space-shooter-game-p"
LICENSE_NOTE = "chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)"

# Solar Neon Arcade-Pop Palette (Variant B)
NAVY_OUTLINE = (8, 20, 62, 255)      # #08143E — crisp cel outline (not black)
PEARL_LIGHT  = (250, 253, 255, 255)  # sunlit top-left highlight
PEARL_BASE   = (226, 238, 255, 255)  # pearl-white armor mid
PEARL_SHADE  = (176, 202, 242, 255)  # cool sky-blue shadow

AZURE_LIGHT  = (68, 164, 255, 255)   # bright cobalt-cyan highlight
AZURE_BASE   = (24, 108, 242, 255)   # electric cobalt-blue base
AZURE_SHADE  = (14, 62, 168, 255)    # deep royal-blue shade

GOLD_LIGHT   = (255, 244, 132, 255)
GOLD_BASE    = (255, 208, 18, 255)
GOLD_SHADE   = (230, 126, 0, 255)

TANG_LIGHT   = (255, 172, 64, 255)
TANG_BASE    = (255, 106, 12, 255)
TANG_SHADE   = (198, 52, 8, 255)

CYAN_WHITE   = (232, 255, 255, 255)
CYAN_LIGHT   = (112, 252, 255, 255)
CYAN_BASE    = (0, 226, 255, 255)
CYAN_SHADE   = (0, 148, 204, 255)

EMERALD_BASE = (0, 238, 180, 255)
EMER_LIGHT   = (140, 255, 224, 255)
EMER_BASE    = (0, 238, 180, 255)
EMER_SHADE   = (0, 152, 118, 255)
MAGENTA_BASE = (255, 42, 146, 255)


def downsample_straight_rgba(im, target_size):
    """Downsample RGBA image via premultiplied Lanczos, then unpremultiply back to
    straight RGBA so silhouette borders have ZERO dark or white fringes (Gate A1)."""
    if im.size == target_size:
        return im.copy()
    arr = np.asarray(im, dtype=np.float32)
    a = arr[:, :, 3:4] / 255.0
    premul = np.concatenate([arr[:, :, :3] * a, arr[:, :, 3:4]], axis=2)
    pm_im = Image.fromarray(np.clip(np.round(premul), 0, 255).astype(np.uint8), mode="RGBA")
    pm_small = pm_im.resize(target_size, Image.LANCZOS)
    s_arr = np.asarray(pm_small, dtype=np.float32)
    sa = s_arr[:, :, 3:4] / 255.0
    rgb = np.where(sa > 1e-3, s_arr[:, :, :3] / np.maximum(sa, 1e-3), 0.0)
    out = np.concatenate([np.clip(np.round(rgb), 0, 255), np.clip(np.round(s_arr[:, :, 3:4]), 0, 255)], axis=2)
    # Zero out tiny sub-threshold alpha dust at extreme outer corners
    out[out[:, :, 3] < 4] = 0
    return Image.fromarray(out.astype(np.uint8), mode="RGBA")


def draw_cel_poly(canvas, pts, base_c, shade_c, light_c, outline_w=6, outline_c=NAVY_OUTLINE):
    """Draw a 3-tone stepped cel-shaded polygon lit from 30 deg top-left (-0.75, -0.66)."""
    if len(pts) < 3:
        return
    W, H = canvas.size
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(pts, fill=255)

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = max(0, int(min(xs)) - outline_w - 4), max(0, int(min(ys)) - outline_w - 4)
    x1, y1 = min(W, int(max(xs)) + outline_w + 5), min(H, int(max(ys)) + outline_w + 5)
    if x1 <= x0 or y1 <= y0:
        return

    sub_m = np.asarray(mask.crop((x0, y0, x1, y1)), dtype=np.uint8)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    span = max(1.0, ((max(xs) - min(xs)) + (max(ys) - min(ys))) * 0.5)
    cx, cy = (min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5
    # Directional coordinate along top-left -> bottom-right axis
    proj = ((xx - cx) * 0.72 + (yy - cy) * 0.69) / (span * 0.48)

    patch = np.zeros((y1 - y0, x1 - x0, 4), dtype=np.uint8)
    lit = proj < -0.22
    shd = proj > 0.26
    mid = (~lit) & (~shd)

    for cond, col in [(lit, light_c), (mid, base_c), (shd, shade_c)]:
        sel = cond & (sub_m > 127)
        patch[sel] = col

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(Image.fromarray(patch, mode="RGBA"), (x0, y0))

    if outline_w > 0:
        od = ImageDraw.Draw(layer)
        closed = list(pts) + [pts[0]]
        od.line(closed, fill=outline_c, width=outline_w, joint="curve")

    canvas.alpha_composite(layer)


def mirror_pts(pts, cx):
    return [(2 * cx - x, y) for (x, y) in pts]


def draw_sym_cel(canvas, right_pts, cx, base_c, shade_c, light_c, outline_w=6):
    """Draw mirrored left & right cel-shaded polygons."""
    left_pts = mirror_pts(right_pts, cx)
    draw_cel_poly(canvas, left_pts, base_c, shade_c, light_c, outline_w=outline_w)
    draw_cel_poly(canvas, right_pts, base_c, shade_c, light_c, outline_w=outline_w)


def draw_canopy(canvas, cx, y_top, y_bot, half_w, outline_w=6):
    """Draw signature gleaming Neon-Cyan crystal cockpit canopy with orange-gold collar."""
    h = y_bot - y_top
    collar = [
        (cx, y_top - h * 0.16),
        (cx + half_w * 1.28, y_top + h * 0.42),
        (cx + half_w * 1.12, y_bot + h * 0.14),
        (cx, y_bot + h * 0.24),
        (cx - half_w * 1.12, y_bot + h * 0.14),
        (cx - half_w * 1.28, y_top + h * 0.42),
    ]
    draw_cel_poly(canvas, collar, TANG_BASE, TANG_SHADE, GOLD_BASE, outline_w=outline_w)

    glass = [
        (cx, y_top),
        (cx + half_w * 0.92, y_top + h * 0.36),
        (cx + half_w * 0.78, y_bot - h * 0.12),
        (cx, y_bot),
        (cx - half_w * 0.78, y_bot - h * 0.12),
        (cx - half_w * 0.92, y_top + h * 0.36),
    ]
    draw_cel_poly(canvas, glass, CYAN_BASE, CYAN_SHADE, CYAN_LIGHT, outline_w=outline_w)

    # Specular white-cyan glint on upper-left facet
    d = ImageDraw.Draw(canvas)
    glint = [
        (cx - half_w * 0.12, y_top + h * 0.12),
        (cx - half_w * 0.56, y_top + h * 0.38),
        (cx - half_w * 0.38, y_top + h * 0.66),
        (cx - half_w * 0.08, y_top + h * 0.46),
    ]
    d.polygon(glint, fill=CYAN_WHITE)


def draw_gun_barrel(canvas, x, y_tip, y_base, w, outline_w=5):
    pts = [
        (x - w * 0.45, y_tip),
        (x + w * 0.45, y_tip),
        (x + w * 0.62, y_base),
        (x - w * 0.62, y_base),
    ]
    draw_cel_poly(canvas, pts, PEARL_BASE, AZURE_SHADE, PEARL_LIGHT, outline_w=outline_w)
    tip = [
        (x - w * 0.55, y_tip - w * 0.3),
        (x + w * 0.55, y_tip - w * 0.3),
        (x + w * 0.55, y_tip + w * 0.4),
        (x - w * 0.55, y_tip + w * 0.4),
    ]
    draw_cel_poly(canvas, tip, CYAN_BASE, CYAN_SHADE, CYAN_WHITE, outline_w=max(3, outline_w - 1))


def draw_thruster(canvas, x, y_top, y_bot, w, outline_w=5):
    bell = [
        (x - w * 0.48, y_top),
        (x + w * 0.48, y_top),
        (x + w * 0.66, y_bot),
        (x - w * 0.66, y_bot),
    ]
    draw_cel_poly(canvas, bell, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=outline_w)
    d = ImageDraw.Draw(canvas)
    d.ellipse([x - w * 0.42, y_bot - w * 0.28, x + w * 0.42, y_bot + w * 0.28], fill=CYAN_LIGHT, outline=NAVY_OUTLINE, width=max(2, outline_w // 2))


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


def render_ship(unit_idx):
    """Render 1 of 25 distinct Solar Neon Arcade-Pop starfighters at 1024x1024 (4x of 256)."""
    S = 1024
    cx = S * 0.5
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fam = (unit_idx - 1) // 5       # 0..4
    sub = (unit_idx - 1) % 5        # 0..4

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


def render_drone(unit_idx):
    """Render 1 of 13 distinct Orbital Wingman Drones at 512x512 (4x of 128)."""
    S = 512
    cx, cy = S * 0.5, S * 0.52
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fam = (unit_idx - 1) % 5
    ver = (unit_idx - 1) // 5

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
    """Render 1 of 8 player bullets/beams at 4x resolution."""
    if kind in ("beam", "beamheavy"):
        # 4x of 32x512 = 128x2048; period = 256px (64px at 1x) -> 100% seamless vertical tile!
        W, H = 128, 2048
        yy, xx = np.mgrid[0:H, 0:W]
        dx = np.abs(xx - (W - 1) * 0.5)
        phase = 2.0 * math.pi * (yy % 256) / 256.0
        wave = np.sin(phase) * (5.0 if kind == "beam" else 9.0)
        half_w = (36.0 if kind == "beam" else 48.0) + wave

        arr = np.zeros((H, W, 4), dtype=np.uint8)
        inside = dx <= half_w
        rim = inside & (dx > half_w - 11.0)
        outer = inside & (~rim) & (dx > half_w * 0.52)
        mid = inside & (dx <= half_w * 0.52) & (dx > half_w * 0.24)
        core = inside & (dx <= half_w * 0.24)

        arr[rim] = NAVY_OUTLINE
        if kind == "beam":
            arr[outer] = AZURE_BASE
            arr[mid] = CYAN_BASE
        else:
            # Heavy overdrive beam: golden-cyan energetic edge + blazing white-cyan core
            helix = np.abs(xx - ((W - 1) * 0.5 + np.sin(phase * 2.0) * 22.0)) < 10.0
            arr[outer] = GOLD_BASE
            arr[mid] = CYAN_BASE
            arr[inside & (~rim) & helix] = GOLD_LIGHT
        arr[core] = CYAN_WHITE
        return Image.fromarray(arr, mode="RGBA")

    # 32x32 bullets rendered at 128x128 (4x)
    S = 128
    cx, cy = S * 0.5, S * 0.5
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    if kind == "dronebolt":
        pts = [(cx, 10), (cx + 28, 46), (cx + 18, 114), (cx, 100), (cx - 18, 114), (cx - 28, 46)]
        draw_cel_poly(im, pts, CYAN_BASE, AZURE_SHADE, CYAN_WHITE, outline_w=8)
        d.polygon([(cx, 24), (cx + 10, 52), (cx, 84), (cx - 10, 52)], fill=CYAN_WHITE)
    elif kind == "plasmaorb":
        pts = [(cx + math.cos(a) * 48, cy + math.sin(a) * 48) for a in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
        draw_cel_poly(im, pts, CYAN_BASE, AZURE_BASE, CYAN_LIGHT, outline_w=9)
        d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=CYAN_WHITE)
        for ang in (0, math.pi / 2):
            dx, dy = math.cos(ang) * 38, math.sin(ang) * 38
            d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=PEARL_LIGHT, width=6)
    elif kind == "missile":
        fin = [(cx - 36, 86), (cx + 36, 86), (cx + 28, 108), (cx - 28, 108)]
        draw_cel_poly(im, fin, TANG_BASE, TANG_SHADE, GOLD_BASE, outline_w=7)
        body = [(cx, 8), (cx + 22, 38), (cx + 22, 96), (cx - 22, 96), (cx - 22, 38)]
        draw_cel_poly(im, body, PEARL_BASE, PEARL_SHADE, PEARL_LIGHT, outline_w=8)
        head = [(cx, 8), (cx + 20, 38), (cx - 20, 38)]
        draw_cel_poly(im, head, TANG_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=7)
        d.polygon([(cx - 12, 98), (cx + 12, 98), (cx, 122)], fill=GOLD_LIGHT)
    elif kind == "boltmk5":
        pts = [(cx, 8), (cx + 42, 54), (cx + 26, 72), (cx + 18, 116), (cx, 98), (cx - 18, 116), (cx - 26, 72), (cx - 42, 54)]
        draw_cel_poly(im, pts, GOLD_BASE, TANG_SHADE, GOLD_LIGHT, outline_w=8)
        d.polygon([(cx, 22), (cx + 18, 52), (cx, 84), (cx - 18, 52)], fill=CYAN_WHITE)
    elif kind == "childbolt":
        pts = [(cx, 12), (cx + 34, cy), (cx, 116), (cx - 34, cy)]
        draw_cel_poly(im, pts, CYAN_BASE, AZURE_BASE, CYAN_LIGHT, outline_w=8)
        d.polygon([(cx, 32), (cx + 15, cy), (cx, 96), (cx - 15, cy)], fill=CYAN_WHITE)
    else:  # beamflare
        pts = []
        for k in range(16):
            r = 52 if k % 2 == 0 else 22
            a = k * math.pi / 8
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        draw_cel_poly(im, pts, EMERALD_BASE, CYAN_SHADE, CYAN_WHITE, outline_w=7)
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=PEARL_LIGHT)
    return im


def render_fx(kind):
    """Render 1 of 2 player FX sprites at 512x512 (4x of 128)."""
    S = 512
    cx, cy = S * 0.5, S * 0.5
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    if kind == "engineplume":
        # Downward roaring solar-plasma afterburner plume
        outer = [
            (cx - 72, 42), (cx + 72, 42),
            (cx + 108, 165), (cx + 68, 325),
            (cx, 482),
            (cx - 68, 325), (cx - 108, 165),
        ]
        draw_cel_poly(im, outer, TANG_BASE, MAGENTA_BASE, GOLD_BASE, outline_w=8)
        mid = [
            (cx - 50, 48), (cx + 50, 48),
            (cx + 72, 150), (cx + 38, 285),
            (cx, 405),
            (cx - 38, 285), (cx - 72, 150),
        ]
        draw_cel_poly(im, mid, GOLD_BASE, TANG_BASE, GOLD_LIGHT, outline_w=0)
        core = [(cx - 28, 52), (cx + 28, 52), (cx + 36, 130), (cx, 295), (cx - 36, 130)]
        d.polygon(core, fill=CYAN_WHITE)
        # Shock diamonds
        for yy, rw in [(155, 22), (245, 16), (325, 11)]:
            d.polygon([(cx, yy - rw), (cx + rw * 1.4, yy), (cx, yy + rw), (cx - rw * 1.4, yy)], fill=PEARL_LIGHT)
    else:
        # Muzzle flash: symmetrical 8-point neon-cyan + white starburst + shockwave ring
        d.ellipse([cx - 175, cy - 175, cx + 175, cy + 175], outline=CYAN_BASE, width=14)
        pts = []
        for k in range(16):
            r = (225 if k % 4 == 0 else 155) if k % 2 == 0 else 56
            a = k * math.pi / 8
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        draw_cel_poly(im, pts, CYAN_BASE, AZURE_BASE, CYAN_LIGHT, outline_w=7)
        in_pts = []
        for k in range(16):
            r = 140 if k % 2 == 0 else 36
            a = k * math.pi / 8
            in_pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        d.polygon(in_pts, fill=CYAN_WHITE)
    return im


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
