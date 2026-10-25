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
from ui_render_context import file_context, export_context

EXTRACT = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
OUT_RAW = os.environ.get("UI_RAW", "reverse-engineering/raw/ui")
OUT_MD = os.environ.get("UI_MD", "docs/apk-analysis/20-ui-layout.md")
UNITY_VERSION = os.environ.get("UNITY_VERSION", "2022.3.62f3")
TTG_BACKEND = os.environ.get("TTG_BACKEND", "AssetStudio")
MAX_NODES = int(os.environ.get("UI_MAX_NODES", "6000"))
MAX_COMPONENTS = int(os.environ.get("UI_MAX_COMPONENTS", "12"))
MAX_BYTES = int(os.environ.get("UI_MAX_BYTES", "4000000"))
ROOT_PREFIXES = ("Board_", "Popup_", "Tab_")
EXTRA_UI_ROOTS = {"GP_Tutorials", "Tut_Settings", "Tut_Settings1"}
TRANSFORM_TYPES = ("Transform", "RectTransform")
RECT_KEYS = ("m_AnchorMin", "m_AnchorMax", "m_AnchoredPosition", "m_SizeDelta", "m_Pivot")


CLASS_MAP: dict[int, str] = {}


def build_class_map(env) -> None:
    """path_id -> C# class name, parsed from the raw ObjectReaders.

    Parsed objects do not expose `parse_monobehaviour_head`, so the names have to
    be collected from the readers once and looked up by path_id afterwards.
    """
    n = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            head = obj.parse_monobehaviour_head()
            CLASS_MAP[obj.path_id] = head.m_Script.deref_parse_as_object().m_ClassName or ""
            n += 1
        except Exception:  # noqa: BLE001
            continue
    print(f"class map: {n} MonoBehaviours")


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


def stable_object_id(obj):
    """Unity asset ID, not Python id(parsed_object), for deterministic output."""
    reader = getattr(obj, "object_reader", None)
    value = getattr(reader, "path_id", None)
    if value is None:
        value = getattr(obj, "path_id", None)
    return value if value is not None else id(obj)


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


def tree_of(comp) -> dict:
    """Typetree of a component: parsed objects delegate to their ObjectReader."""
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
    """Class name via the reader (head) or the pre-built map."""
    try:
        head = comp.parse_monobehaviour_head()
        return head.m_Script.deref_parse_as_object().m_ClassName or "MonoBehaviour"
    except Exception:  # noqa: BLE001
        pass
    try:
        pid = comp.object_reader.path_id
        name = CLASS_MAP.get(pid)
        if name:
            return name
    except Exception:  # noqa: BLE001
        pass
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
    out["local_pos"] = _xyz(getattr(tr, "m_LocalPosition", None))
    rot = getattr(tr, "m_LocalRotation", None)
    if rot is not None:
        try:
            out["rotation"] = [round(float(rot.x), 3), round(float(rot.y), 3),
                               round(float(rot.z), 3), round(float(rot.w), 3)]
        except Exception:  # noqa: BLE001
            out["rotation"] = None
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
        if any(k in cname for k in ("Text", "Input", "Label", "Language")):
            tree = tree_of(comp)
            txt = tree.get("m_text") or tree.get("m_Text") or getattr(comp, "m_text", None)
            if isinstance(txt, str) and txt.strip():
                entry["text"] = txt[:200]
            # localization key lives on LanguageTextMeshPro; names vary, so scan strings
            for k, v in tree.items():
                if not isinstance(v, str) or not v.strip() or v == txt:
                    continue
                if k in ("m_text", "m_Text", "m_Name"):
                    continue
                low = k.lower()
                if "key" in low or "id" in low or "code" in low:
                    entry["key"] = v[:120]
                    entry["key_field"] = k
                    break
        if "Image" in cname or "Sprite" in cname or "Renderer" in cname:
            try:
                sp = _pptr(getattr(comp, "m_Sprite", None))
                if sp is not None:
                    entry["sprite"] = (getattr(sp, "m_Name", "") or "")[:80]
            except Exception:  # noqa: BLE001
                pass
        # Preserve drawing-critical properties omitted by the earlier layout
        # summary. These are serialized values, not runtime screen geometry.
        if cname in ("SpriteRenderer", "SpriteMask", "Image", "TextMeshPro",
                     "TextMeshProUGUI", "Camera"):
            tree = tree_of(comp)
            keys = ("m_Sprite", "m_Color", "m_FlipX", "m_FlipY", "m_DrawMode",
                    "m_Size", "m_SortingLayerID", "m_SortingOrder", "m_Materials",
                    "m_fontAsset", "m_sharedMaterial", "m_fontSize", "m_fontSizeBase",
                    "m_fontColor", "m_fontStyle", "m_enableAutoSizing",
                    "m_fontSizeMin", "m_fontSizeMax", "m_HorizontalAlignment",
                    "m_VerticalAlignment", "m_textAlignment", "m_margin",
                    "m_overflowMode", "m_enableWordWrapping", "m_Orthographic",
                    "orthographic size", "m_ViewportRect")
            entry["visual_properties"] = {k: tree[k] for k in keys if k in tree}
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
        key = stable_object_id(tr)
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


def linked_tutorial_panels(head):
    """Panel references may be siblings, not children of GP_Tutorials."""
    result = []
    reader = getattr(head, "object_reader", None)
    asset_file = getattr(reader, "assets_file", None)
    objects = getattr(asset_file, "objects", {})
    for field, ref in tree_of(head).items():
        if not (field.startswith("tutobj") or field in
                ("tutSettings", "tutSettings2", "coverObject")):
            continue
        item = {"field": field, "reference": ref}
        try:
            if not isinstance(ref, dict) or ref.get("m_FileID", 0) != 0:
                item["status"] = "external_or_non_pptr"
            elif not ref.get("m_PathID"):
                item["status"] = "null"
            else:
                obj = objects[ref["m_PathID"]].read()
                tr = transform_of(obj)
                if tr is None:
                    raise ValueError("referenced object has no transform")
                item["nodes"] = walk(tr, MAX_NODES)
                item["status"] = "local_panel_exported"
        except Exception as exc:
            item["status"] = "unresolved"
            item["error"] = str(exc)[:160]
        result.append(item)
    return result


def main() -> int:
    env = load_env()
    build_class_map(env)
    os.makedirs(OUT_RAW, exist_ok=True)
    index, seen_roots = [], set()
    comp_classes: Counter = Counter()
    empty_nodes = [0]

    candidates = []
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            head = obj.parse_monobehaviour_head()
            cls = head.m_Script.deref_parse_as_object().m_ClassName or ""
        except Exception:  # noqa: BLE001
            continue
        if cls.startswith(ROOT_PREFIXES) or cls in EXTRA_UI_ROOTS:
            candidates.append((cls, head))
    print(f"screen candidates: {len(candidates)}")

    skipped = Counter()
    skipped_by_class: dict = {}
    for cls, head in candidates:
        def _skip(reason: str) -> None:
            skipped[reason] += 1
            skipped_by_class.setdefault(cls, Counter())[reason] += 1

        go = _pptr(getattr(head, "m_GameObject", None))
        if go is None:
            _skip("no gameobject")
            continue
        # The screen MonoBehaviour lives on the panel root, so its GameObject IS
        # the subtree we want. (Climbing to the scene root instead produced the
        # whole canvas for every screen - 593k duplicated nodes.)
        top = go
        root_key = stable_object_id(top)
        # Trước đây dedupe theo GameObject và bỏ qua lặng lẽ: 793 candidate chỉ
        # ra 607 file, `skipped` rỗng, và cả class biến mất (Board_Shop...) vì
        # nhiều Board_* MB nằm chung một GameObject gốc. Nay dedupe theo
        # (class, root) và ghi lại mọi lần bỏ.
        dedupe_key = (cls, root_key)
        if dedupe_key in seen_roots:
            _skip("duplicate (class, root)")
            continue
        seen_roots.add(dedupe_key)
        top_tr = transform_of(top)
        if top_tr is None:
            _skip("no transform")
            continue
        nodes = walk(top_tr, MAX_NODES)
        for n in nodes:
            if not n["components"]:
                empty_nodes[0] += 1
            for c in n["components"]:
                comp_classes[c["class"]] += 1
        if not nodes:
            _skip("empty subtree")
            continue
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in cls)[:80]
        fn = os.path.join(OUT_RAW, f"{safe}__{root_key}.json.gz")
        payload = {"class": cls, "root_path_id": root_key, "nodes": nodes,
                   "note": "RectTransform layout as stored in the prefab. Temporary: runtime "
                           "layout groups / safe area may override these numbers."}
        payload.update(file_context(head))
        if cls == "GP_Tutorials":
            payload["linked_panels"] = linked_tutorial_panels(head)
        with gzip.open(fn, "wt", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        size = os.path.getsize(fn)
        if size > MAX_BYTES:
            os.remove(fn)
            _skip("too big")
            continue
        index.append({"class": cls, "root_path_id": root_key, "nodes": len(nodes),
                      "text_nodes": sum(1 for n in nodes
                                        if any("text" in c for c in n["components"])),
                      "buttons": sum(1 for n in nodes
                                     if any("Button" in c["class"] for c in n["components"])),
                      "bytes": size, "file": os.path.basename(fn)})
    print("skipped:", dict(skipped))
    # Class nào có candidate mà không ra file nào cũng phải lộ diện.
    written_classes = {r["class"] for r in index}
    for cls in sorted({c for c, _h in candidates} - written_classes):
        skipped_by_class.setdefault(cls, Counter())["no file written"] += 1
    # Vì sao một màn có thể biến mất giữa hai lần chạy: trước đây chỉ có tổng,
    # không biết màn nào bị bỏ. Ghi rõ theo từng class để lần sau đọc log là biết.
    if True:
        with open(os.path.join(OUT_RAW, "_skipped.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["class", "reason", "count"])
            for cls, reasons in sorted(skipped_by_class.items()):
                for reason, n in reasons.items():
                    w.writerow([cls, reason, n])

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
    if comp_classes:
        lines += ["## Component gặp nhiều nhất", "", "| class | số node |", "|---|---:|"]
        for k, v in comp_classes.most_common(25):
            lines.append(f"| `{k}` | {v} |")
        lines += ["", f"- node không đọc được component: **{empty_nodes[0]}**", ""]
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
              "- **UI của game này phần lớn là SpriteRenderer trong world space** (chỉ 1 Canvas),",
              "  nên dùng `local_pos` + `scale` là chính; `anchor_*` chỉ có ở node RectTransform.",
              "- `local_pos` là **local space của Transform cha**, đơn vị Unity",
              "  không gán một tỉ lệ px/unit cố định nếu chưa resolve camera/runtime viewport).",
              "- `anchor_min`/`anchor_max` quyết định responsive: `[0,0]`–`[1,1]` = full stretch.",
              "- `size_delta` = kích thước khi anchor không stretch; khi stretch thì là phần cộng thêm.",
              ""]
    os.makedirs(os.path.dirname(OUT_MD) or ".", exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines[:16]))
    print("UI render context:", export_context(env, os.path.join(OUT_RAW, "render-context")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
