#!/usr/bin/env python3
"""Dump the UI layout of every Board_* / Popup_* screen as numbers.

Unity stores UI layout in `RectTransform` components of the prefab, not in the
C# code. This walks each screen's transform subtree and records, per node:

    path, anchors, anchoredPosition, sizeDelta, pivot, scale, active,
    component classes, text (TMP) and sprite name

so the layout can be rebuilt in another engine instead of eyeballing screenshots.

Reads through UnityPy's generated classes (attributes), falling back to
`read_typetree()` with an IL2CPP generator when a field is not exposed.

Raw output (kept, gzipped):
    reverse-engineering/raw/ui/<Class>__<path_id>.json.gz
    reverse-engineering/raw/ui/_index.csv
Human summary:
    docs/apk-analysis/20-ui-layout.md
"""
from __future__ import annotations

import csv
import gzip
import json
import os
import sys
from collections import Counter

import UnityPy

EXTRACT = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
OUT_RAW = os.environ.get("UI_RAW", "reverse-engineering/raw/ui")
OUT_MD = os.environ.get("UI_MD", "docs/apk-analysis/20-ui-layout.md")
UNITY_VERSION = os.environ.get("UNITY_VERSION", "2022.3.62f3")
TTG_BACKEND = os.environ.get("TTG_BACKEND", "AssetStudio")
MAX_NODES = int(os.environ.get("UI_MAX_NODES", "2000"))
MAX_COMPONENTS = int(os.environ.get("UI_MAX_COMPONENTS", "12"))
MAX_BYTES = int(os.environ.get("UI_MAX_BYTES", "3000000"))
ROOT_PREFIXES = ("Board_", "Popup_", "Tab_")
TRANSFORM_TYPES = ("Transform", "RectTransform")
RECT_KEYS = ("m_AnchorMin", "m_AnchorMax", "m_AnchoredPosition", "m_SizeDelta", "m_Pivot")


def load_env():
    files = [os.path.join(EXTRACT, f) for f in ("data.unity3d", "resources.resource")]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        raise SystemExit(f"no unity files under {EXTRACT}")
    env = UnityPy.load(*files)
    # typetrees are stripped from IL2CPP release builds -> rebuild them
    try:
        from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
        gen = TypeTreeGenerator(UNITY_VERSION, generator=TTG_BACKEND)
        with open(os.path.join(EXTRACT, "libil2cpp.so"), "rb") as f:
            il2cpp = f.read()
        with open(os.path.join(EXTRACT, "global-metadata.dat"), "rb") as f:
            meta = f.read()
        gen.load_il2cpp(il2cpp, meta)
        env.typetree_generator = gen
        print("typetree generator ready:", TTG_BACKEND)
    except Exception as e:  # noqa: BLE001
        print("no typetree generator (attributes only):", repr(e)[:160])
    return env


def _pptr(value):
    if value is None:
        return None
    if isinstance(value, dict):
        return None                     # plain dicts from read_typetree: not dereferenceable
    try:
        return value.deref_parse_as_object()
    except Exception:  # noqa: BLE001
        return None


def _type_name(comp):
    try:
        return comp.object_reader.type.name
    except Exception:  # noqa: BLE001
        try:
            return comp.read_typetree_name() if hasattr(comp, "read_typetree_name") else ""
        except Exception:  # noqa: BLE001
            return ""


def components_of(go):
    comps = []
    try:
        arr = go.m_Component or []
    except Exception:  # noqa: BLE001
        arr = []
    for c in arr[:MAX_COMPONENTS]:
        pptr = getattr(c, "component", None) or getattr(c, "m_Component", None) or c
        comp = _pptr(pptr)
        if comp is not None:
            comps.append(comp)
    return comps


def transform_of(go):
    for comp in components_of(go):
        if _type_name(comp) in TRANSFORM_TYPES:
            return comp
    return None


def script_class(comp):
    try:
        head = comp.parse_monobehaviour_head()
        script = head.m_Script.deref_parse_as_object()
        return script.m_ClassName or "MonoBehaviour"
    except Exception:  # noqa: BLE001
        return "MonoBehaviour"


def _xy(value):
    if value is None:
        return None
    try:
        return [round(float(value.x), 3), round(float(value.y), 3)]
    except Exception:  # noqa: BLE001
        pass
    if isinstance(value, dict):
        try:
            return [round(float(value.get("x", 0)), 3), round(float(value.get("y", 0)), 3)]
        except Exception:  # noqa: BLE001
            return None
    return None


def _xyz(value):
    if value is None:
        return None
    try:
        return [round(float(value.x), 3), round(float(value.y), 3), round(float(value.z), 3)]
    except Exception:  # noqa: BLE001
        pass
    if isinstance(value, dict):
        try:
            return [round(float(value.get(k, 0)), 3) for k in ("x", "y", "z")]
        except Exception:  # noqa: BLE001
            return None
    return None


def rect_fields(tr):
    """RectTransform layout via attributes, then via typetree."""
    out = {}
    names = {"m_AnchorMin": "anchor_min", "m_AnchorMax": "anchor_max",
             "m_AnchoredPosition": "anchored_pos", "m_SizeDelta": "size_delta",
             "m_Pivot": "pivot"}
    got_any = False
    for src, key in names.items():
        val = getattr(tr, src, None)
        out[key] = _xy(val)
        if out[key] is not None:
            got_any = True
    out["scale"] = _xyz(getattr(tr, "m_LocalScale", None))
    if not got_any:
        try:
            tree = tr.read_typetree()
            for src, key in names.items():
                out[key] = _xy(tree.get(src))
            out["scale"] = _xyz(tree.get("m_LocalScale"))
        except Exception:  # noqa: BLE001
            pass
    return out


def node_info(tr):
    go = _pptr(getattr(tr, "m_GameObject", None))
    if go is None:
        return None
    name = ""
    active = 1
    try:
        name = go.m_Name or ""
        active = int(getattr(go, "m_IsActive", 1) or 0)
    except Exception:  # noqa: BLE001
        pass
    comps = []
    for comp in components_of(go):
        cname = script_class(comp) if _type_name(comp) == "MonoBehaviour" else _type_name(comp)
        entry = {"class": cname}
        if any(k in cname for k in ("Text", "Input", "Label")):
            try:
                tree = comp.read_typetree()
                txt = tree.get("m_text")
                if isinstance(txt, str) and txt.strip():
                    entry["text"] = txt[:200]
                for k in ("key", "m_Key", "localizeKey", "keyLocalize"):
                    v = tree.get(k)
                    if isinstance(v, str) and v.strip():
                        entry["key"] = v[:120]
                        break
            except Exception:  # noqa: BLE001
                pass
        if "Image" in cname or "Sprite" in cname or "Renderer" in cname:
            try:
                sp = _pptr(getattr(comp, "m_Sprite", None))
                if sp is not None:
                    entry["sprite"] = (getattr(sp, "m_Name", "") or "")[:80]
            except Exception:  # noqa: BLE001
                pass
        comps.append(entry)
    node = {"name": name, "active": active, "components": comps}
    node.update(rect_fields(tr))
    return node


def walk(root, budget):
    out = []
    queue = [(root, "", 0)]
    seen = set()
    while queue and len(out) < budget:
        tr, parent_path, depth = queue.pop(0)
        if tr is None:
            continue
        key = getattr(tr, "path_id", id(tr))
        if key in seen:
            continue
        seen.add(key)
        node = node_info(tr)
        if node is None:
            continue
        path = f"{parent_path}/{node['name']}" if parent_path else node["name"]
        node.update({"path": path, "depth": depth})
        out.append(node)
        try:
            children = tr.m_Children or []
        except Exception:  # noqa: BLE001
            children = []
        for ch in children[:80]:
            child = _pptr(ch)
            if child is not None:
                queue.append((child, path, depth + 1))
    return out


def main() -> int:
    env = load_env()
    os.makedirs(OUT_RAW, exist_ok=True)
    index, seen_roots = [], set()

    candidates = []
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            head = obj.parse_monobehaviour_head()
            cls = head.m_Script.deref_parse_as_object().m_ClassName or ""
        except Exception:  # noqa: BLE001
            continue
        if cls.startswith(ROOT_PREFIXES):
            candidates.append((cls, head))
    print(f"screen candidates: {len(candidates)}")

    skipped = Counter()
    for cls, head in candidates:
        go = _pptr(getattr(head, "m_GameObject", None))
        if go is None:
            skipped["no gameobject"] += 1
            continue
        # climb to the outermost transform
        cur, top = go, go
        for _ in range(24):
            tr = transform_of(cur)
            if tr is None:
                break
            father = _pptr(getattr(tr, "m_Father", None))
            if father is None:
                break
            fgo = _pptr(getattr(father, "m_GameObject", None))
            if fgo is None:
                break
            cur = top = fgo
        root_key = getattr(top, "path_id", id(top))
        if root_key in seen_roots:
            continue
        seen_roots.add(root_key)
        top_tr = transform_of(top)
        if top_tr is None:
            skipped["no transform"] += 1
            continue
        nodes = walk(top_tr, MAX_NODES)
        if not nodes:
            skipped["empty subtree"] += 1
            continue
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in cls)[:80]
        fn = os.path.join(OUT_RAW, f"{safe}__{root_key}.json.gz")
        payload = {"class": cls, "root_path_id": root_key, "nodes": nodes,
                   "note": "RectTransform layout as stored in the prefab. Temporary: runtime "
                           "layout groups / safe area may override these numbers."}
        with gzip.open(fn, "wt", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        size = os.path.getsize(fn)
        if size > MAX_BYTES:
            os.remove(fn)
            skipped["too big"] += 1
            continue
        index.append({"class": cls, "root_path_id": root_key, "nodes": len(nodes),
                      "text_nodes": sum(1 for n in nodes
                                        if any("text" in c for c in n["components"])),
                      "buttons": sum(1 for n in nodes
                                     if any("Button" in c["class"] for c in n["components"])),
                      "bytes": size, "file": os.path.basename(fn)})
    print("skipped:", dict(skipped))

    with open(os.path.join(OUT_RAW, "_index.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["class", "root_path_id", "nodes", "text_nodes",
                                          "buttons", "bytes", "file"])
        w.writeheader()
        w.writerows(sorted(index, key=lambda r: (-r["nodes"], r["class"])))

    total = sum(r["bytes"] for r in index)
    lines = ["# UI layout (số đo bóc từ prefab)", "",
             "> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể",
             "> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham",
             "> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.", "",
             f"- màn hình dump được: **{len(index)}**",
             f"- tổng node: **{sum(r['nodes'] for r in index)}**",
             f"- dung lượng thô (gz): **{total / 1e6:.1f} MB**", ""]
    if skipped:
        lines += ["- bỏ qua: " + ", ".join(f"{k} ({v})" for k, v in skipped.items()), ""]
    lines += ["## Màn hình nhiều node nhất", "",
              "| class | node | text | button | KB |", "|---|---:|---:|---:|---:|"]
    for r in sorted(index, key=lambda r: -r["nodes"])[:40]:
        lines.append(f"| `{r['class']}` | {r['nodes']} | {r['text_nodes']} | {r['buttons']} "
                     f"| {r['bytes'] / 1024:.0f} |")
    lines += ["", "## Cấu trúc mỗi node", "", "```json",
              '{"path": "Background/Star_01", "depth": 2, "active": 1,',
              ' "anchor_min": [0,0], "anchor_max": [1,1], "anchored_pos": [0,0],',
              ' "size_delta": [0,0], "pivot": [0.5,0.5], "scale": [1,1,1],',
              ' "components": [{"class":"Image","sprite":"Star"},',
              '                 {"class":"LanguageTextMeshPro","key":"txt_play","text":"Play"}]}',
              "```", "",
              "- Toạ độ là **local space của RectTransform cha**, đơn vị Unity",
              "  (canvas tham chiếu thường 1080×1920 → 1 unit = 100 px).",
              "- `anchor_min`/`anchor_max` quyết định responsive: `[0,0]`–`[1,1]` = full stretch.",
              "- `size_delta` = kích thước khi anchor không stretch; khi stretch thì là phần cộng thêm.",
              ""]
    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
