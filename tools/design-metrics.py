#!/usr/bin/env python3
"""design-metrics.py — đo **yếu tố thiết kế** từ ảnh chụp thật (không cần PIL).

Vì sao có tool này: "đẹp" không phải ý kiến. Từ 35 ảnh chụp gameplay/UI của bản gốc
ta đo được những thứ tái dùng được cho bản mới: khung hình, bảng màu thật, độ tương
phản, mức bão hoà, mật độ chi tiết, và HUD nằm ở đâu.

Không dùng ảnh để **vẽ lại** asset (vi phạm bản quyền) — chỉ dùng để **đo tỉ lệ**.

Chạy:  python3 tools/design-metrics.py [thư mục] [--json out.json]
"""
from __future__ import annotations

import glob
import json
import os
import struct
import sys
import zlib

# ── giải PNG (chỉ 8-bit, không interlace: đủ cho ảnh chụp màn hình) ──────


def _chunks(blob: bytes):
    i = 8
    while i < len(blob):
        (ln,) = struct.unpack(">I", blob[i:i + 4])
        typ = blob[i + 4:i + 8]
        yield typ, blob[i + 8:i + 8 + ln]
        i += 12 + ln


def read_png(path: str):
    """(w, h, bpp, bytes) với bytes là RGB(A) đã bỏ filter."""
    blob = open(path, "rb").read()
    ihdr = next(d for t, d in _chunks(blob) if t == b"IHDR")
    w, h, depth, color, _comp, _filt, inter = struct.unpack(">IIBBBBB", ihdr)
    if depth != 8 or inter != 0 or color not in (2, 6):
        raise ValueError(f"{path}: chỉ hỗ trợ 8-bit RGB/RGBA không interlace")
    bpp = 4 if color == 6 else 3
    raw = zlib.decompress(b"".join(d for t, d in _chunks(blob) if t == b"IDAT"))
    stride = w * bpp
    out = bytearray(stride * h)
    prev = bytearray(stride)
    pos = 0
    for y in range(h):
        ft = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        if ft == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 0xFF
        elif ft == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 0xFF
        elif ft == 3:
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((left + prev[x]) >> 1)) & 0xFF
        elif ft == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, bpp, bytes(out)


# ── đo ────────────────────────────────────────────────────────────────

HUES = ["red", "orange", "yellow", "lime", "green", "spring",
        "cyan", "azure", "blue", "violet", "magenta", "rose"]


def _hsv(r: int, g: int, b: int):
    mx, mn = max(r, g, b), min(r, g, b)
    v = mx / 255.0
    s = 0.0 if mx == 0 else (mx - mn) / mx
    if mx == mn:
        return 0.0, s, v
    d = mx - mn
    if mx == r:
        hh = ((g - b) / d) % 6
    elif mx == g:
        hh = (b - r) / d + 2
    else:
        hh = (r - g) / d + 4
    return hh * 60.0, s, v


def measure(path: str, stride: int = 2):
    w, h, bpp, px = read_png(path)
    hist: dict[tuple[int, int, int], int] = {}
    hue_bins = [0] * 12
    n = 0
    s_sum = v_sum = 0.0
    lums: list[float] = []
    accent = 0
    band_sum = [0.0, 0.0, 0.0]
    band_n = [0, 0, 0]
    grad = 0
    grad_n = 0
    for y in range(0, h, stride):
        row = y * w * bpp
        for x in range(0, w, stride):
            i = row + x * bpp
            r, g, b = px[i], px[i + 1], px[i + 2]
            n += 1
            hh, s, v = _hsv(r, g, b)
            s_sum += s
            v_sum += v
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            lums.append(lum)
            if s > 0.6 and v > 0.6:
                accent += 1
            if s > 0.15:
                hue_bins[min(11, int(hh / 30))] += 1
            band = 0 if y < h * 0.15 else (2 if y > h * 0.85 else 1)
            band_sum[band] += lum
            band_n[band] += 1
            key = (r >> 4, g >> 4, b >> 4)
            hist[key] = hist.get(key, 0) + 1
            if x + stride < w:
                j = i + stride * bpp
                grad += abs(px[j] - r) + abs(px[j + 1] - g) + abs(px[j + 2] - b)
                grad_n += 1
    lums.sort()
    top = sorted(hist.items(), key=lambda kv: -kv[1])[:8]
    return {
        "file": os.path.basename(path),
        "w": w, "h": h, "aspect": round(w / h, 4),
        "pixels_sampled": n,
        "mean_saturation": round(s_sum / n, 4),
        "mean_value": round(v_sum / n, 4),
        "luminance_p05": round(lums[int(len(lums) * 0.05)] / 255, 4),
        "luminance_p50": round(lums[int(len(lums) * 0.50)] / 255, 4),
        "luminance_p95": round(lums[int(len(lums) * 0.95)] / 255, 4),
        "accent_share": round(accent / n, 4),
        "detail_gradient": round(grad / max(grad_n, 1), 2),
        "bands_luma": [round(band_sum[k] / max(band_n[k], 1) / 255, 3) for k in range(3)],
        "hue_share": {HUES[k]: round(v / max(sum(hue_bins), 1), 3)
                      for k, v in enumerate(hue_bins) if v},
        "palette": ["#%02x%02x%02x" % ((k[0] << 4) + 8, (k[1] << 4) + 8, (k[2] << 4) + 8)
                    for k, _ in top],
        "palette_share": [round(v / n, 3) for _, v in top],
    }


def main(argv: list[str]) -> int:
    root = argv[1] if len(argv) > 1 and not argv[1].startswith("-") else \
        "docs/apk-analysis/ramus/2026-10-23-phone"
    out = None
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
    files = sorted(glob.glob(os.path.join(root, "*.png")))
    if not files:
        print("không thấy ảnh trong", root)
        return 1
    rows = []
    for f in files:
        try:
            rows.append(measure(f))
        except ValueError as e:  # ảnh lạ: bỏ qua, không bịa số
            print("bỏ qua:", e)
    print(f"{'ảnh':28s} {'bão hoà':>8s} {'tương phản':>10s} {'accent':>7s} {'chi tiết':>9s}  dải sáng (trên/giữa/dưới)")
    for r in rows:
        print(f"{r['file'][:28]:28s} {r['mean_saturation']:8.3f} "
              f"{r['luminance_p95'] - r['luminance_p05']:10.3f} {r['accent_share']:7.3f} "
              f"{r['detail_gradient']:9.1f}  {r['bands_luma']}")
    if rows:
        mean = lambda k: round(sum(r[k] for r in rows) / len(rows), 4)
        print("\nTRUNG BÌNH:", {k: mean(k) for k in
                              ("mean_saturation", "mean_value", "accent_share", "detail_gradient")})
        print("khung hình:", {r["aspect"] for r in rows})
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=1)
        print("đã ghi", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
