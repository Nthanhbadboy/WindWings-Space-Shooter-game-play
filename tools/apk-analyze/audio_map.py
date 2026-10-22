#!/usr/bin/env python3
"""Map the game's sound-id table to the exported audio files.

`SoundClip` (92 ScriptableObjects) is the game's sound registry:

    m_Name        = logical id used in code   ("Bgm_Boss1", "Sfx_Shoot")
    soundClip     = PPtr to the AudioClip     (path_id)

`04-asset-manifest.csv` now carries `path_id` for every exported asset, so the
two can be joined and the registry becomes a real audio map:

    datas/audio_map.json      sound id -> {path_id, file, seconds, channels}
    docs/apk-analysis/21-audio-map.md
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter

DOCS = os.environ.get("DOCS", "docs/apk-analysis")
OUT_JSON = os.environ.get("AUDIO_MAP_JSON", "datas/audio_map.json")
OUT_MD = os.environ.get("AUDIO_MAP_MD", "docs/apk-analysis/21-audio-map.md")
ASSETS_IDX = os.environ.get("AUDIO_IDX", "docs/assets/audio-index.csv")


def read_csv(path):
    if not os.path.isfile(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    manifest = read_csv(os.path.join(DOCS, "04-asset-manifest.csv"))
    audio_assets = {}
    for r in manifest:
        if r.get("type") != "AudioClip":
            continue
        pid = (r.get("path_id") or "").strip()
        if pid:
            audio_assets[pid] = {"name": r.get("name", ""), "file": r.get("path", ""),
                                 "bytes": int(r.get("bytes") or 0)}

    sound = read_csv(os.path.join(DOCS, "SoundClip.csv"))
    entries = []
    unresolved = 0
    for r in sound:
        pid = (r.get("soundClip.m_PathID") or "").strip()
        target = audio_assets.get(pid)
        if target is None:
            unresolved += 1
        entries.append({"sound_id": r.get("m_Name", ""), "clip_path_id": pid,
                        "clip_name": target["name"] if target else None,
                        "file": target["file"] if target else None,
                        "bytes": target["bytes"] if target else None})
    entries.sort(key=lambda e: e["sound_id"])

    # duration / format from the audio index (name based)
    dur = {}
    for r in read_csv(ASSETS_IDX):
        # index keys the sanitised export file name; match on its stem
        stem = os.path.splitext(os.path.basename(r.get("file", "")))[0]
        dur[stem] = r
        dur.setdefault(r.get("name", ""), r)
    for e in entries:
        stem = os.path.splitext(os.path.basename(e["file"] or ""))[0]
        d = dur.get(stem) or (dur.get(e["clip_name"]) if e["clip_name"] else None)
        if d:
            e["seconds"] = float(d.get("seconds") or 0)
            e["channels"] = int(d.get("channels") or 0)
            e["sample_rate"] = int(d.get("sample_rate") or 0)
            e["format"] = d.get("format", "")

    payload = {"source": "SoundClip.m_Name -> soundClip PPtr -> export manifest path_id",
               "count": len(entries), "resolved": len(entries) - unresolved,
               "unresolved": unresolved,
               "note": "Temporary: SoundClip sounds are the registry the code uses; "
                       "clips are the raw AudioClip assets.",
               "items": entries}
    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    kind = Counter()
    for e in entries:
        sid = e["sound_id"]
        kind["bgm" if sid.lower().startswith("bgm") else
             "sfx" if sid.lower().startswith("sfx") else "other"] += 1

    lines = ["# Audio map — sound id → file", "",
             "> **Kết luận tạm thời.** Join theo `path_id`; asset name lấy từ manifest export.",
             "", f"- tiếng trong registry (`SoundClip`): **{len(entries)}**",
             f"- resolve được ra file: **{len(entries) - unresolved}**",
             f"- nhóm: " + ", ".join(f"{k} {v}" for k, v in kind.most_common()), "",
             "| sound id | clip | giây | file |", "|---|---|---:|---|"]
    for e in entries[:120]:
        lines.append(f"| `{e['sound_id']}` | {e['clip_name'] or '—'} | "
                     f"{e.get('seconds', 0) or 0:.2f} | `{e['file'] or '—'}` |")
    lines += ["", f"- Bảng đầy đủ (JSON): [`datas/audio_map.json`](../../datas/audio_map.json)",
              "- File âm thanh thật: release `windwings-assets-1.3.118` → `AudioClip/`.",
              "- `clip_path_id` = pathID Unity, tra ngược bằng `datas/sprites.csv` không áp dụng",
              "  cho audio; dùng cột `file` là đường dẫn trong zip asset.", ""]
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines[:14]))
    print(f"unresolved: {unresolved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
