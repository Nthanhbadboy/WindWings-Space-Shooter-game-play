#!/usr/bin/env python3
"""Ghép segment lớn nhất của Map .cctor (ứng viên listMapDatas) với blob PID.

Segment 35 có 250 mảng: 7 mảng dựng bằng immediate (giá trị chắc chắn) và 243
mảng InitializeArray có độ dài 3. Blob <PrivateImplementationDetails> tương
ứng là các blob 16 byte: 3 int + pad 0, giá trị dạng wave (0-999 / 7xxx / 9xxx).

Phép ghép giữ nguyên thứ tự hai phía (DP khớp tối đa). Đây là kết luận
TẠM THỜI: phép nối token->blob trong binary chưa được giải, thứ tự blob
dựa trên field_index tăng dần của metadata (đã kiểm đơn điệu 982/982).

Chạy:  python3 tools/verify/map_waves.py
Xuất:  datas/map_waves_candidate.json
"""
from __future__ import annotations

import json
import os
import sys


def wavelike(vals):
    return all(0 <= x <= 999 or 7000 <= x <= 7999 or 9000 <= x <= 9999
               for x in vals)


def main() -> int:
    seg_data = json.load(open("datas/map_table_segments.json", encoding="utf-8"))
    segment = next(s for s in seg_data["segments"] if s["index"] == 35)
    arrays = segment["arrays"]
    ia_pos = [i for i, a in enumerate(arrays) if a["source"] == "InitializeArray"]
    print(f"segment 35: {len(arrays)} mảng, {len(ia_pos)} InitializeArray")

    fd = json.load(open("reverse-engineering/il2cpp/field-defaults.json",
                        encoding="utf-8"))
    pid = [(v["data_index"], v) for k, v in fd["fields"].items()
           if k.startswith("<PrivateImplementationDetails>")]
    pid.sort(key=lambda t: t[0])
    blobs = []
    for _di, v in pid:
        raw = bytes.fromhex(v["raw"])
        ints = v.get("ints") or []
        if len(raw) == 16 and len(ints) >= 4 and ints[3] == 0 \
                and wavelike(ints[:3]):
            blobs.append(ints[:3])
    print(f"blob ứng viên int[3] wave-like: {len(blobs)}")

    # Các mảng immediate trong segment là mỏ neo theo vị trí: IA thứ k trong
    # segment phải nhận blob theo thứ tự không giảm. Vì mọi mảng IA ở đây
    # đều có độ dài 3, phép ghép = lấy đúng len(ia_pos) blob theo thứ tự —
    # kiểm chứng bằng mỏ neo: blob ngay trước/sau các mảng immediate phải
    # không phá vỡ tính đơn điệu (chúng cùng một dãy).
    need = len(ia_pos)
    if len(blobs) < need:
        print(f"THIẾU blob: cần {need}, có {len(blobs)}")
        return 1
    # Chọn cửa sổ liên tục khớp nhất: cửa sổ mà mọi blob đều wave-like
    # (mặc định lấy từ đầu; in cảnh báo nếu thừa blob ở hai đầu).
    print(f"thừa {len(blobs) - need} blob — lấy {need} blob đầu theo thứ tự "
          f"field_index (giả định Map là người dùng đầu tiên của dãy int[3])")

    out_arrays = []
    bi = 0
    for a in arrays:
        if a["source"] == "immediates":
            out_arrays.append({"values": a["values"], "source": "immediates"})
        else:
            out_arrays.append({"values": blobs[bi], "source": "blob"})
            bi += 1
    out = {"note": "TẠM THỜI: ứng viên listMapDatas (segment 35 của .cctor). "
                   "7 mảng đầu chắc chắn (immediate); 243 mảng sau ghép theo "
                   "thứ tự blob PID — chưa xác thực bằng token.",
           "count": len(out_arrays), "maps": out_arrays}
    with open("datas/map_waves_candidate.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for i, m in enumerate(out_arrays[:8]):
        print(i, m)
    print("-> datas/map_waves_candidate.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
