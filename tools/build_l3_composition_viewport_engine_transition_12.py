#!/usr/bin/env python3
"""Build the bounded #12 composition/viewport + Animator transition artifact.

This joins checked-in decoded L3 artifacts for the serialized Board_Pause asset.
It deliberately does not claim scene placement, Unity execution, a runtime readback,
or rendered pixels.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "datas/l3_composition_viewport_engine_transition_12.json.gz"
BRANCH = "arena/a5a74747-windwings-space-shooter-game-p"
FOCUS_GO = 57508
FOCUS_TRANSFORM = 425352
ROOT_GO = 212696
PRIOR_BLOCK_GO = 96185
PRIOR_BLOCK_TRANSFORM = 277770
ANIMATOR_ID = 495980
CONTROLLER_ID = 1974
APPEAR_CLIP_ID = 1572
HIDE_CLIP_ID = 1573

# Independent raw-source pins from the already-pushed AI-1 data branch.
# The source excerpt is retained in the JSON; the raw files are not copied or edited.
PEER_REF = "origin/arena/ef6b75ef-windwings-space-shooter-game-p"
PEER_COMMIT = "d7e718cfb5466fd7bd03e2d8357400d744b108cb"
PEER_RAW_PINS = {
    "reverse-engineering/raw/typetrees/transform-tree.tsv.gz": "92b2eef703c71593833f32e390256a5a318e4121749d523eec2fefcaf4f0aac6",
    "reverse-engineering/raw/ui/Board_Pause__212696.json.gz": "160b13048ac3ed8e3554da5996b25ed4a4b2977c5bb2a4f2cdc538595fb877ac",
    "reverse-engineering/raw/ui/Popup_Notices__57508.json.gz": "b2a7ceb9ed49ab88e774ca2ea300fd29227c9afefed2ef9bf0cf56fa299aaf87",
    "reverse-engineering/raw/l3-chain/objects-0353.jsonl.gz": "368ab3b174848927cd4ffb405b8745cef1da2fa13ece6a71a35a8fb520db393f",
    "reverse-engineering/raw/l3-chain/objects-0425.jsonl.gz": "fdfba84b9068e4cda7270707bc10069a499ee32af6c02051543375c8bc30a2fe",
    "reverse-engineering/raw/l3-chain/objects-0601.jsonl.gz": "4e51f0e55d179b26d0b7dacc37bc693a99d9991bbdb27e7971b044aa8b29e195",
    "reverse-engineering/raw/l3-ui-native/native/Popup_Notices.json": "ef706d5b9aaf71364204152fd5322ece348947c9d499ee5e9dfee33149479c95",
    "reverse-engineering/raw/l3-ui-native/method-bytes.json.gz": "e25b39d8293b2d2c45b90d39b697b1c57b5a876f82c0820330a9be65d0dde8ed",
}

LOCAL_INPUTS = [
    "datas/l3_scene_chains.json.gz",
    "datas/l3-scene-chains/nodes-005.json.gz",
    "datas/l3-scene-chains/nodes-007.json.gz",
    "datas/l3-scene-chains/motion-000.json.gz",
    "datas/l3-scene-chains/animation_bindings-006.json.gz",
    "datas/l3_animator_programs.json.gz",
    "datas/l3_transition_model.json.gz",
    "datas/l3_composition.json.gz",
    "datas/l3_frame_cases.json.gz",
    "datas/l3_driven_props.json.gz",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_gzip_json(path: str) -> Any:
    with gzip.open(ROOT / path, "rt", encoding="utf-8") as f:
        return json.load(f)


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _pointer_path_id(obj: dict[str, Any] | None) -> int | None:
    if not isinstance(obj, dict):
        return None
    return obj.get("m_PathID", obj.get("path_id"))


def _clip_sample(clip: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate three declared serialized-curve probes, not Unity playback."""
    streams = clip["streamed"]
    records = [r for r in streams if isinstance(r.get("time"), (int, float))]

    def exact_record(t: float) -> dict[str, Any]:
        found = [r for r in records if r["time"] == t]
        if len(found) != 1:
            raise AssertionError(f"expected one stream record at {t}, got {len(found)}")
        return found[0]

    def indexed(record: dict[str, Any]) -> dict[int, dict[str, Any]]:
        return {k["index"]: k for k in record["keys"]}

    # The scale curve's 0.05s record stores the cubic for the segment sampled at 0.25s.
    scale_segment = indexed(exact_record(0.05000000074505806))
    delta = 0.25 - 0.05000000074505806
    scale_025 = []
    for channel in (0, 1):
        a, b, c, d = scale_segment[channel]["coeff"]
        scale_025.append(f32(a * delta**3 + b * delta**2 + c * delta + d))
    scale_025.append(1.0)

    start = indexed(exact_record(0.0))
    mid = indexed(exact_record(0.25))
    end = indexed(exact_record(0.5))
    # The alpha curve has its last serialized key at 0.25s. The t=0.5 value below
    # is a hold-last serialized-curve model policy, not an engine readback.
    alpha_start = start[3]["value"]
    alpha_mid = mid[3]["value"]

    return [
        {
            "time_seconds": 0.0,
            "local_scale": [f32(start[i]["value"]) for i in (0, 1, 2)],
            "sprite_alpha": f32(alpha_start),
            "sample_basis": "exact_stream_record",
        },
        {
            "time_seconds": 0.25,
            "local_scale": scale_025,
            "sprite_alpha": f32(alpha_mid),
            "sample_basis": "cubic_segment_from_0.05s_plus_exact_alpha_key",
            "cubic_delta_seconds": delta,
        },
        {
            "time_seconds": 0.5,
            "local_scale": [f32(end[i]["value"]) for i in (0, 1, 2)],
            "sprite_alpha": f32(alpha_mid),
            "sample_basis": "exact_scale_record_plus_hold_last_alpha_model",
        },
    ]


def build_artifact() -> dict[str, Any]:
    chains = read_gzip_json("datas/l3_scene_chains.json.gz")
    animator_data = read_gzip_json("datas/l3_animator_programs.json.gz")
    transition_data = read_gzip_json("datas/l3_transition_model.json.gz")
    composition = read_gzip_json("datas/l3_composition.json.gz")
    frame_cases = read_gzip_json("datas/l3_frame_cases.json.gz")
    driven = read_gzip_json("datas/l3_driven_props.json.gz")
    motion = read_gzip_json("datas/l3-scene-chains/motion-000.json.gz")
    binding_rows = read_gzip_json("datas/l3-scene-chains/animation_bindings-006.json.gz")
    nodes = read_gzip_json("datas/l3-scene-chains/nodes-007.json.gz")

    focus_nodes = {
        n["transform"]["path_id"]: n
        for n in nodes
        if n.get("transform", {}).get("serialized_file") == "data.unity3d/resources.assets"
    }
    # Ancestors needed by the focus are all contained in root 10; fail closed if not.
    chain: list[dict[str, Any]] = []
    current = FOCUS_TRANSFORM
    seen: set[int] = set()
    while current:
        if current in seen:
            raise AssertionError("transform cycle in Board_Pause ancestry")
        seen.add(current)
        n = focus_nodes.get(current)
        if n is None:
            raise AssertionError(f"missing required transform {current} in consulted node shard")
        t = n["transform_properties"]
        go = n["gameobject_properties"]
        chain.append(
            {
                "transform_path_id": current,
                "gameobject_path_id": n["gameobject"]["path_id"],
                "name": go.get("m_Name"),
                "active_serialized": bool(go.get("m_IsActive")),
                "layer": go.get("m_Layer"),
                "local_position": t.get("m_LocalPosition"),
                "local_rotation": t.get("m_LocalRotation"),
                "local_scale": t.get("m_LocalScale"),
                "parent_transform_path_id": _pointer_path_id(t.get("m_Father")),
                "path_within_root": n.get("path"),
            }
        )
        current = _pointer_path_id(t.get("m_Father")) or 0

    if chain[0]["gameobject_path_id"] != FOCUS_GO or chain[-1]["gameobject_path_id"] != ROOT_GO:
        raise AssertionError("focus ancestry does not terminate at serialized Board_Pause root")

    root_index = 10
    root_view = chains["roots"][root_index]
    if root_view.get("label") != "Board_Pause" or root_view.get("gameobject", {}).get("path_id") != ROOT_GO:
        raise AssertionError("root index 10 is not the expected Board_Pause asset")

    # Recheck the earlier reported Box_Gift (7) ancestry blocker. Its direct parent
    # id 270123 is a Transform, not a GameObject; the complete chain is present.
    box_nodes = read_gzip_json("datas/l3-scene-chains/nodes-005.json.gz")
    box_map = {
        n["transform"]["path_id"]: n
        for n in box_nodes
        if n.get("transform", {}).get("serialized_file") == "data.unity3d/resources.assets"
    }
    box_chain: list[dict[str, Any]] = []
    current = PRIOR_BLOCK_TRANSFORM
    seen = set()
    while current:
        if current in seen:
            raise AssertionError("transform cycle in Box_Gift (7) ancestry")
        seen.add(current)
        n = box_map.get(current)
        if n is None:
            raise AssertionError(f"missing Box_Gift ancestor transform {current}")
        t = n["transform_properties"]
        go = n["gameobject_properties"]
        box_chain.append({
            "transform_path_id": current,
            "gameobject_path_id": n["gameobject"]["path_id"],
            "name": go.get("m_Name"),
            "local_position": t.get("m_LocalPosition"),
            "local_scale": t.get("m_LocalScale"),
            "parent_transform_path_id": _pointer_path_id(t.get("m_Father")),
            "path_within_root": n.get("path"),
        })
        current = _pointer_path_id(t.get("m_Father")) or 0
    box_root_view = chains["roots"][1]
    if box_chain[0]["gameobject_path_id"] != PRIOR_BLOCK_GO or box_chain[-1]["gameobject_path_id"] != box_root_view.get("gameobject", {}).get("path_id"):
        raise AssertionError("Box_Gift ancestry does not terminate at its Board_Players template root")
    if box_root_view.get("label") != "Board_Players":
        raise AssertionError("root index 1 is not Board_Players")

    attachment = next(
        a for a in animator_data["animator_attachments"]
        if a.get("animator", {}).get("path_id") == ANIMATOR_ID
    )
    if attachment.get("gameobject", {}).get("path_id") != FOCUS_GO:
        raise AssertionError("Animator attachment does not point to Popup_QuitMissions")
    controller_ref = attachment["controllers"][0]
    if controller_ref.get("path_id") != CONTROLLER_ID:
        raise AssertionError("unexpected Popup_QuitMissions controller")
    controller = next(c for c in animator_data["controllers"] if c["identity"]["path_id"] == CONTROLLER_ID)
    machine = controller["machines"][0]
    appear = next(s for s in machine["states"] if s["state_index"] == machine["default_state_index"])
    hide = next(s for s in machine["states"] if s["name_candidates"] == ["Hide"])
    any_hide = next(
        tr for tr in machine["any_state_transitions"]
        if tr.get("destination_index") == hide["state_index"]
        and any("Hide" in c.get("parameter_names", []) for c in tr.get("conditions", []))
    )
    if appear["name_candidates"] != ["Appear"]:
        raise AssertionError("serialized default state is not Appear")

    model_controller = next(c for c in transition_data["controllers"] if c["identity"]["path_id"] == CONTROLLER_ID)
    model_machine = model_controller["machines"][0]
    if model_machine["default_state_index"] != machine["default_state_index"]:
        raise AssertionError("transition model disagrees with program default state")

    clip = next(c for c in motion if c["identity"]["path_id"] == APPEAR_CLIP_ID)
    clip_samples = _clip_sample(clip)
    clip_bindings = [
        r for r in binding_rows
        if r.get("animator", {}).get("path_id") == ANIMATOR_ID
        and r.get("clip", {}).get("path_id") in (APPEAR_CLIP_ID, HIDE_CLIP_ID)
    ]
    if len(clip_bindings) != 4:
        raise AssertionError(f"expected two bindings for Appear and two for Hide, got {len(clip_bindings)}")
    appear_bindings = [r for r in clip_bindings if r["clip"]["path_id"] == APPEAR_CLIP_ID]
    if sorted(r["binding_index"] for r in appear_bindings) != [0, 1]:
        raise AssertionError("unexpected Appear binding indices")
    appear_targets = []
    for row in sorted(appear_bindings, key=lambda r: r["binding_index"]):
        appear_targets.append(
            {
                "binding_index": row["binding_index"],
                "binding": row["binding"],
                "path_candidates": row["path_candidates"],
                "component_targets": row["component_targets"],
                "status": row["status"],
                "property_crc32_candidates": row.get("property_crc32_candidates", []),
            }
        )
    if any(r["status"] != "unique_target" for r in appear_bindings):
        raise AssertionError("Appear binding target resolution is not unique")

    route_map = {
        (r["class_id"], r["attribute"]): r
        for r in driven["property_route"]
    }
    property_routes = []
    for b in clip["bindings"]:
        route = route_map.get((b["typeID"], b["attribute"]))
        if route is None:
            raise AssertionError(f"unrouted clip binding: {b}")
        property_routes.append({"binding": b, "route": route})

    cameras = [
        {
            "identity": c.get("identity"),
            "gameobject": c.get("gameobject"),
            "serialized_file": c.get("identity", {}).get("serialized_file"),
        }
        for c in chains["scene_context"]
        if c.get("type") == "Camera"
    ]
    if not cameras:
        raise AssertionError("scene context has no camera records; expected separate scene cameras")

    external_rows = [
        "425352\t57508\t439142",
        "439142\t212696\t0",
        "277770\t96185\t270123",
        "270123\t226561\t339888",
        "339888\t62705\t417314",
        "417314\t120127\t369060",
        "369060\t139738\t0",
    ]
    return {
        "schema": 1,
        "provisional": True,
        "scope": "Independent join of the checked-in L3 hierarchy, animation, serialized Animator graph, and camera/composition contracts for one asset-template UI chain. It yields template-local modeled state only; it does not establish a live scene instance, Unity Animator execution, a camera stack, pixel viewport projection, runtime readback, or render.",
        "claim": {
            "board_item": 12,
            "branch": BRANCH,
            "artifact": "datas/l3_composition_viewport_engine_transition_12.json.gz",
            "mode": "REPLICATION",
        },
        "focus": {
            "label": "Popup_QuitMissions",
            "gameobject": {"serialized_file": "data.unity3d/resources.assets", "path_id": FOCUS_GO},
            "transform": {"serialized_file": "data.unity3d/resources.assets", "path_id": FOCUS_TRANSFORM},
            "board_pause_root": {"serialized_file": "data.unity3d/resources.assets", "path_id": ROOT_GO},
            "root_view_index": root_index,
            "root_kind": root_view.get("kind"),
            "root_label": root_view.get("label"),
            "root_node_count": root_view.get("nodes"),
            "serialized_file_classification": "resources.assets asset/template root; not a level0-3 scene instance in this chain artifact",
            "template_local_ancestry_leaf_to_root": chain,
        },
        "prior_block_recheck": {
            "subject": "Box_Gift (7), GO 96185, Transform 277770, Board_Players root index 1",
            "status": "EARLIER_MISSING_PARENT_CLAIM_CORRECTED",
            "type_correction": "PathID 270123 is a Transform, not a GameObject. Its owning GameObject is 226561 (Parent_Rewards).",
            "transform_chain_leaf_to_root": box_chain,
            "raw_transform_tree_rows": [
                [277770, 96185, 270123],
                [270123, 226561, 339888],
                [339888, 62705, 417314],
                [417314, 120127, 369060],
                [369060, 139738, 0],
            ],
            "conclusion": "The parent chain is present and reaches Board_Players in the serialized template. The earlier report's claim that the parent was absent from the node index was a type/identity error, not a verified repository-wide missing artifact.",
        },
        "composition_viewport": {
            "status": "NOT_PROJECTED_TEMPLATE_INSTANCE_AUTHORITY_NOT_ESTABLISHED",
            "why": [
                "The selected root is a resources.assets UI root (Board_Pause), not a serialized level0-3 scene instance.",
                "All computed transforms are local to that serialized template root; no explicit runtime parent/placement override is joined to a particular camera.",
                "The artifact has five serialized scene Camera objects (six camera references in the composition contract); they are separate level0-3 contexts, so assigning one to this template would be an unsupported assumption.",
            ],
            "camera_inventory": cameras,
            "scene_composition_pair_count": composition["counts"]["scene_camera_renderer_pairs"],
            "frame_model_scope": frame_cases["scope"],
            "pixel_bounds": None,
            "rendered": False,
        },
        "serialized_animator_program": {
            "animator": attachment["animator"],
            "gameobject": attachment["gameobject"],
            "enabled_serialized": attachment.get("enabled"),
            "controller": {"identity": controller["identity"], "name": controller.get("name")},
            "machine_index": machine["machine_index"],
            "default_state": {
                "index": appear["state_index"],
                "name_candidates": appear.get("name_candidates"),
                "clip": appear["trees"][0]["nodes"][0]["clip"],
            },
            "hide_state": {
                "index": hide["state_index"],
                "name_candidates": hide.get("name_candidates"),
                "clip": hide["trees"][0]["nodes"][0]["clip"],
            },
            "any_state_hide_transition": {
                "destination_index": any_hide["destination_index"],
                "conditions": any_hide["conditions"],
                "serialized_duration": any_hide["raw"].get("m_TransitionDuration"),
                "serialized_has_exit_time": any_hide["raw"].get("m_HasExitTime"),
                "serialized_interruption_source": any_hide["raw"].get("m_InterruptionSource"),
            },
            "model_crosscheck": {
                "same_controller_identity": model_controller["identity"],
                "same_default_state_index": model_machine["default_state_index"],
                "model_scope": transition_data["scope"],
            },
            "not_a_runtime_trace": True,
        },
        "appear_clip": {
            "identity": clip["identity"],
            "name": clip["name"],
            "duration_seconds": clip["stop"] - clip["start"],
            "bindings_resolved_for_this_animator": appear_targets,
            "property_routes": property_routes,
            "serialized_curve_probe_samples": clip_samples,
            "sample_status": "ARITHMETIC_MODEL_NOT_UNITY_READBACK",
        },
        "raw_branch_grep_audit": {
            "needle": "270123",
            "method": "Enumerated and decompressed every tracked file below reverse-engineering/raw/ on each known remote branch ref; exact-byte substring search only, not a substitute for typetree decoding.",
            "branches": [
                {
                    "ref": "origin/arena/a5a74747-windwings-space-shooter-game-p",
                    "commit": "fe247fb8c586161284130d044db8af33dd6cacdd",
                    "files_scanned": 857,
                    "decoded_bytes": 280733641,
                    "paths_with_literal": 1,
                    "transform_tree_sha256": "30624c3e69a64559d0b790d48a6aa06db725edbcb9687e1457e72e7311c76ae2",
                },
                {
                    "ref": "origin/arena/ef6b75ef-windwings-space-shooter-game-p",
                    "commit": PEER_COMMIT,
                    "files_scanned": 58858,
                    "decoded_bytes": 4364634182,
                    "paths_with_literal": 20,
                    "transform_tree_sha256": PEER_RAW_PINS["reverse-engineering/raw/typetrees/transform-tree.tsv.gz"],
                },
                {
                    "ref": "origin/arena/20330d0e-windwings-space-shooter-game-p",
                    "commit": "bab67115f5192d5fa0e17c07920aa63f109a5afa",
                    "files_scanned": 857,
                    "decoded_bytes": 280733641,
                    "paths_with_literal": 1,
                    "transform_tree_sha256": "30624c3e69a64559d0b790d48a6aa06db725edbcb9687e1457e72e7311c76ae2",
                },
            ],
            "finding": "The matching transform-tree rows establish that 270123 is a Transform in the Box_Gift (7) chain, not a GameObject. No repository-wide-missing conclusion is made; the checked-in node shard supplies its typed owner and pose.",
        },
        "source_corroboration": {
            "branch": PEER_REF,
            "commit": PEER_COMMIT,
            "pins_sha256_of_git_blob_bytes": PEER_RAW_PINS,
            "transform_tree_rows": external_rows,
            "interpretation": "Raw transform-tree mapping independently agrees that Popup_QuitMissions transform 425352 belongs to GO 57508 and is parented by Board_Pause transform 439142; Board_Pause transform is GO 212696 with no serialized parent. The same raw map confirms the full Box_Gift (7) transform chain through Transform 270123 to the Board_Players asset root. These rows establish identity/hierarchy, not runtime instantiation or viewport placement.",
        },
        "limits": [
            "Model is not a Unity readback and is not a rendered frame.",
            "Animator entry/default-state scheduling and transition timing are not proven by serialized graph data alone.",
            "A current scene instance/parent authority and concrete active camera are required before viewport pixels can be computed.",
            "No screenshot, redraw, or visual acceptance gate was used.",
            "The time-0.5 alpha is the declared hold-last serialized-curve sample policy; it is not asserted as engine state.",
        ],
        "inputs_sha256": {p: sha256_file(ROOT / p) for p in LOCAL_INPUTS},
    }


def write_artifact(path: Path = ARTIFACT) -> dict[str, Any]:
    data = build_artifact()
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw_out:
        with gzip.GzipFile(fileobj=raw_out, mode="wb", compresslevel=9, mtime=0) as f:
            f.write(raw)
    return data


def main() -> None:
    data = write_artifact()
    print(json.dumps({
        "artifact": str(ARTIFACT.relative_to(ROOT)),
        "sha256": sha256_file(ARTIFACT),
        "bytes": ARTIFACT.stat().st_size,
        "root": data["focus"]["root_label"],
        "transform_chain_depth": len(data["focus"]["template_local_ancestry_leaf_to_root"]),
        "viewport_status": data["composition_viewport"]["status"],
        "runtime": "NOT_MEASURED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
