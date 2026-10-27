#!/usr/bin/env python3
"""Gợi ý nhãn từ **trang atlas** trong `resolved-geometry.json.gz`.

Khác `classify-knn.py`: đây không phải "hàng xóm gần nhất" mà là **nguồn dữ liệu gốc** —
sprite nào được pack vào page nào. Page của bản gốc có tên **có nghĩa** (`Bullets`, `UI_Home`,
`Enemy_Air`, `Boss3+7`…), nên tên page là một bằng chứng độc lập với tên sprite.

Nguyên tắc (để không lặp lại lỗi R4 "tự cấp A"):
1. **Đo trước, dùng sau.** Với mỗi họ page, đo độ chính xác trên các sprite **đã có nhãn A/B**;
   chỉ những họ `n ≥ 10` và `precision ≥ 0,95` mới được tự gán — phần còn lại chỉ là **gợi ý**.
2. Không ghi vào `category_auto` của `sprites-auto-classified.csv`; ghi bảng riêng.
3. Page không chứng minh ngữ nghĩa: một page có thể chứa nhiều loại (đo được là 0,36–1,00),
   nên mỗi dòng mang theo `precision` + `n_labeled` để người đọc tự cân.

Chạy: `python3 tools/classify-by-atlas.py`
Ghi: `docs/assets/sprites-atlas-page.csv`
"""

from __future__ import annotations

import collections
import csv
import gzip
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOM = "reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz"
AUTO = "docs/assets/sprites-auto-classified.csv"
OUT = "docs/assets/sprites-atlas-page.csv"

MIN_N = 10          # số sprite đã có nhãn tối thiểu để tin một họ page
MIN_PRECISION = 0.95


def family(page: str | None) -> str | None:
    """`sactx-0-1024x1024-ETC2-Bullets-fe66e1a9` → `Bullets`."""
    if not page:
        return None
    return re.sub(r"^sactx-\d+-[\dx]+-ETC2-", "", page).split("-")[0]


def main() -> int:
    with gzip.open(os.path.join(ROOT, GEOM), "rt", encoding="utf-8") as fh:
        geo = json.load(fh)
    page_of = {s["name"]: ((s.get("texture") or {}).get("name"))
               for s in geo["sprites"] if s.get("name")}

    with open(os.path.join(ROOT, AUTO), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    labeled = [r for r in rows if r["confidence"] in ("A", "B")]
    stats: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in labeled:
        fam = family(page_of.get(r["name"]))
        if fam:
            stats[fam][r["category_auto"]] += 1

    rules: dict[str, tuple[str, float, int]] = {}
    for fam, cnt in stats.items():
        total = sum(cnt.values())
        cat, hit = cnt.most_common(1)[0]
        if total >= MIN_N and hit / total >= MIN_PRECISION:
            rules[fam] = (cat, hit / total, total)

    out = []
    applied = collections.Counter()
    suggested = collections.Counter()
    for r in rows:
        fam = family(page_of.get(r["name"]))
        cat, prec, n = rules.get(fam, ("", 0.0, sum(stats[fam].values()) if fam in stats else 0))
        is_unres = r["category_auto"] == "unresolved"
        out.append({
            "name": r["name"],
            "path_id": r["path_id"],
            "texture_page": page_of.get(r["name"]) or "",
            "page_family": fam or "",
            "suggested_category": cat,
            "precision": f"{prec:.3f}" if cat else "",
            "n_labeled": n,
            "applied": "true" if (cat and is_unres) else "false",
            "current_category": r["category_auto"],
        })
        if cat and is_unres:
            applied[cat] += 1
        elif cat:
            suggested[cat] += 1

    with open(os.path.join(ROOT, OUT), "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out[0]))
        wr.writeheader()
        wr.writerows(out)

    n_un = sum(1 for r in rows if r["category_auto"] == "unresolved")
    n_page = sum(1 for r in rows if r["category_auto"] == "unresolved" and page_of.get(r["name"]))
    print(f"page: {len(page_of)} sprite có geometry · {len({p for p in page_of.values() if p})} texture")
    print(f"luật page đủ chuẩn (n≥{MIN_N}, precision≥{MIN_PRECISION}): {len(rules)} họ")
    for fam, (cat, prec, n) in sorted(rules.items(), key=lambda kv: -kv[1][2]):
        print(f"  {fam:16s} → {cat:10s} precision {prec:.3f} (n={n})")
    print(f"unresolved: {n_un} · có page: {n_page} · tự gán được: {sum(applied.values())} {dict(applied)}")
    print(f"đã ghi {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
