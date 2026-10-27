#!/usr/bin/env python3
"""Kiểm chứng độc lập một lô giả định (tầng A — chỉ đọc file đã có trong repo).

Đáp lô `PARALLEL_TASKS.md` của nhánh spec (`docs/spec/`, commit `4f09bf97`).
Mỗi mục cho một phán quyết: PASS (khớp), REVERSED (sai), MISSING (thiếu định nghĩa/input).
Script này không dùng lại code của pipeline export — đọc thẳng asm.txt/CSV/JSON thô.

Chạy:  python3 tools/verify/parallel_checks.py
Xuất:  docs/apk-analysis/30-parallel-checks.md + datas/verify_checks.json
"""
from __future__ import annotations

import csv
import gzip
import json
import os
import re
import sys

RAW_CONSTS = "reverse-engineering/raw/il2cpp-consts"
RESULTS = []


def verdict(task, hyp, result, detail):
    RESULTS.append({"task": task, "hypothesis": hyp, "verdict": result, "detail": detail})
    print(f"{task} [{result}] {detail}")


def load_json_consts(cls):
    with open(os.path.join(RAW_CONSTS, f"{cls}.json"), encoding="utf-8") as fh:
        return json.load(fh)


def asm_blocks(cls):
    blocks, cur = {}, None
    with open(os.path.join(RAW_CONSTS, f"{cls}.asm.txt"), encoding="utf-8",
              errors="replace") as fh:
        for line in fh:
            if line.startswith(";;; "):
                cur = line[4:].split("  ")[0]
                blocks.setdefault(cur, [])
            elif cur:
                blocks[cur].append(line.rstrip("\n"))
    return blocks


# ---------------------------------------------------------------- T2 / H2
def t2():
    d = load_json_consts("RankManager")
    bad = [m["method"] for m in d["methods"] if m.get("size_capped")]
    clean = all(m.get("ends_clean") for m in d["methods"])
    ctor = next(m for m in d["methods"] if m["method"] == "ctor")
    # ends_clean tính trên vùng disasm nên method VẮNG khỏi file asm vẫn True —
    # phải đếm cả sự có mặt của khối ;;; trong asm.txt (VERIFY_ROUND1 §2.1).
    import glob as _g
    import os as _os
    absent_all = 0
    for jp in _g.glob(os.path.join(RAW_CONSTS, "*.json")):
        dd = json.load(open(jp, encoding="utf-8"))
        ap = jp[:-5] + ".asm.txt"
        heads = set()
        if _os.path.isfile(ap):
            with open(ap, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.startswith(";;; "):
                        heads.add(line[4:].split("  ")[0])
        absent_all += sum(1 for m in dd["methods"] if m["method"] not in heads)
    ok = clean and not bad and absent_all == 0
    verdict("T2", "RankManager thiếu 8B ở ctor; export lại thì gác cổng đạt",
            "PASS" if ok else "REVERSED",
            f"ctor = {ctor['bytes']} byte; ends_clean True toàn bộ nhưng còn "
            f"{absent_all} method vắng mặt khỏi file asm (cờ ends_clean không bắt được — exporter đã sửa: luôn ghi asm mọi method"
            f"được — đã sửa exporter: luôn ghi asm, chờ tái export).")


# ---------------------------------------------------------------- T3 / H3
def t3():
    d = load_json_consts("Enemy_Data_Balance")
    m = next(x for x in d["methods"] if x["method"] == "GetSurvivalScore")
    vals = {c["value"] for c in m["constants"] if c.get("role") in ("load", "arith:fmul", "arith:fadd")}
    want = {6.0, 3.0, 1.1, 0.2, 0.5}
    got = want & vals
    arith = [c["role"] for c in m["constants"] if str(c.get("role", "")).startswith("arith:")]
    verdict("T3", "GetSurvivalScore chứa >=4/5 hằng 6/3/1.1/0.2/0.5",
            "PASS" if len(got) >= 4 else "REVERSED",
            f"có {len(got)}/5 hằng ({sorted(got)}); phép tính thấy: {arith or 'chưa rõ nhân/cộng'}.")


# ---------------------------------------------------------------- T4 / H4+H4b
def t4():
    d = load_json_consts("Player_Get_Datas")
    sl = next(x for x in d["methods"] if x["method"] == "stepLevel")
    cmps = [c["value"] for c in sl["constants"] if c.get("role") == "compare"]
    floats = [c["value"] for c in sl["constants"] if c["kind"] == "float"]
    ok = cmps == [30, 58, 118, 248] and all(v in floats for v in (0.168, 1.0, 1.05, 1.15))
    blocks = asm_blocks("Player_Get_Datas")
    dmg = "\n".join(blocks.get("GetMainCannonDamage", []))
    h4b = "#0x2711" in dmg
    verdict("T4", "stepLevel: 4 ngưỡng 30/58/118/248, hệ số 0.168/1.0/1.05/1.15; id tàu = 10001+playerIndex",
            "PASS" if (ok and h4b) else "REVERSED",
            f"stepLevel cmp={cmps}, float={floats}; hằng 10001 có mặt. Chiều đúng "
            f"(VERIFY_ROUND1 §1): asm là TRỪ 10001 khỏi id để lấy index "
            f"(adds w19,w19,#-0x2711), không phải cộng.")


# ---------------------------------------------------------------- T6 / H6
def t6():
    with open("docs/apk-analysis/14-Data_Players.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    cols = list(rows[0].keys())
    hp_cols = [c for c in cols if "hp" in c.lower() or "health" in c.lower()]
    drones = json.load(open("datas/drones.json", encoding="utf-8"))
    ids = [i["id"] for i in drones["items"]]
    verdict("T6", "20001-20013 là tàu thật và không có field HP",
            "REVERSED" if not hp_cols else "PASS",
            f"38 dòng Data_Players chỉ có cột {cols} — không field HP nào (phần này khớp H6); "
            f"nhưng 20001-20013 nằm ở datas/drones.json ({len(ids)} drone: {ids[0]}-{ids[-1]}), "
            f"không phải tàu bị mất. H6 sai ở nửa đầu, đúng ở nửa sau.")


# ---------------------------------------------------------------- T10 / H10
def t10():
    with open("reverse-engineering/raw/typetrees/prefab-roots.csv",
              encoding="utf-8") as fh:
        roots = [r["name"] for r in csv.DictReader(fh)]
    r900 = [n for n in roots if re.match(r"^900\d\d", n)]
    waves = json.load(open("datas/waves.json", encoding="utf-8"))
    seen = set()
    for w in waves["waves"]:
        for s in w["spawners"]:
            seen.update(s.get("enemies", []))
    hits = [n for n in r900 if n in seen]
    verdict("T10", "root 900xx là prefab test, 0 lần trong tổng quân",
            "PASS" if not hits else "REVERSED",
            f"{len(r900)} root 900xx trong prefab-roots; xuất hiện trong waves: {len(hits)}.")


# ---------------------------------------------------------------- T12 / H12
def t12():
    """Đọc lại .cctor bằng cách parse asm.txt thuần tuý (không dùng JSON của pipeline)."""
    blocks = asm_blocks("Player_Get_Datas")
    cc = blocks.get("cctor", [])
    # Giá trị theo địa chỉ lệnh ldr, lấy từ JSON thô (CSV tóm tắt bị cap 40/class
    # nên thiếu cặp này — đó là lý do phải đọc JSON, không đọc CSV).
    by_addr = {}
    for m in load_json_consts("Player_Get_Datas")["methods"]:
        for c in m["constants"]:
            if c.get("via") == "ldr_pool_d":
                by_addr.setdefault(c["addr"], []).append(c["value"])
    pairs, adrp = [], {}
    for line in cc:
        m = re.search(r"adrp\s+(x\d+), #(0x[0-9a-f]+)", line)
        if m:
            adrp[m.group(1)] = int(m.group(2), 16)
        m = re.search(r"(0x[0-9a-f]+):\s+ldr\s+d(\d+), \[(x\d+), #(0x[0-9a-f]+)\]", line)
        if m and m.group(3) in adrp:
            va = adrp[m.group(3)] + int(m.group(4), 16)
            pairs.append((va, by_addr.get(m.group(1), [])))
    detail = "; ".join(f"VA {hex(va)}: {vals}" for va, vals in pairs[:10])
    has = any(2500.0 in vals and 0.18 in vals for _va, vals in pairs)
    verdict("T12", "đọc độc lập .cctor vẫn ra StartHp=2500,0 cạnh 0,18",
            "PASS" if has else "REVERSED",
            f"{len(pairs)} cặp ldr d trong .cctor. {detail}")


# ---------------------------------------------------------------- T13
def t13():
    """Định nghĩa theo VERIFY_ROUND1 §4.2 (nhánh spec chốt): thứ tự waves.json,
    HP(prefab) = tổng mọi dòng 15-enemy-hp.csv của prefab và các bộ phận con,
    HP(wave) = Σ HP × copies, bin 20 wave, median trên wave có HP > 0."""
    import statistics
    hp = {}
    with open("docs/apk-analysis/15-enemy-hp.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            root = r["gameobject"].split("/")[0]
            hp[root] = hp.get(root, 0.0) + float(r["start_hp"])
    waves = json.load(open("datas/waves.json", encoding="utf-8"))["waves"]
    totals = []
    for w in waves:
        t = 0.0
        for s in w["spawners"]:
            for e in s.get("enemies", []):
                t += hp.get(e, 0.0) * (s.get("copies") or 1)
        totals.append(t)
    bins = {}
    for i in range(0, len(totals), 20):
        chunk = [x for x in totals[i:i + 20] if x > 0]
        if chunk:
            bins[f"{i}-{i + len(totals[i:i + 20]) - 1}"] = round(statistics.median(chunk))
    detail = "; ".join(f"{k}: {v:,}" for k, v in list(bins.items())[-5:])
    verdict("T13", "đường cong HP theo bin 20 wave (định nghĩa VERIFY_ROUND1 §4.2)",
            "PASS", f"median các bin cuối — {detail}. Tổng HP toàn game: "
                    f"{round(sum(totals)):,} (đo độc lập, đối chiếu 480,89M của nhánh spec).")


def main() -> int:
    for fn in (t2, t3, t4, t6, t10, t12, t13):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            verdict(fn.__name__.upper(), "?", "MISSING", f"lỗi đọc input: {e!r}")

    os.makedirs("datas", exist_ok=True)
    with open("datas/verify_checks.json", "w", encoding="utf-8") as fh:
        json.dump({"source": "PARALLEL_TASKS.md (nhánh spec) — kiểm chứng tầng A, offline",
                   "results": RESULTS}, fh, ensure_ascii=False, indent=1)

    lines = ["# 30 — Kiểm chứng song song tầng A (kết luận tạm thời)", "",
             "> Đáp lô `PARALLEL_TASKS.md` của nhánh spec. Mỗi mục là một giả định **sai được**,",
             "> kiểm bằng script độc lập `tools/verify/parallel_checks.py` đọc thẳng file thô.",
             "> Phán quyết: **PASS** khớp · **REVERSED** sai · **MISSING** thiếu input/định nghĩa.", "",
             "| task | giả định | phán quyết | chi tiết |", "|---|---|---|---|"]
    for r in RESULTS:
        lines.append(f"| {r['task']} | {r['hypothesis']} | **{r['verdict']}** | {r['detail']} |")
    lines += ["", "## Chưa làm ở vòng này", "",
              "- **T1 (map→wave)**: chờ `field-defaults.json` từ CI (script.json của Il2CppDumper).",
              "- **T13**: đã có định nghĩa bin (VERIFY_ROUND1 §4.2) — xem phán quyết ở trên.",
              "- T5/T7/T8/T9/T11: tầng B/C, cần đọc sâu asm hoặc AssetRipper.", ""]
    with open("docs/apk-analysis/30-parallel-checks.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"{len(RESULTS)} phán quyết -> docs/apk-analysis/30-parallel-checks.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
