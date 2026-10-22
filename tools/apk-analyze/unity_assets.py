#!/usr/bin/env python3
"""UnityPy probe/export for WindWings `data.unity3d`.

Usage:
    python3 unity_assets.py probe
    EXPORT=1 python3 unity_assets.py export
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict

import UnityPy

DATA = os.environ.get("UNITY_DATA", "/tmp/apk/extract")
OUT = "/tmp/apk/unity"
TEXT = os.path.join(OUT, "textassets")
EXPORT = os.path.join(OUT, "export")
MAX_TEXT_FILES = 4000
MAX_TEXT_BYTES = 40 * 1024 * 1024


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def safe_name(name: str, used: set[str]) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:120] or "unnamed"
    cand = base
    i = 1
    while cand in used:
        i += 1
        cand = f"{base}__{i}"
    used.add(cand)
    return cand


def textasset_bytes(obj) -> bytes:
    d = obj.read()
    script = getattr(d, "m_Script", b"")
    if isinstance(script, str):
        return script.encode("utf-8", "surrogateescape")
    return bytes(script)


def probe(env) -> dict:
    info: dict = {
        "data_file": DATA,
        "data_size": os.path.getsize(DATA),
        "files": [],
        "types": {},
        "textassets": [],
        "monobehaviours": {"count": 0, "typetree_ok": 0, "names": [], "samples": []},
        "textures": [],
        "sprites": [],
        "audio": [],
        "fonts": [],
        "shaders": [],
        "containers": [],
    }
    for path, sf in getattr(env, "files", {}).items():
        try:
            objects = len(sf.get_objects())
        except Exception:  # noqa: BLE001
            objects = -1
        info["files"].append(
            {
                "path": str(path),
                "version": str(getattr(sf, "version", "")),
                "objects": objects,
            }
        )
    types: Counter = Counter()
    textures = []
    audio = []
    mono_names = Counter()
    mono_typetree_keys = Counter()
    textassets = []
    for obj in env.objects:
        t = obj.type.name
        types[t] += 1
        try:
            name = obj.peek_name() or ""
        except Exception:  # noqa: BLE001
            name = ""
        if t == "TextAsset":
            try:
                b = textasset_bytes(obj)
                textassets.append({"name": name, "size": len(b)})
            except Exception as e:  # noqa: BLE001
                textassets.append({"name": name, "error": repr(e)})
        elif t == "Texture2D":
            try:
                d = obj.read()
                textures.append(
                    {
                        "name": name,
                        "width": int(getattr(d, "m_Width", 0) or 0),
                        "height": int(getattr(d, "m_Height", 0) or 0),
                        "format": str(getattr(d, "m_TextureFormat", "")),
                    }
                )
            except Exception:  # noqa: BLE001
                pass
        elif t == "AudioClip":
            try:
                d = obj.read()
                audio.append({"name": name, "channels": int(getattr(d, "m_Channels", 0) or 0),
                              "frequency": int(getattr(d, "m_Frequency", 0) or 0)})
            except Exception:  # noqa: BLE001
                pass
        elif t == "MonoBehaviour":
            mono_names[name] += 1
            try:
                tree = obj.read_typetree()
                info["monobehaviours"]["typetree_ok"] += 1
                if isinstance(tree, dict):
                    for k in list(tree)[:40]:
                        mono_typetree_keys[k] += 1
            except Exception:  # noqa: BLE001
                pass
    info["types"] = dict(types.most_common())
    info["source_files"] = sorted(getattr(env, "files", {}).keys())
    info["textassets"] = sorted(textassets, key=lambda x: -x.get("size", 0))
    info["textures"] = sorted(textures, key=lambda x: -(x["width"] * x["height"]))[:200]
    info["audio"] = sorted(audio, key=lambda x: x["name"])[:500]
    info["monobehaviours"] = {
        "count": types.get("MonoBehaviour", 0),
        "typetree_ok": info["monobehaviours"]["typetree_ok"],
        "names": mono_names.most_common(80),
        "typetree_keys": mono_typetree_keys.most_common(80),
    }
    info["sprites"] = [{"count": types.get("Sprite", 0)}]
    info["fonts"] = [{"count": types.get("Font", 0)}]
    info["shaders"] = [{"count": types.get("Shader", 0)}]
    try:
        info["containers"] = [str(k) for k in list(env.container)[:80]]
    except Exception:  # noqa: BLE001
        pass
    return info


def write_probe_report(info: dict) -> None:
    lines = ["# Unity data probe", ""]
    lines.append(f"- source: `{info['data_file']}` ({human(info['data_size'])})")
    for f in info["files"]:
        lines.append(f"- serialized file `{f['path']}` — version `{f['version']}`, {f['objects']} objects")
    lines += ["", "## Object types", "", "| type | count |", "|---|---:|"]
    for t, c in info["types"].items():
        lines.append(f"| {t} | {c} |")
    lines += ["", "## TextAssets", "", f"Count: **{len(info['textassets'])}**", "", "| size | name |", "|---:|---|"]
    for a in info["textassets"][:200]:
        lines.append(f"| {a.get('size', 'ERR')} | `{a['name']}` |")
    lines += ["", "## Textures (top 200 by pixels)", "", "| size | name |", "|---:|---|"]
    for t in info["textures"][:200]:
        lines.append(f"| {t['width']}×{t['height']} | `{t['name']}` ({t['format']}) |")
    lines += ["", "## Audio", "", "| name | ch | Hz |", "|---|---:|---:|"]
    for a in info["audio"][:200]:
        lines.append(f"| `{a['name']}` | {a.get('channels')} | {a.get('frequency')} |")
    mb = info["monobehaviours"]
    lines += ["", "## MonoBehaviour", "", f"- total: {mb['count']}", f"- typetree readable: {mb['typetree_ok']}", "",
              "Top names:", "", "| name | count |", "|---|---:|"]
    for n, c in mb.get("names", [])[:80]:
        lines.append(f"| `{n}` | {c} |")
    lines += ["", "Typetree keys:", "", "`" + "`, `".join(k for k, _ in mb.get("typetree_keys", [])[:80]) + "`", ""]
    if info.get("containers"):
        lines += ["", "## Containers", ""] + [f"- `{c}`" for c in info["containers"]]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "probe.md"), "w") as f:
        f.write("\n".join(lines))
    with open(os.path.join(OUT, "probe.json"), "w") as f:
        json.dump(info, f, indent=2)
    print("\n".join(lines[:60]))


def export_text(env) -> int:
    os.makedirs(TEXT, exist_ok=True)
    used: set[str] = set()
    total = 0
    count = 0
    manifest = []
    for obj in env.objects:
        if obj.type.name != "TextAsset" or count >= MAX_TEXT_FILES or total >= MAX_TEXT_BYTES:
            continue
        try:
            name = obj.peek_name() or f"text_{count}"
            b = textasset_bytes(obj)
        except Exception:  # noqa: BLE001
            continue
        fn = safe_name(name, used)
        ext = ".txt"
        head = b[:200].lstrip()
        if head.startswith(b"{") or head.startswith(b"["):
            ext = ".json"
        elif head.startswith(b"<"):
            ext = ".xml"
        fn += ext
        with open(os.path.join(TEXT, fn), "wb") as f:
            f.write(b)
        manifest.append({"name": name, "file": fn, "size": len(b)})
        total += len(b)
        count += 1
    with open(os.path.join(OUT, "textassets.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(OUT, "textassets_sizes.txt"), "w") as f:
        f.write(f"files={count} bytes={total}\n")
    print(f"exported {count} text assets, {human(total)}")
    return 0


def export_assets(env) -> None:
    os.makedirs(EXPORT, exist_ok=True)
    counters: Counter = Counter()
    bytes_out: Counter = Counter()
    manifest = []
    for obj in env.objects:
        t = obj.type.name
        if t not in ("Texture2D", "Sprite", "AudioClip", "Font", "TextAsset"):
            continue
        try:
            d = obj.read()
            name = (getattr(d, "m_Name", "") or f"obj_{obj.path_id}")[:100]
        except Exception:  # noqa: BLE001
            continue
        sub = os.path.join(EXPORT, t)
        os.makedirs(sub, exist_ok=True)
        used: set[str] = set()
        try:
            if t in ("Texture2D", "Sprite"):
                img = getattr(d, "image", None)
                if img is None:
                    continue
                fn = safe_name(name, used) + ".png"
                p = os.path.join(sub, fn)
                img.save(p)
                counters[t] += 1
                bytes_out[t] += os.path.getsize(p)
                manifest.append((t, name, os.path.getsize(p), os.path.relpath(p, EXPORT)))
            elif t == "AudioClip":
                samples = getattr(d, "samples", None)
                if not samples:
                    continue
                for sname, data in samples.items():
                    fn = safe_name(f"{name}_{sname}", used) + ".wav"
                    p = os.path.join(sub, fn)
                    with open(p, "wb") as f:
                        f.write(data)
                    counters[t] += 1
                    bytes_out[t] += len(data)
                    manifest.append((t, name, len(data), os.path.relpath(p, EXPORT)))
            elif t == "Font":
                data = getattr(d, "m_FontData", None)
                if data:
                    fn = safe_name(name, used) + ".ttf"
                    p = os.path.join(sub, fn)
                    with open(p, "wb") as f:
                        f.write(bytes(data))
                    counters[t] += 1
        except Exception:  # noqa: BLE001
            continue
    lines = ["# Unity asset export", ""]
    for t, c in counters.items():
        lines.append(f"- {t}: {c} files, {human(bytes_out[t])}")
    with open(os.path.join(OUT, "export.md"), "w") as f:
        f.write("\n".join(lines))
    with open(os.path.join(OUT, "export-manifest.csv"), "w") as f:
        f.write("type,name,bytes,path\n")
        for row in sorted(manifest, key=lambda r: (r[0], r[1])):
            f.write(",".join('"' + str(x).replace('"', '""') + '"' for x in row) + "\n")
    print("\n".join(lines))


def load_env():
    """Load the serialized files we extracted, skipping ones UnityPy rejects."""
    candidates = [
        os.path.join(DATA, "data.unity3d") if os.path.isdir(DATA) else DATA,
        os.path.join(DATA, "resources.resource"),
        os.path.join(DATA, "globalgamemanagers"),
        os.path.join(DATA, "globalgamemanagers.assets"),
    ]
    candidates = [p for p in candidates if os.path.isfile(p)]
    if not candidates:
        raise SystemExit(f"no unity files under {DATA}")
    env = UnityPy.load(candidates[0])
    for path in candidates[1:]:
        try:
            with open(path, "rb") as f:
                env.load_file(f, name=os.path.basename(path))
            print("loaded extra file", path)
        except Exception as e:  # noqa: BLE001
            print("skip", path, repr(e))
    print("source files:", list(getattr(env, "files", {}).keys()))
    return env


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "probe"
    env = load_env()
    if mode == "probe":
        write_probe_report(probe(env))
    elif mode == "text":
        export_text(env)
    elif mode == "export":
        export_assets(env)
    return 0


if __name__ == "__main__":
    sys.exit(main())
