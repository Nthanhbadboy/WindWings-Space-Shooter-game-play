"""Lossless-source ingestion for NEW Variant-B painted masters.

Only AI-painted masters generated for this branch are accepted here; never use
APK/GCenter atlases or contact-sheet crops as game assets. The extractor removes
the generated black backing, rejects isolated star specks, preserves straight
RGBA, and fits the complete subject into a transparent master canvas.
"""
from __future__ import annotations

import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def _flood_background(passable: np.ndarray) -> np.ndarray:
    h, w = passable.shape
    cur = np.zeros((h, w), dtype=bool)
    cur[0, :] = passable[0, :]
    cur[-1, :] = passable[-1, :]
    cur[:, 0] = passable[:, 0]
    cur[:, -1] = passable[:, -1]
    for size in (15, 3):
        previous = -1
        while True:
            total = int(cur.sum())
            if total == previous:
                break
            previous = total
            dil = np.asarray(Image.fromarray(cur.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(size))) > 0
            cur = (cur | dil) & passable
    return cur


def extract_painted(raw_path: str, *, crop_box=None, canvas=1024, fill=0.88,
                    rotate=None, widen=1.0, brightness=1.03, saturation=1.06,
                    contrast=1.02, remove_specks=True, cut_black=False,
                    keep_largest=False) -> Image.Image:
    """Return a transparent, centered master from a generated black-backed PNG."""
    source = Image.open(raw_path).convert("RGB")
    if crop_box is not None:
        source = source.crop(crop_box)
    if rotate == "270":
        source = source.transpose(Image.ROTATE_270)
    elif rotate == "180":
        source = source.transpose(Image.ROTATE_180)
    arr = np.asarray(source, dtype=np.float32)
    h, w, _ = arr.shape
    corners = np.concatenate([
        arr[:8, :8].reshape(-1, 3), arr[:8, -8:].reshape(-1, 3),
        arr[-8:, :8].reshape(-1, 3), arr[-8:, -8:].reshape(-1, 3),
    ])
    bg = np.median(corners, axis=0)
    diff = np.sqrt(np.sum((arr - bg) ** 2, axis=2))

    # Mask at a bounded resolution: deterministic and much faster than a full-
    # resolution flood fill on 1408px painted sources.
    scale = min(1.0, 384.0 / max(h, w))
    small_size = (max(8, round(w * scale)), max(8, round(h * scale)))
    small_diff = np.asarray(Image.fromarray(np.clip(diff, 0, 255).astype(np.uint8), "L").resize(small_size, Image.BILINEAR), dtype=np.float32)
    bg_small = _flood_background(small_diff < 62.0)
    fg_small = ~bg_small
    if remove_specks:
        # Erode away isolated stars, then dilate the surviving large subject
        # region. Thin guns close to the hull are restored by the final mask.
        core = np.asarray(Image.fromarray(fg_small.astype(np.uint8) * 255, "L").filter(ImageFilter.MinFilter(5))) > 0
        keep = np.asarray(Image.fromarray(core.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(25))) > 0
        fg_small &= keep
    if keep_largest:
        # Retain the central connected fortress and discard detached crop
        # fragments from the surrounding generated ring.
        hh, ww = fg_small.shape
        seen = np.zeros_like(fg_small, dtype=bool)
        best = []
        for sy in range(hh):
            for sx in range(ww):
                if not fg_small[sy, sx] or seen[sy, sx]:
                    continue
                stack = [(sy, sx)]; seen[sy, sx] = True; component = []
                while stack:
                    yy, xx = stack.pop(); component.append((yy, xx))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if not dx and not dy:
                                continue
                            ny, nx = yy + dy, xx + dx
                            if 0 <= ny < hh and 0 <= nx < ww and fg_small[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True; stack.append((ny, nx))
                if len(component) > len(best):
                    best = component
        largest = np.zeros_like(fg_small, dtype=bool)
        for yy, xx in best:
            largest[yy, xx] = True
        fg_small = largest
    fg = np.asarray(Image.fromarray(fg_small.astype(np.uint8) * 255, "L").resize((w, h), Image.BILINEAR), dtype=np.float32) / 255.0
    # Soft alpha only at the exterior edge; interior dark mechanical panels stay.
    bg_dil = np.asarray(Image.fromarray((fg > 0.5).astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(5))) > 0
    edge = (fg > 0.05) & bg_dil
    alpha = np.clip(fg, 0.0, 1.0)
    alpha[edge] *= np.clip((diff[edge] - 18.0) / 68.0, 0.0, 1.0)
    alpha = np.asarray(Image.fromarray(np.clip(alpha * 255, 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.45)), dtype=np.float32) / 255.0
    alpha[alpha < 0.035] = 0.0
    if cut_black:
        # A cropped circular fortress can enclose a black backing pocket that
        # is not reachable from the crop border. Remove only true near-black
        # backing pixels; coloured armour and lit mechanical ribs remain.
        alpha[(diff < 42.0) | (np.max(arr, axis=2) < 42.0)] = 0.0

    # Despill the black backing at antialiased edges without flattening metal.
    a_safe = np.maximum(alpha[..., None], 0.12)
    unmixed = np.clip((arr - (1.0 - alpha[..., None]) * bg) / a_safe, 0, 255)
    rgb = np.where((alpha[..., None] < 0.98) & (alpha[..., None] > 0), unmixed, arr)
    rgb_im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
    rgb_im = ImageEnhance.Brightness(rgb_im).enhance(brightness)
    rgb_im = ImageEnhance.Color(rgb_im).enhance(saturation)
    rgb_im = ImageEnhance.Contrast(rgb_im).enhance(contrast)
    rgba = np.dstack([np.asarray(rgb_im), np.clip(alpha * 255, 0, 255).astype(np.uint8)])
    rgba[rgba[:, :, 3] == 0] = [0, 0, 0, 0]
    ys, xs = np.where(rgba[:, :, 3] > 16)
    if not len(xs):
        raise ValueError(f"No foreground extracted from {raw_path}")
    pad = 4
    x0, x1 = max(0, int(xs.min()) - pad), min(w, int(xs.max()) + pad + 1)
    y0, y1 = max(0, int(ys.min()) - pad), min(h, int(ys.max()) + pad + 1)
    cut = Image.fromarray(rgba[y0:y1, x0:x1], "RGBA")
    cw, ch = int(round(cut.width * widen)), cut.height
    factor = (canvas * fill) / max(cw, ch)
    nw, nh = max(1, round(cw * factor)), max(1, round(ch * factor))
    # Premultiplied resize prevents black halos around the extracted subject.
    ca = np.asarray(cut, dtype=np.float32)
    aa = ca[:, :, 3:4] / 255.0
    pm = np.concatenate([ca[:, :, :3] * aa, ca[:, :, 3:4]], axis=2)
    pm_im = Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8), "RGBA").resize((nw, nh), Image.LANCZOS)
    pa = np.asarray(pm_im, dtype=np.float32)
    na = pa[:, :, 3:4] / 255.0
    straight = np.where(na > 1e-3, pa[:, :, :3] / np.maximum(na, 1e-3), 0.0)
    out = np.concatenate([np.clip(straight, 0, 255), pa[:, :, 3:4]], axis=2).astype(np.uint8)
    out[out[:, :, 3] < 5] = [0, 0, 0, 0]
    master = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    master.alpha_composite(Image.fromarray(out, "RGBA"), ((canvas - nw) // 2, (canvas - nh) // 2))
    return master


def hue_shift(im: Image.Image, degrees: float, *, sat_threshold=42, val_threshold=38,
              brightness=1.0, saturation=1.0) -> Image.Image:
    """Shift only coloured alloy/glow pixels; retain neutral brushed metal."""
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    hsv = np.asarray(rgba.convert("RGB").convert("HSV"), dtype=np.uint8).copy()
    mask = (hsv[:, :, 1] >= sat_threshold) & (hsv[:, :, 2] >= val_threshold)
    hsv[:, :, 0][mask] = (hsv[:, :, 0][mask].astype(np.int16) + round(degrees / 360.0 * 255)) % 256
    rgb = Image.fromarray(hsv, "HSV").convert("RGB")
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    rgb = ImageEnhance.Color(rgb).enhance(saturation)
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def export_soften(master: Image.Image, size, *, blur=0.22, mix=0.0) -> Image.Image:
    """Scale-aware export filtering: suppress 1px sparkle, retain panel structure."""
    im = master
    if blur > 0:
        softened = im.filter(ImageFilter.GaussianBlur(blur))
        if mix > 0:
            im = Image.blend(im, softened, mix)
        else:
            im = softened
    # Reuse the branch's straight-RGBA downsampler when available.
    import pbr25d
    return pbr25d.downsample_straight_rgba(im, size)
