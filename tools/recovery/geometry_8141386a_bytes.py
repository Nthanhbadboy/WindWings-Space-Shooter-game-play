"""Read-only, cached-original #5 prefix/byte witness. No UnityPy, media export or APK mods.
provenance: arena/8141386a-windwings-space-shooter-game-p
Reuses ef's handed-off UnityFS/SerializedFile readers, explicitly NOT independent framing.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.verify.serialized110_binary import header, parse
from tools.verify.unityfs111_binary import framing, block_bytes

BRANCH = "arena/8141386a-windwings-space-shooter-game-p"
RAW = ROOT / "reverse-engineering/raw/geometry-8141386a"
XAPK_SHA = "f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e"
DATA_SHA = "7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def sprite_prefix(blob):
    if len(blob) < 4:
        raise ValueError("truncated name length")
    length = struct.unpack_from("<i", blob)[0]
    if not 0 <= length <= 4096 or 4 + length > len(blob):
        raise ValueError("invalid name length")
    name = blob[4:4+length].decode("utf-8")
    pos = (4 + length + 3) // 4 * 4
    fields = {}
    for field, count in (("m_Rect", 4), ("m_Offset", 2), ("m_Border", 4),
                         ("m_PixelsToUnits", 1), ("m_Pivot", 2)):
        stop = pos + 4 * count
        if stop > len(blob):
            raise ValueError("truncated sprite prefix")
        part = blob[pos:stop]
        fields[field] = dict(offset=pos, size=len(part), hex=part.hex(),
                             values=list(struct.unpack("<" + "f" * count, part)), sha256=sha(part))
        pos = stop
    return dict(name=name, fields=fields, prefix_hex=blob[:pos].hex(), prefix_sha256=sha(blob[:pos]),
                layout_scope="Selected Sprite prefix field order seeded from captured typetree; not independent schema discovery")


def recover(path):
    if sha(path.read_bytes()) != XAPK_SHA:
        raise ValueError("original XAPK mismatch")
    bundles = []
    with zipfile.ZipFile(path) as outer:
        for member in sorted(outer.namelist()):
            if not member.endswith(".apk"):
                continue
            apk = outer.read(member)
            with zipfile.ZipFile(io.BytesIO(apk)) as inner:
                target = "assets/bin/Data/data.unity3d"
                if target in inner.namelist():
                    data = inner.read(target)
                    bundles.append((member, sha(apk), data))
    if len(bundles) != 1 or sha(bundles[0][2]) != DATA_SHA:
        raise ValueError("missing/non-unique original data.unity3d")
    apk_name, apk_sha, blob = bundles[0]
    frame = framing(blob)
    cache, receipts = {}, {}

    def read(offset, size):
        if not 0 <= offset <= offset + size <= frame["uncompressed_size"]:
            raise ValueError("range outside UnityFS logical file")
        out = []
        for b in frame["blocks"]:
            start = b["uncompressed_start"]
            if offset < start+b["uncompressed_size"] and start < offset+size:
                if b["index"] not in cache:
                    packed = blob[b["physical_start"]:b["physical_start"]+b["compressed_size"]]
                    cache[b["index"]] = block_bytes(blob, b)
                    receipts[b["index"]] = dict(**b, compressed_sha256=sha(packed),
                                                 decoded_sha256=sha(cache[b["index"]]))
                block = cache[b["index"]]
                out.append(block[max(0, offset-start):min(len(block), offset+size-start)])
        value = b"".join(out)
        if len(value) != size:
            raise ValueError("range consumption mismatch")
        return value

    query = json.loads((RAW / "byte-queries.json").read_bytes())
    if query["provenance"] != BRANCH or query["xapk_sha256"] != XAPK_SHA:
        raise ValueError("query provenance/source disagreement")
    tables, files, objects = {}, [], []
    for q in query["objects"]:
        file = q["identity"]["serialized_file"]
        if file not in tables:
            node = next(n for n in frame["nodes"] if "data.unity3d/"+n["path"] == file)
            h = header(read(node["offset"], 48))
            prefix = read(node["offset"], h["data_offset"])
            table = parse(prefix)
            if h["file_size"] != node["size"] or h["endian"] != "<":
                raise ValueError("unsupported source file")
            tables[file] = node, table
            files.append(dict(serialized_file=file, node=node, header=h, metadata_prefix_sha256=sha(prefix),
                              metadata_size=len(prefix), object_count=len(table["objects"])))
        node, table = tables[file]
        r = next(r for r in table["objects"] if r["path_id"] == q["identity"]["path_id"])
        if r["class_id"] != q["class_id"]:
            raise ValueError("source class mismatch")
        value = read(node["offset"]+r["byte_start"], r["byte_size"])
        if sha(value) != q["expected_object_sha256"]:
            raise ValueError("source object SHA differs from raw102")
        result = dict(identity=q["identity"], role=q["role"], object_table_entry=r,
                      logical_start=node["offset"]+r["byte_start"], object_sha256=sha(value),
                      fresh_source_sha_matches_raw102=True)
        if q["capture"] == "sprite_prefix_fields":
            result["prefix"] = sprite_prefix(value)
        objects.append(result)
    pin_paths = ["tools/recovery/geometry_8141386a_bytes.py", "tools/verify/serialized110_binary.py",
                 "tools/verify/unityfs111_binary.py", "reverse-engineering/raw/geometry-8141386a/byte-queries.json"]
    result = dict(schema=1, provenance=BRANCH, xapk_sha256=XAPK_SHA, bundle_sha256=DATA_SHA,
                  apk_member=apk_name, apk_sha256=apk_sha, files=files, objects=objects,
                  block_receipts=[receipts[i] for i in sorted(receipts)],
                  tool_pins={p:sha((ROOT/p).read_bytes()) for p in pin_paths},
                  scope="Fresh original-source object hashes + narrow Sprite prefix bytes. No renderer generator/native execution, Unity readback or render.",
                  lineage="UnityFS111/Serialized110 are shared ef6b75ef readers; schema field ordering is seeded from raw102, not clean-room.")
    body = (json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n").encode()
    (RAW/"byte-witness.json.gz").write_bytes(gzip.compress(body, mtime=0))
    print(f"Fresh source: {len(objects)} object hashes, {len(receipts)} decoded blocks; original bytes unchanged", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xapk", type=Path, required=True)
    args = parser.parse_args()
    recover(args.xapk)
