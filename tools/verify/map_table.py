#!/usr/bin/env python3
"""Trích bảng map từ thân .cctor của Map_Get_Datas (asm đã export trong repo).

.cctor dựng các List<int[]> tĩnh bằng hai cách:
  (a) `new int[L]` rồi `str w,#imm` từng phần tử — giá trị nằm ngay trong asm;
  (b) `new int[L]` + RuntimeHelpers.InitializeArray (bl 0x205b07c) — dữ liệu
      là blob <PrivateImplementationDetails> trong global-metadata.dat
      (xem field-defaults.json; phép nối token->blob chưa chốt, để riêng).

Script này tách .cctor thành các segment theo mốc tạo List mới, ghi lại mọi
mảng dựng được bằng cách (a) và độ dài của mảng cách (b).

Chạy:  python3 tools/verify/map_table.py
Xuất:  datas/map_table_segments.json (kết luận TẠM THỜI — chưa gắn tên field).
"""
from __future__ import annotations

import json
import os
import re
import sys

ASM = "reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt"
LIST_NEW = "#0x110d240"      # newobj List<...>
ARRAY_NEW = "#0x110d09c"     # il2cpp_array_new
INIT_ARRAY = "#0x205b07c"    # RuntimeHelpers.InitializeArray (mã máy)


def cctor_lines():
    blocks, cur = {}, None
    with open(ASM, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith(";;; "):
                cur = line[4:].split("  ")[0]
                blocks[cur] = []
            elif cur:
                blocks[cur].append(line.rstrip("\n"))
    return blocks["cctor"]


def imm(text):
    m = re.search(r"#(0x[0-9a-f]+|\d+)\s*$", text)
    return int(m.group(1), 0) if m else None


def main() -> int:
    cc = cctor_lines()
    segments = []
    seg = {"index": 0, "arrays": []}
    segments.append(seg)
    pending_len = None
    cur = None          # mảng đang dựng: {"len": L, "values": {k: v}, "init": bool}
    last_imm = {}       # reg -> immediate gần nhất

    def flush():
        nonlocal cur
        if cur is not None:
            if cur["init"]:
                seg["arrays"].append({"len": cur["len"], "source": "InitializeArray",
                                      "addr": cur["addr"]})
            else:
                vals = [cur["values"].get(k) for k in range(cur["len"])]
                seg["arrays"].append({"len": cur["len"], "source": "immediates",
                                      "values": vals, "addr": cur["addr"]})
            cur = None

    for line in cc:
        body = line.split(":", 1)[-1].strip()
        if f"bl       {LIST_NEW}" in body or f"bl {LIST_NEW}" in body:
            flush()
            seg = {"index": len(segments), "arrays": []}
            segments.append(seg)
            continue
        m = re.match(r"mov\s+(w\d+), #(0x[0-9a-f]+|\d+)$", body)
        if m:
            last_imm[m.group(1)] = int(m.group(2), 0)
            if m.group(1) == "w1":
                pending_len = int(m.group(2), 0)
            continue
        if ARRAY_NEW in body:
            flush()
            addr = line.split(":", 1)[0].strip()
            cur = {"len": pending_len or 0, "values": {}, "init": False,
                   "addr": addr}
            continue
        if INIT_ARRAY in body and cur is not None:
            cur["init"] = True
            continue
        # str w9, [x1, #0x24] — phần tử mảng tại offset 0x20 + 4*k
        m = re.match(r"str\s+(w\d+), \[x\d+, #(0x[0-9a-f]+|\d+)\]$", body)
        if m and cur is not None:
            off = int(m.group(2), 0)
            if 0x20 <= off < 0x20 + 4 * max(cur["len"], 0):
                k = (off - 0x20) // 4
                if m.group(1) in last_imm:
                    cur["values"][k] = last_imm[m.group(1)]
            continue
    flush()
    segments = [s for s in segments if s["arrays"]]

    out = {"source": ".cctor của Map_Get_Datas (asm trong repo) — kết luận tạm thời",
           "segments": segments}
    os.makedirs("datas", exist_ok=True)
    with open("datas/map_table_segments.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for s in segments:
        imm_n = sum(1 for a in s["arrays"] if a["source"] == "immediates")
        print(f"segment {s['index']}: {len(s['arrays'])} mảng "
              f"({imm_n} từ immediate, {len(s['arrays']) - imm_n} InitializeArray); "
              f"độ dài đầu: {[a['len'] for a in s['arrays'][:6]]}")
    print("-> datas/map_table_segments.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
