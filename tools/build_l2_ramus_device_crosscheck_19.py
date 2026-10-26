#!/usr/bin/env python3
"""Build the evidence-bounded #19 Ramus/map/device crosscheck artifact.

Joins the checked-in 2026-10-23 single-phone Ramus receipt with static APK
1.3.118 tables. It resolves the 12-capture vs 10-list-entry classification from
the source .cctor, but deliberately does not claim map-content parity: the old
phone response contains nested-array type names, not values, and no refreshed
arr=256/depth=2 device receipt is present.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "datas/l2_ramus_device_crosscheck_19.json.gz"
BRANCH = "arena/a5a74747-windwings-space-shooter-game-p"
PHONE = "docs/apk-analysis/ramus/2026-10-23-phone"

INPUTS = [
    "datas/maps.json",
    "datas/device_table.json",
    "docs/apk-analysis/31-map-tables.md",
    "docs/apk-analysis/01-apk-inventory.md",
    f"{PHONE}/CROSSCHECK-static-vs-runtime.md",
    f"{PHONE}/SUMMARY_vi.md",
    f"{PHONE}/health_game.json",
    f"{PHONE}/boss_state.json",
    f"{PHONE}/statics_Map_Get_Datas.json",
    f"{PHONE}/statics_Device_Get_Data.json",
    "reverse-engineering/raw/il2cpp-consts/Device_Get_Data.asm.txt",
    "reverse-engineering/raw/il2cpp-consts/Device_Get_Data.json",
    "reverse-engineering/il2cpp/dump.cs.gz",
    "runtime-probe/RamusBridge.cs",
    "runtime-probe/collect.sh",
]

# Checked remote snapshots searched for independent raw phone/runtime evidence.
# Their pinned files are not copied into this artifact; this is a scope-limited
# audit log, not a repository-wide proof of absence.
REMOTE_AUDIT = [
    {
        "ref": "origin/arena/ef6b75ef-windwings-space-shooter-game-p",
        "commit": "d7e718cfb5466fd7bd03e2d8357400d744b108cb",
        "checked_paths": [
            "reverse-engineering/raw/cross-build-phone/provenance.json",
            "reverse-engineering/raw/cross-build-phone/CROSSCHECK-static-vs-runtime.md",
            "reverse-engineering/raw/cross-build-phone/SUMMARY_vi.md",
            "reverse-engineering/raw/runtime-probe/40181812673/artifact/reports/runtime-probe/report.md",
        ],
        "result": "same Mate 20 X 1.0.69 receipt; runtime-probe run 40181812673 reports no bridge in 1.3.118 source XAPK; no second independent device receipt found in these checked paths",
        "remote_sha256": {
            "reverse-engineering/raw/cross-build-phone/provenance.json": "c14f39e09d4b03e33891c5d386e74651d7cf335a6e0cd84271d41df3bdbfda2e",
            "reverse-engineering/raw/cross-build-phone/CROSSCHECK-static-vs-runtime.md": "455e2b264700d6459792f287db920ee71416573b8b3687203848bc329ec6a452",
            "reverse-engineering/raw/cross-build-phone/SUMMARY_vi.md": "da2b74be5c89c80abbb29844a1de63ed114dd4313203b09dda5e1167f1b3051e",
            "reverse-engineering/raw/runtime-probe/40181812673/artifact/reports/runtime-probe/report.md": "bcd40336d98d96a3a811e870149e99f5571e6ab1c39c386203ef6b06de6e50cd",
        },
    },
    {
        "ref": "origin/arena/20330d0e-windwings-space-shooter-game-p",
        "commit": "bab67115f5192d5fa0e17c07920aa63f109a5afa",
        "checked_paths": [
            f"docs/apk-analysis/ramus/2026-10-23-phone/statics_Map_Get_Datas.json",
            f"docs/apk-analysis/ramus/2026-10-23-phone/statics_Device_Get_Data.json",
            "reverse-engineering/raw/runtime-probe/40181812673/ci-run.json",
        ],
        "result": "same archived phone capture and same no-bridge probe receipt; not an independent device readback",
    },
    {
        "ref": "origin/a2033",
        "commit": "aa07737cea934cd2a53b28e199a5c14bdc9a059a",
        "checked_paths": [
            f"docs/apk-analysis/ramus/2026-10-23-phone/statics_Map_Get_Datas.json",
            f"docs/apk-analysis/ramus/2026-10-23-phone/statics_Device_Get_Data.json",
        ],
        "result": "same archived phone capture; no independent device readback found in checked paths",
    },
    {
        "ref": "origin/aef6b",
        "commit": "9f90c1acbf5123038c9cfa31771490adde3d2226",
        "checked_paths": [
            "reverse-engineering/raw/cross-build-phone/provenance.json",
            "reverse-engineering/raw/cross-build-phone/CROSSCHECK-static-vs-runtime.md",
            "reverse-engineering/raw/cross-build-phone/SUMMARY_vi.md",
        ],
        "result": "same archived Mate 20 X capture; no second independent device readback found in checked paths",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def read_json(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_bytes(path: str) -> bytes:
    return (ROOT / path).read_bytes()


def read_dump_class() -> str:
    import gzip as _gzip

    text = _gzip.decompress(read_bytes("reverse-engineering/il2cpp/dump.cs.gz")).decode(
        "utf-8", errors="replace"
    )
    start = text.index("public class Device_Get_Data : MonoBehaviour")
    end = text.find("\n// Namespace:", start)
    if end < 0:
        raise AssertionError("Device_Get_Data type block has no following namespace boundary")
    return text[start:end]


def build_artifact() -> dict[str, Any]:
    if not asm_bridge or not collect_script:
        set_script_sources()
    maps = read_json("datas/maps.json")
    device_table = read_json("datas/device_table.json")
    map_runtime = read_json(f"{PHONE}/statics_Map_Get_Datas.json")
    device_runtime = read_json(f"{PHONE}/statics_Device_Get_Data.json")
    phone_state = read_json(f"{PHONE}/boss_state.json")
    phone_health = read_json(f"{PHONE}/health_game.json")

    map_values = maps["maps"]
    runtime_map_fields = map_runtime["fields"]
    runtime_map = runtime_map_fields["listMapDatas"]
    map_count = runtime_map_fields["listMapDatas_count"]
    runtime_map_placeholders = [v for v in runtime_map if isinstance(v, str)]
    runtime_map_types = sorted(set(runtime_map_placeholders))

    device_arrays = device_table["arrays"]
    runtime_device_fields = device_runtime["fields"]
    runtime_device_list = runtime_device_fields["listStatValues"]
    runtime_device_count = runtime_device_fields["listStatValues_count"]

    asm = read_bytes("reverse-engineering/raw/il2cpp-consts/Device_Get_Data.asm.txt").decode(
        "utf-8", errors="replace"
    )
    cctor_marker = ";;; cctor  private static void .cctor() { }"
    cctor = asm.split(cctor_marker, 1)[1].split("\n;;; ", 1)[0]
    dump_class = read_dump_class()

    # Dump.cs field offsets + the cctor's ten list insertions and two direct
    # field stores classify the 12 captures without calling all of them devices.
    field_offsets: dict[str, str] = {}
    for field in ("listStatValues", "percentByLevels1", "percentByLevels2"):
        match = re.search(rf"\b{field};\s*//\s*(0x[0-9a-fA-F]+)", dump_class)
        if not match:
            raise AssertionError(f"Device_Get_Data field offset missing: {field}")
        field_offsets[field] = match.group(1).lower()

    init_calls = re.findall(r"^\s*(0x[0-9a-f]+): bl\s+#0x205b07c\s*$", cctor, re.M)
    list_element_stores = re.findall(r"^\s*(0x[0-9a-f]+): str\s+x20, \[x8, #0x20\]\s*$", cctor, re.M)
    list_slot_store = re.search(r"^\s*(0x[0-9a-f]+): str\s+x19, \[x8\]\s*$", cctor, re.M)
    percent1_store = re.search(r"^\s*(0x[0-9a-f]+): str\s+x19, \[x8, #8\]\s*$", cctor, re.M)
    percent2_store = re.search(r"^\s*(0x[0-9a-f]+): str\s+x19, \[x8, #0x10\]\s*$", cctor, re.M)
    if len(device_arrays) != 12 or len(init_calls) != 12 or len(list_element_stores) != 10:
        raise AssertionError("unexpected Device_Get_Data .cctor InitializeArray/List structure")
    if not (list_slot_store and percent1_store and percent2_store):
        raise AssertionError("could not find list/percent static-field stores in Device_Get_Data .cctor")
    if len(map_values) != 250 or map_count != 250:
        raise AssertionError("map static/runtime reported length changed from 250")
    if len(runtime_map) != 128 or len(runtime_map_placeholders) != 128:
        raise AssertionError("archived runtime map response no longer matches the documented 128 placeholders")
    if runtime_device_count != 10 or len(runtime_device_list) != 10:
        raise AssertionError("archived runtime listStatValues response no longer reports ten entries")
    if any(not isinstance(v, str) for v in runtime_device_list):
        raise AssertionError("archived runtime listStatValues entries are no longer all placeholders")

    # Convert observed runtime decimal JSON values to their actual IEEE-754
    # float32 representation before comparing against InitializeArray data.
    runtime_percent_match: dict[str, bool] = {}
    percent_rows = []
    for index, name, offset in (
        (10, "percentByLevels1", field_offsets["percentByLevels1"]),
        (11, "percentByLevels2", field_offsets["percentByLevels2"]),
    ):
        static_values = device_arrays[index]["stats"]
        runtime_values = runtime_device_fields[name]
        exact_f32 = [f32(x) for x in runtime_values] == static_values
        runtime_percent_match[name] = exact_f32
        if not exact_f32 or len(static_values) != 5 or device_arrays[index]["len"] != 5:
            raise AssertionError(f"static capture {index} does not match runtime {name} at float32 precision")
        percent_rows.append(
            {
                "capture_index": index,
                "assigned_field": name,
                "field_offset": offset,
                "static_values": static_values,
                "runtime_values_as_reported": runtime_values,
                "runtime_values_rounded_to_float32": [f32(x) for x in runtime_values],
                "bitwise_float32_match": True,
            }
        )

    input_pins = [
        {"path": path, "sha256": sha256(read_bytes(path)), "bytes": len(read_bytes(path))}
        for path in INPUTS
    ]
    builder_path = Path(__file__).resolve()
    builder_sha = sha256(builder_path.read_bytes())
    bridge_supports_arr_depth = (
        "Q(req, \"arr\", 128)" in asm_bridge
        and "Q(req, \"depth\", 2)" in asm_bridge
        and "&arr=256&depth=2" in collect_script
    )

    return {
        "schema": "arena.ramus-device-crosscheck.v1",
        "claim": "PR12 item #19 — Ramus device crosscheck: Map nested arrays and Device 12-capture vs 10-list discrepancy",
        "branch": BRANCH,
        "status": "PARTIAL_MAP_CONTENTS_NOT_MEASURED_DEVICE_GROUPING_RESOLVED",
        "evidence_policy": {
            "measured_from_artifacts_only": True,
            "model_is_not_runtime_readback": True,
            "runtime_readback_is_not_render": True,
            "screenshots_used_as_gate": False,
            "same_build_parity_claimed": False,
            "second_device_parity_claimed": False,
        },
        "apk_provenance": {
            "static_source": {
                "package": "com.Wind.wings.Space.Shooter",
                "version": "1.3.118",
                "version_code": 312,
                "base_apk_sha256": "6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1",
                "source_xapk_sha256": "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e",
            },
            "runtime_source": {
                "package": "com.Gcenter.WindWings.SpaceShooter.Premium",
                "reported_version": "mod 1.0.69 repackaged",
                "device_model": phone_state["device"],
                "os": phone_state["os"],
                "unity": phone_health.get("unity"),
                "capture_scope": "one archived Mate 20 X session; the runtime receipt is distinct from the official 1.3.118 APK",
            },
        },
        "map_nested_array_crosscheck": {
            "runtime_receipt": {
                "class": map_runtime["type"],
                "field": "listMapDatas",
                "reported_count": map_count,
                "returned_outer_items": len(runtime_map),
                "returned_placeholder_items": len(runtime_map_placeholders),
                "placeholder_types": runtime_map_types,
                "nested_integer_values_read": False,
                "arr_depth_request": {
                    "arr": 256,
                    "depth": 2,
                    "supported_by_current_bridge_and_collector": bridge_supports_arr_depth,
                    "applied_to_archived_phone_receipt": False,
                },
                "content_verdict": "NOT_CROSSCHECKED_ARCHIVED_RECEIPT_HAS_TYPE_PLACEHOLDERS_ONLY",
            },
            "static_source_apk_decoded_values": {
                "dataset": "datas/maps.json",
                "source_note": maps.get("source"),
                "entry_count": len(map_values),
                "values": map_values,
                "runtime_parity": "NOT_ESTABLISHED_DIFFERENT_PACKAGE_BUILD_AND_NO_RUNTIME_NESTED_VALUES",
            },
            "count_comparison": {
                "static_entries": len(map_values),
                "runtime_reported_count": map_count,
                "outer_length_equal": len(map_values) == map_count,
                "content_equal": None,
            },
        },
        "device_list_crosscheck": {
            "runtime_receipt": {
                "class": device_runtime["type"],
                "field": "listStatValues",
                "reported_count": runtime_device_count,
                "returned_items": len(runtime_device_list),
                "all_items_are_type_placeholders": True,
                "row_float_values_read": False,
            },
            "static_source_apk_cctor": {
                "initialize_array_captures": len(device_arrays),
                "captures_appended_to_listStatValues": len(list_element_stores),
                "captures_assigned_to_other_fields": 2,
                "field_offsets_from_dump_cs": field_offsets,
                "list_reference_store_instruction": list_slot_store.group(1),
                "percent_by_level_stores": {
                    "percentByLevels1": percent1_store.group(1),
                    "percentByLevels2": percent2_store.group(1),
                },
                "list_entries": [
                    {
                        "capture_index": i,
                        "array_new_addr": device_arrays[i]["array_new_addr"],
                        "length": device_arrays[i]["len"],
                        "values": device_arrays[i]["stats"],
                    }
                    for i in range(10)
                ],
                "separate_percent_fields": percent_rows,
            },
            "discrepancy_verdict": {
                "old_total_capture_count": 12,
                "actual_static_list_entries": 10,
                "archived_runtime_list_entries": runtime_device_count,
                "resolution": "12_TOTAL_INITIALIZEARRAY_CAPTURES_EQUAL_10_LIST_ENTRIES_PLUS_2_PERCENT_FIELDS",
                "static_runtime_list_length": "MATCH_10_ACROSS_DIFFERENT_BUILDS_ONLY",
                "inner_device_values_parity": "NOT_ESTABLISHED_RUNTIME_ROWS_ARE_PLACEHOLDERS",
                "percent_arrays_crossbuild_f32_match": runtime_percent_match,
                "not_a_proven_device_count": True,
            },
        },
        "searched_raw_branches": REMOTE_AUDIT,
        "next_measurement": {
            "required": "refresh a provenance-bound runtime capture with the bridge active, then compare Map_Get_Datas.listMapDatas values using arr=256 and depth=2; retain package/version/device receipt",
            "current_collector_has_query": bridge_supports_arr_depth,
            "available_capture_has_query_receipt": False,
            "screenshots_required": False,
        },
        "source_pins": {
            "builder_sha256": builder_sha,
            "files": input_pins,
        },
    }


# The bridge check is separated from the main builder below to keep all inputs
# explicit while still pinning the exact collector semantics.
asm_bridge = ""
collect_script = ""


def set_script_sources() -> None:
    global asm_bridge, collect_script
    asm_bridge = (ROOT / "runtime-probe/RamusBridge.cs").read_text(encoding="utf-8")
    collect_script = (ROOT / "runtime-probe/collect.sh").read_text(encoding="utf-8")


def main() -> int:
    set_script_sources()
    artifact = build_artifact()
    raw = json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT.open("wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as gz:
            gz.write(raw)
    print(f"wrote {ARTIFACT.relative_to(ROOT)} ({ARTIFACT.stat().st_size} bytes) sha256={sha256(ARTIFACT.read_bytes())}")
    return 0


if __name__ == "__main__":
    set_script_sources()
    raise SystemExit(main())
