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
            if cls and code.endswith(";") and "(" not in code and "=" not in code:
                toks = code[:-1].split()
                if len(toks) >= 3 and toks[0] in MODIFIERS:
                    body = [t for t in toks if t not in MODIFIERS]
                    if len(body) >= 2:
                        out[f"{cls}.{body[-1]}"] = " ".join(body[:-1])
    return out


def read_str(blob, str_off, idx):
    if idx < 0:
        return "?"
    end = blob.find(b"\x00", str_off + idx)
    if end < 0:
        return "?"
    return blob[str_off + idx:end].decode("utf-8", "replace")


def parse_types(blob, header):
    """Trả [(class_name, field_start, field_count)] + tổng số field metadata."""
    td_off, td_size = header["typeDefinitions"]
    f_off, f_size = header["fields"]
    str_off, _ = header["string"]
    n_fields = f_size // 12
    best = None
    for size in (84, 88, 92, 104, 112, 116):
        if td_size % size:
            continue
        n = td_size // size
        try:
            ok, prev_max = 0, -1
            for i in range(min(n, 4000)):
                base = td_off + i * size
                field_start, field_count = struct.unpack_from("<iH", blob, base + 28)
                nm = struct.unpack_from("<i", blob, base)[0]
                if field_start < prev_max - 0 or field_count > 400:
                    break
                if 0 <= nm < header["string"][1]:
                    ok += 1
                prev_max = max(prev_max, field_start)
            score = ok
        except struct.error:
            score = -1
        if best is None or score > best[0]:
            best = (score, size, n)
    _score, size, n = best
    print(f"typeDefinitions: {n} types, struct size {size} (score {_score}); "
          f"metadata fields: {n_fields}")
    types = []
    for i in range(n):
        base = td_off + i * size
        name_idx = struct.unpack_from("<i", blob, base)[0]
        field_start, field_count = struct.unpack_from("<iH", blob, base + 28)
        types.append((read_str(blob, str_off, name_idx), field_start, field_count))
    return types, n_fields, (f_off, str_off)


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

    types, _n_fields, (f_off, str_off) = parse_types(blob, header)
    # fieldIndex toàn cục -> "Class.field" + tên field (từ section fields)
    index2name = {}
    for cls_name, start, count in types:
        if start < 0:
            continue
        for k in range(count):
            fidx = start + k
            name_idx = struct.unpack_from("<i", blob, f_off + fidx * 12)[0]
            index2name[fidx] = f"{cls_name}.{read_str(blob, str_off, name_idx)}"

    types_by_name = dump_field_types(dump_path) if os.path.isfile(dump_path) else {}
    print(f"dump.cs field types: {len(types_by_name)}; mapped indices: {len(index2name)}")

    result, skipped, reasons = {}, 0, {}
    for i in range(0, fdv_size - 11, 12):
        field_idx, _type_idx, data_idx = struct.unpack_from("<iii", blob, fdv_off + i)
        key = index2name.get(field_idx)
        if key is None or data_idx < 0:
            skipped += 1
            reasons["no-name"] = reasons.get("no-name", 0) + 1
            continue
        typ = types_by_name.get(key)
        if typ is None:
            skipped += 1
            reasons["no-dump-type"] = reasons.get("no-dump-type", 0) + 1
            continue
        value = decode(typ, data, data_idx)
        if value is None:
            skipped += 1
            reasons["decode"] = reasons.get("decode", 0) + 1
            continue
        result[key] = {"type": typ, "value": value, "data_index": data_idx}
    print(f"decoded: {len(result)}, skipped: {skipped} {reasons}")

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
