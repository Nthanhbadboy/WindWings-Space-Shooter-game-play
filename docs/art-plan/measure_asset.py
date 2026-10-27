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
    return m


def run_dir(folder: pathlib.Path, cls: str | None) -> int:
    files = sorted(folder.glob("*.png"))
    if not files:
        print(f"✗ không có .png trong {folder}")
        return 1
    bands = BANDS.get(cls) if cls else None
    if cls and not bands:
        print(f"✗ --class phải là một trong: {', '.join(BANDS)}")
        return 1
    fails = 0
    print(f"{'file':34s} {'colors':>6s} {'val':>6s} {'val_std':>8s} {'dark':>6s} {'chroma':>7s} {'fill':>6s}")
    for f in files:
        try:
            m = measure_png(f)
        except Exception as exc:  # noqa: BLE001 - in lỗi rồi đi tiếp
            print(f"{f.name:34s} LỖI: {exc}")
            fails += 1
            continue
        flag = ""
        if bands:
            bad = [k for k in ("colors", "val", "val_std", "dark", "chroma")
                   if not in_band(m[k], bands[k])]
            if bad:
                flag = "  ← lệch: " + ", ".join(
                    f"{k}={m[k]:.3f}∉[{bands[k][0]:.2f},{bands[k][1]:.2f}]" if k != "colors"
                    else f"colors={int(m['colors'])}∉[{bands[k][0]:.0f},{bands[k][1]:.0f}]"
                    for k in bad)
                fails += 1
        print(f"{f.name:34s} {int(m['colors']):6d} {m['val']:6.3f} {m['val_std']:8.3f} "
              f"{m['dark']:6.3f} {m['chroma']:7.3f} {m['fill']:6.3f}{flag}")
    print()
    if fails:
        print(f"✗ {fails}/{len(files)} asset lệch — sửa art, không sửa dải")
        return 1
    print(f"✓ {len(files)}/{len(files)} asset trong dải" + (f" của nhóm `{cls}`" if cls else ""))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Đo sprite theo giao thức §4.9 của ART_REDRAW_PLAN")
    ap.add_argument("--recipe", action="store_true", help="tái lập 9 công thức tô (§4.5) — không cần Pillow")
    ap.add_argument("--dir", type=pathlib.Path, help="thư mục chứa PNG cần đo")
    ap.add_argument("--class", dest="cls", help=f"nhóm để chấm dải §4.3: {', '.join(BANDS)}")
    args = ap.parse_args(argv)

    if args.recipe and not args.dir:
        return run_recipe_selftest()
    if args.dir:
        return run_dir(args.dir, args.cls)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
