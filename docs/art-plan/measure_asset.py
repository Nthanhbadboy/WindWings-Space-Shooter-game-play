#!/usr/bin/env python3
"""measure_asset.py — đo sprite theo giao thức §4.9 của ART_REDRAW_PLAN.

Hai chế độ:

    python3 docs/art-plan/measure_asset.py --recipe
        Tái lập bảng 9 công thức tô (§4.5) từ hex palette + tỉ lệ diện tích, rồi
        đối chiếu với dải mục tiêu từng nhóm (§4.3). Không cần thư viện ngoài.
        Exit 0 = 9/9 công thức khớp số đã công bố VÀ nằm trong dải mục tiêu.

    python3 docs/art-plan/measure_asset.py --dir <thư mục> [--class ship|drone|...]
        Đo mọi file .png trong thư mục (cần Pillow) và chấm theo dải §4.3.
        Exit 0 = mọi asset trong dải; 1 = có asset lệch (in ra metric nào lệch).

Giao thức đo (§4.9) — khác `tools/art-study.py` ở 4 điểm:
  1. đo trên PNG có alpha (JPEG làm `dark`/`colors` thành cận dưới);
  2. mask = alpha > 0,5 (không flood-fill nền caro);
  3. lượng tử 32 bậc/kênh rồi đếm màu (`colors`);
  4. `sat` chỉ trên pixel V ≥ 0,25; thêm `chroma = S·V` trên toàn sprite.

Định nghĩa số (giống hệt bảng §4.5, đã tái lập 9/9):
  val      = trung bình V của pixel trong mask
  val_std  = độ lệch chuẩn **quần thể** (pstdev) của V
  dark     = tỉ lệ pixel có max(R,G,B) < 45
  chroma   = trung bình S·V
  colors   = số ô màu khác nhau sau khi lượng tử mỗi kênh về 32 bậc
"""

from __future__ import annotations

import argparse
import pathlib
import statistics
import sys

# ---------------------------------------------------------------- palette (§4.4)
PALETTE: dict[str, tuple[int, int, int]] = {
    "ink900": (0x0B, 0x0E, 0x14),
    "ink700": (0x16, 0x1C, 0x26),
    "ink500": (0x2A, 0x34, 0x42),
    "ink300": (0x4A, 0x56, 0x6B),
    "paper": (0xE8, 0xE3, 0xD9),
    "ember": (0xFF, 0x5A, 0x2B),
    "emberdim": (0x8C, 0x2F, 0x17),
    "teal": (0x4F, 0xD1, 0xC5),
    "gold": (0xF5, 0xC5, 0x18),
    "danger": (0xE2, 0x3A, 0x3A),
    "white": (0xFF, 0xFF, 0xFF),
}

# ------------------------------------------------------- 9 công thức (§4.5), % diện tích
RECIPES: dict[str, dict[str, int]] = {
    "ship":   {"ink300": 40, "ink500": 25, "ink700": 8, "paper": 10, "ember": 12, "emberdim": 5},
    "enemy":  {"ink300": 50, "paper": 30, "teal": 15, "ink700": 5},
    "drone":  {"ink300": 50, "ink500": 30, "gold": 12, "paper": 8},
    "boss":   {"ink300": 50, "ink500": 15, "paper": 10, "emberdim": 15, "ember": 6, "ink900": 4},
    "bullet": {"ink900": 45, "ink300": 45, "emberdim": 10},
    "ui":     {"ink500": 50, "ink300": 25, "ink700": 8, "paper": 12, "ember": 5},
    "fx":     {"paper": 55, "white": 30, "ink300": 12, "teal": 3},
    "bg":     {"ink900": 40, "ink700": 20, "ink500": 30, "teal": 10},
    "item":   {"ink300": 45, "gold": 25, "paper": 25, "ink500": 5},
}

# --------------------------------------- số đã công bố ở §4.5 (val, val_std, dark, chroma)
PUBLISHED: dict[str, tuple[float, float, float, float]] = {
    "ship":   (0.483, 0.271, 0.080, 0.209),
    "enemy":  (0.613, 0.250, 0.050, 0.162),
    "drone":  (0.476, 0.243, 0.000, 0.202),
    "boss":   (0.485, 0.226, 0.040, 0.205),
    "bullet": (0.279, 0.185, 0.450, 0.120),
    "ui":     (0.405, 0.253, 0.080, 0.133),
    "fx":     (0.875, 0.174, 0.000, 0.063),
    "bg":     (0.221, 0.213, 0.600, 0.106),
    "item":   (0.669, 0.269, 0.000, 0.294),
}

# ------------------------------------- dải mục tiêu từng nhóm (§4.3): (lo, hi) hoặc None
BANDS: dict[str, dict[str, tuple[float, float]]] = {
    "ship":   {"colors": (110, 160), "val": (0.46, 0.52), "val_std": (0.24, 0.30), "dark": (0.00, 0.10), "chroma": (0.19, 0.23)},
    "drone":  {"colors": (100, 130), "val": (0.45, 0.52), "val_std": (0.22, 0.26), "dark": (0.00, 0.08), "chroma": (0.18, 0.22)},
    "boss":   {"colors": (110, 160), "val": (0.45, 0.52), "val_std": (0.20, 0.24), "dark": (0.00, 0.10), "chroma": (0.18, 0.23)},
    "enemy":  {"colors": (30, 60),   "val": (0.58, 0.65), "val_std": (0.23, 0.27), "dark": (0.00, 0.06), "chroma": (0.14, 0.17)},
    "bullet": {"colors": (24, 40),   "val": (0.25, 0.30), "val_std": (0.18, 0.26), "dark": (0.40, 1.00), "chroma": (0.00, 0.12)},
    "ui":     {"colors": (40, 70),   "val": (0.38, 0.44), "val_std": (0.24, 0.28), "dark": (0.00, 0.12), "chroma": (0.00, 0.14)},
    "fx":     {"colors": (3, 10),    "val": (0.70, 0.90), "val_std": (0.15, 0.25), "dark": (0.00, 0.02), "chroma": (0.00, 0.08)},
    "bg":     {"colors": (30, 50),   "val": (0.15, 0.25), "val_std": (0.18, 0.22), "dark": (0.55, 1.00), "chroma": (0.00, 0.12)},
    "item":   {"colors": (50, 80),   "val": (0.62, 0.70), "val_std": (0.22, 0.28), "dark": (0.00, 0.05), "chroma": (0.25, 0.30)},
}

# ------------------------- dải ba chỉ số style 2.5D (STYLE-CORRECTION lần 149)
# Hiệu chuẩn trên 3 mẫu dựng bằng máy (`--style-selftest`): mẫu "2.5D" phải ĐẠT,
# hai mẫu lỗi (A = vector phẳng, B = cartoon viền dày) phải TRƯỢT. Xem ART_REDRAW_PLAN §4.5b.
STYLE_BANDS: dict[str, dict[str, tuple[float, float]]] = {
    "ship":   {"grad_stops": (6, 25), "outline_px": (0.0, 1.5), "detail": (0.05, 0.30)},
    "drone":  {"grad_stops": (5, 25), "outline_px": (0.0, 1.5), "detail": (0.04, 0.30)},
    "boss":   {"grad_stops": (7, 25), "outline_px": (0.0, 1.5), "detail": (0.06, 0.32)},
    "enemy":  {"grad_stops": (5, 25), "outline_px": (0.0, 1.5), "detail": (0.04, 0.28)},
    "bullet": {"grad_stops": (3, 12), "outline_px": (0.0, 2.0), "detail": (0.02, 0.30)},
    "ui":     {"grad_stops": (4, 14), "outline_px": (0.0, 1.2), "detail": (0.02, 0.20)},
    "fx":     {"grad_stops": (4, 16), "outline_px": (0.0, 0.5), "detail": (0.03, 0.40)},
    "bg":     {"grad_stops": (8, 25), "outline_px": (0.0, 0.5), "detail": (0.03, 0.20)},
    "item":   {"grad_stops": (5, 18), "outline_px": (0.0, 1.2), "detail": (0.04, 0.25)},
}

# tham số đo style — ghi ở đây để người kiểm đổi được mà không phải đọc code
DARK_VAL = 0.18        # = 45/255, khớp định nghĩa `dark` của §4.9
DETAIL_RANGE = 0.10    # biên độ 3×3 tối thiểu để 1 pixel tính là "chi tiết"
GRAD_BIN = 0.02        # bề rộng một bậc sáng khi đếm gradient-stop
GRAD_MIN_SHARE = 0.008 # một bậc chỉ được đếm nếu chiếm ≥ 0,8 % pixel đục
OUTLINE_CAP = 8        # trần độ dày viền đo được (px)

TOL_PUBLISHED = 0.002


def hsv_v_s(rgb: tuple[int, int, int]) -> tuple[float, float]:
    """Trả (V, S) theo định nghĩa HSV thường dùng (0..1)."""
    r, g, b = (c / 255.0 for c in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    s = 0.0 if mx == 0 else (mx - mn) / mx
    return mx, s


def metrics_from_pixels(pixels: list[tuple[int, int, int]]) -> dict[str, float]:
    """val · val_std · dark · chroma · colors theo §4.9."""
    vs, ss = [], []
    for rgb in pixels:
        v, s = hsv_v_s(rgb)
        vs.append(v)
        ss.append(s)
    dark = sum(1 for p in pixels if max(p) < 45) / len(pixels)
    chroma_all = statistics.fmean(s * v for s, v in zip(ss, vs))
    quant = {(r >> 3, g >> 3, b >> 3) for r, g, b in pixels}
    return {
        "val": statistics.fmean(vs),
        "val_std": statistics.pstdev(vs),
        "dark": dark,
        "chroma": chroma_all,
        "colors": float(len(quant)),
        "sat_v25": statistics.fmean([s for s, v in zip(ss, vs) if v >= 0.25] or [0.0]),
    }


def grid_from_image(img) -> tuple[list[float], list[bool], int, int]:
    """(val, mask, w, h) — val = max(R,G,B)/255 theo §4.9, mask = alpha > 0,5."""
    w, h = img.size
    r, g, b, a = (band.tobytes() for band in img.split())
    vals = [max(rr, gg, bb) / 255.0 for rr, gg, bb in zip(r, g, b)]
    mask = [aa > 127 for aa in a]
    return vals, mask, w, h


def style_metrics(vals: list[float], mask: list[bool], w: int, h: int) -> dict[str, float]:
    """Ba chỉ số style 2.5D mà bản v1 của kế hoạch còn thiếu.

    grad_stops  = số bậc sáng (rộng 0,02) chiếm ≥ 0,8 % pixel đục — proxy cho
                  "gradient ≥ 3–5 mức/panel" của lần-149. Art phẳng chỉ có 2–4.
    outline_px  = độ dày trung bình (px) của dải tối đi vào trong từ biên silhouette.
                  Viền đen dày của lỗi B cho 4–8; render 2.5D có rim-light cho ≈ 0–1,5.
    dark_edge   = tỉ lệ pixel biên có V < 0,30 (chỉ để đọc, không chấm một mình).
    detail      = tỉ lệ pixel đục có biên độ 3×3 ≥ 0,10 — panel-line/khe tản nhiệt/rivet.
    """
    opaque = sum(1 for m in mask if m)
    if not opaque:
        raise ValueError("không có pixel alpha > 0,5")

    bins = [0] * 50
    for v, m in zip(vals, mask):
        if m:
            k = int(v / GRAD_BIN)
            bins[49 if k > 49 else k] += 1
    grad = float(sum(1 for c in bins if c / opaque >= GRAD_MIN_SHARE))

    boundary: list[tuple[int, int]] = []
    for y in range(h):
        row = y * w
        for x in range(w):
            i = row + x
            if not mask[i]:
                continue
            if (x == 0 or y == 0 or x == w - 1 or y == h - 1
                    or not mask[i - 1] or not mask[i + 1]
                    or not mask[i - w] or not mask[i + w]):
                boundary.append((x, y))

    dark_b = [(x, y) for x, y in boundary if vals[y * w + x] < DARK_VAL]
    dark_edge = len(dark_b) / len(boundary) if boundary else 0.0

    depths: list[int] = []
    for x, y in dark_b:
        inner: list[int] = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            # chỉ tính hướng đi VÀO trong: bước đầu phải vẫn nằm trong mask
            if not (0 <= nx < w and 0 <= ny < h) or not mask[ny * w + nx]:
                continue
            cx, cy, d = x, y, 0
            while d < OUTLINE_CAP:
                cx += dx
                cy += dy
                if not (0 <= cx < w and 0 <= cy < h):
                    break
                j = cy * w + cx
                if not mask[j] or vals[j] >= DARK_VAL:
                    break
                d += 1
            inner.append(d)
        depths.append(min(inner) if inner else 0)
    outline = sum(depths) / len(depths) if depths else 0.0

    # "chi tiết" chỉ tính trên RUỘT sprite: cách biên ≥ 3 px, bỏ chính pixel viền tối.
    # Nếu không, một mảng phẳng có viền dày cũng bị tính là "nhiều chi tiết".
    tot = hot = 0
    for y in range(3, h - 3):
        row = y * w
        for x in range(3, w - 3):
            i = row + x
            if not mask[i] or vals[i] < DARK_VAL:
                continue
            edge = False
            for dy in (-3, 0, 3):
                for dx in (-3, 0, 3):
                    if not mask[i + dy * w + dx]:
                        edge = True
                        break
                if edge:
                    break
            if edge:
                continue
            lo, hi = 2.0, -1.0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    j = i + dy * w + dx
                    if mask[j]:
                        v = vals[j]
                        if v < lo:
                            lo = v
                        if v > hi:
                            hi = v
            tot += 1
            if hi - lo >= DETAIL_RANGE:
                hot += 1
    detail = hot / tot if tot else 0.0

    return {"grad_stops": grad, "outline_px": round(outline, 2),
            "dark_edge": round(dark_edge, 3), "detail": round(detail, 3)}


def _lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(round(a[k] + (b[k] - a[k]) * t)) for k in range(3))  # type: ignore[return-value]


def _archetype(kind: str):
    """Ba mẫu dựng bằng máy, CÙNG silhouette, khác kỹ thuật render.

    flat    = lỗi A (vector phẳng): 2 mảng phẳng + viền 1 px.
    cartoon = lỗi B: viền đen dày 6 px + mảng phẳng.
    metal   = chuẩn 2.5D: ramp 5 bậc + AO 1 px + rim-light trên + panel-line + rivet.
    """
    from PIL import Image, ImageDraw

    size = 128
    hull = [(64, 10), (104, 44), (112, 96), (64, 118), (16, 96), (24, 44)]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def hull_mask():
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).polygon(hull, fill=255)
        return m

    if kind == "flat":
        d.polygon(hull, fill=PALETTE["ink500"])
        d.rectangle((44, 44, 84, 84), fill=PALETTE["ink300"])
        d.line(hull + [hull[0]], fill=PALETTE["ink900"], width=1)
    elif kind == "cartoon":
        d.polygon(hull, fill=PALETTE["ink300"])
        d.rectangle((44, 44, 84, 84), fill=PALETTE["paper"])
        d.line(hull + [hull[0]], fill=PALETTE["ink900"], width=6)
    elif kind == "metal":
        ramp = Image.new("RGB", (size, size))
        rd = ImageDraw.Draw(ramp)
        lo, hi = PALETTE["ink500"], PALETTE["paper"]
        stops = 5
        for b in range(stops):
            col = _lerp(lo, hi, b / (stops - 1))
            y0 = 8 + b * 22
            rd.rectangle((0, y0, size, y0 + 21), fill=col)
        img.paste(ramp, (0, 0), hull_mask())
        d2 = ImageDraw.Draw(img)
        # panel-line + rivet (chi tiết cơ khí)
        for y in range(28, 112, 12):
            d2.line((20, y, 108, y), fill=PALETTE["ink700"], width=1)
        for x, y in ((40, 34), (64, 34), (88, 34), (52, 96), (76, 96)):
            d2.ellipse((x - 2, y - 2, x + 2, y + 2), fill=PALETTE["paper"])
        # rim-light trên
        d2.line([(40, 26), (64, 14), (88, 26)], fill=PALETTE["paper"], width=3)
        # AO: 1 px tối sát biên
        d2.line(hull + [hull[0]], fill=PALETTE["ink900"], width=1)
    else:
        raise ValueError(kind)
    return img


ARCHETYPES = ("flat", "cartoon", "metal")


def run_style_selftest(verbose: bool = True) -> int:
    """Chứng minh 3 chỉ số TÁCH ĐƯỢC 3 kỹ thuật render — bằng số, không bằng cảm giác."""
    if verbose:
        print(f"{'mẫu':8s} {'grad_stops':>10s} {'outline_px':>10s} {'dark_edge':>9s} "
              f"{'detail':>7s}   §4.5b")
    got: dict[str, dict[str, float]] = {}
    for kind in ARCHETYPES:
        vals, mask, w, h = grid_from_image(_archetype(kind).convert("RGBA"))
        got[kind] = style_metrics(vals, mask, w, h)
        band = STYLE_BANDS["ship"]
        ok = all(in_band(got[kind][k], band[k])
                 for k in ("grad_stops", "outline_px", "detail"))
        if verbose:
            print(f"{kind:8s} {got[kind]['grad_stops']:10.0f} {got[kind]['outline_px']:10.2f} "
                  f"{got[kind]['dark_edge']:9.3f} {got[kind]['detail']:7.3f}   "
                  f"{'ĐẠT' if ok else 'TRƯỢT'}")
    fails = 0
    checks = [
        ("2.5D đạt dải `ship`", all(in_band(got["metal"][k], STYLE_BANDS["ship"][k])
                                    for k in ("grad_stops", "outline_px", "detail")), True),
        ("A-flat trượt ở grad_stops",
         in_band(got["flat"]["grad_stops"], STYLE_BANDS["ship"]["grad_stops"]), False),
        ("detail 2.5D ≥ 3× detail A-flat",
         got["metal"]["detail"] >= 3 * got["flat"]["detail"], True),
        ("B-cartoon trượt ở outline_px",
         in_band(got["cartoon"]["outline_px"], STYLE_BANDS["ship"]["outline_px"]), False),
        ("outline B-cartoon > 2×2.5D",
         got["cartoon"]["outline_px"] > 2 * max(got["metal"]["outline_px"], 0.3), True),
        ("grad 2.5D > grad B-cartoon",
         got["metal"]["grad_stops"] > got["cartoon"]["grad_stops"], True),
        ("detail 2.5D > detail A-flat",
         got["metal"]["detail"] > got["flat"]["detail"], True),
    ]
    print()
    for name, actual, want in checks:
        ok = actual == want
        print(f"  {'OK ' if ok else 'FAIL'} {name:36s} got {actual!r}  want {want!r}")
        fails += not ok
    print()
    if fails:
        print(f"✗ {fails} phép kiểm style trượt — sửa NGƯỠNG, rồi ghi lại §4.5b")
        return 1
    print("✓ 3 chỉ số tách đúng 3 kỹ thuật render: 2.5D ĐẠT, A (phẳng) và B (viền dày) TRƯỢT.")
    return 0


def recipe_pixels(recipe: str) -> list[tuple[int, int, int]]:
    """Dựng mẫu pixel theo tỉ lệ diện tích của công thức (§4.5) — 1 đơn vị = 1 pixel."""
    out: list[tuple[int, int, int]] = []
    for name, weight in RECIPES[recipe].items():
        out.extend([PALETTE[name]] * weight)
    if sum(RECIPES[recipe].values()) != 100:
        raise ValueError(f"{recipe}: tỉ lệ không cộng 100")
    return out


def in_band(value: float, band: tuple[float, float]) -> bool:
    return band[0] - 1e-9 <= value <= band[1] + 1e-9


def run_recipe_selftest(verbose: bool = True) -> int:
    fails = 0
    print(f"{'recipe':8s} {'val':>6s} {'val_std':>8s} {'dark':>6s} {'chroma':>7s}   §4.5   §4.3")
    for name in RECIPES:
        m = metrics_from_pixels(recipe_pixels(name))
        pub = PUBLISHED[name]
        same = all(abs(m[k] - want) <= TOL_PUBLISHED
                   for k, want in zip(("val", "val_std", "dark", "chroma"), pub))
        band_ok = all(in_band(m[k], BANDS[name][k])
                      for k in ("val", "val_std", "dark", "chroma"))
        print(f"{name:8s} {m['val']:6.3f} {m['val_std']:8.3f} {m['dark']:6.3f} {m['chroma']:7.3f}   "
              f"{'khớp' if same else 'LỆCH':6s} {'trong dải' if band_ok else 'RA NGOÀI'}")
        if verbose and not same:
            print(f"         §4.5 công bố: val {pub[0]:.3f} · val_std {pub[1]:.3f} · "
                  f"dark {pub[2]:.3f} · chroma {pub[3]:.3f}")
        if not band_ok:
            for k in ("val", "val_std", "dark", "chroma"):
                if not in_band(m[k], BANDS[name][k]):
                    print(f"         ngoài dải §4.3: {k} = {m[k]:.3f} ∉ "
                          f"[{BANDS[name][k][0]:.2f}, {BANDS[name][k][1]:.2f}]")
        fails += (not same) + (not band_ok)
    print()
    if fails:
        print(f"✗ {fails} điểm lệch — sửa **tỉ lệ công thức**, đừng sửa bảng (§4.5)")
        return 1
    print("✓ 9/9 công thức: tái lập đúng số §4.5 và nằm trong dải mục tiêu §4.3 "
          "(trên 4 chỉ số đo được; `colors` chỉ đếm được trên art thật)")
    return 0


def measure_png(path: pathlib.Path) -> dict[str, float]:
    from PIL import Image  # import trễ: --recipe không cần Pillow

    img = Image.open(path).convert("RGBA")
    r, g, b, a = (band.tobytes() for band in img.split())
    px = [(rr, gg, bb) for rr, gg, bb, aa in zip(r, g, b, a) if aa > 127]  # mask = alpha > 0,5
    if not px:
        raise ValueError(f"{path.name}: không có pixel alpha > 0,5")
    m = metrics_from_pixels(px)
    m["fill"] = round(len(px) / (img.width * img.height), 3)
    vals, mask, w, h = grid_from_image(img)
    m.update(style_metrics(vals, mask, w, h))
    return m


def run_dir(folder: pathlib.Path, cls: str | None, style: bool = False) -> int:
    files = sorted(folder.glob("*.png"))
    if not files:
        print(f"✗ không có .png trong {folder}")
        return 1
    bands = BANDS.get(cls) if cls else None
    if cls and not bands:
        print(f"✗ --class phải là một trong: {', '.join(BANDS)}")
        return 1
    sbands = STYLE_BANDS.get(cls) if cls else None
    bad_files: set[str] = set()
    extra = f" {'grad':>5s} {'outl':>5s} {'detail':>7s}" if style else ""
    print(f"{'file':34s} {'colors':>6s} {'val':>6s} {'val_std':>8s} {'dark':>6s} "
          f"{'chroma':>7s} {'fill':>6s}{extra}")
    for f in files:
        try:
            m = measure_png(f)
        except Exception as exc:  # noqa: BLE001 - in lỗi rồi đi tiếp
            print(f"{f.name:34s} LỖI: {exc}")
            bad_files.add(f.name)
            continue
        flag = ""
        if bands:
            bad_m = [k for k in ("colors", "val", "val_std", "dark", "chroma")
                     if not in_band(m[k], bands[k])]
            if bad_m:
                bad_files.add(f.name)
                flag = "  ← lệch: " + ", ".join(
                    f"{k}={m[k]:.3f}∉[{bands[k][0]:.2f},{bands[k][1]:.2f}]" if k != "colors"
                    else f"colors={int(m['colors'])}∉[{bands[k][0]:.0f},{bands[k][1]:.0f}]"
                    for k in bad_m)
        if style and sbands:
            bad_style = [k for k in ("grad_stops", "outline_px", "detail")
                         if not in_band(m[k], sbands[k])]
            if bad_style:
                bad_files.add(f.name)
                flag += "  ← style lệch: " + ", ".join(
                    f"{k}={m[k]:.2f}∉[{sbands[k][0]:g},{sbands[k][1]:g}]" for k in bad_style)
        line = f"{f.name:34s} {int(m['colors']):6d} {m['val']:6.3f} {m['val_std']:8.3f} " \
               f"{m['dark']:6.3f} {m['chroma']:7.3f} {m['fill']:6.3f}"
        if style:
            line += f" {m['grad_stops']:5.0f} {m['outline_px']:5.2f} {m['detail']:7.3f}"
        print(line + flag)
    print()
    if bad_files:
        print(f"✗ {len(bad_files)}/{len(files)} asset lệch — sửa art, không sửa dải")
        return 1
    print(f"✓ {len(files)}/{len(files)} asset trong dải" + (f" của nhóm `{cls}`" if cls else ""))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đo sprite theo giao thức §4.9 của ART_REDRAW_PLAN")
    ap.add_argument("--recipe", action="store_true", help="tái lập 9 công thức tô (§4.5) — không cần Pillow")
    ap.add_argument("--dir", type=pathlib.Path, help="thư mục chứa PNG cần đo")
    ap.add_argument("--class", dest="cls", help=f"nhóm để chấm dải §4.3: {', '.join(BANDS)}")
    ap.add_argument("--style", action="store_true",
                    help="in + chấm 3 chỉ số 2.5D (grad_stops · outline_px · detail) — cần --class")
    ap.add_argument("--style-selftest", action="store_true",
                    help="dựng 3 mẫu (phẳng · cartoon viền dày · 2.5D) và chứng minh 3 chỉ số tách được")
    args = ap.parse_args(argv)

    if args.style_selftest:
        return run_style_selftest()
    if args.recipe and not args.dir:
        return run_recipe_selftest()
    if args.dir:
        return run_dir(args.dir, args.cls, args.style)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
