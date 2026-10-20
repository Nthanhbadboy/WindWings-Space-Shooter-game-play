"""
Sinh bộ sprite mẫu + bảng style cho giao diện WindWings 3D.

Chạy:  python3 docs/tools/make_assets.py
Kết quả:
  docs/asset-samples/ic_*.png        icon 192x192 (nền trong suốt, dùng ở @2x)
  docs/asset-samples/ship_*_cel.png  tàu 3D render -> sprite cel
  docs/asset-styleboard.png          bảng style tổng hợp
"""
from __future__ import annotations

import os
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "asset-samples"
OUT.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path.home() / ".fonts"
F700 = FONT_DIR / "barlow-condensed-700-normal.ttf"
F800 = FONT_DIR / "barlow-condensed-800-normal.ttf"
F900 = FONT_DIR / "barlow-condensed-900-normal.ttf"
FI700 = FONT_DIR / "barlow-condensed-700-italic.ttf"

# ---------------------------------------------------------------- palette
C = {
    "bg0": "#070C1C",
    "bg1": "#0A1026",
    "bg2": "#0F1B43",
    "bar": "#131838",
    "bar2": "#171733",
    "panel": "#0C2452",
    "panel2": "#0A1836",
    "edge": "#123265",
    "line": "#2B6FD0",
    "cyan": "#6FD8FF",
    "cyan2": "#A7E6FF",
    "orange": "#E49302",
    "orange_hi": "#FFC04A",
    "orange_lo": "#B46400",
    "gold": "#F7A507",
    "gold_hi": "#FFD66B",
    "coin": "#FDB507",
    "green": "#18C11E",
    "green_hi": "#6BF05E",
    "green_lo": "#0B7A10",
    "blue": "#0364CF",
    "blue_hi": "#4FA8FF",
    "blue_lo": "#02408A",
    "gem": "#0F9ACC",
    "gem_hi": "#7FE6FF",
    "gem_lo": "#075F86",
    "red": "#C81515",
    "violet": "#7A4BD0",
    "white": "#FFFFFF",
    "text": "#EAF4FF",
    "muted": "#7F93B8",
    "gray": "#5B5F60",
    "gray_hi": "#9AA0A6",
    "gray_lo": "#33383C",
}


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def vgrad(w: int, h: int, stops: list[tuple[float, str]]) -> Image.Image:
    """Gradient dọc, stops = [(0..1, hex), ...] đã sắp xếp."""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / max(1e-6, p1 - p0)
                a, b = hx(c0), hx(c1)
                col = tuple(round(a[j] + (b[j] - a[j]) * k) for j in range(3))
                d.line([(0, y), (w, y)], fill=col)
                break
        else:
            d.line([(0, y), (w, y)], fill=hx(stops[-1][1]))
    return img


def shape_mask(size: tuple[int, int], fn) -> Image.Image:
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    fn(d)
    return m


def add_glow(base: Image.Image, mask: Image.Image, color: str, radius: float, alpha: int) -> None:
    a = mask.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * alpha / 255))
    layer = Image.new("RGB", base.size, hx(color))
    base.paste(layer, (0, 0), a)


def add_glow_rgba(base: Image.Image, mask: Image.Image, color: str, radius: float, alpha: int) -> None:
    a = mask.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * alpha / 255))
    layer = Image.new("RGBA", base.size, hx(color) + (0,))
    layer.putalpha(a)
    base.alpha_composite(layer)


def paint_grad(canvas: Image.Image, mask: Image.Image, grad: Image.Image) -> None:
    canvas.paste(grad, (0, 0), mask)


def text_shadow(d: ImageDraw.ImageDraw, xy, txt, f, fill, shadow="#050A18", off=(2, 3), anchor="la"):
    d.text((xy[0] + off[0], xy[1] + off[1]), txt, font=f, fill=shadow, anchor=anchor)
    d.text(xy, txt, font=f, fill=fill, anchor=anchor)


# ---------------------------------------------------------------- icons
S = 192  # 192px = @2x của 96px
PAD = 16


def icon_star(size=S, color="#F7A507") -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size / 2, size / 2
    ro, ri = size * 0.44, size * 0.19
    import math

    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = math.radians(-90 + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    m = shape_mask((size, size), lambda d: d.polygon(pts, fill=255))
    add_glow_rgba(img, m, color, size * 0.09, 90)
    paint_grad(img, m, vgrad(size, size, [(0, "#FFE08A"), (0.35, "#FFC13A"), (0.62, color), (1, "#C25A00")]))
    d = ImageDraw.Draw(img)
    d.line(pts + [pts[0]], fill=hx("#5C2A00"), width=max(2, size // 48), joint="curve")
    hl = shape_mask((size, size), lambda dd: dd.ellipse(
        (size * 0.30, size * 0.20, size * 0.62, size * 0.46), fill=255))
    hl = ImageChops.multiply(hl, m)
    layer = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    layer.putalpha(hl.filter(ImageFilter.GaussianBlur(size * 0.02)).point(lambda v: int(v * 0.55)))
    img.alpha_composite(layer)
    return img


def icon_coin(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pad = size * 0.08
    box = (pad, pad, size - pad, size - pad)
    outer = shape_mask((size, size), lambda d: d.ellipse(box, fill=255))
    add_glow_rgba(img, outer, "#FFB300", size * 0.10, 80)
    paint_grad(img, outer, vgrad(size, size, [(0, "#FFE79A"), (0.45, "#FFC42E"), (1, "#E08A00")]))
    d = ImageDraw.Draw(img)
    inner = (pad + size * 0.10, pad + size * 0.10, size - pad - size * 0.10, size - pad - size * 0.10)
    d.ellipse(inner, fill=hx("#F2A100"))
    inner2 = (pad + size * 0.155, pad + size * 0.155, size - pad - size * 0.155, size - pad - size * 0.155)
    d.ellipse(inner2, fill=hx("#FFCB3D"))
    d.arc(box, 200, 340, fill=hx("#FFF3C4"), width=max(2, size // 40))
    d.ellipse((size * 0.33, size * 0.24, size * 0.52, size * 0.36), fill=hx("#FFF0B8"))
    d.ellipse(box, outline=hx("#7A3E00"), width=max(2, size // 44))
    return img


def icon_gem(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx = size / 2
    top = size * 0.14
    mid = size * 0.40
    bot = size * 0.88
    table = size * 0.30
    pts = [
        (cx - table, mid), (cx - size * 0.16, top), (cx + size * 0.16, top),
        (cx + table, mid), (cx, bot),
    ]
    m = shape_mask((size, size), lambda d: d.polygon(pts, fill=255))
    add_glow_rgba(img, m, "#28E0FF", size * 0.10, 85)
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=hx("#12A6D8"))
    # mặt trên sáng
    d.polygon([pts[1], pts[2], (cx + size * 0.18, mid), (cx - size * 0.18, mid)], fill=hx("#7FE6FF"))
    d.polygon([pts[0], pts[1], (cx - size * 0.18, mid)], fill=hx("#4FD2F2"))
    d.polygon([pts[2], pts[3], (cx + size * 0.18, mid)], fill=hx("#25B6E0"))
    d.polygon([(cx - size * 0.18, mid), (cx + size * 0.18, mid), (cx, bot)], fill=hx("#0C7FB0"))
    d.polygon([pts[0], (cx, bot), (cx - size * 0.18, mid)], fill=hx("#0F93C4"))
    d.polygon(pts, outline=hx("#04405C"))
    # tia sáng
    d.line([(cx - size * 0.10, size * 0.22), (cx - size * 0.02, size * 0.36)], fill=hx("#E8FCFF"), width=max(2, size // 40))
    return img


def icon_flask(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    body = (size * 0.24, size * 0.30, size * 0.76, size * 0.86)
    m = shape_mask((size, size), lambda d: d.rounded_rectangle(body, radius=size * 0.16, fill=255))
    add_glow_rgba(img, m, "#2BFF6A", size * 0.09, 70)
    paint_grad(img, m, vgrad(size, size, [(0, "#B6FFC4"), (0.35, "#3BE05C"), (1, "#0E8A28")]))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(body, radius=size * 0.16, outline=hx("#06451A"), width=max(2, size // 44))
    d.rounded_rectangle((size * 0.38, size * 0.14, size * 0.62, size * 0.34), radius=size * 0.05, fill=hx("#C9D6DF"), outline=hx("#4A5A66"), width=3)
    d.rounded_rectangle((size * 0.34, size * 0.10, size * 0.66, size * 0.18), radius=size * 0.03, fill=hx("#8E9DA8"))
    d.ellipse((size * 0.34, size * 0.46, size * 0.48, size * 0.62), fill=hx("#EAFFF0"))
    f = font(F900, int(size * 0.26))
    d.text((size * 0.50, size * 0.76), "∞", font=f, fill=hx("#EAFFF0"), anchor="mm")
    return img


def icon_gear(size=S, color="#5FD8FF") -> Image.Image:
    import math

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx = cy = size / 2
    pts = []
    teeth = 9
    for i in range(teeth * 4):
        a = math.radians(i * 360 / (teeth * 4) - 90)
        r = size * 0.44 if (i % 4) in (1, 2) else size * 0.34
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    m = shape_mask((size, size), lambda d: d.polygon(pts, fill=255))
    add_glow_rgba(img, m, color, size * 0.08, 90)
    paint_grad(img, m, vgrad(size, size, [(0, "#CFF6FF"), (0.5, color), (1, "#1E86B8")]))
    d = ImageDraw.Draw(img)
    d.polygon(pts, outline=hx("#063A55"))
    d.ellipse((cx - size * 0.15, cy - size * 0.15, cx + size * 0.15, cy + size * 0.15), fill=hx("#0A1A33"), outline=hx("#063A55"), width=3)
    d.ellipse((cx - size * 0.09, cy - size * 0.09, cx + size * 0.09, cy + size * 0.09), fill=hx(color))
    return img


def icon_lock(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = (size * 0.22, size * 0.44, size * 0.78, size * 0.88)
    m = shape_mask((size, size), lambda dd: dd.rounded_rectangle(body, radius=size * 0.07, fill=255))
    add_glow_rgba(img, m, "#6FD8FF", size * 0.07, 60)
    paint_grad(img, m, vgrad(size, size, [(0, "#CFEFFF"), (0.55, "#6FD8FF"), (1, "#2A8FC8")]))
    d.rounded_rectangle(body, radius=size * 0.07, outline=hx("#063A55"), width=max(2, size // 48))
    d.arc((size * 0.27, size * 0.12, size * 0.73, size * 0.60), 180, 360, fill=hx("#BFE9FF"), width=int(size * 0.075))
    d.arc((size * 0.27, size * 0.12, size * 0.73, size * 0.60), 180, 360, fill=hx("#063A55"), width=3)
    d.ellipse((size * 0.46, size * 0.56, size * 0.54, size * 0.68), fill=hx("#063A55"))
    return img


def icon_gift(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = (size * 0.18, size * 0.42, size * 0.82, size * 0.86)
    lid = (size * 0.13, size * 0.30, size * 0.87, size * 0.48)
    m = shape_mask((size, size), lambda dd: (
        dd.rounded_rectangle(body, radius=size * 0.05, fill=255),
        dd.rounded_rectangle(lid, radius=size * 0.05, fill=255)))
    add_glow_rgba(img, m, "#FF3B3B", size * 0.08, 70)
    paint_grad(img, m, vgrad(size, size, [(0, "#FF7A6B"), (0.45, "#E02424"), (1, "#9E0F14")]))
    d.rounded_rectangle(body, radius=size * 0.05, outline=hx("#5C0508"), width=3)
    d.rounded_rectangle(lid, radius=size * 0.05, outline=hx("#5C0508"), width=3)
    # ruy băng vàng
    d.rectangle((size * 0.45, size * 0.30, size * 0.55, size * 0.86), fill=hx("#FFC93C"))
    d.rectangle((size * 0.13, size * 0.36, size * 0.87, size * 0.42), fill=hx("#FFD75E"))
    # nơ
    d.ellipse((size * 0.28, size * 0.14, size * 0.50, size * 0.33), fill=hx("#FFD75E"), outline=hx("#8A5A00"), width=3)
    d.ellipse((size * 0.50, size * 0.14, size * 0.72, size * 0.33), fill=hx("#FFD75E"), outline=hx("#8A5A00"), width=3)
    d.ellipse((size * 0.43, size * 0.22, size * 0.57, size * 0.36), fill=hx("#FFE9A8"))
    return img


def icon_crown(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(size * 0.12, size * 0.72), (size * 0.18, size * 0.30), (size * 0.34, size * 0.50),
           (size * 0.50, size * 0.22), (size * 0.66, size * 0.50), (size * 0.82, size * 0.30),
           (size * 0.88, size * 0.72)]
    m = shape_mask((size, size), lambda dd: dd.polygon(pts, fill=255))
    add_glow_rgba(img, m, "#FFC93C", size * 0.09, 90)
    paint_grad(img, m, vgrad(size, size, [(0, "#FFEAA1"), (0.45, "#FFC12E"), (1, "#B26A00")]))
    d.polygon(pts, outline=hx("#5C3600"))
    d.rectangle((size * 0.12, size * 0.72, size * 0.88, size * 0.82), fill=hx("#D98B00"), outline=hx("#5C3600"), width=3)
    for x in (0.18, 0.50, 0.82):
        d.ellipse((size * (x - 0.05), size * 0.24, size * (x + 0.05), size * 0.34), fill=hx("#FFF2BE"), outline=hx("#5C3600"), width=2)
    d.ellipse((size * 0.44, size * 0.44, size * 0.56, size * 0.56), fill=hx("#7A4BD0"), outline=hx("#2E155C"), width=2)
    return img


def icon_skull(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = shape_mask((size, size), lambda dd: (
        dd.ellipse((size * 0.16, size * 0.14, size * 0.84, size * 0.72), fill=255),
        dd.rounded_rectangle((size * 0.32, size * 0.58, size * 0.68, size * 0.88), radius=size * 0.06, fill=255)))
    add_glow_rgba(img, m, "#BFE9FF", size * 0.07, 60)
    paint_grad(img, m, vgrad(size, size, [(0, "#FFFFFF"), (0.6, "#DCE8F2"), (1, "#9FB2C4")]))
    d.ellipse((size * 0.16, size * 0.14, size * 0.84, size * 0.72), outline=hx("#0A1026"), width=3)
    d.rounded_rectangle((size * 0.32, size * 0.58, size * 0.68, size * 0.88), radius=size * 0.06, outline=hx("#0A1026"), width=3)
    d.ellipse((size * 0.27, size * 0.34, size * 0.45, size * 0.54), fill=hx("#0A1026"))
    d.ellipse((size * 0.55, size * 0.34, size * 0.73, size * 0.54), fill=hx("#0A1026"))
    d.polygon([(size * 0.50, size * 0.54), (size * 0.56, size * 0.64), (size * 0.44, size * 0.64)], fill=hx("#0A1026"))
    for x in (0.42, 0.50, 0.58):
        d.line([(size * x, size * 0.68), (size * x, size * 0.84)], fill=hx("#7F93B8"), width=3)
    return img


def icon_shield(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(size * 0.50, size * 0.08), (size * 0.86, size * 0.22), (size * 0.80, size * 0.62),
           (size * 0.50, size * 0.92), (size * 0.20, size * 0.62), (size * 0.14, size * 0.22)]
    m = shape_mask((size, size), lambda dd: dd.polygon(pts, fill=255))
    add_glow_rgba(img, m, "#3FA0FF", size * 0.08, 80)
    paint_grad(img, m, vgrad(size, size, [(0, "#8FD0FF"), (0.5, "#2E7FE0"), (1, "#0B3F86")]))
    d.polygon(pts, outline=hx("#04203F"))
    inner = [(size * 0.50, size * 0.18), (size * 0.76, size * 0.28), (size * 0.72, size * 0.58),
             (size * 0.50, size * 0.80), (size * 0.28, size * 0.58), (size * 0.24, size * 0.28)]
    d.polygon(inner, outline=hx("#A7E6FF"), width=2)
    d.line([(size * 0.50, size * 0.24), (size * 0.50, size * 0.76)], fill=hx("#A7E6FF"), width=2)
    return img


def icon_clock(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = size * 0.10
    outer = (pad, pad, size - pad, size - pad)
    m = shape_mask((size, size), lambda dd: dd.ellipse(outer, fill=255))
    add_glow_rgba(img, m, "#FFC12E", size * 0.09, 80)
    paint_grad(img, m, vgrad(size, size, [(0, "#FFE9A8"), (0.5, "#F2B01E"), (1, "#9A5F00")]))
    d.ellipse(outer, outline=hx("#5C3600"), width=3)
    face = (pad + size * 0.10, pad + size * 0.10, size - pad - size * 0.10, size - pad - size * 0.10)
    d.ellipse(face, fill=hx("#0B2E4E"))
    d.ellipse(face, outline=hx("#6FD8FF"), width=3)
    cx = cy = size / 2
    import math
    for i in range(12):
        a = math.radians(i * 30)
        r0, r1 = size * 0.31, size * 0.35
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
                (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], fill=hx("#A7E6FF"), width=2)
    d.line([(cx, cy), (cx, cy - size * 0.22)], fill=hx("#EAF4FF"), width=5)
    d.line([(cx, cy), (cx + size * 0.15, cy + size * 0.08)], fill=hx("#EAF4FF"), width=5)
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=hx("#EAF4FF"))
    return img


def icon_pause(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = shape_mask((size, size), lambda dd: (
        dd.rounded_rectangle((size * 0.24, size * 0.18, size * 0.42, size * 0.82), radius=size * 0.05, fill=255),
        dd.rounded_rectangle((size * 0.58, size * 0.18, size * 0.76, size * 0.82), radius=size * 0.05, fill=255)))
    add_glow_rgba(img, m, "#6FD8FF", size * 0.07, 70)
    paint_grad(img, m, vgrad(size, size, [(0, "#DFF6FF"), (0.5, "#6FD8FF"), (1, "#2A8FC8")]))
    return img


def icon_plus(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = shape_mask((size, size), lambda dd: dd.ellipse((size * 0.06, size * 0.06, size * 0.94, size * 0.94), fill=255))
    add_glow_rgba(img, m, "#3BE05C", size * 0.08, 80)
    paint_grad(img, m, vgrad(size, size, [(0, "#8CFF7A"), (0.5, "#18C11E"), (1, "#0B7A10")]))
    d.ellipse((size * 0.06, size * 0.06, size * 0.94, size * 0.94), outline=hx("#0A3A0C"), width=3)
    d.rounded_rectangle((size * 0.42, size * 0.24, size * 0.58, size * 0.76), radius=size * 0.03, fill=hx("#FFFFFF"))
    d.rounded_rectangle((size * 0.24, size * 0.42, size * 0.76, size * 0.58), radius=size * 0.03, fill=hx("#FFFFFF"))
    return img


def icon_check(size=S) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(size * 0.18, size * 0.54), (size * 0.40, size * 0.76), (size * 0.84, size * 0.24)]
    d.line(pts, fill=hx("#0A3A0C"), width=int(size * 0.16), joint="curve")
    d.line(pts, fill=hx("#FFFFFF"), width=int(size * 0.10), joint="curve")
    return img


def icon_drone(size=S) -> Image.Image:
    """Drone 4 cánh: thân xanh, 4 rotor cyan, mắt camera."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    arm = hx("#0A2A12")
    for cx, cy in ((0.24, 0.28), (0.76, 0.28), (0.24, 0.72), (0.76, 0.72)):
        d.line((size * 0.5, size * 0.5, size * cx, size * cy), fill=arm, width=int(size * 0.07))
    for cx, cy in ((0.24, 0.28), (0.76, 0.28), (0.24, 0.72), (0.76, 0.72)):
        r = size * 0.14
        ring = shape_mask((size, size), lambda dd, cx=cx, cy=cy, r=r: dd.ellipse(
            (size * cx - r, size * cy - r, size * cx + r, size * cy + r), fill=255))
        add_glow_rgba(img, ring, "#6FD8FF", size * 0.03, 90)
        d.ellipse((size * cx - r, size * cy - r, size * cx + r, size * cy + r),
                  fill=hx("#123A4A"), outline=hx("#0A1A22"), width=4)
        d.ellipse((size * cx - r * 0.62, size * cy - r * 0.62, size * cx + r * 0.62, size * cy + r * 0.62),
                  fill=hx("#8FE9FF"))
        d.ellipse((size * cx - r * 0.30, size * cy - r * 0.30, size * cx + r * 0.30, size * cy + r * 0.30),
                  fill=hx("#FFFFFF"))
    body = shape_mask((size, size), lambda dd: dd.rounded_rectangle(
        (size * 0.36, size * 0.38, size * 0.64, size * 0.64), radius=size * 0.09, fill=255))
    add_glow_rgba(img, body, "#3BE05C", size * 0.05, 90)
    paint_grad(img, body, vgrad(size, size, [(0, "#8CFF7A"), (0.55, "#18C11E"), (1, "#0B6A12")]))
    d.rounded_rectangle((size * 0.36, size * 0.38, size * 0.64, size * 0.64), radius=size * 0.09,
                        outline=hx("#06350B"), width=4)
    d.ellipse((size * 0.45, size * 0.45, size * 0.55, size * 0.55), fill=hx("#0A1A22"))
    d.ellipse((size * 0.465, size * 0.465, size * 0.515, size * 0.515), fill=hx("#6FD8FF"))
    return img


def icon_pilot(size=S) -> Image.Image:
    """Phi công: mũ + kính cyan + vai."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    shoulder = shape_mask((size, size), lambda dd: dd.ellipse(
        (size * 0.12, size * 0.62, size * 0.88, size * 1.12), fill=255))
    paint_grad(img, shoulder, vgrad(size, size, [(0, "#2A69C2"), (1, "#0E2E60")]))
    d.arc((size * 0.12, size * 0.60, size * 0.88, size * 1.10), 180, 360,
          fill=hx("#8FD8FF"), width=3)
    helm = shape_mask((size, size), lambda dd: dd.ellipse(
        (size * 0.26, size * 0.16, size * 0.74, size * 0.72), fill=255))
    add_glow_rgba(img, helm, "#6FD8FF", size * 0.04, 60)
    paint_grad(img, helm, vgrad(size, size, [(0, "#FFFFFF"), (0.5, "#D7E6F5"), (1, "#8FA3B8")]))
    d.ellipse((size * 0.26, size * 0.16, size * 0.74, size * 0.72), outline=hx("#0A1740"), width=4)
    visor = shape_mask((size, size), lambda dd: dd.rounded_rectangle(
        (size * 0.31, size * 0.34, size * 0.69, size * 0.54), radius=size * 0.08, fill=255))
    add_glow_rgba(img, visor, "#6FD8FF", size * 0.03, 120)
    paint_grad(img, visor, vgrad(size, size, [(0, "#DFF8FF"), (0.45, "#6FD8FF"), (1, "#1E6FA8")]))
    d.rounded_rectangle((size * 0.31, size * 0.34, size * 0.69, size * 0.54), radius=size * 0.08,
                        outline=hx("#0A1740"), width=4)
    d.line((size * 0.36, size * 0.39, size * 0.58, size * 0.39), fill=hx("#FFFFFF"), width=4)
    d.line((size * 0.64, size * 0.20, size * 0.64, size * 0.10), fill=hx("#8FA3B8"), width=4)
    d.ellipse((size * 0.605, size * 0.06, size * 0.675, size * 0.13), fill=hx("#F79707"))
    return img


def icon_map(size=S) -> Image.Image:
    """Bản đồ gấp: 3 tấm, đường hành trình cyan, ghim đỏ."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = shape_mask((size, size), lambda dd: dd.rounded_rectangle(
        (size * 0.10, size * 0.20, size * 0.90, size * 0.82), radius=size * 0.05, fill=255))
    add_glow_rgba(img, m, "#E49302", size * 0.05, 70)
    paint_grad(img, m, vgrad(size, size, [(0, "#FFE0A0"), (0.5, "#E8B85C"), (1, "#A87428")]))
    for fx in (0.37, 0.63):
        d.line((size * fx, size * 0.21, size * fx, size * 0.81), fill=hx("#8A5A18"), width=3)
    d.rounded_rectangle((size * 0.10, size * 0.20, size * 0.90, size * 0.82), radius=size * 0.05,
                        outline=hx("#5A3A0C"), width=4)
    route = [(0.20, 0.66), (0.32, 0.50), (0.46, 0.58), (0.58, 0.40), (0.72, 0.46)]
    for i in range(len(route) - 1):
        x0, y0 = route[i]
        x1, y1 = route[i + 1]
        d.line((size * x0, size * y0, size * x1, size * y1), fill=hx("#0364CF"), width=int(size * 0.035))
    px, py = size * 0.72, size * 0.44
    d.polygon([(px, py), (px - size * 0.09, py - size * 0.11), (px + size * 0.06, py - size * 0.11)],
              fill=hx("#C81515"))
    d.ellipse((px - size * 0.11, py - size * 0.19, px + size * 0.06, py - size * 0.06), fill=hx("#FF4B4B"))
    d.ellipse((px - size * 0.07, py - size * 0.16, px - size * 0.01, py - size * 0.09), fill=hx("#FFFFFF"))
    return img


def icon_sound(size=S) -> Image.Image:
    """Loa + 2 sóng âm."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = shape_mask((size, size), lambda dd: (
        dd.polygon([(size * 0.14, size * 0.38), (size * 0.34, size * 0.38), (size * 0.56, size * 0.18),
                    (size * 0.56, size * 0.82), (size * 0.34, size * 0.62), (size * 0.14, size * 0.62)], fill=255)))
    add_glow_rgba(img, m, "#6FD8FF", size * 0.05, 70)
    paint_grad(img, m, vgrad(size, size, [(0, "#EAF9FF"), (0.5, "#6FD8FF"), (1, "#1F6F9E")]))
    d.polygon([(size * 0.14, size * 0.38), (size * 0.34, size * 0.38), (size * 0.56, size * 0.18),
               (size * 0.56, size * 0.82), (size * 0.34, size * 0.62), (size * 0.14, size * 0.62)],
              outline=hx("#063A55"))
    for i, r in enumerate((0.20, 0.32)):
        d.arc((size * (0.46 - r * 0.2), size * (0.5 - r), size * (0.46 + r * 1.3), size * (0.5 + r)),
              300, 60, fill=hx("#9BE8FF"), width=int(size * 0.07))
    return img


def icon_music(size=S) -> Image.Image:
    """Nốt nhạc đôi."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = hx("#B79BFF")
    d.rounded_rectangle((size * 0.58, size * 0.16, size * 0.66, size * 0.66), radius=size * 0.03, fill=col)
    d.rounded_rectangle((size * 0.30, size * 0.26, size * 0.66, size * 0.34), radius=size * 0.03, fill=col)
    d.rounded_rectangle((size * 0.30, size * 0.26, size * 0.38, size * 0.72), radius=size * 0.03, fill=col)
    for cx, cy in ((0.24, 0.74), (0.52, 0.66)):
        d.ellipse((size * (cx - 0.13), size * (cy - 0.10), size * (cx + 0.13), size * (cy + 0.10)),
                  fill=col, outline=hx("#2A1A55"), width=3)
        d.ellipse((size * (cx - 0.07), size * (cy - 0.06), size * (cx + 0.02), size * (cy + 0.01)),
                  fill=hx("#FFFFFF"))
    d.polygon([(size * 0.58, size * 0.16), (size * 0.66, size * 0.16), (size * 0.66, size * 0.30),
               (size * 0.58, size * 0.24)], fill=hx("#7A4BD0"))
    return img


def icon_install(size=S) -> Image.Image:
    """Tải về: mũi tên xuống + khay."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = hx("#18C11E")
    dark = hx("#063A0B")
    d.rounded_rectangle((size * 0.44, size * 0.14, size * 0.56, size * 0.54), radius=size * 0.03,
                        fill=col, outline=dark, width=3)
    d.polygon([(size * 0.30, size * 0.46), (size * 0.70, size * 0.46), (size * 0.50, size * 0.74)],
              fill=col, outline=dark, width=1)
    d.polygon([(size * 0.345, size * 0.48), (size * 0.655, size * 0.48), (size * 0.50, size * 0.70)],
              fill=hx("#6BF05E"))
    d.rounded_rectangle((size * 0.18, size * 0.76, size * 0.82, size * 0.90), radius=size * 0.05,
                        fill=hx("#7FE6FF"), outline=hx("#063A55"), width=3)
    return img


def icon_globe(size=S) -> Image.Image:
    """Quả địa cầu: biển cyan + lục địa xanh."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = shape_mask((size, size), lambda dd: dd.ellipse(
        (size * 0.10, size * 0.10, size * 0.90, size * 0.90), fill=255))
    add_glow_rgba(img, m, "#2A69C2", size * 0.05, 90)
    paint_grad(img, m, vgrad(size, size, [(0, "#BFEFFF"), (0.5, "#3FA8E0"), (1, "#0B4C80")]))
    land = shape_mask((size, size), lambda dd: (
        dd.ellipse((size * 0.20, size * 0.26, size * 0.46, size * 0.50), fill=255),
        dd.ellipse((size * 0.50, size * 0.44, size * 0.78, size * 0.66), fill=255),
        dd.ellipse((size * 0.30, size * 0.62, size * 0.48, size * 0.76), fill=255)))
    land = ImageChops.multiply(land, m)
    paint_grad(img, land, vgrad(size, size, [(0, "#8CF07A"), (1, "#18A03C")]))
    d.ellipse((size * 0.10, size * 0.10, size * 0.90, size * 0.90), outline=hx("#062A4A"), width=4)
    d.arc((size * 0.36, size * 0.10, size * 0.64, size * 0.90), 0, 360, fill=hx("#EAF9FF"), width=2)
    d.line((size * 0.10, size * 0.50, size * 0.90, size * 0.50), fill=hx("#EAF9FF"), width=2)
    d.arc((size * 0.22, size * 0.10, size * 0.78, size * 0.90), 0, 360, fill=hx("#D7F3FF"), width=2)
    return img


def icon_info(size=S) -> Image.Image:
    """Chữ i trong vòng tròn."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = shape_mask((size, size), lambda dd: dd.ellipse(
        (size * 0.08, size * 0.08, size * 0.92, size * 0.92), fill=255))
    add_glow_rgba(img, m, "#0364CF", size * 0.06, 80)
    paint_grad(img, m, vgrad(size, size, [(0, "#7FC4FF"), (0.5, "#2A69C2"), (1, "#0A2A5C")]))
    d.ellipse((size * 0.08, size * 0.08, size * 0.92, size * 0.92), outline=hx("#061A38"), width=4)
    d.ellipse((size * 0.44, size * 0.26, size * 0.56, size * 0.38), fill=hx("#FFFFFF"))
    d.rounded_rectangle((size * 0.44, size * 0.44, size * 0.56, size * 0.74), radius=size * 0.03,
                        fill=hx("#FFFFFF"))
    return img


def icon_trash(size=S) -> Image.Image:
    """Thùng rác."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    red = hx("#C81515")
    dark = hx("#3A0505")
    d.rounded_rectangle((size * 0.24, size * 0.30, size * 0.76, size * 0.86), radius=size * 0.06,
                        fill=red, outline=dark, width=4)
    d.rounded_rectangle((size * 0.34, size * 0.42, size * 0.42, size * 0.76), radius=size * 0.02, fill=hx("#FFB0A0"))
    d.rounded_rectangle((size * 0.48, size * 0.42, size * 0.56, size * 0.76), radius=size * 0.02, fill=hx("#FFB0A0"))
    d.rounded_rectangle((size * 0.16, size * 0.20, size * 0.84, size * 0.30), radius=size * 0.03,
                        fill=hx("#FF6B5E"), outline=dark, width=3)
    d.rounded_rectangle((size * 0.38, size * 0.10, size * 0.62, size * 0.22), radius=size * 0.04,
                        fill=hx("#FF6B5E"), outline=dark, width=3)
    return img


def icon_speed(size=S) -> Image.Image:
    """Hai mũi tên nhanh (fast forward)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, x0 in enumerate((0.14, 0.48)):
        pts = [(size * x0, size * 0.22), (size * (x0 + 0.34), size * 0.50), (size * x0, size * 0.78)]
        m = shape_mask((size, size), lambda dd, pts=pts: dd.polygon(pts, fill=255))
        add_glow_rgba(img, m, "#F7A507", size * 0.04, 70)
        paint_grad(img, m, vgrad(size, size, [(0, "#FFE08A"), (0.5, "#F7A507"), (1, "#A85A00")]))
        d.line(pts + [pts[0]], fill=hx("#5A2A00"), width=4, joint="curve")
    return img


def icon_cannon(size=S) -> Image.Image:
    """Đạn pháo: đầu đỏ, thân vàng, đuôi lửa."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    flame = shape_mask((size, size), lambda dd: (
        dd.polygon([(size * 0.36, size * 0.80), (size * 0.64, size * 0.80), (size * 0.50, size * 0.99)], fill=255),
        dd.polygon([(size * 0.30, size * 0.78), (size * 0.42, size * 0.78), (size * 0.36, size * 0.92)], fill=255),
        dd.polygon([(size * 0.58, size * 0.78), (size * 0.70, size * 0.78), (size * 0.64, size * 0.92)], fill=255)))
    add_glow_rgba(img, flame, "#FFB020", size * 0.06, 150)
    paint_grad(img, flame, vgrad(size, size, [(0, "#FFE08A"), (0.45, "#F79707"), (1, "#C81515")]))
    body = shape_mask((size, size), lambda dd: dd.rounded_rectangle(
        (size * 0.33, size * 0.36, size * 0.67, size * 0.80), radius=size * 0.07, fill=255))
    paint_grad(img, body, vgrad(size, size, [(0, "#FFF2C4"), (0.30, "#F7A507"), (0.75, "#B46400"), (1, "#7A3E00")]))
    d.rounded_rectangle((size * 0.33, size * 0.36, size * 0.67, size * 0.80), radius=size * 0.07,
                        outline=hx("#4A2400"), width=4)
    d.rounded_rectangle((size * 0.31, size * 0.60, size * 0.69, size * 0.70), radius=size * 0.02,
                        fill=hx("#FFD66B"), outline=hx("#4A2400"), width=3)
    tip = shape_mask((size, size), lambda dd: dd.polygon(
        [(size * 0.33, size * 0.40), (size * 0.50, size * 0.10), (size * 0.67, size * 0.40)], fill=255))
    paint_grad(img, tip, vgrad(size, size, [(0, "#FF8A7A"), (0.5, "#C81515"), (1, "#7A0505")]))
    d.polygon([(size * 0.33, size * 0.40), (size * 0.50, size * 0.10), (size * 0.67, size * 0.40)],
              outline=hx("#4A0808"), width=4)
    d.ellipse((size * 0.44, size * 0.16, size * 0.50, size * 0.26), fill=hx("#FFD9D0"))
    return img


def icon_armor(size=S) -> Image.Image:
    """Giáp ngực: vai + ức, gờ cam, lõi cyan."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = [(size * 0.24, size * 0.26), (size * 0.38, size * 0.20), (size * 0.50, size * 0.30),
            (size * 0.62, size * 0.20), (size * 0.76, size * 0.26), (size * 0.72, size * 0.74),
            (size * 0.50, size * 0.88), (size * 0.28, size * 0.74)]
    m = shape_mask((size, size), lambda dd: dd.polygon(body, fill=255))
    add_glow_rgba(img, m, "#2A69C2", size * 0.05, 110)
    paint_grad(img, m, vgrad(size, size, [(0, "#8FD8FF"), (0.42, "#2A69C2"), (1, "#0A2A5C")]))
    d.polygon(body, outline=hx("#05142C"), width=5)
    d.polygon([(size * 0.30, size * 0.62), (size * 0.50, size * 0.72), (size * 0.70, size * 0.62),
               (size * 0.66, size * 0.78), (size * 0.50, size * 0.84), (size * 0.34, size * 0.78)],
              fill=hx("#E49302"), outline=hx("#5A3200"), width=2)
    d.ellipse((size * 0.42, size * 0.40, size * 0.58, size * 0.56), fill=hx("#0B2A4A"))
    d.ellipse((size * 0.45, size * 0.43, size * 0.55, size * 0.53), fill=hx("#8FE9FF"))
    d.arc((size * 0.18, size * 0.14, size * 0.44, size * 0.40), 180, 360, fill=hx("#FFD66B"), width=5)
    d.arc((size * 0.56, size * 0.14, size * 0.82, size * 0.40), 180, 360, fill=hx("#FFD66B"), width=5)
    return img


def icon_magnet(size=S) -> Image.Image:
    """Nam châm chữ U: đỏ, hai cực bạc."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = int(size * 0.20)
    arc = shape_mask((size, size), lambda dd: dd.arc(
        (size * 0.18, size * 0.16, size * 0.82, size * 0.80), 180, 360, fill=255, width=w))
    legs = shape_mask((size, size), lambda dd: (
        dd.rectangle((size * 0.18, size * 0.48, size * 0.38, size * 0.78), fill=255),
        dd.rectangle((size * 0.62, size * 0.48, size * 0.82, size * 0.78), fill=255)))
    red = ImageChops.lighter(arc, legs)
    add_glow_rgba(img, red, "#C81515", size * 0.05, 110)
    paint_grad(img, red, vgrad(size, size, [(0, "#FF8A7A"), (0.35, "#E03030"), (1, "#8A0A0A")]))
    for x0 in (0.18, 0.62):
        d.rectangle((size * x0, size * 0.66, size * (x0 + 0.20), size * 0.78),
                    fill=hx("#DCE6F0"), outline=hx("#2A3440"), width=4)
    d.arc((size * 0.18, size * 0.16, size * 0.82, size * 0.80), 180, 360,
          fill=hx("#4A0505"), width=4)
    return img


ICONS = {
    "star": icon_star,
    "coin": icon_coin,
    "gem": icon_gem,
    "flask": icon_flask,
    "gear": icon_gear,
    "lock": icon_lock,
    "gift": icon_gift,
    "crown": icon_crown,
    "skull": icon_skull,
    "shield": icon_shield,
    "clock": icon_clock,
    "pause": icon_pause,
    "plus": icon_plus,
    "check": icon_check,
    "drone": icon_drone,
    "pilot": icon_pilot,
    "map": icon_map,
    "sound": icon_sound,
    "music": icon_music,
    "install": icon_install,
    "globe": icon_globe,
    "info": icon_info,
    "trash": icon_trash,
    "speed": icon_speed,
    "cannon": icon_cannon,
    "armor": icon_armor,
    "magnet": icon_magnet,
}


def export_icons() -> None:
    for name, fn in ICONS.items():
        im = fn()
        im.save(OUT / f"ic_{name}.png")
    print(f"icons: {len(ICONS)} -> {OUT}")


def remove_dark_bg(im: Image.Image, tol: int = 46) -> Image.Image:
    """Xoá nền tối quanh sprite (thumb render có nền đen) bằng flood fill từ 4 góc."""
    im = im.convert("RGBA")
    if im.getchannel("A").getextrema()[0] == 0:
        return im
    from PIL import ImageDraw as _D
    flood = im.convert("RGB").copy()
    mask = Image.new("L", im.size, 0)
    for xy in [(0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)]:
        try:
            _D.floodfill(flood, xy, (255, 0, 255), thresh=tol)
        except Exception:
            pass
    px = flood.load()
    mp = mask.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == (255, 0, 255):
                mp[x, y] = 255
    alpha = ImageChops.subtract(im.getchannel("A"), mask)
    im.putalpha(alpha)
    return im


# ---------------------------------------------------------------- ship sprite
def cel_sprite(src: Path, dst: Path, size: int = 420) -> Image.Image:
    """3D render -> sprite 'painted': tăng bão hoà, posterize, viền tối, rim light."""
    im = remove_dark_bg(Image.open(src))
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    im.thumbnail((size, size), Image.LANCZOS)
    rgb = im.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(1.55)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.18)
    rgb = ImageEnhance.Brightness(rgb).enhance(1.05)
    rgb = ImageOps.posterize(rgb, 4)
    alpha = im.getchannel("A")
    # viền tối
    er = alpha.filter(ImageFilter.MinFilter(5))
    edge = ImageChops.subtract(alpha, er)
    outline = Image.new("RGBA", im.size, (6, 12, 30, 0))
    outline.putalpha(edge)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    body = rgb.convert("RGBA")
    body.putalpha(alpha)
    out.alpha_composite(body)
    # rim light trên-trái
    rim = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(7)))
    from PIL import ImageDraw as _D

    grad = vgrad(im.width, im.height, [(0, "#BFEFFF"), (0.55, "#6FD8FF"), (1, "#1E6FA8")]).convert("RGBA")
    grad.putalpha(rim.point(lambda v: int(v * 0.75)))
    out.alpha_composite(grad)
    out.alpha_composite(outline)
    out.save(dst)
    return out


# ---------------------------------------------------------------- board helpers
def panel(d: ImageDraw.ImageDraw, box, radius=14, fill=("#122A58", "#0A1836"), border="#2E7FBF", bw=2, brackets=True):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=radius, fill=hx(fill[1]))
    return box


def draw_panel(canvas: Image.Image, box, radius=14, top="#142E5E", bot="#0A1836", border="#2E7FBF", glow=True, brackets=True):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    r = radius
    m = shape_mask(canvas.size, lambda dd: dd.rounded_rectangle(box, radius=r, fill=255))
    if glow:
        add_glow_rgba(canvas, m, "#2B6FD0", 18, 70)
    g = vgrad(canvas.width, canvas.height, [(0, top), (1, bot)]).convert("RGBA")
    g.putalpha(m.point(lambda v: int(v * 0.94)))
    canvas.alpha_composite(g)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(box, radius=r, outline=hx(border), width=2)
    d.line([(x0 + r, y0 + 1), (x1 - r, y0 + 1)], fill=hx("#5FA8E8"), width=1)
    if brackets:
        L = 22
        col = hx("#6FD8FF")
        for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            d.line([(cx + sx * 2, cy + sy * 2), (cx + sx * (L + 8), cy + sy * 2)], fill=col, width=3)
            d.line([(cx + sx * 2, cy + sy * 2), (cx + sx * 2, cy + sy * (L + 8))], fill=col, width=3)


def draw_button(canvas: Image.Image, box, kind="orange", label="PLAY", icon: Image.Image | None = None, font_px=40, radius=14):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    styles = {
        "orange": (("#FFCF63", "#E49302", "#B46400"), "#FFE9B0", "#5C2A00", 90),
        "green": (("#6BF05E", "#18C11E", "#0B7A10"), "#C8FFBE", "#0A3A0C", 80),
        "blue": (("#4FA8FF", "#0364CF", "#02408A"), "#B3DEFF", "#04203F", 80),
        "gray": (("#8A9096", "#5B5F60", "#33383C"), "#B9BEC2", "#1A1D20", 40),
        "violet": (("#C084FF", "#7A4BD0", "#3A1F7A"), "#E2C7FF", "#2A1352", 80),
    }
    stops, rim, dark, glow = styles[kind]
    m = shape_mask(canvas.size, lambda dd: dd.rounded_rectangle(box, radius=radius, fill=255))
    add_glow_rgba(canvas, m, stops[1], 20, glow)
    g = vgrad(canvas.width, canvas.height, [(0, stops[0]), (0.48, stops[1]), (1, stops[2])]).convert("RGBA")
    g.putalpha(m)
    canvas.alpha_composite(g)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(box, radius=radius, outline=hx(rim), width=3)
    d.rounded_rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), radius=radius - 2, outline=hx(dark), width=1)
    # vệt sáng trên
    hl = shape_mask(canvas.size, lambda dd: dd.rounded_rectangle((x0 + 8, y0 + 6, x1 - 8, y0 + h * 0.42), radius=radius - 4, fill=255))
    hl = ImageChops.multiply(hl, m)
    layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    layer.putalpha(hl.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.16)))
    canvas.alpha_composite(layer)

    f = font(F900, font_px)
    has_icon = icon is not None
    d.text  # noqa
    tw = d.textlength(label, font=f)
    iw = int(font_px * 0.95) if has_icon else 0
    total = tw + (iw + 18 if has_icon else 0)
    cx = x0 + w / 2 - total / 2
    cy = y0 + h / 2
    text_shadow(d, (cx + iw + (18 if has_icon else 0), cy), label, f, hx("#FFFFFF"),
                shadow=hx(dark), off=(2, 3), anchor="lm")
    if has_icon:
        ic = icon.resize((iw, iw), Image.LANCZOS)
        canvas.alpha_composite(ic, (int(cx), int(cy - iw / 2)))


def draw_plate(canvas: Image.Image, cx, y, w, h, text, size=24):
    """Bảng tiêu đề hình thang (CAMPAIGN / TECHNOLOGY)."""
    d = ImageDraw.Draw(canvas)
    x0, x1 = cx - w / 2, cx + w / 2
    pts = [(x0, y), (x1, y), (x1 - 26, y + h), (x0 + 26, y + h)]
    m = shape_mask(canvas.size, lambda dd: dd.polygon(pts, fill=255))
    g = vgrad(canvas.width, canvas.height, [(0, "#2A74CC"), (1, "#0E3572")]).convert("RGBA")
    g.putalpha(m)
    canvas.alpha_composite(g)
    add_glow_rgba(canvas, m, "#37B6FF", 14, 60)
    d.polygon(pts, outline=hx("#6FD8FF"))
    d.line([(x0 + 26, y + h - 1), (x1 - 26, y + h - 1)], fill=hx("#6FD8FF"), width=3)
    text_shadow(d, (cx, y + h / 2 - 1), text, font(F800, size), hx("#7FE6FF"), shadow=hx("#06254F"), off=(0, 2), anchor="mm")


def draw_node(canvas: Image.Image, cx, cy, r=52, number="7", state="normal"):
    d = ImageDraw.Draw(canvas)
    box = (cx - r, cy - r, cx + r, cy + r)
    if state == "current":
        add_glow_rgba(canvas, shape_mask(canvas.size, lambda dd: dd.ellipse(box, fill=255)), "#48D652", 22, 180)
        d.ellipse((box[0] - 8, box[1] - 8, box[2] + 8, box[3] + 8), outline=hx("#48D652"), width=8)
        d.arc((box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4), 20, 150, fill=hx("#BFFFD0"), width=4)
    # vành kim loại
    ring = shape_mask(canvas.size, lambda dd: dd.ellipse(box, fill=255))
    g = vgrad(canvas.width, canvas.height, [(0, "#8A9096"), (0.45, "#4A5056"), (1, "#15181C")]).convert("RGBA")
    g.putalpha(ring)
    add_glow_rgba(canvas, ring, "#000000", 10, 90)
    canvas.alpha_composite(g)
    d.ellipse(box, outline=hx("#05070B"), width=3)
    inner = (cx - r * 0.80, cy - r * 0.80, cx + r * 0.80, cy + r * 0.80)
    d.ellipse(inner, fill=hx("#11141A"))
    d.arc(inner, 150, 330, fill=hx("#6A737C"), width=2)
    if state == "boss":
        ic = ICONS["skull"]().resize((int(r * 1.1), int(r * 1.1)), Image.LANCZOS)
        canvas.alpha_composite(ic, (int(cx - r * 0.55), int(cy - r * 0.55)))
    else:
        text_shadow(d, (cx, cy), str(number), font(F900, int(r * 0.95)), hx("#FFFFFF"),
                    shadow=hx("#000000"), off=(2, 3), anchor="mm")


def draw_ribbon(canvas: Image.Image, box, text, reward="392", reward_icon="coin", star_on=True):
    x0, y0, x1, y1 = box
    h = y1 - y0
    pts = [(x0, y0), (x1 - 22, y0), (x1, y0 + h / 2), (x1 - 22, y1), (x0, y1)]
    m = shape_mask(canvas.size, lambda dd: dd.polygon(pts, fill=255))
    g = vgrad(canvas.width, canvas.height, [(0, "#1A4680"), (0.5, "#123C77"), (1, "#0A2450")]).convert("RGBA")
    g.putalpha(m.point(lambda v: int(v * 0.92)))
    canvas.alpha_composite(g)
    d = ImageDraw.Draw(canvas)
    d.line(pts + [pts[0]], fill=hx("#2B6FD0"), width=1, joint="curve")
    # ô sao
    tile = (x0 + 8, y0 + 6, x0 + 8 + h - 12, y1 - 6)
    d.rounded_rectangle(tile, radius=6, fill=hx("#1B4C92"), outline=hx("#5FA8E8"))
    ic = ICONS["star" if star_on else "star"]().resize((int(h * 0.62), int(h * 0.62)), Image.LANCZOS)
    if not star_on:
        ic = ImageOps.grayscale(ic.convert("RGB")).convert("RGBA")
        ic.putalpha(ic.getchannel("A").point(lambda v: int(v * 0.55)))
    canvas.alpha_composite(ic, (int(tile[0] + (tile[2] - tile[0] - ic.width) / 2), int(y0 + (h - ic.height) / 2)))
    text_shadow(d, (tile[2] + 18, y0 + h / 2), text, font(F700, int(h * 0.40)), hx("#A7E6FF"),
                shadow=hx("#04122B"), off=(1, 2), anchor="lm")
    ric = ICONS[reward_icon]().resize((int(h * 0.52), int(h * 0.52)), Image.LANCZOS)
    canvas.alpha_composite(ric, (int(x1 - 30 - ric.width), int(y0 + (h - ric.height) / 2)))
    text_shadow(d, (x1 - 40 - ric.width, y0 + h / 2), reward, font(F800, int(h * 0.42)), hx("#FFFFFF"),
                shadow=hx("#04122B"), off=(1, 2), anchor="rm")


def draw_exp(canvas: Image.Image, box, pct=0.62):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(box, radius=(y1 - y0) // 2, fill=hx("#04101F"), outline=hx("#0A1026"), width=2)
    w = (x1 - x0 - 6) * pct
    inner = (x0 + 3, y0 + 3, x0 + 3 + w, y1 - 3)
    m = shape_mask(canvas.size, lambda dd: dd.rounded_rectangle(inner, radius=(y1 - y0) // 2 - 2, fill=255))
    g = vgrad(canvas.width, canvas.height, [(0, "#8CFF7A"), (0.45, "#3BE03C"), (1, "#17A81B")]).convert("RGBA")
    g.putalpha(m)
    canvas.alpha_composite(g)
    d.rounded_rectangle(inner, radius=(y1 - y0) // 2 - 2, outline=hx("#B8FFAE"), width=1)


def draw_hex(canvas: Image.Image, cx, cy, r, fill=("#2E7FE0", "#0B2E5E"), border="#6FD8FF", img=None):
    import math

    pts = [(cx + r * math.cos(math.radians(-90 + i * 60)), cy + r * math.sin(math.radians(-90 + i * 60))) for i in range(6)]
    m = shape_mask(canvas.size, lambda dd: dd.polygon(pts, fill=255))
    g = vgrad(canvas.width, canvas.height, [(0, fill[0]), (1, fill[1])]).convert("RGBA")
    g.putalpha(m)
    canvas.alpha_composite(g)
    d = ImageDraw.Draw(canvas)
    d.polygon(pts, outline=hx(border), width=3)
    if img is not None:
        clip = Image.new("L", canvas.size, 0)
        ImageDraw.Draw(clip).polygon(pts, fill=255)
        im2 = img.resize((int(r * 1.5), int(r * 1.5)), Image.LANCZOS)
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), clip))
        canvas.alpha_composite(layer)


def draw_card(canvas: Image.Image, box, icon_img, qty="x10", radius=10):
    x0, y0, x1, y1 = box
    m = shape_mask(canvas.size, lambda dd: dd.rounded_rectangle(box, radius=radius, fill=255))
    add_glow_rgba(canvas, m, "#9A5CFF", 10, 60)
    g = vgrad(canvas.width, canvas.height, [(0, "#8A4AD8"), (1, "#3A1F7A")]).convert("RGBA")
    g.putalpha(m)
    canvas.alpha_composite(g)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(box, radius=radius, outline=hx("#C9A0FF"), width=2)
    ic = icon_img.resize((int((x1 - x0) * 0.66), int((x1 - x0) * 0.66)), Image.LANCZOS)
    canvas.alpha_composite(ic, (int(x0 + (x1 - x0 - ic.width) / 2), int(y0 + (y1 - y0 - ic.height) / 2 - 6)))
    text_shadow(d, (x1 - 8, y1 - 6), qty, font(F800, 20), hx("#FFFFFF"), shadow=hx("#2A1352"), off=(1, 2), anchor="rs")


# ---------------------------------------------------------------- board

# ---------------------------------------------------------------- backgrounds
def _stars(layer: Image.Image, n: int, seed: int, alpha=(90, 255)):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        x, y = rnd.randrange(layer.width), rnd.randrange(layer.height)
        a = rnd.randint(*alpha)
        s = rnd.choice([1, 1, 1, 2, 2, 3])
        d.ellipse((x, y, x + s, y + s), fill=(255, 255, 255, a))
    for _ in range(6):
        x, y = rnd.randrange(layer.width), rnd.randrange(layer.height)
        r = rnd.randint(3, 6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(190, 235, 255, 140))
        d.line((x - r * 4, y, x + r * 4, y), fill=(190, 235, 255, 60))
        d.line((x, y - r * 4, x, y + r * 4), fill=(190, 235, 255, 60))


def plate_nebula(w: int, h: int, seed: int = 7) -> Image.Image:
    base = vgrad(w, h, [(0, "#050B1E"), (0.45, "#0A1A46"), (1, "#040814")]).convert("RGBA")
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    palette = ["#2158FF", "#6A2FE0", "#D040E8", "#12A6E8", "#2F7BFF"]
    for _ in range(9):
        cx, cy = rnd.uniform(0.12, 0.92) * w, rnd.uniform(0.10, 0.88) * h
        rx, ry = rnd.uniform(0.20, 0.50) * w, rnd.uniform(0.10, 0.30) * h
        ld.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=hx(rnd.choice(palette)) + (105,))
    # dải tinh vân chéo
    ld.polygon([(w * 0.30, h * 0.70), (w * 0.62, h * 0.42), (w * 0.86, h * 0.50), (w * 0.52, h * 0.80)],
               fill=hx("#FF4FD0") + (60,))
    layer = layer.filter(ImageFilter.GaussianBlur(w * 0.045))
    base.alpha_composite(layer)
    # lõi sáng
    core = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse((w * 0.10, h * 0.26, w * 0.66, h * 0.78), fill=(120, 210, 255, 90))
    base.alpha_composite(core.filter(ImageFilter.GaussianBlur(w * 0.055)))
    # hành tinh
    r = min(w, h) * 0.34
    cx, cy = w * 0.16, h * 0.60
    pm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(pm).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    pg = vgrad(w, h, [(0, "#E8FBFF"), (0.28, "#7FD8FF"), (0.62, "#1E6FD0"), (1, "#08204A")]).convert("RGBA")
    pg.putalpha(pm)
    # bóng tối nửa phải
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((cx - r * 0.2, cy - r, cx + r, cy + r), fill=(2, 6, 18, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(r * 0.18))
    pmask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(pmask).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    shadow.putalpha(ImageChops.multiply(shadow.getchannel("A"), pmask))
    base.alpha_composite(pg)
    base.alpha_composite(shadow)
    # vân mây
    clouds = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for _ in range(9):
        bx = rnd.uniform(cx - r * 0.8, cx + r * 0.5)
        by = rnd.uniform(cy - r * 0.7, cy + r * 0.7)
        bw, bh = rnd.uniform(r * 0.2, r * 0.6), rnd.uniform(r * 0.04, r * 0.12)
        cd.ellipse((bx - bw, by - bh, bx + bw, by + bh), fill=(255, 255, 255, 38))
    clouds.putalpha(ImageChops.multiply(clouds.getchannel("A"), pmask))
    base.alpha_composite(clouds.filter(ImageFilter.GaussianBlur(r * 0.03)))
    # khí quyển
    atm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(atm).ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), outline=255, width=10)
    base.alpha_composite(Image.merge("RGBA", (*[atm.point(lambda v: int(v * 0.55))] * 3, atm.point(lambda v: int(v * 0.55)))))
    _stars(base, int(w * h / 2400), seed + 3)
    return base


def plate_hangar(w: int, h: int) -> Image.Image:
    base = vgrad(w, h, [(0, "#0A1430"), (0.5, "#0C1B3E"), (1, "#060C1E")]).convert("RGBA")
    # quầng sáng ấm giữa dưới
    warm = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(warm).ellipse((w * 0.14, h * 0.36, w * 0.86, h * 1.10), fill=(255, 150, 40, 165))
    base.alpha_composite(warm.filter(ImageFilter.GaussianBlur(w * 0.05)))
    d = ImageDraw.Draw(base)
    # sàn lục giác
    pts = [(w * 0.5, h * 0.52), (w * 0.82, h * 0.68), (w * 0.82, h * 0.98), (w * 0.5, h * 1.12),
           (w * 0.18, h * 0.98), (w * 0.18, h * 0.68)]
    m = shape_mask((w, h), lambda dd: dd.polygon(pts, fill=255))
    g = vgrad(w, h, [(0, "#7A4A18"), (1, "#2A1706")]).convert("RGBA")
    g.putalpha(m.point(lambda v: int(v * 0.75)))
    base.alpha_composite(g)
    d.polygon(pts, outline=hx("#E49302"), width=3)
    # hai vòng docking
    for cx in (w * 0.27, w * 0.73):
        r = w * 0.17
        cy = h * 0.40
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=hx("#3A4450"), width=14)
        d.ellipse((cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7), outline=hx("#8A9096"), width=2)
        for a0 in (20, 110, 200, 290):
            d.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 34, fill=hx("#E49302"), width=6)
        d.ellipse((cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82), fill=hx("#0A1120"))
        d.ellipse((cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82), outline=hx("#1E2A3A"), width=2)
    # vạch hazard hai bên sàn
    for side in (-1, 1):
        x0 = w * (0.5 + side * 0.30)
        for i in range(5):
            d.polygon([(x0 - 14, h * 0.80 + i * 16), (x0 + 10, h * 0.80 + i * 16),
                       (x0 + 24, h * 0.80 + i * 16 + 8), (x0, h * 0.80 + i * 16 + 8)], fill=hx("#E49302"))
    # trụ trung tâm + đèn cyan
    d.rounded_rectangle((w * 0.46, h * 0.46, w * 0.54, h * 0.94), radius=6, fill=hx("#2A1706"), outline=hx("#B46400"), width=2)
    d.line((w * 0.50 - 10, h * 0.50, w * 0.50 - 10, h * 0.90), fill=hx("#6FD8FF"), width=3)
    d.line((w * 0.50 + 10, h * 0.50, w * 0.50 + 10, h * 0.90), fill=hx("#6FD8FF"), width=3)
    # vignette
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse((-w * 0.25, -h * 0.25, w * 1.25, h * 1.25), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(w * 0.04))
    dark = Image.new("RGBA", (w, h), (3, 6, 14, 210))
    dark.putalpha(ImageChops.invert(vig).point(lambda v: int(v * 0.55)))
    base.alpha_composite(dark)
    return base


def ring_porthole(size: int = 512) -> Image.Image:
    """Vòng cửa sổ khoang tàu: vành kim loại có khấc, điểm vàng, lòng tối."""
    import math as _m
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    r_out = size * 0.485
    r_in = size * 0.375
    # nền trong (lòng khoang)
    disc = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse((c - r_in, c - r_in, c + r_in, c + r_in), fill=(9, 20, 40, 255))
    inner = vgrad(size, size, [(0, "#12395E"), (0.55, "#0A1A33"), (1, "#050C1A")]).convert("RGBA")
    img.alpha_composite(Image.composite(inner, Image.new("RGBA", (size, size), (0, 0, 0, 0)),
                                       Image.new("L", (size, size), 0)))
    m_in = shape_mask((size, size), lambda x: x.ellipse((c - r_in, c - r_in, c + r_in, c + r_in), fill=255))
    paint_grad(img, m_in, inner)
    # quầng sáng lòng khoang
    add_glow_rgba(img, m_in, "#2A7FC8", size * 0.02, 90)
    # vành kim loại
    band = shape_mask((size, size), lambda x: x.ellipse((c - r_out, c - r_out, c + r_out, c + r_out), fill=255))
    hole = shape_mask((size, size), lambda x: x.ellipse((c - r_in, c - r_in, c + r_in, c + r_in), fill=255))
    ring = ImageChops.subtract(band, hole)
    metal = vgrad(size, size, [(0, "#9AA2A8"), (0.35, "#6E767D"), (0.62, "#454C52"), (1, "#23282C")]).convert("RGBA")
    paint_grad(img, ring, metal)
    # khấc chia đoạn
    for i in range(48):
        a = _m.radians(i * 7.5)
        x0, y0 = c + _m.cos(a) * (r_in + 3), c + _m.sin(a) * (r_in + 3)
        x1, y1 = c + _m.cos(a) * (r_out - 3), c + _m.sin(a) * (r_out - 3)
        d.line((x0, y0, x1, y1), fill=hx("#232A30") + (150,), width=2)
    # 4 mảng vàng
    for a0, a1 in ((18, 46), (108, 136), (198, 226), (288, 316)):
        gold = shape_mask((size, size), lambda x, a0=a0, a1=a1: x.pieslice(
            (c - r_out, c - r_out, c + r_out, c + r_out), a0, a1, fill=255))
        gold = ImageChops.multiply(gold, ring)
        paint_grad(img, gold, vgrad(size, size, [(0, "#FFD66B"), (0.5, "#E49302"), (1, "#9A5A00")]).convert("RGBA"))
    # viền trong/ngoài + highlight
    d.ellipse((c - r_out, c - r_out, c + r_out, c + r_out), outline=hx("#0B1116") + (255,), width=max(3, size // 110))
    d.ellipse((c - r_in - 2, c - r_in - 2, c + r_in + 2, c + r_in + 2), outline=hx("#B7C0C7") + (170,), width=max(2, size // 200))
    hl = shape_mask((size, size), lambda x: x.arc(
        (c - r_out + 6, c - r_out + 6, c + r_out - 6, c + r_out - 6), 186, 300, fill=255, width=int(size * 0.02)))
    white = Image.new("RGBA", (size, size), (240, 250, 255, 0))
    white.putalpha(hl.point(lambda v: int(v * 0.55)))
    img.alpha_composite(white)
    # bóng trong lòng
    sh = shape_mask((size, size), lambda x: x.arc(
        (c - r_in + 8, c - r_in + 8, c + r_in - 8, c + r_in - 8), 20, 160, fill=255, width=int(size * 0.03)))
    dark = Image.new("RGBA", (size, size), (3, 7, 16, 0))
    dark.putalpha(sh.point(lambda v: int(v * 0.55)))
    img.alpha_composite(dark)
    return img


def build_board() -> Image.Image:
    W, H = 1600, 2940
    SS = 2
    canvas = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 255))
    # nền
    bg = vgrad(W * SS, H * SS, [(0, "#0B1228"), (0.45, "#0A1026"), (1, "#070B18")]).convert("RGBA")
    canvas.alpha_composite(bg)
    # quầng sáng sau tiêu đề
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-W * SS * 0.2, -H * SS * 0.25, W * SS * 1.2, H * SS * 0.35), fill=hx("#1E3F86") + (120,))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    canvas = canvas.resize((W, H), Image.LANCZOS)

    d = ImageDraw.Draw(canvas)
    M = 64

    # header
    text_shadow(d, (M, 56), "WINDWINGS 3D", font(F900, 54), hx("#FFFFFF"), off=(3, 4))
    text_shadow(d, (M, 122), "ASSET BLUEPRINT  ·  UI & SPRITE SPEC v1", font(F700, 24), hx("#7FE6FF"), off=(2, 3))
    text_shadow(d, (W - M, 70), "tham chiếu: 9 ảnh WindWings 720×1496", font(F700, 18), hx("#7F93B8"), off=(0, 0), anchor="ra")
    text_shadow(d, (W - M, 96), "font: Barlow Condensed (OFL)", font(F700, 18), hx("#7F93B8"), off=(0, 0), anchor="ra")
    d.line([(M, 164), (W - M, 164)], fill=hx("#1E3F86"), width=2)

    # ---------------- 01 palette
    text_shadow(d, (M, 186), "01 · BẢNG MÀU", font(F900, 20), hx("#6FD8FF"), off=(1, 2))
    chrome = [("#0A1026", "NỀN SÂU"), ("#0F1B43", "NỀN"), ("#131838", "THANH TRÊN"), ("#0C2452", "PANEL"), ("#123265", "EDGE"), ("#2B6FD0", "VIỀN")]
    accents = [("#E49302", "CAM CTA"), ("#F7A507", "SAO"), ("#FDB507", "XU"), ("#18C11E", "XANH MUA"), ("#0364CF", "XANH PHỤ"), ("#0F9ACC", "GEM"), ("#C81515", "ĐỎ"), ("#7A4BD0", "TÍM"), ("#6FD8FF", "CYAN")]
    x = M
    for c, name in chrome:
        d.rounded_rectangle((x, 224, x + 150, 300), radius=8, fill=hx(c), outline=hx("#243A66"))
        text_shadow(d, (x, 310), name, font(F800, 13), hx("#8FA8CC"), off=(0, 0))
        text_shadow(d, (x, 328), c, font(F800, 15), hx("#EAF4FF"), off=(0, 0))
        x += 162
    x = M
    for c, name in accents:
        d.rounded_rectangle((x, 366, x + 150, 442), radius=8, fill=hx(c), outline=hx("#243A66"))
        text_shadow(d, (x, 452), name, font(F800, 13), hx("#8FA8CC"), off=(0, 0))
        text_shadow(d, (x, 470), c, font(F800, 15), hx("#EAF4FF"), off=(0, 0))
        x += 162

    # ---------------- 02 typography
    text_shadow(d, (M, 512), "02 · KIỂU CHỮ", font(F900, 20), hx("#6FD8FF"), off=(1, 2))
    text_shadow(d, (M, 548), "PLAY", font(F900, 86), hx("#FFFFFF"), off=(4, 6))
    text_shadow(d, (M + 260, 570), "99.999.999", font(FI700, 52), hx("#FFFFFF"), off=(3, 4))
    text_shadow(d, (M + 620, 578), "STAGE 3", font(F800, 40), hx("#FFFFFF"), off=(2, 3))
    text_shadow(d, (M + 790, 578), "[NORMAL]", font(F800, 40), hx("#FAC31D"), off=(2, 3))
    text_shadow(d, (M, 660), "Eliminate 47 enemies", font(F700, 28), hx("#A7E6FF"), off=(2, 3))
    text_shadow(d, (M + 420, 660), "Day 1/2", font(F800, 28), hx("#FAC31D"), off=(2, 3))
    text_shadow(d, (M + 560, 666), "LOGIN FOR 2 DAYS", font(F800, 24), hx("#A7E6FF"), off=(1, 2))
    text_shadow(d, (M + 860, 666), "LVL. 3/30", font(F800, 28), hx("#FFFFFF"), off=(2, 3))
    text_shadow(d, (M, 712), "Barlow Condensed 700/800/900 · số dùng italic · chữ mô tả màu cyan nhạt, nhấn mạnh màu hổ phách",
                font(F700, 17), hx("#7F93B8"), off=(0, 0))

    # ---------------- 03 buttons
    text_shadow(d, (M, 762), "03 · NÚT", font(F900, 20), hx("#6FD8FF"), off=(1, 2))
    bw, bh, gap = 340, 96, 32
    bx = [M, M + bw + gap, M + (bw + gap) * 2, M + (bw + gap) * 3 - 20]
    draw_button(canvas, (bx[0], 800, bx[0] + bw, 800 + bh), "orange", "PLAY", None, 44, 16)
    draw_button(canvas, (bx[1], 812, bx[1] + bw, 812 + bh - 14), "green", "+1 lvl", ICONS["coin"](), 30, 14)
    draw_button(canvas, (bx[2], 812, bx[2] + bw, 812 + bh - 14), "blue", "+1 lvl", ICONS["gem"](), 30, 14)
    draw_button(canvas, (bx[3], 812, bx[3] + bw, 812 + bh - 14), "gray", "NOT REACHED", None, 24, 14)
    caps = [("CTA chính · cam", bx[0]), ("mua bằng xu · xanh lá", bx[1]), ("mua bằng gem · xanh dương", bx[2]), ("khoá / chưa tới · xám", bx[3])]
    for cap, cx in caps:
        text_shadow(d, (cx, 928), cap, font(F700, 15), hx("#7F93B8"), off=(0, 0))

    # ---------------- 04 components
    text_shadow(d, (M, 972), "04 · KHUNG & LINH KIỆN", font(F900, 20), hx("#6FD8FF"), off=(1, 2))
    draw_panel(canvas, (M, 1008, M + 720, 1368))
    draw_plate(canvas, M + 360, 1008, 300, 52, "CAMPAIGN", 26)
    draw_ribbon(canvas, (M + 24, 1080, M + 696, 1144), "Eliminate 47 enemies", "392", "coin", True)
    draw_ribbon(canvas, (M + 24, 1152, M + 696, 1216), "Eliminate 107 enemies", "672", "coin", False)
    draw_ribbon(canvas, (M + 24, 1224, M + 696, 1288), "Eliminate 190 enemies", "10", "gem", False)
    draw_exp(canvas, (M + 24, 1310, M + 696, 1348), 0.62)
    text_shadow(d, (M + 34, 1329), "EXP   2.510 / 4.200", font(F800, 20), hx("#FFFFFF"), off=(1, 2), anchor="lm")

    # right: badges + node + card
    draw_hex(canvas, 880, 1090, 78, ("#2E7FE0", "#0B2E5E"), "#6FD8FF")
    ic = ICONS["star"]().resize((120, 120), Image.LANCZOS)
    canvas.alpha_composite(ic, (820, 1030))
    text_shadow(d, (880, 1184), "STAR · hex badge", font(F700, 15), hx("#7F93B8"), off=(0, 0), anchor="ma")

    draw_node(canvas, 1080, 1090, 58, "7", "normal")
    draw_node(canvas, 1260, 1090, 58, "3", "current")
    draw_node(canvas, 1440, 1090, 58, "", "boss")
    text_shadow(d, (1080, 1166), "thường", font(F700, 15), hx("#7F93B8"), off=(0, 0), anchor="ma")
    text_shadow(d, (1260, 1166), "hiện tại", font(F700, 15), hx("#7F93B8"), off=(0, 0), anchor="ma")
    text_shadow(d, (1440, 1166), "boss", font(F700, 15), hx("#7F93B8"), off=(0, 0), anchor="ma")

    draw_card(canvas, (850, 1210, 966, 1326), ICONS["gem"](), "x10")
    draw_card(canvas, (986, 1210, 1102, 1326), ICONS["gift"](), "x1")
    text_shadow(d, (850, 1340), "item card · nền tím, số lượng góc phải", font(F700, 15), hx("#7F93B8"), off=(0, 0))
    draw_button(canvas, (1150, 1224, 1360, 1312), "blue", "COLLECT", None, 26, 12)
    draw_button(canvas, (1380, 1224, 1560, 1312), "violet", "COLLECT", None, 22, 12)
    text_shadow(d, (1150, 1340), "nút nhận · xanh / tím premium", font(F700, 15), hx("#7F93B8"), off=(0, 0))

    # ---------------- 05 icons
    text_shadow(d, (M, 1404), "05 · ICON SET  (PNG 192×192, nền trong suốt)", font(F900, 20), hx("#6FD8FF"), off=(1, 2))
    order = ["star", "coin", "gem", "flask", "gear", "lock", "gift", "crown",
             "skull", "shield", "clock", "pause", "plus", "check", "drone", "pilot",
             "map", "sound", "music", "install", "globe", "info", "trash", "speed",
             "cannon", "armor", "magnet"]
    per_row = 12
    for i, name in enumerate(order):
        row, col = divmod(i, per_row)
        cx = M + 58 + col * 124
        cy = 1470 + row * 140
        ic = ICONS[name]().resize((76, 76), Image.LANCZOS)
        canvas.alpha_composite(ic, (cx - 38, cy - 50))
        text_shadow(d, (cx, cy + 36), name, font(F700, 15), hx("#7F93B8"), off=(0, 0), anchor="ma")

    # ---------------- 06 ship sprites
    text_shadow(d, (M, 1806), "06 · SPRITE TÀU (8 tàu, vẽ tay — không render 3D)", font(F900, 20), hx("#6FD8FF"), off=(1, 2))
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ship_sprites as SS

    names = list(SS.SHIPS)
    bw, bh = 168, 168
    for i, nm in enumerate(names):
        row, col = divmod(i, 4)
        cx = M + 84 + col * (bw + 22)
        cy = 1936 + row * (bh + 56)
        spr = SS.render_ship(nm, 156)
        canvas.alpha_composite(spr, (cx - 78, cy - 84))
        text_shadow(d, (cx, cy + 84), nm, font(F700, 15), hx("#7F93B8"), off=(0, 0), anchor="ma")
        sp = OUT / f"ship_{nm}.png"
        SS.render_ship(nm, 512).save(sp)

    # hero + ghi chú kỹ thuật
    hero = SS.render_ship("striker", 300)
    canvas.alpha_composite(hero, (M + 830, 1848))
    text_shadow(d, (M + 830, 2168), "sprite 512×512, mũi hướng lên, nền trong suốt", font(F700, 15), hx("#7F93B8"), off=(0, 0))
    notes = [
        "Cùng một bộ dựng: đa giác thân/cánh » gradient 2 chiều + facet sáng–tối,",
        "specular dọc thân, panel line, buồng lái phát sáng, ống xả + lửa 2 lớp,",
        "viền tối 5px, rim light góc trên–trái, bóng đổ mềm.",
        "",
        "Màu: mỗi tàu 1 base + light + dark + accent + canopy + flame (bảng 01).",
        "Không dùng bevel hay đổ bóng dày — khối nằm ở mảng màu, viền và ánh sáng.",
        "File: docs/asset-samples/ship_<tên>.png · hàm: docs/tools/ship_sprites.py",
    ]
    for i, line in enumerate(notes):
        text_shadow(d, (M + 830, 2210 + i * 26), line, font(F700, 16), hx("#8FA8CC"), off=(0, 0))

    # ---------------- 07 backgrounds
    text_shadow(d, (M, 2440), "07 · NỀN VẼ (không phải gradient CSS)", font(F900, 20), hx("#6FD8FF"), off=(1, 2))
    b1 = plate_hangar(720, 330)
    canvas.alpha_composite(b1, (M, 2480))
    b2 = plate_nebula(700, 330, 11)
    canvas.alpha_composite(b2, (M + 760, 2480))
    text_shadow(d, (M, 2828), "khoang tàu: quầng ấm + vòng docking + sàn lục giác", font(F700, 15), hx("#7F93B8"), off=(0, 0))
    text_shadow(d, (M + 760, 2828), "bản đồ: tinh vân + hành tinh + sao (sinh bằng script, seed cố định)", font(F700, 15), hx("#7F93B8"), off=(0, 0))

    # footer
    d.line([(M, 2860), (W - M, 2860)], fill=hx("#1E3F86"), width=2)
    text_shadow(d, (M, 2880), "Quy ước: chrome tối gần phẳng · viền 1–2px phát sáng · accent rực chỉ dùng cho hành động/giá trị quan trọng · sprite bóng (glossy) thay cho emoji",
                font(F700, 15), hx("#8FA8CC"), off=(0, 0))
    text_shadow(d, (M, 2906), "Không dùng bevel/đổ bóng dày kiểu “giả 3D”. Nền là tranh vẽ (tinh vân, hành tinh, khoang tàu), không phải gradient CSS.",
                font(F700, 15), hx("#8FA8CC"), off=(0, 0))
    text_shadow(d, (W - M, 2880), "docs/windwings-ui-spec.md", font(F800, 17), hx("#6FD8FF"), off=(0, 0), anchor="ra")
    text_shadow(d, (W - M, 2906), "docs/windwings-refs/*.jpg", font(F800, 17), hx("#6FD8FF"), off=(0, 0), anchor="ra")

    return canvas


def main() -> None:
    export_icons()
    board = build_board()
    path = ROOT / "docs" / "asset-styleboard.png"
    board.convert("RGB").save(path, optimize=True)
    print("board:", path, board.size)

    # nền dọc 9:16 dùng thật trong UI/game
    ring_porthole(512).save(OUT / "ring_porthole.png")
    print("ring:", OUT / "ring_porthole.png")
    for i, seed in enumerate((11, 23, 37), start=1):
        plate_nebula(900, 1600, seed).convert("RGB").save(
            OUT / f"bg_nebula_{i}.jpg", quality=86, optimize=True,
            progressive=True)
        print("bg:", OUT / f"bg_nebula_{i}.jpg")


if __name__ == "__main__":
    main()
