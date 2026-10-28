#!/usr/bin/env python3
"""Bóc timeline animation của Spine từ TextAsset JSON đã export.

Chạy **offline** trên `reverse-engineering/textassets/*.json` (26 skeleton + Saw.json),
không cần APK/UnityPy — nên chạy được cả trong sandbox lẫn CI.

Xuất:
  datas/spine_anim.json.gz          timeline đầy đủ (bone/slot/deform/drawOrder/events)
  docs/apk-analysis/spine-events.csv mọi event (rig, animation, time, tên event)
  docs/apk-analysis/23-spine-anim.md báo cáo tóm tắt

Mọi số liệu là **kết luận tạm thời**: đọc từ file JSON mà game nạp, chưa đối chiếu runtime.
"""
from __future__ import annotations

import csv
import glob
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

SRC = os.environ.get("SPINE_TEXTASSETS", "reverse-engineering/textassets")
OUT_JSON = os.environ.get("SPINE_ANIM_JSON", "datas/spine_anim.json.gz")
OUT_CSV = os.environ.get("SPINE_EVENTS_CSV", "docs/apk-analysis/spine-events.csv")
OUT_MD = os.environ.get("SPINE_ANIM_MD", "docs/apk-analysis/23-spine-anim.md")


def load_skeletons(src: str):
    """Trả [(rig_id, data)] cho mọi file JSON có khoá `animations`."""
    out = []
    for path in sorted(glob.glob(os.path.join(src, "*.json"))):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict) or not isinstance(data.get("animations"), dict):
            continue
        rig = os.path.splitext(os.path.basename(path))[0]
        out.append((rig, data))
    return out


def _frames(timeline):
    """Spine 3.8: list frame; frame[0] là setup pose (rỗng), các frame sau có `time`."""
    if not isinstance(timeline, list):
        return []
    frames = []
    for f in timeline:
        if not isinstance(f, dict):
            continue
        if "time" not in f:
            continue                       # frame setup
        rec = {"t": round(float(f["time"]), 4)}
        for k in ("x", "y", "angle", "value", "color", "gx", "gy", "rx", "ry",
                  "width", "height", "mixX", "mixY", "curve"):
            if k in f:
                v = f[k]
                rec[k] = round(v, 4) if isinstance(v, float) else v
        frames.append(rec)
    return frames


def anim_summary(anim: dict):
    bones, slots = {}, {}
    for name, tl in (anim.get("bones") or {}).items():
        tracks = {k: _frames(v) for k, v in tl.items() if k in
                  ("rotate", "translate", "scale", "shear")}
        tracks = {k: v for k, v in tracks.items() if v}
        if tracks:
            bones[name] = tracks
    # slots: 3.8 dùng dict {slot: {"attachment": [...]}}; 4.x dùng list
    slot_src = anim.get("slots")
    if isinstance(slot_src, dict):
        slot_items = slot_src.items()
    else:
        slot_items = []
    for name, tl in slot_items:
        if isinstance(tl, dict):
            tracks = {k: _frames(v) for k, v in tl.items() if k in
                      ("attachment", "color", "rgba", "rgba2")}
            tracks = {k: v for k, v in tracks.items() if v}
            if tracks:
                slots[name] = tracks
    events = []
    for e in anim.get("events") or []:
        if isinstance(e, dict) and "name" in e:
            events.append({"t": round(float(e.get("time", 0)), 4), "name": e["name"],
                           "int": e.get("int"), "float": e.get("float"),
                           "string": e.get("string")})
    keyframes = sum(len(f) for b in bones.values() for f in b.values())
    keyframes += sum(len(f) for s in slots.values() for f in s.values())
    duration = 0.0
    for coll in (bones, slots):
        for tl in coll.values():
            for frames in tl.values():
                if frames:
                    duration = max(duration, frames[-1]["t"])
    for e in events:
        duration = max(duration, e["t"])
    return {"bones": bones, "slots": slots,
            "deform": len(anim.get("deform") or {}) if isinstance(anim.get("deform"), dict) else 0,
            "draw_order": len(anim.get("drawOrder") or []) if isinstance(anim.get("drawOrder"), list) else 0,
            "events": events, "keyframes": keyframes, "duration": round(duration, 4)}


def main() -> int:
    rigs = load_skeletons(SRC)
    if not rigs:
        print(f"không thấy skeleton JSON trong {SRC}")
        return 0

    out = {"note": "Kết luận tạm thời. Bóc offline từ TextAsset JSON của Spine.",
           "source": SRC, "rigs": {}}
    events_rows = []
    curve_kinds = Counter()
    ev_names = Counter()
    total_kf = 0
    total_anim = 0

    for rig, data in rigs:
        entry = {"bones_total": len(data.get("bones") or []),
                 "slots_total": len(data.get("slots") or []),
                 "animations": {}}
        for name, anim in data["animations"].items():
            if not isinstance(anim, dict):
                continue
            s = anim_summary(anim)
            total_kf += s["keyframes"]
            total_anim += 1
            for b in s["bones"].values():
                for frames in b.values():
                    for f in frames:
                        curve_kinds[str(f.get("curve", "linear"))[:12]] += 1
            for e in s["events"]:
                ev_names[e["name"]] += 1
                events_rows.append([rig, name, e["t"], e["name"], "", ""])
            entry["animations"][name] = s
        out["rigs"][rig] = entry

    out["totals"] = {"rigs": len(rigs), "animations": total_anim,
                     "keyframes": total_kf, "curve_kinds": dict(curve_kinds),
                     "events": sum(ev_names.values())}

    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    with gzip.open(OUT_JSON, "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    raw_mb = os.path.getsize(OUT_JSON) / 1e6

    os.makedirs(os.path.dirname(OUT_CSV) or ".", exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["rig", "animation", "time", "event", "int", "string"])
        w.writerows(sorted(events_rows, key=lambda r: (r[0], r[1], r[2])))

    write_md(out, events_rows, ev_names, curve_kinds)
    print(f"{len(rigs)} rig, {total_anim} animation, {total_kf} keyframe, "
          f"{len(events_rows)} event -> {OUT_JSON} ({raw_mb:.2f} MB gz)")
    return 0


def write_md(out, events_rows, ev_names, curve_kinds):
    t = out["totals"]
    L = ["# 23 — Spine animation: timeline thật (kết luận tạm thời)", "",
         "> **Kết luận tạm thời.** Bóc trực tiếp từ TextAsset JSON mà game nạp",
         "> (`reverse-engineering/textassets/skeleton*.json`, `Saw.json`) — không vẽ lại, không",
         "> đoán. Chưa đối chiếu runtime; thời điểm có thể lệch nếu game chỉnh `animation.timeScale`.",
         "", "## Tổng quan", "",
         f"- rig: **{t['rigs']}**, animation: **{t['animations']}**, keyframe: **{t['keyframes']:,}**",
         f"- event: **{t['events']}**, loại curve: " +
         ", ".join(f"`{k}`×{v}" for k, v in sorted(curve_kinds.items())) or "—", "",
         "File máy đọc: `datas/spine_anim.json.gz` (timeline đầy đủ), "
         "`docs/apk-analysis/spine-events.csv` (mọi event).", ""]

    L += ["## Rig lớn nhất", "",
          "| rig | bone | slot | anim | keyframe | thời lượng max (s) |",
          "|---|---:|---:|---:|---:|---:|"]
    rows = []
    for rig, e in out["rigs"].items():
        kf = sum(a["keyframes"] for a in e["animations"].values())
        dur = max((a["duration"] for a in e["animations"].values()), default=0)
        rows.append((rig, e["bones_total"], e["slots_total"], len(e["animations"]), kf, dur))
    for r in sorted(rows, key=lambda r: -r[4])[:12]:
        L.append(f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} | {r[4]:,} | {r[5]} |")

    L += ["", "## Event trong animation (dùng để căn thời điểm bắn/va chạm)", "",
          "| rig | animation | t (s) | event |", "|---|---|---:|---|"]
    for rig, anim, tsec, name, _i, _s in sorted(events_rows, key=lambda r: (r[0], r[1], r[2]))[:120]:
        L.append(f"| `{rig}` | `{anim}` | {tsec} | `{name}` |")
    if not events_rows:
        L.append("| — | không có event | — | — |")
    if ev_names:
        L += ["", "Đếm theo tên: " + ", ".join(f"`{k}`×{v}" for k, v in ev_names.most_common(20))]
    L += ["", "## Còn thiếu", "",
          "- Chưa map rig → đơn vị trong game (ship nào / boss nào) — cần đối chiếu `datas/spine.json`",
          "  (`atlas_asset_name`) với prefab.",
          "- `deform` / `drawOrder` chỉ đếm số mục, chưa xuất nội dung.",
          "- Chưa có `timeScale` runtime, nên thời lượng có thể ngắn hơn khi chơi thật.", ""]

    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
