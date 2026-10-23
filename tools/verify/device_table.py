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
    floats = [struct.unpack("<f", struct.pack("<i", v))[0] for v in e["ints"]]
    out.append({"index": len(out), "len": e["len"], "stats": floats})
json.dump({"source": "Device_Get_Data..cctor List<float[5]> qua ia-resolved "
                     "(A-); cột chưa đặt tên — GetStatValue1/2 quyết định",
           "devices": out},
          open("datas/device_table.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for r in out:
    print(r["index"], [round(x, 4) for x in r["stats"]])
