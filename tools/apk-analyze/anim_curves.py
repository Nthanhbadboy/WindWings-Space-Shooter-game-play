#!/usr/bin/env python3
"""Thử đọc keyframe curve của `AnimationClip` bằng UnityPy `parse_as_object()`.

Bối cảnh: typetree cho `m_FloatCurves/m_PositionCurves/... = 0` ở mọi clip (xem
`26-native-animation.md`) — curve nằm trong streamed clip. Tool này dùng reader
chuyên dụng của UnityPy để lấy những gì reader đó thấy được, ghi lại trung thực
kể cả khi kết quả là 0 (khi đó kết luận "phải giải streamed clip thủ công" mới chắc).

Cần file gốc Unity (`UNITY_DATA`, mặc định `/tmp/apk/extract`) → chỉ chạy trên CI.
Mọi số liệu là **kết luận tạm thời**.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from collections import Counter

EXTRACT = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
OUT_JSON = os.environ.get("ANIM_CURVES_JSON", "datas/anim_clips.json.gz")
OUT_MD = os.environ.get("ANIM_CURVES_MD", "docs/apk-analysis/27-anim-curves.md")
MAX_CLIPS = int(os.environ.get("ANIM_MAX_CLIPS", "0"))  # 0 = tất cả


def curve_points(curve) -> list:
    """Keyframe của một AnimationCurve: [[time, value, inSlope, outSlope], ...]."""
    out = []
    raw = getattr(curve, "m_Curve", None) or []
    for kf in raw:
        try:
            out.append([round(float(kf.time), 4), round(float(kf.value), 5),
                        round(float(getattr(kf, "inSlope", 0.0)), 4),
                        round(float(getattr(kf, "outSlope", 0.0)), 4)])
        except (TypeError, ValueError, AttributeError):
            continue
    return out


def clip_summary(obj) -> dict | None:
    try:
        clip = obj.parse_as_object()
    except Exception:  # noqa: BLE001
        return None
    row: dict = {"path_id": obj.path_id, "name": getattr(clip, "m_Name", "") or ""}
    for attr in ("m_Legacy", "m_Compressed", "m_UseHighQualityCurve", "m_SampleRate"):
        if hasattr(clip, attr):
            row[attr[2:].lower()] = getattr(clip, attr)

    muscle = getattr(clip, "m_MuscleClip", None)
    info = getattr(muscle, "m_Info", None) if muscle is not None else None
    # thời lượng: ưu tiên m_StopTime của MuscleClip, fallback độ dài curve
    stop = None
    for holder in (muscle, info):
        if holder is not None and hasattr(holder, "m_StopTime"):
            try:
                stop = float(holder.m_StopTime)
                break
            except (TypeError, ValueError):
                pass
    if stop:
        row["duration"] = round(stop, 4)

    total_kf = 0
    curves_out = {}
    for attr, kind in (("m_RotationCurves", "rotation"), ("m_PositionCurves", "position"),
                       ("m_ScaleCurves", "scale"), ("m_EulerCurves", "euler"),
                       ("m_FloatCurves", "float"), ("m_PPtrCurves", "pptr")):
        curves = getattr(clip, attr, None) or []
        if not curves:
            continue
        entries = []
        for c in curves:
            pts = curve_points(getattr(c, "curve", None)) if kind != "pptr" else []
            total_kf += len(pts)
            entries.append({"path": getattr(c, "path", ""), "keyframes": pts})
        if entries:
            curves_out[kind] = entries
    row["keyframe_total"] = total_kf
    if curves_out:
        row["curves"] = curves_out

    events = getattr(clip, "m_Events", None) or []
    if events:
        row["events"] = [{"time": round(float(getattr(e, "time", 0.0)), 4),
                           "function": getattr(e, "functionName", "") or ""}
                          for e in events]
    return row


def main() -> int:
    import UnityPy

    files = [os.path.join(EXTRACT, f) for f in ("data.unity3d", "resources.resource")]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        print(f"không có file Unity trong {EXTRACT} — bỏ qua")
        write_md([], Counter())
        return 0

    env = UnityPy.load(*files)
    rows, kinds = [], Counter()
    seen = 0
    for obj in env.objects:
        if obj.type.name != "AnimationClip":
            continue
        seen += 1
        if MAX_CLIPS and seen > MAX_CLIPS:
            break
        row = clip_summary(obj)
        if row is None:
            kinds["parse_fail"] += 1
            continue
        kinds["parsed"] += 1
        if row.get("keyframe_total"):
            kinds["with_keyframes"] += 1
        rows.append(row)

    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    with gzip.open(OUT_JSON, "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump({"note": "Kết luận tạm thời. Keyframe đọc bằng UnityPy AnimationClip reader.",
                   "clips": rows}, fh, ensure_ascii=False, separators=(",", ":"))

    write_md(rows, kinds)
    total_kf = sum(r.get("keyframe_total", 0) for r in rows)
    print(f"AnimationClip: {kinds['parsed']} đọc được, {kinds['with_keyframes']} có keyframe, "
          f"{total_kf:,} keyframe -> {OUT_JSON}")
    return 0


def write_md(rows, kinds):
    with_kf = [r for r in rows if r.get("keyframe_total")]
    total_kf = sum(r.get("keyframe_total", 0) for r in rows)
    lines = ["# 27 — Keyframe của AnimationClip (kết luận tạm thời)", "",
             "> **Kết luận tạm thời.** Đọc bằng UnityPy `parse_as_object()` trên file gốc,",
             "> khác với typetree ở `26-native-animation.md` (nơi mọi curve đều = 0).", "",
             f"- clip đọc được: **{kinds.get('parsed', 0)}**, lỗi parse: **{kinds.get('parse_fail', 0)}**",
             f"- clip có keyframe: **{len(with_kf)}**, tổng keyframe: **{total_kf:,}**", ""]
    if with_kf:
        lines += ["| clip | thời lượng (s) | keyframe | loại curve |", "|---|---:|---:|---|"]
        for r in sorted(with_kf, key=lambda x: -x["keyframe_total"])[:30]:
            lines.append(f"| `{r['name']}` | {r.get('duration', '')} | {r['keyframe_total']} | "
                         f"{', '.join((r.get('curves') or {}).keys())} |")
    else:
        lines += ["**Reader này cũng không thấy keyframe nào** — curve nằm trong streamed clip",
                  "ở định dạng nén riêng; muốn lấy phải giải mã `m_StreamedClip` thủ công.",
                  "Kết luận thực dụng: dựng lại chuyển động Mecanim bằng số nhịp ở `26-native-animation.md`",
                  "(tên + thời lượng + loop + event), không chờ curve."]
    lines.append("")
    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
