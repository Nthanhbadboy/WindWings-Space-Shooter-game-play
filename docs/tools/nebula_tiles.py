"""Cắt 3 tấm tinh vân THẬT từ ảnh gốc 4k trong `image-search/` và nướng vignette.

Chạy:  python3 docs/tools/nebula_tiles.py
Ra:    prototype/src/ui/nebula_a.jpg · nebula_b.jpg · nebula_c.jpg

Vì sao phải nướng vignette: các đám mây được vẽ bằng `AdditiveBlending`, nên chỗ ảnh đen
là chỗ trong suốt. Nhân ảnh với một đường ramp mềm ở 4 cạnh → mép ảnh biến mất hoàn toàn,
không thấy khung chữ nhật, không cần shader mask lúc chạy.

Không tăng bão hoà, không vẽ thêm sao, không ghép ảnh: chỉ cắt + đổi cỡ + làm mờ mép.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "image-search"
UI = ROOT / "prototype" / "src" / "ui"

TARANTULA = SRC / "nebula-wallpaper-4k-3840x2160-real-hubbl-2.jpg"   # ESO/NASA, 3840×2160
CARINA = SRC / "hubble-deep-space-nebula-stars-real-phot-1.jpg"     # Hubble, 1279×2575
EAGLE = SRC / "nebula-wallpaper-4k-3840x2160-real-hubbl-3.jpg"      # Hubble, 3840×2160

# (file, nguồn, hộp cắt, cỡ ra, chất lượng, bán kính làm mờ) — hộp cắt tính bằng px ảnh gốc
TILES = [
    ("nebula_a.jpg", TARANTULA, (260, 0, 3180, 2160), (2560, 2016), 86, 0),
    ("nebula_b.jpg", TARANTULA, (1500, 520, 3840, 2100), (1760, 1188), 86, 0),
    ("nebula_c.jpg", CARINA, (0, 140, 1279, 2060), (1100, 1650), 86, 0),
    # lớp sương xa: tinh vân xanh/lam làm mờ mạnh → chỉ còn mảng màu, không còn chi tiết vụn.
    # Cắt bỏ 260 px đáy: ở đó có watermark "www.DesktopBackground.org" của trang tải ảnh.
    ("nebula_haze.jpg", EAGLE, (0, 0, 3840, 1900), (1920, 1080), 84, 22),
]
EDGE = 0.22        # bề rộng ramp mép, tính theo tỉ lệ cạnh
POWER = 1.45       # luỹ thừa cho ramp — càng lớn mép càng tối nhanh


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def vignette(w, h):
    u = (np.arange(w) + 0.5) / w
    v = (np.arange(h) + 0.5) / h
    rx = smoothstep(u / EDGE) * smoothstep((1 - u) / EDGE)
    ry = smoothstep(v / EDGE) * smoothstep((1 - v) / EDGE)
    return (np.outer(ry, rx) ** POWER)[..., None]


def main():
    for out, src, box, size, q, blur in TILES:
        im = Image.open(src).convert("RGB").crop(box)
        im = im.resize(size, Image.LANCZOS)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        a = np.asarray(im, dtype=np.float32) * vignette(*im.size)
        out_path = UI / out
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out_path, quality=q, optimize=True)
        print(f"{out:14s} {im.size[0]}×{im.size[1]}  {out_path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
