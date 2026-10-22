#!/usr/bin/env python3
"""Dump the UI layout of every Board_* / Popup_* screen as numbers.

Unity stores UI layout in `RectTransform` components of the prefab, not in the
C# code. This walks each screen's transform subtree and records, per node:

    path, anchors, anchoredPosition, sizeDelta, pivot, scale, active,
    component classes, text (TMP) and sprite name

so the layout can be rebuilt in another engine instead of eyeballing screenshots.

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
from collections import Counter, defaultdict

import UnityPy

EXTRACT = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
OUT_RAW = os.environ.get("UI_RAW", "reverse-engineering/raw/ui")
OUT_MD = os.environ.get("UI_MD", "docs/apk-analysis/20-ui-layout.md")
MAX_NODES = int(os.environ.get("UI_MAX_NODES", "1500"))
MAX_COMPONENTS = int(os.environ.get("UI_MAX_COMPONENTS", "10"))
MAX_BYTES = int(os.environ.get("UI_MAX_BYTES", "3_000_000".replace("_", "")))
ROOT_PREFIXES = ("Board_", "Popup_", "Tab_")


def load_env():
    files = [os.path.join(EXTRACT, f) for f in ("data.unity3d", "resources.resource")]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        raise SystemExit(f"no unity files under {EXTRACT}")
    return UnityPy.load(*files)


def _pptr(obj):
    """PPtr(dict or object) -> dereferenced object or None."""
    if obj is None:
        return None
    try:
        return obj.deref_parse_as_object()
    except Exception:  # noqa: BLE001
        return None


def _go_of(transform):
    t = transform
    return _pptr(getattr(t, "m_GameObject", None))


def _script_class(component):
    try:
        head = component.parse_monobehaviour_head()
        script = head.m_Script.deref_parse_as_object()
        return script.m_ClassName or "MonoBehaviour"
    except Exception:  # noqa: BLE001
        return "MonoBehaviour"


def _vec(value, keys):
    if isinstance(value, dict):
        return [round(float(value.get(k, 0) or 0), 3) for k in keys]
    out = []
    for k in keys:
        try:
            out.append(round(float(getattr(value, k, 0) or 0), 3))
        except Exception:  # noqa: BLE001
            out.append(0.0)
    return out


def node_info(transform, depth=0):
    """Layout of one transform node (+ its direct component list)."""
    go = _go_of(transform)
    if go is None:
        return None
    try:
        tree = transform.read_typetree()
    except Exception:  # noqa: BLE001
        tree = {}
    name = ""
    active = 1
    comps = []
    try:
        go_tree = go.read_typetree()
        name = go_tree.get("m_Name", "")
        active = int(go_tree.get("m_IsActive", 1) or 0)
        for c in (go_tree.get("m_Component") or [])[:MAX_COMPONENTS]:
            pptr = c.get("component") if isinstance(c, dict) else c
            comp = _pptr(pptr)
            if comp is None:
                continue
            cname = _script_class(comp)
            entry = {"class": cname}
            if any(k in cname for k in ("Text", "Input")):
                try:
                    ct = comp.read_typetree()
                    txt = ct.get("m_text")
                    if isinstance(txt, str) and txt.strip():
                        entry["text"] = txt[:200]
                    key = ct.get("key") or ct.get("m_Key") or ct.get("localizeKey")
                    if isinstance(key, str) and key.strip():
                        entry["key"] = key[:120]
                except Exception:  # noqa: BLE001
                    pass
            if "Image" in cname or "Sprite" in cname:
                try:
                    ct = comp.read_typetree()
                    sp = _pptr(ct.get("m_Sprite"))
                    if sp is not None:
                        entry["sprite"] = (getattr(sp, "m_Name", "") or "")[:80]
                except Exception:  # noqa: BLE001
                    pass
            comps.append(entry)
    except Exception:  # noqa: BLE001
        pass
    node = {
        "name": name,
        "active": active,
        "components": comps,
        "anchor_min": _vec(tree.get("m_AnchorMin"), ("x", "y")) if "m_AnchorMin" in tree else None,
        "anchor_max": _vec(tree.get("m_AnchorMax"), ("x", "y")) if "m_AnchorMax" in tree else None,
        "anchored_pos": _vec(tree.get("m_AnchoredPosition"), ("x", "y")) if "m_AnchoredPosition" in tree else None,
        "size_delta": _vec(tree.get("m_SizeDelta"), ("x", "y")) if "m_SizeDelta" in tree else None,
        "pivot": _vec(tree.get("m_Pivot"), ("x", "y")) if "m_Pivot" in tree else None,
        "scale": _vec(tree.get("m_LocalScale"), ("x", "y", "z")) if "m_LocalScale" in tree else None,
    }
    return node, tree


def walk(root, budget):
    """Breadth-first subtree dump -> list of {path, depth, ...}"""
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
        info = node_info(tr, depth)
        if info is None:
            continue
        node, tree = info
        path = f"{parent_path}/{node['name']}" if parent_path else node["name"]
        node.update({"path": path, "depth": depth})
        out.append(node)
        children = tree.get("m_Children") or []
        for ch in children[:60]:
            child = _pptr(ch if not isinstance(ch, dict) else ch)
            if child is not None:
                queue.append((child, path, depth + 1))
    return out


def main() -> int:
    env = load_env()
    os.makedirs(OUT_RAW, exist_ok=True)
    index = []
    seen_roots = set()
    sizes = Counter()

    # find screen roots: a MonoBehaviour whose class name looks like a screen
    candidates = []
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            head = obj.parse_monobehaviour_head()
            script = head.m_Script.deref_parse_as_object()
            cls = script.m_ClassName or ""
        except Exception:  # noqa: BLE001
            continue
        if cls.startswith(ROOT_PREFIXES):
            candidates.append((cls, obj, head))

    print(f"screen candidates: {len(candidates)}")
    for cls, obj, head in candidates:
        go = _pptr(getattr(head, "m_GameObject", None))
        if go is None:
            continue
        top = go
        for _ in range(24):                       # climb to the UI root
            tr = None
            try:
                got = go.read_typetree()
                for c in (got.get("m_Component") or [])[:MAX_COMPONENTS]:
                    comp = _pptr(c.get("component") if isinstance(c, dict) else c)
                    if comp is not None and comp.object_reader.type.name in ("Transform", "RectTransform"):
                        tr = comp
                        break
            except Exception:  # noqa: BLE001
                tr = None
            if tr is None:
                break
            father = _pptr(getattr(tr, "m_Father", None))
            if father is None:
                break
            fgo = _go_of(father)
            if fgo is None:
                break
            top = fgo
            go = fgo
        root_key = getattr(top, "path_id", id(top))
        if root_key in seen_roots:
            continue
        seen_roots.add(root_key)

        # the transform of the top GameObject
        top_tr = None
        try:
            got = top.read_typetree()
            for c in (got.get("m_Component") or [])[:MAX_COMPONENTS]:
                comp = _pptr(c.get("component") if isinstance(c, dict) else c)
                if comp is not None and comp.object_reader.type.name in ("Transform", "RectTransform"):
                    top_tr = comp
                    break
        except Exception:  # noqa: BLE001
            pass
        if top_tr is None:
            continue

        nodes = walk(top_tr, MAX_NODES)
        if not nodes:
            continue
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in cls)[:80]
        fn = os.path.join(OUT_RAW, f"{safe}__{root_key}.json.gz")
        payload = {"class": cls, "root_path_id": root_key, "nodes": nodes,
                   "note": "RectTransform layout as stored in the prefab. Temporary: engine defaults "
                           "may override sizes at runtime."}
        with gzip.open(fn, "wt", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        size = os.path.getsize(fn)
        sizes[cls] += size
        texts = sum(1 for n in nodes if any("text" in c for c in n["components"]))
        buttons = sum(1 for n in nodes if any("Button" in c["class"] for c in n["components"]))
        index.append({"class": cls, "root_path_id": root_key, "nodes": len(nodes),
                      "text_nodes": texts, "buttons": buttons, "bytes": size, "file": fn})
        if size > MAX_BYTES:
            os.remove(fn)
            index[-1]["file"] = ""
            index[-1]["bytes"] = 0

    with open(os.path.join(OUT_RAW, "_index.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["class", "root_path_id", "nodes", "text_nodes",
                                          "buttons", "bytes", "file"])
        w.writeheader()
        w.writerows(sorted(index, key=lambda r: (-r["nodes"])))

    total = sum(r["bytes"] for r in index)
    lines = ["# UI layout (số đo bóc từ prefab)", "",
             "> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể",
             "> ghi đè (layout group, code set anchor, đổi theo tỉ lệ màn hình), nên chỉ dùng làm",
             "> khung tham chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.", "",
             f"- màn hình dump được: **{len(index)}**",
             f"- tổng node: **{sum(r['nodes'] for r in index)}**",
             f"- dung lượng thô (gz): **{total / 1e6:.1f} MB**", "",
             "## Màn hình nhiều node nhất", "",
             "| class | node | text | button | KB |", "|---|---:|---:|---:|---:|"]
    for r in sorted(index, key=lambda r: -r["nodes"])[:40]:
        lines.append(f"| `{r['class']}` | {r['nodes']} | {r['text_nodes']} | {r['buttons']} "
                     f"| {r['bytes'] / 1024:.0f} |")
    lines += ["", "## Cấu trúc mỗi node", "",
              "```json",
              '{"path": "Background/Star_01", "depth": 2, "active": 1,',
              ' "anchor_min": [0,0], "anchor_max": [1,1], "anchored_pos": [0,0],',
              ' "size_delta": [0,0], "pivot": [0.5,0.5], "scale": [1,1,1],',
              ' "components": [{"class":"Image","sprite":"Star"},',
              '                 {"class":"LanguageTextMeshPro","key":"txt_play","text":"Play"}]}',
              "```", "",
              "- Toạ độ là **local space của RectTransform cha**, đơn vị Unity (1 unit = 100 px ở",
              "  canvas mặc định) — muốn ra pixel thì nhân theo `Canvas.referenceResolution`.",
              "- `anchor_min`/`anchor_max` quyết định responsive: `[0,0]`–`[1,1]` = full stretch.",
              ""]
    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines[:20]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
