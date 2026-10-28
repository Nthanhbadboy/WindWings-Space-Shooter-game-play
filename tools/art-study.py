#!/usr/bin/env python3
"""art-study.py — đo **mẫu gốc** (contact sheet của atlas) để học thiết kế, không chép hình.

Vì sao: "phong cách" phải thành số thì mới dùng được. Tool này đọc từng ô sprite trong
42 contact sheet (`docs/assets/contact-sheets/`), tách nền caro, rồi đo:

* khung hình sprite (rộng:cao), độ lấp đầy ô
* số màu phân biệt (kỷ luật palette), top-3 màu và tỉ lệ
* độ bão hoà / độ sáng trung bình, độ lệch sáng trong sprite (flat hay gradient)
* tỉ lệ pixel gần đen trong sprite (**outline**) — chỉ đo trên ô nền xám để không lẫn nền đen

Cần ImageMagick (`convert`) để giải JPEG; phần còn lại là Python thuần.

Chạy:  python3 tools/art-study.py [--csv docs/assets/art-study.csv] [--limit-sheets N]
"""
from __future__ import annotations

import collections
import csv
import os
import subprocess
import sys

INDEX = "docs/assets/sprites-index.csv"
SHEETS = "docs/assets/contact-sheets"
COLS = 8


def ppm(path: str):
    """(w, h, bytes RGB) — ImageMagick giải JPEG rồi đọc PPM nhị phân."""
    out = subprocess.run(["convert", path, "-depth", "8", "ppm:-"],
                         capture_output=True, check=True).stdout
    # header: P6\n<w> <h>\n255\n
    parts = out.split(b"\n", 3)
    if parts[0].strip() != b"P6":
        raise ValueError("không phải PPM P6: " + path)
    w, h = (int(x) for x in parts[1].split())
    return w, h, parts[3]


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def _is_bg(px, iw, x, y, tones, tol):
    i = (y * iw + x) * 3
    c = (px[i], px[i + 1], px[i + 2])
    return min(_dist(c, tones[0]), _dist(c, tones[1])) < tol


def bg_mask(px, iw, x0, y0, cell, tones, tol=60):
    """Nền = vùng màu caro **nối với viền ô** (flood fill).

    Vì sao phải flood fill: một trong hai màu caro là gần đen, nên nếu chỉ so màu
    thì **outline đen của sprite bị ăn mất**. Nhờ nối-với-viền, mảng đen nằm trong
    sprite không bị coi là nền nữa.
    """
    bg = bytearray(cell * cell)
    stack = []
    for x in range(cell):
        for y in (0, cell - 1):
            if not bg[y * cell + x] and _is_bg(px, iw, x0 + x, y0 + y, tones, tol):
                bg[y * cell + x] = 1
                stack.append((x, y))
    for y in range(cell):
        for x in (0, cell - 1):
            if not bg[y * cell + x] and _is_bg(px, iw, x0 + x, y0 + y, tones, tol):
                bg[y * cell + x] = 1
                stack.append((x, y))
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < cell and 0 <= ny < cell and not bg[ny * cell + nx] \
                    and _is_bg(px, iw, x0 + nx, y0 + ny, tones, tol):
                bg[ny * cell + nx] = 1
                stack.append((nx, ny))
    return bg


def measure_tile(px, iw, x0, y0, cell, tones, stride=2):
    """Đo một ô sprite. Nền xác định bằng flood fill từ viền ô."""
    bg = bg_mask(px, iw, x0, y0, cell, tones)
    hist = collections.Counter()
    n = sat = lum = 0.0
    cnt = 0
    dark = 0
    lums = []
    xmin, xmax, ymin, ymax = cell, -1, cell, -1
    for y in range(0, cell, stride):
        for x in range(0, cell, stride):
            if bg[y * cell + x]:
                continue
            i = ((y0 + y) * iw + x0 + x) * 3
            r, g, b = px[i], px[i + 1], px[i + 2]
            c = (r, g, b)
            cnt += 1
            if x < xmin:
                xmin = x
            if x > xmax:
                xmax = x
            if y < ymin:
                ymin = y
            if y > ymax:
                ymax = y
            mx, mn = max(c), min(c)
            s = 0.0 if mx == 0 else (mx - mn) / mx
            v = mx / 255.0
            sat += s
            lum += v
            lums.append(v)
            if mx < 45:
                dark += 1
            hist[(r >> 5 << 5, g >> 5 << 5, b >> 5 << 5)] += 1
    if cnt < 30:
        return None
    comps = components(bg, cell)
    lums.sort()
    std = (sum((v - lum / cnt) ** 2 for v in lums) / cnt) ** 0.5
    top = hist.most_common(3)
    return {
        "px": cnt,
        "bbox_w": xmax - xmin + 1,
        "bbox_h": ymax - ymin + 1,
        "aspect": round((xmax - xmin + 1) / max(ymax - ymin + 1, 1), 3),
        "fill": round(cnt * stride * stride / (cell * cell), 3),
        "colors": len(hist),
        "sat": round(sat / cnt, 3),
        "val": round(lum / cnt, 3),
        "val_std": round(std, 3),
        "dark_share": round(dark / cnt, 3),
        "top_share": round(top[0][1] / cnt, 3) if top else 0.0,
        "top_hex": "#%02x%02x%02x" % top[0][0] if top else "",
        "ncomp": len(comps),
        "comps": ";".join(f"{x},{y},{w},{h},{a}" for x, y, w, h, a in comps[:8]),
    }


def components(bg, cell, min_area=20, keep=8):
    """Các cụm pixel không-phải-nền (4 hướng), trả [(x,y,w,h,area)] lớn trước.

    Dùng để (a) phát hiện sprite thật ra là **sheet nhiều hình**, và (b) lấy rect
    để tách. Toạ độ theo ô contact sheet.
    """
    seen = bytearray(cell * cell)
    out = []
    for sy in range(cell):
        for sx in range(cell):
            p0 = sy * cell + sx
            if bg[p0] or seen[p0]:
                continue
            seen[p0] = 1
            stack = [(sx, sy)]
            n = 0
            x0 = x1 = sx
            y0 = y1 = sy
            while stack:
                x, y = stack.pop()
                n += 1
                if x < x0:
                    x0 = x
                if x > x1:
                    x1 = x
                if y < y0:
                    y0 = y
                if y > y1:
                    y1 = y
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < cell and 0 <= ny < cell:
                        q = ny * cell + nx
                        if not bg[q] and not seen[q]:
                            seen[q] = 1
                            stack.append((nx, ny))
            if n >= min_area:
                out.append((x0, y0, x1 - x0 + 1, y1 - y0 + 1, n))
    out.sort(key=lambda t: -t[4])
    return out


def main(argv):
    out_csv = "docs/assets/art-study.csv"
    limit = None
    if "--csv" in argv:
        out_csv = argv[argv.index("--csv") + 1]
    if "--limit-sheets" in argv:
        limit = int(argv[argv.index("--limit-sheets") + 1])

    rows = list(csv.DictReader(open(INDEX, encoding="utf-8")))
    by_sheet = collections.defaultdict(list)
    for r in rows:
        if r.get("contact_sheet") and r.get("tile"):
            by_sheet[r["contact_sheet"]].append(r)

    results = []
    sheets = sorted(by_sheet)[:limit] if limit else sorted(by_sheet)
    for sh in sheets:
        path = os.path.join(SHEETS, sh)
        if not os.path.isfile(path):
            continue
        try:
            iw, ih, px = ppm(path)
        except (subprocess.CalledProcessError, ValueError) as e:
            print("bỏ qua", sh, ":", e)
            continue
        cell = iw // COLS
        # 2 màu nền caro = 2 màu phổ biến nhất trong dải 4 px đầu
        tones = collections.Counter()
        for y in range(0, min(ih, cell), 2):
            for x in range(0, iw, 2):
                i = (y * iw + x) * 3
                tones[(px[i], px[i + 1], px[i + 2])] += 1
        t = [c for c, _ in tones.most_common(2)]
        if len(t) < 2:
            continue
        for r in by_sheet[sh]:
            tile = int(r["tile"])
            if tile < 1:
                continue
            col = (tile - 1) % COLS
            row = (tile - 1) // COLS
            x0, y0 = col * cell, row * cell
            if x0 + cell > iw or y0 + cell > ih:
                continue
            m = measure_tile(px, iw, x0, y0, cell, t)
            if not m:
                continue
            m.update({"category": r["category"], "name": r["name"],
                      "sheet": sh, "tile": tile})
            results.append(m)
        print(f"{sh:22s} ô {cell:3d}px · {len(by_sheet[sh]):2d} sprite · nền {t[0]} + {t[1]}")

    if not results:
        print("không đo được ô nào")
        return 1
    cols = ["category", "name", "sheet", "tile", "px", "bbox_w", "bbox_h", "aspect",
            "fill", "colors", "sat", "val", "val_std", "dark_share", "top_share", "top_hex",
            "ncomp", "comps"]
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow({k: r[k] for k in cols})
    print("\nđã ghi", out_csv, "·", len(results), "sprite")

    # tổng hợp theo nhóm
    def med(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if xs else 0

    print(f"\n{'nhóm':14s} {'n':>5s} {'colors':>7s} {'sat':>6s} {'val':>6s} "
          f"{'val_std':>8s} {'dark':>6s} {'fill':>6s} {'aspect':>7s}")
    groups = collections.defaultdict(list)
    for r in results:
        groups[r["category"]].append(r)
    for cat in sorted(groups, key=lambda c: -len(groups[c])):
        g = groups[cat]
        print(f"{cat:14s} {len(g):5d} {med([r['colors'] for r in g]):7d} "
              f"{med([r['sat'] for r in g]):6.2f} {med([r['val'] for r in g]):6.2f} "
              f"{med([r['val_std'] for r in g]):8.2f} {med([r['dark_share'] for r in g]):6.2f} "
              f"{med([r['fill'] for r in g]):6.2f} {med([r['aspect'] for r in g]):7.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
