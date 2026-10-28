#!/usr/bin/env python3
"""Build the bounded serialized SpriteAtlas/remap and Sprite-skinning audit for PR12 #6.

This resolves serialized Sprite -> SpriteAtlas -> m_RenderDataMap identities and
attaches static vertex bounds from the pinned mesh contract. It does not execute
Unity, request an atlas, instantiate SpriteSkin, or measure runtime deformation.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = Path("datas/l2_a5a74747_6_spriteatlas_remap.json.gz")
RAW_DIR = Path("reverse-engineering/raw/sprite-geometry")
INDEX_PATH = RAW_DIR / "index.json"
MESH_CONTRACT_PATH = Path("datas/sprite_mesh_contract.json.gz")
DUMP_PATH = Path("reverse-engineering/il2cpp/dump.cs.gz")
INDEX_SHA256 = "29b074baac8946033b1abc1542b945bdbd601524475e6deca1a23d06a3fe5531"
MESH_CONTRACT_SHA256 = "90fc5252b3e8416686c0788aa7bae50b3bb4c9b5382887d39e14bd93023eaffa"
DUMP_COMPRESSED_SHA256 = "e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454"
DUMP_DECOMPRESSED_SHA256 = "8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c"
RAW_SOURCE_BRANCH = "arena/ef6b75ef-windwings-space-shooter-game-p"
RAW_SOURCE_SNAPSHOT = "72041a1d400be6b0972f5bfa9868efe3befaeca7"
RAW_SOURCE_COMMIT = "d9739910662be2de07f44faba30ed72e4b593e5c"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _read(rel: str | Path) -> bytes:
    return (ROOT / rel).read_bytes()


def _load_json_gzip(rel: str | Path, expected_sha: str) -> tuple[Any, bytes]:
    payload = _read(rel)
    if sha256(payload) != expected_sha:
        raise ValueError(f"pinned compressed source SHA-256 mismatch: {rel}")
    return json.loads(gzip.decompress(payload)), payload


def _identity(row: dict[str, Any]) -> tuple[str, int]:
    return row["serialized_file"], int(row["path_id"])


def _key(value: Any) -> str:
    return canonical_json(value).decode("utf-8")


def _load_raw_objects() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    index_bytes = _read(INDEX_PATH)
    if sha256(index_bytes) != INDEX_SHA256:
        raise ValueError("pinned Sprite-geometry index SHA-256 mismatch")
    index = json.loads(index_bytes)
    objects: list[dict[str, Any]] = []
    pins: list[dict[str, Any]] = []
    for shard in index.get("files", []):
        rel = RAW_DIR / shard["path"]
        payload = _read(rel)
        decoded = gzip.decompress(payload)
        if sha256(decoded) != shard["sha256_decompressed"]:
            raise ValueError(f"decoded Sprite-geometry shard SHA mismatch: {rel}")
        lines = decoded.splitlines()
        if len(lines) != shard["rows"]:
            raise ValueError(f"Sprite-geometry shard row count mismatch: {rel}")
        rows = [json.loads(line) for line in lines]
        objects.extend(rows)
        pins.append({
            "path": rel.as_posix(),
            "rows": len(rows),
            "compressed_bytes": len(payload),
            "compressed_sha256": sha256(payload),
            "decompressed_sha256": sha256(decoded),
        })
    return objects, pins


def _local_pointer(owner_file: str, pointer: dict[str, Any], label: str) -> tuple[str, int]:
    file_id = int(pointer.get("m_FileID", 0))
    path_id = int(pointer.get("m_PathID", 0))
    if file_id != 0:
        raise ValueError(f"out-of-scope nonlocal {label} PPtr: fileID={file_id}")
    return owner_file, path_id


def _zero_aabb(aabb: dict[str, Any]) -> bool:
    center = aabb.get("m_Center", {})
    extent = aabb.get("m_Extent", {})
    return all(float(center.get(k, 0)) == 0.0 and float(extent.get(k, 0)) == 0.0 for k in "xyz")


def build_receipt() -> dict[str, Any]:
    index_bytes = _read(INDEX_PATH)
    if sha256(index_bytes) != INDEX_SHA256:
        raise ValueError("pinned Sprite-geometry index SHA-256 mismatch")
    index = json.loads(index_bytes)
    if index.get("counts") != {"Texture2D": 654, "Sprite": 2185, "SpriteAtlas": 66}:
        raise ValueError("Sprite-geometry source inventory changed")
    objects, shard_pins = _load_raw_objects()
    counts = Counter(row.get("type") for row in objects)
    if counts != Counter({"Sprite": 2185, "Texture2D": 654, "SpriteAtlas": 66}):
        raise ValueError(f"Sprite-geometry object counts changed: {counts}")

    sprites = [row for row in objects if row["type"] == "Sprite"]
    atlases = [row for row in objects if row["type"] == "SpriteAtlas"]
    textures = [row for row in objects if row["type"] == "Texture2D"]
    sprite_by_id: dict[tuple[str, int], dict[str, Any]] = {}
    atlas_by_id: dict[tuple[str, int], dict[str, Any]] = {}
    texture_by_id: dict[tuple[str, int], dict[str, Any]] = {}
    for rows, lookup, label in ((sprites, sprite_by_id, "Sprite"), (atlases, atlas_by_id, "SpriteAtlas"), (textures, texture_by_id, "Texture2D")):
        for row in rows:
            identity = _identity(row)
            if identity in lookup:
                raise ValueError(f"duplicate {label} identity: {identity}")
            if row.get("context_status") != "resolved" or row.get("projection") == "metadata_only_no_image_data" and label != "Texture2D":
                raise ValueError(f"unexpected source row status for {label}: {identity}")
            lookup[identity] = row

    mesh_contract, mesh_payload = _load_json_gzip(MESH_CONTRACT_PATH, MESH_CONTRACT_SHA256)
    if mesh_contract.get("status") != "PROVISIONAL_SERIALIZED_MESH_REFERENCE_NOT_UNITY_SCENE_PLACEMENT_OR_PNG_PIVOT":
        raise ValueError("pinned Sprite mesh contract status changed")
    mesh_by_id: dict[tuple[str, int], dict[str, Any]] = {}
    for row in mesh_contract.get("sprites", []):
        raw_identity = row.get("identity", {})
        serialized_file = str(raw_identity.get("serialized_file", ""))
        if serialized_file.startswith("data.unity3d/"):
            serialized_file = serialized_file[len("data.unity3d/"):]
        identity = (serialized_file, int(raw_identity.get("path_id", -1)))
        if identity in mesh_by_id:
            raise ValueError(f"duplicate mesh-contract identity: {identity}")
        mesh_by_id[identity] = row
    if set(mesh_by_id) != set(sprite_by_id):
        raise ValueError("Sprite mesh contract identity set differs from raw Sprite census")

    atlas_data: dict[tuple[str, int], dict[str, Any]] = {}
    atlas_entries_by_key: dict[tuple[str, int], dict[str, int]] = {}
    atlas_rows: list[dict[str, Any]] = []
    all_map_keys: Counter[str] = Counter()
    packed_refs: Counter[tuple[str, int]] = Counter()
    total_map_entries = total_packed_refs = total_name_rows = 0
    packed_name_matches = 0
    texture_resolutions = 0
    for atlas in sorted(atlases, key=lambda row: (_identity(row)[0], _identity(row)[1])):
        atlas_id = _identity(atlas)
        tree = atlas.get("tree", {})
        entries = tree.get("m_RenderDataMap", [])
        packed = tree.get("m_PackedSprites", [])
        packed_names = tree.get("m_PackedSpriteNamesToIndex", [])
        by_key: dict[str, int] = {}
        normalized_entries: list[dict[str, Any]] = []
        for map_index, entry in enumerate(entries):
            if not isinstance(entry, list) or len(entry) != 2:
                raise ValueError(f"malformed render-data-map entry: {atlas_id}/{map_index}")
            render_key, render_data = entry
            key = _key(render_key)
            if key in by_key:
                raise ValueError(f"duplicate render-data key within atlas {atlas_id}")
            by_key[key] = map_index
            all_map_keys[key] += 1
            texture_ptr = render_data.get("texture", {})
            texture_id = _local_pointer(atlas_id[0], texture_ptr, "atlas texture")
            texture = texture_by_id.get(texture_id)
            if texture is None:
                raise ValueError(f"unresolved atlas texture PPtr: {atlas_id}/{map_index}/{texture_id}")
            texture_resolutions += 1
            tex_tree = texture.get("tree", {})
            normalized_entries.append({
                "map_index": map_index,
                "render_data_key": render_key,
                "texture": {
                    "serialized_file": texture_id[0],
                    "path_id": texture_id[1],
                    "name": tex_tree.get("m_Name", ""),
                    "dimensions": [tex_tree.get("m_Width"), tex_tree.get("m_Height")],
                    "object_bytes_sha256": texture.get("object_bytes_sha256"),
                },
                "alpha_texture_pptr": render_data.get("alphaTexture"),
                "texture_rect": render_data.get("textureRect"),
                "texture_rect_offset": render_data.get("textureRectOffset"),
                "atlas_rect_offset": render_data.get("atlasRectOffset"),
                "uv_transform": render_data.get("uvTransform"),
                "downscale_multiplier": render_data.get("downscaleMultiplier"),
                "settings_raw": render_data.get("settingsRaw"),
                "secondary_textures": render_data.get("secondaryTextures", []),
            })
        if len(packed) != len(packed_names) or len(entries) != len(packed):
            raise ValueError(f"packed sprites, names, and render-data map do not align: {atlas_id}")
        for packed_index, pointer in enumerate(packed):
            packed_id = _local_pointer(atlas_id[0], pointer, "packed Sprite")
            packed_sprite = sprite_by_id.get(packed_id)
            if packed_sprite is None:
                raise ValueError(f"unresolved packed Sprite PPtr: {atlas_id}/{packed_index}/{packed_id}")
            packed_refs[packed_id] += 1
            sprite_name = packed_sprite.get("tree", {}).get("m_Name", "")
            if packed_names[packed_index] != sprite_name:
                raise ValueError(f"packed Sprite name/order mismatch: {atlas_id}/{packed_index}")
            packed_name_matches += 1
        total_map_entries += len(entries)
        total_packed_refs += len(packed)
        total_name_rows += len(packed_names)
        atlas_entries_by_key[atlas_id] = by_key
        atlas_data[atlas_id] = {"row": atlas, "entries": normalized_entries}
        atlas_rows.append({
            "identity": {"serialized_file": atlas_id[0], "path_id": atlas_id[1]},
            "name": tree.get("m_Name", ""),
            "object_bytes_sha256": atlas.get("object_bytes_sha256"),
            "packed_sprite_count": len(packed),
            "packed_name_count": len(packed_names),
            "render_data_map_count": len(entries),
            "packed_name_order_matches_sprite_pptrs": True,
            "normalized_render_data_map_sha256": sha256(canonical_json(normalized_entries)),
        })

    if len(all_map_keys) != total_map_entries or any(n != 1 for n in all_map_keys.values()):
        raise ValueError("render-data keys are not unique across the inventoried atlases")
    if len(packed_refs) != 1550 or any(n != 1 for n in packed_refs.values()):
        raise ValueError("packed Sprite pointers are not a one-to-one inventory")

    route_counts: Counter[str] = Counter()
    sprite_rows: list[dict[str, Any]] = []
    mapping_rows: list[dict[str, Any]] = []
    rendered_keys: Counter[tuple[str, int, str]] = Counter()
    bone_counts: Counter[str] = Counter()
    bindpose_counts: Counter[str] = Counter()
    channel_layouts: Counter[str] = Counter()
    zero_submesh_aabb = 0
    for sprite in sorted(sprites, key=lambda row: (_identity(row)[0], _identity(row)[1])):
        sprite_id = _identity(sprite)
        tree = sprite.get("tree", {})
        rd = tree.get("m_RD", {})
        mesh = mesh_by_id[sprite_id]
        if mesh.get("raw", {}).get("object_sha256") != sprite.get("object_bytes_sha256"):
            raise ValueError(f"mesh-contract object SHA differs from raw Sprite: {sprite_id}")
        bones = tree.get("m_Bones", [])
        bindposes = rd.get("m_Bindpose", [])
        bone_counts[str(len(bones))] += 1
        bindpose_counts[str(len(bindposes))] += 1
        channels = rd.get("m_VertexData", {}).get("m_Channels", [])
        active_channels = [i for i, channel in enumerate(channels) if int(channel.get("dimension", 0)) > 0]
        layout = {"active_channel_indices": active_channels,
                  "active_channel_descriptors": [channels[i] for i in active_channels]}
        channel_layouts[canonical_json(layout).decode("utf-8")] += 1
        for submesh in rd.get("m_SubMeshes", []):
            if _zero_aabb(submesh.get("localAABB", {})):
                zero_submesh_aabb += 1

        atlas_ptr = tree.get("m_SpriteAtlas", {})
        atlas_path_id = int(atlas_ptr.get("m_PathID", 0))
        atlas_id: tuple[str, int] | None = None
        key = tree.get("m_RenderDataKey")
        map_index: int | None = None
        route = "direct_sprite_render_data"
        if atlas_path_id:
            atlas_id = _local_pointer(sprite_id[0], atlas_ptr, "SpriteAtlas")
            if atlas_id not in atlas_data:
                raise ValueError(f"unresolved SpriteAtlas PPtr: {sprite_id} -> {atlas_id}")
            key_text = _key(key)
            map_index = atlas_entries_by_key[atlas_id].get(key_text)
            if map_index is None:
                raise ValueError(f"exact Sprite m_RenderDataKey missing in referenced atlas: {sprite_id}")
            route = "atlas_pointer_and_exact_render_data_key"
            rendered_keys[(atlas_id[0], atlas_id[1], key_text)] += 1
            atlas = atlas_data[atlas_id]["row"]
            packed = atlas.get("tree", {}).get("m_PackedSprites", [])
            packed_index = next((i for i, pointer in enumerate(packed)
                                 if _local_pointer(atlas_id[0], pointer, "packed Sprite") == sprite_id), None)
            if packed_index is None:
                raise ValueError(f"Sprite PPtr is not in referenced atlas packed list: {sprite_id}")
            atlas_name = atlas.get("tree", {}).get("m_Name", "")
            entry = atlas_data[atlas_id]["entries"][map_index]
            mapping_rows.append({
                "sprite": {"serialized_file": sprite_id[0], "path_id": sprite_id[1],
                           "name": tree.get("m_Name", ""),
                           "object_bytes_sha256": sprite.get("object_bytes_sha256")},
                "atlas": {"serialized_file": atlas_id[0], "path_id": atlas_id[1],
                          "name": atlas_name,
                          "object_bytes_sha256": atlas.get("object_bytes_sha256")},
                "atlas_tag": tree.get("m_AtlasTags", []),
                "render_data_key": key,
                "render_data_map_index": map_index,
                "packed_sprite_index": packed_index,
                "resolved_render_data": entry,
            })
        else:
            if tree.get("m_AtlasTags", []):
                raise ValueError(f"direct Sprite render-data route unexpectedly has atlas tags: {sprite_id}")
            packed_index = None
            atlas_name = None
            key_text = _key(key)
        route_counts[route] += 1

        bounds = mesh.get("metrics", {})
        sprite_rows.append({
            "identity": {"serialized_file": sprite_id[0], "path_id": sprite_id[1]},
            "name": tree.get("m_Name", ""),
            "object_bytes_sha256": sprite.get("object_bytes_sha256"),
            "atlas_route": route,
            "atlas": None if atlas_id is None else {
                "serialized_file": atlas_id[0], "path_id": atlas_id[1], "name": atlas_name,
            },
            "render_data_key": key,
            "render_data_map_index": map_index,
            "atlas_tag": tree.get("m_AtlasTags", []),
            "serialized_bone_count": len(bones),
            "serialized_bindpose_count": len(bindposes),
            "active_vertex_channel_indices": active_channels,
            "static_vertex_aabb": {
                "minimum": bounds.get("minimum"),
                "maximum": bounds.get("maximum"),
                "span": bounds.get("span"),
                "vertex_count": mesh.get("decode_proof", {}).get("vertices"),
            },
            "serialized_submesh_local_aabb_zero": all(
                _zero_aabb(row.get("localAABB", {})) for row in rd.get("m_SubMeshes", [])
            ),
        })

    if route_counts != Counter({"direct_sprite_render_data": 635, "atlas_pointer_and_exact_render_data_key": 1550}):
        raise ValueError(f"Sprite route counts changed: {route_counts}")
    if len(rendered_keys) != 1550 or any(n != 1 for n in rendered_keys.values()):
        raise ValueError("Sprite render-data keys are not a one-to-one map join")
    if sum(bone_counts.values()) != 2185 or bone_counts != Counter({"0": 2185}):
        raise ValueError(f"unexpected serialized Sprite bone counts: {bone_counts}")
    if bindpose_counts != Counter({"0": 2185}):
        raise ValueError(f"unexpected serialized Sprite bindpose counts: {bindpose_counts}")
    if len(mesh_by_id) != 2185 or len(sprite_rows) != 2185:
        raise ValueError("static vertex bounds do not cover the raw Sprite identity set")

    dump_payload = _read(DUMP_PATH)
    if sha256(dump_payload) != DUMP_COMPRESSED_SHA256:
        raise ValueError("pinned IL2CPP dump compressed SHA mismatch")
    dump_decoded = gzip.decompress(dump_payload)
    if sha256(dump_decoded) != DUMP_DECOMPRESSED_SHA256:
        raise ValueError("pinned IL2CPP dump decompressed SHA mismatch")
    dump_text = dump_decoded.decode("utf-8")
    atlas_requested_declared = "private static Action<string, Action<SpriteAtlas>> atlasRequested;" in dump_text
    atlas_registered_declared = "private static Action<SpriteAtlas> atlasRegistered;" in dump_text
    if not atlas_requested_declared or not atlas_registered_declared:
        raise ValueError("pinned UnityEngine.U2D.SpriteAtlasManager event fields not found")

    return {
        "schema_version": 1,
        "task": "PR12 #6 — bounded serialized SpriteAtlas remap and Sprite skinning-bounds audit",
        "status": "BOUNDED_STATIC_ATLAS_MAP_AND_SPRITE_VERTEX_BOUNDS_RUNTIME_REMAP_NOT_OBSERVED",
        "source_provenance": {
            "raw_geometry_snapshot": {
                "branch": RAW_SOURCE_BRANCH,
                "snapshot_commit": RAW_SOURCE_SNAPSHOT,
                "raw_chunk_history_commit": RAW_SOURCE_COMMIT,
                "index_path": INDEX_PATH.as_posix(),
                "index_sha256": sha256(index_bytes),
                "unitypy_version": index.get("unitypy_version"),
                "apk_input_sha256": index.get("inputs_sha256", {}).get("data.unity3d"),
                "libil2cpp_input_sha256": index.get("inputs_sha256", {}).get("libil2cpp.so"),
                "metadata_input_sha256": index.get("inputs_sha256", {}).get("global-metadata.dat"),
                "shards": shard_pins,
            },
            "mesh_contract": {
                "path": MESH_CONTRACT_PATH.as_posix(),
                "compressed_sha256": sha256(mesh_payload),
                "sprites": len(mesh_by_id),
                "limits": "serialized positions / static vertex bounds only; no scene placement or deformed mesh",
            },
            "il2cpp_api_dump": {
                "path": DUMP_PATH.as_posix(),
                "compressed_sha256": sha256(dump_payload),
                "decompressed_sha256": sha256(dump_decoded),
                "unity_api_declares_atlas_requested": atlas_requested_declared,
                "unity_api_declares_atlas_registered": atlas_registered_declared,
                "game_subscription_or_invocation": "NOT_OBSERVED",
            },
        },
        "summary": {
            "raw_object_counts": dict(sorted(counts.items())),
            "sprites": len(sprites),
            "sprite_atlases": len(atlases),
            "textures_metadata_only": len(textures),
            "atlas_map_entry_count": total_map_entries,
            "packed_sprite_pointer_count": total_packed_refs,
            "packed_name_count": total_name_rows,
            "packed_names_matching_sprite_pointer_order": packed_name_matches,
            "atlas_texture_pointer_resolutions": texture_resolutions,
            "unique_render_data_keys_across_atlases": len(all_map_keys),
            "cross_atlas_duplicate_render_data_keys": sum(1 for count in all_map_keys.values() if count > 1),
            "sprites_with_exact_atlas_pointer_and_render_key_join": route_counts["atlas_pointer_and_exact_render_data_key"],
            "sprites_using_direct_m_RD_route": route_counts["direct_sprite_render_data"],
            "unresolved_or_ambiguous_sprite_atlas_joins": 0,
            "unmatched_atlas_packed_sprite_pointers": 0,
            "serialized_sprite_bone_count_histogram": dict(sorted(bone_counts.items())),
            "serialized_sprite_bindpose_count_histogram": dict(sorted(bindpose_counts.items())),
            "serialized_submesh_local_aabb_zero_count": zero_submesh_aabb,
            "static_vertex_bounds_rows": len(sprite_rows),
            "static_vertex_count_total": sum(row["static_vertex_aabb"]["vertex_count"] or 0 for row in sprite_rows),
            "vertex_channel_layout_histogram": {
                key: value for key, value in sorted(channel_layouts.items())
            },
        },
        "atlases": atlas_rows,
        "atlas_sprite_mappings": mapping_rows,
        "sprite_static_bounds_and_skin_metadata": sprite_rows,
        "runtime_boundary": {
            "serialized_atlas_resolution": "EXACT_STATIC_PPTR_AND_RENDER_DATA_KEY_JOIN",
            "runtime_atlas_request_or_registration": "NOT_OBSERVED",
            "UnityEngine.U2D.SpriteAtlasManager_api": "The pinned API dump declares atlasRequested and atlasRegistered events; this does not prove a game subscription, request, or registration during play.",
            "sprite_bone_and_bindpose_data": "All 2185 inventoried Sprite typetrees serialize empty m_Bones and m_RD.m_Bindpose arrays. This is scoped to those Sprite rows, not all components or runtime meshes.",
            "bounds": "Bounds are static vertex AABBs from the pinned serialized Sprite mesh contract. Serialized submesh localAABB fields are retained as zero where present; no runtime-deformed/skinned bounds are claimed.",
        },
        "evidence_boundary": [
            "The six pinned JSONL shards contain 2185 Sprite, 66 SpriteAtlas, and 654 Texture2D metadata records; texture pixels are not in this projection.",
            "All 1550 packed Sprite PPtrs, packed-name positions, and SpriteAtlas renderDataMap rows form an exact one-to-one static join in this inventoried input set.",
            "The static join does not establish a live/runtime SpriteAtlasManager request, late remap, scene instantiation, or GPU render result.",
            "No Sprite bone/bindpose arrays are populated in the inventoried Sprite typetrees; this does not rule out other component types, native code, or runtime-generated geometry outside the bounded scope.",
            "No rendered, runtime-deformed, or placement-authoritative skinning bounds are produced.",
        ],
    }


def encode_receipt(value: dict[str, Any]) -> bytes:
    raw = canonical_json(value) + b"\n"
    import io
    target = io.BytesIO()
    with gzip.GzipFile(fileobj=target, mode="wb", compresslevel=9, mtime=0, filename="") as stream:
        stream.write(raw)
    return target.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(OUTPUT_PATH), help="output path relative to repository root")
    args = parser.parse_args()
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(encode_receipt(build_receipt()))
    print(f"wrote {target.relative_to(ROOT)} ({target.stat().st_size} bytes; sha256={sha256(target.read_bytes())})")


if __name__ == "__main__":
    main()
