"""Dựng ảnh xem trước lớp tinh vân L1 bằng CHÍNH các ảnh thật + đúng phép chiếu của game.

Chạy:  python3 docs/tools/nebula_preview.py
Ra:    docs/previews/nen-d20-chuyen-dong.jpg  (3 khung: t = 0 s · 10 s · 20 s)

Không phải ảnh render WebGL: chỉ ghép ảnh thật bằng PIL theo toạ độ/độ mờ lấy từ
prototype/src/backdrop.js, để duyệt bố cục và độ sáng. Muốn xem chuyển động thật thì mở
prototype (npm run dev).
"""
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "prototype" / "src" / "ui"
OUT = ROOT / "docs" / "previews" / "nen-d20-chuyen-dong.jpg"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"

VW, VH = 360, 780          # khung dọc 9:19,5 — gần đúng điện thoại
FOV = 46.0
ASPECT = VW / VH
TAN = math.tan(math.radians(FOV / 2))
SKY_Z = 320.0
SKY_LIGHT = 0xA0 / 255.0   # material.color #9e9e9e, làm tròn lên cho bản xem trước
NEB_K = 0.72
THEME_OPACITY = 0.85       # CHAPTERS[0].theme.fog — setTheme nhân opacity với số này
TINT = (0.66, 0.69, 0.71)  # setTheme: 0,72 · lerp(màu chương, 10 %)
TIMES = [0.0, 10.0, 20.0]

# đọc thẳng CLOUD_DEFS từ game để ảnh xem trước không bao giờ lệch code
JS = (ROOT / "prototype" / "src" / "backdrop.js").read_text(encoding="utf-8")
DEF_RE = re.compile(
    r"\{ key: '(\w+)', h: ([\d.]+), x: (-?[\d.]+), y: (-?[\d.]+), "
    r"sp: ([\d.]+), op: ([\d.]+), z: (\d+), mir: (-?\d+) \}")
FILE = {"nebulaA": "nebula_a.jpg", "nebulaB": "nebula_b.jpg", "nebulaC": "nebula_c.jpg",
        "nebulaHaze": "nebula_haze.jpg"}
NEBULA = [
    (FILE[k], float(h), float(x), float(y), float(op), float(z), int(mir), float(sp))
    for k, h, x, y, sp, op, z, mir in DEF_RE.findall(JS)
]
assert len(NEBULA) >= 3, "không đọc được CLOUD_DEFS"

view_h = lambda z: 2 * TAN * z
view_w = lambda z: view_h(z) * ASPECT


def cover(path, w, h):
    im = Image.open(path).convert("RGB")
    k = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * k)), max(h, round(im.height * k))), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def frame(t):
    sky = cover(UI / "sky_deep.jpg", VW, VH)
    canvas = np.asarray(sky, dtype=np.float32) * SKY_LIGHT

    for name, hf, xf, yf, op, z, mir, sp in NEBULA:
        tex = Image.open(UI / name).convert("RGB")
        ww = view_w(z) / VW          # 1 đơn vị thế giới = bao nhiêu pixel màn hình
        hh = view_h(z) / VH
        ph = hf * VH                 # cao bao nhiêu pixel màn hình
        pw = ph * tex.width / tex.height
        px = VW / 2 + xf * VW
        # trôi xuống rồi quấn vòng qua mép trên
        py = VH / 2 - yf * VH + (sp * VH * t) % (VH * 2.7)
        img = tex.resize((max(1, round(pw)), max(1, round(ph))), Image.LANCZOS)
        if mir < 0:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        arr = np.asarray(img, dtype=np.float32) * (op * THEME_OPACITY)
        arr = arr * np.array(TINT, dtype=np.float32)
        x0, y0 = round(px - pw / 2), round(py - ph / 2)
        x1, y1 = x0 + round(pw), y0 + round(ph)
        cx0, cy0 = max(0, x0), max(0, y0)
        cx1, cy1 = min(VW, x1), min(VH, y1)
        if cx1 > cx0 and cy1 > cy0:
            patch = arr[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
            canvas[cy0:cy1, cx0:cx1] += patch      # additive, đúng như AdditiveBlending
        _ = (ww, hh)

    # mô phỏng bloom của game (UnrealBloomPass 0,9) để ảnh xem trước không tối hơn thực tế
    base = np.clip(canvas, 0, 255).astype(np.uint8)
    hi = np.clip((canvas - 118) * 1.5, 0, 255).astype(np.uint8)
    glow = np.asarray(Image.fromarray(hi).filter(ImageFilter.GaussianBlur(11)), dtype=np.float32)
    return Image.fromarray(np.clip(base.astype(np.float32) + glow * 0.55, 0, 255).astype(np.uint8))


def font(size, bold=False):
    return ImageFont.truetype(FONT % ("-Bold" if bold else ""), size)


GAP, PAD = 18, 26
W = PAD * 2 + VW * len(TIMES) + GAP * (len(TIMES) - 1)
H = 132 + VH + PAD
board = Image.new("RGB", (W, H), (6, 10, 22))
d = ImageDraw.Draw(board)
d.text((PAD, 18), "LỚP 2 — TINH VÂN ẢNH THẬT, CÓ CHUYỂN ĐỘNG", font=font(19, True), fill=(240, 246, 255))
d.text((PAD, 44),
       "L0 Hubble Ultra Deep Field 2560² đứng yên tuyệt đối · L1 bốn đám Tarantula/Carina trôi 0,009–0,015 màn/giây",
       font=font(11), fill=(150, 175, 205))
d.text((PAD, 62),
       "cộng sáng (additive) · mép nướng vignette nên không thấy khung chữ nhật · không xoay",
       font=font(11), fill=(150, 175, 205))
d.text((PAD, 80),
       "ghép bằng PIL theo đúng toạ độ/độ mờ trong backdrop.js + mô phỏng bloom 0,9 — không phải ảnh render",
       font=font(11), fill=(118, 142, 172))

for i, t in enumerate(TIMES):
    x = PAD + i * (VW + GAP)
    y = 108
    board.paste(frame(t), (x, y))
    d.rectangle([x, y, x + VW - 1, y + VH - 1], outline=(58, 86, 126))
    d.rectangle([x, y + VH - 26, x + VW - 1, y + VH - 1], fill=(4, 8, 18))
    d.text((x + 10, y + VH - 21), f"t = {int(t)} s", font=font(12, True), fill=(255, 224, 150))
    d.text((x + VW - 96, y + VH - 21), "trôi 0,011 × t", font=font(10), fill=(140, 165, 195))

board.save(OUT, quality=88)
print(f"{OUT.relative_to(ROOT)}  {board.width}×{board.height}  {OUT.stat().st_size // 1024} KB")
