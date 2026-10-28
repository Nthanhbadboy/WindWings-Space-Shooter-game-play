#!/usr/bin/env python3
"""Inventory every APK inside the WindWings XAPK.

Writes JSON + human-readable text so the sandbox (which cannot see Actions
logs) can read the results through git.
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict

XAPK = "/tmp/apk/windwings.xapk"
PARTS = "/tmp/apk/parts"
OUT = "/tmp/apk/inventory"

INTEREST = re.compile(
    r"(global-metadata|libil2cpp|libunity|libmain|libmono|unity default|"
    r"data\.unity3d|\.obb$|\.bundle$|resources\.assets|sharedassets|level[0-9]|"
    r"\.assets$|\.resS$|\.resource$|\.dat$|\.json$|\.txt$|\.csv$|\.xml$|"
    r"\.mp3$|\.ogg$|\.wav$|\.png$|\.jpg$|\.webp$|\.atlas$|\.spriteatlas)",
    re.I,
)


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{n}B"
        n /= 1024
    return f"{n:.1f}GB"


def part_summary(path: str) -> dict:
    z = zipfile.ZipFile(path)
    infos = z.infolist()
    total = sum(i.file_size for i in infos)
    top = defaultdict(lambda: [0, 0])
    ext = Counter()
    unity = []
    for i in infos:
        name = i.filename
        key = name.split("/")[0] if "/" in name else "(root)"
        top[key][0] += 1
        top[key][1] += i.file_size
        base = name.rsplit("/", 1)[-1]
        e = ("." + base.rsplit(".", 1)[-1].lower()) if "." in base else "(none)"
        ext[e] += 1
        if INTEREST.search(name):
            unity.append({"name": name, "size": i.file_size, "compressed": i.compress_size})
    unity.sort(key=lambda x: -x["size"])
    return {
        "file": os.path.basename(path),
        "size": os.path.getsize(path),
        "entries": len(infos),
        "uncompressed": total,
        "top_level": {k: {"entries": v[0], "bytes": v[1]} for k, v in sorted(top.items(), key=lambda kv: -kv[1][1])},
        "extensions": dict(ext.most_common(30)),
        "interesting": unity[:400],
        "interesting_count": len(unity),
    }


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    report = {"xapk_size": os.path.getsize(XAPK), "xapk_sha256": None, "manifest": None, "parts": []}

    z = zipfile.ZipFile(XAPK)
    names = z.namelist()
    if "manifest.json" in names:
        raw = z.read("manifest.json").decode("utf-8", "replace")
        try:
            report["manifest"] = json.loads(raw)
        except Exception:
            report["manifest"] = raw
    os.makedirs(PARTS, exist_ok=True)
    for n in names:
        if n.lower().endswith((".apk", ".obb", ".zip")) and not n.endswith("/"):
            target = os.path.join(PARTS, os.path.basename(n))
            if not os.path.exists(target) or os.path.getsize(target) != z.getinfo(n).file_size:
                with z.open(n) as src, open(target, "wb") as dst:
                    while True:
                        chunk = src.read(1 << 20)
                        if not chunk:
                            break
                        dst.write(chunk)

    for name in sorted(os.listdir(PARTS)):
        p = os.path.join(PARTS, name)
        if not zipfile.is_zipfile(p):
            report["parts"].append({"file": name, "size": os.path.getsize(p), "error": "not a zip"})
            continue
        try:
            report["parts"].append(part_summary(p))
        except Exception as e:  # noqa: BLE001
            report["parts"].append({"file": name, "size": os.path.getsize(p), "error": repr(e)})

    with open(os.path.join(OUT, "inventory.json"), "w") as f:
        json.dump(report, f, indent=2)

    lines = []
    lines.append(f"# XAPK inventory\n")
    lines.append(f"- xapk size: {report['xapk_size']} bytes ({human(report['xapk_size'])})")
    man = report["manifest"]
    if isinstance(man, dict):
        lines.append(f"- package: `{man.get('package_name')}`")
        lines.append(f"- version: `{man.get('version_name')}` (code {man.get('version_code')})")
        lines.append(f"- min/target sdk: {man.get('min_sdk_version')} / {man.get('target_sdk_version')}")
        lines.append(f"- split apks: {man.get('split_apks')}")
        lines.append(f"- permissions: {man.get('permissions')}")
        lines.append("")
    for part in report["parts"]:
        lines.append(f"## `{part['file']}` — {human(part['size'])}")
        if "error" in part:
            lines.append(f"ERROR: {part['error']}")
            continue
        lines.append(f"- entries: {part['entries']}, uncompressed: {human(part['uncompressed'])}")
        lines.append("- top-level:")
        for k, v in part["top_level"].items():
            lines.append(f"  - `{k}`: {v['entries']} files, {human(v['bytes'])}")
        lines.append("- extensions: " + ", ".join(f"`{k}`×{v}" for k, v in part["extensions"].items()))
        lines.append("")
        lines.append(f"### Interesting entries ({part['interesting_count']} matched, top {len(part['interesting'])})")
        lines.append("")
        lines.append("| size | name |")
        lines.append("|---:|---|")
        for e in part["interesting"]:
            lines.append(f"| {e['size']} | `{e['name']}` |")
        lines.append("")
    open(os.path.join(OUT, "inventory.md"), "w").write("\n".join(lines))
    print("\n".join(lines[:80]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
