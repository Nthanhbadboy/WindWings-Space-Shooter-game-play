#!/usr/bin/env python3
"""Turn extracted ScriptableObject JSON into readable tables.

Input : /tmp/apk/unity/data/<Namespace>.<Class>/<path_id>.json
Output: docs/apk-analysis/12-localization.*  (19 languages, 1,426 keys)
        docs/apk-analysis/13-iap-products.* (99 non-consumable + 71 consumable)
        docs/apk-analysis/14-data-tables.*  (ships, drones, bosses, items)
"""
from __future__ import annotations

import csv
import json
import os
import sys

DATA = os.environ.get("SO_DATA", "/tmp/apk/unity/data")
OUT = os.environ.get("SO_OUT", "docs/apk-analysis")
LANG_ORDER = ["English", "Vietnamese", "Russian", "Spanish", "French", "Portuguese", "Arabic",
              "Indonesian", "Thai", "Romanian", "Italian", "Japanese", "German", "Czech", "Dutch",
              "SerboCroatian", "Korean", "Turkish", "ChineseSimplified"]


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


def pptr(value):
    if isinstance(value, dict):
        return value.get("m_PathID", "")
    return value


def main() -> int:
    os.makedirs(OUT, exist_ok=True)

    # ---------- localization ----------
    langs: dict[str, dict[str, str]] = {}
    order: list[str] = []
    for fn, tree in load_class("LanguageAssets"):
        name = str(tree.get("m_Name", "")).replace("Language Assets ", "").strip()
        keys = tree.get("listKey") or []
        vals = tree.get("listValue") or []
        d = {}
        for i, k in enumerate(keys):
            if i >= len(vals):
                break
            if k not in order:
                order.append(k)
            d[k] = vals[i]
        langs[name] = d
    if langs:
        languages = [l for l in LANG_ORDER if l in langs] + [l for l in langs if l not in LANG_ORDER]
        with open(os.path.join(OUT, "12-localization.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Key"] + languages)
            for k in order:
                w.writerow([k] + [langs[l].get(k, "") for l in languages])
        with open(os.path.join(OUT, "12-localization-vi.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Key", "English", "Vietnamese"])
            for k in order:
                w.writerow([k, langs.get("English", {}).get(k, ""), langs.get("Vietnamese", {}).get(k, "")])
        lines = ["# Localization table", "",
                 f"- keys: **{len(order)}**",
                 f"- languages: **{len(languages)}** ({', '.join(languages)})",
                 f"- Vietnamese entries: **{len(langs.get('Vietnamese', {}))}**", "",
                 "## Sample", "", "| key | English | Vietnamese |", "|---|---|---|"]
        for k in order[:120]:
            en = str(langs.get("English", {}).get(k, "")).replace("|", "/")[:90]
            vi = str(langs.get("Vietnamese", {}).get(k, "")).replace("|", "/")[:90]
            lines.append(f"| `{k}` | {en} | {vi} |")
        lines += ["", "- Full 19-language table: [`12-localization.csv`](12-localization.csv)",
                  "- Key / English / Vietnamese only: [`12-localization-vi.csv`](12-localization-vi.csv)", ""]
        open(os.path.join(OUT, "12-localization.md"), "w", encoding="utf-8").write("\n".join(lines))
        print("localization:", len(order), "keys,", len(languages), "languages")

    # ---------- enemy / boss HP table (from the flat dump) ----------
    hp_csv = os.path.join(DATA, "Enemy_Datas.csv")
    if os.path.isfile(hp_csv):
        rows = []
        with open(hp_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    hp = float(row.get("StartHealthPoint") or 0)
                except ValueError:
                    hp = 0.0
                rows.append((row.get("_gameobject") or row.get("m_Name") or "",
                             hp, row.get("path_id", "")))
        rows.sort(key=lambda r: -r[1])
        with open(os.path.join(OUT, "15-enemy-hp.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["gameobject", "start_hp", "path_id"])
            w.writerows(rows)
        lines = ["# Enemy / boss HP (từ `Enemy_Datas` MonoBehaviour)", "",
                 f"- số instance: **{len(rows)}**",
                 f"- HP lớn nhất: **{rows[0][1]:,.0f}** (`{rows[0][0] or 'không tên'}`)",
                 "", "## Top 40 theo HP", "", "| # | GameObject | StartHealthPoint |", "|---:|---|---:|"]
        for i, (name, hp, _) in enumerate(rows[:40], 1):
            lines.append(f"| {i} | `{name or '—'}` | {hp:,.0f} |")
        roots: dict[str, list[float]] = {}
        for name, hp, _ in rows:
            root = (name or "?").split("/")[0]
            roots.setdefault(root, []).append(hp)
        agg = sorted(((r, max(v), len(v)) for r, v in roots.items()), key=lambda x: -x[1])
        lines += ["", "## Top 30 prefab gốc theo HP cao nhất", "",
                  "| root prefab | HP max | số component HP |", "|---|---:|---:|"]
        for r, hp, n in agg[:30]:
            lines.append(f"| `{r}` | {hp:,.0f} | {n} |")
        lines += ["", "- Bảng đầy đủ: [`15-enemy-hp.csv`](15-enemy-hp.csv)",
                  "- Đây là HP serialize trong prefab/scene của `data.unity3d`; giá trị runtime còn bị",
                  "  nhân bởi `Enemy_Data_Balance` / `Stage_Get_Datas` theo chapter/stage.", ""]
        open(os.path.join(OUT, "15-enemy-hp.md"), "w", encoding="utf-8").write("\n".join(lines))
        print("enemy hp rows:", len(rows))

    # ---------- IAP ----------
    iap = [tree for _, tree in load_class("IAPProduct")]
    if iap:
        products = set()
        lines = ["# IAP products", ""]
        for t in iap:
            for key in ("NonConsumableProducts", "ConsumableProducts"):
                vals = t.get(key) or []
                lines += [f"## `{key}` ({len(vals)})", ""]
                for v in vals:
                    lines.append(f"- `{v}`")
                    products.add((key, str(v)))
                lines.append("")
        lines += [f"**Total product IDs: {len(products)}**", ""]
        open(os.path.join(OUT, "13-iap-products.md"), "w").write("\n".join(lines))
        with open(os.path.join(OUT, "13-iap-products.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["type", "product_id"])
            w.writerows(sorted(products))
        print("iap:", len(products))

    # ---------- data tables ----------
    tables = [("Data_Players", "allPlayers", "ships"), ("Data_Players", "allPlayers", "drones"),
              ("Data_Boss", "allBosses", "bosses"), ("Data_Items", "allDropItems", "items")]
    lines = ["# Data tables", ""]
    for cls, array_key, label in tables:
        rows = []
        for fn, tree in load_class(cls):
            name = str(tree.get("m_Name", ""))
            if label == "ships" and name != "Data_Players":
                continue
            if label == "drones" and name != "Data_Drones":
                continue
            for item in tree.get(array_key) or []:
                if isinstance(item, dict):
                    rows.append(item)
        if not rows:
            continue
        keys = sorted({k for r in rows for k in r})
        out_csv = os.path.join(OUT, f"14-{label}.csv")
        with open(out_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(keys)
            for r in rows:
                w.writerow([pptr(r.get(k, "")) for k in keys])
        lines += [f"## `{label}` (`{cls}.{array_key}`) — {len(rows)} rows", "",
                  "| " + " | ".join(keys) + " |",
                  "|" + "|".join(["---"] * len(keys)) + "|"]
        for r in rows[:200]:
            lines.append("| " + " | ".join(str(pptr(r.get(k, "")))[:60] for k in keys) + " |")
        lines.append("")
        print("table:", label, len(rows))
    open(os.path.join(OUT, "14-data-tables.md"), "w").write("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
