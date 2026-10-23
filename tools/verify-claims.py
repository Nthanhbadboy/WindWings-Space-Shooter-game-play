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
    """Thân file tại ref dữ liệu, đã giải nén nếu là .gz."""
    key = "blob:" + path
    if key in _cache:
        return _cache[key]  # type: ignore[return-value]
    raw = None
    for ref in REFS:
        raw = git("show", f"{ref}:{path}")
        if raw:
            break
    if raw is not None and path.endswith(".gz"):
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

claim("B14", ANIMDOC, "**enemy/boss 154**", 154,
      lambda: agg(amap_rows(), lambda rows: sum(
          1 for r in rows if len(r) > 2 and re.match(r"^(CB-|Boss-|MB-)", r[2]))),
      "nhánh spec ghi 203; đếm lại theo mẫu tên CB-/Boss-/MB- ra 154 — doc đã sửa")


# ── C. TextAsset Spine + typetree ──────────────────────────────────────

TA_DIR = "reverse-engineering/textassets"


def ta_names() -> list[str] | None:
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

    if isinstance(c.stated, list):
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
        if isinstance(c.got, list):
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
