#!/usr/bin/env python3
"""Bảng HP enemy theo id từ .cctor của Enemy_Get_Datas.

.cctor dựng `Dictionary<int, float> AllStartHealthPointEnemies` bằng chuỗi
Add(id, hp): `mov w1, #id` + float (immediate 0x447a0000 = 1000.0 hoặc nạp từ
pool) rồi `bl` Add. Ghép cặp theo thứ tự địa chỉ trong JSON hằng số đã export.

Chạy:  python3 tools/verify/enemy_hp.py
Xuất:  datas/enemy_hp_by_id.json (kết luận tạm thời)
"""
from __future__ import annotations

import json
import os
import struct
import sys


def as_float(c):
    if c["kind"] == "float":
        return c["value"]
    if c["kind"] == "int" and c.get("bits"):
        try:
            return struct.unpack("<f", struct.pack("<I", int(c["bits"], 16)))[0]
        except (ValueError, struct.error):
            return None
    return None


def main() -> int:
    # map địa chỉ lệnh -> float pool (từ JSON), để biết giá trị `ldr sN, [...]`
    d = json.load(open("reverse-engineering/raw/il2cpp-consts/Enemy_Get_Datas.json",
                       encoding="utf-8"))
    pool = {}
    for m in d["methods"]:
        for c in m["constants"]:
            if c["kind"] == "float":
                pool[c["addr"]] = c["value"]
    txt = open("reverse-engineering/raw/il2cpp-consts/Enemy_Get_Datas.asm.txt",
               encoding="utf-8").read()
    seg = txt[txt.find(";;; cctor"):]
    import re
    import struct as _st
    sreg, wreg, table = {}, {}, {}
    key = None
    for line in seg.splitlines():
        if ":" not in line:
            continue
        addr, body = line.split(":", 1)
        addr = addr.strip()
        body = body.strip()
        m = re.match(r"mov\s+(w\d+), #(0x[0-9a-f]+|\d+)$", body)
        if m:
            wreg[m.group(1)] = int(m.group(2), 0)
            if m.group(1) == "w1":
                key = int(m.group(2), 0)
            continue
        m = re.match(r"fmov\s+(s\d+), (w\d+)$", body)
        if m and m.group(2) in wreg:
            sreg[m.group(1)] = _st.unpack("<f", _st.pack("<I", wreg[m.group(2)] & 0xFFFFFFFF))[0]
            continue
        m = re.match(r"ldr\s+(s\d+), \[", body)
        if m and addr in pool:
            sreg[m.group(1)] = pool[addr]
            continue
        m = re.match(r"mov\s+v0\.16b, v(\d+)\.16b", body)
        if m and f"s{m.group(1)}" in sreg:
            sreg["s0"] = sreg[f"s{m.group(1)}"]
            continue
        if "#0x193a074" in body:  # Dictionary.Add
            if key is not None and "s0" in sreg:
                table[key] = sreg["s0"]
            key = None
    print(f"Add(id, hp): {len(table)} cặp")
    for k in sorted(table)[:12]:
        print(f"  {k}: {table[k]}")
    out = {"source": "Enemy_Get_Datas..cctor Dictionary<int,float> "
                     "AllStartHealthPointEnemies (tạm thời)",
           "count": len(table),
           "hp_by_id": {str(k): table[k] for k in sorted(table)}}
    with open("datas/enemy_hp_by_id.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("-> datas/enemy_hp_by_id.json")

    import csv
    ser = {}
    with open("docs/apk-analysis/15-enemy-hp.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            ser[r["gameobject"].split("/")[0]] = \
                ser.get(r["gameobject"].split("/")[0], 0.0) + float(r["start_hp"])
    hits = [(f"CB-{k}", v, ser.get(f"CB-{k}")) for k, v in sorted(table.items())
            if f"CB-{k}" in ser]
    print(f"khớp tên CB-<id> trong bảng serialize: {len(hits)}")
    for name, runtime, serialized in hits[:8]:
        print(f"  {name}: runtime={runtime} serialize={serialized}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
