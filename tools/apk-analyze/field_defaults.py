#!/usr/bin/env python3
"""Giá trị mặc định của field (kể cả mảng literal) từ global-metadata.dat.

Các bảng như map->wave (`Map_Get_Datas.listMapDatas`) không nằm trong .so:
trong mã máy chúng là token metadata (0x80000xxx) trỏ vào vùng
fieldDefaultValueData của global-metadata.dat. Công cụ này đọc thẳng vùng đó:
header metadata v29 -> fieldDefaultValues {fieldIndex, typeIndex, dataIndex},
giải mã blob theo kiểu field lấy từ dump.cs (int[]/float[]/int/float/bool...).

Dùng: python3 field_defaults.py <global-metadata.dat> <dump.cs> [out.json]
Chỉ giữ field có giá trị mặc định; mảng cắt ở 5000 phần tử.
"""
from __future__ import annotations

import json
import os
import re
import struct
import sys

# Thứ tự cặp (offset,size) trong header metadata v24-v29 (sau magic+version).
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


def dump_fields(dump_path):
    """[(class, field, type)] theo đúng thứ tự metadata (chỉ số field toàn cục)."""
    out, cls = [], None
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
                    if len(body) >= 2:
                        out.append((cls, body[-1], " ".join(body[:-1])))
    return out


def decode(typ, blob, pos):
    """Giải một giá trị tại blob[pos]; trả (value, consumed) hoặc (None, 0)."""
    is_array = typ.endswith("[]")
    elem = typ[:-2] if is_array else typ
    if elem not in TYPE_SIZES:
        return None, 0
    fmt, size = TYPE_SIZES[elem]
    try:
        if is_array:
            (count,) = struct.unpack_from("<i", blob, pos)
            if count < 0 or count > 5000:
                return None, 0
            vals = list(struct.unpack_from(f"<{count}{fmt}", blob, pos + 4))
            if elem == "bool":
                vals = [bool(v) for v in vals]
            return vals, 4 + count * size
        (val,) = struct.unpack_from(f"<{fmt}", blob, pos)
        if elem == "bool":
            val = bool(val)
        if isinstance(val, float):
            val = round(val, 6)
        return val, size
    except (struct.error, OverflowError):
        return None, 0


def main() -> int:
    meta_path = sys.argv[1] if len(sys.argv) > 1 else sys.argv[0]
    dump_path = sys.argv[2] if len(sys.argv) > 2 else "dump.cs"
    out_path = sys.argv[3] if len(sys.argv) > 3 else \
        "reverse-engineering/il2cpp/field-defaults.json"
    if not os.path.isfile(meta_path):
        print(f"missing {meta_path}")
        return 0
    blob = open(meta_path, "rb").read()
    magic, version = struct.unpack_from("<ii", blob, 0)
    print(f"metadata magic={magic:#x} version={version} size={len(blob)}")
    header = {}
    for i, name in enumerate(HEADER_FIELDS):
        header[name] = struct.unpack_from("<ii", blob, 8 + 8 * i)
    fdv_off, fdv_size = header["fieldDefaultValues"]
    data_off, data_size = header["fieldDefaultValueData"]
    data = blob[data_off:data_off + data_size]
    print(f"fieldDefaultValues: off={fdv_off} size={fdv_size} "
          f"entries={fdv_size // 12}; fieldDefaultValueData: {data_size} B")

    fields = dump_fields(dump_path)
    print(f"fields in dump.cs: {len(fields)}")

    result = {}
    decoded, skipped = 0, 0
    for i in range(0, fdv_size - 11, 12):
        field_idx, _type_idx, data_idx = struct.unpack_from("<iii", blob, fdv_off + i)
        if not (0 <= field_idx < len(fields)) or data_idx < 0:
            skipped += 1
            continue
        cls, name, typ = fields[field_idx]
        value, _used = decode(typ, data, data_idx)
        if value is None:
            skipped += 1
            continue
        result[f"{cls}.{name}"] = {"type": typ, "value": value,
                                   "data_index": data_idx}
        decoded += 1
    print(f"decoded: {decoded}, skipped: {skipped}")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"source": "global-metadata.dat fieldDefaultValues (metadata v"
                             f"{version}) + dump.cs field order",
                   "count": len(result), "fields": result},
                  fh, ensure_ascii=False, indent=1)
    print(f"wrote {out_path} ({os.path.getsize(out_path)} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
