"""Sprite tàu vẽ tay bằng hình học (không dùng render 3D).

Mỗi tàu là một bộ đa giác tham số trong khung 512x512, mũi tàu hướng lên.
Bộ vẽ dùng chung: nền tối, cánh tô gradient + facet sáng/tối, thân có dải
specular, buồng lái phát sáng, ống xả + lửa, viền tối 5px, rim light góc trên
trái. Kết quả là minh hoạ phẳng nhưng có khối, đúng hướng WindWings.

Chạy trực tiếp:  python3 docs/tools/ship_sprites.py   (xuất contact sheet /tmp)
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

S = 512
CX = S / 2


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def vgrad(w: int, h: int, top: str, bottom: str, mid: str | None = None) -> Image.Image:
    stops = [(0.0, top), (1.0, bottom)] if mid is None else [(0.0, top), (0.55, mid), (1.0, bottom)]
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


def hgrad(w: int, h: int, left: str, right: str, mid: str | None = None) -> Image.Image:
    stops = [(0.0, left), (1.0, right)] if mid is None else [(0.0, left), (0.5, mid), (1.0, right)]
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for x in range(w):
        t = x / max(1, w - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / max(1e-6, p1 - p0)
                a, b = hx(c0), hx(c1)
                col = tuple(round(a[j] + (b[j] - a[j]) * k) for j in range(3))
                d.line([(x, 0), (x, h)], fill=col)
                break
        else:
            d.line([(x, 0), (x, h)], fill=hx(stops[-1][1]))
    return img


def hgrad_px(w: int, h: int, stops) -> Image.Image:
    """Gradient ngang với stop theo toạ độ pixel: [(x, hex), ...]."""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for x in range(w):
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= x <= p1:
                k = (x - p0) / max(1e-6, p1 - p0)
                a, b = hx(c0), hx(c1)
                d.line([(x, 0), (x, h)], fill=tuple(round(a[j] + (b[j] - a[j]) * k) for j in range(3)))
                break
        else:
            d.line([(x, 0), (x, h)], fill=hx(stops[-1][1]))
    return img


def poly_mask(polys, size=(S, S)) -> Image.Image:
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon(p, fill=255)
    return m


def paint(canvas: Image.Image, mask: Image.Image, grad: Image.Image) -> None:
    canvas.paste(grad, (0, 0), mask)


def mirror(poly):
    return [(2 * CX - x, y) for x, y in poly]


def dilate(mask: Image.Image, r: int) -> Image.Image:
    return mask.filter(ImageFilter.MaxFilter(2 * r + 1))


def glow(canvas: Image.Image, mask: Image.Image, color: str, radius: float, alpha: int) -> None:
    a = mask.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * alpha / 255))
    layer = Image.new("RGBA", canvas.size, hx(color) + (0,))
    layer.putalpha(a)
    canvas.alpha_composite(layer)


# ------------------------------------------------------------------ shapes
# Trả về dict: hull [poly...], wings [poly...] (chỉ nửa phải), boom [poly...],
# canopy box, nozzles [(x, y, w, h)], stripes [(x0, y0, x1, y1)], tip pods.

def geo_striker():
    hull = [[(256, 54), (274, 118), (296, 176), (304, 330), (292, 428),
             (220, 428), (208, 330), (216, 176), (238, 118)]]
    wing_r = [[(294, 198), (410, 262), (426, 306), (300, 316)],
              [(300, 322), (400, 330), (392, 356), (300, 350)]]
    pods = [[(392, 246), (424, 268), (420, 312), (386, 300)]]
    canopy = [(238, 116), (274, 116), (282, 184), (256, 210), (230, 184)]
    nozzles = [(226, 420, 26, 20), (260, 420, 26, 20)]
    stripes = [(256, 120, 256, 300)]
    return dict(hull=hull, wing=wing_r, boom=pods, canopy=canopy, nozzles=nozzles, stripes=stripes)


def geo_zenith():
    hull = [[(256, 36), (270, 110), (284, 210), (300, 400), (288, 448),
             (224, 448), (212, 400), (228, 210), (242, 110)]]
    wing_r = [[(286, 206), (448, 384), (438, 420), (300, 372), (296, 300)]]
    pods = []
    canopy = [(236, 128), (276, 128), (270, 214), (256, 240), (242, 214)]
    nozzles = [(224, 436, 64, 26)]
    stripes = [(256, 210, 256, 380)]
    return dict(hull=hull, wing=wing_r, boom=pods, canopy=canopy, nozzles=nozzles, stripes=stripes)


def geo_challenger():
    hull = [[(256, 62), (278, 128), (292, 300), (288, 412), (224, 412), (220, 300), (234, 128)]]
    wing_r = [[(288, 214), (352, 214), (352, 300), (288, 300)],
              [(288, 306), (352, 306), (352, 356), (288, 336)]]
    boom = [[(326, 166), (360, 178), (366, 424), (326, 424)],
            [(300, 372), (352, 372), (352, 404), (300, 404)]]
    canopy = [(236, 122), (276, 122), (282, 196), (256, 224), (230, 196)]
    nozzles = [(330, 414, 30, 24), (214, 402, 26, 20), (272, 402, 26, 20)]
    stripes = [(256, 236, 256, 392)]
    return dict(hull=hull, wing=wing_r, boom=boom, canopy=canopy, nozzles=nozzles, stripes=stripes)


def geo_spitfire():
    hull = [[(256, 66), (274, 136), (284, 300), (284, 424), (228, 424), (228, 300), (238, 136)]]
    wing_r = [[(278, 246), (432, 150), (458, 178), (300, 300)],
              [(278, 300), (436, 350), (420, 382), (292, 340)]]
    pods = [[(430, 152), (472, 168), (468, 206), (424, 190)],
            [(422, 352), (462, 366), (454, 400), (414, 386)]]
    canopy = [(240, 128), (272, 128), (266, 204), (256, 228), (246, 204)]
    nozzles = [(438, 190, 24, 16), (430, 386, 24, 16), (266, 392, 22, 16), (232, 392, 22, 16)]
    stripes = [(256, 220, 256, 370)]
    return dict(hull=hull, wing=wing_r, boom=pods, canopy=canopy, nozzles=nozzles, stripes=stripes)


def geo_insurgent():
    hull = [[(256, 84), (302, 148), (316, 250), (316, 408), (196, 408), (196, 250), (210, 148)]]
    wing_r = [[(312, 244), (388, 244), (396, 356), (312, 356)]]
    boom = [[(146, 210), (188, 214), (188, 384), (146, 374)],
            [(320, 300), (372, 300), (372, 344), (320, 344)]]
    canopy = [(228, 138), (286, 138), (292, 206), (256, 236), (220, 206)]
    nozzles = [(204, 398, 30, 22), (242, 398, 30, 22), (280, 398, 30, 22)]
    stripes = [(212, 250, 300, 250), (212, 300, 300, 300)]
    return dict(hull=hull, wing=wing_r, boom=boom, canopy=canopy, nozzles=nozzles, stripes=stripes)


def geo_executioner():
    hull = [[(256, 30), (272, 120), (280, 250), (286, 430), (226, 430), (232, 250), (240, 120)]]
    wing_r = [[(276, 296), (418, 420), (400, 446), (272, 366)],
              [(276, 214), (356, 236), (352, 262), (276, 246)]]
    pods = []
    canopy = [(242, 96), (270, 96), (274, 168), (256, 196), (238, 168)]
    nozzles = [(236, 418, 30, 20), (268, 418, 30, 20)]
    stripes = [(256, 200, 256, 390)]
    return dict(hull=hull, wing=wing_r, boom=pods, canopy=canopy, nozzles=nozzles, stripes=stripes)


def geo_omen():
    hull = [[(256, 60), (280, 140), (296, 260), (292, 424), (220, 424), (216, 260), (232, 140)]]
    wing_r = [[(290, 210), (352, 172), (410, 200), (392, 240), (462, 292),
               (430, 312), (470, 380), (372, 338), (298, 352)]]
    pods = []
    canopy = [(240, 126), (272, 126), (266, 196), (256, 220), (246, 196)]
    nozzles = [(228, 414, 26, 20), (258, 414, 26, 20)]
    stripes = [(256, 230, 256, 400)]
    return dict(hull=hull, wing=wing_r, boom=pods, canopy=canopy, nozzles=nozzles, stripes=stripes)


def geo_dispatcher():
    hull = [[(256, 96), (316, 156), (326, 260), (326, 414), (186, 414), (186, 260), (196, 156)]]
    wing_r = [[(320, 190), (398, 246), (398, 392), (320, 392)]]
    boom = [[(132, 236), (184, 244), (184, 396), (132, 384)],
            [(328, 268), (376, 282), (376, 352), (328, 344)]]
    canopy = [(232, 146), (280, 146), (284, 208), (256, 228), (228, 208)]
    nozzles = [(196, 404, 26, 20), (230, 404, 26, 20), (264, 404, 26, 20), (298, 404, 26, 20)]
    stripes = [(256, 240, 256, 396), (206, 340, 306, 340)]
    return dict(hull=hull, wing=wing_r, boom=boom, canopy=canopy, nozzles=nozzles, stripes=stripes)


SHIPS = {
    "striker": dict(geo=geo_striker, base="#E49302", light="#FFD066", dark="#8C4C00",
                    accent="#F2F9FF", canopy="#6FE6FF", flame="#7FE0FF", boom_col="#D9DEE6"),
    "zenith": dict(geo=geo_zenith, base="#2A69C2", light="#8FD8FF", dark="#0E2E60",
                   accent="#FFC04A", canopy="#7FE6FF", flame="#8FD8FF", boom_col="#9FB6D4"),
    "challenger": dict(geo=geo_challenger, base="#B23BC8", light="#F29BFF", dark="#54105E",
                       accent="#F2F9FF", canopy="#FFD066", flame="#FFB0F0", boom_col="#C9CCD6"),
    "spitfire": dict(geo=geo_spitfire, base="#18B03C", light="#8CF07A", dark="#074F18",
                     accent="#F7A507", canopy="#7FE6FF", flame="#8CFF9B", boom_col="#D9DEE6"),
    "insurgent": dict(geo=geo_insurgent, base="#C81515", light="#FF7A5E", dark="#5C0505",
                      accent="#C9D3DE", canopy="#FFC04A", flame="#FFB07A", boom_col="#8C96A4"),
    "executioner": dict(geo=geo_executioner, base="#5B3FA8", light="#B79BFF", dark="#22103F",
                        accent="#FFD34D", canopy="#FFC04A", flame="#C9B0FF", boom_col="#B9B3CC"),
    "omen": dict(geo=geo_omen, base="#17327A", light="#6F9BFF", dark="#050C22",
                 accent="#FFC93C", canopy="#8FE9FF", flame="#8FE9FF", boom_col="#7C86A6"),
    "dispatcher": dict(geo=geo_dispatcher, base="#0E7FA8", light="#7FE6FF", dark="#03303F",
                       accent="#FF8A2B", canopy="#B6F3FF", flame="#7FE6FF", boom_col="#A9B6C6"),
}


# ------------------------------------------------------------------ render
def render_ship(name: str, size: int = 360) -> Image.Image:
    spec = SHIPS[name]
    g = spec["geo"]()

    def all_polys():
        polys = list(g["hull"]) + list(g["boom"])
        for p in g["wing"]:
            polys.append(p)
            polys.append(mirror(p))
        return polys

    body_polys = all_polys()
    body_mask = poly_mask(body_polys)

    # 1) viền tối (vẽ dưới)
    dark = dilate(body_mask, 5)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    border = Image.new("RGBA", (S, S), hx("#050A18") + (255,))
    out.paste(border, (0, 0), dark)
    d = ImageDraw.Draw(out)

    # 1b) bóng đổ mềm dưới tàu
    sh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sh).ellipse((CX - 150, 396, CX + 150, 470), fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    shl = Image.new("RGBA", (S, S), (3, 7, 18, 0))
    shl.putalpha(sh)
    out.alpha_composite(shl)

    # 2) cánh: gradient + facet
    wing_mask = poly_mask([p for p in sum([[w, mirror(w)] for w in g["wing"]], [])])
    wg = vgrad(S, S, spec["light"], spec["dark"], spec["base"]).convert("RGBA")
    paint(out, wing_mask, wg)
    # facet sáng ở mép trước, tối ở mép sau
    for w in g["wing"]:
        for ww in (w, mirror(w)):
            cxw = sum(p[0] for p in ww) / len(ww)
            cyw = sum(p[1] for p in ww) / len(ww)
            # mảng sáng phía mép trước (nửa trên của đa giác)
            lead = sorted(ww, key=lambda p: p[1])[:2]
            light_tri = [lead[0], lead[1], (cxw, cyw)]
            lf = poly_mask([light_tri])
            p2 = Image.new("RGBA", (S, S), hx(spec["light"]) + (0,))
            p2.putalpha(lf.point(lambda v: int(v * 0.70)))
            out.alpha_composite(p2)
            # mảng tối phía mép sau
            trail = sorted(ww, key=lambda p: p[1])[-2:]
            dark_tri = [trail[0], trail[1], (cxw, cyw)]
            df = poly_mask([dark_tri])
            p3 = Image.new("RGBA", (S, S), hx("#050A18") + (0,))
            p3.putalpha(df.point(lambda v: int(v * 0.40)))
            out.alpha_composite(p3)
            # gân cánh
            d.line([ (lead[0][0], lead[0][1]), (trail[1][0], trail[1][1]) ],
                   fill=hx(spec["accent"]) + (150,), width=4)

    # 3) boom (pod) sáng hơn thân
    boom_mask = poly_mask([p for p in sum([[b, mirror(b)] for b in g["boom"]], [])])
    bg_ = hgrad(S, S, spec["boom_col"], spec["dark"], spec["boom_col"]).convert("RGBA")
    paint(out, boom_mask, bg_)

    # 4) thân: gradient ngang (trái sáng, phải tối) + specular
    hull_mask = poly_mask(g["hull"])
    hb = hull_mask.getbbox() or (0, 0, S, S)
    hw = max(1, hb[2] - hb[0])
    hg = hgrad_px(S, S, [(hb[0], spec["light"]), (hb[0] + hw * 0.34, spec["base"]),
                         (hb[0] + hw * 0.78, spec["dark"]), (hb[2], spec["dark"])]).convert("RGBA")
    paint(out, hull_mask, hg)
    spec_mask = ImageChops.subtract(hull_mask, ImageChops.offset(hull_mask, 0, 0))
    band = Image.new("L", (S, S), 0)
    ImageDraw.Draw(band).rectangle((CX - 46, 0, CX - 18, S), fill=255)
    band = ImageChops.multiply(band.filter(ImageFilter.GaussianBlur(9)), hull_mask)
    hi = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    hi.putalpha(band.point(lambda v: int(v * 0.30)))
    out.alpha_composite(hi)
    del spec_mask

    # 5) dải accent dọc thân
    for x0, y0, x1, y1 in g["stripes"]:
        if x0 == x1:
            d.line((x0, y0, x1, y1), fill=hx(spec["accent"]) + (235,), width=9)
            d.line((x0 - 3, y0, x1 - 3, y1), fill=hx("#FFFFFF") + (120,), width=2)
        else:
            d.line((x0, y0, x1, y1), fill=hx(spec["accent"]) + (200,), width=7)

    # 6) panel lines
    for w in g["wing"]:
        for ww in (w, mirror(w)):
            d.line([ww[0], ww[-1]], fill=hx("#0A1120") + (120,), width=2)

    # 6b) đinh tán / chi tiết nhỏ trên thân
    for k in range(3):
        ry = 250 + k * 46
        for bx in (CX - 20, CX + 20):
            d.ellipse((bx - 3, ry - 3, bx + 3, ry + 3), fill=hx(spec["accent"]) + (170,))
            d.ellipse((bx - 3, ry - 4, bx + 3, ry - 1), fill=hx("#FFFFFF") + (120,))

    # 7) canopy + glow
    cm = poly_mask([g["canopy"]])
    cg = vgrad(S, S, "#FFFFFF", spec["canopy"], "#0A3550").convert("RGBA")
    glow(out, cm, spec["canopy"], 10, 150)
    paint(out, cm, cg)
    d.polygon(g["canopy"], outline=hx("#071426") + (255,), width=4)
    # highlight buồng lái
    xs = [p[0] for p in g["canopy"]]
    ys = [p[1] for p in g["canopy"]]
    hx0, hx1 = min(xs), max(xs)
    hy0, hy1 = min(ys), max(ys)
    hm = Image.new("L", (S, S), 0)
    ImageDraw.Draw(hm).ellipse((hx0 + (hx1 - hx0) * 0.16, hy0 + (hy1 - hy0) * 0.07,
                                hx0 + (hx1 - hx0) * 0.58, hy0 + (hy1 - hy0) * 0.24), fill=255)
    hm = ImageChops.multiply(hm, cm)
    white = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    white.putalpha(hm.point(lambda v: int(v * 0.85)))
    out.alpha_composite(white)

    # 8) ống xả + lửa
    for (nx, ny, nw, nh) in g["nozzles"]:
        for nx2 in (nx, 2 * CX - nx - nw):
            if nx2 < nx - 1 and nx == 0:
                continue
            box = (nx2, ny, nx2 + nw, ny + nh)
            fmask = Image.new("L", (S, S), 0)
            ImageDraw.Draw(fmask).ellipse(box, fill=255)
            glow(out, fmask, spec["flame"], 14, 210)
            d.ellipse(box, fill=hx("#0A1120") + (255,))
            d.ellipse((box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 3), fill=hx(spec["flame"]) + (255,))
            d.ellipse((box[0] + 7, box[1] + 6, box[2] - 8, box[3] - 7), fill=hx("#FFFFFF") + (230,))
            # lửa phía sau: 2 lớp, dài gấp 2.4 lần ống xả
            fy = box[3] - 2
            mid = (box[0] + box[2]) / 2
            fl = [(box[0] + 2, fy), (box[2] - 2, fy), (mid, fy + nh * 2.4)]
            fm2 = poly_mask([fl])
            glow(out, fm2, spec["flame"], 12, 190)
            d.polygon(fl, fill=hx(spec["flame"]) + (190,))
            fl2 = [(box[0] + 6, fy), (box[2] - 6, fy), (mid, fy + nh * 1.2)]
            d.polygon(fl2, fill=hx("#FFFFFF") + (215,))

    # 9) rim light góc trên-trái: viền sáng dọc silhouette
    inner = body_mask.filter(ImageFilter.MinFilter(5))
    edge = ImageChops.subtract(body_mask, inner)
    diag = Image.new("L", (S, S), 0)
    dd = ImageDraw.Draw(diag)
    for i in range(S):
        v = max(0, 255 - int(i * 255 / (S * 0.95)))
        dd.line([(0, S - i), (i, S)], fill=v)  # noqa: F841  (giữ chỗ, không dùng)
    # dùng gradient chéo: sáng ở góc trên-trái
    diag = Image.new("L", (S, S), 0)
    dd = ImageDraw.Draw(diag)
    for y in range(S):
        for x in range(0, S, 4):
            v = max(0, min(255, int(220 - (x + y) * 0.30)))
            dd.rectangle((x, y, x + 3, y), fill=v)
    rim = ImageChops.multiply(edge, diag.filter(ImageFilter.GaussianBlur(3)))
    rimc = Image.new("RGBA", (S, S), hx("#EAF6FF") + (0,))
    rimc.putalpha(rim.point(lambda v: int(v * 0.9)))
    out.alpha_composite(rimc)

    if size != S:
        out = out.resize((size, size), Image.LANCZOS)
    return out


def contact_sheet(path: str = "/tmp/ships.png", size: int = 300) -> None:
    names = list(SHIPS)
    cols, rows = 4, 2
    pad = 16
    sheet = Image.new("RGBA", (cols * (size + pad) + pad, rows * (size + pad) + pad), hx("#0A1026") + (255,))
    for i, n in enumerate(names):
        sp = render_ship(n, size)
        x = pad + (i % cols) * (size + pad)
        y = pad + (i // cols) * (size + pad)
        sheet.alpha_composite(sp, (x, y))
    sheet.convert("RGB").save(path, quality=92)
    print("sheet:", path)


if __name__ == "__main__":
    import sys

    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/ships.png"
    contact_sheet(out)
