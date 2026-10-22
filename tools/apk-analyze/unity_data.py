#!/usr/bin/env python3
"""Extract ScriptableObject / MonoBehaviour values from WindWings.

UnityPy can rebuild MonoBehaviour typetrees from `libil2cpp.so` +
`global-metadata.dat` (TypeTreeGeneratorAPI), which is the only way to read the
actual designer values out of a stripped IL2CPP player build.

Two groups of classes are dumped:

* **config**   — the ScriptableObjects (Data_Players, IAPProduct, LanguageAssets ...)
* **runtime**  — gameplay components that actually hold balance numbers
                 (Gun_Attack → damage, Call_Data → wave composition,
                  Enemy_Datas → HP, ...)

Per-class caps keep the output small: only `MAX_READ_PER_CLASS` objects are
typetree-read, `MAX_DUMP_PER_CLASS` are written as JSON, `MAX_CSV_ROWS` go to CSV.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

EXTRACT = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
OUT = "/tmp/apk/unity/data"
RAW = "/tmp/apk/unity/raw/typetrees"          # untouched typetree JSON, gzipped
REPORT = "/tmp/apk/unity/data-report.md"
UNITY_VERSION = os.environ.get("UNITY_VERSION", "2022.3.62f3")
TTG_BACKEND = os.environ.get("TTG_BACKEND", "AssetStudio")

# ---------------------------------------------------------------- config group
CONFIG = {
    "Data_Players",
    "Data_Boss",
    "Data_Items",
    "Tech_Ability_Data",
    "IAPProduct",
    "LanguageStringData",
    "LanguageAssets",
    "SoundClip",
    "SkeletonDataAsset",
    "AnimationReferenceAsset",
    "EventDataReferenceAsset",
    "TMP_Settings",
    "TMP_StyleSheet",
    "TMP_ColorGradient",
    "PanelSettings",
    "GlobalDisplaySettings",
}

# --------------------------------------------------------------- runtime group
# These are the components that carry the numbers the balance report needs.
RUNTIME = {
    # weapons / bullets
    "Gun_Attack",
    "Bullet_Linearly",
    "Bullet_SineWave",
    "Player19Laser",
    "Rocket_Spawner",
    # enemies / waves / maps
    "Enemy_Datas",
    "Enemy_Health",
    "Enemy_Controller",
    "Enemy_Movement",
    "Enemy_Sub",
    "Enemy_Appear",
    "Wave",
    "Call_Data",
    "Spawner",
    "PointToPoint_Spawner",
    "PinMap_Spawner",
    "Path_Spawner",
    "AirFree_Spawner",
    "Waypoints_Spawner",
    "MeteoriteGenerator",
    "MapController",
    "PathCreator",
    "Stage_Behaviour",
    # items / economy
    "Sub_Item",
    "Item_Movement",
    "Box_Rewards",
    "Shop_Cell",
    # bosses
    "Boss_BodyPhysics",
    "Boss4_ExplosionTimer",
    # managers that do get serialized
    "RankManager",
    "DataShopPack",
    "ArenaManager",
    "GP_Datas",
    "GridLayoutManager",
}

TARGETS = CONFIG | RUNTIME

MAX_READ_PER_CLASS = int(os.environ.get("MAX_READ_PER_CLASS", "1500"))
MAX_DUMP_PER_CLASS = int(os.environ.get("MAX_DUMP_PER_CLASS", "20"))
MAX_CSV_ROWS = int(os.environ.get("MAX_CSV_ROWS", "1200"))
MAX_RAW_BYTES_CLASS = int(os.environ.get("MAX_RAW_BYTES_CLASS", "4000000"))
MAX_RAW_BYTES_TOTAL = int(os.environ.get("MAX_RAW_BYTES_TOTAL", "45000000"))


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def _component_transform(go):
    for c in getattr(go, "m_Component", None) or []:
        pptr = getattr(c, "component", None) or c
        try:
            comp = pptr.deref_parse_as_object()
        except Exception:  # noqa: BLE001
            continue
        try:
            if comp.object_reader.type.name == "Transform":
                return comp
        except Exception:  # noqa: BLE001
            pass
    return None


def gameobject_path(go, depth=10):
    """`root/child/grandchild` name path for a GameObject (best effort)."""
    try:
        tr = _component_transform(go)
        names, seen = [], set()
        while tr is not None and len(names) < depth:
            if id(tr) in seen:
                break
            seen.add(id(tr))
            try:
                names.append(tr.m_GameObject.deref_parse_as_object().m_Name)
            except Exception:  # noqa: BLE001
                break
            try:
                tr = tr.m_Father.deref_parse_as_object()
            except Exception:  # noqa: BLE001
                tr = None
        return "/".join(reversed([n for n in names if n]))
    except Exception:  # noqa: BLE001
        return ""


def load_env() -> UnityPy.Environment:
    files = [os.path.join(EXTRACT, f) for f in ("data.unity3d", "resources.resource")]
    files = [f for f in files if os.path.isfile(f)]
    return UnityPy.load(*files)


def flatten(value, prefix="", out=None, depth=0):
    if out is None:
        out = {}
    if depth > 4:
        return out
    if isinstance(value, dict):
        for k, v in value.items():
            flatten(v, f"{prefix}.{k}" if prefix else k, out, depth + 1)
    elif isinstance(value, (list, tuple)):
        out[prefix] = f"[{len(value)}]"
        for i, v in enumerate(value[:5]):
            flatten(v, f"{prefix}[{i}]", out, depth + 1)
    else:
        if hasattr(value, "name"):  # PPtr
            try:
                value = value.deref_parse_as_object().m_Name
            except Exception:  # noqa: BLE001
                value = str(value)
        if isinstance(value, (bytes, bytearray)):
            value = f"<{len(value)} bytes>"
        out[prefix] = value
    return out


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    env = load_env()
    print("loaded files:", list(getattr(env, "files", {}).keys()))
    gen = TypeTreeGenerator(UNITY_VERSION, generator=TTG_BACKEND)
    print("typetree backend:", TTG_BACKEND)
    with open(os.path.join(EXTRACT, "libil2cpp.so"), "rb") as f:
        il2cpp = f.read()
    with open(os.path.join(EXTRACT, "global-metadata.dat"), "rb") as f:
        metadata = f.read()
    gen.load_il2cpp(il2cpp, metadata)
    env.typetree_generator = gen
    print("typetree generator ready")

    import gzip
    raw_files: dict[str, object] = {}
    raw_bytes: Counter = Counter()
    raw_written: Counter = Counter()

    def raw_write(cls: str, payload: dict) -> None:
        """Append one object to <Class>.jsonl.gz, respecting the size caps."""
        if sum(raw_bytes.values()) > MAX_RAW_BYTES_TOTAL:
            return
        fh = raw_files.get(cls)
        if fh is None:
            path = os.path.join(RAW, f"{cls}.jsonl.gz")
            fh = gzip.open(path, "wt", encoding="utf-8")
            raw_files[cls] = fh
        line = json.dumps(payload, ensure_ascii=False, default=str)
        if raw_bytes[cls] + len(line) > MAX_RAW_BYTES_CLASS:
            return
        fh.write(line + "\n")
        raw_bytes[cls] += len(line)
        raw_written[cls] += 1

    inventory: Counter = Counter()
    counts: Counter = Counter()
    errors: Counter = Counter()
    samples = defaultdict(list)
    records = defaultdict(list)
    skipped_cap = Counter()

    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            head = obj.parse_monobehaviour_head()
            script = head.m_Script.deref_parse_as_object()
            cls = script.m_ClassName
            ns = script.m_Namespace
        except Exception:  # noqa: BLE001
            errors["script"] += 1
            continue
        inventory[cls] += 1
        if cls not in TARGETS:
            continue
        if counts[cls] >= MAX_READ_PER_CLASS:
            skipped_cap[cls] += 1
            continue
        try:
            tree = obj.read_typetree()
        except Exception as e:  # noqa: BLE001
            errors[f"typetree:{cls}"] += 1
            if len(samples[cls]) < 2:
                samples[cls].append(f"ERROR {e!r}")
            continue
        counts[cls] += 1
        flat = flatten(tree)
        try:
            go_name = gameobject_path(head.m_GameObject.deref_parse_as_object())
        except Exception:  # noqa: BLE001
            go_name = ""
        if go_name:
            flat["_gameobject"] = go_name
        records[cls].append((obj.path_id, flat))
        raw_write(cls, {"path_id": obj.path_id, "gameobject": go_name, "tree": tree})
        if counts[cls] <= MAX_DUMP_PER_CLASS:
            safe = f"{ns}.{cls}" if ns else cls
            d = os.path.join(OUT, safe)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"{obj.path_id}.json"), "w") as f:
                json.dump(tree, f, indent=1, default=str)
            if len(samples[cls]) < 2:
                samples[cls].append(flat)

    for fh in raw_files.values():
        try:
            fh.close()
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------ inventory
    with open(os.path.join(OUT, "class-inventory.csv"), "w") as f:
        f.write("class,instances\n")
        for cls, c in inventory.most_common():
            f.write(f'"{cls}",{c}\n')

    # ------------------------------------------------------------- report
    lines = ["# ScriptableObject / MonoBehaviour data (IL2CPP typetrees)", "",
             f"- source: `{EXTRACT}`", f"- Unity: `{UNITY_VERSION}`",
             f"- typetree backend: **{TTG_BACKEND}**", "",
             "| class | instances | dumped |", "|---|---:|---:|"]
    for cls, c in counts.most_common():
        lines.append(f"| `{cls}` | {inventory[cls]} | {c} |")
    lines.append("")
    half = [(c, n) for c, n in skipped_cap.items()]
    if half:
        lines += ["Ghi chú: các class sau bị **cắt bớt** (chỉ đọc mẫu, không dump hết):", ""]
        for c, n in sorted(half, key=lambda x: -x[1])[:15]:
            lines.append(f"- `{c}`: còn {n} object chưa đọc")
        lines.append("")
    for cls, errs in errors.items():
        lines.append(f"- error `{cls}`: {errs}")
    lines.append("")

    if raw_written:
        lines += ["## Raw typetree dump (giữ nguyên)", "",
                  f"- thư mục: `{RAW}` (`<Class>.jsonl.gz`, mỗi dòng 1 object, **không cắt field**)",
                  "- đây là dữ liệu thô để đối chiếu lại mọi kết luận sau này", "",
                  "| class | object | bytes (chưa nén) |", "|---|---:|---:|"]
        for cls, n in raw_written.most_common(30):
            lines.append(f"| `{cls}` | {n} | {raw_bytes[cls]:,} |")
        lines.append("")

    lines += ["## MonoBehaviour class inventory (top 40)", "",
              "Toàn bộ class name trong `data.unity3d` (đầy đủ: `class-inventory.csv`)", "",
              "| class | instances |", "|---|---:|"]
    for cls, c in inventory.most_common(40):
        lines.append(f"| `{cls}` | {c} |")
    lines.append("")

    for cls, items in samples.items():
        lines += [f"## `{cls}` samples", ""]
        for s in items:
            lines += ["```json", json.dumps(s, indent=1, default=str)[:4000], "```"]
        lines.append("")

    # ---------------------------------------------------------------- CSV
    for cls, rows in records.items():
        if not rows:
            continue
        keys = sorted({k for _, r in rows for k in r})
        priority = [k for k in ("_gameobject",) if k in keys]
        keys = priority + [k for k in keys if k not in priority][:400]
        with open(os.path.join(OUT, f"{cls}.csv"), "w") as f:
            f.write(",".join(['"path_id"'] + ['"' + k + '"' for k in keys]) + "\n")
            for path_id, r in rows[:MAX_CSV_ROWS]:
                f.write(",".join(['"' + str(path_id) + '"'] +
                                 ['"' + str(r.get(k, "")).replace('"', '""') + '"' for k in keys]) + "\n")

    open(REPORT, "w").write("\n".join(lines))
    print("\n".join(lines[:50]))
    print("errors:", dict(errors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
