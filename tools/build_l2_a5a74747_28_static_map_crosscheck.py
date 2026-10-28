#!/usr/bin/env python3
"""Build the bounded, static-only fallback receipt for PR12 item #28.

This compares the latest #21 peer constructor-binding receipt with this branch's
prior Map table extractions. It does not run a game, start a session, or claim
runtime /statics readback.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PEER_PATH = Path(
    "reverse-engineering/raw/l2-a5a74747-28-static-crosscheck/"
    "peer-l2_ef6b75ef108_map_entry_bindings.json.gz"
)
PEER_REPORT_PATH = Path(
    "reverse-engineering/raw/l2-a5a74747-28-static-crosscheck/"
    "peer-report-108-ef6b75ef.md"
)
MAPS_PATH = Path("datas/maps.json")
SEGMENTS_PATH = Path("datas/map_segments_full.json")
OUTPUT_PATH = Path("datas/l2_a5a74747_28_loader_fallback1.json.gz")
PEER_BRANCH = "arena/ef6b75ef-windwings-space-shooter-game-p"
PEER_COMMIT = "706c704e6024b831097a2b53a1d5332e588e30b6"
EXPECTED_PEER_ARTIFACT_SHA256 = "ccf8309e0503dd504d651abb4c6df658fb68a4836f91b2711d236797905f09cd"
EXPECTED_PEER_REPORT_SHA256 = "a1100c0502f33717e03ed36c4396d3ed7410dcf9ab80e3c92f0447a4f7ff1424"
EXPECTED_MAPS_SHA256 = "93f8670dd3960d3f3792f56b5abaf7bf95f91dbd46c7c953c170b5a9165d44f9"
EXPECTED_SEGMENTS_SHA256 = "1b6fe5a776419b1846e0ced64499f62e1408f9780edb46d84336410260298250"
SOURCE_XAPK_SHA256 = "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e"
SOURCE_LIB_SHA256 = "9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99"
SCHEMA = "windwings.l2-map-static-crosscheck-28.v1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _integer_list(values: Any, where: str) -> list[int]:
    if not isinstance(values, list) or any(type(value) is not int for value in values):
        raise ValueError(f"{where}: expected a list of integers")
    return values


def build_receipt(
    peer: dict[str, Any],
    local_maps: dict[str, Any],
    local_segments: dict[str, Any],
    input_hashes: dict[str, str],
) -> dict[str, Any]:
    if peer.get("schema") != "windwings.map-entry108.v1":
        raise ValueError("unexpected #21 peer artifact schema")
    if peer.get("provenance") != "arena/ef6b75ef":
        raise ValueError("peer provenance is not arena/ef6b75ef")
    if peer.get("input_apk_sha256") != SOURCE_XAPK_SHA256:
        raise ValueError("peer input APK/XAPK SHA-256 does not match the pinned source package")
    if peer.get("input_lib_sha256") != SOURCE_LIB_SHA256:
        raise ValueError("peer input native-library SHA-256 does not match the pin")
    if len(peer.get("bindings", [])) != 576:
        raise ValueError("peer artifact must contain all 576 InitializeArray bindings")

    root = peer.get("constructor_roots", {}).get("listMapDatas")
    if not isinstance(root, dict) or root.get("allocation") is None:
        raise ValueError("peer artifact has no listMapDatas constructor root")
    peer_items = root.get("items")
    if not isinstance(peer_items, list) or len(peer_items) != 250:
        raise ValueError("peer listMapDatas root must have 250 ordered entries")

    candidate_maps = local_maps.get("maps")
    if not isinstance(candidate_maps, list) or len(candidate_maps) != 250:
        raise ValueError("local datas/maps.json must contain 250 maps")

    matching_segments = [
        segment for segment in local_segments.get("segments", [])
        if segment.get("index") == 35
    ]
    if len(matching_segments) != 1:
        raise ValueError("expected exactly one local candidate segment 35")
    segment_rows = matching_segments[0].get("arrays")
    if not isinstance(segment_rows, list) or len(segment_rows) != 250:
        raise ValueError("local candidate segment 35 must contain 250 arrays")

    ia_bindings: dict[int, dict[str, Any]] = {}
    for binding in peer["bindings"]:
        if binding.get("root") != "listMapDatas":
            continue
        path = binding.get("index_path")
        if not isinstance(path, list) or len(path) != 1 or type(path[0]) is not int:
            raise ValueError("listMapDatas binding has an unexpected index path")
        index = path[0]
        if index in ia_bindings:
            raise ValueError(f"duplicate InitializeArray binding at map index {index}")
        ia_bindings[index] = binding

    literal_leaves: dict[int, dict[str, Any]] = {}
    for leaf in peer.get("non_InitializeArray_leaves", []):
        if leaf.get("root") != "listMapDatas":
            continue
        path = leaf.get("index_path")
        if not isinstance(path, list) or len(path) != 1 or type(path[0]) is not int:
            raise ValueError("listMapDatas literal has an unexpected index path")
        index = path[0]
        if index in literal_leaves:
            raise ValueError(f"duplicate inline literal at map index {index}")
        literal_leaves[index] = leaf

    if len(ia_bindings) != 243 or len(literal_leaves) != 7:
        raise ValueError(
            f"expected 243 InitializeArray rows and 7 inline literals; got "
            f"{len(ia_bindings)} and {len(literal_leaves)}"
        )
    if set(ia_bindings) & set(literal_leaves):
        raise ValueError("an index is both InitializeArray-backed and inline")
    if set(ia_bindings) | set(literal_leaves) != set(range(250)):
        raise ValueError("peer rows do not cover each listMapDatas index exactly once")

    rows: list[dict[str, Any]] = []
    value_lengths: Counter[int] = Counter()
    total_values = 0
    for index, peer_item in enumerate(peer_items):
        peer_values = _integer_list(peer_item.get("values"), f"peer item {index}")
        map_values = _integer_list(candidate_maps[index], f"datas/maps.json[{index}]")
        segment_row = segment_rows[index]
        segment_values = _integer_list(segment_row.get("values"), f"segment35[{index}]")
        if peer_item.get("length") != len(peer_values):
            raise ValueError(f"peer length field mismatch at index {index}")
        if segment_row.get("len") != len(segment_values):
            raise ValueError(f"local segment length field mismatch at index {index}")
        if peer_values != map_values:
            raise ValueError(f"prior datas/maps.json values differ at index {index}")
        if peer_values != segment_values:
            raise ValueError(f"local segment 35 values differ at index {index}")

        if index in ia_bindings:
            source = "InitializeArray"
            binding = ia_bindings[index]
            initializer = binding.get("initializer")
            if not isinstance(initializer, dict):
                raise ValueError(f"missing peer initializer identity at index {index}")
            if binding.get("values") != peer_values:
                raise ValueError(f"peer InitializeArray values differ at index {index}")
            if binding.get("array_new_site", "").lower() != segment_row.get("addr", "").lower():
                raise ValueError(f"peer/local allocation site differs at index {index}")
            if initializer.get("field") != segment_row.get("field"):
                raise ValueError(f"peer/local initializer field differs at index {index}")
            if initializer.get("pc", "").lower() != segment_row.get("initialize_array_addr", "").lower():
                raise ValueError(f"peer/local InitializeArray call site differs at index {index}")
            if peer_item.get("initializer") != initializer:
                raise ValueError(f"peer root and binding initializer differ at index {index}")
            initializer_field = initializer["field"]
            initialize_array_pc = initializer["pc"]
        else:
            source = "inline-immediate"
            leaf = literal_leaves[index]
            if leaf.get("values") != peer_values or leaf.get("length") != len(peer_values):
                raise ValueError(f"peer inline-literal values differ at index {index}")
            if leaf.get("array_new_site", "").lower() != segment_row.get("addr", "").lower():
                raise ValueError(f"peer/local inline allocation site differs at index {index}")
            if peer_item.get("initializer") is not None or segment_row.get("source") != "immediates":
                raise ValueError(f"unexpected initializer on inline literal at index {index}")
            initializer_field = None
            initialize_array_pc = None

        if peer_item.get("kind") != "array" or peer_item.get("element_type") != "int[]_TypeInfo":
            raise ValueError(f"unexpected static array shape at index {index}")
        value_lengths[len(peer_values)] += 1
        total_values += len(peer_values)
        rows.append({
            "index": index,
            "values": peer_values,
            "length": len(peer_values),
            "values_sha256_canonical_json": sha256(canonical_json(peer_values)),
            "source": source,
            "array_new_site": segment_row["addr"],
            "peer_allocation": peer_item["allocation"],
            "initializer_field": initializer_field,
            "initialize_array_pc": initialize_array_pc,
            "matches_previous_maps_json": True,
            "matches_previous_segment35": True,
        })

    peer_constructor_count = len(peer_items)
    local_candidate_count = len(candidate_maps)
    local_segment_count = len(segment_rows)
    if total_values != 742:
        raise ValueError(f"unexpected total static integer count: {total_values}")

    return {
        "schema": SCHEMA,
        "status": "STATIC_CROSSCHECK_NOT_RUNTIME",
        "task": {
            "board_item": "PR12 #28",
            "path": "approved-loader path checked; board fallback ① used",
            "requested_runtime_parameters": {"arr": 256, "depth": 2},
            "runtime_readback": "NOT_OBSERVED",
            "session_started": False,
            "source_apk_modified": False,
            "explicit_boundary": (
                "Every map value below is static constructor evidence from the #21 peer "
                "receipt, cross-checked against prior local static candidate artifacts. "
                "No runtime /statics request or live readback is represented."
            ),
        },
        "provenance": {
            "replication": True,
            "peer_branch": PEER_BRANCH,
            "peer_commit": PEER_COMMIT,
            "peer_artifact_path": PEER_PATH.as_posix(),
            "peer_artifact_sha256": input_hashes[PEER_PATH.as_posix()],
            "peer_artifact_uncompressed_sha256": input_hashes["peer_artifact_uncompressed"],
            "peer_artifact_schema": peer["schema"],
            "peer_artifact_scope": peer["scope"],
            "source_xapk_sha256": peer["input_apk_sha256"],
            "source_lib_sha256": peer["input_lib_sha256"],
            "peer_report_path": PEER_REPORT_PATH.as_posix(),
            "peer_report_sha256": input_hashes[PEER_REPORT_PATH.as_posix()],
            "local_sources": {
                MAPS_PATH.as_posix(): input_hashes[MAPS_PATH.as_posix()],
                SEGMENTS_PATH.as_posix(): input_hashes[SEGMENTS_PATH.as_posix()],
            },
            "source_map_field": "Map_Get_Datas.listMapDatas",
            "static_field_offset": "0x28",
            "map_index_interpretation": "zero-based constructor order; UI numbering not verified",
        },
        "crosscheck": {
            "peer_constructor_entries": peer_constructor_count,
            "local_maps_json_entries": local_candidate_count,
            "local_segment35_entries": local_segment_count,
            "peer_initialize_array_rows": len(ia_bindings),
            "peer_inline_literal_rows": len(literal_leaves),
            "value_rows_compared": len(rows),
            "value_mismatch_count": 0,
            "allocation_site_mismatch_count": 0,
            "initializer_field_or_pc_mismatch_count": 0,
            "total_integer_values": total_values,
            "length_distribution": {
                str(length): value_lengths[length] for length in sorted(value_lengths)
            },
            "all_rows_match": True,
            "comparison_rows": rows,
            "anchors": {
                "first": {"index": 0, "values": rows[0]["values"]},
                "second": {"index": 1, "values": rows[1]["values"]},
                "last": {"index": 249, "values": rows[-1]["values"]},
            },
            "consumer_route_context": peer["consumer_campaign_route"],
        },
    }


def read_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    peer_bytes = (ROOT / PEER_PATH).read_bytes()
    hashes = {
        PEER_PATH.as_posix(): sha256(peer_bytes),
        "peer_artifact_uncompressed": sha256(gzip.decompress(peer_bytes)),
    }
    if hashes[PEER_PATH.as_posix()] != EXPECTED_PEER_ARTIFACT_SHA256:
        raise ValueError("pinned peer artifact SHA-256 mismatch")
    peer_report_bytes = (ROOT / PEER_REPORT_PATH).read_bytes()
    hashes[PEER_REPORT_PATH.as_posix()] = sha256(peer_report_bytes)
    if hashes[PEER_REPORT_PATH.as_posix()] != EXPECTED_PEER_REPORT_SHA256:
        raise ValueError("pinned peer report 108 SHA-256 mismatch")
    maps_bytes = (ROOT / MAPS_PATH).read_bytes()
    segments_bytes = (ROOT / SEGMENTS_PATH).read_bytes()
    hashes[MAPS_PATH.as_posix()] = sha256(maps_bytes)
    hashes[SEGMENTS_PATH.as_posix()] = sha256(segments_bytes)
    if hashes[MAPS_PATH.as_posix()] != EXPECTED_MAPS_SHA256:
        raise ValueError("pinned local maps.json SHA-256 mismatch")
    if hashes[SEGMENTS_PATH.as_posix()] != EXPECTED_SEGMENTS_SHA256:
        raise ValueError("pinned local map_segments_full.json SHA-256 mismatch")
    peer = json.loads(gzip.decompress(peer_bytes))
    local_maps = json.loads(maps_bytes)
    local_segments = json.loads(segments_bytes)
    return peer, local_maps, local_segments, hashes


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
