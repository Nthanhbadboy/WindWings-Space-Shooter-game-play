#!/usr/bin/env python3
"""Verifier receipts generator — role build-spec/verifier (branch arena/ef6b75ef).

Checks the Godot-coder delivery `game/` at a given commit WITHOUT running Godot
(no engine binary in this sandbox). Every number in the human report is re-derived
here so the report can be audited line by line.

Usage:
  python3 verify_m1m4.py --target /tmp/verify-m1m4 --canonical . \
      --peer-csv-dir /tmp --out verify_m1m4.json

  --peer-csv-dir must contain Item_Movement.csv, Enemy_Movement.csv, Gun_Attack.csv
  exported from the spec branch commit the coder pinned (default: skip those checks).

Nothing here mutates the target tree.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

SCHEMA = "verify-ef6b75ef-m1m4/v2"
SECRET_TOKENS = ("keystore", "apikey", "api_key", "secret", "password", "bearer ")
NETWORK_TOKENS = (
    "HTTPRequest", "HTTPClient", "StreamPeerTCP", "StreamPeerTLS", "WebSocketPeer",
    "PacketPeerUDP", "UDPServer", "TCPServer", "OS.execute", "OS.shell_open",
    "JavaScriptBridge", "JavaClassWrapper", "Engine.has_singleton",
    "ClassDB.instantiate", 'load("res://addons',
)
MAPPING_FIELDS = {
    "bullet_id": "bltId",
    "damage": "bltDamage",
    "speed": "bltSpeed",
    "lifetime_seconds": "bltLifetime",
    "gun_type": "gunType",
    "time_start_seconds": "timeStart",
    "count_mags": "allGunDatas[0].countMags",
    "count_shots": "allGunDatas[0].countShots",
    "time_reload_seconds": "allGunDatas[0].timeReload",
    "time_rounds_seconds": "allGunDatas[0].timeRounds",
    "time_shot_seconds": "allGunDatas[0].timeShot",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(p: Path, root: Path) -> str:
    return str(p.relative_to(root)).replace("\\", "/")


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_gdscript(paths: list[Path]) -> dict:
    try:
        from gdtoolkit.parser import parser as gdparser  # type: ignore
    except Exception as exc:  # pragma: no cover
        return {"status": "UNVERIFIABLE", "reason": f"gdtoolkit import failed: {exc}",
                "parsed": 0, "failed": [], "tool": None}
    ok, failed = 0, []
    for p in paths:
        try:
            gdparser.parse(p.read_text())
            ok += 1
        except Exception as exc:
            failed.append({"file": p.name, "error": f"{type(exc).__name__}: {exc}"[:300]})
    try:
        import importlib.metadata as md
        version = md.version("gdtoolkit")
    except Exception:
        version = "unknown"
    return {"status": "PASS" if not failed else "FAIL", "parsed": ok, "failed": failed,
            "tool": f"gdtoolkit {version} (Godot 4 GDScript parser)"}


def check_coins(game_coins: dict, csv_dir: Path | None) -> dict:
    if csv_dir is None:
        return {"status": "UNVERIFIABLE", "reason": "no --peer-csv-dir"}
    rows = list(csv.DictReader(open(csv_dir / "Item_Movement.csv")))
    coin_rows = {r["_gameobject"] for r in rows
                 if r["isCoin"] == "True" and r["_gameobject"].startswith("Wave_0000")}
    listed = {c["gameobject_path"] for c in game_coins.get("coins", [])}
    return {
        "status": "PASS" if listed == coin_rows else "FAIL",
        "declared_count": game_coins.get("count"),
        "listed": len(listed),
        "source_rows": len(coin_rows),
        "listed_not_in_source": sorted(listed - coin_rows),
        "source_not_listed": sorted(coin_rows - listed),
        "ids": sorted({str(c["item_id"]) for c in game_coins.get("coins", [])}),
        "source_csv_sha256": sha256(csv_dir / "Item_Movement.csv"),
    }


def check_movement(game_mov: dict, csv_dir: Path | None) -> dict:
    if csv_dir is None:
        return {"status": "UNVERIFIABLE", "reason": "no --peer-csv-dir"}
    rows = list(csv.DictReader(open(csv_dir / "Enemy_Movement.csv")))
    bad = []
    for pid, rec in game_mov.get("enemy_by_id", {}).items():
        cands = [r for r in rows if r["_gameobject"].split("/")[0].endswith(f"-{pid}")]
        if not cands:
            bad.append({"id": pid, "issue": "no source row"})
            continue
        speeds = sorted({r["listSpeeds[0]"] for r in cands if r["listSpeeds[0]"]})
        turrets = sorted({r["isTurret"] for r in cands})
        if len(speeds) > 1:
            bad.append({"id": pid, "issue": f"source has several listSpeeds[0] {speeds}"})
        elif speeds and abs(float(speeds[0]) - float(rec.get("speed", 0))) > 1e-6:
            bad.append({"id": pid, "issue": f"speed {rec.get('speed')} vs {speeds[0]}"})
        if len(turrets) == 1 and bool(rec.get("is_turret")) != (turrets[0] == "True"):
            bad.append({"id": pid, "issue": f"isTurret {rec.get('is_turret')} vs {turrets[0]}"})
    return {"status": "PASS" if not bad else "FAIL", "ids": len(game_mov.get("enemy_by_id", {})),
            "mismatches": bad, "source_csv_sha256": sha256(csv_dir / "Enemy_Movement.csv")}


def check_guns(game_guns: dict, csv_dir: Path | None) -> dict:
    if csv_dir is None:
        return {"status": "UNVERIFIABLE", "reason": "no --peer-csv-dir"}
    rows = list(csv.DictReader(open(csv_dir / "Gun_Attack.csv")))
    per_id, bad = {}, []
    for pid, rec in game_guns.get("enemy_by_id", {}).items():
        prefab = rec["prefab"]
        sel = [r for r in rows if r["_gameobject"].startswith(f"{prefab}/Enemy_Ingame")]
        signatures = {tuple(r[k] for k in MAPPING_FIELDS.values()) for r in sel}
        alts = rec.get("alternatives", [])
        per_id[pid] = {"source_rows": len(sel), "source_distinct": len(signatures), "game_alternatives": len(alts)}
        if len(signatures) != len(alts):
            bad.append({"id": pid, "issue": f"distinct source {len(signatures)} vs alternatives {len(alts)}"})
            continue
        for alt in alts:
            match = None
            for sig in signatures:
                ok = True
                for game_key, csv_key in MAPPING_FIELDS.items():
                    cv, av = num(sig[list(MAPPING_FIELDS.values()).index(csv_key)]), alt.get(game_key)
                    if cv is None or av is None:
                        continue
                    if abs(cv - float(av)) > 1e-5:
                        ok = False
                        break
                if ok:
                    match = sig
                    break
            if match is None:
                bad.append({"id": pid, "issue": "alternative has no matching source signature"})
    return {"status": "PASS" if not bad else "FAIL", "per_id": per_id, "mismatches": bad,
            "source_csv_sha256": sha256(csv_dir / "Gun_Attack.csv")}


def check_training_gun(training: dict, csv_dir: Path | None) -> dict:
    if csv_dir is None:
        return {"status": "UNVERIFIABLE", "reason": "no --peer-csv-dir"}
    rows = list(csv.DictReader(open(csv_dir / "Gun_Attack.csv")))
    sel = [r for r in rows if r["_gameobject"].startswith(f"{training['prefab']}/Enemy_Ingame")
           and r["bltId"] == str(int(training["bullet_id"]))]
    if not sel:
        return {"status": "FAIL", "reason": "no source row with that prefab + bltId"}
    r = sel[0]
    same = (abs(num(r["bltDamage"]) - training["damage"]) < 1e-5
            and abs(num(r["bltSpeed"]) - training["speed"]) < 1e-5
            and abs(num(r["bltLifetime"]) - training["lifetime_seconds"]) < 1e-5
            and num(r["timeStart"]) == training["time_start_seconds"])
    return {"status": "PASS" if same else "FAIL", "rows": len(sel),
            "source": {k: r[k] for k in ("bltId", "bltDamage", "bltSpeed", "bltLifetime", "timeStart")}}


def check_il2cpp(game_stats: dict, canonical: Path) -> dict:
    path = canonical / "reverse-engineering/il2cpp/ia-resolved.json"
    entries = json.loads(path.read_text())["methods"].get("Player_Get_Datas.cctor")
    if not entries:
        return {"status": "UNVERIFIABLE", "reason": "no Player_Get_Datas.cctor entries"}
    game = {f["field"]: f["values"] for f in game_stats["fields"]}
    matched = {}
    for entry in entries:
        raw, n = bytes.fromhex(entry["raw"])[: 4 * entry["len"]], entry["len"]
        for typ in ("int", "float"):
            vals = list(struct.unpack(f"<{n}{'i' if typ == 'int' else 'f'}", raw))
            for name, gv in game.items():
                if name in matched or len(gv) != n:
                    continue
                if typ == "int":
                    ok = all(int(x) == int(y) for x, y in zip(vals, gv))
                else:
                    ok = all(abs(float(x) - float(y)) <= 1e-4 * max(1.0, abs(float(y))) for x, y in zip(vals, gv))
                if ok:
                    matched[name] = {"addr": entry["addr"], "type": typ}
    return {"status": "PASS" if len(matched) == len(game) else "FAIL",
            "fields": len(game), "matched": len(matched), "map": matched,
            "source_sha256": sha256(path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--peer-csv-dir", default=None)
    ap.add_argument("--out", default="verify_m1m4.json")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    canon = Path(args.canonical).resolve()
    csv_dir = Path(args.peer_csv_dir).resolve() if args.peer_csv_dir else None
    game = target / "game"
    if not game.is_dir():
        print(f"missing {game}", file=sys.stderr)
        return 2

    files = sorted(p for p in game.rglob("*") if p.is_file())
    by_ext: dict[str, int] = {}
    for p in files:
        key = p.suffix.lower() or "(none)"
        by_ext[key] = by_ext.get(key, 0) + 1
    media = [rel(p, target) for p in files if p.suffix.lower() in
             (".png", ".jpg", ".jpeg", ".webp", ".svg", ".wav", ".ogg", ".mp3", ".ttf", ".otf", ".atlas")]

    receipts: dict = {
        "schema": SCHEMA,
        "inputs": {},
        "inventory": {
            "files": len(files), "by_ext": by_ext, "media_files": media,
            "max_bytes": max(p.stat().st_size for p in files),
            "total_bytes": sum(p.stat().st_size for p in files),
            "sha256": {rel(p, target): sha256(p) for p in files},
        },
        "checks": {},
    }

    banned = [rel(p, target) for p in files if p.suffix.lower() in
              (".keystore", ".jks", ".pfx", ".p12", ".exe", ".apk", ".aab", ".dll", ".so")]
    over = [rel(p, target) for p in files if p.stat().st_size >= 5_000_000]
    receipts["checks"]["V1_hygiene"] = {
        "status": "PASS" if not banned and not over else "FAIL",
        "banned_files": banned, "over_5mb": over,
    }

    gd_files = [p for p in files if p.suffix == ".gd"]
    tscn_files = [p for p in files if p.suffix == ".tscn"]
    data_dir = game / "data"

    provenance = []
    for p in sorted(data_dir.glob("*.json")):
        doc = json.loads(p.read_text())
        entry = {"file": rel(p, target), "sha256": sha256(p), "source": None, "source_sha256": None,
                 "canonical_sha256": None, "match": None}
        if isinstance(doc, dict):
            entry["source"] = doc.get("source")
            entry["source_sha256"] = doc.get("source_sha256")
        m = re.search(r"(datas/[\w./-]+\.json(?:\.gz)?)", entry["source"] or "")
        if m and (canon / m.group(1)).exists():
            entry["canonical_sha256"] = sha256(canon / m.group(1))
            want = entry["source_sha256"] or entry["sha256"]
            entry["match"] = entry["canonical_sha256"] == want
        provenance.append(entry)
    unpinned = [e["file"] for e in provenance if e["source"] and not e["source_sha256"]]
    receipts["checks"]["V8_provenance"] = {
        "status": "PASS" if not media and not [e for e in provenance if e["match"] is False] else "FAIL",
        "media_files": len(media), "data_files": provenance,
        "unpinned_sources": unpinned,
    }

    receipts["checks"]["parse_gdscript"] = parse_gdscript(gd_files)

    missing: list[str] = []
    for p in tscn_files:
        for m in re.finditer(r'path="res://([^"]+)"', p.read_text()):
            if not (game / m.group(1)).exists():
                missing.append(f"{rel(p, target)} -> res://{m.group(1)}")
    for p in gd_files:
        for m in re.finditer(r'(?:preload|load)\("res://([^"]+)"\)', p.read_text()):
            if not (game / m.group(1)).exists():
                missing.append(f"{rel(p, target)} -> res://{m.group(1)}")
    proj = (game / "project.godot").read_text()
    main_scene = re.search(r'run/main_scene="res://([^"]+)"', proj)
    main_ok = bool(main_scene) and (game / main_scene.group(1)).exists()
    class_names = sorted(re.findall(r"^class_name\s+(\w+)", "\n".join(p.read_text() for p in gd_files), re.M))
    dupes = sorted({c for c in class_names if class_names.count(c) > 1})
    receipts["checks"]["resources"] = {
        "status": "PASS" if not missing and main_ok and not dupes else "FAIL",
        "missing": missing, "main_scene": main_scene.group(1) if main_scene else None,
        "main_scene_exists": main_ok, "scenes": len(tscn_files), "scripts": len(gd_files),
        "class_names": class_names, "duplicate_class_names": dupes,
    }

    hits = []
    for p in gd_files:
        text = p.read_text()
        for tok in NETWORK_TOKENS + SECRET_TOKENS:
            if tok in text:
                hits.append({"file": rel(p, target), "token": tok})
    receipts["checks"]["network_and_secrets"] = {
        "status": "PASS" if not hits else "FAIL", "hits": hits,
        "tokens_checked": len(NETWORK_TOKENS) + len(SECRET_TOKENS),
    }

    wave = json.loads((data_dir / "wave_0000.json").read_text())
    rows = wave["wave"]["spawners"]
    copies = sum(int(r.get("copies", 1)) for r in rows)
    entries = sum(int(r.get("copies", 1)) * len(r.get("enemies", [])) for r in rows)
    prefabs = sorted({e for r in rows for e in r.get("enemies", [])})
    hp = json.loads((data_dir / "enemy_hp_by_id.json").read_text())
    mov = json.loads((data_dir / "enemy_movement_wave_0000.json").read_text())
    guns = json.loads((data_dir / "enemy_guns_wave_0000.json").read_text())
    coins = json.loads((data_dir / "wave_0000_coin_manifest.json").read_text())
    stats = json.loads((data_dir / "player_start_stats.json").read_text())
    shop = json.loads((data_dir / "shop_contract.json").read_text())
    pvp = json.loads((data_dir / "pvp_reward_arrays.json").read_text())
    iap = json.loads((data_dir / "iap_products.json").read_text())
    groups = iap.get("groups", {})
    iap_ids = [str(x) for k in ("ConsumableProducts", "NonConsumableProducts") for x in groups.get(k, [])]
    ids = {str(int(p.split("-", 1)[1])) for p in prefabs}
    hp_keys = {str(k) for k in hp["hp_by_id"]}
    mov_keys = {str(k) for k in mov["enemy_by_id"]}

    canon_rows = next(w["spawners"] for w in json.loads((canon / "datas/waves.json").read_text())["waves"]
                      if w.get("wave") == "Wave_0000")

    checks_ok = [
        len(rows) == 42 and copies == 150 and entries == 883 and len(prefabs) == 15,
        rows == canon_rows,
        len(hp["hp_by_id"]) == 150 and not (ids - hp_keys) and not (ids - mov_keys),
        iap.get("count") == 170 and len(set(iap_ids)) == 170,
        len(shop.get("families", [])) == 3 and all(f.get("slots") == 5 for f in shop.get("families", [])),
        len(pvp.get("arrays", {})) == 6,
    ]
    receipts["checks"]["data"] = {
        "status": "PASS" if all(checks_ok) else "FAIL",
        "wave": {"rows": len(rows), "sum_copies": copies, "entries_copies_x_len": entries,
                 "prefabs": len(prefabs), "identical_to_canonical": rows == canon_rows},
        "hp": {"entries": len(hp["hp_by_id"]), "declared": hp.get("count"), "prefabs_missing": sorted(ids - hp_keys)},
        "movement": {"entries": len(mov["enemy_by_id"]), "prefabs_missing": sorted(ids - mov_keys)},
        "iap": {"count_field": iap.get("count"), "consumable": len(groups.get("ConsumableProducts", [])),
                "non_consumable": len(groups.get("NonConsumableProducts", [])), "unique": len(set(iap_ids))},
        "shop": {"families": [f.get("name") for f in shop.get("families", [])],
                 "slots": [f.get("slots") for f in shop.get("families", [])],
                 "shop_names": shop.get("shop_names"), "popup_quantity": shop.get("popup_quantity")},
        "pvp": {"arrays": sorted(pvp.get("arrays", {}))},
    }

    base = (game / "scripts/monetization_provider.gd").read_text()
    svc = (game / "scripts/monetization_service.gd").read_text()
    cfg = json.loads((data_dir / "monetization_config.json").read_text())
    fail_closed = {
        "base_is_available_false": "func is_available() -> bool:\n\treturn false" in base,
        "config_real_plugins_disabled": cfg.get("real_plugins_enabled") is False,
        "service_stub_marker": "STUB_ONLY" in svc,
        "stubs_extend_base": all("extends MonetizationProvider" in (game / f"scripts/{n}").read_text()
                                 for n in ("amazon_iap_stub.gd", "hms_iap_ads_stub.gd", "windows_commerce_stub.gd")),
        "no_sdk_or_network": not hits,
        "provider_count": len(cfg.get("provider_ids", [])),
    }
    fail_closed["status"] = "PASS" if (fail_closed["base_is_available_false"] and fail_closed["config_real_plugins_disabled"]
                                       and fail_closed["service_stub_marker"] and fail_closed["stubs_extend_base"]
                                       and fail_closed["no_sdk_or_network"]) else "FAIL"
    receipts["checks"]["fail_closed_monetization"] = fail_closed

    receipts["checks"]["source_reconciliation"] = {
        "coins": check_coins(coins, csv_dir),
        "movement": check_movement(mov, csv_dir),
        "guns": check_guns(guns, csv_dir),
        "training_gun": check_training_gun(json.loads((data_dir / "training_gun.json").read_text()), csv_dir),
    }
    sr = receipts["checks"]["source_reconciliation"]
    sr["status"] = "PASS" if all(sr[k].get("status") == "PASS" for k in sr) else (
        "UNVERIFIABLE" if all(sr[k].get("status") == "UNVERIFIABLE" for k in sr) else "FAIL")
    identical = {}
    for name, canon_path in (("iap_products.json", "datas/iap_products.json"),
                             ("items.json", "datas/items.json"),
                             ("enemy_hp_by_id.json", "datas/enemy_hp_by_id.json")):
        cpath = canon / canon_path
        identical[name] = bool(cpath.exists()) and sha256(data_dir / name) == sha256(cpath)
    receipts["checks"]["canonical_identity"] = {
        "status": "PASS" if all(identical.values()) else "FAIL",
        "byte_identical_to_datas": identical,
    }
    receipts["checks"]["il2cpp_decode"] = check_il2cpp(stats, canon)

    baseline = json.loads((data_dir / "player_baseline.json").read_text())
    claim_rows = [
        ("wave has 42 spawner rows", len(rows) == 42),
        ("sum(copies) = 150", copies == 150),
        ("883 entry attempts", entries == 883),
        ("15 prefab ids referenced", len(prefabs) == 15),
        ("150-entry HP map", len(hp["hp_by_id"]) == 150),
        ("49 coin objects", coins.get("count") == 49),
        ("24-entry StartMainCannonDamages", len(stats["fields"][1]["values"]) == 24),
        ("24-entry PlayerCosts", len(stats["fields"][0]["values"]) == 24),
        ("170 product ids", iap.get("count") == 170),
        ("baseline hull 2500", baseline.get("base_hp") == 2500.0),
        ("3 s invulnerability", baseline.get("hit_invulnerability_seconds") == 3.0),
        ("no original media", not media),
    ]
    receipts["checks"]["claims"] = {
        "status": "PASS" if all(ok for _, ok in claim_rows) else "FAIL",
        "results": [{"claim": c, "holds": ok} for c, ok in claim_rows],
    }

    receipts["checks"]["engine_boundaries"] = {
        "status": "UNVERIFIABLE",
        "V2_preset_contract": "no export_presets.cfg in game/ — nothing to diff against GODOT_EXPORT_PRESET_CONTRACT.json",
        "V3_version_consistency": "no version.json / no version output — not delivered yet",
        "V4_engine_constraints": "partial: renderer gl_compatibility + min_sdk default only; no preset to read",
        "V5_rebuild": "no Godot binary in sandbox (Godot 4.7.2-stable unavailable) — cannot import or launch",
        "V6_size": "no export artifact",
        "V7_signature": "no APK/AAB, no apksigner",
        "project_features": re.search(r'config/features=(.*)', proj).group(1) if re.search(r'config/features=(.*)', proj) else None,
        "renderer": re.search(r'renderer/rendering_method="([^"]+)"', proj).group(1) if re.search(r'renderer/rendering_method="([^"]+)"', proj) else None,
        "viewport": re.search(r'window/size/viewport_width=(\d+)\nwindow/size/viewport_height=(\d+)', proj).groups() if re.search(r'viewport_width=(\d+)', proj) else None,
    }

    receipts["inputs"] = {
        "target_tree_sha256": hashlib.sha256(
            "".join(f"{rel(p, target)}:{sha256(p)}\n" for p in files).encode()).hexdigest(),
        "canonical": {k: sha256(canon / k) for k in
                      ("datas/waves.json", "datas/enemy_hp_by_id.json", "datas/iap_products.json",
                       "datas/items.json", "reverse-engineering/il2cpp/ia-resolved.json")},
    }
    receipts["tool"] = {"name": "verify_m1m4.py", "schema": SCHEMA,
                        "parser": receipts["checks"]["parse_gdscript"].get("tool")}
    receipts["summary"] = {k: v.get("status") for k, v in receipts["checks"].items()}

    Path(args.out).write_text(json.dumps(receipts, indent=1, sort_keys=True) + "\n")
    print(json.dumps(receipts["summary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
