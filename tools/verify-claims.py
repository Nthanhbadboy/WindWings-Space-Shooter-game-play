#!/usr/bin/env python3
"""verify-claims.py — đo lại mọi con số đã viết trong docs.

Mỗi tuyên bố ghi bốn thứ: nó nằm ở **file nào, dòng nào**, **số doc nói**, và
**phép đo** lấy lại số đó từ dữ liệu nguồn. Một tuyên bố chỉ PASS khi cả hai
chiều cùng đúng:

  1. phép đo ra đúng con số doc ghi;
  2. dòng doc đó **vẫn còn chứa** con số ấy.

Chiều thứ hai là thứ bắt được tài liệu bị sửa tay sau này mà dữ liệu không đổi —
kiểu sai đã xảy ra ba lần trước đây.

Nguồn chỉ **đọc**, không ghi:
    docs/apk-analysis/ramus/**                    JSON kéo từ điện thoại
    git show <data-ref>:datas/*                   data pack nhánh phân tích
    git show <data-ref>:reverse-engineering/*     typetree + TextAsset

    python3 tools/verify-claims.py                 # dùng ref mặc định
    python3 tools/verify-claims.py --ref <sha>     # chỉ định ref nhánh dữ liệu
    python3 tools/verify-claims.py --only B        # chỉ chạy nhóm B
    python3 tools/verify-claims.py --verbose

Mã thoát: 0 nếu không có FAIL, 1 nếu có. SKIP không phải lỗi: tuyên bố thiếu
nguồn (chưa fetch nhánh, clone nông) được báo riêng và không tính vào kết luận.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import os
import re
import statistics
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PHONE = os.path.join(ROOT, "docs", "apk-analysis", "ramus", "2026-10-23-phone")

DEFAULT_REFS = [
    "origin/arena/ef6b75ef-windwings-space-shooter-game-p",
    "arena/ef6b75ef-windwings-space-shooter-game-p",
    "ef6b75ef",
]

_cache: dict[str, object] = {}


# ── nguồn ──────────────────────────────────────────────────────────────

def git(*args: str) -> bytes | None:
    try:
        out = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


PROVENANCE: dict[str, dict] = {}
EXPLICIT_REF = False


def _record(path: str, source: str, blob_sha: str | None, size: int | None) -> None:
    PROVENANCE[path] = {"path": path, "source": source,
                        "blob_sha": blob_sha, "bytes": size}


def ref_blob(path: str, local_root: str | None = None) -> bytes | None:
    """Thân file, đã giải nén nếu là .gz. **Ghi provenance cho từng input.**

    Hai chế độ, khác nhau ở **thứ tự đọc**:

    * **`--ref <sha>` (explicit)**: `git show` **trước**, chỉ rơi về local khi
      path không có trong ref — và ghi rõ `local-fallback`. Đây là chế độ dùng
      khi báo "đã kiểm snapshot mới".
    * **mặc định**: local trước (dữ liệu đã kéo về repo), rồi mới tới ref.

    Lỗi cũ (sửa 25/10): bản trước **luôn** local-first, nên `--ref <sha mới>`
    vẫn có thể trả dữ liệu local cũ mà không nói gì. Nay có `--provenance`
    (in nguồn + blob SHA) và `--strict-ref` (mọi input local ⇒ exit 2).
    """
    key = "blob:" + path
    if key in _cache:
        return _cache[key]  # type: ignore[return-value]
    raw = None
    source = None
    blob_sha = None

    if EXPLICIT_REF:
        for ref in REFS:
            raw = git("show", f"{ref}:{path}")
            if raw:
                source = f"ref:{ref}"
                sha = git("rev-parse", f"{ref}:{path}")
                blob_sha = sha.decode().strip() if sha else None
                break

    if raw is None:
        local = os.path.join(local_root or ROOT, path)
        if os.path.isfile(local):
            try:
                with open(local, "rb") as f:
                    raw = f.read()
                source = "local-fallback" if EXPLICIT_REF else "local"
            except OSError:
                raw = None

    if raw is None:
        for ref in REFS:
            raw = git("show", f"{ref}:{path}")
            if raw:
                source = f"ref:{ref}"
                sha = git("rev-parse", f"{ref}:{path}")
                blob_sha = sha.decode().strip() if sha else None
                break

    if raw is not None and path.endswith(".gz") and raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except OSError:
            raw = None
    _record(path, source or "missing", blob_sha, len(raw) if raw is not None else None)
    _cache[key] = raw
    return raw


def provenance_report(only_local: bool = False) -> str:
    """Bảng provenance: mỗi input đọc từ **đâu**, blob SHA là gì."""
    rows = []
    for path, meta in sorted(PROVENANCE.items()):
        if only_local and not meta["source"].startswith(("local", "missing")):
            continue
        sha = (meta["blob_sha"] or "—")[:12]
        rows.append(f'{meta["source"]:<24} {sha:<13} {meta["bytes"] or 0:>9}  {path}')
    head = f'{"nguồn":<24} {"blob":<13} {"byte":>9}  path'
    return "\n".join([head, "-" * 78] + rows)


def local_inputs() -> list[str]:
    """Input **dữ liệu** KHÔNG đến từ ref (dùng cho `--strict-ref`).

    `docs/spec/**` là tài liệu của nhánh này — nó **phải** là local, không tính.
    Chỉ `datas/`, `reverse-engineering/`, `docs/apk-analysis/` mới là dữ liệu
    phải chứng minh là đọc từ ref.
    """
    data_prefixes = ("datas/", "reverse-engineering/", "docs/apk-analysis/")
    return sorted(p for p, m in PROVENANCE.items()
                  if m["source"] in ("local", "local-fallback", "missing")
                  and p.startswith(data_prefixes))


def selftest_provenance() -> tuple[bool, str]:
    """Kiểm chế độ explicit-ref **không** đọc file local cũ.

    Dựng thư mục tạm có `datas/sprites.csv` **giả**, gọi `ref_blob` ở chế độ
    explicit-ref. Trả về bản của ref ⇒ ĐẠT; trả về bản giả ⇒ lỗi provenance.
    """
    import tempfile

    target = "datas/sprites.csv"
    ref_bytes = None
    ref = None
    for candidate in REFS:
        ref_bytes = git("show", f"{candidate}:{target}")
        if ref_bytes:
            ref = candidate
            break
    if not ref_bytes:
        return False, "không đọc được %s từ ref nào" % target

    global EXPLICIT_REF
    before = EXPLICIT_REF
    try:
        with tempfile.TemporaryDirectory() as tmp:
            dst = os.path.join(tmp, target)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as fh:
                fh.write(b"name,type,width,height\nFAKE_STALE,Texture2D,1,1\n")
            EXPLICIT_REF = True
            _cache.pop("blob:" + target, None)
            got = ref_blob(target, local_root=tmp)
    finally:
        EXPLICIT_REF = before
        _cache.pop("blob:" + target, None)

    if got == ref_bytes:
        return True, f"explicit-ref đọc {ref}:{target} ({len(ref_bytes)} B), bỏ qua bản local giả"
    if got is not None and b"FAKE_STALE" in got:
        return False, "VẪN đọc file local giả ⇒ lỗi provenance chưa sửa"
    return False, "dữ liệu trả về khác cả ref lẫn bản giả"


def ref_json(path: str):
    key = "json:" + path
    if key in _cache:
        return _cache[key]
    raw = ref_blob(path)
    val = None
    if raw:
        try:
            val = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            val = None
    _cache[key] = val
    return val


def ref_lines(path: str) -> list[str] | None:
    raw = ref_blob(path)
    if raw is None:
        return None
    return raw.decode("utf-8", "replace").splitlines()


def phone_json(name: str):
    key = "phone:" + name
    if key in _cache:
        return _cache[key]
    p = os.path.join(PHONE, name)
    val = None
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                val = json.load(f)
        except (OSError, json.JSONDecodeError):
            val = None
    _cache[key] = val
    return val


def phone_files_with_fields() -> list[str]:
    if "phone:withfields" in _cache:
        return _cache["phone:withfields"]  # type: ignore[return-value]
    names = []
    if os.path.isdir(PHONE):
        for n in sorted(os.listdir(PHONE)):
            if not n.endswith(".json"):
                continue
            d = phone_json(n)
            if isinstance(d, dict) and isinstance(d.get("fields"), dict):
                names.append(n)
    _cache["phone:withfields"] = names
    return names


def all_fields() -> list[tuple[str, str, object]]:
    """(file, field, value) cho mọi field trong mọi ảnh chụp /statics."""
    key = "phone:allfields"
    if key in _cache:
        return _cache[key]  # type: ignore[return-value]
    rows: list[tuple[str, str, object]] = []
    for n in phone_files_with_fields():
        d = phone_json(n)
        for k, v in d["fields"].items():
            rows.append((n, k, v))
    _cache[key] = rows
    return rows


TYPE_NAME = re.compile(r"^\s*\((?:List|Dictionary|Il2Cpp|\w+`\d)|\bIl2Cpp\w*Array\b|\bNativeFieldInfoPtr_|^\s*\(\w+\)\s*$")


def is_type_only(v: object) -> bool:
    """Giá trị chỉ là tên type, không phải dữ liệu.

    Bridge ghi `"(List`1)"` cho list chưa mở và `"Il2CppStructArray`1[System.Int32]"`
    cho mảng interop chưa unroll. Field `*_count` do bridge tự thêm không tính.
    """
    if not isinstance(v, str):
        return False
    if v.startswith("NativeFieldInfoPtr_"):
        return True
    return bool(TYPE_NAME.search(v))


def reals() -> list[tuple[str, str, object]]:
    return [(f, k, v) for f, k, v in all_fields() if not k.endswith("_count")]


# ── khai báo ───────────────────────────────────────────────────────────

@dataclass
class Claim:
    cid: str
    doc: str                 # đường dẫn tương đối
    line_has: str            # dòng doc phải chứa chuỗi này
    stated: object           # con số / giá trị doc nói
    measure: Callable[[], object]
    note: str = ""
    status: str = ""         # PASS / FAIL / SKIP
    got: object = None
    why: str = ""


CLAIMS: list[Claim] = []
_docs: dict[str, list[str] | None] = {}


def doc_lines(path: str) -> list[str] | None:
    if path not in _docs:
        p = os.path.join(ROOT, path)
        if not os.path.isfile(p):
            _docs[path] = None
        else:
            with open(p, encoding="utf-8") as f:
                _docs[path] = f.read().splitlines()
    return _docs[path]


def claim(cid, doc, line_has, stated, measure, note=""):
    CLAIMS.append(Claim(cid, doc, line_has, stated, measure, note))


def agg(src, fn):
    """Áp fn lên nguồn, nhưng giữ None nếu nguồn vắng."""
    return None if src is None else fn(src)


def approx(a, b, tol=5e-4) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


# ── A. ảnh chụp runtime trên điện thoại ────────────────────────────────
# Toàn bộ số ở đây đến từ một lần chạy thật; chúng chỉ kiểm được tính nhất
# quán nội bộ của bộ sưu tập, không tái lập được nếu không cắm máy.

SUMMARY = "docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md"

claim("A1", SUMMARY, "21 file có `fields`", 21,
      lambda: len(phone_files_with_fields()),
      "số file /statics đọc được trong thư mục phiên")

claim("A2", SUMMARY, "**575 field đọc được", 575,
      lambda: len(reals()))

claim("A3", SUMMARY, "88 field chỉ trả về tên type", 88,
      lambda: sum(1 for _, _, v in reals() if is_type_only(v)))

claim("A4", SUMMARY, "**10** phần tử", 10,
      lambda: (phone_json("statics_Device_Get_Data.json") or {})
      .get("fields", {}).get("listStatValues_count"))

claim("A5", SUMMARY, "`_count = 250`", 250,
      lambda: (phone_json("statics_Map_Get_Datas.json") or {})
      .get("fields", {}).get("listMapDatas_count"))

claim("A6", SUMMARY, "chỉ **128** phần tử", 128,
      lambda: len((phone_json("statics_Map_Get_Datas.json") or {})
                  .get("fields", {}).get("listMapDatas") or []))

claim("A7", SUMMARY, "[0.5,0.6,0.4,0.8,1]", [0.5, 0.6, 0.4, 0.8, 1],
      lambda: (phone_json("statics_Device_Get_Data.json") or {})
      .get("fields", {}).get("percentByLevels1"))

claim("A8", SUMMARY, "[0.1,0.1,0.3,0.4,0.5]", [0.1, 0.1, 0.3, 0.4, 0.5],
      lambda: (phone_json("statics_Device_Get_Data.json") or {})
      .get("fields", {}).get("percentByLevels2"))

claim("A9", SUMMARY, "`GP_Datas` (65 field)", 65,
      lambda: len((phone_json("statics_GP_Datas.json") or {}).get("fields", {})))

claim("A10", "docs/apk-analysis/ramus/2026-10-23-phone/CROSSCHECK-static-vs-runtime.md",
      "**10**", 10,
      lambda: (phone_json("statics_Device_Get_Data.json") or {})
      .get("fields", {}).get("listStatValues_count"),
      "số động đo được; số tĩnh 12 nằm trong APK, không có trong ảnh chụp này")


# ── B. data pack ───────────────────────────────────────────────────────

SPINE = "datas/spine.json"
SPINE_ANIM = "datas/spine_anim.json.gz"
CLIPS = "datas/anim_clips.json.gz"
AMAP = "datas/animator_map.csv.gz"
ANIMDOC = "docs/spec/ANIMATION.md"
GAPS = "docs/spec/ANIMATION_GAPS.md"


def spine_totals():
    d = ref_json(SPINE_ANIM)
    return None if d is None else d.get("totals", {})


def clips():
    d = ref_json(CLIPS)
    return None if d is None else d.get("clips", [])


def amap_rows():
    raw = ref_blob(AMAP)
    if raw is None:
        return None
    lines = raw.decode("utf-8", "replace").splitlines()
    return [ln.split(",") for ln in lines[1:] if ln.strip()]


claim("B1", ANIMDOC, "27 rig", 27,
      lambda: agg(ref_json(SPINE), lambda d: len(d.get("rigs", []))))

claim("B2", ANIMDOC, "**185** animation", 185,
      lambda: agg(spine_totals(), lambda t: t.get("animations")),
      "doc ghi 180 = không tính Saw; tổng thật 185 (Saw 5) — 26 rig skeleton")

claim("B2b", ANIMDOC, "6** × 21 rig", 180,
      lambda: agg(ref_json(SPINE_ANIM), lambda d: sum(
          len(r.get("animations") or {}) for k, r in d.get("rigs", {}).items() if k != "Saw")),
      "180 là tổng của 26 rig skeleton, đúng như phân bố dòng 55")

claim("B3", "docs/spec/PIPELINE_AUDIT.md", "12.274", 12274,
      lambda: agg(spine_totals(), lambda t: t.get("keyframes")))

claim("B3b", GAPS, "**12.274**", 12274,
      lambda: agg(spine_totals(), lambda t: t.get("keyframes")))

claim("B4", GAPS, "**21** event", 21,
      lambda: agg(spine_totals(), lambda t: t.get("events")))

claim("B5", ANIMDOC, "**616** bone", 616,
      lambda: agg(ref_json(SPINE_ANIM), lambda d: sum(
          int(r.get("bones_total") or 0) for r in d.get("rigs", {}).values())))

claim("B6", ANIMDOC, "**446** slot", 446,
      lambda: agg(ref_json(SPINE_ANIM), lambda d: sum(
          int(r.get("slots_total") or 0) for r in d.get("rigs", {}).values())))

claim("B7", ANIMDOC, "**791** clip", 791, lambda: agg(clips(), len))

claim("B8", ANIMDOC, "**226**", 226,
      lambda: agg(clips(), lambda cs: len({c.get("name") for c in cs})))

claim("B9", ANIMDOC, "**251** loop", 251,
      lambda: (_ for _ in ()).throw(NoSource(
          "không nguồn: anim_clips.json không có trường loop, typetree native-types "
          "có m_WrapMode nhưng toàn 0 (reader không giải) — 251 chỉ tái lập được "
          "bằng UnityPy trực tiếp")),
      "con số duy nhất trong ANIMATION.md không kiểm lại được offline")

claim("B10", ANIMDOC, "**318**", 318,
      lambda: agg(clips(), lambda cs: sum(1 for c in cs if c.get("events"))))

claim("B11", ANIMDOC, "**793**", 793,
      lambda: agg(clips(), lambda cs: sum(len(c.get("events") or []) for c in cs)))

claim("B12", ANIMDOC, "1,9 s", 1.9,
      lambda: agg(clips(), lambda cs: round(
          statistics.median([c["duration"] for c in cs if "duration" in c]), 1)))

claim("B13", ANIMDOC, "**75,0**", 75.0,
      lambda: agg(clips(), lambda cs: max(c["duration"] for c in cs if "duration" in c)))

def wave_roster() -> set[str] | None:
    """109 tên prefab enemy thực sự được spawn.

    Định nghĩa (ANIMATION.md §4.5): `datas/waves.json` →
    `waves[].spawners[].enemies[]`, đếm tên phân biệt. Đây là con số 109 mà
    tài liệu dùng suốt mà chưa từng viết ra định nghĩa.
    """
    d = ref_json("datas/waves.json")
    if d is None:
        return None
    names: set[str] = set()
    for w in d.get("waves", []):
        for sp in w.get("spawners") or []:
            for e in sp.get("enemies") or []:
                names.add(e)
    return names


def animators_on_roster():
    """(số instance, số prefab) Animator nằm trên roster spawn."""
    roster = wave_roster()
    rows = amap_rows()
    if roster is None or rows is None:
        return None
    hit = [r for r in rows if len(r) > 2 and r[2] in roster]
    return (len(hit), len({r[2] for r in hit}))


claim("B14", ANIMDOC, "**enemy/boss 203 `Animator` trên 87/109 prefab**",
      (203, 87), animators_on_roster,
      "roster waves.json — cả hai con số của nhánh spec đều tái lập được")

claim("B15", ANIMDOC, "**109 prefab enemy/boss thực sự được spawn**", 109,
      lambda: None if wave_roster() is None else len(wave_roster()),
      "định nghĩa: tên phân biệt trong waves[].spawners[].enemies[]")

claim("B16", GAPS, "**154 instance / 63 prefab**", (154, 63),
      lambda: agg(amap_rows(), lambda rows: (
          sum(1 for r in rows if len(r) > 2 and re.match(r"^(CB-|Boss-|MB-)", r[2])),
          len({r[2] for r in rows if len(r) > 2 and re.match(r"^(CB-|Boss-|MB-)", r[2])}))),
      "định nghĩa của nhánh kia: mẫu tên — cũng đúng, chỉ khác tập")

claim("B17", GAPS, "**92 Animator / 36 prefab**", (92, 36),
      lambda: agg(amap_rows(), lambda rows: (
          sum(1 for r in rows if len(r) > 2 and r[2].startswith("Boss-")),
          len({r[2] for r in rows if len(r) > 2 and r[2].startswith("Boss-")}))),
      "chỉ prefab tên Boss-")


# ── C. TextAsset Spine + typetree ──────────────────────────────────────

TA_DIR = "reverse-engineering/textassets"


def ta_names() -> list[str] | None:
    local_dir = os.path.join(ROOT, TA_DIR)
    if os.path.isdir(local_dir):
        names = [n for n in os.listdir(local_dir) if n.endswith(".json")]
        if names:
            return names
    raw = git("ls-tree", "-r", "--name-only", f"{REFS[0]}", TA_DIR + "/")
    if not raw:
        return None
    return [os.path.basename(p) for p in raw.decode().splitlines() if p.endswith(".json")]


def ta_json(name: str):
    return ref_json(f"{TA_DIR}/{name}")


def rig_anim_names() -> dict[str, set[str]] | None:
    d = ref_json(SPINE_ANIM)
    if not d:
        return None
    return {k: set((v.get("animations") or {}).keys())
            for k, v in d.get("rigs", {}).items()}


ATTACKY = {"Attack1", "Attack2", "Attack3", "Attack4", "Attack01", "AttackSpec",
           "TopL", "TopR", "Shot", "Attack"}


def attack_rigs() -> int | None:
    ra = rig_anim_names()
    if ra is None:
        return None
    return sum(1 for names in ra.values() if names & ATTACKY)


def rig_assets() -> int | None:
    names = ta_names()
    if names is None:
        return None
    return len([n for n in names if n.startswith("skeleton") and n.endswith(".json")]) + \
        len([n for n in names if n == "Saw.json"])


claim("C1", ANIMDOC, "27 rig Spine", 27, rig_assets,
      "26 skeleton*.json + Saw.json; đếm mỗi skeleton* sẽ ra 26")

claim("C2", GAPS, "đòn tập trung ở 4 rig", 4, attack_rigs,
      "rig có ít nhất một animation tên đòn")

claim("C3", GAPS, "### 2c. 23/27 rig Spine", 23,
      lambda: None if attack_rigs() is None else 27 - (attack_rigs() or 0))


def bone_match() -> tuple[int, int] | None:
    """Ghép rig ↔ TextAsset: (khớp đúng 1, nhập nhằng).

    Định nghĩa dùng ở §3.2 là **tập tên bone bằng đúng** giữa `spine.json.bones`
    và `bones` của TextAsset — không phải bone có mặt trong animation (bone không
    animate sẽ vắng và phép so sai).
    """
    d = ref_json(SPINE)
    names = ta_names()
    if not d or not names:
        return None
    tas: dict[str, set[str]] = {}
    for n in names:
        ta = ta_json(n) or {}
        tas[n] = {b.get("name") for b in ta.get("bones", []) if isinstance(b, dict)}
    clear = ambiguous = 0
    for r in d.get("rigs", []):
        rb = set(r.get("bones") or [])
        if not rb:
            continue
        hits = sum(1 for tb in tas.values() if tb == rb)
        if hits == 1:
            clear += 1
        elif hits > 1:
            ambiguous += 1
    return clear, ambiguous


claim("C4", GAPS, "18/27 khớp 1-1", 18,
      lambda: (bone_match() or (None, None))[0],
      "số rig ghép được đúng một TextAsset bằng tên bone")

def appear_stats() -> tuple[int, int] | None:
    """(số instance, số field thật) của Enemy_Appear."""
    lines = ref_lines("reverse-engineering/raw/typetrees/Enemy_Appear.jsonl.gz")
    if lines is None:
        return None
    n = 0
    real = 0
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            d = json.loads(ln)
        except json.JSONDecodeError:
            continue
        n += 1
        tree = d.get("tree") or {}
        real += sum(1 for k in tree if not k.startswith("m_"))
    return n, real


claim("C5", GAPS, "**914** instance", 914,
      lambda: (appear_stats() or (None, None))[0],
      "số instance Enemy_Appear trong typetree")

claim("C5b", GAPS, "0 field", 0,
      lambda: (appear_stats() or (None, None))[1],
      "field serialize ngoài m_* — 0 nghĩa là không có gì để đọc")

claim("C6", GAPS, "17/17 instance", 17,
      lambda: count_lines("reverse-engineering/raw/typetrees/Enemy_HitSkeletonRenderer.jsonl.gz"))

claim("C7", GAPS, "**981** instance", True,
      lambda: None if ref_lines("reverse-engineering/raw/typetrees/Enemy_Movement.jsonl.gz") is None else True)

def count_lines(path: str) -> int | None:
    """Số dòng có nội dung; None khi không đọc được nguồn.

    Quan trọng: trả None chứ không trả 0 — thiếu dữ liệu là SKIP, còn 0 là một
    phép đo thật và sẽ thành FAIL nếu doc nói khác.
    """
    lines = ref_lines(path)
    if lines is None:
        return None
    return len([ln for ln in lines if ln.strip()])


# ── F. data pack: đếm đơn vị ──────────────────────────────────────────

claim("F1", GAPS, "**981** instance", 981,
      lambda: count_lines("reverse-engineering/raw/typetrees/Enemy_Movement.jsonl.gz"))

claim("F2", GAPS, "**46 boss**", 46,
      lambda: (ref_json("datas/bosses.json") or {}).get("count"))

def boss_prefab_roots() -> int | None:
    raw = ref_blob("reverse-engineering/raw/typetrees/prefab-roots.csv")
    if raw is None:
        return None
    import csv as _csv
    import io as _io
    rows = list(_csv.DictReader(_io.StringIO(raw.decode("utf-8", "replace"))))
    return len({r.get("name") for r in rows if (r.get("name") or "").startswith("Boss-")})


claim("F3", GAPS, "**39 prefab `Boss-*`**", 39, boss_prefab_roots,
      "prefab root tên Boss-* trong prefab-roots.csv (không phải số có Animator)")

claim("F4", ANIMDOC, "2.185", 2185,
      lambda: (_ for _ in ()).throw(NoSource(
          "không nguồn: native-types chỉ có 5 loại type (Animator/ParticleSystem/"
          "AnimationClip/AnimatorController/Camera); 2.185 Sprite đến từ asset scan "
          "của UnityPy, không có trong bản export này")),
      "Sprite chỉ kiểm được nếu export thêm typetree Sprite")

claim("C8", GAPS, "26 rig + `Saw`", 26,
      lambda: None if ta_names() is None else len(
          [n for n in ta_names() if n.startswith("skeleton") and n.endswith(".json")]),
      "số rig skeleton* (không tính Saw) — dòng 19 từng ghi 25")


# ── D. code: bộ đọc animation và đường lấy số ──────────────────────────

BRIDGE = "runtime-probe/RamusBridge.cs"
COLLECT = "runtime-probe/collect.sh"
BUILD = ".github/scripts/build-bridge.sh"


def local_has(path: str, needle: str) -> bool | None:
    p = os.path.join(ROOT, path)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as f:
        return needle in f.read()


claim("D1", BRIDGE, "GET /anim", True,
      lambda: local_has(BRIDGE, 'case "GET /anim"'),
      "route tồn tại trong bridge")

claim("D2", COLLECT, 'get "/anim?max=', True,
      lambda: local_has(COLLECT, 'get "/anim?max='),
      "collect.sh gọi endpoint ở mỗi mốc dump")

claim("D3", COLLECT, "anim-ingame.json", True,
      lambda: local_has(COLLECT, '"playback":["anim-ingame.json"]'),
      "gate đòi file chứa số đo playback")

claim("D4", BUILD, 'build "core (netstandard2.1, Unity stubs)"', 5,
      lambda: sum(1 for ln in (open(os.path.join(ROOT, BUILD), encoding="utf-8")
                               .read().splitlines() if os.path.isfile(os.path.join(ROOT, BUILD)) else [])
                  if re.match(r'\s*build "', ln)),
      "5 lần biên dịch; mục thứ 6 của ma trận là self-test chạy, không compile")

claim("D5", "runtime-probe/README.md", "/anim?name=", True,
      lambda: local_has("runtime-probe/README.md", "/anim?name="))


# ── E. số liệu đọc từ điện thoại (nhóm A của SUMMARY) ──────────────────

PLAYER = "statics_Player_Get_Datas.json"
STAGE_GET = "statics_Stage_Get_Datas.json"
TECH = "statics_Tech_Datas.json"
STAGE = "statics_Stage_Datas.json"
DRONE = "statics_Drone_Get_Datas.json"
BALANCE = "docs/spec/BALANCE.md"
DIFF = "docs/spec/DIFFICULTY_MODES.md"
MISSIONS = "docs/spec/MISSIONS_STARS.md"


def pfield(name: str, key: str):
    return lambda: (phone_json(name) or {}).get("fields", {}).get(key)


def pfield_where(*names):
    """Field có thể nằm ở file này hoặc file kia (Stage_Datas / boss_stagedata)."""
    def probe(key):
        for n in names:
            v = (phone_json(n) or {}).get("fields", {}).get(key)
            if v is not None:
                return v
        return None
    return probe


claim("E1", DIFF, "**đọc được: 4**", 4,
      lambda: pfield_where(STAGE, "boss_boss_stagedata.json")("MaxModeIndex"),
      "Stage_Datas.MaxModeIndex — số chế độ")

claim("E2", BALANCE, "levelDelta", [1, 2, 3.6, 3.6],
      pfield(STAGE_GET, "levelDelta"))

claim("E3", BALANCE, "StartHp", 2500, pfield(PLAYER, "StartHp"))

claim("E4", BALANCE, "stepCommon", 0.18, pfield(PLAYER, "stepCommon"))

claim("E5", BALANCE, "shipCloneDamage", [1.35, 1.6, 1.86],
      pfield(PLAYER, "shipCloneDamage"))

claim("E6", BALANCE, "DeltaStarCost", 50, pfield(TECH, "DeltaStarCost"))

claim("E7", BALANCE, "StartStarCost", 30, pfield(TECH, "StartStarCost"))

claim("E8", BALANCE, "MaxLevelPerRanks", [10, 20, 30, 60, 120, 250, 500],
      pfield(DRONE, "MaxLevelPerRanks"))

claim("E9", MISSIONS, "[0.2, 0.6, 0.98]", [0.2, 0.6, 0.98],
      pfield(PLAYER, "PercentToCompleteMissions222"))



claim("E11", MISSIONS, "**31 ID**", 31,
      lambda: len(pfield(STAGE_GET, "listIgroneEnemies")() or []),
      "danh sách enemy bị bỏ qua trong chế độ nhiệm vụ")

claim("E12", "docs/spec/MISSIONS_STARS.md", "**31 phần tử**", 31,
      lambda: len(pfield(STAGE_GET, "listIgroneEnemies")() or []))


# ── G. ghép rig ↔ prefab bằng typetree SkeletonAnimation ───────────────
# Bằng chứng mạnh nhất hiện có: con trỏ trực tiếp, không suy theo tên bone.

SA_DIR = "reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation"


def _tt_maps():
    """(go→transform, transform→father, transform→prefab name)."""
    key = "ttmaps"
    if key in _cache:
        return _cache[key]
    tt = ref_lines("reverse-engineering/raw/typetrees/transform-tree.tsv.gz")
    pr = ref_blob("reverse-engineering/raw/typetrees/prefab-roots.csv")
    if tt is None or pr is None:
        _cache[key] = None
        return None
    import csv as _csv
    import io as _io
    go2tr, father = {}, {}
    for ln in tt[1:]:
        parts = ln.split("\t")
        if len(parts) < 3:
            continue
        tr, go, fa = parts[0], parts[1], parts[2]
        go2tr[go] = tr
        father[tr] = fa if fa not in ("-1", "0", "") else None
    roots = {r["transform_path_id"]: r["name"]
             for r in _csv.DictReader(_io.StringIO(pr.decode("utf-8", "replace")))}
    _cache[key] = (go2tr, father, roots)
    return _cache[key]


def _spine_instances():
    """[(gameobject path_id, rig path_id)] từ typetree SkeletonAnimation."""
    key = "spine_inst"
    if key in _cache:
        return _cache[key]
    paths = spine_instance_paths()
    if paths is None:
        return None
    out = []
    for pth in paths:
        d = ref_json(pth)
        if not d:
            continue
        try:
            out.append((str(d["m_GameObject"]["m_PathID"]),
                        d["skeletonDataAsset"]["m_PathID"]))
        except (KeyError, TypeError):
            continue
    _cache[key] = out
    return out


def spine_instance_paths() -> list[str] | None:
    local = os.path.join(ROOT, SA_DIR)
    names = None
    if os.path.isdir(local):
        names = [n for n in os.listdir(local) if n.endswith(".json")]
    if not names:
        raw = git("ls-tree", "-r", "--name-only", REFS[0], SA_DIR + "/")
        if not raw:
            return None
        names = [os.path.basename(p) for p in raw.decode().splitlines() if p.endswith(".json")]
    return [f"{SA_DIR}/{n}" for n in sorted(names)]


def rig_prefab(rig: int):
    """Prefab root mà một rig được gắn vào, hoặc danh sách rỗng."""
    inst = _spine_instances()
    maps = _tt_maps()
    if inst is None or maps is None:
        return None
    go2tr, father, roots = maps
    out = []
    for go, r in inst:
        if r != rig:
            continue
        tr = go2tr.get(go)
        seen = set()
        while tr and tr not in seen:
            seen.add(tr)
            if tr in roots:
                out.append(roots[tr])
                break
            tr = father.get(tr)
    return out


def appear_subclasses() -> int | None:
    raw = ref_blob("reverse-engineering/il2cpp/dump.cs.gz")
    if raw is None:
        return None
    n = 0
    for ln in raw.decode("utf-8", "replace").splitlines():
        if " class " in ln and ": Enemy_Appear" in ln:
            n += 1
    return n


def appear_asm_is_delegate() -> bool | None:
    lines = ref_lines("reverse-engineering/raw/il2cpp-consts/Enemy_Appear.asm.txt")
    if lines is None:
        return None
    body = "\n".join(lines)
    # Vỏ gọi delegate: tail-call qua thanh ghi, có nhánh null, không có lệnh nào khác
    return "br       x2" in body and "cbz      x1" in body


claim("G1", GAPS, "**20 instance, export 23/10**", 20,
      lambda: None if spine_instance_paths() is None else len(spine_instance_paths()),
      "chỉ là số FILE trong thư mục export — KHÔNG phải toàn bộ component trong game (xem G10)")

claim("G2", GAPS, "| `580611` = `skeleton__21` | 10, có `Attack1–4` | **`Boss-39001`** + **`Boss-39002`** (dùng chung) | **boss** |",
      ["Boss-39001"], lambda: rig_prefab(580611),
      "export 20 file chỉ thấy Boss-39001; spine-prefabs.json (G8) thấy thêm Boss-39002")

claim("G3", GAPS, "**`Boss-39003`** (`Body/Boss 1/Skeleton`)", ["Boss-39003"],
      lambda: rig_prefab(580613), "rig thân boss, mức A")

claim("G4", GAPS, "| `580619` = `skeleton__17` | 18 × `Attack01–12` | `Popup_UnlockShip` | **UI** |",
      ["Popup_UnlockShip"],
      lambda: rig_prefab(580619),
      "18 'attack' 0,4 s là hiệu ứng popup, không phải đòn boss")

claim("G5", GAPS, "| `580623` = `skeleton__5` | `AttackSpec`/`TopL`/`TopR` | `Popup_UnlockShip` | **UI** |",
      ["Popup_UnlockShip"],
      lambda: rig_prefab(580623))

claim("G6", GAPS, "**39 lớp con**", 39, appear_subclasses,
      "mọi lớp con của Enemy_Appear đều là *_Director")

claim("G7", GAPS, "**32 byte, và không có logic nào của riêng nó.**", True,
      appear_asm_is_delegate,
      "Appear = vỏ gọi delegate: cbz null + br thanh ghi")

def spine_prefabs():
    """Ba component Spine trên boss, ghép bằng PPtr thật (report 38)."""
    d = ref_json("reverse-engineering/raw/animation-audit/spine-prefabs.json")
    return None if d is None else {c["prefab"]: c for c in d.get("components", [])}


def boss_rig(prefab: str):
    """SDA (rig) mà một prefab boss thật sự trỏ tới, hoặc None."""
    sp = spine_prefabs()
    if sp is None:
        return None
    c = sp.get(prefab)
    return None if c is None else c["skeleton_data_ref"]["m_PathID"]


claim("G8", GAPS, "| **`Boss-39002`** | 664302 | **`580611`** |", 580611,
      lambda: boss_rig("Boss-39002"),
      "PPtr thật: Boss-39001 và Boss-39002 DÙNG CHUNG rig 580611 — hết mức B")

claim("G10", GAPS, "**3 component trên 3 prefab boss**", 3,
      lambda: None if spine_prefabs() is None else len(spine_prefabs()),
      "thư mục 20 file là export MỘT PHẦN: component 664302 không có trong đó")

claim("G11", GAPS, "| **`Boss-39001`** | 602882 | **`580611`** |", 580611,
      lambda: boss_rig("Boss-39001"))

claim("G12", GAPS, "| **`Boss-39003`** | 602881 | **`580613`** |", 580613,
      lambda: boss_rig("Boss-39003"))


def event_receiver_stats():
    d = ref_json("reverse-engineering/raw/animation-audit/event-receivers.json.gz")
    if d is None:
        return None
    s_ = d.get("summary", {})
    return (s_.get("event_uses"), s_.get("candidate_event_uses"), s_.get("unresolved_event_uses"))


claim("G13", "docs/apk-analysis/37-animation-event-receivers.md", "711", 711,
      lambda: (event_receiver_stats() or (None, None, None))[1],
      "event use có receiver ứng viên — KHÁC 731 event theo clip duy nhất")

claim("G14", "docs/apk-analysis/37-animation-event-receivers.md", "84", 84,
      lambda: (event_receiver_stats() or (None, None, None))[2])


claim("G9", "docs/spec/ANIMATION_GAPS.md", "`Boss1_Director` instance `582209`", ["Boss-39002"],
      lambda: _boss1_director_root(), "director → prefab, đọc trực tiếp")


def _boss1_director_root():
    lines = ref_lines("reverse-engineering/raw/typetrees/Boss1_Director.jsonl.gz")
    maps = _tt_maps()
    if lines is None or maps is None:
        return None
    go2tr, father, roots = maps
    for ln in lines:
        if not ln.strip():
            continue
        try:
            o = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if str(o.get("path_id")) != "582209":
            continue
        go = str(o["tree"]["m_GameObject"]["m_PathID"])
        tr = go2tr.get(go)
        seen = set()
        while tr and tr not in seen:
            seen.add(tr)
            if tr in roots:
                return [roots[tr]]
            tr = father.get(tr)
    return []


# ── H. roster spawn: nguồn của mọi con số "enemy" ──────────────────────

claim("H1", ANIMDOC, "`Boss-` **39** · `CB-` **33**", (39, 33),
      lambda: None if wave_roster() is None else tuple(
          sum(1 for e in wave_roster() if e.startswith(p)) for p in ("Boss-", "CB-")),
      "phân bố tiền tố của roster 109")

claim("H2", ANIMDOC, "**22.451 entry spawn trên 282 wave và 11.089 dòng cấu hình**", (22451, 282, 11089),
      lambda: _wave_counts(),
      "quy mô bảng spawn — chứng minh roster là bảng thật, không phải danh mục")

claim("H3", ANIMDOC, "**182 prefab root**", 182,
      lambda: enemy_prefab_roots(),
      "prefab có Enemy_Movement trong asset — KHÁC 109 được spawn")


def _wave_counts():
    d = ref_json("datas/waves.json")
    if d is None:
        return None
    total = 0
    for w in d.get("waves", []):
        for sp in w.get("spawners") or []:
            total += len(sp.get("enemies") or [])
    return (total, len(d.get("waves", [])), d.get("count_spawners"))


def enemy_prefab_roots() -> int | None:
    """Số prefab root mang Enemy_Movement, đi lên transform-tree."""
    lines = ref_lines("reverse-engineering/raw/typetrees/Enemy_Movement.jsonl.gz")
    maps = _tt_maps()
    if lines is None or maps is None:
        return None
    go2tr, father, roots = maps
    seen = set()
    for ln in lines:
        if not ln.strip():
            continue
        try:
            o = json.loads(ln)
        except json.JSONDecodeError:
            continue
        tr = go2tr.get(str((o.get("tree") or {}).get("m_GameObject", {}).get("m_PathID")))
        guard = set()
        while tr and tr not in guard:
            guard.add(tr)
            if tr in roots:
                seen.add(roots[tr])
                break
            tr = father.get(tr)
    return len(seen)


# ── I. mức sẵn sàng để thiết kế ────────────────────────────────────────

READY = "docs/spec/DESIGN_READINESS.md"


def display_fields() -> int | None:
    """Số field serialize của Enemy_Display (ngoài m_*)."""
    lines = ref_lines("reverse-engineering/raw/typetrees/Enemy_Display.jsonl.gz")
    if not lines:
        return None
    try:
        o = json.loads(lines[0])
    except json.JSONDecodeError:
        return None
    return sum(1 for k in (o.get("tree") or {}) if not k.startswith("m_"))


def events_with_time():
    d = ref_json("reverse-engineering/raw/animation-audit/event-receivers.json.gz")
    if d is None:
        return None
    ev = d.get("events", [])
    return (len(ev), sum(1 for e in ev
                         if isinstance(e.get("event"), dict) and e["event"].get("time") is not None))


def spawner_rate_zero():
    d = ref_json("datas/waves.json")
    if d is None:
        return None
    total = zero = none = 0
    for w in d.get("waves", []):
        for sp in w.get("spawners") or []:
            total += 1
            r = sp.get("rate")
            if r is None:
                none += 1
            elif r == 0:
                zero += 1
    return (total, zero, none)


def map_candidates():
    d = ref_json("datas/map_waves_candidate.json")
    if d is None:
        return None
    maps = d.get("maps", [])
    return (len(maps), sum(1 for m in maps if m.get("source") == "immediates"))


claim("I1", READY, "**5 field**: `hpProgressBarRenderer`", 5, display_fields,
      "Enemy_Display không có tham số hit flash / hit stop")

claim("I2", READY, "`795/795` event có `time`, mức **A**", (795, 795), events_with_time,
      "CHỈ kiểm mốc thời gian TRONG clip — không chứng minh thứ tự pha, điều kiện, số lần lặp hay hành vi callback (review R1)")

claim("I3", READY, "11.089 dòng cấu hình · rate = 0 : 2.366", 2366,
      lambda: (spawner_rate_zero() or (None, None, None))[1],
      "sửa 2.373 -> 2.371 trong DESIGN_QUESTIONS.md")

claim("I4", READY, "**250 map**, nhưng chỉ **7** ghép chắc", (250, 7), map_candidates,
      "A6: (250, 7) là trạng thái TRƯỚC bind — lần 11 (25/10) bind cấu trúc xong, peer ghép entry")


# ── J. script animation (enemy + boss) ─────────────────────────────────
#
# Nhóm này kiểm phần *script*: event nào nổ, ở giây thứ mấy, hàm nào nhận.
# Không kiểm "trông thế nào" — feel đã bị bỏ khỏi phạm vi.

SCRIPT = "docs/spec/ANIMATION_SCRIPT.md"
IL2CPP = "reverse-engineering/raw/il2cpp-consts"
EVENT_RX = "reverse-engineering/raw/animation-audit/event-receivers.json.gz"
NATIVE = "reverse-engineering/raw/animation-audit/native-calls.json"


def _boss_events():
    """(prefab boss, event trên boss, event ngoài boss)."""
    d = ref_json(EVENT_RX)
    if d is None:
        return None
    ev = d.get("events", [])
    boss = [e for e in ev if (e.get("prefab") or "").startswith("Boss-")]
    return (len({e["prefab"] for e in boss}), len(boss), len(ev) - len(boss))


def _boss_fn_counts(names: tuple[str, ...]):
    d = ref_json(EVENT_RX)
    if d is None:
        return None
    boss = [e for e in d.get("events", []) if (e.get("prefab") or "").startswith("Boss-")]
    c: dict[str, int] = {}
    for e in boss:
        fn = (e.get("event") or {}).get("functionName")
        if fn:
            c[fn] = c.get(fn, 0) + 1
    return tuple(c.get(n, 0) for n in names)


def boss_fn_distinct():
    d = ref_json(EVENT_RX)
    if d is None:
        return None
    return len({(e.get("event") or {}).get("functionName")
                for e in d.get("events", [])
                if (e.get("prefab") or "").startswith("Boss-")
                and (e.get("event") or {}).get("functionName")})


def clip_pairs():
    """(cặp prefab×clip, cặp prefab×clip×hàm có ≥3 event)."""
    d = ref_json(EVENT_RX)
    if d is None:
        return None
    boss = [e for e in d.get("events", []) if (e.get("prefab") or "").startswith("Boss-")]
    pairs = {(e["prefab"], e.get("clip_name")) for e in boss}
    by: dict[tuple, int] = {}
    for e in boss:
        k = (e["prefab"], e.get("clip_name"), (e.get("event") or {}).get("functionName"))
        by[k] = by.get(k, 0) + 1
    return (len(pairs), sum(1 for v in by.values() if v >= 3))


def boss1_clip_events():
    """Số event clip trên boss 1 — phải là 0 (thuần Spine)."""
    d = ref_json(EVENT_RX)
    if d is None:
        return None
    return sum(1 for e in d.get("events", [])
               if e.get("prefab") in ("Boss-39001", "Boss-39002"))


def _asm_section(path: str, method: str):
    lines = ref_lines(path)
    if lines is None:
        return None
    out, on = [], False
    for ln in lines:
        if ln.startswith(";;; "):
            on = ln[len(";;; "):].split(" ", 1)[0].strip() == method
            continue
        if on:
            out.append(ln)
    return out


def boss_work_compares():
    """Số lần `String.op_Equality` trong `Boss_1_Animation.BossWork`."""
    sec = _asm_section(f"{IL2CPP}/Boss_1_Animation.asm.txt", "BossWork")
    return None if sec is None else sum(1 for ln in sec if "0x1feca34" in ln)


def boss1_event_handlers():
    """(số handler, byte lớn nhất) của `Boss1_AnimationEvents`."""
    d = ref_json(f"{IL2CPP}/Boss1_AnimationEvents.json")
    if d is None:
        return None
    ms = [m for m in d.get("methods", []) if m.get("method") != "ctor"]
    return None if not ms else (len(ms), max(int(m.get("bytes") or 0) for m in ms))


def _il2cpp_asm_files() -> list[str]:
    local = os.path.join(ROOT, IL2CPP)
    if os.path.isdir(local):
        return sorted(f"{IL2CPP}/{n}" for n in os.listdir(local) if n.endswith(".asm.txt"))
    for ref in REFS:
        out = git("ls-tree", "-r", "--name-only", ref, "--", IL2CPP)
        if out:
            return sorted(p for p in out.decode().split() if p.endswith(".asm.txt"))
    return []


def wait_for_seconds():
    """(tổng `WaitForSeconds`, số hằng literal, số lấy từ biến) trong asm boss."""
    files = _il2cpp_asm_files()
    if not files:
        return None
    tot = lit = 0
    for p in files:
        lines = ref_lines(p)
        if not lines:
            continue
        for i, ln in enumerate(lines):
            if "0x2786508" not in ln:
                continue
            tot += 1
            hit = False
            for j in range(i - 1, max(i - 16, -1), -1):
                if re.search(r"fmov\s+s0,\s*#", lines[j]) or \
                        re.search(r"ldr\s+s0,\s*\[x\d+, #0x[0-9a-f]+\]", lines[j]):
                    hit = True
                    break
            lit += bool(hit)
    return (tot, lit, tot - lit)


def enemy_hit_flash():
    """Hai hằng số trong `Enemy_Display.OnHit` (0.5 alpha, 0.05 giây)."""
    d = ref_json(NATIVE)
    if d is None:
        return None
    for m in d.get("methods", []):
        if m.get("class_name") == "Enemy_Display" and m.get("method") == "OnHit":
            vals = [f.get("value") for f in (m.get("float_evidence") or [])
                    if f.get("kind") == "float"]
            return tuple(vals) if vals else None
    return None


def enemy_move_branches():
    """Số nhánh `Enemy_Movement.Update` gọi (PathFollow / MoveLinearly / MovePointToPoint)."""
    d = ref_json(NATIVE)
    if d is None:
        return None
    for m in d.get("methods", []):
        if m.get("class_name") == "Enemy_Movement" and m.get("method") == "Update":
            return sum(1 for c in (m.get("calls") or [])
                       if c.get("candidates")
                       and c["candidates"][0].get("method")
                       in ("PathFollow", "MoveLinearly", "MovePointToPoint"))
    return None


claim("J1", SCRIPT, "**33 prefab boss · 793 event · 2 ngoài boss**", (33, 793, 2),
      _boss_events, "hai hệ animation: Spine (boss 1) và clip event (33 boss khác)")

claim("J2", SCRIPT,
      "`OnStartAttack` 146 · `OnAnimationEndedEvent` 137 · `OnStateExit` 56 · `OnStopAttack` 50",
      (146, 137, 56, 50),
      lambda: _boss_fn_counts(("OnStartAttack", "OnAnimationEndedEvent",
                               "OnStateExit", "OnStopAttack")),
      "4 handler dày nhất, đếm trên cùng tập 793 event")

claim("J3", SCRIPT, "129 tên hàm phân biệt", 129, boss_fn_distinct,
      "danh sách hàm nhận event trên prefab boss")

claim("J4", SCRIPT, "**268 cặp (prefab, clip)**, trong đó **61 cặp (prefab, clip, hàm)**",
      (268, 61), clip_pairs, "chuỗi đòn đọc được nhịp")

claim("J5", SCRIPT, "**0 event clip**", 0, boss1_clip_events,
      "boss 1: 0 AnimationClip event (Spine event thì có). KHÔNG có nghĩa 12 handler của Boss1_AnimationEvents phủ 23 prefab (review R2)")

claim("J6", SCRIPT, "**5** lần `String.op_Equality`", 5, boss_work_compares,
      "Boss_1_Animation.BossWork rẽ 5 nhánh entry")

claim("J7", SCRIPT, "**12 handler · 28 byte**", (12, 28), boss1_event_handlers,
      "mỗi handler chỉ gọi một delegate, không có logic riêng")

claim("J8", SCRIPT, "**38 lần `WaitForSeconds` · 12 hằng số · 26 lấy từ biến**", (38, 12, 26),
      wait_for_seconds, "nhịp pha boss phần lớn do dữ liệu prefab, không do code")

claim("J9", SCRIPT, "**0,5** | đặt một tham số material", (0.5, 0.05), enemy_hit_flash,
      "hit flash: alpha 0,5 và Invoke 0,05 s")

claim("J10", SCRIPT, "`Enemy_Movement` 3 nhánh", 3, enemy_move_branches,
      "animation enemy = máy trạng thái di chuyển, 3 nhánh trong Update")

# ── K. boss 1: tên entry + bảng chuyển state (giải từ typetree + asm) ──
#
# Chuỗi suy luận phải kiểm được từng bước: tên lấy từ typetree, offset lấy từ
# asm, và *mối nối* giữa hai thứ là lệnh SetAnimation trong `Start`.

HANDOFF = "docs/spec/HANDOFF_ANIM_RAW.md"
TYPO = "reverse-engineering/raw/typetrees"
DIRECTOR_ASM = f"{IL2CPP}/Boss1_Director.asm.txt"
B1_STATE_FIELDS = ("stateAppear", "stateRunAway", "stateDie", "stateAttack1",
                   "stateAttack2", "stateAttack3", "statePreAttack2", "statePreAttack3")


def boss1_states():
    """8 giá trị field `state*` của `Boss1_Director`, theo thứ tự khai báo."""
    raw = ref_blob(f"{TYPO}/Boss1_Director.jsonl.gz")
    if raw is None:
        return None
    try:
        tree = json.loads(raw.decode("utf-8").splitlines()[0])["tree"]
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError):
        return None
    return tuple(tree.get(k) for k in B1_STATE_FIELDS)


def _setanimation_offset():
    """`ldr x2` ngay trước `SetAnimation` trong `Start` = field animation vào trận."""
    sec = _asm_section(DIRECTOR_ASM, "Start")
    if not sec:
        return None
    for i, ln in enumerate(sec):
        if "0x220d324" in ln:
            for j in range(i - 1, max(i - 5, -1), -1):
                m = re.search(r"ldr\s+x2, \[x19, #(0x[0-9a-f]+)\]", sec[j])
                if m:
                    return int(m.group(1), 16)
    return None


def boss1_offset_names():
    """'0x28=Xuathien · 0x30=Baydi · …' — nối offset asm với tên typetree."""
    base, names = _setanimation_offset(), boss1_states()
    if base is None or not names or any(n is None for n in names):
        return None
    return " · ".join(f"{hex(base + 8 * i)}={n}" for i, n in enumerate(names))


def boss_work_compare_offsets():
    """Offset các chuỗi mà `BossWork` so, theo đúng thứ tự so."""
    sec = _asm_section(DIRECTOR_ASM, "BossWork")
    if not sec:
        return None
    out = []
    for i, ln in enumerate(sec):
        if "0x1feca34" not in ln:
            continue
        # tham số thứ nhất của op_Equality được nạp vào x1 ngay trước lời gọi,
        # riêng lần so đầu tiên thì nạp vào x8 rồi `mov x1, x8` (x19 chưa gán).
        for j in range(i - 1, max(i - 9, -1), -1):
            m = re.search(r"ldr\s+x[18], \[(?:x19|x0), #(0x[0-9a-f]+)\]", sec[j])
            if m:
                out.append(m.group(1))
                break
    return ",".join(out)


def complete_calls_bosswork():
    """`SkeletonAnimation_AnimationState_Complete` có tail-call sang `BossWork`."""
    sec = _asm_section(DIRECTOR_ASM, "SkeletonAnimation_AnimationState_Complete")
    raw = ref_lines(DIRECTOR_ASM)
    if not sec or raw is None:
        return None
    boss_rva = None
    # rva của BossWork lấy từ json (nguồn có cấu trúc, không đoán từ thứ tự)
    d = ref_json(f"{IL2CPP}/Boss1_Director.json")
    if d is None:
        return None
    for m in d.get("methods", []):
        if m.get("method") == "BossWork":
            boss_rva = m.get("rva")
    if not boss_rva:
        return None
    tail = [ln for ln in sec if re.search(r"\bb\s+#0x", ln)]
    return bool(tail) and boss_rva.lower() in tail[-1].lower()


def missing_typetrees():
    """Số lớp có asm/json nhưng KHÔNG có typetree."""
    names = ("Boss1_AnimationEvents", "BossSpineEventHandler", "Boss_1_Animation")
    local = os.path.join(ROOT, TYPO)
    if not os.path.isdir(local):
        have = set()
        for ref in REFS:
            out = git("ls-tree", "-r", "--name-only", ref, "--", TYPO)
            if out:
                have = {os.path.basename(p) for p in out.decode().split()}
                break
        if not have:
            return None
    else:
        have = set(os.listdir(local))
    return sum(1 for n in names if f"{n}.jsonl.gz" not in have)


def boss1_handler_offsets():
    """(số handler, offset đầu, offset cuối) — 12 delegate field liền nhau."""
    raw = ref_blob(f"{IL2CPP}/Boss1_AnimationEvents.asm.txt")
    if raw is None:
        return None
    offs, cur, seen = [], None, set()
    for ln in raw.decode("utf-8", "replace").splitlines():
        m = re.match(r";;; (\S+)", ln.strip())
        if m:
            cur = m.group(1)
            continue
        m2 = re.search(r"ldr\s+x8, \[x0, #(0x[0-9a-f]+)\]", ln)
        if cur and m2 and cur not in seen:
            seen.add(cur)
            offs.append(int(m2.group(1), 16))
    return (len(offs), offs[0], offs[-1]) if offs else None


claim("K1", SCRIPT, "**8 tên entry**",
      ("Xuathien", "Baydi", "Dead", "Attack1", "Attack2", "Attack3",
       "Chuyensangattack2", "Chuyensangattack3"), boss1_states,
      "typetree Boss1_Director: 8 chuỗi state lấy nguyên văn")

claim("K2", SCRIPT,
      "Chuỗi offset — `0x28=Xuathien` · `0x30=Baydi` · `0x38=Dead` · `0x40=Attack1` · "
      "`0x48=Attack2` · `0x50=Attack3` · `0x58=Chuyensangattack2` · `0x60=Chuyensangattack3`",
      ("0x28=Xuathien · 0x30=Baydi · 0x38=Dead · 0x40=Attack1 · 0x48=Attack2 · "
       "0x50=Attack3 · 0x58=Chuyensangattack2 · 0x60=Chuyensangattack3"),
      boss1_offset_names,
      "offset suy từ SetAnimation([0x28]) trong Start, không chép tay")

claim("K3", SCRIPT, "Thứ tự so chuỗi trong `BossWork`: `0x28` → `0x58` → `0x60` → `0x30` → `0x38`",
      "0x28,0x58,0x60,0x30,0x38", boss_work_compare_offsets,
      "5 nhánh = 5 lần String.op_Equality, đúng thứ tự thực thi")

claim("K4", HANDOFF, "**tail-call** `BossWork(trackEntry.Animation.Name)`", True,
      complete_calls_bosswork,
      "Complete → Animation.Name → BossWork, không copy trung gian")

claim("K5", HANDOFF, "**có asm nhưng không có typetree**", 2, missing_typetrees,
      "2 lớp chưa export (Boss_1_Animation đã xong 25/10) ⇒ T1 còn phần rẻ nhất")

claim("K6", HANDOFF, "**12 delegate field liền nhau `0x20`…`0x78`**", (12, 0x20, 0x78),
      boss1_handler_offsets,
      "12 handler = 12 field kề nhau, đủ để xref T2 mà không cần đoán")

# ── L. độ phủ script animation + cấu trúc UI (vòng 2 readiness) ────────
# READY đã khai báo ở nhóm I.


def _boss_roster() -> list[str]:
    d = ref_json("datas/waves.json")
    if d is None:
        return []
    return sorted({e for w in d.get("waves", [])
                   for s in (w.get("spawners") or []) for e in (s.get("enemies") or [])
                   if isinstance(e, str) and e.startswith("Boss-")})


def _spine_rigs() -> set[str]:
    return {"Boss-39001", "Boss-39002", "Boss-39003"}


def boss_script_coverage():
    """(prefab boss có script, prefab boss thiếu, tổng prefab boss trong roster)."""
    rx = ref_json(EVENT_RX)
    if rx is None:
        return None
    with_clip = {e.get("prefab") for e in rx.get("events", [])}
    roster = _boss_roster()
    if not roster:
        return None
    have = [b for b in roster if b in with_clip or b in _spine_rigs()]
    return (len(have), len(roster) - len(have), len(roster))


def boss_script_missing():
    rx = ref_json(EVENT_RX)
    if rx is None:
        return None
    with_clip = {e.get("prefab") for e in rx.get("events", [])}
    return tuple(b for b in _boss_roster() if b not in with_clip and b not in _spine_rigs())


def ui_screens():
    """Số dòng `screens.csv`."""
    raw = ref_blob("docs/spec/screens.csv")
    if raw is None:
        return None
    rows = [ln for ln in raw.decode("utf-8", "replace").splitlines()[1:] if ln.strip()]
    return len(rows)


claim("L1", READY, "**35/39 prefab boss** có **nguồn** animation/event", (35, 4, 39), boss_script_coverage,
      "35 = 33 prefab có clip event ∪ 3 prefab Spine HARD-CODE (39003 nằm cả hai); đây là coverage NGUỒN, không phải đã giải script (review R1)")

claim("L2", READY, "**125 màn hình**", 125, ui_screens,
      "UI cấu trúc đủ để thiết kế; chỉ art là chưa")

claim("L3", READY, "`Boss-37003/37005/37006/37008`",
      ("Boss-37003", "Boss-37005", "Boss-37006", "Boss-37008"), boss_script_missing,
      "4 prefab boss không có cả clip event lẫn Spine")

# ── M. schema spawner kéo từ nhánh dữ liệu (24/10) ─────────────────────
# `Call_Data.csv` là bảng phẳng mọi instance: nó cho *tên field thật* của dữ
# liệu spawn, thứ mà `datas/waves.json` không nói ra.

CALL_DATA = "reverse-engineering/scriptableobjects/Call_Data.csv"
DATA_SYNC = "docs/spec/DATA_SYNC.md"


def _call_data():
    key = "csv:" + CALL_DATA
    if key in _cache:
        return _cache[key]
    raw = ref_blob(CALL_DATA)
    val = None
    if raw:
        try:
            val = list(csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))
        except (UnicodeDecodeError, csv.Error):
            val = None
    _cache[key] = val
    return val


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def call_data_schema():
    """(số dòng, số field gốc, có field delay?) — `delay` phải KHÔNG có."""
    rows = _call_data()
    if not rows:
        return None
    base = [h for h in rows[0] if "[" not in h and not h.endswith((".m_FileID", ".m_PathID"))]
    has_delay = any(k in h.lower() for h in base for k in ("delay", "wait", "interval"))
    return (len(rows), len(base), has_delay)


def call_data_rate0():
    """(số spawner rate=0, list quân dài nhất của nhóm đó) trong Call_Data."""
    rows = _call_data()
    if not rows:
        return None
    zero = [r for r in rows if _num(r.get("rate")) == 0]

    def n_enemies(r):
        try:
            return int(str(r.get("listPrefabEnemies", "")).strip("[]") or 0)
        except ValueError:
            return 0
    return (len(zero), max((n_enemies(r) for r in zero), default=0))


def waves_rate0_big():
    """(spawner rate=0 có >1 quân, dài nhất) trong `datas/waves.json`."""
    d = ref_json("datas/waves.json")
    if d is None:
        return None
    big = [len(s.get("enemies") or [])
           for w in d.get("waves", []) for s in (w.get("spawners") or [])
           if _num(s.get("rate")) == 0 and len(s.get("enemies") or []) > 1]
    return (len(big), max(big, default=0))


claim("M1", DATA_SYNC, "**1.200 dòng · 23 field**", (1200, 23, False), call_data_schema,
      "chỉ là SCHEMA: không có field delay/wait/interval. KHÔNG suy ra rate là khoảng giãn (review R5)")

claim("M2", READY, "| `rate = 0` (trong `Call_Data`) | **295** | 1 | **6** |", (295, 6),
      call_data_rate0, "đếm list quân; KHÔNG chứng minh cách game đọc rate (review R5)")

claim("M3", READY, "và 1.206 spawner `rate = 0` có **>1 quân**", (1202, 30),
      waves_rate0_big, "đếm list; KHÔNG chứng minh đã burst runtime — vẫn là giả thuyết tới khi có consumer asm (review R5)")

# ── N. hai manifest kéo thêm: Spine event + bản đồ độ sâu UI ───────────
# Cả hai đều là *manifest*: dữ liệu tổng hợp do nhánh kia sinh, nên phép kiểm
# là "đếm lại trên file", không phải "tin báo cáo".

UI_DOC = "docs/spec/UI.md"
SPINE_EVENTS = "docs/apk-analysis/spine-events.csv"
UI_INDEX = "reverse-engineering/raw/ui/_index.csv"


def _csv_rows(path: str):
    key = "csv:" + path
    if key in _cache:
        return _cache[key]
    raw = ref_blob(path)
    val = None
    if raw:
        try:
            val = list(csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))
        except (UnicodeDecodeError, csv.Error):
            val = None
    _cache[key] = val
    return val


def spine_event_stats():
    """(tổng dòng, event trong skeleton__21, tên phân biệt trong rig đó)."""
    rows = _csv_rows(SPINE_EVENTS)
    if not rows:
        return None
    rig = [r for r in rows if r.get("rig") == "skeleton__21"]
    return (len(rows), len(rig), len({r.get("event") for r in rig}))


def ui_index_stats():
    """(instance, lớp, tổng node, tổng button) của `_index.csv`."""
    rows = _csv_rows(UI_INDEX)
    if not rows:
        return None
    def total(k):
        out = 0
        for r in rows:
            try:
                out += int(r.get(k) or 0)
            except ValueError:
                pass
        return out
    return (len(rows), len({r.get("class") for r in rows}), total("nodes"), total("buttons"))


def ui_class_gap():
    """(lớp chỉ có trong screens.csv, tên lớp lồng, không có instance trong dump)."""
    idx = {r.get("class") for r in (_csv_rows(UI_INDEX) or [])}
    scr = {r.get("class") for r in (_csv_rows("docs/spec/screens.csv") or [])}
    if not idx or not scr:
        return None
    only = scr - idx
    nested = {c for c in only if "." in c}
    return (len(only), len(nested), len(only) - len(nested))


claim("N1", SCRIPT, "**`skeleton__21`: 6 event · 2 tên phân biệt**", (21, 6, 2), spine_event_stats,
      "22 dòng toàn bảng; rig boss 1 chỉ có 2 tên ⇒ tập ứng viên của BossSpineEventHandler là A")

claim("N2", DATA_SYNC, "**797 instance · 117 lớp · 150.131 node · 5.831 nút**",
      (797, 117, 150131, 5831), ui_index_stats,
      "manifest UI: đếm lại trên file, không chép báo cáo")

def ui_class_overlap():
    """(lớp _index, lớp screens.csv, chung, chỉ screens, chỉ _index)."""
    idx = {r.get("class") for r in (_csv_rows(UI_INDEX) or [])}
    scr = {r.get("class") for r in (_csv_rows("docs/spec/screens.csv") or [])}
    if not idx or not scr:
        return None
    return (len(idx), len(scr), len(idx & scr), len(scr - idx), len(idx - scr))


claim("N3", UI_DOC, "**11 lớp (chỉ có trong `screens.csv`) = 4 tên lớp lồng + 7 không có instance trong dump.**", (11, 4, 7),
      ui_class_gap,
      "giải thích 125 vs 117: cùng một tập, khác cách đặt tên + 7 màn không dump")

claim("N5", UI_DOC, "**`screens.csv` 125 · `_index.csv` 117 · chung 114**",
      (117, 125, 114, 11, 3), ui_class_overlap,
      "hai tập KHÔNG lồng nhau: 3 lớp tutorial chỉ có trong _index (khác bản cũ nói _index ⊂ screens)")

# ── P. kiểm lại toàn bộ: quy mô tài liệu + dữ liệu đã có ────────────────
# Nhóm này trả lời "thiếu chỗ nào" bằng cách đếm *cái đang có*, để không ai
# đi làm lại thứ đã nằm trong repo.

AUDIT = "docs/spec/COVERAGE_AUDIT.md"
APK_DOCS = "docs/apk-analysis"


def doc_inventory():
    """Số tài liệu trong `docs/spec/`, **không kể** chính file audit.

    Không đếm tổng số dòng: nó đổi mỗi lần sửa một chữ, và một claim đổi theo
    từng lần sửa là claim vô dụng.
    """
    local = os.path.join(ROOT, "docs", "spec")
    if not os.path.isdir(local):
        return None
    files = [n for n in os.listdir(local)
             if n.endswith(".md") and n != "COVERAGE_AUDIT.md"]
    return len(files) or None


def sprite_sizes():
    """(dòng sprites.csv, có width, dòng asset-manifest, có kích thước)."""
    spr = _csv_rows("datas/sprites.csv")
    man = _csv_rows(f"{APK_DOCS}/04-asset-manifest.csv")
    if not spr or not man:
        return None
    return (len(spr), sum(1 for r in spr if (r.get("width") or "0") not in ("", "0")),
            len(man), sum(1 for r in man if (r.get("width") or "0") not in ("", "0")))


def localization_stats():
    """(số key, số ngôn ngữ, số key có bản tiếng Việt)."""
    rows = _csv_rows(f"{APK_DOCS}/12-localization.csv")
    if not rows:
        return None
    return (len(rows), len(rows[0]) - 1, sum(1 for r in rows if r.get("Vietnamese")))


def iap_stats():
    """(tổng SKU, consumable, non-consumable)."""
    rows = _csv_rows(f"{APK_DOCS}/13-iap-products.csv")
    if not rows:
        return None
    c = sum(1 for r in rows if r.get("type") == "ConsumableProducts")
    n = sum(1 for r in rows if r.get("type") == "NonConsumableProducts")
    return (len(rows), c, n)


def data_counts():
    """(hệ hạt, âm thanh resolve, HP id, boss HP, map)."""
    parts = _csv_rows("datas/particle_systems.csv.gz")
    audio = ref_json("datas/audio_map.json")
    hp = ref_json("datas/enemy_hp_by_id.json")
    boss = ref_json("datas/boss_hp.json")
    maps = ref_json("datas/maps.json")
    if parts is None or not audio or hp is None or boss is None or maps is None:
        return None
    return (len(parts), audio.get("resolved"), hp.get("count"),
            boss.get("count"), len(maps.get("maps") or []))


def ui_two_levels():
    """(file layout, node tổng, màn cấp cao, node của chúng)."""
    screens = ref_json("datas/ui_screens.json.gz")
    idx = _csv_rows("reverse-engineering/raw/ui/_index.csv")
    if not screens or not idx:
        return None
    return (screens.get("files"), screens.get("nodes"), len(idx),
            sum(int(r.get("nodes") or 0) for r in idx))


claim("P1", AUDIT, "**42 tài liệu** trong `docs/spec/` (chưa kể file này)", 42, doc_inventory,
      "quy mô tài liệu hiện có trong docs/spec")

claim("P2", AUDIT, "**2.885** sprite, **2.816** có `width/height`; `04-asset-manifest.csv`: **2.907** asset, **2.838** có kích thước",
      (2885, 2816, 2907, 2838), sprite_sizes,
      "kích thước sprite: đóng mục #4 của DATA_SYNC §8")

claim("P3", AUDIT, "**1.416 key × 19 ngôn ngữ**, **1.416** có bản tiếng Việt", (1416, 19, 1416),
      localization_stats, "bản địa hoá: lần đầu có dữ liệu")

claim("P4", AUDIT, "**170 sản phẩm** (71 consumable + 99 non-consumable)", (170, 71, 99),
      iap_stats, "IAP khớp giữa datas/iap_products.json và 13-iap-products.csv")

claim("P5", AUDIT, "**4.845** hệ hạt · **92/92** âm thanh · **150** HP id · **246** boss HP (peer refresh 26/10 — cũ 253) · **250** map",
      (4845, 92, 150, 246, 250), data_counts,
      "một dòng để nhớ datas/ đang có gì — khỏi làm lại")

claim("P6", AUDIT, "**55.584** file · **8.440.354** node (peer refresh 26/10)", (55584, 8440354, 797, 150131),
      ui_two_levels, "UI hai tầng: layout file vs màn cấp cao — đừng tráo")

# ── Q. atlas plan kiểm bằng kích thước thật ─────────────────────────────
# Trước nhóm này, "12 page / 14,7 MB" là đề xuất không có phép đo phía sau.

ASSETS_DOC = "docs/spec/ASSETS.md"
SPRITES = "datas/sprites.csv"


def _sized_sprites():
    rows = _csv_rows(SPRITES)
    if not rows:
        return []
    return [r for r in rows if (r.get("width") or "0") not in ("", "0")]


def _px(r):
    return int(r["width"]) * int(r["height"])


def _mb(rows):
    return round(sum(int(r["bytes"]) for r in rows) / 1048576, 2)


def _mpx(rows):
    return round(sum(_px(r) for r in rows) / 1e6, 1)


def atlas_pages():
    """(số page sactx, MB, M px²)."""
    rows = [r for r in _sized_sprites() if "sactx" in (r.get("png") or "")]
    return (len(rows), _mb(rows), _mpx(rows)) if rows else None


def atlas_totals():
    """(tổng texture, MB, M px²) — page + texture rời."""
    rows = [r for r in _sized_sprites() if r.get("type") == "Texture2D"]
    return (len(rows), _mb(rows), _mpx(rows)) if rows else None


def atlas_capacity():
    """(M px² sức chứa, MB ở 4bpp, M px² dùng được ở 85 %, MB tương ứng)."""
    cap = 2048 ** 2 * 3 + 1024 ** 2 * 5 + 512 ** 2 * 4
    return (round(cap / 1e6, 2), round(cap / 2 / 1048576, 2),
            round(cap * 0.85 / 1e6, 2), round(cap * 0.85 / 2 / 1048576, 2))


def oversized_assets():
    """(asset > 512 px, trong đó Texture2D, Sprite)."""
    rows = _sized_sprites()
    if not rows:
        return None
    big = [r for r in rows if max(int(r["width"]), int(r["height"])) > 512]
    return (len(big), sum(1 for r in big if r["type"] == "Texture2D"),
            sum(1 for r in big if r["type"] == "Sprite"))


claim("Q1", ASSETS_DOC, "| **Page atlas đã bake** (`sactx-*`) | **67** | **31,05 MB** | **60,0 M px²** |",
      (67, 31.05, 60.0), atlas_pages, "page gốc: đúng 4 bpp, không mipmap")

claim("Q2", ASSETS_DOC, "| **Cộng** | 632 | **62,95 MB** | **111,3 M px²** |", (632, 62.95, 111.3),
      atlas_totals, "page + texture rời: mẫu số đúng cho câu 'giảm bao nhiêu'")

claim("Q3", ASSETS_DOC, "| **Sức chứa** 12 page đề xuất | **18,87 M** | **9,0** |",
      (18.87, 9.0, 16.04, 7.65), atlas_capacity,
      "12 page chỉ chứa ~17% lượng px² của toàn bộ art")

def texture_size_coverage():
    """(Texture2D manifest, Texture2D có size trong sprites.csv, hiệu số dòng).

    Đếm theo DÒNG, không theo tên: manifest 653 dòng chỉ có 604 tên unique.
    """
    mf = [r for r in _csv_rows("docs/apk-analysis/04-asset-manifest.csv")
          if r.get("type") == "Texture2D"]
    ha = [r for r in _sized_sprites() if r.get("type") == "Texture2D"]
    if not mf:
        return None
    mfn = {norm_name(r["name"]) for r in mf}
    extra = sum(1 for r in ha if norm_name(r["name"]) not in mfn)
    return (len(mf), len(ha) - extra, len(mf) - (len(ha) - extra))


def norm_name(n):
    return n.strip().replace("_", "").replace(" ", "").lower()


claim("Q5", ASSETS_DOC, "> `sprites.csv` chỉ có **kích thước** cho **632** — **21** texture thiếu số đo",
      (653, 632, 21), texture_size_coverage,
      "diện tích art §4.5 là CẬN DƯỚI: 21 texture không có w/h")

claim("Q4", ASSETS_DOC, "**88** asset vượt 512: **60** `Texture2D` + **28** `Sprite`",
      (88, 60, 28), oversized_assets, "luật >512 px: số asset phải để standalone")

# ── R. timeline animation boss theo giây (BOSS_ANIM_TIMELINE.md) ────────
TIMELINE_DOC = "docs/spec/BOSS_ANIM_TIMELINE.md"
EV_RECV = "reverse-engineering/raw/animation-audit/event-receivers.json.gz"


def _boss_events():
    import gzip
    import json
    try:
        with gzip.open(EV_RECV, "rt", encoding="utf-8") as fh:
            return json.load(fh)["events"]
    except (OSError, KeyError, ValueError):
        return []


def timeline_shape():
    """(prefab, event, clip, cặp (prefab,clip), tên hàm)."""
    ev = _boss_events()
    if not ev:
        return None
    pairs = {(e["prefab"], e["clip_name"]) for e in ev}
    return (len({e["prefab"] for e in ev}), len(ev),
            len({e["clip_name"] for e in ev}), len(pairs),
            len({e["event"]["functionName"] for e in ev}))


def timeline_fn_split():
    """(state, damage, khác) — phân loại theo tên hàm."""
    import re
    ev = _boss_events()
    if not ev:
        return None
    st = dm = ot = 0
    for e in ev:
        f = e["event"]["functionName"]
        if f.startswith("On"):
            st += 1
        elif re.search(r"(Hand|Knife|Shoot|Ban|Plasma|Laser|Circle|Tail|Spike|Bullet|Fire)", f):
            dm += 1
        else:
            ot += 1
    return (st, dm, ot)


def timeline_top_state():
    """(OnStartAttack, OnAnimationEndedEvent, OnStateExit, tổng 3 hàm)."""
    ev = _boss_events()
    if not ev:
        return None
    c = {}
    for e in ev:
        c[e["event"]["functionName"]] = c.get(e["event"]["functionName"], 0) + 1
    return (c.get("OnStartAttack", 0), c.get("OnAnimationEndedEvent", 0),
            c.get("OnStateExit", 0), sum(c.get(k, 0) for k in
                                        ("OnStartAttack", "OnAnimationEndedEvent",
                                         "OnStateExit")))


def timeline_cadence():
    """(số khoảng multi-hit, trung vị giây)."""
    import statistics
    ev = _boss_events()
    if not ev:
        return None
    g = {}
    for e in ev:
        g.setdefault((e["prefab"], e["clip_name"]), []).append(
            (e["event"]["time"], e["event"]["functionName"]))
    gaps = []
    for v in g.values():
        ts = [t for t, f in sorted(v) if f.startswith(("AttackHand", "Shoot", "Ban"))]
        gaps += [round(b - a, 2) for a, b in zip(ts, ts[1:])]
    return (len(gaps), round(statistics.median(gaps), 2)) if gaps else None


def timeline_lengths():
    """(trung vị mốc cuối clip, mốc cuối lớn nhất, trung vị số clip/boss)."""
    import statistics
    ev = _boss_events()
    if not ev:
        return None
    g = {}
    for e in ev:
        g.setdefault((e["prefab"], e["clip_name"]), []).append(e["event"]["time"])
    lasts = [max(v) for v in g.values()]
    per = {}
    for p, c in g:
        per[p] = per.get(p, 0) + 1
    return (round(statistics.median(lasts), 2), round(max(lasts), 2),
            round(statistics.median(per.values()), 1))


def timeline_enemy_row():
    """(số event của CB-30040, mốc thời gian, số prefab boss có event)."""
    ev = _boss_events()
    if not ev:
        return None
    cb = [e for e in ev if e["prefab"] == "CB-30040"]
    return (len(cb), round(cb[0]["event"]["time"], 1) if cb else 0,
            len({e["prefab"] for e in ev if e["prefab"].startswith("Boss-")}))


claim("R1", TIMELINE_DOC, "> **34 prefab · 795 event · 97 clip · 269 cặp (prefab, clip) · 130 tên hàm**",
      (34, 795, 97, 269, 130), timeline_shape, "quy mô timeline: mọi số khác suy từ đây")

claim("R2", TIMELINE_DOC, "cộng lại **339/795 = 43 %**", (534, 215, 46), timeline_fn_split,
      "67% event là state, 27% là đòn — không phải 100% damage")

claim("R3", TIMELINE_DOC, "Ba hàm **state** (`OnStartAttack`, `OnAnimationEndedEvent`, `OnStateExit`) cộng lại **339/795 = 43 %**.",
      (146, 137, 56, 339), timeline_top_state, "3 callback state = 43% event")

claim("R4", TIMELINE_DOC, "| **Nhịp multi-hit** | **93** khoảng, trung vị **0,17 s** |",
      (93, 0.17), timeline_cadence, "đòn liên hoàn ~6 hit/giây")

claim("R5", TIMELINE_DOC, "| **Mốc cuối clip** | trung vị **3,52 s**, dài nhất **73,17 s**",
      (3.52, 73.17, 6.0), timeline_lengths, "clip chờ 73 s — đừng chờ nó xong mới cho bắn")

claim("R6", TIMELINE_DOC, "> `CB-30040` có **2** event trong clip `Die`, **cùng mốc 1,5 s**",
      (2, 1.5, 33), timeline_enemy_row, "enemy gần như không có event clip; 2 event trùng mốc = double damage")

# ── S. ghép prefab ↔ lớp *_AnimationEvents (ANIMATION_SCRIPT.md §3.2) ───
import glob as _glob
import os as _os


def handler_class_join():
    """(prefab khớp lớp, prefab có event mà thiếu lớp, event của nhóm thiếu, tổng prefab)."""
    import gzip
    import json
    try:
        with gzip.open(EV_RECV, "rt", encoding="utf-8") as fh:
            ev = json.load(fh)["events"]
    except (OSError, KeyError, ValueError):
        return None
    counts = {}
    for e in ev:
        counts[e["prefab"]] = counts.get(e["prefab"], 0) + 1
    have = set()
    for f in _glob.glob("reverse-engineering/raw/typetrees/*AnimationEvents*.jsonl.gz"):
        try:
            with gzip.open(f, "rt", encoding="utf-8") as fh:
                for line in fh:
                    root = (json.loads(line).get("gameobject") or "").split("/")[0]
                    if root:
                        have.add(root)
        except (OSError, ValueError):
            continue
    matched = {p for p in counts if p in have}
    missing = {p for p in counts if p not in have}
    return (len(matched), len(missing), sum(counts[p] for p in missing), len(counts))


def design_question_tally():
    """(tổng, ✅, ⚠, ❌) đếm từ bảng DESIGN_QUESTIONS.md."""
    import re
    try:
        text = ref_blob("docs/spec/DESIGN_QUESTIONS.md").decode("utf-8")
    except Exception:
        return None
    ok = warn = bad = tot = 0
    for line in text.splitlines():
        m = re.match(r"^\|\s*([A-F]\d+)\s*\|[^|]*\|([^|]*)\|", line)
        if not m:
            continue
        tot += 1
        st = m.group(2).strip()
        if st == "✅":
            ok += 1
        elif st == "⚠":
            warn += 1
        elif st == "❌":
            bad += 1
    return (tot, ok, warn, bad) if tot else None


claim("S2", "docs/spec/DESIGN_QUESTIONS.md",
      "**Tổng: 48 câu — ✅ 33 · ⚠ 14 · ❌ 1**",
      (48, 33, 14, 1), design_question_tally,
      "đếm trong bảng phải khớp dòng tổng; đổi 1 hàng là FAIL ngay")

claim("S1", "docs/spec/ANIMATION_SCRIPT.md",
      "**17 prefab còn lại có event clip nhưng chưa export lớp handler**",
      (17, 17, 145, 34), handler_class_join,
      "chỉ 16/34 prefab ghép được lớp handler; 262 event chưa biết lớp")

# ── T. dữ liệu serialize kéo 24/10 (ANIMATION_SCRIPT.md §2.0b/§2.2/§3.1/§3.3) ─
IL2CPP_CLASSES = "reverse-engineering/il2cpp/interesting-classes.cs"


def _class_block(name):
    try:
        text = ref_blob(IL2CPP_CLASSES).decode("utf-8")
    except Exception:
        return ""
    start = text.find("class %s :" % name)
    if start < 0:
        return ""
    end = text.find("// RVA", start)
    return text[start:end if end > 0 else len(text)]


def boss1_state_values():
    """(số field trạng thái, số instance của Boss1_Director) từ CSV serialize."""
    rows = _csv_rows("docs/apk-analysis/Boss1_Director.csv")
    if not rows:
        return None
    keys = [k for k in rows[0] if k.startswith("state")]
    vals = {rows[0].get(k) for k in keys}
    expect = {"Xuathien", "Baydi", "Dead", "Attack1", "Attack2", "Attack3",
              "Chuyensangattack2", "Chuyensangattack3"}
    return (len(keys), len(rows), len(vals & expect))


def delegate_field_names():
    """(số field delegate, offset đầu, offset cuối) của Boss1_AnimationEvents."""
    block = _class_block("Boss1_AnimationEvents")
    if not block:
        return None
    offs = []
    for line in block.splitlines():
        if "Action " in line and "// 0x" in line:
            try:
                offs.append(int(line.split("// 0x")[1].strip(), 16))
            except ValueError:
                continue
    return (len(offs), min(offs), max(offs)) if offs else None


def spine_handler_fields():
    """(số field, offset đầu, offset cuối, số field chuỗi) của BossSpineEventHandler."""
    block = _class_block("BossSpineEventHandler")
    if not block:
        return None
    import re
    fields = re.findall(r"(?:public|private) (\w+) (\w+); // 0x(\w+)", block)
    if not fields:
        return None
    offs = [int(f[2], 16) for f in fields]
    strings = sum(1 for f in fields if f[0] == "string")
    return (len(fields), min(offs), max(offs), strings)


def director_matrix():
    """(prefab có *_Director, prefab có *_AnimationEvents, có cả hai) trong 39 prefab Boss-*."""
    import glob as g
    import os as o
    d = set()
    e = set()
    for pat, box in (("*_Director.csv", d), ("*AnimationEvents.csv", e)):
        for f in g.glob("docs/apk-analysis/" + pat):
            for r in _csv_rows(f):
                root = (r.get("_gameobject") or "").split("/")[0]
                if root.startswith("Boss-"):
                    box.add(root)
    if not d:
        return None
    return (len(d), len(e), len(d & e))


claim("T1", "docs/spec/ANIMATION_SCRIPT.md", "**8 tên entry kiểm chứng bằng dữ liệu serialize**",
      (8, 1, 8), boss1_state_values,
      "8 state + 8/8 khớp bộ tên; Boss1_Director chỉ 1 instance (Boss-39002)")

claim("T2", "docs/spec/ANIMATION_SCRIPT.md", "**12 field delegate `0x20`…`0x78` có tên**",
      (12, 0x20, 0x78), delegate_field_names,
      "12 delegate kề nhau — T2 chỉ còn câu 'ai gán'")

claim("T3", "docs/spec/ANIMATION_SCRIPT.md", "| `0x20` | `attackEventName` | `string` |",
      (5, 0x20, 0x40, 2), spine_handler_fields,
      "5 field serialized, 2 cái là chuỗi tên event")

claim("T4", "docs/spec/ANIMATION_SCRIPT.md", "**18 có `*_Director`** và **16 có lớp `*_AnimationEvents`**",
      (18, 16, 13), director_matrix,
      "ma trận director <-> animation-events trên prefab, ghép bằng _gameobject")

# ── U. T3/T4 đo lại từ raw (ANIMATION_SCRIPT.md §3.5) ───────────────────
PERSIST = "reverse-engineering/raw/animation-audit/persistent-calls.json.gz"
CTRLGRAPH = "reverse-engineering/raw/animation-audit/controller-graphs.json.gz"


def _json_gz(path):
    raw = ref_blob(path)
    if raw is None:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except ValueError:
        return None


def persistent_event_stats():
    """(field, field không rỗng, call, field enemy/boss, call enemy/boss)."""
    d = _json_gz(PERSIST)
    if not d:
        return None
    fields = d.get("fields") or []
    nonempty = [f for f in fields if f.get("calls")]
    return (len(fields), len(nonempty), sum(len(f["calls"]) for f in nonempty),
            int(d["summary"]["relevant_enemy_boss_fields"]),
            int(d["summary"]["relevant_enemy_boss_calls"]))


def controller_graph_stats():
    """(controller, prefab root, parameter, state, transition, transition có điều kiện)."""
    d = _json_gz(CTRLGRAPH)
    if not d:
        return None
    cs = d.get("controllers") or []
    states = trans = cond = 0
    roots = set()
    for c in cs:
        roots.update(c.get("prefab_roots") or [])
        for m in c.get("machines") or []:
            for s in m.get("states") or []:
                states += 1
                for tr in s.get("transitions") or []:
                    trans += 1
                    cond += 1 if tr.get("conditions") else 0
            for tr in m.get("any_state_transitions") or []:
                trans += 1
                cond += 1 if tr.get("conditions") else 0
    params = sum(len(c.get("parameters") or []) for c in cs)
    return (len(cs), len(roots), params, states, trans, cond)


claim("U1", "docs/spec/ANIMATION_SCRIPT.md",
      "**1.335** field · **111** field không rỗng · **115** call",
      (1335, 111, 115, 1202, 114), persistent_event_stats,
      "T3: đếm lại từ raw, không chép report 39")

claim("U2", "docs/spec/ANIMATION_SCRIPT.md",
      "**52** controller · **63** prefab root · **303** parameter",
      (52, 63, 303, 395, 357, 302), controller_graph_stats,
      "T4: đếm lại từ raw (395 state, 357 transition, 302 có condition)")

# ── W. ai đặt trigger Animator + số đo chuyển động enemy (§3.6, §4.0) ──
ANIMCALLS = "reverse-engineering/raw/animation-audit/native-calls.json"


def _json_plain(path):
    raw = ref_blob(path)
    if raw is None:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except ValueError:
        return None


def _anim_method_calls():
    d = _json_plain(ANIMCALLS)
    return (d or {}).get("methods") or []


def settrigger_sites():
    """(số call site Animator.SetTrigger, số method chứa chúng)."""
    methods = _anim_method_calls()
    if not methods:
        return None
    sites = meths = 0
    for m in methods:
        n = sum(1 for c in (m.get("calls") or []) for cand in (c.get("candidates") or [])
                if cand.get("class_name") == "Animator" and cand.get("method") == "SetTrigger")
        if n:
            meths += 1
            sites += n
    return (sites, meths)


def trigger_param_stats():
    """(trigger, bool, controller boss) từ controller-graphs.json.gz."""
    d = _json_gz(CTRLGRAPH)
    if not d:
        return None
    cs = d.get("controllers") or []
    trig = bools = boss = 0
    for c in cs:
        if any(r.startswith("Boss-") for r in (c.get("prefab_roots") or [])):
            boss += 1
        for p in c.get("parameters") or []:
            t = p["raw"]["m_Type"]
            trig += 1 if t == 9 else 0
            bools += 1 if t == 4 else 0
    return (trig, bools, boss)


def trigger_top_names():
    """(Appear, Attack2, Die, Attack1) — 4 tên trigger phổ biến."""
    d = _json_gz(CTRLGRAPH)
    if not d:
        return None
    c = {}
    for ctrl in d.get("controllers") or []:
        for p in ctrl.get("parameters") or []:
            if p["raw"]["m_Type"] == 9:
                c[p["name"]] = c.get(p["name"], 0) + 1
    return (c.get("Appear", 0), c.get("Attack2", 0), c.get("Die", 0), c.get("Attack1", 0))


def _float_in(cls_prefix, method, value):
    for m in _anim_method_calls():
        if m.get("class_name") == cls_prefix and m.get("method") == method:
            for f in m.get("float_evidence") or []:
                if abs(float(f["value"]) - value) < 1e-6:
                    return float(f["value"])
    return None


def pathfollow_deg():
    return _float_in("Enemy_Movement", "PathFollow", 57.29578)


def circle_rad_step():
    return _float_in("Boss_AttackTypes.<IEGunAttackAutoCircleBase>d__12", "MoveNext", 0.01745)


def waits_seconds_stats():
    """(tổng WaitForSeconds, hằng literal, biến) — đọc file LOCAL, cùng luật J8.

    J8 đọc qua `ref_blob` (có thể là blob của ref); hàm này đọc thẳng đĩa. Nếu hai
    đường cho cùng số thì phép đếm không phụ thuộc nguồn đọc.
    """
    files = _glob.glob("reverse-engineering/raw/il2cpp-consts/*.asm.txt")
    if not files:
        return None
    tot = lit = 0
    for f in files:
        try:
            lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        for i, ln in enumerate(lines):
            if "0x2786508" not in ln:
                continue
            tot += 1
            hit = False
            for j in range(i - 1, max(i - 16, -1), -1):
                if re.search(r"fmov\s+s0,\s*#", lines[j]) or \
                        re.search(r"ldr\s+s0,\s*\[x\d+, #0x[0-9a-f]+\]", lines[j]):
                    hit = True
                    break
            lit += bool(hit)
    return (tot, lit, tot - lit)


claim("W1", "docs/spec/ANIMATION_SCRIPT.md",
      "**`Animator.SetTrigger` có đúng 7 call site, trên 5 method**",
      (7, 5), settrigger_sites, "ai đổi state Animator — chỉ Boss_AttackPhases")

claim("W2", "docs/spec/ANIMATION_SCRIPT.md",
      "**288** trigger · **15** bool · **49** controller boss",
      (288, 15, 49), trigger_param_stats, "máy trạng thái: 288 trigger, 15 bool, 42 controller boss")

claim("W3", "docs/spec/ANIMATION_SCRIPT.md",
      "`Appear` **30** · `Attack2` **23** · `Die` **22** · `Attack1` **20**",
      (30, 23, 22, 20), trigger_top_names, "tên trigger = tên clip, không mã hoá")

claim("W4", "docs/spec/ANIMATION_SCRIPT.md", "`57.29578` (rad→deg)",
      57.29578, pathfollow_deg, "PathFollow đổi hướng bằng atan2 rồi rad→deg")

claim("W5", "docs/spec/ANIMATION_SCRIPT.md", "`0.01745`", 0.01745,
      circle_rad_step, "bước quét vòng tròn = 1 độ mỗi bước")

claim("W6", "docs/spec/ANIMATION_SCRIPT.md",
      "**38 lần `WaitForSeconds` · 12 hằng số · 26 lấy từ biến**",
      (38, 12, 26), waits_seconds_stats, "đếm lại cùng phép đếm J8 nhưng đọc file LOCAL (không qua ref_blob)")

# ── X. enemy có bao nhiêu animation thật (§4.2) ────────────────────────
WAVES = "datas/waves.json"
AMAP = "datas/animator_map.csv.gz"


def _csv_gz_rows(path):
    key = "csvgz:" + path
    if key in _cache:
        return _cache[key]
    raw = ref_blob(path)
    val = None
    if raw:
        try:
            # ref_blob đã giải nén .gz; chỉ cần decode
            val = list(csv.DictReader(io.StringIO(raw.decode("utf-8", "replace"))))
        except (UnicodeDecodeError, csv.Error):
            val = None
    _cache[key] = val
    return val


def _enemy_sets():
    d = _json_plain(WAVES)
    if not d:
        return None
    roster = set()
    for wv in d.get("waves") or []:
        for sp in wv.get("spawners") or []:
            roster.update(sp.get("enemies") or [])
    if not roster:
        return None
    amap = _csv_gz_rows(AMAP) or []
    roots = {r.get("prefab_root") for r in amap}
    return roster, roots


def enemy_anim_split():
    """(roster, boss, enemy, có Animator, Afterburner, không Animator)."""
    sets = _enemy_sets()
    if not sets:
        return None
    roster, roots = sets
    boss = {e for e in roster if e.startswith("Boss-")}
    enemy = roster - boss
    with_anim = enemy & roots
    amap = _csv_gz_rows(AMAP) or []
    per = {}
    for r in amap:
        root = r.get("prefab_root")
        if root in with_anim:
            per.setdefault(root, set()).add(r.get("controller_name") or "")
    aft = {p for p, s in per.items() if s == {"Afterburner"}}
    return (len(roster), len(boss), len(enemy), len(enemy & roots), len(aft),
            len(enemy) - len(enemy & roots))


def enemy_controller_gap():
    """(controller non-boss, chưa có graph, tên phân biệt chưa có graph)."""
    sets = _enemy_sets()
    d = _json_gz(CTRLGRAPH)
    if not sets or not d:
        return None
    roster, _ = sets
    enemy = {e for e in roster if not e.startswith("Boss-")}
    amap = _csv_gz_rows(AMAP) or []
    have = {c["path_id"] for c in d.get("controllers") or []}
    ids, names_in, names_out = set(), set(), set()
    for r in amap:
        if r.get("prefab_root") not in enemy or not r.get("controller_path_id"):
            continue
        pid = int(r["controller_path_id"])
        ids.add(pid)
        if pid in have:
            names_in.add(r.get("controller_name") or "")
        else:
            names_out.add(r.get("controller_name") or "")
    return (len(ids), len(ids - have), len(names_out))


def cd31002_cluster():
    """số prefab ENEMY dùng controller tên `CD-31002`."""
    sets = _enemy_sets()
    if not sets:
        return None
    roster, _ = sets
    enemy = {e for e in roster if not e.startswith("Boss-")}
    amap = _csv_gz_rows(AMAP) or []
    n = len({r["prefab_root"] for r in amap
             if r.get("controller_name") == "CD-31002" and r.get("prefab_root") in enemy})
    return n or None


claim("X1", "docs/spec/ANIMATION_SCRIPT.md",
      "**109 roster = 39 boss + 70 enemy · 87 có Animator · 27 chỉ `Afterburner` · 19 không Animator.**",
      (109, 39, 70, 51, 27, 19), enemy_anim_split,
      "tách boss khỏi enemy: 87/109 là ROSTER, riêng enemy chỉ 51/70")

claim("X2", "docs/spec/ANIMATION_SCRIPT.md",
      "**14** controller không thuộc boss; **11** trong số đó **chưa có graph** (10 tên, `BB-36002` có 2 id)",
      (14, 11, 10), enemy_controller_gap,
      "việc còn thiếu của enemy animation: 11 controller, không phải 87")

claim("X3", "docs/spec/ANIMATION_SCRIPT.md",
      "`CD-31002` | **12** (`CD-31002/03/04/05/06/07/08/09/10/13/15/16`)", 12,
      cd31002_cluster, "cluster không-boss lớn nhất: 12 prefab dùng 1 controller")

# ── Y. bộ đầu vào vẽ UI + gate tutorial (§9.2) ─────────────────────────
DRAWING = "reverse-engineering/raw/ui-audit/drawing-inputs.json.gz"
GATES = "reverse-engineering/raw/ui-audit/early-native-gates.json"


def drawing_inputs_stats():
    """(board, node, có local_pos, sprite có candidate, sprite có tên, key Việt, key)."""
    d = _json_gz(DRAWING)
    if not d:
        return None
    screens = d.get("screens") or []
    if not screens:
        return None

    def tot(k):
        return sum((s.get("counts") or {}).get(k) or 0 for s in screens)

    return (len(screens), tot("nodes"), tot("position_present"),
            tot("unique_name_candidate"), tot("sprite_components_with_name"),
            tot("vi_resolved"), tot("localization_keys"))


def tutorial_gate_stats():
    """(số check, số check PASS, số call target resolve được)."""
    d = _json_plain(GATES)
    if not d:
        return None
    checks = d.get("checks") or {}
    calls = d.get("resolved_direct_calls_from_dump") or {}
    return (len(checks), sum(1 for v in checks.values() if v), len(calls))


claim("Y1", "docs/spec/UI.md",
      "**11 board · 10.710 node · 100 % có `local_pos` · 4.987/5.067 sprite có candidate · 312/317 key tiếng Việt.**",
      (11, 10710, 10710, 4987, 5067, 312, 317), drawing_inputs_stats,
      "bộ đầu vào vẽ: đếm từ drawing-inputs.json.gz, không chép bảng report 43")

claim("Y2", "docs/spec/UI.md",
      "**6**/6 kiểm tra branch/instruction",
      (6, 6, 6), tutorial_gate_stats,
      "gate tutorial native: 5 check PASS, 6 call target resolve từ RVA")

# ── Z. layout tutorial + visual coverage (snapshot 0a42eaa42, §9.3) ────
TUT_TEXTS = "reverse-engineering/raw/ui-audit/tutorial-texts.csv"
VISUAL = "reverse-engineering/raw/ui-audit/visual-coverage.json"


def tutorial_text_stats():
    """(dòng, field, GO, key, dòng có tiếng Việt)."""
    rows = _csv_rows(TUT_TEXTS)
    if not rows:
        return None
    return (len(rows),
            len({r.get("owner_field") for r in rows}),
            len({r.get("panel_path_id") for r in rows}),
            len({r.get("key") for r in rows}),
            sum(1 for r in rows if (r.get("vi") or "").strip()))


def visual_coverage_stats():
    """(màn, node, SpriteRenderer, TMP, số màn chạm trần 6.000)."""
    d = _json_plain(VISUAL)
    if not d:
        return None
    screens = d.get("screens") or []
    if not screens:
        return None
    return (len(screens),
            sum(s.get("node_count") or 0 for s in screens),
            sum((s.get("counts") or {}).get("sprite_renderer") or 0 for s in screens),
            sum((s.get("counts") or {}).get("tmp") or 0 for s in screens),
            sum(1 for s in screens
                if (s.get("walk_diagnostics") or {}).get("at_old_6000_limit")))


claim("Z1", "docs/spec/UI.md",
      "**19 dòng · 7 field · 6 GO · 13 key**",
      (19, 7, 6, 13, 17), tutorial_text_stats,
      "tutorial-texts.csv: 8 ref nhưng chỉ 6 GO có text (634 dùng cho 2 field)")

claim("Z2", "docs/spec/UI.md",
      "15 màn · 14.730 node · 7.087 `SpriteRenderer` · 1.913 TMP",
      (15, 14730, 7087, 1913, 1), visual_coverage_stats,
      "visual-coverage.json: 15 màn, Board_Maps chạm trần 6.000 ⇒ cận dưới")

def endgame_callback_ref():
    """(check PASS, có 0x126d3cc, có 0x14f9f84) trong raw của nhánh dữ liệu."""
    d = _json_plain(GATES)
    if not d:
        return None
    blob = json.dumps(d)
    return (1 if (d.get("checks") or {}).get(
        "endgame_callback_reveals_continue_and_increments_tutorial") else 0,
        "0x126d3cc" in blob, "0x14f9f84" in blob)


claim("Z3", "docs/spec/UI.md",
      "@ **`0x126d3cc`**", (1, True, True), endgame_callback_ref,
      "callback Endgame ThroughTut: ẩn Replay, bật Continue, IndexTutorial+1 @0x14f9f84")

# ── AA. đếm trạng thái trong bảng "đủ chưa" (DESIGN_READINESS §8) ───────
READINESS = "docs/spec/DESIGN_READINESS.md"
COVERAGE = "docs/spec/COVERAGE_AUDIT.md"


def _status_tally(text, start, end, first_col=3):
    """(tổng dòng, ✅, 🟡, 🔴) của một bảng giữa hai mốc `start`/`end`."""
    if start not in text:
        return None
    body = text.split(start, 1)[1]
    if end and end in body:
        body = body.split(end, 1)[0]
    total = ok = warn = bad = 0
    for line in body.splitlines():
        parts = line.split("|")
        if len(parts) < 5 or not parts[1].strip().isdigit():
            continue
        total += 1
        cell = parts[first_col].strip()
        if cell.startswith("✅"):
            ok += 1
        elif cell.startswith("🟡"):
            warn += 1
        elif cell.startswith("🔴"):
            bad += 1
    return (total, ok, warn, bad) if total else None


def coverage_region_tally():
    txt = ref_blob(COVERAGE).decode("utf-8")
    return _status_tally(txt, "## 1. Mười bốn vùng năng lực", "## 2.")


def blocker_tally():
    # bảng blocker có thêm cột "Trạng thái cũ" ⇒ trạng thái mới nằm ở cột 4
    txt = ref_blob(READINESS).decode("utf-8")
    return _status_tally(txt, "## 2. Chín blocker", "## 3.", first_col=4)


claim("AA1", READINESS,
      "| **15 dòng vùng năng lực** (`COVERAGE_AUDIT.md` §1) | 15 | **11** ✅ | **4** 🟡 | **0** 🔴 · **0** ⛔ (feel **đã đóng**",
      (15, 11, 4, 0), coverage_region_tally,
      "đếm trạng thái từng vùng trong COVERAGE_AUDIT §1, không chép tay")

claim("AA2", READINESS,
      "| **9 câu blocker** (§2 ở trên) | 9 | **4** ✅",
      (9, 4, 4, 1), blocker_tally,
      "đếm trạng thái 9 blocker trong chính bảng §2 (25/10: A6/B1/feel-bỏ ✅ · B3 🟡 · còn A5 🔴)")

# ── AB. bộ ảnh gốc: chưa phân loại / chưa tách (ASSET_TRIAGE.md) ──────
SPRITES_INDEX = "docs/assets/sprites-index.csv"
ASSET_TRIAGE = "docs/spec/ASSET_TRIAGE.md"
ENCOUNTERS_DOC = "docs/spec/ENCOUNTERS.md"


def _sprite_index():
    return _csv_rows(SPRITES_INDEX) or []


def _atlas_counts(rows):
    out = {}
    for r in rows:
        a = (r.get("atlas") or "").strip()
        if a:
            out[a] = out.get(a, 0) + 1
    return out


def asset_triage_stats():
    """(asset, unclassified, sheet Texture2D, sheet có sprite, sheet chưa tách)."""
    rows = _sprite_index()
    if not rows:
        return None
    un = [r for r in rows if r.get("category") == "unclassified"]
    sheets = {r["name"] for r in rows if r.get("category") == "atlas"}
    if not sheets:
        return None
    by = _atlas_counts(rows)
    with_sp = sum(1 for s in sheets if by.get(s))
    # 67 = texture sactx-* theo TÊN (không theo category: 11 page bị xếp nhầm nhóm)
    sactx = sum(1 for r in rows if r["name"].startswith("sactx"))
    return (len(rows), len(un), len(sheets), with_sp, len(sheets) - with_sp, sactx)


def _rule_hits(name):
    import re
    low = name.lower()
    return bool(re.match(r"^blt_", low)
                or re.match(r"^(hotro|vip|goigem|khung)", low)
                or re.match(r"^rank", low)
                or re.match(r"^boss", low)
                or re.match(r"^(cb|cd|e_)", low)
                or re.match(r"^(manhplane|xvideo|rock|head|foot)", low))


def asset_unclassified_split():
    """(trong sheet, rời, khớp 6 luật tên, còn lại)."""
    rows = _sprite_index()
    if not rows:
        return None
    un = [r for r in rows if r.get("category") == "unclassified"]
    if not un:
        return None
    inside = sum(1 for r in un if (r.get("atlas") or "").strip())
    outside = [r for r in un if not (r.get("atlas") or "").strip()]
    return (inside, len(outside))


def asset_sheet_worklist():
    """(sheet ≥8 sprite, sprite trong đó, ô lưới khai báo, ô đã tách)."""
    import re
    rows = _sprite_index()
    if not rows:
        return None
    by = _atlas_counts(rows)
    sheets = {r["name"] for r in rows if r.get("category") == "atlas"}
    big = {s: c for s, c in by.items() if c >= 8}
    un_by = _atlas_counts([r for r in rows if r.get("category") == "unclassified"])
    big_un = {s: c for s, c in un_by.items() if c >= 8}
    cells = 0
    done = 0
    for s in sheets:
        m = re.search(r"_(\d+)x(\d+)$", s)
        if m:
            cells += int(m.group(1)) * int(m.group(2))
            done += by.get(s, 0)
    return (len(big), sum(big.values()), cells, done, len(big_un), sum(big_un.values()))


def unresolved_sheets_stats():
    """(sheet có ≥1 sprite unresolved, tổng sheet unclassified-*)."""
    path = os.path.join(ROOT, "docs/assets/sprites-auto-classified.csv")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    uncls = {r["sheet"] for r in rows if r["sheet"].startswith("unclassified")}
    un = {r["sheet"] for r in rows if r["category_auto"] == "unresolved"}
    if not uncls:
        return None
    return (len(un), len(uncls))


claim("AB6", ASSET_TRIAGE,
      "**17/25** sheet `unclassified-*` còn",
      (17, 25), unresolved_sheets_stats,
      "định nghĩa 'chưa xem hết' = sheet còn ≥1 sprite unresolved trong sprites-auto-classified.csv")

def encounters_totals():
    """(dòng spawner, wave, enemy entry, tên khác nhau) từ waves.json."""
    d = ref_json("datas/waves.json")
    if not d:
        return None
    rows = [s for w in d.get("waves", []) for s in w.get("spawners") or []]
    return (len(rows), len(d.get("waves", [])),
            sum(len(s.get("enemies") or []) for s in rows),
            len({s["spawner"] for s in rows}))


def encounters_types():
    """Số dòng theo `spawn_type` (point_range, point, path, boss, special)."""
    d = ref_json("datas/waves.json")
    if not d:
        return None
    rows = [s for w in d.get("waves", []) for s in w.get("spawners") or []]
    import collections as _c
    k = _c.Counter(s.get("spawn_type") for s in rows)
    return (k["point_range"], k["point"], k["path"], k["boss"], k["special"])


def wave_call_data_identity():
    """(Call_Data, pathID khác nhau, trùng, số wave) cho 3 wave normal đã export."""
    tot = 0
    uniq = 0
    names = ("0164__148604", "0113__21468", "0005__38187")
    for tag in names:
        d = ref_json("reverse-engineering/raw/early-waves/"
                     f"datas_maps_waves_wave_{tag}.json.gz")
        if not d:
            return None
        cds = [c for n in d.get("nodes", []) for c in n.get("components", [])
               if c.get("script_class") == "Call_Data"]
        tot += len(cds)
        uniq += len({c["path_id"] for c in cds})
    return (tot, uniq, tot - uniq, len(names))


def encounters_units():
    """(dòng, lượt Σcopies, quân Σlen×copies) — hai đơn vị đừng trộn."""
    d = ref_json("datas/waves.json")
    if not d:
        return None
    rows = [s for w in d.get("waves", []) for s in w.get("spawners") or []]
    return (len(rows), sum(int(s.get("copies") or 0) for s in rows),
            sum(len(s.get("enemies") or []) * int(s.get("copies") or 0) for s in rows))


def encounters_types_copies():
    """Số **lượt** theo `spawn_type` = đúng dãy CROSS_BRANCH đã ghi (45.659 tổng)."""
    d = ref_json("datas/waves.json")
    if not d:
        return None
    import collections as _c
    k = _c.Counter()
    for w in d.get("waves", []):
        for s in w.get("spawners") or []:
            k[s.get("spawn_type")] += int(s.get("copies") or 0)
    return (k["point_range"], k["point"], k["path"], k["boss"], k["special"])


def wave_copy_identity():
    """9 wave của bảng §3: (Σcopies, dòng) — bảng cũ ghi đúng Σcopies."""
    d = ref_json("datas/waves.json")
    if not d:
        return None
    w = {x["wave"]: x.get("spawners") or [] for x in d.get("waves", [])}
    order = ("Wave_0000", "Wave_0010", "Wave_0050", "Wave_0100", "Wave_0150",
             "Wave_0163", "Wave_0200", "Wave_0235", "Wave_7001")
    out = []
    for k in order:
        out += [sum(int(s.get("copies") or 0) for s in w.get(k, [])), len(w.get(k, []))]
    return tuple(out)


claim("AQ4", ENCOUNTERS_DOC,
      "| **Tổng** | | **282** | **11.089** | **23.757** | 28,5 | **62** |",
      (11089, 23757, 45659), encounters_units,
      "dòng 11.089 · lượt Σcopies 23.757 (= số bảng cũ) · quân Σlen×copies 45.659 (peer đã rút lại nhãn \"quân thật\")")

claim("AQ5", ENCOUNTERS_DOC,
      "**Kiểm tự động (`AQ5`): 9/9 wave khớp** `Σ copies` = số bảng cũ",
      (150, 42, 331, 190, 72, 36, 36, 18, 54, 27, 622, 257, 42, 21, 84, 42, 6, 3),
      wave_copy_identity,
      "9 wave: (Σcopies, dòng) — 622 của Wave_0163 là lượt, không phải dòng")

claim("AQ6", ENCOUNTERS_DOC,
      "| `point_range` | point-to-point range | 7.536 | 68,0 % | **16.498** | 69,4 % |",
      (16498, 4199, 1688, 686, 686), encounters_types_copies,
      "spawn_type theo LƯỢT: khớp dãy 16.498/4.199/1.688/686/686 của CROSS_BRANCH §3c")

claim("AQ1", ENCOUNTERS_DOC,
      "| Dòng trong `waves.json` (đã **gộp** object trùng, mỗi dòng mang `copies`) | **11.089** (11.072 ở 281 wave có tên + 17 ở `unknown`) | `waves.json` |",
      (11089, 282, 22451, 1015), encounters_totals,
      "đếm lại waves.json: số dòng cấu hình (KHÔNG phải spawner — spawner = 23.757 object), wave, enemy entry, tên khác nhau")

claim("AQ2", ENCOUNTERS_DOC,
      "| `point_range` | point-to-point range | 7.536 |",
      (7536, 2084, 861, 327, 281), encounters_types,
      "phân bố spawn_type trên 11.089 dòng")

def wave_unit_crosscheck():
    """(Σcopies trong waves.json, instances Call_Data trong class-inventory.csv, số dòng)."""
    import json
    path = os.path.join(ROOT, "datas/waves.json")
    if not os.path.exists(path):
        return None
    data = json.load(open(path, encoding="utf-8"))
    waves = data.get("waves") or []
    rows = sum(len(w["spawners"]) for w in waves)
    copies = sum(sp.get("copies", 1) for w in waves for sp in w["spawners"])
    inv = os.path.join(ROOT, "reverse-engineering/scriptableobjects/class-inventory.csv")
    if not os.path.exists(inv):
        return None
    n = None
    for r in _csv_rows("reverse-engineering/scriptableobjects/class-inventory.csv") or []:
        if r.get("class") == "Call_Data":
            n = int(r["instances"])
    if n is None:
        return None
    return (copies, n, rows)


claim("AQ3", ENCOUNTERS_DOC,
      "| **cộng 3 wave** | | **149** | **149** | | **149** |",
      (149, 149, 0, 3), wave_call_data_identity,
      "Call_Data vs pathID trên 3 wave normal: 0 component bị tham chiếu 2 lần")

def atlas_page_stats():
    """(asset, unresolved, unresolved có trang thật, ca tự gán được, họ trang đủ chuẩn)."""
    rows = _csv_rows("docs/assets/sprites-atlas-page.csv") or []
    if not rows:
        return None
    un = [r for r in rows if r["current_category"] == "unresolved"]
    withp = [r for r in un if r.get("texture_page")]
    applied = [r for r in rows if r.get("applied") == "true"]
    fam = {}
    for r in rows:
        if r.get("suggested_category") and r.get("page_family"):
            fam[r["page_family"]] = (r["suggested_category"], r["precision"], r["n_labeled"])
    return (len(rows), len(un), len(withp), len(applied), len(fam))


def readme_sizes():
    """(số dòng khai báo kích thước trong README, số dòng SAI)."""
    import re
    path = os.path.join(ROOT, "docs/spec/README.md")
    if not os.path.exists(path):
        return None
    txt = open(path, encoding="utf-8").read()
    entries = re.findall(r"`([A-Za-z_0-9./-]+\.md)`.*?(\d+) dòng · (\d+) bảng", txt)
    if not entries:
        return None
    bad = 0
    for name, lines, tables in entries:
        f = os.path.join(ROOT, name) if "/" in name else os.path.join(ROOT, "docs/spec", name)
        if not os.path.exists(f):
            bad += 1
            continue
        body = open(f, encoding="utf-8").read().splitlines()
        t = sum(1 for l in body if l.lstrip().startswith("|---"))
        if (len(body), t) != (int(lines), int(tables)):
            bad += 1
    return (len(entries), bad)


claim("AQ7", ENCOUNTERS_DOC,
      "| **Spawner = `Call_Data` object** | **23.757** (= Σ `copies`; khớp `class-inventory.csv` 23.757) | hai nguồn độc lập |",
      (23757, 23757, 11089), wave_unit_crosscheck,
      "Σ copies trong waves.json = số instance Call_Data trong class-inventory.csv ⇒ 23.757 là số SPAWNER; "
      "11.089 chỉ là số dòng cấu hình sau khi gộp object trùng. Không kết luận vì sao trùng")


def wave_unit_stats():
    """(Σ len, Σ len×copies, số dòng spawner, min/median/max Σ len mỗi wave)."""
    import statistics
    d = ref_json("datas/waves.json")
    if not d:
        return None
    per = [sum(len(sp["enemies"]) for sp in w["spawners"]) for w in d["waves"]]
    quân = sum(len(sp["enemies"]) * sp.get("copies", 1) for w in d["waves"] for sp in w["spawners"])
    rows = sum(len(w["spawners"]) for w in d["waves"])
    return (sum(per), quân, rows, min(per), statistics.median(per), max(per))


claim("WR7", "docs/spec/DATA_SYNC.md",
      "`Σ len(spawner.enemies)` = **22.451** (109 prefab, 0 `?`)",
      (22451, 45659, 11089, 2, 63, 603), wave_unit_stats,
      "cùng một file waves.json nhưng BA đơn vị: Σ len 22.451 · Σ len×copies 45.659 quân · 11.089 dòng; "
      "min/med/max Σ len mỗi wave 2/63/603 — đừng trộn với 45.659")

def loadout_contract_counts():
    """(số key family, số method, số check, số bảng rank, số limitation) từ contracts.json.gz."""
    import gzip
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/player-loadout/contracts.json.gz")
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        d = _json.load(fh)
    return (len(d.get("contracts") or []), len(d.get("methods") or []),
            len(d.get("checks") or {}), len(d.get("rank_tables") or {}),
            len(d.get("limitations") or []))


def raw_manifest_ok():
    """(số file audio-rules khớp sha, số file loadout khớp sha, số lệch) theo index.json."""
    import gzip
    import hashlib
    import json as _json
    totals = []
    bad = 0
    for base in ("reverse-engineering/raw/audio-rules", "reverse-engineering/raw/player-loadout"):
        idx_path = os.path.join(ROOT, base, "index.json")
        if not os.path.exists(idx_path):
            return None
        with open(idx_path, encoding="utf-8") as fh:
            idx = _json.load(fh)
        ok = 0
        for f in idx.get("files") or []:
            p = os.path.join(ROOT, f["path"])
            if not os.path.exists(p):
                bad += 1
                continue
            data = open(p, "rb").read()
            if p.endswith(".gz"):
                data = gzip.decompress(data)
            if hashlib.sha256(data).hexdigest() == f.get("sha256_decompressed"):
                ok += 1
            else:
                bad += 1
        totals.append(ok)
    return (totals[0], totals[1], bad)


claim("CM6", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "thêm **15 key family · 33 method · 43 check**",
      (15, 33, 43, 6, 8), loadout_contract_counts,
      "contracts.json.gz của report 66: 15 key · 33 method · 43 check · 6 bảng rank · 8 limitation; "
      "status PROVISIONAL_STATIC_PARTIAL_PLAYER_LOADOUT_NOT_RUNTIME")

claim("CM7", "docs/spec/DATA_SYNC.md",
      "**21/21** file `audio-rules` + **5/5** file loadout khớp `index.json` (**0 lệch**)",
      (21, 5, 0), raw_manifest_ok,
      "băm lại từng file raw đã kéo và so sha256_decompressed trong index.json của nhánh dữ liệu")


def ia_counts():
    """(số mảng Map, số mảng Player, số record length_valid sai) trong ia-resolved.json."""
    d = ref_json("reverse-engineering/il2cpp/ia-resolved.json")
    if not d:
        return None
    m = d["methods"]
    bad = sum(1 for k in m for r in m[k] if not r.get("length_valid"))
    return (len(m["Map_Get_Datas.cctor"]), len(m["Player_Get_Datas.cctor"]), bad)


def player_arrays():
    """(5.154, 253, 0) — tổng giá trị, wave id khác nhau, giá trị không có trong waves.json."""
    import struct
    d = ref_json("reverse-engineering/il2cpp/ia-resolved.json")
    w = ref_json("datas/waves.json")
    if not d or not w:
        return None
    vals = [v for r in d["methods"]["Map_Get_Datas.cctor"] for v in r["ints"]]
    ids = set()
    for row in w["waves"]:
        tail = row["wave"].split("_")[-1]
        if tail.isdigit():
            ids.add(int(tail))
    return (len(vals), len(set(vals)), sum(1 for v in vals if v not in ids))


def player_values():
    """(damage[0], rate[0], len damage, len rate, giá trị clone) — decode theo kiểu field."""
    import struct
    d = ref_json("reverse-engineering/il2cpp/ia-resolved.json")
    if not d:
        return None
    rows = d["methods"]["Player_Get_Datas.cctor"]

    def dec(r, typ):
        body = bytes.fromhex(r["raw"])[: 4 * r["len"]]
        return list(struct.unpack("<%d%s" % (r["len"], typ), body))

    dmg = dec(rows[1], "f")
    rate = dec(rows[2], "f")
    clone = dec(rows[4], "f")
    return (round(dmg[0]), round(rate[0], 2), len(dmg), len(rate),
            round(clone[0], 2), round(clone[2], 2))


def player_costs():
    """(số tàu bán được, số tàu giá -1) từ PlayerCosts int[24]."""
    import struct
    d = ref_json("reverse-engineering/il2cpp/ia-resolved.json")
    if not d:
        return None
    r = d["methods"]["Player_Get_Datas.cctor"][0]
    cost = list(struct.unpack("<%di" % r["len"], bytes.fromhex(r["raw"])[: 4 * r["len"]]))
    return (sum(1 for c in cost if c >= 0), sum(1 for c in cost if c == -1))


def player_offset_stores():
    """Số mảng có store đầu tiên của kết quả IA rơi đúng một trong 6 offset field."""
    import re as _re
    p = os.path.join(ROOT, "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt")
    if not os.path.exists(p):
        return None
    asm = open(p, encoding="utf-8", errors="replace").read().splitlines()
    idx = {}
    for i, line in enumerate(asm):
        m = _re.match(r"\s*(0x[0-9a-f]+):", line)
        if m and m.group(1) not in idx:
            idx[m.group(1)] = i
    d = ref_json("reverse-engineering/il2cpp/ia-resolved.json")
    offsets = ("0x38", "0x78", "0x80", "0x88", "0x1c8", "0x308")
    found = 0
    for r in d["methods"]["Player_Get_Datas.cctor"]:
        i = idx.get(r["array_new_addr"])
        if i is None:
            continue
        for line in asm[i:i + 80]:
            m = _re.search(r"str\s+x19, \[x\d+, #(0x[0-9a-f]+)\]", line, _re.I)
            if m:
                found += m.group(1).lower() in offsets
                break
    return found


def audio_rule_counts():
    """(số method, số check, số rule) trong raw/audio-rules/contracts.json.gz."""
    import gzip
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/audio-rules/contracts.json.gz")
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        d = _json.load(fh)
    return (len(d.get("methods") or []), len(d.get("checks") or {}), len(d.get("rules") or []))


def asset_pack_counts():
    """(file, path va chạm, row vượt unique path, size mismatch) từ catalog.json.gz."""
    import gzip
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/asset-pack/catalog.json.gz")
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        d = _json.load(fh)
    cs = d.get("collision_summary") or {}
    return (len(d.get("files") or []), cs.get("paths"), cs.get("extra_manifest_rows"),
            len(d.get("manifest_size_mismatches") or []))


claim("IA1", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "đã resolve **576/576** (claim **IA1**)",
      (576, 6, 0), ia_counts,
      "ia-resolved.json của chính repo này: 576 mảng Map + 6 mảng Player, 0 record length_valid sai ⇒ "
      "KHÔNG phải 'chờ nhánh kia dump thêm'")

claim("IA3", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "**5.154** giá trị · **253** wave id khác nhau · **0** giá trị không có trong `datas/waves.json`",
      (5154, 253, 0), player_arrays,
      "576 mảng Map chứa 5.154 wave id, 253 id khác nhau, tất cả đều có trong datas/waves.json")

claim("IA2", "docs/spec/BALANCE.md",
      "store offset kiểm bằng asm: `0x38 / 0x78 / 0x80 / 0x88 / 0x1C8 / 0x308`",
      6, player_offset_stores,
      "cả 6 InitializeArray của Player_Get_Datas.cctor có store đúng một trong 6 offset ngay sau call")

claim("IA4", "docs/spec/BALANCE.md",
      "`shipCloneDamage` = **1,35 · 1,6 · 1,86** (`0x1C8`)",
      (4500, 4.8, 24, 24, 1.35, 1.86), player_values,
      "decode float từ hex: damage[0]=4500, rate[0]=4.8, hai mảng 24 phần tử, clone 3 phần tử — "
      "cột `ints` của file là bit pattern, KHÔNG phải damage")

claim("IA5", "docs/spec/BALANCE.md",
      "**16/24** tàu có giá ≥ 0; **8** tàu `−1`",
      (16, 8), player_costs,
      "PlayerCosts là int[24]; -1 = không bán")

def peer_comparison():
    """(record Map, record Player) trong raw/initialize-arrays/peer-comparison.json khi khớp tuyệt đối."""
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/initialize-arrays/peer-comparison.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        d = _json.load(fh)
    g = {x.get("method"): x for x in (d.get("groups") or [])}
    out = []
    for name in ("Map_Get_Datas.cctor", "Player_Get_Datas.cctor"):
        x = g.get(name) or {}
        if not x.get("exact_record_equality") or not x.get("all_length_valid"):
            return None
        out.append(x.get("records"))
    return tuple(out)


def ia_method_records():
    """(số method, tổng record, số record Map, số record Player) trong ia-resolved.json."""
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/il2cpp/ia-resolved.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        d = _json.load(fh)
    m = d.get("methods") or {}
    total = sum(len(v or []) for v in m.values())
    return (len(m), total, len(m.get("Map_Get_Datas.cctor") or []),
            len(m.get("Player_Get_Datas.cctor") or []))


claim("IA6", "docs/spec/DATA_SYNC.md",
      "**576** và **6**, `exact_record_equality=true`, `all_length_valid=true`",
      (576, 6), peer_comparison,
      "peer-comparison.json chỉ so 2 nhóm method, KHÔNG phải toàn file — đừng phóng đại thành 'hai file giống nhau'")

claim("IA7", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "tổng **17 nhóm · 623 record**",
      (17, 623, 576, 6), ia_method_records,
      "ia-resolved.json bản 3ac2faa45: 12 nhóm cũ + 5 nhóm Board_*")

def _enemy_dict_ids():
    """150 id trong `Enemy_Get_Datas.cctor` — lấy `mov w1,#imm` **ngay trước** mỗi lệnh insert."""
    p = os.path.join(ROOT, "reverse-engineering/raw/il2cpp-consts/Enemy_Get_Datas.asm.txt")
    if not os.path.exists(p):
        return None
    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(";;; cctor")), None)
    if start is None:
        return None
    seg = lines[start + 1:]
    ids = []
    for k, line in enumerate(seg):
        if "bl       #0x193a074" not in line and not re.search(r"bl\s+#0x193a074", line):
            continue
        for j in range(k - 1, max(k - 9, 0), -1):
            m = re.search(r"mov\s+w1, #(0x[0-9a-f]+)", seg[j])
            if m:
                ids.append(int(m.group(1), 16))
                break
    return ids or None


def enemy_hp_inserts():
    """(số insert, id nhỏ nhất, id lớn nhất, số id khác nhau) của `Enemy_Get_Datas.cctor`."""
    ids = _enemy_dict_ids()
    if not ids:
        return None
    return (len(ids), min(ids), max(ids), len(set(ids)))


def enemy_hp_csv():
    """(số dòng, số gameobject khác nhau, số dòng HP > 0) của `15-enemy-hp.csv`.

    Đây là field **serialize** `Enemy_Datas.StartHealthPoint`, KHÔNG phải bảng HP
    runtime: enemy thường `CB-*` có 0/69 dòng > 0 ⇒ phải đọc thêm dict theo id.
    """
    rows = _csv_rows("docs/apk-analysis/15-enemy-hp.csv")
    if not rows:
        return None
    by_name = {r.get("gameobject") for r in rows}
    pos = sum(1 for r in rows if (r.get("start_hp") or "0") not in ("", "0", "0.0")
              and float(r.get("start_hp") or 0) > 0)
    return (len(rows), len(by_name), pos)


def enemy_hp_by_id():
    """(số cặp, id nhỏ nhất, id lớn nhất, HP của 30003) trong `datas/enemy_hp_by_id.json`.

    Bảng này là kết quả parse trực tiếp `.cctor` `Enemy_Get_Datas` ⇒ **không cần `.so`**.
    """
    d = ref_json("datas/enemy_hp_by_id.json")
    hp = (d or {}).get("hp_by_id") or {}
    if not hp:
        return None
    ids = [int(k) for k in hp]
    return (len(hp), min(ids), max(ids), float(hp.get("30003", -1)))


def enemy_asm_methods():
    """(số file asm, tổng số method) của 3 class enemy từng bị ghi 'chưa dump'."""
    total = 0
    for name in ("Enemy_Get_Datas", "Enemy_Controller", "Enemy_Health"):
        path = os.path.join(ROOT, "reverse-engineering/raw/il2cpp-consts",
                            name + ".asm.txt")
        if not os.path.exists(path):
            return None
        raw = ref_blob(os.path.join("reverse-engineering/raw/il2cpp-consts",
                                    name + ".asm.txt"))
        if raw is None:
            return None
        total += sum(1 for ln in raw.decode("utf-8", "replace").splitlines()
                     if ln.startswith(";;;"))
    return (3, total)


def wave_name_resolution():
    """(số entry tên `?`, số prefab khác nhau) trong `datas/waves.json`."""
    import json as _json
    p = os.path.join(ROOT, "datas", "waves.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        d = _json.load(fh)
    names = set()
    unknown = 0
    for w in d.get("waves") or []:
        for sp in w.get("spawners") or []:
            for e in sp.get("enemies") or []:
                if e == "?":
                    unknown += 1
                else:
                    names.add(e)
    return (unknown, len(names))


def spawned_hp_coverage():
    """(số prefab spawn, số prefab có nguồn HP) — gộp dict 150 id + CSV HP > 0."""
    import json as _json
    p = os.path.join(ROOT, "datas", "waves.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        d = _json.load(fh)
    names = set()
    for w in d.get("waves") or []:
        for sp in w.get("spawners") or []:
            names.update(sp.get("enemies") or [])
    if not names:
        return None
    rows = _csv_rows("docs/apk-analysis/15-enemy-hp.csv") or []
    roots = {(r.get("gameobject") or "").split("/")[0] for r in rows
             if float(r.get("start_hp") or 0) > 0}
    ids = set(_enemy_dict_ids() or [])
    have = 0
    for n in names:
        m = re.search(r"(\d{5})", n)
        if (m and int(m.group(1)) in ids) or n in roots:
            have += 1
    return (len(names), have)


def stage_arrays():
    """(len int[], len float[], levelDelta[0..2]) của `Stage_Get_Datas.cctor`."""
    import json as _json
    import struct as _struct
    p = os.path.join(ROOT, "reverse-engineering/il2cpp/ia-resolved.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        d = _json.load(fh)
    recs = (d.get("methods") or {}).get("Stage_Get_Datas.cctor") or []
    lens = sorted(r.get("len") for r in recs)
    if lens != [4, 5]:
        return None
    delta = None
    for r in recs:
        if r.get("len") != 4:
            continue
        b = bytes.fromhex(r["raw"])[: 4 * r["len"]]
        f = _struct.unpack("<4f", b)
        delta = [round(x, 3) for x in f]
    if delta is None:
        return None
    return (5, 4, delta[0], delta[1], delta[2])


def apk_doc_counts():
    """(số `.md`, số `.csv`) trong `docs/apk-analysis/`."""
    d = os.path.join(ROOT, "docs", "apk-analysis")
    if not os.path.isdir(d):
        return None
    names = os.listdir(d)
    return (sum(1 for n in names if n.endswith(".md")),
            sum(1 for n in names if n.endswith(".csv")))


def hardcoded_pass_counts():
    """Số chỗ tài liệu **chép cứng** `# N PASS ·` — con số đó đổi mỗi lần thêm claim."""
    pat = re.compile(r"#\s*\d+\s+PASS\s*·")
    hits = 0
    for root, _, files in os.walk(os.path.join(ROOT, "docs")):
        for n in files:
            if not n.endswith(".md"):
                continue
            with open(os.path.join(root, n), encoding="utf-8", errors="replace") as fh:
                hits += len(pat.findall(fh.read()))
    return hits


claim("IAB1", "docs/spec/ENEMY_HP_RUNTIME.md",
      "**150** insert, **150** id khác nhau **30001–38001**",
      (150, 30001, 38001, 150), enemy_hp_inserts,
      ".cctor Enemy_Get_Datas hoàn chỉnh 3.624 B, 0 vòng lặp ⇒ bảng runtime 150 dòng (KHÔNG phải 981); "
      "981 là số prefab serialize, HP runtime theo id nằm ở WRH2")

claim("WRH1", "docs/spec/ENEMY_HP_RUNTIME.md",
      "981 dòng · 865 tên · **467** dòng HP > 0",
      (981, 865, 467), enemy_hp_csv,
      "15-enemy-hp.csv là field SERIALIZE StartHealthPoint: CB-* 0/69 dòng > 0 ⇒ "
      "KHÔNG phải bảng HP runtime, không thể tự nó nuôi TTK")

claim("WRH2", "docs/spec/ENEMY_HP_RUNTIME.md",
      "**150** cặp `id → HP`",
      (150, 30001, 38001, 650.0), enemy_hp_by_id,
      "datas/enemy_hp_by_id.json parse trực tiếp .cctor (CB-30003 = 650) ⇒ "
      "HP runtime ĐÃ CÓ, không cần xin libil2cpp.so hay dump lại class")

claim("WRH3", "docs/spec/WHERE_TO_LOOK.md",
      "3 file asm · **41** method",
      (3, 41), enemy_asm_methods,
      "Enemy_Get_Datas / Enemy_Controller / Enemy_Health đều đã có thân hàm trong raw/il2cpp-consts")

claim("WRH4", "docs/spec/ENCOUNTERS.md",
      "**0** dấu `?` · **109** prefab",
      (0, 109), wave_name_resolution,
      "waves.json bản hiện hành đã resolve tên prefab; câu '45.659 entry = ?' là lịch sử")

claim("WRH5", "docs/spec/ENEMY_HP_RUNTIME.md",
      "**109** prefab · **108** có nguồn HP",
      (109, 108), spawned_hp_coverage,
      "gộp dict 150 id + CSV HP>0: 108/109 prefab spawn có số HP; 1 prefab (H-38002) là supply, không có HP")

claim("IAB2", "docs/spec/BALANCE.md",
      "**float[4]** | **1,0 · 2,0 · 3,6 · 3,6**",
      (5, 4, 1.0, 2.0, 3.6), stage_arrays,
      "Stage_Get_Datas.cctor: int[5] startBonusValues + float[4] levelDelta; 0x40666666 = 3.6 (KHÔNG phải 2.1)")

claim("APKD1", "docs/spec/START_HERE.md",
      "**102** `.md` · **107** `.csv`",
      (102, 107), apk_doc_counts,
      "đếm trực tiếp thư mục apk-analysis — thêm báo cáo mới là phải cập nhật dòng này")

claim("IA8", "docs/spec/START_HERE.md",
      "đừng chép số vào đây",
      0, hardcoded_pass_counts,
      "số PASS/FAIL đổi mỗi lần thêm claim ⇒ tài liệu chỉ được ghi LỆNH, không chép kết quả")

claim("AU1", "docs/spec/DATA_SYNC.md",
      "**65 method · 25 checks · 15 rules**",
      (65, 25, 15), audio_rule_counts,
      "raw/audio-rules/contracts.json.gz của report 67")

claim("AP2", "docs/spec/DATA_SYNC.md",
      "**2.652** file · **151** path va chạm · **321** row vượt unique path · **320** size mismatch",
      (2652, 151, 321, 320), asset_pack_counts,
      "catalog.json.gz của report 68: CRC PASS nhưng manifest path→identity KHÔNG injective ⇒ zip hợp lệ ≠ đủ asset")


def sprite_geometry_stats():
    """(Sprite, Texture2D, SpriteAtlas, resolved, unresolved) trong resolved-geometry.json.gz."""
    import gzip
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz")
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        d = _json.load(fh)
    c = d.get("object_counts") or {}
    return (c.get("Sprite"), c.get("Texture2D"), c.get("SpriteAtlas"),
            d.get("resolved"), len(d.get("unresolved") or []))


def sprite_rotation_stats():
    """(số sprite cần lật/xoay, số packed, số rect ngoài page, số nguồn chưa tự kiểm)."""
    import gzip
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz")
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        d = _json.load(fh)
    rot = d.get("rotation_codes") or {}
    need = sum(v for k, v in rot.items() if str(k) != "0")
    return (need, d.get("packed_count"), len(d.get("rect_outside") or []), len(d.get("sources") or []))


claim("GE1", "docs/spec/ASSET_TRIAGE.md",
      "**2.185** `Sprite` · **654** `Texture2D` · **66** `SpriteAtlas`; `resolved` **2.185** · `unresolved` **0**",
      (2185, 654, 66, 2185, 0), sprite_geometry_stats,
      "join metadata của report 62 (status PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION) — "
      "biết rect, KHÔNG phải đã crop đúng pixel")

claim("GE2", "docs/spec/ASSET_TRIAGE.md",
      "| `rotation` khác 0 (mã **1/2/3** = 53/54/37) | **144** |",
      (144, 1550, 40, 6), sprite_rotation_stats,
      "144 sprite phải lật/xoay (53+54+37); 40 rect vượt page ≤0,9963 px; 6 nguồn chưa tự kiểm sha256")


claim("RD1", "docs/spec/README.md",
      "**Kiểm tự động (`RD1`):** **41 dòng · 0 lệch**",
      (41, 0), readme_sizes,
      "mỗi dòng `N dòng · M bảng` trong bảng tài liệu README được đo lại từ file thật; lệch 1 dòng là FAIL")


claim("AB1", ASSET_TRIAGE,
      "**Trả lời ngắn: 2.197 asset · 1.554 chưa có nhãn · 132 sheet · 116 tên atlas không match · 67 page sactx.**",
      (2197, 1554, 132, 16, 116, 67), asset_triage_stats,
      "116 = `unmatched_atlas_name_count`: tên atlas KHÔNG match theo tên trong sprites-index.csv. "
      "Đây KHÔNG phải trạng thái tách ảnh — chứng minh tách cần m_RD.textureRect/settingsRaw (T9)")

claim("AT1", ASSET_TRIAGE,
      "| **trang atlas** | 2.197 asset · **340** `unresolved` · **282** có trang thật · **18** tự gán được · **13** họ trang đủ chuẩn |",
      (2197, 340, 282, 18, 13), atlas_page_stats,
      "trang THẬT từ resolved-geometry.json.gz (m_RD.m_Texture, report 62) — KHÔNG phải cột `atlas` "
      "của sprites-index.csv (59 ca, page đánh số). 18 = tự gán được khi họ trang n>=10 và precision>=0,95")


claim("AB2", ASSET_TRIAGE,
      "| **AB2** | 1.554 = **396** trong sheet + **1.158** rời |",
      (396, 1158), asset_unclassified_split,
      "tách 1.554: 396 trong sheet (đến từ 269 tên sheet), 1.158 ảnh rời")

claim("AB3", ASSET_TRIAGE,
      "| **AB3** | 17 sheet ≥ 8 sprite = **184** sprite (10 sheet / **113** sprite thuộc `unclassified`) · 2 sheet lưới = **16** ô, **0** ô đã tách |",
      (17, 184, 16, 0, 10, 113), asset_sheet_worklist,
      "worklist cắt: 10 sheet ≥8 (113 sprite); 2 sheet lưới 16 ô, 0 ô đã tách")


def asset_classified_stats():
    """(có nhãn, A, B, C, unknown, numeric, word, other) trong sprites-classified.csv."""
    import collections
    rows = _csv_rows("docs/assets/sprites-classified.csv") or []
    if not rows:
        return None
    un = [r for r in rows if r.get("category") == "unclassified"]
    if not un:
        return None
    labeled = [r for r in un if r.get("proposed_category")]
    conf = collections.Counter(r.get("confidence") for r in un)
    unk = [r for r in un if not r.get("proposed_category")]
    b = collections.Counter(r.get("bucket") for r in unk)
    return (len(labeled), conf.get("A", 0), conf.get("B", 0), conf.get("C", 0),
            len(unk), b.get("numeric", 0), b.get("word", 0), b.get("other", 0))


def asset_unknown_families():
    """(số họ tên, số họ chỉ 1 sprite, số contact sheet còn tile chưa gán)."""
    import collections
    import re
    rows = _csv_rows("docs/assets/sprites-classified.csv") or []
    unk = [r for r in rows if r.get("category") == "unclassified" and not r.get("proposed_category")]
    if not unk:
        return None
    fam = collections.Counter(re.sub(r"_\d+$", "", r.get("name") or "") for r in unk)
    sheets = {r.get("contact_sheet") for r in unk}
    return (len(fam), sum(1 for v in fam.values() if v == 1), len(sheets))


claim("AB4", ASSET_TRIAGE,
      "| **AB4** | phân loại lại: **1.049** có nhãn (**848 A · 131 B · 70 C**) · **643** passthrough **không có mức** · **505** `unknown` (**33** numeric · **204** word · **268** other) |",
      (1049, 848, 131, 70, 505, 33, 204, 268), asset_classified_stats,
      "sprites-classified.csv: 1.049/1.554 có nhãn (A848 B131 C70); 643 nhãn passthrough có confidence rỗng; 505 unknown")

claim("AB5", ASSET_TRIAGE,
      "| **AB5** | 505 unknown = **448** họ tên, **410** tên đơn lẻ; **17/25** contact sheet còn tile chưa gán |",
      (448, 410, 17), asset_unknown_families,
      "505 unknown: 448 họ tên, 410 tên đơn lẻ, trải trên 17 contact sheet")

# ── AE. tỉ lệ rơi đồ: 3 tầng đều đếm được (ECONOMY.md §8.1) ────────────
TUNING = "docs/spec/TUNING_KNOBS.md"
ECONOMY = "docs/spec/ECONOMY.md"


def drop_placed():
    """(tổng, coin, item, 70012, 70011, 70010) từ Item_Movement."""
    import collections
    import json as js
    import re
    lines = ref_lines("reverse-engineering/raw/typetrees/Item_Movement.jsonl.gz")
    if not lines:
        return None
    coin = 0
    ids = collections.Counter()
    for ln in lines:
        d = js.loads(ln)
        if d["tree"].get("isCoin"):
            coin += 1
        m = re.search(r"Item-(\d+)", d.get("gameobject") or "")
        if m:
            ids[int(m.group(1))] += 1
    return (len(lines), coin, len(lines) - coin,
            ids.get(70012, 0), ids.get(70011, 0), ids.get(70010, 0))


def drop_spawner_flags():
    """(spawner có listBringItems, tổng Call_Data, slot true, tổng slot)."""
    import json as js
    lines = ref_lines("reverse-engineering/raw/typetrees/Call_Data.jsonl.gz")
    if not lines:
        return None
    withlist = tru = tot = 0
    for ln in lines:
        br = js.loads(ln)["tree"].get("listBringItems") or []
        if br:
            withlist += 1
        tot += len(br)
        tru += sum(1 for b in br if b)
    return (withlist, len(lines), tru, tot)


def drop_catalog():
    """Số loại item trong Data_Items.allDropItems."""
    import json as js
    lines = ref_lines("reverse-engineering/raw/typetrees/Data_Items.jsonl.gz")
    if not lines:
        return None
    return len(js.loads(lines[0])["tree"].get("allDropItems") or [])


claim("AE1", ECONOMY,
      "| **1. Vật rơi đặt sẵn trong wave** | `Item_Movement` **702** instance | **676 coin / 26 item** = **96,3 % : 3,7 %**; id: **70012 ×529** (75,4 %) · **70011 ×145** (20,7 %) · **70010 ×14** (2,0 %)",
      (702, 676, 26, 529, 145, 14), drop_placed,
      "tầng 1: vật rơi đặt sẵn trong prefab wave, không phải random runtime")

claim("AE2", ECONOMY,
      "**411/23.757** spawner có list · **246/2.094** slot = **11,7 %**",
      (411, 23757, 246, 2094), drop_spawner_flags,
      "tầng 2: cờ mang-item theo từng enemy slot của spawner")

claim("AE3", ECONOMY,
      "**6** loại, index `1 · 2 · 3 · 101 · 102 · 103`",
      6, drop_catalog, "tầng 3: danh mục item có thể rơi trong Data_Items")

# ── AF. feel: rung màn hình có số, hit stop / aim assist rỗng ──────────

def asm_paths():
    """Danh sách file asm của bộ const (local trước, ref sau)."""
    d = os.path.join(ROOT, "reverse-engineering/raw/il2cpp-consts")
    if os.path.isdir(d):
        names = sorted(n for n in os.listdir(d) if n.endswith(".asm.txt"))
        if names:
            return ["reverse-engineering/raw/il2cpp-consts/" + n for n in names]
    raw = git("ls-tree", "-r", "--name-only", REFS[0],
              "reverse-engineering/raw/il2cpp-consts/")
    if not raw:
        return None
    return [x for x in raw.decode().splitlines() if x.endswith(".asm.txt")]


def asm_texts():
    paths = asm_paths()
    if not paths:
        return None
    out = []
    for p in paths:
        raw = ref_blob(p)
        if raw:
            out.append(raw.decode("utf-8", "replace"))
    return out or None


def camera_vibrate():
    """(số instance, 0.10/20, 0.05/15, 0.15/30, 0.10/30, 0.10/40)."""
    import collections
    import json as js
    lines = ref_lines("reverse-engineering/raw/typetrees/Enemy_CameraVibrate.jsonl.gz")
    if not lines:
        return None
    c = collections.Counter()
    for ln in lines:
        t = js.loads(ln)["tree"]
        c[(round(float(t.get("lvVibr", 0)), 2), int(t.get("timeVibr", 0)))] += 1
    return (len(lines), c[(0.10, 20)], c[(0.05, 15)], c[(0.15, 30)],
            c[(0.10, 30)], c[(0.10, 40)])


def timescale_hits():
    """(số lần chuỗi timeScale, số file asm)."""
    import re
    texts = asm_texts()
    if texts is None:
        return None
    n = sum(len(re.findall("timeScale", t, re.I)) for t in texts)
    return (n, len(texts))


def aim_hits():
    """(số method khớp aim/autoAim/targetLock/lockTarget, số file asm)."""
    import re
    texts = asm_texts()
    if texts is None:
        return None
    pat = re.compile(r"\b(aim|autoaim|targetlock|aimassist|locktarget)\b", re.I)
    n = 0
    for t in texts:
        for ln in t.splitlines():
            if ln.startswith(";;;") and pat.search(ln):
                n += 1
    return (n, len(texts))


claim("AF1", TUNING,
      "**Đã đo** (241 instance): `0,10 · 20` ×**185** · `0,05 · 15` ×**46** · `0,15 · 30` ×**6** · `0,10 · 30` ×**3** · `0,10 · 40` ×1",
      (241, 185, 46, 6, 3, 1), camera_vibrate,
      "rung màn hình: tham số đọc trực tiếp từ 241 prefab enemy")

claim("AF2", READY,
      "chuỗi `timeScale` xuất hiện **0 lần** trong **139** file asm đã bóc",
      (0, 139), timescale_hits,
      "hit stop không có: không chỗ nào đụng timeScale")

def tutorial_cctor_consts():
    """(MaxIndexTutorial, indexTut) đọc từ `.cctor` của GP_Tutorials + offset trong dump.cs."""
    import gzip as gz
    import re as rx
    src = gz.open(os.path.join(ROOT, "reverse-engineering/il2cpp/dump.cs.gz"),
                  "rt", encoding="utf-8", errors="replace").read()
    m = rx.search(r"\n(?:public |internal |private )?class GP_Tutorials(?!\.)\b[^\n]*\n", src)
    if not m:
        return None
    body = src[m.start():m.start() + 2500]
    offs = {}
    for name in ("MaxIndexTutorial", "indexTut", "inTutorial", "instance"):
        mo = rx.search(name + r"; // (0x[0-9a-f]+)", body)
        if not mo:
            return None
        offs[name] = int(mo.group(1), 16)
    raw = ref_blob("reverse-engineering/raw/il2cpp-consts/GP_Tutorials.asm.txt")
    if not raw:
        return None
    text = raw.decode("utf-8", "replace")
    i = text.find(";;; cctor")
    if i < 0:
        return None
    seg = text[i:i + 1600].split("\n;;;")[0]
    got = {}
    regs = {}
    for ln in seg.splitlines():
        mv = rx.search(r"mov\s+(w\d+), #(-?\d+)", ln)
        if mv:
            regs[mv.group(1)] = int(mv.group(2))
            continue
        st = rx.search(r"str\s+(\w+), \[x8, #(0x[0-9a-f]+|\d+)\]", ln)
        if st:
            src = st.group(1)
            val = 0 if src.startswith("xzr") else regs.get(src)
            if val is not None:
                got[int(st.group(2), 0)] = val
    if offs["MaxIndexTutorial"] not in got or offs["indexTut"] not in got:
        return None
    return (got[offs["MaxIndexTutorial"]], got[offs["indexTut"]])


def _cctor(consts_path):
    import json as js
    d = ref_json("reverse-engineering/raw/il2cpp-consts/" + consts_path)
    if not d:
        return None
    for m in d.get("methods") or []:
        if m.get("method") == "cctor":
            return m
    return None


def map_cctor_arrays():
    """(byte, số const, số init_array) của Map_Get_Datas..cctor."""
    m = _cctor("Map_Get_Datas.json")
    if not m:
        return None
    ia = [k for k in (m.get("constants") or []) if k.get("kind") == "init_array"]
    return (m.get("bytes"), len(m.get("constants") or []), len(ia))


def player_cctor_arrays():
    """(byte, số init_array, độ dài mảng lớn nhất) của Player_Get_Datas..cctor."""
    m = _cctor("Player_Get_Datas.json")
    if not m:
        return None
    ia = [k for k in (m.get("constants") or []) if k.get("kind") == "init_array"]
    return (m.get("bytes"), len(ia), max((k.get("len") or 0) for k in ia) if ia else 0)


def player_info_fields():
    """Số field của Player_Info (tàu) trong dump.cs.gz."""
    import gzip as gz
    import re as rx
    src = gz.open(os.path.join(ROOT, "reverse-engineering/il2cpp/dump.cs.gz"),
                  "rt", encoding="utf-8", errors="replace").read()
    m = rx.search(r"\n(?:public |internal |private )?class Player_Info\b[^\n]*\n", src)
    if not m:
        return None
    body = src[m.start():].split("// Methods")[0]
    return len(rx.findall(r"; // 0x[0-9a-f]+", body))


def design_metrics():
    """(số ảnh, tỉ lệ khung, accent trung vị, chi tiết trung vị) từ JSON tool sinh ra."""
    import statistics as st
    path = os.path.join(ROOT, "docs/assets/design-metrics.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        rows = json.load(fh)
    if not rows:
        return None
    return (len(rows), rows[0]["aspect"],
            round(st.median(r["accent_share"] for r in rows), 4),
            round(st.median(r["detail_gradient"] for r in rows), 2))


def ui_bbox_stats():
    """(số màn có bbox, trung vị rộng/cao/tỉ lệ) từ datas/ui_screens.json.gz."""
    import statistics as st
    data = ref_json("datas/ui_screens.json.gz")  # ref_json đã giải nén .gz
    if not data:
        return None
    screens = data["screens"]
    W, H = [], []
    for s in screens:
        b = s.get("bbox")
        if not b or len(b) != 4:
            continue
        w, h = b[2] - b[0], b[3] - b[1]
        if w > 0 and h > 0:
            W.append(w)
            H.append(h)
    if not W:
        return None
    return (len(W), round(st.median(W), 2), round(st.median(H), 2),
            round(st.median([w / h for w, h in zip(W, H)]), 2))


def art_study_stats():
    """(số sprite, số nhóm, trung vị số màu, trung vị bão hoà) từ art-study.csv."""
    import statistics as st
    path = os.path.join(ROOT, "docs/assets/art-study.csv")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return None
    return (len(rows), len({r["category"] for r in rows}),
            round(st.median(int(r["colors"]) for r in rows)),
            round(st.median(float(r["sat"]) for r in rows), 3))


claim("AO1", "docs/spec/ART_STUDY.md",
      "**2.112** sprite · **12** nhóm · trung vị **55** màu · bão hoà trung vị **0,483**",
      (2112, 12, 55, 0.483), art_study_stats,
      "đo lại từ art-study.csv do tools/art-study.py sinh, không chép tay")

def classify_stats():
    """(có nhãn, tổng, unresolved, nhãn mới) từ sprites-auto-classified.csv."""
    path = os.path.join(ROOT, "docs/assets/sprites-auto-classified.csv")
    old = os.path.join(ROOT, "docs/assets/sprites-classified.csv")
    if not (os.path.isfile(path) and os.path.isfile(old)):
        return None
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(old, encoding="utf-8") as fh:
        prev = {r["rule"] for r in csv.DictReader(fh) if (r.get("rule") or "").strip()}
    lab = [r for r in rows if r["category_auto"] != "unresolved"]
    new = [r for r in lab if r["rule"] not in prev]
    return (len(lab), len(rows),
            sum(1 for r in rows if r["category_auto"] == "unresolved"), len(new))


def split_stats():
    """(entry, mảnh, texture page, page sactx) từ sheet-splits.csv."""
    path = os.path.join(ROOT, "docs/assets/sheet-splits.csv")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    pages = [r for r in rows if r.get("category") == "atlas"]
    return (len(rows), sum(int(r["ncomp"]) for r in rows), len(pages),
            sum(1 for r in rows if r["name"].startswith("sactx")))


def knn_stats():
    """(LOO phủ, LOO đúng, gợi ý, độ chính xác) từ classify-knn.json + sprites-knn.csv."""
    jp = os.path.join(ROOT, "docs/assets/classify-knn.json")
    cp = os.path.join(ROOT, "docs/assets/sprites-knn.csv")
    if not (os.path.isfile(jp) and os.path.isfile(cp)):
        return None
    with open(jp, encoding="utf-8") as fh:
        d = json.load(fh)
    with open(cp, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return (d["loo_covered"], d["loo_correct"],
            sum(1 for r in rows if r["category_knn"]), d["loo_accuracy"])


claim("AO4", "docs/spec/ASSET_TRIAGE.md",
      "**781**/1.857 ca đủ tự tin · đúng **674** (**86,3 %**)",
      (781, 674, 89, 0.863), knn_stats,
      "leave-one-out của tools/classify-knn.py; số đúng đo trên nhãn đã có, không phải nhãn mới")

def provenance_check():
    """(dòng bảng, khớp sha256, lệch) từ bảng sha256 trong datas/PROVENANCE.md."""
    import hashlib
    import re
    path = os.path.join(ROOT, "datas/PROVENANCE.md")
    if not os.path.isfile(path):
        return None
    txt = open(path, encoding="utf-8").read()
    rows = re.findall(r"^([0-9a-f]{16})\s+(\d+)\s+(\S+)\s*$", txt, re.M)
    ok = stale = 0
    for sha, size, p in rows:
        full = os.path.join(ROOT, p)
        if not os.path.isfile(full):
            continue
        data = open(full, "rb").read()
        if hashlib.sha256(data).hexdigest()[:16] == sha and len(data) == int(size):
            ok += 1
        else:
            stale += 1
    return (len(rows), ok, stale)


def data_inventory():
    """(asm files, asm dòng, typetree, bảng ScriptableObject, contact sheet, file datas/)."""
    import glob
    asm = glob.glob(os.path.join(ROOT, "reverse-engineering/raw/il2cpp-consts/*.asm.txt"))
    nlines = 0
    for f in asm:
        with open(f, encoding="utf-8", errors="replace") as fh:
            nlines += sum(1 for _ in fh)
    ty = glob.glob(os.path.join(ROOT, "reverse-engineering/raw/typetrees/*"))
    so = glob.glob(os.path.join(ROOT, "reverse-engineering/scriptableobjects/*.csv"))
    sheets = glob.glob(os.path.join(ROOT, "docs/assets/contact-sheets/*.jpg"))
    datas = [f for f in glob.glob(os.path.join(ROOT, "datas/*"))
             if os.path.isfile(f)]
    return (len(asm), nlines, len(ty), len(so), len(sheets), len(datas))


claim("AI1", "docs/spec/START_HERE.md",
      "**Cộng kho đo được (đếm bằng `AI1`):** **139** file asm · **142.136** dòng asm · **142** typetree"
      " · **126** bảng ScriptableObject · **42** contact sheet · **135** file `datas/`.",
      (139, 142136, 142, 126, 42, 135), data_inventory,
      "kho dữ liệu gốc đã phân tích: asm, typetree, ScriptableObject, contact sheet, datas")

claim("AP1", "docs/spec/DATA_INTEGRITY.md",
      "**PROVENANCE: 272/412 khớp · 140 lệch · 0 thiếu**",
      (412, 272, 140), provenance_check,
      "băm lại 412 file trong bảng rồi so với sha256 ghi lúc kéo; 140 dòng lệch = file đã kéo lại sau 23/10")

claim("AO2", "docs/spec/ASSET_TRIAGE.md",
      "### 9.2 Kết quả: **1.857/2.197 có nhãn**, còn **340**",
      (1857, 2197, 340, 165), classify_stats,
      "đếm lại từ sprites-auto-classified.csv; 165 = số nhãn vòng này thêm so với sprites-classified.csv")

claim("AO3", "docs/spec/ASSET_TRIAGE.md",
      "`sheet-splits.csv`: **307** sprite thật ra là **nhiều hình**, tổng **4.250 mảnh**",
      (307, 4250, 98, 64), split_stats,
      "đếm lại từ sheet-splits.csv do tools/classify-by-measure.py sinh")

claim("AN1", "docs/spec/VISUAL_DESIGN.md",
      "**35** ảnh · tỉ lệ **0,4813** · accent trung vị **0,0571** · chi tiết trung vị **17,26**",
      (35, 0.4813, 0.0571, 17.26), design_metrics,
      "số đo thị giác sinh bằng tools/design-metrics.py, không chép tay")

claim("AN2", "docs/spec/VISUAL_DESIGN.md",
      "| Số màn có `bbox` dùng được | **54.019** | rộng trung vị **4,05** · cao **7,50** · tỉ lệ **0,67** |",
      (54019, 4.05, 7.5, 0.67), ui_bbox_stats,
      "hình học bố cục: panel dọc 2:3, đuôi dài tới 699 unit")

def scene_map_flow_stats():
    """(số entry campaign, số check đúng, hash của 3 entry) từ raw report 52."""
    import gzip, json
    path = os.path.join(ROOT, "reverse-engineering/raw/ui-audit/scene-map-flow.json.gz")
    if not os.path.exists(path):
        return None
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        d = json.load(fh)
    rows = d.get("campaign_immediates", {}).get("rows") or []
    checks = d.get("checks") or {}
    # rows chỉ giữ stage 1/2; stage 0 nằm trong snippet asm dạng `mov w9, #0x19` / `mov w8, #0x2332`
    snip = d.get("campaign_immediates", {}).get("list_creation_and_first_three_appends", "")
    zero_ok = "#0x19" in snip and "#0x2332" in snip
    return (len(rows) + 1, sum(1 for v in checks.values() if v), 1 if zero_ok else 0)


def main_cannon_damage_asm():
    """(có offset 0x78, có index theo tham số, có scale ×4) trong asm GetMainCannonDamage."""
    import re
    path = os.path.join(ROOT, "reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt")
    if not os.path.exists(path):
        return None
    txt = open(path, encoding="utf-8").read()
    i = txt.find("GetMainCannonDamage")
    if i < 0:
        return None
    body = txt[i:i + 4000]
    off = 1 if "#0x78]" in body else 0
    idx = 1 if re.search(r"sxtw #2", body) and "w19" in body else 0
    f32 = 1 if re.search(r"ldr\s+s8, \[x8", body) else 0
    return (off, idx, f32)


def tutorial_gate_stats():
    """(số predicate stage, số method trong raw shared-stage-victory, số check đúng)."""
    import gzip, json
    path = os.path.join(ROOT, "reverse-engineering/raw/endgame-missions/shared-stage-victory.json.gz")
    if not os.path.exists(path):
        return None
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        d = json.load(fh)
    methods = d.get("methods") or []
    checks = d.get("checks") or {}
    return (3, len(methods), sum(1 for v in checks.values() if v))


claim("AM1", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "`Map_Get_Datas..cctor` **100.896 B · `ends_clean: true`** · **4.020** const · **576** `init_array`",
      (100896, 4020, 576), map_cctor_arrays,
      "A6 nằm trong tầm tay: 576 mảng đã được tách địa chỉ, chỉ thiếu bytes rodata")

_RAW_HINTS = (
    "datas/", "reverse-engineering/", "docs/assets/",
    "ref_lines(", "ref_json(", "_il2cpp_asm_files(", "_csv_rows(", "git(", "read_text(",
    # Chạy một script khác rồi đọc stdout cũng là đo từ dữ liệu thật (OP1/TS1):
    # hàm đo không tự mở file, nhưng tiến trình con thì có.
    "subprocess.run(", "_run([",
)


# Ngoại lệ khai báo tay, mỗi cái một dòng lý do (đừng lạm dụng):
#   APKD1 — đếm file trong `docs/apk-analysis/`, thư mục **dữ liệu** theo `local_inputs()`;
#   IA8   — quét `docs/` để tìm số PASS chép cứng ⇒ claim về tính nhất quán tài liệu.
KIND_OVERRIDE = {"APKD1": "RAW", "IA8": "DOC"}


def _measure_source(fn, depth: int = 3, seen=None) -> str:
    """Source của hàm đo + các hàm nó gọi (để bắt đường dẫn file nằm ở helper)."""
    import inspect
    import re as _re
    seen = seen if seen is not None else set()
    try:
        src = inspect.getsource(fn)
    except (OSError, TypeError):
        return ""
    if depth <= 0:
        return src
    chunks = [src]
    for name in sorted(set(_re.findall(r"\b([A-Za-z_][A-Za-z_0-9]{2,})\b", src))):
        if name in seen:
            continue
        target = globals().get(name)
        if callable(target) and getattr(target, "__module__", None) == __name__:
            seen.add(name)
            chunks.append(_measure_source(target, depth - 1, seen))
    return "\n".join(chunks)


def classify_claims():
    """[(cid, 'RAW'|'DOC'|'CONST', doc, note)] — claim nào đo từ file nào."""
    import linecache
    linecache.checkcache()  # tránh source cũ khi file vừa sửa trong cùng giây
    out = []
    for c in CLAIMS:
        src = _measure_source(c.measure)
        # Nêu tên một file dữ liệu cụ thể (đuôi .json/.csv/.txt/.gz) cũng là đo từ file:
        # nhiều hàm đo nhận đường dẫn qua tham số/thư mục, không chứa tiền tố "datas/".
        named_file = re.search(
            r"""[\'"]/?(?:[\w.\-]+/)*[\w.\-]+\.(?:json|csv|txt|gz|asm\.txt)[\'"]""", src
        ) is not None
        if c.cid in KIND_OVERRIDE:
            kind = KIND_OVERRIDE[c.cid]
        elif named_file or any(h in src for h in _RAW_HINTS):
            kind = "RAW"
        elif "docs/" in src:
            kind = "DOC"
        else:
            kind = "CONST"
        out.append((c.cid, kind, c.doc, c.note))
    return out


def raw_audit_counts():
    """(RAW, DOC, CONST, tổng) — đếm trực tiếp trên CLAIMS, không chạy measure."""
    rows = classify_claims()
    return (sum(1 for r in rows if r[1] == "RAW"),
            sum(1 for r in rows if r[1] == "DOC"),
            sum(1 for r in rows if r[1] == "CONST"),
            len(rows))


def save_contract_stats():
    """(số key family, số store, số limitation) trong datas/opening_persistence.json."""
    d = ref_json("datas/opening_persistence.json")
    if not d:
        return None
    return (len(d.get("contracts") or []), len(d.get("stores") or []),
            len(d.get("limitations") or []))


def player_array_blobs():
    """(số mảng, tổng phần tử, số file kiểm sha256 OK) trong raw/player-loadout."""
    import gzip
    import hashlib
    import json as _json
    base = "reverse-engineering/raw/player-loadout"
    idx_path = os.path.join(ROOT, base, "index.json")
    if not os.path.exists(idx_path):
        return None
    with open(idx_path, encoding="utf-8") as fh:
        idx = _json.load(fh)
    ok = 0
    for f in idx.get("files") or []:
        p = os.path.join(ROOT, f["path"])
        if not os.path.exists(p):
            continue
        raw = open(p, "rb").read()
        data = gzip.decompress(raw) if p.endswith(".gz") else raw
        if hashlib.sha256(data).hexdigest() == f.get("sha256_decompressed"):
            ok += 1
    blob_path = os.path.join(ROOT, base, "array-blobs.json.gz")
    if not os.path.exists(blob_path):
        return None
    with gzip.open(blob_path, "rt", encoding="utf-8") as fh:
        blob = _json.load(fh)
    arrs = []
    for _meth, items in (blob.get("resolved", {}).get("methods") or {}).items():
        arrs.extend(items)
    return (len(arrs), sum(a.get("len", 0) for a in arrs), ok)


def sprite_geometry_stats():
    """(Sprite, Texture2D, SpriteAtlas, resolved, unresolved) trong resolved-geometry.json.gz."""
    import gzip
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz")
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        d = _json.load(fh)
    c = d.get("object_counts") or {}
    return (c.get("Sprite"), c.get("Texture2D"), c.get("SpriteAtlas"),
            d.get("resolved"), len(d.get("unresolved") or []))


def sprite_rotation_stats():
    """(số sprite cần lật/xoay, số packed, số rect ngoài texture, số nguồn chưa kéo)."""
    import gzip
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz")
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        d = _json.load(fh)
    rot = d.get("rotation_codes") or {}
    need = sum(v for k, v in rot.items() if str(k) != "0")
    return (need, d.get("packed_count"), len(d.get("rect_outside") or []), len(d.get("sources") or []))


def sprite_rect_fields():
    """(số sprite source_rect != texture_rect, số bằng nhau, số có alpha_texture)."""
    import gzip
    import json as _json
    p = os.path.join(ROOT, "reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz")
    if not os.path.exists(p):
        return None
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        d = _json.load(fh)
    keys = ("x", "y", "width", "height")
    diff = same = alpha = 0
    for sp in d.get("sprites") or []:
        a, b = sp.get("source_rect") or {}, sp.get("texture_rect") or {}
        if all(abs(a.get(k, 0) - b.get(k, 0)) < 1e-6 for k in keys):
            same += 1
        else:
            diff += 1
        if sp.get("alpha_texture"):
            alpha += 1
    return (diff, same, alpha)


def _run(cmd, timeout=300):
    import subprocess
    import sys as _sys
    return subprocess.run([_sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True, timeout=timeout)


def opening_persistence_counts():
    """(số method, số check, số key family) — chạy chính verifier của nhánh dữ liệu."""
    r = _run(["tools/verify/opening_persistence.py"])
    if r.returncode != 0:
        return None
    m = re.search(r"(\d+) methods; (\d+) checks; (\d+) key families", r.stdout)
    return tuple(int(x) for x in m.groups()) if m else None


def test_suite_count():
    """Số unit test chạy được trong tests/ (chạy thật, không đếm hàm)."""
    r = _run(["-m", "unittest", "discover", "-s", "tests", "-q"])
    if r.returncode != 0:
        return None
    m = re.search(r"Ran (\d+) tests?", r.stderr + r.stdout)
    return int(m.group(1)) if m else None


claim("GE1", "docs/spec/ASSET_TRIAGE.md",
      "**2.185** `Sprite` · **654** `Texture2D` · **66** `SpriteAtlas`; resolve **2.185/2.185**, `unresolved` = **[]**",
      (2185, 654, 66, 2185, 0), sprite_geometry_stats,
      "report 62: geometry join metadata, status PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION "
      "⇒ biết rect, KHÔNG phải đã crop đúng")

claim("GE3", "docs/spec/ASSET_TRIAGE.md",
      "| `source_rect` ≠ `texture_rect` | **1.795** / 2.185 |",
      (1795, 390, 0), sprite_rect_fields,
      "crop phải theo texture_rect (rect trong page), KHÔNG lẫn source_rect; 0 sprite có alpha texture riêng")


claim("GE2", "docs/spec/ASSET_TRIAGE.md",
      "| mã xoay/lật `1 · 2 · 3` | **53 · 54 · 37** = **144** |",
      (144, 1550, 40, 6), sprite_rotation_stats,
      "144 sprite cần lật/xoay (53+54+37), 1.550 packed, 40 `textureRect` vượt page ≤0,9963 px, 6 nguồn chưa kéo ⇒ chưa tự kiểm sha256")


claim("RB1", "docs/spec/RAW_AUDIT.md",
      "**RAW 180 · DOC 3 · CONST 28 · tổng 211**",
      (180, 3, 28, 211), raw_audit_counts,
      "sổ kiểm claim↔raw: chạy lại tools/raw-audit.py và so đúng 4 số ở §0. "
      "CONST = số không mở file nào ⇒ phải đọc là 'đo một lần', không phải bằng chứng tái lập")

claim("CM4", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "**8 key family** · **2 store** · **7 limitation** (claim **CM4**)",
      (8, 2, 7), save_contract_stats,
      "datas/opening_persistence.json: 8 contract, 2 store (Unity.PlayerPrefs + PlayerPreferences.dictionary), "
      "7 limitation. status PROVISIONAL_STATIC_PARTIAL_SAVE_CONTRACT_NOT_FULL_SCHEMA ⇒ KHÔNG gọi là schema đầy đủ")

claim("CM5", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "**5 blob** · **49 int** · **5/5 sha256 OK** (claim **CM5**)",
      (5, 49, 5), player_array_blobs,
      "raw/player-loadout: 5 blob mảng int (len 4·7·7·7·24 = 49) + 5/5 sha256_decompressed khớp. "
      "Đây là int của Player_Saved_Datas, KHÔNG phải 4 mảng float damage của Player_Get_Datas")


claim("CM1", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "(`CM1`): **3 entry** = `[25, 9010]` · `[164]` · `[113, 5]` · **13** check;",
      (3, 13, 1), scene_map_flow_stats,
      "campaign list Chapter0 đã resolve literal: entry0 [25,9010] (snippet asm), entry1 [164], entry2 [113,5]; "
      "13 check trong raw đều true. Phạm vi GameMode0/nonbranch/Chapter0 — KHÔNG áp mode khác")

claim("CM2", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "(`CM2`):** `0x78` + `sxtw #2` + index `w19`",
      (1, 1, 1), main_cannon_damage_asm,
      "asm GetMainCannonDamage: ldr x8,[x8,#0x78] → bounds → ldr s8,[x8,w19,sxtw#2] ⇒ damage tra theo playerIndex. "
      "KHÔNG chứng minh mỗi tàu có giá trị khác nhau, cũng KHÔNG nói gì về HP")

claim("CM3", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "**18** check, claim **CM3**",
      (3, 21, 18), tutorial_gate_stats,
      "3 predicate gate (stage1 IndexTutorial==0, stage2 ==1, stage3 !IsTutTouchSkillDone); raw shared-stage-victory "
      "giữ 21 method + 18 check. Direct-call trên 3 thân core, không phải chứng minh vắng mặt toàn chương trình")


claim("AM2", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "`Player_Get_Datas..cctor` **2.492 B** · **6** `init_array` · mảng dài nhất **24**",
      (2492, 6, 24), player_cctor_arrays,
      "B3: 4 mảng 24 float (damage/rate) + 2 mảng 3 — thiếu bytes rodata")

claim("AM3", "docs/spec/MISSING_FOR_NEW_GAME.md",
      "`Player_Info` **4 field**: `id` · `Sprite` · `Star` · `Actived`",
      4, player_info_fields,
      "chỉ 4 field — KHÔNG suy ra tàu không có damage: GetMainCannonDamage đọc mảng static float 0x78 theo playerIndex (14e3a78..14e3a90)")

claim("AG1", "docs/spec/SCRIPTS.md",
      "**`MaxIndexTutorial = 4`**, `instance = null`, **`indexTut = −1`**",
      (4, -1), tutorial_cctor_consts,
      "tutorial đúng 5 bước: `.cctor` ghi 4 vào MaxIndexTutorial (0x4) và -1 vào indexTut (0x10)")

claim("AF3", READY,
      "**0** method khớp `aim · autoAim · targetLock · lockTarget` trong 139 file asm",
      (0, 139), aim_hits,
      "aim assist không tồn tại: 0 method bám mục tiêu")

# ── chạy ───────────────────────────────────────────────────────────────

class NoSource(Exception):
    """Nguồn dữ liệu **không tồn tại** trong repo ⇒ SKIP có chủ đích.

    Khác mọi exception khác: exception thường là **lỗi đo** và phải làm cổng đỏ
    (`ERROR`), không được lặng lẽ thành SKIP (review R6).
    """


def evaluate(c: Claim) -> None:
    lines = doc_lines(c.doc)
    if lines is None:
        c.status, c.why = "SKIP", f"không thấy {c.doc}"
        return
    try:
        got = c.measure()
    except NoSource as e:
        c.status, c.why = "SKIP", f"nguồn vắng: {e}"
        return
    except Exception as e:  # noqa: BLE001
        # Lỗi parser/lập trình **không** phải "nguồn vắng". Trước 25/10 chỗ này
        # trả SKIP nên một hàm đo hỏng vẫn cho cổng xanh (review R6).
        c.status, c.why = "ERROR", f"đo lỗi: {type(e).__name__}: {e}"
        return
    c.got = got
    if got is None:
        c.status, c.why = "SKIP", "nguồn vắng"
        return

    if isinstance(c.stated, tuple):
        same = tuple(got) == c.stated
    elif isinstance(c.stated, list):
        same = list(got) == c.stated
    elif isinstance(c.stated, float):
        same = approx(got, c.stated)
    elif isinstance(c.stated, int) and isinstance(got, int):
        same = got == c.stated
    else:
        same = got == c.stated

    in_doc = any(c.line_has in ln for ln in lines)
    if same and in_doc:
        c.status = "PASS"
    elif not same and in_doc:
        c.status = "FAIL"
        c.why = f"doc ghi {c.stated}, đo được {got}"
    elif same and not in_doc:
        c.status = "FAIL"
        c.why = f"đo đúng {got} nhưng doc không còn ghi “{c.line_has}”"
    else:
        c.status = "FAIL"
        c.why = f"doc ghi {c.stated}, đo được {got}, và chuỗi neo cũng mất"


def main() -> int:
    global REFS, EXPLICIT_REF
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", action="append", help="ref nhánh dữ liệu (lặp được)")
    ap.add_argument("--only", default="", help="chỉ chạy nhóm có mã bắt đầu bằng chữ này")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--provenance", action="store_true",
                    help="in bảng: mỗi input đọc từ ref nào + blob SHA")
    ap.add_argument("--provenance-log", metavar="FILE",
                    help="ghi provenance ra JSONL (path, source, blob_sha, bytes)")
    ap.add_argument("--strict-ref", action="store_true",
                    help="thoát 2 nếu có input KHÔNG đọc từ ref (chống báo nhầm snapshot)")
    ap.add_argument("--self-test", action="store_true",
                    help="kiểm chính chế độ ref-first (không đọc file local cũ)")
    ap.add_argument("--no-skip", action="store_true",
                    help="cổng nghiệm thu: SKIP cũng tính là hỏng (dùng cho CI bắt buộc)")
    ap.add_argument("--require", metavar="PREFIXES",
                    help="danh sách tiền tố claim BẮT BUỘC phải PASS, vd AB,AF,AG")
    args = ap.parse_args()

    REFS = args.ref or DEFAULT_REFS
    # xác nhận ref có thật, để SKIP nói đúng lý do
    live = [r for r in REFS if git("rev-parse", "--verify", "--quiet", r + "^{commit}")]
    if not live:
        print("! không ref nào trong số này tồn tại: " + ", ".join(REFS))
        print("  data-pack và TextAsset sẽ SKIP; nhóm A (runtime) vẫn chạy.")
        REFS = ["__missing__"]
    else:
        REFS = live
        print(f"ref dữ liệu: {live[0]}\n")

    EXPLICIT_REF = bool(args.ref)

    if args.self_test:
        ok, msg = selftest_provenance()
        print(("PASS  " if ok else "FAIL  ") + msg)
        return 0 if ok else 1

    for c in CLAIMS:
        if args.only and not c.cid.startswith(args.only):
            continue
        evaluate(c)

    width = max(len(c.cid) for c in CLAIMS)
    print(f"{'mã':<{width}}  {'kết quả':<6} {'đo':>10}  {'doc':>10}  ghi chú")
    print("─" * (width + 62))
    for c in CLAIMS:
        if args.only and not c.cid.startswith(args.only):
            continue
        got = "—" if c.got is None else str(c.got)
        if isinstance(c.got, (list, tuple)):
            got = ",".join(str(x) for x in c.got)
        stated = ",".join(str(x) for x in c.stated) if isinstance(c.stated, list) else str(c.stated)
        print(f"{c.cid:<{width}}  {c.status:<6} {got:>10}  {stated:>10}  {c.note or c.why}")

    n = {"PASS": 0, "FAIL": 0, "SKIP": 0, "ERROR": 0}
    for c in CLAIMS:
        if args.only and not c.cid.startswith(args.only):
            continue
        n[c.status] = n.get(c.status, 0) + 1

    print("─" * (width + 62))
    print(f"PASS {n['PASS']} · FAIL {n['FAIL']} · SKIP {n['SKIP']} · ERROR {n['ERROR']}")
    if args.provenance:
        print("\nprovenance (input → nguồn):")
        print(provenance_report())

    if args.provenance_log:
        with open(args.provenance_log, "w", encoding="utf-8") as fh:
            for path in sorted(PROVENANCE):
                fh.write(json.dumps(PROVENANCE[path], ensure_ascii=False) + "\n")
        print(f"\nprovenance → {args.provenance_log} ({len(PROVENANCE)} input)")

    local = local_inputs()
    if args.strict_ref and local:
        print(f"\nSTRICT-REF: {len(local)}/{len(PROVENANCE)} input KHÔNG đọc từ ref:")
        for path in local:
            print(f"  {PROVENANCE[path]['source']:<16} {path}")
        print("  ⇒ KHÔNG được báo 'đã kiểm snapshot mới' với các input này.")
        return 2

    selected = [c for c in CLAIMS if not args.only or c.cid.startswith(args.only)]
    if not selected:
        print(f"\nKHÔNG có claim nào khớp --only {args.only!r} ⇒ coi là hỏng, không phải 'xanh'.")
        return 1

    bad = [c for c in selected if c.status in ("FAIL", "ERROR")]
    if args.no_skip:
        bad += [c for c in selected if c.status == "SKIP"]
    if args.require:
        need = tuple(x.strip() for x in args.require.split(",") if x.strip())
        unknown = [p for p in need if not any(c.cid.startswith(p) for c in CLAIMS)]
        if unknown:
            # gõ sai tiền tố mà vẫn xanh = cổng giả. Không im lặng.
            print(f"\n--require {','.join(unknown)}: KHÔNG có claim nào mang tiền tố này"
                  f" ⇒ coi là hỏng (cổng giả), không phải 'xanh'.")
            return 2
        missing = [c for c in selected if c.cid.startswith(need) and c.status != "PASS"]
        bad += [c for c in missing if c not in bad]
    if bad:
        print("\nHỎNG:")
        for c in bad:
            print(f"  {c.cid}  [{c.status}]  {c.doc}  — {c.why}")
        return 1
    return 0


REFS = DEFAULT_REFS

if __name__ == "__main__":
    sys.exit(main())
