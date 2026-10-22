#!/usr/bin/env python3
"""Extract the wave / spawn composition of WindWings campaign maps.

`Call_Data` holds one spawner definition (spawn type, rate, speed, Y position,
enemy prefabs). Its GameObject path looks like

    Wave_0002/Path_CB3 (9)     -> wave index 2, path CB3, spawner 9

so grouping by the `Wave_NNNN` segment gives the full enemy composition of each
wave — the data the IL2CPP dump alone cannot provide.

Output:
    datas/waves.json                       (consumed by the data pack)
    docs/apk-analysis/16-waves.md          (human readable sample + stats)
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

EXTRACT = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
UNITY_VERSION = os.environ.get("UNITY_VERSION", "2022.3.62f3")
TTG_BACKEND = os.environ.get("TTG_BACKEND", "AssetStudio")
OUT_JSON = os.environ.get("WAVES_JSON", "datas/waves.json")
OUT_MD = os.environ.get("WAVES_MD", "docs/apk-analysis/16-waves.md")
MAX_WAVES = int(os.environ.get("MAX_WAVES", "4000"))

WAVE_RE = re.compile(r"(Wave_[0-9]+)")
SPAWN_TYPES = {0: "point", 1: "path", 2: "point_range", 3: "follow", 4: "formation",
               5: "boss", 6: "special"}


def load_env():
    files = [os.path.join(EXTRACT, f) for f in ("data.unity3d", "resources.resource")]
    files = [f for f in files if os.path.isfile(f)]
    env = UnityPy.load(files[0])
    for f in files[1:]:
        try:
            with open(f, "rb") as fh:
                env.load_file(fh, name=os.path.basename(f))
        except Exception:  # noqa: BLE001
            pass
    return env


def _path_of(go, depth=10):
    try:
        tr = None
        for c in getattr(go, "m_Component", None) or []:
            pptr = getattr(c, "component", None) or c
            comp = pptr.deref_parse_as_object()
            if comp.object_reader.type.name == "Transform":
                tr = comp
                break
        names, seen = [], set()
        while tr is not None and len(names) < depth:
            if id(tr) in seen:
                break
            seen.add(id(tr))
            names.append(tr.m_GameObject.deref_parse_as_object().m_Name)
            try:
                tr = tr.m_Father.deref_parse_as_object()
            except Exception:  # noqa: BLE001
                tr = None
        return "/".join(reversed(names))
    except Exception:  # noqa: BLE001
        return ""


def _pptr_ids(tree):
    """path_id list of listPrefabEnemies, resolved to names later."""
    out = []
    for pptr in tree.get("listPrefabEnemies") or []:
        pid = 0
        if isinstance(pptr, dict):            # typetree gives plain {"m_FileID","m_PathID"}
            pid = pptr.get("m_PathID", 0)
        else:
            pid = getattr(pptr, "m_PathID", 0)
            if not pid:
                try:
                    pid = getattr(pptr, "path_id", 0)
                except Exception:  # noqa: BLE001
                    pid = 0
        try:
            out.append(int(pid))
        except Exception:  # noqa: BLE001
            out.append(0)
    return out


def main() -> int:
    env = load_env()
    gen = TypeTreeGenerator(UNITY_VERSION, generator=TTG_BACKEND)
    with open(os.path.join(EXTRACT, "libil2cpp.so"), "rb") as f:
        il2cpp = f.read()
    with open(os.path.join(EXTRACT, "global-metadata.dat"), "rb") as f:
        metadata = f.read()
    gen.load_il2cpp(il2cpp, metadata)
    env.typetree_generator = gen
    print("typetree ready, backend", TTG_BACKEND)

    waves: dict[str, list] = defaultdict(list)
    seen_wave_ids: Counter = Counter()
    spawn_counter: Counter = Counter()
    path_counter: Counter = Counter()
    errors = 0
    needed_ids: set[int] = set()
    pending: list[tuple] = []

    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            head = obj.parse_monobehaviour_head()
            script = head.m_Script.deref_parse_as_object()
            if script.m_ClassName != "Call_Data":
                continue
            tree = obj.read_typetree()
        except Exception:  # noqa: BLE001
            errors += 1
            continue
        path = _path_of(head.m_GameObject.deref_parse_as_object())
        m = WAVE_RE.search(path)
        wave_id = m.group(1) if m else "unknown"
        spawn_type = int(tree.get("spawnType") or 0)
        path_name = path.split("/")[-1] if path else ""
        path_counter[path_name] += 1
        spawn_counter[SPAWN_TYPES.get(spawn_type, str(spawn_type))] += 1
        seen_wave_ids[wave_id] += 1
        ids = _pptr_ids(tree)
        needed_ids.update(i for i in ids if i)
        pending.append((wave_id, path_name, SPAWN_TYPES.get(spawn_type, str(spawn_type)), ids,
                        int(tree.get("number") or 0),
                        round(float(tree.get("rate") or 0), 3),
                        round(float(tree.get("speed") or 0), 3),
                        round(float(tree.get("ySpawn") or 0), 2),
                        round(float(tree.get("radius") or 0), 2)))

    # pass 2: path_id -> prefab name (cheap peek, no typetree)
    names: dict[int, str] = {}
    for obj in env.objects:
        if obj.path_id in needed_ids and obj.path_id not in names:
            try:
                nm = obj.peek_name()
            except Exception:  # noqa: BLE001
                nm = None
            if not nm:
                try:
                    nm = obj.read().m_Name
                except Exception:  # noqa: BLE001
                    nm = None
            if nm:
                names[obj.path_id] = nm
    print(f"resolved prefab names: {len(names)}/{len(needed_ids)}")

    # pass 3: group + dedupe identical spawners inside a wave
    for wave_id, path_name, spawn_type, ids, number, rate, speed, y_spawn, radius in pending:
        enemies = [names.get(i) or (f"pathID:{i}" if i else "?") for i in ids]
        key = (path_name, spawn_type, tuple(enemies), number, rate, speed, y_spawn, radius)
        bucket = waves[wave_id]
        for entry in bucket:
            if entry["_key"] == key:
                entry["copies"] += 1
                break
        else:
            bucket.append({"_key": key, "spawner": path_name, "spawn_type": spawn_type,
                           "enemies": enemies, "count": number, "rate": rate, "speed": speed,
                           "y_spawn": y_spawn, "radius": radius, "copies": 1})

    def wave_num(w):
        m2 = re.search(r"(\d+)", w)
        return int(m2.group(1)) if m2 else 10 ** 6

    ordered = sorted(waves.items(), key=lambda kv: wave_num(kv[0]))
    for _, spawners in ordered:
        for s_ in spawners:
            s_.pop("_key", None)
    payload = {
        "source": "Call_Data MonoBehaviours in data.unity3d, grouped by Wave_NNNN",
        "count_waves": len(ordered),
        "count_spawners": sum(len(v) for _, v in ordered),
        "note": ("enemies = prefab GameObject names referenced by listPrefabEnemies; "
                 "count=0 means the spawner uses a prefab list without an explicit count."),
        "waves": [{"wave": w, "spawners": v} for w, v in ordered],
    }
    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    enemy_freq = Counter()
    for _, spawners in ordered:
        for s in spawners:
            for e in s["enemies"]:
                enemy_freq[e] += s.get("copies", 1)

    lines = ["# Wave composition (campaign maps)", "",
             f"- waves: **{len(ordered)}**", f"- spawners: **{payload['count_spawners']}**",
             f"- typetree backend: **{TTG_BACKEND}**", ""]
    if errors:
        lines.append(f"- lỗi đọc: {errors} object")
        lines.append("")
    lines += ["## Spawn type", "", "| type | số spawner |", "|---|---:|"]
    for k, v in spawn_counter.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## Enemy prefab xuất hiện nhiều nhất", "",
              "| prefab | số spawner dùng |", "|---|---:|"]
    for k, v in enemy_freq.most_common(40):
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## 20 wave đầu", ""]
    for w, spawners in ordered[:20]:
        enemies = sorted({e for s in spawners for e in s["enemies"]})
        lines += [f"### `{w}` — {len(spawners)} spawner", "",
                  "| spawner | type | rate | speed | enemies |", "|---|---|---:|---:|---|"]
        for s in spawners[:12]:
            lines.append(f"| `{s['spawner']}` | {s['spawn_type']} | {s['rate']} | {s['speed']} | "
                         f"{', '.join(s['enemies'][:6]) or '—'} |")
        if len(spawners) > 12:
            lines.append(f"| … | | | | còn {len(spawners) - 12} spawner |")
        lines.append("")
    lines += ["## Ghi chú", "",
              "- Dữ liệu đầy đủ: [`datas/waves.json`](../../datas/waves.json).",
              "- `rate` = giây giữa 2 lần spawn; `speed` = tốc độ di chuyển của nhóm enemy.",
              "- Prefab name lấy từ `listPrefabEnemies[i].m_Name`; nếu trỏ tới prefab không nằm trong",
              "  `data.unity3d` thì ghi `pathID:<id>`.", ""]
    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines[:25]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
