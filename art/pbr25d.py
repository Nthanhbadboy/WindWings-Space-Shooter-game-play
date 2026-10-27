#!/usr/bin/env python3
"""
art/pbr25d.py — v3 Commercial 2.5D Semi-Realistic Machined-Metallic Shader Engine
for Variant B ("Solar Neon 2.5D") on branch arena/eca8588b-windwings-space-shooter-game-p.

Upgraded for STYLE-CORRECTION ROUND 2 (lần 154 / 6447078574):
  - Automatic corner chamfering (`chamfer_poly`) so plates never look like raw MS-Paint triangles
  - Precision CNC dark-titanium seam bezel + inner bright specular chamfer around every plate
  - Brushed anodized metal longitudinal micro-grain (`anisotropic streak`)
  - Dual-scale 3D curved hull normals + baked multi-layer contact AO between stacked plates
  - High-density engraved panel seams, recessed glowing louver heat-vents, and raised rivets
  - Multi-pane framed armored glass canopies + volumetric linear-light plasma bloom
"""

from __future__ import annotations

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


LIGHT_DIR = np.array([-0.34, -0.56, 0.755], dtype=np.float32)
LIGHT_DIR /= np.linalg.norm(LIGHT_DIR)

VIEW_DIR = np.array([0.0, 0.0, 1.0], dtype=np.float32)
HALF_VEC = LIGHT_DIR + VIEW_DIR
HALF_VEC /= np.linalg.norm(HALF_VEC)


def _rgb(col) -> tuple[float, float, float]:
    return (float(col[0]), float(col[1]), float(col[2]))


def downsample_straight_rgba(canvas: Image.Image, target_size: tuple[int, int], zero_corners: bool = True) -> Image.Image:
    """Premultiply RGB by A -> Lanczos resize -> unpremultiply back to straight RGBA (zero dark halo)."""
    arr = np.asarray(canvas, dtype=np.float32)
    alpha = arr[:, :, 3:4] / 255.0
    pm = np.concatenate([arr[:, :, :3] * alpha, arr[:, :, 3:4]], axis=2)
    pm_img = Image.fromarray(np.clip(np.round(pm), 0, 255).astype(np.uint8), "RGBA")
    pm_small = np.asarray(pm_img.resize(target_size, Image.LANCZOS), dtype=np.float32)
    a_s = pm_small[:, :, 3:4] / 255.0
    rgb_s = np.where(a_s > 1e-3, pm_small[:, :, :3] / np.maximum(a_s, 1e-3), 0.0)
    out = np.concatenate([np.clip(np.round(rgb_s), 0, 255), pm_small[:, :, 3:4]], axis=2).astype(np.uint8)
    if zero_corners:
        out[out[:, :, 3] < 4] = 0
        for cy in (0, target_size[1] - 1):
            for cx in (0, target_size[0] - 1):
                out[cy, cx] = [0, 0, 0, 0]
    return Image.fromarray(out, "RGBA")


def chamfer_poly(pts, frac: float = 0.14) -> list[tuple[float, float]]:
    """Subdivide sharp polygon corners into crisp machined chamfers so zero shapes look toy-like."""
    n = len(pts)
    if n < 3 or n > 18 or frac <= 0.0:
        return list(pts)
    out = []
    for i in range(n):
        p_prev = pts[(i - 1) % n]
        p_cur = pts[i]
        p_next = pts[(i + 1) % n]
        vx1, vy1 = p_prev[0] - p_cur[0], p_prev[1] - p_cur[1]
        vx2, vy2 = p_next[0] - p_cur[0], p_next[1] - p_cur[1]
        d1 = math.hypot(vx1, vy1)
        d2 = math.hypot(vx2, vy2)
        if d1 < 8.0 or d2 < 8.0:
            out.append(p_cur)
            continue
        f1 = min(frac, 18.0 / d1)
        f2 = min(frac, 18.0 / d2)
        out.append((p_cur[0] + vx1 * f1, p_cur[1] + vy1 * f1))
        out.append((p_cur[0] + vx2 * f2, p_cur[1] + vy2 * f2))
    return out


def draw_25d_metal_poly(
    canvas: Image.Image,
    pts,
    base_col,
    shade_col=None,
    light_col=None,
    *,
    bevel_Frac: float = 0.22,
    metallic: float = 0.88,
    greebles: bool = True,
    cast_ao: bool = True,
    glow_vent_c: tuple[int, int, int] | None = None,
    chamfer: float = 0.12,
    seam_bezel: bool = True,
) -> None:
    """Render a machined 2.5D semi-realistic metallic armor cowling onto RGBA `canvas`."""
    if len(pts) < 3:
        return
    if chamfer > 0.0 and len(pts) <= 14:
        pts = chamfer_poly(pts, chamfer)

    W, H = canvas.size
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = 16
    x0, y0 = max(0, int(math.floor(min(xs))) - pad), max(0, int(math.floor(min(ys))) - pad)
    x1, y1 = min(W, int(math.ceil(max(xs))) + pad), min(H, int(math.ceil(max(ys))) + pad)
    bw, bh = x1 - x0, y1 - y0
    if bw <= 3 or bh <= 3:
        return

    lpts = [(x - x0, y - y0) for (x, y) in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    min_dim = min(max(xs) - min(xs), max(ys) - min(ys))
    scale_w = max(1, int(round(max(W, H) / 380.0)))

    # 1. 2x supersampled AA silhouette mask
    mask_2x = Image.new("L", (bw * 2, bh * 2), 0)
    ImageDraw.Draw(mask_2x).polygon([(px * 2.0, py * 2.0) for (px, py) in lpts], fill=255)
    mask_im = mask_2x.resize((bw, bh), Image.BOX)
    m_f = np.asarray(mask_im, dtype=np.float32) / 255.0
    inside = m_f > 0.02
    if not np.any(inside):
        return

    # 2. Deep contact Ambient Occlusion cast onto underlying plates/skeleton
    if cast_ao and min_dim >= 12:
        ao_r = max(2.5, min(14.0, span * 0.042))
        ao_im = mask_im.filter(ImageFilter.GaussianBlur(radius=ao_r))
        ao_a = (np.asarray(ao_im, dtype=np.float32) * 0.56).astype(np.uint8)
        sub = canvas.crop((x0, y0, x1, y1))
        sub_arr = np.asarray(sub, dtype=np.uint8)
        if np.any(sub_arr[:, :, 3] > 8):
            ao_layer = np.zeros((bh, bw, 4), dtype=np.uint8)
            ao_layer[:, :, :3] = (8, 12, 24)
            ao_layer[:, :, 3] = np.minimum(ao_a, (sub_arr[:, :, 3].astype(np.uint16) * 215 // 255).astype(np.uint8))
            ao_pil = Image.alpha_composite(sub, Image.fromarray(ao_layer, "RGBA"))
            canvas.paste(ao_pil, (x0, y0))

    # 3. Micro bevel heightfield + full-plate macro curvature
    r1 = max(1.3, min(10.0, min_dim * bevel_Frac * 0.26 + 1.1))
    r2 = max(2.8, min(28.0, span * bevel_Frac * 0.42 + 2.4))
    h1 = np.asarray(mask_im.filter(ImageFilter.GaussianBlur(radius=r1)), dtype=np.float32) / 255.0
    h2 = np.asarray(mask_im.filter(ImageFilter.GaussianBlur(radius=r2)), dtype=np.float32) / 255.0
    height = 0.42 * h1 + 0.58 * h2

    # High-density mechanical surface details (panel seams, louver vents, rivets)
    seam_ao = np.ones((bh, bw), dtype=np.float32)
    vent_glow = np.zeros((bh, bw), dtype=np.float32)
    rivet_spec = np.zeros((bh, bw), dtype=np.float32)

    if greebles and min_dim >= 26 * scale_w and span >= 44 * scale_w:
        seam_im = Image.new("L", (bw, bh), 128)
        sd = ImageDraw.Draw(seam_im)
        cx_p = sum(p[0] for p in lpts) / len(lpts)
        cy_p = sum(p[1] for p in lpts) / len(lpts)
        sw = max(2, scale_w)

        # Inset armor perimeter panel groove + bright inner lip
        inset_pts = [(cx_p + (px - cx_p) * 0.76, cy_p + (py - cy_p) * 0.76) for (px, py) in lpts]
        sd.line(inset_pts + [inset_pts[0]], fill=18, width=sw * 2)
        inset_hi = [(px + sw * 1.4, py + sw * 1.4) for (px, py) in inset_pts]
        sd.line(inset_hi + [inset_hi[0]], fill=232, width=sw)

        # Secondary inner panel sub-division seams (angled aerospace chevrons + twin offset longitudinal seams!)
        for yf, slope in ((-0.20, 0.24), (0.18, -0.20)):
            py_c = int(cy_p + min_dim * yf)
            dy_e = int(bw * 0.5 * slope)
            if 4 < py_c < bh - 4:
                chev = [(0, py_c + dy_e), (int(cx_p), py_c), (bw, py_c + dy_e)]
                chev_hi = [(0, py_c + dy_e + sw * 2), (int(cx_p), py_c + sw * 2), (bw, py_c + dy_e + sw * 2)]
                sd.line(chev, fill=18, width=sw * 2)
                sd.line(chev_hi, fill=236, width=sw)
        if (max(xs) - min(xs)) >= 64 * scale_w:
            for s_off in (-0.24, 0.24):
                px_s = int(cx_p + bw * s_off)
                sd.line([(px_s, int(bh * 0.14)), (px_s, int(bh * 0.86))], fill=24, width=sw * 2)
                sd.line([(px_s + sw * 2, int(bh * 0.14)), (px_s + sw * 2, int(bh * 0.86))], fill=230, width=sw)

        # Recessed dark louver heat-sink vents
        if min_dim >= 42 * scale_w:
            vw = max(7 * sw, int(min(bw, bh) * 0.20))
            vh = max(2 * sw, 3)
            vx0 = int(cx_p - vw * 0.5)
            vy_base = int(cy_p + min_dim * 0.05)
            gv_im = Image.new("L", (bw, bh), 0)
            gvd = ImageDraw.Draw(gv_im)
            for k in range(4):
                vy = vy_base + k * (vh + 3 * sw)
                if 3 < vy < bh - vh - 3:
                    sd.rectangle([vx0, vy, vx0 + vw, vy + vh], fill=6)
                    sd.line([(vx0, vy + vh + 1), (vx0 + vw, vy + vh + 1)], fill=236, width=sw)
                    if glow_vent_c is not None and k in (0, 1):
                        gvd.rectangle([vx0 + sw, vy, vx0 + vw - sw, vy + vh], fill=225 - k * 55)
            if glow_vent_c is not None:
                vent_glow = np.asarray(gv_im.filter(ImageFilter.GaussianBlur(radius=1.6 * sw)), dtype=np.float32) / 255.0

        # High-density metallic micro-rivets along vertices & mid-edges
        rv_im = Image.new("L", (bw, bh), 0)
        rvd = ImageDraw.Draw(rv_im)
        rr = max(2, int(sw * 1.4))
        n_pts = len(lpts)
        for i in range(n_pts):
            p0 = lpts[i]
            p1 = lpts[(i + 1) % n_pts]
            for t in (0.0, 0.5):
                mx = p0[0] * (1.0 - t) + p1[0] * t
                my = p0[1] * (1.0 - t) + p1[1] * t
                rx = int(cx_p + (mx - cx_p) * 0.64)
                ry = int(cy_p + (my - cy_p) * 0.64)
                if rr + 2 < rx < bw - rr - 2 and rr + 2 < ry < bh - rr - 2:
                    sd.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=215)
                    rvd.ellipse([rx - rr, ry - rr, rx + max(1, rr - 1), ry + max(1, rr - 1)], fill=255)
        rivet_spec = np.asarray(rv_im, dtype=np.float32) / 255.0

        seam_f = (np.asarray(seam_im, dtype=np.float32) - 128.0) / 128.0
        seam_f *= (m_f > 0.86).astype(np.float32)
        height = np.clip(height + seam_f * 0.24, 0.0, 1.25)
        seam_ao = np.where(seam_f < -0.08, np.clip(1.0 + seam_f * 0.85, 0.18, 1.0), 1.0)

    # 4. Dual-scale 3D surface normals (micro bevel/seam + macro curved plate shell)
    gy_m, gx_m = np.gradient(height)
    micro_amp = max(3.6, min(10.5, span * 0.055))
    nx_micro = -gx_m * micro_amp
    ny_micro = -gy_m * micro_amp

    yy_idx, xx_idx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    w_sum = max(float(m_f.sum()), 1.0)
    cx_m = float((xx_idx * m_f).sum() / w_sum)
    cy_m = float((yy_idx * m_f).sum() / w_sum)
    ys_in, xs_in = np.where(m_f > 0.2)
    rx_m = max(float(xs_in.max() - xs_in.min()) * 0.5, 4.0)
    ry_m = max(float(ys_in.max() - ys_in.min()) * 0.5, 4.0)
    ux = np.clip((xx_idx - cx_m) / rx_m, -1.15, 1.15)
    uy = np.clip((yy_idx - cy_m) / ry_m, -1.15, 1.15)

    nx = ux * 0.54 + nx_micro * 0.76
    ny = uy * 0.56 + ny_micro * 0.76
    nz = np.ones_like(nx)
    inv_len = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz + 1e-6)
    nx *= inv_len
    ny *= inv_len
    nz *= inv_len

    # 5. Grounded Commercial Metallic Tone Curve (rich midtones, deep AO, razor-sharp 5% speculars!)
    base = np.array(_rgb(base_col), dtype=np.float32) * 0.86
    if shade_col is not None:
        shade = np.minimum(np.array(_rgb(shade_col), dtype=np.float32) * 0.58, base * 0.36)
    else:
        shade = base * 0.24
    shade = np.maximum(shade, np.array([18.0, 22.0, 32.0], dtype=np.float32))
    light = np.clip(base * 1.28 + 32.0, 0.0, 246.0)

    ndotl = np.clip(nx * LIGHT_DIR[0] + ny * LIGHT_DIR[1] + nz * LIGHT_DIR[2], -1.0, 1.0)
    ndoth = np.clip(nx * HALF_VEC[0] + ny * HALF_VEC[1] + nz * HALF_VEC[2], 0.0, 1.0)

    t = np.clip((ndotl + 0.22) / 1.28, 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)
    low_w = np.clip(1.0 - t * 1.85, 0.0, 1.0)
    hi_w = np.clip((t - 0.58) * 2.1, 0.0, 1.0)
    mid_w = np.clip(1.0 - low_w - hi_w, 0.0, 1.0)

    # Subtle brushed-titanium vertical micro-streaks (+/- 3.5%)
    grain = 1.0 + 0.035 * np.sin(xx_idx * 1.9 + np.sin(yy_idx * 0.14) * 1.5)

    spec_broad = (ndoth ** 24.0) * (0.22 * metallic)
    spec_sharp = (ndoth ** 72.0) * (0.58 * metallic)

    edge_band = np.clip(1.0 - h1, 0.0, 1.0) * (m_f > 0.18)
    top_rim = np.clip(-ny, 0.0, 1.0) ** 1.65 * edge_band * 0.62
    bot_bounce = np.clip(ny, 0.0, 1.0) ** 1.75 * edge_band * 0.18

    # Machined CNC bezel: dark-titanium outer groove + crisp inner chamfer lip!
    bezel_mul = np.ones_like(m_f)
    chamfer_add = np.zeros_like(m_f)
    if seam_bezel and min_dim >= 16:
        outer_groove = np.clip((0.76 - h1) / 0.58, 0.0, 1.0) * (m_f > 0.22)
        bezel_mul = 1.0 - outer_groove * 0.52
        inner_lip = np.exp(-((h1 - 0.82) / 0.09) ** 2) * np.clip(-0.45 * nx - 0.75 * ny + 0.20, 0.0, 1.1)
        chamfer_add = inner_lip * 34.0

    edge_ao = (0.56 + 0.44 * np.clip(h1 * 1.45, 0.0, 1.0)) * seam_ao * bezel_mul

    out = np.zeros((bh, bw, 4), dtype=np.float32)
    sky_tint = np.array([96.0, 214.0, 255.0], dtype=np.float32)
    warm_rim = np.array([255.0, 248.0, 224.0], dtype=np.float32)

    for c in range(3):
        col = (shade[c] * low_w + base[c] * mid_w + light[c] * hi_w) * edge_ao * grain
        col += (light[c] * 0.42 + 148.0) * spec_broad
        col += 255.0 * spec_sharp
        col += warm_rim[c] * top_rim + chamfer_add
        col += sky_tint[c] * bot_bounce
        col += 245.0 * rivet_spec * 0.65
        if glow_vent_c is not None:
            col = col * (1.0 - vent_glow * 0.55) + float(glow_vent_c[c]) * vent_glow * 1.35
        out[:, :, c] = np.clip(col, 0.0, 255.0)

    out[:, :, 3] = np.clip(m_f * 255.0, 0.0, 255.0)
    layer = Image.fromarray(out.astype(np.uint8), "RGBA")
    canvas.alpha_composite(layer, (x0, y0))


def draw_25d_glass_dome(
    canvas: Image.Image,
    pts,
    deep_col=(8, 42, 128),
    mid_col=(0, 196, 255),
    rim_col=(188, 250, 255),
    *,
    core_rgb=None,
    deep_rgb=None,
) -> None:
    """Render a curved 3D tinted glass cockpit dome with horizon reflection & zenith specular."""
    if deep_rgb is not None:
        deep_col = deep_rgb
    if core_rgb is not None:
        mid_col = core_rgb
    if len(pts) < 3:
        return
    W, H = canvas.size
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = 8
    x0, y0 = max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad)
    x1, y1 = min(W, int(max(xs)) + pad), min(H, int(max(ys)) + pad)
    bw, bh = x1 - x0, y1 - y0
    if bw <= 3 or bh <= 3:
        return
    lpts = [(x - x0, y - y0) for (x, y) in pts]

    mask_2x = Image.new("L", (bw * 2, bh * 2), 0)
    ImageDraw.Draw(mask_2x).polygon([(px * 2.0, py * 2.0) for (px, py) in lpts], fill=255)
    mask_im = mask_2x.resize((bw, bh), Image.BOX)
    m_f = np.asarray(mask_im, dtype=np.float32) / 255.0
    if not np.any(m_f > 0.02):
        return

    r = max(2.2, min(bw, bh) * 0.24)
    dome = np.asarray(mask_im.filter(ImageFilter.GaussianBlur(radius=r)), dtype=np.float32) / 255.0
    gy, gx = np.gradient(dome)
    nx, ny = -gx * 8.0, -gy * 8.0
    nz = np.ones_like(nx)
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz + 1e-6)
    nx, ny, nz = nx * inv, ny * inv, nz * inv

    fresnel = np.clip(1.0 - nz, 0.0, 1.0) ** 1.4
    spec1 = np.clip(nx * (-0.36) + ny * (-0.58) + nz * 0.73, 0.0, 1.0) ** 32.0
    spec2 = np.clip(nx * 0.28 + ny * 0.45 + nz * 0.85, 0.0, 1.0) ** 16.0 * 0.32
    grad_y = np.linspace(0.0, 1.0, bh, dtype=np.float32)[:, None]

    out = np.zeros((bh, bw, 4), dtype=np.float32)
    for c in range(3):
        body = deep_col[c] * (1.0 - grad_y * 0.65) + mid_col[c] * (grad_y * 0.65 + dome * 0.35)
        col = body * (0.72 + 0.28 * dome) + rim_col[c] * fresnel * 0.78 + 255.0 * (spec1 * 0.96 + spec2)
        out[:, :, c] = np.clip(col, 0.0, 255.0)
    out[:, :, 3] = np.clip(m_f * 255.0, 0.0, 255.0)
    canvas.alpha_composite(Image.fromarray(out.astype(np.uint8), "RGBA"), (x0, y0))


def draw_25d_plasma_bloom(
    canvas: Image.Image,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    outer_rgb=(0, 212, 255),
    core_rgb=(255, 255, 255),
    intensity: float = 1.0,
    strength: float | None = None,
) -> None:
    """Linear-light radial/elliptical plasma glow with incandescent white core."""
    if strength is not None:
        intensity = strength
    W, H = canvas.size
    pad_x, pad_y = int(rx * 2.2 + 6), int(ry * 2.2 + 6)
    x0, y0 = max(0, int(cx) - pad_x), max(0, int(cy) - pad_y)
    x1, y1 = min(W, int(cx) + pad_x), min(H, int(cy) + pad_y)
    bw, bh = x1 - x0, y1 - y0
    if bw <= 2 or bh <= 2:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt(((xx - cx) / max(rx, 1.0)) ** 2 + ((yy - cy) / max(ry, 1.0)) ** 2)
    halo = np.exp(-(d * 1.08) ** 2) * intensity
    core = np.exp(-(d * 2.45) ** 2) * intensity
    out = np.zeros((bh, bw, 4), dtype=np.float32)
    a = np.clip(halo * 0.92 + core * 0.65, 0.0, 1.0)
    w_core = np.clip(core / np.maximum(a, 1e-4), 0.0, 1.0)
    for c in range(3):
        out[:, :, c] = np.clip(outer_rgb[c] * (1.0 - w_core) + core_rgb[c] * w_core, 0.0, 255.0)
    out[:, :, 3] = a * 255.0
    canvas.alpha_composite(Image.fromarray(out.astype(np.uint8), "RGBA"), (x0, y0))


def draw_25d_9slice_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    rim_triple,
    fill_rgba,
    inner_glow_rgb=(0, 224, 255),
    bevel_w: int = 12,
) -> None:
    """Uniform-edge 9-slice metallic beveled frame/button (ASSETS.md §5 compliant)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    bw, bh = x1 - x0, y1 - y0
    if bw <= 4 or bh <= 4:
        return
    base_c, shade_c, light_c = rim_triple

    m2 = Image.new("L", (bw * 2, bh * 2), 0)
    ImageDraw.Draw(m2).rounded_rectangle([0, 0, bw * 2 - 1, bh * 2 - 1], radius=radius * 2, fill=255)
    mask_im = m2.resize((bw, bh), Image.BOX)
    m_f = np.asarray(mask_im, dtype=np.float32) / 255.0

    r = max(2.0, min(bevel_w * 0.55, min(bw, bh) * 0.22))
    h_im = mask_im.filter(ImageFilter.GaussianBlur(radius=r))
    h_f = np.asarray(h_im, dtype=np.float32) / 255.0
    gy, gx = np.gradient(h_f)
    nx, ny = -gx * 8.0, -gy * 8.0
    nz = np.ones_like(nx)
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz + 1e-6)
    nx, ny, nz = nx * inv, ny * inv, nz * inv

    ndotl = np.clip(nx * LIGHT_DIR[0] + ny * LIGHT_DIR[1] + nz * LIGHT_DIR[2], 0.0, 1.0)
    ndoth = np.clip(nx * HALF_VEC[0] + ny * HALF_VEC[1] + nz * HALF_VEC[2], 0.0, 1.0)
    spec = (ndoth ** 24.0) * 0.72
    top_rim = np.clip(-ny, 0.0, 1.0) ** 1.6 * np.clip(1.0 - h_f, 0.0, 1.0) * 0.85

    out = np.zeros((bh, bw, 4), dtype=np.float32)
    for c in range(3):
        col = shade_c[c] * (1.0 - ndotl) + base_c[c] * (ndotl * 0.65) + light_c[c] * (ndotl * 0.35)
        col += 255.0 * (spec + top_rim * 0.55)
        out[:, :, c] = np.clip(col, 0.0, 255.0)
    out[:, :, 3] = m_f * 255.0
    panel = Image.fromarray(out.astype(np.uint8), "RGBA")

    ins = max(4, bevel_w)
    if bw > ins * 2 + 8 and bh > ins * 2 + 8:
        well = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        wd = ImageDraw.Draw(well)
        ir = max(3, radius - ins)
        wd.rounded_rectangle([ins - 2, ins - 2, bw - ins + 1, bh - ins + 1], radius=ir + 2, fill=(14, 24, 56, 215))
        wd.rounded_rectangle([ins, ins, bw - ins - 1, bh - ins - 1], radius=ir, fill=fill_rgba, outline=(*inner_glow_rgb[:3], 210), width=2)
        panel = Image.alpha_composite(panel, well)

    canvas.alpha_composite(panel, (x0, y0))
