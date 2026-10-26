#!/usr/bin/env python3
"""Try every TypeTreeGeneratorAPI backend against WindWings IL2CPP metadata."""
from __future__ import annotations

import json
import os
import traceback

from TypeTreeGeneratorAPI import TypeTreeGenerator

EXTRACT = "/tmp/apk/extract"
CLASSES = [
    ("Assembly-CSharp.dll", "Data_Players"),
    ("Assembly-CSharp.dll", "LanguageStringData"),
    ("Assembly-CSharp.dll", "IAPProduct"),
    ("Assembly-CSharp.dll", "Player_Saved_Datas"),
    ("Assembly-CSharp.dll", "Player_Attack_1"),
]
VERSIONS = ["2022.3.62f3", "2022.3.62"]
BACKENDS = ["AssetsTools", "AssetStudio", "AssetRipper"]

il2cpp = open(os.path.join(EXTRACT, "libil2cpp.so"), "rb").read()
metadata = open(os.path.join(EXTRACT, "global-metadata.dat"), "rb").read()
lines = ["# TypeTreeGenerator backend probe", ""]

for version in VERSIONS:
    for backend in BACKENDS:
        lines.append(f"## `{backend}` / Unity `{version}`")
        lines.append("")
        try:
            gen = TypeTreeGenerator(version, generator=backend)
            gen.load_il2cpp(il2cpp, metadata)
        except Exception as e:  # noqa: BLE001
            lines.append(f"- INIT ERROR: `{e!r}`")
            lines.append("")
            continue
        for asm, cls in CLASSES:
            try:
                nodes = gen.get_nodes_as_json(asm, cls)
                parsed = json.loads(nodes)
                lines.append(f"- `{cls}`: OK — {len(parsed)} top-level nodes")
                lines.append("```json")
                lines.append(json.dumps(parsed[:3], indent=1)[:1500])
                lines.append("```")
            except Exception as e:  # noqa: BLE001
                lines.append(f"- `{cls}`: FAIL `{e!r}`")
        lines.append("")

open("/tmp/typetree-probe.md", "w").write("\n".join(lines))
print("\n".join(lines))
