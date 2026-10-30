#!/usr/bin/env python3
"""Tach nen + xuat canvas dung slot cho lo linh kien Dreadnought (Boss-37001 §3.2A).

Quy trinh (tap 04 §4.3.4) — ban 2, sua 2 loi phat hien o ban 1:
  1. flood-fill tu bien (nen sinh anh = den tuyen doi 0..1) => mat na nen.
  2. alpha mem: pixel sat bien lay alpha theo do sang (ramp), phan con lai = 255.
  3. an vien sang 1px (erode) de cat vien rang cua/ringing roi moi lam mem.
  4. THU NHO TRONG KHONG GIAN PREMULTIPLIED  -> khong con quang sang (halo)
     do Lanczos ringing tren mep den/nau.
  5. kiem halo tren nen sang + nen toi, do "do sang mep" tu dong.

Chay:  python3 cutout.py            (xu ly moi file trong masters/)
"""
import json
import os
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(HERE, "masters")
EXPORTS = os.path.join(HERE, "exports")
REVIEW = os.path.join(HERE, "review")

# slot -> (rong, cao) theo contract coder (tap 04 §4.3.4)
SLOTS = {
    "01-hull-clean": (512, 512),
    "02-hull-damage-light": (512, 512),
    "03-hull-damage-medium": (512, 512),
    "04-hull-damage-heavy": (512, 512),
    "05-subturret-head": (64, 64),
    "06-subturret-base": (64, 64),
    "07-fancannon-head": (64, 64),
    "08-fancannon-base": (64, 64),
    "09-core-ring-open": (128, 128),
    "10-biggun-base-destroyed": (128, 128),
}

BG_MAX = 24        # moi kenh < BG_MAX => coi la nen khi flood-fill
EDGE_LO, EDGE_HI = 6, 46   # ramp alpha cho pixel sat nen
ERODE_PX = 1       # an vien tren master
SOFT_PX = 1.4      # lam mem mep (master px)


def bg_mask(rgb):
    """True = nen (lien thong 4-huong tu bien, mau gan den)."""
    h, w, _ = rgb.shape
    dark = rgb.max(axis=2) < BG_MAX
    seen = np.zeros((h, w), dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if dark[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if dark[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and dark[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((nx, ny))
    return seen


def build_alpha(rgb):
    h, w, _ = rgb.shape
    bg = bg_mask(rgb)
    alpha = np.where(bg, 0.0, 255.0)

    # ramp cho dai chuyen tiep: pixel KHONG phai nen nhung sat nen va toi
    bg_img = Image.fromarray((bg * 255).astype(np.uint8))
    near = np.array(bg_img.filter(ImageFilter.MaxFilter(5))) > 0   # lan 2px quanh nen
    lum = rgb.max(axis=2).astype(float)
    ramp = np.clip((lum - EDGE_LO) / (EDGE_HI - EDGE_LO), 0.0, 1.0) * 255.0
    band = near & (~bg)
    alpha = np.where(band, np.minimum(alpha, ramp), alpha)

    # an vien 1px roi lam mem
    a_img = Image.fromarray(alpha.astype(np.uint8))
    a_img = a_img.filter(ImageFilter.MinFilter(2 * ERODE_PX + 1))
    a_img = a_img.filter(ImageFilter.GaussianBlur(SOFT_PX))
    return np.array(a_img).astype(float)


def premultiplied_resize(rgb, alpha, tw, th):
    """Thu nho trong khong gian premultiplied => khong ringing tren mep."""
    h, w, _ = rgb.shape
    a = alpha / 255.0
    pre = np.dstack([rgb * a[..., None], alpha]).astype(np.float32)
    im = Image.fromarray(np.clip(pre, 0, 255).astype(np.uint8), "RGBA")
    im = im.resize((tw, th), Image.LANCZOS)
    arr = np.array(im).astype(np.float32)
    a2 = arr[..., 3:4] / 255.0
    out_rgb = np.where(a2 > 1e-4, arr[..., :3] / np.maximum(a2, 1e-4), 0)
    out = np.dstack([np.clip(out_rgb, 0, 255), arr[..., 3]])
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def fit_slot(rgb, alpha, name):
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        raise SystemExit("anh trong: " + name)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    rgb = rgb[y0:y1 + 1, x0:x1 + 1]
    alpha = alpha[y0:y1 + 1, x0:x1 + 1]
    tw, th = SLOTS[name]
    pad = 0.98
    scale = min(tw * pad / rgb.shape[1], th * pad / rgb.shape[0])
    nw, nh = max(1, round(rgb.shape[1] * scale)), max(1, round(rgb.shape[0] * scale))
    im = premultiplied_resize(rgb, alpha, nw, nh)
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    canvas.paste(im, ((tw - nw) // 2, (th - nh) // 2), im)
    return canvas


def edge_report(im):
    """Do 'quang sang': pixel vien (alpha thap) ma mau sang => halo."""
    a = np.array(im).astype(float)
    alpha, rgb = a[..., 3], a[..., :3]
    lum = rgb.max(axis=2)
    rim = (alpha > 20) & (alpha < 200)
    if rim.sum() == 0:
        return {"rim_px": 0}
    return {"rim_px": int(rim.sum()),
            "rim_lum_mean": round(float(lum[rim].mean()), 1),
            "rim_lum_p99": round(float(np.percentile(lum[rim], 99)), 1),
            "opaque_lum_mean": round(float(lum[alpha >= 250].mean()), 1) if (alpha >= 250).any() else None}


def main():
    os.makedirs(EXPORTS, exist_ok=True)
    os.makedirs(REVIEW, exist_ok=True)
    rows = []
    for f in sorted(os.listdir(MASTERS)):
        if not f.endswith(".png"):
            continue
        name = f[:-4]
        if name not in SLOTS:
            print("bo qua (khong co slot):", f)
            continue
        src = os.path.join(MASTERS, f)
        rgb = np.array(Image.open(src).convert("RGB")).astype(float)
        alpha = build_alpha(rgb)
        out = fit_slot(rgb, alpha, name)
        dst = os.path.join(EXPORTS, name + ".png")
        out.save(dst)
        rep = edge_report(out)
        bb = out.split()[-1].getbbox()
        rows.append({"master": f, "export": name + ".png",
                     "master_px": [rgb.shape[1], rgb.shape[0]],
                     "canvas_px": list(out.size), "bbox": list(bb or []),
                     "halo": rep})
        for bgname, bg in (("dark", (16, 19, 26)), ("light", (230, 232, 236))):
            plate = Image.new("RGBA", out.size, bg + (255,))
            plate.alpha_composite(out)
            big = plate.convert("RGB").resize(
                (out.width * 3 // 2, out.height * 3 // 2), Image.LANCZOS)
            big.save(os.path.join(REVIEW, f"{name}--halo-{bgname}.png"))
        print(f"{name:26s} {rgb.shape[1]}x{rgb.shape[0]} -> {out.size} bbox={bb} halo={rep}")
    with open(os.path.join(HERE, "cutout-report.json"), "w") as fh:
        json.dump(rows, fh, indent=2)


if __name__ == "__main__":
    main()
