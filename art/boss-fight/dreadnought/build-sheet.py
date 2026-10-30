#!/usr/bin/env python3
"""Dung anh sheet tong cho Lo 1 Dreadnought.

Sheet gom:
  A. Than Dreadnought da xuat, dat o co boss 512 + ban thu nho 205px (co doc that).
  B. 11 diem hoa luc do tren canvas 512 (toa do do tu file that, khong chep tu
     bang thiet ke §3.2A).
  C. Bang trang thai 10 mon cua Lo 1: mon nao DA CO / CHUA SINH (bi chan 403).

Chay: python3 build-sheet.py
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORTS = os.path.join(HERE, "exports")
REVIEW = os.path.join(HERE, "review")

W, H = 1640, 1150
BG = (14, 16, 22)
PANEL = (22, 26, 34)
TEXT = (226, 230, 236)
DIM = (128, 138, 152)
TEAL = (64, 214, 200)
AMBER = (232, 168, 72)
RED = (214, 84, 84)


def font(sz, bold=False):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
              else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


# toa do do tu exports/01-hull-clean.png (canvas 512) — xem manifest.json
STATIONS = [
    ("ụ phụ vai T", 136, 62, "mount"),
    ("ụ phụ vai P", 372, 62, "mount"),
    ("lõi (core)", 246, 118, "core"),
    ("BigGun L", 133, 158, "mount"),
    ("BigGun R", 369, 158, "mount"),
    ("pod tên lửa T", 37, 188, "pod"),
    ("pod tên lửa P", 476, 188, "pod"),
    ("pháo quạt T", 193, 229, "mount"),
    ("pháo quạt P", 316, 229, "mount"),
    ("ụ phụ hông T", 103, 293, "mount"),
    ("ụ phụ hông P", 410, 293, "mount"),
]

ITEMS = [
    ("01", "Thân Dreadnought trần (sạch)", "CO", "512×512"),
    ("02", "Thân hư hại NHẸ", "CHUA SINH", "403"),
    ("03", "Thân hư hại VỪA", "CHUA SINH", "403"),
    ("04", "Thân hư hại NẶNG", "CHUA SINH", "403"),
    ("05", "Đầu ụ phụ (2 nòng)", "CHUA SINH", "403"),
    ("06", "Đế tĩnh ụ phụ", "CHUA SINH", "403"),
    ("07", "Đầu pháo quạt sát lõi", "CHUA SINH", "403"),
    ("08", "Đế pháo quạt", "CHUA SINH", "403"),
    ("09", "Vòng giáp lõi (MỞ)", "CHUA SINH", "403"),
    ("10", "Đế BigGun ĐÃ PHÁ", "CHUA SINH", "403"),
]


def main():
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    f_big, f_h, f_t, f_s, f_xs = font(34, True), font(26, True), font(19), font(16), font(14)

    d.text((28, 20), "BOSS-37001 DREADNOUGHT — LÔ 1 LINH KIỆN", font=f_big, fill=TEXT)
    d.text((28, 62), "Boss Book §3.2A · canvas boss 512×512 · hướng xuống · nền trong suốt",
           font=f_s, fill=DIM)

    hull = Image.open(os.path.join(EXPORTS, "01-hull-clean.png")).convert("RGBA")

    # ---- Panel A: than o co 512 + ban thu nho
    ax, ay, asz = 28, 100, 560
    d.rectangle([ax - 6, ay - 6, ax + asz + 6, ay + asz + 6], fill=PANEL)
    plate = Image.new("RGBA", hull.size, (16, 19, 26, 255))
    plate.alpha_composite(hull)
    sheet.paste(plate.convert("RGB"), (ax, ay))
    d.text((ax, ay + asz + 14), "A. 01-hull-clean · 512×512 (cỡ boss thật)",
           font=f_t, fill=TEAL)

    # thu nho: co doc that trong tran (boss hien ~205px o viewport 10,8 unit)
    small = plate.resize((205, 205), Image.LANCZOS)
    d.rectangle([ax + asz + 26, ay, ax + asz + 26 + 205 + 12, ay + 205 + 12],
                fill=(10, 12, 16))
    sheet.paste(small.convert("RGB"), (ax + asz + 32, ay + 6))
    d.text((ax + asz + 26, ay + 228), "thử 205px (cỡ đọc thật)", font=f_xs, fill=DIM)
    d.text((ax + asz + 26, ay + 250), "silhouette + 9 bệ mặt gắn đọc được", font=f_xs, fill=DIM)
    d.text((ax + asz + 26, ay + 272), "ở cỡ nhỏ nhất", font=f_xs, fill=DIM)

    # ---- Panel B: 11 diem hoa luc
    bx = ax + asz + 26
    by = ay + 310
    d.text((bx, by), "B. 11 điểm hỏa lực (đo từ file thật)", font=f_t, fill=TEXT)
    by += 30
    colors = {"mount": AMBER, "core": TEAL, "pod": (150, 170, 210)}
    o = Image.new("RGBA", hull.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(o)
    for label, x, y, kind in STATIONS:
        c = colors[kind]
        od.ellipse([x - 7, y - 7, x + 7, y + 7], outline=c + (255,), width=2)
        od.line([x - 12, y, x + 12, y], fill=c + (200,), width=1)
        od.line([x, y - 12, x, y + 12], fill=c + (200,), width=1)
    base = Image.new("RGBA", hull.size, (16, 19, 26, 255))
    base.alpha_composite(hull)
    base.alpha_composite(o)
    mini = base.resize((280, 280), Image.LANCZOS).convert("RGB")
    sheet.paste(mini, (bx + 6, by))
    lx = bx + 296
    ly = by + 4
    for label, x, y, kind in STATIONS:
        d.ellipse([lx, ly + 6, lx + 8, ly + 14], outline=colors[kind], width=2)
        d.text((lx + 14, ly), label, font=f_xs, fill=TEXT)
        d.text((lx + 168, ly), f"({x}, {y})", font=f_xs, fill=DIM)
        ly += 22

    # ---- Panel C: trang thai 10 mon
    cy = 756
    d.text((28, cy - 34), "C. Bảng kê 10 món của Lô 1", font=f_t, fill=TEXT)
    col = [28, 74, 344, 700, 830]
    for i, h in enumerate(["#", "MÓN", "TRẠNG THÁI", "CANVAS"]):
        d.text((col[i], cy), h, font=f_xs, fill=DIM)
    cy += 22
    for num, name, status, size in ITEMS:
        ok = status == "CO"
        d.text((col[0], cy), num, font=f_xs, fill=TEXT if ok else DIM)
        d.text((col[1], cy), name, font=f_xs, fill=TEXT if ok else DIM)
        d.text((col[2], cy), ("ĐÃ GIAO" if ok else "BỊ CHẶN 403 — chưa sinh"),
               font=f_xs, fill=TEAL if ok else RED)
        d.text((col[3], cy), size, font=f_xs, fill=TEXT if ok else DIM)
        cy += 24

    # right column note
    nx = 900
    d.rectangle([nx + 40, 690, W - 28, H - 28], fill=PANEL)
    d.text((nx + 60, 708), "TRẠNG THÁI LÔ 1: 1/10 — DỪNG THEO KỶ LUẬT", font=f_t, fill=RED)
    lines = [
        "Gọi sinh ảnh thứ 2 (02-hull-damage-light) trả về:",
        "",
        "403 PERMISSION_DENIED",
        "\"Request rejected due to terms of use violation. Your account has been",
        " flagged for suspicious activity. Please check the email associated",
        " with your account for more details.\"",
        "",
        "endpoint: google-genai / gemini-3.1-flash-image",
        "thời điểm: 2026-10-30 18:49 UTC",
        "",
        "⇒ DỪNG NGAY, không retry (tập 04 §4.3 mục (b)).",
        "⇒ 9 món còn lại của Lô 1 chưa sinh; chờ USER gỡ cờ tài khoản.",
    ]
    ly = 764
    for ln in lines:
        d.text((nx + 60, ly), ln, font=f_xs, fill=TEXT if ln and not ln.startswith("403") else RED)
        ly += 17

    out = os.path.join(REVIEW, "LO1-sheet.png")
    sheet.save(out)
    sheet.resize((W // 2, H // 2), Image.LANCZOS).save(
        os.path.join(REVIEW, "LO1-sheet-half.png"))
    print("written", out, sheet.size)


if __name__ == "__main__":
    main()
