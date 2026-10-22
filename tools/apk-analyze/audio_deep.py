#!/usr/bin/env python3
"""Diagnose / recover AudioClip audio from a stripped Unity build.

`unity_assets.py export` produced 0 WAV files for this build, so this script
tries the three routes UnityPy offers and reports which one works:

1. ``AudioClip.samples``                (raw AudioClipData -> WAV)
2. ``extract_audioclip_samples``        (helper, same data, different path)
3. ``obj.read()`` on the **AudioClip object** vs ``obj.read()`` on the
   ``AudioClip`` *Resource* entry inside FSB/``.resS`` side files

It also dumps the AudioClip typetree keys, which tells us whether the clip is
FSB-packed (``m_Resource``), streamed (``m_StreamData``) or empty.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

import UnityPy

EXTRACT = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
OUT = os.environ.get("AUDIO_OUT", "/tmp/apk/unity/audio")
REPORT = os.environ.get("AUDIO_REPORT", "docs/apk-analysis/17-audio-diagnose.md")


def load_env():
    files = [os.path.join(EXTRACT, f) for f in ("data.unity3d", "resources.resource")]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        raise SystemExit(f"no unity files under {EXTRACT}")
    return UnityPy.load(files)


def main() -> int:
    env = load_env()
    os.makedirs(OUT, exist_ok=True)
    stats = Counter()
    rows = []

    for obj in env.objects:
        if obj.type.name != "AudioClip":
            continue
        stats["clips"] += 1
        entry = {"path_id": obj.path_id, "name": "", "keys": [], "has_resource": None,
                 "streamed": None, "size_bytes": None, "samples": 0, "saved": None, "error": None}
        try:
            head = obj.read()
            entry["name"] = getattr(head, "m_Name", "") or ""
        except Exception as e:  # noqa: BLE001
            entry["error"] = f"read: {e!r}"
            rows.append(entry)
            continue
        # typetree keys tell us how the audio is stored
        try:
            tree = obj.read_typetree()
            entry["keys"] = sorted(tree.keys()) if isinstance(tree, dict) else []
            res = tree.get("m_Resource") if isinstance(tree, dict) else None
            if res is not None:
                stats["has_resource"] += 1
                entry["has_resource"] = True
                if isinstance(res, dict):
                    entry["resource"] = {k: v for k, v in res.items()
                                         if k in ("m_Source", "m_Offset", "m_Size")}
                    stats["res_bytes"] += int(res.get("m_Size") or 0)
                    src = str(res.get("m_Source") or "")
                    if src:
                        stats[f"src:{src[:40]}"] += 1
            sd = tree.get("m_StreamData") if isinstance(tree, dict) else None
            if isinstance(sd, dict):
                entry["streamed"] = bool(sd.get("path") or sd.get("offset"))
                if entry["streamed"]:
                    stats["streamed"] += 1
            size = tree.get("m_Size") if isinstance(tree, dict) else None
            if size:
                entry["size_bytes"] = int(size)
                stats["bytes"] += int(size)
        except Exception as e:  # noqa: BLE001
            entry["keys"] = [f"typetree error: {e!r}"]
            stats["typetree_fail"] += 1

        # route 1/2: samples
        for route in ("samples", "converter"):
            if entry["samples"]:
                break
            try:
                if route == "samples":
                    data = getattr(head, "samples", None) or {}
                else:
                    from UnityPy.export.AudioClipConverter import extract_audioclip_samples
                    data = extract_audioclip_samples(head) or {}
            except Exception as e:  # noqa: BLE001
                stats[f"{route}_error"] += 1
                entry[f"{route}_error"] = repr(e)[:200]
                continue
            if data:
                stats[f"{route}_ok"] += 1
                entry["samples"] = len(data)
                for sname, blob in data.items():
                    fn = f"{entry['name'] or obj.path_id}_{sname}.wav"
                    fn = "".join(c if c.isalnum() or c in "._-" else "_" for c in fn)[:120]
                    with open(os.path.join(OUT, fn), "wb") as f:
                        f.write(blob)
                    entry["saved"] = fn
                break
            if not data:
                stats[f"{route}_empty"] += 1
        if not entry["samples"]:
            stats["silent"] += 1
        rows.append(entry)

    # also look at resources exposed by the bundle (FSB / .resS side files)
    side = []
    try:
        for name in list(getattr(env, "files", {}).keys()):
            side.append(name)
    except Exception:  # noqa: BLE001
        pass

    lines = ["# Audio diagnosis", "",
             f"- clips: **{stats.get('clips', 0)}**",
             f"- có `m_Resource` (FSB trong bundle): **{stats.get('has_resource', 0)}**",
             f"- streamed (`m_StreamData`): **{stats.get('streamed', 0)}**",
             f"- xuất được WAV: **{stats.get('samples_ok', 0) + stats.get('converter_ok', 0)}**",
             f"- không xuất được: **{stats.get('silent', 0)}**",
             f"- tổng `m_Size` khai báo: **{stats.get('bytes', 0):,} bytes**", "",
             "## File trong bundle", "", "```"]
    lines += side[:40]
    lines += ["```", "", "## Từng clip (20 đầu)", "",
              "| path_id | name | resource | streamed | size | samples | saved |",
              "|---|---|---|---|---:|---:|---|"]
    for e in rows[:20]:
        lines.append(f"| {e['path_id']} | `{e['name'][:40]}` | {e['has_resource']} | "
                     f"{e['streamed']} | {e['size_bytes'] or ''} | {e['samples']} | {e['saved'] or '—'} |")
    keys = Counter(k for e in rows for k in e["keys"])
    lines += ["", "## Typetree keys (mọi clip)", "", "| key | số clip |", "|---|---:|"]
    for k, v in keys.most_common(40):
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "Kết luận: nếu `m_Resource`/`m_Size` có nhưng `samples` = 0 thì dữ liệu FSB nằm",
              "trong file audio riêng (`.resS`/`.resource`) chưa được extract — cần lấy thêm từ APK.", ""]

    os.makedirs(os.path.dirname(REPORT) or ".", exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(os.path.join(OUT, "audio-diagnose.json"), "w") as f:
        json.dump({"stats": dict(stats), "clips": rows}, f, indent=1)
    print("\n".join(lines[:24]))
    print("stats:", dict(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
