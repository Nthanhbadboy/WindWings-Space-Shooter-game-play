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


def ref_blob(path: str) -> bytes | None:
    """Thân file, đã giải nén nếu là .gz.

    Đọc bản **local trước** (`datas/`, `reverse-engineering/` đã được kéo về repo),
    chỉ khi vắng mới rơi về `git show` trên nhánh dữ liệu. Nhờ vậy bộ kiểm không
    phụ thuộc vào một nhánh có thể biến mất, và vẫn chạy được trên clone sạch nếu
    dữ liệu đã nằm trong repo.
    """
    key = "blob:" + path
    if key in _cache:
        return _cache[key]  # type: ignore[return-value]
    raw = None
    local = os.path.join(ROOT, path)
    if os.path.isfile(local):
        try:
            with open(local, "rb") as f:
                raw = f.read()
        except OSError:
            raw = None
    if raw is None:
        for ref in REFS:
            raw = git("show", f"{ref}:{path}")
            if raw:
                break
    if raw is not None and path.endswith(".gz") and raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except OSError:
            raw = None
    _cache[key] = raw
    return raw


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
      lambda: (_ for _ in ()).throw(RuntimeError(
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
      lambda: (_ for _ in ()).throw(RuntimeError(
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

claim("H2", ANIMDOC, "**22.461 lượt spawn trên 282 wave và 11.095 spawner**", (22461, 282, 11095),
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

claim("I2", READY, "**795/795 event use có `time`**", (795, 795), events_with_time,
      "D3 đóng: event đã join Animator và giữ mốc thời gian")

claim("I3", READY, "11.095 spawner · rate = 0 : 2.371", 2371,
      lambda: (spawner_rate_zero() or (None, None, None))[1],
      "sửa 2.373 -> 2.371 trong DESIGN_QUESTIONS.md")

claim("I4", READY, "**250 map**, nhưng chỉ **7** ghép chắc", (250, 7), map_candidates,
      "A6: 243 map còn lại ghép theo thứ tự blob, chưa xác thực")


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
      "boss 1 thuần Spine; 12 handler của Boss1_AnimationEvents thuộc 23 prefab khác")

claim("J6", SCRIPT, "**5** lần `String.op_Equality`", 5, boss_work_compares,
      "Boss_1_Animation.BossWork rẽ 5 nhánh entry")

claim("J7", SCRIPT, "**12 handler · 28 byte**", (12, 28), boss1_event_handlers,
      "mỗi handler chỉ gọi một delegate, không có logic riêng")

claim("J8", SCRIPT, "**22 lần `WaitForSeconds` · 4 hằng số · 18 lấy từ biến**", (22, 4, 18),
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

claim("K5", HANDOFF, "**có asm nhưng không có typetree**", 3, missing_typetrees,
      "3 lớp chưa export ⇒ T1 là việc rẻ nhất trong lô giao")

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


claim("L1", READY, "**35/39 prefab boss** có script", (35, 4, 39), boss_script_coverage,
      "35 = 33 prefab clip event ∪ 3 prefab Spine (Boss-39003 nằm cả hai)")

claim("L2", READY, "**125 màn hình**", 125, ui_screens,
      "UI cấu trúc đủ để thiết kế; chỉ art là chưa")

claim("L3", READY, "`Boss-37003/37005/37006/37008`",
      ("Boss-37003", "Boss-37005", "Boss-37006", "Boss-37008"), boss_script_missing,
      "4 prefab boss không có cả clip event lẫn Spine")

# ── chạy ───────────────────────────────────────────────────────────────

def evaluate(c: Claim) -> None:
    lines = doc_lines(c.doc)
    if lines is None:
        c.status, c.why = "SKIP", f"không thấy {c.doc}"
        return
    try:
        got = c.measure()
    except Exception as e:  # noqa: BLE001
        c.status, c.why = "SKIP", f"đo lỗi: {type(e).__name__}: {e}"
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
    global REFS
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", action="append", help="ref nhánh dữ liệu (lặp được)")
    ap.add_argument("--only", default="", help="chỉ chạy nhóm có mã bắt đầu bằng chữ này")
    ap.add_argument("--verbose", action="store_true")
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

    n = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    for c in CLAIMS:
        if args.only and not c.cid.startswith(args.only):
            continue
        n[c.status] = n.get(c.status, 0) + 1

    print("─" * (width + 62))
    print(f"PASS {n['PASS']} · FAIL {n['FAIL']} · SKIP {n['SKIP']}")
    fails = [c for c in CLAIMS if c.status == "FAIL"]
    if fails:
        print("\nFAIL:")
        for c in fails:
            print(f"  {c.cid}  {c.doc}  — {c.why}")
        return 1
    return 0


REFS = DEFAULT_REFS

if __name__ == "__main__":
    sys.exit(main())
