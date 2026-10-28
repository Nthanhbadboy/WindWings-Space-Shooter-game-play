#!/usr/bin/env python3
"""classify-knn.py — gợi ý nhãn cho các sprite `unresolved` bằng **hàng xóm gần nhất**.

Khác `tools/classify-by-measure.py` (luật tay): ở đây không có luật nào do người viết.
Máy xếp 1.857 sprite **đã có nhãn** vào không gian 10 số đo rồi lấy 3 hàng xóm gần
nhất. Vì vậy **sai số phải đo**, không được tin mặc định:

  * leave-one-out trên chính 1.857 nhãn đã có (bỏ nhãn của nó ra rồi đoán lại);
  * chỉ nhận gợi ý khi 3 hàng xóm **đồng ý ≥2/3**;
  * in **recall/precision từng nhóm** để biết nhóm nào đáng tin.

Kết quả **không** ghi đè `category_auto`; nó ra file riêng, cột `category_knn`.
Nhãn nào sai số cao (parts, enemy, drones…) thì đọc là *gợi ý*, không phải nhãn.

Đầu vào : docs/assets/sprites-auto-classified.csv · docs/apk-analysis/04-asset-manifest.csv
Đầu ra  : docs/assets/sprites-knn.csv · docs/assets/classify-knn.json

Chạy: python3 tools/classify-knn.py [--k 3] [--margin 0.6]
"""
from __future__ import annotations

import collections
import csv
import json
import math
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs/assets/sprites-auto-classified.csv")
MANIFEST = os.path.join(ROOT, "docs/apk-analysis/04-asset-manifest.csv")
OUT_CSV = os.path.join(ROOT, "docs/assets/sprites-knn.csv")
OUT_JSON = os.path.join(ROOT, "docs/assets/classify-knn.json")

# 10 số đo. Log cho các đại lượng lệch nhiều bậc (pixel, màu, bytes) để khoảng cách
# không bị một cột chi phối.
FEATURES = ("log_w", "log_h", "log_colors", "fill", "sat", "val", "dark",
            "log_ncomp", "log_bytes", "log_aspect")


def features(r: dict, nbytes: int) -> list[float]:
    w = int(r["w"]) or 1
    h = int(r["h"]) or 1
    return [
        math.log(w), math.log(h),
        math.log(max(int(r["colors"]), 1)),
        float(r["fill"]), float(r["sat"]), float(r["val"]), float(r["dark"]),
        math.log1p(int(r["ncomp"])),
        math.log10(max(nbytes, 1)),
        abs(math.log(w / h)),
    ]


def main(argv: list[str]) -> int:
    k = int(argv[argv.index("--k") + 1]) if "--k" in argv else 3
    margin = float(argv[argv.index("--margin") + 1]) if "--margin" in argv else 0.6

    with open(SRC, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(MANIFEST, encoding="utf-8") as fh:
        nbytes = {r["path_id"]: int(r["bytes"] or 0) for r in csv.DictReader(fh)}

    lab = [r for r in rows if r["category_auto"] != "unresolved"]
    if len(lab) < 100:
        print("quá ít sprite có nhãn:", len(lab))
        return 1
    X = [features(r, nbytes.get(r["path_id"], 0)) for r in lab]
    Y = [r["category_auto"] for r in lab]

    d = len(FEATURES)
    mu = [st.mean(c[i] for c in X) for i in range(d)]
    sd = [st.pstdev(c[i] for c in X) or 1.0 for i in range(d)]
    Z = [[(c[i] - mu[i]) / sd[i] for i in range(d)] for c in X]

    def neighbours(z: list[float], exclude: int | None = None) -> list[tuple[float, int]]:
        out = []
        for j, zz in enumerate(Z):
            if j == exclude:
                continue
            out.append((sum((a - b) ** 2 for a, b in zip(z, zz)), j))
        out.sort()
        return out[:k]

    def vote(ds: list[tuple[float, int]]) -> tuple[str, float]:
        c = collections.Counter(Y[j] for _, j in ds).most_common()
        second = c[1][1] if len(c) > 1 else 0
        return c[0][0], (c[0][1] - second) / k

    # ── leave-one-out: đo sai số thật, không giả định ──
    hit = collections.Counter()
    tot = collections.Counter()
    got = collections.Counter()   # số lần máy đoán ra nhãn X
    ok = collections.Counter()    # ... và đúng
    covered = 0
    for i, z in enumerate(Z):
        cat, m = vote(neighbours(z, i))
        if m < margin:
            continue
        covered += 1
        tot[Y[i]] += 1
        got[cat] += 1
        if cat == Y[i]:
            hit[Y[i]] += 1
            ok[cat] += 1
    correct = sum(hit.values())
    per_class = {
        c: {"n": tot[c], "recall": round(hit[c] / tot[c], 3),
            "precision": round(ok[c] / got[c], 3) if got[c] else None}
        for c in sorted(tot, key=lambda c: -tot[c])
    }

    # ── áp lên unresolved ──
    out_rows = []
    for r in rows:
        if r["category_auto"] != "unresolved":
            continue
        z = [(features(r, nbytes.get(r["path_id"], 0))[i] - mu[i]) / sd[i] for i in range(d)]
        cat, m = vote(neighbours(z))
        pc = per_class.get(cat, {})
        out_rows.append({
            "name": r["name"], "path_id": r["path_id"], "w": r["w"], "h": r["h"],
            "category_knn": cat if m >= margin else "",
            "margin": round(m, 3),
            "precision_measured": pc.get("precision") if m >= margin else "",
            "rule": f"kNN k={k} trên 10 số đo · margin ≥{margin}",
        })
    if not out_rows:
        print("không có unresolved để gợi ý")
        return 1
    out_rows.sort(key=lambda r: (not r["category_knn"], -float(r["margin"])))
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        wr.writeheader()
        wr.writerows(out_rows)

    sugg = collections.Counter(r["category_knn"] for r in out_rows if r["category_knn"])
    summary = {
        "k": k, "margin": margin,
        "labeled": len(lab), "unresolved": len(out_rows),
        "loo_covered": covered,
        "loo_accuracy": round(correct / covered, 3) if covered else None,
        "loo_correct": correct,
        "suggested": sum(sugg.values()),
        "suggested_by_category": dict(sugg),
        "per_class": per_class,
        "features": list(FEATURES),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)

    print(f"LOO: {covered}/{len(lab)} ca đủ tự tin · đúng {correct} "
          f"({summary['loo_accuracy']:.1%})")
    for c, v in per_class.items():
        print(f"  {c:11s} recall {v['recall']:.2f} · precision {v['precision'] or 0:.2f} · n={v['n']}")
    print(f"\ngợi ý cho {summary['suggested']}/{len(out_rows)} sprite unresolved: {dict(sugg)}")
    print("đã ghi", os.path.relpath(OUT_CSV, ROOT), "và", os.path.relpath(OUT_JSON, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
