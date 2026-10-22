#!/usr/bin/env python3
"""Extract ScriptableObject data from WindWings using IL2CPP-generated typetrees.

UnityPy can rebuild MonoBehaviour typetrees from `libil2cpp.so` +
`global-metadata.dat` (TypeTreeGeneratorAPI), which is the only way to read the
actual designer values out of a stripped IL2CPP player build.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

EXTRACT = "/tmp/apk/extract"
OUT = "/tmp/apk/unity/data"
REPORT = "/tmp/apk/unity/data-report.md"
UNITY_VERSION = os.environ.get("UNITY_VERSION", "2022.3.62f3")
# ScriptableObjects found in the build + the designer-data MonoBehaviours that
# hold the actual balance numbers (damage, hp, costs, waves, ranks ...).
TARGETS = {
    # ScriptableObjects
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
    "StyleSheet",
    "TextSettings",
    "TextStyleSheet",
    "TextColorGradient",
    "PanelSettings",
    "GlobalDisplaySettings",
    # balance / save data components
    "Player_Get_Datas",
    "Player_Datas",
    "Player_Saved_Datas",
    "Player_Device_Saved_Datas",
    "Drone_Get_Datas",
    "Drone_Saved_Datas",
    "Device_Get_Data",
    "Device_Saved_Data",
    "Enemy_Get_Datas",
    "Enemy_Datas",
    "Enemy_Data_Balance",
    "Droid_Data_Balance",
    "Stage_Get_Datas",
    "Stage_Datas",
    "Map_Get_Datas",
    "Tech_Datas",
    "Bonus_Get_Datas",
    "GameDatas",
    "DataShopPack",
    "ConvertDatas",
    "GP_Datas",
    "RankManager",
    "ArenaManager",
    "IAP_Manager",
}
MAX_DUMP_PER_CLASS = int(os.environ.get("MAX_DUMP_PER_CLASS", "25"))


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def load_env() -> UnityPy.Environment:
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
    env = load_env()
    print("loaded files:", list(getattr(env, "files", {}).keys()))
    backend = os.environ.get("TTG_BACKEND", "AssetStudio")
    print("typetree backend:", backend)
    gen = TypeTreeGenerator(UNITY_VERSION, generator=backend)
    with open(os.path.join(EXTRACT, "libil2cpp.so"), "rb") as f:
        il2cpp = f.read()
    with open(os.path.join(EXTRACT, "global-metadata.dat"), "rb") as f:
        metadata = f.read()
    gen.load_il2cpp(il2cpp, metadata)
    env.typetree_generator = gen
    print("typetree generator ready")

    counts = Counter()
    errors = Counter()
    samples = defaultdict(list)
    records = defaultdict(list)

    for n, obj in enumerate(env.objects):
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            head = obj.parse_monobehaviour_head()
            script = head.m_Script.deref_parse_as_object()
            cls = script.m_ClassName
            ns = script.m_Namespace
            asm = script.m_AssemblyName
        except Exception as e:  # noqa: BLE001
            errors["script"] += 1
            continue
        if cls not in TARGETS:
            continue
        try:
            tree = obj.read_typetree()
        except Exception as e:  # noqa: BLE001
            errors[f"typetree:{cls}"] += 1
            if len(samples[cls]) < 3:
                samples[cls].append(f"ERROR {e!r}")
            continue
        counts[cls] += 1
        flat = flatten(tree)
        records[cls].append((obj.path_id, flat))
        safe = f"{ns}.{cls}" if ns else cls
        if counts[cls] <= MAX_DUMP_PER_CLASS:
            d = os.path.join(OUT, safe)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"{obj.path_id}.json"), "w") as f:
                json.dump(tree, f, indent=1, default=str)
            if len(samples[cls]) < 2:
                samples[cls].append(flat)

    lines = ["# ScriptableObject / MonoBehaviour data (IL2CPP typetrees)", "",
             f"- source: `{EXTRACT}`", f"- Unity: `{UNITY_VERSION}`", ""]
    lines.append("| class | instances |")
    lines.append("|---|---:|")
    for cls, c in counts.most_common():
        lines.append(f"| `{cls}` | {c} |")
    lines.append("")
    for cls, errs in errors.items():
        lines.append(f"- error `{cls}`: {errs}")
    lines.append("")
    for cls, items in samples.items():
        lines.append(f"## `{cls}` samples")
        lines.append("")
        for s in items:
            lines.append("```json")
            lines.append(json.dumps(s, indent=1, default=str)[:4000])
            lines.append("```")
        lines.append("")

    # flat CSV for every dumped class (max 25 rows / 400 columns per file)
    for cls, rows in records.items():
        if not rows:
            continue
        keys = sorted({k for _, r in rows for k in r})[:400]
        with open(os.path.join(OUT, f"{cls}.csv"), "w") as f:
            f.write(",".join(['"path_id"'] + ['"' + k + '"' for k in keys]) + "\n")
            for path_id, r in rows[:25]:
                f.write(",".join(['"' + str(path_id) + '"'] + ['"' + str(r.get(k, "")).replace('"', '""') + '"' for k in keys]) + "\n")

    open(REPORT, "w").write("\n".join(lines))
    print("\n".join(lines[:60]))
    print("errors:", dict(errors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
