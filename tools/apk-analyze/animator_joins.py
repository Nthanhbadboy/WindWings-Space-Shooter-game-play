#!/usr/bin/env python3
"""Nối `Animator` → prefab gốc + tên `AnimatorController` (offline).

Chuỗi: `Animator.m_GameObject` → Transform → leo `m_Father` → prefab gốc;
`Animator.m_Controller` (chỉ khi `m_FileID = 0`) → tên controller trong cùng file.

Đầu vào: `raw/typetrees/native-types.jsonl.gz` + `transform-tree.tsv.gz` + `prefab-roots.csv`.
Đầu ra: `datas/animator_map.csv.gz`. **Kết luận tạm thời** (prefab ≠ runtime).
"""
from __future__ import annotations

import csv
import gzip
import json
import os
import sys
from collections import Counter

RAW = os.environ.get("TYPETREE_RAW", "reverse-engineering/raw/typetrees")
OUT_CSV = os.environ.get("ANIMATOR_MAP_CSV", "datas/animator_map.csv.gz")


def main() -> int:
    trans, go2tr, roots = {}, {}, {}
    with gzip.open(os.path.join(RAW, "transform-tree.tsv.gz"), "rt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            a, b, c = line.rstrip("\n").split("\t")
            a, b, c = int(a), int(b), int(c)
            trans[a] = c
            if b:
                go2tr.setdefault(b, a)
    with open(os.path.join(RAW, "prefab-roots.csv"), newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            roots[int(r["transform_path_id"])] = r["name"]

    cache: dict[int, str | None] = {}

    def root_name(tpid):
        if tpid in cache:
            return cache[tpid]
        cur, chain = tpid, []
        for _ in range(128):
            chain.append(cur)
            fa = trans.get(cur, 0)
            if not fa:
                name = roots.get(cur)
                for x in chain:
                    cache[x] = name
                return name
            cur = fa
        return None

    controllers, animators = {}, []
    with gzip.open(os.path.join(RAW, "native-types.jsonl.gz"), "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["type"] == "AnimatorController":
                controllers[r["path_id"]] = r.get("m_Name", "")
            elif r["type"] == "Animator":
                animators.append(r)

    rows, stats = [], Counter()
    for r in animators:
        go = (r.get("m_GameObject") or {}).get("m_PathID") or 0
        tpid = go2tr.get(go)
        root = root_name(tpid) if tpid else None
        ctrl = r.get("m_Controller") or {}
        cpid = ctrl.get("m_PathID") or 0
        cname = controllers.get(cpid, "") if ctrl.get("m_FileID") == 0 else ""
        stats[("root", bool(root))] += 1
        stats[("controller", bool(cname))] += 1
        rows.append([r["path_id"], go, root or "", cpid, cname])

    os.makedirs(os.path.dirname(OUT_CSV) or ".", exist_ok=True)
    with gzip.open(OUT_CSV, "wt", newline="", encoding="utf-8", compresslevel=9) as fh:
        w = csv.writer(fh)
        w.writerow(["animator_path_id", "gameobject_path_id", "prefab_root",
                    "controller_path_id", "controller_name"])
        w.writerows(rows)

    print(f"Animator: {len(rows)}, nối được prefab gốc {stats[('root', True)]}, "
          f"tên controller {stats[('controller', True)]} -> {OUT_CSV}")
    top = Counter(r[4] for r in rows if r[4])
    print("controller phổ biến:", top.most_common(8))
    return 0


if __name__ == "__main__":
    sys.exit(main())
