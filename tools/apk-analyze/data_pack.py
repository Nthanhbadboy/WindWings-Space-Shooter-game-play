#!/usr/bin/env python3
"""Build the engine-agnostic data pack from the extracted analysis CSVs.

Runs offline (no APK needed) on top of what the CI commits back:

    docs/apk-analysis/14-ships.csv          -> datas/ships.json
    docs/apk-analysis/14-drones.csv         -> datas/drones.json
    docs/apk-analysis/14-bosses.csv         -> datas/bosses.json
    docs/apk-analysis/14-items.csv          -> datas/items.json
    docs/apk-analysis/15-enemy-hp.csv       -> datas/enemy_hp.json + datas/boss_hp.json
    docs/apk-analysis/13-iap-products.csv   -> datas/iap_products.json
    docs/apk-analysis/12-localization.csv   -> i18n/en.json + i18n/vi.json
    docs/apk-analysis/04-asset-manifest.csv -> datas/sprites.csv (path_id -> name/png)

Usage: python3 tools/apk-analyze/data_pack.py [--root .]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import re
import sys
from collections import defaultdict

LANGS = ["English", "Vietnamese", "Russian", "Spanish", "French", "Portuguese", "Arabic",
         "Indonesian", "Thai", "Romanian", "Italian", "Japanese", "German", "Czech", "Dutch",
         "SerboCroatian", "Korean", "Turkish", "ChineseSimplified"]

SOURCE_NOTE = "Extracted from WindWings 1.3.118 (com.Wind.wings.Space.Shooter)."


def read_csv(path):
    if not os.path.isfile(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def as_int(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def load_sprites(root):
    """path_id -> {name, png, type} from the export manifest (if it has path_id)."""
    # prefer the fresh CI export (already has path_id), fall back to the committed copy
    candidates = [
        os.environ.get("EXPORT_MANIFEST", "/tmp/apk/unity/export-manifest.csv"),
        os.path.join(root, "docs/apk-analysis/04-asset-manifest.csv"),
    ]
    rows = []
    for c in candidates:
        if c and os.path.isfile(c):
            rows = read_csv(c)
            if rows and "path_id" in rows[0]:
                print("manifest:", c)
                break
            rows = []
    sprites = {}
    if rows and "path_id" not in rows[0]:
        return sprites, False
    for r in rows:
        pid = (r.get("path_id") or "").strip()
        if not pid:
            continue
        sprites[pid] = {"name": r.get("name", ""), "png": r.get("path", ""),
                        "type": r.get("type", ""), "bytes": as_int(r.get("bytes")),
                        "width": as_int(r.get("width")), "height": as_int(r.get("height"))}
    return sprites, True


def resolve(sprites, pid):
    s = sprites.get(str(pid))
    return s["name"] if s else None


def dump(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    docs = os.path.join(root, "docs/apk-analysis")
    datas = os.path.join(root, "datas")
    i18n = os.path.join(root, "i18n")

    sprites, have_pids = load_sprites(root)
    print(f"sprites indexed: {len(sprites)} (path_id column present: {have_pids})")

    # ---------------------------------------------------------------- ships
    ships = []
    for r in read_csv(os.path.join(docs, "14-ships.csv")):
        pid = as_int(r.get("Sprite"))
        ships.append({"id": as_int(r.get("id")), "star": round(as_float(r.get("Star")), 3),
                      "actived": (r.get("Actived", "").lower() == "true"),
                      "sprite_path_id": pid, "sprite_name": resolve(sprites, pid)})
    dump(os.path.join(datas, "ships.json"),
         {"source": "Data_Players.allPlayers (ships, id 10001-10024 + 10999)", "count": len(ships),
          "note": SOURCE_NOTE + " star = strength tier, actived=false = locked/unused.", "items": ships})

    # --------------------------------------------------------------- drones
    drones = []
    for r in read_csv(os.path.join(docs, "14-drones.csv")):
        pid = as_int(r.get("Sprite"))
        drones.append({"id": as_int(r.get("id")), "star": round(as_float(r.get("Star")), 3),
                       "actived": (r.get("Actived", "").lower() == "true"),
                       "sprite_path_id": pid, "sprite_name": resolve(sprites, pid)})
    dump(os.path.join(datas, "drones.json"),
         {"source": "Data_Players(Data_Drones).allPlayers (id 20001-20013)", "count": len(drones),
          "note": SOURCE_NOTE, "items": drones})

    # --------------------------------------------------------------- waves
    waves_path = os.path.join(datas, "waves.json")
    if os.path.isfile(waves_path):
        with open(waves_path, encoding="utf-8") as f:
            w = json.load(f)
        print(f"waves.json: {w.get('count_waves')} waves, {w.get('count_spawners')} spawners")

    # --------------------------------------------------------------- bosses
    bosses = []
    for r in read_csv(os.path.join(docs, "14-bosses.csv")):
        wave = as_int(r.get("idWave"))
        pid = as_int(r.get("Sprite"))
        bosses.append({"id_wave": wave, "chapter": 1 if 7000 <= wave < 8000 else 2,
                       "sprite_path_id": pid, "sprite_name": resolve(sprites, pid),
                       "has_icon": pid != 0})
    dump(os.path.join(datas, "bosses.json"),
         {"source": "Data_Boss.allBosses (Boss_Info{idWave, Sprite})", "count": len(bosses),
          "note": SOURCE_NOTE + " chapter 1 = idWave 7001-7022, chapter 2 = 9001-9024; "
                                  "sprite_path_id 0 = wave without boss icon.",
          "items": bosses})

    # ---------------------------------------------------------------- items
    items = []
    for r in read_csv(os.path.join(docs, "14-items.csv")):
        icon = as_int(r.get("iconSprite"))
        stats = [as_int(x) for x in re.findall(r"m_PathID':\s*(\d+)", r.get("allStatSprites") or "")]
        items.append({"index": as_int(r.get("index")), "icon_sprite_path_id": icon,
                      "icon_sprite_name": resolve(sprites, icon),
                      "stat_sprite_path_ids": stats})
    dump(os.path.join(datas, "items.json"),
         {"source": "Data_Items.allDropItems (ItemSprites{index, iconSprite, allStatSprites[]})",
          "count": len(items), "note": SOURCE_NOTE, "items": items})

    # -------------------------------------------------------------- enemy HP
    hp_rows = []
    for r in read_csv(os.path.join(docs, "15-enemy-hp.csv")):
        hp_rows.append({"path": r.get("gameobject", ""), "hp": as_float(r.get("start_hp")),
                        "path_id": as_int(r.get("path_id"))})
    dump(os.path.join(datas, "enemy_hp.json"),
         {"source": "Enemy_Datas.StartHealthPoint (serialized prefabs/scenes)", "count": len(hp_rows),
          "note": SOURCE_NOTE + " runtime HP is scaled by Enemy_Data_Balance and stage.",
          "items": hp_rows})

    # boss HP grouped by root prefab ("" root -> keep as-is)
    grouped = defaultdict(lambda: {"instances": 0, "hp_max": 0.0, "hp_values": set()})
    for row in hp_rows:
        root_name = (row["path"] or "unknown").split("/")[0]
        g = grouped[root_name]
        g["instances"] += 1
        g["hp_max"] = max(g["hp_max"], row["hp"])
        g["hp_values"].add(row["hp"])
    boss_hp = [{"root": k, "instances": v["instances"], "hp_max": v["hp_max"],
                "hp_values": sorted(x for x in v["hp_values"] if x)}
               for k, v in grouped.items()]
    boss_hp.sort(key=lambda x: -x["hp_max"])
    dump(os.path.join(datas, "boss_hp.json"),
         {"source": "15-enemy-hp.csv grouped by root prefab", "count": len(boss_hp),
          "note": "Same prefab appears several times (scene copies). hp_max = strongest copy.",
          "items": boss_hp})

    # ------------------------------------------------------------------ IAP
    iap = defaultdict(list)
    for r in read_csv(os.path.join(docs, "13-iap-products.csv")):
        iap[r.get("type", "unknown")].append(r.get("product_id", ""))
    dump(os.path.join(datas, "iap_products.json"),
         {"source": "IAPProduct ScriptableObject", "note": SOURCE_NOTE,
          "count": sum(len(v) for v in iap.values()),
          "groups": {k: sorted(v) for k, v in iap.items()}})

    # -------------------------------------------------------------- sprites
    if sprites:
        os.makedirs(datas, exist_ok=True)
        with open(os.path.join(datas, "sprites.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["path_id", "type", "name", "png", "bytes", "width", "height"])
            for pid, s in sorted(sprites.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
                w.writerow([pid, s["type"], s["name"], s["png"], s["bytes"],
                            s.get("width", 0), s.get("height", 0)])

    # ---------------------------------------------------------------- i18n
    # CSV was already deduplicated last-wins. Prefer preserved APK arrays:
    # LanguageAssets.GetText uses Contains/IndexOf (report 73).
    native_tables = {}
    graph_dir = os.path.join(root, "reverse-engineering/raw/font-language")
    graph_path = os.path.join(graph_dir, "graph-index.json")
    if os.path.isfile(graph_path):
        with open(graph_path, encoding="utf-8") as f:
            graph = json.load(f)
        for chunk in graph["chunks"]:
            with gzip.open(os.path.join(graph_dir, chunk["path"]), "rt", encoding="utf-8") as f:
                for line in f:
                    row = json.loads(line)
                    if row.get("class_name") != "LanguageAssets":
                        continue
                    table = {}
                    tree = row["tree"]
                    assert len(tree["listKey"]) == len(tree["listValue"])
                    for key, value in zip(tree["listKey"], tree["listValue"]):
                        if key:
                            table.setdefault(key, value)
                    native_tables[row["name"].removeprefix("Language Assets ")] = table
        assert len(native_tables) == graph["scan_counts"]["LanguageAssets"]
    rows = read_csv(os.path.join(docs, "12-localization.csv"))
    if rows:
        langs = [l for l in LANGS if l in rows[0]]
        for lang in ("English", "Vietnamese"):
            if lang not in langs:
                continue
            table = {r["Key"]: r.get(lang, "") for r in rows if r.get("Key")}
            source = f"12-localization.csv column {lang}"
            note = SOURCE_NOTE
            if lang in native_tables:
                table = native_tables[lang]
                source = f"raw/font-language LanguageAssets {lang}, first IndexOf (report 73)"
                note += " Duplicate keys follow APK LanguageAssets.GetText first IndexOf, not CSV last-wins; see report 73."
            dump(os.path.join(i18n, f"{lang[:2].lower()}.json"),
                 {"_source": source,
                  "_count": len(table), "_note": note, "strings": table})
        cfg = {"_note": "Languages available in the build (LanguageAssets).",
               "languages": langs, "default": "English", "fallback": "English"}
        dump(os.path.join(i18n, "languages.json"), cfg)
        print(f"i18n: {len(rows)} keys, languages: {len(langs)}")

    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
