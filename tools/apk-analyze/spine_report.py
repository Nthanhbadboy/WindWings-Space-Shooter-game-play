#!/usr/bin/env python3
"""Catalogue the Spine skeletal rigs used by ships / bosses / bosses-minions.

Ships and bosses are Spine animations, not sprite sheets. Each rig is a
`SkeletonDataAsset` pointing at a `skeleton` TextAsset (JSON) and an atlas
TextAsset. This joins them by path_id so every rig gets:

    identity hints (atlas region names, region count, Vietnamese part names),
    bones / slots / skins / animations (name + duration), events,
    the atlas page size (VRAM budget for re-rigging)

Output:
    datas/spine.json                     engine-agnostic rig spec
    docs/apk-analysis/22-spine-rigs.md   human summary
"""
from __future__ import annotations

import json
import os
import sys

import UnityPy

EXTRACT = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
UNITY_VERSION = os.environ.get("UNITY_VERSION", "2022.3.62f3")
TTG_BACKEND = os.environ.get("TTG_BACKEND", "AssetStudio")
OUT_JSON = os.environ.get("SPINE_JSON", "datas/spine.json")
OUT_MD = os.environ.get("SPINE_MD", "docs/apk-analysis/22-spine-rigs.md")


def load_env():
    files = [os.path.join(EXTRACT, f) for f in ("data.unity3d", "resources.resource")]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        raise SystemExit(f"no unity files under {EXTRACT}")
    env = UnityPy.load(*files)
    try:
        from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
        gen = TypeTreeGenerator(UNITY_VERSION, generator=TTG_BACKEND)
        with open(os.path.join(EXTRACT, "libil2cpp.so"), "rb") as f:
            il2cpp = f.read()
        with open(os.path.join(EXTRACT, "global-metadata.dat"), "rb") as f:
            meta = f.read()
        gen.load_il2cpp(il2cpp, meta)
        env.typetree_generator = gen
        print("typetree ready:", TTG_BACKEND)
    except Exception as e:  # noqa: BLE001
        print("no typetree:", repr(e)[:120])
    return env


def read_typetree(comp) -> dict:
    ro = getattr(comp, "object_reader", None)
    if ro is not None and hasattr(ro, "read_typetree"):
        try:
            return ro.read_typetree() or {}
        except Exception:  # noqa: BLE001
            pass
    try:
        return comp.read_typetree() or {}
    except Exception:  # noqa: BLE001
        return {}


def text_of(obj):
    try:
        d = obj.read()
        script = getattr(d, "m_Script", b"")
        if isinstance(script, str):
            return script
        return bytes(script).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return ""


def _max_time(node, depth=0) -> float:
    """Largest `time` key anywhere in an animation track tree (Shapes differ 3.8/4.x)."""
    if depth > 6:
        return 0.0
    best = 0.0
    if isinstance(node, dict):
        t = node.get("time")
        if isinstance(t, (int, float)):
            best = float(t)
        for v in node.values():
            best = max(best, _max_time(v, depth + 1))
    elif isinstance(node, list):
        for v in node:
            best = max(best, _max_time(v, depth + 1))
    return best


def skeleton_summary(raw: str) -> dict:
    try:
        d = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        return {"error": repr(e)[:200]}
    s = d.get("skeleton", {}) or {}
    anims = []
    for a in d.get("animations", {}) or {}:
        anims.append(a)
    durations = {}
    for name, body in (d.get("animations") or {}).items():
        durations[name] = round(_max_time(body), 3)
    raw_skins = d.get("skins") or {}
    if isinstance(raw_skins, dict):          # Spine 3.8: {"default": {...}}
        skins = list(raw_skins.keys())
    else:                                     # Spine 4.x: [{"name": "default", ...}]
        skins = [x.get("name", "") for x in raw_skins if isinstance(x, dict)]
    return {
        "spine_version": s.get("spine", ""),
        "size": [s.get("width"), s.get("height")],
        "bones": [b.get("name", "") for b in d.get("bones", []) or []],
        "slots": [x.get("name", "") for x in d.get("slots", []) or []],
        "skins": skins,
        "animations": anims,
        "animation_seconds": durations,
        "events": list((d.get("events") or {}).keys()),
    }


def atlas_summary(raw: str) -> dict:
    pages, regions = [], []
    cur = None
    for line in raw.replace("\r", "").split("\n"):
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith((".png", ".jpg")):
            if cur:
                pages.append(cur)
            cur = {"page": line.strip(), "size": ""}
            continue
        if cur is not None and line.startswith("size:"):
            cur["size"] = line.split(":", 1)[1].strip()
            continue
        if not line.startswith(" ") and cur is not None:
            regions.append(line.strip())
    if cur:
        pages.append(cur)
    return {"pages": pages, "regions": regions}


def main() -> int:
    env = load_env()
    text_assets = {}          # path_id -> bytes, name
    sdas = []                 # (path_id, typetree)
    for obj in env.objects:
        t = obj.type.name
        if t == "TextAsset":
            try:
                name = obj.peek_name() or ""
            except Exception:  # noqa: BLE001
                name = ""
            text_assets[obj.path_id] = (name, obj)
        elif t == "MonoBehaviour":
            try:
                head = obj.parse_monobehaviour_head()
                cls = head.m_Script.deref_parse_as_object().m_ClassName
            except Exception:  # noqa: BLE001
                continue
            if cls == "SkeletonDataAsset":
                sdas.append((obj.path_id, obj))
    print(f"TextAssets: {len(text_assets)}, SkeletonDataAssets: {len(sdas)}")

    rigs = []
    for pid, obj in sdas:
        tree = read_typetree(obj)
        sj = tree.get("skeletonJSON") or {}
        at = (tree.get("atlasAssets") or [{}])[0] or {}
        sj_pid = int(sj.get("m_PathID") or 0) if isinstance(sj, dict) else 0
        at_pid = int(at.get("m_PathID") or 0) if isinstance(at, dict) else 0
        sk_entry = text_assets.get(sj_pid)
        at_entry = text_assets.get(at_pid)
        rig = {"skeleton_data_path_id": pid, "skeleton_json_path_id": sj_pid,
               "atlas_path_id": at_pid,
               "skeleton_name": sk_entry[0] if sk_entry else None,
               "atlas_name": at_entry[0] if at_entry else None}
        if sk_entry:
            rig.update(skeleton_summary(text_of(sk_entry[1])))
        if at_entry:
            rig["atlas"] = atlas_summary(text_of(at_entry[1]))
        # identity hint: the atlas region names are the most descriptive signal
        regions = (rig.get("atlas") or {}).get("regions") or []
        rig["identity_hint"] = ", ".join(regions[:6])
        rigs.append(rig)

    rigs.sort(key=lambda r: (-len(r.get("animations") or []), r["skeleton_data_path_id"]))
    payload = {"source": "SkeletonDataAsset -> skeletonJSON / atlasAssets (path_id join)",
               "count": len(rigs),
               "note": "Temporary: rig identities are inferred from atlas region names; "
                       "the build does not store a human-readable rig name.",
               "rigs": rigs}
    os.makedirs(os.path.dirname(OUT_JSON) or ".", exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    total_anims = sum(len(r.get("animations") or []) for r in rigs)
    lines = ["# Spine rigs — tàu / boss", "",
             "> **Kết luận tạm thời.** Ghép theo `path_id`; tên rig suy ra từ tên region trong",
             "> atlas, không phải tên do dev đặt.", "",
             f"- rig: **{len(rigs)}**", f"- animation: **{total_anims}**", "",
             "## Tổng quan", "",
             "| rig (path_id) | bone | slot | skin | anim | atlas page | hint |",
             "|---|---:|---:|---:|---:|---|---|"]
    for r in rigs:
        pages = ", ".join(p["page"] for p in (r.get("atlas") or {}).get("pages", [])) or "—"
        lines.append(f"| `{r['skeleton_data_path_id']}` | {len(r.get('bones') or [])} "
                     f"| {len(r.get('slots') or [])} | {len(r.get('skins') or [])} "
                     f"| {len(r.get('animations') or [])} | {pages} "
                     f"| {(r.get('identity_hint') or '')[:40]} |")
    lines += ["", "## Animation theo rig", ""]
    for r in rigs[:20]:
        anims = r.get("animations") or []
        if not anims:
            continue
        secs = r.get("animation_seconds") or {}
        shown = ", ".join(f"`{a}`" + (f" ({secs[a]}s)" if secs.get(a) else "") for a in anims[:14])
        lines.append(f"- **{r['skeleton_data_path_id']}** — {len(anims)} anim: {shown}")
    lines += ["", "## Dùng để làm gì", "",
              "- `datas/spine.json` là spec rig cho bản mới: cùng bộ animation (Idle/Attack/…) nhưng",
              "  xương/skin do bạn vẽ lại.",
              "- `atlas.pages[].size` cho biết VRAM mỗi nhân vật chiếm bao nhiêu.",
              "- Tên region tiếng Việt (`Canh_Duoi_…`) cho thấy team gốc đặt tên theo bộ phận —",
              "  hữu ích khi rig lại.", ""]
    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines[:18]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
