"""kitbash25d.py — Commercial 2.5D Painted Modular Kitbash & Multi-Band Anodizing Engine.

Constructs distinct, silhouette-diverse player starfighters, escort drones, dedicated
enemy invader hulls, boss dreadnoughts, and modular boss sub-parts exclusively from
branch-owned commercial 2.5D painted masters — eliminating all flat/toy-plastic
procedural holdovers and prohibiting cross-role reuse (enemies never reuse player
drones or boss icons).
"""
from __future__ import annotations

import math
import os
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

ART_ROOT = os.path.dirname(os.path.abspath(__file__))
_MASTER_CACHE: dict[str, Image.Image] = {}


def load_master(rel_from_art: str) -> Image.Image:
    if rel_from_art not in _MASTER_CACHE:
        p = os.path.join(ART_ROOT, rel_from_art)
        _MASTER_CACHE[rel_from_art] = Image.open(p).convert("RGBA")
    return _MASTER_CACHE[rel_from_art].copy()


def _premul_resize_rotate(im: Image.Image, new_w: int, new_h: int, angle_deg: float = 0.0) -> Image.Image:
    """Premultiplied-alpha resize & optional rotation so edges never develop dark halos."""
    arr = np.asarray(im, dtype=np.float32)
    a = arr[:, :, 3:4] / 255.0
    pm = np.concatenate([arr[:, :, :3] * a, arr[:, :, 3:4]], axis=2)
    pm_im = Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), "RGBA")
    if (new_w, new_h) != im.size:
        pm_im = pm_im.resize((max(1, int(new_w)), max(1, int(new_h))), Image.LANCZOS)
    if abs(angle_deg) > 0.1:
        pm_im = pm_im.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    pa = np.asarray(pm_im, dtype=np.float32)
    na = pa[:, :, 3:4] / 255.0
    st = np.where(na > 1e-3, pa[:, :, :3] / np.maximum(na, 1e-3), 0.0)
    out = np.concatenate([np.clip(st, 0, 255), pa[:, :, 3:4]], axis=2).astype(np.uint8)
    out[out[:, :, 3] < 4] = [0, 0, 0, 0]
    return Image.fromarray(out, "RGBA")


def recolor_anodized(
    im: Image.Image,
    hue_shift_deg: float = 0.0,
    warm_shift_deg: float | None = None,
    sat_mult: float = 1.0,
    val_mult: float = 1.0,
    contrast_mult: float = 1.0,
    sat_gate: float = 0.15,
) -> Image.Image:
    """Smooth float32 dual-band metallic anodizing:
    - Preserves low-saturation brushed titanium/gunmetal skeleton & white speculars (`s < sat_gate`).
    - Allows shifting primary cool/mid armor (`hue_shift_deg`) independently from warm trim/glow (`warm_shift_deg`).
    """
    arr = np.asarray(im, dtype=np.float32)
    rgb = arr[:, :, :3] / 255.0
    alpha = arr[:, :, 3:4]

    mx = np.max(rgb, axis=2)
    mn = np.min(rgb, axis=2)
    diff = mx - mn
    s = np.where(mx > 1e-5, diff / np.maximum(mx, 1e-5), 0.0)
    v = mx

    # Vectorized RGB -> H in [0, 360)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    h = np.zeros_like(mx)
    nz = diff > 1e-5
    mr = nz & (mx == r)
    mg = nz & (mx == g) & (~mr)
    mb = nz & (~mr) & (~mg)
    h[mr] = (60.0 * ((g[mr] - b[mr]) / diff[mr]) + 360.0) % 360.0
    h[mg] = 60.0 * ((b[mg] - r[mg]) / diff[mg]) + 120.0
    h[mb] = 60.0 * ((r[mb] - g[mb]) / diff[mb]) + 240.0

    # Smooth feather weight for colored alloy vs neutral gunmetal/chrome
    w_col = np.clip((s - sat_gate) / 0.12, 0.0, 1.0)
    if warm_shift_deg is None:
        dh = np.full_like(h, hue_shift_deg)
    else:
        # Warm gold/amber band roughly [12, 68] deg
        is_warm = np.clip(1.0 - np.abs(((h - 40.0 + 180.0) % 360.0) - 180.0) / 34.0, 0.0, 1.0)
        dh = hue_shift_deg * (1.0 - is_warm) + warm_shift_deg * is_warm

    h_new = (h + dh * w_col) % 360.0
    s_new = np.clip(s * (1.0 + (sat_mult - 1.0) * w_col), 0.0, 1.0)
    v_new = np.clip(v * val_mult, 0.0, 1.0)

    # HSV -> RGB
    c = v_new * s_new
    x = c * (1.0 - np.abs(((h_new / 60.0) % 2.0) - 1.0))
    m = v_new - c
    hi = (h_new // 60.0).astype(np.int32) % 6
    ro = np.select([hi == 0, hi == 1, hi == 2, hi == 3, hi == 4, hi == 5], [c, x, 0.0, 0.0, x, c]) + m
    go = np.select([hi == 0, hi == 1, hi == 2, hi == 3, hi == 4, hi == 5], [x, c, c, x, 0.0, 0.0]) + m
    bo = np.select([hi == 0, hi == 1, hi == 2, hi == 3, hi == 4, hi == 5], [0.0, 0.0, x, c, c, x]) + m

    rgb_out = np.stack([ro, go, bo], axis=2) * 255.0
    if abs(contrast_mult - 1.0) > 1e-3:
        rgb_img = Image.fromarray(np.clip(rgb_out, 0, 255).astype(np.uint8), "RGB")
        rgb_img = ImageEnhance.Contrast(rgb_img).enhance(contrast_mult)
        rgb_out = np.asarray(rgb_img, dtype=np.float32)

    out = np.concatenate([np.clip(rgb_out, 0, 255), alpha], axis=2).astype(np.uint8)
    out[out[:, :, 3] == 0] = [0, 0, 0, 0]
    return Image.fromarray(out, "RGBA")


def extract_subpart(master: Image.Image, box: tuple[int, int, int, int], feather: int = 8) -> Image.Image:
    """Crop a mechanical sub-assembly with feathered inner seam edges."""
    x0, y0, x1, y1 = box
    crop = master.crop((x0, y0, x1, y1)).convert("RGBA")
    if feather > 0:
        w, h = crop.size
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rectangle((feather, feather, max(feather + 1, w - feather), max(feather + 1, h - feather)), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(feather * 0.7))
        crop.putalpha(ImageChops.multiply(crop.getchannel("A"), m))
    return crop


def paste_with_ao(
    canvas: Image.Image,
    part: Image.Image,
    cx: float,
    cy: float,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    angle_deg: float = 0.0,
    flip_x: bool = False,
    flip_y: bool = False,
    ao_radius: float = 12.0,
    ao_strength: float = 0.55,
    ao_dy: int = 6,
) -> None:
    """Composite a 2.5D sub-part onto `canvas` with realistic contact ambient occlusion on lower armor."""
    p = part
    if flip_x:
        p = p.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_y:
        p = p.transpose(Image.FLIP_TOP_BOTTOM)
    nw = max(4, round(p.width * scale_x))
    nh = max(4, round(p.height * scale_y))
    p = _premul_resize_rotate(p, nw, nh, angle_deg=angle_deg)

    px = round(cx - p.width * 0.5)
    py = round(cy - p.height * 0.5)

    if ao_strength > 0.01:
        layer_a = Image.new("L", canvas.size, 0)
        layer_a.paste(p.getchannel("A"), (px, py + ao_dy))
        ao_blur = layer_a.filter(ImageFilter.GaussianBlur(ao_radius))
        # Darken ONLY existing opaque pixels of `canvas` underneath `part`
        ca = np.asarray(canvas, dtype=np.float32)
        ao_f = (np.asarray(ao_blur, dtype=np.float32) / 255.0) * ao_strength
        ca[:, :, :3] *= (1.0 - ao_f[:, :, None] * 0.72)
        canvas.paste(Image.fromarray(np.clip(ca, 0, 255).astype(np.uint8), "RGBA"))

    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.paste(p, (px, py))
    canvas.alpha_composite(tmp)


def fit_on_canvas(im: Image.Image, canvas_size: int = 1024, target_fill: float = 0.88, widen: float = 1.0) -> Image.Image:
    """Center & scale a kitbashed assembly cleanly inside `canvas_size x canvas_size` with 0-alpha corners."""
    arr = np.asarray(im)
    ys, xs = np.where(arr[:, :, 3] > 12)
    if not len(xs):
        return Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    x0, x1 = max(0, int(xs.min()) - 4), min(im.width, int(xs.max()) + 5)
    y0, y1 = max(0, int(ys.min()) - 4), min(im.height, int(ys.max()) + 5)
    cut = im.crop((x0, y0, x1, y1))
    cw = cut.width * widen
    ch = float(cut.height)
    sc = (canvas_size * target_fill) / max(cw, ch, 1.0)
    resized = _premul_resize_rotate(cut, round(cw * sc), round(ch * sc))
    out = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    out.alpha_composite(resized, ((canvas_size - resized.width) // 2, (canvas_size - resized.height) // 2))
    return out


def polish_rim_no_dark_border(im: Image.Image, min_boundary_v: float = 0.20) -> Image.Image:
    """Apply subtle ambient steel rim on outer alpha silhouette boundary so no sprite has dark cartoon outline_px > 1."""
    arr = np.asarray(im, dtype=np.float32)
    a = arr[:, :, 3]
    mask = a > 127.0
    if not np.any(mask):
        return im
    eroded = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255, "L").filter(ImageFilter.MinFilter(3))) > 0
    ring1 = mask & (~eroded)
    eroded2 = np.asarray(Image.fromarray(eroded.astype(np.uint8) * 255, "L").filter(ImageFilter.MinFilter(3))) > 0
    ring2 = eroded & (~eroded2)
    for ring, target_v in ((ring1, min_boundary_v), (ring2, min_boundary_v * 0.92)):
        if not np.any(ring):
            continue
        rgb_r = arr[:, :, :3][ring]
        mx = np.max(rgb_r, axis=1, keepdims=True)
        too_dark = (mx[:, 0] < target_v * 255.0)
        if np.any(too_dark):
            # Lift dark edge pixels smoothly toward cool brushed-steel rim (52, 58, 68)
            boost = np.maximum(rgb_r[too_dark], np.array([[50.0, 55.0, 64.0]], dtype=np.float32) * (target_v / 0.20))
            rgb_r[too_dark] = boost
            arr[:, :, :3][ring] = rgb_r
    out = np.clip(arr, 0, 255).astype(np.uint8)
    out[out[:, :, 3] == 0] = [0, 0, 0, 0]
    return Image.fromarray(out, "RGBA")


# ==============================================================================
# 1. W1 PLAYER SHIPS (25/25 Commercial Painted + Kitbashed Fleet)
# ==============================================================================
def render_w1_ship(idx: int) -> Image.Image:
    m01 = load_master("w1-player-b/masters/hero_painted_01_1024.png")
    m04 = load_master("w1-player-b/masters/hero_painted_04_1024.png")
    m08 = load_master("w1-player-b/masters/hero_painted_08_1024.png")
    m12 = load_master("w1-player-b/masters/hero_painted_12_1024.png")
    m13 = load_master("w1-player-b/masters/hero_painted_13_1024.png")
    m15 = load_master("w1-player-b/masters/hero_painted_15_1024.png")
    m16 = load_master("w1-player-b/masters/hero_painted_16_1024.png")
    m25 = load_master("w1-player-b/masters/hero_painted_25_1024.png")
    d01 = load_master("w1-player-b/masters/drone_painted_01_1024.png")
    d05 = load_master("w1-player-b/masters/drone_painted_05_1024.png")

    # 8 Pure Archetype Heroes
    if idx == 1:
        return polish_rim_no_dark_border(m01)
    if idx == 4:
        return polish_rim_no_dark_border(m04)
    if idx == 8:
        return polish_rim_no_dark_border(m08)
    if idx == 12:
        return polish_rim_no_dark_border(m12)
    if idx == 13:
        return polish_rim_no_dark_border(m13)
    if idx == 15:
        return polish_rim_no_dark_border(m15)
    if idx == 16:
        return polish_rim_no_dark_border(m16)
    if idx == 25:
        return polish_rim_no_dark_border(m25)

    # Reusable painted mechanical sub-assemblies
    nacelle_l = extract_subpart(m15, (60, 110, 295, 860), feather=8)
    wing13_l = extract_subpart(m13, (60, 290, 410, 740), feather=10)
    scythe16_l = extract_subpart(m16, (60, 130, 385, 885), feather=10)
    prong04_l = extract_subpart(m04, (205, 60, 445, 560), feather=10)
    sniper_brl = extract_subpart(d01, (430, 70, 594, 455), feather=8)
    wing25_l = extract_subpart(m25, (60, 330, 445, 710), feather=10)
    binder12_l = extract_subpart(m12, (65, 380, 440, 790), feather=10)

    c = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))

    if idx == 2:
        # Solar-Ruby Swept Canard Interceptor
        w = recolor_anodized(wing13_l, hue_shift_deg=15, warm_shift_deg=10, sat_mult=1.12)
        paste_with_ao(c, w, 255, 565, 0.92, 1.05, angle_deg=12)
        paste_with_ao(c, w, 769, 565, 0.92, 1.05, angle_deg=-12, flip_x=True)
        body = recolor_anodized(m01, hue_shift_deg=135, warm_shift_deg=0, sat_mult=1.10)
        paste_with_ao(c, body, 512, 512, 0.84, 0.98)
    elif idx == 3:
        # Emerald-Jade Heavy Twin-Boom Carrier
        nac = recolor_anodized(nacelle_l, hue_shift_deg=-95, warm_shift_deg=110, sat_mult=1.08)
        paste_with_ao(c, nac, 225, 535, 0.95, 0.92)
        paste_with_ao(c, nac, 799, 535, 0.95, 0.92, flip_x=True)
        body = recolor_anodized(m13, hue_shift_deg=138, warm_shift_deg=95, sat_mult=1.12)
        paste_with_ao(c, body, 512, 520, 0.88, 1.08)
    elif idx == 5:
        # Royal-Violet Delta Spearhead Striker
        w = recolor_anodized(wing25_l, hue_shift_deg=68, sat_mult=1.35, sat_gate=0.05)
        paste_with_ao(c, w, 255, 605, 0.96, 1.15, angle_deg=-14)
        paste_with_ao(c, w, 769, 605, 0.96, 1.15, angle_deg=14, flip_x=True)
        body = recolor_anodized(m01, hue_shift_deg=68, warm_shift_deg=-75, sat_mult=1.15)
        paste_with_ao(c, body, 512, 495, 0.78, 1.02)
    elif idx == 6:
        # Crimson-Pearl Astrolabe Ring + Outboard Nacelle Gunship (#06)
        ring = recolor_anodized(m08, hue_shift_deg=195, warm_shift_deg=-35, sat_mult=1.08)
        paste_with_ao(c, ring, 512, 512, 1.02, 0.96, angle_deg=180)
        nac = recolor_anodized(nacelle_l, hue_shift_deg=95, warm_shift_deg=-25)
        paste_with_ao(c, nac, 210, 520, 0.78, 0.76)
        paste_with_ao(c, nac, 814, 520, 0.78, 0.76, flip_x=True)
        core = recolor_anodized(m01, hue_shift_deg=145, warm_shift_deg=0, sat_mult=1.06)
        paste_with_ao(c, core, 512, 505, 0.72, 0.88)
    elif idx == 7:
        # Wide-Wing Pearl & Emerald Twin-Prong Gunship (#07)
        w = recolor_anodized(scythe16_l, hue_shift_deg=-38, warm_shift_deg=65)
        paste_with_ao(c, w, 225, 535, 0.88, 0.85, angle_deg=-8)
        paste_with_ao(c, w, 799, 535, 0.88, 0.85, angle_deg=8, flip_x=True)
        body = recolor_anodized(m04, hue_shift_deg=72, warm_shift_deg=76, sat_mult=1.08)
        paste_with_ao(c, body, 512, 512, 0.90, 0.96)
    elif idx == 9:
        # Solar-Lime Forward-Tip Lance Fighter (#09)
        sc = recolor_anodized(scythe16_l, hue_shift_deg=-22, warm_shift_deg=15)
        paste_with_ao(c, sc, 260, 585, 0.76, 0.82, angle_deg=18)
        paste_with_ao(c, sc, 764, 585, 0.76, 0.82, angle_deg=-18, flip_x=True)
        body = recolor_anodized(m01, hue_shift_deg=-55, warm_shift_deg=85, sat_mult=1.10)
        paste_with_ao(c, body, 512, 488, 0.74, 1.04)
    elif idx == 10:
        # Dual-Concentric Emerald/Violet Turbine Ring (#10)
        r_outer = recolor_anodized(m08, hue_shift_deg=-35, warm_shift_deg=88, sat_mult=1.15)
        paste_with_ao(c, r_outer, 512, 512, 1.02, 1.02, angle_deg=90)
        r_inner = recolor_anodized(m08, hue_shift_deg=110, warm_shift_deg=95, sat_mult=1.10)
        paste_with_ao(c, r_inner, 512, 512, 0.78, 0.78, angle_deg=-45)
        pod = recolor_anodized(d05, hue_shift_deg=95, warm_shift_deg=80)
        paste_with_ao(c, pod, 512, 495, 0.68, 0.72)
    elif idx == 11:
        # Magenta-Emerald Splayed-Claw Ring Heavy Gunship (#11)
        ring = recolor_anodized(m08, hue_shift_deg=165, warm_shift_deg=95, sat_mult=1.12)
        paste_with_ao(c, ring, 512, 495, 0.94, 0.90)
        pr = recolor_anodized(prong04_l, hue_shift_deg=295, warm_shift_deg=85, sat_mult=1.15)
        paste_with_ao(c, pr, 235, 625, 1.05, 1.02, angle_deg=148)
        paste_with_ao(c, pr, 789, 625, 1.05, 1.02, angle_deg=-148, flip_x=True)
        core = recolor_anodized(m04, hue_shift_deg=298, warm_shift_deg=90, sat_mult=1.12)
        paste_with_ao(c, core, 512, 490, 0.78, 0.82)
    elif idx == 14:
        # Cobalt-Gold Twin-Boom Heavy Assault Fighter (#14)
        paste_with_ao(c, sniper_brl, 355, 255, 0.92, 0.95)
        paste_with_ao(c, sniper_brl, 669, 255, 0.92, 0.95, flip_x=True)
        w = recolor_anodized(binder12_l, hue_shift_deg=-15, warm_shift_deg=5)
        paste_with_ao(c, w, 248, 520, 0.95, 0.95, angle_deg=-22)
        paste_with_ao(c, w, 776, 520, 0.95, 0.95, angle_deg=22, flip_x=True)
        body = recolor_anodized(m04, hue_shift_deg=185, warm_shift_deg=-10, sat_mult=1.08)
        paste_with_ao(c, body, 512, 535, 0.84, 0.90)
    elif idx == 17:
        # Emerald-Crimson Heavy Mandible Dreadnought Fighter (#17)
        nac = recolor_anodized(nacelle_l, hue_shift_deg=-115, warm_shift_deg=95, sat_mult=1.15)
        paste_with_ao(c, nac, 215, 515, 0.88, 0.92)
        paste_with_ao(c, nac, 809, 515, 0.88, 0.92, flip_x=True)
        body = recolor_anodized(m04, hue_shift_deg=96, warm_shift_deg=305, sat_mult=1.18)
        paste_with_ao(c, body, 512, 505, 0.92, 0.98)
    elif idx == 18:
        # Sapphire-Emerald Long-Nose Railgun Interceptor (#18)
        paste_with_ao(c, sniper_brl, 395, 225, 0.82, 0.90)
        paste_with_ao(c, sniper_brl, 629, 245, 0.72, 0.80, flip_x=True)
        w = recolor_anodized(binder12_l, hue_shift_deg=-35, warm_shift_deg=95)
        paste_with_ao(c, w, 268, 600, 0.88, 0.92)
        paste_with_ao(c, w, 756, 600, 0.88, 0.92, flip_x=True)
        body = recolor_anodized(m01, hue_shift_deg=-12, warm_shift_deg=95, sat_mult=1.12)
        paste_with_ao(c, body, 512, 495, 0.84, 1.02)
    elif idx == 19:
        # Pearl-Solar Swept Crescent Strike Fighter (#19)
        sc = recolor_anodized(scythe16_l, hue_shift_deg=195, warm_shift_deg=-15, sat_mult=0.85)
        paste_with_ao(c, sc, 238, 560, 0.86, 0.84, angle_deg=155)
        paste_with_ao(c, sc, 786, 560, 0.86, 0.84, angle_deg=-155, flip_x=True)
        body = recolor_anodized(m01, hue_shift_deg=25, warm_shift_deg=-8, sat_mult=1.10)
        paste_with_ao(c, body, 512, 495, 0.82, 0.98)
    elif idx == 20:
        # Cyan-Teal Forward V-Wing Interceptor (#20)
        w = recolor_anodized(wing13_l, hue_shift_deg=175, warm_shift_deg=145, sat_mult=1.18)
        paste_with_ao(c, w, 245, 565, 0.98, 1.05, angle_deg=-26)
        paste_with_ao(c, w, 779, 565, 0.98, 1.05, angle_deg=26, flip_x=True)
        body = recolor_anodized(m01, hue_shift_deg=-32, warm_shift_deg=155, sat_mult=1.10)
        paste_with_ao(c, body, 512, 490, 0.76, 1.02)
    elif idx == 21:
        # Sapphire-Violet Twin-Arc Heavy Nacelle Cruiser (#21)
        sc = recolor_anodized(scythe16_l, hue_shift_deg=82, warm_shift_deg=165, sat_mult=1.15)
        paste_with_ao(c, sc, 220, 495, 0.84, 0.94)
        paste_with_ao(c, sc, 804, 495, 0.84, 0.94, flip_x=True)
        body = recolor_anodized(m15, hue_shift_deg=-42, warm_shift_deg=195, sat_mult=1.12)
        paste_with_ao(c, body, 512, 512, 0.86, 0.98)
    elif idx == 22:
        # Violet-Crimson Bat-Wing Stealth Phantom (#22)
        b = recolor_anodized(binder12_l, hue_shift_deg=65, warm_shift_deg=315, sat_mult=1.22)
        paste_with_ao(c, b, 235, 645, 0.92, 0.88, angle_deg=18)
        paste_with_ao(c, b, 789, 645, 0.92, 0.88, angle_deg=-18, flip_x=True)
        body = recolor_anodized(m16, hue_shift_deg=108, warm_shift_deg=285, sat_mult=1.20)
        paste_with_ao(c, body, 512, 485, 0.94, 0.92)
    elif idx == 23:
        # Blazing Solar-Flame Overdrive Mecha-Valkyrie (#23)
        sc = recolor_anodized(scythe16_l, hue_shift_deg=-135, warm_shift_deg=-15, sat_mult=1.25)
        paste_with_ao(c, sc, 215, 520, 0.82, 0.78, angle_deg=-24)
        paste_with_ao(c, sc, 809, 520, 0.82, 0.78, angle_deg=24, flip_x=True)
        body = recolor_anodized(m12, hue_shift_deg=168, warm_shift_deg=-12, sat_mult=1.22)
        paste_with_ao(c, body, 512, 510, 0.96, 1.02)
    else:  # idx == 24
        # Bio-Emerald & Ruby Quad-Blade Tri-Hull (#24)
        b = recolor_anodized(binder12_l, hue_shift_deg=-85, warm_shift_deg=320, sat_mult=1.22)
        paste_with_ao(c, b, 235, 635, 0.94, 0.90)
        paste_with_ao(c, b, 789, 635, 0.94, 0.90, flip_x=True)
        body = recolor_anodized(m15, hue_shift_deg=-135, warm_shift_deg=96, sat_mult=1.20)
        paste_with_ao(c, body, 512, 495, 0.92, 0.94)

    return polish_rim_no_dark_border(fit_on_canvas(c, 1024, target_fill=0.88))


# ==============================================================================
# 2. W1 ESCORT DRONES (13/13 Commercial Painted + Kitbashed Pods)
# ==============================================================================
def render_w1_drone(idx: int) -> Image.Image:
    d01 = load_master("w1-player-b/masters/drone_painted_01_1024.png")
    d04 = load_master("w1-player-b/masters/drone_painted_04_1024.png")
    d05 = load_master("w1-player-b/masters/drone_painted_05_1024.png")

    if idx == 1:
        return polish_rim_no_dark_border(fit_on_canvas(d01, 1024, 0.86, widen=1.18))
    if idx == 4:
        return polish_rim_no_dark_border(d04)
    if idx == 5:
        return polish_rim_no_dark_border(d05)

    shield_l = extract_subpart(d04, (70, 145, 345, 875), feather=8)
    wing5_l = extract_subpart(d05, (70, 210, 365, 885), feather=8)
    brl1 = extract_subpart(d01, (430, 70, 594, 460), feather=8)
    pod1 = extract_subpart(d01, (280, 390, 744, 950), feather=8)

    c = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    if idx in (2, 6, 10):
        # Armored Scarab Winged Assault Pod (#02 Cyan-Violet, #06 Pearl-Sapphire, #10 Violet-Emerald)
        hs = {2: (145, 195), 6: (175, 165), 10: (215, 95)}[idx]
        w = recolor_anodized(wing5_l, hue_shift_deg=hs[0], warm_shift_deg=hs[1], sat_mult=1.12)
        paste_with_ao(c, w, 245, 535, 0.95, 0.92, angle_deg=12)
        paste_with_ao(c, w, 779, 535, 0.95, 0.92, angle_deg=-12, flip_x=True)
        core = recolor_anodized(pod1, hue_shift_deg=hs[0], warm_shift_deg=hs[1], sat_mult=1.05)
        paste_with_ao(c, core, 512, 520, 1.08, 1.05)
    elif idx in (3, 7, 11):
        # Hinged-Collar Heavy Beam Turret Pod (#03 Crimson, #07 Solar-Amber, #11 Cobalt-Orange)
        hs = {3: (-32, -28), 7: (-10, 5), 11: (185, 8)}[idx]
        paste_with_ao(c, brl1, 415, 255, 0.85, 0.82)
        paste_with_ao(c, brl1, 609, 255, 0.85, 0.82, flip_x=True)
        body = recolor_anodized(d04, hue_shift_deg=hs[0], warm_shift_deg=hs[1], sat_mult=1.14)
        paste_with_ao(c, body, 512, 545, 0.94, 0.88)
    elif idx in (8, 12):
        # Swept Twin-Blade Interceptor Drone (#08 Violet-Gold, #12 Emerald-Lime)
        hs = {8: (245, 45), 12: (98, 72)}[idx]
        sh = recolor_anodized(shield_l, hue_shift_deg=hs[0], warm_shift_deg=hs[1], sat_mult=1.15)
        paste_with_ao(c, sh, 225, 520, 0.85, 0.82, angle_deg=-18)
        paste_with_ao(c, sh, 799, 520, 0.85, 0.82, angle_deg=18, flip_x=True)
        body = recolor_anodized(d05, hue_shift_deg=hs[0], warm_shift_deg=hs[1], sat_mult=1.15)
        paste_with_ao(c, body, 512, 512, 0.86, 0.92)
    elif idx == 9:
        # Emerald-Gold Heavy Twin-Claw Turret (#09)
        sh = recolor_anodized(shield_l, hue_shift_deg=72, warm_shift_deg=15, sat_mult=1.18)
        paste_with_ao(c, sh, 255, 560, 0.78, 0.76)
        paste_with_ao(c, sh, 769, 560, 0.78, 0.76, flip_x=True)
        body = recolor_anodized(d01, hue_shift_deg=35, warm_shift_deg=8, sat_mult=1.15)
        paste_with_ao(c, body, 512, 512, 1.05, 0.96)
    else:  # idx == 13 (Stealth Gunmetal Sniper Pod matching drones-01 #13!)
        w = recolor_anodized(wing5_l, hue_shift_deg=0, sat_mult=0.22, val_mult=0.82, sat_gate=0.02)
        paste_with_ao(c, w, 275, 565, 0.86, 0.86)
        paste_with_ao(c, w, 749, 565, 0.86, 0.86, flip_x=True)
        body = recolor_anodized(d01, hue_shift_deg=155, sat_mult=0.28, val_mult=0.86, sat_gate=0.02)
        paste_with_ao(c, body, 512, 505, 1.04, 0.98)

    return polish_rim_no_dark_border(fit_on_canvas(c, 1024, target_fill=0.86))


# ==============================================================================
# 3. W2 DEDICATED ENEMY INVADERS (22/22 Hulls — Zero Player/Boss Reuse!)
# ==============================================================================
def render_w2_enemy(idx: int, variant: str, pal: str) -> Image.Image:
    e_orb = load_master("w2-enemy-b/masters/enemy_painted_orb_1024.png")
    e_rai = load_master("w2-enemy-b/masters/enemy_painted_raider_1024.png")
    e_mec = load_master("w2-enemy-b/masters/enemy_painted_mech_1024.png")
    e_sau = load_master("w2-enemy-b/masters/enemy_painted_saucer_1024.png")

    # 4 Exact Dedicated Enemy Anchors
    if variant == "swarmling_pod":      # enemy-01 #1 Cobalt Scout Orb
        return polish_rim_no_dark_border(fit_on_canvas(e_orb, 512, 0.88))
    if variant == "beetle_cruiser":     # items-01 #2 Crimson Twin-Intake Raider
        return polish_rim_no_dark_border(fit_on_canvas(e_rai, 512, 0.88))
    if variant == "phantom_hex":        # items-01 #3 Emerald Shoulder-Cannon Mech
        return polish_rim_no_dark_border(fit_on_canvas(e_mec, 512, 0.88))
    if variant == "cyber_disc":         # Octagonal Cyber Saw-Disc
        return polish_rim_no_dark_border(fit_on_canvas(e_sau, 512, 0.88))

    pincer_l = extract_subpart(e_rai, (75, 130, 365, 920), feather=10)
    shld_pod_l = extract_subpart(e_mec, (80, 70, 355, 620), feather=10)
    claw_bot_l = extract_subpart(e_mec, (210, 610, 495, 955), feather=8)
    blaster_bot_l = extract_subpart(e_orb, (140, 620, 390, 945), feather=8)

    pal_hue = {"crimson": 0, "magenta": -38, "violet": -85, "amber": 38}.get(pal, 0)
    c = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))

    if variant == "scout_dart":
        # enemy-01 #16 Swept Delta-Chevron Crimson Dive-Dart (distinct from beetle_cruiser!)
        core = extract_subpart(e_rai, (295, 65, 729, 865), feather=12)
        p = recolor_anodized(pincer_l, hue_shift_deg=6, sat_mult=1.22)
        paste_with_ao(c, p, 245, 545, 0.96, 0.78, angle_deg=38, flip_y=True)
        paste_with_ao(c, p, 779, 545, 0.96, 0.78, angle_deg=-38, flip_x=True, flip_y=True)
        paste_with_ao(c, recolor_anodized(core, hue_shift_deg=8, sat_mult=1.16), 512, 455, 0.74, 0.88)
    elif variant == "viper_lance":
        paste_with_ao(c, claw_bot_l, 355, 765, 0.95, 1.08)
        paste_with_ao(c, claw_bot_l, 669, 765, 0.95, 1.08, flip_x=True)
        body = recolor_anodized(e_rai, hue_shift_deg=12, warm_shift_deg=0, sat_mult=1.10)
        paste_with_ao(c, body, 512, 465, 0.76, 0.94)
    elif variant == "wasp_raider":
        p = recolor_anodized(pincer_l, hue_shift_deg=-42, sat_mult=1.20)
        paste_with_ao(c, p, 215, 445, 0.95, 0.78, angle_deg=28)
        paste_with_ao(c, p, 809, 445, 0.95, 0.78, angle_deg=-28, flip_x=True)
        body = recolor_anodized(e_mec, hue_shift_deg=195, warm_shift_deg=-15, sat_mult=1.15)
        paste_with_ao(c, body, 512, 520, 0.82, 0.96)
    elif variant == "manta_glider":
        p = recolor_anodized(pincer_l, hue_shift_deg=-88, sat_mult=1.18)
        paste_with_ao(c, p, 205, 495, 1.08, 0.72, angle_deg=42)
        paste_with_ao(c, p, 819, 495, 1.08, 0.72, angle_deg=-42, flip_x=True)
        body = recolor_anodized(e_orb, hue_shift_deg=65, sat_mult=1.12)
        paste_with_ao(c, body, 512, 520, 0.78, 0.82)
    elif variant == "stalker_blade":
        body = recolor_anodized(e_rai, hue_shift_deg=-45, sat_mult=1.18)
        paste_with_ao(c, body, 512, 512, 0.68, 1.05)
    elif variant == "dread_carrier":
        sp = recolor_anodized(shld_pod_l, hue_shift_deg=165, sat_mult=1.15)
        paste_with_ao(c, sp, 195, 515, 1.05, 1.05)
        paste_with_ao(c, sp, 829, 515, 1.05, 1.05, flip_x=True)
        body = recolor_anodized(e_mec, hue_shift_deg=165, sat_mult=1.15)
        paste_with_ao(c, body, 512, 512, 0.88, 0.92)
    elif variant == "spire_frigate":
        paste_with_ao(c, blaster_bot_l, 355, 765, 0.92, 1.05)
        paste_with_ao(c, blaster_bot_l, 669, 765, 0.92, 1.05, flip_x=True)
        body = recolor_anodized(e_rai, hue_shift_deg=8, sat_mult=1.12)
        paste_with_ao(c, body, 512, 465, 0.74, 0.98)
    elif variant == "centurion_mk1":
        p = recolor_anodized(pincer_l, hue_shift_deg=0, sat_mult=1.12)
        paste_with_ao(c, p, 215, 535, 0.88, 0.88)
        paste_with_ao(c, p, 809, 535, 0.88, 0.88, flip_x=True)
        body = recolor_anodized(e_orb, hue_shift_deg=142, sat_mult=1.18)
        paste_with_ao(c, body, 512, 505, 0.86, 0.88)
    elif variant == "centurion_turret":
        paste_with_ao(c, blaster_bot_l, 385, 785, 0.92, 0.92)
        paste_with_ao(c, blaster_bot_l, 639, 785, 0.92, 0.92, flip_x=True)
        body = recolor_anodized(e_sau, hue_shift_deg=42, sat_mult=1.12)
        paste_with_ao(c, body, 512, 475, 0.84, 0.84, angle_deg=22.5)
    elif variant == "wingpod_wide":
        sp = recolor_anodized(shld_pod_l, hue_shift_deg=235, sat_mult=1.18)
        paste_with_ao(c, sp, 195, 520, 1.12, 0.86, angle_deg=90)
        paste_with_ao(c, sp, 829, 520, 1.12, 0.86, angle_deg=-90, flip_x=True)
        body = recolor_anodized(e_orb, hue_shift_deg=145, sat_mult=1.15)
        paste_with_ao(c, body, 512, 520, 0.84, 0.76)
    elif variant == "wingpod_core":
        body = recolor_anodized(e_orb, hue_shift_deg=98, sat_mult=1.18)
        paste_with_ao(c, body, 512, 512, 0.78, 0.98)
    elif variant == "void_sentinel":
        p = recolor_anodized(pincer_l, hue_shift_deg=-48, sat_mult=1.18)
        for ang, dx, dy in [(0, 235, 512), (180, 789, 512), (90, 512, 235), (-90, 512, 789)]:
            paste_with_ao(c, p, dx, dy, 0.62, 0.56, angle_deg=ang)
        body = recolor_anodized(e_sau, hue_shift_deg=-25, sat_mult=1.15)
        paste_with_ao(c, body, 512, 512, 0.72, 0.72)
    elif variant == "automaton_droid":
        body = recolor_anodized(e_mec, hue_shift_deg=-65, warm_shift_deg=0, sat_mult=1.16)
        paste_with_ao(c, body, 512, 512, 0.98, 0.92)
    elif variant == "chrono_mine":
        body = recolor_anodized(e_sau, hue_shift_deg=52, sat_mult=1.18)
        paste_with_ao(c, body, 512, 512, 0.94, 0.94, angle_deg=45)
    elif variant == "reaper_scythe":
        p = recolor_anodized(pincer_l, hue_shift_deg=5, sat_mult=1.18)
        paste_with_ao(c, p, 195, 545, 1.05, 1.02, angle_deg=16)
        paste_with_ao(c, p, 829, 545, 1.05, 1.02, angle_deg=-16, flip_x=True)
        body = recolor_anodized(e_mec, hue_shift_deg=242, sat_mult=1.18)
        paste_with_ao(c, body, 512, 475, 0.82, 0.86)
    elif variant == "juggernaut_hull":
        sp = recolor_anodized(shld_pod_l, hue_shift_deg=242, sat_mult=1.18)
        paste_with_ao(c, sp, 195, 485, 1.08, 1.08)
        paste_with_ao(c, sp, 829, 485, 1.08, 1.08, flip_x=True)
        body = recolor_anodized(e_rai, hue_shift_deg=0, sat_mult=1.12)
        paste_with_ao(c, body, 512, 520, 0.92, 0.94)
    elif variant == "juggernaut_core":
        r2 = recolor_anodized(e_sau, hue_shift_deg=38, sat_mult=1.15)
        paste_with_ao(c, r2, 512, 512, 0.96, 0.96, angle_deg=18)
        core = recolor_anodized(e_orb, hue_shift_deg=165, sat_mult=1.15)
        paste_with_ao(c, core, 512, 512, 0.66, 0.66)
    else:  # target_drone (AP-0068)
        paste_with_ao(c, shld_pod_l, 225, 512, 0.85, 0.78, angle_deg=90)
        paste_with_ao(c, shld_pod_l, 799, 512, 0.85, 0.78, angle_deg=-90, flip_x=True)
        body = recolor_anodized(e_sau, hue_shift_deg=28, sat_mult=1.18)
        paste_with_ao(c, body, 512, 512, 0.76, 0.76)

    return polish_rim_no_dark_border(fit_on_canvas(c, 512, target_fill=0.88))


# ==============================================================================
# 4. W3 BOSS DREADNOUGHTS (35/35 Bodies + 7/7 Modular Sub-Parts)
# ==============================================================================
def render_w3_boss(arch_key: str, pcfg: int, pal: str) -> Image.Image:
    b7001 = load_master("w3-boss-b/masters/boss_painted_7001_1024.png")
    b7002 = load_master("w3-boss-b/masters/boss_painted_7002_1024.png")
    b7003 = load_master("w3-boss-b/masters/boss_painted_7003_1024.png")
    b7004 = load_master("w3-boss-b/masters/boss_painted_7004_1024.png")
    b7005 = load_master("w3-boss-b/masters/boss_painted_7005_1024.png")
    b_krk = load_master("w3-boss-b/masters/boss_painted_kraken_1024.png")
    b_col = load_master("w3-boss-b/masters/boss_painted_colossus_1024.png")
    e_sau = load_master("w2-enemy-b/masters/enemy_painted_saucer_1024.png")

    gatling_arm_l = extract_subpart(b7002, (50, 265, 385, 760), feather=12)
    pincer_arm_l = extract_subpart(b_krk, (50, 290, 395, 760), feather=12)
    wing_col_l = extract_subpart(b_col, (50, 275, 420, 680), feather=12)

    pal_shift = {"crimson": 0, "violet": -75, "emerald": 115, "magenta": -32, "amber": 32}.get(pal, 0)
    mk_shift = pcfg * 24

    c = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))

    # Mk1 keeps pure decoded anchor silhouette on 7001..7005; Mk2..Mk4 add progressive siege modules!
    if arch_key == "citadel":
        base = b7001 if pcfg == 0 else recolor_anodized(b7001, hue_shift_deg=pal_shift + mk_shift, sat_mult=1.06)
        if pcfg >= 1:
            g = recolor_anodized(gatling_arm_l, hue_shift_deg=pal_shift, sat_mult=1.08)
            paste_with_ao(c, g, 195, 555, 0.86, 0.92)
            paste_with_ao(c, g, 829, 555, 0.86, 0.92, flip_x=True)
        paste_with_ao(c, base, 512, 512, 1.0 if pcfg == 0 else 0.88, 1.0 if pcfg == 0 else 0.94)
    elif arch_key == "arachnid":
        base = b7002 if pcfg == 0 else recolor_anodized(b7002, hue_shift_deg=pal_shift + mk_shift, sat_mult=1.08)
        if pcfg >= 1:
            p = recolor_anodized(pincer_arm_l, hue_shift_deg=pal_shift + 40, sat_mult=1.10)
            paste_with_ao(c, p, 210, 370, 0.84, 0.84, angle_deg=-25)
            paste_with_ao(c, p, 814, 370, 0.84, 0.84, angle_deg=25, flip_x=True)
        paste_with_ao(c, base, 512, 525 if pcfg >= 1 else 512, 1.0, 1.08 if pcfg >= 1 else 1.0)
    elif arch_key == "leviathan":
        base = b7003 if pcfg == 0 else recolor_anodized(b7003, hue_shift_deg=pal_shift + mk_shift, sat_mult=1.08)
        if pcfg >= 1:
            w = recolor_anodized(wing_col_l, hue_shift_deg=pal_shift + 90)
            paste_with_ao(c, w, 215, 385, 0.88, 0.88)
            paste_with_ao(c, w, 809, 385, 0.88, 0.88, flip_x=True)
        paste_with_ao(c, base, 512, 535 if pcfg >= 1 else 512, 1.0, 1.12 if pcfg >= 1 else 1.0)
    elif arch_key == "chronos":
        base = b7004 if pcfg == 0 else recolor_anodized(b7004, hue_shift_deg=pal_shift + mk_shift, sat_mult=1.08)
        if pcfg >= 1:
            saw = recolor_anodized(e_sau, hue_shift_deg=pal_shift)
            paste_with_ao(c, saw, 225, 365, 0.36, 0.36)
            paste_with_ao(c, saw, 799, 365, 0.36, 0.36)
        paste_with_ao(c, base, 512, 535 if pcfg >= 1 else 512, 1.0, 1.12 if pcfg >= 1 else 1.0)
    elif arch_key == "seraph":
        base = b7005 if pcfg == 0 else recolor_anodized(b7005, hue_shift_deg=pal_shift + mk_shift, sat_mult=1.08)
        if pcfg >= 1:
            p = recolor_anodized(pincer_arm_l, hue_shift_deg=pal_shift)
            paste_with_ao(c, p, 195, 560, 0.78, 0.84)
            paste_with_ao(c, p, 829, 560, 0.78, 0.84, flip_x=True)
        paste_with_ao(c, base, 512, 505, 1.0 if pcfg == 0 else 0.90, 1.0 if pcfg == 0 else 0.92)
    elif arch_key == "kraken":
        base = b_krk if pcfg == 0 else recolor_anodized(b_krk, hue_shift_deg=pal_shift + mk_shift, sat_mult=1.10)
        if pcfg >= 1:
            g = recolor_anodized(gatling_arm_l, hue_shift_deg=pal_shift)
            paste_with_ao(c, g, 245, 355, 0.78, 0.78, angle_deg=180)
            paste_with_ao(c, g, 779, 355, 0.78, 0.78, angle_deg=180, flip_x=True)
        paste_with_ao(c, base, 512, 520, 1.0, 1.14)
    elif arch_key == "scorpion":
        # Coiled Cyber-Scorpion Dreadnought: arched dorsal stinger pincers + heavy gatling jaws!
        stinger = recolor_anodized(pincer_arm_l, hue_shift_deg=pal_shift + 145, sat_mult=1.18)
        paste_with_ao(c, stinger, 285, 295, 0.96, 0.92, angle_deg=142)
        paste_with_ao(c, stinger, 739, 295, 0.96, 0.92, angle_deg=-142, flip_x=True)
        jaw = recolor_anodized(gatling_arm_l, hue_shift_deg=pal_shift + mk_shift, sat_mult=1.12)
        paste_with_ao(c, jaw, 235, 615, 0.86, 0.86)
        paste_with_ao(c, jaw, 789, 615, 0.86, 0.86, flip_x=True)
        core = recolor_anodized(b7001, hue_shift_deg=pal_shift + 42 + mk_shift, sat_mult=1.10)
        paste_with_ao(c, core, 512, 525, 0.76, 0.78)
    elif arch_key == "colossus":
        base = b_col if pcfg == 0 else recolor_anodized(b_col, hue_shift_deg=pal_shift + mk_shift, sat_mult=1.10)
        if pcfg >= 1:
            g = recolor_anodized(gatling_arm_l, hue_shift_deg=pal_shift)
            paste_with_ao(c, g, 235, 635, 0.80, 0.80)
            paste_with_ao(c, g, 789, 635, 0.80, 0.80, flip_x=True)
        paste_with_ao(c, base, 512, 495, 1.0, 1.16)
    elif arch_key == "emblem_s":
        # AP-0117 Sovereign-S Flagship Boss
        w = recolor_anodized(wing_col_l, hue_shift_deg=85, sat_mult=1.18)
        paste_with_ao(c, w, 215, 455, 1.05, 1.08)
        paste_with_ao(c, w, 809, 455, 1.05, 1.08, flip_x=True)
        core = recolor_anodized(b7001, hue_shift_deg=12, sat_mult=1.12)
        paste_with_ao(c, core, 512, 525, 0.84, 0.88)
    elif arch_key == "overlord_x":
        # AP-0118 Overlord-X Quad-Pincer Dreadnought
        p = recolor_anodized(pincer_arm_l, hue_shift_deg=135, sat_mult=1.18)
        paste_with_ao(c, p, 215, 335, 0.88, 0.84, angle_deg=155)
        paste_with_ao(c, p, 809, 335, 0.88, 0.84, angle_deg=-155, flip_x=True)
        paste_with_ao(c, p, 215, 675, 0.92, 0.88, angle_deg=12)
        paste_with_ao(c, p, 809, 675, 0.92, 0.88, angle_deg=-12, flip_x=True)
        core = recolor_anodized(b7002, hue_shift_deg=-35, sat_mult=1.15)
        paste_with_ao(c, core, 512, 512, 0.84, 0.92)
    else:  # aegis_bastion (AP-0119)
        ring = recolor_anodized(b7005, hue_shift_deg=35, sat_mult=1.12)
        paste_with_ao(c, ring, 512, 512, 0.96, 0.96)
        prow = recolor_anodized(b7003, hue_shift_deg=-65, sat_mult=1.15)
        paste_with_ao(c, prow, 512, 565, 0.88, 0.92)

    if arch_key in ("citadel", "arachnid", "leviathan", "chronos", "seraph") and pcfg == 0:
        return polish_rim_no_dark_border(c)
    return polish_rim_no_dark_border(fit_on_canvas(c, 1024, target_fill=0.90))


def render_w3_part(idx: int, variant: str, pal: str) -> Image.Image:
    """7/7 Modular Boss Sub-Parts built from painted 2.5D commercial boss & turret assemblies."""
    b7001 = load_master("w3-boss-b/masters/boss_painted_7001_1024.png")
    b7002 = load_master("w3-boss-b/masters/boss_painted_7002_1024.png")
    b7003 = load_master("w3-boss-b/masters/boss_painted_7003_1024.png")
    b_krk = load_master("w3-boss-b/masters/boss_painted_kraken_1024.png")
    e_sau = load_master("w2-enemy-b/masters/enemy_painted_saucer_1024.png")
    d01 = load_master("w1-player-b/masters/drone_painted_01_1024.png")

    c = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    if variant == "command_head":
        head = extract_subpart(b_krk, (315, 255, 709, 735), feather=12)
        paste_with_ao(c, recolor_anodized(head, hue_shift_deg=0, sat_mult=1.12), 512, 512, 1.65, 1.65)
    elif variant == "chrono_gear_turret":
        brl = extract_subpart(d01, (430, 70, 594, 460), feather=8)
        paste_with_ao(c, brl, 512, 745, 1.35, 1.25, flip_y=True)
        paste_with_ao(c, recolor_anodized(e_sau, hue_shift_deg=25, sat_mult=1.15), 512, 455, 0.78, 0.78)
    elif variant == "venom_fang_pod":
        pod = extract_subpart(b7003, (295, 275, 729, 745), feather=12)
        paste_with_ao(c, recolor_anodized(pod, hue_shift_deg=12, sat_mult=1.14), 512, 512, 1.65, 1.65)
    elif variant == "broadside_railgun":
        gat = extract_subpart(b7002, (52, 265, 415, 765), feather=12)
        paste_with_ao(c, gat, 365, 512, 1.18, 1.38)
        paste_with_ao(c, gat, 659, 512, 1.18, 1.38, flip_x=True)
    elif variant == "rotary_saw_ring":
        paste_with_ao(c, recolor_anodized(e_sau, hue_shift_deg=-18, sat_mult=1.22), 512, 512, 0.96, 0.96, angle_deg=15)
    elif variant == "combiner_claw_arm":
        claw = extract_subpart(b_krk, (50, 275, 425, 762), feather=10)
        paste_with_ao(c, recolor_anodized(claw, hue_shift_deg=-115, sat_mult=1.18), 512, 512, 1.68, 1.68, angle_deg=28)
    else:  # energy_snare_web (AP-0128: volumetric plasma web + 8 painted armored node pylons + central core)
        web = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        wd = ImageDraw.Draw(web)
        for rad in (170, 290, 410):
            pts = [(512 + math.cos(a) * rad, 512 + math.sin(a) * rad) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
            wd.line(pts + [pts[0]], fill=(0, 232, 255, 215), width=22)
        for k in range(8):
            a = k * math.pi / 4
            wd.line([(512, 512), (512 + math.cos(a) * 425, 512 + math.sin(a) * 425)], fill=(255, 214, 38, 215), width=18)
        web = web.filter(ImageFilter.GaussianBlur(6.0))
        wd2 = ImageDraw.Draw(web)
        for rad in (170, 290, 410):
            pts = [(512 + math.cos(a) * rad, 512 + math.sin(a) * rad) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
            wd2.line(pts + [pts[0]], fill=(245, 255, 255, 235), width=5)
        c.alpha_composite(web)
        node = recolor_anodized(e_sau, hue_shift_deg=35, sat_mult=1.15)
        for k in range(8):
            a = k * math.pi / 4
            paste_with_ao(c, node, 512 + math.cos(a) * 412, 512 + math.sin(a) * 412, 0.14, 0.14, ao_strength=0.35)
        core = extract_subpart(b7001, (320, 310, 704, 675), feather=16)
        paste_with_ao(c, core, 512, 512, 0.62, 0.62)
        return polish_rim_no_dark_border(c)

    return polish_rim_no_dark_border(fit_on_canvas(c, 1024, target_fill=0.88))
