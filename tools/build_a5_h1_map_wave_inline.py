#!/usr/bin/env python3
"""Extract Map_Get_Datas.listMapDatas from the captured managed ARM64 listing.

The output is a static table receipt. It does not run the game or claim runtime
map/wave selection parity. InitializeArray payload bytes are taken from the
repo's pinned, decoded managed-method inventory and matched to exact allocation
and callsite PCs in Map_Get_Datas.asm.txt.
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
ASM = Path("reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt")
INVENTORY = Path("reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.json")
IA_RESOLVED = Path("reverse-engineering/il2cpp/ia-resolved.json")
DUMP = Path("reverse-engineering/il2cpp/dump.cs.gz")
PRIOR_MAPS = Path("datas/maps.json")
LEGACY_CANDIDATE = Path("datas/map_waves_candidate.json")
OUT = Path("datas/l3_a5_h1_map_wave_inline.json")

EXPECTED_SHA256 = {
    ASM.as_posix(): "a95539643a1d0a17e546c5fde41cf1a12a7230f934cc12a30807bcdf644edae6",
    INVENTORY.as_posix(): "1b588f39932d2ffee3de214c76fa927fa58e6d4fddf70a8426dba95de7c5b249",
    IA_RESOLVED.as_posix(): "2583a4c472400fe85f96b96f0a8d2839963eddae95760483424119501d989e37",
    PRIOR_MAPS.as_posix(): "93f8670dd3960d3f3792f56b5abaf7bf95f91dbd46c7c953c170b5a9165d44f9",
    LEGACY_CANDIDATE.as_posix(): "4c0fe9e87ad554c7d9ada0b13dde44189453f753b2082411c1c087b33ca1756b",
}
EXPECTED_DUMP_GZIP_SHA256 = "e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454"
EXPECTED_DUMP_TEXT_SHA256 = "8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c"
EXPECTED_ROWS = 250
FIRST_NEWARR_PC = 0x1406C08
FIELD_STORE_PC = 0x140E19C
EXPECTED_FIRST_ROWS = [[25, 9010], [164], [113, 5]]

INSTRUCTION = re.compile(r"\s*(0x[0-9a-f]+):\s+(\S+)\s*(.*?)\s*$", re.I)
IMM_MOV = re.compile(r"(w\d+),\s*#(0x[0-9a-f]+|\d+)\s*$", re.I)
ARRAY_STORE = re.compile(r"(w\d+|wzr),\s*\[x1,\s*#(0x[0-9a-f]+|\d+)\]\s*$", re.I)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def read_pinned(path: Path) -> bytes:
    data = (ROOT / path).read_bytes()
    expected = EXPECTED_SHA256.get(path.as_posix())
    actual = sha256(data)
    if expected and actual != expected:
        raise ValueError(f"source pin mismatch for {path}: {actual} != {expected}")
    return data


def parse_instructions(asm: str) -> list[dict[str, Any]]:
    result = []
    for line in asm.splitlines():
        match = INSTRUCTION.fullmatch(line)
        if match:
            result.append({
                "pc": int(match.group(1), 16),
                "mnemonic": match.group(2).lower(),
                "operands": match.group(3).strip(),
                "source": line,
            })
    return result


def find_immediate_length(instructions: list[dict[str, Any]], index: int) -> int:
    candidates = instructions[max(0, index - 8):index]
    for ins in reversed(candidates):
        if ins["mnemonic"] == "mov":
            match = IMM_MOV.fullmatch(ins["operands"])
            if match and match.group(1).lower() == "w1":
                return int(match.group(2), 0)
    raise ValueError(f"no immediate array length before newarr at {instructions[index]['source']}")


def literal_values(instructions: list[dict[str, Any]], start: int, end: int, length: int) -> list[dict[str, Any]]:
    registers: dict[str, int] = {}
    values: dict[int, dict[str, Any]] = {}
    for ins in instructions[start + 1:end]:
        if ins["mnemonic"] == "mov":
            match = IMM_MOV.fullmatch(ins["operands"])
            if match:
                registers[match.group(1).lower()] = int(match.group(2), 0)
                continue
        if ins["mnemonic"] != "str":
            continue
        match = ARRAY_STORE.fullmatch(ins["operands"])
        if not match:
            continue
        reg, off_text = match.groups()
        offset = int(off_text, 0)
        if offset < 0x20 or (offset - 0x20) % 4:
            continue
        element = (offset - 0x20) // 4
        if element >= length:
            continue
        reg = reg.lower()
        if reg == "wzr":
            value = 0
        elif reg in registers:
            value = registers[reg]
        else:
            raise ValueError(f"literal store at {ins['source']} has no immediate definition")
        values[element] = {"index": element, "value": value, "pc": f"0x{ins['pc']:x}", "instruction": ins["source"].strip()}
    if set(values) != set(range(length)):
        raise ValueError(f"literal array initialized at {len(values)}/{length} elements")
    return [values[i] for i in range(length)]


def _static_field_offset(dump_text: str) -> int:
    match = re.search(
        r"public class Map_Get_Datas\s*:\s*MonoBehaviour.*?\n\s*// Fields\n(?P<fields>.*?)(?=\n\s*// Methods)",
        dump_text,
        re.S,
    )
    if not match:
        raise ValueError("Map_Get_Datas field block missing from pinned dump")
    field = re.search(r"private static List<int\[\]> listMapDatas;\s*//\s*(0x[0-9a-f]+)", match.group("fields"))
    if not field:
        raise ValueError("listMapDatas static field missing from pinned dump")
    return int(field.group(1), 16)


def build() -> dict[str, Any]:
    asm_bytes = read_pinned(ASM)
    inventory_bytes = read_pinned(INVENTORY)
    ia_bytes = read_pinned(IA_RESOLVED)
    maps_bytes = read_pinned(PRIOR_MAPS)
    candidate_bytes = read_pinned(LEGACY_CANDIDATE)
    dump_compressed = (ROOT / DUMP).read_bytes()
    dump_text_bytes = gzip.decompress(dump_compressed)
    if sha256(dump_compressed) != EXPECTED_DUMP_GZIP_SHA256 or sha256(dump_text_bytes) != EXPECTED_DUMP_TEXT_SHA256:
        raise ValueError("dump.cs.gz source pin mismatch")
    dump_text = dump_text_bytes.decode("utf-8")

    inventory = json.loads(inventory_bytes)
    cctor = next((m for m in inventory["methods"] if m.get("method") == "cctor"), None)
    if not cctor or cctor.get("size_capped") is not False or cctor.get("ends_clean") is not True or cctor.get("bytes") != 100896:
        raise ValueError("Map_Get_Datas cctor inventory does not match the uncapped clean 100,896-byte method")
    field_offset = _static_field_offset(dump_text)

    instructions = parse_instructions(asm_bytes.decode("utf-8"))
    by_pc = {ins["pc"]: i for i, ins in enumerate(instructions)}
    if FIRST_NEWARR_PC not in by_pc or FIELD_STORE_PC not in by_pc:
        raise ValueError("expected listMapDatas construction anchors are missing")
    store = instructions[by_pc[FIELD_STORE_PC]]
    if store["mnemonic"] != "str" or store["operands"] != "x28, [x8, #0x28]" or field_offset != 0x28:
        raise ValueError("listMapDatas static field store/metadata offset does not agree")

    allocation_indices = [
        i for i, ins in enumerate(instructions)
        if FIRST_NEWARR_PC <= ins["pc"] < FIELD_STORE_PC
        and ins["mnemonic"] == "bl" and ins["operands"].lower() == "#0x110d09c"
    ]
    if len(allocation_indices) != EXPECTED_ROWS or instructions[allocation_indices[0]]["pc"] != FIRST_NEWARR_PC:
        raise ValueError(f"expected 250 ordered map-table array allocations; found {len(allocation_indices)}")
    end_index = by_pc[FIELD_STORE_PC]

    ia_root = json.loads(ia_bytes)["methods"].get("Map_Get_Datas.cctor")
    if not isinstance(ia_root, list):
        raise ValueError("Map_Get_Datas.cctor IA inventory missing")
    ia_by_allocation = {int(row["array_new_addr"], 16): row for row in ia_root}
    prior_maps = json.loads(maps_bytes).get("maps")
    if not isinstance(prior_maps, list) or len(prior_maps) != EXPECTED_ROWS:
        raise ValueError("pinned datas/maps.json does not have exactly 250 entries")
    legacy_maps = json.loads(candidate_bytes).get("maps")
    if not isinstance(legacy_maps, list) or len(legacy_maps) != EXPECTED_ROWS:
        raise ValueError("pinned legacy candidate does not have exactly 250 entries")

    rows = []
    for ordinal, index in enumerate(allocation_indices):
        ins = instructions[index]
        allocation_pc = ins["pc"]
        next_index = allocation_indices[ordinal + 1] if ordinal + 1 < len(allocation_indices) else end_index
        length = find_immediate_length(instructions, index)
        ia_row = ia_by_allocation.get(allocation_pc)
        if ia_row:
            init_pc = int(ia_row["addr"], 16)
            init_index = by_pc.get(init_pc)
            if init_index is None or init_index <= index or init_index >= next_index:
                raise ValueError(f"InitializeArray callsite is outside allocation {ordinal}'s block")
            init_ins = instructions[init_index]
            if init_ins["mnemonic"] != "bl" or init_ins["operands"].lower() != "#0x205b07c":
                raise ValueError(f"unexpected InitializeArray call at {init_ins['source']}")
            values = ia_row.get("ints")
            raw = bytes.fromhex(ia_row.get("raw", ""))
            if not isinstance(values, list) or len(values) != length or not ia_row.get("length_valid"):
                raise ValueError(f"invalid decoded payload for listMapDatas index {ordinal}")
            if len(raw) < 4 * length or list(struct.unpack("<" + "i" * length, raw[:4 * length])) != values:
                raise ValueError(f"raw payload bytes do not decode to listed int values at index {ordinal}")
            row = {
                "table_index": ordinal,
                "values": values,
                "source_kind": "RuntimeHelpers.InitializeArray payload",
                "array_new_pc": f"0x{allocation_pc:x}",
                "array_length": length,
                "initialize_array_pc": f"0x{init_pc:x}",
                "private_implementation_field": ia_row["field"],
                "payload_hex": ia_row["raw"],
            }
        else:
            stores = literal_values(instructions, index, next_index, length)
            values = [item["value"] for item in stores]
            row = {
                "table_index": ordinal,
                "values": values,
                "source_kind": "immediate element stores in cctor",
                "array_new_pc": f"0x{allocation_pc:x}",
                "array_length": length,
                "literal_stores": stores,
            }
        old = prior_maps[ordinal]
        if not isinstance(old, list) or old != values:
            raise ValueError(f"pinned prior maps.json disagrees with source extraction at index {ordinal}")
        rows.append(row)

    if [row["values"] for row in rows[:3]] != EXPECTED_FIRST_ROWS:
        raise ValueError("the three previously resolved map/wave entries do not match")
    ia_count = sum(row["source_kind"].startswith("RuntimeHelpers") for row in rows)
    if ia_count != 243 or len(rows) - ia_count != 7:
        raise ValueError(f"unexpected source split: {ia_count} InitializeArray / {len(rows)-ia_count} literals")
    legacy_mismatches = []
    for i, (row, old) in enumerate(zip(rows, legacy_maps)):
        old_values = old.get("values") if isinstance(old, dict) else None
        if old_values != row["values"]:
            legacy_mismatches.append({"table_index": i, "extracted": row["values"], "legacy_candidate": old_values})

    return {
        "schema": "windwings.a5-h1-map-wave-static-table.v1",
        "status": "STATIC_ONLY_EXTRACTED_LISTMAPDATAS_NOT_RUNTIME_PARITY",
        "table": "Map_Get_Datas.listMapDatas",
        "table_field_static_offset": "0x28",
        "indexing": "zero-based cctor List<int[]> insertion order; not display/UI numbering",
        "method": {
            "name": "Map_Get_Datas..cctor",
            "start_pc": "0x13feec8",
            "bytes": cctor["bytes"],
            "size_capped": cctor["size_capped"],
            "ends_clean": cctor["ends_clean"],
            "first_array_new_pc": f"0x{FIRST_NEWARR_PC:x}",
            "final_static_field_store_pc": f"0x{FIELD_STORE_PC:x}",
            "array_count": len(rows),
            "initialize_array_count": ia_count,
            "literal_array_count": len(rows) - ia_count,
        },
        "crosscheck": {
            "previously_resolved_entries": [
                {"table_index": i, "expected": EXPECTED_FIRST_ROWS[i], "extracted": rows[i]["values"], "match": True}
                for i in range(3)
            ],
            "prior_local_maps_artifact": {
                "path": PRIOR_MAPS.as_posix(),
                "entries_matched": len(rows),
                "mismatches": 0,
            },
            "superseded_legacy_candidate": {
                "path": LEGACY_CANDIDATE.as_posix(),
                "entries_compared": len(rows),
                "mismatches": len(legacy_mismatches),
                "first_mismatches": legacy_mismatches[:5],
                "meaning": "old candidate is not authoritative for full row ordering/payloads; preserved unchanged",
            },
        },
        "source_pins": {
            ASM.as_posix(): sha256(asm_bytes),
            INVENTORY.as_posix(): sha256(inventory_bytes),
            IA_RESOLVED.as_posix(): sha256(ia_bytes),
            DUMP.as_posix(): {
                "compressed_sha256": sha256(dump_compressed),
                "decompressed_sha256": sha256(dump_text_bytes),
            },
            PRIOR_MAPS.as_posix(): sha256(maps_bytes),
            LEGACY_CANDIDATE.as_posix(): sha256(candidate_bytes),
        },
        "limitations": [
            "Static constructor payload extraction only; does not establish runtime or Unity readback/parity.",
            "The source split is 243 decoded InitializeArray payloads plus seven immediate-initialized int arrays.",
            "Table indices are the List<int[]> insertion order, not a claim about displayed map numbering.",
            "Values do not resolve any downstream gameplay meaning beyond the statically named map/wave data table.",
        ],
        "entries": rows,
    }


def main() -> int:
    out = build()
    path = ROOT / OUT
    path.write_bytes(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n")
    print(f"{OUT}: {len(out['entries'])} entries; 3 known-entry checks; 243 InitializeArray + 7 immediate; sha256 {sha256(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
