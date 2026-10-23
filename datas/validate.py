#!/usr/bin/env python3
"""Validate the data pack in datas/ and i18n/.

    python3 datas/validate.py

Checks that every JSON parses, that the declared `count` matches the payload,
that IDs are unique, and that both language files cover the same keys.
Exits non-zero on any problem, so it can be used in CI.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
errors: list[str] = []


def load(name):
    path = os.path.join(HERE, name)
    if not os.path.isfile(path):
        errors.append(f"missing {name}")
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        errors.append(f"{name}: invalid JSON ({e})")
        return None


def check_items(name, key):
    data = load(name)
    if data is None:
        return []
    items = data.get("items", [])
    if data.get("count") != len(items):
        errors.append(f"{name}: count={data.get('count')} but {len(items)} items")
    ids = [i.get(key) for i in items]
    dupes = {x for x in ids if ids.count(x) > 1}
    if dupes:
        errors.append(f"{name}: duplicate {key}: {sorted(dupes)[:5]}")
    print(f"{name:24s} {len(items):5d} items")
    return items


def main() -> int:
    ships = check_items("ships.json", "id")
    drones = check_items("drones.json", "id")
    bosses = check_items("bosses.json", "id_wave")
    items = check_items("items.json", "index")
    hp = check_items("enemy_hp.json", "path_id")
    boss_hp = check_items("boss_hp.json", "root")

    iap = load("iap_products.json")
    if iap:
        n = sum(len(v) for v in iap.get("groups", {}).values())
        if iap.get("count") != n:
            errors.append(f"iap_products.json: count={iap.get('count')} but {n} ids")
        print(f"{'iap_products.json':24s} {n:5d} ids")

    for name in ("ships.json", "drones.json"):
        data = load(name) or {}
        unlocked = [i for i in data.get("items", []) if i.get("actived")]
        print(f"  {name}: {len(unlocked)} active of {len(data.get('items', []))}")

    for name in ("en.json", "vi.json"):
        data = load(os.path.join("..", "i18n", name))
        if data:
            print(f"i18n/{name:20s} {data.get('_count', len(data.get('strings', {}))):5d} keys")

    en = load(os.path.join("..", "i18n", "en.json")) or {}
    vi = load(os.path.join("..", "i18n", "vi.json")) or {}
    missing_vi = set(en.get("strings", {})) - set(vi.get("strings", {}))
    if missing_vi:
        errors.append(f"vi.json missing {len(missing_vi)} keys, e.g. {sorted(missing_vi)[:3]}")
    empty_vi = [k for k, v in vi.get("strings", {}).items() if not str(v).strip()]
    if empty_vi:
        print(f"  note: {len(empty_vi)} Vietnamese strings are empty")

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("\nOK — data pack consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
