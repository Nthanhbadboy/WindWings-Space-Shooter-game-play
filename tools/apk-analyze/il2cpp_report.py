#!/usr/bin/env python3
"""Summarize Il2CppDumper output for WindWings.

Reads /tmp/apk/il2cpp/{dump.cs,stringliteral.json,il2cpp.h,script.json} and
writes a Markdown report + a class index JSON + an "interesting classes" file.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict

DUMP = "/tmp/apk/il2cpp/dump.cs"
STRINGS = "/tmp/apk/il2cpp/stringliteral.json"
OUT = "/tmp/apk/il2cpp_report"
META = "/tmp/apk/extract/global-metadata.dat"

KEYWORDS = [
    "Player", "Ship", "Spaceship", "Enemy", "Boss", "Wave", "Level", "Stage", "Chapter",
    "Bullet", "Weapon", "Cannon", "Laser", "Missile", "Upgrade", "PowerUp", "Shop", "Store",
    "Item", "Currency", "Coin", "Gem", "Diamond", "Energy", "Save", "Load", "Data", "Config",
    "Setting", "Ads", "Ad ", "Reward", "Daily", "Mission", "Achievement", "Leaderboard",
    "PvP", "Battle", "Mode", "Spawn", "Difficulty", "Damage", "Health", "Speed", "Drop",
    "Loot", "Chest", "Skin", "Drone", "Support", "Tech", "IAP", "Purchase", "Billing",
    "Analytics", "Firebase", "Cheat", "Hack", "Debug", "Root", "Emulator", "Frida",
    "Anti", "Security", "Encrypt", "Decrypt", "Localization", "Language", "Audio", "Sound",
    "Music", "UI", "Popup", "Panel", "Screen", "Tutorial", "Quest", "Event", "Season",
    "Pass", "Bundle", "Offer", "Spin", "Wheel", "Gacha", "Inventory", "Equip", "Stat",
]

DECL = re.compile(
    r"^(?:(?:public|internal|private|protected|sealed|abstract|static|readonly|partial)\s+)*"
    r"(class|struct|enum|interface)\s+([\w`<>\[\],. ]+?)(?:\s*:\s*([^{]+))?\s*$"
)
MEMBER = re.compile(r"^\s{1,8}(?:public|private|protected|internal|static|readonly|const|virtual|override|extern|unsafe|sealed)\s+.*?[;{]")


def read(path: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return b""


def parse_dump(text: str) -> tuple[list[dict], str]:
    lines = text.splitlines()
    classes: list[dict] = []
    ns = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^// Namespace: (.*)$", line)
        if m:
            ns = m.group(1).strip()
            i += 1
            if i >= len(lines):
                break
            decl = lines[i].strip()
            dm = DECL.match(decl)
            if not dm:
                i += 1
                continue
            kind, name, base = dm.group(1), dm.group(2).strip(), (dm.group(3) or "").strip()
            body = [line, lines[i]]
            j = i + 1
            methods = 0
            fields = 0
            while j < len(lines) and not lines[j].startswith("// Namespace: "):
                body.append(lines[j])
                s = lines[j].strip()
                if re.match(r"^(public|private|protected|internal|static|virtual|override|extern|unsafe|sealed).*\(", s):
                    methods += 1
                elif re.match(r"^(public|private|protected|internal|static|readonly|const).*;", s):
                    fields += 1
                j += 1
            classes.append(
                {
                    "namespace": ns,
                    "name": name,
                    "kind": kind,
                    "base": base,
                    "methods": methods,
                    "fields": fields,
                    "line": i,
                    "body": "\n".join(body),
                }
            )
            i = j
            continue
        i += 1
    return classes, ns


def load_strings() -> list[str]:
    raw = read(STRINGS)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:  # noqa: BLE001
        return []
    out = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                v = item.get("value") or item.get("string") or item.get("literal")
                if isinstance(v, str):
                    out.append(v)
            elif isinstance(item, str):
                out.append(item)
    return out


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    dump = read(DUMP).decode("utf-8", "replace")
    classes, _ = parse_dump(dump)
    strings = load_strings()
    meta = read(META)

    meta_info = {}
    if len(meta) >= 8:
        import struct
        sanity, version = struct.unpack("<Ii", meta[:8])
        meta_info = {"sanity": hex(sanity), "metadata_version": version, "size": len(meta)}

    ns_counter = Counter(c["namespace"] or "(global)" for c in classes)
    kind_counter = Counter(c["kind"] for c in classes)

    index = [
        {
            "namespace": c["namespace"],
            "name": c["name"],
            "kind": c["kind"],
            "base": c["base"],
            "methods": c["methods"],
            "fields": c["fields"],
        }
        for c in classes
    ]
    with open(os.path.join(OUT, "class-index.json"), "w") as f:
        json.dump(index, f, indent=1)

    interesting = []
    for c in classes:
        blob = f"{c['namespace']}.{c['name']} {c['base']}"
        hits = [k for k in KEYWORDS if k.lower() in blob.lower()]
        if hits:
            interesting.append((hits, c))
    interesting.sort(key=lambda x: (-len(x[0]), x[1]["namespace"], x[1]["name"]))

    with open(os.path.join(OUT, "interesting-classes.cs"), "w") as f:
        for hits, c in interesting[:150]:
            f.write(f"// ===== keywords: {', '.join(hits)}\n")
            f.write(c["body"])
            f.write("\n\n")

    urls = sorted({s for s in strings if s.startswith(("http://", "https://"))})
    ips = sorted({s for s in strings if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?", s or "")})
    emails = sorted({s for s in strings if re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.]+", s or "")})
    jsonish = [s for s in strings if s.strip().startswith(("{", "[")) and len(s) < 2000]
    suspicious = [
        s
        for s in strings
        if re.search(r"(frida|ptrace|magisk|supersu|emulator|root(ed)?|cheat|hack|debugger|signature|tamper|proxy|vpn)", s, re.I)
    ]

    md = ["# IL2CPP analysis", ""]
    if meta_info:
        md += [
            "## global-metadata.dat",
            "",
            f"- size: {meta_info['size']} bytes",
            f"- sanity: `{meta_info['sanity']}`",
            f"- metadata version: **{meta_info['metadata_version']}**",
            "",
        ]
    md += [
        "## dump.cs",
        "",
        f"- size: {len(dump)} bytes",
        f"- classes/structs/enums/interfaces: **{len(classes)}**",
        "- kinds: " + ", ".join(f"{k}={v}" for k, v in kind_counter.items()),
        "",
        "### Namespaces (top 60)",
        "",
        "| namespace | types |",
        "|---|---:|",
    ]
    for n, c in ns_counter.most_common(60):
        md.append(f"| `{n}` | {c} |")
    md += [
        "",
        f"### Keyword matches: {len(interesting)} types",
        "",
        "| keywords | type | base | methods | fields |",
        "|---|---|---|---:|---:|",
    ]
    for hits, c in interesting[:120]:
        md.append(
            f"| {', '.join(hits)} | `{c['namespace']}.{c['name']}` | `{c['base'][:60]}` | {c['methods']} | {c['fields']} |"
        )

    md += ["", "## String literals", "", f"- count: **{len(strings)}**"]
    md += ["", f"### URLs ({len(urls)})", ""]
    for u in urls[:300]:
        md.append(f"- `{u[:300]}`")
    if ips:
        md += ["", f"### IPs ({len(ips)})", ""] + [f"- `{x}`" for x in ips[:100]]
    if emails:
        md += ["", f"### Emails ({len(emails)})", ""] + [f"- `{x}`" for x in emails[:100]]
    md += ["", f"### JSON-looking literals: {len(jsonish)}", ""]
    for s in jsonish[:100]:
        md.append(f"- `{s[:300]}`")
    md += ["", f"### Anti-cheat / debug / emulator strings: {len(suspicious)}", ""]
    for s in suspicious[:300]:
        md.append(f"- `{s[:300]}`")

    with open(os.path.join(OUT, "il2cpp-report.md"), "w") as f:
        f.write("\n".join(md))
    with open(os.path.join(OUT, "strings.json"), "w") as f:
        json.dump({"count": len(strings), "urls": urls, "ips": ips, "emails": emails,
                   "suspicious": suspicious, "json": jsonish[:1000]}, f, indent=2)

    print("\n".join(md[:80]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
