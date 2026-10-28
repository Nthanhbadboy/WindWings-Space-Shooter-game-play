#!/usr/bin/env python3
"""Build a bounded serialized-data geometry model for coordination item #5.

This is an independent, source-pinned model of border-aware SpriteRenderer
slicing and borderless tiled rectangles. It is not Unity's native generator,
a runtime readback, or render validation.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "datas/l3_a5a74747_5_sliced_tiled_geometry.json.gz"
PEER_BRANCH = "arena/ef6b75ef-windwings-space-shooter-game-p"
PEER_COMMIT = "f5a447c15a117ca4571e2768f0274d1ad4f20b39"

# The compressed source artifacts are copied/pinned in peer commit PEER_COMMIT.
PINS = {
    "datas/scene_sprite_contract.json.gz": "6f46fe33303aac2adbe16cbd9889568fa7e0d9ce3439d75cef6c6bc404696095",
    "datas/sprite_mesh_contract.json.gz": "90fc5252b3e8416686c0788aa7bae50b3bb4c9b5382887d39e14bd93023eaffa",
    "reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz": "ea1d2b6d056fe4b2c099f1927ef6c41fc6a901bb35a9c5a24a5e0b684a319bd3",
    "reverse-engineering/raw/sprite-geometry/index.json": "29b074baac8946033b1abc1542b945bdbd601524475e6deca1a23d06a3fe5531",
    "reverse-engineering/il2cpp/dump.cs.gz": "e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454",
}
CONTENT_PINS = {
    "datas/scene_sprite_contract.json.gz": "94969cd1eee1524becacf5056bd95b1a4547757d220122eb977296d388bbb3a4",
    "datas/sprite_mesh_contract.json.gz": "03b06b19ddaf319e129b8121160b97a116f335af9e79a20b2616c5e783135c99",
    "reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz": "f1c663c206a8b6adf7be2211d71f93d8a7788de0fd86870dfdcccbdf9bfec3aa",
    "reverse-engineering/raw/sprite-geometry/index.json": "29b074baac8946033b1abc1542b945bdbd601524475e6deca1a23d06a3fe5531",
    "reverse-engineering/il2cpp/dump.cs.gz": "8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c",
}
APK_INPUTS = {
    "data.unity3d": "7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7",
    "libil2cpp.so": "9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99",
    "global-metadata.dat": "449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69",
}
EPS = 1e-9


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def normalize_asset(path: str) -> str:
    return path.removeprefix("data.unity3d/")


def load_inputs(root: Path) -> tuple[dict[str, bytes], dict[str, bytes]]:
    archived: dict[str, bytes] = {}
    contents: dict[str, bytes] = {}
    for relative, expected in PINS.items():
        raw = (root / relative).read_bytes()
        if sha256(raw) != expected:
            raise ValueError(f"source SHA mismatch: {relative}")
        content = gzip.decompress(raw) if relative.endswith(".gz") else raw
        if sha256(content) != CONTENT_PINS[relative]:
            raise ValueError(f"decompressed source SHA mismatch: {relative}")
        archived[relative] = raw
        contents[relative] = content
    return archived, contents


def key_of(identity: dict) -> tuple[str, int]:
    return normalize_asset(identity["serialized_file"]), int(identity["path_id"])


def _dict_map(rows: list[dict], key_fn, label: str) -> dict:
    out = {}
    for row in rows:
        key = key_fn(row)
        if key in out:
            raise ValueError(f"duplicate {label} identity: {key}")
        out[key] = row
    return out


def _direct_unpacked(geometry: dict) -> bool:
    settings = geometry.get("settings", {})
    return (
        settings.get("packed") is False
        and settings.get("packing_rotation") == 0
        and geometry.get("atlas") is None
        and geometry.get("route") == "sprite_render_data"
    )


def _nonzero_border(border: dict) -> bool:
    return any(float(border.get(axis, 0.0)) != 0.0 for axis in "xyzw")


def _validate_direct_uv_source(sprite: dict, geometry: dict) -> None:
    rect = sprite["source_rect"]
    texture_rect = geometry["texture_rect"]
    offset = geometry.get("texture_rect_offset", {})
    for axis in ("x", "y", "width", "height"):
        if abs(float(rect[axis]) - float(texture_rect[axis])) > EPS:
            raise ValueError("direct model expects source_rect == texture_rect")
    if any(abs(float(offset.get(axis, 0.0))) > EPS for axis in ("x", "y")):
        raise ValueError("direct model does not accept nonzero texture_rect_offset")


def _validate_border(sprite: dict) -> tuple[float, float, float, float]:
    border = sprite["border"]
    values = tuple(float(border[k]) for k in "xyzw")
    if not all(math.isfinite(v) and v >= 0.0 for v in values):
        raise ValueError("negative/non-finite Sprite.border component")
    rect = sprite["source_rect"]
    # Model convention: Vector4 xyzw is interpreted as left,bottom,right,top.
    if values[0] + values[2] > float(rect["width"]) + EPS:
        raise ValueError("horizontal border exceeds source rect")
    if values[1] + values[3] > float(rect["height"]) + EPS:
        raise ValueError("vertical border exceeds source rect")
    return values


def _uv_rect(sprite: dict, geometry: dict) -> tuple[float, float, float, float]:
    texture = geometry["texture"]
    width, height = map(float, texture["dimensions"])
    rect = geometry["texture_rect"]
    if width <= 0 or height <= 0:
        raise ValueError("invalid texture dimensions")
    u0 = float(rect["x"]) / width
    u1 = (float(rect["x"]) + float(rect["width"])) / width
    v0 = float(rect["y"]) / height
    v1 = (float(rect["y"]) + float(rect["height"])) / height
    return u0, v0, u1, v1


def _slice_model(renderer: dict, sprite: dict, geometry: dict) -> dict:
    tree = renderer["renderer_tree"]
    size = {axis: float(tree["m_Size"][axis]) for axis in ("x", "y")}
    ppu = float(sprite["pixels_to_units"])
    if not math.isfinite(ppu) or ppu <= 0.0:
        raise ValueError("invalid pixels-to-units")
    border = _validate_border(sprite)
    left, bottom, right, top = border
    if size["x"] + EPS < (left + right) / ppu or size["y"] + EPS < (bottom + top) / ppu:
        raise ValueError("requested size is smaller than fixed border sum")
    _validate_direct_uv_source(sprite, geometry)

    pivot = sprite["source_pivot"]
    xlo = -float(pivot["x"]) * size["x"]
    xhi = (1.0 - float(pivot["x"])) * size["x"]
    ylo = -float(pivot["y"]) * size["y"]
    yhi = (1.0 - float(pivot["y"])) * size["y"]
    xs = [xlo, xlo + left / ppu, xhi - right / ppu, xhi]
    ys = [yhi, yhi - top / ppu, ylo + bottom / ppu, ylo]

    u0, v0, u1, v1 = _uv_rect(sprite, geometry)
    tex = geometry["texture"]["dimensions"]
    uv_x = [u0, u0 + left / float(tex[0]), u1 - right / float(tex[0]), u1]
    uv_y = [v1, v1 - top / float(tex[1]), v0 + bottom / float(tex[1]), v0]
    vertices = []
    for row, y in enumerate(ys):
        for col, x in enumerate(xs):
            vertices.append({"position": [x, y, 0.0], "uv": [uv_x[col], uv_y[row]]})

    indices = []
    cell_signed_areas = []
    for row in range(3):
        for col in range(3):
            a = row * 4 + col
            b = a + 1
            c = a + 4
            d = c + 1
            # Top-left, top-right, bottom-left then bottom-left, top-right, bottom-right.
            indices.extend([a, b, c, c, b, d])
            for tri in ((a, b, c), (c, b, d)):
                p0, p1, p2 = (vertices[i]["position"] for i in tri)
                cell_signed_areas.append(
                    ((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])) / 2.0
                )
    if len(vertices) != 16 or len(indices) != 54 or min(indices) != 0 or max(indices) != 15:
        raise ValueError("slice grid topology invariant failed")
    if any(area > EPS for area in cell_signed_areas):
        raise ValueError("slice index winding changed")
    if any(not (u0 - EPS <= v["uv"][0] <= u1 + EPS and v0 - EPS <= v["uv"][1] <= v1 + EPS) for v in vertices):
        raise ValueError("slice UV escapes the direct texture rectangle")

    return {
        "renderer": renderer["identity"],
        "renderer_object_sha256": renderer["raw_object_sha256"],
        "scene_path": renderer["source_scene_path"],
        "renderer_name": renderer["name"],
        "draw_mode_code": int(tree["m_DrawMode"]),
        "requested_size": size,
        "tile_mode_code": int(tree.get("m_SpriteTileMode", 0)),
        "sprite": sprite["identity"],
        "sprite_name": sprite["name"],
        "sprite_object_sha256": sprite["raw"]["object_sha256"],
        "source": {
            "border_xyzw": list(border),
            "border_component_interpretation": "x=left,y=bottom,z=right,w=top (model convention; not native-body verified)",
            "pixels_to_units": ppu,
            "source_rect": sprite["source_rect"],
            "pivot_normalized": pivot,
            "texture": geometry["texture"],
            "texture_rect": geometry["texture_rect"],
        },
        "grid": {"columns": 3, "rows": 3, "vertices": 16, "quads": 9, "triangles": 18},
        "vertices": vertices,
        "triangle_indices": indices,
        "metrics": {
            "local_bounds_xy": [xlo, ylo, xhi, yhi],
            "column_x": xs,
            "row_y_top_to_bottom": ys,
            "uv_u_left_to_right": uv_x,
            "uv_v_top_to_bottom": uv_y,
            "fixed_border_units_lbrt": [left / ppu, bottom / ppu, right / ppu, top / ppu],
            "triangle_signed_area_min": min(cell_signed_areas),
            "triangle_signed_area_max": max(cell_signed_areas),
            "degenerate_triangle_count": sum(abs(area) <= EPS for area in cell_signed_areas),
        },
        "classification": "MODEL_NOT_NATIVE_RENDERER_READBACK",
    }


def _tile_model(renderer: dict, sprite: dict, geometry: dict) -> dict:
    tree = renderer["renderer_tree"]
    size = {axis: float(tree["m_Size"][axis]) for axis in ("x", "y")}
    ppu = float(sprite["pixels_to_units"])
    if not math.isfinite(ppu) or ppu <= 0.0 or min(size.values()) <= 0.0:
        raise ValueError("invalid tile dimensions/PPU")
    border = _validate_border(sprite)
    if any(border):
        raise ValueError("this bounded tile model only handles the observed zero-border tiled records")
    _validate_direct_uv_source(sprite, geometry)
    rect = sprite["source_rect"]
    tile_w = float(rect["width"]) / ppu
    tile_h = float(rect["height"]) / ppu
    if tile_w <= 0 or tile_h <= 0:
        raise ValueError("invalid source tile size")
    nx = math.ceil(size["x"] / tile_w - EPS)
    ny = math.ceil(size["y"] / tile_h - EPS)
    if nx * ny > 4096:
        raise ValueError("tile model cell cap exceeded")

    pivot = sprite["source_pivot"]
    xlo = -float(pivot["x"]) * size["x"]
    xhi = (1.0 - float(pivot["x"])) * size["x"]
    ylo = -float(pivot["y"]) * size["y"]
    yhi = (1.0 - float(pivot["y"])) * size["y"]
    u0, v0, u1, v1 = _uv_rect(sprite, geometry)
    vertices: list[dict] = []
    indices: list[int] = []
    tile_rows = []
    for row in range(ny):
        yb = ylo + row * tile_h
        yt = min(yb + tile_h, yhi)
        if yb >= yhi - EPS:
            continue
        y_fraction = (yt - yb) / tile_h
        for col in range(nx):
            xl = xlo + col * tile_w
            xr = min(xl + tile_w, xhi)
            if xl >= xhi - EPS:
                continue
            x_fraction = (xr - xl) / tile_w
            base = len(vertices)
            uu = u0 + (u1 - u0) * x_fraction
            vv = v0 + (v1 - v0) * y_fraction
            vertices.extend([
                {"position": [xl, yt, 0.0], "uv": [u0, vv]},
                {"position": [xr, yt, 0.0], "uv": [uu, vv]},
                {"position": [xl, yb, 0.0], "uv": [u0, v0]},
                {"position": [xr, yb, 0.0], "uv": [uu, v0]},
            ])
            indices.extend([base, base + 1, base + 2, base + 2, base + 1, base + 3])
            tile_rows.append({"row": row, "column": col, "local_bounds_xy": [xl, yb, xr, yt], "uv_fraction_xy": [x_fraction, y_fraction]})
    if len(vertices) != nx * ny * 4 or len(indices) != nx * ny * 6:
        raise ValueError("tile grid topology invariant failed")
    return {
        "renderer": renderer["identity"],
        "renderer_object_sha256": renderer["raw_object_sha256"],
        "scene_path": renderer["source_scene_path"],
        "renderer_name": renderer["name"],
        "draw_mode_code": int(tree["m_DrawMode"]),
        "requested_size": size,
        "tile_mode_code": int(tree.get("m_SpriteTileMode", 0)),
        "sprite": sprite["identity"],
        "sprite_name": sprite["name"],
        "sprite_object_sha256": sprite["raw"]["object_sha256"],
        "source": {
            "border_xyzw": list(border),
            "pixels_to_units": ppu,
            "source_rect": rect,
            "pivot_normalized": pivot,
            "texture": geometry["texture"],
            "texture_rect": geometry["texture_rect"],
            "native_tile_size_xy": [tile_w, tile_h],
        },
        "grid": {"columns": nx, "rows": ny, "quads": nx * ny, "vertices": len(vertices), "triangles": len(indices) // 3},
        "vertices": vertices,
        "triangle_indices": indices,
        "tiles": tile_rows,
        "policy": "continuous partial-edge tiling clipped at requested bounds; model policy, not native enum behavior",
        "classification": "MODEL_NOT_NATIVE_RENDERER_READBACK",
    }


def build(root: Path = ROOT) -> dict:
    archived, contents = load_inputs(root)
    scene = json.loads(contents["datas/scene_sprite_contract.json.gz"])
    sprite_contract = json.loads(contents["datas/sprite_mesh_contract.json.gz"])
    resolved = json.loads(contents["reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz"])
    source_index = json.loads(contents["reverse-engineering/raw/sprite-geometry/index.json"])
    dump_text = contents["reverse-engineering/il2cpp/dump.cs.gz"].decode()

    if scene.get("sources", {}).get("sprite_mesh_contract_sha256_decompressed") != CONTENT_PINS["datas/sprite_mesh_contract.json.gz"]:
        raise ValueError("scene receipt no longer pins the sprite mesh contract")
    if scene.get("sources", {}).get("dump_sha256_decompressed") != CONTENT_PINS["reverse-engineering/il2cpp/dump.cs.gz"]:
        raise ValueError("scene receipt dump identity changed")
    if sprite_contract.get("inputs_sha256") != APK_INPUTS or resolved.get("inputs_sha256") != APK_INPUTS:
        raise ValueError("sprite receipts do not bind the same original APK input hashes")
    if source_index.get("inputs_sha256") != APK_INPUTS:
        raise ValueError("raw sprite index input identity changed")
    if source_index.get("counts") != {"Texture2D": 654, "Sprite": 2185, "SpriteAtlas": 66}:
        raise ValueError("raw sprite source index counts changed")
    if "public Vector4 border { get; }" not in dump_text or "public float pixelsPerUnit { get; }" not in dump_text or "public Vector2 pivot { get; }" not in dump_text:
        raise ValueError("Sprite public metadata API declarations changed")
    if "public Vector2 size { get; set; }" not in dump_text:
        raise ValueError("SpriteRenderer size API declaration changed")

    sprites = _dict_map(sprite_contract["sprites"], lambda s: key_of(s["identity"]), "Sprite contract")
    geometry = _dict_map(resolved["sprites"], lambda g: (normalize_asset(g["serialized_file"]), int(g["path_id"])), "resolved Sprite")
    for key, sprite in sprites.items():
        geo = geometry.get(key)
        if geo is None or geo.get("object_bytes_sha256") != sprite["raw"].get("object_sha256"):
            raise ValueError(f"Sprite raw-object binding mismatch: {key}")

    mode_counts: Counter[str] = Counter()
    nonzero_by_mode: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    sliced_models = []
    tiled_models = []
    exclusions: list[dict] = []
    all_mode_rows = 0
    candidate_rows = []
    for renderer in scene["renderers"]:
        tree = renderer["renderer_tree"]
        mode = int(tree["m_DrawMode"])
        mode_counts[str(mode)] += 1
        if mode not in (1, 2):
            continue
        all_mode_rows += 1
        sprite_ref = renderer.get("sprite")
        if not sprite_ref:
            raise ValueError(f"draw-mode renderer has null sprite: {renderer['identity']}")
        key = key_of(sprite_ref)
        sprite = sprites.get(key)
        geo = geometry.get(key)
        if sprite is None or geo is None:
            raise ValueError(f"draw-mode renderer has unresolved Sprite: {renderer['identity']}")
        border = _validate_border(sprite)
        nonzero = any(border)
        route_counts["direct_unpacked" if _direct_unpacked(geo) else "atlas_or_other"] += 1
        if nonzero:
            nonzero_by_mode[str(mode)] += 1
        candidate_rows.append((renderer, sprite, geo, mode, nonzero))

    for renderer, sprite, geo, mode, nonzero in candidate_rows:
        direct = _direct_unpacked(geo)
        if mode == 1 and nonzero:
            if not direct:
                exclusions.append({"renderer": renderer["identity"], "renderer_name": renderer["name"], "reason": "packed_or_atlas_route_outside_direct-texture-model"})
                continue
            size = renderer["renderer_tree"]["m_Size"]
            left, bottom, right, top = _validate_border(sprite)
            ppu = float(sprite["pixels_to_units"])
            if float(size["x"]) + EPS < (left + right) / ppu or float(size["y"]) + EPS < (bottom + top) / ppu:
                exclusions.append({
                    "renderer": renderer["identity"],
                    "renderer_name": renderer["name"],
                    "sprite_name": sprite["name"],
                    "requested_size": size,
                    "fixed_border_units_lbrt": [left / ppu, bottom / ppu, right / ppu, top / ppu],
                    "reason": "requested_size_below_fixed_border_sum_no_shrink_policy_assumed",
                })
                continue
            sliced_models.append(_slice_model(renderer, sprite, geo))
        elif mode == 2:
            if nonzero:
                exclusions.append({"renderer": renderer["identity"], "renderer_name": renderer["name"], "reason": "bordered_tiled_case_not_in_scoped_source"})
            elif not direct:
                exclusions.append({"renderer": renderer["identity"], "renderer_name": renderer["name"], "reason": "packed_or_atlas_route_outside_direct-tile-model"})
            else:
                tiled_models.append(_tile_model(renderer, sprite, geo))
        elif mode == 1 and not nonzero:
            exclusions.append({"renderer": renderer["identity"], "renderer_name": renderer["name"], "reason": "zero_border_sliced_instance_outside_primary_nonzero-border-case"})

    summary = {
        "source_scene_sprite_renderers": len(scene["renderers"]),
        "draw_mode_code_counts": dict(sorted(mode_counts.items())),
        "sliced_mode_code": 1,
        "tiled_mode_code": 2,
        "sliced_instances": mode_counts["1"],
        "tiled_instances": mode_counts["2"],
        "sliced_nonzero_border_instances": nonzero_by_mode["1"],
        "tiled_nonzero_border_instances": nonzero_by_mode["2"],
        "direct_unpacked_nonzero_border_sliced_modelled": len(sliced_models),
        "direct_unpacked_borderless_tiled_modelled": len(tiled_models),
        "excluded_instances": len(exclusions),
        "unique_sprite_objects_in_models": len({(m["sprite"]["serialized_file"], m["sprite"]["path_id"]) for m in sliced_models + tiled_models}),
    }
    if summary["source_scene_sprite_renderers"] != 1377 or summary["sliced_instances"] != 441 or summary["tiled_instances"] != 14:
        raise ValueError("serialized scene draw-mode inventory changed")
    if summary["sliced_nonzero_border_instances"] != 236 or summary["tiled_nonzero_border_instances"] != 0:
        raise ValueError("serialized scene border inventory changed")
    if summary["direct_unpacked_nonzero_border_sliced_modelled"] != 112 or summary["direct_unpacked_borderless_tiled_modelled"] != 10:
        raise ValueError("bounded model coverage changed")

    return {
        "schema_version": 1,
        "task": "#5 border-aware sliced/tiled SpriteRenderer geometry model",
        "status": "BOUNDED_STATIC_REPLICATION_MODEL_NOT_NATIVE_GENERATOR_OR_RUNTIME",
        "replication": {
            "label": "REPLICATION",
            "source_branch": PEER_BRANCH,
            "source_commit": PEER_COMMIT,
            "scope": "Independent deterministic model over pinned serialized scene/Sprite receipts; not clean-room APK extraction and not Unity engine execution.",
            "source_identity_sha256": APK_INPUTS,
        },
        "model_policy": {
            "border_vector": "Interpret m_Border Vector4 xyzw as left,bottom,right,top for the geometric model; the dump exposes Vector4 but native renderer component consumption is not recovered.",
            "pivot": "Place requested m_Size bounds around the normalized Sprite pivot: x=[-pivot.x*size.x,(1-pivot.x)*size.x], y=[-pivot.y*size.y,(1-pivot.y)*size.y].",
            "sliced": "Create a 4x4 grid from fixed border pixel widths divided by pixelsToUnits; interpolate the center region. No scale-down rule is guessed when fixed border sums exceed requested size.",
            "uv": "Direct, unpacked sprites only; use textureRect/texture dimensions and border pixel cuts. Atlas/packed routes are reported as exclusions, not silently flattened.",
            "tiled": "For observed borderless direct tiled rows only, repeat at sourceRect/pixelsToUnits and clip a partial terminal tile against m_Size. This is an explicit model policy, not native SpriteTileMode semantics.",
            "topology": "Grid vertices in top-row-first order; each quad indices [top-left,top-right,bottom-left,bottom-left,top-right,bottom-right], matching the negative-XY winding convention of the pinned serialized Sprite meshes.",
        },
        "summary": summary,
        "source_pins": {path: sha256(data) for path, data in archived.items()},
        "source_content_pins": {path: sha256(data) for path, data in contents.items()},
        "scene_source_chunks": scene["sources"]["chunks"],
        "sprite_source_chunks": source_index["files"],
        "outputs": {"sliced": sliced_models, "tiled": tiled_models, "excluded": exclusions},
        "limits": [
            "All inputs are static serialized-data receipts from the pinned 1.3.118 source build; the model is not a native SpriteRenderer implementation.",
            "No SpriteRenderer generated-mesh runtime readback, Unity execution, screenshot, redraw, or render acceptance was used.",
            "Only direct/unpacked texture mappings are modeled. Atlas-backed nonzero-border sliced and tiled rows are explicitly excluded; this does not settle atlas remap (#6).",
            "The serialized scene has no nonzero-border tiled rows. The tiled output models only the ten direct, borderless instances and does not claim bordered tiled behavior.",
            "One direct nonzero-border sliced instance has requested width zero below its fixed border sum and is rejected; no undocumented border shrink rule is invented.",
            "Vector4 border component-to-side interpretation and pivot anchoring are explicit model conventions, not verified native method semantics.",
            "The model's triangle ordering/winding is a consistent grid output and is not proof of the native renderer's emitted index buffer.",
            "Serialized source counts describe these four scene files, not all prefabs, runtime-created renderers, or every SpriteRenderer in the APK.",
        ],
    }


def build_file(check: bool = False) -> bytes:
    data = gzip.compress(canonical(build()), mtime=0)
    if check:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != data:
            raise SystemExit("artifact differs; rebuild with this tool")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_file(check=args.check)
    print(f"artifact_bytes={len(data)} sha256={sha256(data)}")


if __name__ == "__main__":
    main()
