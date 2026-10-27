#!/usr/bin/env python3
"""
W3 BOSS sprite builder — WindWings (Godot port) · vai Art-designer · arena/5438fec9

42 units from art-planner.csv @971a7eea8 (lane BOSS, wave W3):
  AP-0117/0118/0119 B-BODY singles x3        target_px 512  recipe boss
  AP-0120 GLYPH-boss-7001..9018 x32          target_px 512  recipe boss
  AP-0122..0128 B-PART x7                    target_px 256  recipe boss
Same pipeline as W1/W2: flat-vector originals in exact Ink & Ember hex, recipe
area ratios (boss: ink300 50 · ink500 15 · paper 10 · emberdim 15 · ember 6 ·
ink900 4), supersample, §4.9 measurement, G-A gate (plan §4.3 windows).
Boss rules from plan: asymmetry + >=1 glowing destructible block (ember core)
+ <=2 sub-blocks. Bosses face DOWN. AP-0124 venom sac uses teal ("doc xanh"),
declared in PROGRESS. Deterministic seeds. Run: python3 build_w3.py
"""
import colorsys
import csv
import json
import math
import os
import random

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 2

INK900 = (0x0B, 0x0E, 0x14)
INK500 = (0x2A, 0x34, 0x42)
INK300 = (0x4A, 0x56, 0x6B)
PAPER = (0xE8, 0xE3, 0xD9)
EMBER = (0xFF, 0x5A, 0x2B)
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
    def __init__(self, size, aspect):
        self.W = self.H = size * SS
        self.cx = self.W / 2
        self.cy = self.H / 2
        m = self.W * 0.88
        if aspect >= 1:
            self.bw, self.bh = m, m / aspect
        else:
            self.bw, self.bh = m * aspect, m

    def P(self, u, v):
        return (self.cx + u * self.bw, self.cy + v * self.bh)

    def E(self, u, v, ru, rv):
        return [self.cx + (u - ru) * self.bw, self.cy + (v - rv) * self.bh,
                self.cx + (u + ru) * self.bw, self.cy + (v + rv) * self.bh]

    def R(self, u0, v0, u1, v1):
        return [self.cx + min(u0, u1) * self.bw, self.cy + min(v0, v1) * self.bh,
                self.cx + max(u0, u1) * self.bw, self.cy + max(v0, v1) * self.bh]


def shadow_ellipse(d, box, off=SS):
    d.ellipse([box[0] + off, box[1] + off, box[2] + off, box[3] + off], fill=INK900 + (255,))


def shadow_poly(d, pts, off=SS):
    d.polygon([(x + off, y + off) for x, y in pts], fill=INK900 + (255,))


def shadow_rrect(d, B, box, rad, off=SS):
    d.rounded_rectangle([box[0] + off, box[1] + off, box[2] + off, box[3] + off], radius=rad, fill=INK900 + (255,))


def core(d, B, u, v, r, rv=None):
    """Glowing destructible block: ink900 socket / emberdim / ember / hot dot."""
    rv = r if rv is None else rv
    d.ellipse(B.E(u, v, r * 1.28, rv * 1.28), fill=INK900 + (255,))
    d.ellipse(B.E(u, v, r, rv), fill=EMBERDIM + (255,))
    d.ellipse(B.E(u, v, r * 0.62, rv * 0.62), fill=EMBER + (255,))
    d.ellipse(B.E(u - r * 0.18, v - rv * 0.2, r * 0.2, rv * 0.2), fill=mix(EMBER, PAPER, 0.75) + (255,))


def gunpod(d, B, u, v, w=0.11, h=0.16, barrel=True):
    d.rounded_rectangle(B.R(u - w / 2, v - h / 2, u + w / 2, v + h / 2), radius=B.bw * 0.03, fill=INK500 + (255,))
    d.rectangle(B.R(u - w * 0.34, v + h * 0.18, u + w * 0.34, v + h * 0.42), fill=EMBERDIM + (255,))
    if barrel:
        d.rectangle(B.R(u - w * 0.16, v + h / 2, u + w * 0.16, v + h / 2 + 0.07), fill=INK500 + (255,))


def star(d, B, u, v, r_out, r_in, teeth, fill, rot=0.0, rv_scale=1.0):
    pts = []
    for k in range(teeth * 2):
        a = rot + math.pi * k / teeth
        rr = r_out if k % 2 == 0 else r_in
        pts.append(B.P(u + rr * math.cos(a), v + rr * rv_scale * math.sin(a)))
    d.polygon(pts, fill=fill + (255,))
    return pts


# ---------------------------------------------------------------- boss families (face DOWN)
def fam_dreadnought(d, B, v, crown=False):
    flip = -1 if v % 2 else 1
    hull = B.R(-0.46, -0.30, 0.46, 0.20)
    shadow_rrect(d, B, hull, B.bw * 0.06)
    d.rounded_rectangle(hull, radius=B.bw * 0.06, fill=INK300 + (255,))
    d.rectangle(B.R(-0.42, 0.08, 0.42, 0.30), fill=EMBERDIM + (255,))  # ember skirt
    d.polygon([B.P(-0.46, -0.05), B.P(-0.58, 0.18), B.P(-0.46, 0.20)], fill=INK500 + (255,))
    d.polygon([B.P(0.46, -0.05), B.P(0.58, 0.18), B.P(0.46, 0.20)], fill=INK500 + (255,))
    deck_x = -0.06 * flip
    d.rounded_rectangle(B.R(deck_x - 0.26, -0.30, deck_x + 0.26, -0.10), radius=B.bw * 0.04, fill=PAPER + (255,))
    d.rectangle(B.R(deck_x - 0.20, -0.24, deck_x + 0.20, -0.19), fill=INK500 + (255,))
    if crown:
        for k in range(-2, 3):
            cx = k * 0.13
            d.polygon([B.P(cx - 0.045, -0.30), B.P(cx, -0.44 - 0.03 * (2 - abs(k))), B.P(cx + 0.045, -0.30)],
                      fill=(PAPER if k == 0 else INK500) + (255,))
    gunpod(d, B, -0.30, 0.24)
    gunpod(d, B, 0.30, 0.24, w=0.11 if v < 2 else 0.13)
    if v >= 2:
        gunpod(d, B, flip * 0.13, 0.26, w=0.09, h=0.13)
    core(d, B, flip * 0.07, -0.01, 0.115 if not crown else 0.135)
    d.rectangle(B.R(-flip * 0.30, -0.06, -flip * 0.16, 0.02), fill=INK500 + (255,))  # asym vent block


def fam_spider(d, B, v):
    flip = -1 if v % 2 else 1
    for side in (-1, 1):
        for k in range(3):
            vv = -0.16 + k * 0.16
            lift = -0.10 if (side == flip and k == 2 and v % 2) else 0.0
            pts = [B.P(side * 0.20, vv), B.P(side * 0.42, vv - 0.06 + lift), B.P(side * 0.52, vv + 0.14 + lift)]
            d.line(pts, fill=INK300 + (255,), width=int(B.bw * 0.05), joint="curve")
            d.ellipse(B.E(side * 0.42, vv - 0.06 + lift, 0.045, 0.05), fill=INK500 + (255,))
    abd = B.E(0, -0.10, 0.31, 0.31)
    shadow_ellipse(d, abd)
    d.ellipse(abd, fill=INK300 + (255,))
    d.pieslice(abd, start=175, end=335, fill=mix(INK300, PAPER, 0.62) + (255,))  # carapace cap
    d.ellipse(B.E(flip * 0.09, -0.13, 0.17, 0.15), fill=EMBERDIM + (255,))  # venom sac
    d.ellipse(B.E(-flip * 0.15, 0.04, 0.09, 0.08), fill=EMBERDIM + (255,))
    d.ellipse(B.E(0, 0.20, 0.17, 0.16), fill=INK500 + (255,))  # head
    core(d, B, flip * 0.09, -0.14, 0.088 if v == 3 else 0.075)
    for k, du in enumerate((-0.07, 0.0, 0.07)):
        d.ellipse(B.E(du, 0.24 + (0.03 if k == 1 else 0), 0.032, 0.036), fill=EMBER + (255,))
    d.polygon([B.P(-0.08, 0.32), B.P(-0.03, 0.42), B.P(-0.01, 0.32)], fill=PAPER + (255,))
    d.polygon([B.P(0.08, 0.32), B.P(0.03, 0.42), B.P(0.01, 0.32)], fill=PAPER + (255,))


def fam_ringfort(d, B, v):
    flip = -1 if v % 2 else 1
    ring = B.E(0, -0.02, 0.44, 0.44)
    wdt = int(B.bw * 0.17)
    d.ellipse([ring[0] + SS, ring[1] + SS, ring[2] + SS, ring[3] + SS], outline=INK900 + (255,), width=wdt)
    d.ellipse(ring, outline=INK300 + (255,), width=wdt)
    d.arc(ring, start=190, end=315, fill=PAPER + (255,), width=int(B.bw * 0.06))
    d.ellipse(B.E(0, -0.02, 0.33, 0.33), outline=EMBERDIM + (255,), width=int(B.bw * 0.055))
    for a_deg in (90, 210, 330):
        a = math.radians(a_deg + 12 * v)
        d.line([B.P(0, -0.02), B.P(0.36 * math.cos(a), -0.02 + 0.36 * math.sin(a))],
               fill=INK500 + (255,), width=int(B.bw * 0.07))
    for a_deg in (60, 120, 255 + 25 * flip):
        a = math.radians(a_deg)
        tu, tv = 0.44 * math.cos(a), -0.02 + 0.44 * math.sin(a)
        d.ellipse(B.E(tu, tv, 0.075, 0.075), fill=INK500 + (255,))
        d.ellipse(B.E(tu, tv, 0.035, 0.035), fill=EMBERDIM + (255,))
    core(d, B, 0, -0.02, 0.13)


def fam_mantis(d, B, v):
    flip = -1 if v % 2 else 1
    body = [B.P(u, vv) for u, vv in [(0, -0.48), (0.15, -0.30), (0.13, 0.05), (0.09, 0.28),
                                     (0, 0.36), (-0.09, 0.28), (-0.13, 0.05), (-0.15, -0.30)]]
    shadow_poly(d, body)
    d.polygon(body, fill=mix(INK300, PAPER, 0.30) + (255,))
    d.polygon([B.P(u, vv) for u, vv in [(0.12, -0.05), (0.10, 0.26), (0, 0.33), (-0.10, 0.26), (-0.12, -0.05)]],
              fill=INK500 + (255,))  # abdomen
    for k in range(3):
        vv = 0.03 + k * 0.085
        d.rectangle(B.R(-0.105, vv, 0.105, vv + 0.045), fill=EMBERDIM + (255,))
    d.polygon([B.P(-0.13, -0.30), B.P(0.0, -0.38), B.P(-0.02, -0.12), B.P(-0.12, -0.08)], fill=mix(INK300, PAPER, 0.55) + (255,))
    for k in range(3):  # spine chevrons
        vv = -0.38 + k * 0.11
        d.polygon([B.P(-0.09, vv), B.P(0, vv + 0.045), B.P(0.09, vv), B.P(0, vv - 0.01)], fill=mix(INK300, PAPER, 0.6) + (255,))
    # big claw on flip side
    arm = [B.P(flip * 0.12, -0.02), B.P(flip * 0.34, 0.10), B.P(flip * 0.36, 0.30)]
    d.line(arm, fill=INK500 + (255,), width=int(B.bw * 0.10), joint="curve")
    d.polygon([B.P(flip * 0.36, 0.28), B.P(flip * 0.48, 0.44), B.P(flip * 0.30, 0.46)], fill=mix(INK300, PAPER, 0.65) + (255,))
    d.polygon([B.P(flip * 0.36, 0.28), B.P(flip * 0.26, 0.46), B.P(flip * 0.42, 0.48)], fill=INK300 + (255,))
    gunpod(d, B, -flip * 0.30, 0.16, w=0.13, h=0.19)
    d.ellipse(B.E(0, 0.38, 0.10, 0.09), fill=INK500 + (255,))  # head
    core(d, B, flip * 0.04, -0.10, 0.10)
    d.ellipse(B.E(0, 0.40, 0.05, 0.05), fill=EMBER + (255,))


def fam_carrier(d, B, v):
    flip = -1 if v % 2 else 1
    deck = B.R(-0.48, -0.28, 0.48, 0.20)
    shadow_rrect(d, B, deck, B.bw * 0.05)
    d.rounded_rectangle(deck, radius=B.bw * 0.05, fill=INK300 + (255,))
    d.rectangle(B.R(-0.48, -0.28, 0.48, -0.04), fill=mix(INK300, PAPER, 0.38) + (255,))  # lit fore-deck
    d.rectangle(B.R(-0.055, -0.28, 0.055, 0.20), fill=PAPER + (255,))  # runway
    for k in range(4):
        d.rectangle(B.R(-0.055, -0.22 + k * 0.11, 0.055, -0.19 + k * 0.11), fill=INK500 + (255,))
    for side in (-1, 1):
        d.rounded_rectangle(B.R(side * 0.20, -0.18, side * 0.42, 0.06), radius=B.bw * 0.03, fill=INK500 + (255,))
        d.rectangle(B.R(side * 0.20, -0.18, side * 0.42, -0.11), fill=PAPER + (255,))  # hangar roof
        d.rectangle(B.R(side * 0.24, -0.02, side * 0.38, 0.06), fill=EMBERDIM + (255,))  # hangar door
    d.polygon([B.P(-0.16, 0.20), B.P(0.16, 0.20), B.P(0, 0.34)], fill=PAPER + (255,))  # bow wedge
    d.rectangle(B.R(-0.44, 0.19, 0.44, 0.29), fill=EMBERDIM + (255,))
    gunpod(d, B, -0.34, 0.22, w=0.09, h=0.12)
    gunpod(d, B, 0.34, 0.22, w=0.09, h=0.12)
    d.line([B.P(flip * 0.40, -0.28), B.P(flip * 0.40, -0.42)], fill=INK500 + (255,), width=int(B.bw * 0.03))
    d.ellipse(B.E(flip * 0.40, -0.43, 0.03, 0.04), fill=EMBER + (255,))
    core(d, B, 0, 0.10, 0.10)


def fam_sawmill(d, B, v):
    flip = -1 if v % 2 else 1
    ch = B.R(-0.20, -0.30, 0.20, 0.26)
    shadow_rrect(d, B, ch, B.bw * 0.04)
    d.rounded_rectangle(ch, radius=B.bw * 0.04, fill=INK300 + (255,))
    d.rounded_rectangle(B.R(-0.16, -0.30, 0.16, -0.12), radius=B.bw * 0.03, fill=mix(INK300, PAPER, 0.15) + (255,))
    d.rectangle(B.R(-0.20, 0.08, 0.20, 0.16), fill=INK500 + (255,))  # dark chassis band -> spread
    for k in range(3):
        d.rectangle(B.R(-0.11 + k * 0.08, -0.26, -0.06 + k * 0.08, -0.16), fill=EMBERDIM + (255,))
    for side in (-1, 1):
        u = side * 0.31
        star(d, B, u, 0.04, 0.20, 0.155, 12, INK300, rot=0.3 * v + side * 0.15)
        star(d, B, u, 0.04, 0.165, 0.135, 12, mix(INK300, PAPER, 0.22), rot=0.3 * v + side * 0.15)
        d.ellipse(B.E(u, 0.04, 0.125, 0.135), fill=EMBERDIM + (255,))
    d.polygon([B.P(-0.20, 0.24), B.P(0.20, 0.24), B.P(0, 0.42)], fill=PAPER + (255,))  # ram
    d.rectangle(B.R(-0.18, 0.16, 0.18, 0.24), fill=EMBERDIM + (255,))
    core(d, B, flip * 0.31, 0.04, 0.075)  # destructible hub on one saw
    d.ellipse(B.E(-flip * 0.31, 0.04, 0.04, 0.045), fill=INK900 + (255,))


def fam_obelisk(d, B, v):
    flip = -1 if v % 2 else 1
    spire = [B.P(u, vv) for u, vv in [(0, -0.50), (0.17, -0.15), (0.13, 0.28), (0, 0.46), (-0.13, 0.28), (-0.17, -0.15)]]
    shadow_poly(d, spire)
    d.polygon(spire, fill=INK300 + (255,))
    d.polygon([B.P(u, vv) for u, vv in [(0, -0.50), (-0.17, -0.15), (-0.13, 0.28), (0, 0.20)]], fill=mix(INK300, PAPER, 0.42) + (255,))
    for k in range(3):
        vv = -0.28 + k * 0.17
        d.rectangle(B.R(-0.15 + k * 0.015, vv, 0.15 - k * 0.015, vv + 0.045), fill=INK500 + (255,))
    d.polygon([B.P(-0.20, 0.30), B.P(0.20, 0.30), B.P(0.10, 0.46), B.P(-0.10, 0.46)], fill=EMBERDIM + (255,))
    for side, sc in ((-1, 1.0), (1, 0.8 if v % 2 else 1.0)):  # floating sub-shards
        u, vv = side * 0.34, -0.02 + (0.10 if side == flip else -0.06)
        pts = [B.P(u, vv - 0.15 * sc), B.P(u + 0.07 * sc, vv), B.P(u, vv + 0.15 * sc), B.P(u - 0.07 * sc, vv)]
        shadow_poly(d, pts)
        d.polygon(pts, fill=(EMBERDIM if side == flip else INK500) + (255,))
        d.polygon([pts[0], pts[3], B.P(u, vv)], fill=mix(INK300, PAPER, 0.45) + (255,))
    core(d, B, 0, 0.06, 0.10)


def fam_behemoth(d, B, v):
    flip = -1 if v % 2 else 1
    tiers = [(-0.46, 0.02, 0.46, 0.34, INK300), (-0.38, -0.16, 0.38, 0.04, mix(INK500, INK300, 0.45)), (-0.28, -0.34, 0.28, -0.14, INK300)]
    shadow_rrect(d, B, B.R(*tiers[0][:4]), B.bw * 0.05)
    for u0, v0, u1, v1, col in tiers:
        d.rounded_rectangle(B.R(u0, v0, u1, v1), radius=B.bw * 0.05, fill=col + (255,))
    d.rectangle(B.R(-0.28, -0.34, 0.28, -0.27), fill=PAPER + (255,))  # top cap strip
    d.rectangle(B.R(-0.46, 0.26, 0.46, 0.34), fill=EMBERDIM + (255,))
    for side in (-1, 1):  # chimneys
        d.rectangle(B.R(side * 0.40, -0.26, side * 0.48, -0.02), fill=EMBERDIM + (255,))
        d.rectangle(B.R(side * 0.40, -0.26, side * 0.48, -0.21), fill=EMBER + (255,))
    for k in range(-3, 4):  # rivets
        if k:
            d.ellipse(B.E(k * 0.11, -0.06, 0.016, 0.02), fill=PAPER + (255,))
    # furnace mouth (destructible)
    d.pieslice(B.E(0, 0.16, 0.17, 0.18), start=0, end=180, fill=INK900 + (255,))
    d.rectangle(B.R(-0.17, 0.16, 0.17, 0.34), fill=INK900 + (255,))
    core(d, B, flip * 0.03, 0.20, 0.105, rv=0.115)


def boss_warlord(d, B, v=0):
    for k in range(4):
        a = math.radians(45 + 90 * k)
        tip = (0.46 * math.cos(a), 0.46 * math.sin(a))
        perp = a + math.pi / 2
        wdt = 0.14
        blade = [B.P(wdt * math.cos(perp), wdt * math.sin(perp)), B.P(*tip),
                 B.P(-wdt * math.cos(perp), -wdt * math.sin(perp)),
                 B.P(tip[0] * 0.42, tip[1] * 0.42)]
        d.polygon(blade, fill=mix(INK300, PAPER, 0.12) + (255,))
        d.polygon([blade[1], blade[3], B.P(tip[0] * 0.7, tip[1] * 0.7)], fill=PAPER + (255,))
        d.polygon([B.P(tip[0] * 0.18, tip[1] * 0.18), B.P(tip[0] * 0.40, tip[1] * 0.40),
                   B.P(tip[0] * 0.28 - wdt * math.cos(perp) * 0.7, tip[1] * 0.28 - wdt * math.sin(perp) * 0.7)],
                  fill=EMBERDIM + (255,))
    shadow_ellipse(d, B.E(0, 0, 0.21, 0.25))
    d.ellipse(B.E(0, 0, 0.21, 0.25), fill=INK300 + (255,))
    d.pieslice(B.E(0, 0, 0.21, 0.25), start=180, end=320, fill=mix(INK300, PAPER, 0.4) + (255,))
    core(d, B, 0, 0.0, 0.115, rv=0.135)


def boss_shieldcore(d, B, v=0):
    for rr, col, wd in ((0.44, INK300, 0.085), (0.35, EMBERDIM, 0.05), (0.27, mix(INK300, PAPER, 0.5), 0.035)):
        d.arc(B.E(0, 0.30, rr, 0.62), start=180, end=360, fill=col + (255,), width=int(B.bw * wd))
    for side in (-1, 1):  # emitter pylons
        d.rounded_rectangle(B.R(side * 0.43, 0.05, side * 0.50, 0.38), radius=B.bw * 0.02, fill=INK500 + (255,))
        d.ellipse(B.E(side * 0.465, 0.02, 0.028, 0.07), fill=EMBER + (255,))
    base = B.R(-0.22, 0.04, 0.22, 0.42)
    shadow_rrect(d, B, base, B.bw * 0.03)
    d.rounded_rectangle(base, radius=B.bw * 0.03, fill=INK300 + (255,))
    d.rectangle(B.R(-0.22, 0.04, 0.22, 0.12), fill=mix(INK300, PAPER, 0.45) + (255,))
    d.rectangle(B.R(-0.22, 0.34, 0.22, 0.42), fill=EMBERDIM + (255,))
    core(d, B, 0, 0.24, 0.085, rv=0.16)


# ---------------------------------------------------------------- B-PART @256
def part_turretcore(d, B):
    base = B.E(0, -0.04, 0.42, 0.42)
    shadow_ellipse(d, base)
    d.ellipse(base, fill=INK300 + (255,))
    d.pieslice(base, start=180, end=330, fill=mix(INK300, PAPER, 0.35) + (255,))
    d.ellipse(B.E(0, -0.04, 0.34, 0.34), outline=INK500 + (255,), width=int(B.bw * 0.06))
    d.arc(base, start=190, end=300, fill=PAPER + (255,), width=int(B.bw * 0.05))
    for side in (-1, 1):
        d.rectangle(B.R(side * 0.10, 0.10, side * 0.19, 0.44), fill=INK500 + (255,))
        d.rectangle(B.R(side * 0.10, 0.30, side * 0.19, 0.38), fill=EMBERDIM + (255,))
    d.ellipse(B.E(0, -0.04, 0.24, 0.24), fill=EMBERDIM + (255,))
    core(d, B, 0, -0.04, 0.13)


def part_clockcore(d, B):
    star(d, B, 0, 0, 0.46, 0.385, 12, INK500, rot=0.13)
    star(d, B, 0, 0, 0.435, 0.365, 12, INK300, rot=0.13)
    d.ellipse(B.E(0, 0, 0.35, 0.35), fill=EMBERDIM + (255,))
    d.ellipse(B.E(0, 0, 0.29, 0.29), fill=mix(INK300, PAPER, 0.28) + (255,))
    d.pieslice(B.E(0, 0, 0.29, 0.29), start=180, end=300, fill=PAPER + (255,))
    for k in range(12):
        a = math.radians(k * 30)
        u, vv = 0.235 * math.sin(a), -0.235 * math.cos(a)
        d.ellipse(B.E(u, vv, 0.02, 0.02), fill=INK900 + (255,))
    d.line([B.P(0, 0), B.P(-0.13, -0.15)], fill=INK900 + (255,), width=int(B.bw * 0.055))
    d.line([B.P(0, 0), B.P(0.17, -0.13)], fill=INK900 + (255,), width=int(B.bw * 0.04))
    d.line([B.P(0, 0), B.P(0.05, 0.20)], fill=EMBERDIM + (255,), width=int(B.bw * 0.025))
    core(d, B, 0, 0, 0.085)


def part_venomsac(d, B):
    for side in (-1, 1):
        for k in range(2):
            vv = -0.05 + k * 0.22
            d.line([B.P(side * 0.22, vv), B.P(side * 0.42, vv - 0.05), B.P(side * 0.50, vv + 0.10)],
                   fill=INK300 + (255,), width=int(B.bw * 0.055), joint="curve")
    abd = B.E(0, -0.04, 0.33, 0.34)
    shadow_ellipse(d, abd)
    d.ellipse(abd, fill=INK500 + (255,))
    d.pieslice(abd, start=185, end=320, fill=INK300 + (255,))
    d.ellipse(B.E(-0.10, -0.16, 0.15, 0.13), fill=TEAL + (255,))   # venom sacs (declared teal)
    d.ellipse(B.E(0.11, -0.08, 0.12, 0.11), fill=TEAL + (255,))
    d.ellipse(B.E(0.0, 0.10, 0.10, 0.09), fill=mix(TEAL, PAPER, 0.25) + (255,))
    d.ellipse(B.E(-0.13, -0.20, 0.05, 0.04), fill=mix(TEAL, PAPER, 0.55) + (255,))
    d.ellipse(B.E(0, 0.28, 0.15, 0.13), fill=INK300 + (255,))  # head stub
    d.ellipse(B.E(-0.05, 0.30, 0.03, 0.03), fill=TEAL + (255,))
    d.ellipse(B.E(0.05, 0.30, 0.03, 0.03), fill=TEAL + (255,))


def part_dualcannon(d, B):
    spine = B.R(-0.20, -0.48, 0.20, 0.48)
    shadow_rrect(d, B, spine, B.bw * 0.05)
    d.rounded_rectangle(spine, radius=B.bw * 0.05, fill=INK300 + (255,))
    d.rectangle(B.R(-0.20, -0.48, 0.20, -0.36), fill=PAPER + (255,))
    d.rectangle(B.R(-0.20, -0.48, -0.08, 0.48), fill=mix(INK300, PAPER, 0.48) + (255,))
    for k, vv in enumerate((-0.24, 0.03, 0.30)):
        d.rectangle(B.R(-0.20, vv - 0.075, 0.20, vv + 0.075), fill=INK500 + (255,))
        for side in (-1, 1):  # side cannons ("ban 2 ben")
            d.rectangle(B.R(side * 0.20, vv - 0.05, side * 0.46, vv + 0.05), fill=INK300 + (255,))
            d.rectangle(B.R(side * 0.31, vv - 0.05, side * 0.41, vv + 0.05), fill=EMBERDIM + (255,))
            d.rectangle(B.R(side * 0.43, vv - 0.05, side * 0.47, vv + 0.05), fill=INK500 + (255,))
        core(d, B, 0, vv, 0.088, rv=0.06)
    d.polygon([B.P(-0.16, 0.48), B.P(0.16, 0.48), B.P(0, 0.56)], fill=EMBERDIM + (255,))


def part_rotor(d, B):
    bar = B.R(-0.48, -0.16, 0.48, 0.16)
    shadow_rrect(d, B, bar, B.bh * 0.12)
    d.rounded_rectangle(bar, radius=B.bh * 0.12, fill=INK300 + (255,))
    d.rectangle(B.R(-0.48, -0.16, 0.48, -0.04), fill=mix(INK300, PAPER, 0.62) + (255,))
    d.rectangle(B.R(-0.48, 0.08, 0.48, 0.16), fill=INK500 + (255,))
    for side in (-1, 1):
        u = side * 0.38
        star(d, B, u, 0, 0.15, 0.11, 6, INK300, rot=side * 0.4, rv_scale=1.6)
        d.ellipse(B.E(u, 0, 0.065, 0.11), fill=EMBERDIM + (255,))
        d.ellipse(B.E(side * 0.49, 0, 0.022, 0.05), fill=EMBER + (255,))
    d.ellipse(B.E(0, 0, 0.13, 0.22), fill=INK500 + (255,))
    core(d, B, 0, 0, 0.085, rv=0.14)


def part_dockjoint(d, B):
    sq = B.R(-0.36, -0.36, 0.36, 0.36)
    shadow_rrect(d, B, sq, B.bw * 0.06)
    d.rounded_rectangle(sq, radius=B.bw * 0.06, fill=INK300 + (255,))
    d.rectangle(B.R(-0.36, -0.36, 0.36, -0.08), fill=PAPER + (255,))
    d.rounded_rectangle(B.R(-0.28, -0.28, 0.28, 0.28), radius=B.bw * 0.04, outline=EMBERDIM + (255,), width=int(B.bw * 0.105))
    for su, sv in ((-1, -1), (1, -1), (-1, 1), (1, 1)):  # clamps
        d.line([B.P(su * 0.24, sv * 0.24), B.P(su * 0.46, sv * 0.46)], fill=INK300 + (255,), width=int(B.bw * 0.09))
        d.ellipse(B.E(su * 0.46, sv * 0.46, 0.05, 0.05), fill=INK500 + (255,))
        d.polygon([B.P(su * 0.28, sv * 0.36), B.P(su * 0.36, sv * 0.36), B.P(su * 0.36, sv * 0.28)], fill=PAPER + (255,))
    d.rectangle(B.R(-0.20, -0.20, 0.20, 0.20), fill=mix(INK300, PAPER, 0.55) + (255,))
    d.rectangle(B.R(-0.135, -0.135, 0.135, 0.135), fill=INK900 + (255,))  # socket
    d.rectangle(B.R(-0.135, -0.135, 0.135, -0.075), fill=INK500 + (255,))
    core(d, B, 0.10, 0.10, 0.07)


def part_web(d, B):
    for k in range(8):
        a = math.radians(k * 45 + 10)
        col = mix(INK300, PAPER, 0.55) if k % 2 else INK300
        d.line([B.P(0, 0), B.P(0.47 * math.cos(a), 0.47 * math.sin(a))], fill=col + (255,),
               width=int(B.bw * (0.042 if k % 2 else 0.03)))
    for rr, col in ((0.16, INK300), (0.28, EMBERDIM), (0.40, INK300)):
        pts = [B.P(rr * math.cos(math.radians(k * 45 + 10)), rr * math.sin(math.radians(k * 45 + 10))) for k in range(8)]
        d.line(pts + [pts[0]], fill=col + (255,), width=int(B.bw * 0.03), joint="curve")
    for k in range(8):
        a = math.radians(k * 45 + 10)
        d.ellipse(B.E(0.28 * math.cos(a), 0.28 * math.sin(a), 0.02, 0.02), fill=EMBER + (255,))
        u, vv = 0.47 * math.cos(a), 0.47 * math.sin(a)
        d.polygon([B.P(u - 0.05, vv - 0.05), B.P(u + 0.05, vv - 0.05), B.P(u, vv + 0.065)], fill=INK500 + (255,))
    core(d, B, 0, 0, 0.072)


# ---------------------------------------------------------------- measurement (§4.9, same as W1/W2)
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
    "boss": {"val": (0.45, 0.52), "val_std": (0.20, 0.24), "dark": (0.0, 0.10), "chroma": (0.18, 0.23)},
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


def render(size, aspect, fn, seed):
    B = Box(size, aspect)
    im = Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), B)
    im = im.resize((size, size), Image.LANCZOS)
    im = light_pass(im, 0.16, 0.14)
    return add_grain(im, 0.03, seed=seed)


FAMS = [("dreadnought", fam_dreadnought, 1.25), ("spider", fam_spider, 1.10),
        ("ringfort", fam_ringfort, 1.00), ("mantis", fam_mantis, 0.72),
        ("carrier", fam_carrier, 1.45), ("sawmill", fam_sawmill, 1.20),
        ("obelisk", fam_obelisk, 0.66), ("behemoth", fam_behemoth, 1.05)]
ASPECT_JITTER = [1.00, 0.88, 1.12, 0.95]
GLYPH_IDS = [i for i in range(7001, 7019) if i not in (7007, 7008)] + \
            [i for i in range(9002, 9019) if i != 9016]

PARTS = [
    ("AP-0122", "boss", "turretcore", part_turretcore, 512 / 504),
    ("AP-0123", "boss dong ho real", "clockcore", part_clockcore, 512 / 512),
    ("AP-0124", "boss nhen doc xanh", "venomsac", part_venomsac, 512 / 506),
    ("AP-0125", "boss to vc ban 2 ben", "dualcannon", part_dualcannon, 378 / 1024),
    ("AP-0126", "minibosstronxoay", "rotor", part_rotor, 512 / 255),
    ("AP-0127", "sieuhopthe tachbophan", "dockjoint", part_dockjoint, 322 / 315),
    ("AP-0128", "web", "web", part_web, 256 / 256),
]


def main():
    # B-BODY singles
    singles = [
        ("AP-0117", "bosss", "sentinel", lambda d, B: fam_dreadnought(d, B, 1, crown=True), 150 / 126, 117),
        ("AP-0118", "bossx", "warlord", boss_warlord, 204 / 132, 118),
        ("AP-0119", "boss_shields", "shieldcore", boss_shieldcore, 82 / 42, 119),
    ]
    for row_id, base, name, fn, aspect, seed in singles:
        im = render(512, aspect, fn, seed=seed)
        emit(im, f"sprites/bodies/boss_{name}_512@ember.png",
             {"row_id": row_id, "batch": "B-BODY", "unit_no": name, "planner_base": base,
              "variant": name, "target_px": 512, "recipe": "boss"})
    # 32 glyph bosses
    fam_count = {}
    for idx, gid in enumerate(GLYPH_IDS):
        fam, fn, asp = FAMS[idx % 8]
        var = idx // 8
        fam_count[fam] = fam_count.get(fam, 0) + 1
        n = fam_count[fam]
        im = render(512, asp * ASPECT_JITTER[var], lambda d, B, f=fn, vv=var: f(d, B, vv), seed=700 + idx)
        emit(im, f"sprites/bodies/boss_{fam}{n:02d}_512@ember.png",
             {"row_id": "AP-0120", "batch": "B-BODY", "unit_no": f"{fam}{n:02d}",
              "planner_base": f"GLYPH-boss-{gid}", "variant": f"{fam}-v{var}",
              "target_px": 512, "recipe": "boss"})
    # B-PART
    for i, (row_id, base, name, fn, aspect) in enumerate(PARTS):
        im = render(256, aspect, fn, seed=900 + i)
        emit(im, f"sprites/parts/bosspart_{name}_256@ember.png",
             {"row_id": row_id, "batch": "B-PART", "unit_no": name, "planner_base": base,
              "variant": name, "target_px": 256, "recipe": "boss"})
    with open(os.path.join(HERE, "w3_units.csv"), "w", newline="", encoding="utf-8") as f:
        wcsv = csv.DictWriter(f, fieldnames=list(UNITS[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(UNITS)
    with open(os.path.join(HERE, "w3_units.json"), "w", encoding="utf-8") as f:
        json.dump(UNITS, f, indent=1, ensure_ascii=False)
    npass = sum(1 for u in UNITS if u["gate_a"] == "PASS")
    print(f"\nUNITS={len(UNITS)}  G-A PASS={npass}  FAIL={len(UNITS) - npass}")


if __name__ == "__main__":
    main()
