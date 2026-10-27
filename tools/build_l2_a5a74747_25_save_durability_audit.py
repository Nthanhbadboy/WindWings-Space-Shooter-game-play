#!/usr/bin/env python3
"""Build a scoped static save/flush/migration-entry audit for PR12 item #25.

The audit is limited to the pinned persistence receipts plus literal direct
branch references in the current checkout's raw ASM corpus. It is not a global
save-schema or runtime-durability proof.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OPENING_PATH = Path("reverse-engineering/raw/persistence/opening-contracts.json.gz")
LOADOUT_PATH = Path("reverse-engineering/raw/player-loadout/contracts.json.gz")
LOADOUT_INDEX_PATH = Path("reverse-engineering/raw/player-loadout/index.json")
PREFERENCES_ASM_PATH = Path("reverse-engineering/raw/ui-audit/extra-native/PlayerPreferences.asm.txt")
PREFERENCES_JSON_PATH = Path("reverse-engineering/raw/ui-audit/extra-native/PlayerPreferences.json")
DUMP_PATH = Path("reverse-engineering/il2cpp/dump.cs.gz")
OPENING_DATA_PATH = Path("datas/opening_persistence.json")
LOADOUT_DATA_PATH = Path("datas/player_loadout_persistence.json")
OUTPUT_PATH = Path("datas/l2_a5a74747_25_save_durability_audit.json.gz")

PINS = {
    OPENING_PATH.as_posix(): "ec35b5ab33e4c78a77ad391e5ac9c03d00328b74abc35d8d9ed66f83ca88544f",
    LOADOUT_PATH.as_posix(): "045dd36ff3f81eb4193953860856009dde6ed8c541e2749291eeb9dae22eb276",
    LOADOUT_INDEX_PATH.as_posix(): "f3a049c8c6f4380946395d5e47b6e86230f164fb376dd1ad901bdaa12d4843cd",
    PREFERENCES_ASM_PATH.as_posix(): "aa983280bda35434d4011944a212b85381a726778c7c6b612c786afa5e4d70ac",
    PREFERENCES_JSON_PATH.as_posix(): "ed8dc8c7f3ffb3fbc493d7660ea4ff8f374ca6625a1ce561cc203d5aa23939bd",
    DUMP_PATH.as_posix(): "e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454",
    OPENING_DATA_PATH.as_posix(): "2af3d80567a1a593376091ae24412fe17c3c9616b625f1992e28a4bf71f588e6",
    LOADOUT_DATA_PATH.as_posix(): "2edfab3377f2d8c9cd7f4fa6704f707ca048060c0add67aa496cc1c94c36feb4",
}
SOURCE_DUMP_DECOMPRESSED_SHA256 = "8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c"
PLAYERPREFS_SAVE_RVA = "0x277cf6c"
EXPECTED_ASM_INVENTORY_SHA256 = "c9e29739bc0ade975b85bd8eb26f04afc4cb961a1f0fe3026d6811a0e74a57d0"
DIRECT_BRANCH = re.compile(r"\b(?:bl|b)\s+#?0x0*277cf6c\b", re.IGNORECASE)
SAVE_MIGRATION_SIGNAL = re.compile(r"save[_ ]?version|schema[_ ]?version|migrat(?:e|ion)", re.IGNORECASE)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _load_pinned_json(path: Path, pins: dict[str, str], compressed: bool = False) -> tuple[dict[str, Any], bytes]:
    payload = (ROOT / path).read_bytes()
    if sha256(payload) != pins[path.as_posix()]:
        raise ValueError(f"pinned source SHA-256 mismatch: {path.as_posix()}")
    body = gzip.decompress(payload) if compressed else payload
    return json.loads(body), payload


def _rva(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    try:
        return f"0x{int(value, 16):x}"
    except ValueError:
        return value.lower()


def _method_id(method: dict[str, Any]) -> str:
    return f"{method.get('class_name')}.{method.get('method')}"


def _call_record(method: dict[str, Any], call: dict[str, Any], source: str) -> dict[str, Any]:
    declaration = call.get("declaration") or {}
    return {
        "source_receipt": source,
        "caller": _method_id(method),
        "callsite": call.get("callsite"),
        "instruction": call.get("instruction"),
        "target_rva": call.get("target_rva"),
        "target_class": declaration.get("class_name"),
        "target_signature": declaration.get("signature"),
    }


def _dump_save_declaration(dump_text: str) -> dict[str, str]:
    class_match = re.search(r"public class PlayerPrefs // TypeDefIndex: 7791\s*\{(?P<body>.*?)(?:\n\})", dump_text, re.DOTALL)
    if not class_match:
        raise ValueError("PlayerPrefs TypeDefIndex 7791 class block missing from pinned dump")
    body = class_match.group("body")
    method_match = re.search(
        r"// RVA: (0x[0-9A-Fa-f]+)[^\n]*\n\s*public static void Save\(\) \{ \}", body
    )
    if not method_match:
        raise ValueError("PlayerPrefs.Save() declaration missing from pinned dump")
    rva = _rva(method_match.group(1))
    if rva != PLAYERPREFS_SAVE_RVA:
        raise ValueError(f"PlayerPrefs.Save RVA changed: {rva}")
    return {"class": "UnityEngine.PlayerPrefs", "signature": "public static void Save()", "rva": rva}


def build_receipt(
    opening: dict[str, Any],
    loadout: dict[str, Any],
    loadout_index: dict[str, Any],
    preferences_json: dict[str, Any],
    dump_text: str,
    opening_data: dict[str, Any],
    loadout_data: dict[str, Any],
    source_pins: dict[str, str],
    raw_files: list[dict[str, Any]],
) -> dict[str, Any]:
    opening_methods = opening.get("methods", [])
    loadout_methods = loadout.get("methods", [])
    if len(opening_methods) != 41 or len(loadout_methods) != 33:
        raise ValueError("pinned persistence receipts must retain 41 + 33 method records")
    method_map: dict[str, tuple[str, dict[str, Any]]] = {}
    for source_name, methods in ((OPENING_PATH.as_posix(), opening_methods), (LOADOUT_PATH.as_posix(), loadout_methods)):
        for method in methods:
            key = _method_id(method)
            if key in method_map:
                raise ValueError(f"duplicate selected method record: {key}")
            method_map[key] = (source_name, method)
    if len(method_map) != 74:
        raise ValueError(f"expected 74 distinct selected methods, got {len(method_map)}")

    prefs_methods = [method for method in opening_methods if method.get("class_name") == "PlayerPreferences"]
    if len(prefs_methods) != 18:
        raise ValueError(f"expected 18 PlayerPreferences bodies in opening receipt, got {len(prefs_methods)}")
    if len(preferences_json.get("methods", [])) != 21:
        raise ValueError("raw PlayerPreferences inventory should contain 21 method records")
    if preferences_json.get("class") != "PlayerPreferences":
        raise ValueError("unexpected PlayerPreferences native JSON class label")

    edges: list[dict[str, Any]] = []
    for source_name, methods in ((OPENING_PATH.as_posix(), opening_methods), (LOADOUT_PATH.as_posix(), loadout_methods)):
        for method in methods:
            for call in method.get("calls", []):
                edges.append(_call_record(method, call, source_name))

    save_named = [
        edge for edge in edges
        if edge["target_class"] == "PlayerPrefs"
        and re.search(r"\bSave\s*\(", edge["target_signature"] or "")
    ]
    save_rva_edges = [edge for edge in edges if _rva(edge["target_rva"]) == PLAYERPREFS_SAVE_RVA]
    save_to_disk_edges = [
        edge for edge in edges
        if edge["target_class"] == "PlayerPreferences"
        and re.search(r"\bSaveToDisk\s*\(", edge["target_signature"] or "")
    ]
    expected_save_to_disk = {
        ("PlayerPreferences.DeleteAll", "0x13f1ab0"),
        ("PlayerPreferences.OnApplicationFocus", "0x13f1cd0"),
        ("PlayerPreferences.OnApplicationQuit", "0x13f1c84"),
    }
    observed_save_to_disk = {(edge["caller"], (edge["callsite"] or "").lower()) for edge in save_to_disk_edges}
    if observed_save_to_disk != expected_save_to_disk:
        raise ValueError(f"scoped SaveToDisk callers changed: {sorted(observed_save_to_disk)}")

    file_write_edges = [
        edge for edge in edges
        if edge["caller"] == "PlayerPreferences.SaveToDisk"
        and edge["target_class"] == "File"
        and "WriteAllBytes" in (edge["target_signature"] or "")
    ]
    if len(file_write_edges) != 1 or file_write_edges[0]["callsite"] != "0x13f1b3c":
        raise ValueError("expected one scoped File.WriteAllBytes call from PlayerPreferences.SaveToDisk")

    playerprefs_api_counts = Counter(
        edge["target_signature"] for edge in edges
        if edge["target_class"] == "PlayerPrefs"
    )
    signal_hits: list[dict[str, str]] = []
    for method in [*opening_methods, *loadout_methods]:
        id_ = _method_id(method)
        for call in method.get("calls", []):
            declaration = call.get("declaration") or {}
            text = f"{declaration.get('class_name', '')} {declaration.get('signature', '')}"
            if SAVE_MIGRATION_SIGNAL.search(text):
                signal_hits.append({"method": id_, "callsite": call.get("callsite"), "declaration": text.strip()})
        if SAVE_MIGRATION_SIGNAL.search(method.get("signature", "")) or SAVE_MIGRATION_SIGNAL.search(method.get("method", "")):
            signal_hits.append({"method": id_, "callsite": "method declaration", "declaration": method.get("signature", method.get("method", ""))})

    asm_matches: list[dict[str, Any]] = []
    asm_pins: list[dict[str, Any]] = []
    for record in raw_files:
        path = record["path"]
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            if DIRECT_BRANCH.search(line):
                asm_matches.append({"path": path, "line": line_no, "text": line.strip()})
        asm_pins.append({"path": path, "size": record["size"], "sha256": record["sha256"]})
    asm_pins.sort(key=lambda item: item["path"])
    inventory_blob = b"\n".join(
        f"{item['path']}\0{item['size']}\0{item['sha256']}".encode("utf-8")
        for item in asm_pins
    )
    asm_total_bytes = sum(item["size"] for item in asm_pins)
    if len(asm_pins) != 314 or asm_total_bytes != 7_823_314:
        raise ValueError(f"raw ASM corpus changed: {len(asm_pins)} files / {asm_total_bytes} bytes")
    asm_inventory_sha = sha256(inventory_blob)
    if asm_inventory_sha != EXPECTED_ASM_INVENTORY_SHA256:
        raise ValueError("pinned raw ASM inventory SHA-256 mismatch")

    dump_decompressed_sha = sha256(dump_text.encode("utf-8"))
    if dump_decompressed_sha != SOURCE_DUMP_DECOMPRESSED_SHA256:
        raise ValueError("decompressed dump.cs SHA-256 mismatch")
    playerprefs_save = _dump_save_declaration(dump_text)
    identity = loadout_index.get("inputs_sha256", {})
    xapk_sha = loadout_index.get("xapk_sha256")
    lib_sha = identity.get("lib/arm64-v8a/libil2cpp.so")
    metadata_sha = identity.get("assets/bin/Data/Managed/Metadata/global-metadata.dat")
    if not xapk_sha or not lib_sha or not metadata_sha:
        raise ValueError("source package/native/metadata identity missing from pinned recovery index")
    if opening_data.get("schema_version") != 1 or loadout_data.get("schema_version") != 1:
        raise ValueError("expected current contract-pack format version 1")

    return {
        "schema": "windwings.l2-save-durability-audit-25.v1",
        "status": "SCOPED_STATIC_SAVE_CALL_CENSUS_NOT_DURABILITY_PROOF",
        "task": {
            "board_item": "PR12 #25",
            "claim_comment": "6415333947",
            "scope": "Direct Unity PlayerPrefs.Save() call census across two pinned persistence receipts plus exact direct-branch search in all raw ASM files present in this checkout; scoped custom PlayerPreferences save callers and save-format/migration signal census.",
            "runtime_readback": "NOT_OBSERVED",
            "source_package_modified": False,
        },
        "source_identity": {
            "xapk_sha256": xapk_sha,
            "libil2cpp_so_sha256": lib_sha,
            "global_metadata_sha256": metadata_sha,
            "source_identity_authority": "raw/player-loadout/index.json; original package itself was not retrieved for this audit",
        },
        "unity_playerprefs_save_api": {
            **playerprefs_save,
            "declaration_source": DUMP_PATH.as_posix(),
            "dump_sha256_decompressed": dump_decompressed_sha,
            "body_in_dump": False,
            "interpretation": "Declaration/address pin only; no engine implementation or platform flush behavior inferred.",
        },
        "persistence_receipt_method_census": {
            "opening_contracts_method_records": len(opening_methods),
            "player_loadout_contract_method_records": len(loadout_methods),
            "distinct_method_records": len(method_map),
            "playerpreferences_bodies_in_opening_receipt": len(prefs_methods),
            "raw_playerpreferences_inventory_method_records": len(preferences_json["methods"]),
            "direct_playerprefs_save_named_call_count": len(save_named),
            "direct_playerprefs_save_rva_call_count": len(save_rva_edges),
            "direct_playerprefs_save_calls": save_named,
            "playerprefs_api_call_counts": dict(sorted(playerprefs_api_counts.items())),
            "custom_save_to_disk_call_count": len(save_to_disk_edges),
            "custom_save_to_disk_callers": sorted(save_to_disk_edges, key=lambda item: (item["caller"], item["callsite"] or "")),
            "custom_save_to_disk_file_write_count": len(file_write_edges),
            "custom_save_to_disk_file_writes": file_write_edges,
            "save_format_or_migration_signal_count": len(signal_hits),
            "save_format_or_migration_signal_hits": signal_hits,
            "contract_pack_schema_versions": {
                "datas/opening_persistence.json": opening_data["schema_version"],
                "datas/player_loadout_persistence.json": loadout_data["schema_version"],
            },
            "contract_pack_schema_note": "These schema_version values version the analysis JSON packs, not the game's save format.",
        },
        "raw_asm_direct_branch_scan": {
            "scope_root": "reverse-engineering/raw/",
            "file_pattern": "**/*.asm.txt",
            "file_count": len(asm_pins),
            "total_bytes": asm_total_bytes,
            "search_pattern": "BL/B direct branch destination 0x277cf6c (PlayerPrefs.Save RVA)",
            "direct_branch_match_count": len(asm_matches),
            "direct_branch_matches": asm_matches,
            "inventory_sha256": asm_inventory_sha,
            "file_pins": asm_pins,
            "boundary": "Only the exact direct BL/B target text in currently present ASM files is scanned; indirect calls, unexported methods, other builds, generated/native engine code, or missing ranges are outside scope.",
        },
        "evidence_boundary": [
            "Zero direct PlayerPrefs.Save references in these 74 method records and zero exact direct BL/B references across 314 current raw ASM files do not establish repository-wide absence.",
            "PlayerPreferences.OnApplicationFocus, OnApplicationQuit, and DeleteAll call the custom SaveToDisk path; this path's selected body writes an encoded custom dictionary file via File.WriteAllBytes.",
            "PlayerPrefs.SetInt/SetFloat/SetString wrappers tail-branch to Unity APIs; a setter call is not evidence of an explicit PlayerPrefs.Save invocation or durable flush.",
            "No platform flush guarantee, crash atomicity, transactional save, migration correctness, cloud synchronization, full global save schema, or runtime round-trip is established.",
            "The audit records no save-format/migration signal in the selected 74 method receipts; this is a scoped search, not proof no such mechanism exists elsewhere.",
        ],
        "source_pins": source_pins,
    }


def read_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str, dict[str, Any], dict[str, Any], dict[str, str], list[dict[str, Any]]]:
    source_pins: dict[str, str] = {}
    loaded: dict[str, Any] = {}
    for path in (OPENING_PATH, LOADOUT_PATH, LOADOUT_INDEX_PATH, PREFERENCES_JSON_PATH, OPENING_DATA_PATH, LOADOUT_DATA_PATH):
        data, payload = _load_pinned_json(path, PINS, compressed=path.suffix == ".gz")
        loaded[path.as_posix()] = data
        source_pins[path.as_posix()] = sha256(payload)
    preferences_asm = (ROOT / PREFERENCES_ASM_PATH).read_bytes()
    if sha256(preferences_asm) != PINS[PREFERENCES_ASM_PATH.as_posix()]:
        raise ValueError("pinned PlayerPreferences ASM SHA-256 mismatch")
    source_pins[PREFERENCES_ASM_PATH.as_posix()] = sha256(preferences_asm)
    dump_bytes = (ROOT / DUMP_PATH).read_bytes()
    if sha256(dump_bytes) != PINS[DUMP_PATH.as_posix()]:
        raise ValueError("pinned dump.cs.gz SHA-256 mismatch")
    dump_text = gzip.decompress(dump_bytes).decode("utf-8", errors="replace")
    source_pins[DUMP_PATH.as_posix()] = sha256(dump_bytes)
    source_pins["dump.cs.gz (decompressed)"] = sha256(dump_text.encode("utf-8"))

    paths = sorted((ROOT / "reverse-engineering/raw").rglob("*.asm.txt"))
    raw_files = []
    for path in paths:
        payload = path.read_bytes()
        raw_files.append({
            "path": path.relative_to(ROOT).as_posix(),
            "size": len(payload),
            "sha256": sha256(payload),
        })
    return (
        loaded[OPENING_PATH.as_posix()],
        loaded[LOADOUT_PATH.as_posix()],
        loaded[LOADOUT_INDEX_PATH.as_posix()],
        loaded[PREFERENCES_JSON_PATH.as_posix()],
        dump_text,
        loaded[OPENING_DATA_PATH.as_posix()],
        loaded[LOADOUT_DATA_PATH.as_posix()],
        source_pins,
        raw_files,
    )


def encode_receipt(receipt: dict[str, Any]) -> bytes:
    body = json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    return gzip.compress(body, compresslevel=9, mtime=0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / OUTPUT_PATH)
    parser.add_argument("--check", action="store_true", help="compare deterministic output without writing")
    args = parser.parse_args(argv)
    try:
        receipt = build_receipt(*read_inputs())
    except (OSError, KeyError, TypeError, ValueError, gzip.BadGzipFile, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    payload = encode_receipt(receipt)
    if args.check:
        try:
            current = args.output.read_bytes()
        except OSError as exc:
            print(f"FAIL: cannot read {args.output}: {exc}", file=sys.stderr)
            return 1
        if current != payload:
            print(f"FAIL: {args.output} differs from deterministic rebuild", file=sys.stderr)
            return 1
        print(f"PASS: {args.output.relative_to(ROOT)} is deterministic ({len(payload)} bytes)")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"Wrote {args.output.relative_to(ROOT)} ({len(payload)} bytes; {sha256(payload)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
