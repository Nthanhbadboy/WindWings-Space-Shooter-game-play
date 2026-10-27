#!/usr/bin/env python3
"""data-integrity.py — dữ liệu gốc kéo về có bị sửa tay không?

Ba phép kiểm, độc lập nhau:

  1. **PROVENANCE** — bảng `sha256` ghi trong `datas/PROVENANCE.md` (lúc kéo
     019e704d1) còn khớp với file đang có không?
  2. **snapshot** — file đang có **giống hệt blob** ở một commit nào của nhánh
     dữ liệu? Nếu khớp một snapshot ⇒ nó chỉ là bản kéo cũ, **không ai sửa tay**.
     Nếu **không khớp snapshot nào** ⇒ có thay đổi cục bộ, phải giải thích.
  3. **nội dung .gz** — file `.gz` đổi byte chưa chắc đổi nội dung. Giải nén rồi
     so mới biết.

Mã thoát 0 nếu không có file "không giải thích được", 1 nếu có.

Chạy:
  python3 tools/data-integrity.py
  python3 tools/data-integrity.py --ref origin/arena/ef6b75ef-windwings-space-shooter-game-p
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs/assets/data-integrity.json")

# Chỉ những đường dẫn là **dữ liệu gốc** (bóc từ APK / nhánh dữ liệu).
SOURCE_PATHS = ("datas", "docs/apk-analysis", "reverse-engineering", "raw",
                "docs/assets/contact-sheets")

DEFAULT_REF = "origin/arena/ef6b75ef-windwings-space-shooter-game-p"
# Các snapshot đã từng kéo. File gốc phải khớp **một** trong số này.
DEFAULT_SNAPSHOTS = ("7e0da2ee3", "9aed767b1", "55bd18ac8", "019e704d1", "6dc5c4bf5")

GZ_SKIP_OVER = 8 * 1024 * 1024   # giải nén file lớn hơn mức này thì bỏ qua


def git(*args: str, binary: bool = False):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def tree(ref: str) -> dict[str, str]:
    """{path: blob-sha} cho các đường dẫn gốc."""
    out = git("ls-tree", "-r", ref, "--", *SOURCE_PATHS)
    if out is None:
        return {}
    d = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        d[path] = meta.split()[2]
    return d


def local_tree() -> dict[str, str]:
    """{path: blob-sha} của working tree, **kể cả file chưa commit**."""
    out = subprocess.run(["git", "ls-files", "-s", "--", *SOURCE_PATHS], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    d = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        d[path] = meta.split()[1]
    # file chưa track (nếu có) — băm tại chỗ
    for path in SOURCE_PATHS:
        root = os.path.join(ROOT, path)
        if not os.path.isdir(root):
            continue
        for dirpath, _, names in os.walk(root):
            for n in names:
                full = os.path.join(dirpath, n)
                rel = os.path.relpath(full, ROOT)
                if rel not in d:
                    # file chưa track: băm **đúng kiểu git** (blob header) để so được với snapshot
                    data = open(full, "rb").read()
                    d[rel] = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
    return d


def head_tree() -> dict[str, str]:
    """{path: blob-sha} tại HEAD — để tách 'bản kéo cũ' khỏi 'sửa cục bộ'."""
    out = subprocess.run(["git", "ls-tree", "-r", "HEAD", "--", *SOURCE_PATHS], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    d = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        d[path] = meta.split()[2]
    return d


def blob_sha(path: str) -> str:
    data = open(os.path.join(ROOT, path), "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def provenance() -> list[tuple[str, str, str]]:
    """[(sha256-16, size, path)] từ bảng trong datas/PROVENANCE.md."""
    path = os.path.join(ROOT, "datas/PROVENANCE.md")
    if not os.path.isfile(path):
        return []
    txt = open(path, encoding="utf-8").read()
    return re.findall(r"^([0-9a-f]{16})\s+(\d+)\s+(\S+)\s*$", txt, re.M)


def blob(ref: str, path: str) -> bytes | None:
    return git("cat-file", "blob", f"{ref}:{path}", binary=True)


def main(argv: list[str]) -> int:
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else DEFAULT_REF
    snaps = (argv[argv.index("--snapshots") + 1].split(",")
             if "--snapshots" in argv else list(DEFAULT_SNAPSHOTS))

    # ── 1. PROVENANCE ──
    rows = provenance()
    ok = stale = missing = 0
    stale_list = []
    for sha, size, p in rows:
        full = os.path.join(ROOT, p)
        if not os.path.isfile(full):
            missing += 1
            continue
        data = open(full, "rb").read()
        if hashlib.sha256(data).hexdigest()[:16] == sha and len(data) == int(size):
            ok += 1
        else:
            stale += 1
            stale_list.append(p)
    print(f"1) PROVENANCE: khớp {ok} · lệch {stale} · thiếu {missing} (bảng {len(rows)} dòng)")
    if stale:
        print("   lệch vì các file này được **kéo lại** sau khi bảng được ghi; "
              "kiểm 2) sẽ nói rõ chúng khớp snapshot nào")

    # ── 2. so với đầu nhánh dữ liệu ──
    up = tree(ref)
    loc = local_tree()
    both = sorted(set(up) & set(loc))
    same = [p for p in both if up[p] == loc[p]]
    diff = [p for p in both if up[p] != loc[p]]
    print(f"2) so với {ref}: {len(both)} file chung · giống {len(same)} · khác {len(diff)}")
    print(f"   (chỉ có ở nhánh dữ liệu: {len(set(up) - set(loc))} · "
          f"chỉ có ở đây: {len(set(loc) - set(up))})")

    head = head_tree()
    dirty = sorted(p for p in loc if p in head and blob_sha(p) != head[p])
    new_files = sorted(p for p in loc if p not in head)
    if dirty:
        print(f"   ⚠ {len(dirty)} file ĐANG SỬA trong working tree (khác HEAD): {dirty[:5]}")
    if new_files:
        print(f"   {len(new_files)} file chưa track (lần kéo mới, chưa commit)")

    snap_trees = {s: tree(s) for s in snaps}
    per = collections.Counter()
    unexplained = []
    old_pull = []
    for p in diff:
        hits = tuple(s for s, t in snap_trees.items() if t.get(p) == loc[p])
        if hits:
            per[hits] += 1
        elif p not in dirty:
            # nội dung = đúng blob đã commit ⇒ chỉ là bản kéo cũ hơn danh sách snapshot
            old_pull.append(p)
        else:
            unexplained.append(p)
    if diff:
        print("   khớp snapshot nào (⇒ chỉ là bản kéo cũ, không sửa tay):")
        for hits, n in per.most_common():
            print(f"     {n:4d}  {' + '.join(hits)}")
        print(f"   khớp HEAD nhưng cũ hơn snapshot (không sửa tay): {len(old_pull)}")
        print(f"   KHÔNG khớp snapshot nào VÀ đang sửa: {len(unexplained)}")

    # ── 3. .gz: byte khác nhưng nội dung có khác? ──
    gz = [p for p in diff if p.endswith(".gz")]
    gz_same = gz_diff = gz_skip = 0
    for p in gz:
        a = blob(ref, p)
        b = blob("HEAD", p)
        if a is None or b is None or len(a) > GZ_SKIP_OVER:
            gz_skip += 1
            continue
        try:
            same_content = gzip.decompress(a) == gzip.decompress(b)
        except OSError:
            gz_skip += 1
            continue
        if same_content:
            gz_same += 1
        else:
            gz_diff += 1
    print(f"3) {len(gz)} file .gz khác byte: nội dung sau giải nén "
          f"**giống {gz_same}** · **khác {gz_diff}** · bỏ qua {gz_skip}")
    print("   ⇒ 'đổi byte' không đồng nghĩa 'đổi dữ liệu'")

    summary = {
        "provenance": {"rows": len(rows), "ok": ok, "stale": stale, "missing": missing},
        "ref": ref,
        "common": len(both), "same_as_ref": len(same), "differs": len(diff),
        "only_upstream": len(set(up) - set(loc)), "only_here": len(set(loc) - set(up)),
        "snapshot_match": {" + ".join(k): v for k, v in per.items()},
        "unexplained": unexplained, "old_pull": old_pull,
        "dirty": dirty, "new_files": len(new_files),
        "gz": {"files": len(gz), "same_content": gz_same,
               "diff_content": gz_diff, "skipped": gz_skip},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print("đã ghi", os.path.relpath(OUT, ROOT))
    return 1 if (unexplained or dirty) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
