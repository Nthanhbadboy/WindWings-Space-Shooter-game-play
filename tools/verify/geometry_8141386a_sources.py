"""Branch-owned, narrow #5 source selection. Never rewrites peer capture/artifacts.
provenance: arena/8141386a-windwings-space-shooter-game-p
Raw102/Graph are shared, already handed-off evidence, not a second APK parser.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from tools.verify.l3_chain_graph import ROOT, identity, key
from tools.verify.l3_visual_surface import read_source

BRANCH = "arena/8141386a-windwings-space-shooter-game-p"
RAW = ROOT / "reverse-engineering/raw/geometry-8141386a"
SELECTED = RAW / "selected-inputs.json.gz"
QUERY = RAW / "byte-queries.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def select():
    index, graph, locations, _ = read_source()
    kept = {}
    used_paths = {"reverse-engineering/raw/l3-visual-surface/index.json"}

    def keep(k):
        if k not in graph.rows:
            raise ValueError(f"uncaptured object: {k}")
        kept[k] = graph.rows[k]
        used_paths.add(locations[k]["path"])
        return graph.rows[k]

    cases = []
    root = ("data.unity3d/level2", 5739)
    targets = [root] + sorted(k for k, r in graph.rows.items()
                              if r["type"] == "SpriteRenderer" and r["tree"]["m_DrawMode"] == 2)
    for renderer in targets:
        row = keep(renderer)
        sprite = graph.target(renderer, ".m_Sprite")
        if sprite is None:
            raise ValueError("selected renderer has no resolved sprite")
        s = keep(sprite)
        atlas = graph.target(sprite, ".m_SpriteAtlas")
        if atlas is not None:
            a = keep(atlas)
            matches = [(i, rd) for i, (render_key, rd) in enumerate(a["tree"]["m_RenderDataMap"])
                       if render_key == s["tree"]["m_RenderDataKey"]]
            if len(matches) != 1:
                raise ValueError("non-unique exact SpriteAtlas render key")
            slot, render_data = matches[0]
            texture = graph.target(atlas, f".m_RenderDataMap[{slot}][1].texture")
        else:
            slot = None
            render_data = s["tree"]["m_RD"]
            texture = graph.target(sprite, ".m_RD.texture")
        if texture is None:
            raise ValueError("selected sprite has no resolved source texture")
        tex = keep(texture)
        cases.append(dict(renderer=identity(renderer), sprite=identity(sprite), atlas=identity(atlas),
                          render_key_slot=slot, texture=identity(texture), render_data=render_data,
                          texture_size=[tex["width"], tex["height"]],
                          role="nonzero_border_root" if renderer == root else "serialized_tiled_renderer",
                          source_context="serialized_scene" if renderer[0].endswith("/level2")
                          else "asset_template_NOT_placed"))
    pins = {p: sha((ROOT / p).read_bytes()) for p in sorted(used_paths)}
    result = dict(schema=1, provenance=BRANCH,
                  lineage=dict(branch="arena/ef6b75ef-windwings-space-shooter-game-p",
                               source_tree="f5a447c15a117ca4571e2768f0274d1ad4f20b39",
                               handoff_comment=6403986603, report=102,
                               note="Shared UnityPy capture and Graph reference resolution; not independent APK parsing"),
                  xapk_sha256=index["xapk_sha256"], payload_inputs=index["inputs"], source_chunk_pins=pins,
                  records=[dict(identity=identity(k), raw_location=locations[k], record=kept[k])
                           for k in sorted(kept)], cases=cases)
    # Source recovery is limited to the concrete non-zero-border root chain. Other tiled
    # cases retain raw102 object pins; do NOT advertise fresh byte recovery for them.
    first = cases[0]
    wanted = [(key(first[n]), n) for n in ("renderer", "sprite", "atlas", "texture")]
    queries = dict(schema=1, provenance=BRANCH, xapk_sha256=index["xapk_sha256"],
                   objects=[dict(identity=identity(k), role=role, class_id=kept[k]["class_id"],
                                 expected_object_sha256=kept[k]["raw_object_sha256"],
                                 capture="sprite_prefix_fields" if role == "sprite" else "hash_only")
                            for k, role in wanted])
    return result, queries


def verify_pins(value):
    for name, expected in value["source_chunk_pins"].items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("source pin mismatch: " + name)
    for item in value["records"]:
        loc = item["raw_location"]
        rows = gzip.decompress((ROOT / loc["path"]).read_bytes()).splitlines()
        if json.loads(rows[loc["row"]]) != item["record"]:
            raise ValueError("selected row differs from pinned raw capture")
        if key(item["identity"]) != key(item["record"]):
            raise ValueError("identity disagreement")


def load():
    value = json.loads(gzip.decompress(SELECTED.read_bytes()))
    verify_pins(value)
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    value, queries = select()
    outputs = {SELECTED: gzip.compress(canonical(value), mtime=0), QUERY: canonical(queries)}
    for path, body in outputs.items():
        if args.check:
            if not path.exists() or path.read_bytes() != body:
                raise SystemExit("selection drift: " + str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    print(f"{len(value['cases'])} selected renderer cases, {len(value['records'])} pinned objects")


if __name__ == "__main__":
    main()
