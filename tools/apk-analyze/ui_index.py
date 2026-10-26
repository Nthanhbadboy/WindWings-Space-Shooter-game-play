#!/usr/bin/env python3
"""Lập danh mục **mọi** file layout UI đang có trong `reverse-engineering/raw/ui/`.

Vì sao cần: `_index.csv` chỉ liệt kê file do **lần chạy gần nhất** sinh ra (630 file),
trong khi trên đĩa còn 6.5k file từ các lần trước — trong đó có **16 màn chỉ tồn tại ở
các file cũ** (`Board_Shop`, `Board_Pause`, `Board_Drones`…). Bỏ qua chúng là mất dữ liệu.
Tool này đọc hết, không xoá gì, và xuất:

  datas/ui_screens.json        mỗi file: class, node, text, button, key, bbox
  docs/apk-analysis/24-ui-screens.md  bảng theo màn (98 màn)
  datas/ui_text_keys.csv       text + localization key theo màn/đường dẫn node

Chạy offline, không cần APK. Mọi số là **kết luận tạm thời** (prefab ≠ runtime).
"""
from __future__ import annotations

import csv
import glob
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

SRC = os.environ.get("UI_RAW", "reverse-engineering/raw/ui")
OUT_JSON = os.environ.get("UI_SCREENS_JSON", "datas/ui_screens.json.gz")
OUT_MD = os.environ.get("UI_SCREENS_MD", "docs/apk-analysis/24-ui-screens.md")
OUT_CSV = os.environ.get("UI_TEXT_CSV", "datas/ui_text_keys.csv.gz")


def world_pos(paths, node):
    """Cộng dồn local_pos theo chuỗi cha (scale/rotation coi như identity).

    Chỉ để so sánh tương đối giữa các node trong cùng màn — prefab là world-space
    nên toạ độ gốc đã là "unit thế giới", không phải pixel.
    """
    x = y = 0.0
    cur = node
    guard = 0
    while cur is not None and guard < 64:
        guard += 1
        lp = cur.get("local_pos") or (0.0, 0.0, 0.0)
        try:
            x += float(lp[0])
            y += float(lp[1])
        except (TypeError, ValueError, IndexError):
            pass
        parent = cur["path"].rsplit("/", 1)[0] if "/" in cur.get("path", "") else None
        cur = paths.get(parent)
    return round(x, 2), round(y, 2)


def summarise(path):
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    nodes = data.get("nodes") or []
    cls = data.get("class") or os.path.basename(path).split("__")[0]
    paths = {n.get("path"): n for n in nodes}

    comp_classes: Counter = Counter()
    texts, keys = [], []
    sprites, buttons = [], 0
    for n in nodes:
        for c in n.get("components") or []:
            cname = c.get("class", "?")
            comp_classes[cname] += 1
            if "Button" in cname:
                buttons += 1
            if c.get("text"):
                texts.append((n.get("path", ""), cname, c["text"], c.get("key", "")))
            elif c.get("key"):
                keys.append((n.get("path", ""), cname, c["key"]))
            if c.get("sprite"):
                sprites.append(c["sprite"])

    xs, ys = [], []
    for n in nodes:
        if n.get("local_pos") is None:
            continue
        wx, wy = world_pos(paths, n)
        xs.append(wx)
        ys.append(wy)

    return {
        "class": cls,
        "file": os.path.basename(path),
        "root_path_id": data.get("root_path_id"),
        "nodes": len(nodes),
        "components": dict(comp_classes.most_common()),
        "texts": texts,
        "keys": keys,
        "buttons": buttons,
        "sprites": len(set(sprites)),
        "bbox": [min(xs), min(ys), max(xs), max(ys)] if xs else None,
        "bytes": os.path.getsize(path),
    }


def main() -> int:
    files = sorted(glob.glob(os.path.join(SRC, "*.json.gz")))
    if not files:
        print(f"không có file trong {SRC}")
        return 0

    rows, text_rows = [], []
    by_class: dict = defaultdict(list)
    for path in files:
        s = summarise(path)
        if not s:
            continue
        rows.append({k: v for k, v in s.items() if k not in ("texts", "keys")})
        by_class[s["class"]].append(s)
        seen = set()
        for npath, cname, text, key in s["texts"]:
            k = (npath, text)
            if k in seen:
                continue
            seen.add(k)
            text_rows.append([s["class"], s["root_path_id"], npath, cname, text, key])
        for npath, cname, key in s["keys"]:
            if (npath, key) in seen:
                continue
            seen.add((npath, key))
            text_rows.append([s["class"], s["root_path_id"], npath, cname, "", key])

    total_nodes = sum(r["nodes"] for r in rows)
    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    payload = {"note": "Kết luận tạm thời. Mỗi dòng = 1 file layout trong raw/ui.",
               "files": len(rows), "nodes": total_nodes, "screens": rows}
    with gzip.open(OUT_JSON, "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))

    os.makedirs(os.path.dirname(OUT_CSV) or ".", exist_ok=True)
    with gzip.open(OUT_CSV, "wt", newline="", encoding="utf-8", compresslevel=9) as fh:
        w = csv.writer(fh)
        w.writerow(["class", "root_path_id", "node_path", "component", "text", "key"])
        w.writerows(text_rows)

    write_md(by_class, rows, text_rows)
    print(f"{len(rows)} file, {len(by_class)} màn, {total_nodes:,} node, "
          f"{len(text_rows):,} dòng text/key -> {OUT_JSON}")
    return 0


def write_md(by_class, rows, text_rows):
    L = ["# 24 — Danh mục layout UI (kết luận tạm thời)", "",
         "> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,",
         "> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →",
         "> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.",
         "",
         "Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể",
         "khác — chưa đối chiếu screenshot.", "",
         f"- file: **{len(rows)}**, màn (class): **{len(by_class)}**, node: **{sum(r['nodes'] for r in rows):,}**",
         f"- dòng text/key: **{len(text_rows):,}** (CSV.gz: `datas/ui_text_keys.csv.gz`)", "",
         "## Theo màn", "",
         "| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |",
         "|---|---:|---:|---:|---:|---:|---:|---|---|"]

    rows_sorted = []
    for cls, items in by_class.items():
        best = max(items, key=lambda r: r["nodes"])
        texts = len({t[2] for i in items for t in i["texts"]})
        keys = len({k[2] for i in items for k in i["keys"]})
        buttons = max(i["buttons"] for i in items)
        sprites = max(i["sprites"] for i in items)
        bbox = best.get("bbox")
        rows_sorted.append((cls, len(items), best["nodes"], texts, keys, buttons, sprites,
                            bbox[0] if bbox else None, bbox[2] if bbox else None,
                            bbox[1] if bbox else None, bbox[3] if bbox else None))
    for r in sorted(rows_sorted, key=lambda r: -r[2]):
        L.append(f"| `{r[0]}` | {r[1]} | {r[2]:,} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | "
                 f"{r[7]}…{r[8]} | {r[9]}…{r[10]} |")

    # Camera: nếu đã export native-types thì lấy orthographicSize thật,
    # đây là mốc đổi world-unit -> màn hình (chiều cao thấy được = 2 x size).
    cam_note = []
    cam_path = os.path.join(os.path.dirname(SRC.rstrip("/")), "typetrees", "native-types.jsonl.gz")
    if os.path.isfile(cam_path):
        sizes = []
        try:
            with gzip.open(cam_path, "rt", encoding="utf-8") as fh:
                for line in fh:
                    rec = json.loads(line)
                    if rec.get("type") == "Camera":
                        sizes.append(rec.get("orthographic size"))
        except (OSError, ValueError):
            sizes = []
        sizes = [v for v in sizes if isinstance(v, (int, float))]
        if sizes:
            cam_note = ["", "## Camera (đo từ prefab, mức A)", "",
                        f"- số Camera trong build: **{len(sizes)}**, tất cả orthographic",
                        f"- `orthographicSize` = **{round(sizes[0], 3)}** → chiều cao vùng thấy được = **{round(2 * sizes[0], 3)} world-unit**",
                        "- khớp mốc spawn `y = 9,6` trong dữ liệu wave: quân hiện ở đúng mép trên màn hình.",
                        "- đổi sang pixel: `px = world / (2 × 9,6) × screenHeight`."]

    big = [r for r in rows_sorted if r[7] is not None]
    if big:
        widths = sorted({round(r[8] - r[7], 1) for r in big})
        heights = sorted({round(r[10] - r[9], 1) for r in big})
        L += ["", "## Hệ toạ độ (suy ra từ bbox, mức C)", "",
              f"- bề rộng bbox phổ biến: `{widths[:3]} … {widths[-3:]}`",
              f"- chiều cao bbox phổ biến: `{heights[:3]} … {heights[-3:]}`",
              "- toạ độ là **unit world-space của prefab**, không phải pixel màn hình;",
              "  muốn ra pixel phải nhân với `orthographicSize` của camera runtime (chưa bóc được).",
              "- vì vậy mọi con số ở đây dùng để **so sánh tỉ lệ giữa các màn**, không phải để đặt pixel."]

    L += cam_note
    L += ["", "## Text & localization key", ""]
    per_class = Counter(r[0] for r in text_rows)
    with_key = Counter(r[0] for r in text_rows if r[5])
    L += ["| màn | dòng text | có key | % có key |", "|---|---:|---:|---:|"]
    for cls, n in per_class.most_common(25):
        k = with_key.get(cls, 0)
        L.append(f"| `{cls}` | {n} | {k} | {100.0 * k / n if n else 0:.0f}% |")
    L += ["", "## Còn thiếu", "",
          "- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`",
          "  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.",
          "- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.",
          "- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.",
          ""]

    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
