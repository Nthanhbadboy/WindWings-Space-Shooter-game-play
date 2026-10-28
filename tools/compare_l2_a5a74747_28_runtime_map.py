#!/usr/bin/env python3
"""Compare a RamusBridge Map_Get_Datas readback to static fallback ①.

The input must be the raw JSON response from
`/statics?type=Map_Get_Datas&max=200&arr=256&depth=2`.
This tool never creates runtime data: it only validates and compares a supplied
response. A missing/partial response remains NOT_OBSERVED, never a zero-filled map.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

DEFAULT_STATIC = Path("datas/l2_a5a74747_28_loader_fallback1.json.gz")


def expected_rows(static_path: Path = DEFAULT_STATIC) -> list[list[int]]:
    with gzip.open(static_path, "rt", encoding="utf-8") as stream:
        static = json.load(stream)
    rows = static["crosscheck"]["comparison_rows"]
    values = [row["values"] for row in rows]
    if len(values) != 250 or sum(map(len, values)) != 742:
        raise ValueError("pinned static fallback ① no longer contains 250 rows / 742 values")
    return values


def _int_value(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path}: expected an integer JSON scalar, got {type(value).__name__}")
    if not math.isfinite(value) or int(value) != value:
        raise ValueError(f"{path}: expected a finite integral value, got {value!r}")
    return int(value)


def compare(runtime: dict[str, Any], static_path: Path = DEFAULT_STATIC) -> dict[str, Any]:
    expected = expected_rows(static_path)
    fields = runtime.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("runtime response has no fields object")
    rows = fields.get("listMapDatas")
    if not isinstance(rows, list):
        raise ValueError("runtime fields.listMapDatas is missing or is not an array")
    if len(rows) != len(expected):
        raise ValueError(f"runtime outer row count {len(rows)} != static {len(expected)}")
    count = fields.get("listMapDatas_count")
    if count != len(expected):
        raise ValueError(f"runtime listMapDatas_count {count!r} != {len(expected)}")

    compared = []
    value_mismatches = []
    for i, (got_row, want_row) in enumerate(zip(rows, expected)):
        if not isinstance(got_row, list):
            raise ValueError(f"runtime row {i} is not an array")
        got = [_int_value(v, f"fields.listMapDatas[{i}][{j}]") for j, v in enumerate(got_row)]
        if len(got) != len(want_row):
            value_mismatches.append({"row": i, "kind": "length", "expected": len(want_row), "observed": len(got)})
        for j, (observed, expected_value) in enumerate(zip(got, want_row)):
            if observed != expected_value:
                value_mismatches.append({"row": i, "offset": j, "expected": expected_value, "observed": observed})
        compared.append({"index": i, "expected": want_row, "observed": got, "matches": got == want_row})

    result = {
        "schema": "windwings-runtime-map-crosscheck/v1",
        "static_reference": str(static_path),
        "static_reference_sha256": hashlib.sha256(static_path.read_bytes()).hexdigest(),
        "status": "RUNTIME_READBACK_MATCHES_STATIC" if not value_mismatches else "RUNTIME_READBACK_MISMATCH",
        "evidence_level": "RUNTIME_READBACK",
        "runtime_type": runtime.get("type"),
        "request": {"type": "Map_Get_Datas", "max": 200, "arr": 256, "depth": 2},
        "rows_compared": len(compared),
        "values_compared": sum(len(row["observed"]) for row in compared),
        "value_mismatch_count": len(value_mismatches),
        "all_rows_match": not value_mismatches,
        "mismatches": value_mismatches,
        "rows": compared,
    }
    if result["values_compared"] != 742:
        result["status"] = "RUNTIME_READBACK_INCOMPLETE"
        result["all_rows_match"] = False
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime_json", type=Path, help="raw JSON returned by RamusBridge /statics")
    parser.add_argument("--static", type=Path, default=DEFAULT_STATIC)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        runtime = json.loads(args.runtime_json.read_text(encoding="utf-8"))
        if not isinstance(runtime, dict) or runtime.get("ok") is not True:
            raise ValueError("runtime response does not declare ok=true")
        result = compare(runtime, args.static)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({k: result[k] for k in ("status", "rows_compared", "values_compared", "value_mismatch_count", "all_rows_match")}, sort_keys=True))
        return 0 if result["status"] == "RUNTIME_READBACK_MATCHES_STATIC" else 1
    except Exception as exc:
        failure = {
            "schema": "windwings-runtime-map-crosscheck/v1",
            "status": "NOT_COMPARABLE",
            "evidence_level": "NO_RUNTIME_COMPARISON",
            "error": str(exc),
            "runtime_values": None,
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"NOT_COMPARABLE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
