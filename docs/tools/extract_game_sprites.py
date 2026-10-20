#!/usr/bin/env python3
"""Tách sprite tàu/địch từ ảnh generate (nền magenta/lime) → PNG trong suốt.

Chạy:  python3 docs/tools/extract_game_sprites.py
Vào:   docs/asset-samples/raw_sprite_<id>.jpg, raw_enemy_<id>.jpg, raw_boss_<id>.jpg
Ra:    prototype/src/art/game/<id>.png  (512×512, alpha, đã cắt sát + đệm)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "docs" / "asset-samples"
OUT = ROOT / "prototype" / "src" / "art" / "game"

SHIPS = ["striker", "zenith", "challenger", "spitfire",
         "insurgent", "executioner", "omen", "dispatcher"]
ENEMIES = ["wasp", "hornet"]
BOSSES = ["imperial", "pancake", "dreadnought"]

KEYS = {"magenta": np.array([255, 0, 255], np.float32),
        "green": np.array([0, 255, 0], np.float32)}


def key_out(im: Image.Image, key: str, soft=(42, 120)) -> Image.Image:
    """Xoá nền theo màu key + khử ám màu ở viền."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    # màu nền thực tế = trung bình 4 góc (model hay lệch màu)
    corners = np.stack([a[2, 2], a[2, -3], a[-3, 2], a[-3, -3]])
    k = np.median(corners, axis=0)
    if float(k.max() - k.min()) < 40:  # góc bị vật thể che / nền xám → màu chuẩn
        k = KEYS[key]
    magenta = k[0] + k[2] > 2 * k[1]  # nền hồng-tím hay xanh lá?
    d = np.sqrt(((a - k) ** 2).sum(axis=2))
    lo, hi = soft
    alpha = np.clip((d - lo) / (hi - lo), 0, 1)

    spill = alpha < 0.985
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if magenta:
        cap = g + 40
        a[..., 0] = np.where(spill, np.minimum(r, cap), r)
        a[..., 2] = np.where(spill, np.minimum(b, cap), b)
    else:
        cap = np.maximum(r, b) + 30
        a[..., 1] = np.where(spill, np.minimum(g, cap), g)

    out = Image.fromarray(np.dstack([a, alpha * 255]).astype("uint8"), "RGBA")
    out.putalpha(out.getchannel("A").filter(ImageFilter.GaussianBlur(0.7)))
    return out


def find_raw(stem: str):
    for ext in (".jpg", ".png"):
        p = SAMPLES / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def fit_square(im: Image.Image, size: int = 512, margin: float = 1.08) -> Image.Image:
    mask = im.getchannel("A").point(lambda v: 255 if v > 16 else 0)
    box = mask.getbbox()
    if box:
        im = im.crop(box)
    w, h = im.size
    side = max(1, int(max(w, h) * margin))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
    return canvas.resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    done = []
    for i, sid in enumerate(SHIPS):
        src = find_raw(f"raw_sprite_{sid}")
        if src is None:
            continue
        key = "green" if "challenger" in src.name else "magenta"
        fit_square(key_out(Image.open(src), key)).save(OUT / f"{sid}.png")
        done.append(sid)
    for eid in ENEMIES:
        src = find_raw(f"raw_enemy_{eid}")
        if src is None:
            continue
        fit_square(key_out(Image.open(src), "magenta")).save(OUT / f"enemy_{eid}.png")
        done.append("enemy_" + eid)
    for bid in BOSSES:
        src = find_raw(f"raw_boss_{bid}")
        if src is None:
            continue
        key = "green" if bid == "pancake" else "magenta"
        # boss cần nét hơn địch nhỏ → 640 px (giữ nguyên màu, không nén bảng màu)
        fit_square(key_out(Image.open(src), key), size=640).save(OUT / f"boss_{bid}.png", optimize=True)
        done.append("boss_" + bid)
    total = sum((OUT / f"{n}.png").stat().st_size for n in done) / 1024
    print("OK", len(done), "sprite →", OUT, f"({total:.0f} KB)")


if __name__ == "__main__":
    main()
