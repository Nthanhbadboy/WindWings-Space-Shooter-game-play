#!/usr/bin/env python3
"""Re-check a bounded native serializer field-name sequence from pinned raw bytes.

This consumes a retained peer-generated machine-code evidence artifact. It does
not load UnityPy, infer a complete TypeTree, or claim clean-room extraction.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "reverse-engineering/raw/l3-controller-schema-replication-17/controller112_probe.json.gz"
OUTPUT = ROOT / "datas/l3_controller_schema_replication_17.json.gz"
INPUT_SHA256 = "0b541954d0f96de0b3d0bb08d3dd6382de5b31a9efe97944a814b8e9da2ece51"
SOURCE_COMMIT = "72041a1d400be6b0972f5bfa9868efe3befaeca7"
XAPK_SHA256 = "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e"
LIBUNITY_SHA256 = "d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7"
LIBUNITY_SIZE = 17_783_496
FIELDS = ("m_InterruptionSource", "m_OrderedInterruption", "m_CanTransitionToSelf")
PATHS = {
    "native_path_A": {
        "entry": 0xB7FCB0,
        "helper": 0x5EB544,
        "sequence": ("m_InterruptionSource", "m_OrderedInterruption", "m_CanTransitionToSelf"),
    },
    "native_path_B": {
        "entry": 0xB851B8,
        "helper": 0x5EBF2C,
        "sequence": ("m_InterruptionSource", "m_OrderedInterruption", "m_CanTransitionToSelf"),
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sign_extend(value: int, bits: int) -> int:
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def decode_adrp(word: int, pc: int) -> tuple[int, int] | None:
    if word & 0x9F000000 != 0x90000000:
        return None
    immediate = sign_extend((((word >> 5) & 0x7FFFF) << 2) | ((word >> 29) & 3), 21) << 12
    return word & 31, (pc & ~0xFFF) + immediate


def decode_add_imm(word: int) -> tuple[int, int, int] | None:
    if word & 0xFFC00000 != 0x91000000:
        return None
    shift = 12 if (word >> 22) & 1 else 0
    return word & 31, (word >> 5) & 31, ((word >> 10) & 0xFFF) << shift


def decode_bl(word: int, pc: int) -> int | None:
    if word & 0xFC000000 != 0x94000000:
        return None
    return pc + (sign_extend(word & 0x03FFFFFF, 26) << 2)


def _word_at(window: dict, va: int) -> int:
    offset = va - window["va"]
    raw = bytes.fromhex(window["hex"])
    if offset < 0 or offset + 4 > len(raw) or offset % 4:
        raise ValueError(f"instruction address outside aligned raw window: {va:#x}")
    return struct.unpack_from("<I", raw, offset)[0]


def _find_window(windows: list[dict], va: int, through: int) -> dict:
    found = [w for w in windows if w["va"] <= va and va + through <= w["va"] + len(w["hex"]) // 2]
    if not found:
        raise ValueError(f"no retained native window spans {va:#x}..{va + through:#x}")
    return min(found, key=lambda w: len(w["hex"]))


def _literal_va(probe: dict, field: str) -> int:
    item = next((s for s in probe["strings"] if s["text"] == field), None)
    if item is None or not item["occurrences"]:
        raise ValueError(f"no retained literal occurrence for {field}")
    # Stable selection: the probe records source occurrences; all observed
    # xrefs below are required to target this same literal VA.
    return min(o["va"] for o in item["occurrences"])


def _field_transfer(probe: dict, field: str, ref_va: int, helper: int) -> dict:
    target = _literal_va(probe, field)
    window = _find_window(probe["windows"], ref_va, 0x80)
    first = _word_at(window, ref_va)
    adrp = decode_adrp(first, ref_va)
    if adrp is None or adrp[0] != 1:
        raise ValueError(f"expected ADRP x1 at {ref_va:#x}")

    # The literal-address ADD may be separated by up to two instructions. Only
    # allow recognized ADD-immediate instructions that write a register other
    # than x1 in that gap; this fails closed on unknown/clobbering instructions.
    add_va = None
    computed_target = None
    for step in range(1, 4):
        pc = ref_va + step * 4
        word = _word_at(window, pc)
        add = decode_add_imm(word)
        if add is not None and add[0] == 1 and add[1] == 1:
            add_va = pc
            computed_target = adrp[1] + add[2]
            break
        if add is None or add[0] == 1:
            raise ValueError(f"unreviewed instruction/clobber between ADRP and literal ADD at {pc:#x}")
    if add_va is None or computed_target != target:
        raise ValueError(f"literal xref mismatch for {field}: {computed_target!r} != {target:#x}")

    call_va = None
    call_target = None
    words = []
    for pc in range(add_va + 4, add_va + 4 + 0x40, 4):
        word = _word_at(window, pc)
        words.append({"va": pc, "word_hex": word.to_bytes(4, "little").hex()})
        branch = decode_bl(word, pc)
        if branch is not None:
            call_va, call_target = pc, branch
            break
        add = decode_add_imm(word)
        if add is not None and add[0] == 1:
            raise ValueError(f"x1 overwritten before helper call at {pc:#x}")
    if call_va is None or call_target != helper:
        raise ValueError(f"unexpected first BL after {field} at {ref_va:#x}: {call_target!r}")
    return {
        "field": field,
        "literal_va": target,
        "adrp_va": ref_va,
        "adrp_word_hex": first.to_bytes(4, "little").hex(),
        "literal_add_va": add_va,
        "literal_add_word_hex": _word_at(window, add_va).to_bytes(4, "little").hex(),
        "helper_call_va": call_va,
        "helper_target_va": call_target,
        "post_add_instructions_through_call": words,
    }


def build(source_gzip: bytes) -> dict:
    if sha256(source_gzip) != INPUT_SHA256:
        raise ValueError("pinned controller112 evidence SHA-256 mismatch")
    probe = json.loads(gzip.decompress(source_gzip))
    required = {
        "xapk_sha256": XAPK_SHA256,
        "libunity_sha256": LIBUNITY_SHA256,
        "libunity_size": LIBUNITY_SIZE,
        "provenance": "arena/ef6b75ef",
        "query_source": "109 shared builtin schema used ONLY to choose search strings, not evidence of APK schema",
    }
    for key, expected in required.items():
        if probe.get(key) != expected:
            raise ValueError(f"pinned source field mismatch: {key}")
    if len(FIELDS) != 3:
        raise AssertionError("unexpected bounded field slice")

    results = {}
    for path_name, path in PATHS.items():
        refs = []
        for field in path["sequence"]:
            refs.append(_field_transfer(probe, field, _path_ref(path_name, field), path["helper"]))
        if tuple(r["field"] for r in refs) != path["sequence"]:
            raise AssertionError("native field-name sequence changed")
        results[path_name] = {
            "helper_target_va": path["helper"],
            "field_sequence": refs,
        }

    return {
        "artifact": "l3_controller_schema_replication_17",
        "result": "PARTIAL_NATIVE_SERIALIZER_SEQUENCE_REPLICATION",
        "replication": True,
        "source": {
            "peer_branch": "arena/ef6b75ef-windwings-space-shooter-game-p",
            "peer_commit": SOURCE_COMMIT,
            "peer_artifact_path": "reverse-engineering/raw/controller112/probe.json.gz",
            "peer_artifact_sha256": INPUT_SHA256,
            "original_xapk_sha256_as_pinned_in_peer_artifact": XAPK_SHA256,
            "libunity_sha256_as_pinned_in_peer_artifact": LIBUNITY_SHA256,
            "libunity_size": LIBUNITY_SIZE,
            "peer_probe_tool_sha256": probe["tool_sha256"],
            "query_schema_sha256": probe["query_schema_sha256"],
            "query_selection_disclosure": probe["query_source"],
            "original_xapk_download_attempt": "gh release download failed with EOF at release-assets.githubusercontent.com; not locally verified",
        },
        "observations": results,
        "limits": [
            "This is a REPLICATION over retained peer-selected machine-code windows, not clean-room APK extraction; the original XAPK/libunity.so was not locally retrieved.",
            "The field names were seeded from the peer's shared UnityPy built-in schema search list; native literals/xrefs are corroborating evidence, not independent discovery of the owning serialized schema.",
            "Two code paths reference the same three literal names in sequence and call the pinned native helper addresses; helper semantics and path direction are not named or assumed here.",
            "No owning class/type-tree identity, complete field order/types, serialized offsets, runtime readback, or engine/render behavior is established.",
            "The peer artifact itself records candidate xrefs without full control-flow/clobber analysis; this builder re-decodes only the bounded retained instructions listed above.",
        ],
    }


def _path_ref(path_name: str, field: str) -> int:
    # Addresses are selected from the peer's retained raw code windows. They
    # mark the first ADRP of each literal-reference sequence; all bytes are
    # re-decoded and checked against the pinned literal address and helper.
    table = {
        "native_path_A": {
            "m_InterruptionSource": 0xB7FCB0,
            "m_OrderedInterruption": 0xB7FCEC,
            "m_CanTransitionToSelf": 0xB7FD24,
        },
        "native_path_B": {
            "m_InterruptionSource": 0xB851B8,
            "m_OrderedInterruption": 0xB85230,
            "m_CanTransitionToSelf": 0xB85290,
        },
    }
    return table[path_name][field]


def build_from_file(input_path: Path = INPUT, output_path: Path = OUTPUT, check: bool = False) -> bytes:
    source = input_path.read_bytes()
    value = build(source)
    data = gzip.compress(canonical_json(value), mtime=0)
    if check:
        if not output_path.exists() or output_path.read_bytes() != data:
            raise SystemExit("artifact differs; regenerate with this builder")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_from_file(check=args.check)
    print(f"artifact_bytes={len(data)} sha256={sha256(data)}")


if __name__ == "__main__":
    main()
