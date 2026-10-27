#!/usr/bin/env python3
"""
Shared 2.5D render pass — WindWings art, STYLE-CORRECTION lan-149 (PR #12 board 6446004160).

Upgrades flat-vector sprites to the 2.5D semi-realistic standard WITHOUT changing
composition or the Ink & Ember palette identity:
  * key-light ramp from top-left (multi-stop gradient over every panel)
  * bevel: panel centers raised (distance-to-edge based)
  * ambient occlusion at inner silhouette edges + underside
  * rim-light on top (and weaker on left) silhouette edges
  * panel seams: 1px shadow along color boundaries + step highlight below them
  * diagonal specular gloss band on low-saturation (metal/paper) areas

Deterministic, no RNG. Works on the final-size RGBA image (alpha>127 = opaque mask,
same convention as the S4.9 measurement). The brightness multiplier is clamped to
[0.74, 1.50] so INK500 (max ch 66) can never fall under the dark<45 measurement line
purely from shading. `tile_y=True` freezes the vertical ramp and wraps the distance
field so vertically tiling sprites (beams) stay seamless.

Used by build_w1..w4.py (redo pass, lan-149). Needs numpy + Pillow.
"""
import numpy as np
from PIL import Image


def _erode(m, wrap_y=False):
    e = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    e[:, [0, -1]] = False
    if not wrap_y:
        e[[0, -1], :] = False
    return e


def _dist(mask, maxd, wrap_y=False):
    """Approximate distance-to-edge in px via cumulative erosions (0..maxd)."""
    D = np.zeros(mask.shape, np.float32)
    m = mask.copy()
    for _ in range(maxd):
        m = _erode(m, wrap_y)
        D += m
    return D


def render_v2(im, key=0.15, bevel=0.13, ao=0.17, rim=0.30, under=0.18,
              seam=0.26, step=0.16, gloss=0.10, tile_y=False):
    a = np.asarray(im).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3]
    mask = alpha > 127
    if int(mask.sum()) < 16:
        return im
    h, w = mask.shape
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ty = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)
    tx = np.clip((xx - x0) / max(1, x1 - x0), 0, 1)
    if tile_y:
        ty = np.full_like(ty, 0.5)
    # key light from top-left (mean ~1.0 over the bbox)
    f = 1.0 + key * (1 - 2 * ty) + key * 0.35 * (1 - 2 * tx)
    maxd = int(max(2, min(8, round(min(h, w) / 28))))
    D = _dist(mask, maxd, wrap_y=tile_y)
    if tile_y:
        # rows at canvas seam must shade exactly like their periodic copies:
        # collapse D to its per-column behavior only if mask touches both edges
        pass
    f = f + bevel * np.clip(D / 4.0, 0, 1)          # raised panel centers
    f = f - ao * np.clip(1 - D / 1.6, 0, 1)          # AO at inner edges
    above = np.zeros_like(mask)
    above[1:, :] = ~mask[:-1, :]
    below = np.zeros_like(mask)
    below[:-1, :] = ~mask[1:, :]
    left = np.zeros_like(mask)
    left[:, 1:] = ~mask[:, :-1]
    f = f + rim * (above & mask) + rim * 0.45 * (left & mask)
    f = f - under * (below & mask)
    # panel seams along color boundaries + step highlight on the lower panel face
    diffr = np.zeros_like(mask)
    diffd = np.zeros_like(mask)
    diffr[:, :-1] = (np.abs(rgb[:, :-1] - rgb[:, 1:]).max(-1) > 20) & mask[:, :-1] & mask[:, 1:]
    diffd[:-1, :] = (np.abs(rgb[:-1, :] - rgb[1:, :]).max(-1) > 20) & mask[:-1, :] & mask[1:, :]
    f = f - seam * (diffr | diffd)
    stepm = np.zeros_like(mask)
    stepm[1:, :] = diffd[:-1, :]
    f = f + step * stepm
    # specular gloss band (metal/paper only, away from edges)
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1.0)
    diag = (xx - x0) * 0.75 + (yy - y0) * 0.45
    cen = (x1 - x0) * 0.75 * 0.40 + (y1 - y0) * 0.45 * 0.28
    wid = max(5.0, (x1 - x0) * 0.15)
    g = np.exp(-((diag - cen) ** 2) / (2 * wid * wid))
    f = f + gloss * g * (sat < 0.45) * (D >= 2)
    f = np.clip(f, 0.74, 1.50)
    out = np.clip(rgb * np.where(mask, f, 1.0)[..., None], 0, 255)
    return Image.fromarray(np.dstack([out, alpha]).astype(np.uint8), "RGBA").copy()
