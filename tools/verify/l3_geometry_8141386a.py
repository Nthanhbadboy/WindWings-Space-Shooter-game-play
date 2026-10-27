"""#5 metadata-driven sliced/tiled generator + provenance and original-byte witnesses.
provenance: arena/8141386a-windwings-space-shooter-game-p
No imports of a5a74747's in-progress generator. No peer files are modified.
"""
from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter

from tools.verify.geometry_8141386a_sources import ROOT, RAW, SELECTED, BRANCH, canonical, sha, load
from tools.verify.l3_chain_graph import key
from tools.verify.l3_geometry_8141386a_math import sliced, tiled, UnsupportedGeometry

OUT = ROOT / "datas/l3_geometry_bounds.json.gz"
WITNESS = RAW / "byte-witness.json.gz"


def specification(selected, case):
    rows = {key(r["identity"]): r["record"] for r in selected["records"]}
    renderer = rows[key(case["renderer"])]
    sprite = rows[key(case["sprite"])]
    st, rd = sprite["tree"], case["render_data"]
    source = dict(source_rect_px=[st["m_Rect"][c] for c in ("width", "height")],
                  border_px_lbrt=[st["m_Border"][c] for c in "xyzw"],
                  pixels_per_unit=st["m_PixelsToUnits"],
                  pivot_normalized=[st["m_Pivot"][c] for c in "xy"],
                  sprite_offset_px=[st["m_Offset"][c] for c in "xy"],
                  trim_offset_px=[rd["textureRectOffset"][c] for c in "xy"],
                  texture_rect_px=[rd["textureRect"][c] for c in ("x", "y", "width", "height")],
                  texture_size=case["texture_size"], settings_raw=rd["settingsRaw"],
                  downscale_multiplier=rd["downscaleMultiplier"],
                  uv_transform_xyzw=[rd["uvTransform"][c] for c in "xyzw"])
    t = renderer["tree"]
    request = dict(size=[t["m_Size"][c] for c in "xy"], draw_mode=t["m_DrawMode"],
                   tile_mode=t["m_SpriteTileMode"], adaptive_threshold=t["m_AdaptiveModeThreshold"],
                   flip=[t["m_FlipX"], t["m_FlipY"]])
    evidence = dict(renderer=case["renderer"], sprite=case["sprite"], sprite_name=st["m_Name"],
                    atlas=case["atlas"], texture=case["texture"],
                    serialized_render_key=st.get("m_RenderDataKey"), exact_render_key_slot=case["render_key_slot"],
                    raw_object_sha256={role:rows[key(case[role])]["raw_object_sha256"]
                                       for role in ("renderer", "sprite", "atlas", "texture") if case[role]},
                    raw_locations={role:next(r["raw_location"] for r in selected["records"]
                                             if key(r["identity"]) == key(case[role]))
                                   for role in ("renderer", "sprite", "atlas", "texture") if case[role]},
                    source_uv0_kept_not_used=sprite.get("geometry", {}).get("m_UV0"),
                    source_context=case["source_context"], role=case["role"])
    return source, request, evidence


def byte_witness(selected, required=True):
    if not WITNESS.exists():
        if required:
            raise ValueError("original-source byte witness pending: run branch-owned recovery CI")
        return dict(status="PENDING_SOURCE_RECOVERY_NOT_A_COMPLETED_HANDOFF")
    value = json.loads(gzip.decompress(WITNESS.read_bytes()))
    if value["provenance"] != BRANCH or value["xapk_sha256"] != selected["xapk_sha256"]:
        raise ValueError("byte witness source/provenance mismatch")
    for path, digest in value["tool_pins"].items():
        if sha((ROOT/path).read_bytes()) != digest:
            raise ValueError("recovery tool/query pin mismatch: "+path)
    rows = {key(r["identity"]):r["record"] for r in selected["records"]}
    for r in value["objects"]:
        if rows[key(r["identity"])]["raw_object_sha256"] != r["object_sha256"]:
            raise ValueError("recovered original object differs from raw102")
    sprite = next(r for r in value["objects"] if r["role"] == "sprite")
    st = rows[key(sprite["identity"])]["tree"]
    from tools.recovery.geometry_8141386a_bytes import sprite_prefix
    prefix = sprite_prefix(bytes.fromhex(sprite["prefix"]["prefix_hex"]))
    if prefix != sprite["prefix"]:
        raise ValueError("stored byte-field witness cannot be decoded back exactly")
    expected = dict(m_Rect=[st["m_Rect"][c] for c in ("x","y","width","height")],
                    m_Offset=[st["m_Offset"][c] for c in "xy"],
                    m_Border=[st["m_Border"][c] for c in "xyzw"],
                    m_PixelsToUnits=[st["m_PixelsToUnits"]],
                    m_Pivot=[st["m_Pivot"][c] for c in "xy"])
    if prefix["name"] != st["m_Name"] or any(prefix["fields"][n]["values"] != v for n,v in expected.items()):
        raise ValueError("source byte floats differ from serialized metadata")
    return dict(status="FRESH_ORIGINAL_BYTES_CORROBORATE_CAPTURED_FIELDS", receipt_sha256=sha(WITNESS.read_bytes()),
                xapk_sha256=value["xapk_sha256"], bundle_sha256=value["bundle_sha256"],
                apk_sha256=value["apk_sha256"], objects=value["objects"], files=value["files"],
                decoded_blocks=len(value["block_receipts"]),
                limit="Shared ef111/110 framing, typed-prefix layout seeded raw102; not independently discovered schema or native renderer execution")


def generate(source, request):
    if request["draw_mode"] == 1:
        return sliced(source, request["size"], flip=request["flip"])
    if request["draw_mode"] == 2:
        return tiled(source, request["size"], tile_mode=request["tile_mode"], flip=request["flip"],
                     adaptive_threshold=request["adaptive_threshold"])
    raise UnsupportedGeometry("only serialized sliced1/tiled2 accepted; no replacement simple quad")


def build(require_witness=True):
    selected = load()
    cases = []
    for case in selected["cases"]:
        source, request, evidence = specification(selected, case)
        try:
            geometry = generate(source, request)
        except UnsupportedGeometry as exc:
            geometry = dict(status="not_generated", reason=str(exc), vertices=None, uvs=None, indices=None)
        cases.append(dict(evidence=evidence, source=source, request=request, geometry=geometry))
    root = cases[0]
    if key(root["evidence"]["renderer"]) != ("data.unity3d/level2",5739) or root["geometry"]["status"] == "not_generated":
        raise ValueError("concrete non-zero-border root must be generated, not silently skipped")
    # Explicit tests of model boundaries; NOT additional observed renderer states.
    experiments = []
    for name, size, mode in (("compressed_borders",[.4,.2],1), ("partial_nonzero_border_tiles",[1.13,.77],2)):
        req = dict(root["request"], size=size, draw_mode=mode)
        experiments.append(dict(name=name, evidence_level="EXPLICIT_SYNTHETIC_REQUEST_USING_PINNED_SPRITE_NOT_RUNTIME", request=req,
                                source=root["evidence"]["sprite"], geometry=generate(root["source"],req)))
    inputs = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in
              [SELECTED, ROOT/"tools/verify/geometry_8141386a_sources.py",
               ROOT/"tools/verify/l3_geometry_8141386a.py",ROOT/"tools/verify/l3_geometry_8141386a_math.py"]}
    if WITNESS.exists():
        inputs[str(WITNESS.relative_to(ROOT))] = sha(WITNESS.read_bytes())
    return dict(schema=1, provenance=BRANCH, item=5, disposition="BOUNDED_METADATA_DRIVEN_MODEL_WITH_SOURCE_BYTE_PROOF",
                independent_replication_of_item=True,
                independence_limit="Independent implementation vs a5a74747 #5, shared raw102 capture/Graph with ef6b75ef. No second native/API implementation.",
                lineage=selected["lineage"], xapk_sha256=selected["xapk_sha256"], inputs=inputs,
                source_chunk_pins=selected["source_chunk_pins"], byte_witness=byte_witness(selected,require_witness),
                counts=dict(cases=len(cases), serialized_draw_modes=dict(Counter(str(c["request"]["draw_mode"]) for c in cases)),
                            statuses=dict(Counter(c["geometry"]["status"] for c in cases)),
                            generated_vertices=sum(len(c["geometry"]["vertices"] or []) for c in cases),
                            generated_triangles=sum(len(c["geometry"].get("triangles",[])) for c in cases),
                            synthetic_requests=len(experiments)),
                cases=cases, experiments=experiments,
                boundaries=["Metadata border/PPU/pivot/UV entry corroborated with original source bytes for root chain, not readback of generated topology.",
                            "Atlas map is exact serialized source entry, NOT live atlas overrides/remap (#6 separate).",
                            "Sliced compression/continuous tile tail clipping/topology order are explicit CPU model policies; native SpriteRenderer generator not recovered/executed.",
                            "Adaptive mode, trimmed/downscaled/rotated/tight atlas entries and excessive tile counts reject explicitly; no guessed geometry.",
                            "No automatic write to peer Frame103/104, no camera/visibility/shader/render claim, no screenshot gate.",
                            "To prove engine-exact topology/compression/repetition needs pinned libunity generator entry/callees or approved same-build vertex/UV/index readback; serialized inputs alone cannot decide native implementation."])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--allow-pending-witness", action="store_true", help="Diagnostic only, never a final handoff")
    args = parser.parse_args()
    result = build(not args.allow_pending_witness)
    body = gzip.compress(canonical(result),mtime=0)
    if args.check:
        if not OUT.exists() or OUT.read_bytes() != body:
            raise SystemExit("artifact drift: "+str(OUT))
    else:
        OUT.write_bytes(body)
    print(json.dumps(result["counts"],sort_keys=True))
    print("sha256",sha(body),"bytes",len(body),"provenance",BRANCH)


if __name__ == "__main__":
    main()
