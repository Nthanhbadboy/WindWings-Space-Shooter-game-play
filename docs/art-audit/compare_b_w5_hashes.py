#!/usr/bin/env python3
"""Compare duplicate-file partitions in old and new B W5 manifests.

Equal bytes are evidence of pixel reuse, not by themselves a runtime defect.
The board and planner/source mapping must establish whether a reuse is suspect.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
from pathlib import Path


def load(root: Path):
    wave = root / "art/w5-full-b"
    with (wave / "w5b_units.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    hashes = {}
    ids = {}
    for row in rows:
        rel = row["file"]
        if rel in hashes:
            raise ValueError(f"Duplicate file path in manifest: {rel}")
        digest = hashlib.sha256((wave / rel).read_bytes()).hexdigest()
        groups[digest].append(rel)
        hashes[rel], ids[rel] = digest, row["row_id"]
    return rows, groups, hashes, ids


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--old-root", type=Path, required=True)
    ap.add_argument("--new-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--by-row-id", action="store_true", help="compare revisions that renamed asset files")
    args = ap.parse_args()
    old_rows, old_groups, old_hash, old_ids = load(args.old_root)
    new_rows, new_groups, new_hash, new_ids = load(args.new_root)
    if args.by_row_id:
        old_paths = {row["row_id"]: row["file"] for row in old_rows}
        new_paths = {row["row_id"]: row["file"] for row in new_rows}
        if (len(old_paths) != len(old_rows) or len(new_paths) != len(new_rows)
                or set(old_paths) != set(new_paths)):
            raise ValueError("W5 row IDs must be unique and unchanged for --by-row-id")
        print(f"Old: {len(old_rows)} files, {len(old_groups)} unique hashes; "
              f"{len(old_rows) - len(old_groups)} duplicates beyond first")
        print(f"New: {len(new_rows)} files, {len(new_groups)} unique hashes; "
              f"{len(new_rows) - len(new_groups)} duplicates beyond first")
        fields = ["row_id", "old_path_relative_to_w5", "new_path_relative_to_w5", "old_sha256", "new_sha256",
                  "old_duplicate_group_size", "new_duplicate_group_size"]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            for row_id in sorted(old_paths):
                op, np = old_paths[row_id], new_paths[row_id]
                oh, nh = old_hash[op], new_hash[np]
                writer.writerow({"row_id": row_id, "old_path_relative_to_w5": op,
                                 "new_path_relative_to_w5": np, "old_sha256": oh, "new_sha256": nh,
                                 "old_duplicate_group_size": len(old_groups[oh]),
                                 "new_duplicate_group_size": len(new_groups[nh])})
        print(f"Wrote {args.out}")
        return
    if set(old_hash) != set(new_hash) or old_ids != new_ids:
        raise ValueError("Old/new manifests no longer have identical paths and row IDs")
    old_parts = {tuple(sorted(group)) for group in old_groups.values()}
    new_parts = {tuple(sorted(group)) for group in new_groups.values()}
    duplicate_parts = sorted((p for p in new_parts if len(p) > 1), key=lambda p: (-len(p), p))
    print(f"Old: {len(old_rows)} files, {len(old_groups)} unique hashes")
    print(f"New: {len(new_rows)} files, {len(new_groups)} unique hashes")
    print(f"All duplicate-equivalence partitions identical: {old_parts == new_parts}")
    print(f"New repeated groups: {len(duplicate_parts)}; duplicate files beyond first: "
          f"{sum(len(p) - 1 for p in duplicate_parts)}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        fields = ["group", "group_size", "row_id", "path_relative_to_w5", "old_sha256", "new_sha256"]
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for n, group in enumerate(duplicate_parts, 1):
            for rel in group:
                writer.writerow({"group": n, "group_size": len(group), "row_id": new_ids[rel],
                                 "path_relative_to_w5": rel, "old_sha256": old_hash[rel],
                                 "new_sha256": new_hash[rel]})
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
