"""Vẽ bảng 'xác định lớp không gian' (docs/previews/lop-khong-gian.png).

Chạy:  python3 docs/tools/layer_board.py
Cần:   Pillow + font DejaVu (có sẵn trên Linux).
Số liệu lấy đúng từ prototype/src/backdrop.js; đổi code thì đổi cả đây.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "previews" / "lop-khong-gian.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"

W, H = 1500, 1200
img = Image.new("RGB", (W, H), (8, 14, 28))
d = ImageDraw.Draw(img, "RGBA")


def F(size, bold=False):
    return ImageFont.truetype(FONT % ("-Bold" if bold else ""), size)


for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(8 + 14 * (1 - t)), int(14 + 18 * (1 - t)), int(28 + 30 * (1 - t))))

d.text((40, 26), "XÁC ĐỊNH LỚP KHÔNG GIAN", font=F(34, True), fill=(242, 248, 255))
d.text((40, 70), "tốc độ trên màn hình phải tăng dần khi tới gần — đó là thứ mắt đọc thành chiều sâu",
       font=F(17), fill=(150, 175, 205))

# (tên, z, tốc độ màn hình, mô tả, màu, giá trị để vẽ thanh)
LAYERS = [
    ("L0  VŨ TRỤ SÂU", "z −320", "≈ 0", "ẢNH THẬT Deep Field 2560² — đứng yên tuyệt đối", (42, 63, 107), 0.006),
    ("L1  TINH VÂN ★", "z −292…−308", "0,007 → 0,014", "sương + 3 đám THẬT (Tarantula/Carina) trôi", (58, 96, 150), 0.014),
    ("L2  SAO XA", "z −260", "0,006", "150 điểm, nhỏ, lạnh", (53, 80, 127), 0.006),
    ("L3  SAO GIỮA", "z −170", "0,010", "95 điểm", (61, 95, 147), 0.010),
    ("L4  SAO GẦN", "z −110", "0,016", "48 điểm, ấm", (74, 115, 168), 0.016),
    ("L5  MẢNH VỤN", "z −110…−40", "0,17 → 1,0", "thiên thạch nhỏ", (63, 143, 208), 1.0),
    ("L6  BỤI", "z −95…−20", "0,07 → 1,56", "4 tầng, càng gần càng nhanh", (63, 163, 224), 1.56),
    ("L7  LỚP GẦN ★", "z −1,7…−4,8", "2,2 → 4,1", "TRƯỚC cả tàu — che ngang tàu/đạn", (255, 183, 0), 4.1),
]

y0, rh = 112, 86
mx = math.log10(5.0)
for i, (name, z, speed, desc, col, sv) in enumerate(LAYERS):
    y = y0 + i * rh
    d.rounded_rectangle([40, y, 860, y + rh - 12], radius=8,
                        fill=(col[0], col[1], col[2], 70), outline=(col[0], col[1], col[2], 190))
    d.rounded_rectangle([40, y, 47, y + rh - 12], radius=3, fill=col)
    d.text((64, y + 12), name, font=F(21, True), fill=(240, 247, 255))
    d.text((64, y + 44), desc, font=F(15), fill=(158, 182, 212))
    zw = d.textlength(z, font=F(16))
    d.text((700 - zw, y + 14), z, font=F(16), fill=(150, 175, 205))
    tw = d.textlength(speed, font=F(15, True))
    d.text((848 - tw, y + 14), speed, font=F(15, True), fill=(255, 225, 140))
    frac = max(0.004, math.log10(max(sv, 0.001) + 1.001) / mx)
    d.rounded_rectangle([470, y + 50, 470 + frac * 110, y + 62], radius=6, fill=col)
    if i:
        d.line([(28, y + 2), (28, y + rh - 14)], fill=(110, 140, 180, 120), width=2)

# ---- ghi chú D20 (bỏ Trái Đất, lớp 2 là ảnh thật trôi) ----
ny = y0 + len(LAYERS) * rh + 26
d.text((40, ny), "GHI CHÚ D20", font=F(20, True), fill=(255, 225, 140))
lines = [
    "Bỏ hẳn Trái Đất, trạm, dầm và mọi mây vẽ tay — không vẽ lại thứ gì; vẽ không đẹp thì bỏ.",
    "L0: Hubble Ultra Deep Field 4000² → 2560², hạ sáng 0,62, đứng yên tuyệt đối.",
    "L1: sương xanh/lam + 3 đám THẬT cắt từ ảnh 4k, mép nướng vignette + cộng sáng.",
    "L1 trôi 0,007–0,014 màn/giây, tái sinh ở mép trên → không mối nối, lớp không bao giờ trống.",
]
for i, line in enumerate(lines):
    ly = ny + 40 + i * 30
    d.text((40, ly), "•", font=F(16, True), fill=(255, 225, 140))
    d.text((62, ly), line, font=F(15), fill=(226, 238, 252))

RX = 900


def thumb(path, y, w, label, sub, edge):
    im = Image.open(ROOT / path).convert("RGB")
    im = im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)
    img.paste(im, (RX, y))
    d.rectangle([RX - 2, y - 2, RX + w + 2, y + im.height + 2], outline=edge, width=2)
    d.text((RX, y + im.height + 10), label, font=F(15, True), fill=(207, 228, 255))
    if sub:
        d.text((RX, y + im.height + 30), sub, font=F(13), fill=(150, 175, 205))
    return im.height


h1 = thumb("docs/windwings-refs/v2/02-gameplay.jpg", 112, 260,
           "WindWings thật — 5 lớp đọc được", "tinh vân → Trái Đất → trạm → địch → HUD (bản gốc)", (63, 169, 255, 170))
y2 = 112 + h1 + 56
h2 = thumb("docs/nen-tham-chieu/nen-doc-craftpix.jpg", y2, 260,
           "CraftPix — nền dọc nhiều tầng", "tinh vân màu + sao + hành tinh + đá", (122, 95, 176, 170))
y3 = y2 + h2 + 56
h3 = thumb("docs/nen-tham-chieu/parallax-pixel.jpg", y3, 260,
           "Parallax pixel — tách lớp rõ nhất", "sao 3 độ sáng · tinh vân · đá trôi", (63, 163, 224, 170))

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT)
print("đã ghi", OUT, img.size, "nội dung tới y =", y3 + h3 + 30)
