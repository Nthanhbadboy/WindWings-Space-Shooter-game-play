#!/usr/bin/env python3
"""
art/mecha25d.py — v2 Commercial Aerospace & Mecha Multi-Component Assembly Engine
for Variant B ("Solar Neon 2.5D", branch arena/eca8588b-windwings-space-shooter-game-p).

Fixes double-mirror bug (`orient(pts, s)`), eliminates protruding chassis bars, grounds metallic
tone curves to match AI-painted hero ships #01 & #04, aligns iconic silhouette classes across #01..#25
(including Astrolabe Halo-Rings #06/#08/#10/#11, Transformable Mecha-Valkyries #12/#23, Twin-Prong
Gunships #04/#07/#17, Tri-Hull Nacelles #15/#21, Stealth Phantoms #16/#22, and Twin-Turbine Stealth
Prototype #25), and integrates sleek military tactical asymmetry on every craft.
"""

from __future__ import annotations

import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import pbr25d

GUNMETAL = ((84, 96, 118), (28, 34, 48), (156, 174, 202))
DARK_STEEL = ((58, 68, 86), (22, 26, 38), (122, 138, 166))
CHROME_TRIM = ((196, 210, 232), (96, 114, 144), (248, 252, 255))


def orient(pts: list[tuple[float, float]], side: int) -> list[tuple[float, float]]:
    """Preserve clockwise winding when coordinates already applied `cx + side * dx`."""
    return pts if side == 1 else list(reversed(pts))


def reg_poly(cx: float, cy: float, rx: float, ry: float, n: int = 20, rot: float = 0.0):
    return [(cx + math.cos(rot + 2 * math.pi * k / n) * rx, cy + math.sin(rot + 2 * math.pi * k / n) * ry) for k in range(n)]


def ring_sector(cx: float, cy: float, r_out: float, r_in: float, a0: float, a1: float, steps: int = 18):
    outer = [(cx + math.cos(a) * r_out, cy + math.sin(a) * r_out) for a in np.linspace(a0, a1, steps)]
    inner = [(cx + math.cos(a) * r_in, cy + math.sin(a) * r_in) for a in np.linspace(a1, a0, steps)]
    return outer + inner


def metal(canvas: Image.Image, pts, triple, *, greebles=True, glow_c=None, chamfer=0.12, metallic=0.90):
    pbr25d.draw_25d_metal_poly(
        canvas, pts, triple[0], triple[1], triple[2],
        metallic=metallic, greebles=greebles, cast_ao=True, glow_vent_c=glow_c, chamfer=chamfer,
    )


def draw_jet_nozzle(canvas: Image.Image, cx: float, y_top: float, w: float, h: float, glow_rgb=(0, 228, 255), pointing_down: bool = True):
    d_sign = 1.0 if pointing_down else -1.0
    y_end = y_top + d_sign * h
    collar = [
        (cx - w * 0.56, y_top),
        (cx + w * 0.56, y_top),
        (cx + w * 0.48, y_top + d_sign * h * 0.48),
        (cx - w * 0.48, y_top + d_sign * h * 0.48),
    ]
    metal(canvas, collar if pointing_down else list(reversed(collar)), GUNMETAL, greebles=False, chamfer=0.08)
    for k in (-2, -1, 0, 1, 2):
        px = cx + k * (w * 0.18)
        pw = w * 0.13
        petal = [
            (px - pw, y_top + d_sign * h * 0.36),
            (px + pw, y_top + d_sign * h * 0.36),
            (px + pw * 0.78, y_end),
            (px - pw * 0.78, y_end),
        ]
        metal(canvas, petal if pointing_down else list(reversed(petal)), DARK_STEEL if k % 2 else GUNMETAL, greebles=False, chamfer=0.05)
    pbr25d.draw_25d_plasma_bloom(canvas, cx, y_end + d_sign * 4, w * 0.32, h * 0.22, glow_rgb, intensity=0.82)


def draw_gun_barrel(canvas: Image.Image, cx: float, y_base: float, y_tip: float, w: float = 34.0, barrels: int = 2, glow_rgb=(0, 228, 255)):
    d_sign = 1.0 if y_tip > y_base else -1.0
    mid_y = y_base + (y_tip - y_base) * 0.52
    housing = [
        (cx - w * 0.62, y_base),
        (cx + w * 0.62, y_base),
        (cx + w * 0.52, mid_y),
        (cx - w * 0.52, mid_y),
    ]
    metal(canvas, housing if d_sign < 0 else list(reversed(housing)), GUNMETAL, greebles=False, chamfer=0.10)
    offsets = [0.0] if barrels == 1 else ([-w * 0.24, w * 0.24] if barrels == 2 else [-w * 0.30, 0.0, w * 0.30])
    bw = w * (0.24 if barrels == 1 else 0.15)
    for ox in offsets:
        bx = cx + ox
        brl = [(bx - bw, mid_y), (bx + bw, mid_y), (bx + bw * 0.85, y_tip), (bx - bw * 0.85, y_tip)]
        metal(canvas, brl, DARK_STEEL, greebles=False, chamfer=0.04)
        muz = [(bx - bw * 1.25, y_tip - d_sign * 14), (bx + bw * 1.25, y_tip - d_sign * 14), (bx + bw * 1.1, y_tip), (bx - bw * 1.1, y_tip)]
        metal(canvas, muz, CHROME_TRIM, greebles=False, chamfer=0.04)
        pbr25d.draw_25d_plasma_bloom(canvas, bx, y_tip, bw * 1.0, 7.0, glow_rgb, intensity=0.60)


def draw_ribbed_spine(canvas: Image.Image, cx: float, y0: float, y1: float, w_top: float, w_bot: float, n_ribs: int = 6):
    """Compact dark brushed-gunmetal mechanical spine tucked cleanly inside the wing roots."""
    body = [
        (cx - w_top, y0), (cx + w_top, y0),
        (cx + w_bot * 1.06, (y0 + y1) * 0.54),
        (cx + w_bot, y1), (cx - w_bot, y1),
        (cx - w_bot * 1.06, (y0 + y1) * 0.54),
    ]
    metal(canvas, body, DARK_STEEL, greebles=False, chamfer=0.10)
    for k in range(n_ribs):
        t = (k + 0.6) / (n_ribs + 0.2)
        ry = y0 + (y1 - y0) * t
        rw = (w_top * (1.0 - t) + w_bot * t) * 0.94
        rh = max(7.0, abs(y1 - y0) / (n_ribs * 2.8))
        rib = [(cx - rw, ry - rh), (cx + rw, ry - rh), (cx + rw, ry + rh), (cx - rw, ry + rh)]
        metal(canvas, rib, GUNMETAL, greebles=False, chamfer=0.06)


def draw_plasma_trough(canvas: Image.Image, cx: float, cy: float, w: float, h: float, glow_rgb=(0, 232, 255), cells: int = 4, angle: float = 0.0):
    ca, sa = math.cos(angle), math.sin(angle)

    def rot(dx, dy):
        return (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)

    well = [rot(-w * 0.5, -h * 0.5), rot(w * 0.5, -h * 0.5), rot(w * 0.5, h * 0.5), rot(-w * 0.5, h * 0.5)]
    metal(canvas, well, DARK_STEEL, greebles=False, chamfer=0.14)
    for k in range(cells):
        ty = -h * 0.36 + (h * 0.72) * (k / max(1, cells - 1)) if cells > 1 else 0.0
        px, py = rot(0.0, ty)
        pbr25d.draw_25d_plasma_bloom(canvas, px, py, w * 0.38, (h / max(1, cells)) * 0.48, glow_rgb, intensity=1.02)
    for k in range(cells - 1):
        ty = -h * 0.36 + (h * 0.72) * ((k + 0.5) / max(1, cells - 1))
        rib = [rot(-w * 0.52, ty - 4.5), rot(w * 0.52, ty - 4.5), rot(w * 0.52, ty + 4.5), rot(-w * 0.52, ty + 4.5)]
        metal(canvas, rib, GUNMETAL, greebles=False, chamfer=0.04)


def draw_framed_cockpit(canvas: Image.Image, cx: float, cy: float, rx: float, ry: float, glass_triple, frame_triple):
    collar = reg_poly(cx, cy, rx * 1.22, ry * 1.18, 10, rot=math.pi / 10)
    metal(canvas, collar, frame_triple, greebles=False, chamfer=0.12)
    glass_pts = [
        (cx, cy - ry),
        (cx + rx * 0.86, cy - ry * 0.34),
        (cx + rx, cy + ry * 0.32),
        (cx + rx * 0.58, cy + ry),
        (cx - rx * 0.58, cy + ry),
        (cx - rx, cy + ry * 0.32),
        (cx - rx * 0.86, cy - ry * 0.34),
    ]
    pbr25d.draw_25d_glass_dome(canvas, glass_pts, glass_triple[0], glass_triple[1], glass_triple[2])
    for yf, wf in [(-0.22, 0.88), (0.34, 0.96)]:
        by = cy + ry * yf
        bw = rx * wf
        bow = [(cx - bw, by - 5.0), (cx + bw, by - 5.0), (cx + bw, by + 5.0), (cx - bw, by + 5.0)]
        metal(canvas, bow, frame_triple, greebles=False, chamfer=0.06)


def draw_tactical_asymmetry(canvas: Image.Image, cx: float, wing_x: float, wing_y: float, idx: int, L: dict):
    """Sleek, aerodynamic military tactical asymmetry integrated cleanly onto wing hardpoints (like #01 & #04)."""
    mode = idx % 4
    if mode == 0:
        # Starboard compact AWACS armored radome disc + Port extended twin Gatling barrels!
        rx, ry = cx + wing_x * 0.62, wing_y - 26
        metal(canvas, reg_poly(rx, ry, 44, 44, 18), GUNMETAL, greebles=False, chamfer=0.0)
        metal(canvas, reg_poly(rx, ry, 28, 28, 16), L["acc"], greebles=False, chamfer=0.0)
        draw_gun_barrel(canvas, cx - wing_x * 0.62, wing_y + 12, wing_y - 135, w=36, barrels=2, glow_rgb=L["glow"])
    elif mode == 1:
        # Port 4-cell micro-missile pod + Starboard extended sniper plasma barrel!
        mx, my = cx - wing_x * 0.64, wing_y - 12
        pod = [(mx - 34, my - 44), (mx + 34, my - 44), (mx + 38, my + 44), (mx - 38, my + 44)]
        metal(canvas, pod, GUNMETAL, greebles=False, chamfer=0.12)
        for ox in (-14, 14):
            for oy in (-16, 16):
                metal(canvas, reg_poly(mx + ox, my + oy, 9, 9, 10), L["acc"], greebles=False, chamfer=0.0)
        draw_gun_barrel(canvas, cx + wing_x * 0.64, wing_y + 18, wing_y - 155, w=32, barrels=1, glow_rgb=L["glow"])
    elif mode == 2:
        # Starboard swept telemetry blade fin + Port plasma capacitor pod!
        ax, ay = cx + wing_x * 0.72, wing_y - 18
        ant = [(ax - 10, ay + 38), (ax + 14, ay + 38), (ax + 24, ay - 135), (ax + 4, ay - 152)]
        metal(canvas, ant, L["acc"], greebles=False, chamfer=0.08)
        draw_plasma_trough(canvas, cx - wing_x * 0.62, wing_y - 8, 38, 92, L["glow"], cells=3)
    else:
        # Port triple rotary cannon + Starboard auxiliary vernier pod!
        draw_gun_barrel(canvas, cx - wing_x * 0.65, wing_y + 8, wing_y - 128, w=40, barrels=3, glow_rgb=L["glow"])
        vx, vy = cx + wing_x * 0.64, wing_y + 4
        vpod = [(vx - 30, vy - 54), (vx + 34, vy - 38), (vx + 30, vy + 54), (vx - 28, vy + 46)]
        metal(canvas, vpod, L["sec"], greebles=False, chamfer=0.14)


_AI_CACHE: dict[str, Image.Image] = {}


def load_polished_ai_ship(raw_path: str, rot_270: bool = True, widen: float = 1.24) -> Image.Image | None:
    key = f"{raw_path}:{rot_270}:{widen}"
    if key in _AI_CACHE:
        return _AI_CACHE[key].copy()
    if not os.path.exists(raw_path):
        return None
    im = Image.open(raw_path).convert("RGB")
    if rot_270:
        im = im.transpose(Image.ROTATE_270)
    arr = np.asarray(im, dtype=np.float32)
    H, W, _ = arr.shape
    patches = np.concatenate([
        arr[:10, :10].reshape(-1, 3), arr[:10, -10:].reshape(-1, 3),
        arr[-10:, :10].reshape(-1, 3), arr[-10:, -10:].reshape(-1, 3),
    ], axis=0)
    bg = np.median(patches, axis=0)
    diff = np.sqrt(np.sum((arr - bg) ** 2, axis=2))

    passable = diff < 92.0
    cur = np.zeros((H, W), dtype=bool)
    cur[0, :] = passable[0, :]; cur[-1, :] = passable[-1, :]; cur[:, 0] = passable[:, 0]; cur[:, -1] = passable[:, -1]
    for filt_sz in (15, 3):
        prev = -1
        while True:
            s = int(cur.sum())
            if s == prev:
                break
            prev = s
            dil = np.asarray(Image.fromarray(cur.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(filt_sz))) > 0
            cur = (cur | dil) & passable

    fg_hard = ~cur
    bg_dil = np.asarray(Image.fromarray(cur.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(5))) > 0
    edge_band = fg_hard & bg_dil
    alpha = np.where(edge_band, np.clip((diff - 44.0) / 86.0, 0.0, 1.0), fg_hard.astype(np.float32))
    alpha = np.asarray(Image.fromarray((alpha * 255.0).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255.0
    alpha = np.where(alpha < 0.05, 0.0, np.clip((alpha - 0.05) / 0.91, 0.0, 1.0))

    despill_zone = np.asarray(Image.fromarray(cur.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(9))) > 0
    a_safe = np.maximum(alpha, 0.14)[..., None]
    unmixed = np.clip((arr - (1.0 - alpha[..., None]) * bg) / a_safe, 0.0, 255.0)
    out_rgb = np.where((alpha[..., None] < 0.96) & (alpha[..., None] > 0.0), unmixed, arr)
    excess_m = np.maximum(0.0, np.minimum(out_rgb[:, :, 0], out_rgb[:, :, 2]) - out_rgb[:, :, 1] - 32.0)
    out_rgb[:, :, 0] = np.where(despill_zone, out_rgb[:, :, 0] - excess_m * 0.70, out_rgb[:, :, 0])
    out_rgb[:, :, 2] = np.where(despill_zone, out_rgb[:, :, 2] - excess_m * 0.80, out_rgb[:, :, 2])

    rgb_im = Image.fromarray(np.clip(out_rgb, 0, 255).astype(np.uint8), "RGB")
    rgb_im = ImageEnhance.Brightness(rgb_im).enhance(1.16)
    rgb_im = ImageEnhance.Color(rgb_im).enhance(1.24)
    rgb_im = ImageEnhance.Contrast(rgb_im).enhance(1.08)

    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    rgba[:, :, :3] = np.asarray(rgb_im, dtype=np.uint8)
    rgba[:, :, 3] = (alpha * 255.0).astype(np.uint8)
    rgba[rgba[:, :, 3] == 0] = [0, 0, 0, 0]

    ys, xs = np.where(rgba[:, :, 3] > 16)
    crop = Image.fromarray(rgba[int(ys.min()):int(ys.max()) + 1, int(xs.min()):int(xs.max()) + 1], "RGBA")
    cw, ch = int(crop.width * widen), crop.height
    scale = (1024 * 0.88) / max(cw, ch)
    nw, nh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))

    ca = np.asarray(crop, dtype=np.float32)
    al = ca[:, :, 3:4] / 255.0
    pm = np.concatenate([ca[:, :, :3] * al, ca[:, :, 3:4]], axis=2)
    pm_r = np.asarray(Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), "RGBA").resize((nw, nh), Image.LANCZOS), dtype=np.float32)
    na = pm_r[:, :, 3:4] / 255.0
    rgb_s = np.where(na > 1e-3, pm_r[:, :, :3] / np.maximum(na, 1e-3), 0.0)
    st = np.concatenate([np.clip(rgb_s, 0, 255), pm_r[:, :, 3:4]], axis=2).astype(np.uint8)
    st[st[:, :, 3] < 5] = [0, 0, 0, 0]

    master = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    master.alpha_composite(Image.fromarray(st, "RGBA"), ((1024 - nw) // 2, (1024 - nh) // 2))
    _AI_CACHE[key] = master
    return master.copy()


# Map each of the 25 player ship slots to an iconic commercial class aligned with WindWings' fleet variety!
# 0=GullWing, 1=TwinProng, 2=AstrolabeRing, 3=MechaValkyrie, 4=TriHullNacelle, 5=SpearheadDelta, 6=StealthBat, 7=TwinBoomCarrier, 8=TwinFanStealth25
SHIP_CLASS_MAP = {
    1: 0,  2: 0,  3: 7,  4: 1,  5: 5,
    6: 2,  7: 1,  8: 2,  9: 5,  10: 2,
    11: 2, 12: 3, 13: 0, 14: 7, 15: 4,
    16: 6, 17: 1, 18: 5, 19: 7, 20: 5,
    21: 4, 22: 6, 23: 3, 24: 4, 25: 8,
}


def render_commercial_ship(idx: int, L: dict, raw_dir: str) -> Image.Image:
    """Render 1 of 25 commercial-grade 2.5D semi-realistic metallic starfighters (1024x1024 master)."""
    masters_parent = os.path.dirname(raw_dir.rstrip("/"))
    baked_path = os.path.join(masters_parent, f"hero_painted_{idx:02d}_1024.png")
    if idx in (1, 4, 8, 12, 13) and os.path.exists(baked_path):
        return Image.open(baked_path).convert("RGBA")
    if idx == 1:
        m = load_polished_ai_ship(os.path.join(raw_dir, "ship_01_raw.png"), rot_270=True, widen=1.24)
        if m is not None:
            return m
    if idx == 4:
        m = load_polished_ai_ship(os.path.join(raw_dir, "ship_04_raw.png"), rot_270=True, widen=1.28)
        if m is not None:
            return m

    S = 1024
    cx = 512.0
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cls = SHIP_CLASS_MAP[idx]
    tier = (idx - 1) // 6  # 0..4 progressive weapon/wing evolution

    # Special #25: Brushed Gunmetal Twin-Rotor Stealth Prototype (inspired by ships-01 #25!)
    if cls == 8:
        for s in (-1, 1):
            draw_jet_nozzle(im, cx + s * 112, 785, 86, 82, L["glow"], pointing_down=True)
            wing = [
                (cx + s * 86, 315), (cx + s * 468, 465), (cx + s * 476, 635),
                (cx + s * 345, 765), (cx + s * 245, 675), (cx + s * 98, 695),
            ]
            metal(im, orient(wing, s), L["sec"], glow_c=L["glow"])
            # Recessed circular VTOL stealth lift-fan turbine in each wing!
            fx, fy = cx + s * 258, 515
            metal(im, reg_poly(fx, fy, 118, 118, 26), L["hull"], greebles=False)
            metal(im, reg_poly(fx, fy, 86, 86, 22), DARK_STEEL, greebles=False)
            for b in range(6):
                ba = b * math.pi / 3 + 0.2
                blade = [
                    (fx + math.cos(ba) * 18, fy + math.sin(ba) * 18),
                    (fx + math.cos(ba + 0.32) * 82, fy + math.sin(ba + 0.32) * 82),
                    (fx + math.cos(ba + 0.55) * 78, fy + math.sin(ba + 0.55) * 78),
                ]
                metal(im, blade, GUNMETAL, greebles=False, chamfer=0.02)
            metal(im, reg_poly(fx, fy, 28, 28, 14), L["acc"], greebles=False)
        draw_tactical_asymmetry(im, cx, 365, 485, idx, L)
        fus = [(cx, 118), (cx + 98, 265), (cx + 118, 665), (cx, 845), (cx - 118, 665), (cx - 98, 265)]
        metal(im, fus, L["hull"], glow_c=L["glow"])
        draw_framed_cockpit(im, cx, 425, 58, 112, L["glass"], GUNMETAL)
        return im

    # 1. Rear multi-petal jet turbine nozzles
    if cls in (1, 4, 7) or tier >= 2:
        for nx_off, ny_off, nw in [(-124, 838, 80), (-50, 862, 74), (50, 862, 74), (124, 838, 80)]:
            draw_jet_nozzle(im, cx + nx_off, ny_off, nw, 80, L["glow"], pointing_down=True)
    else:
        for nx_off in (-74, 74):
            draw_jet_nozzle(im, cx + nx_off, 846, 94, 88, L["glow"], pointing_down=True)

    # 2. Compact central dark-gunmetal spine (tucked strictly inside fuselage & inner wing roots!)
    draw_ribbed_spine(im, cx, 185, 845, 76, 128, n_ribs=7)

    # 3. Underslung forward multi-barrel weapon batteries
    for s in (-1, 1):
        draw_gun_barrel(im, cx + s * (152 + (idx % 3) * 14), 455, 205 - tier * 14, w=38, barrels=2, glow_rgb=L["glow"])

    # 4. Eight distinct commercial spacecraft classes (both left & right wings properly oriented!)
    if cls == 0:
        # CLASS I: Vanguard Swept Gull-Wing Starfighter
        span = 456 + (idx % 3) * 12
        for s in (-1, 1):
            outer_w = [
                (cx + s * 135, 415), (cx + s * span, 555), (cx + s * (span + 14), 695),
                (cx + s * 335, 735), (cx + s * 255, 655), (cx + s * 125, 675),
            ]
            metal(im, orient(outer_w, s), L["sec"], glow_c=L["glow"])
            tip = [(cx + s * (span - 22), 505), (cx + s * (span + 18), 542), (cx + s * (span + 22), 738), (cx + s * (span - 18), 712)]
            metal(im, orient(tip, s), L["acc"], greebles=False)
            mid_w = [(cx + s * 92, 335), (cx + s * 318, 468), (cx + s * 288, 638), (cx + s * 98, 612)]
            metal(im, orient(mid_w, s), L["hull"], glow_c=L["glow"])
            draw_plasma_trough(im, cx + s * 172, 432, 44, 102, L["glow"], cells=3, angle=s * 0.24)
            tail = [(cx + s * 82, 695), (cx + s * 208, 765), (cx + s * 182, 902), (cx + s * 72, 862)]
            metal(im, orient(tail, s), L["acc"], greebles=False)

        draw_tactical_asymmetry(im, cx, 355, 545, idx, L)
        aft_spine = [(cx - 104, 495), (cx + 104, 495), (cx + 122, 845), (cx, 902), (cx - 122, 845)]
        metal(im, aft_spine, L["sec"], glow_c=L["glow"])
        fore_hull = [(cx, 68), (cx + 86, 215), (cx + 122, 525), (cx + 74, 785), (cx - 74, 785), (cx - 122, 525), (cx - 86, 215)]
        metal(im, fore_hull, L["hull"], glow_c=L["glow"])
        nose_cap = [(cx, 64), (cx + 56, 198), (cx, 252), (cx - 56, 198)]
        metal(im, nose_cap, L["acc"], greebles=False)
        draw_framed_cockpit(im, cx, 428, 56, 116, L["glass"], GUNMETAL)

    elif cls == 1:
        # CLASS II: Twin-Prong Mandible Heavy Plasma Gunship
        for s in (-1, 1):
            paul_o = [(cx + s * 165, 365), (cx + s * 462, 485), (cx + s * 448, 685), (cx + s * 312, 775), (cx + s * 168, 665)]
            metal(im, orient(paul_o, s), L["acc"], glow_c=L["glow"])
            paul_i = [(cx + s * 125, 315), (cx + s * 356, 435), (cx + s * 332, 695), (cx + s * 135, 735)]
            metal(im, orient(paul_i, s), L["sec"], glow_c=L["glow"])
            prong = [
                (cx + s * 92, 435), (cx + s * 232, 365), (cx + s * 248, 152),
                (cx + s * 168, 78), (cx + s * 112, 128), (cx + s * 96, 335),
            ]
            metal(im, orient(prong, s), L["hull"], glow_c=L["glow"])
            draw_plasma_trough(im, cx + s * 158, 238, 48, 162, L["glow"], cells=4)

        draw_tactical_asymmetry(im, cx, 375, 535, idx, L)
        core_hull = [(cx, 205), (cx + 128, 315), (cx + 144, 765), (cx, 882), (cx - 144, 765), (cx - 128, 315)]
        metal(im, core_hull, L["hull"], glow_c=L["glow"])
        collar_plate = [(cx - 92, 615), (cx + 92, 615), (cx + 68, 825), (cx - 68, 825)]
        metal(im, collar_plate, L["acc"], greebles=False)
        draw_framed_cockpit(im, cx, 465, 68, 110, L["glass"], GUNMETAL)

    elif cls == 2:
        # CLASS III: Astrolabe Orbital Halo-Ring Gunship (#06, #08, #10, #11)
        r_ring = 436 - (idx % 2) * 16
        for q in range(8):
            a0 = q * math.pi * 0.25 + 0.04
            a1 = a0 + math.pi * 0.25 - 0.08
            arc = ring_sector(cx, 512, r_ring, r_ring - 64, a0, a1, steps=12)
            metal(im, arc, GUNMETAL if q % 2 else L["acc"], greebles=False, chamfer=0.02)
        # 4 Heavy Notched Gyro-Clamp Brackets around the Astrolabe Ring!
        for ca in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
            clamp = ring_sector(cx, 512, r_ring + 22, r_ring - 82, ca - 0.11, ca + 0.11, steps=8)
            metal(im, clamp, L["sec"], greebles=False, chamfer=0.03)
        for s in (-1, 1):
            pylon = [(cx + s * 98, 365), (cx + s * (r_ring - 16), 445), (cx + s * (r_ring - 28), 575), (cx + s * 112, 625)]
            metal(im, orient(pylon, s), L["sec"], glow_c=L["glow"])
            cpod = [
                (cx + s * 108, 285), (cx + s * 228, 225), (cx + s * 268, 355),
                (cx + s * 242, 725), (cx + s * 118, 695),
            ]
            metal(im, orient(cpod, s), L["hull"], glow_c=L["glow"])
            draw_plasma_trough(im, cx + s * 188, 455, 42, 132, L["glow"], cells=3)
            draw_gun_barrel(im, cx + s * 186, 255, 84, w=48, barrels=2, glow_rgb=L["glow"])
            pbr25d.draw_25d_plasma_bloom(im, cx + s * 180, 718, 34, 34, L["glow"], intensity=1.05)

        draw_tactical_asymmetry(im, cx, 385, 495, idx, L)
        body = [(cx, 118), (cx + 118, 265), (cx + 138, 565), (cx + 78, 805), (cx - 78, 805), (cx - 138, 565), (cx - 118, 265)]
        metal(im, body, L["hull"], glow_c=L["glow"])
        nose_chev = [(cx, 112), (cx + 76, 245), (cx, 298), (cx - 76, 245)]
        metal(im, nose_chev, L["acc"], greebles=False)
        draw_framed_cockpit(im, cx, 435, 62, 112, L["glass"], GUNMETAL)

    elif cls == 3:
        # CLASS IV: Transformable Mecha-Valkyrie Striker (#12, #23) — swept V-pauldrons & splayed thrusters!
        for s in (-1, 1):
            # Swept upper wing-binder (angled aggressively upward & outward like REF #12!)
            binder = [(cx + s * 115, 315), (cx + s * 468, 195), (cx + s * 442, 345), (cx + s * 295, 425), (cx + s * 135, 415)]
            metal(im, orient(binder, s), L["sec"], glow_c=L["glow"])
            # Layered spiked Mecha Shoulder Pauldron!
            shld = [(cx + s * 88, 285), (cx + s * 296, 215), (cx + s * 318, 365), (cx + s * 224, 465), (cx + s * 98, 435)]
            metal(im, orient(shld, s), L["hull"], glow_c=L["glow"])
            shld_trim = [(cx + s * 132, 268), (cx + s * 282, 224), (cx + s * 266, 305), (cx + s * 145, 335)]
            metal(im, orient(shld_trim, s), L["acc"], greebles=False)
            # Articulated Forearm Gauntlet
            arm = [(cx + s * 172, 435), (cx + s * 316, 485), (cx + s * 292, 655), (cx + s * 182, 615)]
            metal(im, orient(arm, s), GUNMETAL, greebles=False)
            # Splayed Armored Thruster Leg + Knee Guard + Side Skirt!
            skirt = [(cx + s * 52, 545), (cx + s * 195, 575), (cx + s * 172, 705), (cx + s * 58, 675)]
            metal(im, orient(skirt, s), L["sec"], greebles=False)
            leg = [(cx + s * 72, 645), (cx + s * 204, 665), (cx + s * 246, 885), (cx + s * 108, 912)]
            metal(im, orient(leg, s), L["hull"], glow_c=L["glow"])
            knee = [(cx + s * 98, 625), (cx + s * 192, 645), (cx + s * 184, 748), (cx + s * 104, 735)]
            metal(im, orient(knee, s), L["acc"], greebles=False)
            draw_jet_nozzle(im, cx + s * 176, 895, 68, 56, L["glow"], pointing_down=True)

        # Asymmetric Mecha Loadout: Starboard long-barrel beam rifle + Port plasma saber!
        draw_gun_barrel(im, cx + 272, 505, 96, w=46, barrels=1, glow_rgb=L["glow"])
        saber_hilt = [(cx - 302, 485), (cx - 242, 485), (cx - 232, 585), (cx - 312, 585)]
        metal(im, saber_hilt, L["acc"], greebles=False)
        saber_blade = [(cx - 276, 108), (cx - 238, 245), (cx - 254, 490), (cx - 292, 490)]
        metal(im, saber_blade, CHROME_TRIM, greebles=False, glow_c=L["glow"])
        pbr25d.draw_25d_plasma_bloom(im, cx - 270, 290, 24, 168, L["glow"], intensity=0.92)

        # Tapered V-Chest Mecha Torso + Twin Golden Chest Intakes!
        torso = [(cx - 138, 295), (cx + 138, 295), (cx + 92, 615), (cx - 92, 615)]
        metal(im, torso, GUNMETAL, greebles=True)
        chest = [(cx, 255), (cx + 128, 315), (cx + 96, 515), (cx, 585), (cx - 96, 515), (cx - 128, 315)]
        metal(im, chest, L["hull"], glow_c=L["glow"])
        for s in (-1, 1):
            intake = [(cx + s * 36, 325), (cx + s * 112, 342), (cx + s * 98, 412), (cx + s * 38, 398)]
            metal(im, orient(intake, s), L["acc"], greebles=False)
        head = [(cx, 128), (cx + 56, 198), (cx + 44, 282), (cx - 44, 282), (cx - 56, 198)]
        metal(im, head, L["hull"], greebles=False)
        for s in (-1, 1):
            vfin = [(cx + s * 14, 175), (cx + s * 126, 72), (cx + s * 96, 138), (cx + s * 28, 205)]
            metal(im, orient(vfin, s), L["acc"], greebles=False, chamfer=0.04)
        draw_framed_cockpit(im, cx, 445, 46, 78, L["glass"], GUNMETAL)

    elif cls == 4:
        # CLASS V: Tri-Hull Outboard-Nacelle Heavy Striker (#15, #21, #24)
        for s in (-1, 1):
            truss = [(cx + s * 92, 415), (cx + s * 365, 455), (cx + s * 365, 585), (cx + s * 92, 595)]
            metal(im, orient(truss, s), GUNMETAL, greebles=True)
            shoulder = [(cx + s * 102, 365), (cx + s * 262, 415), (cx + s * 242, 615), (cx + s * 102, 625)]
            metal(im, orient(shoulder, s), L["acc"], glow_c=L["glow"])
            nac_x = cx + s * 368
            draw_jet_nozzle(im, nac_x, 735, 76, 76, L["glow"], pointing_down=True)
            draw_gun_barrel(im, nac_x, 315, 148, w=40, barrels=2, glow_rgb=L["glow"])
            nac = [
                (nac_x, 215), (nac_x + 76, 315), (nac_x + 84, 685),
                (nac_x + 46, 755), (nac_x - 46, 755), (nac_x - 84, 685), (nac_x - 76, 315),
            ]
            metal(im, nac, L["hull"], glow_c=L["glow"])
            draw_plasma_trough(im, nac_x, 465, 44, 148, L["glow"], cells=4)

        draw_tactical_asymmetry(im, cx, 235, 485, idx, L)
        for s in (-1, 1):
            vtail = [(cx + s * 44, 715), (cx + s * 172, 835), (cx + s * 122, 918), (cx + s * 28, 835)]
            metal(im, orient(vtail, s), L["acc"], greebles=False)
        hull = [(cx, 74), (cx + 94, 235), (cx + 116, 565), (cx + 66, 845), (cx - 66, 845), (cx - 116, 565), (cx - 94, 235)]
        metal(im, hull, L["sec"], glow_c=L["glow"])
        spine = [(cx, 118), (cx + 66, 285), (cx + 74, 685), (cx, 795), (cx - 74, 685), (cx - 66, 285)]
        metal(im, spine, L["hull"], glow_c=L["glow"])
        draw_framed_cockpit(im, cx, 395, 52, 110, L["glass"], L["acc"])

    elif cls == 5:
        # CLASS VI: Bio-Tech Spearhead Delta Interceptor (#05, #09, #18, #20)
        for s in (-1, 1):
            fin = [(cx + s * 86, 485), (cx + s * 458, 735), (cx + s * 418, 878), (cx + s * 126, 735)]
            metal(im, orient(fin, s), L["sec"], glow_c=L["glow"])
            mid_f = [(cx + s * 76, 315), (cx + s * 322, 565), (cx + s * 268, 715), (cx + s * 86, 635)]
            metal(im, orient(mid_f, s), L["hull"], glow_c=L["glow"])

        draw_tactical_asymmetry(im, cx, 335, 625, idx, L)
        spear_cowl = [(cx, 64), (cx + 152, 265), (cx + 96, 335), (cx, 245), (cx - 96, 335), (cx - 152, 265)]
        metal(im, spear_cowl, L["acc"], glow_c=L["glow"])
        fus = [(cx, 195), (cx + 126, 365), (cx + 144, 685), (cx, 875), (cx - 144, 685), (cx - 126, 365)]
        metal(im, fus, L["hull"], glow_c=L["glow"])
        collar = [(cx - 136, 555), (cx + 136, 555), (cx + 96, 685), (cx - 96, 685)]
        metal(im, collar, L["acc"], greebles=False)
        draw_framed_cockpit(im, cx, 415, 62, 110, L["glass"], GUNMETAL)
        metal(im, reg_poly(cx, 695, 74, 74, 20), GUNMETAL, greebles=False)
        pbr25d.draw_25d_plasma_bloom(im, cx, 695, 48, 48, L["glow"], intensity=1.15)

    elif cls == 6:
        # CLASS VII: Forward-Swept Scalloped Stealth Phantom (#16, #22)
        for s in (-1, 1):
            bat = [
                (cx + s * 90, 285), (cx + s * 285, 345), (cx + s * 382, 215),
                (cx + s * 476, 465), (cx + s * 452, 655), (cx + s * 315, 565),
                (cx + s * 225, 665), (cx + s * 106, 585),
            ]
            metal(im, orient(bat, s), L["sec"], glow_c=L["glow"])
            rib_w = [(cx + s * 86, 315), (cx + s * 345, 415), (cx + s * 285, 535), (cx + s * 96, 495)]
            metal(im, orient(rib_w, s), L["hull"], glow_c=L["glow"])
            draw_plasma_trough(im, cx + s * 245, 425, 38, 124, L["glow"], cells=3, angle=-s * 0.42)
            fang = [(cx + s * 56, 695), (cx + s * 146, 755), (cx + s * 110, 918), (cx + s * 40, 835)]
            metal(im, orient(fang, s), L["acc"], greebles=False)

        draw_tactical_asymmetry(im, cx, 355, 465, idx, L)
        fus = [(cx, 62), (cx + 94, 245), (cx + 116, 595), (cx, 914), (cx - 116, 595), (cx - 94, 245)]
        metal(im, fus, L["hull"], glow_c=L["glow"])
        for ky in (285, 545, 665):
            rib = [(cx, ky - 34), (cx + 80, ky + 14), (cx, ky + 46), (cx - 80, ky + 14)]
            metal(im, rib, CHROME_TRIM, greebles=False)
        draw_framed_cockpit(im, cx, 415, 52, 114, L["glass"], L["acc"])

    else:
        # CLASS VIII: Sovereign Twin-Boom Forward-Canard Heavy Carrier (#03, #14, #19)
        for s in (-1, 1):
            canard = [(cx + s * 76, 225), (cx + s * 268, 175), (cx + s * 248, 295), (cx + s * 86, 325)]
            metal(im, orient(canard, s), L["acc"], greebles=False)
            main_w = [(cx + s * 116, 395), (cx + s * 468, 515), (cx + s * 452, 715), (cx + s * 136, 685)]
            metal(im, orient(main_w, s), L["hull"], glow_c=L["glow"])
            boom = [(cx + s * 175, 315), (cx + s * 265, 335), (cx + s * 276, 855), (cx + s * 165, 855)]
            metal(im, orient(boom, s), L["sec"], glow_c=L["glow"])
            draw_gun_barrel(im, cx + s * 218, 325, 118, w=44, barrels=2, glow_rgb=L["glow"])

        draw_tactical_asymmetry(im, cx, 385, 575, idx, L)
        fus = [(cx, 68), (cx + 106, 225), (cx + 126, 685), (cx, 855), (cx - 126, 685), (cx - 106, 225)]
        metal(im, fus, L["hull"], glow_c=L["glow"])
        metal(im, reg_poly(cx, 645, 76, 76, 18), GUNMETAL, greebles=False)
        metal(im, reg_poly(cx, 645, 50, 50, 14), L["acc"], greebles=False)
        draw_framed_cockpit(im, cx, 395, 60, 114, L["glass"], GUNMETAL)

    return im


def render_commercial_drone(idx: int, L: dict) -> Image.Image:
    """Render 1 of 13 commercial-grade articulated escort weapon drones (512x512 2x master)."""
    baked = os.path.join(os.path.dirname(__file__), "w1-player-b", "masters", f"drone_painted_{idx:02d}_1024.png")
    if idx in (4, 5) and os.path.exists(baked):
        return pbr25d.downsample_straight_rgba(Image.open(baked).convert("RGBA"), (512, 512))
    S = 512
    cx, cy = 256.0, 268.0
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cls = (idx - 1) % 4

    draw_jet_nozzle(im, cx, 412, 66, 54, L["glow"], pointing_down=True)

    if cls == 0:
        # DRONE CLASS 1: Heavy Sniper-Turret Gun-Pod + Rear Articulated Claws (both port & starboard!)
        draw_gun_barrel(im, cx + (12 if idx % 2 else 0), 215, 34, w=54, barrels=1, glow_rgb=L["glow"])
        for s in (-1, 1):
            claw = [(cx + s * 66, 325), (cx + s * 148, 355), (cx + s * 118, 468), (cx + s * 56, 435)]
            metal(im, orient(claw, s), L["sec"], greebles=False)
            shld = [(cx + s * 60, 195), (cx + s * 162, 235), (cx + s * 150, 355), (cx + s * 66, 345)]
            metal(im, orient(shld, s), L["acc"], glow_c=L["glow"])
        pod = [(cx - 82, 168), (cx + 82, 168), (cx + 98, 365), (cx, 418), (cx - 98, 365)]
        metal(im, pod, L["hull"], glow_c=L["glow"])
        draw_framed_cockpit(im, cx, 275, 40, 62, L["glass"], GUNMETAL)

    elif cls == 1:
        # DRONE CLASS 2: Armored Scarab Assault Pod + Twin Hinged Outer Mandibles + Plasma Vents
        for s in (-1, 1):
            mand = [(cx + s * 92, 245), (cx + s * 212, 285), (cx + s * 216, 395), (cx + s * 158, 468), (cx + s * 112, 375)]
            metal(im, orient(mand, s), L["sec"], glow_c=L["glow"])
            metal(im, reg_poly(cx + s * 142, 295, 22, 22, 14), GUNMETAL, greebles=False, chamfer=0.0)
        shell = [(cx, 54), (cx + 118, 128), (cx + 128, 325), (cx + 68, 428), (cx - 68, 428), (cx - 128, 325), (cx - 118, 128)]
        metal(im, shell, L["hull"], glow_c=L["glow"])
        nose = [(cx, 48), (cx + 68, 98), (cx + 42, 152), (cx - 42, 152), (cx - 68, 98)]
        metal(im, nose, GUNMETAL, greebles=False)
        for s in (-1, 1):
            draw_plasma_trough(im, cx + s * 68, 215, 26, 88, L["glow"], cells=3)
        draw_plasma_trough(im, cx, 368, 52, 74, L["glow"], cells=4)

    elif cls == 2:
        # DRONE CLASS 3: Wide Saucer-Collar Shield/Beam Turret + Twin Antenna Horns + Twin Side Guns
        for s in (-1, 1):
            horn = [(cx + s * 58, 138), (cx + s * 128, 62), (cx + s * 146, 82), (cx + s * 86, 158)]
            metal(im, orient(horn, s), L["acc"], greebles=False, chamfer=0.04)
            draw_gun_barrel(im, cx + s * 192, 265, 168, w=36, barrels=1, glow_rgb=L["glow"])
            jaw = [(cx + s * 62, 345), (cx + s * 148, 355), (cx + s * 112, 455), (cx + s * 48, 425)]
            metal(im, orient(jaw, s), L["sec"], greebles=False)
        saucer = reg_poly(cx, 258, 198, 146, 22)
        metal(im, saucer, L["hull"], glow_c=L["glow"])
        dome = reg_poly(cx, 288, 108, 96, 18)
        metal(im, dome, L["acc"], glow_c=L["glow"])
        metal(im, reg_poly(cx, 162, 40, 32, 16), GUNMETAL, greebles=False, chamfer=0.0)
        pbr25d.draw_25d_plasma_bloom(im, cx, 162, 24, 18, L["glow"], intensity=1.10)

    else:
        # DRONE CLASS 4: Swept Quad-Blade Interceptor Drone + Asymmetric Port Autocannon
        for s in (-1, 1):
            fore_b = [(cx + s * 58, 148), (cx + s * 198, 98), (cx + s * 218, 225), (cx + s * 88, 235)]
            metal(im, orient(fore_b, s), L["acc"], greebles=False)
            aft_b = [(cx + s * 78, 235), (cx + s * 228, 335), (cx + s * 188, 445), (cx + s * 68, 365)]
            metal(im, orient(aft_b, s), L["sec"], glow_c=L["glow"])
        draw_gun_barrel(im, cx - 135, 225, 76, w=32, barrels=2, glow_rgb=L["glow"])
        body = [(cx, 92), (cx + 108, 185), (cx + 96, 375), (cx, 425), (cx - 96, 375), (cx - 108, 185)]
        metal(im, body, L["hull"], glow_c=L["glow"])
        draw_framed_cockpit(im, cx, 248, 46, 70, L["glass"], GUNMETAL)

    return im
