#!/usr/bin/env python3
"""Giá trị mặc định của field (kể cả mảng literal) từ global-metadata.dat.

Các bảng như map->wave không nằm hết trong .so: một phần là field có giá trị
mặc định / RVA data trong vùng fieldDefaultValueData của global-metadata.dat.
Tool này parse thẳng metadata (v31 đã gặp thực tế):

  header -> fieldDefaultValues {fieldIndex, typeIndex, dataIndex}
  typeDefinitions (fieldStart/fieldCount) + fields (nameIndex) + string blob
    -> ánh xạ fieldIndex toàn cục về "Class.field" không cần dump.cs.

Kiểu của field lấy từ dump.cs theo tên (chỉ để giải mã blob); field nào không
tìm thấy kiểu tương thích sẽ bị bỏ qua và đếm riêng.

Dùng: python3 field_defaults.py <global-metadata.dat> <dump.cs> [out.json]
"""
from __future__ import annotations

import json
import os
import re
import struct
import sys

HEADER_FIELDS = [
    "stringLiteral", "stringLiteralData", "string", "events", "properties",
    "methods", "parameterDefaultValues", "fieldDefaultValues",
    "fieldDefaultValueData", "fieldMarshaledSizes", "parameters", "fields",
    "genericParameters", "genericParameterConstraints", "genericContainers",
    "nestedTypes", "interfaces", "vtableMethods", "interfaceOffsets",
    "typeDefinitions", "images", "assemblies", "metadataUsageLists",
    "metadataUsagePairs", "fieldRefs", "referencedAssemblies",
    "attributesInfo", "attributeTypes",
    "unresolvedVirtualCallParameterTypes", "unresolvedVirtualCallParameterIndices",
    "windowsRuntimeTypeNames", "windowsRuntimeStrings",
    "exportedTypeDefinitions",
]

CLS_RE = re.compile(r"^(?:public|private|internal|protected)[\w ]*?\b(?:class|struct)\s+([\w.]+)")
MODIFIERS = {"private", "public", "protected", "internal", "static",
             "readonly", "volatile", "const", "new"}
TYPE_SIZES = {"int": ("i", 4), "uint": ("I", 4), "float": ("f", 4),
              "double": ("d", 8), "short": ("h", 2), "ushort": ("H", 2),
              "long": ("q", 8), "ulong": ("Q", 8), "byte": ("B", 1),
              "sbyte": ("b", 1), "bool": ("B", 1)}


def dump_field_types(dump_path):
    """{Class.field: type} từ dump.cs — chỉ để biết kiểu khi giải mã blob."""
    out, cls = {}, None
    with open(dump_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = CLS_RE.match(line)
            if m:
                cls = m.group(1)
                continue
            code = line.split("//")[0].strip()
            if cls and code.endswith(";") and "(" not in code:
                toks = code[:-1].split()
                if len(toks) >= 3 and toks[0] in MODIFIERS:
                    body = [t for t in toks if t not in MODIFIERS]
                    if "=" in body:
                        eq = body.index("=")
                        if eq >= 2:
                            out[f"{cls}.{body[eq - 1]}"] = " ".join(body[:eq - 1])
                    elif len(body) >= 2:
                        out[f"{cls}.{body[-1]}"] = " ".join(body[:-1])
    return out


def read_str(blob, str_off, idx):
    if idx < 0:
        return "?"
    end = blob.find(b"\x00", str_off + idx)
    if end < 0:
        return "?"
    return blob[str_off + idx:end].decode("utf-8", "replace")


IDENT_RE = re.compile(r"^[A-Za-z_<][\w<>.`]*$")


def parse_types(blob, header):
    """Trả [(class_name, field_start, field_count)] + tổng số field metadata.

    Tự hiệu chuẩn: thử mọi kích thước struct khả thi, chấm theo tỉ lệ tên
    type giải mã được thành định danh hợp lệ trong vùng string.
    """
    td_off, td_size = header["typeDefinitions"]
    f_off, f_size = header["fields"]
    str_off, str_size = header["string"]
    n_fields = f_size // 12
    print("header pairs: " + ", ".join(
        f"{k}={v[0]}/{v[1]}" for k, v in header.items()))
    best = None
    for size in range(76, 132, 4):
        if td_size % size:
            continue
        n = td_size // size
        total = min(n, 600)
        good = 0
        for i in range(total):
            nm = struct.unpack_from("<i", blob, td_off + i * size)[0]
            name = read_str(blob, str_off, nm) if 0 <= nm < str_size else "?"
            if IDENT_RE.match(name or ""):
                good += 1
        print(f"  struct size {size}: {n} types, ten hop le {good}/{total}")
        if best is None or good > best[0]:
            best = (good, size, n)
    _good, size, n = best
    print(f"typeDefinitions: {n} types, struct size {size}; "
          f"metadata fields: {n_fields}")
    # v31 (đã đọc từ dump thô): fieldStart = int32 @+32, fieldCount = u16 @+68
    # (16 int32 đầu, sau đó 8 u16: method/property/field/event/nested/vtable/
    #  interfaces/interfaceOffsets, rồi bitfield+token).
    fs_off, fc_off = 32, 68
    types = []
    for i in range(n):
        base = td_off + i * size
        name_idx = struct.unpack_from("<i", blob, base)[0]
        field_start = struct.unpack_from("<i", blob, base + fs_off)[0]
        field_count = struct.unpack_from("<H", blob, base + fc_off)[0]
        types.append((read_str(blob, str_off, name_idx), field_start, field_count))
    print(f"  tong fieldCount={sum(t[2] for t in types)} (metadata: {n_fields})")
    print(f"  sample type names: {[t[0] for t in types[:12]]}")
    return types, n_fields, (f_off, str_off, f_size)


def decode(typ, blob, pos):
    is_array = typ.endswith("[]")
    elem = typ[:-2] if is_array else typ
    if elem not in TYPE_SIZES:
        return None
    fmt, size = TYPE_SIZES[elem]
    try:
        if is_array:
            (count,) = struct.unpack_from("<i", blob, pos)
            if count < 0 or count > 5000:
                return None
            vals = list(struct.unpack_from(f"<{count}{fmt}", blob, pos + 4))
            if elem == "bool":
                vals = [bool(v) for v in vals]
            return vals
        (val,) = struct.unpack_from(f"<{fmt}", blob, pos)
        if elem == "bool":
            val = bool(val)
        if isinstance(val, float):
            val = round(val, 6)
        return val
    except (struct.error, OverflowError):
        return None


def main() -> int:
    meta_path = sys.argv[1]
    dump_path = sys.argv[2] if len(sys.argv) > 2 else "dump.cs"
    out_path = sys.argv[3] if len(sys.argv) > 3 else \
        "reverse-engineering/il2cpp/field-defaults.json"
    if not os.path.isfile(meta_path):
        print(f"missing {meta_path}")
        return 0
    blob = open(meta_path, "rb").read()
    _magic, version = struct.unpack_from("<ii", blob, 0)
    print(f"metadata version={version} size={len(blob)}")
    header = {}
    for i, name in enumerate(HEADER_FIELDS):
        header[name] = struct.unpack_from("<ii", blob, 8 + 8 * i)
    fdv_off, fdv_size = header["fieldDefaultValues"]
    data_off, data_size = header["fieldDefaultValueData"]
    data = blob[data_off:data_off + data_size]
    print(f"fieldDefaultValues entries={fdv_size // 12}; data={data_size} B")

    types, _n_fields, (f_off, str_off, f_size) = parse_types(blob, header)
    # fieldIndex toàn cục -> "Class.field" + tên field (từ section fields)
    index2name = {}
    for cls_name, start, count in types:
        if start < 0:
            continue
        for k in range(count):
            fidx = start + k
            if not (0 <= fidx * 12 + 4 <= f_size):
                continue
            name_idx = struct.unpack_from("<i", blob, f_off + fidx * 12)[0]
            index2name[fidx] = f"{cls_name}.{read_str(blob, str_off, name_idx)}"

    # metadataUsagePairs: {destinationIndex, encodedSourceIndex}; token trong
    # mã máy là (kind<<29)|index — thử truy ngược token 0x80000955 (2389).
    up_off, up_size = header["metadataUsagePairs"]
    pairs = [struct.unpack_from("<II", blob, up_off + 8 * i)
             for i in range(up_size // 8)]
    print(f"  usagePairs: {len(pairs)}; sample: {pairs[:5]}")
    for dest, enc in pairs:
        if dest == 2389 or enc == 0x80000955 or (enc & 0x1FFFFFFF) == 2389:
            print(f"  usage hit: dest={dest} enc={enc:#x} kind={enc >> 29} "
                  f"src={enc & 0x1FFFFFFF}")
    fr_off, fr_size = header["fieldRefs"]
    types_by_name = dump_field_types(dump_path) if os.path.isfile(dump_path) else {}
    print(f"dump.cs field types: {len(types_by_name)}; mapped indices: {len(index2name)}")

    entries = []
    for i in range(0, fdv_size - 11, 12):
        field_idx, _type_idx, data_idx = struct.unpack_from("<iii", blob, fdv_off + i)
        key = index2name.get(field_idx)
        if key is None or data_idx < 0:
            continue
        entries.append((data_idx, field_idx, key))
    entries.sort()
    result, skipped, reasons = {}, 0, {}
    for pos, (data_idx, field_idx, key) in enumerate(entries):
        nxt = entries[pos + 1][0] if pos + 1 < len(entries) else len(data)
        blob_bytes = data[data_idx:min(nxt, data_idx + 65536)]
        typ = types_by_name.get(key)
        value = decode(typ, data, data_idx) if typ else None
        entry = {"type": typ or "?", "data_index": data_idx,
                 "field_index": field_idx, "raw": blob_bytes.hex()}
        if value is not None:
            entry["value"] = value
        elif 0 <= data_idx <= len(data) - 4:
            entry["int32"] = struct.unpack_from("<i", data, data_idx)[0]
        if len(blob_bytes) % 4 == 0 and len(blob_bytes) >= 8:
            ints = list(struct.unpack(f"<{len(blob_bytes) // 4}i", blob_bytes))
            if all(-100000 <= v <= 100000000 for v in ints):
                entry["ints"] = ints
        result[key] = entry
    print(f"decoded: {len(result)}, skipped: {skipped} {reasons}")
    # Probe: token IA -> fieldRefs[src] = (typeIndex, fieldIndex-within-type)
    try:
        fr_off, fr_size = header["fieldRefs"]
        mj = json.load(open("reverse-engineering/raw/il2cpp-consts/"
                            "Map_Get_Datas.json", encoding="utf-8"))
        cc_m = next(m for m in mj["methods"] if m["method"] == "cctor")
        toks = [c for c in cc_m["constants"] if c.get("kind") == "init_array"]
        _pid = _len = _range = 0
        for c in toks:
            src = int(c["slot_val"], 16) & 0x1FFFFFFF
            if 8 * src + 8 > fr_size:
                continue
            ti, fi = struct.unpack_from("<ii", blob, fr_off + 8 * src)
            if 0 <= ti < len(types):
                _nm, _fs, _fc = types[ti]
                if 0 <= fi < _fc:
                    _range += 1
                    fname = index2name.get(_fs + fi, "?")
                    if fname.startswith("<PrivateImplementationDetails>"):
                        _pid += 1
                        ent = result.get(fname)
                        if ent and abs(len(bytes.fromhex(ent["raw"])) // 4
                                       - c["len"]) <= 3:
                            _len += 1
        print(f"  fieldRefs probe: hợp lệ {_range}/{len(toks)}, "
              f"PID {_pid}, khớp độ dài {_len}")
    except Exception as e:  # noqa: BLE001
        print(f"  fieldRefs probe lỗi: {e!r}")
    # Probe: token IA -> index field static (theo thứ tự dump.cs)
    try:
        static_fields = []
        _cls = None
        for _line in open(dump_path, encoding="utf-8", errors="replace"):
            _m = CLS_RE.match(_line)
            if _m:
                _cls = _m.group(1)
                continue
            _code = _line.split("//")[0].strip()
            if _cls and _code.endswith(";") and "(" not in _code:
                _toks = _code[:-1].split()
                if len(_toks) >= 3 and _toks[0] in MODIFIERS and "static" in _toks:
                    _name = _toks[-1]
                    if "=" in _toks:
                        _name = _toks[_toks.index("=") - 1]
                    static_fields.append(f"{_cls}.{_name}")
        mj = json.load(open("reverse-engineering/raw/il2cpp-consts/"
                            "Map_Get_Datas.json", encoding="utf-8"))
        cc_m = next(m for m in mj["methods"] if m["method"] == "cctor")
        toks = [c for c in cc_m["constants"] if c.get("kind") == "init_array"]
        _hit = _len = 0
        for c in toks:
            src = int(c["slot_val"], 16) & 0x1FFFFFFF
            if src < len(static_fields):
                nm2 = static_fields[src]
                if nm2.startswith("<PrivateImplementationDetails>"):
                    _hit += 1
                    ent = result.get(nm2)
                    if ent and abs(len(bytes.fromhex(ent["raw"])) // 4
                                   - c["len"]) <= 3:
                        _len += 1
        print(f"  static-index probe: {len(static_fields)} field static; "
              f"PID hit {_hit}/{len(toks)}, khớp độ dài {_len}")
    except Exception as e:  # noqa: BLE001
        print(f"  static probe lỗi: {e!r}")
    # Probe: field index tương đối theo image (Assembly-CSharp) cho token IA
    try:
        im_off, im_size = header["images"]
        str_off2, _ss = header["string"]
        images = []
        for i in range(im_size // 40):
            nm, _asm, tstart, tcount = struct.unpack_from("<iiii", blob, im_off + 40 * i)
            images.append((read_str(blob, str_off2, nm), tstart, tcount))
        map_t = next(i for i, t in enumerate(types) if t[0] == "Map_Get_Datas")
        img = next((im for im in images if im[1] <= map_t < im[1] + im[2]), None)
        print(f"  image của Map_Get_Datas (type {map_t}): {img}")
        if img:
            _nm, tstart, tcount = img
            base_field = sum(types[i][2] for i in range(tstart))
            rel = {}
            for i in range(tstart, tstart + tcount):
                nm_i, fs_i, fc_i = types[i]
                for k in range(fc_i):
                    rel[fs_i + k - base_field] = index2name.get(fs_i + k)
            mj = json.load(open("reverse-engineering/raw/il2cpp-consts/"
                                "Map_Get_Datas.json", encoding="utf-8"))
            cc_m = next(m for m in mj["methods"] if m["method"] == "cctor")
            toks = [c for c in cc_m["constants"] if c.get("kind") == "init_array"]
            by_name = result
            hit = pid_hit = 0
            for c in toks:
                src = int(c["slot_val"], 16) & 0x1FFFFFFF
                nm2 = rel.get(src)
                if nm2:
                    hit += 1
                    if nm2.startswith("<PrivateImplementationDetails>"):
                        ent = by_name.get(nm2)
                        if ent and abs(len(bytes.fromhex(ent["raw"])) // 4
                                       - c["len"]) <= 3:
                            pid_hit += 1
            print(f"  image-relative: {hit}/{len(toks)} có tên, "
                  f"{pid_hit} khớp blob PID (±3)")
    except Exception as e:  # noqa: BLE001
        print(f"  image probe lỗi: {e!r}")
    # Thử 4 giả thuyết ánh xạ token InitializeArray -> field, in 8 token đầu
    # của Map_Get_Datas..cctor dưới mỗi giả thuyết.
    try:
        mj = json.load(open("reverse-engineering/raw/il2cpp-consts/"
                            "Map_Get_Datas.json", encoding="utf-8"))
        cc_m = next(m for m in mj["methods"] if m["method"] == "cctor")
        toks = [c for c in cc_m["constants"] if c.get("kind") == "init_array"]
        srcs = [int(c["slot_val"], 16) & 0x1FFFFFFF for c in toks]
        fdv_by_field = sorted(result.items(), key=lambda kv: kv[1]["field_index"])
        pid_only = [(k, v) for k, v in fdv_by_field
                    if k.startswith("<PrivateImplementationDetails>")]
        print(f"  token probe: {len(toks)} token; src đầu {srcs[:8]}")
        for label, table in (
                ("global-field", None), ("fdv-by-field", fdv_by_field),
                ("pid-only", pid_only)):
            names = []
            for src in srcs[:8]:
                if table is None:
                    names.append(index2name.get(src, "?"))
                elif src < len(table):
                    names.append(table[src][0])
                else:
                    names.append("OOR")
            print(f"  [{label}] {names}")
    except Exception as e:  # noqa: BLE001
        print(f"  token probe lỗi: {e!r}")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"source": f"global-metadata.dat fieldDefaultValues v{version} "
                             "(typeDefinitions/fields/string sections)",
                   "count": len(result), "fields": result},
                  fh, ensure_ascii=False, indent=1)
    print(f"wrote {out_path} ({os.path.getsize(out_path)} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
