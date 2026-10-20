#!/usr/bin/env python3
"""
GHI CHÚ D20: script này sinh Trái Đất VẼ TAY — KHÔNG còn dùng cho nền game.
Nền nay là ảnh thật (xem prototype/src/ui/NGUON-ANH.md). Giữ file làm tư liệu.
Sinh texture Trái Đất (equirectangular) + thiên thạch vẽ tay cho lớp nền game.

Chạy:  python3 docs/tools/planet_art.py
Ra:    prototype/src/ui/earth.jpg         1024×512  (map lên mặt cầu)
       prototype/src/art/game/meteor.png  512×512   (alpha)
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "prototype" / "src" / "ui"
ART = ROOT / "prototype" / "src" / "art" / "game"

W, H = 1536, 768


# ------------------------------------------------------------------ noise
def _noise(w: int, h: int, gw: int, gh: int, seed: int) -> np.ndarray:
    """Value-noise nội suy, lặp ngang (seamless theo kinh độ)."""
    rng = np.random.default_rng(seed)
    g = rng.random((gh, gw))
    xs = np.arange(w) / w * gw
    x0 = np.floor(xs).astype(int) % gw
    tx = (xs - np.floor(xs))[None, :]
    ys = np.arange(h) / h * gh
    y0 = np.clip(np.floor(ys).astype(int), 0, gh - 1)
    ty = (ys - np.floor(ys))[:, None]
    y1 = np.clip(y0 + 1, 0, gh - 1)
    a = g[y0][:, x0] * (1 - tx) + g[y0][:, (x0 + 1) % gw] * tx
    b = g[y1][:, x0] * (1 - tx) + g[y1][:, (x0 + 1) % gw] * tx
    return a * (1 - ty) + b * ty


def fbm(seed: int, base: tuple[int, int] = (6, 3), octaves: int = 5) -> np.ndarray:
    out = np.zeros((H, W))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        gw = base[0] * 2 ** o
        gh = max(2, base[1] * 2 ** o)
        out += _noise(W, H, gw, gh, seed + o * 17) * amp
        total += amp
        amp *= 0.5
    return out / total


def smoothstep(a: float, b: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def mix(c1, c2, t):
    c1 = np.array(c1, np.float64)
    c2 = np.array(c2, np.float64)
    return c1[None, None, :] * (1 - t[..., None]) + c2[None, None, :] * t[..., None]


def earth() -> Image.Image:
    """Texture equirectangular vẽ tay: biển sâu xanh mực, thềm ngọc lam, lục địa xanh sống động."""
    lat = (np.arange(H)[:, None] / H - 0.5) * 2          # -1 nam … +1 bắc
    lat2 = np.repeat(lat, W, axis=1)

    plate = fbm(101, base=(3, 2), octaves=3)
    mid = fbm(211, base=(7, 4), octaves=4)
    detail = fbm(409, base=(16, 8), octaves=5)
    elev = plate * 0.50 + mid * 0.33 + detail * 0.17
    lo, hi = np.percentile(elev, 2), np.percentile(elev, 98)
    elev = np.clip((elev - lo) / (hi - lo), 0, 1)

    thr = np.percentile(elev, 68)                        # ~32 % diện tích là đất
    land = smoothstep(thr - 0.003, thr + 0.006, elev)
    shelf = smoothstep(thr - 0.07, thr - 0.003, elev) * (1 - land)
    deepness = 1 - smoothstep(0.0, thr - 0.02, elev)

    # ---- biển: xanh mực → xanh thẳm → ngọc lam ở thềm
    deepSea = np.array([6, 16, 49], np.float64)
    bodySea = np.array([9, 39, 96], np.float64)
    shelfSea = np.array([24, 126, 158], np.float64)
    sea = deepSea + (bodySea - deepSea) * (1 - deepness[..., None])
    sea = sea * (1 - shelf[..., None]) + shelfSea * shelf[..., None]

    # ---- đất: xanh lá sống động, xen đồng cỏ vàng, núi xám, tuyết chỉ trên đỉnh cao
    biome = fbm(307, base=(5, 3), octaves=4)
    jungle = np.array([26, 104, 62], np.float64)
    grass = np.array([92, 146, 66], np.float64)
    savanna = np.array([176, 148, 74], np.float64)

    t1 = smoothstep(0.30, 0.62, biome)[..., None]
    ground = jungle * (1 - t1) + grass * t1
    t2 = smoothstep(0.68, 0.88, biome)[..., None]
    ground = ground * (1 - t2) + savanna * t2

    # núi: xám xanh, cao hơn thì sáng
    rock = np.array([104, 112, 126], np.float64)
    rockHi = np.array([168, 176, 186], np.float64)
    rk = smoothstep(0.72, 0.93, elev)[..., None]
    mtn = rock * (1 - rk) + rockHi * rk
    km = smoothstep(0.70, 0.86, elev)[..., None]
    ground = ground * (1 - km) + mtn * km

    snow = smoothstep(0.935, 0.985, elev)[..., None]
    ground = ground * (1 - snow) + np.array([240, 246, 252], np.float64) * snow

    # đổ bóng sườn dốc nhẹ (giữ gam phẳng kiểu tranh)
    gy, gx = np.gradient(elev)
    relief = np.clip(1.0 - (gx * 4.5 + gy * 4.5), 0.78, 1.22)
    ground = np.clip(ground * relief[..., None], 0, 255)

    rgb = sea * (1 - land[..., None]) + ground * land[..., None]

    # viền bờ: dải cát mảnh + mép tối
    sand = (smoothstep(thr + 0.002, thr + 0.008, elev) - smoothstep(thr + 0.010, thr + 0.026, elev)) * land
    rgb = rgb * (1 - sand[..., None] * 0.6) + np.array([222, 206, 160], np.float64) * sand[..., None] * 0.6
    surf = (smoothstep(thr - 0.028, thr - 0.006, elev) - smoothstep(thr - 0.006, thr, elev)) * (1 - land)
    rgb = rgb * (1 - surf[..., None] * 0.5) + np.array([196, 246, 250], np.float64) * surf[..., None] * 0.5

    # băng cực mềm
    ice = smoothstep(0.88, 0.96, np.abs(lat2))
    rgb = rgb * (1 - ice[..., None]) + np.array([232, 243, 252], np.float64) * ice[..., None]

    # ---- mây
    cloud = fbm(509, base=(6, 3), octaves=6)
    cloud = smoothstep(0.60, 0.80, cloud) * (0.30 + 0.70 * np.cos(lat2 * 1.05))
    cloud = np.asarray(Image.fromarray((cloud * 255).astype("uint8"), "L")
                       .filter(ImageFilter.GaussianBlur(1.1))) / 255.0
    globals()["_CLOUD"] = cloud

    # ---- đèn thành phố (dùng cho shader ban đêm)
    rng = np.random.default_rng(11)
    lights = np.zeros((H, W), np.float32)
    cityMask = land * (1 - ice) * (1 - snow[..., 0]) * (1 - smoothstep(0.60, 0.9, elev))
    ys, xs = np.nonzero(cityMask > 0.65)
    if len(xs):
        n = min(len(xs), int(W * H * 0.0035))
        pick = rng.choice(len(xs), size=n, replace=False)
        for i in pick:
            lights[ys[i], xs[i]] = rng.uniform(0.45, 1.0)
        n2 = int(W * H * 0.0009)
        pick2 = rng.choice(len(xs), size=n2, replace=False)
        for i in pick2:
            y, x = ys[i], xs[i]
            rr = int(rng.uniform(1, 3))
            lights[max(0, y - rr):y + rr + 1, max(0, x - 2 * rr):x + 2 * rr + 1] += rng.uniform(0.25, 0.6)
    lights = np.asarray(Image.fromarray((np.clip(lights, 0, 1) * 255).astype(np.uint8), "L")
                        .filter(ImageFilter.GaussianBlur(0.7))) / 255.0
    globals()["_LIGHTS"] = lights

    shade = 1 - 0.14 * smoothstep(0.6, 1.0, np.abs(lat2))
    rgb = np.clip(rgb * shade[..., None], 0, 255)
    return Image.fromarray(rgb.astype("uint8"), "RGB")


def sphere_preview(equirect: Image.Image, size: int = 420, lon0: float = 0.6) -> Image.Image:
    """Render thử mặt cầu từ texture equirect để soi trước khi đưa vào game."""
    out = Image.new("RGB", (size, size), (4, 7, 16))
    px = out.load()
    src = equirect.convert("RGB")
    sw, sh = src.size
    sun = np.array([-0.62, 0.55, 0.55])
    sun /= np.linalg.norm(sun)
    r = size / 2
    for y in range(size):
        for x in range(size):
            nx = (x - r) / r
            ny = (r - y) / r
            d2 = nx * nx + ny * ny
            if d2 > 1:
                continue
            nz = math.sqrt(max(0.0, 1 - d2))
            n = np.array([nx, ny, nz])
            lam = 2 * math.pi * lon0 + math.atan2(nx, nz)
            phi = math.asin(max(-1.0, min(1.0, ny)))
            u = (lam / (2 * math.pi)) % 1.0
            v = 0.5 - phi / math.pi
            sx = int(u * (sw - 1))
            sy = int(v * (sh - 1))
            c = src.getpixel((sx, sy))
            l = max(0.0, float(n @ sun))
            k = 0.24 + 1.0 * (l ** 0.9)
            rim = (1 - nz) ** 3
            cr = min(255, c[0] * k + 60 * rim * (0.3 + 0.7 * l))
            cg = min(255, c[1] * k + 110 * rim * (0.3 + 0.7 * l))
            cb = min(255, c[2] * k + 190 * rim * (0.3 + 0.7 * l))
            px[x, y] = (int(cr), int(cg), int(cb))
    return out


# --------------------------------------------------------------- meteor
def meteor(size: int = 512) -> Image.Image:
    """Thiên thạch vẽ tay: khối đá gradient, hố va chạm, viền navy đậm."""
    rng = np.random.default_rng(42)
    S = size * 3
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = S / 2, S / 2
    n = 26
    pts = []
    for i in range(n):
        a = i / n * math.tau
        r = S * 0.34 * (1 + 0.16 * math.sin(a * 3 + 0.7) + 0.09 * math.sin(a * 5 + 2.1)
                        + rng.uniform(-0.045, 0.045))
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * 0.97))

    d.polygon(pts, fill=(18, 24, 52, 255))
    inner = [(cx + (x - cx) * 0.94, cy + (y - cy) * 0.94) for x, y in pts]

    body = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.polygon(inner, fill=(126, 112, 104, 255))
    grad = Image.new("L", (S, S), 0)
    gd = ImageDraw.Draw(grad)
    for i in range(S):
        gd.line([(0, i), (S, i)], fill=int(255 * (1 - i / S)))
    grad = grad.rotate(38, resample=Image.BICUBIC)
    dark = Image.new("RGBA", (S, S), (48, 42, 48, 255))
    light = Image.new("RGBA", (S, S), (206, 190, 168, 255))
    body = Image.composite(light, body, grad.point(lambda v: int(v * 0.85)))
    body = Image.composite(dark, body, grad.point(lambda v: int(max(0, 90 - v) * 1.4)))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).polygon(inner, fill=255)
    img.paste(body, (0, 0), Image.composite(mask, Image.new("L", (S, S), 0), body.getchannel("A")))

    d = ImageDraw.Draw(img)
    for _ in range(9):
        a = rng.uniform(0, math.tau)
        rr = rng.uniform(0, S * 0.26)
        px_, py_ = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        cr = rng.uniform(S * 0.022, S * 0.062)
        d.ellipse([px_ - cr, py_ - cr, px_ + cr, py_ + cr], fill=(84, 74, 76, 255))
        d.arc([px_ - cr, py_ - cr, px_ + cr, py_ + cr], 200, 340,
              fill=(212, 198, 178, 255), width=max(2, S // 190))
    for _ in range(3):
        x, y = cx + rng.uniform(-S * 0.2, S * 0.2), cy + rng.uniform(-S * 0.2, S * 0.2)
        seg = [(x, y)]
        for _ in range(4):
            x += rng.uniform(-S * 0.06, S * 0.06)
            y += rng.uniform(-S * 0.06, S * 0.06)
            seg.append((x, y))
        d.line(seg, fill=(40, 36, 48, 220), width=max(2, S // 220))

    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(rim).polygon(inner, outline=(255, 236, 210, 190), width=int(S * 0.012))
    rim = rim.filter(ImageFilter.GaussianBlur(S * 0.004))
    img = Image.alpha_composite(img, rim)

    bbox = img.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    img = img.crop(bbox)
    w, h = img.size
    side = int(max(w, h) * 1.05)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - w) // 2, (side - h) // 2), img)
    return canvas.resize((size, size), Image.LANCZOS)


def earth_lights() -> Image.Image:
    """Đèn thành phố phía ban đêm (Pha R, alpha cao) — shader dùng kênh R."""
    l = np.clip(globals().get("_LIGHTS", np.zeros((H, W))), 0, 1)
    l = (l * 1.9) ** 0.9
    l = np.clip(l, 0, 1)
    img = np.dstack([l * 255, l * 190, l * 120, l * 255])
    return Image.fromarray(img.astype("uint8"), "RGBA")


def earth_clouds() -> Image.Image:
    """Lớp mây RGBA (trắng + alpha) để dán lên mặt cầu Trái Đất."""
    a = np.clip(globals().get("_CLOUD", np.zeros((H, W))), 0, 1)
    a = (a * 1.55) ** 1.15
    a = np.clip(a, 0, 1)
    rgba = np.dstack([np.full((H, W), 255, np.float32),
                      np.full((H, W), 255, np.float32),
                      np.full((H, W), 255, np.float32),
                      a * 255])
    return Image.fromarray(rgba.astype("uint8"), "RGBA")


def main() -> None:
    UI.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    e = earth()
    c = earth_clouds().resize((768, 384), Image.LANCZOS)
    c.save(UI / "earth_clouds.png", optimize=True)
    li = earth_lights().resize((768, 384), Image.LANCZOS)
    li.save(UI / "earth_lights.png", optimize=True)
    e.save(UI / "earth.jpg", quality=88, optimize=True)
    e.resize((768, 384), Image.LANCZOS).save("/tmp/earth_preview.jpg", quality=90)
    sphere_preview(e, 420, 0.35).save("/tmp/earth_sphere.jpg", quality=92)
    m = meteor()
    m.save(ART / "meteor.png")
    print("earth.jpg", (UI / "earth.jpg").stat().st_size // 1024, "KB")
    print("earth_clouds.png", (UI / "earth_clouds.png").stat().st_size // 1024, "KB")
    print("earth_lights.png", (UI / "earth_lights.png").stat().st_size // 1024, "KB")
    print("meteor.png", (ART / "meteor.png").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
