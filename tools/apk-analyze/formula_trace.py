#!/usr/bin/env python3
"""Truy vết thứ tự phép tính trong các method cân bằng, từ raw IL2CPP đã bóc.

Nguồn: `reverse-engineering/raw/il2cpp-consts/<Class>.json` (hằng số + role đã gán
bởi `il2cpp_consts.py`) và `<Class>.asm.txt` (disassembly). Tool này:

1. Với mỗi method, sắp xếp các hằng số **theo địa chỉ** và giữ các role có nghĩa
   (`compare`, `load`, `arith:*`, `return`) → thành "dòng chảy" đọc được.
2. Giải các lệnh `bl #0x…` sang tên method khi địa chỉ đích trùng RVA của một method
   đã biết; nếu đích nằm **giữa** thân method khác (generic dùng chung) thì ghi
   `~TênMethod+offset` và đánh dấu gần đúng.

Xuất `datas/formula_traces.json.gz` + `docs/apk-analysis/28-formula-traces.md`.
Chạy offline. **Kết luận tạm thời**: thứ tự lệnh ≠ công thức chắc chắn — còn rẽ nhánh.
"""
from __future__ import annotations

import bisect
import glob
import gzip
import json
import os
import re
import sys
from collections import Counter

RAW = os.environ.get("CONSTS_RAW", "reverse-engineering/raw/il2cpp-consts")
OUT_JSON = os.environ.get("FORMULA_JSON", "datas/formula_traces.json.gz")
OUT_MD = os.environ.get("FORMULA_MD", "docs/apk-analysis/28-formula-traces.md")

BL_RE = re.compile(r"^\s+0x([0-9a-f]+):\s+bl\s+#0x([0-9a-f]+)")
HEAD_RE = re.compile(r"^;;; (\S+)\s")
KEEP_ROLES = ("compare", "load", "return")


def load_methods():
    methods = {}  # (class, method) -> json row
    for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for m in data.get("methods", []):
            # key kèm rva để không mất các overload trùng tên
            methods[(data["class"], m["method"], m.get("rva", ""))] = m
    return methods


def parse_calls():
    """(class, method) -> [địa chỉ đích của bl, ...] theo thứ tự xuất hiện."""
    calls = {}
    for path in sorted(glob.glob(os.path.join(RAW, "*.asm.txt"))):
        cls = os.path.basename(path)[:-len(".asm.txt")]
        current = None
        for line in open(path, encoding="utf-8", errors="replace"):
            head = HEAD_RE.match(line)
            if head:
                current = head.group(1)
                calls.setdefault((cls, current), [])
                continue
            if current is None:
                continue
            m = BL_RE.match(line)
            if m:
                calls[(cls, current)].append(int(m.group(2), 16))
    return calls


def main() -> int:
    methods = load_methods()
    if not methods:
        print(f"không có JSON trong {RAW}")
        return 0
    calls = parse_calls()

    rva_map = {}
    for (cls, name, _rva), m in methods.items():
        try:
            rva_map[int(m["rva"], 16)] = f"{cls}.{name}"
        except (KeyError, ValueError):
            continue
    rvas = sorted(rva_map)

    def resolve(target: int) -> str:
        if target in rva_map:
            return rva_map[target]
        i = bisect.bisect_right(rvas, target) - 1
        if i < 0:
            return f"ext@0x{target:x}"
        base = rvas[i]
        return f"~{rva_map[base]}+0x{target - base:x}"

    traces = []
    for (cls, name, _rva), m in sorted(methods.items()):
        consts = [c for c in m.get("constants", [])
                  if c.get("role") in KEEP_ROLES or str(c.get("role", "")).startswith("arith:")]
        consts.sort(key=lambda c: int(str(c.get("addr", "0x0")), 16))
        flow = [{"role": c["role"], "kind": c.get("kind"), "value": c.get("value"),
                 "addr": c.get("addr")} for c in consts]
        targets = [resolve(t) for t in calls.get((cls, name), [])]
        pool = [c["value"] for c in consts
                if c.get("role") == "load" and c.get("kind") == "float"]
        arith = [c["role"].split(":", 1)[1] for c in consts
                 if str(c.get("role", "")).startswith("arith:")]
        traces.append({"class": cls, "method": name,
                       "signature": m.get("signature", ""),
                       "getter_kind": m.get("getter_kind"),
                       "pool_floats": pool, "arith_ops": arith,
                       "flow": flow, "calls": targets})

    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    with gzip.open(OUT_JSON, "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump({"note": "Kết luận tạm thời. flow = hằng số theo thứ tự địa chỉ; "
                           "calls = đích bl đã giải tên (~ = nằm giữa thân method khác).",
                   "traces": traces}, fh, ensure_ascii=False, separators=(",", ":"))

    write_md(traces)
    n_calls = sum(1 for t in traces for c in t["calls"] if not c.startswith(("~", "ext")))
    print(f"{len(traces)} method, {n_calls} bl giải đúng tên -> {OUT_JSON}")
    return 0


def write_md(traces):
    interesting = [t for t in traces if len(t["pool_floats"]) >= 2 or len(t["arith_ops"]) >= 2]
    interesting.sort(key=lambda t: -(len(t["pool_floats"]) + len(t["arith_ops"])))
    lines = ["# 28 — Truy vết công thức trong method cân bằng (kết luận tạm thời)", "",
             "> **Kết luận tạm thời.** Sinh offline từ `raw/il2cpp-consts/*.json` + `*.asm.txt`",
             "> bằng `tools/apk-analyze/formula_trace.py`. Cột `flow` là hằng số theo **thứ tự địa chỉ**",
             "> trong thân hàm; còn rẽ nhánh (`b.ne`, `csel`…) nên đây là **nguyên liệu** để đọc công thức,",
             "> chưa phải công thức. Đích `bl` có `~` nghĩa là nằm giữa thân method khác (generic dùng chung).",
             "", f"- method có trace: **{len(traces)}**, method đáng đọc trước: **{len(interesting)}**", "",
             "## Đọc thử một method", "",
             "`Player_Get_Datas.GetWingCannonDamage` — flow theo địa chỉ:", "",
             "```",
             "`cmp 4` → load **0.168** → `cmp 58` → load **0.1764** → `cmp 118` → load **0.1932** (fmul)",
             "→ `cmp 248` → **fadd 1.0**",
             "```", "",
             "Đọc ra (mức **B**): hệ số damage chọn theo **ngưỡng** của một giá trị so sánh",
             "(4 / 58 / 118 / 248 — khả năng là cấp tech hoặc chỉ số cộng dồn), 0.1764 = 0.168 × 1.05",
             "và 0.1932 = 0.168 × 1.15, cuối cùng có `+ 1.0` kiểu `(1 + x)`. Chưa chắc cho đến khi",
             "đọc rẽ nhánh đầy đủ trong `.asm.txt`.", "",
             "## Method đáng đọc trước (nhiều float pool / phép tính nhất)", "",
             "| class.method | float từ pool | phép tính | gọi tới (đã giải tên) |",
             "|---|---|---|---|"]
    for t in interesting[:40]:
        named = [c for c in t["calls"] if not c.startswith(("~", "ext"))]
        lines.append(f"| `{t['class']}.{t['method']}` | {', '.join(str(v) for v in t['pool_floats'][:8])} "
                     f"| {', '.join(t['arith_ops'][:8])} | {', '.join(sorted(set(named))[:4])} |")
    lines += ["", "## Giới hạn", "",
              "- `bl` vào giữa thân method (generic IL2CPP dùng chung) chỉ ghi gần đúng bằng `~`.",
              "- Hằng số `compare` có thể là ngưỡng cấp, ID item hoặc enum — phải đọc ngữ cảnh rẽ nhánh.",
              "- Muốn công thức chắc chắn: đọc `.asm.txt` của từng method trong bảng trên, hoặc Ghidra.",
              ""]
    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
