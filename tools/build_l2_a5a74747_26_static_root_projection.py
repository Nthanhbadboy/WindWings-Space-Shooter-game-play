#!/usr/bin/env python3
"""Build the bounded static-root / pixel-projection evidence for PR12 item #26.

This joins one resources.assets UI template to the explicitly inventoried initial
scene renderer/context captures. It intentionally does not infer an instance,
select a camera, or produce pixel bounds when those authorities are absent.
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
OUTPUT_PATH = Path("datas/l2_a5a74747_26_static_root_projection.json.gz")
BOARD_PATH = Path("reverse-engineering/raw/ui/Board_Pause__212696.json.gz")
POPUP_PATH = Path("reverse-engineering/raw/ui/Popup_Notices__57508.json.gz")
TRANSFORM_TREE_PATH = Path("reverse-engineering/raw/typetrees/transform-tree.tsv.gz")
SCENE_SPRITES_INDEX_PATH = Path("reverse-engineering/raw/scene-sprites/index.json")
SCENE_CONTEXT_INDEX_PATH = Path("reverse-engineering/raw/scene-context/index.json")
PRIOR_COMPOSITION_PATH = Path("datas/l3_composition_viewport_engine_transition_12.json.gz")
SPRITE_CONTRACT_PATH = Path("datas/scene_sprite_contract.json.gz")
CONTEXT_CONTRACT_PATH = Path("datas/scene_render_context_contract.json.gz")

# Exact byte pins for the selected templates, the prior composition result,
# current-contract inputs, the local transform tree, and the two raw-capture
# indexes. Per-shard decoded pins are authenticated by each pinned index.json.
PINNED_SHA256 = {
    "datas/scene_sprite_contract.json.gz": "6f46fe33303aac2adbe16cbd9889568fa7e0d9ce3439d75cef6c6bc404696095",
    "datas/scene_render_context_contract.json.gz": "312f71154e6c17469a37c2fc9063ea46c600d381bc7cd3a884a9842a4fe3b8f3",
    "datas/l3_composition_viewport_engine_transition_12.json.gz": "5fc9fd3673949948a9535ce119b8ac24334c428c96a054b1858346df92294f20",
    "reverse-engineering/raw/ui/Board_Pause__212696.json.gz": "160b13048ac3ed8e3554da5996b25ed4a4b2977c5bb2a4f2cdc538595fb877ac",
    "reverse-engineering/raw/ui/Popup_Notices__57508.json.gz": "b2a7ceb9ed49ab88e774ca2ea300fd29227c9afefed2ef9bf0cf56fa299aaf87",
    "reverse-engineering/raw/typetrees/transform-tree.tsv.gz": "30624c3e69a64559d0b790d48a6aa06db725edbcb9687e1457e72e7311c76ae2",
    "reverse-engineering/raw/l3-chain/objects-0353.jsonl.gz": "368ab3b174848927cd4ffb405b8745cef1da2fa13ece6a71a35a8fb520db393f",
    "reverse-engineering/raw/l3-chain/objects-0425.jsonl.gz": "fdfba84b9068e4cda7270707bc10069a499ee32af6c02051543375c8bc30a2fe",
    "reverse-engineering/raw/l3-chain/objects-0601.jsonl.gz": "4e51f0e55d179b26d0b7dacc37bc693a99d9991bbdb27e7971b044aa8b29e195",
    "reverse-engineering/raw/scene-sprites/index.json": "d9df999de1d0e53bf47e6329064d47ec3f14454f0432f1acc2d9a1195a736b65",
    "reverse-engineering/raw/scene-context/index.json": "1793e16a3bc385dd23759713568e9b6e6d548ad1bb90edb955d50327a6d5e998",
}
PEER_RAW_TIP = "33cdc61a912c006a6169583dfad444841033df7a"
PEER_RAW_BRANCH = "arena/ef6b75ef-windwings-space-shooter-game-p"
BOARD_ROOT_ID = 212696
POPUP_GO_ID = 57508
POPUP_TRANSFORM_ID = 425352
BOARD_TRANSFORM_ID = 439142
EXPECTED_SCENE_FILES = [
    "data.unity3d/level0",
    "data.unity3d/level1",
    "data.unity3d/level2",
    "data.unity3d/level3",
]
EXPECTED_SCENE_PATHS = [
    "Assets/GameAssets/Scenes/Menu.unity",
    "Assets/GameAssets/Scenes/Home.unity",
    "Assets/GameAssets/Scenes/Game.unity",
    "Assets/GameAssets/Scenes/EndGame.unity",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _read_bytes(path: str | Path, pins: dict[str, str] | None = None) -> bytes:
    rel = Path(path).as_posix()
    payload = (ROOT / rel).read_bytes()
    expected = (pins or {}).get(rel)
    if expected and sha256(payload) != expected:
        raise ValueError(f"pinned source SHA-256 mismatch: {rel}")
    return payload


def _load_json(path: str | Path, pins: dict[str, str] | None = None, compressed: bool = False) -> tuple[Any, bytes]:
    payload = _read_bytes(path, pins)
    data = gzip.decompress(payload) if compressed else payload
    return json.loads(data), payload


def _load_capture(kind: str, index_path: Path, source_pins: dict[str, str]) -> dict[str, Any]:
    index, index_bytes = _load_json(index_path, source_pins)
    raw_dir = index_path.parent
    objects: list[dict[str, Any]] = []
    chunk_pins: list[dict[str, Any]] = []
    for chunk in index.get("chunks", []):
        rel = (raw_dir / chunk["path"]).as_posix()
        payload = _read_bytes(rel)
        decoded = gzip.decompress(payload)
        if sha256(decoded) != chunk["sha256_decompressed"]:
            raise ValueError(f"decoded object shard pin mismatch: {rel}")
        lines = decoded.splitlines()
        if len(lines) != chunk["rows"]:
            raise ValueError(f"object shard row-count mismatch: {rel}")
        records = [json.loads(line) for line in lines]
        objects.extend(records)
        chunk_pins.append({
            "path": rel,
            "compressed_bytes": len(payload),
            "compressed_sha256": sha256(payload),
            "decoded_sha256": sha256(decoded),
            "rows": len(records),
        })
    links_rel = (raw_dir / "links.json.gz").as_posix()
    links_payload = _read_bytes(links_rel)
    links_decoded = gzip.decompress(links_payload)
    if sha256(links_decoded) != index.get("links_sha256_decompressed"):
        raise ValueError(f"decoded links pin mismatch: {links_rel}")
    links = json.loads(links_decoded)
    if not isinstance(links, list):
        raise ValueError(f"link source must be a JSON list: {links_rel}")
    return {
        "kind": kind,
        "index": index,
        "index_bytes": index_bytes,
        "objects": objects,
        "links": links,
        "chunk_pins": chunk_pins,
        "links_pin": {
            "path": links_rel,
            "compressed_bytes": len(links_payload),
            "compressed_sha256": sha256(links_payload),
            "decoded_sha256": sha256(links_decoded),
            "rows": len(links),
        },
    }


def _walk(value: Any, path: str = "$"):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            yield from _walk(child, f"{path}[{idx}]")


def _source_matches(objects: list[dict[str, Any]], links: list[dict[str, Any]]) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    direct_edges: list[dict[str, Any]] = []
    prefab_instances = 0
    for source_kind, records in (("object", objects), ("link", links)):
        for row_idx, record in enumerate(records):
            if source_kind == "object" and record.get("type") == "PrefabInstance":
                prefab_instances += 1
            for field_path, value in _walk(record):
                if value == BOARD_ROOT_ID and isinstance(value, int):
                    matches.append({"kind": source_kind, "row": row_idx, "field": field_path, "value": value})
                elif value == "Board_Pause":
                    matches.append({"kind": source_kind, "row": row_idx, "field": field_path, "value": value})
            if source_kind == "link":
                target = record.get("target") or {}
                pointer = record.get("pointer") or {}
                if (target.get("serialized_file") == "data.unity3d/resources.assets" and target.get("path_id") == BOARD_ROOT_ID) or pointer.get("m_PathID") == BOARD_ROOT_ID:
                    direct_edges.append({"row": row_idx, "owner": record.get("owner"), "target": target, "pointer": pointer})
    return {
        "exact_name_or_path_id_matches": matches,
        "direct_pointer_edges_to_board_pause_root": direct_edges,
        "captured_prefab_instance_typed_rows": prefab_instances,
    }


def _parse_transform_tree(payload: bytes) -> dict[int, dict[str, int]]:
    text = gzip.decompress(payload).decode("utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "path_id\tgameobject\tfather":
        raise ValueError("unexpected transform-tree header")
    out: dict[int, dict[str, int]] = {}
    for line in lines[1:]:
        fields = line.split("\t")
        if len(fields) != 3:
            raise ValueError("malformed transform-tree row")
        path_id, gameobject, father = map(int, fields)
        out[path_id] = {"gameobject": gameobject, "father": father}
    return out


def _jsonl_file(path: str | Path, expected_sha: str) -> list[dict[str, Any]]:
    payload = _read_bytes(path)
    if sha256(payload) != expected_sha:
        raise ValueError(f"pinned raw object shard SHA-256 mismatch: {path}")
    lines = gzip.decompress(payload).splitlines()
    return [json.loads(line) for line in lines]


def read_inputs() -> dict[str, Any]:
    pin_paths = dict(PINNED_SHA256)
    board, board_bytes = _load_json(BOARD_PATH, PINNED_SHA256, compressed=True)
    popup, popup_bytes = _load_json(POPUP_PATH, PINNED_SHA256, compressed=True)
    prior, prior_bytes = _load_json(PRIOR_COMPOSITION_PATH, PINNED_SHA256, compressed=True)
    sprite_contract, sprite_contract_bytes = _load_json(SPRITE_CONTRACT_PATH, PINNED_SHA256, compressed=True)
    context_contract, context_contract_bytes = _load_json(CONTEXT_CONTRACT_PATH, PINNED_SHA256, compressed=True)
    transform_bytes = _read_bytes(TRANSFORM_TREE_PATH, PINNED_SHA256)
    transform_rows = _parse_transform_tree(transform_bytes)

    scene_sprites = _load_capture("scene-sprites", SCENE_SPRITES_INDEX_PATH, PINNED_SHA256)
    scene_context = _load_capture("scene-context", SCENE_CONTEXT_INDEX_PATH, PINNED_SHA256)
    # These three raw object chunks are compact identity corroboration for the
    # popup transform, Animator, and Popup_Notices component, not scene proof.
    raw_0353 = _jsonl_file("reverse-engineering/raw/l3-chain/objects-0353.jsonl.gz", PINNED_SHA256["reverse-engineering/raw/l3-chain/objects-0353.jsonl.gz"])
    raw_0425 = _jsonl_file("reverse-engineering/raw/l3-chain/objects-0425.jsonl.gz", PINNED_SHA256["reverse-engineering/raw/l3-chain/objects-0425.jsonl.gz"])
    raw_0601 = _jsonl_file("reverse-engineering/raw/l3-chain/objects-0601.jsonl.gz", PINNED_SHA256["reverse-engineering/raw/l3-chain/objects-0601.jsonl.gz"])
    return {
        "board": board,
        "board_bytes": board_bytes,
        "popup": popup,
        "popup_bytes": popup_bytes,
        "prior": prior,
        "prior_bytes": prior_bytes,
        "sprite_contract": sprite_contract,
        "sprite_contract_bytes": sprite_contract_bytes,
        "context_contract": context_contract,
        "context_contract_bytes": context_contract_bytes,
        "transform_bytes": transform_bytes,
        "transform_rows": transform_rows,
        "scene_sprites": scene_sprites,
        "scene_context": scene_context,
        "raw_l3_objects": [raw_0353, raw_0425, raw_0601],
        "pin_paths": pin_paths,
    }


def build_receipt(inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    inputs = inputs or read_inputs()
    board = inputs["board"]
    popup = inputs["popup"]
    prior = inputs["prior"]
    sprite_contract = inputs["sprite_contract"]
    context_contract = inputs["context_contract"]
    transform_rows = inputs["transform_rows"]
    scene_sprites = inputs["scene_sprites"]
    scene_context = inputs["scene_context"]

    if board.get("class") != "Board_Pause" or board.get("root_path_id") != BOARD_ROOT_ID:
        raise ValueError("pinned Board_Pause template identity changed")
    if board.get("serialized_file") != "resources.assets" or len(board.get("nodes", [])) != 235:
        raise ValueError("expected the 235-node Board_Pause resources.assets template")
    board_nodes = board["nodes"]
    if board_nodes[0].get("name") != "Board_Pause" or board_nodes[0].get("active") != 0:
        raise ValueError("Board_Pause root name/activity changed")
    popup_node = next((row for row in board_nodes if row.get("path") == "Board_Pause/Popup_QuitMissions"), None)
    if popup_node is None or popup_node.get("active") != 0:
        raise ValueError("inactive Popup_QuitMissions node missing from Board_Pause template")
    if popup.get("class") != "Popup_Notices" or popup.get("root_path_id") != POPUP_GO_ID or popup.get("serialized_file") != "resources.assets":
        raise ValueError("Popup_Notices template identity changed")
    if len(popup.get("nodes", [])) != 19 or popup["nodes"][0].get("name") != "Popup_QuitMissions":
        raise ValueError("expected the 19-node Popup_QuitMissions template")
    if popup["nodes"][0].get("active") != 0 or popup["nodes"][0].get("local_pos") != [0.0, 0.0, -2.0]:
        raise ValueError("Popup_QuitMissions serialized root pose/activity changed")

    child_row = transform_rows.get(POPUP_TRANSFORM_ID)
    root_row = transform_rows.get(BOARD_TRANSFORM_ID)
    if child_row != {"gameobject": POPUP_GO_ID, "father": BOARD_TRANSFORM_ID}:
        raise ValueError("Popup_QuitMissions Transform→GO/parent edge changed")
    if root_row != {"gameobject": BOARD_ROOT_ID, "father": 0}:
        raise ValueError("Board_Pause template root Transform edge changed")
    if prior.get("focus", {}).get("board_pause_root", {}).get("path_id") != BOARD_ROOT_ID:
        raise ValueError("prior composition artifact does not identify the same Board_Pause root")
    if prior.get("focus", {}).get("gameobject", {}).get("path_id") != POPUP_GO_ID:
        raise ValueError("prior composition artifact does not identify the same popup GameObject")
    if prior.get("composition_viewport", {}).get("pixel_bounds") is not None:
        raise ValueError("prior composition result unexpectedly contains pixel bounds")

    transform_object = next((row for row in inputs["raw_l3_objects"][0] if row.get("path_id") == POPUP_TRANSFORM_ID), None)
    animator_object = next((row for row in inputs["raw_l3_objects"][1] if row.get("path_id") == 495980), None)
    popup_component = next((row for row in inputs["raw_l3_objects"][2] if row.get("path_id") == 644901), None)
    if not transform_object or transform_object.get("type") != "Transform":
        raise ValueError("pinned raw popup Transform record missing")
    transform_tree = transform_object.get("tree", {})
    if transform_tree.get("m_GameObject", {}).get("m_PathID") != POPUP_GO_ID or transform_tree.get("m_Father", {}).get("m_PathID") != BOARD_TRANSFORM_ID:
        raise ValueError("raw popup Transform PPtrs do not match the selected hierarchy")
    if transform_tree.get("m_LocalPosition") != {"x": 0.0, "y": 0.0, "z": -2.0}:
        raise ValueError("raw popup Transform local position changed")
    if not animator_object or animator_object.get("tree", {}).get("m_GameObject", {}).get("m_PathID") != POPUP_GO_ID:
        raise ValueError("pinned Animator does not attach to Popup_QuitMissions")
    if not popup_component or popup_component.get("class_name") != "Popup_Notices" or popup_component.get("tree", {}).get("m_GameObject", {}).get("m_PathID") != POPUP_GO_ID:
        raise ValueError("pinned Popup_Notices component does not attach to Popup_QuitMissions")

    if sprite_contract.get("scope", {}).get("root_files") != EXPECTED_SCENE_FILES:
        raise ValueError("scene sprite contract root_files changed")
    if sprite_contract.get("source_scene_paths") != EXPECTED_SCENE_PATHS:
        raise ValueError("BuildSettings scene path labels changed")
    if context_contract.get("scope", {}).get("root_files") != EXPECTED_SCENE_FILES:
        raise ValueError("scene context contract root_files changed")
    for capture in (scene_sprites, scene_context):
        if capture["index"].get("root_files") != EXPECTED_SCENE_FILES:
            raise ValueError(f"{capture['kind']} source root_files changed")
        if capture["index"].get("read_errors") or capture["index"].get("unresolved_links") or capture["index"].get("gameobject_transform_errors"):
            raise ValueError(f"{capture['kind']} pinned capture contains declared extraction errors")

    sprite_matches = _source_matches(scene_sprites["objects"], scene_sprites["links"])
    context_matches = _source_matches(scene_context["objects"], scene_context["links"])
    for label, matches in (("scene-sprites", sprite_matches), ("scene-context", context_matches)):
        if matches["exact_name_or_path_id_matches"] or matches["direct_pointer_edges_to_board_pause_root"]:
            raise ValueError(f"unexpected Board_Pause exact match in {label} capture")

    if len(scene_sprites["objects"]) != sum(scene_sprites["index"].get("object_counts", {}).values()):
        raise ValueError("scene-sprites object count does not match pinned index totals")
    if len(scene_sprites["objects"]) != 5698 or len(scene_sprites["links"]) != 10279:
        raise ValueError("scene-sprites bounded input record counts changed")
    if len(scene_context["objects"]) != 122 or len(scene_context["links"]) != 194:
        raise ValueError("scene-context bounded input record counts changed")
    if sum(scene_context["index"].get("object_counts", {}).values()) != len(scene_context["objects"]):
        raise ValueError("scene-context object count does not match pinned index totals")

    sprite_record_types = Counter(row.get("type") for row in scene_sprites["objects"])
    context_record_types = Counter(row.get("type") for row in scene_context["objects"])
    if sprite_record_types["PrefabInstance"] != 0:
        raise ValueError("captured scene-sprites subset unexpectedly contains PrefabInstance rows")

    cameras = []
    raw_cameras = {
        (row.get("serialized_file"), row.get("path_id")): row
        for row in scene_context["objects"] if row.get("type") == "Camera"
    }
    for camera in context_contract.get("cameras", []):
        identity = camera.get("identity", {})
        file_name = identity.get("serialized_file")
        if file_name not in EXPECTED_SCENE_FILES:
            continue
        raw = raw_cameras.get((file_name, identity.get("path_id")))
        if raw is None or raw.get("raw_object_sha256") != camera.get("raw_object_sha256"):
            raise ValueError("scene camera contract row does not join its pinned raw Camera object")
        tree = camera.get("tree", {})
        cameras.append({
            "serialized_file": file_name,
            "scene_path": EXPECTED_SCENE_PATHS[EXPECTED_SCENE_FILES.index(file_name)],
            "camera_path_id": identity.get("path_id"),
            "gameobject_path_id": camera.get("gameobject", {}).get("path_id"),
            "name": camera.get("name"),
            "orthographic": tree.get("orthographic"),
            "orthographic_size": tree.get("orthographic size"),
            "normalized_viewport_rect": tree.get("m_NormalizedViewPortRect"),
            "target_texture": tree.get("m_TargetTexture"),
            "transform_chain_path_ids_leaf_to_root": [
                row.get("identity", {}).get("path_id") for row in camera.get("transform_chain_leaf_to_root", [])
            ],
            "selected_for_board_pause_projection": False,
            "template_instance_link": None,
        })
    if len(cameras) != 5:
        raise ValueError(f"expected five serialized cameras in level0..level3, got {len(cameras)}")

    buildsettings = next((row for row in scene_sprites["objects"] if row.get("type") == "BuildSettings"), None)
    if not buildsettings or buildsettings.get("tree", {}).get("scenes") != EXPECTED_SCENE_PATHS:
        raise ValueError("pinned BuildSettings scene list does not match the contract labels")

    all_sources: list[dict[str, Any]] = []
    for path, expected in sorted(PINNED_SHA256.items()):
        payload = _read_bytes(path)
        if sha256(payload) != expected:
            raise ValueError(f"pinned source changed during receipt construction: {path}")
        all_sources.append({"path": path, "bytes": len(payload), "sha256": sha256(payload)})
    for capture in (scene_sprites, scene_context):
        all_sources.append({
            "path": capture["links_pin"]["path"],
            "bytes": capture["links_pin"]["compressed_bytes"],
            "sha256": capture["links_pin"]["compressed_sha256"],
        })
        all_sources.extend({
            "path": pin["path"],
            "bytes": pin["compressed_bytes"],
            "sha256": pin["compressed_sha256"],
        } for pin in capture["chunk_pins"])
    all_sources = sorted(all_sources, key=lambda row: row["path"])
    manifest_bytes = b"\n".join(
        f"{row['path']}\0{row['bytes']}\0{row['sha256']}".encode("utf-8") for row in all_sources
    )

    return {
        "schema": "windwings.l2-static-root-projection-26.v1",
        "status": "BOUNDED_STATIC_EVIDENCE_NO_SCENE_INSTANCE_PIXEL_BOUNDS_NULL",
        "task": {
            "board_item": "PR12 #26",
            "claim_comment": "6415498086",
            "scope": "Join the exact Board_Pause resources.assets root and Popup_QuitMissions local transform chain against the explicitly inventoried level0..level3 scene renderer/context captures and their camera rows.",
            "runtime_readback": "NOT_OBSERVED",
            "rendered": False,
            "source_package_modified": False,
        },
        "template_root": {
            "name": "Board_Pause",
            "class": board.get("class"),
            "serialized_file": "data.unity3d/resources.assets",
            "path_id": BOARD_ROOT_ID,
            "root_transform_path_id": BOARD_TRANSFORM_ID,
            "serialized_active": bool(board_nodes[0].get("active")),
            "local_position": board_nodes[0].get("local_pos"),
            "node_count": len(board_nodes),
            "root_kind": prior.get("focus", {}).get("root_kind"),
            "source_asset_external_paths": [row.get("path") for row in board.get("externals", [])],
            "interpretation": "Serialized resource/template root; not, by itself, evidence of a level-scene instance or runtime activation.",
        },
        "popup_template": {
            "name": "Popup_QuitMissions",
            "class": popup.get("class"),
            "serialized_file": "data.unity3d/resources.assets",
            "gameobject_path_id": POPUP_GO_ID,
            "transform_path_id": POPUP_TRANSFORM_ID,
            "parent_transform_path_id": BOARD_TRANSFORM_ID,
            "serialized_active": bool(popup["nodes"][0].get("active")),
            "local_position": popup["nodes"][0].get("local_pos"),
            "node_count": len(popup["nodes"]),
            "board_pause_hierarchy_path": popup_node.get("path"),
            "pointers": {
                "transform_m_GameObject": POPUP_GO_ID,
                "transform_m_Father": BOARD_TRANSFORM_ID,
                "parent_transform_m_GameObject": BOARD_ROOT_ID,
                "parent_transform_m_Father": 0,
            },
            "corroborating_raw_objects": [
                {"type": "Transform", "path_id": POPUP_TRANSFORM_ID, "raw_chunk": "objects-0353.jsonl.gz"},
                {"type": "Animator", "path_id": 495980, "raw_chunk": "objects-0425.jsonl.gz"},
                {"type": "MonoBehaviour/Popup_Notices", "path_id": 644901, "raw_chunk": "objects-0601.jsonl.gz"},
            ],
            "interpretation": "Template-local serialized hierarchy/pose only; no runtime instance, active state, or engine readback is implied.",
        },
        "inventoried_scene_scope": {
            "root_files": EXPECTED_SCENE_FILES,
            "source_scene_paths": EXPECTED_SCENE_PATHS,
            "scene_sprites": {
                "capture_status": scene_sprites["index"].get("status"),
                "object_records": len(scene_sprites["objects"]),
                "link_records": len(scene_sprites["links"]),
                "object_type_counts": dict(sorted(sprite_record_types.items())),
                "renderer_counts_all_serialized_files": scene_sprites["index"].get("renderer_counts_all_serialized_files"),
                "exact_name_or_path_id_matches": len(sprite_matches["exact_name_or_path_id_matches"]),
                "direct_pointer_edges_to_board_pause_root": len(sprite_matches["direct_pointer_edges_to_board_pause_root"]),
                "captured_prefab_instance_typed_rows": sprite_matches["captured_prefab_instance_typed_rows"],
                "capture_limits": scene_sprites["index"].get("limits"),
                "scope_note": "All 1377 initial level0..level3 SpriteRenderer roots plus their recorded parent/linked-object closure are represented; this is not a complete all-class scene or PrefabInstance census.",
            },
            "scene_context": {
                "capture_status": scene_context["index"].get("status"),
                "object_records": len(scene_context["objects"]),
                "link_records": len(scene_context["links"]),
                "object_type_counts": dict(sorted(context_record_types.items())),
                "exact_name_or_path_id_matches": len(context_matches["exact_name_or_path_id_matches"]),
                "direct_pointer_edges_to_board_pause_root": len(context_matches["direct_pointer_edges_to_board_pause_root"]),
                "camera_records_level0_through_level3": len(cameras),
                "capture_limits": scene_context["index"].get("limits"),
                "scope_note": "Serialized camera and mask context only; no dynamic camera writer, active-stack arbitration, or Board_Pause instance binding is supplied.",
            },
            "scoped_reference_result": "No Board_Pause name or path ID 212696 match and no direct PPtr edge to data.unity3d/resources.assets:212696 occurs in these inventoried renderer/context object-and-link records.",
            "absence_boundary": "This is only a non-observation in the explicitly pinned scene-sprites and scene-context captures; it is not proof of absence from all scene object classes, all bundles, runtime-spawned instances, or the repository.",
        },
        "camera_inventory": cameras,
        "projection": {
            "status": "NOT_PROJECTED_NO_SCENE_INSTANCE_CAMERA_BINDING",
            "pixel_bounds": None,
            "rendered": False,
            "why": [
                "Board_Pause is a resources.assets template root; the inspected sources do not bind it to a particular level0..level3 scene instance or placement override.",
                "The five serialized cameras belong to separate level0..level3 contexts; none is linked to this template in the inspected inputs, so selecting one would guess.",
                "The normalized viewport rectangles are serialized camera fields, not a template-to-camera join or a pixel-resolution/render-target authority.",
                "The scene captures are scoped renderer/context closures rather than a complete all-class scene/PrefabInstance census; no broader not-in-bundle claim is made.",
            ],
            "prior_report_112_status": prior.get("composition_viewport", {}).get("status"),
            "prior_report_112_pixel_bounds": prior.get("composition_viewport", {}).get("pixel_bounds"),
        },
        "source_provenance": {
            "raw_scene_capture_snapshot": {
                "branch": PEER_RAW_BRANCH,
                "commit": PEER_RAW_TIP,
                "note": "The selected raw UI/template, scene-sprites, scene-context and l3-chain source files were read from this pinned peer snapshot and copied byte-for-byte into this branch for the bounded reproduction.",
            },
            "transform_tree_source": {
                "path": TRANSFORM_TREE_PATH.as_posix(),
                "sha256": sha256(inputs["transform_bytes"]),
                "note": "Current-branch local source. It independently confirms Transform 425352→GO 57508 / parent 439142, then Transform 439142→GO 212696 / root.",
            },
            "source_capture_package_metadata": scene_sprites["index"].get("inputs"),
            "package_metadata_authority": "Inherited from pinned capture index; the original package was not independently retrieved or decoded during this #26 audit.",
            "prior_composition_artifact": {
                "path": PRIOR_COMPOSITION_PATH.as_posix(),
                "sha256": sha256(inputs["prior_bytes"]),
                "report": "docs/apk-analysis/112-L3-composition-viewport-engine-transition-arena-a5a74747-windwings-space-shooter-game-p.md",
            },
        },
        "input_pins": all_sources,
        "input_manifest_sha256": sha256(manifest_bytes),
        "evidence_boundary": [
            "Static serialized evidence only; no screenshot, redraw, device/session, runtime readback, or render was used.",
            "The not-observed result is restricted to the listed scene-sprites and scene-context captures and their decoded pins; it is not repository-wide or all-bundle absence proof.",
            "Template-local serialized transforms do not establish prefab instantiation, runtime parentage, active camera selection, screen-pixel resolution, native layout overrides, or rendered visibility.",
            "Camera candidates are inventories only; no camera was guessed or selected for Board_Pause.",
            "No runtime/render approval, pixel bounds, global scene closure, or protected-file change is claimed.",
        ],
    }


def encode_receipt(receipt: dict[str, Any]) -> bytes:
    payload = canonical_json(receipt)
    return gzip.compress(payload, compresslevel=9, mtime=0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail unless the checked-in artifact matches a deterministic rebuild")
    args = parser.parse_args(argv)
    try:
        encoded = encode_receipt(build_receipt())
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, gzip.BadGzipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    target = ROOT / OUTPUT_PATH
    if args.check:
        if not target.exists() or target.read_bytes() != encoded:
            print(f"FAIL: {OUTPUT_PATH.as_posix()} differs from deterministic rebuild", file=sys.stderr)
            return 1
        print(f"PASS: deterministic #26 artifact matches {OUTPUT_PATH.as_posix()}")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(encoded)
    print(f"WROTE: {OUTPUT_PATH.as_posix()} ({len(encoded)} bytes, sha256={sha256(encoded)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
