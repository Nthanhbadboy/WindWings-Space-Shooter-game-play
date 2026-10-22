#!/usr/bin/env python3
"""Turn extracted ScriptableObject JSON into readable tables.

Input : /tmp/apk/unity/data/<Namespace>.<Class>/<path_id>.json
Output: docs/apk-analysis/12-localization.md + .csv
        docs/apk-analysis/13-iap-products.md + .csv
        docs/apk-analysis/14-data-tables.md + .csv
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

DATA = "/tmp/apk/unity/data"
OUT = "docs/apk-analysis"


def load_class(cls: str):
    out = []
    for name in os.listdir(DATA):
        if name.split(".")[-1] != cls:
            continue
        base = os.path.join(DATA, name)
        if not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            if not fn.endswith(".json"):
                continue
            try:
                out.append((fn, json.load(open(os.path.join(base, fn)))))
            except Exception:  # noqa: BLE001
                pass
    return out


def pptr_name(value):
    if isinstance(value, dict):
        return value.get("m_Name") or value.get("name") or json.dumps(value)[:80]
    return value


def main() -> int:
    os.makedirs(OUT, exist_ok=True)

    # ---- localization ----
    rows = []
    for fn, tree in load_class("LanguageStringData"):
        items = tree.get("m_Items") or tree.get("Items") or []
        if isinstance(items, dict):
            items = [items]
        for item in items:
            if isinstance(item, dict):
                rows.append(item)
    if rows:
        fields = ["Keys", "English", "Vietnamese", "Japanese", "ChineseSimplified",
                  "Korean", "Thai", "Indonesian", "Spanish", "Portuguese", "French", "German"]
        fields = [f for f in fields if any(f in r for r in rows)]
        with open(os.path.join(OUT, "12-localization.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(fields)
            for r in rows:
                w.writerow([r.get(k, "") for k in fields])
        lines = ["# Localization table", "", f"- entries: **{len(rows)}**",
                 f"- languages: {len([k for k in rows[0] if k != 'Keys'])}", "",
                 "## Sample (first 100 keys)", "",
                 "| key | English | Vietnamese |", "|---|---|---|"]
        for r in rows[:100]:
            lines.append(f"| `{r.get('Keys','')}` | {str(r.get('English','')).replace('|','/')[:80]} | {str(r.get('Vietnamese','')).replace('|','/')[:80]} |")
        lines += ["", "Full table: [`12-localization.csv`](12-localization.csv)", ""]
        open(os.path.join(OUT, "12-localization.md"), "w").write("\n".join(lines))
        print("localization rows:", len(rows))

    # ---- IAP ----
    iap = []
    for fn, tree in load_class("IAPProduct"):
        iap.append(tree)
    if iap:
        lines = ["# IAP products", ""]
        products = set()
        for t in iap:
            for key in ("NonConsumableProducts", "ConsumableProducts"):
                vals = t.get(key) or []
                lines.append(f"## `{key}` ({len(vals)})")
                lines.append("")
                for v in vals:
                    lines.append(f"- `{v}`")
                    products.add((key, v))
                lines.append("")
        lines += ["", f"Total product IDs: **{len(products)}**", ""]
        open(os.path.join(OUT, "13-iap-products.md"), "w").write("\n".join(lines))
        with open(os.path.join(OUT, "13-iap-products.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["type", "product_id"])
            w.writerows(sorted(products))

    # ---- data tables ----
    lines = ["# Data tables", ""]
    csvs = []
    for cls, array_key in (("Data_Players", "allPlayers"), ("Data_Boss", "allBosses"), ("Data_Items", "allDropItems")):
        rows = []
        for fn, tree in load_class(cls):
            items = tree.get(array_key) or []
            for item in items:
                if isinstance(item, dict):
                    rows.append(item)
        if not rows:
            continue
        keys = sorted({k for r in rows for k in r})
        with open(os.path.join(OUT, f"14-{cls}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(keys)
            for r in rows:
                w.writerow([pptr_name(r.get(k, "")) for k in keys])
        lines += [f"## `{cls}.{array_key}` — {len(rows)} rows", "",
                  "| " + " | ".join(keys) + " |",
                  "|" + "|".join(["---"] * len(keys)) + "|"]
        for r in rows[:200]:
            lines.append("| " + " | ".join(str(pptr_name(r.get(k, "")))[:60] for k in keys) + " |")
        lines.append("")
        csvs.append(cls)
    open(os.path.join(OUT, "14-data-tables.md"), "w").write("\n".join(lines))
    print("data tables:", csvs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
