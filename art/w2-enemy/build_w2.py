#!/usr/bin/env python3
"""
W2 ENEMY sprite builder — WindWings (Godot port) · vai Art-designer · arena/5438fec9

34 units from art-planner.csv @971a7eea8:
  AP-0046..0068 E-BODY   x23  target_px 128  recipe enemy
  AP-0070..0080 E-BULLET x11  target_px 64   recipe bullet
Same pipeline as W1 (build_w1.py): flat-vector originals in exact Ink & Ember hex,
recipe area ratios, supersample x4, §4.9 measurement, G-A gate. Enemies face DOWN
(toward player). Per-row content box follows the planner max_w x max_h aspect hint
(proportion only — no original art). Deterministic seeds.
Run: python3 build_w2.py (needs Pillow).
"""
import colorsys
import csv
import json
import math
import os
import random

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 4

INK900 = (0x0B, 0x0E, 0x14)
INK700 = (0x16, 0x1C, 0x26)
INK500 = (0x2A, 0x34, 0x42)
INK300 = (0x4A, 0x56, 0x6B)
PAPER = (0xE8, 0xE3, 0xD9)
EMBERDIM = (0x8C, 0x2F, 0x17)
TEAL = (0x4F, 0xD1, 0xC5)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def light_pass(im, hi=0.16, lo=0.14):
    w, h = im.size
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a >= 200:
                t = x / w * 0.55 + y / h * 0.45
                f = 1.0 + hi * (0.5 - t) * 2 - lo * max(0.0, t - 0.5)
                f = max(0.78, min(1.30, f))
                px[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
    return im


def add_grain(im, amount=0.03, seed=7):
    rng = random.Random(seed)
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 0:
                n = 1.0 + rng.uniform(-amount, amount)
                px[x, y] = (min(255, int(r * n)), min(255, int(g * n)), min(255, int(b * n)), a)
    return im


class Box:
    """Normalized -0.5..0.5 space mapped to an aspect-fit box inside the SS canvas."""
    def __init__(self, size, aspect):
        self.W = self.H = size * SS
        self.cx = self.W / 2
        self.cy = self.H / 2
        m = self.W * 0.86
        if aspect >= 1:
            self.bw, self.bh = m, m / aspect
        else:
            self.bw, self.bh = m * aspect, m

    def P(self, u, v):
        return (self.cx + u * self.bw, self.cy + v * self.bh)

    def E(self, u, v, ru, rv):
        return [self.cx + (u - ru) * self.bw, self.cy + (v - rv) * self.bh,
                self.cx + (u + ru) * self.bw, self.cy + (v + rv) * self.bh]


def eye(d, B, u, v, ru, rv, pupil=True):
    """Big teal sensor eye (recipe teal ~15%) with paper glint."""
    d.ellipse(B.E(u, v, ru, rv), fill=TEAL + (255,))
    d.ellipse(B.E(u - ru * 0.35, v - rv * 0.4, ru * 0.42, rv * 0.42), fill=mix(TEAL, PAPER, 0.45) + (255,))
    if pupil:
        d.ellipse(B.E(u, v + rv * 0.1, ru * 0.30, rv * 0.30), fill=INK700 + (255,))
        d.ellipse(B.E(u - ru * 0.12, v - rv * 0.05, ru * 0.10, rv * 0.10), fill=PAPER + (255,))


def shadow_ellipse(d, box, off=SS):
    d.ellipse([box[0] + off, box[1] + off, box[2] + off, box[3] + off], fill=INK900 + (255,))


def shadow_poly(d, pts, off=SS):
    d.polygon([(x + off, y + off) for x, y in pts], fill=INK900 + (255,))


# ---------------------------------------------------------------- enemy bodies (face DOWN)
def fam_saucer(d, B, v):
    body = B.E(0, 0.02, 0.48, 0.30)
    shadow_ellipse(d, body)
    d.ellipse(body, fill=mix(INK300, PAPER, 0.15) + (255,))
    d.pieslice(body, start=180, end=360, fill=PAPER + (255,))  # paper top dome (recipe paper 30)
    d.ellipse(B.E(0, -0.06, 0.20, 0.16), fill=mix(INK300, PAPER, 0.45) + (255,))
    d.ellipse(B.E(0, 0.18, 0.30, 0.07), fill=INK500 + (255,))  # underside band
    eye(d, B, 0, 0.02, 0.12, 0.14)
    for k in range(-2, 3):  # teal rim lights
        if k:
            d.ellipse(B.E(k * 0.17, 0.20, 0.045, 0.055), fill=TEAL + (255,))
    d.rectangle([B.P(-0.03, 0.24)[0], B.P(0, 0.24)[1], B.P(0.03, 0.34)[0], B.P(0, 0.34)[1]], fill=INK700 + (255,))


def fam_triblade(d, B, v):
    rot = [90, 30, 150, 90][v % 4]
    hub = B.E(0, 0, 0.17, 0.17)
    blades = []
    for k in range(3):
        a = math.radians(rot + 120 * k)
        tip = (0.46 * math.cos(a), 0.46 * math.sin(a))
        perp = a + math.pi / 2
        wdt = 0.13
        blades.append([B.P(tip[0] * 0.18 + wdt * math.cos(perp), tip[1] * 0.18 + wdt * math.sin(perp)),
                       B.P(tip[0], tip[1]),
                       B.P(tip[0] * 0.18 - wdt * math.cos(perp), tip[1] * 0.18 - wdt * math.sin(perp)),
                       B.P(tip[0] * 0.42, tip[1] * 0.42)])
    shadow_ellipse(d, hub)
    for bl in blades:
        d.polygon(bl, fill=INK500 + (255,))  # shaded base
        d.polygon([bl[0], bl[1], bl[3]], fill=PAPER + (255,))  # lit half -> bimodal
        mid = B.P((bl[1][0] - B.cx) / B.bw * 0.52, (bl[1][1] - B.cy) / B.bh * 0.52)
        d.polygon([bl[0], mid, bl[2]], fill=TEAL + (255,))  # teal blade root -> chroma
    d.ellipse(hub, fill=mix(INK300, PAPER, 0.45) + (255,))
    d.ellipse(B.E(0, 0, 0.12, 0.12), outline=TEAL + (255,), width=int(B.bw * 0.025))
    d.ellipse(B.E(0, 0, 0.08, 0.08), fill=INK500 + (255,))
    eye(d, B, 0, 0.01, 0.075, 0.075)


def fam_lance(d, B, v):
    pts_half = [(0, 0.48), (0.10, 0.28), (0.15, 0.05), (0.13, -0.18), (0.30, -0.34),
                (0.26, -0.42), (0.09, -0.38), (0.07, -0.48), (0, -0.44)]
    poly = [B.P(u, vv) for u, vv in pts_half] + [B.P(-u, vv) for u, vv in reversed(pts_half)]
    shadow_poly(d, poly)
    d.polygon(poly, fill=mix(INK300, PAPER, 0.15) + (255,))
    spine = [B.P(u, vv) for u, vv in [(0, 0.44), (0.075, 0.1), (0.06, -0.3), (0, -0.38), (-0.06, -0.3), (-0.075, 0.1)]]
    d.polygon(spine, fill=PAPER + (255,))
    for sgn in (1, -1):
        d.polygon([B.P(sgn * 0.09, -0.05), B.P(sgn * 0.20, -0.28), B.P(sgn * 0.10, -0.3)], fill=INK500 + (255,))
        d.ellipse(B.E(sgn * 0.17, -0.36, 0.045, 0.05), fill=TEAL + (255,))
    eye(d, B, 0, 0.22, 0.075, 0.10)


def fam_ringgun(d, B, v):
    ring = B.E(0, -0.04, 0.40, 0.40)
    d.ellipse([ring[0] + SS, ring[1] + SS, ring[2] + SS, ring[3] + SS],
              outline=INK900 + (255,), width=int(B.bw * 0.16))
    d.ellipse(ring, outline=mix(INK300, PAPER, 0.38) + (255,), width=int(B.bw * 0.16))
    d.ellipse(B.E(0, -0.04, 0.40, 0.40), outline=mix(INK300, PAPER, 0.62) + (255,), width=int(B.bw * 0.05))
    d.ellipse(B.E(0, -0.04, 0.30, 0.30), outline=INK500 + (255,), width=int(B.bw * 0.04))
    # gun barrel down
    d.polygon([B.P(-0.09, -0.10), B.P(0.09, -0.10), B.P(0.06, 0.40), B.P(0, 0.48), B.P(-0.06, 0.40)],
              fill=PAPER + (255,))
    d.polygon([B.P(-0.05, 0.05), B.P(0.05, 0.05), B.P(0.035, 0.38), B.P(-0.035, 0.38)], fill=INK500 + (255,))
    eye(d, B, 0, -0.06, 0.10, 0.11)
    for uu, vv in [(0.40, -0.04), (-0.40, -0.04), (0, -0.44), (0.28, 0.24), (-0.28, 0.24)]:
        d.ellipse(B.E(uu, vv, 0.06, 0.06), fill=TEAL + (255,))


def rect(d, B, u0, v0, u1, v1, fill):
    x0, y0 = B.P(min(u0, u1), min(v0, v1))
    x1, y1 = B.P(max(u0, u1), max(v0, v1))
    d.rectangle([x0, y0, x1, y1], fill=fill)


def fam_barge(d, B, v):
    body = [B.P(-0.46, -0.30)[0], B.P(0, -0.30)[1], B.P(0.46, 0.26)[0], B.P(0, 0.26)[1]]
    shadow_ellipse(d, body)
    d.rounded_rectangle(body, radius=B.bw * 0.10, fill=mix(INK300, PAPER, 0.15) + (255,))
    d.rounded_rectangle([B.P(-0.40, -0.30)[0], B.P(0, -0.30)[1], B.P(0.40, -0.08)[0], B.P(0, -0.08)[1]],
                        radius=B.bw * 0.08, fill=PAPER + (255,))
    for sgn in (1, -1):
        pod = [B.P(sgn * 0.34, -0.05)[0], B.P(0, -0.05)[1], B.P(sgn * 0.47, 0.30)[0], B.P(0, 0.30)[1]]
        pod = [min(pod[0], pod[2]), pod[1], max(pod[0], pod[2]), pod[3]]
        d.rounded_rectangle(pod, radius=B.bw * 0.05, fill=INK500 + (255,))
        rect(d, B, sgn * 0.35, -0.04, sgn * 0.46, 0.03, TEAL + (255,))
        rect(d, B, sgn * 0.35, 0.20, sgn * 0.46, 0.30, INK700 + (255,))
        rect(d, B, sgn * 0.37, 0.30, sgn * 0.42, 0.37, INK900 + (255,))
        eye(d, B, sgn * 0.24, 0.08, 0.075, 0.09, pupil=False)
    rect(d, B, -0.17, 0.08, 0.17, 0.19, TEAL + (255,))


def fam_orbiter(d, B, v, timer=False):
    orb = B.E(0, 0, 0.27, 0.27)
    shadow_ellipse(d, orb)
    pods = 3 if v % 2 else 2
    for k in range(pods):
        a = math.radians(90 + (360 / pods) * k + 30 * v)
        pu, pv = 0.42 * math.cos(a), 0.42 * math.sin(a)
        d.line([B.P(0, 0), B.P(pu, pv)], fill=INK300 + (255,), width=int(B.bw * 0.07))
        d.ellipse(B.E(pu, pv, 0.10, 0.10), fill=mix(INK300, PAPER, 0.20) + (255,))
        d.ellipse(B.E(pu, pv, 0.065, 0.065), fill=TEAL + (255,))
        d.ellipse(B.E(pu, pv, 0.03, 0.03), fill=PAPER + (255,))
    d.ellipse(orb, fill=mix(INK300, PAPER, 0.30) + (255,))
    topcol = mix(INK300, PAPER, 0.85) if timer else PAPER
    d.pieslice(orb, start=180, end=360, fill=topcol + (255,))  # bright top half -> bimodal
    if timer:
        d.pieslice(orb, start=0, end=180, fill=INK300 + (255,))  # darker bottom half -> spread
    d.ellipse(B.E(0, 0.02, 0.15, 0.15), fill=(INK500 if timer else INK900) + (255,))
    if timer:
        for k in range(3):
            d.arc(B.E(0, 0, 0.24, 0.24), start=k * 120 + 15, end=k * 120 + 95,
                  fill=TEAL + (255,), width=int(B.bw * 0.018))
    eye(d, B, 0, 0.02, 0.12, 0.12)


def fam_shard(d, B, v):
    outer = [(0, 0.48), (0.16, 0.18), (0.34, 0.05), (0.20, -0.22), (0.26, -0.44),
             (0, -0.32), (-0.26, -0.44), (-0.20, -0.22), (-0.34, 0.05), (-0.16, 0.18)]
    poly = [B.P(u, vv) for u, vv in outer]
    shadow_poly(d, poly)
    d.polygon(poly, fill=mix(INK300, PAPER, 0.18) + (255,))
    inner = [(0, 0.36), (0.10, 0.12), (0.20, 0.02), (0.11, -0.16), (0.14, -0.32),
             (0, -0.24), (-0.14, -0.32), (-0.11, -0.16), (-0.20, 0.02), (-0.10, 0.12)]
    d.polygon([B.P(u, vv) for u, vv in inner], fill=PAPER + (255,))
    d.polygon([B.P(0, -0.20), B.P(0.09, -0.02), B.P(0, 0.16), B.P(-0.09, -0.02)], fill=INK700 + (255,))
    eye(d, B, 0, 0.16, 0.10, 0.115)
    for sgn in (1, -1):
        d.polygon([B.P(sgn * 0.33, -0.43), B.P(sgn * 0.39, -0.30), B.P(sgn * 0.21, -0.23)], fill=TEAL + (255,))


FAMS = {"saucer": fam_saucer, "triblade": fam_triblade, "lance": fam_lance,
        "ringgun": fam_ringgun, "barge": fam_barge, "orbiter": fam_orbiter, "shard": fam_shard}

# row_id -> (planner_base, family, variant, aspect from max_w/max_h)
BODY_ROWS = [
    ("AP-0046", "1.", "lance", 0, 149 / 256), ("AP-0047", "14_2", "lance", 1, 118 / 210),
    ("AP-0048", "212_1", "shard", 0, 126 / 176), ("AP-0049", "23_0", "barge", 0, 269 / 162),
    ("AP-0050", "5_0", "saucer", 0, 244 / 284), ("AP-0051", "5_2", "orbiter", 0, 76 / 88),
    ("AP-0052", "6.", "triblade", 0, 73 / 128), ("AP-0053", "7_1", "lance", 2, 221 / 386),
    ("AP-0054", "7_4", "shard", 1, 99 / 178), ("AP-0055", "cb", "lance", 3, 151 / 256),
    ("AP-0056", "cb-", "ringgun", 0, 138 / 159), ("AP-0057", "cb-009a", "saucer", 1, 91 / 57),
    ("AP-0058", "cb-009b", "triblade", 1, 58 / 82), ("AP-0059", "cd", "triblade", 2, 1.0),
    ("AP-0060", "da", "shard", 2, 1.0), ("AP-0061", "droid", "orbiter", 1, 96 / 103),
    ("AP-0062", "droid1_timer", "orbiter", 2, 1.0), ("AP-0063", "e", "saucer", 2, 1.0),
    ("AP-0064", "e_", "ringgun", 1, 147 / 236), ("AP-0065", "e_3308a", "barge", 1, 186 / 252),
    ("AP-0066", "e_3308b", "triblade", 3, 95 / 100), ("AP-0067", "enemy_hp", "orbiter", 3, 1.0),
    ("AP-0068", "enemytut", "saucer", 3, 89 / 51),
]


def draw_body(row_id, base, fam, var, aspect):
    S = 128
    im = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    B = Box(S, max(0.5, min(1.9, aspect)))
    if fam == "orbiter" and base == "droid1_timer":
        fam_orbiter(d, B, var, timer=True)
    else:
        FAMS[fam](d, B, var)
    im = im.resize((S, S), Image.LANCZOS)
    im = light_pass(im, 0.21, 0.19)
    return add_grain(im, 0.03, seed=int(row_id[-2:]) + 300)


# ---------------------------------------------------------------- enemy bullets (64px, point DOWN)
def draw_ebullet(code):
    S = 64
    im = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    B = Box(S, 1.0)
    cx = B.cx
    SHELL = mix(INK300, (0xE8, 0xE3, 0xD9), 0.12)
    if code in ("orb", "miniorb", "orbspike"):
        r = 0.30 if code != "miniorb" else 0.22
        if code == "orbspike":
            pts = []
            for k in range(16):
                a = math.radians(k * 22.5)
                rr = 0.40 if k % 2 == 0 else 0.29
                pts.append(B.P(rr * math.cos(a), rr * math.sin(a)))
            d.polygon(pts, fill=SHELL + (255,))
        else:
            d.ellipse(B.E(0, 0, r + 0.07, r + 0.07), fill=SHELL + (255,))
        d.ellipse(B.E(0, 0, r, r), fill=INK900 + (255,))
        d.arc(B.E(0, 0, r * 0.62, r * 0.62), start=300, end=140, fill=EMBERDIM + (255,), width=3 * SS)
        d.ellipse(B.E(0, 0, r * 0.16, r * 0.16), fill=EMBERDIM + (255,))
    elif code == "capsule":
        box = [B.P(-0.16, -0.42)[0], B.P(0, -0.42)[1], B.P(0.16, 0.42)[0], B.P(0, 0.42)[1]]
        d.rounded_rectangle(box, radius=B.bw * 0.15, fill=SHELL + (255,))
        box2 = [B.P(-0.10, -0.36)[0], B.P(0, -0.36)[1], B.P(0.10, 0.36)[0], B.P(0, 0.36)[1]]
        d.rounded_rectangle(box2, radius=B.bw * 0.09, fill=INK900 + (255,))
        d.polygon([B.P(-0.07, 0.28), B.P(0.07, 0.28), B.P(0, 0.44)], fill=EMBERDIM + (255,))
    elif code in ("teardrop", "spike", "spikeheavy", "blade"):
        wdt = {"teardrop": 0.17, "spike": 0.10, "spikeheavy": 0.16, "blade": 0.18}[code]
        outer = [(0, 0.46), (wdt, 0.05), (wdt * 0.66, -0.38), (0, -0.46), (-wdt * 0.66, -0.38), (-wdt, 0.05)]
        d.polygon([B.P(u, v) for u, v in outer], fill=SHELL + (255,))
        s = 0.74 if code == "blade" else 0.68
        d.polygon([B.P(u * s, v * 0.9 + 0.02) for u, v in outer], fill=INK900 + (255,))
        d.polygon([B.P(-wdt * 0.5, 0.30), B.P(wdt * 0.5, 0.30), B.P(0, 0.46)], fill=EMBERDIM + (255,))
        if code == "blade":
            d.rectangle([B.P(-0.20, -0.30)[0], B.P(0, -0.30)[1], B.P(0.20, -0.24)[0], B.P(0, -0.24)[1]],
                        fill=mix(EMBERDIM, PAPER, 0.50) + (255,))
    elif code == "hitburst":
        pts = []
        for k in range(12):
            a = math.radians(k * 30 - 90)
            rr = 0.42 if k % 2 == 0 else 0.21
            pts.append(B.P(rr * math.cos(a), rr * math.sin(a)))
        d.polygon(pts, fill=mix(INK300, PAPER, 0.45) + (255,))
        pts2 = [B.P((p[0] - cx) / B.bw * 0.82, (p[1] - B.cy) / B.bh * 0.82) for p in pts]
        d.polygon(pts2, fill=INK900 + (255,))
        d.ellipse(B.E(0, 0, 0.07, 0.07), fill=EMBERDIM + (255,))
    elif code == "warning":
        d.polygon([B.P(0, -0.40), B.P(0.34, 0), B.P(0, 0.40), B.P(-0.34, 0)], fill=SHELL + (255,))
        d.polygon([B.P(0, -0.31), B.P(0.26, 0), B.P(0, 0.31), B.P(-0.26, 0)], fill=INK900 + (255,))
        d.rectangle([B.P(-0.04, -0.16)[0], B.P(0, -0.16)[1], B.P(0.04, 0.06)[0], B.P(0, 0.06)[1]],
                    fill=EMBERDIM + (255,))
        d.ellipse(B.E(0, 0.14, 0.05, 0.05), fill=EMBERDIM + (255,))
    elif code == "arrow":
        for dy, sc in [(-0.16, 1.0), (0.14, 0.78)]:
            d.polygon([B.P(-0.34 * sc, dy - 0.16), B.P(0, dy + 0.08), B.P(0.34 * sc, dy - 0.16),
                       B.P(0.34 * sc, dy - 0.02), B.P(0, dy + 0.22), B.P(-0.34 * sc, dy - 0.02)],
                      fill=mix(INK300, PAPER, 0.02) + (255,))
            d.polygon([B.P(-0.25 * sc, dy - 0.14), B.P(0, dy + 0.02), B.P(0.25 * sc, dy - 0.14),
                       B.P(0.25 * sc, dy - 0.02), B.P(0, dy + 0.14), B.P(-0.25 * sc, dy - 0.02)],
                      fill=INK900 + (255,))
        d.polygon([B.P(-0.05, 0.30), B.P(0.05, 0.30), B.P(0, 0.42)], fill=EMBERDIM + (255,))
    im = im.resize((S, S), Image.LANCZOS)
    return light_pass(im, hi=0.30, lo=0.12)


BULLET_ROWS = [
    ("AP-0070", "22_0", "miniorb", "enemy_bullet_miniorb_64@emberdim.png"),
    ("AP-0071", "7_2", "teardrop", "enemy_bullet_teardrop_64@emberdim.png"),
    ("AP-0072", "7_3", "spike", "enemy_bullet_spike_64@emberdim.png"),
    ("AP-0073", "9.", "spikeheavy", "enemy_bullet_spikeheavy_64@emberdim.png"),
    ("AP-0074", "ebullet", "capsule", "enemy_bullet_capsule_64@emberdim.png"),
    ("AP-0075", "efx_bullethit", "hitburst", "enemy_bullet_hitburst_64@emberdim.png"),
    ("AP-0076", "sword", "blade", "enemy_bullet_blade_64@emberdim.png"),
    ("AP-0077", "warning", "warning", "enemy_bullet_warning_64@emberdim.png"),
    ("AP-0078", "arrow", "arrow", "enemy_bullet_arrow_64@emberdim.png"),
    ("AP-0079", "blt", "orb", "enemy_bullet_orb_64@emberdim.png"),
    ("AP-0080", "blt_", "orbspike", "enemy_bullet_orbspike_64@emberdim.png"),
]


# ---------------------------------------------------------------- measurement (§4.9, same as W1)
def measure(im):
    w, h = im.size
    px = im.load()
    n = dark = 0
    colors = set()
    vals, chromas = [], []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 127:
                n += 1
                colors.add((r // 8, g // 8, b // 8))
                if max(r, g, b) < 45:
                    dark += 1
                _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                vals.append(v)
                chromas.append(s * v)
    if not n:
        return {}
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    return {"colors_q32": len(colors), "val": round(mean, 3), "val_std": round(var ** 0.5, 3),
            "dark": round(dark / n, 3), "chroma": round(sum(chromas) / n, 3),
            "fill": round(n / (w * h), 3)}


TARGETS = {
    "enemy": {"val": (0.58, 0.65), "val_std": (0.23, 0.27), "dark": (0.0, 0.06), "chroma": (0.14, 0.17)},
    "bullet": {"val": (0.25, 0.30), "val_std": (0.18, 0.26), "dark": (0.40, 1.0), "chroma": (0.0, 0.12)},
}


def gate_a(m, recipe):
    out = [k for k in ("val", "val_std", "dark", "chroma")
           if not (TARGETS[recipe][k][0] <= m[k] <= TARGETS[recipe][k][1])]
    return ("PASS" if len(out) <= 1 else "FAIL"), out


UNITS = []


def emit(im, rel, row):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "PNG", optimize=True)
    m = measure(im)
    verdict, out = gate_a(m, row["recipe"])
    row.update({"file": rel, "delivered_px": f"{im.width}x{im.height}",
                "bytes": os.path.getsize(path), **m, "gate_a": verdict, "gate_a_out": ";".join(out)})
    UNITS.append(row)
    print(f"{rel} {im.width}x{im.height} {m} G-A:{verdict}{out}")


def main():
    fam_count = {}
    for row_id, base, fam, var, aspect in BODY_ROWS:
        fam_count[fam] = fam_count.get(fam, 0) + 1
        n = fam_count[fam]
        im = draw_body(row_id, base, fam, var, aspect)
        emit(im, f"sprites/bodies/enemy_body_{fam}{n:02d}_128@teal.png",
             {"row_id": row_id, "batch": "E-BODY", "unit_no": f"{fam}{n:02d}", "planner_base": base,
              "variant": f"{fam}-v{var}", "target_px": 128, "recipe": "enemy"})
    for row_id, base, code, fname in BULLET_ROWS:
        emit(draw_ebullet(code), f"sprites/bullets/{fname}",
             {"row_id": row_id, "batch": "E-BULLET", "unit_no": code, "planner_base": base,
              "variant": code, "target_px": 64, "recipe": "bullet"})
    with open(os.path.join(HERE, "w2_units.csv"), "w", newline="", encoding="utf-8") as f:
        wcsv = csv.DictWriter(f, fieldnames=list(UNITS[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(UNITS)
    with open(os.path.join(HERE, "w2_units.json"), "w", encoding="utf-8") as f:
        json.dump(UNITS, f, indent=1, ensure_ascii=False)
    npass = sum(1 for u in UNITS if u["gate_a"] == "PASS")
    print(f"\nUNITS={len(UNITS)}  G-A PASS={npass}  FAIL={len(UNITS) - npass}")


if __name__ == "__main__":
    main()
