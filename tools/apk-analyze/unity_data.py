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
    "Call_Point",
    # items / economy
    "Sub_Item",
    "Item_Movement",
    "Box_Rewards",
    "Shop_Cell",
    # bosses
    "Boss_BodyPhysics",
    "Boss4_ExplosionTimer",
    # --- lớp hành vi enemy (audit của nhánh spec chỉ ra: PathID đã nằm trong
    #     Enemy_Controller.dataScript/healthScript/... nên chỉ cần export là nối được 100%)
    "Enemy_Physics",
    "Enemy_Destroy",
    "Enemy_Burned",
    "Enemy_Stun",
    "Enemy_UI",
    "Enemy_LookAtPlayer",
    "Enemy_Attack",
    "Enemy_Attack_Event",
    "Enemy_Passive_Attack",
    "Enemy_Sync_Attack",
    "Enemy_Sync_Attack2",
    "Enemy_SpawnChilds",
    "Enemy_DestroyDelayed",
    "Enemy_DestroyAttack",
    "Enemy_BombDie",
    "Enemy_BurstBulletWhenDie",
    "Enemy_DropGold",
    "Enemy_Rotate",
    "Enemy_Helicopter",
    "Enemy_Display",
    "Enemy_Hp_Bar",
    "Enemy_Laser_Gun",
    "Enemy_Rocket_Attack",
    "Enemy_CameraVibrate",
    "Enemy_EfxDestroyed",
    "Enemy_OffObjectWhenDestroy",
    "Enemy_HitSkeletonRenderer",
    # managers that do get serialized
    "RankManager",
    "DataShopPack",
    "ArenaManager",
    "GP_Datas",
    "GridLayoutManager",
}

# 44 class đạo diễn boss/mini-boss sống ở tiền tố khác nhau (Boss1_Director,
# MB6_ChildDirector, Boss19_AttackPhases...). Ghép theo hậu tố để không phải
# liệt kê tay từng cái và không bỏ sót class mới khi game cập nhật.
TARGET_SUFFIXES = ("_Director", "_MiniDirector", "ChildDirector", "_AttackPhases")

TARGETS = CONFIG | RUNTIME


def is_target(cls: str) -> bool:
    return cls in TARGETS or cls.endswith(TARGET_SUFFIXES)

MAX_READ_PER_CLASS = int(os.environ.get("MAX_READ_PER_CLASS", "1500"))

# Bảng lớn bị cap 1.500 ở các lần chạy trước (audit nhánh spec §7.8): 6 bảng sinh quân
# + đường bay bị cắt. Chúng nén rất tốt (~1 MB gz cho toàn bộ typetree hiện có) nên
# đọc đủ rẻ hơn nhiều so với việc phải suy luận lại từ CSV đã làm phẳng list.
CAP_OVERRIDES = {
    "Call_Data": (30000, 24_000_000),
    "Call_Point": (30000, 12_000_000),
    "PointToPoint_Spawner": (14000, 12_000_000),
    "PinMap_Spawner": (3400, 10_000_000),
    "Rocket_Spawner": (2200, 6_000_000),
    "PathCreator": (1800, 12_000_000),
    "Path_Spawner": (1800, 6_000_000),
    "Transform": (300000, 60_000_000),
}
MAX_DUMP_PER_CLASS = int(os.environ.get("MAX_DUMP_PER_CLASS", "20"))
MAX_CSV_ROWS = int(os.environ.get("MAX_CSV_ROWS", "1200"))
MAX_RAW_BYTES_CLASS = int(os.environ.get("MAX_RAW_BYTES_CLASS", "4000000"))
MAX_RAW_BYTES_TOTAL = int(os.environ.get("MAX_RAW_BYTES_TOTAL", "220000000"))


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


def export_transform_tree(env) -> None:
    """Xuất cây cha–con của Transform + tên prefab gốc.

    Vì sao: audit của nhánh spec chỉ ra 5 mắt ghép = 0% **cùng một nguyên nhân** —
    component nằm trên object con, còn `Enemy_Controller` nằm trên object gốc; chuỗi
    nối duy nhất là `m_GameObject → Transform.m_Father → … → root`. Bảng `Transform`
    (228.432 object) chưa từng được export nên cả 5 mắt không nối được.

    Xuất dạng TSV gz (path_id, gameobject, father) để file nhỏ — JSON sẽ phình 5×.
    """
    import gzip

    tsv = os.path.join(RAW, "transform-tree.tsv.gz")
    rows = 0
    fathers: dict[int, int] = {}
    gos: dict[int, int] = {}
    try:
        with gzip.open(tsv, "wt", encoding="utf-8", compresslevel=9) as fh:
            fh.write("path_id\tgameobject\tfather\n")
            for obj in env.objects:
                if obj.type.name != "Transform":
                    continue
                try:
                    tree = obj.read_typetree()
                except Exception:  # noqa: BLE001
                    continue
                go = (tree.get("m_GameObject") or {}).get("m_PathID") or 0
                fa = (tree.get("m_Father") or {}).get("m_PathID") or 0
                fh.write(f"{obj.path_id}\t{go}\t{fa}\n")
                fathers[obj.path_id] = fa
                gos[obj.path_id] = go
                rows += 1
    except OSError:
        return
    print(f"transform tree: {rows} dòng -> {tsv}")

    # root = transform không có cha; chỉ đọc tên GameObject của đúng những root này
    children_of_root: Counter = Counter()
    for fa in fathers.values():
        if fa:
            children_of_root[fa] += 1
    roots = [pid for pid, fa in fathers.items() if not fa]
    go_of_root = {gos[pid] for pid in roots if gos.get(pid)}
    names: dict[int, str] = {}
    for obj in env.objects:
        if obj.type.name != "GameObject" or obj.path_id not in go_of_root:
            continue
        try:
            names[obj.path_id] = obj.read_typetree().get("m_Name") or ""
        except Exception:  # noqa: BLE001
            continue
    with open(os.path.join(RAW, "prefab-roots.csv"), "w", newline="", encoding="utf-8") as fh:
        fh.write("transform_path_id,gameobject_path_id,name,children\n")
        for tpid in sorted(roots):
            gpid = gos.get(tpid, 0)
            fh.write(f'{tpid},{gpid},"{names.get(gpid, "")}",{children_of_root.get(tpid, 0)}\n')
    print(f"prefab roots: {len(roots)}")


def export_native_types(env) -> None:
    """Xuất tóm tắt `AnimationClip` + `AnimatorController` (object gốc, không phải MonoBehaviour).

    Vì sao: 791 clip + 308 controller chưa từng được export — đây là lớp animation
    thứ hai ngoài Spine. Chỉ ghi **tóm tắt** (tên, độ dài, số curve/tham số/layer):
    curve đầy đủ rất nặng và muốn dựng lại chuyển động thì Spine đã đủ chi tiết hơn.
    `ParticleSystem` chỉ ghi `path_id` (typetree của nó gồm ~30 module, xuất hết sẽ phình).
    `Animator` ghi tóm tắt gồm `m_GameObject` + `m_Controller` để nối controller → prefab.
    """
    import gzip

    wanted = {"AnimationClip", "AnimatorController", "ParticleSystem", "Animator", "Camera"}
    counts: Counter = Counter()
    out_path = os.path.join(RAW, "native-types.jsonl.gz")
    written = 0
    with gzip.open(out_path, "wt", encoding="utf-8", compresslevel=9) as fh:
        for obj in env.objects:
            tname = obj.type.name
            if tname not in wanted:
                continue
            counts[tname] += 1
            if tname == "ParticleSystem":
                # Đọc typetree nhưng chỉ giữ scalar + scalar một cấp trong module:
                # đủ cho thời lượng/tốc độ/vòng lặp, không phình vì curve.
                try:
                    tree = obj.read_typetree()
                except Exception:  # noqa: BLE001
                    continue
                if not isinstance(tree, dict):
                    continue
                summary = {"type": tname, "path_id": obj.path_id}
                for key, val in tree.items():
                    if isinstance(val, (int, float, str, bool)) or val is None:
                        summary[key] = val
                    elif isinstance(val, dict):
                        scalars = {k: v for k, v in val.items()
                                   if isinstance(v, (int, float, str, bool))}
                        if scalars:
                            summary[key] = scalars
                    elif isinstance(val, list):
                        summary[f"{key}__count"] = len(val)
                line = json.dumps(summary, ensure_ascii=False, default=str)
                if len(line) > 20000:
                    continue
                fh.write(line + "\n")
                written += 1
                continue
            try:
                tree = obj.read_typetree()
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(tree, dict):
                continue
            summary = {"type": tname, "path_id": obj.path_id}
            for key, val in tree.items():
                if isinstance(val, (int, float, str, bool)) or val is None:
                    summary[key] = val
                elif isinstance(val, list):
                    summary[f"{key}__count"] = len(val)
                elif isinstance(val, dict):
                    # giữ lại các scalar một cấp (vd m_MuscleClipInfo)
                    scalars = {k: v for k, v in val.items()
                               if isinstance(v, (int, float, str, bool))}
                    if scalars:
                        summary[key] = scalars
            fh.write(json.dumps(summary, ensure_ascii=False, default=str) + "\n")
            written += 1
    print(f"native types: {dict(counts)}, tóm tắt đã ghi {written} -> {out_path}")


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
    PID_CLASS: dict = {}
    SCRIPT_LINKS: list = []
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
        class_cap = CAP_OVERRIDES.get(cls, (0, MAX_RAW_BYTES_CLASS))[1]
        if raw_bytes[cls] + len(line) > class_cap:
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
        PID_CLASS[obj.path_id] = cls
        if not is_target(cls):
            continue
        if counts[cls] >= CAP_OVERRIDES.get(cls, (MAX_READ_PER_CLASS, 0))[0]:
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
        # ghi lại mọi PPtr tên "*Script" để biết field nào trỏ tới class nào
        for k, v in tree.items():
            if not k.endswith("Script") or not isinstance(v, dict):
                continue
            tpid = v.get("m_PathID") or 0
            if tpid:
                SCRIPT_LINKS.append({"owner_class": cls, "owner_path_id": obj.path_id,
                                     "field": k, "target_path_id": tpid})
        raw_write(cls, {"path_id": obj.path_id, "gameobject": go_name, "tree": tree})
        if counts[cls] <= MAX_DUMP_PER_CLASS:
            safe = f"{ns}.{cls}" if ns else cls
            d = os.path.join(OUT, safe)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"{obj.path_id}.json"), "w") as f:
                json.dump(tree, f, indent=1, default=str)
            if len(samples[cls]) < 2:
                samples[cls].append(flat)

    # ------------------------------------------------------- script link map
    if SCRIPT_LINKS:
        os.makedirs(RAW, exist_ok=True)
        path = os.path.join(RAW, "script-links.jsonl.gz")
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            for row in SCRIPT_LINKS:
                row["target_class"] = PID_CLASS.get(row["target_path_id"], "")
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"script links: {len(SCRIPT_LINKS)} -> {path}")

    try:
        export_transform_tree(env)
    except Exception as e:  # noqa: BLE001
        print(f"transform tree failed (bỏ qua): {e!r}")
    try:
        export_native_types(env)
    except Exception as e:  # noqa: BLE001
        print(f"native types failed (bỏ qua, các bảng khác vẫn dùng được): {e!r}")

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
