#!/usr/bin/env python3
"""Nối component → prefab gốc bằng cây `Transform` (offline, không cần APK).

Chuỗi nối: `component.m_GameObject` (hoặc field PPtr trỏ GameObject) → Transform của
GameObject đó → leo `m_Father` tới root → tên prefab trong `prefab-roots.csv`.

Đầu vào: `reverse-engineering/raw/typetrees/*.jsonl.gz` + `transform-tree.tsv.gz`.
Đầu ra: `datas/prefab_joins.csv.gz` — mỗi dòng: class, field, path_id của component,
path_id đích, prefab gốc. **Kết luận tạm thời** (prefab ≠ runtime).
"""
from __future__ import annotations

import csv
import glob
import gzip
import json
import os
import sys
from collections import Counter

RAW = os.environ.get("TYPETREE_RAW", "reverse-engineering/raw/typetrees")
OUT_CSV = os.environ.get("JOINS_CSV", "datas/prefab_joins.csv.gz")

# (class, field, field này trỏ tới GameObject hay Transform?)
SEAMS = [
    ("Gun_Attack", "m_GameObject", "go"),
    ("Boss_BodyPhysics", "m_GameObject", "go"),
    ("Enemy_Controller", "m_GameObject", "go"),
    ("Enemy_Movement", "parentRotate", "transform"),
    ("Wave", "startPoint", "transform"),
    ("Wave", "endPoint", "transform"),
    ("Stage_Behaviour", "bossObj", "go"),
]


def load_transforms():
    trans, go2tr = {}, {}
    with gzip.open(os.path.join(RAW, "transform-tree.tsv.gz"), "rt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            a, b, c = line.rstrip("\n").split("\t")
            a, b, c = int(a), int(b), int(c)
            trans[a] = c
            if b:
                go2tr.setdefault(b, a)
    roots = {}
    with open(os.path.join(RAW, "prefab-roots.csv"), newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            roots[int(r["transform_path_id"])] = r["name"]
    return trans, go2tr, roots


def main() -> int:
    trans, go2tr, roots = load_transforms()
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

    rows, stats = [], Counter()
    for cls, field, kind in SEAMS:
        path = os.path.join(RAW, f"{cls}.jsonl.gz")
        if not os.path.isfile(path):
            continue
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line)
                tree = rec.get("tree") or {}
                ref = tree.get(field) or {}
                target = ref.get("m_PathID") or 0
                if not target:
                    continue
                tpid = go2tr.get(target) if kind == "go" else target
                name = root_name(tpid) if tpid else None
                stats[(cls, field, bool(name))] += 1
                rows.append([cls, field, rec.get("path_id"), target, name or ""])

    os.makedirs(os.path.dirname(OUT_CSV) or ".", exist_ok=True)
    with gzip.open(OUT_CSV, "wt", newline="", encoding="utf-8", compresslevel=9) as fh:
        w = csv.writer(fh)
        w.writerow(["class", "field", "component_path_id", "target_path_id", "prefab_root"])
        w.writerows(rows)

    for (cls, field, ok), n in sorted(stats.items()):
        print(f"{cls}.{field}: {'hit' if ok else 'miss'} {n}")
    print(f"{len(rows)} dòng -> {OUT_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
