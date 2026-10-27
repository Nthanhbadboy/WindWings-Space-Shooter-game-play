#!/usr/bin/env python3
"""Worklist art cho AI vẽ lại — sinh từ 04-asset-manifest.csv (2.185 Sprite).

Luật dedup (lần 19, 25/10 — pin để chạy lại được):
  1) glyph = tên ≤2 ký tự HOẶC toàn số → 1 bộ bitmap font, không vẽ từng cái.
  2) tên gốc: lowercase · bỏ `(n)` · bỏ đuôi số (2 lần, xử lý `_n`/`-n`/` n`) → 623 gốc.
  (DONE §1.6 ghi "~641" là ước lượng cũ — chênh 18 ≈ 2,8 %; dùng danh sách này cho việc vẽ.)
Đầu ra: docs/assets/art-worklist.csv (base_name · variants · example · max w/h).
"""
import csv, re
from collections import OrderedDict

SRC = "docs/apk-analysis/04-asset-manifest.csv"
OUT = "docs/assets/art-worklist.csv"


def is_glyph(n):
    s = n.strip().lower()
    return len(s) <= 2 or s.isdigit()


def base(n):
    s = n.strip().lower()
    s = re.sub(r"\((\d+)\)", "", s)
    s = re.sub(r"(\d+)$", "", s)
    s = re.sub(r"[_\- ]+$", "", s)
    s = re.sub(r"(\d+)$", "", s)
    return s or n.strip().lower()


def main():
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["type"] == "Sprite"]
    glyphs = [r for r in rows if is_glyph(r["name"])]
    rest = [r for r in rows if not is_glyph(r["name"])]
    groups = OrderedDict()
    for r in rest:
        groups.setdefault(base(r["name"]), []).append(r)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["base_name", "variants", "example_name", "max_width", "max_height"])
        for k, rs in sorted(groups.items()):
            dims = [(int(r["width"] or 0), int(r["height"] or 0)) for r in rs]
            w.writerow([k, len(rs), rs[0]["name"], max(w for w, _ in dims), max(h for _, h in dims)])
    print(f"Sprite {len(rows)} · glyph {len(glyphs)} · phải vẽ {len(groups)} (+1 bộ font {len(glyphs)} glyph)")
    print(f"đã ghi {OUT}")


if __name__ == "__main__":
    main()
