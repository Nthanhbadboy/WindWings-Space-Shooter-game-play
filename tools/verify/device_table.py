#!/usr/bin/env python3
"""Device_Get_Data..cctor: List<float[5]> — mỗi phần tử là 1 IA blob, theo thứ tự.

Giá trị lấy từ ia-resolved (token 2*ordinal+1 -> PID blob), hiểu theo float32.
Danh sách tĩnh: index = thứ tự Add trong .cctor (chưa khop tên device).
"""
import json
import struct

jd = json.load(open("reverse-engineering/il2cpp/ia-resolved.json",
                    encoding="utf-8"))
rows = jd["methods"]["Device_Get_Data.cctor"]
out = []
for e in rows:
    assert e["length_valid"] and len(e["ints"]) == e["len"]
    floats = [struct.unpack("<f", struct.pack("<i", v))[0] for v in e["ints"]]
    out.append({"index": len(out), "len": e["len"], "stats": floats, "field": e["field"],
                "initialize_array_addr": e["addr"], "array_new_addr": e["array_new_addr"]})
json.dump({"source": "Device_Get_Data..cctor List<float[5]> qua ia-resolved "
                     "(PROVISIONAL); 12 array captures, NOT 12 proven devices; field grouping pending",
           "arrays": out},
          open("datas/device_table.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for r in out:
    print(r["index"], [round(x, 4) for x in r["stats"]])
