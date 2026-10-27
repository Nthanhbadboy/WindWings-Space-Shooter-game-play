#!/usr/bin/env python3
"""
W4 FX + ITEM sprite builder — WindWings (Godot port) · vai Art-designer · arena/5438fec9

35 units from art-planner.csv @971a7eea8:
  ITEM lane (wave W3 remainder) AP-0130..0138 I-DROP  x9   target 128  recipe item
  FX lane  AP-0082..0086 F-BOOM x5 @256 · AP-0088 F-ENEMY x1 @128 ·
           AP-0140..0159 F-GLOW x20 @256              recipe fx
Recipes (plan S4.5): fx = paper 55 · white 30 · ink300 12 · teal 3 (near-achromatic
glows, no ink900, no shadow/light-pass/grain); item = ink300 45 · gold 25 ·
paper 25 · ink500 5 (standard pipeline). G-A windows from plan S4.3, S4.9
measurement as W1-W3. Deterministic seeds. Run: python3 build_w4.py
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
WHITE = (0xFF, 0xFF, 0xFF)
GOLD = (0xF5, 0xC5, 0x18)
TEAL = (0x4F, 0xD1, 0xC5)
TEALTINT = None  # set after mix()


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


TEALTINT = mix(TEAL, PAPER, 0.82)


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


def star(d, B, u, v, r_out, r_in, teeth, fill, rot=0.0, rv_scale=1.0):
    pts = []
    for k in range(teeth * 2):
        a = rot + math.pi * k / teeth
        rr = r_out if k % 2 == 0 else r_in
        pts.append(B.P(u + rr * math.cos(a), v + rr * rv_scale * math.sin(a)))
    d.polygon(pts, fill=fill + (255,))
    return pts


def spark4(d, B, u, v, r, col, rv_scale=1.0):
    """4-point sparkle (thin diamond cross)."""
    wdt = r * 0.16
    d.polygon([B.P(u, v - r * rv_scale), B.P(u + wdt, v), B.P(u, v + r * rv_scale), B.P(u - wdt, v)], fill=col + (255,))
    d.polygon([B.P(u - r, v), B.P(u, v - wdt * rv_scale), B.P(u + r, v), B.P(u, v + wdt * rv_scale)], fill=col + (255,))


def glow_core(d, B, u, v, r, rv=None):
    rv = r if rv is None else rv
    d.ellipse(B.E(u, v, r, rv), fill=PAPER + (255,))
    d.ellipse(B.E(u, v, r * 0.60, rv * 0.60), fill=WHITE + (255,))


def halo(d, B, u, v, r, alpha=70, rv=None):
    """Faint 2-step halo (draw FIRST; alpha<128 so it stays out of S4.9 opaque stats)."""
    rv = r if rv is None else rv
    d.ellipse(B.E(u, v, r, rv), fill=PAPER + (int(alpha * 0.38),))
    d.ellipse(B.E(u, v, r * 0.78, rv * 0.78), fill=PAPER + (int(alpha * 0.75),))


def bolt(d, B, u, v, s, col):
    pts = [(0.06, -0.5), (-0.14, 0.08), (-0.02, 0.08), (-0.08, 0.5), (0.14, -0.06), (0.02, -0.06)]
    d.polygon([B.P(u + x * s, v + y * s) for x, y in pts], fill=col + (255,))


# ---------------------------------------------------------------- FX (no ink900)
def fx_bombburst(d, B):
    halo(d, B, 0, -0.05, 0.52, rv=0.55)
    for du, dv, rr in ((-0.30, -0.28, 0.11), (0.32, -0.18, 0.09), (-0.36, 0.06, 0.08), (0.30, 0.22, 0.10)):
        d.ellipse(B.E(du, dv, rr, rr), fill=INK300 + (255,))  # debris
    d.polygon([B.P(-0.20, -0.18), B.P(0.20, -0.18), B.P(0.07, 0.44), B.P(0, 0.50), B.P(-0.07, 0.44)], fill=PAPER + (255,))
    d.polygon([B.P(-0.10, -0.10), B.P(0.10, -0.10), B.P(0.03, 0.36), B.P(-0.03, 0.36)], fill=WHITE + (255,))
    glow_core(d, B, 0, -0.24, 0.24, rv=0.20)
    spark4(d, B, -0.3, -0.38, 0.09, PAPER)
    spark4(d, B, 0.34, 0.02, 0.07, PAPER)


def fx_boom(d, B):
    halo(d, B, 0, 0, 0.55)
    for k in range(8):
        a = math.radians(k * 45 + 10)
        d.ellipse(B.E(0.40 * math.cos(a), 0.40 * math.sin(a), 0.085, 0.085), fill=INK300 + (255,))
    star(d, B, 0, 0, 0.46, 0.26, 12, PAPER, rot=0.1)
    star(d, B, 0, 0, 0.32, 0.19, 12, WHITE, rot=0.32)
    glow_core(d, B, 0, 0, 0.15)


def fx_crossfire(d, B):
    halo(d, B, 0, 0, 0.52)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        tip = (0.46 * math.cos(a), 0.46 * math.sin(a))
        perp = a + math.pi / 2
        wdt = 0.075
        d.polygon([B.P(wdt * math.cos(perp), wdt * math.sin(perp)), B.P(*tip),
                   B.P(-wdt * math.cos(perp), -wdt * math.sin(perp))], fill=PAPER + (255,))
        d.polygon([B.P(tip[0] * 0.25, tip[1] * 0.25), B.P(tip[0] * 0.8, tip[1] * 0.8),
                   B.P(tip[0] * 0.25 - wdt * 0.5 * math.cos(perp), tip[1] * 0.25 - wdt * 0.5 * math.sin(perp))],
                  fill=WHITE + (255,))
    for du, dv in ((-0.30, 0), (0.30, 0), (0, -0.30), (0, 0.30)):
        d.ellipse(B.E(du, dv, 0.035, 0.035), fill=INK300 + (255,))
    glow_core(d, B, 0, 0, 0.17)


def fx_newdevice(d, B):
    halo(d, B, 0, 0, 0.5)
    d.ellipse(B.E(0, 0, 0.36, 0.36), outline=mix(INK300, PAPER, 0.35) + (255,), width=int(B.bw * 0.024))
    spark4(d, B, 0, 0, 0.34, PAPER)
    spark4(d, B, 0, 0, 0.22, WHITE)
    spark4(d, B, 0.30, -0.28, 0.10, PAPER)
    spark4(d, B, -0.32, 0.26, 0.08, WHITE)
    glow_core(d, B, 0, 0, 0.09)


def fx_sawflash(d, B):
    halo(d, B, 0, 0, 0.54)
    star(d, B, 0, 0, 0.46, 0.38, 16, INK300, rot=0.1)
    d.ellipse(B.E(0, 0, 0.36, 0.36), fill=PAPER + (255,))
    d.arc(B.E(0, 0, 0.30, 0.30), start=200, end=330, fill=WHITE + (255,), width=int(B.bw * 0.07))
    d.ellipse(B.E(0, 0, 0.20, 0.20), fill=WHITE + (255,))
    d.ellipse(B.E(0, 0, 0.07, 0.07), fill=INK300 + (255,))


def fx_enemyhit(d, B):
    halo(d, B, 0, 0, 0.44, rv=0.5)
    d.polygon([B.P(0, -0.48), B.P(0.16, 0), B.P(0, 0.48), B.P(-0.16, 0)], fill=PAPER + (255,))
    d.polygon([B.P(0, -0.36), B.P(0.08, 0), B.P(0, 0.36), B.P(-0.08, 0)], fill=WHITE + (255,))
    for dv in (-0.30, 0.30):
        d.ellipse(B.E(-0.24, dv, 0.045, 0.045), fill=INK300 + (255,))
        d.ellipse(B.E(0.24, -dv, 0.045, 0.045), fill=INK300 + (255,))
    spark4(d, B, 0, 0, 0.13, PAPER)


def fx_beemap(d, B):
    def hexp(u, v, r):
        return [B.P(u + r * math.cos(math.radians(60 * k + 30)), v + r * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    cells = [(0, 0)] + [(0.30 * math.cos(math.radians(60 * k)), 0.30 * math.sin(math.radians(60 * k))) for k in range(6)]
    halo(d, B, 0, 0, 0.55)
    for u, v in cells:
        d.polygon(hexp(u, v, 0.16), fill=INK300 + (255,))
    for i, (u, v) in enumerate(cells):
        d.polygon(hexp(u, v, 0.125), fill=PAPER + (255,))
        d.polygon(hexp(u, v, 0.07), fill=WHITE + (255,))
    d.ellipse(B.E(0, 0, 0.035, 0.035), fill=TEALTINT + (255,))


def fx_blackhole(d, B):
    halo(d, B, 0, 0, 0.55)
    d.ellipse(B.E(0, 0, 0.42, 0.30), outline=PAPER + (255,), width=int(B.bw * 0.09))
    d.ellipse(B.E(0, 0, 0.30, 0.20), outline=WHITE + (255,), width=int(B.bw * 0.05))
    d.arc(B.E(0, 0, 0.47, 0.36), start=20, end=140, fill=INK300 + (255,), width=int(B.bw * 0.05))
    d.arc(B.E(0, 0, 0.47, 0.36), start=200, end=320, fill=INK300 + (255,), width=int(B.bw * 0.05))
    d.ellipse(B.E(0, 0, 0.13, 0.09), outline=mix(INK300, PAPER, 0.3) + (255,), width=int(B.bw * 0.03))
    spark4(d, B, -0.34, -0.30, 0.08, PAPER)
    spark4(d, B, 0.36, 0.26, 0.07, WHITE)
    # center stays transparent -> the "hole" (declared)


def fx_haloring(d, B):
    halo(d, B, 0, 0, 0.54)
    d.ellipse(B.E(0, 0, 0.40, 0.40), outline=TEALTINT + (255,), width=int(B.bw * 0.13))
    d.ellipse(B.E(0, 0, 0.40, 0.40), outline=PAPER + (255,), width=int(B.bw * 0.07))
    d.ellipse(B.E(0, 0, 0.29, 0.29), outline=WHITE + (255,), width=int(B.bw * 0.035))
    d.arc(B.E(0, 0, 0.44, 0.44), start=210, end=300, fill=INK300 + (255,), width=int(B.bw * 0.03))
    spark4(d, B, 0.18, -0.36, 0.09, WHITE)


def fx_haloring2(d, B):
    halo(d, B, 0, 0, 0.54)
    d.ellipse(B.E(0, 0, 0.42, 0.42), outline=PAPER + (255,), width=int(B.bw * 0.06))
    d.ellipse(B.E(0, 0, 0.30, 0.30), outline=TEALTINT + (255,), width=int(B.bw * 0.08))
    d.ellipse(B.E(0, 0, 0.21, 0.21), outline=WHITE + (255,), width=int(B.bw * 0.03))
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        d.ellipse(B.E(0.42 * math.cos(a), 0.42 * math.sin(a), 0.04, 0.04), fill=INK300 + (255,))
    glow_core(d, B, 0, 0, 0.07)


def fx_bossmask(d, B):
    halo(d, B, 0, 0, 0.54)
    d.ellipse(B.E(0, 0, 0.42, 0.42), outline=INK300 + (255,), width=int(B.bw * 0.16))
    d.ellipse(B.E(0, 0, 0.42, 0.42), outline=PAPER + (255,), width=int(B.bw * 0.09))
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        u, v = 0.42 * math.cos(a), 0.42 * math.sin(a)
        d.rectangle(B.R(u - 0.045, v - 0.045, u + 0.045, v + 0.045), fill=INK300 + (255,))
        d.ellipse(B.E(u, v, 0.025, 0.025), fill=WHITE + (255,))
    d.ellipse(B.E(0, 0, 0.20, 0.20), outline=WHITE + (255,), width=int(B.bw * 0.03))


def fx_shatter(d, B):
    halo(d, B, 0, 0, 0.52)
    for k in range(9):
        a = math.radians(k * 40 + 8)
        L = 0.46 if k % 3 else 0.36
        col = INK300 if k % 3 == 2 else PAPER
        perp = a + math.pi / 2
        d.polygon([B.P(0.07 * math.cos(perp), 0.07 * math.sin(perp)), B.P(L * math.cos(a), L * math.sin(a)),
                   B.P(-0.07 * math.cos(perp), -0.07 * math.sin(perp))], fill=col + (255,))
    star(d, B, 0, 0, 0.17, 0.10, 8, WHITE, rot=0.2)
    glow_core(d, B, 0, 0, 0.08)


def fx_gate(d, B):
    halo(d, B, 0, 0, 0.55)
    d.ellipse(B.E(0, 0, 0.44, 0.44), outline=PAPER + (255,), width=int(B.bw * 0.07))
    sq = [B.P(0.30 * math.cos(math.radians(45 + 90 * k)), 0.30 * math.sin(math.radians(45 + 90 * k))) for k in range(4)]
    d.line(sq + [sq[0]], fill=WHITE + (255,), width=int(B.bw * 0.05), joint="curve")
    d.ellipse(B.E(0, 0, 0.22, 0.22), outline=INK300 + (255,), width=int(B.bw * 0.04))
    spark4(d, B, 0, 0, 0.15, PAPER)
    glow_core(d, B, 0, 0, 0.06)


def fx_gatesmall(d, B):
    halo(d, B, 0, 0, 0.52)
    sq = [B.P(0, -0.42), B.P(0.38, 0), B.P(0, 0.42), B.P(-0.38, 0)]
    d.line(sq + [sq[0]], fill=PAPER + (255,), width=int(B.bw * 0.09), joint="curve")
    sq2 = [B.P(0, -0.26), B.P(0.23, 0), B.P(0, 0.26), B.P(-0.23, 0)]
    d.line(sq2 + [sq2[0]], fill=WHITE + (255,), width=int(B.bw * 0.05), joint="curve")
    for u, v in sq:
        d.ellipse(B.E((u - B.cx) / B.bw, (v - B.cy) / B.bh, 0.04, 0.04), fill=INK300 + (255,))
    glow_core(d, B, 0, 0, 0.09)


def fx_ghost(d, B):
    halo(d, B, 0, -0.05, 0.5, rv=0.55)
    body = B.E(0, -0.16, 0.30, 0.30)
    d.pieslice(body, start=180, end=360, fill=PAPER + (255,))
    d.rectangle(B.R(-0.30, -0.16, 0.30, 0.28), fill=PAPER + (255,))
    d.rectangle(B.R(-0.30, 0.10, 0.30, 0.28), fill=mix(INK300, PAPER, 0.45) + (255,))
    for k in range(5):  # wavy hem
        u = -0.24 + k * 0.12
        d.ellipse(B.E(u, 0.30, 0.065, 0.09), fill=PAPER + (255,) if k % 2 else mix(INK300, PAPER, 0.45) + (255,))
    d.pieslice(B.E(0, -0.20, 0.22, 0.22), start=180, end=300, fill=WHITE + (255,))
    for du in (-0.11, 0.11):  # transparent eye holes
        d.ellipse(B.E(du, -0.12, 0.045, 0.07), fill=(0, 0, 0, 0))
    d.ellipse(B.E(0, 0.02, 0.05, 0.045), fill=(0, 0, 0, 0))
    for du in (-0.20, 0.20):
        d.ellipse(B.E(du, 0.0, 0.05, 0.035), fill=TEALTINT + (255,))


def fx_glowstreak(d, B):
    halo(d, B, 0, 0, 0.5, rv=0.36)
    d.rounded_rectangle(B.R(-0.46, -0.20, 0.46, 0.20), radius=B.bh * 0.2, fill=PAPER + (255,))
    d.rounded_rectangle(B.R(-0.34, -0.11, 0.34, 0.11), radius=B.bh * 0.11, fill=WHITE + (255,))
    for du in (-0.42, 0.42):
        d.ellipse(B.E(du, 0, 0.05, 0.09), fill=INK300 + (255,))


def fx_heal(d, B):
    halo(d, B, 0, 0.02, 0.5, rv=0.55)
    d.rectangle(B.R(-0.14, -0.30, 0.14, 0.34), fill=mix(INK300, PAPER, 0.40) + (255,))  # grey backing cross
    d.rectangle(B.R(-0.31, -0.07, 0.31, 0.11), fill=mix(INK300, PAPER, 0.40) + (255,))
    d.rectangle(B.R(-0.09, -0.34, 0.09, 0.30), fill=PAPER + (255,))
    d.rectangle(B.R(-0.26, -0.11, 0.26, 0.07), fill=PAPER + (255,))
    d.rectangle(B.R(-0.05, -0.27, 0.05, 0.23), fill=WHITE + (255,))
    d.rectangle(B.R(-0.19, -0.07, 0.19, 0.03), fill=WHITE + (255,))
    for du, dv, rr in ((-0.24, -0.34, 0.05), (0.26, -0.22, 0.04), (0.0, 0.42, 0.045)):
        d.ellipse(B.E(du, dv, rr, rr), fill=PAPER + (255,))
    for du, dv in ((-0.30, 0.18), (0.30, 0.24)):
        d.ellipse(B.E(du, dv, 0.035, 0.035), fill=INK300 + (255,))
    spark4(d, B, 0.28, -0.36, 0.08, WHITE)


def fx_lastbossmark(d, B):
    halo(d, B, 0, 0, 0.52)
    d.rectangle(B.R(-0.36, 0.02, 0.36, 0.22), fill=INK300 + (255,))
    d.rectangle(B.R(-0.36, 0.02, 0.36, 0.09), fill=PAPER + (255,))
    for k, du in enumerate((-0.26, 0.0, 0.26)):
        h = 0.30 if k == 1 else 0.22
        d.polygon([B.P(du - 0.10, 0.04), B.P(du, -h), B.P(du + 0.10, 0.04)], fill=PAPER + (255,))
        d.ellipse(B.E(du, 0.15, 0.045, 0.045), fill=WHITE + (255,))
    spark4(d, B, 0, -0.34, 0.10, WHITE)


def fx_lightshaft(d, B):
    halo(d, B, 0, 0, 0.55)
    d.ellipse(B.E(0, 0, 0.34, 0.34), outline=INK300 + (255,), width=int(B.bw * 0.03))
    for k in range(12):
        a = math.radians(k * 30)
        L = 0.47 if k % 2 == 0 else 0.34
        perp = a + math.pi / 2
        wdt = 0.045
        d.polygon([B.P(0.12 * math.cos(a) + wdt * math.cos(perp), 0.12 * math.sin(a) + wdt * math.sin(perp)),
                   B.P(L * math.cos(a), L * math.sin(a)),
                   B.P(0.12 * math.cos(a) - wdt * math.cos(perp), 0.12 * math.sin(a) - wdt * math.sin(perp))],
                  fill=PAPER + (255,))
    glow_core(d, B, 0, 0, 0.20)


def fx_overtimebar(d, B):
    halo(d, B, 0, 0, 0.52, rv=0.62)
    d.rounded_rectangle(B.R(-0.48, -0.30, 0.48, 0.30), radius=B.bh * 0.3, fill=PAPER + (255,))
    d.rectangle(B.R(-0.48, 0.14, 0.48, 0.30), fill=mix(INK300, PAPER, 0.35) + (255,))
    d.rounded_rectangle(B.R(-0.38, -0.16, 0.38, 0.16), radius=B.bh * 0.16, fill=WHITE + (255,))
    for du in (-0.455, 0.455):
        d.rectangle(B.R(du - 0.035, -0.30, du + 0.035, 0.30), fill=INK300 + (255,))


def fx_talentpoint(d, B):
    halo(d, B, 0, 0, 0.5)
    d.polygon([B.P(0, -0.40), B.P(0.26, 0), B.P(0, 0.40), B.P(-0.26, 0)], fill=PAPER + (255,))
    d.polygon([B.P(0, -0.26), B.P(0.16, 0), B.P(0, 0.26), B.P(-0.16, 0)], fill=WHITE + (255,))
    d.polygon([B.P(0, -0.40), B.P(0.26, 0), B.P(0, -0.08)], fill=INK300 + (255,))
    spark4(d, B, 0.30, -0.28, 0.09, PAPER)


def fx_squareglow(d, B):
    halo(d, B, 0, 0, 0.54)
    d.rounded_rectangle(B.R(-0.36, -0.36, 0.36, 0.36), radius=B.bw * 0.08, fill=PAPER + (255,))
    d.rounded_rectangle(B.R(-0.24, -0.24, 0.24, 0.24), radius=B.bw * 0.05, fill=WHITE + (255,))
    for su, sv in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        d.polygon([B.P(su * 0.36, sv * 0.22), B.P(su * 0.36, sv * 0.36), B.P(su * 0.22, sv * 0.36)], fill=INK300 + (255,))


def fx_superpower(d, B):
    halo(d, B, 0, 0.05, 0.52)
    for dy, sc, col in ((0.16, 1.0, PAPER), (-0.08, 0.8, PAPER)):
        d.polygon([B.P(-0.36 * sc, dy + 0.16), B.P(0, dy - 0.10), B.P(0.36 * sc, dy + 0.16),
                   B.P(0.36 * sc, dy + 0.02), B.P(0, dy - 0.24), B.P(-0.36 * sc, dy + 0.02)], fill=col + (255,))
    d.polygon([B.P(-0.20, 0.10), B.P(0, -0.02), B.P(0.20, 0.10), B.P(0.20, 0.02), B.P(0, -0.10), B.P(-0.20, 0.02)],
              fill=WHITE + (255,))
    d.rectangle(B.R(-0.30, 0.36, 0.30, 0.42), fill=INK300 + (255,))
    spark4(d, B, 0, -0.36, 0.11, WHITE)


def fx_victorybar(d, B):
    halo(d, B, 0, 0, 0.52, rv=0.7)
    d.rounded_rectangle(B.R(-0.48, -0.26, 0.48, 0.26), radius=B.bh * 0.26, fill=PAPER + (255,))
    d.rectangle(B.R(-0.48, 0.12, 0.48, 0.26), fill=mix(INK300, PAPER, 0.35) + (255,))
    d.rounded_rectangle(B.R(-0.40, -0.13, 0.40, 0.13), radius=B.bh * 0.13, fill=WHITE + (255,))
    for du in (-0.455, 0.455):
        d.rectangle(B.R(du - 0.032, -0.26, du + 0.032, 0.26), fill=INK300 + (255,))
    star(d, B, 0, 0, 0.10, 0.045, 5, PAPER, rot=-math.pi / 2, rv_scale=2.2)
    star(d, B, 0, 0, 0.055, 0.028, 5, WHITE, rot=-math.pi / 2, rv_scale=2.2)


def fx_powerup(d, B):
    halo(d, B, 0, 0, 0.52)
    d.ellipse(B.E(0, 0, 0.40, 0.40), outline=INK300 + (255,), width=int(B.bw * 0.10))
    d.ellipse(B.E(0, 0, 0.40, 0.40), outline=PAPER + (255,), width=int(B.bw * 0.06))
    d.polygon([B.P(0, -0.26), B.P(0.17, -0.02), B.P(0.06, -0.02), B.P(0.06, 0.24), B.P(-0.06, 0.24),
               B.P(-0.06, -0.02), B.P(-0.17, -0.02)], fill=WHITE + (255,))
    spark4(d, B, 0.30, -0.30, 0.08, PAPER)


def fx_circleset(d, B):
    halo(d, B, 0, 0, 0.55)
    kinds = ["ring", "spark", "disc", "spark", "core", "ring", "disc", "ring", "spark"]
    for i, kind in enumerate(kinds):
        r, c = divmod(i, 3)
        u, v = -0.30 + c * 0.30, -0.30 + r * 0.30
        if kind == "ring":
            d.ellipse(B.E(u, v, 0.11, 0.11), outline=PAPER + (255,), width=int(B.bw * 0.045))
            d.ellipse(B.E(u, v, 0.05, 0.05), outline=INK300 + (255,), width=int(B.bw * 0.02))
        elif kind == "disc":
            d.ellipse(B.E(u, v, 0.10, 0.10), fill=PAPER + (255,))
            d.ellipse(B.E(u, v, 0.05, 0.05), fill=WHITE + (255,))
        elif kind == "core":
            glow_core(d, B, u, v, 0.11)
        else:
            spark4(d, B, u, v, 0.12, PAPER)


# ---------------------------------------------------------------- ITEMS (standard pipeline)
def shadow_ellipse(d, box, off=SS):
    d.ellipse([box[0] + off, box[1] + off, box[2] + off, box[3] + off], fill=INK900 + (255,))


def shadow_rrect(d, box, rad, off=SS):
    d.rounded_rectangle([box[0] + off, box[1] + off, box[2] + off, box[3] + off], radius=rad, fill=INK900 + (255,))


def it_cellamber(d, B):
    body = B.R(-0.26, -0.34, 0.26, 0.40)
    shadow_rrect(d, body, B.bw * 0.12)
    d.rounded_rectangle(body, radius=B.bw * 0.12, fill=INK300 + (255,))
    d.rounded_rectangle(B.R(-0.16, -0.18, 0.16, 0.20), radius=B.bw * 0.07, fill=GOLD + (255,))
    d.rounded_rectangle(B.R(-0.26, -0.34, 0.26, -0.16), radius=B.bw * 0.10, fill=mix(INK300, PAPER, 0.82) + (255,))
    d.rectangle(B.R(-0.08, -0.44, 0.08, -0.34), fill=mix(INK300, PAPER, 0.82) + (255,))
    d.rectangle(B.R(-0.26, 0.30, 0.26, 0.40), fill=INK500 + (255,))
    bolt(d, B, 0, 0.02, 0.34, PAPER)


def it_cellround(d, B):
    disc = B.E(0, 0, 0.42, 0.42)
    shadow_ellipse(d, disc)
    d.ellipse(disc, fill=INK300 + (255,))
    d.pieslice(disc, start=180, end=320, fill=mix(INK300, PAPER, 0.35) + (255,))
    d.ellipse(B.E(0, 0, 0.275, 0.275), fill=GOLD + (255,))
    d.ellipse(B.E(0, 0, 0.19, 0.19), fill=PAPER + (255,))
    bolt(d, B, 0, 0, 0.26, GOLD)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        d.ellipse(B.E(0.36 * math.cos(a), 0.36 * math.sin(a), 0.035, 0.035), fill=INK500 + (255,))


def it_crate(d, B):
    box = B.R(-0.38, -0.34, 0.38, 0.38)
    shadow_rrect(d, box, B.bw * 0.05)
    d.rounded_rectangle(box, radius=B.bw * 0.05, fill=INK300 + (255,))
    d.rectangle(B.R(-0.38, -0.34, 0.38, -0.14), fill=mix(INK300, PAPER, 0.7) + (255,))
    for du in (-0.38, 0.315):
        d.rectangle(B.R(du, -0.34, du + 0.065, 0.38), fill=GOLD + (255,))
    d.rectangle(B.R(-0.38, 0.315, 0.38, 0.38), fill=GOLD + (255,))
    d.rectangle(B.R(-0.38, -0.02, 0.38, 0.06), fill=INK500 + (255,))
    star(d, B, 0, 0.15, 0.11, 0.05, 5, GOLD, rot=-math.pi / 2)
    star(d, B, 0, 0.15, 0.06, 0.03, 5, PAPER, rot=-math.pi / 2)


def it_lootbag(d, B):
    sack = B.E(0, 0.10, 0.40, 0.34)
    shadow_ellipse(d, sack)
    d.ellipse(sack, fill=mix(INK300, PAPER, 0.18) + (255,))
    d.pieslice(sack, start=185, end=330, fill=mix(INK300, PAPER, 0.5) + (255,))
    d.polygon([B.P(-0.12, -0.14), B.P(0.12, -0.14), B.P(0.06, -0.30), B.P(-0.06, -0.30)], fill=INK300 + (255,))
    d.rectangle(B.R(-0.14, -0.19, 0.14, -0.08), fill=GOLD + (255,))
    for du, dv, rr in ((-0.20, -0.24, 0.115), (-0.03, -0.33, 0.125), (0.14, -0.30, 0.11), (0.26, -0.18, 0.085)):
        d.ellipse(B.E(du, dv, rr, rr * 0.8), fill=GOLD + (255,))
        d.ellipse(B.E(du - rr * 0.3, dv - rr * 0.25, rr * 0.35, rr * 0.28), fill=PAPER + (255,))
    d.rounded_rectangle(B.R(-0.17, 0.10, 0.12, 0.32), radius=B.bw * 0.04, fill=PAPER + (255,))
    d.pieslice(B.E(0.05, 0.16, 0.30, 0.24), start=30, end=150, fill=INK500 + (255,))


def it_banana(d, B):
    # thick ink300 crescent shell (boomerang cell) + thin gold inlay stripe + paper ridge
    d.pieslice(B.E(0, 0.30, 0.48, 0.62), start=190, end=350, fill=mix(INK300, PAPER, 0.28) + (255,))
    d.pieslice(B.E(0, 0.02, 0.44, 0.60), start=190, end=350, fill=(0, 0, 0, 0))  # hollow -> thick crescent
    d.arc(B.E(0, 0.17, 0.455, 0.585), start=202, end=338, fill=GOLD + (255,), width=int(B.bh * 0.21))
    d.arc(B.E(0, 0.27, 0.465, 0.605), start=212, end=328, fill=PAPER + (255,), width=int(B.bh * 0.055))
    for du in (-0.40, 0.40):  # tip caps
        d.ellipse(B.E(du, -0.12, 0.055, 0.10), fill=INK500 + (255,))
    d.rounded_rectangle(B.R(-0.09, -0.38, 0.09, -0.14), radius=B.bw * 0.05, fill=mix(INK300, PAPER, 0.28) + (255,))  # grip block
    d.rectangle(B.R(-0.09, -0.38, 0.09, -0.29), fill=PAPER + (255,))


def it_landingfoot(d, B):
    shadow_rrect(d, B.R(-0.34, 0.05, 0.40, 0.34), B.bw * 0.06)
    d.rounded_rectangle(B.R(-0.16, -0.38, 0.14, 0.10), radius=B.bw * 0.06, fill=mix(INK300, PAPER, 0.15) + (255,))  # shin
    d.rectangle(B.R(-0.16, -0.38, 0.14, -0.24), fill=mix(INK300, PAPER, 0.6) + (255,))
    d.rectangle(B.R(-0.06, -0.22, 0.04, -0.06), fill=GOLD + (255,))  # shin stripe
    d.ellipse(B.E(-0.01, 0.02, 0.17, 0.17), fill=GOLD + (255,))  # ankle joint
    d.ellipse(B.E(-0.01, 0.02, 0.07, 0.07), fill=INK500 + (255,))
    d.rounded_rectangle(B.R(-0.34, 0.05, 0.40, 0.28), radius=B.bw * 0.07, fill=mix(INK300, PAPER, 0.15) + (255,))  # foot block
    d.rounded_rectangle(B.R(0.10, 0.05, 0.40, 0.21), radius=B.bw * 0.06, fill=PAPER + (255,))  # toe plate
    d.rectangle(B.R(-0.34, 0.28, 0.40, 0.38), fill=INK500 + (255,))  # sole
    d.rectangle(B.R(-0.32, 0.11, -0.02, 0.23), fill=GOLD + (255,))


def it_fullpower(d, B):
    body = B.R(-0.28, -0.30, 0.28, 0.42)
    shadow_rrect(d, body, B.bw * 0.08)
    d.rounded_rectangle(body, radius=B.bw * 0.08, fill=INK300 + (255,))
    d.rectangle(B.R(-0.10, -0.42, 0.10, -0.30), fill=mix(INK300, PAPER, 0.65) + (255,))
    d.rounded_rectangle(B.R(-0.28, -0.30, 0.28, -0.12), radius=B.bw * 0.08, fill=mix(INK300, PAPER, 0.65) + (255,))
    for k in range(3):
        vv = -0.04 + k * 0.14
        d.rounded_rectangle(B.R(-0.21, vv, 0.21, vv + 0.10), radius=B.bw * 0.03, fill=GOLD + (255,))
    d.rectangle(B.R(-0.28, 0.34, 0.28, 0.42), fill=INK500 + (255,))
    bolt(d, B, 0, 0.12, 0.42, PAPER)


def it_bosshead(d, B):
    helm = B.R(-0.34, -0.36, 0.34, 0.30)
    shadow_rrect(d, helm, B.bw * 0.14)
    d.rounded_rectangle(helm, radius=B.bw * 0.14, fill=INK300 + (255,))
    d.polygon([B.P(-0.05, -0.50), B.P(0.05, -0.50), B.P(0.10, -0.34), B.P(-0.10, -0.34)], fill=PAPER + (255,))  # crest
    d.rounded_rectangle(B.R(-0.34, -0.36, 0.34, -0.16), radius=B.bw * 0.12, fill=mix(INK300, PAPER, 0.35) + (255,))
    d.rounded_rectangle(B.R(-0.27, -0.08, 0.27, 0.13), radius=B.bw * 0.07, fill=GOLD + (255,))  # visor
    d.rectangle(B.R(-0.27, 0.012, 0.27, 0.04), fill=INK500 + (255,))
    d.rounded_rectangle(B.R(-0.20, 0.18, 0.20, 0.38), radius=B.bw * 0.06, fill=INK500 + (255,))  # jaw
    for du in (-0.10, 0.0, 0.10):
        d.rectangle(B.R(du - 0.025, 0.22, du + 0.025, 0.34), fill=PAPER + (255,))
    d.line([B.P(0.30, -0.30), B.P(0.42, -0.46)], fill=INK300 + (255,), width=int(B.bw * 0.05))
    d.ellipse(B.E(0.43, -0.47, 0.05, 0.05), fill=GOLD + (255,))
    for side in (-1, 1):
        d.ellipse(B.E(side * 0.30, 0.16, 0.06, 0.09), fill=GOLD + (255,))


def it_orechunk(d, B):
    rock = [B.P(u, v) for u, v in [(-0.30, -0.28), (0.05, -0.42), (0.36, -0.20), (0.42, 0.14),
                                   (0.20, 0.38), (-0.14, 0.42), (-0.40, 0.16), (-0.38, -0.12)]]
    d.polygon([(x + SS, y + SS) for x, y in rock], fill=INK900 + (255,))
    d.polygon(rock, fill=mix(INK300, PAPER, 0.12) + (255,))
    d.polygon([B.P(-0.30, -0.28), B.P(0.05, -0.42), B.P(0.14, -0.02), B.P(-0.22, 0.06)], fill=PAPER + (255,))
    d.polygon([B.P(0.14, -0.02), B.P(0.36, -0.20), B.P(0.42, 0.14), B.P(0.10, 0.18)], fill=INK500 + (255,))
    d.polygon([B.P(-0.22, 0.06), B.P(0.10, 0.18), B.P(0.20, 0.38), B.P(-0.14, 0.42), B.P(-0.40, 0.16)],
              fill=mix(INK300, PAPER, 0.35) + (255,))
    for u, v, s in ((-0.14, -0.14, 0.17), (0.20, 0.02, 0.14), (-0.04, 0.22, 0.15), (0.26, -0.24, 0.10)):  # gold crystals
        d.polygon([B.P(u, v - s), B.P(u + s * 0.7, v + s * 0.4), B.P(u - s * 0.2, v + s * 0.8), B.P(u - s * 0.7, v + s * 0.2)],
                  fill=GOLD + (255,))


# ---------------------------------------------------------------- measurement (§4.9)
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
    "fx": {"val": (0.70, 0.90), "val_std": (0.15, 0.25), "dark": (0.0, 0.02), "chroma": (0.0, 0.08)},
    "item": {"val": (0.62, 0.70), "val_std": (0.22, 0.28), "dark": (0.0, 0.05), "chroma": (0.25, 0.30)},
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


def render(size, aspect, fn, seed, fx_mode=False):
    B = Box(size, aspect)
    im = Image.new("RGBA", (B.W, B.H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), B)
    im = im.resize((size, size), Image.LANCZOS)
    if fx_mode:
        return im  # glows: no light-pass / grain (declared)
    im = light_pass(im, 0.16, 0.14)
    return add_grain(im, 0.03, seed=seed)


FX_ROWS = [
    ("AP-0082", "F-BOOM", "bomb", "bombburst", fx_bombburst, 256, 84 / 128),
    ("AP-0083", "F-BOOM", "boom", "boom", fx_boom, 256, 256 / 256),
    ("AP-0084", "F-BOOM", "crossfire", "crossfire", fx_crossfire, 256, 227 / 256),
    ("AP-0085", "F-BOOM", "newdevice", "newdevice", fx_newdevice, 256, 99 / 99),
    ("AP-0086", "F-BOOM", "saw", "sawflash", fx_sawflash, 256, 256 / 256),
    ("AP-0088", "F-ENEMY", "fxenemy", "enemyhit", fx_enemyhit, 128, 70 / 128),
    ("AP-0140", "F-GLOW", "beemap", "beemap", fx_beemap, 256, 330 / 314),
    ("AP-0141", "F-GLOW", "blackhold", "blackhole", fx_blackhole, 256, 128 / 128),
    ("AP-0142", "F-GLOW", "circle_blue", "haloring", fx_haloring, 256, 256 / 256),
    ("AP-0143", "F-GLOW", "circle_blue copy", "haloring2", fx_haloring2, 256, 256 / 256),
    ("AP-0144", "F-GLOW", "circle_mask_bigboss", "bossmask", fx_bossmask, 256, 128 / 128),
    ("AP-0145", "F-GLOW", "fx_footbroken", "shatter", fx_shatter, 256, 256 / 248),
    ("AP-0146", "F-GLOW", "gate", "gate", fx_gate, 256, 512 / 512),
    ("AP-0147", "F-GLOW", "gatenho", "gatesmall", fx_gatesmall, 256, 256 / 231),
    ("AP-0148", "F-GLOW", "ghost", "ghost", fx_ghost, 256, 420 / 512),
    ("AP-0149", "F-GLOW", "glow", "glowstreak", fx_glowstreak, 256, 153 / 107),
    ("AP-0150", "F-GLOW", "heal", "heal", fx_heal, 256, 65 / 98),
    ("AP-0151", "F-GLOW", "lastboss", "lastbossmark", fx_lastbossmark, 256, 62 / 59),
    ("AP-0152", "F-GLOW", "light", "lightshaft", fx_lightshaft, 256, 256 / 256),
    ("AP-0153", "F-GLOW", "overtime", "overtimebar", fx_overtimebar, 256, 433 / 37),
    ("AP-0154", "F-GLOW", "point_talent", "talentpoint", fx_talentpoint, 256, 64 / 64),
    ("AP-0155", "F-GLOW", "square64x", "squareglow", fx_squareglow, 256, 64 / 64),
    ("AP-0156", "F-GLOW", "supperpower", "superpower", fx_superpower, 256, 113 / 87),
    ("AP-0157", "F-GLOW", "victory", "victorybar", fx_victorybar, 256, 453 / 35),
    ("AP-0158", "F-GLOW", "powerup", "powerup", fx_powerup, 256, 97 / 87),
    ("AP-0159", "F-GLOW", "circle", "circleset", fx_circleset, 256, 256 / 256),
]

ITEM_ROWS = [
    ("AP-0130", "05_0", "cellamber", it_cellamber, 69 / 82),
    ("AP-0131", "05_1", "cellround", it_cellround, 68 / 65),
    ("AP-0132", "5_1", "crate", it_crate, 241 / 284),
    ("AP-0133", "bag", "lootbag", it_lootbag, 486 / 338),
    ("AP-0134", "banana", "banana", it_banana, 124 / 60),
    ("AP-0135", "foot", "landingfoot", it_landingfoot, 128 / 128),
    ("AP-0136", "fullpower", "fullpower", it_fullpower, 74 / 113),
    ("AP-0137", "head", "bosshead", it_bosshead, 511 / 1024),
    ("AP-0138", "rock", "orechunk", it_orechunk, 150 / 182),
]


def main():
    for i, (row_id, base, name, fn, aspect) in enumerate(ITEM_ROWS):
        im = render(128, aspect, fn, seed=400 + i)
        emit(im, f"sprites/items/item_{name}_128@gold.png",
             {"row_id": row_id, "batch": "I-DROP", "unit_no": name, "planner_base": base,
              "variant": name, "target_px": 128, "recipe": "item"})
    for i, (row_id, batch, base, name, fn, size, aspect) in enumerate(FX_ROWS):
        im = render(size, aspect, fn, seed=600 + i, fx_mode=True)
        emit(im, f"sprites/fx/fx_{name}_{size}@paper.png",
             {"row_id": row_id, "batch": batch, "unit_no": name, "planner_base": base,
              "variant": name, "target_px": size, "recipe": "fx"})
    with open(os.path.join(HERE, "w4_units.csv"), "w", newline="", encoding="utf-8") as f:
        wcsv = csv.DictWriter(f, fieldnames=list(UNITS[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(UNITS)
    with open(os.path.join(HERE, "w4_units.json"), "w", encoding="utf-8") as f:
        json.dump(UNITS, f, indent=1, ensure_ascii=False)
    npass = sum(1 for u in UNITS if u["gate_a"] == "PASS")
    print(f"\nUNITS={len(UNITS)}  G-A PASS={npass}  FAIL={len(UNITS) - npass}")


if __name__ == "__main__":
    main()
