#!/usr/bin/env python3
"""
W1 PLAYER sprite builder — WindWings (Godot port) · vai Art-designer · arena/5438fec9

48 units from art-planner.csv @971a7eea8 (branch 1b836828):
  AP-0016 P-SHIP   x25  target_px 256  recipe ship
  AP-0011 P-DRONE  x13  target_px 128  recipe drone
  AP-0002..0009 P-BULLET x8 target_px 32 recipe bullet (beams 32x512 per plan §4.7)
  AP-0013/0014 P-FX x2  target_px 128  recipe fx

Method: original sprites drawn programmatically in the exact Ink & Ember
hex palette (plan §4.4) at recipe area ratios (§4.5), 3 tones + accent + rim (§4.6),
supersampled x4 then downscaled, finished with the shared 2.5D render pass
(../render25d.py: panel gradients, bevel, AO, rim-light, panel seams, gloss)
per STYLE-CORRECTION lan-149. No original-game art, no original filenames (§4.7).
Every sprite is measured with the §4.9 protocol (alpha>0.5 mask) and gated G-A (§4.10).

Run: python3 build_w1.py   (needs Pillow). Deterministic (fixed seeds).
"""
import csv
import json
import math
import os
import random
import colorsys
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from render25d import render_v2  # 2.5D render pass (STYLE-CORRECTION lan-149 redo)
SS = 4  # supersample

# Ink & Ember — ART_REDRAW_PLAN §4.4
INK900 = (0x0B, 0x0E, 0x14)
INK700 = (0x16, 0x1C, 0x26)
INK500 = (0x2A, 0x34, 0x42)
INK300 = (0x4A, 0x56, 0x6B)
PAPER = (0xE8, 0xE3, 0xD9)
WHITE = (0xFF, 0xFF, 0xFF)
EMBER = (0xFF, 0x5A, 0x2B)
EMBERDIM = (0x8C, 0x2F, 0x17)
TEAL = (0x4F, 0xD1, 0xC5)
GOLD = (0xF5, 0xC5, 0x18)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def finish(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


def add_grain(im, amount=0.05, seed=7):
    """Paper grain: luminance noise blended inside alpha>0 area (plan §4.6: <=6%)."""
    rng = random.Random(seed)
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0:
                n = 1.0 + rng.uniform(-amount, amount)
                px[x, y] = (min(255, int(r * n)), min(255, int(g * n)), min(255, int(b * n)), a)
    return im


def apply_light(im, mask, strength=0.30):
    """Single light from top-left 30deg: diagonal white->black gradient inside mask."""
    w, h = im.size
    grad = Image.new("L", (w, h), 0)
    gd = grad.load()
    for y in range(h):
        for x in range(w):
            t = (x / w * 0.6 + y / h * 0.4)  # 0 top-left .. 1 bottom-right
            gd[x, y] = int(255 * (1 - t))
    white = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    black = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    m = mask.point(lambda v: int(v * strength))
    im.paste(Image.composite(white, black, grad), (0, 0),
             Image.composite(m, Image.new("L", (w, h), 0), grad.point(lambda v: 255 if v > 127 else 0)))
    # simpler robust pass: multiply-ish light via per-pixel on downscaled later; keep subtle
    return im


def light_pass(im, hi=0.16, lo=0.20):
    """Cheap per-pixel diagonal light on final-size sprite (masked by alpha>0)."""
    w, h = im.size
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a >= 200:
                t = x / w * 0.55 + y / h * 0.45
                f = 1.0 + hi * (0.5 - t) * 2 - lo * max(0.0, t - 0.5)
                f = max(0.78, min(1.30, f))  # clamp: keep INK500 (max 66) above dark<45 line
                px[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
    return im


def mirror_pts(half, cx):
    """half: [(x,y)...] right side from top-center to bottom-center. Return full polygon."""
    left = [(2 * cx - x, y) for x, y in reversed(half)]
    return half + left


# ---------------------------------------------------------------- ships
# Hull families (half-outline params in unit box: x=0 center..0.5 edge, y=0 top..1 bottom)
SHIP_FAMILIES = [
    # name, nose_y, half-points (x,y) nose->tail-center
    ("dart", [(0.00, 0.03), (0.07, 0.22), (0.11, 0.40), (0.13, 0.52), (0.40, 0.74),
              (0.36, 0.80), (0.15, 0.78), (0.13, 0.92), (0.05, 0.95), (0.00, 0.90)]),
    ("delta", [(0.00, 0.05), (0.08, 0.20), (0.12, 0.34), (0.46, 0.82), (0.42, 0.88),
               (0.14, 0.86), (0.10, 0.94), (0.00, 0.92)]),
    ("broad", [(0.00, 0.08), (0.10, 0.18), (0.17, 0.30), (0.19, 0.44), (0.47, 0.60),
               (0.44, 0.72), (0.20, 0.76), (0.17, 0.90), (0.06, 0.94), (0.00, 0.90)]),
    ("crescent", [(0.00, 0.06), (0.07, 0.20), (0.11, 0.36), (0.13, 0.46), (0.46, 0.34),
                  (0.48, 0.44), (0.22, 0.66), (0.15, 0.88), (0.06, 0.94), (0.00, 0.88)]),
    ("twinboom", [(0.00, 0.04), (0.06, 0.20), (0.10, 0.38), (0.11, 0.55), (0.34, 0.70),
                  (0.32, 0.78), (0.12, 0.76), (0.11, 0.92), (0.04, 0.94), (0.00, 0.86)]),
]


def draw_ship(idx, fam_i, var_i):
    S = 256
    im = canvas(S, S)
    d = ImageDraw.Draw(im)
    W = H = S * SS
    cx = W / 2
    rng = random.Random(1000 + idx)
    fam_name, pts = SHIP_FAMILIES[fam_i]
    # variant jitter (deterministic): scale width/wing reach, nose length
    w_scale = 0.88 + 0.055 * var_i
    pts2 = []
    for (x, y) in pts:
        x2 = x * w_scale * (1.0 + (0.05 if x > 0.3 and var_i % 2 else 0.0))
        y2 = y + (0.03 * (var_i - 2) if y < 0.3 else (0.035 * (var_i - 2) if x > 0.3 else 0.0))
        pts2.append((cx + x2 * W * 0.88, 0.04 * H + y2 * H * 0.92))
    hull = mirror_pts(pts2, cx)

    # negative edge: ink900 silhouette offset down-right 1px final (shaded side only, §4.6)
    off = [(x + 1 * SS, y + 1 * SS) for x, y in hull]
    d.polygon(off, fill=INK900 + (255,))
    # hull base INK300 (recipe: ink300 40 = largest share), INK500 = secondary plates 25
    d.polygon(hull, fill=INK300 + (255,))
    # fuselage spine (bright top plate, paper-mixed — feeds paper 10 + val_std)
    spine_w = W * (0.085 + 0.012 * (var_i % 3))
    spine = [(cx, H * 0.07), (cx + spine_w, H * 0.38), (cx + spine_w * 0.8, H * 0.78),
             (cx, H * 0.84), (cx - spine_w * 0.8, H * 0.78), (cx - spine_w, H * 0.38)]
    d.polygon(spine, fill=mix(INK300, PAPER, 0.27) + (255,))
    d.line([(cx, H * 0.10), (cx, H * 0.30)], fill=PAPER + (255,), width=max(2, int(1.2 * SS)))
    # wing plates INK500 (secondary mass)
    wy = 0.52 + 0.05 * (var_i % 3)
    for sgn in (1, -1):
        plate = [(cx + sgn * W * 0.10, H * (wy - 0.10)), (cx + sgn * W * 0.30 * w_scale, H * (wy + 0.14)),
                 (cx + sgn * W * 0.28 * w_scale, H * (wy + 0.20)), (cx + sgn * W * 0.11, H * (wy + 0.12))]
        d.polygon(plate, fill=INK500 + (255,))
        # small INK700 panel (kept near recipe 8% incl. nozzles+edge) + thin panel line
        pan = [(cx + sgn * W * 0.13, H * (wy + 0.15)), (cx + sgn * W * 0.22 * w_scale, H * (wy + 0.20)),
               (cx + sgn * W * 0.14, H * (wy + 0.23))]
        d.polygon(pan, fill=INK700 + (255,))
        d.line([(cx + sgn * W * 0.11, H * (wy - 0.02)), (cx + sgn * W * 0.29 * w_scale, H * (wy + 0.16))],
               fill=INK500 + (255,), width=SS)
    # twinboom pods
    if fam_name == "twinboom":
        for sgn in (1, -1):
            px0 = cx + sgn * W * 0.20
            d.rounded_rectangle([px0 - W * 0.045, H * 0.52, px0 + W * 0.045, H * 0.90],
                                radius=W * 0.04, fill=INK500 + (255,))
            d.rounded_rectangle([px0 - W * 0.045, H * 0.52, px0 + W * 0.045, H * 0.62],
                                radius=W * 0.04, fill=mix(INK300, PAPER, 0.15) + (255,))
    # canopy (teal <=4% declared rim accent; dark glass + paper glint)
    cy0 = H * (0.30 + 0.03 * (var_i % 2))
    canopy = [(cx, cy0 - H * 0.09), (cx + W * 0.045, cy0 + H * 0.03), (cx + W * 0.035, cy0 + H * 0.11),
              (cx, cy0 + H * 0.14), (cx - W * 0.035, cy0 + H * 0.11), (cx - W * 0.045, cy0 + H * 0.03)]
    d.polygon(canopy, fill=shade(TEAL, 0.55) + (255,))
    d.ellipse([cx - W * 0.018, cy0 - H * 0.02, cx + W * 0.006, cy0 + H * 0.035], fill=TEAL + (255,))
    d.ellipse([cx - W * 0.014, cy0 - H * 0.012, cx - W * 0.002, cy0 + H * 0.012], fill=PAPER + (255,))
    # ember accents: engine nozzles + glows, wingtip stripes, nose stripe variants
    n_eng = 1 + (idx % 3)  # 1..3 nozzles
    eng_xs = [0] if n_eng == 1 else ([-0.09, 0.09] if n_eng == 2 else [-0.13, 0, 0.13])
    for ex in eng_xs:
        exx = cx + ex * W
        d.rounded_rectangle([exx - W * 0.030, H * 0.82, exx + W * 0.030, H * 0.915],
                            radius=W * 0.02, fill=INK700 + (255,))
        d.ellipse([exx - W * 0.023, H * 0.878, exx + W * 0.023, H * 0.932], fill=EMBER + (255,))
        d.ellipse([exx - W * 0.010, H * 0.89, exx + W * 0.010, H * 0.92], fill=mix(PAPER, EMBER, 0.35) + (255,))
    for sgn in (1, -1):
        # wingtip ember cap (bigger — ember must reach ~12% of mask)
        tx = cx + sgn * W * 0.30 * w_scale
        d.polygon([(tx, H * (wy + 0.06)), (tx + sgn * W * 0.10, H * (wy + 0.15)),
                   (tx + sgn * W * 0.085, H * (wy + 0.22)), (tx, H * (wy + 0.17))], fill=EMBER + (255,))
        # ember fuselage side stripe
        d.polygon([(cx + sgn * W * 0.085, H * 0.50), (cx + sgn * W * 0.115, H * 0.52),
                   (cx + sgn * W * 0.105, H * 0.76), (cx + sgn * W * 0.080, H * 0.76)], fill=EMBER + (255,))
        # ember trailing band on wing plate (thinner on narrow variants to hold chroma)
        tf = 0.60 + 0.15 * var_i
        d.polygon([(cx + sgn * W * 0.12, H * (wy + 0.17)), (cx + sgn * W * 0.29 * w_scale, H * (wy + 0.17 + 0.065 * tf)),
                   (cx + sgn * W * 0.28 * w_scale, H * (wy + 0.21 + 0.06 * tf)), (cx + sgn * W * 0.12, H * (wy + 0.17 + 0.04 * tf))],
                  fill=EMBER + (255,))
        # emberdim intake edge
        d.polygon([(cx + sgn * W * 0.12, H * 0.58), (cx + sgn * W * 0.155, H * 0.60),
                   (cx + sgn * W * 0.145, H * 0.72), (cx + sgn * W * 0.12, H * 0.72)], fill=EMBERDIM + (255,))
        # paper leading-edge rim (top-left light: stronger on left wing + nose)
    rim_w = max(2, int(2.0 * SS))
    d.line([(cx, H * 0.06), (cx - W * 0.10, H * 0.36), (cx - W * 0.12, H * 0.50)], fill=PAPER + (255,), width=rim_w)
    d.line([(cx - W * 0.12, H * (wy - 0.08)), (cx - W * 0.33 * w_scale, H * (wy + 0.12))], fill=PAPER + (200,), width=rim_w)
    d.line([(cx, H * 0.06), (cx + W * 0.07, H * 0.30)], fill=mix(PAPER, INK300, 0.4) + (255,), width=max(1, rim_w - 1))

    im = finish(im, S, S)
    im = render_v2(im, key=0.26, bevel=0.06, ao=0.22, rim=0.26, under=0.26,
                   seam=0.36, step=0.24, gloss=0.07)  # 2.5D (replaces flat light_pass)
    im = add_grain(im, 0.037, seed=50 + idx)
    return im, fam_name


# ---------------------------------------------------------------- drones
def draw_drone(idx):
    S = 128
    im = canvas(S, S)
    d = ImageDraw.Draw(im)
    W = H = S * SS
    cx = cy = W / 2
    kind = idx % 5
    v = idx // 5  # 0..2 sub-variant within kind (silhouette variation)
    r = W * 0.30
    # negative edge offset
    # body by kind
    if kind == 0:      # orb + full ring
        ry = r * 0.62 * (0.82 + 0.16 * v)
        d.ellipse([cx - r * 1.25 + 3, cy - ry + 3, cx + r * 1.25 + 3, cy + ry + 3], fill=INK900 + (255,))
        d.ellipse([cx - r * 1.25, cy - ry, cx + r * 1.25, cy + ry], outline=INK300 + (255,), width=int(r * 0.28))
        d.ellipse([cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72], fill=INK300 + (255,))
        d.ellipse([cx - r * 0.50, cy - r * 0.50, cx + r * 0.50, cy + r * 0.50], fill=mix(INK300, PAPER, 0.18) + (255,))
    elif kind == 1:    # hexagon pod
        rot = 90 + 30 * v
        pts = [(cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a)) for a in
               [math.radians(rot + 60 * k) for k in range(6)]]
        d.polygon([(x + 4, y + 5) for x, y in pts], fill=INK900 + (255,))
        d.polygon(pts, fill=INK300 + (255,))
        pts2 = [(cx + r * 0.50 * math.cos(a), cy + r * 0.50 * math.sin(a)) for a in
                [math.radians(rot + 60 * k) for k in range(6)]]
        d.polygon(pts2, fill=INK500 + (255,))
        for sgn in (1, -1):
            d.rectangle([cx + sgn * r * 0.95 - r * 0.10, cy - r * 0.16, cx + sgn * r * 0.95 + r * 0.22, cy + r * 0.16],
                        fill=INK500 + (255,))
    elif kind == 2:    # crescent guard + orb
        a0, a1 = 300 + 12 * v, 240 - 12 * v
        d.pieslice([cx - r * 0.98 + 3, cy - r * 0.98 + 3, cx + r * 0.98 + 3, cy + r * 0.98 + 3],
                   start=a0, end=a1, fill=INK900 + (255,))
        d.pieslice([cx - r * 0.98, cy - r * 0.98, cx + r * 0.98, cy + r * 0.98], start=a0, end=a1, fill=INK500 + (255,))
        d.pieslice([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], start=a0, end=a1, fill=INK300 + (255,))
        d.ellipse([cx - r * 0.60, cy - r * 0.60, cx + r * 0.60, cy + r * 0.60], fill=INK500 + (255,))
        d.ellipse([cx - r * 0.48, cy - r * 0.48, cx + r * 0.48, cy + r * 0.48], fill=mix(INK300, PAPER, 0.25) + (255,))
    elif kind == 3:    # twin pods + bar
        d.rounded_rectangle([cx - r * 1.1 + 4, cy - r * 0.34 + 5, cx + r * 1.1 + 4, cy + r * 0.34 + 5],
                            radius=r * 0.3, fill=INK900 + (255,))
        d.rounded_rectangle([cx - r * 1.1, cy - r * 0.34, cx + r * 1.1, cy + r * 0.34], radius=r * 0.3, fill=INK500 + (255,))
        for sgn in (1, -1):
            px0 = cx + sgn * r * (0.78 + 0.06 * v)
            d.ellipse([px0 - r * 0.42, cy - r * (0.50 + 0.06 * v), px0 + r * 0.42, cy + r * (0.50 + 0.06 * v)], fill=INK300 + (255,))
            grx, gry = r * (0.165 + 0.012 * v), r * (0.23 + 0.015 * v)
            d.ellipse([px0 - grx, cy - gry, px0 + grx, cy + gry], fill=GOLD + (255,))
        d.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30], fill=mix(INK300, PAPER, 0.25) + (255,))
    else:              # capsule vertical
        hh = r * (0.94 + 0.09 * v)
        d.rounded_rectangle([cx - r * 0.62 + 4, cy - hh + 5, cx + r * 0.62 + 4, cy + hh + 5],
                            radius=r * 0.6, fill=INK900 + (255,))
        d.rounded_rectangle([cx - r * 0.62, cy - hh, cx + r * 0.62, cy + hh],
                            radius=r * 0.6, fill=INK300 + (255,))
        d.rounded_rectangle([cx - r * 0.40, cy - r * 0.80, cx + r * 0.40, cy + r * 0.30],
                            radius=r * 0.35, fill=mix(INK500, INK300, 0.45) + (255,))
        for sgn in (1, -1):
            d.polygon([(cx + sgn * r * 0.55, cy + r * 0.55), (cx + sgn * r * 0.95, cy + r * 0.95),
                       (cx + sgn * r * 0.45, cy + r * 0.98)], fill=INK500 + (255,))
    if kind != 3:
        # gold core + paper glint (recipe gold 12 / paper 8)
        cr = r * (0.33 if kind == 2 else 0.35 + 0.01 * (idx // 5))
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=GOLD + (255,))
        d.ellipse([cx - cr * 0.55, cy - cr * 0.62, cx - cr * 0.05, cy - cr * 0.12], fill=PAPER + (255,))
        d.ellipse([cx - cr * 0.18, cy - cr * 0.18, cx + cr * 0.18, cy + cr * 0.18], fill=mix(GOLD, PAPER, 0.25) + (255,))
    # top-left paper rim tick
    d.arc([cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72], start=140, end=235,
          fill=PAPER + (220,), width=max(2, int(1.4 * SS)))
    im = finish(im, S, S)
    im = render_v2(im, key=0.16, bevel=0.05, ao=0.15, rim=0.20, under=0.16,
                   seam=0.28, step=0.18, gloss=0.07)
    im = add_grain(im, 0.03, seed=90 + idx)
    return im, ["orb-ring", "hexpod", "crescent", "twinpod", "capsule"][kind]


# ---------------------------------------------------------------- bullets
def bolt_base():
    return canvas(32, 32)


def draw_bullet(code):
    if code in ("beam", "beamheavy"):
        W, H = 32, 512
        im = canvas(W, H)
        d = ImageDraw.Draw(im)
        wpx, hpx = W * SS, H * SS
        core = 0.30 if code == "beam" else 0.36
        # widths tuned to recipe by area: ink900 ~45-52 / ink300 ~39-47 / emberdim ~9
        d.rectangle([wpx * 0.12, 0, wpx * 0.88, hpx], fill=INK900 + (255,))
        d.rectangle([wpx * (0.5 - core / 2), 0, wpx * (0.5 + core / 2), hpx], fill=INK300 + (255,))
        d.rectangle([wpx * (0.5 - core * 0.2), 0, wpx * (0.5 + core * 0.2), hpx], fill=mix(INK300, PAPER, 0.35) + (255,))
        d.rectangle([wpx * 0.12, 0, wpx * 0.155, hpx], fill=EMBERDIM + (255,))
        d.rectangle([wpx * 0.845, 0, wpx * 0.88, hpx], fill=EMBERDIM + (255,))
        # periodic chevron bands, period 64 final px -> tileable vertically
        per = 64 * SS
        for k in range(0, hpx // per + 1):
            y0 = k * per
            d.polygon([(wpx * 0.5, y0 + per * 0.20), (wpx * (0.5 + core / 2), y0 + per * 0.38),
                       (wpx * (0.5 + core / 2), y0 + per * 0.46), (wpx * 0.5, y0 + per * 0.28),
                       (wpx * (0.5 - core / 2), y0 + per * 0.46), (wpx * (0.5 - core / 2), y0 + per * 0.38)],
                      fill=mix(INK300, PAPER, 0.22) + (255,))
        # tile-safe 2.5D (no vertical ramp, wrapped distance) — seams stay invisible
        return render_v2(finish(im, W, H), key=0.06, bevel=0.10, rim=0.10,
                         under=0.0, gloss=0.05, tile_y=True)
    S = 32
    im = canvas(S, S)
    d = ImageDraw.Draw(im)
    W = H = S * SS
    cx = W / 2
    if code == "dronebolt":       # capsule bolt — dark core widened to recipe share
        d.rounded_rectangle([cx - W * 0.17, H * 0.10, cx + W * 0.17, H * 0.90], radius=W * 0.16, fill=mix(INK300, PAPER, 0.12) + (255,))
        d.rounded_rectangle([cx - W * 0.10, H * 0.15, cx + W * 0.10, H * 0.85], radius=W * 0.09, fill=INK900 + (255,))
        d.polygon([(cx - W * 0.07, H * 0.19), (cx + W * 0.07, H * 0.19), (cx, H * 0.08)], fill=EMBERDIM + (255,))
    elif code == "plasmaorb":     # orb — thin light shell, big dark core
        d.ellipse([W * 0.12, H * 0.12, W * 0.88, H * 0.88], fill=mix(INK300, PAPER, 0.12) + (255,))
        d.ellipse([W * 0.20, H * 0.20, W * 0.80, H * 0.80], fill=INK900 + (255,))
        d.arc([W * 0.28, H * 0.28, W * 0.72, H * 0.72], start=200, end=40, fill=EMBERDIM + (255,), width=2 * SS)
    elif code == "missile":       # compact missile — dark lower body, small emberdim shares
        d.polygon([(cx, H * 0.05), (cx + W * 0.15, H * 0.30), (cx + W * 0.15, H * 0.72),
                   (cx, H * 0.78), (cx - W * 0.15, H * 0.72), (cx - W * 0.15, H * 0.30)], fill=INK300 + (255,))
        d.rectangle([cx - W * 0.15, H * 0.40, cx + W * 0.15, H * 0.74], fill=INK900 + (255,))
        d.rectangle([cx - W * 0.15, H * 0.40, cx - W * 0.115, H * 0.74], fill=INK500 + (255,))
        d.rectangle([cx + W * 0.115, H * 0.40, cx + W * 0.15, H * 0.74], fill=INK500 + (255,))
        d.polygon([(cx, H * 0.05), (cx + W * 0.10, H * 0.22), (cx - W * 0.10, H * 0.22)], fill=EMBERDIM + (255,))
        for sgn in (1, -1):
            d.polygon([(cx + sgn * W * 0.15, H * 0.58), (cx + sgn * W * 0.30, H * 0.80),
                       (cx + sgn * W * 0.15, H * 0.80)], fill=INK900 + (255,))
            d.polygon([(cx + sgn * W * 0.24, H * 0.72), (cx + sgn * W * 0.30, H * 0.80),
                       (cx + sgn * W * 0.22, H * 0.80)], fill=INK500 + (255,))
        d.polygon([(cx - W * 0.045, H * 0.78), (cx + W * 0.045, H * 0.78), (cx, H * 0.90)], fill=EMBERDIM + (255,))
    elif code == "boltmk5":       # teardrop bolt (standard) — wider dark core
        d.polygon([(cx, H * 0.04), (cx + W * 0.17, H * 0.42), (cx + W * 0.11, H * 0.88),
                   (cx, H * 0.96), (cx - W * 0.11, H * 0.88), (cx - W * 0.17, H * 0.42)], fill=mix(INK300, PAPER, 0.12) + (255,))
        d.polygon([(cx, H * 0.14), (cx + W * 0.115, H * 0.44), (cx + W * 0.075, H * 0.84),
                   (cx, H * 0.90), (cx - W * 0.075, H * 0.84), (cx - W * 0.115, H * 0.44)], fill=INK900 + (255,))
        d.polygon([(cx - W * 0.06, H * 0.20), (cx + W * 0.06, H * 0.20), (cx, H * 0.05)], fill=EMBERDIM + (255,))
    elif code == "childbolt":     # small diamond — core scaled up
        d.polygon([(cx, H * 0.08), (cx + W * 0.21, H * 0.50), (cx, H * 0.92), (cx - W * 0.21, H * 0.50)],
                  fill=mix(INK300, PAPER, 0.12) + (255,))
        d.polygon([(cx, H * 0.17), (cx + W * 0.155, H * 0.50), (cx, H * 0.83), (cx - W * 0.155, H * 0.50)],
                  fill=INK900 + (255,))
        d.ellipse([cx - W * 0.04, H * 0.44, cx + W * 0.04, H * 0.56], fill=EMBERDIM + (255,))
    elif code == "beamflare":     # 4-point flare burst — light rim star + dark inner star
        def star(scale, fill):
            pts = []
            for k in range(8):
                ang = math.radians(k * 45 - 90)
                rr = W * scale * (0.44 if k % 2 == 0 else 0.16)
                pts.append((cx + rr * math.cos(ang), H / 2 + rr * math.sin(ang)))
            d.polygon(pts, fill=fill)
        star(1.0, INK300 + (255,))
        star(0.70, INK900 + (255,))
        d.polygon([(cx, H * 0.07), (cx + W * 0.035, H * 0.16), (cx - W * 0.035, H * 0.16)], fill=EMBERDIM + (255,))
        d.polygon([(cx, H * 0.93), (cx + W * 0.035, H * 0.84), (cx - W * 0.035, H * 0.84)], fill=EMBERDIM + (255,))
    im = im.resize((S, S), Image.LANCZOS)
    # thin bright shell over dark core: no edge-AO (it would eat the shell at 32px)
    im = render_v2(im, key=0.14, bevel=0.14, ao=0.0, rim=0.34, under=0.0,
                   seam=0.30, step=0.18, gloss=0.08)
    return im


# ---------------------------------------------------------------- fx
def draw_fx(code):
    S = 128
    im = canvas(S, S)
    d = ImageDraw.Draw(im)
    W = H = S * SS
    cx = W / 2
    if code == "engineplume":     # afterburner plume, points DOWN (exhaust)
        # outer ink300 wisp, paper mid, white core (fx recipe)
        d.polygon([(cx, H * 0.97), (cx + W * 0.20, H * 0.45), (cx + W * 0.12, H * 0.10),
                   (cx - W * 0.12, H * 0.10), (cx - W * 0.20, H * 0.45)], fill=INK300 + (255,))
        d.polygon([(cx, H * 0.88), (cx + W * 0.145, H * 0.42), (cx + W * 0.085, H * 0.08),
                   (cx - W * 0.085, H * 0.08), (cx - W * 0.145, H * 0.42)], fill=PAPER + (255,))
        d.polygon([(cx, H * 0.66), (cx + W * 0.075, H * 0.34), (cx + W * 0.045, H * 0.07),
                   (cx - W * 0.045, H * 0.07), (cx - W * 0.075, H * 0.34)], fill=WHITE + (255,))
        # teal sparks 3%
        for (sx, sy) in [(0.40, 0.55), (0.60, 0.62), (0.50, 0.78)]:
            d.ellipse([W * sx - 5, H * sy - 5, W * sx + 5, H * sy + 5], fill=TEAL + (255,))
        # soft halo (alpha<0.5 so it stays out of the §4.9 mask)
        halo = Image.new("RGBA", im.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hd.ellipse([cx - W * 0.30, H * 0.05, cx + W * 0.30, H * 0.75], fill=PAPER + (70,))
        im = Image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(10 * SS)), im)
    else:                          # muzzleflash star
        pts = []
        for k in range(16):
            ang = math.radians(k * 22.5 - 90)
            rr = W * (0.44 if k % 4 == 0 else (0.26 if k % 2 == 0 else 0.12))
            pts.append((cx + rr * math.cos(ang), H / 2 + rr * math.sin(ang) * 0.92))
        d.polygon(pts, fill=PAPER + (255,))
        pts2 = []
        for k in range(16):
            ang = math.radians(k * 22.5 - 90 + 11.25)
            rr = W * (0.20 if k % 4 == 0 else 0.08)
            pts2.append((cx + rr * math.cos(ang), H / 2 + rr * math.sin(ang) * 0.92))
        d.polygon(pts2, fill=WHITE + (255,))
        # ink300 shards (~12% per fx recipe) + teal core dot
        for k in range(8):
            ang = math.radians(k * 45 - 22.5)
            x2, y2 = cx + W * 0.34 * math.cos(ang), H / 2 + W * 0.34 * math.sin(ang)
            d.polygon([(x2, y2), (x2 - W * 0.055, y2 + W * 0.030), (x2 + W * 0.015, y2 - W * 0.055),
                       (x2 + W * 0.05, y2 + W * 0.01)], fill=INK300 + (255,))
        d.ellipse([cx - W * 0.045, H / 2 - W * 0.045, cx + W * 0.045, H / 2 + W * 0.045], fill=TEAL + (255,))
    im = im.resize((S, S), Image.LANCZOS)
    # glow sprites: only a whisper of shading (fx recipe caps dark at 0.02)
    return render_v2(im, key=0.07, bevel=0.06, ao=0.08, rim=0.14, under=0.08,
                     seam=0.10, step=0.08, gloss=0.04)


# ---------------------------------------------------------------- measurement (§4.9)
def measure(im):
    """alpha>0.5 mask; colors after 32-level/channel quantize (step 8);
    val/val_std on V; dark=max<45 share; chroma=mean(S*V); fill=mask/canvas."""
    w, h = im.size
    px = im.load()
    n_mask = 0
    colors = set()
    vals, chromas = [], []
    dark = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 127:
                n_mask += 1
                colors.add((r // 8, g // 8, b // 8))
                if max(r, g, b) < 45:
                    dark += 1
                _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                vals.append(v)
                chromas.append(s * v)
    if n_mask == 0:
        return {}
    mean = sum(vals) / n_mask
    var = sum((v - mean) ** 2 for v in vals) / n_mask
    return {"colors_q32": len(colors), "val": round(mean, 3), "val_std": round(var ** 0.5, 3),
            "dark": round(dark / n_mask, 3), "chroma": round(sum(chromas) / n_mask, 3),
            "fill": round(n_mask / (w * h), 3)}


# §4.3 new-game targets (colors informational; G-A = 4 indices, <=1 out)
TARGETS = {
    "ship":   {"colors": (110, 160), "val": (0.46, 0.52), "val_std": (0.24, 0.30), "dark": (0.0, 0.10), "chroma": (0.19, 0.23)},
    "drone":  {"colors": (100, 130), "val": (0.45, 0.52), "val_std": (0.22, 0.26), "dark": (0.0, 0.08), "chroma": (0.18, 0.22)},
    "bullet": {"colors": (8, 16),    "val": (0.25, 0.30), "val_std": (0.18, 0.26), "dark": (0.40, 1.0), "chroma": (0.0, 0.12)},
    "fx":     {"colors": (3, 10),    "val": (0.70, 0.90), "val_std": (0.15, 0.25), "dark": (0.0, 0.02), "chroma": (0.0, 0.08)},
}


def gate_a(m, recipe):
    t = TARGETS[recipe]
    out = []
    for k in ("val", "val_std", "dark", "chroma"):
        lo, hi = t[k]
        if not (lo <= m[k] <= hi):
            out.append(k)
    return ("PASS" if len(out) <= 1 else "FAIL"), out


UNITS = []  # manifest rows


def emit(im, rel, row):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "PNG", optimize=True)
    m = measure(im)
    verdict, out = gate_a(m, row["recipe"])
    row.update({"file": rel, "delivered_px": f"{im.width}x{im.height}",
                "bytes": os.path.getsize(path), **m, "gate_a": verdict,
                "gate_a_out": ";".join(out)})
    UNITS.append(row)
    print(f"{rel} {im.width}x{im.height} {row['bytes']//1024}KB {m} G-A:{verdict}{out}")


def main():
    # ships x25 — AP-0016 glyph bucket (25 designs 10001..10999 range in planner)
    i = 0
    for fam_i in range(5):
        for var_i in range(5):
            i += 1
            im, fam = draw_ship(i, fam_i, var_i)
            emit(im, f"sprites/ships/player_ship_{i:02d}_256@ember.png",
                 {"row_id": "AP-0016", "batch": "P-SHIP", "unit_no": i, "planner_base": "GLYPH-ship-10001..10999",
                  "variant": f"{fam}-{var_i+1}", "target_px": 256, "recipe": "ship"})
    # drones x13 — AP-0011
    for k in range(1, 14):
        im, kind = draw_drone(k)
        emit(im, f"sprites/drones/player_drone_{k:02d}_128@gold.png",
             {"row_id": "AP-0011", "batch": "P-DRONE", "unit_no": k, "planner_base": "GLYPH-drone-20001..20013",
              "variant": kind, "target_px": 128, "recipe": "drone"})
    # bullets x8 — AP-0002..0009 (functional new names; planner base kept in mapping only)
    bullets = [
        ("AP-0002", "drone_laser", "dronebolt", "sprites/bullets/player_bullet_dronebolt_32@emberdim.png"),
        ("AP-0003", "laser", "beam", "sprites/bullets/player_bullet_beam_32x512@emberdim.png"),
        ("AP-0004", "laserbeam_player", "beamheavy", "sprites/bullets/player_bullet_beamheavy_32x512@emberdim.png"),
        ("AP-0005", "plasmagun", "plasmaorb", "sprites/bullets/player_bullet_plasmaorb_32@emberdim.png"),
        ("AP-0006", "rocket", "missile", "sprites/bullets/player_bullet_missile_32@emberdim.png"),
        ("AP-0007", "blt_player_5.", "boltmk5", "sprites/bullets/player_bullet_boltmk5_32@emberdim.png"),
        ("AP-0008", "drone_laser_child", "childbolt", "sprites/bullets/player_bullet_childbolt_32@emberdim.png"),
        ("AP-0009", "plasma_beam_flare_green", "beamflare", "sprites/bullets/player_bullet_beamflare_32@emberdim.png"),
    ]
    for row_id, base, code, rel in bullets:
        emit(draw_bullet(code), rel,
             {"row_id": row_id, "batch": "P-BULLET", "unit_no": code, "planner_base": base,
              "variant": code, "target_px": 32, "recipe": "bullet"})
    # fx x2 — AP-0013/0014
    emit(draw_fx("engineplume"), "sprites/fx/player_fx_engineplume_128@paper.png",
         {"row_id": "AP-0013", "batch": "P-FX", "unit_no": "engineplume", "planner_base": "afterburner",
          "variant": "engineplume", "target_px": 128, "recipe": "fx"})
    emit(draw_fx("muzzleflash"), "sprites/fx/player_fx_muzzleflash_128@paper.png",
         {"row_id": "AP-0014", "batch": "P-FX", "unit_no": "muzzleflash", "planner_base": "shooter",
          "variant": "muzzleflash", "target_px": 128, "recipe": "fx"})

    with open(os.path.join(HERE, "w1_units.csv"), "w", newline="", encoding="utf-8") as f:
        wcsv = csv.DictWriter(f, fieldnames=list(UNITS[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(UNITS)
    with open(os.path.join(HERE, "w1_units.json"), "w", encoding="utf-8") as f:
        json.dump(UNITS, f, indent=1, ensure_ascii=False)
    npass = sum(1 for u in UNITS if u["gate_a"] == "PASS")
    print(f"\nUNITS={len(UNITS)}  G-A PASS={npass}  FAIL={len(UNITS)-npass}")


if __name__ == "__main__":
    main()
