#!/usr/bin/env python3
"""
art/pbr25d.py — v2 True 2.5D Semi-Realistic Sculpted Metallic Engine for Variant B ("Solar Neon 2.5D").

Key v2 upgrades after visual side-by-side inspection against ships-01.jpg / drones-01.jpg / bosses-01.jpg:
  1. Dual-Scale 3D Normals (N_macro curved hull shell across full plate + N_micro machined edge chamfer,
     bold engraved panel-seams, recessed dark cooling vents & raised specular rivets) -> NEVER blows out
     to flat white even on 1024x1024 master plates; produces 6-9 rich continuous metallic stops per plate!
  2. Deep anodized metallic shadow floor (0.16..0.24 V in underside creases) + top zenith rim-light +
     focused Blinn-Phong specular highlight + subtle sky/neon underside bounce.
  3. ZERO dark cartoon outline stroke (outline_dark_px <= 1.0 px).
"""

from __future__ import annotations

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _norm3(x: float, y: float, z: float) -> tuple[float, float, float]:
    n = math.sqrt(x * x + y * y + z * z)
    return (x / n, y / n, z / n)


L_KEY    = _norm3(-0.38, -0.68, 0.62)   # Sunlit top-left-front key light
H_BROAD  = _norm3(-0.26, -0.50, 0.83)   # Broad brushed-metal sheen half-vector
H_SHARP  = _norm3(-0.22, -0.44, 0.87)   # Sharp specular highlight half-vector
L_BOUNCE = _norm3(0.36,  0.80, 0.48)    # Cool sky/cyan underside bounce


def downsample_straight_rgba(im: Image.Image, target_size: tuple[int, int], zero_corners: bool = True) -> Image.Image:
    if im.size == target_size:
        arr = np.asarray(im).copy()
    else:
        f = np.asarray(im, dtype=np.float32)
        a = f[:, :, 3:4] / 255.0
        pm = Image.fromarray(np.clip(np.round(np.concatenate([f[:, :, :3] * a, f[:, :, 3:4]], axis=2)), 0, 255).astype(np.uint8), "RGBA")
        s = np.asarray(pm.resize(target_size, Image.LANCZOS), dtype=np.float32)
        sa = s[:, :, 3:4] / 255.0
        rgb = np.where(sa > 1e-3, s[:, :, :3] / np.maximum(sa, 1e-3), 0.0)
        arr = np.concatenate([np.clip(np.round(rgb), 0, 255), np.clip(np.round(s[:, :, 3:4]), 0, 255)], axis=2).astype(np.uint8)
    if zero_corners:
        arr[arr[:, :, 3] < 4] = 0
        for cy in (0, target_size[1] - 1):
            for cx in (0, target_size[0] - 1):
                arr[cy, cx] = [0, 0, 0, 0]
    return Image.fromarray(arr, "RGBA")


def apply_contact_ao(canvas: Image.Image, mask_l: Image.Image, x0: int, y0: int, radius: float = 8.0, strength: float = 0.62, dy: int = 4) -> None:
    """Strong, realistic 2.5D contact Ambient Occlusion cast onto underlying armor plates."""
    W, H = canvas.size
    bw, bh = mask_l.size
    pad = int(radius * 2.2 + abs(dy) + 4)
    cx0, cy0 = max(0, x0 - pad), max(0, y0 - pad)
    cx1, cy1 = min(W, x0 + bw + pad), min(H, y0 + bh + pad)
    if cx1 <= cx0 or cy1 <= cy0:
        return

    ao_img = Image.new("L", (cx1 - cx0, cy1 - cy0), 0)
    ao_img.paste(mask_l, (x0 - cx0, y0 - cy0 + dy))
    ao_img = ao_img.filter(ImageFilter.GaussianBlur(radius=radius))
    ao = np.asarray(ao_img, dtype=np.float32) / 255.0

    sub = np.asarray(canvas.crop((cx0, cy0, cx1, cy1)), dtype=np.float32).copy()
    if not np.any(sub[:, :, 3] > 2.0):
        return
    mul = 1.0 - strength * ao
    sub[:, :, 0] *= mul
    sub[:, :, 1] *= mul
    sub[:, :, 2] *= mul
    canvas.paste(Image.fromarray(np.clip(sub, 0, 255).astype(np.uint8), "RGBA"), (cx0, cy0))


def draw_25d_metal_poly(
    canvas: Image.Image,
    pts: list[tuple[float, float]],
    base_c: tuple[int, int, int, int],
    shade_c: tuple[int, int, int, int] | None = None,
    light_c: tuple[int, int, int, int] | None = None,
    *,
    bevel_px: float | None = None,
    metallic: float = 0.85,
    greebles: bool = True,
    cast_ao: bool = True,
    glow_vent_c: tuple[int, int, int] = (0, 228, 255),
) -> None:
    if len(pts) < 3:
        return
    W, H = canvas.size
    xs = [float(p[0]) for p in pts]
    ys = [float(p[1]) for p in pts]
    pad = 14
    x0, y0 = max(0, int(math.floor(min(xs))) - pad), max(0, int(math.floor(min(ys))) - pad)
    x1, y1 = min(W, int(math.ceil(max(xs))) + pad), min(H, int(math.ceil(max(ys))) + pad)
    bw, bh = x1 - x0, y1 - y0
    if bw <= 3 or bh <= 3:
        return

    lpts = [(x - x0, y - y0) for (x, y) in pts]
    min_x, max_x = min(p[0] for p in lpts), max(p[0] for p in lpts)
    min_y, max_y = min(p[1] for p in lpts), max(p[1] for p in lpts)
    span_x = max(max_x - min_x, 2.0)
    span_y = max(max_y - min_y, 2.0)
    span = max(span_x, span_y)
    min_span = max(min(span_x, span_y), 2.0)
    cx, cy = (min_x + max_x) * 0.5, (min_y + max_y) * 0.5

    # 1. Anti-aliased 2x silhouette mask (zero black cartoon stroke)
    m2 = Image.new("L", (bw * 2, bh * 2), 0)
    ImageDraw.Draw(m2).polygon([(x * 2.0, y * 2.0) for (x, y) in lpts], fill=255)
    mask_l = m2.resize((bw, bh), Image.BILINEAR)
    alpha_f = np.asarray(mask_l, dtype=np.float32) / 255.0
    if alpha_f.max() < 0.02:
        return

    # 2. Contact AO shadow cast onto lower armor layers
    if cast_ao and min_span >= 8.0:
        ao_r = max(2.8, min(12.0, min_span * 0.13))
        apply_contact_ao(canvas, mask_l, x0, y0, radius=ao_r, strength=0.60, dy=max(2, int(ao_r * 0.5)))

    # 3. Dual-Scale 3D Height & Macro Curvature
    r_bev = bevel_px if bevel_px is not None else max(2.0, min(9.5, min_span * 0.12))
    r_mid = max(r_bev * 2.6, min(26.0, min_span * 0.34))
    h_bev = np.asarray(mask_l.filter(ImageFilter.GaussianBlur(radius=r_bev)), dtype=np.float32) / 255.0
    h_mid = np.asarray(mask_l.filter(ImageFilter.GaussianBlur(radius=r_mid)), dtype=np.float32) / 255.0
    micro_h = 0.62 * h_bev + 0.38 * h_mid

    # 4. Crisp Downsampling-Proof Mechanical Seams, Recessed Dark Vents & Specular Rivets
    groove_ao = np.ones((bh, bw), dtype=np.float32)
    vent_glow = np.zeros((bh, bw), dtype=np.float32)
    scale_w = max(2, int(round(span / 105.0)))  # scales cleanly from 256->1024 canvases!

    if greebles and min_span >= 28.0:
        interior = np.clip((h_bev - 0.58) * 3.5, 0.0, 1.0)
        seam_img = Image.new("L", (bw, bh), 0)
        sd = ImageDraw.Draw(seam_img)

        # Recessed inset armor plate seam
        ins_pts = [(cx + (x - cx) * 0.70, cy + (y - cy) * 0.70) for (x, y) in lpts]
        sd.line(ins_pts + [ins_pts[0]], fill=235, width=scale_w)

        # Structural cross-panel seams
        if span >= 64.0:
            if span_y >= span_x:
                sd.line([(0, cy - span_y * 0.12), (bw, cy - span_y * 0.05)], fill=215, width=scale_w)
                sd.line([(0, cy + span_y * 0.18), (bw, cy + span_y * 0.24)], fill=215, width=scale_w)
            else:
                sd.line([(cx - span_x * 0.12, 0), (cx - span_x * 0.05, bh)], fill=215, width=scale_w)
                sd.line([(cx + span_x * 0.16, 0), (cx + span_x * 0.22, bh)], fill=215, width=scale_w)

        seam_arr = (np.asarray(seam_img.filter(ImageFilter.GaussianBlur(radius=0.9 * scale_w * 0.5)), dtype=np.float32) / 255.0) * interior
        micro_h -= 0.22 * seam_arr
        groove_ao *= (1.0 - 0.58 * seam_arr)

        # Recessed dark metallic louver cooling vents
        if min_span >= 46.0 and span >= 82.0:
            vent_img = Image.new("L", (bw, bh), 0)
            vd = ImageDraw.Draw(vent_img)
            n_slots = 4 if span >= 135.0 else 3
            vw = max(8.0, min(32.0, span_x * 0.26))
            sp = max(5.0, min(13.0, span_y * 0.065))
            vy0 = cy - (n_slots - 1) * sp * 0.5
            slot_w = max(2, int(sp * 0.48))
            for k in range(n_slots):
                vy = vy0 + k * sp
                vd.line([(cx - vw * 0.5, vy), (cx + vw * 0.5, vy + vw * 0.12)], fill=255, width=slot_w)
            vent_arr = (np.asarray(vent_img.filter(ImageFilter.GaussianBlur(radius=0.8)), dtype=np.float32) / 255.0) * interior
            micro_h -= 0.28 * vent_arr
            groove_ao *= (1.0 - 0.78 * vent_arr)
            vent_glow = np.clip(vent_arr - 0.45, 0.0, 1.0) * 0.55

        # Specular raised metallic rivets at armor corners
        riv_img = Image.new("L", (bw, bh), 0)
        rd = ImageDraw.Draw(riv_img)
        rr = max(1.6, min(4.2, min_span * 0.036))
        for vx, vy in lpts[::max(1, len(lpts) // 6)]:
            rx = cx + (vx - cx) * 0.78
            ry = cy + (vy - cy) * 0.78
            rd.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=255)
        riv_arr = (np.asarray(riv_img.filter(ImageFilter.GaussianBlur(radius=1.0)), dtype=np.float32) / 255.0) * interior
        micro_h += 0.16 * riv_arr

    # 5. Combine Full-Plate 3D Macro Curvature Normal + Micro Bevel/Greeble Normal
    gy, gx = np.gradient(micro_h)
    bump_scale = max(8.5, min(18.0, 28.0 / max(r_bev, 1.5)))

    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    # Macro curved armor shell normal: spans [-1, +1] across EVERY plate regardless of canvas size!
    ux = (xx - cx) / (span_x * 0.52)
    uy = (yy - cy) / (span_y * 0.52)
    nx = -gx * bump_scale + ux * 0.68
    ny = -gy * bump_scale + uy * 0.62
    nz = np.ones_like(nx)
    inv_len = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz + 1e-6)
    nx *= inv_len
    ny *= inv_len
    nz *= inv_len

    # 6. Rich Semi-Realistic 2.5D Metallic Shading (deep metallic shadows + vibrant midtone + focused specular)
    b_rgb = np.array(base_c[:3], dtype=np.float32) / 255.0
    # Guarantee deep 3D shadow contrast even when caller passes a bright pastel shade_c!
    raw_s = (np.array(shade_c[:3], dtype=np.float32) / 255.0) if shade_c is not None else (b_rgb * 0.25)
    s_rgb = np.minimum(raw_s * 0.68, b_rgb * 0.34)
    l_rgb = (np.array(light_c[:3], dtype=np.float32) / 255.0) if light_c is not None else np.clip(b_rgb * 1.32 + 0.16, 0.0, 1.0)

    # Subtle brushed-alloy micro-grain
    grain = 1.0 + 0.035 * np.sin((xx * 0.72 + yy * 0.16) * 1.1)

    ndotl = np.clip(nx * L_KEY[0] + ny * L_KEY[1] + nz * L_KEY[2], -1.0, 1.0)
    # Centered S-curve metallic diffuse so midtone dominates ~50%, deep shadow ~30%, bright crest ~20%
    t_diff = np.clip(ndotl * 0.62 + 0.34, 0.0, 1.0)
    lo_t = np.clip(t_diff * 1.85, 0.0, 1.0)[:, :, None]
    hi_t = (np.clip((t_diff - 0.54) / 0.46, 0.0, 1.0) ** 1.45)[:, :, None]

    albedo = s_rgb[None, None, :] * (1.0 - lo_t) + b_rgb[None, None, :] * lo_t
    albedo = albedo * (1.0 - hi_t * 0.72) + l_rgb[None, None, :] * (hi_t * 0.72)
    albedo *= grain[:, :, None]

    # Focused metallic specular (prevents washing out midtones while giving crisp metal gleam!)
    ndoth1 = np.clip(nx * H_BROAD[0] + ny * H_BROAD[1] + nz * H_BROAD[2], 0.0, 1.0)
    ndoth2 = np.clip(nx * H_SHARP[0] + ny * H_SHARP[1] + nz * H_SHARP[2], 0.0, 1.0)
    spec_broad = (ndoth1 ** 16.0) * (0.24 * metallic)
    spec_sharp = (ndoth2 ** 52.0) * (0.68 * metallic)
    spec_tint = 0.45 * l_rgb + 0.55 * np.array([1.0, 1.0, 1.0], dtype=np.float32)

    # Crisp Top Rim-Light ("rim-light từ trên" on top-facing beveled edges only!)
    bevel_zone = np.clip(1.08 - h_bev, 0.0, 1.0)
    top_rim = (np.clip(-ny, 0.0, 1.0) ** 2.6) * bevel_zone * 0.88
    rim_tint = 0.35 * l_rgb + 0.65 * np.array([0.95, 0.98, 1.0], dtype=np.float32)

    # Underside beveled dark-metal self-AO + subtle cool cyan bounce
    edge_ao = 1.0 - 0.52 * (np.clip(ny, 0.0, 1.0) ** 1.5) * bevel_zone
    bounce = (np.clip(nx * L_BOUNCE[0] + ny * L_BOUNCE[1] + nz * L_BOUNCE[2], 0.0, 1.0) ** 2.8) * bevel_zone
    bounce_rgb = np.array([0.14, 0.58, 0.96], dtype=np.float32) * 0.22

    rgb = albedo * (groove_ao * edge_ao)[:, :, None]
    rgb += (spec_broad + spec_sharp)[:, :, None] * spec_tint[None, None, :] * groove_ao[:, :, None]
    rgb += top_rim[:, :, None] * rim_tint[None, None, :]
    rgb += bounce[:, :, None] * bounce_rgb[None, None, :]
    if np.any(vent_glow > 0):
        vg_c = np.array(glow_vent_c, dtype=np.float32) / 255.0
        rgb += vent_glow[:, :, None] * vg_c[None, None, :]

    out = np.zeros((bh, bw, 4), dtype=np.uint8)
    out[:, :, :3] = np.clip(np.round(rgb * 255.0), 0, 255).astype(np.uint8)
    out[:, :, 3] = np.clip(np.round(alpha_f * (base_c[3] if len(base_c) > 3 else 255)), 0, 255).astype(np.uint8)
    canvas.alpha_composite(Image.fromarray(out, "RGBA"), (x0, y0))


def draw_25d_glass_dome(
    canvas: Image.Image,
    pts: list[tuple[float, float]],
    core_rgb: tuple[int, int, int] = (0, 228, 255),
    deep_rgb: tuple[int, int, int] = (6, 26, 72),
) -> None:
    if len(pts) < 3:
        return
    W, H = canvas.size
    xs, ys = [float(p[0]) for p in pts], [float(p[1]) for p in pts]
    pad = 8
    x0, y0 = max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad)
    x1, y1 = min(W, int(max(xs)) + pad), min(H, int(max(ys)) + pad)
    bw, bh = x1 - x0, y1 - y0
    if bw <= 3 or bh <= 3:
        return
    lpts = [(x - x0, y - y0) for (x, y) in pts]
    cx = sum(p[0] for p in lpts) / len(lpts)
    cy = sum(p[1] for p in lpts) / len(lpts)
    rx = max((max(p[0] for p in lpts) - min(p[0] for p in lpts)) * 0.5, 2.0)
    ry = max((max(p[1] for p in lpts) - min(p[1] for p in lpts)) * 0.5, 2.0)

    m2 = Image.new("L", (bw * 2, bh * 2), 0)
    ImageDraw.Draw(m2).polygon([(x * 2, y * 2) for (x, y) in lpts], fill=255)
    ml = m2.resize((bw, bh), Image.BILINEAR)
    af = np.asarray(ml, dtype=np.float32) / 255.0
    apply_contact_ao(canvas, ml, x0, y0, radius=5.0, strength=0.62, dy=3)

    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    ux, uy = (xx - cx) / rx, (yy - cy) / ry
    r2 = np.clip(ux * ux + uy * uy, 0.0, 1.3)
    nz = np.sqrt(np.clip(1.0 - r2 * 0.84, 0.04, 1.0))
    nx, ny = ux * 0.86, uy * 0.86

    caustic = np.clip(1.0 - np.sqrt(ux * ux * 1.25 + (uy - 0.22) ** 2 * 1.15), 0.0, 1.0) ** 1.6
    fresnel = np.clip(1.0 - nz, 0.0, 1.0) ** 2.0
    c_deep = np.array(deep_rgb, dtype=np.float32) / 255.0
    c_core = np.array(core_rgb, dtype=np.float32) / 255.0

    rgb = c_deep[None, None, :] * (1.0 - caustic[:, :, None]) + c_core[None, None, :] * (caustic[:, :, None] * 1.06)
    rgb += (caustic ** 3.6)[:, :, None] * np.array([0.45, 0.50, 0.52], dtype=np.float32)[None, None, :]
    spec1 = np.clip(-(nx * 0.48 + ny * 0.62) + nz * 0.50, 0.0, 1.0) ** 22.0
    spec2 = np.clip(-(nx * 0.36 + ny * 0.56) + nz * 0.60, 0.0, 1.0) ** 72.0
    rgb += spec1[:, :, None] * 0.52 + spec2[:, :, None] * 0.95
    rgb += fresnel[:, :, None] * c_core[None, None, :] * 0.28

    out = np.zeros((bh, bw, 4), dtype=np.uint8)
    out[:, :, :3] = np.clip(np.round(rgb * 255.0), 0, 255).astype(np.uint8)
    out[:, :, 3] = np.clip(np.round(af * 255.0), 0, 255).astype(np.uint8)
    canvas.alpha_composite(Image.fromarray(out, "RGBA"), (x0, y0))


def draw_25d_plasma_bloom(
    canvas: Image.Image,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    glow_rgb: tuple[int, int, int] = (0, 232, 255),
    strength: float = 0.92,
) -> None:
    W, H = canvas.size
    pad_x, pad_y = int(rx * 2.2 + 6), int(ry * 2.2 + 6)
    x0, y0 = max(0, int(cx) - pad_x), max(0, int(cy) - pad_y)
    x1, y1 = min(W, int(cx) + pad_x), min(H, int(cy) + pad_y)
    bw, bh = x1 - x0, y1 - y0
    if bw <= 2 or bh <= 2:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt(((xx - cx) / max(rx, 1.0)) ** 2 + ((yy - cy) / max(ry, 1.0)) ** 2)
    halo = np.exp(-(d * d) * 1.2) * strength
    core = np.exp(-(d * d) * 5.0) * strength
    g = np.array(glow_rgb, dtype=np.float32)
    rgb = g[None, None, :] * (1.0 - core[:, :, None]) + 255.0 * core[:, :, None]
    out = np.zeros((bh, bw, 4), dtype=np.uint8)
    out[:, :, :3] = np.clip(np.round(rgb), 0, 255).astype(np.uint8)
    out[:, :, 3] = np.clip(np.round(halo * 255.0), 0, 255).astype(np.uint8)
    canvas.alpha_composite(Image.fromarray(out, "RGBA"), (x0, y0))


def draw_25d_9slice_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    rim_triple: tuple[tuple[int, int, int, int], tuple[int, int, int, int], tuple[int, int, int, int]],
    well_rgba: tuple[int, int, int, int],
    inner_glow_rgb: tuple[int, int, int] = (0, 224, 255),
    bevel_w: int = 12,
) -> None:
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    if bw <= 6 or bh <= 6:
        return

    m2 = Image.new("L", (bw * 2, bh * 2), 0)
    ImageDraw.Draw(m2).rounded_rectangle([0, 0, bw * 2 - 1, bh * 2 - 1], radius=radius * 2, fill=255)
    ml = m2.resize((bw, bh), Image.BILINEAR)
    af = np.asarray(ml, dtype=np.float32) / 255.0

    hb = np.asarray(ml.filter(ImageFilter.GaussianBlur(radius=max(2.2, bevel_w * 0.42))), dtype=np.float32) / 255.0
    gy, gx = np.gradient(hb)
    nx, ny = -gx * 10.5, -gy * 10.5
    il = 1.0 / np.sqrt(nx * nx + ny * ny + 1.0)
    nx, ny, nz = nx * il, ny * il, il

    b_c = np.array(rim_triple[0][:3], dtype=np.float32) / 255.0
    s_c = np.minimum(np.array(rim_triple[1][:3], dtype=np.float32) / 255.0 * 0.65, b_c * 0.35)
    l_c = np.array(rim_triple[2][:3], dtype=np.float32) / 255.0

    yy = np.linspace(0.0, 1.0, bh, dtype=np.float32)[:, None]
    v_grad = 1.12 - 0.34 * yy
    t = np.clip((nx * -0.32 + ny * -0.74 + nz * 0.59) * 0.65 + 0.38, 0.0, 1.0)[:, :, None]
    rgb = (s_c[None, None, :] * (1.0 - t) + l_c[None, None, :] * t) * 0.62 + b_c[None, None, :] * 0.38
    rgb *= v_grad[:, :, None]
    top_rim = (np.clip(-ny, 0.0, 1.0) ** 2.6) * np.clip(1.08 - hb, 0.0, 1.0) * 0.72
    rgb += top_rim[:, :, None]

    frame = np.zeros((bh, bw, 4), dtype=np.uint8)
    frame[:, :, :3] = np.clip(np.round(rgb * 255.0), 0, 255).astype(np.uint8)
    frame[:, :, 3] = np.clip(np.round(af * 255.0), 0, 255).astype(np.uint8)
    layer = Image.fromarray(frame, "RGBA")

    ins = max(6, bevel_w)
    if bw > ins * 2 + 8 and bh > ins * 2 + 8:
        well_im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        wd = ImageDraw.Draw(well_im)
        r_in = max(4, radius - ins)
        wd.rounded_rectangle([ins, ins, bw - 1 - ins, bh - 1 - ins], radius=r_in, fill=well_rgba)
        wd.rounded_rectangle([ins, ins, bw - 1 - ins, bh - 1 - ins], radius=r_in, outline=(*inner_glow_rgb, 205), width=2)
        wd.line([(ins + r_in, ins + 2), (bw - 1 - ins - r_in, ins + 2)], fill=(4, 8, 22, 185), width=3)
        wd.line([(ins + r_in, bh - 2 - ins), (bw - 1 - ins - r_in, bh - 2 - ins)], fill=(*inner_glow_rgb, 235), width=2)
        layer.alpha_composite(well_im)

    canvas.alpha_composite(layer, (x0, y0))
